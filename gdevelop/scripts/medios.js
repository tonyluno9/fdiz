/* FDI-Z · Fase 46 · Bloque Medios (reporte de pruebas de jugabilidad).
 * Se incrusta en un evento JavaScript de la escena Juego con scripts/fase46_medios.py. No editar el evento a mano.
 *
 *  4) M.borde(scn): qué personajes se dibujan por delante de la oscuridad de los salones (capa SupervivientesBorde). Antes usaba el
 *     tamaño del dibujo (cambia con cada cuadro de la animación y con el volteo), así que un personaje en el borde saltaba
 *     entre capas y parpadeaba. Ahora usa una caja fija a partir de los pies y espera 3 cuadros antes de cambiar de capa.
 *  5) M.anim(scn, objs): elige la animación de caminar (lado / arriba / abajo / quieto) y el volteo con histéresis. Antes
 *     comparaba |vx| con |vy| en cada cuadro: en diagonal o rozando una pared cambiaba de animación cada cuadro (reinicia la
 *     caminata) y volteaba al personaje por velocidades casi nulas.
 *  6) M.llaves(scn, objs): las llaves de la conserjería solo las toma un jugador humano (no los bots); se avisa con un texto cuando
 *     un humano está cerca, muestra el progreso con su nombre y al terminar sale el aviso "¡<Nombre> tomó las llaves!".
 */
