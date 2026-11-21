"""Fase 48 · Bloque Menores del reporte de pruebas (escena Menu, paso "equipo" = elegir personaje). Idempotente; va después de la fase 47.
 8) Con todos los jugadores ya confirmados la cola de pendientes (Cola) queda en 0 y los clics sobre las celdas se ignoraban.
    Ahora, en ese estado, un clic izquierdo en un personaje libre se lo asigna al Player 1 (el clic en uno ya ocupado no hace nada).
 9) Botón visible "SALIR (ESC)" arriba a la izquierda, solo en el paso de elegir personaje; hace lo mismo que ESC/B (vuelve a "unirse",
    o al tipo de jefe si el modo es Jefe). Brilla al pasar el ratón."""
import copy, datetime, json, os, shutil

AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
STD = "BuiltinCommonInstructions::Standard"
CM = "BuiltinCommonInstructions::Comment"
MK = "FDIZ-FASE48"
BX, BY, BW, BH = 40, 40, 280, 84


def C(t, *p, inv=False): return {"type": {"inverted": inv, "value": t}, "parameters": list(p)}
def A(t, *p): return {"type": {"value": t}, "parameters": list(p)}
def std(cs, acs): return {"type": STD, "conditions": cs, "actions": acs, "events": []}
def cmt(k, n): return {"type": CM, "color": {"b": 109, "g": 230, "r": 255, "textB": 0, "textG": 0, "textR": 0}, "comment": "%s-%s:%d" % (MK, k, n), "comment2": ""}
def en_caja(x0, y0, x1, y1):
    return [C("BuiltinCommonInstructions::CompareNumbers", "MouseX()", ">=", str(x0)), C("BuiltinCommonInstructions::CompareNumbers", "MouseX()", "<", str(x1)),
            C("BuiltinCommonInstructions::CompareNumbers", "MouseY()", ">=", str(y0)), C("BuiltinCommonInstructions::CompareNumbers", "MouseY()", "<", str(y1))]


def quitar(ev):
    i = 0
    while i < len(ev):
        e = ev[i]
        if e.get("type") == CM and e.get("comment", "").startswith(MK + "-"):
            n = int(e["comment"].rsplit(":", 1)[1]); del ev[i:i + 1 + n]
        else:
            i += 1


