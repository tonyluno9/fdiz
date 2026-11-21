/* FDI-Z · Fase 53 · Flechas de aliados fuera de pantalla (bloque Jugabilidad y mecánicas, parte 4).
 * Se incrusta con scripts/fase53_flechas.py justo después del evento del minimapa. Por cada aliado vivo (alumnos y profes) que queda fuera de lo que
 * ve la cámara, dibuja en el borde de la pantalla una flecha con su color y su nombre apuntando hacia él. Los caídos y mordidos parpadean y lo indican.
 * Solo en la partida normal (no en pausa, cinemáticas, modo Jefe ni con el cuadro de lanzables abierto). */
(function () {
  "use strict";
  const scn = runtimeScene, V = scn.getVariables();
  const dib = (scn.getObjects("FlechasDib") || [])[0];
  if (!dib) return;
  const U = scn._fdizFlechas || (scn._fdizFlechas = { tx: [] });
  dib.setLayer("HUD"); dib.setZOrder(70000); dib.clear();
  const lzAbierto = scn._fdizLzUi && scn._fdizLzUi.open;
  const ver = V.get("Estado").getAsString() === "juego" && V.get("Pausa").getAsNumber() !== 1 && V.get("Jefe").getAsNumber() !== 1 && !lzAbierto;
  let n = 0;
  if (ver) {
    const L = scn.getLayer(""), z = Math.max(0.1, L.getCameraZoom ? L.getCameraZoom() : 1), cx = L.getCameraX(), cy = L.getCameraY();
    const PLAY = ["255;215;80", "100;170;255", "120;220;110", "255;120;190"];
    const t = scn.getTimeManager().getTimeFromStart();
    const X0 = 70, X1 = 1850, Y0 = 70, Y1 = 1010, CX = 960, CY = 540;
    for (const s of scn.getObjects("Sup") || []) {
      const g = s.getVariables(), est = g.get("Estado").getAsString();
      if (est === "muerto" || est === "fuera") continue;
      const sx = (s.getX() - cx) * z + CX, sy = (s.getY() - 40 - cy) * z + CY;
      if (sx >= 40 && sx <= 1880 && sy >= 40 && sy <= 1040) continue;       // se ve en pantalla
      const dx = sx - CX, dy = sy - CY;
      const k = Math.min((X1 - CX) / Math.max(1e-6, Math.abs(dx)), (Y1 - CY) / Math.max(1e-6, Math.abs(dy)));
      const ex = CX + dx * k, ey = CY + dy * k, a = Math.atan2(dy, dx);
      const pj = g.get("Jugador").getAsNumber() || 1, mal = est !== "normal" || g.get("Mordido").getAsNumber() > 0;
      const op = mal ? Math.round(120 + 135 * (0.5 + 0.5 * Math.sin(t * 8))) : 255;
      const col = est !== "normal" ? "140;140;140" : (pj > 4 ? "200;160;255" : PLAY[(pj - 1) % 4]);
      const c = Math.cos(a), sn = Math.sin(a), L1 = 30, W1 = 20;
      dib.setFillColor(col); dib.setFillOpacity(op); dib.setOutlineColor(mal ? "255;80;80" : "255;255;255"); dib.setOutlineOpacity(op); dib.setOutlineSize(3);
      // triángulo relleno hecho con líneas (el pintor no tiene drawTriangle): punta + base
      const tx = ex + c * L1, ty = ey + sn * L1, b1x = ex - c * 10 - sn * W1, b1y = ey - sn * 10 + c * W1, b2x = ex - c * 10 + sn * W1, b2y = ey - sn * 10 - c * W1;
      dib.setOutlineColor(col); dib.setOutlineOpacity(op);
      for (let i = 0; i <= 10; i++) { const f = i / 10; dib.drawLine(tx, ty, b1x + (b2x - b1x) * f, b1y + (b2y - b1y) * f, 5); }
      dib.setOutlineColor(mal ? "255;80;80" : "255;255;255");
      dib.drawLine(tx, ty, b1x, b1y, 3); dib.drawLine(tx, ty, b2x, b2y, 3); dib.drawLine(b1x, b1y, b2x, b2y, 3);
      // nombre (hacia adentro de la pantalla)
      let o = U.tx[n];
      if (!o) { o = scn.createObject("JfTexto"); o.setLayer("HUD"); o.setZOrder(70001); U.tx[n] = o; o._k = ""; }
      const nom = String(g.get("Personaje").getAsString() || "");
      const s1 = (nom.charAt(0).toUpperCase() + nom.slice(1)) + (est === "caido" ? " (caído)" : (est !== "normal" ? " (" + est + ")" : (mal ? " (mordido)" : "")));
      if (o._k !== s1) { o._k = s1; o.setText(s1); o.setCharacterSize(20); o.setColor("255;255;255"); o.setTextAlignment("center"); o.setWrapping(false); }
      o.hide(false);
      const tw = o.getWidth ? o.getWidth() : 100;
      o.setPosition(Math.max(8, Math.min(1912 - tw, ex - c * 64 - tw / 2)), ey - sn * 50 - 12);
      n++;
    }
  }
  for (let i = n; i < U.tx.length; i++) if (U.tx[i]) U.tx[i].hide(true);
})();
