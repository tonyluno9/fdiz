// Pruebas de scripts/dialogo.js y de los datos del banco (fase 64), sin GDevelop:  node gdevelop/scripts/prueba_dialogo.js
"use strict";
const fs = require("fs"), path = require("path"), vm = require("vm");
const RAIZ = path.join(__dirname, "..", "..");
const PROY = path.join(RAIZ, "gdevelop", "FDI-Z");
const d = JSON.parse(fs.readFileSync(path.join(PROY, "FDI-Z.json"), "utf8"));
const J = d.layouts.find((l) => l.name === "Juego");
let ok = 0, mal = 0;
function prueba(n, f) { try { f(); ok++; console.log("  OK   " + n); } catch (e) { mal++; console.log("  MAL  " + n + " -> " + e.message); } }
const igual = (a, b, m) => { if (JSON.stringify(a) !== JSON.stringify(b)) throw new Error((m || "") + ": " + JSON.stringify(a) + " != " + JSON.stringify(b)); };
const si = (c, m) => { if (!c) throw new Error(m || "falso"); };
const norm = (s) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();

// ---------------------------------------------------------------- mundo falso
function variable(x) { return { getAsNumber: () => Number(x) || 0, getAsString: () => String(x), setNumber: (n) => { x = n; }, setString: (s) => { x = s; } }; }
function cont(ini) { const V = {}; for (const k in ini || {}) V[k] = variable(ini[k]); return { V, get: (n) => V[n] || (V[n] = variable(0)), has: (n) => n in V }; }
function obj(nombre, x, y, vars, w, h) {
  const C = cont(vars);
  return { nombre, x, y, w: w || 64, h: h || 120, C, oculto: false, getVariables: () => C, getX() { return this.x; }, getY() { return this.y; },
    getWidth() { return this.w; }, getHeight() { return this.h; }, getDrawableX() { return this.x - this.w / 2; }, getDrawableY() { return this.y - this.h; },
    isHidden() { return this.oculto; } };
}
const sup = (j, pj, x, y, o) => obj("Sup", x, y, Object.assign({ Jugador: j, Personaje: pj, Estado: "normal", Mordido: 0, Curando: 0, HabTxt: "LISTA", EspTxt: "LISTO",
  Arma: "puños", Lanz: "", LanzUsos: 0, Turbo: 0, Usando: 0, Accion: "", Kills: 0, MovX: 0, MovY: 0, Control: j - 1 }, o));
