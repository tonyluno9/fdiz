"""Fase 60 · Efectos de sonido de la carpeta "sonidos 2d" (22 OGG). Idempotente.

Uso (desde la carpeta fdiz, con GDevelop CERRADO):
    python -I gdevelop/scripts/fase60_sonidos2d.py ["ruta de la carpeta con los .ogg"]
La carpeta por defecto es ..\\sonidos 2d\\sonidos 2d\\ogg (junto a fdiz). Si ya están en fdiz/sonidos/, no hace falta.

Qué hace:
  1) Copia los 22 .ogg a fdiz/sonidos/ y los registra como recursos de audio con el MISMO nombre del archivo
     ("ui_click.ogg", ...). El archivo del recurso es "../../sonidos/<nombre>.ogg" (relativo a FDI-Z.json).
  2) Incrusta scripts/sfx.js al inicio de TODAS las escenas (FDIZ-FASE60-MOD + FDIZ-FASE60-TICK, sin compuerta de host):
     interfaz (hover, clic, aceptar, error), golpes, dolor, caídas, zombis (growl, ataque, mordida, muerte, aparición),
     objetos, oro, curarse, oleadas, entrada a cada escena (título, transiciones, empezar partida, victoria / game over).
  3) Eventos de Juego que ya tenían un sonido equivalente pasan al nuevo:
       puerta_abrir.ogg -> puerta_casillero.ogg   (se abre una puerta)
       locker.ogg       -> puerta_casillero.ogg   (se abre un locker / mochila / máquina)
       bidon.ogg        -> objeto_recoger.ogg     (tomar y entregar el bidón)
       infestacion_sube -> oleada_riser.ogg       (sube la infestación = nueva oleada)
       final_inicio     -> evento_impacto_cinematico.ogg (empieza el final, la alarma)
       escape.ogg       + puerta_casillero.ogg    (se abre la salida)
     Se quitan (los pone sfx.js, para no sonar dos veces): comer.ogg (curarse -> curar_powerup), mordida.ogg
     (zombie_mordida), victoria.ogg de Resultados (victoria / game_over) y jefe_invocar.ogg del modo Jefe
     (zombie_spawn_braam + oro_moneda + ui_confirm). Los mensajes de error del Jefe ("Te falta oro", ...) suenan con ui_error.
  4) Deja preparados, desactivados y con comentario, los eventos de pasos (// TODO: footsteps) y de música de partida /
     tensión (// TODO: música de partida / tensión), que se dispara al empezar una oleada (variable OleadaInicio).
"""
import copy, datetime, hashlib, json, os, shutil, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
PROY = os.path.join(RAIZ, "gdevelop", "FDI-Z")
PRY = os.path.join(PROY, "FDI-Z.json")
DEST = os.path.join(RAIZ, "sonidos")
FUENTE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(RAIZ, "..", "sonidos 2d", "sonidos 2d", "ogg")
MK = "FDIZ-FASE60"

SONIDOS = ["ui_click", "ui_hover", "ui_confirm", "ui_error", "golpe_impacto", "jugador_dolor", "cuerpo_caida", "whoosh_esquivar",
           "zombie_growl", "zombie_ataque", "zombie_mordida", "zombie_muerte_01", "zombie_muerte_02", "zombie_spawn_braam",
           "oro_moneda", "objeto_recoger", "puerta_casillero", "curar_powerup", "oleada_riser", "evento_impacto_cinematico",
           "game_over", "victoria"]
REL = "../../sonidos/"                      # desde gdevelop/FDI-Z/ hasta fdiz/sonidos/

