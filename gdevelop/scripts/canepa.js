/* FDI-Z · Fase 61 · Modo Historia: conversación con el profe Canepa en el camión (misión 5/6, entre la comida de la
 * nevería y la gasolina). Se incrusta en la escena Juego con scripts/fase61_canepa.py (FDIZ-FASE61-MOD y -TICK, sin
 * compuerta de host). No editar el evento a mano: editar este archivo y volver a correr el script.
 *
 * Flujo (variable de escena CanepaCharla, sincronizada en línea):
 *   0  pendiente   El evento del objetivo "canepa" (fase 55) la pone en 1 una sola vez, al terminar de mantener F junto
 *                  a Canepa. Mientras sea < 2, el diálogo de reclutamiento de Canepa no se ofrece en Historia
 *                  (reservado()), así nadie lo rechaza ni lo convierte antes de esta charla.
 *   1  diálogo     Host / sin red: Estado = "dialogo", el mundo se congela (TimeScale 0) y los jugadores no tienen control.
 *                  Las líneas van en orden (CinLinea, CinHabla); cada máquina dibuja la burbuja y pone la voz.
 *   2  hecha       Se devuelve todo como estaba, Paso = 99 (misión cumplida una sola vez) y sigue la gasolina.
 *
 * Burbujas: con el estilo de las de los profes (TxtProfe sobre ProfPanel, y una colita con DlgDib). Encima de quien
 * habla; si ahí tapan el HUD, una cara u otro texto, se corren a un lado o debajo de los pies.
 * Voces: VOCES[línea] = { pj, archivo }. Solo suena si el que habla es ese personaje; un solo canal (CANAL), así nunca
 * se encima una voz con otra. Sin archivo, la línea dura lo que tarda leerla y la secuencia sigue igual. */
