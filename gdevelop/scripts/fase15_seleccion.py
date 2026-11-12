"""Fase 15 de FDI-Z: pantalla de selección de personaje como el mockup (personaje grande, cuadrícula de 8, habilidades, 4 barras de jugador).
Correr DESPUÉS de fase14_pantallas.py (GDevelop cerrado):   python fase15_seleccion.py <FDI-Z.json>
No cambia la lógica anterior (A/D, F, pads, Enter). Agrega: clic en un retrato = elegir (primero P1, luego los bots en orden),
clic derecho = quitar, W/S o arriba/abajo = cambiar de fila. El marco de cada retrato toma el color del jugador que lo tiene."""
import json, os, sys, shutil
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gd_util import *

ruta = sys.argv[1]
RAIZ = os.path.dirname(os.path.abspath(ruta))
p = json.load(open(ruta, encoding="utf-8"))
UI = "assets/interfaz/"
recursos = {r["name"]: r for r in p["resources"]["resources"]}
def img(nombre, archivo):
    recursos[nombre] = res_imagen(nombre, archivo); return nombre

def cvar(v, op, val): return c("VarScene", v, op, str(val))
def cvt(v, val, op="="): return c("VarSceneTxt", v, op, val)
def vnum(o, v, op, val): return c("VarObjet", o, v, op, str(val))
def svar(v, op, val): return a("ModVarScene", v, op, str(val))
def svt(v, val): return a("ModVarSceneTxt", v, "=", val)
def texto(o, expr): return a("TextObject::String", o, "=", expr)
def anim(o, expr): return a("SetAnimationName", o, expr)
def suelta(k): return c("KeyReleased", "", k)
def pad_suelta(k, b): return c("Gamepads::C_Button_released", "", str(k), f"\"{b}\"", "")
def stimer(t, seg): return c("CompareTimer", "", f"\"{t}\"", ">=", str(seg))
def cmp(e1, op, e2): return c("BuiltinCommonInstructions::CompareNumbers", e1, op, e2)
def o_(*conds): return {"type": {"value": "BuiltinCommonInstructions::Or"}, "parameters": [], "subInstructions": list(conds)}
def opac(o, v): return a("Opacity", o, "=", str(v))
def fx(o, expr): return a("MettreX", o, "=", expr)
def fy(o, expr): return a("MettreY", o, "=", expr)
def mouse_en(x0, y0, w, h):
    return [cmp("MouseX()", ">=", x0), cmp("MouseX()", "<", x0 + w), cmp("MouseY()", ">=", y0), cmp("MouseY()", "<", y0 + h)]

def spr(nombre, anims, variables=()):
    return objeto_sprite(nombre, [animacion(n, [img(f"p15_{nombre}_{n}", f if f.startswith("assets/") else UI + f)], 1, False, (0, 0)) for n, f in anims], list(variables))
def txt(nombre, tam=26, color="255;255;255", alin="left", contorno=4):
    return {"assetStoreId": "", "name": nombre, "type": "TextObject::Text", "variables": [var("Idx", 0), var("Slot", 0)], "effects": [], "behaviors": [],
            "content": {"bold": True, "isOutlineEnabled": contorno > 0, "isShadowEnabled": False, "italic": False, "outlineColor": "0;0;0",
                        "outlineThickness": contorno, "shadowAngle": 90, "shadowBlurRadius": 2, "shadowColor": "0;0;0", "shadowDistance": 4,
                        "shadowOpacity": 127, "smoothed": False, "underlined": False, "text": "", "font": "", "textAlignment": alin,
                        "verticalTextAlignment": "top", "characterSize": tam, "lineHeight": 0, "color": color}}
def I(nombre, x, y, z=1, w=None, h=None, **vs):
    return instancia(nombre, x, y, "", z, w, h, [var(k, v) for k, v in vs.items()])

