# -*- coding: utf-8 -*-
"""bsj_estilo.py - revision y correccion de mensajes de Bansenjin para el kit (misma interfaz que hmj_revisar_estilo).
Usa revisar_bsj.py (formato, codigos, renglones: 690 px, 4 en la ventana de abajo / 16 en pantalla completa)
y avisos_auto.py (avisos con regla fija). Reglas editables en reglas_bsj.tsv."""
import re
import revisar_bsj as rb, avisos_auto as aa

MARCAS = re.compile(r'\{v:[^}]*\}|\{/v\}|\{end\}|\{u000A\}|' + rb.JR)
_REGLAS = None
def _reglas():
    global _REGLAS
    if _REGLAS is None: _REGLAS = rb.cargar_reglas()
    return _REGLAS

def corregir(es, jp=''):
    """formato + nombres/regionalismos con regla fija. Devuelve el texto corregido."""
    rep = []
    es = rb.corregir(es.strip(' \r\n\t'), jp, rep, '')
    corr, _ = _reglas()
    for rx, rem, motivo in corr: es = rx.sub(rem, es)
    es = aa.corregir_avisos(es, jp, lambda m: None)
    return es

def revisar(jp, es, reglas=None, hw=None):
    """lista de (nivel, problema): nivel ERROR (no entra al juego) o AVISO."""
    rep = []
    _, avisos = _reglas()
    rb.validar(es, jp, rep, '', avisos)
    return [('ERROR' if t == 'ERROR' else 'AVISO', d) for _, t, d in rep]

def limite(jp): return rb.limite(jp)
def wrap(es): return rb.hw.wrap(es, rb.ANCHO_PX)
