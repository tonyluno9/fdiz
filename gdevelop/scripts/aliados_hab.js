/* FDI-Z · Fase 51 · Habilidades de aliados con clic (bloque Jugabilidad y mecánicas, parte 2).
 * Se incrusta con scripts/fase51_aliados_hab.py justo después del grupo "Entrada (teclado y controles)" (antes de que actúen bots y habilidades).
 * Clic en el icono Q (habilidad) o E (especial) del panel de un aliado bot = le pide usarla (PideHab / PideEsp). Si aún está en recarga no pasa nada
 * (se ve un destello rojo); si está lista, el bot la ejecuta (destello verde). Los bots siguen usándolas solos según su criterio.
 * Mientras el cursor está sobre uno de esos iconos, el clic no golpea con el ratón. Sin red cliente (NetRol 2) no actúa. */
(function () {
  "use strict";
  const scn = runtimeScene, V = scn.getVariables();
  if (scn.getGame().getVariables().get("NetRol").getAsNumber() === 2) return;
  const dib = (scn.getObjects("HabDib") || [])[0];
  if (!dib) return;
  const S = scn._fdizHabClick || (scn._fdizHabClick = { prev: false, flash: [] });
  dib.setLayer("HUD"); dib.setZOrder(60); dib.clear();
  if (V.get("Pausa").getAsNumber() === 1 || V.get("Estado").getAsString() !== "juego" || V.get("Jefe").getAsNumber() === 1) { S.prev = false; return; }
  const im = scn.getGame().getInputManager();
  const hp = scn.getLayer("HUD").convertCoords(im.getMouseX(), im.getMouseY(), 0), hx = hp[0], hy = hp[1];
  const down = im.isMouseButtonPressed(0), edge = down && !S.prev; S.prev = down;
  const T = scn.getTimeManager().getTimeFromStart();
  const sups = scn.getObjects("Sup") || [];
  const iconos = scn.getObjects("HudIcono") || [];
  const clamp01 = (v) => Math.max(0, Math.min(1, v));
  // --- efectos de iluminado ---
  function brackets(x0, y0, x1, y1, len, col, op, th) {   // cuatro esquinas en L
    dib.setOutlineColor(col); dib.setOutlineOpacity(op); dib.setFillOpacity(0); dib.setOutlineSize(th);
    for (const [px, py, sx, sy] of [[x0, y0, 1, 1], [x1, y0, -1, 1], [x0, y1, 1, -1], [x1, y1, -1, -1]]) {
      dib.drawLine(px, py, px + sx * len, py, th); dib.drawLine(px, py, px, py + sy * len, th);
    }
  }
  function hover(x0, y0, x1, y1, lista) {
    const p = 0.5 + 0.5 * Math.sin(T * 7), col = lista ? "120;255;220" : "255;190;90";
    // halo suave que respira (capas translúcidas hacia afuera)
    dib.setOutlineSize(0); dib.setFillColor(col);
    for (let i = 4; i >= 1; i--) { dib.setFillOpacity(Math.round((22 + 26 * p) / i)); dib.drawRectangle(x0 - i * 4, y0 - i * 4, x1 + i * 4, y1 + i * 4); }
    // brillo interior
    dib.setFillColor("255;255;255"); dib.setFillOpacity(Math.round(30 + 40 * p)); dib.drawRectangle(x0, y0, x1, y1);
    // marco fino + esquinas que se abren y cierran
    const o = 3 + 3 * p;
    dib.setFillOpacity(0); dib.setOutlineColor("255;255;255"); dib.setOutlineOpacity(220); dib.setOutlineSize(2); dib.drawRectangle(x0 - 1, y0 - 1, x1 + 1, y1 + 1);
    brackets(x0 - o, y0 - o, x1 + o, y1 + o, 14, col, 255, 4);
  }
  function onda(x0, y0, x1, y1, k, ok) {   // k: 0 (inicio) → 1 (fin)
    const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2, col = ok ? "90;255;140" : "255;80;80", f = 1 - k;
    dib.setFillOpacity(0); dib.setOutlineColor(col); dib.setOutlineSize(3);
    if (ok) {
      for (let r = 0; r < 2; r++) { const q = clamp01(k * 1.3 - r * 0.25); if (q <= 0 || q >= 1) continue; dib.setOutlineOpacity(Math.round(255 * (1 - q))); dib.drawCircle(cx, cy, 20 + 44 * q); }
      for (let i = 0; i < 10; i++) { const a = i * Math.PI / 5 + 0.3, r0 = 18 + 40 * k, r1 = r0 + 10 * f; dib.setOutlineOpacity(Math.round(255 * f)); dib.drawLine(cx + Math.cos(a) * r0, cy + Math.sin(a) * r0, cx + Math.cos(a) * r1, cy + Math.sin(a) * r1, 3); }
      dib.setFillColor(col); dib.setFillOpacity(Math.round(120 * f)); dib.setOutlineSize(0); dib.drawRectangle(x0, y0, x1, y1);
    } else {
      const sh = Math.sin(k * 40) * 3 * f, m = 8;
      dib.setOutlineOpacity(Math.round(255 * f)); dib.setOutlineSize(4);
      dib.drawLine(x0 + m + sh, y0 + m, x1 - m + sh, y1 - m, 5); dib.drawLine(x1 - m + sh, y0 + m, x0 + m + sh, y1 - m, 5);
      dib.setFillColor(col); dib.setFillOpacity(Math.round(80 * f)); dib.setOutlineSize(0); dib.drawRectangle(x0 + sh, y0, x1 + sh, y1);
    }
  }
  let sobre = false;
  for (let k = 1; k <= 4; k++) {
    const bot = sups.find((s) => s.getVariables().get("Jugador").getAsNumber() === k && s.getVariables().get("Control").getAsNumber() === -1);
    if (!bot) continue;
    const g = bot.getVariables(), vivo = g.get("Estado").getAsString() === "normal";
    for (const slot of [1, 2]) {
      const ic = iconos.find((o) => o.getVariables().get("Jugador").getAsNumber() === k && o.getVariables().get("Slot").getAsNumber() === slot);
      if (!ic) continue;
      const x0 = ic.getDrawableX(), y0 = ic.getDrawableY(), x1 = x0 + ic.getWidth(), y1 = y0 + ic.getHeight();
      const dentro = hx >= x0 && hx <= x1 && hy >= y0 && hy <= y1;
      const lista = g.get(slot === 1 ? "HabTxt" : "EspTxt").getAsString() === (slot === 1 ? "LISTA" : "LISTO");
      if (dentro && vivo) {
        sobre = true;
        hover(x0, y0, x1, y1, lista);
        if (edge) {
          if (lista) g.get(slot === 1 ? "PideHab" : "PideEsp").setNumber(1);
          S.flash[k * 3 + slot] = { t0: T, t: T + 0.55, ok: lista };
        }
      }
      const f = S.flash[k * 3 + slot];
      if (f && T < f.t) onda(x0, y0, x1, y1, (T - f.t0) / (f.t - f.t0), f.ok);
    }
  }
  // el clic sobre un icono no debe golpear
  if (sobre) for (const s of sups) { const g = s.getVariables(); if (g.get("Control").getAsNumber() === 0) g.get("QuierePegar").setNumber(0); }
})();
