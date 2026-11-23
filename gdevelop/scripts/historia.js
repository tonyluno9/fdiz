/* FDI-Z · Fase 68 · MODO HISTORIA (12 pasos fijos). Solo con Modo global = "historia"; Escape y Jefe no cambian.
 * Fuente: gdevelop/historia/02_HISTORIA_PARA_GDEVELOP.md (secuencia) y 01_DIALOGOS_PARA_VOCES.md (textos y voces).
 * Se incrusta en la escena Juego con scripts/fase68_historia.py (no editar el evento a mano: editar este archivo y volver a
 * correr el script). Datos (líneas, voces y duración de cada audio, videos que existen): gdjs.fdizHistoriaDatos, que el
 * script genera en el evento FDIZ-FASE68-DATOS.
 *
 * Sistemas:
 *   Cinemáticas  video a pantalla completa (capa HUD, encima de todo), con el mundo congelado (Estado "cine", TimeScale 0,
 *                jugadores sin control) y la música del juego en pausa. Mantener Espacio / Enter / A 1 s la salta
 *                (indicador circular abajo a la derecha). Si el archivo no existe: pantalla negra 1 s y siguen los diálogos.
 *                Cada video se ve una vez por partida (Historia.CinematicasVistas, global: sobrevive al reintentar).
 *   Diálogos     línea por línea {audio, personaje, texto}: globo sobre quien habla (o retrato + nombre abajo si no está en
 *                pantalla) y su voz en un canal propio (8). Pasa a la siguiente al terminar el audio + 0.3 s; Espacio
 *                adelanta. Bloqueantes [D]: el mundo se congela. De gameplay [G]: el juego sigue.
 *   Objetivos    texto en el letrero de objetivos de siempre (TxtObjetivo) y la flecha amarilla de siempre hacia la zona
 *                (HistObjX/HistObjY). Zonas = rectángulos invisibles; se activan cuando entra cualquier jugador del equipo.
 *                Las de "usar" son un Objetivo (F / A, como los demás objetivos del juego).
 *   Checkpoints  al empezar cada paso se guarda Historia.Paso (y armas). Al reintentar desde Resultados la partida vuelve
 *                al inicio de ese paso, con el mundo como debe estar en ese momento.
 * Autoridad: el host (o sin red) decide todo; HistCine, HistLinea, HistHabla, HistVelo, HistAlarma y HistAyuda viajan a
 * los clientes, que solo dibujan y ponen las voces. */
