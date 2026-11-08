"""Fase 12 de FDI-Z: mejoras de juego. Correr DESPUÉS de fases_6_a_11.py (con GDevelop cerrado):
    python fase12_mejoras.py <FDI-Z.json> <mapa_fdiz_datos.json> <mapa_fdiz_props.json>
Agrega a la escena Juego:
- Lanzables (balón, engrapadora, libro gordo): se recogen pasando encima; Q o clic derecho / B para lanzar.
- Lockers y mochilas que se revisan (mantener Usar) y máquinas expendedoras que venden con el dinero del equipo.
- Monedas, galletas y jugo; cada zombie tumbado da $2; 1 comida guardada que se come sola bajo 30 % de vida.
- Compañeros mordidos: salvar o no salvar (curarlo cuesta tiempo y vida; si no, se vuelve zombie).
- Números de daño y temblor de cámara.
- Pasivas: Ojo de oferta (Alan), Rutas (César), AirDrop (Gabo).
- Director automático (calma, crecimiento y picos) y zona roja en el minimapa del Jefe.
"""
import json, os, sys, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gd_util import *

ruta, datos_json, props_json = sys.argv[1:4]
p = json.load(open(ruta, encoding="utf-8"))
datos = json.load(open(datos_json, encoding="utf-8"))
props = json.load(open(props_json, encoding="utf-8"))["props"]
esc = next(l for l in p["layouts"] if l["name"] == "Juego")
GEN = "../../generado/sprites/"
EXTRA = "assets/extra/"
random.seed(12)

# ---------------- helpers (los mismos de fases_6_a_11) ----------------
def cmp(e1, op, e2): return c("BuiltinCommonInstructions::CompareNumbers", e1, op, e2)
def cstr(e1, op, e2): return c("BuiltinCommonInstructions::CompareStrings", e1, op, e2)
def vtxt(o, v, val, inv=False): return c("VarObjetTxt", o, v, "=", f"\"{val}\"", invertida=inv)
def vnum(o, v, op, val): return c("VarObjet", o, v, op, str(val))
def setn(o, v, op, val): return a("ModVarObjet", o, v, op, str(val))
def sett(o, v, val): return a("ModVarObjetTxt", o, v, "=", val)
def svar(v, op, val): return a("ModVarScene", v, op, str(val))
def cvar(v, op, val): return c("VarScene", v, op, str(val))
def svt(v, val): return a("ModVarSceneTxt", v, "=", val)
def cvt(v, val, op="="): return c("VarSceneTxt", v, op, val)
def gnum(v, op, val): return c("VarGlobal", v, op, str(val))
def timer_ok(o, t, seg): return c("CompareObjectTimer", o, f"\"{t}\"", ">=", str(seg))
def reset_t(o, t): return a("ResetObjectTimer", o, f"\"{t}\"")
def stimer(t, seg): return c("CompareTimer", "", f"\"{t}\"", ">=", str(seg))
def sreset(t): return a("ResetTimer", "", f"\"{t}\"")
def suelta(k): return c("KeyReleased", "", k)
def once(): return c("BuiltinCommonInstructions::Once")
def o_(*conds): return {"type": {"value": "BuiltinCommonInstructions::Or"}, "parameters": [], "subInstructions": list(conds)}
def foreach(obj, conds, acts, sub=None):
    return {"type": "BuiltinCommonInstructions::ForEach", "object": obj, "conditions": conds, "actions": acts, "events": sub or []}
def crear(obj, x, y, capa="Juego"): return a("Create", "", obj, str(x), str(y), f"\"{capa}\"")
def texto(o, expr): return a("TextObject::String", o, "=", expr)
def anim(o, n): return a("SetAnimationName", o, f"\"{n}\"")
def sonido(nombre, vol=80):
    return ev([gnum("SonidoActivo", "=", 1)], [a("PlaySound", "", f"\"{nombre}\"", "", str(vol), "1")])
def banner(txt, seg=2.5): return [svt("Banner", txt), sreset("banner"), svar("BannerSeg", "=", seg)]
VIVO = vtxt("Sup", "Estado", "normal")
def dist_sup(x, y): return f"DistanceBetweenPositions(Sup.X(), Sup.Y(), {x}, {y})"

recursos = {r["name"]: r for r in p["resources"]["resources"]}
def img(nombre, archivo):
    recursos[nombre] = res_imagen(nombre, archivo)
    return nombre
def gen(rel, org=(16, 32)):   # imagen de generado/sprites
    return (img(rel, GEN + rel), org)

nuevos = []
def sprite(nombre, anims, variables=()):
    o = objeto_sprite(nombre, [animacion(n, [im], 1, False, org) for n, (im, org) in anims], variables)
    nuevos.append(o); return o
def obj_texto(nombre, tam=22, color="255;255;255", alin="center"):
    return {"assetStoreId": "", "name": nombre, "type": "TextObject::Text", "variables": [var("Jugador", 0), var("Vende", 0), var("Listo", 0)],
            "effects": [], "behaviors": [], "content": {"bold": True, "isOutlineEnabled": True, "isShadowEnabled": False,
            "italic": False, "outlineColor": "0;0;0", "outlineThickness": 3, "shadowAngle": 90, "shadowBlurRadius": 2,
            "shadowColor": "0;0;0", "shadowDistance": 4, "shadowOpacity": 127, "smoothed": False, "underlined": False,
            "text": "", "font": "", "textAlignment": alin, "verticalTextAlignment": "top", "characterSize": tam,
            "lineHeight": 0, "color": color}}

# ---------------- objetos ----------------
LANZ = {"balon": (7, 1, -520, 0), "engrapadora": (9, 8, -160, 0), "libro": (24, 1, -260, 1)}   # daño, usos, empujón, aturde (s)
sprite("LanzPiso", [(t, gen(f"objetos/lanzables/{t}.png")) for t in LANZ], [var("Tipo", "")])
sprite("Proyectil", [("balon", gen("objetos/lanzables/balon.png", (16, 16))), ("grapa", gen("objetos/lanzables/grapa.png", (8, 8))),
                     ("libro", gen("objetos/lanzables/libro.png", (16, 16)))],
       [var("Tipo", ""), var("Danio", 0), var("Jugador", 0)])
sprite("Contenedor", [(f"{t}_{e}", gen(f"objetos/contenedores/{t}_{e}.png", (24, 60)))
                      for t in ("locker", "mochila", "maquina") for e in ("cerrado", "abierto")
                      if os.path.basename(f"{t}_{e}") != ""], [var("Tipo", ""), var("Abierto", 0), var("Progreso", 0),
                                                              var("Vende", 0), var("Precio", 0), var("Usada", 0)])
# los PNG de mochila y máquina se llaman *_cerrada / *_abierta
for o in nuevos:
    if o["name"] == "Contenedor":
        for an in o["animations"]:
            f = an["directions"][0]["sprites"][0]["image"]
            if "mochila" in f or "maquina" in f:
                nf = f.replace("_cerrado", "_cerrada").replace("_abierto", "_abierta")
                recursos.pop(f, None); img(nf, GEN + nf); an["directions"][0]["sprites"][0]["image"] = nf
sprite("Moneda", [("moneda", gen("objetos/objetivos/moneda.png", (12, 24)))], [var("Valor", 10)])
sprite("Ruta", [("punto", (img("extra/punto.png", EXTRA + "punto.png"), (32, 32)))])
# zona roja del minimapa del Jefe: un cuadro rojo de 8x8 que se estira (assets/extra/rojo.png lo crea este script)
sprite("ZonaRoja", [("rojo", (img("extra/rojo.png", EXTRA + "rojo.png"), (0, 0)))])
txts = [obj_texto("TxtPrecio", 16, "120;255;140"), obj_texto("TxtMordido", 22, "140;255;120")]
NOMBRES = {o["name"] for o in nuevos + txts}
esc["objects"] = [o for o in esc["objects"] if o["name"] not in NOMBRES] + nuevos + txts

def agregar_vars(obj, vs):
    for o in esc["objects"]:
        if o["name"] == obj:
            for v in vs:
                if not any(x["name"] == v["name"] for x in o["variables"]):
                    o["variables"].append(v)
