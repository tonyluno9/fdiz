"""Fase 46 · Bloque Medios del reporte de pruebas de jugabilidad. Idempotente; va al final de la cadena (después de fase45).

Uso (desde la carpeta fdiz, con GDevelop CERRADO):  python3 gdevelop/scripts/fase46_medios.py
Qué hace en FDI-Z.json (escena Juego; la lógica está en scripts/medios.js):
  4) Oscuridad de los salones inestable: el evento JavaScript que decide qué personajes se dibujan por delante de la oscuridad
     (capa SupervivientesBorde) pasa a medios.js -> borde(): caja fija desde los pies y 3 cuadros de espera (antes usaba el
     tamaño del dibujo, que cambia en cada cuadro de la animación, y saltaba de capa).
  5) Animación de caminar de lado bugueada: los eventos que elegían animación y volteo comparando |vx| con |vy| cada cuadro
     se reemplazan por medios.js -> anim() (histéresis en diagonal, volteo solo con velocidad real).
  6) Llaves: solo las toma un jugador humano. Los bots ya no las eligen como destino (condición Tipo != llaves) y medios.js ->
     llaves() deshace cualquier progreso sumado por un no humano, avisa cuando hay un humano cerca, muestra su nombre mientras
     las toma y publica "¡<Nombre> tomó las llaves!".
  7) Habilidad E trabada: la animación de cada especial duraba 0.5 s pero el bloqueo (Atacando) termina a 0.28 s, así que se
     cortaba a la mitad y el personaje quedaba "congelado" en el cuadro. Ahora los 5 cuadros duran 0.05 s (0.25 s en total).
"""
import copy, datetime, json, os, shutil

AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
MK = "FDIZ-FASE46"
NOCLI = {"type": {"inverted": False, "value": "VarGlobal"}, "parameters": ["NetRol", "!=", "2"]}
PRINCIPALES = {"tony", "tonyfuerte", "miranda", "cesar", "alan", "castillo", "alessandro", "gabo", "carlos"}


def js(code, marca, objs=""):
    return {"type": "BuiltinCommonInstructions::JsCode", "inlineCode": "/*" + marca + "*/\n" + code,
            "parameterObjects": objs, "useStrict": True, "eventsSheetExpanded": False}


def std(conds, acts, sub=()):
    return {"type": "BuiltinCommonInstructions::Standard", "conditions": conds, "actions": acts, "events": list(sub)}


def recorrer(lst):
    for e in lst:
        yield e
        yield from recorrer(e.get("events", []))


def tiene_marca(e, marca):
    return any(x.get("type", "").endswith("JsCode") and x.get("inlineCode", "").startswith("/*" + marca) for x in recorrer([e]))


def grupo(ev, prefijo):
    return next(e for e in ev if e["type"].endswith("Group") and e.get("name", "").startswith(prefijo))


