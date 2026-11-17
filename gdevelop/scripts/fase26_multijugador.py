"""Fase 26 · Correcciones de multijugador local, Jefe, pausa/controles, bots y texturas CIC. Idempotente.
Uso: python3 fase26_multijugador.py   (parchea ../FDI-Z/FDI-Z.json, crea respaldo la primera vez)
(No confundir con fase26_correcciones.py, que es un script antiguo de otra numeración.)"""
import json, copy, os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gd_util import c, a, instancia, res_imagen

AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
bak = os.path.join(AQUI, "..", "respaldos", "antes_de_fase26_20261117.json")
if not os.path.exists(bak):
    shutil.copy(PRY, bak)
d = json.load(open(PRY))
J = next(l for l in d["layouts"] if l["name"] == "Juego")
M = next(l for l in d["layouts"] if l["name"] == "Menu")
MK = "FDIZ-FASE26"

def std(conds, acts, sub=()):
    return {"type": "BuiltinCommonInstructions::Standard", "conditions": conds, "actions": acts, "events": list(sub)}
def js(code, marca):
    return {"type": "BuiltinCommonInstructions::JsCode", "inlineCode": "/*" + marca + "*/\n" + code, "parameterObjects": "", "useStrict": True, "eventsSheetExpanded": False}
def orc(*subs):
    return {"type": {"inverted": False, "value": "BuiltinCommonInstructions::Or"}, "parameters": [], "subInstructions": list(subs)}
def grupo(nombre):
    return next(e for e in J["events"] if e.get("name") == nombre)
def tiene(e, texto):
    return texto in json.dumps(e, ensure_ascii=False)
def addvar(lay, nombre, valor):
    if not any(v["name"] == nombre for v in lay["variables"]):
        lay["variables"].append({"name": nombre, "type": "number", "value": valor})
def nuevo(lst, idx, e, clave):
    """inserta e en lst[idx] si no existe ya un evento con la marca clave (comentario previo)"""
    marca = {"type": "BuiltinCommonInstructions::Comment", "color": {"b": 109, "g": 230, "r": 255, "textB": 0, "textG": 0, "textR": 0}, "comment": MK + "-" + clave, "comment2": ""}
    if any(x.get("comment") == MK + "-" + clave for x in lst):
        return False
    lst.insert(idx, marca); lst.insert(idx + 1, e)
    return True
def recorre(lst):
    for e in lst:
        yield e
        yield from recorre(e.get("events", []))

# =====================================================================
# 0 · TEXTURAS CIC (mostrador curvo y puerta restringida electrónica)
# =====================================================================
RES = "mapa/muebles/mapa_extra/cic__mostrador_curvo_h180.png"
if not any(r["name"] == RES for r in d["resources"]["resources"]):
    d["resources"]["resources"].append(res_imagen(RES, "assets/" + RES))
for o in J["objects"]:
    if o["name"] == "Mueble":
        for an in o["animations"]:
            if an["name"] == "extra/cic__mostrador_curvo_h180":
                for dr in an["directions"]:
                    for s in dr["sprites"]:
                        s["image"] = RES
                        s["originPoint"] = {"name": "origine", "x": 132, "y": 180}

# =====================================================================
# 1 · UNIRSE CON CONTROL (bug: el control robaba al primer superviviente)
# =====================================================================
G = grupo("Unirse con control")
ini = [
    std([c("VarGlobal", "NetRol", "!=", "2"), c("DepartScene", "")],
        [a("ModVarScene", "Pad%d" % k, "=", "min(1, " + " + ".join("(1 - sign(abs(GlobalVariable(P%dCtl) - %d)))" % (p, k) for p in (1, 2, 3, 4)) + ")") for k in (1, 2, 3, 4)]),
    std([c("VarGlobal", "NetRol", "!=", "2"), c("DepartScene", ""), c("VarGlobalTxt", "Modo", "=", '"jefe"')],
        [a("ModVarScene", "Pad%d" % k, "=", "1") for k in (1, 2, 3, 4)]),
]
if not any(x.get("comment") == MK + "-PAD" for x in G["events"]):
    G["events"][0:0] = [{"type": "BuiltinCommonInstructions::Comment", "color": {"b": 109, "g": 230, "r": 255, "textB": 0, "textG": 0, "textR": 0}, "comment": MK + "-PAD", "comment2": "Fase 26: los mandos ya asignados en el menú cuentan como ocupados (Pad=1); en modo Jefe nadie se une."}] + ini
