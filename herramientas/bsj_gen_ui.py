# -*- coding: utf-8 -*-
"""bsj_gen_ui.py - interfaz de Bansenjin en espanol: title, extra, config, award.
  python bsj_gen_ui.py SCREEN_ORIGINAL(data/screen) SALIDA(ui_es/data/screen) FUENTE.otf
Copia cada carpeta COMPLETA y reescribe solo las imagenes con japones. El ingles se queda."""
import sys, os, shutil
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bsj_ui as B
import bsj_gen_config as GC

def guardar(src, dst, nm, img):
    B.U.reemplazar_dzi(src, dst, nm, img)

def copiar(src, dst):
    if os.path.isdir(dst): shutil.rmtree(dst)
    shutil.copytree(src, dst)

BARRA_CONFIG = [(428, 48, 'Guardar'), (508, 52, 'Cargar'), (592, 128, 'Juego'), (748, 116, 'Texto'), (896, 132, 'Sonido'),
                (1056, 128, 'Voces'), (1212, 152, 'Atajos'), (1396, 116, 'Lista de atajos'), (1544, 100, 'Volver al título'),
                (1672, 104, 'Salir del juego')]
TABS_CONFIG = {'tab_save': 'Guardar', 'tab_load': 'Cargar', 'tab_game': 'Juego', 'tab_text': 'Texto', 'tab_sound': 'Sonido',
               'tab_voice': 'Voces', 'tab_key': 'Atajos', 'tab_shortcut': 'Lista de atajos', 'returntitle_o': 'Volver al título',
               'exitgame_o': 'Salir del juego', 'close_o': 'Cerrar'}
ATAJOS_IZQ = ['Avanzar el texto', 'Cancelar selección / mostrar menú', 'Ocultar la ventana de mensajes',
              'Leer el historial (hacia atrás)', 'Leer el historial (hacia adelante) / avanzar',
              'Mantener para saltar texto (solo lo leído)', 'Mantener para saltar texto (también lo no leído)',
              'Repetir la voz', 'Mostrar el historial', 'Abrir o cerrar la pantalla de guardado',
              'Abrir o cerrar la pantalla de carga', 'Abrir la configuración', 'Cambiar ventana / pantalla completa',
              'Activar o desactivar el modo automático', 'En modo automático: mostrar u ocultar',
              'el texto mientras suena la voz', 'Volver al título / salir del recuerdo']
ATAJOS_DER = ['Minimizar la ventana', 'Saltar hasta la siguiente opción', 'Iniciar o detener el salto de texto',
              'Guardado rápido', 'Cargar el último guardado rápido', 'Mostrar la lista de atajos']
FILAS_ATAJOS = [146, 189, 231, 272, 314, 356, 398, 442, 483, 525, 567, 609, 651, 692, 735, 777, 819]

def barra(img, items, y=58, h=48):
    for x, w, t in items: B.sub_bajo_opaco2(img, (x - 6, y, w + 12, h), t)

NOMBRES_VOZ = {  # pantalla de Voces (chara01_1 ... chara24_1), segun VNDB / lectura del propio juego
 1: 'Hiiragi Yoshiya', 2: 'Ishigami Shizuno', 3: 'Sera Nobuaki', 4: 'Higoromo Nanten', 5: 'Sera Mizuki', 6: 'Manase Akira',
 7: 'Tatsunobe Ayumi', 8: 'Gadou Rinko', 9: 'Oosugi Harumitsu', 10: 'Narutaki Atsushi', 11: 'Nozawa Shouko',
 12: 'Tatsumiya Yurika', 13: 'Hiiragi Seijuurou', 14: 'Hiiragi Eriko', 15: 'Manase Gouzou', 16: 'Ashizumi Hanae',
 17: 'Kurana Munechika', 18: 'Amakasu Masahiko', 19: 'Keira Georgievna Gurdjieva', 20: 'Dan Karuma',
 21: 'Shinno Akikage', 22: 'Kriemhild Lebenstein', 23: 'Huang Jinlong', 24: 'Otros'}

