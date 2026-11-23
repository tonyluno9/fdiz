"""Fase 68 · MODO HISTORIA de 12 pasos (cinemáticas en video, diálogos con voz, objetivos y checkpoints). Idempotente.

Uso (desde la carpeta fdiz, con GDevelop CERRADO):
    python gdevelop/scripts/fase68_historia.py
    node gdevelop/scripts/prueba_historia2.js          # pruebas de historia.js (sin GDevelop)
Va al final de la cadena (después de fase67). Volver a correrlo:
  * al agregar un video nuevo (C03.mp4 ... C10.mp4) en gdevelop/FDI-Z/assets/historia/video/;
  * al cambiar un audio de gdevelop/FDI-Z/assets/historia/audio/ o los textos de gdevelop/historia/01_DIALOGOS_PARA_VOCES.md;
  * después de volver a correr fase40 (profes.js), fase56 (usar.js), fase64 (dialogo.js) o fase65 (cine.js), porque esta fase
    vuelve a incrustar esos cuatro archivos con sus ganchos para la historia.

Fuentes: gdevelop/historia/02_HISTORIA_PARA_GDEVELOP.md (secuencia) y 01_DIALOGOS_PARA_VOCES.md (textos y nombres de audio).
Lógica: scripts/historia.js (gdjs.fdizHistoria). Datos generados: scripts/historia_datos.js (gdjs.fdizHistoriaDatos).

Qué hace en el proyecto:
  * Recursos: los 55 audios "historia/audio/<archivo>.mp3" y "efectos/eventos/alarma_loop.wav" (se genera si falta);
    un video "vid_hist_<C..>" + objeto "Vid<C..>" por cada archivo que exista en assets/historia/video/. Si no existe C10.mp4,
    VidC10 usa assets/interfaz/videos/15_victoria.mp4 (como pide el documento).
  * Objetos de Juego: HistDib (dibujo), TxtHist (texto) y HistRetrato (copia de HudRetrato). Resultados: TxtHistRes.
  * Variables: globales Historia.{Paso, CinematicasVistas, Armas, Final}; de Juego HistObjX/Y, HistCine(Seq), HistLinea(Seq),
    HistHabla, HistVelo, HistAlarma, HistAyuda y FinalSeg (60 = como siempre; Historia usa 90). Las Hist* viajan en línea.
  * Eventos de Juego: FDIZ-FASE68-DATOS y -MOD (arriba), -TICK (después de la de la fase 65), -TRAS (antes de "Combate: pegar"),
    -FLECHA (la flecha de objetivos apunta a la zona de la historia) y el final ¡Aguanten! con FinalSeg; en Historia la victoria
    y el texto del final los maneja historia.js (paso 12).
  * Menú: elegir HISTORIA empieza la historia desde el paso 1; la tarjeta dice "12 pasos".
  * Resultados: en Historia, "REINTENTAR" tras una derrota (sigue desde el último paso) y la línea final de Tony en la victoria.
"""
import copy, datetime, json, math, os, re, shutil, struct, sys, wave

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
PROY = os.path.join(RAIZ, "gdevelop", "FDI-Z")
PRY = os.path.join(PROY, "FDI-Z.json")
DOC_DIALOGOS = os.path.join(RAIZ, "gdevelop", "historia", "01_DIALOGOS_PARA_VOCES.md")
AUDIO = "assets/historia/audio"
VIDEO = "assets/historia/video"
ALARMA = "efectos/eventos/alarma_loop.wav"
MK = "FDIZ-FASE68"
VIDEOS = ["C01_T1", "C01_T2", "C02", "C03", "C04", "C05", "C06", "C065", "C07", "C08", "C09", "C10"]
VICTORIA = "assets/interfaz/videos/15_victoria.mp4"
VARS = [("HistObjX", -1), ("HistObjY", -1), ("HistCine", ""), ("HistCineSeq", 0), ("HistLinea", ""), ("HistLineaSeq", 0),
        ("HistHabla", ""), ("HistVelo", 0), ("HistAlarma", 0), ("HistAyuda", ""), ("HistDefensa", 0), ("FinalSeg", 60)]