def main():
    d = json.load(open(PRY, encoding="utf-8"))
    resp = os.path.join(AQUI, "..", "respaldos"); os.makedirs(resp, exist_ok=True)
    bak = os.path.join(resp, "antes_de_fase48_%s.json" % datetime.date.today().strftime("%Y%m%d"))
    if not os.path.exists(bak): shutil.copy(PRY, bak)
    M = next(l for l in d["layouts"] if l["name"] == "Menu")
    ME = M["events"]
    quitar(ME)

    # ---- imagen del botón sin la calavera del botón "difícil": se tapa con el color de fondo del marco
    from PIL import Image, ImageDraw
    ruta = os.path.join(AQUI, "..", "FDI-Z", "assets", "interfaz", "ui_boton_salir_p48.png")
    if not os.path.exists(ruta):
        im = Image.open(os.path.join(AQUI, "..", "FDI-Z", "assets", "interfaz", "ui_boton_dificil_p19.png")).convert("RGBA")
        fondo = im.getpixel((300, 84))
        ImageDraw.Draw(im).rectangle([32, 30, 135, 126], fill=fondo)
        im.save(ruta)
    if not any(r["name"] == "p48_BtnSalir" for r in d["resources"]["resources"]):
        d["resources"]["resources"].append({"file": "assets/interfaz/ui_boton_salir_p48.png", "kind": "image", "metadata": "", "name": "p48_BtnSalir", "smoothed": False, "userAdded": True})

    # ---- objetos e instancias del botón
    dif = next(o for o in M["objects"] if o["name"] == "DifBtn")
    if not any(o["name"] == "BtnSalir" for o in M["objects"]):
        spr = copy.deepcopy(dif); spr["name"] = "BtnSalir"; spr["variables"] = []
        spr["animations"] = [x for x in spr["animations"] if x["name"] == "dificil"]; spr["animations"][0]["name"] = "n"
        M["objects"].append(spr)
        t = copy.deepcopy(next(o for o in M["objects"] if o["name"] == "TxtDif")); t["name"] = "TxtSalir"; t["variables"] = []
        t["string"] = "SALIR (ESC)"; t["content"]["text"] = "SALIR (ESC)"; t["characterSize"] = 30; t["content"]["characterSize"] = 30
        M["objects"].append(t)
    for o in M["objects"]:
        if o["name"] == "BtnSalir": o["animations"][0]["directions"][0]["sprites"][0]["image"] = "p48_BtnSalir"
    for nm, base, x, y, z, w, h in (("BtnSalir", "DifBtn", BX, BY, 8, BW, BH), ("TxtSalir", "TxtDif", BX + BW // 2, BY + BH // 2, 9, None, None)):
        if not any(i["name"] == nm for i in M["instances"]):
            n = copy.deepcopy(next(i for i in M["instances"] if i["name"] == base))
            n.update({"name": nm, "x": x, "y": y, "zOrder": z, "initialVariables": [], "persistentUuid": __import__("uuid").uuid4().hex[:8] + "-0000-4000-8000-" + __import__("uuid").uuid4().hex[:12]})
            if w: n.update({"width": w, "height": h, "customSize": True})
            M["instances"].append(n)

    # ---- 9) botón Salir (eventos al final de la escena)
    paso_eq = C("VarSceneTxt", "Paso", "=", "\"equipo\"")
    boton = [
        std([paso_eq], [A("Montre", "BtnSalir", ""), A("Montre", "TxtSalir", "")]),
        std([C("VarSceneTxt", "Paso", "!=", "\"equipo\"")], [A("Cache", "BtnSalir"), A("Cache", "TxtSalir")]),
        std([], [A("MettreX", "TxtSalir", "=", "%d - TxtSalir.Width() / 2" % (BX + BW // 2)), A("MettreY", "TxtSalir", "=", "%d - TxtSalir.Height() / 2" % (BY + BH // 2))]),
        std([paso_eq] + en_caja(BX, BY, BX + BW, BY + BH), [A("Opacity", "BtnSalir", "=", "255")]),
        std([paso_eq, C("BuiltinCommonInstructions::Or") ] , []),   # (se reemplaza abajo)
    ]
    # brillo: opacidad 200 cuando el ratón no está encima
    fuera = {"type": "BuiltinCommonInstructions::Standard", "conditions": [paso_eq], "actions": [A("Opacity", "BtnSalir", "=", "200")], "events": []}
    boton = [boton[0], boton[1], boton[2], fuera, boton[3]]      # primero 200 y luego 255 si está encima (el último gana)
    clic = lambda extra, acs: std([paso_eq, C("CompareTimer", "", "\"paso\"", ">=", "0.3"), C("MouseButtonReleased", "", "Left")] + en_caja(BX, BY, BX + BW, BY + BH) + extra, acs)
    boton.append(clic([C("VarGlobalTxt", "Modo", "!=", "\"jefe\"")], [A("ModVarSceneTxt", "Paso", "=", "\"unirse\""), A("ResetTimer", "", "\"paso\"")]))
    boton.append(clic([C("VarGlobalTxt", "Modo", "=", "\"jefe\"")], [A("ModVarSceneTxt", "Paso", "=", "\"jefetipo\""), A("ModVarScene", "Sel", "=", "0"), A("ResetTimer", "", "\"paso\"")]))

    # ---- 8) reasignar al Player 1 cuando ya no queda nadie por elegir (Cola = 0)
    celdas = []
    for e in ME:
        cs = e.get("conditions", [])
        if e.get("type") == STD and any(c["type"]["value"] == "MouseButtonReleased" and c["parameters"][1] == "Left" for c in cs) and any(c["type"]["value"] == "VarScene" and c["parameters"][:2] == ["Cola", ">"] for c in cs) \
                and any(x.get("actions") and x["actions"][0]["parameters"][:2] == ["S1Pj", "="] for x in e.get("events", [])):
            k = int(next(x for x in e["events"] if x["actions"][0]["parameters"][0] == "S1Pj")["actions"][0]["parameters"][2])
            celdas.append((k, e))
    assert len(celdas) == 8, len(celdas)
    nuevos = []
    for k, e in sorted(celdas, key=lambda t: t[0]):
        cs = copy.deepcopy(e["conditions"])
        for c in cs:
            if c["type"]["value"] == "VarScene" and c["parameters"][:2] == ["Cola", ">"]: c["parameters"] = ["Cola", "=", "0"]
        nuevos.append(std(cs, [A("ModVarScene", "S1Pj", "=", str(k)), A("ModVarScene", "S1Ok", "=", "1"), A("ModVarScene", "Foco", "=", "1")]))

    # inserción: justo después del último clic derecho de celdas; el botón, al final
    pos = max(i for i, e in enumerate(ME) if any(c["type"]["value"] == "MouseButtonReleased" and c["parameters"][1] == "Right" for c in e.get("conditions", [])) and e.get("events")
              and e["events"][0].get("actions") and e["events"][0]["actions"][0]["parameters"][0] == "S1Ok") + 1
    ME[pos:pos] = [cmt("REASIGNAR", len(nuevos))] + nuevos
    ME.extend([cmt("SALIR", len(boton))] + boton)
    json.dump(d, open(PRY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("OK fase48 (celdas %d, botón %d eventos, insertado en %d)" % (len(nuevos), len(boton), pos))


main()
