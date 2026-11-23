"""FDI-Z · Fase 84 · Símbolo de tecla en los avisos, Tony más grande en su especial, puertas que se rompen de un balazo
y Resultados de Historia con REINTENTAR desde 0 y CONTINUAR desde el punto de control.
Correr con GDevelop cerrado, después de la 83:
    python gdevelop/scripts/fase84_teclas_tony_puertas_historia.py

* usar.js (FDIZ-FASE56-MOD): el aviso de interacción lleva la tecla dibujada como símbolo ([F] Mantén para abrir; A verde
  en mando). Los avisos sin tecla (puerta restringida) no llevan símbolo.
* tony_gym.js (evento FDIZ-FASE84-TONY): Tony crece 20 % mientras dura el Modo gym.
* Balas y perdigones: al chocar con una puerta normal (Tipo "normal") la rompen de un tiro (Vida = 0; el evento de
  siempre la abre). Las restringidas y electrónicas no (son parte de las misiones).
* historia.js (FDIZ-FASE68-MOD): al reintentar, el control humano vuelve al jugador 1 antes de pasar a los demás a bot
  (antes, si el control había quedado en otro alumno por un cambio de personaje, todos quedaban como bots).
* resultados_historia.js (escena Resultados, evento FDIZ-FASE84-RES): REINTENTAR empieza la historia desde el paso 1;
  botón nuevo CONTINUAR (C) sigue desde el punto de control, salvo en dificultad pesadilla (sin puntos de control).
Idempotente.
"""
import json
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")


def recorrer(evs):
    for e in evs:
        yield e
        yield from recorrer(e.get("events", []))


def tiene(e, t, p):
    return any(x["type"]["value"] == t and x["parameters"][:len(p)] == p for x in e.get("conditions", []) + e.get("actions", []))


def js(marca, codigo):
    return {"type": "BuiltinCommonInstructions::JsCode", "inlineCode": marca + "\n" + codigo, "parameterObjects": "",
            "useStrict": True, "eventsSheetExpanded": False}


def poner(lista, marca, codigo, donde=None):
    ex = [e for e in lista if e.get("type", "").endswith("JsCode") and e.get("inlineCode", "").startswith(marca)]
    if ex:
        ex[0]["inlineCode"] = marca + "\n" + codigo
    elif donde is None:
        lista.append(js(marca, codigo))
    else:
        lista.insert(donde, js(marca, codigo))


def leer(n):
    return open(os.path.join(AQUI, n), encoding="utf-8").read()


def main():
    d = json.load(open(PRY, encoding="utf-8"))
    J = next(l for l in d["layouts"] if l["name"] == "Juego")
    R = next(l for l in d["layouts"] if l["name"] == "Resultados")
    ev = J["events"]

    for archivo, marca in (("usar.js", "/*FDIZ-FASE56-MOD*/"), ("historia.js", "/*FDIZ-FASE68-MOD*/")):
        e = [x for x in recorrer(ev) if x.get("type", "").endswith("JsCode") and x.get("inlineCode", "").startswith(marca)]
        assert len(e) == 1, "no encuentro " + marca
        e[0]["inlineCode"] = marca + "\n" + leer(archivo)

    poner(ev, "/*FDIZ-FASE84-TONY*/", leer("tony_gym.js") + "\nif (gdjs.fdizTonyGym) gdjs.fdizTonyGym.tick(runtimeScene);\n")
    poner(R["events"], "/*FDIZ-FASE84-RES*/", leer("resultados_historia.js"))

    # balazo a una puerta normal: Vida = 0 (antes del evento que borra la bala)
    n = 0
    for e in recorrer(ev):
        hijos = e.get("events", [])
        for i, h in enumerate(hijos):
            if tiene(h, "CollisionNP", ["Proyectil", "Puerta"]) and tiene(h, "ModVarObjet", ["Proyectil", "Pego", "=", "1"]):
                if not any(tiene(x, "ModVarObjet", ["Puerta", "Vida", "=", "0"]) for x in hijos):
                    hijos.insert(i + 1, {
                        "type": "BuiltinCommonInstructions::Standard",
                        "conditions": [
                            {"type": {"inverted": False, "value": "CollisionNP"}, "parameters": ["Proyectil", "Puerta", "", ""]},
                            {"type": {"value": "BuiltinCommonInstructions::Or"}, "parameters": [], "subInstructions": [
                                {"type": {"inverted": False, "value": "VarObjetTxt"}, "parameters": ["Proyectil", "Tipo", "=", '"bala"']},
                                {"type": {"inverted": False, "value": "VarObjetTxt"}, "parameters": ["Proyectil", "Tipo", "=", '"perdigon"']}]},
                            {"type": {"inverted": False, "value": "VarObjetTxt"}, "parameters": ["Puerta", "Tipo", "=", '"normal"']},
                            {"type": {"inverted": False, "value": "VarObjet"}, "parameters": ["Puerta", "Vida", ">", "0"]}],
                        "actions": [
                            {"type": {"value": "ModVarObjet"}, "parameters": ["Puerta", "Vida", "=", "0"]},
                            {"type": {"value": "ChangeColor"}, "parameters": ["Puerta", '"255;160;160"']}],
                        "events": [{"type": "BuiltinCommonInstructions::Standard",
                                    "conditions": [{"type": {"inverted": False, "value": "VarGlobal"}, "parameters": ["SonidoActivo", "=", "1"]}],
                                    "actions": [{"type": {"value": "PlaySound"}, "parameters": ["", "efectos/mundo/puerta_golpe.wav", "", "70", "1"]}]}]})
                    n += 1
                break

    tmp = PRY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=2))
    os.replace(tmp, PRY)
    print("Fase 84 aplicada. Evento de balazo a puertas: %s" % ("agregado" if n else "ya estaba"))


if __name__ == "__main__":
    main()
