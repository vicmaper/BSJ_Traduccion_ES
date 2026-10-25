# Soushuu Senshinkan Gakuen: Bansenjin — traducción al español

Kit para **hacer tu propia traducción al español** de **Soushuu Senshinkan Gakuen: Bansenjin** (light, 2017, motor MALIE),
secuela de *Hachimyoujin*, con **tu** copia del juego: sacas el guion a un CSV, traduces, el kit revisa y corrige el formato,
y genera los archivos para jugarla.

**Dudas y reportes:** Discord <https://discord.gg/k3Zfp85jMr>

## Qué hace
- Saca el guion de **tu** copia del juego a un CSV (`id, voice, japanese, spanish, status`) que se edita en Excel o LibreOffice.
- Revisa y corrige solo lo seguro (marcas `{v:}{/v}{end}{u000A}`, puntuación japonesa, `«…»`, `¡¿`, honoríficos, espacios,
  nombres y regionalismos con cambio seguro), pone los saltos de renglón por píxeles (690 px) y avisa lo que no cabe
  (ventana de abajo: 4 renglones; pantalla completa: 16).
- Genera `data3.dat` (el juego lo carga encima de `data1.dat` y `data2.dat`) con:
  guion, nombres del historial, opciones de elección, interfaz y fuente adaptada en español.
- Crea `malie_es.exe` (menús de Windows y avisos en español) a partir de tu `malie.exe`.
- Exporta tu traducción **sin japonés** para compartirla.

## Edición compatible
| | |
|---|---|
| Juego | Soushuu Senshinkan Gakuen: Bansenjin, light, 2017 (PC, disco) |
| `malie.exe` | v1.1.0.0 (2017-09-06), md5 `5ea9b73378814b1dbc178449136b2266` |
| `exec.dat` (en `data2.dat`) | md5 `2b08465872c5cd034c2a633b6e99c836` |
| Clave de los `.dat` | `Soushuu Senshinkan Gakuen Bansenjin` |

Sin parches oficiales. Si tu copia es otra, el kit se detiene sin cambiar nada: pide ayuda en el Discord.

## Uso rápido
1. Descarga `BSJ_Traduccion_ES.zip` de *Releases* y descomprímelo fuera de la carpeta del juego.
2. Abre `BSJ_Kit.exe`, elige la carpeta del juego y pulsa **1** (sacar el CSV).
3. Traduce la columna `spanish` (en la pestaña *Editar mensajes* o con Excel/LibreOffice).
4. Pulsa **2** (revisar), **3** (generar e instalar) y **4** (malie_es.exe), y juega con `malie_es.exe`.

Guía completa: [GUIA_PARA_FANS.txt](GUIA_PARA_FANS.txt).

Con Python 3.10+: `pip install -r requirements.txt` y `python herramientas/bsj_gui.py`
(o `python herramientas/bsj_kit.py extraer|revisar|validar|generar|exe|compartir|dividir`).

## Qué NO trae este repositorio
- Ningún archivo del juego, ni imágenes, ni la fuente, ni el texto japonés.
  La interfaz y la fuente en español se **rehacen en tu computadora** a partir de tu copia.
- `traduccion/cadenas_es.tsv` lleva los nombres del historial y las opciones en español (sin japonés, por offset).
  Si pones un `traduccion/BSJ_es.csv` (id, voice, spanish), el kit lo usa como punto de partida; si no está,
  el CSV de trabajo sale con la columna `spanish` vacía para que traduzcas desde cero.
- `herramientas/bsj_exe_parche.json` lleva solo los bytes que cambian (texto en español) para `malie_es.exe`.

No subas aquí el CSV de trabajo, la carpeta `trabajo/` ni ningún `.dat`: llevan el texto y los archivos del juego
(`.gitignore` ya los excluye).

## Cómo se arma el .exe
Al publicar una versión (Releases → *Draft a new release*), GitHub Actions (`.github/workflows/construir-exe.yml`)
arma `BSJ_Kit.exe` con PyInstaller 6.10 y sube `BSJ_Traduccion_ES.zip` a esa versión.
También se puede lanzar a mano en Actions → *Construir BSJ_Kit.exe* → *Run workflow*.

## Créditos
Traducción y herramientas: proyecto de traducción de Senshinkan (ver Discord). Basado en las herramientas MALIE de los
proyectos Kajiri Kamui Kagura, Paradise Lost y Hachimyoujin. Claves de cifrado MALIE tomadas de GARbro.
Proyecto de fans sin fines de lucro; compra el juego original.
