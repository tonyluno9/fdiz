// Pruebas de scripts/sfx.js (fase 60) y de su conexión con el proyecto, sin GDevelop:  node gdevelop/scripts/prueba_sfx.js
"use strict";
const fs = require("fs"), path = require("path"), vm = require("vm");
const RAIZ = path.join(__dirname, "..", "..");
const d = JSON.parse(fs.readFileSync(path.join(RAIZ, "gdevelop", "FDI-Z", "FDI-Z.json"), "utf8"));
let ok = 0, mal = 0;
function prueba(n, f) { try { f(); ok++; console.log("  OK   " + n); } catch (e) { mal++; console.log("  MAL  " + n + " -> " + e.message); } }
const igual = (a, b, m) => { if (JSON.stringify(a) !== JSON.stringify(b)) throw new Error((m || "") + ": " + JSON.stringify(a) + " != " + JSON.stringify(b)); };
const si = (c, m) => { if (!c) throw new Error(m || "falso"); };

// ---------------------------------------------------------------- mundo falso
function variable(x) {
  return { getAsNumber: () => Number(x) || 0, getAsString: () => String(x), setNumber: (n) => { x = n; }, setString: (s) => { x = s; }, getValue: () => x };
}
function cont(ini) {
  const V = {};
  for (const k in ini || {}) V[k] = variable(ini[k]);
  return { V, get: (n) => V[n] || (V[n] = variable(0)), has: (n) => n in V };
}
function obj(nombre, x, y, vars, an) {
  const C = cont(vars);
  return { nombre, x, y, an: an || "", C, w: 100, h: 50, vis: true,
    getVariables: () => C, getX() { return this.x; }, getY() { return this.y; }, getWidth() { return this.w; }, getHeight() { return this.h; },
    getAnimationName() { return this.an; }, getLayer: () => "HUD", isVisible() { return this.vis; }, getOpacity: () => 255 };
}
const sup = (j, pj, x, y, o) => obj("Sup", x, y, Object.assign({ Jugador: j, Personaje: pj, Control: 0, Estado: "normal", Vida: 100, Arma: "puños", Lanz: "",
  ComidaCura: 0, Usando: 0, Accion: "", ArmaFuego: 0 }, o), pj + "_quieto");
const zombi = (n, tipo, x, y, o) => obj(n, x, y, Object.assign({ Tipo: tipo, Vida: 30, Estado: "persigue", Aliado: 0 }, o), "caminar_abajo");

let reloj = 1000, azar = [];
const raton = { x: 0, y: 0, suelta: false };
function mundo() {
  const sonado = [], red = [];
  const sound = {
    playSound: (scn, f, loop, vol, p) => { red.push(f); sonado.push({ f, loop, vol, p }); },
  };
  sound._orig = (scn, f, loop, vol, p) => sonado.push({ f, loop, vol, p });
  const gdjs = { evtTools: { sound, input: {
    getMouseX: () => raton.x, getMouseY: () => raton.y, isMouseButtonReleased: () => raton.suelta } } };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, "sfx.js"), "utf8"), { gdjs, Math, Date });
  const X = gdjs.fdizSfx;
  X.now = () => reloj;
  X.rnd = () => (azar.length ? azar.shift() : 0.5);
  return { gdjs, X, sonado, red };
}
function escena(nombre, objs, sv, gl) {
  const S = cont(Object.assign({ Estado: "juego", Pausa: 0 }, sv)), G = cont(Object.assign({ SonidoActivo: 1, NetRol: 0, Modo: "escape", Resultado: "derrota" }, gl));
  return { objs, S, G, getName: () => nombre, getVariables: () => S, getGame: () => ({ getVariables: () => G }),
    getObjects: (n) => objs.filter((o) => o.nombre === n), getLayer: () => ({ getCameraX: () => 0, getCameraY: () => 0 }) };
}
const nombres = (w) => w.sonado.map((s) => s.f.replace(".ogg", ""));
function correr(w, sc, seg) { for (let t = 0; t < seg; t += 0.1) { reloj += 0.1; w.X.tick(sc); } }

// ---------------------------------------------------------------- proyecto
const SON = ["ui_click", "ui_hover", "ui_confirm", "ui_error", "golpe_impacto", "jugador_dolor", "cuerpo_caida", "whoosh_esquivar",
  "zombie_growl", "zombie_ataque", "zombie_mordida", "zombie_muerte_01", "zombie_muerte_02", "zombie_spawn_braam", "oro_moneda",
  "objeto_recoger", "puerta_casillero", "curar_powerup", "oleada_riser", "evento_impacto_cinematico", "game_over", "victoria"];
