"""Lote 1 UI: 23 hojas. Un solo intento por hoja (sin regenerar).
Uso: python generar_ui_lote1.py --dry   # imprime payload de una hoja y un fondo
     python generar_ui_lote1.py         # genera las que no existan
"""
import json, os, sys, time, argparse, threading
from concurrent.futures import ThreadPoolExecutor
import requests
sys.path.insert(0, os.path.dirname(__file__))
from comun import RAIZ, LOG, ruta
import generar as g

MAN = RAIZ / "pipeline" / "scripts" / "manifest_ui_lote1.json"
LOGUI = LOG / "jobs_ui.jsonl"
L = threading.Lock()


def logui(d):
    with L:
        LOG.mkdir(parents=True, exist_ok=True)
        with open(LOGUI, "a", encoding="utf-8") as f:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")


def enviados(jid):
    if not LOGUI.exists(): return 0
    return len({e["request_id"] for e in map(json.loads, filter(None, LOGUI.read_text(encoding="utf-8").splitlines()))
                if e.get("id") == jid and e.get("request_id")})


def dest(j):
    return RAIZ / "generado" / "interfaz" / "hojas" / f"{j['id']}.png"


def payload(m, j, urls):
    blq = m["bloque_hoja"] if j["tipo"] == "hoja" else m["bloque_fondo"]
    return {"prompt": m["bloque_estilo"] + " " + j["prompt"] + " " + blq,
            "images": [urls[r] for r in j["refs"]],
            "aspect_ratio": j["aspect_ratio"], "resolution": m["resolution"],
            "output_format": m["output_format"]}


def uno(m, j, urls):
    jid = j["id"]; d = dest(j)
    if d.exists(): return jid, "existe", None
    if enviados(jid) >= 1: return jid, "ya_enviado_antes", None
    t0 = time.time()
    reg = {"id": jid, "request_id": None, "estado": None, "segundos": None, "error": None}
    try:
        r = g.con_reintentos(lambda: requests.post(
            f"{g.API}/{m['modelo_con_refs']}", headers={**g.hdr(), "Content-Type": "application/json"},
            json=payload(m, j, urls), timeout=60), f"submit {jid}")
    except Exception as e:
        reg.update(estado="envio_fallido", error=str(e)[:300]); logui(reg); return jid, "envio_fallido", None
    if r.status_code != 200:
        reg.update(estado="rechazado", error=f"HTTP {r.status_code} {r.text[:300]}"); logui(reg)
        return jid, "rechazado " + r.text[:200], None
    jj = r.json(); dd = jj.get("data") or jj; rid = dd.get("id")
    if not rid:
        reg.update(estado="sin_id", error=str(jj)[:300]); logui(reg); return jid, "sin_id", None
    logui({"id": jid, "request_id": rid, "estado": "enviado", "segundos": round(time.time() - t0, 1), "error": None})
    reg["request_id"] = rid
    estado, outs, err = dd.get("status"), dd.get("outputs") or [], dd.get("error")
    lim = time.time() + 900
    while estado != "completed" and estado not in g.TERMINAL_FALLO and time.time() < lim:
        time.sleep(3)
        try:
            rr = g.con_reintentos(lambda: requests.get(f"{g.API}/predictions/{rid}/result", headers=g.hdr(), timeout=30), f"poll {jid}")
            x = rr.json(); x = x.get("data") or x
            estado, outs, err = x.get("status"), x.get("outputs") or [], x.get("error")
        except Exception as e:
            err = str(e)
    if estado == "completed" and outs:
        try:
            img = g.con_reintentos(lambda: requests.get(outs[0], timeout=120), f"download {jid}")
            img.raise_for_status()
            d.parent.mkdir(parents=True, exist_ok=True); d.write_bytes(img.content)
        except Exception as e:
            reg.update(estado="descarga_fallida", error=f"{e} url={outs[0]}"[:400], segundos=round(time.time() - t0, 1)); logui(reg)
            return jid, "descarga_fallida", rid
        reg.update(estado="completed", segundos=round(time.time() - t0, 1)); logui(reg)
        return jid, "OK", rid
    reg.update(estado=estado or "sin_respuesta", error=(err or "")[:300] or None, segundos=round(time.time() - t0, 1)); logui(reg)
    return jid, f"fallo:{estado} {err}", rid


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dry", action="store_true"); a = ap.parse_args()
    if not g.KEY: sys.exit("Falta WAVESPEED_API_KEY")
    m = json.loads(MAN.read_text(encoding="utf-8")); jobs = m["jobs"]
    assert len(jobs) == 23 and m["modelo_con_refs"] == "google/nano-banana-2.1/edit"
    pend = [j for j in jobs if not dest(j).exists()]
    refs = sorted({r for j in pend for r in j["refs"]})
    falta = [r for r in refs if not ruta(r).exists()]
    if falta: sys.exit(f"Faltan referencias: {falta}")
    urls = g.subir_referencias(refs)
    if a.dry:
        for jid in ("ui_botones", "bg_titulo"):
            j = next(x for x in jobs if x["id"] == jid); b = payload(m, j, urls)
            print(f"[{jid}] tipo={j['tipo']} modelo={m['modelo_con_refs']} images={len(b['images'])} aspect={b['aspect_ratio']} res={b['resolution']} fmt={b['output_format']} len={len(b['prompt'])}")
            for r, u in zip(j["refs"], b["images"]): print("   img:", r, "url ok" if u.startswith("http") else u)
            print("   ini:", b["prompt"][:80]); print("   fin:", b["prompt"][-80:])
        print("pendientes:", len(pend)); return
    with ThreadPoolExecutor(max_workers=3) as ex:
        for res in ex.map(lambda j: uno(m, j, urls), pend):
            print(res, flush=True)


if __name__ == "__main__":
    main()
