"""Pruebas del modo Historia sin GDevelop:  python gdevelop/scripts/prueba_historia.py [proyecto.json]

Interpreta los eventos REALES de los grupos "Objetivos y flecha" y "Final ¡Aguanten!" del proyecto (un subconjunto de
GDevelop: variables, comparaciones, Trigger once, ForEach, Crear/Borrar, selección de objetos por variable) y simula a
los jugadores completando cada objetivo. Los jugadores (Sup) no existen: las acciones de usar / recoger se simulan
marcando el objetivo como hecho o el bidón / la bolsa como tocados.
Compara también Escape contra el respaldo anterior a la fase 43 (mismos números al azar -> mismo resultado).
"""
import glob, json, math, os, random, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
DT = 1 / 60

ZONAS_CIC = [(2688, 1632, 2944, 1888), (2976, 1632, 3456, 2080), (3488, 1632, 3744, 1888)]   # Pasillo oeste, CIC, Pasillo este
NEVERIA = (1536, 1440, 1984, 2432)


def dentro(z, x, y):
    return z[0] <= x < z[2] and z[1] <= y < z[3]


class Inst:
    def __init__(self, nombre, x, y):
        self.n, self.x, self.y, self.v, self.tocado = nombre, x, y, {}, False


class Sim:
    def __init__(self, layouts, modo, semilla):
        J = next(l for l in layouts if l["name"] == "Juego")
        self.ev = [g for g in J["events"] if g.get("name") in ("Objetivos y flecha", "Final ¡Aguanten!")]
        self.V = {v["name"]: v["value"] for v in J["variables"]}
        self.V["Estado"] = "juego"
        self.G = {"NetRol": 0, "Modo": modo, "SonidoActivo": 1}
        self.T = {"TxtObjetivo": "", "TxtAyuda": ""}
        sup = Inst("Sup", 0, 0)             # un jugador virtual de pie (lejos de todo: las distancias no se cumplen solas)
        sup.v.update({"Estado": "normal", "Jugador": 1, "Usando": 0, "Personaje": "tony", "Control": 0})
        self.objs = [sup]                   # instancias vivas
        self.timers = {}
        self.t = 0.0
        self.primero = True
        self.once = {}
        self.rnd = random.Random(semilla)
        self.sonidos, self.creados, self.letreros, self.charlas = [], [], [], []

    # ---------------- expresiones
    CACHE = {}

    def ev_expr(self, s, pick):
        code = Sim.CACHE.get(s)
        if code is None:
            code = Sim.CACHE[s] = compile(self.traducir(s), "<expr>", "eval")
        return self.evaluar(code, s, pick)

    def traducir(self, s):
        py = s
        py = py.replace("NewLine()", '"\\n"').replace("TimeDelta()", "DT")
        py = re.sub(r"GlobalVariableString\((\w+)\)", r'GS("\1")', py)
        py = re.sub(r"GlobalVariable\((\w+)\)", r'GN("\1")', py)
        py = re.sub(r"VariableString\((\w+)\)", r'SS("\1")', py)
        py = re.sub(r"(\w+)\.VariableString\((\w+)\)", r'OS("\1","\2")', py)
        py = re.sub(r"(\w+)\.Variable\((\w+)\)", r'OV("\1","\2")', py)
        py = re.sub(r"(?<![\w.])Variable\((\w+)\)", r'SN("\1")', py)
        py = re.sub(r"(\w+)\.String\(\)", r'TX("\1")', py)
        py = re.sub(r"(\w+)\.(X|Y)\(\)", r'OXY("\1","\2")', py)
        py = re.sub(r"PickedInstancesCount\((\w+)\)", r'PC("\1")', py)
        py = re.sub(r'TimerElapsedTime\("(\w+)"\)', r'TM("\1")', py)
        py = py.replace("ToString(", "TS(").replace("RandomInRange(", "RR(").replace("mod(", "MOD(")
        return py

    def evaluar(self, code, s, pick):
        def first(n):
            l = pick.get(n, [])
            return l[0] if l else None
        env = {
            "DT": DT, "TS": lambda x: (str(int(x)) if float(x) == int(x) else str(x)), "RR": lambda a, b: self.rnd.randint(int(a), int(b)),
            "MOD": lambda a, b: a % b, "max": max, "min": min, "ceil": math.ceil, "round": round, "floor": math.floor,
            "SN": lambda n: float(self.V.get(n, 0) or 0), "SS": lambda n: str(self.V.get(n, "")),
            "GN": lambda n: float(self.G.get(n, 0)), "GS": lambda n: str(self.G.get(n, "")),
            "OV": lambda o, n: float((first(o).v.get(n, 0) if first(o) else 0) or 0),
            "OS": lambda o, n: str(first(o).v.get(n, "") if first(o) else ""),
            "TX": lambda n: self.T.get(n, ""), "OXY": lambda o, k: (getattr(first(o), k.lower()) if first(o) else 0),
            "PC": lambda o: len(pick.get(o, [])), "TM": lambda n: self.t - self.timers.get(n, 0),
            "CameraBorderLeft": lambda *a: 0, "CameraBorderRight": lambda *a: 9999, "CameraBorderTop": lambda *a: 0,
            "CameraBorderBottom": lambda *a: 9999, "CameraX": lambda *a: 0, "CameraY": lambda *a: 0, "SceneInstancesCount": lambda *a: 0,
            "DistanceBetweenPositions": lambda x1, y1, x2, y2: math.hypot(x1 - x2, y1 - y2), "Zombies": None, "Sup": None,
        }
        try:
            return eval(code, {"__builtins__": {}}, env)
        except Exception as e:
            raise RuntimeError("expresión %r: %s" % (s, e))

    # ---------------- condiciones
    def cmp(self, a, op, b):
        return {"=": a == b, "!=": a != b, "<": a < b, ">": a > b, "<=": a <= b, ">=": a >= b}[op]

    def num(self, s, pick):
        return float(self.ev_expr(s, pick))

    def cond(self, c, pick, eid):
        t, p, inv = c["type"]["value"], c["parameters"], c["type"].get("inverted", False)
        r = self.cond2(t, p, pick, eid, c)
        return (not r) if inv else r

    def filtra(self, pick, nombre, f):
        base = pick.get(nombre)
        if base is None:
            base = [o for o in self.objs if o.n == nombre or (nombre == "Zombies" and False)]
        sel = [o for o in base if f(o)]
        pick[nombre] = sel
        return bool(sel)

    def cond2(self, t, p, pick, eid, c):
        if t == "VarGlobal":
            return self.cmp(float(self.G.get(p[0], 0)), p[1], self.num(p[2], pick))
        if t == "VarGlobalTxt":
            return self.cmp(str(self.G.get(p[0], "")), p[1], self.ev_expr(p[2], pick))
        if t == "VarScene":
            return self.cmp(float(self.V.get(p[0], 0) or 0), p[1], self.num(p[2], pick))
        if t == "VarSceneTxt":
            return self.cmp(str(self.V.get(p[0], "")), p[1], self.ev_expr(p[2], pick))
        if t == "BuiltinCommonInstructions::CompareNumbers":
            return self.cmp(self.num(p[0], pick), p[1], self.num(p[2], pick))
        if t == "DepartScene":
            return self.primero
        if t == "BuiltinCommonInstructions::Once":
            ok = not self.once.get(eid, False)
            self.once[eid + "_now"] = True
            return ok
        if t == "BuiltinCommonInstructions::Or":
            return any(self.cond(s, dict(pick), eid) for s in c.get("subInstructions", []))
        if t in ("VarObjet", "VarObjetTxt"):
            if p[0] == "Zombies":
                return False
            val = lambda o: (float(o.v.get(p[1], 0) or 0) if t == "VarObjet" else str(o.v.get(p[1], "")))
            rhs = self.num(p[3], pick) if t == "VarObjet" else self.ev_expr(p[3], pick)
            return self.filtra(pick, p[0], lambda o: self.cmp(val(o), p[2], rhs))
        if t in ("CollisionNP", "Distance"):
            if p[0] == "Sup" and p[1] in ("Bidon", "Bolsa"):
                return self.filtra(pick, p[1], lambda o: o.tocado)
            return False
        if t == "CompareTimer":
            return self.cmp(self.t - self.timers.get(p[1].strip('"'), 0), p[2], self.num(p[3], pick))
        if t == "PickNearest":
            return self.filtra(pick, p[0], lambda o: True) and (pick.__setitem__(p[0], pick[p[0]][:1]) or True)
        if t in ("KeyPressed", "KeyReleased", "MouseButtonReleased"):
            return False
        raise RuntimeError("condición sin simular: " + t)

    # ---------------- acciones
    def acc(self, x, pick):
        t, p = x["type"]["value"], x["parameters"]
        if t in ("ModVarScene", "ModVarSceneTxt", "ModVarGlobal", "ModVarGlobalTxt"):
            D = self.V if "Scene" in t else self.G
            val = self.ev_expr(p[2], pick)
            if t.endswith("Txt"):
                D[p[0]] = (str(D.get(p[0], "")) + str(val)) if p[1] == "+" else str(val)
                if p[0] == "Banner":
                    self.letreros.append((round(self.t, 2), D[p[0]]))
            else:
                cur = float(D.get(p[0], 0) or 0); val = float(val)
                D[p[0]] = {"=": val, "+": cur + val, "-": cur - val, "*": cur * val, "/": cur / val if val else 0}[p[1]]
        elif t == "Create":
            o = Inst(p[1], self.num(p[2], pick), self.num(p[3], pick))
            self.objs.append(o)
            pick[p[1]] = [o]
            self.creados.append((round(self.t, 2), p[1], o.x, o.y))
        elif t in ("ModVarObjet", "ModVarObjetTxt"):
            for o in self.sel(pick, p[0]):
                val = self.ev_expr(p[3], {**pick, p[0]: [o]})
                if t == "ModVarObjetTxt":
                    o.v[p[1]] = str(val)
                else:
                    cur = float(o.v.get(p[1], 0) or 0); val = float(val)
                    o.v[p[1]] = {"=": val, "+": cur + val, "-": cur - val, "*": cur * val}[p[2]]
        elif t == "Delete":
            for o in self.sel(pick, p[0]):
                if o in self.objs:
                    self.objs.remove(o)
            pick[p[0]] = []
        elif t == "ResetTimer":
            self.timers[p[1].strip('"')] = self.t
        elif t == "PlaySound":
            self.sonidos.append((round(self.t, 2), os.path.basename(p[1])))
        elif t == "TextObject::String":
            self.T[p[0]] = str(self.ev_expr(p[2], pick))
        elif t == "SetAnimationName" and p[0] == "Objetivo":
            for o in self.sel(pick, "Objetivo"):
                o.v["_anim"] = p[1].strip('"')
        # el resto (mostrar, ocultar, ángulos, capas, sonido de fondo, comportamientos) no afecta a la prueba

    def sel(self, pick, nombre):
        if nombre in pick:
            return list(pick[nombre])
        return [o for o in self.objs if o.n == nombre]

    # ---------------- eventos
    def correr(self, lst, pick, ruta):
        for i, e in enumerate(lst):
            eid = ruta + "/" + str(i)
            t = e.get("type", "")
            if t.endswith("Comment") or t.endswith("JsCode"):
                continue
            if t.endswith("Group"):
                self.correr(e.get("events", []), dict(pick), eid)
                continue
            if t.endswith("ForEach"):
                if not all(self.cond(c, dict(pick), eid) for c in e.get("conditions", []) if c["parameters"][:1] != [e["object"]]):
                    continue
                for o in [o for o in self.sel(pick, e["object"])]:
                    pk = dict(pick); pk[e["object"]] = [o]
                    if all(self.cond(c, pk, eid) for c in e.get("conditions", [])):
                        for x in e.get("actions", []):
                            self.acc(x, pk)
                        self.correr(e.get("events", []), pk, eid)
                continue
            pk = {k: list(v) for k, v in pick.items()}
            ok = True
            for c in e.get("conditions", []):
                if not self.cond(c, pk, eid):
                    ok = False
                    break
            if ok:
                for x in e.get("actions", []):
                    self.acc(x, pk)
                self.correr(e.get("events", []), pk, eid)

    def paso(self):
        self.correr(self.ev, {}, "")
        for k in [k for k in self.once if k.endswith("_now")]:
            pass
        # Trigger once: verdadero solo si el cuadro anterior no se cumplieron sus condiciones
        nuevos = {k[:-4]: True for k in self.once if k.endswith("_now")}
        self.once = nuevos
        self.primero = False
        self.t += DT