for e in recorre(G["events"]):
    if e["type"].endswith("Standard"):
        acts = [(x["type"]["value"], x["parameters"]) for x in e.get("actions", [])]
        if any(t == "ModVarObjet" and p[0] == "Sup" and p[1] == "Control" and p[2] == "=" and p[3] in ("1", "2", "3", "4") for t, p in acts):
            cc = c("VarObjet", "Sup", "Control", "=", "-1")
            if cc not in e["conditions"]:
                e["conditions"].append(cc)   # solo puede tomar un BOT, nunca a un humano
        elif any(x["type"]["value"] == "VarGlobal" and x["parameters"][:3] == ["NetRol", "!=", "2"] for x in e.get("conditions", [])) and any(x["type"]["value"] == "VarScene" and x["parameters"][0] == "Pausa" for x in e["conditions"]) and e.get("events"):
            cc = c("VarGlobalTxt", "Modo", "!=", '"jefe"')
            if cc not in e["conditions"]:
                e["conditions"].append(cc)
# aviso en modo Jefe
pads = [c("Gamepads::C_Button_released", "", str(k), '"A"', "") for k in (1, 2, 3, 4)]
nuevo(G["events"], len(G["events"]),
      std([c("VarGlobal", "NetRol", "!=", "2"), c("VarGlobalTxt", "Modo", "=", '"jefe"'), c("VarScene", "Pausa", "=", "0"), orc(*pads)],
          [a("ModVarSceneTxt", "Banner", "=", '"MODO JEFE: nadie puede unirse a tu partida. Los 4 sobrevivientes son bots."'),
           a("ResetTimer", "", '"banner"'), a("ModVarScene", "BannerSeg", "=", "3.5")]), "AVISOJEFE")

# =====================================================================
# 2 · BOTS: siguen al humano que les toca (round-robin entre humanos vivos)
# =====================================================================
sup = next(o for o in J["objects"] if o["name"] == "Sup")
for n in ("BotX", "BotY"):
    if not any(v["name"] == n for v in sup["variables"]):
        sup["variables"].append({"name": n, "type": "number", "value": 0})
GB = grupo("Bots")
def purga(lst, firma=MK):
    """quita eventos JS con la firma (aunque fase25 los haya envuelto en una compuerta NetRol != 2) y los envoltorios vacíos"""
    for e in list(lst):
        if e["type"].endswith("JsCode") and firma in e["inlineCode"]:
            lst.remove(e); continue
        if e.get("events"):
            purga(e["events"], firma)
            if e["type"].endswith("Standard") and not e["events"] and not e.get("actions") and [x["parameters"] for x in e["conditions"]] == [["NetRol", "!=", "2"]]:
                lst.remove(e)
