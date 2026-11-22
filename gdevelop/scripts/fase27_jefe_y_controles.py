"""Fase 27 · Pantalla de controles con ilustraciones, pantalla Local/En línea del modo Jefe,
lobby en línea con estilo del juego (código de sala, host secundario). Idempotente.
Orden de uso:  python3 fase25_online.py && python3 fase26_multijugador.py && python3 fase27_jefe_y_controles.py
(fase25 re-embebe net_core.js, que esta fase también parchea).
"""
import json, copy, os, shutil, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gd_util import c, a, instancia, res_imagen, objeto_sprite, animacion

AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
NET = os.path.join(AQUI, "net_core.js")
bak = os.path.join(AQUI, "..", "respaldos", "antes_de_fase27_20261117.json")
if not os.path.exists(bak):
    shutil.copy(PRY, bak)
d = json.load(open(PRY))
J = next(l for l in d["layouts"] if l["name"] == "Juego")
M = next(l for l in d["layouts"] if l["name"] == "Menu")
O = next(l for l in d["layouts"] if l["name"] == "Online")
MK = "FDIZ-FASE27"
STD = "BuiltinCommonInstructions::Standard"

def std(conds, acts, sub=()):
    return {"type": STD, "conditions": conds, "actions": acts, "events": list(sub)}
def orc(*subs):
    return {"type": {"inverted": False, "value": "BuiltinCommonInstructions::Or"}, "parameters": [], "subInstructions": list(subs)}
def marca(clave):
    return {"type": "BuiltinCommonInstructions::Comment", "color": {"b": 109, "g": 230, "r": 255, "textB": 0, "textG": 0, "textR": 0}, "comment": MK + "-" + clave, "comment2": ""}
def nuevo(lst, idx, e, clave):
    if any(x.get("comment") == MK + "-" + clave for x in lst):
        return False
    if idx is None or idx > len(lst): idx = len(lst)
    lst.insert(idx, marca(clave)); lst.insert(idx + 1, e)
    return True
def hay_marca(lst, clave): return any(x.get("comment") == MK + "-" + clave for x in lst)
def vid(l, n): return next(o for o in l["objects"] if o["name"] == n)
def addres(nombre, archivo):
    if not any(r["name"] == nombre for r in d["resources"]["resources"]):
        d["resources"]["resources"].append(res_imagen(nombre, archivo))
def addvar_global(nombre, valor):
    if not any(v["name"] == nombre for v in d["variables"]):
        d["variables"].append({"name": nombre, "type": "number", "value": valor})
def addvar(lay, nombre, valor):
    if not any(v["name"] == nombre for v in lay["variables"]):
        lay["variables"].append({"name": nombre, "type": "number", "value": valor})
def hallar(lst, pred):
    return next((i, e) for i, e in enumerate(lst) if e["type"].endswith("Standard") and pred(e))
def cond_has(e, tipo, params):
    return any(x["type"]["value"] == tipo and x["parameters"][:len(params)] == params for x in e.get("conditions", []))
def act_has(e, tipo, params):
    return any(x["type"]["value"] == tipo and x["parameters"][:len(params)] == params for x in e.get("actions", []))
def add_cond(e, cc):
    if cc not in e["conditions"]: e["conditions"].append(cc)
def add_act(e, aa):
    if aa not in e["actions"]: e["actions"].append(aa)

# ---------------------------------------------------------------- recursos y variables
for n in ("p27_ctl_teclado", "p27_ctl_mando", "p27_ilus_local", "p27_ilus_online", "p27_panel_sala"):
    pass
addres("p27_ctl_teclado", "assets/interfaz/p27_ctl_teclado.png")
addres("p27_ctl_mando", "assets/interfaz/p27_ctl_mando.png")
addres("p27_ilus_local", "assets/interfaz/ilus_modo_local.png")
addres("p27_ilus_online", "assets/interfaz/ilus_modo_online.png")
addres("p27_panel_sala", "assets/interfaz/p27_panel_sala.png")
addvar_global("OnlineJefe", 0)