def main():
    d = json.load(open(PRY, encoding="utf-8"))
    resp = os.path.join(AQUI, "..", "respaldos")
    os.makedirs(resp, exist_ok=True)
    bak = os.path.join(resp, "antes_de_fase46_%s.json" % datetime.date.today().strftime("%Y%m%d"))
    if not os.path.exists(bak):
        shutil.copy(PRY, bak)
    J = next(l for l in d["layouts"] if l["name"] == "Juego")
    ev = J["events"]

    # ---- módulo (arriba de todo, sin envoltura: se define en todas las máquinas)
    ev[:] = [e for e in ev if not (tiene_marca(e, MK + "-MOD") and len(list(recorrer([e]))) <= 2)]
    ev.insert(0, js(open(os.path.join(AQUI, "medios.js"), encoding="utf-8").read(), MK + "-MOD"))

    # ---- 4) capa del borde: se cambia el código del evento JavaScript existente (queda en su sitio y con su envoltura)
    n4 = 0
    for e in recorrer(ev):
        if e.get("type", "").endswith("JsCode") and ("El sprite puede pasar por delante del borde" in e.get("inlineCode", "") or e.get("inlineCode", "").startswith("/*" + MK + "-BORDE")):
            e["inlineCode"] = "/*" + MK + "-BORDE*/\nif (gdjs.fdizMedios) gdjs.fdizMedios.borde(runtimeScene);"
            n4 += 1
    assert n4 == 1, "no encontré el evento de la capa del borde (%d)" % n4

    # ---- 5) animación de caminar
    gm = grupo(ev, "Movimiento y animación")
    n5 = 0
    for e in recorrer(gm["events"]):
        if e.get("type", "").endswith("ForEach") and e.get("object") == "Sup" and any(
                c["type"]["value"] == "VarObjet" and c["parameters"][:4] == ["Sup", "Atacando", "=", "0"] for c in e.get("conditions", [])):
            e["events"] = [std([copy.deepcopy(NOCLI)], [], [js("if (gdjs.fdizMedios) gdjs.fdizMedios.anim(runtimeScene, objects);", MK + "-ANIM", "Sup")])]
            n5 += 1
    assert n5 == 1, "no encontré el ForEach de animación (%d)" % n5

    # ---- 6) llaves
    go = grupo(ev, "Objetivos y flecha")
    n6 = 0
    for e in recorrer(go["events"]):
        lst = e.get("events", [])
        k = next((i for i, x in enumerate(lst) if any(a["type"]["value"] == "ModVarObjet" and a["parameters"][:4] == ["Objetivo", "Hecho", "=", "1"] for a in x.get("actions", []))
                  and any("Progreso" in "".join(c["parameters"]) for c in x.get("conditions", []))), None)
        if k is None:
            continue
        lst[:] = [x for x in lst if not tiene_marca(x, MK + "-LLAVES")]
        k = next(i for i, x in enumerate(lst) if any(a["type"]["value"] == "ModVarObjet" and a["parameters"][:4] == ["Objetivo", "Hecho", "=", "1"] for a in x.get("actions", [])))
        lst.insert(k, std([copy.deepcopy(NOCLI)], [], [js("if (gdjs.fdizMedios) gdjs.fdizMedios.llaves(runtimeScene, objects);", MK + "-LLAVES", "Objetivo")]))
        n6 += 1
    assert n6 == 1, "no encontré el evento de progreso de objetivos (%d)" % n6

    gb = grupo(ev, "Bots: objetivos y puertas")
    n7 = 0
    for e in recorrer(gb["events"]):
        cs = e.get("conditions", [])
        if len(cs) >= 2 and cs[0]["type"]["value"] == "VarObjet" and cs[0]["parameters"][:4] == ["Objetivo", "Hecho", "=", "0"] and cs[1]["type"]["value"] == "PickNearest" and cs[1]["parameters"][0] == "Objetivo":
            cs.insert(1, {"type": {"inverted": False, "value": "VarObjetTxt"}, "parameters": ["Objetivo", "Tipo", "!=", "\"llaves\""]})
            n7 += 1
        elif len(cs) >= 3 and cs[1]["type"]["value"] == "VarObjetTxt" and cs[1]["parameters"] == ["Objetivo", "Tipo", "!=", "\"llaves\""]:
            n7 += 1
    assert n7 == 1, "no encontré el evento de bots hacia objetivos (%d)" % n7

    # ---- 7) animación de los especiales: 5 cuadros x 0.05 s = 0.25 s (el bloqueo dura 0.28 s)
    sup = next(o for o in J["objects"] if o["name"] == "Sup")
    n8 = 0
    for a in sup["animations"]:
        if a["name"].endswith("_especial") and a["name"][: -len("_especial")] in PRINCIPALES:
            for dr in a["directions"]:
                dr["timeBetweenFrames"] = round(0.25 / max(1, len(dr["sprites"])), 4)
            n8 += 1
    assert n8 == 9, "especiales: %d" % n8

    json.dump(d, open(PRY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("OK fase46 (capa %d, anim %d, llaves %d, bots %d, especiales %d)" % (n4, n5, n6, n7, n8))


main()
