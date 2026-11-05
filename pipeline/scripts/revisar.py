"""Fase 4: revisión automática -> generado/revision/metricas.json
           + hojas de contacto -> generado/revision/hojas/<entidad>.png
"""
import json
import os
import sys
from collections import defaultdict

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
from comun import BASE_ENTIDAD, GEN, LOG, RAIZ, cargar_manifest, ruta

REV = GEN / "revision"
HOJAS = REV / "hojas"
PROC = LOG / "proc"
UMBRAL_ESTATURA = 0.12
UMBRAL_PALETA = 22.0  # distancia RGB media (HD) contra la paleta de la base


def clave_revision(job):
    """Entidad de revisión: efectos van con su personaje."""
    if job["categoria"] == "objetos":
        return "objetos"
    return job["entidad"]


def frames_de(job):
    if job["categoria"] == "objetos":
        d = GEN / "sprites" / "objetos" / job["animacion"]
        return [_leer(d / f"{n}.png") for n in job["nombres"] if (d / f"{n}.png").exists()]
    d = GEN / "sprites" / job["categoria"] / job["entidad"] / job["animacion"]
    return [_leer(p) for p in sorted(d.glob(f"{job['animacion']}_[0-9][0-9].png"))]


def _leer(p):
    with Image.open(p) as im:
        return np.array(im.convert("RGBA"))


def magenta_sobrante(frames):
    n = 0
    for a in frames:
        r, g, b, al = [a[..., i].astype(int) for i in range(4)]
        n += int(((al > 0) & (r - g > 80) & (b - g > 80) & (r > 150) & (b > 150)).sum())
    return n


def metricas_job(job, info):
    frames = frames_de(job)
    m = {"id": job["id"], "categoria": job["categoria"], "entidad": job["entidad"],
         "animacion": job["animacion"], "cuadros_esperados": job["frames"],
         "cuadros_detectados": info.get("detectados"), "metodo_separacion": info.get("metodo"),
         "alertas": list(info.get("marcas", []))}
    if m["cuadros_detectados"] != m["cuadros_esperados"] or info.get("metodo") == "partes_iguales":
        if "REVISAR: cuadros" not in m["alertas"]:
            m["alertas"].append("REVISAR: cuadros")
    # estatura (en HD) de los cuadros de pie
    alt = info.get("alturas_hd", [])
    esc = job["escala"]
    if job["categoria"] in ("personajes", "profes", "zombies") and alt:
        if esc == "frames_1_6_standing":
            de_pie = [alt[i] for i in (0, 5) if i < len(alt)]
        elif esc == "frame_1_standing":
            de_pie = alt[:1]
        else:
            de_pie = alt
        var = (max(de_pie) - min(de_pie)) / float(np.median(de_pie)) if len(de_pie) > 1 else 0.0
        m["variacion_estatura"] = round(var, 3)
        if var > UMBRAL_ESTATURA:
            m["alertas"].append(f"estatura varía {var:.0%}")
    ms = magenta_sobrante(frames)
    m["pixeles_magenta"] = ms
    if ms > 0:
        m["alertas"].append(f"{ms} px magenta")
    m["cuadros_cortados"] = info.get("cortados", [])
    if m["cuadros_cortados"]:
        m["alertas"].append(f"cuadros cortados en el borde: {[i + 1 for i in m['cuadros_cortados']]}")
    dp = info.get("dist_paleta")
    m["distancia_paleta"] = round(dp, 1) if dp is not None else None
    if dp is not None and dp > UMBRAL_PALETA:
        m["alertas"].append(f"colores lejos de la base ({dp:.0f})")
    rep = []
    if job["frames"] > 1:
        for i in range(len(frames)):
            for k in range(i + 1, len(frames)):
                if frames[i].shape == frames[k].shape and np.array_equal(frames[i], frames[k]):
                    rep.append([i + 1, k + 1])
    m["cuadros_repetidos"] = rep
    if rep:
        m["alertas"].append(f"cuadros idénticos {rep}")
    return m


