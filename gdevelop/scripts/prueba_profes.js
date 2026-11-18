/* Banco de pruebas de scripts/profes.js (sin GDevelop). Uso: node gdevelop/scripts/prueba_profes.js
 * Simula lo mínimo del motor (objetos, variables, capas, entrada, tiempo y red) y ejecuta los casos de la Fase 40.
 * No prueba los eventos de GDevelop (combate, navegación, colisiones): eso queda para la vista previa. */
"use strict";
const fs = require("fs"), path = require("path"), vm = require("vm");

// ------------------------------------------------------------------ motor simulado
class Var {
  constructor(v) { this.v = v === undefined ? 0 : v; }
  getAsNumber() { return typeof this.v === "number" ? this.v : Number(this.v) || 0; }
  getAsString() { return String(this.v); }
  setNumber(n) { this.v = n; } setString(s) { this.v = s; } add(n) { this.v = this.getAsNumber() + n; }
  getType() { return typeof this.v === "string" ? "string" : "number"; }
}
class Vars {
  constructor(o) { this.m = {}; for (const k in o || {}) this.m[k] = new Var(o[k]); }
  get(n) { return this.m[n] || (this.m[n] = new Var(0)); } has(n) { return n in this.m; }
}
const DEF = {
  Sup: { Personaje: "tony", Jugador: 1, Control: 0, Init: 0, Vida: 120, VidaMax: 120, Velocidad: 204, Fuerza: 1, Estado: "normal", Arma: "puños",
    MovX: 0, MovY: 0, QuierePegar: 0, Usando: 0, PideHab: 0, PideEsp: 0, QuiereLanzar: 0, Mordido: 0, Cura: 0, Curando: 0, Golpeado: 0, Ayuda: 0,
    ComidaCura: 0, Atacando: 0, BotX: 0, BotY: 0, Huye: 0, Revivir: 0, Init12: 0, CdOk: 0 },
  Profe: { Nombre: "", Estado: "espera", Progreso: 0, Vida: 100 },
  ZJoel: { Tipo: "profe_joel", Vida: 250, VidaMax: 250, Danio: 12, Velocidad: 84, Estado: "persigue", DifOk: 0 },
  ZNormal: { Tipo: "normal", Vida: 30, VidaMax: 30, Danio: 5, Velocidad: 99, Estado: "paseando", DifOk: 0 },
};
DEF.ZJustino = Object.assign({}, DEF.ZJoel, { Tipo: "profe_justino" }); DEF.ZCanepa = Object.assign({}, DEF.ZJoel, { Tipo: "profe_canepa" });
let ESC; // escena actual
class Obj {
  constructor(name, scn) {
    this.name = name; this.scn = scn; this.x = 0; this.y = 0; this.layer = ""; this.anim = ""; this.hidden = false; this.op = 255; this.z = 0;
    this.vars = new Vars(DEF[name]); this.timers = {}; this.text = ""; this.color = "255;255;255"; this.flip = false; this.moving = false;
  }
  getName() { return this.name; } getX() { return this.x; } getY() { return this.y; } setPosition(x, y) { this.x = x; this.y = y; } setX(x) { this.x = x; } setY(y) { this.y = y; }
  setLayer(l) { this.layer = l; } getLayer() { return this.layer; } getAnimationName() { return this.anim; } setAnimationName(a) { this.anim = a; }
  hide(h) { this.hidden = !!h; } isHidden() { return this.hidden; } getOpacity() { return this.op; } setOpacity(o) { this.op = o; }
  setZOrder(z) { this.z = z; } getZOrder() { return this.z; } setColor(c) { this.color = c; } flipX(f) { this.flip = !!f; }
  getVariables() { return this.vars; } getWidth() { return this.name === "Niebla" ? this.w : Math.max(10, this.text.length * 10); } getHeight() { return this.name === "Niebla" ? this.h : 24; }
  deleteFromScene() { const a = this.scn.objs[this.name]; const i = a.indexOf(this); if (i >= 0) a.splice(i, 1); this.deleted = true; }
  resetTimer(n) { this.timers[n] = 0; } getTimerElapsedTimeInSeconds(n) { return this.timers[n] || 0; }
  getBehavior(n) { const o = this; return n === "TopDownMovement" ? { isMoving: () => o.moving } : null; }
  setWidth(w) { this.w = w; } setHeight(h) { this.h = h; }
  setText(t) { this.text = t; } getText() { return this.text; } setCharacterSize() {} setWrapping() {} setWrappingWidth() {} setTextAlignment() {}
  clear() { this.rects = []; } setFillColor() {} setOutlineSize() {} drawRectangle(a, b, c, d) { (this.rects = this.rects || []).push([a, b, c, d]); }
}
const teclas = new Set(); let mouse = false; let pads = [null, null, null, null]; let T = 0;
const GVAR = new Vars({ NetRol: 0, SonidoActivo: 1, DifDanio: 1 });
function escena() {
  const s = {
    objs: {}, timeScale: 1, dt: 1 / 60,
    vars: new Vars({ ProfJoel: "espera", ProfJustino: "espera", ProfCanepa: "espera", ProfJoelSeg: 0, ProfJustinoSeg: 0, ProfCanepaSeg: 0, ProfDlg: 0,
      Estado: "juego", Pausa: 0, Rescatados: 0, Banner: "", BannerSeg: 0, FinalActivo: 0,
      J1Ok: 1, J2Ok: 1, J3Ok: 1, J4Ok: 1, M1: 0, M2: 0, M3: 0, M4: 0, J1X: 0, J1Y: 0, J2X: 0, J2Y: 0, J3X: 0, J3Y: 0, J4X: 0, J4Y: 0 }),
    getObjects(n) { return this.objs[n] || (this.objs[n] = []); },
    createObject(n) { const o = new Obj(n, this); this.getObjects(n).push(o); return o; },
    getVariables() { return this.vars; },
    getGame() { return { getVariables: () => GVAR, getInputManager: () => IM }; },
    getLayer(n) { const s3 = this; return { isVisible: () => true, convertCoords: (x, y) => [x, y],
      convertInverseCoords: (x, y) => { const c = s3.getObjects("Sup")[0] || { x: 960, y: 540 }; return [x - c.x + 960, y - c.y + 540]; } }; },
    getElapsedTime() { return this.dt * 1000 * this.timeScale; },
    getTimeManager() { const s2 = this; return { setTimeScale: (k) => { s2.timeScale = k; }, getTimeFromStart: () => T * 1000 }; },
  };
  return s;
}
const IM = { isKeyPressed: (c) => teclas.has(c), isMouseButtonPressed: () => mouse, getCursorX: () => 0, getCursorY: () => 0 };
const sonidos = [];
const ctx = { gdjs: { evtTools: { runtimeScene: { resetTimer() {} }, sound: { playSound: (s, f) => sonidos.push(f) } } },
  navigator: { getGamepads: () => pads }, performance: { now: () => T * 1000 }, console, Math, JSON };
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(path.join(__dirname, "profes.js"), "utf8"), ctx);
const API = ctx.gdjs.fdizProfes;

