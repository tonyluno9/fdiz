"""Fase 25 · Online por internet (PeerJS). Idempotente. Uso: python3 fase25_online.py"""
import json, copy, os, shutil, sys
sys.path.insert(0, os.path.dirname(__file__))
from gd_util import c, a, instancia, capa

AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
bak = os.path.join(AQUI, "..", "respaldos", "antes_de_fase25_20261113.json")
if not os.path.exists(bak):
    shutil.copy(PRY, bak)
d = json.load(open(PRY))
J = next(l for l in d["layouts"] if l["name"] == "Juego")
M = next(l for l in d["layouts"] if l["name"] == "Menu")
TI = next(l for l in d["layouts"] if l["name"] == "Titulo")
RE = next(l for l in d["layouts"] if l["name"] == "Resultados")
ev = J["events"]
MK = "FDIZ-FASE25"

def js(code, marca):
    return {"type": "BuiltinCommonInstructions::JsCode", "inlineCode": "/*" + marca + "*/\n" + code, "parameterObjects": "", "useStrict": True, "eventsSheetExpanded": False}
def std(conds, acts, sub=()):
    return {"type": "BuiltinCommonInstructions::Standard", "conditions": conds, "actions": acts, "events": list(sub)}
def esmarca(e, marca):
    return e["type"].endswith("JsCode") and e["inlineCode"].startswith("/*" + marca)
def quita(lst, marca):
    lst[:] = [e for e in lst if not esmarca(e, marca)]

# ---- variables globales / Sup
if not any(v["name"] == "NetRol" for v in d["variables"]):
    d["variables"].append({"name": "NetRol", "type": "number", "value": 0})
sup = next(o for o in J["objects"] if o["name"] == "Sup")
for n in ("NetSp", "NetDr"):
    if not any(v["name"] == n for v in sup["variables"]):
        sup["variables"].append({"name": n, "type": "number", "value": 0})

# ---- configuración de sincronización
TRACK = ["Sup", "ZNormal", "ZCorredor", "ZGriton", "ZGordo", "ZConserje", "ZCurado", "Golpe", "Salpicadura", "ArmaPiso", "Objetivo", "Bidon", "Bolsa", "Comida",
         "Aparato", "EfectoPj", "Profe", "Efecto", "Canepa", "LanzPiso", "Proyectil", "Contenedor", "Moneda", "Ruta", "Puerta", "Niebla", "GolpeFx", "Flecha",
         "TxtDanio", "TxtPrecio", "TxtMordido"]
TXT = {"TxtDanio", "TxtPrecio", "TxtMordido"}
objs = []
for n in TRACK:
    o = next(x for x in J["objects"] if x["name"] == n)
    objs.append({"n": n, "t": 1 if n in TXT else 0, "v": [[v["name"], "s" if v["type"] == "string" else "n"] for v in o["variables"] if v["type"] in ("string", "number")]})
EXC = ("Cam", "Humanos", "HumTot", "Pausa", "Jefe", "AyudaTec", "AyudaPad", "InfVista", "Pres", "VerDebug", "Bloq", "OscIni")
sv = [v["name"] for v in J["variables"] if v["type"] in ("string", "number") and not v["name"].startswith(EXC)]
cfg = {"objs": objs, "sv": sv}

# ---- Titulo: peerjs + núcleo
peer = open(os.path.join(AQUI, "peerjs.min.js"), encoding="utf8").read()
core = open(os.path.join(AQUI, "net_core.js"), encoding="utf8").read()
codigo = ("(function(){\nif(!window.__fdizPeer){window.__fdizPeer=1;\n(function(module,exports,define){\n" + peer + "\n}).call(window,undefined,undefined,undefined);}\n"
          "gdjs.fdizNetCfg=" + json.dumps(cfg, ensure_ascii=False) + ";\n" + core + "\n})();")
quita(TI["events"], MK + "-NUCLEO")
TI["events"].insert(0, js(codigo, MK + "-NUCLEO"))

# ---- Juego: bloquear lógica en clientes
LIBRES = {"HUD", "Textos centrados", "Música y sonido de fondo", "Inventario en el panel", "Zona roja del minimapa", "Cámara compartida", "Temblor de cámara", "Interfaz: HUD con paneles"}
NOCLI = c("VarGlobal", "NetRol", "!=", "2")
SOLOOFF = c("VarGlobal", "NetRol", "=", "0")
def compuerta(lst, cond):
    for i, e in enumerate(lst):
        t = e["type"]
        if t.endswith("Comment"):
            continue
        if t.endswith("Standard"):
            if cond not in e["conditions"]:
                e["conditions"].insert(0, cond)
        else:
            lst[i] = std([cond], [], [e])