function hudObj(n) {
  return { n, nombre: n, txt: "", oculto: false, x: 0, y: 0, w: 0, h: 0, cs: 20, ww: 0,
    setLayer() {}, setZOrder() {}, hide(b) { this.oculto = b; }, isHidden() { return this.oculto; }, setText(s) { this.txt = s; }, getString() { return this.txt; },
    setCharacterSize(c) { this.cs = c; }, setColor() {}, setWrapping() {}, setWrappingWidth(w) { this.ww = w; }, setTextAlignment() {},
    setPosition(x, y) { this.x = x; this.y = y; }, getX() { return this.x; }, getY() { return this.y; },
    getWidth() { return this.n === "TxtProfe" ? Math.min(this.ww || 9999, this.txt.length * this.cs * 0.55) : this.w; },
    getHeight() { return this.n === "TxtProfe" ? this.cs * 1.3 * Math.ceil(Math.max(1, this.txt.length * this.cs * 0.55) / (this.ww || 9999)) : this.h; },
    setWidth(w) { this.w = w; }, setHeight(h) { this.h = h; }, clear() { this.tri = null; }, setFillColor() {}, setFillOpacity() {}, setOutlineSize() {},
    setOutlineColor() {}, setOutlineOpacity() {}, beginFillPath(x, y) { this.tri = [[x, y]]; }, drawPathLineTo(x, y) { this.tri.push([x, y]); }, closePath() {}, endFillPath() {} };
}
let reloj = 1000;
function mundo() {
  const sonidos = [], canal = { suena: null, encimadas: 0, paradas: 0 };
  const sound = {
    playSoundOnChannel: (scn, f, ch) => { if (canal.suena) canal.encimadas++; sonidos.push({ f, ch, t: reloj }); canal.suena = f; },
    stopSoundOnChannel: () => { canal.suena = null; canal.paradas++; },
  };
  const gdjs = { evtTools: { sound } };
  const datos = fs.readFileSync(path.join(__dirname, "dialogos_datos.js"), "utf8");
  vm.runInNewContext(datos + "\n" + fs.readFileSync(path.join(__dirname, "dialogo.js"), "utf8"), { gdjs, Math, Date, Map, Set, Number, Object, JSON });
  gdjs.fdizDialogo.now = () => reloj;
  gdjs.fdizDialogo.rnd = () => 0.01;                      // siempre pasa las probabilidades y elige la primera opción
  return { gdjs, D: gdjs.fdizDialogo, datos: gdjs.fdizDialogosDatos, sonidos, canal };
}
function escena(objs, sv, gl) {
  const S = cont(Object.assign({ Estado: "juego", Pausa: 0, DlgSeq: 0, DlgLinea: "", DlgHabla: "", Interruptores: 0, FinalActivo: 0, ObjNum: 1, ObjIni: 1,
    Tarjeta: 0, Apagon: 0, Horda: 0, Festin: 0, ProfJustino: "espera", ObjTipo: "llamada" }, sv));
  const G = cont(Object.assign({ NetRol: 0, SonidoActivo: 1 }, gl));
  const sc = { objs, S, cam: [500, 500], getVariables: () => S, getGame: () => ({ getVariables: () => G }),
    getObjects: (n) => objs.filter((o) => o.nombre === n),
    getLayer: (n) => ({ getCameraX: () => sc.cam[0], getCameraY: () => sc.cam[1],
      convertInverseCoords: (x, y) => [x - sc.cam[0] + 960, y - sc.cam[1] + 540], convertCoords: (x, y) => [x, y] }),
    createObject: (n) => { const h = hudObj(n); objs.push(h); return h; } };
  return sc;
}
const linea = (sc) => sc.S.get("DlgLinea").getAsString();
function correr(w, sc, seg, cada) {
  const vistas = [];
  for (let t = 0; t < seg; t += 0.1) {
    reloj += 0.1; if (cada) cada(t); w.D.tick(sc);
    const id = linea(sc);
    if (id && vistas[vistas.length - 1] !== id) vistas.push(id);
  }
  return vistas.map((id) => { const it = w.D.item(id); return it.pj + ": " + it.txt; });
}
const panel = (sc) => sc.objs.find((o) => o.n === "ProfPanel");

