"""Dibuja las dos imágenes de la pantalla de controles en estilo pixel art (con código, no con IA) con los controles vigentes:
teclado + ratón (712x320) y mando de Xbox (560x320). Guarda assets/interfaz/ctl_teclado_ia.png y ctl_mando_ia.png; luego correr fase49_arte.py."""
import os
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(AQUI, "..", "FDI-Z", "assets", "interfaz")
FUENTE = os.path.join(IMG, "fuentes", "PixelifySans.ttf")
BG, BORDE, LUZ, TXT = (42, 48, 70), (110, 150, 225), (176, 206, 255), (236, 240, 255)
OSC = (14, 16, 28)


def fuente(n): return ImageFont.truetype(FUENTE, n)


def panel(w, h):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 14, fill=BORDE)
    d.rounded_rectangle([4, 4, w - 5, h - 5], 11, fill=BG)
    return im, d


def tecla(d, x, y, w, h, txt, col, f):
    claro = tuple(min(255, c + 55) for c in col); osc = tuple(int(c * 0.6) for c in col)
    d.rounded_rectangle([x, y, x + w, y + h], 8, fill=OSC)
    d.rounded_rectangle([x + 3, y + 3, x + w - 3, y + h - 3], 6, fill=osc)
    d.rounded_rectangle([x + 3, y + 3, x + w - 3, y + h - 9], 6, fill=col)
    d.line([x + 8, y + 6, x + w - 8, y + 6], fill=claro, width=3)
    tw = d.textlength(txt, font=f)
    d.text((x + (w - tw) / 2, y + (h - 8) / 2 - 12), txt, font=f, fill=OSC if sum(col) > 520 else (255, 255, 255))


def texto(d, x, y, t, n=15, ancla="l", col=TXT):
    f = fuente(n); w = d.textlength(t, font=f)
    x0 = x if ancla == "l" else (x - w / 2 if ancla == "c" else x - w)
    d.text((x0, y), t, font=f, fill=col); return x0, x0 + w


def linea(d, pts, col=LUZ):
    for a, b in zip(pts, pts[1:]): d.line([a, b], fill=col, width=3)
    x, y = pts[-1]; d.rectangle([x - 3, y - 3, x + 3, y + 3], fill=col)


def teclado():
    W, H = 712, 320
    im, d = panel(W, H); f = fuente(26)
    gris, azul, mor, rojo, ver, ama = (200, 205, 220), (70, 140, 255), (170, 100, 245), (235, 80, 85), (70, 200, 110), (250, 205, 60)
    # fila 1
    tecla(d, 28, 70, 60, 54, "Esc", gris, fuente(22)); tecla(d, 118, 70, 52, 54, "Q", mor, f); tecla(d, 182, 70, 52, 54, "W", azul, f)
    tecla(d, 246, 70, 52, 54, "E", mor, f); tecla(d, 310, 70, 52, 54, "R", rojo, f); tecla(d, 400, 70, 52, 54, "P", gris, f)
    # fila 2
    for x, t, c in ((150, "A", azul), (214, "S", azul), (278, "D", azul), (342, "F", ver)): tecla(d, x, 134, 52, 54, t, c, f)
    tecla(d, 28, 212, 120, 54, "Shift", ama, fuente(24))
    # contorno MOVER alrededor de W A S D
    P = [(176, 62), (240, 62), (240, 128), (336, 128), (336, 196), (144, 196), (144, 128), (176, 128), (176, 62)]
    for a, b in zip(P, P[1:]): d.line([a, b], fill=LUZ, width=3)
    # rótulos teclado (cada línea toca solo su tecla)
    texto(d, 56, 36, "PAUSA", 15, "c"); linea(d, [(56, 54), (56, 70)])
    texto(d, 144, 36, "HABILIDAD", 15, "c"); linea(d, [(144, 54), (144, 70)])
    texto(d, 272, 36, "ESPECIAL", 15, "c"); linea(d, [(272, 54), (272, 70)])
    texto(d, 336, 12, "LANZAR", 15, "c"); linea(d, [(336, 30), (336, 70)])
    texto(d, 426, 36, "PAUSA", 15, "c"); linea(d, [(426, 54), (426, 70)])
    texto(d, 240, 204, "MOVER", 15, "c")
    texto(d, 368, 204, "USAR (MANTENER)", 15, "c"); linea(d, [(368, 188), (368, 202)])
    texto(d, 88, 274, "CORRER", 15, "c"); linea(d, [(88, 266), (88, 272)])
    # ratón
    cx = 570
    d.rounded_rectangle([cx - 62, 70, cx + 62, 232], 56, fill=OSC)
    d.rounded_rectangle([cx - 58, 74, cx + 58, 228], 52, fill=(52, 60, 88))
    d.rounded_rectangle([cx - 56, 76, cx - 3, 136], 34, fill=(255, 150, 40), corners=(True, False, False, False))
    d.rounded_rectangle([cx + 3, 76, cx + 56, 136], 34, fill=(235, 70, 75), corners=(False, True, False, False))
    d.rounded_rectangle([cx - 4, 90, cx + 4, 120], 4, fill=(190, 200, 220))
    d.line([cx - 56, 138, cx + 56, 138], fill=OSC, width=3)
    texto(d, cx, 240, "MOUSE", 34, "c")
    texto(d, cx - 30, 34, "PEGAR", 15, "c"); linea(d, [(cx - 30, 52), (cx - 30, 76)])
    texto(d, cx + 30, 34, "LANZAR", 15, "c"); linea(d, [(cx + 30, 52), (cx + 30, 76)])
    # cursor
    ax, ay = 662, 120
    d.polygon([(ax, ay), (ax, ay + 30), (ax + 8, ay + 23), (ax + 14, ay + 36), (ax + 20, ay + 33), (ax + 14, ay + 21), (ax + 25, ay + 21)], fill=(255, 255, 255), outline=OSC)
    texto(d, ax + 6, ay + 52, "APUNTAR", 15, "c")
    return im


