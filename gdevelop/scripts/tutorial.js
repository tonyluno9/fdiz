/* FDI-Z · Fase 83 / 85 · Tutorial de controles al empezar la partida, por pasos.
 * Se incrusta en la escena Juego con scripts/fase83_impactos_mira_tutorial.py (evento FDIZ-FASE83-TUTORIAL, al final de la
 * escena; la fase 85 lo vuelve a incrustar).
 * La primera vez que empieza una partida en esta sesión (Estado = "juego", sin cinemática, sin red y fuera del modo Jefe)
 * se detiene el juego (TimeScale 0) y salen 3 cuadros, uno a la vez (fase 85: antes era una tabla con todo):
 *   1. MOVERSE: W A S D (o stick izquierdo), con Tony caminando de un lado a otro.
 *   2. ATACAR: con las manos o un arma cuerpo a cuerpo, clic izquierdo (X) y Tony pega; con pistola, apuntas con la mira
 *      (el ratón) y disparas igual, y Tony dispara a la mira.
 *   3. MÁS CONTROLES: correr, usar, habilidades, lanzar y pausa, con las imágenes de los controles.
 * Clic, Enter, Espacio o A pasan al siguiente; Retroceso / flecha izquierda regresa; Esc cierra. El clic que cierra no golpea
 * (usa el bloqueo de entrada del cuadro de los lanzables, scn._fdizLzUi.cierre). No vuelve a salir hasta recargar el juego.
 * Tony de muestra: objeto TutoTony (copia de las animaciones de Tony del objeto Sup, sin comportamientos ni variables). */
