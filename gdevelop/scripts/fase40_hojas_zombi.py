"""Fase 40 · Hojas de sprites de los profes zombi -> GIF (Joel y Canepa).

Uso (desde la carpeta fdiz):  python gdevelop/scripts/fase40_hojas_zombi.py
Requiere solo Pillow. Después correr fase40_sprites_profes.py y fase40_profesores.py.

Lee las hojas de referencia (fondo blanco, cuadrícula de 4 columnas x 3 filas):
    animaciones_gif/profes_zombi/hojas/<profe>_caminar.jpg   fila 1 caminar de lado, fila 2 de espaldas, fila 3 de frente
    animaciones_gif/profes_zombi/hojas/<profe>_ataque.jpg    fila 1 ataque de lado, fila 2 golpe de arriba hacia abajo,
                                                             fila 3 golpe final y muerte (con humo)
y escribe un GIF por animación en animaciones_gif/profes_zombi/<profe>/ (fondo transparente), con los mismos
nombres que los de Justino: caminar_lado, caminar_arriba, caminar_abajo, atacar_lado, atacar_abajo y golpe_morir.
atacar_arriba no viene en las hojas: fase40_sprites_profes.py la deriva de caminar_arriba.

Correcciones de consistencia que aplica (ver BITACORA, Fase 40):
  - Joel camina mirando a la IZQUIERDA en su hoja; el juego espera la derecha (y voltea con FlipX): se voltea.
  - Restos de fondo blanco encerrados entre brazo y cuerpo (o junto a la cara) se vuelven transparentes.
  - Se quita el halo claro que deja el JPG alrededor del contorno.
"""
import os
from collections import deque
from PIL import Image

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ZG = os.path.join(RAIZ, "animaciones_gif", "profes_zombi")
HOJAS = os.path.join(ZG, "hojas")

# hoja -> filas (animación por fila); "voltear" = la hoja mira a la izquierda
HOJAS_PROFE = {
    "canepa": {"caminar": (["caminar_lado", "caminar_arriba", "caminar_abajo"], False),
               "ataque": (["atacar_lado", "atacar_abajo", "golpe_morir"], False)},
    "joel": {"caminar": (["caminar_lado", "caminar_arriba", "caminar_abajo"], True),
             "ataque": (["atacar_lado", "atacar_abajo", "golpe_morir"], False)},
}
# milisegundos por cuadro del GIF (solo para verlo; el juego usa ANIM_Z de fase40_profesores.py)
MS = {"caminar": 200, "atacar": 120, "golpe": 150}


def es_fondo_claro(p, thr=226):
    r, g, b = p[:3]
    return min(r, g, b) >= thr and max(r, g, b) - min(r, g, b) < 24


def vecinos(i, W, H):
    x, y = i % W, i // W
    if x > 0: yield i - 1
    if x < W - 1: yield i + 1
    if y > 0: yield i - W
    if y < H - 1: yield i + W


def componentes(mask, W, H):
    """Etiqueta componentes 4-conexos de mask (bytearray). Devuelve lista de listas de índices."""
    vis = bytearray(W * H)
    out = []
    for s in range(W * H):
        if mask[s] and not vis[s]:
            vis[s] = 1
            q = deque([s]); pts = []
            while q:
                i = q.popleft(); pts.append(i)
                for j in vecinos(i, W, H):
                    if mask[j] and not vis[j]:
                        vis[j] = 1; q.append(j)
            out.append(pts)
    return out


