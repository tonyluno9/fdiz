"""FDI-Z · Fase 86 · Derrota en silencio (solo el golpe de miedo) y pausa total también con el tutorial abierto.
Correr con GDevelop cerrado, después de la 85:
    python gdevelop/scripts/fase86_derrota_y_pausa_tutorial.py

* Resultados (derrota): ya no suena musica/derrota.ogg. Se detienen la música (canales 1 y 2) y las voces / alarma que
  vinieran de la partida (canales 7, 8 y 9), y el video de derrota queda sin sonido. Lo único que suena es el golpe de
  game_over.ogg (sfx.js, al entrar a Resultados) y después silencio.
* pausa_total.js (FDIZ-FASE85-PAUSA): también pausa con el tutorial abierto, y congela el reloj de diálogos, historia,
  cinemáticas y la charla con Canepa (antes las voces seguían con el tutorial en pantalla).
* Puertas restringidas (P47 dirección, P59 conserjería): las balas y perdigones también las rompen (cine_ui_escape.js y el
  evento de balazo a puertas).
Idempotente.
"""
import json
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")


def recorrer(evs):
    for e in evs:
        yield e
        yield from recorrer(e.get("events", []))


def leer(n):
    return open(os.path.join(AQUI, n), encoding="utf-8").read()


def main():
    d = json.load(open(PRY, encoding="utf-8"))
    R = next(l for l in d["layouts"] if l["name"] == "Resultados")
    J = next(l for l in d["layouts"] if l["name"] == "Juego")

    # derrota: sin música
    n = 0
    for e in recorrer(R["events"]):
        acts = e.get("actions", [])
        if any(a["type"]["value"] == "PlayMusicCanal" and a["parameters"][1] == "musica/derrota.ogg" for a in acts):
            e["actions"] = [{"type": {"value": "StopMusicCanal"}, "parameters": ["", "1"]},
                            {"type": {"value": "StopMusicCanal"}, "parameters": ["", "2"]},
                            {"type": {"value": "StopSoundCanal"}, "parameters": ["", "7"]},
                            {"type": {"value": "StopSoundCanal"}, "parameters": ["", "8"]},
                            {"type": {"value": "StopSoundCanal"}, "parameters": ["", "9"]}]
            n += 1
    for o in R["objects"]:
        if o["name"] == "VidDerrota":
            o["content"]["volume"] = 0

    # re-incrustar módulos
    for marca, archivo, llamada in (("/*FDIZ-FASE85-PAUSA*/", "pausa_total.js", "gdjs.fdizPausaTotal"),
                                    ("/*FDIZ-FASE85-CINEUI*/", "cine_ui_escape.js", "gdjs.fdizCineUi")):
        ex = [e for e in J["events"] if e.get("type", "").endswith("JsCode") and e.get("inlineCode", "").startswith(marca)]
        assert len(ex) == 1, "falta " + marca
        ex[0]["inlineCode"] = marca + "\n" + leer(archivo) + "\nif (" + llamada + ") " + llamada + ".tick(runtimeScene);\n"

    # balazo a puertas: también las restringidas
    m = 0
    for e in recorrer(J["events"]):
        for c in e.get("conditions", []):
            if c["type"]["value"] == "VarObjetTxt" and c["parameters"][:4] == ["Puerta", "Tipo", "=", '"normal"'] and \
                    any(a["parameters"][:4] == ["Puerta", "Vida", "=", "0"] for a in e.get("actions", [])):
                c["type"] = {"value": "BuiltinCommonInstructions::Or"}
                c["parameters"] = []
                c["subInstructions"] = [
                    {"type": {"inverted": False, "value": "VarObjetTxt"}, "parameters": ["Puerta", "Tipo", "=", '"normal"']},
                    {"type": {"inverted": False, "value": "VarObjetTxt"}, "parameters": ["Puerta", "Tipo", "=", '"restringida"']}]
                e["conditions"].append({"type": {"inverted": False, "value": "VarObjet"}, "parameters": ["Puerta", "Vida", "<", "9999"]})
                m += 1

    tmp = PRY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=2))
    os.replace(tmp, PRY)
    print("Fase 86 aplicada. Música de derrota quitada: %d · puertas restringidas a balazos: %d" % (n, m))


if __name__ == "__main__":
    main()
