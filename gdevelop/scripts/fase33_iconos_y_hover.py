"""Fase 33 · (1) Pantalla Local / En línea (Escape y Jefe): vuelven los iconos de computadora y globo (los videos de Escape/Jefe ya no tapan las tarjetas).
(2) Reacción al mouse en todos los botones: se iluminan (sin cambiar tamaño ni posición) y el cursor cambia a mano. Idempotente.
Va después de fase32 (cadena fase25 -> ... -> fase33)."""
import json, os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
bak = os.path.join(AQUI, "..", "respaldos", "antes_de_fase33_20261117.json")
if not os.path.exists(bak):
    shutil.copy(PRY, bak)
d = json.load(open(PRY))
capa = {l["name"]: l for l in d["layouts"]}
MK = "FDIZ-FASE33"

def walk(lst):
    for e in lst:
        yield e
        yield from walk(e.get("events", []))

# ---------------------------------------------------------------- 1 · iconos Local / En línea
G = next(e for e in capa["Menu"]["events"] if e.get("name") == "Videos")
def cond_paso(e, op):
    return any(c["type"]["value"] == "VarSceneTxt" and c["parameters"][:3] == ["Paso", op, '"modo"'] for c in e.get("conditions", []))
for e in walk(G["events"]):
    for x in e.get("actions", []):
        p = x["parameters"]
        if x["type"]["value"] != "MettreX" or p[:1] not in (["VidIlusEscape"], ["VidIlusJefe"]): continue
        if cond_paso(e, "!="): p[2] = "-6000"                       # fuera de la pantalla de modos: el video no se ve
        elif cond_paso(e, "="): p[2] = "390" if p[0] == "VidIlusEscape" else "1190"

# ---------------------------------------------------------------- 2 · hover en todos los botones
JS = r'''/*FDIZ-FASE33-HOVER*/
(function () {
  const S = runtimeScene, inp = gdjs.evtTools.input, LISTA = __LISTA__;
  let cursor = false;
  const vivo = (o) => o.isVisible() && o.getOpacity() > 0 && o.getX() > -500 && o.getX() < 2600;
  for (const nm of LISTA) {
    const arr = S.getObjects(nm) || [];
    for (const o of arr) {
      const x = o.getX(), y = o.getY(), w = o.getWidth(), h = o.getHeight();
      let b = o._fz;
      if (!b || x !== b.lx || y !== b.ly || w !== b.lw || h !== b.lh) b = o._fz = { x, y, w, h, k: 0, lx: x, ly: y, lw: w, lh: h, on: false };
      let ref = b;
      if (nm === "IlusModo" || nm === "VidIlusEscape" || nm === "VidIlusJefe") {
        const ms = S.getObjects("MarcoModo") || [];
        const m = ms.find((q) => q._fz && Math.abs(q._fz.x - b.x) < 160);
        if (m) ref = m._fz;
      }
      const lay = o.getLayer();
      const mx = inp.getMouseX(S, lay, 0), my = inp.getMouseY(S, lay, 0);
      const sobre = vivo(o) && mx >= ref.x && mx <= ref.x + ref.w && my >= ref.y && my <= ref.y + ref.h;
      if (sobre) cursor = true;
      const k0 = b.k;
      b.k += ((sobre ? 1 : 0) - b.k) * 0.3;
      if (b.k < 0.01) b.k = 0;
      const on = b.k > 0.5;
      if (on !== b.on && o.setColor) { b.on = on; o.setColor(on ? "255;238;190" : "255;255;255"); }
    }
  }
  try { const cv = S.getGame().getRenderer().getCanvas(); if (cv) cv.style.cursor = cursor ? "pointer" : "default"; } catch (e) {}
})();'''
LISTAS = {
    "Menu": ["MarcoModo", "SelMarco", "DifBtn", "EqCelda", "EqRet"],
    "Juego": ["PausaBtn", "BtnOmitir"],
    "Resultados": ["BtnRei", "BtnMenuR"],
}
def marca(clave):
    return {"type": "BuiltinCommonInstructions::Comment", "color": {"b": 109, "g": 230, "r": 255, "textB": 0, "textG": 0, "textR": 0}, "comment": MK + "-" + clave, "comment2": ""}
def purga(lst):
    """quita mis eventos viejos aunque fase25 los haya envuelto en NetRol != 2, y sus marcas y envoltorios vacios"""
    for e in list(lst):
        if e["type"].endswith("JsCode") and "FDIZ-FASE33-HOVER" in e["inlineCode"]:
            lst.remove(e); continue
        if e.get("comment") == MK + "-HOVER":
            lst.remove(e); continue
        if e.get("events"):
            purga(e["events"])
            if e["type"].endswith("Standard") and not e["events"] and not e.get("actions") and [x["parameters"] for x in e["conditions"]] == [["NetRol", "!=", "2"]]:
                lst.remove(e)
for esc, lista in LISTAS.items():
    ev = capa[esc]["events"]
    purga(ev)
    ev.append(marca("HOVER"))
    ev.append({"type": "BuiltinCommonInstructions::JsCode", "inlineCode": JS.replace("__LISTA__", json.dumps(lista)), "parameterObjects": "", "useStrict": True, "eventsSheetExpanded": False})

json.dump(d, open(PRY, "w"), ensure_ascii=False, indent=2)
print("OK fase 33")
