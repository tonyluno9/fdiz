"""FDI-Z · Fase 81 · Escape (Local) vuelve a tener selector de personajes (deshace esa parte de la fase 72).
Correr con GDevelop cerrado, después de la 80:
    python gdevelop/scripts/fase81_escape_con_selector.py

* Menú: elegir Escape (Local) vuelve a ir a «unirse» (selección de personajes y equipo) en lugar de saltar a la
  dificultad con el equipo fijo.
* En la dificultad, Escape (tecla) vuelve otra vez al equipo, como en los demás modos.
Lo demás de la fase 72 (Historia con cambio de personaje, AK-47) no se toca. Idempotente.
"""
import json
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
FIJO = {("ModVarSceneTxt", "Paso"), ("ModVarScene", "Sel"), ("ModVarScene", "S1Pj"), ("ModVarScene", "S2Pj"), ("ModVarScene", "S3Pj"),
        ("ModVarScene", "S4Pj"), ("ModVarScene", "S2Ctl"), ("ModVarScene", "S3Ctl"), ("ModVarScene", "S4Ctl")}


def recorrer(evs):
    for e in evs:
        yield e
        yield from recorrer(e.get("events", []))


def tiene(e, t, p):
    return any(x["type"]["value"] == t and x["parameters"][:len(p)] == p for x in e.get("conditions", []) + e.get("actions", []))


def main():
    d = json.load(open(PRY, encoding="utf-8"))
    M = next(l for l in d["layouts"] if l["name"] == "Menu")
    n = 0
    for e in recorrer(M["events"]):
        if (tiene(e, "VarSceneTxt", ["Paso", "=", '"jefetipo"']) and tiene(e, "VarScene", ["JT", "=", "0"])
                and tiene(e, "ModVarGlobalTxt", ["Modo", "=", '"escape"']) and tiene(e, "ModVarSceneTxt", ["Paso", "=", '"dificultad"'])):
            e["actions"] = [{"type": {"value": "ModVarSceneTxt"}, "parameters": ["Paso", "=", '"unirse"']}] + \
                [x for x in e["actions"] if (x["type"]["value"], x["parameters"][0]) not in FIJO]
            n += 1
    me = M["events"]
    me[:] = [e for e in me if not (tiene(e, "VarSceneTxt", ["Paso", "=", '"dificultad"']) and tiene(e, "VarGlobalTxt", ["Modo", "=", '"escape"'])
                                    and tiene(e, "ModVarSceneTxt", ["Paso", "=", '"jefetipo"']))]
    for e in me:
        if tiene(e, "VarSceneTxt", ["Paso", "=", '"dificultad"']) and tiene(e, "ModVarSceneTxt", ["Paso", "=", '"equipo"']):
            e["conditions"] = [x for x in e["conditions"] if not (x["type"]["value"] == "VarGlobalTxt" and x["parameters"][:3] == ["Modo", "!=", '"escape"'])]
    tmp = PRY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=2))
    os.replace(tmp, PRY)
    print("Fase 81 aplicada. Escape local con selector en %d eventos." % n)


if __name__ == "__main__":
    main()