(function (gdjs) {
  "use strict";
  if (gdjs.fdizMedios && gdjs.fdizMedios.VER === 1) return;
  const M = (gdjs.fdizMedios = { VER: 1 });

  M.CFG = {
    caja: { izq: 26, der: 26, arriba: 100, abajo: 6 },   // caja del personaje respecto de sus pies (px)
    cuadros: 3,                                          // cuadros seguidos que debe pedirse otra capa para cambiar
    histeresis: 1.3,                                     // |vx| debe superar a |vy| x 1.3 (o al revés) para cambiar de eje
    vMin: 12,                                            // velocidad mínima (px/s) para cambiar el volteo / arriba-abajo
    llaveCerca: 220, llaveUsar: 140,                     // px: aviso y alcance para tomar las llaves
  };

  const NOMBRES = { tony: "Tony", miranda: "Miranda", cesar: "César", alan: "Alan", castillo: "Castillo", alessandro: "Alessandro", gabo: "Gabo", carlos: "Carlos", tonyfuerte: "Tony" };
  const NAMES = ["Sup", "Profe", "ZNormal", "ZCorredor", "ZGriton", "ZGordo", "ZConserje", "ZCurado", "ZJoel", "ZJustino", "ZCanepa"];
  const num = (o, n) => o.getVariables().get(n).getAsNumber();
  const str = (o, n) => o.getVariables().get(n).getAsString();

  // ---------- 4) capa de los personajes junto a la oscuridad de los salones ----------
  M.borde = function (scn) {
    const K = M.CFG.caja;
    const capa = scn.getLayer("NieblaSalas");
    const zonas = [];
    if (capa && capa.isVisible()) {
      for (const n of scn.getObjects("Niebla") || []) {
        if (n.isHidden() || n.getOpacity() <= 0) continue;
        const x = n.getX(), y = n.getY();
        zonas.push([x, y, x + n.getWidth(), y + n.getHeight()]);
      }
    }
    for (const nombre of NAMES) {
      for (const p of scn.getObjects(nombre) || []) {
        const px = p.getX(), py = p.getY();
        const izq = px - K.izq, der = px + K.der, arr = py - K.arriba, aba = py + K.abajo;
        let cruza = false;
        for (const z of zonas) {
          if (z[0] <= px && px < z[2] && z[1] <= py && py < z[3]) { cruza = false; break; }   // con los pies dentro, la sala lo tapa
          if (izq < z[2] && z[0] < der && arr < z[3] && z[1] < aba) cruza = true;
        }
        const quiere = cruza ? "SupervivientesBorde" : "Juego";
        const st = p.__f46b || (p.__f46b = { n: 0 });
        if (p.getLayer() === quiere) { st.n = 0; continue; }
        if (++st.n >= M.CFG.cuadros) { p.setLayer(quiere); st.n = 0; }
      }
    }
  };

  // ---------- 5) animación de caminar ----------
  M.anim = function (scn, objs) {
    const C = M.CFG;
    for (const s of objs) {
      const td = s.getBehavior("TopDownMovement");
      if (!td) continue;
      const pj = str(s, "Personaje");
      const st = s.__f46a || (s.__f46a = { eje: null, vert: "abajo", flip: false });
      let nombre, flip = st.flip;
      if (td.isMoving()) {
        const vx = td.getXVelocity(), vy = td.getYVelocity(), ax = Math.abs(vx), ay = Math.abs(vy);
        if (st.eje === null) st.eje = ax > ay ? "x" : "y";
        else if (st.eje === "x" && ay > ax * C.histeresis) st.eje = "y";
        else if (st.eje === "y" && ax > ay * C.histeresis) st.eje = "x";
        if (st.eje === "x") {
          nombre = pj + "_caminar_lado";
          if (vx < -C.vMin) st.flip = true; else if (vx > C.vMin) st.flip = false;
          flip = st.flip;
        } else {
          if (vy < -C.vMin) st.vert = "arriba"; else if (vy > C.vMin) st.vert = "abajo";
          nombre = pj + "_caminar_" + st.vert;
          flip = false;
        }
      } else {
        st.eje = null;
        nombre = pj + "_quieto"; flip = false;
      }
      if (s.getAnimationName() !== nombre) s.setAnimationName(nombre);
      if (s.isFlippedX() !== flip) s.flipX(flip);
    }
  };

  // ---------- 6) llaves: solo las toma un humano, con aviso claro ----------
  const humano = (s) => { const c = num(s, "Control"); return (c >= 0 || c === -3) && str(s, "Estado") === "normal"; };
  function texto(scn, nombre, s) {
    const t = (scn.getObjects(nombre) || [])[0];
    if (t) t.setText(s);
  }
  function banner(scn, txt, seg) {
    const V = scn.getVariables(); V.get("Banner").setString(txt); V.get("BannerSeg").setNumber(seg || 2.5);
    try { gdjs.evtTools.runtimeScene.resetTimer(scn, "banner"); } catch (e) { /* sin temporizador: no pasa nada */ }
  }
  function ayuda(scn, txt) {
    texto(scn, "TxtAyuda", txt);
    try { gdjs.evtTools.runtimeScene.resetTimer(scn, "ayuda"); } catch (e) { /* ídem */ }
  }
  const quien = (s) => (NOMBRES[str(s, "Personaje")] || str(s, "Personaje")) + " (P" + num(s, "Jugador") + ")";

  M.llaves = function (scn, objs) {
    const C = M.CFG, sups = scn.getObjects("Sup") || [];
    for (const o of objs) {
      if (str(o, "Tipo") !== "llaves") continue;
      const st = o.__f46k || (o.__f46k = { prev: 0, aviso: -9 });
      const V = o.getVariables(), prog = V.get("Progreso"), usada = V.get("Usada");
      const tiempo = Math.max(0.01, V.get("Tiempo").getAsNumber());
      const dist = (s) => Math.hypot(s.getX() - o.getX(), s.getY() - o.getY());
      // fase 56: con el árbitro de la F (gdjs.fdizUsar) solo cuenta quien tiene elegido este objetivo (UsaObjetivo + Elegida)
      const elegido = (s) => !gdjs.fdizUsar || (num(s, "UsaObjetivo") === 1 && V.get("Elegida").getAsNumber() === 1);
      const toman = sups.filter((s) => humano(s) && num(s, "Usando") === 1 && elegido(s) && dist(s) < C.llaveUsar);
      if (prog.getAsNumber() > st.prev && !toman.length) {         // el cuadro lo sumó alguien que no es humano: se deshace
        prog.setNumber(st.prev);
        usada.setNumber(0);
      } else if (toman.length) {
        const p = Math.min(100, Math.round(100 * prog.getAsNumber() / tiempo));
        ayuda(scn, quien(toman[0]) + " toma las llaves... " + p + "%");
        if (prog.getAsNumber() >= tiempo && !st.dicho) {
          st.dicho = true;
          banner(scn, "¡" + quien(toman[0]) + " tomó las llaves!", 3);
        }
      }
      st.prev = prog.getAsNumber();
      // aviso de acercamiento (solo si nadie las está tomando)
      if (!toman.length) {
        const cerca = sups.filter((s) => humano(s) && dist(s) < C.llaveCerca).sort((a, b) => dist(a) - dist(b))[0];
        if (cerca && scn.getVariables().get("Estado").getAsString() === "juego") {
          const tecla = num(cerca, "Control") === 0 || num(cerca, "Control") === -3 ? "F" : "A";
          ayuda(scn, quien(cerca) + ": mantén " + tecla + " junto a las llaves para tomarlas (solo los jugadores pueden)");
        }
      }
    }
  };
})(gdjs);
