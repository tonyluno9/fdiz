// Pruebas de scripts/usar.js y de su conexión con los eventos, sin GDevelop:  node gdevelop/scripts/prueba_usar.js
"use strict";
const fs = require("fs"), path = require("path"), vm = require("vm");

function variable(v) {
  let x = v;
  return { getAsNumber: () => Number(x) || 0, getAsString: () => String(x), setNumber: (n) => { x = n; }, setString: (s) => { x = s; } };
}
function obj(nombre, x, y, vars, w, h) {
  const V = {};
  for (const k in vars || {}) V[k] = variable(vars[k]);
  return {
    nombre, x, y, w: w || 40, h: h || 40, V, hidden: false, _livingOnScene: true,
    getVariables() { return { get: (n) => V[n] || (V[n] = variable(0)) }; },
    getX() { return this.x; }, getY() { return this.y; }, getWidth() { return this.w; }, getHeight() { return this.h; },
    getDrawableX() { return this.x - this.w / 2; }, getDrawableY() { return this.y - this.h; }, getCenterX() { return this.w / 2; }, getCenterY() { return this.h / 2; },
    isHidden() { return this.hidden; },
  };
}
const sup = (j, x, y, o) => obj("Sup", x, y, Object.assign({ Jugador: j, Control: 0, Estado: "normal", Usando: 0, Mordido: 0, Revivir: 0, Cura: 0, Personaje: "tony" }, o), 40, 96);
const puerta = (x, y, o) => obj("Puerta", x, y, Object.assign({ TiempoAbrir: 1, Progreso: 0, Tipo: "normal" }, o), 32, 64);

function escena(objs) {
  const textos = [];
  const capa = { convertInverseCoords: (x, y) => [x, y], convertCoords: (x, y) => [x, y] };
  const SV = { Estado: variable("juego"), Pausa: variable(0), ProfDlg: variable(0) };
  const sc = {
    objs, textos,
    getObjects: (n) => objs.filter((o) => o.nombre === n && o._livingOnScene),
    getLayer: () => capa, getVariables: () => ({ get: (n) => SV[n] || variable(0) }),
    createObject(n) {
      if (n === "UsarDib") return { clear() {}, setOutlineSize() {}, setFillOpacity() {}, setFillColor() {}, drawRectangle() {}, setLayer() {}, setPosition() {}, setZOrder() {} };
      const t = { txt: "", oculto: false, setLayer() {}, hide(b) { this.oculto = b; }, setText(s) { this.txt = s; }, setTextAlignment() {}, setColor() {},
                  setPosition() {}, setZOrder() {}, getWidth: () => 100, getHeight: () => 20 };
      textos.push(t); return t;
    },
  };
  return sc;
}
const gdjs = {};
vm.runInNewContext(fs.readFileSync(path.join(__dirname, "usar.js"), "utf8"), { gdjs, Math, Map, Set });
const U = gdjs.fdizUsar;
const n = (o, k) => o.getVariables().get(k).getAsNumber(), s_ = (o, k) => o.getVariables().get(k).getAsString();
const banderas = (o) => ["UsaPuerta", "UsaRevivir", "UsaCurar", "UsaObjetivo", "UsaCofre"].filter((k) => n(o, k) === 1);
let ok = 0, mal = 0;
function prueba(nombre, f) { try { f(); ok++; console.log("  OK  ", nombre); } catch (e) { mal++; console.log("  MAL ", nombre, "->", e.message); } }
const igual = (a, b, m) => { if (JSON.stringify(a) !== JSON.stringify(b)) throw new Error((m || "") + ": " + JSON.stringify(a) + " != " + JSON.stringify(b)); };
const visibles = (sc) => sc.textos.filter((t) => !t.oculto).map((t) => t.txt);

