"""Fase 19 de FDI-Z (13 nov 2026): segunda tanda de correcciones pedidas por Tony. Se aplica SOBRE el FDI-Z.json actual
(no regenera nada) y es idempotente. Correr con GDevelop cerrado (o recargar sin guardar):
    python fase19_correcciones.py <FDI-Z.json>
Antes correr una vez:  python fase19_botones.py <FDI-Z/assets/interfaz>   (limpia y unifica los botones de dificultad)

1. Botones de dificultad: sin la placa gris horneada en la imagen, los tres del mismo tamano (480x168), texto claro con borde.
2. Zombis: animacion atacar_arriba (cuadros de caminar_arriba con una embestida hacia arriba) para los 5 tipos.
3. Efecto de golpe: estaba invertido (el arco "C" apuntaba hacia el personaje). Se gira 180 grados.
4. Zombis que no desaparecian: quedaban con la animacion de morir en pausa (la pausa de la fase 18). Ahora la reanudan y,
   por seguridad, se borran 1.2 s despues de morir.
5. Tony en modo Gym: los cuadros de tonyfuerte eran mas chicos que los de Tony. Se escalan x1.09 (carpeta personajes_p19)
   y se agregan las animaciones que faltaban (pegar arriba/abajo, caer, festejo, habilidad, especial).
6. Rutas de Cesar: la linea recta se reemplaza por un camino calculado con el A* del juego (evita muros, muebles y salones),
   se recalcula cada 0.6 s mientras dura (14 s) y los puntos son mas grandes, con borde oscuro.
7. Pantalla de derrota: botones REINICIAR (R, Enter, Espacio o clic: misma seleccion de personajes) y MENU (Esc o clic).
   Si hay un solo jugador humano con 3 bots y cae, es derrota inmediata.
"""
import copy, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gd_util import c, a, ev, var, res_imagen, animacion

ruta = sys.argv[1]
RAIZ = os.path.dirname(os.path.abspath(ruta))
GEN = os.path.normpath(os.path.join(RAIZ, "..", "..", "generado", "sprites"))
p = json.load(open(ruta, encoding="utf-8"))

def lay(n): return next(l for l in p["layouts"] if l["name"] == n)
def obj(l, n): return next((o for o in l["objects"] if o["name"] == n), None)
def es_grupo(e, nombre): return e.get("type", "").endswith("Group") and e.get("name") == nombre
def cmp(e1, op, e2): return c("BuiltinCommonInstructions::CompareNumbers", e1, op, e2)
def recorrer(evs):
    for e in evs:
        yield e
        yield from recorrer(e.get("events", []))
def quitar_tag(evs, tag):
    n = 0
    for e in list(evs):
        if e.get(tag):
            evs.remove(e); n += 1
        else:
            n += quitar_tag(e.get("events", []), tag)
    return n
def marcado(e): e["fdiz19"] = True; return e
RES = {r["name"]: r for r in p["resources"]["resources"]}
def add_res(nombre, archivo):
    if nombre in RES:
        RES[nombre]["file"] = archivo
    else:
        r = res_imagen(nombre, archivo); p["resources"]["resources"].append(r); RES[nombre] = r

J = lay("Juego")
M = lay("Menu")
R = lay("Resultados")

# =============================================================== 1. botones de dificultad
BASE_UI = "assets/interfaz/"
for n, k in (("facil", "facil"), ("normal_dificultad", "normal_dificultad"), ("dificil", "dificil")):
    add_res("p14_DifBtn_" + k, BASE_UI + "ui_boton_%s_p19.png" % n)
ys = iter((257, 461, 653))
for i in M["instances"]:
    if i["name"] == "DifBtn":
        i["x"], i["y"], i["width"], i["height"], i["customSize"] = 720, next(ys), 480, 168, True
txt = obj(M, "TxtDif")
txt["color"] = {"b": 200, "g": 240, "r": 255}
txt["content"].update({"color": "255;240;200", "isOutlineEnabled": True, "outlineColor": "20;16;40", "outlineThickness": 5})
print("botones de dificultad: OK")

