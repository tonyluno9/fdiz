# Sprites provisionales hechos en código (mismo estilo: contorno oscuro, sombreado plano)
import numpy as np
from PIL import Image, ImageDraw
SPR = '/mnt/user-data/uploads/fdiz/generado/sprites/'
OUT = '/home/claude/mapa_work/final/sprites_extra/'
import os; os.makedirs(OUT, exist_ok=True)
C = dict(contorno=(26, 29, 43), blanco=(244, 242, 236), blanco_s=(214, 210, 200), blanco_o=(186, 182, 172),
         verde=(47, 107, 74), verde_c=(70, 140, 100), verde_o=(33, 80, 55), junta=(30, 66, 46), gris=(120, 124, 132))

def rect(d, x0, y0, x1, y1, fill, outline=C['contorno']):
    d.rectangle([x0, y0, x1, y1], fill=fill, outline=outline)

# ---- barra en L de la nevería (tramo horizontal + vuelta hacia abajo a la izquierda) ----
def barra_L(W=320, brazo=150):
    top, frente, ancho_brazo = 22, 36, 30
    H = brazo + top + frente
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    # brazo vertical (solo se ve la cubierta y su frente abajo)
    rect(d, 0, 0, ancho_brazo, brazo + top, C['blanco'])
    d.line([2, 2, 2, brazo + top - 2], fill=(255, 255, 255))
    rect(d, 0, brazo + top, ancho_brazo, H - 1, C['verde'])
    for yy in range(brazo + top + 9, H - 2, 9): d.line([1, yy, ancho_brazo - 1, yy], fill=C['junta'])
    for xx in range(9, ancho_brazo, 9): d.line([xx, brazo + top + 1, xx, H - 2], fill=C['junta'])
    # tramo horizontal arriba
    rect(d, 0, 0, W - 1, top, C['blanco'])
    d.line([2, 2, W - 3, 2], fill=(255, 255, 255)); d.line([1, top - 3, W - 2, top - 3], fill=C['blanco_s'])
    rect(d, ancho_brazo, top, W - 1, top + frente, C['verde'])
    for yy in range(top + 9, top + frente, 9): d.line([ancho_brazo + 1, yy, W - 2, yy], fill=C['junta'])
    for xx in range(ancho_brazo + 9, W - 1, 9): d.line([xx, top + 1, xx, top + frente - 1], fill=C['junta'])
    d.line([ancho_brazo + 1, top + 1, W - 2, top + 1], fill=C['verde_c'])
    # recubre la esquina interior de la cubierta
    rect(d, 0, 0, ancho_brazo, top, C['blanco']); d.line([0, top, ancho_brazo, top], fill=C['blanco_s'])
    d.rectangle([0, 0, W - 1, top], outline=C['contorno'])
    im.save(OUT + 'neveria__barra_L.png'); return im

# ---- silla vista de espaldas (respaldo) en blanco o negro ----
def silla_espalda(col, sombra, nombre):
    im = Image.new('RGBA', (28, 42), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for x in (4, 22): d.rectangle([x, 22, x + 2, 41], fill=C['gris'], outline=C['contorno'])
    rect(d, 2, 18, 25, 24, sombra)
    rect(d, 3, 0, 24, 18, col); d.line([5, 3, 22, 3], fill=tuple(min(255, c + 25) for c in col))
    for yy in (7, 11): d.line([6, yy, 21, yy], fill=sombra)
    im.save(OUT + nombre + '.png'); return im

def recolor_negro(src, nombre):
    im = Image.open(src).convert('RGBA'); a = np.array(im).astype(np.float32)
    lum = a[..., :3].mean(-1, keepdims=True)
    dark = 18 + (lum / 255.0) * 70           # blanco -> gris oscuro
    a[..., :3] = np.where(a[..., 3:] > 0, np.concatenate([dark, dark, dark + 8], -1), a[..., :3])
    out = Image.fromarray(a.clip(0, 255).astype(np.uint8), 'RGBA'); out.save(OUT + nombre + '.png'); return out

def mesa(n_lugares, nombre):
    """mesa blanca cuadrada (1 o 2 juntas) alineada, con sillas atrás (de frente) y adelante (de espaldas)"""
    silla_f = Image.open(SPR + 'mapa/neveria/silla_blanca.png').convert('RGBA')
    silla_b = Image.open(OUT + 'silla_blanca_espalda.png').convert('RGBA')
    tw = 52 * n_lugares; W = tw + 8; H = 104
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    cols = [4 + 26 * (2 * i + 1) - 14 + (k * 0) for i in range(n_lugares) for k in (0,)]
    xs = []
    for i in range(n_lugares):
        xs += [4 + 52 * i + 6, 4 + 52 * i + 30]
    for x in xs: im.alpha_composite(silla_f, (x - 2, 0))
    # mesa
    y0 = 30
    for x in (6, W - 10): d.rectangle([x, y0 + 26, x + 3, y0 + 46], fill=C['blanco_o'], outline=C['contorno'])
    rect(d, 2, y0, W - 3, y0 + 26, C['blanco']); d.line([4, y0 + 2, W - 5, y0 + 2], fill=(255, 255, 255))
    rect(d, 2, y0 + 26, W - 3, y0 + 32, C['blanco_s'])
    if n_lugares == 2: d.line([W // 2, y0 + 1, W // 2, y0 + 31], fill=C['blanco_o'])
    for x in xs: im.alpha_composite(silla_b, (x - 2, H - 42))
    im.save(OUT + nombre + '.png'); return im

def carros():
    for k in ('pickup_blanca', 'sedan_rojo', 'suv_gris'):
        im = Image.open(SPR + f'mapa/estacionamiento/{k}.png').convert('RGBA')
        izq = im.rotate(90, expand=True)
        izq.save(OUT + f'estacionamiento__{k}_izq.png'); izq.transpose(Image.FLIP_LEFT_RIGHT).save(OUT + f'estacionamiento__{k}_der.png')
    cam = Image.open(SPR + 'objetos/camion/camion.png').convert('RGBA')
    cam = cam.resize((cam.width * 2, cam.height * 2), Image.NEAREST).rotate(90, expand=True)
    cam.save(OUT + 'camion_izq.png')

if __name__ == '__main__':
    barra_L()
    silla_espalda(C['blanco'], C['blanco_s'], 'silla_blanca_espalda')
    silla_espalda((48, 50, 58), (28, 30, 38), 'silla_negra_espalda')
    recolor_negro(SPR + 'mapa/neveria/silla_blanca.png', 'silla_negra_frente')
    mesa(1, 'neveria__mesa_4'); mesa(2, 'neveria__mesa_doble')
    carros()
    c = Image.new('RGBA', (900, 260), (120, 140, 115, 255)); x = 5
    for n in ('neveria__barra_L', 'neveria__mesa_4', 'neveria__mesa_doble', 'silla_negra_frente', 'silla_negra_espalda', 'silla_blanca_espalda', 'estacionamiento__sedan_rojo_izq'):
        im = Image.open(OUT + n + '.png'); c.alpha_composite(im, (x, 250 - im.height)); x += im.width + 10
    c.resize((1800, 520), Image.NEAREST).save('/tmp/extra.png')