purga(GB["events"])
# 3b · sin colisiones entre supervivientes/bots: se elimina el empuje mutuo (scripts/separar_supervivientes.js)
purga(J["events"], "Los pies conservan su máscara del mapa")
JSBOT = r"""
const scn = runtimeScene;
if (scn.getGame().getVariables().get("NetRol").getAsNumber() === 2) return;
const sups = scn.getObjects("Sup") || [];
const sv = scn.getVariables();
const sx = sv.get("SegX").getAsNumber(), sy = sv.get("SegY").getAsNumber();
const humanos = [];
for (const o of sups) {
  const v = o.getVariables();
  let ctl = v.get("Control").getAsNumber();
  if (ctl === -2 && v.has("CtlReal")) ctl = v.get("CtlReal").getAsNumber();
  if (ctl >= 0 || ctl === -3) humanos.push(o);
}
let pool = humanos.filter((o) => o.getVariables().get("Estado").getAsString() === "normal");
if (!pool.length) pool = humanos;
pool.sort((p, q) => p.getVariables().get("Jugador").getAsNumber() - q.getVariables().get("Jugador").getAsNumber());
const bots = sups.filter((o) => o.getVariables().get("Control").getAsNumber() === -1);
bots.sort((p, q) => p.getVariables().get("Jugador").getAsNumber() - q.getVariables().get("Jugador").getAsNumber());
bots.forEach((b, i) => {
  let tx = sx, ty = sy;
  if (pool.length) {
    // reparte los bots entre los humanos; si el que le toca está lejísimos, sigue al más cercano
    let h = pool[i % pool.length];
    tx = h.getX(); ty = h.getY();
  }
  const bv = b.getVariables();
  bv.get("BotX").setNumber(tx);
  bv.get("BotY").setNumber(ty);
});
"""
GB["events"].insert(1, js(JSBOT, MK + "-BOTS"))
for e in recorre(GB["events"]):
    for lista in (e.get("conditions", []), e.get("actions", [])):
        for x in lista:
            x["parameters"] = [p.replace("Variable(SegX)", "Sup.Variable(BotX)").replace("Variable(SegY)", "Sup.Variable(BotY)") if isinstance(p, str) else p for p in x["parameters"]]

# =====================================================================
# 3 · RECOGER OBJETOS CLAVE: cualquier superviviente (por cercanía además de colisión)
# =====================================================================
GO = grupo("Objetivos y flecha")
for nom in ("Bidon", "Bolsa"):
    orig = next((e for e in GO["events"] if e["type"].endswith("Standard") and any(x["type"]["value"] == "CollisionNP" and x["parameters"][:2] == ["Sup", nom] for x in e["conditions"])), None)
    if orig and not any(e["type"].endswith("Standard") and any(x["type"]["value"] == "Distance" and x["parameters"][:2] == ["Sup", nom] for x in e["conditions"]) for e in GO["events"]):
        cp = copy.deepcopy(orig)
        cp["conditions"] = [c("Distance", "Sup", nom, "70") if x["type"]["value"] == "CollisionNP" else x for x in cp["conditions"]]
        GO["events"].insert(GO["events"].index(orig) + 1, cp)

# =====================================================================
# 4 · PAUSA: botón CONTROLES + pantalla de controles
# =====================================================================
addvar(J, "PausaVista", 0)
HUD = "HUD"
b2 = next(o for o in J["objects"] if o["name"] == "TxtPausaB2")
for n in ("TxtPausaB3", "TxtPausaCtl1", "TxtPausaCtl2"):
    if not any(o["name"] == n for o in J["objects"]):
        o = copy.deepcopy(b2); o["name"] = n
        if n.startswith("TxtPausaCtl"):
            o["characterSize"] = 30; o["textAlignment"] = "left"
            o["content"]["characterSize"] = 30; o["content"]["textAlignment"] = "left"
        J["objects"].append(o)
        J["instances"].append(instancia(n, 960, 500, HUD, 90004))
btn = [i for i in J["instances"] if i["name"] == "PausaBtn"]
if len(btn) == 3:
    nuevo4 = copy.deepcopy(btn[2]); nuevo4["persistentUuid"] = __import__("uuid").uuid4().hex[:8] + "-0000-4000-8000-000000000026"
    nuevo4["initialVariables"] = [{"name": "Idx", "type": "number", "value": 3}]
    J["instances"].append(nuevo4); btn.append(nuevo4)
for i in btn:
    idx = int(next(v["value"] for v in i["initialVariables"] if v["name"] == "Idx"))
    i["y"] = 320 + 115 * idx; i["height"] = 95

GP = grupo("Menú de pausa")
NR0 = c("VarGlobal", "NetRol", "=", "0")
V0 = c("VarScene", "PausaVista", "=", "0")
def ya(e, cc): return cc in e["conditions"]
def gate(e, cc):
    if not ya(e, cc): e["conditions"].append(cc)
