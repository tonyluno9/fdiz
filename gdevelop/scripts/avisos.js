/* FDI-Z · Fase 63 (+ fase 70) · Color de los letreros de eventos (TxtBanner) durante la partida. Todos los modos.
 * Se incrusta en la escena Juego con scripts/fase63_avisos.py (no editar el evento a mano): FDIZ-FASE63-MOD arriba de
 * todo y FDIZ-FASE63-COLOR dentro del evento del grupo "HUD" que muestra el letrero (corre en todas las máquinas).
 *
 * Todos los letreros pasan por la variable de escena Banner (eventos de objetivos, final, mordidos, habilidades, HUD,
 * puertas, y los módulos profes.js, medios.js e historia.js) y se muestran con el objeto TxtBanner.
 * Regla (fase 70, clasificación de gdevelop/ALERTAS.md):
 *   ROJO     peligro: un personaje se infectó (mordido / mordida, infectado, se convirtió en zombi), la FDI se está
 *            llenando, el zombi rompió la puerta (Historia) o un profe quedó fuera de combate;
 *   AMARILLO aviso de evento: se fue la luz, nuevo objetivo, al estacionamiento, ¡aguanten!, los objetivos de Historia,
 *            recoge la pistola, llave de la reja, vienen más, la última oleada, un profe se quedó atrás;
 *   VERDE    todo lo demás (acciones cumplidas, habilidades, salvados, se une al equipo, escaparon...).
 * El texto se compara normalizado (minúsculas, sin acentos ni signos, espacios simples), así que «¡P2 MORDIDO!»,
 * «Canepa mordida», «SE CONVIRTIÓ EN ZOMBIE» o «la fdi se esta llenando» se clasifican igual. El texto y el momento en
 * que aparece cada letrero no cambian: solo el color. */
(function (gdjs) {
  "use strict";
  if (gdjs.fdizAvisos && gdjs.fdizAvisos.VER === 2) return;
  const A = (gdjs.fdizAvisos = { VER: 2 });
  A.ROJO = "255;80;80";
  A.AMARILLO = "255;240;150";
  A.VERDE = "110;230;110";

  A.normalizar = function (s) {
    return String(s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase()
      .replace(/[^a-z0-9]+/g, " ").replace(/\s+/g, " ").trim();
  };
  const INFECCION = [/\bmordid[oa]s?\b/, /\binfectad[oa]s?\b/, /\bse infect/, /\bconvirti\w* en zombi(e|s|es)?\b/, /\bzombificad/];
  const LLENA = [/\bfdi\b.*\bllen(ando|a|o|ndose)\b/];
  const POSITIVO = [/\bsalvad[oa]s?\b/, /\bcurad[oa]s?\b/, /\bya no\b/];   // «curado de la mordida» no es rojo
  const PELIGRO = [/^rompio la puerta$/, /\bquedo fuera de combate$/];
  const AVISO = [
    /^se fue la luz$/, /^nuevo objetivo$/, /^al estacionamiento$/, /^aguanten\b/,
    // objetivos de Historia (historia.js, función objetivo): el texto empieza con la acción
    /^(revisa|llega|usa|encuentra|busca|consigue) /,
    /^recoge la pistola\b/, /^llave de la reja\b/, /^vienen mas$/, /^la ultima oleada$/, /\bse quedo atras$/,
  ];
  A.esRojo = function (texto) {
    const t = A.normalizar(texto);
    if (!t) return false;
    if (LLENA.some((r) => r.test(t)) && !/\bya no\b/.test(t)) return true;
    if (PELIGRO.some((r) => r.test(t))) return true;
    return INFECCION.some((r) => r.test(t)) && !POSITIVO.some((r) => r.test(t));
  };
  A.esAmarillo = function (texto) {
    const t = A.normalizar(texto);
    return !!t && !A.esRojo(texto) && AVISO.some((r) => r.test(t));
  };
  A.color = (texto) => (A.esRojo(texto) ? A.ROJO : A.esAmarillo(texto) ? A.AMARILLO : A.VERDE);

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
