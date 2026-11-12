"""Fase 14 de FDI-Z: pantallas Titulo, Menu (modo / unirse / personaje / dificultad) y Resultados con las piezas de interfaz.
Correr DESPUÉS de fase13_interfaz.py (con GDevelop cerrado):
    python fase14_pantallas.py <FDI-Z.json>
La lógica de teclado/control del menú NO cambia (sigue en fases_6_a_11.py); aquí solo se agregan imágenes, marcos y textos encima,
que se muestran u ocultan según la variable de escena Paso."""
import json, os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gd_util import *

ruta = sys.argv[1]
RAIZ = os.path.dirname(os.path.abspath(ruta))
p = json.load(open(ruta, encoding="utf-8"))
UI = "assets/interfaz/"
recursos = {r["name"]: r for r in p["resources"]["resources"]}
def img(nombre, archivo):
    recursos[nombre] = res_imagen(nombre, archivo); return nombre

# ---------- helpers de eventos ----------
def cmp(e1, op, e2): return c("BuiltinCommonInstructions::CompareNumbers", e1, op, e2)
def vnum(o, v, op, val): return c("VarObjet", o, v, op, str(val))
def cvar(v, op, val): return c("VarScene", v, op, str(val))
def cvt(v, val, op="="): return c("VarSceneTxt", v, op, val)
def svt(v, val): return a("ModVarSceneTxt", v, "=", val)
def gtxt(v, val, op="="): return c("VarGlobalTxt", v, op, val)
def texto(o, expr): return a("TextObject::String", o, "=", expr)
def anim(o, expr): return a("SetAnimationName", o, expr)
def o_(*conds): return {"type": {"value": "BuiltinCommonInstructions::Or"}, "parameters": [], "subInstructions": list(conds)}
def fija(o, x=None, y=None):
    r = []
    if x is not None: r.append(a("MettreX", o, "=", str(x)))
    if y is not None: r.append(a("MettreY", o, "=", str(y)))
    return r
def centra_x(o, cx): return a("MettreX", o, "=", f"{cx} - {o}.Width() / 2")
def centra_y(o, cy): return a("MettreY", o, "=", f"{cy} - {o}.Height() / 2")
def opac(o, v): return a("Opacity", o, "=", str(v))

def spr(nombre, anims, variables=()):
    return objeto_sprite(nombre, [animacion(n, [img(f"p14_{nombre}_{n}", f if f.startswith("assets/") else UI + f)], 1, False, (0, 0)) for n, f in anims], list(variables))
def panel(nombre, archivo, m, ancho=200, alto=100):
    """Marco de 9 cortes: el PNG se arma aquí al tamaño exacto (los bordes no se estiran) y se usa como Sprite normal."""
    l, t, r, b = m
    src = Image.open(os.path.join(RAIZ, archivo)).convert("RGBA"); W, H = src.size
    out = Image.new("RGBA", (ancho, alto))
    xs = [(0, l, 0, l), (l, W - r, l, ancho - r), (W - r, W, ancho - r, ancho)]
    ys = [(0, t, 0, t), (t, H - b, t, alto - b), (H - b, H, alto - b, alto)]
    for sx0, sx1, dx0, dx1 in xs:
        for sy0, sy1, dy0, dy1 in ys:
            parte = src.crop((sx0, sy0, sx1, sy1)).resize((dx1 - dx0, dy1 - dy0), Image.NEAREST)
            out.paste(parte, (dx0, dy0))
    rel = f"assets/interfaz/hud/p9_{nombre}.png"
    out.save(os.path.join(RAIZ, rel))
    return spr(nombre, [("p", "hud/p9_" + nombre + ".png")], [var("Idx", 0), var("Slot", 0)])
def txt(nombre, tam=32, color="255;255;255", alin="left", contorno=4, vars_=("Idx", "Slot")):
    o = obj_texto_base(nombre, tam, color, alin)
    o["content"]["outlineThickness"] = contorno
    o["content"]["isOutlineEnabled"] = contorno > 0
    o["variables"] = [var(v, 0) for v in vars_]
    return o