for e in GP["events"]:
    if not e["type"].endswith("Standard"):
        continue
    acts = [(x["type"]["value"], x["parameters"]) for x in e.get("actions", [])]
    conds = e["conditions"]
    # DepartScene: inicializa vista
    if any(x["type"]["value"] == "DepartScene" for x in conds) and not any(p[:1] == ["PausaVista"] for t, p in acts):
        e["actions"].append(a("ModVarScene", "PausaVista", "=", "0"))
    # Pausa = 0: ocultar todo
    if any(x["type"]["value"] == "VarScene" and x["parameters"] == ["Pausa", "=", "0"] for x in conds) and any(t == "Cache" and p[0] == "PausaVelo" for t, p in acts):
        for n in ("TxtPausaB3", "TxtPausaCtl1", "TxtPausaCtl2"):
            if not any(t == "Cache" and p[0] == n for t, p in acts): e["actions"].append(a("Cache", n, ""))
        if not any(p[:1] == ["PausaVista"] for t, p in acts): e["actions"].append(a("ModVarScene", "PausaVista", "=", "0"))
    # navegación arriba/abajo con 4 botones
    for x in e.get("actions", []):
        if x["type"]["value"] == "ModVarScene" and x["parameters"][0] == "PausaSel":
            x["parameters"][2] = x["parameters"][2].replace("+ 2, 3)", "+ 3, 4)").replace("+ 1, 3)", "+ 1, 4)")
    if any(t == "ModVarScene" and p[0] in ("PausaSel", "PausaGo") and p[1] == "=" and p[2] in ("0", "1", "2", "3") and len(p) == 3 for t, p in acts) and any(x["type"]["value"] in ("Gamepads::C_Button_released", "BuiltinCommonInstructions::Or", "MouseButtonReleased") for x in conds):
        gate(e, V0)
    if any(t == "ModVarScene" and p[0] == "PausaSel" and "mod(" in p[2] for t, p in acts):
        gate(e, V0)
# reconstruye el evento "mostrar pausa" y los 3 clics -> 4 clics, y las acciones de PausaGo
i_show = next(i for i, e in enumerate(GP["events"]) if e["type"].endswith("Standard") and any(x["type"]["value"] == "Montre" and x["parameters"][0] == "PausaVelo" for x in e["actions"]))
show = GP["events"][i_show]
if not any(x["parameters"][:1] == ["TxtPausaB3"] for x in show["actions"]):
    acts = [a("Montre", n, "") for n in ("PausaVelo", "PausaPanel", "PausaBtn", "TxtPausaTit", "TxtPausaB0", "TxtPausaB1", "TxtPausaB2", "TxtPausaB3")]
    acts += [a("Cache", "TxtPausaCtl1", ""), a("Cache", "TxtPausaCtl2", ""), a("Opacity", "PausaVelo", "=", "150")]
    for n, t in (("Tit", "PAUSA"), ("B0", "CONTINUAR"), ("B1", "CONTROLES"), ("B2", "REINICIAR"), ("B3", "MENÚ")):
        acts.append(a("TextObject::String", "TxtPausa" + n, "=", '"%s"' % t))
    acts += [a("MettreX", "TxtPausaTit", "=", "960 - TxtPausaTit.Width() / 2"), a("MettreY", "TxtPausaTit", "=", "262 - TxtPausaTit.Height() / 2")]
    for k in range(4):
        n = "TxtPausaB%d" % k
        acts += [a("MettreX", n, "=", "960 - %s.Width() / 2" % n), a("MettreY", n, "=", "%d - %s.Height() / 2" % (367 + 115 * k, n))]
    show["actions"] = acts
    gate(show, V0)
