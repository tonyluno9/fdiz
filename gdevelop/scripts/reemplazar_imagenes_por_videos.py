"""
Script: reemplazar_imagenes_por_videos.py
Propósito: Reemplaza las imágenes estáticas de fondo e ilustraciones del proyecto
           FDI-Z con objetos de video (Video::VideoObject) en GDevelop 5.

Reglas de volumen:
  - Personajes (04-11): 35% (0.35 en GDevelop = 35)
  - Todos los demás:    10% (0.10 en GDevelop = 10)

Todos los videos están en bucle (loop = true).

Mapeo video → escena/objeto:
  01_titulo_v1_mejor.mp4   → Titulo: Fondo (1920×1080)
  02_modo_escape.mp4       → Menu: IlusModo anim "e" (340×322)
  03_modo_jefe.mp4         → Menu: IlusModo anim "j" (340×322)
  04_personaje_tony.mp4    → Menu: SelRetrato anim "tony"
  05_personaje_miranda.mp4 → Menu: SelRetrato anim "miranda"
  06_personaje_cesar.mp4   → Menu: SelRetrato anim "cesar"
  07_personaje_alan.mp4    → Menu: SelRetrato anim "alan"
  08_personaje_castillo.mp4→ Menu: SelRetrato anim "castillo"
  09_personaje_alessandro.mp4 → Menu: SelRetrato anim "alessandro"
  10_personaje_gabo.mp4    → Menu: SelRetrato anim "gabo"
  11_personaje_carlos.mp4  → Menu: SelRetrato anim "carlos"
  12_fondo_modos.mp4       → Menu: Fondo anim "modo" (1920×1080)
  13_fondo_seleccion.mp4   → Menu: Fondo anim "sel" (1920×1080)
  14_fondo_tienda.mp4      → Juego: FondoTienda (1920×1080, nuevo)
  15_victoria.mp4          → Resultados: Fondo anim "v" (1920×1080)
  16_derrota.mp4           → Resultados: Fondo anim "d" (1920×1080)
"""

import json
import copy
import uuid
import sys
from pathlib import Path

PROJECT_PATH = Path(__file__).parent.parent / "FDI-Z" / "FDI-Z.json"
VIDEO_DIR = "assets/interfaz/videos"

# Volumen según video (GDevelop: 0–100)
VOLUMEN_PERSONAJE = 35   # videos 04–11
VOLUMEN_DEFAULT   = 10   # todos los demás

# ───────────────────────────────────────────────
# Helpers
# ───────────────────────────────────────────────

def nuevo_uuid():
    return str(uuid.uuid4())

def recurso_video(nombre_res, archivo_mp4):
    """Devuelve un dict de recurso tipo video para la sección resources."""
    return {
        "file": f"{VIDEO_DIR}/{archivo_mp4}",
        "kind": "video",
        "metadata": "",
        "name": nombre_res,
        "userAdded": True
    }

def objeto_video(nombre_obj, nombre_res, volumen, loop=True):
    """Devuelve un dict de objeto Video::VideoObject."""
    return {
        "adaptCollisionMaskAutomatically": False,
        "assetStoreId": "",
        "name": nombre_obj,
        "type": "Video::VideoObject",
        "updateIfNotVisible": False,
        "variables": [],
        "effects": [],
        "behaviors": [],
        "content": {
            "loop": loop,
            "muted": False,
            "volume": volumen,
            "videoResource": nombre_res
        }
    }

def instancia_video(nombre_obj, x, y, ancho, alto, z_order, capa="", extra_vars=None):
    """Devuelve una instancia de un objeto de video."""
    inst = {
        "angle": 0,
        "customSize": True,
        "height": alto,
        "layer": capa,
        "name": nombre_obj,
        "persistentUuid": nuevo_uuid(),
        "width": ancho,
        "x": x,
        "y": y,
        "zOrder": z_order,
        "numberProperties": [],
        "stringProperties": [],
        "initialVariables": extra_vars or []
    }
    return inst

def insertar_objeto_al_frente(escena, obj):
    """Inserta el objeto al principio de la lista de objetos de la escena."""
    escena["objects"].insert(0, obj)

