"""Fase 61 · Modo Historia: conversación con el profe Canepa en el camión (misión 5 de 6). Idempotente.

Uso (desde la carpeta fdiz, con GDevelop CERRADO), después de fase55_historia.py (que pone la misión en el orden):
    python gdevelop/scripts/fase61_canepa.py
    node gdevelop/scripts/prueba_canepa.js
Va al final de la cadena (después de la fase 60). Si se vuelve a correr fase40_profesores.py, fase56_interaccion.py o
fase25_online.py, correr esta fase otra vez (vuelve a incrustar profes.js y usar.js, y saca los eventos de la compuerta).

Qué hace en Juego:
  * Incrusta scripts/canepa.js (FDIZ-FASE61-MOD y FDIZ-FASE61-TICK al inicio, sin compuerta de host: cada máquina dibuja
    las burbujas y pone las voces; el host lleva la secuencia).
  * Objeto DlgDib (dibujador, copia de ProfDib) para la colita de la burbuja.
  * Vuelve a incrustar profes.js (FDIZ-FASE40-MOD) y usar.js (FDIZ-FASE56-MOD), que ahora preguntan a canepa.js si
    Canepa está reservado para la charla (en Historia no se le puede reclutar ni rechazar antes de la misión 5).
La misión en sí (orden, HUD, letrero, objetivo junto a Canepa, evento que abre la charla) está en fase55_historia.py.
"""
import copy, datetime, json, os, shutil

AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
MK = "FDIZ-FASE61"


def js(code, marca):
    return {"type": "BuiltinCommonInstructions::JsCode", "inlineCode": "/*" + marca + "*/\n" + code,
            "parameterObjects": "", "useStrict": True, "eventsSheetExpanded": False}


def recorrer(lst):
    for e in lst:
        yield e
        yield from recorrer(e.get("events", []))


def es_marca(e, marca):
    return e.get("type", "").endswith("JsCode") and e.get("inlineCode", "").startswith("/*" + marca)


def main():
    d = json.load(open(PRY, encoding="utf-8"))
    resp = os.path.join(AQUI, "..", "respaldos")
    os.makedirs(resp, exist_ok=True)
    bak = os.path.join(resp, "antes_de_fase61_%s.json" % datetime.date.today().strftime("%Y%m%d"))
    if not os.path.exists(bak):
        shutil.copy(PRY, bak)
    J = next(l for l in d["layouts"] if l["name"] == "Juego")
    if not any(v["name"] == "CanepaCharla" for v in J["variables"]):
        raise SystemExit("Falta la misión de Canepa: corre antes fase55_historia.py")
    hecho = []

    # objeto para la colita de la burbuja
    ob = {o["name"]: o for o in J["objects"]}
    if "DlgDib" not in ob:
        t = copy.deepcopy(ob["ProfDib"]); t["name"] = "DlgDib"; J["objects"].append(t); hecho.append("DlgDib")

    # módulo y llamada por cuadro (arriba de todo; si una fase anterior los metió en la compuerta de host, se sacan)
    ev = J["events"]
    for e in list(recorrer(ev)):
        for sub in (e.get("events", []),):
            sub[:] = [x for x in sub if not (es_marca(x, MK + "-MOD") or es_marca(x, MK + "-TICK"))]
    ev[:] = [x for x in ev if not (es_marca(x, MK + "-MOD") or es_marca(x, MK + "-TICK"))]
    k = next((i for i, e in enumerate(ev) if es_marca(e, "FDIZ-FASE56-MOD")), 0)
    ev[k:k] = [js(open(os.path.join(AQUI, "canepa.js"), encoding="utf-8").read(), MK + "-MOD"),
               js("if (gdjs.fdizCanepa) gdjs.fdizCanepa.tick(runtimeScene);", MK + "-TICK")]
    hecho.append("canepa.js")

    # profes.js y usar.js actualizados (Canepa reservado en Historia hasta la charla)
    for marca, archivo in (("FDIZ-FASE40-MOD", "profes.js"), ("FDIZ-FASE56-MOD", "usar.js")):
        m = next((e for e in recorrer(ev) if es_marca(e, marca)), None)
        if m is None:
            raise SystemExit("No encontré el evento " + marca)
        m["inlineCode"] = "/*" + marca + "*/\n" + open(os.path.join(AQUI, archivo), encoding="utf-8").read()
        hecho.append(archivo)

    tmp = PRY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=2))
    os.replace(tmp, PRY)
    print("Fase 61 aplicada:", hecho)


if __name__ == "__main__":
    main()