# deshacer huellas previas de mis eventos nuevos antes de volver a compuertar
for lst in [ev]:
    for marca in ("-BEGIN", "-INPUT", "-END"):
        quita(lst, MK + marca)
for i, e in enumerate(ev):
    if e["type"].endswith("Group"):
        n = e.get("name", "")
        if n in LIBRES:
            continue
        compuerta(e["events"], SOLOOFF if n == "Menú de pausa" else NOCLI)
    elif e["type"].endswith("JsCode"):
        ev[i] = std([NOCLI], [], [e])
    elif e["type"].endswith("Standard") and NOCLI not in e["conditions"]:
        e["conditions"].insert(0, NOCLI)
def grupo(nombre):
    return next(e for e in ev if e.get("name") == nombre)
# cámara: el clamp de Sup lo hace el host
for e in grupo("Cámara compartida")["events"]:
    if e["type"].endswith("Standard") and any(x["type"]["value"] == "MettreXY" and x["parameters"][0] == "Sup" for x in e["actions"]):
        if NOCLI not in e["conditions"]:
            e["conditions"].insert(0, NOCLI)
# apagón: los clientes oscurecen su pantalla; el Jefe (host) no
amb = grupo("Ambiente: noche y apagón")
for e in amb["events"]:
    if e["type"].endswith("Standard") and any(x["type"]["value"] == "SetLayerAmbientLightColor" for x in e["actions"]):
        e["conditions"] = [x for x in e["conditions"] if x != NOCLI]
        cs = e["conditions"]
        if any(x["type"]["value"] == "VarScene" and x["parameters"] == ["Apagon", "=", "1"] for x in cs):
            if not any(x["parameters"][:1] == ["Jefe"] for x in cs if x["type"]["value"] == "VarScene"):
                cs.append(c("VarScene", "Jefe", "=", "0"))
if not any(e.get("comment", "").startswith(MK + "-APAGON") for e in amb["events"]):
    amb["events"].append({"type": "BuiltinCommonInstructions::Comment", "color": {"b": 109, "g": 230, "r": 255, "textB": 0, "textG": 0, "textR": 0}, "comment": MK + "-APAGON · el Jefe no sufre su propio apagón."})
    amb["events"].append(std([c("VarScene", "Apagon", "=", "1"), c("VarScene", "Jefe", "=", "1")], [a("SetLayerAmbientLightColor", "", '"Luz"', '"120;125;165"')]))
# sin cinemática ni oscuridad inicial en línea
for nombre in ("Cinemática de inicio", "Oscuridad inicial y botón omitir"):
    for e in grupo(nombre)["events"]:
        if e["type"].endswith("Standard") and any(x["type"]["value"] == "VarGlobal" and x["parameters"][:3] == ["VioIntro", "=", "0"] for x in e["conditions"]):
            if SOLOOFF not in e["conditions"]:
                e["conditions"].append(SOLOOFF)

# duplicados de eventos que leen teclado directo (correr y abrir puerta) para jugadores remotos (Control -3)
def dup(lst):
    out = []
    for e in lst:
        out.append(e)
        if not e["type"].endswith("Standard"):
            if e.get("events"):
                e["events"] = dup(e["events"])
            continue
        cs = e["conditions"]
        ctrl = [x for x in cs if x["type"]["value"] == "VarObjet" and x["parameters"][:4] == ["Sup", "Control", "=", "0"]]
        tecla = [x for x in cs if x["type"]["value"] == "KeyPressed" and x["parameters"][1] in ("LShift", "r")]
        if ctrl and tecla:
            n = copy.deepcopy(e)
            n["conditions"] = [x for x in n["conditions"] if x not in ctrl and x not in tecla]
            n["conditions"].append(c("VarObjet", "Sup", "Control", "=", "-3"))
            n["conditions"].append(c("VarObjet", "Sup", "NetSp" if tecla[0]["parameters"][1] == "LShift" else "NetDr", "=", "1"))
            if not any(q.get("actions") == n["actions"] and q.get("conditions") == n["conditions"] for q in lst):
                out.append(n)
        e["events"] = dup(e.get("events", []))
    return out
