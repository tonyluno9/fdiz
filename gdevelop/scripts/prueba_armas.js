// Pruebas de scripts/armas.js (fase 62) y de su conexión con el proyecto, sin GDevelop:  node gdevelop/scripts/prueba_armas.js
"use strict";
const fs = require("fs"), path = require("path"), vm = require("vm");
const PROY = path.join(__dirname, "..", "FDI-Z");
const d = JSON.parse(fs.readFileSync(path.join(PROY, "FDI-Z.json"), "utf8"));
const J = d.layouts.find((l) => l.name === "Juego");
const res = Object.fromEntries(d.resources.resources.map((r) => [r.name, r.file]));
let ok = 0, mal = 0;
function prueba(n, f) { try { f(); ok++; console.log("  OK   " + n); } catch (e) { mal++; console.log("  MAL  " + n + " -> " + e.message); } }
const igual = (a, b, m) => { if (JSON.stringify(a) !== JSON.stringify(b)) throw new Error((m || "") + ": " + JSON.stringify(a) + " != " + JSON.stringify(b)); };
const si = (c, m) => { if (!c) throw new Error(m || "falso"); };
const rec = function* (evs) { for (const e of evs || []) { yield e; yield* rec(e.events); } };
const grupo = (n) => [...rec(J.events)].find((e) => (e.type || "").endsWith("Group") && e.name === n);
const tiene = (e, tipo, ps) => (e.conditions || []).concat(e.actions || []).some((x) => x.type.value === tipo && ps.every((p, i) => x.parameters[i] === p));

// ---------------------------------------------------------------- mundo falso
function variable(x) { return { getAsNumber: () => Number(x) || 0, getAsString: () => String(x), setNumber: (n) => { x = n; }, setString: (s) => { x = s; } }; }
function cont(ini) { const V = {}; for (const k in ini || {}) V[k] = variable(ini[k]); return { get: (n) => V[n] || (V[n] = variable(0)) }; }
const ANIMS = new Set(J.objects.find((o) => o.name === "Sup").animations.map((a) => a.name));
function obj(nombre, x, y, vars, w, h) {
  const C = cont(vars);
  return { nombre, x, y, w: w || 64, h: h || 120, C, an: "", oculto: false, vis: true, _vivo: true,
    getVariables: () => C, getX() { return this.x; }, getY() { return this.y; }, getWidth() { return this.w; }, getHeight() { return this.h; },
    getDrawableX() { return this.x - this.w / 2; }, getDrawableY() { return this.y - this.h; }, isHidden() { return this.oculto; }, isVisible() { return this.vis; },
    getAnimationName() { return this.an; }, setAnimationName(n) { if (this.nombre === "Sup" && !ANIMS.has(n)) return false; this.an = n; return true; } };
}
const sup = (j, pj, x, y, o) => { const s = obj("Sup", x, y, Object.assign({ Jugador: j, Personaje: pj, Control: j - 1, Estado: "normal", Arma: "puños", Usos: 0, AimX: 1, AimY: 0, Atacando: 0 }, o)); s.an = pj + "_quieto"; return s; };
function hudObj(n) {
  return { n, txt: "", oculto: false, x: 0, y: 0, w: 11, h: 11, op: 255, z: 0, col: "", rects: [], nombre: n,
    setLayer() {}, setZOrder(z) { this.z = z; }, hide(b) { this.oculto = b; }, isHidden() { return this.oculto; }, setText(s) { this.txt = s; }, getString() { return this.txt; },
    setColor(c) { this.col = c; }, setPosition(x, y) { this.x = x; this.y = y; }, getX() { return this.x; }, getY() { return this.y; }, getWidth() { return this.w; }, getHeight() { return this.h; },
    setOpacity(o) { this.op = o; }, deleteFromScene(sc) { sc.objs.splice(sc.objs.indexOf(this), 1); },
    clear() { this.rects = []; this.rellenos = []; }, setOutlineSize() {}, setOutlineColor() {}, setOutlineOpacity() {}, setFillOpacity() {},
    setFillColor(c) { this.fill = c; }, drawRectangle(x0, y0, x1, y1) { this.rects.push([x0, y0, x1, y1, this.fill]); } };
}
function escena(objs, sv, gl) {
  const S = cont(Object.assign({ Estado: "juego", Pausa: 0 }, sv)), G = cont(Object.assign({ NetRol: 0 }, gl));
  const sc = { objs, S, getVariables: () => S, getGame: () => ({ getVariables: () => G }),
    getObjects: (n) => objs.filter((o) => (o.nombre || o.n) === n),
    createObject: (n) => { const h = hudObj(n); objs.push(h); return h; } };
  for (const [j, xy] of Object.entries({ 1: [351, 94], 2: [1813, 94], 3: [351, 978], 4: [1813, 978] })) {
    const t = hudObj("TxtBalas"); t.getVariables = () => cont({ Jugador: Number(j) }); objs.push(t);
    const i = obj("HudIcono", xy[0], xy[1], { Jugador: Number(j), Slot: 3 }, 54, 54); objs.push(i);
  }
  return sc;
}
function cargar() {
  const gdjs = {};
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, "armas.js"), "utf8"), { gdjs, Math, String });
  return gdjs.fdizArmas;
}
const txt = (sc, j) => sc.objs.find((o) => o.n === "TxtBalas" && o.getVariables().get("Jugador").getAsNumber() === j);
const mira = (s) => s.__fdizMira;