def obj_texto_base(nombre, tam, color, alin):
    return {"assetStoreId": "", "name": nombre, "type": "TextObject::Text", "variables": [], "effects": [], "behaviors": [],
            "content": {"bold": True, "isOutlineEnabled": True, "isShadowEnabled": False, "italic": False, "outlineColor": "0;0;0",
                        "outlineThickness": 4, "shadowAngle": 90, "shadowBlurRadius": 2, "shadowColor": "0;0;0", "shadowDistance": 4,
                        "shadowOpacity": 127, "smoothed": False, "underlined": False, "text": "", "font": "", "textAlignment": alin,
                        "verticalTextAlignment": "top", "characterSize": tam, "lineHeight": 0, "color": color}}
def I(nombre, x, y, z=1, w=None, h=None, **vs):
    return instancia(nombre, x, y, "", z, w, h, [var(k, v) for k, v in vs.items()])

# ---------- pieza auxiliar: velo oscuro y detección de la barra gris de los botones de dificultad ----------
os.makedirs(os.path.join(RAIZ, "assets/interfaz/hud"), exist_ok=True)
Image.new("RGBA", (8, 8), (0, 0, 0, 255)).save(os.path.join(RAIZ, "assets/interfaz/hud/velo.png"))
def barra(archivo):
    im = Image.open(os.path.join(RAIZ, archivo)).convert("RGB"); w, h = im.size; px = im.load()
    xs, ys = [], []
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            if 165 <= r <= 235 and 165 <= g <= 235 and 165 <= b <= 240 and max(r, g, b) - min(r, g, b) < 30:
                xs.append(x); ys.append(y)
    return (min(xs), min(ys), max(xs), max(ys), w, h)

def capa_escena(nombre):
    return next(l for l in p["layouts"] if l["name"] == nombre)
def nuevo(esc, objetos, instancias, eventos, variables=(), grupos=()):
    nom = {o["name"] for o in objetos}
    esc["objects"] = [o for o in esc["objects"] if o["name"] not in nom] + objetos
    esc["instances"] = [i for i in esc["instances"] if i["name"] not in nom] + instancias
    esc["events"] = esc["events"] + eventos
    esc["variables"] = [v for v in esc["variables"] if v["name"] not in {x["name"] for x in variables}] + list(variables)
    esc["objectsGroups"] = [g for g in esc["objectsGroups"] if g["name"] not in {x["name"] for x in grupos}] + list(grupos)
def grp(nombre, objs): return {"name": nombre, "objects": [{"name": n} for n in objs]}
def quita_obj(esc, nombres):
    esc["objects"] = [o for o in esc["objects"] if o["name"] not in nombres]
    esc["instances"] = [i for i in esc["instances"] if i["name"] not in nombres]
def quita_accion(eventos, tipo, objeto=None):
    for e in eventos:
        if "actions" in e:
            e["actions"] = [x for x in e["actions"] if not (x["type"]["value"] == tipo and (objeto is None or x["parameters"][0] == objeto))]
        if "events" in e: quita_accion(e["events"], tipo, objeto)
def tamano(esc, nombre, tam):
    for o in esc["objects"]:
        if o["name"] == nombre: o["content"]["characterSize"] = tam
def mover(esc, nombre, x=None, y=None):
    for i in esc["instances"]:
        if i["name"] == nombre:
            if x is not None: i["x"] = x
            if y is not None: i["y"] = y

PJS = ["tony", "miranda", "cesar", "alan", "castillo", "alessandro", "gabo", "carlos"]
NOMB = {"tony": "TONY", "miranda": "MIRANDA", "cesar": "CÉSAR", "alan": "ALAN", "castillo": "CASTILLO", "alessandro": "ALESSANDRO", "gabo": "GABO", "carlos": "CARLOS"}
DESC = {"tony": "Cocinar / Modo gym", "miranda": "Arrullo / Minigun", "cesar": "Hackeo / Control escuela", "alan": "Gorrear / Reembolso",
        "castillo": "Tragar / App de salud", "alessandro": "Chiste / Reloj", "gabo": "Supervelocidad / Ecosistema", "carlos": "Llave maestra / Tanque"}

