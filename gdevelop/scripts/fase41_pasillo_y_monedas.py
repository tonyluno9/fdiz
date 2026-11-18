"""Fase 41 · Pasillo de la nevería más ancho y monedas solo en modo Jefe.

Uso (desde la carpeta fdiz, con GDevelop CERRADO):  python gdevelop/scripts/fase41_pasillo_y_monedas.py
Idempotente (se puede correr varias veces). Va al final de la cadena, después de fase40_profesores.py.
Si se vuelve a importar el mapa (importar_mapa.py), correr esta fase otra vez.

1. Pasillo de piedra entre la nevería (puerta P45) y las Salas 3 y 4.
   Medía 32 px (1 casilla); el pie de un personaje mide 40 px y la navegación A* pide 2 x 18 px de holgura,
   así que nadie pasaba. La pared izquierda de las Salas 3 y 4 se recorre 2 casillas (64 px) a la derecha:
   el pasillo queda de 96 px (x 2016-2112) y las salas de 512 px (antes 576).
     - Muro: paredes de las salas recortadas/movidas (choques y navegación A* salen de Muro y ChoqueMueble).
     - Fondo visible (assets/mapa/fondo/fondo_*.png) y mapa_fdiz_completo.png: piso de piedra y pared movida.
     - Tilemap (Mapa / MapaChoque, oculto) y los datos fuente de mapa/final para que una nueva importación
       conserve el cambio.
     - Niebla de Sala 3 y Sala 4 ajustada a su nuevo ancho.
     - Se quita la primera columna de computadoras de cada sala (quedaba dentro de la pared nueva) y el letrero
       de salida de emergencia de la Sala 4 se recorre con la pared.
2. Monedas: los lockers y mochilas soltaban una moneda (45 %) en todos los modos, aunque la fase 28 ya había
   quitado la tienda y el dinero (y no hay evento para recogerlas). Ahora la moneda solo sale en modo Jefe;
   en modo escape ese 45 % da galletas (Cura 30), como pretendía la fase 28.
"""
import copy, json, os, shutil, datetime

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
PROY_DIR = os.path.join(RAIZ, "gdevelop", "FDI-Z")
PRY = os.path.join(PROY_DIR, "FDI-Z.json")
FINAL = os.path.join(RAIZ, "mapa", "final")
MK = "FDIZ-FASE41"

DX = 64                    # cuánto se recorre la pared (2 casillas de 32 px)
Y0, Y1 = 1376, 2112        # alto de la pared izquierda de las salas en el fondo (con el remate de arriba)
PIEDRA_X = 2016            # columna de piedra original del pasillo (32 px)
PARED_X = 2048             # columna de pared original (32 px)

# rectángulos de choque: (x, y, w, h) viejo -> nuevo
MUROS = {
    (2048, 1376, 2336, 64): (2048 + DX, 1376, 2336 - DX, 64),  # remate de arriba (de las salas al CIC)
    (2048, 1440, 640, 32): (2048 + DX, 1440, 640 - DX, 32),    # pared de arriba de Sala 3
    (2048, 1472, 32, 640): (2048 + DX, 1472, 32, 640),         # pared izquierda de las salas
    (2080, 1728, 576, 64): (2080 + DX, 1728, 576 - DX, 64),    # muro entre Sala 3 y Sala 4
    (2080, 1792, 544, 32): (2080 + DX, 1792, 544 - DX, 32),
    (2080, 2080, 576, 32): (2080 + DX, 2080, 576 - DX, 32),    # pared de abajo de Sala 4
}
ZONAS = {"Sala 3", "Sala 4"}       # x 2080, w 576 -> x 2144, w 512
CHOQUES_FUERA = {(2112, 1470), (2112, 1686), (2112, 1822), (2112, 2038)}   # pupitres de la primera columna
MUEBLES_FUERA = {(2144, y) for y in (1510, 1546, 1694, 1726, 1862, 1898, 2046, 2078)}
LETRERO = ((2112, 1818), (2112 + DX, 1818))   # senaletica/salida_emergencia en la pared de Sala 4


# ------------------------------------------------------------------ utilidades
def escribir_json(ruta, datos, **kw):
    tmp = ruta + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, **kw)
    os.replace(tmp, ruta)


def respaldo(ruta, etiqueta):
    resp = os.path.join(RAIZ, "gdevelop", "respaldos")
    os.makedirs(resp, exist_ok=True)
    dest = os.path.join(resp, "antes_de_fase41_%s_%s" % (etiqueta, os.path.basename(ruta)))
    if not os.path.exists(dest):
        shutil.copy(ruta, dest)


def walk(lst):
    for e in lst:
        yield e
        yield from walk(e.get("events", []))


# ------------------------------------------------------------------ imagen del fondo
def ya_movido(get):
    """La columna x 2048-2080 era pared (43, 51, 82); después es piedra."""
    return get(2064, 1600)[:3] != (43, 51, 82)


