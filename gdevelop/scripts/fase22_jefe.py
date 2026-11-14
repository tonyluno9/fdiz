"""Fase 22 · Modo Jefe de zombies funcional (idempotente). Uso: python3 fase22_jefe.py"""
import json, copy, os, shutil, sys, datetime
sys.path.insert(0, os.path.dirname(__file__))
from gd_util import res_imagen, animacion, objeto_sprite, instancia, c, a

AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
MARCA_J = "FDIZ-FASE22-JEFE"
MARCA_B = "FDIZ-FASE22-BOTS"

bak = os.path.join(AQUI, "..", "respaldos", "antes_de_fase22_20261113.json")
if not os.path.exists(bak):
    shutil.copy(PRY, bak)
d = json.load(open(PRY))
esc = next(l for l in d["layouts"] if l["name"] == "Juego")
ev = esc["events"]

def grupo(nombre):
    return next(e for e in ev if e.get("name") == nombre)

def js_evento(codigo):
    return {"type": "BuiltinCommonInstructions::JsCode", "inlineCode": codigo, "parameterObjects": "",
            "useStrict": True, "eventsSheetExpanded": False}

def estandar(conds, acts, sub=()):
    return {"type": "BuiltinCommonInstructions::Standard", "conditions": conds, "actions": acts, "events": list(sub)}

def comentario(txt):
    return {"type": "BuiltinCommonInstructions::Comment", "color": {"b": 109, "g": 230, "r": 255, "textB": 0, "textG": 0, "textR": 0}, "comment": txt}

def agrega_cond(e, cond):
    if cond not in e["conditions"]:
        e["conditions"].append(cond)

cond_no_jefe = c("VarGlobalTxt", "Modo", "!=", '"jefe"')

# ---------- 1. recursos ----------
R = d["resources"]["resources"]
nombres = {r["name"] for r in R}
nuevos = [("jefe_carta", "assets/interfaz/hud_carta_jefe.png")] + [("jefe_icono_c%d" % i, "assets/interfaz/jefe_icono_c%d.png" % i) for i in range(1, 9)]
for n, f in nuevos:
    if n not in nombres:
        R.append(res_imagen(n, f))

# ---------- 2. objetos ----------
O = {o["name"] for o in esc["objects"]}
if "JfCarta" not in O:
    esc["objects"].append(objeto_sprite("JfCarta", [animacion("c", ["jefe_carta"], 1, False, (0, 0))]))
if "JfIcono" not in O:
    esc["objects"].append(objeto_sprite("JfIcono", [animacion("c%d" % i, ["jefe_icono_c%d" % i], 1, False, (0, 0)) for i in range(1, 9)]))
if "JfTexto" not in O:
    t = copy.deepcopy(next(o for o in esc["objects"] if o["name"] == "TxtHudDinero"))
    t["name"] = "JfTexto"; t["variables"] = []
    t["bold"] = True; t["characterSize"] = 22; t["color"] = {"b": 255, "g": 255, "r": 255}
    t["content"].update({"characterSize": 22, "color": "255;255;255", "outlineThickness": 3})
    esc["objects"].append(t)
for n in ("JfDibB", "JfDibO", "JfDibM"):
    if n not in O:
        esc["objects"].append({"assetStoreId": "", "name": n, "type": "PrimitiveDrawing::Drawer", "variables": [], "effects": [], "behaviors": [],
                               "fillOpacity": 255, "outlineSize": 1, "outlineOpacity": 255, "fillColor": {"b": 0, "g": 0, "r": 0}, "outlineColor": {"b": 0, "g": 0, "r": 0},
                               "absoluteCoordinates": True, "clearBetweenFrames": False, "antialiasing": "none"})
for o in esc["objects"]:
    if o["name"] in ("JfDibB", "JfDibO", "JfDibM"):
        o["absoluteCoordinates"] = True; o["clearBetweenFrames"] = False