# ------------------------------------------------------------------ jugador simulado
def jugar(sim, max_s=240, doble_bidon=True):
    """Completa objetivos como lo haría un jugador: mantiene Usar en el objetivo activo (lo marca hecho) y recoge
    bidones y bolsas. Devuelve la lista de ObjTipo en el orden en que se activaron."""
    tipos = []
    ultimo = sim.V.get("_ultimo")
    tocar_par = doble_bidon
    while sim.t < max_s and sim.V.get("Estado") == "juego":
        sim.paso()
        if sim.V.get("ObjIni") == 1 and sim.V.get("ObjTipo") != ultimo:
            ultimo = sim.V.get("ObjTipo"); tipos.append(ultimo); sim.V["_ultimo"] = ultimo
        if sim.V.get("ObjTipo") == "final":
            if sim.V.get("FinalActivo", 0) == 0 and any(o.n == "Objetivo" for o in sim.objs):
                sim.V["FinalActivo"] = 1; sim.timers["final"] = sim.t       # alguien llega al camión
            continue
        bid = [o for o in sim.objs if o.n == "Bidon"]
        if bid:
            if tocar_par and len(bid) >= 2:
                bid[0].tocado = bid[1].tocado = True; tocar_par = False      # 2 bidones en el mismo cuadro
            else:
                bid[0].tocado = True
            continue
        bol = [o for o in sim.objs if o.n == "Bolsa"]
        if bol:
            bol[0].tocado = True
            continue
        if sim.V.get("CanepaCharla", 0) == 1:
            # la charla con Canepa (canepa.js, que esta prueba no corre): al terminar el diálogo pone Paso = 99 y CanepaCharla = 2
            sim.charlas.append(round(sim.t, 2))
            sim.V["Paso"] = 99; sim.V["CanepaCharla"] = 2
            continue
        objetivo = [o for o in sim.objs if o.n == "Objetivo" and o.v.get("Hecho", 0) == 0]
        if objetivo and int(sim.t * 60) % 30 == 0:
            o = objetivo[0]
            o.v["Progreso"] = o.v.get("Tiempo", 1)
            o.v["Hecho"] = 1                                                  # terminó de mantener Usar
            # sigue "manteniendo" sobre el mismo objetivo: no debe volver a contar
            sim.paso(); o.v["Hecho"] = 1; sim.paso()
    return tipos


