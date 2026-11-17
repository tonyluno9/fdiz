"""Fase 29 · Menús reparados, fondo detrás de los textos, fuente con más carácter, IA de zombies/bots (Jefe local),
título con "Presiona Enter / A" latiendo. Idempotente.
Orden: fase25 -> fase26 -> fase27 -> fase28 -> fase29
"""
import json, copy, os, shutil, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gd_util import c, a, res_imagen

AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
JEFE_SRC = os.path.join(AQUI, "jefe_modo.js")
bak = os.path.join(AQUI, "..", "respaldos", "antes_de_fase29_20261117.json")
if not os.path.exists(bak):
    shutil.copy(PRY, bak)
d = json.load(open(PRY))
LAY = {l["name"]: l for l in d["layouts"]}
T_, M, J, R, O = LAY["Titulo"], LAY["Menu"], LAY["Juego"], LAY["Resultados"], LAY["Online"]
MK = "FDIZ-FASE29"
STD = "BuiltinCommonInstructions::Standard"

def std(conds, acts, sub=()):
    return {"type": STD, "conditions": conds, "actions": acts, "events": list(sub)}
def marca(clave):
    return {"type": "BuiltinCommonInstructions::Comment", "color": {"b": 109, "g": 230, "r": 255, "textB": 0, "textG": 0, "textR": 0}, "comment": MK + "-" + clave, "comment2": ""}
def hay(lst, clave): return any(x.get("comment") == MK + "-" + clave for x in lst)
def js_event(code):
    return {"type": "BuiltinCommonInstructions::JsCode", "inlineCode": code, "parameterObjects": "", "useStrict": True, "eventsSheetExpanded": False}
def walk(lst):
    for e in lst:
        yield e
        yield from walk(e.get("events", []))
def grupo(lay, nombre): return next(e for e in lay["events"] if e.get("name") == nombre)
def cond_has(e, tipo, params, inv=None):
    return any(x["type"]["value"] == tipo and x["parameters"][:len(params)] == params and (inv is None or bool(x["type"].get("inverted")) == inv) for x in e.get("conditions", []))

# =====================================================================
# 1 · RECURSOS: fondo de texto (9 cortes) y objeto PanelSprite en cada escena
# =====================================================================
png = os.path.join(AQUI, "..", "FDI-Z", "assets", "interfaz", "p29_fondo_texto.png")
if not os.path.exists(png):
    from PIL import Image
    S = 72
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    px = im.load()
    for y in range(S):
        for x in range(S):
            dx = min(x, S - 1 - x); dy = min(y, S - 1 - y); m = min(dx, dy)
            esq = dx < 4 and dy < 4 and (dx + dy) < 4          # esquinas cortadas (pixel art)
            if esq: continue
            if m < 2: px[x, y] = (6, 8, 20, 235)               # contorno oscuro
            elif m < 5: px[x, y] = (255, 176, 64, 255)         # borde naranja
            elif m < 6: px[x, y] = (255, 226, 150, 255)        # brillo interior
            else: px[x, y] = (14, 18, 44, 226)                 # relleno azul noche
    im.save(png)
if not any(r["name"] == "p29_fondo_texto" for r in d["resources"]["resources"]):
    d["resources"]["resources"].append(res_imagen("p29_fondo_texto", "assets/interfaz/p29_fondo_texto.png"))
PANEL = {"assetStoreId": "", "bottomMargin": 14, "height": 72, "leftMargin": 14, "name": "FondoTxt", "rightMargin": 14, "texture": "p29_fondo_texto",
         "tiled": False, "topMargin": 14, "type": "PanelSpriteObject::PanelSprite", "width": 72, "variables": [], "effects": [], "behaviors": []}
for lay in (T_, M, J, O):
    if not any(o["name"] == "FondoTxt" for o in lay["objects"]):
        lay["objects"].append(copy.deepcopy(PANEL))

# =====================================================================
# 2 · FUENTE con más carácter en TODOS los textos de interfaz
# =====================================================================
for lay in d["layouts"]:
    for o in lay["objects"]:
        if o["type"] != "TextObject::Text": continue
        o["font"] = "PixelifySans.ttf"
        ct = o.setdefault("content", {})
        ct["font"] = "PixelifySans.ttf"
        if not ct.get("isOutlineEnabled"):
            ct["isOutlineEnabled"] = True; ct["outlineColor"] = "0;0;0"; ct["outlineThickness"] = 3
        ct["isShadowEnabled"] = True; ct["shadowColor"] = "0;0;0"; ct["shadowOpacity"] = 190
        ct["shadowDistance"] = 3; ct["shadowAngle"] = 90; ct["shadowBlurRadius"] = 0

