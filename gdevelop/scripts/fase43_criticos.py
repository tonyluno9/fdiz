"""Fase 43 · Bloque Críticos del reporte de pruebas de jugabilidad. Idempotente; va al final de la cadena (después de fase42).

Uso (desde la carpeta fdiz, con GDevelop CERRADO):  python3 gdevelop/scripts/fase43_criticos.py
Qué hace en FDI-Z.json:
  1) Conserje (y demás zombis) atravesaba puertas: el cuadro 'atacar_arriba' de ZNormal, ZCorredor, ZGriton, ZGordo y
     ZConserje no tenía máscara de colisión (usaba todo el sprite, 14 px más alto) y SeparateFromObjects lo empujaba
     al otro lado de la puerta. Se le pone la misma máscara de pies que a los demás cuadros. Red de seguridad:
     criticos.js -> puertas() devuelve al zombi a su última posición si cambia de lado de una puerta cerrada.
  2) Aliados atorados: criticos.js -> desatasco() (paso lateral, salir de celda bloqueada, salto corto por la ruta,
     reaparecer junto a un humano).
  4) Golpes de zombis a través de puertas: además de las 7 muestras de la línea de vista del evento original, se añade un
     veto exacto (criticos.js -> golpe()): si el segmento zombi→objetivo toca una puerta (con 10 px de margen) o un muro,
     no hay daño.
  5) Pasos angostos que A* cerraba (entrada al pasillo de la conserjería y otros 9): criticos.js -> abrirPasos().
  6) Ojo de oferta de Alan: criticos.js -> ojo() (6 s, vuelve a oscurecer 100 %, enfriamiento 30 s, alcance por borde).
  7) Los bots corren solos con estamina (scripts/correr.js; correr esta fase DESPUÉS de fase42).
  3) Oscuridad inicial: se despeja al pasar el borde del salón (margen 8 px en vez de 80), o en cuanto se rompe su
     puerta (P03 o P06), y se desvanece más rápido (450/s en vez de 200/s).
"""
import copy, datetime, json, os, re, shutil

AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
MK = "FDIZ-FASE43"
NOCLI = {"type": {"inverted": False, "value": "VarGlobal"}, "parameters": ["NetRol", "!=", "2"]}
ZOMBIS = ["ZNormal", "ZCorredor", "ZGriton", "ZGordo", "ZConserje"]


def js(code, marca):
    return {"type": "BuiltinCommonInstructions::JsCode", "inlineCode": "/*" + marca + "*/\n" + code,
            "parameterObjects": "", "useStrict": True, "eventsSheetExpanded": False}


def std(conds, acts, sub=()):
    return {"type": "BuiltinCommonInstructions::Standard", "conditions": conds, "actions": acts, "events": list(sub)}


def recorrer(lst):
    for e in lst:
        yield e
        yield from recorrer(e.get("events", []))


def tiene_marca(e, marca):
    return any(x.get("type", "").endswith("JsCode") and x.get("inlineCode", "").startswith("/*" + marca)
               for x in recorrer([e]))


def quitar(lst, marca):
    lst[:] = [e for e in lst if not (tiene_marca(e, marca) and len(list(recorrer([e]))) <= 2)]


def grupo(ev, prefijo):
    return next(e for e in ev if e["type"].endswith("Group") and e.get("name", "").startswith(prefijo))


