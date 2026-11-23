"""Fase 69 · Correcciones (pistola inicial, daño de armas, Historia solo con Tony, mundo sin congelar, menú de modos, CIC,
Joel y casillero). Idempotente. Va DESPUÉS de fase68_historia.py (que incrusta historia.js, usar.js, profes.js, dialogo.js y
cine.js); esta fase incrusta armas.js y cambia eventos, objetos e instancias.

Uso (desde la carpeta fdiz, con GDevelop CERRADO):
    python gdevelop/scripts/fase68_historia.py
    python gdevelop/scripts/fase69_correcciones.py
    node gdevelop/scripts/prueba_historia2.js

Qué cambia:
  Fase 2 · Daño de las armas de fuego (todos los modos)
    * Cada zombi guarda su vida completa (VidaIni) al aplicarle la dificultad (evento DifOk).
    * Cada proyectil de arma de fuego lleva Golpes: 2 = pistola pequeña (mata exactamente en 2 impactos), 1 = sheriff y
      escopeta (matan en 1). Al pegar: daño = un impacto: max(daño del arma, VidaIni + 0.01); dos impactos:
      min(VidaIni - 0.01, max(daño del arma, VidaIni / 2 + 0.01)). Los lanzables (Golpes 0) no cambian.
    * Un proyectil no pega a un zombi que ya está a 0 de vida (perdigones: una sola muerte, un solo contador).
    * La bala y el perdigón hacen la misma reacción que el puñetazo: tinte rojo, empujón de 280, salpicadura y temblor.
  Fase 3 · Historia solo con Tony
    * Menú: HISTORIA va directo a la dificultad con Tony en P1 (con el teclado o el mando con que se eligió) y Miranda,
      Alan y César como bots. Escape vuelve a ELIGE EL MODO. (historia.js también lo fuerza al empezar la partida.)
    * Sup: tony_pistola_lado = los 4 cuadros de animaciones_gif/personajes/tony/tony_disparar_lado_pistola.gif y nueva
      tony_escopeta_lado (tony_disparar_lado_escopeta.gif). Hacia la izquierda se voltean, como todas las de "lado".
  Fase 5 · La pausa no se abre durante una escena de la historia (HistBloq = 1); el mundo sigue (historia.js).
  Fase 6 · Menú de modos: HISTORIA | ESCAPE | JEFE DE ZOMBIES, con las ilustraciones de Historia y Escape intercambiadas.
  Fase 7 · CIC: se quita la engrapadora que flotaba sobre el muro (2936, 1625) y el reloj sube a la pared (3424, 1650).
  Fase 8 · Joel espera dentro de la Sala 2 (puerta P38 en 3744, 1792), en (3990, 1965).
"""
import copy, datetime, json, os, shutil, sys
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
PRY = os.path.join(RAIZ, "gdevelop", "FDI-Z", "FDI-Z.json")
GEN = os.path.join(RAIZ, "generado", "sprites")
GIFS = os.path.join(RAIZ, "animaciones_gif", "personajes", "tony")
DATOS = os.path.join(RAIZ, "mapa", "final", "mapa_fdiz_datos.json")
PROPS = os.path.join(RAIZ, "mapa", "final", "mapa_fdiz_props.json")
MK = "FDIZ-FASE69"
ZOMBIS = ["ZNormal", "ZCorredor", "ZGriton", "ZGordo", "ZConserje", "ZJoel", "ZJustino", "ZCanepa"]
JOEL = (3990, 1965)
RELOJ = (3424, 1690, 1650)          # x, y antes, y nueva
ENGRAPADORA = (2936, 1625)
DISPARO = {"pistola": "tony_disparar_lado_pistola.gif", "escopeta": "tony_disparar_lado_escopeta.gif"}
LIENZO = (160, 127)                  # el doble de ancho que los demás cuadros (80) para que quepa el arma; origen al centro
ORIGEN = (80, 125)
ALTO_CUERPO = 98                      # alto de Tony (de los pies a la cabeza) en sus cuadros de 80 x 127
SEG_CUADRO = 0.07                     # 4 cuadros = 0.28 s, lo que dura Atacando


