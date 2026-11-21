/* FDI-Z · Fase 42 · Correr con estamina.
 * Se incrusta en la escena Juego con scripts/fase42_correr.py (no editar el evento a mano: editar este archivo y volver a correr el script).
 * Define gdjs.fdizCorrer.
 *
 * Antes, Shift hacía caminar a media velocidad (no servía de nada). Ahora:
 *   Shift (izq. o der.) en teclado, LB o L3 (clic del stick izq.) en mando  ->  correr (x CFG.factor).
 *   Correr gasta estamina; al soltar se recupera después de una pausa corta. Si se vacía, el jugador queda "agotado" y
 *   no puede volver a correr hasta juntar CFG.umbral (así no se puede spamear tocando el botón).
 *   Solo gasta si de verdad se mueve. Solo los 4 personajes principales de pie (Jugador <= 4, Estado "normal"); los bots corren solos (pideBot).
 *   La pausa congela todo (usa el tiempo de juego escalado).
 *
 * Variables de objeto en Sup (se sincronizan en línea): Estamina (0..CFG.max), Agotado (0/1), Corre (0/1),
 * EstPausa (s desde que dejó de correr).
 * Autoridad: sin red o host (NetRol != 2) calcula (mover). Todos dibujan la barra (dibujar) con los valores sincronizados.
 * El cliente manda Shift / LB en su entrada ("sp" en net_core.js -> NetSp en el host, Control -3). */
