import sys
from pathlib import Path
import numpy as np
from PIL import Image
from collections import deque
R = Path(__file__).resolve().parents[2]
OUT = R/"generado/interfaz/piezas"; GD = R/"gdevelop/FDI-Z/assets/interfaz"
OUT.mkdir(parents=True, exist_ok=True); GD.mkdir(parents=True, exist_ok=True)

def fondo_mask(a, tol):
    h, w = a.shape[:2]
    ref = a[0, 0, :3].astype(int)
    cand = (np.abs(a[:, :, :3].astype(int) - ref).max(axis=2) <= tol)
    vis = np.zeros((h, w), bool); dq = deque()
    for x in range(w):
        for y in (0, h-1):
            if cand[y, x] and not vis[y, x]: vis[y, x] = True; dq.append((y, x))
    for y in range(h):
        for x in (0, w-1):
            if cand[y, x] and not vis[y, x]: vis[y, x] = True; dq.append((y, x))
    while dq:
        y, x = dq.popleft()
        for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
            yy, xx = y+dy, x+dx
            if 0 <= yy < h and 0 <= xx < w and cand[yy, xx] and not vis[yy, xx]:
                vis[yy, xx] = True; dq.append((yy, xx))
    return vis

for n in "tony tonyfuerte miranda cesar alan castillo alessandro gabo carlos".split():
    im = Image.open(R/f"assetsimage/{n}.png").convert("RGBA"); a = np.array(im)
    bg = fondo_mask(a, 14)
    fg = ~bg
    from scipy import ndimage
    lab,nl = ndimage.label(fg)
    sz = ndimage.sum(fg,lab,range(1,nl+1)); fg = lab==(1+int(np.argmax(sz))); bg = ~fg
    ys, xs = np.where(fg); top = ys.min(); bot = ys.max(); H = bot - top
    # cabeza: filas del 12% superior
    hr = fg[top:top+int(H*0.12)]; hx = np.where(hr.any(axis=0))[0]
    cx = (hx.min()+hx.max())//2
    side = int(H*0.47)
    x0 = cx - side//2; y0 = top - int(side*0.03)
    for _ in range(4):
        near = ndimage.binary_dilation(bg, iterations=1) & ~bg & (a[:,:,:3].min(axis=2) >= 232)
        bg = bg | near
    a[bg, 3] = 0
    im2 = Image.fromarray(a)
    pad = Image.new("RGBA", (im.width+2*side, im.height+2*side), (0,0,0,0)); pad.paste(im2, (side, side))
    c = pad.crop((x0+side, y0+side, x0+side+side, y0+side+side)).resize((256,256), Image.NEAREST)
    c.save(OUT/f"retrato_{n}.png"); c.save(GD/f"retrato_{n}.png")
    if n == "tony":
        al = np.array(c); s = np.zeros_like(al); s[:,:,3] = np.where(al[:,:,3] > 0, 255, 0)
        s[:,:,:3] = 0
        Image.fromarray(s).save(OUT/"retrato_silueta.png"); Image.fromarray(s).save(GD/"retrato_silueta.png")
    print(n, side)
# hoja de contacto
nombres = "tony tonyfuerte miranda cesar alan castillo alessandro gabo carlos silueta".split()
sh = Image.new("RGBA", (256*5, 256*2), (90,90,120,255))
for i, n in enumerate(nombres):
    p = Image.open(OUT/f"retrato_{n}.png"); sh.paste(p, ((i%5)*256, (i//5)*256), p)
sh.save(R/"generado/interfaz/_contacto_retratos.png")
