// Pruebas de scripts/avisos.js (fase 63): color de los letreros de eventos, sin GDevelop:  node gdevelop/scripts/prueba_avisos.js
"use strict";
const fs = require("fs"), path = require("path"), vm = require("vm");
const d = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "FDI-Z", "FDI-Z.json"), "utf8"));
const J = d.layouts.find((l) => l.name === "Juego");
let ok = 0, mal = 0;
function prueba(n, f) { try { f(); ok++; console.log("  OK   " + n); } catch (e) { mal++; console.log("  MAL  " + n + " -> " + e.message); } }
const igual = (a, b, m) => { if (JSON.stringify(a) !== JSON.stringify(b)) throw new Error((m || "") + ": " + JSON.stringify(a) + " != " + JSON.stringify(b)); };
const si = (c, m) => { if (!c) throw new Error(m || "falso"); };
const rec = function* (evs) { for (const e of evs || []) { yield e; yield* rec(e.events); } };
const gdjs = {};
vm.runInNewContext(fs.readFileSync(path.join(__dirname, "avisos.js"), "utf8"), { gdjs, String });
const A = gdjs.fdizAvisos;
const R = "rojo", V = "verde";
const cual = (t) => (A.esRojo(t) ? R : V);

// Todos los letreros que hoy pone el juego (Banner), con los números como «n». Si se agrega uno, hay que clasificarlo aquí.
const EVENTOS = {
  "": V,
  "¡Tarjeta! Las puertas electrónicas abren en 1 s": V,
  "¡SE FUE LA LUZ!": V,
  "NUEVO OBJETIVO": V,
  "OBJETIVO n/n · LLAMAR DESDE EL CIC": V,
  "OBJETIVO n/n · ¡SE FUE LA LUZ! INTERRUPTORES DEL CIC": V,
  "OBJETIVO n/n · LAS LLAVES DEL CONSERJE": V,
  "OBJETIVO n/n · COMIDA A LA NEVERÍA": V,
  "OBJETIVO n/n · HABLAR CON CANEPA EN EL CAMIÓN": V,
  "OBJETIVO n/n · BUSCAR LA GASOLINA": V,
  "¡AL ESTACIONAMIENTO!": V,
  "¡Servidor prendido! Ahora la llamada": V,
  "¡OBJETIVO CUMPLIDO!": V,
  "¡OBJETIVO n/n CUMPLIDO!": V,
  "¡AGUANTEN!": V,
  "¡ESCAPARON!": V,
  "¡FESTÍN! Los zombies van a la nevería": V,
  "Sabía a... facultad.": V,
  "Aquí no pueden pasar... excepto yo.": V,
  "¡LA FDI SE ESTÁ LLENANDO!": R,
  "¡Pn MORDIDO!": R,
  "¡P1 MORDIDO!": R,
  "¡P1 SALVADO!": V, "¡P2 SALVADO!": V, "¡P3 SALVADO!": V, "¡P4 SALVADO!": V,
  "¡P1 SE CONVIRTIÓ EN ZOMBIE!": R, "¡P2 SE CONVIRTIÓ EN ZOMBIE!": R, "¡P3 SE CONVIRTIÓ EN ZOMBIE!": R, "¡P4 SE CONVIRTIÓ EN ZOMBIE!": R,
};
// letreros de profes.js y medios.js (con un nombre de ejemplo) y el fragmento que debe existir en el código
const MODULOS = [
  ["¡Tony (P1) tomó las llaves!", V, "medios.js", " tomó las llaves!"],
  ["¡JOEL SE UNE AL EQUIPO! El equipo se cura", V, "profes.js", " SE UNE AL EQUIPO! El equipo se cura"],
  ["JUSTINO SE QUEDÓ ATRÁS", V, "profes.js", " SE QUEDÓ ATRÁS"],
  ["¡CANEPA SE CONVIRTIÓ EN ZOMBI!", R, "profes.js", " SE CONVIRTIÓ EN ZOMBI!"],
  ["JOEL QUEDÓ FUERA DE COMBATE", V, "profes.js", " QUEDÓ FUERA DE COMBATE"],
  ["¡JUSTINO SALVADO!", V, "profes.js", " SALVADO!"],
  ["¡AGUANTEN! Canepa repara el camión", V, "profes.js", "¡AGUANTEN! Canepa repara el camión"],
  ["¡AGUANTEN! Reparen el camión y resistan", V, "profes.js", "¡AGUANTEN! Reparen el camión y resistan"],
  ["¡JOEL MORDIDO!", R, "profes.js", " MORDIDO!"],
];

function textoDe(expr) {           // "¡P" + ToString(Sup.Variable(Jugador)) + " MORDIDO!"  ->  "¡Pn MORDIDO!"
  let s = expr;
  for (let k = 0; k < 4; k++) s = s.replace(/ToString\((?:[^()]|\((?:[^()]|\([^()]*\))*\))*\)/g, '"n"');
  return [...s.matchAll(/"((?:[^"\\]|\\.)*)"/g)].map((m) => m[1]).join("");
}