# =====================================================================
# 1 · PAUSA → CONTROLES con ilustración de teclado/ratón y mando
# =====================================================================
for nom, res in (("CtlTeclado", "p27_ctl_teclado"), ("CtlMando", "p27_ctl_mando")):
    if not any(o["name"] == nom for o in J["objects"]):
        J["objects"].append(objeto_sprite(nom, [animacion("p", [res], 1, False, (0, 0))]))
        J["instances"].append(instancia(nom, 150 if nom == "CtlTeclado" else 1050, 190, "HUD", 90003, 720, 300))
for nom in ("TxtPausaCtl1", "TxtPausaCtl2"):
    o = vid(J, nom); o["characterSize"] = 26; o["content"]["characterSize"] = 26

CTL1 = ("TECLADO Y RATÓN\nW A S D  moverse  ·  Ratón  apuntar\nClic izq.  golpear / disparar\nClic der. o R  lanzar objeto\nF (mantener)  abrir puertas, salvar,\n revisar y usar objetivos\nQ  habilidad  ·  E  especial\nShift  correr  ·  Esc o P  pausa")
CTL2 = ("MANDO\nStick izq.  moverse  ·  Stick der.  apuntar\nX  golpear / disparar\nB  lanzar objeto\nA (mantener)  abrir puertas, salvar,\n revisar y usar objetivos\nY  habilidad  ·  RB  especial\nStart  pausa")
def lit(t): return '"' + t.replace("\n", '" + NewLine() + "') + '"'
GP = next(e for e in J["events"] if e.get("name") == "Menú de pausa")
for e in GP["events"]:
    if not e["type"].endswith("Standard"): continue
    acts = e.get("actions", [])
    if any(x["type"]["value"] == "TextObject::String" and x["parameters"][0] == "TxtPausaCtl1" for x in acts):
        for x in acts:
            p = x["parameters"]
            if x["type"]["value"] == "TextObject::String" and p[0] == "TxtPausaCtl1": p[2] = lit(CTL1)
            if x["type"]["value"] == "TextObject::String" and p[0] == "TxtPausaCtl2": p[2] = lit(CTL2)
            if x["type"]["value"] == "MettreY" and p[0] in ("TxtPausaCtl1", "TxtPausaCtl2"): p[2] = "505"
        if any(x["type"]["value"] == "Montre" and x["parameters"][0] == "TxtPausaCtl1" for x in acts):
            for n in ("CtlTeclado", "CtlMando"): add_act(e, a("Montre", n, ""))
    # ocultar en el resto de estados (Pausa=0 y vista normal)
    if any(x["type"]["value"] == "Cache" and x["parameters"][0] == "TxtPausaCtl1" for x in acts):
        for n in ("CtlTeclado", "CtlMando"): add_act(e, a("Cache", n, ""))

# =====================================================================
# 2 · MENÚ: paso "jefetipo" (Local / En línea) para el modo Jefe
# =====================================================================
for n in ("p27_ilus_local", "p27_ilus_online"): pass
ilus = vid(M, "IlusModo")
for nom, res in (("l", "p27_ilus_local"), ("o", "p27_ilus_online")):
    if not any(an["name"] == nom for an in ilus["animations"]):
        ilus["animations"].append(animacion(nom, [res], 1, False, (0, 0)))
ME = M["events"]
PJT = c("VarSceneTxt", "Paso", "=", '"jefetipo"')
NOJT = c("VarSceneTxt", "Paso", "!=", '"jefetipo"')

# 2a · entrar: Jefe → jefetipo (en lugar de "unirse")
i11, e11 = hallar(ME, lambda e: cond_has(e, "VarSceneTxt", ["Paso", "=", '"modo"']) and cond_has(e, "VarScene", ["Sel", "!=", "2"]) and act_has(e, "ModVarSceneTxt", ["Paso", "=", '"unirse"']))
for sub in e11["events"]:
    if cond_has(sub, "VarScene", ["Sel", "=", "1"]):
        add_act(sub, a("ModVarSceneTxt", "Paso", "=", '"jefetipo"'))
        add_act(sub, a("ModVarScene", "Sel", "=", "0"))
        add_act(sub, a("ModVarGlobal", "OnlineJefe", "=", "0"))