// ---------------------------------------------------------------- datos y voces
prueba("Voces: las 76 de audios_fish quedaron con su línea exacta (mismo personaje y mismo texto grabado), sin repetir ni sobrar", () => {
  const w = mundo(), usadas = new Set(), porArchivo = {};
  for (const carpeta of ["Alan", "Castillo", "Cesar", "Miranda", "Tony"]) {
    for (const fila of fs.readFileSync(path.join(RAIZ, "audios_fish", carpeta, "lista.txt"), "utf8").split(/\r?\n/).slice(1).filter(Boolean)) {
      const [archivo, , texto] = fila.split("\t"); porArchivo[carpeta.toLowerCase() + "/" + archivo] = norm(texto.replace(/\([^)]*\)/g, " "));
    }
  }
  const revisar = (pj, txt, voz) => {
    if (!voz) return;
    const k = voz.replace("voces/", "");
    si(k.startsWith(pj + "/"), "voz de otro personaje: " + voz);
    igual(norm(txt), porArchivo[k], voz);
    usadas.add(k);
  };
  w.datos.lineas.forEach((L) => L.cuadros.forEach((c) => revisar(L.pj, c.txt, c.voz)));
  w.datos.conversaciones.forEach((C) => C.lineas.forEach((x) => revisar(x.pj, x.txt, x.voz)));
  igual(usadas.size, 76, "relacionadas");
  igual(Object.keys(porArchivo).length, 76);
  const R = Object.fromEntries(d.resources.resources.map((r) => [r.name, r.file]));
  for (const k of usadas) { const f = R["voces/" + k]; si(f && fs.existsSync(path.join(PROY, f)), "recurso de " + k); }
});
prueba("Banco: 132 frases y 38 conversaciones; las de Gabo, Alessandro, Carlos y los profes no tienen voz pero conservan el texto", () => {
  const w = mundo();
  igual([w.datos.lineas.length, w.datos.conversaciones.length], [132, 38]);
  si(w.datos.lineas.filter((L) => ["gabo", "alessandro", "carlos", "justino", "canepa"].includes(L.pj)).every((L) => L.cuadros.every((c) => !c.voz && c.txt.length > 3)));
  const md = fs.readFileSync(path.join(RAIZ, "gdevelop", "DIALOGOS.md"), "utf8");
  si(md.includes("**falta**") && md.includes("audios_fish/Tony/tony_16_cae.wav"), "DIALOGOS.md con voces y faltantes");
});

