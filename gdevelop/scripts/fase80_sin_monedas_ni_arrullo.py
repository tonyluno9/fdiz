"""FDI-Z · Fase 80 · Sin sonido de monedas ni de la habilidad de dormir de Miranda.
Correr con GDevelop cerrado, después de la 79:
    python gdevelop/scripts/fase80_sin_monedas_ni_arrullo.py

* sfx.js ya no toca oro_moneda (monedas, dinero ni oro del Jefe); se vuelve a incrustar en FDIZ-FASE60-MOD de todas las escenas.
* Juego › «Habilidades, especiales y pasivas»: se quita el sonido miranda_habilidad.ogg de la habilidad de Miranda
  (dormir zombis). Su voz (miranda_06) no se toca.
Idempotente.
"""
import json
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
SONIDO = "efectos/habilidades/miranda_habilidad.ogg"


def recorrer(evs):
    for e in evs:
        yield e
        yield from recorrer(e.get("events", []))


def main():
    d = json.load(open(PRY, encoding="utf-8"))
    codigo = open(os.path.join(AQUI, "sfx.js"), encoding="utf-8").read()
    n = q = 0
    for L in d["layouts"]:
        for e in recorrer(L["events"]):
            if e.get("type", "").endswith("JsCode") and e.get("inlineCode", "").startswith("/*FDIZ-FASE60-MOD*/"):
                e["inlineCode"] = "/*FDIZ-FASE60-MOD*/\n" + codigo
                n += 1
            subs = e.get("events", [])
            antes = len(subs)
            subs[:] = [s for s in subs if not (len(s.get("actions", [])) == 1 and s["actions"][0]["type"]["value"] == "PlaySound"
                                                and s["actions"][0]["parameters"][1] == SONIDO
                                                and any(c["parameters"][:1] == ["Zombies"] for x in subs for c in x.get("conditions", [])))]
            q += antes - len(subs)
    tmp = PRY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=2))
    os.replace(tmp, PRY)
    print("Fase 80 aplicada. sfx.js en %d escenas; sonidos de Miranda quitados: %d" % (n, q))


if __name__ == "__main__":
    main()
