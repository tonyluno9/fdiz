"""Fase 47 · Los textos de porcentaje (usando, revisando, curando) pasan de 100%: se limita a 100 con min(100, ...). Idempotente; va después de la fase 46."""
import datetime, json, os, shutil
AQUI = os.path.dirname(os.path.abspath(__file__))
PRY = os.path.join(AQUI, "..", "FDI-Z", "FDI-Z.json")
d = json.load(open(PRY, encoding="utf-8"))
resp = os.path.join(AQUI, "..", "respaldos"); os.makedirs(resp, exist_ok=True)
bak = os.path.join(resp, "antes_de_fase47_%s.json" % datetime.date.today().strftime("%Y%m%d"))
if not os.path.exists(bak): shutil.copy(PRY, bak)
PAT = ["round(100 * Objetivo.Variable(Progreso) / Objetivo.Variable(Tiempo))",
       "round(100 * Contenedor.Variable(Progreso))",
       "round(100 * Sup.Variable(Cura) / 3)"]
n = 0
def walk(ev):
    global n
    for e in ev:
        for a in e.get("actions", []):
            ps = a.get("parameters", [])
            for i, p in enumerate(ps):
                if isinstance(p, str) and "Variable(" in p and p.count("%") and any(x in p for x in PAT):
                    for x in PAT:
                        if "min(100, " + x + ")" not in p:
                            p = p.replace(x, "min(100, " + x + ")")
                    if p != ps[i]: ps[i] = p
                    n += 1
        walk(e.get("events", []))
for l in d["layouts"]: walk(l["events"])
json.dump(d, open(PRY, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("OK fase47 (%d textos)" % n)