agregar_vars("Sup", [var("Mordido", 0), var("Cura", 0), var("ComidaCura", 0), var("Lanz", ""), var("LanzUsos", 0),
                     var("QuiereLanzar", 0), var("Init12", 0), var("Ojo", 0), var("Golpeado", 0), var("Curando", 0), var("InvTxt", "")])
for z in ("ZNormal", "ZCorredor", "ZGriton", "ZGordo", "ZConserje", "ZCurado"):
    agregar_vars(z, [var("DineroDado", 0)])
agregar_vars("Niebla", [var("Vista", 0)])
agregar_vars("Comida", [var("Cura", 40)])

VARS = {"AirTipo": "", "AirX": 0, "AirY": 0, "DirFase": "", "DirAfloja": 0, "Temblor": 0, "DirMult": 1, "DirExtra": 0,
        "MordTxt": "", "DbgM": 0, "Comprado": 0, "GuiaSinRuta": 0, "GuiaAlt": 0, "DistBot": 0, "DestX": 0, "DestY": 0, "UltObj": 0}
for k in range(1, 5):
    VARS.update({f"M{k}": 0, f"M{k}Seg": 0, f"Salvo{k}": 0})
esc["variables"] = [v for v in esc["variables"] if v["name"] not in VARS] + [var(n, v) for n, v in VARS.items()]

# ---------------- instancias: lanzables, contenedores y máquinas ----------------
QUITAR = {"LanzPiso", "Contenedor", "Moneda", "TxtPrecio", "TxtMordido", "ZonaRoja"}
esc["instances"] = [i for i in esc["instances"] if i["name"] not in QUITAR]
def de_tipo(nombre): return [x for x in props if x["sprite"].split("/")[-1] == nombre]
def centro(x): return x["x"] + x["w"] // 2, x["y"] + x["h"]
pupitres = de_tipo("pupitre_espalda"); random.shuffle(pupitres)
escritorios = de_tipo("escritorio_profesor") + de_tipo("escritorio_oficina_pc"); random.shuffle(escritorios)
canastas = de_tipo("canasta_basquet") + de_tipo("cancha__canasta_basquet_espejo")
inst = esc["instances"]
for x in pupitres[:7]:
    cx, cy = centro(x); inst.append(instancia("LanzPiso", cx, cy + 34, "Juego", 5, variables=[var("Tipo", "libro")]))
for x in escritorios[:5]:
    cx, cy = centro(x); inst.append(instancia("LanzPiso", cx, cy + 30, "Juego", 5, variables=[var("Tipo", "engrapadora")]))
for x in canastas:
    cx, cy = centro(x)
    for d in (-50, 50):
        inst.append(instancia("LanzPiso", cx + d, cy + 70, "Juego", 5, variables=[var("Tipo", "balon")]))
for x in de_tipo("lockers_cerrados"):
    cx, cy = centro(x); inst.append(instancia("Contenedor", cx, cy + 6, "Juego", 6, variables=[var("Tipo", "locker")]))
for x in pupitres[7:21]:
    cx, cy = centro(x); inst.append(instancia("Contenedor", cx + 20, cy + 40, "Juego", 6, variables=[var("Tipo", "mochila")]))
VENDE = {1: ("comida", 40), 2: ("lanzable", 60), 3: ("arma", 80), 4: ("arma rara", 200)}
for k, x in enumerate(de_tipo("refri_refresco")[:4], 1):
    cx, cy = centro(x)
    inst.append(instancia("Contenedor", cx, cy + 6, "Juego", 6,
                          variables=[var("Tipo", "maquina"), var("Vende", k), var("Precio", VENDE[k][1])]))
    inst.append(instancia("TxtPrecio", cx - 60, cy - 110, "Juego", 50, variables=[var("Vende", k)]))
for k in range(1, 5):
    inst.append(instancia("TxtMordido", 0, 0, "Juego", 60, variables=[var("Jugador", k)]))
inst.append(instancia("ZonaRoja", -100, -100, "HUD", 30))

G = []
# ======================= Lanzables =======================
lz = [comentario("Lanzables: balón (empuja lejos, se recoge otra vez), engrapadora (8 grapas rápidas) y libro gordo (aturde 1 s, se "
                 "recoge otra vez). Se recogen pasando encima si no traes otro. Lanzar: Q o clic derecho (teclado), B (control); "
                 "los bots lanzan cuando tienen 2+ zombies cerca.")]
lz += [
    ev([], [setn("Sup", "QuiereLanzar", "=", 0)]),
    ev([vnum("Sup", "Control", "=", 0), o_(suelta("q"), c("MouseButtonReleased", "", "Right"))], [setn("Sup", "QuiereLanzar", "=", 1)]),
] + [ev([vnum("Sup", "Control", "=", k), c("Gamepads::C_Button_released", "", str(k), "\"B\"", "")], [setn("Sup", "QuiereLanzar", "=", 1)])
     for k in range(1, 5)] + [
    ev([vnum("Sup", "Control", "=", -1), vnum("Sup", "Cerca", ">=", 2), vtxt("Sup", "Lanz", "", inv=True), timer_ok("Sup", "lanz", 1.5)],
       [setn("Sup", "QuiereLanzar", "=", 1)]),
    # recoger
    foreach("Sup", [VIVO, vtxt("Sup", "Lanz", ""), c("CollisionNP", "Sup", "LanzPiso", "", "")], [], sub=[
        ev([], [sett("Sup", "Lanz", "LanzPiso.VariableString(Tipo)")],
           sub=[ev([vtxt("Sup", "Lanz", t)], [setn("Sup", "LanzUsos", "=", u)]) for t, (_, u, _, _) in LANZ.items()]
               + [ev([], [a("Delete", "LanzPiso", "")])])]),
    # lanzar
    foreach("Sup", [VIVO, vnum("Sup", "QuiereLanzar", "=", 1), vtxt("Sup", "Lanz", "", inv=True), timer_ok("Sup", "lanz", 0.25)],
            [reset_t("Sup", "lanz"), crear("Proyectil", "Sup.X()", "Sup.Y() - 40"),
             sett("Proyectil", "Tipo", "Sup.VariableString(Lanz)"), setn("Proyectil", "Jugador", "=", "Sup.Variable(Jugador)"),
             a("AddForceAL", "Proyectil", "ToDeg(atan2(Sup.Variable(AimY), Sup.Variable(AimX)))", "760", "1"),
             reset_t("Proyectil", "vida"), setn("Sup", "LanzUsos", "-", 1)], sub=[
        ev([vtxt("Proyectil", "Tipo", t)], [setn("Proyectil", "Danio", "=", f"{d} * Sup.Variable(Fuerza)"),
                                            anim("Proyectil", "grapa" if t == "engrapadora" else t)])
        for t, (d, _, _, _) in LANZ.items()] + [
        ev([vnum("Sup", "LanzUsos", "<=", 0)], [sett("Sup", "Lanz", "\"\"")]),
        sonido("efectos/combate/lanzar.ogg")]),
    # pegarle a un zombie
    foreach("Proyectil", [], [], sub=[
        ev([vtxt("Zombies", "Estado", "muerto", inv=True), vnum("Zombies", "Aliado", "=", 0),
            cmp("DistanceBetweenPositions(Zombies.X(), Zombies.Y() - 40, Proyectil.X(), Proyectil.Y())", "<", "46"),
            c("PickNearest", "Zombies", "Proyectil.X()", "Proyectil.Y() + 40", "")],
           [setn("Zombies", "Vida", "-", "Proyectil.Variable(Danio)"), a("ChangeColor", "Zombies", "\"255;90;90\""), reset_t("Zombies", "tinte"),
            sett("Zombies", "Estado", "\"persigue\""), setn("Zombies", "UltJugador", "=", "Proyectil.Variable(Jugador)"),
            crear("TxtDanio", "Zombies.X()", "Zombies.Y() - 110"), texto("TxtDanio", "ToString(round(Proyectil.Variable(Danio)))"),
            reset_t("TxtDanio", "vida"), setn("Proyectil", "Pego", "=", 1)], sub=[
            ev([vtxt("Proyectil", "Tipo", t)], [a("AddForceVersPos", "Zombies", "Proyectil.X()", "Proyectil.Y() + 40", str(emp), "0")]
               + ([sett("Zombies", "Estado", "\"aturdido\""), setn("Zombies", "Paralisis", "=", at), reset_t("Zombies", "par"),
                   a("ActivateBehavior", "Zombies", "Pathfinding", "no")] if at else []))
            for t, (_, _, emp, at) in LANZ.items()]),
        ev([c("CollisionNP", "Proyectil", "Solidos", "", "")], [setn("Proyectil", "Pego", "=", 1)]),
        ev([timer_ok("Proyectil", "vida", 0.9)], [setn("Proyectil", "Pego", "=", 1)]),
        ev([vnum("Proyectil", "Pego", "=", 1)], [], sub=[
            ev([vtxt("Proyectil", "Tipo", "engrapadora", inv=True)],
               [crear("LanzPiso", "Proyectil.X()", "Proyectil.Y() + 30"), sett("LanzPiso", "Tipo", "Proyectil.VariableString(Tipo)"),
                a("SetAnimationName", "LanzPiso", "Proyectil.VariableString(Tipo)"), a("SeparateFromObjects", "LanzPiso", "Solidos", "")]),
            ev([], [a("Delete", "Proyectil", "")])]),
    ]),
    ev([c("DepartScene", "")], [a("SetAnimationName", "LanzPiso", "LanzPiso.VariableString(Tipo)")]),
    ev([cvar("Pres", "=", 1), suelta("Num9")], [], sub=[   # F1 + 9: engrapadora para P1
        ev([vnum("Sup", "Jugador", "=", 1)], [sett("Sup", "Lanz", "\"engrapadora\""), setn("Sup", "LanzUsos", "=", 8)])]),
]
agregar_vars("Proyectil", [var("Pego", 0)])
G.append(grupo("Lanzables", lz))

