"""Lote V0: UN solo video Kling 3.0 Std. Un solo envio aceptado."""
import json, os, sys, time
import requests
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from comun import RAIZ, LOG
import generar as g

OUT = RAIZ / "generado" / "interfaz" / "video" / "titulo"
LOGUI = LOG / "jobs_ui.jsonl"
JID = "V0_titulo_kling"
MODELO = "kwaivgi/kling-v3.0-std/image-to-video"
PROMPT = ("Animate this pixel art title screen as a subtle, seamless looping idle animation. The camera is completely locked: no zoom, no pan, no tilt, no camera shake. Keep every object and character exactly in place, with the same design, colors and chunky pixel art style as the image. Small motions only: the four students on the left breathe gently and shift their weight slightly; the green-skinned zombies at the door sway and shuffle in place with their arms stretched forward; the old janitor zombie in the doorway sways slightly and his mop moves a little; the yellow light cones of the two street lamps flicker softly; the palm tree leaves and the round bushes sway gently in a light night breeze; the moon glows softly. The scene ends exactly as it starts.")
NEG = "camera movement, zoom, pan, camera shake, scene change, cut, new characters, characters walking away, characters leaving the frame, morphing, melting, face distortion, extra limbs, realistic style, 3D render, smooth painterly shading, blur, motion blur, text, letters, logo, watermark, flashing, strobe"


def logui(d):
    LOG.mkdir(parents=True, exist_ok=True)
    with open(LOGUI, "a", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False) + "\n")


def ya_enviado():
    if not LOGUI.exists(): return False
    return any(e.get("id") == JID and e.get("request_id")
               for e in map(json.loads, filter(None, LOGUI.read_text(encoding="utf-8").splitlines())))


def main():
    dry = "--dry" in sys.argv
    if not g.KEY: sys.exit("Falta WAVESPEED_API_KEY")
    if ya_enviado(): sys.exit("V0 ya enviado antes; no se reenvia.")
    OUT.mkdir(parents=True, exist_ok=True)
    ent = OUT / "entrada_titulo.png"
    if not ent.exists():
        im = Image.open(RAIZ / "gdevelop/FDI-Z/assets/interfaz/bg_titulo.png").convert("RGBA")
        bg = Image.new("RGB", im.size, (0, 0, 0)); bg.paste(im, mask=im.split()[3]); bg.save(ent)
    r = g.con_reintentos(lambda: requests.post(f"{g.API}/media/upload/binary", headers=g.hdr(),
        files={"file": (ent.name, ent.read_bytes(), "image/png")}, timeout=120), "upload")
    r.raise_for_status(); j = r.json(); url = (j.get("data") or j).get("download_url")
    assert url
    body = {"image": url, "last_image": url, "duration": 3, "cfg_scale": 0.5, "sound": False,
            "prompt": PROMPT, "negative_prompt": NEG}
    print(json.dumps({k: (v if k not in ("prompt", "negative_prompt") else v[:50] + "...") for k, v in body.items()}, indent=1))
    if dry: return
    t0 = time.time(); reg = {"id": JID, "request_id": None, "estado": None, "segundos": None, "error": None}
    rr = None
    for intento in range(4):
        try:
            rr = requests.post(f"{g.API}/{MODELO}", headers={**g.hdr(), "Content-Type": "application/json"}, json=body, timeout=60)
            if rr.status_code >= 500 or rr.status_code == 429:
                print("reintento envio", rr.status_code); time.sleep(5); continue
            break
        except requests.RequestException as e:
            print("reintento envio", e); time.sleep(5)
    if rr is None or rr.status_code != 200:
        reg.update(estado="rechazado", error=(f"HTTP {rr.status_code} {rr.text[:400]}" if rr is not None else "sin respuesta")); logui(reg)
        sys.exit("Envio no aceptado: " + reg["error"])
    dd = rr.json().get("data") or rr.json(); rid = dd.get("id")
    logui({"id": JID, "request_id": rid, "estado": "enviado", "segundos": round(time.time() - t0, 1), "error": None})
    print("request_id", rid, flush=True)
    estado, outs, err, x = dd.get("status"), [], None, dd
    lim = time.time() + 1500
    while estado != "completed" and estado not in g.TERMINAL_FALLO and time.time() < lim:
        time.sleep(10)
        try:
            x = requests.get(f"{g.API}/predictions/{rid}/result", headers=g.hdr(), timeout=30).json()
            x = x.get("data") or x; estado, outs, err = x.get("status"), x.get("outputs") or [], x.get("error")
        except Exception as e:
            err = str(e)
    if estado == "completed" and x.get("outputs"):
        v = requests.get(x["outputs"][0], timeout=300); v.raise_for_status()
        (OUT / "raw_kling_titulo.mp4").write_bytes(v.content)
        reg.update(request_id=rid, estado="completed", segundos=round(time.time() - t0, 1))
        print("timings", x.get("timings"), "extra", {k: x[k] for k in x if k in ("price", "cost", "has_nsfw_contents")})
    else:
        reg.update(request_id=rid, estado=estado or "sin_respuesta", error=(err or "")[:300] or None, segundos=round(time.time() - t0, 1))
    logui(reg); print(reg)

main()
