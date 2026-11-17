"""Fase 28 · UI "de lanzamiento" (sin textos de guía), Resultados/pantalla de muerte, Jefe (monedas y sin instrucciones),
fuera la tienda y el dinero del equipo, nuevo pasivo de Tony. Idempotente.
Orden: python3 fase25_online.py && python3 fase26_multijugador.py && python3 fase27_jefe_y_controles.py && python3 fase28_ui_jefe_tienda.py
"""
import json, copy, os, shutil, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gd_util import c, a, instancia, res_imagen

AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
NET = os.path.join(AQUI, "net_core.js")
JEFE_SRC = os.path.join(AQUI, "jefe_modo.js")
bak = os.path.join(AQUI, "..", "respaldos", "antes_de_fase28_20261117.json")
if not os.path.exists(bak):
    shutil.copy(PRY, bak)
d = json.load(open(PRY))
LAY = {l["name"]: l for l in d["layouts"]}
T_, M, J, R, O = LAY["Titulo"], LAY["Menu"], LAY["Juego"], LAY["Resultados"], LAY["Online"]
MK = "FDIZ-FASE28"
STD = "BuiltinCommonInstructions::Standard"

def std(conds, acts, sub=()):
    return {"type": STD, "conditions": conds, "actions": acts, "events": list(sub)}
def orc(*subs):
    return {"type": {"inverted": False, "value": "BuiltinCommonInstructions::Or"}, "parameters": [], "subInstructions": list(subs)}
def marca(clave):
    return {"type": "BuiltinCommonInstructions::Comment", "color": {"b": 109, "g": 230, "r": 255, "textB": 0, "textG": 0, "textR": 0}, "comment": MK + "-" + clave, "comment2": ""}
def hay(lst, clave): return any(x.get("comment") == MK + "-" + clave for x in lst)
def nuevo(lst, idx, e, clave):
    if hay(lst, clave): return False
    if idx is None or idx > len(lst): idx = len(lst)
    lst.insert(idx, marca(clave)); lst.insert(idx + 1, e); return True
def walk(lst):
    for e in lst:
        yield e
        yield from walk(e.get("events", []))
def own(e): return json.dumps({k: v for k, v in e.items() if k != "events"}, ensure_ascii=False)
def cond_has(e, tipo, params, inv=None):
    return any(x["type"]["value"] == tipo and x["parameters"][:len(params)] == params and (inv is None or bool(x["type"].get("inverted")) == inv) for x in e.get("conditions", []))
def act_has(e, tipo, params):
    return any(x["type"]["value"] == tipo and x["parameters"][:len(params)] == params for x in e.get("actions", []))
def add_cond(e, cc):
    if cc not in e["conditions"]: e["conditions"].append(cc)
def add_act(e, aa):
    if aa not in e["actions"]: e["actions"].append(aa)
def vid(l, n): return next(o for o in l["objects"] if o["name"] == n)
def addres(nombre, archivo, kind="image"):
    if not any(r["name"] == nombre for r in d["resources"]["resources"]):
        r = res_imagen(nombre, archivo); r["kind"] = kind
        if kind == "font": r.pop("smoothed", None)
        d["resources"]["resources"].append(r)
def addvar(lay, nombre, valor):
    if not any(v["name"] == nombre for v in lay["variables"]):
        lay["variables"].append({"name": nombre, "type": "number", "value": valor})
def grupo(lay, nombre): return next(e for e in lay["events"] if e.get("name") == nombre)
def poner_texto(lay, obj, contiene, nuevo_val, solo_primero=False):
    """cambia el literal de acciones String(obj) cuyo valor contiene `contiene` (None = cualquiera con literal)"""
    n = 0
    for e in walk(lay["events"]):
        for x in e.get("actions", []):
            p = x["parameters"]
            if x["type"]["value"].endswith("String") and p[:1] == [obj] and len(p) >= 3 and p[1] == "=" and p[2] != nuevo_val and p[2].lstrip().startswith('"') \
               and (contiene is None or contiene in p[2]):
                p[2] = nuevo_val; n += 1
    return n

