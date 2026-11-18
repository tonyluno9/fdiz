"""Fase 40 · Profesores reclutables (Joel, Justino y Canepa). Idempotente.

Uso (con GDevelop cerrado, desde la carpeta fdiz):
    python gdevelop/scripts/fase40_sprites_profes.py     # solo si cambiaron los GIF o el arte zombi
    python gdevelop/scripts/fase40_profesores.py

Va al FINAL de la cadena de parches (después de fase39). Si se vuelve a correr fase25_online.py (re-incrusta net_core.js
y la configuración de red) o cualquier fase anterior, hay que volver a correr este script.

Qué hace en FDI-Z.json:
  * Sup: animaciones joel_* / justino_* / canepa_* (los profes reclutados son un "Sup" bot más, Jugador 5/6/7).
  * Profe: un solo objeto para los tres profes que esperan (variable Nombre); se quita el objeto Canepa.
    Una instancia de cada uno: Joel en su lugar de cómputo/CIC, Justino en la nevería (lado interior de la barra),
    Canepa junto al camión.
  * ZJoel / ZJustino / ZCanepa: versión zombi (grupo Zombies) con la vida base de ZConserje.
  * Objetos de interfaz TxtProfe, ProfPanel y ProfDib; variables de escena Prof<Nombre>, Prof<Nombre>Seg y ProfDlg.
  * Eventos: módulo profes.js, grupo "Profesores reclutables" (reemplaza "Rescates: Joel y Justino"), ganchos en
    Entrada, Bots, Vida/caída, Compañeros mordidos; filtros Jugador <= 4 donde la lógica es solo de los 4 principales.
  * Red: objetos/variables nuevos en la configuración de sincronía y mensaje "prof" en net_core.js.
"""
import json, os, sys, glob, copy, shutil, re, datetime, uuid

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
SPR = os.path.join(RAIZ, "generado", "sprites")
REL = "../../generado/sprites/"
MK = "FDIZ-FASE40"

# ------------------------------------------------------------------ configuración (documentada en BITACORA, Fase 40)
PROFES = ["joel", "justino", "canepa"]
POS = {"joel": (3616, 2000),      # placeholder original, Cubículos CIC (zona de cómputo)
       "justino": (1936, 1668),   # nevería: lado interior de la pata de la barra en L, bajo el congelador (ver BITACORA: la franja de atrás está cerrada)
       "canepa": (544, 3328)}     # junto al camión (marcador "canepa" del mapa)
ZOMBI = {"joel": "ZJoel", "justino": "ZJustino", "canepa": "ZCanepa"}
Z_DANIO = 12        # ZNormal 5 · ZConserje 14
Z_VELOCIDAD = 84    # ZNormal 99 · ZConserje 72
Z_ORO = 5           # como ZConserje (solo cuenta para el Jefe)

ANIM_SUP = {  # animación del juego -> (carpeta en generado/sprites/profes/<profe>/, s por cuadro, se repite)
    "quieto": ("quieto", 0.16, True), "caminar_abajo": ("caminar_abajo", 0.1, True), "caminar_arriba": ("caminar_arriba", 0.1, True),
    "caminar_lado": ("caminar_lado", 0.1, True), "pegar_lado": ("pegar_lado", 0.07, False), "pegar_abajo": ("pegar_abajo", 0.07, False),
    "pegar_arriba": ("pegar_arriba", 0.07, False), "caer_levantarse": ("caer_levantarse", 0.1, False),
    "festejo": ("quieto", 0.16, True), "habilidad": ("quieto", 0.16, False), "especial": ("quieto", 0.16, False),
}
# Arte real de 4 cuadros por animación (ver fase40_sprites_profes.py): caminar 0.72 s por ciclo (los zombis
# normales, 7 x 0.125 = 0.875 s), ataque 0.48 s, golpe final 0.6 s.
ANIM_Z = {"caminar_abajo": (0.18, True), "caminar_arriba": (0.18, True), "caminar_lado": (0.18, True), "atacar_lado": (0.12, False),
          "atacar_abajo": (0.12, False), "atacar_arriba": (0.12, False), "golpe_morir": (0.15, False)}

