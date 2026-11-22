"""Fase 65 · Cinemáticas del modo Historia como videos. Idempotente. Solo Historia (Escape y Jefe no cambian).

Uso (desde la carpeta fdiz, con GDevelop CERRADO), después de fase64:
    python gdevelop/scripts/fase65_cinematicas.py
    node gdevelop/scripts/prueba_cine.js
VOLVER A CORRER este script cada vez que se agregue (o quite) un video en la carpeta: solo se registran los que existen.

Carpeta de los videos (la del proyecto para videos es assets/interfaz/videos/; los de la historia van en su subcarpeta):
    gdevelop/FDI-Z/assets/interfaz/videos/historia/<archivo de VIDEOS>
Por cada archivo que exista: recurso de video "vid_historia_0N" (ruta relativa a FDI-Z.json) y objeto Video VidHist0N
(sin loop). Si falta, cine.js muestra una tarjeta de texto (y para el 8, la charla con burbujas de la fase 61).

Qué más hace en Juego:
  * La intro de Escape ya no arranca en Historia (condición Modo != "historia" en su primer evento). Su contenido no cambia.
  * Objetos CineDib (velo de la tarjeta) y TxtCine (textos); variables CineVid, CineModo, CineSeq, HistVistos (en la red).
  * scripts/cine.js: FDIZ-FASE65-MOD arriba y FDIZ-FASE65-TICK justo después de "Cinemática de inicio" (todas las máquinas).
"""
import copy, datetime, json, os, re, shutil

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
PROY = os.path.join(RAIZ, "gdevelop", "FDI-Z")
PRY = os.path.join(PROY, "FDI-Z.json")
CARPETA = "assets/interfaz/videos/historia"
MK = "FDIZ-FASE65"
VIDEOS = {
    1: ("historia_01_inicio_aula.mp4", "Escenas 1, 2 y 3 del salón en un solo video (inicio de la partida)"),
    2: ("historia_02_joel_cic.mp4", "Los estudiantes encuentran al profesor Joel (Cubículos del CIC)"),
    3: ("historia_03_telefono_apagon.mp4", "El teléfono no tiene línea y se corta la energía en el CIC"),
    4: ("historia_04_zombi_conserje.mp4", "Aparece el zombi conserje al abrir su puerta (P59)"),
    5: ("historia_05_escopeta_casillero.mp4", "Encuentran el objeto del casillero (escopeta, conserjería)"),
    6: ("historia_06_justino_neveria.mp4", "Encuentran al profesor Justino (nevería)"),
    7: ("historia_07_cajon_director.mp4", "Encuentran el objeto en el cajón del director (revólver sheriff)"),
    8: ("historia_08_canepa_autobus.mp4", "Hablan con Cánepa después de llevar la comida (luego, la gasolina)"),
}
VARS = [("CineVid", 0), ("CineModo", ""), ("CineSeq", 0), ("HistVistos", "")]


def js(code, marca):
    return {"type": "BuiltinCommonInstructions::JsCode", "inlineCode": "/*" + marca + "*/\n" + code,
            "parameterObjects": "", "useStrict": True, "eventsSheetExpanded": False}


def recorrer(lst):
    for e in lst:
        yield e
        yield from recorrer(e.get("events", []))


def es_js(e, marca):
    return e.get("type", "").endswith("JsCode") and e.get("inlineCode", "").startswith("/*" + marca)


def quitar(lst, marca):
    lst[:] = [e for e in lst if not es_js(e, marca)]
    for e in lst:
        if e.get("events"):
            quitar(e["events"], marca)