# 2b · Online desde el menú de modos: no es Jefe
for e in ME:
    if e["type"].endswith("Standard") and cond_has(e, "VarSceneTxt", ["Paso", "=", '"modo"']) and act_has(e, "Scene", ["", '"Online"']):
        add_act(e, a("ModVarGlobal", "OnlineJefe", "=", "0"))
# 2c · volver de la sala en línea del Jefe → pantalla jefetipo
i1, e1 = hallar(ME, lambda e: cond_has(e, "DepartScene", []) and act_has(e, "ModVarSceneTxt", ["Paso", "=", '"modo"']))
nuevo(ME, i1 + 1, std([c("DepartScene", ""), c("VarGlobal", "OnlineJefe", ">=", "1")],
                       [a("ModVarSceneTxt", "Paso", "=", '"jefetipo"'), a("ModVarScene", "Sel", "=", "1"), a("ModVarGlobalTxt", "Modo", "=", '"jefe"'),
                        a("ModVarScene", "S1Ctl", "=", "-1"), a("ModVarGlobal", "OnlineJefe", "=", "0"), a("ResetTimer", "", '"paso"')]), "VOLVER-ONLINE")

# 2d · Esc: jefetipo → modo; equipo (Jefe) → jefetipo
i158, e158 = hallar(ME, lambda e: cond_has(e, "VarSceneTxt", ["Paso", "=", '"equipo"']) and cond_has(e, "CompareTimer", ["", '"paso"']) and act_has(e, "ModVarSceneTxt", ["Paso", "=", '"unirse"']))
esc_or = next(x for x in e158["conditions"] if x["type"]["value"].endswith("Or"))
add_cond(e158, c("VarGlobalTxt", "Modo", "!=", '"jefe"'))
nuevo(ME, ME.index(e158) + 1, std([c("VarSceneTxt", "Paso", "=", '"equipo"'), c("VarGlobalTxt", "Modo", "=", '"jefe"'), copy.deepcopy(next(x for x in e158["conditions"] if x["type"]["value"] == "CompareTimer")), copy.deepcopy(esc_or)],
                                  [a("ModVarSceneTxt", "Paso", "=", '"jefetipo"'), a("ModVarScene", "Sel", "=", "0"), a("ResetTimer", "", '"paso"')]), "ESC-EQUIPO")
TIMER = copy.deepcopy(next(x for x in e158["conditions"] if x["type"]["value"] == "CompareTimer"))

# 2e · aspecto: tarjetas visibles, ilustraciones y textos
for e in ME:
    if not e["type"].endswith("Standard"): continue
    # ocultar tarjetas en otros pasos
    if cond_has(e, "VarSceneTxt", ["Paso", "!=", '"modo"']) and act_has(e, "Cache", ["MarcoModo"]):
        add_cond(e, NOJT)
    # animación de la ilustración
    if cond_has(e, "VarObjet", ["IlusModo", "Idx"]) and any(x["type"]["value"] == "SetAnimationName" for x in e["actions"]) and len(e["conditions"]) == 1:
        add_cond(e, NOJT)
    # textos de las tarjetas
    for cap in ("TxtCapA", "TxtCapB"):
        if cond_has(e, "VarObjet", [cap, "Idx"]) and len(e["conditions"]) == 1 and any(x["type"]["value"] == "TextObject::String" for x in e["actions"]):
            add_cond(e, NOJT)
