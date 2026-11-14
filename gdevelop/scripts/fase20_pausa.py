"""Fase 20 de FDI-Z (13 nov 2026): menu de pausa en la escena Juego. Se aplica SOBRE el FDI-Z.json actual, es idempotente.
    python fase20_pausa.py <FDI-Z.json>

- Esc o P pausa / reanuda (solo mientras Estado = "juego", o sea no durante la cinematica ni en la pantalla final).
- Al pausar: ChangeTimeScale 0 (congela movimiento, animaciones, temporizadores y zombis) y se muestra un velo gris
  semitransparente sobre toda la pantalla con un panel: CONTINUAR / REINICIAR / MENU.
- Seleccion: W/S o flechas + Enter/Espacio, o clic. Esc o el boton CONTINUAR reanudan.
- Los grupos de eventos de entrada (pegar, habilidades, lanzar, usar...) se envuelven en una condicion Pausa = 0 para que
  no se pueda atacar ni usar nada con el juego en pausa.
"""
import copy, json, os, sys, uuid
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gd_util import c, a, ev, res_imagen, animacion

ruta = sys.argv[1]
RAIZ = os.path.dirname(os.path.abspath(ruta))
p = json.load(open(ruta, encoding="utf-8"))
J = next(l for l in p["layouts"] if l["name"] == "Juego")
RES = {r["name"]: r for r in p["resources"]["resources"]}
def add_res(n, f):
    if n in RES: RES[n]["file"] = f
    else:
        r = res_imagen(n, f); p["resources"]["resources"].append(r); RES[n] = r
def obj(n): return next((o for o in J["objects"] if o["name"] == n), None)
def cmp(e1, op, e2): return c("BuiltinCommonInstructions::CompareNumbers", e1, op, e2)
def quitar_tag(evs, tag):
    for e in list(evs):
        if e.get(tag): evs.remove(e)
        else: quitar_tag(e.get("events", []), tag)

# ---------- imagen del velo (gris azulado liso) ----------
Image.new("RGBA", (8, 8), (62, 68, 80, 255)).save(os.path.join(RAIZ, "assets/interfaz/p20_velo_pausa.png"))
add_res("p20_velo_pausa", "assets/interfaz/p20_velo_pausa.png")
add_res("p20_panel_pausa", "assets/interfaz/ui_panel_pausa.png")
add_res("p19_BtnRei", "assets/interfaz/ui_boton_normal_dificultad_p19.png")
add_res("p19_BtnMenu", "assets/interfaz/ui_boton_facil_p19.png")

# ---------- objetos ----------
def spr(nombre, anims):
    return {"adaptCollisionMaskAutomatically": False, "assetStoreId": "", "name": nombre, "type": "Sprite", "updateIfNotVisible": False,
            "variables": [], "effects": [], "behaviors": [], "animations": anims}
def txt(nombre, tam):
    t = copy.deepcopy(obj("TxtAyuda")); t["name"] = nombre; t["characterSize"] = tam
    t["content"]["characterSize"] = tam; t["content"]["isOutlineEnabled"] = True; t["content"]["outlineThickness"] = 5
    t["content"]["outlineColor"] = "20;16;40"; t["color"] = {"b": 200, "g": 240, "r": 255}; t["content"]["color"] = "255;240;200"
    t["content"]["text"] = ""; t["string"] = ""; t["textAlignment"] = "center"; t["content"]["textAlignment"] = "center"
    return t
NUEVOS = {
    "PausaVelo": lambda: spr("PausaVelo", [animacion("v", ["p20_velo_pausa"], 1, False, (0, 0))]),
    "PausaPanel": lambda: spr("PausaPanel", [animacion("p", ["p20_panel_pausa"], 1, False, (0, 0))]),
    "PausaBtn": lambda: spr("PausaBtn", [animacion("n", ["p19_BtnMenu"], 1, False, (0, 0)), animacion("s", ["p19_BtnRei"], 1, False, (0, 0))]),
    "TxtPausaTit": lambda: txt("TxtPausaTit", 44),
    "TxtPausaB0": lambda: txt("TxtPausaB0", 34),
    "TxtPausaB1": lambda: txt("TxtPausaB1", 34),
    "TxtPausaB2": lambda: txt("TxtPausaB2", 34),
}
for n, mk in NUEVOS.items():
    if not obj(n): J["objects"].append(mk())
btn = obj("PausaBtn")
if not any(v["name"] == "Idx" for v in btn["variables"]):
    btn["variables"].append({"name": "Idx", "type": "number", "value": 0})

