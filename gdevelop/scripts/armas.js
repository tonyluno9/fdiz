/* FDI-Z · Fase 62 · Uso de las armas de fuego: mira, munición en el HUD y animación con pistola. Todos los modos.
 * Se incrusta en la escena Juego con scripts/fase62_armas_uso.py (no editar el evento a mano):
 *   FDIZ-FASE62-MOD y FDIZ-FASE62-TICK arriba de todo, sin compuerta de host (cada máquina dibuja su mira y su HUD);
 *   FDIZ-FASE62-ANIM al final de "Combate: pegar" (host / sin red; la animación llega a los clientes por la red).
 *
 * Munición: es la de siempre (Sup.Usos, se gasta 1 por disparo y al llegar a 0 vuelven los puños). No hay recarga ni
 * balas de reserva: el HUD muestra las balas que le quedan al arma y, debajo del ícono, el cargador completo con las
 * gastadas en gris. CARGADOR = las balas con que se recoge cada arma (fase 59).
 * Mira (fase 83): con ratón va donde está el cursor, con cualquier arma, y se oculta la flecha del sistema. Con mando: una cruz hueca de 11 px a 78 px del arma, hacia donde apunta (AimX, AimY); más transparente si queda sobre un
 * personaje o un zombi. Solo para jugadores (no bots) con arma de fuego, de pie, en juego y sin pausa.
 * Animación: con pistola (pequeña o sheriff) el golpe de lado o hacia abajo usa <personaje>_pistola_lado / _abajo; con escopeta,
 * de lado, <personaje>_escopeta_lado (fase 69: Tony usa sus animaciones de disparo de animaciones_gif/personajes/tony/).
 * Hacia arriba no hay animación de pistola: se queda la de pegar hacia arriba de siempre. Si un personaje no tiene la
 * animación de pistola, setAnimationName no cambia nada y sigue la de pegar (nunca queda invisible ni detenido).
 * Pistola inicial (fase 67): nadie empieza con ella. Al empezar la partida (host / sin red) se pone UNA pistola pequeña
 * en el piso (ArmaPiso Tipo "pistolita", Solo = 1) del salón donde está el jugador 1: B-01 (intro de Escape e Historia)
 * o E-04 (aparición normal: Jefe, en línea, Escape sin intro). Se recoge con el sistema de siempre ("Armas del salón":
 * pasar encima con los puños; solo el jugador 1 por Solo = 1), que la equipa con 9 balas y borra la del piso.
 * PistolaPuesta (variable de la escena) evita ponerla dos veces; se reinicia sola con la escena (partida nueva). */
