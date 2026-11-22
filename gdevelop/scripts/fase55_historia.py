"""Fase 55 · Modo HISTORIA: 6 misiones fijas en orden. Idempotente (también actualiza un proyecto con la versión de 5).

Uso (desde la carpeta fdiz, con GDevelop CERRADO):
    python gdevelop/scripts/fase55_ilus_historia.py     # (una vez) ilustración provisional de la tarjeta
    python gdevelop/scripts/fase55_historia.py
    python gdevelop/scripts/prueba_historia.py          # simula los eventos de objetivos (sin GDevelop)
Va al final de la cadena (después de las fases 43-54 de cesar). Si se vuelve a correr una fase anterior que regenere eventos del Menú o
de Juego (fase5, fases_6_a_11, fase12, fase25...), correr esta fase otra vez.

Orden de Historia (Modo global = "historia"):
    1 llamada   Llamar desde la computadora del CIC (sin el paso previo del servidor del SITE, que está tras una
                puerta restringida: así la llamada no depende de algo que todavía no se puede hacer).
    2 luz       Se va la luz y hay que activar los 3 interruptores, todos dentro del CIC.
    3 llaves    Las llaves del conserje (conserjería; su puerta es restringida: a golpes o con Carlos, como siempre).
    4 carnada   Llevar comida a la nevería para distraer a la horda.
    5 canepa    Hablar con el profe Canepa en el camión (fase 61, 2026-11-22): mantener F junto a él abre la conversación
                (scripts/canepa.js, burbujas sobre quien habla); ahí descubren que falta gasolina. Al terminar el diálogo
                se cumple la misión (Paso = 99, una sola vez: CanepaCharla 0 -> 1 -> 2) y empieza la gasolina.
    6 gasolina  3 bidones al camión.
    y después el final del camión (igual que en Escape).
Escape (3 al azar) y Jefe no cambian: con ObjTotal = 3 y ObjEspera = 0 sus eventos se comportan igual que antes.

Qué cambia en Juego (grupo "Objetivos y flecha"):
  * Variables de escena ObjTotal (3 / 6), O4, O5, O6, ObjEspera, ObjTxt, CanepaCharla, CinLinea, CinHabla.
  * Los "/3" y "ObjNum = 4" fijos pasan a usar ObjTotal (también en "Guía de los bots" y "Modo presentación").
  * Señales: al cumplir, letrero "¡OBJETIVO n/5 CUMPLIDO!" + sonido; 2.5 s después se activa el siguiente con
    "OBJETIVO n/5 · ..." + sonido (antes el letrero de "cumplido" se borraba al cuadro siguiente).
  * Una sola vez: los objetivos ya se borraban al cumplirse; además, si se recogen 2 bidones en el mismo cuadro
    ahora cuentan los 2 (antes contaba 1 y la gasolina quedaba imposible).
  * En línea: el texto del objetivo viaja en ObjTxt y los clientes lo muestran (antes no lo veían).
Menú: tercera tarjeta HISTORIA (Escape | Jefe | Historia), clic sobre cada tarjeta, Local / En línea como Escape.
Red (net_core.js): la sala se crea en modo "historia" si se llegó desde esa tarjeta.
"""
import copy, datetime, json, os, re, shutil, sys, uuid

AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
NET = os.path.join(AQUI, "net_core.js")
MK = "FDIZ-FASE55"

ORDEN = ["llamada", "luz", "llaves", "carnada", "canepa", "gasolina"]
CANEPA = (544, 3328)                                   # donde espera Canepa, junto al camión (instancia Profe "canepa")
HABLAR = 0.6                                           # s manteniendo F junto a Canepa para empezar la charla
COMPU = (3136, 1760)                                   # computadora del CIC (zona "CIC")
INTERRUPTORES = [(2736, 1640), (3336, 1760), (3696, 1640)]   # pasillo CIC oeste, salón del CIC, pasillo CIC este
ESPERA = 2.5                                           # s entre "cumplido" y el siguiente objetivo
HUD = {  # texto del HUD en Historia (el de carnada es el mismo de Escape)
    "llamada": "Llamen desde la computadora del CIC",
    "luz": "Activen los 3 interruptores del CIC",
    "llaves": "Busquen las llaves del conserje en la conserjería",
    "canepa": "Hablen con el profe Canepa en el camión",
    "gasolina": "Busquen la gasolina: 3 bidones al camión",
}
LETRERO = {  # letrero al activarse cada objetivo
    "llamada": "LLAMAR DESDE EL CIC",
    "luz": "¡SE FUE LA LUZ! INTERRUPTORES DEL CIC",
    "llaves": "LAS LLAVES DEL CONSERJE",
    "carnada": "COMIDA A LA NEVERÍA",
    "canepa": "HABLAR CON CANEPA EN EL CAMIÓN",
    "gasolina": "BUSCAR LA GASOLINA",
}

