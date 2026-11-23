"""FDI-Z · Fase 79 · La música de fondo sigue durante las cinemáticas (solo se callan los diálogos) y video C04.
Correr con GDevelop cerrado, después de la 78:
    python gdevelop/scripts/fase79_musica_en_cine.py

* cine.js e historia.js ya no pausan la música de fondo al reproducir un video; sí cortan voces, alarma y efectos sueltos.
* dialogo.js: sin diálogos mientras CineModo no esté vacío (además de cuando la Historia está ocupada).
* Registra assets/historia/video/C04.mp4 (recurso vid_hist_C04, objeto VidC04) y lo agrega a historia_datos.js.
* Vuelve a incrustar historia_datos.js y dialogos_datos.js (duraciones de las voces nuevas de Tony).
* C5_01_tony usa su voz nueva (assets/historia/audio/C5_01_tony.mp3).
Idempotente.
"""
import json
import os
import re

AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")


def recorrer(evs):
    for e in evs:
        yield e
        yield from recorrer(e.get("events", []))


def main():
    # historia_datos.js: agregar C04 si el video existe
    hd = os.path.join(AQUI, "historia_datos.js")
    s = open(hd, encoding="utf-8").read()
    if os.path.exists(os.path.join(AQUI, "..", "FDI-Z", "assets", "historia", "video", "C04.mp4")) and '"C04"' not in s:
        s = s.replace('  "C03": "VidC03",\n', '  "C03": "VidC03",\n  "C04": "VidC04",\n', 1)
        open(hd, "w", encoding="utf-8", newline="\n").write(s)

    le = os.path.join(AQUI, "..", "FDI-Z", "assets", "historia", "video", "LEEME.txt")
    t = open(le, encoding="utf-8").read()
    open(le, "w", encoding="utf-8", newline="\n").write(t.replace("C04.mp4    FALTA", "C04.mp4    OK"))

    d = json.load(open(PRY, encoding="utf-8"))
    res = d["resources"]["resources"]
    if not any(r["name"] == "vid_hist_C04" for r in res):
        res.append({"file": "assets/historia/video/C04.mp4", "kind": "video", "metadata": "", "name": "vid_hist_C04", "userAdded": True})
    if not any(r["name"] == "historia/audio/C5_01_tony.mp3" for r in res):   # C5_01 ahora la dice Tony con su voz
        res.append({"file": "assets/historia/audio/C5_01_tony.mp3", "kind": "audio", "metadata": "", "name": "historia/audio/C5_01_tony.mp3",
                    "preloadAsMusic": False, "preloadAsSound": True, "preloadInCache": False, "userAdded": True})
    J = next(l for l in d["layouts"] if l["name"] == "Juego")
    if not any(o["name"] == "VidC04" for o in J["objects"]):
        J["objects"].append({"assetStoreId": "", "name": "VidC04", "type": "Video::VideoObject", "variables": [], "effects": [],
                             "behaviors": [], "content": {"opacity": 255, "loop": False, "volume": 100, "videoResource": "vid_hist_C04"}})
    for archivo, marca in (("historia_datos.js", "/*FDIZ-FASE68-DATOS*/"), ("historia.js", "/*FDIZ-FASE68-MOD*/"),
                           ("cine.js", "/*FDIZ-FASE65-MOD*/"), ("dialogo.js", "/*FDIZ-FASE64-MOD*/"),
                           ("dialogos_datos.js", "/*FDIZ-FASE64-DATOS*/")):
        codigo = open(os.path.join(AQUI, archivo), encoding="utf-8").read()
        js = [e for e in recorrer(J["events"]) if e.get("type", "").endswith("JsCode") and e.get("inlineCode", "").startswith(marca)]
        assert len(js) == 1, "no encuentro " + marca
        js[0]["inlineCode"] = marca + "\n" + codigo
    tmp = PRY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=2))
    os.replace(tmp, PRY)
    print("Fase 79 aplicada.")


if __name__ == "__main__":
    main()
