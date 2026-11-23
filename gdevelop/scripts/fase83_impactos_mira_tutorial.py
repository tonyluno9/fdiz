"""FDI-Z · Fase 83 · Balas que pegan a cualquier zombi, mira en el cursor y tutorial de controles.
Correr con GDevelop cerrado, después de la 82:
    python gdevelop/scripts/fase83_impactos_mira_tutorial.py

* Impactos (balas, perdigones y lanzables): la condición era «Comparar dos números» con
  DistanceBetweenPositions(Zombies.X(), Zombies.Y() - 40, Proyectil.X(), Proyectil.Y()). Esa condición no filtra por
  zombi: GDevelop toma UN solo zombi del grupo (el primero del último tipo que haya en el mapa), así que la bala solo
  pegaba si pasaba junto a ese zombi y atravesaba a los demás. Ahora es la condición de objeto «Distancia» (Zombies,
  Proyectil), que revisa cada zombi por su centro; radio 72 px para balas y perdigones (46 para lanzables).
* Mira: armas.js (FDIZ-FASE62-MOD). Con ratón la mira va donde está el cursor, con cualquier arma, y se oculta la flecha
  del sistema durante la partida.
* Tutorial: evento FDIZ-FASE83-TUTORIAL (scripts/tutorial.js) al final de la escena Juego.
Idempotente.
"""
import json
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
VIEJA = "DistanceBetweenPositions(Zombies.X(), Zombies.Y() - 40, Proyectil.X(), Proyectil.Y())"
MARCA = "/*FDIZ-FASE83-TUTORIAL*/"
# radio desde el centro del zombi: lanzables 46 px como antes; balas y perdigones 72 (antes 62 desde un punto fijo a
# 40 px de los pies: en zombis grandes como el conserje la bala por el pecho quedaba justo en el borde)
RADIO = "46 + 26 * min(1, Proyectil.Variable(Golpes))"


def recorrer(evs):
    for e in evs:
        yield e
        yield from recorrer(e.get("events", []))


def main():
    d = json.load(open(PRY, encoding="utf-8"))
    J = next(l for l in d["layouts"] if l["name"] == "Juego")
    ev = J["events"]

    n = 0
    for e in recorrer(ev):
        cs = e.get("conditions", [])
        for k, c in enumerate(cs):
            if c["type"]["value"] == "BuiltinCommonInstructions::CompareNumbers" and c["parameters"][0] == VIEJA:
                cs[k] = {"type": {"inverted": False, "value": "Distance"},
                         "parameters": ["Zombies", "Proyectil", RADIO, ""]}
                n += 1
            elif c["type"]["value"] == "Distance" and c["parameters"][:2] == ["Zombies", "Proyectil"] and c["parameters"][2] != RADIO:
                c["parameters"][2] = RADIO
                n += 1

    codigo = open(os.path.join(AQUI, "armas.js"), encoding="utf-8").read()
    js = [e for e in recorrer(ev) if e.get("type", "").endswith("JsCode") and e.get("inlineCode", "").startswith("/*FDIZ-FASE62-MOD*/")]
    assert len(js) == 1, "no encuentro FDIZ-FASE62-MOD"
    js[0]["inlineCode"] = "/*FDIZ-FASE62-MOD*/\n" + codigo

    tuto = MARCA + "\n" + open(os.path.join(AQUI, "tutorial.js"), encoding="utf-8").read() + \
        "\nif (gdjs.fdizTuto) gdjs.fdizTuto.tick(runtimeScene);\n"
    t = [e for e in ev if e.get("type", "").endswith("JsCode") and e.get("inlineCode", "").startswith(MARCA)]
    if t:
        t[0]["inlineCode"] = tuto
    else:
        ev.append({"type": "BuiltinCommonInstructions::JsCode", "inlineCode": tuto, "parameterObjects": "",
                   "useStrict": True, "eventsSheetExpanded": False})

    tmp = PRY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=2))
    os.replace(tmp, PRY)
    print("Fase 83 aplicada. Condiciones de impacto cambiadas: %d · tutorial %s" % (n, "actualizado" if t else "agregado"))


if __name__ == "__main__":
    main()
