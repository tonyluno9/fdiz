"""Fase 3: procesa las tiras de generado/raw -> sprites listos para GDevelop.

Uso: python procesar.py            (procesa todo lo que tenga raw)
     python procesar.py --entidades tony normal
"""
import argparse
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(__file__))
from comun import BASE_ENTIDAD, GEN, LOG, RAIZ, cargar_manifest, ruta

MAGENTA = np.array([255, 0, 255], dtype=np.float32)
SPRITES = GEN / "sprites"
HD = GEN / "limpio_hd"
PREVIEW = GEN / "preview"
PROC = LOG / "proc"
GRIS_PREVIEW = (200, 200, 200)
ES_PERSONAJE = {"personajes", "profes", "zombies"}
UMBRAL_PALETA = 55  # distancia RGB a partir de la cual un color no es "de la base"


# ---------------------------------------------------------------- fondo
def quitar_fondo(rgb, personaje):
    """rgb uint8 HxWx3 -> máscara fg bool HxW."""
    f = rgb.astype(np.float32)
    dist = np.sqrt(((f - MAGENTA) ** 2).sum(-1))
    cerca = dist < 90
    lab, n = ndi.label(cerca)
    borde = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    fondo = np.isin(lab, borde[borde > 0])
    # pasada global: manchas magenta aisladas (entre piernas/brazos)
    fondo |= dist < 70
    # halo: orillas con tinte magenta
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    tinte = ((r - g) > 50) & ((b - g) > 50) & (dist < 200)
    for _ in range(3):
        orilla = ndi.binary_dilation(fondo, iterations=1) & ~fondo
        quitar = orilla & tinte
        if not quitar.any():
            break
        fondo |= quitar
    if personaje:
        # sombra del piso pintada como magenta oscuro: mismo tono magenta, menos brillo
        tono = (r - g > 60) & (b - g > 60) & (np.abs(r - b) < 70) & (g < 0.5 * np.minimum(r, b))
        fondo |= tono
    fg = ~fondo
    # ruido diminuto
    lab, n = ndi.label(fg, structure=np.ones((3, 3)))
    if n:
        tam = ndi.sum(fg, lab, range(1, n + 1))
        chicos = np.where(tam < 25)[0] + 1
        fg[np.isin(lab, chicos)] = False
    # sombra gris en el piso separada del cuerpo
    if personaje:
        lab, n = ndi.label(fg, structure=np.ones((3, 3)))
        H = fg.shape[0]
        for i, sl in enumerate(ndi.find_objects(lab), start=1):
            h = sl[0].stop - sl[0].start
            w = sl[1].stop - sl[1].start
            if sl[0].start < 0.6 * H or h > 0.35 * w:
                continue
            m = lab[sl] == i
            px = f[sl][m]
            sat = px.max(1) - px.min(1)
            lum = px.mean(1)
            if np.median(sat) < 30 and 50 < np.median(lum) < 215:
                fg[sl][m] = False
    return fg


# ---------------------------------------------------------------- cuadros
def segmentos_columnas(fg, min_hueco=3):
    occ = fg.sum(0) > 1
    segs, x, W = [], 0, fg.shape[1]
    while x < W:
        if occ[x]:
            x0 = x
            while x < W and occ[x]:
                x += 1
            segs.append([x0, x])
        else:
            x += 1
    # unir huecos muy pequeños
    out = []
    for s in segs:
        if out and s[0] - out[-1][1] < min_hueco:
            out[-1][1] = s[1]
        else:
            out.append(s)
    return out


