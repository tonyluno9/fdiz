"""Fase 44 · Cierra con vallas blancas los huecos de la valla sur (calle). Idempotente; va al final de la cadena (después de fase43).

Uso (desde la carpeta fdiz, con GDevelop CERRADO):  python3 gdevelop/scripts/fase44_valla_sur.py
Qué hace en FDI-Z.json (escena Juego):
  La fila de vallas del sur (ChoqueMueble de 128x20 en y=5226 + sprite 'hitos/reja_blanca' en y=5246) tenía dos huecos:
  x 1920-2432 (la entrada principal junto al arco: el jugador salía a la calle) y x 2688-2816 (entre la última valla y el muro) y x 4384-5600.
  También estaba abierto x 4384-5600 (junto a la calle del estacionamiento, de muro a muro).
  Se añaden 15 tramos con el mismo patrón (choque en x,5226; reja visible en x+64,5246).
  Ahora se cruza el arco solo hasta la valla: no hay salida al sur.
"""
import datetime, json, os, shutil, uuid

AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
TRAMOS = [1920, 2048, 2176, 2304, 2688] + [4320 + 128 * k for k in range(10)]


def main():
    d = json.load(open(PRY, encoding="utf-8"))
    resp = os.path.join(AQUI, "..", "respaldos")
    os.makedirs(resp, exist_ok=True)
    bak = os.path.join(resp, "antes_de_fase44_%s.json" % datetime.date.today().strftime("%Y%m%d"))
    if not os.path.exists(bak):
        shutil.copy(PRY, bak)
    J = next(l for l in d["layouts"] if l["name"] == "Juego")
    ins = J["instances"]
    iv = lambda i: {v["name"]: v["value"] for v in i.get("initialVariables", [])}
    plantilla_ch = next(i for i in ins if i["name"] == "ChoqueMueble" and i["x"] == 1792 and i["y"] == 5226)
    plantilla_mu = next(i for i in ins if i["name"] == "Mueble" and i["x"] == 1856 and i["y"] == 5246
                        and iv(i).get("Sprite") == "hitos/reja_blanca")
    hay = {(i["name"], i["x"], i["y"]) for i in ins}
    import copy
    nuevos = 0
    for x in TRAMOS:
        if ("ChoqueMueble", x, 5226) not in hay:
            c = copy.deepcopy(plantilla_ch)
            c["x"] = x
            c["persistentUuid"] = str(uuid.uuid5(uuid.NAMESPACE_URL, "fdiz-f44-ch-%d" % x))
            ins.append(c); nuevos += 1
        if ("Mueble", x + 64, 5246) not in hay:
            m = copy.deepcopy(plantilla_mu)
            m["x"] = x + 64
            m["persistentUuid"] = str(uuid.uuid5(uuid.NAMESPACE_URL, "fdiz-f44-mu-%d" % x))
            ins.append(m); nuevos += 1
    json.dump(d, open(PRY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("OK fase44 (instancias nuevas: %d)" % nuevos)


main()
