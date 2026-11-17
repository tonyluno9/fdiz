"""Fase 39 · Navegacion con mando en todo el juego. Idempotente.
1) El stick izquierdo cuenta como cruceta (Arriba/Abajo/Izquierda/Derecha) en la extension Gamepads: todos los menus que ya usaban la cruceta responden tambien al joystick.
2) Seleccion de personajes: Start del mando confirma al jugador de turno y, si ya no falta nadie, pasa a la pantalla de dificultad.
3) Cinematica: Select (BACK) del mando tambien la omite.
4) Resultados: cruceta/joystick eligen Reintentar o Menu (A/Start confirman la opcion resaltada).
5) Pausa: el mando 4 tambien pausa y navega (antes solo 1-3)."""
import json, os, shutil, sys, copy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gd_util import c, a
AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
GP = os.path.join(AQUI, "Gamepads.json")
bak = os.path.join(AQUI, "..", "respaldos", "antes_de_fase39_20261117.json")
if not os.path.exists(bak): shutil.copy(PRY, bak)
MK = "FDIZ-FASE39"
STD = "BuiltinCommonInstructions::Standard"
OR = "BuiltinCommonInstructions::Or"
CMP = "BuiltinCommonInstructions::CompareNumbers"

# ---------------------------------------------------------------- 1 · stick como cruceta
VIEJA = "buttonState.isPressed = gamepad.buttons[buttonId].pressed;"
NUEVA = ("buttonState.isPressed = gamepad.buttons[buttonId].pressed || (buttonId >= 12 && buttonId <= 15 && buttonId === ((ax, ay) => Math.abs(ax) >= Math.abs(ay) ? (ax > 0.6 ? 15 : (ax < -0.6 ? 14 : -1)) : (ay > 0.6 ? 13 : (ay < -0.6 ? 12 : -1)))(gamepad.axes[0] || 0, gamepad.axes[1] || 0)); /*FDIZ-F39*/")
def parchea_ext(ext):
    n = 0
    for f in ext["eventsFunctions"]:
        if f["name"] != "onFirstSceneLoaded": continue
        for e in f["events"]:
            if not e["type"].endswith("JsCode"): continue
            ic = e["inlineCode"]
            lines = ic if isinstance(ic, list) else ic.split("\n")
            for i, l in enumerate(lines):
                if "FDIZ-F39" in l: n = -99
                elif VIEJA in l and n >= 0:
                    lines[i] = l.replace(VIEJA, NUEVA); n += 1
            e["inlineCode"] = lines if isinstance(ic, list) else "\n".join(lines)
    return n
