/* FDI-Z · Fase 57 · Volumen de música y efectos por separado.
 * Se incrusta en TODAS las escenas con scripts/fase57_volumen.py (no editar el evento a mano: editar este archivo y volver a correr el script).
 * Define gdjs.fdizAudio.
 *
 * Volumen: variables globales VolMusica y VolEfectos (0..100, pasos de 10; 100 = como antes). Se guardan también en el
 * navegador (localStorage "fdiz_volumen") para la siguiente vez que se abra el juego.
 * Cómo se aplica (sin tocar las ~45 acciones de sonido del proyecto): se envuelve createHowlerSound del gestor de
 * sonido de GDevelop, que usan playSound, playSoundOnChannel, playMusic y playMusicOnChannel. Cada sonido nuevo sale
 * con su volumen x VolEfectos / 100 y cada música x VolMusica / 100. Al mover una barra se actualizan también los que
 * ya están sonando (música de fondo incluida) y los videos de la escena (su audio cuenta como música).
 * Pantalla: en el menú de pausa, botón AJUSTES (antes CONTROLES) -> "CONTROLES Y SONIDO": filas MÚSICA, EFECTOS y VOLVER.
 *   Teclado: W/S o flechas eligen la fila, A/D o flechas bajan/suben, Enter o Espacio en VOLVER sale, Retroceso sale.
 *   Mando: cruceta o stick izquierdo; A en VOLVER sale; B sale (evento del proyecto).
 *   Ratón: clic en − / +, clic sobre la barra para fijar el valor, clic en VOLVER. */
