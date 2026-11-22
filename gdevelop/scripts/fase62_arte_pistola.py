"""Fase 62 · Arte (placeholders) para usar las armas de fuego. Solo Pillow; se puede volver a correr (mismo resultado).

Uso (desde la carpeta fdiz):
    python gdevelop/scripts/fase62_arte_pistola.py
Genera, en generado/sprites/:
  * objetos/armas/mira.png         indicador de apuntado: mira hueca de 11 x 11 px (no tapa lo que hay debajo)
  * objetos/armas/pistolita.png    pistola pequeña de lado (13 x 8 px), la que se dibuja en la mano
  * <personaje>/pistola_lado/pistola_lado_00..02.png   y   <personaje>/pistola_abajo/pistola_abajo_00..02.png
    para cada personaje del objeto Sup que tenga pegar_lado y pegar_abajo (alumnos, Tony gym y profes).
    Base: el cuadro del brazo estirado de pegar_lado (1) y la guardia de frente de pegar_abajo (0), con la pistola en
    el puño; cuadro 1 = retroceso de 1 px y fogonazo. Son PLACEHOLDERS: mismo tamaño, origen y máscara que la base.
"""
import json, os
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
PRY = os.path.join(RAIZ, "gdevelop", "FDI-Z", "FDI-Z.json")
GEN = os.path.join(RAIZ, "generado", "sprites")

O = (20, 20, 30, 255)        # contorno (como el de los personajes)
S = (112, 118, 132, 255)     # corredera clara
B = (62, 66, 78, 255)        # cuerpo
G = (44, 40, 40, 255)        # cacha
M = (8, 8, 10, 255)          # boca del cañón
_ = None

PISTOLA_LADO = [             # apunta a la derecha; la cacha queda bajo el puño
    "OOOOOOOOOOOO.",
    "OSSSSSSSSSSSO",
    "OBBBBBBBBBBBO",
    "OOGGGOOOOOOO.",
    ".OGGGO.......",
    ".OGGGO.......",
    ".OOOOO.......",
    ".............",
]
PISTOLA_FRENTE = [           # de frente: se ve la boca del cañón
    "OOOOOO",
    "OSSSSO",
    "OBMMBO",
    "OBMMBO",
    "OBBBBO",
    "OOOOOO",
]
FOGONAZO = [                 # 5 x 5
    "..Y..",
    ".YWY.",
    "YWWWY",
    ".YWY.",
    "..Y..",
]
COL = {"O": O, "S": S, "B": B, "G": G, "M": M, "Y": (255, 200, 60, 255), "W": (255, 250, 220, 255)}


def dibujo(filas, col=None):
    col = col or COL
    im = Image.new("RGBA", (len(filas[0]), len(filas)), (0, 0, 0, 0))
    for y, f in enumerate(filas):
        for x, ch in enumerate(f):
            if ch in col:
                im.putpixel((x, y), col[ch])
    return im


def mira():
    # cruz hueca: cuatro marcas con contorno y un punto central; nada lleno en el medio
    im = Image.new("RGBA", (11, 11), (0, 0, 0, 0))
    W, K = (245, 245, 235, 255), O
    marcas = [((5, 0), (5, 2)), ((5, 8), (5, 10)), ((0, 5), (2, 5)), ((8, 5), (10, 5))]
    for (x0, y0), (x1, y1) in marcas:          # contorno
        for x in range(min(x0, x1) - 1, max(x0, x1) + 2):
            for y in range(min(y0, y1) - 1, max(y0, y1) + 2):
                if 0 <= x < 11 and 0 <= y < 11:
                    im.putpixel((x, y), K)
    for (x0, y0), (x1, y1) in marcas:          # relleno claro
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                im.putpixel((x, y), W)
    im.putpixel((5, 5), W)
    return im


def cuerpo(p):
    """Píxel del personaje (no el brillo amarillo del modo gym ni bordes semitransparentes)."""
    r, g, b, a = p
    return a >= 200 and not (r > 240 and g > 120 and b < 110)