# =====================================================================  TÍTULO
t = capa_escena("Titulo")
quita_obj(t, ["Fondo"])
quita_accion(t["events"], "ChangeColor", "Fondo")
objs = [spr("Fondo", [("t", UI + "bg_titulo.png")]), spr("Logo", [("l", UI + "logo_fdiz_1.png")]),
        panel("Cartel", UI + "ui_boton_seleccionado.png", (24, 23, 24, 24), 800, 170),
        ]
inst = [I("Fondo", 0, 0, 0, 1920, 1080), I("Logo", 960 - 450, 40, 3, 900, 358), I("Cartel", 1050, 770, 2, 800, 170)]
ev_t = [
    comentario("Título con el fondo ilustrado, el logo y el cartel de inicio. El texto y la lógica de teclado siguen igual."),
    ev([], [texto("TxtSub", "\"PRESIONA ENTER, ESPACIO O CLIC\" + NewLine() + \"(CONTROL: A)\""), texto("TxtTitulo", "\"La FDI se llenó de zombies. Escapen.\""),
            centra_x("TxtSub", 1490), centra_y("TxtSub", 855), centra_x("TxtTitulo", 1450), a("MettreY", "TxtTitulo", "=", "965")]),
]
tamano(t, "TxtSub", 34); tamano(t, "TxtTitulo", 32)
for o_t in t["objects"]:
    if o_t["name"] == "TxtTitulo": o_t["content"]["color"] = "255;235;140"
nuevo(t, objs, inst, ev_t)
mover(t, "TxtSub", y=855)
for i_ in t["instances"]:
    if i_["name"] == "TxtSub": i_["zOrder"] = 6

# =====================================================================  MENÚ
m = capa_escena("Menu")

tamano(m, "TxtMenu", 44); tamano(m, "TxtPie", 24)
CARTAS = ["SelPanel", "SelMarco", "SelRetrato", "TxtNom", "TxtCtl", "TxtListo", "TxtFlechas"]
CARTAS_EQ = ["SelIcono", "TxtDs"]
MODO = ["MarcoModo", "IlusModo", "TxtCapA", "TxtCapB"]
DIF = ["DifBtn", "TxtDif"]
barras = {n: barra(UI + f"ui_boton_{n}.png") for n in ("facil", "normal_dificultad", "dificil")}
barras["normal_dificultad"] = (170, 75, 342, 115, 512, 190)
barras["dificil"] = (165, 66, 369, 106, 488, 172)
print("barras gris:", barras)
DIFN = [("facil", "FÁCIL"), ("normal_dificultad", "NORMAL"), ("dificil", "PESADILLA")]
ICON_ANIMS = [(f"{pj}_{s}", f"hud/ico128_{pj}_{f}.png") for pj in PJS for s, f in (("q", "q"), ("e", "e"), ("p", "pasiva"))]
RETR = [(pj, f"retrato_{pj}.png") for pj in PJS] + [("silueta", "retrato_silueta.png"), ("vacio", "retrato_vacio.png")]
objs = [
    spr("Fondo", [("modo", UI + "bg_modos.png"), ("sel", UI + "bg_seleccion.png")]),
    spr("Velo", [("v", "assets/interfaz/hud/velo.png".replace("assets/interfaz/", UI))]),
    spr("Placa", [("p", UI + "ui_placa_titulo.png")]),
    panel("BarraPie", UI + "ui_panel_detalle.png", (11, 11, 11, 11), 1840, 72),
    txt("TxtSubM", 28, "255;235;140", "center"),
    # modo
    spr("MarcoModo", [("n", UI + "ui_ranura_retrato.png"), ("s", UI + "ui_ranura_retrato_sel.png")], [var("Idx", 0)]),
    spr("IlusModo", [("e", UI + "ilus_modo_escape.png"), ("j", UI + "ilus_modo_jefe.png")], [var("Idx", 0)]),
    txt("TxtCapA", 40, "255;235;140", "center"), txt("TxtCapB", 26, "255;255;255", "center"),
    # cartas de jugador
    panel("SelPanel", UI + "ui_panel_tienda.png", (45, 45, 45, 45), 410, 640),
    panel("SelMarco", UI + "ui_ranura_retrato_sel.png", (33, 33, 34, 36), 430, 660),
    spr("SelRetrato", RETR, [var("Slot", 0)]),
    txt("TxtNom", 38, "255;235;140", "center"), txt("TxtCtl", 24, "190;230;255", "center"), txt("TxtListo", 40, "120;255;120", "center"),
    txt("TxtFlechas", 36, "255;255;255", "center"),
    spr("SelIcono", ICON_ANIMS, [var("Slot", 0), var("Idx", 0)]), txt("TxtDs", 22, "255;255;255", "center"),
    # dificultad
    spr("DifBtn", [(n, UI + f"ui_boton_{n}.png") for n, _ in DIFN], [var("Idx", 0)]),
    txt("TxtDif", 32, "25;25;55", "center", 0),
]
CX = [300, 740, 1180, 1620]
inst = [I("Fondo", 0, 0, 0, 1920, 1080), I("Velo", 0, 0, 1, 1920, 1080), I("Placa", 610, 0, 2, 700, 190),
        I("BarraPie", 40, 948, 2, 1840, 72)]
