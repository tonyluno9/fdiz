"""Fase 67 · La pistola pequeña inicial está en el piso del salón de inicio y se recoge. Idempotente. Todos los modos.

Uso (desde la carpeta fdiz, con GDevelop CERRADO), después de fase66:
    python gdevelop/scripts/fase62_armas_uso.py         # quita el evento viejo que la equipaba e incrusta armas.js
    python gdevelop/scripts/fase67_pistola_inicial.py
    node gdevelop/scripts/prueba_armas.js

Usa el sistema de armas que ya existe (objeto ArmaPiso con variable Tipo, grupo "Armas del salón"):
  * Nadie empieza con la pistola: fase62_armas_uso.py ya no la da en "Inicio de supervivientes".
  * armas.js (host / sin red) pone UNA ArmaPiso Tipo "pistolita" en el salón donde está el jugador 1 cuando ya se
    colocó el equipo: B-01 (6000, 3100) en la intro de Escape y en Historia; E-04 (5200, 2570) en la aparición normal
    (Jefe, en línea, Escape con la intro ya vista). La variable de la escena PistolaPuesta evita ponerla otra vez.
  * Se recoge como las demás: pasando encima con los puños. El evento de siempre la equipa (Arma = pistolita, 9 balas,
    valores de arma de fuego) y borra la del piso, así que no se puede obtener dos veces.
  * Solo el jugador 1 la recoge (la pistola inicial era solo suya): variable de objeto ArmaPiso.Solo (0 = cualquiera,
    1 = solo el jugador 1). Condición agregada al evento de recoger: Solo = 0 o Solo = Sup.Jugador.
  * Escape: al terminar o saltar la intro el jugador 1 ya NO recibe la regla (antes la recibía si estaba a puños; con la
    regla en la mano no podría recoger la pistola, porque las armas se recogen solo con los puños). El consejo de la
    intro dice "¡Agarra la pistola!" en vez de "¡Agarra la regla!". La silla y la escoba siguen apareciendo en el salón.
  * Sprite de piso: generado/sprites/objetos/armas/pistolita_piso.png = pistolita.png x3 (pixel art, vecino más
    cercano), del tamaño de las demás armas del piso. Animación "pistolita" de ArmaPiso, origen abajo al centro.
No hay partidas guardadas en el juego (solo se guarda el volumen), así que no hay estado guardado que respetar.
"""
import datetime, json, os, shutil

from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
PRY = os.path.join(RAIZ, "gdevelop", "FDI-Z", "FDI-Z.json")
GEN = os.path.join(RAIZ, "generado", "sprites", "objetos", "armas")
REL = "../../generado/sprites/"
MK = "FDIZ-FASE67"
TIPO = "pistolita"
SPRITE = "objetos/armas/pistolita_piso.png"
ESCALA = 3


def c(tipo, *p, inv=False):
    return {"type": {"inverted": inv, "value": tipo}, "parameters": list(p)}


def recorrer(lst):
    for e in lst:
        yield e
        yield from recorrer(e.get("events", []))


def es(e, tipo, params):
    return any(x["type"]["value"] == tipo and x["parameters"][:len(params)] == params for x in e.get("conditions", []) + e.get("actions", []))