# =====================================================================
# 3 · FONDO DETRÁS DE LOS TEXTOS (motor genérico por escena)
# =====================================================================
BD = r"""
/*FDIZ-FASE29-BD*/
(function () {
  const scn = runtimeScene, CFG = __CFG__;
  const B = scn._fdizBd || (scn._fdizBd = { a: [], n: 0 }); B.n = 0;
  const nuevo = () => { let p = B.a[B.n]; if (!p) { p = scn.createObject("FondoTxt"); B.a.push(p); } B.n++; return p; };
  const poner = (p, x0, y0, x1, y1, z, layer) => { p.hide(false); p.setLayer(layer); p.setPosition(x0, y0); p.setWidth(x1 - x0); p.setHeight(y1 - y0); p.setZOrder(z); };
  for (const c of CFG) {
    const items = [];
    for (const nm of c.o) for (const o of (scn.getObjects(nm) || [])) { if (o.isHidden() || !String(o.getText()).trim()) continue; items.push(o); }
    if (c.pair) {
      const g = {};
      for (const o of items) { const k = o.getVariables().get(c.pair).getAsNumber(); const e = g[k] || (g[k] = { x0: 1e9, y0: 1e9, x1: -1e9, y1: -1e9, z: 1e9 });
        e.x0 = Math.min(e.x0, o.getX()); e.y0 = Math.min(e.y0, o.getY()); e.x1 = Math.max(e.x1, o.getX() + o.getWidth()); e.y1 = Math.max(e.y1, o.getY() + o.getHeight()); e.z = Math.min(e.z, o.getZOrder()); }
      for (const k in g) { const e = g[k]; poner(nuevo(), e.x0 - c.px, e.y0 - c.py, e.x1 + c.px, e.y1 + c.py, e.z - 1, c.layer); }
    } else {
      for (const o of items) poner(nuevo(), o.getX() - c.px, o.getY() - c.py, o.getX() + o.getWidth() + c.px, o.getY() + o.getHeight() + c.py, o.getZOrder() - 1, c.layer);
    }
  }
  for (let i = B.n; i < B.a.length; i++) B.a[i].hide(true);
})();
"""
def agrega_bd(lay, cfg):
    if hay(lay["events"], "BD"): return
    lay["events"].append(marca("BD"))
    lay["events"].append(js_event(BD.replace("__CFG__", json.dumps(cfg))))
agrega_bd(T_, [{"o": ["TxtTitulo"], "px": 26, "py": 12, "layer": ""}])
agrega_bd(M, [{"o": ["TxtCapA", "TxtCapB"], "pair": "Idx", "px": 24, "py": 12, "layer": ""},
              {"o": ["TxtSlots"], "px": 20, "py": 12, "layer": ""}])
agrega_bd(J, [{"o": ["TxtAyuda", "TxtBanner", "TxtDialogo"], "px": 22, "py": 10, "layer": "HUD"}])

# etiquetas del mapa del Jefe (ZONA VISIBLE / NO CABE) con su propio fondo
def parche_jefe(s):
    viejo = 'if (why) txt(why, hx + 26, hy + 8, 22, "255;140;140", "left", 300);'
    nuevo = ('if (why) { if (dB) { dB.setFillColor("14;18;44"); dB.setFillOpacity(235); dB.setOutlineColor("255;176;64"); dB.setOutlineOpacity(255); dB.setOutlineSize(3);'
             ' dB.drawRectangle(hx + 18, hy, hx + 44 + why.length * 13, hy + 38); } txt(why, hx + 30, hy + 6, 22, "255;140;140", "left", 300); }')
    return s.replace(viejo, nuevo)
for e in walk(grupo(J, "Modo Jefe de zombies")["events"]):
    if e["type"].endswith("JsCode") and "Modo Jefe de zombies" in e["inlineCode"]:
        n = parche_jefe(e["inlineCode"])
        if n != e["inlineCode"]: e["inlineCode"] = n
src = open(JEFE_SRC, encoding="utf-8").read(); ns = parche_jefe(src)
if ns != src: open(JEFE_SRC, "w", encoding="utf-8").write(ns)