# =============================================================== 2. atacar_arriba de los zombis
from PIL import Image
TIPOS = {"ZNormal": "normal", "ZCorredor": "corredor", "ZGriton": "griton", "ZGordo": "gordo", "ZConserje": "conserje"}
SUBE = [0, 5, 11, 4]          # px que sube el cuerpo en cada cuadro (embestida hacia arriba)
ORIG = [1, 2, 3, 2]           # cuadros de caminar_arriba que se reutilizan
for onombre, t in TIPOS.items():
    o = obj(J, onombre)
    if any(an["name"] == "atacar_arriba" for an in o["animations"]):
        continue
    cam = next(an for an in o["animations"] if an["name"] == "caminar_arriba")
    atq = next(an for an in o["animations"] if an["name"] == "atacar_abajo")
    ox, oy = cam["directions"][0]["sprites"][0]["originPoint"]["x"], cam["directions"][0]["sprites"][0]["originPoint"]["y"]
    carpeta = os.path.join(GEN, "zombies", t, "atacar_arriba"); os.makedirs(carpeta, exist_ok=True)
    nombres = []
    for k, (src, up) in enumerate(zip(ORIG, SUBE)):
        sp = cam["directions"][0]["sprites"][src]
        f = os.path.normpath(os.path.join(RAIZ, RES[sp["image"]]["file"]))
        im = Image.open(f).convert("RGBA")
        extra = 14
        lienzo = Image.new("RGBA", (im.width, im.height + extra), (0, 0, 0, 0))
        lienzo.paste(im, (0, extra - up), im)
        nom = "atacar_arriba_%02d.png" % k
        lienzo.save(os.path.join(carpeta, nom))
        clave = "zombies/%s/atacar_arriba/%s" % (t, nom)
        add_res(clave, "../../generado/sprites/zombies/%s/atacar_arriba/%s" % (t, nom))
        nombres.append(clave)
    nueva = animacion("atacar_arriba", nombres, 1 / atq["directions"][0]["timeBetweenFrames"], False, (ox, oy + 14))
    o["animations"].append(nueva)
print("atacar_arriba: OK")

# =============================================================== 3. efecto de golpe al reves
ataque_g = next(e for e in J["events"] if es_grupo(e, "Combate: pegar"))
n_ang = 0
for e in recorrer(ataque_g["events"]):
    if e.get("fdiz19ang"):
        continue
    for x in e.get("actions", []):
        if x["type"]["value"] == "SetAngle" and x["parameters"][0] == "GolpeFx":
            x["parameters"][2] = str((int(float(x["parameters"][2])) + 180) % 360)
            e["fdiz19ang"] = True; n_ang += 1
print("angulos del efecto de golpe invertidos:", n_ang)

# =============================================================== 4. zombis que no desaparecian
zg = next(e for e in J["events"] if es_grupo(e, "Zombies: IA, ataque y muerte"))
quitar_tag(zg["events"], "fdiz19")
for onombre in TIPOS:
    o = obj(J, onombre)
    if not any(v["name"] == "MuerteIni" for v in o["variables"]):
        o["variables"].append(var("MuerteIni", 0))
for e in zg["events"]:
    if e.get("actions") and any(x["type"]["value"] == "SetAnimationName" and x["parameters"][1] == '"golpe_morir"' for x in e["actions"]):
        if not any(x["type"]["value"] == "PlayAnimation" for x in e["actions"]):
            e["actions"].append(a("PlayAnimation", "Zombies"))
zg["events"].append(marcado(ev([c("VarObjetTxt", "Zombies", "Estado", "=", '"muerto"'), c("VarObjet", "Zombies", "MuerteIni", "=", "0")],
                              [a("ModVarObjet", "Zombies", "MuerteIni", "=", "1"), a("ResetObjectTimer", "Zombies", '"muerte"'),
                               a("PlayAnimation", "Zombies")])))
zg["events"].append(marcado(ev([c("VarObjetTxt", "Zombies", "Estado", "=", '"muerto"'), c("VarObjet", "Zombies", "MuerteIni", "=", "1"),
                               c("CompareObjectTimer", "Zombies", '"muerte"', ">=", "1.2")],
                              [a("Delete", "Zombies", "")])))
