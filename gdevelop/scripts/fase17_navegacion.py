"""Fase 17 de FDI-Z: navegación A* (zombis, bots, guía), puertas que sí se abren y zonas que se descubren.
Correr con GDevelop cerrado, DESPUÉS de fase16_videos.py:   python fase17_navegacion.py <FDI-Z.json>
Idempotente: quita lo que puso una corrida anterior y lo vuelve a poner.

1) Evento JavaScript (primero de la escena Juego) con scripts/nav_astar.js: sustituye el buscador de rutas del behavior Pathfinding
   (moveTo) y su avance (doStepPreEvents). Todo lo existente (SetDestination, PathFound, NextNodeX...) sigue funcionando.
2) Puertas: se restauran "Usar junto a la puerta" (todos los controles y bots), golpes de jugadores/zombis y el descubrimiento de
   zonas (ZonasAbiertas) que dejó de funcionar al quitar la lógica original. R (teclado) sigue abriendo.
3) Se desactiva el empuje directo de zombis hacia el jugador cuando no hay ruta (los pegaba contra las paredes)."""
import json, os, sys, shutil, time, copy
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gd_util import c, a, ev, comentario

ruta = sys.argv[1]
RAIZ = os.path.dirname(os.path.abspath(ruta))
resp = os.path.join(os.path.dirname(RAIZ), "respaldos")
os.makedirs(resp, exist_ok=True)
shutil.copy(ruta, os.path.join(resp, f"FDI-Z_antes_de_navegacion_{time.strftime('%Y%m%d_%H%M%S')}.json"))
p = json.load(open(ruta, encoding="utf-8"))
J = next(l for l in p["layouts"] if l["name"] == "Juego")
MARCA = "FDIZ-NAV"

# ---------------------------------------------------------------- 1) JavaScript
modulo = open(os.path.join(HERE, "nav_astar.js"), encoding="utf-8").read()
GLUE = r"""
const NAV = gdjs.fdizNav;
const scn = runtimeScene;
const rectsDe = (n) => { const l = scn.getObjects(n) || []; const r = []; for (const o of l) { const b = o.getAABB(); r.push([b.min[0], b.min[1], b.max[0], b.max[1]]); } return r; };
// rejilla nueva al empezar la escena
if (NAV.scene !== scn) {
  NAV.scene = scn;
  NAV.setup(rectsDe("Muro").concat(rectsDe("ChoqueMueble")), rectsDe("Puerta"));
  NAV.doorN = (scn.getObjects("Puerta") || []).length; NAV.doorCheck = 0;
}
// presupuesto de expansiones A* por cuadro y puertas (cambian al abrirse)
NAV.budget = 90000;
NAV.doorCheck -= scn.getElapsedTime() / 1000;
if (NAV.doorCheck <= 0) {
  NAV.doorCheck = 0.4;
  const n = (scn.getObjects("Puerta") || []).length;
  if (n !== NAV.doorN) { NAV.doorN = n; NAV.setDoors(rectsDe("Puerta")); }
}
// parches al behavior Pathfinding (una sola vez)
if (!NAV.patched) {
  NAV.patched = true;
  const P = gdjs.PathfindingRuntimeBehavior.prototype;
  const origMove = P.moveTo, origStep = P.doStepPreEvents;
  P.moveTo = function (container, x, y) {
    const o = this.owner;
    if (!NAV.grid || !NAV.scene) return origMove.call(this, container, x, y);
    const now = NAV.scene.getTimeManager().getTimeFromStart() / 1000;
    const gc = NAV.cellOf(x, y);
    if (!this._navForce && this._navGoal === gc && this._path.length > 1 && !this._reachedEnd && now - this._navT < 0.35) return;
    if (NAV.budget <= 0) { NAV.stats.skipped++; return; }
    const r = NAV.path(o.getX(), o.getY(), x, y);
    NAV.budget -= r.exp + 40;
    this._navForce = false; this._navGoal = gc; this._navT = now;
    if (!r.found || r.pts.length < 2) { this._pathFound = false; return; }
    this._path = r.pts;
    this._enterSegment(0);
    this._pathFound = true;
  };
  P.doStepPreEvents = function (container) {
    const o = this.owner, p = this._path;
    if (p.length === 0 || this._reachedEnd) return;
    if (this._maxSpeed <= 0) {
      // movido por otro medio (bots con TopDown) o en espera: solo avanza los tramos por cercanía, no reubica al objeto
      let guard = 0;
      while (!this._reachedEnd && this._currentSegment < p.length - 1 && guard++ < 8) {
        const q = p[this._currentSegment + 1];
        if (Math.hypot(q[0] - o.getX(), q[1] - o.getY()) < 24) this._enterSegment(this._currentSegment + 1); else break;
      }
      return;
    }
    origStep.call(this, container);
    // atoramiento: casi sin avanzar con velocidad -> forzar ruta nueva y sacar de una celda bloqueada
    const now = NAV.scene ? NAV.scene.getTimeManager().getTimeFromStart() / 1000 : 0;
    if (this._navPX === undefined) { this._navPX = o.getX(); this._navPY = o.getY(); this._navPT = now; }
    if (now - this._navPT >= 0.6) {
      const moved = Math.hypot(o.getX() - this._navPX, o.getY() - this._navPY);
      if (this._speed > 20 && !this._reachedEnd && moved < 6 && NAV.grid) {
        this._navForce = true;
        const c = NAV.cellOf(o.getX(), o.getY());
        if (NAV.grid.cls[c] === 1) { const f = NAV.nearestFree(o.getX(), o.getY(), 6); if (f) { o.setX(f[0]); o.setY(f[1]); } }
      }
      this._navPX = o.getX(); this._navPY = o.getY(); this._navPT = now;
    }
  };
}
"""
codigo = f"/*{MARCA}*/\nif (!(gdjs.fdizNav && gdjs.fdizNav.ready)) {{\n{modulo}\ngdjs.fdizNav.ready = true;\n}}\n{GLUE}"
evento_js = {"type": "BuiltinCommonInstructions::JsCode", "inlineCode": codigo, "parameterObjects": "", "useStrict": True,
             "eventsSheetExpanded": False}

