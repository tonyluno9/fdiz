"""Fase 6: genera generado/revision/index.html y generado/revision/REPORTE.md."""
import html
import json
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from comun import (BASE_ENTIDAD, GEN, LIMITE_TOTAL, cargar_manifest, cargar_overrides,
                   generaciones_usadas, leer_log, ruta)

REV = GEN / "revision"
CALIF = REV / "calificaciones.json"
NOTAS = REV / "notas_proceso.json"  # cambios a prompts genéricos / decisiones de proceso
ORDEN_ENT = ["tony", "miranda", "cesar", "alan", "castillo", "alessandro", "gabo", "carlos",
             "tonyfuerte", "normal", "corredor", "griton", "gordo", "conserje", "curado",
             "objetos", "canepa", "joel", "justino"]


def clave(j):
    return "objetos" if j["categoria"] == "objetos" else j["entidad"]


def gif_rel(j):
    return f"../preview/{j['categoria']}/{j['entidad']}/{j['animacion']}.gif"


def tira_rel(j):
    if j["categoria"] == "objetos":
        return f"generado/sprites/objetos/{j['animacion']}/"
    return f"generado/sprites/{j['categoria']}/{j['entidad']}/{j['animacion']}/{j['animacion']}_tira.png"


def main():
    jobs = cargar_manifest()
    cal = {}
    for p in sorted((REV / "calif").glob("*.json")):
        cal.update(json.loads(p.read_text(encoding="utf-8")))
    CALIF.write_text(json.dumps(cal, ensure_ascii=False, indent=1), encoding="utf-8")
    met = json.loads((REV / "metricas.json").read_text(encoding="utf-8"))
    notas = json.loads(NOTAS.read_text(encoding="utf-8")) if NOTAS.exists() else {}
    log = leer_log()
    usadas = generaciones_usadas(log)
    por_ent = defaultdict(list)
    for j in jobs:
        por_ent[clave(j)].append(j)

    def calif(j):
        if not ruta(j["salida_raw"]).exists():
            if j["categoria"] == "profes":
                return "PENDIENTE", "no generado: papel de los profes sin definir"
            return "FALTA", "no se generó (falló o sin límite)"
        c = cal.get(j["id"], {})
        return c.get("calificacion", "SIN CALIFICAR"), c.get("razon", "")

    # ------------------------------------------------ HTML
    css = """body{font-family:system-ui,Segoe UI,Arial;background:#f4f4f4;margin:20px;color:#222}
h1{margin:0 0 6px} .ent{background:#fff;border-radius:8px;padding:14px;margin:18px 0;display:flex;gap:18px}
.base img{height:260px;image-rendering:pixelated;border:1px solid #ddd;background:#fff}
.anims{display:flex;flex-wrap:wrap;gap:10px;align-items:flex-start}
.a{border:2px solid #ccc;border-radius:6px;padding:6px;background:#fafafa;max-width:420px}
.a img{image-rendering:pixelated;max-width:400px;display:block}
.a.PENDIENTE{opacity:.5}.a.REVISAR{background:#fff6bf;border-color:#e0b400}.a.REHACER,.a.FALTA{background:#ffd6d6;border-color:#d00}
.n{font-weight:600;font-size:14px}.r{font-size:12px;color:#444;margin-top:3px}
.b{font-size:11px;padding:1px 6px;border-radius:8px;background:#ddd;margin-left:6px}
.REVISAR .b{background:#e0b400}.REHACER .b,.FALTA .b{background:#d00;color:#fff}.OK .b{background:#3a3;color:#fff}
.filtro{margin:8px 0} label{margin-right:12px}"""
    cuenta = Counter()
    partes = []
    for e in ORDEN_ENT + [k for k in por_ent if k not in ORDEN_ENT]:
        if e not in por_ent:
            continue
        if all(not ruta(j["salida_raw"]).exists() for j in por_ent[e]) and e in ("joel", "justino", "canepa"):
            partes.append(f'<div class="ent" id="{e}"><div class="base"><div class="n">{e}</div></div><div class="anims"><i>Pendiente: papel del profe sin definir; no se generó nada.</i></div></div>')
            for j in por_ent[e]:
                cuenta["PENDIENTE"] += 1
            continue
        b = BASE_ENTIDAD.get(e)
        base_html = (f'<div class="base"><img src="../../assetsimage/{b}" title="{b}"><div class="n">{e}</div></div>'
                     if b else f'<div class="base"><div class="n">objetos</div><div class="r">referencia de estilo: alessandro.png</div></div>')
        items = []
        for j in por_ent[e]:
            c, r = calif(j)
            cuenta[c] += 1
            alert = ", ".join(met.get(j["id"], {}).get("alertas", []))
            img = f'<img src="{gif_rel(j)}" loading="lazy">' if c not in ("FALTA", "PENDIENTE") else ""
            items.append(f'<div class="a {c}"><div class="n">{html.escape(j["categoria"] + "/" + j["animacion"])}'
                         f'<span class="b">{c}</span></div>{img}<div class="r">{html.escape(r)}</div>'
                         + (f'<div class="r"><i>auto: {html.escape(alert)}</i></div>' if alert else "") + "</div>")
        partes.append(f'<div class="ent" id="{e}">{base_html}<div class="anims">{"".join(items)}</div></div>')
    resumen = " · ".join(f"{k}: {v}" for k, v in cuenta.most_common())
    js = """<script>function f(){const s=document.getElementById('solo').checked;
document.querySelectorAll('.a').forEach(a=>{a.style.display=(s&&a.classList.contains('OK'))?'none':''})}</script>"""
    pagina = f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><title>FDI-Z · revisión de sprites</title>
