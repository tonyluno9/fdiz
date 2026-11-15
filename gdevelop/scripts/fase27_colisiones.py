"""Ajusta el mobiliario de la nevería, SITE y las salas de cómputo.

Aplicar sobre el proyecto de la fase 26 con GDevelop cerrado o recargar después.
Uso: python gdevelop/scripts/fase27_colisiones.py
"""

import json
from pathlib import Path

from gd_util import a, c, ev, instancia


RAIZ = Path(__file__).resolve().parents[2]
RUTA_PROYECTO = RAIZ / "gdevelop/FDI-Z/FDI-Z.json"
RUTA_PROPS = RAIZ / "mapa/final/mapa_fdiz_props.json"
MARCA = "/* FDIZ-FASE27 */\n"


def codigo_separacion():
    return MARCA + Path(__file__).with_name("separar_supervivientes.js").read_text(encoding="utf-8")


def valor(objeto, nombre):
    return next((v["value"] for v in objeto["initialVariables"] if v["name"] == nombre), None)


def recorrer(eventos):
    for evento in eventos:
        yield evento
        yield from recorrer(evento.get("events", []))


def rect(x, y, w, h):
    return dict(x=x, y=y, w=w, h=h)


def actualizar_muebles(juego, props):
    muebles = {(valor(i, "Sprite"), i["x"], i["y"]): i for i in juego["instances"] if i["name"] == "Mueble"}
    choques = {(i["x"], i["y"], i["width"], i["height"]): i
               for i in juego["instances"] if i["name"] == "ChoqueMueble"}

    def colocar(prop, colision, x=None, y=None, z=None):
        mueble = muebles.get((prop["sprite"], prop["x"], prop["y"]))
        previo = prop["colision"]
        if x is not None:
            prop["x"], prop["y"] = x, y
        if mueble:
            mueble.update(x=prop["x"], y=prop["y"], zOrder=prop["y"] if z is None else z)
        if z is not None:
            prop["zOrder"] = z
        if colision is not None:
            nuevo = (colision["x"], colision["y"], colision["w"], colision["h"])
            anterior = tuple(previo[k] for k in ("x", "y", "w", "h")) if previo else nuevo
            choque = choques.get(anterior) or choques.get(nuevo)
            if choque:
                choque.update(x=nuevo[0], y=nuevo[1], width=nuevo[2], height=nuevo[3])
            else:
                juego["instances"].append(instancia("ChoqueMueble", nuevo[0], nuevo[1], "Juego",
                                                    w=nuevo[2], h=nuevo[3]))
        prop["colision"] = colision

    maquinas = []
    for prop in props:
        sprite = prop["sprite"]
        x, y = prop["x"], prop["y"]
        if sprite == "neveria/refri_refresco":
            colocar(prop, rect(x - 29, y - 51, 58, 51))
            maquinas.append(muebles[(sprite, x, y)])
        elif sprite == "neveria/congelador_helados" and y > 1440:
            colocar(prop, rect(1900, 1509, 80, 35), x=1940, y=1544)
        elif sprite == "extra/neveria__menu_pared_h72":
            colocar(prop, None, x=1840, y=1498)
        elif sprite == "extra/extra__neveria__barra_L_espejo":
            colocar(prop, rect(1580, 1568, 320, 59), z=1627)
        elif sprite == "colision" and (prop["colision"]["x"], prop["colision"]["y"]) in ((1870, 1568), (1869, 1627)):
            colocar(prop, rect(1869, 1627, 31, 149))
        elif sprite == "neveria/caja_registradora" and y == 1586:
            colocar(prop, None, z=1628)
        elif sprite == "site/cables_piso":
            colocar(prop, rect(3509, 1564, 54, 26), x=3536, y=1590)
        elif sprite == "site/ups":
            colocar(prop, rect(x - 21, y - 34, 42, 34))
        elif sprite in ("laboratorio/pc_frente", "laboratorio/pc_espalda", "laboratorio/mesa_maestro_lab"):
            profundidad = 44 if sprite == "laboratorio/mesa_maestro_lab" else 40
            colocar(prop, rect(x - prop["w"] // 2, y - profundidad, prop["w"], profundidad))
    return maquinas


def ajustar_maquinas(juego, grupo, maquinas):
    # La máquina de compra usa el mismo arte y la misma posición que el mueble
    # anterior. ChoqueMueble conserva su huella también para la navegación A*.
    objetos = {o["name"]: o for o in juego["objects"]}
    refri = next(anim for anim in objetos["Mueble"]["animations"] if anim["name"] == "neveria/refri_refresco")
    for anim in objetos["Contenedor"]["animations"]:
        if anim["name"].startswith("maquina_"):
            for direccion in anim["directions"]:
                for frame in direccion["sprites"]:
                    frame.update(refri["directions"][0]["sprites"][0],
                                 hasCustomCollisionMask=True, customCollisionMask=[])

    for indice, mueble in enumerate(maquinas, 1):
        x, y = mueble["x"], mueble["y"]
        for i in juego["instances"]:
            if i["name"] == "Contenedor" and valor(i, "Vende") == indice:
                i.update(x=x, y=y, zOrder=y)
            elif i["name"] == "TxtPrecio" and valor(i, "Vende") == indice:
                i.update(x=x - 60, y=y - 136, zOrder=y + 1)
        juego["instances"].remove(mueble)

    # Después de mover las máquinas atrás de la barra, entregar al comprador
    # evita que la mercancía aparezca dentro del mostrador o tras un mueble.
    for e in recorrer(grupo["events"]):
        for accion in e.get("actions", []):
            p = accion["parameters"]
            if accion["type"]["value"] == "Create" and p[2:4] == ["Contenedor.X() + 30", "Contenedor.Y() + 50"]:
                p[2:4] = ["Sup.X()", "Sup.Y()"]


def ajustar_juego(juego):
    grupos = {e["name"]: e for e in juego["events"] if e["type"].endswith("::Group")}
    objetivos = grupos["Objetivos y flecha"]["events"]
    for e in recorrer(objetivos):
        acciones = e.get("actions", [])
        if a("SetAnimationName", "Objetivo", '"servidor"') in acciones:
            crear = next(x for x in acciones if x["type"]["value"] == "Create" and x["parameters"][1] == "Objetivo")
            crear["parameters"][3] = "1476"
    objetivos.append(ev([c("VarGlobal", "NetRol", "!=", "2"),
                         c("VarObjetTxt", "Objetivo", "Tipo", "=", '"servidor"')],
                        [a("ChangePlan", "Objetivo", "=", "Objetivo.Y()")]))
    objeto = next(o for o in juego["objects"] if o["name"] == "Objetivo")
    servidor = next(anim for anim in objeto["animations"] if anim["name"] == "servidor")
    for d in servidor["directions"]:
        for sprite in d["sprites"]:
            sprite["customCollisionMask"] = [[dict(x=x, y=y) for x, y in
                                               ((4, 20), (45, 20), (45, 64), (4, 64))]]

    choques = grupos["Mapa: choques y puertas"]["events"]
    choques[:] = [e for e in choques if a("SeparateFromObjects", "Sup", "Sup", "") not in e.get("actions", [])]
    # Aplicar una última separación del escenario después del empuje de zombis,
    # y luego resolver la separación entre jugadores sin empujarlos a un sólido.
    indice = next(i for i, e in enumerate(juego["events"])
                  if e.get("inlineCode", "").startswith("/*FDIZ-FASE25-END"))
    juego["events"][indice:indice] = [
        ev([c("VarGlobal", "NetRol", "!=", "2")],
           [a("SeparateFromObjects", "Sup", nombre, "") for nombre in ("Objetivo", "Contenedor", "Solidos")]),
        {"type": "BuiltinCommonInstructions::JsCode",
         "inlineCode": codigo_separacion(),
         "parameterObjects": "", "useStrict": True, "eventsSheetExpanded": False},
    ]
    return grupos


def main():
    proyecto = json.loads(RUTA_PROYECTO.read_text(encoding="utf-8"))
    juego = next(l for l in proyecto["layouts"] if l["name"] == "Juego")
    aplicado = next((e for e in juego["events"] if e.get("inlineCode", "").startswith(MARCA)), None)
    if aplicado is not None:
        if aplicado["inlineCode"] != codigo_separacion():
            aplicado["inlineCode"] = codigo_separacion()
            RUTA_PROYECTO.write_text(json.dumps(proyecto, ensure_ascii=False, indent=2), encoding="utf-8")
        return
    mapa = json.loads(RUTA_PROPS.read_text(encoding="utf-8"))
    maquinas = actualizar_muebles(juego, mapa["props"])
    grupos = ajustar_juego(juego)
    ajustar_maquinas(juego, grupos["Lockers, mochilas, máquinas y dinero"], maquinas)
    RUTA_PROPS.write_text(json.dumps(mapa, ensure_ascii=False, indent=0), encoding="utf-8")
    RUTA_PROYECTO.write_text(json.dumps(proyecto, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
