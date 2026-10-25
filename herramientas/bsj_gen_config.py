# -*- coding: utf-8 -*-
"""bsj_gen_config.py - configuracion de Bansenjin en espanol (textos de HMJ, coordenadas de BSJ)."""
import sys, os, re, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bsj_ui as B
# (x, y, w, h): (tipo, texto)   tipo: head (con icono), label (con barra azul), desc, sub (subtitulo bajo el titulo ingles)
PANTALLAS = {
 'game_base': {
   (835, 45, 132, 25): ('sub', 'Juego'),
   (0, 110, 260, 45): ('head', 'Pantalla'), (36, 189, 140, 25): ('label', 'Modo de pantalla'),
   (37, 222, 240, 21): ('desc', 'Cambia el modo de visualización.'),
   (0, 337, 260, 45): ('head', 'Efectos'), (36, 416, 225, 25): ('label', 'Aparición de personajes'),
   (37, 449, 285, 21): ('desc', 'Elige cómo aparecen los personajes.'),
   (36, 522, 192, 25): ('label', 'Aparición de CG y fondos'), (37, 555, 290, 21): ('desc', 'Elige cómo aparecen las CG y los fondos.'),
   (36, 628, 293, 25): ('label', 'Animación de la ventana'), (37, 661, 340, 21): ('desc', 'Elige cómo aparece la ventana de mensajes.'),
   (903, 110, 190, 45): ('head', 'Detalles'), (951, 189, 185, 25): ('label', 'Corte de voz'),
   (952, 222, 305, 21): ('desc', 'Corta la voz al pasar al siguiente mensaje.'),
   (951, 295, 172, 25): ('label', 'Música durante las voces'), (952, 328, 266, 21): ('desc', 'Baja la música mientras suena una voz.'),
   (903, 443, 215, 45): ('head', 'Guardado'), (951, 522, 148, 25): ('label', 'Comentarios'),
   (952, 555, 330, 21): ('desc', 'Elige si se pide un comentario al guardar.'),
   (951, 628, 186, 25): ('label', 'Guardado automático'), (952, 661, 254, 21): ('desc', 'Activa o desactiva el guardado automático.'),
 },
 'text_base': {
   (826, 45, 150, 25): ('sub', 'Texto'),
   (0, 110, 260, 45): ('head', 'Mensajes'), (903, 110, 215, 45): ('head', 'Otros'),
   (36, 189, 190, 25): ('label', 'Velocidad del texto'), (37, 222, 300, 21): ('desc', 'Ajusta la velocidad con que aparece el texto.'),
   (951, 189, 186, 25): ('label', 'Modo automático'), (951, 222, 389, 21): ('desc', 'Ajusta la espera antes del siguiente mensaje.'),
   (36, 345, 137, 25): ('label', 'Contorno de letras'), (37, 378, 263, 21): ('desc', 'Agrega un contorno al texto.'),
   (951, 345, 190, 25): ('label', 'Texto con voz'), (952, 378, 362, 21): ('desc', 'Muestra u oculta el texto con voz.'),
   (36, 451, 206, 25): ('label', 'Opacidad de la ventana'), (37, 484, 311, 21): ('desc', 'Ajusta la opacidad de la ventana de mensajes.'),
   (951, 451, 151, 25): ('label', 'Salto de texto'), (952, 484, 252, 21): ('desc', 'Elige qué texto se puede saltar.'),
   (36, 607, 169, 25): ('label', 'Mensajes leídos'), (36, 640, 241, 21): ('desc', 'Colorea los mensajes ya leídos.'),
   (951, 607, 151, 25): ('label', 'Velocidad de salto'), (952, 640, 312, 21): ('desc', 'Ajusta la velocidad al saltar texto.'),
 },
 'sound_base': {
   (824, 45, 153, 25): ('sub', 'Sonido'),
   (0, 110, 175, 45): ('head', 'Volumen'),
   (36, 189, 127, 25): ('label', 'Música'), (37, 222, 266, 21): ('desc', 'Ajusta el volumen de la música.'),
   (951, 189, 137, 25): ('label', 'Efectos de sonido'), (952, 222, 288, 21): ('desc', 'Ajusta el volumen de los efectos de sonido.'),
   (36, 345, 133, 25): ('label', 'Voces'), (37, 378, 270, 21): ('desc', 'Ajusta el volumen de las voces.'),
   (951, 345, 211, 25): ('label', 'Sonidos del sistema'), (952, 378, 273, 21): ('desc', 'Ajusta el volumen de los sonidos del sistema.'),
   (36, 501, 137, 25): ('label', 'Sonido ambiental'), (37, 534, 288, 21): ('desc', 'Ajusta el volumen del sonido ambiental.'),
   (951, 501, 151, 25): ('label', 'Videos'), (953, 534, 225, 21): ('desc', 'Ajusta el volumen de los videos.'),
 },
 'voice_base': {
   (835, 41, 132, 25): ('sub', 'Voces'),
   (0, 106, 370, 45): ('head', 'Voces de personajes'),
   (36, 185, 403, 21): ('desc', 'Activa, desactiva y ajusta el volumen de la voz de cada personaje.'),
 },
}
BOTONES_BASE = {  # textos de los botones dibujados en la base, de izquierda a derecha y de arriba a abajo
 'game_base': ['Ventana', 'Pantalla completa', 'Activado', 'Desactivado', 'Normal', 'Bajar música',
               'Normal', 'Instantánea', 'Normal', 'Instantánea', 'Con comentario', 'Sin comentario',
               'Normal', 'Instantánea', 'Activado', 'Desactivado'],
 'text_base': ['Con contorno', 'Sin contorno', 'Mostrar', 'No mostrar', 'Solo lo leído', 'Todo', 'Salto automático',
               'Sin color', 'Con color', 'Normal', 'Rápida'],
}
BOTONES = {
 'screen_window': 'Ventana', 'screen_full': 'Pantalla completa',
 'cgeffect_normal': 'Normal', 'cgeffect_high': 'Instantánea', 'mweffect_normal': 'Normal', 'mweffect_high': 'Instantánea',
 'voicecut_yes': 'Activado', 'voicecut_no': 'Desactivado', 'fadebgm_no': 'Normal', 'fadebgm_yes': 'Bajar música',
 'savecomment_yes': 'Con comentario', 'savecomment_no': 'Sin comentario', 'autosave_yes': 'Activado', 'autosave_no': 'Desactivado',
 'openface_yes': 'Con contorno', 'openface_no': 'Sin contorno', 'autovoice_yes': 'Mostrar', 'autovoice_no': 'No mostrar',
 'skip_readonly': 'Solo lo leído', 'skip_all': 'Todo', 'skip_auto': 'Salto automático',
 'skspeed_normal': 'Normal', 'skspeed_high': 'Rápida', 'readcolor_no': 'Sin color', 'readcolor_yes': 'Con color',
}

def renglon(img, box, tipo, txt):
    x, y, w, h = box
    if tipo == 'head': B.texto_alfa(img, box, txt, size=30, keep_left='auto')
    elif tipo == 'label': B.texto_alfa(img, box, txt, size=21, keep_left=10, x=x + 14)
    elif tipo == 'desc': B.texto_alfa(img, box, txt, size=17)
    elif tipo == 'sub': B.sub_bajo_alfa(img, (700, 0, 400, 75), txt, size=16)

def base(src, nm):
    img = B.z.armar(src, nm).convert('RGBA')
    import numpy as np
    rects = sorted(B.opacos(np.array(img)), key=lambda r: (r[1] // 30, r[0]))
    for (box, (tipo, txt)) in PANTALLAS[nm].items(): renglon(img, box, tipo, txt)
    for r, t in zip(rects, BOTONES_BASE.get(nm, [])): B.boton_c(img, r, t)
    return img

if __name__ == '__main__':
    src = sys.argv[1]; out = sys.argv[2]
    for nm in PANTALLAS:
        im = base(src, nm); im.save(os.path.join(out, nm + '.png')); print('ok', nm)