def unir_pequenos(segs, fg):
    segs = [list(s) for s in segs]
    while len(segs) > 1:
        masas = [fg[:, a:b].sum() for a, b in segs]
        anchos = [b - a for a, b in segs]
        mm, ma = np.median(masas), np.median(anchos)
        idx = [i for i in range(len(segs)) if masas[i] < 0.12 * mm or anchos[i] < 0.25 * ma]
        if not idx:
            break
        i = min(idx, key=lambda k: masas[k])
        # vecino más cercano
        izq = segs[i][0] - segs[i - 1][1] if i > 0 else 1e9
        der = segs[i + 1][0] - segs[i][1] if i < len(segs) - 1 else 1e9
        j = i - 1 if izq <= der else i + 1
        a, b = min(segs[i][0], segs[j][0]), max(segs[i][1], segs[j][1])
        segs[min(i, j)] = [a, b]
        del segs[max(i, j)]
    return segs


def agrupar_por_centro(fg, k):
    """Agrupa piezas (componentes) por su centro horizontal en k grupos (k-means 1D)."""
    lab, n = ndi.label(fg, structure=np.ones((3, 3)))
    if n < k:
        return None
    objs = ndi.find_objects(lab)
    masas = ndi.sum(fg, lab, range(1, n + 1))
    cx = np.array([ndi.center_of_mass(fg, lab, i)[1] for i in range(1, n + 1)])
    W = fg.shape[1]
    xs = fg.any(0).nonzero()[0]
    c = np.linspace(xs.min(), xs.max(), 2 * k + 1)[1::2]
    for _ in range(50):
        asig = np.argmin(np.abs(cx[:, None] - c[None, :]), 1)
        nc = np.array([np.average(cx[asig == j], weights=masas[asig == j]) if (asig == j).any() else c[j]
                       for j in range(k)])
        if np.allclose(nc, c):
            break
        c = nc
    if len(set(asig)) != k:
        return None
    grupos = []
    for j in range(k):
        ids = np.where(asig == j)[0]
        a = min(objs[i][1].start for i in ids)
        b = max(objs[i][1].stop for i in ids)
        grupos.append((a, b, set(ids + 1)))
    grupos.sort()
    gm = [masas[np.array(list(ids)) - 1].sum() for _, _, ids in grupos]
    if min(gm) < 0.3 * np.median(gm):
        return None
    # no se permiten solapes grandes
    for (a1, b1, _), (a2, b2, _) in zip(grupos, grupos[1:]):
        if a2 < b1 - 0.25 * (b1 - a1):
            return None
    return grupos, lab


def partes_iguales(fg, k):
    xs = fg.any(0).nonzero()[0]
    x0, x1 = xs.min(), xs.max() + 1
    prof = fg.sum(0)
    cortes = [x0]
    paso = (x1 - x0) / k
    for j in range(1, k):
        c = int(x0 + j * paso)
        r = int(paso * 0.12)
        ventana = prof[c - r:c + r + 1]
        c = c - r + int(np.argmin(ventana))  # afina al valle más cercano
        cortes.append(c)
    cortes.append(x1)
    return [[cortes[i], cortes[i + 1]] for i in range(k)]


def partir_valles(segs, fg, k):
    """Si hay menos segmentos que k, parte el más ancho en el valle de la proyección."""
    segs = [list(x) for x in segs]
    prof = ndi.uniform_filter1d(fg.sum(0).astype(float), 9)
    while 0 < len(segs) < k:
        anchos = [b - a for a, b in segs]
        i = int(np.argmax(anchos))
        a, b = segs[i]
        w = b - a
        tipico = (np.ptp(fg.any(0).nonzero()[0]) + 1) / k
        if w < 1.4 * tipico:
            return None
        n = max(2, round(w / tipico))
        lo, hi = a + int(w / n * 0.6), a + int(w / n * 1.4)
        c = lo + int(np.argmin(prof[lo:hi]))
        segs[i:i + 1] = [[a, c], [c, b]]
    return segs if len(segs) == k else None