<style>{css}</style>{js}</head><body><h1>FDI-Z · revisión de sprites</h1>
<div>Generaciones usadas: {usadas}/{LIMITE_TOTAL} · {resumen}</div>
<div class="filtro"><label><input type="checkbox" id="solo" onchange="f()"> Mostrar solo lo marcado (amarillo = REVISAR, rojo = REHACER)</label></div>
{''.join(partes)}</body></html>"""
    (REV / "index.html").write_text(pagina, encoding="utf-8")

    # ------------------------------------------------ REPORTE.md
    sin_raw = [j["id"] for j in jobs if not ruta(j["salida_raw"]).exists()]
    pend = [s for s in sin_raw if s.split("__")[0] in ("canepa", "joel", "justino")]
    fallidos_int = [x for x in log if x.get("estado") not in ("completed", "enviado")]
    cerrados = {x["request_id"] for x in log if x.get("request_id") and x.get("estado") != "enviado"}
    huerfanos = [x for x in log if x.get("estado") == "enviado" and x["request_id"] not in cerrados]
    sin_raw = [j["id"] for j in jobs if not ruta(j["salida_raw"]).exists()]
    marcadas = []
    for e in ORDEN_ENT + [k for k in por_ent if k not in ORDEN_ENT]:
        for j in por_ent.get(e, []):
            c, r = calif(j)
            if c not in ("OK", "PENDIENTE"):
                marcadas.append((j, c, r))
    L = ["# FDI-Z · Reporte de generación de sprites", ""]
    L += ["## Generaciones", "",
          f"- Generaciones usadas: **{usadas} de {LIMITE_TOTAL}** (180 del manifiesto + 40 de margen).",
          f"- Intentos que no terminaron bien: {len(fallidos_int)}."]
    if fallidos_int:
        for x in fallidos_int:
            L.append(f"  - `{x['id']}` intento {x.get('intento')}: {x.get('estado')} {x.get('error') or ''}".rstrip())
    for x in huerfanos:
        L.append(f"  - `{x['id']}`: enviado (request_id `{x['request_id']}`) pero la corrida se cortó antes de recibir el resultado.")
    L.append("- **Ojo con el cobro:** la corrida de la fase 2 la detuvo Claude Code por falta de memoria. Hasta **3 trabajos** que estaban en curso "
             "pudieron cobrarse en WaveSpeed sin quedar en el log (en esa versión del script la línea se escribía al terminar). "
             "Revisa el historial de WaveSpeed: el uso real puede ser hasta 3 generaciones mayor que el de arriba. "
             "Desde entonces el script escribe una línea \"enviado\" con su request_id antes de esperar el resultado.")
    pend = [s for s in sin_raw if s.split("__")[0] in ("canepa", "joel", "justino")]
    otros = [s for s in sin_raw if s not in pend]
    L.append(f"- Trabajos sin imagen al final: {len(sin_raw)}" + (f" ({len(pend)} de profes, pendientes a propósito)" if pend else "")
             + (": " + ", ".join(f"`{s}`" for s in otros) if otros else "."))
    reh = notas.get("rehechos", [])
    if reh:
        L.append(f"- Regenerados tras la revisión (REHACER): {len(reh)}: " + ", ".join(f"`{x}`" for x in reh) + ".")
    L += ["", "## Resultado", ""]
    for k in ("OK", "REVISAR", "REHACER", "FALTA", "PENDIENTE", "SIN CALIFICAR"):
        if cuenta.get(k):
            L.append(f"- **{k}:** {cuenta[k]}")
    L += ["", "## Lo que hay que revisar", ""]
    if marcadas:
        L += ["| Entidad | Animación | Calificación | Razón | GIF | Tira |", "|---|---|---|---|---|---|"]
        for j, c, r in marcadas:
            L.append(f"| {j['entidad']} | {j['categoria']}/{j['animacion']} | {c} | {r.replace('|', '/')} | "
                     f"`generado/preview/{j['categoria']}/{j['entidad']}/{j['animacion']}.gif` | `{tira_rel(j)}` |")
    else:
        L.append("Nada: todas las animaciones quedaron OK.")
    L += ["", "## Lo que no se generó", "",
          "- **Criollo:** todavía no tiene imagen base, así que no se generó nada de él.",
          "- **Profes (Canepa, Joel, Justino): PENDIENTE.** Su papel en el juego todavía no se define, así que por decisión del equipo no se generaron los "
          + str(len(pend)) + " trabajos que faltaban: " + ", ".join(f"`{s}`" for s in pend) + ". "
          "De Canepa sí quedaron las 6 animaciones que alcanzaron a generarse (procesadas y revisadas); Joel y Justino no tienen nada todavía. "
          "Cuando se defina su papel, se generan con `python generar.py --ids ...` (los que ya existen no se vuelven a cobrar).",
          "", "## Cambios a los prompts genéricos", ""]
    ov = cargar_overrides()
    if ov.get("reemplazos_genericos"):
        for r in ov["reemplazos_genericos"]:
            L.append(f"- Se cambió «{r['de']}» por «{r['a']}».")
    else:
        L.append("- Ninguno: el piloto salió bien con las frases de formato originales.")
    if ov.get("correcciones"):
        L.append("- Frases de corrección añadidas al regenerar (solo en esos trabajos, sin tocar la descripción del personaje):")
        for k, v in ov["correcciones"].items():
            L.append(f"  - `{k}`: “{v}”")
    if notas.get("proceso"):
        L += ["", "## Notas del procesamiento", ""] + [f"- {n}" for n in notas["proceso"]]
    (REV / "REPORTE.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"index.html y REPORTE.md listos. {dict(cuenta)}; generaciones {usadas}/{LIMITE_TOTAL}")


if __name__ == "__main__":
    main()