def main():
    d = json.load(open(PRY, encoding="utf-8"))
    resp = os.path.join(AQUI, "..", "respaldos")
    os.makedirs(resp, exist_ok=True)
    bak = os.path.join(resp, "antes_de_fase43_%s.json" % datetime.date.today().strftime("%Y%m%d"))
    if not os.path.exists(bak):
        shutil.copy(PRY, bak)
    J = next(l for l in d["layouts"] if l["name"] == "Juego")
    ob = {o["name"]: o for o in J["objects"]}

    # ---- 1) máscara de atacar_arriba
    for n in ZOMBIS:
        anims = {a["name"]: a for a in ob[n]["animations"]}
        ref = anims["caminar_abajo"]["directions"][0]["sprites"][0]
        ata = anims["atacar_arriba"]["directions"][0]["sprites"]
        for f in ata:
            dx = f["originPoint"]["x"] - ref["originPoint"]["x"]
            dy = f["originPoint"]["y"] - ref["originPoint"]["y"]
            f["hasCustomCollisionMask"] = True
            f["customCollisionMask"] = [[{"x": p["x"] + dx, "y": p["y"] + dy} for p in poly] for poly in ref["customCollisionMask"]]

    ev = J["events"]
    # ---- módulo
    quitar(ev, MK + "-MOD")
    ev.insert(0, js(open(os.path.join(AQUI, "criticos.js"), encoding="utf-8").read(), MK + "-MOD"))

    # ---- red de seguridad de puertas: justo después de separar a los zombis de los sólidos
    gz = grupo(ev, "Zombies: IA, ataque y muerte")["events"]
    quitar(gz, MK + "-PUERTAS")
    k = next(i for i, e in enumerate(gz) if any(a["type"]["value"] == "SeparateFromObjects" and a["parameters"][:2] == ["Zombies", "Solidos"] for a in e.get("actions", [])))
    gz.insert(k + 1, std([copy.deepcopy(NOCLI)], [], [js("if (gdjs.fdizCriticos) gdjs.fdizCriticos.puertas(runtimeScene);", MK + "-PUERTAS")]))

    # ---- desatasco: al final de los grupos de bots (antes de aplicar el movimiento)
    gb = grupo(ev, "Bots: curar mordidos")["events"]
    quitar(gb, MK + "-DESATASCO")
    gb.append(std([copy.deepcopy(NOCLI)], [], [js("if (gdjs.fdizCriticos) gdjs.fdizCriticos.desatasco(runtimeScene);", MK + "-DESATASCO")]))

    # ---- ataque de zombis: veto exacto de puertas y muros justo antes del evento que quita vida
    for e in recorrer(gz):
        if e.get("type", "").endswith("ForEach") and e.get("object") == "Zombies" and \
                [c["parameters"][1] for c in e["conditions"][:2]] == ['Estado', '"ataque"']:
            sub = next(x for x in e["events"] if x.get("conditions") and x["conditions"][0]["parameters"][:1] == ["Sup"])
            quitar(sub["events"], MK + "-GOLPE")
            kd = next(i for i, x in enumerate(sub["events"]) if any(a2["type"]["value"] == "ModVarObjet" and a2["parameters"][:2] == ["Sup", "Vida"] for a2 in x.get("actions", [])))
            veto = js("if (gdjs.fdizCriticos) gdjs.fdizCriticos.golpe(runtimeScene, objects);", MK + "-GOLPE")
            veto["parameterObjects"] = "Zombies"
            sub["events"].insert(kd, std([copy.deepcopy(NOCLI)], [], [veto]))
            break
    else:
        raise SystemExit("no encontré el evento de ataque de zombis")

    # ---- Ojo de oferta: el efecto pasa a JS (6 s, vuelve a oscurecer, enfría 30 s); la activación queda como estaba
    gp = grupo(ev, "Pasivas: Ojo de oferta")["events"]
    ko = None if any(tiene_marca(e, MK + "-OJO") for e in gp) else next((i for i, e in enumerate(gp) if e.get("type", "").endswith("Standard") and
               any(c["type"]["value"] == "VarObjet" and c["parameters"][:3] == ["Sup", "Ojo", "="] and c["parameters"][3] == "1" for x in [e] for c in x.get("conditions", []) + [cc for s2 in x.get("events", []) for cc in s2.get("conditions", [])])
               and not any(x2.get("type", "").endswith("JsCode") for x2 in e.get("events", []))), None)
    if ko is not None:
        gp[ko] = std([copy.deepcopy(NOCLI)], [], [js("if (gdjs.fdizCriticos) gdjs.fdizCriticos.ojo(runtimeScene);", MK + "-OJO")])
    else:
        assert any(tiene_marca(e, MK + "-OJO") for e in gp), "no encontré el efecto del Ojo"

    # ---- oscuridad inicial
    go = grupo(ev, "Oscuridad inicial")["events"]
    quitar(go, MK + "-OSC")  # (por si acaso)
    go[:] = [e for e in go if not (e.get("type", "").endswith("Standard") and any(
        c["type"]["value"] == "VarScene" and c["parameters"][:1] == ["OscX"] for c in e.get("conditions", [])) and e.get("actions") and e["actions"][0]["parameters"][:3] == ["OscIni", "=", "0"])]
    n_m = 0
    for e in recorrer(go):
        for c in e.get("conditions", []):
            for s in c.get("subInstructions", []):
                p = s["parameters"]
                if len(p) == 3 and re.search(r"Variable\(Osc[XY]\)(?: \+ Variable\(Osc[WH]\))? [-+] \d+$", p[2]):
                    p[2] = re.sub(r"(?<=[-+] )\d+$", "8", p[2]); n_m += 1
        for a in e.get("actions", []):
            if a["type"]["value"] == "Opacity" and a["parameters"][:2] == ["OscuridadIni", "-"]:
                a["parameters"][3 - 1 + 0] = "450 * TimeDelta()" if len(a["parameters"]) == 3 else a["parameters"][2]
    assert n_m == 4, n_m
    ik = next(i for i, e in enumerate(go) if any(x.get("type", "").endswith("ForEach") for x in e.get("events", [])))
    nuevos = []
    for oscx, puerta in ((4928, "P03"), (5792, "P06")):
        nuevos.append(std([copy.deepcopy(NOCLI),
                           {"type": {"inverted": False, "value": "VarScene"}, "parameters": ["OscIni", "=", "1"]},
                           {"type": {"inverted": False, "value": "VarScene"}, "parameters": ["OscX", "=", str(oscx)]},
                           {"type": {"inverted": False, "value": "VarSceneTxt"}, "parameters": ["Estado", "=", '"juego"']},
                           {"type": {"inverted": True, "value": "VarObjetTxt"}, "parameters": ["Puerta", "Id", "=", '"%s"' % puerta]}],
                          [{"type": {"value": "ModVarScene"}, "parameters": ["OscIni", "=", "0"]}]))
    go[ik + 1:ik + 1] = nuevos
    json.dump(d, open(PRY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("OK fase43")


main()
