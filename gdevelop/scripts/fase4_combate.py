"""Fase 4: combate (pegar con clic hacia el cursor, armas del salón), zombies con Pathfinding,
vida/daño, tipos (normal, corredor, gritón, gordo, conserje; curado listo para la fase 7) e infestación.
Uso: python fase4_combate.py <FDI-Z.json> <atlas.json> <mapa_fdiz_datos.json>   (re-ejecutable)
Los sprites de zombies, armas y efectos se referencian en ../../generado/sprites (ver empaquetar_recursos.py).
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gd_util import *

ruta, atlas_json, datos_json = sys.argv[1:4]
p = json.load(open(ruta, encoding="utf-8"))
atlas = json.load(open(atlas_json, encoding="utf-8"))
datos = json.load(open(datos_json, encoding="utf-8"))
esc = next(l for l in p["layouts"] if l["name"] == "Juego")
GEN = "../../generado/sprites/"          # relativo a la carpeta del proyecto

recursos = {r["name"]: r for r in p["resources"]["resources"]}
def recurso(rel):
    recursos[rel] = res_imagen(rel, GEN + rel)
    return rel

# ---------------- zombies ----------------
TIPOS = {  # objeto: (entidad, vida, velocidad px/s (x3), daño, oro del Jefe)
    "ZNormal":   ("normal",   30, 99,  5, 1),
    "ZCorredor": ("corredor", 16, 192, 4, 1),
    "ZGriton":   ("griton",   34, 90,  4, 2),
    "ZGordo":    ("gordo",   120, 63, 11, 3),
    "ZConserje": ("conserje",250, 72, 14, 5),
    "ZCurado":   ("curado",   30, 99,  0, 0),
}
def objeto_zombie(nombre, ent, vida, vel, dano, oro):
    e = atlas["entidades"][f"zombies/{ent}"]
    w, h = e["lienzo"]
    origen = (w // 2, h - 2)
    mascara = (origen[0] - 16, origen[1] - 14, origen[0] + 16, origen[1])
    anims = [animacion(n, [recurso(f) for f in an["cuadros"]], an["fps"], an["loop"], origen, mascara)
             for n, an in e["animaciones"].items()]
    pf = {"name": "Pathfinding", "type": "PathfindingBehavior::PathfindingBehavior",
          "allowDiagonals": True, "acceleration": 900, "maxSpeed": vel, "angularMaxSpeed": 180,
          "rotateObject": False, "angleOffset": 0, "cellWidth": 32, "cellHeight": 32,
          "extraBorder": 0, "gridOffsetX": 0, "gridOffsetY": 0, "smoothingMaxCellGap": 1}
    return objeto_sprite(nombre, anims, variables=[
        var("Tipo", ent), var("Vida", vida), var("VidaMax", vida), var("Danio", dano),
        var("Velocidad", vel), var("Oro", oro), var("Estado", "paseando"), var("Init", 0),
        var("Grito", 0)], comportamientos=[pf])

nuevos = [objeto_zombie(n, *v) for n, v in TIPOS.items()]

# ---------------- golpe, efectos y armas ----------------
og = atlas["objetos"]
golpe = objeto_sprite("Golpe", [animacion("arco", [recurso(og["efectos_generales"]["arco_golpe"]["archivo"])],
                                          1, False, (0, 15))],
                      variables=[var("Danio", 0)])
salp = objeto_sprite("Salpicadura", [animacion("verde", [recurso(og["efectos_generales"]["salpicadura_verde"]["archivo"])],
                                               1, False, (16, 16))])
armas = ["escoba", "silla", "regla", "bate", "extintor"]
arma_piso = objeto_sprite("ArmaPiso",
    [animacion(t, [recurso(og["armas"][t]["archivo"])], 1, False,
               (og["armas"][t]["tamano"][0] // 2, og["armas"][t]["tamano"][1])) for t in armas],
    variables=[var("Tipo", "escoba")])
txt = {"assetStoreId": "", "name": "TxtDebug", "type": "TextObject::Text", "variables": [], "effects": [],
       "behaviors": [], "content": {"bold": True, "isOutlineEnabled": True, "isShadowEnabled": False,
       "italic": False, "outlineColor": "0;0;0", "outlineThickness": 3, "shadowAngle": 90,
       "shadowBlurRadius": 2, "shadowColor": "0;0;0", "shadowDistance": 4, "shadowOpacity": 127,
       "smoothed": False, "underlined": False, "text": "depuración", "font": "",
       "textAlignment": "left", "verticalTextAlignment": "top", "characterSize": 26, "lineHeight": 0,
       "color": "255;255;160"}}
nuevos += [golpe, salp, arma_piso, txt]

NOMBRES = {o["name"] for o in nuevos}
esc["objects"] = [o for o in esc["objects"] if o["name"] not in NOMBRES] + nuevos
p["resources"]["resources"] = list(recursos.values())
esc["objectsGroups"] = [g for g in esc["objectsGroups"] if g["name"] != "Zombies"] + [
    {"name": "Zombies", "objects": [{"name": n} for n in TIPOS if n != "ZCurado"]}]

# variables nuevas de Tony
tony = next(o for o in esc["objects"] if o["name"] == "Tony")
for v in [var("Arma", "puños"), var("Usos", 0), var("DanioArma", 7), var("Alcance", 1.0),
          var("Cadencia", 0.35), var("Atacando", 0)]:
    if not any(x["name"] == v["name"] for x in tony["variables"]):
        tony["variables"].append(v)
for v in [var("Infestacion", 1), var("ObjZombies", 10), var("MaxTipo", 6), var("R", 0), var("R2", 0),
          var("Tumbados", 0), var("OroJefe", 0), var("DbgDist", 0), var("DbgAng", 0)]:
    esc["variables"] = [x for x in esc["variables"] if x["name"] != v["name"]] + [v]

# ---------------- instancias de prueba: armas del salón y zombies iniciales ----------------
esc["instances"] = [i for i in esc["instances"] if i["name"] not in NOMBRES]
def arma(t, x, y):
    i = instancia("ArmaPiso", x, y, "Juego", int(y), variables=[var("Tipo", t)])
    i["numberProperties"] = [{"name": "animation", "value": armas.index(t)}]
    esc["instances"].append(i)
arma("escoba", 5210, 2440); arma("regla", 5330, 2560); arma("silla", 5010, 2580)   # salón E-04
arma("extintor", 4700, 2720)                                                          # pasillo E
b = datos["marcadores"]["botin_raro"]; arma("bate", b["x"], b["y"])                    # Dirección
esc["instances"].append(instancia("TxtDebug", 20, 20, "HUD", 100))
def zombie(obj, x, y, estado="paseando"):
    esc["instances"].append(instancia(obj, x, y, "Juego", int(y), variables=[var("Estado", estado)]))
for x in (3900, 4300, 4700, 5600):
    zombie("ZNormal", x, 2780)
zombie("ZCorredor", 6200, 2900); zombie("ZGordo", 5400, 3150); zombie("ZGriton", 4800, 3050)
cz = datos["marcadores"]["conserje_zombie"]; zombie("ZConserje", cz["x"], cz["y"], "guardia")

# ---------------- eventos ----------------
def cmp(e1, op, e2): return c("BuiltinCommonInstructions::CompareNumbers", e1, op, e2)
def vtxt(o, v, val, inv=False): return c("VarObjetTxt", o, v, "=", f"\"{val}\"", invertida=inv)
def vnum(o, v, op, val): return c("VarObjet", o, v, op, str(val))
def setn(o, v, op, val): return a("ModVarObjet", o, v, op, str(val))
def sett(o, v, val): return a("ModVarObjetTxt", o, v, "=", val)
def timer_ok(o, t, seg): return c("CompareObjectTimer", o, f"\"{t}\"", ">=", str(seg))
def reset_t(o, t): return a("ResetObjectTimer", o, f"\"{t}\"")
def foreach(obj, conds, acts, sub=None):
    return {"type": "BuiltinCommonInstructions::ForEach", "object": obj,
            "conditions": conds, "actions": acts, "events": sub or []}
VIVO = vtxt("Tony", "Estado", "normal")
DX, DY = "(CursorX() - Tony.X())", "(CursorY() - (Tony.Y() - 40))"

STATS = {"puños": (7, 1.0, 0.35), "escoba": (10, 1.4, 0.45), "regla": (13, 1.15, 0.3),
         "silla": (18, 1.0, 0.7), "bate": (21, 1.25, 0.5), "extintor": (3, 1.6, 0.6)}
USOS = {"escoba": 28, "regla": 30, "silla": 12, "bate": 24, "extintor": 10}

g_armas = grupo("Armas del salón", [
    comentario("Se recoge pasando encima si traes las manos vacías (cambiar arma con Usar: fase 8). "
               "Daño, alcance, cadencia y usos según la tabla del equipo."),
    ev([c("CollisionNP", "Tony", "ArmaPiso", "", ""), vtxt("Tony", "Arma", "puños"), VIVO],
       [sett("Tony", "Arma", "ArmaPiso.VariableString(Tipo)")],
       sub=[ev([vtxt("Tony", "Arma", t)], [setn("Tony", "Usos", "=", u)]) for t, u in USOS.items()]
           + [ev([], [a("Delete", "ArmaPiso", "")])]),
] + [ev([vtxt("Tony", "Arma", t)], [setn("Tony", "DanioArma", "=", d), setn("Tony", "Alcance", "=", r),
                                    setn("Tony", "Cadencia", "=", k)]) for t, (d, r, k) in STATS.items()])

g_pegar = grupo("Combate: pegar (clic hacia el cursor)", [
    ev([c("DepartScene", "")], [reset_t("Tony", "golpe"), reset_t("Tony", "tinte")]),
    ev([c("MouseButtonPressed", "", "Left"), timer_ok("Tony", "golpe", "Tony.Variable(Cadencia)"), VIVO],
       [reset_t("Tony", "golpe"), setn("Tony", "Atacando", "=", 1), a("ModVarScene", "DbgDist", "=", "99999"),
        a("Create", "", "Golpe", "Tony.X()", "Tony.Y() - 40", "\"Juego\"")], sub=[
        ev([], [a("SetAngle", "Golpe", "=", f"ToDeg(atan2({DY}, {DX}))"),
                a("ChangeScale", "Golpe", "=", "2.2 * Tony.Variable(Alcance)"),
                setn("Golpe", "Danio", "=", "Tony.Variable(DanioArma) * Tony.Variable(Fuerza)"),
                reset_t("Golpe", "vida")]),
        ev([cmp(f"abs({DX})", ">", f"abs({DY})")], [a("SetAnimationName", "Tony", "\"pegar_lado\"")], sub=[
            ev([cmp(DX, "<", "0")], [a("FlipX", "Tony", "yes")]),
            ev([cmp(DX, ">=", "0")], [a("FlipX", "Tony", "no")])]),
        ev([cmp(f"abs({DX})", "<=", f"abs({DY})"), cmp(DY, "<", "0")],
           [a("SetAnimationName", "Tony", "\"pegar_arriba\""), a("FlipX", "Tony", "no")]),
        ev([cmp(f"abs({DX})", "<=", f"abs({DY})"), cmp(DY, ">=", "0")],
           [a("SetAnimationName", "Tony", "\"pegar_abajo\""), a("FlipX", "Tony", "no")]),
        foreach("Zombies", [vtxt("Zombies", "Estado", "muerto", inv=True)],
            [a("ModVarScene", "DbgDist", "=", "min(Variable(DbgDist), DistanceBetweenPositions(Zombies.X(), Zombies.Y() - 40, "
               "Golpe.X() + cos(ToRad(Golpe.Angle())) * 50 * Tony.Variable(Alcance), "
               "Golpe.Y() + sin(ToRad(Golpe.Angle())) * 50 * Tony.Variable(Alcance)))"),
             a("ModVarScene", "DbgAng", "=", "Golpe.Angle()")]),
        foreach("Zombies", [vtxt("Zombies", "Estado", "muerto", inv=True),
            cmp("DistanceBetweenPositions(Zombies.X(), Zombies.Y() - 40, "
                "Golpe.X() + cos(ToRad(Golpe.Angle())) * 50 * Tony.Variable(Alcance), "
                "Golpe.Y() + sin(ToRad(Golpe.Angle())) * 50 * Tony.Variable(Alcance))",
                "<", "58 * Tony.Variable(Alcance)")],
           [setn("Zombies", "Vida", "-", "Golpe.Variable(Danio)"),
            a("ChangeColor", "Zombies", "\"255;90;90\""), reset_t("Zombies", "tinte"),
            a("AddForceVersPos", "Zombies", "Tony.X()", "Tony.Y()", "-280", "0"),
            sett("Zombies", "Estado", "\"persigue\""),
            a("Create", "", "Salpicadura", "Zombies.X()", "Zombies.Y() - 48", "\"Juego\""),
            reset_t("Salpicadura", "vida")]),
        ev([vtxt("Tony", "Arma", "puños", inv=True)], [setn("Tony", "Usos", "-", 1)]),
        ev([vtxt("Tony", "Arma", "puños", inv=True), vnum("Tony", "Usos", "<=", 0)],
           [sett("Tony", "Arma", "\"puños\"")]),
    ]),
    ev([vnum("Tony", "Atacando", "=", 1), timer_ok("Tony", "golpe", 0.28)], [setn("Tony", "Atacando", "=", 0)]),
    ev([], [a("MettreXY", "Golpe", "=", "Tony.X()", "=", "Tony.Y() - 40")]),
    ev([timer_ok("Golpe", "vida", 0.12)], [a("Delete", "Golpe", "")]),
    ev([timer_ok("Salpicadura", "vida", 0.4)], [a("Delete", "Salpicadura", "")]),
])

def anim_dir(obj, dx, dy, pre):
    return [
        ev([cmp(f"abs({dx})", ">", f"abs({dy})")], [a("SetAnimationName", obj, f"\"{pre}_lado\"")], sub=[
            ev([cmp(dx, "<", "0")], [a("FlipX", obj, "yes")]),
            ev([cmp(dx, ">=", "0")], [a("FlipX", obj, "no")])]),
        ev([cmp(f"abs({dx})", "<=", f"abs({dy})"), cmp(dy, "<", "0")],
           [a("SetAnimationName", obj, f"\"{pre}_arriba\""), a("FlipX", obj, "no")]),
        ev([cmp(f"abs({dx})", "<=", f"abs({dy})"), cmp(dy, ">=", "0")],
           [a("SetAnimationName", obj, f"\"{pre}_abajo\""), a("FlipX", obj, "no")]),
    ]

ZX = "(Zombies.Pathfinding::NextNodeX() - Zombies.X())"
ZY = "(Zombies.Pathfinding::NextNodeY() - Zombies.Y())"
g_zombies = grupo("Zombies: IA, ataque y muerte", [
    comentario("Te notan a 255 px. Persiguen con Pathfinding (ruta cada 0.5 s), pegan cada 1 s. "
               "Gritón despierta a los cercanos. Gordo empuja. Velocidad × (1 + 8% por nivel de infestación)."),
    ev([vnum("Zombies", "Init", "=", 0)],
       [setn("Zombies", "Init", "=", 1), reset_t("Zombies", "ruta"), reset_t("Zombies", "ataque"),
        reset_t("Zombies", "paseo"), reset_t("Zombies", "tinte"),
        a("PathfindingBehavior::MaxSpeed", "Zombies", "Pathfinding", "=",
          "Zombies.Variable(Velocidad) * (1 + 0.08 * (Variable(Infestacion) - 1))")]),
    ev([vtxt("Zombies", "Estado", "paseando"), c("Distance", "Zombies", "Tony", "255"), VIVO],
       [sett("Zombies", "Estado", "\"persigue\"")]),
    ev([vtxt("Zombies", "Estado", "guardia"), c("Distance", "Zombies", "Tony", "255"), VIVO],
       [sett("Zombies", "Estado", "\"persigue\"")]),
    ev([vtxt("Zombies", "Estado", "persigue"), timer_ok("Zombies", "ruta", 0.75)],
       [a("PathfindingBehavior::SetDestination", "Zombies", "Pathfinding", "", "Tony.X()", "Tony.Y()"),
        reset_t("Zombies", "ruta")]),
    ev([vtxt("Zombies", "Estado", "paseando"), timer_ok("Zombies", "paseo", 4)],
       [a("PathfindingBehavior::SetDestination", "Zombies", "Pathfinding", "",
          "Zombies.X() + RandomInRange(-160, 160)", "Zombies.Y() + RandomInRange(-160, 160)"),
        reset_t("Zombies", "paseo")]),
    foreach("Zombies", [vtxt("Zombies", "Estado", "persigue"),
                        c("PathfindingBehavior::PathFound", "Zombies", "Pathfinding", invertida=True)],
            [a("AddForceVersPos", "Zombies", "Tony.X()", "Tony.Y()", "Zombies.Variable(Velocidad) * 0.8", "0")]),
    foreach("ZGriton", [vtxt("ZGriton", "Estado", "persigue"), vnum("ZGriton", "Grito", "=", 0)],
            [setn("ZGriton", "Grito", "=", 1), a("SetAnimationName", "ZGriton", "\"gritar\""),
             reset_t("ZGriton", "ataque")],
            [ev([c("Distance", "Zombies", "ZGriton", "450"), vtxt("Zombies", "Estado", "muerto", inv=True)],
                [sett("Zombies", "Estado", "\"persigue\"")])]),
    ev([vtxt("Zombies", "Estado", "persigue"), c("Distance", "Zombies", "Tony", "80"),
        timer_ok("Zombies", "ataque", 1), VIVO],
       [reset_t("Zombies", "ataque"), setn("Tony", "Vida", "-", "Zombies.Variable(Danio)"),
        a("ChangeColor", "Tony", "\"255;110;110\""), reset_t("Tony", "tinte")], sub=
       anim_dir("Zombies", "(Tony.X() - Zombies.X())", "(Tony.Y() - Zombies.Y())", "atacar")),
    foreach("Zombies", [vtxt("Zombies", "Estado", "muerto", inv=True), timer_ok("Zombies", "ataque", 0.45),
                        cmp("Zombies.Pathfinding::Speed()", ">", "1")], [],
            anim_dir("Zombies", ZX, ZY, "caminar")),
    ev([c("CollisionNP", "Tony", "ZGordo", "", ""), vtxt("ZGordo", "Estado", "muerto", inv=True)],
       [a("AddForceVersPos", "Tony", "ZGordo.X()", "ZGordo.Y()", "-220", "0")]),
    ev([c("CollisionNP", "Tony", "ZConserje", "", ""), vtxt("ZConserje", "Estado", "muerto", inv=True)],
       [a("AddForceVersPos", "Tony", "ZConserje.X()", "ZConserje.Y()", "-220", "0")]),
    ev([vnum("Zombies", "Vida", "<=", 0), vtxt("Zombies", "Estado", "muerto", inv=True)],
       [sett("Zombies", "Estado", "\"muerto\""), a("SetAnimationName", "Zombies", "\"golpe_morir\""),
        a("ActivateBehavior", "Zombies", "Pathfinding", "no"), a("ModVarScene", "Tumbados", "+", "1"),
        a("ModVarScene", "OroJefe", "+", "Zombies.Variable(Oro)")]),
    ev([vtxt("Zombies", "Estado", "muerto"), c("AnimationEnded", "Zombies")], [a("Delete", "Zombies", "")]),
    ev([timer_ok("Zombies", "tinte", 0.12)], [a("ChangeColor", "Zombies", "\"255;255;255\"")]),
    ev([], [a("SeparateFromObjects", "Zombies", "Solidos", ""), a("ChangePlan", "Zombies", "=", "Zombies.Y()")]),
    ev([vtxt("Zombies", "Estado", "muerto", inv=True), VIVO], [a("SeparateFromObjects", "Tony", "Zombies", "")]),
])

g_vida = grupo("Tony: vida y caída", [
    comentario("Con 0 de vida cae (cuadro 4 de caer_levantarse). Revivir con compañeros: fase 5. "
               "Depuración: U lo levanta con vida llena."),
    ev([timer_ok("Tony", "tinte", 0.15)], [a("ChangeColor", "Tony", "\"255;255;255\"")]),
    ev([vnum("Tony", "Vida", "<=", 0), VIVO],
       [sett("Tony", "Estado", "\"caido\""), setn("Tony", "Vida", "=", 0),
        a("SetAnimationName", "Tony", "\"caer_levantarse\""), a("ActivateBehavior", "Tony", "TopDownMovement", "no")]),
    ev([vtxt("Tony", "Estado", "caido"), c("Sprite", "Tony", ">=", "3")], [a("PauseAnimation", "Tony")]),
])

g_inf = grupo("Infestación", [
    comentario("Sube un nivel cada 95 s hasta 5. Zombies paseando: 10/15/22/30/40. "
               "Nivel 2: corredores. Nivel 3+: gordos y gritones. Salen de las rejillas lejos de la cámara."),
    ev([c("DepartScene", "")], [a("ResetTimer", "", "\"infest\""), a("ResetTimer", "", "\"spawn\""),
                                a("ModVarScene", "Infestacion", "=", "1")]),
    ev([c("CompareTimer", "", "\"infest\"", ">=", "95"), c("VarScene", "Infestacion", "<", "5")],
       [a("ModVarScene", "Infestacion", "+", "1"), a("ResetTimer", "", "\"infest\"")]),
] + [ev([c("VarScene", "Infestacion", "=", str(n))],
        [a("ModVarScene", "ObjZombies", "=", str(o)), a("ModVarScene", "MaxTipo", "=", str(m))])
     for n, o, m in [(1, 10, 6), (2, 15, 8), (3, 22, 10), (4, 30, 10), (5, 40, 10)]] + [
    ev([c("CompareTimer", "", "\"spawn\"", ">=", "2"),
        cmp("SceneInstancesCount(Zombies)", "<", "Variable(ObjZombies)")],
       [a("ResetTimer", "", "\"spawn\""),
        a("ModVarScene", "R", "=", f"RandomInRange(0, {len(datos['marcadores']['rejillas_jefe']) - 1})"),
        a("ModVarScene", "R2", "=", "RandomInRange(1, Variable(MaxTipo))")], sub=[
        ev([vtxt("Marcador", "Tipo", "salida_zombie"), vnum("Marcador", "Indice", "=", "Variable(R)"),
            cmp("abs(Marcador.X() - CameraX()) + abs(Marcador.Y() - CameraY())", ">", "1300")], [], sub=[
            ev([c("VarScene", "R2", "<=", "6")],
               [a("Create", "", "ZNormal", "Marcador.X() + 16", "Marcador.Y() + 32", "\"Juego\""),
                sett("ZNormal", "Estado", "\"persigue\"")]),
            ev([c("VarScene", "R2", ">=", "7"), c("VarScene", "R2", "<=", "8")],
               [a("Create", "", "ZCorredor", "Marcador.X() + 16", "Marcador.Y() + 32", "\"Juego\""),
                sett("ZCorredor", "Estado", "\"persigue\"")]),
            ev([c("VarScene", "R2", "=", "9")],
               [a("Create", "", "ZGordo", "Marcador.X() + 16", "Marcador.Y() + 32", "\"Juego\""),
                sett("ZGordo", "Estado", "\"persigue\"")]),
            ev([c("VarScene", "R2", "=", "10")],
               [a("Create", "", "ZGriton", "Marcador.X() + 16", "Marcador.Y() + 32", "\"Juego\""),
                sett("ZGriton", "Estado", "\"persigue\"")]),
        ]),
    ]),
])

# Animación por dirección de Tony: solo si está de pie y no está pegando
NOMBRES_G = {"Armas del salón", "Combate: pegar (clic hacia el cursor)", "Zombies: IA, ataque y muerte",
             "Tony: vida y caída", "Infestación"}
evs = [e for e in esc["events"] if e.get("name") not in NOMBRES_G]
for e in evs:
    if e.get("name") == "Animación por dirección":
        for sub in e["events"]:
            if sub.get("type") == "BuiltinCommonInstructions::Standard":
                sub["conditions"] = [x for x in sub["conditions"] if x["type"]["value"] not in ("VarObjetTxt", "VarObjet")]
                sub["conditions"] += [VIVO, vnum("Tony", "Atacando", "=", 0)]
    if e.get("name") == "Depuración (quitar antes de presentar)":
        e["events"] = [x for x in e["events"] if "DEP4" not in json.dumps(x)]
        e["events"] += [
            ev([], [a("TextObject::String", "TxtDebug", "=",
                "\"Tony \" + Tony.VariableString(Estado) + \"  vida \" + ToString(Tony.Variable(Vida)) + "
                "\"  arma \" + Tony.VariableString(Arma) + \" (\" + ToString(Tony.Variable(Usos)) + \")\" + "
                "\"   infestación \" + ToString(Variable(Infestacion)) + \"   zombies \" + "
                "ToString(SceneInstancesCount(Zombies)) + \"   tumbados \" + ToString(Variable(Tumbados)) + "
                "\"   [golpe ang \" + ToString(round(Variable(DbgAng))) + \" dist \" + ToString(round(Variable(DbgDist))) + \"]\"")]),
            comentario("DEP4 · U: levantar a Tony con vida llena · Z: zombie normal cerca · N: subir infestación"),
            ev([c("KeyPressed", "", "u"), c("BuiltinCommonInstructions::Once")],
               [sett("Tony", "Estado", "\"normal\""), setn("Tony", "Vida", "=", "Tony.Variable(VidaMax)"),
                a("ActivateBehavior", "Tony", "TopDownMovement", "yes"), a("PlayAnimation", "Tony")]),
            ev([c("KeyPressed", "", "z"), c("BuiltinCommonInstructions::Once")],
               [a("Create", "", "ZNormal", "Tony.X() + 300", "Tony.Y()", "\"Juego\"")]),
            ev([c("KeyPressed", "", "n"), c("BuiltinCommonInstructions::Once"), c("VarScene", "Infestacion", "<", "5")],
               [a("ModVarScene", "Infestacion", "+", "1"), a("ResetTimer", "", "\"infest\"")]),
        ]
i_mapa = next(k for k, e in enumerate(evs) if e.get("name") == "Mapa: ayudas y choques")
evs[i_mapa + 1:i_mapa + 1] = [g_armas, g_pegar, g_zombies, g_vida, g_inf]
esc["events"] = evs
json.dump(p, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("OK fase 4:", len(nuevos), "objetos,", sum(1 for i in esc["instances"] if i["name"] in NOMBRES), "instancias")