def por_componentes(fg, k):
    """Cuando dos cuadros se enciman en x (p. ej. el cuadro acostado debajo del que cae):
    si hay exactamente k piezas grandes claramente separadas del resto, cada una es un cuadro;
    las piezas chicas se unen a la grande más cercana. Orden por centro x."""
    lab, n = ndi.label(fg, structure=np.ones((3, 3)))
    if n < k:
        return None
    masas = np.asarray(ndi.sum(fg, lab, range(1, n + 1)))
    orden = np.argsort(masas)[::-1]
    kth = masas[orden[k - 1]]
    sig = masas[orden[k]] if n > k else 0
    if kth < 0.25 * masas[orden[0]] or sig > 0.2 * kth:
        return por_componentes_humo(fg, lab, n, masas, orden, k)
    grandes = orden[:k] + 1
    cms = np.array(ndi.center_of_mass(fg, lab, list(grandes)))
    asign = {int(g): [int(g)] for g in grandes}
    for i in orden[k:] + 1:
        cm = np.array(ndi.center_of_mass(fg, lab, int(i)))
        j = int(np.argmin(((cms - cm) ** 2).sum(1)))
        asign[int(grandes[j])].append(int(i))
    orden_x = np.argsort(cms[:, 1])
    return [np.isin(lab, asign[int(grandes[o])]) for o in orden_x]


def por_componentes_humo(fg, lab, n, masas, orden, k):
    """k-1 piezas grandes + un cuadro hecho de piezas chicas (humo, polvo) fuera
    del rango horizontal de las grandes (p. ej. el último cuadro de golpe_morir)."""
    if n < k or k < 3:
        return None
    big = orden[:k - 1]
    if masas[big[-1]] < 0.25 * masas[orden[0]] or masas[orden[k - 1]] > 0.35 * masas[big[-1]]:
        return None
    objs = ndi.find_objects(lab)
    x0 = min(objs[i][1].start for i in big)
    x1 = max(objs[i][1].stop for i in big)
    resto = orden[k - 1:]
    fuera_d = [i for i in resto if objs[i][1].start >= x1]
    fuera_i = [i for i in resto if objs[i][1].stop <= x0]
    lados = [f for f in (fuera_d, fuera_i) if f and masas[f].sum() >= 0.02 * masas.sum()]
    if len(lados) != 1:
        return None
    fuera = lados[0]
    grupos = {int(g) + 1: [int(g) + 1] for g in big}
    nuevo = [int(i) + 1 for i in fuera]
    cms = np.array(ndi.center_of_mass(fg, lab, [int(g) + 1 for g in big]))
    for i in resto:
        if i in fuera:
            continue
        cm = np.array(ndi.center_of_mass(fg, lab, int(i) + 1))
        j = int(np.argmin(((cms - cm) ** 2).sum(1)))
        grupos[int(big[j]) + 1].append(int(i) + 1)
    lista = [(c[1], grupos[int(g) + 1]) for c, g in zip(cms, big)]
    cx_n = float(np.mean([ndi.center_of_mass(fg, lab, i)[1] for i in nuevo]))
    lista.append((cx_n, nuevo))
    lista.sort(key=lambda t: t[0])
    return [np.isin(lab, ids) for _, ids in lista]


def separar(fg, k):
    """-> (lista de máscaras de cuadro), metodo"""
    segs = unir_pequenos(segmentos_columnas(fg), fg)
    metodo = "proyeccion"
    if len(segs) < k:
        c = por_componentes(fg, k)
        if c:
            return c, "componentes"
        v = partir_valles(segs, fg, k)
        if v:
            segs, metodo = v, "valle"
    if len(segs) == k:
        masks = []
        for a, b in segs:
            m = np.zeros_like(fg)
            m[:, a:b] = fg[:, a:b]
            masks.append(m)
        return masks, metodo
    g = agrupar_por_centro(fg, k)
    if g:
        grupos, lab = g
        masks = [np.isin(lab, list(ids)) for _, _, ids in grupos]
        return masks, "centros"
    masks = []
    for a, b in partes_iguales(fg, k):
        m = np.zeros_like(fg)
        m[:, a:b] = fg[:, a:b]
        masks.append(m)
    return masks, "partes_iguales"


def bbox(m):
    ys, xs = np.nonzero(m)
    return ys.min(), ys.max() + 1, xs.min(), xs.max() + 1


