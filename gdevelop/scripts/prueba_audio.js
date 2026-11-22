// Pruebas de scripts/audio.js y de su conexión con el proyecto, sin GDevelop:  node gdevelop/scripts/prueba_audio.js
"use strict";
const fs = require("fs"), path = require("path"), vm = require("vm");

function variable(v) {
  let x = v;
  return { getAsNumber: () => Number(x) || 0, getAsString: () => String(x), setNumber: (n) => { x = n; }, setString: (s) => { x = s; }, getType: () => typeof x === "string" ? "string" : "number" };
}
function vars(init) { const V = {}; for (const k in init) V[k] = variable(init[k]); return { get: (n) => V[n] || (V[n] = variable(0)), _V: V }; }

// --- gestor de sonido parecido al de GDevelop (solo lo que usa el módulo)
class Sonido { constructor(nombre, esMusica, vol) { this.nombre = nombre; this.esMusica = esMusica; this.vol = vol; this.parado = false; } setVolume(v) { this.vol = Math.max(0, Math.min(1, v)); } stopped() { return this.parado; } }
class GestorSonido {
  constructor() { this._sounds = {}; this._musics = {}; this._freeSounds = []; this._freeMusics = []; this.log = []; }
  createHowlerSound(nombre, esMusica, vol) { return new Sonido(nombre, esMusica, vol); }
  playSound(n, loop, vol) { const s = this.createHowlerSound(n, false, vol / 100, loop, 1); this._freeSounds.push(s); this.log.push(s); return s; }
  playMusicOnChannel(n, ch, loop, vol) { if (this._musics[ch]) this._musics[ch].parado = true; const s = this.createHowlerSound(n, true, vol / 100, loop, 1); this._musics[ch] = s; return s; }
  clearAll() { for (const s of [...this._freeSounds, ...this._freeMusics, ...Object.values(this._musics)]) s.parado = true; this._musics = {}; this._freeSounds = []; }
}
const almacen = {};
const localStorage = { getItem: (k) => (k in almacen ? almacen[k] : null), setItem: (k, v) => { almacen[k] = String(v); } };
let padBotones = Array(16).fill(false), padEjes = [0, 0];
const navigator = { getGamepads: () => [{ buttons: padBotones.map((p) => ({ pressed: p })), axes: padEjes }] };
const gdjs = { HowlerSoundManager: GestorSonido };
vm.runInNewContext(fs.readFileSync(path.join(__dirname, "audio.js"), "utf8"), { gdjs, Math, JSON, Number, localStorage, navigator });
const A = gdjs.fdizAudio;

function juego(globales) {
  const sm = new GestorSonido();
  const input = { just: new Set(), soltado: false, cx: 0, cy: 0, wasKeyJustPressed(k) { return this.just.has(k); }, isMouseButtonReleased() { return this.soltado; }, getCursorX() { return this.cx; }, getCursorY() { return this.cy; } };
  return { sm, input, V: vars(Object.assign({ SonidoActivo: 1, VolMusica: 100, VolEfectos: 100 }, globales)), getVariables() { return this.V; }, getSoundManager() { return this.sm; }, getInputManager() { return this.input; } };
}
function escena(game, sv, instancias) {
  const textos = [], volver = { x: 920, y: 930, color: "", getX() { return this.x; }, getY() { return this.y; }, getWidth: () => 80, getHeight: () => 40, setColor(c) { this.color = c; } };
  const SV = vars(Object.assign({ Pausa: 0, PausaVista: 0 }, sv));
  return {
    game, textos, volver, SV, inst: instancias || [],
    getGame: () => game, getVariables: () => SV, getAdhocListOfAllInstances() { return this.inst; },
    getLayer: () => ({ convertCoords: (x, y) => [x, y] }),
    getObjects: (n) => (n === "TxtPausaB0" ? [volver] : []),
    createObject(n) {
      if (n === "VolDib") return { clear() {}, setOutlineSize() {}, setFillOpacity() {}, setFillColor() {}, drawRectangle() {}, setLayer() {}, setPosition() {}, setZOrder() {} };
      const t = { txt: "", oculto: false, setLayer() {}, hide(b) { this.oculto = b; }, setText(s) { this.txt = s; }, setCharacterSize() {}, setColor() {}, getWidth: () => 60, getHeight: () => 30, setPosition() {}, setZOrder() {} };
      textos.push(t); return t;
    },
  };
}
const video = (vol) => ({ v: vol, getVolume() { return this.v; }, setVolume(x) { this.v = Math.max(0, Math.min(100, x)); }, isPlayed: () => true });
const num = (g, n) => g.V.get(n).getAsNumber();
let ok = 0, mal = 0;
function prueba(nombre, f) { try { f(); ok++; console.log("  OK  ", nombre); } catch (e) { mal++; console.log("  MAL ", nombre, "->", e.message); } }
const igual = (a, b, m) => { if (Math.abs(a - b) > 1e-9) throw new Error((m || "") + ": " + a + " != " + b); };
const cierto = (c, m) => { if (!c) throw new Error(m); };
function cuadro(sc, teclas) { sc.game.input.just = new Set(teclas || []); A.aplicar(sc); A.pausa(sc); sc.game.input.just = new Set(); sc.game.input.soltado = false; }

