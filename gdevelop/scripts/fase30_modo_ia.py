"""Fase 30 · Menú de modos solo con ESCAPE y JEFE, orientación de zombis por su movimiento real, colisión entre bots solo en Jefe local,
bots que huyen de zombis grandes. Idempotente. Va DESPUÉS de fase28 y fase29 (las deshace parcialmente: tercera tarjeta EN LÍNEA)."""
import json, os, re, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gd_util import c, a

AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
bak = os.path.join(AQUI, "..", "respaldos", "antes_de_fase30_20261117.json")
if not os.path.exists(bak):
    shutil.copy(PRY, bak)
d = json.load(open(PRY))
LAY = {l["name"]: l for l in d["layouts"]}
M, J = LAY["Menu"], LAY["Juego"]
MK = "FDIZ-FASE30"
def walk(lst):
    for e in lst:
        yield e
        yield from walk(e.get("events", []))
def marca(clave):
    return {"type": "BuiltinCommonInstructions::Comment", "color": {"b": 109, "g": 230, "r": 255, "textB": 0, "textG": 0, "textR": 0}, "comment": MK + "-" + clave, "comment2": ""}
def hay(lst, clave): return any(x.get("comment") == MK + "-" + clave for x in lst)
def js_event(code):
    return {"type": "BuiltinCommonInstructions::JsCode", "inlineCode": code, "parameterObjects": "", "useStrict": True, "eventsSheetExpanded": False}
def grupo(lay, nombre): return next(e for e in lay["events"] if e.get("name") == nombre)
def cond_has(e, tipo, params):
    return any(x["type"]["value"] == tipo and x["parameters"][:len(params)] == params for x in e.get("conditions", []))

# ---------------------------------------------------------------- 1 · Menú de modos: solo ESCAPE y JEFE (como al principio)
M["instances"] = [i for i in M["instances"] if not (i["name"] in ("MarcoModo", "IlusModo", "TxtCapA", "TxtCapB")
                  and any(v["name"] == "Idx" and v["value"] == 2 for v in i.get("initialVariables", [])))]
POS = {("MarcoModo", "0"): "340", ("IlusModo", "0"): "390", ("MarcoModo", "1"): "1140", ("IlusModo", "1"): "1190"}
for e in walk(M["events"]):
    if not e["type"].endswith("Standard"): continue
    modo = cond_has(e, "VarSceneTxt", ["Paso", "=", '"modo"'])
    for x in e["actions"]:
        p = x["parameters"]
        # Sel solo entre 2 opciones en el paso "modo"
        if modo and p[:2] == ["Sel", "="] and "mod(Variable(Sel)" in p[2]: p[2] = p[2].replace(" + 2, 3)", " + 1, 2)").replace(" + 1, 3)", " + 1, 2)")
        # leyendas bajo sus tarjetas
        if x["type"]["value"] == "MettreX" and p[:1] in (["TxtCapA"], ["TxtCapB"]) and cond_has(e, "VarSceneTxt", ["Paso", "!=", '"jefetipo"']):
            for k, cx in (("0", "560"), ("1", "1360")):
                if any(y["type"]["value"] == "VarObjet" and y["parameters"][:4] == [p[0], "Idx", "=", k] for y in e["conditions"]):
                    p[2] = re.sub(r"^\d+ - ", cx + " - ", p[2])
        # posiciones de marcos e ilustraciones
        if modo and x["type"]["value"] == "MettreX" and p[:1] in (["MarcoModo"], ["IlusModo"]):
            for y in e["conditions"]:
                if y["type"]["value"] == "VarObjet" and y["parameters"][:3] == [p[0], "Idx", "="] and (p[0], y["parameters"][3]) in POS:
                    p[2] = POS[(p[0], y["parameters"][3])]
# videos de las tarjetas
for e in walk(grupo(M, "Videos")["events"]):
    for x in e.get("actions", []):
        p = x["parameters"]
        if x["type"]["value"] == "MettreX" and p[:1] == ["VidIlusEscape"]: p[2] = "390"
        if x["type"]["value"] == "MettreX" and p[:1] == ["VidIlusJefe"]: p[2] = "1190"
# resalte con ratón: dos tarjetas
ME = M["events"]
for i in range(len(ME) - 1, -1, -1):
    cm = ME[i].get("comment", "")
    if cm == "FDIZ-FASE28-HOV-M2":
        del ME[i:i + 2]
    elif cm in ("FDIZ-FASE28-HOV-M0", "FDIZ-FASE28-HOV-M1"):
        x0 = 340 if cm.endswith("M0") else 1140
        ev = ME[i + 1]
        for cc in ev["conditions"]:
            if cc["type"]["value"].endswith("CompareNumbers") and cc["parameters"][0] == "MouseX()":
                cc["parameters"][2] = str(x0) if cc["parameters"][1] == ">=" else str(x0 + 440)