# ======================= Lockers, mochilas, máquinas y dinero =======================
SOLTAR_RANDOM = [  # lo que puede salir de un locker o mochila
    (0.45, [crear("Moneda", "Contenedor.X() + RandomInRange(-20, 20)", "Contenedor.Y() + 40"),
            setn("Moneda", "Valor", "=", "RandomInRange(1, 3) * 10")]),
    (0.65, [crear("Comida", "Contenedor.X() + 24", "Contenedor.Y() + 40"), anim("Comida", "galletas"), setn("Comida", "Cura", "=", 30)]),
    (0.8, [crear("Comida", "Contenedor.X() + 24", "Contenedor.Y() + 40"), anim("Comida", "jugo"), setn("Comida", "Cura", "=", 22)]),
    (1.01, [crear("LanzPiso", "Contenedor.X() + 24", "Contenedor.Y() + 40"), sett("LanzPiso", "Tipo", "\"libro\""), anim("LanzPiso", "libro")]),
]
def soltar_random():
    evs, low = [], 0
    for hi, acts in SOLTAR_RANDOM:
        evs.append(ev([cmp("Variable(R3)", ">=", str(low)), cmp("Variable(R3)", "<", str(hi))], acts)); low = hi
    return [ev([], [svar("R3", "=", "RandomFloat(1)")])] + evs
ARMAS_BASICAS, ARMAS_RARAS = ["escoba", "regla", "silla"], ["bate", "extintor"]
def soltar_arma(lista):
    return [ev([], [svar("R3", "=", f"RandomInRange(0, {len(lista) - 1})")])] + [
        ev([cvar("R3", "=", i)], [crear("ArmaPiso", "Contenedor.X() + 30", "Contenedor.Y() + 50"), sett("ArmaPiso", "Tipo", f"\"{t}\""),
                                  anim("ArmaPiso", t)]) for i, t in enumerate(lista)]
VENDE_ACC = {
    1: [ev([], [crear("Comida", "Contenedor.X() + 30", "Contenedor.Y() + 50"), anim("Comida", "torta"), setn("Comida", "Cura", "=", 40)])],
    2: [ev([], [svar("R3", "=", "RandomInRange(0, 1)")]),
        ev([cvar("R3", "=", 0)], [crear("LanzPiso", "Contenedor.X() + 30", "Contenedor.Y() + 50"), sett("LanzPiso", "Tipo", "\"engrapadora\""), anim("LanzPiso", "engrapadora")]),
        ev([cvar("R3", "=", 1)], [crear("LanzPiso", "Contenedor.X() + 30", "Contenedor.Y() + 50"), sett("LanzPiso", "Tipo", "\"balon\""), anim("LanzPiso", "balon")])],
    3: soltar_arma(ARMAS_BASICAS),
    4: soltar_arma(ARMAS_RARAS),
}
cont = [comentario("Lockers y mochilas: mantener Usar 1 s junto a ellos para revisarlos (monedas, galletas, jugo o un libro). "
                   "Máquinas expendedoras: mantener Usar 1 s para comprar con el dinero del equipo; el precio sale arriba. "
                   "Cada zombie tumbado da $2. Cada quien guarda 1 comida si tiene la vida llena y se la come sola bajo 30 %.")]
cont += [
    ev([c("DepartScene", "")], [a("SetAnimationName", "Contenedor", "Contenedor.VariableString(Tipo) + \"_cerrado\"")]),
    ev([], [setn("Contenedor", "Usada", "=", 0), svar("Comprado", "=", 0)]),
    foreach("Contenedor", [vnum("Contenedor", "Abierto", "=", 0)], [], sub=[
        ev([vnum("Sup", "Usando", "=", 1), VIVO, c("Distance", "Sup", "Contenedor", "95")],
           [setn("Contenedor", "Progreso", "+", "TimeDelta()"), setn("Contenedor", "Usada", "=", 1)], sub=[
            ev([cmp("Contenedor.Variable(Progreso)", ">=", "1"), cvar("Comprado", "=", 0)], [setn("Contenedor", "Progreso", "=", 0), svar("Comprado", "=", 1)], sub=[
                ev([vtxt("Contenedor", "Tipo", "maquina", inv=True)],
                   [setn("Contenedor", "Abierto", "=", 1), a("SetAnimationName", "Contenedor", "Contenedor.VariableString(Tipo) + \"_abierto\"")],
                   sub=soltar_random() + [sonido("efectos/mundo/locker.ogg")]),
                ev([vtxt("Contenedor", "Tipo", "maquina"), cmp("Variable(Dinero)", ">=", "Contenedor.Variable(Precio)")],
                   [svar("Dinero", "-", "Contenedor.Variable(Precio)"), anim("Contenedor", "maquina_abierto"), reset_t("Contenedor", "abierta")],
                   sub=[ev([vnum("Contenedor", "Vende", "=", k)], [], sub=acc) for k, acc in VENDE_ACC.items()]
                       + [sonido("efectos/mundo/maquina.ogg")]),
                ev([vtxt("Contenedor", "Tipo", "maquina"), cmp("Variable(Dinero)", "<", "Contenedor.Variable(Precio)")],
                   banner("\"Les faltan $\" + ToString(ceil(Contenedor.Variable(Precio) - Variable(Dinero))) + \" para comprar\"", 1.5)),
            ])])]),
    ev([vnum("Contenedor", "Usada", "=", 0)], [setn("Contenedor", "Progreso", "=", 0)]),
    ev([vtxt("Contenedor", "Tipo", "maquina"), timer_ok("Contenedor", "abierta", 0.8)], [anim("Contenedor", "maquina_cerrado")]),
    # barra de progreso al revisar
    foreach("Contenedor", [vnum("Contenedor", "Usada", "=", 1)],
            [texto("TxtAyuda", "\"Revisando... \" + ToString(round(100 * Contenedor.Variable(Progreso))) + \"%\""), sreset("ayuda")]),
] + [ev([vnum("TxtPrecio", "Vende", "=", k)], [texto("TxtPrecio", f"\"${pr}\" + NewLine() + \"{n}\"")])
     for k, (n, pr) in VENDE.items()] + [
    foreach("TxtPrecio", [vnum("TxtPrecio", "Listo", "=", 0)], [setn("TxtPrecio", "Listo", "=", 1),
                                                                a("MettreX", "TxtPrecio", "=", "TxtPrecio.X() + 60 - TxtPrecio.Width() / 2")]),
    foreach("Contenedor", [vtxt("Contenedor", "Tipo", "maquina"), vnum("Contenedor", "Usada", "=", 1)],
            [texto("TxtAyuda", "\"Comprando... (hay $\" + ToString(floor(Variable(Dinero))) + \")\""), sreset("ayuda")]),
] + [
    # monedas
    ev([VIVO, c("CollisionNP", "Sup", "Moneda", "", "")], [svar("Dinero", "+", "Moneda.Variable(Valor)"), a("Delete", "Moneda", "")],
       sub=[sonido("efectos/mundo/moneda.ogg")]),
    # $2 por zombie tumbado
    ev([vtxt("Zombies", "Estado", "muerto"), vnum("Zombies", "DineroDado", "=", 0), cvar("Jefe", "=", 0)],
       [svar("Dinero", "+", "2 * PickedInstancesCount(Zombies)"), setn("Zombies", "DineroDado", "=", 1)]),
    # comida guardada
    ev([VIVO, c("CollisionNP", "Sup", "Comida", "", ""), cmp("Sup.Variable(Vida)", ">=", "Sup.Variable(VidaMax)"),
        vnum("Sup", "ComidaCura", "=", 0)], [setn("Sup", "ComidaCura", "=", "Comida.Variable(Cura)"), a("Delete", "Comida", "")]),
    ev([VIVO, vnum("Sup", "ComidaCura", ">", 0), cmp("Sup.Variable(Vida)", "<", "Sup.Variable(VidaMax) * 0.3")],
       [setn("Sup", "Vida", "=", "min(Sup.Variable(VidaMax), Sup.Variable(Vida) + Sup.Variable(ComidaCura))"), setn("Sup", "ComidaCura", "=", 0)],
       sub=[sonido("efectos/movimiento/comer.ogg")]),
]
cont += [  # depuración (F3 visible): T lleva a P1 a la siguiente máquina expendedora
    ev([cvar("VerDebug", "=", 1), suelta("t")], [svar("DbgM", "=", "mod(Variable(DbgM), 4) + 1")], sub=[
        ev([vtxt("Contenedor", "Tipo", "maquina"), vnum("Contenedor", "Vende", "=", "Variable(DbgM)")], [], sub=[
            ev([vnum("Sup", "Jugador", "=", 1)], [a("MettreXY", "Sup", "=", "Contenedor.X()", "=", "Contenedor.Y() + 70"),
                                                 a("CameraX", "", "=", "Contenedor.X()", "", ""), a("CameraY", "", "=", "Contenedor.Y()", "", "")])])]),
]
G.append(grupo("Lockers, mochilas, máquinas y dinero", cont))