(function (gdjs) {
  "use strict";
  if (gdjs.fdizAudio && gdjs.fdizAudio.VER === 1) return;
  const A = (gdjs.fdizAudio = { VER: 1 });
  A.PASO = 10;
  A.CLAVE = "fdiz_volumen";
  A.vol = { m: 100, e: 100 };                 // lo que se está aplicando
  A.MUESTRA = "efectos/mundo/interruptor.ogg"; // sonido de prueba al mover EFECTOS
  const limita = (v) => Math.max(0, Math.min(100, Math.round((Number(v) || 0) / A.PASO) * A.PASO));
  A.limita = limita;

  // ------------------------------------------------------------------ gestor de sonido
  function instalar() {
    const SM = gdjs.HowlerSoundManager;
    if (!SM || !SM.prototype || SM.prototype._fdizVol) return;
    const orig = SM.prototype.createHowlerSound;
    SM.prototype.createHowlerSound = function (nombre, esMusica, vol, loop, rate) {
      const f = (esMusica ? A.vol.m : A.vol.e) / 100;
      const s = orig.call(this, nombre, esMusica, vol * f, loop, rate);
      try { s._fdizBase = vol; s._fdizMusica = !!esMusica; } catch (e) {}
      return s;
    };
    SM.prototype._fdizVol = true;
  }
  function sonando(sm) {
    const out = [];
    const add = (s) => { if (s && s._fdizBase !== undefined) out.push(s); };
    for (const k of ["_sounds", "_musics"]) { const o = sm[k]; if (o) for (const c in o) add(o[c]); }
    for (const k of ["_freeSounds", "_freeMusics"]) { const a = sm[k]; if (a) for (const s of a) add(s); }
    return out;
  }
  function actualizarSonando(game) {
    let sm = null; try { sm = game.getSoundManager(); } catch (e) {}
    if (!sm) return;
    for (const s of sonando(sm)) {
      try { if (!s.stopped || !s.stopped()) s.setVolume(s._fdizBase * (s._fdizMusica ? A.vol.m : A.vol.e) / 100); } catch (e) {}
    }
  }

  // ------------------------------------------------------------------ variables globales y guardado
  const GV = (game, n) => game.getVariables().get(n);
  function cargarGuardado(game) {
    if (A._cargado) return;
    A._cargado = true;
    try {
      const raw = typeof localStorage !== "undefined" ? localStorage.getItem(A.CLAVE) : null;
      if (raw) { const o = JSON.parse(raw); GV(game, "VolMusica").setNumber(limita(o.m)); GV(game, "VolEfectos").setNumber(limita(o.e)); }
    } catch (e) {}
  }
  function guardar() {
    try { if (typeof localStorage !== "undefined") localStorage.setItem(A.CLAVE, JSON.stringify(A.vol)); } catch (e) {}
  }

  // Cada cuadro, en todas las escenas (antes de la música de inicio de escena).
  A.aplicar = function (scn) {
    const game = scn.getGame();
    instalar();
    cargarGuardado(game);
    const m = limita(GV(game, "VolMusica").getAsNumber()), e = limita(GV(game, "VolEfectos").getAsNumber());
    if (GV(game, "VolMusica").getAsNumber() !== m) GV(game, "VolMusica").setNumber(m);       // valores siempre en 0..100
    if (GV(game, "VolEfectos").getAsNumber() !== e) GV(game, "VolEfectos").setNumber(e);
    if (m !== A.vol.m || e !== A.vol.e) { A.vol = { m, e }; actualizarSonando(game); guardar(); }
    // audio de los videos de esta escena = música
    if (scn._fdizVidM !== m || (scn._fdizVidN || 0) < 3) {
      scn._fdizVidN = (scn._fdizVidN || 0) + 1;                   // los primeros cuadros, por si se crean tarde
      scn._fdizVidM = m;
      for (const o of scn.getAdhocListOfAllInstances()) {
        if (typeof o.setVolume !== "function" || typeof o.getVolume !== "function" || typeof o.isPlayed !== "function") continue;
        if (o._fdizBase === undefined) o._fdizBase = o.getVolume();
        o.setVolume(o._fdizBase * m / 100);
      }
    }
  };

  // Para cambiar el volumen desde otro lado (y para las pruebas).
  A.cambiar = function (game, cual, delta) {
    const n = cual === "musica" ? "VolMusica" : "VolEfectos";
    GV(game, n).setNumber(limita(GV(game, n).getAsNumber() + delta));
  };

  // ------------------------------------------------------------------ pantalla CONTROLES Y SONIDO (menú de pausa)
  const FILAS = [{ k: "musica", t: "MÚSICA" }, { k: "efectos", t: "EFECTOS" }, { k: "volver" }];
  const Y = [832, 882];                        // centro de cada fila
  const BX0 = 760, BX1 = 1160;                 // barra
  const MENOS = [700, 744], MAS = [1176, 1220];
  function padEstado() {
    let pads = []; try { pads = navigator.getGamepads ? navigator.getGamepads() : []; } catch (e) {}
    const r = { arriba: false, abajo: false, izq: false, der: false, ok: false };
    for (let i = 0; i < 4; i++) {
      const g = pads && pads[i]; if (!g) continue;
      const b = (n) => !!(g.buttons[n] && g.buttons[n].pressed), ax = g.axes[0] || 0, ay = g.axes[1] || 0;
      r.arriba = r.arriba || b(12) || ay < -0.6; r.abajo = r.abajo || b(13) || ay > 0.6;
      r.izq = r.izq || b(14) || ax < -0.6; r.der = r.der || b(15) || ax > 0.6; r.ok = r.ok || b(0);
    }
    return r;
  }
  function texto(scn, st, i, s, x, y, o) {
    let t = st.txt[i];
    if (!t) { t = st.txt[i] = scn.createObject("TxtVol"); if (!t) return null; t.setLayer("HUD"); }
    t.hide(false);
    if (t._k !== s) { t.setText(s); t._k = s; }
    if (o.size && t.setCharacterSize) t.setCharacterSize(o.size);
    t.setColor(o.col || "235;235;235");
    const w = t.getWidth();
    t.setPosition(Math.round(o.al === "right" ? x - w : o.al === "left" ? x : x - w / 2), Math.round(y - t.getHeight() / 2));
    t.setZOrder(90006);
    return t;
  }
  function ocultar(scn, st) {
    for (const t of st.txt) if (t) t.hide(true);
    if (st.dib) st.dib.clear();
    const v = (scn.getObjects("TxtPausaB0") || [])[0]; if (v) v.setColor("255;255;255");
  }

  A.pausa = function (scn) {
    const st = scn._fdizVolUI || (scn._fdizVolUI = { txt: [], dib: null, sel: 0, abierto: false, pad: {} });
    const SV = scn.getVariables();
    const abierto = SV.get("Pausa").getAsNumber() === 1 && SV.get("PausaVista").getAsNumber() === 2;
    if (!abierto) { if (st.abierto) ocultar(scn, st); st.abierto = false; st.sel = 0; return; }
    const primero = !st.abierto;
    st.abierto = true;
    if (!st.dib) { st.dib = scn.createObject("VolDib"); if (st.dib) { st.dib.setLayer("HUD"); st.dib.setPosition(0, 0); st.dib.setZOrder(90005); } }
    const game = scn.getGame(), I = game.getInputManager();
    const H = scn.getLayer("HUD"), c = H.convertCoords(I.getCursorX(), I.getCursorY(), 0), mx = c[0], my = c[1];
    const p = padEstado(), flanco = (k) => p[k] && !st.pad[k];
    const tecla = (...cods) => cods.some((k) => I.wasKeyJustPressed(k));
    const clic = I.isMouseButtonReleased(0);
    const volver = () => { SV.get("PausaVista").setNumber(0); };
    let cambio = null;
    if (!primero) {
      if (tecla(38, 87) || flanco("arriba")) st.sel = (st.sel + FILAS.length - 1) % FILAS.length;
      if (tecla(40, 83) || flanco("abajo")) st.sel = (st.sel + 1) % FILAS.length;
      if (st.sel < 2 && (tecla(37, 65) || flanco("izq"))) cambio = [FILAS[st.sel].k, -A.PASO];
      if (st.sel < 2 && (tecla(39, 68) || flanco("der"))) cambio = [FILAS[st.sel].k, A.PASO];
      if (st.sel === 2 && (tecla(13, 32) || flanco("ok"))) volver();
      if (tecla(8)) volver();                                    // Retroceso
      if (clic) {
        for (let i = 0; i < 2; i++) {
          if (Math.abs(my - Y[i]) > 22) continue;
          if (mx >= MENOS[0] && mx <= MENOS[1]) { st.sel = i; cambio = [FILAS[i].k, -A.PASO]; }
          else if (mx >= MAS[0] && mx <= MAS[1]) { st.sel = i; cambio = [FILAS[i].k, A.PASO]; }
          else if (mx >= BX0 - 6 && mx <= BX1 + 6) {
            st.sel = i;
            const n = FILAS[i].k === "musica" ? "VolMusica" : "VolEfectos";
            GV(game, n).setNumber(limita((mx - BX0) / (BX1 - BX0) * 100));
            cambio = [FILAS[i].k, 0];
          }
        }
        const v = (scn.getObjects("TxtPausaB0") || [])[0];
        if (v && mx >= v.getX() - 30 && mx <= v.getX() + v.getWidth() + 30 && my >= v.getY() - 15 && my <= v.getY() + v.getHeight() + 15) volver();
      }
    }
    st.pad = p;
    if (cambio) {
      if (cambio[1]) A.cambiar(game, cambio[0], cambio[1]);
      A.aplicar(scn);
      if (cambio[0] === "efectos") {
        try { if (game.getVariables().get("SonidoActivo").getAsNumber() === 1) game.getSoundManager().playSound(A.MUESTRA, false, 60, 1); } catch (e) {}
      }
    }
    if (SV.get("PausaVista").getAsNumber() !== 2) { ocultar(scn, st); st.abierto = false; return; }

    // dibujo
    const D = st.dib; if (D) { D.clear(); D.setOutlineSize(0); }
    let n = 0;
    texto(scn, st, n++, "SONIDO", 960, 788, { size: 30, col: "255;230;120" });
    for (let i = 0; i < 2; i++) {
      const sel = st.sel === i, v = i === 0 ? A.vol.m : A.vol.e, y = Y[i];
      texto(scn, st, n++, (sel ? "▶ " : "") + FILAS[i].t, 680, y, { size: 26, al: "right", col: sel ? "255;230;80" : "220;220;230" });
      texto(scn, st, n++, "−", (MENOS[0] + MENOS[1]) / 2, y, { size: 30, col: "255;255;255" });
      texto(scn, st, n++, "+", (MAS[0] + MAS[1]) / 2, y, { size: 30, col: "255;255;255" });
      texto(scn, st, n++, v === 0 ? "SIN SONIDO" : v + " %", 1240, y, { size: 26, al: "left", col: sel ? "255;230;80" : "220;220;230" });
      if (D) {
        D.setFillOpacity(255);
        for (const b of [MENOS, MAS]) { D.setFillColor(sel ? "90;80;30" : "40;44;70"); D.drawRectangle(b[0], y - 20, b[1], y + 20); }
        D.setFillColor("12;14;24"); D.drawRectangle(BX0 - 3, y - 13, BX1 + 3, y + 13);
        const seg = (BX1 - BX0) / 10;
        for (let k = 0; k < 10; k++) {
          const on = (k + 1) * 10 <= v;
          D.setFillColor(on ? (sel ? "255;210;80" : "90;205;255") : "38;42;66");
          D.drawRectangle(BX0 + k * seg + 2, y - 10, BX0 + (k + 1) * seg - 2, y + 10);
        }
      }
    }
    texto(scn, st, n++, "↑ ↓ elegir   ← → ajustar   (cruceta o stick en el mando)", 960, 990, { size: 18, col: "170;170;190" });
    const v = (scn.getObjects("TxtPausaB0") || [])[0];
    if (v) v.setColor(st.sel === 2 ? "255;230;80" : "255;255;255");
    for (let i = n; i < st.txt.length; i++) if (st.txt[i]) st.txt[i].hide(true);
  };
})(gdjs);
