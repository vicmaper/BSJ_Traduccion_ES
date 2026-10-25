# -*- coding: utf-8 -*-
"""avisos_auto.py - corrige solo los AVISOS que tienen una regla fija (se usa con revisar_bsj.py --corregir-avisos).

Corrige:
  - honorificos japoneses pegados a un nombre (Yoshiya-kun -> Yoshiya), salvo excepciones (Kuma-tan)
  - letras y numeros de ancho completo (ＡＢＣ１２３ -> ABC123)
  - » usado como cierre de dialogo donde el japones tiene 」
  - muletilla «este» al inicio de dialogo o entre comas
  - palabras regionales con equivalente seguro (diccionario REGIONALES)
  - ¿ / ¡ de apertura que faltan (los pone al inicio de la frase)
No toca: groserias, vosotros, palabras que dependen del contexto (carro, onda, vale, coger...).
"""
import re, unicodedata

EXCEPCIONES_HONOR = {'kuma-tan'}
HONOR = re.compile(r'\b([A-ZÁÉÍÓÚÑ][\wáéíóúñü]+)-(san|kun|chan|sama|dono|tan|chin|nee|nii)\b')

# palabra (regex, respeta mayuscula inicial) -> reemplazo
REGIONALES = [
    (r'platicar', 'conversar'), (r'platicando', 'conversando'), (r'platicamos', 'conversamos'),
    (r'platiqué', 'conversé'), (r'platicó', 'conversó'), (r'platica', 'conversa'), (r'platican', 'conversan'),
    (r'platicaron', 'conversaron'), (r'plática', 'conversación'), (r'pláticas', 'conversaciones'),
    (r'chamarra', 'chaqueta'), (r'chamarras', 'chaquetas'), (r'regadera', 'ducha'),
    (r'chamaco', 'niño'), (r'chamaca', 'niña'), (r'chamacos', 'niños'), (r'chamacas', 'niñas'),
    (r'chido', 'genial'), (r'chida', 'genial'), (r'chidos', 'geniales'), (r'chidas', 'geniales'),
    (r'padrísimo', 'genial'), (r'padrísima', 'genial'),
    (r'híjole', 'vaya'), (r'órale', 'vaya'), (r'ándale', 'anda'), (r'ándele', 'ande'), (r'ándenle', 'anden'),
    (r'ni modo', 'ni hablar'), (r'luego luego', 'enseguida'), (r'qué onda', 'qué tal'),
    (r'neta', 'en serio'), (r'nomás', 'solo'), (r'ahorita', 'ahora'), (r'ya mero', 'ya casi'),
    (r'apenado', 'avergonzado'), (r'apenada', 'avergonzada'), (r'apenados', 'avergonzados'), (r'apenadas', 'avergonzadas'),
    (r'recargado', 'apoyado'), (r'recargada', 'apoyada'), (r'recargándose', 'apoyándose'),
    (r'güero', 'rubio'), (r'güera', 'rubia'), (r'chaparro', 'bajito'), (r'chaparra', 'bajita'),
    (r'pelón', 'calvo'), (r'pelona', 'calva'), (r'popote', 'pajita'), (r'alberca', 'piscina'),
    (r'cubeta', 'balde'), (r'charola', 'bandeja'), (r'cachetes', 'mejillas'), (r'calzones', 'ropa interior'),
    (r'flojera', 'pereza'), (r'tantito', 'un poco'), (r'se me hace que', 'me parece que'),
    (r'aventó', 'lanzó'), (r'aventé', 'lancé'), (r'aventar', 'lanzar'), (r'aventando', 'lanzando'),
    (r'jaló', 'tiró'), (r'jalar', 'tirar'), (r'jalando', 'tirando'), (r'jalé', 'tiré'), (r'jalaron', 'tiraron'),
    (r'latoso', 'pesado'), (r'latosa', 'pesada'),
]
REG = [(re.compile(r'(?<![\wáéíóúñü])(' + p + r')(?![\wáéíóúñü])', re.I), r, p) for p, r in REGIONALES]

def _caso(orig, nuevo):
    if orig.isupper() and len(orig) > 1: return nuevo.upper()
    if orig[:1].isupper(): return nuevo[:1].upper() + nuevo[1:]
    return nuevo