// ---------------------------------------------------------------- munición y armas
prueba("Munición: pistola pequeña 9, escopeta 6, sheriff 4 (al recogerla) y el HUD usa los mismos números", () => {
  const A = cargar();
  igual(A.CARGADOR, { pistolita: 9, pistola: 4, escopeta: 6 });
  const recoge = [...rec(grupo("Armas del salón").events)].find((e) => tiene(e, "ModVarObjetTxt", ["Sup", "Arma", "=", "ArmaPiso.VariableString(Tipo)"]));
  const usos = (t) => recoge.events.find((e) => tiene(e, "VarObjetTxt", ["Sup", "Arma", "=", '"' + t + '"'])).actions[0].parameters[3];
  igual([usos("pistola"), usos("escopeta")], ["4", "6"]);
});
prueba("El jugador 1 (y solo él) empieza con la pistola pequeña y 9 balas, en todos los modos", () => {
  const ini = [...rec(grupo("Inicio de supervivientes").events)].find((e) => tiene(e, "VarObjet", ["Sup", "Init", "=", "0"]));
  const ev = ini.events.filter((e) => tiene(e, "ModVarObjetTxt", ["Sup", "Arma", "=", '"pistolita"']));
  igual(ev.length, 1);
  igual(ev[0].conditions.map((c) => c.type.value + "|" + c.parameters.join("|")), ["VarObjet|Sup|Jugador|=|1"]);
  si(tiene(ev[0], "ModVarObjet", ["Sup", "Usos", "=", "9"]));
  si(!JSON.stringify(ini.conditions).includes("Modo"), "no depende del modo");
});
prueba("La pistola pequeña dispara una bala (12 de daño, más aguda) y se gasta con la regla de siempre", () => {
  const sub = [...rec(grupo("Combate: pegar").events)].find((e) => tiene(e, "VarObjetTxt", ["Sup", "Arma", "=", '"pistolita"']) && tiene(e, "Create", ["", "Proyectil"]));
  si(sub && sub.actions.filter((x) => x.type.value === "Create").length === 1, "una bala");
  si(JSON.stringify(sub.events).includes('"1.3"'), "pitch");
  const val = [...rec(grupo("Armas del salón").events)].find((e) => tiene(e, "VarObjetTxt", ["Sup", "Arma", "=", '"pistolita"']) && tiene(e, "ModVarObjet", ["Sup", "ArmaFuego", "=", "1"]));
  si(tiene(val, "ModVarObjet", ["Sup", "DanioArma", "=", "12"]));
  si([...rec(grupo("Combate: pegar").events)].some((e) => tiene(e, "ModVarObjet", ["Sup", "Usos", "-", "1"])), "regla de gasto");
});