def insertar_objeto_al_final(escena, obj):
    """Inserta el objeto al final de la lista de objetos de la escena."""
    escena["objects"].append(obj)

def insertar_instancia_zorder_bajo(escena, inst):
    """Inserta la instancia al principio de instances (z-order bajo)."""
    escena["instances"].insert(0, inst)

# ───────────────────────────────────────────────
# Eventos de control para videos
# ───────────────────────────────────────────────

def evento_iniciar_video(nombre_obj):
    """Evento: al iniciar la escena, reproduce el video."""
    return {
        "type": "BuiltinCommonInstructions::Standard",
        "conditions": [
            {
                "type": {"inverted": False, "value": "DepartScene"},
                "parameters": [""]
            }
        ],
        "actions": [
            {
                "type": {"value": "Video::VideoObject::Play"},
                "parameters": [nombre_obj]
            }
        ],
        "disabled": False,
        "folded": False
    }

def evento_play_siempre(nombre_obj):
    """Evento: condición vacía, siempre reproduce (para inicio automático)."""
    return {
        "type": "BuiltinCommonInstructions::Standard",
        "conditions": [],
        "actions": [
            {
                "type": {"value": "Video::VideoObject::Play"},
                "parameters": [nombre_obj]
            }
        ],
        "disabled": False,
        "folded": False
    }

def evento_play_en_depart(nombre_obj):
    """Reproduce el video en DepartScene."""
    return {
        "type": "BuiltinCommonInstructions::Standard",
        "conditions": [
            {
                "type": {"inverted": False, "value": "DepartScene"},
                "parameters": [""]
            }
        ],
        "actions": [
            {
                "type": {"value": "Video::VideoObject::Play"},
                "parameters": [nombre_obj]
            }
        ],
        "disabled": False,
        "folded": False
    }

def evento_condicional_video(condiciones, nombre_obj_mostrar, todos_los_obj):
    """
    Evento que muestra un video y oculta los demás según condición.
    'todos_los_obj' es lista de nombres de todos los videos alternativos.
    """
    acciones = []
    # Ocultar todos primero
    for obj in todos_los_obj:
        acciones.append({
            "type": {"value": "Cache"},
            "parameters": [obj]
        })
    # Mostrar y reproducir el correcto
    acciones.append({
        "type": {"value": "Montre"},
        "parameters": [nombre_obj_mostrar]
    })
    acciones.append({
        "type": {"value": "Video::VideoObject::Play"},
        "parameters": [nombre_obj_mostrar]
    })
    return {
        "type": "BuiltinCommonInstructions::Standard",
        "conditions": condiciones,
        "actions": acciones,
        "disabled": False,
        "folded": False
    }

# ───────────────────────────────────────────────
# Transformaciones por escena
# ───────────────────────────────────────────────

def transformar_titulo(data):
    """
    Escena Titulo: reemplaza Fondo (Sprite con p14_Fondo_t) 
    por FondoVideo (Video::VideoObject, 01_titulo_v1_mejor.mp4)
    """
    escena = data["layouts"][0]
    assert escena["name"] == "Titulo", f"Se esperaba Titulo, se obtuvo {escena['name']}"

    nombre_res = "vid_titulo"
    nombre_obj = "FondoVideo"
    mp4 = "01_titulo_v1_mejor.mp4"

    # 1. Registrar recurso de video
    data["resources"]["resources"].append(recurso_video(nombre_res, mp4))

    # 2. Eliminar objeto Fondo original (Sprite)
    escena["objects"] = [o for o in escena["objects"] if o["name"] != "Fondo"]

    # 3. Eliminar instancias de Fondo original
    escena["instances"] = [i for i in escena["instances"] if i.get("name") != "Fondo"]

    # 4. Agregar objeto video
    obj = objeto_video(nombre_obj, nombre_res, VOLUMEN_DEFAULT)
    escena["objects"].insert(0, obj)

    # 5. Agregar instancia (z-order 0, capa "", tamaño 1920×1080)
    inst = instancia_video(nombre_obj, 0, 0, 1920, 1080, 0)
    escena["instances"].insert(0, inst)

    # 6. Agregar evento de reproducción al inicio
    # Insertar al inicio del array de events
    ev = evento_play_en_depart(nombre_obj)
    escena["events"].insert(0, ev)

    # Actualizar objectsFolderStructure si existe
    _actualizar_folder_structure(escena, "Fondo", nombre_obj)

    print(f"  [Titulo] ✓ Fondo → {nombre_obj} ({mp4})")