def main():
    d = json.load(open(PRY, encoding="utf-8"))
    resp = os.path.join(RAIZ, "gdevelop", "respaldos")
    os.makedirs(resp, exist_ok=True)
    bak = os.path.join(resp, "antes_de_fase67_%s.json" % datetime.date.today().strftime("%Y%m%d"))
    if not os.path.exists(bak):
        shutil.copy(PRY, bak)
    J = next(l for l in d["layouts"] if l["name"] == "Juego")
    ob = {o["name"]: o for o in J["objects"]}
    hecho = []

    # ---- el evento viejo no debe existir (lo quita fase62_armas_uso.py)
    ini = next(e for e in recorrer(J["events"]) if e.get("type", "").endswith("Group") and e.get("name") == "Inicio de supervivientes")
    if any(es(e, "ModVarObjetTxt", ["Sup", "Arma", "=", '"%s"' % TIPO]) for e in recorrer(ini["events"])):
        raise SystemExit("El jugador 1 todavía empieza con la pistola: corre antes fase62_armas_uso.py")
    if not any(e.get("inlineCode", "").startswith("/*FDIZ-FASE62-MOD") and "A.ponerPistola" in e["inlineCode"] for e in J["events"]):
        raise SystemExit("armas.js del proyecto es viejo: corre antes fase62_armas_uso.py")

    # ---- sprite de piso y animación
    org = Image.open(os.path.join(GEN, "pistolita.png")).convert("RGBA")
    img = org.resize((org.width * ESCALA, org.height * ESCALA), Image.NEAREST)
    dest = os.path.join(GEN, "pistolita_piso.png")
    if not os.path.exists(dest) or Image.open(dest).convert("RGBA").tobytes() != img.tobytes():
        img.save(dest); hecho.append("sprite")
    if not any(r["name"] == SPRITE for r in d["resources"]["resources"]):
        d["resources"]["resources"].append({"file": REL + SPRITE, "kind": "image", "metadata": "", "name": SPRITE, "smoothed": False, "userAdded": True})
    ap = ob["ArmaPiso"]
    an = {"name": TIPO, "useMultipleDirections": False, "directions": [{"looping": False, "timeBetweenFrames": 0.08, "sprites": [
        {"hasCustomCollisionMask": False, "image": SPRITE, "points": [], "originPoint": {"name": "origine", "x": img.width // 2, "y": img.height},
         "centerPoint": {"automatic": True, "name": "centre", "x": 0, "y": 0}, "customCollisionMask": []}]}]}
    k = next((i for i, x in enumerate(ap["animations"]) if x["name"] == TIPO), None)
    if k is None:
        ap["animations"].append(an); hecho.append("ArmaPiso/" + TIPO)
    else:
        ap["animations"][k] = an

    # ---- variables
    if not any(v["name"] == "Solo" for v in ap["variables"]):
        ap["variables"].append({"name": "Solo", "type": "number", "value": 0}); hecho.append("ArmaPiso.Solo")
    if not any(v["name"] == "PistolaPuesta" for v in J["variables"]):
        J["variables"].append({"name": "PistolaPuesta", "type": "number", "value": 0}); hecho.append("PistolaPuesta")

    # ---- recoger: Solo = 0 o Solo = jugador
    GA = next(e for e in J["events"] if e.get("type", "").endswith("Group") and e.get("name") == "Armas del salón")
    rec = next(e for e in recorrer(GA["events"]) if e.get("type", "").endswith("ForEach") and e.get("object") == "Sup"
               and es(e, "CollisionNP", ["Sup", "ArmaPiso"]) and any(es(s, "ModVarObjetTxt", ["Sup", "Arma", "=", "ArmaPiso.VariableString(Tipo)"]) for s in recorrer(e.get("events", []))))
    o = {"type": {"value": "BuiltinCommonInstructions::Or"}, "parameters": [],
         "subInstructions": [c("VarObjet", "ArmaPiso", "Solo", "=", "0"), c("VarObjet", "ArmaPiso", "Solo", "=", "Sup.Variable(Jugador)")]}
    rec["conditions"] = [x for x in rec["conditions"] if not (x["type"]["value"].endswith("Or") and "Solo" in json.dumps(x))]
    k = next(i for i, x in enumerate(rec["conditions"]) if x["type"]["value"] == "CollisionNP") + 1
    rec["conditions"].insert(k, o)

    # ---- Escape: al terminar o saltar la intro, el jugador 1 ya no recibe la regla (así puede recoger la pistola)
    cin = next(e for e in J["events"] if e.get("type", "").endswith("Group") and e.get("name", "").startswith("Cinemática de inicio"))
    for e in recorrer(cin["events"]):
        antes = len(e.get("events", []))
        e["events"] = [s for s in e.get("events", []) if not (es(s, "VarObjet", ["Sup", "Jugador", "=", "1"])
                                                             and es(s, "ModVarObjetTxt", ["Sup", "Arma", "=", '"regla"']))]
        if len(e["events"]) != antes:
            hecho.append("sin regla al terminar la intro")
        for x in e.get("actions", []):
            if x["type"]["value"] == "TextObject::String" and x["parameters"][0] == "TxtDialogo" and "Agarra la regla" in x["parameters"][2]:
                x["parameters"][2] = x["parameters"][2].replace("Agarra la regla", "Agarra la pistola"); hecho.append("texto de la intro")

    tmp = PRY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=2))
    os.replace(tmp, PRY)
    print("Fase 67 aplicada:", hecho or "sin cambios (ya aplicada)")


if __name__ == "__main__":
    main()