# geometria (capa HUD, 1920x1080)
PX, PY, PW, PH = 754, 190, 412, 672
BW, BH, BX = 300, 105, 810
BYS = (340, 490, 640)
def inst(nombre, x, y, w=None, h=None, z=0, idx=None):
    i = {"angle": 0, "customSize": w is not None, "height": h or 0, "layer": "HUD", "name": nombre,
         "persistentUuid": str(uuid.uuid4()), "width": w or 0, "x": x, "y": y, "zOrder": z,
         "numberProperties": [], "stringProperties": [], "initialVariables": []}
    if idx is not None: i["initialVariables"] = [{"name": "Idx", "value": idx}]
    return i
NOMBRES = ("PausaVelo", "PausaPanel", "PausaBtn", "TxtPausaTit", "TxtPausaB0", "TxtPausaB1", "TxtPausaB2")
J["instances"] = [i for i in J["instances"] if i["name"] not in NOMBRES]
J["instances"] += [inst("PausaVelo", 0, 0, 1920, 1080, 90000), inst("PausaPanel", PX, PY, PW, PH, 90001)]
for k in range(3):
    J["instances"].append(inst("PausaBtn", BX, BYS[k], BW, BH, 90002, idx=k))
for n in ("TxtPausaTit", "TxtPausaB0", "TxtPausaB1", "TxtPausaB2"):
    J["instances"].append(inst(n, 960, 500, z=90003))

# ---------- envolver los grupos de entrada en Pausa = 0 ----------
GATE = ["Unirse con control", "Entrada (teclado y controles)", "Combate: pegar", "Armas del salón", "Habilidades, especiales y pasivas",
        "Lanzables", "Puertas: tipos y golpes", "Lockers, mochilas, máquinas y dinero", "Compañeros mordidos: salvar o no salvar",
        "Inventario en el panel", "Modo presentación (F1)", "Director automático"]
n_gate = 0
for g in J["events"]:
    if g.get("type", "").endswith("Group") and g.get("name") in GATE:
        if len(g["events"]) == 1 and g["events"][0].get("fdiz20wrap"):
            continue
        w = ev([c("VarScene", "Pausa", "=", "0")], [], sub=g["events"]); w["fdiz20wrap"] = True
        g["events"] = [w]; n_gate += 1
print("grupos protegidos durante la pausa:", n_gate)

# ---------- grupo de eventos de la pausa ----------
quitar_tag(J["events"], "fdiz20")
VIS = ["PausaVelo", "PausaPanel", "PausaBtn", "TxtPausaTit", "TxtPausaB0", "TxtPausaB1", "TxtPausaB2"]
def dentro(k):
    return [cmp('MouseX("HUD", 0)', ">=", str(BX)), cmp('MouseX("HUD", 0)', "<=", str(BX + BW)),
            cmp('MouseY("HUD", 0)', ">=", str(BYS[k])), cmp('MouseY("HUD", 0)', "<=", str(BYS[k] + BH))]
E = []
E.append(ev([c("DepartScene", "")], [a("ModVarScene", "Pausa", "=", "0"), a("ModVarScene", "PausaSel", "=", "0"),
                                    a("ModVarScene", "PausaCambio", "=", "0"), a("ModVarScene", "PausaGo", "=", "0"),
                                    a("ChangeTimeScale", "", "1")]))
# tecla Esc / P
E.append(ev([c("VarSceneTxt", "Estado", "=", '"juego"'),
             {"type": {"value": "BuiltinCommonInstructions::Or"}, "parameters": [],
              "subInstructions": [c("KeyReleased", "", "Escape"), c("KeyReleased", "", "p")]}],
            [a("ModVarScene", "PausaCambio", "=", "1")]))
E.append(ev([c("VarScene", "PausaCambio", "=", "1"), c("VarScene", "Pausa", "=", "0")], [a("ModVarScene", "PausaNueva", "=", "1")]))
E.append(ev([c("VarScene", "PausaCambio", "=", "1"), c("VarScene", "Pausa", "=", "1")], [a("ModVarScene", "PausaNueva", "=", "0")]))
E.append(ev([c("VarScene", "PausaCambio", "=", "1")],
            [a("ModVarScene", "Pausa", "=", "Variable(PausaNueva)"), a("ModVarScene", "PausaCambio", "=", "0"),
             a("ModVarScene", "PausaSel", "=", "0"), a("ChangeTimeScale", "", "1 - Variable(PausaNueva)")]))
