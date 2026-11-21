"""Fase 51 · Bloque Jugabilidad y mecánicas, parte 2: habilidades de aliados con clic. Idempotente; va al final de la cadena (después de fase50).

Uso (desde la carpeta fdiz, con GDevelop CERRADO):  python3 gdevelop/scripts/fase51_aliados_hab.py
Crea el pintor "HabDib" (capa HUD) y un evento JavaScript (scripts/aliados_hab.js) justo después del grupo "Entrada (teclado y controles)".
"""
import copy, datetime, json, os, shutil

AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
MK = "FDIZ-FASE51-ALIADOS"


def main():
    d = json.load(open(PRY, encoding="utf-8"))
    resp = os.path.join(AQUI, "..", "respaldos"); os.makedirs(resp, exist_ok=True)
    bak = os.path.join(resp, "antes_de_fase51_%s.json" % datetime.date.today().strftime("%Y%m%d"))
    if not os.path.exists(bak): shutil.copy(PRY, bak)
    J = next(l for l in d["layouts"] if l["name"] == "Juego")
    if not any(o["name"] == "HabDib" for o in J["objects"]):
        o = copy.deepcopy(next(o for o in J["objects"] if o["name"] == "JfDibO")); o["name"] = "HabDib"; J["objects"].append(o)
    if not any(i["name"] == "HabDib" for i in J["instances"]):
        i = copy.deepcopy(next(i for i in J["instances"] if i["name"] == "JfDibO")); i["name"] = "HabDib"; J["instances"].append(i)
    ev = J["events"]
    ev[:] = [e for e in ev if not (e["type"].endswith("JsCode") and e.get("inlineCode", "").startswith("/*" + MK))]
    k = next(i for i, e in enumerate(ev) if e["type"].endswith("Group") and e.get("name", "").startswith("Entrada (teclado y controles)"))
    ev.insert(k + 1, {"type": "BuiltinCommonInstructions::JsCode", "inlineCode": "/*" + MK + "*/\n" + open(os.path.join(AQUI, "aliados_hab.js"), encoding="utf-8").read(),
                      "parameterObjects": "", "useStrict": True, "eventsSheetExpanded": False})
    json.dump(d, open(PRY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("OK fase51 (habilidades de aliados con clic)")


main()
