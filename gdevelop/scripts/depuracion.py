"""Agrega (o reemplaza) el grupo de eventos de depuración en la escena Juego.
Piloto automático para probar animaciones: I/J/K/L = caminar solo hacia arriba/izq/abajo/der, O = parar.
Uso: python depuracion.py <FDI-Z.json> [--quitar]
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from gd_util import *

ruta = sys.argv[1]
quitar = "--quitar" in sys.argv
p = json.load(open(ruta, encoding="utf-8"))
esc = next(l for l in p["layouts"] if l["name"] == "Juego")
NOMBRE = "Depuración (quitar antes de presentar)"
esc["events"] = [e for e in esc["events"] if e.get("name") != NOMBRE]
esc["variables"] = [v for v in esc["variables"] if v["name"] != "Piloto"]
esc["objectsFolderStructure"] = {"folderName": "__ROOT"}

if not quitar:
    esc["variables"].append(var("Piloto", ""))
    T = ("Tony", "TopDownMovement")
    teclas = {"i": "arriba", "j": "izq", "k": "abajo", "l": "der", "o": ""}
    simula = {"arriba": "SimulateUpKey", "izq": "SimulateLeftKey",
              "abajo": "SimulateDownKey", "der": "SimulateRightKey"}
    evs = [comentario("I/J/K/L: Tony camina solo hacia arriba/izquierda/abajo/derecha. O: parar.")]
    for k, d in teclas.items():
        evs.append(ev([c("KeyPressed", "", k), c("BuiltinCommonInstructions::Once")],
                      [a("ModVarSceneTxt", "Piloto", "=", f"\"{d}\"")]))
    for d, s in simula.items():
        evs.append(ev([c("VarSceneTxt", "Piloto", "=", f"\"{d}\"")],
                      [a(f"TopDownMovementBehavior::{s}", *T)]))
    esc["events"].insert(1, grupo(NOMBRE, evs, color=(200, 80, 80)))

json.dump(p, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("OK", "quitado" if quitar else "agregado")
