/* FDI-Z · Fase 52 · Lanzables: impacto = distracción + daño en área. Se ejecuta DENTRO del ForEach de Proyectil (objects = proyectiles elegidos),
 * justo antes del evento que los borra (Pego = 1). Balón y libro hacen ruido: los zombis cercanos van hacia donde cayó unos segundos
 * (estado "distraido"; lo mueve lanz_frame.js) y reciben un daño en área. La engrapadora no distrae (son 8 disparos seguidos). */
(function () {
  "use strict";
  const scn = runtimeScene;
  if (scn.getGame().getVariables().get("NetRol").getAsNumber() === 2) return;
  const LZ = scn._fdizLz || (scn._fdizLz = { rings: [] });
  const CFG = {
    balon: { radio: 650, seg: 5, splashR: 120, splash: 5 },
    libro: { radio: 550, seg: 4, splashR: 110, splash: 8 },
  };
  const ZN = ["ZNormal", "ZCorredor", "ZGriton", "ZGordo"];
  const T = scn.getTimeManager().getTimeFromStart();
  for (const p of objects) {
    const g = p.getVariables();
    if (g.get("Pego").getAsNumber() !== 1 || p._lzDone) continue;
    p._lzDone = true;
    const c = CFG[g.get("Tipo").getAsString()]; if (!c) continue;
    const x = p.getX(), y = p.getY() + 40;
    LZ.rings.push({ x, y, t0: T, r: c.splashR });
    for (const n of ZN) {
      const arr = scn.getObjects(n) || [];
      for (const z of arr) {
        const v = z.getVariables(), est = v.get("Estado").getAsString();
        if (est === "muerto" || v.get("Aliado").getAsNumber() === 1) continue;
        const d = Math.hypot(z.getX() - x, z.getY() - y);
        if (d <= c.splashR) {   // daño en área
          v.get("Vida").setNumber(v.get("Vida").getAsNumber() - c.splash);
          v.get("UltJugador").setNumber(g.get("Jugador").getAsNumber());
          try { z.setColor("255;90;90"); z.resetTimer("tinte"); } catch (e) {}
          try { const t = scn.createObject("TxtDanio"); t.setPosition(z.getX(), z.getY() - 110); t.setText(String(c.splash)); t.resetTimer("vida"); } catch (e) {}
        }
        if (d <= c.radio && v.get("Vida").getAsNumber() > 0 && (est === "persigue" || est === "paseando" || est === "guardia")) {
          z._lz = { x, y, t: T + c.seg, next: 0 };
          v.get("Estado").setString("distraido");
        }
      }
    }
  }
})();