# =====================================================================
# 1 · FUENTE
# =====================================================================
addres("PixelifySans.ttf", "assets/interfaz/fuentes/PixelifySans.ttf", "font")
def fuente(lay, nombre, size=None):
    o = vid(lay, nombre); o["font"] = "PixelifySans.ttf"
    if "content" in o: o["content"]["font"] = "PixelifySans.ttf"
    if size: o["characterSize"] = size; o["content"]["characterSize"] = size

# =====================================================================
# 2 · TIENDA FUERA (máquinas, precios, dinero del equipo, monedas, pasiva de Tony)
# =====================================================================
J["instances"] = [i for i in J["instances"] if not (i["name"] == "TxtPrecio" or (i["name"] == "Contenedor" and any(v["name"] == "Tipo" and v["value"] == "maquina" for v in i.get("initialVariables", []))))]
GL = grupo(J, "Lockers, mochilas, máquinas y dinero")
# 2a · la moneda de los lockers pasa a ser galletas
def monedas_a_galletas(lst):
    for e in walk(lst):
        if any(x["type"]["value"] == "Create" and x["parameters"][:1] == ["Moneda"] for x in e.get("actions", [])):
            nuevas = []
            for x in e["actions"]:
                p = x["parameters"]
                if x["type"]["value"] == "Create" and p[:1] == ["Moneda"]:
                    p[0] = "Comida"; nuevas += [x, a("SetAnimationName", "Comida", '"galletas"')]
                elif x["type"]["value"] == "ModVarObjet" and p[:2] == ["Moneda", "Valor"]:
                    nuevas.append(a("ModVarObjet", "Comida", "Cura", "=", "30"))
                else: nuevas.append(x)
            e["actions"] = nuevas
monedas_a_galletas(GL["events"])
# 2b · quitar eventos de compra/precio/dinero
def es_tienda(e):
    o = own(e)
    if not e["type"].endswith("Standard"): return "TxtPrecio" in o or "Comprando" in o

    if "TxtPrecio" in o or "DineroDado" in o: return True
    if any(x["type"]["value"] == "ModVarScene" and x["parameters"][:1] == ["Dinero"] for x in e.get("actions", [])): return True
    if any("Dinero" in " ".join(map(str, x["parameters"])) for x in e.get("conditions", [])): return True
    if any(x["type"]["value"] == "CollisionNP" and x["parameters"][:2] == ["Sup", "Moneda"] for x in e.get("conditions", [])): return True
    if cond_has(e, "VarObjetTxt", ["Contenedor", "Tipo", "=", '"maquina"'], inv=False) and (
            any(x["type"]["value"] == "CompareObjectTimer" for x in e["conditions"]) or cond_has(e, "VarObjet", ["Contenedor", "Usada", "=", "1"])):
        return True
    if cond_has(e, "VarScene", ["VerDebug", "=", "1"]) and any(x["type"]["value"] == "KeyReleased" and x["parameters"][-1] == "t" for x in e["conditions"]): return True
    if any(x["type"]["value"] == "ModVarSceneTxt" and x["parameters"][:1] == ["Banner"] and "para comprar" in x["parameters"][-1] for x in e.get("actions", [])): return True
    return False
def quitar_tienda(lst):
    n = 0
    for e in list(lst):
        if es_tienda(e): lst.remove(e); n += 1
        elif e.get("events"): n += quitar_tienda(e["events"])
    return n
quitar_tienda(J["events"])
# el comentario del grupo
for e in walk(GL["events"]):
    if e["type"].endswith("Comment") and "xpendedoras" in e["comment"]:
        e["comment"] = "Lockers y mochilas: mantener Usar 1 s junto a ellos para revisarlos (galletas, jugo o un libro). Comida guardada: con la vida llena se guarda 1 comida y se come sola bajo 30 % de vida."
