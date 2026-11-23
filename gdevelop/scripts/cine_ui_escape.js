/* FDI-Z · Fase 85 · Interfaz oculta en las cinemáticas y modo Escape sin armas de fuego.
 * Se incrusta en la escena Juego con scripts/fase85_pausa_ui_tutorial_escape.py (evento FDIZ-FASE85-CINEUI, el último de
 * la escena: así decide después de que cada módulo dibujó lo suyo).
 *
 * Cinemáticas (video o tarjeta de cine.js con CineModo, o de la Historia con HistCine): se esconde todo lo de la capa HUD
 * (paneles, minimapa, flechas hacia el objetivo, letrero de objetivo, avisos, ayudas, globos) y la mira, salvo lo que usa
 * la propia cinemática (video, velo, subtítulos, botón OMITIR). Lo que se escondió aquí vuelve a verse al terminar.
 * Balas y perdigones rompen una puerta normal aunque salgan pegados a ella (revisión por tramo, ver balasPuertas). Corre
 * también en FDIZ-FASE85-BALAS, justo después de «Combate: pegar»: a quemarropa el perdigón nace sobre el marco (muro) y el
 * evento de proyectiles lo borra en ese mismo cuadro.
 * Escape: no hay pistolas, escopeta ni AK-47. Las armas de fuego del piso se quitan al aparecer (las del mapa, la pistola
 * pequeña inicial y las de las escenas del casillero y el cajón) y nadie las conserva en la mano. */
(function (gdjs) {
  "use strict";
  if (gdjs.fdizCineUi && gdjs.fdizCineUi.VER === 1) return;
  const C = (gdjs.fdizCineUi = { VER: 1 });
  C.DEJAR = { CineDib: 1, TxtCine: 1, HistDib: 1, HistRetrato: 1, ProfPanel: 1, TxtHist: 1, TxtProfe: 1, BtnOmitir: 1, TxtOmitir: 1,
    PausaBtn: 1, PausaPanel: 1, PausaVelo: 1, TxtPausaB0: 1, TxtPausaB1: 1, TxtPausaB2: 1, TxtPausaB3: 1, TxtPausaTit: 1, TxtPausaCtl1: 1, TxtPausaCtl2: 1 };
  C.FUEGO = { pistola: 1, pistolita: 1, escopeta: 1, ak47: 1 };
  const str = (o, n) => { try { return o.getVariables().get(n).getAsString(); } catch (e) { return ""; } };

  C.enCine = function (scn) {
    const cm = str(scn, "CineModo"), hc = str(scn, "HistCine");
    return (cm !== "" && cm !== "0") || (hc !== "" && hc !== "0");
  };

  function interfaz(scn) {
    const st = scn._fdizCineUi || (scn._fdizCineUi = { ocultos: new Set() });
    if (C.enCine(scn)) {
      let lista = [];
      try { lista = scn.getAdhocListOfAllInstances(); } catch (e) { return; }
      for (const o of lista) {
        const n = o.getName();
        const ui = o.getLayer() === "HUD" || n === "Mira" || n === "TxtMordido";
        if (!ui || C.DEJAR[n] || /^Vid/.test(n) || o.getType && o.getType() === "Video::VideoObject") continue;
        if (!(o.isHidden && o.isHidden())) { o.hide(true); st.ocultos.add(o); }
      }
    } else if (st.ocultos.size) {
      for (const o of st.ocultos) { try { if (o._livingOnScene !== false) o.hide(false); } catch (e) { /* ya no está */ } }
      st.ocultos.clear();
    }
  }

  function sinFuego(scn) {
    if (scn.getGame().getVariables().get("Modo").getAsString() !== "escape") return;
    if (scn.getGame().getVariables().get("NetRol").getAsNumber() === 2) return;   // el host decide
    for (const a of (scn.getObjects("ArmaPiso") || []).slice()) if (C.FUEGO[str(a, "Tipo")]) a.deleteFromScene(scn);
    for (const s of scn.getObjects("Sup") || []) {
      if (!C.FUEGO[str(s, "Arma")]) continue;
      s.getVariables().get("Arma").setString("puños"); s.getVariables().get("Usos").setNumber(0);
    }
  }

  // balas y perdigones contra puertas normales, por tramo: entre el cuadro anterior y este una bala avanza ~30 px y de
  // cerca podía brincarse la puerta (la escopeta a quemarropa no la rompía). Se revisa el segmento recorrido.
  function balasPuertas(scn) {
    if (scn.getGame().getVariables().get("NetRol").getAsNumber() === 2) return;
    let puertas = null;
    for (const p of scn.getObjects("Proyectil") || []) {
      const tipo = str(p, "Tipo");
      if (tipo !== "bala" && tipo !== "perdigon") continue;
      let x = p.getCenterXInScene(), y = p.getCenterYInScene();
      let ax = p.__f85x, ay = p.__f85y;
      const nueva = ax === undefined;
      if (ax === undefined) {                                    // bala nueva: el tramo empieza en el arma de quien disparó
        ax = x; ay = y;                                          // (sale 34 px adelante: a quemarropa ya nace del otro lado)
        const j = p.getVariables().get("Jugador").getAsNumber();
        const s = (scn.getObjects("Sup") || []).find((q) => q.getVariables().get("Jugador").getAsNumber() === j);
        if (s) { ax = s.getX(); ay = s.getY() - 46; }
      }
      p.__f85x = x; p.__f85y = y;
      if (nueva) {                                               // y lo que avanzará en su primer cuadro (si nace sobre el
        const r = p.getAngle() * Math.PI / 180;                  // marco de la puerta, el evento de proyectiles la borra antes)
        x += Math.cos(r) * 32; y += Math.sin(r) * 32;
      }
      if (!puertas) puertas = (scn.getObjects("Puerta") || []).filter((q) => q.isVisible() && str(q, "Tipo") === "normal" && q.getVariables().get("Vida").getAsNumber() > 0);
      for (const q of puertas) {
        const x0 = q.getX() - 6, y0 = q.getY() - 6, x1 = q.getX() + q.getWidth() + 6, y1 = q.getY() + q.getHeight() + 6;
        let toca = false;
        const n = Math.max(6, Math.ceil(Math.hypot(x - ax, y - ay) / 8));
        for (let k = 0; k <= n && !toca; k++) { const px = ax + (x - ax) * k / n, py = ay + (y - ay) * k / n; toca = px >= x0 && px <= x1 && py >= y0 && py <= y1; }
        if (!toca) continue;
        q.getVariables().get("Vida").setNumber(0);
        try { q.setColor("255;160;160"); } catch (e) { /* sin color */ }
        p.getVariables().get("Pego").setNumber(1);
        try { if (scn.getGame().getVariables().get("SonidoActivo").getAsNumber() === 1) gdjs.evtTools.sound.playSound(scn, "efectos/mundo/puerta_golpe.wav", false, 70, 1); } catch (e) { /* sin sonido */ }
        break;
      }
    }
  }

  C.balas = function (scn) { try { balasPuertas(scn); } catch (e) { /* sin puertas */ } };   // también justo después de disparar
  C.tick = function (scn) {
    try { sinFuego(scn); } catch (e) { /* sin armas */ }
    try { balasPuertas(scn); } catch (e) { /* sin puertas */ }
    interfaz(scn);
  };
})(gdjs);
