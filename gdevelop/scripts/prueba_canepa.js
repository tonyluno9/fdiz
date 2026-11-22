// Pruebas de scripts/canepa.js (fase 61) y de su conexión con el proyecto, sin GDevelop:  node gdevelop/scripts/prueba_canepa.js
"use strict";
const fs = require("fs"), path = require("path"), vm = require("vm");
const d = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "FDI-Z", "FDI-Z.json"), "utf8"));
let ok = 0, mal = 0;
function prueba(n, f) { try { f(); ok++; console.log("  OK   " + n); } catch (e) { mal++; console.log("  MAL  " + n + " -> " + e.message); } }
const igual = (a, b, m) => { if (JSON.stringify(a) !== JSON.stringify(b)) throw new Error((m || "") + ": " + JSON.stringify(a) + " != " + JSON.stringify(b)); };
const si = (c, m) => { if (!c) throw new Error(m || "falso"); };

// ---------------------------------------------------------------- mundo falso
function variable(x) { return { getAsNumber: () => Number(x) || 0, getAsString: () => String(x), setNumber: (n) => { x = n; }, setString: (s) => { x = s; }, add: (n) => { x = Number(x) + n; } }; }
function cont(ini) { const V = {}; for (const k in ini || {}) V[k] = variable(ini[k]); return { V, get: (n) => V[n] || (V[n] = variable(0)), has: (n) => n in V }; }
function obj(nombre, x, y, vars, w, h) {
  const C = cont(vars);
  return { nombre, x, y, w: w || 64, h: h || 120, C, hidden: false, _livingOnScene: true,
    getVariables: () => C, getX() { return this.x; }, getY() { return this.y; }, getWidth() { return this.w; }, getHeight() { return this.h; },
    getDrawableX() { return this.x - this.w / 2; }, getDrawableY() { return this.y - this.h; }, isHidden() { return this.hidden; },
    getCenterX() { return this.w / 2; }, getCenterY() { return this.h / 2; } };
}
const sup = (j, pj, x, y, ctl) => obj("Sup", x, y, { Jugador: j, Personaje: pj, Control: ctl === undefined ? 0 : ctl, Estado: "normal", MovX: 1, Usando: 1 });
function hudObj(n) {
  const o = { n, txt: "", oculto: false, x: 0, y: 0, w: 0, h: 0, k: null, cs: 20,
    setLayer() {}, setZOrder() {}, hide(b) { this.oculto = b; }, isHidden() { return this.oculto; }, setText(s) { this.txt = s; }, getString() { return this.txt; },
    setCharacterSize(c) { this.cs = c; }, setColor() {}, setWrapping() {}, setWrappingWidth(w) { this.ww = w; }, setTextAlignment() {},
    setPosition(x, y) { this.x = x; this.y = y; }, getX() { return this.x; }, getY() { return this.y; },
    getWidth() { return this.n === "TxtProfe" ? Math.min(this.ww || 9999, this.txt.length * this.cs * 0.55) : this.w; },
    getHeight() { return this.n === "TxtProfe" ? this.cs * 1.3 * Math.ceil(this.txt.length * this.cs * 0.55 / (this.ww || 9999)) : this.h; },
    setWidth(w) { this.w = w; }, setHeight(h) { this.h = h; },
    clear() { this.tri = null; }, setFillColor() {}, setFillOpacity() {}, setOutlineSize() {}, setOutlineColor() {}, setOutlineOpacity() {},
    beginFillPath(x, y) { this.tri = [[x, y]]; }, drawPathLineTo(x, y) { this.tri.push([x, y]); }, closePath() {}, endFillPath() {} };
  return o;
}
let reloj = 1000;
const teclas = new Set();
function mundo(o) {
  o = o || {};
  const sonidos = [], canal = { suena: false, archivo: null, para: 0 };
  const sound = {
    playSoundOnChannel: (scn, f, ch, loop, vol) => { if (o.romper) throw new Error("no carga"); if (canal.suena) canal.encimadas = (canal.encimadas || 0) + 1; sonidos.push({ f, ch, vol }); canal.suena = true; canal.archivo = f; },
    stopSoundOnChannel: () => { canal.suena = false; canal.para++; },
    isSoundOnChannelPlaying: () => canal.suena,
  };
  const input = { isKeyPressed: (s, k) => teclas.has(k), isMouseButtonPressed: () => false };
  const gdjs = { evtTools: { sound, input } };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, "canepa.js"), "utf8"), { gdjs, Math, Date, RegExp, Map, Number });
  gdjs.fdizCanepa.now = () => reloj;
  return { gdjs, C: gdjs.fdizCanepa, sonidos, canal };
}
function escena(objs, sv, gl) {
  const S = cont(Object.assign({ Estado: "juego", CanepaCharla: 0, CinLinea: -1, CinHabla: "", Paso: 0, Pausa: 0 }, sv));
  const G = cont(Object.assign({ NetRol: 0, Modo: "historia", SonidoActivo: 1 }, gl));
  let escala = 1;
  const hud = [];
  const capa = { convertInverseCoords: (x, y) => [x - sc.camX + 960, y - sc.camY + 540], convertCoords: (x, y) => [x, y] };
  const sc = { objs, S, G, hud, camX: 544, camY: 3200,
    getVariables: () => S, getGame: () => ({ getVariables: () => G }), getLayer: () => capa,
    getObjects: (n) => objs.filter((o) => o.nombre === n).concat(hud.filter((h) => h.n === n)),
    getTimeManager: () => ({ getTimeScale: () => escala, setTimeScale: (x) => { escala = x; } }), escala: () => escala,
    createObject: (n) => { const h = hudObj(n); hud.push(h); return h; } };
  return sc;
}
const profe = () => obj("Profe", 544, 3328, { Nombre: "canepa", Estado: "espera" });
const cuadro = (w, sc, dt) => { reloj += dt || 0.1; w.C.tick(sc); };
const burbuja = (sc) => sc.hud.find((h) => h.n === "ProfPanel");
const textos = (sc) => sc.hud.filter((h) => h.n === "TxtProfe");

