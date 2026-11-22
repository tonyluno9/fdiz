"""Fase 64 · Diálogos en burbujas con voz en la partida. Idempotente. Todos los modos.

Uso (desde la carpeta fdiz, con GDevelop CERRADO):
    python -I gdevelop/scripts/fase64_datos_dialogos.py   # (si cambia el banco o las voces) datos + gdevelop/DIALOGOS.md
    python gdevelop/scripts/fase64_dialogos.py
    node gdevelop/scripts/prueba_dialogo.js
Si se vuelve a correr fase25_online.py (compuerta de host en los eventos JS sueltos de Juego), correr esta fase otra vez.

Qué hace:
  * Registra como recursos de audio las voces relacionadas por fase64_datos_dialogos.py (nombre "voces/<pj>/<archivo>",
    archivo ../../audios_fish/<Personaje>/<archivo>) y las agrega a audio_manifest.json.
  * Juego: variables DlgSeq, DlgLinea, DlgHabla (también en la red); eventos FDIZ-FASE64-DATOS y -MOD arriba de todo y
    FDIZ-FASE64-TICK justo después del grupo "Cinemática de inicio" (para reemplazar sus líneas de charla en el mismo cuadro).
"""
import datetime, json, os, re, shutil

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
PROY = os.path.join(RAIZ, "gdevelop", "FDI-Z")
PRY = os.path.join(PROY, "FDI-Z.json")
MK = "FDIZ-FASE64"
VARS = [("DlgSeq", 0), ("DlgLinea", ""), ("DlgHabla", "")]


def js(code, marca):
    return {"type": "BuiltinCommonInstructions::JsCode", "inlineCode": "/*" + marca + "*/\n" + code,
            "parameterObjects": "", "useStrict": True, "eventsSheetExpanded": False}


def recorrer(lst):
    for e in lst:
        yield e
        yield from recorrer(e.get("events", []))


def es_js(e, marca):
    return e.get("type", "").endswith("JsCode") and e.get("inlineCode", "").startswith("/*" + marca)


def quitar(lst, marca):
    lst[:] = [e for e in lst if not es_js(e, marca)]
    for e in lst:
        if e.get("events"):
            quitar(e["events"], marca)


def main():
    voces = json.load(open(os.path.join(AQUI, "dialogos_voces.json"), encoding="utf-8"))["recursos"]
    for v in voces:
        if not os.path.exists(os.path.normpath(os.path.join(PROY, v["archivo"]))):
            raise SystemExit("Falta la voz " + v["archivo"])
    d = json.load(open(PRY, encoding="utf-8"))
    resp = os.path.join(RAIZ, "gdevelop", "respaldos")
    os.makedirs(resp, exist_ok=True)
    bak = os.path.join(resp, "antes_de_fase64_%s.json" % datetime.date.today().strftime("%Y%m%d"))
    if not os.path.exists(bak):
        shutil.copy(PRY, bak)

    # ---- recursos de voz
    res = d["resources"]["resources"]
    nombres = {r["name"]: r for r in res}
    for v in voces:
        r = nombres.get(v["nombre"])
        if r is None:
            res.append({"file": v["archivo"], "kind": "audio", "metadata": "", "name": v["nombre"], "userAdded": True})
        else:
            r.update({"file": v["archivo"], "kind": "audio"})

    # ---- variables y red
    J = next(l for l in d["layouts"] if l["name"] == "Juego")
    for n, val in VARS:
        if not any(x["name"] == n for x in J["variables"]):
            J["variables"].append({"name": n, "type": "string" if isinstance(val, str) else "number", "value": val})
    T = next(l for l in d["layouts"] if l["name"] == "Titulo")
    nucleo = next(e for e in recorrer(T["events"]) if e.get("type", "").endswith("JsCode") and "gdjs.fdizNetCfg=" in e["inlineCode"])
    code = nucleo["inlineCode"]
    m = re.search(r"gdjs\.fdizNetCfg=", code)
    cfg, fin = json.JSONDecoder().raw_decode(code, m.end())
    for n, _ in VARS:
        if n not in cfg["sv"]:
            cfg["sv"].append(n)
    nucleo["inlineCode"] = code[:m.end()] + json.dumps(cfg, ensure_ascii=False) + code[fin:]

    # ---- eventos
    ev = J["events"]
    for s in ("-DATOS", "-MOD", "-TICK"):
        quitar(ev, MK + s)
    k = next((i for i, e in enumerate(ev) if es_js(e, "FDIZ-FASE56-MOD")), 0)
    ev[k:k] = [js(open(os.path.join(AQUI, "dialogos_datos.js"), encoding="utf-8").read(), MK + "-DATOS"),
               js(open(os.path.join(AQUI, "dialogo.js"), encoding="utf-8").read(), MK + "-MOD")]
    cin = next(i for i, e in enumerate(ev) if e.get("type", "").endswith("Group") and e.get("name", "").startswith("Cinemática de inicio"))
    ev.insert(cin + 1, js("if (gdjs.fdizDialogo) gdjs.fdizDialogo.tick(runtimeScene);", MK + "-TICK"))

    # ---- manifiesto de audio (para validar_audio.py)
    pm = os.path.join(PROY, "audio_manifest.json")
    man = json.load(open(pm, encoding="utf-8"))
    ya = {x["path"] for x in man["effects"]}
    for v in voces:
        if v["archivo"] not in ya:
            man["effects"].append({"id": "VOZ_" + re.sub(r"[^A-Z0-9]+", "_", os.path.splitext(v["nombre"][6:])[0].upper()), "path": v["archivo"], "priority": "P2"})
    json.dump(man, open(pm, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    tmp = PRY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=2))
    os.replace(tmp, PRY)
    print("Fase 64 aplicada: %d voces, datos y dialogo.js en Juego." % len(voces))


if __name__ == "__main__":
    main()