// ---------------------------------------------------------------- momentos del juego
prueba("Cae Tony: su línea con su voz, encima de él", () => {
  const w = mundo(), t = sup(1, "tonyfuerte", 500, 500), sc = escena([t, sup(2, "gabo", 900, 500)]);
  correr(w, sc, 0.3);
  t.C.get("Estado").setString("caido");
  const v = correr(w, sc, 6);
  igual(v, ["tony: No me dejen aquí, chico. Soy joven para morir."]);
  igual(w.sonidos.map((s) => [s.f, s.ch]), [["voces/tony/tony_16_cae.wav", 7]]);
  si(panel(sc).oculto, "la burbuja se retira al terminar");
});
prueba("Revivir: habla quien levanta (Tony) y, si no tiene frase, la del que se levanta (César)", () => {
  const w = mundo(), t = sup(1, "tony", 500, 500), c = sup(2, "cesar", 560, 500, { Estado: "caido" }), sc = escena([t, c]);
  correr(w, sc, 0.3); c.C.get("Estado").setString("normal");
  igual(correr(w, sc, 6), ["tony: Ándale, párate, güey. Todavía nos faltan planes pa hoy."]);
  const w2 = mundo(), g = sup(1, "gabo", 500, 500), m = sup(2, "miranda", 560, 500, { Estado: "caido" }), sc2 = escena([g, m]);
  correr(w2, sc2, 0.3); m.C.get("Estado").setString("normal");
  igual(correr(w2, sc2, 6), ["miranda: ¿Así de real? Pensé que te habías ido AFK, menso."]);
});
prueba("Habilidades: Castillo traga con Alan cerca = conversación en orden (cada quien en su turno, una voz a la vez)", () => {
  const w = mundo(), a = sup(1, "alan", 500, 500), c = sup(2, "castillo", 620, 500), sc = escena([a, c]);
  w.D.CFG.conv = 1;                                       // siempre la conversación
  correr(w, sc, 0.3); c.C.get("HabTxt").setString("15");
  const v = correr(w, sc, 12);
  igual(v.slice(0, 2), ["alan: No manches, Castillo. ¿Ése venía en el combo o lo pediste aparte?", "castillo: Pues sí cura, bro. ¿Quieres uno?"]);
  igual(w.canal.encimadas, 0, "nunca dos voces juntas");
});
prueba("Habilidades sin compañero: Tony Modo gym (su voz); Alan Gorrear con y sin comida", () => {
  const w = mundo(), t = sup(1, "tony", 500, 500), sc = escena([t]);
  correr(w, sc, 0.3); t.C.get("EspTxt").setString("40");
  igual(correr(w, sc, 5), ["tony: A un lado, perros. Ya calenté."]);
  const w2 = mundo(), a = sup(1, "alan", 500, 500), sc2 = escena([a]);
  correr(w2, sc2, 0.3); a.C.get("HabTxt").setString("15");
  sc2.objs.push(obj("Comida", 520, 520, {}));
  igual(correr(w2, sc2, 6), ["alan: Salió comida. De uno en uno, no se amontonen."]);
  const w3 = mundo(), a3 = sup(1, "alan", 500, 500), sc3 = escena([a3]);
  correr(w3, sc3, 0.3); a3.C.get("HabTxt").setString("15");
  igual(correr(w3, sc3, 6), ["alan: Ahí va una regla. A ver si de chiripa le pegan a algo."]);
});
prueba("Eventos de equipo: apagón (Miranda), llaves recogidas (Alan), bidón (Alan), tarjeta (Carlos, sin voz)", () => {
  const w = mundo(), a = sup(1, "alan", 500, 500), m = sup(2, "miranda", 600, 500), ll = obj("Objetivo", 520, 500, { Tipo: "llaves", Usada: 0, Hecho: 0 });
  const b = obj("Bidon", 900, 500, {}), sc = escena([a, m, ll, b]);
  correr(w, sc, 0.3);
  sc.S.get("Apagon").setNumber(1);
  let v = correr(w, sc, 6); igual(v, ["miranda: ¿Quién apagó la luz? Güey, ni aire estoy viendo."]);
  ll.C.get("Hecho").setNumber(1);
  v = correr(w, sc, 6); igual(v, ["alan: Ahí están las llaves. Tanto desmadre pa un llavero."]);
  a.x = 880; sc.objs.splice(sc.objs.indexOf(b), 1);
  reloj += 50; v = correr(w, sc, 6); igual(v, ["alan: Ya recogí un bidón. Los demás nomás vienen de paseo."]);
  const w2 = mundo(), c = sup(1, "carlos", 500, 500), sc2 = escena([c]);
  correr(w2, sc2, 0.3); sc2.S.get("Tarjeta").setNumber(1);
  igual(correr(w2, sc2, 6), ["carlos: ¡Eso! Ya tenemos con qué abrir sin hacer la escena de los golpes."]);
  igual(w2.sonidos.length, 0, "Carlos no tiene voz: solo la burbuja");
});
prueba("Frase de dos cuadros (Gabo, se calma el pasillo): los dos seguidos, en orden", () => {
  const w = mundo(), g = sup(1, "gabo", 500, 500, { Kills: 0 }), z = obj("ZNormal", 600, 500, { Estado: "persigue", Aliado: 0 });
  const sc = escena([g, z]);
  correr(w, sc, 0.3);
  for (let k = 1; k <= 3; k++) { g.C.get("Kills").setNumber(k); correr(w, sc, 0.2); }
  z.C.get("Estado").setString("muerto");
  const v = correr(w, sc, 20).filter((x) => x.startsWith("gabo: Mañana") || x === "gabo: Hay exposición.");
  igual(v, ["gabo: Mañana hay que venir a la escuela después de que todo pase.", "gabo: Hay exposición."]);
});
prueba("Final y escape: líneas en orden, una a la vez; en el escape hasta dos personajes", () => {
  const w = mundo(), a = sup(1, "alan", 500, 500), m = sup(2, "miranda", 560, 500), t = sup(3, "tony", 620, 500), sc = escena([a, m, t]);
  correr(w, sc, 0.3);
  sc.S.get("FinalActivo").setNumber(1);
  const v1 = correr(w, sc, 4);
  si(v1.length === 1 && /^(alan|miranda): /.test(v1[0]), JSON.stringify(v1));
  correr(w, sc, 6);                                         // termina la línea del final
  sc.S.get("Estado").setString("victoria");
  const v2 = correr(w, sc, 14);
  igual(v2.length, 2, JSON.stringify(v2));
  igual(w.canal.encimadas, 0);
});
prueba("Sin voz para una línea: el texto se ve igual y la secuencia sigue; con voz, dura lo que la voz", () => {
  const w = mundo(), g = sup(1, "gabo", 500, 500), sc = escena([g]);
  correr(w, sc, 0.3); g.C.get("HabTxt").setString("15");
  let ini = null, fin = null;
  correr(w, sc, 8, () => { const id = linea(sc); if (id && ini === null) ini = reloj; if (!id && ini !== null && fin === null) fin = reloj; });
  si(fin - ini > 2 && fin - ini < 6.5, "dura lo que tarda leerla: " + (fin - ini));
  const w2 = mundo(), t = sup(1, "tony", 500, 500), sc2 = escena([t]);
  correr(w2, sc2, 0.3); t.C.get("Estado").setString("caido"); ini = null; fin = null;
  correr(w2, sc2, 8, () => { const id = linea(sc2); if (id && ini === null) ini = reloj; if (!id && ini !== null && fin === null) fin = reloj; });
  const dur = w2.datos.lineas.find((L) => L.cuadros[0].voz === "voces/tony/tony_16_cae.wav").cuadros[0].dur;
  si(Math.abs(fin - ini - (dur + 0.35)) < 0.25, "dura lo que la voz: " + (fin - ini) + " vs " + dur);
});
prueba("Burbuja: encima de quien habla, sin tapar el HUD, caras ni otra burbuja; cerca del borde se acomoda dentro de la pantalla", () => {
  const w = mundo(), t = sup(1, "tony", 500, 500), m = sup(2, "miranda", 560, 500), sc = escena([t, m]);
  const otra = hudObj("ProfPanel"); otra.x = 900; otra.y = 200; otra.w = 300; otra.h = 60; sc.objs.push(otra);
  correr(w, sc, 0.3); t.C.get("Estado").setString("caido"); correr(w, sc, 0.3);
  const P = sc.objs.filter((o) => o.n === "ProfPanel").find((o) => o !== otra), B = [P.x, P.y, P.x + P.w, P.y + P.h];
  const cruza = (a, b) => Math.min(a[2], b[2]) > Math.max(a[0], b[0]) && Math.min(a[3], b[3]) > Math.max(a[1], b[1]);
  const cara = (o) => { const x0 = o.getDrawableX() - sc.cam[0] + 960, y0 = o.getDrawableY() - sc.cam[1] + 540; return [x0, y0, x0 + o.w, y0 + o.h * 0.45]; };
  si(!cruza(B, cara(t)) && !cruza(B, cara(m)), "no tapa caras");
  si(!w.D.HUD.some((z) => cruza(B, z)), "no tapa el HUD");
  si(!cruza(B, [900, 200, 1200, 260]), "no tapa otra burbuja");
  si(B[3] <= cara(t)[1] + 2 || B[1] >= t.y - sc.cam[1] + 540, "encima de Tony (o debajo de sus pies si no cabe)");
  // en el borde izquierdo de la pantalla
  const w2 = mundo(), t2 = sup(1, "tony", 500, 500), sc2 = escena([t2]); sc2.cam = [500 + 960 - 30, 500];
  correr(w2, sc2, 0.3); t2.C.get("Estado").setString("caido"); correr(w2, sc2, 0.3);
  const P2 = panel(sc2); si(P2.x >= 16 && P2.x + P2.w <= 1904 && P2.y >= 16 && P2.y + P2.h <= 1064, "dentro de la pantalla");
});
prueba("Pausa y charla con Canepa: se retira la burbuja, se corta la voz y no se acumulan líneas", () => {
  const w = mundo(), t = sup(1, "tony", 500, 500), sc = escena([t]);
  correr(w, sc, 0.3); t.C.get("Estado").setString("caido"); correr(w, sc, 0.5);
  si(linea(sc) && w.canal.suena, "hablando");
  sc.S.get("Pausa").setNumber(1); correr(w, sc, 0.3);
  igual([linea(sc), w.canal.suena, panel(sc).oculto], ["", null, true]);
  sc.S.get("Pausa").setNumber(0); sc.S.get("CanepaCharla").setNumber(1); t.C.get("Estado").setString("normal"); correr(w, sc, 0.3);
  t.C.get("Estado").setString("caido"); correr(w, sc, 3);
  igual(linea(sc), "", "durante la charla no hay diálogos");
});
prueba("En línea: el cliente no detecta nada, pero muestra la burbuja y pone la voz que manda el host", () => {
  const w = mundo(), t = sup(1, "tony", 500, 500), sc = escena([t], {}, { NetRol: 2 });
  correr(w, sc, 0.3); t.C.get("Estado").setString("caido"); correr(w, sc, 1);
  igual(linea(sc), "", "no decide");
  const i = w.datos.lineas.findIndex((L) => L.cuadros[0].voz === "voces/tony/tony_16_cae.wav");
  sc.S.get("DlgLinea").setString("l:" + i + ":0"); sc.S.get("DlgHabla").setString("sup:1"); sc.S.get("DlgSeq").setNumber(5);
  correr(w, sc, 0.2);
  si(!panel(sc).oculto && sc.objs.some((o) => o.n === "TxtProfe" && o.txt.includes("Soy joven para morir")));
  igual(w.sonidos.map((s) => s.f), ["voces/tony/tony_16_cae.wav"]);
});
prueba("Intro: las líneas de antes de la alerta las dicen (con voz) los del equipo; se quita la línea «Tony: …» del texto", () => {
  const w = mundo(), t = sup(1, "tony", 500, 500), a = sup(2, "alan", 600, 500), c = sup(3, "castillo", 700, 500);
  const txt = hudObj("TxtDialogo"); txt.n = "TxtDialogo";
  const sc = escena([t, a, c, txt], { Estado: "intro" });
  const v = correr(w, sc, 10, (s) => { if (s < 0.15) txt.txt = "Tony: ¿Por qué no llega el profe?"; });
  igual(txt.txt, "", "la línea de la intro la reemplaza la burbuja");
  igual(v.length, 3, JSON.stringify(v));
  igual(new Set(v.map((x) => x.split(":")[0])).size, 3, "tres personajes distintos");
  si(w.sonidos.length === 3 && w.canal.encimadas === 0, "con voz y una a la vez");
});

