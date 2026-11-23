/* FDI-Z · Fase 56 · Interacción con F (o A del mando): una sola acción a la vez.
 * Se incrusta en la escena Juego con scripts/fase56_interaccion.py (no editar el evento a mano: editar este archivo y volver a correr el script).
 * Define gdjs.fdizUsar.
 *
 * Antes, mantener Usar (F / A) hacía TODO lo que estuviera a su alcance a la vez: abrir una puerta, levantar a un caído,
 * curar a un mordido, usar un objetivo y revisar un locker. Además R abría puertas (y también lanza objetos).
 * Ahora, para cada jugador humano, este módulo elige UN objetivo interactuable:
 *   - candidatos dentro del alcance de cada acción (los mismos de los eventos): levantar a un caído 80 px, curar a un
 *     mordido 95 px, abrir una puerta 130 px (desde los pies al centro de la puerta), usar un objetivo 140 px y revisar un
 *     locker o mochila 95 px (centro a centro), hablar con un profe 115 px;
 *   - gana el de menor distancia relativa a su alcance (d / alcance); salvar a alguien pesa x0.75 (es urgente);
 *   - mientras se mantiene Usar se conserva el objetivo elegido (no salta a otro a la mitad), si sigue a su alcance.
 * Solo el elegido avanza: el módulo pone en el Sup una sola bandera Usa<Acción> = 1 y marca la puerta u objetivo elegido
 * (Elegida = 1). Los eventos de cada acción leen su bandera en vez de Usando. Puertas restringidas sin derribar
 * (TiempoAbrir 0) no se pueden abrir con F: solo se avisa. Los bots (y los profes aliados) siguen como antes: todas sus
 * banderas = Usando y todas las puertas / objetivos a su alcance quedan elegidos.
 * Indicación: "Mantén F para abrir" (A en mando) sobre cada jugador local, con barra de progreso mientras lo mantiene.
 * Autoridad: el host (o sin red) elige. Accion, UsarTxt y UsarProg se sincronizan; todos dibujan la indicación de sus
 * jugadores locales. */
