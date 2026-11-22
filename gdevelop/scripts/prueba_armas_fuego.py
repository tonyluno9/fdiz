"""Pruebas de la fase 59 (revólver y escopeta) sin GDevelop:  python gdevelop/scripts/prueba_armas_fuego.py"""
import json, math, os, sys
from collections import deque
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
PROY = os.path.join(RAIZ, "gdevelop", "FDI-Z")
d = json.load(open(os.path.join(PROY, "FDI-Z.json"), encoding="utf-8"))
J = next(l for l in d["layouts"] if l["name"] == "Juego")
ob = {o["name"]: o for o in J["objects"]}
res = {r["name"]: r for r in d["resources"]["resources"]}
sys.path.insert(0, AQUI)
from fase59_armas_fuego import ARMAS, DISPARO, POS

ok = mal = 0


def prueba(nombre, f):
    global ok, mal
    try:
        f(); ok += 1; print("  OK  ", nombre)
    except AssertionError as e:
        mal += 1; print("  MAL ", nombre, "->", e)


def recorrer(lst):
    for e in lst:
        yield e
        yield from recorrer(e.get("events", []))


def es(e, tipo, params):
    return any(x["type"]["value"] == tipo and x["parameters"][:len(params)] == params for x in e.get("conditions", []) + e.get("actions", []))


def grupo(n):
    return next(e for e in J["events"] if e.get("type", "").endswith("Group") and e.get("name") == n)["events"]


def archivo(nombre_res):
    f = res[nombre_res]["file"]
    return os.path.normpath(os.path.join(PROY, f))


def rect_sprite(obj, anim, x, y):
    s = next(a for a in ob[obj]["animations"] if a["name"] == anim)["directions"][0]["sprites"][0]
    w, h = Image.open(archivo(s["image"])).size
    return (x - s["originPoint"]["x"], y - s["originPoint"]["y"], x - s["originPoint"]["x"] + w, y - s["originPoint"]["y"] + h)


def cruza(r, q, m=0):
    return r[0] < q[2] + m and r[2] > q[0] - m and r[1] < q[3] + m and r[3] > q[1] - m


solidos = [(i["x"], i["y"], i["x"] + i["width"], i["y"] + i["height"]) for i in J["instances"] if i["name"] in ("Muro", "ChoqueMueble", "Puerta")]
mueble = ob["Mueble"]
muebles = []
for i in J["instances"]:
    if i["name"] == "Mueble":
        k = next((p["value"] for p in i.get("numberProperties", []) if p["name"] == "animation"), 0)
        an = mueble["animations"][k]["name"]
        muebles.append((an, rect_sprite("Mueble", an, i["x"], i["y"])))


def instancias(tipo):
    return [i for i in J["instances"] if i["name"] == "ArmaPiso" and any(v["name"] == "Tipo" and v["value"] == tipo for v in i.get("initialVariables", []))]


# ---------------- arte, íconos y sonido
def t_recursos():
    for tipo in ARMAS:
        an = next((a for a in ob["ArmaPiso"]["animations"] if a["name"] == tipo), None)
        assert an, "ArmaPiso sin animación " + tipo
        assert os.path.exists(archivo(an["directions"][0]["sprites"][0]["image"])), "falta el sprite de " + tipo
        hud = next(a for a in ob["HudIcono"]["animations"] if a["name"] == tipo)
        assert os.path.exists(archivo(hud["directions"][0]["sprites"][0]["image"])), "falta el ícono " + tipo
    assert next(a for a in ob["HudIcono"]["animations"] if a["name"] == "pistola")["directions"][0]["sprites"][0]["image"] == "p48_ico_revolver"
    for proy, _, _, sonido, _ in DISPARO.values():
        assert any(a["name"] == proy for a in ob["Proyectil"]["animations"]), "Proyectil sin " + proy
        assert sonido in res and os.path.exists(os.path.join(PROY, *res[sonido]["file"].split("/"))), "falta " + sonido
prueba("Sprites de piso, íconos del HUD (pistola = revólver), proyectiles y sonidos existen", t_recursos)