// ---------------------------------------------------------------- pruebas
prueba("Líneas: el diálogo pedido, en orden y con quien lo dice", () => {
  const w = mundo();
  igual(w.C.LINEAS.map((l) => l.rol), ["canepa", "tony", "canepa", "miranda", "canepa", "tony"]);
  igual(w.C.LINEAS[2].txt, "No queda suficiente gasolina. Sin combustible no podremos alejarnos del campus.");
  igual(Object.keys(w.C.VOCES).length, 0, "no hay voces grabadas de estas líneas");
});
prueba("Canepa reservado en Historia hasta la charla (ni en Escape ni los otros profes)", () => {
  const w = mundo(), sc = escena([]);
  si(w.C.reservado(sc, "canepa") && !w.C.reservado(sc, "joel"));
  sc.S.get("CanepaCharla").setNumber(2); si(!w.C.reservado(sc, "canepa"), "después de la charla se puede reclutar");
  si(!w.C.reservado(escena([], {}, { Modo: "escape" }), "canepa"), "Escape no cambia");
});
prueba("Quién habla: Tony y Miranda si están; si no, otro del equipo (nunca un bot de profe)", () => {
  const w = mundo();
  igual(w.C.asignar(escena([sup(1, "tonyfuerte", 0, 0), sup(2, "miranda", 0, 0), sup(7, "canepa", 0, 0, -1)])), { canepa: "npc:canepa", tony: "sup:1", miranda: "sup:2" });
  igual(w.C.asignar(escena([sup(1, "alan", 0, 0), sup(2, "gabo", 0, 0), sup(3, "miranda", 0, 0)])), { canepa: "npc:canepa", tony: "sup:1", miranda: "sup:3" });
  igual(w.C.asignar(escena([sup(1, "carlos", 0, 0), sup(2, "cesar", 0, 0)])), { canepa: "npc:canepa", tony: "sup:1", miranda: "sup:2" });
  igual(w.C.asignar(escena([sup(1, "castillo", 0, 0)])), { canepa: "npc:canepa", tony: "sup:1", miranda: "sup:1" });
});
prueba("Secuencia: congela el mundo, quita el control, muestra las 6 líneas en orden y al final cumple la misión una sola vez", () => {
  const w = mundo(), t = sup(1, "tonyfuerte", 500, 3300), m = sup(2, "miranda", 600, 3300), b = sup(3, "gabo", 650, 3300, -1), r = sup(4, "alan", 700, 3300, -3);
  const sc = escena([profe(), t, m, b, r]);
  cuadro(w, sc); igual(sc.S.get("Estado").getAsString(), "juego", "sin charla no pasa nada");
  sc.S.get("CanepaCharla").setNumber(1); cuadro(w, sc);
  igual([sc.S.get("Estado").getAsString(), sc.escala(), [t, m, b, r].map((s) => s.C.get("Control").getAsNumber()), t.C.get("MovX").getAsNumber()],
    ["dialogo", 0, [-2, -2, -1, -2], 0]);
  const vistas = [], quien = [];
  for (let k = 0; k < 400 && sc.S.get("CanepaCharla").getAsNumber() === 1; k++) {
    cuadro(w, sc);
    const i = sc.S.get("CinLinea").getAsNumber();
    if (i >= 0 && vistas[vistas.length - 1] !== i) { vistas.push(i); quien.push(sc.S.get("CinHabla").getAsString()); }
  }
  igual(vistas, [0, 1, 2, 3, 4, 5]);
  igual(quien, ["npc:canepa", "sup:1", "npc:canepa", "sup:2", "npc:canepa", "sup:1"]);
  igual([sc.S.get("Estado").getAsString(), sc.escala(), [t, m, b, r].map((s) => s.C.get("Control").getAsNumber()), sc.S.get("CanepaCharla").getAsNumber(), sc.S.get("Paso").getAsNumber()],
    ["juego", 1, [0, 0, -1, -3], 2, 99], "todo vuelve como estaba y Paso = 99");
  sc.S.get("Paso").setNumber(0); for (let k = 0; k < 50; k++) cuadro(w, sc);
  igual(sc.S.get("Paso").getAsNumber(), 0, "no se cumple dos veces");
  si(burbuja(sc).oculto && textos(sc).every((x) => x.oculto), "la burbuja se retira al terminar");
});
prueba("Saltar: F / Enter / Espacio adelanta la línea (después de 0.6 s); mantenerla no salta más líneas", () => {
  const w = mundo(), sc = escena([profe(), sup(1, "tony", 500, 3300)]);
  teclas.add("f"); sc.S.get("CanepaCharla").setNumber(1); cuadro(w, sc);       // la F con la que se habló sigue apretada
  for (let k = 0; k < 10; k++) cuadro(w, sc);
  igual(sc.S.get("CinLinea").getAsNumber(), 0, "mantener F no salta");
  teclas.clear(); cuadro(w, sc); teclas.add("Return"); cuadro(w, sc);
  igual(sc.S.get("CinLinea").getAsNumber(), 1, "Enter salta a la siguiente");
  cuadro(w, sc, 0.1); igual(sc.S.get("CinLinea").getAsNumber(), 1, "sigue apretada: no salta otra");
  teclas.clear(); cuadro(w, sc, 0.1); teclas.add("Space"); cuadro(w, sc, 0.1);
  igual(sc.S.get("CinLinea").getAsNumber(), 1, "antes de 0.6 s no se salta");
  teclas.clear();
});
prueba("Cada línea dura lo que tarda leerla (2.4 a 6.5 s) cuando no hay voz", () => {
  const w = mundo();
  const ds = w.C.LINEAS.map((l) => w.C.duracion(l.txt));
  si(ds.every((x) => x >= 2.4 && x <= 6.5), JSON.stringify(ds));
  const L = w.C.LINEAS.map((l) => l.txt.length);
  for (let i = 0; i < L.length; i++) for (let j = 0; j < L.length; j++) if (L[i] > L[j]) si(ds[i] >= ds[j], "más larga, más tiempo");
  igual(Math.round(w.C.duracion("¿Qué pasó?") * 10) / 10, 2.4, "las cortas, el mínimo");
});
prueba("Burbuja: encima de quien habla, sin tapar el HUD ni caras; con su nombre y la colita hacia él", () => {
  const w = mundo(), t = sup(1, "tonyfuerte", 470, 3330), m = sup(2, "miranda", 620, 3330), cn = profe();
  const sc = escena([cn, t, m]);
  sc.S.get("CanepaCharla").setNumber(1); cuadro(w, sc);
  const B = burbuja(sc), [nom, txt] = textos(sc);
  igual([nom.txt, txt.txt], ["CANEPA", "«¡Llegaron! Necesito ayuda. El autobús no puede salir.»"]);
  const caja = [B.x, B.y, B.x + B.w, B.y + B.h];
  const cara = (o) => { const x0 = o.getDrawableX() - sc.camX + 960, y0 = o.getDrawableY() - sc.camY + 540; return [x0, y0, x0 + o.w, y0 + o.h * 0.45]; };
  const cruza = (a, b) => Math.min(a[2], b[2]) > Math.max(a[0], b[0]) && Math.min(a[3], b[3]) > Math.max(a[1], b[1]);
  si(B.y + B.h <= cara(cn)[1], "va encima de la cabeza de Canepa");
  si(![cn, t, m].some((o) => cruza(caja, cara(o))), "no tapa ninguna cara");
  si(!w.C.HUD.some((z) => cruza(caja, z)), "no tapa el HUD");
  const tri = sc.hud.find((h) => h.n === "DlgDib").tri;
  si(tri && tri[2][1] > tri[0][1], "colita hacia abajo, hacia Canepa");
});
prueba("Burbuja: si arriba está el HUD, se acomoda (debajo o a un lado) sin taparlo", () => {
  const w = mundo(), t = sup(1, "tonyfuerte", 544, 3328);
  const sc = escena([profe(), t]); sc.camY = 3328 + 540 - 260;          // Canepa queda arriba, junto a los paneles superiores
  sc.camX = 544 + 960 - 300;                                           // y a la izquierda, bajo el panel del jugador 1
  sc.S.get("CanepaCharla").setNumber(1); cuadro(w, sc);
  const B = burbuja(sc), caja = [B.x, B.y, B.x + B.w, B.y + B.h];
  si(!w.C.HUD.some((z) => Math.min(caja[2], z[2]) > Math.max(caja[0], z[0]) && Math.min(caja[3], z[3]) > Math.max(caja[1], z[1])), JSON.stringify(caja));
  si(caja[0] >= 16 && caja[2] <= 1904 && caja[1] >= 16 && caja[3] <= 1064, "dentro de la pantalla");
});
prueba("Burbuja: no tapa el letrero (TxtBanner) si está a la vista", () => {
  const w = mundo(), sc = escena([profe(), sup(1, "tonyfuerte", 470, 3330)]);
  sc.camY = 3328 - 120;                                                  // la cabeza de Canepa queda a la altura del letrero
  const ban = sc.createObject("TxtBanner"); ban.txt = "¡OBJETIVO 4/6 CUMPLIDO!"; ban.x = 600; ban.y = 380; ban.w = 720; ban.h = 60;
  sc.S.get("CanepaCharla").setNumber(1); cuadro(w, sc);
  const B = burbuja(sc);
  si(!(Math.min(B.x + B.w, 1320) > Math.max(B.x, 600) && Math.min(B.y + B.h, 440) > Math.max(B.y, 380)), JSON.stringify([B.x, B.y, B.w, B.h]));
});
prueba("Voces: sin archivos la secuencia sigue igual (solo texto) y no suena nada", () => {
  const w = mundo(), sc = escena([profe(), sup(1, "tony", 500, 3300)]);
  sc.S.get("CanepaCharla").setNumber(1);
  for (let k = 0; k < 400 && sc.S.get("CanepaCharla").getAsNumber() === 1; k++) cuadro(w, sc);
  igual([sc.S.get("CanepaCharla").getAsNumber(), w.sonidos.length], [2, 0]);
});
prueba("Voces: una sola a la vez en su canal; la línea espera a que termine; solo si la dice ese personaje", () => {
  const w = mundo(); w.C.VOCES[1] = { pj: "tony", archivo: "voz_tony.wav" }; w.C.VOCES[3] = { pj: "miranda", archivo: "voz_miranda.wav" };
  const sc = escena([profe(), sup(1, "tonyfuerte", 500, 3300), sup(2, "gabo", 600, 3300)]);   // Miranda no está: su línea la dice Gabo
  sc.S.get("CanepaCharla").setNumber(1);
  let t1 = null, fin1 = null;
  for (let k = 0; k < 600 && sc.S.get("CanepaCharla").getAsNumber() === 1; k++) {
    cuadro(w, sc);
    const i = sc.S.get("CinLinea").getAsNumber();
    if (i === 1 && t1 === null) t1 = reloj;
    if (i === 1 && reloj - t1 > 7 && w.canal.suena) w.canal.suena = false;  // la voz de Tony dura 7 s
    if (i === 2 && fin1 === null) fin1 = reloj - t1;
  }
  igual(w.sonidos.map((s) => [s.f, s.ch]), [["voz_tony.wav", 7]], "la de Miranda no suena con Gabo");
  si(fin1 >= 7 && fin1 < 7.5, "la línea 1 esperó a la voz: " + fin1);
  si(!w.canal.encimadas, "nunca dos voces a la vez");
});
prueba("Voces: un archivo que no carga no detiene la misión", () => {
  const w = mundo({ romper: true }); w.C.VOCES[0] = { pj: "canepa", archivo: "no_existe.wav" };
  const sc = escena([profe(), sup(1, "tony", 500, 3300)]);
  sc.S.get("CanepaCharla").setNumber(1);
  for (let k = 0; k < 400 && sc.S.get("CanepaCharla").getAsNumber() === 1; k++) cuadro(w, sc);
  igual(sc.S.get("CanepaCharla").getAsNumber(), 2);
});
prueba("En línea: el cliente no lleva la secuencia, pero dibuja la burbuja que manda el host", () => {
  const w = mundo(), sc = escena([profe(), sup(1, "tony", 500, 3300)], { CanepaCharla: 1, CinLinea: 3, CinHabla: "sup:1", Estado: "dialogo" }, { NetRol: 2 });
  for (let k = 0; k < 100; k++) cuadro(w, sc);
  igual([sc.S.get("CinLinea").getAsNumber(), sc.escala(), textos(sc)[1].txt], [3, 1, "«Acabamos de distraer a la horda. Podemos buscar gasolina.»"]);
  igual(textos(sc)[0].txt, "TONY", "la línea de Miranda la dice Tony si ella no está");
  sc.S.get("CanepaCharla").setNumber(2); sc.S.get("CinLinea").setNumber(-1); cuadro(w, sc);
  si(burbuja(sc).oculto, "se retira cuando el host termina");
});
prueba("Fuera de Historia no hace nada", () => {
  const w = mundo(), sc = escena([profe(), sup(1, "tony", 0, 0)], { CanepaCharla: 1 }, { Modo: "escape" });
  for (let k = 0; k < 20; k++) cuadro(w, sc);
  igual([sc.S.get("Estado").getAsString(), sc.escala(), sc.hud.length], ["juego", 1, 0]);
});

