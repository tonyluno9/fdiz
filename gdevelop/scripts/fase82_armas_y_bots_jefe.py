"""FDI-Z · Fase 82 · Balas que llegan lejos, bots que disparan a distancia y bots del modo Jefe que no se atoran.
Correr con GDevelop cerrado, después de la 81:
    python gdevelop/scripts/fase82_armas_y_bots_jefe.py

* Balas y perdigones: chocaban con ChoqueMueble (las cajas de pupitres, sillas y mesas, dentro del grupo Solidos) y se
  borraban ahí, así que en salones y pasillos con muebles solo dañaban de cerca. Ahora solo los detienen Muro y Puerta;
  los demás lanzables (balón, libro, engrapadora) siguen chocando con todo. Alcance de cada arma sin cambios: la escopeta
  es la única corta (~270 px); pistolas y AK-47 llegan a ~500-600 px.
* Bots con arma de fuego (todos los modos): antes solo disparaban con el zombi a 95 px y caminaban hasta pegarse a él.
  Ahora disparan en cuanto lo ven dentro de su alcance (Alcance x 240 px) y no se acercan a menos de ~300 px.
* Modo Jefe: evento FDIZ-FASE82-BOTSJEFE (scripts/bots_jefe.js) entre «Bots: objetivos y puertas» y «Bots: curar
  mordidos». Movimiento por ruta, lugar y personalidad propios, reacción a zombis y desatasco (ver el archivo).
  El bot más cercano al objetivo va a cumplirlo; los demás lo cubren.
* Llaves de la conserjería: solo las tomaba un humano, así que en el modo Jefe (4 bots) la primera misión nunca se
  cumplía. medios.js: en el modo Jefe también las toman los bots.
Idempotente.
"""
import json
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
MARCA = "/*FDIZ-FASE82-BOTSJEFE*/"


def c(t, *p, inv=False):
    return {"type": {"inverted": inv, "value": t}, "parameters": list(p)}


def a(t, *p):
    return {"type": {"value": t}, "parameters": list(p)}


def recorrer(evs):
    for e in evs:
        yield e
        yield from recorrer(e.get("events", []))


def tiene(e, t, p):
    return any(x["type"]["value"] == t and x["parameters"][:len(p)] == p for x in e.get("conditions", []) + e.get("actions", []))


def main():
    d = json.load(open(PRY, encoding="utf-8"))
    J = next(l for l in d["layouts"] if l["name"] == "Juego")
    ev = J["events"]

    # ---- 1) balas y perdigones: solo Muro y Puerta las detienen
    n1 = 0
    for e in recorrer(ev):
        hijos = e.get("events", [])
        for i, h in enumerate(hijos):
            if tiene(h, "CollisionNP", ["Proyectil", "Solidos"]) and tiene(h, "ModVarObjet", ["Proyectil", "Pego", "=", "1"]):
                if not tiene(h, "VarObjetTxt", ["Proyectil", "Tipo", "=", '"bala"']):
                    h["conditions"] += [c("VarObjetTxt", "Proyectil", "Tipo", "=", '"bala"', inv=True),
                                        c("VarObjetTxt", "Proyectil", "Tipo", "=", '"perdigon"', inv=True)]
                    for obj in ("Muro", "Puerta"):
                        hijos.insert(i + 1, {"type": "BuiltinCommonInstructions::Standard",
                                             "conditions": [c("CollisionNP", "Proyectil", obj, "", "")],
                                             "actions": [a("ModVarObjet", "Proyectil", "Pego", "=", "1")]})
                    n1 += 1
                break

    # ---- 2) bots con arma de fuego disparan a distancia (todos los modos)
    n2 = 0
    for e in recorrer(ev):
        hijos = e.get("events", [])
        for i, h in enumerate(hijos):
            if tiene(h, "VarScene", ["Bloq", "=", "0"]) and tiene(h, "BuiltinCommonInstructions::CompareNumbers", ["Sup.Distance(Zombies)", ">", "70"]):
                for x in h["conditions"]:
                    if x["parameters"][:3] == ["Sup.Distance(Zombies)", ">", "70"]:
                        x["parameters"][2] = "70 + 230 * Sup.Variable(ArmaFuego)"
                        n2 += 1
            if (tiene(h, "VarScene", ["Bloq", "=", "0"]) and tiene(h, "BuiltinCommonInstructions::CompareNumbers", ["Sup.Distance(Zombies)", "<=", "95"])
                    and tiene(h, "ModVarObjet", ["Sup", "QuierePegar", "=", "1"])):
                nuevo = {"type": "BuiltinCommonInstructions::Standard",
                         "conditions": [c("VarScene", "Bloq", "=", "0"), c("VarObjet", "Sup", "ArmaFuego", "=", "1"),
                                        c("BuiltinCommonInstructions::CompareNumbers", "Sup.Distance(Zombies)", "<=", "Sup.Variable(Alcance) * 240")],
                         "actions": [a("ModVarObjet", "Sup", "QuierePegar", "=", "1")]}
                if not any(tiene(x, "BuiltinCommonInstructions::CompareNumbers", ["Sup.Distance(Zombies)", "<=", "Sup.Variable(Alcance) * 240"]) for x in hijos):
                    hijos.insert(i + 1, nuevo)
                    n2 += 1
                break

    # ---- 3) bots del modo Jefe
    codigo = open(os.path.join(AQUI, "bots_jefe.js"), encoding="utf-8").read()
    inline = MARCA + "\n" + codigo + "\nif (gdjs.fdizBotsJefe) gdjs.fdizBotsJefe.tick(runtimeScene);\n"
    js = [e for e in ev if e.get("type", "").endswith("JsCode") and e.get("inlineCode", "").startswith(MARCA)]
    if js:
        js[0]["inlineCode"] = inline
    else:
        k = next(i for i, e in enumerate(ev) if e.get("name") == "Bots: curar mordidos")
        ev.insert(k, {"type": "BuiltinCommonInstructions::JsCode", "inlineCode": inline, "parameterObjects": "",
                      "useStrict": True, "eventsSheetExpanded": False})

    # ---- 4) llaves: en el modo Jefe también las toman los bots (medios.js, FDIZ-FASE46-MOD)
    med = open(os.path.join(AQUI, "medios.js"), encoding="utf-8").read()
    for e in recorrer(ev):
        if e.get("type", "").endswith("JsCode") and e.get("inlineCode", "").startswith("/*FDIZ-FASE46-MOD*/"):
            e["inlineCode"] = "/*FDIZ-FASE46-MOD*/\n" + med

    tmp = PRY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=2))
    os.replace(tmp, PRY)
    print("Fase 82 aplicada. Balas: %d · bots con arma: %d · bots del Jefe: %s" % (n1, n2, "actualizado" if js else "agregado"))


if __name__ == "__main__":
    main()