def c(tipo, *p, inv=False):
    return {"type": {"inverted": inv, "value": tipo}, "parameters": list(p)}


def a(tipo, *p):
    return {"type": {"value": tipo}, "parameters": list(p)}


def recorrer(lst):
    for e in lst:
        yield e
        yield from recorrer(e.get("events", []))


def tiene(e, tipo, params):
    return any(x["type"]["value"] == tipo and x["parameters"][:len(params)] == params for x in e.get("conditions", []) + e.get("actions", []))


def grupo(ev, nombre):
    return next(e for e in ev if e.get("type", "").endswith("Group") and e.get("name") == nombre)


def var_obj(obj, nombre, valor=0):
    if not any(v["name"] == nombre for v in obj["variables"]):
        obj["variables"].append({"name": nombre, "type": "string" if isinstance(valor, str) else "number", "value": valor})


def es_js(e, marca):
    return e.get("type", "").endswith("JsCode") and e.get("inlineCode", "").startswith("/*" + marca + "*/")


# ------------------------------------------------------------------ arte: cuadros de disparo de Tony
def cuadros_gif(ruta):
    """Cuadros distintos de un ciclo (el GIF repite cada cuadro con 70 ms + 30 ms)."""
    im = Image.open(ruta)
    out = []
    for i in range(im.n_frames):
        im.seek(i)
        f = im.convert("RGBA")
        if out and f.tobytes() == out[-1].tobytes():
            continue
        if out and f.tobytes() == out[0].tobytes():
            break
        out.append(f.copy())
    return out


def anclas(f):
    """Pies (y) y centro del cuerpo (x, por las piernas: el 20 % de abajo, sin el arma)."""
    caja = f.getbbox()
    alto = caja[3] - caja[1]
    px = f.load()
    y0 = caja[3] - int(alto * 0.2)
    xs = [x for x in range(f.size[0]) for y in range(y0, caja[3]) if px[x, y][3] > 128]
    return caja[1], caja[3], (min(xs) + max(xs)) / 2


def arte_tony():
    hechos = {}
    for arma, gif in DISPARO.items():
        cuadros = cuadros_gif(os.path.join(GIFS, gif))
        top, pie, cx = anclas(cuadros[0])
        s = ALTO_CUERPO / (pie - top)
        carpeta = os.path.join(GEN, "personajes", "tony", "disparo_%s_lado" % arma)
        os.makedirs(carpeta, exist_ok=True)
        nombres = []
        for k, f in enumerate(cuadros):
            g = f.resize((max(1, round(f.size[0] * s)), max(1, round(f.size[1] * s))), Image.LANCZOS)
            al = g.getchannel("A").point(lambda v: 255 if v >= 110 else 0)      # bordes nítidos, como el resto del arte
            g.putalpha(al)
            lienzo = Image.new("RGBA", LIENZO, (0, 0, 0, 0))
            lienzo.alpha_composite(g, (round(ORIGEN[0] - cx * s), round(ORIGEN[1] - pie * s)))
            nombre = "disparo_%s_lado_%02d.png" % (arma, k)
            lienzo.save(os.path.join(carpeta, nombre))
            nombres.append("personajes/tony/disparo_%s_lado/%s" % (arma, nombre))
        hechos[arma] = nombres
    return hechos


def animacion(nombre, imagenes):
    mask = [[{"x": ORIGEN[0] - 20, "y": 109}, {"x": ORIGEN[0] + 20, "y": 109}, {"x": ORIGEN[0] + 20, "y": 125}, {"x": ORIGEN[0] - 20, "y": 125}]]
    return {"name": nombre, "useMultipleDirections": False, "directions": [{"looping": False, "timeBetweenFrames": SEG_CUADRO, "sprites": [
        {"hasCustomCollisionMask": True, "image": im, "points": [], "originPoint": {"name": "origine", "x": ORIGEN[0], "y": ORIGEN[1]},
         "centerPoint": {"automatic": True, "name": "centre", "x": 0, "y": 0}, "customCollisionMask": mask} for im in imagenes]}]}


