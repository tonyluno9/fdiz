"""Fase 36 · Selector de personajes: al pasar el mouse sobre un retrato se muestra su video, nombre y habilidades (vista previa) y el retrato se resalta ligeramente. Idempotente.
Variable de escena HV (-1 = sin vista previa, 0..7 = personaje bajo el mouse). El clic sigue eligiendo como antes."""
import json, os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gd_util import c, a
AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
bak = os.path.join(AQUI, "..", "respaldos", "antes_de_fase36_20261117.json")
if not os.path.exists(bak): shutil.copy(PRY, bak)
d = json.load(open(PRY))
M = next(l for l in d["layouts"] if l["name"] == "Menu")
ME = M["events"]
MK = "FDIZ-FASE36"
CMP = "BuiltinCommonInstructions::CompareNumbers"
STD = "BuiltinCommonInstructions::Standard"
PJ = [("tony", "TONY"), ("miranda", "MIRANDA"), ("cesar", "CÉSAR"), ("alan", "ALAN"), ("castillo", "CASTILLO"), ("alessandro", "ALESSANDRO"), ("gabo", "GABO"), ("carlos", "CARLOS")]
if not any(v["name"] == "HV" for v in M["variables"]):
    M["variables"].append({"name": "HV", "type": "number", "value": -1})
def marca(k):
    return {"type": "BuiltinCommonInstructions::Comment", "color": {"b": 109, "g": 230, "r": 255, "textB": 0, "textG": 0, "textR": 0}, "comment": MK + "-" + k, "comment2": ""}
def hay(k): return any(e.get("comment") == MK + "-" + k for e in ME)
def std(conds, acts): return {"type": STD, "conditions": conds, "actions": acts, "events": []}
EQ = c("VarSceneTxt", "Paso", "=", '"equipo"')
def orr(subs): return {"type": {"inverted": False, "value": "BuiltinCommonInstructions::Or"}, "parameters": [], "subInstructions": subs}

# 1 · detectar el retrato bajo el mouse (antes de que se actualice PMX/PMY) y limpiar
if not hay("SET"):
    pm = next(i for i, e in enumerate(ME) if e["type"].endswith("Standard") and not e["conditions"] and any(x["parameters"][:1] == ["PMX"] for x in e["actions"]))
    nuevos = [marca("SET")]
    for i in range(8):
        x0, y0 = 1105 + 171 * (i % 4), 212 + 176 * (i // 4)
        nuevos.append(std([EQ, orr([c(CMP, "MouseX()", "!=", "Variable(PMX)"), c(CMP, "MouseY()", "!=", "Variable(PMY)")]),
                           c(CMP, "MouseX()", ">=", str(x0)), c(CMP, "MouseX()", "<", str(x0 + 156)), c(CMP, "MouseY()", ">=", str(y0)), c(CMP, "MouseY()", "<", str(y0 + 156))],
                          [a("ModVarScene", "HV", "=", str(i))]))
    # fuera de la rejilla, fuera del paso, o al navegar con teclado/mando: se quita la vista previa
    teclas = [c("KeyReleased", "", k) for k in ("Left", "Right", "Up", "Down", "a", "d", "w", "s", "Return")]
    nuevos.append(std([c("VarScene", "HV", ">=", "0"), orr([c(CMP, "MouseX()", "<", "1105"), c(CMP, "MouseX()", ">=", "1774"), c(CMP, "MouseY()", "<", "212"), c(CMP, "MouseY()", ">=", "544")] + teclas)],
                      [a("ModVarScene", "HV", "=", "-1")]))
    nuevos.append(std([c("VarSceneTxt", "Paso", "!=", '"equipo"')], [a("ModVarScene", "HV", "=", "-1")]))
    ME[pm:pm] = nuevos

# 2 · la vista previa reemplaza al personaje enfocado (despues de calcular KF / NMF y antes de dibujar)
if not hay("PREV"):
    ik = max(i for i, e in enumerate(ME) if e["type"].endswith("Standard") and any(x["type"]["value"] == "ModVarSceneTxt" and x["parameters"][:1] == ["KF"] for x in e["actions"]) and any(cc["parameters"][:3] == ["Foco", "=", "4"] for cc in e["conditions"]))
    nuevos = [marca("PREV")]
    for i, (k, n) in enumerate(PJ):
        nuevos.append(std([EQ, c("VarScene", "HV", "=", str(i))], [a("ModVarSceneTxt", "KF", "=", '"%s"' % k), a("ModVarSceneTxt", "NMF", "=", '"%s"' % n)]))
    ME[ik + 1:ik + 1] = nuevos

# 3 · el subtitulo conserva su texto original por slot (P1 / BOT 2 / P2... · eligiendo / LISTO): se quita el texto "VISTA PREVIA" de la primera version
for i in range(len(ME) - 1, -1, -1):
    if ME[i].get("comment") == MK + "-SUB":
        del ME[i:i + 2]

# 4 · resalte ligero del retrato (motor de hover de fase33)
f33 = os.path.join(AQUI, "fase33_iconos_y_hover.py")
s = open(f33, encoding="utf-8").read()
if '"EqRet"' not in s:
    s = s.replace('"DifBtn", "EqCelda"]', '"DifBtn", "EqCelda", "EqRet"]'); open(f33, "w", encoding="utf-8").write(s)
json.dump(d, open(PRY, "w"), ensure_ascii=False, indent=2)
print("OK fase 36")