def transformar_menu(data):
    """
    Escena Menu:
    - Fondo.modo → FondoModos (12_fondo_modos.mp4, 1920×1080, vol 10%)
    - Fondo.sel  → FondoSel   (13_fondo_seleccion.mp4, 1920×1080, vol 10%)
    - IlusModo.e → IlusModoEscape (02_modo_escape.mp4, 340×322, vol 10%)
    - IlusModo.j → IlusModoJefe   (03_modo_jefe.mp4, 340×322, vol 10%)
    - SelRetrato.*→ 8 videos de personajes (04-11, vol 35%)
    """
    escena = data["layouts"][1]
    assert escena["name"] == "Menu", f"Se esperaba Menu, se obtuvo {escena['name']}"

    # ---- Instancias actuales que necesitamos para posición/tamaño ----
    inst_fondo = next((i for i in escena["instances"] if i.get("name") == "Fondo"), None)
    inst_ilus = [i for i in escena["instances"] if i.get("name") == "IlusModo"]
    inst_retrato = next((i for i in escena["instances"] if i.get("name") == "SelRetrato"), None)

    # Tamaños desde las instancias existentes
    fondo_w = inst_fondo["width"] if inst_fondo else 1920
    fondo_h = inst_fondo["height"] if inst_fondo else 1080

    ilus_e_inst = inst_ilus[0] if len(inst_ilus) > 0 else None
    ilus_j_inst = inst_ilus[1] if len(inst_ilus) > 1 else None
    ilus_w = ilus_e_inst["width"] if ilus_e_inst else 340
    ilus_h = ilus_e_inst["height"] if ilus_e_inst else 322
    ilus_e_x = ilus_e_inst["x"] if ilus_e_inst else 390
    ilus_e_y = ilus_e_inst["y"] if ilus_e_inst else 288
    ilus_j_x = ilus_j_inst["x"] if ilus_j_inst else 1190
    ilus_j_y = ilus_j_inst["y"] if ilus_j_inst else 288

    ret_w = inst_retrato["width"] if inst_retrato else 128
    ret_h = inst_retrato["height"] if inst_retrato else 128
    ret_x = inst_retrato["x"] if inst_retrato else 0
    ret_y = inst_retrato["y"] if inst_retrato else 0
    ret_z = inst_retrato["zOrder"] if inst_retrato else 5

    # ======== FONDOS MODO / SEL ========

    videos_fondo = [
        ("vid_fondo_modos", "FondoModos", "12_fondo_modos.mp4"),
        ("vid_fondo_sel",   "FondoSel",   "13_fondo_seleccion.mp4"),
    ]
    for nombre_res, nombre_obj, mp4 in videos_fondo:
        data["resources"]["resources"].append(recurso_video(nombre_res, mp4))
        obj = objeto_video(nombre_obj, nombre_res, VOLUMEN_DEFAULT)
        escena["objects"].insert(0, obj)
        inst = instancia_video(nombre_obj, 0, 0, 1920, 1080, 0)
        escena["instances"].insert(0, inst)
        print(f"  [Menu] ✓ Fondo ({mp4.split('_')[0]}) → {nombre_obj}")

    # Eliminar objeto Fondo original y sus instancias
    escena["objects"] = [o for o in escena["objects"] if o["name"] != "Fondo"]
    # Eliminar instancias Fondo pero no las nuevas
    escena["instances"] = [i for i in escena["instances"]
                           if not (i.get("name") == "Fondo")]

    # ======== ILUSTRACIONES DE MODO ========

    videos_ilus = [
        ("vid_modo_escape", "IlusModoEscape", "02_modo_escape.mp4",
         ilus_e_x, ilus_e_y, ilus_w, ilus_h, 3, 0),
        ("vid_modo_jefe",   "IlusModoJefe",   "03_modo_jefe.mp4",
         ilus_j_x, ilus_j_y, ilus_w, ilus_h, 3, 1),
    ]
    for nombre_res, nombre_obj, mp4, ix, iy, iw, ih, iz, idx in videos_ilus:
        data["resources"]["resources"].append(recurso_video(nombre_res, mp4))
        obj = objeto_video(nombre_obj, nombre_res, VOLUMEN_DEFAULT)
        escena["objects"].append(obj)
        inst = instancia_video(nombre_obj, ix, iy, iw, ih, iz,
                               extra_vars=[{"name":"Idx","type":"number","value":idx}])
        escena["instances"].append(inst)
        print(f"  [Menu] ✓ IlusModo ({mp4}) → {nombre_obj}")

    # Eliminar IlusModo Sprite original y sus instancias
    escena["objects"] = [o for o in escena["objects"] if o["name"] != "IlusModo"]
    escena["instances"] = [i for i in escena["instances"] if i.get("name") != "IlusModo"]

    # ======== RETRATOS DE PERSONAJES ========

    personajes = [
        ("tony",        "04_personaje_tony.mp4"),
        ("miranda",     "05_personaje_miranda.mp4"),
        ("cesar",       "06_personaje_cesar.mp4"),
        ("alan",        "07_personaje_alan.mp4"),
        ("castillo",    "08_personaje_castillo.mp4"),
        ("alessandro",  "09_personaje_alessandro.mp4"),
        ("gabo",        "10_personaje_gabo.mp4"),
        ("carlos",      "11_personaje_carlos.mp4"),
    ]

    for pj_nombre, mp4 in personajes:
        nombre_res = f"vid_personaje_{pj_nombre}"
        nombre_obj = f"RetratoPJ_{pj_nombre}"
        data["resources"]["resources"].append(recurso_video(nombre_res, mp4))
        obj = objeto_video(nombre_obj, nombre_res, VOLUMEN_PERSONAJE)
        escena["objects"].append(obj)
        # Instancia en la misma posición que SelRetrato, oculto por defecto
        inst = instancia_video(nombre_obj, ret_x, ret_y, ret_w, ret_h, ret_z,
                               extra_vars=[{"name":"Personaje","type":"string","value":pj_nombre}])
        escena["instances"].append(inst)
        print(f"  [Menu] ✓ SelRetrato.{pj_nombre} → {nombre_obj} ({mp4})")

    # Eliminar SelRetrato Sprite original y sus instancias
    escena["objects"] = [o for o in escena["objects"] if o["name"] != "SelRetrato"]
    escena["instances"] = [i for i in escena["instances"] if i.get("name") != "SelRetrato"]

    # ======== EVENTOS ========

    # Evento: al entrar a la escena, reproducir todos los videos de fondo
    # (los de personaje serán controlados por los eventos existentes de selección)
    todos_fondos = ["FondoModos", "FondoSel"]
    todos_ilus   = ["IlusModoEscape", "IlusModoJefe"]
    todos_pj     = [f"RetratoPJ_{n}" for n, _ in personajes]

    # Eventos de reproducción de fondos y ilus al iniciar
    ev_inicio = {
        "type": "BuiltinCommonInstructions::Standard",
        "conditions": [
            {"type": {"inverted": False, "value": "DepartScene"}, "parameters": [""]}
        ],
        "actions": [
            {"type": {"value": "Video::VideoObject::Play"}, "parameters": [obj_n]}
            for obj_n in todos_fondos + todos_ilus + todos_pj
        ],
        "disabled": False,
        "folded": False
    }
    escena["events"].insert(0, ev_inicio)

    # Adaptar los eventos existentes que cambian animación de Fondo:
    # Buscar eventos que hacen SetAnimationName en Fondo → reemplazar por
    # mostrar/ocultar los videos de fondo correspondientes.
    _adaptar_eventos_fondo_menu(escena, todos_fondos)

    # Adaptar eventos de IlusModo
    _adaptar_eventos_iludo_menu(escena)

    # Adaptar eventos de SelRetrato → videos de personajes
    _adaptar_eventos_retrato_menu(escena, personajes)

    # Limpiar objectsFolderStructure
    _actualizar_folder_structure(escena, "Fondo", "FondoModos")
    _actualizar_folder_structure(escena, "IlusModo", "IlusModoEscape")
    _actualizar_folder_structure(escena, "SelRetrato", "RetratoPJ_tony")