# ======================= Compañeros mordidos: salvar o no salvar =======================
MORD_SEG, CURA_SEG, CHANCE = 35, 3, 0.12
mord = [comentario(f"Cada golpe de zombie tiene {int(CHANCE * 100)} % de probabilidad de morder (Tony en Modo gym no). El mordido tiene "
                   f"{MORD_SEG} s: un compañero lo cura manteniendo Usar {CURA_SEG} s junto a él, pero le cuesta su comida guardada o "
                   "20 de vida. Si nadie lo cura, se convierte en zombie y queda fuera hasta el siguiente objetivo. A los profes no los muerden.")]
mord += [
    foreach("Sup", [vnum("Sup", "Golpeado", "=", 1)], [setn("Sup", "Golpeado", "=", 0)], sub=[
        ev([vnum("Sup", "Mordido", "=", 0), VIVO, vtxt("Sup", "Personaje", "tonyfuerte", inv=True), cmp("RandomFloat(1)", "<", str(CHANCE)),
            cvt("Estado", "\"juego\"")],
           [setn("Sup", "Mordido", "=", 1), setn("Sup", "Cura", "=", 0), reset_t("Sup", "mordida")]
           + banner("\"¡P\" + ToString(Sup.Variable(Jugador)) + \" MORDIDO! Cúrenlo: mantener Usar junto a él\"", 2.5),
           sub=[sonido("efectos/combate/mordida.ogg")])]),
    ev([vnum("Sup", "Mordido", "=", 1), timer_ok("Sup", "tinte", 0.5)], [a("ChangeColor", "Sup", "\"150;255;150\"")]),
]
for k in range(1, 5):
    mord += [
        ev([], [svar(f"M{k}", "=", 0)]),
        foreach("Sup", [vnum("Sup", "Jugador", "=", k), vnum("Sup", "Mordido", "=", 1)],
                [svar(f"M{k}", "=", 1), svar(f"M{k}Seg", "=", f"max(0, ceil({MORD_SEG} - Sup.ObjectTimerElapsedTime(\"mordida\")))"),
                 setn("Sup", "Curando", "=", 0)], sub=[
            ev([cvar(f"J{j}Ok", "=", 1), cvar(f"J{j}Usa", "=", 1),
                cmp(dist_sup(f"Variable(J{j}X)", f"Variable(J{j}Y)"), "<", "95")],
               [setn("Sup", "Curando", "=", 1), svar(f"Salvo{j}", "=", 1)]) for j in range(1, 5) if j != k] + [
            ev([vnum("Sup", "Curando", "=", 1)], [setn("Sup", "Cura", "+", "TimeDelta()"),
                                                texto("TxtAyuda", f"\"Curando a P{k}... \" + ToString(round(100 * Sup.Variable(Cura) / {CURA_SEG})) + \"%\""),
                                                sreset("ayuda")]),
            ev([vnum("Sup", "Curando", "=", 0)], [setn("Sup", "Cura", "=", 0)] + [svar(f"Salvo{j}", "=", 0) for j in range(1, 5)]),
            ev([vnum("Sup", "Cura", ">=", CURA_SEG)],
               [setn("Sup", "Mordido", "=", 0), setn("Sup", "Cura", "=", 0), a("ChangeColor", "Sup", "\"255;255;255\"")] + banner(f"\"¡P{k} SALVADO!\"", 2), sub=[
                ev([cvar(f"Salvo{j}", "=", 1)], [svar(f"Salvo{j}", "=", 2)]) for j in range(1, 5)]),
            # no lo salvaron: zombie
            ev([timer_ok("Sup", "mordida", MORD_SEG)],
               [crear("ZNormal", "Sup.X()", "Sup.Y()"), sett("ZNormal", "Estado", "\"persigue\""),
                setn("Sup", "Mordido", "=", 0), sett("Sup", "Estado", "\"fuera\""), a("Cache", "Sup"), sett("Sup", "Arma", "\"puños\""),
                a("ActivateBehavior", "Sup", "TopDownMovement", "no")] + banner(f"\"¡P{k} SE CONVIRTIÓ EN ZOMBIE!\"", 3),
               sub=[sonido("efectos/combate/convertido.ogg")]),
        ]),
        # costo para quien salvó: su comida guardada o 20 de vida
        foreach("Sup", [vnum("Sup", "Jugador", "=", k), cvar(f"Salvo{k}", "=", 2)], [svar(f"Salvo{k}", "=", 0)], sub=[
            ev([vnum("Sup", "ComidaCura", ">", 0)], [setn("Sup", "ComidaCura", "=", 0)]),
            ev([vnum("Sup", "ComidaCura", "=", 0)], [setn("Sup", "Vida", "=", "max(1, Sup.Variable(Vida) - 20)")])]),
        # letrero sobre el mordido
        ev([vnum("TxtMordido", "Jugador", "=", k), cvar(f"M{k}", "=", 1)],
           [a("Montre", "TxtMordido", ""), texto("TxtMordido", f"\"MORDIDO \" + ToString(Variable(M{k}Seg)) + \" s\""),
            a("MettreXY", "TxtMordido", "=", f"Variable(J{k}X) - TxtMordido.Width() / 2", "=", f"Variable(J{k}Y) - 150")]),
        ev([vnum("TxtMordido", "Jugador", "=", k), cvar(f"M{k}", "=", 0)], [a("Cache", "TxtMordido")]),
    ]