(function (gdjs) {
  "use strict";
  if (gdjs.fdizArmas && gdjs.fdizArmas.VER === 2) return;
  const A = (gdjs.fdizArmas = { VER: 2 });

  A.CARGADOR = { pistolita: 24, pistola: 9, escopeta: 16, ak47: 30 };   // fase 78: más balas (AK-47 de Alan, fase 72: 30)
  A.PISTOLAS = { pistolita: true, pistola: true, ak47: true };       // el AK-47 usa la animación de disparo de lado (<pj>_pistola_lado)
  A.RADIO = 78;                 // px del arma a la mira
  A.ALTO = 46;                  // el arma (y la salida de las balas) está 46 px arriba de los pies (fase 59)
  A.ICONO = { 1: [351, 94], 2: [1813, 94], 3: [351, 978], 4: [1813, 978] };   // ícono del arma (54 x 54) de cada panel
  A.BAJAS = 2;                  // con estas balas o menos, el número se pone rojo

  const VS = (o, n) => o.getVariables().get(n);
  const num = (o, n) => VS(o, n).getAsNumber();
  const str = (o, n) => VS(o, n).getAsString();
  const objs = (scn, n) => { try { return scn.getObjects(n) || []; } catch (e) { return []; } };
  const rol = (scn) => { try { return scn.getGame().getVariables().get("NetRol").getAsNumber(); } catch (e) { return 0; } };
  const SV = (scn, n) => scn.getVariables().get(n);
  A.deFuego = (s) => A.CARGADOR[str(s, "Arma")] !== undefined;

  // ------------------------------------------------------------------ animación (host / sin red)
  A.anim = function (scn) {
    if (rol(scn) === 2) return;
    for (const s of objs(scn, "Sup")) {
      const arma = str(s, "Arma");
      if (num(s, "Atacando") !== 1 || !(A.PISTOLAS[arma] || arma === "escopeta")) continue;
      const pj = str(s, "Personaje"), an = s.getAnimationName();
      // fase 69: con escopeta, de lado, <personaje>_escopeta_lado (Tony la tiene; los demás siguen con la de pegar)
      const tipo = arma === "escopeta" ? "escopeta" : "pistola";
      if (an === pj + "_pegar_lado") s.setAnimationName(pj + "_" + tipo + "_lado");
      // fase 73: arriba y abajo con placeholders propios (<pj>_<arma>_arriba / _abajo) para pistola y escopeta
      else if (an === pj + "_pegar_abajo") s.setAnimationName(pj + "_" + tipo + "_abajo");
      else if (an === pj + "_pegar_arriba") s.setAnimationName(pj + "_" + tipo + "_arriba");
    }
  };

  // ------------------------------------------------------------------ mira
  const caja = (o) => {
    const x = o.getDrawableX ? o.getDrawableX() : o.getX(), y = o.getDrawableY ? o.getDrawableY() : o.getY();
    return [x, y, x + o.getWidth(), y + o.getHeight()];
  };
  const dentro = (b, x, y, m) => x >= b[0] - m && x <= b[2] + m && y >= b[1] - m && y <= b[3] + m;
  A.ZN = ["ZNormal", "ZCorredor", "ZGriton", "ZGordo", "ZConserje", "ZJoel", "ZJustino", "ZCanepa", "Profe"];
  A.posMira = function (s) {
    let ax = num(s, "AimX"), ay = num(s, "AimY");
    const n = Math.hypot(ax, ay);
    if (n < 0.01) return null;
    ax /= n; ay /= n;
    return [s.getX() + ax * A.RADIO, s.getY() - A.ALTO + ay * A.RADIO];
  };
  // posición del cursor en el mundo (misma capa que usa la puntería: CursorX() de la capa base)
  A.posCursor = function (scn) {
    try {
      const I = scn.getGame().getInputManager();
      const p = scn.getLayer("").convertCoords(I.getCursorX(), I.getCursorY());
      return [p[0], p[1]];
    } catch (e) { return null; }
  };
  // con la mira en el cursor se oculta la flecha del sistema (vuelve en menús, pausa y cuadros)
  // (net_core.js la vuelve a poner en cada cuadro: el evento del tutorial, el último de la escena, la aplica otra vez con scn.__fdizSinFlecha)
  function flecha(scn, ocultar) {
    scn.__fdizSinFlecha = !!ocultar;
    try {
      const c = scn.getGame().getRenderer().getCanvas();
      const v = ocultar ? "none" : "";
      if (c && c.style.cursor !== v) c.style.cursor = v;
    } catch (e) { /* sin lienzo */ }
  }
  function miras(scn) {
    const juego = SV(scn, "Estado").getAsString() === "juego" && SV(scn, "Pausa").getAsNumber() !== 1 &&
      !(scn._fdizLzUi && scn._fdizLzUi.open) && !(scn._fdizTuto && scn._fdizTuto.open);
    let hayRaton = false;
    const sups = objs(scn, "Sup");
    const otros = sups.concat(...A.ZN.map((n) => objs(scn, n)));
    for (const s of sups) {
      const j = num(s, "Jugador");
      // fase 71: también con un lanzable en la mano (modo de lanzar). La mira solo indica hacia dónde apunta: el impacto lo decide la bala
      const lanza = (() => { try { const l = str(s, "Lanz"); return l !== "" && l !== "0"; } catch (e) { return false; } })();
      // fase 83: el jugador con ratón (Control 0) siempre ve la mira donde está el cursor (ahí va la bala o el golpe);
      // los de mando la siguen viendo a 78 px del arma, solo con arma de fuego o lanzable
      const raton = juego && num(s, "Control") === 0 && str(s, "Estado") === "normal";
      const ver = raton || (juego && j >= 1 && j <= 4 && num(s, "Control") !== -1 && str(s, "Estado") === "normal" && ((A.deFuego(s) && num(s, "Usos") > 0) || lanza));
      const p = !ver ? null : raton ? A.posCursor(scn) : A.posMira(s);
      if (raton) hayRaton = true;
      let m = s.__fdizMira;
      if (!p) { if (m) m.hide(true); continue; }
      if (!m) {
        m = s.__fdizMira = scn.createObject("Mira");
        if (!m) continue;
        m.setLayer("Juego");
      }
      m.hide(false);
      try { const e = raton ? 2.2 : 1; if (m.getScaleX && Math.abs(m.getScaleX() - e) > 0.01) m.setScale(e); } catch (e) { /* sin escala */ }
      m.setPosition(Math.round(p[0] - m.getWidth() / 2), Math.round(p[1] - m.getHeight() / 2));
      m.setZOrder(100000);
      const tapa = otros.some((o) => o !== s && !(o.isHidden && o.isHidden()) && dentro(caja(o), p[0], p[1], 2));
      m.setOpacity(raton ? (tapa ? 200 : 255) : (tapa ? 110 : 210));
    }
    flecha(scn, hayRaton);
    for (const m of objs(scn, "Mira")) {                            // miras de jugadores que ya no están
      if (!sups.some((s) => s.__fdizMira === m)) m.deleteFromScene(scn);
    }
  }

  // ------------------------------------------------------------------ munición en el HUD
  function hud(scn) {
    const st = scn.__fdizArmas || (scn.__fdizArmas = {});
    if (!st.dib) { st.dib = scn.createObject("BalasDib"); if (st.dib) { st.dib.setLayer("HUD"); st.dib.setPosition(0, 0); st.dib.setZOrder(60); } }
    const d = st.dib;
    if (d) d.clear();
    const intro = SV(scn, "Estado").getAsString() === "intro";
    for (const t of objs(scn, "TxtBalas")) {
      const j = num(t, "Jugador"), s = objs(scn, "Sup").find((o) => num(o, "Jugador") === j);
      const icono = objs(scn, "HudIcono").find((o) => num(o, "Jugador") === j && num(o, "Slot") === 3);
      const ver = !intro && s && A.deFuego(s) && num(s, "Usos") > 0 && (!icono || (icono.isVisible ? icono.isVisible() : !icono.isHidden()));
      if (!ver) { t.hide(true); continue; }
      const usos = Math.max(0, Math.round(num(s, "Usos"))), cap = Math.max(usos, A.CARGADOR[str(s, "Arma")]);
      const xy = A.ICONO[j] || [icono.getX(), icono.getY()];
      t.hide(false);
      if (t.getString() !== String(usos)) t.setText(String(usos));
      t.setColor(usos <= A.BAJAS ? "255;110;90" : "255;255;255");
      t.setPosition(xy[0] + 58, xy[1] + 10);
      if (!d) continue;
      // cargador: una marca por bala; las gastadas en gris (no hay reservas: solo lo que trae el arma)
      // fase 78: con cargadores grandes (más de 9) las marcas son más delgadas y van en filas de 13, dentro del panel
      const chico = cap <= 9, w = chico ? 4 : 3, g = chico ? 2 : 1, fila = chico ? cap : 13;
      const total = Math.min(cap, fila) * (w + g) - g, x0 = Math.round(xy[0] + 27 - total / 2), y0 = xy[1] + 57;
      d.setOutlineSize(chico ? 1 : 0); d.setOutlineColor("20;20;30"); d.setOutlineOpacity(255); d.setFillOpacity(255);
      for (let k = 0; k < cap; k++) {
        const c = k % fila, f = Math.floor(k / fila);
        d.setFillColor(k < usos ? "232;190;90" : "70;70;84");
        d.drawRectangle(x0 + c * (w + g), y0 + f * 10, x0 + c * (w + g) + w, y0 + f * 10 + 8);
      }
    }
  }

  // ------------------------------------------------------------------ pistola inicial en el piso (host / sin red)
  A.PISTOLA = {
    tipo: "pistolita",
    espera: 40,                 // cuadros después de que todos los Sup tienen Init = 1 (Historia y la intro ya los movieron)
    salones: [                  // muros del salón y dónde va la pistola (pies del arma), en el pasillo entre pupitres
      { zona: "B-01", x0: 5824, y0: 2848, x1: 6144, y1: 3264, x: 6000, y: 3100 },
      { zona: "E-04", x0: 4960, y0: 2368, x1: 5408, y1: 2624, x: 5200, y: 2570 },
    ],
  };
  const espera = new WeakMap();
  A.salonDe = function (x, y) {
    const S = A.PISTOLA.salones;
    const en = S.find((q) => x >= q.x0 && x <= q.x1 && y >= q.y0 && y <= q.y1);
    if (en) return en;
    const d = (q) => Math.hypot(x - (q.x0 + q.x1) / 2, y - (q.y0 + q.y1) / 2);
    return S.slice().sort((a, b) => d(a) - d(b))[0];
  };
  A.ponerPistola = function (scn) {
    if (rol(scn) === 2) return;
    const V = SV(scn, "PistolaPuesta");
    if (V.getAsNumber() !== 0) return;
    const sups = objs(scn, "Sup");
    if (!sups.length || sups.some((s) => num(s, "Init") !== 1)) return;
    const n = (espera.get(scn) || 0) + 1;
    espera.set(scn, n);
    if (n < A.PISTOLA.espera) return;
    const p1 = sups.find((s) => num(s, "Jugador") === 1) || sups[0];
    const q = A.salonDe(p1.getX(), p1.getY());
    const a = scn.createObject("ArmaPiso");
    if (!a) return;
    a.setLayer("Juego"); a.setPosition(q.x, q.y); a.setZOrder(q.y);
    VS(a, "Tipo").setString(A.PISTOLA.tipo); VS(a, "Solo").setNumber(1);
    a.setAnimationName(A.PISTOLA.tipo);
    V.setNumber(1);
  };

  // Fase 69: la pistola pequeña siempre se puede recoger. El sistema de siempre ("Armas del salón") solo recoge con los
  // puños; si el jugador trae un arma cuerpo a cuerpo (escoba, silla...) y pisa la pistola, esa arma se deja en el piso
  // y en este mismo cuadro el evento de siempre le da la pistola (y borra la del piso). Las armas de fuego no se cambian.
  A.cambiarPorPistola = function (scn) {
    if (rol(scn) === 2) return;
    for (const a of objs(scn, "ArmaPiso")) {
      if (str(a, "Tipo") !== A.PISTOLA.tipo) continue;
      const solo = num(a, "Solo");
      for (const s of objs(scn, "Sup")) {
        const arma = str(s, "Arma");
        if (arma === "puños" || A.deFuego(s) || str(s, "Estado") !== "normal" || (solo && num(s, "Jugador") !== solo)) continue;
        if (Math.hypot(s.getX() - a.getX(), s.getY() - a.getY()) > 40) continue;
        const d = scn.createObject("ArmaPiso");
        if (d) { d.setLayer("Juego"); d.setPosition(s.getX() - 56, s.getY() + 6); d.setZOrder(s.getY() + 6); VS(d, "Tipo").setString(arma); d.setAnimationName(arma); }
        VS(s, "Arma").setString("puños"); VS(s, "Usos").setNumber(0);
      }
    }
  };

  // ------------------------------------------------------------------ fase 71: reacción de daño de los zombis
  // Cuando un zombi pierde vida y sigue vivo, hace los 2 primeros cuadros de "golpe_morir" (el golpe) durante 0.22 s.
  // Mientras dura, se ignoran los cambios de animación de la IA (caminar / atacar) en ese zombi. Host / sin red.
  A.DOLOR_MS = 220;
  A.ZOMBIS = ["ZNormal", "ZCorredor", "ZGriton", "ZGordo", "ZConserje", "ZJoel", "ZJustino", "ZCanepa"];
  function dolor(scn) {
    if (rol(scn) === 2) return;
    const t = Date.now();
    for (const n of A.ZOMBIS) for (const z of objs(scn, n)) {
      let v; try { v = num(z, "Vida"); } catch (e) { continue; }
      const prev = z.__fdizVida; z.__fdizVida = v;
      if (prev === undefined || !(v < prev - 0.001) || v <= 0 || str(z, "Estado") === "muerto") continue;
      if (!z.__fdizAnim) {
        z.__fdizAnim = z.setAnimationName.bind(z);
        z.setAnimationName = function (nom) { if (Date.now() < this.__fdizDolor && nom !== "golpe_morir") return; return this.__fdizAnim(nom); };
      }
      if (!(z.__fdizDolor && t < z.__fdizDolor)) z.__fdizPrev = z.getAnimationName();
      z.__fdizDolor = t + A.DOLOR_MS;
      try { z.__fdizAnim("golpe_morir"); z.setAnimationFrame(0); z.playAnimation && z.playAnimation(); } catch (e) { /* sin animación */ }
    }
    for (const n of A.ZOMBIS) for (const z of objs(scn, n)) {        // no pasar del cuadro 1 (el 2 ya es caer)
      if (!z.__fdizDolor || str(z, "Estado") === "muerto" || z.getAnimationName() !== "golpe_morir") continue;
      if (t < z.__fdizDolor) { if (z.getAnimationFrame() > 1) z.setAnimationFrame(1); }
      else { z.__fdizDolor = 0; try { z.__fdizAnim(z.__fdizPrev && z.__fdizPrev !== "golpe_morir" ? z.__fdizPrev : "caminar_abajo"); } catch (e) { /* sin animación */ } }
    }
  }

  // ------------------------------------------------------------------ cada cuadro (todas las máquinas)
  A.tick = function (scn) {
    try { dolor(scn); } catch (e) { /* sin zombis */ }
    try { A.ponerPistola(scn); } catch (e) { /* sin la pistola inicial */ }
    try { A.cambiarPorPistola(scn); } catch (e) { /* sin armas en el piso */ }
    miras(scn);
    hud(scn);
  };
})(gdjs);