# ---------------------------------------------------------------- color
def mascara_base(rgb):
    f = rgb.astype(np.float32)
    blanco = np.sqrt(((f - 255) ** 2).sum(-1)) < 40
    lab, _ = ndi.label(blanco)
    borde = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    return ~np.isin(lab, borde[borde > 0])


def paleta_de(px, n=32):
    px = px.reshape(-1, 3)
    if len(px) > 200000:
        px = px[np.random.default_rng(0).choice(len(px), 200000, replace=False)]
    im = Image.fromarray(px.reshape(1, -1, 3).astype(np.uint8), "RGB")
    q = im.quantize(colors=n, method=Image.Quantize.MEDIANCUT)
    pal = np.array(q.getpalette()[: 3 * n], dtype=np.float32).reshape(-1, 3)
    usados = np.unique(np.array(q))
    return pal[usados]


_PAL_CACHE = {}


def paleta_base(rel):
    if rel not in _PAL_CACHE:
        with Image.open(ruta(rel)) as im0:
            im = im0.copy()
        if im.mode == "RGBA":
            a = np.array(im)
            rgb = a[..., :3].copy()
            rgb[a[..., 3] < 128] = 255
        else:
            rgb = np.array(im.convert("RGB"))
        m = mascara_base(rgb)
        _PAL_CACHE[rel] = paleta_de(rgb[m])
    return _PAL_CACHE[rel]


def a_paleta(rgb, pal):
    """Mapea cada píxel al color más cercano. Devuelve (rgb_nuevo, distancia media)."""
    f = rgb.reshape(-1, 3).astype(np.float32)
    d = ((f[:, None, :] - pal[None, :, :]) ** 2).sum(-1)
    i = d.argmin(1)
    dist = np.sqrt(d[np.arange(len(f)), i])
    return pal[i].astype(np.uint8).reshape(rgb.shape), dist


# ---------------------------------------------------------------- escalado
def reducir(rgba, factor):
    im = Image.fromarray(rgba, "RGBA")
    w = max(1, round(im.width * factor))
    h = max(1, round(im.height * factor))
    im = im.resize((w, h), Image.Resampling.BOX)
    a = np.array(im)
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0, :3] = 0
    return a


def objetivo_estatura(job):
    if job["entidad"] in ("gordo", "conserje"):
        return 104
    return 96


def estatura_ref(alturas, escala):
    if escala == "frames_1_6_standing":
        sel = [alturas[i] for i in (0, 5) if i < len(alturas)]
        return float(np.mean(sel))
    if escala == "frame_1_standing":
        return float(alturas[0])
    return float(np.median(alturas))


# ---------------------------------------------------------------- por trabajo
def procesar_job(job):
    raw = ruta(job["salida_raw"])
    with Image.open(raw) as im0:
        rgb = np.array(im0.convert("RGB"))
    H, W = rgb.shape[:2]
    cat = job["categoria"]
    personaje = cat in ES_PERSONAJE
    fg = quitar_fondo(rgb, personaje)
    k = job["frames"]
    masks, metodo = separar(fg, k)
    cuadros = []
    for m in masks:
        if not m.any():
            cuadros.append(None)
            continue
        y0, y1, x0, x1 = bbox(m)
        sub = np.zeros((y1 - y0, x1 - x0, 4), np.uint8)
        sub[..., :3] = rgb[y0:y1, x0:x1]
        sub[..., 3] = np.where(m[y0:y1, x0:x1], 255, 0)
        sub[sub[..., 3] == 0, :3] = 0
        corta = bool(y0 <= 1 or x0 <= 1 or y1 >= H - 1 or x1 >= W - 1)
        cuadros.append({"rgba": sub, "bbox": [int(y0), int(y1), int(x0), int(x1)], "cortado": corta})
    vacios = sum(c is None for c in cuadros)
    cuadros_ok = [c for c in cuadros if c is not None]
    revisar = []
    if metodo == "partes_iguales":
        revisar.append("REVISAR: cuadros")
    if vacios:
        revisar.append("REVISAR: cuadros vacíos")
    info = {"id": job["id"], "metodo": metodo, "esperados": k,
            "segmentos_proyeccion": len(unir_pequenos(segmentos_columnas(fg), fg)),
            "detectados": len(cuadros_ok), "cortados": [i for i, c in enumerate(cuadros) if c and c["cortado"]],
            "alturas_hd": [int(c["rgba"].shape[0]) for c in cuadros_ok], "marcas": revisar}
    return cuadros_ok, info