VARS = [("ObjTotal", 3)] + [("O%d" % n, "") for n in range(4, len(ORDEN) + 1)] +        [("ObjEspera", 0), ("ObjTxt", ""), ("CanepaCharla", 0), ("CinLinea", -1), ("CinHabla", "")]

NOCLI = {"type": {"inverted": False, "value": "VarGlobal"}, "parameters": ["NetRol", "!=", "2"]}
CLI = {"type": {"inverted": False, "value": "VarGlobal"}, "parameters": ["NetRol", "=", "2"]}
HIST = {"type": {"inverted": False, "value": "VarGlobalTxt"}, "parameters": ["Modo", "=", '"historia"']}
NOHIST = {"type": {"inverted": False, "value": "VarGlobalTxt"}, "parameters": ["Modo", "!=", '"historia"']}


# ------------------------------------------------------------------ utilidades
def c(tipo, *p, inv=False):
    return {"type": {"inverted": inv, "value": tipo}, "parameters": list(p)}


def a(tipo, *p):
    return {"type": {"value": tipo}, "parameters": list(p)}


def std(conds, acts, sub=()):
    return {"type": "BuiltinCommonInstructions::Standard", "conditions": conds, "actions": acts, "events": list(sub)}


def comentario(t):
    return {"type": "BuiltinCommonInstructions::Comment", "color": {"b": 109, "g": 230, "r": 255, "textB": 0, "textG": 0, "textR": 0},
            "comment": t, "comment2": ""}


def recorrer(lst):
    for e in lst:
        yield e
        yield from recorrer(e.get("events", []))


def es(e, tipo, params, n=None):
    """¿El evento tiene la condición/acción `tipo` con esos primeros parámetros?"""
    n = n or len(params)
    return any(x["type"]["value"] == tipo and x["parameters"][:n] == params
               for x in e.get("conditions", []) + e.get("actions", []))


def marcado(lst, clave):
    return any(x.get("type", "").endswith("Comment") and x.get("comment", "").startswith(MK + "-" + clave) for x in lst)


def asegura_var(lista, nombre, valor):
    if not any(v["name"] == nombre for v in lista):
        lista.append({"name": nombre, "type": "string" if isinstance(valor, str) else "number", "value": valor})


def grupo(ev, nombre):
    return next(e for e in ev if e["type"].endswith("Group") and e.get("name") == nombre)


def buscar(lst, pred, que):
    r = [e for e in recorrer(lst) if pred(e)]
    if not r:
        sys.exit("No encontré: " + que)
    return r


def padre_de(raiz, hijo):
    for e in recorrer(raiz):
        if hijo in e.get("events", []):
            return e["events"]
    if hijo in raiz:
        return raiz
    sys.exit("sin padre")


def crea_objetivo(x, y, tipo, tiempo, anim):
    return [a("Create", "", "Objetivo", str(float(x)), str(float(y)), '"Juego"'),
            a("ModVarObjetTxt", "Objetivo", "Tipo", "=", '"%s"' % tipo),
            a("ModVarObjet", "Objetivo", "Tiempo", "=", str(tiempo)),
            a("SetAnimationName", "Objetivo", '"%s"' % anim)]


