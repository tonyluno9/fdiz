"""Fase 24 · Multijugador local: iconos en los huecos de jugadores, mandos completos, Jefe con sobrevivientes con control.
Idempotente. Uso: python3 fase24_local.py"""
import json, copy, os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gd_util import res_imagen, animacion, objeto_sprite, instancia, c, a
from PIL import Image, ImageDraw

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.join(AQUI, "..", "FDI-Z")
PRY = os.path.join(RAIZ, "FDI-Z.json")
bak = os.path.join(AQUI, "..", "respaldos", "antes_de_fase24_20261113.json")
if not os.path.exists(bak):
    shutil.copy(PRY, bak)

# ---------- iconos (pixel art 24x18, escala x6 -> 144x108) ----------
S = 6
OSC, GRIS, CLARO, BLANCO, VERDE, ROJO, AMA, AZUL = (20, 24, 50), (90, 98, 140), (170, 180, 215), (245, 245, 250), (110, 230, 130), (240, 90, 90), (255, 215, 80), (90, 170, 255)

def lienzo():
    return Image.new("RGBA", (24, 18), (0, 0, 0, 0))

def rect(dr, x0, y0, x1, y1, col):
    dr.rectangle([x0, y0, x1, y1], fill=col)

def guarda(img, nombre):
    img.resize((24 * S, 18 * S), Image.NEAREST).save(os.path.join(RAIZ, "assets", "interfaz", nombre))

def mando(col_cuerpo, col_det, plus=False):
    im = lienzo(); dr = ImageDraw.Draw(im)
    rect(dr, 3, 5, 20, 12, OSC)
    rect(dr, 4, 4, 19, 4, OSC); rect(dr, 4, 13, 8, 15, OSC); rect(dr, 15, 13, 19, 15, OSC)
    rect(dr, 4, 5, 19, 12, col_cuerpo); rect(dr, 5, 13, 7, 14, col_cuerpo); rect(dr, 16, 13, 18, 14, col_cuerpo)
    rect(dr, 6, 7, 8, 7, col_det); rect(dr, 7, 6, 7, 8, col_det)            # cruceta
    rect(dr, 15, 6, 16, 7, ROJO if not plus else col_det); rect(dr, 17, 8, 18, 9, VERDE if not plus else col_det)  # botones
    rect(dr, 10, 9, 11, 10, col_det); rect(dr, 13, 9, 14, 10, col_det)      # palancas
    if plus:
        rect(dr, 19, 0, 21, 4, AMA); rect(dr, 18, 2, 22, 2, AMA)
    return im

def teclado():
    im = lienzo(); dr = ImageDraw.Draw(im)
    rect(dr, 1, 6, 15, 15, OSC); rect(dr, 2, 7, 14, 14, GRIS)
    for fy in (8, 10, 12):
        for fx in (3, 5, 7, 9, 11, 13 - 1):
            rect(dr, fx, fy, fx, fy, CLARO)
    rect(dr, 4, 14 - 0, 12, 14, CLARO)
    rect(dr, 17, 4, 22, 14, OSC); rect(dr, 18, 5, 21, 13, BLANCO)
    rect(dr, 19, 5, 19, 8, GRIS); rect(dr, 18, 8, 21, 8, GRIS)
    rect(dr, 18, 5, 18, 7, AZUL)
    return im

def robot():
    im = lienzo(); dr = ImageDraw.Draw(im)
    rect(dr, 11, 1, 12, 2, AMA); rect(dr, 11, 3, 12, 4, OSC)
    rect(dr, 5, 5, 18, 14, OSC); rect(dr, 6, 6, 17, 13, CLARO)
    rect(dr, 8, 8, 10, 10, OSC); rect(dr, 13, 8, 15, 10, OSC); rect(dr, 9, 9, 9, 9, AMA); rect(dr, 14, 9, 14, 9, AMA)
    rect(dr, 9, 12, 14, 12, GRIS); rect(dr, 3, 8, 4, 11, OSC); rect(dr, 19, 8, 20, 11, OSC)
    return im

guarda(teclado(), "slot_ico_teclado.png")
guarda(mando(CLARO, GRIS), "slot_ico_mando.png")
guarda(mando(GRIS, OSC, plus=True), "slot_ico_libre.png")
guarda(robot(), "slot_ico_bot.png")