print("zombis muertos: reanudan animacion y se borran a 1.2 s")

# ---- zombis "flotando": la pausa de la fase 18 usaba Pathfinding::Speed(), que vale 0 cuando el zombi se mueve por
# fuerzas (AddForceVersPos). Ahora se mide el movimiento real (variable Mov: promedio movil de lo que se desplaza por cuadro).
for onombre in TIPOS:
    o = obj(J, onombre)
    for vn in ("Mov", "PX", "PY"):
        if not any(v["name"] == vn for v in o["variables"]):
            o["variables"].append(var(vn, 0))
n_mov = 0
for e in recorrer(zg["events"]):
    if not e.get("fdiz18"):
        continue
    for cc in e.get("conditions", []):
        if cc["type"]["value"] == "BuiltinCommonInstructions::CompareNumbers" and cc["parameters"][0] == "Zombies.Pathfinding::Speed()":
            cc["parameters"][0] = "Zombies.Variable(Mov)"
            cc["parameters"][2] = "0.3" if cc["parameters"][1] == ">" else "0.3"
            n_mov += 1
zg["events"].insert(0, marcado(ev([], [a("ModVarObjet", "Zombies", "Mov", "=", "Zombies.Variable(Mov) * 0.85 + (abs(Zombies.X() - Zombies.Variable(PX)) + abs(Zombies.Y() - Zombies.Variable(PY))) * 0.15"),
                                       a("ModVarObjet", "Zombies", "PX", "=", "Zombies.X()"), a("ModVarObjet", "Zombies", "PY", "=", "Zombies.Y()")])))
print("zombis: pausa por movimiento real en", n_mov, "condicion(es)")

# =============================================================== 5. Tony en modo Gym
S = obj(J, "Sup")
def alto_cuerpo(f):
    """alto del cuerpo (pelo a zapatos, pixeles oscuros) sin contar las llamas"""
    im = Image.open(f).convert("RGBA"); w, h = im.size; px = im.load()
    top = bot = None
    for y in range(h):
        for x in range(w):
            r, g, b, al = px[x, y]
            if al > 200 and r < 70 and g < 70 and b < 70:
                if top is None: top = y
                bot = y
    return (bot - top + 1) if top is not None else 1
def fuente(clave):
    f = RES[clave]["file"].replace("personajes_p19", "personajes")
    return os.path.normpath(os.path.join(RAIZ, f)), f
escalas = {}
for an in S["animations"]:
    if not an["name"].startswith("tonyfuerte_"):
        continue
    nombre = an["name"][len("tonyfuerte_"):]
    ref = next((x for x in S["animations"] if x["name"] == "tony_" + nombre), None)
    if ref is None or nombre not in ("quieto", "caminar_abajo", "caminar_arriba", "caminar_lado", "pegar_lado"):
        continue
    # cada animacion se escala para que el cuerpo mida lo mismo que el de Tony normal
    h_ref = max(alto_cuerpo(fuente(s["image"])[0]) for s in ref["directions"][0]["sprites"])
    h_fue = max(alto_cuerpo(fuente(s["image"])[0]) for s in an["directions"][0]["sprites"])
    esc = h_ref / h_fue
    escalas[nombre] = round(esc, 3)
    for sp in an["directions"][0]["sprites"]:
        rr = RES[sp["image"]]
        fsrc, src = fuente(sp["image"])
        dst = src.replace("/personajes/", "/personajes_p19/")
        fdst = os.path.normpath(os.path.join(RAIZ, dst))
        im = Image.open(fsrc).convert("RGBA")
        im2 = im.resize((round(im.width * esc), round(im.height * esc)), Image.LANCZOS)
        os.makedirs(os.path.dirname(fdst), exist_ok=True); im2.save(fdst)
        rr["file"] = dst
        sp["originPoint"]["x"], sp["originPoint"]["y"] = round(42 * esc), round(98 * esc)
ESC = escalas
have = {an["name"] for an in S["animations"]}
def clonar(origen, destino):
    if destino in have: return
    an = copy.deepcopy(next(x for x in S["animations"] if x["name"] == origen)); an["name"] = destino
    S["animations"].append(an); have.add(destino)
