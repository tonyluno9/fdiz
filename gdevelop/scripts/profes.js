/* FDI-Z · Fase 40 · Profesores reclutables (Joel, Justino y Canepa).
 * Se incrusta en la escena Juego con scripts/fase40_profesores.py (no editar el evento a mano: editar este archivo y volver a correr el script).
 * Define gdjs.fdizProfes. El estado de cada partida vive en la escena (runtimeScene._fdizPf y variables de escena),
 * así que reiniciar la escena devuelve todo a su condición inicial.
 *
 * Estados (variable de escena Prof<Nombre>, se sincroniza en línea):
 *   espera        en su lugar, inmune, no lo eligen los zombis (es el objeto Profe, no un superviviente)
 *   conversacion  alguien tiene abierto el diálogo con él (sigue inmune)
 *   aliado        reclutado: es un "Sup" bot más (Jugador 5/6/7) con vida, combate, mordidas y caídas
 *   mordido       aliado mordido (35 s para curarlo, como los alumnos)
 *   caido         aliado en el piso (25 s para revivirlo, como los alumnos)
 *   rechazado     lo dejaron: sin inmunidad, quieto, cuenta individual de 30 s de juego y se convierte
 *   convertido    ya es un zombi hostil (ZJoel / ZJustino / ZCanepa)
 *   fuera         aliado que nadie revivió a tiempo: queda fuera el resto de la partida
 * Prof<Nombre>Seg: segundos que faltan (rechazado: conversión; mordido: mordida).
 *
 * Autoridad: sin red (NetRol 0) o host (NetRol 1) decide todo. Los clientes (NetRol 2) solo dibujan la interfaz y mandan
 * sus decisiones al host con un mensaje {t:"prof"} (net_core.js -> N.onProf). El host acepta una sola decisión por profe. */
