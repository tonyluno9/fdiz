"""Fase 34 · Las pantallas de jugar en línea (menu, codigo, conectando, error y sala) tambien se manejan con el mouse. Idempotente.
Parchea net_core.js (se embebe con fase25 al correr la cadena; correr la cadena dos veces)."""
import os
AQUI = os.path.dirname(os.path.abspath(__file__))
NET = os.path.join(AQUI, "net_core.js")
js = open(NET, encoding="utf-8").read()
if "FDIZ-F34" not in js:
    def rep(viejo, nuevo):
        global js
        assert js.count(viejo) == 1, viejo[:80]
        js = js.replace(viejo, nuevo)
    # T devuelve su rectangulo
    rep("p.setHeight(o.getHeight() + 20);\n    }\n  }\n  const keyDown",
        "p.setHeight(o.getHeight() + 20);\n    }\n    return { x: o.getX(), y: o.getY(), w: o.getWidth(), h: o.getHeight() };\n  }\n"
        "  /*FDIZ-F34*/ // mouse: posicion, clic (al soltar) y botones de texto con resalte\n"
        "  const ms = (scn, I) => { const p = scn.getLayer(\"\").convertCoords(I.getMouseX(), I.getMouseY(), 0); const mv = N._mx !== p[0] || N._my !== p[1]; N._mx = p[0]; N._my = p[1]; return { x: p[0], y: p[1], moved: mv, up: I.isMouseButtonReleased(0) }; };\n"
        "  const over = (m, r) => m.x >= r.x - 30 && m.x <= r.x + r.w + 30 && m.y >= r.y - 12 && m.y <= r.y + r.h + 12;\n"
        "  const B = (scn, m, s, x, y, size, col, al) => { const r = T(scn, s, x, y, size, col, al || \"center\"); const h = over(m, r); if (h) { N._ptr = true; const P = poolOf(scn); P.a[P.n - 1].setColor(\"255;240;150\"); } return { hover: h, click: h && m.up }; };\n"
        "  const keyDown")
    rep("    const W = 1920;\n", "    const W = 1920;\n    const M = ms(scn, I); N._ptr = false;\n")
    # menu
    rep("      for (let i = 0; i < 2; i++) T(scn, (u.sel === i ? \">> \" : \"   \") + opts[i], 960, 350 + i * 90, 48, u.sel === i ? \"255;255;255\" : \"190;190;190\", \"center\");\n      if (ok || pad(IDX.A)) {",
        "      let mclk = false;\n"
        "      for (let i = 0; i < 2; i++) { const r = T(scn, (u.sel === i ? \">> \" : \"   \") + opts[i], 960, 350 + i * 90, 48, u.sel === i ? \"255;255;255\" : \"190;190;190\", \"center\"); if (over(M, r)) { N._ptr = true; if (M.moved) u.sel = i; if (M.up) { u.sel = i; mclk = true; } } }\n"
        "      if (B(scn, M, \"Volver\", 960, 600, 36, \"190;190;190\").click) go(scn, \"Menu\");\n"
        "      if (ok || pad(IDX.A) || mclk) {")
    # codigo
    rep("      T(scn, (u.code || \"\") + \"_\", 960, 450, 90, \"140;255;160\", \"center\");\n",
        "      T(scn, (u.code || \"\") + \"_\", 960, 450, 90, \"140;255;160\", \"center\");\n"
        "      if (B(scn, M, \"Pegar código\", 960, 580, 40, \"190;220;255\").click) { try { navigator.clipboard.readText().then((t) => { u.code = (t || \"\").toUpperCase().replace(/[^A-Z0-9]/g, \"\").slice(0, 8); }); } catch (x) {} }\n"
        "      if (B(scn, M, \"Unirme a la sala\", 960, 650, 40, u.code.length >= 3 ? \"140;255;160\" : \"120;120;120\").click && u.code.length >= 3) N.join(u.code);\n"
        "      if (B(scn, M, \"Volver\", 960, 720, 36, \"190;190;190\").click) u.st = \"menu\";\n")
    # conectando
    rep("      if (esc) { N.shutdown(); }\n", "      const bcn = B(scn, M, \"Cancelar\", 960, 600, 36, \"190;190;190\");\n      if (esc || bcn.click) { N.shutdown(); }\n")
    # error
    rep("      if (ok || esc || pad(IDX.A) || pad(IDX.B)) { N.shutdown(); }",
        "      const bac = B(scn, M, \"Aceptar\", 960, 620, 40, \"190;220;255\");\n      if (ok || esc || pad(IDX.A) || pad(IDX.B) || bac.click) { N.shutdown(); }")
    # sala
    rep("lobbyUi(scn, I, { up, dn, ok, esc, pad, IDX, pe });", "lobbyUi(scn, I, { up, dn, ok, esc, pad, IDX, pe, M });")
    rep("    } else T(scn, jf ? \"Esperando a que el Jefe inicie la partida…\" : \"Esperando al host…\", 960, 956, 32, \"255;220;140\", \"center\");\n  }\n",
        "    } else T(scn, jf ? \"Esperando a que el Jefe inicie la partida…\" : \"Esperando al host…\", 960, 956, 32, \"255;220;140\", \"center\");\n"
        "    /*FDIZ-F34*/ { const M = k.M; const bx = 1640; let by = 400; const yo = mine.players.find((p) => p.ctl === 0);\n"
        "      T(scn, \"CON EL RATÓN\", bx, by - 50, 24, \"190;210;255\", \"center\", 0, true);\n"
        "      const lin = (s, col, fn) => { if (B(scn, M, s, bx, by, 30, col).click) fn(); by += 56; };\n"
        "      if (!yo) lin(\"Unirme\", \"255;255;255\", () => act(0, \"ok\"));\n"
        "      else {\n"
        "        if (!yo.ok) { lin(\"◄ Personaje\", \"255;255;255\", () => act(0, \"l\")); lin(\"Personaje ►\", \"255;255;255\", () => act(0, \"r\")); lin(\"Listo ✔\", \"140;255;160\", () => act(0, \"ok\")); }\n"
        "        lin(\"Cancelar\", \"190;190;190\", () => act(0, \"cancel\"));\n"
        "      }\n"
        "      if (host) {\n"
        "        lin(\"Dificultad: \" + L.dif.toUpperCase(), \"255;230;120\", () => { const o = [\"facil\", \"normal\", \"pesadilla\"]; L.dif = o[(o.indexOf(L.dif) + 1) % 3]; pushLobby(); });\n"
        "        if (N.canStart()) lin(\"INICIAR PARTIDA\", \"140;255;160\", () => N.startGame(scn));\n"
        "      }\n"
        "      lin(\"Salir\", \"255;150;150\", () => N.shutdown());\n"
        "    }\n  }\n")
    # cursor
    rep("    if (u.st !== \"lobby\") N._bgOn = true;\n",
        "    if (u.st !== \"lobby\") N._bgOn = true;\n    /*FDIZ-F34*/ try { const cv = scn.getGame().getRenderer().getCanvas(); if (cv) cv.style.cursor = N._ptr ? \"pointer\" : \"default\"; } catch (e) {}\n")
    open(NET, "w", encoding="utf-8").write(js)
print("OK fase 34")
