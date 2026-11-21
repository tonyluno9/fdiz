"""Fase 52 · Bloque Jugabilidad y mecánicas, parte 3: lanzables con distracción + daño en área, y cuadro explicativo del primer lanzable.
Idempotente; va al final de la cadena (después de fase51).

Uso (desde la carpeta fdiz, con GDevelop CERRADO):  python3 gdevelop/scripts/fase52_lanzables.py
- Objetos nuevos: LzMundo (pintor en la capa Juego: ondas de impacto) y LzInfo (pintor en HUD: cuadro). Variable de escena LanzInfo (0 al iniciar o reiniciar).
- lanz_impacto.js: dentro del ForEach de Proyectil, antes de borrarlo (Pego = 1): distracción + daño en área (balón y libro).
- lanz_frame.js: tras el grupo "Lanzables": mueve a los distraídos, dibuja ondas y muestra el cuadro del primer lanzable (pausa el juego).
- lanz_entrada.js: tras el grupo "Entrada (teclado y controles)": bloquea movimiento y golpes mientras el cuadro está abierto.
"""
import copy, datetime, json, os, shutil

AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
MK = "FDIZ-FASE52"


def leer(n): return open(os.path.join(AQUI, n), encoding="utf-8").read()


def js(code, marca, objs=""):
    return {"type": "BuiltinCommonInstructions::JsCode", "inlineCode": "/*" + marca + "*/\n" + code, "parameterObjects": objs, "useStrict": True, "eventsSheetExpanded": False}


def con_marca(e):
    return e["type"].endswith("JsCode") and e.get("inlineCode", "").startswith("/*" + MK)


def limpiar(lst):
    lst[:] = [e for e in lst if not (con_marca(e) or (e["type"].endswith("Standard") and not e.get("conditions") and len(e.get("events", [])) == 1 and con_marca(e["events"][0])))]
    for e in lst: limpiar(e.get("events", []))


def main():
    d = json.load(open(PRY, encoding="utf-8"))
    resp = os.path.join(AQUI, "..", "respaldos"); os.makedirs(resp, exist_ok=True)
    bak = os.path.join(resp, "antes_de_fase52_%s.json" % datetime.date.today().strftime("%Y%m%d"))
    if not os.path.exists(bak): shutil.copy(PRY, bak)
    J = next(l for l in d["layouts"] if l["name"] == "Juego")

    for nom, capa in (("LzMundo", "Juego"), ("LzInfo", "HUD")):
        if not any(o["name"] == nom for o in J["objects"]):
            o = copy.deepcopy(next(o for o in J["objects"] if o["name"] == "JfDibO")); o["name"] = nom; J["objects"].append(o)
        if not any(i["name"] == nom for i in J["instances"]):
            i = copy.deepcopy(next(i for i in J["instances"] if i["name"] == "JfDibO")); i["name"] = nom; i["layer"] = capa; J["instances"].append(i)
    if not any(v["name"] == "LanzInfo" for v in J["variables"]):
        J["variables"].append({"name": "LanzInfo", "type": "number", "value": 0})

    ev = J["events"]
    limpiar(ev)
    # 1) impacto: dentro del ForEach de Proyectil, justo antes del evento Pego = 1
    gl = next(e for e in ev if e["type"].endswith("Group") and e.get("name") == "Lanzables")
    def borra(lst):
        return any(a["type"]["value"] == "Delete" and a["parameters"][0] == "Proyectil" for x in lst for a in x.get("actions", [])) or any(borra(x.get("events", [])) for x in lst)

    def buscar(lst):
        for e in lst:
            if e["type"].endswith("ForEach") and not e.get("conditions") and borra(e.get("events", [])):
                return e
            r = buscar(e.get("events", []))
            if r: return r
    fe = buscar(gl["events"])
    assert fe, "no encontré el ForEach de Proyectil"
    k = next(i for i, x in enumerate(fe["events"]) if any(c["type"]["value"] == "VarObjet" and c["parameters"][:3] == ["Proyectil", "Pego", "="] for c in x.get("conditions", [])))
    fe["events"].insert(k, {"type": "BuiltinCommonInstructions::Standard", "conditions": [], "actions": [], "events": [js(leer("lanz_impacto.js"), MK + "-IMPACTO", "Proyectil")]})
    # 2) cada cuadro, después del grupo Lanzables
    k = ev.index(gl)
    ev.insert(k + 1, js(leer("lanz_frame.js"), MK + "-FRAME"))
    # 3) bloqueo de entrada, después del grupo Entrada
    ge = next(e for e in ev if e["type"].endswith("Group") and e.get("name", "").startswith("Entrada (teclado y controles)"))
    ev.insert(ev.index(ge) + 1, js(leer("lanz_entrada.js"), MK + "-ENTRADA"))
    json.dump(d, open(PRY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("OK fase52 (lanzables: distracción + cuadro)")


main()
