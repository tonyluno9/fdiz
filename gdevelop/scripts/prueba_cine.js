// Pruebas de scripts/cine.js (fase 65): cinemáticas del modo Historia, sin GDevelop:  node gdevelop/scripts/prueba_cine.js
"use strict";
const fs = require("fs"), path = require("path"), vm = require("vm");
const PROY = path.join(__dirname, "..", "FDI-Z");
const d = JSON.parse(fs.readFileSync(path.join(PROY, "FDI-Z.json"), "utf8"));
const J = d.layouts.find((l) => l.name === "Juego");
let ok = 0, mal = 0;
function prueba(n, f) { try { f(); ok++; console.log("  OK   " + n); } catch (e) { mal++; console.log("  MAL  " + n + " -> " + e.message); } }
const igual = (a, b, m) => { if (JSON.stringify(a) !== JSON.stringify(b)) throw new Error((m || "") + ": " + JSON.stringify(a) + " != " + JSON.stringify(b)); };
const si = (c, m) => { if (!c) throw new Error(m || "falso"); };

// ---------------------------------------------------------------- mundo falso
function variable(x) { return { getAsNumber: () => Number(x) || 0, getAsString: () => String(x), setNumber: (n) => { x = n; }, setString: (s) => { x = s; } }; }
function cont(ini) { const V = {}; for (const k in ini || {}) V[k] = variable(ini[k]); return { V, get: (n) => V[n] || (V[n] = variable(0)), has: (n) => n in V }; }
function obj(nombre, x, y, vars) {
  const C = cont(vars);
  return { nombre, x, y, C, oculto: false, color: "", anim: "", vivo: true, getVariables: () => C, getX() { return this.x; }, getY() { return this.y; },
    setPosition(a, b) { this.x = a; this.y = b; }, setLayer() {}, setZOrder() {}, hide(b) { this.oculto = b; }, isHidden() { return this.oculto; },
    setColor(c) { this.color = c; }, setAnimationName(a) { this.anim = a; }, deleteFromScene(sc) { this.vivo = false; sc.objs.splice(sc.objs.indexOf(this), 1); },
    getWidth: () => 64, getHeight: () => 32 };
}
const sup = (j, ctl, o) => obj("Sup", 5100 + j * 60, 2528, Object.assign({ Jugador: j, Control: ctl, Estado: "normal", Init: 1, MovX: 1, Usando: 1, Personaje: "tony" }, o));
let reloj = 1000;
const teclas = new Set();
function hudObj(n, sc) {
  const o = obj(n, 0, 0, {});
  Object.assign(o, { txt: "", getString() { return this.txt; }, setText(s) { this.txt = s; }, setCharacterSize() {}, setWrapping() {}, setWrappingWidth() {},
    getWidth() { return 400; }, clear() { this.rects = []; }, setFillColor() {}, setFillOpacity() {}, setOutlineSize() {}, drawRectangle(...r) { (this.rects = this.rects || []).push(r); } });
  return o;
}
function videoObj(n, dur) {
  const o = obj(n, 0, 0, {});
  Object.assign(o, { t: 0, dur, jugando: false, play() { this.jugando = true; }, pause() { this.jugando = false; }, isEnded() { return this.dur > 0 && this.t >= this.dur; },
    getDuration() { return this.dur; }, getCurrentTime() { return this.t; }, setWidth() {}, setHeight() {}, setLoop() {}, setCurrentTime(x) { this.t = x; }, setVolume() {} });
  return o;
}
function mundo() {
  const musica = [], capa = [], sonidos = [];   // canal 1 = música de partida; canal 2 = la capa de encima (fase 66)
  const canal = (ch) => (ch === 2 ? capa : musica);
  const sound = { pauseMusicOnChannel: (s, ch) => canal(ch).push("pausa"), continueMusicOnChannel: (s, ch) => canal(ch).push("sigue"), playSound: (s, f) => sonidos.push(f) };
  const input = { isKeyPressed: (s, k) => teclas.has(k), isMouseButtonPressed: () => false };
  const gdjs = { evtTools: { sound, input } };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, "cine.js"), "utf8"), { gdjs, Math, Date, Map, Set, Number, String });
  gdjs.fdizCine.now = () => reloj;
  return { gdjs, C: gdjs.fdizCine, musica, capa, sonidos };
}
function escena(objs, sv, gl, videos) {
  const S = cont(Object.assign({ Estado: "juego", Pausa: 0, CineVid: 0, CineModo: "", CineSeq: 0, HistVistos: "", ProfJoel: "espera", ProfJustino: "espera", CamX: 0, CamY: 0 }, sv));
  const G = cont(Object.assign({ NetRol: 0, Modo: "historia", SonidoActivo: 1, VolEfectos: 100 }, gl));
  let escala = 1;
  const cam = { x: 0, y: 0 };
  const sc = { objs, S, G, videos: videos || {}, cam, getVariables: () => S, getGame: () => ({ getVariables: () => G }),
    getObjects: (n) => (/^VidHist/.test(n) && !(n in sc.videos) ? undefined : objs.filter((o) => o.nombre === n)),
    getTimeManager: () => ({ getTimeScale: () => escala, setTimeScale: (x) => { escala = x; } }), escala: () => escala,
    getLayer: () => ({ getCameraX: () => cam.x, getCameraY: () => cam.y, setCameraX: (x) => { cam.x = x; }, setCameraY: (y) => { cam.y = y; } }),
    createObject: (n) => {
      if (/^VidHist/.test(n)) { if (!(n in sc.videos)) return null; const v = videoObj(n, sc.videos[n]); objs.push(v); return v; }
      const o = ["CineDib", "TxtCine"].includes(n) ? hudObj(n) : obj(n, 0, 0, {}); objs.push(o); return o;
    } };
  return sc;
}
function base(extra) {
  return [sup(1, 0), sup(2, 1), sup(3, -1), obj("Puerta", 5792, 2976, { Id: "P06", Vida: 80 }), obj("Puerta", 5024, 768, { Id: "P59", Vida: 150 }),
    obj("ArmaPiso", 5136, 650, { Tipo: "escopeta" }), obj("ArmaPiso", 3400, 4470, { Tipo: "pistola" }), obj("ArmaPiso", 3328, 4400, { Tipo: "bate" }),
    obj("Profe", 3616, 2000, { Nombre: "joel" }), obj("Profe", 1936, 1668, { Nombre: "justino" })].concat(extra || []);
}
const cuadro = (w, sc, dt) => { reloj += dt === undefined ? 0.1 : dt; w.C.tick(sc); };
const correr = (w, sc, s) => { for (let t = 0; t < s; t += 0.1) cuadro(w, sc); };
const de = (sc, n) => sc.objs.filter((o) => o.nombre === n);
const modo = (sc) => sc.S.get("CineModo").getAsString();
function inicio(w, sc) {                                   // video 1 (o su tarjeta) + interludio, hasta devolver el control
  correr(w, sc, 0.5);
  for (let k = 0; k < 200 && modo(sc) !== ""; k++) cuadro(w, sc);
  for (let k = 0; k < 200 && (modo(sc) !== "" || sc.S.get("Estado").getAsString() !== "juego"); k++) cuadro(w, sc);
}

