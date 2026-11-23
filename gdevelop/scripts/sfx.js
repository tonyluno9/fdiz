/* FDI-Z · Fase 60 · Efectos de sonido de la carpeta sonidos/ (recursos con el nombre del archivo: "ui_click.ogg", ...).
 * Se incrusta al inicio de TODAS las escenas (evento FDIZ-FASE60-MOD) y se llama cada cuadro (FDIZ-FASE60-TICK), sin
 * compuerta de host: cada máquina calcula sus propios sonidos a partir de lo que ya se sincroniza (vida, estado, animación,
 * variables de escena). Por eso se reproducen con la función ORIGINAL de GDevelop (sin el reenvío por red de net_core):
 * así no se oyen dos veces en los clientes.
 *
 * Reglas:
 *  - Todos son de un solo disparo (sin loop). El growl se repite con intervalo aleatorio y volumen según la distancia.
 *  - Volumen: efectos 70-100, interfaz 50-60 (tabla VOL). La música (cuando se agregue) va en 40-50.
 *  - Pitch aleatorio ±0.1 en golpes, dolor y growl (tabla VAR). Zombis: normal 1.0, grande 0.7, rápido 1.3 (TONO_Z).
 *    Dolor: 0.8 para todos los personajes salvo Miranda (1.0) (voz()).
 *  - Cooldown corto (tabla CD) para lo que se puede disparar muchas veces seguidas (golpes, monedas, ...).
 *  - Los sonidos del mundo de un zombi solo suenan si está a menos de LEJOS px del centro de la cámara de esta máquina.
 *  - El volumen general de efectos (Ajustes, fase 57) se aplica a todo esto porque pasa por el mismo gestor de sonido.
 *
 * Sonidos que siguen en los eventos (no aquí): puerta_casillero (puertas, lockers, salida), objeto_recoger (bidones),
 * oleada_riser (sube la infestación) y evento_impacto_cinematico (empieza el final). */