# ---------------- piezas hechas aquí ----------------
SEL = "assets/interfaz/sel/"
os.makedirs(os.path.join(RAIZ, SEL), exist_ok=True)
PJS = ["tony", "miranda", "cesar", "alan", "castillo", "alessandro", "gabo", "carlos"]
NOMB = {"tony": "TONY", "miranda": "MIRANDA", "cesar": "CÉSAR", "alan": "ALAN", "castillo": "CASTILLO", "alessandro": "ALESSANDRO", "gabo": "GABO", "carlos": "CARLOS"}
COL = [(255, 220, 40), (70, 170, 255), (130, 235, 70), (255, 100, 200)]
for pj in PJS:   # cuerpo completo de frente
    shutil.copy(os.path.join(RAIZ, "..", "..", "generado", "sprites", "personajes", pj, "caminar_abajo", "caminar_abajo_00.png"), os.path.join(RAIZ, SEL, f"cuerpo_{pj}.png"))
def guarda(im, nombre): im.save(os.path.join(RAIZ, SEL, nombre))
# celda
cel = Image.new("RGBA", (156, 156), (18, 22, 58, 255)); d = ImageDraw.Draw(cel)
d.rectangle((0, 0, 155, 155), outline=(70, 82, 140, 255), width=4); d.rectangle((4, 4, 151, 151), outline=(10, 12, 36, 255), width=2); guarda(cel, "celda.png")
# marcos de selección (uno por jugador, 168x168, borde 7)
for k, col in enumerate(COL, 1):
    m = Image.new("RGBA", (168, 168), (0, 0, 0, 0)); d = ImageDraw.Draw(m)
    d.rectangle((0, 0, 167, 167), outline=col + (255,), width=7); d.rectangle((7, 7, 160, 160), outline=(0, 0, 0, 200), width=2); guarda(m, f"marco_p{k}.png")
# barras de jugador (400x108)
for k, col in enumerate(COL, 1):
    b = Image.new("RGBA", (400, 108), (14, 18, 52, 255)); d = ImageDraw.Draw(b)
    d.rectangle((0, 0, 399, 107), outline=col + (255,), width=6); d.rectangle((6, 6, 393, 101), outline=(0, 0, 0, 160), width=2)
    d.rectangle((14, 14, 99, 93), fill=(8, 10, 30, 255), outline=col + (255,), width=3); guarda(b, f"barra_p{k}.png")
# foco de luz bajo el personaje
foc = Image.new("RGBA", (460, 120), (0, 0, 0, 0)); d = ImageDraw.Draw(foc)
for i, al in enumerate((22, 40, 62, 90)):
    d.ellipse((i * 18, i * 7, 459 - i * 18, 119 - i * 7), fill=(120, 210, 235, al))
guarda(foc, "foco.png")
# marco 9 cortes del personaje grande (borde teal)
def nueve(archivo, m, ancho, alto, salida):
    l, t, r, b = m
    src = Image.open(os.path.join(RAIZ, archivo)).convert("RGBA"); W, H = src.size
    out = Image.new("RGBA", (ancho, alto))
    xs = [(0, l, 0, l), (l, W - r, l, ancho - r), (W - r, W, ancho - r, ancho)]
    ys = [(0, t, 0, t), (t, H - b, t, alto - b), (H - b, H, alto - b, alto)]
    for sx0, sx1, dx0, dx1 in xs:
        for sy0, sy1, dy0, dy1 in ys:
            out.paste(src.crop((sx0, sy0, sx1, sy1)).resize((dx1 - dx0, dy1 - dy0), Image.NEAREST), (dx0, dy0))
    guarda(out, salida)
nueve(UI + "ui_marco_icono_teal.png", (24, 24, 24, 24), 630, 650, "marco_grande.png")
nueve(UI + "ui_panel_detalle.png", (11, 11, 11, 11), 651, 342, "panel_habilidades.png")

