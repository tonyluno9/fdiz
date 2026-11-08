"""Copia dentro del proyecto todos los recursos que apuntan fuera de él (rutas que empiezan con ../)
y reescribe sus rutas, para que la carpeta FDI-Z sea portable por sí sola.
Uso (con GDevelop cerrado): python empaquetar_recursos.py <carpeta del proyecto FDI-Z>
No toca los originales de generado\\: solo copia.
"""
import json, os, shutil, sys, datetime

proy = sys.argv[1]
ruta = os.path.join(proy, "FDI-Z.json")
resp = os.path.join(os.path.dirname(proy), "respaldos")
os.makedirs(resp, exist_ok=True)
shutil.copyfile(ruta, os.path.join(resp, "FDI-Z_antes_empaquetar_" +
                                   datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S") + ".json"))
p = json.load(open(ruta, encoding="utf-8"))
n = 0
for r in p["resources"]["resources"]:
    f = r.get("file", "")
    if f.startswith("../"):
        origen = os.path.normpath(os.path.join(proy, f))
        nuevo = "assets/ext/" + f.replace("../", "")
        destino = os.path.join(proy, *nuevo.split("/"))
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        shutil.copyfile(origen, destino)
        r["file"] = nuevo
        n += 1
json.dump(p, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"OK: {n} recursos copiados a assets/ext/")
