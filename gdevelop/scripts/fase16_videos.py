"""Fase 16 de FDI-Z: integra los videos de videos_equipo en las escenas (reemplaza reemplazar_imagenes_por_videos.py).
Correr con GDevelop cerrado:   python fase16_videos.py <FDI-Z.json>
Es idempotente: quita lo que puso una corrida anterior (objetos Vid*, recursos vid_*, eventos del grupo "Videos") y lo vuelve a poner.

Notas técnicas (por qué falló el intento anterior):
 - Las acciones del objeto video son "Video::Play" / "Video::Pause" (no "Video::VideoObject::Play").
 - El renderer del objeto video IGNORA Montre/Cache (hidden). Para ocultarlo se usa Opacity 0 + Pause.
 - Un objeto video = un archivo; no se cambia de video por animación. Por eso hay un objeto por video y se activa solo el que toca.
 - Los sprites originales se conservan (solo se ocultan con Cache) por si hay que revertir.
Volumen: personajes (04-11) 35, todo lo demás 10. Todos en bucle."""
import json, os, sys, shutil, time, uuid
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gd_util import c, a, ev, comentario, grupo, var

ruta = sys.argv[1]
RAIZ = os.path.dirname(os.path.abspath(ruta))
resp = os.path.join(os.path.dirname(RAIZ), "respaldos")
os.makedirs(resp, exist_ok=True)
shutil.copy(ruta, os.path.join(resp, f"FDI-Z_antes_de_videos_{time.strftime('%Y%m%d_%H%M%S')}.json"))
p = json.load(open(ruta, encoding="utf-8"))
V = "assets/interfaz/videos/"
VOL_PJ, VOL = 35, 10
PJS = ["tony", "miranda", "cesar", "alan", "castillo", "alessandro", "gabo", "carlos"]
PJ_ARCH = dict(zip(PJS, ["04_personaje_tony", "05_personaje_miranda", "06_personaje_cesar", "07_personaje_alan",
                          "08_personaje_castillo", "09_personaje_alessandro", "10_personaje_gabo", "11_personaje_carlos"]))

def lay(n): return next(l for l in p["layouts"] if l["name"] == n)

def objeto_video(nombre, recurso, vol, opacidad=255):
    return {"assetStoreId": "", "name": nombre, "type": "Video::VideoObject", "variables": [], "effects": [], "behaviors": [],
            "content": {"opacity": opacidad, "loop": True, "volume": vol, "videoResource": recurso}}

def inst_video(nombre, x, y, w, h, z):
    return {"angle": 0, "customSize": True, "depth": 1, "height": h, "keepRatio": False, "layer": "", "name": nombre,
            "persistentUuid": str(uuid.uuid4()), "width": w, "x": x, "y": y, "zOrder": z,
            "numberProperties": [], "stringProperties": [], "initialVariables": [], "opacity": 255}

def limpiar(escena, nombres):
    escena["objects"] = [o for o in escena["objects"] if o["name"] not in nombres]
    escena["instances"] = [i for i in escena["instances"] if i["name"] not in nombres]
    escena["events"] = [e for e in escena["events"] if not (e.get("type", "").endswith("Group") and e.get("name") == "Videos")]

def play(o): return a("Video::Play", o)
def pause(o): return a("Video::Pause", o)
POSX = {}
FUERA = -6000   # el renderer de video ignora Montre/Cache y Opacity no es válida para Video::VideoObject: se oculta sacándolo de la pantalla
def mx(o, x): return a("MettreX", o, "=", str(x))
def suena(o): return c("Video::Play", o)  # condición: se está reproduciendo
def cvt(v, val, op="="): return c("VarSceneTxt", v, op, val)
def cvar(v, op, val): return c("VarScene", v, op, str(val))

def activar(obj, cond):
    """Si cond: visible y reproduciendo. Si no (se pasa invertido en `inactivo`): invisible y pausado."""
    return [ev(cond + [c("Video::Play", obj, invertida=True)], [play(obj)]),
            ev(cond, [mx(obj, POSX[obj])])]

def desactivar(obj, cond_inactivo):
    return [ev(cond_inactivo, [mx(obj, FUERA)]), ev(cond_inactivo + [c("Video::Play", obj)], [pause(obj)])]

def ev_visible(obj, cond_on, cond_off):
    return activar(obj, cond_on) + desactivar(obj, cond_off)

recursos = {r["name"]: r for r in p["resources"]["resources"]}
for k in [k for k in recursos if k.startswith("vid_")]:
    del recursos[k]
def res_video(nombre, archivo):
    recursos[nombre] = {"file": V + archivo, "kind": "video", "metadata": "", "name": nombre, "userAdded": True}
    return nombre

