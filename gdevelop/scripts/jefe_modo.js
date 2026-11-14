/* FDI-Z · Modo Jefe de zombies (fase 22). Se incrusta en el grupo "Modo Jefe de zombies" de la escena Juego con scripts/fase22_jefe.py.
 * Interfaz y reglas completas en JavaScript: cámara libre (WASD/flechas), cartas con iconos, invocar con clic en el mapa,
 * zona roja = lo que ven los sobrevivientes (ahí no se puede invocar), minimapa con puntos, ayuda y mensajes.
 * El Jefe juega solo con teclado y ratón; los 4 sobrevivientes son bots. */
(function () {
  "use strict";
  const scn = runtimeScene;
  const V = scn.getVariables();
  if (V.get("Jefe").getAsNumber() !== 1) return;
  const T0 = scn.getTimeManager().getTimeFromStart();
  if (scn._fdizJf && T0 < (scn._fdizJfT || 0)) scn._fdizJf = null; // la escena se reinició
  scn._fdizJfT = T0;
  const J = scn._fdizJf || (scn._fdizJf = build());
  try { J.frame(); } catch (e) { if (!J.err) { J.err = true; console.error("[FDI-Z Jefe]", e); } }

  function build() {
    const WW = 8768, WH = 5376, ZOOM = 0.8, VIS = 620;
    const MM = { x: 1482, y: 300, w: 418, h: 256 };
    const CD = { x0: 476, y0: 806, w: 114, h: 175, gap: 8 };
    const PLAY = ["255;215;80", "100;170;255", "120;220;110", "255;120;190"];
    const CARTAS = [
      { n: "Zombie", cost: 2, cd: 0.4, obj: "ZNormal", cnt: 1, desc: "Zombi básico: persigue y muerde. Barato, sirve para acosar y cansar al grupo.", stat: "Vida 30 · Daño 5 · velocidad media" },
      { n: "Corredor", cost: 3, cd: 1.5, obj: "ZCorredor", cnt: 1, desc: "Muy rápido pero frágil. Ideal para alcanzar a quien se separó del grupo.", stat: "Vida 16 · Daño 4 · muy rápido" },
      { n: "Gritón", cost: 5, cd: 10, obj: "ZGriton", cnt: 1, desc: "Su grito atrae a los zombis cercanos hacia los sobrevivientes.", stat: "Vida 34 · Daño 4 · velocidad media" },
      { n: "Gordo", cost: 7, cd: 15, obj: "ZGordo", cnt: 1, desc: "Aguanta muchísimo y pega fuerte. Bloquea pasillos y agota munición.", stat: "Vida 120 · Daño 11 · lento" },
      { n: "Horda chica", cost: 8, cd: 20, obj: "ZNormal", cnt: 5, desc: "Cinco zombis básicos al mismo tiempo en la zona elegida.", stat: "5 zombis básicos" },
      { n: "Trabar puerta", cost: 4, cd: 15, sp: "puerta", desc: "Atranca la puerta normal más cercana al clic durante 10 s: tendrán que romperla.", stat: "Efecto · 10 segundos" },
      { n: "Apagón", cost: 6, cd: 30, sp: "apagon", desc: "Apaga las luces 15 s para que los sobrevivientes vean menos. Clic en cualquier punto.", stat: "Efecto · 15 segundos" },
      { n: "Horda grande", cost: 18, cd: 60, minInf: 3, mix: ["ZNormal", "ZCorredor", "ZGordo", "ZNormal", "ZCorredor", "ZGordo", "ZNormal", "ZCorredor", "ZGordo", "ZNormal", "ZCorredor", "ZGordo"], desc: "12 zombis mezclados de golpe. Se desbloquea en el nivel 3 de infestación.", stat: "12 zombis · nivel 3+" },
    ];
    { const GV = scn.getGame().getVariables(), d0 = GV.get("Dificultad").getAsString();
      const k = d0 === "facil" ? [0.7, 0.7] : (d0 === "pesadilla" ? [1.6, 1.6] : [1, 1]);
      GV.get("DifVida").setNumber(k[0]); GV.get("DifDanio").setNumber(k[1]); }
    const ZN = ["ZNormal", "ZCorredor", "ZGriton", "ZGordo", "ZConserje", "ZCurado"];
    const im = scn.getGame().getInputManager();
    const base = scn.getLayer(""), hud = scn.getLayer("HUD");
    const st = { t: 0, sel: 0, cdEnd: new Array(8).fill(0), goldT: 0, prev: {}, mprev: [false, false], msg: null, fx: [],
      help: true, helpT: 0, doors: [], apagonUntil: 0, tx: [], txn: 0, cards: [], icons: [], cam: null, firstSpawn: false, count: 0 };

    const first = (n) => { const a = scn.getObjects(n); return a && a.length ? a[0] : null; };
    const dB = first("JfDibB"), dO = first("JfDibO"), dM = first("JfDibM");
    if (dB) dB.setZOrder(55); if (dO) dO.setZOrder(66); if (dM) dM.setZOrder(99999);
    if (dM) dM.setLayer("Techo");
    if (dB) dB.setLayer("HUD"); if (dO) dO.setLayer("HUD");

    // tarjetas e iconos (sprites en la capa HUD)
    for (let i = 0; i < 8; i++) {
      const c = scn.createObject("JfCarta"); c.setLayer("HUD"); c.setZOrder(62); c.setWidth(CD.w); c.setHeight(CD.h); st.cards.push(c);
      const ic = scn.createObject("JfIcono"); ic.setLayer("HUD"); ic.setZOrder(63); ic.setAnimationName("c" + (i + 1)); ic.setWidth(76); ic.setHeight(76); st.icons.push(ic);
    }
    const mini = first("Minimapa");
    if (mini) { mini.setPosition(MM.x, MM.y); mini.setWidth(MM.w); mini.setHeight(MM.h); mini.setZOrder(5); }

    // ---------- utilidades ----------
    function txt(s, x, y, size, color, align, w) {
      let o = st.tx[st.txn];
      if (!o) { o = scn.createObject("JfTexto"); o.setLayer("HUD"); o.setZOrder(70); o.setWrapping(true); st.tx.push(o); o._k = ""; }
      st.txn++;
      const key = s + "|" + size + "|" + color + "|" + align + "|" + w;
      if (o._k !== key) {
        o._k = key; o.setText(s); o.setCharacterSize(size); o.setColor(color || "255;255;255");
        o.setTextAlignment(align || "left"); o.setWrappingWidth(w || 900);
      }
      o.hide(false); o.setPosition(x, y);
    }
    const hit = (px, py, x, y, w, h) => px >= x && px <= x + w && py >= y && py <= y + h;
    const mmX = (wx) => MM.x + wx * MM.w / WW, mmY = (wy) => MM.y + wy * MM.h / WH;
    function walk(x, y) {
      const NAV = gdjs.fdizNav, g = NAV && NAV.grid; if (!g) return true;
      const cx = Math.floor(x / NAV.cfg.C), cy = Math.floor(y / NAV.cfg.C);
      if (cx < 0 || cy < 0 || cx >= g.W || cy >= g.H) return false;
      return g.cls[cy * g.W + cx] === 0;
    }
    function sups() { return scn.getObjects("Sup") || []; }
    function zombies() { const r = []; for (const n of ZN) { const a = scn.getObjects(n); if (a) for (const z of a) r.push(z); } return r; }
    const sv = (o, n) => o.getVariables().get(n);
    function nearSurv(x, y) {
      let best = 1e9;
      for (const s of sups()) { if (sv(s, "Estado").getAsString() === "muerto") continue; const d = Math.hypot(s.getX() - x, s.getY() - y); if (d < best) best = d; }
      return best;
    }
    function say(text, color) { st.msg = { text, color: color || "255;120;120", t: st.t + 2.2 }; }
    function card(i) { return CARTAS[i]; }
    function status(i) {
      const c = card(i), inf = V.get("Infestacion").getAsNumber(), oro = V.get("OroJefe").getAsNumber();
      if (c.minInf && inf < c.minInf) return { ok: false, why: "lock", txt: "Nivel " + c.minInf };
      const rest = st.cdEnd[i] - st.t;
      if (rest > 0) return { ok: false, why: "cd", rest, txt: Math.ceil(rest) + " s" };
      if (oro < c.cost) return { ok: false, why: "oro", txt: "Falta oro" };
      return { ok: true };
    }
    function place(i, wx, wy) {
      const c = card(i), s = status(i);
      if (!s.ok) { say(s.why === "lock" ? "Se desbloquea en el nivel " + c.minInf + " de infestación" : s.why === "cd" ? "Recargando: " + s.txt : "Te falta oro (cuesta " + c.cost + ")"); return false; }
      if (c.sp === "apagon") {
        V.get("Apagon").setNumber(1); st.apagonUntil = st.t + 15;
      } else if (c.sp === "puerta") {
        let best = null, bd = 300;
        for (const p of scn.getObjects("Puerta") || []) {
          if (sv(p, "Tipo").getAsString() !== "normal") continue;
          const d = Math.hypot(p.getX() + p.getWidth() / 2 - wx, p.getY() + p.getHeight() / 2 - wy); if (d < bd) { bd = d; best = p; }
        }
        if (!best) { say("No hay una puerta normal cerca del clic"); return false; }
        sv(best, "Trabada").setNumber(1); sv(best, "TiempoAbrir").setNumber(99); st.doors.push({ o: best, until: st.t + 10 });
      } else {
        const sd = nearSurv(wx, wy);
        if (sd < VIS) { say("Zona visible: la ven los sobrevivientes (zona roja)"); return false; }
        if (!walk(wx, wy)) { say("No cabe un zombi ahí (pared o mueble)"); return false; }
        const list = c.mix || new Array(c.cnt).fill(c.obj);
        let n = 0;
        for (let k = 0; k < list.length; k++) {
          let px = wx, py = wy;
          if (list.length > 1) { for (let t = 0; t < 8; t++) { px = wx + (Math.random() - 0.5) * 140; py = wy + (Math.random() - 0.5) * 140; if (walk(px, py) && nearSurv(px, py) >= VIS) break; px = wx; py = wy; } }
          const z = scn.createObject(list[k]); if (!z) continue;
          z.setPosition(px, py); z.setLayer("Juego"); sv(z, "Estado").setString("persigue"); n++;
        }
        if (!n) return false;
      }
      V.get("OroJefe").setNumber(V.get("OroJefe").getAsNumber() - c.cost);
      st.cdEnd[i] = st.t + c.cd; st.fx.push({ x: wx, y: wy, t: st.t, sp: !!c.sp }); st.firstSpawn = true; if (st.help) st.help = false;
      scn.getGame().getSoundManager().playSound("efectos/interfaz/jefe_invocar.ogg", false, 75, 1);
      return true;
    }

    function frame() {
      const dt = Math.min(0.1, scn.getElapsedTime() / 1000);
      const estado = V.get("Estado").getAsString(), pausa = V.get("Pausa").getAsNumber() === 1;
      const active = estado === "juego" && !pausa;
      st.txn = 0;
      for (const d of [dB, dO, dM]) if (d) d.clear();
      const S = sups(), Zs = zombies();
      if (!st.cam && S.length) { let ax = 0, ay = 0; for (const s of S) { ax += s.getX(); ay += s.getY(); } st.cam = { x: ax / S.length, y: ay / S.length }; }
      if (!st.cam) st.cam = { x: 4000, y: 2600 };
      if (active) st.t += dt;
      const tj = first("TxtJefe"); if (tj) tj.hide(true);
      if (estado === "juego") {
        const algunoVivo = S.some((s) => sv(s, "Estado").getAsString() === "normal");
        st.sinVivos = algunoVivo ? 0 : (st.sinVivos || 0) + dt;
        if (st.sinVivos > 2) { V.get("Estado").setString("derrota"); scn.getTimeManager().addTimer("fin"); }
      }

      // ------ entrada ------
      const keyDown = (c) => im.isKeyPressed(c);
      const keyEdge = (c) => im.wasKeyReleased(c);
      const mx = im.getMouseX(), my = im.getMouseY();
      const hp = hud.convertCoords(mx, my, 0), hx = hp[0], hy = hp[1];
      const wp = base.convertCoords(mx, my, 0), wx = wp[0], wy = wp[1];
      const ld = im.isMouseButtonPressed(0), rd = im.isMouseButtonPressed(1);
      // se actúa al soltar el botón: así un clic muy corto (menos de un cuadro) tampoco se pierde
      const click = im.isMouseButtonReleased(0), rclick = im.isMouseButtonReleased(1);
      const edge72 = keyEdge(72), edge32 = keyEdge(32);
      const nk = [49, 50, 51, 52, 53, 54, 55, 56], np = [97, 98, 99, 100, 101, 102, 103, 104];
      const nEdges = nk.map((k, i) => keyEdge(k) || keyEdge(np[i]));
      if (active) {
        let sp = (keyDown(16) ? 2600 : 1500) * dt, dx = 0, dy = 0;
        if (keyDown(65) || keyDown(37)) dx -= 1; if (keyDown(68) || keyDown(39)) dx += 1;
        if (keyDown(87) || keyDown(38)) dy -= 1; if (keyDown(83) || keyDown(40)) dy += 1;
        st.cam.x += dx * sp; st.cam.y += dy * sp;
        if (edge32) { const al = S.filter((s) => sv(s, "Estado").getAsString() !== "muerto"); if (al.length) { let ax = 0, ay = 0; for (const s of al) { ax += s.getX(); ay += s.getY(); } st.cam.x = ax / al.length; st.cam.y = ay / al.length; } }
        if (edge72) st.help = !st.help;
        for (let i = 0; i < 8; i++) if (nEdges[i]) st.sel = i;
        if (rclick) st.sel = -1;
      }
      // zona de interfaz
      const cardX = (i) => CD.x0 + i * (CD.w + CD.gap);
      let overCard = -1;
      for (let i = 0; i < 8; i++) if (hit(hx, hy, cardX(i), CD.y0 - 14, CD.w, CD.h + 14)) overCard = i;
      const overMini = hit(hx, hy, MM.x, MM.y, MM.w, MM.h);
      const overPanel = hit(hx, hy, 20, 300, 400, 330) || hit(hx, hy, 0, 0, 1920, 190) && (hx < 440 || hx > 1480) || hit(hx, hy, 20, 880, 420, 190) || hit(hx, hy, 1482, 880, 420, 190) || hit(hx, hy, 430, 960, 1060, 120);
      const overUI = overCard >= 0 || overMini || overPanel;
      if (active && click) {
        if (overCard >= 0) st.sel = overCard;
        else if (overMini) { st.cam.x = (hx - MM.x) / MM.w * WW; st.cam.y = (hy - MM.y) / MM.h * WH; }
        else if (!overUI) {
          if (st.help && st.helpT > 1) st.help = false;
          else if (st.sel < 0) say("Primero elige una carta (teclas 1 a 8)", "255;225;120");
          else place(st.sel, wx, wy);
        }
      }
      if (active && ld && overMini) { st.cam.x = (hx - MM.x) / MM.w * WW; st.cam.y = (hy - MM.y) / MM.h * WH; }
      st.cam.x = Math.max(960 / ZOOM, Math.min(WW - 960 / ZOOM, st.cam.x));
      st.cam.y = Math.max(540 / ZOOM, Math.min(WH - 540 / ZOOM, st.cam.y));
      base.setCameraZoom(ZOOM, 0); base.setCameraX(st.cam.x, 0); base.setCameraY(st.cam.y, 0);

      // ------ oro, puertas, apagón ------
      if (active) {
        const dif = scn.getGame().getVariables().get("Dificultad").getAsString(); st.rate = dif === "facil" ? 2 : (dif === "pesadilla" ? 6 : 4);
        st.goldT += dt * st.rate;
        if (st.goldT >= 1) { const n = Math.floor(st.goldT); st.goldT -= n; V.get("OroJefe").setNumber(V.get("OroJefe").getAsNumber() + n); }
        st.helpT += dt; if (st.help && st.helpT > 22) st.help = false;
      }
      for (let i = st.doors.length - 1; i >= 0; i--) if (st.t >= st.doors[i].until) { const p = st.doors[i].o; try { sv(p, "Trabada").setNumber(0); sv(p, "TiempoAbrir").setNumber(1); } catch (e) {} st.doors.splice(i, 1); }
      if (st.apagonUntil && st.t >= st.apagonUntil) { st.apagonUntil = 0; if (V.get("ObjTipo").getAsString() !== "luz") V.get("Apagon").setNumber(0); }

      // ------ dibujo en el mundo ------
      if (dM) {
        for (const s of S) {
          if (sv(s, "Estado").getAsString() === "muerto") continue;
          dM.setFillColor("255;50;50"); dM.setFillOpacity(34); dM.setOutlineColor("255;90;90"); dM.setOutlineOpacity(150); dM.setOutlineSize(5);
          dM.drawCircle(s.getX(), s.getY() - 40, VIS);
        }
        for (let i = st.fx.length - 1; i >= 0; i--) {
          const f = st.fx[i], k = (st.t - f.t) / 0.6; if (k > 1) { st.fx.splice(i, 1); continue; }
          dM.setFillOpacity(0); dM.setOutlineColor(f.sp ? "255;230;90" : "255;255;255"); dM.setOutlineOpacity(255 * (1 - k)); dM.setOutlineSize(8);
          dM.drawCircle(f.x, f.y, 20 + 110 * k);
        }
        if (!overUI && active && st.sel >= 0) {
          const c = card(st.sel); let ok = status(st.sel).ok, why = "";
          if (!c.sp) { if (nearSurv(wx, wy) < VIS) { ok = false; why = "ZONA VISIBLE"; } else if (!walk(wx, wy)) { ok = false; why = "NO CABE"; } }
          dM.setFillColor(ok ? "90;255;120" : "255;80;80"); dM.setFillOpacity(70); dM.setOutlineColor(ok ? "200;255;200" : "255;180;180"); dM.setOutlineOpacity(255); dM.setOutlineSize(5);
          dM.drawCircle(wx, wy, c.cnt > 1 || c.mix ? 90 : 30);
          if (why) txt(why, hx + 26, hy + 8, 22, "255;140;140", "left", 300);
        }
      }

      // ------ HUD: panel de misión ------
      const vivos = S.filter((s) => sv(s, "Estado").getAsString() === "normal").length;
      const inf = V.get("Infestacion").getAsNumber(), oro = V.get("OroJefe").getAsNumber();
      if (dB) {
        const panel = (x, y, w, h, line) => { dB.setFillColor("14;18;44"); dB.setFillOpacity(222); dB.setOutlineColor(line || "70;190;170"); dB.setOutlineOpacity(255); dB.setOutlineSize(4); dB.drawRectangle(x, y, x + w, y + h); };
        panel(20, 300, 400, 330);
        dB.setFillColor("70;190;170"); dB.setOutlineSize(0); dB.setFillOpacity(255); dB.drawRectangle(20, 300, 420, 344);
        // barra de progreso del próximo oro
        dB.setFillColor("40;46;86"); dB.drawRectangle(40, 586, 400, 604);
        dB.setFillColor("255;215;80"); dB.drawRectangle(40, 586, 40 + 360 * st.goldT, 604);
        // minimapa: marco
        dB.setFillColor("14;18;44"); dB.setOutlineColor("70;190;170"); dB.setOutlineSize(4); dB.setFillOpacity(0); dB.drawRectangle(MM.x - 6, MM.y - 6, MM.x + MM.w + 6, MM.y + MM.h + 6);
        // tarjeta de ayuda de cartas (tooltip)
        const tip = overCard >= 0 ? overCard : st.sel;
        if (tip >= 0) { panel(CD.x0, 640, 968, 148, "255;215;80"); }
      }
      txt("MISIÓN DEL JEFE", 20, 306, 28, "20;24;50", "center", 400);
      txt("Detén a los 4 sobrevivientes antes de que cumplan el objetivo y escapen.", 36, 354, 20, "255;255;255", "left", 370);
      txt("1) Elige una carta (1-8 o clic).", 36, 428, 19, "170;230;255", "left", 370);
      txt("2) Clic en el mapa FUERA de la zona roja (lo que ven ellos).", 36, 454, 19, "170;230;255", "left", 370);
      txt("En pie: " + vivos + "/" + S.length + "    Zombis: " + Zs.length, 36, 500, 20, "255;225;120", "left", 380);
      txt("Infestación " + inf + "/5" + (inf < 3 ? " (Horda grande: nivel 3)" : ""), 36, 528, 18, "255;190;120", "left", 380);
      txt("Oro: +" + (st.rate || 4) + " por segundo", 36, 556, 16, "255;225;90", "left", 380);
      txt("WASD cámara · Espacio: grupo · H: ayuda", 36, 612, 14, "190;190;210", "left", 380);

      // ------ cartas ------
      for (let i = 0; i < 8; i++) {
        const c = card(i), s = status(i), sel = st.sel === i, lift = sel || overCard === i ? -12 : 0, x = cardX(i), y = CD.y0 + lift;
        st.cards[i].setPosition(x, y); st.icons[i].setPosition(x + 19, y + 44);
        if (dO) {
          if (!s.ok) { dO.setFillColor(s.why === "cd" ? "10;10;24" : "10;10;24"); dO.setFillOpacity(s.why === "oro" ? 120 : 170); dO.setOutlineSize(0); dO.drawRectangle(x + 6, y + 6, x + CD.w - 6, y + CD.h - 6); }
          if (s.why === "cd") { const k = s.rest / c.cd; dO.setFillColor("255;255;255"); dO.setFillOpacity(60); dO.drawRectangle(x + 6, y + CD.h - 6 - (CD.h - 12) * k, x + CD.w - 6, y + CD.h - 6); }
          if (sel) { dO.setFillOpacity(0); dO.setOutlineColor("255;215;80"); dO.setOutlineOpacity(255); dO.setOutlineSize(6); dO.drawRectangle(x, y, x + CD.w, y + CD.h); }
          dO.setFillColor(oro >= c.cost ? "255;205;60" : "120;100;60"); dO.setFillOpacity(255); dO.setOutlineColor("120;80;0"); dO.setOutlineSize(3); dO.setOutlineOpacity(255);
          dO.drawCircle(x + 28, y + CD.h - 22, 11);
        }
        txt(String(i + 1), x, y + 8, 26, "255;255;255", "center", CD.w);
        txt(c.n, x + 2, y + 122, 17, "255;255;255", "center", CD.w - 4);
        txt(String(c.cost), x + 46, y + CD.h - 38, 26, oro >= c.cost ? "255;225;90" : "255;120;120", "left", 60);
        if (!s.ok && s.why !== "oro") txt(s.txt, x, y + 70, s.why === "lock" ? 18 : 28, "255;255;255", "center", CD.w);
      }
      const tip = overCard >= 0 ? overCard : st.sel;
      if (tip >= 0) {
        const c = card(tip);
        txt(c.n.toUpperCase() + "   ·   " + c.cost + " de oro   ·   recarga " + c.cd + " s", CD.x0 + 18, 648, 24, "255;215;80", "left", 930);
        txt(c.desc, CD.x0 + 18, 690, 21, "255;255;255", "left", 930);
        txt(c.stat, CD.x0 + 18, 748, 19, "170;230;255", "left", 930);
      }

      // ------ minimapa ------
      if (dO) {
        dO.setOutlineSize(0);
        for (const s of S) { if (sv(s, "Estado").getAsString() === "muerto") continue; dO.setFillColor("255;60;60"); dO.setFillOpacity(40); dO.drawCircle(mmX(s.getX()), mmY(s.getY()), VIS * MM.w / WW); }
        dO.setFillColor("255;70;70"); dO.setFillOpacity(255);
        for (const z of Zs) dO.drawRectangle(mmX(z.getX()) - 2, mmY(z.getY()) - 2, mmX(z.getX()) + 2, mmY(z.getY()) + 2);
        for (const s of S) {
          const dead = sv(s, "Estado").getAsString() !== "normal", pj = (sv(s, "Jugador").getAsNumber() || 1) - 1;
          dO.setFillColor(dead ? "130;130;130" : PLAY[pj % 4]); dO.setFillOpacity(255); dO.setOutlineColor("255;255;255"); dO.setOutlineSize(2); dO.setOutlineOpacity(255);
          dO.drawCircle(mmX(s.getX()), mmY(s.getY()), 6);
        }
        const ot = V.get("ObjTipo").getAsString();
        if (ot && ot !== "") { const ox = V.get("ObjX").getAsNumber(), oy = V.get("ObjY").getAsNumber(); if (ox > 0) { dO.setFillColor("255;225;40"); dO.setOutlineColor("60;40;0"); dO.setOutlineSize(2); dO.drawRectangle(mmX(ox) - 5, mmY(oy) - 5, mmX(ox) + 5, mmY(oy) + 5); } }
        dO.setFillOpacity(0); dO.setOutlineColor("255;255;255"); dO.setOutlineOpacity(230); dO.setOutlineSize(2);
        const vw = 1920 / ZOOM, vh = 1080 / ZOOM;
        dO.drawRectangle(mmX(st.cam.x - vw / 2), mmY(st.cam.y - vh / 2), mmX(st.cam.x + vw / 2), mmY(st.cam.y + vh / 2));
      }
      txt("MAPA · clic para mover la cámara", MM.x, MM.y - 34, 18, "255;255;255", "left", MM.w);
      txt("● sobrevivientes   ■ zombis   ■ objetivo", MM.x, MM.y + MM.h + 8, 15, "200;200;220", "left", MM.w);

      // ------ ayuda inicial y mensajes ------
      if (st.help && active && dB) {
        dB.setFillColor("8;10;30"); dB.setFillOpacity(236); dB.setOutlineColor("255;215;80"); dB.setOutlineOpacity(255); dB.setOutlineSize(6); dB.drawRectangle(500, 210, 1420, 556);
        for (let k = 0; k < 3; k++) { dB.setFillColor("255;215;80"); dB.setOutlineSize(0); dB.drawCircle(556, 336 + k * 74, 22); }
        txt("CÓMO JUGAR EL MODO JEFE", 500, 226, 36, "255;215;80", "center", 920);
        txt("1", 540, 316, 30, "20;24;50", "center", 32); txt("2", 540, 390, 30, "20;24;50", "center", 32); txt("3", 540, 464, 30, "20;24;50", "center", 32);
        txt("ELIGE una carta de abajo (teclas 1-8 o clic).", 600, 318, 26, "255;255;255", "left", 800);
        txt("HAZ CLIC en el mapa FUERA de la zona roja para invocar zombis.", 600, 392, 26, "255;255;255", "left", 800);
        txt("Sobrevivientes (bots o mandos): ¡deténlos antes de que escapen!", 600, 466, 26, "255;255;255", "left", 800);
        txt("WASD mueve la cámara · H oculta esta ayuda", 500, 516, 18, "170;230;255", "center", 920);
      }
      if (st.msg && st.t < st.msg.t && !overUI) txt(st.msg.text, hx + 24, hy - 40, 24, st.msg.color, "left", 520);
      else if (st.msg && st.t < st.msg.t) txt(st.msg.text, 560, 596, 26, st.msg.color, "left", 800);
      for (let i = st.txn; i < st.tx.length; i++) st.tx[i].hide(true);
    }
    return { frame, st };
  }
})();
