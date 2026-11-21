/* FDI-Z · Fase 43 · Bloque Críticos (reporte de pruebas de jugabilidad).
 * Se incrusta en un evento JavaScript de la escena Juego con scripts/fase43_criticos.py. No editar el evento a mano.
 *
 *  1) K.puertas(scn): red de seguridad para zombis. Si un zombi cambia de lado de una puerta cerrada en un cuadro
 *     (por ejemplo empujado por una máscara de colisión mal puesta), vuelve a su última posición buena.
 *  2) K.desatasco(scn): los aliados (bots y profes aliados, Control = -1) se destraban solos. Si quieren moverse y no
 *     avanzan, prueban en orden: paso lateral, salir de una celda bloqueada, salto corto por la ruta y, como último
 *     recurso, reaparecer junto a un humano. Nunca cruzan una puerta cerrada ni un muro al saltar.
 */
(function (gdjs) {
  "use strict";
  const K = (gdjs.fdizCriticos = gdjs.fdizCriticos || {});

  // ---------- 1) zombis y puertas ----------
  // ¿el segmento a→b toca el rectángulo? (Liang–Barsky)
  K.segRect = function (ax, ay, bx, by, x0, y0, x1, y1) {
    let t0 = 0, t1 = 1;
    const dx = bx - ax, dy = by - ay;
    const p = [-dx, dx, -dy, dy], q = [ax - x0, x1 - ax, ay - y0, y1 - ay];
    for (let i = 0; i < 4; i++) {
      if (p[i] === 0) { if (q[i] < 0) return false; continue; }
      const r = q[i] / p[i];
      if (p[i] < 0) { if (r > t1) return false; if (r > t0) t0 = r; }
      else { if (r < t0) return false; if (r < t1) t1 = r; }
    }
    return true;
  };
  K.dentro = function (x, y, r) { return x >= r[0] && x <= r[2] && y >= r[1] && y <= r[3]; };

  const ZN = ["ZNormal", "ZCorredor", "ZGriton", "ZGordo", "ZConserje", "ZCurado", "ZJoel", "ZJustino", "ZCanepa"];
  K.puertas = function (scn) {
    K.abrirPasos(gdjs.fdizNav);
    const doors = scn.getObjects("Puerta") || [];
    const R = [];
    for (const p of doors) { const b = p.getAABB(); R.push([b.min[0] - 2, b.min[1] - 2, b.max[0] + 2, b.max[1] + 2]); }
    for (const n of ZN) {
      for (const z of (scn.getObjects(n) || [])) {
        const x = z.getX(), y = z.getY(), L = z.__f43;
        if (!L) { z.__f43 = { x, y }; continue; }
        let cruza = false;
        if (Math.abs(x - L.x) + Math.abs(y - L.y) > 0.01) {
          for (const r of R) {
            // prefiltro por caja del movimiento
            if (Math.max(x, L.x) < r[0] || Math.min(x, L.x) > r[2] || Math.max(y, L.y) < r[1] || Math.min(y, L.y) > r[3]) continue;
            if (K.dentro(L.x, L.y, r)) continue; // ya estaba encima de la puerta (nació ahí): lo dejamos salir
            if (K.dentro(x, y, r) || K.segRect(L.x, L.y, x, y, r[0], r[1], r[2], r[3])) { cruza = true; break; }
          }
        }
        if (cruza) { z.setPosition(L.x, L.y); K.cruces = (K.cruces || 0) + 1; }
        else { L.x = x; L.y = y; }
      }
    }
  };


  // Veto exacto de golpes: el evento original muestrea 7 puntos de la línea; aquí se prueba el segmento completo contra
  // las puertas (+10 px a lo largo, solo si zombi y objetivo quedan de lados opuestos). `objects` = zombi del "Para cada"
  // (evento con parámetro de objeto Zombies).
  K.golpe = function (scn, objetos) {
    if (!objetos || !objetos.length) return;
    const z = objetos[0], zx = z.getX(), zy = z.getY();
    let t = null, md = 1e9;
    for (const s of (scn.getObjects("Sup") || [])) {
      if (s.getVariables().get("Estado").getAsString() !== "normal") continue;
      const d = Math.hypot(s.getX() - zx, s.getY() - zy); if (d < md) { md = d; t = s; }
    }
    if (!t || md > 160) return;
    const tx = t.getX(), ty = t.getY();
    const x0 = Math.min(zx, tx) - 12, x1 = Math.max(zx, tx) + 12, y0 = Math.min(zy, ty) - 12, y1 = Math.max(zy, ty) + 12;
    for (const o of (scn.getObjects("Puerta") || [])) {
      const b = o.getAABB(), horiz = (b.max[0] - b.min[0]) >= (b.max[1] - b.min[1]);
      const r = horiz ? [b.min[0] - 10, b.min[1], b.max[0] + 10, b.max[1]] : [b.min[0], b.min[1] - 10, b.max[0], b.max[1] + 10];
      if (r[2] < x0 || r[0] > x1 || r[3] < y0 || r[1] > y1) continue;
      const lado = (x, y) => horiz ? (y < b.min[1] ? -1 : y > b.max[1] ? 1 : 0) : (x < b.min[0] ? -1 : x > b.max[0] ? 1 : 0);
      if (lado(zx, zy) * lado(tx, ty) !== -1) continue;
      if (K.segRect(zx, zy, tx, ty, r[0], r[1], r[2], r[3])) { scn.getVariables().get("Bloq").setNumber(1); K.vetos = (K.vetos || 0) + 1; return; }
    }
  };

  // ---------- 1b) pasos angostos que la rejilla A* cerraba ----------
  // La rejilla deja 18 px de holgura a cada lado (cuerpo de 32 px de ancho), pero los pies miden solo 14 px de alto:
  // un paso horizontal de 32 px de alto (como la entrada al pasillo de la conserjería) cabe, y A* lo creía cerrado. Resultado:
  // el conserje y los bots no encontraban ruta. Aquí se abren las celdas que, con la holgura real de los pies, son
  // transitables Y unen dos zonas que de otro modo quedan separadas (no se abre nada más).
  K.abrirPasos = function (NAV) {
    const g = NAV && NAV.grid; if (!g || g.__f43 || !g.rects) return;
    g.__f43 = true;
    const C = NAV.cfg.C, W = g.W, H = g.H, n = W * H, wall = g.wall;
    const F = new Uint8Array(n);
    for (const r of g.rects) {
      const x0 = r[0] - 18, x1 = r[2] + 18, y0 = r[1] - 2, y1 = r[3] + 16;
      const cx0 = Math.max(0, Math.floor(x0 / C - 0.5)), cx1 = Math.min(W - 1, Math.ceil(x1 / C - 0.5));
      const cy0 = Math.max(0, Math.floor(y0 / C - 0.5)), cy1 = Math.min(H - 1, Math.ceil(y1 / C - 0.5));
      for (let cy = cy0; cy <= cy1; cy++) {
        const py = (cy + 0.5) * C; if (py <= y0 || py >= y1) continue;
        for (let cx = cx0; cx <= cx1; cx++) { const px = (cx + 0.5) * C; if (px > x0 && px < x1) F[cy * W + cx] = 1; }
      }
    }
    const comp = new Int32Array(n).fill(-1); let nc = 0; const pila = [];
    const vec = [1, -1, W, -W];
    for (let s0 = 0; s0 < n; s0++) {
      if (wall[s0] !== 0 || comp[s0] >= 0) continue;
      comp[s0] = nc; pila.push(s0);
      while (pila.length) {
        const c = pila.pop(), x = c % W;
        for (let k = 0; k < 4; k++) {
          if (k === 0 && x === W - 1) continue; if (k === 1 && x === 0) continue;
          const m = c + vec[k]; if (m < 0 || m >= n) continue;
          if (wall[m] === 0 && comp[m] < 0) { comp[m] = nc; pila.push(m); }
        }
      }
      nc++;
    }
    const visto = new Uint8Array(n); let abiertas = 0;
    for (let s0 = 0; s0 < n; s0++) {
      if (visto[s0] || wall[s0] !== 1 || F[s0] !== 0) continue;
      const grupo = [s0], zonas = new Set(); visto[s0] = 1; pila.push(s0);
      while (pila.length) {
        const c = pila.pop(), x = c % W;
        for (let k = 0; k < 4; k++) {
          if (k === 0 && x === W - 1) continue; if (k === 1 && x === 0) continue;
          const m = c + vec[k]; if (m < 0 || m >= n) continue;
          if (comp[m] >= 0) zonas.add(comp[m]);
          if (wall[m] === 1 && F[m] === 0 && !visto[m]) { visto[m] = 1; pila.push(m); grupo.push(m); }
        }
      }
      if (zonas.size >= 2) for (const c of grupo) { wall[c] = 0; if (g.cls[c] === 1) g.cls[c] = 0; abiertas++; }
    }
    K.pasosAbiertos = abiertas;
  };

  // ---------- 3) Ojo de oferta (Alan) ----------
  // Dura OJO.dur s; al terminar, las zonas reveladas vuelven a oscurecerse y arranca el enfriamiento de 30 s (los 30 s
  // los cuenta el evento de activación con el cronómetro "ojo"). Alcance: distancia al borde de la zona, no a su centro.
  K.OJO = { dur: 6, radio: 900, opac: 80, vuelta: 0.4 };
  K.ojo = function (scn) {
    const O = K.OJO;
    const dt = Math.min(0.1, scn.getTimeManager().getElapsedTime() / 1000);   // 0 en pausa
    const nie = scn.getObjects("Niebla") || [];
    const st = scn._f43ojo || (scn._f43ojo = { rest: new Set() });
    const vivas = new Set(nie);
    for (const s of (scn.getObjects("Sup") || [])) {
      const v = s.getVariables();
      if (v.get("Personaje").getAsString() !== "alan") continue;
      if (v.get("Ojo").getAsNumber() !== 1) { s.__f43o = null; continue; }
      const o = s.__f43o || (s.__f43o = { t: 0 });
      o.t += dt;
      if (o.t < O.dur && v.get("Estado").getAsString() === "normal") {
        const sx = s.getX(), sy = s.getY();
        for (const z of nie) {
          const zv = z.getVariables();
          if (zv.get("Abierta").getAsNumber() !== 0) continue;
          const dx = Math.max(z.getX() - sx, 0, sx - (z.getX() + z.getWidth()));
          const dy = Math.max(z.getY() - sy, 0, sy - (z.getY() + z.getHeight()));
          if (Math.hypot(dx, dy) < O.radio) { z.setOpacity(O.opac); zv.get("Vista").setNumber(1); st.rest.delete(z); }
        }
      } else {
        v.get("Ojo").setNumber(0);
        if (typeof s.resetTimer === "function") s.resetTimer("ojo");
        s.__f43o = null;
        for (const z of nie) { const zv = z.getVariables(); if (zv.get("Vista").getAsNumber() === 1) { zv.get("Vista").setNumber(0); if (zv.get("Abierta").getAsNumber() === 0) st.rest.add(z); } }
      }
    }
    for (const z of Array.from(st.rest)) {
      if (!vivas.has(z) || z.getVariables().get("Abierta").getAsNumber() === 1) { st.rest.delete(z); continue; }
      const op = z.getOpacity() + (255 - O.opac) / O.vuelta * Math.max(dt, 0.001);
      if (op >= 255) { z.setOpacity(255); st.rest.delete(z); } else z.setOpacity(op);
    }
  };

  // ---------- 2) desatasco de aliados ----------
  const CFG = {
    ventana: 0.5,     // s entre revisiones de avance
    minAvance: 7,     // px: menos que esto en una ventana con intención de moverse = sin avanzar
    disparo: 1.0,     // s sin avanzar para actuar
    lateral: 0.6,     // s que dura el paso lateral
    olvido: 9,        // s sin atorarse para reiniciar la escalera de remedios
    gracia: 0.8,      // s de calma tras un remedio
    saltoCorto: 120,  // px por la ruta
    saltoLargo: 260,
  };
  K.CFG = CFG;
  const DIRS = [];
  for (let k = 0; k < 8; k++) DIRS.push([Math.cos(k * Math.PI / 4), Math.sin(k * Math.PI / 4)]);

  function libre(g, C, x, y) {
    if (!g) return true;
    const cx = Math.floor(x / C), cy = Math.floor(y / C);
    if (cx < 0 || cy < 0 || cx >= g.W || cy >= g.H) return false;
    return g.cls[cy * g.W + cx] === 0;
  }
  K.libre = libre;

  // punto a `dist` px por la ruta; se detiene antes de cualquier puerta cerrada o muro
  K.puntoPorRuta = function (NAV, ax, ay, tx, ty, dist) {
    if (!NAV || !NAV.grid) return null;
    const r = NAV.path(ax, ay, tx, ty, 6000);
    if (!r || !r.found || r.pts.length < 2) return null;
    let acc = 0, px = r.pts[0][0], py = r.pts[0][1];
    for (let i = 1; i < r.pts.length; i++) {
      const q = r.pts[i];
      if (!NAV.los(px, py, q[0], q[1])) break; // ahí hay una puerta o un muro: no se salta
      const seg = Math.hypot(q[0] - px, q[1] - py);
      if (acc + seg >= dist) { const t = (dist - acc) / Math.max(1, seg); return [px + (q[0] - px) * t, py + (q[1] - py) * t]; }
      acc += seg; px = q[0]; py = q[1];
    }
    return acc > 24 ? [px, py] : null;
  };

  function humanosVivos(sups) {
    const h = [];
    for (const o of sups) {
      const v = o.getVariables();
      let ctl = v.get("Control").getAsNumber();
      if (ctl === -2 && v.has("CtlReal")) ctl = v.get("CtlReal").getAsNumber();
      if ((ctl >= 0 || ctl === -3) && v.get("Estado").getAsString() === "normal") h.push(o);
    }
    return h;
  }

  function reaparecerCerca(NAV, b, humanos) {
    if (!humanos.length) return false;
    let h = null, md = 1e9;
    for (const o of humanos) { const d = Math.hypot(o.getX() - b.getX(), o.getY() - b.getY()); if (d < md) { md = d; h = o; } }
    const C = NAV.cfg.C, g = NAV.grid;
    for (const rad of [130, 170, 90, 210]) {
      for (let k = 0; k < 8; k++) {
        const a = (k + Math.random()) * Math.PI / 4, x = h.getX() + Math.cos(a) * rad, y = h.getY() + Math.sin(a) * rad;
        if (libre(g, C, x, y) && NAV.los(h.getX(), h.getY(), x, y)) { b.setPosition(x, y); return true; }
      }
    }
    return false;
  }

  K.desatasco = function (scn) {
    const SV = scn.getVariables();
    if (SV.get("Pausa").getAsNumber() === 1 || SV.get("Estado").getAsString() !== "juego") return;
    const dt = Math.min(0.1, scn.getElapsedTime() / 1000);
    const NAV = gdjs.fdizNav, g = NAV && NAV.grid, C = NAV && NAV.cfg ? NAV.cfg.C : 16;
    const sups = scn.getObjects("Sup") || [];
    let humanos = null;
    for (const b of sups) {
      const v = b.getVariables();
      if (v.get("Control").getAsNumber() !== -1) continue;
      const bx = b.getX(), by = b.getY();
      const s = b.__f43 || (b.__f43 = { px: bx, py: by, win: 0, intent: 0, stuck: 0, rep: 0, repT: 0, lat: 0, dx: 0, dy: 0, gracia: 0 });
      const ocupado = v.get("Estado").getAsString() !== "normal" || v.get("Usando").getAsNumber() === 1 ||
        v.get("Atacando").getAsNumber() === 1 || (v.has("Curando") && v.get("Curando").getAsNumber() === 1) ||
        (v.has("Revivir") && v.get("Revivir").getAsNumber() > 0);
      if (ocupado) { s.px = bx; s.py = by; s.win = 0; s.intent = 0; s.stuck = 0; s.lat = 0; continue; }
      const mx = v.get("MovX").getAsNumber(), my = v.get("MovY").getAsNumber();
      const quiere = Math.abs(mx) + Math.abs(my) > 0.2;
      s.gracia = Math.max(0, s.gracia - dt);
      if (s.rep > 0) { s.repT -= dt; if (s.repT <= 0) s.rep = 0; }

      // paso lateral en curso: manda sobre el movimiento normal
      if (s.lat > 0) {
        s.lat -= dt;
        v.get("MovX").setNumber(s.dx); v.get("MovY").setNumber(s.dy);
      }
      s.win += dt;
      if (quiere || s.lat > 0) s.intent += dt;
      if (s.win < CFG.ventana) continue;

      const movido = Math.hypot(bx - s.px, by - s.py);
      if (s.intent >= CFG.ventana * 0.7 && movido < CFG.minAvance && s.gracia <= 0) s.stuck += s.win;
      else if (movido > 24) s.stuck = 0;
      else s.stuck = Math.max(0, s.stuck - s.win);
      s.px = bx; s.py = by; s.win = 0; s.intent = 0;
      if (s.stuck < CFG.disparo) continue;

      // ---- remedio ----
      s.stuck = 0; s.rep++; s.repT = CFG.olvido; s.gracia = CFG.gracia;
      const tx = v.get("BotX").getAsNumber(), ty = v.get("BotY").getAsNumber();
      try { const pb = b.getBehavior("PathBot"); if (pb) { pb._navForce = true; pb._navGoal = -1; } } catch (e) { /* sin behavior */ }
      if (s.rep >= 7) {
        if (!humanos) humanos = humanosVivos(sups);
        if (NAV && reaparecerCerca(NAV, b, humanos)) { s.rep = 0; s.gracia = 3; s.px = b.getX(); s.py = b.getY(); continue; }
      }
      if (s.rep >= 3 && NAV && g) {
        // salir de una celda bloqueada y saltar un trecho por la ruta
        if (g.cls[Math.max(0, Math.min(g.H - 1, Math.floor(by / C))) * g.W + Math.max(0, Math.min(g.W - 1, Math.floor(bx / C)))] === 1) {
          const f = NAV.nearestFree(bx, by, 8); if (f) b.setPosition(f[0], f[1]);
        }
        const p = K.puntoPorRuta(NAV, b.getX(), b.getY(), tx, ty, s.rep >= 5 ? CFG.saltoLargo : CFG.saltoCorto);
        if (p) {
          let q = libre(g, C, p[0], p[1]) ? p : NAV.nearestFree(p[0], p[1], 4);
          if (q && libre(g, C, q[0], q[1])) { b.setPosition(q[0], q[1]); s.px = q[0]; s.py = q[1]; continue; }
        }
      }
      // paso lateral: de las 8 direcciones libres, una que no vaya contra la meta
      const dl = Math.max(1, Math.hypot(tx - bx, ty - by)), ux = (tx - bx) / dl, uy = (ty - by) / dl;
      const cand = [];
      for (const d of DIRS) {
        const dot = d[0] * ux + d[1] * uy;
        if (dot < -0.35) continue;
        if (g && !(libre(g, C, bx + d[0] * 28, by + d[1] * 28) && libre(g, C, bx + d[0] * 56, by + d[1] * 56))) continue;
        cand.push(d);
      }
      const d = cand.length ? cand[Math.floor(Math.random() * cand.length)] : DIRS[Math.floor(Math.random() * 8)];
      s.dx = d[0]; s.dy = d[1]; s.lat = CFG.lateral;
    }
  };
})(typeof gdjs !== "undefined" ? gdjs : (globalThis.gdjs = globalThis.gdjs || {}));
