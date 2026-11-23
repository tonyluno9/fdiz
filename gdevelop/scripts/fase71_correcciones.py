"""FDI-Z · Fase 71 · Correcciones (pedido del 2026-11-23). Correr con GDevelop cerrado, después de la 68 y la 69:
    python gdevelop/scripts/fase71_correcciones.py

* historia.js (se vuelve a incrustar en FDIZ-FASE68-MOD):
  - Diálogos del inicio (pasos 1 a 3): Tony se mueve libre, sin salir del salón B-01.
  - Los zombis no se mueven hasta que termina la alerta (fin de la secuencia del paso 3).
  - Joel (paso 5): el diálogo solo arranca con la puerta de su sala abierta (P37 o P38, x 3744) y Tony adentro, junto a él.
  - El zombi de la sala del conserje (paso 7) es el gordo (ZGordo).
* Impacto de bala y perdigón: vuelve el tinte rojo de daño (la fase 69 lo había quitado al reescribir las acciones).
* Animaciones de disparo de lado con los GIF de animaciones_gif/personajes/<pj>/:
  alan (AK-47, para pistola y escopeta), cesar y miranda (escopeta). Igual que las de Tony: la izquierda se voltea.
Segunda tanda (mismo día):
* historia.js: Tony también se mueve en los diálogos de Joel (paso 5) y de la llamada del CIC (paso 6) (H.DLG_LIBRE);
  Joel arranca al abrir P37 o P38; luz circular que sigue a Tony durante el apagón; la pistola inicial pasa a (5830, 3036)
  (en 5960, 2960 quedaba dentro del choque del escritorio); la sheriff queda en el piso de la dirección junto a P47 y
  Tony la recoge aunque traiga otra arma; un checkpoint en un paso automático ya no se queda en negro.
* armas.js (se vuelve a incrustar en FDIZ-FASE62-MOD): mira también con un lanzable en la mano; reacción de daño de los
  zombis (cuadros 0-1 de golpe_morir, 0.22 s) cuando pierden vida y siguen vivos.
* Se quita el sonido de la ulti (especial) de Miranda.
Idempotente.
"""
import json
import os
import sys

from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import fase69_correcciones as F  # noqa: E402  (reutiliza cuadros_gif, anclas, animacion, constantes)

RAIZ, PRY, GEN = F.RAIZ, F.PRY, F.GEN
GIFS = os.path.join(RAIZ, "animaciones_gif", "personajes")
# personaje -> {animación: gif}
ARTE = {
    "alan": {"pistola": "alan_disparo_lado_ak47.gif", "escopeta": "alan_disparo_lado_ak47.gif"},
    "cesar": {"escopeta": "cesar_disparar_lado_escopeta.gif"},
    "miranda": {"escopeta": "miranda_disparo_lado_escopeta.gif"},
}


def arte(pj, arma, gif):
    cuadros = F.cuadros_gif(os.path.join(GIFS, pj, gif))
    if len(cuadros) > 8:                                     # GIF con muchos cuadros: se toman 6 repartidos
        cuadros = [cuadros[round(i * (len(cuadros) - 1) / 5)] for i in range(6)]
    top, pie, cx = F.anclas(cuadros[0])
    s = F.ALTO_CUERPO / (pie - top)
    carpeta = os.path.join(GEN, "personajes", pj, "disparo_%s_lado" % arma)
    os.makedirs(carpeta, exist_ok=True)
    nombres = []
    for k, f in enumerate(cuadros):
        g = f.resize((max(1, round(f.size[0] * s)), max(1, round(f.size[1] * s))), Image.LANCZOS)
        g.putalpha(g.getchannel("A").point(lambda v: 255 if v >= 110 else 0))
        lienzo = Image.new("RGBA", F.LIENZO, (0, 0, 0, 0))
        lienzo.alpha_composite(g, (round(F.ORIGEN[0] - cx * s), round(F.ORIGEN[1] - pie * s)))
        nombre = "disparo_%s_lado_%02d.png" % (arma, k)
        lienzo.save(os.path.join(carpeta, nombre))
        nombres.append("personajes/%s/disparo_%s_lado/%s" % (pj, arma, nombre))
    return nombres


def main():
    d = json.load(open(PRY, encoding="utf-8"))
    J = next(l for l in d["layouts"] if l["name"] == "Juego")
    ob = {o["name"]: o for o in J["objects"]}
    res = d["resources"]["resources"]
    nombres = {r["name"] for r in res}

    # ---- animaciones
    hechas = {}
    sup = ob["Sup"]
    for pj, armas in ARTE.items():
        for arma, gif in armas.items():
            imgs = arte(pj, arma, gif)
            for im in imgs:
                if im not in nombres:
                    res.append({"file": "../../generado/sprites/" + im, "kind": "image", "metadata": "", "name": im, "smoothed": False, "userAdded": True})
                    nombres.add(im)
            nombre = "%s_%s_lado" % (pj, arma)
            nueva = F.animacion(nombre, imgs)
            k = next((i for i, x in enumerate(sup["animations"]) if x["name"] == nombre), None)
            if k is None:
                sup["animations"].append(nueva)
            else:
                sup["animations"][k] = nueva
            hechas[nombre] = len(imgs)

    # ---- tinte rojo al impacto de bala / perdigón
    lz = F.grupo(J["events"], "Lanzables")
    tintes = 0
    for e in F.recorrer(lz["events"]):
        tipo = next((x["parameters"][3] for x in e.get("conditions", []) if x["type"]["value"] == "VarObjetTxt" and x["parameters"][:3] == ["Proyectil", "Tipo", "="]), None)
        if tipo not in ('"bala"', '"perdigon"'):
            continue
        if not F.tiene(e, "ChangeColor", ["Zombies"]):
            e["actions"] += [F.a("ChangeColor", "Zombies", '"255;90;90"'), F.a("ResetObjectTimer", "Zombies", '"tinte"')]
        tintes += 1

    # ---- sin sonido en la ulti (especial) de Miranda
    mudos = 0
    for e in F.recorrer(J["events"]):
        antes = len(e.get("actions", []))
        if antes:
            e["actions"] = [x for x in e["actions"] if not (x["type"]["value"] in ("PlaySound", "PlaySoundCanal") and "miranda_especial" in json.dumps(x["parameters"]))]
            mudos += antes - len(e["actions"])

    # ---- historia.js y armas.js (se vuelven a incrustar)
    for archivo, marca in (("historia.js", "/*FDIZ-FASE68-MOD*/"), ("armas.js", "/*FDIZ-FASE62-MOD*/")):
        codigo = open(os.path.join(AQUI, archivo), encoding="utf-8").read()
        js = [e for e in F.recorrer(J["events"]) if e.get("type", "").endswith("JsCode") and e.get("inlineCode", "").startswith(marca)]
        assert len(js) == 1, "no encuentro " + marca
        js[0]["inlineCode"] = marca + "\n" + codigo

    tmp = PRY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=2))
    os.replace(tmp, PRY)
    print("Fase 71 aplicada. Animaciones:", hechas, "· impactos con tinte:", tintes, "· sonidos de la ulti de Miranda quitados:", mudos)


if __name__ == "__main__":
    main()
