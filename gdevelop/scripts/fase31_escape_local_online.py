"""Fase 31 · Escape también pasa por la pantalla Local / En línea (modos -> Escape o Jefe -> Local / En línea). Idempotente.
Va después de fase30 (la cadena es fase25 -> ... -> fase31)."""
import json, copy, os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gd_util import c, a

AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
bak = os.path.join(AQUI, "..", "respaldos", "antes_de_fase31_20261117.json")
if not os.path.exists(bak):
    shutil.copy(PRY, bak)
d = json.load(open(PRY))
M = next(l for l in d["layouts"] if l["name"] == "Menu")
ME = M["events"]
MK = "FDIZ-FASE31"
STD = "BuiltinCommonInstructions::Standard"

def std(conds, acts, sub=()):
    return {"type": STD, "conditions": conds, "actions": acts, "events": list(sub)}
def marca(clave):
    return {"type": "BuiltinCommonInstructions::Comment", "color": {"b": 109, "g": 230, "r": 255, "textB": 0, "textG": 0, "textR": 0}, "comment": MK + "-" + clave, "comment2": ""}
def hay(lst, clave): return any(x.get("comment") == MK + "-" + clave for x in lst)
def nuevo(lst, idx, e, clave):
    if hay(lst, clave): return False
    if idx is None or idx > len(lst): idx = len(lst)
    lst.insert(idx, marca(clave)); lst.insert(idx + 1, e); return True
def cond_has(e, tipo, params):
    return any(x["type"]["value"] == tipo and x["parameters"][:len(params)] == params for x in e.get("conditions", []))
def act_has(e, tipo, params):
    return any(x["type"]["value"] == tipo and x["parameters"][:len(params)] == params for x in e.get("actions", []))
def add_act(e, aa):
    if aa not in e["actions"]: e["actions"].append(aa)
def add_cond(e, cc):
    if cc not in e["conditions"]: e["conditions"].append(cc)

for v in ("OnlineEsc",):
    if not any(x["name"] == v for x in d["variables"]):
        d["variables"].append({"name": v, "type": "number", "value": 0})
if not any(v["name"] == "JT" for v in M["variables"]):
    M["variables"].append({"name": "JT", "type": "number", "value": 0})   # 0 = Escape, 1 = Jefe (pantalla Local / En línea)

PM = c("VarSceneTxt", "Paso", "=", '"modo"')
PJT = c("VarSceneTxt", "Paso", "=", '"jefetipo"')
JT0, JT1 = c("VarScene", "JT", "=", "0"), c("VarScene", "JT", "=", "1")
# ---------------------------------------------------------------- 1 · entrar: Escape y Jefe van a la pantalla Local / En línea
for e in ME:
    if e["type"].endswith("Standard") and cond_has(e, "VarSceneTxt", ["Paso", "=", '"modo"']) and cond_has(e, "CompareTimer", ["", '"paso"']) and act_has(e, "ModVarSceneTxt", ["Paso", "=", '"unirse"']):
        for sub in e["events"]:
            if cond_has(sub, "VarScene", ["Sel", "=", "0"]):
                for aa in (a("ModVarSceneTxt", "Paso", "=", '"jefetipo"'), a("ModVarScene", "Sel", "=", "0"), a("ModVarScene", "JT", "=", "0"),
                           a("ModVarGlobal", "OnlineJefe", "=", "0"), a("ModVarGlobal", "OnlineEsc", "=", "0")):
                    add_act(sub, aa)
            if cond_has(sub, "VarScene", ["Sel", "=", "1"]):
                add_act(sub, a("ModVarScene", "JT", "=", "1")); add_act(sub, a("ModVarGlobal", "OnlineEsc", "=", "0"))
# atajo oculto Num3 / tarjeta 3 (En línea directo): fuera
for e in list(ME):
    if e["type"].endswith("Standard") and cond_has(e, "VarSceneTxt", ["Paso", "=", '"modo"']) and act_has(e, "Scene", ["", '"Online"']):
        ME.remove(e)

# ---------------------------------------------------------------- 2 · aceptar: Local / En línea según el modo (JT)
LOCAL_ESC = [a("ModVarSceneTxt", "Paso", "=", '"unirse"'), a("ResetTimer", "", '"paso"'), a("ModVarGlobalTxt", "Modo", "=", '"escape"'),
             a("ModVarScene", "S1Ctl", "=", "0"), a("ModVarGlobal", "OnlineJefe", "=", "0"), a("ModVarGlobal", "OnlineEsc", "=", "0")]