def transformar(get, put):
    """get/put en coordenadas del mundo. Lee todo antes de escribir."""
    nuevo = {}
    for y in range(Y0, Y1):
        for x in range(PARED_X, PARED_X + 2 * 32):      # 2048-2112: piedra (o piso exterior arriba)
            sy = y
            if x >= PARED_X + 32 and y >= 1440:          # la 2.a copia desfasada 64 px para que no se repita igual
                sy = 1440 + ((y - 1440 + 64) % (Y1 - 1440))
            nuevo[(x, y)] = get(PIEDRA_X + (x - PARED_X) % 32, sy)
        for x in range(PARED_X + DX, PARED_X + DX + 32):  # 2112-2144: la pared
            nuevo[(x, y)] = get(x - DX, y)
    for (x, y), p in nuevo.items():
        put(x, y, p)


def fondo_trozos():
    """Pedazos de 2048 px del fondo del proyecto (fondo_<fila>_<columna>.png)."""
    from PIL import Image
    T = 2048
    carp = os.path.join(PROY_DIR, "assets", "mapa", "fondo")
    abiertos = {}

    def img(x, y):
        k = (y // T, x // T)
        if k not in abiertos:
            ruta = os.path.join(carp, "fondo_%d_%d.png" % k)
            im = Image.open(ruta).convert("RGBA")
            abiertos[k] = [ruta, im, im.load(), False]
        return abiertos[k]

    def get(x, y):
        return img(x, y)[2][x % T, y % T]

    def put(x, y, p):
        r = img(x, y)
        r[2][x % T, y % T] = p
        r[3] = True

    return get, put, abiertos


def parchar_fondo():
    from PIL import Image
    hecho = []
    get, put, abiertos = fondo_trozos()
    if not ya_movido(get):
        transformar(get, put)
        for ruta, im, _, cambio in abiertos.values():
            if cambio:
                respaldo(ruta, "fondo")
                im.save(ruta)
                hecho.append(os.path.basename(ruta))
    comp = os.path.join(FINAL, "mapa_fdiz_completo.png")
    Image.MAX_IMAGE_PIXELS = None
    im = Image.open(comp)
    modo = im.mode
    im = im.convert("RGBA")
    px = im.load()
    if not ya_movido(lambda x, y: px[x, y]):
        transformar(lambda x, y: px[x, y], lambda x, y, p: px.__setitem__((x, y), p))
        respaldo(comp, "mapa")
        (im if modo == "RGBA" else im.convert(modo)).save(comp)
        hecho.append("mapa_fdiz_completo.png")
    return hecho


# ------------------------------------------------------------------ tilemap (Tiled)
def parchar_tiled(ruta):
    t = json.load(open(ruta, encoding="utf-8"))
    W = t["width"]
    c_pie, c_par = PIEDRA_X // 32, PARED_X // 32                # 63, 64
    muros = next(l for l in t["layers"] if l["name"] == "muros")["data"]
    cambio = False
    for l in t["layers"]:
        if l["type"] != "tilelayer" or muros[50 * W + c_par] == 0:   # columna 64 ya sin pared: ya aplicado
            continue
        cambio = True
        d = l["data"]
        viejo = list(d)
        for r in range(Y0 // 32, Y1 // 32):
            d[r * W + c_par + DX // 32] = viejo[r * W + c_par]      # pared en la columna 66
            for c in range(c_par, c_par + DX // 32):                # piedra en las columnas 64 y 65
                d[r * W + c] = viejo[r * W + c_pie]
    for l in t["layers"]:
        if l["type"] != "objectgroup":
            continue
        for o in l.get("objects", []):
            k = (round(o["x"]), round(o["y"]), round(o["width"]), round(o["height"]))
            if l["name"] == "colisiones" and k in MUROS:
                o["x"], o["y"], o["width"], o["height"] = MUROS[k]
                cambio = True
            if l["name"] == "zonas_niebla" and o.get("name") in ZONAS and k[0] == 2080:
                o["x"], o["width"] = 2080 + DX, o["width"] - DX
                cambio = True
    if cambio:
        respaldo(ruta, "tiled")
        escribir_json(ruta, t)
    return cambio


# ------------------------------------------------------------------ datos fuente del mapa
def parchar_datos():
    ruta = os.path.join(FINAL, "mapa_fdiz_datos.json")
    d = json.load(open(ruta, encoding="utf-8"))
    n = 0
    for c in d["colisiones"]:
        k = (c["x"], c["y"], c["w"], c["h"])
        if k in MUROS:
            c["x"], c["y"], c["w"], c["h"] = MUROS[k]; n += 1
    for z in d["zonas"]:
        if z["nombre"] in ZONAS and z["x"] == 2080:
            z["x"], z["w"] = 2080 + DX, z["w"] - DX; n += 1
    for c in d["cuartos"]:
        if c["nombre"] in ZONAS and c["x0"] == 2080:
            c["x0"] = 2080 + DX; n += 1
    if n:
        respaldo(ruta, "datos")
        escribir_json(ruta, d, indent=1)
    ruta = os.path.join(FINAL, "mapa_fdiz_props.json")
    pj = json.load(open(ruta, encoding="utf-8"))
    antes = len(pj["props"])
    pj["props"] = [p for p in pj["props"] if (p["x"], p["y"]) not in MUEBLES_FUERA]
    m = antes - len(pj["props"])
    for p in pj["props"]:
        if (p["x"], p["y"]) == LETRERO[0] and p["sprite"] == "senaletica/salida_emergencia":
            p["x"], p["y"] = LETRERO[1]; m += 1
    if m:
        respaldo(ruta, "props")
        escribir_json(ruta, pj, indent=0)
    return n, m


# ------------------------------------------------------------------ proyecto
def parchar_proyecto(d):
    J = next(l for l in d["layouts"] if l["name"] == "Juego")
    cambios = []
    inst = []
    for i in J["instances"]:
        k = (i["x"], i["y"], i.get("width"), i.get("height"))
        iv = {v["name"]: v.get("value") for v in i.get("initialVariables", [])}
        if i["name"] == "Muro" and k in MUROS:
            i["x"], i["y"], i["width"], i["height"] = MUROS[k]; cambios.append("Muro %s" % (k,))
        elif i["name"] == "Niebla" and iv.get("Zona") in ZONAS and i["x"] == 2080:
            i["x"], i["width"] = 2080 + DX, i["width"] - DX; cambios.append("Niebla " + iv["Zona"])
        elif i["name"] == "ChoqueMueble" and (i["x"], i["y"]) in CHOQUES_FUERA:
            cambios.append("quita ChoqueMueble %s" % ((i["x"], i["y"]),)); continue
        elif i["name"] == "Mueble" and (i["x"], i["y"]) in MUEBLES_FUERA:
            cambios.append("quita Mueble %s %s" % ((i["x"], i["y"]), iv.get("Sprite"))); continue
        elif i["name"] == "Mueble" and (i["x"], i["y"]) == LETRERO[0] and iv.get("Sprite") == "senaletica/salida_emergencia":
            i["x"], i["y"] = LETRERO[1]; cambios.append("mueve letrero de salida")
        inst.append(i)
    J["instances"] = inst

    # monedas: solo en modo Jefe; en escape ese 45 % da galletas
    for e in walk(J["events"]):
        acts = e.get("actions", [])
        if not any(a["type"]["value"] == "Create" and a["parameters"][1:2] == ["Moneda"] for a in acts):
            continue
        if any(c["type"]["value"] == "VarScene" and c["parameters"][:1] == ["Jefe"] for c in e.get("conditions", [])):
            continue                                                 # ya aplicado
        rango = [copy.deepcopy(c) for c in e["conditions"]]
        e["conditions"].append({"type": {"inverted": False, "value": "VarScene"}, "parameters": ["Jefe", "=", "1"]})
        padre = next(p for p in walk(J["events"]) if e in p.get("events", []))
        k = padre["events"].index(e)
        galletas = {"type": "BuiltinCommonInstructions::Standard",
                    "conditions": rango + [{"type": {"inverted": False, "value": "VarScene"},
                                            "parameters": ["Jefe", "!=", "1"]}],
                    "actions": [{"type": {"value": "Create"}, "parameters": ["", "Comida", "Contenedor.X() + 24", "Contenedor.Y() + 40", "\"Juego\""]},
                                {"type": {"value": "SetAnimationName"}, "parameters": ["Comida", "\"galletas\""]},
                                {"type": {"value": "ModVarObjet"}, "parameters": ["Comida", "Cura", "=", "30"]}],
                    "events": []}
        marca = {"type": "BuiltinCommonInstructions::Comment",
                 "color": {"b": 109, "g": 230, "r": 255, "textB": 0, "textG": 0, "textR": 0},
                 "comment": MK + "-MONEDAS: la moneda solo sale en modo Jefe; en escape, galletas.", "comment2": ""}
        padre["events"][k + 1:k + 1] = [galletas]
        padre["events"].insert(k, marca)
        cambios.append("monedas solo en Jefe")
        break
    return cambios


def main():
    d = json.load(open(PRY, encoding="utf-8"))
    respaldo(PRY, datetime.date.today().strftime("%Y%m%d"))
    cambios = parchar_proyecto(d)
    escribir_json(PRY, d, indent=2)
    print("Proyecto:", "; ".join(cambios) if cambios else "sin cambios (ya aplicado)")
    print("Fondo:", parchar_fondo() or "sin cambios (ya aplicado)")
    for r in (os.path.join(PROY_DIR, "assets", "mapa", "mapa_fdiz_gdevelop.json"),
              os.path.join(FINAL, "mapa_fdiz_gdevelop.json"), os.path.join(FINAL, "mapa_fdiz.tmj")):
        print("Tiled", os.path.relpath(r, RAIZ) + ":", "aplicado" if parchar_tiled(r) else "sin cambios")
    print("Datos fuente (colisiones/zonas, muebles):", parchar_datos())
    print("Fase 41 aplicada.")


if __name__ == "__main__":
    main()
