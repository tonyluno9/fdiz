"""Fase 59 · Revólver (tipo sheriff) y escopeta como armas del piso. Idempotente.

Uso (desde la carpeta fdiz, con GDevelop CERRADO):
    python gdevelop/scripts/fase59_arte_armas.py      # (una vez) arte y sonidos
    python gdevelop/scripts/fase59_armas_fuego.py
    node gdevelop/scripts/prueba_armas_fuego.js
Va al final de la cadena (después de fase58).

Usa el sistema de armas que ya existe (grupo "Armas del salón" y "Combate: pegar"):
  * Se recogen igual que las demás: pasando encima con los puños (ArmaPiso con variable Tipo).
  * Sup.Arma = "pistola" (revólver) o "escopeta"; Usos = munición (se gasta 1 por disparo con la regla de siempre y al
    llegar a 0 vuelve a "puños"); DanioArma, Alcance y Cadencia como las demás armas; el daño se multiplica por Fuerza.
  * En vez del golpe cuerpo a cuerpo disparan con el objeto Proyectil de los lanzables (el mismo de la engrapadora):
    daña al primer zombi a 46 px, se detiene en muros y puertas (Solidos), da la baja a quien disparó (UltJugador).
    Alcance = duración del proyectil x 4 (s): revólver 2.4 -> 0.6 s a 1000 px/s = ~600 px; escopeta 1.2 -> 0.3 s a
    900 px/s = ~270 px con 5 perdigones en abanico.
  * Íconos del HUD: "escopeta" ya existía; "pistola" ahora muestra el revólver (ico128_arma_revolver.png).

| Arma | Usos (munición) | DanioArma | Alcance | Cadencia |
|---|---|---|---|---|
| pistola (revólver) | 6 | 24 por bala | 2.4 (~600 px) | 0.55 s |
| escopeta | 6 | 9 por perdigón x 5 | 1.2 (~270 px) | 0.95 s |
(para comparar: bate 21 / 1.25 / 0.5 s, 24 usos; minigun de Miranda 6 / 0.1 s)
"""
import copy, datetime, json, os, shutil, sys, uuid

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
PRY = os.path.join(RAIZ, "gdevelop", "FDI-Z", "FDI-Z.json")
REL = "../../generado/sprites/"
MK = "FDIZ-FASE59"

ARMAS = {   # Tipo: (Usos, DanioArma, Alcance, Cadencia)
    "pistola": (6, 24, 2.4, 0.55),
    "escopeta": (6, 9, 1.2, 0.95),
}
DISPARO = {  # Tipo: (proyectil, velocidad px/s, ángulos de los proyectiles, sonido, empuje)
    "pistola": ("bala", 1000, [0], "efectos/combate/revolver.wav", -120),
    "escopeta": ("perdigon", 900, [-12, -6, 0, 6, 12], "efectos/combate/escopeta.wav", -90),
}
# Dónde están (pies del arma: origen abajo al centro, como las demás ArmaPiso). None = falta ubicarla.
POS = {
    "escopeta": (5136, 650),     # conserjería, a la derecha de las llaves (5056, 640) y antes del bote de basura
    "pistola": None,             # sala de la imagen de referencia: pendiente
}


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


def es(e, tipo, params):
    return any(x["type"]["value"] == tipo and x["parameters"][:len(params)] == params for x in e.get("conditions", []) + e.get("actions", []))


def marcado(lst, clave):
    return any(x.get("type", "").endswith("Comment") and x.get("comment", "").startswith(MK + "-" + clave) for x in lst)


def asegura_var(lista, nombre, valor):
    if not any(v["name"] == nombre for v in lista):
        lista.append({"name": nombre, "type": "string" if isinstance(valor, str) else "number", "value": valor})


def recurso(d, nombre, archivo):
    if not any(r["name"] == nombre for r in d["resources"]["resources"]):
        d["resources"]["resources"].append({"file": archivo, "kind": "image", "metadata": "", "name": nombre, "smoothed": False, "userAdded": True})


def anim_simple(nombre, imagen, ox, oy):
    return {"name": nombre, "useMultipleDirections": False, "directions": [{"looping": False, "timeBetweenFrames": 0.08, "sprites": [
        {"hasCustomCollisionMask": False, "image": imagen, "points": [], "originPoint": {"name": "origine", "x": ox, "y": oy},
         "centerPoint": {"automatic": True, "name": "centre", "x": 0, "y": 0}, "customCollisionMask": []}]}]}


