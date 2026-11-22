"""Fase 56 · Interacción con F / A: una acción a la vez, según el objetivo más cercano. Idempotente.

Uso (desde la carpeta fdiz, con GDevelop CERRADO):  python gdevelop/scripts/fase56_interaccion.py
Va al final de la cadena (después de fase55). Si se vuelve a correr una fase que regenere los eventos de Juego
(fase5, fases_6_a_11, fase12, fase17, fase25, fase40...), correr esta fase otra vez.
Pruebas: node gdevelop/scripts/prueba_usar.js

Qué hace en FDI-Z.json (lógica en scripts/usar.js, ver su encabezado):
  * Módulo usar.js (evento JS FDIZ-FASE56-MOD). Al inicio de "Mapa: choques y puertas" el host elige qué hace cada
    jugador con Usar (gdjs.fdizUsar.elegir) y en "Interfaz: HUD con paneles" todos dibujan la indicación.
  * Cada acción lee su propia bandera en vez de Usando:
      puertas      Sup.UsaPuerta  + Puerta.Elegida   (se quitan R del teclado y R remoto para abrir puertas: solo F / A)
      levantar     J<n>Rev  (antes J<n>Usa)      y si nadie lo ayuda el avance vuelve a 0 (antes bajaba poco a poco)
      curar        J<n>Cur  (antes J<n>Usa)
      objetivos    Sup.UsaObjetivo + Objetivo.Elegida
      lockers      Sup.UsaCofre
      profes       profes.js abre el diálogo solo si la acción elegida para ese jugador es "profe"; curar a un profe
                   mordido lee UsaCurar.
  * Textos de controles del menú de pausa (y su fuente fase27_jefe_y_controles.py) y comentarios de los eventos.
  * Red: Accion, UsarTxt y UsarProg del Sup se sincronizan (los clientes dibujan la indicación de su jugador).
"""
import copy, datetime, json, os, re, shutil, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
MK = "FDIZ-FASE56"
NOCLI = {"type": {"inverted": False, "value": "VarGlobal"}, "parameters": ["NetRol", "!=", "2"]}

SUP_VARS = [("UsaPuerta", 0), ("UsaRevivir", 0), ("UsaCurar", 0), ("UsaObjetivo", 0), ("UsaCofre", 0),
            ("Accion", ""), ("UsarTxt", ""), ("UsarProg", 0)]
SYNC = [("Accion", "s"), ("UsarTxt", "s"), ("UsarProg", "n")]

CTL_F = ('"F (mantener)  usar puertas, cofres," + NewLine() + " máquinas"',
         '"F (mantener)  abrir puertas, salvar," + NewLine() + " revisar y usar objetivos"')
CTL_A = ('"A (mantener)  usar puertas, cofres," + NewLine() + " máquinas"',
         '"A (mantener)  abrir puertas, salvar," + NewLine() + " revisar y usar objetivos"')
FUENTES = {  # textos iguales en los scripts que los generan
    "fase27_jefe_y_controles.py": [("F (mantener)  usar puertas, cofres,\\n máquinas", "F (mantener)  abrir puertas, salvar,\\n revisar y usar objetivos"),
                                   ("A (mantener)  usar puertas, cofres,\\n máquinas", "A (mantener)  abrir puertas, salvar,\\n revisar y usar objetivos")],
    "fase17_navegacion.py": [("Puerta: mantener Usar (F, A del control, o bots) o R en teclado junto a ella ",
                              "Puerta: mantener Usar (F, A del control, o bots) junto a ella; con varias cosas cerca, usar.js (fase 56) elige una ")],
}
COMENTARIOS = [
    ("Puerta: mantener Usar (F, A del control, o bots) o R en teclado junto a ella",
     "Puerta: mantener Usar (F, A del control, o bots) junto a ella; si hay varias cosas cerca, usar.js (fase 56) elige la más cercana y solo esa avanza"),
    ("F usar/revivir, Q habilidad", "F (mantener) interactuar: una acción a la vez, la más cercana, Q habilidad"),
    ("A usar/revivir.", "A (mantener) interactuar."),
    ("Un compañero de pie revive manteniendo Usar 3 s junto a él (vuelve con 50% de vida).",
     "Un compañero de pie lo salva manteniendo Usar 3 s junto a él (vuelve con 50% de vida); si suelta o se aleja, el avance se pierde."),
]


def c(tipo, *p, inv=False):
    return {"type": {"inverted": inv, "value": tipo}, "parameters": list(p)}


def a(tipo, *p):
    return {"type": {"value": tipo}, "parameters": list(p)}


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
    return any(x.get("type", "").endswith("JsCode") and x.get("inlineCode", "").startswith("/*" + marca) for x in recorrer([e]))


def quitar(lst, marca):
    lst[:] = [e for e in lst if not (tiene_marca(e, marca) and len(list(recorrer([e]))) <= 2)]