(function (gdjs) {
  "use strict";
  if (gdjs.fdizHistoria && gdjs.fdizHistoria.VER === 1) return;
  const H = (gdjs.fdizHistoria = { VER: 1 });

  // ------------------------------------------------------------------ configuración
  H.CANAL = 8;              // voces de la historia (dialogo.js usa el 7)
  H.CANAL_ALARMA = 9;
  H.VOL = 100;
  H.HUECO = 0.3;            // s después de cada audio
  H.SALTAR = 1.0;           // s manteniendo para saltar un video
  H.NEGRO = 1.0;            // s de pantalla negra si falta un video
  H.FALLA = 6;              // s: un video que no carga no deja la historia trabada
  H.EQUIPO = ["tony", "miranda", "alan", "cesar"];
  H.NOMBRES = { alan: "Alan", miranda: "Miranda", tony: "Tony", cesar: "César", joel: "Joel", justino: "Justino", canepa: "Canepa", altavoz: "Altavoz" };
  H.COLORES = { alan: "150;150;160", miranda: "215;170;120", tony: "255;255;255", cesar: "90;160;255", joel: "110;220;120",
    justino: "255;140;200", canepa: "255;160;60", altavoz: "255;70;70" };
  H.TITULOS = { C01_T1: "La bolsa", C01_T2: "La bolsa", C02: "La pistola y la alarma", C03: "Golpes en la puerta", C04: "El profe Joel",
    C05: "Sin línea", C06: "La sala del conserje", C065: "La escopeta", C07: "Justino en la nevería", C08: "La oficina del director",
    C09: "El autobús y Canepa", C10: "Escape" };

  // Zonas: [x0, y0, x1, y1] en el mundo (Zona_<id> del documento). Ver gdevelop/BITACORA.md (fase 68) para el porqué de cada una.
  H.ZONAS = {
    Escritorio: [5904, 2884, 6064, 2984],     // frente al escritorio del profe, salón B-01
    Pasillo1: [4380, 2080, 4460, 4300],       // franja a mitad de camino entre B-01 y el CIC (cualquier ruta la cruza)
    CIC: [2688, 1632, 3744, 2080],            // CIC con sus dos pasillos (oeste y este)
    Conserje: [4930, 792, 5190, 884],         // pasillo frente a la puerta de la conserjería (P59)
    Neveria: [1536, 1440, 1984, 2432],
    Direccion: [3200, 4256, 3456, 4544],      // oficina del director
    Autobus: [240, 3080, 740, 3460],          // junto al autobús (400, 3264) y Canepa (544, 3328)
  };
  // Zonas de "usar" (mantener F / A): un Objetivo en ese punto. ver = se dibuja (el teléfono es la computadora del CIC).
  // sala = hay que estar adentro; puerta = esa puerta ya se abrió o la tumbaron (fase 69: nada se revisa a través de un muro)
  H.USAR = {
    Telefono: { x: 3136, y: 1760, anim: "computadora", ver: true, tipo: "h_telefono", sala: [2976, 1632, 3456, 2080] },
    Casillero: { x: 5112, y: 622, anim: "llaves", ver: false, tipo: "h_casillero", sala: [4896, 512, 5216, 768], puerta: "P59" },
    CajonDirector: { x: 3328, y: 4436, anim: "llaves", ver: false, tipo: "h_cajon", sala: [3200, 4256, 3456, 4544], puerta: "P47" },
  };
  H.SALON = [5700, 2700, 6250, 3350];         // la luz roja de la alarma se ve con la cámara aquí
  H.REJA = { x: 1504, y: 3072, w: 32, h: 480 };  // la única entrada del campus al estacionamiento: la "reja trasera"
  H.SPAWN = { salon: [5984, 3024, 60], cic: [3216, 1960, 50], conserjeria: [5056, 690, 50], neveria: [1760, 1800, 50], direccion: [3328, 4486, 50] };
  H.LUGAR = {
    puertaSalon: "P06", puertaConserje: "P59", puertaDireccion: "P47",
    intruso: [5740, 3008], intendencia: [5100, 640],
    pasilloCIC: [[2816, 1700], [3600, 1700], [3660, 1820]],
    joelQueda: [5000, 690], locker: [5112, 600],
    conserje: [4600, 4400], armasFuera: [["escopeta", 5136, 650], ["pistola", 3400, 4470]],
    olas: [[620, 2600], [620, 3900], [1300, 2700], [1300, 3800], [200, 2750], [200, 3750]],
  };
  H.FINAL_SEG = 90;
  // fase 71: pasos en los que Tony se mueve libre durante los diálogos (inicio en el salón, Joel y la llamada del CIC)
  H.DLG_LIBRE = { 1: true, 2: true, 3: true, 4: true, 5: true, 6: true, 7: true, 8: true, 9: true, 10: true, 11: true, 12: true };   // fase 73: todos
  // fase 71: en (5960, 2960) quedaba dentro del choque del escritorio y no se alcanzaba; ahora en el pasillo izquierdo del salón
  H.PISTOLA = { x: 5830, y: 3036 };

  // Los 12 pasos. obj = objetivo que se muestra al empezar el paso (con su zona o "usar"); auto = empieza solo.
  // seq: ["fade"] · ["v", video] · ["d", líneas...] (bloqueante) · ["e", evento] · ["w", espera] (el juego sigue)
  H.PASOS = {
    1: { spawn: "salon", auto: true, seq: [["fade"], ["d", "INT_01_cesar", "INT_02_alan", "INT_03_cesar", "INT_04_miranda", "INT_05_tony", "INT_06_alan"]] },
    2: { spawn: "salon", obj: { txt: "Revisa el escritorio del profe", zona: "Escritorio" },
      seq: [["v", "C01_T1"], ["d", "C1_01_alan", "C1_02_miranda"], ["v", "C01_T2"], ["d", "C1_03_alan", "C1_04_cesar", "C1_05_tony"]] },
    3: { spawn: "salon", auto: true, seq: [["v", "C02"], ["d", "C2_01_alan", "C2_02_miranda"], ["e", "alarma"], ["d", "C2_03_altavoz", "C2_04_cesar"]] },
    4: { spawn: "salon", auto: true, seq: [["v", "C03"], ["d", "C3_01_miranda", "C3_02_tony", "C3_03_cesar"], ["e", "pistola"], ["e", "controla", "tony"], ["e", "irrumpe"], ["w", "intruso"]] },
    5: { spawn: "salon", obj: { txt: "Llega al CIC", zona: "CIC", puerta: ["P37", "P38"], txt2: "Checa de dónde viene el ruido", flecha: [3760, 1824] },
      seq: [["v", "C04"], ["d", "C4_01_joel", "C4_02_tony", "C4_03_joel", "C4_04_miranda", "C4_05_alan", "C4_06_joel"], ["e", "joel"]] },
    6: { spawn: "cic", obj: { txt: "Usa el teléfono del CIC", usar: "Telefono" },
      seq: [["v", "C05"], ["e", "apagon"], ["d", "C5_01_tony", "C5_02_joel", "C5_03_miranda"], ["e", "zombisPasillo"]] },
    7: { spawn: "cic", obj: { txt: "Encuentra la sala del conserje", zona: "Conserje" },
      seq: [["v", "C06"], ["d", "C6_01_tony", "C6_02_alan"], ["e", "intendencia"], ["w", "intendencia"]] },
    8: { spawn: "conserjeria", obj: { txt: "Revisa el casillero del conserje", usar: "Casillero" },
      seq: [["v", "C065"], ["d", "C65_01_cesar", "C65_02_joel", "C65_03_tony"], ["e", "escopeta"], ["e", "controla", "cesar"], ["d", "C65_04_joel", "C65_05_tony"], ["e", "joelSeQueda"]] },
    9: { spawn: "conserjeria", obj: { txt: "Busca a otro profesor: la nevería", zona: "Neveria" },
      seq: [["v", "C07"], ["d", "C7_01_justino", "C7_02_miranda", "C7_03_justino", "C7_04_tony", "C7_05_justino", "C7_06_alan", "C7_07_justino"], ["e", "justino"], ["e", "pasaEscopeta"], ["e", "controla", "miranda"]] },
    10: { spawn: "neveria", obj: { txt: "Consigue la llave en la oficina del director", zona: "Direccion", usar: "CajonDirector", txt2: "Revisa el escritorio del director" },
      seq: [["v", "C08"], ["e", "llave"], ["e", "controla", "alan"], ["d", "C8_01_tony", "C8_02_cesar", "C8_03_alan", "C8_04_miranda"]] },
    11: { spawn: "direccion", obj: { txt: "Llega al autobús", zona: "Autobus" },
      seq: [["v", "C09"], ["d", "C9_01_canepa", "C9_02_tony", "C9_03_canepa", "C9_04_alan", "C9_05_miranda"], ["e", "defensa"], ["w", "defensa"]] },
    12: { auto: true, seq: [["d", "C10_01_canepa", "C10_02_alan"], ["v", "C10"], ["e", "victoria"]] },
  };
  // Diálogos durante el gameplay [G]: suenan sin detener el juego.
  H.CHARLAS = [
    { id: "J1", paso: 5, zona: "Pasillo1", lineas: ["J1_01_alan", "J1_02_miranda"] },
    { id: "J2", paso: 7, salir: "CIC", lineas: ["J2_01_tony"] },
  ];

  // ------------------------------------------------------------------ utilidades
  H.now = () => Date.now() / 1000;
  const VS = (o, n) => o.getVariables().get(n);
  const num = (o, n) => VS(o, n).getAsNumber();
  const str = (o, n) => VS(o, n).getAsString();
  const SV = (scn, n) => scn.getVariables().get(n);
  const GV = (scn, n) => scn.getGame().getVariables().get(n);
  const HV = (scn, k) => GV(scn, "Historia").getChild(k);
  const objs = (scn, n) => { try { return scn.getObjects(n) || []; } catch (e) { return []; } };
  const rol = (scn) => { try { return GV(scn, "NetRol").getAsNumber(); } catch (e) { return 0; } };
  const vivo = (o) => o && o._livingOnScene !== false;
  const dentro = (r, x, y) => x >= r[0] && x < r[2] && y >= r[1] && y < r[3];
  // fase 72: líneas de la versión final de la historia que aún no están en 01_DIALOGOS_PARA_VOCES.md (sin voz: el globo dura
  // según el largo del texto). C8_03_alan es un texto provisional; C8_04_miranda usa la voz de C8_03_miranda (misma frase).
  H.EXTRA = {
    C5_01_tony: { de: "C5_01_cesar", pj: "tony", sinVoz: true },
    C8_03_alan: { pj: "alan", txt: "¡Y un AK-47! Este me lo quedo yo." },
    C8_04_miranda: { de: "C8_03_miranda" },
    G_balas_alan: { pj: "alan", txt: "¡Encontré balas!" },        // fase 76: defensa del autobús, cada 24 s
  };
  const datos = () => {
    const D = gdjs.fdizHistoriaDatos || { lineas: {}, videos: {} };
    if (!D._extra) {
      D._extra = true;
      for (const [id, e] of Object.entries(H.EXTRA)) {
        if (D.lineas[id]) continue;
        const b = e.de && D.lineas[e.de] ? D.lineas[e.de] : { pj: e.pj, txt: e.txt || "", audio: "", dur: 0 };
        D.lineas[id] = { pj: e.pj || b.pj, txt: e.txt || b.txt, audio: e.sinVoz ? "" : b.audio, dur: e.sinVoz ? 0 : b.dur };
      }
    }
    return D;
  };
  const ZN = ["ZNormal", "ZCorredor", "ZGriton", "ZGordo", "ZConserje", "ZJoel", "ZJustino", "ZCanepa"];
  H.activo = (scn) => { try { return GV(scn, "Modo").getAsString() === "historia"; } catch (e) { return false; } };
  const S = (scn) => scn._fdizHist || (scn._fdizHist = {
    ini: false, remap: false, paso: 0, run: null, lin: null, gq: [], charlas: {}, kb: {}, local: { voz: -1, cine: "", n: 0 },
    cong: null, hechos: {}, olas: {}, listo: 0,
  });
  H.equipo = (scn) => objs(scn, "Sup").filter((s) => { const j = num(s, "Jugador"); return j >= 1 && j <= 4; });
  const pj = (s) => { const p = str(s, "Personaje"); return p === "tonyfuerte" ? "tony" : p; };
  function banner(scn, txt, seg) {
    SV(scn, "Banner").setString(txt); SV(scn, "BannerSeg").setNumber(seg || 2.5);
    try { gdjs.evtTools.runtimeScene.resetTimer(scn, "banner"); } catch (e) { /* sin temporizador */ }
  }
  function sonido(scn, archivo, vol) {
    try { if (GV(scn, "SonidoActivo").getAsNumber() === 1) gdjs.evtTools.sound.playSound(scn, archivo, false, vol || 70, 1); } catch (e) { /* sin sonido */ }
  }
  function zombi(scn, tipo, x, y, estado) {
    const z = scn.createObject(tipo); if (!z) return null;
    z.setLayer("Juego"); z.setPosition(x, y); z.setZOrder(Math.round(y)); VS(z, "Estado").setString(estado || "persigue");
    return z;
  }
  const zombis = (scn) => { const out = []; for (const n of ZN) for (const z of objs(scn, n)) out.push(z); return out; };
  const muerto = (z) => !vivo(z) || str(z, "Estado") === "muerto";
  function puerta(scn, id) { return objs(scn, "Puerta").find((p) => str(p, "Id") === id) || null; }
  function quitarPuerta(scn, id) {   // como si la tumbaran: el evento de puertas descubre sus zonas y la borra
    const p = puerta(scn, id); if (!p) return;
    VS(p, "Vida").setNumber(0); VS(p, "TiempoAbrir").setNumber(0.001); VS(p, "Progreso").setNumber(1); VS(p, "Bloqueo").setString("");
  }
  const vistas = (scn) => HV(scn, "CinematicasVistas").getAsString();
  const vista = (scn, v) => ("," + vistas(scn) + ",").includes("," + v + ",");
  function marcarVista(scn, v) { const a = vistas(scn); if (!vista(scn, v)) HV(scn, "CinematicasVistas").setString(a ? a + "," + v : v); }
  const armas = (scn) => HV(scn, "Armas").getAsString().split(",").filter(Boolean);
  function anotarArma(scn, t) { const a = armas(scn); a.push(t); HV(scn, "Armas").setString(a.join(",")); }

  // ------------------------------------------------------------------ solo Tony (fase 69)
  // En Historia solo se juega como Tony: el jugador 1 es Tony (con su control) y Miranda, Alan y César lo acompañan
  // como bots (NPC). Primer cuadro, antes de "Inicio de supervivientes"; aunque el menú o una partida anterior hayan
  // dejado otra cosa en P1Pj..P4Pj, aquí se corrige (también esas globales, para el HUD).
  H.ACOMPANAN = ["miranda", "alan", "cesar"];
  H.remap = function (scn) {
    const eq = H.equipo(scn).sort((a, b) => num(a, "Jugador") - num(b, "Jugador"));
    eq.forEach((s, k) => {
      const p = k === 0 ? "tony" : H.ACOMPANAN[(k - 1) % 3];
      if (str(s, "Personaje") !== p) { VS(s, "Personaje").setString(p); VS(s, "Init").setNumber(0); }
      if (k > 0 && num(s, "Control") !== -1) VS(s, "Control").setNumber(-1);
      try { GV(scn, "P" + num(s, "Jugador") + "Pj").setString(p); if (k > 0) GV(scn, "P" + num(s, "Jugador") + "Ctl").setNumber(-1); } catch (e) { /* sin global */ }
    });
  };

  // ------------------------------------------------------------------ bloquear / devolver el control (host)
  // Fase 69: durante videos y diálogos el mundo SIGUE (no se toca TimeScale ni Estado): zombis, bots, daño, tiempos y
  // derrota funcionan como siempre. Solo los jugadores humanos quedan sin control (Control -2) mientras dura la escena
  // guionizada, y la pausa no se abre (HistBloq = 1). Al terminar se devuelve el control cuando se suelta la tecla con la
  // que se avanzó, para que ese botón no active otra interacción (A también es "usar").
  function congelar(scn, st) {
    if (st.cong) { st.cong.soltar = false; return; }
    st.cong = { ctl: new Map(), soltar: false };
    SV(scn, "HistBloq").setNumber(1);
    for (const s of objs(scn, "Sup")) {
      const c = num(s, "Control");
      if (c >= 0 || c === -3) { st.cong.ctl.set(s, c); VS(s, "Control").setNumber(-2); }
      if (c >= 0 || c === -3) for (const n of ["MovX", "MovY", "QuierePegar", "Usando", "PideHab", "PideEsp", "QuiereLanzar"]) VS(s, n).setNumber(0);
    }
  }
  function devolver(scn, st, ya) {
    if (!st.cong) return;
    if (!ya) { st.cong.soltar = true; return; }                  // se devuelve en host() cuando ya no se mantiene la tecla
    const C = st.cong; st.cong = null;
    for (const [s, c] of C.ctl) { try { if (vivo(s) && num(s, "Control") === -2) VS(s, "Control").setNumber(c); } catch (e) { /* ya no está */ } }
    SV(scn, "HistBloq").setNumber(0);
  }

  // ------------------------------------------------------------------ armas
  const DE_FUEGO = { pistolita: 9, pistola: 4, escopeta: 6, ak47: 30 };
  const deFuego = (s) => DE_FUEGO[str(s, "Arma")] !== undefined;
  // a quién le toca: el preferido si no trae arma de fuego, luego un humano sin arma de fuego, luego cualquiera
  function darArma(scn, tipo, pref, paraTony) {
    const eq = H.equipo(scn).filter((s) => str(s, "Estado") !== "fuera");
    if (paraTony) {                                             // Tony la toma; si traía otra arma de fuego, se la pasa a un compañero
      const t = eq.find((o) => pj(o) === "tony");
      if (t) {
        const prev = str(t, "Arma"), usos = num(t, "Usos");
        if (DE_FUEGO[prev] !== undefined && prev !== tipo && usos > 0) {
          const c = eq.find((o) => o !== t && !deFuego(o));
          if (c) { VS(c, "Arma").setString(prev); VS(c, "Usos").setNumber(usos); }
        }
        VS(t, "Arma").setString(tipo); VS(t, "Usos").setNumber(DE_FUEGO[tipo]);
        return t;
      }
    }
    const cg = S(scn).cong;                                    // congelado: el control real está guardado
    const humano = (s) => { const c = cg && cg.ctl.has(s) ? cg.ctl.get(s) : num(s, "Control"); return c >= 0 || c === -3; };
    let s = null;
    for (const p of pref || []) { s = eq.find((o) => (p === "P1" ? num(o, "Jugador") === 1 : pj(o) === p) && !deFuego(o)); if (s) break; }
    s = s || eq.find((o) => humano(o) && !deFuego(o)) || eq.find((o) => !deFuego(o));
    s = s || eq.slice().sort((a, b) => num(a, "Usos") - num(b, "Usos"))[0];
    if (!s) return null;
    VS(s, "Arma").setString(tipo); VS(s, "Usos").setNumber(DE_FUEGO[tipo]);
    return s;
  }
  // ------------------------------------------------------------------ fase 72: personaje controlado y armas de cada quien
  // (02_HISTORIA_PARA_GDEVELOP.md, 3.4 y 3.5). El jugador controla UN alumno; los otros tres son bots. Cambiar = pasar el
  // control (Control y P<j>Ctl) del controlado al nuevo; el anterior queda como bot (-1). Cada alumno lleva una sola arma.
  H.CONTROL_INICIO = { 1: "alan", 2: "alan", 3: "alan", 4: "alan", 5: "tony", 6: "tony", 7: "tony", 8: "tony", 9: "cesar", 10: "miranda", 11: "alan", 12: "alan" };
  H.DUENO = (t, n) => ({ pistolita: "tony", pistola: "cesar", ak47: "alan", escopeta: n >= 10 ? "miranda" : "cesar" })[t];
  const humanoCtl = (st, s) => { const c = st.cong && st.cong.ctl.has(s) ? st.cong.ctl.get(s) : num(s, "Control"); return c >= 0 || c === -3 ? c : null; };
  H.controlado = (scn) => { const st = S(scn); return H.equipo(scn).find((s) => humanoCtl(st, s) !== null) || null; };
  H.controlar = function (scn, st, p, callado) {
    const eq = H.equipo(scn), nuevo = eq.find((s) => pj(s) === p); if (!nuevo) return;
    HV(scn, "Controlado").setString(p);
    const viejo = eq.find((s) => humanoCtl(st, s) !== null);
    if (!viejo || viejo === nuevo) return;
    const c = humanoCtl(st, viejo);
    if (st.cong) { st.cong.ctl.delete(viejo); st.cong.ctl.set(nuevo, c); VS(nuevo, "Control").setNumber(-2); }
    else VS(nuevo, "Control").setNumber(c);
    VS(viejo, "Control").setNumber(-1);
    for (const n of ["MovX", "MovY", "QuierePegar", "Usando", "PideHab", "PideEsp", "QuiereLanzar"]) { VS(viejo, n).setNumber(0); VS(nuevo, n).setNumber(0); }
    VS(viejo, "BotX").setNumber(viejo.getX()); VS(viejo, "BotY").setNumber(viejo.getY());
    try { GV(scn, "P" + num(viejo, "Jugador") + "Ctl").setNumber(-1); GV(scn, "P" + num(nuevo, "Jugador") + "Ctl").setNumber(c); } catch (e) { /* sin global */ }
    // fase 73: aviso pequeño (la línea de ayuda de abajo), no el letrero grande
    if (!callado) { st.avisoCambio = { txt: "Cambio de personaje: ahora controlas a " + (H.NOMBRES[p] || p), hasta: H.now() + 3 }; sonido(scn, "efectos/eventos/rescate_logrado.ogg", 40); }
  };
  function armar(scn, tipo, p) {
    const s = H.equipo(scn).find((o) => pj(o) === p); if (!s) return null;
    VS(s, "Arma").setString(tipo); VS(s, "Usos").setNumber(tipo === "puños" ? 0 : DE_FUEGO[tipo]);
    return s;
  }
  const PREF = { pistolita: ["P1"], escopeta: ["tony"], pistola: ["cesar", "miranda", "alan", "tony"] };
  const PARA_TONY = { escopeta: true, pistola: true };   // C65_03: Tony carga la escopeta; fase 71: la sheriff la recoge Tony
  H.SHERIFF = { x: 3350, y: 4510 };          // fase 71: la sheriff queda en el piso de la dirección, junto a la puerta (P47): Tony la recoge al pasar
  function ponerSheriff(scn, st) {
    if (st.sheriff && vivo(st.sheriff)) return;
    const a = scn.createObject("ArmaPiso"); if (!a) return;
    a.setLayer("Juego"); a.setPosition(H.SHERIFF.x, H.SHERIFF.y); a.setZOrder(H.SHERIFF.y);
    VS(a, "Tipo").setString("pistola"); VS(a, "Solo").setNumber(1); try { a.setAnimationName("pistola"); } catch (e) { /* sin animación */ }
    st.sheriff = a;
  }
  // el evento "Armas del salón" solo recoge con los puños: aquí Tony la toma aunque traiga otra arma (la anterior pasa a un compañero)
  function recogerSheriff(scn, st) {
    const a = st.sheriff; if (!a) return;
    if (!vivo(a)) { st.sheriff = null; if (!armas(scn).includes("pistola")) anotarArma(scn, "pistola"); return; }
    const t = H.equipo(scn).find((o) => pj(o) === "tony" && str(o, "Estado") === "normal"); if (!t) return;
    const b = a.getAABB(), x = t.getX(), y = t.getY();
    if (x + 20 < b.min[0] || x - 20 > b.max[0] || y < b.min[1] || y - 16 > b.max[1]) return;
    darArma(scn, "pistola", PREF.pistola, true); anotarArma(scn, "pistola");
    a.deleteFromScene(scn); st.sheriff = null;
    banner(scn, "¡TONY TIENE LA SHERIFF!", 2.5);
  }
  // pistola del profe en el piso (ArmaPiso "pistolita", Solo = 1: solo el jugador 1 la recoge, como en la fase 67)
  function ponerPistola(scn, x, y) {
    if (objs(scn, "ArmaPiso").some((a) => str(a, "Tipo") === "pistolita")) return;
    const a = scn.createObject("ArmaPiso"); if (!a) return;
    a.setLayer("Juego"); a.setPosition(x, y); a.setZOrder(y);
    VS(a, "Tipo").setString("pistolita"); VS(a, "Solo").setNumber(1); a.setAnimationName("pistolita");
  }
  // cuando el jugador 1 la recoge (evento "Armas del salón"), queda anotada para los checkpoints
  function pistola(scn, st) {
    if (armas(scn).includes("pistolita")) return;
    const p1 = H.equipo(scn).find((s) => num(s, "Jugador") === 1);
    if (p1 && str(p1, "Arma") === "pistolita") anotarArma(scn, "pistolita");
  }
  // ¿este jugador puede usar este Objetivo de la historia? (usar.js lo pregunta para el indicador y para avanzar)
  H.puedeUsar = function (scn, s, g) {
    if (!H.activo(scn)) return true;
    const t = str(g, "Tipo"); if (!/^h_/.test(t)) return true;
    const U = Object.values(H.USAR).find((u) => u.tipo === t); if (!U) return true;
    if (U.sala && !dentro(U.sala, s.getX(), s.getY())) return false;
    if (num(s, "Control") === -1 && H.equipo(scn).some(esJugador)) return false;   // lo usa el jugador, no los bots
    if (U.puerta && puerta(scn, U.puerta)) return false;
    return true;
  };
  const NOMBRE_ARMA = { pistolita: "la pistola del profe", escopeta: "la escopeta", pistola: "la otra pistola" };

  // ------------------------------------------------------------------ Joel (seguidor) y profes
  function supJoel(scn) { return objs(scn, "Sup").find((s) => pj(s) === "joel") || null; }
  function npc(scn, k) { return objs(scn, "Profe").find((p) => str(p, "Nombre") === k) || null; }
  function unirJoel(scn, x, y) {
    if (supJoel(scn)) return supJoel(scn);
    const P = gdjs.fdizProfes;
    try { SV(scn, "ProfJoel").setString("espera"); } catch (e) { /* sin profes */ }
    if (P && P.unir) P.unir(scn, "joel");
    const s = supJoel(scn);
    if (s && x !== undefined) { s.setPosition(x, y); VS(s, "BotX").setNumber(x); VS(s, "BotY").setNumber(y); }
    return s;
  }
  function joelSeQueda(scn) {
    const s = supJoel(scn); if (s) s.deleteFromScene(scn);
    const vieja = npc(scn, "joel"); if (vieja) vieja.deleteFromScene(scn);
    const p = scn.createObject("Profe");
    if (p) {
      const [x, y] = H.LUGAR.joelQueda;
      p.setLayer("Juego"); p.setPosition(x, y); p.setZOrder(y);
      VS(p, "Nombre").setString("joel"); VS(p, "Estado").setString("espera");
      try { p.setAnimationName("joel_quieto"); } catch (e) { /* sin animación */ }
    }
    try { SV(scn, "ProfJoel").setString("espera"); SV(scn, "ProfJoelSeg").setNumber(0); } catch (e) { /* sin profes */ }
  }
  // En Historia los profes no se reclutan con F ni piden ayuda: Joel se une por la historia y Justino y Canepa se quedan.
  H.reservado = (scn) => H.activo(scn);
  H.sinMordida = (scn) => H.activo(scn);

  // ------------------------------------------------------------------ reja trasera (estacionamiento)
  function ponerReja(scn, st) {
    if (st.reja) return;
    const R = H.REJA, c = scn.createObject("ChoqueMueble");
    st.reja = { choque: c, vis: [] };
    if (c) { c.setLayer("Juego"); c.setPosition(R.x, R.y); c.setWidth(R.w); c.setHeight(R.h); c.hide(true); }
    for (let i = 0; i < 4; i++) {            // la reja blanca de las vallas, girada (4 tramos de 128 px)
      const m = scn.createObject("Mueble"); if (!m) continue;
      m.setLayer("Juego"); m.setAnimationName("hitos/reja_blanca"); m.setAngle(90);
      const cy = R.y + 60 + i * 120;
      m.setPosition(R.x + R.w / 2, cy + 57); m.setZOrder(cy + 40);
      st.reja.vis.push(m);
    }
  }
  function quitarReja(scn, st) {
    if (!st.reja) return;
    for (const o of [st.reja.choque].concat(st.reja.vis)) if (vivo(o)) o.deleteFromScene(scn);
    st.reja = null;
  }

  // ------------------------------------------------------------------ objetivos y zonas
  function objetivo(scn, st, o) {
    st.obj = o || null;
    for (const g of objs(scn, "Objetivo").slice()) if (/^h_/.test(str(g, "Tipo"))) g.deleteFromScene(scn);
    st.usarObj = null;
    if (o && o.usar) {
      const U = H.USAR[o.usar], g = scn.createObject("Objetivo");
      if (g) {
        g.setLayer("Juego"); g.setPosition(U.x, U.y); g.setZOrder(U.y);
        VS(g, "Tipo").setString(U.tipo); VS(g, "Tiempo").setNumber(1); VS(g, "Hecho").setNumber(0); VS(g, "Progreso").setNumber(0);
        try { g.setAnimationName(U.anim); } catch (e) { /* sin animación */ }
        if (!U.ver) { g.setScale(0.2); g.hide(true); }
        st.usarObj = g;
      }
    }
    if (o) { sonido(scn, "efectos/eventos/objetivo_nuevo.ogg", 65); banner(scn, o.txt.toUpperCase(), 3); }
  }
  function centro(z) { const r = H.ZONAS[z]; return [(r[0] + r[2]) / 2, (r[1] + r[3]) / 2]; }
  const enZona = (scn, z, quien) => (quien || H.equipo(scn)).some((s) => str(s, "Estado") === "normal" && dentro(H.ZONAS[z], s.getX(), s.getY()));
  // fase 69: los disparadores los activa el jugador (Tony); los compañeros bot solo lo siguen. Sin humanos (demo), cualquiera.
  const esJugador = (s) => { const c = num(s, "Control"); return c >= 0 || c === -2 || c === -3; };
  H.jugadores = (scn) => { const eq = H.equipo(scn), h = eq.filter(esJugador); return h.length ? h : eq; };
  function textoObjetivo(scn, st) {
    let t = "", x = -1, y = -1;
    const o = st.obj;
    if (o && !st.run) {
      t = o.txt;
      if (o.usar) {                                  // la flecha va a lo que se usa; con zona (dirección) cambia el texto adentro
        const U = H.USAR[o.usar]; x = U.x; y = U.y;
        if (o.zona && o.txt2 && enZona(scn, o.zona)) t = o.txt2;
      } else if (o.zona) [x, y] = centro(o.zona);
      // fase 76: paso 5, ya en el CIC: la misión es abrir la sala de la derecha (Joel); la flecha va a su puerta
      if (o.puerta && o.txt2) {
        if (!st.hechos.cic && enZona(scn, o.zona, H.jugadores(scn))) {
          st.hechos.cic = true; banner(scn, o.txt2.toUpperCase(), 3); sonido(scn, "efectos/eventos/objetivo_nuevo.ogg", 65);
        }
        if (st.hechos.cic) { t = o.txt2; [x, y] = o.flecha; }
      }
    }
    if (st.defensa && st.paso === 11) {
      if (SV(scn, "FinalActivo").getAsNumber() === 1) {
        const r = Math.max(0, Math.ceil(H.FINAL_SEG - tiempoFinal(scn)));
        t = "Protege a Canepa: " + Math.floor(r / 60) + ":" + String(r % 60).padStart(2, "0");
      } else if (!st.cong) { t = "Llega al autobús"; x = 400; y = 3264; }
    }
    SV(scn, "HistObjX").setNumber(x); SV(scn, "HistObjY").setNumber(y);
    const T = objs(scn, "TxtObjetivo")[0];
    const s = t ? "Objetivo" + "\n" + t : "";
    if (T && T.getString() !== s) T.setString(s);
  }
  const tiempoFinal = (scn) => { try { return gdjs.evtTools.runtimeScene.getTimerElapsedTimeInSeconds(scn, "final"); } catch (e) { return 0; } };

  // ------------------------------------------------------------------ checkpoints: el mundo al inicio de cada paso
  function restaurar(scn, st, n) {
    const L = H.LUGAR;
    // armas que ya tenían (con el cargador lleno)
    // fase 72: cada arma con su dueño del documento (cargador lleno) y el personaje controlado al inicio del paso
    for (const t of armas(scn)) armar(scn, t, H.DUENO(t, n));
    H.controlar(scn, st, H.CONTROL_INICIO[n] || "alan", true);
    if (n >= 4 && n <= 6) SV(scn, "HistAlarma").setNumber(1);
    if (n === 7 || n === 8) SV(scn, "Apagon").setNumber(1);
    if (n >= 5) quitarPuerta(scn, L.puertaSalon);
    if (n >= 8) quitarPuerta(scn, L.puertaConserje);
    if (n >= 11) { quitarPuerta(scn, L.puertaDireccion); st.llave = true; SV(scn, "ExtraZombies").setNumber(8); }
    if (n >= 9) joelSeQueda(scn);
    if (n >= 11) conserje(scn, st);
  }
  function colocar(scn, st, lugar) {
    const P = H.SPAWN[lugar]; if (!P) return;
    const [x, y, dx] = P;
    for (const s of H.equipo(scn)) {
      const j = num(s, "Jugador");
      s.setPosition(x + (j - 2.5) * dx, y);
      VS(s, "BotX").setNumber(s.getX()); VS(s, "BotY").setNumber(s.getY());
    }
    try {
      SV(scn, "CamX").setNumber(x); SV(scn, "CamY").setNumber(y - 48);
      const capas = []; scn.getAllLayerNames(capas);           // todas las del mundo (la cámara de los eventos es la de la capa base)
      for (const n of capas) if (n !== "HUD") { const L = scn.getLayer(n); L.setCameraX(x); L.setCameraY(y - 48); }
    } catch (e) { /* sin capa */ }
    for (const z of zombis(scn)) if (!muerto(z) && Math.hypot(z.getX() - x, z.getY() - y) < 700) z.deleteFromScene(scn);  // llegada justa
  }
  function revivirFuera(scn) {   // como el evento de "objetivo cumplido": los que quedaron fuera vuelven con media vida
    let cx = 0, cy = 0; try { cx = SV(scn, "CamX").getAsNumber(); cy = SV(scn, "CamY").getAsNumber(); } catch (e) { /* sin cámara */ }
    for (const s of H.equipo(scn)) if (str(s, "Estado") === "fuera") {
      VS(s, "Estado").setString("normal"); VS(s, "Vida").setNumber(num(s, "VidaMax") * 0.5);
      s.hide(false); try { s.activateBehavior("TopDownMovement", true); } catch (e) { /* sin comportamiento */ }
      s.setPosition(cx, cy + 48); try { s.setAnimationName(pj(s) + "_quieto"); } catch (e) { /* sin animación */ }
    }
  }
  function guardar(scn, n) {
    if (n > 11) return;
    HV(scn, "Paso").setNumber(n);
  }

  // ------------------------------------------------------------------ preparar la partida (host, una vez)
  function preparar(scn, st) {
    st.ini = true;
    SV(scn, "PistolaPuesta").setNumber(1);                       // la pistola inicial llega por la historia (paso 3)
    for (const a of objs(scn, "ArmaPiso").slice()) {
      const t = str(a, "Tipo");
      if (t === "pistolita" || H.LUGAR.armasFuera.some(([k, x, y]) => k === t && Math.hypot(a.getX() - x, a.getY() - y) < 40)) a.deleteFromScene(scn);
    }
    for (const z of objs(scn, "ZConserje").slice()) z.deleteFromScene(scn);   // el jefe aparece en el paso 10
    const lk = st.locker || scn.createObject("Mueble"); st.locker = lk;                       // casillero del conserje (se ve; se usa con el Objetivo)
    if (lk) { lk.setLayer("Juego"); lk.setAnimationName("cic/lockers_cerrados"); lk.setPosition(H.LUGAR.locker[0], H.LUGAR.locker[1]); lk.setZOrder(H.LUGAR.locker[1]); }
    // puerta del salón cerrada hasta que entra el zombi (paso 4)
    let n = HV(scn, "Paso").getAsNumber();
    if (!(n >= 1 && n <= 11)) { n = 1; HV(scn, "CinematicasVistas").setString(""); HV(scn, "Armas").setString(""); }
    HV(scn, "Final").setNumber(0);
    st.paso = n;
    if (n <= 10) ponerReja(scn, st);
    restaurar(scn, st, n);
    colocar(scn, st, H.PASOS[n].spawn);
    if (n >= 6 && n <= 8) { const [x, y] = H.SPAWN[H.PASOS[n].spawn]; unirJoel(scn, x, y + 60); }
    empezarPaso(scn, st, n);
    if (!st.run) { SV(scn, "HistVelo").setNumber(0); devolver(scn, st, true); }   // checkpoint sin escena: a jugar
  }
  function empezarPaso(scn, st, n) {
    st.paso = n; st.hechos = {};
    const P = H.PASOS[n];
    guardar(scn, n);
    if (n > 1) revivirFuera(scn);
    objetivo(scn, st, P.obj || null);
    if (P.auto) correr(scn, st, P.seq);
  }
  function correr(scn, st, seq) {
    st.run = { seq, i: 0, it: null };
    objetivo(scn, st, null);
  }
  function siguientePaso(scn, st) {
    st.run = null;
    devolver(scn, st);
    if (st.paso < 12) empezarPaso(scn, st, st.paso + 1);
  }

  // ------------------------------------------------------------------ eventos de la historia (host)
  function conserje(scn, st) {
    if (objs(scn, "ZConserje").some((z) => !muerto(z)) || st.conserjeMuerto) return;
    const [x, y] = H.LUGAR.conserje;
    st.conserje = zombi(scn, "ZConserje", x, y, "persigue");
  }
  H.EVENTOS = {
    alarma(scn) { SV(scn, "HistAlarma").setNumber(1); },
    pistola(scn) {                                              // fase 72: Tony toma la pistola del profe (C03)
      armar(scn, "pistolita", "tony"); if (!armas(scn).includes("pistolita")) anotarArma(scn, "pistolita");
      for (const a of objs(scn, "ArmaPiso").slice()) if (str(a, "Tipo") === "pistolita") a.deleteFromScene(scn);
    },
    controla(scn, st, p) { H.controlar(scn, st, p); },
    pasaEscopeta(scn) {                                         // fase 72: César le pasa la escopeta a Miranda (C07)
      armar(scn, "puños", "cesar"); armar(scn, "escopeta", "miranda");
      banner(scn, "César le pasa la escopeta a Miranda", 2.5);
    },
    irrumpe(scn, st) {
      for (const z of zombis(scn)) if (!muerto(z) && Math.hypot(z.getX() - 5984, z.getY() - 3024) < 1100) z.deleteFromScene(scn);
      quitarPuerta(scn, H.LUGAR.puertaSalon);
      st.intruso = zombi(scn, "ZNormal", H.LUGAR.intruso[0], H.LUGAR.intruso[1], "persigue");
      st.tutorial = H.now() + 30;
      banner(scn, "¡ROMPIÓ LA PUERTA!", 2);
      sonido(scn, "evento_impacto_cinematico.ogg", 90);
    },
    joel(scn, st) {
      const n = npc(scn, "joel"), x = n ? n.getX() : 3216, y = n ? n.getY() : 1960;
      unirJoel(scn, x, y);
    },
    apagon(scn) { SV(scn, "Apagon").setNumber(1); SV(scn, "HistAlarma").setNumber(0); banner(scn, "¡SE FUE LA LUZ!", 2.5); },
    zombisPasillo(scn) { for (const [x, y] of H.LUGAR.pasilloCIC) zombi(scn, "ZNormal", x, y, "persigue"); },
    intendencia(scn, st) {
      quitarPuerta(scn, H.LUGAR.puertaConserje);
      st.intendencia = zombi(scn, "ZGordo", H.LUGAR.intendencia[0], H.LUGAR.intendencia[1], "persigue");
    },
    escopeta(scn) {
      const s = armar(scn, "escopeta", "cesar"); anotarArma(scn, "escopeta");   // fase 72: la escopeta es de César
      SV(scn, "Apagon").setNumber(0);
      banner(scn, "¡" + (s ? H.NOMBRES[pj(s)] || "" : "").toUpperCase() + " TIENE LA ESCOPETA! Volvió la luz", 3);
      sonido(scn, "efectos/mundo/interruptor.ogg", 60);
    },
    joelSeQueda(scn) { joelSeQueda(scn); },
    justino(scn) {
      for (const s of H.equipo(scn)) if (str(s, "Estado") === "normal") VS(s, "Vida").setNumber(num(s, "VidaMax"));
      banner(scn, "La nevería: el equipo recupera toda la vida", 3);
      sonido(scn, "curar_powerup.ogg", 70);
    },
    llave(scn, st) {
      st.llave = true; quitarReja(scn, st);
      armar(scn, "pistola", "cesar"); armar(scn, "ak47", "alan");  // fase 72: pistola del director -> César, AK-47 -> Alan
      anotarArma(scn, "pistola"); anotarArma(scn, "ak47");
      SV(scn, "ExtraZombies").setNumber(8);
      conserje(scn, st);
      banner(scn, "¡LLAVE DE LA REJA, PISTOLA PARA CÉSAR Y AK-47 PARA ALAN! El conserje los persigue", 3.5);
      sonido(scn, "evento_impacto_cinematico.ogg", 90);
    },
    defensa(scn, st) {
      st.defensa = true; st.olas = {};
      SV(scn, "HistDefensa").setNumber(1);                         // el evento FDIZ-FASE68-OBJ deja correr el final de siempre
      SV(scn, "FinalSeg").setNumber(H.FINAL_SEG);
      SV(scn, "ObjTotal").setNumber(0); SV(scn, "ObjNum").setNumber(1); SV(scn, "ObjIni").setNumber(0);  // el final de siempre
      conserje(scn, st);
    },
    victoria(scn, st) {
      devolver(scn, st, true);
      SV(scn, "Estado").setString("victoria");
      try { gdjs.evtTools.runtimeScene.resetTimer(scn, "fin"); } catch (e) { /* sin temporizador */ }
      GV(scn, "Resultado").setString("victoria");
      try { GV(scn, "TiempoFinal").setNumber(SV(scn, "Tiempo").getAsNumber()); } catch (e) { /* sin tiempo */ }
      banner(scn, "¡ESCAPARON!", 4);
      sonido(scn, "efectos/eventos/escape.ogg", 75);
      HV(scn, "Final").setNumber(1);                               // Resultados: C10_03 sobre la pantalla de victoria
      HV(scn, "Paso").setNumber(0); HV(scn, "CinematicasVistas").setString(""); HV(scn, "Armas").setString("");
    },
  };
  H.ESPERAS = {
    intruso: (scn, st, t) => !st.intruso || muerto(st.intruso) || t > 40,
    intendencia: (scn, st, t) => !st.intendencia || muerto(st.intendencia) || t > 60,
    defensa: (scn, st) => {
      if (SV(scn, "FinalActivo").getAsNumber() !== 1) return false;
      const t = tiempoFinal(scn);
      for (const [k, n] of [[30, 4], [60, 6]]) if (t >= k && !st.olas[k]) {       // oleadas crecientes
        st.olas[k] = true;
        for (let i = 0; i < n; i++) { const p = H.LUGAR.olas[(i + k) % H.LUGAR.olas.length]; zombi(scn, i % 3 === 2 ? "ZGordo" : "ZCorredor", p[0], p[1], "persigue"); }
        banner(scn, k === 30 ? "¡VIENEN MÁS!" : "¡LA ÚLTIMA OLEADA!", 2);
      }
      return t >= H.FINAL_SEG && SV(scn, "Estado").getAsString() === "juego";
    },
  };

  // ------------------------------------------------------------------ entrada (host)
  function entrada(scn, st) {
    const I = gdjs.evtTools && gdjs.evtTools.input;
    let esp = false, ent = false, pad = false;
    try { esp = I.isKeyPressed(scn, "Space"); ent = I.isKeyPressed(scn, "Return"); } catch (e) { /* sin teclado */ }
    try { for (const g of (typeof navigator !== "undefined" && navigator.getGamepads ? navigator.getGamepads() : []) || []) if (g && g.buttons && g.buttons[0] && g.buttons[0].pressed) pad = true; } catch (e) { /* sin mandos */ }
    const k = st.kb;
    const r = { esp: esp && !k.esp, todo: (esp && !k.esp) || (ent && !k.ent) || (pad && !k.pad), mantiene: esp || ent || pad };
    k.esp = esp; k.ent = ent; k.pad = pad;
    return r;
  }

  // ------------------------------------------------------------------ líneas de diálogo (host)
  function hablanteDe(scn, p) {
    if (p === "altavoz") return "";
    for (const s of objs(scn, "Sup")) if (pj(s) === p && str(s, "Estado") !== "fuera" && !s.isHidden()) return "sup:" + num(s, "Jugador");
    const n = npc(scn, p); return n ? "npc:" + p : "";
  }
  H.deId = function (scn, id) {
    if (!id) return null;
    if (id.startsWith("npc:")) return npc(scn, id.slice(4));
    const j = Number(id.slice(4));
    return objs(scn, "Sup").find((s) => num(s, "Jugador") === j) || null;
  };
  // fase 73: en el inicio (pasos 1 a 3), quien dice su línea da unos pasos cortos (18 px en 0.5 s) si no se está moviendo
  H.PASITO = { px: 18, seg: 0.5 };
  function pasito(scn, st, id) {
    if (st.paso > 3) return;
    const L = datos().lineas[id]; if (!L) return;
    const s = H.equipo(scn).find((o) => pj(o) === L.pj && str(o, "Estado") === "normal"); if (!s) return;
    const mueve = (o) => num(o, "Control") !== -1 && (num(o, "MovX") !== 0 || num(o, "MovY") !== 0);   // el jugador ya se está moviendo
    if (mueve(s)) return;
    s.__fdizMueve = mueve;
    const dir = s.__fdizDir = -(s.__fdizDir || (Math.random() < 0.5 ? 1 : -1));   // alterna: no se aleja del lugar
    if (!s.__fdizAnimP) {
      s.__fdizAnimP = s.setAnimationName.bind(s);
      s.setAnimationName = function (n) { if (this.__fdizPaseo && n !== this.__fdizPaseo.an) return; return this.__fdizAnimP(n); };
    }
    s.__fdizPaseo = { x0: s.getX(), dir, t0: H.now(), an: pj(s) + "_caminar_lado" };
    try { s.activateBehavior("PathBot", false); } catch (e) { /* sin ruta */ }    // la ruta de los bots lo regresaría cada cuadro
    st.paseos = st.paseos || new Set(); st.paseos.add(s);
  }
  function paseos(scn, st) {
    if (!st.paseos) return;
    for (const s of [...st.paseos]) {
      const P = s.__fdizPaseo;
      const f = P ? (H.now() - P.t0) / H.PASITO.seg : 2;
      if (!P || f >= 1 || !vivo(s) || str(s, "Estado") !== "normal" || s.__fdizMueve(s)) {
        s.__fdizPaseo = null; st.paseos.delete(s);
        try { s.activateBehavior("PathBot", true); } catch (e) { /* sin ruta */ }
        try { s.__fdizAnimP(pj(s) + "_quieto"); } catch (e) { /* sin animación */ }
        continue;
      }
      s.setX(P.x0 + P.dir * H.PASITO.px * f);
      try { s.__fdizAnimP(P.an); s.flipX(P.dir < 0); } catch (e) { /* sin animación */ }
    }
  }
  function decir(scn, st, id, bloq) {
    pasito(scn, st, id);
    const L = datos().lineas[id] || { pj: "", dur: 2.5 };
    const dur = L.dur > 0 ? L.dur : Math.max(2.2, Math.min(6, (L.txt || "").length * 0.06));
    st.lin = { id, t0: H.now(), fin: H.now() + dur + H.HUECO, bloq };
    SV(scn, "HistLinea").setString(id); SV(scn, "HistHabla").setString(hablanteDe(scn, L.pj));
    SV(scn, "HistLineaSeq").add(1);
  }
  function callar(scn, st) {
    st.lin = null;
    if (SV(scn, "HistLinea").getAsString() !== "") { SV(scn, "HistLinea").setString(""); SV(scn, "HistHabla").setString(""); SV(scn, "HistLineaSeq").add(1); }
  }
  // ¿terminó la línea? (audio + 0.3 s, o Espacio)
  function lineaLista(st, inp, bloq) {
    if (!st.lin) return true;
    const t = H.now();
    return t >= st.lin.fin || (t - st.lin.t0 > 0.25 && (bloq ? inp.todo : inp.esp));
  }

  // ------------------------------------------------------------------ cinemáticas (host)
  const objVideo = (v) => (datos().videos || {})[v] || "";
  H.hayVideo = (scn, v) => { const o = objVideo(v); if (!o) return false; try { return !!scn.getObjects(o); } catch (e) { return false; } };
  // fase 76: durante la cuenta del autobús, Alan recarga el AK-47 cada 24 s y lo dice (globo sin voz, no bloquea)
  H.BALAS_SEG = 24;
  function balasAlan(scn, st) {
    if (st.balasLin && H.now() > st.balasLin) { st.balasLin = 0; if (st.lin && st.lin.id === "G_balas_alan") callar(scn, st); }
    if (!(st.defensa && st.paso === 11 && SV(scn, "FinalActivo").getAsNumber() === 1)) { st.balasT = 0; return; }
    if (!st.balasT) { st.balasT = H.now(); return; }
    if (H.now() - st.balasT < H.BALAS_SEG) return;
    st.balasT = H.now();
    const a = H.equipo(scn).find((o) => pj(o) === "alan" && str(o, "Estado") !== "fuera"); if (!a) return;
    armar(scn, "ak47", "alan");
    if (!st.lin) { decir(scn, st, "G_balas_alan", false); st.balasLin = H.now() + 2.2; }
    sonido(scn, "efectos/eventos/objetivo_nuevo.ogg", 45);
  }
  // fase 75: fundido a negro antes y después de cada cinemática (segundos de cada mitad)
  H.FUNDIDO = 0.35;
  function salida(scn, st) {
    if (!st.salida) return;
    const f = (H.now() - st.salida) / H.FUNDIDO;
    if (f >= 1) { st.salida = 0; SV(scn, "HistVelo").setNumber(0); return; }
    SV(scn, "HistVelo").setNumber(Math.round(255 * (1 - f)));
  }
  // fase 73: durante la cinemática se congela todo el mundo (jugadores, bots y zombis): TimeScale 0 hasta que termina
  function helar(scn, st, si) {
    try {
      const T = scn.getTimeManager();
      if (si) { if (!st.helado) { st.helado = true; T.setTimeScale(0); } }
      else if (st.helado) { st.helado = false; if (SV(scn, "Pausa").getAsNumber() !== 1) T.setTimeScale(1); }
    } catch (e) { /* sin tiempo */ }
  }
  function empezarCine(scn, st, v) {
    helar(scn, st, true);
    const modo = H.hayVideo(scn, v) ? "v" : "n";
    st.cine = { v, modo, t0: H.now(), hold: 0, armado: false, tUlt: H.now() };
    marcarVista(scn, v);
    SV(scn, "HistCine").setString(modo + ":" + v); SV(scn, "HistCineSeq").add(1);
  }
  function terminarCine(scn, st) {
    helar(scn, st, false);
    st.cine = null; st.local.salto = 0;
    SV(scn, "HistCine").setString(""); SV(scn, "HistCineSeq").add(1);
  }
  function pasoCine(scn, st, inp) {
    const C = st.cine, t = H.now() - C.t0, dt = Math.min(0.1, H.now() - C.tUlt);
    C.tUlt = H.now();
    if (!inp.mantiene) C.armado = true;                          // la tecla que venía apretada no cuenta
    C.hold = C.armado && inp.mantiene ? C.hold + dt : 0;
    st.local.salto = Math.min(1, C.hold / H.SALTAR);
    if (C.hold >= H.SALTAR) return true;
    if (C.modo === "n") return t >= H.NEGRO;
    const v = st.local.vid;
    try {
      if (v && (v.isEnded() || (v.getDuration() > 0 && v.getCurrentTime() >= v.getDuration() - 0.05))) return true;
      if (t > H.FALLA && (!v || !(v.getDuration() > 0))) return true;
      if (v && v.getDuration() > 0 && t > v.getDuration() + 3) return true;
    } catch (e) { return t > H.FALLA; }
    return false;
  }

  // ------------------------------------------------------------------ secuencia (host)
  function pasoSeq(scn, st, inp) {
    const R = st.run;
    for (let guarda = 0; guarda < 8; guarda++) {
      const it = R.seq[R.i];
      if (!it) { siguientePaso(scn, st); return; }
      const tipo = it[0];
      if (!R.it) {                                              // empieza el elemento
        R.it = { t0: H.now(), k: 1 };
        if (tipo !== "fade" && !st.salida) SV(scn, "HistVelo").setNumber(0);   // fase 71: un checkpoint en un paso automático no se queda en negro
        if (tipo === "fade") { congelar(scn, st); SV(scn, "HistVelo").setNumber(255); }
        else if (tipo === "v") {
          if (vista(scn, it[1])) { R.i++; R.it = null; continue; }     // ya se vio en esta partida: no se repite
          // fase 75: primero se desvanece a negro (H.FUNDIDO s) y luego empieza el video
          congelar(scn, st); callar(scn, st); st.gq = []; helar(scn, st, true); st.salida = 0; R.it.entrada = true;
        } else if (tipo === "d") {
          // fase 71: en los diálogos del inicio (pasos 1 a 3, antes de la alerta) Tony se mueve libre dentro del salón
          if (H.DLG_LIBRE[st.paso]) devolver(scn, st, true); else congelar(scn, st);
          callar(scn, st); st.gq = [];
        }
        else if (tipo === "e") { try { H.EVENTOS[it[1]](scn, st, it[2]); } catch (e) { console.error("historia: evento " + it[1], e); } R.i++; R.it = null; continue; }
        else if (tipo === "w") devolver(scn, st);
      }
      const t = H.now() - R.it.t0;
      if (tipo === "fade") {
        const f = Math.max(0, 1 - t / 1.4);
        SV(scn, "HistVelo").setNumber(Math.round(255 * f));
        if (f > 0) return;
      } else if (tipo === "v") {
        if (R.it.entrada) {                                       // fase 75: fundido a negro antes del video
          SV(scn, "HistVelo").setNumber(Math.round(255 * Math.min(1, t / H.FUNDIDO)));
          if (t < H.FUNDIDO) return;
          R.it.entrada = false; empezarCine(scn, st, it[1]);
        }
        if (!pasoCine(scn, st, inp)) return;
        terminarCine(scn, st);
        SV(scn, "HistVelo").setNumber(255); st.salida = H.now();   // fase 75: y desde negro al terminar
      } else if (tipo === "d") {
        if (!st.lin) { if (R.it.k < it.length) { decir(scn, st, it[R.it.k], true); R.it.k++; } }
        else if (lineaLista(st, inp, true)) { callar(scn, st); if (R.it.k < it.length) { decir(scn, st, it[R.it.k], true); R.it.k++; } }
        if (st.lin) return;
      } else if (tipo === "w") {
        if (!H.ESPERAS[it[1]](scn, st, t)) return;
      }
      R.i++; R.it = null;
      if (tipo === "d" || tipo === "v" || tipo === "fade") {
        const sig = R.seq[R.i];
        if (!sig || !(sig[0] === "d" || sig[0] === "v" || sig[0] === "fade")) devolver(scn, st);
      }
      return;
    }
  }

  // ------------------------------------------------------------------ esperar el disparador del paso (host)
  function disparador(scn, st, saltar) {
    const n = st.paso, P = H.PASOS[n];
    if (n === 12 || P.auto) return;
    const o = P.obj || {};
    let ok = !!saltar;
    if (!ok && o.usar) {
      const g = st.usarObj;
      if (!g || !vivo(g)) objetivo(scn, st, o);                 // alguien lo borró: vuelve a ponerse
      else if (num(g, "Hecho") === 1) ok = true;
    } else if (!ok && o.puerta) ok = o.puerta.some((id) => !puerta(scn, id));   // fase 71: Joel arranca al abrir la puerta de su sala
    else if (!ok && o.zona) ok = enZona(scn, o.zona, H.jugadores(scn));
    if (!ok) return;
    if (st.usarObj && vivo(st.usarObj)) st.usarObj.deleteFromScene(scn);
    st.usarObj = null;
    correr(scn, st, P.seq);
  }
  function charlas(scn, st, inp) {
    if (!st.run) for (const C of H.CHARLAS) {
      if (st.charlas[C.id] || C.paso !== st.paso) continue;
      let ok = false;
      if (C.zona) ok = enZona(scn, C.zona, H.jugadores(scn));
      else if (C.salir) {
        const quien = H.equipo(scn).filter((s) => { const c = num(s, "Control"); return c >= 0 || c === -3; });
        const g = quien.length ? quien : H.equipo(scn);
        if (enZona(scn, C.salir, g)) st.charlas["_dentro" + C.id] = true;
        else if (st.charlas["_dentro" + C.id]) ok = true;
      }
      if (ok) { st.charlas[C.id] = true; st.gq.push(...C.lineas); }
    }
    if (st.run) return;
    if (st.lin && lineaLista(st, inp, false)) callar(scn, st);
    if (!st.lin && st.gq.length) decir(scn, st, st.gq.shift(), false);
  }

  // ------------------------------------------------------------------ fase 71: inicio
  // Hasta que termina la alerta (fin de la secuencia del paso 3) los zombis no se mueven, y el equipo no sale del salón.
  function quietos(scn, st) {
    const frio = st.paso < 3 || (st.paso === 3 && !!st.run);
    for (const z of zombis(scn)) {
      if (frio) {
        if (!z._fdizFrz) { z._fdizFrz = [z.getX(), z.getY()]; try { z.activateBehavior("Pathfinding", false); } catch (e) { /* sin ruta */ } }
        z.setPosition(z._fdizFrz[0], z._fdizFrz[1]);
        try { z.clearForces(); } catch (e) { /* sin fuerzas */ }
      } else if (z._fdizFrz) { z._fdizFrz = null; try { z.activateBehavior("Pathfinding", true); } catch (e) { /* sin ruta */ } }
    }
    if (st.paso <= 3) {
      const R = H.SALON;
      for (const s of H.equipo(scn)) {
        const x = Math.min(R[2] - 24, Math.max(R[0] + 24, s.getX())), y = Math.min(R[3] - 24, Math.max(R[1] + 24, s.getY()));
        if (x !== s.getX() || y !== s.getY()) s.setPosition(x, y);
      }
    }
  }

  // ------------------------------------------------------------------ cada cuadro, host
  function host(scn, st) {
    if (!st.remap) {
      st.remap = true; H.remap(scn);
      // fase 69: desde el primer cuadro el equipo ya está donde empieza el paso guardado (antes aparecía 1 s afuera, frente
      // a E-04, hasta que la historia lo movía), con la pantalla en negro y el jugador sin control hasta que empiece
      let n = HV(scn, "Paso").getAsNumber(); if (!(n >= 1 && n <= 11)) n = 1;
      colocar(scn, st, H.PASOS[n].spawn);
      SV(scn, "HistVelo").setNumber(255);
      congelar(scn, st);
    }
    if (!st.ini) {
      const eq = H.equipo(scn);
      if (!eq.length || !eq.every((s) => num(s, "Init") === 1)) return;
      st.listo = st.listo || H.now();
      if (H.now() - st.listo < 0.2) return;
      try { preparar(scn, st); } catch (e) {                    // no se queda trabada en silencio: lo intenta otra vez
        console.error("FDI-Z historia: preparar", e); st.ini = false; st.listo = H.now(); return;
      }
    }
    // modo presentación (F1 + 1): completa lo que se esté esperando
    let saltar = false;
    if (SV(scn, "Paso").getAsNumber() === 99) { SV(scn, "Paso").setNumber(0); saltar = true; }
    // puerta del salón: cerrada hasta que la rompe el zombi del paso 4
    if (st.paso <= 4 && !(st.run && st.paso === 4 && st.intruso)) {
      const p = puerta(scn, H.LUGAR.puertaSalon);
      if (p) { VS(p, "TiempoAbrir").setNumber(0); VS(p, "Vida").setNumber(99999); VS(p, "Bloqueo").setString("!La puerta está cerrada"); }
    }
    if (st.conserje && muerto(st.conserje)) { st.conserjeMuerto = true; st.conserje = null; }
    const inp = entrada(scn, st), pausa = SV(scn, "Pausa").getAsNumber() === 1;
    if (st.cong && st.cong.soltar && !inp.mantiene) devolver(scn, st, true);   // terminó la escena y ya soltó la tecla
    quietos(scn, st);
    paseos(scn, st);
    salida(scn, st);
    balasAlan(scn, st);
    if (!pausa) {
      if (st.run) {
        if (saltar && st.run.seq[st.run.i] && st.run.seq[st.run.i][0] === "w") {
          if (st.intruso && !muerto(st.intruso)) VS(st.intruso, "Vida").setNumber(0);
          if (st.intendencia && !muerto(st.intendencia)) VS(st.intendencia, "Vida").setNumber(0);
          if (st.defensa) { st.run.i++; st.run.it = null; }
        }
        pasoSeq(scn, st, inp);
      } else if (SV(scn, "Estado").getAsString() === "juego") disparador(scn, st, saltar);
      charlas(scn, st, inp);          // el paso 12 lo dispara la cuenta del autobús (espera "defensa" del paso 11)
    }
    // ayudas en pantalla
    let ayuda = "";
    const p1 = H.controlado(scn);
    if (st.tutorial && H.now() < st.tutorial && st.intruso && !muerto(st.intruso) && p1 && deFuego(p1)) ayuda = "Clic izquierdo (o gatillo del mando) para disparar";
    if (!st.llave && st.reja && H.equipo(scn).some((s) => Math.hypot(s.getX() - (H.REJA.x + 16), s.getY() - (H.REJA.y + H.REJA.h / 2)) < 260))
      ayuda = "La reja trasera está cerrada con llave";
    if (st.avisoCambio && H.now() < st.avisoCambio.hasta) ayuda = st.avisoCambio.txt;
    if (SV(scn, "HistAyuda").getAsString() !== ayuda) SV(scn, "HistAyuda").setString(ayuda);
    textoObjetivo(scn, st);
  }

  // ------------------------------------------------------------------ cada máquina: video, velo, alarma, globo y voz
  function aPantalla(scn, x, y) {
    try { const c = scn.getLayer("Juego").convertInverseCoords(x, y, 0); return scn.getLayer("HUD").convertCoords(c[0], c[1], 0); } catch (e) { return [x, y]; }
  }
  function pool(scn, L) {
    if (L.pool) return L.pool;
    const mk = (n, z) => { const o = scn.createObject(n); if (o) { o.setLayer("HUD"); o.setZOrder(z); } return o; };
    const P = (L.pool = {
      dib: mk("HistDib", 431), panel: mk("ProfPanel", 430), nom: mk("TxtProfe", 432), txt: mk("TxtProfe", 432), ret: mk("HistRetrato", 433),
      velo: mk("HistDib", 1990), ind: mk("HistDib", 2005), rojo: mk("HistDib", 2), ayuda: mk("TxtHist", 420), cap: mk("TxtHist", 1995), salto: mk("TxtHist", 2006),
    });
    if (P.dib) P.dib.setPosition(0, 0);
    for (const k of ["velo", "ind", "rojo"]) if (P[k]) P[k].setPosition(0, 0);
    if (P.nom) { P.nom.setCharacterSize(19); if (P.nom.setTextAlignment) P.nom.setTextAlignment("left"); }
    if (P.txt) { P.txt.setCharacterSize(21); P.txt.setColor("255;255;255"); P.txt.setWrapping(true); P.txt.setWrappingWidth(460); if (P.txt.setTextAlignment) P.txt.setTextAlignment("left"); }
    if (P.ret) P.ret.hide(true);
    return P;
  }
  function musica(scn, L, pausar) {
    if (L.musica === pausar) return;
    L.musica = pausar;
    const S_ = gdjs.evtTools.sound;
    for (const ch of [1, 2]) { try { if (pausar) S_.pauseMusicOnChannel(scn, ch); else S_.continueMusicOnChannel(scn, ch); } catch (e) { /* nada en ese canal */ } }
    try { if (pausar) S_.pauseSoundOnChannel(scn, H.CANAL_ALARMA); else if (L.alarma) S_.continueSoundOnChannel(scn, H.CANAL_ALARMA); } catch (e) { /* sin alarma */ }
  }
  function quitarVideo(scn, L) { if (L.vid) { try { L.vid.pause(); L.vid.deleteFromScene(scn); } catch (e) { /* ya no está */ } L.vid = null; } }
  function cine(scn, st, L, P) {
    const c = SV(scn, "HistCine").getAsString(), seq = SV(scn, "HistCineSeq").getAsNumber();
    const modo = c.slice(0, 1), v = c.slice(2);
    musica(scn, L, modo === "v");
    if (modo !== "v" || L.cine !== c || L.cineSeq !== seq) quitarVideo(scn, L);
    if (modo === "v" && !L.vid) {
      const o = objVideo(v), vid = o ? scn.createObject(o) : null;
      if (vid) {
        vid.setLayer("HUD"); vid.setPosition(0, 0); vid.setZOrder(2000);
        try { vid.setWidth(1920); vid.setHeight(1080); } catch (e) { /* tamaño */ }
        try { vid.setLoop(false); vid.setCurrentTime(0); vid.setVolume(Math.max(0, Math.min(100, GV(scn, "VolMusica").getAsNumber()))); vid._fdizBase = 100; } catch (e) { /* sin cargar */ }
        try { vid.play(); } catch (e) { /* sin cargar */ }
        L.vid = vid;
      }
    }
    L.cine = c; L.cineSeq = seq;
    // velo negro: placeholder de un video que falta, o el fundido de la entrada
    const velo = SV(scn, "HistVelo").getAsNumber(), D = P.velo;
    if (D) {
      D.clear(); D.setOutlineSize(0);
      const a = modo === "n" ? 255 : (modo === "v" ? 255 : velo);
      if (a > 0) { D.setFillColor("0;0;0"); D.setFillOpacity(a); D.drawRectangle(0, 0, 1920, 1080); }
    }
    // indicador de "mantener para saltar" (solo quien puede saltar: host o sin red), encima del video
    const I = P.ind;
    if (I) {
      I.clear(); I.setOutlineSize(0);
      const f = rol(scn) !== 2 ? (L.salto || 0) : 0, D = I;
      if (modo && rol(scn) !== 2) {
        const cx = 1846, cy = 1006, r = 26;
        D.setFillColor("30;30;40"); D.setFillOpacity(200); D.drawCircle(cx, cy, r + 6);
        if (f > 0) {
          D.setFillOpacity(0); D.setOutlineSize(7); D.setOutlineColor("255;230;120"); D.setOutlineOpacity(255);
          D.drawArc(cx, cy, r - 2, -90, -90 + 360 * f, false, false);
          D.setOutlineSize(0);
        }
      }
    }
    const pon = (t, s, x, y, size, col, al) => {
      if (!t) return; t.hide(!s); if (!s) return;
      if (t.getString() !== s) t.setText(s); t.setCharacterSize(size); t.setColor(col);
      if (t.setTextAlignment) t.setTextAlignment(al || "center");
      t.setPosition(al === "right" ? x - t.getWidth() : x - t.getWidth() / 2, y);
    };
    pon(P.cap, modo === "n" ? (H.TITULOS[v] || "") : "", 960, 500, 34, "230;230;235");
    pon(P.salto, modo && rol(scn) !== 2 ? "Mantén ESPACIO / A para saltar" : "", 1806, 992, 18, "190;190;205", "right");
  }
  function alarma(scn, L, P) {
    const on = SV(scn, "HistAlarma").getAsNumber() === 1;
    const S_ = gdjs.evtTools.sound;
    if (on && !L.alarma) { L.alarma = true; try { if (GV(scn, "SonidoActivo").getAsNumber() === 1) S_.playSoundOnChannel(scn, "efectos/eventos/alarma_loop.wav", H.CANAL_ALARMA, true, 22, 1); } catch (e) { /* sin sonido */ } }
    if (!on && L.alarma) { L.alarma = false; try { S_.stopSoundOnChannel(scn, H.CANAL_ALARMA); } catch (e) { /* nada sonaba */ } }
    const D = P.rojo; if (!D) return;
    D.clear(); D.setOutlineSize(0);
    let cx = 0, cy = 0; try { const Lj = scn.getLayer("Juego"); cx = Lj.getCameraX(); cy = Lj.getCameraY(); } catch (e) { /* sin capa */ }
    if (on && dentro(H.SALON, cx, cy)) {
      const a = 0.5 + 0.5 * Math.sin(H.now() * Math.PI * 1.6);
      D.setFillColor("220;20;20"); D.setFillOpacity(Math.round(18 + 52 * a)); D.drawRectangle(0, 0, 1920, 1080);
    }
  }
  function voz(scn, L, seq, it) {
    if (L.voz === seq) return;
    L.voz = seq;
    const S_ = gdjs.evtTools.sound;
    try { S_.stopSoundOnChannel(scn, H.CANAL); } catch (e) { /* nada sonaba */ }
    if (!it || !it.audio) return;
    try { if (GV(scn, "SonidoActivo").getAsNumber() === 1) S_.playSoundOnChannel(scn, it.audio, H.CANAL, false, H.VOL, 1); } catch (e) { /* el archivo no carga: queda el texto */ }
  }
  function enPantalla(scn, o) {
    if (!o || (o.isHidden && o.isHidden())) return false;
    const p = aPantalla(scn, o.getX(), o.getY() - 60);
    return p[0] > 60 && p[0] < 1860 && p[1] > 120 && p[1] < 1040;
  }
  function globo(scn, L, P) {
    const id = SV(scn, "HistLinea").getAsString(), seq = SV(scn, "HistLineaSeq").getAsNumber();
    const it = id ? datos().lineas[id] : null;
    voz(scn, L, it ? seq : -1, it);
    const D = P.dib; if (D) D.clear();
    const ocultar = () => { for (const k of ["panel", "nom", "txt", "ret"]) if (P[k]) P[k].hide(true); };
    if (!it || !P.txt || !P.panel || !P.nom) { ocultar(); return; }
    const quien = H.deId(scn, SV(scn, "HistHabla").getAsString());
    const nombre = (H.NOMBRES[it.pj] || it.pj).toUpperCase();
    if (P.txt._k !== id) { P.txt._k = id; P.txt.setText("«" + it.txt + "»"); P.nom.setText(nombre); P.nom.setColor(H.COLORES[it.pj] || "255;230;120"); }
    const PAD = 14, cine = SV(scn, "HistCine").getAsString() !== "";
    if (!cine && quien && enPantalla(scn, quien)) {
      // globo sobre quien habla (lugar libre: el mismo criterio que los diálogos de la fase 64)
      P.ret.hide(true);
      const w = Math.max(P.txt.getWidth(), P.nom.getWidth()) + PAD * 2, h = P.nom.getHeight() + 4 + P.txt.getHeight() + PAD * 1.4;
      let B = null;
      if (gdjs.fdizDialogo && gdjs.fdizDialogo.colocar) { try { B = gdjs.fdizDialogo.colocar(scn, quien, w, h, []); } catch (e) { B = null; } }
      if (!B) { const p = aPantalla(scn, quien.getX(), quien.getY() - 130); B = { x: Math.max(16, Math.min(1904 - w, p[0] - w / 2)), y: Math.max(16, p[1] - h - 20), arriba: true, cx: p[0], ty: p[1] }; }
      P.panel.hide(false); P.panel.setPosition(B.x, B.y); P.panel.setWidth(w); P.panel.setHeight(h);
      P.nom.hide(false); P.nom.setPosition(B.x + PAD, B.y + PAD * 0.6);
      P.txt.hide(false); P.txt.setPosition(B.x + PAD, B.y + PAD * 0.6 + P.nom.getHeight() + 4);
      if (D) {
        D.setFillColor("14;18;44"); D.setFillOpacity(226); D.setOutlineSize(2); D.setOutlineColor("6;8;20"); D.setOutlineOpacity(235);
        const y0 = B.arriba ? B.y + h - 1 : B.y + 1, y1 = B.arriba ? Math.min(B.ty - 4, y0 + 18) : Math.max(B.ty + 4, y0 - 18);
        D.beginFillPath(B.cx - 10, y0); D.drawPathLineTo(B.cx + 10, y0); D.drawPathLineTo(B.cx, y1); D.closePath(); D.endFillPath();
      }
      return;
    }
    // fuera de pantalla (o sin personaje en el mapa, como el altavoz): retrato + nombre abajo, al centro
    const conRet = !!P.ret && H.EQUIPO.includes(it.pj);
    const RW = conRet ? 92 : 0;
    const w = Math.max(P.txt.getWidth(), P.nom.getWidth()) + PAD * 2 + RW, h = Math.max(RW ? 92 : 0, P.nom.getHeight() + 4 + P.txt.getHeight() + PAD * 1.4);
    const x = 960 - w / 2, y = cine ? 1080 - h - 30 : 820 - h;
    P.panel.hide(false); P.panel.setPosition(x, y); P.panel.setWidth(w); P.panel.setHeight(h);
    if (P.panel.setZOrder) P.panel.setZOrder(cine ? 2010 : 430);
    for (const k of ["nom", "txt", "ret"]) if (P[k] && P[k].setZOrder) P[k].setZOrder(cine ? 2012 : 432);
    if (conRet) {
      P.ret.hide(false); try { P.ret.setAnimationName(it.pj); } catch (e) { /* sin retrato */ }
      P.ret.setWidth(76); P.ret.setHeight(76); P.ret.setPosition(x + 10, y + (h - 76) / 2);
    } else if (P.ret) P.ret.hide(true);
    P.nom.hide(false); P.nom.setPosition(x + RW + PAD, y + PAD * 0.6);
    P.txt.hide(false); P.txt.setPosition(x + RW + PAD, y + PAD * 0.6 + P.nom.getHeight() + 4);
  }
  // fase 71: durante el apagón, un círculo de luz pequeño sigue a Tony (capa de luz "Luz") hasta que vuelve la luz
  function linterna(scn, L) {
    let on = false;
    try { on = SV(scn, "Apagon").getAsNumber() === 1; } catch (e) { /* sin variable */ }
    const t = on ? (H.controlado(scn) || H.equipo(scn).find((s) => num(s, "Jugador") === 1)) : null;   // fase 72: sigue al controlado
    if (!t) { if (L.luz) L.luz.visible = false; return; }
    if (!L.luz) {
      try {
        const cv = document.createElement("canvas"); cv.width = cv.height = 256;
        const x = cv.getContext("2d"), g = x.createRadialGradient(128, 128, 0, 128, 128, 128);
        g.addColorStop(0, "rgba(255,240,210,1)"); g.addColorStop(0.55, "rgba(255,240,210,0.85)"); g.addColorStop(1, "rgba(255,240,210,0)");
        x.fillStyle = g; x.fillRect(0, 0, 256, 256);
        const sp = new PIXI.Sprite(PIXI.Texture.from(cv));
        sp.anchor.set(0.5); sp.blendMode = PIXI.BLEND_MODES.ADD; sp.width = sp.height = 260;
        scn.getLayer("Luz").getRenderer().getRendererObject().addChild(sp);
        L.luz = sp;
      } catch (e) { L.luz = { visible: false, position: { set() {} } }; return; }   // sin PIXI: sin linterna
    }
    L.luz.visible = true;
    L.luz.position.set(t.getX(), t.getY() - 48);
  }
  function render(scn, st) {
    const L = st.local, P = pool(scn, L);
    linterna(scn, L);
    cine(scn, st, L, P);
    alarma(scn, L, P);
    globo(scn, L, P);
    if (P.panel && !P.panel.isHidden() && SV(scn, "HistCine").getAsString() === "") { P.panel.setZOrder(430); for (const k of ["nom", "txt", "ret"]) if (P[k]) P[k].setZOrder(432); }
    const a = SV(scn, "HistAyuda").getAsString(), T = P.ayuda;
    if (T) {
      T.hide(!a || SV(scn, "HistCine").getAsString() !== "");
      if (a) { if (T.getString() !== a) T.setText(a); T.setCharacterSize(26); T.setColor("255;240;150"); T.setPosition(960 - T.getWidth() / 2, 700); }
    }
  }

  // ------------------------------------------------------------------ API para los eventos y los demás módulos
  // ¿Está hablando u ocupada la historia? (dialogo.js se calla mientras tanto)
  H.ocupado = function (scn) {
    if (!H.activo(scn)) return false;
    try { return SV(scn, "HistLinea").getAsString() !== "" || SV(scn, "HistCine").getAsString() !== "" || !!(S(scn).run); } catch (e) { return false; }
  };
  H.tick = function (scn) {
    if (!H.activo(scn)) return;
    const st = S(scn);
    try { if (rol(scn) !== 2) host(scn, st); } catch (e) { if ((st.err = (st.err || 0) + 1) <= 5) console.error("FDI-Z historia", e); }
    try { render(scn, st); } catch (e) { if ((st.errR = (st.errR || 0) + 1) <= 5) console.error("FDI-Z historia (pantalla)", e); }
  };
  // Antes de "Combate: pegar" (host): Joel acompaña pero no ataca; si cae se levanta a los 5 s.
  H.tras = function (scn) {
    if (!H.activo(scn) || rol(scn) === 2) return;
    const st0 = S(scn);
    if (st0.ini && (st0.paso < 3 || (st0.paso === 3 && st0.run)))       // fase 76: en el inicio nadie da golpes (Tony pegaba al aire)
      for (const o of H.equipo(scn)) for (const n of ["QuierePegar", "PideHab", "PideEsp", "QuiereLanzar"]) VS(o, n).setNumber(0);
    const s = supJoel(scn); if (!s) return;
    for (const n of ["QuierePegar", "PideHab", "PideEsp", "QuiereLanzar"]) VS(s, n).setNumber(0);
    if (num(s, "Mordido") === 1) { VS(s, "Mordido").setNumber(0); s.setColor("255;255;255"); }
    if (str(s, "Estado") === "caido" && s.getTimerElapsedTimeInSeconds && s.getTimerElapsedTimeInSeconds("caido") >= 5) {
      VS(s, "Estado").setString("normal"); VS(s, "Vida").setNumber(num(s, "VidaMax") * 0.5); VS(s, "Revivir").setNumber(0);
      try { s.activateBehavior("TopDownMovement", true); } catch (e) { /* sin comportamiento */ }
      try { s.resumeAnimation ? s.resumeAnimation() : s.playAnimation(); } catch (e) { /* sin animación */ }
      try { s.setAnimationName("joel_quieto"); } catch (e) { /* sin animación */ }
    }
  };
  H._S = S;   // para las pruebas
})(gdjs);