def main():
    from PIL import Image
    d = json.load(open(PRY, encoding="utf-8"))
    resp = os.path.join(RAIZ, "gdevelop", "respaldos")
    os.makedirs(resp, exist_ok=True)
    bak = os.path.join(resp, "antes_de_fase59_%s.json" % datetime.date.today().strftime("%Y%m%d"))
    if not os.path.exists(bak):
        shutil.copy(PRY, bak)
    J = next(l for l in d["layouts"] if l["name"] == "Juego")
    ob = {o["name"]: o for o in J["objects"]}
    hecho = []

    # ---------------- recursos y animaciones
    for tipo, archivo in (("pistola", "objetos/armas/pistola.png"), ("escopeta", "objetos/armas/escopeta.png")):
        ruta = os.path.join(RAIZ, "generado", "sprites", *archivo.split("/"))
        if not os.path.exists(ruta):
            sys.exit("Falta %s: corre fase59_arte_armas.py" % ruta)
        w, h = Image.open(ruta).size
        recurso(d, archivo, REL + archivo)
        if not any(x["name"] == tipo for x in ob["ArmaPiso"]["animations"]):
            ob["ArmaPiso"]["animations"].append(anim_simple(tipo, archivo, w // 2, h)); hecho.append("ArmaPiso/" + tipo)
    for tipo, archivo in (("bala", "objetos/lanzables/bala.png"), ("perdigon", "objetos/lanzables/perdigon.png")):
        w, h = Image.open(os.path.join(RAIZ, "generado", "sprites", *archivo.split("/"))).size
        recurso(d, archivo, REL + archivo)
        if not any(x["name"] == tipo for x in ob["Proyectil"]["animations"]):
            ob["Proyectil"]["animations"].append(anim_simple(tipo, archivo, w // 2, h // 2)); hecho.append("Proyectil/" + tipo)
    recurso(d, "p48_ico_revolver", "assets/interfaz/hud/ico128_arma_revolver.png")
    for x in ob["HudIcono"]["animations"]:
        if x["name"] == "pistola":
            x["directions"][0]["sprites"][0]["image"] = "p48_ico_revolver"
    for nombre in ("efectos/combate/revolver.wav", "efectos/combate/escopeta.wav"):
        if not any(r["name"] == nombre for r in d["resources"]["resources"]):
            d["resources"]["resources"].append({"file": nombre, "kind": "audio", "metadata": "", "name": nombre, "userAdded": True})
    asegura_var(ob["Sup"]["variables"], "ArmaFuego", 0)
    asegura_var(ob["Proyectil"]["variables"], "Dura", 0.9)

    ev = J["events"]
    # ---------------- recoger y valores (Armas del salón)
    GA = next(e for e in ev if e.get("type", "").endswith("Group") and e.get("name") == "Armas del salón")
    raiz = GA["events"][0]["events"]                                   # dentro de "NetRol != 2 y Pausa = 0"
    recoge = next(e for e in recorrer(raiz) if es(e, "ModVarObjetTxt", ["Sup", "Arma", "=", "ArmaPiso.VariableString(Tipo)"]))
    for tipo, (usos, _, _, _) in ARMAS.items():
        if not any(es(s, "VarObjetTxt", ["Sup", "Arma", "=", '"%s"' % tipo]) for s in recoge["events"]):
            k = len(recoge["events"]) - 1                                   # antes del Delete ArmaPiso
            recoge["events"].insert(k, std([c("VarObjetTxt", "Sup", "Arma", "=", '"%s"' % tipo)], [a("ModVarObjet", "Sup", "Usos", "=", str(usos))]))
    if not marcado(raiz, "VALORES"):
        k = next(i for i, e in enumerate(raiz) if es(e, "VarObjetTxt", ["Sup", "Arma", "=", '"puños"']) and es(e, "ModVarObjet", ["Sup", "DanioArma"]))
        nuevos = [comentario(MK + "-VALORES · Armas de fuego: Usos = munición, DanioArma por proyectil, Alcance -> distancia del disparo, Cadencia entre disparos."),
                  std([], [a("ModVarObjet", "Sup", "ArmaFuego", "=", "0")])]
        raiz[k:k] = nuevos
        for tipo, (_, danio, alcance, cad) in ARMAS.items():
            raiz.append(std([c("VarObjetTxt", "Sup", "Arma", "=", '"%s"' % tipo)],
                            [a("ModVarObjet", "Sup", "DanioArma", "=", str(danio)), a("ModVarObjet", "Sup", "Alcance", "=", str(alcance)),
                             a("ModVarObjet", "Sup", "Cadencia", "=", str(cad)), a("ModVarObjet", "Sup", "ArmaFuego", "=", "1")]))
        hecho.append("valores")

    # ---------------- disparar (Combate: pegar)
    GC = next(e for e in ev if e.get("type", "").endswith("Group") and e.get("name") == "Combate: pegar")
    ataque = next(e for e in recorrer(GC["events"]) if e.get("type", "").endswith("ForEach") and e.get("object") == "Sup"
                  and es(e, "VarObjet", ["Sup", "QuierePegar", "=", "1"]))
    sub = ataque["events"]
    melee = next(e for e in sub if e.get("type", "").endswith("ForEach") and e.get("object") == "Zombies")
    if not es(melee, "VarObjet", ["Sup", "ArmaFuego"]):
        melee["conditions"].append(c("VarObjet", "Sup", "ArmaFuego", "=", "0")); hecho.append("sin golpe cuerpo a cuerpo con armas de fuego")
    if not marcado(sub, "DISPARO"):
        k = next(i for i, e in enumerate(sub) if es(e, "ModVarObjet", ["Golpe", "Danio"])) + 1
        disparos = []
        for tipo, (proy, vel, angs, sonido, _) in DISPARO.items():
            acts = []
            for ang in angs:
                angulo = "ToDeg(atan2(Sup.Variable(AimY), Sup.Variable(AimX)))" + (" + %d" % ang if ang else "")
                acts += [a("Create", "", "Proyectil", "Sup.X() + cos(atan2(Sup.Variable(AimY), Sup.Variable(AimX))) * 34",
                           "Sup.Y() - 46 + sin(atan2(Sup.Variable(AimY), Sup.Variable(AimX))) * 34", '"Juego"'),
                         a("ModVarObjetTxt", "Proyectil", "Tipo", "=", '"%s"' % proy),
                         a("SetAnimationName", "Proyectil", '"%s"' % proy),
                         a("ModVarObjet", "Proyectil", "Danio", "=", "Sup.Variable(DanioArma) * Sup.Variable(Fuerza)"),
                         a("ModVarObjet", "Proyectil", "Jugador", "=", "Sup.Variable(Jugador)"),
                         a("ModVarObjet", "Proyectil", "Dura", "=", "Sup.Variable(Alcance) / 4"),
                         a("SetAngle", "Proyectil", "=", angulo),
                         a("AddForceAL", "Proyectil", angulo, str(vel), "1"),
                         a("ResetObjectTimer", "Proyectil", '"vida"')]
            disparos.append(std([c("VarObjetTxt", "Sup", "Arma", "=", '"%s"' % tipo)], acts,
                                [std([c("VarGlobal", "SonidoActivo", "=", "1")], [a("PlaySound", "", sonido, "", "70", "1")])]))
        sub[k:k] = [comentario(MK + "-DISPARO · Revólver y escopeta: en vez del golpe, proyectiles (objeto Proyectil de los lanzables)."),
                    std([c("VarObjet", "Sup", "ArmaFuego", "=", "1")], [a("Delete", "Golpe", ""), a("Delete", "GolpeFx", "")], disparos)]
        hecho.append("disparo")

    # ---------------- proyectiles (Lanzables): duración, empuje y que no queden en el piso
    GL = next(e for e in ev if e.get("type", "").endswith("Group") and e.get("name") == "Lanzables")
    for e in recorrer(GL["events"]):
        for x in e.get("conditions", []):
            if x["type"]["value"] == "CompareObjectTimer" and x["parameters"][:2] == ["Proyectil", '"vida"'] and x["parameters"][3] == "0.9":
                x["parameters"][3] = "Proyectil.Variable(Dura)"; hecho.append("duración por proyectil")
        if es(e, "Create", ["", "LanzPiso"]) and not es(e, "VarObjetTxt", ["Proyectil", "Tipo", "=", '"bala"']):
            e["conditions"] += [c("VarObjetTxt", "Proyectil", "Tipo", "=", '"bala"', inv=True),
                                c("VarObjetTxt", "Proyectil", "Tipo", "=", '"perdigon"', inv=True)]
            hecho.append("balas no quedan en el piso")
    golpe = next(e for e in recorrer(GL["events"]) if es(e, "ModVarObjet", ["Proyectil", "Pego", "=", "1"]) and es(e, "ModVarObjet", ["Zombies", "Vida", "-"]))
    for tipo, (proy, _, _, _, empuje) in DISPARO.items():
        if not any(es(s, "VarObjetTxt", ["Proyectil", "Tipo", "=", '"%s"' % proy]) for s in golpe["events"]):
            golpe["events"].append(std([c("VarObjetTxt", "Proyectil", "Tipo", "=", '"%s"' % proy)],
                                       [a("AddForceVersPos", "Zombies", "Proyectil.X()", "Proyectil.Y() + 40", str(empuje), "0")]))

    # ---------------- en el mapa
    for tipo, pos in POS.items():
        uid = str(uuid.uuid5(uuid.NAMESPACE_URL, "fdiz-armapiso-" + tipo))
        J["instances"] = [i for i in J["instances"] if i.get("persistentUuid") != uid]
        if pos:
            idx = next(i for i, x in enumerate(ob["ArmaPiso"]["animations"]) if x["name"] == tipo)   # como las demás del mapa
            J["instances"].append({"angle": 0, "customSize": False, "height": 0, "layer": "Juego", "name": "ArmaPiso",
                                   "persistentUuid": uid, "width": 0, "x": pos[0], "y": pos[1], "zOrder": pos[1],
                                   "numberProperties": [{"name": "animation", "value": idx}], "stringProperties": [],
                                   "initialVariables": [{"name": "Tipo", "type": "string", "value": tipo}]})
            hecho.append("%s en %s" % (tipo, pos))

    tmp = PRY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=2))
    os.replace(tmp, PRY)
    print("Fase 59 aplicada:", hecho or "sin cambios (ya aplicada)")


if __name__ == "__main__":
    main()
