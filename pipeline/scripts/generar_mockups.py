"""Lote M: 8 mockups de interfaz. Un solo intento por imagen (sin regenerar).
Uso: python generar_mockups.py --dry [id]   # imprime payload de un trabajo, no envia
     python generar_mockups.py              # genera los que no existan
"""
import json, os, sys, time, argparse
from concurrent.futures import ThreadPoolExecutor
import requests
sys.path.insert(0, os.path.dirname(__file__))
from comun import RAIZ, ruta, intentos_de
import generar as g

MAN = RAIZ / "pipeline" / "manifest_mockups.json"


def cargar():
    m = json.loads(MAN.read_text(encoding="utf-8"))
    return m, m["jobs"]


def payload(m, job, urls):
    return {
        "prompt": m["bloque_estilo"] + " " + job["prompt"],
        "images": [urls[r] for r in job["referencias"]],
        "aspect_ratio": m["aspect_ratio"],
        "resolution": m["resolution"],
        "output_format": m["output_format"],
    }


def uno(m, job, urls):
    dest = ruta(job["salida"])
    if dest.exists():
        return job["id"], "existe", None
    if intentos_de(job["id"]) >= 1:
        return job["id"], "ya_enviado_antes", None
    t0 = time.time()
    body = payload(m, job, urls)
    reg = {"id": job["id"], "intento": 1, "request_id": None, "estado": None, "segundos": None, "error": None}
    try:
        r = g.con_reintentos(lambda: requests.post(
            f"{g.API}/{m['modelo']}", headers={**g.hdr(), "Content-Type": "application/json"},
            json=body, timeout=60), f"submit {job['id']}")
    except Exception as e:
        reg.update(estado="envio_fallido", error=str(e)[:300]); g.log_intento(reg)
        return job["id"], "envio_fallido", None
    if r.status_code != 200:
        reg.update(estado="rechazado", error=f"HTTP {r.status_code} {r.text[:300]}"); g.log_intento(reg)
        return job["id"], "rechazado", None
    j = r.json(); d = j.get("data") or j; rid = d.get("id")
    if not rid:
        reg.update(estado="sin_id", error=str(j)[:300]); g.log_intento(reg)
        return job["id"], "sin_id", None
    g.log_intento({"id": job["id"], "intento": 1, "request_id": rid, "estado": "enviado",
                   "segundos": round(time.time() - t0, 1), "error": None})
    reg["request_id"] = rid
    estado, outputs, err = d.get("status"), d.get("outputs") or [], d.get("error")
    limite = time.time() + 900
    while estado != "completed" and estado not in g.TERMINAL_FALLO and time.time() < limite:
        time.sleep(3)
        try:
            rr = g.con_reintentos(lambda: requests.get(
                f"{g.API}/predictions/{rid}/result", headers=g.hdr(), timeout=30), f"poll {job['id']}")
            dd = rr.json(); dd = dd.get("data") or dd
            estado, outputs, err = dd.get("status"), dd.get("outputs") or [], dd.get("error")
        except Exception as e:
            err = str(e)
    if estado == "completed" and outputs:
        try:
            img = g.con_reintentos(lambda: requests.get(outputs[0], timeout=120), f"download {job['id']}")
            img.raise_for_status()
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(img.content)
        except Exception as e:
            reg.update(estado="descarga_fallida", error=f"{e} url={outputs[0]}"[:400],
                       segundos=round(time.time() - t0, 1)); g.log_intento(reg)
            return job["id"], "descarga_fallida", rid
        reg.update(estado="completed", segundos=round(time.time() - t0, 1)); g.log_intento(reg)
        return job["id"], "OK", rid
    reg.update(estado=estado or "sin_respuesta", error=(err or "")[:300] or None,
               segundos=round(time.time() - t0, 1)); g.log_intento(reg)
    return job["id"], f"fallo:{estado} {err}", rid


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dry", nargs="?", const="M1_titulo")
    a = ap.parse_args()
    if not g.KEY: sys.exit("Falta WAVESPEED_API_KEY")
    m, jobs = cargar()
    assert len(jobs) == 8 and m["modelo"] == "google/nano-banana-2.1/edit"
    pend = [j for j in jobs if not ruta(j["salida"]).exists()]
    refs = sorted({r for j in pend for r in j["referencias"]})
    urls = g.subir_referencias(refs)
    if a.dry:
        j = next(x for x in jobs if x["id"] == a.dry)
        b = payload(m, j, urls)
        print("modelo:", m["modelo"], "| images:", len(b["images"]), "aspect:", b["aspect_ratio"],
              "res:", b["resolution"], "fmt:", b["output_format"], "| prompt len:", len(b["prompt"]))
        for r, u in zip(j["referencias"], b["images"]): print("  img:", r, "->", "url ok" if u.startswith("http") else u)
        print("prompt ini:", b["prompt"][:80]); print("prompt fin:", b["prompt"][-80:])
        return
    with ThreadPoolExecutor(max_workers=3) as ex:
        for res in ex.map(lambda j: uno(m, j, urls), pend):
            print(res, flush=True)


if __name__ == "__main__":
    main()