SYNC = ["HistCine", "HistCineSeq", "HistLinea", "HistLineaSeq", "HistHabla", "HistVelo", "HistAlarma", "HistAyuda", "HistObjX", "HistObjY"]
REINCRUSTAR = [("FDIZ-FASE56-MOD", "usar.js"), ("FDIZ-FASE40-MOD", "profes.js"), ("FDIZ-FASE64-MOD", "dialogo.js"), ("FDIZ-FASE65-MOD", "cine.js")]
PJ = {"ALAN": "alan", "MIRANDA": "miranda", "TONY": "tony", "CÉSAR": "cesar", "JOEL": "joel", "JUSTINO": "justino",
      "CANEPA": "canepa", "ALTAVOZ": "altavoz"}


# ------------------------------------------------------------------ datos
def dur_mp3(ruta):
    """Duración de un MP3 (MPEG 1/2/2.5, capa III) sumando sus cuadros. Sin herramientas externas."""
    b = open(ruta, "rb").read()
    i = 0
    if b[:3] == b"ID3":
        i = 10 + ((b[6] & 0x7F) << 21 | (b[7] & 0x7F) << 14 | (b[8] & 0x7F) << 7 | (b[9] & 0x7F))
    BR = {1: [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320],
          2: [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160]}
    SR = {3: [44100, 48000, 32000], 2: [22050, 24000, 16000], 0: [11025, 12000, 8000]}
    seg = 0.0
    while i + 4 <= len(b):
        if b[i] != 0xFF or (b[i + 1] & 0xE0) != 0xE0:
            i += 1
            continue
        ver, capa = (b[i + 1] >> 3) & 3, (b[i + 1] >> 1) & 3
        bri, sri, pad = b[i + 2] >> 4, (b[i + 2] >> 2) & 3, (b[i + 2] >> 1) & 1
        if ver == 1 or capa != 1 or bri in (0, 15) or sri == 3:
            i += 1
            continue
        br = BR[1 if ver == 3 else 2][bri] * 1000
        sr = SR[ver][sri]
        muestras = 1152 if ver == 3 else 576
        largo = (144 if ver == 3 else 72) * br // sr + pad
        if largo < 4:
            i += 1
            continue
        seg += muestras / sr
        i += largo
    return round(seg, 2)


def leer_dialogos():
    """Tabla de 01_DIALOGOS_PARA_VOCES.md -> {id: {pj, txt}} (texto exacto, sin las marcas de énfasis *...*)."""
    out = {}
    for linea in open(DOC_DIALOGOS, encoding="utf-8"):
        m = re.match(r"\|\s*`([A-Za-z0-9_]+)\.mp3`\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", linea)
        if not m:
            continue
        ident, pj, txt = m.group(1), m.group(2).strip().upper(), m.group(3).strip()
        out[ident] = {"pj": PJ.get(pj, pj.lower()), "txt": re.sub(r"\*([^*]+)\*", r"\1", txt)}
    return out