# vista de controles
CTL1 = ("TECLADO Y RATÓN\n\nW A S D ........ moverse\nRatón .......... apuntar\nClic izquierdo . golpear / disparar\nClic derecho o R  lanzar objeto\nF (mantener) ... usar: puertas, cofres,\n                 máquinas\nQ .............. habilidad\nE .............. especial\nShift izq. ..... correr\nEsc o P ........ pausa")
CTL2 = ("MANDO\n\nStick izquierdo . moverse\nStick derecho .. apuntar\nX .............. golpear / disparar\nB .............. lanzar objeto\nA (mantener) ... usar: puertas, cofres,\n                 máquinas\nY .............. habilidad\nRB ............. especial\nStart .......... pausa")
def lit(t): return '"' + t.replace("\n", '" + NewLine() + "') + '"'
vista = std([NR0, c("VarScene", "Pausa", "=", "1"), c("VarScene", "PausaVista", ">=", "1")],
            [a("Montre", "PausaVelo", ""), a("Opacity", "PausaVelo", "=", "238"), a("Cache", "PausaPanel", ""), a("Cache", "PausaBtn", ""),
             a("Cache", "TxtPausaB1", ""), a("Cache", "TxtPausaB2", ""), a("Cache", "TxtPausaB3", ""),
             a("Montre", "TxtPausaTit", ""), a("Montre", "TxtPausaB0", ""), a("Montre", "TxtPausaCtl1", ""), a("Montre", "TxtPausaCtl2", ""),
             a("TextObject::String", "TxtPausaTit", "=", '"CONTROLES"'), a("TextObject::String", "TxtPausaCtl1", "=", lit(CTL1)), a("TextObject::String", "TxtPausaCtl2", "=", lit(CTL2)),
             a("TextObject::String", "TxtPausaB0", "=", '"Enter, clic o A: volver"'),
             a("MettreX", "TxtPausaTit", "=", "960 - TxtPausaTit.Width() / 2"), a("MettreY", "TxtPausaTit", "=", "110 - TxtPausaTit.Height() / 2"),
             a("MettreX", "TxtPausaCtl1", "=", "150"), a("MettreY", "TxtPausaCtl1", "=", "220"),
             a("MettreX", "TxtPausaCtl2", "=", "1050"), a("MettreY", "TxtPausaCtl2", "=", "220"),
             a("MettreX", "TxtPausaB0", "=", "960 - TxtPausaB0.Width() / 2"), a("MettreY", "TxtPausaB0", "=", "930")])
nuevo(GP["events"], i_show + 1, vista, "VISTA")
# cuatro botones con el mouse
mouse = [e for e in GP["events"] if e["type"].endswith("Standard") and any(x["type"]["value"] == "MouseButtonReleased" for x in e["conditions"]) and any(x["parameters"][:1] == ["PausaSel"] for x in e["actions"])]
if len(mouse) == 3:
    plantilla = mouse[0]
    pos = GP["events"].index(mouse[2]) + 1
    for k in range(4):
        cp = copy.deepcopy(plantilla)
        for x in cp["conditions"]:
            if x["type"]["value"] == "BuiltinCommonInstructions::CompareNumbers" and x["parameters"][0] == 'MouseY("HUD", 0)':
                x["parameters"][2] = str(320 + 115 * k if x["parameters"][1] == ">=" else 415 + 115 * k)
        for x in cp["actions"]:
            if x["parameters"][0] == "PausaSel": x["parameters"][2] = str(k)
        gate(cp, V0)
        GP["events"].insert(pos + k, cp)
    for e in mouse: GP["events"].remove(e)
# acciones al aceptar: 0 continuar, 1 controles, 2 reiniciar, 3 menú
go = [e for e in GP["events"] if e["type"].endswith("Standard") and any(x["parameters"] == ["PausaGo", "=", "1"] for x in e["conditions"] if x["type"]["value"] == "VarScene") and any(x["parameters"][:2] == ["PausaSel", "="] for x in e["conditions"] if x["type"]["value"] == "VarScene")]
if len(go) == 3 and not any(tiene(e, "PausaVista") for e in go):
    go[2]["conditions"] = [c("VarScene", "PausaGo", "=", "1"), c("VarScene", "PausaSel", "=", "3")] if False else go[2]["conditions"]
    for x in go[2]["conditions"]:
        if x["parameters"][:2] == ["PausaSel", "="]: x["parameters"][2] = "3"
    for x in go[1]["conditions"]:
        if x["parameters"][:2] == ["PausaSel", "="]: x["parameters"][2] = "2"
    ctlgo = std([NR0, c("VarScene", "PausaGo", "=", "1"), c("VarScene", "PausaSel", "=", "1")], [a("ModVarScene", "PausaVista", "=", "1")])
    GP["events"].insert(GP["events"].index(go[0]) + 1, ctlgo)