def main():
    d = json.load(open(PRY, encoding="utf-8"))
    resp = os.path.join(RAIZ, "gdevelop", "respaldos")
    os.makedirs(resp, exist_ok=True)
    bak = os.path.join(resp, "antes_de_fase65_%s.json" % datetime.date.today().strftime("%Y%m%d"))
    if not os.path.exists(bak):
        shutil.copy(PRY, bak)
    carpeta = os.path.join(PROY, *CARPETA.split("/"))
    os.makedirs(carpeta, exist_ok=True)
    J = next(l for l in d["layouts"] if l["name"] == "Juego")
    ob = {o["name"]: o for o in J["objects"]}
    res = d["resources"]["resources"]

    # ---- videos: recurso y objeto solo si el archivo existe
    hay, faltan, reales = [], [], {}
    en_carpeta = sorted(os.listdir(carpeta))
    for n, (archivo, _) in VIDEOS.items():
        nombre_res, nombre_obj = "vid_historia_%02d" % n, "VidHist%02d" % n
        # Windows suele ocultar la extensión y el archivo queda como "x.mp4.mp4": se acepta tal cual (no se renombra)
        if archivo not in en_carpeta:
            archivo = next((f for f in en_carpeta if f.lower().startswith(archivo.lower()) and f.lower().endswith(".mp4")), archivo)
        reales[n] = archivo
        existe = os.path.exists(os.path.join(carpeta, archivo))
        d["resources"]["resources"] = res = [r for r in res if r["name"] != nombre_res]
        J["objects"] = [o for o in J["objects"] if o["name"] != nombre_obj]
        if existe:
            res.append({"file": CARPETA + "/" + archivo, "kind": "video", "metadata": "", "name": nombre_res, "userAdded": True})
            J["objects"].append({"assetStoreId": "", "name": nombre_obj, "type": "Video::VideoObject", "variables": [], "effects": [], "behaviors": [],
                                 "content": {"opacity": 255, "loop": False, "volume": 100, "videoResource": nombre_res}})
            hay.append(n)
        else:
            faltan.append(n)
    ob = {o["name"]: o for o in J["objects"]}

    # ---- objetos de la tarjeta
    if "CineDib" not in ob:
        t = copy.deepcopy(ob["ProfDib"]); t["name"] = "CineDib"; J["objects"].append(t)
    if "TxtCine" not in ob:
        t = copy.deepcopy(ob["TxtDialogo"]); t["name"] = "TxtCine"; J["objects"].append(t)

    # ---- variables y red
    for n, v in VARS:
        if not any(x["name"] == n for x in J["variables"]):
            J["variables"].append({"name": n, "type": "string" if isinstance(v, str) else "number", "value": v})
    T = next(l for l in d["layouts"] if l["name"] == "Titulo")
    nucleo = next(e for e in recorrer(T["events"]) if e.get("type", "").endswith("JsCode") and "gdjs.fdizNetCfg=" in e["inlineCode"])
    code = nucleo["inlineCode"]
    m = re.search(r"gdjs\.fdizNetCfg=", code)
    cfg, fin = json.JSONDecoder().raw_decode(code, m.end())
    for n, _ in VARS:
        if n not in cfg["sv"]:
            cfg["sv"].append(n)
    nucleo["inlineCode"] = code[:m.end()] + json.dumps(cfg, ensure_ascii=False) + code[fin:]

    # ---- la intro de Escape no arranca en Historia (Historia tiene su video y su interludio corto)
    ev = J["events"]
    cin = next(e for e in ev if e.get("type", "").endswith("Group") and e.get("name", "").startswith("Cinemática de inicio"))
    ini = next(x for x in cin["events"] if any(a["type"]["value"] == "ModVarSceneTxt" and a["parameters"][:3] == ["Estado", "=", '"intro"'] for a in x.get("actions", [])))
    if not any(c["type"]["value"] == "VarGlobalTxt" and c["parameters"][:3] == ["Modo", "!=", '"historia"'] for c in ini["conditions"]):
        ini["conditions"].append({"type": {"inverted": False, "value": "VarGlobalTxt"}, "parameters": ["Modo", "!=", '"historia"']})

    # ---- cine.js
    quitar(ev, MK + "-MOD"); quitar(ev, MK + "-TICK")
    k = next((i for i, e in enumerate(ev) if es_js(e, "FDIZ-FASE56-MOD")), 0)
    ev.insert(k, js(open(os.path.join(AQUI, "cine.js"), encoding="utf-8").read(), MK + "-MOD"))
    c = next(i for i, e in enumerate(ev) if e is cin)
    ev.insert(c + 1, js("if (gdjs.fdizCine) gdjs.fdizCine.tick(runtimeScene);", MK + "-TICK"))

    # ---- qué espera la carpeta
    lee = ["Videos de las cinemáticas del modo Historia (fase 65). Formato: MP4 (H.264), 1920x1080 o 16:9, con su audio.",
           "Después de copiar o cambiar un video, correr con GDevelop cerrado:  python gdevelop/scripts/fase65_cinematicas.py", ""]
    for n, (archivo, desc) in VIDEOS.items():
        nota = "   [FALTA]" if n in faltan else ("" if reales[n] == archivo else "   [en la carpeta como %s]" % reales[n])
        lee.append("%s  ->  %s%s" % (archivo, desc, nota))
    open(os.path.join(carpeta, "LEEME.txt"), "w", encoding="utf-8", newline="\n").write("\n".join(lee) + "\n")

    tmp = PRY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=2))
    os.replace(tmp, PRY)
    print("Fase 65 aplicada. Videos en el proyecto: %s; faltan: %s" % (hay or "ninguno", [VIDEOS[n][0] for n in faltan] or "ninguno"))


if __name__ == "__main__":
    main()