mord += [  # atajos del modo presentación (F1)
    ev([cvar("Pres", "=", 1), suelta("Num7")], [], sub=[
        ev([vnum("Sup", "Jugador", "=", 1), VIVO], [setn("Sup", "Mordido", "=", 1), setn("Sup", "Cura", "=", 0), reset_t("Sup", "mordida")]
           + banner("\"¡P1 MORDIDO! Cúrenlo: mantener Usar junto a él\"", 2.5))]),
    ev([cvar("Pres", "=", 1), suelta("Num8")], [svar("Dinero", "+", 200)]),
]
G.append(grupo("Compañeros mordidos: salvar o no salvar", mord))

# bots: van a curar al mordido (va después de "Bots", antes del movimiento)
bots_m = [comentario("Los bots van a curar a un compañero mordido que esté a menos de 600 px.")]
for k in range(1, 5):
    bots_m.append(foreach("Sup", [vnum("Sup", "Control", "=", -1), VIVO, cvar(f"M{k}", "=", 1), vnum("Sup", "Jugador", "!=", k)], [], sub=[
        ev([cmp(dist_sup(f"Variable(J{k}X)", f"Variable(J{k}Y)"), "<", "600")],
           [setn("Sup", "MovX", "=", f"(Variable(J{k}X) - Sup.X()) / max(1, {dist_sup(f'Variable(J{k}X)', f'Variable(J{k}Y)')})"),
            setn("Sup", "MovY", "=", f"(Variable(J{k}Y) - Sup.Y()) / max(1, {dist_sup(f'Variable(J{k}X)', f'Variable(J{k}Y)')})"),
            setn("Sup", "QuierePegar", "=", 0)], sub=[
            ev([cmp(dist_sup(f"Variable(J{k}X)", f"Variable(J{k}Y)"), "<", "70")],
               [setn("Sup", "MovX", "=", 0), setn("Sup", "MovY", "=", 0), setn("Sup", "Usando", "=", 1)])])]))

# ======================= Números de daño y temblor =======================
G.append(grupo("Números de daño", [
    ev([], [a("MettreY", "TxtDanio", "-", "70 * TimeDelta()")]),
    ev([timer_ok("TxtDanio", "vida", 0.75)], [a("Delete", "TxtDanio", "")]),
]))

# ======================= Pasivas: Ojo de oferta, Rutas, AirDrop =======================
pas = [comentario("Alan, Ojo de oferta (cada 30 s): 6 s ve dentro de las zonas oscuras cercanas. César, Rutas (cada 25 s): una línea "
                  "punteada hacia el objetivo, 10 s. Gabo, AirDrop: si pisa un arma que ya trae, se la manda al compañero más "
                  "cercano que pelea a puños.")]
pas += [
    ev([vnum("Sup", "Init12", "=", 0)], [setn("Sup", "Init12", "=", 1), reset_t("Sup", "ojo"), reset_t("Sup", "rutas"), reset_t("Sup", "lanz")]),
    # Ojo de oferta
    foreach("Sup", [vtxt("Sup", "Personaje", "alan"), VIVO, vnum("Sup", "Ojo", "=", 0), timer_ok("Sup", "ojo", 30), cvt("Estado", "\"juego\"")],
            [setn("Sup", "Ojo", "=", 1), reset_t("Sup", "ojo")] + [texto("TxtAyuda", "\"Alan: ¡Ojo de oferta! (ve dentro de lo oscuro)\""), sreset("ayuda")]),
    foreach("Sup", [vtxt("Sup", "Personaje", "alan"), vnum("Sup", "Ojo", "=", 1)], [], sub=[
        ev([vnum("Niebla", "Abierta", "=", 0),
            cmp("DistanceBetweenPositions(Niebla.X() + Niebla.Width() / 2, Niebla.Y() + Niebla.Height() / 2, Sup.X(), Sup.Y())", "<", "900")],
           [a("Opacity", "Niebla", "=", "80"), setn("Niebla", "Vista", "=", 1)]),
        ev([timer_ok("Sup", "ojo", 6)], [setn("Sup", "Ojo", "=", 0), reset_t("Sup", "ojo")], sub=[
            ev([vnum("Niebla", "Vista", "=", 1), vnum("Niebla", "Abierta", "=", 0)], [a("Opacity", "Niebla", "=", "255"), setn("Niebla", "Vista", "=", 0)])])]),
    # Rutas
    foreach("Sup", [vtxt("Sup", "Personaje", "cesar"), VIVO, timer_ok("Sup", "rutas", 25), cvar("ObjX", ">=", 0), cvt("Estado", "\"juego\"")],
            [reset_t("Sup", "rutas"), a("Delete", "Ruta", "")] + [texto("TxtAyuda", "\"César: Rutas (sigan los puntos amarillos)\""), sreset("ayuda")], sub=[
        ev([], [crear("Ruta", f"Sup.X() + (Variable(ObjX) - Sup.X()) * {i / 12:.4f}", f"Sup.Y() + (Variable(ObjY) - Sup.Y()) * {i / 12:.4f}"),
                a("ChangeScale", "Ruta", "=", "0.35"), a("ChangeColor", "Ruta", "\"255;235;90\""), reset_t("Ruta", "vida")])
        for i in range(1, 12)]),
    ev([timer_ok("Ruta", "vida", 10)], [a("Delete", "Ruta", "")]),
    ev([], [a("Opacity", "Ruta", "=", "150 + 100 * sin(TimeFromStart() * 6)")]),
    # AirDrop
    foreach("Sup", [vtxt("Sup", "Personaje", "gabo"), VIVO, vtxt("Sup", "Arma", "puños", inv=True), c("CollisionNP", "Sup", "ArmaPiso", "", ""),
                    cstr("ArmaPiso.VariableString(Tipo)", "=", "Sup.VariableString(Arma)"), cvt("AirTipo", "\"\"")],
            [svt("AirTipo", "ArmaPiso.VariableString(Tipo)"), svar("AirX", "=", "Sup.X()"), svar("AirY", "=", "Sup.Y()"), a("Delete", "ArmaPiso", "")]),
    ev([cvt("AirTipo", "\"\"", "!="), VIVO, vtxt("Sup", "Arma", "puños"), vtxt("Sup", "Personaje", "gabo", inv=True),
        c("PickNearest", "Sup", "Variable(AirX)", "Variable(AirY)", "")],
       [sett("Sup", "Arma", "VariableString(AirTipo)"), setn("Sup", "Usos", "=", 24), svt("AirTipo", "\"\"")]
       + [texto("TxtAyuda", "\"Gabo: AirDrop a P\" + ToString(Sup.Variable(Jugador))"), sreset("ayuda")]),
    ev([cvt("AirTipo", "\"\"", "!=")], [crear("ArmaPiso", "Variable(AirX) + 70", "Variable(AirY)"), sett("ArmaPiso", "Tipo", "VariableString(AirTipo)"),
                                         a("SetAnimationName", "ArmaPiso", "VariableString(AirTipo)"), svt("AirTipo", "\"\"")]),
]
G.append(grupo("Pasivas: Ojo de oferta, Rutas y AirDrop", pas))

# efectos de habilidad (los crea H() en fases_6_a_11): siguen al personaje 1.2 s
ef = [ev([timer_ok("EfectoPj", "vida", 1.2)], [a("Delete", "EfectoPj", "")])]
for k in range(1, 5):
    ef.append(ev([vnum("EfectoPj", "Jugador", "=", k)], [a("MettreXY", "EfectoPj", "=", f"Variable(J{k}X)", "=", f"Variable(J{k}Y) - 50")]))
G.append(grupo("Efectos de habilidad", ef))

