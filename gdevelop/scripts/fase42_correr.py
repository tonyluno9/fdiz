"""Fase 42 · Correr con estamina (Shift / LB / L3) en lugar de caminar despacio. Idempotente.

Uso (desde la carpeta fdiz, con GDevelop CERRADO):  python gdevelop/scripts/fase42_correr.py
Va al final de la cadena (después de fase41). Si se vuelve a correr fase5_jugadores.py (regenera los eventos de
movimiento) o fase25_online.py (re-incrusta net_core.js y la configuración de red), correr esta fase otra vez.

Qué hace en FDI-Z.json:
  * Sup: variables Estamina (15), Agotado, Corre, EstPausa.  Objeto EstDib (dibujo en el HUD) para la barra, que va
    pegada al panel de cada jugador; los espacios de inventario (HudInv) se recorren para dejarle lugar.
  * Eventos: módulo scripts/correr.js; en "Movimiento y animación" se quitan los dos eventos de caminar despacio
    (Shift del teclado y NetSp del jugador remoto) y se pone la carrera con estamina; la barra se dibuja en todos.
  * Texto de controles del mando: "LB  correr".
  * Red: Estamina, Agotado y Corre se sincronizan; el cliente manda Shift (antes preguntaba por la tecla 16, que en
    GDevelop nunca llega: Shift izq. es 1016 y der. 2016) y LB / L3 del mando. También en net_core.js.
"""
import copy, datetime, json, os, re, shutil, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
MK = "FDIZ-FASE42"
NOCLI = {"type": {"inverted": False, "value": "VarGlobal"}, "parameters": ["NetRol", "!=", "2"]}
VARS = [("Estamina", 15), ("Agotado", 0), ("Corre", 0), ("EstPausa", 0)]
SYNC = ["Estamina", "Agotado", "Corre"]
INV_Y = {186: 210, 858: 832}

NET_TECLA = ("o.sp = I.isKeyPressed(16) ? 1 : 0;",
             "o.sp = (I.isKeyPressed(1016) || I.isKeyPressed(2016) || I.isKeyPressed(16)) ? 1 : 0;")
NET_PAD = ("o.hit = b(2); o.use = b(0); o.hab = b(3); o.esp = b(5); o.lz = b(1);",
           "o.hit = b(2); o.use = b(0); o.hab = b(3); o.esp = b(5); o.lz = b(1); o.sp = (b(4) || b(10)) ? 1 : 0;")


def js(code, marca):
    return {"type": "BuiltinCommonInstructions::JsCode", "inlineCode": "/*" + marca + "*/\n" + code,
            "parameterObjects": "", "useStrict": True, "eventsSheetExpanded": False}


def std(conds, acts, sub=()):
    return {"type": "BuiltinCommonInstructions::Standard", "conditions": conds, "actions": acts, "events": list(sub)}


def recorrer(lst):
    for e in lst:
        yield e
        yield from recorrer(e.get("events", []))


def tiene_marca(e, marca):
    return any(x.get("type", "").endswith("JsCode") and x.get("inlineCode", "").startswith("/*" + marca)
               for x in recorrer([e]))


def quitar(lst, marca):
    lst[:] = [e for e in lst if not (tiene_marca(e, marca) and len(list(recorrer([e]))) <= 2)]


def parchear_net(s):
    for viejo, nuevo in (NET_TECLA, NET_PAD):
        if nuevo not in s:
            if viejo not in s:
                sys.exit("No encontré en net_core el texto: " + viejo)
            s = s.replace(viejo, nuevo)
    return s


def es_lento(e):
    """Los eventos viejos de caminar despacio: MaxSpeed = Velocidad * 0.5 (Shift del teclado o NetSp remoto)."""
    return (e.get("type", "").endswith("Standard")
            and any(a["type"]["value"] == "TopDownMovementBehavior::MaxSpeed" and "* 0.5" in a["parameters"][-1]
                    for a in e.get("actions", []))
            and any((c["type"]["value"] == "KeyPressed" and c["parameters"][-1] == "LShift")
                    or (c["type"]["value"] == "VarObjet" and c["parameters"][:2] == ["Sup", "NetSp"])
                    for c in e.get("conditions", [])))


def es_base(e):
    return any(a["type"]["value"] == "TopDownMovementBehavior::MaxSpeed"
               and a["parameters"][-1] == "Sup.Variable(Velocidad) * Sup.Variable(Rapidez)" for a in e.get("actions", []))