def config(src, dst):
    copiar(src, dst)
    for i, nom in NOMBRES_VOZ.items():
        nm = 'chara%02d_1' % i
        im = B.z.armar(src, nm).convert('RGBA')
        B.texto_alfa(im, (84, 2, 206, 32), nom, size=20, keep_left='auto', maxw=176)
        guardar(src, dst, nm, im)
    fr = B.z.armar(src, 'frame').convert('RGBA'); barra(fr, BARRA_CONFIG)
    B.sub_bajo_opaco2(fr, (1790, 1000, 100, 50), 'Cerrar'); guardar(src, dst, 'frame', fr)
    for nm, t in TABS_CONFIG.items():
        im = B.z.armar(src, nm).convert('RGBA'); B.sub_bajo_alfa(im, (0, 0) + im.size, t); guardar(src, dst, nm, im)
    # pantallas con renglones y botones
    for nm in GC.PANTALLAS:
        guardar(src, dst, nm, GC.base(src, nm))
    for nm, t in GC.BOTONES.items():
        im = B.z.armar(src, nm).convert('RGBA'); B.boton_c(im, (0, 0) + im.size, t, color=(170, 245, 255), glow=(30, 150, 255))
        guardar(src, dst, nm, im)
    # guardar / cargar
    for nm, sub, desc in (('save_frame', 'Guardar', 'Guarda tu partida.'), ('load_frame', 'Cargar', 'Carga una partida guardada.')):
        im = B.z.armar(src, nm).convert('RGBA')
        B.sub_bajo_alfa(im, (820, 0, 160, 72), sub, size=15)
        B.texto_alfa(im, (36, 91, 240, 22), desc, size=17)
        guardar(src, dst, nm, im)
    # lista de atajos
    im = B.z.armar(src, 'shortcut_base').convert('RGBA')
    B.sub_bajo_alfa(im, (700, 0, 300, 72), 'Lista de atajos', size=16)
    B.texto_alfa(im, (0, 99, 570, 25), 'Teclas de atajo para jugar con más comodidad', size=21, keep_left=8, x=12)
    B.texto_alfa(im, (0, 229, 190, 28), '[Espacio] [H]', size=24)
    for y, t in zip(FILAS_ATAJOS, ATAJOS_IZQ):
        B.texto_alfa(im, (356, y - 2, 560, 30), t, size=22, x=362)
    for y, t in zip(FILAS_ATAJOS, ATAJOS_DER):
        B.texto_alfa(im, (1072, y - 2, 355, 30), t, size=22, x=1078, maxw=345)
    guardar(src, dst, 'shortcut_base', im)
    # configuracion de atajos (imagen opaca a pantalla completa)
    kf = B.z.armar(src, 'keyconfig_frame').convert('RGBA')
    barra(kf, BARRA_CONFIG); B.sub_bajo_opaco2(kf, (1790, 1000, 100, 50), 'Cerrar')
    B.sub_bajo_opaco2(kf, (780, 158, 360, 82), 'Atajos', size=17)
    B.texto_opaco_oscuro(kf, (182, 420, 340, 28), 'Asigna un atajo a cada tecla.', 22, x=186)
    B.texto_opaco_oscuro(kf, (1116, 474, 254, 88), ['Mantén pulsado el botón derecho', 'y mueve el ratón arriba, abajo,',
                         'a la izquierda o a la derecha', 'para usar los gestos.'], 17, x=1118, salto=20)
    B.texto_opaco_oscuro(kf, (168, 946, 820, 48), ['Puedes asignar atajos a las teclas 1–9, al botón derecho y a los gestos del ratón.',
                         'Arrastra cada icono hasta la posición que quieras.'], 18, x=172, salto=21)
    guardar(src, dst, 'keyconfig_frame', kf)
    # historial (atlas)
    bl = B.z.armar(src, 'backlog_base').convert('RGBA')
    B.sub_bajo_opaco2(bl, (930, 64, 200, 84), 'Historial', size=13)
    B.sub_bajo_opaco2(bl, (1862, 1040, 80, 46), 'Cerrar', size=9)
    guardar(src, dst, 'backlog_base', bl)

BARRA_EXTRA = [(456, 112, 'Galería de CG'), (652, 188, 'Galería de música'), (928, 104, 'Galería de escenas'),
               (1144, 136, 'Galería de videos'), (1396, 100, 'Volver al título'), (1628, 100, 'Salir del juego')]
