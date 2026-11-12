"""Lote del mapa: recorta las hojas de props (varias piezas por imagen), quita el magenta,
las escala al tamaño del juego (personaje = 96 px) y arma una hoja de revisión.

Uso:
  python procesar_mapa.py                 # todas las hojas que ya tengan raw
  python procesar_mapa.py --ids mapa__salon mapa__cic
Salida:
  generado/sprites/mapa/<hoja>/<nombre>.png      (tamaño final del juego)
  generado/limpio_hd/mapa/<hoja>/<nombre>.png    (recorte en alta, sin escalar)
  generado/sprites/mapa/mapa_atlas.json
  generado/revision/mapa/<hoja>.png              (revisión, con un personaje para comparar escala)
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

RAIZ = Path(__file__).resolve().parents[2]
GEN = RAIZ / "generado"
MANIFEST = RAIZ / "pipeline" / "manifest_mapa.json"
# hojas donde el modelo no respetó el orden pedido: índice (en orden de corte) de cada nombre
ORDEN_MANUAL = {"mapa__hitos": [0, 2, 1, 3]}  # el corazón quedó arriba del arco chico

REF_PERSONAJE = GEN / "sprites" / "personajes" / "tony" / "caminar_abajo" / "caminar_abajo_00.png"


def mascara_fondo(rgb):
    f = rgb.astype(np.float32)
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    dist = np.sqrt((r - 255) ** 2 + g ** 2 + (b - 255) ** 2)
    magenta = (dist < 110) | ((r > 140) & (b > 140) & (g < 0.55 * np.minimum(r, b)) & (np.abs(r - b) < 70))
    # halo: orillas rosadas pegadas al fondo
    cerca = ndi.binary_dilation(magenta, iterations=2)
    halo = cerca & (r > 120) & (b > 110) & (g < 0.7 * np.minimum(r, b))
    return magenta | halo


def componentes(fg, n, filas):
    area_min = fg.size * 0.0008
    for it in (8, 5, 3, 12, 16):
        grupos = ndi.binary_dilation(fg, iterations=it)
        lab, k = ndi.label(grupos)
        objs = ndi.find_objects(lab)
        comps = []
        for i, sl in enumerate(objs, 1):
            m = (lab[sl] == i) & fg[sl]
            a = int(m.sum())
            if a >= area_min:
                comps.append({"id": i, "sl": sl, "area": a,
                              "cy": (sl[0].start + sl[0].stop) / 2, "cx": (sl[1].start + sl[1].stop) / 2})
        if len(comps) >= n:
            break
    # demasiadas piezas: unir las más pequeñas a su vecina más cercana
    lab_final = lab.copy()
    while len(comps) > n:
        comps.sort(key=lambda c: c["area"])
        p = comps.pop(0)
        vec = min(comps, key=lambda c: (c["cx"] - p["cx"]) ** 2 + (c["cy"] - p["cy"]) ** 2)
        lab_final[lab_final == p["id"]] = vec["id"]
        y0 = min(p["sl"][0].start, vec["sl"][0].start); y1 = max(p["sl"][0].stop, vec["sl"][0].stop)
        x0 = min(p["sl"][1].start, vec["sl"][1].start); x1 = max(p["sl"][1].stop, vec["sl"][1].stop)
        vec.update(sl=(slice(y0, y1), slice(x0, x1)), area=vec["area"] + p["area"], cy=(y0 + y1) / 2, cx=(x0 + x1) / 2)
    # orden: por filas y luego de izquierda a derecha
    if filas > 1 and len(comps) > 1:
        ys = sorted(c["cy"] for c in comps)
        gaps = [(ys[i + 1] - ys[i], i) for i in range(len(ys) - 1)]
        corte = (ys[max(gaps)[1]] + ys[max(gaps)[1] + 1]) / 2
        comps.sort(key=lambda c: (c["cy"] > corte, c["cx"]))
    else:
        comps.sort(key=lambda c: c["cx"])
    return comps, lab_final


def quitar_tinte(rgb, m):
    """Despill: pixeles con tinte magenta (orillas, mallas, vidrios) -> se les quita el magenta."""
    f = rgb.astype(np.int16)
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    t = (r - g > 50) & (b - g > 50) & (np.abs(r - b) < 70) & m
    k = np.minimum(r, b) - g
    f[..., 0] = np.where(t, r - k, r); f[..., 2] = np.where(t, b - k, b)
    return np.clip(f, 0, 255).astype(np.uint8)


def escalar(rgba, eje, px):
    w, h = rgba.size
    f = px / (h if eje == "alto" else w)
    nw, nh = max(1, round(w * f)), max(1, round(h * f))
    a = rgba.resize((nw, nh), Image.BOX)
    arr = np.array(a)
    arr[..., 3] = np.where(arr[..., 3] >= 128, 255, 0)
    rgb = Image.fromarray(arr[..., :3]).quantize(colors=40, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")
    out = np.dstack([np.array(rgb), arr[..., 3]])
    return Image.fromarray(out.astype(np.uint8), "RGBA")


def procesar(job, atlas):
    raw = RAIZ / job["salida_raw"]
    if not raw.exists():
        print(f"falta raw: {job['id']}"); return False
    hoja = job["animacion"]
    rgb = np.array(Image.open(raw).convert("RGB"))
    if job["escala"] == "textura":
        # 2x2: cortar cuadrantes por la línea magenta central y guardar en alta (las termino aparte)
        H, W = rgb.shape[:2]
        dest = GEN / "limpio_hd" / "mapa" / "texturas"; dest.mkdir(parents=True, exist_ok=True)
        fondo = mascara_fondo(rgb)
        for k, nom in enumerate(job["nombres"]):
            y0, x0 = (k // 2) * H // 2, (k % 2) * W // 2
            q = rgb[y0:y0 + H // 2, x0:x0 + W // 2]; fq = fondo[y0:y0 + H // 2, x0:x0 + W // 2]
            filas_ok = np.where((~fq).mean(1) > 0.9)[0]; cols_ok = np.where((~fq).mean(0) > 0.9)[0]
            if len(filas_ok) and len(cols_ok):
                q = q[filas_ok.min():filas_ok.max() + 1, cols_ok.min():cols_ok.max() + 1]
            Image.fromarray(q).save(dest / f"{nom}.png")
        print(f"OK  texturas -> {dest}"); return True
    fondo = mascara_fondo(rgb)
    fg = ~fondo
    fg = ndi.binary_opening(fg, iterations=1)
    n = len(job["nombres"])
    comps, lab = componentes(fg, n, job.get("filas", 1))
    if len(comps) != n:
        print(f"AVISO {job['id']}: encontré {len(comps)} piezas y se esperaban {n}; revisa la hoja de revisión")
    if job["id"] in ORDEN_MANUAL and len(comps) == n:
        comps = [comps[i] for i in ORDEN_MANUAL[job["id"]]]
    dhd = GEN / "limpio_hd" / "mapa" / hoja; dhd.mkdir(parents=True, exist_ok=True)
    dsp = GEN / "sprites" / "mapa" / hoja; dsp.mkdir(parents=True, exist_ok=True)
    piezas = []
    for nom, c in zip(job["nombres"], comps):
        sl = c["sl"]
        m = (lab[sl] == c["id"]) & fg[sl]
        m = ndi.binary_fill_holes(m) & ~fondo[sl] | m
        ys, xs = np.where(m)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        crop = rgb[sl][y0:y1, x0:x1]; mm = m[y0:y1, x0:x1]
        crop = quitar_tinte(crop, mm)
        rgba = Image.fromarray(np.dstack([crop, (mm * 255).astype(np.uint8)]), "RGBA")
        rgba.save(dhd / f"{nom}.png")
        eje, px = list(job["tamanos"][nom].items())[0]
        fin = escalar(rgba, eje, px)
        fin.save(dsp / f"{nom}.png")
        atlas[f"{hoja}/{nom}"] = {"archivo": f"mapa/{hoja}/{nom}.png", "tamano": list(fin.size), "ancla": "bottom-center"}
        piezas.append((nom, fin))
    revision(hoja, piezas)
    print(f"OK  {job['id']}: {len(piezas)} piezas")
    return True


def revision(hoja, piezas):
    ref = Image.open(REF_PERSONAJE).convert("RGBA") if REF_PERSONAJE.exists() else None
    todas = ([("personaje", ref)] if ref else []) + piezas
    W = sum(p.width for _, p in todas) + 24 * (len(todas) + 1)
    H = max(p.height for _, p in todas) + 40
    lienzo = Image.new("RGBA", (W, H), (150, 170, 140, 255))
    d = ImageDraw.Draw(lienzo)
    x = 24
    for nom, p in todas:
        lienzo.alpha_composite(p, (x, H - 22 - p.height))
        d.text((x, H - 16), nom[:14], fill=(20, 20, 20))
        x += p.width + 24
    lienzo = lienzo.resize((W * 2, H * 2), Image.NEAREST)
    dest = GEN / "revision" / "mapa"; dest.mkdir(parents=True, exist_ok=True)
    lienzo.save(dest / f"{hoja}.png")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--ids", nargs="*"); a = ap.parse_args()
    jobs = json.load(open(MANIFEST, encoding="utf-8"))["jobs"]
    if a.ids: jobs = [j for j in jobs if j["id"] in set(a.ids)]
    ap_path = GEN / "sprites" / "mapa" / "mapa_atlas.json"
    atlas = json.load(open(ap_path, encoding="utf-8")) if ap_path.exists() else {}
    for j in jobs:
        try:
            procesar(j, atlas)
        except Exception as e:
            print(f"ERR {j['id']}: {e}")
    ap_path.parent.mkdir(parents=True, exist_ok=True)
    json.dump(atlas, open(ap_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"atlas: {ap_path} ({len(atlas)} piezas)")


if __name__ == "__main__":
    main()
