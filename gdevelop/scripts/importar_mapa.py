"""FDI-Z · Importa el mapa a la escena Juego del proyecto GDevelop.

Uso (con GDevelop CERRADO):
    python importar_mapa.py <RAIZ fdiz> <carpeta del proyecto FDI-Z>

Qué hace (todo se puede volver a correr cuando cambie el mapa):
  1. Respaldo con fecha del FDI-Z.json en gdevelop\\respaldos\\.
  2. Copia al proyecto: mapa_fdiz_gdevelop.json, tileset_fdiz.png y los PNG de muebles usados.
  3. BORRA todos los objetos e instancias del mapa (lista OBJETOS_MAPA) y los vuelve a crear:
       Mapa (Tilemap), MapaChoque (Tilemap collision mask, clase "muro"),
       Muro (uno por rectángulo de "colisiones"), ChoqueMueble (uno por mueble con "colision"),
       Mueble (un objeto con una animación por sprite; cada instancia elige la suya),
       Puerta, Niebla (una por zona) y Marcador (inicio, objetivos, bidones, rejillas, etc.).
  4. Pone a los jugadores en el primer punto de "aparicion_jugadores".
No usa librerías externas (lee el tamaño de los PNG a mano).
"""
import json, os, shutil, struct, sys, datetime, uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gd_util import res_imagen, var, cuadro, animacion, objeto_sprite, instancia

RAIZ, PROY = sys.argv[1], sys.argv[2]
PJSON = os.path.join(PROY, "FDI-Z.json")
FINAL = os.path.join(RAIZ, "mapa", "final")
SPRITES = os.path.join(RAIZ, "generado", "sprites")

OBJETOS_MAPA = ["Mapa", "MapaChoque", "Muro", "ChoqueMueble", "Mueble", "Puerta", "Niebla", "Marcador"]
CAPA_FONDO, CAPA_JUEGO, CAPA_NIEBLA = "Fondo", "Juego", "Niebla"

def png_tamano(ruta):
    with open(ruta, "rb") as f:
        cab = f.read(24)
    return struct.unpack(">II", cab[16:24])

def png_color(ruta, rgba, w=32, h=32):
    """Escribe un PNG de color sólido sin librerías."""
    import zlib
    fila = b"\x00" + bytes(rgba) * w
    datos = zlib.compress(fila * h)
    def trozo(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    png = b"\x89PNG\r\n\x1a\n" + trozo(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)) \
        + trozo(b"IDAT", datos) + trozo(b"IEND", b"")
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    open(ruta, "wb").write(png)

def rel(*partes):
    return "/".join(partes)

# ---------- 1. respaldo ----------
resp_dir = os.path.join(os.path.dirname(PROY), "respaldos")
os.makedirs(resp_dir, exist_ok=True)
sello = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
shutil.copyfile(PJSON, os.path.join(resp_dir, f"FDI-Z_antes_importar_mapa_{sello}.json"))

p = json.load(open(PJSON, encoding="utf-8"))
esc = next(l for l in p["layouts"] if l["name"] == "Juego")
datos = json.load(open(os.path.join(FINAL, "mapa_fdiz_datos.json"), encoding="utf-8"))
props = json.load(open(os.path.join(FINAL, "mapa_fdiz_props.json"), encoding="utf-8"))["props"]

# ---------- 2. copiar archivos ----------
copiados = []
def copia(origen, destino_rel):
    destino = os.path.join(PROY, *destino_rel.split("/"))
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    shutil.copyfile(origen, destino)
    copiados.append(destino_rel)

copia(os.path.join(FINAL, "mapa_fdiz_gdevelop.json"), "assets/mapa/mapa_fdiz_gdevelop.json")
copia(os.path.join(FINAL, "tileset_fdiz.png"), "assets/mapa/tileset_fdiz.png")

recursos = [r for r in p["resources"]["resources"] if not r["name"].startswith("mapa/")]
recursos.append({"file": "assets/mapa/mapa_fdiz_gdevelop.json", "kind": "tilemap", "metadata": "",
                 "name": "mapa/mapa_fdiz_gdevelop.json", "userAdded": True})
recursos.append(res_imagen("mapa/tileset_fdiz.png", "assets/mapa/tileset_fdiz.png"))