I = {i["name"] for i in esc["instances"]}
for n, capa in (("JfDibB", "HUD"), ("JfDibO", "HUD"), ("JfDibM", "Techo")):
    if n not in I:
        esc["instances"].append(instancia(n, 0, 0, capa, 0))

# ---------- 3. JS del Jefe (grupo "Modo Jefe de zombies") ----------
g31 = grupo("Modo Jefe de zombies")
js_jefe = open(os.path.join(AQUI, "jefe_modo.js"), encoding="utf-8").read()
cuerpo = "// " + MARCA_J + "\n" + js_jefe
ya = g31["events"] and g31["events"][0].get("comment", "").startswith(MARCA_J)
e46_11 = next(e for e in grupo("Cámara compartida")["events"] if e["type"].endswith("Standard") and any(x["parameters"][:1] == ['"fin"'] or x["parameters"][1:2] == ['"fin"'] for x in e["conditions"] if x["type"]["value"] == "CompareTimer"))
fin_conds = [c("VarScene", "Jefe", "=", "1")] + [x for x in copy.deepcopy(e46_11["conditions"]) if x["type"]["value"] != "VarScene"]
fin_acts = copy.deepcopy(e46_11["actions"])
if not ya:
    g31["events"] = [
        comentario(MARCA_J + " · Modo Jefe (fase 22). El Jefe juega con teclado y ratón; los 4 sobrevivientes son bots. Interfaz, cámara libre, cartas, invocación con clic y zona prohibida (círculo rojo) están en el código JavaScript de abajo (scripts/jefe_modo.js)."),
        js_evento(cuerpo),
        estandar(fin_conds, fin_acts),
    ]
else:
    g31["events"][1]["inlineCode"] = cuerpo

# ---------- 4. JS de habilidades de bots (antes del grupo 27) ----------
js_b = open(os.path.join(AQUI, "bots_habilidades.js"), encoding="utf-8").read()
for e in ev:
    if e["type"].endswith("JsCode") and MARCA_B in e.get("inlineCode", ""):
        e["inlineCode"] = "// " + MARCA_B + "\n" + js_b
if not any(e["type"].endswith("JsCode") and MARCA_B in e.get("inlineCode", "") for e in ev):
    pos = next(i for i, e in enumerate(ev) if e.get("name") == "Habilidades, especiales y pasivas")
    ev.insert(pos, js_evento("// " + MARCA_B + "\n" + js_b))

# ---------- 5. Inicio: 4 bots, sin cinemática ni oscuridad inicial ----------
g1 = grupo("Configuración y dificultad")
g1["events"] = [e for e in g1["events"] if not (any(x["type"]["value"] == "VarGlobalTxt" and x["parameters"][:3] == ["Modo", "=", '"jefe"'] for x in e.get("conditions", []))
                                               and any(x["type"]["value"] == "Delete" for x in e.get("actions", [])))]
if not any(e.get("comment", "").startswith(MARCA_J) for e in g1["events"]):
    g1["events"].append(comentario(MARCA_J + " · Modo Jefe: los 4 sobrevivientes son bots (Control -1)."))
    g1["events"].append(estandar([c("DepartScene", ""), c("VarGlobalTxt", "Modo", "=", '"jefe"')],
                                 [a("ModVarObjet", "Sup", "Control", "=", "-1")]))
for nombre in ("Cinemática de inicio", "Oscuridad inicial y botón omitir"):
    g = grupo(nombre)
    for e in g["events"]:
        if e["type"].endswith("Standard") and any(x["type"]["value"] == "VarGlobal" and x["parameters"][:3] == ["VioIntro", "=", "0"] for x in e["conditions"]):
            agrega_cond(e, cond_no_jefe)

# ---------- 6. Niebla, infestación, cámara, zona roja ----------
for e in grupo("Niebla por zonas")["events"]:
    if e["type"].endswith("Standard") and any(x["type"]["value"] == "DepartScene" for x in e["conditions"]) and any(x["type"]["value"] == "ShowLayer" for x in e["actions"]):
        agrega_cond(e, cond_no_jefe)
