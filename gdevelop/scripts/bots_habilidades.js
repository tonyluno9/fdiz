/* FDI-Z · Bots: uso inteligente de Habilidad (Q) y Especial (E) (fase 22).
 * Corre antes del grupo "Habilidades, especiales y pasivas". Solo marca PideHab / PideEsp; el grupo 27 aplica la recarga.
 * Cada personaje tiene su criterio según lo que hace su poder. */
(function () {
  "use strict";
  const scn = runtimeScene, V = scn.getVariables();
  if (V.get("Pausa").getAsNumber() === 1 || V.get("Estado").getAsString() !== "juego") return;
  const sups = scn.getObjects("Sup") || [];
  if (!sups.length) return;
  const ZN = ["ZNormal", "ZCorredor", "ZGriton", "ZGordo", "ZConserje", "ZCurado"];
  const zs = [];
  for (const n of ZN) { const a = scn.getObjects(n); if (a) for (const z of a) { const st = z.getVariables().get("Estado").getAsString(); if (st === "persigue" || st === "ataca") zs.push(z); } }
  const g = (o, n) => o.getVariables().get(n);
  const hist = scn._fdizBotH || (scn._fdizBotH = {});
  for (const s of sups) {
    if (g(s, "Control").getAsNumber() !== -1 || g(s, "Estado").getAsString() !== "normal") continue;
    const sx = s.getX(), sy = s.getY(), who = g(s, "Personaje").getAsString();
    let n120 = 0, n220 = 0, n330 = 0, big = 0, bigNear = 0;
    for (const z of zs) {
      const d = Math.hypot(z.getX() - sx, z.getY() - sy);
      if (d < 120) n120++; if (d < 220) n220++; if (d < 330) n330++;
      if (d < 260 && z.getVariables().get("Vida").getAsNumber() > 60) bigNear++;
    }
    const vida = g(s, "Vida").getAsNumber(), vmax = Math.max(1, g(s, "VidaMax").getAsNumber()), hp = vida / vmax;
    const mord = g(s, "Mordido").getAsNumber() > 0;
    // aliados heridos cerca
    let heridos = 0, muyHeridos = 0;
    for (const o of sups) {
      if (g(o, "Estado").getAsString() === "muerto") continue;
      if (Math.hypot(o.getX() - sx, o.getY() - sy) > 360) continue;
      const h = g(o, "Vida").getAsNumber() / Math.max(1, g(o, "VidaMax").getAsNumber());
      if (h < 0.65) heridos++; if (h < 0.35) muyHeridos++;
    }
    let hab = false, esp = false;
    const peligro = n220 >= 2 && hp < 0.45;
    switch (who) {
      case "tony": hab = n220 >= 2 || heridos >= 1 && n330 >= 1; esp = n220 >= 4 || peligro || n330 >= 6; break;
      case "miranda": hab = n220 >= 2; esp = n330 >= 3 || bigNear >= 1; break;
      case "cesar": hab = n220 >= 2; esp = n220 >= 4 || bigNear >= 2; break;
      case "alan": hab = n220 >= 3; esp = n330 >= 5 || peligro; break;
      case "castillo": hab = hp < 0.6 || heridos >= 1 && n330 >= 1; esp = muyHeridos >= 1 || heridos >= 2 || mord; break;
      case "alessandro": hab = n220 >= 2; esp = n220 >= 4 || peligro || bigNear >= 2; break;
      case "gabo": hab = n220 >= 2 || hp < 0.6 && n330 >= 1; esp = n220 >= 3 || peligro; break;
      case "carlos": hab = n220 >= 2; esp = n120 >= 2 || peligro || bigNear >= 1; break;
      default: hab = n220 >= 3; esp = n220 >= 5;
    }
    if (n330 === 0) { hab = false; esp = false; if (who === "castillo" && (hp < 0.5 || mord)) { hab = hp < 0.5; esp = mord || muyHeridos >= 1; } }
    if (hab) g(s, "PideHab").setNumber(1);
    if (esp) g(s, "PideEsp").setNumber(1);
  }
})();