prueba("En 100 % todo suena igual que antes", () => {
  const g = juego(); const sc = escena(g); A.aplicar(sc);
  const m = g.sm.playMusicOnChannel("musica/menu.ogg", 1, true, 45), s = g.sm.playSound("x", false, 60);
  igual(m.vol, 0.45, "música"); igual(s.vol, 0.6, "efecto");
});
prueba("Música 50 %: la que ya suena baja al momento y la nueva sale a la mitad; los efectos no cambian", () => {
  const g = juego(); const sc = escena(g); A.aplicar(sc);
  const m = g.sm.playMusicOnChannel("musica/menu.ogg", 1, true, 45);
  g.V.get("VolMusica").setNumber(50); A.aplicar(sc);
  igual(m.vol, 0.225, "música sonando"); igual(g.sm.playMusicOnChannel("musica/partida_1.ogg", 1, true, 45).vol, 0.225, "música nueva");
  igual(g.sm.playSound("x", false, 60).vol, 0.6, "efecto");
});
prueba("Efectos 30 %: los efectos nuevos salen al 30 % y la música no cambia", () => {
  const g = juego({ VolMusica: 100 }); const sc = escena(g); A.aplicar(sc);
  const m = g.sm.playMusicOnChannel("m", 1, true, 50);
  g.V.get("VolEfectos").setNumber(30); A.aplicar(sc);
  igual(g.sm.playSound("x", false, 60).vol, 0.18, "efecto"); igual(m.vol, 0.5, "música");
});
prueba("Valores siempre en 0..100 y en pasos de 10", () => {
  const g = juego({ VolMusica: 150, VolEfectos: -20 }); const sc = escena(g); A.aplicar(sc);
  igual(num(g, "VolMusica"), 100); igual(num(g, "VolEfectos"), 0);
  g.V.get("VolMusica").setNumber(47); A.aplicar(sc); igual(num(g, "VolMusica"), 50);
  A.cambiar(g, "musica", +100); A.aplicar(sc); igual(num(g, "VolMusica"), 100, "tope");
});
prueba("Cambiar de escena: la configuración sigue (globales) y la escena nueva la aplica desde el primer cuadro", () => {
  const g = juego(); const s1 = escena(g); A.aplicar(s1);
  g.V.get("VolMusica").setNumber(40); g.V.get("VolEfectos").setNumber(70); A.aplicar(s1);
  g.sm.clearAll();                                          // GDevelop detiene los sonidos al empezar la escena nueva
  const vid = video(12), s2 = escena(g, {}, [vid]); A.aplicar(s2);
  const m = g.sm.playMusicOnChannel("musica/menu.ogg", 1, true, 45);
  igual(m.vol, 0.18, "música de la escena nueva"); igual(vid.v, 12 * 0.4, "video de la escena nueva");
  igual(num(g, "VolMusica"), 40); igual(num(g, "VolEfectos"), 70);
});
prueba("Se guarda en el navegador y se recupera al abrir el juego otra vez", () => {
  cierto(JSON.parse(almacen[A.CLAVE]).m === 40, "guardado: " + almacen[A.CLAVE]);
  A._cargado = false;                                       // como si se abriera de nuevo
  const g = juego(); A.aplicar(escena(g));
  igual(num(g, "VolMusica"), 40); igual(num(g, "VolEfectos"), 70);
});
prueba("Nunca dos músicas: la del canal anterior se detiene al poner otra", () => {
  const g = juego(); const sc = escena(g); A.aplicar(sc);
  const a = g.sm.playMusicOnChannel("musica/menu.ogg", 1, true, 45), b = g.sm.playMusicOnChannel("musica/menu.ogg", 1, true, 45);
  cierto(a.parado && !b.parado, "la primera debe quedar detenida");
});
prueba("Videos: su audio sigue a la música sin perder su volumen base", () => {
  const g = juego({ VolMusica: 100 }); A._cargado = true; const v = video(3), sc = escena(g, {}, [v]); A.aplicar(sc);
  igual(v.v, 3); g.V.get("VolMusica").setNumber(50); A.aplicar(sc); igual(v.v, 1.5);
  g.V.get("VolMusica").setNumber(100); A.aplicar(sc); igual(v.v, 3, "vuelve a su base");
});

