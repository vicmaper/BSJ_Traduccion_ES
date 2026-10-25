# -*- coding: utf-8 -*-
"""revisar_bsj.py - revisa, corrige el formato e integra la traduccion del equipo (Bansenjin).

Uso:
  python revisar_bsj.py EQUIPO.csv [--base script_es.csv] [--salida CARPETA]

  EQUIPO.csv  CSV del equipo con columnas id, voice, japanese, spanish, status
              (por ejemplo no_traducidos.csv ya traducido).
  --base      CSV completo (script_es.csv). Si se da, se arma el CSV final con los
              mensajes del equipo que pasaron la revision.
  --salida    carpeta de resultados (por defecto: carpeta "revision" junto a EQUIPO.csv).
  --corregir-avisos  ademas corrige solos los AVISOS con regla fija (avisos_auto.py):
              honorificos, ¿¡ de apertura, ancho completo, » por 」, «este», regionalismos seguros.

Nunca sobrescribe los archivos de entrada. Escribe en la carpeta de salida:
  <equipo>_corregido.csv     el CSV del equipo con las correcciones automaticas
  reporte_revision.csv       una fila por cambio, error o aviso (id, tipo, detalle)
  script_es_final.csv        (con --base) guion completo: borrador + equipo aprobado
  script_es_final_listo.csv  (con --base) lo mismo con los saltos de renglon para el juego

Tipos del reporte:
  CORREGIDO  la herramienta arreglo el formato sola (revisar que este bien)
  ERROR      el mensaje NO se integra hasta corregirlo a mano
  AVISO      se integra, pero conviene revisarlo (palabra regional, honorifico, etc.)
"""
import csv, os, re, sys, math
try: sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception: pass
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import hmj_wrap as hw

ANCHO_PX = 690          # medido en Bansenjin (prueba 1): 692 px cabe, 697 no
REN_ABAJO = 4           # ventana de abajo (modo ADV): 4 renglones (prueba 4)
REN_NOVELA = 16         # pantalla completa (mensajes con {u000A})
ESTADOS_OK = ('draft', 'reviewed', 'approved')

def arg(n, d=None):
    return sys.argv[sys.argv.index(n) + 1] if n in sys.argv else d

# ---------------------------------------------------------------- codigos
JR = r'(?:\{u0006\}\{u000[0-9A-F]\}|\{u0006\}.|\{u000[0-9B-F]\})(?:\u3000?(?:\{u0006\}\{u000[0-9A-F]\}|\{u0006\}.|\{u000[0-9B-F]\}))*'
TOK = re.compile(r'\{v:[^}]*\}|\{/v\}|\{end\}|\{u000A\}|\{n\}|' + JR)
COMPACTO = re.compile(r'\{(V|/V|E|P|N|J)\}')

def kinds(t):
    out = []
    for m in TOK.finditer(t):
        s = m.group(0)
        k = 'V' if s.startswith('{v:') else '/V' if s == '{/v}' else 'E' if s == '{end}' else \
            'P' if s == '{u000A}' else 'N' if s == '{n}' else 'J'
        out.append((k, s))
    return out

def jp_lineas(jp, ancho=700):
    t = re.sub(r'\{r:([^}|]*)\|[^}]*\}', r'\1', jp)
    segs = re.split(r'\{n\}|\{u000A\}', t)
    return sum(max(1, math.ceil(hw.px(re.sub(r'\{[^}]*\}', '', s)) / ancho)) for s in segs)

def limite(jp):
    return REN_ABAJO if ('{u000A}' not in jp and jp_lineas(jp) <= REN_ABAJO) else REN_NOVELA

# ---------------------------------------------------------------- reglas
def cargar_reglas():
    corr, avis = [], []
    p = os.path.join(AQUI, 'reglas_bsj.tsv')
    for l in open(p, encoding='utf-8-sig'):
        if not l.strip() or l.startswith('#'): continue
        c = l.rstrip('\n').split('\t')
        if c[0] == 'CORREGIR' and len(c) >= 3: corr.append((re.compile(c[1]), c[2], c[3] if len(c) > 3 else ''))
        elif c[0] == 'AVISO' and len(c) >= 3: avis.append((re.compile(c[1], re.I if (len(c) < 4 or c[3] != 'si') else 0), c[2]))
    return corr, avis