prueba("Junto a una puerta sin mantener F: indicación «Mantén F para abrir», nada avanza", () => {
  const p1 = sup(1, 100, 200), pu = puerta(84, 140); const sc = escena([p1, pu]);
  U.elegir(sc); U.dibujar(sc);
  igual(banderas(p1), [], "banderas"); igual(visibles(sc), ["Mantén F para abrir"]);
});
prueba("Mantener F junto a la puerta: solo UsaPuerta y esa puerta elegida", () => {
  const p1 = sup(1, 100, 200, { Usando: 1 }), pu = puerta(84, 140), otra = puerta(600, 140); const sc = escena([p1, pu, otra]);
  U.elegir(sc);
  igual(banderas(p1), ["UsaPuerta"]); igual([n(pu, "Elegida"), n(otra, "Elegida")], [1, 0]);
});
prueba("Puerta y compañero caído a la vez: elige UNO (salvar pesa más) y nunca los dos", () => {
  // puerta a 78 px (78/130 = 0.60) y caído a 60 px (60/80 x 0.75 = 0.56): las dos al alcance, gana salvar
  const p1 = sup(1, 100, 200, { Usando: 1 }), pu = puerta(84, 90), p2 = sup(2, 160, 200, { Estado: "caido" }); const sc = escena([p1, pu, p2]);
  U.elegir(sc); U.dibujar(sc);
  igual(banderas(p1), ["UsaRevivir"]); igual(n(pu, "Elegida"), 0, "puerta"); igual(visibles(sc), ["Mantén F para salvar a P2"]);
});
prueba("La puerta mucho más cerca que el caído: abre la puerta (la más cercana)", () => {
  const p1 = sup(1, 100, 200, { Usando: 1 }), pu = puerta(84, 168), p2 = sup(2, 178, 200, { Estado: "caido" }); const sc = escena([p1, pu, p2]);
  U.elegir(sc);
  igual(banderas(p1), ["UsaPuerta"]);
});
prueba("Mientras mantiene F conserva lo elegido aunque otra cosa quede más cerca", () => {
  const p1 = sup(1, 100, 200, { Usando: 1 }), pu = puerta(84, 168), p2 = sup(2, 250, 200, { Estado: "caido" }); const sc = escena([p1, pu, p2]);
  U.elegir(sc); igual(banderas(p1), ["UsaPuerta"]);
  p2.x = 130; U.elegir(sc);
  igual(banderas(p1), ["UsaPuerta"], "sigue con la puerta");
});
prueba("Terminó de abrir con F mantenida: no empieza a salvar hasta soltar F", () => {
  const p1 = sup(1, 100, 200, { Usando: 1 }), pu = puerta(84, 168), p2 = sup(2, 160, 200, { Estado: "caido" }); const sc = escena([p1, pu, p2]);
  U.elegir(sc); igual(banderas(p1), ["UsaPuerta"]);
  pu._livingOnScene = false;                         // la puerta se abrió (se borra)
  U.elegir(sc); U.dibujar(sc);
  igual(banderas(p1), [], "esperando a soltar"); igual(visibles(sc), ["Suelta F para la siguiente acción"]);
  p1.getVariables().get("Usando").setNumber(0); U.elegir(sc);
  p1.getVariables().get("Usando").setNumber(1); U.elegir(sc);
  igual(banderas(p1), ["UsaRevivir"], "nueva pulsación");
});
prueba("Alejarse mientras mantiene F: deja de avanzar (el evento pone el progreso en 0)", () => {
  const p1 = sup(1, 100, 200, { Usando: 1 }), pu = puerta(84, 168); const sc = escena([p1, pu]);
  U.elegir(sc); igual(banderas(p1), ["UsaPuerta"]);
  p1.x = 400; U.elegir(sc);
  igual(banderas(p1), []); igual(n(pu, "Elegida"), 0);
});
prueba("Puerta restringida (TiempoAbrir 0): no se abre con F, avisa que es a golpes", () => {
  const p1 = sup(1, 100, 200, { Usando: 1 }), pu = puerta(84, 168, { TiempoAbrir: 0, Tipo: "restringida" }); const sc = escena([p1, pu]);
  U.elegir(sc); U.dibujar(sc);
  igual(banderas(p1), []); igual(visibles(sc), ["Puerta restringida: derríbala a golpes"]);
});
prueba("Puerta electrónica: indica el tiempo; con tarjeta (1 s) dice solo «abrir»", () => {
  const p1 = sup(1, 100, 200), pu = puerta(84, 168, { TiempoAbrir: 8, Tipo: "electronica" }); const sc = escena([p1, pu]);
  U.elegir(sc); igual(s_(p1, "UsarTxt"), "abrir (electrónica, 8 s)");
  pu.getVariables().get("TiempoAbrir").setNumber(1); U.elegir(sc); igual(s_(p1, "UsarTxt"), "abrir");
});
prueba("Compañero mordido: «Mantén F para curar a P3» y solo UsaCurar", () => {
  const p1 = sup(1, 100, 200, { Usando: 1 }), p3 = sup(3, 150, 200, { Mordido: 1 }); const sc = escena([p1, p3]);
  U.elegir(sc); U.dibujar(sc);
  igual(banderas(p1), ["UsaCurar"]); igual(visibles(sc), ["Mantén F para curar a P3"]);
});
prueba("Mando (Control 2): «Mantén A para …»; jugador remoto (-3) elige pero no se dibuja en el host", () => {
  const p2 = sup(2, 100, 200, { Control: 2 }), p3 = sup(3, 900, 200, { Control: -3, Usando: 1 }), pu = puerta(84, 168), pr = puerta(884, 168);
  const sc = escena([p2, p3, pu, pr]);
  U.elegir(sc); U.dibujar(sc);
  igual(visibles(sc), ["Mantén A para abrir"]); igual(banderas(p3), ["UsaPuerta"]);
});
prueba("Bots: como antes (todas sus banderas = Usando y todas las puertas a su alcance)", () => {
  const b = sup(2, 100, 200, { Control: -1, Usando: 1 }), pu = puerta(84, 168), p4 = sup(4, 150, 200, { Estado: "caido" }); const sc = escena([b, pu, p4]);
  U.elegir(sc); U.dibujar(sc);
  igual(banderas(b), ["UsaPuerta", "UsaRevivir", "UsaCurar", "UsaObjetivo", "UsaCofre"]); igual(n(pu, "Elegida"), 1); igual(visibles(sc), []);
});
prueba("Objetivo: «Mantén F para llamar»; el camión del final no se ofrece", () => {
  const p1 = sup(1, 100, 200, { Usando: 1 }), g = obj("Objetivo", 150, 200, { Tipo: "computadora", Tiempo: 20, Hecho: 0, Progreso: 5 }, 31, 32);
  const fin = obj("Objetivo", 90, 200, { Tipo: "camion", Tiempo: 9999, Hecho: 0 }, 64, 64); const sc = escena([p1, g, fin]);
  U.elegir(sc);
  igual(banderas(p1), ["UsaObjetivo"]); igual(s_(p1, "UsarTxt"), "llamar"); igual([n(g, "Elegida"), n(fin, "Elegida")], [1, 0]); igual(n(p1, "UsarProg"), 0.25);
});
prueba("Locker: «revisar» con UsaCofre; uno ya abierto no se ofrece", () => {
  const p1 = sup(1, 100, 200, { Usando: 1 }), l = obj("Contenedor", 120, 200, { Abierto: 0, Progreso: 0 }), ab = obj("Contenedor", 100, 210, { Abierto: 1 });
  const sc = escena([p1, l, ab]); U.elegir(sc);
  igual(banderas(p1), ["UsaCofre"]); igual(s_(p1, "UsarTxt"), "revisar");
});
prueba("Profe esperando más cerca: la acción es «profe» (su propio diálogo), sin otras banderas", () => {
  const p1 = sup(1, 100, 200, { Usando: 1 }), pr = obj("Profe", 140, 200, { Estado: "espera" }), pu = puerta(84, 90); const sc = escena([p1, pr, pu]);
  U.elegir(sc);
  igual(s_(p1, "Accion"), "profe"); igual(banderas(p1), []); igual(U.permite(p1, "profe"), true);
  pu.y = 168; pr.x = 210; U.elegir(sc);
  igual(s_(p1, "Accion"), "puerta"); igual(U.permite(p1, "profe"), false, "F es para la puerta");
});
prueba("Caído o fuera de juego: no interactúa ni muestra indicación", () => {
  const p1 = sup(1, 100, 200, { Usando: 1, Estado: "caido" }), pu = puerta(84, 168); const sc = escena([p1, pu]);
  U.elegir(sc); U.dibujar(sc); igual(banderas(p1), []); igual(visibles(sc), []);
});

