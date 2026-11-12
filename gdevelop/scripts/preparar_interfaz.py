"""Prepara piezas derivadas de la interfaz (correr antes de fase13_interfaz.py):
- assets/interfaz/hud/ico128_<nombre>.png : cada icono_* ajustado a un cuadro de 128x128 (centrado, sin deformar)
- assets/interfaz/hud/vida.png, seg_on.png : relleno de la barra de vida y del segmento de infestación
- imprime la geometria de las ranuras del panel de infestacion."""
import os, sys, json
import numpy as np
from PIL import Image
base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "FDI-Z", "assets", "interfaz")
sal = os.path.join(base, "hud"); os.makedirs(sal, exist_ok=True)
n = 0
for f in sorted(os.listdir(base)):
    if f.startswith("icono_") and f.endswith(".png"):
        im = Image.open(os.path.join(base, f)).convert("RGBA")
        bb = im.getbbox()
        if bb: im = im.crop(bb)
        s = min(120 / im.width, 120 / im.height)
        im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
        lienzo = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
        lienzo.paste(im, ((128 - im.width) // 2, (128 - im.height) // 2), im)
        lienzo.save(os.path.join(sal, "ico128_" + f[len("icono_"):])); n += 1
# relleno de barra de vida (rojo) y segmento de infestación (verde tóxico), 16x16 con luz arriba y sombra abajo
def bloque(nombre, luz, medio, sombra):
    im = Image.new("RGBA", (16, 16), medio)
    px = im.load()
    for y in range(16):
        for x in range(16):
            px[x, y] = luz if y < 4 else (sombra if y >= 12 else medio)
    im.save(os.path.join(sal, nombre))
bloque("vida.png", (255, 90, 80, 255), (214, 48, 49, 255), (150, 25, 30, 255))
bloque("seg_on.png", (190, 255, 90, 255), (124, 252, 0, 255), (70, 170, 10, 255))
# geometria de las ranuras del panel de infestacion
im = np.array(Image.open(os.path.join(base, "hud_panel_infestacion.png")).convert("RGB")).astype(int)
H, W = im.shape[:2]
fila = im[H // 2]
claro = (fila.sum(axis=1) > 75)    # interior azul marino (28,31,59) ~ suma 118; bordes casi negros
runs, ini = [], None
for x in range(190, W - 5):
    if claro[x] and ini is None: ini = x
    if (not claro[x] or x == W - 6) and ini is not None:
        if x - ini > 40: runs.append((ini, x - 1))
        ini = None
col = im[:, (runs[0][0] + runs[0][1]) // 2] if runs else None
ys = [y for y in range(H) if im[y, (runs[0][0] + runs[0][1]) // 2].sum() > 75] if runs else []
print(json.dumps({"iconos": n, "ranuras_x": runs, "y": [min(ys), max(ys)] if ys else None, "W": W, "H": H}))
