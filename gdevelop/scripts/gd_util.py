"""Utilidades para generar partes del proyecto GDevelop de FDI-Z (formato 5.6)."""
import json, uuid

def res_imagen(nombre, archivo):
    return {"file": archivo, "kind": "image", "metadata": "", "name": nombre,
            "smoothed": False, "userAdded": True}

def var(nombre, valor):
    t = "number" if isinstance(valor, (int, float)) and not isinstance(valor, bool) else \
        "boolean" if isinstance(valor, bool) else "string"
    return {"name": nombre, "type": t, "value": valor}

def cuadro(imagen, origen, mascara=None):
    s = {"hasCustomCollisionMask": mascara is not None, "image": imagen, "points": [],
         "originPoint": {"name": "origine", "x": origen[0], "y": origen[1]},
         "centerPoint": {"automatic": True, "name": "centre", "x": 0, "y": 0},
         "customCollisionMask": []}
    if mascara:
        x0, y0, x1, y1 = mascara
        s["customCollisionMask"] = [[{"x": x0, "y": y0}, {"x": x1, "y": y0},
                                     {"x": x1, "y": y1}, {"x": x0, "y": y1}]]
    return s

def animacion(nombre, imagenes, fps, loop, origen, mascara=None):
    return {"name": nombre, "useMultipleDirections": False,
            "directions": [{"looping": bool(loop), "timeBetweenFrames": round(1.0 / fps, 4),
                            "sprites": [cuadro(i, origen, mascara) for i in imagenes]}]}

def objeto_sprite(nombre, animaciones, variables=(), comportamientos=()):
    return {"adaptCollisionMaskAutomatically": False, "assetStoreId": "", "name": nombre,
            "type": "Sprite", "updateIfNotVisible": False,
            "variables": list(variables), "effects": [], "behaviors": list(comportamientos),
            "animations": animaciones}

def instancia(nombre, x, y, capa, z=0, w=None, h=None, variables=()):
    i = {"angle": 0, "customSize": w is not None, "height": h or 0, "layer": capa,
         "name": nombre, "persistentUuid": str(uuid.uuid4()), "width": w or 0,
         "x": x, "y": y, "zOrder": z, "numberProperties": [], "stringProperties": [],
         "initialVariables": list(variables)}
    return i

def capa(nombre, sigue_camara=True, luz=False, ambiente=(200, 200, 200), visible=True):
    return {"ambientLightColorB": ambiente[2], "ambientLightColorG": ambiente[1],
            "ambientLightColorR": ambiente[0], "camera2DPlaneMaxDrawingDistance": 5000,
            "camera3DFarPlaneDistance": 10000, "camera3DFieldOfView": 45,
            "camera3DNearPlaneDistance": 3, "cameraType": "",
            "followBaseLayerCamera": sigue_camara, "isLightingLayer": luz,
            "isLocked": False, "name": nombre, "renderingType": "", "visibility": visible,
            "cameras": [{"defaultSize": True, "defaultViewport": True, "height": 0,
                         "viewportBottom": 1, "viewportLeft": 0, "viewportRight": 1,
                         "viewportTop": 0, "width": 0}],
            "effects": []}

# ---- eventos ----
def c(tipo, *params, invertida=False):
    return {"type": {"inverted": invertida, "value": tipo}, "parameters": list(params)}

def a(tipo, *params):
    return {"type": {"value": tipo}, "parameters": list(params)}

def ev(condiciones, acciones, sub=None):
    e = {"type": "BuiltinCommonInstructions::Standard",
         "conditions": condiciones, "actions": acciones}
    if sub:
        e["events"] = sub
    return e

def comentario(texto):
    return {"type": "BuiltinCommonInstructions::Comment",
            "color": {"b": 109, "g": 230, "r": 255, "textB": 0, "textG": 0, "textR": 0},
            "comment": texto, "comment2": ""}

def grupo(nombre, eventos, color=(74, 176, 228)):
    return {"type": "BuiltinCommonInstructions::Group", "colorB": color[2],
            "colorG": color[1], "colorR": color[0], "creationTime": 0, "name": nombre,
            "source": "", "events": eventos, "parameters": []}