# inventario en el panel (lo lee el HUD) y textos ocultos durante la cinemática
G.append(grupo("Inventario en el panel", [
    ev([], [sett("Sup", "InvTxt", "\"\"")]),
    ev([vtxt("Sup", "Lanz", "", inv=True)], [sett("Sup", "InvTxt", "\"  +  \" + Sup.VariableString(Lanz) + \" x\" + ToString(Sup.Variable(LanzUsos))")]),
    ev([vnum("Sup", "ComidaCura", ">", 0)], [sett("Sup", "InvTxt", "Sup.VariableString(InvTxt) + \"  +  comida\"")]),
    ev([vnum("Sup", "Mordido", "=", 1)], [sett("Sup", "InvTxt", "Sup.VariableString(InvTxt) + \"  MORDIDO\"")]),
    ev([cvt("Estado", "\"intro\"")], [a("Cache", "TxtObjetivo"), a("Cache", "Flecha")]),
    # Modo gym: Tony no puede ser tumbado
    ev([vtxt("Sup", "Personaje", "tonyfuerte"), cmp("Sup.Variable(Vida)", "<", "1")], [setn("Sup", "Vida", "=", 1)]),
    ev([cvt("Estado", "\"intro\"", "!=")], [a("Montre", "TxtObjetivo", "")]),
]))

# ======================= Guía de los bots (cuando no hay humanos) =======================
B01 = next(z for z in datos["zonas"] if z["nombre"] == "B-01")
GX, GY = B01["x"] + B01["w"] // 2, B01["y"] + B01["h"] // 2
pf = {"name": "Pathfinding", "type": "PathfindingBehavior::PathfindingBehavior", "allowDiagonals": True, "acceleration": 900,
      "maxSpeed": 160, "angularMaxSpeed": 180, "rotateObject": False, "angleOffset": 0, "cellWidth": 32, "cellHeight": 32,
      "extraBorder": 0, "gridOffsetX": 0, "gridOffsetY": 0, "smoothingMaxCellGap": 1}
guia = objeto_sprite("Guia", [animacion("punto", [img("extra/punto.png", EXTRA + "punto.png")], 1, False, (32, 32))], [], [pf])
esc["objects"] = [o for o in esc["objects"] if o["name"] != "Guia"] + [guia]
# las puertas cerradas ya no son obstáculo de Pathfinding: zombies y guía planean a través de ellas; el guía espera a que
# los bots la abran y los zombies la tumban a golpes ("Puertas: tipos y golpes")
for o in esc["objects"]:
    if o["name"] == "Puerta":
        o["behaviors"] = [b for b in o["behaviors"] if b.get("type") != "PathfindingBehavior::PathfindingObstacleBehavior"]
PB = next(p_ for p_ in datos["puertas"] if "B-01" in p_["zonas"])
GX, GY = PB["x"] - 70, PB["y"] + PB["h"] // 2   # en el pasillo, frente a la puerta del salón inicial
esc["instances"] = [i for i in esc["instances"] if i["name"] != "Guia"] + [instancia("Guia", GX, GY, "Juego", 1)]
# puntos de acceso libres junto a cada lugar de objetivo (muchos objetivos están sobre un mueble o pegados a la pared)
RECTS = [(r["x"], r["y"], r["w"], r["h"]) for r in datos["colisiones"]] + \
        [(x["colision"]["x"], x["colision"]["y"], x["colision"]["w"], x["colision"]["h"]) for x in props if x.get("colision")]
def libre(x, y, m=22):
    return not any(rx - m <= x < rx + rw + m and ry - m <= y < ry + rh + m for rx, ry, rw, rh in RECTS)
def acceso(x, y):
    if libre(x, y): return x, y
    best = None
    for r in range(16, 200, 16):
        for k in range(16):
            import math
            ax, ay = x + r * math.cos(k * math.pi / 8), y + r * math.sin(k * math.pi / 8)
            if libre(ax, ay):
                return round(ax), round(ay)
    return x, y
Mk = datos["marcadores"]
lugares = [Mk["servidor_site"], Mk["llaves_conserjeria"], Mk["carnada_neveria"], Mk["interruptor_principal"], Mk["interruptor_luz_lab"],
           Mk["camion"], {"x": Mk["computadoras_llamada"][0]["x"], "y": Mk["computadoras_llamada"][0]["y"]},
           {"x": Mk["computadoras_llamada"][1]["x"] + 40, "y": Mk["computadoras_llamada"][1]["y"]}] + \
          list(Mk["bidones_posibles"]) + list(Mk["bolsa_comida_posible"])
esc["instances"] = [i for i in esc["instances"] if not (i["name"] == "Marcador" and any(v.get("value") == "acceso" for v in i["initialVariables"]))]
for L_ in lugares:
    ax, ay = acceso(L_["x"], L_["y"])
    esc["instances"].append(instancia("Marcador", ax, ay, "Juego", 0, variables=[var("Tipo", "acceso")]))