prueba("Letreros de los eventos del proyecto: todos clasificados (rojo solo infección y FDI llenándose)", () => {
  const vistos = new Set();
  for (const e of rec(J.events)) for (const a of e.actions || [])
    if (a.type.value === "ModVarSceneTxt" && a.parameters[0] === "Banner") vistos.add(textoDe(a.parameters[2]));
  const sinTabla = [...vistos].filter((t) => !(t in EVENTOS));
  igual(sinTabla, [], "letreros nuevos sin clasificar en la prueba");
  const malos = Object.entries(EVENTOS).filter(([t, c]) => cual(t) !== c).map(([t, c]) => t + " -> " + cual(t) + " (esperado " + c + ")");
  igual(malos, []);
});
prueba("Letreros de profes.js y medios.js: mismo criterio", () => {
  for (const [t, c, f, frag] of MODULOS) {
    si(fs.readFileSync(path.join(__dirname, f), "utf8").includes(frag), "ya no está en " + f + ": " + frag);
    igual(cual(t), c, t);
  }
});
prueba("Acentos, mayúsculas, espacios y variaciones no cambian la clasificación", () => {
  const rojos = ["¡p2 mordido!", "P3 MORDIDA", "  ¡P1   Mordido! ", "Canepa fue mordido", "¡P1 SE CONVIRTIO EN ZOMBI!", "se convirtió en zombie",
    "SE CONVIRTIERON EN ZOMBIES", "Gabo está infectado", "¡INFECTADA!", "la fdi se esta llenando", "¡LA FDI SE ESTA LLENANDO!", "La FDI   se está llenando de zombies"];
  const verdes = ["¡FESTIN! los zombies van a la neveria", "Los zombis rompieron la puerta", "¡P1 salvado de la mordida!", "Curado: ya no está mordido",
    "Habitación desinfectada", "¡Objetivo 3/6 cumplido!", "la fdi ya no se está llenando", "MORDIDÍSIMO no es una palabra", "Zombificado no aplica a FDIs"];
  igual(rojos.filter((t) => !A.esRojo(t)), [], "debían ser rojos");
  igual(verdes.filter((t) => A.esRojo(t) && !/zombificado/i.test(t)), [], "debían ser verdes");
  igual([A.color("¡P1 MORDIDO!"), A.color("¡ESCAPARON!")], ["255;80;80", "110;230;110"]);
});
prueba("aplicar(): pone el color del texto que se ve y solo lo recalcula si cambia", () => {
  let veces = 0;
  const t = { s: "¡LA FDI SE ESTÁ LLENANDO!", col: "", getString() { return this.s; }, setColor(c) { this.col = c; veces++; } };
  const sc = { getObjects: (n) => (n === "TxtBanner" ? [t] : []) };
  A.aplicar(sc); igual(t.col, A.ROJO);
  A.aplicar(sc); A.aplicar(sc); igual(veces, 1, "mismo texto: no se vuelve a pintar");
  t.s = "¡OBJETIVO 2/6 CUMPLIDO!"; A.aplicar(sc); igual(t.col, A.VERDE);
});
prueba("Proyecto: TxtBanner verde por defecto, avisos.js arriba de Juego y el color al mostrar el letrero (grupo HUD)", () => {
  const o = J.objects.find((x) => x.name === "TxtBanner");
  igual([o.content.color, o.color], ["110;230;110", { r: 110, g: 230, b: 110 }]);
  si(J.events.some((e) => (e.inlineCode || "").startsWith("/*FDIZ-FASE63-MOD")), "módulo");
  const ev = [...rec(J.events)].filter((e) => (e.actions || []).some((a) => a.type.value === "TextObject::String" && a.parameters[0] === "TxtBanner"));
  igual(ev.length, 1);
  si((ev[0].events || []).some((x) => (x.inlineCode || "").startsWith("/*FDIZ-FASE63-COLOR")), "color al mostrar");
  si(J.events.find((e) => (e.inlineCode || "").startsWith("/*FDIZ-FASE63-MOD")).inlineCode.includes(fs.readFileSync(path.join(__dirname, "avisos.js"), "utf8").trim().slice(0, 200)), "código al día");
});
prueba("Los textos no cambian (mismos letreros que antes de la fase 63)", () => {
  const glob = fs.readdirSync(path.join(__dirname, "..", "respaldos")).filter((f) => f.startsWith("antes_de_fase63_")).sort();
  if (!glob.length) return;
  const viejo = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "respaldos", glob[0]), "utf8")).layouts.find((l) => l.name === "Juego");
  const lista = (L) => [...rec(L.events)].flatMap((e) => e.actions || []).filter((a) => a.type.value === "ModVarSceneTxt" && a.parameters[0] === "Banner").map((a) => a.parameters.join("|"));
  igual(lista(J), lista(viejo));
});

console.log(ok + " correctas, " + mal + " fallidas");
process.exit(mal ? 1 : 0);