inst += [I("TxtSubM", 960, 215, 5)]
for i, cx in enumerate((560, 1360)):
    inst += [I("MarcoModo", cx - 220, 250, 2, 440, 420, Idx=i), I("IlusModo", cx - 170, 288, 3, 340, 322, Idx=i),
             I("TxtCapA", cx, 690, 5, Idx=i), I("TxtCapB", cx, 745, 5, Idx=i)]
for k, cx in enumerate(CX, 1):
    inst += [I("SelMarco", cx - 215, 240, 1, 430, 660, Slot=k), I("SelPanel", cx - 205, 250, 2, 410, 640, Slot=k),
             I("SelRetrato", cx - 110, 275, 3, 220, 220, Slot=k), I("TxtNom", cx, 510, 5, Slot=k), I("TxtCtl", cx, 560, 5, Slot=k),
             I("TxtFlechas", cx, 770, 5, Slot=k), I("TxtListo", cx, 820, 5, Slot=k), I("TxtDs", cx, 700, 5, Slot=k)]
    for j in (1, 2, 3):
        inst.append(I("SelIcono", cx - 100 + (j - 1) * 70 - 12 + 24, 620, 4, 64, 64, Slot=k, Idx=j))
Y_DIF = [265, 455, 655]
for i, (n, _) in enumerate(DIFN):
    b = barras[n]; w0, h0 = b[4], b[5]; esc_ = 0.95
    inst.append(I("DifBtn", 960 - round(w0 * esc_ / 2), Y_DIF[i], 3, round(w0 * esc_), round(h0 * esc_), Idx=i))
    inst.append(I("TxtDif", 960, Y_DIF[i] + round(((b[1] + b[3]) / 2) * esc_), 5, Idx=i))

E = [comentario("Pantallas del menú con piezas de interfaz. Cada paso muestra su grupo y oculta los demás (Paso = modo / unirse / equipo / dificultad).")]
# fondo y títulos por paso
E += [ev([cvt("Paso", "\"unirse\"")], [anim("Fondo", "\"sel\"")]), ev([cvt("Paso", "\"equipo\"")], [anim("Fondo", "\"sel\"")]),
      ev([cvt("Paso", "\"modo\"")], [anim("Fondo", "\"modo\"")]), ev([cvt("Paso", "\"dificultad\"")], [anim("Fondo", "\"modo\"")]),
      ev([], [opac("Velo", 75), opac("Fondo", 255)])]
for paso, titulo in (("modo", "ELIGE EL MODO"), ("unirse", "ÚNANSE"), ("equipo", "ELIGEN SU PERSONAJE"), ("dificultad", "DIFICULTAD")):
    E.append(ev([cvt("Paso", f"\"{paso}\"")], [texto("TxtMenu", f"\"{titulo}\"")]))