NOCLI = {"type": {"inverted": False, "value": "VarGlobal"}, "parameters": ["NetRol", "!=", "2"]}


def c(tipo, *p, inv=False):
    return {"type": {"inverted": inv, "value": tipo}, "parameters": list(p)}


def js(code, marca, objetos=""):
    return {"type": "BuiltinCommonInstructions::JsCode", "inlineCode": "/*" + marca + "*/\n" + code,
            "parameterObjects": objetos, "useStrict": True, "eventsSheetExpanded": False}


def std(conds, acts, sub=()):
    return {"type": "BuiltinCommonInstructions::Standard", "conditions": conds, "actions": acts, "events": list(sub)}


def comentario(t):
    return {"type": "BuiltinCommonInstructions::Comment", "color": {"b": 109, "g": 230, "r": 255, "textB": 0, "textG": 0, "textR": 0},
            "comment": t, "comment2": ""}


def tiene_marca(e, marca):
    if e["type"].endswith("JsCode") and e.get("inlineCode", "").startswith("/*" + marca):
        return True
    if e["type"].endswith("Comment") and e.get("comment", "").startswith(marca):
        return True
    return any(tiene_marca(x, marca) for x in e.get("events", []))


def quitar(lst, marca):
    """Quita de la lista los eventos con la marca (el JsCode o el Standard que lo envuelve). Solo para ganchos propios
    insertados directamente en esa lista: no usar con listas cuyos hijos contienen otros eventos del juego."""
    lst[:] = [e for e in lst if not (tiene_marca(e, marca) and len(list(recorrer([e]))) <= 2)]


def recorrer(lst):
    for e in lst:
        yield e
        yield from recorrer(e.get("events", []))


def grupo(ev, nombre):
    return next(e for e in ev if e["type"].endswith("Group") and e.get("name") == nombre)


def var(nombre, valor):
    t = "string" if isinstance(valor, str) else "number"
    return {"name": nombre, "type": t, "value": valor}


def asegura_var(lista, nombre, valor):
    for v in lista:
        if v["name"] == nombre:
            return v
    v = var(nombre, valor)
    lista.append(v)
    return v


# ------------------------------------------------------------------ sprites -> animaciones
def cuadros(carpeta):
    return sorted(glob.glob(os.path.join(SPR, carpeta, "*_[0-9][0-9].png")))


def recurso(d, ruta_abs):
    rel = os.path.relpath(ruta_abs, SPR).replace("\\", "/")
    nombre = rel
    if not any(r["name"] == nombre for r in d["resources"]["resources"]):
        d["resources"]["resources"].append({"file": REL + rel, "kind": "image", "metadata": "", "name": nombre,
                                            "smoothed": False, "userAdded": True})
    return nombre


def animacion(d, nombre, archivos, seg, loop, mascara):
    """Origen en los pies (centro, 2 px sobre el borde inferior) y máscara rectangular en los pies."""
    from PIL import Image
    sprites = []
    for f in archivos:
        w, h = Image.open(f).size
        ox, oy = w // 2, h - 2
        mx, my = mascara
        sprites.append({"hasCustomCollisionMask": True, "image": recurso(d, f), "points": [],
                        "originPoint": {"name": "origine", "x": ox, "y": oy},
                        "centerPoint": {"automatic": True, "name": "centre", "x": 0, "y": 0},
                        "customCollisionMask": [[{"x": ox - mx, "y": oy - my}, {"x": ox + mx, "y": oy - my},
                                                 {"x": ox + mx, "y": oy}, {"x": ox - mx, "y": oy}]]})
    return {"name": nombre, "useMultipleDirections": False,
            "directions": [{"looping": loop, "timeBetweenFrames": seg, "sprites": sprites}]}