ONLINE_ESC = [a("ModVarGlobalTxt", "Modo", "=", '"escape"'), a("ModVarGlobal", "OnlineJefe", "=", "0"), a("ModVarGlobal", "OnlineEsc", "=", "1"), a("Scene", "", '"Online"', "")]
if not hay(ME, "ACEPTAR"):
    copias = []
    for e in ME:
        if not e["type"].endswith("Standard") or not cond_has(e, "VarSceneTxt", ["Paso", "=", '"jefetipo"']): continue
        es_local = act_has(e, "ModVarSceneTxt", ["Paso", "=", '"equipo"']) and act_has(e, "ModVarGlobalTxt", ["Modo", "=", '"jefe"'])
        es_online = act_has(e, "Scene", ["", '"Online"']) and act_has(e, "ModVarGlobalTxt", ["Modo", "=", '"jefe"'])
        if not (es_local or es_online): continue
        add_cond(e, JT1)
        if es_online: add_act(e, a("ModVarGlobal", "OnlineEsc", "=", "0"))
        if es_local: add_act(e, a("ModVarGlobal", "OnlineEsc", "=", "0"))
        cp = copy.deepcopy(e)
        cp["conditions"] = [JT0 if x == JT1 else x for x in cp["conditions"]]
        cp["actions"] = copy.deepcopy(LOCAL_ESC if es_local else ONLINE_ESC)
        copias.append(cp)
    ME.append(marca("ACEPTAR")); ME.extend(copias)

# ---------------------------------------------------------------- 3 · volver
# Esc en la pantalla Local/En línea: de regreso a la tarjeta del modo elegido
for e in ME:
    if e["type"].endswith("Standard") and cond_has(e, "VarSceneTxt", ["Paso", "=", '"jefetipo"']) and any(y["type"]["value"] == "ModVarSceneTxt" and y["parameters"][-1] == '"modo"' for y in e["actions"]):
        for x in e["actions"]:
            if x["type"]["value"] == "ModVarScene" and x["parameters"][:2] == ["Sel", "="]: x["parameters"][2] = "Variable(JT)"
# Esc en "unirse" (Escape local) -> Local / En línea
for e in ME:
    if e["type"].endswith("Standard") and cond_has(e, "VarSceneTxt", ["Paso", "=", '"unirse"']) and cond_has(e, "CompareTimer", ["", '"paso"']) \
       and any(y["type"]["value"] == "ModVarSceneTxt" and y["parameters"][-1] == '"modo"' for y in e["actions"]):
        for x in e["actions"]:
            if x["type"]["value"] == "ModVarSceneTxt" and x["parameters"][-1] == '"modo"': x["parameters"][-1] = '"jefetipo"'
        add_act(e, a("ModVarScene", "Sel", "=", "0")); add_act(e, a("ModVarScene", "JT", "=", "0"))
# regreso desde la sala en línea
for e in ME:
    if e["type"].endswith("Standard") and cond_has(e, "DepartScene", []) and cond_has(e, "VarGlobal", ["OnlineJefe", ">=", "1"]):
        add_act(e, a("ModVarScene", "JT", "=", "1"))
nuevo(ME, len(ME), std([c("DepartScene", ""), c("VarGlobal", "OnlineEsc", ">=", "1")],
                       [a("ModVarSceneTxt", "Paso", "=", '"jefetipo"'), a("ModVarScene", "Sel", "=", "1"), a("ModVarScene", "JT", "=", "0"),
                        a("ModVarGlobalTxt", "Modo", "=", '"escape"'), a("ModVarScene", "S1Ctl", "=", "0"), a("ModVarGlobal", "OnlineEsc", "=", "0"), a("ResetTimer", "", '"paso"')]), "VOLVER-ONLINE-ESC")

# ---------------------------------------------------------------- 4 · textos de la pantalla Local / En línea por modo
if not hay(ME, "TXT"):
    copias = []
    for e in ME:
        if not e["type"].endswith("Standard") or not cond_has(e, "VarSceneTxt", ["Paso", "=", '"jefetipo"']): continue
        if cond_has(e, "VarScene", ["JT"]): continue
        cambios = {}
        for x in e["actions"]:
            if x["type"]["value"] == "TextObject::String" and x["parameters"][:1] == ["TxtMenu"]: cambios[id(x)] = '"ESCAPE"'
            if x["type"]["value"] == "TextObject::String" and x["parameters"][:1] == ["TxtCapB"]:
                cambios[id(x)] = '"1 a 4 jugadores + bots"' if "bots" in x["parameters"][-1] else '"Hasta 4 jugadores · sala con código"'
        if not cambios: continue
        add_cond(e, JT1)
        cp = copy.deepcopy(e)
        cp["conditions"] = [JT0 if x == JT1 else x for x in cp["conditions"]]
        for x_orig, x_cp in zip(e["actions"], cp["actions"]):
            if id(x_orig) in cambios: x_cp["parameters"][-1] = cambios[id(x_orig)]
        copias.append(cp)
    ME.append(marca("TXT")); ME.extend(copias)

json.dump(d, open(PRY, "w"), ensure_ascii=False, indent=2)
print("OK fase 31")