# ================================================================== Juego
def parchar_juego(J):
    for n, v in VARS:
        asegura_var(J["variables"], n, v)
    ev = J["events"]
    G = grupo(ev, "Objetivos y flecha")["events"]

    # 0) cuenta regresiva entre objetivos (solo se usa en Historia; en los demás modos queda en 0)
    if not marcado(G, "ESPERA"):
        k = next(i for i, e in enumerate(G) if not e["type"].endswith("Comment"))
        G[k:k] = [comentario(MK + "-ESPERA · Historia: pausa de %.1f s entre el letrero de cumplido y el siguiente objetivo." % ESPERA),
                  std([copy.deepcopy(NOCLI), c("VarScene", "ObjEspera", ">", "0")], [a("ModVarScene", "ObjEspera", "-", "TimeDelta()")])]

    # 1) elección de objetivos: ObjTotal y orden fijo en Historia
    sel = buscar(G, lambda e: es(e, "DepartScene", [""]) and es(e, "ModVarScene", ["ObjNum", "=", "1"]), "elección de objetivos")[0]
    if not es(sel, "ModVarScene", ["ObjTotal"]):
        sel["actions"].append(a("ModVarScene", "ObjTotal", "=", "3"))
    acts = [a("ModVarSceneTxt", "O%d" % (i + 1), "=", '"%s"' % t) for i, t in enumerate(ORDEN)] + \
           [a("ModVarScene", "ObjTotal", "=", str(len(ORDEN)))]
    hist = next((x for x in sel["events"] if any(y["type"]["value"] == "VarGlobalTxt" and y["parameters"][:3] == HIST["parameters"]
                                                 for y in x.get("conditions", []))), None)
    if hist is None:
        sel["events"].append(std([copy.deepcopy(HIST)], acts))
    else:
        hist["actions"] = acts                                  # se actualiza si cambia el orden (antes: 5 objetivos)

    # 2) ObjNum -> ObjTipo: O4, O5 y el final en ObjTotal + 1
    fin = buscar(G, lambda e: es(e, "ModVarSceneTxt", ["ObjTipo", "=", '"final"']), "ObjTipo final")[0]
    for x in fin["conditions"]:
        if x["type"]["value"] == "VarScene" and x["parameters"][:3] == ["ObjNum", "=", "4"]:
            x.update(c("BuiltinCommonInstructions::CompareNumbers", "Variable(ObjNum)", "=", "Variable(ObjTotal) + 1"))
    lst = padre_de(G, fin)
    for n in range(4, len(ORDEN) + 1):
        if not any(es(e, "ModVarSceneTxt", ["ObjTipo", "=", "VariableString(O%d)" % n]) for e in lst):
            k = lst.index(fin)
            lst.insert(k, std([copy.deepcopy(NOCLI), c("VarScene", "ObjNum", "=", str(n)), c("VarScene", "ObjTotal", ">=", str(n))],
                              [a("ModVarSceneTxt", "ObjTipo", "=", "VariableString(O%d)" % n)]))

    # 3) creación del objetivo
    crea = buscar(G, lambda e: es(e, "VarScene", ["ObjIni", "=", "0"]) and es(e, "VarSceneTxt", ["Estado", "=", '"juego"'])
                  and any(es(s, "VarSceneTxt", ["ObjTipo", "=", '"llamada"']) for s in e.get("events", [])), "creación de objetivos")[0]
    for x in crea["conditions"]:
        if x["type"]["value"] == "VarScene" and x["parameters"][:3] == ["ObjNum", "<=", "3"]:
            x.update(c("BuiltinCommonInstructions::CompareNumbers", "Variable(ObjNum)", "<=", "Variable(ObjTotal)"))
    if not es(crea, "BuiltinCommonInstructions::CompareNumbers", ["Variable(ObjEspera)"]):
        crea["conditions"].append(c("BuiltinCommonInstructions::CompareNumbers", "Variable(ObjEspera)", "<=", "0"))
    sub = crea["events"]
    if not marcado(sub, "CREA"):
        # llamada: en Historia, directo la computadora del CIC
        k = next(i for i, e in enumerate(sub) if es(e, "VarSceneTxt", ["ObjTipo", "=", '"llamada"']))
        sub[k]["conditions"].append(copy.deepcopy(NOHIST))
        sub.insert(k + 1, std([c("VarSceneTxt", "ObjTipo", "=", '"llamada"'), copy.deepcopy(HIST)],
                              crea_objetivo(COMPU[0], COMPU[1], "computadora", 20, "computadora") + [a("ModVarScene", "ExtraZombies", "=", "6")]))
        # luz: en Historia, los 3 interruptores dentro del CIC
        k = next(i for i, e in enumerate(sub) if es(e, "VarSceneTxt", ["ObjTipo", "=", '"luz"']) and es(e, "ModVarScene", ["Apagon", "=", "1"]))
        sub[k]["conditions"].append(copy.deepcopy(NOHIST))
        acts = [a("ModVarScene", "Interruptores", "=", "0"), a("ModVarScene", "Apagon", "=", "1")]
        for (x, y) in INTERRUPTORES:
            acts += crea_objetivo(x, y, "interruptor", 5, "interruptor")
        sub.insert(k + 1, std([c("VarSceneTxt", "ObjTipo", "=", '"luz"'), copy.deepcopy(HIST)], acts))
        # letrero del objetivo que empieza (después del "NUEVO OBJETIVO" de siempre, que lo sobrescribe)
        k = next(i for i, e in enumerate(sub) if es(e, "ModVarSceneTxt", ["Banner", "=", '"NUEVO OBJETIVO"']))
        nuevos = [comentario(MK + "-CREA · Historia: letrero con el número y el objetivo que empieza.")]
        for t in ORDEN:
            nuevos.append(std([copy.deepcopy(HIST), c("VarSceneTxt", "ObjTipo", "=", '"%s"' % t)],
                              [a("ModVarSceneTxt", "Banner", "=", '"OBJETIVO " + ToString(Variable(ObjNum)) + "/" + ToString(Variable(ObjTotal)) + " · %s"' % LETRERO[t]),
                               a("ResetTimer", "", '"banner"'), a("ModVarScene", "BannerSeg", "=", "3")]))
        sub[k + 1:k + 1] = nuevos
    # canepa (fase 61): el punto de la misión junto a Canepa; mantener F HABLAR s abre la conversación
    if not any(es(e, "VarSceneTxt", ["ObjTipo", "=", '"canepa"']) and es(e, "Create", ["", "Objetivo"]) for e in sub):
        k = next(i for i, e in enumerate(sub) if es(e, "ModVarSceneTxt", ["Banner", "=", '"NUEVO OBJETIVO"']))
        sub.insert(k, std([c("VarSceneTxt", "ObjTipo", "=", '"canepa"'), copy.deepcopy(HIST)],
                          crea_objetivo(CANEPA[0], CANEPA[1], "canepa", HABLAR, "camion")))
    # letreros que falten (al agregar una misión al orden)
    # solo los letreros de Historia ("OBJETIVO n/N · ..."); los eventos de Escape (p. ej. "¡SE FUE LA LUZ!") no se tocan
    letrero = lambda e, t: es(e, "VarSceneTxt", ["ObjTipo", "=", '"%s"' % t]) and es(e, "VarGlobalTxt", ["Modo", "=", '"historia"']) and \
        any(x["type"]["value"] == "ModVarSceneTxt" and x["parameters"][:1] == ["Banner"] and x["parameters"][2].startswith('"OBJETIVO "')
            for x in e.get("actions", []))
    for t in ORDEN:
        if not any(letrero(e, t) for e in sub):
            k = max(i for i, e in enumerate(sub) if any(letrero(e, u) for u in ORDEN))
            sub.insert(k + 1, std([copy.deepcopy(HIST), c("VarSceneTxt", "ObjTipo", "=", '"%s"' % t)],
                                  [a("ModVarSceneTxt", "Banner", "=", '"OBJETIVO " + ToString(Variable(ObjNum)) + "/" + ToString(Variable(ObjTotal)) + " · %s"' % LETRERO[t]),
                                   a("ResetTimer", "", '"banner"'), a("ModVarScene", "BannerSeg", "=", "3")]))
    # orden de los letreros = orden de las misiones (solo cosmético)
    idx = [i for i, e in enumerate(sub) if any(letrero(e, u) for u in ORDEN)]
    orden = sorted((sub[i] for i in idx), key=lambda e: next(n for n, u in enumerate(ORDEN) if letrero(e, u)))
    for i, e in zip(idx, orden):
        sub[i] = e

    # 4) final: en ObjTotal + 1 y después de la pausa
    fcrea = buscar(G, lambda e: es(e, "VarScene", ["ObjIni", "=", "0"]) and es(e, "ModVarObjetTxt", ["Objetivo", "Tipo", "=", '"camion"'])
                   and es(e, "ModVarSceneTxt", ["Banner"]), "creación del final")[0]
    for x in fcrea["conditions"]:
        if x["type"]["value"] == "VarScene" and x["parameters"][:3] == ["ObjNum", "=", "4"]:
            x.update(c("BuiltinCommonInstructions::CompareNumbers", "Variable(ObjNum)", "=", "Variable(ObjTotal) + 1"))
    if not es(fcrea, "BuiltinCommonInstructions::CompareNumbers", ["Variable(ObjEspera)"]):
        fcrea["conditions"].append(c("BuiltinCommonInstructions::CompareNumbers", "Variable(ObjEspera)", "<=", "0"))

    # 5) objetivo cumplido: en Historia el letrero dice cuál y se espera antes del siguiente
    p99 = buscar(G, lambda e: es(e, "VarScene", ["Paso", "=", "99"]) and es(e, "ModVarScene", ["ObjNum", "+", "1"]), "objetivo cumplido")[0]
    if not any(es(s, "ModVarScene", ["ObjEspera"]) for s in p99["events"]):
        p99["events"].append(std([copy.deepcopy(HIST)], [
            a("ModVarSceneTxt", "Banner", "=", '"¡OBJETIVO " + ToString(Variable(ObjNum) - 1) + "/" + ToString(Variable(ObjTotal)) + " CUMPLIDO!"'),
            a("ResetTimer", "", '"banner"'), a("ModVarScene", "BannerSeg", "=", str(ESPERA)),
            a("ModVarScene", "ObjEspera", "=", str(ESPERA))]))

    # 6) bidones: contar todos los que se recogen en el mismo cuadro (antes: +1 aunque fueran 2)
    for e in recorrer(G):
        acts = e.get("actions", [])
        if any(x["type"]["value"] == "Delete" and x["parameters"][:1] == ["Bidon"] for x in acts) and \
                any(x["type"]["value"] == "ModVarScene" and x["parameters"][:3] == ["Bidones", "+", "1"] for x in acts):
            e["actions"] = [a("ModVarScene", "Bidones", "+", "PickedInstancesCount(Bidon)")] + \
                           [x for x in acts if not (x["type"]["value"] == "ModVarScene" and x["parameters"][:1] == ["Bidones"])]

    # 6b) canepa (fase 61): al terminar de mantener F empieza la conversación (canepa.js). La misión se cumple cuando
    #     acaba el diálogo (canepa.js pone Paso = 99). CanepaCharla = 0 en la condición: una sola vez.
    if not marcado(G, "CANEPA"):
        ll = buscar(G, lambda e: es(e, "VarObjetTxt", ["Objetivo", "Tipo", "=", '"llaves"']) and es(e, "VarObjet", ["Objetivo", "Hecho", "=", "1"]),
                    "llaves cumplidas")[0]
        lst = padre_de(G, ll)
        k = lst.index(ll) + 1
        lst[k:k] = [comentario(MK + "-CANEPA · Historia: con Canepa se habla (scripts/canepa.js); la misión se cumple al terminar el diálogo."),
                    std([copy.deepcopy(NOCLI), c("VarObjetTxt", "Objetivo", "Tipo", "=", '"canepa"'), c("VarObjet", "Objetivo", "Hecho", "=", "1"),
                         c("VarScene", "CanepaCharla", "=", "0")],
                        [a("Delete", "Objetivo", ""), a("ModVarScene", "CanepaCharla", "=", "1")])]

    # 7) textos del HUD
    for e in recorrer(G):
        for x in e.get("actions", []):
            if x["type"]["value"] == "TextObject::String" and x["parameters"][:1] == ["TxtObjetivo"]:
                x["parameters"][-1] = x["parameters"][-1].replace('"/3"', '"/" + ToString(Variable(ObjTotal))')
    if not marcado(G, "TEXTO"):
        k = max(i for i, e in enumerate(G) if es(e, "VarSceneTxt", ["ObjTipo", "=", '"carnada"']) and es(e, "TextObject::String", ["TxtObjetivo"]))
        G[k + 1:k + 1] = [comentario(MK + "-TEXTO · Historia: textos propios (antes de sumar los contadores de bidones e interruptores).")] + [
            std([copy.deepcopy(NOCLI), copy.deepcopy(HIST), c("VarSceneTxt", "ObjTipo", "=", '"%s"' % t)],
                [a("TextObject::String", "TxtObjetivo", "=", '"Objetivo " + ToString(Variable(ObjNum)) + "/" + ToString(Variable(ObjTotal)) + NewLine() + "%s"' % HUD[t])])
            for t in ORDEN if t in HUD]
    texto = lambda e, t: es(e, "VarGlobalTxt", ["Modo", "=", '"historia"']) and es(e, "VarSceneTxt", ["ObjTipo", "=", '"%s"' % t]) and \
        es(e, "TextObject::String", ["TxtObjetivo"])
    for t in ORDEN:
        if t in HUD and not any(texto(e, t) for e in G):
            k = max(i for i, e in enumerate(G) if any(texto(e, u) for u in HUD))
            G.insert(k + 1, std([copy.deepcopy(NOCLI), copy.deepcopy(HIST), c("VarSceneTxt", "ObjTipo", "=", '"%s"' % t)],
                                [a("TextObject::String", "TxtObjetivo", "=", '"Objetivo " + ToString(Variable(ObjNum)) + "/" + ToString(Variable(ObjTotal)) + NewLine() + "%s"' % HUD[t])]))
    if not marcado(G, "SYNC"):
        k = max(i for i, e in enumerate(G) if es(e, "TextObject::String", ["TxtObjetivo"]))
        G[k + 1:k + 1] = [
            comentario(MK + "-SYNC · Historia: durante la pausa se anuncia el cumplido. ObjTxt lleva el texto a los clientes en línea."),
            std([copy.deepcopy(NOCLI), copy.deepcopy(HIST), c("VarScene", "ObjEspera", ">", "0")],
                [a("TextObject::String", "TxtObjetivo", "=",
                   '"¡Objetivo " + ToString(Variable(ObjNum) - 1) + "/" + ToString(Variable(ObjTotal)) + " cumplido!" + NewLine() + "Prepárense: viene el siguiente objetivo"')]),
            std([copy.deepcopy(NOCLI)], [a("ModVarSceneTxt", "ObjTxt", "=", "TxtObjetivo.String()")])]

    # 8) clientes en línea: muestran el texto del host
    H = grupo(ev, "Interfaz: HUD con paneles")["events"]
    if not marcado(H, "CLIENTE"):
        H[0:0] = [comentario(MK + "-CLIENTE · En línea: el texto del objetivo llega del host (ObjTxt)."),
                  std([copy.deepcopy(CLI), c("VarSceneTxt", "ObjTxt", "!=", '""')],
                      [a("TextObject::String", "TxtObjetivo", "=", "VariableString(ObjTxt)")])]

    # 9) otros "4" fijos
    for e in recorrer(grupo(ev, "Guía de los bots")["events"]):
        for x in e.get("conditions", []):
            if x["type"]["value"] == "VarScene" and x["parameters"][:3] == ["ObjNum", "<", "4"]:
                x.update(c("BuiltinCommonInstructions::CompareNumbers", "Variable(ObjNum)", "<=", "Variable(ObjTotal)"))
    for e in recorrer(grupo(ev, "Modo presentación (F1)")["events"]):
        for x in e.get("actions", []):
            if x["type"]["value"] == "ModVarScene" and x["parameters"][:3] == ["ObjNum", "=", "4"]:
                x["parameters"][2] = "Variable(ObjTotal) + 1"