// ---------------------------------------------------------------- animaciones
const PJS = ["tony", "tonyfuerte", "miranda", "cesar", "alan", "castillo", "alessandro", "gabo", "carlos", "joel", "justino", "canepa"];
prueba("Animaciones placeholder de pistola de lado y hacia abajo para los 12 personajes (mismo origen y máscara que la base)", () => {
  const S = J.objects.find((o) => o.name === "Sup"), an = Object.fromEntries(S.animations.map((a) => [a.name, a]));
  for (const pj of PJS) for (const [dir, base, idx] of [["lado", "pegar_lado", 1], ["abajo", "pegar_abajo", 0]]) {
    const a = an[pj + "_pistola_" + dir]; si(a, "falta " + pj + "_pistola_" + dir);
    const sp = a.directions[0].sprites, b = an[pj + "_" + base].directions[0].sprites[idx];
    igual(sp.length, 3, pj + " " + dir);
    for (const s of sp) {
      si(fs.existsSync(path.join(PROY, res[s.image])), "falta el archivo " + res[s.image]);
      igual([s.originPoint, s.hasCustomCollisionMask, s.customCollisionMask], [b.originPoint, b.hasCustomCollisionMask, b.customCollisionMask], pj + " " + dir);
    }
  }
  si(!S.animations.some((a) => a.name.endsWith("_pistola_arriba")), "hacia arriba no hay: se usa pegar_arriba");
});
prueba("Al disparar con pistola: de lado y abajo la animación de pistola; arriba, escopeta o sin animación sigue la de pegar", () => {
  const A = cargar();
  const casos = [["tony", "pistolita", "tony_pegar_lado", "tony_pistola_lado"], ["miranda", "pistola", "miranda_pegar_abajo", "miranda_pistola_abajo"],
    ["gabo", "pistolita", "gabo_pegar_arriba", "gabo_pegar_arriba"], ["cesar", "escopeta", "cesar_pegar_lado", "cesar_pegar_lado"],
    ["tonyfuerte", "pistola", "tonyfuerte_pegar_lado", "tonyfuerte_pistola_lado"]];
  for (const [pj, arma, de, a] of casos) {
    const s = sup(1, pj, 0, 0, { Arma: arma, Usos: 3, Atacando: 1 }); s.an = de;
    A.anim(escena([s])); igual(s.an, a, pj + " " + arma);
  }
  const raro = sup(1, "nuevo", 0, 0, { Arma: "pistolita", Usos: 3, Atacando: 1 }); raro.an = "nuevo_pegar_lado";
  A.anim(escena([raro])); igual(raro.an, "nuevo_pegar_lado", "sin animación de pistola: no queda invisible");
  const s = sup(1, "tony", 0, 0, { Arma: "pistolita", Usos: 3, Atacando: 1 }); s.an = "tony_pegar_lado";
  A.anim(escena([s], {}, { NetRol: 2 })); igual(s.an, "tony_pegar_lado", "el cliente no cambia animaciones (llegan del host)");
});

// ---------------------------------------------------------------- mira
prueba("Mira: hacia donde apunta, a 78 px del arma, centrada; solo jugadores con arma de fuego y balas", () => {
  const A = cargar();
  const p1 = sup(1, "tony", 1000, 1000, { Arma: "pistolita", Usos: 9, AimX: 0, AimY: 1 });
  const p2 = sup(2, "gabo", 2000, 1000, { Arma: "bate", Usos: 5 });
  const bot = sup(3, "alan", 3000, 1000, { Arma: "escopeta", Usos: 6, Control: -1 });
  const p4 = sup(4, "cesar", 4000, 1000, { Arma: "pistola", Usos: 0 });
  const sc = escena([p1, p2, bot, p4]);
  A.tick(sc);
  const m = mira(p1);
  igual([m.oculto, m.x + 5.5, m.y + 5.5], [false, 1000.5, 1000 - 46 + 78 + 0.5]);
  si(!mira(p2) && !mira(bot) && !mira(p4), "ni cuerpo a cuerpo, ni bots, ni sin balas");
  p1.C.get("AimX").setNumber(-3); p1.C.get("AimY").setNumber(4); A.tick(sc);
  si(Math.abs(m.x + 5.5 - (1000 - 0.6 * 78)) <= 1 && Math.abs(m.y + 5.5 - (954 + 0.8 * 78)) <= 1, "dirección normalizada (±1 px por el redondeo a píxel): " + [m.x, m.y]);
});
prueba("Mira: discreta sobre personajes y zombis (más transparente), y se esconde en pausa, diálogo, al caer o sin arma", () => {
  const A = cargar();
  const p1 = sup(1, "tony", 1000, 1000, { Arma: "pistolita", Usos: 9 });
  const z = obj("ZNormal", 1078, 1000, {}, 50, 120);
  const sc = escena([p1, z]);
  A.tick(sc); igual(mira(p1).op, 110, "sobre un zombi");
  z.x = 3000; A.tick(sc); igual(mira(p1).op, 210, "libre");
  sc.S.get("Pausa").setNumber(1); A.tick(sc); si(mira(p1).oculto, "pausa");
  sc.S.get("Pausa").setNumber(0); sc.S.get("Estado").setString("dialogo"); A.tick(sc); si(mira(p1).oculto, "diálogo");
  sc.S.get("Estado").setString("juego"); p1.C.get("Estado").setString("caido"); A.tick(sc); si(mira(p1).oculto, "caído");
  p1.C.get("Estado").setString("normal"); p1.C.get("Arma").setString("puños"); A.tick(sc); si(mira(p1).oculto, "sin arma");
  sc.objs.splice(sc.objs.indexOf(p1), 1); A.tick(sc); si(!sc.objs.some((o) => o.n === "Mira"), "se borra si el jugador ya no está");
});