clonar("tonyfuerte_pegar_lado", "tonyfuerte_pegar_abajo")
clonar("tonyfuerte_pegar_lado", "tonyfuerte_pegar_arriba")
for k in ("caer_levantarse", "festejo", "habilidad", "especial"):
    clonar("tony_" + k, "tonyfuerte_" + k)
print("Tony Gym escalado por animacion:", ESC)

# =============================================================== 6. Rutas de Cesar con A*
MARCA = "/*FDIZ19-RUTA*/"
JS_RUTA = MARCA + r"""
(function () {
  const NAV = gdjs.fdizNav; if (!NAV || !NAV.grid) return;
  const sc = runtimeScene, vars = sc.getVariables();
  const S = (gdjs.fdizRuta = gdjs.fdizRuta || { act: false, t0: 0, last: -9 });
  const now = sc.getTimeManager().getTimeFromStart() / 1000;
  const go = vars.get("RutaGo");
  if (go.getAsNumber() === 1) { go.setNumber(0); S.act = true; S.t0 = now; S.last = -9; }
  if (!S.act) return;
  const limpiar = () => { const l = sc.getObjects("Ruta") || []; for (let i = l.length - 1; i >= 0; i--) l[i].deleteFromScene(); };
  let ces = null;
  for (const o of (sc.getObjects("Sup") || [])) {
    const v = o.getVariables();
    if (v.get("Personaje").getAsString() === "cesar" && v.get("Estado").getAsString() === "normal") { ces = o; break; }
  }
  if (!ces || now - S.t0 >= 14) { S.act = false; limpiar(); return; }
  if (now - S.last < 0.6) return;
  S.last = now;
  const ox = vars.get("ObjX").getAsNumber(), oy = vars.get("ObjY").getAsNumber();
  const r = NAV.path(ces.getX(), ces.getY(), ox, oy, 60000);
  limpiar();
  if (!r || !r.found || r.pts.length < 2) return;
  const pts = r.pts, PASO = 46, MAXD = 2600, MAXN = 56;
  let acum = 70, total = 0, n = 0;     // empieza 70 px delante de Cesar
  for (let i = 0; i < pts.length - 1 && n < MAXN && total < MAXD; i++) {
    const ax = pts[i][0], ay = pts[i][1], bx = pts[i + 1][0], by = pts[i + 1][1];
    const L = Math.hypot(bx - ax, by - ay); if (L < 1e-3) continue;
    let d = acum;
    while (d <= L && n < MAXN) {
      const x = ax + (bx - ax) * d / L, y = ay + (by - ay) * d / L;
      const borde = sc.createObject("Ruta"); borde.setLayer("Niebla"); borde.setPosition(x, y); borde.setScale(0.56);
      borde.setColor("15;12;30"); borde.setZOrder(90000); borde.resetTimer("vida");
      const dot = sc.createObject("Ruta"); dot.setLayer("Niebla"); dot.setPosition(x, y); dot.setScale(0.4);
      dot.setColor("255;240;70"); dot.setZOrder(90001); dot.resetTimer("vida");
      n++; d += PASO;
    }
    acum = d - L; total += L;
  }
})();
"""
pas = next(e for e in J["events"] if es_grupo(e, "Pasivas: Ojo de oferta, Rutas y AirDrop"))
pas["events"] = [e for e in pas["events"] if not (e.get("type", "").endswith("JsCode") and MARCA in e.get("inlineCode", ""))]
idx_disp = None
for i, e in enumerate(pas["events"]):
    acts = e.get("actions", [])
    if any(x["type"]["value"] == "Delete" and x["parameters"][0] == "Ruta" for x in acts) and any(
            cc["type"]["value"] == "CompareObjectTimer" and cc["parameters"][1] == '"rutas"' for cc in e["conditions"]):
        # fuera los 11 puntos en linea recta y se avisa a la rutina JS
        e["events"] = [s for s in e.get("events", []) if not any(x["type"]["value"] == "Create" and x["parameters"][1] == "Ruta" for x in s.get("actions", []))]
        if not any(x["type"]["value"] == "ModVarScene" and x["parameters"][0] == "RutaGo" for x in acts):
            acts.append(a("ModVarScene", "RutaGo", "=", "1"))
        idx_disp = i
