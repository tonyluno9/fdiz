// Pruebas con objetos simulados de scripts/medios.js (node scripts/prueba_medios.js). No usa GDevelop.
"use strict";
const fs = require("fs");
global.gdjs = { evtTools: { runtimeScene: { resetTimer() {} } } };
eval(fs.readFileSync(__dirname + "/medios.js", "utf8"));
const M = gdjs.fdizMedios;
let ok = 0, mal = 0;
const prueba = (n, f) => { try { f(); ok++; console.log("  OK  ", n); } catch (e) { mal++; console.log("  FALLA", n, "->", e.message); } };
const igual = (a, b, m) => { if (a !== b) throw new Error((m || "") + " esperado " + b + " y fue " + a); };
const variable = (v) => ({ v, getAsNumber() { return +this.v; }, getAsString() { return String(this.v); }, setNumber(x) { this.v = x; }, setString(x) { this.v = x; } });
function vars(o) { const m = {}; for (const k in o) m[k] = variable(o[k]); return { get: (k) => m[k] || (m[k] = variable(0)), has: (k) => k in m, m }; }
function sup(o) {
  const V = vars(Object.assign({ Personaje: "tony", Jugador: 1, Control: 0, Estado: "normal", Usando: 0 }, o.v || {}));
  const td = { mov: false, vx: 0, vy: 0, isMoving() { return this.mov; }, getXVelocity() { return this.vx; }, getYVelocity() { return this.vy; } };
  const s = { x: o.x || 0, y: o.y || 0, anim: "", flip: false, layer: "Juego", td, getVariables: () => V, getX() { return this.x; }, getY() { return this.y; },
    getBehavior: () => td, getAnimationName() { return this.anim; }, setAnimationName(n) { this.anim = n; this.cambios = (this.cambios || 0) + 1; },
    isFlippedX() { return this.flip; }, flipX(f) { this.flip = f; }, getLayer() { return this.layer; }, setLayer(l) { this.layer = l; } };
  return s;
}
const mueve = (s, vx, vy) => { s.td.mov = true; s.td.vx = vx; s.td.vy = vy; M.anim(null, [s]); };

prueba("Camina de lado, volteo según el signo y no reinicia la animación cada cuadro", () => {
  const s = sup({}); mueve(s, 200, 10); igual(s.anim, "tony_caminar_lado"); igual(s.flip, false);
  mueve(s, -200, 0); igual(s.flip, true, "izquierda"); const c = s.cambios; for (let i = 0; i < 20; i++) mueve(s, -200, 5); igual(s.cambios, c, "sin cambios de animación");
});
prueba("En diagonal (|vx| casi igual a |vy|) no salta entre lado y arriba/abajo", () => {
  const s = sup({}); mueve(s, 200, 150); igual(s.anim, "tony_caminar_lado");
  for (let i = 0; i < 30; i++) mueve(s, 150 + (i % 2) * 30, 160 - (i % 2) * 20);
  igual(s.anim, "tony_caminar_lado", "se queda en lado"); igual(s.cambios, 1, "una sola vez");
  mueve(s, 50, 220); igual(s.anim, "tony_caminar_abajo", "cambia cuando abajo domina");
});
prueba("Rozar una pared (vx casi 0) no voltea al personaje", () => {
  const s = sup({}); mueve(s, -200, 0); igual(s.flip, true); mueve(s, 3, 0); igual(s.flip, true, "vx diminuta");
});
prueba("Arriba, abajo y quieto", () => {
  const s = sup({}); mueve(s, 0, -200); igual(s.anim, "tony_caminar_arriba"); mueve(s, 0, 200); igual(s.anim, "tony_caminar_abajo");
  s.td.mov = false; M.anim(null, [s]); igual(s.anim, "tony_quieto"); igual(s.flip, false);
});
prueba("Personaje con otro nombre (tonyfuerte)", () => { const s = sup({ v: { Personaje: "tonyfuerte" } }); mueve(s, 100, 0); igual(s.anim, "tonyfuerte_caminar_lado"); });

function escena(sups, objetivos) {
  const V = vars({ Estado: "juego", Banner: "", BannerSeg: 0 });
  const txt = { t: "", setText(s) { this.t = s; } };
  return { sups, txt, V, getVariables: () => V, getObjects: (n) => (n === "Sup" ? sups : n === "TxtAyuda" ? [txt] : n === "Niebla" ? (escena.n || []) : []), getLayer: () => ({ isVisible: () => true }) };
}
function llave(prog) { const V = vars({ Tipo: "llaves", Progreso: prog || 0, Tiempo: 1, Usada: 0 }); return { x: 500, y: 500, getVariables: () => V, getX() { return this.x; }, getY() { return this.y; } }; }
prueba("Un bot cerca usando NO suma progreso a las llaves", () => {
  const b = sup({ x: 510, y: 500, v: { Control: -1, Usando: 1, Personaje: "alan", Jugador: 4 } }), o = llave(0), sc = escena([b]);
  o.getVariables().get("Progreso").setNumber(0.3); M.llaves(sc, [o]);   // simula que el evento suma 0.3
  igual(o.getVariables().get("Progreso").getAsNumber(), 0, "deshecho"); igual(o.getVariables().get("Usada").getAsNumber(), 0);
});
prueba("Un humano que mantiene F suma, se ve su nombre y al terminar sale el aviso", () => {
  const h = sup({ x: 510, y: 500, v: { Usando: 1, Personaje: "cesar", Jugador: 3 } }), o = llave(0), sc = escena([h]);
  M.llaves(sc, [o]); o.getVariables().get("Progreso").setNumber(0.5); M.llaves(sc, [o]);
  if (!/César \(P3\) toma las llaves/.test(sc.txt.t)) throw new Error("texto: " + sc.txt.t);
  o.getVariables().get("Progreso").setNumber(1.02); M.llaves(sc, [o]);
  igual(sc.V.get("Banner").getAsString(), "¡César (P3) tomó las llaves!");
});
prueba("Humano cerca sin pulsar: aviso de cómo tomarlas; bot cerca: no avisa", () => {
  const h = sup({ x: 600, y: 500 }), o = llave(0), sc = escena([h]);
  M.llaves(sc, [o]); if (!/mantén F/.test(sc.txt.t)) throw new Error(sc.txt.t);
  const b = sup({ x: 600, y: 500, v: { Control: -1 } }), sc2 = escena([b]); M.llaves(sc2, [llave(0)]); igual(sc2.txt.t, "", "sin aviso");
});
prueba("Capa del borde: estable, con histéresis y pies dentro de la sala = capa Juego", () => {
  const p = sup({ x: 1000, y: 1000 }); const sc = escena([p]); escena.n = [{ isHidden: () => false, getOpacity: () => 255, getX: () => 1020, getY: () => 800, getWidth: () => 300, getHeight: () => 300 }];
  const orig = sc.getObjects; sc.getObjects = (n) => (n === "Sup" ? [p] : n === "Niebla" ? escena.n : []);
  M.borde(sc); igual(p.layer, "Juego", "1.er cuadro aún no cambia"); M.borde(sc); igual(p.layer, "Juego"); M.borde(sc); igual(p.layer, "SupervivientesBorde", "al 3.º");
  p.x = 1100; p.y = 900; M.borde(sc); M.borde(sc); M.borde(sc); igual(p.layer, "Juego", "con los pies dentro de la sala vuelve a Juego");
});
console.log(mal ? mal + " fallidas" : ok + " correctas, 0 fallidas");
process.exit(mal ? 1 : 0);
