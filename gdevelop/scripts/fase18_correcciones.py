"""Fase 18 de FDI-Z (13 nov 2026): correcciones pedidas por Tony. Se aplica SOBRE el FDI-Z.json actual (no regenera nada).
Es idempotente. Correr con GDevelop cerrado (o recargar sin guardar):
    python fase18_correcciones.py <FDI-Z.json>

1. Los personajes de pie ya no chocan entre si (se quita SeparateFromObjects Sup contra Sup).
2. Efecto de golpe: sale pegado al punio, solo cuando el brazo ya esta extendido, y en la direccion de la animacion
   (arriba / abajo / lado). El arco anterior (objeto Golpe) queda como zona de dano invisible.
3. Selector de personaje: marco amarillo (el mismo de las tarjetas de modo) alrededor del video de cada personaje.
4. Bugs de IA: (a) los bots no se apilan en el mismo punto: se separan entre ellos, pero nunca empujan al jugador;
   (b) los zombis no se apilan entre si; (c) los zombis quietos ya no "caminan en su lugar": quedan de pie (cuadro 0)
   mirando al superviviente mas cercano y reanudan la animacion al moverse o atacar.
"""
import copy, json, os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gd_util import c, a, ev, grupo, comentario, var, res_imagen, animacion, objeto_sprite

ruta = sys.argv[1]
RAIZ = os.path.dirname(os.path.abspath(ruta))
p = json.load(open(ruta, encoding="utf-8"))

def lay(n): return next(l for l in p["layouts"] if l["name"] == n)
def es_grupo(e, nombre): return e.get("type", "").endswith("Group") and e.get("name") == nombre
def cmp(e1, op, e2): return c("BuiltinCommonInstructions::CompareNumbers", e1, op, e2)
def vnum(o, v, op, val): return c("VarObjet", o, v, op, str(val))
def setn(o, v, op, val): return a("ModVarObjet", o, v, op, str(val))
def timer_ok(o, t, seg): return c("CompareObjectTimer", o, f"\"{t}\"", ">=", str(seg))
def reset_t(o, t): return a("ResetObjectTimer", o, f"\"{t}\"")
def foreach(obj, conds, acts, sub=None):
    return {"type": "BuiltinCommonInstructions::ForEach", "object": obj, "conditions": conds, "actions": acts, "events": sub or []}

J = lay("Juego")

# ---------- 1. sin colision entre personajes ----------
def quitar_sep(evs):
    n = 0
    for e in list(evs):
        if e.get("fdiz18"):
            continue                                    # la separacion entre bots (punto 4a) es nuestra
        acts = e.get("actions", [])
        k = [x for x in acts if x["type"]["value"] == "SeparateFromObjects" and x["parameters"][:2] == ["Sup", "Sup"]]
        if k:
            e["actions"] = [x for x in acts if x not in k]
            n += len(k)
            if not e["actions"] and not e.get("events"):
                evs.remove(e)
        n += quitar_sep(e.get("events", []))
    return n
print("colision Sup-Sup quitada:", quitar_sep(J["events"]))

# ---------- 2. efecto de golpe pegado al punio ----------
# desplazamiento del punio respecto a los pies del personaje (Sup.X(), Sup.Y()) en el cuadro con el brazo extendido
DIRS = {  # nombre: (condiciones, offx, offy, angulo del efecto)
    "der": ([cmp("abs(Sup.Variable(AimX))", ">", "abs(Sup.Variable(AimY))"), cmp("Sup.Variable(AimX)", ">=", "0")], 46, -62, 180),
    "izq": ([cmp("abs(Sup.Variable(AimX))", ">", "abs(Sup.Variable(AimY))"), cmp("Sup.Variable(AimX)", "<", "0")], -46, -62, 0),
    "arr": ([cmp("abs(Sup.Variable(AimX))", "<=", "abs(Sup.Variable(AimY))"), cmp("Sup.Variable(AimY)", "<", "0")], 10, -106, 90),
    "aba": ([cmp("abs(Sup.Variable(AimX))", "<=", "abs(Sup.Variable(AimY))"), cmp("Sup.Variable(AimY)", ">=", "0")], 16, -40, 270),
}
if not any(o["name"] == "GolpeFx" for o in J["objects"]):
    golpe = next(o for o in J["objects"] if o["name"] == "Golpe")
    fx = copy.deepcopy(golpe)
    fx["name"] = "GolpeFx"
    fx["variables"] = [var("Jugador", 0), var("OffX", 0), var("OffY", 0)]
    for an in fx["animations"]:
        for d in an["directions"]:
            for s in d["sprites"]:
                s["originPoint"] = {"name": "origine", "x": 16, "y": 15}
    J["objects"].append(fx)