# ---------------- textos de habilidades ----------------
HAB = {
 "tony": [("Cocinar", "Deja 2 comidas; cerca de la nevería, un festín"), ("Modo gym (10 s)", "Fuerza x2 y 40 % menos daño"), ("Pasiva", "Gana dinero para el equipo")],
 "miranda": [("Arrullo", "Duerme a los zombies cercanos 6 s"), ("Minigun (8 s)", "Golpes rápidos de largo alcance"), ("Pasiva", "Se cura sola si no la golpean")],
 "cesar": [("Hackeo", "Abre la puerta cercana; objetivo al doble"), ("Control de la escuela", "Empuja y aturde zombies lejanos"), ("Rutas", "Cada 25 s marca el camino al objetivo")],
 "alan": [("Gorrear", "Aparece una regla y a veces comida"), ("Reembolso", "Escobas para quien pelea a puños"), ("Ojo de oferta", "Cada 30 s ve zonas oscuras cercanas")],
 "castillo": [("Tragar", "Se come un zombie cercano y cura 15"), ("App de salud", "Hasta 4 zombies pelean de su lado"), ("Pasiva", "La comida lo cura")],
 "alessandro": [("Chiste", "Los zombies cercanos se ríen 4 s"), ("Reloj", "Congela a todos los zombies 4 s"), ("Pasiva", "Recargas 20 % más rápidas cerca")],
 "gabo": [("Supervelocidad", "Velocidad x2 y avienta zombies (4 s)"), ("Ecosistema", "3 aparatos que distraen zombies 8 s"), ("AirDrop", "Pasa su arma a un compañero sin arma")],
 "carlos": [("Llave maestra", "Abre cualquier puerta cercana"), ("Tanque (8 s)", "50 % menos daño para el equipo"), ("Pasiva", "Recibe 25 % menos daño")],
}

# ---------------- objetos ----------------
GX = [1105, 1276, 1447, 1618]; GY = [212, 388]
BX = [95, 537, 979, 1421]; BYY = 941
ICON_ANIMS = [(f"{pj}_{s}", f"hud/ico128_{pj}_{f}.png") for pj in PJS for s, f in (("q", "q"), ("e", "e"), ("p", "pasiva"))]
RETR = [(pj, f"retrato_{pj}.png") for pj in PJS] + [("silueta", "retrato_silueta.png")]
objs = [
    spr("EqMarcoGrande", [("m", SEL + "marco_grande.png")]),
    spr("EqFoco", [("f", SEL + "foco.png")]),
    spr("EqCuerpo", [(pj, SEL + f"cuerpo_{pj}.png") for pj in PJS]),
    spr("EqPlaca", [("p", "ui_placa_nombre.png")]),
    txt("EqNombre", 36, "255;235;140", "center"), txt("EqSub", 22, "190;230;255", "center"),
    spr("EqCelda", [("c", SEL + "celda.png")], [var("Idx", 0)]),
    spr("EqRet", RETR, [var("Idx", 0)]),
    spr("EqSel", [(f"s{k}", SEL + f"marco_p{k}.png") for k in range(1, 5)], [var("Slot", 0)]),
] + [txt(f"EqTag{k}", 24, ";".join(map(str, COL[k - 1])), "left") for k in range(1, 5)] + [
    spr("EqPanel", [("p", SEL + "panel_habilidades.png")]),
    spr("EqIcoMarco", [("q", "ui_marco_icono_teal.png"), ("e", "ui_marco_icono_naranja.png"), ("p", "ui_marco_icono_morado.png")], [var("Idx", 0)]),
    spr("EqIco", ICON_ANIMS, [var("Idx", 0)]),
    txt("EqTitulo", 28, "255;235;140", "left"), txt("EqDesc", 20, "255;255;255", "left"),
    spr("EqBarra", [(f"b{k}", SEL + f"barra_p{k}.png") for k in range(1, 5)], [var("Slot", 0)]),
    spr("EqBarRet", RETR, [var("Slot", 0)]),
    txt("EqBarNom", 22, "255;255;255", "left"), txt("EqBarEst", 20, "190;230;255", "left"),
]
NOM_EQ = [o["name"] for o in objs]
inst = [I("EqMarcoGrande", 153, 216, 2, 630, 650), I("EqFoco", 237, 715, 3, 460, 120), I("EqCuerpo", 307, 262, 4, 320, 508),
        I("EqPlaca", 240, 813, 6, 455, 104), I("EqNombre", 467, 826, 8), I("EqSub", 467, 872, 8)]