def puno(im, y0f, y1f):
    """Punto más adelantado (a la derecha) del personaje entre esas alturas relativas: el puño."""
    xs_ = [x for x in range(im.width) for y in range(im.height) if cuerpo(im.getpixel((x, y)))]
    ys_ = [y for y in range(im.height) if any(cuerpo(im.getpixel((x, y))) for x in range(im.width))]
    bb = (min(xs_), min(ys_), max(xs_) + 1, max(ys_) + 1)
    h = bb[3] - bb[1]
    filas = []
    for y in range(bb[1] + int(h * y0f), bb[1] + int(h * y1f)):
        xs = [x for x in range(im.width) if cuerpo(im.getpixel((x, y)))]
        if xs:
            filas.append((max(xs), y))
    mx = max(x for x, _ in filas)
    ys = sorted(y for x, y in filas if x >= mx - 1)
    return mx, ys[len(ys) // 2]


def lado(base):
    fx, fy = puno(base, 0.22, 0.62)
    pis = dibujo(PISTOLA_LADO)
    cuadros = []
    for k, (dx, dy, fuego) in enumerate(((0, 0, False), (-1, -1, True), (0, 0, False))):
        im = Image.new("RGBA", base.size, (0, 0, 0, 0))
        px, py = fx - 5 + dx, fy - 2 + dy
        im.alpha_composite(pis, (max(0, px), max(0, py)))        # la pistola va DEBAJO: el puño tapa la cacha
        im.alpha_composite(base)
        if fuego:
            fl = dibujo(FOGONAZO)
            x = min(base.width - 5, px + pis.width)
            im.alpha_composite(fl, (x, max(0, py - 1)))
        cuadros.append(im)
    return cuadros


def piel(p):
    r, g, b, a = p
    return cuerpo(p) and r > g > b and r - b > 40 and r > 110


def puno_piel(im, y0f, y1f):
    """De frente (guardia): el puño derecho es la piel más a la derecha a la altura del pecho."""
    ys_ = [y for y in range(im.height) if any(cuerpo(im.getpixel((x, y))) for x in range(im.width))]
    top, h = min(ys_), max(ys_) - min(ys_)
    puntos = [(x, y) for y in range(top + int(h * y0f), top + int(h * y1f)) for x in range(im.width) if piel(im.getpixel((x, y)))]
    if not puntos:
        return puno(im, y0f, y1f)
    mx = max(x for x, _ in puntos)
    ys = sorted(y for x, y in puntos if x >= mx - 3)
    return mx, ys[len(ys) // 2]


def abajo(base):
    fx, fy = puno_piel(base, 0.3, 0.6)
    pis = dibujo(PISTOLA_FRENTE)
    cuadros = []
    for k, (dy, fuego) in enumerate(((0, False), (-1, True), (0, False))):
        im = base.copy()
        px, py = fx - 7, fy - 2 + dy
        im.alpha_composite(pis, (max(0, px), max(0, py)))        # de frente va ENCIMA de las manos
        if fuego:
            im.alpha_composite(dibujo(FOGONAZO), (max(0, px), min(base.height - 5, py + 4)))
        cuadros.append(im)
    return cuadros


def main():
    d = json.load(open(PRY, encoding="utf-8"))
    J = next(l for l in d["layouts"] if l["name"] == "Juego")
    res = {r["name"]: r["file"] for r in d["resources"]["resources"]}
    sup = next(o for o in J["objects"] if o["name"] == "Sup")
    anims = {a["name"]: a for a in sup["animations"]}
    os.makedirs(os.path.join(GEN, "objetos", "armas"), exist_ok=True)
    mira().save(os.path.join(GEN, "objetos", "armas", "mira.png"))
    dibujo(PISTOLA_LADO).save(os.path.join(GEN, "objetos", "armas", "pistolita.png"))
    hechos = []
    for nombre in sorted(anims):
        if not nombre.endswith("_pegar_lado"):
            continue
        pj = nombre[:-len("_pegar_lado")]
        if pj + "_pegar_abajo" not in anims:
            continue
        for dir_, fuente, idx, fn in (("lado", "_pegar_lado", 1, lado), ("abajo", "_pegar_abajo", 0, abajo)):
            sprites = anims[pj + fuente]["directions"][0]["sprites"]
            archivo = res[sprites[min(idx, len(sprites) - 1)]["image"]]
            ruta = os.path.normpath(os.path.join(RAIZ, "gdevelop", "FDI-Z", archivo))
            base = Image.open(ruta).convert("RGBA")
            carpeta = os.path.join(os.path.dirname(os.path.dirname(ruta)), "pistola_" + dir_)
            os.makedirs(carpeta, exist_ok=True)
            for k, im in enumerate(fn(base)):
                im.save(os.path.join(carpeta, "pistola_%s_%02d.png" % (dir_, k)))
        hechos.append(pj)
    print("Arte de la fase 62:", ", ".join(hechos))


if __name__ == "__main__":
    main()
