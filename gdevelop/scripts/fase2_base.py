"""Fase 2 de FDI-Z: configura el proyecto base y agrega a Tony.

Uso: python fase2_base.py <FDI-Z.json> <atlas.json> <carpeta generado/sprites> <carpeta del proyecto>
- Copia los cuadros de Tony a <proyecto>/assets/sprites/personajes/tony/ (no toca los originales).
- Deja la escena Juego con capas Fondo, Juego, Techo, Niebla, Luz y HUD.
- Es re-ejecutable: reemplaza lo que ya haya creado antes con el mismo nombre.
"""
import json, os, shutil, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from gd_util import *

proyecto_json, atlas_json, sprites_dir, proyecto_dir = sys.argv[1:5]
p = json.load(open(proyecto_json, encoding="utf-8"))
atlas = json.load(open(atlas_json, encoding="utf-8"))

# ---------- propiedades del juego ----------
pr = p["properties"]
pr.update({"windowWidth": 1920, "windowHeight": 1080, "antialiasingMode": "none",
           "pixelsRounding": True, "scaleMode": "nearest", "name": "FDI-Z",
           "author": "Equipo FDI-Z", "sizeOnStartupMode": "adaptWidth"})

# ---------- escena Juego ----------
esc = p["layouts"][0]
viejo = esc["name"]
esc.update({"name": "Juego", "mangledName": "Juego", "r": 18, "v": 18, "b": 26})
p["firstLayout"] = "Juego"
p["layoutsFolderStructure"] = {"folderName": "__ROOT", "children": [{"itemName": "Juego"}]}
esc["uiSettings"]["gridWidth"] = esc["uiSettings"]["gridHeight"] = 32

# Capas de abajo hacia arriba. La capa base "" se queda (la usan las acciones de cámara
# por defecto) pero vacía; las demás siguen su cámara salvo HUD.
esc["layers"] = [
    capa("", True),
    capa("Fondo", True),
    capa("Juego", True),
    capa("Techo", True),
    capa("Niebla", True),
    capa("Luz", True, luz=True, ambiente=(120, 125, 165)),   # noche suave (fase 10 la ajusta)
    capa("HUD", False),
]

esc["variables"] = [v for v in esc["variables"] if v["name"] not in ("Estado",)]
esc["variables"].append(var("Estado", "juego"))

