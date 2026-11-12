"""Fase 13 de FDI-Z: HUD con las piezas de interfaz (paneles de jugador, retratos, iconos, banner, infestación y dinero).
Correr DESPUÉS de fase12_mejoras.py y de preparar_interfaz.py (con GDevelop cerrado):
    python fase13_interfaz.py <FDI-Z.json>
Reemplaza los textos del HUD de la escena Juego (TxtPanel, TxtInfest). TxtObjetivo se coloca sobre el banner."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gd_util import *

ruta = sys.argv[1]
p = json.load(open(ruta, encoding="utf-8"))
esc = next(l for l in p["layouts"] if l["name"] == "Juego")
# resolución fija 1920x1080 (letterbox): el HUD está puesto en pixeles de 1920 de ancho y se cortaba en ventanas más angostas
p["properties"]["adaptGameResolutionAtRuntime"] = False
p["properties"]["sizeOnStartupMode"] = ""
UI = "assets/interfaz/"
recursos = {r["name"]: r for r in p["resources"]["resources"]}
def img(nombre, archivo):
    recursos[nombre] = res_imagen(nombre, archivo); return nombre

# ---------------- helpers ----------------
def cmp(e1, op, e2): return c("BuiltinCommonInstructions::CompareNumbers", e1, op, e2)
def vtxt(o, v, val, inv=False): return c("VarObjetTxt", o, v, "=", f"\"{val}\"", invertida=inv)
def vnum(o, v, op, val): return c("VarObjet", o, v, op, str(val))
def cvar(v, op, val): return c("VarScene", v, op, str(val))
def cvt(v, val, op="="): return c("VarSceneTxt", v, op, val)
def texto(o, expr): return a("TextObject::String", o, "=", expr)
def anim(o, n): return a("SetAnimationName", o, n if n.startswith("Sup.") else f"\"{n}\"")
def obj_texto(nombre, tam, color="255;255;255"):
    return {"assetStoreId": "", "name": nombre, "type": "TextObject::Text", "variables": [var("Jugador", 0), var("Slot", 0)], "effects": [],
            "behaviors": [], "content": {"bold": True, "isOutlineEnabled": True, "isShadowEnabled": False, "italic": False,
            "outlineColor": "0;0;0", "outlineThickness": 4, "shadowAngle": 90, "shadowBlurRadius": 2, "shadowColor": "0;0;0",
            "shadowDistance": 4, "shadowOpacity": 127, "smoothed": False, "underlined": False, "text": "", "font": "",
            "textAlignment": "left", "verticalTextAlignment": "top", "characterSize": tam, "lineHeight": 0, "color": color}}
def spr(nombre, anims):
    return objeto_sprite(nombre, [animacion(n, [img(f"ui_{f}", UI + f)], 1, False, (0, 0)) for n, f in anims],
                         [var("Jugador", 0), var("Slot", 0), var("Idx", 0)])

PJ = ["tony", "miranda", "cesar", "alan", "castillo", "alessandro", "gabo", "carlos"]
RETR = PJ + ["tonyfuerte", "silueta"]
ICON = []
for pj in PJ:
    for t, f in (("q", "q"), ("e", "e"), ("p", "pasiva")):
        ICON.append((f"{pj}_{t}", f"hud/ico128_{pj}_{f}.png"))
for t, f in (("q", "q"), ("e", "e"), ("p", "pasiva")):   # Tony en modo gym usa los mismos iconos
    ICON.append((f"tonyfuerte_{t}", f"hud/ico128_tony_{f}.png"))
ARMAS = [("puños", "punos"), ("escoba", "escoba"), ("regla", "regla"), ("silla", "silla"), ("bate", "bate"),
         ("extintor", "extintor"), ("pistola", "pistola"), ("escopeta", "escopeta")]
ICON += [(n, f"hud/ico128_arma_{f}.png") for n, f in ARMAS]

objs = [
    spr("HudPanel", [(str(k), f"hud_panel_p{k}_{col}.png") for k, col in enumerate(["amarillo", "azul", "verde", "rosa"], 1)]),
    spr("HudRetrato", [(n, f"retrato_{n}.png") for n in RETR]),
    spr("HudVida", [("vida", "hud/vida.png")]),
    spr("HudIcono", ICON),
    spr("HudInv", [("comida", "hud/ico128_comida_guardada.png"), ("lanzable", "hud/ico128_lanzable.png"), ("mordido", "hud/ico128_mordido.png")]),
    spr("HudBanner", [("b", "hud_banner_objetivo.png")]),
    spr("HudInfPanel", [("b", "hud_panel_infestacion.png")]),
    spr("HudDinPanel", [("b", "hud_panel_dinero.png")]),
    spr("HudSeg", [("on", "hud/seg_on.png")]),
    obj_texto("TxtHudVida", 18), obj_texto("TxtCd", 22, "255;255;255"), obj_texto("TxtHudDinero", 30, "255;225;90"), obj_texto("TxtHudTiempo", 22, "220;235;255"),
]
FIJOS = ["HudPanel", "HudRetrato", "HudVida", "HudIcono", "TxtHudVida", "TxtCd", "HudBanner", "HudInfPanel", "HudDinPanel", "TxtHudDinero", "TxtHudTiempo"]
DIN = ["HudSeg", "HudInv"]
NOMBRES = {o["name"] for o in objs}
esc["objects"] = [o for o in esc["objects"] if o["name"] not in NOMBRES] + objs
esc["objectsGroups"] = [g for g in esc["objectsGroups"] if g["name"] not in ("HudFijo", "HudDin")] + [
    {"name": "HudFijo", "objects": [{"name": n} for n in FIJOS]}, {"name": "HudDin", "objects": [{"name": n} for n in DIN]}]

# ---------------- instancias ----------------
esc["instances"] = [i for i in esc["instances"] if i["name"] not in NOMBRES]
def inst(n, x, y, z, w=None, h=None, **vs):
    esc["instances"].append(instancia(n, x, y, "HUD", z, w, h, [var(k, v) for k, v in vs.items()]))
S = 0.8
PW, PH = round(523 * S), round(205 * S)
ORIG = {1: (20, 16), 2: (1920 - 20 - PW, 16), 3: (20, 1080 - 16 - PH), 4: (1920 - 20 - PW, 1080 - 16 - PH)}
CEN = {1: (246, 131), 2: (347, 131), 3: (447, 131)}   # centro de cada ranura de habilidad en el panel (px originales)
RET = (99, 99)
for k, (ox, oy) in ORIG.items():
    inst("HudPanel", ox, oy, 1, PW, PH, Jugador=k)
    inst("HudVida", ox + 154, oy + 30, 2, 238, 24, Jugador=k)
    inst("HudRetrato", ox + round(RET[0] * S) - 52, oy + round(RET[1] * S) - 52, 3, 104, 104, Jugador=k)
    inst("TxtHudVida", ox + 160, oy + 31, 6, Jugador=k)
    for s in (1, 2, 3):
        cx, cy = round(CEN[s][0] * S), round(CEN[s][1] * S)
        inst("HudIcono", ox + cx - 27, oy + cy - 27, 4, 54, 54, Jugador=k, Slot=s)
        if s < 3:
            inst("TxtCd", ox + cx - 12, oy + cy - 14, 7, Jugador=k, Slot=s)
    yinv = oy + PH + 6 if k <= 2 else oy - 42
    for s in (1, 2, 3):
        inst("HudInv", ox + 160 + (s - 1) * 44, yinv, 4, 38, 38, Jugador=k, Slot=s)
BW, BH = 760, 137
inst("HudBanner", (1920 - BW) // 2, 14, 1, BW, BH)
IX, IY = 658, 985
inst("HudInfPanel", IX, IY, 1, 388, 95)
inst("HudDinPanel", IX + 398, IY, 1, 207, 95)
SLOTS = [(199, 289), (302, 392), (405, 501), (519, 610), (623, 736)]
for i, (x0, x1) in enumerate(SLOTS, 1):
    inst("HudSeg", IX + round(x0 * 0.5), IY + 20, 2, round((x1 - x0 + 1) * 0.5), 55, Idx=i)
inst("TxtHudDinero", IX + 398 + 85, IY + 32, 6)
inst("TxtHudTiempo", 760, 948, 6)
# otros textos del HUD que quedaban encima
for i in esc["instances"]:
    if i["name"] == "TxtAyuda": i["y"] = 165
    if i["name"] == "TxtJefe": i["y"] = 858
for o in esc["objects"]:
    if o["name"] == "TxtObjetivo": o["content"]["characterSize"] = 22

# ---------------- eventos ----------------
E = []
E.append(comentario("HUD con las piezas de interfaz: panel por jugador (retrato, vida, Habilidad Q, Especial E, arma), banner de objetivo, "
                    "infestación, dinero y tiempo. El HUD de texto anterior (TxtPanel, TxtInfest) queda oculto."))
E.append(ev([cvt("Estado", "\"intro\"")], [a("Cache", "HudFijo"), a("Cache", "HudDin")]))
E.append(ev([cvt("Estado", "\"intro\"", "!=")], [a("Montre", "HudFijo"), a("Cache", "HudInv")]))
for s_, n in ((1, "comida"), (2, "lanzable"), (3, "mordido")):
    E.append(ev([vnum("HudInv", "Slot", "=", s_)], [anim("HudInv", n)]))
for k in range(1, 5):
    E.append(ev([vnum("HudPanel", "Jugador", "=", k)], [anim("HudPanel", str(k))]))
    sup, ret = vnum("Sup", "Jugador", "=", k), vnum("HudRetrato", "Jugador", "=", k)
    E.append(ev([sup, ret], [a("SetAnimationName", "HudRetrato", "Sup.VariableString(Personaje)")]))
    E.append(ev([sup, ret, vtxt("Sup", "Estado", "normal")], [a("Opacity", "HudRetrato", "=", "255")]))
    E.append(ev([sup, ret, vtxt("Sup", "Estado", "normal", inv=True)], [a("Opacity", "HudRetrato", "=", "110")]))
    E.append(ev([sup, vnum("HudVida", "Jugador", "=", k)],
                [a("ChangeWidth", "HudVida", "=", "max(1, 238 * max(0, Sup.Variable(Vida)) / max(1, Sup.Variable(VidaMax)))")]))
    tv = vnum("TxtHudVida", "Jugador", "=", k)
    E.append(ev([sup, tv], [texto("TxtHudVida", "Sup.VariableString(Personaje) + \"  \" + ToString(round(Sup.Variable(Vida))) + \"/\" + ToString(Sup.Variable(VidaMax))")]))
    E.append(ev([sup, tv, vnum("Sup", "Control", "=", -1)], [texto("TxtHudVida", "TxtHudVida.String() + \"  [bot]\"")]))
    for s_, suf, tx in ((1, "_q", "HabTxt"), (2, "_e", "EspTxt")):
        ic = [sup, vnum("HudIcono", "Jugador", "=", k), vnum("HudIcono", "Slot", "=", s_)]
        ready = "LISTA" if s_ == 1 else "LISTO"
        E.append(ev(ic, [a("SetAnimationName", "HudIcono", f"Sup.VariableString(Personaje) + \"{suf}\"")]))
        E.append(ev(ic + [vtxt("Sup", tx, ready)], [a("Opacity", "HudIcono", "=", "255")]))
        E.append(ev(ic + [vtxt("Sup", tx, ready, inv=True)], [a("Opacity", "HudIcono", "=", "90")]))
        cd = [sup, vnum("TxtCd", "Jugador", "=", k), vnum("TxtCd", "Slot", "=", s_)]
        E.append(ev(cd, [texto("TxtCd", f"Sup.VariableString({tx})")]))
        E.append(ev(cd + [vtxt("Sup", tx, ready)], [texto("TxtCd", "\"\"")]))
        cx = ORIG[k][0] + round(CEN[s_][0] * S)
        E.append(ev([vnum("TxtCd", "Jugador", "=", k), vnum("TxtCd", "Slot", "=", s_)], [a("MettreX", "TxtCd", "=", f"{cx} - TxtCd.Width() / 2")]))
    E.append(ev([sup, vnum("HudIcono", "Jugador", "=", k), vnum("HudIcono", "Slot", "=", 3)],
                [a("SetAnimationName", "HudIcono", "Sup.VariableString(Arma)")]))
    # inventario (comida guardada, lanzable, mordido): todos ocultos arriba; se muestra el que corresponda
    for s_, cond in ((1, vnum("Sup", "ComidaCura", ">", 0)), (2, vtxt("Sup", "Lanz", "", inv=True)), (3, vnum("Sup", "Mordido", "=", 1))):
        E.append(ev([sup, cond, vnum("HudInv", "Jugador", "=", k), vnum("HudInv", "Slot", "=", s_), cvt("Estado", "\"intro\"", "!=")], [a("Montre", "HudInv", "")]))
# segmentos de infestación
for i in range(1, 6):
    E.append(ev([vnum("HudSeg", "Idx", "=", i), cvar("Infestacion", ">=", i), cvt("Estado", "\"intro\"", "!=")], [a("Montre", "HudSeg", "")]))
    E.append(ev([vnum("HudSeg", "Idx", "=", i), cvar("Infestacion", "<", i)], [a("Cache", "HudSeg")]))
E.append(ev([cvt("Estado", "\"intro\"")], [a("Cache", "HudSeg"), a("Cache", "HudInv")]))
E.append(ev([], [texto("TxtHudDinero", "ToString(floor(Variable(Dinero)))"),
                 a("MettreX", "TxtHudDinero", "=", f"{IX + 398 + 140} - TxtHudDinero.Width() / 2"),
                 texto("TxtHudTiempo", "\"Tiempo \" + ToString(floor(Variable(Tiempo) / 60)) + \":\" + VariableString(SegTxt) + \"     Nivel \" + "
                                       "ToString(Variable(Infestacion)) + \"/5     Tumbados \" + ToString(Variable(Tumbados))"),
                 a("MettreX", "TxtHudTiempo", "=", "960 - TxtHudTiempo.Width() / 2"),
                 # el objetivo va dentro del banner
                 a("MettreX", "TxtObjetivo", "=", f"{(1920 - BW) // 2 + 112 + (BW - 126) // 2} - TxtObjetivo.Width() / 2"),
                 a("MettreY", "TxtObjetivo", "=", f"{14 + BH // 2} - TxtObjetivo.Height() / 2"),
                 # el HUD de texto viejo queda oculto
                 a("Cache", "TxtPanel"), a("Cache", "TxtInfest")]))
NOM = "Interfaz: HUD con paneles"
EV = esc["events"]
EV[:] = [e for e in EV if e.get("name") != NOM]
EV.append(grupo(NOM, E))
p["resources"]["resources"] = list(recursos.values())
json.dump(p, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("OK fase 13:", len(objs), "objetos,", len(E), "eventos")
