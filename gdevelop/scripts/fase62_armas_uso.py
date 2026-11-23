"""Fase 62 · Uso de las armas: pistola pequeña inicial, mira, munición en el HUD y animación con pistola. Idempotente.

Uso (desde la carpeta fdiz, con GDevelop CERRADO), después de fase59_armas_fuego.py:
    python gdevelop/scripts/fase62_arte_pistola.py      # (si cambian los sprites) mira, pistola y animaciones placeholder
    python gdevelop/scripts/fase62_armas_uso.py
    node gdevelop/scripts/prueba_armas.js
Si se vuelve a correr fase25_online.py (compuerta de host en los eventos JS sueltos de Juego), correr esta fase otra vez.

Qué hace en Juego (todos los modos: Escape, Historia y Jefe; sin red, host y clientes):
  * Pistola pequeña ("pistolita", 9 balas): desde la fase 67 NADIE empieza con ella. armas.js la pone en el piso del
    salón donde empieza el jugador 1 y se recoge como las demás armas (ver fase67_pistola_inicial.py). Esta fase quita
    el evento viejo que la equipaba en "Inicio de supervivientes".
  * Animaciones <personaje>_pistola_lado y _pistola_abajo (3 cuadros, placeholders de fase62_arte_pistola.py) con el
    mismo origen y máscara de colisión que la base (pegar_lado cuadro 1 / pegar_abajo cuadro 0).
  * Objetos: Mira (sprite de la mira), TxtBalas (texto como TxtCd) con 4 instancias junto al ícono del arma de cada
    panel, BalasDib (dibujador para el cargador).
  * scripts/armas.js: FDIZ-FASE62-MOD y -TICK arriba de todo (cada máquina) y FDIZ-FASE62-ANIM al final de
    "Combate: pegar" (host).
"""
import copy, datetime, json, os, shutil, uuid
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
PRY = os.path.join(RAIZ, "gdevelop", "FDI-Z", "FDI-Z.json")
GEN = os.path.join(RAIZ, "generado", "sprites")
REL = "../../generado/sprites/"
MK = "FDIZ-FASE62"
INICIAL = ("pistolita", 9)                      # pistola pequeña (ya no se equipa al empezar: fase 67)
TXT_POS = {1: (409, 104), 2: (1871, 104), 3: (409, 988), 4: (1871, 988)}   # a la derecha del ícono del arma


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


def es(e, tipo, params):
    return any(x["type"]["value"] == tipo and x["parameters"][:len(params)] == params for x in e.get("conditions", []) + e.get("actions", []))


def es_js(e, marca):
    return e.get("type", "").endswith("JsCode") and e.get("inlineCode", "").startswith("/*" + marca)


def quitar(lst, pred):
    lst[:] = [e for e in lst if not pred(e)]
    for e in lst:
        if e.get("events"):
            quitar(e["events"], pred)


def recurso(d, nombre, archivo):
    if not any(r["name"] == nombre for r in d["resources"]["resources"]):
        d["resources"]["resources"].append({"file": archivo, "kind": "image", "metadata": "", "name": nombre, "smoothed": False, "userAdded": True})


def grupo(ev, nombre):
    return next(e for e in recorrer(ev) if e.get("type", "").endswith("Group") and e.get("name") == nombre)


