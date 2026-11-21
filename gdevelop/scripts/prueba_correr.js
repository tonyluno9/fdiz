// Pruebas de scripts/correr.js sin GDevelop:  node gdevelop/scripts/prueba_correr.js
"use strict";
const fs = require("fs"), path = require("path"), vm = require("vm");

function variable(v) {
  let x = v;
  return { getAsNumber: () => Number(x), getAsString: () => String(x), setNumber: (n) => { x = n; }, setString: (s) => { x = s; } };
}
function sup(o) {
  const vars = {};
  const def = { Jugador: 1, Control: 0, Estado: "normal", Estamina: 15, Agotado: 0, Corre: 0, EstPausa: 0, NetSp: 0, Velocidad: 200, Rapidez: 1, Huye: 0, BotX: 100, BotY: 100, Usando: 0, Atacando: 0 };
  for (const k in def) vars[k] = variable(o && k in o ? o[k] : def[k]);
  const td = { max: 200, moving: true, setMaxSpeed(v) { this.max = v; }, getMaxSpeed() { return this.max; }, isMoving() { return this.moving; } };
  return {
    vars, td, anim: 1, hidden: false,
    getVariables: () => ({ get: (n) => vars[n] || (vars[n] = variable(0)), has: (n) => n in vars }),
    getRuntimeScene() { return this.escena; },
    getBehavior: () => td, setAnimationSpeedScale(s) { this.anim = s; }, isHidden() { return this.hidden; },
    getX: () => 100, getY: () => 100,
    base() { td.max = vars.Velocidad.getAsNumber() * vars.Rapidez.getAsNumber(); },   // el evento de MaxSpeed base
  };
}
function panel(j, x, y, oculto) {
  const vars = { Jugador: variable(j) };
  return { getVariables: () => ({ get: (n) => vars[n] }), isHidden: () => !!oculto, getX: () => x, getY: () => y, getWidth: () => 418, getHeight: () => 164 };
}
function escena(sups, paneles) {
  paneles = paneles || [panel(1, 20, 16), panel(2, 1482, 16, true), panel(3, 20, 900, true), panel(4, 1482, 900, true)];
  const teclas = new Set();
  let dt = 1000 / 60, t = 0;
  const dib = { rects: 0, r: [], clear() { this.rects = 0; this.r = []; }, setOutlineSize() {}, setFillOpacity() {}, setFillColor() {},
                drawRectangle(a, b, c, d) { this.rects++; this.r.push([a, b, c, d]); },
                setLayer() {}, setPosition() {}, setZOrder() {} };
  const capa = { convertInverseCoords: (x, y) => [x, y], convertCoords: (x, y) => [x, y] };
  return {
    teclas, dib, setDt(ms) { dt = ms; },
    zombis: [],
    getObjects(n) { return n === "HudPanel" ? paneles : n === "Sup" ? sups : (n.startsWith("Z") ? this.zombis : []); },
    getTimeManager: () => ({ getElapsedTime: () => dt, getTimeFromStart: () => t }),
    getGame: () => ({ getInputManager: () => ({ isKeyPressed: (k) => teclas.has(k) }) }),
    createObject: () => dib, getLayer: () => capa,
    paso() { t += dt; for (const s of sups) s.escena = this; for (const s of sups) s.base(); gdjs.fdizCorrer.mover(this); gdjs.fdizCorrer.dibujar(this); },
  };
}

const gdjs = {};
// mando 1 (Control 1) desconectado; mando 2 (Control 2) con LB apretado
const nav = { getGamepads: () => [null, { buttons: Array.from({ length: 16 }, (_, i) => ({ pressed: i === 4 })) }] };
vm.runInNewContext(fs.readFileSync(path.join(__dirname, "correr.js"), "utf8"), { gdjs, navigator: nav, Math });
const K = gdjs.fdizCorrer.CFG;
let ok = 0, mal = 0;
function prueba(nombre, f) { try { f(); ok++; console.log("  OK  ", nombre); } catch (e) { mal++; console.log("  MAL ", nombre, "->", e.message); } }
const igual = (a, b, m) => { if (Math.abs(a - b) > 1e-6) throw new Error(m + ": " + a + " != " + b); };
const cierto = (c, m) => { if (!c) throw new Error(m); };
const seg = (sc, s) => { for (let i = 0; i < Math.round(s * 60); i++) sc.paso(); };

