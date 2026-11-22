/* FDI-Z · Fase 64 · Diálogos en burbujas con voz (banco de diálogos). Todos los modos.
 * Se incrusta en la escena Juego con scripts/fase64_dialogos.py (no editar el evento a mano):
 *   FDIZ-FASE64-DATOS (gdjs.fdizDialogosDatos, generado por fase64_datos_dialogos.py), FDIZ-FASE64-MOD y FDIZ-FASE64-TICK
 *   arriba de todo, sin compuerta de host.
 *
 * Host / sin red: detecta los momentos del juego (DISPARADORES, abajo), elige una línea o conversación del banco y la
 *   pone en una cola. Las líneas salen de una en una y en orden: la variable de escena DlgLinea dice cuál se ve
 *   ("l:<frase>:<cuadro>" o "c:<conversación>:<línea>"), DlgHabla quién la dice ("sup:<Jugador>" o "npc:<profe>") y DlgSeq
 *   cambia con cada línea. Esas tres viajan a los clientes.
 * Cada máquina: dibuja la burbuja encima de quien habla (estilo de las de los profes) y pone su voz en UN canal (CANAL),
 *   así nunca suenan dos voces juntas. La línea dura lo que dura su voz; sin voz, lo que tarda leerla. Al terminar se
 *   retira la burbuja y, tras una pausa corta, sale la siguiente.
 * No hay diálogos durante la pausa, la charla con Canepa (fase 61) ni fuera de la partida. En la intro (sin red) las
 *   tres líneas de antes de la alerta las dicen, con su voz, los personajes del equipo que tengan frase de ese momento. */
