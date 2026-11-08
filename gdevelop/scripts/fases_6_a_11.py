"""Fases 6 a 11 de FDI-Z. Correr DESPUÉS de fase5_jugadores.py (con GDevelop cerrado):
    python fases_6_a_11.py <FDI-Z.json> <mapa_fdiz_datos.json> <carpeta assets extra generados>
Agrega a la escena Juego: niebla por zonas, tipos de puerta y puertas que se tumban, objetivos al azar con flecha,
final "¡Aguanten!", rescates de Joel y Justino, Canepa, habilidades/especiales/pasivas de los 8 personajes, HUD,
dificultad, cinemática de inicio, modo Jefe de zombies, ambiente (luces, destrozos), eventos de sonido (apagados
hasta que existan los audios: variable global SonidoActivo) y modo presentación (F1).
Crea las escenas Titulo, Menu y Resultados.
"""
import json, os, sys, random, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gd_util import *

ruta, datos_json = sys.argv[1:3]
p = json.load(open(ruta, encoding="utf-8"))
datos = json.load(open(datos_json, encoding="utf-8"))
esc = next(l for l in p["layouts"] if l["name"] == "Juego")
M = datos["marcadores"]
GEN = "../../generado/sprites/"

# ---------------- helpers ----------------
def cmp(e1, op, e2): return c("BuiltinCommonInstructions::CompareNumbers", e1, op, e2)
def vtxt(o, v, val, inv=False): return c("VarObjetTxt", o, v, "=", f"\"{val}\"", invertida=inv)
def vnum(o, v, op, val): return c("VarObjet", o, v, op, str(val))
def setn(o, v, op, val): return a("ModVarObjet", o, v, op, str(val))
def sett(o, v, val): return a("ModVarObjetTxt", o, v, "=", val)
def svar(v, op, val): return a("ModVarScene", v, op, str(val))
def cvar(v, op, val): return c("VarScene", v, op, str(val))
def svt(v, val): return a("ModVarSceneTxt", v, "=", val)
def cvt(v, val, op="="): return c("VarSceneTxt", v, op, val)
def gset(v, op, val): return a("ModVarGlobal", v, op, str(val))
def gsett(v, val): return a("ModVarGlobalTxt", v, "=", val)
def gnum(v, op, val): return c("VarGlobal", v, op, str(val))
def gtxt(v, val, op="="): return c("VarGlobalTxt", v, op, val)
def timer_ok(o, t, seg): return c("CompareObjectTimer", o, f"\"{t}\"", ">=", str(seg))
def reset_t(o, t): return a("ResetObjectTimer", o, f"\"{t}\"")
def stimer(t, seg): return c("CompareTimer", "", f"\"{t}\"", ">=", str(seg))
def sreset(t): return a("ResetTimer", "", f"\"{t}\"")
def suelta(k): return c("KeyReleased", "", k)
def pad_suelta(k, b): return c("Gamepads::C_Button_released", "", str(k), f"\"{b}\"", "")
def once(): return c("BuiltinCommonInstructions::Once")
def o_(*conds): return {"type": {"value": "BuiltinCommonInstructions::Or"}, "parameters": [], "subInstructions": list(conds)}
def foreach(obj, conds, acts, sub=None):
    return {"type": "BuiltinCommonInstructions::ForEach", "object": obj, "conditions": conds, "actions": acts, "events": sub or []}
def crear(obj, x, y, capa="Juego"): return a("Create", "", obj, str(x), str(y), f"\"{capa}\"")
def texto(o, expr): return a("TextObject::String", o, "=", expr)
def sonido(nombre, vol=80):   # quedan listos con el nombre de la lista de sonidos; suenan cuando SonidoActivo = 1
    return ev([gnum("SonidoActivo", "=", 1)], [a("PlaySound", "", f"\"{nombre}\"", "", str(vol), "1")])
def banner(txt, seg=2.5): return [svt("Banner", f"\"{txt}\""), sreset("banner"), svar("BannerSeg", "=", seg)]
VIVO = vtxt("Sup", "Estado", "normal")

def centrar(objetos):
    """Los textos con alineación centrada se colocan a mitad de pantalla (GDevelop centra las líneas dentro del bloque,
    pero el bloque empieza en la X de la instancia)."""
    return [ev([], [a("MettreX", o["name"], "=", f"960 - {o['name']}.Width() / 2") for o in objetos
                    if o.get("type") == "TextObject::Text" and o["content"].get("textAlignment") == "center"])]
def obj_texto(nombre, tam=32, color="255;255;255", alin="left", txt=""):
    return {"assetStoreId": "", "name": nombre, "type": "TextObject::Text", "variables": [var("Jugador", 0)], "effects": [],
            "behaviors": [], "content": {"bold": True, "isOutlineEnabled": True, "isShadowEnabled": False, "italic": False,
            "outlineColor": "0;0;0", "outlineThickness": 4, "shadowAngle": 90, "shadowBlurRadius": 2, "shadowColor": "0;0;0",
            "shadowDistance": 4, "shadowOpacity": 127, "smoothed": False, "underlined": False, "text": txt, "font": "",
            "textAlignment": alin, "verticalTextAlignment": "top", "characterSize": tam, "lineHeight": 0, "color": color}}

recursos = {r["name"]: r for r in p["resources"]["resources"]}
def img(nombre, archivo):
    recursos[nombre] = res_imagen(nombre, archivo)
    return nombre

# ---------------- variables globales ----------------
GLOBALES = [var("SonidoActivo", 0), var("Modo", "escape"), var("Dificultad", "normal"), var("DifInf", 1), var("DifVida", 1),
            var("DifDanio", 1), var("DifHorda", 1), var("Listo", 0), var("VioIntro", 0), var("Resultado", ""),
            var("TiempoFinal", 0), var("Premios", ""), var("SinRecord", 0), var("Demo", 0), var("MejorTiempo", 0)]
for k in range(1, 5):
    GLOBALES += [var(f"P{k}Pj", ""), var(f"P{k}Ctl", -1)]
p["variables"] = [v for v in p["variables"] if v["name"] not in {g["name"] for g in GLOBALES}] + GLOBALES

# ---------------- objetos nuevos de Juego ----------------
EXTRA = "assets/extra/"
nuevos = []
def sprite_simple(nombre, anims, variables=()):
    o = objeto_sprite(nombre, [animacion(n, [img(r, f)], 1, False, org) for n, r, f, org in anims], variables)
    nuevos.append(o); return o
sprite_simple("Objetivo", [
    ("servidor", "extra/servidor.png", EXTRA + "servidor.png", (24, 64)),
    ("computadora", "objetos/props_especiales/laptop.png", GEN + "objetos/props_especiales/laptop.png", (16, 32)),
    ("llaves", "objetos/objetivos/llaves_conserjeria.png", GEN + "objetos/objetivos/llaves_conserjeria.png", (16, 32)),
    ("camion", "extra/punto.png", EXTRA + "punto.png", (32, 32)),
    ("interruptor", "extra/interruptor.png", EXTRA + "interruptor.png", (12, 40)),
    ("carnada", "extra/punto.png", EXTRA + "punto.png", (32, 32))],
    [var("Tipo", ""), var("Tiempo", 1), var("Progreso", 0), var("Usada", 0), var("Hecho", 0)])
sprite_simple("Bidon", [("bidon", "objetos/objetivos/bidon.png", GEN + "objetos/objetivos/bidon.png", (16, 32))])
sprite_simple("Bolsa", [("bolsa", "objetos/comida/bolsa_comida.png", GEN + "objetos/comida/bolsa_comida.png", (16, 32))])
sprite_simple("Comida", [("hamburguesa", "objetos/comida/hamburguesa.png", GEN + "objetos/comida/hamburguesa.png", (16, 32)),
                         ("torta", "objetos/comida/torta.png", GEN + "objetos/comida/torta.png", (16, 32)),
                         ("galletas", "objetos/comida/galletas.png", GEN + "objetos/comida/galletas.png", (16, 32)),
                         ("jugo", "objetos/comida/jugo.png", GEN + "objetos/comida/jugo.png", (16, 32))],
              [var("Cura", 40)])
sprite_simple("Aparato", [("celular", "objetos/props_especiales/celular.png", GEN + "objetos/props_especiales/celular.png", (16, 16)),
                          ("audifonos", "objetos/props_especiales/audifonos.png", GEN + "objetos/props_especiales/audifonos.png", (16, 16)),
                          ("tablet", "objetos/props_especiales/tablet.png", GEN + "objetos/props_especiales/tablet.png", (16, 16))])