(function (gdjs) {
  "use strict";
  if (gdjs.fdizCanepa && gdjs.fdizCanepa.VER === 1) return;
  const C = (gdjs.fdizCanepa = { VER: 1 });

  // rol: "canepa" (el profe), "tony" y "miranda" (si no están en el equipo, la línea la dice otro del equipo)
  C.LINEAS = [
    { rol: "canepa", txt: "¡Llegaron! Necesito ayuda. El autobús no puede salir." },
    { rol: "tony", txt: "¿Qué pasó?" },
    { rol: "canepa", txt: "No queda suficiente gasolina. Sin combustible no podremos alejarnos del campus." },
    { rol: "miranda", txt: "Acabamos de distraer a la horda. Podemos buscar gasolina." },
    { rol: "canepa", txt: "Gracias. Revisen el campus, pero tengan cuidado." },
    { rol: "tony", txt: "De acuerdo. Vamos a encontrarla." },
  ];
  // Voces grabadas de estas líneas: ninguna todavía (audios_fish no trae estas frases; Canepa es profe y no tiene voz).
  // Para agregar una: C.VOCES[1] = { pj: "tony", archivo: "voz_tony_que_paso.wav" } (nombre del recurso en GDevelop).
  C.VOCES = {};
  C.CANAL = 7;
  C.VOL = 95;
  C.CFG = { min: 2.4, porLetra: 0.055, max: 6.5, vozMax: 10, saltoMin: 0.6 };
  C.NOMBRES = { tony: "Tony", tonyfuerte: "Tony", miranda: "Miranda", cesar: "César", alan: "Alan", castillo: "Castillo",
    alessandro: "Alessandro", gabo: "Gabo", carlos: "Carlos", canepa: "Canepa" };
  // zonas del HUD (1920 x 1080) que las burbujas no deben tapar
  C.HUD = [[20, 16, 438, 250], [1482, 16, 1900, 250], [580, 14, 1340, 200], [20, 832, 438, 1064], [1482, 832, 1900, 1064],
    [658, 940, 1263, 1080], [1252, 662, 1892, 1054]];
  C.now = () => Date.now() / 1000;

  const VS = (o, n) => o.getVariables().get(n);
  const num = (o, n) => VS(o, n).getAsNumber();
  const str = (o, n) => VS(o, n).getAsString();
  const SV = (scn) => scn.getVariables();
  const GV = (scn) => scn.getGame().getVariables();
  const rol = (scn) => { try { return GV(scn).get("NetRol").getAsNumber(); } catch (e) { return 0; } };
  const historia = (scn) => { try { return GV(scn).get("Modo").getAsString() === "historia"; } catch (e) { return false; } };
  const objs = (scn, n) => { try { return scn.getObjects(n) || []; } catch (e) { return []; } };
  const estado = (scn) => SV(scn).get("CanepaCharla").getAsNumber();
  const S = (scn) => scn._fdizCn || (scn._fdizCn = { on: false, linea: -1, vozLinea: -1, ctl: new Map(), kb: {}, pad: {}, pool: null });

  C.duracion = (txt) => Math.max(C.CFG.min, Math.min(C.CFG.max, 1.2 + C.CFG.porLetra * txt.length));

  // Canepa no se ofrece para reclutar en Historia hasta después de esta charla (usar.js y profes.js lo preguntan)
  C.reservado = function (scn, nombre) {
    return nombre === "canepa" && historia(scn) && estado(scn) < 2;
  };

  // ------------------------------------------------------------------ quién dice cada línea
  C.asignar = function (scn) {
    const eq = objs(scn, "Sup").filter((s) => num(s, "Jugador") >= 1 && num(s, "Jugador") <= 4)
      .sort((a, b) => (str(b, "Estado") === "normal") - (str(a, "Estado") === "normal") || num(a, "Jugador") - num(b, "Jugador"));
    const de = (re) => eq.find((s) => re.test(str(s, "Personaje")));
    let tony = de(/^tony/), mir = de(/^miranda$/);
    const libres = eq.filter((s) => s !== tony && s !== mir);
    if (!tony) tony = libres.shift() || mir;
    if (!mir) mir = libres.shift() || tony;
    const id = (s) => (s ? "sup:" + num(s, "Jugador") : "");
    return { canepa: "npc:canepa", tony: id(tony), miranda: id(mir) };
  };
  function hablante(scn, id) {
    if (!id) return null;
    if (id === "npc:canepa") {
      for (const p of objs(scn, "Profe")) if (str(p, "Nombre") === "canepa") return p;
      for (const s of objs(scn, "Sup")) if (num(s, "Jugador") === 7) return s;
      return null;
    }
    const j = Number(id.slice(4));
    for (const s of objs(scn, "Sup")) if (num(s, "Jugador") === j) return s;
    return null;
  }
  const pjDe = (o) => (o ? (o.getVariables().has && o.getVariables().has("Personaje") ? str(o, "Personaje") : str(o, "Nombre")) : "");

  // ------------------------------------------------------------------ host / sin red
  function linea(scn, st, i) {
    st.i = i; st.t0 = C.now();
    SV(scn).get("CinLinea").setNumber(i);
    SV(scn).get("CinHabla").setString(i >= 0 ? st.quien[C.LINEAS[i].rol] || "" : "");
  }
  function iniciar(scn, st) {
    st.on = true;
    st.quien = C.asignar(scn);
    const V = SV(scn);
    st.estadoPrev = V.get("Estado").getAsString();
    V.get("Estado").setString("dialogo");                          // se detienen objetivos, cámara, bots, profes, pausa
    try { st.escala = scn.getTimeManager().getTimeScale(); scn.getTimeManager().setTimeScale(0); } catch (e) { st.escala = 1; }
    st.ctl.clear();
    for (const s of objs(scn, "Sup")) {
      const c = num(s, "Control");
      if (c >= 0 || c === -3) { st.ctl.set(s, c); VS(s, "Control").setNumber(-2); }  // como en la intro: sin control
      for (const n of ["MovX", "MovY", "QuierePegar", "Usando", "PideHab", "PideEsp", "QuiereLanzar"]) VS(s, n).setNumber(0);
    }
    leerEntrada(scn, st);                                           // la F con la que se habló no cuenta para saltar
    linea(scn, st, 0);
  }
  function terminar(scn, st) {
    st.on = false;
    const V = SV(scn);
    linea(scn, st, -1);
    for (const [s, c] of st.ctl) { try { VS(s, "Control").setNumber(c); } catch (e) { /* ya no existe */ } }
    st.ctl.clear();
    V.get("Estado").setString(st.estadoPrev === "dialogo" || !st.estadoPrev ? "juego" : st.estadoPrev);
    try { scn.getTimeManager().setTimeScale(st.escala > 0 ? st.escala : 1); } catch (e) { /* sin gestor */ }
    V.get("CanepaCharla").setNumber(2);
    V.get("Paso").setNumber(99);                                    // misión 5 cumplida (una sola vez: solo desde 1)
  }
  function leerEntrada(scn, st) {
    const I = gdjs.evtTools && gdjs.evtTools.input;
    let k = false;
    try { k = I.isKeyPressed(scn, "Return") || I.isKeyPressed(scn, "Space") || I.isKeyPressed(scn, "f") || I.isMouseButtonPressed(scn, "Left"); } catch (e) { /* sin entrada */ }
    let p = false;
    try { const g = typeof navigator !== "undefined" && navigator.getGamepads ? navigator.getGamepads() : []; for (const x of g || []) if (x && x.buttons && x.buttons[0] && x.buttons[0].pressed) p = true; } catch (e) { /* sin mandos */ }
    const flanco = (k && !st.kb.k) || (p && !st.kb.p);
    st.kb.k = k; st.kb.p = p;
    return flanco;
  }
  function host(scn, st) {
    if (!st.on) {
      // fase 65: si está el video de Canepa (historia_08), el video reemplaza esta charla (cine.js la cierra)
      if (estado(scn) === 1 && !(gdjs.fdizCine && gdjs.fdizCine.toma(scn))) iniciar(scn, st);
      return;
    }
    const salto = leerEntrada(scn, st);
    const t = C.now() - st.t0, L = C.LINEAS[st.i];
    const voz = st.vozLinea === st.i && st.vozSuena;
    const listo = (t >= C.duracion(L.txt) && !(voz && t < C.CFG.vozMax)) || (salto && t >= C.CFG.saltoMin);
    if (!listo) return;
    if (st.i + 1 < C.LINEAS.length) linea(scn, st, st.i + 1); else terminar(scn, st);
  }

  // ------------------------------------------------------------------ voces (cada máquina, en un solo canal)
  function voces(scn, st, i, quien) {
    const S_ = gdjs.evtTools && gdjs.evtTools.sound;
    if (i === st.vozLinea) {
      st.vozSuena = !!(S_ && st.vozArchivo && (() => { try { return S_.isSoundOnChannelPlaying(scn, C.CANAL); } catch (e) { return false; } })());
      return;
    }
    st.vozLinea = i; st.vozArchivo = null; st.vozSuena = false;
    try { if (S_) S_.stopSoundOnChannel(scn, C.CANAL); } catch (e) { /* nada sonaba */ }
    const V = i >= 0 ? C.VOCES[i] : null;
    if (!V || !V.archivo || !S_) return;                           // sin grabación: solo texto
    if (V.pj && !new RegExp("^" + V.pj).test(pjDe(quien))) return;  // la dice otro personaje: no se usa esa voz
    try {
      if (GV(scn).get("SonidoActivo").getAsNumber() !== 1) return;
      S_.playSoundOnChannel(scn, V.archivo, C.CANAL, false, C.VOL, 1);
      st.vozArchivo = V.archivo; st.vozSuena = true;
    } catch (e) { st.vozArchivo = null; st.vozSuena = false; }   // archivo que no carga: la línea sigue sin voz
  }

  // ------------------------------------------------------------------ burbuja
  const aPantalla = (scn, x, y) => {
    const c = scn.getLayer("Juego").convertInverseCoords(x, y, 0);
    return scn.getLayer("HUD").convertCoords(c[0], c[1], 0);
  };
  const cruce = (a, b) => Math.max(0, Math.min(a[2], b[2]) - Math.max(a[0], b[0])) * Math.max(0, Math.min(a[3], b[3]) - Math.max(a[1], b[1]));
  function caja(scn, o) {
    const x0 = o.getDrawableX ? o.getDrawableX() : o.getX() - 30, y0 = o.getDrawableY ? o.getDrawableY() : o.getY() - 120;
    const a = aPantalla(scn, x0, y0), b = aPantalla(scn, x0 + o.getWidth(), y0 + o.getHeight());
    return [a[0], a[1], b[0], b[1]];
  }
  // elige dónde va la burbuja (w x h) del que habla: encima, corrida a un lado o debajo de los pies
  C.colocar = function (scn, quien, w, h, extra) {
    const k = caja(scn, quien), cx = (k[0] + k[2]) / 2;
    const caras = [];
    for (const n of ["Sup", "Profe"]) for (const o of objs(scn, n)) {
      if (o.isHidden && o.isHidden()) continue;
      const b = caja(scn, o); caras.push([b[0], b[1], b[2], b[1] + (b[3] - b[1]) * 0.45]);
    }
    const evitar = C.HUD.concat(extra || []);
    const cand = [];
    [0, -0.35, 0.35, -0.7, 0.7].forEach((dx, n) => cand.push({ x: cx - w / 2 + dx * w, y: k[1] - 22 - h, arriba: true, pref: n }));
    [0, -0.5, 0.5].forEach((dx, n) => cand.push({ x: cx - w / 2 + dx * w, y: k[3] + 22, arriba: false, pref: 6 + n }));
    let mejor = null;
    for (const c of cand) {
      const x = Math.max(16, Math.min(1920 - 16 - w, c.x)), y = Math.max(16, Math.min(1080 - 16 - h, c.y));
      const r = [x, y, x + w, y + h];
      let p = c.pref * 40 + Math.abs(x - c.x) * 2 + Math.abs(y - c.y) * 4;
      for (const z of evitar) p += cruce(r, z) * 4;
      for (const z of caras) p += cruce(r, z) * 3;
      if (!mejor || p < mejor.p) mejor = { x, y, w, h, arriba: c.arriba, p, cx: Math.max(x + 18, Math.min(x + w - 18, cx)), ty: c.arriba ? k[1] : k[3] };
    }
    return mejor;
  };
  function pool(scn, st) {
    if (st.pool && st.pool.ok) return st.pool;
    const mk = (n, z) => { const o = scn.createObject(n); if (o) { o.setLayer("HUD"); o.setZOrder(z); } return o; };
    st.pool = { ok: true, panel: mk("ProfPanel", 430), nom: mk("TxtProfe", 432), txt: mk("TxtProfe", 432), dib: mk("DlgDib", 431) };
    const P = st.pool;
    if (P.nom) { P.nom.setCharacterSize(18); P.nom.setColor("255;230;120"); if (P.nom.setTextAlignment) P.nom.setTextAlignment("left"); }
    if (P.txt) { P.txt.setCharacterSize(20); P.txt.setColor("255;255;255"); P.txt.setWrapping(true); P.txt.setWrappingWidth(460); if (P.txt.setTextAlignment) P.txt.setTextAlignment("left"); }
    if (P.dib) P.dib.setPosition(0, 0);
    return P;
  }
  function ocultar(st) {
    const P = st.pool; if (!P) return;
    for (const k of ["panel", "nom", "txt"]) if (P[k]) P[k].hide(true);
    if (P.dib) P.dib.clear();
  }
  function dibujar(scn, st, i, quien) {
    const P = pool(scn, st);
    if (!P.txt || !P.panel || !P.nom) return;
    const L = C.LINEAS[i];
    const nombre = C.NOMBRES[pjDe(quien)] || C.NOMBRES[L.rol] || "";
    if (P.txt._k !== i) { P.txt._k = i; P.txt.setText("«" + L.txt + "»"); P.nom.setText(nombre.toUpperCase()); }
    const PAD = 14, w = Math.max(P.txt.getWidth(), P.nom.getWidth()) + PAD * 2, h = P.nom.getHeight() + 4 + P.txt.getHeight() + PAD * 1.4;
    const extra = [];
    for (const n of ["TxtBanner", "TxtAyuda"]) for (const t of objs(scn, n)) {
      if ((t.isHidden && t.isHidden()) || !(t.getString ? t.getString() : "")) continue;
      extra.push([t.getX(), t.getY(), t.getX() + t.getWidth(), t.getY() + t.getHeight()]);
    }
    const B = quien ? C.colocar(scn, quien, w, h, extra) : { x: 960 - w / 2, y: 700 - h, w, h, arriba: true, cx: 960, ty: 720 };
    P.panel.hide(false); P.panel.setPosition(B.x, B.y); P.panel.setWidth(w); P.panel.setHeight(h);
    P.nom.hide(false); P.nom.setPosition(B.x + PAD, B.y + PAD * 0.6);
    P.txt.hide(false); P.txt.setPosition(B.x + PAD, B.y + PAD * 0.6 + P.nom.getHeight() + 4);
    if (P.dib) {                                                    // colita hacia quien habla
      const d = P.dib; d.clear();
      d.setFillColor("14;18;44"); d.setFillOpacity(226); d.setOutlineSize(2); d.setOutlineColor("6;8;20"); d.setOutlineOpacity(235);
      const y0 = B.arriba ? B.y + h - 1 : B.y + 1, y1 = B.arriba ? Math.min(B.ty - 4, y0 + 18) : Math.max(B.ty + 4, y0 - 18);
      d.beginFillPath(B.cx - 10, y0); d.drawPathLineTo(B.cx + 10, y0); d.drawPathLineTo(B.cx, y1); d.closePath(); d.endFillPath();
    }
    C.ultima = B;
  }

  // ------------------------------------------------------------------ cada cuadro (todas las máquinas)
  C.tick = function (scn) {
    if (!historia(scn)) return;
    const st = S(scn);
    if (rol(scn) !== 2) host(scn, st);
    const i = SV(scn).get("CinLinea").getAsNumber();
    const activa = estado(scn) === 1 && i >= 0 && i < C.LINEAS.length;
    const quien = activa ? hablante(scn, SV(scn).get("CinHabla").getAsString()) : null;
    voces(scn, st, activa ? i : -1, quien);
    if (activa) dibujar(scn, st, i, quien); else ocultar(st);
  };
})(gdjs);
