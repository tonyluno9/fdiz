"""Fase 66 · Música nueva: menú (soundtrack2d) y partida (ambiente juego + su capa encima). Idempotente.

Uso (desde la carpeta fdiz, con GDevelop CERRADO):
    python gdevelop/scripts/fase66_musica.py ["carpeta con los originales"]
La carpeta por defecto es fdiz/sonidosfdi/.

Qué hace:
  1) Copia a gdevelop/FDI-Z/musica/ y registra como recursos de audio:
       SOUNDTRACK2D.MP3.mpeg            -> musica/soundtrack2d.mp3      (copia exacta; solo cambia la extensión, es un MP3)
       ambiente juego.wav               -> musica/ambiente_juego.wav    (PCM 24 -> 16 bits, la regla del proyecto)
       va encima de ambiente de juego.wav -> musica/ambiente_juego_capa.wav (igual)
  2) Menú (Titulo, Menu, Online): soundtrack2d en el canal 1, en bucle, volumen 45 (antes musica/menu.ogg).
  3) Partida (Juego, todos los modos): ambiente_juego en el canal 1 (45) y la capa encima en el canal 2 (40), ambas en
     bucle desde el inicio. Los cambios de pista por infestación y por el final (partida_2, partida_3, final_aguanten)
     quedan desactivados para que el ambiente no se corte; los .ogg viejos se conservan.
  4) Al entrar a Titulo, Menu, Online y Resultados se detiene el canal 2 (la capa no sigue fuera de la partida).
  5) audio_manifest.json: agrega las 3 pistas y la extensión .mp3.
cine.js (fase 65) pausa los canales 1 y 2 durante los videos; si se cambia, volver a correr fase65_cinematicas.py.
"""
import datetime, json, os, shutil, sys, wave

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
PROY = os.path.join(RAIZ, "gdevelop", "FDI-Z")
PRY = os.path.join(PROY, "FDI-Z.json")
MANI = os.path.join(PROY, "audio_manifest.json")
FUENTE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(RAIZ, "sonidosfdi")
MK = "FDIZ-FASE66"

MENU = "musica/soundtrack2d.mp3"
AMB = "musica/ambiente_juego.wav"
CAPA = "musica/ambiente_juego_capa.wav"
ARCHIVOS = [("SOUNDTRACK2D.MP3.mpeg", MENU), ("ambiente juego.wav", AMB), ("va encima de ambiente de juego.wav", CAPA)]
VOL_MENU, VOL_AMB, VOL_CAPA = "45", "45", "40"
VIEJAS = {"musica/partida_2.ogg", "musica/partida_3.ogg", "musica/final_aguanten.ogg"}


