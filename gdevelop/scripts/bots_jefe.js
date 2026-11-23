/* FDI-Z · Fase 82 · Bots del modo Jefe: cada uno se mueve distinto, reacciona a lo que tiene cerca y no se atora.
 * Se incrusta en la escena Juego con scripts/fase82_armas_y_bots_jefe.py (no editar el evento a mano): evento
 * FDIZ-FASE82-BOTSJEFE entre «Bots: objetivos y puertas» y «Bots: curar mordidos» (curar sigue mandando sobre esto).
 *
 * Antes: sin humanos, los 4 bots iban en línea recta (sin ruta) hacia el mismo guía invisible; se formaban en fila, se
 * pegaban a las esquinas y no peleaban (el guía pisaba el combate) salvo con el zombi a 95 px.
 * Ahora (solo Jefe = 1, host / sin red, bots de pie):
 *   - Meta común: el objetivo actual (ObjX, ObjY) o, si no hay, el guía. Cada bot va a SU lugar alrededor de la meta
 *     (ángulo y distancia propios) por ruta A* (gdjs.fdizNav), recalculada cada ~0.7 s, así no se enciman ni hacen fila.
 *   - Personalidad (PERFIL): Tony va al frente y pelea de cerca; Miranda se queda atrás y cubre; César flanquea por un
 *     lado y deambula un poco; Alan explora y se desvía a casilleros cercanos. Distinto radio de reacción y ritmo.
 *   - Reacción: zombi cerca y a la vista -> con arma de fuego dispara a distancia (hasta su alcance) y retrocede si se
 *     le acerca demasiado; sin arma va por él y le pega. Si FASE29 marcó huir (Huye = 1) se aleja por ruta.
 *   - Puertas: con una puerta cerrada en su camino se detiene y la abre (Usando); si en 3 s no abre, la golpea.
 *   - Desatasco: si quiere moverse y en 0.8 s avanzó menos de 18 px, toma un rodeo a un punto libre cercano 1.2 s.
 *   - Misión: el bot más cercano al objetivo va a él y lo usa (Usando = 1, también las llaves); los demás lo cubren.
 *   - Junto al objetivo o a una puerta (Usando = 1, eventos de la fase de objetivos) no toca nada: ahí se cumple la misión. */