# =====================================================================
# 4 · MENÚ: título y leyendas de "¿Cómo quieres jugar?" bien centrados
# =====================================================================
for e in walk(M["events"]):
    if not e["type"].endswith("Standard"): continue
    for x in e["actions"]:
        p = x["parameters"]
        if x["type"]["value"].endswith("String") and p[:1] == ["TxtMenu"] and "CÓMO QUIERES JUGAR" in p[-1]:
            p[-1] = '"MODO JEFE"'
        if x["type"]["value"] == "MettreX" and p[:1] in (["TxtCapA"], ["TxtCapB"]) and cond_has(e, "VarSceneTxt", ["Paso", "=", '"jefetipo"']):
            if any(y["type"]["value"] == "VarObjet" and y["parameters"][:3] == [p[0], "Idx", "="] and y["parameters"][3] == "0" for y in e["conditions"]):
                p[2] = re.sub(r"^\d+ - ", "560 - ", p[2])
            if any(y["type"]["value"] == "VarObjet" and y["parameters"][:3] == [p[0], "Idx", "="] and y["parameters"][3] == "1" for y in e["conditions"]):
                p[2] = re.sub(r"^\d+ - ", "1360 - ", p[2])

# =====================================================================
# 5 · TÍTULO: "PRESIONA ENTER / A PARA INICIAR" con latido
# =====================================================================
for e in walk(T_["events"]):
    for x in e.get("actions", []):
        p = x["parameters"]
        if x["type"]["value"].endswith("String") and p[:2] == ["TxtSub", "="] and p[2] in ('""', '"La FDI se llenó de zombies. Escapen."'):
            p[2] = '"PRESIONA ENTER / A PARA INICIAR"'
PULSO = r"""
/*FDIZ-FASE29-LATIDO*/
{
  const o = (runtimeScene.getObjects("TxtSub") || [])[0];
  if (o) {
    const t = runtimeScene.getTimeManager().getTimeFromStart() / 1000, ph = (t % 1.3) / 1.3;
    const lub = Math.exp(-Math.pow((ph - 0.10) / 0.055, 2)), dub = 0.65 * Math.exp(-Math.pow((ph - 0.30) / 0.065, 2)), p = Math.min(1, lub + dub);
    o.setText("PRESIONA ENTER / A PARA INICIAR");
    o.setCharacterSize(Math.round(34 * (1 + 0.16 * p)));
    o.setColor(p > 0.35 ? "255;240;170" : "255;200;90");
    o.setOpacity(Math.round(175 + 80 * p));
    o.setPosition(1490 - o.getWidth() / 2, 855 - o.getHeight() / 2);
    o.setZOrder(6);
  }
}
"""
if not hay(T_["events"], "LATIDO"):
    T_["events"].append(marca("LATIDO")); T_["events"].append(js_event(PULSO))

# =====================================================================
# 6 · IA: zombies sin atascarse y bots que huyen / patrullan en Jefe local
# =====================================================================
G21 = grupo(J, "Zombies: IA, ataque y muerte")
# 6a · fuera el choque rígido zombi↔zombi (formaba la masa inmóvil)
for e in list(G21["events"]):
    if e["type"].endswith("Standard") and any("Separate" in x["type"]["value"] and x["parameters"][:2] == ["Zombies", "Zombies"] for x in e["actions"]):
        G21["events"].remove(e)
# 6b · rutas escalonadas y destino con hueco propio alrededor del objetivo
for e in walk(G21["events"]):
    for cc in e.get("conditions", []):
        if cc["type"]["value"] == "CompareObjectTimer" and cc["parameters"][:2] == ["Zombies", '"ruta"'] and cc["parameters"][3] == "0.75":
            cc["parameters"][3] = "0.6 + Zombies.Variable(RutaJit)"
    for x in e.get("actions", []):
        if x["type"]["value"] == "SetDestination" and x["parameters"][:2] == ["Zombies", "Pathfinding"] and x["parameters"][3] == "Sup.X()":
            x["parameters"][3] = "Sup.X() + Zombies.Variable(OffX)"; x["parameters"][4] = "Sup.Y() + Zombies.Variable(OffY)"
for o in J["objects"]:
    if o["name"] in ("ZNormal", "ZCorredor", "ZGriton", "ZGordo", "ZConserje", "ZCurado"):
        for v in ("Ang", "OffX", "OffY", "RutaJit"):
            if not any(q["name"] == v for q in o["variables"]): o["variables"].append({"name": v, "type": "number", "value": 0})
    if o["name"] == "Sup" and not any(q["name"] == "Huye" for q in o["variables"]):
        o["variables"].append({"name": "Huye", "type": "number", "value": 0})