# volver de la vista (se arma un cuadro después para no cerrarla con la misma pulsación que la abre)
if not any(e.get("comment") == MK + "-VOLVER" for e in GP["events"]):
    volver = std([NR0, c("VarScene", "Pausa", "=", "1"), c("VarScene", "PausaVista", "=", "2"),
                  orc(c("KeyReleased", "", "Return"), c("KeyReleased", "", "Space"), c("MouseButtonReleased", "", "Left"),
                      *[c("Gamepads::C_Button_released", "", str(k), '"A"', "") for k in (1, 2, 3, 4)], *[c("Gamepads::C_Button_released", "", str(k), '"B"', "") for k in (1, 2, 3, 4)])],
                 [a("ModVarScene", "PausaVista", "=", "0")])
    armar = std([NR0, c("VarScene", "Pausa", "=", "1"), c("VarScene", "PausaVista", "=", "1")], [a("ModVarScene", "PausaVista", "=", "2")])
    fin = len(GP["events"]) - 1   # el último evento reinicia PausaGo
    GP["events"].insert(fin, {"type": "BuiltinCommonInstructions::Comment", "color": {"b": 109, "g": 230, "r": 255, "textB": 0, "textG": 0, "textR": 0}, "comment": MK + "-VOLVER", "comment2": ""})
    GP["events"].insert(fin + 1, volver); GP["events"].insert(fin + 2, armar)

# =====================================================================
# 5 · MENÚ: modos con 3 opciones, selección por turnos, aviso del Jefe
# =====================================================================
for n, v in (("Turno", 5), ("TurnoPrev", 5), ("AvisoJefe", 0)):
    addvar(M, n, v)
ME = M["events"]
# 5a · lista de modos con la opción 3 seleccionable
for e in ME:
    for x in e.get("actions", []):
        if x["type"]["value"].endswith("String") and x["parameters"][0] == "TxtMenu" and "EN LÍNEA" in x["parameters"][-1] and "VariableString(M2)" not in x["parameters"][-1]:
            x["parameters"][-1] = x["parameters"][-1].replace('"3  EN LÍNEA (internet)"', 'VariableString(M2) + "3  EN LÍNEA (internet)"')
i7 = next((i for i, e in enumerate(ME) if e["type"].endswith("Standard") and any(x["parameters"] == ["Sel", "=", "1 - Variable(Sel)"] for x in e.get("actions", [])) and any(x["parameters"] == ["Paso", "=", '"modo"'] for x in e["conditions"] if x["type"]["value"] == "VarSceneTxt")), None)
if i7 is not None:
    e7 = ME[i7]
    orx = next(x for x in e7["conditions"] if x["type"]["value"].endswith("Or"))
    arriba = [x for x in orx["subInstructions"] if x["parameters"][-1 if x["type"]["value"] == "KeyReleased" else 2].strip('"').lower() in ("up", "w")]
    abajo = [x for x in orx["subInstructions"] if x not in arriba]
    base = [x for x in e7["conditions"] if x is not orx]
    ME[i7] = std(base + [orc(*arriba)], [a("ModVarScene", "Sel", "=", "mod(Variable(Sel) + 2, 3)")])
    ME.insert(i7 + 1, std(copy.deepcopy(base) + [orc(*copy.deepcopy(abajo))], [a("ModVarScene", "Sel", "=", "mod(Variable(Sel) + 1, 3)")]))