(function (gdjs) {
  "use strict";
  if (gdjs.fdizTuto && gdjs.fdizTuto.VER === 2) return;
  const T = (gdjs.fdizTuto = { VER: 2, visto: (gdjs.fdizTuto && gdjs.fdizTuto.visto) || false });

  T.RESTO = [
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
    const U = scn._fdizTuto || (scn._fdizTuto = { open: false, tx: [], img: {}, dib: null, prev: null, t0: 0, pag: 0, tp: 0 });
    const I = scn.getGame().getInputManager();
    const cine = (str(scn, "CineModo") !== "" && str(scn, "CineModo") !== "0") || (str(scn, "HistCine") !== "" && str(scn, "HistCine") !== "0");
    // flecha del sistema: oculta si armas.js puso la mira en el cursor (se aplica aquí, al final, porque otro módulo la
    // vuelve a poner en cada cuadro)
    try { const c = scn.getGame().getRenderer().getCanvas(); const v = scn.__fdizSinFlecha && !U.open ? "none" : ""; if (c && c.style.cursor !== v && (v === "none" || c.style.cursor === "none")) c.style.cursor = v; } catch (e) { /* sin lienzo */ }
    if (!U.open && !T.visto && rol === 0 && str(scn, "Estado") === "juego" && SV(scn, "Jefe").getAsNumber() !== 1 &&
        SV(scn, "Pausa").getAsNumber() !== 1 && !cine && !(scn._fdizLzUi && scn._fdizLzUi.open)) {
      U.open = true; T.visto = true; U.t0 = U.tp = ahora(); U.prev = null; U.pag = 0;
      scn.getTimeManager().setTimeScale(0);
    }
    if (!U.open) return;
    SV(scn, "ProfDlg").setNumber(1);                               // bloquea la pausa mientras está abierto
    const L = scn._fdizLzUi || (scn._fdizLzUi = { open: false, tx: [], prev: {}, t0: 0, cierre: 0 });
    L.cierre = ahora() + 0.4;                                      // sin moverse ni pegar mientras está y 0.4 s después

    // ---- dibujo
    if (!U.dib) { U.dib = scn.createObject("LzInfo"); if (U.dib) { U.dib.setLayer("HUD"); U.dib.setZOrder(90000); } }
    const d = U.dib; if (!d) return;
    const W = 1920, H = 1080, pw = 1180, ph = 760, px = (W - pw) / 2, py = (H - ph) / 2;
    const t = ahora() - U.tp;
    d.clear();
    d.setOutlineSize(0); d.setFillColor("0;0;0"); d.setFillOpacity(190); d.drawRectangle(0, 0, W, H);
    d.setFillColor("14;18;44"); d.setFillOpacity(248); d.setOutlineColor("120;220;110"); d.setOutlineOpacity(255); d.setOutlineSize(5);
    d.drawRectangle(px, py, px + pw, py + ph);
    const pulso = 0.5 + 0.5 * Math.sin(ahora() * 5);
    d.setFillColor("120;220;110"); d.setFillOpacity(Math.round(170 + 60 * pulso)); d.setOutlineColor("20;70;20"); d.setOutlineSize(3);
    d.drawRectangle(W / 2 - 190, py + ph - 98, W / 2 + 190, py + ph - 34);
    for (let k = 0; k < 3; k++) {                                  // puntitos de página
      d.setOutlineSize(0); d.setFillOpacity(255); d.setFillColor(k === U.pag ? "255;215;80" : "60;70;110");
      d.drawRectangle(W / 2 - 40 + k * 30, py + 30, W / 2 - 26 + k * 30, py + 44);
    }

    let i = 0;
    function txt(s, x, y, size, color, align, w) {
      let o = U.tx[i];
      if (!o) { o = scn.createObject("JfTexto"); if (!o) return; o.setLayer("HUD"); o.setZOrder(90002); o.setWrapping(true); U.tx[i] = o; o._k = ""; }
      const key = s + "|" + size + "|" + color + "|" + align + "|" + w;
      if (o._k !== key) { o._k = key; o.setText(s); o.setCharacterSize(size); o.setColor(color); o.setTextAlignment(align); o.setWrappingWidth(w); }
      o.hide(false); o.setPosition(x, y); i++;
    }
    // tecla dibujada (mismo estilo que los avisos de «usar»)
    function tecla(x, y, s) {
      const w = 64;
      d.setOutlineSize(0); d.setFillOpacity(255);
      d.setFillColor("10;12;20"); d.drawRectangle(x, y + 5, x + w, y + 69);
      d.setFillColor("236;236;242"); d.drawRectangle(x, y, x + w, y + 64);
      d.setFillColor("200;200;212"); d.drawRectangle(x, y + 52, x + w, y + 64);
      txt(s, x, y + 8, 36, "20;22;34", "center", w);
    }
    const usados = {};
    function img(nombre, anim, x, y, escala, flip) {
      const clave = nombre + "|" + anim;
      let o = U.img[clave];
      if (!o) { o = scn.createObject(nombre); if (!o) return null; o.setLayer("HUD"); o.setZOrder(90001); U.img[clave] = o; if (anim) o.setAnimationName(anim); }
      usados[clave] = true;
      o.hide(false);
      if (escala && Math.abs(o.getScaleX() - escala) > 0.001) o.setScale(escala);
      if (flip !== undefined && o.flipX) o.flipX(flip);
      o.setPosition(x, y);
      // con TimeScale 0 las animaciones no avanzan solas: se avanzan a mano
      try { if (anim && o.getAnimationFrameCount && o.getAnimationFrameCount() > 1) o.setAnimationFrame(Math.floor(t * 8) % o.getAnimationFrameCount()); } catch (e) { /* sin cuadros */ }
      return o;
    }

    if (U.pag === 0) {
      txt("1 / 3  ·  MUÉVETE", px, py + 70, 54, "120;220;110", "center", pw);
      txt("Camina con las teclas W A S D", px, py + 150, 32, "255;255;255", "center", pw);
      const kx = W / 2 - 32, ky = py + 215;
      tecla(kx, ky, "W"); tecla(kx - 76, ky + 76, "A"); tecla(kx, ky + 76, "S"); tecla(kx + 76, ky + 76, "D");
      const vaiven = Math.sin(t * 1.6), x = W / 2 + vaiven * 320;         // Tony camina de un lado a otro (origen en los pies)
      img("TutoTony", "tony_caminar_lado", x, py + 560, 2.4, Math.cos(t * 1.6) < 0);
      txt("Con control: stick izquierdo", px, py + 590, 26, "170;230;255", "center", pw);
    } else if (U.pag === 1) {
      txt("2 / 3  ·  ATACA", px, py + 70, 54, "120;220;110", "center", pw);
      txt("Apunta con el ratón (la mira) y ataca con CLIC IZQUIERDO", px, py + 150, 30, "255;255;255", "center", pw);
      const cx1 = px + pw * 0.27, cx2 = px + pw * 0.73, ty = py + 445;   // ty = pies de Tony
      img("TutoTony", "tony_pegar_lado", cx1, ty, 2.4, false);
      txt("CON LAS MANOS O UN ARMA", cx1 - 260, py + 465, 26, "255;215;80", "center", 520);
      txt("Acércate y dale clic: Tony golpea hacia la mira", cx1 - 260, py + 510, 22, "220;220;235", "center", 520);
      img("TutoTony", "tony_pistola_lado", cx2 - 120, ty, 2.4, false);
      const fase = (t * 1.4) % 1, bx0 = cx2 - 20, by = ty - 110, mx = cx2 + 230;   // la bala va hacia la mira, en bucle
      d.setOutlineSize(0); d.setFillOpacity(255); d.setFillColor("255;230;120");
      d.drawRectangle(bx0 + fase * (mx - bx0), by - 3, bx0 + fase * (mx - bx0) + 18, by + 3);
      d.setFillColor("255;80;80"); d.drawRectangle(mx - 2, by - 22, mx + 2, by + 22); d.drawRectangle(mx - 22, by - 2, mx + 22, by + 2);
      txt("CON PISTOLA", cx2 - 260, py + 470, 26, "255;215;80", "center", 520);
      txt("Pon la mira sobre el zombi y dale clic: la bala va a la mira", cx2 - 260, py + 510, 22, "220;220;235", "center", 520);
      txt("Con control: apunta con el stick derecho y ataca con X", px, py + 590, 26, "170;230;255", "center", pw);
    } else {
      txt("3 / 3  ·  MÁS CONTROLES", px, py + 70, 50, "120;220;110", "center", pw);
      const c1 = px + 60, c2 = px + 470, c3 = px + 880, y0 = py + 145, dy = 42;
      txt("ACCIÓN", c1, y0, 20, "150;160;190", "left", 400);
      txt("TECLADO Y RATÓN", c2, y0, 20, "150;160;190", "left", 400);
      txt("CONTROL", c3, y0, 20, "150;160;190", "left", 260);
      T.RESTO.forEach((l, k) => {
        const y = y0 + 34 + k * dy;
        txt(l[0], c1, y, 24, "255;215;80", "left", 400);
        txt(l[1], c2, y, 24, "255;255;255", "left", 400);
        txt(l[2], c3, y, 24, "170;230;255", "left", 260);
      });
      const yi = y0 + 34 + T.RESTO.length * dy + 10, hImg = py + ph - 115 - yi;
      [["CtlTeclado", px + 40], ["CtlMando", px + pw / 2 + 20]].forEach(([n, x]) => {
        const o = img(n, "", x, yi);
        if (!o) return;
        const esc = Math.min((pw / 2 - 60) / (o.getWidth() / o.getScaleX()), hImg / (o.getHeight() / o.getScaleY()));
        if (Math.abs(o.getScaleX() - esc) > 0.001) o.setScale(esc);
        o.setPosition(x + (pw / 2 - 60 - o.getWidth()) / 2, yi);
      });
    }
    txt(U.pag < 2 ? "SIGUIENTE" : "¡A JUGAR!", W / 2 - 190, py + ph - 88, 38, "10;40;10", "center", 380);
    txt("(clic, Enter, Espacio o A" + (U.pag > 0 ? " · Retroceso para regresar" : "") + ")", px, py + ph - 28, 20, "200;200;220", "center", pw);
    for (let k = i; k < U.tx.length; k++) if (U.tx[k]) U.tx[k].hide(true);
    for (const k in U.img) if (!usados[k] && U.img[k]) U.img[k].hide(true);

    // ---- avanzar / regresar / cerrar
    const cur = { clic: I.isMouseButtonPressed(0), k: [13, 32].some((c) => I.isKeyPressed(c)), a: false };
    try { const gp = navigator.getGamepads ? navigator.getGamepads() : []; for (let g = 0; g < 4; g++) if (gp && gp[g] && gp[g].buttons[0] && gp[g].buttons[0].pressed) cur.a = true; } catch (e) { /* sin mandos */ }
    const solto = (() => { try { return I.isMouseButtonReleased(0) || [13, 32].some((c) => I.wasKeyReleased(c)); } catch (e) { return false; } })();
    const sig = U.prev ? ((cur.clic && !U.prev.clic) || (cur.k && !U.prev.k) || (cur.a && !U.prev.a) || solto) : false;
    const atras = (() => { try { return I.wasKeyReleased(8) || I.wasKeyReleased(37); } catch (e) { return false; } })();
    const salir = (() => { try { return I.wasKeyReleased(27); } catch (e) { return false; } })();
    U.prev = cur;
    if (ahora() - U.tp < 0.35) return;                             // un respiro entre páginas (el mismo clic no salta dos)
    if (atras && U.pag > 0) { U.pag--; U.tp = ahora(); return; }
    if (sig && U.pag < 2) { U.pag++; U.tp = ahora(); return; }
    if ((sig && U.pag === 2) || salir) {
      U.open = false;
      for (const o of U.tx) if (o) o.hide(true);
      for (const k in U.img) if (U.img[k]) U.img[k].hide(true);
      d.clear();
      SV(scn, "ProfDlg").setNumber(2);
      if (SV(scn, "Pausa").getAsNumber() === 0) scn.getTimeManager().setTimeScale(1);
    }
  };
})(gdjs);