const rec = function* (evs) { for (const e of evs || []) { yield e; yield* rec(e.events); } };
const L = (n) => d.layouts.find((l) => l.name === n);

prueba("Los 22 OGG están en fdiz/sonidos/ y son recursos de audio con el mismo nombre", () => {
  for (const n of SON) {
    const f = path.join(RAIZ, "sonidos", n + ".ogg");
    si(fs.existsSync(f), "falta " + f);
    igual(fs.readFileSync(f).slice(0, 4).toString(), "OggS", n);
    const r = d.resources.resources.find((x) => x.name === n + ".ogg");
    si(r && r.kind === "audio" && r.file === "../../sonidos/" + n + ".ogg", "recurso " + n);
  }
});
prueba("Cada escena carga sfx.js y lo llama cada cuadro, sin compuerta de host, después del volumen (fase 57)", () => {
  for (const l of d.layouts) {
    const top = l.events.map((e) => (e.inlineCode || "").slice(0, 24));
    const m = top.findIndex((s) => s.startsWith("/*FDIZ-FASE60-MOD")), t = top.findIndex((s) => s.startsWith("/*FDIZ-FASE60-TICK"));
    const v = top.findIndex((s) => s.startsWith("/*FDIZ-FASE57-APLICAR"));
    si(m >= 0 && t === m + 1 && v < m, l.name + ": " + [v, m, t]);
  }
});
prueba("Eventos: los sonidos equivalentes cambiaron y los que pone sfx.js ya no están", () => {
  const f = (l) => [...rec(L(l).events)].flatMap((e) => e.actions || []).filter((a) => a.type.value === "PlaySound").map((a) => a.parameters[1]);
  const j = f("Juego"), r = f("Resultados");
  for (const viejo of ["puerta_abrir", "locker", "bidon", "infestacion_sube", "final_inicio", "comer", "mordida"]) si(!j.some((x) => x.includes(viejo)), "queda " + viejo);
  igual(j.filter((x) => x === "puerta_casillero.ogg").length, 3, "puerta, locker y salida");
  igual(j.filter((x) => x === "objeto_recoger.ogg").length, 2, "bidón");
  si(j.includes("oleada_riser.ogg") && j.includes("evento_impacto_cinematico.ogg"));
  si(!r.some((x) => x.includes("victoria")), "Resultados todavía pone victoria.ogg");
  const jf = [...rec(L("Juego").events)].map((e) => e.inlineCode || "").join("\n");
  si(!jf.includes("jefe_invocar.ogg") && jf.includes('gdjs.fdizSfx.ui(scn, "error")'), "jefe_modo sin parche");
  const src = fs.readFileSync(path.join(__dirname, "jefe_modo.js"), "utf8");
  si(!src.includes("jefe_invocar.ogg") && src.includes('gdjs.fdizSfx.ui(scn, "error")'), "jefe_modo.js (fuente) sin parche");
});
prueba("TODO de pasos y de música de tensión: comentario + evento desactivado listo; OleadaInicio existe", () => {
  const ev = [...rec(L("Juego").events)];
  const i = ev.findIndex((e) => (e.comment || "").startsWith("// TODO: footsteps"));
  const k = ev.findIndex((e) => (e.comment || "").startsWith("// TODO: música de partida / tensión"));
  si(i >= 0 && k >= 0, "faltan comentarios");
  si(ev[i + 1].disabled && JSON.stringify(ev[i + 1]).includes("pasos.ogg"), "evento de pasos");
  si(ev[k + 1].disabled && JSON.stringify(ev[k + 1]).includes("OleadaInicio") && JSON.stringify(ev[k + 1]).includes("PlayMusicCanal"), "evento de música");
  si(L("Juego").variables.some((v) => v.name === "OleadaInicio"));
});
prueba("Volúmenes: interfaz 50-60, efectos 70-100; ninguno en loop", () => {
  const w = mundo();
  for (const [k, v] of Object.entries(w.X.VOL)) si(k.startsWith("ui_") ? v >= 50 && v <= 60 : v >= 70 && v <= 100, k + "=" + v);
  igual(Object.keys(w.X.VOL).sort(), SON.slice().sort(), "tabla completa");
});

