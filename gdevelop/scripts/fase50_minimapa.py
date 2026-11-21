"""Fase 50 · Bloque Jugabilidad y mecánicas, parte 1: minimapa del modo normal. Idempotente; va al final de la cadena (después de fase49).

Uso (desde la carpeta fdiz, con GDevelop CERRADO):  python3 gdevelop/scripts/fase50_minimapa.py
- Crea el pintor "MmDib" (capa HUD) y un evento JavaScript (scripts/minimapa.js) justo después del grupo "Interfaz: HUD con paneles".
- Usa el sprite "Minimapa" (que ya existía para el Jefe) a la derecha de la pantalla, con aliados, objetivo y cuadro de cámara. Tecla M: mostrar/ocultar.
"""
import copy, datetime, json, os, shutil

AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
MK = "FDIZ-FASE50-MINIMAPA"


def main():
    d = json.load(open(PRY, encoding="utf-8"))
    resp = os.path.join(AQUI, "..", "respaldos"); os.makedirs(resp, exist_ok=True)
    bak = os.path.join(resp, "antes_de_fase50_%s.json" % datetime.date.today().strftime("%Y%m%d"))
    if not os.path.exists(bak): shutil.copy(PRY, bak)
    J = next(l for l in d["layouts"] if l["name"] == "Juego")

    if not any(o["name"] == "MmDib" for o in J["objects"]):
        o = copy.deepcopy(next(o for o in J["objects"] if o["name"] == "JfDibO")); o["name"] = "MmDib"
        J["objects"].append(o)
    if not any(i["name"] == "MmDib" for i in J["instances"]):
        i = copy.deepcopy(next(i for i in J["instances"] if i["name"] == "JfDibO")); i["name"] = "MmDib"
        J["instances"].append(i)

    ev = J["events"]
    ev[:] = [e for e in ev if not (e["type"].endswith("JsCode") and e.get("inlineCode", "").startswith("/*" + MK))]
    k = next(i for i, e in enumerate(ev) if e["type"].endswith("Group") and e.get("name", "").startswith("Interfaz: HUD con paneles"))
    ev.insert(k + 1, {"type": "BuiltinCommonInstructions::JsCode", "inlineCode": "/*" + MK + "*/\n" + open(os.path.join(AQUI, "minimapa.js"), encoding="utf-8").read(),
                      "parameterObjects": "", "useStrict": True, "eventsSheetExpanded": False})
    json.dump(d, open(PRY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("OK fase50 (minimapa)")


main()