# ---------------------------------------------------------------- 2 · Colisión entre supervivientes SOLO en Jefe local (4 bots)
COL = '/*FDIZ-FASE30-COL*/ if (runtimeScene.getVariables().get("Jefe").getAsNumber() !== 1 || runtimeScene.getGame().getVariables().get("NetRol").getAsNumber() !== 0) return;\n' + "\n".join(l for l in open(os.path.join(AQUI, "separar_supervivientes.js"), encoding="utf-8").read().split("\n") if not l.startswith("//"))
if not any("FDIZ-FASE30-COL" in e.get("inlineCode", "") for e in walk(J["events"])):
    for i in range(len(J["events"]) - 1, -1, -1):
        if J["events"][i].get("comment") == MK + "-COL": J["events"].pop(i)
    ev = {"type": "BuiltinCommonInstructions::Standard", "conditions": [c("VarGlobal", "NetRol", "!=", "2")], "actions": [], "events": [js_event(COL)]}
    fin = len(J["events"]) - 1 if J["events"][-1].get("inlineCode", "").startswith("/*FDIZ-FASE25-END*/") else len(J["events"])
    J["events"].insert(fin, marca("COL")); J["events"].insert(fin + 1, ev)
# y el empuje superviviente↔zombi (hacía vibrar a los bots contra las paredes) no se aplica en Jefe
for e in walk(J["events"]):
    if e["type"].endswith("Standard") and any("Separate" in x["type"]["value"] and x["parameters"][:2] == ["Sup", "Zombies"] for x in e["actions"]):
        cc = c("VarScene", "Jefe", "=", "0")
        if cc not in e["conditions"]: e["conditions"].append(cc)

# ---------------------------------------------------------------- 3 · Zombis: orientación según el movimiento real
DIR = r"""
/*FDIZ-FASE30-DIR*/
const scn = runtimeScene;
if (scn.getGame().getVariables().get("NetRol").getAsNumber() === 2) return;
if (scn.getVariables().get("Pausa").getAsNumber() === 1) return;
for (const n of ["ZNormal", "ZCorredor", "ZGriton", "ZGordo", "ZConserje", "ZCurado"]) {
  for (const z of (scn.getObjects(n) || [])) {
    const x = z.getX(), y = z.getY();
    if (z._ox === undefined) { z._ox = x; z._oy = y; z._vx = 0; z._vy = 0; continue; }
    z._vx = z._vx * 0.85 + (x - z._ox) * 0.15; z._vy = z._vy * 0.85 + (y - z._oy) * 0.15; z._ox = x; z._oy = y;
    const est = z.getVariables().get("Estado").getAsString();
    if (est !== "persigue" && est !== "paseando") continue;
    if (z.getTimerElapsedTimeInSeconds("ataque") < 0.45 && est === "persigue" && z._dn !== undefined && z._dn < 90) continue;
    if (Math.hypot(z._vx, z._vy) < 0.35) continue;
    if (Math.abs(z._vx) > Math.abs(z._vy)) { z.setAnimationName("caminar_lado"); z.flipX(z._vx < 0); }
    else { z.setAnimationName(z._vy < 0 ? "caminar_arriba" : "caminar_abajo"); z.flipX(false); }
  }
}
"""
if not hay(J["events"], "DIR"):
    J["events"].append(marca("DIR")); J["events"].append(js_event(DIR))
# separación entre zombis más suave (antes podía arrastrarlos hacia atrás)
for e in walk(J["events"]):
    if e["type"].endswith("JsCode") and "FDIZ-FASE29-IA" in e["inlineCode"]:
        e["inlineCode"] = e["inlineCode"].replace("Math.min(2.2, (R - d) * 0.12)", "Math.min(1.1, (R - d) * 0.06)")

# ---------------------------------------------------------------- 4 · Bots: los zombis grandes pesan más al decidir huir
for e in walk(J["events"]):
    if e["type"].endswith("JsCode") and "FDIZ-FASE29-BOTS" in e["inlineCode"] and "FDIZ-F30" not in e["inlineCode"]:
        s = e["inlineCode"]
        s = s.replace("if (d < 240) { n++; zx += z.getX(); zy += z.getY(); }",
                      "/*FDIZ-F30*/ const gr = z.getName() === \"ZConserje\" || z.getName() === \"ZGordo\"; if (d < (gr ? 340 : 240)) { n += gr ? 3 : 1; zx += z.getX(); zy += z.getY(); }")
        s = s.replace("const d = Math.hypot(z.getX() - px, z.getY() - py); if (d < md) md = d;",
                      "const d = Math.hypot(z.getX() - px, z.getY() - py) - (z.getName() === \"ZConserje\" || z.getName() === \"ZGordo\" ? 140 : 0); if (d < md) md = d;")
        e["inlineCode"] = s

json.dump(d, open(PRY, "w"), ensure_ascii=False, indent=2)
print("OK fase 30")