guia_ev = [comentario("Si no hay ningún humano de pie (demo del título, o Jefe sin controles), los bots siguen a un guía invisible que va "
                      "con Pathfinding al objetivo (o a la puerta cerrada más cercana si no hay camino) y espera a que lo alcancen. "
                      "Con humanos, los bots siguen al grupo como siempre."),
    ev([c("DepartScene", "")], [a("Cache", "Guia"), a("ChangeScale", "Guia", "=", "0.3"), sreset("guia"), sreset("guiaespera"), sreset("objdemo")]),
    ev([cvar("VerDebug", "=", 1)], [a("Montre", "Guia", ""), a("TextObject::String", "TxtDebug", "=",
        "TxtDebug.String() + NewLine() + \"obj \" + VariableString(ObjTipo) + \" paso \" + ToString(Variable(Paso)) + \" en \" + "
        "ToString(round(Variable(ObjX))) + \",\" + ToString(round(Variable(ObjY))) + \"  guía \" + ToString(round(Guia.X())) + \",\" + "
        "ToString(round(Guia.Y())) + \" sin ruta \" + ToString(Variable(GuiaSinRuta)) + \" alt \" + ToString(Variable(GuiaAlt)) + "
        "\" botmin \" + ToString(round(Variable(DistBot)))")]), ev([cvar("VerDebug", "=", 0)], [a("Cache", "Guia")]),
    # depuración: B convierte a P1 en bot (y otra vez en teclado)
    ev([cvar("VerDebug", "=", 1), suelta("b")], [], sub=[
        ev([vnum("Sup", "Jugador", "=", 1), vnum("Sup", "Control", "=", 0)], [setn("Sup", "Control", "=", 9)]),
        ev([vnum("Sup", "Jugador", "=", 1), vnum("Sup", "Control", "=", -1)], [setn("Sup", "Control", "=", 0)]),
        ev([vnum("Sup", "Jugador", "=", 1), vnum("Sup", "Control", "=", 9)], [setn("Sup", "Control", "=", -1)])]),
    ev([], [svar("SegX", "=", "Variable(CamX)"), svar("SegY", "=", "Variable(CamY)")]),
    ev([cvar("Humanos", "=", 0), cvt("Estado", "\"juego\"")], [svar("SegX", "=", "Guia.X()"), svar("SegY", "=", "Guia.Y()"),
                                                             svar("DistBot", "=", 99999)], sub=[
        # el guía avanza mientras el bot más cercano lo alcance; los rezagados (más de 450 px) aparecen junto a él
        foreach("Sup", [VIVO], [svar("DistBot", "=", "min(Variable(DistBot), DistanceBetweenPositions(Sup.X(), Sup.Y(), Guia.X(), Guia.Y()))")], sub=[
            ev([cmp("DistanceBetweenPositions(Sup.X(), Sup.Y(), Guia.X(), Guia.Y())", ">", "450")],
               [a("MettreXY", "Sup", "=", "Guia.X() + RandomInRange(-20, 20)", "=", "Guia.Y() + RandomInRange(-20, 20)")])]),
        ev([cvar("DistBot", "<", "75")], [a("PathfindingBehavior::MaxSpeed", "Guia", "Pathfinding", "=", "150"), sreset("guiaespera")]),
        ev([cvar("DistBot", ">=", "75")], [a("PathfindingBehavior::MaxSpeed", "Guia", "Pathfinding", "=", "0")]),
        # si nadie lo alcanza en 2.5 s (un bot se atoró en una esquina), el guía regresa junto al bot más cercano
        ev([cvar("DistBot", ">=", "75"), stimer("guiaespera", 2.5), VIVO, c("PickNearest", "Sup", "Guia.X()", "Guia.Y()", "")],
           [a("MettreXY", "Guia", "=", "Sup.X()", "=", "Sup.Y()"), sreset("guiaespera"), sreset("guia")]),
        ev([cmp("DistanceBetweenPositions(Guia.X(), Guia.Y(), Variable(CamX), Variable(CamY))", ">", "900")],
           [a("MettreXY", "Guia", "=", "Variable(CamX)", "=", "Variable(CamY)")]),
        ev([stimer("guia", 1), cvar("ObjX", ">=", 0)], [sreset("guia"), svar("DestX", "=", "Variable(ObjX)"), svar("DestY", "=", "Variable(ObjY)")], sub=[
            ev([vtxt("Marcador", "Tipo", "acceso"), c("PickNearest", "Marcador", "Variable(ObjX)", "Variable(ObjY)", "")], [], sub=[
                ev([cmp("DistanceBetweenPositions(Marcador.X(), Marcador.Y(), Variable(ObjX), Variable(ObjY))", "<", "220")],
                   [svar("DestX", "=", "Marcador.X()"), svar("DestY", "=", "Marcador.Y()")])]),
            ev([], [a("PathfindingBehavior::SetDestination", "Guia", "Pathfinding", "", "Variable(DestX)", "Variable(DestY)")]),
            ev([c("PathfindingBehavior::PathFound", "Guia", "Pathfinding", invertida=True)],
               [a("PathfindingBehavior::SetDestination", "Guia", "Pathfinding", "", "Variable(ObjX) + 40", "Variable(ObjY) + 0")]),
            ev([c("PathfindingBehavior::PathFound", "Guia", "Pathfinding", invertida=True)],
               [a("PathfindingBehavior::SetDestination", "Guia", "Pathfinding", "", "Variable(ObjX) - 40", "Variable(ObjY) + 0")]),
            ev([c("PathfindingBehavior::PathFound", "Guia", "Pathfinding", invertida=True)],
               [a("PathfindingBehavior::SetDestination", "Guia", "Pathfinding", "", "Variable(ObjX) + 0", "Variable(ObjY) + 40")]),
            ev([c("PathfindingBehavior::PathFound", "Guia", "Pathfinding", invertida=True)],
               [a("PathfindingBehavior::SetDestination", "Guia", "Pathfinding", "", "Variable(ObjX) + 0", "Variable(ObjY) - 40")]),
            ev([c("PathfindingBehavior::PathFound", "Guia", "Pathfinding", invertida=True)],
               [a("PathfindingBehavior::SetDestination", "Guia", "Pathfinding", "", "Variable(ObjX) + 40", "Variable(ObjY) + 40")]),
            ev([c("PathfindingBehavior::PathFound", "Guia", "Pathfinding", invertida=True)],
               [a("PathfindingBehavior::SetDestination", "Guia", "Pathfinding", "", "Variable(ObjX) - 40", "Variable(ObjY) + 40")]),
            ev([c("PathfindingBehavior::PathFound", "Guia", "Pathfinding", invertida=True)],
               [a("PathfindingBehavior::SetDestination", "Guia", "Pathfinding", "", "Variable(ObjX) + 40", "Variable(ObjY) - 40")]),
            ev([c("PathfindingBehavior::PathFound", "Guia", "Pathfinding", invertida=True)],
               [a("PathfindingBehavior::SetDestination", "Guia", "Pathfinding", "", "Variable(ObjX) - 40", "Variable(ObjY) - 40")]),
            ev([c("PathfindingBehavior::PathFound", "Guia", "Pathfinding", invertida=True)],
               [a("PathfindingBehavior::SetDestination", "Guia", "Pathfinding", "", "Variable(ObjX) + 72", "Variable(ObjY) + 0")]),
            ev([c("PathfindingBehavior::PathFound", "Guia", "Pathfinding", invertida=True)],
               [a("PathfindingBehavior::SetDestination", "Guia", "Pathfinding", "", "Variable(ObjX) - 72", "Variable(ObjY) + 0")]),
            ev([c("PathfindingBehavior::PathFound", "Guia", "Pathfinding", invertida=True)],
               [a("PathfindingBehavior::SetDestination", "Guia", "Pathfinding", "", "Variable(ObjX) + 0", "Variable(ObjY) + 72")]),
            ev([c("PathfindingBehavior::PathFound", "Guia", "Pathfinding", invertida=True)],
               [a("PathfindingBehavior::SetDestination", "Guia", "Pathfinding", "", "Variable(ObjX) + 0", "Variable(ObjY) - 72")]),
            # (el objetivo suele estar sobre un mueble: se prueban puntos alrededor)
            ev([c("PathfindingBehavior::PathFound", "Guia", "Pathfinding", invertida=True)], [svar("GuiaSinRuta", "+", 1)]),
            ev([c("PathfindingBehavior::PathFound", "Guia", "Pathfinding")], [svar("GuiaSinRuta", "=", 0)]),
            # atorado dentro de un mueble: se mueve un poco al azar
            ev([cvar("GuiaSinRuta", ">=", 3)], [svar("GuiaSinRuta", "=", 0),
                a("MettreXY", "Guia", "=", "Guia.X() + RandomInRange(-2, 2) * 32", "=", "Guia.Y() + RandomInRange(-2, 2) * 32")]),
            # sin camino: prueba la puerta más cercana al objetivo y, si tampoco hay camino, la más cercana al guía
            ev([c("PathfindingBehavior::PathFound", "Guia", "Pathfinding", invertida=True), cvar("GuiaAlt", "=", 0),
                c("PickNearest", "Puerta", "Variable(ObjX)", "Variable(ObjY)", "")],
               [svar("R3", "=", "max(1, DistanceBetweenPositions(Guia.X(), Guia.Y(), Puerta.X() + Puerta.Width() / 2, Puerta.Y() + Puerta.Height() / 2))"),
                a("PathfindingBehavior::SetDestination", "Guia", "Pathfinding", "",
                  "Puerta.X() + Puerta.Width() / 2 + (Guia.X() - Puerta.X() - Puerta.Width() / 2) / Variable(R3) * 70",
                  "Puerta.Y() + Puerta.Height() / 2 + (Guia.Y() - Puerta.Y() - Puerta.Height() / 2) / Variable(R3) * 70")]),
            ev([c("PathfindingBehavior::PathFound", "Guia", "Pathfinding", invertida=True), cvar("GuiaAlt", "=", 1),
                c("PickNearest", "Puerta", "Guia.X()", "Guia.Y()", "")],
               [svar("R3", "=", "max(1, DistanceBetweenPositions(Guia.X(), Guia.Y(), Puerta.X() + Puerta.Width() / 2, Puerta.Y() + Puerta.Height() / 2))"),
                a("PathfindingBehavior::SetDestination", "Guia", "Pathfinding", "",
                  "Puerta.X() + Puerta.Width() / 2 + (Guia.X() - Puerta.X() - Puerta.Width() / 2) / Variable(R3) * 70",
                  "Puerta.Y() + Puerta.Height() / 2 + (Guia.Y() - Puerta.Y() - Puerta.Height() / 2) / Variable(R3) * 70")]),
            ev([c("PathfindingBehavior::PathFound", "Guia", "Pathfinding", invertida=True)], [svar("GuiaAlt", "=", "1 - Variable(GuiaAlt)")]),
        ]),
    ]),
]
# demo del título: si los bots tardan más de 80 s en un objetivo, se da por cumplido para que la demo siga avanzando
guia_ev += [
    ev([c("BuiltinCommonInstructions::CompareNumbers", "Variable(ObjNum)", "!=", "Variable(UltObj)")], [svar("UltObj", "=", "Variable(ObjNum)"), sreset("objdemo")]),
    ev([gnum("Demo", "=", 1), stimer("partida", 240)], [a("ModVarGlobal", "Demo", "=", "0"), a("Scene", "", "\"Titulo\"", "")]),
    ev([gnum("Demo", "=", 1)], [texto("TxtAyuda", "\"DEMOSTRACIÓN · presiona Enter, A o haz clic para jugar\""), sreset("ayuda")]),
    ev([gnum("Demo", "=", 1), cvar("Humanos", "=", 0), stimer("objdemo", 80), cvar("ObjNum", "<", 4)],
       [sreset("objdemo"), svar("Paso", "=", 99), a("Delete", "Objetivo", ""), a("Delete", "Bidon", ""), a("Delete", "Bolsa", ""), svar("Apagon", "=", 0)]),
]
# bots: usar objetivos, recoger bidones/bolsas y abrir puertas (va después de "Bots")
def ir_a(obj, radio):
    d = f"Sup.Distance({obj})"
    return ev([cmp(d, "<", str(radio))], [setn("Sup", "MovX", "=", f"({obj}.X() - Sup.X()) / max(1, {d})"),
                                           setn("Sup", "MovY", "=", f"({obj}.Y() - Sup.Y()) / max(1, {d})")])