def _fuera_de_codigos(t, fn):
    """aplica fn solo al texto que no esta entre llaves"""
    partes = re.split(r'(\{[^}]*\})', t)
    return ''.join(p if p.startswith('{') else fn(p) for p in partes)

def _aperturas(s):
    """pone ¿ y ¡ al inicio de la frase cuando falta"""
    out = []; ini = 0
    # frases: terminan en ? ! (con posibles combinaciones) ; empiezan tras . ! ? … 「 」 o inicio
    for m in re.finditer(r'[?!]+', s):
        fin = m.end(); cierre = m.group(0)
        # inicio de la frase: despues del ultimo separador antes de m.start()
        prev = s[ini:m.start()]
        k = max(prev.rfind(x) for x in ('. ', '! ', '? ', '「', '」', '　'))
        if k >= 0:
            sep = next(x for x in ('. ', '! ', '? ', '「', '」', '　') if prev.rfind(x) == k)
            st = ini + k + len(sep)
        else:
            st = ini
        frase = s[st:m.start()]
        cuerpo = frase.lstrip(' ')
        st2 = st + (len(frase) - len(cuerpo))
        if cuerpo and re.search(r'[A-Za-zÁÉÍÓÚÑáéíóúñü]', cuerpo) and '¿' not in cuerpo and '¡' not in cuerpo and not cuerpo.startswith((',', ';', ':')):
            necesita = ''
            if '?' in cierre and '¿' not in cuerpo: necesita += '¿'
            if '!' in cierre and '¡' not in cuerpo: necesita = '¡' + necesita
            if necesita:
                # orden de cierre: si cierra con ?! o !? se normaliza a ?!
                out.append(s[ini:st2]); out.append(necesita); out.append(s[st2:m.start()])
                if '?' in cierre and '!' in cierre: cierre = '?!'
                out.append(cierre); ini = fin; continue
        out.append(s[ini:fin]); ini = fin
    out.append(s[ini:])
    return ''.join(out)

def corregir_avisos(es, jp, nota):
    t = es
    # ancho completo
    t2 = _fuera_de_codigos(t, lambda p: ''.join(unicodedata.normalize('NFKC', c) if '！' <= c <= '～' and c not in '！？' else c for c in p))
    if t2 != t: nota('letras de ancho completo cambiadas'); t = t2
    # honorificos
    def h(m):
        if m.group(0).lower() in EXCEPCIONES_HONOR: return m.group(0)
        return m.group(1)
    t2 = _fuera_de_codigos(t, lambda p: HONOR.sub(h, p))
    if t2 != t: nota('honorífico japonés quitado (-san, -kun…)'); t = t2
    # » como cierre de dialogo cuando el japones usa 」 en ese punto
    if '」' in jp and '»' in t:
        t2 = re.sub(r'»(?=\{/v\})', '」', t)
        t2 = re.sub(r'(\{v:[^}]*\})«', r'\1「', t2)
        if t2 != t and t2.count('「') <= jp.count('「') and t2.count('」') <= jp.count('」'):
            nota('» cambiado por 」'); t = t2
    # muletilla «este»
    t2 = _fuera_de_codigos(t, lambda p: re.sub(r'「Este, ', '「Eh, ', re.sub(r', este(?=[,…])', ', eh', p)))
    if t2 != t: nota('muletilla «este» cambiada por «eh»'); t = t2
    # groseria como exclamacion suelta: ¡Mierda! / 「Mierda…」 -> Maldición (dentro de una frase solo se avisa)
    t2 = _fuera_de_codigos(t, lambda p: re.sub(r'(?<=[¡「])([Mm])ierda(?=[!,…」?])', lambda m: 'Maldición' if m.group(1) == 'M' else 'maldición', p))
    if t2 != t: nota('exclamación «mierda» cambiada por «maldición»'); t = t2
    # regionales
    for rx, rem, pal in REG:
        t2 = _fuera_de_codigos(t, lambda p: rx.sub(lambda m: _caso(m.group(1), rem), p))
        if t2 != t: nota('regionalismo cambiado: «%s» → «%s»' % (pal, rem)); t = t2
    # aperturas ¿ ¡
    t2 = _fuera_de_codigos(t, _aperturas)
    if t2 != t: nota('¿ o ¡ de apertura agregado'); t = t2
    return t