def main():
    d = json.load(open(PRY, encoding="utf-8"))
    ok = mal = 0

    def prueba(nombre, cond, extra=""):
        nonlocal ok, mal
        if cond:
            ok += 1; print("  OK  ", nombre)
        else:
            mal += 1; print("  MAL ", nombre, extra)

    # ---------------- Historia
    sim = Sim(d["layouts"], "historia", 1)
    tipos = jugar(sim)
    prueba("Historia: 6 misiones en el orden pedido y luego el final", tipos == ["llamada", "luz", "llaves", "carnada", "canepa", "gasolina", "final"], tipos)
    prueba("Historia: termina en victoria", sim.V.get("Estado") == "victoria", sim.V.get("Estado"))
    servidor = [c for c in sim.creados if c[1] == "Objetivo" and (c[2], c[3]) == (3616.0, 1476.0)]
    compu = [c for c in sim.creados if c[1] == "Objetivo" and (c[2], c[3]) == (3136.0, 1760.0)]
    prueba("Llamada: directo la computadora del CIC (sin el servidor del SITE)", not servidor and len(compu) == 1 and dentro(ZONAS_CIC[1], 3136, 1760))
    inter = [c for c in sim.creados if c[1] == "Objetivo" and (c[2], c[3]) not in ((3136.0, 1760.0),) and 1600 <= c[3] <= 1800 and 2600 <= c[2] <= 3800]
    prueba("Interruptores: 3, todos dentro del CIC", len(inter) == 3 and all(any(dentro(z, x, y) for z in ZONAS_CIC) for _, _, x, y in inter), inter)
    prueba("Carnada: se entrega en la nevería", any(c[1] == "Objetivo" and dentro(NEVERIA, c[2], c[3]) for c in sim.creados))
    prueba("Gasolina: 2 bidones recogidos en el mismo cuadro cuentan 2 (y el objetivo se puede completar)", "gasolina" in tipos and tipos[-1] == "final")
    # lo que se ve es el último letrero de cada cuadro (un evento puede reemplazar al anterior en el mismo cuadro)
    vis = {}
    for t, txt in sim.letreros:
        vis[t] = txt
    sim.letreros = sorted(vis.items())
    cumplidos = [l for l in sim.letreros if "CUMPLIDO" in l[1]]
    nuevos = [l for l in sim.letreros if l[1].startswith("OBJETIVO ")]
    prueba("Señal al cumplir cada misión: ¡OBJETIVO n/6 CUMPLIDO! (6 veces, una por misión)",
           [l[1] for l in cumplidos] == ["¡OBJETIVO %d/6 CUMPLIDO!" % n for n in range(1, 7)], [l[1] for l in cumplidos])
    prueba("Señal al activar cada misión: OBJETIVO n/6 · ... (6 veces)", [l[1][:15] for l in nuevos] == ["OBJETIVO %d/6 · " % n for n in range(1, 7)], [l[1] for l in nuevos])
    prueba("Misión 5: OBJETIVO 5/6 · HABLAR CON CANEPA EN EL CAMIÓN", any(l[1] == "OBJETIVO 5/6 · HABLAR CON CANEPA EN EL CAMIÓN" for l in nuevos), [l[1] for l in nuevos])
    canepa = [c for c in sim.creados if c[1] == "Objetivo" and (c[2], c[3]) == (544.0, 3328.0)]
    prueba("Canepa: un solo punto de misión, junto a él en el camión (544, 3328)", len(canepa) == 1, canepa)
    t_comida = next((l[0] for l in cumplidos if l[1] == "¡OBJETIVO 4/6 CUMPLIDO!"), None)
    t_gas = next((l[0] for l in nuevos if "GASOLINA" in l[1]), None)
    prueba("La charla con Canepa va una sola vez, después de entregar la comida y antes de activar la gasolina",
           len(sim.charlas) == 1 and t_comida is not None and t_gas is not None and t_comida < sim.charlas[0] < t_gas, (sim.charlas, t_comida, t_gas))
    pausas = []
    for t, txt in cumplidos:
        sig = [l for l in sim.letreros if l[0] > t and (l[1].startswith("OBJETIVO ") or l[1] == "¡AL ESTACIONAMIENTO!")]
        pausas.append(round(sig[0][0] - t, 2) if sig else None)
    prueba("El letrero de cumplido se ve 2.5 s antes de que empiece el siguiente", all(p is not None and 2.4 <= p <= 2.6 for p in pausas), pausas)
    sn = [os.path.splitext(s[1])[0] + ".ogg" for s in sim.sonidos]   # sin importar el formato (fase 47: algunos son .wav)
    prueba("Sonidos: 6 de cumplido y 6 de nuevo objetivo", sn.count("objetivo_cumplido.ogg") == 6 and sn.count("objetivo_nuevo.ogg") == 6,
           (sn.count("objetivo_cumplido.ogg"), sn.count("objetivo_nuevo.ogg")))
    prueba("Cada misión se cumple una sola vez (ObjNum termina en 7 = final)", sim.V.get("ObjNum") == 7, sim.V.get("ObjNum"))

    # HUD
    sim2 = Sim(d["layouts"], "historia", 2)
    textos = {}
    for _ in range(int(60 * 0.5)):
        sim2.paso()
    textos["llamada"] = sim2.T["TxtObjetivo"]
    prueba("HUD: «Objetivo 1/6» + texto de la llamada", textos["llamada"] == "Objetivo 1/6\nLlamen desde la computadora del CIC", repr(textos["llamada"]))
    # HUD de la misión de Canepa: se ve mientras está activa (también durante la charla)
    sim3 = Sim(d["layouts"], "historia", 4)
    hud = None
    while sim3.t < 240 and hud is None and sim3.V.get("Estado") == "juego":
        jugar_un_paso = [o for o in sim3.objs if o.n == "Objetivo" and o.v.get("Hecho", 0) == 0]
        if sim3.V.get("ObjTipo") == "canepa" and sim3.V.get("ObjIni") == 1 and sim3.V.get("ObjEspera", 0) <= 0:
            sim3.paso(); hud = sim3.T["TxtObjetivo"]; break
        jugar(sim3, max_s=sim3.t + 0.6)
    prueba("HUD: «Objetivo 5/6» + Hablen con el profe Canepa en el camión", hud == "Objetivo 5/6\nHablen con el profe Canepa en el camión", repr(hud))
    prueba("En línea: ObjTxt lleva el mismo texto para los clientes", sim2.V.get("ObjTxt") == textos["llamada"])

    # ---------------- Escape: igual que antes de la fase 43
    resp = sorted(glob.glob(os.path.join(AQUI, "..", "respaldos", "antes_de_fase55_*.json")))
    if resp:
        viejo = json.load(open(resp[0], encoding="utf-8"))
        for semilla in (3, 7, 11):
            a, b = Sim(d["layouts"], "escape", semilla), Sim(viejo["layouts"], "escape", semilla)
            ta, tb = jugar(a, doble_bidon=False), jugar(b, doble_bidon=False)
            for s_ in (a, b):
                vis = {}
                for t, txt in s_.letreros:
                    vis[t] = txt
                s_.letreros = sorted(vis.items())
            iguales = ta == tb and [c[1:] for c in a.creados] == [c[1:] for c in b.creados] and \
                [l[1] for l in a.letreros] == [l[1] for l in b.letreros] and a.V.get("Estado") == b.V.get("Estado")
            prueba("Escape (semilla %d): mismos objetivos, objetos, letreros y resultado que antes: %s" % (semilla, " > ".join(ta)), iguales,
                   (tb, a.V.get("Estado"), b.V.get("Estado")))
        a = Sim(d["layouts"], "escape", 5)
        a.paso()
        for _ in range(30):
            a.paso()
        prueba("Escape: el HUD sigue diciendo «Objetivo 1/3»", a.T["TxtObjetivo"].startswith("Objetivo 1/3"), repr(a.T["TxtObjetivo"]))
    else:
        print("  (sin respaldo antes_de_fase55: no se compara Escape)")
    print("%d correctas, %d fallidas" % (ok, mal))
    sys.exit(1 if mal else 0)


if __name__ == "__main__":
    main()
