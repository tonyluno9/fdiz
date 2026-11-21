"""Fase 53 · Bloque Jugabilidad y mecánicas, parte 4: flechas de aliados fuera de pantalla. Idempotente; va al final de la cadena (después de fase52).

Uso (desde la carpeta fdiz, con GDevelop CERRADO):  python3 gdevelop/scripts/fase53_flechas.py
Crea el pintor "FlechasDib" (capa HUD) y un evento JavaScript (scripts/flechas.js) justo después del evento del minimapa (fase 50).
"""
import copy, datetime, json, os, shutil

AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
MK = "FDIZ-FASE53-FLECHAS"


def main():
    d = json.load(open(PRY, encoding="utf-8"))
    resp = os.path.join(AQUI, "..", "respaldos"); os.makedirs(resp, exist_ok=True)
    bak = os.path.join(resp, "antes_de_fase53_%s.json" % datetime.date.today().strftime("%Y%m%d"))
    if not os.path.exists(bak): shutil.copy(PRY, bak)
    J = next(l for l in d["layouts"] if l["name"] == "Juego")
    if not any(o["name"] == "FlechasDib" for o in J["objects"]):
        o = copy.deepcopy(next(o for o in J["objects"] if o["name"] == "JfDibO")); o["name"] = "FlechasDib"; J["objects"].append(o)
    if not any(i["name"] == "FlechasDib" for i in J["instances"]):
        i = copy.deepcopy(next(i for i in J["instances"] if i["name"] == "JfDibO")); i["name"] = "FlechasDib"; J["instances"].append(i)
    ev = J["events"]
    ev[:] = [e for e in ev if not (e["type"].endswith("JsCode") and e.get("inlineCode", "").startswith("/*" + MK))]
    k = next(i for i, e in enumerate(ev) if e["type"].endswith("JsCode") and e.get("inlineCode", "").startswith("/*FDIZ-FASE50-MINIMAPA"))
    ev.insert(k + 1, {"type": "BuiltinCommonInstructions::JsCode", "inlineCode": "/*" + MK + "*/\n" + open(os.path.join(AQUI, "flechas.js"), encoding="utf-8").read(),
                      "parameterObjects": "", "useStrict": True, "eventsSheetExpanded": False})
    json.dump(d, open(PRY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("OK fase53 (flechas de aliados)")


main()
