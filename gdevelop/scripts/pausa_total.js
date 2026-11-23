/* FDI-Z · Fase 85 / 86 · Pausa total: con el menú de pausa o con el tutorial abierto se detiene TODO —sonido (música,
 * efectos, voces, alarma), videos y el reloj de los diálogos, la historia y las cinemáticas— y al cerrarlo cada cosa sigue
 * justo donde se quedó.
 * Se incrusta en la escena Juego con scripts/fase85_pausa_ui_tutorial_escape.py (evento FDIZ-FASE85-PAUSA, al final).
 * Antes la pausa solo ponía el tiempo del juego en 0 (ChangeTimeScale): lo que ya sonaba seguía sonando y los diálogos
 * (dialogo.js, historia.js, cine.js miden con el reloj real) seguían avanzando: con el tutorial abierto se oían las voces.
 * Cómo:
 *   - Sonido: pausa cada sonido activo de Howler (el motor de audio de GDevelop) y lo reanuda al salir. Se usa Howler
 *     directamente porque el pause() de los sonidos sueltos de GDevelop no siempre surte efecto.
 *   - Videos: los de la escena que estén corriendo.
 *   - Reloj: D.now, H.now y C.now (diálogos, historia, cinemáticas) pasan a P.ahora, un reloj que se congela mientras dura
 *     la pausa y al salir sigue sin saltarse el tiempo que estuvo detenido.
 * Motivos: "menu" (Pausa = 1) y "tuto" (tutorial abierto, scn._fdizTuto.open). Se reanuda cuando ya no queda ninguno.
 * Los sonidos nuevos durante la pausa (clics del menú) sí suenan. */
(function (gdjs) {
  "use strict";
  if (gdjs.fdizPausaTotal && gdjs.fdizPausaTotal.VER === 2) return;
  const P = (gdjs.fdizPausaTotal = { VER: 2, offset: 0, congelado: null });

  P.ahora = () => (P.congelado !== null ? P.congelado : Date.now() / 1000 - P.offset);
  function relojes() {
    for (const m of [gdjs.fdizDialogo, gdjs.fdizHistoria, gdjs.fdizCine, gdjs.fdizCanepa]) if (m && m.now !== P.ahora) m.now = P.ahora;
  }
  function activos() {
    const out = [];
    const H = (typeof Howler !== "undefined" && Howler) || (typeof window !== "undefined" && window.Howler);
    for (const h of (H && H._howls) || []) for (const snd of h._sounds || []) if (!snd._paused && !snd._ended) out.push([h, snd._id]);
    return out;
  }
  function videos(scn) {
    const out = [];
    try { for (const o of scn.getAdhocListOfAllInstances()) if (typeof o.isPlayed === "function" && typeof o.pause === "function") out.push(o); } catch (e) { /* sin lista */ }
    return out;
  }

  P.tick = function (scn) {
    relojes();
    const st = scn._fdizPausaTotal || (scn._fdizPausaTotal = { activa: false, s: [], v: [] });
    let menu = false; try { menu = scn.getVariables().get("Pausa").getAsNumber() === 1; } catch (e) { return; }
    const tuto = !!(scn._fdizTuto && scn._fdizTuto.open);
    const pausa = menu || tuto;
    if (pausa && !st.activa) {
      st.activa = true; st.s = []; st.v = [];
      P.congelado = Date.now() / 1000 - P.offset;
      for (const [h, id] of activos()) { try { h.pause(id); st.s.push([h, id]); } catch (e) { /* ya terminó */ } }
      for (const v of videos(scn)) { try { if (v.isPlayed()) { v.pause(); st.v.push(v); } } catch (e) { /* sin video */ } }
    } else if (!pausa && st.activa) {
      st.activa = false;
      if (P.congelado !== null) { P.offset = Date.now() / 1000 - P.congelado; P.congelado = null; }
      for (const [h, id] of st.s) { try { const snd = h._soundById ? h._soundById(id) : null; if (snd && snd._paused && !snd._ended) h.play(id); } catch (e) { /* ya no existe */ } }
      for (const v of st.v) { try { if (v._livingOnScene !== false) v.play(); } catch (e) { /* ya no está */ } }
      st.s = []; st.v = [];
    }
  };
})(gdjs);