# ---------- recursos y objeto Tony ----------
ent = atlas["entidades"]["personajes/tony"]
lienzo_w, lienzo_h = ent["lienzo"]
origen = (lienzo_w // 2, lienzo_h - 2)                     # pies: 2 px arriba del borde
mascara = (origen[0] - 14, origen[1] - 16, origen[0] + 14, origen[1])  # solo los pies

recursos = {r["name"]: r for r in p["resources"]["resources"]}
copiados = []
anims = []
orden = ["quieto", "caminar_abajo", "caminar_arriba", "caminar_lado", "pegar_abajo",
         "pegar_arriba", "pegar_lado", "habilidad", "especial", "caer_levantarse", "festejo"]
for nombre in orden:
    an = ent["animaciones"][nombre]
    imgs = []
    for rel in an["cuadros"]:
        destino_rel = "assets/sprites/" + rel
        destino = os.path.join(proyecto_dir, *destino_rel.split("/"))
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        shutil.copyfile(os.path.join(sprites_dir, *rel.split("/")), destino)
        copiados.append(destino_rel)
        rname = rel  # p.ej. personajes/tony/quieto/quieto_00.png
        recursos[rname] = res_imagen(rname, destino_rel)
        imgs.append(rname)
    anims.append(animacion(nombre, imgs, an["fps"], an["loop"], origen, mascara))

topdown = {"name": "TopDownMovement", "type": "TopDownMovementBehavior::TopDownMovementBehavior",
           "acceleration": 1600, "allowDiagonals": True, "angleOffset": 0,
           "angularMaxSpeed": 180, "customIsometryAngle": 30, "deceleration": 1800,
           "ignoreDefaultControls": True, "maxSpeed": 204, "movementAngleOffset": 0,
           "rotateObject": False, "useLegacyTurnBack": False, "viewpoint": "TopDown"}
tony = objeto_sprite("Tony", anims,
                     variables=[var("Personaje", "tony"), var("Jugador", 1), var("Vida", 120),
                                var("VidaMax", 120), var("Fuerza", 1.3), var("Estado", "normal")],
                     comportamientos=[topdown])

# ---------- piso de prueba (marcador provisional hasta la fase 3) ----------
piso_rel = "assets/provisional/piso_prueba.png"
piso = Image.new("RGBA", (512, 512), (60, 62, 74, 255))
for ty in range(16):
    for tx in range(16):
        if (tx + ty) % 2:
            for yy in range(32):
                for xx in range(32):
                    piso.putpixel((tx * 32 + xx, ty * 32 + yy), (72, 75, 90, 255))
os.makedirs(os.path.join(proyecto_dir, "assets", "provisional"), exist_ok=True)
piso.save(os.path.join(proyecto_dir, *piso_rel.split("/")))
copiados.append(piso_rel)
recursos["provisional/piso_prueba.png"] = res_imagen("provisional/piso_prueba.png", piso_rel)
piso_obj = objeto_sprite("PisoPrueba", [animacion("piso", ["provisional/piso_prueba.png"], 1, False, (0, 0))])

p["resources"]["resources"] = list(recursos.values())
nombres = {"Tony", "PisoPrueba"}
esc["objects"] = [o for o in esc["objects"] if o["name"] not in nombres] + [piso_obj, tony]
esc["objectsFolderStructure"] = {"folderName": "__ROOT", "children": [
    {"folderName": "Personajes", "children": [{"itemName": "Tony"}]},
    {"folderName": "Provisional", "children": [{"itemName": "PisoPrueba"}]}]}

# ---------- instancias ----------
esc["instances"] = [i for i in esc["instances"] if i["name"] not in nombres]
for gy in range(6):
    for gx in range(8):
        esc["instances"].append(instancia("PisoPrueba", gx * 512, gy * 512, "Fondo", 0))
esc["instances"].append(instancia("Tony", 2048, 1536, "Juego", 1536))

# ---------- eventos ----------
T = ("Tony", "TopDownMovement")
def tecla(k): return c("KeyPressed", "", k)
def cmp(e1, op, e2): return c("BuiltinCommonInstructions::CompareNumbers", e1, op, e2)
VX, VY = "Tony.TopDownMovement::XVelocity()", "Tony.TopDownMovement::YVelocity()"

eventos = [
    comentario("FDI-Z · Fase 2: Tony se mueve con WASD (izquierda = espejo de caminar_lado) "
               "y la cámara lo sigue. Los controles completos y el control de Xbox llegan en la fase 5."),
    grupo("Movimiento (teclado P1)", [
        ev([tecla("w")], [a("TopDownMovementBehavior::SimulateUpKey", *T)]),
        ev([tecla("s")], [a("TopDownMovementBehavior::SimulateDownKey", *T)]),
        ev([tecla("a")], [a("TopDownMovementBehavior::SimulateLeftKey", *T)]),
        ev([tecla("d")], [a("TopDownMovementBehavior::SimulateRightKey", *T)]),
    ]),
    grupo("Animación por dirección", [
        ev([c("TopDownMovementBehavior::IsMoving", *T)], [], sub=[
            ev([cmp(f"abs({VX})", ">", f"abs({VY})")],
               [a("SetAnimationName", "Tony", "\"caminar_lado\"")], sub=[
                ev([cmp(VX, "<", "0")], [a("FlipX", "Tony", "yes")]),
                ev([cmp(VX, ">", "0")], [a("FlipX", "Tony", "no")]),
            ]),
            ev([cmp(f"abs({VX})", "<=", f"abs({VY})"), cmp(VY, "<", "0")],
               [a("SetAnimationName", "Tony", "\"caminar_arriba\""), a("FlipX", "Tony", "no")]),
            ev([cmp(f"abs({VX})", "<=", f"abs({VY})"), cmp(VY, ">", "0")],
               [a("SetAnimationName", "Tony", "\"caminar_abajo\""), a("FlipX", "Tony", "no")]),
        ]),
        ev([c("TopDownMovementBehavior::IsMoving", *T, invertida=True)],
           [a("SetAnimationName", "Tony", "\"quieto\""), a("FlipX", "Tony", "no")]),
    ]),
    grupo("Orden por Y y cámara", [
        ev([], [a("ChangePlan", "Tony", "=", "Tony.Y()")]),
        ev([c("DepartScene", "")], [a("CameraX", "", "=", "Tony.X()", "", ""),
                                    a("CameraY", "", "=", "Tony.Y() - 48", "", "")]),
        ev([], [a("CameraX", "", "=", "CameraX() + (Tony.X() - CameraX()) * min(1, 8 * TimeDelta())", "", ""),
                a("CameraY", "", "=", "CameraY() + (Tony.Y() - 48 - CameraY()) * min(1, 8 * TimeDelta())", "", "")]),
    ]),
]
esc["events"] = eventos

json.dump(p, open(proyecto_json, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("OK", len(copiados), "archivos copiados")
json.dump(copiados, open(os.path.join(os.path.dirname(proyecto_json), ".fase2_archivos.json"), "w"))