function nueva() {
  const s = escena(); ESC = s;
  const pos = { joel: [3616, 2000], justino: [1936, 1668], canepa: [544, 3328] };
  for (const k in pos) { const o = s.createObject("Profe"); o.setPosition(pos[k][0], pos[k][1]); o.vars.get("Nombre").setString(k); }
  for (let j = 1; j <= 4; j++) { const o = s.createObject("Sup"); o.setPosition(5000 + j * 60, 2528); o.vars.get("Jugador").setNumber(j); o.vars.get("Control").setNumber(j === 1 ? 0 : -1); }
  return s;
}
function paso(s, n) {
  for (let i = 0; i < (n || 1); i++) {
    T += s.dt;
    for (const k in s.objs) for (const o of s.objs[k]) for (const t in o.timers) o.timers[t] += s.dt * s.timeScale;
    for (const o of s.getObjects("Sup")) for (const v of ["MovX", "MovY", "Usando", "QuierePegar"]) o.vars.get(v).setNumber(0);
    for (const o of s.getObjects("Sup")) if (o.vars.get("Control").getAsNumber() === 0 && teclas.has(70)) o.vars.get("Usando").setNumber(1); // F = Usar
    API.input(s); API.bots(s); API.ayuda(s); API.mordidas(s);
    for (const o of s.getObjects("Sup")) o.vars.get("Golpeado").setNumber(0);
    API.tick(s);
  }
}
const seg = (s, n) => paso(s, Math.round(n * 60));
const P1 = (s) => s.getObjects("Sup").find((o) => o.vars.get("Jugador").getAsNumber() === 1);
const est = (s, n) => s.vars.get("Prof" + n).getAsString();
const sup = (s, j) => s.getObjects("Sup").filter((o) => o.vars.get("Jugador").getAsNumber() === j);
const textos = (s) => (s._fdizPf ? s._fdizPf.ui.a.filter((t) => !t.hidden).map((t) => t.text) : []);
function pulsar(s, codigo, t) { teclas.add(codigo); seg(s, t || 0.05); teclas.delete(codigo); seg(s, 0.2); }
function hablar(s, x, y) { P1(s).setPosition(x, y + 60); seg(s, 0.1); pulsar(s, 70); seg(s, 0.2); }