def _adaptar_eventos_fondo_menu(escena, todos_fondos):
    """
    Reemplaza acciones SetAnimationName en Fondo con acciones de show/hide para videos.
    Fondo.modo → mostrar FondoModos, ocultar FondoSel
    Fondo.sel  → mostrar FondoSel,   ocultar FondoModos
    """
    for ev in escena.get("events", []):
        acciones = ev.get("actions", [])
        nuevas_acciones = []
        cambio = False
        for accion in acciones:
            tipo = accion.get("type", {}).get("value", "")
            params = accion.get("parameters", [])
            if tipo == "SetAnimationName" and len(params) >= 2 and params[0] == "Fondo":
                anim = params[1].strip('"')
                cambio = True
                if anim == "modo":
                    # Mostrar FondoModos, ocultar FondoSel
                    nuevas_acciones.append({"type": {"value": "Montre"}, "parameters": ["FondoModos"]})
                    nuevas_acciones.append({"type": {"value": "Cache"},  "parameters": ["FondoSel"]})
                    nuevas_acciones.append({"type": {"value": "Video::VideoObject::Play"}, "parameters": ["FondoModos"]})
                elif anim == "sel":
                    # Mostrar FondoSel, ocultar FondoModos
                    nuevas_acciones.append({"type": {"value": "Cache"},  "parameters": ["FondoModos"]})
                    nuevas_acciones.append({"type": {"value": "Montre"}, "parameters": ["FondoSel"]})
                    nuevas_acciones.append({"type": {"value": "Video::VideoObject::Play"}, "parameters": ["FondoSel"]})
                else:
                    nuevas_acciones.append(accion)
            else:
                nuevas_acciones.append(accion)
        if cambio:
            ev["actions"] = nuevas_acciones
            print(f"  [Menu] ✓ Evento adaptado: Fondo.SetAnimationName → show/hide video")