def a16(origen, destino):
    """WAV PCM a 16 bits (si ya es de 16, copia tal cual). Toma los 2 bytes altos de cada muestra."""
    w = wave.open(origen, "rb")
    ch, ancho, hz, n = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
    datos = w.readframes(n); w.close()
    if ancho == 2:
        shutil.copyfile(origen, destino); return
    if ancho != 3:
        raise SystemExit("%s: solo se convierte PCM de 24 bits (tiene %d bytes por muestra)" % (origen, ancho))
    out = bytearray(len(datos) // 3 * 2)
    out[0::2] = datos[1::3]
    out[1::2] = datos[2::3]
    tmp = destino + ".tmp"
    s = wave.open(tmp, "wb"); s.setnchannels(ch); s.setsampwidth(2); s.setframerate(hz); s.writeframes(bytes(out)); s.close()
    os.replace(tmp, destino)


def recorrer(lst):
    for e in lst:
        yield e
        yield from recorrer(e.get("events", []))


def musica(e):
    return [x for x in e.get("actions", []) if x["type"]["value"] == "PlayMusicCanal"]


def play(archivo, canal, vol):
    return {"type": {"value": "PlayMusicCanal"}, "parameters": ["", archivo, canal, "yes", vol, "1"]}


def parar2():
    return {"type": {"value": "StopMusicCanal"}, "parameters": ["", "2"]}


def main():
    # ---- archivos
    dest = os.path.join(PROY, "musica")
    for org, res in ARCHIVOS:
        o = os.path.join(FUENTE, org)
        if not os.path.exists(o):
            raise SystemExit("Falta %s" % o)
        d_ = os.path.join(PROY, *res.split("/"))
        if res.endswith(".wav"):
            a16(o, d_)
        else:
            shutil.copyfile(o, d_)

    d = json.load(open(PRY, encoding="utf-8"))
    resp = os.path.join(RAIZ, "gdevelop", "respaldos")
    os.makedirs(resp, exist_ok=True)
    bak = os.path.join(resp, "antes_de_fase66_%s.json" % datetime.date.today().strftime("%Y%m%d"))
    if not os.path.exists(bak):
        shutil.copy(PRY, bak)

    res = d["resources"]["resources"]
    for _, nombre in ARCHIVOS:
        if not any(r["name"] == nombre for r in res):
            res.append({"file": nombre, "kind": "audio", "metadata": "", "name": nombre, "userAdded": True})

    L = {l["name"]: l for l in d["layouts"]}
    cambios = []

    # ---- menú
    for n in ("Titulo", "Menu", "Online"):
        for e in recorrer(L[n]["events"]):
            for x in musica(e):
                if x["parameters"][1] in ("musica/menu.ogg", MENU) and x["parameters"][2] == "1":
                    x["parameters"][1], x["parameters"][4] = MENU, VOL_MENU
                    cambios.append(n + ": menú -> soundtrack2d")

    # ---- partida
    J = L["Juego"]
    for e in recorrer(J["events"]):
        ms = musica(e)
        if any(x["parameters"][1] in ("musica/partida_1.ogg", AMB) for x in ms):
            e["actions"] = [x for x in e["actions"] if not (x["type"]["value"] == "PlayMusicCanal" and x["parameters"][2] in ("1", "2"))]
            e["actions"] += [play(AMB, "1", VOL_AMB), play(CAPA, "2", VOL_CAPA)]
            cambios.append("Juego: inicio -> ambiente_juego + capa")
        elif any(x["parameters"][1] in VIEJAS for x in ms) and not e.get("disabled"):
            e["disabled"] = True
            cambios.append("Juego: desactivado el cambio a " + ms[0]["parameters"][1])
    grupo = next(g for g in J["events"] if g.get("type", "").endswith("Group") and any(
        x["parameters"][1] == AMB for e in recorrer(g.get("events", [])) for x in musica(e)))
    if not any(e.get("type", "").endswith("Comment") and e.get("comment", "").startswith(MK) for e in grupo["events"]):
        grupo["events"].insert(0, {"type": "BuiltinCommonInstructions::Comment",
                                   "color": {"b": 109, "g": 230, "r": 255, "textB": 0, "textG": 0, "textR": 0},
                                   "comment": MK + " · Música de partida (todos los modos): ambiente_juego.wav en el canal 1 (45) y "
                                   "ambiente_juego_capa.wav encima, en el canal 2 (40), en bucle. Los cambios por infestación y el "
                                   "final quedan desactivados para no cortar el ambiente.", "comment2": ""})

    # ---- el canal 2 se apaga fuera de la partida
    for n in ("Titulo", "Menu", "Online", "Resultados"):
        for e in recorrer(L[n]["events"]):
            if musica(e) and any(c["type"]["value"] == "DepartScene" for c in e.get("conditions", [])):
                if not any(x["type"]["value"] == "StopMusicCanal" and x["parameters"][1] == "2" for x in e["actions"]):
                    e["actions"].insert(0, parar2())
                    cambios.append(n + ": para el canal 2")

    tmp = PRY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=2))
    os.replace(tmp, PRY)

    # ---- manifiesto
    m = json.load(open(MANI, encoding="utf-8"))
    ext = m["format"].setdefault("extensions", [m["format"]["extension"]])
    if ".mp3" not in ext:
        ext.append(".mp3")
    for i, p in (("MUSICA_MENU_SOUNDTRACK2D", MENU), ("MUSICA_PARTIDA_AMBIENTE", AMB), ("MUSICA_PARTIDA_AMBIENTE_CAPA", CAPA)):
        if not any(x["path"] == p for x in m["music"]):
            m["music"].append({"id": i, "path": p, "loop": True, "priority": "P1"})
    open(MANI, "w", encoding="utf-8", newline="\r\n").write(json.dumps(m, ensure_ascii=False, indent=2))  # CRLF, sin salto final, como estaba

    print("Fase 66 aplicada:\n  " + ("\n  ".join(cambios) if cambios else "sin cambios (ya estaba)"))


if __name__ == "__main__":
    main()