grp = next(e for e in J["events"] if es_grupo(e, "Combate: pegar"))
ataque = grp["events"][0]
assert ataque["type"].endswith("ForEach") and ataque["object"] == "Sup"
if not any(x["type"]["value"] == "Create" and x["parameters"][1] == "GolpeFx" for x in ataque["actions"]):
    ataque["actions"].append(a("Create", "", "GolpeFx", "Sup.X()", "Sup.Y()", "\"Juego\""))
    base = ataque["events"][0]            # el evento que fija angulo/escala/danio del Golpe
    base["actions"].append(a("Cache", "Golpe"))          # el arco viejo queda solo como zona de dano
    ataque["events"].append(ev([], [setn("GolpeFx", "Jugador", "=", "Sup.Variable(Jugador)"),
                                     a("ChangeScale", "GolpeFx", "=", "1.2 * Sup.Variable(Alcance)"),
                                     a("Cache", "GolpeFx"), reset_t("GolpeFx", "vida")]))
    for nombre, (conds, ox, oy, ang) in DIRS.items():
        ataque["events"].append(ev(conds, [setn("GolpeFx", "OffX", "=", ox), setn("GolpeFx", "OffY", "=", oy),
                                           a("SetAngle", "GolpeFx", "=", ang)]))

J["events"] = [e for e in J["events"] if not es_grupo(e, "Golpe: efecto en el punio")]
efectos = grupo("Golpe: efecto en el punio", [
    comentario("El efecto sigue al personaje y se muestra solo mientras el brazo esta extendido (0.06 a 0.22 s del golpe)."),
    foreach("GolpeFx", [], [], sub=[
        ev([vnum("Sup", "Jugador", "=", "GolpeFx.Variable(Jugador)")],
           [a("MettreXY", "GolpeFx", "=", "Sup.X() + GolpeFx.Variable(OffX)", "=", "Sup.Y() + GolpeFx.Variable(OffY)"),
            a("ChangePlan", "GolpeFx", "=", "Sup.Y() + 5")])]),
    ev([timer_ok("GolpeFx", "vida", 0.06)], [a("Montre", "GolpeFx", "")]),
    ev([timer_ok("GolpeFx", "vida", 0.22)], [a("Delete", "GolpeFx", "")]),
])
J["events"].insert(J["events"].index(grp) + 1, efectos)

# ---------- 3. marco amarillo en el video de cada personaje (selector) ----------
M = lay("Menu")
src = Image.open(os.path.join(RAIZ, "assets/interfaz/ui_ranura_retrato.png")).convert("RGBA")
W, H = src.size
mg, AN, AL = 38, 630, 650
out = Image.new("RGBA", (AN, AL))
xs = [(0, mg, 0, mg), (mg, W - mg, mg, AN - mg), (W - mg, W, AN - mg, AN)]
ys = [(0, mg, 0, mg), (mg, H - mg, mg, AL - mg), (H - mg, H, AL - mg, AL)]
for i, (sx0, sx1, dx0, dx1) in enumerate(xs):
    for j, (sy0, sy1, dy0, dy1) in enumerate(ys):
        if i == 1 and j == 1:
            continue                                    # centro transparente: se ve el video
        out.paste(src.crop((sx0, sy0, sx1, sy1)).resize((dx1 - dx0, dy1 - dy0), Image.NEAREST), (dx0, dy0))
rel = "assets/interfaz/hud/p9_EqMarcoVideo.png"
out.save(os.path.join(RAIZ, rel))
if not any(r["name"] == "p18_EqMarcoVideo" for r in p["resources"]["resources"]):
    p["resources"]["resources"].append(res_imagen("p18_EqMarcoVideo", rel))
o = next(o for o in M["objects"] if o["name"] == "EqMarcoGrande")
o["animations"][0]["directions"][0]["sprites"][0]["image"] = "p18_EqMarcoVideo"
for i in M["instances"]:
    if i["name"] == "EqMarcoGrande":
        i["zOrder"] = 5                                 # encima del video (z 4)

# ---------- 4. bugs de zombis y bots ----------
TAG = "fdiz18"
def sin_tag(evs):
    return [e for e in evs if not e.get(TAG)]
def marca(e):
    e[TAG] = True
    return e
def vtxt(o, v, val, inv=False): return c("VarObjetTxt", o, v, "=", f"\"{val}\"", invertida=inv)

