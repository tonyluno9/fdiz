"""Arma GIFs animados (fondo transparente) a partir de generado/sprites/atlas.json.
Salida: RAIZ/animaciones_gif/<categoria>/<entidad>/<animacion>.gif (x3, sin suavizado)
Las animaciones de lado también salen volteadas como <animacion>_izquierda.gif.
Uso: python hacer_gifs.py [escala]"""
import json, os, sys
from PIL import Image
RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SPR = os.path.join(RAIZ, 'generado', 'sprites')
OUT = os.path.join(RAIZ, 'animaciones_gif')
ESC = int(sys.argv[1]) if len(sys.argv) > 1 else 3
LADO = ('caminar_lado', 'pegar_lado', 'atacar_lado', 'caminar_miedo_lado')

def to_gif_frame(im):
    im = im.convert('RGBA')
    a = im.getchannel('A')
    rgb = im.convert('RGB').quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    pal = rgb.getpalette()[:255 * 3] + [255, 0, 255]
    rgb.putpalette(pal)
    mask = a.point(lambda v: 255 if v < 128 else 0)
    rgb.paste(255, mask=mask)
    rgb.info['transparency'] = 255
    return rgb

def guardar(frames, dest, fps, loop, voltear=False):
    ims = []
    for f in frames:
        im = Image.open(f).convert('RGBA')
        if voltear: im = im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        im = im.resize((im.width * ESC, im.height * ESC), Image.Resampling.NEAREST)
        ims.append(to_gif_frame(im))
    d = max(20, int(1000 / (fps or 8)))
    dur = [d] * len(ims)
    if not loop: dur[-1] = 700  # pausa al final para ver bien las que no se repiten
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    ims[0].save(dest, save_all=True, append_images=ims[1:], duration=dur, loop=0, disposal=2, transparency=255, optimize=False)

atlas = json.load(open(os.path.join(SPR, 'atlas.json'), encoding='utf-8'))
n = 0
for clave, ent in atlas['entidades'].items():
    for anim, info in ent['animaciones'].items():
        frames = [os.path.join(SPR, c) for c in info['cuadros']]
        if not all(os.path.exists(f) for f in frames): print('falta', clave, anim); continue
        base = os.path.join(OUT, clave, anim)
        guardar(frames, base + '.gif', info.get('fps', 8), info.get('loop', True)); n += 1
        if anim in LADO:
            guardar(frames, base.replace('_lado', '_izquierda') + '.gif', info.get('fps', 8), info.get('loop', True), voltear=True); n += 1
print('GIFs creados:', n, 'en', OUT)