CAP = {("TxtCapA", 0): ("LOCAL", 560), ("TxtCapB", 0): ("Contra 4 bots (sin internet)", 560), ("TxtCapA", 1): ("EN LÍNEA", 1360), ("TxtCapB", 1): ("Sala con código · 4 jugadores", 1360)}
if not hay_marca(ME, "ASPECTO"):
    nuevo(ME, len(ME), std([PJT], [a("Montre", n, "") for n in ("MarcoModo", "IlusModo", "TxtCapA", "TxtCapB")]), "ASPECTO")
    ME.append(std([PJT, c("VarObjet", "IlusModo", "Idx", "=", "0")], [a("SetAnimationName", "IlusModo", '"l"')]))
    ME.append(std([PJT, c("VarObjet", "IlusModo", "Idx", "=", "1")], [a("SetAnimationName", "IlusModo", '"o"')]))
    for (cap, idx), (txt, cx) in CAP.items():
        ME.append(std([PJT, c("VarObjet", cap, "Idx", "=", str(idx))], [a("TextObject::String", cap, "=", '"%s"' % txt), a("MettreX", cap, "=", "%d - %s.Width() / 2" % (cx, cap))]))
    ME.append(std([PJT], [a("TextObject::String", "TxtMenu", "=", '"MODO JEFE: ¿CÓMO QUIERES JUGAR?"'),
                          a("MettreX", "TxtMenu", "=", "960 - TxtMenu.Width() / 2"),
                          a("TextObject::String", "TxtSubM", "=", '"Local: tú eres el Jefe contra 4 bots. En línea: crea una sala o únete con un código."'),
                          a("MettreX", "TxtSubM", "=", "960 - TxtSubM.Width() / 2"),
                          a("TextObject::String", "TxtSlots", "=", '""'),
                          a("TextObject::String", "TxtPie", "=", '"◄ ► / A D elegir (o 1 / 2) · Enter, F o clic: aceptar · Esc: volver · Mando: cruceta y A"'),
                          a("MettreX", "TxtPie", "=", "960 - TxtPie.Width() / 2")]))
    ME.append(std([c("VarSceneTxt", "Paso", "=", '"equipo"'), c("VarGlobalTxt", "Modo", "=", '"jefe"')],
                  [a("TextObject::String", "TxtSubM", "=", '"Jefe local: elige el personaje de cada uno de los 4 bots (clic, o A/D y F). Esc: volver."'),
                   a("MettreX", "TxtSubM", "=", "960 - TxtSubM.Width() / 2")]))
# (fase25 añadía "3 EN LÍNEA" a cualquier título con "JEFE DE ZOMBIES": se corrige un título ya creado)
for e in ME:
    for x in e.get("actions", []):
        if x["parameters"][:1] == ["TxtMenu"] and "CÓMO QUIERES JUGAR" in x["parameters"][-1]:
            x["parameters"][-1] = '"MODO JEFE: ¿CÓMO QUIERES JUGAR?"'
# fondo de escuela (video) para la pantalla jefetipo
GV = next(e for e in ME if e.get("name") == "Videos")
if not hay_marca(GV["events"], "VBG"):
    GV["events"].insert(1, marca("VBG")); GV["events"].insert(2, std([PJT], [a("ModVarSceneTxt", "VBg", "=", '"modo"')]))
# el grupo Videos oculta IlusModo cada cuadro: aquí se vuelve a mostrar (corre después)
if not hay_marca(ME, "ILUS"):
    nuevo(ME, len(ME), std([PJT], [a("Montre", "IlusModo", "")]), "ILUS")