// ---------------- pantalla de pausa
function pausaAbierta(globales) { const g = juego(Object.assign({ VolMusica: 50, VolEfectos: 50 }, globales)); A._cargado = true; const sc = escena(g, { Pausa: 1, PausaVista: 2 }); cuadro(sc); return { g, sc }; }
prueba("Pantalla abierta: muestra SONIDO, MÚSICA y EFECTOS con su porcentaje", () => {
  const { sc } = pausaAbierta(); cuadro(sc);
  const t = sc.textos.filter((x) => !x.oculto).map((x) => x.txt);
  cierto(t.includes("SONIDO") && t.includes("▶ MÚSICA") && t.includes("EFECTOS") && t.filter((x) => x === "50 %").length === 2, t.join(" | "));
});
prueba("Teclado: → sube la música, ↓ y ← bajan efectos (con sonido de prueba), ↓ a VOLVER y Enter sale", () => {
  const { g, sc } = pausaAbierta();
  cuadro(sc, [39]); igual(num(g, "VolMusica"), 60, "→");
  cuadro(sc, [40]); cuadro(sc, [37]); igual(num(g, "VolEfectos"), 40, "←"); cierto(g.sm.log.some((s) => s.nombre === A.MUESTRA), "sin sonido de prueba");
  cuadro(sc, [83]); cuadro(sc, [13]); igual(sc.SV.get("PausaVista").getAsNumber(), 0, "salió");
});
prueba("Enter / A sobre MÚSICA no cierra (antes cualquier tecla cerraba); Retroceso sí", () => {
  const { sc } = pausaAbierta(); cuadro(sc, [13]); igual(sc.SV.get("PausaVista").getAsNumber(), 2, "Enter");
  cuadro(sc, [8]); igual(sc.SV.get("PausaVista").getAsNumber(), 0, "Retroceso");
});
prueba("Mando: cruceta derecha sube una vez por pulsación (mantenerla no repite)", () => {
  const { g, sc } = pausaAbierta();
  padBotones[15] = true; cuadro(sc); cuadro(sc); cuadro(sc); padBotones[15] = false; cuadro(sc);
  igual(num(g, "VolMusica"), 60);
  padEjes = [0, 0.9]; cuadro(sc); padEjes = [-0.9, 0]; cuadro(sc); padEjes = [0, 0]; cuadro(sc);
  igual(num(g, "VolEfectos"), 40, "stick abajo y luego izquierda");
});
prueba("Ratón: clic en +, clic en la barra (fija el valor) y clic en VOLVER", () => {
  const { g, sc } = pausaAbierta();
  Object.assign(g.input, { cx: 1198, cy: 832, soltado: true }); cuadro(sc); igual(num(g, "VolMusica"), 60, "+");
  Object.assign(g.input, { cx: 760 + 0.3 * 400, cy: 882, soltado: true }); cuadro(sc); igual(num(g, "VolEfectos"), 30, "barra");
  Object.assign(g.input, { cx: 722, cy: 882, soltado: true }); cuadro(sc); igual(num(g, "VolEfectos"), 20, "−");
  Object.assign(g.input, { cx: 950, cy: 945, soltado: true }); cuadro(sc); igual(sc.SV.get("PausaVista").getAsNumber(), 0, "VOLVER");
});
prueba("Fuera de esa pantalla no se dibuja nada", () => {
  const { sc } = pausaAbierta(); sc.SV.get("PausaVista").setNumber(0); cuadro(sc);
  cierto(sc.textos.every((t) => t.oculto), "quedan textos visibles");
});