def fuente(t=14):
    for f in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(f, t)
        except OSError:
            pass
    return ImageFont.load_default()


def sobre_gris(a):
    im = Image.fromarray(a, "RGBA")
    bg = Image.new("RGBA", im.size, (200, 200, 200, 255))
    bg.alpha_composite(im)
    return bg.convert("RGB")


def hoja_contacto(clave, jobs):
    f = fuente(16)
    filas = []
    for j in jobs:
        if j["categoria"] == "objetos":
            fr = frames_de(j)
            if not fr:
                continue
            H = max(x.shape[0] for x in fr) + 4
            W = sum(x.shape[1] + 6 for x in fr)
            t = np.zeros((H, W, 4), np.uint8)
            x = 0
            for a in fr:
                t[H - 2 - a.shape[0]:H - 2, x:x + a.shape[1]] = a
                x += a.shape[1] + 6
            im = sobre_gris(t)
            nom = f"{j['animacion']}: " + ", ".join(j["nombres"])
        else:
            p = GEN / "sprites" / j["categoria"] / j["entidad"] / j["animacion"] / f"{j['animacion']}_tira.png"
            if not p.exists():
                continue
            im = sobre_gris(_leer(p))
            nom = f"{j['animacion']}  ({j['frames']} cuadros{', loop' if j.get('loop') else ''})"
        im = im.resize((im.width * 2, im.height * 2), Image.Resampling.NEAREST)
        filas.append((nom, im))
    if not filas:
        return None
    base_nombre = BASE_ENTIDAD.get(clave)
    if base_nombre:
        with Image.open(RAIZ / "assetsimage" / base_nombre) as b0:
            base = b0.convert("RGBA")
        bg = Image.new("RGBA", base.size, (255, 255, 255, 255))
        bg.alpha_composite(base)
        base = bg.convert("RGB")
        base = base.resize((int(base.width * 420 / base.height), 420), Image.Resampling.LANCZOS)
    else:
        base = Image.new("RGB", (280, 420), "white")
        ImageDraw.Draw(base).text((10, 10), "objetos\n(sin base:\nreferencia de estilo\nalessandro.png)", fill="black", font=f)
    ancho = base.width + 20 + max(max(im.width, int(f.getlength(n)) + 10) for n, im in filas) + 20
    alto = max(base.height + 40, sum(im.height + 30 for _, im in filas) + 20)
    hoja = Image.new("RGB", (ancho, alto), "white")
    d = ImageDraw.Draw(hoja)
    d.text((10, 8), f"BASE: {clave}", fill="black", font=f)
    hoja.paste(base, (10, 30))
    y = 10
    x0 = base.width + 30
    for nom, im in filas:
        d.text((x0, y), nom, fill="black", font=f)
        hoja.paste(im, (x0, y + 20))
        y += im.height + 30
    HOJAS.mkdir(parents=True, exist_ok=True)
    p = HOJAS / f"{clave}.png"
    hoja.save(p)
    return p


def main():
    jobs = cargar_manifest()
    metricas = {}
    por_entidad = defaultdict(list)
    for j in jobs:
        pi = PROC / f"{j['id']}.json"
        if not pi.exists():
            continue
        info = json.loads(pi.read_text(encoding="utf-8"))
        metricas[j["id"]] = metricas_job(j, info)
        por_entidad[clave_revision(j)].append(j)
    REV.mkdir(parents=True, exist_ok=True)
    (REV / "metricas.json").write_text(json.dumps(metricas, ensure_ascii=False, indent=1), encoding="utf-8")
    if "--hojas" in sys.argv:
        for clave, js in por_entidad.items():
            js.sort(key=lambda j: (j["categoria"] == "efectos",))
            hoja_contacto(clave, js)
    con = sum(1 for m in metricas.values() if m["alertas"])
    print(f"{len(metricas)} animaciones medidas, {con} con alertas; {len(por_entidad)} hojas de contacto")


if __name__ == "__main__":
    main()