for gname in ("Movimiento y animación", "Mapa: choques y puertas"):
    g = grupo(gname); g["events"] = dup(g["events"])

# insertar begin / input / end
ix = next(i for i, e in enumerate(ev) if e.get("name") == "Entrada (teclado y controles)")
ev.insert(ix + 1, js("if (gdjs.fdizNet) gdjs.fdizNet.inputs(runtimeScene);", MK + "-INPUT"))
ev.insert(0, js("if (gdjs.fdizNet) gdjs.fdizNet.begin(runtimeScene);", MK + "-BEGIN"))
ev.append(js("if (gdjs.fdizNet) gdjs.fdizNet.end(runtimeScene);", MK + "-END"))

# ---- Resultados
quita(RE["events"], MK + "-RES")
RE["events"].insert(0, js("if (gdjs.fdizNet) gdjs.fdizNet.sceneEnter(runtimeScene, \"Resultados\");", MK + "-RES"))
def rscenes(lst):
    for e in lst:
        for x in e.get("actions", []):
            if x["type"]["value"] == "Scene" and x["parameters"][1] in ('"Juego"', '"Titulo"'):
                x["parameters"][1] = 'if(GlobalVariable(NetRol) > 0, "Online", %s)' % x["parameters"][1]
        rscenes(e.get("events", []))
rscenes(RE["events"])

# ---- escena Online
if not any(l["name"] == "Online" for l in d["layouts"]):
    on = copy.deepcopy(TI)
    on["name"] = on["mangledName"] = "Online"
    on["events"] = []; on["instances"] = []; on["objects"] = []; on["variables"] = []; on["objectsGroups"] = []
    on["objectsFolderStructure"] = {"folderName": "__ROOT", "children": []} if "objectsFolderStructure" in on else None
    if on["objectsFolderStructure"] is None: del on["objectsFolderStructure"]
    d["layouts"].append(on)
on = next(l for l in d["layouts"] if l["name"] == "Online")
names = {o["name"] for o in on["objects"]}
if "TxtOn" not in names:
    t = copy.deepcopy(next(o for o in J["objects"] if o["name"] == "JfTexto")); t["name"] = "TxtOn"; on["objects"].append(t)
for n in ("Fondo", "Velo"):
    if n not in names:
        on["objects"].append(copy.deepcopy(next(o for o in M["objects"] if o["name"] == n)))
if not on["instances"]:
    on["instances"] = [instancia("Fondo", 0, 0, "", 0, 1920, 1080), instancia("Velo", 0, 0, "", 1, 1920, 1080)]
on["events"] = [js("if (gdjs.fdizNet) gdjs.fdizNet.ui_tick(runtimeScene); else { runtimeScene.requestChange(3, \"Menu\"); }", MK + "-UI")]
on["events"].append(std([c("DepartScene", "")], [a("SetAnimationName", "Fondo", '"modo"')]))

# ---- Menú: opción 3 En línea
for e in M["events"]:
    for x in e.get("actions", []):
        if x["type"]["value"].endswith("String") and x["parameters"][0] == "TxtMenu" and "JEFE DE ZOMBIES" in x["parameters"][-1] and "EN LÍNEA" not in x["parameters"][-1]:
            x["parameters"][-1] = x["parameters"][-1].rstrip() + ' + NewLine() + "3  EN LÍNEA (internet)"'
            x["parameters"][-1] = x["parameters"][-1].replace("(1 a 3 contra el Jefe con ratón)", "(Jefe vs 4 bots; en línea, vs personas)")
if not any(e.get("comment", "").startswith(MK + "-MENU") for e in M["events"]):
    M["events"].append({"type": "BuiltinCommonInstructions::Comment", "color": {"b": 109, "g": 230, "r": 255, "textB": 0, "textG": 0, "textR": 0}, "comment": MK + "-MENU · opción 3: jugar en línea."})
    M["events"].append(std([c("VarSceneTxt", "Paso", "=", '"modo"'), c("KeyReleased", "", "Num3")], [a("Scene", "", '"Online"', "")]))
def limpia(o):
    if isinstance(o, dict):
        o.pop("_net", None)
        for v in o.values(): limpia(v)
    elif isinstance(o, list):
        for v in o: limpia(v)
limpia(d)
json.dump(d, open(PRY, "w"), ensure_ascii=False, indent=2)
print("OK fase 25")