for r in range(2):
    for cc in range(4):
        i = r * 4 + cc
        inst += [I("EqCelda", GX[cc], GY[r], 2, 156, 156, Idx=i), I("EqRet", GX[cc] + 10, GY[r] + 10, 3, 136, 136, Idx=i)]
for k in range(1, 5):
    inst += [I("EqSel", 1099, 206, 5, 168, 168, Slot=k), I(f"EqTag{k}", 1110, 218, 7),
             I("EqBarra", BX[k - 1], BYY, 2, 400, 108, Slot=k), I("EqBarRet", BX[k - 1] + 14, BYY + 14, 3, 86, 80, Slot=k),
             I("EqBarNom", BX[k - 1] + 112, BYY + 18, 5, Slot=k), I("EqBarEst", BX[k - 1] + 112, BYY + 60, 5, Slot=k)]
inst.append(I("EqPanel", 1109, 572, 2, 651, 342))
for j in (1, 2, 3):
    y = 590 + (j - 1) * 105
    inst += [I("EqIcoMarco", 1135, y, 3, 88, 88, Idx=j), I("EqIco", 1147, y + 12, 4, 64, 64, Idx=j),
             I("EqTitulo", 1245, y + 2, 5, Idx=j), I("EqDesc", 1245, y + 44, 5, Idx=j)]

# ---------------- eventos ----------------
EQ = cvt("Paso", "\"equipo\"")
E = [comentario("Selección de personaje al estilo del mockup. Foco = último jugador que movió su selección (o al que se le asignó con clic). "
                "Cola = siguiente espacio que se elige con el ratón (primero P1, luego los bots en orden).")]
vars_ = [var("Foco", 1), var("Cola", 0), var("KF", ""), var("NMF", "")] + [var(f"Prev{k}", -1) for k in range(1, 5)]
# visibilidad
E += [ev([EQ], [a("Montre", "SelEq", ""), a("Cache", "CartasJugador"), a("Cache", "CartasEquipo"), a("Cache", "BarraPie")]),
      ev([cvt("Paso", "\"equipo\"", "!=")], [a("Cache", "SelEq")])]
# Foco
for k in range(1, 5):
    E.append(ev([EQ, cvar(f"S{k}Ctl", "!=", -1), cmp(f"Variable(S{k}Pj)", "!=", f"Variable(Prev{k})")], [svar("Foco", "=", k)]))
    E.append(ev([], [svar(f"Prev{k}", "=", f"Variable(S{k}Pj)")]))
for k in range(1, 5):
    E.append(ev([cvar("Foco", "=", k)], [svt("KF", f"VariableString(K{k})"), svt("NMF", f"VariableString(NM{k})")]))
# personaje grande, nombre y subtítulo
E.append(ev([], [anim("EqCuerpo", "VariableString(KF)"), texto("EqNombre", "VariableString(NMF)"), fx("EqNombre", "467 - EqNombre.Width() / 2")]))
for k in range(1, 5):
    for ctl_ok, pref in ((("=", -1), f"BOT {k}"), (("!=", -1), f"P{k}")):
        for ok, suf in ((1, "LISTO"), (0, "eligiendo")):
            ok_c = cvar(f"S{k}Ok", "=", 1) if ok else cvar(f"S{k}Ok", "!=", 1)
            expr = f"\"{pref}  ·  {suf}\"" if ctl_ok[1] == -1 else f"\"{pref} · \" + VariableString(C{k}) + \"  ·  {suf}\""
            E.append(ev([cvar("Foco", "=", k), cvar(f"S{k}Ctl", ctl_ok[0], -1), ok_c], [texto("EqSub", expr), fx("EqSub", "467 - EqSub.Width() / 2")]))