let ok = 0, mal = 0;
function prueba(nombre, fn) {
  try { fn(); console.log("  OK   " + nombre); ok++; } catch (e) { console.log("  FALLA " + nombre + "\n        " + e.message); mal++; }
}
function eq(a, b, m) { if (a !== b) throw new Error((m || "") + " esperado " + JSON.stringify(b) + ", obtuvo " + JSON.stringify(a)); }
function si(c, m) { if (!c) throw new Error(m); }

console.log("Fase 40 · profes.js");
prueba("1. Encontrarlo sin interactuar: se queda en su lugar, inmune y pide ayuda (con límite)", () => {
  const s = nueva(); const npc = s.getObjects("Profe")[0];
  P1(s).setPosition(3616, 2000 + 300); seg(s, 0.5);
  si(textos(s).some((t) => t.includes("¡Por aquí!")), "no se mostró la petición de ayuda");
  P1(s).setPosition(3616, 2000 + 90); seg(s, 60);
  eq(est(s, "Joel"), "espera"); eq(npc.x, 3616); eq(npc.y, 2000); eq(sup(s, 5).length, 0, "no debe ser aliado"); eq(s.getObjects("ZJoel").length, 0);
  si(textos(s).some((t) => t.includes("[F] Hablar con Joel")), "falta la indicación [F]");
  P1(s).setPosition(3616, 2300); const G = s._fdizPf.grito.joel; seg(s, 200); si(G.n <= 4, "repite demasiado: " + G.n);
});
prueba("2. Abrir y cerrar el diálogo conserva la espera (y no pausa con Esc)", () => {
  const s = nueva(); hablar(s, 3616, 2000);
  si(s._fdizPf.dlg, "no abrió el diálogo"); eq(est(s, "Joel"), "conversacion"); eq(s.timeScale, 0, "sin red la partida se detiene");
  si(textos(s).some((t) => t.includes("Ayudar y agregar al equipo")) && textos(s).some((t) => t.includes("Dejarlo aquí")), "faltan opciones");
  teclas.add(27); seg(s, 0.1); si(!s._fdizPf.dlg, "Esc no cerró"); eq(s.vars.get("ProfDlg").getAsNumber() !== 0, true, "la pausa debe seguir bloqueada mientras Esc está presionado");
  teclas.delete(27); paso(s, 1); eq(s.vars.get("ProfDlg").getAsNumber() !== 0, true, "el cuadro en que se suelta Esc no debe pausar"); seg(s, 0.1);
  eq(s.vars.get("ProfDlg").getAsNumber(), 0); eq(est(s, "Joel"), "espera"); eq(s.timeScale, 1); eq(s.getObjects("Profe").length, 3);
});
prueba("2b. El mismo botón que abre no confirma (mantener F no recluta)", () => {
  const s = nueva(); P1(s).setPosition(3616, 2060); seg(s, 0.1); teclas.add(70); seg(s, 2); teclas.delete(70); seg(s, 0.1);
  eq(est(s, "Joel"), "conversacion"); eq(sup(s, 5).length, 0);
});
prueba("3. Aceptar: aliado bot (Jugador 5) en el lugar del profe, cura al equipo una vez", () => {
  const s = nueva(); P1(s).vars.get("Vida").setNumber(50); hablar(s, 3616, 2000); pulsar(s, 70);
  eq(est(s, "Joel"), "aliado"); const a = sup(s, 5); eq(a.length, 1); eq(a[0].vars.get("Control").getAsNumber(), -1); eq(a[0].vars.get("Personaje").getAsString(), "joel");
  eq(a[0].x, 3616); eq(s.getObjects("Profe").length, 2); eq(s.vars.get("Rescatados").getAsNumber(), 1); eq(P1(s).vars.get("Vida").getAsNumber(), 80);
  eq(s.timeScale, 1); seg(s, 5); eq(s.vars.get("Rescatados").getAsNumber(), 1, "contador una sola vez");
  hablar(s, 3616, 2000); eq(sup(s, 5).length, 1, "no se puede reclutar dos veces");
});
prueba("4. Los tres reclutados con 4 principales: 7 Sup, panel compacto con 3 filas", () => {
  const s = nueva(); hablar(s, 3616, 2000); pulsar(s, 70); seg(s, 0.5); hablar(s, 1936, 1668); pulsar(s, 70); seg(s, 0.5); hablar(s, 544, 3328); pulsar(s, 70);
  eq(s.getObjects("Sup").length, 7); eq([5, 6, 7].map((j) => sup(s, j).length).join(), "1,1,1"); eq(s.vars.get("Rescatados").getAsNumber(), 3);
  const t = textos(s); si(["JOEL", "JUSTINO", "CANEPA"].every((n) => t.includes(n)), "faltan filas del panel: " + t.join("|"));
  si([1, 2, 3, 4].every((j) => sup(s, j).length === 1), "se perdió un principal");
});
prueba("5. Rechazar: consecuencia en el diálogo y cuenta individual de 30 s", () => {
  const s = nueva(); hablar(s, 3616, 2000); pulsar(s, 83); pulsar(s, 70);
  si(textos(s).some((t) => t.includes("30 segundos se convertirá en zombi")), "no avisa la consecuencia"); eq(est(s, "Joel"), "conversacion");
  pulsar(s, 87); pulsar(s, 70); eq(est(s, "Joel"), "rechazado"); si(s.vars.get("ProfJoelSeg").getAsNumber() > 29.5, "la cuenta no empezó en 30");
  eq(est(s, "Justino"), "espera"); eq(est(s, "Canepa"), "espera");
});
prueba("6. Pausar detiene la cuenta; alejarse no la detiene ni la reinicia; los golpes no la cambian", () => {
  const s = nueva(); hablar(s, 3616, 2000); pulsar(s, 83); pulsar(s, 70); pulsar(s, 87); pulsar(s, 70);
  const c0 = s.vars.get("ProfJoelSeg").getAsNumber();
  s.vars.get("Pausa").setNumber(1); s.timeScale = 0; seg(s, 10); eq(s.vars.get("ProfJoelSeg").getAsNumber(), c0, "avanzó en pausa");
  s.vars.get("Pausa").setNumber(0); s.timeScale = 1; P1(s).setPosition(100, 100); seg(s, 10);
  const c1 = s.vars.get("ProfJoelSeg").getAsNumber(); si(Math.abs(c0 - c1 - 10) < 0.1, "alejado: " + c0 + " -> " + c1);
  const z = s.createObject("ZNormal"); z.setPosition(3616 + 30, 2000); z.vars.get("Estado").setString("persigue"); seg(s, 5);
  const c2 = s.vars.get("ProfJoelSeg").getAsNumber(); si(Math.abs(c1 - c2 - 5) < 0.1, "los golpes cambiaron la cuenta");
  si(s.getObjects("Profe").find((o) => o.vars.get("Nombre").getAsString() === "joel").vars.get("Vida").getAsNumber() < 100, "sin inmunidad debería recibir golpes");
});
prueba("7. Conversión: exactamente un enemigo con la vida de ZConserje (escala de dificultad la aplica DifOk una vez)", () => {
  const s = nueva(); hablar(s, 3616, 2000); pulsar(s, 83); pulsar(s, 70); pulsar(s, 87); pulsar(s, 70); seg(s, 31);
  eq(est(s, "Joel"), "convertido"); eq(s.getObjects("ZJoel").length, 1); const z = s.getObjects("ZJoel")[0];
  eq(z.vars.get("Vida").getAsNumber(), 250); eq(z.vars.get("DifOk").getAsNumber(), 0); eq(z.vars.get("Estado").getAsString(), "persigue");
  eq(z.x, 3616); eq(s.getObjects("Profe").filter((o) => o.vars.get("Nombre").getAsString() === "joel").length, 0);
  seg(s, 20); eq(s.getObjects("ZJoel").length, 1, "se duplicó");
  si(textos(s).some((t) => t === "JOEL (ZOMBI)"), "sin identificación del profe convertido");
});
prueba("8a. Aliado mordido y curado por un compañero (3 s de Usar)", () => {
  const s = nueva(); hablar(s, 1936, 1668); pulsar(s, 70); const a = sup(s, 6)[0];
  const r = Math.random; ctx.Math.random = () => 0; a.vars.get("Golpeado").setNumber(1); API.mordidas(s); ctx.Math.random = r;
  eq(a.vars.get("Mordido").getAsNumber(), 1); seg(s, 0.1); eq(est(s, "Justino"), "mordido");
  P1(s).setPosition(a.x + 40, a.y); teclas.add(70); seg(s, 3.2); teclas.delete(70);
  eq(a.vars.get("Mordido").getAsNumber(), 0, "no se curó"); seg(s, 0.1); eq(est(s, "Justino"), "aliado");
});
prueba("8b. Aliado mordido sin cura: a los 35 s se convierte en su zombi", () => {
  const s = nueva(); hablar(s, 1936, 1668); pulsar(s, 70); const a = sup(s, 6)[0];
  a.vars.get("Mordido").setNumber(1); a.resetTimer("mordida"); P1(s).setPosition(0, 0); seg(s, 36);
  eq(est(s, "Justino"), "convertido"); eq(sup(s, 6).length, 0); eq(s.getObjects("ZJustino").length, 1);
});
prueba("8c. Aliado caído: un bot va a auxiliarlo; un profe de pie revive a un alumno caído", () => {
  const s = nueva(); hablar(s, 1936, 1668); pulsar(s, 70); const a = sup(s, 6)[0]; a.vars.get("Estado").setString("caido");
  const b = sup(s, 2)[0]; b.setPosition(a.x + 300, a.y); API.bots(s); si(b.vars.get("MovX").getAsNumber() < -0.9, "el bot no va hacia el profe");
  b.setPosition(a.x + 40, a.y); API.bots(s); eq(b.vars.get("Usando").getAsNumber(), 1);
  a.vars.get("Estado").setString("normal"); a.vars.get("Usando").setNumber(1); const c = sup(s, 3)[0]; c.vars.get("Estado").setString("caido"); c.setPosition(a.x + 50, a.y);
  c.vars.get("Ayuda").setNumber(0); API.ayuda(s); eq(c.vars.get("Ayuda").getAsNumber(), 1);
  a.vars.get("Estado").setString("fuera"); seg(s, 0.1); eq(est(s, "Justino"), "fuera"); eq(sup(s, 6).length, 0);
});
prueba("10. Decisiones simultáneas en línea: el host procesa una sola", () => {
  const s = nueva(); GVAR.get("NetRol").setNumber(1); const N = ctx.gdjs.fdizNet = { scn: s, started: true }; seg(s, 0.1);
  N.onProf("A", { k: "canepa", d: "abre" }); eq(est(s, "Canepa"), "conversacion");
  N.onProf("B", { k: "canepa", d: "acepta" }); eq(est(s, "Canepa"), "conversacion", "B no tenía el diálogo");
  N.onProf("A", { k: "canepa", d: "acepta" }); N.onProf("A", { k: "canepa", d: "acepta" }); N.onProf("B", { k: "canepa", d: "rechaza" });
  eq(est(s, "Canepa"), "aliado"); eq(sup(s, 7).length, 1); eq(s.vars.get("Rescatados").getAsNumber(), 1);
  // cliente: manda su decisión al host y no crea nada localmente
  const sc = nueva(); GVAR.get("NetRol").setNumber(2); const enviados = []; ctx.gdjs.fdizNet = { scn: sc, toHost: (o) => enviados.push(o) };
  hablar(sc, 3616, 2000); pulsar(sc, 70); eq(sup(sc, 5).length, 0); si(enviados.some((m) => m.t === "prof" && m.k === "joel" && m.d === "acepta"), "no mandó la decisión");
  const p = [{ s: 0, mx: 1, use: 1 }]; seg(sc, 0.5); hablar(sc, 1936, 1668); si(sc._fdizPf.dlg, "no abrió en el cliente"); ctx.gdjs.fdizNet.onLocalInput(sc, p); eq(p[0].mx, 0, "el cliente sigue moviéndose en el diálogo");
  GVAR.get("NetRol").setNumber(0); ctx.gdjs.fdizNet = undefined;
});
prueba("11. Final: Canepa aliado repara; rechazado o convertido -> el final sigue y no aparece otro Canepa", () => {
  const s = nueva(); hablar(s, 544, 3328); pulsar(s, 70); const c = sup(s, 7)[0]; c.setPosition(544, 3328);
  s.vars.get("FinalActivo").setNumber(1); seg(s, 0.1); si(s.vars.get("Banner").getAsString().includes("Canepa repara"), s.vars.get("Banner").getAsString());
  eq(c.anim, "canepa_pegar_lado");
  const s2 = nueva(); hablar(s2, 544, 3328); pulsar(s2, 83); pulsar(s2, 70); pulsar(s2, 87); pulsar(s2, 70); seg(s2, 31);
  s2.vars.get("FinalActivo").setNumber(1); seg(s2, 0.1); si(s2.vars.get("Banner").getAsString().includes("Reparen"), s2.vars.get("Banner").getAsString());
  eq(s2.getObjects("ZCanepa").length, 1); eq(s2.getObjects("Canepa").length, 0); eq(s2.getObjects("ZCanepa")[0].anim, "", "animaron al Canepa zombi");
});
prueba("12. Reiniciar (escena nueva) devuelve a los tres a su condición inicial", () => {
  const s = nueva(); hablar(s, 3616, 2000); pulsar(s, 70); const s2 = nueva(); seg(s2, 0.5);
  eq(["Joel", "Justino", "Canepa"].map((n) => est(s2, n)).join(), "espera,espera,espera"); eq(s2.getObjects("Profe").length, 3); eq(sup(s2, 5).length, 0);
  eq(s2.vars.get("Rescatados").getAsNumber(), 0); si(s2._fdizPf !== s._fdizPf, "el estado no es por escena");
});
prueba("Sala oscura: la petición no se dibuja sobre el profe, se avisa la zona", () => {
  const s = nueva(); const n = s.createObject("Niebla"); n.setPosition(3488, 1920); n.w = 256; n.h = 160;
  P1(s).setPosition(3616, 2000 + 350); seg(s, 0.5);
  si(textos(s).some((t) => t.startsWith("Alguien pide ayuda desde CÓMPUTO")), "no avisó la zona: " + textos(s).join("|"));
  si(!textos(s).some((t) => t === "«¡Por aquí! ¡Estoy en cómputo!»"), "dibujó la burbuja dentro de la sala oscura");
});
prueba("Mando: indicación (A), navegación con cruceta, B cierra", () => {
  const s = nueva(); const p1 = P1(s); p1.vars.get("Control").setNumber(1);
  const g = { axes: [0, 0], buttons: Array.from({ length: 16 }, () => ({ pressed: false })) }; pads = [g, null, null, null];
  p1.setPosition(3616, 2060); seg(s, 0.1); si(textos(s).some((t) => t.includes("(A) Hablar con Joel")), "falta (A)");
  g.buttons[0].pressed = true; seg(s, 0.05); g.buttons[0].pressed = false; seg(s, 0.05); si(s._fdizPf.dlg, "A no abrió");
  g.buttons[13].pressed = true; seg(s, 0.05); g.buttons[13].pressed = false; seg(s, 0.05); eq(s._fdizPf.dlg.sel, 1);
  g.buttons[1].pressed = true; seg(s, 0.05); g.buttons[1].pressed = false; seg(s, 0.05); si(!s._fdizPf.dlg, "B no cerró"); eq(est(s, "Joel"), "espera");
  pads = [null, null, null, null];
});
console.log(ok + " correctas, " + mal + " fallidas");
process.exitCode = mal ? 1 : 0;