def main():
    d = json.load(open(PRY, encoding="utf-8"))
    hoy = datetime.date.today().strftime("%Y%m%d")
    resp = os.path.join(AQUI, "..", "respaldos")
    os.makedirs(resp, exist_ok=True)
    bak = os.path.join(resp, "antes_de_fase40_%s.json" % hoy)
    if not os.path.exists(bak) and not any(f.startswith("antes_de_fase40_") for f in os.listdir(resp)):
        shutil.copy(PRY, bak)

    J = next(l for l in d["layouts"] if l["name"] == "Juego")
    TI = next(l for l in d["layouts"] if l["name"] == "Titulo")
    ob = {o["name"]: o for o in J["objects"]}
    ev = J["events"]

    # ---------------- recursos huérfanos de corridas anteriores (cuadros que ya no existen)
    d["resources"]["resources"] = [r for r in d["resources"]["resources"]
                                   if not (r["file"].startswith(REL + "profes/") or r["file"].startswith(REL + "zombies/profe_"))
                                   or os.path.exists(os.path.join(SPR, r["file"][len(REL):]))]

    # ---------------- Sup: animaciones de los profes aliados
    sup = ob["Sup"]
    sup["animations"] = [a for a in sup["animations"] if a["name"].split("_")[0] not in PROFES]
    for p in PROFES:
        for an, (src, seg, loop) in ANIM_SUP.items():
            fs = cuadros("profes/%s/%s" % (p, src))
            if not fs:
                sys.exit("Faltan cuadros de %s/%s: corre primero fase40_sprites_profes.py" % (p, src))
            sup["animations"].append(animacion(d, "%s_%s" % (p, an), fs, seg, loop, (20, 16)))

    # ---------------- Profe: objeto único para los profes que esperan; se quita Canepa
    prof = ob["Profe"]
    prof["animations"] = [animacion(d, p + "_quieto", cuadros("profes/%s/quieto" % p), 0.16, True, (20, 16)) for p in PROFES]
    prof["variables"] = [var("Nombre", ""), var("Estado", "espera"), var("Progreso", 0), var("Vida", 100)]
    if "Canepa" in ob:
        J["objects"] = [o for o in J["objects"] if o["name"] != "Canepa"]
        for g in J.get("objectsGroups", []):
            g["objects"] = [x for x in g["objects"] if x["name"] != "Canepa"]
    J["instances"] = [i for i in J["instances"] if i["name"] not in ("Canepa", "Profe")]
    for p in PROFES:
        x, y = POS[p]
        J["instances"].append({"angle": 0, "customSize": False, "height": 0, "layer": "Juego", "name": "Profe",
                               "persistentUuid": str(uuid.uuid5(uuid.NAMESPACE_URL, "fdiz-profe-" + p)), "width": 0,
                               "x": x, "y": y, "zOrder": y, "numberProperties": [], "stringProperties": [],
                               "initialVariables": [var("Nombre", p), var("Estado", "espera")]})

    # ---------------- zombis de los profes (vida base de ZConserje; DifOk aplica la dificultad una sola vez)
    cons = ob["ZConserje"]
    vida_cons = next(v["value"] for v in cons["variables"] if v["name"] == "Vida")
    J["objects"] = [o for o in J["objects"] if o["name"] not in ZOMBI.values()]
    zg = next(g for g in J["objectsGroups"] if g["name"] == "Zombies")
    for p, zn in ZOMBI.items():
        z = copy.deepcopy(cons)
        z["name"] = zn
        for v in z["variables"]:
            if v["name"] == "Tipo": v["value"] = "profe_" + p
            if v["name"] in ("Vida", "VidaMax"): v["value"] = vida_cons
            if v["name"] == "Danio": v["value"] = Z_DANIO
            if v["name"] == "Velocidad": v["value"] = Z_VELOCIDAD
            if v["name"] == "Oro": v["value"] = Z_ORO
            if v["name"] == "Estado": v["value"] = "persigue"
        for b in z["behaviors"]:
            if b["type"].startswith("PathfindingBehavior"): b["maxSpeed"] = Z_VELOCIDAD
        z["animations"] = []
        for an, (seg, loop) in ANIM_Z.items():
            fs = cuadros("zombies/profe_%s/%s" % (p, an))
            if not fs:
                sys.exit("Faltan cuadros de zombies/profe_%s/%s: corre fase40_sprites_profes.py" % (p, an))
            z["animations"].append(animacion(d, an, fs, seg, loop, (16, 14)))
        J["objects"].append(z)
        if not any(x["name"] == zn for x in zg["objects"]):
            zg["objects"].append({"name": zn})
    ob = {o["name"]: o for o in J["objects"]}

    # ---------------- objetos de interfaz
    J["objects"] = [o for o in J["objects"] if o["name"] not in ("TxtProfe", "ProfPanel", "ProfDib")]
    t = copy.deepcopy(ob["TxtAyuda"]); t["name"] = "TxtProfe"; t["variables"] = []
    pnl = copy.deepcopy(ob["FondoTxt"]); pnl["name"] = "ProfPanel"
    dib = copy.deepcopy(ob["JfDibB"]); dib["name"] = "ProfDib"; dib["clearBetweenFrames"] = True; dib["outlineSize"] = 0
    J["objects"] += [t, pnl, dib]
    ob = {o["name"]: o for o in J["objects"]}

    # ---------------- variables de escena
    for p in PROFES:
        n = "Prof" + p.capitalize()
        asegura_var(J["variables"], n, "espera")["value"] = "espera"
        asegura_var(J["variables"], n + "Seg", 0)
    asegura_var(J["variables"], "ProfDlg", 0)

    # ================================================================ eventos
    modulo = open(os.path.join(AQUI, "profes.js"), encoding="utf-8").read()
    quitar(ev, MK + "-MOD")
    ev.insert(0, js(modulo, MK + "-MOD"))

    # entrada: quien está en el diálogo no se mueve (después de FASE25-INPUT)
    quitar(ev, MK + "-INPUT")
    i = next(k for k, e in enumerate(ev) if tiene_marca(e, "FDIZ-FASE25-INPUT"))
    ev.insert(i + 1, std([copy.deepcopy(NOCLI)], [], [js("if (gdjs.fdizProfes) gdjs.fdizProfes.input(runtimeScene);", MK + "-INPUT")]))

    # grupo de rescates anterior -> grupo nuevo (sin compuerta de red: también dibuja la interfaz en los clientes)
    ev[:] = [e for e in ev if not (e["type"].endswith("Group") and e.get("name") in ("Rescates: Joel y Justino", "Profesores reclutables"))]
    fin_idx = next(k for k, e in enumerate(ev) if e["type"].endswith("Group") and e.get("name") == "Final ¡Aguanten!")
    ev.insert(fin_idx + 1, {
        "type": "BuiltinCommonInstructions::Group", "colorB": 120, "colorG": 200, "colorR": 90, "creationTime": 0,
        "name": "Profesores reclutables", "source": "", "parameters": [], "events": [
            comentario(MK + " · Joel, Justino y Canepa esperan inmunes; con Usar se abre el diálogo (Ayudar / Dejarlo aquí). "
                       "Aceptar: aliado bot (Jugador 5-7). Rechazar: 30 s de juego y se convierte en zombi. Lógica en scripts/profes.js."),
            js("if (gdjs.fdizProfes) gdjs.fdizProfes.tick(runtimeScene);", MK + "-TICK")]})

    # final: el camión ya no anima ni crea a Canepa (lo hace profes.js solo si es aliado y está ahí)
    for e in recorrer(grupo(ev, "Final ¡Aguanten!")["events"]):
        if "actions" in e:
            e["actions"] = [a for a in e["actions"] if not (a["type"]["value"] == "SetAnimationName" and a["parameters"][:1] == ["Canepa"])]

    # bots: Canepa va al camión durante el final (después de repartir BotX/BotY)
    gb = grupo(ev, "Bots")["events"]
    quitar(gb, MK + "-BOTSDEST")
    i = next(k for k, e in enumerate(gb) if tiene_marca(e, "FDIZ-FASE26-BOTS"))
    gb.insert(i + 1, js("if (gdjs.fdizProfes) gdjs.fdizProfes.botsDestino(runtimeScene);", MK + "-BOTSDEST"))
    # distancia a la que se detiene cada bot: 90 + 45·Jugador (P2..P4); profes 5/6/7 -> 150/195/240 en vez de 315/360/405
    viejo = "90 + 45 * Sup.Variable(Jugador)"
    nuevo = "90 + 45 * Sup.Variable(Jugador) - 165 * sign(max(0, Sup.Variable(Jugador) - 4))"
    for e in recorrer(gb):
        for x in e.get("conditions", []):
            x["parameters"] = [p.replace(nuevo, viejo).replace(viejo, nuevo) if isinstance(p, str) else p for p in x["parameters"]]

    gcm = grupo(ev, "Bots: curar mordidos")["events"]
    quitar(gcm, MK + "-BOTS")
    gcm.append(std([copy.deepcopy(NOCLI)], [], [js("if (gdjs.fdizProfes) gdjs.fdizProfes.bots(runtimeScene);", MK + "-BOTS")]))

    # vida: un profe que mantiene Usar revive a quien esté caído junto a él (antes de sumar Revivir)
    gv = grupo(ev, "Vida, caída y revivir")["events"]
    quitar(gv, MK + "-AYUDA")
    i = next(k for k, e in enumerate(gv) if any(a["type"]["value"] == "ModVarObjet" and a["parameters"][:3] == ["Sup", "Revivir", "+"]
                                               for a in e.get("actions", [])))
    gv.insert(i, std([copy.deepcopy(NOCLI)], [], [js("if (gdjs.fdizProfes) gdjs.fdizProfes.ayuda(runtimeScene);", MK + "-AYUDA")]))
    # derrota: solo cuentan los 4 personajes principales de pie
    for e in gv:
        if any(a["type"]["value"] == "ModVarScene" and a["parameters"][:1] == ["Vivos"] and "PickedInstancesCount" in a["parameters"][2]
               for a in e.get("actions", [])):
            if not any(x["type"]["value"] == "VarObjet" and x["parameters"][:2] == ["Sup", "Jugador"] for x in e["conditions"]):
                e["conditions"].append(c("VarObjet", "Sup", "Jugador", "<=", "4"))

    # mordidas: los profes tienen su propio aviso (con nombre); los ciclos M1..M4 aceptan cura de un profe
    gm = grupo(ev, "Compañeros mordidos: salvar o no salvar")["events"]
    quitar(gm, MK + "-MORD")
    gm.insert(0, std([copy.deepcopy(NOCLI)], [], [js("if (gdjs.fdizProfes) gdjs.fdizProfes.mordidas(runtimeScene);", MK + "-MORD")]))
    for e in recorrer(gm):
        cs = e.get("conditions", [])
        if any(x["type"]["value"] == "BuiltinCommonInstructions::CompareNumbers" and "RandomFloat" in x["parameters"][0] for x in cs) \
                and any(a["type"]["value"] == "ModVarObjet" and a["parameters"][:2] == ["Sup", "Mordido"] for a in e.get("actions", [])):
            if not any(x["type"]["value"] == "VarObjet" and x["parameters"][:2] == ["Sup", "Jugador"] for x in cs):
                cs.append(c("VarObjet", "Sup", "Jugador", "<=", "4"))
    for e in recorrer(gm):
        sub = e.get("events", [])
        sub[:] = [x for x in sub if not (x["type"].endswith("JsCode") and x.get("inlineCode", "").startswith("/*" + MK + "-CURA"))]
        k = next((n for n, x in enumerate(sub) if any(a["type"]["value"] == "ModVarObjet" and a["parameters"][:3] == ["Sup", "Cura", "+"]
                                                      for a in x.get("actions", []))), None)
        if k is not None and e["type"].endswith("ForEach"):
            sub.insert(k, js("if (gdjs.fdizProfes) gdjs.fdizProfes.curaAlumno(runtimeScene, objects);", MK + "-CURA", "Sup"))

    # unirse con control: un mando solo toma el lugar de un bot principal, nunca de un profe
    for e in recorrer(grupo(ev, "Unirse con control")["events"]):
        cs = e.get("conditions", [])
        if any(x["type"]["value"] == "VarObjet" and x["parameters"][:4] == ["Sup", "Control", "=", "-1"] for x in cs):
            if not any(x["type"]["value"] == "VarObjet" and x["parameters"][:2] == ["Sup", "Jugador"] for x in cs):
                cs.append(c("VarObjet", "Sup", "Jugador", "<=", "4"))

    # objetivo cumplido: reaparecen los alumnos "fuera"; un profe perdido no vuelve
    for e in recorrer(grupo(ev, "Objetivos y flecha")["events"]):
        cs = e.get("conditions", [])
        if any(x["type"]["value"] == "VarObjetTxt" and x["parameters"][:3] == ["Sup", "Estado", "="] and x["parameters"][3] == '"fuera"' for x in cs) \
                and any(a["type"]["value"] == "ModVarObjetTxt" and a["parameters"][:2] == ["Sup", "Estado"] for a in e.get("actions", [])):
            if not any(x["type"]["value"] == "VarObjet" and x["parameters"][:2] == ["Sup", "Jugador"] for x in cs):
                cs.append(c("VarObjet", "Sup", "Jugador", "<=", "4"))

    # pausa: Esc / P / Start no pausan mientras hay un diálogo con un profe
    for e in grupo(ev, "Menú de pausa")["events"]:
        cs = e.get("conditions", [])
        ors = [x for x in cs if x["type"]["value"] == "BuiltinCommonInstructions::Or"]
        if ors and any(s["type"]["value"] == "KeyReleased" and s["parameters"][1] == "Escape" for s in ors[0].get("subInstructions", [])):
            if not any(x["type"]["value"] == "VarScene" and x["parameters"][:1] == ["ProfDlg"] for x in cs):
                cs.insert(len(cs) - 1, c("VarScene", "ProfDlg", "=", "0"))

    # listas de zombis en el JS incrustado + niebla de bordes + habilidades de bots
    LZ_V = '"ZConserje", "ZCurado"]'
    LZ_N = '"ZConserje", "ZCurado", "ZJoel", "ZJustino", "ZCanepa"]'
    for e in recorrer(ev):
        if e["type"].endswith("JsCode") and not e["inlineCode"].startswith("/*" + MK):
            s = e["inlineCode"].replace(LZ_V, LZ_N)
            s = s.replace('const nombres = ["Sup", "ZNormal"', 'const nombres = ["Sup", "Profe", "ZNormal"')
            s = s.replace('if (g(s, "Control").getAsNumber() !== -1 || g(s, "Estado").getAsString() !== "normal") continue;',
                          'if (g(s, "Control").getAsNumber() !== -1 || g(s, "Estado").getAsString() !== "normal" || g(s, "Jugador").getAsNumber() > 4) continue;')
            e["inlineCode"] = s

    # ================================================================ red (configuración de sincronía + net_core)
    nucleo = next(e for e in TI["events"] if tiene_marca(e, "FDIZ-FASE25-NUCLEO"))
    code = nucleo["inlineCode"]
    m = re.search(r"gdjs\.fdizNetCfg=", code)
    cfg, fin = json.JSONDecoder().raw_decode(code, m.end())
    spec = lambda o: {"n": o["name"], "t": 0, "v": [[v["name"], "s" if v["type"] == "string" else "n"] for v in o["variables"]
                                                    if v["type"] in ("string", "number") and v["name"] not in ("BotX", "BotY")]}
    cfg["objs"] = [s for s in cfg["objs"] if s["n"] not in ("Canepa", "Profe") + tuple(ZOMBI.values())]
    cfg["objs"].append(spec(ob["Profe"]))
    for zn in ZOMBI.values():
        cfg["objs"].append(spec(ob[zn]))
    for p in PROFES:
        for n in ("Prof" + p.capitalize(), "Prof" + p.capitalize() + "Seg"):
            if n not in cfg["sv"]:
                cfg["sv"].append(n)
    code = code[:m.end()] + json.dumps(cfg, ensure_ascii=False) + code[fin:]
    code = parchear_net(code)
    nucleo["inlineCode"] = code

    escribir(PRY, json.dumps(d, ensure_ascii=False, indent=2))

    # ---------------- archivos fuente que también se incrustan
    for nombre, f in (("net_core.js", parchear_net), ("niebla_borde.js", parchear_niebla), ("bots_habilidades.js", parchear_hab)):
        ruta = os.path.join(AQUI, nombre)
        s = open(ruta, encoding="utf-8").read()
        s2 = f(s)
        if s2 != s:
            open(ruta, "w", encoding="utf-8").write(s2)
    print("Fase 40 aplicada. Vida de los profes zombi = %s (ZConserje)." % vida_cons)