(function (gdjs) {
  "use strict";
  if (gdjs.fdizDialogo && gdjs.fdizDialogo.VER === 1) return;
  const D = (gdjs.fdizDialogo = { VER: 1 });

  D.CANAL = 7;                    // el mismo que la charla de Canepa: una sola voz a la vez en todo el juego
  D.VOL = 95;
  D.CFG = { hueco: 0.35, cola: 3, espera: 5, porLinea: 40, porPersonaje: 8, globalTras: 2.5, conv: 0.5, vista: [1000, 600] };
  D.NOMBRES = { alan: "Alan", miranda: "Miranda", tony: "Tony", cesar: "César", castillo: "Castillo", gabo: "Gabo",
    alessandro: "Alessandro", carlos: "Carlos", justino: "Justino", canepa: "Canepa", joel: "Joel" };
  D.HUD = [[20, 16, 438, 250], [1482, 16, 1900, 250], [580, 14, 1340, 200], [20, 832, 438, 1064], [1482, 832, 1900, 1064],
    [658, 940, 1263, 1080], [1252, 662, 1892, 1054]];
  // disparadores que dependen de quién lo hizo (la línea es del que actúa)
  D.DE_ACTOR = new Set(["cae", "cae_cerca", "mordido", "mordido_cerca", "revive", "revivido", "curar", "hab", "hab_regla", "hab_comida",
    "hab_puerta", "esp", "silla", "engrapadora", "locker", "llaves", "llamada", "bidon", "luz", "carnada", "puerta_abre", "atorados",
    "puerta_electronica", "arma_piso", "fin_pelea"]);
  // los que se repiten mucho salen solo a veces
  D.PROB = { fin_pelea: 0.4, arma_piso: 0.5, locker: 0.6, locker_equipo: 0.4, puerta_abre: 0.35, puerta_golpe: 0.5, revive: 0.7, cae: 0.8, objetivo_nuevo: 0.6 };
  D.now = () => Date.now() / 1000;
  D.rnd = () => Math.random();

  const VS = (o, n) => o.getVariables().get(n);
  const num = (o, n) => VS(o, n).getAsNumber();
  const str = (o, n) => VS(o, n).getAsString();
  const SV = (scn, n) => scn.getVariables().get(n);
  const GV = (scn, n) => scn.getGame().getVariables().get(n);
  const objs = (scn, n) => { try { return scn.getObjects(n) || []; } catch (e) { return []; } };
  const rol = (scn) => { try { return GV(scn, "NetRol").getAsNumber(); } catch (e) { return 0; } };
  const dist = (a, b) => Math.hypot(a.getX() - b.getX(), a.getY() - b.getY());
  const datos = () => gdjs.fdizDialogosDatos || { lineas: [], conversaciones: [] };
  const pjDe = (s) => { const p = str(s, "Personaje"); return p === "tonyfuerte" ? "tony" : p; };
  const ZN = ["ZNormal", "ZCorredor", "ZGriton", "ZGordo", "ZConserje", "ZJoel", "ZJustino", "ZCanepa"];
  const S = (scn) => scn._fdizDlg || (scn._fdizDlg = { cola: [], actual: null, fin: 0, ult: {}, pjUlt: {}, globalHasta: 0, prev: null,
    sup: new Map(), puertas: new Map(), bidones: new Map(), objetivos: new Map(), cont: new Map(), seq: 0, voz: { seq: -1 }, pool: null,
    combate: 0, killsPelea: 0, calmaDicha: true, respiroDicho: true, quietoDesde: 0, finalT0: 0, finalDichos: {}, intro: null });

  // ------------------------------------------------------------------ quién es quién
  D.equipo = (scn) => objs(scn, "Sup").filter((s) => str(s, "Estado") !== "fuera" && num(s, "Jugador") >= 1);
  function hablante(scn, pj) {
    for (const s of D.equipo(scn)) if (pjDe(s) === pj) return s;
    for (const p of objs(scn, "Profe")) if (str(p, "Nombre") === pj) return p;
    return null;
  }
  // los personajes (Sup, también los profes aliados) tienen Jugador; el profe que espera (objeto Profe) solo Nombre
  D.idDe = (o) => (!o ? "" : o.getVariables().has("Jugador") ? "sup:" + num(o, "Jugador") : "npc:" + str(o, "Nombre"));
  D.deId = function (scn, id) {
    if (!id) return null;
    if (id.startsWith("npc:")) { const n = id.slice(4); for (const p of objs(scn, "Profe")) if (str(p, "Nombre") === n) return p; return hablante(scn, n); }
    const j = Number(id.slice(4));
    for (const s of objs(scn, "Sup")) if (num(s, "Jugador") === j) return s;
    return null;
  };
  function enVista(scn, o) {
    try { const L = scn.getLayer("Juego"); return Math.abs(o.getX() - L.getCameraX()) < D.CFG.vista[0] && Math.abs(o.getY() - L.getCameraY()) < D.CFG.vista[1]; }
    catch (e) { return true; }
  }
  const puedeHablar = (scn, o, disp) => o && enVista(scn, o) &&
    (!o.getVariables().has || !o.getVariables().has("Estado") || ["normal", "espera", "conversacion", "aliado"].includes(str(o, "Estado"))
      || (/^(cae|cae_cerca|mordido|mordido_cerca)$/.test(disp)));

  // ------------------------------------------------------------------ elegir qué se dice
  function lineaItem(i, k, o) {
    const L = datos().lineas[i], c = L.cuadros[k];
    return { id: "l:" + i + ":" + k, quien: D.idDe(o), pj: L.pj, txt: c.txt, voz: c.voz, dur: c.dur, clave: "l:" + i };
  }
  D.opciones = function (scn, disp, actor, extra) {
    const ops = [], dat = datos();
    const apj = actor ? pjDe(actor) : null;
    dat.conversaciones.forEach((C, i) => {
      if (C.disp !== disp || (C.actor && C.actor !== apj)) return;
      const hab = {};
      for (const x of C.lineas) { const o = (C.actor && x.pj === apj) ? actor : hablante(scn, x.pj); if (!puedeHablar(scn, o, disp)) return; hab[x.pj] = o; }
      if (C.cerca && actor && dist(hab[C.cerca], actor) > 450) return;
      if (disp === "revive" && extra && extra.target && C.cerca && hab[C.cerca] !== extra.target) return;  // César revive a ESE Alessandro
      ops.push({ conv: true, clave: "c:" + i, items: C.lineas.map((x, k) => ({ id: "c:" + i + ":" + k, quien: D.idDe(hab[x.pj]), pj: x.pj, txt: x.txt, voz: x.voz, dur: x.dur })) });
    });
    dat.lineas.forEach((L, i) => {
      if (L.disp !== disp) return;
      let o;
      if (D.DE_ACTOR.has(disp)) { if (!actor || pjDe(actor) !== L.pj) return; o = actor; }
      else if (disp === "turbo") { o = hablante(scn, L.pj); if (!o || o === actor || (actor && dist(o, actor) > 600)) return; }
      else if (disp === "caido_visto") { o = hablante(scn, L.pj); if (!o || o === actor || !actor || dist(o, actor) > 400) return; }
      else o = hablante(scn, L.pj);
      if (!puedeHablar(scn, o, disp)) return;
      ops.push({ conv: false, clave: "l:" + i, items: L.cuadros.map((c, k) => lineaItem(i, k, o)) });
    });
    return ops;
  };
  D.decir = function (scn, disp, actor, extra) {
    const st = S(scn), t = D.now();
    const p = D.PROB[disp];
    if (p !== undefined && D.rnd() > p) return false;
    const ops = D.opciones(scn, disp, actor, extra).filter((o) => !(st.ult[o.clave] > t - D.CFG.porLinea) &&
      !o.items.some((it) => st.pjUlt[it.pj] > t - D.CFG.porPersonaje && !o.conv));
    if (!ops.length) return false;
    const convs = ops.filter((o) => o.conv), solas = ops.filter((o) => !o.conv);
    const lista = convs.length && (!solas.length || D.rnd() < D.CFG.conv) ? convs : solas;
    const n = disp === "escape" ? Math.min(2, lista.length) : 1;
    const elegidas = lista.slice().sort(() => D.rnd() - 0.5).slice(0, n);
    for (const o of elegidas) {
      if (st.cola.length >= D.CFG.cola) return false;
      st.ult[o.clave] = t;
      st.cola.push({ items: o.items.slice(), hasta: t + D.CFG.espera + (extra && extra.prioridad ? 30 : 0), conv: o.conv });
    }
    return true;
  };

  // ------------------------------------------------------------------ cola (host)
  const durDe = (it) => (it.voz && it.dur ? it.dur + 0.35 : Math.max(2.2, Math.min(6, 1.4 + 0.05 * it.txt.length)));
  function publicar(scn, st, it) {
    st.seq += 1;
    SV(scn, "DlgSeq").setNumber(st.seq);
    SV(scn, "DlgLinea").setString(it ? it.id : "");
    SV(scn, "DlgHabla").setString(it ? it.quien : "");
  }
  function avanzar(scn, st) {
    const t = D.now();
    if (st.actual && t < st.fin) return;
    if (st.actual) {                                          // terminó la línea: se retira la burbuja
      st.actual = null; publicar(scn, st, null);
      // sigue la conversación, el 2.º cuadro o la intro: pausa corta; si no, la pausa normal entre diálogos
      const sigue = st.cola.length && (st.cola[0].enCurso || st.cola[0].intro);
      st.globalHasta = t + (sigue ? D.CFG.hueco : D.CFG.globalTras);
      return;
    }
    if (t < st.globalHasta) return;
    while (st.cola.length && !st.cola[0].enCurso && st.cola[0].hasta < t) st.cola.shift();   // se pasó su momento
    const q = st.cola[0];
    if (!q) return;
    const it = q.items.shift();
    q.enCurso = true;
    if (!q.items.length) st.cola.shift();
    const o = D.deId(scn, it.quien);
    if (!o) { if (st.cola[0] === q) st.cola.shift(); return; }   // ya no está: se cancela lo que le quedaba
    st.actual = it; st.fin = t + durDe(it); st.pjUlt[it.pj] = t;
    publicar(scn, st, it);
  }
  D.limpiar = function (scn) {
    const st = S(scn);
    st.cola = []; st.actual = null;
    if (SV(scn, "DlgLinea").getAsString() !== "") publicar(scn, st, null);
  };

  // ------------------------------------------------------------------ detectar los momentos (host)
  function cercano(scn, x, y, filtro) {
    let m = null, md = 1e9;
    for (const s of D.equipo(scn)) { if (filtro && !filtro(s)) continue; const d = Math.hypot(s.getX() - x, s.getY() - y); if (d < md) { md = d; m = s; } }
    return [m, md];
  }
  const normal = (s) => str(s, "Estado") === "normal";
  function zombiCerca(scn, s, r) {
    for (const n of ZN) for (const z of objs(scn, n)) {
      if (str(z, "Estado") === "muerto" || num(z, "Aliado") === 1) continue;
      if (dist(z, s) < r) return true;
    }
    return false;
  }
  function detectar(scn, st) {
    const t = D.now(), eq = D.equipo(scn);
    const dec = (d, a, ex) => D.decir(scn, d, a, ex);
    // jugadores
    let algunoSeMueve = false, kills = 0;
    for (const s of eq) {
      const ahora = { est: str(s, "Estado"), mor: num(s, "Mordido"), cur: num(s, "Curando"), hab: str(s, "HabTxt"), esp: str(s, "EspTxt"),
        arma: str(s, "Arma"), lanz: str(s, "Lanz"), lu: num(s, "LanzUsos"), turbo: num(s, "Turbo"), usa: num(s, "Usando"),
        acc: str(s, "Accion"), kills: num(s, "Kills") };
      const p = st.sup.get(s); st.sup.set(s, ahora);
      if (num(s, "MovX") !== 0 || num(s, "MovY") !== 0 || ahora.usa) algunoSeMueve = true;
      kills += ahora.kills;
      if (!p) continue;
      if (ahora.est === "caido" && p.est === "normal") {
        const [m, md] = cercano(scn, s.getX(), s.getY(), (o) => o !== s && normal(o));
        if (!dec("cae", s) && m && md < 350) dec("cae_cerca", s);        // Alan solo tiene «cae con un compañero cerca»
        dec("caido_visto", s);
      }
      if (ahora.est === "normal" && p.est === "caido") {
        const [m, md] = cercano(scn, s.getX(), s.getY(), (o) => o !== s && normal(o));
        if (!(m && md < 170 && dec("revive", m, { target: s }))) dec("revivido", s);
      }
      if (ahora.mor === 1 && p.mor !== 1) {
        const [m, md] = cercano(scn, s.getX(), s.getY(), (o) => o !== s && normal(o));
        if (!dec("mordido", s) && m && md < 350) dec("mordido_cerca", s); // Miranda solo tiene «con un compañero cerca»
      }
      if (ahora.cur === 1 && p.cur !== 1) dec("curar", s);
      if (p.hab === "LISTA" && ahora.hab !== "LISTA" && ahora.hab !== "") {
        if (pjDe(s) === "alan") st.gorrear = { s, t: t + 0.4, comidas: st.nComida || 0 };   // comidas del cuadro anterior
        else if (pjDe(s) === "cesar" && objs(scn, "Puerta").some((d) => Math.hypot(d.getX() - s.getX(), d.getY() - s.getY()) < 320)) dec("hab_puerta", s) || dec("hab", s);
        else dec("hab", s);
      }
      if (p.esp === "LISTO" && ahora.esp !== "LISTO" && ahora.esp !== "") dec("esp", s);
      if (ahora.arma === "silla" && p.arma !== "silla") dec("silla", s);
      if (ahora.lanz === "engrapadora" && p.lanz === "engrapadora" && ahora.lu < p.lu) dec("engrapadora", s);
      if (ahora.turbo === 1 && p.turbo !== 1) dec("turbo", s);
      if (ahora.usa === 1 && p.usa !== 1) {
        if (ahora.acc === "bloqueada") dec("atorados", s);
        if (ahora.acc === "puerta") {
          const [d] = objs(scn, "Puerta").map((x) => [x, Math.hypot(x.getX() + x.getWidth() / 2 - s.getX(), x.getY() + x.getHeight() / 2 - s.getY())]).sort((a, b) => a[1] - b[1])[0] || [];
          if (d && /electronica/.test(str(d, "Tipo")) && num(d, "TiempoAbrir") > 1) dec("puerta_electronica", s);
        }
      }
      if (ahora.kills > p.kills && !zombiCerca(scn, s, 420)) dec("fin_pelea", s);
      if (normal(s) && ahora.arma && !/^pu/.test(ahora.arma) && objs(scn, "ArmaPiso").some((a) => dist(a, s) < 90)) dec("arma_piso", s);
    }
    const nComida = objs(scn, "Comida").length;
    if (st.gorrear && t >= st.gorrear.t) {                                // Gorrear: ¿salió comida además de la regla?
      const g = st.gorrear; st.gorrear = null;
      dec(nComida > g.comidas ? "hab_comida" : "hab_regla", g.s);
    }
    if (!st.gorrear) st.nComida = nComida;
    // calma, respiro y duda
    const combate = eq.some((s) => zombiCerca(scn, s, 520));
    if (combate) { st.combate = t; if (kills > (st.killsBase || 0)) st.killsPelea += kills - (st.killsBase || 0); }
    st.killsBase = kills;
    if (combate) { st.calmaDicha = st.killsPelea < 3; st.respiroDicho = st.killsPelea < 3; }
    if (!combate && !st.calmaDicha && t - st.combate > 9) { st.calmaDicha = true; st.killsPelea = 0; dec("calma"); }
    if (!combate && !st.respiroDicho && t - st.combate > 28) { st.respiroDicho = true; dec("respiro"); }
    if (algunoSeMueve || combate) st.quietoDesde = t;
    else if (t - st.quietoDesde > 9) { st.quietoDesde = t + 120; dec(SV(scn, "FinalActivo").getAsNumber() === 1 ? "final_duda" : "duda"); }
    // puertas, lockers, objetivos, bidones (lo que desaparece: quién estaba más cerca)
    const vivasP = new Set(objs(scn, "Puerta"));
    for (const d of vivasP) {
      const v = num(d, "Vida"), p = st.puertas.get(d);
      st.puertas.set(d, { v, x: d.getX() + d.getWidth() / 2, y: d.getY() + d.getHeight() / 2 });
      if (p && v < p.v && ZN.some((n) => objs(scn, n).some((z) => Math.hypot(z.getX() - p.x, z.getY() - p.y) < 120)) &&
          eq.some((s) => Math.hypot(s.getX() - p.x, s.getY() - p.y) < 600)) dec("puerta_golpe");
    }
    for (const [d, p] of st.puertas) if (!vivasP.has(d)) {
      st.puertas.delete(d);
      if (p.v > 0) { const [m, md] = cercano(scn, p.x, p.y, normal); if (m && md < 220) dec("puerta_abre", m); }
      else if (eq.some((s) => Math.hypot(s.getX() - p.x, s.getY() - p.y) < 700)) dec("puerta_rota");
    }
    for (const c of objs(scn, "Contenedor")) {
      const a = num(c, "Abierto"), p = st.cont.get(c); st.cont.set(c, a);
      if (p === 0 && a === 1) { const [m] = cercano(scn, c.getX(), c.getY(), normal); (m && dec("locker", m)) || dec("locker_equipo"); }
    }
    const vivosB = new Set(objs(scn, "Bidon"));
    for (const b of vivosB) st.bidones.set(b, [b.getX(), b.getY()]);
    for (const [b, xy] of st.bidones) if (!vivosB.has(b)) { st.bidones.delete(b); const [m] = cercano(scn, xy[0], xy[1], normal); if (m) dec("bidon", m); }
    const vivosO = new Set(objs(scn, "Objetivo"));
    for (const o of vivosO) {
      const tipo = str(o, "Tipo"), p = st.objetivos.get(o), u = num(o, "Usada"), h = num(o, "Hecho");
      st.objetivos.set(o, { tipo, u, h, x: o.getX(), y: o.getY() });
      if (!p) continue;
      const [m] = cercano(scn, o.getX(), o.getY(), normal);
      if (u === 1 && p.u !== 1 && (tipo === "computadora" || tipo === "servidor") && m) dec("llamada", m);
      if (h === 1 && p.h !== 1 && m) {
        if (tipo === "llaves") dec("llaves", m);
        if (tipo === "carnada") dec("carnada", m);
        if (tipo === "interruptor" && SV(scn, "Interruptores").getAsNumber() >= 2) dec("luz", m);
      }
    }
    for (const o of [...st.objetivos.keys()]) if (!vivosO.has(o)) st.objetivos.delete(o);
    // variables de escena
    const V = (n) => { try { return SV(scn, n).getAsNumber(); } catch (e) { return 0; } };
    const ahora = { tarjeta: V("Tarjeta"), apagon: V("Apagon"), horda: V("Horda"), festin: V("Festin"), final: V("FinalActivo"),
      objNum: V("ObjNum"), objIni: V("ObjIni"), estado: SV(scn, "Estado").getAsString(), justino: SV(scn, "ProfJustino").getAsString(),
      tipo: SV(scn, "ObjTipo").getAsString() };
    const p = st.prev; st.prev = ahora;
    if (!p) return;
    if (ahora.tarjeta === 1 && p.tarjeta !== 1) dec("tarjeta");
    if (ahora.apagon === 1 && p.apagon !== 1) dec("apagon");
    if (ahora.horda === 1 && p.horda !== 1) dec("horda");
    if (ahora.festin === 1 && p.festin !== 1) dec("festin");
    if (ahora.objNum > p.objNum) dec("objetivo_cumplido");
    if (ahora.objIni === 1 && p.objIni !== 1) { if (ahora.tipo === "llaves" && dec("objetivo_llaves")) {} else dec("objetivo_nuevo"); }
    if (ahora.final === 1 && p.final !== 1) { st.finalT0 = t; st.finalDichos = {}; dec("final", null, { prioridad: true }); }
    if (ahora.final === 1) for (const [d, seg] of [["final_motor", 5], ["final_entrada", 18], ["final_oleada", 32], ["final_tiempo", 42], ["final_casi", 50]])
      if (!st.finalDichos[d] && t - st.finalT0 >= seg) { st.finalDichos[d] = true; dec(d); }
    if (ahora.estado === "victoria" && p.estado !== "victoria") { st.cola = []; dec("escape", null, { prioridad: true }); }
    if (ahora.justino === "conversacion" && p.justino === "espera") dec("rescate_inicio");
    if (ahora.justino === "aliado" && p.justino !== "aliado") {
      const j = hablante(scn, "justino"), [m] = j ? cercano(scn, j.getX(), j.getY(), (o) => normal(o) && num(o, "Jugador") <= 4) : [null];
      dec("rescate_justino", m, {});
    }
  }

  // ------------------------------------------------------------------ intro (sin red): las líneas de antes de la alerta
  const INTRO = [[0.3, "intro_espera"], [3.3, "intro_espera"], [6.3, "intro_espera"], [10.6, "intro_alerta"], [19.8, "intro_puerta"]];
  function intro(scn, st) {
    const t = D.now();
    if (!st.intro) {
      st.intro = { t0: t, k: 0, usados: new Set(), reemplaza: D.opciones(scn, "intro_espera").length > 0 };
    }
    const I = st.intro;
    while (I.k < INTRO.length && t - I.t0 >= INTRO[I.k][0]) {
      const disp = INTRO[I.k][1]; I.k++;
      const ops = D.opciones(scn, disp).filter((o) => !o.items.some((it) => I.usados.has(it.pj)) && !st.ult[o.clave]);
      if (!ops.length) continue;
      const o = ops[Math.floor(D.rnd() * ops.length) % ops.length];
      o.items.forEach((it) => I.usados.add(it.pj));
      st.ult[o.clave] = t;
      st.cola.push({ items: o.items.slice(), hasta: t + 14, conv: false, intro: true });
    }
    // las líneas "Tony: …", "Alan: …", "Miranda: …" del texto de la intro las reemplazan las burbujas de arriba
    if (I.reemplaza) for (const tx of objs(scn, "TxtDialogo")) {
      const s = tx.getString ? tx.getString() : "";
      if (/^(Tony|Alan|Miranda):/.test(s)) tx.setText("");
    }
  }

  // ------------------------------------------------------------------ burbuja y voz (cada máquina)
  const aPantalla = (scn, x, y) => { const c = scn.getLayer("Juego").convertInverseCoords(x, y, 0); return scn.getLayer("HUD").convertCoords(c[0], c[1], 0); };
  const cruce = (a, b) => Math.max(0, Math.min(a[2], b[2]) - Math.max(a[0], b[0])) * Math.max(0, Math.min(a[3], b[3]) - Math.max(a[1], b[1]));
  function caja(scn, o) {
    const x0 = o.getDrawableX ? o.getDrawableX() : o.getX() - 30, y0 = o.getDrawableY ? o.getDrawableY() : o.getY() - 120;
    const a = aPantalla(scn, x0, y0), b = aPantalla(scn, x0 + o.getWidth(), y0 + o.getHeight());
    return [a[0], a[1], b[0], b[1]];
  }
  D.colocar = function (scn, quien, w, h, extra) {
    const k = caja(scn, quien), cx = (k[0] + k[2]) / 2;
    const caras = [];
    for (const n of ["Sup", "Profe"]) for (const o of objs(scn, n)) {
      if (o.isHidden && o.isHidden()) continue;
      const b = caja(scn, o); caras.push([b[0], b[1], b[2], b[1] + (b[3] - b[1]) * 0.45]);
    }
    const evitar = D.HUD.concat(extra || []), cand = [];
    [0, -0.35, 0.35, -0.7, 0.7].forEach((dx, n) => cand.push({ x: cx - w / 2 + dx * w, y: k[1] - 22 - h, arriba: true, pref: n }));
    [0, -0.5, 0.5].forEach((dx, n) => cand.push({ x: cx - w / 2 + dx * w, y: k[3] + 22, arriba: false, pref: 6 + n }));
    let mejor = null;
    for (const c of cand) {
      const x = Math.max(16, Math.min(1920 - 16 - w, c.x)), y = Math.max(16, Math.min(1080 - 16 - h, c.y)), r = [x, y, x + w, y + h];
      let p = c.pref * 40 + Math.abs(x - c.x) * 2 + Math.abs(y - c.y) * 4;
      for (const z of evitar) p += cruce(r, z) * 4;
      for (const z of caras) p += cruce(r, z) * 3;
      if (!mejor || p < mejor.p) mejor = { x, y, w, h, arriba: c.arriba, p, cx: Math.max(x + 18, Math.min(x + w - 18, cx)), ty: c.arriba ? k[1] : k[3] };
    }
    return mejor;
  };
  function pool(scn, st) {
    if (st.pool) return st.pool;
    const mk = (n, z) => { const o = scn.createObject(n); if (o) { o.setLayer("HUD"); o.setZOrder(z); } return o; };
    const P = (st.pool = { panel: mk("ProfPanel", 425), nom: mk("TxtProfe", 427), txt: mk("TxtProfe", 427), dib: mk("DlgDib", 426) });
    if (P.nom) { P.nom.setCharacterSize(18); P.nom.setColor("255;230;120"); if (P.nom.setTextAlignment) P.nom.setTextAlignment("left"); }
    if (P.txt) { P.txt.setCharacterSize(20); P.txt.setColor("255;255;255"); P.txt.setWrapping(true); P.txt.setWrappingWidth(440); if (P.txt.setTextAlignment) P.txt.setTextAlignment("left"); }
    if (P.dib) P.dib.setPosition(0, 0);
    return P;
  }
  function ocultar(st) {
    const P = st.pool; if (!P) return;
    for (const k of ["panel", "nom", "txt"]) if (P[k]) P[k].hide(true);
    if (P.dib) P.dib.clear();
  }
  D.item = function (id) {
    const [tipo, a, b] = id.split(":"), dat = datos();
    if (tipo === "l") { const L = dat.lineas[+a]; return L ? Object.assign({ pj: L.pj }, L.cuadros[+b]) : null; }
    const C = dat.conversaciones[+a]; return C ? C.lineas[+b] : null;
  };
  function dibujar(scn, st, it, quien) {
    const P = pool(scn, st);
    if (!P.txt || !P.panel || !P.nom) return;
    const nombre = D.NOMBRES[it.pj] || "";
    if (P.txt._k !== it.txt) { P.txt._k = it.txt; P.txt.setText("«" + it.txt + "»"); P.nom.setText(nombre.toUpperCase()); }
    const PAD = 14, w = Math.max(P.txt.getWidth(), P.nom.getWidth()) + PAD * 2, h = P.nom.getHeight() + 4 + P.txt.getHeight() + PAD * 1.4;
    const extra = [];
    for (const n of ["TxtBanner", "TxtAyuda", "TxtDialogo"]) for (const t of objs(scn, n)) {
      if ((t.isHidden && t.isHidden()) || !(t.getString ? t.getString() : "")) continue;
      extra.push([t.getX(), t.getY(), t.getX() + t.getWidth(), t.getY() + t.getHeight()]);
    }
    for (const p of objs(scn, "ProfPanel")) {                // otras burbujas (profes, charla de Canepa): no encimarse
      if (p === P.panel || (p.isHidden && p.isHidden())) continue;
      extra.push([p.getX(), p.getY(), p.getX() + p.getWidth(), p.getY() + p.getHeight()]);
    }
    const B = D.colocar(scn, quien, w, h, extra);
    P.panel.hide(false); P.panel.setPosition(B.x, B.y); P.panel.setWidth(w); P.panel.setHeight(h);
    P.nom.hide(false); P.nom.setPosition(B.x + PAD, B.y + PAD * 0.6);
    P.txt.hide(false); P.txt.setPosition(B.x + PAD, B.y + PAD * 0.6 + P.nom.getHeight() + 4);
    if (P.dib) {
      const d = P.dib; d.clear();
      d.setFillColor("14;18;44"); d.setFillOpacity(226); d.setOutlineSize(2); d.setOutlineColor("6;8;20"); d.setOutlineOpacity(235);
      const y0 = B.arriba ? B.y + h - 1 : B.y + 1, y1 = B.arriba ? Math.min(B.ty - 4, y0 + 18) : Math.max(B.ty + 4, y0 - 18);
      d.beginFillPath(B.cx - 10, y0); d.drawPathLineTo(B.cx + 10, y0); d.drawPathLineTo(B.cx, y1); d.closePath(); d.endFillPath();
    }
    D.ultima = B;
  }
  function voz(scn, st, seq, it) {
    if (st.voz.seq === seq) return;
    st.voz.seq = seq;
    const S_ = gdjs.evtTools && gdjs.evtTools.sound;
    if (!S_) return;
    try { S_.stopSoundOnChannel(scn, D.CANAL); } catch (e) { /* nada sonaba */ }
    if (!it || !it.voz) return;                              // sin voz: la burbuja sola
    try {
      if (GV(scn, "SonidoActivo").getAsNumber() !== 1) return;
      S_.playSoundOnChannel(scn, it.voz, D.CANAL, false, D.VOL, 1);
    } catch (e) { /* el archivo no carga: queda el texto */ }
  }

  // ------------------------------------------------------------------ cada cuadro
  D.tick = function (scn) {
    const st = S(scn), estado = SV(scn, "Estado").getAsString();
    let charla = 0; try { charla = SV(scn, "CanepaCharla").getAsNumber(); } catch (e) { /* sin Historia */ }
    const pausa = SV(scn, "Pausa").getAsNumber() === 1;
    const activo = !pausa && charla !== 1 && (estado === "juego" || estado === "intro" || estado === "victoria");
    if (rol(scn) !== 2) {
      if (!activo) { if (st.actual || st.cola.length) D.limpiar(scn); }
      else {
        if (estado === "intro") intro(scn, st);
        else { if (st.intro) { st.intro = null; D.limpiar(scn); } if (estado === "juego") detectar(scn, st); else if (estado === "victoria") detectar(scn, st); }
        avanzar(scn, st);
      }
    }
    // todas las máquinas: lo que diga DlgLinea
    const id = SV(scn, "DlgLinea").getAsString(), seq = SV(scn, "DlgSeq").getAsNumber();
    const it = activo && id ? D.item(id) : null;
    const quien = it ? D.deId(scn, SV(scn, "DlgHabla").getAsString()) : null;
    voz(scn, st, it ? seq : -1, it);
    if (it && quien) dibujar(scn, st, it, quien); else ocultar(st);
  };
})(gdjs);