gp = json.load(open(GP, encoding="utf-8"))
parchea_ext(gp); json.dump(gp, open(GP, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

d = json.load(open(PRY))
for ext in d["eventsFunctionsExtensions"]:
    if ext["name"] == "Gamepads": parchea_ext(ext)

def walk(lst):
    for e in lst:
        yield e
        yield from walk(e.get("events", []))
def marca(k):
    return {"type": "BuiltinCommonInstructions::Comment", "color": {"b": 109, "g": 230, "r": 255, "textB": 0, "textG": 0, "textR": 0}, "comment": MK + "-" + k, "comment2": ""}
def hay(lst, k): return any(e.get("comment") == MK + "-" + k for e in lst)
def std(conds, acts): return {"type": STD, "conditions": conds, "actions": acts, "events": []}
def btn(n, b): return c("Gamepads::C_Button_released", "", str(n), '"%s"' % b, "")
def tiene(orc, b):
    return any(s["type"]["value"] == "Gamepads::C_Button_released" and s["parameters"][2] == '"%s"' % b for s in orc["subInstructions"])

# ---------------------------------------------------------------- 2 · Start en la seleccion de personajes
ME = next(l for l in d["layouts"] if l["name"] == "Menu")["events"]
if not hay(ME, "START-EQ"):
    nuevos = [marca("START-EQ")]
    for k in (1, 2, 3, 4):
        otros = " + ".join("sign(Variable(S%dCtl) + 1) * (1 - Variable(S%dOk))" % (j, j) for j in (1, 2, 3, 4) if j != k)
        for n in (1, 2, 3, 4):
            base = [c("VarSceneTxt", "Paso", "=", '"equipo"'), c("CompareTimer", "", '"paso"', ">=", "0.3"), c("VarScene", "S%dCtl" % k, "=", str(n)),
                    btn(n, "START"), c("VarScene", "Turno", "=", str(k)), c("VarScene", "S%dOk" % k, "=", "0")]
            nuevos.append(std(base + [c(CMP, otros, "=", "0")], [a("ModVarScene", "S%dOk" % k, "=", "1"), a("ModVarSceneTxt", "Paso", "=", '"dificultad"'),
                                                                   a("ResetTimer", "", '"paso"'), a("ModVarScene", "Sel", "=", "1")]))
            nuevos.append(std(base + [c(CMP, otros, ">", "0")], [a("ModVarScene", "S%dOk" % k, "=", "1")]))
    ME.extend(nuevos)

# ---------------------------------------------------------------- 3 · Select omite la cinematica; 5 · mando 4 en la pausa
JE = next(l for l in d["layouts"] if l["name"] == "Juego")["events"]
def pad_extra(orc, pads_origen=(1, 2, 3), n=4):
    """para cada boton con pad 1..3 en este Or, agrega el del pad n si falta"""
    ya = {(s["parameters"][1], s["parameters"][2]) for s in orc["subInstructions"] if s["type"]["value"] == "Gamepads::C_Button_released"}
    for s in list(orc["subInstructions"]):
        if s["type"]["value"] == "Gamepads::C_Button_released" and s["parameters"][1] == "1" and ("%d" % n, s["parameters"][2]) not in ya:
            t = copy.deepcopy(s); t["parameters"][1] = str(n); orc["subInstructions"].append(t); ya.add((str(n), s["parameters"][2]))
for e in walk(JE):
    if not e["type"].endswith("Standard"): continue
    for cc in e.get("conditions", []):
        if cc["type"]["value"] != OR: continue
        pads = [s for s in cc["subInstructions"] if s["type"]["value"] == "Gamepads::C_Button_released"]
        btns = {s["parameters"][2].upper() for s in pads}
        if '"START"' in btns and any(x["parameters"][:1] == ["Estado"] for x in e["conditions"]) and any(x["parameters"][2] == '"intro"' for x in e["conditions"] if x["parameters"][:1] == ["Estado"]):
            if not tiene(cc, "BACK"):                                                     # cinematica: Select
                for n in (1, 2, 3, 4): cc["subInstructions"].append(btn(n, "BACK"))
        elif btns & {'"START"', '"UP"', '"DOWN"', '"A"'} and "Pausa" in json.dumps(e["conditions"]):
            pad_extra(cc)                                                                 # pausa: mando 4

# ---------------------------------------------------------------- 4 · Resultados: elegir con cruceta / joystick
R = next(l for l in d["layouts"] if l["name"] == "Resultados")
RE = R["events"]
if not any(v["name"] == "Sel" for v in R["variables"]):
    R["variables"].append({"name": "Sel", "type": "number", "value": 0})
if not hay(RE, "NAV"):
    a_ev = next(e for e in RE if e["type"].endswith("Standard") and any(cc["type"]["value"] == OR and any(s["parameters"] == ["", "Return"] for s in cc["subInstructions"] if s["type"]["value"] == "KeyReleased") for cc in e["conditions"]))
    b_ev = next(e for e in RE if e["type"].endswith("Standard") and any(cc["type"]["value"] == OR and any(s["parameters"] == ["", "Escape"] for s in cc["subInstructions"] if s["type"]["value"] == "KeyReleased") for cc in e["conditions"]))
    or_a = next(cc for cc in a_ev["conditions"] if cc["type"]["value"] == OR)
    clon = copy.deepcopy(b_ev)
    clon["conditions"] = [cc for cc in clon["conditions"] if cc["type"]["value"] != OR] + [copy.deepcopy(or_a), c("VarScene", "Sel", "=", "1")]
    a_ev["conditions"].append(c("VarScene", "Sel", "=", "0"))
    nav = [c("KeyReleased", "", "Up"), c("KeyReleased", "", "Down")] + [btn(n, b) for n in (1, 2, 3, 4) for b in ("Up", "Down", "Left", "Right")]
    nuevos = [marca("NAV"), clon,
              std([c("CompareTimer", "", '"t"', ">=", "0.3"), {"type": {"inverted": False, "value": OR}, "parameters": [], "subInstructions": nav}], [a("ModVarScene", "Sel", "=", "1 - Variable(Sel)")]),
              std([c("VarScene", "Sel", "=", "0")], [a("Opacity", "BtnRei", "=", "255")]),
              std([c("VarScene", "Sel", "=", "1")], [a("Opacity", "BtnMenuR", "=", "255")])]
    RE.extend(nuevos)
json.dump(d, open(PRY, "w"), ensure_ascii=False, indent=2)
print("OK fase 39")