# ---------------- Título: Fondo2 (ya existía, hecho a mano) solo necesita reproducirse ----------------
T = lay("Titulo")
T["events"] = [e for e in T["events"] if not (e.get("type", "").endswith("Group") and e.get("name") == "Videos")]
T["events"].insert(0, grupo("Videos", [comentario("Video de fondo 01_titulo_v1_mejor.mp4 (objeto Fondo2, creado a mano). Se reproduce en bucle."),
                                      ev([c("DepartScene", "")], [play("Fondo2")]),
                                      ev([c("Video::Play", "Fondo2", invertida=True)], [play("Fondo2")])]))

# ---------------- Menú ----------------
M = lay("Menu")
vids_menu = ["VidFondoModos", "VidFondoSel", "VidIlusEscape", "VidIlusJefe"] + [f"VidPj_{pj}" for pj in PJS]
limpiar(M, vids_menu)
M["variables"] = [v for v in M.get("variables", []) if v["name"] not in ("VBg", "VPj")] + [var("VBg", ""), var("VPj", "")]

def nuevo(esc, nombre, archivo, vol, x, y, w, h, z):
    POSX[nombre] = x
    r = res_video("vid_" + nombre, archivo)
    esc["objects"].append(objeto_video(nombre, r, vol))
    esc["instances"].append(inst_video(nombre, x, y, w, h, z))

nuevo(M, "VidFondoModos", "12_fondo_modos.mp4", VOL, 0, 0, 1920, 1080, -1)
nuevo(M, "VidFondoSel", "13_fondo_seleccion.mp4", VOL, 0, 0, 1920, 1080, -1)
# Ilustraciones de modo: video recortado al cuadro central (1038x983 de 1920x1080) -> 340x322 como el sprite IlusModo
nuevo(M, "VidIlusEscape", "02_modo_escape_recorte.mp4", VOL, 390, 288, 340, 322, 3)
nuevo(M, "VidIlusJefe", "03_modo_jefe_recorte.mp4", VOL, 1190, 288, 340, 322, 3)
# Personaje grande (marco EqMarcoGrande 630x650 en 153,216); el video recortado 1045x1080 tiene la misma proporción
for pj in PJS:
    nuevo(M, f"VidPj_{pj}", PJ_ARCH[pj] + "_recorte.mp4", VOL_PJ, 153, 216, 630, 650, 4)

EV = [comentario("Videos de las pantallas del menú. Un objeto por video: se muestra solo el que toca (Opacity) y los demás se pausan. "
                 "VBg = fondo según el paso; VPj = personaje en foco mientras se elige equipo. Los sprites originales solo se ocultan.")]
EV += [ev([cvt("Paso", '"modo"')], [a("ModVarSceneTxt", "VBg", "=", '"modo"')]),
       ev([cvt("Paso", '"dificultad"')], [a("ModVarSceneTxt", "VBg", "=", '"modo"')]),
       ev([cvt("Paso", '"unirse"')], [a("ModVarSceneTxt", "VBg", "=", '"sel"')]),
       ev([cvt("Paso", '"equipo"')], [a("ModVarSceneTxt", "VBg", "=", '"sel"')]),
       ev([cvt("Paso", '"equipo"')], [a("ModVarSceneTxt", "VPj", "=", "VariableString(KF)")]),
       ev([cvt("Paso", '"equipo"', "!=")], [a("ModVarSceneTxt", "VPj", "=", '""')]),
       ev([], [a("Cache", "Fondo"), a("Cache", "IlusModo"), a("Cache", "EqCuerpo"), a("Cache", "EqFoco")])]
EV += ev_visible("VidFondoModos", [cvt("VBg", '"modo"')], [cvt("VBg", '"modo"', "!=")])
EV += ev_visible("VidFondoSel", [cvt("VBg", '"sel"')], [cvt("VBg", '"sel"', "!=")])
for obj in ("VidIlusEscape", "VidIlusJefe"):
    EV += ev_visible(obj, [cvt("Paso", '"modo"')], [cvt("Paso", '"modo"', "!=")])
for pj in PJS:
    EV += ev_visible(f"VidPj_{pj}", [cvt("VPj", f'"{pj}"')], [cvt("VPj", f'"{pj}"', "!=")])
M["events"].append(grupo("Videos", EV))

# ---------------- Resultados ----------------
R = lay("Resultados")
limpiar(R, ["VidVictoria", "VidDerrota"])
nuevo(R, "VidVictoria", "15_victoria.mp4", VOL, 0, 0, 1920, 1080, -1)
nuevo(R, "VidDerrota", "16_derrota.mp4", VOL, 0, 0, 1920, 1080, -1)
gan = c("VarGlobalTxt", "Resultado", "=", '"victoria"')
per = c("VarGlobalTxt", "Resultado", "!=", '"victoria"')
ER = [comentario("Video de fondo según el resultado. El sprite Fondo original solo se oculta."), ev([], [a("Cache", "Fondo")])]
ER += ev_visible("VidVictoria", [gan], [per]) + ev_visible("VidDerrota", [per], [gan])
R["events"].append(grupo("Videos", ER))

p["resources"]["resources"] = list(recursos.values())
json.dump(p, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("OK: videos integrados en Titulo, Menu y Resultados")