// ---------------------------------------------------------------- HUD
prueba("HUD: balas que quedan junto al ícono y el cargador debajo (gastadas en gris); rojo con 2 o menos", () => {
  const A = cargar();
  const p1 = sup(1, "tony", 0, 0, { Arma: "pistolita", Usos: 7 }), p2 = sup(2, "gabo", 0, 0, { Arma: "escopeta", Usos: 2 }), p3 = sup(3, "alan", 0, 0, { Arma: "regla", Usos: 20 });
  const sc = escena([p1, p2, p3]);
  A.tick(sc);
  igual([txt(sc, 1).txt, txt(sc, 1).oculto, txt(sc, 1).col], ["7", false, "255;255;255"]);
  igual([txt(sc, 2).txt, txt(sc, 2).col], ["2", "255;110;90"]);
  si(txt(sc, 3).oculto && txt(sc, 4).oculto, "sin arma de fuego no hay número");
  const dib = sc.objs.find((o) => o.n === "BalasDib");
  const de = (x0, x1) => dib.rects.filter((r) => r[0] >= x0 && r[2] <= x1);
  const p1r = de(351, 405), p2r = de(1813, 1867);
  igual([p1r.length, p1r.filter((r) => r[4] === "232;190;90").length], [9, 7], "pistola: 9 marcas, 7 llenas");
  igual([p2r.length, p2r.filter((r) => r[4] === "232;190;90").length], [6, 2], "escopeta: 6 marcas, 2 llenas");
  si(p1r.every((r) => r[1] >= 94 + 54 && r[3] <= 180), "debajo del ícono, dentro del panel");
  si(txt(sc, 1).x >= 405 && txt(sc, 1).x + 26 <= 438, "a la derecha del ícono, dentro del panel");
});
prueba("HUD: no se ve en la intro ni si el panel del jugador está oculto; se actualiza al gastar balas", () => {
  const A = cargar();
  const p1 = sup(1, "tony", 0, 0, { Arma: "pistolita", Usos: 9 });
  const sc = escena([p1], { Estado: "intro" });
  A.tick(sc); si(txt(sc, 1).oculto, "intro");
  sc.S.get("Estado").setString("juego"); A.tick(sc); igual(txt(sc, 1).txt, "9");
  p1.C.get("Usos").setNumber(8); A.tick(sc); igual(txt(sc, 1).txt, "8");
  sc.objs.find((o) => o.nombre === "HudIcono" && o.C.get("Jugador").getAsNumber() === 1).vis = false; A.tick(sc);
  si(txt(sc, 1).oculto, "panel oculto");
});

// ---------------------------------------------------------------- proyecto
prueba("Proyecto: armas.js arriba de Juego (todas las máquinas) y la animación al final de «Combate: pegar» (host)", () => {
  const top = J.events.map((e) => (e.inlineCode || "").slice(0, 22));
  const m = top.findIndex((s) => s.startsWith("/*FDIZ-FASE62-MOD")), t = top.findIndex((s) => s.startsWith("/*FDIZ-FASE62-TICK"));
  si(m >= 0 && t === m + 1, "MOD/TICK " + [m, t]);
  const GC = grupo("Combate: pegar").events, ult = GC[GC.length - 1];
  si(tiene(ult, "VarGlobal", ["NetRol", "!=", "2"]) && ult.events[0].inlineCode.startsWith("/*FDIZ-FASE62-ANIM"), "ANIM");
});
prueba("Proyecto: Mira, BalasDib y un TxtBalas por panel; ícono de la pistola pequeña en el HUD", () => {
  si(J.objects.some((o) => o.name === "Mira") && J.objects.some((o) => o.name === "BalasDib" && o.type === "PrimitiveDrawing::Drawer"));
  const t = J.instances.filter((i) => i.name === "TxtBalas").map((i) => i.initialVariables[0].value).sort();
  igual(t, [1, 2, 3, 4]);
  const ic = J.objects.find((o) => o.name === "HudIcono").animations.find((a) => a.name === "pistolita");
  igual(res[ic.directions[0].sprites[0].image], "assets/interfaz/hud/ico128_arma_pistola.png");
  const mi = J.objects.find((o) => o.name === "Mira").animations[0].directions[0].sprites[0].image;
  si(fs.existsSync(path.join(PROY, res[mi])), "falta mira.png");
});

console.log(ok + " correctas, " + mal + " fallidas");
process.exit(mal ? 1 : 0);