def main():
    d = json.load(open(PRY, encoding="utf-8"))
    resp = os.path.join(AQUI, "..", "respaldos")
    os.makedirs(resp, exist_ok=True)
    bak = os.path.join(resp, "antes_de_fase42_%s.json" % datetime.date.today().strftime("%Y%m%d"))
    if not os.path.exists(bak):
        shutil.copy(PRY, bak)

    J = next(l for l in d["layouts"] if l["name"] == "Juego")
    TI = next(l for l in d["layouts"] if l["name"] == "Titulo")
    ob = {o["name"]: o for o in J["objects"]}

    # ---------------- objetos
    sup = ob["Sup"]
    for n, v in VARS:
        if not any(x["name"] == n for x in sup["variables"]):
            sup["variables"].append({"name": n, "type": "number", "value": v})
    if "EstDib" not in ob:
        dib = copy.deepcopy(ob["ProfDib"])
        dib["name"] = "EstDib"
        J["objects"].append(dib)
    # la barra va pegada a cada panel (debajo de los de arriba, encima de los de abajo): los 3 espacios de
    # inventario se recorren para dejarle lugar (arriba 186 -> 210, abajo 858 -> 832)
    for i in J["instances"]:
        if i["name"] == "HudInv" and i["y"] in INV_Y:
            i["y"] = INV_Y[i["y"]]

    # ---------------- eventos
    ev = J["events"]
    quitar(ev, MK + "-MOD")
    ev.insert(0, js(open(os.path.join(AQUI, "correr.js"), encoding="utf-8").read(), MK + "-MOD"))

    g = next(e for e in ev if e["type"].endswith("Group") and e.get("name", "").startswith("Movimiento y anim"))
    ge = g["events"]
    quitados = len([e for e in ge if es_lento(e)])
    ge[:] = [e for e in ge if not es_lento(e)]
    quitar(ge, MK + "-MOVER")
    quitar(ge, MK + "-DIBUJO")
    k = next(i for i, e in enumerate(ge) if es_base(e))
    ge.insert(k + 1, std([copy.deepcopy(NOCLI)], [], [js("if (gdjs.fdizCorrer) gdjs.fdizCorrer.mover(runtimeScene);", MK + "-MOVER")]))
    ge.append(js("if (gdjs.fdizCorrer) gdjs.fdizCorrer.dibujar(runtimeScene);", MK + "-DIBUJO"))

    # comentarios y textos de ayuda
    for e in recorrer(ev):
        if e.get("type", "").endswith("Comment"):
            e["comment"] = e["comment"].replace("Shift (teclado) = caminar despacio.",
                                                "Shift (teclado) o LB / L3 (mando) = correr con estamina (fase 42, scripts/correr.js).")
            e["comment"] = e["comment"].replace("Shift caminar despacio", "Shift correr (LB o L3 en el mando)")
        for a in e.get("actions", []):
            if a["type"]["value"] == "TextObject::String":
                p = a["parameters"][-1]
                if isinstance(p, str) and p.startswith('"MANDO"') and '"LB  correr' not in p:
                    a["parameters"][-1] = p.replace('"Start  pausa"', '"LB  correr  ·  Start  pausa"')

    # ---------------- red
    nucleo = next(e for e in recorrer(TI["events"]) if e.get("type", "").endswith("JsCode") and "gdjs.fdizNetCfg=" in e["inlineCode"])
    code = nucleo["inlineCode"]
    m = re.search(r"gdjs\.fdizNetCfg=", code)
    cfg, fin = json.JSONDecoder().raw_decode(code, m.end())
    spec = next(s for s in cfg["objs"] if s["n"] == "Sup")
    for n in SYNC:
        if not any(x[0] == n for x in spec["v"]):
            spec["v"].append([n, "n"])
    code = code[:m.end()] + json.dumps(cfg, ensure_ascii=False) + code[fin:]
    nucleo["inlineCode"] = parchear_net(code)

    tmp = PRY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=2))
    os.replace(tmp, PRY)

    ruta = os.path.join(AQUI, "net_core.js")
    s = open(ruta, encoding="utf-8", newline="").read()      # newline="": conserva los fines de línea del archivo
    s2 = parchear_net(s)
    if s2 != s:
        open(ruta, "w", encoding="utf-8", newline="").write(s2)
    print("Fase 42 aplicada. Eventos de caminar despacio quitados: %d." % quitados)


if __name__ == "__main__":
    main()