# 4a) bots: ya no empujan ni bloquean a los jugadores, pero entre ellos no se encimen (si no se apilan en el mismo pixel)
choques = next(e for e in J["events"] if es_grupo(e, "Mapa: choques y puertas"))
choques["events"] = sin_tag(choques["events"])
choques["events"].insert(1, marca(ev([c("VarObjet", "Sup", "Control", "=", "-1"), vtxt("Sup", "Estado", "normal")],
                                     [a("SeparateFromObjects", "Sup", "Sup", "")])))

# 4a-bis) en pasillos angostos la separacion lateral choca con las paredes y los bots terminaban en el mismo punto:
# cada bot se detiene a una distancia distinta del guia (J2 180 px, J3 225, J4 270) y asi quedan en fila.
DIST_SEG = "DistanceBetweenPositions(Sup.X(), Sup.Y(), Variable(SegX), Variable(SegY))"
n_seg = 0
def ajustar_seg(evs):
    global n_seg
    for e in evs:
        for cnd in e.get("conditions", []):
            pr = cnd["parameters"]
            if cnd["type"]["value"] == "BuiltinCommonInstructions::CompareNumbers" and pr[0] == DIST_SEG and pr[1] == ">" \
               and pr[2] in ("160", "90 + 45 * Sup.Variable(Jugador)"):
                pr[2] = "90 + 45 * Sup.Variable(Jugador)"; n_seg += 1
        ajustar_seg(e.get("events", []))
ajustar_seg(J["events"])
print("distancia de seguimiento por bot ajustada en", n_seg, "evento(s)")

# 4b) zombis: no se apilan entre si
zg = next(e for e in J["events"] if e.get("name", "").startswith("Zombies: IA"))
zg["events"] = sin_tag(zg["events"])
pos = next(i for i, e in enumerate(zg["events"])
           if any(x["type"]["value"] == "SeparateFromObjects" and x["parameters"][:2] == ["Zombies", "Solidos"] for x in e.get("actions", [])))
zg["events"].insert(pos, marca(ev([vtxt("Zombies", "Estado", "muerto", inv=True)],
                                  [a("SeparateFromObjects", "Zombies", "Zombies", "")])))

# 4c) zombis quietos ya no "caminan en su lugar": se quedan en el cuadro 0 de la caminata (pose de pie), mirando al jugador
def anim_z(dx, dy, pre):
    return [
        ev([cmp(f"abs({dx})", ">", f"abs({dy})")], [a("SetAnimationName", "Zombies", f"\"{pre}_lado\"")], sub=[
            ev([cmp(dx, "<", "0")], [a("FlipX", "Zombies", "yes")]), ev([cmp(dx, ">=", "0")], [a("FlipX", "Zombies", "no")])]),
        ev([cmp(f"abs({dx})", "<=", f"abs({dy})"), cmp(dy, "<", "0")], [a("SetAnimationName", "Zombies", f"\"{pre}_arriba\""), a("FlipX", "Zombies", "no")]),
        ev([cmp(f"abs({dx})", "<=", f"abs({dy})"), cmp(dy, ">=", "0")], [a("SetAnimationName", "Zombies", f"\"{pre}_abajo\""), a("FlipX", "Zombies", "no")]),
    ]
VIVO_Z = vtxt("Zombies", "Estado", "muerto", inv=True)
QUIETO = cmp("Zombies.Pathfinding::Speed()", "<=", "1")
LIBRE = timer_ok("Zombies", "ataque", 0.45)
zg["events"].append(marca(ev([VIVO_Z, vtxt("Zombies", "Estado", "persigue"), QUIETO, LIBRE, vtxt("Sup", "Estado", "normal"),
                              c("PickNearest", "Sup", "Zombies.X()", "Zombies.Y()", "")], [],
                             sub=anim_z("(Sup.X() - Zombies.X())", "(Sup.Y() - Zombies.Y())", "caminar"))))
zg["events"].append(marca(ev([VIVO_Z, QUIETO, LIBRE, c("Sprite", "Zombies", "=", "0")], [a("PauseAnimation", "Zombies")])))
zg["events"].append(marca(ev([VIVO_Z, cmp("Zombies.Pathfinding::Speed()", ">", "1")], [a("PlayAnimation", "Zombies")])))
zg["events"].append(marca(ev([VIVO_Z, c("CompareObjectTimer", "Zombies", "\"ataque\"", "<", "0.45")], [a("PlayAnimation", "Zombies")])))

json.dump(p, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("OK fase 18: sin colision entre personajes, efecto de golpe en el punio, marco amarillo, zombis y bots")