for e in grupo("Infestación")["events"]:
    if e["type"].endswith("Standard") and any(x["type"]["value"] == "CompareTimer" and x["parameters"][1] == '"spawn"' for x in e["conditions"]):
        agrega_cond(e, c("VarScene", "Jefe", "=", "0"))
cam = grupo("Cámara compartida")
for e in cam["events"]:
    if not e["type"].endswith("Standard"):
        continue
    acts = json.dumps(e["actions"])
    if any(x["type"]["value"] == "MettreXY" and x["parameters"][0] == "Sup" for x in e["actions"]):
        agrega_cond(e, c("VarScene", "Jefe", "=", "0"))
    # el evento CamN>0 calcula CamX/CamY (los usa la guía de los bots): solo se bloquea mover la cámara
    if any(x["type"]["value"] == "VarScene" and x["parameters"][:1] == ["CamN"] for x in e["conditions"]):
        e["conditions"] = [x for x in e["conditions"] if not (x["type"]["value"] == "VarScene" and x["parameters"][:1] == ["Jefe"])]
        for sub in e.get("events", []):
            agrega_cond(sub, c("VarScene", "Jefe", "=", "0"))
zr = grupo("Zona roja del minimapa")
zr["events"] = [e for e in zr["events"] if not any(x["type"]["value"] == "Montre" and x["parameters"][0] == "ZonaRoja" for x in e.get("actions", []))]
zr["events"].append(estandar([], [a("Cache", "ZonaRoja", "")]))

# ---------- 7. HUD de dinero muestra el oro del Jefe ----------
for e in grupo("Interfaz: HUD con paneles")["events"]:
    for x in e.get("actions", []):
        if x["type"]["value"] == "TextObject::String" and x["parameters"][0] == "TxtHudDinero":
            x["parameters"][2] = "ToString(floor(Variable(Dinero) * (1 - Variable(Jefe)) + Variable(OroJefe) * Variable(Jefe)))"

# ---------- 8. Resultados ----------
res = next(l for l in d["layouts"] if l["name"] == "Resultados")
if not any(e.get("comment", "").startswith(MARCA_J) for e in res["events"]):
    nuevo = [comentario(MARCA_J + " · textos del modo Jefe."),
             estandar([c("DepartScene", ""), c("VarGlobalTxt", "Modo", "=", '"jefe"'), c("VarGlobalTxt", "Resultado", "=", '"victoria"')],
                      [a("TextObject::String", "TxtRes", "=", '"¡ESCAPARON! EL JEFE PERDIÓ"')]),
             estandar([c("DepartScene", ""), c("VarGlobalTxt", "Modo", "=", '"jefe"'), c("VarGlobalTxt", "Resultado", "!=", '"victoria"')],
                      [a("TextObject::String", "TxtRes", "=", '"¡GANÓ EL JEFE! LOS ATRAPÓ A TODOS"')])]
    pos = 0
    for i, e in enumerate(res["events"]):
        if any(x["type"]["value"] == "VarGlobalTxt" and x["parameters"][2:3] == ['"victoria"'] for x in e.get("conditions", [])) and any(x["parameters"][0] == "TxtRes" for x in e.get("actions", []) if x["type"]["value"] == "TextObject::String"):
            pos = i + 1
    res["events"][pos:pos] = nuevo

# ---------- 9. Música: un solo canal (fase 23) ----------
# PlayMusic suma pistas; PlayMusicCanal reemplaza la que suene en ese canal.
def canal(evs):
    for e in evs:
        for x in e.get("actions", []):
            if x["type"]["value"] == "PlayMusic":
                p = x["parameters"]
                x["type"]["value"] = "PlayMusicCanal"
                x["parameters"] = [p[0], p[1], "1", p[2], p[3], p[4]]
        canal(e.get("events", []))
for l in d["layouts"]:
    canal(l["events"])

json.dump(d, open(PRY, "w"), ensure_ascii=False, indent=2)
print("OK fase 22")