# ================================================================== Menú
CARTAS = {0: 160, 1: 740, 2: 1320}         # x del marco de cada tarjeta en "ELIGE EL MODO" (Escape | Jefe | Historia)


def parchar_menu(d, M):
    ev = M["events"]
    # recurso e imagen de la tarjeta
    if not any(r["name"] == "p43_ilus_historia" for r in d["resources"]["resources"]):
        d["resources"]["resources"].append({"file": "assets/interfaz/ilus_modo_historia.png", "kind": "image", "metadata": "",
                                            "name": "p43_ilus_historia", "smoothed": False, "userAdded": True})
    ilus = next(o for o in M["objects"] if o["name"] == "IlusModo")
    if not any(x["name"] == "h" for x in ilus["animations"]):
        h = copy.deepcopy(next(x for x in ilus["animations"] if x["name"] == "l"))
        h["name"] = "h"
        h["directions"][0]["sprites"][0]["image"] = "p43_ilus_historia"
        ilus["animations"].append(h)

    # instancias de la 3.a tarjeta (Idx 2), copiadas de las de Jefe (Idx 1)
    idx = lambda i: next((v["value"] for v in i.get("initialVariables", []) if v["name"] == "Idx"), None)
    for nombre in ("MarcoModo", "IlusModo", "TxtCapA", "TxtCapB"):
        if not any(i["name"] == nombre and idx(i) == 2 for i in M["instances"]):
            base = next(i for i in M["instances"] if i["name"] == nombre and idx(i) == 1)
            n = copy.deepcopy(base)
            n["persistentUuid"] = str(uuid.uuid5(uuid.NAMESPACE_URL, "fdiz-historia-" + nombre))
            next(v for v in n["initialVariables"] if v["name"] == "Idx")["value"] = 2
            n["x"] = base["x"] + (CARTAS[2] - 1140)
            M["instances"].append(n)

    # posiciones en "ELIGE EL MODO" (3 tarjetas de 440 px)
    for e in recorrer(ev):
        cs = e.get("conditions", [])
        paso_modo = any(x["type"]["value"] == "VarSceneTxt" and x["parameters"][:3] == ["Paso", "=", '"modo"'] for x in cs)
        no_jt = any(x["type"]["value"] == "VarSceneTxt" and x["parameters"][:3] == ["Paso", "!=", '"jefetipo"'] for x in cs)
        i_ = next((x["parameters"][3] if len(x["parameters"]) > 3 else None for x in cs if x["type"]["value"] == "VarObjet" and x["parameters"][1:2] == ["Idx"]), None)
        for x in e.get("actions", []):
            p = x["parameters"]
            if x["type"]["value"] != "MettreX":
                continue
            if paso_modo and p[0] in ("MarcoModo", "IlusModo") and i_ in ("0", "1", "2"):
                p[2] = str(CARTAS[int(i_)] + (50 if p[0] == "IlusModo" else 0))
            elif paso_modo and p[0] == "VidIlusEscape":
                p[2] = str(CARTAS[0] + 50)
            elif paso_modo and p[0] == "VidIlusJefe":
                p[2] = str(CARTAS[1] + 50)
            elif p[0] in ("TxtCapA", "TxtCapB") and i_ in ("0", "1", "2") and (no_jt or (paso_modo and i_ == "2")):
                p[2] = "%d - %s.Width() / 2" % (CARTAS[int(i_)] + 220, p[0])
        # textos e ilustración de la tarjeta 2 (antes era una tarjeta "EN LÍNEA" sin instancias)
        if paso_modo or no_jt:
            for x in e.get("actions", []):
                p = x["parameters"]
                if i_ == "2" and x["type"]["value"] == "TextObject::String" and p[0] == "TxtCapA":
                    p[2] = '"HISTORIA"'
                if i_ == "2" and x["type"]["value"] == "TextObject::String" and p[0] == "TxtCapB":
                    p[2] = '"%d misiones en orden · 1 a 4 jugadores"' % len(ORDEN)
                if i_ == "2" and x["type"]["value"] == "SetAnimationName" and p[0] == "IlusModo" and p[1] == '"o"':
                    p[1] = '"h"'

    # navegación: izquierda/arriba y derecha/abajo entre 3 tarjetas (antes Derecha estaba en los dos eventos y se anulaba)
    for e in recorrer(ev):
        if not any(x["type"]["value"] == "VarSceneTxt" and x["parameters"][:3] == ["Paso", "=", '"modo"'] for x in e.get("conditions", [])):
            continue
        for x in e.get("actions", []):
            if x["type"]["value"] == "ModVarScene" and x["parameters"][0] == "Sel" and x["parameters"][2].startswith("mod(Variable(Sel)"):
                orc = next((y for y in e["conditions"] if y["type"]["value"] == "BuiltinCommonInstructions::Or"), None)
                sube = orc and any(s["parameters"][1:2] in (["Up"], ["w"]) for s in orc["subInstructions"])
                if sube:
                    orc["subInstructions"] = [s for s in orc["subInstructions"]
                                              if not (s["parameters"][1:2] in (["Right"], ["d"]) or s["parameters"][2:3] == ['"Right"'])]
                    x["parameters"][2] = "mod(Variable(Sel) + 2, 3)"
                else:
                    x["parameters"][2] = "mod(Variable(Sel) + 1, 3)"

    # confirmar: la tarjeta 2 ya no está bloqueada y lleva a Local / En línea de Historia (JT = 2)
    conf = next(e for e in ev if any(x["type"]["value"] == "VarSceneTxt" and x["parameters"][:3] == ["Paso", "=", '"modo"'] for x in e.get("conditions", []))
                and any(es(s, "ModVarGlobalTxt", ["Modo", "=", '"escape"']) for s in e.get("events", [])))
    conf["conditions"] = [x for x in conf["conditions"] if not (x["type"]["value"] == "VarScene" and x["parameters"][:3] == ["Sel", "!=", "2"])]
    if not any(es(s, "ModVarGlobalTxt", ["Modo", "=", '"historia"']) for s in conf["events"]):
        conf["events"].append(std([c("VarScene", "Sel", "=", "2")], [
            a("ModVarGlobalTxt", "Modo", "=", '"historia"'), a("ModVarScene", "S1Ctl", "=", "0"),
            a("ModVarSceneTxt", "Paso", "=", '"jefetipo"'), a("ModVarScene", "Sel", "=", "0"), a("ModVarScene", "JT", "=", "2"),
            a("ModVarGlobal", "OnlineJefe", "=", "0"), a("ModVarGlobal", "OnlineEsc", "=", "0")]))
    k = ev.index(conf)
    if not marcado(ev, "CARTAS"):
        clic = [comentario(MK + "-CARTAS · Modo Historia: tecla 3 y clic sobre cada tarjeta (el clic también confirma, evento siguiente).")]
        clic.append(std([c("VarSceneTxt", "Paso", "=", '"modo"'), c("KeyReleased", "", "Num3")], [a("ModVarScene", "Sel", "=", "2")]))
        for i, x0 in CARTAS.items():
            clic.append(std([c("VarSceneTxt", "Paso", "=", '"modo"'), c("MouseButtonReleased", "", "Left"),
                             c("BuiltinCommonInstructions::CompareNumbers", "MouseX()", ">=", str(x0)),
                             c("BuiltinCommonInstructions::CompareNumbers", "MouseX()", "<", str(x0 + 440)),
                             c("BuiltinCommonInstructions::CompareNumbers", "MouseY()", ">=", "250"),
                             c("BuiltinCommonInstructions::CompareNumbers", "MouseY()", "<", "790")],
                            [a("ModVarScene", "Sel", "=", str(i))]))
        ev[k:k] = clic

    # paso "jefetipo" de Historia: copia de los eventos de Escape (JT = 0) con JT = 2
    if not marcado(ev, "JT2"):
        copias = [comentario(MK + "-JT2 · Historia: LOCAL / EN LÍNEA igual que Escape, con Modo historia (OnlineEsc 2 al ir a la sala).")]
        for e in list(ev):
            if e.get("type", "").endswith("Standard") and es(e, "VarScene", ["JT", "=", "0"]):
                n = copy.deepcopy(e)
                for x in n["conditions"]:
                    if x["type"]["value"] == "VarScene" and x["parameters"][:3] == ["JT", "=", "0"]:
                        x["parameters"][2] = "2"
                for x in recorrer_acciones(n):
                    p = x["parameters"]
                    if x["type"]["value"] == "ModVarGlobalTxt" and p[:1] == ["Modo"]:
                        p[2] = '"historia"'
                    if x["type"]["value"] == "ModVarGlobal" and p[:3] == ["OnlineEsc", "=", "1"]:
                        p[2] = "2"
                    if x["type"]["value"] == "TextObject::String" and p[0] == "TxtMenu" and p[2] == '"ESCAPE"':
                        p[2] = '"HISTORIA"'
                    if x["type"]["value"] == "TextObject::String" and p[0] == "TxtCapB" and p[2] == '"1 a 4 jugadores + bots"':
                        p[2] = '"1 a 4 jugadores + bots · %d misiones"' % len(ORDEN)
                copias.append(n)
        ev.extend(copias)
        # la 3.a tarjeta no se ve en el paso Local / En línea
        ev.extend([std([c("VarSceneTxt", "Paso", "=", '"jefetipo"'), c("VarObjet", nm, "Idx", "=", "2")], [a("Cache", nm)])
                   for nm in ("TxtCapA", "TxtCapB")])
    for x in recorrer_acciones({"events": ev}):
        p = x["parameters"]
        if x["type"]["value"] == "TextObject::String" and p[:1] == ["TxtCapB"] and re.fullmatch(r'"1 a 4 jugadores \+ bots · \d (objetivos|misiones)"', p[2]):
            p[2] = '"1 a 4 jugadores + bots · %d misiones"' % len(ORDEN)

    # volver de la sala en línea: OnlineEsc 1 = Escape, 2 = Historia
    vol = next(e for e in ev if es(e, "DepartScene", [""]) and es(e, "VarGlobal", ["OnlineEsc"]))
    for x in vol["conditions"]:
        if x["type"]["value"] == "VarGlobal" and x["parameters"][:3] == ["OnlineEsc", ">=", "1"]:
            x["parameters"][1:3] = ["=", "1"]
    if not any(es(e, "VarGlobal", ["OnlineEsc", "=", "2"]) for e in ev):
        n = copy.deepcopy(vol)
        for x in n["conditions"]:
            if x["type"]["value"] == "VarGlobal" and x["parameters"][:1] == ["OnlineEsc"]:
                x["parameters"][1:3] = ["=", "2"]
        for x in n["actions"]:
            if x["type"]["value"] == "ModVarScene" and x["parameters"][:1] == ["JT"]:
                x["parameters"][2] = "2"
            if x["type"]["value"] == "ModVarGlobalTxt" and x["parameters"][:1] == ["Modo"]:
                x["parameters"][2] = '"historia"'
        ev.insert(ev.index(vol) + 1, n)