d = json.load(open(PRY))
R = d["resources"]["resources"]
nombres = {r["name"] for r in R}
for k in ("teclado", "mando", "libre", "bot"):
    if "slot_ico_" + k not in nombres:
        R.append(res_imagen("slot_ico_" + k, "assets/interfaz/slot_ico_%s.png" % k))

# ---------- MENÚ: iconos en los 4 huecos ----------
menu = next(l for l in d["layouts"] if l["name"] == "Menu")
if not any(o["name"] == "SlotIco" for o in menu["objects"]):
    ob = objeto_sprite("SlotIco", [animacion(k, ["slot_ico_" + k], 1, False, (0, 0)) for k in ("teclado", "mando", "libre", "bot")],
                       variables=[{"name": "Slot", "type": "number", "value": 0}])
    menu["objects"].append(ob)
menu["instances"] = [i for i in menu["instances"] if i["name"] != "SlotIco"]
for n, x in enumerate((300, 740, 1180, 1620), 1):
    menu["instances"].append(instancia("SlotIco", x - 105, 575, "", 6, 210, 158, variables=[{"name": "Slot", "type": "number", "value": n}]))

MARCA = "FDIZ-FASE24-ICONOS"
if not any(e.get("comment", "").startswith(MARCA) for e in menu["events"]):
    def com(t):
        return {"type": "BuiltinCommonInstructions::Comment", "color": {"b": 109, "g": 230, "r": 255, "textB": 0, "textG": 0, "textR": 0}, "comment": t}
    def est(conds, acts):
        return {"type": "BuiltinCommonInstructions::Standard", "conditions": conds, "actions": acts, "events": []}
    ev = [com(MARCA + " · En el paso Únanse cada hueco muestra un icono (teclado y ratón / mando / libre); fuera de ese paso se oculta.")]
    for n in range(1, 5):
        v = "S%dCtl" % n
        un = c("VarSceneTxt", "Paso", "=", '"unirse"')
        sl = c("VarObjet", "SlotIco", "Slot", "=", str(n))
        ev.append(est([un, sl, c("VarScene", v, "=", "0")], [a("SetAnimationName", "SlotIco", '"teclado"'), a("Opacity", "SlotIco", "=", "255")]))
        ev.append(est([un, sl, c("VarScene", v, ">", "0")], [a("SetAnimationName", "SlotIco", '"mando"'), a("Opacity", "SlotIco", "=", "255")]))
        ev.append(est([un, sl, c("VarScene", v, "=", "-1")], [a("SetAnimationName", "SlotIco", '"libre"'), a("Opacity", "SlotIco", "=", "255")]))
        ev.append(est([c("VarSceneTxt", "Paso", "!=", '"unirse"'), sl], [a("Opacity", "SlotIco", "=", "0")]))
        ev.append(est([un, c("VarObjet", "TxtCtl", "Slot", "=", str(n))], [a("TextObject::String", "TxtCtl", "=", '""')]))
    menu["events"].extend(ev)

MARCA2 = "FDIZ-FASE24-TXTJEFE"
ix = next((i for i, e in enumerate(menu["events"]) if e.get("comment", "").startswith(MARCA2)), None)
if ix is not None:
    del menu["events"][ix:ix + 2]
if True:
    menu["events"].append({"type": "BuiltinCommonInstructions::Comment", "color": {"b": 109, "g": 230, "r": 255, "textB": 0, "textG": 0, "textR": 0}, "comment": MARCA2 + " · texto del paso Únanse en modo Jefe."})
    menu["events"].append({"type": "BuiltinCommonInstructions::Standard", "conditions": [c("VarSceneTxt", "Paso", "=", '"unirse"'), c("VarGlobalTxt", "Modo", "=", '"jefe"')],
        "actions": [a("TextObject::String", "TxtSubM", "=", '"Tú eres el Jefe (teclado y ratón). Los 4 sobrevivientes serán bots: para sobrevivientes humanos hace falta jugar en línea desde otras máquinas."'),
                    a("TextObject::String", "TxtSlots", "=", '""')], "events": []})