# visibilidad
E.append(ev([c("VarScene", "Pausa", "=", "0")], [a("Cache", o) for o in VIS]))
E.append(ev([c("VarScene", "Pausa", "=", "1")],
            [a("Montre", o, "") for o in VIS] + [a("Opacity", "PausaVelo", "=", "150"),
             a("TextObject::String", "TxtPausaTit", "=", '"PAUSA"'),
             a("TextObject::String", "TxtPausaB0", "=", '"CONTINUAR"'),
             a("TextObject::String", "TxtPausaB1", "=", '"REINICIAR"'),
             a("TextObject::String", "TxtPausaB2", "=", '"MENÚ"'),
             a("MettreX", "TxtPausaTit", "=", "960 - TxtPausaTit.Width() / 2"), a("MettreY", "TxtPausaTit", "=", "%d - TxtPausaTit.Height() / 2" % (PY + 77))] +
            [x for k in range(3) for x in (a("MettreX", "TxtPausaB%d" % k, "=", "960 - TxtPausaB%d.Width() / 2" % k),
                                          a("MettreY", "TxtPausaB%d" % k, "=", "%d - TxtPausaB%d.Height() / 2" % (BYS[k] + BH // 2, k)))]))
# resaltado del boton elegido
E.append(ev([c("VarScene", "Pausa", "=", "1"), c("VarObjet", "PausaBtn", "Idx", "=", "Variable(PausaSel)")], [a("SetAnimationName", "PausaBtn", '"s"')]))
E.append(ev([c("VarScene", "Pausa", "=", "1"), c("VarObjet", "PausaBtn", "Idx", "!=", "Variable(PausaSel)")], [a("SetAnimationName", "PausaBtn", '"n"')]))
# teclado: arriba / abajo
E.append(ev([c("VarScene", "Pausa", "=", "1"), {"type": {"value": "BuiltinCommonInstructions::Or"}, "parameters": [],
             "subInstructions": [c("KeyReleased", "", "w"), c("KeyReleased", "", "Up")]}],
            [a("ModVarScene", "PausaSel", "=", "mod(Variable(PausaSel) + 2, 3)")]))
E.append(ev([c("VarScene", "Pausa", "=", "1"), {"type": {"value": "BuiltinCommonInstructions::Or"}, "parameters": [],
             "subInstructions": [c("KeyReleased", "", "s"), c("KeyReleased", "", "Down")]}],
            [a("ModVarScene", "PausaSel", "=", "mod(Variable(PausaSel) + 1, 3)")]))
# confirmar
E.append(ev([c("VarScene", "Pausa", "=", "1"), {"type": {"value": "BuiltinCommonInstructions::Or"}, "parameters": [],
             "subInstructions": [c("KeyReleased", "", "Return"), c("KeyReleased", "", "Space")]}],
            [a("ModVarScene", "PausaGo", "=", "1")]))
for k in range(3):
    E.append(ev([c("VarScene", "Pausa", "=", "1"), c("MouseButtonReleased", "", "Left")] + dentro(k),
                [a("ModVarScene", "PausaSel", "=", str(k)), a("ModVarScene", "PausaGo", "=", "1")]))
E.append(ev([c("VarScene", "PausaGo", "=", "1"), c("VarScene", "PausaSel", "=", "0")],
            [a("ModVarScene", "PausaCambio", "=", "1")]))
E.append(ev([c("VarScene", "PausaGo", "=", "1"), c("VarScene", "PausaSel", "=", "1")],
            [a("ChangeTimeScale", "", "1"), a("Scene", "", '"Juego"', "")]))
E.append(ev([c("VarScene", "PausaGo", "=", "1"), c("VarScene", "PausaSel", "=", "2")],
            [a("ChangeTimeScale", "", "1"), a("ModVarGlobal", "Demo", "=", "0"), a("ModVarGlobal", "Listo", "=", "0"),
             a("Scene", "", '"Titulo"', "")]))
E.append(ev([], [a("ModVarScene", "PausaGo", "=", "0")]))
for e in E: e["fdiz20"] = True
grupo = {"type": "BuiltinCommonInstructions::Group", "colorB": 228, "colorG": 176, "colorR": 74, "creationTime": 0,
         "name": "Menú de pausa", "source": "", "events": E, "parameters": [], "fdiz20": True}
J["events"] = [e for e in J["events"] if not e.get("fdiz20")]
J["events"].append(grupo)
json.dump(p, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("OK fase 20: menú de pausa")
