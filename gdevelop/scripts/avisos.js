/* FDI-Z · Fase 63 · Color de los letreros de eventos (TxtBanner) durante la partida. Todos los modos.
 * Se incrusta en la escena Juego con scripts/fase63_avisos.py (no editar el evento a mano): FDIZ-FASE63-MOD arriba de
 * todo y FDIZ-FASE63-COLOR dentro del evento del grupo "HUD" que muestra el letrero (corre en todas las máquinas).
 *
 * Todos los letreros pasan por la variable de escena Banner (eventos de objetivos, final, mordidos, habilidades, HUD,
 * puertas, y los módulos profes.js y medios.js) y se muestran con el objeto TxtBanner. Antes ese objeto era rojo fijo.
 * Regla:
 *   ROJO   solo si el mensaje dice que un personaje se infectó (mordido / mordida, infectado, se convirtió en zombi)
 *          o que la FDI se está llenando;
 *   VERDE  todo lo demás (objetivos, acciones cumplidas, avisos positivos, el final...).
 * El texto se compara normalizado (minúsculas, sin acentos ni signos, espacios simples), así que «¡P2 MORDIDO!»,
 * «Canepa mordida», «SE CONVIRTIÓ EN ZOMBIE» o «la fdi se esta llenando» se clasifican igual. El texto y el momento en
 * que aparece cada letrero no cambian: solo el color. */
(function (gdjs) {
  "use strict";
  if (gdjs.fdizAvisos && gdjs.fdizAvisos.VER === 1) return;
  const A = (gdjs.fdizAvisos = { VER: 1 });
  A.ROJO = "255;80;80";
  A.VERDE = "110;230;110";

  A.normalizar = function (s) {
    return String(s || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase()
      .replace(/[^a-z0-9]+/g, " ").replace(/\s+/g, " ").trim();
  };
  const INFECCION = [/\bmordid[oa]s?\b/, /\binfectad[oa]s?\b/, /\bse infect/, /\bconvirti\w* en zombi(e|s|es)?\b/, /\bzombificad/];
  const LLENA = [/\bfdi\b.*\bllen(ando|a|o|ndose)\b/];
  const POSITIVO = [/\bsalvad[oa]s?\b/, /\bcurad[oa]s?\b/, /\bya no\b/];   // «curado de la mordida» no es rojo
  A.esRojo = function (texto) {
    const t = A.normalizar(texto);
    if (!t) return false;
    if (LLENA.some((r) => r.test(t)) && !/\bya no\b/.test(t)) return true;
    return INFECCION.some((r) => r.test(t)) && !POSITIVO.some((r) => r.test(t));
  };
  A.color = (texto) => (A.esRojo(texto) ? A.ROJO : A.VERDE);

  // dentro del evento que muestra el letrero: pone el color que le toca al texto que se ve
  A.aplicar = function (scn) {
    for (const t of scn.getObjects("TxtBanner") || []) {
      const s = t.getString ? t.getString() : "";
      if (t.__fdizAviso === s) continue;                         // solo cuando cambia el texto
      t.__fdizAviso = s;
      t.setColor(A.color(s));
    }
  };
})(gdjs);
