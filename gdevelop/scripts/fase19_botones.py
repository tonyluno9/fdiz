"""Fase 19: quita la placa gris horneada de los botones de dificultad y los deja del mismo tamaño."""
import sys, os
from PIL import Image
base = sys.argv[1]  # carpeta assets/interfaz
TAM = (480, 168)
def limpiar(im):
    w, h = im.size
    px = im.load()
    def gris(p):
        r, g, b, a = p
        return a > 0 and abs(r-199) < 14 and abs(g-201) < 14 and abs(b-213) < 14
    # relleno por inundacion desde el centro
    ini = (w//2, h//2)
    mask = set([ini]); pila = [ini]
    while pila:
        x, y = pila.pop()
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            q = (x+dx, y+dy)
            if 0 <= q[0] < w and 0 <= q[1] < h and q not in mask and gris(px[q]):
                mask.add(q); pila.append(q)
    xs = [p[0] for p in mask]; ys = [p[1] for p in mask]
    x0, x1, y0, y1 = min(xs)-9, max(xs)+10, min(ys)-5, max(ys)+6
    for y in range(y0, y1):
        src = px[x0-1, y]
        if src[0] > 150 and src[2] > 150: src = px[x0-1, y0-1]
        for x in range(x0, x1):
            px[x, y] = src
    return im
out = {}
for n in ('facil', 'normal_dificultad', 'dificil'):
    im = Image.open(os.path.join(base, 'ui_boton_%s.png' % n)).convert('RGBA')
    im = limpiar(im)
    if n == 'normal_dificultad':
        im = im.crop((24, 22, im.width-24, im.height-20))
    else:
        im = im.crop(im.getbbox())
    im = im.resize(TAM, Image.NEAREST)
    f = os.path.join(base, 'ui_boton_%s_p19.png' % n)
    im.save(f); out[n] = f
c = Image.new('RGBA', (TAM[0], TAM[1]*3+20), (60, 60, 60, 255))
for i, n in enumerate(out):
    im = Image.open(out[n]); c.paste(im, (0, i*(TAM[1]+10)), im)
c.save(os.path.join(base, '..', '..', '..', '..', '_dbg', 'btns2.png'))
print('OK', out)
