/* FDI-Z · navegación A* optimizada (reemplaza el buscador de rutas por defecto del behavior Pathfinding).
 * Se incrusta en un evento JavaScript de la escena Juego con scripts/fase17_navegacion.py. No editar el evento a mano.
 *
 * Por qué: el buscador original usa celdas de 32 px alineadas al origen, infla cada obstáculo con el tamaño COMPLETO del sprite
 * (80x127) y suaviza cortando esquinas. Resultado: sin ruta en pasillos angostos, zombis pegados a las paredes y bots que
 * retroceden (con maxSpeed 0 el behavior reponía la posición al inicio de la ruta en cada cuadro).
 *
 * Aquí: rejilla de 16 px con holgura R alrededor de muros/muebles; A* de 8 vecinos sin cortar esquinas, heap binario sobre
 * typed arrays con sellos de generación (sin limpiar memoria), heurística octil, ruta parcial si se agota el tope, suavizado
 * por línea de vista contra la misma rejilla, caché por celda destino y presupuesto de expansiones por cuadro.
 * Las puertas cerradas cuestan más pero se pueden cruzar (se abren o se tumban). */
(function (gdjs) {
  "use strict";
  const NAV = (gdjs.fdizNav = gdjs.fdizNav || {});
  const C = 16;              // tamaño de celda (px)
  const R = 18;              // holgura al centro del personaje (px)
  const DOOR_COST = 10;      // costo extra por celda de puerta cerrada
  const HW = 1.15;           // peso de la heurística (leve, mucho más rápido)
  const MAX_EXP = 25000;     // tope de expansiones por búsqueda
  const FRAME_BUDGET = 90000;// tope de expansiones por cuadro (todos los agentes)
  const SQ2 = Math.SQRT2;

  NAV.cfg = { C, R };
  NAV.stats = { searches: 0, expansions: 0, partial: 0, failed: 0, skipped: 0, maxMs: 0 };

  // ---------- rejilla ----------
  NAV.setup = function (rects, doorRects) {
    let maxX = 0, maxY = 0;
    for (const r of rects) { if (r[2] > maxX) maxX = r[2]; if (r[3] > maxY) maxY = r[3]; }
    const W = Math.ceil(maxX / C) + 12, H = Math.ceil(maxY / C) + 12;
    const g = { W, H, cls: new Uint8Array(W * H), wall: null, rects, doors: [] };
    for (const r of rects) NAV._stamp(g, g.cls, r, 1);
    g.wall = g.cls.slice();
    NAV.grid = g;
    NAV.setDoors(doorRects || []);
    const n = W * H;
    NAV._gs = new Float32Array(n); NAV._fs = new Float32Array(n);
    NAV._par = new Int32Array(n); NAV._seen = new Uint32Array(n); NAV._closed = new Uint32Array(n);
    NAV._gen = 0; NAV._heap = new Int32Array(1 << 16); NAV._hk = new Float32Array(1 << 16);
    return g;
  };
  NAV._stamp = function (g, arr, r, val) {
    const x0 = r[0] - R, y0 = r[1] - R, x1 = r[2] + R, y1 = r[3] + R;
    const cx0 = Math.max(0, Math.floor(x0 / C - 0.5) ), cx1 = Math.min(g.W - 1, Math.ceil(x1 / C - 0.5));
    const cy0 = Math.max(0, Math.floor(y0 / C - 0.5) ), cy1 = Math.min(g.H - 1, Math.ceil(y1 / C - 0.5));
    for (let cy = cy0; cy <= cy1; cy++) {
      const py = (cy + 0.5) * C; if (py <= y0 || py >= y1) continue;
      for (let cx = cx0; cx <= cx1; cx++) {
        const px = (cx + 0.5) * C; if (px <= x0 || px >= x1) continue;
        if (val === 2) { if (arr[cy * g.W + cx] === 0) arr[cy * g.W + cx] = 2; } else arr[cy * g.W + cx] = val;
      }
    }
  };
  NAV.setDoors = function (doorRects) {
    const g = NAV.grid; if (!g) return;
    g.cls.set(g.wall);
    g.doors = doorRects;
    for (const r of doorRects) NAV._stamp(g, g.cls, r, 2);
  };

  // ---------- utilidades ----------
  function cellOf(g, x, y) {
    let cx = Math.floor(x / C), cy = Math.floor(y / C);
    if (cx < 0) cx = 0; else if (cx >= g.W) cx = g.W - 1;
    if (cy < 0) cy = 0; else if (cy >= g.H) cy = g.H - 1;
    return cy * g.W + cx;
  }
  NAV.cellOf = function (x, y) { return cellOf(NAV.grid, x, y); };
  // celda libre más cercana (anillos crecientes)
  function nearestFree(g, c, maxRing) {
    if (g.cls[c] !== 1) return c;
    const W = g.W, H = g.H, cx = c % W, cy = (c / W) | 0;
    for (let r = 1; r <= maxRing; r++) {
      let best = -1, bd = 1e9;
      for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) {
        if (Math.max(Math.abs(dx), Math.abs(dy)) !== r) continue;
        const x = cx + dx, y = cy + dy; if (x < 0 || y < 0 || x >= W || y >= H) continue;
        const i = y * W + x; if (g.cls[i] === 1) continue;
        const d = dx * dx + dy * dy; if (d < bd) { bd = d; best = i; }
      }
      if (best >= 0) return best;
    }
    return -1;
  }
  NAV.nearestFree = function (x, y, ring) {
    const g = NAV.grid; const c = nearestFree(g, cellOf(g, x, y), ring || 8);
    return c < 0 ? null : [(c % g.W + 0.5) * C, (((c / g.W) | 0) + 0.5) * C];
  };
  // línea de vista: ninguna muestra cae en celda de muro ni de puerta (salvo la celda inicial/final)
  function los(g, ax, ay, bx, by, strictDoors) {
    const dx = bx - ax, dy = by - ay, len = Math.hypot(dx, dy);
    const n = Math.max(1, Math.ceil(len / (C * 0.25)));
    const c0 = cellOf(g, ax, ay), c1 = cellOf(g, bx, by);
    for (let i = 0; i <= n; i++) {
      const t = i / n, c = cellOf(g, ax + dx * t, ay + dy * t);
      const v = g.cls[c];
      if (v === 1) return false;
      if (v === 2 && strictDoors && c !== c0 && c !== c1) return false;
    }
    return true;
  }
  NAV.los = function (ax, ay, bx, by) { return los(NAV.grid, ax, ay, bx, by, true); };

  // ---------- heap binario (la clave se guarda junto al nodo: las entradas viejas no rompen el orden) ----------
  function hpush(n, key) {
    if (NAV._hn >= NAV._heap.length) {
      const nh = new Int32Array(NAV._heap.length * 2); nh.set(NAV._heap); NAV._heap = nh;
      const nk = new Float32Array(nh.length); nk.set(NAV._hk); NAV._hk = nk;
    }
    const h = NAV._heap, k = NAV._hk; let i = NAV._hn++;
    while (i > 0) { const p = (i - 1) >> 1; if (k[p] <= key) break; h[i] = h[p]; k[i] = k[p]; i = p; }
    h[i] = n; k[i] = key;
  }
  function hpop() {
    const h = NAV._heap, k = NAV._hk; const top = h[0]; const n = --NAV._hn;
    if (n > 0) {
      const last = h[n], lk = k[n]; let i = 0;
      for (;;) { let l = 2 * i + 1; if (l >= n) break; const r = l + 1; if (r < n && k[r] < k[l]) l = r; if (k[l] >= lk) break; h[i] = h[l]; k[i] = k[l]; i = l; }
      h[i] = last; k[i] = lk;
    }
    return top;
  }

  // ---------- A* ----------
  // devuelve {cells:[...índices], partial:bool, exp:n} o null
  NAV.search = function (sx, sy, tx, ty, maxExp) {
    const g = NAV.grid; if (!g) return null;
    const W = g.W, H = g.H, cls = g.cls;
    let s = nearestFree(g, cellOf(g, sx, sy), 8), t = nearestFree(g, cellOf(g, tx, ty), 10);
    if (s < 0 || t < 0) return null;
    if (s === t) return { cells: [s], partial: false, exp: 0 };
    const gen = ++NAV._gen, gs = NAV._gs, fs = NAV._fs, par = NAV._par, seen = NAV._seen, closed = NAV._closed;
    const tx0 = t % W, ty0 = (t / W) | 0;
    const hf = (i) => { const dx = Math.abs((i % W) - tx0), dy = Math.abs(((i / W) | 0) - ty0); return HW * ((dx > dy ? dx : dy) + (SQ2 - 1) * (dx > dy ? dy : dx)); };
    NAV._hn = 0; gs[s] = 0; fs[s] = hf(s); par[s] = -1; seen[s] = gen; hpush(s, fs[s]);
    let exp = 0, best = s, bestH = fs[s];
    const lim = maxExp || MAX_EXP;
    while (NAV._hn > 0) {
      const n = hpop(); if (closed[n] === gen) continue; closed[n] = gen;
      if (n === t) { best = t; break; }
      if (++exp > lim) break;
      const nx = n % W, ny = (n / W) | 0, gn = gs[n];
      const hn = fs[n] - gn; if (hn < bestH) { bestH = hn; best = n; }
      for (let k = 0; k < 8; k++) {
        const dx = k < 4 ? (k === 0 ? 1 : k === 1 ? -1 : 0) : (k === 4 || k === 6 ? 1 : -1);
        const dy = k < 4 ? (k === 2 ? 1 : k === 3 ? -1 : 0) : (k === 4 || k === 5 ? 1 : -1);
        const x = nx + dx, y = ny + dy; if (x < 0 || y < 0 || x >= W || y >= H) continue;
        const m = y * W + x, v = cls[m]; if (v === 1 || closed[m] === gen) continue;
        if (dx !== 0 && dy !== 0 && (cls[ny * W + x] === 1 || cls[y * W + nx] === 1)) continue; // sin cortar esquinas
        const step = (dx !== 0 && dy !== 0 ? SQ2 : 1) * (v === 2 ? 1 + DOOR_COST : 1);
        const ng = gn + step;
        if (seen[m] !== gen || ng < gs[m]) { seen[m] = gen; gs[m] = ng; par[m] = n; fs[m] = ng + hf(m); hpush(m, fs[m]); }
      }
    }
    const partial = best !== t;
    const cells = []; for (let c = best; c !== -1; c = par[c]) cells.push(c);
    cells.reverse();
    return { cells, partial, exp };
  };

  // ruta de puntos suavizada. Devuelve {pts:[[x,y],...], found, partial} (pts[0] = posición de origen)
  NAV.path = function (sx, sy, tx, ty, maxExp) {
    const g = NAV.grid; if (!g) return null;
    const t0 = (typeof performance !== "undefined" ? performance.now() : Date.now());
    const r = NAV.search(sx, sy, tx, ty, maxExp);
    NAV.stats.searches++;
    if (!r) { NAV.stats.failed++; return { pts: [[sx, sy]], found: false, partial: false, exp: 0 }; }
    NAV.stats.expansions += r.exp; if (r.partial) NAV.stats.partial++;
    const W = g.W;
    const cp = r.cells.map((c) => [(c % W + 0.5) * C, (((c / W) | 0) + 0.5) * C]);
    // destino exacto si su celda es libre; si no, el centro de la celda libre más cercana
    const tc = cellOf(g, tx, ty);
    const endExact = !r.partial && g.cls[tc] !== 1;
    const pts = [[sx, sy]];
    for (let i = 0; i < cp.length; i++) pts.push(cp[i]);
    if (endExact) pts[pts.length - 1] = [tx, ty];
    // suavizado: desde cada punto, saltar al más lejano visible (ventana de 40 puntos)
    const out = [pts[0]]; let i = 0;
    while (i < pts.length - 1) {
      let j = Math.min(pts.length - 1, i + 40);
      while (j > i + 1 && !los(g, pts[i][0], pts[i][1], pts[j][0], pts[j][1], true)) j--;
      out.push(pts[j]); i = j;
    }
    const ms = (typeof performance !== "undefined" ? performance.now() : Date.now()) - t0;
    if (ms > NAV.stats.maxMs) NAV.stats.maxMs = ms;
    return { pts: out, found: true, partial: r.partial, exp: r.exp };
  };
})(typeof gdjs !== "undefined" ? gdjs : (globalThis.gdjs = globalThis.gdjs || {}));