# 2c · sin Dinero residual
for e in walk(J["events"]):
    for x in e.get("actions", []):
        if x["type"]["value"].endswith("String") and x["parameters"][:1] == ["TxtInfest"]:
            x["parameters"][-1] = re.sub(r'\s*\+\s*"\s+\$"\s*\+\s*ToString\(floor\(Variable\(Dinero\)\)\)', "", x["parameters"][-1])
        if x["type"]["value"] == "ModVarGlobalTxt" and x["parameters"][:1] == ["Premios"]:
            x["parameters"][-1] = x["parameters"][-1].replace(' + NewLine() + "El empresario (Tony): $" + ToString(floor(Variable(Dinero))) + " para el equipo"', "")
        if x["type"]["value"].endswith("String") and x["parameters"][:1] == ["TxtHudDinero"]:
            x["parameters"][-1] = "ToString(floor(Variable(OroJefe) * Variable(Jefe)))"
# 2d · pasiva de Tony nueva: "Buen apetito" (la comida le cura 50 % más)
GH = grupo(J, "Habilidades, especiales y pasivas")
comida = next((e for e in walk(GH["events"]) if e["type"].endswith("Standard") and cond_has(e, "CollisionNP", ["Sup", "Comida"]) and any(x["type"]["value"] == "ModVarObjet" and x["parameters"][:2] == ["Sup", "Vida"] for x in e["actions"])), None)
assert comida is not None
if not any(own(s).find("tony") >= 0 for s in comida.get("events", [])):
    for pj in ("tony", "tonyfuerte"):
        comida.setdefault("events", []).append(std([c("VarObjetTxt", "Sup", "Personaje", "=", '"%s"' % pj)],
            [a("ModVarObjet", "Sup", "Vida", "=", "min(Sup.Variable(VidaMax), Sup.Variable(Vida) + Comida.Variable(Cura) * 0.5)")]))
# 2e · HUD: el panel de dinero solo existe en modo Jefe (muestra el oro)
GHUD = grupo(J, "Interfaz: HUD con paneles")
nuevo(GHUD["events"], None, std([c("VarScene", "Jefe", "=", "0")], [a("Cache", "HudDinPanel", ""), a("Cache", "TxtHudDinero", "")]), "SINDINERO")
# 2f · descripción de Tony
for lay in (M,):
    poner_texto(lay, "EqDesc", "Gana dinero para el equipo", '"Come mejor: la comida le cura 50 % más"')

# =====================================================================
# 3 · MODO JEFE: monedas por dificultad y sin instrucciones (JS)
# =====================================================================
def parche_jefe(s):
    s = s.replace('st.rate = dif === "facil" ? 2 : (dif === "pesadilla" ? 6 : 4);', 'st.rate = dif === "facil" ? 1 / 2.5 : (dif === "pesadilla" ? 1 / 1.5 : 1 / 2);')
    s = s.replace("help: true, helpT: 0,", "help: false, helpT: 0,")
    s = s.replace("if (edge72) st.help = !st.help;", "")
    s = s.replace('else if (st.sel < 0) say("Primero elige una carta (teclas 1 a 8)", "255;225;120");', 'else if (st.sel < 0) { /* sin carta elegida: no pasa nada */ }')
    # panel de instrucciones: se quita; la barra de la próxima moneda se queda, con su marco
    a0 = s.find("        panel(20, 300, 400, 330);")
    if a0 >= 0:
        b0 = s.find("        // barra de progreso del próximo oro")
        s = s[:a0] + "        panel(30, 578, 380, 38, \"70;190;170\");\n" + s[b0:]
    t0 = s.find('      txt("MISIÓN DEL JEFE"')
    if t0 >= 0:
        t1 = s.find('"190;190;210", "left", 380);\n', t0) + len('"190;190;210", "left", 380);\n')
        s = s[:t0] + s[t1:]
    s = s.replace('hit(hx, hy, 20, 300, 400, 330)', 'hit(hx, hy, 30, 578, 380, 38)')
    s = s.replace('txt("MAPA · clic para mover la cámara"', 'txt("MAPA"')
    h0 = s.find("      if (st.help && active && dB) {")
    if h0 >= 0:
        h1 = s.find("      if (st.msg && st.t < st.msg.t && !overUI)", h0)
        s = s[:h0] + s[h1:]
    return s
cambios_jefe = 0
for e in walk(grupo(J, "Modo Jefe de zombies")["events"]):
    if e["type"].endswith("JsCode") and "Modo Jefe de zombies" in e["inlineCode"]:
        nuevo_js = parche_jefe(e["inlineCode"])
        if nuevo_js != e["inlineCode"]: e["inlineCode"] = nuevo_js; cambios_jefe += 1