def recorrer_acciones(e):
    for x in recorrer([e]):
        yield from x.get("actions", [])


# ================================================================== red
NET_PARCHES = [
    ('try { N.preJefe = scn.getGame().getVariables().get("OnlineJefe").getAsNumber() >= 1; } catch (e) { N.preJefe = false; }',
     'try { N.preJefe = scn.getGame().getVariables().get("OnlineJefe").getAsNumber() >= 1; } catch (e) { N.preJefe = false; } '
     'try { N.preHist = !N.preJefe && scn.getGame().getVariables().get("OnlineEsc").getAsNumber() === 2; } catch (e) { N.preHist = false; }'),
    ('mode: (N.preJefe ? "jefe" : "escape")', 'mode: (N.preJefe ? "jefe" : (N.preHist ? "historia" : "escape"))'),
    ('"Modo: " + (jf ? "JEFE DE ZOMBIES" : "ESCAPE")', '"Modo: " + (jf ? "JEFE DE ZOMBIES" : (L.mode === "historia" ? "HISTORIA" : "ESCAPE"))'),
]


def parchar_net(s):
    for viejo, nuevo in NET_PARCHES:
        if nuevo in s:
            continue
        if viejo not in s:
            sys.exit("No encontré en net_core: " + viejo[:70])
        s = s.replace(viejo, nuevo)
    return s