# efectos de habilidad y especial de cada personaje (atlas: efectos/<pj>/efecto_habilidad|efecto_especial)
_atlas_ef = json.load(open(os.path.join(os.path.dirname(datos_json), "..", "..", "generado", "sprites", "atlas.json"), encoding="utf-8"))["entidades"]
_anims_ef = []
for _pj in ["tony", "miranda", "cesar", "alan", "castillo", "alessandro", "gabo", "carlos"]:
    for _t, _n in (("hab", "efecto_habilidad"), ("esp", "efecto_especial")):
        _an = _atlas_ef[f"efectos/{_pj}"]["animaciones"][_n]
        _w, _h = _an["lienzo"]
        _anims_ef.append(animacion(f"{_pj}_{_t}", [img(f, GEN + f) for f in _an["cuadros"]], _an["fps"], True, (_w // 2, _h // 2)))
nuevos.append(objeto_sprite("EfectoPj", _anims_ef, [var("Jugador", 0)]))
sprite_simple("Flecha", [("flecha", "extra/flecha.png", EXTRA + "flecha.png", (24, 24))])
sprite_simple("Profe", [("joel", "extra/joel.png", EXTRA + "joel.png", (40, 94)), ("justino", "extra/justino.png", EXTRA + "justino.png", (40, 94))],
              [var("Nombre", ""), var("Estado", "miedo"), var("Progreso", 0)])
sprite_simple("Minimapa", [("mapa", "extra/minimapa.png", EXTRA + "minimapa.png", (0, 0))])
sprite_simple("Efecto", [("zzz", "objetos/efectos_generales/zzz.png", GEN + "objetos/efectos_generales/zzz.png", (16, 32)),
                         ("estrellas", "objetos/efectos_generales/estrellas_mareo.png", GEN + "objetos/efectos_generales/estrellas_mareo.png", (16, 32)),
                         ("exclamacion", "objetos/efectos_generales/exclamacion.png", GEN + "objetos/efectos_generales/exclamacion.png", (5, 32))])
# Canepa (atlas de profes)
atlas = json.load(open(os.path.join(os.path.dirname(datos_json), "..", "..", "generado", "sprites", "atlas.json"), encoding="utf-8")) \
    if os.path.exists(os.path.join(os.path.dirname(datos_json), "..", "..", "generado", "sprites", "atlas.json")) else None
if atlas:
    e = atlas["entidades"]["profes/canepa"]; w, h = e["lienzo"]
    anims = []
    for n, an in e["animaciones"].items():
        anims.append(animacion(n, [img(f, GEN + f) for f in an["cuadros"]], an["fps"], an["loop"], (w // 2, h - 2)))
    nuevos.append(objeto_sprite("Canepa", anims, [var("Estado", "espera")]))
for n, tam, col, al in [("TxtObjetivo", 34, "255;235;120", "center"), ("TxtBanner", 72, "255;80;80", "center"),
                        ("TxtPanel", 24, "255;255;255", "left"), ("TxtInfest", 26, "255;180;120", "left"),
                        ("TxtPres", 26, "120;255;160", "left"), ("TxtDialogo", 30, "255;255;255", "center"),
                        ("TxtJefe", 26, "255;120;220", "left"), ("TxtAyuda", 22, "200;220;255", "center")]:
    nuevos.append(obj_texto(n, tam, col, al))
NOMBRES = {o["name"] for o in nuevos}
esc["objects"] = [o for o in esc["objects"] if o["name"] not in NOMBRES] + nuevos
for o in esc["objects"]:
    if o["name"].startswith("Z"):
        for v in [var("UltJugador", 0), var("DifOk", 0), var("Paralisis", 0), var("DestX", 0), var("DestY", 0), var("Aliado", 0), var("Contado", 0)]:
            if not any(x["name"] == v["name"] for x in o["variables"]):
                o["variables"].append(v)
    if o["name"] == "Puerta":
        o["variables"] = [v for v in o["variables"] if v["name"] != "Golpeada"] + [var("Golpeada", 0)]
    if o["name"] == "Golpe":
        o["variables"] = [v for v in o["variables"] if v["name"] != "Hecho"] + [var("Hecho", 0)]
p["resources"]["resources"] = list(recursos.values())

# variables de escena nuevas
NV = {"ZonasAbiertas": ",", "O1": "", "O2": "", "O3": "", "ObjNum": 1, "ObjTipo": "", "ObjIni": 0, "ObjX": 0, "ObjY": 0,
      "Paso": 0, "Bidones": 0, "Interruptores": 0, "TieneBolsa": 0, "FinalActivo": 0, "Banner": "", "BannerSeg": 0,
      "Dinero": 0, "ObjDentro": 0, "IntroPuerta": 0, "Rescatados": 0, "Tiempo": 0, "IntroPaso": 0, "Carta": 1, "Jefe": 0, "Apagon": 0, "Pres": 0,
      "VidaInf": 0, "Luz": 1, "R3": 0, "Horda": 0, "Tarjeta": 0, "CartaTxt": "", "VidaInfTxt": "", "JefeTxt": "", "InfBar": "", "SegTxt": ""}
for k in range(1, 5):
    NV[f"J{k}Txt"] = ""; NV[f"J{k}Kills"] = 0; NV[f"J{k}Caidas"] = 0
esc["variables"] = [v for v in esc["variables"] if v["name"] not in NV] + [var(k, v) for k, v in NV.items()]

# instancias fijas
esc["instances"] = [i for i in esc["instances"] if i["name"] not in NOMBRES]
def inst(o, x, y, capa="Juego", z=0, **kv):
    i = instancia(o, x, y, capa, z, variables=[var(k, v) for k, v in kv.items()]); esc["instances"].append(i); return i
inst("TxtObjetivo", 960, 18, "HUD", 10); inst("TxtBanner", 960, 380, "HUD", 11); inst("TxtInfest", 20, 1040, "HUD", 10)
inst("TxtPres", 640, 200, "HUD", 20); inst("TxtDialogo", 960, 860, "HUD", 12); inst("TxtJefe", 20, 980, "HUD", 10)
inst("TxtAyuda", 960, 70, "HUD", 10)
for k, (x, y) in enumerate([(20, 150), (1500, 150), (20, 880), (1500, 880)], 1):
    inst("TxtPanel", x, y, "HUD", 10, Jugador=k)
inst("Flecha", -100, -100, "HUD", 9)
mm = inst("Minimapa", 1920 - 668, 1080 - 418, "HUD", 5); mm["customSize"] = True; mm["width"] = 640; mm["height"] = 392
for nombre, key in [("joel", "joel_rescate"), ("justino", "justino_rescate")]:
    i = inst("Profe", M[key]["x"], M[key]["y"], "Juego", int(M[key]["y"]), Nombre=nombre)
    i["numberProperties"] = [{"name": "animation", "value": 0 if nombre == "joel" else 1}]
if atlas:
    inst("Canepa", M["canepa"]["x"], M["canepa"]["y"], "Juego", int(M["canepa"]["y"]))
# horda dormida de la explanada (se va a comer cuando cumplen la carnada)
hx, hy, hr = M["horda_explanada"]["x"], M["horda_explanada"]["y"], M["horda_explanada"]["radio"]
random.seed(7)
esc["instances"] = [i for i in esc["instances"] if not (i["name"] == "ZNormal" and any(v.get("value") == "horda" for v in i["initialVariables"]))]
for k in range(8):
    ang = k * 0.785
    i = instancia("ZNormal", int(hx + hr * 0.8 * __import__("math").cos(ang)), int(hy + 40 + hr * 0.5 * __import__("math").sin(ang)), "Juego", 0,
                  variables=[var("Estado", "horda")])
    esc["instances"].append(i)
# marcadores de destrozo (todavía no hay sprites): 40 puntos dentro de zonas
esc["instances"] = [i for i in esc["instances"] if not (i["name"] == "Marcador" and any(v.get("value") == "destrozo" for v in i["initialVariables"]))]
for k in range(40):
    z = random.choice(datos["zonas"])
    esc["instances"].append(instancia("Marcador", z["x"] + random.randint(30, max(31, z["w"] - 30)), z["y"] + random.randint(60, max(61, z["h"] - 20)),
                                      "Juego", 0, 24, 24, variables=[var("Tipo", "destrozo"), var("Zona", z["nombre"]),
                                      var("Nota", random.choice(["vidrios rotos", "pupitre volteado", "mochila tirada", "papeles",
                                                                 "celular en el piso", "mancha verde"]))]))

# ---------------- eventos ----------------
EV = esc["events"]
G = []   # grupos nuevos

# ===== Configuración desde el menú, dificultad y estado =====
cfg = [comentario("Lee lo que se eligió en el Menú (variables globales). Si se abre Juego directo, usa el equipo de prueba.")]
for k in range(1, 5):
    cfg.append(ev([c("DepartScene", ""), gnum("Listo", "=", 1), vnum("Sup", "Jugador", "=", k)],
                  [sett("Sup", "Personaje", f"GlobalVariableString(P{k}Pj)"), setn("Sup", "Control", "=", f"GlobalVariable(P{k}Ctl)")]))
cfg += [
    # GDevelop: un temporizador que nunca se inició no cuenta, así que se arrancan todos al empezar.
    ev([c("DepartScene", "")], [sreset(t) for t in ("olafinal", "oro", "parpadeo", "carta8", "ayuda", "banner", "golpepuerta")]),
    ev([c("DepartScene", ""), gtxt("Modo", "\"jefe\""), vnum("Sup", "Jugador", "=", 4)], [a("Delete", "Sup", "")]),
    ev([c("DepartScene", ""), gtxt("Modo", "\"jefe\"")], [svar("Jefe", "=", 1), svar("OroJefe", "=", 10)]),
    ev([c("DepartScene", ""), gtxt("Modo", "\"jefe\"", "!=")], [a("Cache", "Minimapa"), a("Cache", "TxtJefe")]),
    ev([c("DepartScene", "")], [sreset("partida"), a("Cache", "Flecha")]),
    ev([vnum("Zombies", "DifOk", "=", 0)], [setn("Zombies", "DifOk", "=", 1),
                                            setn("Zombies", "Vida", "*", "GlobalVariable(DifVida)")]),
    ev([cvt("Estado", "\"juego\"")], [svar("Tiempo", "=", "TimerElapsedTime(\"partida\")")]),
    ev([gnum("Demo", "=", 1), o_(suelta("Return"), suelta("Space"), c("MouseButtonReleased", "", "Left"), *[pad_suelta(k, "A") for k in range(1, 5)])],
       [gset("Demo", "=", 0), gset("Listo", "=", 0), a("Scene", "", "\"Titulo\"", "")]),
]
G.append(grupo("Configuración y dificultad", cfg))

# ===== Niebla por zonas =====
G.append(grupo("Niebla por zonas", [
    comentario("Todo empieza a oscuras. Una zona se descubre (se desvanece en 0.5 s) al abrir su puerta o al entrar alguien."),
    ev([c("DepartScene", "")], [a("ShowLayer", "", "\"Niebla\"")]),
    foreach("Niebla", [vnum("Niebla", "Abierta", "=", 0),
                       cmp("StrFind(VariableString(ZonasAbiertas), \",\" + Niebla.VariableString(Grupo) + \",\")", ">=", "0")],
            [setn("Niebla", "Abierta", "=", 1)]),
    ev([vnum("Niebla", "Abierta", "=", 0), c("CollisionNP", "Sup", "Niebla", "", ""), VIVO], [setn("Niebla", "Abierta", "=", 1)]),
    ev([vnum("Niebla", "Abierta", "=", 1)], [a("Opacity", "Niebla", "-", "510 * TimeDelta()")]),
    ev([vnum("Niebla", "Abierta", "=", 1), c("Opacity", "Niebla", "<=", "0")], [a("Delete", "Niebla", "")]),
]))
for o in esc["objects"]:
    if o["name"] == "Niebla" and not any(v["name"] == "Abierta" for v in o["variables"]):
        o["variables"].append(var("Abierta", 0))

# ===== Puertas: tipos, tarjeta, golpes =====
G.append(grupo("Puertas: tipos y golpes", [
    comentario("Al abrirse una puerta se descubren sus zonas. Toda puerta se puede tumbar a golpes (normal 80, electrónica 100, "
               "restringida 150). Con la tarjeta, las electrónicas se abren en 1 s. Restringidas: Carlos (Llave maestra) o a golpes."),
    foreach("Golpe", [vnum("Golpe", "Hecho", "=", 0)], [setn("Golpe", "Hecho", "=", 1)], sub=[
        foreach("Puerta", [cmp("DistanceBetweenPositions(Puerta.X() + Puerta.Width() / 2, Puerta.Y() + Puerta.Height() / 2, "
                               "Golpe.X() + cos(ToRad(Golpe.Angle())) * 50, Golpe.Y() + sin(ToRad(Golpe.Angle())) * 50)", "<", "90")],
                [setn("Puerta", "Vida", "-", "Golpe.Variable(Danio)"), a("ChangeColor", "Puerta", "\"255;160;160\"")], sub=[sonido("efectos/mundo/puerta_golpe.ogg")]),
    ]),
    # zombies que llegan a una puerta cerrada (las puertas no bloquean el Pathfinding) le pegan hasta tumbarla
    foreach("Zombies", [vtxt("Zombies", "Estado", "persigue"), timer_ok("Zombies", "ataque", 1)], [], sub=[
        ev([c("Distance", "Puerta", "Zombies", "75"), c("PickNearest", "Puerta", "Zombies.X()", "Zombies.Y()", "")],
           [setn("Puerta", "Vida", "-", "Zombies.Variable(Danio)"), a("ChangeColor", "Puerta", "\"255;160;160\""), reset_t("Zombies", "ataque")],
           sub=[sonido("efectos/mundo/puerta_golpe.ogg")])]),
    ev([vnum("Puerta", "Vida", "<=", 0)], [setn("Puerta", "TiempoAbrir", "=", 0.001), setn("Puerta", "Progreso", "=", 1)]),
    ev([cvar("Tarjeta", "=", 1), vtxt("Puerta", "Tipo", "electronica")], [setn("Puerta", "TiempoAbrir", "=", 1)]),
    foreach("Puerta", [cmp("Puerta.Variable(Progreso)", ">=", "Puerta.Variable(TiempoAbrir)"), vnum("Puerta", "TiempoAbrir", ">", 0)],
            [svt("ZonasAbiertas", "VariableString(ZonasAbiertas) + Puerta.VariableString(Zonas) + \",\""), a("Delete", "Puerta", "")],
            [sonido("efectos/mundo/puerta_abrir.ogg")]),
    ev([vtxt("Marcador", "Tipo", "tarjeta_electronica"), c("Distance", "Marcador", "Sup", "60"), VIVO, cvar("Tarjeta", "=", 0)],
       [svar("Tarjeta", "=", 1)] + banner("¡Tarjeta! Las puertas electrónicas abren en 1 s", 2.5)),
]))
# El evento de puertas de la fase 5 borra la puerta sin descubrir zonas: lo cambiamos a "marcar" y aquí se borra.
def recorrer(evs):
    for e in evs:
        yield e
        yield from recorrer(e.get("events", []))
for e in recorrer(EV):
    for acc in e.get("actions", []):
        if acc["type"]["value"] == "Delete" and acc["parameters"][0] == "Puerta":
            acc["type"]["value"] = "ModVarObjet"; acc["parameters"] = ["Puerta", "Usada", "=", "1"]

# ===== Objetivos =====
TIPOS_OBJ = ["llamada", "llaves", "gasolina", "luz", "carnada"]
triples = [t for t in itertools.permutations(TIPOS_OBJ, 3) if t[0] != "luz"]
elegir = [ev([cvar("R3", "=", k)], [svt("O1", f"\"{t[0]}\""), svt("O2", f"\"{t[1]}\""), svt("O3", f"\"{t[2]}\"")]) for k, t in enumerate(triples)]
TXT = {"llamada": "Prendan el servidor del SITE y llamen desde el CIC", "llaves": "Consigan las llaves de la conserjería",
       "gasolina": "Junten 3 bidones de gasolina y llévenlos al camión", "luz": "Suban los 3 interruptores para regresar la luz",
       "carnada": "Lleven comida a la nevería para distraer a la horda"}
def obj_en(tipo_anim, x, y, tiempo):
    return [crear("Objetivo", x, y), sett("Objetivo", "Tipo", f"\"{tipo_anim}\""), setn("Objetivo", "Tiempo", "=", tiempo),
            a("SetAnimationName", "Objetivo", f"\"{tipo_anim}\"")]
cl = M["computadoras_llamada"]; bp = M["bidones_posibles"]; bo = M["bolsa_comida_posible"]
inicio_obj = {
    "llamada": obj_en("servidor", M["servidor_site"]["x"], M["servidor_site"]["y"], 10) + [svar("ExtraZombies", "=", 6)],
    "llaves": obj_en("llaves", M["llaves_conserjeria"]["x"], M["llaves_conserjeria"]["y"], 1),
    "gasolina": [svar("Bidones", "=", 0), svar("R", "=", f"RandomInRange(0, {len(bp) - 1})")],
    "luz": [svar("Interruptores", "=", 0), svar("Apagon", "=", 1)]
           + obj_en("interruptor", M["interruptor_principal"]["x"], M["interruptor_principal"]["y"], 5)
           + obj_en("interruptor", M["interruptor_luz_lab"]["x"], M["interruptor_luz_lab"]["y"], 5)
           + obj_en("interruptor", cl[1]["x"] + 40, cl[1]["y"], 5) + banner("¡SE FUE LA LUZ!", 2.5),
    "carnada": [svar("TieneBolsa", "=", 0), svar("R", "=", f"RandomInRange(0, {len(bo) - 1})")],
}
sub_ini = [ev([cvt("ObjTipo", f"\"{t}\"")], acc) for t, acc in inicio_obj.items()]
# bidones: 3 de los 8 posibles (R, R+3, R+6 mod 8); bolsa: 1 de 3
bid = []
for k in range(len(bp)):
    for off in (0, 3, 6):
        bid.append(ev([cvt("ObjTipo", "\"gasolina\""), cmp(f"mod(Variable(R) + {off}, {len(bp)})", "=", str(k))],
                      [crear("Bidon", bp[k]["x"], bp[k]["y"])]))
for k in range(len(bo)):
    bid.append(ev([cvt("ObjTipo", "\"carnada\""), cvar("R", "=", k)], [crear("Bolsa", bo[k]["x"], bo[k]["y"])]))
sub_ini += bid + [ev([], [svar("ObjIni", "=", 1)] + banner("NUEVO OBJETIVO", 2))] + [sonido("efectos/eventos/objetivo_nuevo.ogg")]

objs = [
    comentario("3 objetivos al azar (la luz nunca es el primero) y luego el final. El texto de arriba dice qué hacer y la "
               "flecha amarilla apunta hacia dónde ir. Cada objetivo cumplido hace reaparecer a los que estaban fuera."),
    ev([c("DepartScene", "")], [svar("R3", "=", f"RandomInRange(0, {len(triples) - 1})"), svar("ObjNum", "=", 1), svar("ObjIni", "=", 0)],
       sub=elegir),
    ev([cvar("ObjNum", "=", 1)], [svt("ObjTipo", "VariableString(O1)")]),
    ev([cvar("ObjNum", "=", 2)], [svt("ObjTipo", "VariableString(O2)")]),
    ev([cvar("ObjNum", "=", 3)], [svt("ObjTipo", "VariableString(O3)")]),
    ev([cvar("ObjNum", "=", 4)], [svt("ObjTipo", "\"final\"")]),
    ev([cvar("ObjIni", "=", 0), cvar("ObjNum", "<=", 3), cvt("Estado", "\"juego\"")], [], sub=sub_ini),
    ev([cvar("ObjIni", "=", 0), cvar("ObjNum", "=", 4)], [svar("ObjIni", "=", 1)] + obj_en("camion", M["camion"]["x"], M["camion"]["y"], 9999)
       + banner("¡AL ESTACIONAMIENTO!", 2.5)),
    # usar objetivos (mantener Usar cerca); César hace la computadora al doble
    ev([], [setn("Objetivo", "Usada", "=", 0)]),
    foreach("Objetivo", [vnum("Objetivo", "Hecho", "=", 0)], [], sub=[
        ev([vnum("Sup", "Usando", "=", 1), VIVO, c("Distance", "Sup", "Objetivo", "140")], [setn("Objetivo", "Usada", "=", 1),
            setn("Objetivo", "Progreso", "+", "TimeDelta()")], sub=[
            ev([vtxt("Objetivo", "Tipo", "computadora"), vtxt("Sup", "Personaje", "cesar")], [setn("Objetivo", "Progreso", "+", "TimeDelta()")])]),
        ev([cmp("Objetivo.Variable(Progreso)", ">=", "Objetivo.Variable(Tiempo)")], [setn("Objetivo", "Hecho", "=", 1)],
           sub=[sonido("efectos/eventos/paso_objetivo.ogg")]),
    ]),
    # pasos de cada objetivo
    ev([vtxt("Objetivo", "Tipo", "servidor"), vnum("Objetivo", "Hecho", "=", 1)],
       [a("Delete", "Objetivo", "")] + obj_en("computadora", cl[0]["x"], cl[0]["y"], 20) + banner("¡Servidor prendido! Ahora la llamada", 2)),
    ev([vtxt("Objetivo", "Tipo", "computadora"), vnum("Objetivo", "Hecho", "=", 1)], [a("Delete", "Objetivo", ""), svar("Paso", "=", 99)]),
    ev([vtxt("Objetivo", "Tipo", "llaves"), vnum("Objetivo", "Hecho", "=", 1)], [a("Delete", "Objetivo", ""), svar("Paso", "=", 99)]),
    ev([c("CollisionNP", "Sup", "Bidon", "", ""), VIVO], [a("Delete", "Bidon", ""), svar("Bidones", "+", 1)], sub=[sonido("efectos/mundo/bidon.ogg")]),
    ev([cvt("ObjTipo", "\"gasolina\""), cvar("Bidones", ">=", 3), once()], obj_en("camion", M["camion"]["x"], M["camion"]["y"], 3)),
    ev([vtxt("Objetivo", "Tipo", "camion"), vnum("Objetivo", "Hecho", "=", 1), cvt("ObjTipo", "\"gasolina\"")],
       [a("Delete", "Objetivo", ""), svar("Paso", "=", 99)]),
    ev([vtxt("Objetivo", "Tipo", "interruptor"), vnum("Objetivo", "Hecho", "=", 1)], [a("Delete", "Objetivo", ""), svar("Interruptores", "+", 1)],
       sub=[sonido("efectos/mundo/interruptor.ogg")]),
    ev([cvt("ObjTipo", "\"luz\""), cvar("Interruptores", ">=", 3)], [svar("Apagon", "=", 0), svar("Paso", "=", 99), svar("Interruptores", "=", 0)]),
    ev([c("CollisionNP", "Sup", "Bolsa", "", ""), VIVO], [a("Delete", "Bolsa", ""), svar("TieneBolsa", "=", 1)]),
    ev([cvt("ObjTipo", "\"carnada\""), cvar("TieneBolsa", "=", 1), once()],
       obj_en("carnada", M["carnada_neveria"]["x"], M["carnada_neveria"]["y"], 2)),
    ev([vtxt("Objetivo", "Tipo", "carnada"), vnum("Objetivo", "Hecho", "=", 1)], [a("Delete", "Objetivo", ""), svar("Paso", "=", 99), svar("Horda", "=", 1)]),
    # objetivo cumplido
    ev([cvar("Paso", "=", 99)], [svar("Paso", "=", 0), svar("ObjNum", "+", 1), svar("ObjIni", "=", 0), svar("ExtraZombies", "=", 0),
                                 svar("TieneBolsa", "=", 0)] + banner("¡OBJETIVO CUMPLIDO!", 2.5), sub=[
        ev([vtxt("Sup", "Estado", "fuera")], [sett("Sup", "Estado", "\"normal\""), setn("Sup", "Vida", "=", "Sup.Variable(VidaMax) * 0.5"),
                                              a("Montre", "Sup", ""), a("ActivateBehavior", "Sup", "TopDownMovement", "yes"), a("PlayAnimation", "Sup"),
                                              a("MettreXY", "Sup", "=", "Variable(CamX)", "=", "Variable(CamY) + 48")]),
        sonido("efectos/eventos/objetivo_cumplido.ogg")]),
    # posición de la flecha: objetivo, bidón o bolsa más cercano
    ev([], [svar("ObjX", "=", "-1")]),
    ev([vnum("Objetivo", "Hecho", "=", 0), c("PickNearest", "Objetivo", "Variable(CamX)", "Variable(CamY)", "")],
       [svar("ObjX", "=", "Objetivo.X()"), svar("ObjY", "=", "Objetivo.Y()")]),
    ev([cvar("ObjX", "<", 0), c("PickNearest", "Bidon", "Variable(CamX)", "Variable(CamY)", "")], [svar("ObjX", "=", "Bidon.X()"), svar("ObjY", "=", "Bidon.Y()")]),
    ev([cvar("ObjX", "<", 0), c("PickNearest", "Bolsa", "Variable(CamX)", "Variable(CamY)", "")], [svar("ObjX", "=", "Bolsa.X()"), svar("ObjY", "=", "Bolsa.Y()")]),
    ev([], [svar("ObjDentro", "=", 0)]),
    ev([cmp("Variable(ObjX)", ">", "CameraBorderLeft() + 60"), cmp("Variable(ObjX)", "<", "CameraBorderRight() - 60"),
        cmp("Variable(ObjY)", ">", "CameraBorderTop() + 60"), cmp("Variable(ObjY)", "<", "CameraBorderBottom() - 60")], [svar("ObjDentro", "=", 1)]),
    ev([cvar("ObjX", ">=", 0), cvar("ObjDentro", "=", 0)],
       [a("Montre", "Flecha", ""), a("SetAngle", "Flecha", "=", "ToDeg(atan2(Variable(ObjY) - CameraY(), Variable(ObjX) - CameraX()))"),
        a("MettreXY", "Flecha", "=", "960 + cos(ToRad(Flecha.Angle())) * 860", "=", "540 + sin(ToRad(Flecha.Angle())) * 440")]),
    ev([o_(cvar("ObjX", "<", 0), cvar("ObjDentro", "=", 1))], [a("Cache", "Flecha")]),
] + [ev([cvt("ObjTipo", f"\"{t}\"")], [texto("TxtObjetivo", f"\"Objetivo {{}}/3: {txt}\"".replace("{}", "\" + ToString(Variable(ObjNum)) + \""))])
     for t, txt in TXT.items()] + [
    ev([cvt("ObjTipo", "\"gasolina\"")], [texto("TxtObjetivo", "TxtObjetivo.String() + \"  (\" + ToString(Variable(Bidones)) + \"/3)\"")]),
    ev([cvt("ObjTipo", "\"luz\"")], [texto("TxtObjetivo", "TxtObjetivo.String() + \"  (\" + ToString(Variable(Interruptores)) + \"/3)\"")]),
    ev([cvt("ObjTipo", "\"final\""), cvar("FinalActivo", "=", 0)], [texto("TxtObjetivo", "\"¡Lleguen al camión del estacionamiento!\"")]),
    ev([cvt("ObjTipo", "\"final\""), cvar("FinalActivo", "=", 1)],
       [texto("TxtObjetivo", "\"¡AGUANTEN! El camión arranca en \" + ToString(max(0, ceil(60 - TimerElapsedTime(\"final\")))) + \" s\"")]),
    # barra de progreso al usar
    foreach("Objetivo", [vnum("Objetivo", "Usada", "=", 1)], [texto("TxtAyuda", "\"Usando... \" + ToString(round(100 * Objetivo.Variable(Progreso) / Objetivo.Variable(Tiempo))) + \"%\"")]),
]
G.append(grupo("Objetivos y flecha", objs))

# ===== Final ¡Aguanten! y victoria =====
cam = M["camion"]
G.append(grupo("Final ¡Aguanten!", [
    comentario("Al llegar alguien al camión empieza la cuenta de 60 s: Canepa repara, llegan hordas grandes. Al terminar se abre la reja y escapan."),
    ev([cvt("ObjTipo", "\"final\""), cvar("FinalActivo", "=", 0), VIVO,
        cmp(f"DistanceBetweenPositions(Sup.X(), Sup.Y(), {cam['x']}, {cam['y']})", "<", "380")],
       [svar("FinalActivo", "=", 1), sreset("final"), svar("ExtraZombies", "=", 20), svar("SpawnCada", "=", 0.7),
        a("SetAnimationName", "Canepa", "\"pegar_lado\"")] + banner("¡AGUANTEN!", 3), sub=[sonido("efectos/eventos/final_inicio.ogg", 100)]),
    ev([cvar("FinalActivo", "=", 1), stimer("final", 60), cvt("Estado", "\"juego\"")],
       [svt("Estado", "\"victoria\""), sreset("fin"), gsett("Resultado", "\"victoria\""), gset("TiempoFinal", "=", "Variable(Tiempo)")]
       + banner("¡ESCAPARON!", 4), sub=[sonido("efectos/eventos/escape.ogg", 100)]),
    ev([cvar("FinalActivo", "=", 1), cvt("Estado", "\"juego\""), stimer("olafinal", 3), cmp("SceneInstancesCount(Zombies)", "<", "60")],
       [sreset("olafinal"), crear("ZNormal", "460 + 610 * RandomInRange(0, 1)", "CameraBorderTop() - 80"), sett("ZNormal", "Estado", "\"persigue\""),
        crear("ZCorredor", "460 + 610 * RandomInRange(0, 1)", "CameraBorderBottom() + 80"), sett("ZCorredor", "Estado", "\"persigue\"")]),
    ev([cvt("Estado", "\"victoria\""), stimer("fin", 4)], [a("Scene", "", "\"Resultados\"", "")]),
    ev([cvt("Estado", "\"victoria\"")], [a("ActivateBehavior", "Sup", "TopDownMovement", "no")]),
]))

# ===== Rescates y Canepa =====
G.append(grupo("Rescates: Joel y Justino", [
    comentario("Tienen miedo y piden ayuda. Salvarlos: mantener Usar 2 s junto a ellos. Costo: tiempo y van lento detrás del "
               "grupo. Recompensa: el equipo se cura 30 al rescatarlos y cuentan en los premios. A los profes no los muerden."),
    foreach("Profe", [vtxt("Profe", "Estado", "miedo")], [], sub=[
        ev([vnum("Sup", "Usando", "=", 1), VIVO, c("Distance", "Sup", "Profe", "100")], [setn("Profe", "Progreso", "+", "TimeDelta()")]),
        ev([cmp("Profe.Variable(Progreso)", ">=", "2")], [sett("Profe", "Estado", "\"sigue\""), svar("Rescatados", "+", 1),
                                                         setn("Sup", "Vida", "=", "min(Sup.Variable(VidaMax), Sup.Variable(Vida) + 30)")]
           + banner("¡Rescatado! El equipo se cura", 2), sub=[sonido("efectos/eventos/rescate_logrado.ogg")]),
        ev([c("Distance", "Profe", "Sup", "350"), VIVO, timer_ok("Profe", "grito", 4)],
           [reset_t("Profe", "grito"), texto("TxtAyuda", "\"¡Ayuda! ¡Aquí! (mantén Usar)\"")]),
    ]),
    ev([c("DepartScene", "")], [reset_t("Profe", "grito")]),
    ev([vtxt("Profe", "Estado", "sigue")],
       [a("MettreXY", "Profe", "=", "Profe.X() + (Variable(CamX) - 60 - Profe.X()) * min(1, 1.2 * TimeDelta())",
          "=", "Profe.Y() + (Variable(CamY) + 120 - Profe.Y()) * min(1, 1.2 * TimeDelta())"),
        a("ChangePlan", "Profe", "=", "Profe.Y()")]),
    ev([vtxt("Profe", "Estado", "sigue")], [a("SeparateFromObjects", "Profe", "Solidos", "")]),
]))

# ===== Horda de la explanada =====
nev = M["carnada_neveria"]
G.append(grupo("Horda de la explanada", [
    comentario("8 zombies dormidos alrededor de la fuente. Despiertan si alguien pasa a menos de 150 px. Con la carnada (o el festín "
               "de Tony en la nevería) se van a comer a la nevería y dejan el paso libre."),
    ev([vtxt("Zombies", "Estado", "horda"), VIVO, c("Distance", "Zombies", "Sup", "150"), cvar("Horda", "=", 0)], [sett("Zombies", "Estado", "\"persigue\"")]),
    ev([cvar("Horda", "=", 1), vtxt("Zombies", "Estado", "horda")], [sett("Zombies", "Estado", "\"comiendo\""),
        a("PathfindingBehavior::SetDestination", "Zombies", "Pathfinding", "", str(nev["x"]), str(nev["y"] + 60))]),
]))

# ===== Habilidades, especiales y pasivas =====
CD = {"tony": (18, 50), "miranda": (18, 55), "cesar": (14, 55), "alan": (15, 45), "castillo": (16, 55),
      "alessandro": (20, 60), "gabo": (14, 50), "carlos": (12, 50)}
hab = [comentario("E / Y = Habilidad (recarga corta). C / RB = Especial (recarga larga). Los bots usan la Habilidad con 3+ zombies "
                  "cerca y el Especial con 5+. Alessandro cerca: recargas 20% más rápido (pasiva).")]
hab.append(ev([vnum("Sup", "Init", "=", 1), vnum("Sup", "CdOk", "=", 0)], [setn("Sup", "CdOk", "=", 1), reset_t("Sup", "hab"), reset_t("Sup", "esp")],
              sub=[ev([vtxt("Sup", "Personaje", pj)], [setn("Sup", "HabCD", "=", h), setn("Sup", "EspCD", "=", e)]) for pj, (h, e) in CD.items()]))
# bots: deciden según zombies cercanos
hab.append(foreach("Sup", [vnum("Sup", "Control", "=", -1), VIVO], [setn("Sup", "Cerca", "=", 0)], sub=[
    ev([vtxt("Zombies", "Estado", "persigue"), c("Distance", "Zombies", "Sup", "300")], [setn("Sup", "Cerca", "=", "PickedInstancesCount(Zombies)")]),
    ev([vnum("Sup", "Cerca", ">=", 3)], [setn("Sup", "PideHab", "=", 1)]),
    ev([vnum("Sup", "Cerca", ">=", 5)], [setn("Sup", "PideEsp", "=", 1)])]))
# disparo: listo si pasó la recarga
LISTA_H = [VIVO, vnum("Sup", "PideHab", "=", 1), timer_ok("Sup", "hab", "Sup.Variable(HabCD) / Variable(BonoCD)")]
LISTA_E = [VIVO, vnum("Sup", "PideEsp", "=", 1), timer_ok("Sup", "esp", "Sup.Variable(EspCD) / Variable(BonoCD)")]
hab.append(ev([], [svar("BonoCD", "=", 1)]))
hab.append(ev([vtxt("Sup", "Personaje", "alessandro"), VIVO], [svar("BonoCD", "=", 1.2)]))
def H(pj, acciones, sub=None, esp=False):
    conds = (LISTA_E if esp else LISTA_H) + [vtxt("Sup", "Personaje", pj)]
    t = "esp" if esp else "hab"
    efecto = [crear("EfectoPj", "Sup.X()", "Sup.Y() - 50"), a("SetAnimationName", "EfectoPj", f"\"{pj}_{t}\""),
              setn("EfectoPj", "Jugador", "=", "Sup.Variable(Jugador)"), reset_t("EfectoPj", "vida")]
    return foreach("Sup", conds, [reset_t("Sup", t), a("SetAnimationName", "Sup", f"Sup.VariableString(Personaje) + \"_{'especial' if esp else 'habilidad'}\""),
                                  setn("Sup", "Atacando", "=", 1), reset_t("Sup", "golpe")] + efecto + acciones,
                   (sub or []) + [sonido(f"efectos/habilidades/{pj}_{'especial' if esp else 'habilidad'}.ogg")])
def par(zona_r, estado, seg):   # paraliza a los zombies cerca del Sup actual
    return ev([vtxt("Zombies", "Estado", "muerto", inv=True), vtxt("Zombies", "Estado", "horda", inv=True),
               vnum("Zombies", "Aliado", "=", 0), c("Distance", "Zombies", "Sup", str(zona_r))],
              [sett("Zombies", "Estado", f"\"{estado}\""), setn("Zombies", "Paralisis", "=", seg),
               a("ActivateBehavior", "Zombies", "Pathfinding", "no"), reset_t("Zombies", "par")])
hab += [
    # Tony
    H("tony", [crear("Comida", "Sup.X() - 40", "Sup.Y() + 10"), crear("Comida", "Sup.X() + 40", "Sup.Y() + 10")], sub=[
        ev([cmp(f"DistanceBetweenPositions(Sup.X(), Sup.Y(), {nev['x']}, {nev['y']})", "<", "500")],
           [svar("Festin", "=", 1)] + banner("¡FESTÍN! Los zombies van a la nevería", 2), sub=[
            ev([cvt("ObjTipo", "\"carnada\"")], [svar("Paso", "=", 99), svar("Horda", "=", 1)]),
            ev([vtxt("Zombies", "Estado", "persigue")], [sett("Zombies", "Estado", "\"distraido\""), setn("Zombies", "Paralisis", "=", 8),
                setn("Zombies", "DestX", "=", nev["x"]), setn("Zombies", "DestY", "=", nev["y"]), reset_t("Zombies", "par")])])]),
    H("tony", [sett("Sup", "Personaje", "\"tonyfuerte\""), reset_t("Sup", "gym"), setn("Sup", "Fuerza", "=", 2.6), setn("Sup", "ResDanio", "=", 0.6)], esp=True),
    ev([vtxt("Sup", "Personaje", "tonyfuerte"), timer_ok("Sup", "gym", 10)], [sett("Sup", "Personaje", "\"tony\""), setn("Sup", "Fuerza", "=", 1.3),
                                                                             setn("Sup", "ResDanio", "=", 1)]),
    ev([vtxt("Sup", "Personaje", "tony"), VIVO], [svar("Dinero", "+", "TimeDelta()")]),
    # Miranda
    H("miranda", [], sub=[par(380, "dormido", 6)]),
    H("miranda", [reset_t("Sup", "minigun"), setn("Sup", "Minigun", "=", 1)], esp=True),
    ev([vnum("Sup", "Minigun", "=", 1), VIVO], [setn("Sup", "QuierePegar", "=", 1), setn("Sup", "DanioArma", "=", 6), setn("Sup", "Alcance", "=", 2.5),
                                               setn("Sup", "Cadencia", "=", 0.1), setn("Sup", "Rapidez", "=", 0.5)]),
    ev([vnum("Sup", "Minigun", "=", 1), timer_ok("Sup", "minigun", 8)], [setn("Sup", "Minigun", "=", 0), setn("Sup", "Rapidez", "=", 1)]),
    ev([vtxt("Sup", "Personaje", "miranda"), VIVO, timer_ok("Sup", "tinte", 4), cmp("Sup.Variable(Vida)", "<", "Sup.Variable(VidaMax)")],
       [setn("Sup", "Vida", "+", "2 * TimeDelta()")]),
    # César
    H("cesar", [], sub=[ev([c("Distance", "Puerta", "Sup", "220"), c("PickNearest", "Puerta", "Sup.X()", "Sup.Y()", "")], [setn("Puerta", "Vida", "=", 0)]),
                        ev([vtxt("Objetivo", "Tipo", "computadora"), c("Distance", "Objetivo", "Sup", "250")],
                           [setn("Objetivo", "Progreso", "+", "Objetivo.Variable(Tiempo) * 0.5")])]),
    H("cesar", [], esp=True, sub=[ev([c("CollisionNP", "Sup", "Niebla", "", "")], [setn("Niebla", "Abierta", "=", 1)]),
                                  ev([vtxt("Zombies", "Estado", "muerto", inv=True), c("Distance", "Zombies", "Sup", "650")],
                                     [a("AddForceVersPos", "Zombies", "Sup.X()", "Sup.Y()", "-500", "0")]), par(650, "aturdido", 3)]),
    # Alan
    H("alan", [crear("ArmaPiso", "Sup.X() + 30", "Sup.Y()")], sub=[ev([], [sett("ArmaPiso", "Tipo", "\"regla\""), a("SetAnimationName", "ArmaPiso", "\"regla\"")])]
                                                              + [ev([cmp("RandomFloat(1)", "<", "0.4")], [crear("Comida", "Sup.X() - 30", "Sup.Y()")])]),
    H("alan", [], esp=True, sub=[ev([vtxt("Sup", "Arma", "puños")], []),
                                 foreach("Sup", [VIVO, vtxt("Sup", "Arma", "puños")], [crear("ArmaPiso", "Sup.X()", "Sup.Y()")],
                                         [ev([], [sett("ArmaPiso", "Tipo", "\"escoba\""), a("SetAnimationName", "ArmaPiso", "\"escoba\"")])])]),
    # Castillo
    H("castillo", [], sub=[ev([vtxt("ZNormal", "Estado", "muerto", inv=True), c("Distance", "ZNormal", "Sup", "130"),
                               c("PickNearest", "ZNormal", "Sup.X()", "Sup.Y()", "")],
                              [a("Delete", "ZNormal", ""), setn("Sup", "Vida", "=", "min(Sup.Variable(VidaMax), Sup.Variable(Vida) + 15)"),
                               svar("Tumbados", "+", 1)] + banner("Sabía a... facultad.", 1.5))]),
    H("castillo", [], esp=True, sub=[foreach("ZNormal", [vtxt("ZNormal", "Estado", "muerto", inv=True), c("Distance", "ZNormal", "Sup", "320")], [],
                                             [ev([cmp("SceneInstancesCount(ZCurado)", "<", "4")],
                                                 [crear("ZCurado", "ZNormal.X()", "ZNormal.Y()"), a("Delete", "ZNormal", ""),
                                                  setn("ZCurado", "Aliado", "=", 1), sett("ZCurado", "Estado", "\"aliado\""), reset_t("ZCurado", "vida")])])]),
    # Alessandro
    H("alessandro", [], sub=[par(320, "riendo", 4)] ),
    H("alessandro", [], esp=True, sub=[par(99999, "congelado", 4)]),
    # Gabo
    H("gabo", [setn("Sup", "Rapidez", "=", 2), reset_t("Sup", "turbo"), setn("Sup", "Turbo", "=", 1)]),
    ev([vnum("Sup", "Turbo", "=", 1), timer_ok("Sup", "turbo", 4)], [setn("Sup", "Turbo", "=", 0), setn("Sup", "Rapidez", "=", 1)]),
    ev([vnum("Sup", "Turbo", "=", 1), c("Distance", "Zombies", "Sup", "70"), vtxt("Zombies", "Estado", "muerto", inv=True)],
       [a("AddForceVersPos", "Zombies", "Sup.X()", "Sup.Y()", "-600", "0")]),
    H("gabo", [crear("Aparato", "Sup.X() + RandomInRange(-260, 260)", "Sup.Y() + RandomInRange(-260, 260)"),
               crear("Aparato", "Sup.X() + RandomInRange(-260, 260)", "Sup.Y() + RandomInRange(-260, 260)"),
               crear("Aparato", "Sup.X() + RandomInRange(-260, 260)", "Sup.Y() + RandomInRange(-260, 260)")], esp=True, sub=[
        ev([], [reset_t("Aparato", "vida")]),
        foreach("Zombies", [vtxt("Zombies", "Estado", "persigue"), c("Distance", "Zombies", "Sup", "750")], [], [
            ev([c("PickNearest", "Aparato", "Zombies.X()", "Zombies.Y()", "")],
               [sett("Zombies", "Estado", "\"distraido\""), setn("Zombies", "Paralisis", "=", 8), reset_t("Zombies", "par"),
                setn("Zombies", "DestX", "=", "Aparato.X()"), setn("Zombies", "DestY", "=", "Aparato.Y()")])])]),
    ev([timer_ok("Aparato", "vida", 8)], [a("Delete", "Aparato", "")]),
    # Carlos
    H("carlos", [], sub=[ev([c("Distance", "Puerta", "Sup", "220"), c("PickNearest", "Puerta", "Sup.X()", "Sup.Y()", "")],
                            [setn("Puerta", "Vida", "=", 0)] + banner("Aquí no pueden pasar... excepto yo.", 1.5))]),
    H("carlos", [reset_t("Sup", "tanque"), svar("Tanque", "=", 1)], esp=True),
    ev([cvar("Tanque", "=", 1)], [setn("Sup", "ResDanio", "=", 0.5)]),
    ev([vtxt("Sup", "Personaje", "carlos")], [setn("Sup", "ResDanio", "=", 0.75)]),
    ev([cvar("Tanque", "=", 1), vtxt("Sup", "Personaje", "carlos"), timer_ok("Sup", "tanque", 8)], [svar("Tanque", "=", 0)]),
    ev([cvar("Tanque", "=", 0), vtxt("Sup", "Personaje", "carlos", inv=True), vtxt("Sup", "Personaje", "tonyfuerte", inv=True)],
       [setn("Sup", "ResDanio", "=", 1)]),
    # Comida
    ev([c("CollisionNP", "Sup", "Comida", "", ""), VIVO, cmp("Sup.Variable(Vida)", "<", "Sup.Variable(VidaMax)")],
       [setn("Sup", "Vida", "=", "min(Sup.Variable(VidaMax), Sup.Variable(Vida) + Comida.Variable(Cura))"), a("Delete", "Comida", "")], sub=[
        ev([vtxt("Sup", "Personaje", "castillo")], [setn("Sup", "Vida", "=", "min(Sup.Variable(VidaMax), Sup.Variable(Vida) + Comida.Variable(Cura))")]),
        sonido("efectos/movimiento/comer.ogg")]),
]
for o in esc["objects"]:
    if o["name"] == "Sup":
        for v in [var("CdOk", 0), var("Minigun", 0), var("Turbo", 0), var("Cerca", 0), var("HabTxt", ""), var("EspTxt", ""), var("TipoTxt", "")]:
            if not any(x["name"] == v["name"] for x in o["variables"]):
                o["variables"].append(v)
for n in ["BonoCD", "Festin", "Tanque"]:
    esc["variables"] = [v for v in esc["variables"] if v["name"] != n] + [var(n, 1 if n == "BonoCD" else 0)]
G.append(grupo("Habilidades, especiales y pasivas", hab))

# ===== Estados de zombies por habilidades =====
G.append(grupo("Zombies: dormidos, riendo, congelados, distraídos y curados", [
    comentario("Paralizados no se pueden volver a paralizar hasta moverse. Al pasar el tiempo vuelven a perseguir. "
               "Primer golpe a un dormido: doble daño (se aplica al pegarle: el golpe lo despierta)."),
    ev([vtxt("Zombies", "Estado", "dormido")], [a("ChangeColor", "Zombies", "\"170;170;255\"")]),
    ev([vtxt("Zombies", "Estado", "riendo")], [a("ChangeColor", "Zombies", "\"255;255;140\""), a("MettreX", "Zombies", "+", "RandomInRange(-1, 1)")]),
    ev([vtxt("Zombies", "Estado", "congelado")], [a("ChangeColor", "Zombies", "\"128;128;128\""), a("PauseAnimation", "Zombies")]),
    ev([vtxt("Zombies", "Estado", "aturdido")], [a("ChangeColor", "Zombies", "\"255;220;120\"")]),
    foreach("Zombies", [vtxt("Zombies", "Estado", "distraido"), timer_ok("Zombies", "ruta", 0.75)], [
        a("ActivateBehavior", "Zombies", "Pathfinding", "yes"),
        a("PathfindingBehavior::SetDestination", "Zombies", "Pathfinding", "", "Zombies.Variable(DestX)", "Zombies.Variable(DestY)"), reset_t("Zombies", "ruta")]),
    foreach("Zombies", [o_(vtxt("Zombies", "Estado", "dormido"), vtxt("Zombies", "Estado", "riendo"), vtxt("Zombies", "Estado", "congelado"),
                           vtxt("Zombies", "Estado", "aturdido"), vtxt("Zombies", "Estado", "distraido")),
                        cmp("Zombies.ObjectTimerElapsedTime(\"par\")", ">=", "Zombies.Variable(Paralisis)")],
            [sett("Zombies", "Estado", "\"persigue\""), a("ActivateBehavior", "Zombies", "Pathfinding", "yes"), a("PlayAnimation", "Zombies"),
             a("ChangeColor", "Zombies", "\"255;255;255\"")]),
    # curados: pelean del lado del equipo 15 s y luego huyen
    foreach("ZCurado", [vtxt("ZCurado", "Estado", "aliado"), timer_ok("ZCurado", "ruta", 0.5)], [reset_t("ZCurado", "ruta")], sub=[
        ev([vtxt("Zombies", "Estado", "muerto", inv=True), c("PickNearest", "Zombies", "ZCurado.X()", "ZCurado.Y()", "")],
           [a("PathfindingBehavior::SetDestination", "ZCurado", "Pathfinding", "", "Zombies.X()", "Zombies.Y()")], sub=[
            ev([cmp("ZCurado.Distance(Zombies)", "<", "80")], [setn("Zombies", "Vida", "-", "10"), a("ChangeColor", "Zombies", "\"255;90;90\""),
                                                               reset_t("Zombies", "tinte")])])]),
    ev([vtxt("ZCurado", "Estado", "aliado"), vnum("ZCurado", "Init", "=", 0)], [setn("ZCurado", "Init", "=", 1), reset_t("ZCurado", "vida"), reset_t("ZCurado", "ruta")]),
    ev([vtxt("ZCurado", "Estado", "aliado"), timer_ok("ZCurado", "vida", 15)], [crear("Comida", "ZCurado.X()", "ZCurado.Y()"), a("Delete", "ZCurado", "")]),
]))

# ===== Luces, apagón, parpadeo y destrozos =====
G.append(grupo("Ambiente: noche, luces que parpadean y apagón", [
    comentario("Luz ambiente de noche. Parpadeo al azar. En el objetivo de la luz (o apagón del Jefe) todo se pone muy oscuro. "
               "Los marcadores 'destrozo' (40) indican dónde van los props de daño cuando existan."),
    ev([cvar("Apagon", "=", 0), stimer("parpadeo", "Variable(Luz)")],
       [sreset("parpadeo"), svar("Luz", "=", "RandomFloatInRange(0.08, 3)"),
        a("SetLayerAmbientLightColor", "", "\"Luz\"", "\"60;62;90\"")]),
    ev([cvar("Apagon", "=", 0), cmp("TimerElapsedTime(\"parpadeo\")", ">", "0.08")], [a("SetLayerAmbientLightColor", "", "\"Luz\"", "\"120;125;165\"")]),
    ev([cvar("Apagon", "=", 1)], [a("SetLayerAmbientLightColor", "", "\"Luz\"", "\"28;28;42\"")]),
    ev([cvar("Apagon", "=", 1), once()], [], sub=[sonido("efectos/eventos/apagon.ogg")]),
]))

# ===== HUD =====
hud = [comentario("Panel por jugador en cada esquina (color P1 amarillo, P2 azul, P3 verde, P4 rosa), barra de infestación, objetivo, "
                  "tiempo, letreros grandes y la ayuda con la tecla o el botón de cada quien.")]
COL = {1: "255;220;60", 2: "90;170;255", 3: "110;230;110", 4: "255;120;200"}
hud += [
    foreach("Sup", [], [sett("Sup", "HabTxt", "ToString(ceil(Sup.Variable(HabCD) / Variable(BonoCD) - Sup.ObjectTimerElapsedTime(\"hab\"))) + \" s\""),
                        sett("Sup", "EspTxt", "ToString(ceil(Sup.Variable(EspCD) / Variable(BonoCD) - Sup.ObjectTimerElapsedTime(\"esp\"))) + \" s\"")], sub=[
        ev([timer_ok("Sup", "hab", "Sup.Variable(HabCD) / Variable(BonoCD)")], [sett("Sup", "HabTxt", "\"LISTA\"")]),
        ev([timer_ok("Sup", "esp", "Sup.Variable(EspCD) / Variable(BonoCD)")], [sett("Sup", "EspTxt", "\"LISTO\"")]),
        ev([vnum("Sup", "Control", "=", -1)], [sett("Sup", "TipoTxt", "\" (bot)\"")]),
        ev([vnum("Sup", "Control", "=", 0)], [sett("Sup", "TipoTxt", "\" (teclado)\"")]),
        ev([vnum("Sup", "Control", ">", 0)], [sett("Sup", "TipoTxt", "\" (control \" + ToString(Sup.Variable(Control)) + \")\"")]),
    ]),
]
for k in range(1, 5):
    hud.append(ev([vnum("Sup", "Jugador", "=", k)], [svt(f"J{k}Txt",
        f"\"P{k} \" + Sup.VariableString(Personaje) + Sup.VariableString(TipoTxt) + \"   VIDA \" + ToString(round(Sup.Variable(Vida))) + \"/\" + "
        "ToString(Sup.Variable(VidaMax)) + NewLine() + \"Habilidad: \" + Sup.VariableString(HabTxt) + \"   Especial: \" + Sup.VariableString(EspTxt) + "
        "NewLine() + \"Arma: \" + Sup.VariableString(Arma) + Sup.VariableString(InvTxt) + \"   \" + Sup.VariableString(Estado)")]))
    hud.append(ev([vnum("TxtPanel", "Jugador", "=", k)], [texto("TxtPanel", f"VariableString(J{k}Txt)"),
                                                         a("TextObject::ChangeColor", "TxtPanel", f"\"{COL[k]}\"")]))
hud += [ev([cvar("Infestacion", "=", n)], [svt("InfBar", f"\"{'■' * n + '□' * (5 - n)}\"")]) for n in range(1, 6)]
hud += [ev([], [svt("SegTxt", "ToString(floor(mod(Variable(Tiempo), 60)))")]), ev([cmp("mod(Variable(Tiempo), 60)", "<", "10")], [svt("SegTxt", "\"0\" + VariableString(SegTxt)")])]
hud += [
    ev([], [texto("TxtInfest", "\"INFESTACIÓN \" + VariableString(InfBar) + \"  nivel \" + ToString(Variable(Infestacion)) + \"/5\" + \"     Tiempo \" + "
                               "ToString(floor(Variable(Tiempo) / 60)) + \":\" + VariableString(SegTxt) + "
                               "\"     $\" + ToString(floor(Variable(Dinero))) + \"     tumbados \" + ToString(Variable(Tumbados))")]),
    ev([c("CompareTimer", "", "\"banner\"", "<", "Variable(BannerSeg)")], [texto("TxtBanner", "VariableString(Banner)"), a("Montre", "TxtBanner", "")]),
    ev([stimer("banner", "Variable(BannerSeg)")], [a("Cache", "TxtBanner")]),
    ev([stimer("ayuda", 2.5)], [texto("TxtAyuda", "\"\""), sreset("ayuda")]),
    # infestación sube: letrero y alarma
    ev([cvar("Infestacion", ">", 1), c("BuiltinCommonInstructions::CompareNumbers", "Variable(Infestacion)", "!=", "Variable(InfVista)")],
       [svar("InfVista", "=", "Variable(Infestacion)")] + banner("¡LA FDI SE ESTÁ LLENANDO!", 2.5),
       sub=[sonido("efectos/eventos/infestacion_sube.ogg", 100)]),
    # ayuda con la tecla correcta
    ev([c("DepartScene", "")], [texto("TxtAyuda", "\"Teclado: WASD mover · clic pegar · F usar · E habilidad · C especial    Control: stick · X pegar · A usar · Y habilidad · RB especial\""),
                                sreset("ayuda")]),
]
esc["variables"] = [v for v in esc["variables"] if v["name"] != "InfVista"] + [var("InfVista", 1)]
G.append(grupo("HUD", hud))

# ===== Cinemática de inicio =====
B01 = next(z for z in datos["zonas"] if z["nombre"] == "B-01")
bx, by = B01["x"] + B01["w"] // 2, B01["y"] + B01["h"] // 2
PB01 = next(p for p in datos["puertas"] if "B-01" in p["zonas"])
DIALOGOS = [(0, "Tony: ¿Por qué no llega el profe?"), (3, "Alan: ¿Ya nos vamos o qué?"), (6, "Miranda: Ya van 20 minutos..."),
            (9, "📱 ALERTA DE EMERGENCIA: infección zombie en la escuela. NO SALGAN DE LOS SALONES."),
            (13, "¡¿Qué?! ¡Miren por la ventana!"), (16, "¡Atranquen la puerta!"), (19, "*¡CRASH!* ¡Un zombie rompió la puerta!"),
            (21, "¿Qué hacemos? ... ¡Agarra la regla! (CLIC para pegar / X en el control)")]
intro = [comentario("En los dos modos: el salón B-01 (planta 1 de B pendiente: se usa el de planta baja). Relajo, alerta en el teléfono, "
                    "brote, atrancan la puerta, un zombie la rompe y el jugador 1 pega con la regla. Esc o Start la salta. Solo se "
                    "muestra completa la primera vez (VioIntro).")]
intro += [
    ev([c("DepartScene", ""), gnum("VioIntro", "=", 0), gnum("Demo", "=", 0)], [svt("Estado", "\"intro\""), sreset("intro"),
        a("MettreXY", "Sup", "=", f"{bx} + (Sup.Variable(Jugador) - 2.5) * 60", "=", f"{by}"), setn("Sup", "CtlReal", "=", "Sup.Variable(Control)"),
        setn("Sup", "Control", "=", -2), a("Cache", "TxtPanel"), svar("CamX", "=", bx), svar("CamY", "=", by),
        a("CameraX", "", "=", str(bx), "", ""), a("CameraY", "", "=", str(by), "", "")]),
] + [ev([cvt("Estado", "\"intro\""), stimer("intro", t), once()], [texto("TxtDialogo", f"\"{d}\"")]) for t, d in DIALOGOS] + [
    # el zombie llega por el pasillo, tumba la puerta del salón (P06, pared oeste) y entra
    ev([cvt("Estado", "\"intro\""), stimer("intro", 16), once()],
       [crear("ZNormal", PB01["x"] - 160, PB01["y"] + PB01["h"] // 2), sett("ZNormal", "Estado", "\"cinematica\""),
        crear("ZNormal", PB01["x"] - 260, PB01["y"] - 120), sett("ZNormal", "Estado", "\"cinematica\"")]),
    ev([cvt("Estado", "\"intro\""), vtxt("ZNormal", "Estado", "cinematica"), stimer("intro", 16.3), once()],
       [a("PathfindingBehavior::SetDestination", "ZNormal", "Pathfinding", "", str(PB01["x"] - 30), str(PB01["y"] + PB01["h"] // 2))]),
    ev([cvt("Estado", "\"intro\""), stimer("intro", 17), stimer("golpepuerta", 0.6), cvar("IntroPuerta", "=", 0)],
       [sreset("golpepuerta")], sub=[ev([c("PickNearest", "Puerta", str(PB01["x"] + 16), str(PB01["y"] + 32), "")],
                                         [a("ChangeColor", "Puerta", "\"255;150;150\"")]), sonido("efectos/mundo/puerta_golpe.ogg")]),
    ev([cvt("Estado", "\"intro\""), stimer("intro", 19), once()], [svar("IntroPuerta", "=", 1)], sub=[
        ev([c("PickNearest", "Puerta", str(PB01["x"] + 16), str(PB01["y"] + 32), "")], [setn("Puerta", "Vida", "=", 0)]),
        ev([vtxt("ZNormal", "Estado", "cinematica")], [sett("ZNormal", "Estado", "\"persigue\"")])]),
    ev([cvt("Estado", "\"intro\""), stimer("intro", 21), once(), vnum("Sup", "Jugador", "=", 1)],
       [sett("Sup", "Arma", "\"regla\""), setn("Sup", "Usos", "=", 30), setn("Sup", "Control", "=", "Sup.Variable(CtlReal)")]),
    ev([cvt("Estado", "\"intro\""), stimer("intro", 21)], [], sub=[
        ev([cmp("Variable(Tumbados)", ">=", "1")], [svar("IntroPaso", "=", 1)]),
        ev([stimer("intro", 40)], [svar("IntroPaso", "=", 1)])]),
    ev([cvt("Estado", "\"intro\""), o_(suelta("Escape"), pad_suelta(1, "START"), pad_suelta(2, "START"), cvar("IntroPaso", "=", 1))],
       [svt("Estado", "\"juego\""), gset("VioIntro", "=", 1), texto("TxtDialogo", "\"\""), a("Montre", "TxtPanel", ""), sreset("partida"),
        sreset("infest")], sub=[
        ev([vnum("Sup", "Control", "=", -2)], [setn("Sup", "Control", "=", "Sup.Variable(CtlReal)")]),
        ev([vnum("Sup", "Jugador", "=", 1), vtxt("Sup", "Arma", "puños")], [sett("Sup", "Arma", "\"regla\""), setn("Sup", "Usos", "=", 30)]),
        ev([], [crear("ArmaPiso", bx - 80, by + 40), sett("ArmaPiso", "Tipo", "\"silla\""), a("SetAnimationName", "ArmaPiso", "\"silla\""),
                crear("ArmaPiso", bx + 80, by + 40), sett("ArmaPiso", "Tipo", "\"escoba\""), a("SetAnimationName", "ArmaPiso", "\"escoba\"")]) ]),
]
for o in esc["objects"]:
    if o["name"] == "Sup" and not any(v["name"] == "CtlReal" for v in o["variables"]):
        o["variables"].append(var("CtlReal", 0))
G.insert(0, grupo("Cinemática de inicio", intro))

# ===== Modo Jefe de zombies =====
CARTAS = [("Zombie", "ZNormal", 2, 0, 1), ("Corredor", "ZCorredor", 3, 0, 1), ("Gritón", "ZGriton", 5, 10, 1), ("Gordo", "ZGordo", 7, 15, 1),
          ("Horda chica", "ZNormal", 8, 20, 5), ("Trabar puerta", "", 4, 15, 0), ("Apagón", "", 6, 30, 0), ("Horda grande", "ZNormal", 18, 60, 12)]
MMX, MMY, MMW, MMH = 1920 - 668, 1080 - 418, 640, 392
SX, SY = datos["ancho_px"] / MMW, datos["alto_px"] / MMH
jefe = [comentario("Un jugador con ratón compra zombies con oro. Ve el mapa completo en el minimapa (abajo a la derecha). Teclas 1-8 o "
                   "clic en la lista para elegir carta; clic en el minimapa para usarla. No puede poner zombies dentro de lo que ven "
                   "los sobrevivientes (zona roja) salvo en las rejillas. Gana 1 de oro cada 5 s; al doble durante el ¡Aguanten!.")]
jefe += [
    ev([cvar("Jefe", "=", 1), stimer("oro", 5)], [sreset("oro"), svar("OroJefe", "+", 1)], sub=[ev([cvar("FinalActivo", "=", 1)], [svar("OroJefe", "+", 1)])]),
] + [ev([cvar("Jefe", "=", 1), suelta(f"Num{k}")], [svar("Carta", "=", k)]) for k in range(1, 9)] + \
    [ev([cvar("Jefe", "=", 1), suelta(f"Numpad{k}")], [svar("Carta", "=", k)]) for k in range(1, 9)] + [
] + [ev([cvar("Jefe", "=", 1), cvar("Carta", "=", k)], [svt("CartaTxt", f"\"{k} {n} ({pr} de oro)\"")]) for k, (n, _, pr, _, _) in enumerate(CARTAS, 1)] + [
    ev([cvar("Jefe", "=", 1)], [texto("TxtJefe", "\"JEFE DE ZOMBIES   oro \" + ToString(Variable(OroJefe)) + \"   carta: \" + VariableString(CartaTxt) + NewLine() + \"" +
        "  ".join(f"{k}:{n} {pr}" for k, (n, _, pr, _, _) in enumerate(CARTAS, 1)) + "\"")]),
    ev([cvar("Jefe", "=", 1), c("MouseButtonReleased", "", "Left"),
        cmp("MouseX(\"HUD\", 0)", ">=", str(MMX)), cmp("MouseY(\"HUD\", 0)", ">=", str(MMY))],
       [svar("JX", "=", f"(MouseX(\"HUD\", 0) - {MMX}) * {SX:.4f}"), svar("JY", "=", f"(MouseY(\"HUD\", 0) - {MMY}) * {SY:.4f}"),
        svar("JOk", "=", 1)], sub=[
        ev([cmp("abs(Variable(JX) - CameraX())", "<", "1000 / CameraZoom()"), cmp("abs(Variable(JY) - CameraY())", "<", "600 / CameraZoom()")],
           [svar("JOk", "=", 0)], sub=[ev([vtxt("Marcador", "Tipo", "salida_zombie"),
               cmp("DistanceBetweenPositions(Marcador.X(), Marcador.Y(), Variable(JX), Variable(JY))", "<", "200")],
               [svar("JOk", "=", 1), svar("JX", "=", "Marcador.X() + 16"), svar("JY", "=", "Marcador.Y() + 32")])]),
        ev([cvar("JOk", "=", 0)], banner("Zona prohibida: lo ven los sobrevivientes", 1.5)),
    ] + [ev([cvar("JOk", "=", 1), cvar("Carta", "=", k), cvar("OroJefe", ">=", pr), stimer(f"carta{k}", cd)],
            [svar("OroJefe", "-", pr), sreset(f"carta{k}")]
            + ([a("Repeat", "")] if False else [])
            + ([crear(obj, "Variable(JX) + RandomInRange(-40, 40)", "Variable(JY) + RandomInRange(-40, 40)") for _ in range(min(n_, 12))]
               + [sett(obj, "Estado", "\"persigue\"")] if obj else [])
            + ([svar("Apagon", "=", 1), sreset("apagonjefe")] if nombre == "Apagón" else [])
            + ([] if nombre != "Trabar puerta" else []),
            sub=([ev([c("PickNearest", "Puerta", "Variable(JX)", "Variable(JY)", ""), vtxt("Puerta", "Tipo", "normal")],
                     [setn("Puerta", "Trabada", "=", 1), setn("Puerta", "TiempoAbrir", "=", 99), reset_t("Puerta", "trabada")])] if nombre == "Trabar puerta" else [])
            + [sonido("efectos/interfaz/jefe_invocar.ogg")])
         for k, (nombre, obj, pr, cd, n_) in enumerate(CARTAS, 1) if not (nombre == "Horda grande")] + [
        ev([cvar("JOk", "=", 1), cvar("Carta", "=", 8), cvar("OroJefe", ">=", 18), stimer("carta8", 60), cvar("Infestacion", ">=", 3)],
           [svar("OroJefe", "-", 18), sreset("carta8")] + [crear(("ZNormal", "ZCorredor", "ZGordo")[i % 3], "Variable(JX) + RandomInRange(-60, 60)",
                                                                 "Variable(JY) + RandomInRange(-60, 60)") for i in range(12)]),
    ]),
    ev([vnum("Puerta", "Trabada", "=", 1), timer_ok("Puerta", "trabada", 10)], [setn("Puerta", "Trabada", "=", 0), setn("Puerta", "TiempoAbrir", "=", 1)]),
    ev([cvar("Jefe", "=", 1), cvar("Apagon", "=", 1), stimer("apagonjefe", 15), cvt("ObjTipo", "\"luz\"", "!=")], [svar("Apagon", "=", 0)]),
]
for k in range(1, 9):
    jefe.append(ev([c("DepartScene", "")], [sreset(f"carta{k}")]))
esc["variables"] = [v for v in esc["variables"] if v["name"] not in ("JX", "JY", "JOk")] + [var("JX", 0), var("JY", 0), var("JOk", 0)]
G.append(grupo("Modo Jefe de zombies", jefe))

# ===== Modo presentación (F1) =====
pres = [comentario("F1 abre/cierra el menú oculto. 1 completar objetivo · 2 saltar al final · 3 vida infinita · 4 subir infestación · "
                   "5 bajar infestación · 6 reiniciar. Si se usa, no se guarda el récord.")]
pres += [
    ev([suelta("F1")], [svar("Pres", "=", "1 - Variable(Pres)"), gset("SinRecord", "=", 1)]),
    ev([cvar("Pres", "=", 1)], [a("Montre", "TxtPres", ""), texto("TxtPres", "\"MODO PRESENTACIÓN (F1)\" + NewLine() + \"1 completar objetivo\" + NewLine() + "
                                 "\"2 saltar al final (lleva al equipo al camión)\" + NewLine() + \"3 vida infinita: \" + VariableString(VidaInfTxt) + NewLine() + "
                                 "\"4 subir infestación\" + NewLine() + \"5 bajar infestación\" + NewLine() + \"6 reiniciar partida\" + NewLine() + \"7 morder a P1\" + NewLine() + \"8 dar $200 al equipo\" + NewLine() + \"9 engrapadora para P1\"")]),
    ev([cvar("Pres", "=", 0)], [a("Cache", "TxtPres")]),
    ev([], [svt("VidaInfTxt", "\"no\"")]), ev([cvar("VidaInf", "=", 1)], [svt("VidaInfTxt", "\"SÍ\"")]),
    ev([cvar("Pres", "=", 1), suelta("Num1")], [svar("Paso", "=", 99), a("Delete", "Objetivo", ""), a("Delete", "Bidon", ""), a("Delete", "Bolsa", ""), svar("Apagon", "=", 0)]),
    ev([cvar("Pres", "=", 1), suelta("Num2")], [svar("ObjNum", "=", 4), svar("ObjIni", "=", 0), a("Delete", "Objetivo", ""), a("Delete", "Bidon", ""),
                                                a("Delete", "Bolsa", ""), svar("Apagon", "=", 0),
                                                a("MettreXY", "Sup", "=", f"{cam['x']} - 150 + Sup.Variable(Jugador) * 60", "=", f"{cam['y']} + 120"),
                                                a("CameraX", "", "=", f"{cam['x']}", "", ""), a("CameraY", "", "=", f"{cam['y']}", "", "")]),
    ev([cvar("Pres", "=", 1), suelta("Num3")], [svar("VidaInf", "=", "1 - Variable(VidaInf)")]),
    ev([cvar("Pres", "=", 1), suelta("Num4"), cvar("Infestacion", "<", 5)], [svar("Infestacion", "+", 1), sreset("infest")]),
    ev([cvar("Pres", "=", 1), suelta("Num5"), cvar("Infestacion", ">", 1)], [svar("Infestacion", "-", 1), sreset("infest"), svar("InfVista", "=", "Variable(Infestacion)")]),
    ev([cvar("Pres", "=", 1), suelta("Num6")], [a("Scene", "", "\"Juego\"", "")]),
    ev([cvar("VidaInf", "=", 1), vtxt("Sup", "Estado", "fuera", inv=True)], [setn("Sup", "Vida", "=", "Sup.Variable(VidaMax)")]),
]
G.append(grupo("Modo presentación (F1)", pres))
G.append(grupo("Textos centrados", centrar(nuevos)))

# ===== Premios al cambiar a Resultados =====
prem = [comentario("Antes de ir a Resultados se arma el texto de premios. Créditos por zombie tumbado: el último jugador que le pegó.")]
for k in range(1, 5):
    prem.append(ev([vtxt("Zombies", "Estado", "muerto"), vnum("Zombies", "Contado", "=", 0), vnum("Zombies", "UltJugador", "=", k)],
                   [svar(f"J{k}Kills", "+", "PickedInstancesCount(Zombies)"), setn("Zombies", "Contado", "=", 1)]))
    prem.append(ev([vtxt("Sup", "Estado", "caido"), vnum("Sup", "Jugador", "=", k), once()], [svar(f"J{k}Caidas", "+", 1)]))
NOMBRE_PREMIO = {"tony": "El empresario: ganó $\" + ToString(floor(Variable(Dinero))) + \" para el equipo",
                 "miranda": "Gamer de verdad", "cesar": "Hacker", "alan": "El gorrón", "castillo": "Buen provecho",
                 "alessandro": "Mejor chiste", "gabo": "Flash", "carlos": "El muro"}
prem.append(ev([cvar("Jefe", "=", 1)], [svt("JefeTxt", "\"Jefe de zombies: oro restante \" + ToString(Variable(OroJefe))")]))
prem.append(ev([o_(cvt("Estado", "\"victoria\""), cvt("Estado", "\"derrota\"")), once()],
               [gsett("Premios", "\"Tumbados por jugador:\" + NewLine() + " + " + ".join(
                   f"\"P{k}: \" + ToString(Variable(J{k}Kills)) + \"  (cayó \" + ToString(Variable(J{k}Caidas)) + \")\" + NewLine()" for k in range(1, 5))
                   + " + \"Profes rescatados: \" + ToString(Variable(Rescatados)) + NewLine() + \"Tumbados en total: \" + ToString(Variable(Tumbados))"
                   + " + NewLine() + \"El empresario (Tony): $\" + ToString(floor(Variable(Dinero))) + \" para el equipo\""
                   + " + NewLine() + VariableString(JefeTxt)"),
                gset("TiempoFinal", "=", "Variable(Tiempo)")]))
G.append(grupo("Premios", prem))

# ===== Música (lista para cuando existan los archivos) =====
G.append(grupo("Música y sonido de fondo", [
    comentario("Los audios aún no existen. Todo sonido está detrás de la variable global SonidoActivo (0 = apagado). Cuando el equipo "
               "entregue los archivos en fdiz\\sonido y fdiz\\musica con los nombres de la lista, poner SonidoActivo = 1."),
    ev([c("DepartScene", ""), gnum("SonidoActivo", "=", 1)], [a("PlayMusic", "", "\"musica/partida_1.ogg\"", "yes", "60", "1")]),
    ev([gnum("SonidoActivo", "=", 1), cvar("FinalActivo", "=", 1), once()], [a("PlayMusic", "", "\"musica/final_aguanten.ogg\"", "yes", "70", "1")]),
    ev([gnum("SonidoActivo", "=", 1), cvar("Infestacion", "=", 3), once()], [a("PlayMusic", "", "\"musica/partida_2.ogg\"", "yes", "60", "1")]),
    ev([gnum("SonidoActivo", "=", 1), cvar("Infestacion", "=", 5), once()], [a("PlayMusic", "", "\"musica/partida_3.ogg\"", "yes", "60", "1")]),
]))

# insertar grupos nuevos antes de la cámara (último grupo)
NOM = {g["name"] for g in G}
EV = [e for e in EV if e.get("name") not in NOM]
i_cam = next(k for k, e in enumerate(EV) if e.get("name") == "Cámara compartida")
EV[i_cam:i_cam] = [g for g in G if g["name"] != "Cinemática de inicio"]
EV.insert(2, next(g for g in G if g["name"] == "Cinemática de inicio"))
# la configuración del menú va primero: el personaje elegido debe estar puesto antes de calcular vida/velocidad
g_cfg = next(g for g in EV if g.get("name") == "Configuración y dificultad")
EV.remove(g_cfg); EV.insert(0, g_cfg)
esc["events"] = EV

# ======================= Escenas Titulo, Menu y Resultados =======================
def escena(nombre, objetos, instancias, eventos, variables=()):
    eventos = list(eventos) + centrar(objetos)
    base = json.loads(json.dumps(esc))
    base.update({"name": nombre, "mangledName": nombre, "r": 12, "v": 12, "b": 20, "objects": objetos, "instances": instancias,
                 "events": eventos, "variables": list(variables), "objectsGroups": [], "layers": [capa("", True)],
                 "objectsFolderStructure": {"folderName": "__ROOT"}, "behaviorsSharedData": []})
    return base
def ti(o, x, y, z=1, **kv): return instancia(o, x, y, "", z, variables=[var(k, v) for k, v in kv.items()])

PJS = ["tony", "miranda", "cesar", "alan", "castillo", "alessandro", "gabo", "carlos"]
NOMB = {"tony": "Tony", "miranda": "Miranda", "cesar": "César", "alan": "Alan", "castillo": "Castillo", "alessandro": "Alessandro",
        "gabo": "Gabo", "carlos": "Carlos"}
DESC = {"tony": "Cocinar / Modo gym", "miranda": "Arrullo / Minigun", "cesar": "Hackeo / Control de la escuela", "alan": "Gorrear / Reembolso",
        "castillo": "Tragar / App de salud", "alessandro": "Chiste / Reloj", "gabo": "Supervelocidad / Ecosistema", "carlos": "Llave maestra / Tanque"}
CONTINUAR = lambda: o_(suelta("Return"), suelta("Space"), c("MouseButtonReleased", "", "Left"), *[pad_suelta(k, "A") for k in range(1, 5)], *[pad_suelta(k, "START") for k in range(1, 5)])

# --- Título ---
tit_obj = [obj_texto("TxtTitulo", 160, "120;255;120", "center", "FDI-Z"), obj_texto("TxtSub", 40, "255;255;255", "center", ""),
           objeto_sprite("Fondo", [animacion("f", [img("extra/minimapa.png", EXTRA + "minimapa.png")], 1, False, (0, 0))])]
tit_inst = [ti("Fondo", 0, 0, 0), ti("TxtTitulo", 960, 260), ti("TxtSub", 960, 620)]
tit_inst[0].update({"customSize": True, "width": 1920, "height": 1080})
tit_ev = [
    ev([c("DepartScene", "")], [texto("TxtSub", "\"Presiona Enter, A o haz clic\" + NewLine() + NewLine() + \"La FDI se llenó de zombies. Escapen.\""),
                                sreset("demo"), gset("Demo", "=", 0), a("ChangeColor", "Fondo", "\"90;90;110\"")]),
    ev([CONTINUAR()], [a("Scene", "", "\"Menu\"", "")]),
    ev([stimer("demo", 25)], [gset("Demo", "=", 1), gset("Listo", "=", 1), gsett("Modo", "\"escape\""), gset("VioIntro", "=", 1)]
       + [x for k, pj in enumerate(["tony", "miranda", "gabo", "carlos"], 1) for x in (gsett(f"P{k}Pj", f"\"{pj}\""), gset(f"P{k}Ctl", "=", -1))]
       + [a("Scene", "", "\"Juego\"", "")]),
    ev([gnum("SonidoActivo", "=", 1), c("DepartScene", "")], [a("PlayMusic", "", "\"musica/menu.ogg\"", "yes", "60", "1")]),
]
# --- Menú: modo -> unirse -> equipo -> dificultad ---
men_obj = [obj_texto("TxtMenu", 40, "255;255;255", "center"), obj_texto("TxtSlots", 34, "255;235;140", "left"), obj_texto("TxtPie", 26, "190;210;255", "center")]
men_inst = [ti("TxtMenu", 960, 80), ti("TxtSlots", 300, 300), ti("TxtPie", 960, 980)]
MV = [var("Paso", "modo"), var("Sel", 0), var("M0", ""), var("M1", ""), var("M2", ""), var("JefeLinea", "")] + [var(f"{p_}{k}", "") for p_ in ("C", "N", "OK") for k in range(1, 5)]
MV_BASE = MV
MV = MV_BASE + [var(f"S{k}Ctl", -1) for k in range(1, 5)] + [var(f"S{k}Pj", k - 1) for k in range(1, 5)] + \
     [var(f"S{k}Ok", 0) for k in range(1, 5)]
def anterior(k): return o_(*([suelta("a"), suelta("Left")] if True else []))
men_ev = [
    comentario("Orden corto para llegar a jugar en menos de 1 minuto: modo, unirse, elegir equipo, dificultad."),
    ev([c("DepartScene", "")], [svt("Paso", "\"modo\""), svar("S1Ctl", "=", 0)]),
    # modo
    ev([], [svt("M0", "\"   \""), svt("M1", "\"   \""), svt("M2", "\"   \"")]),
    ev([cvar("Sel", "=", 0)], [svt("M0", "\">> \"")]), ev([cvar("Sel", "=", 1)], [svt("M1", "\">> \"")]), ev([cvar("Sel", "=", 2)], [svt("M2", "\">> \"")]),
    ev([cvt("Paso", "\"modo\"")], [texto("TxtMenu", "\"ELIGE EL MODO\" + NewLine() + NewLine() + VariableString(M0) + \"1  ESCAPE (1 a 4 jugadores + bots)\" + NewLine() + "
                                    "VariableString(M1) + \"2  JEFE DE ZOMBIES (1 a 3 contra el Jefe con ratón)\""),
                                   texto("TxtPie", "\"↑↓ / stick para elegir · Enter / A para aceptar\"")]),
    ev([cvt("Paso", "\"modo\""), o_(suelta("Up"), suelta("w"), suelta("Down"), suelta("s"), *[pad_suelta(k, "Up") for k in range(1, 5)], *[pad_suelta(k, "Down") for k in range(1, 5)])],
       [svar("Sel", "=", "1 - Variable(Sel)")]),
    ev([cvt("Paso", "\"modo\""), suelta("Num1")], [svar("Sel", "=", 0)]), ev([cvt("Paso", "\"modo\""), suelta("Num2")], [svar("Sel", "=", 1)]),
    ev([cvt("Paso", "\"modo\""), CONTINUAR(), once()], [svt("Paso", "\"unirse\""), sreset("paso")], sub=[
        ev([cvar("Sel", "=", 0)], [gsett("Modo", "\"escape\""), svar("S1Ctl", "=", 0)]),
        ev([cvar("Sel", "=", 1)], [gsett("Modo", "\"jefe\""), svar("S1Ctl", "=", -1)])]),
]
# unirse
for k in range(1, 5):
    men_ev += [ev([cvar(f"S{k}Ctl", "=", -1)], [svt(f"C{k}", "\"BOT\"")]), ev([cvar(f"S{k}Ctl", "=", 0)], [svt(f"C{k}", "\"teclado y ratón\"")]),
               ev([cvar(f"S{k}Ctl", ">", 0)], [svt(f"C{k}", "\"control \" + ToString(Variable(S" + str(k) + "Ctl))")]),
               ev([], [svt(f"OK{k}", "\"\"")]), ev([cvar(f"S{k}Ok", "=", 1)], [svt(f"OK{k}", "\"  LISTO\"")])]
    men_ev += [ev([cvar(f"S{k}Pj", "=", i)], [svt(f"N{k}", f"\"{NOMB[pj]} — {DESC[pj]}\"")]) for i, pj in enumerate(PJS)]
men_ev += [ev([], [svt("JefeLinea", "\"\"")]), ev([gtxt("Modo", "\"jefe\"")], [svt("JefeLinea", "\"JEFE: ratón (los sobrevivientes juegan con control)\"")])]
men_ev.append(ev([cvt("Paso", "\"unirse\"")], [texto("TxtMenu", "\"ÚNANSE\" + NewLine() + \"Presiona A en tu control para unirte\""),
    texto("TxtSlots", " + ".join(f"\"P{k}: \" + VariableString(C{k}) + NewLine()" for k in range(1, 5)) + " + VariableString(JefeLinea)"),
    texto("TxtPie", "\"Enter / Start para seguir\"")]))
for pad in range(1, 5):
    men_ev.append(ev([cvt("Paso", "\"unirse\""), pad_suelta(pad, "A")] + [cvar(f"S{k}Ctl", "!=", pad) for k in range(1, 5)], [], sub=[
        ev([cvar(f"S{k}Ctl", "=", -1), cvar("Hecho", "=", 0)] + ([cmp("1", "=", "1")] if True else []), [svar(f"S{k}Ctl", "=", pad), svar("Hecho", "=", 1)])
        for k in range(1, 5)] + [ev([], [svar("Hecho", "=", 0)])]))
men_ev.append(ev([cvt("Paso", "\"unirse\""), stimer("paso", 0.3), o_(suelta("Return"), *[pad_suelta(k, "START") for k in range(1, 5)])],
                 [svt("Paso", "\"equipo\""), sreset("paso")]))
# equipo: cada humano cambia con izq/der y confirma
men_ev.append(ev([cvt("Paso", "\"equipo\"")], [texto("TxtMenu", "\"ELIGEN SU PERSONAJE\""),
    texto("TxtSlots", " + ".join(f"\"P{k} (\" + VariableString(C{k}) + \"): \" + VariableString(N{k}) + VariableString(OK{k}) + NewLine() + NewLine()" for k in range(1, 5))),
    texto("TxtPie", "\"Teclado: A/D cambiar, F aceptar · Control: ←/→ cambiar, A aceptar · Enter / Start: empezar (los bots se eligen solos)\"")]))
for k in range(1, 5):
    izq = o_(c("BuiltinCommonInstructions::And", ) if False else suelta("a"), suelta("Left"))
    men_ev += [
        ev([cvt("Paso", "\"equipo\""), cvar(f"S{k}Ctl", "=", 0), cvar(f"S{k}Ok", "=", 0), o_(suelta("a"), suelta("Left"))], [svar(f"S{k}Pj", "=", f"mod(Variable(S{k}Pj) + 7, 8)")]),
        ev([cvt("Paso", "\"equipo\""), cvar(f"S{k}Ctl", "=", 0), cvar(f"S{k}Ok", "=", 0), o_(suelta("d"), suelta("Right"))], [svar(f"S{k}Pj", "=", f"mod(Variable(S{k}Pj) + 1, 8)")]),
        ev([cvt("Paso", "\"equipo\""), cvar(f"S{k}Ctl", "=", 0), suelta("f")], [svar(f"S{k}Ok", "=", "1 - Variable(S" + str(k) + "Ok)")]),
    ]
    for pad in range(1, 5):
        men_ev += [
            ev([cvt("Paso", "\"equipo\""), cvar(f"S{k}Ctl", "=", pad), cvar(f"S{k}Ok", "=", 0), pad_suelta(pad, "Left")], [svar(f"S{k}Pj", "=", f"mod(Variable(S{k}Pj) + 7, 8)")]),
            ev([cvt("Paso", "\"equipo\""), cvar(f"S{k}Ctl", "=", pad), cvar(f"S{k}Ok", "=", 0), pad_suelta(pad, "Right")], [svar(f"S{k}Pj", "=", f"mod(Variable(S{k}Pj) + 1, 8)")]),
            ev([cvt("Paso", "\"equipo\""), cvar(f"S{k}Ctl", "=", pad), stimer("paso", 0.3), pad_suelta(pad, "A")], [svar(f"S{k}Ok", "=", "1 - Variable(S" + str(k) + "Ok)")]),
        ]
# personajes repetidos: el siguiente slot salta al siguiente libre
for k in range(2, 5):
    for j in range(1, k):
        men_ev.append(ev([cvt("Paso", "\"equipo\""), cmp(f"Variable(S{k}Pj)", "=", f"Variable(S{j}Pj)"), cvar(f"S{k}Ok", "=", 0)],
                         [svar(f"S{k}Pj", "=", f"mod(Variable(S{k}Pj) + 1, 8)")]))
men_ev.append(ev([cvt("Paso", "\"equipo\""), stimer("paso", 0.3), o_(suelta("Return"), *[pad_suelta(k, "START") for k in range(1, 5)])],
                 [svt("Paso", "\"dificultad\""), sreset("paso"), svar("Sel", "=", 1)]))
# dificultad
men_ev += [
    ev([cvt("Paso", "\"dificultad\"")], [texto("TxtMenu", "\"DIFICULTAD\" + NewLine() + NewLine() + VariableString(M0) + \"FÁCIL\" + NewLine() + "
                                         "VariableString(M1) + \"NORMAL\" + NewLine() + VariableString(M2) + \"PESADILLA\""),
                                         texto("TxtSlots", "\"\""), texto("TxtPie", "\"↑↓ elegir · Enter / A empezar\"")]),
    ev([cvt("Paso", "\"dificultad\""), o_(suelta("Up"), suelta("w"), *[pad_suelta(k, "Up") for k in range(1, 5)])], [svar("Sel", "=", "mod(Variable(Sel) + 2, 3)")]),
    ev([cvt("Paso", "\"dificultad\""), o_(suelta("Down"), suelta("s"), *[pad_suelta(k, "Down") for k in range(1, 5)])], [svar("Sel", "=", "mod(Variable(Sel) + 1, 3)")]),
    ev([cvt("Paso", "\"dificultad\""), stimer("paso", 0.3), CONTINUAR(), once()], [gset("Listo", "=", 1), gset("SinRecord", "=", 0)], sub=[
        ev([cvar("Sel", "=", 0)], [gsett("Dificultad", "\"facil\""), gset("DifInf", "=", 0.7), gset("DifVida", "=", 0.75), gset("DifDanio", "=", 0.7), gset("DifHorda", "=", 0.75)]),
        ev([cvar("Sel", "=", 1)], [gsett("Dificultad", "\"normal\""), gset("DifInf", "=", 1), gset("DifVida", "=", 1), gset("DifDanio", "=", 1), gset("DifHorda", "=", 1)]),
        ev([cvar("Sel", "=", 2)], [gsett("Dificultad", "\"pesadilla\""), gset("DifInf", "=", 1.45), gset("DifVida", "=", 1.3), gset("DifDanio", "=", 1.3), gset("DifHorda", "=", 1.35)]),
    ] + [ev([cvar(f"S{k}Pj", "=", i)], [gsett(f"P{k}Pj", f"\"{pj}\"")]) for k in range(1, 5) for i, pj in enumerate(PJS)]
      + [ev([], [gset(f"P{k}Ctl", "=", f"Variable(S{k}Ctl)") for k in range(1, 5)] + [a("Scene", "", "\"Juego\"", "")])]),
]
# --- Resultados ---
res_obj = [obj_texto("TxtRes", 96, "255;235;120", "center"), obj_texto("TxtDet", 34, "255;255;255", "center"), obj_texto("TxtPie", 26, "190;210;255", "center")]
res_inst = [ti("TxtRes", 960, 120), ti("TxtDet", 960, 330), ti("TxtPie", 960, 980)]
res_ev = [
    ev([c("DepartScene", "")], [texto("TxtRes", "\"LOS ATRAPARON\"")]), ev([c("DepartScene", ""), gtxt("Resultado", "\"victoria\"")], [texto("TxtRes", "\"¡ESCAPARON!\"")]),
    ev([], [svt("Rec", "\"\"")]), ev([gnum("SinRecord", "=", 1)], [svt("Rec", "\"(se usó el modo presentación: no cuenta para récord)\"")]),
    ev([c("DepartScene", "")], [
        texto("TxtDet", "\"Tiempo: \" + ToString(floor(GlobalVariable(TiempoFinal) / 60)) + \" min \" + ToString(floor(mod(GlobalVariable(TiempoFinal), 60))) + \" s\" + "
                        "\"   ·   Dificultad: \" + GlobalVariableString(Dificultad) + NewLine() + NewLine() + GlobalVariableString(Premios) + "
                        "NewLine() + VariableString(Rec)"),
        texto("TxtPie", "\"Enter / A: volver al título\""), gset("Demo", "=", 0)], sub=[
        ev([gtxt("Resultado", "\"victoria\""), gnum("SinRecord", "=", 0), o_(gnum("MejorTiempo", "=", 0), c("VarGlobal", "MejorTiempo", ">", "GlobalVariable(TiempoFinal)"))],
           [gset("MejorTiempo", "=", "GlobalVariable(TiempoFinal)")]),
        sonido("efectos/eventos/" + "victoria.ogg")]),
    ev([gtxt("Resultado", "\"victoria\"", "!="), c("DepartScene", ""), gnum("SonidoActivo", "=", 1)], [a("PlayMusic", "", "\"musica/derrota.ogg\"", "no", "70", "1")]),
    ev([gtxt("Resultado", "\"victoria\""), c("DepartScene", ""), gnum("SonidoActivo", "=", 1)], [a("PlayMusic", "", "\"musica/victoria.ogg\"", "no", "70", "1")]),
    ev([stimer("t", 1), CONTINUAR()], [a("Scene", "", "\"Titulo\"", "")]),
    ev([c("DepartScene", "")], [sreset("t")]),
]
ESC_NUEVAS = [escena("Titulo", tit_obj, tit_inst, tit_ev), escena("Menu", men_obj, men_inst, men_ev, MV + [var("Hecho", 0)]),
              escena("Resultados", res_obj, res_inst, res_ev, [var("Rec", "")])]
p["layouts"] = [l for l in p["layouts"] if l["name"] not in ("Titulo", "Menu", "Resultados")]
p["layouts"] = [ESC_NUEVAS[0], ESC_NUEVAS[1]] + p["layouts"] + [ESC_NUEVAS[2]]
p["layoutsFolderStructure"] = {"folderName": "__ROOT", "children": [{"itemName": n} for n in ("Titulo", "Menu", "Juego", "Resultados")]}
p["firstLayout"] = "Titulo"
p["resources"]["resources"] = list(recursos.values())
json.dump(p, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("OK fases 6-11:", len(G), "grupos nuevos;", len(triples), "combinaciones de objetivos; escenas:", [l["name"] for l in p["layouts"]])