def segmentar(ruta):
    """Separa la hoja en cuadros {(fila, columna): imagen RGBA recortada}."""
    im = Image.open(ruta).convert("RGB")
    W, H = im.size
    px = im.load()
    claro = bytearray(W * H)
    blanco = bytearray(W * H)
    for y in range(H):
        for x in range(W):
            p = px[x, y]
            if es_fondo_claro(p):
                claro[y * W + x] = 1
                if min(p) >= 236: blanco[y * W + x] = 1
    bg = bytearray(W * H)
    for pts in componentes(claro, W, H):
        toca = any(i % W in (0, W - 1) or i // W in (0, H - 1) for i in pts)
        casi_blanco = sum(blanco[i] for i in pts) >= 0.6 * len(pts)
        # fondo: lo que toca el borde, huecos grandes o restos casi blancos encerrados
        if toca or len(pts) > 350 or (casi_blanco and len(pts) >= 12):
            for i in pts: bg[i] = 1
    # halo del JPG: píxeles claros pegados al fondo (2 pasadas)
    for _ in range(2):
        quitar = []
        for i in range(W * H):
            if not bg[i]:
                p = px[i % W, i // W]
                if min(p) >= 185 and max(p) - min(p) < 30 and any(bg[j] for j in vecinos(i, W, H)):
                    quitar.append(i)
        for i in quitar: bg[i] = 1
    fg = bytearray(1 - v for v in bg)
    comps = []
    for pts in componentes(fg, W, H):
        if len(pts) < 25:
            continue
        xs = [i % W for i in pts]; ys = [i // W for i in pts]
        comps.append((pts, min(xs), min(ys), max(xs) + 1, max(ys) + 1))
    # filas por proyección de las piezas grandes
    prof = [0] * H
    for pts, x0, y0, x1, y1 in comps:
        if len(pts) > 800:
            for y in range(y0, y1): prof[y] += 1
    filas = []; ini = None
    for y in range(H + 1):
        on = y < H and prof[y] > 0
        if on and ini is None: ini = y
        if not on and ini is not None:
            if y - ini > 80: filas.append((ini, y))
            ini = None
    celdas = {}
    for c in comps:
        pts, x0, y0, x1, y1 = c
        cy, cx = (y0 + y1) / 2, (x0 + x1) / 2
        f = min(range(len(filas)), key=lambda k: 0 if filas[k][0] <= cy <= filas[k][1]
                else min(abs(cy - filas[k][0]), abs(cy - filas[k][1])))
        celdas.setdefault((f, int(cx // (W / 4))), []).append(c)
    out = {}
    for rc, lst in celdas.items():
        X0 = min(c[1] for c in lst); Y0 = min(c[2] for c in lst)
        X1 = max(c[3] for c in lst); Y1 = max(c[4] for c in lst)
        o = Image.new("RGBA", (X1 - X0, Y1 - Y0), (0, 0, 0, 0))
        op = o.load()
        for pts, *_ in lst:
            for i in pts:
                x, y = i % W, i // W
                op[x - X0, y - Y0] = px[x, y] + (255,)
        out[rc] = o
    return out


def ancla_x(im, solo_pies):
    """Centro de masa horizontal (de todo el cuerpo o de la franja de los pies)."""
    a = im.split()[3].load()
    w, h = im.size
    y0 = int(h * 0.88) if solo_pies else 0
    tot = sx = 0
    for y in range(y0, h):
        for x in range(w):
            if a[x, y]:
                tot += 1; sx += x
    return sx / tot if tot else w / 2


def armar_gif(cuadros, anim, ruta):
    caminar = anim.startswith("caminar")
    anc = [ancla_x(c, not caminar) for c in cuadros]
    medio = max(max(a, c.width - a) for a, c in zip(anc, cuadros))
    W = int(2 * medio) + 8
    H = max(c.height for c in cuadros) + 4
    fr = []
    for a, c in zip(anc, cuadros):
        o = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        o.alpha_composite(c, (int(round(W / 2 - a)), H - 2 - c.height))
        fr.append(o)
    ms = MS[anim.split("_")[0]]
    fr[0].save(ruta, save_all=True, append_images=fr[1:], duration=ms, loop=0, disposal=2, optimize=False)


def main():
    for profe, hojas in HOJAS_PROFE.items():
        dest = os.path.join(ZG, profe)
        os.makedirs(dest, exist_ok=True)
        for hoja, (anims, voltear) in hojas.items():
            ruta = os.path.join(HOJAS, "%s_%s.jpg" % (profe, hoja))
            celdas = segmentar(ruta)
            for f, anim in enumerate(anims):
                cs = [celdas[(f, c)] for c in range(4) if (f, c) in celdas]
                if anim == "caminar_lado" and voltear:
                    cs = [c.transpose(Image.Transpose.FLIP_LEFT_RIGHT) for c in cs]
                armar_gif(cs, anim, os.path.join(dest, anim + ".gif"))
                print("%-7s %-15s %d cuadros" % (profe, anim, len(cs)))
    print("Listo. Ahora: python gdevelop/scripts/fase40_sprites_profes.py")


if __name__ == "__main__":
    main()