def _adaptar_eventos_iludo_menu(escena):
    """
    Reemplaza acciones SetAnimationName en IlusModo con show/hide de videos.
    """
    for ev in escena.get("events", []):
        acciones = ev.get("actions", [])
        nuevas_acciones = []
        cambio = False
        for accion in acciones:
            tipo = accion.get("type", {}).get("value", "")
            params = accion.get("parameters", [])
            if tipo == "SetAnimationName" and len(params) >= 2 and params[0] == "IlusModo":
                anim = params[1].strip('"')
                cambio = True
                if anim == "e":
                    nuevas_acciones.append({"type": {"value": "Montre"}, "parameters": ["IlusModoEscape"]})
                    nuevas_acciones.append({"type": {"value": "Cache"},  "parameters": ["IlusModoJefe"]})
                    nuevas_acciones.append({"type": {"value": "Video::VideoObject::Play"}, "parameters": ["IlusModoEscape"]})
                elif anim == "j":
                    nuevas_acciones.append({"type": {"value": "Cache"},  "parameters": ["IlusModoEscape"]})
                    nuevas_acciones.append({"type": {"value": "Montre"}, "parameters": ["IlusModoJefe"]})
                    nuevas_acciones.append({"type": {"value": "Video::VideoObject::Play"}, "parameters": ["IlusModoJefe"]})
                else:
                    nuevas_acciones.append(accion)
            else:
                nuevas_acciones.append(accion)
        if cambio:
            ev["actions"] = nuevas_acciones
            print(f"  [Menu] ✓ Evento adaptado: IlusModo.SetAnimationName → show/hide video")