// ---------------------------------------------------------------- proyecto
const J = d.layouts.find((l) => l.name === "Juego");
const rec = function* (evs) { for (const e of evs || []) { yield e; yield* rec(e.events); } };
prueba("Proyecto: canepa.js arriba de Juego, sin compuerta de host, y el objeto DlgDib", () => {
  const top = J.events.map((e) => (e.inlineCode || "").slice(0, 22));
  const m = top.findIndex((s) => s.startsWith("/*FDIZ-FASE61-MOD")), t = top.findIndex((s) => s.startsWith("/*FDIZ-FASE61-TICK"));
  si(m >= 0 && t === m + 1, "eventos " + [m, t]);
  si(J.events[m].inlineCode.includes(fs.readFileSync(path.join(__dirname, "canepa.js"), "utf8").trim().slice(0, 300)), "código al día");
  si(J.objects.some((o) => o.name === "DlgDib" && o.type === "PrimitiveDrawing::Drawer"));
});
prueba("Proyecto: profes.js y usar.js incrustados preguntan por la reserva de Canepa; usar.js dice «hablar con Canepa»", () => {
  const code = (m) => [...rec(J.events)].find((e) => (e.inlineCode || "").startsWith("/*" + m)).inlineCode;
  si(code("FDIZ-FASE40-MOD").includes("gdjs.fdizCanepa.reservado(scn, k)"), "profes.js");
  si(code("FDIZ-FASE56-MOD").includes('gdjs.fdizCanepa.reservado(scn, str(p, "Nombre"))') && code("FDIZ-FASE56-MOD").includes('canepa: "hablar con Canepa"'), "usar.js");
});
prueba("Proyecto: en línea viajan CanepaCharla, CinLinea y CinHabla", () => {
  const T = d.layouts.find((l) => l.name === "Titulo");
  const n = [...rec(T.events)].find((e) => (e.inlineCode || "").includes("gdjs.fdizNetCfg="));
  const m = n.inlineCode.match(/gdjs\.fdizNetCfg=(\{[\s\S]*?\});\n/);
  const cfg = JSON.parse(m[1]);
  for (const v of ["CanepaCharla", "CinLinea", "CinHabla", "O6"]) si(cfg.sv.includes(v), v);
});
prueba("Árbitro de la F (usar.js): junto a Canepa, la F es para la misión y no para reclutarlo", () => {
  const w = mundo();
  const U = {}; const g2 = { fdizCanepa: w.C };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, "usar.js"), "utf8"), { gdjs: g2, Math, Map, Set });
  const s = sup(1, "tony", 520, 3330); s.C.get("Usando").setNumber(1);
  const pr = profe(), ob = obj("Objetivo", 544, 3328, { Tipo: "canepa", Tiempo: 0.6, Progreso: 0, Hecho: 0 }, 32, 32);
  const sc = escena([s, pr, ob]);
  sc.getLayer = () => ({ convertInverseCoords: (x, y) => [x, y], convertCoords: (x, y) => [x, y] });
  g2.fdizUsar.elegir(sc);
  igual([s.C.get("Accion").getAsString(), s.C.get("UsaObjetivo").getAsNumber()], ["objetivo", 1]);
  sc.S.get("CanepaCharla").setNumber(2); ob.hidden = true; sc.objs.splice(sc.objs.indexOf(ob), 1);
  g2.fdizUsar.elegir(sc);
  igual(s.C.get("Accion").getAsString(), "profe", "después de la charla, F vuelve a ofrecer reclutarlo");
});

console.log(ok + " correctas, " + mal + " fallidas");
process.exit(mal ? 1 : 0);