i10 = next(i for i, e in enumerate(ME) if e["type"].endswith("Standard") and any(x["parameters"] == ["Paso", "=", '"modo"'] for x in e["conditions"] if x["type"]["value"] == "VarSceneTxt") and any(x["parameters"] == ["Paso", "=", '"unirse"'] for x in e.get("actions", []) if x["type"]["value"] == "ModVarSceneTxt"))
if not any(x["parameters"] == ["Sel", "!=", "2"] for x in ME[i10]["conditions"] if x["type"]["value"] == "VarScene"):
    online = std(copy.deepcopy(ME[i10]["conditions"]) + [c("VarScene", "Sel", "=", "2")], [a("Scene", "", '"Online"', "")])
    ME[i10]["conditions"].append(c("VarScene", "Sel", "!=", "2"))
    ME.insert(i10 + 1, online)
# 5b · selección por turnos
i71 = next(i for i, e in enumerate(ME) if e["type"].endswith("Standard") and any(x["type"]["value"].endswith("String") and x["parameters"][0] == "TxtMenu" and "ELIGEN SU PERSONAJE" in x["parameters"][-1] for x in e.get("actions", [])) and any(x["parameters"][0] == "TxtSlots" for x in e["actions"]))
PEQ = c("VarSceneTxt", "Paso", "=", '"equipo"')
turno = [std([PEQ], [a("ModVarScene", "Turno", "=", "5")])] + [std([PEQ, c("VarScene", "S%dCtl" % k, "!=", "-1"), c("VarScene", "S%dOk" % k, "=", "0")], [a("ModVarScene", "Turno", "=", str(k))]) for k in (4, 3, 2, 1)]
humanos2 = c("BuiltinCommonInstructions::CompareNumbers", "sign(Variable(S2Ctl) + 1) + sign(Variable(S3Ctl) + 1) + sign(Variable(S4Ctl) + 1)", ">=", "1")
turno.append(std([PEQ, c("VarScene", "Turno", "=", "5"), c("VarScene", "TurnoPrev", "<", "5"), c("CompareTimer", "", '"paso"', ">=", "0.3"), humanos2],
                 [a("ModVarSceneTxt", "Paso", "=", '"dificultad"'), a("ResetTimer", "", '"paso"'), a("ModVarScene", "Sel", "=", "1")]))
nuevo(ME, i71 + 1, turno[0], "TURNO0")
pos = next(i for i, e in enumerate(ME) if e.get("comment") == MK + "-TURNO0") + 2
for k, t in enumerate(turno[1:]):
    if not any(e.get("comment") == MK + "-TURNO%d" % (k + 1) for e in ME):
        ME.insert(pos, {"type": "BuiltinCommonInstructions::Comment", "color": {"b": 109, "g": 230, "r": 255, "textB": 0, "textG": 0, "textR": 0}, "comment": MK + "-TURNO%d" % (k + 1), "comment2": ""})
        ME.insert(pos + 1, t); pos += 2
# compuertas por turno en los eventos de entrada de cada ranura
for e in ME:
    if not e["type"].endswith("Standard") or not any(x["parameters"] == ["Paso", "=", '"equipo"'] for x in e["conditions"] if x["type"]["value"] == "VarSceneTxt"):
        continue
    for k in (1, 2, 3, 4):
        if any(x["type"]["value"] == "VarScene" and x["parameters"][0] == "S%dCtl" % k and x["parameters"][1] == "=" and x["parameters"][2] in ("0", "1", "2", "3", "4") for x in e["conditions"]) \
           and any(x["type"]["value"] == "ModVarScene" and x["parameters"][0] in ("S%dPj" % k, "S%dOk" % k) for x in e["actions"]):
            cc = c("VarScene", "Turno", "=", str(k))
            if cc not in e["conditions"]: e["conditions"].append(cc)
    # seguir (Enter/Start): solo cuando todos los humanos terminaron
    if any(x["type"]["value"] == "CompareTimer" for x in e["conditions"]) and any(x["parameters"][:2] == ["Paso", "="] and x["parameters"][2] == '"dificultad"' for x in e["actions"] if x["type"]["value"] == "ModVarSceneTxt") and not any(x["parameters"][:1] == ["Turno"] for x in e["conditions"]):
        e["conditions"].append(c("VarScene", "Turno", "=", "5"))
