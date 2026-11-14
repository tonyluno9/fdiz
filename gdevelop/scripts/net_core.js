/* FDI-Z · Fase 25 · Módulo de red (online por internet con PeerJS).
 * Se incrusta con scripts/fase25_online.py en la escena Titulo (junto a peerjs.min.js). Define gdjs.fdizNet.
 * Topología: estrella. El host (en modo Jefe: el Jefe) corre TODO el juego y es la autoridad.
 * Los clientes mandan solo su entrada (30 Hz) y reciben instantáneas del estado (30 Hz, solo cambios).
 * Un jugador remoto es un "mando virtual": el host escribe sus MovX/MovY/Aim/Pegar... como si fuera un control (Control = -3).
 * gdjs.fdizNetCfg (inyectado) trae: objs [{n, v:[[nombre,'n'|'s']], t}], sv [variables de escena a sincronizar]. */
(function () {
  "use strict";
  const G = gdjs;
  if (G.fdizNet && G.fdizNet.ver === 6) return;
  const CFG = G.fdizNetCfg || { objs: [], sv: [] };
  const N = (G.fdizNet = { ver: 6, role: 0, myId: "", peer: null, conns: {}, conn: null, code: "", scn: null, cfg: CFG,
    L: null, slots: [], inp: {}, err: "", ui: { st: "menu", code: "", msg: "", sel: 0 }, pend: null, started: false, pm: {}, seen: new Set(), nid: 0 });

  const PJ = ["tony", "miranda", "cesar", "alan", "castillo", "alessandro", "gabo", "carlos"];
  const PJN = ["Tony", "Miranda", "César", "Alan", "Castillo", "Alessandro", "Gabo", "Carlos"];
  const PJD = ["Cocinar / Modo gym", "Arrullo / Minigun", "Hackeo / Control de la escuela", "Gorrear / Reembolso", "Tragar / App de salud", "Chiste / Reloj", "Supervelocidad / Ecosistema", "Llave maestra / Tanque"];
  const DIFS = { facil: [0.7, 0.75, 0.7, 0.75], normal: [1, 1, 1, 1], pesadilla: [1.45, 1.3, 1.3, 1.35] };
  const ALF = "ABCDEFGHJKMNPQRSTUVWXYZ23456789";
  const rnd = (v) => Math.round(v * 10) / 10;
  const r3 = (v) => Math.round(v * 1000) / 1000;
  const PeerC = () => (window.peerjs && window.peerjs.Peer) || window.Peer;
  const GV = (scn) => scn.getGame().getVariables();
  const REPLACE = () => (G.SceneChangeRequest ? G.SceneChangeRequest.REPLACE_SCENE : (G.RuntimeScene && G.RuntimeScene.REPLACE_SCENE !== undefined ? G.RuntimeScene.REPLACE_SCENE : 3));
  const syncRol = (scn) => { try { GV(scn).get("NetRol").setNumber(N.role); } catch (e) {} };
  N.syncRol = syncRol;
  const go = (scn, name) => { try { scn.requestChange(REPLACE(), name); } catch (e) { console.warn("[net] cambio de escena", e); } };

  // ---------------------------------------------------------------- red básica
  const send = (c, o) => { try { if (c && c.open) c.send(o); } catch (e) {} };
  const bcast = (o) => { for (const id in N.conns) send(N.conns[id], o); };
  N.shutdown = function () {
    try { for (const id in N.conns) N.conns[id].close(); if (N.conn) N.conn.close(); if (N.peer) N.peer.destroy(); } catch (e) {}
    N.role = 0; N.peer = null; N.conns = {}; N.conn = null; N.L = null; N.slots = []; N.inp = {}; N.started = false; N.pm = {}; N.seen = new Set(); N.code = "";
    N.ui.st = "menu"; N.ui.msg = ""; if (N.scn) syncRol(N.scn);
  };


  // ---------------------------------------------------------------- sonidos: lo que suena en el host suena en todas las máquinas
  (function () {
    const S = G.evtTools && G.evtTools.sound; if (!S || !S.playSound || S._fdizWrapped) return;
    const orig = S.playSound; S._fdizWrapped = true; S._orig = orig;
    S.playSound = function (...a) {
      if (N.role === 2 && !N._replay) return;           // el cliente solo oye lo que manda el host
      if (N.role === 1 && N.started) bcast({ t: "snd", a: a.slice(1) });
      return orig.apply(this, a);
    };
    N.playRemote = function (args) {
      if (!N.scn) return; try { if (GV(N.scn).get("SonidoActivo").getAsNumber() !== 1) return; } catch (e) {}
      N._replay = true; try { orig.apply(S, [N.scn].concat(args)); } catch (e) {} N._replay = false;
    };
  })();

  // ---------------------------------------------------------------- lobby (autoridad: host)
  const totalPlayers = (L) => L.m.reduce((s, m) => s + m.players.length, 0);
  const takenPj = (L, except) => { const t = new Set(); L.m.forEach((m) => m.players.forEach((p) => { if (p !== except && p.pj >= 0) t.add(p.pj); })); return t; };
  const freePj = (L) => { const t = takenPj(L); for (let i = 0; i < 8; i++) if (!t.has(i)) return i; return -1; };
  const lobbyOut = () => ({ t: "lobby", L: N.L });
  function setPlayers(id, players) {
    const m = N.L.m.find((x) => x.id === id); if (!m) return;
    const out = []; let kb = false;
    for (const p of players || []) {
      if (!p || typeof p.ctl !== "number" || p.ctl < 0 || p.ctl > 4) continue;
      if (p.ctl === 0) { if (kb) continue; kb = true; }
      if (out.some((q) => q.ctl === p.ctl)) continue;
      out.push({ ctl: p.ctl | 0, pj: Math.max(-1, Math.min(7, p.pj | 0)), ok: !!p.ok });
    }
    if (N.L.mode === "jefe" && id === "host") out.length = 0;
    const others = totalPlayers(N.L) - m.players.length;
    while (others + out.length > 4) out.pop();
    m.players = out;
    // personajes únicos: si choca con otro jugador, se quita y se des-confirma
    const seen = new Set(); N.L.m.forEach((mm) => { if (mm !== m) mm.players.forEach((p) => { if (p.pj >= 0) seen.add(p.pj); }); });
    out.forEach((p) => { if (p.pj >= 0 && seen.has(p.pj)) { p.pj = -1; p.ok = false; } if (p.pj >= 0) seen.add(p.pj); });
    out.forEach((p) => { if (p.pj < 0) { for (let i = 0; i < 8; i++) if (!seen.has(i)) { p.pj = i; seen.add(i); break; } } });
  }
  function pushLobby() { if (N.role === 1) bcast(lobbyOut()); }

  // ---------------------------------------------------------------- crear / unirse
  N.host = function () {
    N.shutdown(); N.role = 1; N.ui.st = "connecting"; N.ui.msg = "Creando sala…";
    const mk = () => {
      let code = ""; for (let i = 0; i < 5; i++) code += ALF[Math.floor(Math.random() * ALF.length)];
      const P = PeerC(); if (!P) { N.ui.st = "error"; N.ui.msg = "No se cargó la librería de red."; return; }
      const peer = new P("fdiz-" + code, { debug: 1 });
      N.peer = peer;
      peer.on("open", () => { N.code = code; N.myId = "host"; N.L = { m: [{ id: "host", name: "Host (tú)", players: [] }], mode: "escape", dif: "normal" }; N.ui.st = "lobby"; N.ui.msg = ""; });
      peer.on("error", (e) => { if (e && e.type === "unavailable-id") { try { peer.destroy(); } catch (x) {} mk(); } else { N.ui.st = "error"; N.ui.msg = "Error de red: " + (e && e.type ? e.type : e); } });
      peer.on("disconnected", () => { try { peer.reconnect(); } catch (e) {} });
      peer.on("connection", (c) => {
        c.on("open", () => {
          if (N.started || N.L.m.length >= 5) { send(c, { t: "bye", why: N.started ? "La partida ya empezó." : "Sala llena." }); setTimeout(() => { try { c.close(); } catch (e) {} }, 300); return; }
          N.conns[c.peer] = c; N.L.m.push({ id: c.peer, name: "PC " + (N.L.m.length + 1), players: [] });
          send(c, { t: "hi", me: c.peer }); pushLobby();
        });
        c.on("data", (d) => onHostData(c, d));
        c.on("close", () => onClientGone(c.peer));
        c.on("error", () => onClientGone(c.peer));
      });
    };
    mk();
  };
  N.join = function (code) {
    N.shutdown(); N.role = 2; N.ui.st = "connecting"; N.ui.msg = "Conectando…";
    const P = PeerC(); if (!P) { N.ui.st = "error"; N.ui.msg = "No se cargó la librería de red."; return; }
    const peer = new P({ debug: 1 }); N.peer = peer;
    let to = setTimeout(() => { if (N.ui.st === "connecting") { N.ui.st = "error"; N.ui.msg = "No se pudo conectar (¿código correcto? ¿internet?)."; } }, 15000);
    peer.on("error", (e) => { clearTimeout(to); N.ui.st = "error"; N.ui.msg = e && e.type === "peer-unavailable" ? "No existe esa sala." : "Error de red: " + (e && e.type ? e.type : e); });
    peer.on("open", (id) => {
      N.myId = id;
      const c = peer.connect("fdiz-" + code.toUpperCase(), { reliable: true, serialization: "json" }); N.conn = c;
      c.on("open", () => { clearTimeout(to); N.code = code.toUpperCase(); });
      c.on("data", (d) => onClientData(d));
      c.on("close", () => { if (N.role === 2) { N.err = "Se perdió la conexión con el host."; N.shutdown(); N.ui.st = "error"; N.ui.msg = N.err; if (N.scn && N.started) go(N.scn, "Menu"); } });
    });
  };
  function onClientGone(id) {
    if (!N.conns[id]) return;
    delete N.conns[id];
    if (N.L) { N.L.m = N.L.m.filter((m) => m.id !== id); if (!N.started) pushLobby(); }
    if (N.started && N.scn) { // sus personajes pasan a ser bots
      N.slots.forEach((s, i) => { if (s.owner === id) { s.owner = "bot"; N.setBot = N.setBot || []; N.setBot.push(i); } });
    }
    delete N.inp[id];
  }
  function onHostData(c, d) {
    if (!d || !d.t) return;
    if (d.t === "claim" && !N.started) { setPlayers(c.peer, d.players); pushLobby(); }
    else if (d.t === "in") { N.inp[c.peer] = { at: performance.now(), p: d.p || [], cam: d.cam || null }; }
  }
  function onClientData(d) {
    if (!d || !d.t) return;
    if (d.t === "hi") { N.myId = d.me; N.ui.st = "lobby"; N.ui.msg = ""; }
    else if (d.t === "lobby") N.L = d.L;
    else if (d.t === "bye") { N.ui.st = "error"; N.ui.msg = d.why || "Desconectado."; N.shutdown(); N.ui.st = "error"; N.ui.msg = d.why || "Desconectado."; }
    else if (d.t === "start") N.pend = { go: "Juego", start: d };
    else if (d.t === "scene") N.pend = { go: d.name, g: d.g };
    else if (d.t === "snd") { if (N.started && N.playRemote) N.playRemote(d.a || []); }
    else if (d.t === "snap") { N.snapQ = N.snapQ || []; N.snapQ.push(d); }
  }

  // ---------------------------------------------------------------- arranque de partida
  function applyGlobals(scn, modo, dif, slots, me) {
    const g = GV(scn);
    g.get("Modo").setString(modo); g.get("Dificultad").setString(dif);
    const k = DIFS[dif] || DIFS.normal; g.get("DifInf").setNumber(k[0]); g.get("DifVida").setNumber(k[1]); g.get("DifDanio").setNumber(k[2]); g.get("DifHorda").setNumber(k[3]);
    slots.forEach((s, i) => {
      g.get("P" + (i + 1) + "Pj").setString(PJ[s.pj] || "tony");
      let ctl; if (s.owner === "bot") ctl = -1; else if (s.owner === me) ctl = s.ctl; else ctl = N.role === 1 ? -3 : -4;
      g.get("P" + (i + 1) + "Ctl").setNumber(ctl);
    });
    g.get("Listo").setNumber(1); g.get("SinRecord").setNumber(0); g.get("Demo").setNumber(0);
  }
  N.canStart = function () {
    const L = N.L; if (!L) return false;
    const all = L.m.reduce((a, m) => a.concat(m.players), []);
    if (all.some((p) => !p.ok)) return false;
    if (L.mode === "jefe") return all.length >= 1;
    return all.length >= 1;
  };
  N.startGame = function (scn) {
    const L = N.L; if (!N.canStart()) return;
    const slots = []; const used = new Set();
    L.m.forEach((m) => m.players.forEach((p) => { slots.push({ pj: p.pj, owner: m.id, ctl: p.ctl }); used.add(p.pj); }));
    for (let i = 0; i < 8 && slots.length < 4; i++) if (!used.has(i)) { slots.push({ pj: i, owner: "bot", ctl: -1 }); used.add(i); }
    N.slots = slots.slice(0, 4);
    const msg = { t: "start", modo: L.mode, dif: L.dif, slots: N.slots };
    for (const id in N.conns) send(N.conns[id], Object.assign({ me: id }, msg));
    applyGlobals(scn, L.mode, L.dif, N.slots, "host");
    N.started = true; N.modo = L.mode; go(scn, "Juego");
  };

  // ---------------------------------------------------------------- entrada local
  const im = (scn) => scn.getGame().getInputManager();
  const gp = (k) => { try { const a = navigator.getGamepads ? navigator.getGamepads() : []; return a[k] || null; } catch (e) { return null; } };
  const dz = (v) => (Math.abs(v) < 0.18 ? 0 : v);
  function readLocal(scn, ctl, slot) {
    const I = im(scn); const o = { s: slot, mx: 0, my: 0, ax: 0, ay: 0, aim: 0, hit: 0, use: 0, hab: 0, esp: 0, lz: 0, dr: 0, sp: 0 };
    if (ctl === 0) {
      if (I.isKeyPressed(65)) o.mx -= 1; if (I.isKeyPressed(68)) o.mx += 1; if (I.isKeyPressed(87)) o.my -= 1; if (I.isKeyPressed(83)) o.my += 1;
      const sup = slotSup(scn, slot);
      if (sup) { const p = scn.getLayer("").convertCoords(I.getMouseX(), I.getMouseY(), 0); o.ax = p[0] - sup.getX(); o.ay = p[1] - (sup.getY() - 40); o.aim = 1; }
      o.hit = I.isMouseButtonPressed(0) ? 1 : 0; o.use = I.isKeyPressed(70) ? 1 : 0; o.hab = I.isKeyPressed(81) ? 1 : 0; o.esp = I.isKeyPressed(69) ? 1 : 0;
      o.lz = (I.isKeyPressed(82) || I.isMouseButtonPressed(1)) ? 1 : 0; o.dr = I.isKeyPressed(82) ? 1 : 0; o.sp = I.isKeyPressed(16) ? 1 : 0;
    } else {
      const g = gp(ctl - 1); if (g) {
        const b = (i) => (g.buttons[i] && g.buttons[i].pressed ? 1 : 0);
        o.mx = dz(g.axes[0] || 0); o.my = dz(g.axes[1] || 0);
        const rx = g.axes[2] || 0, ry = g.axes[3] || 0;
        if (Math.abs(rx) + Math.abs(ry) > 0.3) { o.ax = rx; o.ay = ry; o.aim = 1; } else if (Math.abs(o.mx) + Math.abs(o.my) > 0.3) { o.ax = o.mx; o.ay = o.my; o.aim = 1; }
        o.hit = b(2); o.use = b(0); o.hab = b(3); o.esp = b(5); o.lz = b(1);
      }
    }
    return o;
  }
  function slotSup(scn, slot) {
    const a = scn.getObjects("Sup"); for (let i = 0; i < a.length; i++) if (a[i].getVariables().get("Jugador").getAsNumber() === slot + 1) return a[i]; return null;
  }

  // ---------------------------------------------------------------- ids de red
  function initIds(scn) {
    if (scn._netIds) return; scn._netIds = true; N.nid = 0; N.pm = {}; N.seen = new Set(); N.last = new Map(); N.tickN = 0; N.snapQ = [];
    CFG.objs.forEach((s) => { const a = scn.getObjects(s.n); if (a) for (let i = 0; i < a.length; i++) { a[i]._nid = ++N.nid; N.pm[a[i]._nid] = a[i]; } });
  }
  const VAL = (v, t) => (t === "s" ? v.getAsString() : r3(v.getAsNumber()));
  function enc(o, spec, idx) {
    const r = [o._nid, idx, rnd(o.getX()), rnd(o.getY()), rnd(o.getAngle()), o.getAnimationName ? o.getAnimationName() : "", o.isHidden() ? 1 : 0,
      o.getOpacity ? Math.round(o.getOpacity()) : 255, rnd(o.getWidth()), rnd(o.getHeight()), o.isFlippedX && o.isFlippedX() ? 1 : 0, o.getZOrder(), o.getLayer(), spec.t ? o.getText() : ""];
    const vs = o.getVariables(); for (let i = 0; i < spec.v.length; i++) r.push(VAL(vs.get(spec.v[i][0]), spec.v[i][1]));
    return r;
  }

  // ---------------------------------------------------------------- JUEGO: inicio de cada cuadro
  N.begin = function (scn) {
    N.scn = scn; syncRol(scn);
    if (N.role === 0) return;
    initIds(scn);
    if (N.pend && N.pend.go) { const p = N.pend; N.pend = null; if (p.g) { const g = GV(scn); for (const k in p.g) { const v = g.get(k); if (typeof p.g[k] === "string") v.setString(p.g[k]); else v.setNumber(p.g[k]); } } if (p.start) { N.slots = p.start.slots; N.started = true; applyGlobals(scn, p.start.modo, p.start.dif, p.start.slots, p.start.me); } go(scn, p.go); return; }
    if (N.role === 1) { if (N.setBot) { N.setBot.forEach((i) => { const s = slotSup(scn, i); if (s) s.getVariables().get("Control").setNumber(-1); }); N.setBot = null; } return; }
    // cliente: Control local de cada Sup
    if (!scn._netCtl) { scn._netCtl = true; const g = GV(scn); for (let i = 0; i < 4; i++) { const s = slotSup(scn, i); if (s) s.getVariables().get("Control").setNumber(g.get("P" + (i + 1) + "Ctl").getAsNumber()); } GV(scn).get("Modo").setString("escape");
      ["Mapa","Muro","ChoqueMueble","Marcador","Minimapa","TxtJefe","OscuridadIni","BtnOmitir","TxtOmitir","PausaVelo","PausaPanel","PausaBtn","TxtPausaTit","TxtPausaB0","TxtPausaB1","TxtPausaB2","TxtDebug"].forEach((n) => { const a = scn.getObjects(n); if (a) for (let i = 0; i < a.length; i++) a[i].hide(true); }); }
    // aplicar instantáneas recibidas
    const Q = N.snapQ || []; N.snapQ = [];
    for (const d of Q) applySnap(scn, d);
    // suavizado
    for (const id in N.pm) { const o = N.pm[id]; if (o._tx !== undefined) { const dx = o._tx - o.getX(), dy = o._ty - o.getY(); if (Math.abs(dx) + Math.abs(dy) > 220) o.setPosition(o._tx, o._ty); else if (dx || dy) o.setPosition(o.getX() + dx * 0.55, o.getY() + dy * 0.55); } }
    // salir con Esc
    if (im(scn).wasKeyReleased(27)) { N.shutdown(); go(scn, "Menu"); }
  };

  function applySnap(scn, d) {
    if (d.d) for (const id of d.d) { const o = N.pm[id]; if (o) { try { o.deleteFromScene(scn); } catch (e) {} delete N.pm[id]; } }
    if (d.o) for (const r of d.o) {
      let o = N.pm[r[0]]; const spec = CFG.objs[r[1]]; if (!spec) continue;
      if (!o) { o = scn.createObject(spec.n); if (!o) continue; o._nid = r[0]; N.pm[r[0]] = o; o.setLayer(r[12]); o._tx = undefined; }
      if (o._tx === undefined) o.setPosition(r[2], r[3]);
      o._tx = r[2]; o._ty = r[3]; o.setAngle(r[4]);
      if (r[5] && o.getAnimationName && o.getAnimationName() !== r[5]) o.setAnimationName(r[5]);
      o.hide(!!r[6]); if (o.setOpacity) o.setOpacity(r[7]);
      if (!spec.t) { if (Math.abs(o.getWidth() - r[8]) > 1) o.setWidth(r[8]); if (Math.abs(o.getHeight() - r[9]) > 1) o.setHeight(r[9]); }
      if (o.flipX) o.flipX(!!r[10]); o.setZOrder(r[11]); if (o.getLayer() !== r[12]) o.setLayer(r[12]);
      if (spec.t && o.setText) o.setText(r[13]);
      const vs = o.getVariables(); const skip = spec.n === "Sup" ? "Control" : null;
      for (let i = 0; i < spec.v.length; i++) { if (spec.v[i][0] === skip) continue; const v = vs.get(spec.v[i][0]); if (spec.v[i][1] === "s") v.setString(r[14 + i]); else v.setNumber(r[14 + i]); }
    }
    if (d.v) { const V = scn.getVariables(); for (const k in d.v) { const v = V.get(k); if (typeof d.v[k] === "string") v.setString(d.v[k]); else v.setNumber(d.v[k]); } }
  }

  // ---------------------------------------------------------------- JUEGO host: entrada remota (después del grupo Entrada)
  N.inputs = function (scn) {
    if (N.role !== 1 || !N.started) return;
    const now = performance.now();
    N.slots.forEach((s, i) => {
      if (s.owner === "bot" || s.owner === "host") return;
      const sup = slotSup(scn, i); if (!sup) return;
      const V = sup.getVariables(); const bag = N.inp[s.owner];
      const p = bag && now - bag.at < 700 ? bag.p.find((q) => q.s === i) : null;
      if (!p) { V.get("MovX").setNumber(0); V.get("MovY").setNumber(0); return; }
      V.get("MovX").setNumber(p.mx); V.get("MovY").setNumber(p.my);
      if (p.aim) { V.get("AimX").setNumber(p.ax); V.get("AimY").setNumber(p.ay); }
      if (p.hit) V.get("QuierePegar").setNumber(1); if (p.use) V.get("Usando").setNumber(1);
      if (p.hab) V.get("PideHab").setNumber(1); if (p.esp) V.get("PideEsp").setNumber(1);
      if (p.lz) V.get("QuiereLanzar").setNumber(1);
      V.get("NetSp").setNumber(p.sp ? 1 : 0); V.get("NetDr").setNumber(p.dr ? 1 : 0);
      // la máquina con 2+ jugadores humanos comparte pantalla: no pueden salir de lo que ve esa máquina
      const loc = N.slots.filter((q) => q.owner === s.owner).length;
      if (loc >= 2 && bag.cam) { const c = bag.cam, m = 50; const x = Math.max(c[0] + m, Math.min(c[2] - m, sup.getX())), y = Math.max(c[1] + m, Math.min(c[3] - m, sup.getY())); if (x !== sup.getX() || y !== sup.getY()) sup.setPosition(x, y); }
    });
  };

  // ---------------------------------------------------------------- JUEGO: fin de cada cuadro
  N.end = function (scn) {
    if (N.role === 0 || !N.started) return;
    N.tickN = (N.tickN || 0) + 1;
    if (N.role === 2) {
      if (N.tickN % 2) return;
      const p = []; N.slots.forEach((s, i) => { if (s.owner === N.myId) p.push(readLocal(scn, s.ctl, i)); });
      const L = scn.getLayer(""); const z = L.getCameraZoom() || 1, cx = L.getCameraX(0), cy = L.getCameraY(0);
      send(N.conn, { t: "in", p, cam: [cx - 960 / z, cy - 540 / z, cx + 960 / z, cy + 540 / z] });
      return;
    }
    // host: instantánea
    if (N.tickN % 2) return;
    const full = N.tickN % 90 === 0; const out = [], present = new Set();
    CFG.objs.forEach((spec, idx) => {
      const a = scn.getObjects(spec.n); if (!a) return;
      for (let i = 0; i < a.length; i++) {
        const o = a[i]; if (o._nid === undefined) { o._nid = ++N.nid; }
        present.add(o._nid);
        const r = enc(o, spec, idx); const key = JSON.stringify(r);
        if (full || N.last.get(o._nid) !== key) { N.last.set(o._nid, key); out.push(r); }
      }
    });
    const del = []; N.seen.forEach((id) => { if (!present.has(id)) { del.push(id); N.last.delete(id); } }); N.seen = present;
    const V = scn.getVariables(); const sv = {};
    CFG.sv.forEach((n) => { const v = V.get(n); const x = v.getType() === "string" ? v.getAsString() : r3(v.getAsNumber()); if (N.lastSv[n] !== x) { N.lastSv[n] = x; sv[n] = x; } });
    if (full) { for (const k in N.lastSv) sv[k] = N.lastSv[k]; }
    if (out.length || del.length || Object.keys(sv).length) bcast({ t: "snap", o: out, d: del, v: sv });
  };
  N.lastSv = {};

  // ---------------------------------------------------------------- Resultados: el host manda a todos a la misma escena
  N.sceneEnter = function (scn, name) {
    N.scn = scn;
    if (N.role === 1 && !scn._netSent) {
      scn._netSent = true; const g = GV(scn);
      const o = {}; ["Resultado", "TiempoFinal", "Premios", "MejorTiempo", "SinRecord", "Modo"].forEach((k) => { const v = g.get(k); o[k] = v.getType() === "string" ? v.getAsString() : v.getAsNumber(); });
      bcast({ t: "scene", name, g: o }); N.started = false; N.lastSv = {}; N.last = new Map();
    }
    if (N.role === 2) { if (N.pend && N.pend.go) { const p = N.pend; N.pend = null; go(scn, p.go); } N.started = false; }
  };

  // ---------------------------------------------------------------- escena Online: interfaz
  const poolOf = (scn) => { if (!scn._netT) scn._netT = { a: [], n: 0 }; return scn._netT; };
  function T(scn, s, x, y, size, col, al, wrap) {
    const P = poolOf(scn); let o = P.a[P.n++];
    if (!o) { o = scn.createObject("TxtOn"); o.setZOrder(20); o._k = ""; P.a.push(o); }
    o.hide(false); if (o._k !== s) { o.setText(s); o._k = s; }
    o.setCharacterSize(size); o.setColor(col); o.setTextAlignment(al || "center"); o.setWrapping(!!wrap); if (wrap) o.setWrappingWidth(wrap);
    const w = o.getWidth(); o.setPosition(al === "left" ? x : (al === "right" ? x - (wrap || w) : x - (wrap || w) / 2), y);
  }
  const keyDown = (e) => {
    const u = N.ui; if (u.st !== "code") return;
    if (e.key === "Backspace") u.code = u.code.slice(0, -1);
    else if (e.key === "Enter") { if (u.code.length >= 3) N.join(u.code); }
    else if (e.key === "Escape") u.st = "menu";
    else if ((e.ctrlKey || e.metaKey) && (e.key === "v" || e.key === "V")) { try { navigator.clipboard.readText().then((t) => { u.code = (t || "").toUpperCase().replace(/[^A-Z0-9]/g, "").slice(0, 8); }); } catch (x) {} }
    else if (e.key.length === 1 && /[a-zA-Z0-9]/.test(e.key) && u.code.length < 8) u.code += e.key.toUpperCase();
  };
  N.ui_tick = function (scn) {
    N.scn = scn; syncRol(scn); const I = im(scn); const u = N.ui; const P = poolOf(scn); P.n = 0;
    if (N.role === 1 && N.L && !scn._lp) { scn._lp = 1; N.started = false; pushLobby(); if (N.ui.st !== "lobby") N.ui.st = "lobby"; }
    if (N.role === 2 && N.L && !scn._lp) { scn._lp = 1; N.started = false; N.ui.st = "lobby"; }
    if (!window._fdizNetKd) { window._fdizNetKd = true; window.addEventListener("keydown", keyDown); }
    if (N.pend && N.pend.go) { const p = N.pend; N.pend = null; if (p.start) { N.slots = p.start.slots; N.started = true; applyGlobals(scn, p.start.modo, p.start.dif, p.start.slots, p.start.me); } go(scn, p.go); return; }
    const up = I.wasKeyReleased(87) || I.wasKeyReleased(38), dn = I.wasKeyReleased(83) || I.wasKeyReleased(40);
    const ok = I.wasKeyReleased(13) || I.wasKeyReleased(32), esc = I.wasKeyReleased(27);
    // flancos de los mandos
    N._pb = N._pb || [[], [], [], []]; const pe = [];
    for (let k = 0; k < 4; k++) { const g = gp(k); const cur = g ? g.buttons.map((b) => !!b.pressed).concat([g.axes[0] < -0.6, g.axes[0] > 0.6, g.axes[1] < -0.6, g.axes[1] > 0.6]) : []; const prev = N._pb[k]; pe[k] = (i) => !!cur[i] && !prev[i]; N._pb[k] = cur; }
    const pad = (i) => { for (let k = 0; k < 4; k++) if (pe[k](i)) return k + 1; return 0; };
    const IDX = { A: 0, B: 1, X: 2, Y: 3, ST: 9, UP: 12, DN: 13, L: 14, R: 15, SL: 16, SR: 17, SU: 18, SD: 19 };
    const W = 1920;
    T(scn, "JUGAR EN LÍNEA", 960, 40, 64, "255;230;120", "center");
    if (u.st === "menu") {
      if (up || dn || pad(IDX.UP) || pad(IDX.DN)) u.sel = 1 - u.sel;
      const opts = ["Crear sala (soy el host)", "Unirme a una sala con código"];
      for (let i = 0; i < 2; i++) T(scn, (u.sel === i ? ">> " : "   ") + opts[i], 960, 330 + i * 90, 48, u.sel === i ? "255;255;255" : "190;190;190", "center");
      T(scn, "En modo Jefe, el host es el Jefe (teclado y ratón) y los sobrevivientes entran desde otras PCs.", 960, 600, 28, "190;210;255", "center", 1500);
      T(scn, "Hace falta internet. Cada jugador usa su propia copia del juego.", 960, 650, 28, "190;210;255", "center", 1500);
      T(scn, "W/S elegir · Enter aceptar · Esc volver       Mando: cruceta y A", 960, 980, 26, "255;210;190", "center");
      if (ok || pad(IDX.A)) { if (u.sel === 0) N.host(); else { u.st = "code"; u.code = ""; } }
      if (esc || pad(IDX.B)) go(scn, "Menu");
    } else if (u.st === "code") {
      T(scn, "Escribe el código de la sala", 960, 300, 44, "255;255;255", "center");
      T(scn, (u.code || "") + "_", 960, 400, 90, "140;255;160", "center");
      T(scn, "Enter conectar · Ctrl+V pegar · Esc volver", 960, 980, 26, "255;210;190", "center");
    } else if (u.st === "connecting") {
      T(scn, u.msg, 960, 420, 48, "255;255;255", "center");
      if (esc) { N.shutdown(); }
    } else if (u.st === "error") {
      T(scn, u.msg || "Error", 960, 400, 44, "255;120;120", "center", 1500);
      T(scn, "Enter o Esc para volver", 960, 980, 26, "255;210;190", "center");
      if (ok || esc || pad(IDX.A) || pad(IDX.B)) { N.shutdown(); }
    } else if (u.st === "lobby" && N.L) {
      lobbyUi(scn, I, { up, dn, ok, esc, pad, IDX, pe });
    }
    for (let i = P.n; i < P.a.length; i++) P.a[i].hide(true);
  };

  function lobbyUi(scn, I, k) {
    const L = N.L, u = N.ui; const host = N.role === 1; const me = N.myId; const mine = (L.m.find((m) => m.id === me) || { players: [] });
    const mut = (fn) => { if (host) { fn(); setPlayers("host", mine.players); pushLobby(); } else { fn(); send(N.conn, { t: "claim", players: mine.players }); } };
    const canJoin = () => !(host && L.mode === "jefe") && totalPlayers(L) < 4;
    const act = (ctl, what) => {
      const i = mine.players.findIndex((p) => p.ctl === ctl);
      if (what === "ok") {
        if (i < 0) { if (canJoin()) mut(() => { mine.players = mine.players.concat([{ ctl, pj: freePj(L), ok: false }]); }); else u.msg = "No hay lugar (máx. 4 jugadores)."; }
        else if (!mine.players[i].ok) mut(() => { mine.players[i].ok = true; });
        else return false;
      } else if (what === "cancel" && i >= 0) { mut(() => { if (mine.players[i].ok) mine.players[i].ok = false; else mine.players.splice(i, 1); }); }
      else if ((what === "l" || what === "r") && i >= 0 && !mine.players[i].ok) {
        const t = takenPj(L, mine.players[i]); let pj = mine.players[i].pj;
        for (let s = 0; s < 8; s++) { pj = (pj + (what === "r" ? 1 : 7)) % 8; if (!t.has(pj)) break; }
        mut(() => { mine.players[i].pj = pj; });
      }
      return true;
    };
    // teclado (ctl 0)
    let started = false;
    if (k.ok) { const r = act(0, "ok"); if (r === false && host && N.canStart()) { N.startGame(scn); started = true; } }
    if (I.wasKeyReleased(8) || k.esc) { if (mine.players.some((p) => p.ctl === 0)) act(0, "cancel"); else if (k.esc) { N.shutdown(); return; } }
    if (I.wasKeyReleased(65) || I.wasKeyReleased(37)) act(0, "l"); if (I.wasKeyReleased(68) || I.wasKeyReleased(39)) act(0, "r");
    if (host) { if (I.wasKeyReleased(77) && !N.started) { mut(() => { L.mode = L.mode === "jefe" ? "escape" : "jefe"; if (L.mode === "jefe") mine.players = []; }); }
      if (I.wasKeyReleased(78)) { const o = ["facil", "normal", "pesadilla"]; L.dif = o[(o.indexOf(L.dif) + 1) % 3]; pushLobby(); } }
    // mandos
    for (let g = 1; g <= 4; g++) {
      const e = (i) => k.pe[g - 1](i);
      if (e(k.IDX.A)) { const r = act(g, "ok"); if (r === false && host && N.canStart()) { N.startGame(scn); started = true; } }
      if (e(k.IDX.B)) act(g, "cancel");
      if (e(k.IDX.L) || e(k.IDX.SL)) act(g, "l"); if (e(k.IDX.R) || e(k.IDX.SR)) act(g, "r");
      if (host && e(k.IDX.ST) && N.canStart()) { N.startGame(scn); started = true; }
      if (host && e(k.IDX.Y)) { mut(() => { L.mode = L.mode === "jefe" ? "escape" : "jefe"; if (L.mode === "jefe") mine.players = []; }); }
      if (host && e(k.IDX.X)) { const o = ["facil", "normal", "pesadilla"]; L.dif = o[(o.indexOf(L.dif) + 1) % 3]; pushLobby(); }
    }
    // dibujo
    T(scn, host ? "Código de la sala:  " + N.code : "Sala: " + N.code, 960, 120, 50, "140;255;160", "center");
    T(scn, "Modo: " + (L.mode === "jefe" ? "JEFE DE ZOMBIES (el host es el Jefe)" : "ESCAPE") + "      Dificultad (para los sobrevivientes): " + L.dif.toUpperCase(), 960, 190, 30, "255;230;120", "center", 1800);
    let y = 260;
    L.m.forEach((m) => {
      T(scn, (m.id === me ? "► " : "") + m.name + (m.id === "host" && L.mode === "jefe" ? "  — es el Jefe" : ""), 120, y, 32, "190;220;255", "left"); y += 44;
      if (!m.players.length) { T(scn, m.id === "host" && L.mode === "jefe" ? "(juega con teclado y ratón como Jefe)" : "(sin jugadores: pulsa A en un mando o Enter para entrar)", 160, y, 26, "170;170;170", "left"); y += 40; }
      m.players.forEach((p) => {
        const dev = p.ctl === 0 ? "TECLADO" : "MANDO " + p.ctl;
        T(scn, "[" + dev + "]   " + (p.ok ? "" : "◄ ") + (PJN[p.pj] || "?") + (p.ok ? "" : " ►") + "   " + (PJD[p.pj] || "") + (p.ok ? "   ✔ LISTO" : ""), 160, y, 28, p.ok ? "140;255;160" : "255;255;255", "left"); y += 40;
      });
      y += 14;
    });
    const nb = 4 - totalPlayers(L);
    T(scn, nb > 0 ? "Los " + nb + " lugares libres los ocuparán bots." : "Equipo completo.", 960, 900, 28, "190;210;255", "center");
    if (u.msg) T(scn, u.msg, 960, 850, 28, "255;150;150", "center");
    if (host) {
      T(scn, N.canStart() ? "Todos listos: Enter / Start para EMPEZAR" : "Esperando a que todos confirmen (Enter / A)", 960, 940, 34, N.canStart() ? "140;255;160" : "255;220;140", "center");
      T(scn, "M modo (Escape/Jefe) · N dificultad · Mando: Y modo, X dificultad · Esc salir", 960, 1000, 24, "255;210;190", "center");
    } else T(scn, "Esperando al host…   A/D cambiar personaje · Enter confirmar · Esc salir", 960, 960, 28, "255;210;190", "center");
  }
})();
