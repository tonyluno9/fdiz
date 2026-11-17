"""Fase 38 · Pantalla "Unanse": el icono Y/P sube un poco; las siluetas de los 4 jugadores se centran en su tarjeta y bajan un poco. Idempotente."""
import json, os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gd_util import c, a
AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
bak = os.path.join(AQUI, "..", "respaldos", "antes_de_fase38_20261117.json")
if not os.path.exists(bak): shutil.copy(PRY, bak)
d = json.load(open(PRY))
M = next(l for l in d["layouts"] if l["name"] == "Menu")
ME = M["events"]
MK = "FDIZ-FASE38"
# icono Y/P mas arriba (antes y 770)
for i in M["instances"]:
    if i["name"] == "SlotAlt": i["y"] = 745
# siluetas: en "unirse" se corrigen a mano segun la imagen (vacio se ve ~15 px a la izquierda, silueta ~9 px); fuera de "unirse" se dejan como estaban
def marca(k):
    return {"type": "BuiltinCommonInstructions::Comment", "color": {"b": 109, "g": 230, "r": 255, "textB": 0, "textG": 0, "textR": 0}, "comment": MK + "-" + k, "comment2": ""}
if not any(e.get("comment") == MK + "-RETRATOS" for e in ME):
    nuevos = [marca("RETRATOS")]
    for k in (1, 2, 3, 4):
        base = 190 + 440 * (k - 1)
        sl = c("VarObjet", "SelRetrato", "Slot", "=", str(k))
        for conds, dx, y in (([c("VarSceneTxt", "Paso", "=", '"unirse"'), c("VarScene", "S%dCtl" % k, "=", "-1")], 15, 300),
                             ([c("VarSceneTxt", "Paso", "=", '"unirse"'), c("VarScene", "S%dCtl" % k, "!=", "-1")], 9, 300),
                             ([c("VarSceneTxt", "Paso", "!=", '"unirse"')], 0, 275)):
            nuevos.append({"type": "BuiltinCommonInstructions::Standard", "conditions": [sl] + conds,
                           "actions": [a("MettreX", "SelRetrato", "=", str(base + dx)), a("MettreY", "SelRetrato", "=", str(y))], "events": []})
    idx = next(i for i, e in enumerate(ME) if e.get("comment") == "FDIZ-FASE37-CTL")
    ME[idx:idx] = nuevos
json.dump(d, open(PRY, "w"), ensure_ascii=False, indent=2)
print("OK fase 38")