src = open(JEFE_SRC, encoding="utf-8").read(); ns = parche_jefe(src)
if ns != src: open(JEFE_SRC, "w", encoding="utf-8").write(ns)

# =====================================================================
# 4 · TEXTOS DE GUÍA FUERA (Titulo, Menú, Juego, Pausa, Resultados)
# =====================================================================
poner_texto(T_, "TxtSub", "Presiona Enter, Espacio", '"La FDI se llenó de zombies. Escapen."')
poner_texto(T_, "TxtSub", "PRESIONA ENTER", '""')
poner_texto(M, "TxtPie", None, '""')
poner_texto(M, "TxtSubM", None, '""')
poner_texto(M, "TxtMenu", "ÚNANSE", '"ÚNANSE"')
poner_texto(M, "TxtMenu", "ELIGE EL MODO", '"ELIGE EL MODO"')
poner_texto(M, "EqBarEst", "clic en un personaje", '""')
poner_texto(M, "JefeLinea", None, '""')
for e in walk(M["events"]):
    for x in e.get("actions", []):
        if x["type"]["value"] == "ModVarSceneTxt" and x["parameters"][:1] == ["JefeLinea"] and len(x["parameters"]) >= 3: x["parameters"][-1] = '""'
        if x["type"]["value"] == "Montre" and x["parameters"][:1] == ["BarraPie"]:
            x["type"]["value"] = "Cache"
# Juego
poner_texto(J, "TxtDialogo", "CLIC para pegar", '"¿Qué hacemos? ... ¡Agarra la regla!"')
poner_texto(J, "TxtAyuda", "DEMOSTRACIÓN", '""')
poner_texto(J, "TxtAyuda", "Teclado: WASD", '""')
poner_texto(J, "TxtAyuda", "Control: stick", '""')
poner_texto(J, "TxtAyuda", "mantén Usar", '"¡Ayuda! ¡Aquí!"')
poner_texto(J, "TxtOmitir", "OMITIR", '"OMITIR >>"')
poner_texto(J, "TxtPausaB0", "Enter, clic o A", '"VOLVER"')
for e in walk(J["events"]):
    for x in e.get("actions", []):
        p = x["parameters"]
        if x["type"]["value"] == "ModVarSceneTxt" and p[:1] == ["Banner"] and len(p) >= 3:
            if "MORDIDO" in p[-1]:
                p[-1] = re.sub(r'\s*Cúrenlo: mantener Usar junto a él', "", p[-1])
            if "nadie puede unirse a tu partida" in p[-1]: p[-1] = '""'
# Resultados: sin guía
poner_texto(R, "TxtPie", None, '""')

# =====================================================================
# 5 · MENÚ: 3.ª tarjeta EN LÍNEA + hover con el ratón
# =====================================================================
for n in ("PMX", "PMY"): addvar(M, n, -1)
ME = M["events"]
if not any(i["name"] == "MarcoModo" and any(v["name"] == "Idx" and v["value"] == 2 for v in i["initialVariables"]) for i in M["instances"]):
    for nom in ("MarcoModo", "IlusModo", "TxtCapA", "TxtCapB"):
        src_i = next(i for i in M["instances"] if i["name"] == nom and any(v["name"] == "Idx" and v["value"] == 1 for v in i["initialVariables"]))
        ni = copy.deepcopy(src_i); ni["persistentUuid"] = __import__("uuid").uuid4().hex[:8] + "-0000-4000-8000-000000000028"
        ni["initialVariables"] = [dict(v, value=2) if v["name"] == "Idx" else v for v in ni["initialVariables"]]
        M["instances"].append(ni)
CAPX = {0: 390, 1: 960, 2: 1530}
for e in ME:
    if not e["type"].endswith("Standard"): continue
    for x in e.get("actions", []):
        p = x["parameters"]
        if x["type"]["value"] == "MettreX" and p[:1] in (["TxtCapA"], ["TxtCapB"]):
            p[2] = re.sub(r"^(560|1360) - ", lambda m: ("390" if m.group(1) == "560" else "960") + " - ", p[2]) if "PJT" not in p[2] else p[2]
