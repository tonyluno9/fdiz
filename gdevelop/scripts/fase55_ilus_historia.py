"""Fase 55 · Ilustración PROVISIONAL de la tarjeta HISTORIA del menú (mismo estilo plano que LOCAL y EN LÍNEA).

Uso (desde la carpeta fdiz):  python gdevelop/scripts/fase55_ilus_historia.py
Escribe gdevelop/FDI-Z/assets/interfaz/ilus_modo_historia.png (585 x 550, como las demás).
Dibujo: una lista de 5 pasos (los 2 primeros hechos, el 3.o es el actual). Si se hace arte final, basta con
reemplazar ese PNG con el mismo nombre y tamaño; no hace falta volver a correr fase55_historia.py.
"""
import os
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
INT = os.path.join(AQUI, "..", "FDI-Z", "assets", "interfaz")
BASE = os.path.join(INT, "ilus_modo_local.png")
DEST = os.path.join(INT, "ilus_modo_historia.png")

FONDO = (15, 25, 61, 255)
PANEL = (18, 60, 90, 255)
BORDE = (150, 180, 240, 255)
TENUE = (70, 90, 140, 255)
VERDE = (60, 190, 110, 255)
AMARILLO = (245, 200, 60, 255)
BLANCO = (235, 240, 255, 255)


def main():
    im = Image.open(BASE).convert("RGBA")
    W, H = im.size
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([16, 16, W - 17, H - 17], radius=26, fill=FONDO)          # se conserva el marco del original
    # tabla con broche
    x0, y0, x1, y1 = 120, 70, W - 120, H - 50
    d.rounded_rectangle([x0, y0, x1, y1], radius=22, fill=PANEL, outline=BORDE, width=8)
    d.rounded_rectangle([W // 2 - 70, y0 - 22, W // 2 + 70, y0 + 26], radius=12, fill=AMARILLO)
    d.rounded_rectangle([W // 2 - 30, y0 - 34, W // 2 + 30, y0 - 10], radius=8, fill=AMARILLO)
    try:
        f = ImageFont.load_default(size=34)
    except TypeError:
        f = ImageFont.load_default()
    fila = (y1 - y0 - 70) / 5
    for i in range(5):
        cy = int(y0 + 60 + fila * i + fila / 2)
        cx = x0 + 62
        if i < 2:        # hechos
            d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], fill=VERDE)
            d.line([(cx - 13, cy + 1), (cx - 3, cy + 12), (cx + 15, cy - 11)], fill=BLANCO, width=8)
            barra = VERDE
        elif i == 2:     # actual
            d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], fill=AMARILLO)
            d.text((cx, cy), str(i + 1), font=f, fill=FONDO, anchor="mm")
            barra = AMARILLO
        else:            # siguientes
            d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], outline=TENUE, width=6)
            d.text((cx, cy), str(i + 1), font=f, fill=TENUE, anchor="mm")
            barra = TENUE
        largo = [0.95, 0.75, 0.9, 0.7, 0.85][i]
        d.rounded_rectangle([cx + 50, cy - 9, cx + 50 + int((x1 - cx - 90) * largo), cy + 9], radius=9, fill=barra)
    im.save(DEST)
    print("Escrito", os.path.relpath(DEST))


if __name__ == "__main__":
    main()