# 2f · navegación y aceptación
def teclas(*ks): return [c("KeyReleased", "", k) for k in ks]
def pads(*bs): return [c("Gamepads::C_Button_released", "", str(k), '"%s"' % b, "") for b in bs for k in (1, 2, 3, 4)]
nuevo(ME, len(ME), std([PJT, orc(*(teclas("Left", "a", "Up", "w") + pads("Left", "Up")))], [a("ModVarScene", "Sel", "=", "mod(Variable(Sel) + 1, 2)")]), "NAV1")
nuevo(ME, len(ME), std([PJT, orc(*(teclas("Right", "d", "Down", "s") + pads("Right", "Down")))], [a("ModVarScene", "Sel", "=", "mod(Variable(Sel) + 1, 2)")]), "NAV2")
nuevo(ME, len(ME), std([PJT, c("KeyReleased", "", "Num1")], [a("ModVarScene", "Sel", "=", "0")]), "NUM1")
nuevo(ME, len(ME), std([PJT, c("KeyReleased", "", "Num2")], [a("ModVarScene", "Sel", "=", "1")]), "NUM2")
LOCAL = [a("ModVarSceneTxt", "Paso", "=", '"equipo"'), a("ResetTimer", "", '"paso"'), a("ModVarGlobalTxt", "Modo", "=", '"jefe"'), a("ModVarScene", "S1Ctl", "=", "-1"), a("ModVarGlobal", "OnlineJefe", "=", "0")]
ONLINE = [a("ModVarGlobalTxt", "Modo", "=", '"jefe"'), a("ModVarGlobal", "OnlineJefe", "=", "1"), a("Scene", "", '"Online"', "")]
acepta = orc(*(teclas("Return", "Space", "f") + pads("A", "START")))
nuevo(ME, len(ME), std([PJT, copy.deepcopy(TIMER), copy.deepcopy(acepta), c("VarScene", "Sel", "=", "0")], LOCAL), "OK-LOCAL")
nuevo(ME, len(ME), std([PJT, copy.deepcopy(TIMER), copy.deepcopy(acepta), c("VarScene", "Sel", "=", "1"), c("BuiltinCommonInstructions::Once")], ONLINE), "OK-ONLINE")
def clic(x0, x1, acts, clave):
    cds = [PJT, copy.deepcopy(TIMER), c("MouseButtonReleased", "", "Left"),
           c("BuiltinCommonInstructions::CompareNumbers", "MouseX()", ">=", str(x0)), c("BuiltinCommonInstructions::CompareNumbers", "MouseX()", "<", str(x1)),
           c("BuiltinCommonInstructions::CompareNumbers", "MouseY()", ">=", "250"), c("BuiltinCommonInstructions::CompareNumbers", "MouseY()", "<", "790")]
    nuevo(ME, len(ME), std(cds, copy.deepcopy(acts)), clave)
clic(340, 780, LOCAL, "CLIC-LOCAL")
clic(1140, 1580, ONLINE, "CLIC-ONLINE")
nuevo(ME, len(ME), std([PJT, copy.deepcopy(TIMER), copy.deepcopy(esc_or)], [a("ModVarSceneTxt", "Paso", "=", '"modo"'), a("ModVarScene", "Sel", "=", "1"), a("ResetTimer", "", '"paso"')]), "ESC-JEFETIPO")

# =====================================================================
# 3 · ESCENA ONLINE: mismo estilo (fondo de escuela, placa, barra, panel)
# =====================================================================
for nom in ("Placa", "BarraPie"):
    if not any(o["name"] == nom for o in O["objects"]):
        O["objects"].append(copy.deepcopy(vid(M, nom)))
        src = next(i for i in M["instances"] if i["name"] == nom)
        O["instances"].append(instancia(nom, src["x"], src["y"], "", 2, src["width"], src["height"]))
if not any(o["name"] == "PanelOn" for o in O["objects"]):
    O["objects"].append(objeto_sprite("PanelOn", [animacion("p", ["p27_panel_sala"], 1, False, (0, 0))]))
    O["instances"].insert(2, instancia("PanelOn", 110, 290, "", 2, 1700, 640))

