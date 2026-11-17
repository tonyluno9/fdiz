"""Fase 35 · Pantalla de dificultad: al mover el mouse sobre una opcion se selecciona (se ilumina igual que con el teclado); el clic ya la acepta. Idempotente."""
import json, os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gd_util import c, a
AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
bak = os.path.join(AQUI, "..", "respaldos", "antes_de_fase35_20261117.json")
if not os.path.exists(bak): shutil.copy(PRY, bak)
d = json.load(open(PRY))
ME = next(l for l in d["layouts"] if l["name"] == "Menu")["events"]
MK = "FDIZ-FASE35"
CMP = "BuiltinCommonInstructions::CompareNumbers"
def marca(k):
    return {"type": "BuiltinCommonInstructions::Comment", "color": {"b": 109, "g": 230, "r": 255, "textB": 0, "textG": 0, "textR": 0}, "comment": MK + "-" + k, "comment2": ""}
if not any(e.get("comment") == MK + "-HOV-D0" for e in ME):
    pm = next(i for i, e in enumerate(ME) if e["type"].endswith("Standard") and not e["conditions"] and any(x["parameters"][:1] == ["PMX"] for x in e["actions"]))
    nuevos = []
    for i, (y0, y1) in enumerate(((240, 445), (445, 641), (641, 835))):
        mov = {"type": {"inverted": False, "value": "BuiltinCommonInstructions::Or"}, "parameters": [],
               "subInstructions": [c(CMP, "MouseX()", "!=", "Variable(PMX)"), c(CMP, "MouseY()", "!=", "Variable(PMY)")]}
        conds = [c("VarSceneTxt", "Paso", "=", '"dificultad"'), mov,
                 c(CMP, "MouseX()", ">=", "720"), c(CMP, "MouseX()", "<", "1200"), c(CMP, "MouseY()", ">=", str(y0)), c(CMP, "MouseY()", "<", str(y1))]
        nuevos += [marca("HOV-D%d" % i), {"type": "BuiltinCommonInstructions::Standard", "conditions": conds, "actions": [a("ModVarScene", "Sel", "=", str(i))], "events": []}]
    ME[pm:pm] = nuevos
json.dump(d, open(PRY, "w"), ensure_ascii=False, indent=2)
print("OK fase 35")
