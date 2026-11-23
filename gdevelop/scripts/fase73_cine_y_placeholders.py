"""FDI-Z · Fase 73 · Cinemáticas congeladas, diálogos con movimiento, aviso de cambio y placeholders de disparo.
Correr con GDevelop cerrado, después de la 68, 69, 71 y 72:
    python gdevelop/scripts/fase73_cine_y_placeholders.py

* historia.js (se vuelve a incrustar en FDIZ-FASE68-MOD):
  - Durante los videos (y la pantalla negra de los que faltan) se congela todo: TimeScale 0 hasta que termina.
  - En todos los diálogos los personajes se pueden mover (H.DLG_LIBRE).
  - Cambio de personaje: aviso pequeño en la línea de ayuda («Cambio de personaje: ahora controlas a X»), no letrero.
  - Inicio (pasos 1 a 3): quien dice su línea da unos pasos cortos (18 px en 0.5 s, alternando el lado).
* armas.js: el disparo hacia arriba y hacia abajo usa <pj>_<pistola|escopeta>_<arriba|abajo>.
* Placeholders de disparo para Tony, Miranda, Alan y César: <pj>_pistola_arriba, <pj>_escopeta_arriba y
  <pj>_escopeta_abajo (la de pistola hacia abajo ya existía, fase 62). Cuadros en
  generado/sprites/personajes/<pj>/<arma>_<dir>/ (copias de pegar_arriba o de pistola_abajo): para poner el arte
  final basta con reemplazar esos PNG con el mismo nombre y tamaño.
Idempotente (no pisa los PNG que ya existan).
"""
import copy
import json
import os
import shutil
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import fase69_correcciones as F  # noqa: E402

RAIZ, PRY, GEN = F.RAIZ, F.PRY, F.GEN
PJS = ["tony", "miranda", "alan", "cesar"]
# animación nueva -> animación de la que se copian cuadros, origen y máscara
NUEVAS = {"pistola_arriba": "pegar_arriba", "escopeta_arriba": "pegar_arriba", "escopeta_abajo": "pistola_abajo"}


def main():
    d = json.load(open(PRY, encoding="utf-8"))
    J = next(l for l in d["layouts"] if l["name"] == "Juego")
    sup = next(o for o in J["objects"] if o["name"] == "Sup")
    res = d["resources"]["resources"]
    por_nombre = {r["name"]: r for r in res}
    an = {a["name"]: a for a in sup["animations"]}
    hechas = []
    for pj in PJS:
        for nueva, base in NUEVAS.items():
            b = an.get(pj + "_" + base)
            if not b:
                continue
            carpeta = os.path.join(GEN, "personajes", pj, nueva)
            os.makedirs(carpeta, exist_ok=True)
            anim = copy.deepcopy(b)
            anim["name"] = pj + "_" + nueva
            for k, sp in enumerate(anim["directions"][0]["sprites"]):
                origen = por_nombre[sp["image"]]["file"]
                ruta_origen = os.path.normpath(os.path.join(RAIZ, "gdevelop", "FDI-Z", origen))
                archivo = "%s_%02d.png" % (nueva, k)
                destino = os.path.join(carpeta, archivo)
                if not os.path.exists(destino):
                    shutil.copy(ruta_origen, destino)
                nombre = "personajes/%s/%s/%s" % (pj, nueva, archivo)
                if nombre not in por_nombre:
                    r = {"file": "../../generado/sprites/" + nombre, "kind": "image", "metadata": "", "name": nombre, "smoothed": False, "userAdded": True}
                    res.append(r); por_nombre[nombre] = r
                sp["image"] = nombre
            anim["directions"][0]["looping"] = False
            k = next((i for i, x in enumerate(sup["animations"]) if x["name"] == anim["name"]), None)
            if k is None:
                sup["animations"].append(anim)
            else:
                sup["animations"][k] = anim
            hechas.append(anim["name"])

    for archivo, marca in (("historia.js", "/*FDIZ-FASE68-MOD*/"), ("armas.js", "/*FDIZ-FASE62-MOD*/")):
        codigo = open(os.path.join(AQUI, archivo), encoding="utf-8").read()
        js = [e for e in F.recorrer(J["events"]) if e.get("type", "").endswith("JsCode") and e.get("inlineCode", "").startswith(marca)]
        assert len(js) == 1, "no encuentro " + marca
        js[0]["inlineCode"] = marca + "\n" + codigo

    tmp = PRY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=2))
    os.replace(tmp, PRY)
    print("Fase 73 aplicada. Placeholders:", len(hechas))


if __name__ == "__main__":
    main()