E.append(ev([], [centra_x("TxtMenu", 960), centra_y("TxtMenu", 96), texto("TxtSlots", "\"\"")] if True else []))
E.append(ev([cvt("Paso", "\"unirse\"")], [texto("TxtSubM", "\"P1 ya está listo con teclado y ratón. Para sumar un control, presiona A en él.\" + VariableString(JefeLinea)")]))
E.append(ev([cvt("Paso", "\"unirse\"", "!=")], [texto("TxtSubM", "\"\"")]))
E.append(ev([cvt("Paso", "\"dificultad\"")], [texto("TxtSubM", "\"Fácil: menos zombies y daño · Pesadilla: más infección, más vida y más daño\"")]))
E.append(ev([], [centra_x("TxtSubM", 960), centra_y("TxtPie", 984), centra_x("TxtPie", 960)]))
# visibilidad por paso
E += [ev([cvt("Paso", "\"modo\"")], [a("Montre", "MarcoModo", ""), a("Montre", "IlusModo", ""), a("Montre", "TxtCapA", ""), a("Montre", "TxtCapB", "")]),
      ev([cvt("Paso", "\"modo\"", "!=")], [a("Cache", "MarcoModo"), a("Cache", "IlusModo"), a("Cache", "TxtCapA"), a("Cache", "TxtCapB")]),
      ev([o_(cvt("Paso", "\"unirse\""), cvt("Paso", "\"equipo\""))], [a("Montre", g, "") for g in CARTAS]),
      ev([cvt("Paso", "\"unirse\"", "!="), cvt("Paso", "\"equipo\"", "!=")], [a("Cache", g) for g in CARTAS]),
      ev([cvt("Paso", "\"equipo\"")], [a("Montre", g, "") for g in CARTAS_EQ]),
      ev([cvt("Paso", "\"equipo\"", "!=")], [a("Cache", g) for g in CARTAS_EQ]),
      ev([cvt("Paso", "\"dificultad\"")], [a("Montre", "DifBtn", ""), a("Montre", "TxtDif", "")]),
      ev([cvt("Paso", "\"dificultad\"", "!=")], [a("Cache", "DifBtn"), a("Cache", "TxtDif")]),
      ev([cvt("Paso", "\"dificultad\"")], [a("Montre", "BarraPie", "")]) if False else ev([], [a("Montre", "BarraPie", "")])]
# modo
for i, (an, ti_, sub) in enumerate((("e", "ESCAPE", "1 a 4 jugadores + bots"), ("j", "JEFE DE ZOMBIES", "1 a 3 contra el Jefe (él juega con el ratón)"))):
    E.append(ev([vnum("IlusModo", "Idx", "=", i)], [anim("IlusModo", f"\"{an}\"")]))
    E.append(ev([vnum("TxtCapA", "Idx", "=", i)], [texto("TxtCapA", f"\"{ti_}\""), centra_x("TxtCapA", 560 if i == 0 else 1360)]))
    E.append(ev([vnum("TxtCapB", "Idx", "=", i)], [texto("TxtCapB", f"\"{sub}\""), centra_x("TxtCapB", 560 if i == 0 else 1360)]))
    E.append(ev([vnum("MarcoModo", "Idx", "=", i), cvar("Sel", "=", i)], [anim("MarcoModo", "\"s\""), opac("MarcoModo", 255)]))
    E.append(ev([vnum("MarcoModo", "Idx", "=", i), cvar("Sel", "!=", i)], [anim("MarcoModo", "\"n\""), opac("MarcoModo", 110)]))
    E.append(ev([vnum("IlusModo", "Idx", "=", i), cvar("Sel", "=", i)], [opac("IlusModo", 255)]))
    E.append(ev([vnum("IlusModo", "Idx", "=", i), cvar("Sel", "!=", i)], [opac("IlusModo", 100)]))
