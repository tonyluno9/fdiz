"""Fase 57 · Volumen de música y efectos + música en "Elige el modo". Idempotente.

Uso (desde la carpeta fdiz, con GDevelop CERRADO):  python gdevelop/scripts/fase57_volumen.py
Va al final de la cadena (después de fase56). Pruebas: node gdevelop/scripts/prueba_audio.js

Qué hace en FDI-Z.json (lógica en scripts/audio.js, ver su encabezado):
  * Variables globales VolMusica y VolEfectos (100 = como antes).
  * En TODAS las escenas, al principio: el módulo audio.js y gdjs.fdizAudio.aplicar(runtimeScene) cada cuadro (antes de
    la música de inicio de cada escena, para que ya salga con el volumen elegido).
  * Menu y Online: música del menú al entrar (antes no tenían: GDevelop detiene todos los sonidos al empezar una escena,
    así que la música del Título se cortaba al pasar a "Elige el modo" y nadie la volvía a poner). Como cada escena
    detiene lo anterior al empezar, nunca suenan dos músicas a la vez.
  * Menú de pausa: el botón CONTROLES ahora dice AJUSTES y su pantalla es "CONTROLES Y SONIDO", con las filas MÚSICA y
    EFECTOS (− / barra / +) y VOLVER. Esa pantalla ya no se cierra con cualquier tecla o clic (para poder ajustar):
    VOLVER, Retroceso o B del mando.
"""
import copy, datetime, json, os, re, shutil, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
MK = "FDIZ-FASE57"
MUSICA_MENU = ["", "musica/menu.ogg", "1", "yes", "45", "1"]        # la misma acción que usa el Título


def js(code, marca):
    return {"type": "BuiltinCommonInstructions::JsCode", "inlineCode": "/*" + marca + "*/\n" + code,
            "parameterObjects": "", "useStrict": True, "eventsSheetExpanded": False}


def std(conds, acts, sub=()):
    return {"type": "BuiltinCommonInstructions::Standard", "conditions": conds, "actions": acts, "events": list(sub)}


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
        return e.get("comment", "").startswith(marca)
    return False


def quitar_top(lst, marca):
    lst[:] = [e for e in lst if not es_marca(e, marca)]


def main():
    d = json.load(open(PRY, encoding="utf-8"))
    resp = os.path.join(AQUI, "..", "respaldos")
    os.makedirs(resp, exist_ok=True)
    bak = os.path.join(resp, "antes_de_fase57_%s.json" % datetime.date.today().strftime("%Y%m%d"))
    if not os.path.exists(bak):
        shutil.copy(PRY, bak)
    for n in ("VolMusica", "VolEfectos"):
        if not any(v["name"] == n for v in d["variables"]):
            d["variables"].append({"name": n, "type": "number", "value": 100})
    modulo = open(os.path.join(AQUI, "audio.js"), encoding="utf-8").read()
    hecho = {}

    for L in d["layouts"]:
        ev = L["events"]
        quitar_top(ev, MK + "-MOD")
        quitar_top(ev, MK + "-APLICAR")
        ev[0:0] = [js(modulo, MK + "-MOD"), js("if (gdjs.fdizAudio) gdjs.fdizAudio.aplicar(runtimeScene);", MK + "-APLICAR")]
        hecho[L["name"]] = ["módulo"]
        # música del menú al entrar (Menu y la sala en línea no tenían)
        if L["name"] in ("Menu", "Online"):
            if not any(es_marca(e, MK + "-MUSICA") for e in ev):
                ev[2:2] = [comentario(MK + "-MUSICA · La música del menú empieza al entrar (GDevelop detiene los sonidos de la escena anterior, así que no se duplica)."),
                           std([c("DepartScene", ""), c("VarGlobal", "SonidoActivo", "=", "1")], [a("PlayMusicCanal", *MUSICA_MENU)])]
                hecho[L["name"]].append("música")

    J = next(l for l in d["layouts"] if l["name"] == "Juego")
    ob = {o["name"]: o for o in J["objects"]}
    if "TxtVol" not in ob:
        t = copy.deepcopy(ob["TxtPausaCtl1"]); t["name"] = "TxtVol"; J["objects"].append(t)
    if "VolDib" not in ob:
        t = copy.deepcopy(ob["ProfDib"]); t["name"] = "VolDib"; J["objects"].append(t)
    P = next(e for e in J["events"] if e.get("type", "").endswith("Group") and e.get("name") == "Menú de pausa")["events"]
    for e in recorrer(P):
        for x in e.get("actions", []):
            p = x["parameters"]
            if x["type"]["value"] == "TextObject::String" and p[0] == "TxtPausaB1" and p[2] == '"CONTROLES"':
                p[2] = '"AJUSTES"'; hecho["botón"] = "AJUSTES"
            if x["type"]["value"] == "TextObject::String" and p[0] == "TxtPausaTit" and p[2] == '"CONTROLES"':
                p[2] = '"CONTROLES Y SONIDO"'; hecho["título"] = "CONTROLES Y SONIDO"
        # la pantalla de controles se cerraba con cualquier Enter / Espacio / clic / A: ahora solo con B (y VOLVER / Retroceso en audio.js)
        cs = e.get("conditions", [])
        if any(x["type"]["value"] == "VarScene" and x["parameters"][:3] == ["PausaVista", "=", "2"] for x in cs) and \
                any(x["type"]["value"] == "ModVarScene" and x["parameters"][:3] == ["PausaVista", "=", "0"] for x in e.get("actions", [])):
            for x in cs:
                if x["type"]["value"] == "BuiltinCommonInstructions::Or":
                    antes = len(x["subInstructions"])
                    x["subInstructions"] = [s for s in x["subInstructions"]
                                            if s["type"]["value"] == "Gamepads::C_Button_released" and s["parameters"][2] == '"B"']
                    hecho["cerrar"] = "solo B (quitadas %d)" % (antes - len(x["subInstructions"]))
    if not any(es_marca(e, MK + "-PAUSA") or any(es_marca(s, MK + "-PAUSA") for s in e.get("events", [])) for e in P):
        P.append(std([c("VarGlobal", "NetRol", "=", "0")], [], [js("if (gdjs.fdizAudio) gdjs.fdizAudio.pausa(runtimeScene);", MK + "-PAUSA")]))

    tmp = PRY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=2))
    os.replace(tmp, PRY)
    print("Fase 57 aplicada:", hecho)


if __name__ == "__main__":
    main()
