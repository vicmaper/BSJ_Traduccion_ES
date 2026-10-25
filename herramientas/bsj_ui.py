# -*- coding: utf-8 -*-
"""bsj_ui.py - utilidades de interfaz para Bansenjin (BSJ). Textos sobre fondo TRANSPARENTE (mascara por alfa)
y botones opacos (hmj_ui.boton, inpainting)."""
import os, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H)
import hmj_dzi as z, hmj_ui as U
FUENTE = None   # la pone quien llama: la fuente ORIGINAL de la copia del juego (data/font/anticcezannepro.otf)
def F(s): return ImageFont.truetype(FUENTE, int(round(s)))

def opacos(a, minw=60, minh=24):
    """rectangulos opacos grandes (botones) para excluirlos"""
    m = (a[..., 3] > 200).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    return [tuple(int(v) for v in st[i][:4]) for i in range(1, n) if st[i][2] >= minw and st[i][3] >= minh]

def filas(img, excl=(), thr=60, gap=25):
    a = np.array(img.convert('RGBA')); t = a[..., 3] > thr
    for x, y, w, h in list(excl) + opacos(a): t[max(0, y):y + h, max(0, x):x + w] = False
    rows = t.sum(1); W = a.shape[1]
    t[rows > 0.5 * W] = False
    m = cv2.dilate(t.astype(np.uint8) * 255, np.ones((3, gap), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    B = [tuple(int(v) for v in st[i][:4]) for i in range(1, n) if 8 <= st[i][3] <= 70 and st[i][2] >= 14]
    B.sort(key=lambda b: (b[1] // 20, b[0]))
    return B

def ver(img, B, out, fondo=(225, 225, 230)):
    bg = Image.new('RGBA', img.size, fondo + (255,)); bg.alpha_composite(img.convert('RGBA')); d = ImageDraw.Draw(bg)
    for k, (x, y, w, h) in enumerate(B):
        d.rectangle([x, y, x + w, y + h], outline=(255, 0, 0)); d.text((x + w + 2, y), str(k), fill=(255, 0, 0))
    bg.convert('RGB').save(out)

def texto_alfa(img, box, text, size=None, color=None, glow=None, x=None, maxw=None, anchor='lm', borrar=None, minalpha=40, keep_left=0):
    """borra los pixeles visibles del renglon (fondo transparente) y escribe text con el color medio original"""
    a = np.array(img.convert('RGBA')); bx, by, bw, bh = box
    sub = a[by:by + bh, bx:bx + bw]; t = sub[..., 3] > minalpha
    if keep_left == 'auto':
        cols = t.any(0); k = 0; seen = False; gap = 0
        for i, c in enumerate(cols):
            if c: seen = True; gap = 0
            elif seen:
                gap += 1
                if gap >= 4: k = i; break
        keep_left = k
    if keep_left: t[:, :keep_left] = False
    ys, xs = np.where(t)
    if not len(xs): raise SystemExit('sin texto en %s (%s)' % (box, text))
    col = color or tuple(int(c) for c in sub[t][:, :3].mean(0))
    x0, y0, x1, y1 = bx + xs.min(), by + ys.min(), bx + xs.max() + 1, by + ys.max() + 1
    rb = borrar or (bx + keep_left, by, bw - keep_left, bh)
    m = np.zeros(a.shape[:2], bool); m[rb[1]:rb[1] + rb[3], rb[0]:rb[0] + rb[2]] = a[rb[1]:rb[1] + rb[3], rb[0]:rb[0] + rb[2], 3] > 0
    m = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    m[:by, :] = False; m[by + bh:, :] = False
    a[..., 3] = np.where(m, 0, a[..., 3]); out = Image.fromarray(a)
    sz = size or max(10, int((y1 - y0) * 1.05))
    U.FUENTE = FUENTE
    U.escribir(out, (x if x is not None else x0) if not callable(x) else x(x0), (y0 + y1) / 2, text, sz, col, glow, anchor=anchor, maxw=maxw)
    img.paste(out); return out

def boton_c(img, rect, text, size=22, color=(242, 244, 252), glow=(40, 110, 200), zx=(0.15, 0.85), zy=(0.12, 0.9), umbral=28, maxfrac=0.70):
    """boton opaco: borra el texto (relleno por renglon) y escribe el nuevo CENTRADO"""
    a = np.array(img.convert('RGBA')); x, y, w, h = rect
    w = min(w, a.shape[1] - x); h = min(h, a.shape[0] - y); sub = a[y:y + h, x:x + w].copy()
    lum = sub[..., :3].astype(int).mean(2)
    zona = np.zeros(lum.shape, bool); zona[int(h * zy[0]):int(h * zy[1]), int(w * zx[0]):int(w * zx[1])] = True
    med = np.median(lum[zona]); t = (lum > med + umbral) & zona
    col = color or (tuple(int(v) for v in sub[t][:, :3].mean(0)) if t.any() else (240, 245, 255))
    mk = cv2.dilate(t.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool) & zona
    x0, x1 = int(w * zx[0]), int(w * zx[1])
    for yy in range(h):
        if mk[yy].any():
            fila = sub[yy, x0:x1, :3]; libre = ~mk[yy, x0:x1]
            if libre.sum() > 5: sub[yy, :, :3][mk[yy]] = np.median(fila[libre], axis=0).astype(np.uint8)
    a[y:y + h, x:x + w] = sub; out = Image.fromarray(a)
    ys = np.where(t.any(1))[0]; cy = y + (ys.min() + ys.max()) / 2 if len(ys) else y + h / 2
    U.FUENTE = FUENTE
    U.escribir(out, x + w / 2, cy, text, size, col, glow, anchor='mm', glow_r=1.3, glow_k=0.9, maxw=w * maxfrac)
    img.paste(out)

def sub_bajo(img, box, text, size=None, color=None, glow=None, minalpha=60):
    """borra el ULTIMO renglon (el japones pequeno bajo el ingles) dentro de box y escribe text centrado"""
    a = np.array(img.convert('RGBA')); x, y, w, h = box
    w = min(w, a.shape[1] - x); h = min(h, a.shape[0] - y)
    sub = a[y:y + h, x:x + w]; al = sub[..., 3] > minalpha
    rows = al.sum(1); runs = []; cur = None
    for i, v in enumerate(rows):
        if v and cur is None: cur = i
        if not v and cur is not None: runs.append((cur, i)); cur = None
    if cur is not None: runs.append((cur, len(rows)))
    if len(runs) < 2: raise SystemExit('sub_bajo: no hay dos renglones en %s %s' % (box, runs))
    y0, y1 = runs[-1]
    t = al[y0:y1]; sel = sub[y0:y1][t]
    # color: los pixeles mas opacos del renglon
    col = color or tuple(int(v) for v in sel[sel[:, 3] >= np.percentile(sel[:, 3], 70)][:, :3].mean(0))
    a[y + y0 - 1:y + y1 + 1, x:x + w, 3] = 0
    out = Image.fromarray(a)
    sz = size or max(8, int((y1 - y0) * 1.25))
    U.FUENTE = FUENTE
    U.escribir(out, x + w / 2, y + (y0 + y1) / 2, text, sz, col, glow, anchor='mm', maxw=w - 2)
    img.paste(out); return out

def sub_bajo_opaco(img, box, text, size=None, color=None, glow=None, umbral=45):
    """igual que sub_bajo pero sobre fondo opaco oscuro: el texto es lo claro; se rellena por renglon"""
    a = np.array(img.convert('RGBA')); x, y, w, h = box
    sub = a[y:y + h, x:x + w].copy(); lum = sub[..., :3].astype(int).mean(2)
    t = lum > np.median(lum) + umbral
    rows = t.sum(1); runs = []; cur = None
    for i, v in enumerate(rows):
        if v and cur is None: cur = i
        if not v and cur is not None: runs.append((cur, i)); cur = None
    if cur is not None: runs.append((cur, len(rows)))
    if len(runs) < 2:
        a0, a1 = runs[-1]; mid = (a0 + a1) // 2
        k = mid + int(np.argmin(rows[mid:a1 - 3])); runs = [(a0, k), (k + 1, a1)]
    y0, y1 = runs[-1]
    tt = np.zeros_like(t); tt[y0:y1] = t[y0:y1]
    col = color or tuple(int(v) for v in sub[tt][:, :3].mean(0))
    mk = cv2.dilate(tt.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    for yy in range(h):
        if mk[yy].any():
            libre = ~mk[yy]
            if libre.sum() > 3: sub[yy, :, :3][mk[yy]] = np.median(sub[yy, libre, :3], axis=0).astype(np.uint8)
    a[y:y + h, x:x + w] = sub; out = Image.fromarray(a)
    sz = size or max(8, int((y1 - y0) * 1.25))
    U.FUENTE = FUENTE
    U.escribir(out, x + w / 2, y + (y0 + y1) / 2, text, sz, col, glow, anchor='mm', maxw=w - 2)
    img.paste(out); return out

def sub_bajo_opaco2(img, box, text, size=11, color=None, sombra=True, umbral=45):
    """subtitulo japones bajo el ingles en fondo opaco: separa por componentes (las colas de g/p del ingles se quedan)"""
    a = np.array(img.convert('RGBA')); x, y, w, h = box
    sub = a[y:y + h, x:x + w].copy(); lum = sub[..., :3].astype(int).mean(2); med = np.median(lum)
    t = (lum > med + umbral).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(t)
    comps = [(i, st[i]) for i in range(1, n) if st[i][4] >= 2]
    tops = np.array([s[1] for _, s in comps]); bots = np.array([s[1] + s[3] for _, s in comps])
    corte = (tops.min() + bots.max()) / 2.0
    jp = np.zeros_like(t, bool)
    for i, s in comps:
        if s[1] >= corte - 1: jp |= lab == i
    ys, xs = np.where(jp)
    if not len(xs): raise SystemExit('sub_bajo_opaco2: sin japones en %s' % (box,))
    v = lum[jp]; col = color or tuple(int(c) for c in sub[jp][v >= np.percentile(v, 75)][:, :3].mean(0))
    zona = cv2.dilate(jp.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    oscuro = lum < med - 18
    mk = zona | (cv2.dilate(zona.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool) & oscuro & (np.arange(h)[:, None] >= ys.min() - 1))
    for yy in range(h):
        if mk[yy].any():
            libre = ~mk[yy] & ~(t[yy].astype(bool))
            if libre.sum() > 3: sub[yy, :, :3][mk[yy]] = np.median(sub[yy, libre, :3], axis=0).astype(np.uint8)
    a[y:y + h, x:x + w] = sub; out = Image.fromarray(a)
    cy = y + (ys.min() + ys.max()) / 2.0; cx = x + (xs.min() + xs.max()) / 2.0
    U.FUENTE = FUENTE
    if sombra: U.escribir(out, cx + 1, cy + 1, text, size, (10, 10, 18), None, anchor='mm', maxw=w - 2)
    U.escribir(out, cx, cy, text, size, col, None, anchor='mm', maxw=w - 2)
    img.paste(out); return out

def sub_bajo_alfa(img, box, text, size=11, color=None, sombra=True):
    """subtitulo japones bajo el ingles en fondo TRANSPARENTE (imagenes de resaltado): por componentes"""
    a = np.array(img.convert('RGBA')); x, y, w, h = box
    w = min(w, a.shape[1] - x); h = min(h, a.shape[0] - y)
    sub = a[y:y + h, x:x + w]; lum = sub[..., :3].astype(int).mean(2)
    t = ((sub[..., 3] > 90) & (lum > 120)).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(t)
    comps = [(i, st[i]) for i in range(1, n) if st[i][4] >= 2]
    tops = np.array([s[1] for _, s in comps]); bots = np.array([s[1] + s[3] for _, s in comps])
    corte = (tops.min() + bots.max()) / 2.0
    jp = np.zeros(t.shape, bool)
    for i, s in comps:
        if s[1] >= corte - 1: jp |= lab == i
    ys, xs = np.where(jp)
    if not len(xs): raise SystemExit('sub_bajo_alfa: sin japones en %s' % (box,))
    v = lum[jp]; col = color or tuple(int(c) for c in sub[jp][v >= np.percentile(v, 75)][:, :3].mean(0))
    zona = cv2.dilate(jp.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool)
    zona &= ~(t.astype(bool) & ~jp)          # no tocar el ingles
    zona[:max(0, ys.min() - 2)] = False
    sub[..., 3] = np.where(zona, 0, sub[..., 3]); a[y:y + h, x:x + w] = sub
    out = Image.fromarray(a)
    cy = y + (ys.min() + ys.max()) / 2.0; cx = x + (xs.min() + xs.max()) / 2.0
    U.FUENTE = FUENTE
    if sombra: U.escribir(out, cx + 1, cy + 1, text, size, (10, 10, 18), None, anchor='mm', maxw=w - 2)
    U.escribir(out, cx, cy, text, size, col, None, anchor='mm', maxw=w - 2)
    img.paste(out); return out

def texto_opaco_oscuro(img, rect, lineas, size, color=None, x=None, salto=None, umbral=45, glow=None, anchor='lm', cx=None):
    """texto OSCURO (o de color) sobre fondo opaco CLARO: inpainting de lo oscuro y renglones nuevos"""
    a = np.array(img.convert('RGBA')); rx, ry, rw, rh = rect
    sub = a[ry:ry + rh, rx:rx + rw]; lum = sub[..., :3].astype(int).mean(2); med = np.median(lum)
    t = lum < med - umbral
    col = color or (tuple(int(c) for c in sub[t][:, :3].mean(0)) if t.any() else (30, 30, 40))
    m = np.zeros(a.shape[:2], np.uint8); m[ry:ry + rh, rx:rx + rw] = cv2.dilate(t.astype(np.uint8) * 255, np.ones((5, 5), np.uint8))
    rgb = cv2.cvtColor(np.ascontiguousarray(a[..., :3]), cv2.COLOR_RGB2BGR)
    o = cv2.inpaint(rgb, m, 5, cv2.INPAINT_TELEA); a[..., :3] = cv2.cvtColor(o, cv2.COLOR_BGR2RGB)
    out = Image.fromarray(a)
    if isinstance(lineas, str): lineas = [lineas]
    salto = salto or size * 1.25
    y = ry + rh / 2 - salto * (len(lineas) - 1) / 2
    U.FUENTE = FUENTE
    for L in lineas:
        U.escribir(out, cx if cx is not None else (rx if x is None else x), y, L, size, col, glow, anchor=anchor); y += salto
    img.paste(out); return out

def pastilla_fila(img, rect, ref, text, size, color, x):
    """borra rect copiando por renglon el color mediano de las columnas ref=(x0,x1) y escribe text"""
    a = np.array(img.convert('RGBA')); rx, ry, rw, rh = rect
    for yy in range(ry, ry + rh):
        a[yy, rx:rx + rw, :3] = np.median(a[yy, ref[0]:ref[1], :3], axis=0).astype(np.uint8)
    out = Image.fromarray(a); U.FUENTE = FUENTE
    U.escribir(out, x, ry + rh / 2, text, size, color, None); img.paste(out)
