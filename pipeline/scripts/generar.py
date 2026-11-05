"""Fase 1/2: generación con WaveSpeed (google/nano-banana-2.1/edit).

Uso:
  python generar.py --ids id1 id2 ...      # trabajos concretos
  python generar.py --todo                  # resto del manifiesto en orden de prioridad
  python generar.py --ids X --rehacer       # vuelve a generar aunque exista salida_raw
"""
import argparse
import json
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import requests

sys.path.insert(0, os.path.dirname(__file__))
from comun import (GEN, JOBS_LOG, LIMITE_TOTAL, LOG, MAX_INTENTOS, RAIZ, UPLOADS,
                   cargar_manifest, cargar_overrides, generaciones_usadas,
                   intentos_de, leer_log, prompt_final, ruta)

API = "https://api.wavespeed.ai/api/v3"
MODELO = "google/nano-banana-2.1/edit"
KEY = os.environ.get("WAVESPEED_API_KEY")
LOCK = threading.Lock()
TERMINAL_FALLO = {"failed", "cancelled", "timeout", "deleted"}


def hdr():
    return {"Authorization": f"Bearer {KEY}"}


def log_intento(d):
    with LOCK:
        LOG.mkdir(parents=True, exist_ok=True)
        with open(JOBS_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")


def con_reintentos(fn, desc):
    """Reintenta errores de red / 5xx con espera 2,4,8 s."""
    esperas = [2, 4, 8]
    for i in range(len(esperas) + 1):
        try:
            r = fn()
            if r.status_code >= 500 or r.status_code == 429:
                raise requests.HTTPError(f"{desc}: HTTP {r.status_code} {r.text[:200]}")
            return r
        except (requests.ConnectionError, requests.Timeout, requests.HTTPError) as e:
            if i == len(esperas):
                raise
            print(f"  [red] {desc}: {e} -> reintento en {esperas[i]} s", flush=True)
            time.sleep(esperas[i])


def subir_referencias(rels):
    ups = {}
    if UPLOADS.exists():
        ups = json.loads(UPLOADS.read_text(encoding="utf-8"))
    ahora = time.time()
    cambio = False
    for rel in rels:
        e = ups.get(rel)
        if e and ahora - e["t"] < 6 * 86400:
            continue
        p = ruta(rel)
        with open(p, "rb") as f:
            data = f.read()
        r = con_reintentos(lambda: requests.post(
            f"{API}/media/upload/binary", headers=hdr(),
            files={"file": (p.name, data, "image/png")}, timeout=120), f"upload {rel}")
        r.raise_for_status()
        j = r.json()
        url = (j.get("data") or j).get("download_url")
        if not url:
            raise RuntimeError(f"upload sin download_url: {str(j)[:300]}")
        ups[rel] = {"url": url, "t": ahora}
        cambio = True
        print(f"  subida {rel}", flush=True)
    if cambio:
        LOG.mkdir(parents=True, exist_ok=True)
        UPLOADS.write_text(json.dumps(ups, indent=1), encoding="utf-8")
    return {k: v["url"] for k, v in ups.items()}


def un_intento(job, urls, n_intento):
    t0 = time.time()
    body = {
        "prompt": prompt_final(job),
        "images": [urls[r] for r in job["referencias"]],
        "aspect_ratio": job["aspect_ratio"],
        "resolution": "1k",  # regla: nunca más de 1k
        "output_format": "png",
    }
    reg = {"id": job["id"], "intento": n_intento, "request_id": None, "estado": None,
           "segundos": None, "error": None}
    # Envío: solo se reintenta si la API no llegó a aceptar el trabajo
    # (error de conexión / 5xx / 429). Un 200 con id ya cuenta como generación.
    try:
        r = con_reintentos(lambda: requests.post(
            f"{API}/{MODELO}", headers={**hdr(), "Content-Type": "application/json"},
            json=body, timeout=60), f"submit {job['id']}")
    except Exception as e:
        reg.update(estado="envio_fallido", error=str(e)[:300], segundos=round(time.time() - t0, 1))
        log_intento(reg)
        return False
    if r.status_code != 200:
        reg.update(estado="rechazado", error=f"HTTP {r.status_code} {r.text[:300]}",
                   segundos=round(time.time() - t0, 1))
        log_intento(reg)
        return False
    j = r.json()
    d = j.get("data") or j
    rid = d.get("id")
    reg["request_id"] = rid
    if not rid:
        reg.update(estado="sin_id", error=str(j)[:300], segundos=round(time.time() - t0, 1))
        reg["request_id"] = None
        log_intento(reg)
        return False
    # Registro inmediato: el trabajo ya fue aceptado (y cobrado) aunque se corte la corrida
    log_intento({"id": job["id"], "intento": n_intento, "request_id": rid, "estado": "enviado",
                 "segundos": round(time.time() - t0, 1), "error": None})
    # Sondeo
    estado, outputs, err = d.get("status"), d.get("outputs") or [], d.get("error")
    limite = time.time() + 600
    while estado != "completed" and estado not in TERMINAL_FALLO and time.time() < limite:
        time.sleep(2)
        try:
            rr = con_reintentos(lambda: requests.get(
                f"{API}/predictions/{rid}/result", headers=hdr(), timeout=30), f"poll {job['id']}")
            dd = rr.json()
            dd = dd.get("data") or dd
            estado, outputs, err = dd.get("status"), dd.get("outputs") or [], dd.get("error")
        except Exception as e:
            err = str(e)
    if estado == "completed" and outputs:
        dest = ruta(job["salida_raw"])
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():  # guardar versión anterior (rehacer)
            k = 1
            while dest.with_name(f"{dest.stem}.v{k}{dest.suffix}").exists():
                k += 1
            dest.rename(dest.with_name(f"{dest.stem}.v{k}{dest.suffix}"))
        img = con_reintentos(lambda: requests.get(outputs[0], timeout=120), f"download {job['id']}")
        img.raise_for_status()
        dest.write_bytes(img.content)
        reg.update(estado="completed", segundos=round(time.time() - t0, 1))
        log_intento(reg)
        print(f"OK  {job['id']} ({reg['segundos']} s)", flush=True)
        return True
    reg.update(estado=estado or "sin_respuesta", error=(err or "")[:300] or None,
               segundos=round(time.time() - t0, 1))
    log_intento(reg)
    print(f"ERR {job['id']}: {estado} {err}", flush=True)
    return False


RESERVA = threading.Semaphore(1)


def correr_job(job, urls, rehacer, presupuesto):
    """presupuesto: dict compartido {'usadas': n} protegido por LOCK."""
    dest = ruta(job["salida_raw"])
    if dest.exists() and not rehacer:
        return "existe"
    hecho_nuevo = False
    while True:
        with LOCK:
            prev = intentos_de(job["id"])
            # en modo rehacer se permite si quedan intentos para este trabajo
            if prev >= MAX_INTENTOS:
                print(f"SKIP {job['id']}: sin intentos (ya {prev})", flush=True)
                return "sin_intentos"
            if presupuesto["usadas"] + presupuesto["en_vuelo"] >= LIMITE_TOTAL:
                print(f"SKIP {job['id']}: límite total alcanzado", flush=True)
                return "limite"
            presupuesto["en_vuelo"] += 1  # se reserva
        try:
            ok = un_intento(job, urls, prev + 1)
        finally:
            with LOCK:
                presupuesto["en_vuelo"] -= 1
                presupuesto["usadas"] = generaciones_usadas()
        if ok:
            return "ok"
        if rehacer and hecho_nuevo:
            return "fallo"
        hecho_nuevo = True


ORDEN = ["personajes_jugables", "tonyfuerte", "zombies", "curado", "efectos", "objetos", "profes"]


def prioridad(job):
    c, e = job["categoria"], job["entidad"]
    if c == "personajes" and e == "tonyfuerte":
        return 1
    if c == "personajes":
        return 0
    if c == "zombies" and e == "curado":
        return 3
    if c == "zombies":
        return 2
    if c == "efectos":
        return 4
    if c == "objetos":
        return 5
    if c == "profes":
        return 6
    return 7


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", nargs="*")
    ap.add_argument("--todo", action="store_true")
    ap.add_argument("--rehacer", action="store_true")
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()
    if not KEY:
        sys.exit("Falta WAVESPEED_API_KEY. Configúrala con: setx WAVESPEED_API_KEY \"...\" y abre otra terminal.")
    jobs = cargar_manifest()
    if a.ids:
        sel = [j for j in jobs if j["id"] in set(a.ids)]
        faltan = set(a.ids) - {j["id"] for j in sel}
        if faltan:
            sys.exit(f"ids desconocidos: {faltan}")
    elif a.todo:
        sel = sorted(jobs, key=prioridad)  # sort estable: respeta orden del manifiesto
    else:
        sys.exit("indica --ids o --todo")
    refs = sorted({r for j in sel for r in j["referencias"]})
    urls = subir_referencias(refs)
    presupuesto = {"usadas": generaciones_usadas(), "en_vuelo": 0}
    print(f"Generaciones usadas antes: {presupuesto['usadas']}/{LIMITE_TOTAL}", flush=True)
    res = {}
    with ThreadPoolExecutor(max_workers=min(3, a.workers)) as ex:
        futs = {j["id"]: ex.submit(correr_job, j, urls, a.rehacer, presupuesto) for j in sel}
        for k, f in futs.items():
            try:
                res[k] = f.result()
            except Exception as e:
                res[k] = f"excepcion: {e}"
                print(f"EXC {k}: {e}", flush=True)
    from collections import Counter
    print("Resumen:", dict(Counter(res.values())))
    print(f"Generaciones usadas: {generaciones_usadas()}/{LIMITE_TOTAL}")


if __name__ == "__main__":
    main()
