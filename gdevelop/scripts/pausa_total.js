/* FDI-Z · Fase 85 · Pausa total: al abrir el menú de pausa se detiene TODO el sonido (música, efectos, voces, alarma) y
 * los videos; al cerrarlo, cada cosa sigue justo donde se quedó.
 * Se incrusta en la escena Juego con scripts/fase85_pausa_ui_tutorial_escape.py (evento FDIZ-FASE85-PAUSA, cada cuadro).
 * Antes la pausa solo ponía el tiempo en 0 (ChangeTimeScale): lo que ya estaba sonando seguía sonando.
 * Cómo: con Pausa = 1 pausa cada sonido activo de Howler (música, canales y sonidos sueltos), y pausa los videos de la escena. Los anota y al quitar la pausa los reanuda (solo esos: lo que se haya
 * detenido a propósito no vuelve). Los sonidos nuevos durante la pausa (clics del menú) sí suenan. */
(function (gdjs) {
  "use strict";
  if (gdjs.fdizPausaTotal && gdjs.fdizPausaTotal.VER === 1) return;
  const P = (gdjs.fdizPausaTotal = { VER: 1 });

  // cada sonido activo de Howler (el motor de audio de GDevelop): [howl, id]. Se usa Howler directamente porque el pause()
  // de los sonidos sueltos de GDevelop no siempre surte efecto (su id interno no coincide) y así se cubre todo lo que suena.
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
    const st = scn._fdizPausaTotal || (scn._fdizPausaTotal = { activa: false, s: [], v: [] });
    let pausa = false; try { pausa = scn.getVariables().get("Pausa").getAsNumber() === 1; } catch (e) { return; }
    if (pausa && !st.activa) {
      st.activa = true; st.s = []; st.v = [];
      for (const [h, id] of activos()) { try { h.pause(id); st.s.push([h, id]); } catch (e) { /* ya terminó */ } }
      for (const v of videos(scn)) { try { if (v.isPlayed()) { v.pause(); st.v.push(v); } } catch (e) { /* sin video */ } }
    } else if (!pausa && st.activa) {
      st.activa = false;
      for (const [h, id] of st.s) { try { const snd = h._soundById ? h._soundById(id) : null; if (snd && snd._paused && !snd._ended) h.play(id); } catch (e) { /* ya no existe */ } }
      for (const v of st.v) { try { if (v._livingOnScene !== false) v.play(); } catch (e) { /* ya no está */ } }
      st.s = []; st.v = [];
    }
  };
})(gdjs);