# (las posiciones de jefetipo se fijan en sus propios eventos, que corren después)
poner_texto(M, "TxtCapB", "contra el Jefe", '"Jefe contra 4 sobrevivientes"')
for e in ME:
    if e["type"].endswith("Standard") and cond_has(e, "VarObjet", ["TxtCapB", "Idx", "=", "1"]) and len(e["conditions"]) == 2:
        pass
PM = c("VarSceneTxt", "Paso", "=", '"modo"')
PJT = c("VarSceneTxt", "Paso", "=", '"jefetipo"')
def posiciones():
    ev = []
    for k, (mx, ix) in {0: (170, 220), 1: (740, 790), 2: (1310, 1360)}.items():
        ev.append(std([PM, c("VarObjet", "MarcoModo", "Idx", "=", str(k))], [a("MettreX", "MarcoModo", "=", str(mx))]))
        ev.append(std([PM, c("VarObjet", "IlusModo", "Idx", "=", str(k))], [a("MettreX", "IlusModo", "=", str(ix))]))
    for k, (mx, ix) in {0: (340, 390), 1: (1140, 1190)}.items():
        ev.append(std([PJT, c("VarObjet", "MarcoModo", "Idx", "=", str(k))], [a("MettreX", "MarcoModo", "=", str(mx))]))
        ev.append(std([PJT, c("VarObjet", "IlusModo", "Idx", "=", str(k))], [a("MettreX", "IlusModo", "=", str(ix))]))
    return ev
if not hay(ME, "POS"):
    ME.append(marca("POS")); ME.extend(posiciones())
    # animación / aspecto de la tarjeta 3
    ME.append(std([c("VarObjet", "IlusModo", "Idx", "=", "2")], [a("SetAnimationName", "IlusModo", '"o"')]))
    ME.append(std([c("VarObjet", "MarcoModo", "Idx", "=", "2"), c("VarScene", "Sel", "=", "2")], [a("SetAnimationName", "MarcoModo", '"s"'), a("Opacity", "MarcoModo", "=", "255")]))
    ME.append(std([c("VarObjet", "MarcoModo", "Idx", "=", "2"), c("VarScene", "Sel", "!=", "2")], [a("SetAnimationName", "MarcoModo", '"n"'), a("Opacity", "MarcoModo", "=", "110")]))
    ME.append(std([c("VarObjet", "IlusModo", "Idx", "=", "2"), c("VarScene", "Sel", "=", "2")], [a("Opacity", "IlusModo", "=", "255")]))
    ME.append(std([c("VarObjet", "IlusModo", "Idx", "=", "2"), c("VarScene", "Sel", "!=", "2")], [a("Opacity", "IlusModo", "=", "100")]))
    ME.append(std([PM, c("VarObjet", "TxtCapA", "Idx", "=", "2")], [a("TextObject::String", "TxtCapA", "=", '"EN LÍNEA"'), a("MettreX", "TxtCapA", "=", "1530 - TxtCapA.Width() / 2")]))
    ME.append(std([PM, c("VarObjet", "TxtCapB", "Idx", "=", "2")], [a("TextObject::String", "TxtCapB", "=", '"Salas por código · internet"'), a("MettreX", "TxtCapB", "=", "1530 - TxtCapB.Width() / 2")]))
    ME.append(std([PM, c("VarObjet", "IlusModo", "Idx", "=", "2")], [a("Montre", "IlusModo", "")]))
    ME.append(std([PJT, c("VarObjet", "MarcoModo", "Idx", "=", "2")], [a("Cache", "MarcoModo", "")]))
    ME.append(std([PJT, c("VarObjet", "IlusModo", "Idx", "=", "2")], [a("Cache", "IlusModo", "")]))
    ME.append(std([PJT, c("VarObjet", "TxtCapA", "Idx", "=", "2")], [a("Cache", "TxtCapA", "")]))
    ME.append(std([PJT, c("VarObjet", "TxtCapB", "Idx", "=", "2")], [a("Cache", "TxtCapB", "")]))