IA = r"""
/*FDIZ-FASE29-IA*/
const scn = runtimeScene;
if (scn.getGame().getVariables().get("NetRol").getAsNumber() === 2) return;
const SV = scn.getVariables();
if (SV.get("Estado").getAsString() === "intro" || SV.get("Pausa").getAsNumber() === 1) return;
const dt = Math.min(0.1, scn.getElapsedTime() / 1000);
const ZN = ["ZNormal", "ZCorredor", "ZGriton", "ZGordo", "ZConserje", "ZCurado"];
const Z = [];
for (const n of ZN) for (const z of (scn.getObjects(n) || [])) if (z.getVariables().get("Estado").getAsString() !== "muerto") Z.push(z);
const S = (scn.getObjects("Sup") || []).filter((s) => s.getVariables().get("Estado").getAsString() === "normal");
const NAV = gdjs.fdizNav, grid = NAV && NAV.grid;
const libre = (x, y) => { if (!grid) return true; const cx = Math.floor(x / NAV.cfg.C), cy = Math.floor(y / NAV.cfg.C); if (cx < 0 || cy < 0 || cx >= grid.W || cy >= grid.H) return false; return grid.cls[cy * grid.W + cx] === 0; };
const F = scn._f29 || (scn._f29 = { t: 0 }); F.t += dt;

// ---- zombis: hueco propio, separación suave y desatasco ----
const celda = new Map(), R = 34;
for (const z of Z) {
  const v = z.getVariables();
  if (!z._f29) { z._f29 = 1; v.get("Ang").setNumber(Math.random() * 6.2832); v.get("RutaJit").setNumber(Math.random() * 0.5); z._px = z.getX(); z._py = z.getY(); z._st = 0; z._ck = Math.random() * 0.4; }
  let dn = 1e9;
  for (const s of S) { const d = Math.hypot(s.getX() - z.getX(), s.getY() - z.getY()); if (d < dn) dn = d; }
  z._dn = dn;
  const f = Math.max(0, Math.min(1, (320 - dn) / 120)), ox = Math.cos(v.get("Ang").getAsNumber()) * 56 * f, oy = Math.sin(v.get("Ang").getAsNumber()) * 56 * f;
  if (f > 0 && !libre(z.getX() + ox, z.getY() + oy)) { v.get("OffX").setNumber(0); v.get("OffY").setNumber(0); } else { v.get("OffX").setNumber(ox); v.get("OffY").setNumber(oy); }
  const k = Math.floor(z.getX() / R) + "," + Math.floor(z.getY() / R);
  (celda.get(k) || celda.set(k, []).get(k)).push(z);
}
for (const z of Z) {
  const cx = Math.floor(z.getX() / R), cy = Math.floor(z.getY() / R);
  for (let gx = -1; gx <= 1; gx++) for (let gy = -1; gy <= 1; gy++) {
    const l = celda.get((cx + gx) + "," + (cy + gy)); if (!l) continue;
    for (const w of l) {
      if (w === z) continue;
      let dx = z.getX() - w.getX(), dy = z.getY() - w.getY(); const d = Math.hypot(dx, dy);
      if (d >= R) continue;
      if (d < 0.5) { dx = Math.random() - 0.5; dy = Math.random() - 0.5; }
      const dd = Math.hypot(dx, dy) || 1, push = Math.min(2.2, (R - d) * 0.12);
      const nx = z.getX() + dx / dd * push, ny = z.getY() + dy / dd * push;
      if (libre(nx, ny)) z.setPosition(nx, ny);
    }
  }
}
for (const z of Z) {
  const v = z.getVariables();
  z._ck = (z._ck || 0) + dt;
  if (z._ck < 0.4) continue;
  const mv = Math.hypot(z.getX() - z._px, z.getY() - z._py); z._px = z.getX(); z._py = z.getY(); z._ck = 0;
  if (v.get("Estado").getAsString() === "persigue" && mv < 6 && z._dn > 110) z._st += 0.4; else z._st = 0;
  if (z._st >= 1.2) {
    z._st = 0;
    try {
      const a = Math.random() * 6.2832, pf = z.getBehavior("Pathfinding");
      if (pf && pf.moveTo) { pf.moveTo(scn, z.getX() + Math.cos(a) * 230, z.getY() + Math.sin(a) * 230); z.resetTimer("ruta"); }
    } catch (e) { /* sin desatasco */ }
  }
}
"""
if not hay(J["events"], "IA"):
    J["events"].append(marca("IA")); J["events"].append(js_event(IA))

