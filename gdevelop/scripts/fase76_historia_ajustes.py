"""FDI-Z · Fase 76 · Ajustes de Historia y balas más gruesas.
Correr con GDevelop cerrado, después de la 73 y la 74:
    python gdevelop/scripts/fase76_historia_ajustes.py

* historia.js (se vuelve a incrustar en FDIZ-FASE68-MOD):
  - Inicio (hasta que termina la alerta): nadie ataca (Tony pegaba al aire). Se hace en H.tras, antes de «Combate: pegar».
  - Paso 5: al llegar al CIC la misión cambia a «Checa de dónde viene el ruido» (abrir la sala de Joel, flecha a su puerta).
  - Paso 6: el apagón llega en cuanto termina el video de la llamada (C05), antes de los diálogos.
  - Paso 10: la llave y el cambio a Alan ocurren en cuanto termina el video C08, antes de los diálogos.
  - Paso 11: durante la cuenta del autobús Alan recarga el AK-47 cada 24 s y dice «¡Encontré balas!» (globo sin voz).
* Balas y perdigones más gruesos: el dibujo se ve 1.6 veces más grande y el impacto alcanza 62 px del zombi en vez
  de 46 (los lanzables no cambian: su Golpes es 0).
Idempotente.
"""
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import fase69_correcciones as F  # noqa: E402

PRY = F.PRY
VIEJO = "DistanceBetweenPositions(Zombies.X(), Zombies.Y() - 40, Proyectil.X(), Proyectil.Y())"
RADIO = "46 + 16 * min(1, Proyectil.Variable(Golpes))"
ESCALA = "1.6"


def main():
    d = json.load(open(PRY, encoding="utf-8"))
    J = next(l for l in d["layouts"] if l["name"] == "Juego")
    ev = J["events"]
    # radio de impacto
    radios = 0
    for e in F.recorrer(F.grupo(ev, "Lanzables")["events"]):
        for x in e.get("conditions", []):
            if x["type"]["value"] == "BuiltinCommonInstructions::CompareNumbers" and x["parameters"][0] == VIEJO and x["parameters"][1] == "<":
                if x["parameters"][2] in ("46", RADIO):
                    x["parameters"][2] = RADIO
                    radios += 1
    # dibujo más grueso al crear cada proyectil de arma de fuego
    escalas = 0
    for e in F.recorrer(F.grupo(ev, "Combate: pegar")["events"]):
        acts = e.get("actions", [])
        if not any(a["type"]["value"] == "Create" and a["parameters"][1] == "Proyectil" for a in acts):
            continue
        nuevas = []
        for a in acts:
            if a["type"]["value"] == "ChangeScale" and a["parameters"][0] == "Proyectil":
                continue
            nuevas.append(a)
            if a["type"]["value"] == "ResetObjectTimer" and a["parameters"][:2] == ["Proyectil", '"vida"']:
                nuevas.append(F.a("ChangeScale", "Proyectil", "=", ESCALA))
                escalas += 1
        e["actions"] = nuevas
    # historia.js y armas.js
    for archivo, marca in (("historia.js", "/*FDIZ-FASE68-MOD*/"), ("armas.js", "/*FDIZ-FASE62-MOD*/")):
        codigo = open(os.path.join(AQUI, archivo), encoding="utf-8").read()
        js = [e for e in F.recorrer(ev) if e.get("type", "").endswith("JsCode") and e.get("inlineCode", "").startswith(marca)]
        assert len(js) == 1, "no encuentro " + marca
        js[0]["inlineCode"] = marca + "\n" + codigo
    tmp = PRY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=2))
    os.replace(tmp, PRY)
    print("Fase 76 aplicada. Radios de impacto: %d · proyectiles más gruesos: %d" % (radios, escalas))


if __name__ == "__main__":
    main()
