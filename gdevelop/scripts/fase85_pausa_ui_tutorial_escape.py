"""FDI-Z · Fase 85 · Pausa total, interfaz oculta en cinemáticas, tutorial por pasos y Escape sin armas de fuego.
Correr con GDevelop cerrado, después de la 84:
    python gdevelop/scripts/fase85_pausa_ui_tutorial_escape.py

* pausa_total.js (evento FDIZ-FASE85-PAUSA): con la pausa abierta se detiene todo el sonido y los videos; al cerrarla sigue.
* tutorial.js (FDIZ-FASE83-TUTORIAL): 3 cuadros, uno a la vez (moverse, atacar con Tony de ejemplo, más controles).
  Objeto nuevo TutoTony: copia de las animaciones de Tony del objeto Sup (quieto, caminar, pegar y pistola de lado), en
  bucle, sin comportamientos ni variables (solo se dibuja en el tutorial).
* cine_ui_escape.js (FDIZ-FASE85-CINEUI, el último evento de la escena): en cinemáticas se esconde la interfaz; en Escape
  no hay pistolas, escopeta ni AK-47.
Idempotente.
"""
import copy
import json
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
ANIMS = ["tony_quieto", "tony_caminar_lado", "tony_pegar_lado", "tony_pistola_lado"]


def recorrer(evs):
    for e in evs:
        yield e
        yield from recorrer(e.get("events", []))


def leer(n):
    return open(os.path.join(AQUI, n), encoding="utf-8").read()


def js(marca, codigo):
    return {"type": "BuiltinCommonInstructions::JsCode", "inlineCode": marca + "\n" + codigo, "parameterObjects": "",
            "useStrict": True, "eventsSheetExpanded": False}


def main():
    d = json.load(open(PRY, encoding="utf-8"))
    J = next(l for l in d["layouts"] if l["name"] == "Juego")
    ev = J["events"]

    # TutoTony
    sup = next(o for o in J["objects"] if o["name"] == "Sup")
    tt = copy.deepcopy(sup)
    tt["name"] = "TutoTony"; tt["behaviors"] = []; tt["variables"] = []; tt["effects"] = []
    tt["animations"] = [copy.deepcopy(a) for a in sup["animations"] if a["name"] in ANIMS]
    for a in tt["animations"]:
        for dr in a["directions"]:
            dr["looping"] = True
    J["objects"] = [o for o in J["objects"] if o["name"] != "TutoTony"] + [tt]

    # tutorial (re-incrustar)
    t = [e for e in ev if e.get("type", "").endswith("JsCode") and e.get("inlineCode", "").startswith("/*FDIZ-FASE83-TUTORIAL*/")]
    assert len(t) == 1, "falta el tutorial de la fase 83"
    t[0]["inlineCode"] = "/*FDIZ-FASE83-TUTORIAL*/\n" + leer("tutorial.js") + "\nif (gdjs.fdizTuto) gdjs.fdizTuto.tick(runtimeScene);\n"

    # pausa total y, al final, interfaz de cinemáticas / Escape sin armas de fuego
    for marca, archivo, llamada in (("/*FDIZ-FASE85-PAUSA*/", "pausa_total.js", "gdjs.fdizPausaTotal"),
                                    ("/*FDIZ-FASE85-CINEUI*/", "cine_ui_escape.js", "gdjs.fdizCineUi")):
        cod = leer(archivo) + "\nif (" + llamada + ") " + llamada + ".tick(runtimeScene);\n"
        ex = [e for e in ev if e.get("type", "").endswith("JsCode") and e.get("inlineCode", "").startswith(marca)]
        if ex:
            ex[0]["inlineCode"] = marca + "\n" + cod
            ev.remove(ex[0]); ev.append(ex[0])
        else:
            ev.append(js(marca, cod))

    # revisión de balas contra puertas justo después de disparar (antes de que el evento de proyectiles las borre)
    MB = "/*FDIZ-FASE85-BALAS*/"
    for e in [e for e in ev if e.get("type", "").endswith("JsCode") and e.get("inlineCode", "").startswith(MB)]:
        ev.remove(e)
    k = next(i for i, e in enumerate(ev) if e.get("name") == "Combate: pegar")
    ev.insert(k + 1, js(MB, "if (gdjs.fdizCineUi && gdjs.fdizCineUi.balas) gdjs.fdizCineUi.balas(runtimeScene);\n"))

    tmp = PRY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=2))
    os.replace(tmp, PRY)
    print("Fase 85 aplicada. TutoTony con %d animaciones." % len(tt["animations"]))


if __name__ == "__main__":
    main()