(function (gdjs) {
  "use strict";
  const VER = 3;
  if (gdjs.fdizProfes && gdjs.fdizProfes.ver === VER) return;

  // ------------------------------------------------------------------ configuración (ajustar aquí)
  const PROFES = {
    joel: {
      nombre: "Joel", jugador: 5, zombi: "ZJoel", zona: "CÓMPUTO",
      vida: 100, velocidad: 204, fuerza: 1.0,
      pide: "¡Por aquí! ¡Estoy en cómputo!",
      habla: "Si me ayudan a salir, puedo acompañarlos. ¿Me llevan con ustedes?",
      acepta: "¡Gracias! Voy con ustedes.",
      rechaza: "¿Me van a dejar? No sé cuánto pueda aguantar…",
    },
    justino: {
      nombre: "Justino", jugador: 6, zombi: "ZJustino", zona: "LA NEVERÍA",
      vida: 110, velocidad: 198, fuerza: 1.1,
      pide: "¡Aquí, detrás de la barra! ¡Necesito ayuda!",
      habla: "Estoy atrapado en la nevería. Sáquenme de aquí y los ayudo.",
      acepta: "¡Vamos! Me quedo con el equipo.",
      rechaza: "Está bien… intentaré aguantar aquí.",
    },
    canepa: {
      nombre: "Canepa", jugador: 7, zombi: "ZCanepa", zona: "EL ESTACIONAMIENTO",
      vida: 120, velocidad: 192, fuerza: 1.15,
      pide: "¡Acérquense al camión! ¡Necesito apoyo!",
      habla: "Podemos salir de aquí juntos. ¿Cuento con ustedes?",
      acepta: "¡Vamos, equipo! Los acompaño.",
      rechaza: "Entonces me quedo aquí… tengan cuidado.",
    },
  };
  const ORDEN = ["joel", "justino", "canepa"];
  const CFG = {
    cuentaRechazo: 30,      // s de juego desde que se confirma el rechazo hasta la conversión
    mordidaSeg: 35,         // igual que los alumnos (grupo "Compañeros mordidos")
    probMordida: 0.12,      // igual que los alumnos
    curaSeg: 3,             // mantener Usar 3 s junto al mordido
    curaRadio: 95,
    revivirRadio: 80,
    hablarRadio: 115,       // distancia para la indicación "Usar: hablar"
    pedirRadio: 480,        // un humano a esta distancia escucha la petición de ayuda
    gritoCada: 10,          // s entre peticiones del mismo profe
    gritoDura: 2.8,
    gritosPorVisita: 4,     // tope de peticiones mientras el jugador se queda cerca
    ayudaBotRadio: 600,     // los bots van a auxiliar a un profe caído o mordido a esta distancia
    recompensaCura: 30,     // al reclutar (una sola vez por profe) el equipo principal se cura 30
    reparar: { x: 544, y: 3328 },   // lugar de Canepa junto al camión (Final ¡Aguanten!)
    golpeRechazado: 1.0,    // cada cuánto un zombi pegado a un profe rechazado le pega (cosmético: no cambia la cuenta)
  };
  const ZOMBIS = ["ZNormal", "ZCorredor", "ZGriton", "ZGordo", "ZConserje", "ZCurado", "ZJoel", "ZJustino", "ZCanepa"];

  // ------------------------------------------------------------------ utilidades
  const VS = (o, n) => o.getVariables().get(n);
  const num = (o, n) => VS(o, n).getAsNumber();
  const str = (o, n) => VS(o, n).getAsString();
  const SV = (scn) => scn.getVariables();
  const GV = (scn) => scn.getGame().getVariables();
  const rol = (scn) => GV(scn).get("NetRol").getAsNumber();
  const est = (scn, k) => SV(scn).get("Prof" + PROFES[k].nombre).getAsString();
  const setEst = (scn, k, v) => SV(scn).get("Prof" + PROFES[k].nombre).setString(v);
  const seg = (scn, k) => SV(scn).get("Prof" + PROFES[k].nombre + "Seg").getAsNumber();
  const setSeg = (scn, k, v) => SV(scn).get("Prof" + PROFES[k].nombre + "Seg").setNumber(v);
  const objs = (scn, n) => scn.getObjects(n) || [];
  const dist = (a, b) => Math.hypot(a.getX() - b.getX(), a.getY() - b.getY());
  const ahora = () => (typeof performance !== "undefined" ? performance.now() : Date.now()) / 1000;
  const ESPERA = (s) => s === "espera" || s === "conversacion";
  const ALIADO = (s) => s === "aliado" || s === "mordido" || s === "caido";

  function npcDe(scn, k) { for (const o of objs(scn, "Profe")) if (str(o, "Nombre") === k) return o; return null; }
  function supDe(scn, k) { const j = PROFES[k].jugador; for (const o of objs(scn, "Sup")) if (num(o, "Jugador") === j) return o; return null; }
  function zombiDe(scn, k) { const a = objs(scn, PROFES[k].zombi); return a.length ? a[0] : null; }
  function S(scn) {
    return scn._fdizPf || (scn._fdizPf = {
      prev: {}, ui: { n: 0, a: [], pn: 0, pa: [] }, dlg: null, cierre: 0, cd: 0, kb: {}, pad: [{}, {}, {}, {}],
      grito: {}, gritoFin: -99, burbuja: {}, aviso: null, conv: {}, finPrev: 0, golpe: {}, tinte: {}, cura: {}, keep: 0,
    });
  }
  function banner(scn, txt, s) {
    const V = SV(scn); V.get("Banner").setString(txt); V.get("BannerSeg").setNumber(s || 2.5);
    try { gdjs.evtTools.runtimeScene.resetTimer(scn, "banner"); } catch (e) {}
  }
  function sonido(scn, archivo, vol) {
    try { if (GV(scn).get("SonidoActivo").getAsNumber() === 1) gdjs.evtTools.sound.playSound(scn, archivo, false, vol || 70, 1); } catch (e) {}
  }
  // ¿El punto está tapado por una sala oscura? (no revelar su interior)
  function tapado(scn, x, y) {
    let L = null; try { L = scn.getLayer("NieblaSalas"); } catch (e) {}
    if (L && !L.isVisible()) return false;
    for (const n of objs(scn, "Niebla")) {
      if (n.isHidden() || n.getOpacity() < 60) continue;
      if (x >= n.getX() && x < n.getX() + n.getWidth() && y >= n.getY() && y < n.getY() + n.getHeight()) return true;
    }
    return false;
  }
  function libreVista(scn, a, b) {
    const N = gdjs.fdizNav; if (!N || !N.grid || N.scene !== scn) return true;
    try { return N.los(a.getX(), a.getY() - 8, b.getX(), b.getY() - 8); } catch (e) { return true; }
  }
  // humanos de ESTA máquina (teclado 0, mandos 1-4), alumnos principales de pie
  function humanosLocales(scn) {
    const r = [];
    for (const s of objs(scn, "Sup")) {
      if (num(s, "Jugador") > 4 || str(s, "Estado") !== "normal" || s.isHidden()) continue;
      let c = num(s, "Control"); if (c === -2 && s.getVariables().has("CtlReal")) c = num(s, "CtlReal");
      if (c >= 0 && c <= 4) r.push({ s, ctl: c });
    }
    return r;
  }

  // ------------------------------------------------------------------ entrada (teclado y mandos con flancos)
  const TECLAS = { arriba: [87, 38], abajo: [83, 40], ok: [70, 13, 32], usar: [70], cerrar: [8, 27] };
  function leerEntrada(scn, st) {
    const I = scn.getGame().getInputManager();
    const kb = {}; for (const k in TECLAS) kb[k] = TECLAS[k].some((c) => I.isKeyPressed(c));
    kb.clic = I.isMouseButtonPressed(0);
    const nuevo = (prev, cur) => { const e = {}; for (const k in cur) e[k] = cur[k] && !prev[k]; return e; };
    st.kbE = nuevo(st.kb, kb); st.kbH = kb; st.kb = kb;
    let pads = []; try { pads = navigator.getGamepads ? navigator.getGamepads() : []; } catch (e) {}
    st.padE = []; st.padH = [];
    for (let i = 0; i < 4; i++) {
      const g = pads && pads[i]; const b = (n) => !!(g && g.buttons[n] && g.buttons[n].pressed);
      const ay = g ? g.axes[1] || 0 : 0;
      const p = { arriba: b(12) || ay < -0.6, abajo: b(13) || ay > 0.6, ok: b(0), usar: b(0), cerrar: b(1) };
      st.padE[i] = nuevo(st.pad[i], p); st.padH[i] = p; st.pad[i] = p;
    }
    const H = scn.getLayer("HUD"); const c = H.convertCoords(I.getCursorX(), I.getCursorY(), 0);
    st.mx = c[0]; st.my = c[1];
  }
  const flanco = (st, ctl) => (ctl === 0 ? st.kbE : st.padE[ctl - 1] || {});
  const sostenido = (st, ctl) => (ctl === 0 ? st.kbH : st.padH[ctl - 1] || {});
  const tecla = (ctl, k) => (ctl === 0 ? { usar: "F", ok: "F", arriba: "W", abajo: "S", cerrar: "Retroceso" }[k] : { usar: "A", ok: "A", arriba: "↑", abajo: "↓", cerrar: "B" }[k]);
  const btn = (ctl, k) => (ctl === 0 ? "[" + tecla(ctl, k) + "]" : "(" + tecla(ctl, k) + ")");

  // ------------------------------------------------------------------ interfaz (textos y paneles en la capa HUD)
  function aPantalla(scn, x, y) {
    const c = scn.getLayer("Juego").convertInverseCoords(x, y, 0);
    return scn.getLayer("HUD").convertCoords(c[0], c[1], 0);
  }
  function txt(scn, st, s, x, y, o) {
    o = o || {}; const U = st.ui; let t = U.a[U.n++];
    if (!t) { t = scn.createObject("TxtProfe"); t.setLayer("HUD"); U.a.push(t); t._k = null; }
    t.hide(false);
    const key = s + "|" + (o.size || 22) + "|" + (o.col || "") + "|" + (o.wrap || 0);
    if (t._k !== key) {
      t._k = key; t.setCharacterSize(o.size || 22); t.setColor(o.col || "255;255;255");
      t.setWrapping(!!o.wrap); if (o.wrap) t.setWrappingWidth(o.wrap);
      if (t.setTextAlignment) t.setTextAlignment(o.al || "center");
      t.setText(s);
    }
    const w = o.wrap || t.getWidth();
    t.setPosition(o.al === "left" ? x : x - w / 2, y); t.setZOrder(o.z || 402); t.setOpacity(o.op === undefined ? 255 : o.op);
    return t;
  }
  function panel(scn, st, x0, y0, x1, y1, z) {
    const U = st.ui; let p = U.pa[U.pn++];
    if (!p) { p = scn.createObject("ProfPanel"); p.setLayer("HUD"); U.pa.push(p); }
    p.hide(false); p.setPosition(x0, y0); p.setWidth(x1 - x0); p.setHeight(y1 - y0); p.setZOrder(z || 400);
    return p;
  }
  function burbuja(scn, st, s, x, y, col) {
    const p = aPantalla(scn, x, y);
    if (p[0] < -200 || p[0] > 2120 || p[1] < -100 || p[1] > 1180) return;
    const t = txt(scn, st, s, p[0], p[1], { size: 20, col: col || "255;255;255", wrap: 0, z: 412 });
    panel(scn, st, t.getX() - 14, t.getY() - 6, t.getX() + t.getWidth() + 14, t.getY() + t.getHeight() + 6, 411);
  }
  function dibujo(scn, st) {
    if (!st.dib) { st.dib = scn.createObject("ProfDib"); if (st.dib) { st.dib.setLayer("HUD"); st.dib.setPosition(0, 0); st.dib.setZOrder(403); } }
    return st.dib;
  }

  // ------------------------------------------------------------------ decisiones (solo host u offline)
  function reclutar(scn, k) {
    const P = PROFES[k], npc = npcDe(scn, k);
    if (!npc || !ESPERA(est(scn, k)) || supDe(scn, k)) return false;
    const s = scn.createObject("Sup"); if (!s) return false;
    s.setLayer("Juego"); s.setPosition(npc.getX(), npc.getY()); s.setZOrder(Math.round(npc.getY()));
    const set = (n, v) => { const x = VS(s, n); if (typeof v === "string") x.setString(v); else x.setNumber(v); };
    set("Personaje", k); set("Jugador", P.jugador); set("Control", -1); set("Init", 0); set("Init12", 0); set("CdOk", 0);
    set("Vida", P.vida); set("VidaMax", P.vida); set("Velocidad", P.velocidad); set("Fuerza", P.fuerza);
    set("Estado", "normal"); set("Arma", "puños"); set("Mordido", 0); set("Cura", 0); set("Revivir", 0);
    set("BotX", npc.getX()); set("BotY", npc.getY()); set("Huye", 0);
    s.setAnimationName(k + "_quieto");
    npc.deleteFromScene(scn);
    setEst(scn, k, "aliado"); setSeg(scn, k, 0);
    // el contador cuenta cada reclutamiento una sola vez (solo se llega aquí desde "espera")
    SV(scn).get("Rescatados").add(1);
    // recompensa de la mecánica anterior de rescate, una sola vez por profe: el equipo principal se cura 30
    for (const o of objs(scn, "Sup")) if (num(o, "Jugador") <= 4 && str(o, "Estado") === "normal")
      VS(o, "Vida").setNumber(Math.min(num(o, "VidaMax"), num(o, "Vida") + CFG.recompensaCura));
    banner(scn, "¡" + P.nombre.toUpperCase() + " SE UNE AL EQUIPO! El equipo se cura", 2.5);
    sonido(scn, "efectos/eventos/rescate_logrado.ogg", 70);
    return true;
  }
  function rechazar(scn, k) {
    const npc = npcDe(scn, k);
    if (!npc || !ESPERA(est(scn, k))) return false;
    setEst(scn, k, "rechazado"); setSeg(scn, k, CFG.cuentaRechazo);
    VS(npc, "Estado").setString("rechazado");
    banner(scn, PROFES[k].nombre.toUpperCase() + " SE QUEDÓ ATRÁS", 2);
    return true;
  }
  function convertir(scn, k, x, y) {
    if (est(scn, k) === "convertido" || zombiDe(scn, k)) return;
    const z = scn.createObject(PROFES[k].zombi);
    if (z) {
      z.setLayer("Juego"); z.setPosition(x, y); z.setZOrder(Math.round(y));
      VS(z, "Estado").setString("persigue"); // Vida = la del objeto (vida base de ZConserje); el evento DifOk aplica la dificultad una vez
    }
    setEst(scn, k, "convertido"); setSeg(scn, k, 0);
    banner(scn, "¡" + PROFES[k].nombre.toUpperCase() + " SE CONVIRTIÓ EN ZOMBI!", 3);
    sonido(scn, "efectos/combate/convertido.ogg", 70);
  }
  // aplica una decisión (local o recibida de un cliente). Devuelve true si se aceptó.
  function aplicar(scn, k, d, quien) {
    if (!PROFES[k]) return false;
    const st = S(scn), e = est(scn, k);
    if (d === "abre") { if (e === "espera") { setEst(scn, k, "conversacion"); st.conv[k] = { quien, t: ahora() }; return true; } if (e === "conversacion" && st.conv[k] && st.conv[k].quien === quien) { st.conv[k].t = ahora(); return true; } return false; }
    if (d === "cierra") { if (e === "conversacion" && (!st.conv[k] || st.conv[k].quien === quien)) { setEst(scn, k, "espera"); delete st.conv[k]; return true; } return false; }
    if (!ESPERA(e)) return false;                                   // ya decidido: se ignora (una sola decisión válida)
    if (e === "conversacion" && st.conv[k] && st.conv[k].quien !== quien) return false; // otra persona tiene el diálogo
    delete st.conv[k];
    if (d === "acepta") return reclutar(scn, k);
    if (d === "rechaza") return rechazar(scn, k);
    return false;
  }
  function decidir(scn, k, d) {
    const r = rol(scn);
    if (r === 2) { const N = gdjs.fdizNet; if (N && N.toHost) N.toHost({ t: "prof", k, d }); return; }
    aplicar(scn, k, d, "local");
  }

  // ------------------------------------------------------------------ diálogo
  function abrirDialogo(scn, st, k, h) {
    st.dlg = { k, jug: num(h.s, "Jugador"), ctl: h.ctl, paso: 0, sel: 0, armado: false, t0: ahora(), ping: ahora(), aviso: "" };
    SV(scn).get("ProfDlg").setNumber(1);
    if (rol(scn) === 0) scn.getTimeManager().setTimeScale(0);      // sin red: la partida se detiene mientras hablan (como la pausa)
    decidir(scn, k, "abre");
  }
  function cerrarDialogo(scn, st, avisar) {
    const D = st.dlg; if (!D) return;
    if (avisar) decidir(scn, D.k, "cierra");
    st.dlg = null; st.cierre = 2; st.cd = ahora() + 0.4;
    SV(scn).get("ProfDlg").setNumber(2);                             // 2: este cuadro todavía bloquea la pausa (Esc/Start)
    if (rol(scn) === 0 && SV(scn).get("Pausa").getAsNumber() === 0) scn.getTimeManager().setTimeScale(1);
  }
  function opciones(D) {
    return D.paso === 0 ? ["Ayudar y agregar al equipo", "Dejarlo aquí"] : ["Sí, dejarlo aquí", "Volver"];
  }
  function manejarDialogo(scn, st) {
    const D = st.dlg, P = PROFES[D.k], e = est(scn, D.k);
    if (!ESPERA(e)) { cerrarDialogo(scn, st, false); return; }       // otro jugador decidió primero
    const yo = objs(scn, "Sup").find((s) => num(s, "Jugador") === D.jug);
    if (!yo || str(yo, "Estado") !== "normal") { cerrarDialogo(scn, st, true); return; }
    if (rol(scn) === 2 && ahora() - D.ping > 8) { D.ping = ahora(); decidir(scn, D.k, "abre"); }
    const E = flanco(st, D.ctl), Hs = sostenido(st, D.ctl);
    if (!D.armado) { if (!Hs.ok && !Hs.usar && ahora() - D.t0 > 0.12) D.armado = true; }
    const ops = opciones(D);
    // ratón (solo jugador de teclado)
    let clic = -1;
    if (D.ctl === 0 && D.rect) D.rect.forEach((r, i) => { if (st.mx >= r[0] && st.mx <= r[2] && st.my >= r[1] && st.my <= r[3]) { D.sel = i; if (st.kbE.clic) clic = i; } });
    if (E.arriba) D.sel = (D.sel + ops.length - 1) % ops.length;
    if (E.abajo) D.sel = (D.sel + 1) % ops.length;
    if (E.cerrar) { if (D.paso === 1) { D.paso = 0; D.sel = 1; D.armado = false; D.t0 = ahora(); } else cerrarDialogo(scn, st, true); return; }
    const ok = D.armado && (E.ok || clic >= 0);
    if (ok) {
      if (D.paso === 0 && D.sel === 0) { decidir(scn, D.k, "acepta"); cerrarDialogo(scn, st, false); return; }
      if (D.paso === 0 && D.sel === 1) { D.paso = 1; D.sel = 1; D.armado = false; D.t0 = ahora(); return; }
      if (D.paso === 1 && D.sel === 0) { decidir(scn, D.k, "rechaza"); cerrarDialogo(scn, st, false); return; }
      if (D.paso === 1 && D.sel === 1) { D.paso = 0; D.sel = 0; D.armado = false; D.t0 = ahora(); return; }
    }
    // dibujo
    const X0 = 430, X1 = 1490, Y0 = 640, Y1 = 1010;
    panel(scn, st, X0, Y0, X1, Y1, 420);
    txt(scn, st, P.nombre.toUpperCase(), 960, Y0 + 22, { size: 30, col: "255;220;90", z: 421 });
    const cuerpo = D.paso === 0 ? "«" + P.habla + "»"
      : "Si lo dejas aquí, en " + CFG.cuentaRechazo + " segundos se convertirá en zombi y atacará al equipo. No podrás cambiar de opinión.";
    txt(scn, st, cuerpo, 960, Y0 + 70, { size: 24, col: D.paso === 0 ? "235;235;235" : "255;150;130", wrap: 960, z: 421 });
    D.rect = [];
    ops.forEach((s, i) => {
      const y = Y0 + 190 + i * 52, sel = i === D.sel;
      const t = txt(scn, st, (sel ? "▶ " : "   ") + s, 960, y, { size: 28, col: sel ? "255;230;80" : "200;200;200", z: 421 });
      D.rect.push([t.getX() - 20, y - 6, t.getX() + t.getWidth() + 20, y + t.getHeight() + 6]);
    });
    txt(scn, st, btn(D.ctl, "arriba") + "/" + btn(D.ctl, "abajo") + " elegir   " + btn(D.ctl, "ok") + " aceptar   " + btn(D.ctl, "cerrar") + " cerrar",
      960, Y1 - 38, { size: 18, col: "170;170;190", z: 421 });
  }
  function buscarInteraccion(scn, st, ui) {
    const enJuego = SV(scn).get("Estado").getAsString() === "juego" && SV(scn).get("Pausa").getAsNumber() === 0;
    if (!enJuego) return;
    const hs = humanosLocales(scn);
    for (const k of ORDEN) {
      const npc = npcDe(scn, k); if (!npc) continue;
      const e = est(scn, k); if (!ESPERA(e)) continue;
      // fase 61: en Historia, Canepa no se recluta hasta la charla del camión (misión 5); así nadie lo rechaza antes
      if (gdjs.fdizCanepa && gdjs.fdizCanepa.reservado(scn, k)) continue;
      let mejor = null, md = 1e9;
      for (const h of hs) {
        // fase 56: si para ese jugador F es para otra cosa más cercana (puerta, salvar...), el profe no se ofrece
        if (gdjs.fdizUsar && !gdjs.fdizUsar.permite(h.s, "profe")) continue;
        const d = dist(h.s, npc); if (d < CFG.hablarRadio && d < md && libreVista(scn, h.s, npc)) { md = d; mejor = h; }
      }
      if (!mejor) continue;
      if (e === "conversacion" && !st.dlg) { if (ui) burbuja(scn, st, "Alguien habla con " + PROFES[k].nombre + "…", npc.getX(), npc.getY() - 150, "200;200;220"); continue; }
      if (ui) burbuja(scn, st, btn(mejor.ctl, "usar") + " Hablar con " + PROFES[k].nombre, npc.getX(), npc.getY() - 150, "255;230;120");
      // abre con un flanco de Usar de ese jugador (no basta con mantenerlo)
      if (!st.dlg && ahora() > st.cd && flanco(st, mejor.ctl).usar) { abrirDialogo(scn, st, k, mejor); return; }
    }
  }

  // ------------------------------------------------------------------ peticiones de ayuda (cada máquina, solo visual)
  function gritos(scn, st) {
    const t = ahora(), hs = humanosLocales(scn);
    if (SV(scn).get("Estado").getAsString() !== "juego") return;
    for (const k of ORDEN) {
      const npc = npcDe(scn, k), G = st.grito[k] || (st.grito[k] = { sig: 0, n: 0 });
      if (!npc || est(scn, k) !== "espera") continue;
      let md = 1e9; for (const h of hs) md = Math.min(md, dist(h.s, npc));
      if (md > CFG.pedirRadio * 1.3) { G.n = 0; continue; }           // se fue: la próxima visita vuelve a oír
      if (md > CFG.pedirRadio || md < CFG.hablarRadio) continue;
      if (t < G.sig || G.n >= CFG.gritosPorVisita || t < st.gritoFin + 1.2 || (st.dlg && st.dlg.k === k)) continue;
      G.sig = t + CFG.gritoCada; G.n++; st.gritoFin = t + CFG.gritoDura;
      st.aviso = { k, hasta: t + CFG.gritoDura };
    }
    if (st.aviso && t < st.aviso.hasta) {
      const k = st.aviso.k, npc = npcDe(scn, k), P = PROFES[k];
      if (!npc || !ESPERA(est(scn, k))) { st.aviso = null; return; }
      if (tapado(scn, npc.getX(), npc.getY() - 40)) {
        // sala oscura: se avisa de dónde viene la voz, sin dibujar nada encima del profe
        txt(scn, st, "Alguien pide ayuda desde " + P.zona + ": «" + P.pide + "»", 960, 232, { size: 22, col: "255;235;170", z: 412 });
        const t2 = st.ui.a[st.ui.n - 1]; panel(scn, st, t2.getX() - 18, 224, t2.getX() + t2.getWidth() + 18, 268, 411);
      } else burbuja(scn, st, "«" + P.pide + "»", npc.getX(), npc.getY() - 150, "255;255;255");
    }
  }

  // ------------------------------------------------------------------ host: estados, cuentas, conversión, cura
  function logicaHost(scn, st) {
    const dt = Math.min(0.1, scn.getElapsedTime() / 1000);
    const V = SV(scn), corre = V.get("Pausa").getAsNumber() === 0 && V.get("Estado").getAsString() === "juego";
    const sups = objs(scn, "Sup");
    for (const k of ORDEN) {
      const P = PROFES[k]; let e = est(scn, k);
      if (e === "conversacion" && st.conv[k] && ahora() - st.conv[k].t > 30 && !(st.dlg && st.dlg.k === k)) { setEst(scn, k, "espera"); delete st.conv[k]; e = "espera"; }
      if (e === "conversacion" && !st.conv[k] && !(st.dlg && st.dlg.k === k)) { setEst(scn, k, "espera"); e = "espera"; }
      const npc = npcDe(scn, k);
      if (npc) { npc.setZOrder(Math.round(npc.getY())); if (npc.getAnimationName() !== k + "_quieto") npc.setAnimationName(k + "_quieto"); }
      if (e === "rechazado") {
        if (!npc) { setEst(scn, k, "convertido"); continue; }
        if (corre) setSeg(scn, k, Math.max(0, seg(scn, k) - dt)); // pausa = TimeScale 0 y Pausa 1: no avanza
        // sin inmunidad: un zombi pegado le pega (no reinicia, no acumula ni adelanta la cuenta)
        const G = st.golpe[k] || (st.golpe[k] = { t: 0 }); G.t += dt;
        if (corre && G.t >= CFG.golpeRechazado) {
          for (const n of ZOMBIS) for (const z of objs(scn, n)) {
            if (G.t < CFG.golpeRechazado || str(z, "Estado") === "muerto" || dist(z, npc) > 70) continue;
            G.t = 0; VS(npc, "Vida").setNumber(Math.max(1, num(npc, "Vida") - num(z, "Danio") * GV(scn).get("DifDanio").getAsNumber()));
            st.tinte[k] = 0.15;
          }
        }
        if (seg(scn, k) <= 0) { const x = npc.getX(), y = npc.getY(); npc.deleteFromScene(scn); convertir(scn, k, x, y); }
        continue;
      }
      if (!ALIADO(e)) continue;
      const s = supDe(scn, k);
      if (!s) { setEst(scn, k, "fuera"); continue; }
      const es = str(s, "Estado");
      if (es === "fuera") {                                       // caído 25 s sin que nadie lo reviviera
        s.deleteFromScene(scn); setEst(scn, k, "fuera"); setSeg(scn, k, 0);
        banner(scn, P.nombre.toUpperCase() + " QUEDÓ FUERA DE COMBATE", 2.5);
        continue;
      }
      if (num(s, "Mordido") === 1) {
        const tm = s.getTimerElapsedTimeInSeconds ? s.getTimerElapsedTimeInSeconds("mordida") : 0;
        if (tm >= CFG.mordidaSeg) { const x = s.getX(), y = s.getY(); s.deleteFromScene(scn); convertir(scn, k, x, y); continue; }
        setSeg(scn, k, Math.max(0, Math.ceil(CFG.mordidaSeg - tm)));
        // cura: cualquier superviviente de pie (alumno, bot o profe) que mantenga Usar junto a él 3 s
        let quien = null;
        const USA = gdjs.fdizUsar ? "UsaCurar" : "Usando";   // fase 56: solo quien eligió curar (bots: igual que Usando)
        for (const o of sups) if (o !== s && str(o, "Estado") === "normal" && num(o, USA) === 1 && dist(o, s) < CFG.curaRadio) { quien = o; break; }
        if (quien && corre) {
          VS(s, "Cura").add(dt); st.cura[k] = num(s, "Cura");
          if (num(s, "Cura") >= CFG.curaSeg) {
            VS(s, "Mordido").setNumber(0); VS(s, "Cura").setNumber(0); s.setColor("255;255;255"); st.cura[k] = 0;
            if (num(quien, "Jugador") <= 4) {                       // mismo costo que curar a un alumno
              if (num(quien, "ComidaCura") > 0) VS(quien, "ComidaCura").setNumber(0);
              else VS(quien, "Vida").setNumber(Math.max(1, num(quien, "Vida") - 20));
            }
            banner(scn, "¡" + P.nombre.toUpperCase() + " SALVADO!", 2);
          }
        } else if (!quien) { VS(s, "Cura").setNumber(0); st.cura[k] = 0; }
      } else { setSeg(scn, k, 0); st.cura[k] = 0; }
      setEst(scn, k, es === "caido" ? "caido" : (num(s, "Mordido") === 1 ? "mordido" : "aliado"));
      // Canepa repara el camión durante ¡Aguanten! (solo si es aliado, está de pie y llegó al camión)
      if (k === "canepa" && V.get("FinalActivo").getAsNumber() === 1 && es === "normal" && num(s, "Atacando") === 0) {
        const d = Math.hypot(s.getX() - CFG.reparar.x, s.getY() - CFG.reparar.y);
        const mov = s.getBehavior && s.getBehavior("TopDownMovement");
        // Atacando = 1 hace que "Movimiento y animación" no le ponga "quieto" el siguiente cuadro (la animación no se reinicia)
        if (d < 60 && !(mov && mov.isMoving && mov.isMoving())) { s.setAnimationName("canepa_pegar_lado"); s.flipX(true); VS(s, "Atacando").setNumber(1); }
      }
    }
    // inicio del final: el texto dice si Canepa repara o si el equipo lo hace solo
    const fin = V.get("FinalActivo").getAsNumber();
    if (fin === 1 && st.finPrev === 0) {
      const c = supDe(scn, "canepa");
      banner(scn, c && str(c, "Estado") === "normal" ? "¡AGUANTEN! Canepa repara el camión" : "¡AGUANTEN! Reparen el camión y resistan", 3);
    }
    st.finPrev = fin;
  }

  // ------------------------------------------------------------------ dibujo: etiquetas, burbujas de decisión y panel de aliados
  function dibujar(scn, st) {
    const V = SV(scn), t = ahora(), intro = V.get("Estado").getAsString() === "intro";
    const D = dibujo(scn, st); if (D) { D.clear(); D.setOutlineSize(0); }
    if (intro || V.get("Pausa").getAsNumber() === 1) return;
    // transiciones -> frase del profe
    for (const k of ORDEN) {
      const e = est(scn, k), p = st.prev[k];
      if (p !== undefined && p !== e) {
        if (ESPERA(p) && e === "aliado") st.burbuja[k] = { s: "«" + PROFES[k].acepta + "»", hasta: t + 3 };
        if (ESPERA(p) && e === "rechazado") st.burbuja[k] = { s: "«" + PROFES[k].rechaza + "»", hasta: t + 3.5 };
      }
      st.prev[k] = e;
    }
    for (const k of ORDEN) {
      const P = PROFES[k], e = est(scn, k), B = st.burbuja[k];
      const npc = npcDe(scn, k), s = supDe(scn, k), z = zombiDe(scn, k);
      const quien = s || npc;
      if (B && t < B.hasta && quien && !tapado(scn, quien.getX(), quien.getY() - 40)) burbuja(scn, st, B.s, quien.getX(), quien.getY() - 175, "255;255;255");
      if (e === "rechazado" && npc) {
        // tinte: de blanco a verde conforme se acerca la conversión (y rojo al recibir un golpe)
        const f = 1 - Math.max(0, Math.min(1, seg(scn, k) / CFG.cuentaRechazo));
        if (st.tinte[k] > 0) { st.tinte[k] -= scn.getElapsedTime() / 1000; npc.setColor("255;110;110"); }
        else npc.setColor(Math.round(255 - 110 * f) + ";255;" + Math.round(255 - 120 * f));
        if (!tapado(scn, npc.getX(), npc.getY() - 40)) {
          const p = aPantalla(scn, npc.getX(), npc.getY() - 128);
          txt(scn, st, P.nombre + " · " + Math.ceil(seg(scn, k)) + " s", p[0], p[1], { size: 20, col: "255;120;100", z: 405 });
        }
      }
      if (s && !s.isHidden() && !tapado(scn, s.getX(), s.getY() - 40)) {
        const p = aPantalla(scn, s.getX(), s.getY() - 132);
        let l = P.nombre, col = "235;235;255";
        if (e === "mordido") { l += " · MORDIDO " + Math.ceil(seg(scn, k)) + " s"; col = "140;255;120"; }
        if (e === "caido") { l += " · ¡AYÚDALO!"; col = "255;170;120"; }
        txt(scn, st, l, p[0], p[1], { size: 17, col, z: 405 });
        if (st.cura[k] > 0) txt(scn, st, "Curando a " + P.nombre + "… " + Math.round(100 * st.cura[k] / CFG.curaSeg) + "%", p[0], p[1] - 26, { size: 18, col: "200;255;200", z: 405 });
      }
      if (z && str(z, "Estado") !== "muerto" && !tapado(scn, z.getX(), z.getY() - 40)) {
        const p = aPantalla(scn, z.getX(), z.getY() - 130);
        txt(scn, st, P.nombre.toUpperCase() + " (ZOMBI)", p[0], p[1], { size: 17, col: "150;255;110", z: 405 });
      }
    }
    // panel compacto de profes (izquierda, entre los paneles de P1 y P3; no ocupa los 4 paneles principales)
    let fila = 0;
    for (const k of ORDEN) {
      const P = PROFES[k], e = est(scn, k); if (ESPERA(e)) continue;
      const y = 262 + fila * 62; fila++;
      panel(scn, st, 20, y, 300, y + 54, 400);
      const s = supDe(scn, k);
      let estado = { aliado: "ALIADO", mordido: "MORDIDO " + Math.ceil(seg(scn, k)) + " s", caido: "CAÍDO", rechazado: "ZOMBI EN " + Math.ceil(seg(scn, k)) + " s",
        convertido: "CONVERTIDO", fuera: "FUERA" }[e] || e.toUpperCase();
      const col = { aliado: "140;220;255", mordido: "140;255;120", caido: "255;170;120", rechazado: "255;120;100", convertido: "150;255;110", fuera: "170;170;170" }[e] || "255;255;255";
      txt(scn, st, P.nombre.toUpperCase(), 34, y + 6, { size: 18, col: "255;230;150", al: "left", z: 402 });
      txt(scn, st, estado, 132, y + 6, { size: 18, col, al: "left", z: 402 });
      if (D) {
        let f = 0, c = "90;90;90";
        if (s && ALIADO(e)) { f = Math.max(0, Math.min(1, num(s, "Vida") / Math.max(1, num(s, "VidaMax")))); c = e === "caido" ? "200;110;60" : "80;210;90"; }
        if (e === "rechazado") { f = seg(scn, k) / CFG.cuentaRechazo; c = "220;80;60"; }
        D.setFillColor("25;25;35"); D.drawRectangle(34, y + 34, 286, y + 44);
        if (f > 0) { D.setFillColor(c); D.drawRectangle(34, y + 34, 34 + 252 * f, y + 44); }
        if (e === "mordido") {                                     // infección: cuánto le queda a la mordida
          const g = Math.max(0, Math.min(1, 1 - seg(scn, k) / CFG.mordidaSeg));
          D.setFillColor("150;60;200"); D.drawRectangle(34, y + 46, 34 + 252 * g, y + 50);
        }
      }
    }
  }

  // ------------------------------------------------------------------ API llamada desde los eventos
  const API = (gdjs.fdizProfes = { ver: VER, PROFES, CFG, ORDEN });

  // Después del grupo "Entrada": quien está en el diálogo no se mueve ni pega (host y sin red).
  API.input = function (scn) {
    if (rol(scn) === 2) return;
    const st = S(scn); if (!st.dlg) return;
    for (const s of objs(scn, "Sup")) if (num(s, "Jugador") === st.dlg.jug)
      for (const n of ["MovX", "MovY", "QuierePegar", "Usando", "PideHab", "PideEsp", "QuiereLanzar"]) VS(s, n).setNumber(0);
  };

  // Grupo "Profesores reclutables" (corre en todas las máquinas).
  API.tick = function (scn) {
    const st = S(scn), r = rol(scn), V = SV(scn);
    // red: el host recibe decisiones; el cliente no manda la entrada de quien está en el diálogo
    const N = gdjs.fdizNet;
    if (N) {
      N.onProf = (peer, d) => { if (N.scn === scn || !N.scn) aplicar(scn, d.k, d.d, peer); };
      N.onLocalInput = (sc, p) => { const D = S(sc).dlg; if (!D) return; for (const q of p) if (q.s === D.jug - 1) { q.mx = 0; q.my = 0; q.hit = 0; q.use = 0; q.hab = 0; q.esp = 0; q.lz = 0; q.dr = 0; } };
    }
    leerEntrada(scn, st);
    // ProfDlg bloquea la pausa (Esc / P / Start) mientras hay diálogo y hasta 2 cuadros después de soltar Esc/Retroceso
    if (st.cierre > 0) st.cierre--;
    st.libre = st.kbH.cerrar ? 0 : (st.libre || 0) + 1;
    if (!st.dlg && st.cierre === 0 && st.libre >= 2 && V.get("ProfDlg").getAsNumber() !== 0) V.get("ProfDlg").setNumber(0);
    if (r === 2) for (const s of objs(scn, "Sup")) if (num(s, "Jugador") >= 5) VS(s, "Control").setNumber(-1); // en el cliente no son jugadores locales
    if (r !== 2) logicaHost(scn, st);
    // interfaz
    st.ui.n = 0; st.ui.pn = 0;
    if (st.dlg) manejarDialogo(scn, st);
    if (!st.dlg) buscarInteraccion(scn, st, true);
    gritos(scn, st);
    dibujar(scn, st);
    for (let i = st.ui.n; i < st.ui.a.length; i++) st.ui.a[i].hide(true);
    for (let i = st.ui.pn; i < st.ui.pa.length; i++) st.ui.pa[i].hide(true);
  };

  // Después de "Bots: curar mordidos": los bots (alumnos o profes) auxilian a un profe caído o mordido; Canepa va al camión en el final.
  API.bots = function (scn) {
    if (rol(scn) === 2) return;
    const V = SV(scn), sups = objs(scn, "Sup");
    const necesita = sups.filter((s) => num(s, "Jugador") >= 5 && (str(s, "Estado") === "caido" || (str(s, "Estado") === "normal" && num(s, "Mordido") === 1)));
    const ocupado = (b) => { // ya va a ayudar a un alumno principal (eventos existentes)
      for (let j = 1; j <= 4; j++) {
        if (num(b, "Jugador") === j) continue;
        const ok = V.get("J" + j + "Ok").getAsNumber(), m = V.get("M" + j).getAsNumber();
        if ((ok === 2 || m === 1) && Math.hypot(b.getX() - V.get("J" + j + "X").getAsNumber(), b.getY() - V.get("J" + j + "Y").getAsNumber()) < 600) return true;
      }
      return false;
    };
    for (const b of sups) {
      if (num(b, "Control") !== -1 || str(b, "Estado") !== "normal") continue;
      let obj = null, md = CFG.ayudaBotRadio;
      for (const s of necesita) { if (s === b) continue; const d = dist(b, s); if (d < md) { md = d; obj = s; } }
      if (obj && !ocupado(b)) {
        const d = Math.max(1, md);
        if (d < 70) { VS(b, "MovX").setNumber(0); VS(b, "MovY").setNumber(0); VS(b, "Usando").setNumber(1); VS(b, "QuierePegar").setNumber(0); }
        else { VS(b, "MovX").setNumber((obj.getX() - b.getX()) / d); VS(b, "MovY").setNumber((obj.getY() - b.getY()) / d); VS(b, "QuierePegar").setNumber(0); }
        continue;
      }
      // Canepa: último tramo hasta su lugar junto al camión (si no hay zombis encima)
      if (num(b, "Jugador") === 7 && V.get("FinalActivo").getAsNumber() === 1 && num(b, "Mordido") === 0) {
        let cerca = false; for (const n of ZOMBIS) for (const z of objs(scn, n)) if (!cerca && str(z, "Estado") !== "muerto" && dist(z, b) < 220) cerca = true;
        const d = Math.hypot(b.getX() - CFG.reparar.x, b.getY() - CFG.reparar.y);
        if (!cerca && d > 30 && d < 300) { VS(b, "MovX").setNumber((CFG.reparar.x - b.getX()) / d); VS(b, "MovY").setNumber((CFG.reparar.y - b.getY()) / d); VS(b, "QuierePegar").setNumber(0); }
        else if (!cerca && d <= 30) { VS(b, "MovX").setNumber(0); VS(b, "MovY").setNumber(0); }
      }
    }
  };
  // Dentro de "Bots" (después de repartir BotX/BotY): Canepa aliado camina por ruta hasta el camión durante el final.
  API.botsDestino = function (scn) {
    if (rol(scn) === 2 || SV(scn).get("FinalActivo").getAsNumber() !== 1) return;
    const c = supDe(scn, "canepa"); if (!c || str(c, "Estado") !== "normal") return;
    VS(c, "BotX").setNumber(CFG.reparar.x); VS(c, "BotY").setNumber(CFG.reparar.y);
  };
  // En "Vida, caída y revivir" (después de los eventos Ayuda de J1..J4): un profe de pie que mantiene Usar revive al caído de junto.
  API.ayuda = function (scn) {
    if (rol(scn) === 2) return;
    const sups = objs(scn, "Sup");
    const h = sups.filter((s) => num(s, "Jugador") >= 5 && str(s, "Estado") === "normal" && num(s, "Usando") === 1);
    if (!h.length) return;
    for (const s of sups) if (str(s, "Estado") === "caido" && h.some((o) => o !== s && dist(o, s) < CFG.revivirRadio)) VS(s, "Ayuda").setNumber(1);
  };
  // Al inicio de "Compañeros mordidos": mordidas de los profes aliados (12 % por golpe, como los alumnos).
  API.mordidas = function (scn) {
    if (rol(scn) === 2 || SV(scn).get("Estado").getAsString() !== "juego") return;
    for (const s of objs(scn, "Sup")) {
      if (num(s, "Jugador") < 5 || num(s, "Golpeado") !== 1 || num(s, "Mordido") !== 0 || str(s, "Estado") !== "normal") continue;
      if (Math.random() >= CFG.probMordida) continue;
      VS(s, "Mordido").setNumber(1); VS(s, "Cura").setNumber(0); s.resetTimer("mordida");
      const k = str(s, "Personaje"); const P = PROFES[k];
      banner(scn, "¡" + (P ? P.nombre.toUpperCase() : "PROFE") + " MORDIDO!", 2.5);
      sonido(scn, "efectos/combate/mordida.ogg", 65);
    }
  };
  // Dentro de cada ciclo M1..M4 (objects = el alumno mordido): un profe de pie que mantiene Usar junto a él también lo cura.
  API.curaAlumno = function (scn, objetos) {
    if (rol(scn) === 2 || !objetos || !objetos.length) return;
    const m = objetos[0];
    for (const s of objs(scn, "Sup"))
      if (num(s, "Jugador") >= 5 && str(s, "Estado") === "normal" && num(s, "Usando") === 1 && dist(s, m) < CFG.curaRadio) { VS(m, "Curando").setNumber(1); return; }
  };
})(gdjs);