# evento de Juego: archivo viejo -> (archivo nuevo, volumen)
CAMBIAR = {
    "efectos/mundo/puerta_abrir.ogg": ("puerta_casillero.ogg", "80"),
    "efectos/mundo/locker.ogg": ("puerta_casillero.ogg", "80"),
    "efectos/mundo/bidon.ogg": ("objeto_recoger.ogg", "80"),
    "efectos/eventos/infestacion_sube.ogg": ("oleada_riser.ogg", "85"),
    "efectos/eventos/final_inicio.ogg": ("evento_impacto_cinematico.ogg", "95"),
}
QUITAR = {"Juego": ["efectos/movimiento/comer.ogg", "efectos/combate/mordida.ogg"], "Resultados": ["efectos/eventos/victoria.ogg"]}
JEFE = [
    ('function say(text, color) { st.msg = { text, color: color || "255;120;120", t: st.t + 2.2 }; }',
     'function say(text, color) { st.msg = { text, color: color || "255;120;120", t: st.t + 2.2 }; '
     'if (!color) { try { if (gdjs.fdizSfx) gdjs.fdizSfx.ui(scn, "error"); } catch (e) {} } /*FDIZ-FASE60: ui_error*/ }'),
    ('scn.getGame().getSoundManager().playSound("efectos/interfaz/jefe_invocar.ogg", false, 75, 1);',
     '/*FDIZ-FASE60: el gasto suena con oro_moneda + ui_confirm y cada zombi con zombie_spawn_braam (sfx.js)*/'),
]

LISTA = {
    "Titulo": "al entrar: evento_impacto_cinematico (95).",
    "Menu": "al entrar: whoosh_esquivar (70, transición). Cursor sobre un botón: ui_hover (50). Clic, cambiar de paso, "
            "elegir personaje o control, dificultad: ui_click (55). Mover la selección con teclado o mando: ui_hover. "
            "LISTO / empezar: ui_confirm (60).",
    "Online": "al entrar: whoosh_esquivar (70). Cambiar de pantalla de la sala: ui_click; entrar a la sala: ui_confirm; "
              "error de red: ui_error; mover la selección: ui_hover.",
    "Resultados": "al entrar: victoria (90) o game_over (90). Botones: ui_hover / ui_click.",
    "Juego": "al entrar: ui_confirm (empezar partida). Pausa y sus botones: ui_click / ui_hover. Golpes: golpe_impacto (75, ±0.1, "
             "cooldown 0.1 s); jugador golpeado: + zombie_mordida (85) + jugador_dolor (80; pitch 0.8, Miranda 1.0; ±0.1). "
             "Cae un jugador o muere un zombi: cuerpo_caida (75). Ataque del jugador: whoosh_esquivar (70). Zombis (pitch normal "
             "1.0, gordo y conserje 0.7, corredor 1.3): zombie_growl (hasta 80 según la distancia, intervalo aleatorio), "
             "zombie_ataque (75), zombie_muerte_01/02 al azar (80), zombie_spawn_braam (80, también al invocar el Jefe). "
             "Tomar armas, lanzables, comida guardada, bolsa o llaves: objeto_recoger (80). Monedas y oro: oro_moneda (75, "
             "cooldown 0.1 s); compra del Jefe: + ui_confirm; error del Jefe o puerta restringida: ui_error. Curarse o "
             "levantarse: curar_powerup (80). Horda o cuenta regresiva del final: oleada_riser (85). Aparece el conserje "
             "(jefe) o empieza el modo Jefe: evento_impacto_cinematico (95).",
}


def js(code, marca):
    return {"type": "BuiltinCommonInstructions::JsCode", "inlineCode": "/*" + marca + "*/\n" + code,
            "parameterObjects": "", "useStrict": True, "eventsSheetExpanded": False}


def std(conds, acts, sub=(), apagado=False):
    e = {"type": "BuiltinCommonInstructions::Standard", "conditions": conds, "actions": acts, "events": list(sub)}
    if apagado: e["disabled"] = True
    return e


def c(tipo, *p, inv=False):
    return {"type": {"inverted": inv, "value": tipo}, "parameters": list(p)}


def a(tipo, *p):
    return {"type": {"value": tipo}, "parameters": list(p)}


def comentario(t):
    return {"type": "BuiltinCommonInstructions::Comment", "color": {"b": 109, "g": 230, "r": 255, "textB": 0, "textG": 0, "textR": 0},
            "comment": t, "comment2": ""}


def recorrer(lst):
    for e in lst:
        yield e
        yield from recorrer(e.get("events", []))


def es_marca(e, marca):
    if e.get("type", "").endswith("JsCode"):
        return e.get("inlineCode", "").startswith("/*" + marca)
    if e.get("type", "").endswith("Comment"):
        return marca in e.get("comment", "")[:80]
    return bool(e.get("__fdiz") == marca)