def es_nuestro(e):
    return e.get("type", "").endswith("JsCode") and MARCA in e.get("inlineCode", "")
J["events"] = [e for e in J["events"] if not es_nuestro(e)]
J["events"].insert(0, evento_js)

def recorrer(evs):
    for e in evs:
        yield e
        yield from recorrer(e.get("events", []))

# ---------------------------------------------------------------- 3) zombis sin ruta: no empujarlos contra la pared
n_fb = 0
for e in recorrer(J["events"]):
    cs = e.get("conditions", [])
    if any(x["type"].get("inverted") and x["type"]["value"] == "PathfindingBehavior::PathFound" and x["parameters"][0] == "Zombies" for x in cs):
        e["disabled"] = True; n_fb += 1
    # el ForEach de zombis "persigue" sin ruta lleva la condición dentro del propio evento
for e in recorrer(J["events"]):
    if e.get("type", "").endswith("ForEach") and e.get("object") == "Zombies":
        if any(x["type"].get("inverted") and x["type"]["value"] == "PathfindingBehavior::PathFound" for x in e.get("conditions", [])):
            e["disabled"] = True; n_fb += 1
print("  eventos de empuje directo desactivados:", n_fb)

# ---------------------------------------------------------------- 3b) temporizador "ruta" de los bots
# El evento de bots pide ruta con CompareObjectTimer(Sup,"ruta",>=,0.2), pero ese temporizador nunca se iniciaba: la condición
# da NaN >= 0.2 = falso y los bots NUNCA pedían ruta (iban en línea recta y se atoraban en las paredes).
n_t = 0
for e in recorrer(J["events"]):
    acc = e.get("actions", [])
    if any(x["type"]["value"] == "ResetObjectTimer" and x["parameters"][:2] == ["Sup", '"atasco"'] for x in acc) and \
       not any(x["type"]["value"] == "ResetObjectTimer" and x["parameters"][:2] == ["Sup", '"ruta"'] for x in acc):
        acc.append(a("ResetObjectTimer", "Sup", '"ruta"')); n_t += 1
print("  temporizador ruta de bots iniciado en", n_t, "evento(s)")

# ---------------------------------------------------------------- 2) puertas
orig = json.load(open(os.path.join(HERE, "datos", "puertas_originales.json"), encoding="utf-8"))
def grupo_de(nombre):
    return next(e for e in J["events"] if e.get("type", "").endswith("Group") and e.get("name") == nombre)

# 2a) Puertas: tipos y golpes -> eventos originales (golpes, zombis, vida, tarjeta, apertura + zonas)
g_tipos = grupo_de("Puertas: tipos y golpes")
g_tipos["events"] = copy.deepcopy(orig["Puertas: tipos y golpes"])

# 2b) Mapa: choques y puertas -> separación actual + Usar junto a la puerta (+ R en teclado), alcance 140
g_mapa = grupo_de("Mapa: choques y puertas")
actuales = [e for e in g_mapa["events"]   # solo las separaciones (personajes entre sí y contra sólidos); lo demás se regenera
            if any(x["type"]["value"] == "SeparateFromObjects" for x in e.get("actions", []))]
