/* FDI-Z · Fase 62 · Uso de las armas de fuego: mira, munición en el HUD y animación con pistola. Todos los modos.
 * Se incrusta en la escena Juego con scripts/fase62_armas_uso.py (no editar el evento a mano):
 *   FDIZ-FASE62-MOD y FDIZ-FASE62-TICK arriba de todo, sin compuerta de host (cada máquina dibuja su mira y su HUD);
 *   FDIZ-FASE62-ANIM al final de "Combate: pegar" (host / sin red; la animación llega a los clientes por la red).
 *
 * Munición: es la de siempre (Sup.Usos, se gasta 1 por disparo y al llegar a 0 vuelven los puños). No hay recarga ni
 * balas de reserva: el HUD muestra las balas que le quedan al arma y, debajo del ícono, el cargador completo con las
 * gastadas en gris. CARGADOR = las balas con que se recoge cada arma (fase 59).
 * Mira: una cruz hueca de 11 px a 78 px del arma, hacia donde apunta (AimX, AimY); más transparente si queda sobre un
 * personaje o un zombi. Solo para jugadores (no bots) con arma de fuego, de pie, en juego y sin pausa.
 * Animación: con pistola (pequeña o sheriff) el golpe de lado o hacia abajo usa <personaje>_pistola_lado / _abajo.
 * Hacia arriba no hay animación de pistola: se queda la de pegar hacia arriba de siempre. Si un personaje no tiene la
 * animación de pistola, setAnimationName no cambia nada y sigue la de pegar (nunca queda invisible ni detenido). */
(function (gdjs) {
  "use strict";
  if (gdjs.fdizArmas && gdjs.fdizArmas.VER === 1) return;
  const A = (gdjs.fdizArmas = { VER: 1 });

  A.CARGADOR = { pistolita: 9, pistola: 4, escopeta: 6 };
  A.PISTOLAS = { pistolita: true, pistola: true };
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
      if (!A.PISTOLAS[str(s, "Arma")] || num(s, "Atacando") !== 1) continue;
      const pj = str(s, "Personaje"), an = s.getAnimationName();
      if (an === pj + "_pegar_lado") s.setAnimationName(pj + "_pistola_lado");
      else if (an === pj + "_pegar_abajo") s.setAnimationName(pj + "_pistola_abajo");
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
  function miras(scn) {
    const juego = SV(scn, "Estado").getAsString() === "juego" && SV(scn, "Pausa").getAsNumber() !== 1;
    const sups = objs(scn, "Sup");
    const otros = sups.concat(...A.ZN.map((n) => objs(scn, n)));
    for (const s of sups) {
      const j = num(s, "Jugador");
      const ver = juego && j >= 1 && j <= 4 && num(s, "Control") !== -1 && str(s, "Estado") === "normal" && A.deFuego(s) && num(s, "Usos") > 0;
      const p = ver ? A.posMira(s) : null;
      let m = s.__fdizMira;
      if (!p) { if (m) m.hide(true); continue; }
      if (!m) {
        m = s.__fdizMira = scn.createObject("Mira");
        if (!m) continue;
        m.setLayer("Juego");
      }
      m.hide(false);
      m.setPosition(Math.round(p[0] - m.getWidth() / 2), Math.round(p[1] - m.getHeight() / 2));
      m.setZOrder(100000);
      const tapa = otros.some((o) => o !== s && !(o.isHidden && o.isHidden()) && dentro(caja(o), p[0], p[1], 2));
      m.setOpacity(tapa ? 110 : 210);
    }
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
      const w = 4, g = 2, total = cap * (w + g) - g, x0 = Math.round(xy[0] + 27 - total / 2), y0 = xy[1] + 57;
      d.setOutlineSize(1); d.setOutlineColor("20;20;30"); d.setOutlineOpacity(255); d.setFillOpacity(255);
      for (let k = 0; k < cap; k++) {
        d.setFillColor(k < usos ? "232;190;90" : "70;70;84");
        d.drawRectangle(x0 + k * (w + g), y0, x0 + k * (w + g) + w, y0 + 8);
      }
    }
  }

  // ------------------------------------------------------------------ cada cuadro (todas las máquinas)
  A.tick = function (scn) {
    miras(scn);
    hud(scn);
  };
})(gdjs);
