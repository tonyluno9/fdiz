/* FDI-Z · Fase 84 · Tony se hace 20 % más grande mientras dura su especial (Modo gym: Personaje = "tonyfuerte").
 * Se incrusta en la escena Juego con scripts/fase84_teclas_tony_puertas_historia.py (evento FDIZ-FASE84-TONY, cada
 * cuadro, en todas las máquinas: la escala no viaja por la red, cada una la calcula con el Personaje que ya se sincroniza).
 * Crece y vuelve a su tamaño en ~0.25 s; el origen está en los pies, así que crece hacia arriba. */
(function (gdjs) {
  "use strict";
  if (gdjs.fdizTonyGym && gdjs.fdizTonyGym.VER === 1) return;
  const T = (gdjs.fdizTonyGym = { VER: 1, FACTOR: 1.2, VEL: 4 });
  T.tick = function (scn) {
    const dt = Math.min(0.1, scn.getElapsedTime() / 1000);
    for (const s of scn.getObjects("Sup") || []) {
      let p = ""; try { p = s.getVariables().get("Personaje").getAsString(); } catch (e) { continue; }
      const fuerte = p === "tonyfuerte";
      if (s.__f84base === undefined || (!fuerte && !s.__f84activo)) s.__f84base = s.getScaleX();   // tamaño normal
      const base = s.__f84base, meta = fuerte ? base * T.FACTOR : base;
      const cur = s.getScaleX();
      if (Math.abs(cur - meta) < 0.002) { if (cur !== meta) s.setScale(meta); s.__f84activo = fuerte; continue; }
      s.__f84activo = true;
      const paso = base * (T.FACTOR - 1) * T.VEL * dt;
      s.setScale(cur < meta ? Math.min(meta, cur + paso) : Math.max(meta, cur - paso));
    }
  };
})(gdjs);