prueba("Sin Shift: velocidad normal, estamina llena", () => {
  const a = sup(); const sc = escena([a]); seg(sc, 1);
  igual(a.td.max, 200, "velocidad"); igual(a.vars.Estamina.getAsNumber(), 15, "estamina");
});
prueba("Barra en el HUD: bajo el panel de P1 (arriba) y sobre el de P3 (abajo); nada si el panel está oculto", () => {
  const a = sup({ Jugador: 1 }), b = sup({ Jugador: 3 }), c = sup({ Jugador: 2 });
  const sc = escena([a, b, c], [panel(1, 20, 16), panel(3, 20, 900), panel(2, 1482, 16, true)]); seg(sc, 0.1);
  const marcos = sc.dib.r.filter((r) => r[0] === 20 + 4 - 3);   // marco de cada barra (x del panel + margen - 3)
  igual(marcos.length, 2, "dos barras (P2 oculto)");
  const yP1 = marcos.find((r) => r[1] < 540), yP3 = marcos.find((r) => r[1] > 540);
  igual(yP1[1], 16 + 164 + 8 - 3, "P1: justo debajo del panel"); igual(yP3[3], 900 - 8 + 3, "P3: justo encima del panel");
  cierto(sc.dib.r.every((r) => r[0] >= 20 && r[2] <= 20 + 418), "dentro del ancho del panel");
});
prueba("Shift izq. (1016): corre x1.5, gasta 3/s y se ve la barra", () => {
  const a = sup(); const sc = escena([a]); sc.teclas.add(1016); seg(sc, 2);
  igual(a.td.max, 200 * K.factor, "velocidad"); igual(a.vars.Estamina.getAsNumber(), 15 - 2 * K.gasto, "estamina");
  igual(a.anim, K.anim, "animación");
});
prueba("Con la barra llena dura 5 s; luego agotado y vuelve a velocidad normal", () => {
  const a = sup(); const sc = escena([a]); sc.teclas.add(2016); seg(sc, 5.2);
  igual(a.vars.Estamina.getAsNumber(), 0, "vacía"); igual(a.vars.Agotado.getAsNumber(), 1, "agotado"); igual(a.td.max, 200, "velocidad"); igual(a.anim, 1, "animación");
});
prueba("Agotado: aunque mantenga Shift no corre hasta juntar 5 (no se puede spamear)", () => {
  const a = sup(); const sc = escena([a]); sc.teclas.add(1016); seg(sc, 5.2);
  seg(sc, K.espera + 1);   // sigue con Shift: se recupera pero no corre
  igual(a.vars.Corre.getAsNumber(), 0, "no corre"); cierto(a.vars.Estamina.getAsNumber() < K.umbral, "aún bajo el umbral");
  seg(sc, 2);
  cierto(a.vars.Agotado.getAsNumber() === 0 || a.vars.Corre.getAsNumber() === 1, "con 5 vuelve a poder correr");
});
prueba("Se recupera 2.5/s después de 0.8 s sin correr; de 0 a 15 en ~6.8 s", () => {
  const a = sup(); const sc = escena([a]); sc.teclas.add(1016); seg(sc, 5.2); sc.teclas.clear();
  seg(sc, 0.5); igual(a.vars.Estamina.getAsNumber(), 0, "en la pausa no recupera");
  seg(sc, 6.4); igual(a.vars.Estamina.getAsNumber(), 15, "llena"); igual(a.vars.Agotado.getAsNumber(), 0, "ya no agotado");
});
prueba("Toques cortos no reinician: cada toque gasta y la espera de recuperación vuelve a empezar", () => {
  const a = sup(); const sc = escena([a]);
  for (let i = 0; i < 6; i++) { sc.teclas.add(1016); seg(sc, 0.5); sc.teclas.clear(); seg(sc, 0.5); }
  igual(a.vars.Estamina.getAsNumber(), 15 - 6 * 0.5 * K.gasto, "solo gasta, nunca alcanzó a recuperar");
});
prueba("Quieto con Shift no gasta", () => {
  const a = sup(); a.td.moving = false; const sc = escena([a]); sc.teclas.add(1016); seg(sc, 2);
  igual(a.vars.Estamina.getAsNumber(), 15, "estamina"); igual(a.td.max, 200, "velocidad");
});
prueba("Pausa (tiempo 0): la estamina no cambia", () => {
  const a = sup(); const sc = escena([a]); sc.teclas.add(1016); seg(sc, 1); const e = a.vars.Estamina.getAsNumber();
  sc.setDt(0); seg(sc, 3); igual(a.vars.Estamina.getAsNumber(), e, "congelada");
});
prueba("Respeta la Rapidez de cada personaje (pasivas)", () => {
  const a = sup({ Rapidez: 1.2 }); const sc = escena([a]); sc.teclas.add(1016); seg(sc, 0.5);
  igual(a.td.max, 200 * 1.2 * K.factor, "velocidad");
});
prueba("Mando (Control 2, LB) corre; mando sin LB no", () => {
  const a = sup({ Control: 2 }), b = sup({ Control: 1 }); const sc = escena([a, b]); seg(sc, 1);
  igual(a.vars.Corre.getAsNumber(), 1, "Control 2 con LB"); igual(b.vars.Corre.getAsNumber(), 0, "Control 1 sin mando");
});
prueba("Jugador remoto en el host (Control -3) corre con NetSp", () => {
  const a = sup({ Control: -3, NetSp: 1 }); const sc = escena([a]); seg(sc, 1); igual(a.vars.Corre.getAsNumber(), 1, "corre");
});
prueba("Profes aliados (Jugador > 4) y caídos no corren", () => {
  const prof = sup({ Jugador: 5, Control: -1, BotX: 900 }), caido = sup({ Estado: "caido" });
  const sc = escena([prof, caido]); sc.teclas.add(1016); seg(sc, 1);
  for (const s of [prof, caido]) igual(s.vars.Corre.getAsNumber(), 0, "no corre");
});
prueba("Bot lejos de su meta corre y gasta estamina; cerca no; al llegar se detiene", () => {
  const lejos = sup({ Jugador: 2, Control: -1, BotX: 900 }), cerca = sup({ Jugador: 3, Control: -1, BotX: 150 });
  const sc = escena([lejos, cerca]); seg(sc, 1);
  igual(lejos.vars.Corre.getAsNumber(), 1, "lejos corre"); igual(cerca.vars.Corre.getAsNumber(), 0, "cerca camina");
  if (!(lejos.vars.Estamina.getAsNumber() < 14)) throw new Error("no gastó estamina");
  lejos.vars.BotX = variable(150); seg(sc, 0.2); igual(lejos.vars.Corre.getAsNumber(), 0, "llegó");
});
prueba("Cada bot (2, 3 y 4) corre al alejarse de SU distancia de parada y deja de correr al llegar a ella", () => {
  // distancias de parada del evento "Bots": 180 / 225 / 270 px. Los bots empiezan en x=100 y la meta se mueve en X.
  for (const [j, pare] of [[2, 180], [3, 225], [4, 270]]) {
    const b = sup({ Jugador: j, Control: -1, BotX: 100 + pare + 100 }); const sc = escena([b]);   // 100 px de exceso: no corre
    seg(sc, 0.3); igual(b.vars.Corre.getAsNumber(), 0, "bot " + j + " cerca no corre");
    b.vars.BotX = variable(100 + pare + 400); seg(sc, 0.3); igual(b.vars.Corre.getAsNumber(), 1, "bot " + j + " lejos corre");
    b.vars.BotX = variable(100 + pare + 10); seg(sc, 0.3); igual(b.vars.Corre.getAsNumber(), 0, "bot " + j + " llegó a su distancia y deja de correr");
  }
});
prueba("Bot con zombi cerca pelea (no corre) salvo que huya", () => {
  const b = sup({ Jugador: 2, Control: -1, BotX: 900 }); const sc = escena([b]);
  sc.zombis = [{ getVariables: () => ({ get: () => variable("persigue") }), getX: () => 200, getY: () => 100 }];
  seg(sc, 0.5); igual(b.vars.Corre.getAsNumber(), 0, "pelea");
  b.vars.Huye = variable(1); seg(sc, 0.5); igual(b.vars.Corre.getAsNumber(), 1, "huye corre");
});
prueba("Bot que se agota no vuelve a correr hasta recuperar el umbral", () => {
  const b = sup({ Jugador: 2, Control: -1, BotX: 99999, Estamina: 1 }); const sc = escena([b]);
  seg(sc, 1); igual(b.vars.Corre.getAsNumber(), 0, "con 1 no arranca (mínimo de inicio)");
  b.vars.Huye = variable(1); seg(sc, 1); igual(b.vars.Agotado.getAsNumber(), 1, "huyó hasta agotarse");
  b.vars.Huye = variable(0); seg(sc, 1); igual(b.vars.Corre.getAsNumber(), 0, "agotado");
});

console.log(ok + " correctas, " + mal + " fallidas");
process.exit(mal ? 1 : 0);