// ---------------------------------------------------------------- inicio de Historia
prueba("Inicio de Historia sin el video 1: el equipo en el salón, todo congelado y una tarjeta con lo que pasa", () => {
  const w = mundo(), sc = escena(base());
  correr(w, sc, 0.5);
  const [p1, p2, bot] = de(sc, "Sup");
  igual([modo(sc), sc.S.get("Estado").getAsString(), sc.escala(), [p1, p2, bot].map((s) => s.C.get("Control").getAsNumber()), p1.C.get("MovX").getAsNumber()],
    ["tarjeta", "cine", 0, [-2, -2, -1], 0]);
  igual([p1.x, p1.y], [5984 - 1.5 * 60, 3024], "en el salón");
  const t = de(sc, "TxtCine").map((x) => x.txt);
  si(t.includes("EL SALÓN") && t.some((s) => s.includes("alerta")), JSON.stringify(t));
  igual(w.musica, ["pausa"], "la música se pausa");
  igual(w.capa, ["pausa"], "la capa de la música (canal 2) también");
});
prueba("Después del video 1: interludio corto (la puerta empieza a romperse) y el control vuelve; armas guardadas", () => {
  const w = mundo(), sc = escena(base());
  correr(w, sc, 0.5);
  correr(w, sc, 3.6);                                       // termina la tarjeta
  igual(modo(sc), "interludio");
  const zs = de(sc, "ZNormal");
  igual([zs.length, zs.map((z) => z.C.get("Estado").getAsString())], [2, ["cinematica", "cinematica"]]);
  correr(w, sc, 3.5);
  const p06 = de(sc, "Puerta").find((p) => p.C.get("Id").getAsString() === "P06");
  igual(w.sonidos.filter((s) => s.includes("puerta_golpe")).length, 3, "tres golpes");
  igual([p06.C.get("Vida").getAsNumber(), p06.color], [50, "255;255;255"], "dañada, no rota");
  igual([modo(sc), sc.S.get("Estado").getAsString(), sc.escala(), de(sc, "Sup").map((s) => s.C.get("Control").getAsNumber())], ["", "juego", 1, [0, 1, -1]]);
  igual(zs.map((z) => z.C.get("Estado").getAsString()), ["persigue", "persigue"]);
  igual(de(sc, "ArmaPiso").map((a) => a.C.get("Tipo").getAsString()).sort(), ["bate", "escoba", "silla"], "escopeta y sheriff guardados; silla y escoba como en la intro");
  const [cas, caj] = de(sc, "Contenedor");
  igual([cas.x, cas.y, cas.oculto, caj.x, caj.y, caj.oculto], [5120, 596, false, 3328, 4436, true]);
  igual(w.musica, ["pausa", "sigue"], "la música vuelve");
  igual(w.capa, ["pausa", "sigue"], "y su capa");
});
prueba("Espera a que los jugadores tengan su control (Init) antes de congelar", () => {
  const w = mundo(), objs = base(); objs[0].C.get("Init").setNumber(0);
  const sc = escena(objs);
  correr(w, sc, 1); igual(modo(sc), "");
  objs[0].C.get("Init").setNumber(1); correr(w, sc, 0.5); igual(modo(sc), "tarjeta");
});
prueba("Con el video: se reproduce a pantalla completa, sin loop, y termina solo; saltarlo con Enter (no al instante)", () => {
  const w = mundo(), sc = escena(base(), {}, {}, { VidHist01: 6 });
  correr(w, sc, 0.5);
  igual(modo(sc), "video");
  const v = de(sc, "VidHist01")[0];
  si(v && v.jugando, "reproduciendo");
  v.t = 6; cuadro(w, sc);
  igual(modo(sc), "interludio", "terminó el video");
  si(!v.vivo, "se quita el video");
  const w2 = mundo(), sc2 = escena(base(), {}, {}, { VidHist01: 60 });
  teclas.add("Return"); correr(w2, sc2, 0.5); teclas.delete("Return");
  correr(w2, sc2, 0.3); igual(modo(sc2), "video", "la tecla que ya estaba apretada no salta");
  teclas.add("Return"); cuadro(w2, sc2); teclas.delete("Return");
  igual(modo(sc2), "interludio", "Enter salta");
});
prueba("Video que no carga: a los 4 s sigue la historia (no se queda trabado)", () => {
  const w = mundo(), sc = escena(base(), {}, {}, { VidHist01: 0 });
  correr(w, sc, 0.5); igual(modo(sc), "video");
  correr(w, sc, 4.2); igual(modo(sc), "interludio");
});