// ---------------------------------------------------------------- escenas
prueba("Al entrar: Título impacto, Menú whoosh, Juego confirm, Resultados victoria o game over", () => {
  for (const [n, gl, s] of [["Titulo", {}, "evento_impacto_cinematico"], ["Menu", {}, "whoosh_esquivar"], ["Online", {}, "whoosh_esquivar"],
    ["Juego", {}, "ui_confirm"], ["Resultados", { Resultado: "victoria" }, "victoria"], ["Resultados", { Resultado: "derrota" }, "game_over"]]) {
    const w = mundo(); reloj += 10; w.X.tick(escena(n, [], {}, gl)); w.X.tick(escena(n, [], {}, gl));
    igual(nombres(w)[0], s, n);
  }
});
prueba("Jugador golpeado: golpe + mordida + dolor; pitch 0.8 (Miranda 1.0) ±0.1; cooldown 0.1 s", () => {
  const w = mundo(), t = sup(1, "tonyfuerte", 0, 0), m = sup(2, "miranda", 0, 0), sc = escena("Juego", [t, m]);
  correr(w, sc, 1.5); w.sonado.length = 0; sc.__fdizSfx.gNext = 1e12;   // sin growl: no gasta números al azar
  azar = [0.5, 1, 0.5, 0];                                     // golpe 0, dolor de Tony +0.1; golpe 0, dolor de Miranda -0.1
  t.C.get("Vida").setNumber(90); reloj += 0.2; w.X.tick(sc);
  m.C.get("Vida").setNumber(90); reloj += 0.2; w.X.tick(sc);
  igual(nombres(w), ["golpe_impacto", "zombie_mordida", "jugador_dolor", "golpe_impacto", "zombie_mordida", "jugador_dolor"]);
  const dol = w.sonado.filter((s) => s.f === "jugador_dolor.ogg").map((s) => s.p);
  igual(dol, [0.9, 0.9], "0.8+0.1 y 1.0-0.1");
  w.sonado.length = 0;
  t.C.get("Vida").setNumber(80); m.C.get("Vida").setNumber(80); reloj += 0.2; w.X.tick(sc);
  igual(nombres(w).filter((s) => s === "golpe_impacto").length, 1, "dos golpes en el mismo instante = uno");
  si(w.sonado.every((s) => s.loop === false), "loop");
});
prueba("Jugador: cae, se cura, lo levantan, ataca, recoge cosas; puerta restringida = ui_error", () => {
  const w = mundo(), s = sup(1, "alan", 0, 0), sc = escena("Juego", [s]);
  correr(w, sc, 1.5); w.sonado.length = 0;
  const paso = (f) => { f(); reloj += 0.5; w.X.tick(sc); };
  paso(() => { s.C.get("Vida").setNumber(0); s.C.get("Estado").setString("caido"); });
  paso(() => { s.C.get("Vida").setNumber(50); s.C.get("Estado").setString("normal"); });
  paso(() => s.C.get("Vida").setNumber(90));
  paso(() => s.C.get("Vida").setNumber(90.03));                 // regeneración lenta: nada
  paso(() => { s.an = "alan_pegar_lado"; });
  paso(() => s.C.get("Arma").setString("bate"));
  paso(() => s.C.get("Lanz").setString("balon"));
  paso(() => { s.C.get("Accion").setString("bloqueada"); s.C.get("Usando").setNumber(1); });
  igual(nombres(w), ["golpe_impacto", "zombie_mordida", "jugador_dolor", "cuerpo_caida", "curar_powerup", "curar_powerup", "whoosh_esquivar",
    "objeto_recoger", "objeto_recoger", "ui_error"]);
});
prueba("Zombis: no suenan al empezar; aparición, golpe, ataque y muerte con su pitch (normal 1, gordo 0.7, corredor 1.3)", () => {
  const w = mundo(), z1 = zombi("ZNormal", "normal", 100, 0), sc = escena("Juego", [z1]);
  w.X.GROWL.dist = 0;                                          // sin growl en esta prueba
  correr(w, sc, 1.5); igual(nombres(w), ["ui_confirm"], "los del mapa no hacen braam"); w.sonado.length = 0;
  const g = zombi("ZGordo", "gordo", 200, 0), r = zombi("ZCorredor", "corredor", 300, 0);
  sc.objs.push(g); reloj += 0.5; w.X.tick(sc); sc.objs.push(r); reloj += 0.5; w.X.tick(sc);
  g.C.get("Vida").setNumber(10); reloj += 0.5; w.X.tick(sc);
  r.an = "atacar_lado"; reloj += 0.5; w.X.tick(sc);
  azar = [0.9]; r.C.get("Estado").setString("muerto"); reloj += 0.5; w.X.tick(sc);
  igual(w.sonado.map((s) => [s.f.replace(".ogg", ""), s.p]), [["zombie_spawn_braam", 0.7], ["zombie_spawn_braam", 1.3], ["golpe_impacto", 1],
    ["zombie_ataque", 1.3], ["zombie_muerte_02", 1.3], ["cuerpo_caida", 1]]);
  w.sonado.length = 0;
  const lejos = zombi("ZNormal", "normal", 5000, 0); sc.objs.push(lejos); reloj += 0.5; w.X.tick(sc);
  lejos.C.get("Estado").setString("muerto"); reloj += 0.5; w.X.tick(sc);
  igual(nombres(w), [], "fuera de la cámara no suena");
});
prueba("Growl: aleatorio, más bajo cuanto más lejos, nada fuera del radio ni de zombis dormidos o muertos", () => {
  const w = mundo(); azar = [];
  w.X.rnd = Math.random;
  const cerca = zombi("ZNormal", "normal", 150, 0), lejos = zombi("ZGordo", "gordo", 600, 0), fuera = zombi("ZNormal", "normal", 1500, 0),
    dormido = zombi("ZNormal", "normal", 50, 0, { Estado: "dormido" }), muerto = zombi("ZNormal", "normal", 60, 0, { Estado: "muerto" });
  const sc = escena("Juego", [cerca, lejos, fuera, dormido, muerto]);
  correr(w, sc, 120);
  const gr = w.sonado.filter((s) => s.f === "zombie_growl.ogg");
  si(gr.length >= 10 && gr.length <= 50, "cantidad " + gr.length);
  const c = gr.filter((s) => Math.abs(s.p - 1) <= 0.1001), g = gr.filter((s) => Math.abs(s.p - 0.7) <= 0.1001 && s.p < 0.85);
  si(c.length && g.length, "los dos gruñen");
  si(Math.min(...c.map((s) => s.vol)) > Math.max(...g.map((s) => s.vol)), "el cercano suena más fuerte");
  si(gr.every((s) => s.vol <= 80 && s.loop === false));
  igual(gr.length, c.length + g.length, "ni el de fuera del radio, ni el dormido, ni el muerto");
});
prueba("Oro y objetos: monedas, llaves, compra del Jefe (solo en su máquina) y bolsa", () => {
  const w = mundo(), ll = obj("Objetivo", 0, 0, { Tipo: "llaves", Hecho: 0 }), mo = obj("Moneda", 0, 0, {});
  const sc = escena("Juego", [ll, mo], { OroJefe: 10, TieneBolsa: 0 }, { Modo: "jefe" });
  correr(w, sc, 1.5); w.sonado.length = 0;
  const paso = (f) => { f(); reloj += 0.5; w.X.tick(sc); };
  paso(() => ll.C.get("Hecho").setNumber(1));
  paso(() => sc.objs.splice(sc.objs.indexOf(mo), 1));
  paso(() => sc.S.get("OroJefe").setNumber(15));
  paso(() => sc.S.get("OroJefe").setNumber(8));
  paso(() => sc.S.get("TieneBolsa").setNumber(1));
  igual(nombres(w), ["objeto_recoger", "ui_confirm", "objeto_recoger"]);   // fase 80: las monedas ya no suenan
  const w2 = mundo(), sc2 = escena("Juego", [], { OroJefe: 10 }, { Modo: "jefe", NetRol: 2 });
  correr(w2, sc2, 1.5); w2.sonado.length = 0;
  sc2.S.get("OroJefe").setNumber(3); reloj += 0.5; w2.X.tick(sc2);
  igual(nombres(w2), [], "un sobreviviente en línea no oye el oro del Jefe");
});
prueba("Oleadas: horda y final = oleada_riser; OleadaInicio vale 1 un cuadro (también al subir la infestación)", () => {
  const w = mundo(), sc = escena("Juego", [], { Horda: 0, FinalActivo: 0, Infestacion: 1 });
  correr(w, sc, 1.5); w.sonado.length = 0;
  sc.S.get("Infestacion").setNumber(2); reloj += 0.1; w.X.tick(sc);
  igual([nombres(w), sc.S.get("OleadaInicio").getAsNumber()], [[], 1], "infestación: el riser lo pone el evento");
  reloj += 0.1; w.X.tick(sc); igual(sc.S.get("OleadaInicio").getAsNumber(), 0);
  sc.S.get("Horda").setNumber(1); reloj += 2; w.X.tick(sc);
  sc.S.get("FinalActivo").setNumber(1); reloj += 0.2; w.X.tick(sc);
  igual(nombres(w), ["oleada_riser", "oleada_riser"]);
});
prueba("Pausa: el mundo no suena; abrir/cerrar la pausa y moverse por ella sí", () => {
  const w = mundo(), s = sup(1, "gabo", 0, 0), sc = escena("Juego", [s], { PausaSel: 0, PausaVista: 0 });
  correr(w, sc, 1.5); w.sonado.length = 0;
  sc.S.get("Pausa").setNumber(1); reloj += 0.2; w.X.tick(sc);
  sc.S.get("PausaSel").setNumber(1); reloj += 0.2; w.X.tick(sc);
  s.C.get("Vida").setNumber(10); reloj += 0.2; w.X.tick(sc);
  igual(nombres(w), ["ui_click", "ui_hover"]);
});
prueba("Menú: teclado / mando (variables) y ratón (hover al entrar a un botón, clic al soltar); nada en el primer cuadro", () => {
  const w = mundo(), b1 = obj("MarcoModo", 0, 0, {}), b2 = obj("MarcoModo", 200, 0, {});
  raton.x = 50; raton.y = 20; raton.suelta = false;
  const sc = escena("Menu", [b1, b2], { Paso: "modo", Sel: 0, S1Ok: 0, S1Pj: 0 });
  reloj += 1; w.X.tick(sc); w.sonado.length = 0;                     // whoosh de entrada
  reloj += 0.2; w.X.tick(sc); igual(nombres(w), [], "el ratón quieto no suena");
  raton.x = 250; reloj += 0.2; w.X.tick(sc);
  raton.suelta = true; reloj += 0.2; w.X.tick(sc); raton.suelta = false;
  sc.S.get("Sel").setNumber(1); reloj += 0.2; w.X.tick(sc);
  sc.S.get("Paso").setString("equipo"); reloj += 0.2; w.X.tick(sc);
  sc.S.get("S1Pj").setNumber(3); reloj += 0.2; w.X.tick(sc);
  sc.S.get("S1Ok").setNumber(1); reloj += 0.2; w.X.tick(sc);
  sc.G.get("Dificultad").setNumber(2); reloj += 0.2; w.X.tick(sc);
  igual(nombres(w), ["ui_hover", "ui_click", "ui_hover", "ui_click", "ui_click", "ui_confirm", "ui_click"]);
});
prueba("Sala en línea: cambiar de pantalla, entrar al lobby, error de red", () => {
  const w = mundo(); w.gdjs.fdizNet = { ui: { st: "menu", sel: 0 } };
  const sc = escena("Online", []);
  reloj += 1; w.X.tick(sc); w.sonado.length = 0;
  const U = w.gdjs.fdizNet.ui;
  U.sel = 1; reloj += 0.2; w.X.tick(sc);
  U.st = "connecting"; reloj += 0.2; w.X.tick(sc);
  U.st = "lobby"; reloj += 0.2; w.X.tick(sc);
  U.st = "error"; reloj += 0.5; w.X.tick(sc);
  igual(nombres(w), ["ui_hover", "ui_click", "ui_confirm", "ui_error"]);
});
prueba("Red: se reproduce con la función original (no se reenvía) y se respeta SonidoActivo = 0", () => {
  const w = mundo(), sc = escena("Juego", [sup(1, "carlos", 0, 0)]);
  correr(w, sc, 1.5);
  igual(w.red, [], "no pasó por el reenvío de net_core");
  const w2 = mundo(), sc2 = escena("Titulo", [], {}, { SonidoActivo: 0 }); w2.X.tick(sc2);
  igual(w2.sonado, []);
});
prueba("Modo Jefe: mensaje de error del Jefe = ui_error (jefe_modo.js incrustado)", () => {
  const src = fs.readFileSync(path.join(__dirname, "jefe_modo.js"), "utf8");
  const i = src.indexOf("function say(");
  const linea = src.slice(i, src.indexOf("\n", i));
  const w = mundo(), sc = escena("Juego", []);
  const st = { t: 0 }, scn = sc;
  vm.runInNewContext("(function(){" + linea + " say('Te falta oro'); say('Hecho', '120;255;120');})()", { st, scn, gdjs: w.gdjs });
  igual(nombres(w), ["ui_error"], "solo los mensajes rojos (de error)");
});

console.log(ok + " correctas, " + mal + " fallidas");
process.exit(mal ? 1 : 0);