# bots: patrullan por el mapa, huyen de las masas y pelean si los acorralan
BOTS = r"""
/*FDIZ-FASE29-BOTS*/
const scn = runtimeScene;
if (scn.getGame().getVariables().get("NetRol").getAsNumber() === 2) return;
const SV = scn.getVariables();
if (SV.get("Jefe").getAsNumber() !== 1 || SV.get("Estado").getAsString() !== "juego" || SV.get("Pausa").getAsNumber() === 1) return;
const dt = Math.min(0.1, scn.getElapsedTime() / 1000);
const ZN = ["ZNormal", "ZCorredor", "ZGriton", "ZGordo", "ZConserje", "ZCurado"];
const Z = [];
for (const n of ZN) for (const z of (scn.getObjects(n) || [])) if (z.getVariables().get("Estado").getAsString() !== "muerto") Z.push(z);
const bots = (scn.getObjects("Sup") || []).filter((s) => s.getVariables().get("Control").getAsNumber() === -1 && s.getVariables().get("Estado").getAsString() === "normal");
if (!bots.length) return;
const NAV = gdjs.fdizNav, grid = NAV && NAV.grid;
const libre = (x, y) => { if (!grid) return true; const cx = Math.floor(x / NAV.cfg.C), cy = Math.floor(y / NAV.cfg.C); if (cx < 0 || cy < 0 || cx >= grid.W || cy >= grid.H) return false; return grid.cls[cy * grid.W + cx] === 0; };
const H = scn._f29b || (scn._f29b = { t: 0, tgt: null, next: 0 }); H.t += dt;
let gx = 0, gy = 0; for (const b of bots) { gx += b.getX(); gy += b.getY(); } gx /= bots.length; gy /= bots.length;
if (!H.tgt || H.t > H.next || Math.hypot(gx - H.tgt.x, gy - H.tgt.y) < 170) {
  const cand = [];
  for (const o of (scn.getObjects("Contenedor") || [])) { const d = Math.hypot(o.getX() - gx, o.getY() - gy); if (d > 350 && d < 1900 && libre(o.getX(), o.getY() + 60)) cand.push({ x: o.getX(), y: o.getY() + 60 }); }
  if (cand.length) H.tgt = cand[Math.floor(Math.random() * cand.length)]; else H.tgt = { x: SV.get("SegX").getAsNumber(), y: SV.get("SegY").getAsNumber() };
  H.next = H.t + 14;
}
bots.forEach((b, i) => {
  const bv = b.getVariables(), bx = b.getX(), by = b.getY();
  let n = 0, zx = 0, zy = 0;
  for (const z of Z) { const d = Math.hypot(z.getX() - bx, z.getY() - by); if (d < 240) { n++; zx += z.getX(); zy += z.getY(); } }
  const vida = bv.get("Vida").getAsNumber(), vmax = Math.max(1, bv.get("VidaMax").getAsNumber()), bajo = vida / vmax < 0.4;
  let huye = bv.get("Huye").getAsNumber() === 1;
  b._calm = Math.max(0, (b._calm || 0) - dt);
  if (!huye && b._calm <= 0 && (n >= 4 || (n >= 2 && bajo))) { huye = true; b._fl = 2.5; b._ft = 0; }
  if (huye) { b._fl -= dt; if (b._fl <= 0 && n <= 1) huye = false; }
  b._chk = (b._chk || 0) + dt;
  if (b._chk >= 1.2) { const mv = Math.hypot(bx - (b._lx || bx), by - (b._ly || by)); b._lx = bx; b._ly = by; b._chk = 0; if (huye && mv < 25) { huye = false; b._calm = 3; } }
  let tx, ty;
  if (huye) {
    b._ft = (b._ft || 0) - dt;
    if (b._ft <= 0 || !b._esc) {
      b._ft = 0.5; let mejor = -1e9, pt = null;
      for (let k = 0; k < 12; k++) {
        const a = k * Math.PI / 6, px = bx + Math.cos(a) * 420, py = by + Math.sin(a) * 420;
        if (!libre(px, py)) continue;
        let md = 1e9; for (const z of Z) { const d = Math.hypot(z.getX() - px, z.getY() - py); if (d < md) md = d; }
        const sc = Math.min(md, 900) - Math.hypot(px - gx, py - gy) * 0.05;
        if (sc > mejor) { mejor = sc; pt = { x: px, y: py }; }
      }
      b._esc = pt || { x: bx - (zx / Math.max(1, n) - bx), y: by - (zy / Math.max(1, n) - by) };
    }
    tx = b._esc.x; ty = b._esc.y;
  } else {
    b._esc = null;
    const a = i * Math.PI / 2 + 0.6;
    tx = H.tgt.x + Math.cos(a) * 120; ty = H.tgt.y + Math.sin(a) * 120;
    if (!libre(tx, ty)) { tx = H.tgt.x; ty = H.tgt.y; }
  }
  bv.get("BotX").setNumber(tx); bv.get("BotY").setNumber(ty); bv.get("Huye").setNumber(huye ? 1 : 0);
});
"""
G11 = grupo(J, "Bots")
if not hay(G11["events"], "BOTS"):
    i0 = next(i for i, e in enumerate(G11["events"]) if e["type"].endswith("JsCode") and "FDIZ-FASE26-BOTS" in e["inlineCode"])
    G11["events"].insert(i0 + 1, marca("BOTS")); G11["events"].insert(i0 + 2, js_event(BOTS))