# marcadores de color provisionales (rectángulos que se estiran)
COLORES = {"muro": (230, 40, 40, 110), "choque": (255, 150, 0, 110), "niebla": (0, 0, 0, 255),
           "marcador": (255, 220, 0, 200), "falta": (255, 0, 255, 200),
           "puerta_normal": (140, 90, 40, 255), "puerta_electronica": (40, 200, 90, 255),
           "puerta_restringida": (210, 40, 40, 255), "puerta_restringida_electronica": (150, 60, 220, 255)}
for k, col in COLORES.items():
    r = f"assets/mapa/provisional/{k}.png"
    png_color(os.path.join(PROY, *r.split("/")), col)
    copiados.append(r)
    recursos.append(res_imagen(f"mapa/provisional/{k}.png", r))

# ---------- 3. objetos ----------
obstaculo = {"name": "Obstaculo", "type": "PathfindingBehavior::PathfindingObstacleBehavior",
             "cost": 2, "impassable": True}

def obj_rect(nombre, color, variables=(), comps=()):
    return objeto_sprite(nombre, [animacion("rect", [f"mapa/provisional/{color}.png"], 1, False, (0, 0))],
                         variables, comps)

objetos = []
objetos.append({"assetStoreId": "", "name": "Mapa", "type": "TileMap::TileMap",
                "variables": [], "effects": [], "behaviors": [],
                "content": {"tilemapJsonFile": "mapa/mapa_fdiz_gdevelop.json", "tilesetJsonFile": "",
                            "tilemapAtlasImage": "mapa/tileset_fdiz.png", "displayMode": "visible",
                            "layerIndex": 0, "levelIndex": 0, "animationSpeedScale": 1,
                            "animationFps": 4}})
objetos.append({"assetStoreId": "", "name": "MapaChoque", "type": "TileMap::CollisionMask",
                "variables": [], "effects": [], "behaviors": [],
                "content": {"tilemapJsonFile": "mapa/mapa_fdiz_gdevelop.json", "tilesetJsonFile": "",
                            "collisionMaskTag": "muro", "layerIndex": 0, "useAllLayers": True,
                            "debugMode": False, "fillColor": "255;0;0", "outlineColor": "255;0;0",
                            "fillOpacity": 64, "outlineOpacity": 128, "outlineSize": 1}})
objetos.append(obj_rect("Muro", "muro", comps=[obstaculo]))
objetos.append(obj_rect("ChoqueMueble", "choque", comps=[obstaculo]))
objetos.append(obj_rect("Niebla", "niebla", variables=[var("Zona", ""), var("Grupo", "")]))
objetos.append(obj_rect("Marcador", "marcador",
                        variables=[var("Tipo", ""), var("Zona", ""), var("Nota", ""), var("Indice", 0)]))

# Puerta: una animación por tipo
tipos_puerta = ["normal", "electronica", "restringida", "restringida_electronica"]
objetos.append(objeto_sprite("Puerta",
    [animacion(t, [f"mapa/provisional/puerta_{t}.png"], 1, False, (0, 0)) for t in tipos_puerta],
    variables=[var("Id", ""), var("Tipo", "normal"), var("Estilo", ""), var("Orientacion", ""),
               var("Zonas", ""), var("Vida", 80), var("TiempoAbrir", 1), var("Progreso", 0),
               var("Trabada", 0)],
    comportamientos=[obstaculo]))

# Mueble: una animación por sprite distinto
sprites = []
for pr in props:
    if pr.get("archivo") and pr["sprite"] not in sprites:
        sprites.append(pr["sprite"])
