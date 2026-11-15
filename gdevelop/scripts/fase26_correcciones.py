"""Aplica las correcciones sobre el proyecto de la fase 25.

Uso: python gdevelop/scripts/fase26_correcciones.py [ruta/a/FDI-Z.json]
"""

import json
from pathlib import Path
import sys

from gd_util import a, c, capa, ev


def tipo(instruccion):
    return instruccion["type"]["value"]


def temporizador(nombre, segundos):
    return c("CompareTimer", "", f'"{nombre}"', ">=", str(segundos))


def comparar(izq, operador, der):
    return c("BuiltinCommonInstructions::CompareNumbers", izq, operador, der)


def recorrer(eventos):
    for evento in eventos:
        yield evento
        yield from recorrer(evento.get("events", []))


def corregir_intro(grupos):
    intro = grupos["Cinemática de inicio"]["events"]
    en_intro = c("VarSceneTxt", "Estado", "=", '"intro"')
    durante_juego = c("VarSceneTxt", "Estado", "!=", '"intro"')
    if durante_juego in grupos["Zombies: IA, ataque y muerte"]["events"][0].get("conditions", []):
        return

    # Mientras dura la escena, solo se mueve la pareja de zombis dirigida por el guion.
    for evento in grupos["Zombies: IA, ataque y muerte"]["events"]:
        if "conditions" in evento:
            evento["conditions"].append(durante_juego)

    fin = next(e for e in intro if any(x["parameters"] == ["Estado", "=", '"juego"']
                                    for x in e.get("actions", [])))
    ataque = next(e for e in intro if any(x["parameters"] == ["IntroPuerta", "=", "1"]
                                       for x in e.get("actions", [])))
    puerta = c("VarObjetTxt", "Puerta", "Id", "=", '"P06"')
    romper = ataque["events"][0]
    romper["conditions"] = [puerta]
    centro_puerta = "Puerta.Y() + Puerta.Height() / 2"
    romper["events"] = [ev([
        c("VarObjetTxt", "ZNormal", "Estado", "=", '"cinematica"'),
        c("PickNearest", "ZNormal", "Puerta.X()", centro_puerta, ""),
    ], [a("MettreXY", "ZNormal", "=", "Puerta.X() + Puerta.Width() + 18", "=", centro_puerta)])]

    # El jugador recupera el control en el mismo cuadro en que se rompe la puerta.
    # Se mantiene la indicación de la regla durante los primeros segundos jugables.
    reloj = temporizador("intro", 19)
    siguiente = temporizador("intro", 21)
    def a_los_21(e):
        return any(tipo(x) == "CompareTimer" and x["parameters"] == siguiente["parameters"]
                   for x in e.get("conditions", []))

    tutorial = next(e for e in intro if a_los_21(e) and
                    any(x["parameters"][:1] == ["TxtDialogo"] for x in e["actions"]))
    intro[:] = [e for e in intro if not a_los_21(e)]
    fin["conditions"][-1]["subInstructions"].append(reloj)
    limpiar = a("TextObject::String", "TxtDialogo", "=", '""')
    fin["actions"].remove(limpiar)
    sin_ataque = c("VarScene", "IntroPuerta", "=", "0")
    con_ataque = c("VarScene", "IntroPuerta", "=", "1")
    fin["events"].append(ev([sin_ataque], [limpiar], sub=[
        ev([puerta], [a("ChangeColor", "Puerta", '"255;255;255"')]),
        ev([c("VarObjetTxt", "ZNormal", "Estado", "=", '"cinematica"')],
           [a("Delete", "ZNormal", "")]),
    ]))
    tutorial["conditions"] = [x for x in tutorial["conditions"] if x["parameters"] != en_intro["parameters"]]
    tutorial["conditions"].insert(0, con_ataque)
    intro.extend([tutorial, ev([con_ataque, temporizador("intro", 26),
                               c("BuiltinCommonInstructions::Once")], [limpiar])])
    intro[0]["comment"] = ("En B-01, los zombis esperan afuera durante el diálogo y rompen la puerta al final. "
                           "El equipo recupera el control en ese momento. La intro se puede omitir.")


