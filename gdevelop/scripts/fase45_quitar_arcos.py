"""Fase 45 · Quita los dos arcos de entrada/salida del mapa. Idempotente; va al final de la cadena (después de fase44).

Uso (desde la carpeta fdiz, con GDevelop CERRADO):  python3 gdevelop/scripts/fase45_quitar_arcos.py
Qué hace en FDI-Z.json (escena Juego): borra el sprite y su choque de
  - arco_entrada (Mueble en 2208,5056; choque 2048,5016 96x40; marcador 'arco_entrada' en 2192,5040): el arco grande del sur;
  - arco_salida  (Mueble en 6912,4864; choque 6897,4834 30x30): el arco chico con reja.
Ningún evento los usa. No se tocan las vallas, el directorio ni los muros.
"""
import datetime, json, os, shutil

AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
SPRITES = {"hitos/arco_entrada", "hitos/arco_salida"}
CHOQUES = {("ChoqueMueble", 2048, 5016), ("ChoqueMueble", 6897, 4834)}


def main():
    d = json.load(open(PRY, encoding="utf-8"))
    resp = os.path.join(AQUI, "..", "respaldos")
    os.makedirs(resp, exist_ok=True)
    bak = os.path.join(resp, "antes_de_fase45_%s.json" % datetime.date.today().strftime("%Y%m%d"))
    if not os.path.exists(bak):
        shutil.copy(PRY, bak)
    J = next(l for l in d["layouts"] if l["name"] == "Juego")
    iv = lambda i: {v["name"]: v["value"] for v in i.get("initialVariables", [])}

    def quitar(i):
        v = iv(i)
        if i["name"] == "Mueble" and v.get("Sprite") in SPRITES: return True
        if (i["name"], i["x"], i["y"]) in CHOQUES: return True
        return i["name"] == "Marcador" and v.get("Tipo") == "arco_entrada"

    antes = len(J["instances"])
    J["instances"] = [i for i in J["instances"] if not quitar(i)]
    json.dump(d, open(PRY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("OK fase45 (instancias quitadas: %d)" % (antes - len(J["instances"])))


main()