(function (gdjs) {
  "use strict";
  if (gdjs.fdizBotsJefe && gdjs.fdizBotsJefe.VER === 1) return;
  const B = (gdjs.fdizBotsJefe = { VER: 1 });

  // ang: lugar alrededor de la meta (rad); dist: px a la meta; react: px a los que reacciona a un zombi;
  // repath: s entre rutas; vaga: px de deambular; explora: se desvía a casilleros a menos de esos px
  B.PERFIL = {
    tony: { ang: 0.0, dist: 70, react: 340, repath: 0.6, vaga: 20, explora: 0 },
    miranda: { ang: Math.PI, dist: 150, react: 260, repath: 0.8, vaga: 30, explora: 0 },
    cesar: { ang: Math.PI / 2, dist: 120, react: 300, repath: 0.7, vaga: 70, explora: 0 },
    alan: { ang: -Math.PI / 2, dist: 120, react: 280, repath: 0.75, vaga: 40, explora: 420 },
  };
  B.DEF = { ang: 2.4, dist: 110, react: 300, repath: 0.7, vaga: 40, explora: 0 };
  B.CERCA = 170;          // con arma de fuego, más cerca que esto retrocede
  B.MELEE = 95;           // a esta distancia pega (igual que los bots normales)
  B.PX_ALCANCE = 240;     // px de bala por punto de Alcance (bala ~1000 px/s x Alcance/4 s)
  B.ZN = ["ZNormal", "ZCorredor", "ZGriton", "ZGordo", "ZConserje", "ZCurado", "ZJoel", "ZJustino", "ZCanepa"];

  const VS = (o, n) => o.getVariables().get(n);
  const num = (o, n) => VS(o, n).getAsNumber();
  const str = (o, n) => VS(o, n).getAsString();
  const objs = (scn, n) => { try { return scn.getObjects(n) || []; } catch (e) { return []; } };
  const hyp = Math.hypot;

  // línea de tiro libre de muros y puertas (los muebles no tapan las balas)
  function tiroLibre(scn, ax, ay, bx, by) {
    const d = hyp(bx - ax, by - ay), n = Math.max(1, Math.ceil(d / 28));
    const cajas = scn._f82cajas;
    for (let k = 1; k < n; k++) {
      const x = ax + (bx - ax) * k / n, y = ay + (by - ay) * k / n;
      for (const c of cajas) if (x >= c[0] && x <= c[2] && y >= c[1] && y <= c[3]) return false;
    }
    return true;
  }
  function cajas(scn) {
    const out = [];
    for (const n of ["Muro", "Puerta"]) for (const o of objs(scn, n)) {
      if (!o.isVisible() && n === "Puerta") continue;
      out.push([o.getX(), o.getY(), o.getX() + o.getWidth(), o.getY() + o.getHeight()]);
    }
    scn._f82cajas = out;
  }
  function dir(s, x, y, k) {
    const dx = x - s.getX(), dy = y - s.getY(), d = Math.max(1, hyp(dx, dy));
    VS(s, "MovX").setNumber(dx / d * (k || 1)); VS(s, "MovY").setNumber(dy / d * (k || 1));
  }
  function libre(x, y) {
    const N = gdjs.fdizNav; if (!N || !N.grid) return true;
    return N.grid.cls[N.cellOf(x, y)] !== 1;
  }
  // sigue una ruta A* hasta (tx, ty); la recalcula cada «cada» s o si cambió mucho el destino
  function ir(s, m, tx, ty, cada) {
    const N = gdjs.fdizNav;
    if (!N || !N.grid || !N.path) { dir(s, tx, ty); return; }
    const sx = s.getX(), sy = s.getY();
    if (!m.ruta || m.tRuta <= 0 || hyp(tx - m.rx, ty - m.ry) > 90) {
      const r = N.path(sx, sy, tx, ty);
      m.ruta = r && r.pts && r.pts.length ? r.pts.slice(1) : [[tx, ty]]; m.rx = tx; m.ry = ty; m.tRuta = cada;
    }
    while (m.ruta.length > 1 && hyp(m.ruta[0][0] - sx, m.ruta[0][1] - sy) < 26) m.ruta.shift();
    const p = m.ruta[0] || [tx, ty];
    if (hyp(tx - sx, ty - sy) < 24) { VS(s, "MovX").setNumber(0); VS(s, "MovY").setNumber(0); return; }
    if (abrir(s, m, p)) return;
    dir(s, p[0], p[1]);
  }
  // puerta cerrada junto al bot y en su camino: se detiene, la abre (Usando) y, si tarda, la golpea
  function abrir(s, m, p) {
    const scn = s.getRuntimeScene ? s.getRuntimeScene() : null; if (!scn) return false;
    const sx = s.getX(), sy = s.getY();
    let pu = null, pd = 1e9;
    for (const o of objs(scn, "Puerta")) {
      if (!o.isVisible()) continue;
      const cx = o.getX() + o.getWidth() / 2, cy = o.getY() + o.getHeight() / 2, d = hyp(cx - sx, cy - sy);
      if (d < pd) { pd = d; pu = o; }
    }
    if (!pu || pd > 115) { m.tPuerta = 0; return false; }
    const cx = pu.getX() + pu.getWidth() / 2, cy = pu.getY() + pu.getHeight() / 2;
    // solo si el siguiente punto de la ruta queda del otro lado o junto a la puerta
    if (hyp(p[0] - cx, p[1] - cy) > 130 && ((p[0] - sx) * (cx - sx) + (p[1] - sy) * (cy - sy)) <= 0) return false;
    m.tPuerta = (m.tPuerta || 0) + Math.min(0.1, scn.getElapsedTime() / 1000);
    VS(s, "MovX").setNumber(0); VS(s, "MovY").setNumber(0);
    VS(s, "AimX").setNumber(cx - sx); VS(s, "AimY").setNumber(cy - sy);
    VS(s, "Usando").setNumber(1);
    if (m.tPuerta > 3) VS(s, "QuierePegar").setNumber(1);
    if (m.tPuerta > 9) { m.tPuerta = 0; m.rodeo = 0; }
    return true;
  }

  // quiere moverse pero en 0.8 s avanzó menos de 18 px: rodeo a un punto libre cercano 1.2 s
  function desatasco(s, m, sx, sy) {
    if (m.tChk < 0.8) return;
    const quiere = Math.abs(num(s, "MovX")) + Math.abs(num(s, "MovY")) > 0.3;
    if (quiere && hyp(sx - m.lx, sy - m.ly) < 18 && m.rodeo <= 0) {
      for (let k = 0; k < 8; k++) {
        const a = Math.random() * 6.283, r = 90 + Math.random() * 120, px = sx + Math.cos(a) * r, py = sy + Math.sin(a) * r;
        if (libre(px, py)) { m.rx2 = px; m.ry2 = py; m.rodeo = 1.2; m.ruta = null; break; }
      }
    }
    m.lx = sx; m.ly = sy; m.tChk = 0;
  }

  B.tick = function (scn) {
    if (scn.getGame().getVariables().get("NetRol").getAsNumber() === 2) return;
    const SV = scn.getVariables();
    if (SV.get("Jefe").getAsNumber() !== 1 || SV.get("Estado").getAsString() !== "juego" || SV.get("Pausa").getAsNumber() === 1) return;
    const dt = Math.min(0.1, scn.getElapsedTime() / 1000);
    const bots = objs(scn, "Sup").filter((s) => num(s, "Control") === -1 && str(s, "Estado") === "normal");
    if (!bots.length) return;
    cajas(scn);
    const Z = [];
    for (const n of B.ZN) for (const z of objs(scn, n)) {
      try { if (str(z, "Estado") !== "muerto" && num(z, "Aliado") === 0 && num(z, "Vida") > 0) Z.push(z); } catch (e) { /* sin variables */ }
    }
    let mx = SV.get("ObjX").getAsNumber(), my = SV.get("ObjY").getAsNumber();
    if (!(mx >= 0)) { const g = objs(scn, "Guia")[0]; if (g) { mx = g.getX(); my = g.getY(); } else { mx = SV.get("SegX").getAsNumber(); my = SV.get("SegY").getAsNumber(); } }
    const T = scn.getTimeManager().getTimeFromStart() / 1000;
    // la misión: el objetivo sin hacer más cercano a la meta; lo trabaja el bot más cercano (los demás lo cubren)
    let obj = null, od = 1e9;
    for (const o of objs(scn, "Objetivo")) {
      try { if (num(o, "Hecho") !== 0) continue; } catch (e) { continue; }
      const d = hyp(o.getX() - mx, o.getY() - my); if (d < od) { od = d; obj = o; }
    }
    if (obj && od > 400) obj = null;
    let obrero = null;
    if (obj) { let bd = 1e9; for (const s of bots) { const d = hyp(s.getX() - obj.getX(), s.getY() - obj.getY()); if (d < bd) { bd = d; obrero = s; } } }

    for (const s of bots) {
      if (num(s, "Usando") === 1) continue;                 // junto al objetivo / puerta: lo maneja la fase de objetivos
      const P = B.PERFIL[str(s, "Personaje")] || B.DEF;
      const m = s.__f82 || (s.__f82 = { tRuta: 0, lx: s.getX(), ly: s.getY(), tChk: 0, rodeo: 0, rx: 0, ry: 0, ruta: null, fase: Math.random() * 6.28, desvio: null, tDesv: 0 });
      m.tRuta -= dt; m.tChk += dt; m.rodeo -= dt; m.tDesv -= dt;
      const sx = s.getX(), sy = s.getY();

      // ---- el que trabaja la misión va al objetivo y lo usa (solo se defiende si un zombi se le echa encima)
      if (s === obrero) {
        const d = hyp(obj.getX() - sx, obj.getY() - sy);
        let zc = null, zcd = 1e9;
        for (const q of Z) { const dq = hyp(q.getX() - sx, q.getY() - sy); if (dq < zcd) { zcd = dq; zc = q; } }
        if (zc && zcd < 110) { VS(s, "AimX").setNumber(zc.getX() - sx); VS(s, "AimY").setNumber(zc.getY() - sy); VS(s, "QuierePegar").setNumber(1); }
        if (d > 110) { if (m.rodeo > 0) ir(s, m, m.rx2, m.ry2, 0.4); else ir(s, m, obj.getX(), obj.getY(), 0.5); }
        else { VS(s, "MovX").setNumber(0); VS(s, "MovY").setNumber(0); VS(s, "Usando").setNumber(1); }
        desatasco(s, m, sx, sy);
        continue;
      }

      // ---- zombi más cercano a la vista
      let z = null, zd = 1e9;
      for (const q of Z) { const d = hyp(q.getX() - sx, q.getY() - sy); if (d < zd) { zd = d; z = q; } }
      const fuego = num(s, "ArmaFuego") === 1;
      const alcance = fuego ? Math.max(B.CERCA + 40, num(s, "Alcance") * B.PX_ALCANCE) : B.MELEE;
      const vista = z && zd < Math.max(P.react, fuego ? alcance : 0) && tiroLibre(scn, sx, sy - 46, z.getX(), z.getY() - 40);

      if (num(s, "Huye") === 1 && !(fuego && vista && zd > B.CERCA)) {
        ir(s, m, num(s, "BotX"), num(s, "BotY"), 0.5);
      } else if (vista) {
        VS(s, "AimX").setNumber(z.getX() - sx); VS(s, "AimY").setNumber(z.getY() - sy);
        if (fuego) {
          if (zd <= alcance) VS(s, "QuierePegar").setNumber(1);
          if (zd < B.CERCA) { dir(s, sx - (z.getX() - sx), sy - (z.getY() - sy), 0.9); m.ruta = null; }
          else {                                              // se mueve de lado mientras dispara
            const a = Math.atan2(z.getY() - sy, z.getX() - sx) + Math.PI / 2 * (Math.sin(T * 0.9 + m.fase) > 0 ? 1 : -1);
            const px = sx + Math.cos(a) * 60, py = sy + Math.sin(a) * 60;
            if (libre(px, py)) dir(s, px, py, 0.45); else { VS(s, "MovX").setNumber(0); VS(s, "MovY").setNumber(0); }
          }
        } else {
          if (zd > 70) ir(s, m, z.getX(), z.getY(), 0.35);
          else { VS(s, "MovX").setNumber(0); VS(s, "MovY").setNumber(0); }
          if (zd <= B.MELEE) VS(s, "QuierePegar").setNumber(1);
        }
      } else {
        // ---- a su lugar alrededor de la meta (con deambular y desvíos propios)
        const aDir = Math.atan2(my - sy, mx - sx);
        const a = aDir + Math.PI + P.ang + Math.sin(T * 0.35 + m.fase) * 0.35;
        let tx = mx + Math.cos(a) * P.dist + Math.sin(T * 0.7 + m.fase) * P.vaga;
        let ty = my + Math.sin(a) * P.dist + Math.cos(T * 0.6 + m.fase) * P.vaga;
        if (P.explora && hyp(mx - sx, my - sy) > 300) {
          if (m.tDesv <= 0) {
            m.tDesv = 9 + Math.random() * 6; m.desvio = null;
            for (const c of objs(scn, "Contenedor")) {
              const d = hyp(c.getX() - sx, c.getY() - sy);
              if (d > 120 && d < P.explora && libre(c.getX(), c.getY() + 60)) { m.desvio = [c.getX(), c.getY() + 60, T + 3]; break; }
            }
          }
          if (m.desvio && T < m.desvio[2]) { tx = m.desvio[0]; ty = m.desvio[1]; }
        }
        if (!libre(tx, ty)) { const N = gdjs.fdizNav; const f = N && N.nearestFree ? N.nearestFree(tx, ty, 6) : null; if (f) { tx = f[0]; ty = f[1]; } else { tx = mx; ty = my; } }
        if (m.rodeo > 0) ir(s, m, m.rx2, m.ry2, 0.4);
        else ir(s, m, tx, ty, P.repath);
      }

      desatasco(s, m, sx, sy);
    }
  };
})(gdjs);
