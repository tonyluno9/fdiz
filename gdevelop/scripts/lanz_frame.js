/* FDI-Z · Fase 52 · Lanzables: mueve a los zombis distraídos, dibuja las ondas de impacto y muestra el cuadro explicativo del primer lanzable.
 * Se ejecuta cada cuadro justo después del grupo "Lanzables".
 * Cuadro: la primera vez que un jugador HUMANO recoge un lanzable en la partida (variable de escena LanzInfo, que se reinicia con la escena)
 * sale un aviso que detiene el juego (solo sin red: TimeScale 0) hasta que se cierra con clic, Enter, Espacio, Esc o A. Después no vuelve a salir. */
(function () {
  "use strict";
  const scn = runtimeScene, V = scn.getVariables();
  const rol = scn.getGame().getVariables().get("NetRol").getAsNumber();
  const LZ = scn._fdizLz || (scn._fdizLz = { rings: [] });
  const T = scn.getTimeManager().getTimeFromStart();
  const ahora = () => Date.now() / 1000;
  const first = (n) => { const a = scn.getObjects(n); return a && a.length ? a[0] : null; };
  const sups = scn.getObjects("Sup") || [];

  // ---------- zombis distraídos ----------
  if (rol !== 2 && V.get("Estado").getAsString() === "juego" && V.get("Pausa").getAsNumber() !== 1) {
    for (const n of ["ZNormal", "ZCorredor", "ZGriton", "ZGordo"]) {
      for (const z of scn.getObjects(n) || []) {
        const v = z.getVariables();
        if (v.get("Estado").getAsString() !== "distraido") continue;
        const L = z._lz;
        const fin = () => { v.get("Estado").setString("persigue"); try { z.resetTimer("ruta"); z.resetTimer("ataque"); } catch (e) {} };
        if (!L || T > L.t) { fin(); continue; }
        if (sups.some((s) => s.getVariables().get("Estado").getAsString() === "normal" && Math.hypot(s.getX() - z.getX(), s.getY() - z.getY()) < 150)) { fin(); continue; }
        if (Math.hypot(L.x - z.getX(), L.y - z.getY()) > 45 && T >= L.next) {
          L.next = T + 0.5;
          try { const b = z.getBehavior("Pathfinding"); if (b && b.moveTo) b.moveTo(scn, L.x, L.y); } catch (e) {}
        }
      }
    }
  }

  // ---------- ondas de impacto (mundo) ----------
  const mundo = first("LzMundo");
  if (mundo) {
    mundo.setLayer("Juego"); mundo.setZOrder(99990); mundo.clear();
    LZ.rings = LZ.rings.filter((r) => T - r.t0 < 0.7);
    for (const r of LZ.rings) {
      const k = (T - r.t0) / 0.7;
      mundo.setFillOpacity(Math.round(50 * (1 - k))); mundo.setFillColor("255;200;90"); mundo.setOutlineColor("255;240;180"); mundo.setOutlineOpacity(Math.round(255 * (1 - k))); mundo.setOutlineSize(4);
      mundo.drawCircle(r.x, r.y, 20 + (r.r + 40) * k);
      mundo.setFillOpacity(0); mundo.drawCircle(r.x, r.y, 10 + (r.r + 40) * Math.min(1, k * 1.5));
    }
  }

  // ---------- cuadro del primer lanzable ----------
  const dib = first("LzInfo");
  if (!dib) return;
  dib.setLayer("HUD"); dib.setZOrder(80000); dib.clear();
  if (!scn._fdizLzUi) scn._fdizLzUi = { open: false, tx: [], prev: {}, t0: 0, cierre: 0 };
  const U = scn._fdizLzUi;
  const I = scn.getGame().getInputManager();
  const hay = V.get("Estado").getAsString() === "juego" && V.get("Jefe").getAsNumber() !== 1;
  if (!U.open && hay && rol === 0 && V.get("LanzInfo").getAsNumber() === 0 && V.get("Pausa").getAsNumber() !== 1 &&
      sups.some((s) => { const g = s.getVariables(); return g.get("Control").getAsNumber() >= 0 && g.get("Estado").getAsString() === "normal" && g.get("Lanz").getAsString() !== ""; })) {
    U.open = true; U.t0 = ahora(); U.prev = null;
    V.get("LanzInfo").setNumber(1);
    if (rol === 0) scn.getTimeManager().setTimeScale(0);
  }
  if (U.open) {
    V.get("ProfDlg").setNumber(1);   // bloquea la pausa (Esc / P / Start) mientras el cuadro está abierto
    const cur = { clic: I.isMouseButtonPressed(0), k: [13, 32, 27].some((c) => I.isKeyPressed(c)), a: false };
    try { const gp = navigator.getGamepads ? navigator.getGamepads() : []; for (let i = 0; i < 4; i++) if (gp && gp[i] && gp[i].buttons[0] && gp[i].buttons[0].pressed) cur.a = true; } catch (e) {}
    const edge = U.prev ? ((cur.clic && !U.prev.clic) || (cur.k && !U.prev.k) || (cur.a && !U.prev.a)) : false;
    U.prev = cur;
    // dibujo
    const W = 1920, H = 1080, px = 430, py = 190, pw = 1060, ph = 700;
    dib.setOutlineSize(0); dib.setFillColor("0;0;0"); dib.setFillOpacity(165); dib.drawRectangle(0, 0, W, H);
    dib.setFillColor("14;18;44"); dib.setFillOpacity(245); dib.setOutlineColor("255;215;80"); dib.setOutlineOpacity(255); dib.setOutlineSize(5); dib.drawRectangle(px, py, px + pw, py + ph);
    const p = 0.5 + 0.5 * Math.sin(ahora() * 5);
    dib.setFillColor("255;215;80"); dib.setFillOpacity(Math.round(170 + 60 * p)); dib.setOutlineColor("120;80;0"); dib.setOutlineSize(3);
    dib.drawRectangle(W / 2 - 170, py + ph - 100, W / 2 + 170, py + ph - 36);
    const txt = (i, s, x, y, size, color, align, w) => {
      let o = U.tx[i];
      if (!o) { o = scn.createObject("JfTexto"); o.setLayer("HUD"); o.setZOrder(80001); o.setWrapping(true); U.tx[i] = o; o._k = ""; }
      const key = s + "|" + size + "|" + color + "|" + align + "|" + w;
      if (o._k !== key) { o._k = key; o.setText(s); o.setCharacterSize(size); o.setColor(color); o.setTextAlignment(align); o.setWrappingWidth(w); }
      o.hide(false); o.setPosition(x, y);
    };
    txt(0, "¡OBJETO LANZABLE!", px, py + 26, 52, "255;215;80", "center", pw);
    txt(1, "Balones, libros y engrapadoras se lanzan.", px + 50, py + 120, 30, "255;255;255", "left", pw - 100);
    txt(2, "Lanzar:  R o clic derecho (teclado)  ·  B (mando)", px + 50, py + 175, 30, "170;230;255", "left", pw - 100);
    txt(3, "Al caer, el balón y el libro hacen ruido: los zombis cercanos corren hacia donde cayó durante unos segundos, y además reciben daño en área. ¡Úsalos para distraerlos y escapar!", px + 50, py + 250, 30, "255;255;255", "left", pw - 100);
    txt(4, "Balón: empuja lejos.   Libro: aturde 1 s.   Engrapadora: 8 grapas rápidas.", px + 50, py + 420, 28, "255;225;140", "left", pw - 100);
    txt(5, "Se recogen pasando encima si no traes otro. El balón y el libro se gastan al lanzarlos.", px + 50, py + 480, 24, "200;200;220", "left", pw - 100);
    txt(6, "CONTINUAR", W / 2 - 170, py + ph - 88, 38, "40;24;0", "center", 340);
    txt(7, "(clic, Enter, Espacio o A)", px, py + ph - 28, 20, "200;200;220", "center", pw);
    if (edge && ahora() - U.t0 > 0.5) {
      U.open = false; U.cierre = ahora() + 0.4;
      for (const o of U.tx) if (o) o.hide(true);
      V.get("ProfDlg").setNumber(2);
      if (rol === 0 && V.get("Pausa").getAsNumber() === 0) scn.getTimeManager().setTimeScale(1);
    }
  } else {
    for (const o of U.tx) if (o) o.hide(true);
  }
})();