# máximo 4 por máquina; en modo Jefe local no entra ningún humano (se vería la pantalla del Jefe): todos bots
cuenta = "max(0, sign(Variable(S1Ctl))) + max(0, sign(Variable(S2Ctl))) + max(0, sign(Variable(S3Ctl))) + max(0, sign(Variable(S4Ctl)))"
limite = "4 - 4 * sign(StrFind(GlobalVariableString(Modo), \"jefe\"))"
for e in menu["events"]:
    if not e["type"].endswith("Standard"):
        continue
    cs = e.get("conditions", [])
    if any(x["type"]["value"] == "VarSceneTxt" and x["parameters"] == ["Paso", "=", '"unirse"'] for x in cs) and \
       any(x["type"]["value"] == "Gamepads::C_Button_released" and x["parameters"][2] == '"A"' for x in cs):
        cs[:] = [x for x in cs if not (x["type"]["value"] == "BuiltinCommonInstructions::CompareNumbers" and x["parameters"][0] == cuenta)]
        cond = c("BuiltinCommonInstructions::CompareNumbers", cuenta, "<", limite)
        if cond not in cs:
            cs.append(cond)

# ---------- JUEGO ----------
jg = next(l for l in d["layouts"] if l["name"] == "Juego")
ev = jg["events"]

def grupo(n):
    return next(e for e in ev if e.get("name") == n)

# Jefe: los sobrevivientes con control siguen siendo humanos (ya no se fuerza Control -1)
g1 = grupo("Configuración y dificultad")
g1["events"] = [e for e in g1["events"] if not (any(x["type"]["value"] == "VarGlobalTxt" and x["parameters"][:3] == ["Modo", "=", '"jefe"'] for x in e.get("conditions", []))
                                               and any(x["type"]["value"] == "ModVarObjet" and x["parameters"][1:4] == ["Control", "=", "-1"] for x in e.get("actions", [])))]

# Pausa con mando: Start pausa, cruceta mueve, A acepta
pausa = grupo("Menú de pausa")
def mas_or(e, extra):
    for x in e.get("conditions", []):
        if x["type"]["value"] == "BuiltinCommonInstructions::Or":
            for ex in extra:
                if ex not in x["subInstructions"]:
                    x["subInstructions"].append(ex)
            return True
    return False
for e in pausa["events"]:
    acts = e.get("actions", [])
    if any(x["type"]["value"] == "ModVarScene" and x["parameters"][:3] == ["PausaCambio", "=", "1"] for x in acts):
        mas_or(e, [c("Gamepads::C_Button_released", "", str(n), '"Start"', "") for n in range(1, 5)])
    elif any(x["type"]["value"] == "ModVarScene" and x["parameters"][0] == "PausaSel" and len(x["parameters"]) > 2 and "+ 2" in x["parameters"][2] for x in acts):
        mas_or(e, [c("Gamepads::C_Button_released", "", str(n), '"Up"', "") for n in range(1, 5)])
    elif any(x["type"]["value"] == "ModVarScene" and x["parameters"][0] == "PausaSel" and len(x["parameters"]) > 2 and "+ 1" in x["parameters"][2] for x in acts):
        mas_or(e, [c("Gamepads::C_Button_released", "", str(n), '"Down"', "") for n in range(1, 5)])
    elif any(x["type"]["value"] == "ModVarScene" and x["parameters"][:3] == ["PausaGo", "=", "1"] for x in acts):
        mas_or(e, [c("Gamepads::C_Button_released", "", str(n), '"A"', "") for n in range(1, 5)])

# Apuntar con la palanca derecha (si se mueve, manda sobre la izquierda)
ent = grupo("Entrada (teclado y controles)")
def patrulla(evs):
    i = 0
    while i < len(evs):
        e = evs[i]
        if e["type"].endswith("Standard") and any(x["type"]["value"] == "ModVarObjet" and x["parameters"][1] == "AimX" and 'StickForceX(' in x["parameters"][3] and '"Left"' in x["parameters"][3] for x in e.get("actions", [])):
            copia = copy.deepcopy(e)
            txt = json.dumps(copia).replace('\\"Left\\"', '\\"Right\\"')
            copia = json.loads(txt)
            if not any(json.dumps(o) == json.dumps(copia) for o in evs):
                evs.insert(i + 1, copia); i += 1
        else:
            patrulla(e.get("events", []))
        i += 1
patrulla(ent["events"])

json.dump(d, open(PRY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("OK fase 24")