def corregir_resultados(resultados):
    destinos = {'"Juego"': None, '"Titulo"': "BtnMenuR"}
    for evento in resultados["events"]:
        acciones = evento.get("actions", [])
        if len(acciones) != 1 or tipo(acciones[0]) != "Scene":
            continue
        destino = acciones[0]["parameters"][1]
        local = next((n for n in destinos if destino ==
                      f'if(GlobalVariable(NetRol) > 0, "Online", {n})'), None)
        if local is None:
            continue

        condiciones = evento["conditions"]
        derrota = any(x["parameters"] == ["Resultado", "!=", '"victoria"'] for x in condiciones)
        if derrota and any(tipo(x) == "MouseButtonReleased" for x in condiciones):
            boton = destinos[local] or "BtnRei"
            condiciones[:] = [x for x in condiciones if tipo(x) != "BuiltinCommonInstructions::CompareNumbers"]
            # Las coordenadas coinciden con la posición y el tamaño de la instancia.
            for eje, alto_ancho in (("X", "Width"), ("Y", "Height")):
                cursor = f'Cursor{eje}("", 0)'
                origen = f"{boton}.{eje}()"
                condiciones.extend([
                    comparar(cursor, ">=", origen),
                    comparar(cursor, "<", f"{origen} + {boton}.{alto_ancho}()"),
                ])
        if derrota and local == '"Titulo"':
            local = '"Menu"'
        evento["actions"] = []
        evento["events"] = [
            ev([c("VarGlobal", "NetRol", "=", "0")], [a("Scene", "", local, "")]),
            ev([c("VarGlobal", "NetRol", ">", "0")], [a("Scene", "", '"Online"', "")]),
        ]


def esperar_bots(grupos):
    intro = grupos["Cinemática de inicio"]["events"]
    devolver_control = a("ModVarObjet", "Sup", "Control", "=", "Sup.Variable(CtlReal)")
    fin = next(e for e in intro if a("ModVarSceneTxt", "Estado", "=", '"juego"') in e.get("actions", []))
    devolver_humanos = next(e for e in fin["events"] if devolver_control in e["actions"])
    solo_humanos = c("VarObjet", "Sup", "CtlReal", "!=", "-1")
    if solo_humanos in devolver_humanos["conditions"]:
        return
    devolver_humanos["conditions"].append(solo_humanos)
    bot_en_espera = c("VarObjet", "Sup", "Control", "=", "-2")
    era_bot = c("VarObjet", "Sup", "CtlReal", "=", "-1")
    en_partida = c("VarSceneTxt", "Estado", "=", '"juego"')
    intro.append(ev([en_partida, temporizador("partida", 6), bot_en_espera, era_bot], [devolver_control]))

    # El control -2 deja al bot en reposo sin cambiar los controles humanos.
    # Un mando puede tomar su lugar y el HUD sigue identificándolo como bot.
    for nombre in ("Unirse con control", "HUD", "Interfaz: HUD con paneles"):
        for evento in recorrer(grupos[nombre]["events"]):
            for i, condicion in enumerate(evento.get("conditions", [])):
                if tipo(condicion) == "VarObjet" and condicion["parameters"] == ["Sup", "Control", "=", "-1"]:
                    evento["conditions"][i] = {
                        **c("BuiltinCommonInstructions::Or"),
                        "subInstructions": [condicion, {
                            **c("BuiltinCommonInstructions::And"),
                            "subInstructions": [en_partida, bot_en_espera, era_bot],
                        }],
                    }