# el bot que huye no corre hacia el zombi más cercano
for e in walk(G11["events"]):
    if e["type"].endswith("Standard") and any(x["type"]["value"] == "PickNearest" and x["parameters"][:1] == ["Zombies"] for x in e["conditions"]):
        cc = c("VarObjet", "Sup", "Huye", "=", "0")
        if cc not in e["conditions"]: e["conditions"].insert(0, cc)

# =====================================================================
# 7 · ONLINE (net_core.js): fondo detrás de cada texto fuera de la sala
# =====================================================================
NET = os.path.join(AQUI, "net_core.js")
js = open(NET, encoding="utf-8").read()
if "FDIZ-F29" not in js:
    def rep(viejo, nuevo):
        global js
        assert js.count(viejo) == 1, viejo[:60]
        js = js.replace(viejo, nuevo)
    rep("function T(scn, s, x, y, size, col, al, wrap) {",
        "function T(scn, s, x, y, size, col, al, wrap, nobg) {")
    rep('const w = o.getWidth(); o.setPosition(al === "left" ? x : (al === "right" ? x - (wrap || w) : x - (wrap || w) / 2), y);\n  }',
        'const w = o.getWidth(); o.setPosition(al === "left" ? x : (al === "right" ? x - (wrap || w) : x - (wrap || w) / 2), y);\n'
        '    /*FDIZ-F29*/ if (!nobg && N._bgOn !== false && String(s).trim()) {\n'
        '      const B = scn._netB || (scn._netB = { a: [], n: 0 }); let p = B.a[B.n++];\n'
        '      if (!p) { p = scn.createObject("FondoTxt"); p.setZOrder(19); B.a.push(p); }\n'
        '      p.hide(false); p.setPosition(o.getX() - 26, o.getY() - 10); p.setWidth(o.getWidth() + 52); p.setHeight(o.getHeight() + 20);\n'
        '    }\n  }')
    rep("const P = poolOf(scn); P.n = 0;", "const P = poolOf(scn); P.n = 0; { const B0 = scn._netB || (scn._netB = { a: [], n: 0 }); B0.n = 0; }")
    rep('jf0 ? 44 : 54, "255;230;120", "center");', 'jf0 ? 44 : 54, "255;230;120", "center", 0, true);')
    rep("      lobbyUi(scn, I, { up, dn, ok, esc, pad, IDX, pe });", "      N._bgOn = false; lobbyUi(scn, I, { up, dn, ok, esc, pad, IDX, pe });")
    rep("    for (let i = P.n; i < P.a.length; i++) P.a[i].hide(true);",
        "    if (u.st !== \"lobby\") N._bgOn = true;\n    { const B1 = scn._netB; if (B1) for (let i = B1.n; i < B1.a.length; i++) B1.a[i].hide(true); }\n    for (let i = P.n; i < P.a.length; i++) P.a[i].hide(true);")
    open(NET, "w", encoding="utf-8").write(js)
if not any(o["name"] == "FondoTxt" for o in O["objects"]):
    O["objects"].append(copy.deepcopy(PANEL))

json.dump(d, open(PRY, "w"), ensure_ascii=False, indent=2)
print("OK fase 29")