# ------------------------------------------------------------------ main
def main():
    d = json.load(open(PRY, encoding="utf-8"))
    resp = os.path.join(RAIZ, "gdevelop", "respaldos")
    bak = os.path.join(resp, "antes_de_fase69_%s.json" % datetime.date.today().strftime("%Y%m%d"))
    if not os.path.exists(bak):
        shutil.copy(PRY, bak)
    J = next(l for l in d["layouts"] if l["name"] == "Juego")
    M = next(l for l in d["layouts"] if l["name"] == "Menu")
    ob = {o["name"]: o for o in J["objects"]}
    ev = J["events"]
    res = d["resources"]["resources"]

    # ---------------- fase 3: animaciones de disparo de Tony
    arte = arte_tony()
    nombres = {r["name"] for r in res}
    for arma, imgs in arte.items():
        for im in imgs:
            if im not in nombres:
                res.append({"file": "../../generado/sprites/" + im, "kind": "image", "metadata": "", "name": im, "smoothed": False, "userAdded": True})
    sup = ob["Sup"]
    for arma, imgs in arte.items():
        nombre = "tony_%s_lado" % arma
        nueva = animacion(nombre, imgs)
        k = next((i for i, x in enumerate(sup["animations"]) if x["name"] == nombre), None)
        if k is None:
            sup["animations"].append(nueva)
        else:
            sup["animations"][k] = nueva

    # ---------------- fase 2: daño de las armas de fuego
    for z in ZOMBIS:
        var_obj(ob[z], "VidaIni", 0)
    var_obj(ob["Proyectil"], "Golpes", 0)
    conf = grupo(ev, "Configuración y dificultad")["events"]
    dif = next(e for e in conf if tiene(e, "ModVarObjet", ["Zombies", "DifOk", "=", "1"]))
    if not tiene(dif, "ModVarObjet", ["Zombies", "VidaIni"]):
        dif["actions"].append(a("ModVarObjet", "Zombies", "VidaIni", "=", "Zombies.Variable(Vida)"))
    comb = grupo(ev, "Combate: pegar")
    golpes = {"pistolita": "2", "pistola": "1", "escopeta": "1"}
    for e in recorrer(comb["events"]):
        arma = next((x["parameters"][3].strip('"') for x in e.get("conditions", []) if x["type"]["value"] == "VarObjetTxt" and x["parameters"][:3] == ["Sup", "Arma", "="]), None)
        if arma not in golpes or not tiene(e, "Create", ["", "Proyectil"]):
            continue
        acts = [x for x in e["actions"] if not tiene({"actions": [x]}, "ModVarObjet", ["Proyectil", "Golpes"])]
        nuevas = []
        for x in acts:
            nuevas.append(x)
            if x["type"]["value"] == "Create" and x["parameters"][1] == "Proyectil":
                nuevas.append(a("ModVarObjet", "Proyectil", "Golpes", "=", golpes[arma]))
        e["actions"] = nuevas
    lz = grupo(ev, "Lanzables")
    hit = next(e for e in recorrer(lz["events"]) if tiene(e, "ModVarObjet", ["Zombies", "Vida", "-", "Proyectil.Variable(Danio)"]))
    if not tiene(hit, "VarObjet", ["Zombies", "Vida", ">", "0"]):
        k = next(i for i, x in enumerate(hit["conditions"]) if x["type"]["value"] == "PickNearest")
        hit["conditions"].insert(k, c("VarObjet", "Zombies", "Vida", ">", "0"))
    G, H, D = "Proyectil.Variable(Golpes)", "max(Zombies.Variable(VidaIni), Zombies.Variable(Vida))", "Proyectil.Variable(Danio)"
    uno, dos = "max(%s, %s + 0.01)" % (D, H), "min(%s - 0.01, max(%s, %s * 0.5 + 0.01))" % (H, D, H)
    expr = "%s * (1 - %s) * (2 - %s) / 2 + %s * %s * (2 - %s) + %s * %s * (%s - 1) / 2" % (D, G, G, uno, G, G, dos, G, G)
    hit["actions"] = [x for x in hit["actions"] if not (x["type"]["value"] == "ModVarObjet" and x["parameters"][:3] == ["Proyectil", "Danio", "="])]
    hit["actions"].insert(0, a("ModVarObjet", "Proyectil", "Danio", "=", expr))
    for s in hit["events"]:
        tipo = next((x["parameters"][3] for x in s.get("conditions", []) if x["type"]["value"] == "VarObjetTxt" and x["parameters"][:3] == ["Proyectil", "Tipo", "="]), None)
        if tipo not in ('"bala"', '"perdigon"'):
            continue
        s["actions"] = [a("AddForceVersPos", "Zombies", "Proyectil.X()", "Proyectil.Y() + 40", "-280", "0"),
                        a("Create", "", "Salpicadura", "Zombies.X()", "Zombies.Y() - 48", '"Juego"'),
                        a("ResetObjectTimer", "Salpicadura", '"vida"'),
                        a("ModVarScene", "Temblor", "=", "0.12")]

    # ---------------- fase 5: sin pausa durante una escena de la historia
    if not any(v["name"] == "HistBloq" for v in J["variables"]):
        J["variables"].append({"name": "HistBloq", "type": "number", "value": 0})
    pausa = grupo(ev, "Menú de pausa")
    abre = next(e for e in recorrer(pausa["events"]) if tiene(e, "VarScene", ["ProfDlg", "=", "0"]) and tiene(e, "VarSceneTxt", ["Estado", "=", '"juego"']))
    if not tiene(abre, "VarScene", ["HistBloq"]):
        abre["conditions"].insert(1, c("VarScene", "HistBloq", "=", "0"))

    # ---------------- fase 4: la cámara sigue al jugador también mientras está sin control (Control -2: escenas guionizadas)
    cam = grupo(ev, "Cámara compartida")["events"]
    for e in cam:
        if e.get("type", "").endswith(("Standard", "ForEach")) and tiene(e, "VarObjetTxt", ["Sup", "Estado", "=", '"normal"']) \
                and (tiene(e, "VarObjet", ["Sup", "Control", ">=", "0"]) or tiene(e, "VarObjet", ["Sup", "Control", ">=", "-2"])) \
                and (tiene(e, "ModVarScene", ["Humanos"]) or tiene(e, "ModVarScene", ["CamN", "+", "1"])):
            for x in e["conditions"]:
                if x["type"]["value"] == "VarObjet" and x["parameters"][:3] == ["Sup", "Control", ">="]:
                    x["parameters"][3] = "-2"
            if not tiene(e, "VarObjet", ["Sup", "Control", "!=", "-1"]):
                e["conditions"].append(c("VarObjet", "Sup", "Control", "!=", "-1"))

    # ---------------- fase 7: CIC
    J["instances"] = [i for i in J["instances"] if not (i["name"] == "LanzPiso" and (round(i["x"]), round(i["y"])) == ENGRAPADORA)]
    for i in J["instances"]:
        v = {x["name"]: x.get("value") for x in i.get("initialVariables", [])}
        if i["name"] == "Mueble" and v.get("Sprite") == "senaletica/reloj_pared" and round(i["x"]) == RELOJ[0] and round(i["y"]) in (RELOJ[1], RELOJ[2]):
            i["y"] = RELOJ[2]; i["zOrder"] = RELOJ[2]
    props = json.load(open(PROPS, encoding="utf-8"))
    for p in props if isinstance(props, list) else props.get("props", []):
        if p.get("sprite") == "senaletica/reloj_pared" and p.get("x") == RELOJ[0] and p.get("y") == RELOJ[1]:
            p["y"] = RELOJ[2]
    json.dump(props, open(PROPS, "w", encoding="utf-8"), ensure_ascii=False, indent=0)

    # ---------------- fase 8: Joel en la Sala 2 (puerta P38)
    for i in J["instances"]:
        v = {x["name"]: x.get("value") for x in i.get("initialVariables", [])}
        if i["name"] == "Profe" and v.get("Nombre") == "joel":
            i["x"], i["y"], i["zOrder"] = JOEL[0], JOEL[1], JOEL[1]
    datos = json.load(open(DATOS, encoding="utf-8"))
    mk = datos["marcadores"].get("joel_rescate")
    if mk:
        mk.update({"x": float(JOEL[0]), "y": float(JOEL[1]), "zona": "Sala 2", "nota": "fase 69: dentro de la Sala 2 (puerta P38)"})
        json.dump(datos, open(DATOS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # ---------------- armas.js (animación de escopeta)
    src = open(os.path.join(AQUI, "armas.js"), encoding="utf-8").read()
    n = 0
    for e in recorrer(ev):
        if es_js(e, "FDIZ-FASE62-MOD"):
            e["inlineCode"] = "/*FDIZ-FASE62-MOD*/\n" + src; n += 1
    if n != 1:
        sys.exit("No encontré FDIZ-FASE62-MOD")

    # ---------------- Menú: fase 6 (orden y figuras) y fase 3 (Historia directo a dificultad con Tony)
    me = M["events"]
    MODO = ["Paso", "=", '"modo"']
    # posiciones de las tarjetas: Historia (Idx 2) izquierda, Escape (Idx 0) centro, Jefe (Idx 1) derecha
    POS = {("MarcoModo", "0"): "740", ("IlusModo", "0"): "790", ("MarcoModo", "1"): "1320", ("IlusModo", "1"): "1370",
           ("MarcoModo", "2"): "160", ("IlusModo", "2"): "210"}
    CENTRO = {"0": "960", "1": "1540", "2": "380"}
    for e in recorrer(me):
        cs = e.get("conditions", [])
        en_modo = any(x["type"]["value"] == "VarSceneTxt" and x["parameters"][:3] == MODO for x in cs)
        no_jt = any(x["type"]["value"] == "VarSceneTxt" and x["parameters"][:3] == ["Paso", "!=", '"jefetipo"'] for x in cs)
        idx = next(((x["parameters"][0], x["parameters"][3]) for x in cs if x["type"]["value"] == "VarObjet" and x["parameters"][1:3] == ["Idx", "="]), None)
        for x in e.get("actions", []):
            t, p = x["type"]["value"], x["parameters"]
            if en_modo and idx and t == "MettreX" and p[0] == idx[0] and (idx[0], idx[1]) in POS:
                p[2] = POS[(idx[0], idx[1])]
            if (en_modo or no_jt) and idx and idx[0] in ("TxtCapA", "TxtCapB") and t == "MettreX" and p[0] == idx[0]:
                p[2] = "%s - %s.Width() / 2" % (CENTRO[idx[1]], idx[0])
            if no_jt and idx == ("IlusModo", "0") and t == "SetAnimationName":
                p[1] = '"h"'                                       # Escape muestra la figura que tenía Historia
            if en_modo and t == "MettreX" and p[0] == "VidIlusJefe" and p[2] != "-6000":
                p[2] = "1370"
        # la figura de Historia (Idx 2) ya no se muestra en "modo": la que se muestra es la de Escape (Idx 0)
        if en_modo and idx == ("IlusModo", "2") and any(x["type"]["value"] == "Montre" for x in e.get("actions", [])):
            for x in cs:
                if x["type"]["value"] == "VarObjet" and x["parameters"][1:3] == ["Idx", "="]:
                    x["parameters"][3] = "0"
        # VidIlusEscape (la figura que tenía Escape) queda en x 210: la tarjeta de Historia
        # teclas 1, 2, 3 = Historia, Escape, Jefe
        if en_modo:
            tecla = next((x["parameters"][1] for x in cs if x["type"]["value"] == "KeyReleased" and x["parameters"][1] in ("Num1", "Num2", "Num3")), None)
            if tecla:
                for x in e["actions"]:
                    if x["type"]["value"] == "ModVarScene" and x["parameters"][0] == "Sel":
                        x["parameters"][2] = {"Num1": "2", "Num2": "0", "Num3": "1"}[tecla]
            # clic (y cursor) sobre cada tarjeta
            xs = [x for x in cs if x["type"]["value"] == "BuiltinCommonInstructions::CompareNumbers" and x["parameters"][0] == "MouseX()"]
            ors = [y for x in cs if x["type"]["value"] == "BuiltinCommonInstructions::Or" for y in x.get("subInstructions", [])]
            if len(xs) == 2 and not ors:
                hover = any(y["type"]["value"] == "BuiltinCommonInstructions::CompareNumbers" and "PMX" in y["parameters"][2] for x in cs for y in x.get("subInstructions", []))
                sel = next((x["parameters"][2] for x in e["actions"] if x["type"]["value"] == "ModVarScene" and x["parameters"][0] == "Sel"), None)
                rango = {"0": ("740", "1180"), "1": ("1320", "1760"), "2": ("160", "600")}.get(sel)
                if rango:
                    xs[0]["parameters"][2], xs[1]["parameters"][2] = rango
    # cursor: los eventos de "modo" que eligen con el ratón al moverlo (PMX) eran de cuando había 2 tarjetas
    for e in recorrer(me):
        cs = e.get("conditions", [])
        if not any(x["type"]["value"] == "VarSceneTxt" and x["parameters"][:3] == MODO for x in cs):
            continue
        if not any(x["type"]["value"] == "BuiltinCommonInstructions::Or" and any("PMX" in str(y["parameters"]) for y in x.get("subInstructions", [])) for x in cs):
            continue
        sel = next((x["parameters"][2] for x in e["actions"] if x["type"]["value"] == "ModVarScene" and x["parameters"][0] == "Sel"), None)
        xs = [x for x in cs if x["type"]["value"] == "BuiltinCommonInstructions::CompareNumbers" and x["parameters"][0] == "MouseX()"]
        rango = {"0": ("740", "1180"), "1": ("1320", "1760"), "2": ("160", "600")}.get(sel)
        if rango and len(xs) == 2:
            xs[0]["parameters"][2], xs[1]["parameters"][2] = rango
    hov = [e for e in me if any(x["type"]["value"] == "VarSceneTxt" and x["parameters"][:3] == MODO for x in e.get("conditions", []))
           and any(x["type"]["value"] == "BuiltinCommonInstructions::Or" and any("PMX" in str(y["parameters"]) for y in x.get("subInstructions", [])) for x in e.get("conditions", []))]
    if hov and not any(any(x["type"]["value"] == "ModVarScene" and x["parameters"][:3] == ["Sel", "=", "2"] for x in e["actions"]) for e in hov):
        nuevo = copy.deepcopy(hov[0])
        for x in nuevo["actions"]:
            if x["type"]["value"] == "ModVarScene" and x["parameters"][0] == "Sel":
                x["parameters"][2] = "2"
        xs = [x for x in nuevo["conditions"] if x["type"]["value"] == "BuiltinCommonInstructions::CompareNumbers" and x["parameters"][0] == "MouseX()"]
        xs[0]["parameters"][2], xs[1]["parameters"][2] = "160", "600"
        me.insert(me.index(hov[-1]) + 1, nuevo)
    # al entrar al menú, la tarjeta elegida es la primera (Historia)
    ini = next(e for e in me if tiene(e, "DepartScene", [""]) and tiene(e, "ModVarSceneTxt", ["Paso", "=", '"modo"']))
    if not tiene(ini, "ModVarScene", ["Sel", "=", "2"]):
        ini["actions"].append(a("ModVarScene", "Sel", "=", "2"))
    # HISTORIA: directo a la dificultad, con Tony en P1 y los demás como bots (fase 3)
    conf_modo = next(e for e in recorrer(me) if any(x["type"]["value"] == "VarScene" and x["parameters"][:3] == ["Sel", "=", "2"] for x in e.get("conditions", []))
                     and tiene(e, "ModVarGlobalTxt", ["Modo", "=", '"historia"']))
    acts = [x for x in conf_modo["actions"] if not (x["type"]["value"] in ("ModVarSceneTxt", "ModVarScene") and x["parameters"][0] in
                                                     ("Paso", "Sel", "S1Pj", "S2Pj", "S3Pj", "S4Pj", "S2Ctl", "S3Ctl", "S4Ctl", "S1Ok", "S2Ok", "S3Ok", "S4Ok"))]
    acts += [a("ModVarSceneTxt", "Paso", "=", '"dificultad"'), a("ModVarScene", "Sel", "=", "1"),
             a("ModVarScene", "S1Pj", "=", "0"), a("ModVarScene", "S2Pj", "=", "1"), a("ModVarScene", "S3Pj", "=", "3"), a("ModVarScene", "S4Pj", "=", "2"),
             a("ModVarScene", "S2Ctl", "=", "-1"), a("ModVarScene", "S3Ctl", "=", "-1"), a("ModVarScene", "S4Ctl", "=", "-1")]
    conf_modo["actions"] = acts
    conf_modo["events"] = [x for x in conf_modo.get("events", []) if not tiene(x, "Gamepads::C_Button_released", [""])]
    for k in range(1, 5):   # si se eligió con un mando, ese mando es el de Tony
        conf_modo["events"].insert(0, {"type": "BuiltinCommonInstructions::Standard", "events": [],
                                       "conditions": [c("Gamepads::C_Button_released", "", str(k), '"A"', "")],
                                       "actions": [a("ModVarScene", "S1Ctl", "=", str(k))]})
    # Escape en la dificultad: en Historia vuelve a ELIGE EL MODO (no hay pantalla de equipo)
    atras = next(e for e in me if tiene(e, "VarSceneTxt", ["Paso", "=", '"dificultad"']) and tiene(e, "ModVarSceneTxt", ["Paso", "=", '"equipo"']))
    if not tiene(atras, "VarGlobalTxt", ["Modo", "!=", '"historia"']):
        atras["conditions"].append(c("VarGlobalTxt", "Modo", "!=", '"historia"'))
    if not any(tiene(e, "VarGlobalTxt", ["Modo", "=", '"historia"']) and tiene(e, "VarSceneTxt", ["Paso", "=", '"dificultad"']) and tiene(e, "ModVarSceneTxt", ["Paso", "=", '"modo"']) for e in me):
        nuevo = copy.deepcopy(atras)
        nuevo["conditions"] = [x for x in nuevo["conditions"] if not (x["type"]["value"] == "VarGlobalTxt" and x["parameters"][0] == "Modo")]
        nuevo["conditions"].append(c("VarGlobalTxt", "Modo", "=", '"historia"'))
        nuevo["actions"] = [a("ModVarSceneTxt", "Paso", "=", '"modo"'), a("ModVarScene", "Sel", "=", "2"), a("ResetTimer", "", '"paso"')]
        me.insert(me.index(atras) + 1, nuevo)
    for e in recorrer(me):
        for x in e.get("actions", []):
            if x["type"]["value"] == "TextObject::String" and x["parameters"][0] == "TxtCapB":
                x["parameters"][-1] = x["parameters"][-1].replace("12 pasos con cinemáticas · 1 a 4 jugadores", "12 pasos con cinemáticas · juegas como Tony")

    tmp = PRY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=2))
    os.replace(tmp, PRY)
    print("Fase 69 aplicada. Cuadros de Tony:", {k: len(v) for k, v in arte.items()})


if __name__ == "__main__":
    main()