# videos de las tarjetas 1 y 2 en su nueva posición
GVd = grupo(M, "Videos")
for e in walk(GVd["events"]):
    for x in e.get("actions", []):
        if x["type"]["value"] == "MettreX" and x["parameters"][:1] == ["VidIlusEscape"] and x["parameters"][2] == "390": x["parameters"][2] = "220"
        if x["type"]["value"] == "MettreX" and x["parameters"][:1] == ["VidIlusJefe"] and x["parameters"][2] == "1190": x["parameters"][2] = "790"
# izquierda/derecha en la lista de modos
for e in ME:
    if e["type"].endswith("Standard") and cond_has(e, "VarSceneTxt", ["Paso", "=", '"modo"']) and any(x["type"]["value"] == "ModVarScene" and x["parameters"][:2] == ["Sel", "="] and "mod(Variable(Sel)" in x["parameters"][2] for x in e["actions"]):
        orx = next(x for x in e["conditions"] if x["type"]["value"].endswith("Or"))
        arriba = "+ 2, 3" in next(x["parameters"][2] for x in e["actions"] if x["parameters"][:1] == ["Sel"])
        ks = ("Left", "a") if arriba else ("Right", "d")
        for k in ks:
            cc = c("KeyReleased", "", k)
            if cc not in orx["subInstructions"]: orx["subInstructions"].append(cc)
        for k in (("Left",) if arriba else ("Right",)):
            for pad in (1, 2, 3, 4):
                cc = c("Gamepads::C_Button_released", "", str(pad), '"%s"' % k, "")
                if cc not in orx["subInstructions"]: orx["subInstructions"].append(cc)
# hover del ratón (solo si se movió): modo (3 tarjetas) y jefetipo (2)
def hover(paso, k, x0, x1, clave):
    movido = orc(c("BuiltinCommonInstructions::CompareNumbers", "MouseX()", "!=", "Variable(PMX)"), c("BuiltinCommonInstructions::CompareNumbers", "MouseY()", "!=", "Variable(PMY)"))
    cds = [paso, movido, c("BuiltinCommonInstructions::CompareNumbers", "MouseX()", ">=", str(x0)), c("BuiltinCommonInstructions::CompareNumbers", "MouseX()", "<", str(x1)),
           c("BuiltinCommonInstructions::CompareNumbers", "MouseY()", ">=", "250"), c("BuiltinCommonInstructions::CompareNumbers", "MouseY()", "<", "790")]
    nuevo(ME, None, std(cds, [a("ModVarScene", "Sel", "=", str(k))]), clave)
for k, x0 in enumerate((170, 740, 1310)): hover(PM, k, x0, x0 + 440, "HOV-M%d" % k)
for k, x0 in enumerate((340, 1140)): hover(PJT, k, x0, x0 + 440, "HOV-J%d" % k)
nuevo(ME, None, std([], [a("ModVarScene", "PMX", "=", "MouseX()"), a("ModVarScene", "PMY", "=", "MouseY()")]), "PMOUSE")

# =====================================================================
# 6 · RESULTADOS: fuente, ajuste al cuadro, botones de la pantalla de muerte
# =====================================================================
for n, s in (("TxtRes", 60), ("TxtDet", 30), ("TxtBtnRei", 40), ("TxtBtnMenuR", 40)):
    fuente(R, n, s)
RE = R["events"]
# sin pie de guía; barra del pie oculta
nuevo(RE, None, std([], [a("Cache", "BarraPieR", ""), a("Cache", "TxtPie", "")]), "SINPIE")
# títulos del modo Jefe más cortos
poner_texto(R, "TxtRes", "LOS ATRAPÓ A TODOS", '"¡GANÓ EL JEFE!"')
poner_texto(R, "TxtRes", "EL JEFE PERDIÓ", '"¡EL JEFE PERDIÓ!"')
# posición del detalle dentro del panel
for e in walk(RE):
    for x in e.get("actions", []):
        if x["type"]["value"] == "MettreY" and x["parameters"][:1] == ["TxtDet"]: x["parameters"][2] = "452"
# botones visibles en victoria y derrota
for e in list(RE):
    if not e["type"].endswith("Standard"): continue
    if cond_has(e, "VarGlobalTxt", ["Resultado", "=", '"victoria"']) and len(e["conditions"]) == 1 and any(x["type"]["value"] == "Cache" and x["parameters"][:1] == ["BtnRei"] for x in e["actions"]):
        RE.remove(e)
