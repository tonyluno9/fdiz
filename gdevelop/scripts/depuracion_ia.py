"""Depuracion temporal de IA (zombis y bots): inserta/quita un evento JavaScript que escribe _dbg/ia.log cada 1 s.
Uso:  python depuracion_ia.py <FDI-Z.json> on|off      (solo para pruebas; quitarlo con "off" antes de entregar)"""
import json, sys
ruta, modo = sys.argv[1], sys.argv[2]
p = json.load(open(ruta, encoding="utf-8"))
J = next(l for l in p["layouts"] if l["name"] == "Juego")
MARCA = "FDIZ-DBG"
J["events"] = [e for e in J["events"] if not (e.get("type", "").endswith("JsCode") and MARCA in e.get("inlineCode", ""))]
if modo == "on":
    ruta_log = "/Users/cesar/fdiz/_dbg/ia.log"
    codigo = r"""/*FDIZ-DBG*/
(function(){
  const scn = runtimeScene; const D = (gdjs.fdizDbg = gdjs.fdizDbg || {});
  const t = scn.getTimeManager().getTimeFromStart() / 1000;
  if (D.next === undefined || t < D.next - 5) D.next = 0;
  if (t < D.next) return; D.next = t + 1;
  let fs; try { fs = require("fs"); } catch (e) { if (!D.warned) { D.warned = true; console.log("FDIZ-DBG sin fs"); } return; }
  const dir = "/Users/cesar/fdiz/_dbg"; try { fs.mkdirSync(dir, { recursive: true }); } catch (e) {}
  const lines = [];
  const gv = (o, n) => { try { const v = o.getVariables().get(n); return v.getType() === "string" ? v.getAsString() : Math.round(v.getAsNumber() * 100) / 100; } catch (e) { return null; } };
  const R = (v) => Math.round(v);
  for (const tn of ["ZNormal","ZGriton","ZGordo","ZConserje","ZCorredor","ZTanque","ZRapido","ZJefe","ZProfe"]) {
    const l = scn.getObjects(tn); if (!l) continue;
    for (const o of l) {
      let pf = null; try { const b = o.getBehavior("Pathfinding"); pf = [b._pathFound ? 1 : 0, b._reachedEnd ? 1 : 0, R(b._speed || 0), (b._path || []).length, b._currentSegment]; } catch (e) {}
      lines.push(JSON.stringify({ t: R(t), k: "Z", n: tn, id: o.id, x: R(o.getX()), y: R(o.getY()), e: gv(o, "Estado"), v: gv(o, "Vida"), a: o.getAnimationName ? o.getAnimationName() : "", pf }));
    }
  }
  const sl = scn.getObjects("Sup") || [];
  for (const o of sl) {
    let pb = null; try { const b = o.getBehavior("PathBot"); pb = [b._pathFound ? 1 : 0, b._reachedEnd ? 1 : 0, (b._path || []).length, b._currentSegment]; } catch (e) {}
    lines.push(JSON.stringify({ t: R(t), k: "S", id: o.id, pj: gv(o, "Personaje"), j: gv(o, "Jugador"), c: gv(o, "Control"), x: R(o.getX()), y: R(o.getY()), e: gv(o, "Estado"), mx: gv(o, "MovX"), my: gv(o, "MovY"), a: o.getAnimationName ? o.getAnimationName() : "", pb }));
  }
  try { fs.appendFileSync(dir + "/ia.log", lines.join("\n") + "\n"); } catch (e) { if (!D.w2) { D.w2 = 1; console.log("FDIZ-DBG error", e); } }
})();
"""
    J["events"].insert(1, {"type": "BuiltinCommonInstructions::JsCode", "inlineCode": codigo, "parameterObjects": "", "useStrict": True, "eventsSheetExpanded": False})
json.dump(p, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("depuracion", modo)
