"""Fase 37 · Pantalla "Unanse": (a) los slots vacios muestran el boton A del mando Xbox; (b) bajo el teclado del Player 1 aparece una Y de mando:
al pulsar Y en un mando, el P1 juega con ese mando (icono de mando) y abajo aparece una P de teclado; al pulsar P vuelve a teclado y raton (icono de teclado) y abajo otra vez la Y. Idempotente."""
import json, os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gd_util import c, a, instancia, res_imagen, objeto_sprite, animacion
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
IMG = os.path.join(AQUI, "..", "FDI-Z", "assets", "interfaz")
bak = os.path.join(AQUI, "..", "respaldos", "antes_de_fase37_20261117.json")
if not os.path.exists(bak): shutil.copy(PRY, bak)

# ---------------------------------------------------------------- imagenes (pixel art 24x18 -> x6 = 144x108, como slot_ico_*)
NAVY, BORDE = (26, 26, 58, 255), (12, 12, 30, 255)
FONT = {"A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
        "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
        "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"]}
def letra(im, ch, x0, y0, col):
    for r, fila in enumerate(FONT[ch]):
        for k, v in enumerate(fila):
            if v == "1": im.putpixel((x0 + k, y0 + r), col)
def boton(ch, fill, luz, sombra):
    im = Image.new("RGBA", (24, 18), (0, 0, 0, 0)); cx, cy, R = 11.5, 8.5, 8.2
    for y in range(18):
        for x in range(24):
            dd = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            if dd <= R: im.putpixel((x, y), BORDE if dd > R - 1.3 else fill)
    for (x, y) in ((7, 4), (8, 3), (9, 3), (6, 5), (7, 3)): im.putpixel((x, y), luz)
    for (x, y) in ((15, 14), (14, 15), (16, 13), (13, 15)): im.putpixel((x, y), sombra)
    letra(im, ch, 9, 5, NAVY); return im
def tecla(ch):
    im = Image.new("RGBA", (24, 18), (0, 0, 0, 0))
    for y in range(2, 16):
        for x in range(4, 20):
            borde = x in (4, 19) or y in (2, 15)
            im.putpixel((x, y), BORDE if borde else ((122, 122, 181, 255) if y >= 13 else (196, 196, 240, 255)))
    for (x, y) in ((4, 2), (19, 2), (4, 15), (19, 15)): im.putpixel((x, y), (0, 0, 0, 0))
    letra(im, ch, 9, 4, NAVY); return im
def guardar(im, nombre):
    ruta = os.path.join(IMG, nombre + ".png")
    im.resize((144, 108), Image.NEAREST).save(ruta)
guardar(boton("A", (96, 200, 80, 255), (190, 245, 160, 255), (50, 130, 50, 255)), "slot_ico_btn_a")
guardar(boton("Y", (255, 214, 64, 255), (255, 244, 170, 255), (200, 150, 30, 255)), "slot_ico_btn_y")
guardar(tecla("P"), "slot_ico_key_p")

d = json.load(open(PRY))
M = next(l for l in d["layouts"] if l["name"] == "Menu")
ME = M["events"]
MK = "FDIZ-FASE37"
STD = "BuiltinCommonInstructions::Standard"

# ---------------------------------------------------------------- recursos
nombres = {r["name"] for r in d["resources"]["resources"]}
for n in ("slot_ico_btn_a", "slot_ico_btn_y", "slot_ico_key_p"):
    if n not in nombres:
        d["resources"]["resources"].append({"file": "assets/interfaz/%s.png" % n, "kind": "image", "metadata": "", "name": n, "smoothed": False, "userAdded": True})

# ---------------------------------------------------------------- objetos
def anim(nombre, img):
    return {"name": nombre, "useMultipleDirections": False, "directions": [{"looping": False, "timeBetweenFrames": 1.0, "sprites": [
        {"hasCustomCollisionMask": False, "image": img, "points": [], "originPoint": {"name": "origine", "x": 0, "y": 0},
         "centerPoint": {"automatic": True, "name": "centre", "x": 0, "y": 0}, "customCollisionMask": []}]}]}
slot = next(o for o in M["objects"] if o["name"] == "SlotIco")
for an in slot["animations"]:
    if an["name"] == "libre": an["directions"][0]["sprites"][0]["image"] = "slot_ico_btn_a"      # (a) A del mando en los slots vacios
if not any(o["name"] == "SlotAlt" for o in M["objects"]):
    M["objects"].append({"adaptCollisionMaskAutomatically": False, "assetStoreId": "", "name": "SlotAlt", "type": "Sprite", "updateIfNotVisible": False,
                         "variables": [], "effects": [], "behaviors": [], "animations": [anim("y", "slot_ico_btn_y"), anim("p", "slot_ico_key_p")]})
if not any(i["name"] == "SlotAlt" for i in M["instances"]):
    base = next(i for i in M["instances"] if i["name"] == "SlotIco")
    n = json.loads(json.dumps(base))
    n.update({"name": "SlotAlt", "x": 240, "y": 770, "width": 120, "height": 90, "zOrder": 7, "variables": []})
    M["instances"].append(n)

# ---------------------------------------------------------------- eventos
def marca(k):
    return {"type": "BuiltinCommonInstructions::Comment", "color": {"b": 109, "g": 230, "r": 255, "textB": 0, "textG": 0, "textR": 0}, "comment": MK + "-" + k, "comment2": ""}
def hay(k): return any(e.get("comment") == MK + "-" + k for e in ME)
def std(conds, acts): return {"type": STD, "conditions": conds, "actions": acts, "events": []}
UN = c("VarSceneTxt", "Paso", "=", '"unirse"')
if not hay("CTL"):
    nuevos = [marca("CTL")]
    for n in (1, 2, 3, 4):   # Y en el mando n: el P1 pasa a jugar con ese mando (si no lo usa otro jugador)
        conds = [UN, c("VarScene", "S1Ctl", "=", "0"), c("Gamepads::C_Button_released", "", str(n), '"Y"', "")]
        conds += [c("VarScene", "S%dCtl" % k, "!=", str(n)) for k in (2, 3, 4)]
        nuevos.append(std(conds, [a("ModVarScene", "S1Ctl", "=", str(n))]))
    # P en el teclado: el P1 vuelve a teclado y raton
    nuevos.append(std([UN, c("VarScene", "S1Ctl", ">", "0"), c("KeyReleased", "", "p")], [a("ModVarScene", "S1Ctl", "=", "0")]))
    # icono de abajo: Y (si juega con teclado) o P (si juega con mando); solo en esta pantalla
    nuevos.append(std([UN, c("VarScene", "S1Ctl", "<=", "0")], [a("SetAnimationName", "SlotAlt", '"y"'), a("Opacity", "SlotAlt", "=", "255")]))
    nuevos.append(std([UN, c("VarScene", "S1Ctl", ">", "0")], [a("SetAnimationName", "SlotAlt", '"p"'), a("Opacity", "SlotAlt", "=", "255")]))
    nuevos.append(std([c("VarSceneTxt", "Paso", "!=", '"unirse"')], [a("Opacity", "SlotAlt", "=", "0")]))
    # despues de los iconos de slot (evento SlotIco del slot 4)
    idx = max(i for i, e in enumerate(ME) if e["type"].endswith("Standard") and any(x["parameters"][:1] == ["SlotIco"] for x in e["actions"]))
    ME[idx + 1:idx + 1] = nuevos
json.dump(d, open(PRY, "w"), ensure_ascii=False, indent=2)
print("OK fase 37")