// ---------------------------------------------------------------- proyecto
prueba("Proyecto: datos y módulo arriba de Juego, el tick después de la cinemática, variables en la red", () => {
  const top = J.events.map((e) => (e.inlineCode || "").slice(0, 24));
  const da = top.findIndex((s) => s.startsWith("/*FDIZ-FASE64-DATOS")), mo = top.findIndex((s) => s.startsWith("/*FDIZ-FASE64-MOD"));
  const cin = J.events.findIndex((e) => (e.name || "").startsWith("Cinemática de inicio"));
  si(da >= 0 && mo === da + 1 && top[cin + 1].startsWith("/*FDIZ-FASE64-TICK"), [da, mo, cin]);
  const T = d.layouts.find((l) => l.name === "Titulo");
  const rec = function* (evs) { for (const e of evs || []) { yield e; yield* rec(e.events); } };
  const n = [...rec(T.events)].find((e) => (e.inlineCode || "").includes("gdjs.fdizNetCfg="));
  const cfg = JSON.parse(n.inlineCode.match(/gdjs\.fdizNetCfg=(\{[\s\S]*?\});\n/)[1]);
  for (const v of ["DlgSeq", "DlgLinea", "DlgHabla"]) si(cfg.sv.includes(v) && J.variables.some((x) => x.name === v), v);
});

console.log(ok + " correctas, " + mal + " fallidas");
process.exit(mal ? 1 : 0);