JAPO = re.compile(r'[\u3040-\u309f\u30a0-\u30fa\u30fc-\u30ff\u3400-\u9fff\uff66-\uff9f。、！？：；（）［］｛｝～〜ー]')

def corregir(es, jp, rep, i):
    """Correcciones de formato que no cambian el sentido. Devuelve el texto corregido."""
    orig = es; n0 = len(rep)
    def nota(msg):
        rep.append((i, 'CORREGIDO', msg))
    # 1. saltos de linea y tabuladores reales dentro de la celda
    t = es.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    if t != es: nota('saltos de línea o tabuladores reales cambiados por espacio')
    es = t
    # 2. codigos escritos con mayusculas o espacios: { end } {END} {/V} {u000a} {N}
    t = re.sub(r'\{\s*end\s*\}', '{end}', es, flags=re.I)
    t = re.sub(r'\{\s*/\s*v\s*\}', '{/v}', t, flags=re.I)
    t = re.sub(r'\{\s*u000a\s*\}', '{u000A}', t, flags=re.I)
    t = re.sub(r'\{\s*n\s*\}', '{n}', t)
    t = re.sub(r'\{\s*v\s*:\s*([^}\s]+)\s*\}', r'{v:\1}', t, flags=re.I)
    if t != es: nota('códigos escritos con mayúsculas o espacios normalizados')
    es = t
    # 3. forma compacta {V}{/V}{E}{P}{N}{J} -> codigos reales del japones (mismo orden)
    if COMPACTO.search(es) and not TOK.search(es):
        ks = [s for k, s in kinds(jp) if k != 'N']; em = [k for k in COMPACTO.findall(es) if k != 'N']
        if [k for k, s in kinds(jp) if k != 'N'] == em:
            it = iter(ks)
            es = COMPACTO.sub(lambda m: '{n}' if m.group(1) == 'N' else next(it), es)
            nota('códigos compactos ({V}, {E}…) cambiados por los del japonés')
    # 4. voces: mismo orden y cantidad que el japones pero con otro numero -> se copian del japones
    vj = re.findall(r'\{v:[^}]*\}', jp); ve = re.findall(r'\{v:[^}]*\}', es)
    if len(vj) == len(ve) and vj != ve:
        it = iter(vj); es = re.sub(r'\{v:[^}]*\}', lambda m: next(it), es)
        nota('códigos de voz copiados del japonés')
    # 5. furigana olvidada {r:base|lectura} -> se quita (debe traducirse el sentido)
    if '{r:' in es:
        es = re.sub(r'\{r:([^}|]*)\|[^}]*\}', r'\1', es)
        nota('quedaba un {r:…} (furigana); se dejó solo el texto base: revisar')
    # 6. espacios pegados a los codigos
    t = re.sub(r'\s+(\{end\}|\{/v\}|\{u000A\}|\{n\})', r'\1', es)
    t = re.sub(r'(\{n\}|\{u000A\}) +', r'\1', t)
    t = re.sub(r'  +', ' ', t)
    if t != es: nota('espacios sobrantes junto a los códigos')
    es = t
    # 7. puntuacion japonesa o de ancho completo
    tabla = {'！': '!', '？': '?', '：': ':', '；': ';', '（': '(', '）': ')', '、': ',', '。': '.', '～': '', '〜': ''}
    t = ''.join(tabla.get(c, c) for c in es)
    t = re.sub(r'(?<=[^\s}\u3000])\u3000(?=[^\s{\u3000])', ' ', t)   # espacio japones entre palabras
    if t != es: nota('puntuación japonesa o de ancho completo cambiada')
    es = t
    # 8. puntos suspensivos: ... -> … ; …… dentro de texto -> …
    t = re.sub(r'\.{3,}', '…', es)
    t = re.sub(r'(?<=[^\s「…―])…{2,}|…{2,}(?=[^\s」…{―])', '…', t)
    t = re.sub(r'…\.+', '…', t)
    if t != es: nota('puntos suspensivos normalizados (…)')
    es = t
    # 9. punto final antes de 」 (estilo del proyecto: sin punto)
    t = re.sub(r'(?<![.…])\.(?=(\{/v\})?」)', '', es)
    if t != es: nota('punto final antes de 」 quitado')
    es = t
    # 11. sangria: parrafos que en japones empiezan con espacio japones
    pj = jp.split('{u000A}'); pe = es.split('{u000A}')
    if len(pj) == len(pe):
        cambio = False
        for k in range(len(pj)):
            if pj[k].startswith('\u3000') and not pe[k].startswith('\u3000') and pe[k].strip():
                pe[k] = '\u3000' + pe[k].lstrip(' '); cambio = True
            elif not pj[k].startswith('\u3000') and pe[k].startswith('\u3000'):
                pe[k] = pe[k].lstrip('\u3000'); cambio = True
        if cambio: es = '{u000A}'.join(pe)
    # 12. {n} que separa voces: en japones va seguido de espacio japones
    es = re.sub(r'\{end\}\{n\}(?!\u3000)', '{end}{n}\u3000', es) if '{end}{n}\u3000' in jp else es
    es = es.strip(' ')
    if es == orig.strip(' '): del rep[n0:]          # nada cambio al final: sin notas
    elif len(rep) == n0: nota('formato ajustado (sangría o espacios)')
    return es