# ---------------- la escopeta junto a las llaves
LLAVES = (5056, 640)
CONSERJERIA = (4896, 544, 5216, 768)
def t_escopeta_lugar():
    ins = instancias("escopeta")
    assert len(ins) == 1, "escopetas en el mapa: %d" % len(ins)
    i = ins[0]
    idx = next(p["value"] for p in i["numberProperties"] if p["name"] == "animation")
    assert ob["ArmaPiso"]["animations"][idx]["name"] == "escopeta", "la instancia mostraría otra animación"
    r = rect_sprite("ArmaPiso", "escopeta", i["x"], i["y"])
    assert CONSERJERIA[0] <= r[0] and r[2] <= CONSERJERIA[2] and CONSERJERIA[1] <= r[1] and r[3] <= CONSERJERIA[3], "fuera de la conserjería: %s" % (r,)
    choca = [s for s in solidos if cruza(r, s)]
    assert not choca, "dentro de muro / mueble / puerta: %s" % choca
    sobre = [m for m in muebles if cruza(r, m[1])]
    assert not sobre, "encima del dibujo de un mueble: %s" % sobre
    llave = rect_sprite("Objetivo", "llaves", *LLAVES)
    assert not cruza(r, llave, 24), "tapa o pega con las llaves: %s %s" % (r, llave)
    dist = math.hypot(i["x"] - LLAVES[0], i["y"] - LLAVES[1])
    assert 50 <= dist <= 140, "distancia a las llaves %.0f px" % dist
prueba("Escopeta en la conserjería, junto a las llaves sin taparlas, fuera de muros, muebles y puertas", t_escopeta_lugar)