def guardar_hd(job, cuadros, fg_sheet=None):
    d = HD / job["categoria"] / job["entidad"] / job["animacion"]
    d.mkdir(parents=True, exist_ok=True)
    for i, c in enumerate(cuadros):
        Image.fromarray(c["rgba"], "RGBA").save(d / f"{job['animacion']}_{i:02d}.png")


def escalar_y_colorear(job, cuadros, info):
    cat = job["categoria"]
    alturas = [c["rgba"].shape[0] for c in cuadros]
    if cat in ES_PERSONAJE:
        factor = objetivo_estatura(job) / estatura_ref(alturas, job["escala"])
    elif cat == "efectos":
        factor = 96 / max(max(c["rgba"].shape[:2]) for c in cuadros)
    else:
        factor = None  # objetos: por objeto
    pal = None
    if cat in ES_PERSONAJE:
        pal = np.concatenate([paleta_base(r) for r in job["referencias"]])
    out, dists = [], []
    for c in cuadros:
        a = c["rgba"]
        if cat == "objetos":
            lado = 32
            if job["animacion"] == "contenedores":
                lado = 48
            if job["animacion"] == "camion":
                f = 160 / a.shape[0]
            else:
                f = lado / max(a.shape[:2])
            s = reducir(a, f)
        else:
            s = reducir(a, factor)
        vis = s[..., 3] > 0
        if pal is not None:
            # distancia de color medida en HD (más fiable que en 96 px)
            hdm = a[..., 3] > 0
            px = a[..., :3][hdm]
            if len(px) > 20000:
                px = px[np.random.default_rng(1).choice(len(px), 20000, replace=False)]
            _, dd = a_paleta(px.reshape(-1, 1, 3), pal)
            dists.append(float(dd.mean()))
            orig = s[..., :3][vis].reshape(-1, 1, 3)
            nuevo, dd = a_paleta(orig, pal)
            nuevo = nuevo.reshape(-1, 3)
            lejos = dd > UMBRAL_PALETA  # colores nuevos (aura, armas, ojos): paleta propia
            if lejos.any():
                pl = paleta_de(orig.reshape(-1, 3)[lejos], 16)
                n2, _ = a_paleta(orig.reshape(-1, 3)[lejos].reshape(-1, 1, 3), pl)
                nuevo[lejos] = n2.reshape(-1, 3)
            s[..., :3][vis] = nuevo
        else:
            if vis.any():
                pal_l = paleta_de(s[..., :3][vis], 32)
                nuevo, _ = a_paleta(s[..., :3][vis].reshape(-1, 1, 3), pal_l)
                s[..., :3][vis] = nuevo.reshape(-1, 3)
        out.append(s)
    info["factor"] = factor
    info["dist_paleta"] = float(np.mean(dists)) if dists else None
    return out


def recorte(a):
    m = a[..., 3] > 0
    if not m.any():
        return a[:1, :1]
    y0, y1, x0, x1 = bbox(m)
    return a[y0:y1, x0:x1]


def centro_masa_x(a):
    m = a[..., 3] > 0
    return float(np.nonzero(m)[1].mean()) if m.any() else a.shape[1] / 2


def colocar_abajo(a, W, H, cx_lienzo):
    c = np.zeros((H, W, 4), np.uint8)
    h, w = a.shape[:2]
    x = int(round(cx_lienzo - centro_masa_x(a)))
    y = H - 2 - h
    c[y:y + h, x:x + w] = a
    return c