(function (gdjs) {
  "use strict";
  if (gdjs.fdizCorrer && gdjs.fdizCorrer.VER === 4) return;
  const C = (gdjs.fdizCorrer = { VER: 4 });

  // ------------------------------------------------------------------ valores (documentados en BITACORA, Fase 42)
  C.CFG = {
    max: 15,        // estamina total
    gasto: 3,       // por segundo corriendo  -> 5 s de carrera con la barra llena
    regen: 2.5,     // por segundo al recuperarse -> 6 s de vacía a llena
    espera: 0.8,    // segundos sin correr antes de empezar a recuperarse
    umbral: 5,      // si se agotó, no vuelve a correr hasta tener esto
    factor: 1.5,    // velocidad corriendo = velocidad normal x factor (Tony: 204 -> 306 px/s)
    anim: 1.35,     // las piernas se mueven más rápido al correr
    // bots (aliados de los 4 principales): corren solo cuando les conviene
    botLejos: 150,  // px MÁS ALLÁ de su distancia de parada para empezar a correr y alcanzar al grupo
    botCerca: 25,   // px más allá de su distancia de parada para dejar de correr (al llegar)
    botInicio: 7,   // estamina mínima para empezar a correr por alcanzar (huir puede con cualquiera > 0)
    botZombi: 320,  // con un zombi vivo más cerca que esto pelean: no corren hacia él (solo corren si huyen)
  };
  const LSHIFT = 1016, RSHIFT = 2016, SHIFT = 16;   // GDevelop distingue izquierda/derecha (1000 + código / 2000 + código)
  const PAD_LB = 4, PAD_L3 = 10;

  const V = (o, n) => o.getVariables().get(n);
  function pad(i) { try { const a = navigator.getGamepads ? navigator.getGamepads() : []; return a[i] || null; } catch (e) { return null; } }
  const boton = (g, n) => !!(g && g.buttons[n] && g.buttons[n].pressed);

  // ¿Este superviviente está pidiendo correr?
  function pide(scn, s) {
    const ctl = V(s, "Control").getAsNumber();
    if (ctl === 0) { const I = scn.getGame().getInputManager(); return I.isKeyPressed(LSHIFT) || I.isKeyPressed(RSHIFT) || I.isKeyPressed(SHIFT); }
    if (ctl >= 1 && ctl <= 4) { const g = pad(ctl - 1); return boton(g, PAD_LB) || boton(g, PAD_L3); }
    if (ctl === -3) return V(s, "NetSp").getAsNumber() === 1;   // jugador remoto (en el host)
    if (ctl === -1) return pideBot(s);
    return false;                                                // los profes aliados (Jugador > 4) no corren
  }

  // Bots: corren si huyen (Huye = 1) o si van lejos de su meta y no hay un zombi cerca (pelean); histéresis para no parpadear.
  const ZN = ["ZNormal", "ZCorredor", "ZGriton", "ZGordo", "ZConserje", "ZCurado", "ZJoel", "ZJustino", "ZCanepa"];
  function pideBot(s) {
    const K = C.CFG, v = s.getVariables();
    if (v.get("Usando").getAsNumber() === 1 || v.get("Atacando").getAsNumber() === 1 ||
        (v.has("Curando") && v.get("Curando").getAsNumber() === 1) || (v.has("Revivir") && v.get("Revivir").getAsNumber() > 0)) { s.__corrBot = false; return false; }
    if (v.get("Huye").getAsNumber() === 1) { s.__corrBot = true; return true; }
    // Cada bot se detiene a una distancia distinta de su meta (evento "Bots": 90 + 45 x Jugador => 180 / 225 / 270 px). Con un
    // umbral fijo, el bot 4 (el que se queda más lejos) nunca llegaba a dejar de correr ni a volver a empezar. Se mide el exceso.
    const j = v.get("Jugador").getAsNumber();
    const pare = j <= 4 ? 90 + 45 * j : 150;
    const d = Math.hypot(v.get("BotX").getAsNumber() - s.getX(), v.get("BotY").getAsNumber() - s.getY()) - pare;
    const e = v.get("Estamina").getAsNumber();
    let on = !!s.__corrBot;
    if (on && (d < K.botCerca || e <= 0.5)) on = false;
    else if (!on && d > K.botLejos && e >= K.botInicio) on = true;
    if (on) {   // peleando (zombi vivo cerca): no corre hacia él
      const scn = s.getRuntimeScene();
      for (const n of ZN) for (const z of (scn.getObjects(n) || [])) {
        if (z.getVariables().get("Estado").getAsString() === "muerto") continue;
        if (Math.hypot(z.getX() - s.getX(), z.getY() - s.getY()) < K.botZombi) { on = false; break; }
      }
    }
    s.__corrBot = on;
    return on;
  }

  // Host / sin red: después del evento que pone MaxSpeed = Velocidad x Rapidez.
  C.mover = function (scn) {
    const K = C.CFG;
    const dt = scn.getTimeManager().getElapsedTime() / 1000;   // tiempo de juego (0 en pausa)
    for (const s of scn.getObjects("Sup")) {
      const E = V(s, "Estamina"), A = V(s, "Agotado"), Co = V(s, "Corre"), P = V(s, "EstPausa");
      const td = s.getBehavior("TopDownMovement");
      let e = Math.max(0, Math.min(K.max, E.getAsNumber()));
      let ag = A.getAsNumber() === 1;
      const antes = Co.getAsNumber() === 1;
      const puede = V(s, "Jugador").getAsNumber() <= 4 && V(s, "Estado").getAsString() === "normal";
      const corre = !!td && puede && !ag && e > 0 && td.isMoving() && pide(scn, s);
      if (corre) {
        e = Math.max(0, e - K.gasto * dt);
        P.setNumber(0);
        if (e <= 0) ag = true;
        td.setMaxSpeed(td.getMaxSpeed() * K.factor);
      } else {
        const p = P.getAsNumber() + dt;
        P.setNumber(p);
        if (p >= K.espera) e = Math.min(K.max, e + K.regen * dt);
        if (ag && e >= K.umbral) ag = false;
      }
      if (corre !== antes) s.setAnimationSpeedScale(corre ? K.anim : 1);
      E.setNumber(e); A.setNumber(ag ? 1 : 0); Co.setNumber(corre ? 1 : 0);
    }
  };

  // Todos (también los clientes): barra pegada al panel de cada jugador (HudPanel con su variable Jugador).
  // Paneles de arriba: la barra va justo debajo; paneles de abajo: justo encima. Solo si el panel está visible.
  C.BARRA = { alto: 14, sep: 8, margen: 4 };
  C.dibujar = function (scn) {
    const K = C.CFG, B = C.BARRA;
    const st = scn._fdizCorrer || (scn._fdizCorrer = {});
    if (!st.dib) {
      st.dib = scn.createObject("EstDib");
      if (st.dib) { st.dib.setLayer("HUD"); st.dib.setPosition(0, 0); st.dib.setZOrder(399); }
    }
    const D = st.dib; if (!D) return;
    D.clear(); D.setOutlineSize(0);
    const t = scn.getTimeManager().getTimeFromStart() / 1000;
    const porJugador = {};
    for (const s of scn.getObjects("Sup")) {
      const j = V(s, "Jugador").getAsNumber();
      if (j >= 1 && j <= 4) porJugador[j] = s;
    }
    for (const pnl of scn.getObjects("HudPanel")) {
      if (pnl.isHidden()) continue;
      const s = porJugador[V(pnl, "Jugador").getAsNumber()];
      if (!s) continue;
      const e = Math.max(0, Math.min(K.max, V(s, "Estamina").getAsNumber()));
      const ag = V(s, "Agotado").getAsNumber() === 1;
      const x0 = Math.round(pnl.getX() + B.margen), x1 = Math.round(pnl.getX() + pnl.getWidth() - B.margen);
      const arriba = pnl.getY() < 540;
      const y0 = Math.round(arriba ? pnl.getY() + pnl.getHeight() + B.sep : pnl.getY() - B.sep - B.alto);
      const y1 = y0 + B.alto, w = x1 - x0;
      D.setFillOpacity(235); D.setFillColor("12;14;24"); D.drawRectangle(x0 - 3, y0 - 3, x1 + 3, y1 + 3);   // marco
      D.setFillOpacity(255); D.setFillColor("38;42;66"); D.drawRectangle(x0, y0, x1, y1);                   // vacío
      const col = ag ? (Math.floor(t * 5) % 2 ? "225;60;60" : "150;35;35") : (e < K.umbral ? "235;150;40" : "90;205;255");
      if (e > 0) {
        D.setFillColor(col); D.drawRectangle(x0, y0, x0 + w * e / K.max, y1);
        D.setFillColor("255;255;255"); D.setFillOpacity(70); D.drawRectangle(x0, y0, x0 + w * e / K.max, y0 + 3);  // brillo
      }
      D.setFillColor("12;14;24"); D.setFillOpacity(200);       // divisiones cada 5 de estamina
      for (let k = 5; k < K.max; k += 5) { const xk = Math.round(x0 + w * k / K.max); D.drawRectangle(xk - 1, y0, xk + 1, y1); }
      if (ag) {   // agotado: marca dónde vuelve a poder correr
        const xu = Math.round(x0 + w * K.umbral / K.max);
        D.setFillColor("255;255;255"); D.setFillOpacity(220); D.drawRectangle(xu - 1, y0 - 3, xu + 1, y1 + 3);
      }
    }
  };
})(gdjs);
