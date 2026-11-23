// Pruebas de la fase 68 (Modo Historia de 12 pasos), sin GDevelop:  node gdevelop/scripts/prueba_historia2.js
// 1) La secuencia de historia.js es la del documento 02_HISTORIA_PARA_GDEVELOP.md (videos [V] y audios [D]/[G], en orden).
// 2) Los 55 audios de 01_DIALOGOS_PARA_VOCES.md están en los datos, con archivo y duración, y cada uno se usa una vez.
// 3) El proyecto tiene los eventos, objetos, variables y recursos de la fase 68, y Escape/Jefe conservan su final de 60 s.
"use strict";
const fs = require("fs"), path = require("path");
const AQUI = __dirname, RAIZ = path.join(AQUI, "..", "..");
let ok = 0, mal = 0;
const prueba = (nombre, cond, extra) => { if (cond) { ok++; console.log("  OK   " + nombre); } else { mal++; console.log("  MAL  " + nombre + (extra ? " -> " + extra : "")); } };

global.gdjs = {};
require(path.join(AQUI, "historia_datos.js"));
require(path.join(AQUI, "historia.js"));
const H = gdjs.fdizHistoria, D = gdjs.fdizHistoriaDatos;

// ---------------------------------------------------------------- 1) orden del documento
const doc = fs.readFileSync(path.join(RAIZ, "gdevelop", "historia", "02_HISTORIA_PARA_GDEVELOP.md"), "utf8");
const pasosDoc = {};
let n = 0;
for (const linea of doc.split(/\r?\n/)) {
  const m = linea.match(/^### PASO (\d+)/); if (m) { n = +m[1]; pasosDoc[n] = []; continue; }
  if (/^### Derrota/.test(linea)) n = 0;
  if (!n) continue;
  // fase 72: en la versión final una línea puede traer videos y diálogos mezclados ([V] C01_T1 → [D] ... → [V] C01_T2 → ...)
  if (/\[[VDG]\]/.test(linea)) for (const a of linea.matchAll(/`(C[0-9_T]+)\.mp4`|`([A-Z0-9]+_[0-9]+_[a-z]+)`/g)) {
    if (a[1]) { if (/\[V\]/.test(linea)) pasosDoc[n].push("v:" + a[1]); }
    else pasosDoc[n].push((/\[G\]/.test(linea) ? "g:" : "d:") + a[2]);
  }
}
for (let k = 1; k <= 12; k++) {
  const nuestro = [];
  for (const it of H.PASOS[k].seq) { if (it[0] === "v") nuestro.push("v:" + it[1]); if (it[0] === "d") for (const l of it.slice(1)) nuestro.push("d:" + l); }
  // los [G] del documento van en el paso donde se escuchan: J1 durante el objetivo del paso 5, J2 durante el del 7
  for (const c of H.CHARLAS) if (c.paso - 1 === k) for (const l of c.lineas) nuestro.push("g:" + l);
  if (k === 12) nuestro.push("d:C10_03_tony");   // en Resultados, sobre la pantalla de victoria (evento FDIZ-FASE68-RES)
  const esperado = pasosDoc[k] || [];
  prueba("Paso " + k + ": videos y diálogos en el orden del documento", JSON.stringify(nuestro) === JSON.stringify(esperado),
    JSON.stringify(nuestro) + " != " + JSON.stringify(esperado));
}
prueba("Paso 1 empieza solo con fundido desde negro", H.PASOS[1].auto && H.PASOS[1].seq[0][0] === "fade");
prueba("Objetivos del documento", H.PASOS[2].obj.txt === "Revisa el escritorio del profe" && H.PASOS[5].obj.txt === "Llega al CIC" &&
  H.PASOS[7].obj.txt === "Encuentra la sala del conserje" && H.PASOS[9].obj.txt === "Busca a otro profesor: la nevería" &&
  H.PASOS[10].obj.txt === "Consigue la llave en la oficina del director" && H.PASOS[11].obj.txt === "Llega al autobús");
prueba("Disparadores: zonas y 'usar' del documento", H.PASOS[2].obj.zona === "Escritorio" && H.PASOS[5].obj.zona === "CIC" && H.PASOS[6].obj.usar === "Telefono" &&
  H.PASOS[7].obj.zona === "Conserje" && H.PASOS[8].obj.usar === "Casillero" && H.PASOS[9].obj.zona === "Neveria" &&
  H.PASOS[10].obj.zona === "Direccion" && H.PASOS[10].obj.usar === "CajonDirector" && H.PASOS[11].obj.zona === "Autobus" &&
  H.CHARLAS[0].zona === "Pasillo1");
prueba("Las 10 zonas del documento existen", ["Escritorio", "Pasillo1", "CIC", "Conserje", "Neveria", "Direccion", "Autobus"].every((z) => H.ZONAS[z]) &&
  ["Telefono", "Casillero", "CajonDirector"].every((z) => H.USAR[z]));
prueba("Defensa final de 90 s", H.FINAL_SEG === 90);
prueba("Colores de los nombres del documento", H.COLORES.tony === "255;255;255" && H.COLORES.altavoz.startsWith("255;70") && Object.keys(H.COLORES).length === 8);

// ---------------------------------------------------------------- 2) audios
const tabla = fs.readFileSync(path.join(RAIZ, "gdevelop", "historia", "01_DIALOGOS_PARA_VOCES.md"), "utf8");
const ids = [...tabla.matchAll(/\|\s*`([A-Za-z0-9_]+)\.mp3`/g)].map((m) => m[1]);
prueba("55 audios en el documento y en los datos", ids.length === 55 && ids.every((i) => D.lineas[i]), ids.length);
const sinAudio = ids.filter((i) => !D.lineas[i] || !D.lineas[i].audio || !(D.lineas[i].dur > 0));
prueba("Cada línea tiene su archivo y duración", !sinAudio.length, sinAudio.join(","));
const usados = [];
for (const k in H.PASOS) for (const it of H.PASOS[k].seq) if (it[0] === "d") usados.push(...it.slice(1));
for (const c of H.CHARLAS) usados.push(...c.lineas);
usados.push("C10_03_tony");   // se dice en Resultados, sobre la pantalla de victoria
// fase 72: líneas de la versión final sin voz propia (H.EXTRA): cuentan como uso de la voz en que se basan
for (const [id, e] of Object.entries(H.EXTRA || {})) { const k = usados.indexOf(id); if (k >= 0) usados.splice(k, 1, ...(e.de && !e.sinVoz ? [e.de] : [])); }
for (const [, e] of Object.entries(H.EXTRA || {})) if (e.de && e.sinVoz) usados.push(e.de);   // C5_01_cesar: su texto lo dice Tony
prueba("Cada audio se usa exactamente una vez", usados.length === 55 && new Set(usados).size === 55 && ids.every((i) => usados.includes(i)),
  ids.filter((i) => !usados.includes(i)).join(","));
const proy = path.join(RAIZ, "gdevelop", "FDI-Z");
prueba("Los archivos de audio existen en assets/historia/audio", ids.every((i) => fs.existsSync(path.join(proy, "assets", "historia", "audio", i + ".mp3"))));
prueba("Textos exactos (sin marcas de énfasis)", D.lineas.INT_03_cesar.txt === "Está en mi reglamento." && D.lineas.C2_03_altavoz.pj === "altavoz");

// ---------------------------------------------------------------- 3) proyecto
const P = JSON.parse(fs.readFileSync(path.join(proy, "FDI-Z.json"), "utf8"));
const J = P.layouts.find((l) => l.name === "Juego");
const rec = function* (l) { for (const e of l) { yield e; yield* rec(e.events || []); } };
const js = (marca) => [...rec(J.events)].filter((e) => (e.type || "").endsWith("JsCode") && e.inlineCode.startsWith("/*" + marca + "*/"));
prueba("Eventos DATOS, MOD, TICK y TRAS una sola vez", ["DATOS", "MOD", "TICK", "TRAS"].every((k) => js("FDIZ-FASE68-" + k).length === 1));
const top = J.events, idx = (f) => top.findIndex(f);
const iTick = idx((e) => (e.inlineCode || "").startsWith("/*FDIZ-FASE68-TICK*/")), i65 = idx((e) => (e.inlineCode || "").startsWith("/*FDIZ-FASE65-TICK*/"));
const iTras = idx((e) => (e.inlineCode || "").startsWith("/*FDIZ-FASE68-TRAS*/")), iComb = idx((e) => e.name === "Combate: pegar");
const iObj = idx((e) => e.name === "Objetivos y flecha");
prueba("El tick va justo después del de la fase 65 y antes de los objetivos; TRAS antes de 'Combate: pegar'", iTick === i65 + 1 && iTick < iObj && iTras === iComb - 1);
prueba("El módulo incrustado es historia.js", js("FDIZ-FASE68-MOD")[0].inlineCode.endsWith(fs.readFileSync(path.join(AQUI, "historia.js"), "utf8")));
const fin = top.find((e) => e.name === "Final ¡Aguanten!");
const vic = fin.events.find((e) => (e.actions || []).some((a) => a.parameters[0] === "Estado" && a.parameters[2] === '"victoria"'));
prueba("Victoria del final: dura FinalSeg y en Historia la maneja el paso 12",
  vic.conditions.some((c) => c.type.value === "CompareTimer" && c.parameters[3] === "Variable(FinalSeg)") &&
  vic.conditions.some((c) => c.type.value === "VarGlobalTxt" && c.parameters.join() === 'Modo,!=,"historia"'));
prueba("FinalSeg vale 60 por omisión (Escape y Jefe igual que antes)", J.variables.find((v) => v.name === "FinalSeg").value === 60);
const objEv = [...rec(top[iObj].events)].find((e) => (e.conditions || []).some((c) => c.parameters[0] === "HistDefensa"));
prueba("Los objetivos de Escape no corren en Historia hasta la defensa", !!objEv && objEv.actions.some((a) => a.parameters.join() === "ObjNum,=,0"));
const nombres = new Set(J.objects.map((o) => o.name));
prueba("Objetos HistDib, TxtHist, HistRetrato y los videos que existen", ["HistDib", "TxtHist", "HistRetrato"].every((o) => nombres.has(o)) &&
  Object.values(D.videos).every((o) => nombres.has(o)));
const res = new Set(P.resources.resources.map((r) => r.name));
prueba("Recursos: 55 audios y la alarma", ids.every((i) => res.has("historia/audio/" + i + ".mp3")) && res.has("efectos/eventos/alarma_loop.wav"));
const hist = P.variables.find((v) => v.name === "Historia");
prueba("Variable global Historia (Paso, CinematicasVistas, Armas, Final)", hist && hist.type === "structure" &&
  ["Paso", "CinematicasVistas", "Armas", "Final"].every((k) => hist.children.some((c) => c.name === k)));
const T = P.layouts.find((l) => l.name === "Titulo");
const nucleo = [...rec(T.events)].find((e) => (e.inlineCode || "").includes("gdjs.fdizNetCfg="));
prueba("En línea: las variables Hist* viajan a los clientes", ["HistCine", "HistLinea", "HistHabla", "HistAlarma"].every((k) => nucleo.inlineCode.includes('"' + k + '"')));
for (const [marca, archivo] of [["FDIZ-FASE56-MOD", "usar.js"], ["FDIZ-FASE40-MOD", "profes.js"], ["FDIZ-FASE64-MOD", "dialogo.js"], ["FDIZ-FASE65-MOD", "cine.js"]])
  prueba("Re-incrustado " + archivo + " con sus ganchos", js(marca).length === 1 && js(marca)[0].inlineCode === "/*" + marca + "*/\n" + fs.readFileSync(path.join(AQUI, archivo), "utf8"));
const R = P.layouts.find((l) => l.name === "Resultados");
prueba("Resultados: REINICIAR ya no usa if(...) (cambiaba a la escena vacía)", !JSON.stringify(R.events).includes("if(GlobalVariable(NetRol)"));
const M = P.layouts.find((l) => l.name === "Menu");
prueba("Menú: elegir HISTORIA reinicia la historia desde el paso 1", [...rec(M.events)].some((e) => (e.inlineCode || "").startsWith("/*FDIZ-FASE68-MENU*/")));

console.log(ok + " correctas, " + mal + " fallidas");
process.exit(mal ? 1 : 0);
