"""Lote del mapa: usa generar.py tal cual, pero con manifest_mapa.json y su propio tope (20).

Uso (desde RAIZ):
  python pipeline\\scripts\\generar_mapa.py --todo
  python pipeline\\scripts\\generar_mapa.py --ids mapa__salon --rehacer
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import comun
import generar

comun.MANIFEST = comun.RAIZ / "pipeline" / "manifest_mapa.json"
TOPE = 20


def usadas_mapa(entradas=None):
    entradas = comun.leer_log() if entradas is None else entradas
    return len({e["request_id"] for e in entradas
                if e.get("request_id") and str(e.get("id", "")).startswith("mapa__")})


generar.generaciones_usadas = usadas_mapa
generar.LIMITE_TOTAL = TOPE

if __name__ == "__main__":
    generar.main()