def validar(es, jp, rep, i, avisos):
    ok = True
    kj = [k for k, s in kinds(jp) if k != 'N']; ke = [k for k, s in kinds(es) if k != 'N']
    if kj != ke:
        rep.append((i, 'ERROR', 'códigos distintos al japonés. Japonés: %s | Español: %s' % (' '.join(kj), ' '.join(ke)))); ok = False
    else:
        sj = [s for k, s in kinds(jp) if k not in ('N',)]; se = [s for k, s in kinds(es) if k not in ('N',)]
        if sj != se:
            rep.append((i, 'ERROR', 'algún código (voz o escritura especial) no es idéntico al japonés')); ok = False
    if es.count('{end}') != jp.count('{end}'):
        rep.append((i, 'ERROR', 'cantidad de {end}: japonés %d, español %d' % (jp.count('{end}'), es.count('{end}')))); ok = False
    resto = re.sub(r'\{[^}]*\}', '', es)
    jap = JAPO.findall(resto.replace('「', '').replace('」', '').replace('『', '').replace('』', ''))
    if jap:
        rep.append((i, 'ERROR', 'quedan caracteres japoneses: %s' % ''.join(sorted(set(jap)))[:20])); ok = False
    if re.search(r'\{(?!v:|/v\}|end\}|n\}|u000A\}|u0006\}|u000[0-9B-F]\})[^}]*\}', es):
        rep.append((i, 'ERROR', 'hay un código entre llaves que no existe en el juego')); ok = False
    if es.count('{') != es.count('}'):
        rep.append((i, 'ERROR', 'llaves { } sin cerrar')); ok = False
    w, n = hw.wrap(es, ANCHO_PX); lim = limite(jp)
    if n > lim:
        rep.append((i, 'ERROR', 'ocupa %d renglones; máximo %d (%s)' % (n, lim, 'ventana de abajo' if lim == REN_ABAJO else 'pantalla completa'))); ok = False
    if len(resto.strip()) == 0 and len(re.sub(r'\{[^}]*\}', '', jp).strip()) > 0:
        rep.append((i, 'ERROR', 'el español está vacío')); ok = False
    # avisos (no bloquean)
    for rx, motivo in avisos:
        m = rx.search(resto)
        if m: rep.append((i, 'AVISO', '%s: «%s»' % (motivo, m.group(0))))
    for frase in re.split(r'(?<=[.!?])\s+', resto):
        if '?' in frase and '¿' not in frase: rep.append((i, 'AVISO', 'falta ¿ de apertura')); break
    for frase in re.split(r'(?<=[.!?])\s+', resto):
        if '!' in frase and '¡' not in frase: rep.append((i, 'AVISO', 'falta ¡ de apertura')); break
    return ok, w

