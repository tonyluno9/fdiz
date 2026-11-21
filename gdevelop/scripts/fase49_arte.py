"""Fase 49 · Bloque "Arte e interfaz" del reporte de pruebas. Idempotente; va después de la fase 48.
 a) Habilidad E (el Especial; la Habilidad es Q): los efectos "*_esp" salen 2.6 veces más grandes (eran sprites de ~100 px sobre un personaje de ~100 px).
 b) Cámara más cercana: el tope de zoom sube de 1.4 a 1.75 (el piso de 0.7 no cambia, para no perder de vista a los aliados lejanos).
 c) Pantalla de controles: si existen assets/interfaz/ctl_teclado_ia.png y/o ctl_mando_ia.png (imágenes hechas con IA), se recortan, escalan y
    reemplazan a las actuales (sin deformar, 320 px de alto). Sin esos archivos no cambia nada (ver gdevelop/prompts_controles.md)."""
import copy, datetime, json, os, shutil

AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
IMG = os.path.join(AQUI, "..", "FDI-Z", "assets", "interfaz")
MK = "FDIZ-FASE49"
ESC_ZOOM = 2.6
TOPE_ZOOM = 1.75
NOCLI = {"type": {"inverted": False, "value": "VarGlobal"}, "parameters": ["NetRol", "!=", "2"]}
CODIGO = ("/*" + MK + "-EFECTO*/\n"
          "for (const o of objects) {\n"
          "  const n = o.getAnimationName ? o.getAnimationName() : \"\";\n"
          "  const k = /_esp$/.test(n) ? %s : 1;\n"
          "  if (o.__f49 !== k) { o.setScale(k); o.__f49 = k; }\n"
          "}" % ESC_ZOOM)


def recorrer(lst):
    for e in lst:
        yield e
        yield from recorrer(e.get("events", []))


def main():
    d = json.load(open(PRY, encoding="utf-8"))
    resp = os.path.join(AQUI, "..", "respaldos"); os.makedirs(resp, exist_ok=True)
    bak = os.path.join(resp, "antes_de_fase49_%s.json" % datetime.date.today().strftime("%Y%m%d"))
    if not os.path.exists(bak): shutil.copy(PRY, bak)
    J = next(l for l in d["layouts"] if l["name"] == "Juego")

    # ---- b) zoom
    n_z = 0
    for e in recorrer(J["events"]):
        for a in e.get("actions", []):
            p = a.get("parameters", [])
            if a["type"]["value"] == "ModVarScene" and p[:2] == ["CamZoom", "="] and "clamp(" in p[2]:
                p[2] = p[2].replace(", 0.7, 1.4)", ", 0.7, %s)" % TOPE_ZOOM).replace(", 0.7, %s)" % TOPE_ZOOM, ", 0.7, %s)" % TOPE_ZOOM); n_z += 1
                assert p[2].endswith(", 0.7, %s)" % TOPE_ZOOM), p[2]
    assert n_z == 1, n_z

    # ---- a) escala del efecto del Especial (junto al evento que borra los EfectoPj)
    n_e = 0
    def tiene_vida(e):
        return any(c["type"]["value"] == "CompareObjectTimer" and c["parameters"][0] == "EfectoPj" for c in e.get("conditions", []))
    def procesar(lst):
        nonlocal n_e
        lst[:] = [x for x in lst if not (x.get("conditions") == [NOCLI] and len(x.get("events", [])) == 1 and x["events"][0].get("inlineCode", "").startswith("/*" + MK))]
        k = next((i for i, x in enumerate(lst) if tiene_vida(x)), None)
        if k is not None:
            lst.insert(k, {"type": "BuiltinCommonInstructions::Standard", "conditions": [copy.deepcopy(NOCLI)], "actions": [], "events": [
                {"type": "BuiltinCommonInstructions::JsCode", "inlineCode": CODIGO, "parameterObjects": "EfectoPj", "useStrict": True, "eventsSheetExpanded": False}]})
            n_e += 1
        for x in lst:
            if x.get("events"): procesar(x["events"])
    procesar(J["events"])
    assert n_e == 1, n_e

    # ---- c) imágenes de controles hechas con IA (opcionales): se recorta el margen vacío, se escala SIN deformar a 320 px de alto y se centra
    #         en el hueco de cada panel (izquierda: teclado y ratón, centro x 510; derecha: mando, centro x 1410; y = 190)
    from PIL import Image
    ALTO = 400
    n_i = 0
    for res, obj, fuente, destino, recorte, cx in (("p27_ctl_teclado", "CtlTeclado", "ctl_teclado_ia.png", "p49_ctl_teclado.png", None, 497),
                                                   ("p27_ctl_mando", "CtlMando", "ctl_mando_ia.png", "p49_ctl_mando.png", (0, 215, 1024, 800), 1423)):
        f = os.path.join(IMG, fuente)
        if not os.path.exists(f):
            continue
        im = Image.open(f).convert("RGBA")
        if recorte and im.size == (1024, 1024): im = im.crop(recorte)
        w = round(im.width * ALTO / im.height)
        im.resize((w, ALTO), Image.LANCZOS).save(os.path.join(IMG, destino))
        next(r for r in d["resources"]["resources"] if r["name"] == res)["file"] = "assets/interfaz/" + destino
        for o in d["layouts"][[l["name"] for l in d["layouts"]].index("Juego")]["objects"]:
            pass
        for i in J["instances"]:
            if i["name"] == obj:
                i.update({"x": cx - w // 2, "y": 300, "width": w, "height": ALTO, "customSize": True})
        n_i += 1
    # ---- d) quitar el texto explicativo bajo las imágenes de controles (pausa): las cadenas quedan vacías
    def vaciar(lst):
        n = 0
        for x in lst:
            for a_ in x.get("actions", []):
                p_ = a_.get("parameters", [])
                if a_.get("type", {}).get("value") == "TextObject::String" and p_ and p_[0] in ("TxtPausaCtl1", "TxtPausaCtl2") and p_[2] != '""':
                    p_[2] = '""'; n += 1
            n += vaciar(x.get("events", []))
        return n
    n_t = vaciar(J["events"])
    json.dump(d, open(PRY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("textos vaciados", n_t)
    print("OK fase49 (zoom %d, efecto %d, imágenes de controles %d)" % (n_z, n_e, n_i))


main()