TABS_EXTRA = {'tab_cg': 'Galería de CG', 'tab_music': 'Galería de música', 'tab_scene': 'Galería de escenas',
              'tab_movie': 'Galería de videos', 'returntitle_o': 'Volver al título', 'exitgame_o': 'Salir del juego'}
BASES_EXTRA = {  # nombre: (desplazamiento, caja del titulo, subtitulo, caja desc, desc, pastilla?)
 'cg_base': (1308, (820, 0, 290, 72), 'Galería de CG', (672, 98, 576, 28), 'Aquí puedes ver las CG de los eventos que aparecieron en el juego.', True),
 'music_base': (0, (689, 0, 446, 72), 'Galería de música', (668, 98, 490, 28), 'Aquí puedes escuchar la música que sonó en el juego.', False),
 'movie_base': (1308, (780, 0, 360, 72), 'Galería de videos', (692, 98, 536, 28), 'Aquí puedes ver los videos que aparecieron en el juego.', True),
 'scene_base': (1308, (830, 0, 262, 72), 'Galería de escenas', (704, 98, 512, 28), 'Aquí puedes volver a ver las escenas del juego.', True),
}

def extra(src, dst):
    copiar(src, dst)
    fr = B.z.armar(src, 'frame').convert('RGBA'); barra(fr, BARRA_EXTRA, y=56); guardar(src, dst, 'frame', fr)
    for nm, t in TABS_EXTRA.items():
        im = B.z.armar(src, nm).convert('RGBA'); B.sub_bajo_alfa(im, (0, 0) + im.size, t); guardar(src, dst, nm, im)
    for nm, (off, tb, sub, db, desc, pill) in BASES_EXTRA.items():
        im = B.z.armar(src, nm).convert('RGBA')
        B.sub_bajo_alfa(im, (off + tb[0], tb[1], tb[2], tb[3]), sub, size=17)
        B.texto_alfa(im, (off + db[0], db[1], db[2], db[3]), desc, size=21, x=off + 960, anchor='mm')
        if pill: B.pastilla_fila(im, (off + 1438, 96, 104, 33), (off + 1560, off + 1610), 'Avance', 22, (18, 32, 70), off + 1446)
        guardar(src, dst, nm, im)

def title(src, dst):
    copiar(src, dst)
    for base, t in (('cg', 'Galería de CG'), ('movie', 'Galería de videos'), ('music', 'Galería de música'), ('scene', 'Galería de escenas')):
        for suf in ('_n', '_o'):
            nm = base + suf
            if not os.path.isfile(os.path.join(src, nm + '.dzi')): continue
            im = B.z.armar(src, nm).convert('RGBA'); B.sub_bajo_alfa(im, (0, 0) + im.size, t, size=15); guardar(src, dst, nm, im)

def award(src, dst):
    copiar(src, dst)
    aw = B.z.armar(src, 'award_base').convert('RGBA')
    B.U.FUENTE = B.FUENTE
    B.U.texto_opaco(aw, (24, 728, 1000, 96), '¡Moe Game Award 2015!', 66, (255, 140, 40), x=30, glow=(40, 90, 230))
    B.U.texto_opaco(aw, (24, 836, 1890, 124), [
        'Tu voto decide el ganador del «Moe Game Award» de este año.',
        'light apoya esta iniciativa y registró «Soushuu Senshinkan Gakuen: Bansenjin» como título nominado.',
        'Más detalles en la página oficial de abajo.'], 29, (235, 235, 240), x=32, salto=35)
    B.sub_bajo_opaco2(aw, (1796, 998, 84, 50), 'Cerrar')
    guardar(src, dst, 'award_base', aw)
    ex = B.z.armar(src, 'exit_o').convert('RGBA'); B.sub_bajo_alfa(ex, (0, 0) + ex.size, 'Cerrar'); guardar(src, dst, 'exit_o', ex)

if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    if len(sys.argv) > 3: B.FUENTE = sys.argv[3]
    for nombre, fn in (('title', title), ('extra', extra), ('config', config), ('award', award)):
        fn(os.path.join(src, nombre), os.path.join(dst, nombre)); print('ok', nombre)