def _adaptar_eventos_retrato_menu(escena, personajes):
    """
    Reemplaza acciones SetAnimationName en SelRetrato con show/hide de videos de personajes.
    """
    nombre_a_obj = {nombre: f"RetratoPJ_{nombre}" for nombre, _ in personajes}
    todos_pj = list(nombre_a_obj.values())

    for ev in escena.get("events", []):
        acciones = ev.get("actions", [])
        nuevas_acciones = []
        cambio = False
        for accion in acciones:
            tipo = accion.get("type", {}).get("value", "")
            params = accion.get("parameters", [])
            if tipo == "SetAnimationName" and len(params) >= 2 and params[0] == "SelRetrato":
                anim = params[1].strip('"')
                cambio = True
                obj_video = nombre_a_obj.get(anim)
                if obj_video:
                    # Ocultar todos, mostrar el correcto
                    for pj_obj in todos_pj:
                        nuevas_acciones.append({"type": {"value": "Cache"}, "parameters": [pj_obj]})
                    nuevas_acciones.append({"type": {"value": "Montre"}, "parameters": [obj_video]})
                    nuevas_acciones.append({"type": {"value": "Video::VideoObject::Play"}, "parameters": [obj_video]})
                else:
                    nuevas_acciones.append(accion)
            else:
                nuevas_acciones.append(accion)
        if cambio:
            ev["actions"] = nuevas_acciones
            print(f"  [Menu] ✓ Evento adaptado: SelRetrato.SetAnimationName → show/hide video personaje")


def transformar_resultados(data):
    """
    Escena Resultados: reemplaza Fondo (con animaciones v/d) por
    dos video objects: FondoVictoria y FondoDerrota.
    """
    escena = data["layouts"][3]
    assert escena["name"] == "Resultados", f"Se esperaba Resultados, se obtuvo {escena['name']}"

    inst_fondo = next((i for i in escena["instances"] if i.get("name") == "Fondo"), None)
    fondo_w = inst_fondo["width"]  if inst_fondo else 1920
    fondo_h = inst_fondo["height"] if inst_fondo else 1080

    videos_res = [
        ("vid_victoria", "FondoVictoria", "15_victoria.mp4"),
        ("vid_derrota",  "FondoDerrota",  "16_derrota.mp4"),
    ]
    for nombre_res, nombre_obj, mp4 in videos_res:
        data["resources"]["resources"].append(recurso_video(nombre_res, mp4))
        obj = objeto_video(nombre_obj, nombre_res, VOLUMEN_DEFAULT)
        escena["objects"].insert(0, obj)
        inst = instancia_video(nombre_obj, 0, 0, fondo_w, fondo_h, 0)
        escena["instances"].insert(0, inst)
        print(f"  [Resultados] ✓ Fondo.{mp4.split('_')[0]} → {nombre_obj}")

    # Eliminar Fondo Sprite original y sus instancias
    escena["objects"]  = [o for o in escena["objects"]  if o["name"] != "Fondo"]
    escena["instances"] = [i for i in escena["instances"] if i.get("name") != "Fondo"]

    # Adaptar eventos: SetAnimationName Fondo "v"/"d" → show/hide video
    todos_res = ["FondoVictoria", "FondoDerrota"]
    for ev in escena.get("events", []):
        acciones = ev.get("actions", [])
        nuevas = []
        cambio = False
        for accion in acciones:
            tipo   = accion.get("type", {}).get("value", "")
            params = accion.get("parameters", [])
            if tipo == "SetAnimationName" and len(params) >= 2 and params[0] == "Fondo":
                anim = params[1].strip('"')
                cambio = True
                if anim == "v":
                    nuevas.append({"type": {"value": "Cache"},  "parameters": ["FondoDerrota"]})
                    nuevas.append({"type": {"value": "Montre"}, "parameters": ["FondoVictoria"]})
                    nuevas.append({"type": {"value": "Video::VideoObject::Play"}, "parameters": ["FondoVictoria"]})
                elif anim == "d":
                    nuevas.append({"type": {"value": "Cache"},  "parameters": ["FondoVictoria"]})
                    nuevas.append({"type": {"value": "Montre"}, "parameters": ["FondoDerrota"]})
                    nuevas.append({"type": {"value": "Video::VideoObject::Play"}, "parameters": ["FondoDerrota"]})
                else:
                    nuevas.append(accion)
            else:
                nuevas.append(accion)
        if cambio:
            ev["actions"] = nuevas
            print(f"  [Resultados] ✓ Evento adaptado: Fondo.SetAnimationName → show/hide video")

    # Evento de inicio: reproducir ambos para que el bucle empiece, se ocultará el incorrecto después
    ev_inicio = {
        "type": "BuiltinCommonInstructions::Standard",
        "conditions": [
            {"type": {"inverted": False, "value": "DepartScene"}, "parameters": [""]}
        ],
        "actions": [
            {"type": {"value": "Video::VideoObject::Play"}, "parameters": ["FondoVictoria"]},
            {"type": {"value": "Video::VideoObject::Play"}, "parameters": ["FondoDerrota"]},
        ],
        "disabled": False,
        "folded": False
    }
    escena["events"].insert(0, ev_inicio)

    _actualizar_folder_structure(escena, "Fondo", "FondoVictoria")
    print(f"  [Resultados] ✓ Transformación completa")


