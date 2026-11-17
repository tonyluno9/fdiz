"""Fase 32 · El modo en línea también funciona en la versión web (HTML5) y entre web y escritorio. Idempotente.
Parchea net_core.js (se embebe con fase25 al correr la cadena; correr la cadena dos veces)."""
import os
AQUI = os.path.dirname(os.path.abspath(__file__))
NET = os.path.join(AQUI, "net_core.js")
js = open(NET, encoding="utf-8").read()
if "FDIZ-F32" not in js:
    def rep(viejo, nuevo):
        global js
        assert js.count(viejo) == 1, viejo[:70]
        js = js.replace(viejo, nuevo)
    rep("  const PeerC = () => (window.peerjs && window.peerjs.Peer) || window.Peer;",
        "  const PeerC = () => (window.peerjs && window.peerjs.Peer) || window.Peer;\n"
        "  /*FDIZ-F32*/ // Servidores para atravesar routers. STUN (gratis) basta en la mayoría de redes; si alguna red no deja conectar directo, agregar aquí un servidor TURN:\n"
        "  // { urls: \"turn:tu-servidor:3478\", username: \"usuario\", credential: \"clave\" }  (también se puede definir window.FDIZ_TURN = [...] antes de abrir Online)\n"
        "  const TURN = [];\n"
        "  const ICE = () => ({ iceServers: [{ urls: \"stun:stun.l.google.com:19302\" }, { urls: \"stun:stun1.l.google.com:19302\" }, { urls: \"stun:stun.cloudflare.com:3478\" }].concat(TURN, window.FDIZ_TURN || []) });")
    rep('const peer = new P("fdiz-" + code, { debug: 1 });', 'const peer = new P("fdiz-" + code, { debug: 1, config: ICE() });')
    rep("const peer = new P({ debug: 1 }); N.peer = peer;", "const peer = new P({ debug: 1, config: ICE() }); N.peer = peer;")
    rep('"No se pudo conectar (¿código correcto? ¿internet?)."', '"No se pudo conectar (¿código correcto? ¿internet? Algunas redes bloquean la conexión directa)."')
    rep('if (!window._fdizNetKd) { window._fdizNetKd = true; window.addEventListener("keydown", keyDown); }',
        'if (!window._fdizNetKd) { window._fdizNetKd = true; window.addEventListener("keydown", keyDown);\n'
        '      // pegar el código funciona en navegadores donde el portapapeles no se puede leer por tecla (versión web)\n'
        '      window.addEventListener("paste", (e) => { const u2 = N.ui; if (u2.st !== "code") return; const t = (e.clipboardData && e.clipboardData.getData("text")) || ""; u2.code = t.toUpperCase().replace(/[^A-Z0-9]/g, "").slice(0, 8); }); }')
    open(NET, "w", encoding="utf-8").write(js)
print("OK fase 32")
