/* FDI-Z · Fase 65 · Cinemáticas del modo Historia como videos (8). Solo en Historia; Escape y Jefe no cambian.
 * Se incrusta en la escena Juego con scripts/fase65_cinematicas.py (FDIZ-FASE65-MOD y -TICK, sin compuerta de host).
 * No editar el evento a mano: editar este archivo y volver a correr el script.
 *
 * Videos: gdevelop/FDI-Z/assets/interfaz/videos/historia/<archivo> (VIDEOS, abajo). El script crea el objeto VidHist0N
 * solo si el archivo existe. Si falta, se muestra una tarjeta de texto breve con lo que pasa (alternativa segura) y la
 * historia sigue; para el 8 (Canepa) la alternativa es la charla con burbujas de la fase 61.
 *
 * Cuándo (una sola vez por partida: HistVistos, sincronizada en línea):
 *   1 al empezar una partida de Historia, en el salón; después, un interludio corto: la puerta empieza a romperse.
 *   2 un jugador entra a los Cubículos del CIC y Joel sigue esperando ayuda.
 *   3 se completa la llamada en la computadora del CIC (el teléfono no tiene línea y se va la luz: sigue la misión 2).
 *   4 se abre (o se derriba) la puerta de la conserjería (P59).
 *   5 se abre el casillero de la conserjería, que guarda la escopeta (aparece al terminar).
 *   6 un jugador llega a la nevería, junto a Justino, que sigue esperando.
 *   7 se abre el cajón del escritorio del director, que guarda el revólver sheriff (aparece al terminar).
 *   8 se habla con Canepa (misión 5): al terminar se cumple la misión y empieza la gasolina.
 * Durante el video, la tarjeta o el interludio (host / sin red): Estado = "cine", TimeScale 0, los jugadores sin control
 * (Control -2) y sin entradas; la música del canal 1 en pausa en cada máquina. Al terminar o saltar (Enter, Espacio, Esc,
 * clic, A o Start; 0.5 s después de empezar) todo vuelve a como estaba. */