def escribir(ruta, texto):
    """Escribe a un temporal y lo cambia de nombre (si Windows tiene el archivo ocupado un momento, reintenta)."""
    import time
    tmp = ruta + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(texto)
    for intento in range(10):
        try:
            os.replace(tmp, ruta)
            return
        except OSError:
            time.sleep(0.5)
    sys.exit("No se pudo escribir %s (¿GDevelop lo tiene abierto?). El resultado quedó en %s" % (ruta, tmp))


def parchear_net(s):
    a = 'const bcast = (o) => { for (const id in N.conns) send(N.conns[id], o); };'
    if "/*FDIZ-F40*/ N.toHost" not in s:
        s = s.replace(a, a + "\n  /*FDIZ-F40*/ N.toHost = (o) => send(N.conn, o);", 1)
    a = 'else if (d.t === "in") { N.inp[c.peer] = { at: performance.now(), p: d.p || [], cam: d.cam || null }; }'
    if '/*FDIZ-F40*/ else if (d.t === "prof")' not in s:
        s = s.replace(a, a + '\n    /*FDIZ-F40*/ else if (d.t === "prof") { if (N.onProf && N.started) N.onProf(c.peer, d); }', 1)
    a = 'const p = []; N.slots.forEach((s, i) => { if (s.owner === N.myId) p.push(readLocal(scn, s.ctl, i)); });'
    if "/*FDIZ-F40*/ if (N.onLocalInput)" not in s:
        s = s.replace(a, a + " /*FDIZ-F40*/ if (N.onLocalInput) N.onLocalInput(scn, p);", 1)
    for marca in ("/*FDIZ-F40*/ N.toHost", '/*FDIZ-F40*/ else if (d.t === "prof")', "/*FDIZ-F40*/ if (N.onLocalInput)"):
        if marca not in s:
            sys.exit("No se pudo parchear net_core (" + marca + "): revisar el código de red.")
    return s


def parchear_niebla(s):
    return s.replace('const nombres = ["Sup", "ZNormal", "ZCorredor", "ZGriton", "ZGordo", "ZConserje", "ZCurado"];',
                     'const nombres = ["Sup", "Profe", "ZNormal", "ZCorredor", "ZGriton", "ZGordo", "ZConserje", "ZCurado", "ZJoel", "ZJustino", "ZCanepa"];')


def parchear_hab(s):
    s = s.replace('"ZConserje", "ZCurado"];', '"ZConserje", "ZCurado", "ZJoel", "ZJustino", "ZCanepa"];')
    return s.replace('if (g(s, "Control").getAsNumber() !== -1 || g(s, "Estado").getAsString() !== "normal") continue;',
                     'if (g(s, "Control").getAsNumber() !== -1 || g(s, "Estado").getAsString() !== "normal" || g(s, "Jugador").getAsNumber() > 4) continue;')


if __name__ == "__main__":
    main()