# habilidades del personaje en foco
for pj in PJS:
    sub = []
    for j, (tt, dd) in enumerate(HAB[pj], 1):
        sub.append(ev([vnum("EqTitulo", "Idx", "=", j)], [texto("EqTitulo", f"\"{tt}\"")]))
        sub.append(ev([vnum("EqDesc", "Idx", "=", j)], [texto("EqDesc", f"\"{dd}\"")]))
    E.append(ev([cvt("KF", f"\"{pj}\"")], [], sub=sub))
for j, s_ in ((1, "q"), (2, "e"), (3, "p")):
    E.append(ev([vnum("EqIco", "Idx", "=", j)], [anim("EqIco", f"VariableString(KF) + \"_{s_}\"")]))
    E.append(ev([vnum("EqIcoMarco", "Idx", "=", j)], [anim("EqIcoMarco", f"\"{s_}\"")]))
# cuadrícula
for i, pj in enumerate(PJS):
    E.append(ev([vnum("EqRet", "Idx", "=", i)], [anim("EqRet", f"\"{pj}\"")]))
# marcos de selección, etiquetas y barras inferiores
for k in range(1, 5):
    px = f"1099 + mod(Variable(S{k}Pj), 4) * 171"; py = f"206 + floor(Variable(S{k}Pj) / 4) * 176"
    E.append(ev([vnum("EqSel", "Slot", "=", k)], [anim("EqSel", f"\"s{k}\""), fx("EqSel", px), fy("EqSel", py)]))
    E.append(ev([vnum("EqSel", "Slot", "=", k), cvar(f"S{k}Ok", "=", 1)], [opac("EqSel", 255)]))
    E.append(ev([vnum("EqSel", "Slot", "=", k), cvar(f"S{k}Ok", "!=", 1)], [opac("EqSel", 150)]))
    tag = f"EqTag{k}"
    E.append(ev([cvar(f"S{k}Ctl", "=", -1)], [texto(tag, f"\"BOT {k}\"")]))
    E.append(ev([cvar(f"S{k}Ctl", "!=", -1)], [texto(tag, f"\"P{k}\"")]))
    E.append(ev([], [fx(tag, f"1110 + mod(Variable(S{k}Pj), 4) * 171"), fy(tag, f"218 + floor(Variable(S{k}Pj) / 4) * 176")]))
    E.append(ev([vnum("EqBarra", "Slot", "=", k)], [anim("EqBarra", f"\"b{k}\"")]))
    E.append(ev([vnum("EqBarRet", "Slot", "=", k)], [anim("EqBarRet", f"VariableString(K{k})")]))
    E.append(ev([cvar(f"S{k}Ctl", "=", -1), vnum("EqBarNom", "Slot", "=", k)], [texto("EqBarNom", f"\"BOT {k} · \" + VariableString(NM{k})")]))
    E.append(ev([cvar(f"S{k}Ctl", "!=", -1), vnum("EqBarNom", "Slot", "=", k)], [texto("EqBarNom", f"\"P{k} · \" + VariableString(NM{k})")]))
    est = vnum("EqBarEst", "Slot", "=", k)
    E.append(ev([cvar(f"S{k}Ctl", "=", -1), cvar(f"S{k}Ok", "=", 1), est], [texto("EqBarEst", "\"LISTO\"")]))
    E.append(ev([cvar(f"S{k}Ctl", "=", -1), cvar(f"S{k}Ok", "!=", 1), cvar("Cola", "=", k), est], [texto("EqBarEst", "\"clic en un personaje\"")]))
    E.append(ev([cvar(f"S{k}Ctl", "=", -1), cvar(f"S{k}Ok", "!=", 1), cvar("Cola", "!=", k), est], [texto("EqBarEst", "\"automático\"")]))
    E.append(ev([cvar(f"S{k}Ctl", "!=", -1), cvar(f"S{k}Ok", "=", 1), est], [texto("EqBarEst", f"VariableString(C{k}) + \"  ·  LISTO\"")]))
    E.append(ev([cvar(f"S{k}Ctl", "!=", -1), cvar(f"S{k}Ok", "!=", 1), est], [texto("EqBarEst", f"VariableString(C{k}) + \"  ·  eligiendo\"")]))