def agregar_fondo_tienda(data):
    """
    Agrega FondoTienda como objeto global (disponible en todas las escenas)
    o lo agrega a la escena Juego como pendiente.
    Como bg_tienda.png no está asignado a ninguna escena aún, se agrega
    como objeto en escena Juego con visibilidad oculta para uso futuro,
    y se documenta como pendiente de asignar a la escena de tienda.
    """
    # Agregar recurso
    data["resources"]["resources"].append(
        recurso_video("vid_fondo_tienda", "14_fondo_tienda.mp4")
    )

    # Agregar como objeto global del proyecto
    obj = objeto_video("FondoTienda", "vid_fondo_tienda", VOLUMEN_DEFAULT)
    # En GDevelop, los objetos globales van en data["objects"]
    data["objects"].append(obj)
    print(f"  [Global] ✓ FondoTienda (14_fondo_tienda.mp4) agregado como objeto global (pendiente de asignar a escena de tienda)")


def _actualizar_folder_structure(escena, nombre_viejo, nombre_nuevo):
    """Actualiza objectsFolderStructure reemplazando referencias al objeto viejo."""
    folder = escena.get("objectsFolderStructure", {})
    if not folder:
        return
    _reemplazar_en_folder(folder, nombre_viejo, nombre_nuevo)


def _reemplazar_en_folder(node, nombre_viejo, nombre_nuevo):
    if isinstance(node, dict):
        if node.get("objectName") == nombre_viejo:
            node["objectName"] = nombre_nuevo
        for v in node.values():
            _reemplazar_en_folder(v, nombre_viejo, nombre_nuevo)
    elif isinstance(node, list):
        for item in node:
            _reemplazar_en_folder(item, nombre_viejo, nombre_nuevo)


# ───────────────────────────────────────────────
# Main
# ───────────────────────────────────────────────

def main():
    print(f"Cargando proyecto: {PROJECT_PATH}")
    with open(PROJECT_PATH, encoding="utf-8") as f:
        data = json.load(f)

    print("\n── Escena: Titulo ──")
    transformar_titulo(data)

    print("\n── Escena: Menu ──")
    transformar_menu(data)

    print("\n── Escena: Resultados ──")
    transformar_resultados(data)

    print("\n── Video de tienda (global) ──")
    agregar_fondo_tienda(data)

    # Guardar
    print(f"\nGuardando {PROJECT_PATH} ...")
    with open(PROJECT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("\n✅ Listo. Todos los videos han sido configurados.")
    print("   • Videos 04-11 (personajes): volumen 35%")
    print("   • Todos los demás: volumen 10%")
    print("   • Todos en bucle (loop: true)")
    print("   • FondoTienda: objeto global pendiente de asignar a escena de tienda")


if __name__ == "__main__":
    main()
