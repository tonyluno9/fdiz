"""Fase 63 · Color de los letreros de eventos: rojo solo para infección y "la FDI se está llenando"; verde todo lo demás.
Idempotente. Todos los modos.

Uso (desde la carpeta fdiz, con GDevelop CERRADO):
    python gdevelop/scripts/fase63_avisos.py
    node gdevelop/scripts/prueba_avisos.js
Si se vuelve a correr una fase que regenere el grupo "HUD" de Juego o fase25_online.py, correr esta fase otra vez.

Por qué salían rojos: todos los letreros (variable Banner) se muestran con el objeto TxtBanner, cuyo color era rojo
fijo (255;80;80) y ningún evento lo cambiaba. Los escriben eventos de varios grupos (objetivos, final, mordidos,
habilidades, HUD, puertas, unirse) y los módulos profes.js y medios.js, así que se corrige en el único lugar por donde
pasan todos: donde se muestra el letrero.
  * TxtBanner: color por defecto verde (110;230;110).
  * scripts/avisos.js (FDIZ-FASE63-MOD arriba de Juego): clasifica el texto normalizado (sin acentos, mayúsculas ni signos).
  * FDIZ-FASE63-COLOR: dentro del evento del grupo "HUD" que pone el texto del letrero; pone rojo o verde.
No cambia ningún texto ni cuándo aparece.
"""
import datetime, json, os, shutil

AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
MK = "FDIZ-FASE63"
VERDE = (110, 230, 110)


def js(code, marca):
    return {"type": "BuiltinCommonInstructions::JsCode", "inlineCode": "/*" + marca + "*/\n" + code,
            "parameterObjects": "", "useStrict": True, "eventsSheetExpanded": False}


def recorrer(lst):
    for e in lst:
        yield e
        yield from recorrer(e.get("events", []))


def es_js(e, marca):
    return e.get("type", "").endswith("JsCode") and e.get("inlineCode", "").startswith("/*" + marca)


def quitar(lst, marca):
    lst[:] = [e for e in lst if not es_js(e, marca)]
    for e in lst:
        if e.get("events"):
            quitar(e["events"], marca)


def main():
    d = json.load(open(PRY, encoding="utf-8"))
    resp = os.path.join(AQUI, "..", "respaldos")
    os.makedirs(resp, exist_ok=True)
    bak = os.path.join(resp, "antes_de_fase63_%s.json" % datetime.date.today().strftime("%Y%m%d"))
    if not os.path.exists(bak):
        shutil.copy(PRY, bak)
    J = next(l for l in d["layouts"] if l["name"] == "Juego")

    # color por defecto del letrero: verde (lo rojo lo decide avisos.js)
    o = next(x for x in J["objects"] if x["name"] == "TxtBanner")
    o["color"] = {"r": VERDE[0], "g": VERDE[1], "b": VERDE[2]}
    if "content" in o:
        o["content"]["color"] = "%d;%d;%d" % VERDE

    ev = J["events"]
    quitar(ev, MK + "-MOD"); quitar(ev, MK + "-COLOR")
    k = next((i for i, e in enumerate(ev) if es_js(e, "FDIZ-FASE56-MOD")), 0)
    ev.insert(k, js(open(os.path.join(AQUI, "avisos.js"), encoding="utf-8").read(), MK + "-MOD"))

    # el evento del HUD que muestra el letrero
    mostrar = [e for e in recorrer(ev)
               if any(c["type"]["value"] == "CompareTimer" and c["parameters"][1:3] == ['"banner"', "<"] for c in e.get("conditions", []))
               and any(a["type"]["value"] == "TextObject::String" and a["parameters"][:1] == ["TxtBanner"] for a in e.get("actions", []))]
    if len(mostrar) != 1:
        raise SystemExit("Esperaba un evento que muestra TxtBanner; encontré %d" % len(mostrar))
    mostrar[0].setdefault("events", []).append(js("if (gdjs.fdizAvisos) gdjs.fdizAvisos.aplicar(runtimeScene);", MK + "-COLOR"))

    tmp = PRY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=2))
    os.replace(tmp, PRY)
    print("Fase 63 aplicada: TxtBanner verde por defecto, avisos.js y color al mostrar el letrero.")


if __name__ == "__main__":
    main()