def alarma_wav(ruta):
    """Alarma de dos tonos en bucle (2 s, 44.1 kHz, 16 bits, mono). Placeholder hasta tener una grabada."""
    sr, dur = 44100, 2.0
    n = int(sr * dur)
    datos = bytearray()
    fase = 0.0
    for k in range(n):
        t = k / sr
        f = 880 if (t % 1.0) < 0.5 else 660
        fase += 2 * math.pi * f / sr
        v = 0.55 * math.sin(fase) + 0.25 * math.sin(3 * fase) / 3          # algo de "bocina"
        env = min(1.0, (t % 0.5) / 0.02, (0.5 - (t % 0.5)) / 0.02)       # sin chasquidos en los cambios
        datos += struct.pack("<h", int(max(-1, min(1, v * env)) * 9000))
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with wave.open(ruta, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(bytes(datos))


def datos_historia():
    dl = leer_dialogos()
    carpeta = os.path.join(PROY, *AUDIO.split("/"))
    lineas, faltan = {}, []
    for ident, d in dl.items():
        archivo = ident + ".mp3"
        ruta = os.path.join(carpeta, archivo)
        existe = os.path.exists(ruta)
        if not existe:
            faltan.append(archivo)
        lineas[ident] = {"pj": d["pj"], "txt": d["txt"], "audio": ("historia/audio/" + archivo) if existe else "",
                         "dur": dur_mp3(ruta) if existe else 0}
    cv = os.path.join(PROY, *VIDEO.split("/"))
    en = {f.lower(): f for f in (os.listdir(cv) if os.path.isdir(cv) else [])}
    videos = {}
    for v in VIDEOS:
        f = en.get(v.lower() + ".mp4")
        if f:
            videos[v] = (VIDEO + "/" + f)
        elif v == "C10" and os.path.exists(os.path.join(PROY, *VICTORIA.split("/"))):
            videos[v] = VICTORIA
    return lineas, faltan, videos


# ------------------------------------------------------------------ utilidades del proyecto
def c(tipo, *p, inv=False):
    return {"type": {"inverted": inv, "value": tipo}, "parameters": list(p)}


def a(tipo, *p):
    return {"type": {"value": tipo}, "parameters": list(p)}


def std(conds, acts, sub=()):
    return {"type": "BuiltinCommonInstructions::Standard", "conditions": conds, "actions": acts, "events": list(sub)}


def js(code, marca):
    return {"type": "BuiltinCommonInstructions::JsCode", "inlineCode": "/*" + marca + "*/\n" + code,
            "parameterObjects": "", "useStrict": True, "eventsSheetExpanded": False}


def comentario(t):
    return {"type": "BuiltinCommonInstructions::Comment", "color": {"b": 109, "g": 230, "r": 255, "textB": 0, "textG": 0, "textR": 0},
            "comment": t, "comment2": ""}


def recorrer(lst):
    for e in lst:
        yield e
        yield from recorrer(e.get("events", []))


def es_js(e, marca):
    return e.get("type", "").endswith("JsCode") and e.get("inlineCode", "").startswith("/*" + marca + "*/")


def quitar(lst, pred):
    lst[:] = [e for e in lst if not pred(e)]
    for e in lst:
        if e.get("events"):
            quitar(e["events"], pred)


def es_coment(e, marca):
    return e.get("type", "").endswith("Comment") and e.get("comment", "").startswith(marca)


def tiene(e, tipo, params):
    return any(x["type"]["value"] == tipo and x["parameters"][:len(params)] == params for x in e.get("conditions", []) + e.get("actions", []))


def grupo(ev, nombre):
    return next(e for e in ev if e["type"].endswith("Group") and e.get("name") == nombre)


def asegura_var(lista, nombre, valor):
    if not any(v["name"] == nombre for v in lista):
        lista.append({"name": nombre, "type": "string" if isinstance(valor, str) else "number", "value": valor})


HIST = ["Modo", "=", '"historia"']
NOHIST = c("VarGlobalTxt", "Modo", "!=", '"historia"')


def sin_hist(e):
    if not any(x["type"]["value"] == "VarGlobalTxt" and x["parameters"][:3] == ["Modo", "!=", '"historia"'] for x in e["conditions"]):
        e["conditions"].append(copy.deepcopy(NOHIST))


# ------------------------------------------------------------------ main
def main():
    d = json.load(open(PRY, encoding="utf-8"))
    resp = os.path.join(RAIZ, "gdevelop", "respaldos")
    os.makedirs(resp, exist_ok=True)
    bak = os.path.join(resp, "antes_de_fase68_%s.json" % datetime.date.today().strftime("%Y%m%d"))
    if not os.path.exists(bak):
        shutil.copy(PRY, bak)

    # datos y archivo JS de datos
    lineas, faltan, videos = datos_historia()
    if not os.path.exists(os.path.join(PROY, *ALARMA.split("/"))):
        alarma_wav(os.path.join(PROY, *ALARMA.split("/")))
    obj_vid = {v: "Vid" + v for v in videos}
    datos_js = ("/* GENERADO por scripts/fase68_historia.py desde gdevelop/historia/01_DIALOGOS_PARA_VOCES.md y los audios y videos de\n"
                " * gdevelop/FDI-Z/assets/historia/. No editar a mano. dur = segundos del audio. videos = objeto de video de cada cinemática\n"
                " * que existe (las que faltan usan pantalla negra 1 s). */\n"
                "gdjs.fdizHistoriaDatos = " + json.dumps({"lineas": lineas, "videos": obj_vid}, ensure_ascii=False, indent=1) + ";\n")
    open(os.path.join(AQUI, "historia_datos.js"), "w", encoding="utf-8", newline="\n").write(datos_js)

    # recursos
    res = d["resources"]["resources"]
    nombres = {r["name"] for r in res}
    for ident, L in lineas.items():
        if L["audio"] and L["audio"] not in nombres:
            res.append({"file": AUDIO + "/" + ident + ".mp3", "kind": "audio", "metadata": "", "name": L["audio"],
                        "preloadAsMusic": False, "preloadAsSound": True, "preloadInCache": False, "userAdded": True})
    if ALARMA not in nombres:
        res.append({"file": ALARMA, "kind": "audio", "metadata": "", "name": ALARMA,
                    "preloadAsMusic": False, "preloadAsSound": True, "preloadInCache": False, "userAdded": True})
    d["resources"]["resources"] = res = [r for r in res if not r["name"].startswith("vid_hist_")]
    J = next(l for l in d["layouts"] if l["name"] == "Juego")
    J["objects"] = [o for o in J["objects"] if not (o["name"].startswith("VidC") and o["type"] == "Video::VideoObject")]
    for v, ruta in videos.items():
        res.append({"file": ruta, "kind": "video", "metadata": "", "name": "vid_hist_" + v, "userAdded": True})
        J["objects"].append({"assetStoreId": "", "name": "Vid" + v, "type": "Video::VideoObject", "variables": [], "effects": [],
                             "behaviors": [], "content": {"opacity": 255, "loop": False, "volume": 100, "videoResource": "vid_hist_" + v}})
    ob = {o["name"]: o for o in J["objects"]}
    if "HistDib" not in ob:
        t = copy.deepcopy(ob["ProfDib"]); t["name"] = "HistDib"; J["objects"].append(t)
    if "HistRetrato" not in ob:   # retrato propio (los eventos del HUD mueven todas las instancias de HudRetrato)
        t = copy.deepcopy(ob["HudRetrato"]); t["name"] = "HistRetrato"; t["variables"] = []; J["objects"].append(t)
    if "TxtHist" not in ob:
        t = copy.deepcopy(ob["TxtDialogo"]); t["name"] = "TxtHist"; J["objects"].append(t)
    for n, v in VARS:
        asegura_var(J["variables"], n, v)

    # variable global Historia (estructura)
    g = next((v for v in d["variables"] if v["name"] == "Historia"), None)
    if g is None:
        g = {"name": "Historia", "type": "structure", "children": []}
        d["variables"].append(g)
    for n, v in [("Paso", 0), ("CinematicasVistas", ""), ("Armas", ""), ("Final", 0)]:
        asegura_var(g["children"], n, v)

    # sincronización en línea (lista de variables de escena del núcleo de red)
    T = next(l for l in d["layouts"] if l["name"] == "Titulo")
    nucleo = next(e for e in recorrer(T["events"]) if e.get("type", "").endswith("JsCode") and "gdjs.fdizNetCfg=" in e["inlineCode"])
    code = nucleo["inlineCode"]
    m = re.search(r"gdjs\.fdizNetCfg=", code)
    cfg, fin = json.JSONDecoder().raw_decode(code, m.end())
    for n in SYNC:
        if n not in cfg["sv"]:
            cfg["sv"].append(n)
    nucleo["inlineCode"] = code[:m.end()] + json.dumps(cfg, ensure_ascii=False) + code[fin:]

    # módulos con ganchos para la historia (se vuelven a incrustar tal cual el archivo)
    for marca, archivo in REINCRUSTAR:
        src = open(os.path.join(AQUI, archivo), encoding="utf-8").read()
        hechos = 0
        for e in recorrer(J["events"]):
            if es_js(e, marca):
                e["inlineCode"] = "/*" + marca + "*/\n" + src
                hechos += 1
        if hechos != 1:
            sys.exit("No encontré (una vez) el evento " + marca)

    ev = J["events"]
    quitar(ev, lambda e: any(es_js(e, MK + s) for s in ("-DATOS", "-MOD", "-TICK", "-TRAS")))
    k = next(i for i, e in enumerate(ev) if es_js(e, "FDIZ-FASE65-MOD"))
    ev.insert(k + 1, js(datos_js, MK + "-DATOS"))
    ev.insert(k + 2, js(open(os.path.join(AQUI, "historia.js"), encoding="utf-8").read(), MK + "-MOD"))
    k = next(i for i, e in enumerate(ev) if es_js(e, "FDIZ-FASE65-TICK"))
    ev.insert(k + 1, js("if (gdjs.fdizHistoria) gdjs.fdizHistoria.tick(runtimeScene);", MK + "-TICK"))
    k = next(i for i, e in enumerate(ev) if e["type"].endswith("Group") and e.get("name") == "Combate: pegar")
    ev.insert(k, js("if (gdjs.fdizHistoria) gdjs.fdizHistoria.tras(runtimeScene);", MK + "-TRAS"))

    # flecha de objetivos: en Historia apunta a la zona del paso (HistObjX / HistObjY)
    G = grupo(ev, "Objetivos y flecha")["events"]
    quitar(G, lambda e: es_coment(e, MK + "-FLECHA") or (e.get("type", "").endswith("Standard") and tiene(e, "ModVarScene", ["ObjX", "=", "Variable(HistObjX)"])))
    k = next(i for i, e in enumerate(G) if e.get("type", "").endswith("Standard") and tiene(e, "ModVarScene", ["ObjX", "=", "-1"]))
    G[k + 1:k + 1] = [comentario(MK + "-FLECHA · Historia (fase 68): la flecha apunta a la zona del paso actual (historia.js)."),
                      std([c("VarGlobal", "NetRol", "!=", "2"), c("VarGlobalTxt", *HIST), c("VarScene", "HistObjX", ">=", "0")],
                          [a("ModVarScene", "ObjX", "=", "Variable(HistObjX)"), a("ModVarScene", "ObjY", "=", "Variable(HistObjY)")])]
    # en Historia el sistema de objetivos de Escape queda quieto hasta la defensa del autobús (paso 11): sin esto, en el primer
    # cuadro crearía su primera misión antes de que historia.js tome el control
    quitar(G, lambda e: es_coment(e, MK + "-OBJ") or (e.get("type", "").endswith("Standard") and tiene(e, "VarScene", ["HistDefensa", "=", "0"])))
    k = next(i for i, e in enumerate(G) if e.get("type", "").endswith("Standard") and tiene(e, "DepartScene", [""]) and tiene(e, "ModVarScene", ["ObjNum", "=", "1"]))
    G[k + 1:k + 1] = [comentario(MK + "-OBJ · Historia (fase 68): sin objetivos de Escape; el final ¡Aguanten! se activa en el paso 11 (HistDefensa = 1)."),
                      std([c("VarGlobal", "NetRol", "!=", "2"), c("VarGlobalTxt", *HIST), c("VarScene", "HistDefensa", "=", "0")],
                          [a("ModVarScene", "ObjNum", "=", "0"), a("ModVarScene", "ObjIni", "=", "1"), a("ModVarScene", "ObjTotal", "=", "0"),
                           a("ModVarSceneTxt", "ObjTipo", "=", '""')])]
    # texto del final: en Historia lo escribe historia.js ("Protege a Canepa: 1:30"); en los demás, con FinalSeg
    for e in recorrer(G):
        for x in e.get("actions", []):
            if x["type"]["value"] == "TextObject::String" and "El camión arranca en" in x["parameters"][-1]:
                x["parameters"][-1] = x["parameters"][-1].replace("ceil(60 - TimerElapsedTime", "ceil(Variable(FinalSeg) - TimerElapsedTime")
                sin_hist(e)
        if tiene(e, "VarSceneTxt", ["ObjTipo", "=", '"final"']) and any(x["type"]["value"] == "TextObject::String" for x in e.get("actions", [])):
            sin_hist(e)
    # final ¡Aguanten!: dura FinalSeg (60 como siempre; 90 en Historia) y en Historia la victoria es el paso 12
    F = grupo(ev, "Final ¡Aguanten!")["events"]
    vic = next(e for e in F if tiene(e, "ModVarSceneTxt", ["Estado", "=", '"victoria"']))
    for x in vic["conditions"]:
        if x["type"]["value"] == "CompareTimer" and x["parameters"][1] == '"final"':
            x["parameters"][3] = "Variable(FinalSeg)"
    sin_hist(vic)

    # Menú: HISTORIA empieza desde el paso 1; la tarjeta dice 12 pasos
    M = next(l for l in d["layouts"] if l["name"] == "Menu")
    sel = [e for e in recorrer(M["events"]) if tiene(e, "VarScene", ["Sel", "=", "2"]) and tiene(e, "ModVarGlobalTxt", ["Modo", "=", '"historia"'])]
    if not sel:
        sys.exit("No encontré la elección de HISTORIA en el Menú")
    reinicio = ("const h = runtimeScene.getGame().getVariables().get(\"Historia\");\n"
                "h.getChild(\"Paso\").setNumber(0); h.getChild(\"CinematicasVistas\").setString(\"\"); h.getChild(\"Armas\").setString(\"\"); h.getChild(\"Final\").setNumber(0);")
    for e in sel:
        quitar(e.setdefault("events", []), lambda x: es_js(x, MK + "-MENU"))
        e["events"].append(js("// Historia (fase 68): partida nueva desde el paso 1\n" + reinicio, MK + "-MENU"))
    for e in recorrer(M["events"]):
        for x in e.get("actions", []):
            if x["type"]["value"] == "TextObject::String" and x["parameters"][0] == "TxtCapB":
                x["parameters"][-1] = x["parameters"][-1].replace("6 misiones en orden · 1 a 4 jugadores", "12 pasos con cinemáticas · 1 a 4 jugadores") \
                    .replace("1 a 4 jugadores + bots · 6 misiones", "1 a 4 jugadores + bots · 12 pasos")

    # Resultados: REINTENTAR (desde el último paso) y la última línea de Tony en la victoria
    R = next(l for l in d["layouts"] if l["name"] == "Resultados")
    ro = {o["name"]: o for o in R["objects"]}
    if "TxtHistRes" not in ro:
        t = copy.deepcopy(ro["TxtDet"]); t["name"] = "TxtHistRes"; R["objects"].append(t)
    quitar(R["events"], lambda e: es_js(e, MK + "-RES"))
    # corrección (todos los modos): REINICIAR usaba if(...), que GDevelop no tiene: el código generado cambiaba a la escena "".
    # Está dentro de la rama NetRol = 0, así que el valor siempre era "Juego".
    for e in recorrer(R["events"]):
        for x in e.get("actions", []):
            if x["type"]["value"] == "Scene" and any('if(GlobalVariable(NetRol) > 0, "Online", "Juego")' in str(p) for p in x["parameters"]):
                x["parameters"] = [('"Juego"' if 'if(GlobalVariable(NetRol)' in str(p) else p) for p in x["parameters"]]
    c10 = lineas.get("C10_03_tony", {})
    res_js = """// Historia (fase 68): tras una derrota se reintenta desde el último paso; en la victoria, la última línea de Tony.
const scn = runtimeScene, G = scn.getGame().getVariables();
if (G.get("Modo").getAsString() === "historia") {
  const st = scn._fdizHistRes || (scn._fdizHistRes = { t0: Date.now() / 1000, dicho: false, txt: null });
  const H = G.get("Historia"), vic = G.get("Resultado").getAsString() === "victoria";
  if (!vic) for (const b of scn.getObjects("TxtBtnRei") || []) { if (b.getString() !== "REINTENTAR") b.setString("REINTENTAR"); b.setX(340 - b.getWidth() / 2); }
  if (!st.txt) { const t = scn.createObject("TxtHistRes"); if (t) { t.setLayer(""); t.setZOrder(500); t.hide(true); } st.txt = t; }
  const T = st.txt;
  if (T && !vic && H.getChild("Paso").getAsNumber() > 1) {
    const s = "Seguirán desde el paso " + H.getChild("Paso").getAsNumber() + " de 12";
    if (T.getString() !== s) T.setString(s); T.hide(false); T.setCharacterSize(24); T.setPosition(340 - T.getWidth() / 2, 560);
  }
  const t = Date.now() / 1000 - st.t0;
  if (vic && H.getChild("Final").getAsNumber() === 1 && t >= 1.2 && !st.dicho) {
    st.dicho = true; H.getChild("Final").setNumber(0);
    try { if (G.get("SonidoActivo").getAsNumber() === 1) gdjs.evtTools.sound.playSoundOnChannel(scn, %s, 8, false, 100, 1); } catch (e) { /* sin voz */ }
    st.hasta = Date.now() / 1000 + %s;
  }
  if (T && vic) {
    const ver = st.dicho && Date.now() / 1000 < st.hasta;
    T.hide(!ver);
    if (ver) { const s = "TONY: «%s»"; if (T.getString() !== s) T.setString(s); T.setCharacterSize(30); T.setPosition(960 - T.getWidth() / 2, 900); }
  }
}""" % (json.dumps(c10.get("audio", "")), max(4.5, (c10.get("dur") or 2) + 3), c10.get("txt", "… Lo logramos.").replace('"', '\\"'))
    R["events"].append(js(res_js, MK + "-RES"))

    # manifiesto de audio: la alarma (efecto)
    man_ruta = os.path.join(PROY, "audio_manifest.json")
    man = json.load(open(man_ruta, encoding="utf-8"))
    if not any(e["path"] == ALARMA for e in man["effects"]):
        man["effects"].append({"id": "SFX_EVENTO_ALARMA_LOOP", "path": ALARMA, "priority": "P2"})
        open(man_ruta, "w", encoding="utf-8", newline="\n").write(json.dumps(man, ensure_ascii=False, indent=2) + "\n")

    # LEEME de los videos
    cv = os.path.join(PROY, *VIDEO.split("/"))
    os.makedirs(cv, exist_ok=True)
    lee = ["Cinemáticas del modo Historia (fase 68). MP4 (H.264), 16:9, con su propia música y efectos (sin voces).",
           "Nombres exactos: " + ", ".join(v + ".mp4" for v in VIDEOS) + ".",
           "Al copiar un video nuevo, correr con GDevelop cerrado:  python gdevelop/scripts/fase68_historia.py",
           "Las que falten se reemplazan con pantalla negra 1 s + los diálogos de esa escena.", ""]
    for v in VIDEOS:
        lee.append("%-10s %s" % (v + ".mp4", "OK" if videos.get(v, "").startswith(VIDEO) else ("(usa 15_victoria.mp4)" if v in videos else "FALTA")))
    open(os.path.join(cv, "LEEME.txt"), "w", encoding="utf-8", newline="\n").write("\n".join(lee) + "\n")

    tmp = PRY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=2))
    os.replace(tmp, PRY)
    print("Fase 68 aplicada. Líneas: %d (sin audio: %s). Videos: %s" % (len(lineas), faltan or "ninguna",
          ", ".join("%s%s" % (v, "" if p.startswith(VIDEO) else "=15_victoria") for v, p in videos.items()) or "ninguno"))


if __name__ == "__main__":
    main()
