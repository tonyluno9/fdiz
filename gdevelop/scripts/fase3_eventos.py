"""Fase 3: eventos del mapa (choques, puertas, cámara limitada) y quita el piso de prueba.
Uso: python fase3_eventos.py <FDI-Z.json>   (re-ejecutable)
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gd_util import *

ruta = sys.argv[1]
p = json.load(open(ruta, encoding="utf-8"))
esc = next(l for l in p["layouts"] if l["name"] == "Juego")

# fuera el piso de prueba de la fase 2
esc["objects"] = [o for o in esc["objects"] if o["name"] != "PisoPrueba"]
esc["instances"] = [i for i in esc["instances"] if i["name"] != "PisoPrueba"]
p["resources"]["resources"] = [r for r in p["resources"]["resources"]
                               if r["name"] != "provisional/piso_prueba.png"]

ANCHO, ALTO = 8768, 5376
NOMBRES = {"Mapa: ayudas y choques", "Puertas (fase 3: abrir con F)", "Orden por Y y cámara"}
evs = [e for e in esc["events"] if e.get("name") not in NOMBRES]

mapa = grupo("Mapa: ayudas y choques", [
    comentario("Muro, ChoqueMueble y Marcador solo se ven en el editor. La capa Niebla se activa en la fase 6."),
    comentario("El piso se dibuja con MapaFondo (pedazos de mapa_fdiz_completo.png). El Tilemap 'Mapa' "
               "se oculta porque en la vista previa de GDevelop 5.6.287 sale casi negro."),
    ev([c("DepartScene", "")], [a("Cache", "Mapa"), a("Cache", "Muro"), a("Cache", "ChoqueMueble"),
                                a("Cache", "Marcador"),
                                a("HideLayer", "", "\"Niebla\"")]),
    ev([], [a("SeparateFromObjects", "Tony", "Solidos", "")]),
])

puertas = grupo("Puertas (fase 3: abrir con F)", [
    comentario("Mantener F junto a una puerta: normal 1 s, electrónica 8 s. Las restringidas no se abren "
               "con F (Carlos, llave o tumbarla: fase 6)."),
    {"type": "BuiltinCommonInstructions::ForEach", "object": "Puerta",
     "conditions": [], "actions": [], "events": [
        ev([c("KeyPressed", "", "f"),
            c("BuiltinCommonInstructions::CompareNumbers", "Tony.Distance(Puerta)", "<", "90"),
            c("VarObjet", "Puerta", "TiempoAbrir", ">", "0")],
           [a("ModVarObjet", "Puerta", "Progreso", "+", "TimeDelta()")], sub=[
            ev([c("BuiltinCommonInstructions::CompareNumbers", "Puerta.Variable(Progreso)", ">=",
                  "Puerta.Variable(TiempoAbrir)")],
               [a("Delete", "Puerta", "")]),
        ]),
    ]},
    ev([c("KeyPressed", "", "f", invertida=True)], [a("ModVarObjet", "Puerta", "Progreso", "=", "0")]),
])

camara = grupo("Orden por Y y cámara", [
    ev([], [a("ChangePlan", "Tony", "=", "Tony.Y()")]),
    ev([c("DepartScene", "")], [a("CameraX", "", "=", "Tony.X()", "", ""),
                                a("CameraY", "", "=", "Tony.Y() - 48", "", "")]),
    ev([], [a("CameraX", "", "=", "CameraX() + (Tony.X() - CameraX()) * min(1, 8 * TimeDelta())", "", ""),
            a("CameraY", "", "=", "CameraY() + (Tony.Y() - 48 - CameraY()) * min(1, 8 * TimeDelta())", "", ""),
            a("CameraX", "", "=", f"clamp(CameraX(), 960, {ANCHO - 960})", "", ""),
            a("CameraY", "", "=", f"clamp(CameraY(), 540, {ALTO - 540})", "", "")]),
])

# orden: comentario, depuración, movimiento, animación, mapa, puertas, cámara
evs += [mapa, puertas, camara]
esc["events"] = evs
json.dump(p, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("OK eventos fase 3:", [e.get("name", e.get("comment", "")[:20]) for e in evs])