def grupo(ev, nombre):
    return next(e for e in ev if e["type"].endswith("Group") and e.get("name") == nombre)


def asegura_var(lista, nombre, valor):
    if not any(v["name"] == nombre for v in lista):
        lista.append({"name": nombre, "type": "string" if isinstance(valor, str) else "number", "value": valor})


def cambia_cond(e, tipo, viejo, nuevo):
    n = 0
    for x in e.get("conditions", []):
        if x["type"]["value"] == tipo and x["parameters"][:len(viejo)] == viejo:
            x["parameters"][:len(nuevo)] = nuevo
            n += 1
    return n


def main():
    d = json.load(open(PRY, encoding="utf-8"))
    resp = os.path.join(AQUI, "..", "respaldos")
    os.makedirs(resp, exist_ok=True)
    bak = os.path.join(resp, "antes_de_fase56_%s.json" % datetime.date.today().strftime("%Y%m%d"))
    if not os.path.exists(bak):
        shutil.copy(PRY, bak)
    L = {l["name"]: l for l in d["layouts"]}
    J = L["Juego"]
    ob = {o["name"]: o for o in J["objects"]}
    cuenta = {}

    # ---------------- objetos y variables
    for n, v in SUP_VARS:
        asegura_var(ob["Sup"]["variables"], n, v)
    asegura_var(ob["Puerta"]["variables"], "Elegida", 0)
    asegura_var(ob["Objetivo"]["variables"], "Elegida", 0)
    if "TxtUsar" not in ob:
        t = copy.deepcopy(ob["TxtProfe"]); t["name"] = "TxtUsar"; J["objects"].append(t)
    if "UsarDib" not in ob:
        t = copy.deepcopy(ob["ProfDib"]); t["name"] = "UsarDib"; J["objects"].append(t)
    for j in range(1, 5):
        asegura_var(J["variables"], "J%dRev" % j, 0)
        asegura_var(J["variables"], "J%dCur" % j, 0)

    ev = J["events"]
    # ---------------- módulo
    quitar(ev, MK + "-MOD")
    ev.insert(0, js(open(os.path.join(AQUI, "usar.js"), encoding="utf-8").read(), MK + "-MOD"))
    # profes.js actualizado (diálogo solo si la acción elegida es "profe"; curar profe con UsaCurar)
    mod40 = next((e for e in ev if e.get("type", "").endswith("JsCode") and e["inlineCode"].startswith("/*FDIZ-FASE40-MOD")), None)
    if mod40:
        mod40["inlineCode"] = "/*FDIZ-FASE40-MOD*/\n" + open(os.path.join(AQUI, "profes.js"), encoding="utf-8").read()
    # medios.js (fase 46 de cesar) actualizado: el texto "toma las llaves… %" solo cuenta a quien el árbitro le dio el objetivo
    mod46 = next((e for e in ev if e.get("type", "").endswith("JsCode") and e["inlineCode"].startswith("/*FDIZ-FASE46-MOD")), None)
    if mod46:
        mod46["inlineCode"] = "/*FDIZ-FASE46-MOD*/\n" + open(os.path.join(AQUI, "medios.js"), encoding="utf-8").read()

    # ---------------- puertas
    gm = grupo(ev, "Mapa: choques y puertas")["events"]
    quitar(gm, MK + "-ELEGIR")
    k = next(i for i, e in enumerate(gm) if not e["type"].endswith("Comment"))
    gm.insert(k, std([copy.deepcopy(NOCLI)], [], [js("if (gdjs.fdizUsar) gdjs.fdizUsar.elegir(runtimeScene);", MK + "-ELEGIR")]))
    for e in recorrer(gm):
        if e.get("type", "").endswith("ForEach") and e.get("object") == "Puerta":
            sub = e["events"]
            antes = len(sub)
            sub[:] = [s for s in sub if not any((x["type"]["value"] == "KeyPressed" and x["parameters"][-1] == "r")
                                                or (x["type"]["value"] == "VarObjet" and x["parameters"][:2] == ["Sup", "NetDr"])
                                                for x in s.get("conditions", []))]
            cuenta["puertas: R quitada"] = antes - len(sub)
            for s in sub:
                if cambia_cond(s, "VarObjet", ["Sup", "Usando", "=", "1"], ["Sup", "UsaPuerta"]):
                    cuenta["puertas: UsaPuerta"] = 1
                if any(x["parameters"][:2] == ["Sup", "UsaPuerta"] for x in s["conditions"]) and \
                        not any(x["parameters"][:2] == ["Puerta", "Elegida"] for x in s["conditions"]):
                    s["conditions"].append(c("VarObjet", "Puerta", "Elegida", "=", "1"))

    # ---------------- levantar (J<n>Rev) y curar (J<n>Cur)
    gp = grupo(ev, "Posiciones de jugadores")["events"]
    for e in recorrer(gp):
        for x in list(e.get("actions", [])):
            m = re.fullmatch(r"J(\d)Usa", str(x["parameters"][0])) if x["type"]["value"] == "ModVarScene" else None
            if m:
                j = m.group(1)
                if not any(y["parameters"][:1] == ["J%sRev" % j] for y in e["actions"]):
                    e["actions"] += [a("ModVarScene", "J%sRev" % j, "=", "Sup.Variable(UsaRevivir)"),
                                     a("ModVarScene", "J%sCur" % j, "=", "Sup.Variable(UsaCurar)")]
                    cuenta["posiciones"] = cuenta.get("posiciones", 0) + 1
    gv = grupo(ev, "Vida, caída y revivir")["events"]
    for e in recorrer(gv):
        for j in range(1, 5):
            if cambia_cond(e, "VarScene", ["J%dUsa" % j, "=", "1"], ["J%dRev" % j]):
                cuenta["levantar"] = cuenta.get("levantar", 0) + 1
        for x in e.get("actions", []):
            if x["type"]["value"] == "ModVarObjet" and x["parameters"][:3] == ["Sup", "Revivir", "="] and "max(0" in x["parameters"][3]:
                x["parameters"][3] = "0"                    # soltar o alejarse cancela el avance
                cuenta["levantar: cancela"] = 1
    gc = grupo(ev, "Compañeros mordidos: salvar o no salvar")["events"]
    for e in recorrer(gc):
        for j in range(1, 5):
            if cambia_cond(e, "VarScene", ["J%dUsa" % j, "=", "1"], ["J%dCur" % j]):
                cuenta["curar"] = cuenta.get("curar", 0) + 1

    # ---------------- objetivos y lockers
    for e in recorrer(grupo(ev, "Objetivos y flecha")["events"]):
        if cambia_cond(e, "VarObjet", ["Sup", "Usando", "=", "1"], ["Sup", "UsaObjetivo"]):
            cuenta["objetivos"] = 1
        if any(x["parameters"][:2] == ["Sup", "UsaObjetivo"] for x in e.get("conditions", [])) and \
                not any(x["parameters"][:2] == ["Objetivo", "Elegida"] for x in e["conditions"]):
            e["conditions"].append(c("VarObjet", "Objetivo", "Elegida", "=", "1"))
    for e in recorrer(grupo(ev, "Lockers, mochilas, máquinas y dinero")["events"]):
        if cambia_cond(e, "VarObjet", ["Sup", "Usando", "=", "1"], ["Sup", "UsaCofre"]):
            cuenta["lockers"] = 1

    # ---------------- indicación (todos, también clientes)
    gh = grupo(ev, "Interfaz: HUD con paneles")["events"]
    quitar(gh, MK + "-DIBUJO")
    gh.append(js("if (gdjs.fdizUsar) gdjs.fdizUsar.dibujar(runtimeScene);", MK + "-DIBUJO"))

    # ---------------- textos
    for e in recorrer(ev):
        if e.get("type", "").endswith("Comment"):
            for viejo, nuevo in COMENTARIOS:
                e["comment"] = e["comment"].replace(viejo, nuevo)
        for x in e.get("actions", []):
            if x["type"]["value"] == "TextObject::String" and x["parameters"][:1] in (["TxtPausaCtl1"], ["TxtPausaCtl2"]):
                for viejo, nuevo in (CTL_F, CTL_A):
                    if viejo in x["parameters"][-1]:
                        x["parameters"][-1] = x["parameters"][-1].replace(viejo, nuevo)
                        cuenta["textos de pausa"] = cuenta.get("textos de pausa", 0) + 1

    # ---------------- red
    nucleo = next(e for e in recorrer(L["Titulo"]["events"]) if e.get("type", "").endswith("JsCode") and "gdjs.fdizNetCfg=" in e["inlineCode"])
    code = nucleo["inlineCode"]
    m = re.search(r"gdjs\.fdizNetCfg=", code)
    cfg, fin = json.JSONDecoder().raw_decode(code, m.end())
    spec = next(s for s in cfg["objs"] if s["n"] == "Sup")
    for n, t in SYNC:
        if not any(v[0] == n for v in spec["v"]):
            spec["v"].append([n, t])
    nucleo["inlineCode"] = code[:m.end()] + json.dumps(cfg, ensure_ascii=False) + code[fin:]

    tmp = PRY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=2))
    os.replace(tmp, PRY)

    for nombre, cambios in FUENTES.items():
        ruta = os.path.join(AQUI, nombre)
        s = open(ruta, encoding="utf-8", newline="").read()
        s2 = s
        for viejo, nuevo in cambios:
            s2 = s2.replace(viejo, nuevo)
        if s2 != s:
            open(ruta, "w", encoding="utf-8", newline="").write(s2)
            cuenta["fuente " + nombre] = 1
    print("Fase 56 aplicada:", cuenta)


if __name__ == "__main__":
    main()
