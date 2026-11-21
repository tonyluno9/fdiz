/* FDI-Z · Fase 52 · Mientras el cuadro del primer lanzable está abierto (y 0.4 s después de cerrarlo) los jugadores no se mueven ni pegan
 * (así el clic que cierra el cuadro no golpea). Va justo después del grupo "Entrada (teclado y controles)". */
(function () {
  "use strict";
  const U = runtimeScene._fdizLzUi; if (!U) return;
  if (!(U.open || (U.cierre && Date.now() / 1000 < U.cierre))) return;
  for (const s of runtimeScene.getObjects("Sup") || []) {
    if (s.getVariables().get("Control").getAsNumber() < 0) continue;
    for (const n of ["MovX", "MovY", "QuierePegar", "Usando", "PideHab", "PideEsp", "QuiereLanzar"]) s.getVariables().get(n).setNumber(0);
  }
})();