(function (gdjs) {
  "use strict";
  if (gdjs.fdizUsar && gdjs.fdizUsar.VER === 1) return;
  const U = (gdjs.fdizUsar = { VER: 1 });

  U.CFG = {
    alcance: { revivir: 80, curar: 95, puerta: 130, objetivo: 140, cofre: 95, profe: 115, bloqueada: 130 },
    pesoSalvar: 0.75,      // levantar / curar ganan a una puerta u objeto que esté un poco más cerca
    revivirSeg: 3, curaSeg: 3, cofreSeg: 1,
  };
  const BANDERAS = { revivir: "UsaRevivir", curar: "UsaCurar", puerta: "UsaPuerta", objetivo: "UsaObjetivo", cofre: "UsaCofre" };
  const OBJ_TXT = {   // qué se hace con cada objetivo
    servidor: "prender el servidor", computadora: "llamar", llaves: "tomar las llaves", interruptor: "activar el interruptor",
    carnada: "dejar la comida", camion: "cargar la gasolina", canepa: "hablar con Canepa",
    h_telefono: "usar el teléfono", h_casillero: "revisar el casillero", h_cajon: "revisar el escritorio",   // fase 68 (Historia)
  };

  const V = (o, n) => o.getVariables().get(n);
  const num = (o, n) => V(o, n).getAsNumber();
  const str = (o, n) => V(o, n).getAsString();
  const lista = (scn, n) => scn.getObjects(n) || [];
  const dPos = (a, x, y) => Math.hypot(a.getX() - x, a.getY() - y);
  const dCentro = (a, b) => Math.hypot(a.getDrawableX() + a.getCenterX() - b.getDrawableX() - b.getCenterX(),
                                        a.getDrawableY() + a.getCenterY() - b.getDrawableY() - b.getCenterY());
  const humano = (s) => { const c = num(s, "Control"); return (c >= 0 || c === -3) && num(s, "Jugador") <= 4; };
  const nombreSup = (s) => { const j = num(s, "Jugador"); if (j <= 4) return "P" + j; const n = str(s, "Personaje"); return n ? n.charAt(0).toUpperCase() + n.slice(1) : "tu compañero"; };

  // ------------------------------------------------------------------ candidatos de un jugador
  function candidatos(scn, s, sups) {
    const A = U.CFG.alcance, out = [];
    for (const o of sups) {
      if (o === s) continue;
      const d = dPos(o, s.getX(), s.getY());
      if (str(o, "Estado") === "caido" && d < A.revivir) out.push({ t: "revivir", o, d, r: A.revivir });
      else if (str(o, "Estado") === "normal" && num(o, "Mordido") === 1 && d < A.curar) out.push({ t: "curar", o, d, r: A.curar });
    }
    for (const p of lista(scn, "Puerta")) {
      const d = dPos(s, p.getX() + p.getWidth() / 2, p.getY() + p.getHeight() / 2);
      if (d >= A.puerta) continue;
      if (num(p, "TiempoAbrir") > 0) out.push({ t: "puerta", o: p, d, r: A.puerta });
      else out.push({ t: "bloqueada", o: p, d, r: A.bloqueada });
    }
    for (const g of lista(scn, "Objetivo")) {
      if (num(g, "Hecho") !== 0 || num(g, "Tiempo") >= 999) continue;        // el camión del final no se "usa"
      if (gdjs.fdizHistoria && !gdjs.fdizHistoria.puedeUsar(scn, s, g)) continue;   // fase 69: Historia, solo desde dentro de la sala y con su puerta abierta
      const d = dCentro(s, g); if (d < A.objetivo) out.push({ t: "objetivo", o: g, d, r: A.objetivo });
    }
    for (const c of lista(scn, "Contenedor")) {
      if (num(c, "Abierto") !== 0) continue;
      const d = dCentro(s, c); if (d < A.cofre) out.push({ t: "cofre", o: c, d, r: A.cofre });
    }
    for (const p of lista(scn, "Profe")) {
      const e = str(p, "Estado"); if (e !== "espera" && e !== "conversacion") continue;
      if (gdjs.fdizCanepa && gdjs.fdizCanepa.reservado(scn, str(p, "Nombre"))) continue;   // fase 61: en Historia, primero la charla
      if (gdjs.fdizHistoria && gdjs.fdizHistoria.reservado(scn, str(p, "Nombre"))) continue;   // fase 68: los profes van por la historia
      const d = dPos(p, s.getX(), s.getY()); if (d < A.profe) out.push({ t: "profe", o: p, d, r: A.profe });
    }
    return out;
  }
  function puntaje(c) {
    let k = c.d / c.r;
    if (c.t === "revivir" || c.t === "curar") k *= U.CFG.pesoSalvar;
    if (c.t === "bloqueada") k += 1;                                         // solo avisa si no hay otra cosa
    return k;
  }
  function vigente(scn, s, c, sups) {   // el objetivo que se venía manteniendo, ¿sigue valiendo?
    if (!c || !c.o || c.o._livingOnScene === false) return null;
    const lst = candidatos(scn, s, sups);
    return lst.find((x) => x.o === c.o && x.t === c.t) || null;
  }

  function texto(c) {
    switch (c.t) {
      case "revivir": return "salvar a " + nombreSup(c.o);
      case "curar": return "curar a " + nombreSup(c.o);
      case "puerta": return str(c.o, "Tipo") === "electronica" && num(c.o, "TiempoAbrir") > 1 ? "abrir (electrónica, " + Math.round(num(c.o, "TiempoAbrir")) + " s)" : "abrir";
      case "objetivo": return OBJ_TXT[str(c.o, "Tipo")] || "usar";
      case "cofre": return "revisar";
      case "bloqueada": { const v = c.o.getVariables(), q = v.has && v.has("Bloqueo") ? str(c.o, "Bloqueo") : ""; return q && q !== "0" ? q : "!Puerta restringida: derríbala a golpes"; }   // fase 68: Bloqueo = aviso propio (Historia)
      default: return "";
    }
  }
  function progreso(c) {
    const o = c.o, K = U.CFG;
    switch (c.t) {
      case "revivir": return num(o, "Revivir") / K.revivirSeg;
      case "curar": return num(o, "Cura") / K.curaSeg;
      case "puerta": return num(o, "TiempoAbrir") > 0 ? num(o, "Progreso") / num(o, "TiempoAbrir") : 0;
      case "objetivo": return num(o, "Tiempo") > 0 ? num(o, "Progreso") / num(o, "Tiempo") : 0;
      case "cofre": return num(o, "Progreso") / K.cofreSeg;
      default: return 0;
    }
  }

  // ------------------------------------------------------------------ host / sin red: elegir (antes de las puertas)
  U.elegir = function (scn) {
    const st = scn._fdizUsar || (scn._fdizUsar = { fijo: new Map(), soltar: new Set() });
    const sups = lista(scn, "Sup");
    for (const p of lista(scn, "Puerta")) V(p, "Elegida").setNumber(0);
    for (const g of lista(scn, "Objetivo")) V(g, "Elegida").setNumber(0);
    for (const s of sups) {
      const usa = num(s, "Usando") === 1 && str(s, "Estado") === "normal";
      if (!humano(s)) {                                     // bots y profes: como antes
        for (const k in BANDERAS) V(s, BANDERAS[k]).setNumber(usa ? 1 : 0);
        if (usa) {
          for (const p of lista(scn, "Puerta")) if (dPos(s, p.getX() + p.getWidth() / 2, p.getY() + p.getHeight() / 2) < U.CFG.alcance.puerta) V(p, "Elegida").setNumber(1);
          for (const g of lista(scn, "Objetivo")) if (dCentro(s, g) < U.CFG.alcance.objetivo && !(gdjs.fdizHistoria && !gdjs.fdizHistoria.puedeUsar(scn, s, g))) V(g, "Elegida").setNumber(1);
        }
        V(s, "Accion").setString(""); V(s, "UsarTxt").setString(""); V(s, "UsarProg").setNumber(0);
        continue;
      }
      let c = null;
      if (!usa) st.soltar.delete(s);
      if (str(s, "Estado") === "normal") {
        const prev = st.fijo.get(s);
        c = usa && prev ? vigente(scn, s, prev, sups) : null;
        // terminó (o se fue de alcance) lo que se venía manteniendo: hay que soltar F antes de empezar otra cosa,
        // así una misma pulsación nunca salva a alguien y luego abre una puerta
        if (usa && prev && !c) st.soltar.add(s);
        if (!c) {
          let best = null, bk = 1e9;
          for (const x of candidatos(scn, s, sups)) { const k = puntaje(x); if (k < bk) { bk = k; best = x; } }
          c = best;
        }
      }
      const espera = usa && st.soltar.has(s);
      if (usa && !espera && c && c.t !== "bloqueada" && c.t !== "profe") st.fijo.set(s, c); else st.fijo.delete(s);
      for (const k in BANDERAS) V(s, BANDERAS[k]).setNumber(usa && !espera && c && c.t === k ? 1 : 0);
      if (usa && !espera && c && (c.t === "puerta" || c.t === "objetivo")) V(c.o, "Elegida").setNumber(1);
      V(s, "Accion").setString(c ? c.t : "");
      V(s, "UsarTxt").setString(espera ? "!Suelta " + "{K}" + " para la siguiente acción" : (c && c.t !== "profe" ? texto(c) : ""));
      V(s, "UsarProg").setNumber(c && usa && !espera ? Math.max(0, Math.min(1, progreso(c))) : 0);
    }
    for (const s of st.fijo.keys()) if (sups.indexOf(s) < 0) st.fijo.delete(s);
    for (const s of st.soltar) if (sups.indexOf(s) < 0) st.soltar.delete(s);
  };

  // ¿Este jugador puede hacer esta acción? (lo usa profes.js para no abrir el diálogo si F es para otra cosa)
  U.permite = function (s, tipo) {
    try { const a = str(s, "Accion"); return a === "" || a === tipo; } catch (e) { return true; }
  };

  // ------------------------------------------------------------------ todos: indicación sobre los jugadores locales
  U.dibujar = function (scn) {
    const st = scn._fdizUsarUI || (scn._fdizUsarUI = { txt: [], dib: null });
    if (!st.dib) {
      st.dib = scn.createObject("UsarDib");
      if (st.dib) { st.dib.setLayer("HUD"); st.dib.setPosition(0, 0); st.dib.setZOrder(404); }
    }
    const D = st.dib; if (D) { D.clear(); D.setOutlineSize(0); }
    let n = 0;
    const enJuego = (() => { try { const v = scn.getVariables(); return v.get("Estado").getAsString() === "juego" && v.get("Pausa").getAsNumber() === 0 && v.get("ProfDlg").getAsNumber() === 0; } catch (e) { return true; } })();
    const LJ = scn.getLayer("Juego"), LH = scn.getLayer("HUD");
    if (enJuego) for (const s of lista(scn, "Sup")) {
      const ctl = num(s, "Control");
      if (ctl < 0 || ctl > 4 || num(s, "Jugador") > 4 || s.isHidden() || str(s, "Estado") !== "normal") continue;   // solo jugadores de esta máquina
      const frase = str(s, "UsarTxt"); if (!frase) continue;
      const tecla = ctl === 0 ? "F" : "A";
      const msg = (frase.charAt(0) === "!" ? frase.slice(1) : "Mantén {K} para " + frase).replace("{K}", tecla);
      const c = LJ.convertInverseCoords(s.getX(), s.getY() - 128, 0), p = LH.convertCoords(c[0], c[1], 0);
      let t = st.txt[n];
      if (!t) { t = st.txt[n] = scn.createObject("TxtUsar"); if (!t) break; t.setLayer("HUD"); }
      n++;
      t.hide(false);
      if (t._k !== msg) { t.setText(msg); t._k = msg; }
      if (t.setTextAlignment) t.setTextAlignment("center");
      t.setColor(frase.charAt(0) === "!" ? "255;150;120" : "255;240;170");
      t.setPosition(Math.round(p[0] - t.getWidth() / 2), Math.round(p[1] - t.getHeight()));
      t.setZOrder(405);
      const pr = num(s, "UsarProg");
      if (D && pr > 0) {
        const w = Math.max(90, t.getWidth()), x0 = Math.round(p[0] - w / 2), y0 = Math.round(p[1] + 4);
        D.setFillOpacity(220); D.setFillColor("12;14;24"); D.drawRectangle(x0 - 2, y0 - 2, x0 + w + 2, y0 + 8);
        D.setFillOpacity(255); D.setFillColor("120;230;140"); D.drawRectangle(x0, y0, x0 + w * pr, y0 + 6);
      }
    }
    for (let i = n; i < st.txt.length; i++) if (st.txt[i]) st.txt[i].hide(true);
  };
})(gdjs);
