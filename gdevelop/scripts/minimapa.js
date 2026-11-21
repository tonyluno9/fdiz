/* FDI-Z · Fase 50 · Minimapa del modo normal (bloque Jugabilidad y mecánicas, parte 1).
 * Se incrusta en la escena Juego con scripts/fase50_minimapa.py (editar este archivo y volver a correr el script).
 * Sprite "Minimapa" (dibujo del mapa) + pintor "MmDib" (marco, aliados, objetivo, cuadro de cámara) en la capa HUD, a la derecha.
 * Se ve solo en la partida normal (no en modo Jefe, que tiene el suyo). La tecla M lo muestra/oculta.
 * No muestra zombis a propósito (para no quitar tensión): solo aliados, objetivo y lo que enfoca la cámara. */
(function () {
  "use strict";
  const scn = runtimeScene;
  const V = scn.getVariables();
  if (V.get("Jefe").getAsNumber() === 1) return;
  const MM = { x: 1596, y: 446, w: 300, h: 184 };
  const WW = 8768, WH = 5376;
  const PLAY = ["255;215;80", "100;170;255", "120;220;110", "255;120;190"];
  const first = (n) => { const a = scn.getObjects(n); return a && a.length ? a[0] : null; };
  const spr = first("Minimapa"), dib = first("MmDib");
  if (!spr || !dib) return;
  if (!scn._fdizMini) scn._fdizMini = { on: true, init: false };
  const S = scn._fdizMini;
  const im = scn.getGame().getInputManager();
  if (im.wasKeyReleased(77)) S.on = !S.on; // M
  const juego = V.get("Estado").getAsString() === "juego" && V.get("Pausa").getAsNumber() !== 1;
  const ver = juego && S.on;
  if (!S.init) { S.init = true; spr.setLayer("HUD"); dib.setLayer("HUD"); spr.setZOrder(5); dib.setZOrder(6); }
  spr.hide(!ver); dib.hide(!ver);
  dib.clear();
  if (!ver) return;
  spr.setPosition(MM.x, MM.y); spr.setWidth(MM.w); spr.setHeight(MM.h); spr.setOpacity(215);
  const mx = (wx) => MM.x + Math.max(0, Math.min(WW, wx)) * MM.w / WW, my = (wy) => MM.y + Math.max(0, Math.min(WH, wy)) * MM.h / WH;
  // marco
  dib.setFillOpacity(0); dib.setOutlineColor("70;190;170"); dib.setOutlineOpacity(255); dib.setOutlineSize(4);
  dib.drawRectangle(MM.x - 4, MM.y - 4, MM.x + MM.w + 4, MM.y + MM.h + 4);
  // objetivo actual
  const ot = V.get("ObjTipo").getAsString(), ox = V.get("ObjX").getAsNumber(), oy = V.get("ObjY").getAsNumber();
  if (ot && ot !== "" && ox > 0) {
    const t = scn.getTimeManager().getTimeFromStart(), r = 5 + (Math.sin(t * 5) > 0 ? 1.5 : 0);
    dib.setFillColor("255;225;40"); dib.setFillOpacity(255); dib.setOutlineColor("60;40;0"); dib.setOutlineSize(2);
    dib.drawRectangle(mx(ox) - r, my(oy) - r, mx(ox) + r, my(oy) + r);
  }
  // aliados (de pie = color del jugador; caídos/mordidos = gris; profes aliados = lila; humanos con borde blanco más grueso)
  const sups = scn.getObjects("Sup") || [];
  for (const s of sups) {
    const g = s.getVariables(), est = g.get("Estado").getAsString();
    if (est === "muerto" || est === "fuera") continue;
    const pj = g.get("Jugador").getAsNumber() || 1, ctl = g.get("Control").getAsNumber();
    const color = est !== "normal" ? "140;140;140" : (pj > 4 ? "200;160;255" : PLAY[(pj - 1) % 4]);
    dib.setFillColor(color); dib.setFillOpacity(255);
    dib.setOutlineColor("255;255;255"); dib.setOutlineOpacity(255); dib.setOutlineSize(ctl >= 0 ? 3 : 2);
    dib.drawCircle(mx(s.getX()), my(s.getY()), ctl >= 0 ? 6 : 5);
  }
  // cuadro de lo que ve la cámara
  const L = scn.getLayer(""), z = Math.max(0.1, L.getCameraZoom ? L.getCameraZoom() : 1);
  const cx = L.getCameraX(), cy = L.getCameraY(), vw = 1920 / z, vh = 1080 / z;
  dib.setFillOpacity(0); dib.setOutlineColor("255;255;255"); dib.setOutlineOpacity(210); dib.setOutlineSize(2);
  dib.drawRectangle(mx(cx - vw / 2), my(cy - vh / 2), mx(cx + vw / 2), my(cy + vh / 2));
})();
