/* FDI-Z · Fase 84 · Resultados del modo Historia tras una derrota: REINTENTAR empieza de 0 y CONTINUAR va al punto de control.
 * Se incrusta en la escena Resultados con scripts/fase84_teclas_tony_puertas_historia.py (evento FDIZ-FASE84-RES, al final).
 * Antes REINTENTAR seguía desde el último paso guardado. Ahora:
 *   - REINTENTAR (botón de siempre, clic / R / Enter / Espacio / A): la historia empieza desde el paso 1 (Historia.Paso = 0:
 *     historia.js lo toma como partida nueva y borra cinemáticas vistas y armas).
 *   - CONTINUAR (botón nuevo arriba de REINTENTAR, clic o tecla C / Y del mando): sigue desde el paso guardado.
 *     Solo si hay un punto de control (paso 2 o más) y la dificultad NO es pesadilla (la difícil no tiene puntos de control).
 * Sin red (NetRol 0); en línea los botones siguen como antes. */
(function () {
  "use strict";
  const scn = runtimeScene, G = scn.getGame().getVariables();
  if (G.get("Modo").getAsString() !== "historia" || G.get("Resultado").getAsString() === "victoria" || G.get("NetRol").getAsNumber() !== 0) return;
  const H = G.get("Historia"), paso = H.getChild("Paso").getAsNumber();
  const dificil = G.get("Dificultad").getAsString() === "pesadilla";
  const hay = !dificil && paso >= 2 && paso <= 11;
  const st = scn._fdiz84 || (scn._fdiz84 = { t0: Date.now() / 1000, btn: null, txt: null, ido: false });
  const I = scn.getGame().getInputManager();
  const X = 150, Y = 490, W = 380, AL = 132;                     // mismo tamaño que REINTENTAR (150, 640) y MENÚ (150, 790)

  // ---- botón CONTINUAR (copia del de REINTENTAR)
  if (!st.btn && hay) {
    const b = scn.createObject("BtnRei"), t = scn.createObject("TxtBtnRei");
    if (b) {
      b.setLayer(""); b.setPosition(X, Y); b.setZOrder(300);
      const ref = (scn.getObjects("BtnRei") || []).find((o) => o !== b);   // mismo tamaño que REINTENTAR
      try { b.setWidth(ref ? ref.getWidth() : W); b.setHeight(ref ? ref.getHeight() : AL); } catch (e) { /* sin tamaño */ }
    }
    if (t) { t.setLayer(""); t.setZOrder(301); }
    st.btn = b; st.txt = t;
  }
  const sobre = I.getCursorX() >= X && I.getCursorX() < X + W && I.getCursorY() >= Y && I.getCursorY() < Y + AL;
  if (st.btn) { st.btn.setPosition(X, Y); st.btn.setOpacity(sobre ? 255 : 200); }
  if (st.txt) {
    const s = "CONTINUAR (C)";
    if (st.txt.getString() !== s) st.txt.setString(s);
    st.txt.setPosition(X + W / 2 - st.txt.getWidth() / 2, Y + AL / 2 - st.txt.getHeight() / 2);
  }
  // texto de abajo del título (el de la fase 68 decía «Seguirán desde el paso N»)
  const T = scn._fdizHistRes && scn._fdizHistRes.txt;
  if (T) {
    const s = dificil ? "Modo pesadilla: sin puntos de control. Reintentar empieza desde el inicio."
      : hay ? "Punto de control: paso " + paso + " de 12" : "Reintentar empieza desde el inicio";
    if (T.getString() !== s) T.setString(s);
    T.hide(false); T.setCharacterSize(24); T.setPosition(340 - T.getWidth() / 2, 450);
  }

  // ---- acciones (después de 0.6 s, como los botones de siempre)
  if (st.ido || Date.now() / 1000 - st.t0 < 0.6) return;
  let continuar = false;
  if (hay) {
    if (I.isMouseButtonReleased(0) && sobre) continuar = true;
    if (I.wasKeyReleased(67)) continuar = true;                   // C
    try { const gp = navigator.getGamepads ? navigator.getGamepads() : []; for (let g = 0; g < 4; g++) if (gp && gp[g] && gp[g].buttons[3] && gp[g].buttons[3].pressed) continuar = true; } catch (e) { /* sin mandos */ }
  }
  if (continuar) {
    st.ido = true;
    gdjs.evtTools.runtimeScene.replaceScene(scn, "Juego", true);
    return;
  }
  // REINTENTAR: los eventos de siempre cambian a Juego este mismo cuadro; aquí solo se borra el punto de control
  const enRei = I.getCursorX() >= 150 && I.getCursorX() < 530 && I.getCursorY() >= 640 && I.getCursorY() < 772;
  let sel = 0; try { sel = scn.getVariables().get("Sel").getAsNumber(); } catch (e) { /* sin selección */ }
  let a = false; try { const gp = navigator.getGamepads ? navigator.getGamepads() : []; for (let g = 0; g < 4; g++) if (gp && gp[g] && ((gp[g].buttons[0] && gp[g].buttons[0].pressed) || (gp[g].buttons[9] && gp[g].buttons[9].pressed))) a = true; } catch (e) { /* sin mandos */ }
  const teclas = sel === 0 && (I.wasKeyReleased(82) || I.wasKeyReleased(13) || I.wasKeyReleased(32) || a);   // como el evento de siempre: R, Enter, Espacio, A o Start con REINTENTAR elegido
  if ((I.isMouseButtonReleased(0) && enRei) || teclas) {
    H.getChild("Paso").setNumber(0);
    H.getChild("Armas").setString("");
    H.getChild("CinematicasVistas").setString("");
    st.ido = true;
  }
})();