# cartas: textos por jugador
for k in range(1, 5):
    for i, pj in enumerate(PJS):
        E.append(ev([cvar(f"S{k}Pj", "=", i)], [svt(f"K{k}", f"\"{pj}\""), svt(f"NM{k}", f"\"{NOMB[pj]}\""), svt(f"DS{k}", f"\"{DESC[pj]}\"")]))
    slot = lambda o: vnum(o, "Slot", "=", k)
    # retrato: en "unirse" el slot libre se ve vacío y el unido como silueta; en "equipo" cada uno muestra su personaje
    E.append(ev([cvt("Paso", "\"equipo\""), slot("SelRetrato")], [anim("SelRetrato", f"VariableString(K{k})")]))
    E.append(ev([cvt("Paso", "\"unirse\""), slot("SelRetrato"), cvar(f"S{k}Ctl", "=", -1)], [anim("SelRetrato", "\"vacio\"")]))
    E.append(ev([cvt("Paso", "\"unirse\""), slot("SelRetrato"), cvar(f"S{k}Ctl", "!=", -1)], [anim("SelRetrato", "\"silueta\"")]))
    E.append(ev([slot("SelRetrato"), cvt("Paso", "\"equipo\""), cvar(f"S{k}Ctl", "=", -1)], [opac("SelRetrato", 190)]))
    E.append(ev([slot("SelRetrato"), o_(cvt("Paso", "\"unirse\""), cvar(f"S{k}Ctl", "!=", -1))], [opac("SelRetrato", 255)]))
    E.append(ev([cvt("Paso", "\"equipo\""), slot("TxtNom")], [texto("TxtNom", f"VariableString(NM{k})")]))
    E.append(ev([cvt("Paso", "\"unirse\""), slot("TxtNom")], [texto("TxtNom", f"\"JUGADOR {k}\"")]))
    E.append(ev([slot("TxtNom")], [centra_x("TxtNom", CX[k - 1])]))
    E.append(ev([slot("TxtCtl")], [texto("TxtCtl", f"VariableString(C{k})"), centra_x("TxtCtl", CX[k - 1])]))
    E.append(ev([cvt("Paso", "\"unirse\""), slot("TxtCtl"), cvar(f"S{k}Ctl", "=", -1)], [texto("TxtCtl", "\"libre (A en un control)\""), centra_x("TxtCtl", CX[k - 1])]))
    E.append(ev([slot("TxtDs")], [texto("TxtDs", f"VariableString(DS{k})"), centra_x("TxtDs", CX[k - 1])]))
    E.append(ev([slot("SelIcono")] + [cvt("Paso", "\"equipo\"")], [anim("SelIcono", f"VariableString(K{k}) + \"_q\"")]) if False else
             ev([slot("SelIcono"), vnum("SelIcono", "Idx", "=", 1)], [anim("SelIcono", f"VariableString(K{k}) + \"_q\"")]))
    E.append(ev([slot("SelIcono"), vnum("SelIcono", "Idx", "=", 2)], [anim("SelIcono", f"VariableString(K{k}) + \"_e\"")]))
    E.append(ev([slot("SelIcono"), vnum("SelIcono", "Idx", "=", 3)], [anim("SelIcono", f"VariableString(K{k}) + \"_p\"")]))
    # LISTO, flechas y marco de selección
    E.append(ev([slot("TxtListo"), cvar(f"S{k}Ok", "=", 1), cvt("Paso", "\"equipo\"")], [texto("TxtListo", "\"¡LISTO!\""), centra_x("TxtListo", CX[k - 1])]))
    E.append(ev([slot("TxtListo"), o_(cvar(f"S{k}Ok", "!=", 1), cvt("Paso", "\"equipo\"", "!="))], [texto("TxtListo", "\"\"")]))
    E.append(ev([slot("TxtFlechas"), cvt("Paso", "\"equipo\""), cvar(f"S{k}Ok", "=", 0), cvar(f"S{k}Ctl", "!=", -1)], [texto("TxtFlechas", "\"<     >\""), centra_x("TxtFlechas", CX[k - 1])]))
    E.append(ev([slot("TxtFlechas"), o_(cvt("Paso", "\"equipo\"", "!="), cvar(f"S{k}Ok", "=", 1), cvar(f"S{k}Ctl", "=", -1))], [texto("TxtFlechas", "\"\"")]))
    E.append(ev([slot("SelMarco"), cvar(f"S{k}Ok", "=", 1), cvt("Paso", "\"equipo\"")], [a("Montre", "SelMarco", "")]))
    E.append(ev([slot("SelMarco"), o_(cvar(f"S{k}Ok", "!=", 1), cvt("Paso", "\"equipo\"", "!="))], [a("Cache", "SelMarco")]))
    E.append(ev([slot("SelPanel"), cvar(f"S{k}Ctl", "=", -1)], [opac("SelPanel", 170)]))
    E.append(ev([slot("SelPanel"), cvar(f"S{k}Ctl", "!=", -1)], [opac("SelPanel", 255)]))