def colocar_centro(a, W, H):
    c = np.zeros((H, W, 4), np.uint8)
    h, w = a.shape[:2]
    y, x = (H - h) // 2, (W - w) // 2
    c[y:y + h, x:x + w] = a
    return c


def gif(frames, fps, dest, escala=4):
    dest.parent.mkdir(parents=True, exist_ok=True)
    imgs = []
    for a in frames:
        im = Image.fromarray(a, "RGBA")
        bg = Image.new("RGBA", im.size, GRIS_PREVIEW + (255,))
        bg.alpha_composite(im)
        bg = bg.convert("RGB").resize((im.width * escala, im.height * escala), Image.Resampling.NEAREST)
        imgs.append(bg)
    imgs[0].save(dest, save_all=True, append_images=imgs[1:], duration=int(round(1000 / (fps or 6))),
                 loop=0, disposal=2, optimize=False)


def tira(frames):
    H = max(f.shape[0] for f in frames)
    W = sum(f.shape[1] for f in frames)
    t = np.zeros((H, W, 4), np.uint8)
    x = 0
    for f in frames:
        t[:f.shape[0], x:x + f.shape[1]] = f
        x += f.shape[1]
    return t


def guardar_png(a, p):
    p.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(a, "RGBA").save(p)


# ---------------------------------------------------------------- principal
def procesar_grupo(cat, ent, js, atlas):
    print(f"== {cat}/{ent}: {len(js)} animaciones", flush=True)
    resultados = []
    for j in js:
        cuadros, info = procesar_job(j)
        if cat != "objetos":
            guardar_hd(j, cuadros)
        esc = escalar_y_colorear(j, cuadros, info)
        resultados.append((j, cuadros, esc, info))

    if cat == "objetos":
        for j, cuadros, esc, info in resultados:
            nombres = j["nombres"]
            if len(esc) != len(nombres):
                info["marcas"].append("REVISAR: cuadros")
            hd_dir = HD / "objetos" / j["animacion"]
            lista = {}
            for i, s in enumerate(esc):
                nom = nombres[i] if i < len(nombres) else f"extra_{i}"
                s = recorte(s)
                guardar_png(s, SPRITES / "objetos" / j["animacion"] / f"{nom}.png")
                guardar_png(cuadros[i]["rgba"], hd_dir / f"{nom}.png")
                lista[nom] = {"archivo": f"objetos/{j['animacion']}/{nom}.png", "tamano": [int(s.shape[1]), int(s.shape[0])]}
            atlas["objetos"][j["animacion"]] = lista
            # preview: cada objeto centrado en un lienzo común
            Wm = max(s.shape[1] for s in esc) + 4
            Hm = max(s.shape[0] for s in esc) + 4
            gif([colocar_centro(recorte(s), Wm, Hm) for s in esc], 2,
                PREVIEW / "objetos" / "objetos" / f"{j['animacion']}.gif")
            info["lienzo"] = [Wm, Hm]
            (PROC / f"{j['id']}.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
        return

    recortados = {j["id"]: [recorte(s) for s in esc] for j, _, esc, _ in resultados}
    if cat == "efectos":
        for j, cuadros, esc, info in resultados:
            fr = recortados[j["id"]]
            Wc = max(f.shape[1] for f in fr) + 4
            Hc = max(f.shape[0] for f in fr) + 4
            alineados = [colocar_centro(f, Wc, Hc) for f in fr]
            exportar(j, alineados, info, atlas, "center", [Wc, Hc])
        return

    # lienzo común por entidad, anclado abajo al centro de masa
    mitad = 0
    Hc = 0
    for fr in recortados.values():
        for f in fr:
            cx = centro_masa_x(f)
            mitad = max(mitad, cx, f.shape[1] - cx)
            Hc = max(Hc, f.shape[0])
    Wc = int(np.ceil(2 * mitad)) + 4
    Hc = Hc + 4
    for j, cuadros, esc, info in resultados:
        alineados = [colocar_abajo(f, Wc, Hc, Wc / 2) for f in recortados[j["id"]]]
        exportar(j, alineados, info, atlas, "bottom-center", [Wc, Hc])



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--entidades", nargs="*")
    a = ap.parse_args()
    jobs = cargar_manifest()
    PROC.mkdir(parents=True, exist_ok=True)
    grupos = defaultdict(list)
    for j in jobs:
        if not ruta(j["salida_raw"]).exists():
            continue
        if a.entidades and j["entidad"] not in a.entidades:
            continue
        clave = (j["categoria"], j["entidad"])
        grupos[clave].append(j)

    atlas_p = SPRITES / "atlas.json"
    atlas = json.loads(atlas_p.read_text(encoding="utf-8")) if atlas_p.exists() else {}
    atlas["notas"] = [
        "Ancla bottom-center: los pies quedan 2 px arriba del borde inferior del lienzo; efectos centrados.",
        "La izquierda es el espejo horizontal de caminar_lado, pegar_lado y atacar_lado (voltear el sprite en GDevelop).",
        "El cuadro 4 (índice 03) de caer_levantarse sirve como estado 'caído'.",
        "Todas las animaciones de una entidad comparten el mismo lienzo (excepto sus efectos).",
    ]
    atlas.setdefault("entidades", {})
    atlas.setdefault("objetos", {})

    import gc
    from revisar import clave_revision, hoja_contacto
    por_rev = defaultdict(list)
    for (cat, ent), js in grupos.items():
        por_rev[clave_revision(js[0])].append((cat, ent, js))
    for clave, subgrupos in por_rev.items():
        # una entidad a la vez: procesar, GIF, atlas y hoja de contacto antes de la siguiente
        for cat, ent, js in sorted(subgrupos, key=lambda t: t[0] == "efectos"):
            procesar_grupo(cat, ent, js, atlas)
            gc.collect()
        atlas_p.parent.mkdir(parents=True, exist_ok=True)
        atlas_p.write_text(json.dumps(atlas, ensure_ascii=False, indent=1), encoding="utf-8")
        todos = [j for _, _, js in subgrupos for j in js]
        hoja_contacto(clave, sorted(todos, key=lambda j: j["categoria"] == "efectos"))
        gc.collect()
        print(f"   hoja de contacto: {clave}", flush=True)
    atlas_p.parent.mkdir(parents=True, exist_ok=True)
    atlas_p.write_text(json.dumps(atlas, ensure_ascii=False, indent=1), encoding="utf-8")
    print("listo")


def exportar(j, alineados, info, atlas, ancla, lienzo):
    cat, ent, an = j["categoria"], j["entidad"], j["animacion"]
    d = SPRITES / cat / ent / an
    if d.exists():
        for p in d.glob("*.png"):
            p.unlink()
    nombres = []
    for i, f in enumerate(alineados):
        p = d / f"{an}_{i:02d}.png"
        guardar_png(f, p)
        nombres.append(f"{cat}/{ent}/{an}/{an}_{i:02d}.png")
    guardar_png(tira(alineados), d / f"{an}_tira.png")
    hd_d = HD / cat / ent / an
    hd_frames = []
    for p in sorted(hd_d.glob(f"{an}_[0-9][0-9].png")):
        with Image.open(p) as im0:
            hd_frames.append(np.array(im0))
    if hd_frames:
        guardar_png(tira(hd_frames), hd_d / f"{an}_tira.png")
    gif(alineados, j.get("fps"), PREVIEW / cat / ent / f"{an}.gif")
    clave = f"{cat}/{ent}"
    e = atlas["entidades"].setdefault(clave, {"categoria": cat, "entidad": ent, "animaciones": {}})
    e["lienzo"] = lienzo
    e["ancla"] = ancla
    e["animaciones"][an] = {"cuadros": nombres, "lienzo": lienzo, "ancla": ancla,
                            "fps": j.get("fps"), "loop": j.get("loop")}
    info["lienzo"] = lienzo
    (PROC / f"{j['id']}.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
