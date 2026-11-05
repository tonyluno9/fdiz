"""Utilidades compartidas del pipeline FDI-Z."""
import json
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
GEN = RAIZ / "generado"
LOG = GEN / "log"
MANIFEST = RAIZ / "pipeline" / "manifest.json"
JOBS_LOG = LOG / "jobs.jsonl"
UPLOADS = LOG / "uploads.json"
OVERRIDES = LOG / "prompt_overrides.json"   # cambios genéricos y correcciones por trabajo
LIMITE_TOTAL = 220
MAX_INTENTOS = 3  # 1 original + 2 repeticiones

# entidad -> imagen base (para paleta y hoja de contacto)
BASE_ENTIDAD = {
    "tony": "tony.png", "tonyfuerte": "tonyfuerte.png", "miranda": "miranda.png",
    "cesar": "cesar.png", "alan": "alan.png", "castillo": "castillo.png",
    "alessandro": "alessandro.png", "gabo": "gabo.png", "carlos": "carlos.png",
    "canepa": "canepa.png", "joel": "joel.png", "justino": "justino.png",
    "curado": "Z0.png", "normal": "Z1.png", "corredor": "Z2.png",
    "griton": "Z3.png", "gordo": "Z4.png", "conserje": "Z5.png",
}


def cargar_manifest():
    with open(MANIFEST, encoding="utf-8") as f:
        return json.load(f)["jobs"]


def leer_log():
    if not JOBS_LOG.exists():
        return []
    out = []
    with open(JOBS_LOG, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def generaciones_usadas(entradas=None):
    """Generaciones = intentos que la API aceptó (tienen request_id)."""
    entradas = leer_log() if entradas is None else entradas
    return len({e["request_id"] for e in entradas if e.get("request_id")})


def intentos_de(job_id, entradas=None):
    entradas = leer_log() if entradas is None else entradas
    return len({e["request_id"] for e in entradas if e.get("id") == job_id and e.get("request_id")})


def cargar_overrides():
    if OVERRIDES.exists():
        with open(OVERRIDES, encoding="utf-8") as f:
            return json.load(f)
    return {"reemplazos_genericos": [], "correcciones": {}}


def prompt_final(job, ov=None):
    ov = ov or cargar_overrides()
    p = job["prompt"]
    for r in ov.get("reemplazos_genericos", []):
        p = p.replace(r["de"], r["a"])
    extra = ov.get("correcciones", {}).get(job["id"])
    if extra:
        p = p.rstrip() + " " + extra
    return p


def ruta(rel):
    return RAIZ / Path(rel)