// ---------------------------------------------------------------- momentos
function enJuego() { const w = mundo(), sc = escena(base()); inicio(w, sc); w.musica.length = 0; return [w, sc]; }
prueba("Joel: al entrar a los Cubículos del CIC (una sola vez)", () => {
  const [w, sc] = enJuego(), p1 = de(sc, "Sup")[0];
  p1.x = 3600; p1.y = 2000; cuadro(w, sc);
  igual([modo(sc), sc.S.get("CineVid").getAsNumber()], ["tarjeta", 2]);
  correr(w, sc, 4); igual(modo(sc), "");
  p1.x = 3000; correr(w, sc, 0.3); p1.x = 3600; correr(w, sc, 0.5);
  igual(modo(sc), "", "no se repite al volver a entrar");
});
prueba("Teléfono del CIC: al completarse la llamada (la computadora desaparece)", () => {
  const [w, sc] = enJuego(), o = obj("Objetivo", 3136, 1760, { Tipo: "computadora", Hecho: 0 });
  sc.objs.push(o); correr(w, sc, 0.3);
  o.deleteFromScene(sc); cuadro(w, sc);
  igual([modo(sc), sc.S.get("CineVid").getAsNumber()], ["tarjeta", 3]);
});
prueba("Conserje: al abrir o derribar su puerta (P59)", () => {
  const [w, sc] = enJuego();
  de(sc, "Puerta").find((p) => p.C.get("Id").getAsString() === "P59").deleteFromScene(sc); cuadro(w, sc);
  igual([modo(sc), sc.S.get("CineVid").getAsNumber()], ["tarjeta", 4]);
});
prueba("Casillero de la conserjería y cajón del director: al abrirlos, video y aparece el arma en su lugar", () => {
  const [w, sc] = enJuego(), [cas, caj] = de(sc, "Contenedor");
  cas.C.get("Abierto").setNumber(1); cuadro(w, sc);
  igual(sc.S.get("CineVid").getAsNumber(), 5);
  correr(w, sc, 4);
  const esc = de(sc, "ArmaPiso").find((a) => a.C.get("Tipo").getAsString() === "escopeta");
  igual([esc.x, esc.y, esc.anim], [5136, 650, "escopeta"]);
  caj.C.get("Abierto").setNumber(1); cuadro(w, sc);
  igual(sc.S.get("CineVid").getAsNumber(), 7);
  correr(w, sc, 4);
  const pis = de(sc, "ArmaPiso").find((a) => a.C.get("Tipo").getAsString() === "pistola");
  igual([pis.x, pis.y], [3400, 4470]);
  correr(w, sc, 2); igual(de(sc, "ArmaPiso").filter((a) => a.C.get("Tipo").getAsString() === "escopeta").length, 1, "una sola escopeta");
});
prueba("Justino: al llegar a la nevería junto a él (antes de abrir el diálogo de reclutar)", () => {
  const [w, sc] = enJuego(), p1 = de(sc, "Sup")[0];
  p1.x = 1580; p1.y = 1700; cuadro(w, sc); igual(modo(sc), "", "en la nevería pero lejos de Justino");
  p1.x = 1900; p1.y = 1700; cuadro(w, sc);
  igual(sc.S.get("CineVid").getAsNumber(), 6);
});
prueba("Canepa (misión 5): con el video, el video reemplaza la charla y al terminar cumple la misión (sigue la gasolina)", () => {
  const w = mundo(), sc = escena(base(), {}, {}, { VidHist08: 5 });
  inicio(w, sc);
  si(w.C.toma(sc), "canepa.js deja que lo haga el video");
  sc.S.get("CanepaCharla").setNumber(1); cuadro(w, sc);
  igual([modo(sc), sc.S.get("CineVid").getAsNumber()], ["video", 8]);
  de(sc, "VidHist08")[0].t = 5; cuadro(w, sc);
  igual([sc.S.get("CanepaCharla").getAsNumber(), sc.S.get("Paso").getAsNumber(), sc.S.get("Estado").getAsString()], [2, 99, "juego"]);
  const w2 = mundo(), sc2 = escena(base());
  inicio(w2, sc2);
  si(!w2.C.toma(sc2), "sin el video: la charla con burbujas de la fase 61");
  sc2.S.get("CanepaCharla").setNumber(1); cuadro(w2, sc2);
  igual(modo(sc2), "", "cine.js no la toca");
});
prueba("Mientras corre una cinemática no empieza otra, y en pausa no se detectan", () => {
  const [w, sc] = enJuego(), p1 = de(sc, "Sup")[0];
  sc.S.get("Pausa").setNumber(1); p1.x = 3600; p1.y = 2000; correr(w, sc, 0.5); igual(modo(sc), "");
  sc.S.get("Pausa").setNumber(0); cuadro(w, sc); igual(sc.S.get("CineVid").getAsNumber(), 2);
  de(sc, "Puerta").find((p) => p.C.get("Id").getAsString() === "P59").deleteFromScene(sc); cuadro(w, sc);
  igual(sc.S.get("CineVid").getAsNumber(), 2, "sigue la de Joel");
  correr(w, sc, 4); cuadro(w, sc);
  igual(sc.S.get("CineVid").getAsNumber(), 4, "después, la del conserje");
});
prueba("Fuera de Historia no hace nada (Escape, Jefe)", () => {
  const w = mundo(), sc = escena(base(), {}, { Modo: "escape" });
  correr(w, sc, 2);
  igual([modo(sc), sc.S.get("Estado").getAsString(), de(sc, "ArmaPiso").length, de(sc, "Contenedor").length], ["", "juego", 3, 0]);
});
prueba("En línea: el cliente no decide, pero muestra el video o la tarjeta que manda el host y pausa su música", () => {
  const w = mundo(), sc = escena(base(), { CineModo: "video", CineVid: 2, CineSeq: 4, Estado: "cine" }, { NetRol: 2 }, { VidHist02: 9 });
  correr(w, sc, 1);
  si(de(sc, "VidHist02").length === 1 && de(sc, "VidHist02")[0].jugando, "video");
  igual([de(sc, "Contenedor").length, w.musica], [0, ["pausa"]]);
  sc.S.get("CineModo").setString(""); sc.S.get("CineVid").setNumber(0); cuadro(w, sc);
  igual([de(sc, "VidHist02").length, w.musica], [0, ["pausa", "sigue"]]);
});