for e in RE:
    if e["type"].endswith("Standard") and any(x["type"]["value"] == "Montre" and x["parameters"][:1] == ["BtnRei"] for x in e["actions"]):
        e["conditions"] = [x for x in e["conditions"] if not (x["type"]["value"] == "VarGlobalTxt" and x["parameters"][:1] == ["Resultado"])]
        e["actions"] = [x for x in e["actions"] if x["parameters"][:1] != ["TxtPie"]]
# la salida de victoria (Enter/clic -> título) se sustituye por los mismos botones
for e in list(RE):
    if e["type"].endswith("Standard") and cond_has(e, "VarGlobalTxt", ["Resultado", "=", '"victoria"']) and any(x["type"]["value"].endswith("Or") for x in e["conditions"]) and any(x["type"]["value"] == "CompareTimer" for x in e["conditions"]):
        RE.remove(e)
# clics con rectángulos fijos (como el resto de menús) y teclado/mando para ambos resultados
def rect(x0, x1, y0, y1):
    N = "BuiltinCommonInstructions::CompareNumbers"
    return [c(N, "MouseX()", ">=", str(x0)), c(N, "MouseX()", "<", str(x1)), c(N, "MouseY()", ">=", str(y0)), c(N, "MouseY()", "<", str(y1))]
for e in RE:
    if not e["type"].endswith("Standard"): continue
    es_menu_click = any(x["type"]["value"] == "MouseButtonReleased" for x in e["conditions"]) and any("BtnMenuR" in " ".join(map(str, x["parameters"])) for x in e["conditions"])
    es_rei_click = any(x["type"]["value"] == "MouseButtonReleased" for x in e["conditions"]) and any("BtnRei" in " ".join(map(str, x["parameters"])) for x in e["conditions"])
    if es_menu_click or es_rei_click:
        y = (790, 922) if es_menu_click else (640, 772)
        e["conditions"] = [c("CompareTimer", "", '"t"', ">=", "0.6"), c("MouseButtonReleased", "", "Left")] + rect(150, 530, *y)
    elif cond_has(e, "VarGlobalTxt", ["Resultado", "!=", '"victoria"']) and any(x["type"]["value"].endswith("Or") for x in e["conditions"]) and any(x["type"]["value"] == "CompareTimer" for x in e["conditions"]):
        e["conditions"] = [x for x in e["conditions"] if not (x["type"]["value"] == "VarGlobalTxt" and x["parameters"][:1] == ["Resultado"])]
        orx = next(x for x in e["conditions"] if x["type"]["value"].endswith("Or"))
        if any(y["parameters"][-1] == "Escape" for y in orx["subInstructions"] if y["type"]["value"] == "KeyReleased"):
            for pad in (1, 2, 3, 4):
                cc = c("Gamepads::C_Button_released", "", str(pad), '"B"', "")
                if cc not in orx["subInstructions"]: orx["subInstructions"].append(cc)
        for x in e["conditions"]:
            if x["type"]["value"] == "CompareTimer": x["parameters"][-1] = "0.6"
# resalte al pasar el ratón
nuevo(RE, None, std([], [a("Opacity", "BtnRei", "=", "225"), a("Opacity", "BtnMenuR", "=", "225")]), "OPA")
nuevo(RE, None, std(rect(150, 530, 640, 772), [a("Opacity", "BtnRei", "=", "255")]), "HOV-REI")
nuevo(RE, None, std(rect(150, 530, 790, 922), [a("Opacity", "BtnMenuR", "=", "255")]), "HOV-MENU")
# ajuste de texto al cuadro (una vez por escena)
FIT = r"""
/*FDIZ-FASE28-FIT*/
const scn = runtimeScene;
if (!scn._fit28) {
  scn._fit28 = 1;
  const fit = (n, maxW, maxH, base) => { const a = scn.getObjects(n); if (!a || !a.length) return; const o = a[0]; o.setCharacterSize(base); const w = o.getWidth(), h = o.getHeight(); const k = Math.min(1, maxW / Math.max(1, w), maxH / Math.max(1, h)); if (k < 1) o.setCharacterSize(Math.max(14, Math.floor(base * k))); };
  fit("TxtRes", 600, 130, 60);
  fit("TxtDet", 740, 420, 30);
}
"""
if not hay(RE, "FIT"):
    RE.append(marca("FIT")); RE.append({"type": "BuiltinCommonInstructions::JsCode", "inlineCode": FIT, "parameterObjects": "", "useStrict": True, "eventsSheetExpanded": False})