def corregir_niebla(juego, grupos):
    # Retira los bloques y eventos de la primera versión de esta corrección.
    juego["objects"][:] = [o for o in juego["objects"] if o["name"] != "BloqueNiebla"]
    juego["instances"][:] = [i for i in juego["instances"] if i["name"] != "BloqueNiebla"]
    carpeta = juego["objectsFolderStructure"]["children"]
    carpeta[:] = [o for o in carpeta if o.get("itemName") != "BloqueNiebla"]
    choques = grupos["Mapa: choques y puertas"]["events"]
    choques[:] = [e for e in choques if a("Cache", "BloqueNiebla") not in e.get("actions", [])]
    for e in choques:
        if "events" in e:
            e["events"][:] = [hijo for hijo in e["events"]
                              if a("SeparateFromObjects", "Sup", "BloqueNiebla", "") not in hijo.get("actions", [])]

    for evento in grupos["Niebla por zonas"]["events"]:
        if evento.get("object") == "Niebla" and any(
                a("Delete", "BloqueNiebla", "") in hijo["actions"] for hijo in evento.get("events", [])):
            evento.update(ev(evento["conditions"], [a("Delete", "Niebla", "")]))
            del evento["object"], evento["events"]

    if any(l["name"] == "NieblaSalas" for l in juego["layers"]):
        return
    indice = next(i for i, l in enumerate(juego["layers"]) if l["name"] == "Niebla")
    juego["layers"][indice:indice] = [capa("NieblaSalas"), capa("SupervivientesBorde")]
    for instancia in juego["instances"]:
        if instancia["name"] == "Niebla":
            instancia["layer"] = "NieblaSalas"
    for evento in recorrer(juego["events"]):
        for accion in tuple(evento.get("actions", [])):
            if tipo(accion) in ("ShowLayer", "HideLayer") and accion["parameters"] == ["", '"Niebla"']:
                evento["actions"].append(a(tipo(accion), "", '"NieblaSalas"'))

    # Los objetos de las salas quedan debajo de la niebla. Solo se eleva el sprite
    # del superviviente que se proyecta sobre ella con los pies todavía fuera.
    codigo = (Path(__file__).with_name("niebla_borde.js")).read_text(encoding="utf-8")
    juego["events"].append({
        "type": "BuiltinCommonInstructions::JsCode",
        "inlineCode": codigo,
        "parameterObjects": "",
        "useStrict": True,
        "eventsSheetExpanded": False,
    })


def corregir_colisiones(juego, grupos):
    if any(e.get("inlineCode", "").startswith("/* FDIZ-FASE27 */") for e in juego["events"]):
        return
    objetos = {o["name"]: o for o in juego["objects"]}

    mascaras = {
        "servidor": (5, 32, 43, 63),
        "computadora": (2, 14, 29, 31),
        "interruptor": (2, 19, 22, 39),
        "locker": (1, 25, 18, 47),
        "mochila": (6, 23, 36, 47),
        "maquina": (1, 23, 27, 47),
    }
    for nombre in ("Objetivo", "Contenedor"):
        for animacion in objetos[nombre]["animations"]:
            base = animacion["name"].split("_")[0]
            rect = mascaras.get(base)
            mascara = []
            if rect:
                x0, y0, x1, y1 = rect
                mascara = [[{"x": x, "y": y} for x, y in
                            ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]]
            for direccion in animacion["directions"]:
                for sprite in direccion["sprites"]:
                    sprite.update(hasCustomCollisionMask=True, customCollisionMask=mascara)

    # El mostrador del CIC solo tenía una franja sólida en la parte inferior.
    mostrador = next((i for i in juego["instances"] if i["name"] == "ChoqueMueble"
                      and (i["x"], i["y"], i["width"], i["height"]) == (3091, 1848, 250, 56)), None)
    if mostrador:
        mostrador.update(y=1772, height=132)

    choques = grupos["Mapa: choques y puertas"]["events"]
    evento = next(e for e in choques if any(x["parameters"] == ["Sup", "Solidos", ""]
                                          for x in e.get("actions", [])))
    choques_objetos = [a("SeparateFromObjects", "Sup", objeto, "") for objeto in ("Objetivo", "Contenedor")]
    evento["actions"][:0] = [accion for accion in choques_objetos if accion not in evento["actions"]]


def main():
    ruta = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "FDI-Z/FDI-Z.json"
    proyecto = json.loads(ruta.read_text(encoding="utf-8"))
    escenas = {e["name"]: e for e in proyecto["layouts"]}
    juego = escenas["Juego"]
    grupos = {e["name"]: e for e in juego["events"] if e["type"].endswith("::Group")}
    corregir_intro(grupos)
    esperar_bots(grupos)
    corregir_resultados(escenas["Resultados"])
    corregir_colisiones(juego, grupos)
    corregir_niebla(juego, grupos)
    ruta.write_text(json.dumps(proyecto, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