# =====================================================================
# 4 · net_core.js (lobby): modo Jefe desde el menú, host secundario, diseño
# =====================================================================
js = open(NET, encoding="utf-8").read()
if "FDIZ-F27" not in js:
    def rep(viejo, nuevo_, cnt=1):
        global js
        assert js.count(viejo) == cnt, (js.count(viejo), viejo[:80])
        js = js.replace(viejo, nuevo_)
    rep('N.L = { m: [{ id: "host", name: "Host (tú)", players: [] }], mode: "escape", dif: "normal" };',
        'N.L = { m: [{ id: "host", name: (N.preJefe ? "JEFE (tú)" : "Host (tú)"), players: [] }], mode: (N.preJefe ? "jefe" : "escape"), dif: "normal" };')
    rep('name: "PC " + (N.L.m.length + 1)', 'name: (N.L.mode === "jefe" ? "Sub-host " + N.L.m.length : "PC " + (N.L.m.length + 1))')
    rep('N.scn = scn; syncRol(scn); const I = im(scn);',
        '/*FDIZ-F27*/ if (!scn._oj) { scn._oj = 1; try { N.preJefe = scn.getGame().getVariables().get("OnlineJefe").getAsNumber() >= 1; } catch (e) { N.preJefe = false; } }\n    N.scn = scn; syncRol(scn); const I = im(scn);')
    rep('T(scn, "JUGAR EN LÍNEA", 960, 40, 64, "255;230;120", "center");',
        'const jf0 = N.role && N.L ? N.L.mode === "jefe" : !!N.preJefe;\n    T(scn, jf0 ? "JEFE DE ZOMBIES · EN LÍNEA" : "JUGAR EN LÍNEA", 960, 74, jf0 ? 44 : 54, "255;230;120", "center");')
    rep('const opts = ["Crear sala (soy el host)", "Unirme a una sala con código"];',
        'const opts = N.preJefe ? ["Crear sala (soy el Jefe)", "Unirme a una sala (host secundario)"] : ["Crear sala (soy el host)", "Unirme a una sala con código"];')
    rep('T(scn, (u.sel === i ? ">> " : "   ") + opts[i], 960, 330 + i * 90, 48,', 'T(scn, (u.sel === i ? ">> " : "   ") + opts[i], 960, 350 + i * 90, 48,')
    rep('T(scn, "En modo Jefe, el host es el Jefe (teclado y ratón) y los sobrevivientes entran desde otras PCs.", 960, 600, 28, "190;210;255", "center", 1500);\n      T(scn, "Hace falta internet. Cada jugador usa su propia copia del juego.", 960, 650, 28, "190;210;255", "center", 1500);',
        'if (N.preJefe) { T(scn, "Crear sala: tú eres el Jefe (teclado y ratón) y esperas a los sobrevivientes.", 960, 580, 28, "190;210;255", "center", 1500);\n        T(scn, "Unirme: tu PC se vuelve host secundario y aloja hasta 4 sobrevivientes (tú con teclado + mandos).", 960, 625, 28, "190;210;255", "center", 1500); }\n      else T(scn, "Cada jugador usa su propia copia del juego, conectada por internet.", 960, 600, 28, "190;210;255", "center", 1500);\n      T(scn, "Hace falta internet. La sala se identifica con un código de 5 letras y números.", 960, 700, 28, "190;210;255", "center", 1500);')
    rep('T(scn, "Escribe el código de la sala", 960, 300, 44, "255;255;255", "center");\n      T(scn, (u.code || "") + "_", 960, 400, 90, "140;255;160", "center");',
        'T(scn, "Escribe el código de la sala", 960, 360, 44, "255;255;255", "center");\n      T(scn, (u.code || "") + "_", 960, 450, 90, "140;255;160", "center");\n      T(scn, "El código aparece arriba, en la sala del host (letras y números).", 960, 600, 28, "190;210;255", "center", 1500);')
    rep('T(scn, u.msg, 960, 420, 48, "255;255;255", "center");', 'T(scn, u.msg, 960, 480, 48, "255;255;255", "center");')
    rep('T(scn, u.msg || "Error", 960, 400, 44, "255;120;120", "center", 1500);', 'T(scn, u.msg || "Error", 960, 450, 44, "255;120;120", "center", 1500);')
    # modo fijado desde el menú del juego
    rep('if (host) { if (I.wasKeyReleased(77) && !N.started) { mut(() => { L.mode = L.mode === "jefe" ? "escape" : "jefe"; if (L.mode === "jefe") mine.players = []; }); }\n      if (I.wasKeyReleased(78))',
        'if (host) { if (I.wasKeyReleased(78))')
    rep('if (host && e(k.IDX.Y)) { mut(() => { L.mode = L.mode === "jefe" ? "escape" : "jefe"; if (L.mode === "jefe") mine.players = []; }); }\n', '')
    rep('(host && L.mode === "jefe") ? "Eres el Jefe: no puedes unirte como sobreviviente. Los sobrevivientes son las otras PCs (pulsa M para pasar a modo Escape)."',
        '(host && L.mode === "jefe") ? "Eres el Jefe: no puedes unirte como sobreviviente. Los sobrevivientes son las otras PCs que se unan con el código."')
    # dibujo del lobby
    ini = js.index("    // dibujo\n")
    fin = js.rindex("  }\n})();")
    nuevo_dibujo = r'''    // dibujo (Fase 27: código de sala arriba, host secundario, panel del juego)
    const jf = L.mode === "jefe";
    T(scn, "CÓDIGO DE LA SALA", 960, 192, 24, "190;210;255", "center");
    T(scn, N.code || "-----", 960, 218, 80, "140;255;160", "center");
    T(scn, host ? "Díselo a las otras PCs: en su menú, EN LÍNEA > Unirme a una sala" : "Estás en la sala " + (N.code || ""), 960, 305, 24, "190;210;255", "center", 1600);
    T(scn, "Modo: " + (jf ? "JEFE DE ZOMBIES" : "ESCAPE") + "   ·   Dificultad: " + L.dif.toUpperCase() + "   ·   Sobrevivientes: " + totalPlayers(L) + "/4", 960, 335, 28, "255;230;120", "center", 1600);
    let y = 385;
    L.m.forEach((m) => {
      const esJefe = jf && m.id === "host";
      const tag = esJefe ? "  —  JEFE (teclado y ratón)" : (jf ? "  —  host secundario (hasta 4 jugadores)" : "");
      T(scn, (m.id === me ? "► " : "") + m.name + tag, 140, y, 30, "190;220;255", "left"); y += 36;
      if (!m.players.length) { T(scn, esJefe ? "(no juega como sobreviviente)" : "(sin jugadores: Enter = teclado, A = mando)", 180, y, 24, "170;170;170", "left"); y += 30; }
      m.players.forEach((p) => {
        const dev = p.ctl === 0 ? "TECLADO" : "MANDO " + p.ctl;
        T(scn, "[" + dev + "]   " + (p.ok ? "" : "◄ ") + (PJN[p.pj] || "?") + (p.ok ? "" : " ►") + "   " + (PJD[p.pj] || "") + (p.ok ? "   ✔ LISTO" : ""), 180, y, 26, p.ok ? "140;255;160" : "255;255;255", "left"); y += 32;
      });
      y += 8;
    });
    const nb = 4 - totalPlayers(L);
    T(scn, nb > 0 ? "Los " + nb + " lugares libres los ocuparán bots." : "Equipo completo.", 960, 884, 24, "190;210;255", "center");
    if (u.msg && Date.now() - (u.msgT || 0) < 5000) T(scn, u.msg, 960, 916, 24, "255;150;150", "center", 1600);
    if (host) {
      T(scn, N.canStart() ? "Todos listos: Enter / Start para EMPEZAR" : (jf && totalPlayers(L) === 0 ? "Esperando a que se una al menos un sobreviviente…" : "Esperando a que todos confirmen (Enter / A)"), 960, 956, 32, N.canStart() ? "140;255;160" : "255;220;140", "center", 1700);
      T(scn, "N dificultad · Mando: X dificultad · Esc salir", 960, 1000, 22, "255;210;190", "center");
    } else T(scn, jf ? "Esperando a que el Jefe inicie la partida…" : "Esperando al host…", 960, 956, 32, "255;220;140", "center");
    if (!host) T(scn, "A/D cambiar personaje · Enter confirmar · Esc salir", 960, 1000, 22, "255;210;190", "center");
'''
    js = js[:ini] + nuevo_dibujo + js[fin:]
    open(NET, "w", encoding="utf-8").write(js)

json.dump(d, open(PRY, "w"), ensure_ascii=False, indent=2)
print("OK fase 27")