def quitar(lst, marca):
    """Quita los eventos con la marca; si es un comentario marcado, también el evento desactivado que va justo después."""
    fuera, i = [], 0
    while i < len(lst):
        e = lst[i]
        if es_marca(e, marca):
            if e.get("type", "").endswith("Comment") and i + 1 < len(lst) and lst[i + 1].get("disabled"):
                i += 1
            i += 1
            continue
        fuera.append(e); i += 1
    lst[:] = fuera
    for e in lst:
        if e.get("events"): quitar(e["events"], marca)


def grupo(ev, nombre):
    return next(e for e in recorrer(ev) if e.get("type", "").endswith("Group") and e.get("name") == nombre)


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def main():
    # ---- 1) archivos
    os.makedirs(DEST, exist_ok=True)
    copiados = 0
    for n in SONIDOS:
        dst = os.path.join(DEST, n + ".ogg")
        src = os.path.join(FUENTE, n + ".ogg")
        if os.path.exists(src):
            with open(src, "rb") as f:
                if f.read(4) != b"OggS":
                    raise SystemExit("No es OGG: " + src)
            if not os.path.exists(dst) or md5(src) != md5(dst):
                shutil.copyfile(src, dst); copiados += 1
        if not os.path.exists(dst):
            raise SystemExit("Falta " + dst + " (y no está en " + FUENTE + ")")

    d = json.load(open(PRY, encoding="utf-8"))
    resp = os.path.join(AQUI, "..", "respaldos")
    os.makedirs(resp, exist_ok=True)
    bak = os.path.join(resp, "antes_de_fase60_%s.json" % datetime.date.today().strftime("%Y%m%d"))
    if not os.path.exists(bak):
        shutil.copy(PRY, bak)
    hecho = {"copiados": copiados}

    # ---- recursos con el mismo nombre del archivo
    res = d["resources"]["resources"]
    por_nombre = {r["name"]: r for r in res}
    for n in SONIDOS:
        nombre = n + ".ogg"
        r = por_nombre.get(nombre)
        if r is None:
            res.append({"file": REL + nombre, "kind": "audio", "metadata": "", "name": nombre, "userAdded": True})
        else:
            r.update({"file": REL + nombre, "kind": "audio"})
    hecho["recursos"] = len(SONIDOS)

    # ---- 2) módulo en todas las escenas
    modulo = open(os.path.join(AQUI, "sfx.js"), encoding="utf-8").read()
    for L in d["layouts"]:
        ev = L["events"]
        quitar(ev, MK + "-MOD"); quitar(ev, MK + "-TICK"); quitar(ev, MK + "-LISTA")
        k = next((i + 1 for i, e in enumerate(ev) if es_marca(e, "FDIZ-FASE57-APLICAR")), 0)
        nuevos = [js(modulo, MK + "-MOD"), js("if (gdjs.fdizSfx) gdjs.fdizSfx.tick(runtimeScene);", MK + "-TICK")]
        if L["name"] in LISTA:
            nuevos.insert(0, comentario(MK + "-LISTA · Sonidos de sonidos/ (scripts/sfx.js, en cada máquina): " + LISTA[L["name"]]))
        ev[k:k] = nuevos

    # ---- 3) eventos con sonido equivalente
    J = next(l for l in d["layouts"] if l["name"] == "Juego")
    n_c, n_q, n_s = 0, 0, 0
    for L in d["layouts"]:
        quitar_aqui = QUITAR.get(L["name"], [])
        for e in recorrer(L["events"]):
            acts = e.get("actions", [])
            nuevas = []
            for x in acts:
                if x["type"]["value"] == "PlaySound":
                    f = x["parameters"][1]
                    if L["name"] == "Juego" and f in CAMBIAR:
                        x["parameters"][1], x["parameters"][3] = CAMBIAR[f]; n_c += 1
                    elif f in quitar_aqui:
                        n_q += 1; continue
                nuevas.append(x)
                # la salida se abre: además de la sirena, suena la puerta
                if L["name"] == "Juego" and x["type"]["value"] == "PlaySound" and x["parameters"][1] == "efectos/eventos/escape.ogg" and \
                        not any(y["type"]["value"] == "PlaySound" and y["parameters"][1] == "puerta_casillero.ogg" for y in acts):
                    nuevas.append(a("PlaySound", "", "puerta_casillero.ogg", "", "80", "1")); n_s += 1
            if "actions" in e: e["actions"] = nuevas
    hecho.update({"cambiados": n_c, "quitados": n_q, "salida": n_s})

    # ---- jefe_modo.js (fuente y código incrustado)
    p_jefe = os.path.join(AQUI, "jefe_modo.js")
    src = open(p_jefe, encoding="utf-8").read()
    for viejo, nuevo in JEFE:
        src = src.replace(viejo, nuevo)
    open(p_jefe, "w", encoding="utf-8").write(src)
    n_j = 0
    for e in recorrer(J["events"]):
        if e.get("type", "").endswith("JsCode"):
            for viejo, nuevo in JEFE:
                if viejo in e["inlineCode"]:
                    e["inlineCode"] = e["inlineCode"].replace(viejo, nuevo); n_j += 1
    hecho["jefe"] = n_j

    # ---- 4) TODO: pasos y música de tensión (eventos desactivados, listos para activar)
    if not any(v["name"] == "OleadaInicio" for v in J["variables"]):
        J["variables"].append({"name": "OleadaInicio", "type": "number", "value": 0})
    mov = grupo(J["events"], "Movimiento y animación")["events"]
    quitar(mov, MK + "-PASOS")
    paso = {"type": "BuiltinCommonInstructions::ForEach", "object": "Sup", "disabled": True,
            "conditions": [c("VarGlobal", "SonidoActivo", "=", "1"), c("TopDownMovementBehavior::IsMoving", "Sup", "TopDownMovement"),
                           c("CompareObjectTimer", "Sup", '"paso"', ">=", "0.35")],
            "actions": [a("PlaySound", "", "pasos.ogg", "", "70", "RandomFloatInRange(0.9, 1.1)"), a("ResetObjectTimer", "Sup", '"paso"')],
            "events": [], "__fdiz": MK + "-PASOS"}
    mov += [comentario("// TODO: footsteps · " + MK + "-PASOS · Falta el sonido de pasos. Cuando exista: importar pasos.ogg "
                       "(en sonidos/) y activar el evento de abajo (clic derecho > Activar). Un paso cada 0.35 s por jugador "
                       "en movimiento, volumen 70, pitch 0.9-1.1."), paso]
    mus = grupo(J["events"], "Música y sonido de fondo")["events"]
    quitar(mus, MK + "-TENSION")
    tension = std([c("VarScene", "OleadaInicio", "=", "1"), c("VarGlobal", "SonidoActivo", "=", "1")],
                  [a("PlayMusicCanal", "", "musica_tension.ogg", "1", "yes", "45", "1")], apagado=True)
    tension["__fdiz"] = MK + "-TENSION"
    mus += [comentario("// TODO: música de partida / tensión · " + MK + "-TENSION · Falta la música. OleadaInicio vale 1 durante "
                       "un cuadro cuando empieza una oleada (sube la infestación, llega una horda o arranca la cuenta del final). "
                       "Para usarla: importar musica_tension.ogg (y la de partida), y activar el evento de abajo (canal 1, "
                       "volumen 45, en loop). Mientras tanto siguen las músicas sintetizadas de musica/."), tension]
    # el marcador __fdiz no es de GDevelop: se guarda en el comentario y se quita del evento
    for e in recorrer(J["events"]):
        e.pop("__fdiz", None)

    # ---- manifiesto de audio
    pm = os.path.join(PROY, "audio_manifest.json")
    m = json.load(open(pm, encoding="utf-8"))
    ya = {x["path"] for x in m["effects"]}
    for n in SONIDOS:
        if REL + n + ".ogg" not in ya:
            m["effects"].append({"id": "SFX2D_" + n.upper(), "path": REL + n + ".ogg", "priority": "P1"})
    json.dump(m, open(pm, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    json.dump(d, open(PRY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("Fase 60 aplicada:", hecho)


if __name__ == "__main__":
    main()