# =====================================================================
# 7 · ESCENA ONLINE: fondo con video, velo, sin pie
# =====================================================================
if not any(o["name"] == "VidFondoModos" for o in O["objects"]):
    O["objects"].append(copy.deepcopy(vid(M, "VidFondoModos")))
    O["instances"].insert(0, instancia("VidFondoModos", 0, 0, "", -1, 1920, 1080))
vevt = next((e for e in walk(grupo(M, "Videos")["events"]) if e["type"].endswith("Standard") and act_has(e, "Play", ["VidFondoModos"]) and any(x["type"]["value"] == "Play" for x in e["conditions"])), None)
if vevt is not None and not hay(O["events"], "VIDEO"):
    cp = copy.deepcopy(vevt)
    cp["conditions"] = [x for x in cp["conditions"] if x["type"]["value"] != "VarSceneTxt"]
    O["events"].append(marca("VIDEO"))
    O["events"].append(cp)
    O["events"].append(std([], [a("Cache", "Fondo", ""), a("Opacity", "Velo", "=", "75"), a("MettreX", "VidFondoModos", "=", "0")]))

# =====================================================================
# 8 · net_core.js (sala en línea sin textos de guía)
# =====================================================================
js = open(NET, encoding="utf-8").read()
if "FDIZ-F28" not in js:
    lines = js.split("\n")
    def borra(sub, n=1):
        global lines
        idx = [i for i, l in enumerate(lines) if sub in l]
        assert len(idx) == n, (sub, len(idx))
        for i in reversed(idx): del lines[i]
    # menú inicial
    i0 = next(i for i, l in enumerate(lines) if l.strip().startswith("if (N.preJefe) { T(scn, \"Crear sala"))
    del lines[i0:i0 + 4]
    borra("W/S elegir · Enter aceptar")
    borra("El código aparece arriba, en la sala del host")
    borra("Enter conectar · Ctrl+V pegar")
    borra("Enter o Esc para volver")
    borra("Díselo a las otras PCs")
    borra("N dificultad · Mando: X dificultad")
    borra("A/D cambiar personaje · Enter confirmar")
    js = "\n".join(lines)
    def rep(viejo, nuevo_):
        global js
        assert js.count(viejo) == 1, viejo[:70]
        js = js.replace(viejo, nuevo_)
    rep('"(sin jugadores: Enter = teclado, A = mando)"', '"(sin jugadores)"')
    rep('"Todos listos: Enter / Start para EMPEZAR"', '"¡TODOS LISTOS!"')
    rep('"Esperando a que todos confirmen (Enter / A)"', '"Esperando a que todos confirmen…"')
    js = re.sub(r'(Eres el Jefe: no puedes unirte como sobreviviente\.)[^"]*"', r'\1"', js)
    rep("    for (let i = P.n; i < P.a.length; i++) P.a[i].hide(true);",
        "    /*FDIZ-F28*/ { const bp = scn.getObjects(\"BarraPie\"); if (bp && bp[0]) bp[0].hide(!(u.st === \"lobby\" && N.L)); }\n    for (let i = P.n; i < P.a.length; i++) P.a[i].hide(true);")
    open(NET, "w", encoding="utf-8").write(js)

# verificación interna: nada de Dinero (salvo OroJefe) ni TxtPrecio en Juego
resto = [own(e)[:80] for e in walk(J["events"]) if re.search(r"\bDinero\b|TxtPrecio", own(e))]
print("restos de dinero/tienda en Juego:", len(resto), resto[:3])
print("jefe js parcheado:", cambios_jefe)
json.dump(d, open(PRY, "w"), ensure_ascii=False, indent=2)
print("OK fase 28")
