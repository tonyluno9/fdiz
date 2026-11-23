"""FDI-Z · Fase 72 · Historia con cambio de personaje, AK-47 y Escape sin selector de personajes.
Correr con GDevelop cerrado, después de la 68, la 69 y la 71:
    python gdevelop/scripts/fase72_cambio_personaje.py

Fuente: gdevelop/historia/02_HISTORIA_PARA_GDEVELOP.md (versión final), secciones 3.4 y 3.5.
* historia.js (lógica, se incrusta en FDIZ-FASE68-MOD):
  - El jugador controla un alumno a la vez y los otros tres son bots: Alan (pasos 1-4) -> Tony (desde C03) ->
    César (desde C065) -> Miranda (desde C07) -> Alan (desde C08). Aviso «Ahora controlas a X». Historia.Controlado.
  - Armas: pistola pequeña -> Tony (C03); escopeta -> César (C065) y en C07 se la pasa a Miranda; pistola del director
    -> César y AK-47 -> Alan (C08). En los checkpoints cada arma vuelve a su dueño con el cargador lleno.
    Ya no hay pistola en el piso en Historia ni sheriff que recoger.
* AK-47 (arma nueva, "ak47"): 30 balas, cadencia alta (0.12 s, automática: se mantiene el clic), 12 de daño, mata en
  2 impactos (Golpes 2, como la pistola pequeña). Icono del HUD y arma en el piso desde ak47pixelart.png.
  armas.js: cargador y animación de disparo de lado (Alan usa la de su GIF de AK-47).
* Menú: Escape (Local) ya no tiene selector de personajes: va directo a la dificultad con el equipo fijo
  (Tony en P1 y Miranda, Alan y César como bots). Escape en línea no cambia. Escape (tecla) en la dificultad vuelve a
  «Local / En línea».
Idempotente.
"""
import copy
import json
import os
import sys

from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import fase69_correcciones as F  # noqa: E402

RAIZ, PRY, GEN = F.RAIZ, F.PRY, F.GEN
c, a, recorrer, tiene, grupo = F.c, F.a, F.recorrer, F.tiene, F.grupo
AK_FUENTE = os.path.join(GEN, "objetos", "armas", "ak47_original.png")
AK_PISO = "objetos/armas/ak47.png"
AK_HUD = "assets/interfaz/hud/ico128_arma_ak47.png"
AK = {"Usos": "30", "DanioArma": "12", "Alcance": "2.2", "Cadencia": "0.12"}