def mando():
    W, H = 560, 320
    im, d = panel(W, H); dx = -10
    cuerpo, borde = (58, 66, 96), OSC
    # cuerpo
    for box in ([105 + dx, 100, 435 + dx, 215], ):
        d.rounded_rectangle([box[0] - 3, box[1] - 3, box[2] + 3, box[3] + 3], 40, fill=borde)
    d.ellipse([92 + dx, 170, 200 + dx, 285], fill=borde); d.ellipse([340 + dx, 170, 448 + dx, 285], fill=borde)
    d.rounded_rectangle([108 + dx, 103, 432 + dx, 212], 38, fill=cuerpo)
    d.ellipse([97 + dx, 175, 195 + dx, 280], fill=cuerpo); d.ellipse([345 + dx, 175, 443 + dx, 280], fill=cuerpo)
    # bumpers
    d.rounded_rectangle([128 + dx, 78, 215 + dx, 98], 8, fill=(86, 96, 130), outline=borde, width=3)
    d.rounded_rectangle([325 + dx, 78, 412 + dx, 98], 8, fill=(86, 96, 130), outline=borde, width=3)
    texto(d, 171 + dx, 80, "LB", 15, "c"); texto(d, 368 + dx, 80, "RB", 15, "c")
    # logo + centro
    d.ellipse([256 + dx, 106, 284 + dx, 134], fill=(200, 210, 230), outline=borde, width=2)
    d.ellipse([228 + dx, 140, 248 + dx, 160], fill=(30, 36, 56), outline=borde, width=2)           # View
    d.rectangle([234 + dx, 145, 241 + dx, 152], outline=LUZ, width=2)
    d.ellipse([292 + dx, 140, 312 + dx, 160], fill=(30, 36, 56), outline=borde, width=2)           # Start / Menu
    for yy in (145, 150, 155): d.line([296 + dx, yy, 308 + dx, yy], fill=LUZ, width=2)
    # stick izq, cruceta, stick der
    def stick(cx, cy, letra):
        d.ellipse([cx - 27, cy - 27, cx + 27, cy + 27], fill=borde); d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=(40, 46, 70))
        d.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], fill=(70, 80, 112)); texto(d, cx, cy - 12, letra, 20, "c")
    stick(175 + dx, 152, "L"); stick(300 + dx, 200, "R")
    d.rectangle([208 + dx, 188, 252 + dx, 208], fill=(30, 36, 56), outline=borde, width=2); d.rectangle([220 + dx, 176, 240 + dx, 220], fill=(30, 36, 56), outline=borde, width=2)
    d.rectangle([222 + dx, 190, 238 + dx, 206], fill=(30, 36, 56))
    # botones de cara
    bx, by = 380 + dx, 150
    for (ox, oy, col, l) in ((0, -26, (250, 205, 60), "Y"), (0, 26, (70, 200, 110), "A"), (-26, 0, (70, 140, 255), "X"), (26, 0, (235, 80, 85), "B")):
        d.ellipse([bx + ox - 14, by + oy - 14, bx + ox + 14, by + oy + 14], fill=borde); d.ellipse([bx + ox - 11, by + oy - 11, bx + ox + 11, by + oy + 11], fill=col)
        texto(d, bx + ox, by + oy - 10, l, 17, "c", OSC)
    # rótulos
    texto(d, 14, 118, "MOVER", 15); linea(d, [(64, 126), (148 + dx, 140), (150 + dx, 150)][:1] + [(66, 126), (148 + dx, 126), (152 + dx, 140)][1:2] + [(152 + dx, 140)])
    texto(d, 14, 158, "CORRER (CLIC)", 15); linea(d, [(120, 166), (155 + dx, 166), (160 + dx, 170)])
    texto(d, 14, 34, "CORRER (LB)", 15); linea(d, [(100, 42), (171 + dx, 42), (171 + dx, 78)])
    texto(d, 302 + dx, 12, "PAUSA", 15, "c"); linea(d, [(302 + dx, 30), (302 + dx, 140)])
    xl = 440
    texto(d, xl, 58, "ESPECIAL", 15); linea(d, [(xl - 4, 67), (416 + dx, 67), (416 + dx, 80)])
    texto(d, xl, 100, "HABILIDAD", 15); linea(d, [(xl - 4, 109), (bx + 16, 109), (bx + 6, 128)])
    texto(d, xl, 142, "LANZAR", 15); linea(d, [(xl - 4, 151), (bx + 42, 151)])
    texto(d, xl, 184, "USAR (MANTENER)", 15); linea(d, [(xl - 4, 193), (bx + 10, 193), (bx + 6, by + 36)])
    texto(d, bx - 26 + 8, 262, "PEGAR", 15, "l"); linea(d, [(bx - 26, by + 14), (bx - 26, 258)])
    texto(d, 300 + dx - 6, 262, "APUNTAR", 15, "r"); linea(d, [(300 + dx, 228), (300 + dx, 258)])
    return im


if __name__ == "__main__":
    teclado().save(os.path.join(IMG, "ctl_teclado_ia.png")); mando().save(os.path.join(IMG, "ctl_mando_ia.png")); print("OK")