viejos = copy.deepcopy(orig["Mapa: choques y puertas"])
fe = next(e for e in viejos if e["type"].endswith("ForEach") and e.get("object") == "Puerta")
# Distance() compara CENTROS de sprite (el del personaje queda ~62 px sobre sus pies): se cambia por distancia de pies a la puerta
def pies(cond):
    return c("BuiltinCommonInstructions::CompareNumbers",
             "DistanceBetweenPositions(Sup.X(), Sup.Y(), Puerta.X() + Puerta.Width() / 2, Puerta.Y() + Puerta.Height() / 2)", "<", "130")
for s_ in fe["events"]:
    s_["conditions"] = [pies(x) if x["type"]["value"] == "Distance" and x["parameters"][:2] == ["Sup", "Puerta"] else x for x in s_.get("conditions", [])]
sub = next(s for s in fe["events"] if any(x["type"]["value"] == "VarObjet" and x["parameters"][:2] == ["Sup", "Usando"] for x in s.get("conditions", [])))
# variante con R (teclado, Control 0)
sub_r = copy.deepcopy(sub)
sub_r["conditions"] = [x for x in sub_r["conditions"] if not (x["type"]["value"] == "VarObjet" and x["parameters"][:2] == ["Sup", "Usando"])]
sub_r["conditions"] += [c("VarObjet", "Sup", "Control", "=", "0"), c("KeyPressed", "", "r")]
fe["events"].append(sub_r)
resto = [e for e in viejos if e.get("type", "").endswith("Standard") and not e.get("conditions")
         and any(x["type"]["value"] == "ModVarObjet" and x["parameters"][:2] == ["Puerta", "Usada"] for x in e.get("actions", []))]
reset = [e for e in viejos if e.get("type", "").endswith("Standard") and any(
    x["type"]["value"] == "VarObjet" and x["parameters"][:2] == ["Puerta", "Usada"] for x in e.get("conditions", []))]
g_mapa["events"] = [e for e in g_mapa["events"] if e.get("type", "").endswith("Comment")] + \
    [e for e in actuales if not e.get("type", "").endswith("Comment")] + resto[:1] + [fe] + reset
g_mapa["events"].insert(0, comentario("Choques con muros, muebles y puertas. Puerta: mantener Usar (F, A del control, o bots) o R en teclado junto a ella "
                                      "(normal 1 s, electrónica 8 s, a 130 px de los pies). Al abrirse se descubren sus zonas (grupo Puertas: tipos y golpes)."))
# quita comentarios duplicados
vistos = False; nuevo = []
for e in g_mapa["events"]:
    if e.get("type", "").endswith("Comment"):
        if vistos: continue
        vistos = True
    nuevo.append(e)
g_mapa["events"] = nuevo

# 2c) bots: abren las puertas que cruza su ruta (antes solo lo hacían sin humanos y con el guía cerca)
g_bots = grupo_de("Bots: objetivos y puertas")
g_bots["events"] = [e for e in g_bots["events"] if "Sup.PathBot::NextNodeX(), Sup.PathBot::NextNodeY(), Puerta" not in json.dumps(e)]
DC = "Puerta.X() + Puerta.Width() / 2, Puerta.Y() + Puerta.Height() / 2"
bot_puerta = {"type": "BuiltinCommonInstructions::ForEach", "object": "Sup",
              "conditions": [c("VarObjet", "Sup", "Control", "=", "-1"), c("VarObjetTxt", "Sup", "Estado", "=", '"normal"'),
                             c("PathfindingBehavior::PathFound", "Sup", "PathBot")],
              "actions": [],
              "events": [ev([c("PickNearest", "Puerta", "Sup.X()", "Sup.Y()", ""),
                             c("BuiltinCommonInstructions::CompareNumbers", f"DistanceBetweenPositions(Sup.X(), Sup.Y(), {DC})", "<", "110"),
                             c("BuiltinCommonInstructions::CompareNumbers",
                               f"DistanceBetweenPositions(Sup.PathBot::NextNodeX(), Sup.PathBot::NextNodeY(), {DC})", "<", "110")],
                            [a("ModVarObjet", "Sup", "Usando", "=", "1"), a("ModVarObjet", "Sup", "MovX", "=", "0"), a("ModVarObjet", "Sup", "MovY", "=", "0"),
                             a("ModVarObjet", "Sup", "AimX", "=", f"Puerta.X() + Puerta.Width() / 2 - Sup.X()"),
                             a("ModVarObjet", "Sup", "AimY", "=", f"Puerta.Y() + Puerta.Height() / 2 - Sup.Y()")],
                            sub=[ev([{"type": {"value": "BuiltinCommonInstructions::Or"}, "parameters": [], "subInstructions": [
                                c("VarObjet", "Puerta", "TiempoAbrir", ">", "2"), c("VarObjet", "Puerta", "TiempoAbrir", "<=", "0")]}],
                                [a("ModVarObjet", "Sup", "QuierePegar", "=", "1")])])]}
g_bots["events"].append(bot_puerta)

json.dump(p, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("OK: navegación A*, puertas y zonas")