def main():
    d = json.load(open(PRY, encoding="utf-8"))
    resp = os.path.join(RAIZ, "gdevelop", "respaldos")
    os.makedirs(resp, exist_ok=True)
    bak = os.path.join(resp, "antes_de_fase62_%s.json" % datetime.date.today().strftime("%Y%m%d"))
    if not os.path.exists(bak):
        shutil.copy(PRY, bak)
    J = next(l for l in d["layouts"] if l["name"] == "Juego")
    ob = {o["name"]: o for o in J["objects"]}
    res = {r["name"]: r["file"] for r in d["resources"]["resources"]}
    hecho = []
    if not any(x["name"] == INICIAL[0] for x in ob["HudIcono"]["animations"]):
        raise SystemExit("Falta la pistola pequeña en el proyecto: corre antes fase59_armas_fuego.py")

    # ---------------- animaciones de pistola (placeholders) del objeto Sup
    sup = ob["Sup"]
    anims = {x["name"]: x for x in sup["animations"]}
    n_anim = 0
    for nombre in sorted(anims):
        if not nombre.endswith("_pegar_lado") or nombre[:-11] + "_pegar_abajo" not in anims:
            continue
        pj = nombre[:-11]
        for dir_, fuente, idx in (("lado", "_pegar_lado", 1), ("abajo", "_pegar_abajo", 0)):
            sprites = anims[pj + fuente]["directions"][0]["sprites"]
            base = sprites[min(idx, len(sprites) - 1)]
            carpeta_res = os.path.dirname(os.path.dirname(base["image"])) + "/pistola_" + dir_
            carpeta_arch = os.path.dirname(os.path.dirname(res[base["image"]])) + "/pistola_" + dir_
            nuevos = []
            for k in range(3):
                nom = "%s/pistola_%s_%02d.png" % (carpeta_res, dir_, k)
                arch = "%s/pistola_%s_%02d.png" % (carpeta_arch, dir_, k)
                if not os.path.exists(os.path.normpath(os.path.join(RAIZ, "gdevelop", "FDI-Z", arch))):
                    raise SystemExit("Falta %s: corre fase62_arte_pistola.py" % arch)
                recurso(d, nom, arch)
                sp = copy.deepcopy(base); sp["image"] = nom
                nuevos.append(sp)
            an = {"name": "%s_pistola_%s" % (pj, dir_), "useMultipleDirections": False,
                  "directions": [{"looping": False, "timeBetweenFrames": 0.07, "sprites": nuevos}]}
            viejo = next((i for i, x in enumerate(sup["animations"]) if x["name"] == an["name"]), None)
            if viejo is None:
                sup["animations"].append(an)
            else:
                sup["animations"][viejo] = an
            n_anim += 1
    hecho.append("animaciones: %d" % n_anim)

    # ---------------- objetos
    # (pistolita.png no se registra: el sprite de piso es pistolita_piso.png, de la fase 67)
    d["resources"]["resources"] = [r for r in d["resources"]["resources"] if r["name"] != "objetos/armas/pistolita.png"]
    for nombre, archivo in (("objetos/armas/mira.png", "objetos/armas/mira.png"),):
        if not os.path.exists(os.path.join(GEN, *archivo.split("/"))):
            raise SystemExit("Falta %s: corre fase62_arte_pistola.py" % archivo)
        recurso(d, nombre, REL + archivo)
    if "Mira" not in ob:
        w, h = Image.open(os.path.join(GEN, "objetos", "armas", "mira.png")).size
        m = copy.deepcopy(ob["ArmaPiso"]); m["name"] = "Mira"; m["variables"] = []; m["behaviors"] = []; m["effects"] = []
        m["animations"] = [{"name": "mira", "useMultipleDirections": False, "directions": [{"looping": False, "timeBetweenFrames": 0.08, "sprites": [
            {"hasCustomCollisionMask": False, "image": "objetos/armas/mira.png", "points": [], "originPoint": {"name": "origine", "x": 0, "y": 0},
             "centerPoint": {"automatic": True, "name": "centre", "x": 0, "y": 0}, "customCollisionMask": []}]}]}]
        J["objects"].append(m); hecho.append("Mira")
    if "TxtBalas" not in ob:
        t = copy.deepcopy(ob["TxtCd"]); t["name"] = "TxtBalas"; J["objects"].append(t); hecho.append("TxtBalas")
    if "BalasDib" not in ob:
        t = copy.deepcopy(ob["ProfDib"]); t["name"] = "BalasDib"; J["objects"].append(t); hecho.append("BalasDib")
    # TxtBalas NO va en el grupo HudFijo: armas.js decide cuándo se ve (si el HUD lo mostrara, quedaría un número viejo)
    base_txt = next(i for i in J["instances"] if i["name"] == "TxtCd")
    for j, (x, y) in TXT_POS.items():
        uid = str(uuid.uuid5(uuid.NAMESPACE_URL, "fdiz-txtbalas-%d" % j))
        J["instances"] = [i for i in J["instances"] if i.get("persistentUuid") != uid]
        n = copy.deepcopy(base_txt)
        n.update({"persistentUuid": uid, "x": x, "y": y, "name": "TxtBalas"})
        n["initialVariables"] = [{"name": "Jugador", "type": "number", "value": j}]
        J["instances"].append(n)

    # ---------------- la pistola pequeña ya no se da al iniciar cada Sup (fase 67)
    ini = next(e for e in recorrer(grupo(J["events"], "Inicio de supervivientes")["events"])
               if es(e, "VarObjet", ["Sup", "Init", "=", "0"]) and es(e, "ModVarObjet", ["Sup", "Init", "=", "1"]))
    # fase 67: ya NO se equipa al empezar; la pistola está en el piso del salón (armas.js la pone y se recoge como las demás).
    # Se quita el evento que la daba (si un proyecto viejo lo tiene).
    antes = len(ini["events"])
    ini["events"] = [e for e in ini["events"] if not es(e, "ModVarObjetTxt", ["Sup", "Arma", "=", '"%s"' % INICIAL[0]])]
    if len(ini["events"]) != antes:
        hecho.append("ya no empieza con %s" % INICIAL[0])

    # ---------------- armas.js
    ev = J["events"]
    for m in ("-MOD", "-TICK", "-ANIM"):
        quitar(ev, lambda e, m=m: es_js(e, MK + m) or any(es_js(x, MK + m) for x in e.get("events", [])))
    quitar(ev, lambda e: e.get("type", "").endswith("Comment") and e.get("comment", "").startswith(MK + "-ANIM"))
    k = next((i for i, e in enumerate(ev) if es_js(e, "FDIZ-FASE56-MOD")), 0)
    ev[k:k] = [js(open(os.path.join(AQUI, "armas.js"), encoding="utf-8").read(), MK + "-MOD"),
               js("if (gdjs.fdizArmas) gdjs.fdizArmas.tick(runtimeScene);", MK + "-TICK")]
    GC = grupo(ev, "Combate: pegar")["events"]
    GC += [comentario(MK + "-ANIM · Con pistola, el golpe de lado o hacia abajo usa la animación de pistola (si el personaje la tiene)."),
           std([c("VarGlobal", "NetRol", "!=", "2")], [], [js("if (gdjs.fdizArmas) gdjs.fdizArmas.anim(runtimeScene);", MK + "-ANIM")])]
    hecho.append("armas.js")

    tmp = PRY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=2))
    os.replace(tmp, PRY)
    print("Fase 62 aplicada:", hecho)


if __name__ == "__main__":
    main()