(function (gdjs) {
  "use strict";
  if (gdjs.fdizCine && gdjs.fdizCine.VER === 1) return;
  const C = (gdjs.fdizCine = { VER: 1 });

  C.VIDEOS = {
    1: { archivo: "historia_01_inicio_aula.mp4", titulo: "EL SALÓN", texto: "El grupo espera al profe… hasta que llega la alerta: hay zombis en la escuela." },
    2: { archivo: "historia_02_joel_cic.mp4", titulo: "JOEL", texto: "En los cubículos del CIC encuentran al profe Joel. Necesita ayuda." },
    3: { archivo: "historia_03_telefono_apagon.mp4", titulo: "EL TELÉFONO", texto: "El teléfono del CIC no tiene línea… y se corta la energía." },
    4: { archivo: "historia_04_zombi_conserje.mp4", titulo: "LA CONSERJERÍA", texto: "Al abrir la puerta aparece el conserje… convertido en zombi." },
    5: { archivo: "historia_05_escopeta_casillero.mp4", titulo: "EL CASILLERO", texto: "En el casillero de la conserjería hay una escopeta." },
    6: { archivo: "historia_06_justino_neveria.mp4", titulo: "JUSTINO", texto: "En la nevería encuentran al profe Justino." },
    7: { archivo: "historia_07_cajon_director.mp4", titulo: "EL CAJÓN DEL DIRECTOR", texto: "En el cajón del escritorio del director hay un revólver." },
    8: { archivo: "historia_08_canepa_autobus.mp4", titulo: "CANEPA", texto: "" },
  };
  C.CFG = { carta: 3.5, saltar: 0.5, falla: 4, inter: 3.2, golpes: [0.5, 1.4, 2.3] };
  C.LUGAR = {
    salon: { x: 5984, y: 3024 }, puerta: "P06", zombis: [[5748, 3010], [5716, 2988]],
    armasSalon: [["silla", 5904, 3064], ["escoba", 6064, 3064]],
    cubiculos: [3488, 1920, 3744, 2080], neveria: [1536, 1440, 1984, 2432], conserjeria: "P59",
    casillero: { x: 5120, y: 596, arma: "escopeta", ax: 5136, ay: 650 },
    cajon: { x: 3328, y: 4436, arma: "pistola", ax: 3400, ay: 4470 },
  };
  C.now = () => Date.now() / 1000;

  const VS = (o, n) => o.getVariables().get(n);
  const num = (o, n) => VS(o, n).getAsNumber();
  const str = (o, n) => VS(o, n).getAsString();
  const SV = (scn, n) => scn.getVariables().get(n);
  const GV = (scn, n) => scn.getGame().getVariables().get(n);
  const objs = (scn, n) => { try { return scn.getObjects(n) || []; } catch (e) { return []; } };
  const rol = (scn) => { try { return GV(scn, "NetRol").getAsNumber(); } catch (e) { return 0; } };
  const historia = (scn) => { try { return GV(scn, "Modo").getAsString() === "historia"; } catch (e) { return false; } };
  const S = (scn) => scn._fdizCine || (scn._fdizCine = { prev: {}, ctl: new Map(), kb: {}, ini: false, local: { vid: null, n: 0, seq: -1, musica: false } });
  C.objeto = (n) => "VidHist0" + n;
  C.hayVideo = (scn, n) => { try { return scn.getObjects(C.objeto(n)) !== undefined && scn.getObjects(C.objeto(n)) !== null; } catch (e) { return false; } };
  C.visto = (scn, n) => ("," + SV(scn, "HistVistos").getAsString() + ",").includes("," + n + ",");
  function marcar(scn, n) { const v = SV(scn, "HistVistos").getAsString(); SV(scn, "HistVistos").setString(v ? v + "," + n : String(n)); }
  const humano = (s) => { const c = num(s, "Control"); return (c >= 0 || c === -3 || c === -2) && num(s, "Jugador") <= 4; };
  const dentro = (r, x, y) => x >= r[0] && x < r[2] && y >= r[1] && y < r[3];

  // ------------------------------------------------------------------ congelar / devolver (host)
  function congelar(scn, st) {
    if (st.congelado) return;
    st.congelado = true;
    st.estadoPrev = SV(scn, "Estado").getAsString();
    SV(scn, "Estado").setString("cine");
    try { st.escala = scn.getTimeManager().getTimeScale(); scn.getTimeManager().setTimeScale(0); } catch (e) { st.escala = 1; }
    st.ctl.clear();
    for (const s of objs(scn, "Sup")) {
      const c = num(s, "Control");
      if (c >= 0 || c === -3) { st.ctl.set(s, c); VS(s, "Control").setNumber(-2); }
      for (const n of ["MovX", "MovY", "QuierePegar", "Usando", "PideHab", "PideEsp", "QuiereLanzar"]) VS(s, n).setNumber(0);
    }
  }
  function devolver(scn, st) {
    if (!st.congelado) return;
    st.congelado = false;
    for (const [s, c] of st.ctl) { try { VS(s, "Control").setNumber(c); } catch (e) { /* ya no está */ } }
    st.ctl.clear();
    SV(scn, "Estado").setString(!st.estadoPrev || st.estadoPrev === "cine" ? "juego" : st.estadoPrev);
    try { scn.getTimeManager().setTimeScale(st.escala > 0 ? st.escala : 1); } catch (e) { /* sin gestor */ }
  }
  function publicar(scn, modo, n) {
    SV(scn, "CineModo").setString(modo); SV(scn, "CineVid").setNumber(n || 0);
    SV(scn, "CineSeq").setNumber(SV(scn, "CineSeq").getAsNumber() + 1);
  }

  // ------------------------------------------------------------------ empezar / terminar una cinemática (host)
  C.empezar = function (scn, n, despues) {
    const st = S(scn);
    if (st.activa || C.visto(scn, n)) return false;
    marcar(scn, n);
    congelar(scn, st);
    st.activa = { n, t0: C.now(), despues, modo: C.hayVideo(scn, n) ? "video" : "tarjeta" };
    publicar(scn, st.activa.modo, n);
    leerSalto(scn, st);                                    // la tecla con la que se interactuó no cuenta para saltar
    return true;
  };
  function terminar(scn, st) {
    const A = st.activa; st.activa = null;
    publicar(scn, "", 0);
    if (A && A.despues) A.despues(scn, st);
    if (!st.activa && !st.inter) devolver(scn, st);
  }
  function leerSalto(scn, st) {
    const I = gdjs.evtTools && gdjs.evtTools.input;
    let k = false;
    try { k = ["Return", "Space", "Escape"].some((t) => I.isKeyPressed(scn, t)) || I.isMouseButtonPressed(scn, "Left"); } catch (e) { /* sin entrada */ }
    let p = false;
    try { for (const g of (typeof navigator !== "undefined" && navigator.getGamepads ? navigator.getGamepads() : []) || []) if (g && g.buttons && ((g.buttons[0] && g.buttons[0].pressed) || (g.buttons[9] && g.buttons[9].pressed))) p = true; } catch (e) { /* sin mandos */ }
    const f = (k && !st.kb.k) || (p && !st.kb.p);
    st.kb.k = k; st.kb.p = p;
    return f;
  }

  // ------------------------------------------------------------------ interludio corto tras el video 1 (host)
  function interludio(scn, st) {
    const L = C.LUGAR;
    st.inter = { t0: C.now(), golpe: 0, zombis: [] };
    publicar(scn, "interludio", 1);
    for (const [x, y] of L.zombis) {
      const z = scn.createObject("ZNormal"); if (!z) continue;
      z.setLayer("Juego"); z.setPosition(x, y); VS(z, "Estado").setString("cinematica");
      st.inter.zombis.push({ z, x, y });
    }
    try { const Lj = scn.getLayer("Juego"); st.inter.cam = [Lj.getCameraX(), Lj.getCameraY()]; } catch (e) { /* sin capa */ }
  }
  function puerta(scn, id) { return objs(scn, "Puerta").find((p) => str(p, "Id") === id) || null; }
  function pasoInterludio(scn, st) {
    const I = st.inter, t = C.now() - I.t0, L = C.LUGAR, p = puerta(scn, L.puerta);
    while (I.golpe < C.CFG.golpes.length && t >= C.CFG.golpes[I.golpe]) {
      I.golpe++; I.golpeT = t;
      if (p) { p.setColor("255;150;150"); VS(p, "Vida").setNumber(Math.max(1, num(p, "Vida") - 10)); }
      try { if (GV(scn, "SonidoActivo").getAsNumber() === 1) gdjs.evtTools.sound.playSound(scn, "efectos/mundo/puerta_golpe.wav", false, 60, 1); } catch (e) { /* sin sonido */ }
    }
    const f = I.golpeT !== undefined ? Math.max(0, 1 - (t - I.golpeT) / 0.18) : 0;   // empujón y temblor de cada golpe
    for (const q of I.zombis) q.z.setPosition(q.x + 7 * f, q.y);
    if (p && f === 0) p.setColor("255;255;255");
    try { if (I.cam) { const Lj = scn.getLayer("Juego"); Lj.setCameraX(I.cam[0] + (f ? (Math.random() * 2 - 1) * 4 * f : 0)); Lj.setCameraY(I.cam[1]); } } catch (e) { /* sin capa */ }
    if (t < C.CFG.inter && !(t >= C.CFG.saltar && leerSalto(scn, st))) return;
    // fin: la puerta queda dañada, los zombis la siguen golpeando como siempre y el equipo recupera el control
    if (p) p.setColor("255;255;255");
    for (const q of I.zombis) { q.z.setPosition(q.x, q.y); VS(q.z, "Estado").setString("persigue"); }
    try { if (I.cam) { scn.getLayer("Juego").setCameraX(I.cam[0]); scn.getLayer("Juego").setCameraY(I.cam[1]); } } catch (e) { /* sin capa */ }
    for (const [tipo, x, y] of L.armasSalon) {                 // las mismas armas que deja la intro de Escape
      const a = scn.createObject("ArmaPiso"); if (!a) continue;
      a.setLayer("Juego"); a.setPosition(x, y); VS(a, "Tipo").setString(tipo); a.setAnimationName(tipo);
    }
    st.inter = null;
    publicar(scn, "", 0);
    devolver(scn, st);
  }

  // ------------------------------------------------------------------ preparar la partida de Historia (host, una vez)
  function preparar(scn, st) {
    st.ini = true;
    const L = C.LUGAR;
    // el equipo empieza en el salón (como en la intro de Escape)
    for (const s of objs(scn, "Sup")) {
      const j = num(s, "Jugador"); if (j < 1 || j > 4) continue;
      s.setPosition(L.salon.x + (j - 2.5) * 60, L.salon.y);
    }
    try { SV(scn, "CamX").setNumber(L.salon.x); SV(scn, "CamY").setNumber(L.salon.y); const Lj = scn.getLayer("Juego"); Lj.setCameraX(L.salon.x); Lj.setCameraY(L.salon.y); } catch (e) { /* sin capa */ }
    // la escopeta y el revólver van guardados (casillero de la conserjería y cajón del director)
    for (const a of objs(scn, "ArmaPiso").slice()) {
      const t = str(a, "Tipo");
      if ((t === L.casillero.arma && Math.hypot(a.getX() - L.casillero.ax, a.getY() - L.casillero.ay) < 40) ||
          (t === L.cajon.arma && Math.hypot(a.getX() - L.cajon.ax, a.getY() - L.cajon.ay) < 40)) a.deleteFromScene(scn);
    }
    const mk = (q, visible) => {
      const c = scn.createObject("Contenedor"); if (!c) return null;
      c.setLayer("Juego"); c.setPosition(q.x, q.y); c.setZOrder(q.y);
      VS(c, "Tipo").setString("locker"); VS(c, "Abierto").setNumber(0);
      try { c.setAnimationName("locker_cerrado"); } catch (e) { /* sin animación */ }
      if (!visible) c.hide(true);
      return c;
    };
    st.casillero = mk(L.casillero, true);
    st.cajon = mk(L.cajon, false);                             // el cajón es parte del escritorio: no se dibuja
    C.empezar(scn, 1, (sc, s) => interludio(sc, s));
  }
  function arma(scn, q) {
    const a = scn.createObject("ArmaPiso"); if (!a) return;
    a.setLayer("Juego"); a.setPosition(q.ax, q.ay); a.setZOrder(q.ay); VS(a, "Tipo").setString(q.arma); a.setAnimationName(q.arma);
  }

  // ------------------------------------------------------------------ momentos de la historia (host)
  function detectar(scn, st) {
    const L = C.LUGAR, hs = objs(scn, "Sup").filter((s) => humano(s) && str(s, "Estado") === "normal");
    const est = (k) => { try { return SV(scn, "Prof" + k).getAsString(); } catch (e) { return ""; } };
    if (!C.visto(scn, 2) && est("Joel") === "espera" && hs.some((s) => dentro(L.cubiculos, s.getX(), s.getY()))) return C.empezar(scn, 2);
    const jus = objs(scn, "Profe").find((p) => str(p, "Nombre") === "justino");
    if (!C.visto(scn, 6) && jus && est("Justino") === "espera" && hs.some((s) => dentro(L.neveria, s.getX(), s.getY()) && Math.hypot(s.getX() - jus.getX(), s.getY() - jus.getY()) < 240))
      return C.empezar(scn, 6);
    // la computadora del CIC se borra en el mismo cuadro en que se cumple la llamada: se detecta que ya no está
    const compu = objs(scn, "Objetivo").some((o) => str(o, "Tipo") === "computadora");
    if (st.vioCompu && !compu && !C.visto(scn, 3)) { st.vioCompu = false; return C.empezar(scn, 3); }
    st.vioCompu = compu;
    const p59 = puerta(scn, L.conserjeria);
    if (st.vioP59 && !p59 && !C.visto(scn, 4)) { st.vioP59 = false; return C.empezar(scn, 4); }
    if (p59) st.vioP59 = true;
    if (st.casillero && num(st.casillero, "Abierto") === 1 && !C.visto(scn, 5)) return C.empezar(scn, 5, (sc) => arma(sc, L.casillero));
    if (st.cajon && num(st.cajon, "Abierto") === 1 && !C.visto(scn, 7)) return C.empezar(scn, 7, (sc) => arma(sc, L.cajon));
    return false;
  }
  // Canepa (misión 5): con video, el video reemplaza la charla con burbujas (canepa.js pregunta aquí antes de empezar)
  C.toma = (scn) => !gdjs.fdizHistoria && historia(scn) && C.hayVideo(scn, 8) && !C.visto(scn, 8) || !!(S(scn).activa && S(scn).activa.n === 8);
  function canepa(scn, st) {
    let c = 0; try { c = SV(scn, "CanepaCharla").getAsNumber(); } catch (e) { return; }
    if (c === 1 && C.hayVideo(scn, 8) && !C.visto(scn, 8) && !st.activa)
      C.empezar(scn, 8, (sc) => { SV(sc, "CanepaCharla").setNumber(2); SV(sc, "Paso").setNumber(99); });
  }

  // ------------------------------------------------------------------ cada máquina: video o tarjeta en pantalla
  // fase 79: durante el video la música de fondo (canales 1 y 2) sigue; se cortan voces y efectos sueltos
  function musica(scn, L, pausar) {
    if (L.musica === pausar) return;
    L.musica = pausar;
    if (!pausar) return;
    try { gdjs.evtTools.sound.stopSoundOnChannel(scn, 7); } catch (e) { /* sin voz */ }
    try { const sm = scn.getSoundManager(); for (const x of (sm._freeSounds || [])) { try { x.stop(); } catch (e) { /* ya terminó */ } } } catch (e) { /* sin efectos */ }
  }
  function quitarVideo(L, scn) { if (L.vid) { try { L.vid.pause(); L.vid.deleteFromScene(scn); } catch (e) { /* ya no está */ } L.vid = null; L.n = 0; } }
  function pantalla(scn, st) {
    const L = st.local, modo = SV(scn, "CineModo").getAsString(), n = SV(scn, "CineVid").getAsNumber(), seq = SV(scn, "CineSeq").getAsNumber();
    musica(scn, L, modo === "video");   // fase 79: solo se cortan efectos y voces, la música sigue
    if (modo !== "video" || L.n !== n) quitarVideo(L, scn);
    if (modo === "video" && !L.vid) {
      const v = scn.createObject(C.objeto(n));
      if (v) {
        v.setLayer("HUD"); v.setPosition(0, 0); v.setZOrder(2000);
        try { v.setWidth(1920); v.setHeight(1080); } catch (e) { /* tamaño del objeto */ }
        try { v.setLoop(false); v.setCurrentTime(0); v.setVolume(Math.max(0, Math.min(100, GV(scn, "VolEfectos").getAsNumber() || 100))); } catch (e) { /* video sin cargar */ }
        try { v.play(); } catch (e) { /* video sin cargar */ }
        L.vid = v; L.n = n; L.t0 = C.now();
      }
    }
    // tarjeta (si falta el video): velo y texto
    let veil = L.veil;
    if (!veil) { veil = L.veil = scn.createObject("CineDib"); if (veil) { veil.setLayer("HUD"); veil.setPosition(0, 0); veil.setZOrder(1990); } }
    if (!L.tit) { for (const k of ["tit", "txt", "pie"]) { const t = scn.createObject("TxtCine"); if (t) { t.setLayer("HUD"); t.setZOrder(k === "pie" ? 2005 : 1995); } L[k] = t; } }
    if (veil) veil.clear();
    const carta = modo === "tarjeta" && C.VIDEOS[n];
    if (carta && veil) {
      veil.setFillColor("6;8;18"); veil.setFillOpacity(235); veil.setOutlineSize(0); veil.drawRectangle(0, 0, 1920, 1080);
    }
    const pon = (t, s, y, size, col) => { if (!t) return; t.hide(!s); if (!s) return; if (t.getString() !== s) t.setText(s); t.setCharacterSize(size); t.setColor(col);
      if (t.setWrapping) { t.setWrapping(true); t.setWrappingWidth(1300); } t.setPosition(960 - Math.min(1300, t.getWidth()) / 2, y); };
    pon(L.tit, carta ? C.VIDEOS[n].titulo : "", 420, 44, "255;230;120");
    pon(L.txt, carta ? C.VIDEOS[n].texto : "", 500, 30, "235;235;235");
    pon(L.pie, carta || modo === "video" ? (rol(scn) === 2 ? "" : "Enter / A: continuar") : "", 1000, 20, "170;170;190");
    L.seq = seq;
  }

  // ------------------------------------------------------------------ cada cuadro
  C.tick = function (scn) {
    if (gdjs.fdizHistoria) return;            // fase 68: la historia de 12 pasos (historia.js) reemplaza estas 8 cinemáticas
    if (!historia(scn)) return;
    const st = S(scn);
    if (rol(scn) !== 2) {
      // se prepara cuando cada jugador ya tiene su control y sus datos (Init), para devolverle después el mismo
      if (!st.ini && SV(scn, "Estado").getAsString() === "juego" &&
          objs(scn, "Sup").filter((s) => num(s, "Jugador") <= 4).every((s) => num(s, "Init") === 1) && objs(scn, "Sup").length) {
        st.listo = st.listo || C.now();
        if (C.now() - st.listo >= 0.2) preparar(scn, st);
      }
      if (st.inter) pasoInterludio(scn, st);
      else if (st.activa) {
        const A = st.activa, t = C.now() - A.t0, v = st.local.vid;
        let fin = t >= C.CFG.saltar && leerSalto(scn, st);
        if (A.modo === "tarjeta" && t >= C.CFG.carta) fin = true;
        if (A.modo === "video") {
          try {
            if (v && (v.isEnded() || (v.getDuration() > 0 && v.getCurrentTime() >= v.getDuration() - 0.05))) fin = true;
            if (t > C.CFG.falla && (!v || !(v.getDuration() > 0))) fin = true;              // no cargó: no se queda trabado
            if (v && v.getDuration() > 0 && t > v.getDuration() + 3) fin = true;
          } catch (e) { if (t > C.CFG.falla) fin = true; }
        }
        if (fin) terminar(scn, st);
      } else if (SV(scn, "Estado").getAsString() === "juego" && SV(scn, "Pausa").getAsNumber() !== 1) {
        canepa(scn, st);
        if (!st.activa) detectar(scn, st);
      }
    }
    pantalla(scn, st);
  };
})(gdjs);