def main():
    d = json.load(open(PRY, encoding="utf-8"))
    resp = os.path.join(AQUI, "..", "respaldos")
    os.makedirs(resp, exist_ok=True)
    bak = os.path.join(resp, "antes_de_fase55_%s.json" % datetime.date.today().strftime("%Y%m%d"))
    if not os.path.exists(bak):
        shutil.copy(PRY, bak)
    if not os.path.exists(os.path.join(AQUI, "..", "FDI-Z", "assets", "interfaz", "ilus_modo_historia.png")):
        sys.exit("Falta la ilustración: corre primero fase55_ilus_historia.py")
    L = {l["name"]: l for l in d["layouts"]}
    parchar_juego(L["Juego"])
    parchar_menu(d, L["Menu"])

    nucleo = next(e for e in recorrer(L["Titulo"]["events"]) if e.get("type", "").endswith("JsCode") and "gdjs.fdizNetCfg=" in e["inlineCode"])
    code = nucleo["inlineCode"]
    m = re.search(r"gdjs\.fdizNetCfg=", code)
    cfg, fin = json.JSONDecoder().raw_decode(code, m.end())
    for n, _ in VARS:
        if n not in cfg["sv"]:
            cfg["sv"].append(n)
    code = code[:m.end()] + json.dumps(cfg, ensure_ascii=False) + code[fin:]
    nucleo["inlineCode"] = parchar_net(code)

    tmp = PRY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=2))
    os.replace(tmp, PRY)
    s = open(NET, encoding="utf-8", newline="").read()
    s2 = parchar_net(s)
    if s2 != s:
        open(NET, "w", encoding="utf-8", newline="").write(s2)
    print("Fase 55 aplicada (modo Historia).")


if __name__ == "__main__":
    main()
