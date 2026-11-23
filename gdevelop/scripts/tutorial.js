/* FDI-Z · Fase 83 · Tutorial de controles al empezar la partida.
 * Se incrusta en la escena Juego con scripts/fase83_impactos_mira_tutorial.py (no editar el evento a mano): evento
 * FDIZ-FASE83-TUTORIAL al final de la escena, cada cuadro.
 * La primera vez que empieza una partida en esta sesión del juego (Estado = "juego", sin cinemática en curso, sin red y
 * fuera del modo Jefe) sale un cuadro que detiene el juego (TimeScale 0) con lo básico: moverse, atacar con la mira,
 * correr, usar, habilidades, lanzar y pausa, más las imágenes de los controles (teclado y ratón / control de Xbox).
 * Se cierra con clic, Enter, Espacio, Esc o A; el clic que lo cierra no golpea (usa el mismo bloqueo de entrada que el
 * cuadro de los lanzables, scn._fdizLzUi.cierre). No vuelve a salir hasta que se recargue el juego. */
(function (gdjs) {
  "use strict";
  if (gdjs.fdizTuto && gdjs.fdizTuto.VER === 1) return;
  const T = (gdjs.fdizTuto = { VER: 1, visto: false });

  T.LINEAS = [
    ["MOVERSE", "W A S D", "Stick izquierdo"],
    ["ATACAR", "Clic izquierdo: pega o dispara hacia la mira", "X"],
    ["APUNTAR", "La mira sigue al ratón", "Stick derecho"],
    ["CORRER", "Shift (gasta estamina)", "LB o L3"],
    ["USAR / ABRIR / REVIVIR", "Mantén F", "Mantén A"],
    ["HABILIDAD · ESPECIAL", "Q  ·  E", "Y  ·  RB"],
    ["LANZAR OBJETO", "R o clic derecho", "B"],
    ["PAUSA", "Esc o P", "Start"],
  ];
  const ahora = () => Date.now() / 1000;
  const SV = (scn, n) => scn.getVariables().get(n);
  const str = (scn, n) => { try { return SV(scn, n).getAsString(); } catch (e) { return ""; } };

  T.tick = function (scn) {
    const rol = scn.getGame().getVariables().get("NetRol").getAsNumber();
    const U = scn._fdizTuto || (scn._fdizTuto = { open: false, tx: [], img: [], dib: null, prev: null, t0: 0 });
    const I = scn.getGame().getInputManager();
    const cine = (str(scn, "CineModo") !== "" && str(scn, "CineModo") !== "0") || (str(scn, "HistCine") !== "" && str(scn, "HistCine") !== "0");
    if (!U.open && !T.visto && rol === 0 && str(scn, "Estado") === "juego" && SV(scn, "Jefe").getAsNumber() !== 1 &&
        SV(scn, "Pausa").getAsNumber() !== 1 && !cine && !(scn._fdizLzUi && scn._fdizLzUi.open)) {
      U.open = true; T.visto = true; U.t0 = ahora(); U.prev = null;
      scn.getTimeManager().setTimeScale(0);
    }
    // flecha del sistema: oculta si armas.js puso la mira en el cursor (se aplica aquí, al final, porque otro módulo la
    // vuelve a poner en cada cuadro)
    try { const c = scn.getGame().getRenderer().getCanvas(); const v = scn.__fdizSinFlecha && !U.open ? "none" : ""; if (c && c.style.cursor !== v && (v === "none" || c.style.cursor === "none")) c.style.cursor = v; } catch (e) { /* sin lienzo */ }
    if (!U.open) return;
    SV(scn, "ProfDlg").setNumber(1);                               // bloquea la pausa mientras está abierto
    const L = scn._fdizLzUi || (scn._fdizLzUi = { open: false, tx: [], prev: {}, t0: 0, cierre: 0 });
    L.cierre = ahora() + 0.4;                                      // sin moverse ni pegar mientras está y 0.4 s después

    // ---- dibujo
    if (!U.dib) { U.dib = scn.createObject("LzInfo"); if (U.dib) { U.dib.setLayer("HUD"); U.dib.setZOrder(90000); } }
    const d = U.dib; if (!d) return;
    const W = 1920, H = 1080, px = 150, py = 70, pw = 1620, ph = 940;
    d.clear();
    d.setOutlineSize(0); d.setFillColor("0;0;0"); d.setFillOpacity(190); d.drawRectangle(0, 0, W, H);
    d.setFillColor("14;18;44"); d.setFillOpacity(248); d.setOutlineColor("120;220;110"); d.setOutlineOpacity(255); d.setOutlineSize(5);
    d.drawRectangle(px, py, px + pw, py + ph);
    const pulso = 0.5 + 0.5 * Math.sin(ahora() * 5);
    d.setFillColor("120;220;110"); d.setFillOpacity(Math.round(170 + 60 * pulso)); d.setOutlineColor("20;70;20"); d.setOutlineSize(3);
    d.drawRectangle(W / 2 - 190, py + ph - 98, W / 2 + 190, py + ph - 34);

    let i = 0;
    const txt = (s, x, y, size, color, align, w) => {
      let o = U.tx[i];
      if (!o) { o = scn.createObject("JfTexto"); if (!o) return; o.setLayer("HUD"); o.setZOrder(90002); o.setWrapping(true); U.tx[i] = o; o._k = ""; }
      const key = s + "|" + size + "|" + color + "|" + align + "|" + w;
      if (o._k !== key) { o._k = key; o.setText(s); o.setCharacterSize(size); o.setColor(color); o.setTextAlignment(align); o.setWrappingWidth(w); }
      o.hide(false); o.setPosition(x, y); i++;
    };
    txt("CÓMO SE JUEGA", px, py + 22, 54, "120;220;110", "center", pw);
    txt("Objetivo: cumplan las misiones de arriba y escapen. Mantengan al equipo vivo.", px, py + 92, 26, "220;220;235", "center", pw);
    // tabla: acción · teclado y ratón · mando
    const c1 = px + 70, c2 = px + 560, c3 = px + 1210, y0 = py + 150, dy = 44;
    txt("ACCIÓN", c1, y0, 22, "150;160;190", "left", 460);
    txt("TECLADO Y RATÓN", c2, y0, 22, "150;160;190", "left", 620);
    txt("CONTROL", c3, y0, 22, "150;160;190", "left", 360);
    T.LINEAS.forEach((l, k) => {
      const y = y0 + 38 + k * dy;
      txt(l[0], c1, y, 26, "255;215;80", "left", 470);
      txt(l[1], c2, y, 26, "255;255;255", "left", 630);
      txt(l[2], c3, y, 26, "170;230;255", "left", 360);
    });
    // imágenes de los controles (las mismas de la pantalla de controles de la pausa)
    const yi = y0 + 38 + T.LINEAS.length * dy + 14, hImg = py + ph - 120 - yi;
    [["CtlTeclado", px + 70], ["CtlMando", px + pw / 2 + 20]].forEach(([n, x], k) => {
      let o = U.img[k];
      if (!o) { o = scn.createObject(n); if (!o) return; o.setLayer("HUD"); o.setZOrder(90001); U.img[k] = o; }
      o.hide(false);
      const esc = Math.min((pw / 2 - 90) / o.getWidth() * o.getScaleX(), hImg / o.getHeight() * o.getScaleY());
      if (Math.abs(o.getScaleX() - esc) > 0.001) o.setScale(esc);
      o.setPosition(x + (pw / 2 - 90 - o.getWidth()) / 2, yi);
    });
    txt("CONTINUAR", W / 2 - 190, py + ph - 88, 38, "10;40;10", "center", 380);
    txt("(clic, Enter, Espacio o A)", px, py + ph - 28, 20, "200;200;220", "center", pw);
    for (let k = i; k < U.tx.length; k++) if (U.tx[k]) U.tx[k].hide(true);

    // ---- cerrar
    const cur = { clic: I.isMouseButtonPressed(0), k: [13, 32, 27].some((c) => I.isKeyPressed(c)), a: false };
    try { const gp = navigator.getGamepads ? navigator.getGamepads() : []; for (let g = 0; g < 4; g++) if (gp && gp[g] && gp[g].buttons[0] && gp[g].buttons[0].pressed) cur.a = true; } catch (e) { /* sin mandos */ }
    // también al soltar (un clic rápido puede presionar y soltar dentro del mismo cuadro)
    const solto = (() => { try { return I.isMouseButtonReleased(0) || [13, 32, 27].some((c) => I.wasKeyReleased(c)); } catch (e) { return false; } })();
    const edge = U.prev ? ((cur.clic && !U.prev.clic) || (cur.k && !U.prev.k) || (cur.a && !U.prev.a) || solto) : false;
    U.prev = cur;
    if (edge && ahora() - U.t0 > 0.6) {
      U.open = false;
      for (const o of U.tx) if (o) o.hide(true);
      for (const o of U.img) if (o) o.hide(true);
      d.clear();
      SV(scn, "ProfDlg").setNumber(2);
      if (SV(scn, "Pausa").getAsNumber() === 0) scn.getTimeManager().setTimeScale(1);
    }
  };
})(gdjs);
