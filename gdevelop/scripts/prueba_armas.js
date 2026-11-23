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
prueba("Nadie empieza con la pistola pequeña: ningún evento de inicio la equipa (fase 67)", () => {
  const ini = grupo("Inicio de supervivientes");
  si(![...rec(ini.events)].some((e) => tiene(e, "ModVarObjetTxt", ["Sup", "Arma", "=", '"pistolita"'])), "inicio");
  // ningún evento fuera de recoger un arma del piso pone Arma = pistolita
  const pone = [...rec(J.events)].filter((e) => tiene(e, "ModVarObjetTxt", ["Sup", "Arma", "=", '"pistolita"']));
  igual(pone.length, 0, "eventos que equipan la pistolita directamente");
  const js = [...rec(J.events)].filter((e) => (e.inlineCode || "").includes('"pistolita"') && /Arma"\)\.setString\("pistolita/.test(e.inlineCode));
  igual(js.length, 0, "código que la equipe");
  const cin = J.events.find((e) => (e.name || "").startsWith("Cinemática de inicio"));
  si(![...rec(cin.events)].some((e) => tiene(e, "VarObjet", ["Sup", "Jugador", "=", "1"]) && tiene(e, "ModVarObjetTxt", ["Sup", "Arma", "=", '"regla"'])),
    "al terminar la intro de Escape el jugador 1 ya no recibe la regla (así puede recoger la pistola)");
  si(JSON.stringify(cin.events).includes("Agarra la pistola") && !JSON.stringify(cin.events).includes("Agarra la regla"), "consejo de la intro");
});
function escenaPistola(sups, gl) {
  const sc = escena(sups, {}, gl);
  const crear = sc.createObject;
  sc.createObject = (n) => {
    if (n !== "ArmaPiso") return crear(n);
    const a = obj("ArmaPiso", 0, 0, { Tipo: "", Solo: 0 });
    Object.assign(a, { setLayer(l) { this.capa = l; }, setPosition(x, y) { this.x = x; this.y = y; }, setZOrder(z) { this.z = z; } });
    sc.objs.push(a); return a;
  };
  return sc;
}
const pistolas = (sc) => sc.getObjects("ArmaPiso").filter((a) => a.getVariables().get("Tipo").getAsString() === "pistolita");
const cuadros = (A, sc, n) => { for (let k = 0; k < n; k++) A.ponerPistola(sc); };
prueba("La pistola aparece en el piso del salón donde empieza el jugador 1 (B-01 con la intro o Historia; E-04 si no)", () => {
  const A = cargar();
  const b01 = escenaPistola([sup(1, "tony", 5894, 3024, { Init: 1 }), sup(2, "gabo", 5954, 3024, { Init: 1 })]);
  cuadros(A, b01, 60);
  igual(pistolas(b01).map((a) => [a.x, a.y, a.z, a.capa, a.an, a.getVariables().get("Solo").getAsNumber()]), [[6000, 3100, 3100, "Juego", "pistolita", 1]]);
  const e04 = escenaPistola([sup(1, "tony", 5088, 2528, { Init: 1 })]);
  cuadros(A, e04, 60);
  igual(pistolas(e04).map((a) => [a.x, a.y]), [[5200, 2570]]);
  const lejos = escenaPistola([sup(1, "tony", 5300, 2900, { Init: 1 })]);
  cuadros(A, lejos, 60);
  igual(pistolas(lejos).length, 1, "fuera de los dos salones: el más cercano");
});
prueba("Una sola vez: no aparece antes de colocar al equipo, ni dos veces, ni en un cliente en línea", () => {
  const A = cargar();
  const sc = escenaPistola([sup(1, "tony", 5088, 2528, { Init: 1 }), sup(2, "gabo", 5152, 2528, { Init: 0 })]);
  cuadros(A, sc, 100);
  igual(pistolas(sc).length, 0, "un Sup sin Init");
  sc.getObjects("Sup")[1].getVariables().get("Init").setNumber(1);
  cuadros(A, sc, 20);
  igual(pistolas(sc).length, 0, "todavía no (espera a que Historia o la intro muevan al equipo)");
  sc.getObjects("Sup")[0].x = 5894; sc.getObjects("Sup")[0].y = 3024;   // la intro / Historia lo pasó a B-01
  cuadros(A, sc, 40);
  igual(pistolas(sc).map((a) => [a.x, a.y]), [[6000, 3100]], "en el salón final del jugador 1");
  const p = pistolas(sc)[0]; sc.objs.splice(sc.objs.indexOf(p), 1);    // la recogió
  cuadros(A, sc, 200);
  igual(pistolas(sc).length, 0, "recogida: no vuelve a aparecer");
  igual(sc.S.get("PistolaPuesta").getAsNumber(), 1);
  const cli = escenaPistola([sup(1, "tony", 5894, 3024, { Init: 1 })], { NetRol: 2 });
  cuadros(A, cli, 100);
  igual(pistolas(cli).length, 0, "el cliente no la crea (le llega la del host)");
});
prueba("Se recoge con el sistema de siempre: con los puños, solo el jugador 1, se equipa con 9 balas y se borra del piso", () => {
  const f = [...rec(grupo("Armas del salón").events)].find((e) => (e.type || "").endsWith("ForEach") && e.object === "Sup" && tiene(e, "CollisionNP", ["Sup", "ArmaPiso"]));
  si(tiene(f, "VarObjetTxt", ["Sup", "Arma", "=", '"puños"']), "solo con los puños");
  const o = f.conditions.find((c) => c.type.value.endsWith("Or"));
  igual(o.subInstructions.map((c) => c.parameters.join("|")), ["ArmaPiso|Solo|=|0", "ArmaPiso|Solo|=|Sup.Variable(Jugador)"]);
  const recoge = [...rec(f.events)].find((e) => tiene(e, "ModVarObjetTxt", ["Sup", "Arma", "=", "ArmaPiso.VariableString(Tipo)"]));
  const usos = recoge.events.find((e) => tiene(e, "VarObjetTxt", ["Sup", "Arma", "=", '"pistolita"']));
  si(usos && tiene(usos, "ModVarObjet", ["Sup", "Usos", "=", "9"]), "9 balas");
  si(tiene(recoge.events[recoge.events.length - 1], "Delete", ["ArmaPiso"]), "se borra del piso");
  const val = [...rec(grupo("Armas del salón").events)].find((e) => tiene(e, "VarObjetTxt", ["Sup", "Arma", "=", '"pistolita"']) && tiene(e, "ModVarObjet", ["Sup", "ArmaFuego", "=", "1"]));
  si(val, "valores de arma de fuego al tenerla");
  const ap = J.objects.find((x) => x.name === "ArmaPiso");
  si(ap.variables.some((v) => v.name === "Solo" && v.value === 0), "Solo = 0 por defecto (las demás armas, cualquiera)");
  si(J.variables.some((v) => v.name === "PistolaPuesta"), "PistolaPuesta");
  const an = ap.animations.find((a) => a.name === "pistolita").directions[0].sprites[0];
  si(fs.existsSync(path.join(PROY, res[an.image])), "sprite de piso");
});
prueba("El lugar de la pistola está libre (sin muros ni muebles) y dentro de su salón", () => {
  const A = cargar();
  const solidos = J.instances.filter((i) => i.name === "Muro" || i.name === "ChoqueMueble");
  for (const q of A.PISTOLA.salones) {
    si(q.x > q.x0 && q.x < q.x1 && q.y > q.y0 && q.y < q.y1, q.zona + " dentro");
    const caja = [q.x - 20, q.y - 24, q.x + 20, q.y];   // 39 x 24, pies abajo al centro
    const choca = solidos.filter((m) => caja[0] < m.x + m.width && caja[2] > m.x && caja[1] < m.y + m.height && caja[3] > m.y);
    igual(choca.map((m) => [m.name, m.x, m.y]), [], q.zona + " libre");
  }
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
    if (pj === "tony" && dir === "lado") continue;          // fase 69: Tony usa sus cuadros reales de disparo (prueba siguiente)
    const sp = a.directions[0].sprites, b = an[pj + "_" + base].directions[0].sprites[idx];
    igual(sp.length, 3, pj + " " + dir);
    for (const s of sp) {
      si(fs.existsSync(path.join(PROY, res[s.image])), "falta el archivo " + res[s.image]);
      igual([s.originPoint, s.hasCustomCollisionMask, s.customCollisionMask], [b.originPoint, b.hasCustomCollisionMask, b.customCollisionMask], pj + " " + dir);
    }
  }
  si(!S.animations.some((a) => a.name.endsWith("_pistola_arriba")), "hacia arriba no hay: se usa pegar_arriba");
});
prueba("Fase 69: Tony dispara con sus animaciones reales (pistola y escopeta de lado, 4 cuadros, pies en el mismo origen)", () => {
  const S = J.objects.find((o) => o.name === "Sup"), an = Object.fromEntries(S.animations.map((a) => [a.name, a]));
  for (const arma of ["pistola", "escopeta"]) {
    const a = an["tony_" + arma + "_lado"]; si(a, "falta tony_" + arma + "_lado");
    const sp = a.directions[0].sprites;
    igual(sp.length, 4, arma);
    for (const s of sp) {
      si(fs.existsSync(path.join(PROY, res[s.image])), "falta el archivo " + res[s.image]);
      si(/disparo_/.test(s.image), "usa los cuadros de animaciones_gif/personajes/tony: " + s.image);
      igual([s.originPoint.x, s.originPoint.y], [80, 125], arma);
    }
  }
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