def t_alcanzable():
    """Pies del jugador (40 x 16) con la regla de choque real. Las puertas se abren con F o se derriban (la de la
    conserjería es restringida: a golpes o con Carlos), así que no cuentan como pared."""
    G, MX, MY = 8, 20, 16
    W, H = 8768 // G + 2, 5376 // G + 2
    bl = bytearray(W * H)
    for (a, b, c, e) in [(i["x"], i["y"], i["x"] + i["width"], i["y"] + i["height"]) for i in J["instances"] if i["name"] in ("Muro", "ChoqueMueble")]:
        for cy in range(max(0, int(b // G) - 1), min(H, int((e + MY) // G) + 2)):
            py = (cy + .5) * G
            if not (b < py < e + MY): continue
            for cx in range(max(0, int((a - MX) // G)), min(W, int((c + MX) // G) + 2)):
                if a - MX < (cx + .5) * G < c + MX: bl[cy * W + cx] = 1
    st = min((j for j in range(W * H) if not bl[j] and abs((j % W) * G - 5150) < 200 and abs((j // W) * G - 2528) < 200),
             key=lambda j: ((j % W + .5) * G - 5150) ** 2 + ((j // W + .5) * G - 2528) ** 2)
    seen = bytearray(W * H); seen[st] = 1; q = deque([st])
    while q:
        i = q.popleft()
        for j in (i - 1, i + 1, i - W, i + W):
            if 0 <= j < W * H and not seen[j] and not bl[j]: seen[j] = 1; q.append(j)
    i = instancias("escopeta")[0]; r = rect_sprite("ArmaPiso", "escopeta", i["x"], i["y"])
    # se recoge al tocar el arma con la caja de los pies: algún lugar alcanzable cuya caja la toque
    toca = any(seen[cy * W + cx] for cy in range(int(r[1] // G), int((r[3] + MY) // G) + 1)
               for cx in range(int((r[0] - MX) // G), int((r[2] + MX) // G) + 1)
               if 0 <= cx < W and 0 <= cy < H and cruza(((cx + .5) * G - MX, (cy + .5) * G - MY, (cx + .5) * G + MX, (cy + .5) * G), r))
    assert toca, "ningún lugar alcanzable toca la escopeta"
prueba("Un jugador puede llegar a tocarla (se recoge pasando encima, como las demás)", t_alcanzable)

# ---------------- reglas del sistema de armas
def t_recoger_y_valores():
    raiz = grupo("Armas del salón")
    recoge = next(e for e in recorrer(raiz) if es(e, "ModVarObjetTxt", ["Sup", "Arma", "=", "ArmaPiso.VariableString(Tipo)"]))
    padre = next(e for e in recorrer(raiz) if recoge in e.get("events", []))
    assert es(padre, "VarObjetTxt", ["Sup", "Arma", "=", '"puños"']) and es(padre, "CollisionNP", ["Sup", "ArmaPiso"]), "ya no se recoge con los puños al tocarla"
    for tipo, (usos, danio, alcance, cad) in ARMAS.items():
        assert any(es(s, "VarObjetTxt", ["Sup", "Arma", "=", '"%s"' % tipo]) and es(s, "ModVarObjet", ["Sup", "Usos", "=", str(usos)]) for s in recoge["events"]), "munición " + tipo
        v = next(e for e in recorrer(raiz) if es(e, "VarObjetTxt", ["Sup", "Arma", "=", '"%s"' % tipo]) and es(e, "ModVarObjet", ["Sup", "DanioArma"]))
        vals = {x["parameters"][1]: x["parameters"][3] for x in v["actions"]}
        assert vals == {"DanioArma": str(danio), "Alcance": str(alcance), "Cadencia": str(cad), "ArmaFuego": "1"}, vals
prueba("Se recogen con el sistema de siempre y ponen Usos, DanioArma, Alcance y Cadencia", t_recoger_y_valores)


def t_disparo():
    ataque = next(e for e in recorrer(grupo("Combate: pegar")) if e.get("type", "").endswith("ForEach") and e.get("object") == "Sup" and es(e, "VarObjet", ["Sup", "QuierePegar", "=", "1"]))
    assert es(ataque, "CompareObjectTimer", ["Sup", '"golpe"', ">=", "Sup.Variable(Cadencia)"]), "la cadencia ya no manda"
    fuego = next(e for e in ataque["events"] if es(e, "VarObjet", ["Sup", "ArmaFuego", "=", "1"]))
    melee = next(e for e in ataque["events"] if e.get("type", "").endswith("ForEach") and e.get("object") == "Zombies")
    assert es(melee, "VarObjet", ["Sup", "ArmaFuego", "=", "0"]), "con arma de fuego también pegaría cuerpo a cuerpo"
    assert ataque["events"].index(fuego) < ataque["events"].index(melee)
    for tipo, (proy, vel, angs, sonido, _) in DISPARO.items():
        ev = next(s for s in fuego["events"] if es(s, "VarObjetTxt", ["Sup", "Arma", "=", '"%s"' % tipo]))
        crea = [x for x in ev["actions"] if x["type"]["value"] == "Create" and x["parameters"][1] == "Proyectil"]
        assert len(crea) == len(angs), "%s crea %d proyectiles" % (tipo, len(crea))
        dan = [x["parameters"][3] for x in ev["actions"] if x["parameters"][:2] == ["Proyectil", "Danio"]]
        assert all(v == "Sup.Variable(DanioArma) * Sup.Variable(Fuerza)" for v in dan), dan
        assert any(es(s, "PlaySound", ["", sonido]) for s in ev["events"]), "sin sonido"
        alc = ARMAS[tipo][2]
        print("        %s: %d proyectil(es) de %s, %d px/s, alcance %.0f px, %s de daño" %
              (tipo, len(angs), ARMAS[tipo][1], vel, vel * alc / 4, "%d x %d" % (len(angs), ARMAS[tipo][1])))
    usos = [e for e in ataque["events"] if es(e, "ModVarObjet", ["Sup", "Usos", "-", "1"])]
    assert usos, "ya no se gasta munición"
prueba("Disparan proyectiles (1 bala / 5 perdigones) con el daño del arma x Fuerza y gastan 1 de munición por disparo", t_disparo)


def t_proyectiles():
    L = grupo("Lanzables")
    vida = [x for e in recorrer(L) for x in e.get("conditions", []) if x["type"]["value"] == "CompareObjectTimer" and x["parameters"][:2] == ["Proyectil", '"vida"']]
    assert vida and vida[0]["parameters"][3] == "Proyectil.Variable(Dura)", "duración fija"
    dura = next(v["value"] for v in ob["Proyectil"]["variables"] if v["name"] == "Dura")
    assert dura == 0.9, "los lanzables cambiarían su duración"
    choque = next(e for e in recorrer(L) if es(e, "CollisionNP", ["Proyectil", "Solidos"]))
    assert es(choque, "ModVarObjet", ["Proyectil", "Pego", "=", "1"]), "las balas atravesarían muros"
    suelo = next(e for e in recorrer(L) if es(e, "Create", ["", "LanzPiso"]))
    negados = {x["parameters"][3] for x in suelo["conditions"] if x["type"].get("inverted")}
    assert {'"bala"', '"perdigon"', '"engrapadora"'} <= negados, "las balas quedarían tiradas como lanzables"
prueba("Proyectiles: se detienen en muros y puertas, duran según el Alcance y no quedan en el piso", t_proyectiles)


def t_revolver():
    if POS["pistola"] is None:
        print("        (revólver: falta la imagen de referencia para ubicarlo; no está en el mapa)")
        assert not instancias("pistola")
    else:
        i = instancias("pistola"); assert len(i) == 1
        r = rect_sprite("ArmaPiso", "pistola", i[0]["x"], i[0]["y"])
        assert not [s for s in solidos if cruza(r, s)] and not [m for m in muebles if cruza(r, m[1])], "revólver encimado"
prueba("Revólver: colocado (o pendiente de la imagen) sin encimarse", t_revolver)

print("%d correctas, %d fallidas" % (ok, mal))
sys.exit(1 if mal else 0)