(function (gdjs) {
  "use strict";
  if (gdjs.fdizSfx && gdjs.fdizSfx.VER === 1) return;
  const X = (gdjs.fdizSfx = { VER: 1 });

  X.VOL = {
    ui_hover: 50, ui_click: 55, ui_confirm: 60, ui_error: 60,
    golpe_impacto: 75, jugador_dolor: 80, cuerpo_caida: 75, whoosh_esquivar: 70,
    zombie_growl: 80, zombie_ataque: 75, zombie_mordida: 85, zombie_muerte_01: 80, zombie_muerte_02: 80, zombie_spawn_braam: 80,
    oro_moneda: 75, objeto_recoger: 80, puerta_casillero: 80, curar_powerup: 80,
    oleada_riser: 85, evento_impacto_cinematico: 95, game_over: 90, victoria: 90,
  };
  // cooldown en segundos por clave (la clave de las muertes es "zombie_muerte": cubre los dos archivos)
  X.CD = {
    golpe_impacto: 0.1, oro_moneda: 0.1, jugador_dolor: 0.1, zombie_mordida: 0.1, zombie_muerte: 0.1, cuerpo_caida: 0.1,
    whoosh_esquivar: 0.1, zombie_ataque: 0.1, zombie_spawn_braam: 0.25, objeto_recoger: 0.1, curar_powerup: 0.4,
    ui_hover: 0.08, ui_click: 0.1, ui_confirm: 0.15, ui_error: 0.3, oleada_riser: 1, evento_impacto_cinematico: 1,
  };
  X.VAR = { golpe_impacto: 0.1, jugador_dolor: 0.1, zombie_growl: 0.1 };      // ± pitch aleatorio
  X.TONO_Z = { normal: 1.0, griton: 1.0, gordo: 0.7, conserje: 0.7, corredor: 1.3 };
  X.voz = (pj) => (/miranda/i.test(pj || "") ? 1.0 : 0.8);
  X.GROWL = { dist: 1000, vol: 80, min: 12, cadaZ: [5, 12], hueco: [0.8, 2.0] };
  X.LEJOS = 1300;
  X.ZN = ["ZNormal", "ZCorredor", "ZGriton", "ZGordo", "ZConserje", "ZJoel", "ZJustino", "ZCanepa"];
  X.now = () => Date.now() / 1000;
  X.rnd = () => Math.random();
  X.log = null;                                     // las pruebas ponen aquí un arreglo para ver qué sonó

  const ult = {};
  const entre = (a) => a[0] + X.rnd() * (a[1] - a[0]);
  X.play = function (scn, nombre, o) {
    o = o || {};
    try { if (scn.getGame().getVariables().get("SonidoActivo").getAsNumber() !== 1) return false; } catch (e) { /* sin variable: suena */ }
    const k = o.k || nombre, t = X.now(), cd = o.cd != null ? o.cd : X.CD[k] || 0;
    if (cd && ult[k] != null && t - ult[k] >= 0 && t - ult[k] < cd) return false;
    ult[k] = t;
    let p = o.pitch != null ? o.pitch : 1;
    const v = X.VAR[nombre]; if (v) p += (X.rnd() * 2 - 1) * v;
    p = Math.max(0.3, Math.round(p * 1000) / 1000);
    const vol = Math.round(o.vol != null ? o.vol : X.VOL[nombre] != null ? X.VOL[nombre] : 80);
    if (X.log) X.log.push({ s: nombre, vol, p, esc: scn.getName ? scn.getName() : "" });
    try {
      const S = gdjs.evtTools && gdjs.evtTools.sound;
      const f = S && (S._orig || S.playSound);                 // _orig = sin reenviar por la red (net_core)
      if (f) f.call(S, scn, nombre + ".ogg", false, vol, p);
    } catch (e) { return false; }
    return true;
  };
  X.ui = (scn, tipo) => X.play(scn, "ui_" + tipo);

  // ------------------------------------------------------------------ utilidades
  const lista = (scn, n) => { try { return scn.getObjects(n) || []; } catch (e) { return []; } };
  const num = (o, n) => o.getVariables().get(n).getAsNumber();
  const str = (o, n) => o.getVariables().get(n).getAsString();
  const svn = (scn, n) => scn.getVariables().get(n).getAsNumber();
  const svs = (scn, n) => scn.getVariables().get(n).getAsString();
  const gv = (scn) => scn.getGame().getVariables();
  const anim = (o) => { try { return o.getAnimationName ? o.getAnimationName() : ""; } catch (e) { return ""; } };
  const visible = (o) => { try { return (!o.isVisible || o.isVisible()) && (!o.isHidden || !o.isHidden()) && (!o.getOpacity || o.getOpacity() > 0); } catch (e) { return true; } };
  const rol = (scn) => { try { return gv(scn).get("NetRol").getAsNumber(); } catch (e) { return 0; } };

  // ------------------------------------------------------------------ al entrar a cada escena
  const INICIO = {
    Titulo: () => ["evento_impacto_cinematico"],
    Menu: () => ["whoosh_esquivar"],
    Online: () => ["whoosh_esquivar"],
    Juego: () => ["ui_confirm"],                                     // empezar partida
    Resultados: (scn) => [gv(scn).get("Resultado").getAsString() === "victoria" ? "victoria" : "game_over"],
  };

  // ------------------------------------------------------------------ interfaz: variables que cambian = botón usado
  // [variable de escena, sonido o función(antes, ahora) -> sonido]. Vale igual para ratón, teclado y mando.
  const okSnd = (a, b) => (b === 1 ? "ui_confirm" : "ui_click");
  const VIG = {
    Menu: [["Paso", "ui_click"], ["Sel", "ui_hover"], ["Foco", "ui_hover"], ["JT", "ui_hover"], ["HV", (a, b) => (b >= 0 ? "ui_hover" : null)],
      ["S1Pj", "ui_click"], ["S2Pj", "ui_click"], ["S3Pj", "ui_click"], ["S4Pj", "ui_click"],
      ["S1Ok", okSnd], ["S2Ok", okSnd], ["S3Ok", okSnd], ["S4Ok", okSnd],
      ["S1Ctl", "ui_click"], ["S2Ctl", "ui_click"], ["S3Ctl", "ui_click"], ["S4Ctl", "ui_click"],
      ["Hecho", (a, b) => (b === 1 ? "ui_confirm" : null)]],
    Resultados: [["Sel", "ui_hover"]],
    Juego: [["Pausa", "ui_click"], ["PausaVista", "ui_click"], ["PausaSel", "ui_hover"], ["Carta", "ui_click"]],
  };
  const GLOB = { Menu: [["Dificultad", "ui_click"]] };
  // botones bajo el cursor: ui_hover al entrar a uno, ui_click al soltar el clic encima
  const BOTONES = {
    Menu: ["MarcoModo", "SelMarco", "DifBtn", "EqCelda", "EqRet", "BtnSalir"],
    Resultados: ["BtnRei", "BtnMenuR"],
    Juego: ["PausaBtn", "JfCarta"],
  };

  function leer(get) { try { return get(); } catch (e) { return undefined; } }
  function vigilar(scn, st, clave, valor, regla) {
    const k = "v:" + clave, a = st.v[k];
    st.v[k] = valor;
    if (a === undefined || valor === undefined || a === valor || !st.listoUi) return;
    const s = typeof regla === "function" ? regla(a, valor) : regla;
    if (s) X.play(scn, s);
  }

  function interfaz(scn, nom, st) {
    for (const [n, r] of VIG[nom] || []) vigilar(scn, st, n, leer(() => scn.getVariables().has(n) ? scn.getVariables().get(n).getValue() : undefined), r);
    for (const [n, r] of GLOB[nom] || []) vigilar(scn, st, "g" + n, leer(() => gv(scn).get(n).getValue()), r);
    if (nom === "Online" && gdjs.fdizNet && gdjs.fdizNet.ui) {
      const U = gdjs.fdizNet.ui;
      vigilar(scn, st, "on.st", U.st, (a, b) => (b === "error" ? "ui_error" : b === "lobby" ? "ui_confirm" : "ui_click"));
      vigilar(scn, st, "on.sel", U.sel, "ui_hover");
    }
    const nombres = BOTONES[nom];
    if (!nombres) return;
    const inp = gdjs.evtTools && gdjs.evtTools.input;
    if (!inp) return;
    let sobre = null;
    for (const n of nombres) {
      for (const o of lista(scn, n)) {
        if (!visible(o)) continue;
        const lay = o.getLayer ? o.getLayer() : "";
        const mx = leer(() => inp.getMouseX(scn, lay, 0)), my = leer(() => inp.getMouseY(scn, lay, 0));
        if (mx === undefined) continue;
        const x = o.getX(), y = o.getY(), w = o.getWidth(), h = o.getHeight();
        if (mx >= x && mx <= x + w && my >= y && my <= y + h) { sobre = o; break; }
      }
      if (sobre) break;
    }
    const mx = leer(() => inp.getMouseX(scn, "", 0)), my = leer(() => inp.getMouseY(scn, "", 0));
    const movio = st.mx !== undefined && (mx !== st.mx || my !== st.my);
    st.mx = mx; st.my = my;
    if (sobre && sobre !== st.hov && movio && st.listoUi) X.play(scn, "ui_hover");
    st.hov = sobre;
    if (sobre && st.listoUi && leer(() => inp.isMouseButtonReleased(scn, "Left"))) X.play(scn, "ui_click");
  }

  // ------------------------------------------------------------------ partida (escena Juego)
  function juego(scn, st) {
    const t = X.now(), V = scn.getVariables();
    const pausa = leer(() => svn(scn, "Pausa")) === 1;
    if (pausa) return;                                              // en pausa no cambia nada del mundo
    const estado = leer(() => svs(scn, "Estado"));
    const activo = estado === "juego" && t - st.t0 >= 1.0;
    const jefe = leer(() => gv(scn).get("Modo").getAsString()) === "jefe";
    const r = rol(scn);
    let cx = 0, cy = 0;
    try { const L = scn.getLayer("Juego"); cx = L.getCameraX(); cy = L.getCameraY(); } catch (e) { /* sin capa */ }
    const lejos = (o) => Math.hypot(o.getX() - cx, o.getY() - cy) > X.LEJOS;

    // jugadores
    for (const s of lista(scn, "Sup")) {
      const now = {
        vida: num(s, "Vida"), est: str(s, "Estado"), anim: anim(s), arma: str(s, "Arma"), lanz: str(s, "Lanz"),
        cc: num(s, "ComidaCura"), usa: num(s, "Usando"),
      };
      const p = s.__fdizSfx; s.__fdizSfx = now;
      if (!p || !activo) continue;
      if (now.vida < p.vida - 0.01) {                                // un zombi le conectó un golpe (es lo único que le quita vida)
        X.play(scn, "golpe_impacto");
        X.play(scn, "zombie_mordida");
        X.play(scn, "jugador_dolor", { pitch: X.voz(str(s, "Personaje")) });
      } else if (now.vida >= p.vida + 5 && now.est === "normal") {   // curarse (comida, pociones, habilidades); la regeneración lenta no llega a 5
        X.play(scn, "curar_powerup");
      }
      if (now.est !== p.est) {
        if (now.est === "caido") X.play(scn, "cuerpo_caida");
        else if (p.est === "caido" && now.est === "normal") X.play(scn, "curar_powerup");    // lo levantaron
      }
      if (now.anim !== p.anim && /_pegar_/.test(now.anim) && num(s, "ArmaFuego") !== 1) X.play(scn, "whoosh_esquivar");
      if (now.arma !== p.arma && now.arma && !/^pu/.test(now.arma)) X.play(scn, "objeto_recoger");
      if (now.lanz !== p.lanz && now.lanz) X.play(scn, "objeto_recoger");
      if (now.cc > 0 && p.cc <= 0) X.play(scn, "objeto_recoger");
      if (now.usa === 1 && p.usa !== 1 && str(s, "Accion") === "bloqueada" && num(s, "Control") >= 0 && r !== 2) X.ui(scn, "error");
    }

    // zombis
    const vivos = [];
    for (const n of X.ZN) {
      for (const z of lista(scn, n)) {
        const tipo = str(z, "Tipo"), tono = X.TONO_Z[tipo] || 1;
        const now = { vida: num(z, "Vida"), est: str(z, "Estado"), anim: anim(z) };
        const p = z.__fdizSfx; z.__fdizSfx = now;
        const aliado = num(z, "Aliado") === 1;
        if (z.__fdizG === undefined) z.__fdizG = t + entre([1, 8]);
        if (!aliado && now.est !== "muerto") vivos.push({ z, tono, est: now.est });
        if (!activo) continue;
        if (!p) {                                                     // apareció (horda, infestación, invocación del Jefe, convertido)
          if (now.est !== "muerto" && !aliado && !lejos(z)) X.play(scn, "zombie_spawn_braam", { pitch: tono });
          if (tipo === "conserje" && !st.jefeVisto) { st.jefeVisto = true; X.play(scn, "evento_impacto_cinematico"); }
          continue;
        }
        if (tipo === "conserje" && !st.jefeVisto && now.est === "persigue" && p.est !== "persigue") {
          st.jefeVisto = true; X.play(scn, "evento_impacto_cinematico");                       // el jefe entra en acción
        }
        if (lejos(z)) continue;
        if (now.vida < p.vida - 0.01 && p.est !== "muerto") X.play(scn, "golpe_impacto");
        if (now.est === "muerto" && p.est !== "muerto") {
          X.play(scn, X.rnd() < 0.5 ? "zombie_muerte_01" : "zombie_muerte_02", { k: "zombie_muerte", pitch: tono });
          X.play(scn, "cuerpo_caida");
        }
        if (now.anim !== p.anim && /^atacar_/.test(now.anim)) X.play(scn, "zombie_ataque", { pitch: tono });
      }
    }

    // objetos y oro
    for (const o of lista(scn, "Objetivo")) {
      const h = num(o, "Hecho"), p = o.__fdizSfx; o.__fdizSfx = h;
      if (activo && p === 0 && h === 1 && str(o, "Tipo") === "llaves") X.play(scn, "objeto_recoger");
    }
    const monedas = lista(scn, "Moneda").length;
    const sv = {
      bolsa: leer(() => svn(scn, "TieneBolsa")), dinero: leer(() => svn(scn, "Dinero")), oro: leer(() => svn(scn, "OroJefe")),
      horda: leer(() => svn(scn, "Horda")), final: leer(() => svn(scn, "FinalActivo")), inf: leer(() => svn(scn, "Infestacion")),
      monedas, estado,
    };
    const p = st.sv; st.sv = sv;
    let oleada = false;
    if (p && activo) {
      if (sv.bolsa === 1 && p.bolsa !== 1) X.play(scn, "objeto_recoger");
      if (jefe && r !== 2 && sv.oro !== p.oro) {                    // solo en la máquina del Jefe
        // fase 80: las monedas ya no suenan
        if (sv.oro < p.oro) X.ui(scn, "confirm");                     // compra con oro hecha
      }
      if (sv.horda === 1 && p.horda !== 1) { X.play(scn, "oleada_riser"); oleada = true; }
      if (sv.final === 1 && p.final !== 1) { X.play(scn, "oleada_riser", { cd: 0 }); oleada = true; }   // cuenta regresiva del final
      if (sv.inf > p.inf && sv.inf > 1) oleada = true;               // el riser lo pone el evento del HUD
    }
    if (p && jefe && sv.estado === "juego" && p.estado !== "juego" && !st.jefeIni) { st.jefeIni = true; X.play(scn, "evento_impacto_cinematico"); }
    try { V.get("OleadaInicio").setNumber(oleada ? 1 : 0); } catch (e) { /* sin variable */ }   // la lee el TODO de música de tensión

    // growl: un zombi cercano gruñe de vez en cuando, más fuerte cuanto más cerca de la cámara
    if (activo && t >= (st.gNext || 0)) {
      st.gNext = t + entre(X.GROWL.hueco);
      const G = X.GROWL;
      const cand = vivos.filter((c) => !/^(dormido|congelado|cinematica)$/.test(c.est) && c.z.__fdizG <= t &&
        Math.hypot(c.z.getX() - cx, c.z.getY() - cy) < G.dist);
      if (cand.length) {
        const c = cand[Math.floor(X.rnd() * cand.length) % cand.length];
        const d = Math.hypot(c.z.getX() - cx, c.z.getY() - cy);
        const vol = G.vol * Math.pow(1 - d / G.dist, 1.3);
        c.z.__fdizG = t + entre(G.cadaZ);
        if (vol >= G.min) X.play(scn, "zombie_growl", { vol, pitch: c.tono, cd: 0 });
      }
    }
    // TODO: footsteps — cuando haya sonido de pasos: por cada Sup en movimiento, un paso cada ~0.35 s (volumen 70, pitch ±0.1).
  }

  // ------------------------------------------------------------------ cada cuadro
  X.tick = function (scn) {
    const nom = scn.getName ? scn.getName() : "";
    let st = scn.__fdizSfx;
    if (!st) st = scn.__fdizSfx = { t0: X.now(), v: {}, ini: false, listoUi: false };
    if (!st.ini) {
      st.ini = true;
      for (const s of (INICIO[nom] ? INICIO[nom](scn) : [])) X.play(scn, s, { cd: 0 });
    }
    interfaz(scn, nom, st);
    st.listoUi = true;                                               // el primer cuadro solo toma referencias
    if (nom === "Juego") juego(scn, st);
  };
})(gdjs);
