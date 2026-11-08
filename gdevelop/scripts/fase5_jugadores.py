"""Fase 5: de 1 a 4 jugadores locales (teclado+ratón y controles de Xbox), bots, cámara compartida y revivir.
Reemplaza a "Tony" por el objeto "Sup" (un superviviente por instancia, con las animaciones de los
8 personajes nombradas <personaje>_<animación>) y REGENERA todos los eventos de la escena Juego
(incluye la lógica de las fases 2, 3 y 4 adaptada a varios jugadores).
Uso: python fase5_jugadores.py <FDI-Z.json> <atlas.json> <mapa_fdiz_datos.json> <Gamepads.json>
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gd_util import *

ruta, atlas_json, datos_json, gamepads_json = sys.argv[1:5]
p = json.load(open(ruta, encoding="utf-8"))
atlas = json.load(open(atlas_json, encoding="utf-8"))
datos = json.load(open(datos_json, encoding="utf-8"))
esc = next(l for l in p["layouts"] if l["name"] == "Juego")
GEN = "../../generado/sprites/"

# ---------- extensión Gamepads (repositorio oficial de extensiones de GDevelop) ----------
ext = json.load(open(gamepads_json, encoding="utf-8"))
p["eventsFunctionsExtensions"] = [e for e in p["eventsFunctionsExtensions"] if e["name"] != "Gamepads"] + [ext]

# ---------- objeto Sup ----------
PERSONAJES = {  # vida, velocidad (px/s, ×3), fuerza
    "tony": (120, 204, 1.3), "miranda": (95, 228, 1.0), "cesar": (95, 222, 0.9), "alan": (95, 228, 0.95),
    "castillo": (110, 210, 1.1), "alessandro": (100, 216, 1.0), "gabo": (90, 246, 0.9), "carlos": (140, 192, 1.1)}
recursos = {r["name"]: r for r in p["resources"]["resources"]}
anims = []
for pj in list(PERSONAJES) + ["tonyfuerte"]:
    e = atlas["entidades"][f"personajes/{pj}"]
    w, h = e["lienzo"]
    o = (w // 2, h - 2)
    m = (o[0] - 14, o[1] - 16, o[0] + 14, o[1])
    for n, an in e["animaciones"].items():
        imgs = []
        for f in an["cuadros"]:
            recursos[f] = res_imagen(f, GEN + f)
            imgs.append(f)
        anims.append(animacion(f"{pj}_{n}", imgs, an["fps"], an["loop"], o, m))
p["resources"]["resources"] = list(recursos.values())
topdown = {"name": "TopDownMovement", "type": "TopDownMovementBehavior::TopDownMovementBehavior",
           "acceleration": 1600, "allowDiagonals": True, "angleOffset": 0, "angularMaxSpeed": 180,
           "customIsometryAngle": 30, "deceleration": 1800, "ignoreDefaultControls": True, "maxSpeed": 204,
           "movementAngleOffset": 0, "rotateObject": False, "useLegacyTurnBack": False, "viewpoint": "TopDown"}
VARS_SUP = [var("Personaje", "tony"), var("Jugador", 1), var("Control", 0), var("Init", 0),
            var("Vida", 120), var("VidaMax", 120), var("Velocidad", 204), var("Fuerza", 1.3),
            var("Estado", "normal"), var("Arma", "puños"), var("Usos", 0), var("DanioArma", 7),
            var("Alcance", 1.0), var("Cadencia", 0.35), var("Atacando", 0), var("AimX", 0), var("AimY", 1),
            var("QuierePegar", 0), var("Usando", 0), var("Revivir", 0), var("MovX", 0), var("MovY", 0), var("UltX", 0), var("UltY", 0), var("Ayuda", 0), var("ResDanio", 1), var("Kills", 0), var("Golpeado", 0), var("HabCD", 15), var("EspCD", 50), var("PideHab", 0), var("PideEsp", 0), var("Rapidez", 1)]
sup = objeto_sprite("Sup", anims, variables=VARS_SUP, comportamientos=[topdown])
esc["objects"] = [o for o in esc["objects"] if o["name"] not in ("Tony", "Sup")]
i_obj = next(k for k, o in enumerate(esc["objects"]) if o["name"] == "Mapa")
esc["objects"].insert(i_obj, sup)
# números de daño (los usa "Combate: pegar"; los mueve y borra fase12_mejoras.py)
txt_danio = {"assetStoreId": "", "name": "TxtDanio", "type": "TextObject::Text", "variables": [], "effects": [], "behaviors": [],
             "content": {"bold": True, "isOutlineEnabled": True, "isShadowEnabled": False, "italic": False, "outlineColor": "0;0;0",
                         "outlineThickness": 3, "shadowAngle": 90, "shadowBlurRadius": 2, "shadowColor": "0;0;0", "shadowDistance": 4,
                         "shadowOpacity": 127, "smoothed": False, "underlined": False, "text": "", "font": "", "textAlignment": "center",
                         "verticalTextAlignment": "top", "characterSize": 26, "lineHeight": 0, "color": "255;240;120"}}
esc["objects"] = [o for o in esc["objects"] if o["name"] != "TxtDanio"] + [txt_danio]
p["resources"]["resources"] = [r for r in p["resources"]["resources"]
                               if not (r["name"].startswith("personajes/tony/") and r["file"].startswith("assets/"))]
p["resources"]["resources"] = list({r["name"]: r for r in p["resources"]["resources"]}.values())
for r in recursos.values():
    if r["name"] not in {x["name"] for x in p["resources"]["resources"]}:
        p["resources"]["resources"].append(r)

# ---------- instancias: 4 supervivientes en el punto de inicio ----------
ini = datos["marcadores"]["aparicion_jugadores"]
EQUIPO = [("tony", 0), ("miranda", -1), ("cesar", -1), ("alan", -1)]   # Control: 0 teclado, 1-4 control, -1 bot
esc["instances"] = [i for i in esc["instances"] if i["name"] not in ("Tony", "Sup")]
for k, (pj, ctl) in enumerate(EQUIPO):
    esc["instances"].append(instancia("Sup", ini[k]["x"], ini[k]["y"], "Juego", int(ini[k]["y"]),
        variables=[var("Personaje", pj), var("Jugador", k + 1), var("Control", ctl)]))

NV = ["VerDebug", "SegX", "SegY", "DirMult", "DirExtra", "Temblor", "SpawnCada", "ExtraZombies", "Infestacion", "ObjZombies", "MaxTipo", "R", "R2", "Tumbados", "OroJefe", "Piloto", "Estado",
      "CamX", "CamY", "CamMinX", "CamMaxX", "CamMinY", "CamMaxY", "CamN", "CamZoom", "Vivos", "Humanos"]
for k in range(1, 5):
    NV += [f"J{k}X", f"J{k}Y", f"J{k}Ok", f"J{k}Usa"]
for k in range(1, 5):
    NV += [f"Pad{k}"]
esc["variables"] = [v for v in esc["variables"] if v["name"] not in NV + ["DbgDist", "DbgAng"]]
for n in NV:
    esc["variables"].append(var(n, "" if n in ("Piloto", "Estado") else 0))
esc["variables"] = [v if v["name"] != "Estado" else var("Estado", "juego") for v in esc["variables"]]
esc["variables"] = [v if v["name"] != "CamZoom" else var("CamZoom", 1) for v in esc["variables"]]
esc["variables"] = [v if v["name"] != "DirMult" else var("DirMult", 1) for v in esc["variables"]]
esc["variables"] = [v if v["name"] != "SpawnCada" else var("SpawnCada", 2) for v in esc["variables"]]

# ---------- helpers de eventos ----------
def cmp(e1, op, e2): return c("BuiltinCommonInstructions::CompareNumbers", e1, op, e2)
def vtxt(o, v, val, inv=False): return c("VarObjetTxt", o, v, "=", f"\"{val}\"", invertida=inv)
def vnum(o, v, op, val): return c("VarObjet", o, v, op, str(val))
def setn(o, v, op, val): return a("ModVarObjet", o, v, op, str(val))
def sett(o, v, val): return a("ModVarObjetTxt", o, v, "=", val)
def svar(v, op, val): return a("ModVarScene", v, op, str(val))
def cvar(v, op, val): return c("VarScene", v, op, str(val))
def svt(v, val): return a("ModVarSceneTxt", v, "=", val)
def cvt(v, val): return c("VarSceneTxt", v, "=", val)
def timer_ok(o, t, seg): return c("CompareObjectTimer", o, f"\"{t}\"", ">=", str(seg))
def reset_t(o, t): return a("ResetObjectTimer", o, f"\"{t}\"")
def foreach(obj, conds, acts, sub=None):
    return {"type": "BuiltinCommonInstructions::ForEach", "object": obj,
            "conditions": conds, "actions": acts, "events": sub or []}
def tecla(k, inv=False): return c("KeyPressed", "", k, invertida=inv)
def boton(pad, b): return c("Gamepads::C_Button_pressed", "", str(pad), f"\"{b}\"", "")
def anim(o, nombre): return a("SetAnimationName", o, f"Sup.VariableString(Personaje) + \"_{nombre}\"" if o == "Sup"
                              else f"\"{nombre}\"")
VIVO = vtxt("Sup", "Estado", "normal")
TD = ("Sup", "TopDownMovement")
ANCHO, ALTO = datos["ancho_px"], datos["alto_px"]

def anim_dir(obj, dx, dy, pre):
    sa = (lambda s: anim(obj, s)) if obj == "Sup" else (lambda s: a("SetAnimationName", obj, f"\"{s}\""))
    return [
        ev([cmp(f"abs({dx})", ">", f"abs({dy})")], [sa(f"{pre}_lado")], sub=[
            ev([cmp(dx, "<", "0")], [a("FlipX", obj, "yes")]),
            ev([cmp(dx, ">=", "0")], [a("FlipX", obj, "no")])]),
        ev([cmp(f"abs({dx})", "<=", f"abs({dy})"), cmp(dy, "<", "0")], [sa(f"{pre}_arriba"), a("FlipX", obj, "no")]),
        ev([cmp(f"abs({dx})", "<=", f"abs({dy})"), cmp(dy, ">=", "0")], [sa(f"{pre}_abajo"), a("FlipX", obj, "no")]),
    ]

EV = [comentario("FDI-Z · escena Juego. Eventos generados por gdevelop\\scripts\\fase5_jugadores.py "
                 "(no editarlos a mano: cambiar el script y volver a correrlo).")]

# ---------- inicio ----------
EV.append(grupo("Inicio de supervivientes", [
    comentario("Estadísticas por personaje (vida, velocidad ×3, fuerza). Control: 0 teclado y ratón, 1-4 control, -1 bot."),
    ev([vnum("Sup", "Init", "=", 0)], [setn("Sup", "Init", "=", 1), reset_t("Sup", "golpe"), reset_t("Sup", "tinte"),
                                       reset_t("Sup", "caido"), reset_t("Sup", "atasco")], sub=[
        ev([vtxt("Sup", "Personaje", pj)], [setn("Sup", "Vida", "=", v), setn("Sup", "VidaMax", "=", v),
                                            setn("Sup", "Velocidad", "=", s), setn("Sup", "Fuerza", "=", f)])
        for pj, (v, s, f) in PERSONAJES.items()] + [
        ev([], [anim("Sup", "quieto")])]),
    ev([c("DepartScene", "")], [a("Cache", "Mapa"), a("Cache", "Muro"), a("Cache", "ChoqueMueble"),
                                a("Cache", "Marcador"), a("HideLayer", "", "\"Niebla\"")]),
]))

# ---------- unirse con control ----------
union = [comentario("Un control que presione A o Start toma el lugar del primer bot libre.")]
for k in range(1, 5):
    union.append(ev([cvar(f"Pad{k}", "=", 0),
                     {"type": {"value": "BuiltinCommonInstructions::Or"}, "parameters": [],
                      "subInstructions": [boton(k, "A"), boton(k, "START")]}],
                    [], sub=[
        ev([vnum("Sup", "Control", "=", -1), c("BuiltinCommonInstructions::Once")], [], sub=[
            {"type": "BuiltinCommonInstructions::ForEach", "object": "Sup", "conditions": [], "actions": [],
             "events": [ev([cvar(f"Pad{k}", "=", 0)], [setn("Sup", "Control", "=", k), svar(f"Pad{k}", "=", 1)])]}])]))
EV.append(grupo("Unirse con control", union))

# ---------- entrada: teclado y ratón ----------
TEC = vnum("Sup", "Control", "=", 0)
entrada = [
    comentario("Cada cuadro: MovX/MovY, AimX/AimY, QuierePegar y Usando según el control de cada quien. "
               "Teclado: WASD, ratón apunta, clic izq pegar, F usar/revivir, Shift caminar despacio. "
               "Control: stick izq, X pegar, A usar/revivir."),
    ev([], [setn("Sup", "MovX", "=", 0), setn("Sup", "MovY", "=", 0), setn("Sup", "QuierePegar", "=", 0),
            setn("Sup", "Usando", "=", 0), setn("Sup", "PideHab", "=", 0), setn("Sup", "PideEsp", "=", 0)]),
    ev([TEC, tecla("a")], [setn("Sup", "MovX", "-", 1)]),
    ev([TEC, tecla("d")], [setn("Sup", "MovX", "+", 1)]),
    ev([TEC, tecla("w")], [setn("Sup", "MovY", "-", 1)]),
    ev([TEC, tecla("s")], [setn("Sup", "MovY", "+", 1)]),
    ev([TEC], [setn("Sup", "AimX", "=", "CursorX() - Sup.X()"), setn("Sup", "AimY", "=", "CursorY() - (Sup.Y() - 40)")]),
    ev([TEC, c("MouseButtonPressed", "", "Left")], [setn("Sup", "QuierePegar", "=", 1)]),
    ev([TEC, tecla("f")], [setn("Sup", "Usando", "=", 1)]),
    ev([TEC, c("KeyReleased", "", "e")], [setn("Sup", "PideHab", "=", 1)]),
    ev([TEC, c("KeyReleased", "", "c")], [setn("Sup", "PideEsp", "=", 1)]),
    # piloto de depuración (solo P1 de teclado)
    ev([TEC, cvt("Piloto", "\"izq\"")], [setn("Sup", "MovX", "=", -1)]),
    ev([TEC, cvt("Piloto", "\"der\"")], [setn("Sup", "MovX", "=", 1)]),
    ev([TEC, cvt("Piloto", "\"arriba\"")], [setn("Sup", "MovY", "=", -1)]),
    ev([TEC, cvt("Piloto", "\"abajo\"")], [setn("Sup", "MovY", "=", 1)]),
]
for k in range(1, 5):
    P = vnum("Sup", "Control", "=", k)
    sx, sy = f"Gamepads::StickForceX({k}, \"Left\")", f"Gamepads::StickForceY({k}, \"Left\")"
    entrada += [
        ev([P], [setn("Sup", "MovX", "=", sx), setn("Sup", "MovY", "=", sy)]),
        ev([P, cmp(f"abs({sx}) + abs({sy})", ">", "0.3")], [setn("Sup", "AimX", "=", sx), setn("Sup", "AimY", "=", sy)]),
        ev([P, boton(k, "X")], [setn("Sup", "QuierePegar", "=", 1)]),
        ev([P, boton(k, "A")], [setn("Sup", "Usando", "=", 1)]),
        ev([P, c("Gamepads::C_Button_released", "", str(k), "\"Y\"", "")], [setn("Sup", "PideHab", "=", 1)]),
        ev([P, c("Gamepads::C_Button_released", "", str(k), "\"RB\"", "")], [setn("Sup", "PideEsp", "=", 1)]),
    ]
EV.append(grupo("Entrada (teclado y controles)", entrada))

# ---------- bots ----------
BOT = vnum("Sup", "Control", "=", -1)
bots = [
    comentario("Bots: 1) reviven al caído más cercano, 2) pelean con el zombie más cercano a menos de 320 px, "
               "3) siguen al humano más cercano. Si se quedan a más de 1100 px aparecen junto al jugador 1."),
    foreach("Sup", [BOT, VIVO], [setn("Sup", "AimX", "=", "Sup.Variable(AimX)")], sub=[
        # seguir al jugador humano 1 (o al primero vivo)
        ev([cmp("DistanceBetweenPositions(Sup.X(), Sup.Y(), Variable(SegX), Variable(SegY))", ">", "160")],
           [setn("Sup", "MovX", "=", "(Variable(SegX) - Sup.X()) / max(1, DistanceBetweenPositions(Sup.X(), Sup.Y(), Variable(SegX), Variable(SegY)))"),
            setn("Sup", "MovY", "=", "(Variable(SegY) - Sup.Y()) / max(1, DistanceBetweenPositions(Sup.X(), Sup.Y(), Variable(SegX), Variable(SegY)))")]),
        ev([timer_ok("Sup", "atasco", 1.5)], [reset_t("Sup", "atasco")], sub=[
            ev([cmp("DistanceBetweenPositions(Sup.X(), Sup.Y(), Sup.Variable(UltX), Sup.Variable(UltY))", "<", "30"),
                cmp("DistanceBetweenPositions(Sup.X(), Sup.Y(), Variable(SegX), Variable(SegY))", ">", "250")],
               [a("MettreXY", "Sup", "=", "Variable(SegX) + RandomInRange(-50, 50)", "=", "Variable(SegY) + 48")]),
            ev([], [setn("Sup", "UltX", "=", "Sup.X()"), setn("Sup", "UltY", "=", "Sup.Y()")])]),
        ev([cmp("DistanceBetweenPositions(Sup.X(), Sup.Y(), Variable(SegX), Variable(SegY))", ">", "1100")],
           [a("MettreXY", "Sup", "=", "Variable(SegX) + RandomInRange(-60, 60)", "=", "Variable(SegY) + 40")]),
        # pelear
        ev([vtxt("Zombies", "Estado", "muerto", inv=True), c("PickNearest", "Zombies", "Sup.X()", "Sup.Y()", "")], [], sub=[
            ev([cmp("Sup.Distance(Zombies)", "<", "320")],
               [setn("Sup", "AimX", "=", "Zombies.X() - Sup.X()"), setn("Sup", "AimY", "=", "Zombies.Y() - Sup.Y()")], sub=[
                ev([cmp("Sup.Distance(Zombies)", ">", "70")],
                   [setn("Sup", "MovX", "=", "(Zombies.X() - Sup.X()) / max(1, Sup.Distance(Zombies))"),
                    setn("Sup", "MovY", "=", "(Zombies.Y() - Sup.Y()) / max(1, Sup.Distance(Zombies))")]),
                ev([cmp("Sup.Distance(Zombies)", "<=", "95")], [setn("Sup", "QuierePegar", "=", 1)]),
            ]),
        ]),
    ]),
]
# revivir (bots): ir hacia el caído k
for k in range(1, 5):
    bots.append(foreach("Sup", [BOT, VIVO, cvar(f"J{k}Ok", "=", 2)], [], sub=[
        ev([cmp(f"DistanceBetweenPositions(Sup.X(), Sup.Y(), Variable(J{k}X), Variable(J{k}Y))", "<", "600")],
           [setn("Sup", "MovX", "=", f"(Variable(J{k}X) - Sup.X()) / max(1, DistanceBetweenPositions(Sup.X(), Sup.Y(), Variable(J{k}X), Variable(J{k}Y)))"),
            setn("Sup", "MovY", "=", f"(Variable(J{k}Y) - Sup.Y()) / max(1, DistanceBetweenPositions(Sup.X(), Sup.Y(), Variable(J{k}X), Variable(J{k}Y)))"),
            setn("Sup", "QuierePegar", "=", 0)], sub=[
            ev([cmp(f"DistanceBetweenPositions(Sup.X(), Sup.Y(), Variable(J{k}X), Variable(J{k}Y))", "<", "60")],
               [setn("Sup", "MovX", "=", 0), setn("Sup", "MovY", "=", 0), setn("Sup", "Usando", "=", 1)])])]))
EV.append(grupo("Bots", bots))

# ---------- movimiento y animación ----------
EV.append(grupo("Movimiento y animación", [
    comentario("El stick/teclas se simulan en el movimiento top-down. Shift (teclado) = caminar despacio."),
    ev([VIVO], [a("TopDownMovementBehavior::MaxSpeed", *TD, "=", "Sup.Variable(Velocidad) * Sup.Variable(Rapidez)")]),
    ev([VIVO, TEC, tecla("LShift")], [a("TopDownMovementBehavior::MaxSpeed", *TD, "=", "Sup.Variable(Velocidad) * 0.5")]),
    foreach("Sup", [VIVO, cmp("abs(Sup.Variable(MovX)) + abs(Sup.Variable(MovY))", ">", "0.2")],
            [a("TopDownMovementBehavior::SimulateStick", *TD, "ToDeg(atan2(Sup.Variable(MovY), Sup.Variable(MovX)))",
               "min(1, sqrt(Sup.Variable(MovX) * Sup.Variable(MovX) + Sup.Variable(MovY) * Sup.Variable(MovY)))")]),
    foreach("Sup", [VIVO, vnum("Sup", "Atacando", "=", 0)], [], sub=[
        ev([c("TopDownMovementBehavior::IsMoving", *TD)], [],
           sub=anim_dir("Sup", "Sup.TopDownMovement::XVelocity()", "Sup.TopDownMovement::YVelocity()", "caminar")),
        ev([c("TopDownMovementBehavior::IsMoving", *TD, invertida=True)], [anim("Sup", "quieto"), a("FlipX", "Sup", "no")]),
    ]),
]))

# ---------- mapa: choques y puertas ----------
EV.append(grupo("Mapa: choques y puertas", [
    comentario("Choques con muros, muebles y puertas. Puerta: mantener Usar junto a ella (normal 1 s, electrónica 8 s). "
               "Restringidas: fase 6."),
    ev([], [a("SeparateFromObjects", "Sup", "Solidos", "")]),
    ev([], [setn("Puerta", "Usada", "=", 0)]),
    foreach("Puerta", [vnum("Puerta", "TiempoAbrir", ">", 0)], [], sub=[
        ev([vnum("Sup", "Usando", "=", 1), VIVO, c("Distance", "Sup", "Puerta", "110")],
           [setn("Puerta", "Progreso", "+", "TimeDelta()"), setn("Puerta", "Usada", "=", 1)], sub=[
            ev([cmp("Puerta.Variable(Progreso)", ">=", "Puerta.Variable(TiempoAbrir)")], [a("Delete", "Puerta", "")])])]),
    ev([vnum("Puerta", "Usada", "=", 0)], [setn("Puerta", "Progreso", "=", 0)]),
]))

# ---------- armas ----------
STATS = {"puños": (7, 1.0, 0.35), "escoba": (10, 1.4, 0.45), "regla": (13, 1.15, 0.3),
         "silla": (18, 1.0, 0.7), "bate": (21, 1.25, 0.5), "extintor": (3, 1.6, 0.6)}
USOS = {"escoba": 28, "regla": 30, "silla": 12, "bate": 24, "extintor": 10}
EV.append(grupo("Armas del salón", [
    foreach("Sup", [VIVO, vtxt("Sup", "Arma", "puños"), c("CollisionNP", "Sup", "ArmaPiso", "", "")], [], sub=[
        ev([], [sett("Sup", "Arma", "ArmaPiso.VariableString(Tipo)")],
           sub=[ev([vtxt("Sup", "Arma", t)], [setn("Sup", "Usos", "=", u)]) for t, u in USOS.items()]
               + [ev([], [a("Delete", "ArmaPiso", "")])])]),
] + [ev([vtxt("Sup", "Arma", t)], [setn("Sup", "DanioArma", "=", d), setn("Sup", "Alcance", "=", r),
                                   setn("Sup", "Cadencia", "=", k)]) for t, (d, r, k) in STATS.items()]))

# ---------- pegar ----------
AX, AY = "Sup.Variable(AimX)", "Sup.Variable(AimY)"
EV.append(grupo("Combate: pegar", [
    foreach("Sup", [VIVO, vnum("Sup", "QuierePegar", "=", 1), timer_ok("Sup", "golpe", "Sup.Variable(Cadencia)")],
            [reset_t("Sup", "golpe"), setn("Sup", "Atacando", "=", 1),
             a("Create", "", "Golpe", "Sup.X()", "Sup.Y() - 40", "\"Juego\"")], sub=[
        ev([], [a("SetAngle", "Golpe", "=", f"ToDeg(atan2({AY}, {AX}))"),
                a("ChangeScale", "Golpe", "=", "2.2 * Sup.Variable(Alcance)"),
                setn("Golpe", "Danio", "=", "Sup.Variable(DanioArma) * Sup.Variable(Fuerza)"),
                setn("Golpe", "Jugador", "=", "Sup.Variable(Jugador)"), reset_t("Golpe", "vida")]),
        *anim_dir("Sup", AX, AY, "pegar"),
        foreach("Zombies", [vtxt("Zombies", "Estado", "muerto", inv=True),
            cmp("DistanceBetweenPositions(Zombies.X(), Zombies.Y() - 40, "
                "Golpe.X() + cos(ToRad(Golpe.Angle())) * 50 * Sup.Variable(Alcance), "
                "Golpe.Y() + sin(ToRad(Golpe.Angle())) * 50 * Sup.Variable(Alcance))", "<", "58 * Sup.Variable(Alcance)")],
            [setn("Zombies", "Vida", "-", "Golpe.Variable(Danio)"), a("ChangeColor", "Zombies", "\"255;90;90\""),
             reset_t("Zombies", "tinte"), a("AddForceVersPos", "Zombies", "Sup.X()", "Sup.Y()", "-280", "0"),
             sett("Zombies", "Estado", "\"persigue\""), setn("Zombies", "UltJugador", "=", "Sup.Variable(Jugador)"),
             a("Create", "", "Salpicadura", "Zombies.X()", "Zombies.Y() - 48", "\"Juego\""), reset_t("Salpicadura", "vida"),
             a("Create", "", "TxtDanio", "Zombies.X() + RandomInRange(-10, 10)", "Zombies.Y() - 110", "\"Juego\""),
             a("TextObject::String", "TxtDanio", "=", "ToString(round(Golpe.Variable(Danio)))"), reset_t("TxtDanio", "vida"),
             svar("Temblor", "=", 0.12)]),
        ev([vtxt("Sup", "Arma", "puños", inv=True)], [setn("Sup", "Usos", "-", 1)]),
        ev([vtxt("Sup", "Arma", "puños", inv=True), vnum("Sup", "Usos", "<=", 0)], [sett("Sup", "Arma", "\"puños\"")]),
    ]),
    ev([vnum("Sup", "Atacando", "=", 1), timer_ok("Sup", "golpe", 0.28)], [setn("Sup", "Atacando", "=", 0)]),
    ev([timer_ok("Golpe", "vida", 0.12)], [a("Delete", "Golpe", "")]),
    ev([timer_ok("Salpicadura", "vida", 0.4)], [a("Delete", "Salpicadura", "")]),
]))

# ---------- posiciones de jugadores (para revivir y bots) ----------
pos = [ev([], [svar(f"J{k}Ok", "=", 0), svar(f"J{k}Usa", "=", 0)]) for k in range(1, 5)]
for k in range(1, 5):
    pos.append(ev([vnum("Sup", "Jugador", "=", k)], [svar(f"J{k}X", "=", "Sup.X()"), svar(f"J{k}Y", "=", "Sup.Y()"),
                                                    svar(f"J{k}Usa", "=", "Sup.Variable(Usando)")], sub=[
        ev([VIVO], [svar(f"J{k}Ok", "=", 1)]),
        ev([vtxt("Sup", "Estado", "caido")], [svar(f"J{k}Ok", "=", 2)])]))
EV.append(grupo("Posiciones de jugadores", [comentario("J{k}Ok: 0 fuera, 1 de pie, 2 caído.")] + pos))

# ---------- vida, caída y revivir ----------
rev = [
    comentario("Con 0 de vida: caído 25 s. Un compañero de pie revive manteniendo Usar 3 s junto a él "
               "(vuelve con 50% de vida). Si nadie lo revive queda fuera (reaparece al cumplir objetivo: fase 6). "
               "Si no queda nadie de pie: derrota y se reinicia (pantalla de Resultados: fase 8)."),
    ev([timer_ok("Sup", "tinte", 0.15)], [a("ChangeColor", "Sup", "\"255;255;255\"")]),
    ev([vnum("Sup", "Vida", "<=", 0), VIVO, vtxt("Sup", "Personaje", "tonyfuerte", inv=True)],
       [sett("Sup", "Estado", "\"caido\""), setn("Sup", "Vida", "=", 0), setn("Sup", "Revivir", "=", 0),
        reset_t("Sup", "caido"), anim("Sup", "caer_levantarse"), a("ActivateBehavior", "Sup", "TopDownMovement", "no")]),
    ev([vtxt("Sup", "Estado", "caido"), c("Sprite", "Sup", ">=", "3")], [a("PauseAnimation", "Sup")]),
    ev([], [setn("Sup", "Ayuda", "=", 0)]),
]
for k in range(1, 5):
    rev.append(foreach("Sup", [vtxt("Sup", "Estado", "caido"), cvar(f"J{k}Ok", "=", 1), cvar(f"J{k}Usa", "=", 1),
                               vnum("Sup", "Jugador", "!=", k),
                               cmp(f"DistanceBetweenPositions(Sup.X(), Sup.Y(), Variable(J{k}X), Variable(J{k}Y))", "<", "80")],
                       [setn("Sup", "Ayuda", "=", 1)]))
rev += [
    ev([vtxt("Sup", "Estado", "caido"), vnum("Sup", "Ayuda", "=", 1)], [setn("Sup", "Revivir", "+", "TimeDelta()")]),
    ev([vtxt("Sup", "Estado", "caido"), vnum("Sup", "Ayuda", "=", 0)], [setn("Sup", "Revivir", "=", "max(0, Sup.Variable(Revivir) - TimeDelta())")]),
    ev([vtxt("Sup", "Estado", "caido"), vnum("Sup", "Revivir", ">=", 3)],
       [sett("Sup", "Estado", "\"normal\""), setn("Sup", "Vida", "=", "Sup.Variable(VidaMax) * 0.5"), setn("Sup", "Revivir", "=", 0),
        a("ActivateBehavior", "Sup", "TopDownMovement", "yes"), a("PlayAnimation", "Sup"), anim("Sup", "quieto")]),
    ev([vtxt("Sup", "Estado", "caido"), timer_ok("Sup", "caido", 25)],
       [sett("Sup", "Estado", "\"fuera\""), a("Cache", "Sup")]),
    ev([], [svar("Vivos", "=", 0)]),
    ev([VIVO], [svar("Vivos", "=", "PickedInstancesCount(Sup)")]),
    ev([cvar("Vivos", "=", 0), cvt("Estado", "\"juego\"")], [svt("Estado", "\"derrota\""), a("ResetTimer", "", "\"fin\"")]),
    ev([cvt("Estado", "\"derrota\""), c("CompareTimer", "", "\"fin\"", ">=", "4")], [a("ModVarGlobalTxt", "Resultado", "=", "\"derrota\""), a("Scene", "", "\"Resultados\"", "")]),
]
EV.append(grupo("Vida, caída y revivir", rev))

# ---------- zombies ----------
ZX = "(Zombies.Pathfinding::NextNodeX() - Zombies.X())"
ZY = "(Zombies.Pathfinding::NextNodeY() - Zombies.Y())"
zomb = [
    comentario("Notan a 255 px al superviviente de pie más cercano y lo persiguen con Pathfinding (ruta cada 0.75 s; "
               "si no hay ruta van directo). Pegan cada 1 s. Gritón despierta a 450 px. Gordo y conserje empujan."),
    ev([vnum("Zombies", "Init", "=", 0)],
       [setn("Zombies", "Init", "=", 1), reset_t("Zombies", "ruta"), reset_t("Zombies", "ataque"),
        reset_t("Zombies", "paseo"), reset_t("Zombies", "tinte"),
        a("PathfindingBehavior::MaxSpeed", "Zombies", "Pathfinding", "=",
          "Zombies.Variable(Velocidad) * (1 + 0.08 * (Variable(Infestacion) - 1))")]),
    ev([vtxt("Zombies", "Estado", "paseando"), VIVO, c("Distance", "Zombies", "Sup", "255")],
       [sett("Zombies", "Estado", "\"persigue\"")]),
    ev([vtxt("Zombies", "Estado", "guardia"), VIVO, c("Distance", "Zombies", "Sup", "255")],
       [sett("Zombies", "Estado", "\"persigue\"")]),
    foreach("Zombies", [vtxt("Zombies", "Estado", "persigue"), timer_ok("Zombies", "ruta", 0.75)], [reset_t("Zombies", "ruta")], sub=[
        ev([VIVO, c("PickNearest", "Sup", "Zombies.X()", "Zombies.Y()", "")],
           [a("PathfindingBehavior::SetDestination", "Zombies", "Pathfinding", "", "Sup.X()", "Sup.Y()")])]),
    foreach("Zombies", [vtxt("Zombies", "Estado", "persigue"),
                        c("PathfindingBehavior::PathFound", "Zombies", "Pathfinding", invertida=True)], [], sub=[
        ev([VIVO, c("PickNearest", "Sup", "Zombies.X()", "Zombies.Y()", "")],
           [a("AddForceVersPos", "Zombies", "Sup.X()", "Sup.Y()", "Zombies.Variable(Velocidad) * 0.8", "0")])]),
    ev([vtxt("Zombies", "Estado", "paseando"), timer_ok("Zombies", "paseo", 4)],
       [a("PathfindingBehavior::SetDestination", "Zombies", "Pathfinding", "",
          "Zombies.X() + RandomInRange(-160, 160)", "Zombies.Y() + RandomInRange(-160, 160)"), reset_t("Zombies", "paseo")]),
    foreach("ZGriton", [vtxt("ZGriton", "Estado", "persigue"), vnum("ZGriton", "Grito", "=", 0)],
            [setn("ZGriton", "Grito", "=", 1), a("SetAnimationName", "ZGriton", "\"gritar\""), reset_t("ZGriton", "ataque")],
            [ev([c("Distance", "Zombies", "ZGriton", "450"), vtxt("Zombies", "Estado", "muerto", inv=True)],
                [sett("Zombies", "Estado", "\"persigue\"")])]),
    foreach("Zombies", [vtxt("Zombies", "Estado", "persigue"), timer_ok("Zombies", "ataque", 1)], [], sub=[
        ev([VIVO, c("Distance", "Sup", "Zombies", "80"), c("PickNearest", "Sup", "Zombies.X()", "Zombies.Y()", "")],
           [reset_t("Zombies", "ataque"), setn("Sup", "Vida", "-", "Zombies.Variable(Danio) * Sup.Variable(ResDanio) * GlobalVariable(DifDanio)"),
            setn("Sup", "Golpeado", "=", 1),
            a("ChangeColor", "Sup", "\"255;110;110\""), reset_t("Sup", "tinte")],
           sub=anim_dir("Zombies", "(Sup.X() - Zombies.X())", "(Sup.Y() - Zombies.Y())", "atacar"))]),
    foreach("Zombies", [vtxt("Zombies", "Estado", "muerto", inv=True), timer_ok("Zombies", "ataque", 0.45),
                        cmp("Zombies.Pathfinding::Speed()", ">", "1")], [], anim_dir("Zombies", ZX, ZY, "caminar")),
    ev([VIVO, c("CollisionNP", "Sup", "ZGordo", "", ""), vtxt("ZGordo", "Estado", "muerto", inv=True)],
       [a("AddForceVersPos", "Sup", "ZGordo.X()", "ZGordo.Y()", "-220", "0")]),
    ev([VIVO, c("CollisionNP", "Sup", "ZConserje", "", ""), vtxt("ZConserje", "Estado", "muerto", inv=True)],
       [a("AddForceVersPos", "Sup", "ZConserje.X()", "ZConserje.Y()", "-220", "0")]),
    ev([vnum("Zombies", "Vida", "<=", 0), vtxt("Zombies", "Estado", "muerto", inv=True)],
       [sett("Zombies", "Estado", "\"muerto\""), a("SetAnimationName", "Zombies", "\"golpe_morir\""),
        a("ActivateBehavior", "Zombies", "Pathfinding", "no"), svar("Tumbados", "+", 1), 
        svar("OroJefe", "+", "Zombies.Variable(Oro)")]),
    ev([vtxt("Zombies", "Estado", "muerto"), c("AnimationEnded", "Zombies")], [a("Delete", "Zombies", "")]),
    ev([timer_ok("Zombies", "tinte", 0.12)], [a("ChangeColor", "Zombies", "\"255;255;255\"")]),
    ev([], [a("SeparateFromObjects", "Zombies", "Solidos", ""), a("ChangePlan", "Zombies", "=", "Zombies.Y()")]),
    ev([VIVO, vtxt("Zombies", "Estado", "muerto", inv=True)], [a("SeparateFromObjects", "Sup", "Zombies", "")]),
]
EV.append(grupo("Zombies: IA, ataque y muerte", zomb))

# ---------- infestación ----------
inf = [
    comentario("Sube un nivel cada 95 s hasta 5. Objetivo de zombies 10/15/22/30/40. Nivel 2: corredores; 3+: gordos y "
               "gritones. Salen por las salidas libres junto a las rejillas, lejos de la cámara."),
    ev([c("DepartScene", "")], [a("ResetTimer", "", "\"infest\""), a("ResetTimer", "", "\"spawn\""), svar("Infestacion", "=", 1)]),
    ev([c("CompareTimer", "", "\"infest\"", ">=", "95 / GlobalVariable(DifInf)"), cvar("Infestacion", "<", 5)],
       [svar("Infestacion", "+", 1), a("ResetTimer", "", "\"infest\"")]),
] + [ev([cvar("Infestacion", "=", n)], [svar("ObjZombies", "=", o), svar("MaxTipo", "=", m)])
     for n, o, m in [(1, 10, 6), (2, 15, 8), (3, 22, 10), (4, 30, 10), (5, 40, 10)]]
crear = []
for cond, obj in [([cvar("R2", "<=", 6)], "ZNormal"), ([cvar("R2", ">=", 7), cvar("R2", "<=", 8)], "ZCorredor"),
                  ([cvar("R2", "=", 9)], "ZGordo"), ([cvar("R2", "=", 10)], "ZGriton")]:
    crear.append(ev(cond, [a("Create", "", obj, "Marcador.X() + 16", "Marcador.Y() + 32", "\"Juego\""),
                           sett(obj, "Estado", "\"persigue\"")]))
inf.append(ev([c("CompareTimer", "", "\"spawn\"", ">=", "Variable(SpawnCada) * Variable(DirMult)"), cmp("SceneInstancesCount(Zombies)", "<", "Variable(ObjZombies) + Variable(ExtraZombies) + Variable(DirExtra)"), c("VarSceneTxt", "Estado", "!=", "\"intro\"")],
              [a("ResetTimer", "", "\"spawn\""),
               svar("R", "=", f"RandomInRange(0, {len(datos['marcadores']['rejillas_jefe']) - 1})"),
               svar("R2", "=", "RandomInRange(1, Variable(MaxTipo))")], sub=[
    ev([vtxt("Marcador", "Tipo", "salida_zombie"), vnum("Marcador", "Indice", "=", "Variable(R)"),
        cmp("abs(Marcador.X() - CameraX()) + abs(Marcador.Y() - CameraY())", ">", "1300")], [], sub=crear)]))
EV.append(grupo("Infestación", inf))

# ---------- cámara compartida ----------
cam = [
    comentario("Centro = promedio de los humanos de pie (si no hay, de todos los de pie). Se aleja si se separan "
               "(zoom 1 a 0.6) y nadie puede salirse de la pantalla."),
    ev([], [svar("CamN", "=", 0), svar("CamX", "=", 0), svar("CamY", "=", 0), svar("CamMinX", "=", 999999),
            svar("CamMaxX", "=", -999999), svar("CamMinY", "=", 999999), svar("CamMaxY", "=", -999999),
            svar("Humanos", "=", 0)]),
    ev([VIVO, vnum("Sup", "Control", ">=", 0)], [svar("Humanos", "=", "PickedInstancesCount(Sup)")]),
]
for filtro in ([vnum("Sup", "Control", ">=", 0)], []):
    cam.append(foreach("Sup", [VIVO] + filtro + ([cvar("Humanos", "=", 0)] if not filtro else []), [
        svar("CamN", "+", 1), svar("CamX", "+", "Sup.X()"), svar("CamY", "+", "Sup.Y() - 48"),
        svar("CamMinX", "=", "min(Variable(CamMinX), Sup.X())"), svar("CamMaxX", "=", "max(Variable(CamMaxX), Sup.X())"),
        svar("CamMinY", "=", "min(Variable(CamMinY), Sup.Y())"), svar("CamMaxY", "=", "max(Variable(CamMaxY), Sup.Y())")]))
cam += [
    ev([cvar("CamN", ">", 0)], [svar("CamX", "/", "Variable(CamN)"), svar("CamY", "/", "Variable(CamN)"),
        svar("CamZoom", "=", "clamp(min(1500 / max(1, Variable(CamMaxX) - Variable(CamMinX)), "
                             "780 / max(1, Variable(CamMaxY) - Variable(CamMinY))), 0.6, 1)")], sub=[
        ev([c("DepartScene", "")], [a("CameraX", "", "=", "Variable(CamX)", "", ""), a("CameraY", "", "=", "Variable(CamY)", "", "")]),
        ev([], [a("ZoomCamera", "", "CameraZoom() + (Variable(CamZoom) - CameraZoom()) * min(1, 3 * TimeDelta())", "", ""),
                a("CameraX", "", "=", "CameraX() + (Variable(CamX) - CameraX()) * min(1, 6 * TimeDelta())", "", ""),
                a("CameraY", "", "=", "CameraY() + (Variable(CamY) - CameraY()) * min(1, 6 * TimeDelta())", "", ""),
                a("CameraX", "", "=", f"clamp(CameraX(), 960 / CameraZoom(), {ANCHO} - 960 / CameraZoom())", "", ""),
                a("CameraY", "", "=", f"clamp(CameraY(), 540 / CameraZoom(), {ALTO} - 540 / CameraZoom())", "", "")]),
    ]),
    ev([VIVO, vnum("Sup", "Control", ">=", 0)],
       [a("MettreXY", "Sup", "=", "clamp(Sup.X(), CameraBorderLeft() + 40, CameraBorderRight() - 40)",
          "=", "clamp(Sup.Y(), CameraBorderTop() + 100, CameraBorderBottom() - 10)")]),
    ev([], [a("ChangePlan", "Sup", "=", "Sup.Y()")]),
]
EV.append(grupo("Cámara compartida", cam))

# ---------- depuración ----------
dep = [
    comentario("QUITAR ANTES DE PRESENTAR. I/J/K/L: P1 camina solo (O para). U: levantar a todos. H: tumbar a P1. N: subir infestación. "
               "Texto amarillo: estado de cada jugador."),
] + [ev([tecla(k), c("BuiltinCommonInstructions::Once")], [svt("Piloto", f"\"{d}\"")])
     for k, d in {"i": "arriba", "j": "izq", "k": "abajo", "l": "der", "o": ""}.items()] + [
    ev([tecla("u"), c("BuiltinCommonInstructions::Once")],
       [sett("Sup", "Estado", "\"normal\""), setn("Sup", "Vida", "=", "Sup.Variable(VidaMax)"), a("Montre", "Sup", ""),
        a("ActivateBehavior", "Sup", "TopDownMovement", "yes"), a("PlayAnimation", "Sup"), svt("Estado", "\"juego\"")]),
    ev([tecla("h"), c("BuiltinCommonInstructions::Once"), vnum("Sup", "Jugador", "=", 1)], [setn("Sup", "Vida", "=", 0)]),
    ev([tecla("n"), c("BuiltinCommonInstructions::Once"), cvar("Infestacion", "<", 5)],
       [svar("Infestacion", "+", 1), a("ResetTimer", "", "\"infest\"")]),
    ev([], [a("TextObject::String", "TxtDebug", "=",
              "\"infestación \" + ToString(Variable(Infestacion)) + \"   zombies \" + ToString(SceneInstancesCount(Zombies)) + "
              "\"   tumbados \" + ToString(Variable(Tumbados)) + \"   zoom \" + ToString(round(CameraZoom() * 100) / 100) + "
              "\"   estado \" + VariableString(Estado)")]),
    foreach("Sup", [], [a("TextObject::String", "TxtDebug", "=",
        "TxtDebug.String() + NewLine() + \"P\" + ToString(Sup.Variable(Jugador)) + \" \" + Sup.VariableString(Personaje) + "
        "\" [\" + ToString(Sup.Variable(Control)) + \"] \" + Sup.VariableString(Estado) + \" vida \" + "
        "ToString(round(Sup.Variable(Vida))) + \" arma \" + Sup.VariableString(Arma) + \" rev \" + ToString(round(Sup.Variable(Revivir) * 10) / 10)")]),
    ev([tecla("F3"), c("BuiltinCommonInstructions::Once")], [svar("VerDebug", "=", "1 - Variable(VerDebug)")]),
    ev([cvar("VerDebug", "=", 0)], [a("Cache", "TxtDebug")]),
    ev([cvar("VerDebug", "=", 1)], [a("Montre", "TxtDebug", "")]),
]
EV.insert(1, grupo("Depuración (quitar antes de presentar)", dep, color=(200, 80, 80)))

esc["events"] = EV
# variable nueva en Golpe y Puerta
for o in esc["objects"]:
    if o["name"] == "Golpe" and not any(v["name"] == "Jugador" for v in o["variables"]):
        o["variables"].append(var("Jugador", 0))
    if o["name"] == "Puerta" and not any(v["name"] == "Usada" for v in o["variables"]):
        o["variables"].append(var("Usada", 0))
json.dump(p, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("OK fase 5:", len(anims), "animaciones en Sup,", len(EV), "grupos de eventos")