# ratón: la cola y los clics
E.append(ev([], [svar("Cola", "=", 0)]))
for k in range(4, 0, -1):
    E.append(ev([EQ, o_(cvar(f"S{k}Ctl", "=", 0), cvar(f"S{k}Ctl", "=", -1)), cvar(f"S{k}Ok", "=", 0)], [svar("Cola", "=", k)]))
for r in range(2):
    for cc in range(4):
        i = r * 4 + cc
        libre = [o_(cmp(f"Variable(S{j}Pj)", "!=", i), cmp(f"Variable(S{j}Ok)", "!=", 1)) for j in range(1, 5)]
        E.append(ev([EQ, stimer("paso", 0.3), c("MouseButtonReleased", "", "Left"), *mouse_en(GX[cc], GY[r], 156, 156), cvar("Cola", ">", 0), *libre], [], sub=[
            ev([cvar("Cola", "=", t)], [svar(f"S{t}Pj", "=", i), svar(f"S{t}Ok", "=", 1), svar("Foco", "=", t)]) for t in range(1, 5)]))
        E.append(ev([EQ, c("MouseButtonReleased", "", "Right"), *mouse_en(GX[cc], GY[r], 156, 156)], [], sub=[
            ev([cvar(f"S{t}Pj", "=", i), cvar(f"S{t}Ok", "=", 1), o_(cvar(f"S{t}Ctl", "=", 0), cvar(f"S{t}Ctl", "=", -1))], [svar(f"S{t}Ok", "=", 0)]) for t in range(1, 5)]))
# choque entre espacios: si alguien ya confirmado tiene el mismo personaje, se mueve el que aún no confirma (el de menor número también)
for k in range(1, 5):
    for j in range(1, k):
        E.append(ev([EQ, cmp(f"Variable(S{j}Pj)", "=", f"Variable(S{k}Pj)"), cvar(f"S{j}Ok", "=", 0), cvar(f"S{k}Ok", "=", 1)],
                    [svar(f"S{j}Pj", "=", f"mod(Variable(S{j}Pj) + 1, 8)")]))
# teclado y control: arriba/abajo cambian de fila
E.append(ev([EQ, cvar("S1Ctl", "=", 0), cvar("S1Ok", "=", 0), o_(suelta("w"), suelta("Up"), suelta("s"), suelta("Down"))], [svar("S1Pj", "=", "mod(Variable(S1Pj) + 4, 8)")]))
for k in range(1, 5):
    for pad in range(1, 5):
        E.append(ev([EQ, cvar(f"S{k}Ctl", "=", pad), cvar(f"S{k}Ok", "=", 0), o_(pad_suelta(pad, "Up"), pad_suelta(pad, "Down"))], [svar(f"S{k}Pj", "=", f"mod(Variable(S{k}Pj) + 4, 8)")]))
# pie de pantalla
E.append(ev([EQ], [texto("TxtPie", "\"Clic: elegir (P1, luego los bots) · clic derecho: quitar · Teclado: WASD mover, F aceptar · Enter: seguir · Esc: volver\""),
                   a("MettreX", "TxtPie", "=", "960 - TxtPie.Width() / 2"), a("MettreY", "TxtPie", "=", "916")]))

esc = next(l for l in p["layouts"] if l["name"] == "Menu")
esc["objects"] = [o for o in esc["objects"] if o["name"] not in NOM_EQ] + objs
esc["instances"] = [i for i in esc["instances"] if i["name"] not in NOM_EQ] + inst
esc["variables"] = [v for v in esc["variables"] if v["name"] not in {x["name"] for x in vars_}] + vars_
esc["objectsGroups"] = [g for g in esc["objectsGroups"] if g["name"] != "SelEq"] + [{"name": "SelEq", "objects": [{"name": n} for n in NOM_EQ]}]
esc["events"] = esc["events"] + E
p["resources"]["resources"] = list(recursos.values())
json.dump(p, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("OK fase 15: selección de personaje con el diseño del mockup;", len(objs), "objetos,", len(E), "eventos")