bots_obj = [comentario("Bots: se acercan a bidones y bolsas cercanos, mantienen Usar junto al objetivo y junto a una puerta cerrada "
                       "en su camino (y le pegan si no abre).")]
bots_obj += [
    foreach("Sup", [vnum("Sup", "Control", "=", -1), VIVO], [], sub=[
        # sin humanos: seguir de cerca al guía (correa corta para doblar esquinas)
        ev([cvar("Humanos", "=", 0), cvt("Estado", "\"juego\""), cmp(f"DistanceBetweenPositions(Sup.X(), Sup.Y(), Guia.X(), Guia.Y())", ">", "30")],
           [setn("Sup", "MovX", "=", "(Guia.X() - Sup.X()) / max(1, DistanceBetweenPositions(Sup.X(), Sup.Y(), Guia.X(), Guia.Y()))"),
            setn("Sup", "MovY", "=", "(Guia.Y() - Sup.Y()) / max(1, DistanceBetweenPositions(Sup.X(), Sup.Y(), Guia.X(), Guia.Y()))")]),
        ev([c("PickNearest", "Bidon", "Sup.X()", "Sup.Y()", "")], [], sub=[ir_a("Bidon", 110)]),
        ev([c("PickNearest", "Bolsa", "Sup.X()", "Sup.Y()", "")], [], sub=[ir_a("Bolsa", 110)]),
        ev([vnum("Objetivo", "Hecho", "=", 0), c("PickNearest", "Objetivo", "Sup.X()", "Sup.Y()", "")], [], sub=[
            ir_a("Objetivo", 140),
            ev([cmp("Sup.Distance(Objetivo)", "<", "130")], [setn("Sup", "MovX", "=", 0), setn("Sup", "MovY", "=", 0),
                                                            setn("Sup", "Usando", "=", 1), setn("Sup", "QuierePegar", "=", 0)])]),
        ev([cvar("Humanos", "=", 0), c("PickNearest", "Puerta", "Sup.X()", "Sup.Y()", "")], [], sub=[
            ev([cmp("DistanceBetweenPositions(Sup.X(), Sup.Y(), Puerta.X() + Puerta.Width() / 2, Puerta.Y() + Puerta.Height() / 2)", "<", "120"),
                cmp("DistanceBetweenPositions(Guia.X(), Guia.Y(), Puerta.X() + Puerta.Width() / 2, Puerta.Y() + Puerta.Height() / 2)", "<", "200")],
               [setn("Sup", "Usando", "=", 1), setn("Sup", "AimX", "=", "Puerta.X() + Puerta.Width() / 2 - Sup.X()"),
                setn("Sup", "AimY", "=", "Puerta.Y() + Puerta.Height() / 2 - Sup.Y()")], sub=[
                ev([o_(vnum("Puerta", "TiempoAbrir", ">", 2), vnum("Puerta", "TiempoAbrir", "<=", 0))], [setn("Sup", "QuierePegar", "=", 1)])])]),
    ]),
]

# ======================= Director automático =======================
direc = [comentario("Modo Escape: ciclo de 60 s. Calma (18 s, casi no salen zombies), crecimiento y pico (últimos 15 s: salen "
                    "más rápido y 6 extra). Afloja si alguien está caído o mordido, o si el equipo tiene poca vida. "
                    "No toca el final ni el modo Jefe.")]
direc += [
    ev([c("DepartScene", "")], [sreset("director")]),
    ev([stimer("director", 60)], [sreset("director")]),
    ev([], [svar("DirAfloja", "=", 0)]),
    ev([o_(vtxt("Sup", "Estado", "caido"), vnum("Sup", "Mordido", "=", 1))], [svar("DirAfloja", "=", 1)]),
    ev([VIVO, cmp("Sup.Variable(Vida)", "<", "Sup.Variable(VidaMax) * 0.35")], [svar("DirAfloja", "=", 1)]),
    ev([c("CompareTimer", "", "\"director\"", "<", "18")], [svt("DirFase", "\"calma\""), svar("DirMult", "=", 4), svar("DirExtra", "=", -4)]),
    ev([c("CompareTimer", "", "\"director\"", ">=", "18"), c("CompareTimer", "", "\"director\"", "<", "45")],
       [svt("DirFase", "\"crece\""), svar("DirMult", "=", 1), svar("DirExtra", "=", 0)]),
    ev([stimer("director", 45)], [svt("DirFase", "\"pico\""), svar("DirMult", "=", 0.45), svar("DirExtra", "=", 6)]),
    ev([cvar("DirAfloja", "=", 1)], [svar("DirMult", "=", "max(Variable(DirMult), 2)"), svar("DirExtra", "=", "min(Variable(DirExtra), -2)")]),
    ev([o_(cvar("FinalActivo", "=", 1), cvar("Jefe", "=", 1))], [svar("DirMult", "=", 1), svar("DirExtra", "=", 0)]),
]
G.append(grupo("Director automático", direc))

# ======================= Zona roja del minimapa (Jefe) =======================
MMX, MMY, MMW, MMH = 1920 - 668, 1080 - 418, 640, 392
SX, SY = datos["ancho_px"] / MMW, datos["alto_px"] / MMH
G.append(grupo("Zona roja del minimapa", [
    comentario("Lo que ven los sobrevivientes se pinta en rojo en el minimapa del Jefe (ahí no puede poner zombies)."),
    ev([cvar("Jefe", "=", 0)], [a("Cache", "ZonaRoja")]),
    ev([cvar("Jefe", "=", 1)], [a("Montre", "ZonaRoja", ""), a("Opacity", "ZonaRoja", "=", "110"),
        a("MettreXY", "ZonaRoja", "=", f"{MMX} + max(0, CameraX() - 1000 / CameraZoom()) / {SX:.4f}",
          "=", f"{MMY} + max(0, CameraY() - 600 / CameraZoom()) / {SY:.4f}"),
        a("ChangeWidth", "ZonaRoja", "=", f"2000 / CameraZoom() / {SX:.4f}"), a("ChangeHeight", "ZonaRoja", "=", f"1200 / CameraZoom() / {SY:.4f}")]),
]))

# ======================= Temblor (después de la cámara) =======================
temblor = grupo("Temblor de cámara", [
    ev([cvar("Temblor", ">", 0)], [svar("Temblor", "-", "TimeDelta()"),
                                    a("CameraX", "", "+", "RandomInRange(-5, 5)", "", ""), a("CameraY", "", "+", "RandomInRange(-4, 4)", "", "")]),
])

# ---------------- insertar en los eventos ----------------
EV = esc["events"]
NOM = {g["name"] for g in G} | {"Bots: curar mordidos", "Temblor de cámara", "Guía de los bots", "Bots: objetivos y puertas"}
EV[:] = [e for e in EV if e.get("name") not in NOM]
i_cam = next(k for k, e in enumerate(EV) if e.get("name") == "Cámara compartida")
EV[i_cam:i_cam] = G
i_bots = next(k for k, e in enumerate(EV) if e.get("name") == "Bots")
EV.insert(i_bots, grupo("Guía de los bots", guia_ev))
EV.insert(i_bots + 2, grupo("Bots: objetivos y puertas", bots_obj))
EV.insert(i_bots + 3, grupo("Bots: curar mordidos", bots_m))
EV.append(temblor)

# temporizador "director" y otros que se comparan antes de iniciarse
p["resources"]["resources"] = list(recursos.values())
json.dump(p, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("OK fase 12:", len(G) + 2, "grupos;", sum(1 for i in esc["instances"] if i["name"] in QUITAR), "instancias nuevas")