def arte_ak():
    im = Image.open(AK_FUENTE).convert("RGBA")
    im = im.crop(im.getbbox())
    # en el piso: 46 px de ancho
    w = 46; h = max(1, round(im.height * w / im.width))
    im.resize((w, h), Image.NEAREST).save(os.path.join(GEN, *AK_PISO.split("/")))
    # HUD: 128 x 128, el arma ocupa 116 px de ancho, centrada
    w = 116; h = max(1, round(im.height * w / im.width))
    lienzo = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    lienzo.alpha_composite(im.resize((w, h), Image.NEAREST), ((128 - w) // 2, (128 - h) // 2))
    lienzo.save(os.path.join(RAIZ, "gdevelop", "FDI-Z", *AK_HUD.split("/")))
    return (46, round(im.height * 46 / im.width))


def anim_simple(nombre, imagen, origen):
    return {"name": nombre, "useMultipleDirections": False, "directions": [{"looping": False, "timeBetweenFrames": 0.08, "sprites": [
        {"hasCustomCollisionMask": False, "image": imagen, "points": [], "originPoint": {"name": "origine", "x": origen[0], "y": origen[1]},
         "centerPoint": {"automatic": True, "name": "centre", "x": 0, "y": 0}, "customCollisionMask": []}]}]}


def poner_anim(obj, nueva):
    k = next((i for i, x in enumerate(obj["animations"]) if x["name"] == nueva["name"]), None)
    if k is None:
        obj["animations"].append(nueva)
    else:
        obj["animations"][k] = nueva


def main():
    d = json.load(open(PRY, encoding="utf-8"))
    J = next(l for l in d["layouts"] if l["name"] == "Juego")
    M = next(l for l in d["layouts"] if l["name"] == "Menu")
    ob = {o["name"]: o for o in J["objects"]}
    ev = J["events"]
    res = d["resources"]["resources"]
    nombres = {r["name"] for r in res}

    # ---------------- AK-47: arte, recursos y animaciones
    w, h = arte_ak()
    for nombre, archivo in ((AK_PISO, "../../generado/sprites/" + AK_PISO), (AK_HUD, AK_HUD)):
        if nombre not in nombres:
            res.append({"file": archivo, "kind": "image", "metadata": "", "name": nombre, "smoothed": False, "userAdded": True})
    poner_anim(ob["ArmaPiso"], anim_simple("ak47", AK_PISO, (w // 2, h)))
    poner_anim(ob["HudIcono"], anim_simple("ak47", AK_HUD, (0, 0)))

    # ---------------- AK-47: munición, valores y disparo
    salon = grupo(ev, "Armas del salón")["events"]
    for e in list(recorrer(salon)):
        for hijos in [e.get("events", [])]:
            for sub in list(hijos):
                cond = sub.get("conditions", [])
                if len(cond) == 1 and cond[0]["type"]["value"] == "VarObjetTxt" and cond[0]["parameters"][:4] == ["Sup", "Arma", "=", '"escopeta"']:
                    ya = any(len(x.get("conditions", [])) == 1 and x["conditions"][0]["parameters"][:4] == ["Sup", "Arma", "=", '"ak47"'] for x in hijos)
                    if ya:
                        continue
                    nuevo = copy.deepcopy(sub)
                    nuevo["conditions"][0]["parameters"][3] = '"ak47"'
                    for x in nuevo["actions"]:
                        if x["type"]["value"] == "ModVarObjet" and x["parameters"][1] in AK:
                            x["parameters"][3] = AK[x["parameters"][1]]
                    hijos.insert(hijos.index(sub) + 1, nuevo)
    comb = grupo(ev, "Combate: pegar")["events"]
    for e in list(recorrer(comb)):
        hijos = e.get("events", [])
        base = next((x for x in hijos if len(x.get("conditions", [])) == 1 and x["conditions"][0]["parameters"][:4] == ["Sup", "Arma", "=", '"pistolita"']
                     and tiene(x, "Create", ["", "Proyectil"])), None)
        if base is None or any(len(x.get("conditions", [])) == 1 and x["conditions"][0]["parameters"][:4] == ["Sup", "Arma", "=", '"ak47"'] for x in hijos):
            continue
        nuevo = copy.deepcopy(base)
        nuevo["conditions"][0]["parameters"][3] = '"ak47"'
        for s in nuevo.get("events", []):
            for x in s.get("actions", []):
                if x["type"]["value"] == "PlaySound":
                    x["parameters"][3], x["parameters"][4] = "45", "1.6"
        hijos.insert(hijos.index(base) + 1, nuevo)

    # ---------------- Menú: Escape (Local) sin selector de personajes
    me = M["events"]
    FIJO = [a("ModVarSceneTxt", "Paso", "=", '"dificultad"'), a("ModVarScene", "Sel", "=", "1"),
            a("ModVarScene", "S1Pj", "=", "0"), a("ModVarScene", "S2Pj", "=", "1"), a("ModVarScene", "S3Pj", "=", "3"), a("ModVarScene", "S4Pj", "=", "2"),
            a("ModVarScene", "S2Ctl", "=", "-1"), a("ModVarScene", "S3Ctl", "=", "-1"), a("ModVarScene", "S4Ctl", "=", "-1")]
    cambiados = 0
    for e in recorrer(me):
        cs = e.get("conditions", [])
        local_escape = (tiene(e, "VarSceneTxt", ["Paso", "=", '"jefetipo"']) and tiene(e, "VarScene", ["JT", "=", "0"])
                        and tiene(e, "ModVarGlobalTxt", ["Modo", "=", '"escape"']) and not tiene(e, "Scene", [""]))
        if not local_escape:
            continue
        if tiene(e, "ModVarSceneTxt", ["Paso", "=", '"unirse"']):
            e["actions"] = [x for x in e["actions"] if not (x["type"]["value"] == "ModVarSceneTxt" and x["parameters"][0] == "Paso")] + copy.deepcopy(FIJO)
            cambiados += 1
    atras = next(e for e in me if tiene(e, "VarSceneTxt", ["Paso", "=", '"dificultad"']) and tiene(e, "ModVarSceneTxt", ["Paso", "=", '"equipo"']))
    if not tiene(atras, "VarGlobalTxt", ["Modo", "!=", '"escape"']):
        atras["conditions"].append(c("VarGlobalTxt", "Modo", "!=", '"escape"'))
        vuelve = copy.deepcopy(atras)
        vuelve["conditions"] = [x for x in vuelve["conditions"] if not (x["type"]["value"] == "VarGlobalTxt" and x["parameters"][0] == "Modo")]
        vuelve["conditions"].append(c("VarGlobalTxt", "Modo", "=", '"escape"'))
        vuelve["actions"] = [a("ModVarSceneTxt", "Paso", "=", '"jefetipo"'), a("ResetTimer", "", '"paso"'), a("ModVarScene", "Sel", "=", "0"), a("ModVarScene", "JT", "=", "0")]
        me.insert(me.index(atras) + 1, vuelve)
    for e in recorrer(me):
        for x in e.get("actions", []):
            if x["type"]["value"] == "TextObject::String" and x["parameters"][0] == "TxtCapB":
                x["parameters"][-1] = x["parameters"][-1].replace("12 pasos con cinemáticas · juegas como Tony", "12 pasos con cinemáticas · cambias de personaje")

    # ---------------- historia.js y armas.js (se vuelven a incrustar)
    for archivo, marca in (("historia.js", "/*FDIZ-FASE68-MOD*/"), ("armas.js", "/*FDIZ-FASE62-MOD*/")):
        codigo = open(os.path.join(AQUI, archivo), encoding="utf-8").read()
        js = [e for e in recorrer(ev) if e.get("type", "").endswith("JsCode") and e.get("inlineCode", "").startswith(marca)]
        assert len(js) == 1, "no encuentro " + marca
        js[0]["inlineCode"] = marca + "\n" + codigo

    tmp = PRY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=2))
    os.replace(tmp, PRY)
    print("Fase 72 aplicada. Escape local sin selector en %d eventos del menú." % cambiados)


if __name__ == "__main__":
    main()