# dificultad
for i, (n, nombre) in enumerate(DIFN):
    b = barras[n]
    E.append(ev([vnum("DifBtn", "Idx", "=", i)], [anim("DifBtn", f"\"{n}\"")]))
    E.append(ev([vnum("TxtDif", "Idx", "=", i)], [texto("TxtDif", f"\"{nombre}\""), centra_x("TxtDif", 960 + round(((b[0] + b[2]) / 2 - b[4] / 2) * 0.95)),
                                                  a("MettreY", "TxtDif", "=", f"{Y_DIF[i] + round(((b[1] + b[3]) / 2) * 0.95)} - TxtDif.Height() / 2")]))
    E.append(ev([vnum("DifBtn", "Idx", "=", i), cvar("Sel", "=", i)], [opac("DifBtn", 255)]))
    E.append(ev([vnum("DifBtn", "Idx", "=", i), cvar("Sel", "!=", i)], [opac("DifBtn", 120)]))
# el texto largo anterior de cada paso queda oculto: ahora lo dibujan las cartas
vars_nuevas = [var(f"{pref}{k}", "") for pref in ("K", "NM", "DS") for k in range(1, 5)]
grupos_ = [grp("CartasJugador", CARTAS), grp("CartasEquipo", CARTAS_EQ)]
nuevo(m, objs, inst, E, vars_nuevas, grupos_)
# TxtMenu / TxtPie quedan sobre la placa y la barra
mover(m, "TxtMenu", y=80); mover(m, "TxtPie", y=968)
for i in m["instances"]:
    if i["name"] in ("TxtMenu", "TxtPie"): i["zOrder"] = 6

# =====================================================================  RESULTADOS
r = capa_escena("Resultados")
objs = [spr("Fondo", [("v", UI + "bg_victoria.png"), ("d", UI + "bg_derrota.png")]),
        spr("Banner", [("v", UI + "ui_banner_victoria.png"), ("d", UI + "ui_banner_derrota.png")]),
        panel("PanelRes", UI + "ui_panel_resultados.png", (11, 11, 11, 22), 840, 600),
        panel("BarraPieR", UI + "ui_panel_detalle.png", (11, 11, 11, 11), 1840, 72)]
inst = [I("Fondo", 0, 0, 0, 1920, 1080), I("Banner", 1000 - 380, 30, 2, 760, 224), I("PanelRes", 1040, 290, 2, 840, 600), I("BarraPieR", 40, 948, 2, 1840, 72)]
Er = [comentario("Resultados con fondo y banner de victoria o derrota; el panel de premios queda a la derecha para no tapar la ilustración."),
      ev([gtxt("Resultado", "\"victoria\"")], [anim("Fondo", "\"v\""), anim("Banner", "\"v\"")]),
      ev([gtxt("Resultado", "\"victoria\"", "!=")], [anim("Fondo", "\"d\""), anim("Banner", "\"d\"")]),
      ev([], [centra_x("TxtRes", 1000), centra_y("TxtRes", 142), centra_x("TxtDet", 1460), a("MettreY", "TxtDet", "=", "400"),
              centra_x("TxtPie", 960), centra_y("TxtPie", 984)])]
nuevo(r, objs, inst, Er)
tamano(r, "TxtRes", 56); tamano(r, "TxtDet", 28); tamano(r, "TxtPie", 24)
mover(r, "TxtRes", x=960, y=100); mover(r, "TxtDet", y=400); mover(r, "TxtPie", y=968)
for i in r["instances"]:
    if i["name"] in ("TxtRes", "TxtDet", "TxtPie"): i["zOrder"] = 6
# el texto de resultados va centrado en su lugar (centrar() de escena usaba 960)
quita_accion(r["events"], "MettreX", None) if False else None

p["resources"]["resources"] = list(recursos.values())
json.dump(p, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("OK fase 14: Titulo, Menu y Resultados con interfaz")