// ---------------------------------------------------------------- proyecto
const rec = function* (evs) { for (const e of evs || []) { yield e; yield* rec(e.events); } };
prueba("Proyecto: la intro de Escape no arranca en Historia (su contenido no cambia)", () => {
  const cin = J.events.find((e) => (e.name || "").startsWith("Cinemática de inicio"));
  const ini = cin.events.find((x) => (x.actions || []).some((a) => a.type.value === "ModVarSceneTxt" && a.parameters[2] === '"intro"'));
  si(ini.conditions.some((c) => c.type.value === "VarGlobalTxt" && c.parameters.join("|") === 'Modo|!=|"historia"'));
  si(ini.conditions.some((c) => c.type.value === "VarGlobalTxt" && c.parameters.join("|") === 'Modo|!=|"jefe"'), "lo de antes sigue");
});
prueba("Proyecto: cine.js arriba, su tick tras la cinemática de inicio; variables en la red; objetos de la tarjeta; carpeta y LEEME", () => {
  const top = J.events.map((e) => (e.inlineCode || "").slice(0, 22));
  const cin = J.events.findIndex((e) => (e.name || "").startsWith("Cinemática de inicio"));
  si(top.some((s) => s.startsWith("/*FDIZ-FASE65-MOD")) && top[cin + 1].startsWith("/*FDIZ-FASE65-TICK"));
  const T = d.layouts.find((l) => l.name === "Titulo");
  const n = [...rec(T.events)].find((e) => (e.inlineCode || "").includes("gdjs.fdizNetCfg="));
  const cfg = JSON.parse(n.inlineCode.match(/gdjs\.fdizNetCfg=(\{[\s\S]*?\});\n/)[1]);
  for (const v of ["CineVid", "CineModo", "CineSeq", "HistVistos"]) si(cfg.sv.includes(v), v);
  si(J.objects.some((o) => o.name === "CineDib") && J.objects.some((o) => o.name === "TxtCine"));
  const dir = path.join(PROY, "assets", "interfaz", "videos", "historia");
  si(fs.existsSync(path.join(dir, "LEEME.txt")), "LEEME");
  for (let k = 1; k <= 8; k++) {
    const hay = fs.readdirSync(dir).some((f) => f.startsWith("historia_0" + k + "_") && f.toLowerCase().endsWith(".mp4"));
    const objeto = J.objects.some((o) => o.name === "VidHist0" + k), recurso = d.resources.resources.find((r) => r.name === "vid_historia_0" + k);
    igual([objeto, !!recurso], [hay, hay], "video " + k + " registrado solo si existe");
    if (recurso) si(recurso.kind === "video" && recurso.file.startsWith("assets/interfaz/videos/historia/"), "ruta relativa");
  }
  const can = [...rec(J.events)].find((e) => (e.inlineCode || "").startsWith("/*FDIZ-FASE61-MOD")).inlineCode;
  si(can.includes("gdjs.fdizCine.toma(scn)"), "canepa.js pregunta al video");
});

console.log(ok + " correctas, " + mal + " fallidas");
process.exit(mal ? 1 : 0);