def main():
    if len(sys.argv) < 2 or sys.argv[1].startswith('--'):
        print(__doc__); sys.exit(1)
    eq = sys.argv[1]; base = arg('--base')
    sal = arg('--salida', os.path.join(os.path.dirname(os.path.abspath(eq)), 'revision'))
    os.makedirs(sal, exist_ok=True)
    corr, avisos = cargar_reglas()
    rows = list(csv.DictReader(open(eq, newline='', encoding='utf-8-sig')))
    faltan = [c for c in ('id', 'japanese', 'spanish', 'status') if c not in (rows[0].keys() if rows else [])]
    if faltan: raise SystemExit('ERROR: al CSV le faltan las columnas: ' + ', '.join(faltan))
    rep = []; aprobados = {}; n_txt = 0; n_sin_estado = 0
    for r in rows:
        i = r['id'].strip(); es = (r.get('spanish') or '').strip(' \r\n\t'); jp = r['japanese']
        if not es: continue
        n_txt += 1
        es = corregir(es, jp, rep, i)
        for rx, rem, motivo in corr:
            t = rx.sub(rem, es)
            if t != es: rep.append((i, 'CORREGIDO', motivo or ('«%s» → «%s»' % (rx.pattern, rem)))); es = t
        if '--corregir-avisos' in sys.argv:
            import avisos_auto
            es = avisos_auto.corregir_avisos(es, jp, lambda m, i=i: rep.append((i, 'CORREGIDO', m)))
        r['spanish'] = es
        ok, w = validar(es, jp, rep, i, avisos)
        st = (r.get('status') or '').strip().lower()
        if st not in ESTADOS_OK:
            rep.append((i, 'AVISO', 'tiene texto pero status «%s»: no se integra hasta cambiarlo a draft' % st)); n_sin_estado += 1
        elif ok:
            aprobados[i] = (es, w, st)
    nombre = os.path.splitext(os.path.basename(eq))[0]
    with open(os.path.join(sal, nombre + '_corregido.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0].keys())); wr.writeheader(); wr.writerows(rows)
    with open(os.path.join(sal, 'reporte_revision.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        wr = csv.writer(f); wr.writerow(['id', 'tipo', 'detalle']); wr.writerows(rep)
    errores = sorted({x[0] for x in rep if x[1] == 'ERROR'}, key=lambda s: int(s) if s.isdigit() else 0)
    print('Mensajes con texto: %d' % n_txt)
    print('  aprobados para integrar: %d' % len(aprobados))
    print('  con ERROR (no se integran): %d' % len(errores))
    print('  con texto pero sin status draft: %d' % n_sin_estado)
    print('  correcciones automáticas: %d   avisos: %d' % (sum(1 for x in rep if x[1] == 'CORREGIDO'), sum(1 for x in rep if x[1] == 'AVISO')))
    if errores: print('  primeros con error: ' + ', '.join(errores[:20]))
    if base:
        brow = list(csv.DictReader(open(base, newline='', encoding='utf-8-sig')))
        jpb = {r['id']: r['japanese'] for r in brow}
        mal = [i for i in aprobados if i not in jpb or jpb[i] != next(x['japanese'] for x in rows if x['id'].strip() == i)]
        if mal: raise SystemExit('ERROR: estas filas no coinciden con el guion base (¿se movieron o editaron?): ' + ', '.join(mal[:30]))
        listo = [dict(r) for r in brow]
        n_int = 0
        for r, rl in zip(brow, listo):
            if r['id'] in aprobados:
                es, w, st = aprobados[r['id']]
                r['spanish'] = es; r['status'] = st; rl['spanish'] = w; rl['status'] = st; n_int += 1
            elif r['spanish'].strip():
                rl['spanish'] = hw.wrap(r['spanish'], ANCHO_PX)[0]
        for nom, data in (('script_es_final.csv', brow), ('script_es_final_listo.csv', listo)):
            with open(os.path.join(sal, nom), 'w', newline='', encoding='utf-8-sig') as f:
                wr = csv.DictWriter(f, fieldnames=list(brow[0].keys())); wr.writeheader(); wr.writerows(data)
        tot = sum(1 for r in brow if r['spanish'].strip())
        print('CSV final: %d mensajes del equipo integrados; %d de %d mensajes en español.' % (n_int, tot, len(brow)))
    print('Resultados en: ' + sal)

if __name__ == '__main__':
    main()