// ---------------- conexión con los eventos del proyecto
const d = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "FDI-Z", "FDI-Z.json"), "utf8"));
const J = d.layouts.find((l) => l.name === "Juego");
function* rec(l) { for (const e of l) { yield e; yield* rec(e.events || []); } }
const grupo = (n) => J.events.find((e) => e.name === n).events;
const conds = (e) => (e.conditions || []).map((c) => [c.type.value].concat(c.parameters).join("|"));
prueba("Eventos: las puertas solo con F/A (sin R ni R remoto), UsaPuerta y la puerta elegida", () => {
  const fe = [...rec(grupo("Mapa: choques y puertas"))].find((e) => e.type.endsWith("ForEach") && e.object === "Puerta");
  const cs = fe.events.map(conds).flat();
  if (cs.some((c) => c.startsWith("KeyPressed") || c.includes("NetDr") || c.includes("Sup|Usando"))) throw new Error("queda R o Usando: " + cs.join(" ; "));
  if (!cs.includes("VarObjet|Sup|UsaPuerta|=|1") || !cs.includes("VarObjet|Puerta|Elegida|=|1")) throw new Error(cs.join(" ; "));
});
prueba("Eventos: levantar usa J<n>Rev, curar J<n>Cur; soltar o alejarse deja el avance en 0", () => {
  const v = [...rec(grupo("Vida, caída y revivir"))].map(conds).flat(), m = [...rec(grupo("Compañeros mordidos: salvar o no salvar"))].map(conds).flat();
  if (v.some((c) => /J\dUsa/.test(c)) || m.some((c) => /J\dUsa/.test(c))) throw new Error("queda J<n>Usa");
  if (v.filter((c) => /J\dRev\|=\|1/.test(c)).length !== 4 || m.filter((c) => /J\dCur\|=\|1/.test(c)).length !== 12) throw new Error("faltan Rev/Cur");
  const dec = [...rec(grupo("Vida, caída y revivir"))].flatMap((e) => e.actions || []).find((a) => a.parameters[1] === "Revivir" && a.parameters[2] === "=" && a.parameters[3] !== "0" && a.parameters[3] !== "Sup.Variable(VidaMax) * 0.5");
  if (dec) throw new Error("el avance aún baja poco a poco: " + dec.parameters[3]);
});
prueba("Eventos: objetivos con UsaObjetivo + Objetivo.Elegida; lockers con UsaCofre", () => {
  const o = [...rec(grupo("Objetivos y flecha"))].map(conds).flat(), l = [...rec(grupo("Lockers, mochilas, máquinas y dinero"))].map(conds).flat();
  if (!o.includes("VarObjet|Sup|UsaObjetivo|=|1") || !o.includes("VarObjet|Objetivo|Elegida|=|1") || o.some((c) => c.includes("Sup|Usando"))) throw new Error("objetivos");
  if (!l.includes("VarObjet|Sup|UsaCofre|=|1") || l.some((c) => c.includes("Sup|Usando"))) throw new Error("lockers");
});
prueba("Textos de controles del menú de pausa (teclado y mando) actualizados", () => {
  const t = [...rec(grupo("Menú de pausa"))].flatMap((e) => e.actions || []).filter((a) => a.type.value === "TextObject::String" && /TxtPausaCtl[12]/.test(a.parameters[0])).map((a) => a.parameters[2]);
  // la fase 49 (cesar) cambió esos textos por imágenes y los dejó vacíos: vale vacío o el texto nuevo, nunca el viejo
  const vacios = t.length > 0 && t.every((s) => s === '""');
  if (!vacios && (!t.some((s) => s.includes("F (mantener)  abrir puertas, salvar,")) || !t.some((s) => s.includes("A (mantener)  abrir puertas, salvar,")))) throw new Error(t.join("\n"));
  if (t.some((s) => s.includes("usar puertas, cofres"))) throw new Error("queda el texto viejo");
});
prueba("profes.js incrustado: el diálogo pregunta a fdizUsar y curar a un profe usa UsaCurar", () => {
  const m = J.events.find((e) => (e.inlineCode || "").startsWith("/*FDIZ-FASE40-MOD"));
  if (!m.inlineCode.includes('gdjs.fdizUsar.permite(h.s, "profe")') || !m.inlineCode.includes('"UsaCurar"')) throw new Error("profes.js sin actualizar");
});
prueba("Llaves (medios.js de cesar): con el árbitro solo suma quien tiene elegido el objetivo; el resto se deshace", () => {
  const m = J.events.find((e) => (e.inlineCode || "").startsWith("/*FDIZ-FASE46-MOD"));
  if (!m || !m.inlineCode.includes('num(s, "UsaObjetivo") === 1')) throw new Error("medios.js sin actualizar en el proyecto");
  const g2 = { fdizUsar: U };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, "medios.js"), "utf8"), { gdjs: g2, Math, Map, Set, Date });
  const M = g2.fdizMedios;
  const llaves = obj("Objetivo", 500, 500, { Tipo: "llaves", Progreso: 0, Usada: 0, Tiempo: 2, Elegida: 0 });
  const p1 = sup(1, 520, 500, { Usando: 1, UsaObjetivo: 0 });
  const sc = escena([p1, llaves]);
  M.llaves(sc, [llaves]);                            // primera vuelta: fija el progreso de referencia (0)
  llaves.V.Progreso.setNumber(0.5);                  // la suma vino de otra parte: a P1 la F le tocaba otra cosa
  M.llaves(sc, [llaves]);
  igual(n(llaves, "Progreso"), 0, "sin elegir: se deshace");
  p1.V.UsaObjetivo.setNumber(1); llaves.V.Elegida.setNumber(1); llaves.V.Progreso.setNumber(0.5);
  M.llaves(sc, [llaves]);
  igual(n(llaves, "Progreso"), 0.5, "elegido: cuenta");
});

console.log(ok + " correctas, " + mal + " fallidas");
process.exit(mal ? 1 : 0);
