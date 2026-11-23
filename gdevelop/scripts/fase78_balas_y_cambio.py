"""FDI-Z · Fase 78 · Más balas y pausa de 1 s al cambiar de personaje.
Correr con GDevelop cerrado, después de la 74 (con sus hojas renombradas) y la 76:
    python gdevelop/scripts/fase78_balas_y_cambio.py

* Balas: pistola pequeña 24, escopeta 16, sheriff (pistola del director) 9. El AK-47 sigue con 30.
  Evento «Armas del salón» (al recoger), armas.js (A.CARGADOR, HUD) e historia.js (DE_FUEGO, armas por dueño).
* historia.js: al cambiar de personaje todo se congela 1 s (H.PAUSA_CAMBIO) para leer el aviso.
Idempotente.
"""
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import fase69_correcciones as F  # noqa: E402

PRY = F.PRY
BALAS = {'"pistolita"': "24", '"escopeta"': "16", '"pistola"': "9"}


def main():
    d = json.load(open(PRY, encoding="utf-8"))
    J = next(l for l in d["layouts"] if l["name"] == "Juego")
    ev = J["events"]
    n = 0
    for e in F.recorrer(F.grupo(ev, "Armas del salón")["events"]):
        cs = e.get("conditions", [])
        if len(cs) == 1 and cs[0]["type"]["value"] == "VarObjetTxt" and cs[0]["parameters"][:3] == ["Sup", "Arma", "="] and cs[0]["parameters"][3] in BALAS:
            for x in e.get("actions", []):
                if x["type"]["value"] == "ModVarObjet" and x["parameters"][:3] == ["Sup", "Usos", "="]:
                    x["parameters"][3] = BALAS[cs[0]["parameters"][3]]
                    n += 1
    for archivo, marca in (("historia.js", "/*FDIZ-FASE68-MOD*/"), ("armas.js", "/*FDIZ-FASE62-MOD*/")):
        codigo = open(os.path.join(AQUI, archivo), encoding="utf-8").read()
        js = [e for e in F.recorrer(ev) if e.get("type", "").endswith("JsCode") and e.get("inlineCode", "").startswith(marca)]
        assert len(js) == 1, "no encuentro " + marca
        js[0]["inlineCode"] = marca + "\n" + codigo
    tmp = PRY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=2))
    os.replace(tmp, PRY)
    print("Fase 78 aplicada. Cargadores cambiados: %d" % n)


if __name__ == "__main__":
    main()