anims_mueble, faltan = [], []
for s in sprites:
    arch = next(pr["archivo"] for pr in props if pr["sprite"] == s)
    origen = os.path.join(SPRITES, *arch.split("/"))
    if os.path.exists(origen):
        w, h = png_tamano(origen)
        destino_rel = "assets/mapa/muebles/" + arch
        copia(origen, destino_rel)
        rname = "mapa/muebles/" + arch
        recursos.append(res_imagen(rname, destino_rel))
        anims_mueble.append(animacion(s, [rname], 1, False, (w // 2, h)))
    else:  # falta el PNG: rectángulo magenta del tamaño del mueble
        pr0 = next(pr for pr in props if pr["sprite"] == s)
        faltan.append(arch)
        anims_mueble.append(animacion(s, ["mapa/provisional/falta.png"], 1, False, (16, 32)))
indice_anim = {s: i for i, s in enumerate(sprites)}
objetos.append(objeto_sprite("Mueble", anims_mueble,
                             variables=[var("Sprite", ""), var("Capa", "")]))

# Fondo dibujado con sprites: el objeto Tilemap de GDevelop 5.6.287 sale casi negro en la vista
# previa (en el editor se ve bien). Mientras se resuelve, el piso y los muros se dibujan con
# mapa_fdiz_completo.png cortado en pedazos de 2048 px (lo genera el mismo construir_mapa.py).
TROZO = 2048
fondo_png = os.path.join(FINAL, "mapa_fdiz_completo.png")
ancho_px, alto_px = datos["ancho_px"], datos["alto_px"]
trozos = []
for fy in range(0, alto_px, TROZO):
    for fx in range(0, ancho_px, TROZO):
        nombre = f"fondo_{fy // TROZO}_{fx // TROZO}"
        destino_rel = f"assets/mapa/fondo/{nombre}.png"
        trozos.append((nombre, fx, fy, destino_rel))
try:
    from PIL import Image
    img = Image.open(fondo_png)
    for nombre, fx, fy, destino_rel in trozos:
        destino = os.path.join(PROY, *destino_rel.split("/"))
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        img.crop((fx, fy, min(fx + TROZO, ancho_px), min(fy + TROZO, alto_px))).save(destino)
        copiados.append(destino_rel)
except ImportError:
    print("AVISO: sin Pillow (pip install pillow) no se recortó el fondo; se usan los pedazos que ya existan.")
for nombre, fx, fy, destino_rel in trozos:
    recursos.append(res_imagen(f"mapa/fondo/{nombre}.png", destino_rel))
objetos.append(objeto_sprite("MapaFondo",
    [animacion(n, [f"mapa/fondo/{n}.png"], 1, False, (0, 0)) for n, _, _, _ in trozos]))
OBJETOS_MAPA.append("MapaFondo")

p["resources"]["resources"] = recursos
esc["objects"] = [o for o in esc["objects"] if o["name"] not in OBJETOS_MAPA] + objetos
grupos = [g for g in esc["objectsGroups"] if g["name"] != "Solidos"]
grupos.append({"name": "Solidos", "objects": [{"name": "Muro"}, {"name": "ChoqueMueble"},
                                              {"name": "Puerta"}]})
esc["objectsGroups"] = grupos

# ---------- 4. instancias ----------
inst = [i for i in esc["instances"] if i["name"] not in OBJETOS_MAPA]
inst.append(instancia("Mapa", 0, 0, CAPA_FONDO, -1))
inst.append(instancia("MapaChoque", 0, 0, CAPA_FONDO, 0))
for k, (nombre, fx, fy, _) in enumerate(trozos):
    t = instancia("MapaFondo", fx, fy, CAPA_FONDO, 1)
    t["numberProperties"] = [{"name": "animation", "value": k}]
    inst.append(t)

for r in datos["colisiones"]:
    inst.append(instancia("Muro", r["x"], r["y"], CAPA_JUEGO, 0, r["w"], r["h"]))

n_choques = 0
for pr in props:
    col = pr.get("colision")
    if col:
        inst.append(instancia("ChoqueMueble", col["x"], col["y"], CAPA_JUEGO, 0, col["w"], col["h"]))
        n_choques += 1
    if not pr.get("archivo"):
        continue
    z = int(pr["y"]) + (64 if pr["capa"] == "encima" else 0)
    i = instancia("Mueble", pr["x"], pr["y"], CAPA_JUEGO, z,
                  variables=[var("Sprite", pr["sprite"]), var("Capa", pr["capa"])])
    i["numberProperties"] = [{"name": "animation", "value": indice_anim[pr["sprite"]]}]
    if pr["archivo"] in faltan:
        i.update({"customSize": True, "width": pr["w"], "height": pr["h"]})
    inst.append(i)

VIDA = {"normal": 80, "electronica": 100, "restringida": 150, "restringida_electronica": 150}
ABRIR = {"normal": 1, "electronica": 8, "restringida": 0, "restringida_electronica": 0}
for d in datos["puertas"]:
    t = d["tipo"]
    i = instancia("Puerta", d["x"], d["y"], CAPA_JUEGO, int(d["y"] + d["h"]), d["w"], d["h"],
                  variables=[var("Id", d["id"]), var("Tipo", t), var("Estilo", d.get("estilo", "")),
                             var("Orientacion", d.get("orientacion", "")),
                             var("Zonas", ",".join(d.get("zonas", []))), var("Vida", VIDA[t]),
                             var("TiempoAbrir", ABRIR[t])])
    i["numberProperties"] = [{"name": "animation", "value": tipos_puerta.index(t)}]
    inst.append(i)

for z in datos["zonas"]:
    inst.append(instancia("Niebla", z["x"], z["y"], CAPA_NIEBLA, 0, z["w"], z["h"],
                          variables=[var("Zona", z["nombre"]), var("Grupo", z["grupo"])]))

n_marc = 0
def marcador(tipo, d, indice=0):
    global n_marc
    w, h = d.get("w", 32), d.get("h", 32)
    x, y = d["x"] - (16 if "w" not in d else 0), d["y"] - (16 if "h" not in d else 0)
    nota = d.get("nota", "") + (f" radio={d['radio']}" if "radio" in d else "")
    inst.append(instancia("Marcador", x, y, CAPA_JUEGO, 0, w, h,
                          variables=[var("Tipo", tipo), var("Zona", d.get("zona", "")),
                                     var("Nota", nota.strip()), var("Indice", indice)]))
    n_marc += 1

for tipo, v in datos["marcadores"].items():
    if isinstance(v, list):
        for k, d in enumerate(v):
            marcador(tipo, d, k)
    else:
        marcador(tipo, v)
# Salidas de zombies: el punto libre (sin muro ni mueble) más cercano a cada rejilla del Jefe.
bloques = [(r["x"], r["y"], r["w"], r["h"]) for r in datos["colisiones"]] + \
          [(pr["colision"]["x"], pr["colision"]["y"], pr["colision"]["w"], pr["colision"]["h"])
           for pr in props if pr.get("colision")]
def libre(x, y, m=24):
    return all(not (bx - m < x < bx + bw + m and by - m < y < by + bh + m) for bx, by, bw, bh in bloques) \
        and 0 < x < datos["ancho_px"] and 0 < y < datos["alto_px"]
for k, rj in enumerate(datos["marcadores"]["rejillas_jefe"]):
    hecho = False
    for radio in range(0, 640, 32):
        for dx in range(-radio, radio + 1, 32):
            for dy in (-radio, radio) if abs(dx) != radio else range(-radio, radio + 1, 32):
                if libre(rj["x"] + dx, rj["y"] + dy):
                    marcador("salida_zombie", {"x": rj["x"] + dx, "y": rj["y"] + dy}, k)
                    hecho = True
                    break
            if hecho: break
        if hecho: break
# decisión del 5 nov: la cinemática ocurre en B-01 (provisional: el mapa solo tiene planta baja)
b01 = next(z for z in datos["zonas"] if z["nombre"] == "B-01")
marcador("cinematica_salon", {"x": b01["x"] + b01["w"] // 2, "y": b01["y"] + b01["h"] // 2,
                              "zona": "B-01", "nota": "pendiente: planta 1 de B"})

# jugadores al punto de inicio
ini = datos["marcadores"]["aparicion_jugadores"]
k = 0
for i in inst:
    if i["name"] in ("Tony",):
        i["x"], i["y"] = ini[k % len(ini)]["x"], ini[k % len(ini)]["y"]
        i["zOrder"] = int(i["y"])
        k += 1

esc["instances"] = inst

json.dump(p, open(PJSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
json.dump(copiados, open(os.path.join(PROY, ".importar_mapa_archivos.json"), "w"))
print(f"OK · muros {len(datos['colisiones'])} · choques {n_choques} · muebles "
      f"{sum(1 for pr in props if pr.get('archivo'))} ({len(sprites)} sprites, faltan {len(faltan)}: {faltan}) · "
      f"puertas {len(datos['puertas'])} · nieblas {len(datos['zonas'])} · marcadores {n_marc}")