assert idx_disp is not None, "no se encontro el disparador de Rutas"
pas["events"].insert(idx_disp + 1, {"type": "BuiltinCommonInstructions::JsCode", "inlineCode": JS_RUTA, "parameterObjects": "",
                                    "useStrict": True, "eventsSheetExpanded": False})
for e in pas["events"]:
    for x in e.get("actions", []):
        if x["type"]["value"] == "Opacity" and x["parameters"][0] == "Ruta":
            # parpadeo: de casi invisible a 178 (70 % del maximo anterior de 255)
            x["parameters"][2] = "110 + 68 * sin(TimeFromStart() * 5)"
print("Rutas de Cesar con A*: OK")

# =============================================================== 7. pantalla de derrota con reiniciar + derrota inmediata
def txt_obj(nombre, tam):
    base = copy.deepcopy(obj(R, "TxtPie")); base["name"] = nombre; base["characterSize"] = tam
    base["content"]["characterSize"] = tam; base["content"]["isOutlineEnabled"] = True; base["content"]["outlineThickness"] = 5
    base["color"] = {"b": 200, "g": 240, "r": 255}; base["content"]["color"] = "255;240;200"
    return base
def spr_obj(nombre, clave):
    return {"adaptCollisionMaskAutomatically": False, "assetStoreId": "", "name": nombre, "type": "Sprite", "updateIfNotVisible": False,
            "variables": [], "effects": [], "behaviors": [],
            "animations": [animacion("b", [clave], 1, False, (0, 0))]}
add_res("p19_BtnRei", BASE_UI + "ui_boton_normal_dificultad_p19.png")
add_res("p19_BtnMenu", BASE_UI + "ui_boton_facil_p19.png")
BX, BW, BH, Y1, Y2 = 150, 380, 132, 640, 790
for nombre, mk in (("BtnRei", lambda: spr_obj("BtnRei", "p19_BtnRei")), ("BtnMenuR", lambda: spr_obj("BtnMenuR", "p19_BtnMenu")),
                   ("TxtBtnRei", lambda: txt_obj("TxtBtnRei", 40)), ("TxtBtnMenuR", lambda: txt_obj("TxtBtnMenuR", 40))):
    if not obj(R, nombre):
        R["objects"].append(mk())
def inst(nombre, x, y, w=None, h=None, z=50):
    return {"angle": 0, "customSize": w is not None, "height": h or 0, "layer": "", "name": nombre,
            "persistentUuid": __import__("uuid").uuid4().hex, "width": w or 0, "x": x, "y": y, "zOrder": z,
            "numberProperties": [], "stringProperties": [], "initialVariables": []}