# mensajes de espera y foco = turno
CX = {1: 300, 2: 740, 3: 1180, 4: 1620}
for k in (1, 2, 3, 4):
    iL = next(i for i, e in enumerate(ME) if e["type"].endswith("Standard") and any(x["parameters"] == ["TxtListo", "Slot", "=", str(k)] for x in e["conditions"] if x["type"]["value"] == "VarObjet") and any(x["type"]["value"].endswith("Or") for x in e["conditions"]))
    nuevo(ME, iL + 1, std([c("VarObjet", "TxtListo", "Slot", "=", str(k)), PEQ, c("VarScene", "S%dCtl" % k, "!=", "-1"), c("VarScene", "S%dOk" % k, "=", "0"), c("VarScene", "Turno", "!=", str(k))],
                          [a("TextObject::String", "TxtListo", "=", '"ESPERANDO TURNO…"'), a("MettreX", "TxtListo", "=", "%d - TxtListo.Width() / 2" % CX[k])]), "ESPERA%d" % k)
    iF = next(i for i, e in enumerate(ME) if e["type"].endswith("Standard") and any(x["parameters"] == ["TxtFlechas", "Slot", "=", str(k)] for x in e["conditions"] if x["type"]["value"] == "VarObjet") and any(x["parameters"][-1] == '"<     >"' for x in e["actions"]))
    nuevo(ME, iF + 1, std([c("VarObjet", "TxtFlechas", "Slot", "=", str(k)), PEQ, c("VarScene", "Turno", "!=", str(k))], [a("TextObject::String", "TxtFlechas", "=", '""')]), "FLECHAS%d" % k)
iKF = next(i for i, e in enumerate(ME) if e["type"].endswith("Standard") and any(x["parameters"] == ["Foco", "=", "1"] for x in e["conditions"] if x["type"]["value"] == "VarScene") and any(x["parameters"][0] == "KF" for x in e["actions"]))
nuevo(ME, iKF, std([PEQ, c("VarScene", "Turno", "<", "5")], [a("ModVarScene", "Foco", "=", "Variable(Turno)")]), "FOCO")
for e in ME:
    if e["type"].endswith("Standard") and any(x["type"]["value"].endswith("String") and x["parameters"][0] == "TxtPie" and "Clic: elegir" in x["parameters"][-1] for x in e["actions"]):
        for x in e["actions"]:
            if x["parameters"][0] == "TxtPie" and "Turnos" not in x["parameters"][-1]:
                x["parameters"][-1] = '"Eligen por turnos: P1, luego P2… · Clic: elegir para los bots · Teclado: A/D mover, F aceptar · Mando: ◄ ► y A · Enter: seguir · Esc: volver"'
# fin de cuadro: recuerda el turno (para avanzar solo al terminar el último humano)
nuevo(ME, len(ME), std([PEQ], [a("ModVarScene", "TurnoPrev", "=", "Variable(Turno)")]), "TURNOPREV")
# 5c · aviso en el menú cuando alguien pulsa A en modo Jefe
nuevo(ME, len(ME), std([c("VarSceneTxt", "Paso", "=", '"unirse"'), c("VarGlobalTxt", "Modo", "=", '"jefe"'), orc(*[c("Gamepads::C_Button_released", "", str(k), '"A"', "") for k in (1, 2, 3, 4)])], [a("ModVarScene", "AvisoJefe", "=", "1")]), "AVISO1")
nuevo(ME, len(ME), std([c("VarSceneTxt", "Paso", "!=", '"unirse"')], [a("ModVarScene", "AvisoJefe", "=", "0")]), "AVISO2")
nuevo(ME, len(ME), std([c("VarSceneTxt", "Paso", "=", '"unirse"'), c("VarGlobalTxt", "Modo", "=", '"jefe"'), c("VarScene", "AvisoJefe", "=", "1")],
                       [a("TextObject::String", "TxtSubM", "=", '"NO PUEDES UNIRTE: en modo Jefe los 4 sobrevivientes son bots. Para jugar con otras personas, usa 3 EN LÍNEA (sala por código)."')]), "AVISO3")

json.dump(d, open(PRY, "w"), ensure_ascii=False, indent=2)
print("OK fase 26")