// ---------------- proyecto
const d = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "FDI-Z", "FDI-Z.json"), "utf8"));
function* rec(l) { for (const e of l) { yield e; yield* rec(e.events || []); } }
prueba("Todas las escenas cargan audio.js y lo aplican antes que su música de inicio", () => {
  for (const L of d.layouts) {
    const ev = L.events;
    const iMod = ev.findIndex((e) => (e.inlineCode || "").startsWith("/*FDIZ-FASE57-MOD")), iApl = ev.findIndex((e) => (e.inlineCode || "").startsWith("/*FDIZ-FASE57-APLICAR"));
    cierto(iMod >= 0 && iApl === iMod + 1, L.name + ": falta el módulo o su aplicación");
    ev.forEach((e, i) => { if ([...rec([e])].some((x) => (x.actions || []).some((a) => a.type.value === "PlayMusicCanal")) && i <= iApl) throw new Error(L.name + ": música antes del módulo"); });
  }
});
prueba("«Elige el modo» (Menu) y la sala en línea ponen la música del menú al entrar, una sola vez", () => {
  for (const n of ["Menu", "Online"]) {
    const L = d.layouts.find((l) => l.name === n);
    const ev = [...rec(L.events)].filter((e) => (e.actions || []).some((a) => a.type.value === "PlayMusicCanal"));
    cierto(ev.length === 1, n + ": " + ev.length + " eventos de música");
    const c = ev[0].conditions.map((x) => x.type.value);
    cierto(c.includes("DepartScene") && ev[0].actions[0].parameters[1] === "musica/menu.ogg", n + ": " + JSON.stringify(ev[0]));
  }
});
prueba("Pausa: botón AJUSTES, pantalla CONTROLES Y SONIDO, que solo se cierra con B (o VOLVER / Retroceso)", () => {
  const J = d.layouts.find((l) => l.name === "Juego"), P = J.events.find((e) => e.name === "Menú de pausa").events;
  const acts = [...rec(P)].flatMap((e) => e.actions || []).map((a) => a.parameters.join("|"));
  cierto(acts.includes('TxtPausaB1|=|"AJUSTES"') && acts.includes('TxtPausaTit|=|"CONTROLES Y SONIDO"'), "textos");
  const cerrar = [...rec(P)].find((e) => (e.conditions || []).some((c) => c.parameters.join("|") === "PausaVista|=|2") && (e.actions || []).some((a) => a.parameters.join("|") === "PausaVista|=|0"));
  const subs = cerrar.conditions.find((c) => c.type.value.endsWith("Or")).subInstructions;
  cierto(subs.length === 4 && subs.every((s) => s.parameters[2] === '"B"'), "cierra con: " + subs.map((s) => s.parameters.join(",")).join(" ; "));
  cierto(J.objects.some((o) => o.name === "TxtVol") && J.objects.some((o) => o.name === "VolDib"), "objetos");
  cierto(["VolMusica", "VolEfectos"].every((n) => d.variables.some((v) => v.name === n && v.value === 100)), "globales");
});

console.log(ok + " correctas, " + mal + " fallidas");
process.exit(mal ? 1 : 0);