R["instances"] = [i for i in R["instances"] if i["name"] not in ("BtnRei", "BtnMenuR", "TxtBtnRei", "TxtBtnMenuR")]
R["instances"] += [inst("BtnRei", BX, Y1, BW, BH), inst("BtnMenuR", BX, Y2, BW, BH),
                   inst("TxtBtnRei", BX + BW // 2, Y1 + BH // 2, z=60), inst("TxtBtnMenuR", BX + BW // 2, Y2 + BH // 2, z=60)]

quitar_tag(R["events"], "fdiz19")
# el evento "cualquier tecla: volver al titulo" queda solo para la victoria
for e in R["events"]:
    if any(x["type"]["value"] == "Scene" and x["parameters"][1] == '"Titulo"' for x in e.get("actions", [])) and any(
            cc["type"]["value"] == "CompareTimer" for cc in e.get("conditions", [])):
        if not any(cc["type"]["value"] == "VarGlobalTxt" for cc in e["conditions"]):
            e["conditions"].append(c("VarGlobalTxt", "Resultado", "=", '"victoria"'))
def dentro(x0, y0, x1, y1):
    return [cmp("MouseX()", ">=", str(x0)), cmp("MouseX()", "<=", str(x1)), cmp("MouseY()", ">=", str(y0)), cmp("MouseY()", "<=", str(y1))]
DER = c("VarGlobalTxt", "Resultado", "!=", '"victoria"')
T1 = c("CompareTimer", "", '"t"', ">=", "1")
def pads(botones):
    out = []
    for b in botones:
        for pj in ("1", "2", "3", "4"):
            out.append({"type": {"value": "Gamepads::C_Button_released"}, "parameters": ["", pj, '"%s"' % b, ""]})
    return out
nuevos = [
    ev([c("VarGlobalTxt", "Resultado", "=", '"victoria"')],
       [a("Cache", "BtnRei"), a("Cache", "BtnMenuR"), a("Cache", "TxtBtnRei"), a("Cache", "TxtBtnMenuR")]),
    ev([DER], [a("Montre", "BtnRei", ""), a("Montre", "BtnMenuR", ""), a("Montre", "TxtBtnRei", ""), a("Montre", "TxtBtnMenuR", ""),
               a("TextObject::String", "TxtBtnRei", "=", '"REINICIAR"'), a("TextObject::String", "TxtBtnMenuR", "=", '"MENÚ"'),
               a("TextObject::String", "TxtPie", "=", '"R, Enter, Espacio o clic: reiniciar con los mismos personajes   ·   Esc: menú"'),
               a("MettreX", "TxtBtnRei", "=", "%d - TxtBtnRei.Width() / 2" % (BX + BW // 2)),
               a("MettreY", "TxtBtnRei", "=", "%d - TxtBtnRei.Height() / 2" % (Y1 + BH // 2)),
               a("MettreX", "TxtBtnMenuR", "=", "%d - TxtBtnMenuR.Width() / 2" % (BX + BW // 2)),
               a("MettreY", "TxtBtnMenuR", "=", "%d - TxtBtnMenuR.Height() / 2" % (Y2 + BH // 2))]),
    # clic en MENU primero (para que el clic de reiniciar no lo pise)
    ev([DER, T1, c("MouseButtonReleased", "", "Left")] + dentro(BX, Y2, BX + BW, Y2 + BH), [a("Scene", "", '"Titulo"', "")]),
    ev([DER, T1, {"type": {"value": "BuiltinCommonInstructions::Or"}, "parameters": [],
                  "subInstructions": [c("KeyReleased", "", "Escape"), c("KeyReleased", "", "m")]}], [a("Scene", "", '"Titulo"', "")]),
    ev([DER, T1, c("MouseButtonReleased", "", "Left")] + dentro(BX, Y1, BX + BW, Y1 + BH), [a("Scene", "", '"Juego"', "")]),
    ev([DER, T1, {"type": {"value": "BuiltinCommonInstructions::Or"}, "parameters": [],
                  "subInstructions": [c("KeyReleased", "", "r"), c("KeyReleased", "", "Return"), c("KeyReleased", "", "Space")] + pads(["A", "START"])}],
       [a("Scene", "", '"Juego"', "")]),
]
for e in nuevos: marcado(e)
R["events"] += nuevos

# derrota inmediata: un solo humano (con 3 bots) que cae
g46 = next(e for e in J["events"] if es_grupo(e, "Cámara compartida"))
quitar_tag(g46["events"], "fdiz19")
g46["events"] += [marcado(e) for e in (
    ev([], [a("ModVarScene", "HumTot", "=", "0")]),
    ev([c("VarObjet", "Sup", "Control", ">=", "0")], [a("ModVarScene", "HumTot", "=", "PickedInstancesCount(Sup)")]),
    ev([c("VarSceneTxt", "Estado", "=", '"juego"'), c("VarScene", "HumTot", "=", "1"), c("VarScene", "Humanos", "=", "0")],
       [a("ModVarSceneTxt", "Estado", "=", '"derrota"'), a("ResetTimer", "", '"fin"')]),
    ev([c("VarSceneTxt", "Estado", "=", '"derrota"'), c("VarScene", "HumTot", "=", "1"), c("CompareTimer", "", '"fin"', ">=", "0.1")],
       [a("ModVarGlobalTxt", "Resultado", "=", '"derrota"'), a("Scene", "", '"Resultados"', "")]))]
print("derrota con reiniciar e inmediata: OK")

json.dump(p, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("OK fase 19")
