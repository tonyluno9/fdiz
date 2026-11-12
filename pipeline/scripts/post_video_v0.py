import subprocess, glob, os
import numpy as np
from PIL import Image
D = "C:/Users/Angel Perez/Downloads/fdiz/generado/interfaz/video/titulo"
FF = "ffmpeg"
raw = f"{D}/raw_kling_titulo.mp4"
os.makedirs(f"{D}/cuadros_crudos", exist_ok=True); os.makedirs(f"{D}/cuadros_pixel", exist_ok=True)
for f in glob.glob(f"{D}/cuadros_crudos/*.png"): os.remove(f)
subprocess.run([FF, "-y", "-loglevel", "error", "-i", raw, "-vf", "fps=10", f"{D}/cuadros_crudos/c_%02d.png"], check=True)
ent = Image.open(f"{D}/entrada_titulo.png").convert("RGB")
pal = ent.resize((480, 270), Image.BOX).quantize(colors=48, method=Image.Quantize.MEDIANCUT)
crudos = sorted(glob.glob(f"{D}/cuadros_crudos/*.png")); pix = []; cr = []
for i, p in enumerate(crudos):
    im = Image.open(p).convert("RGB"); cr.append(im)
    q = im.resize((480, 270), Image.BOX).quantize(palette=pal, dither=Image.Dither.NONE).convert("RGB")
    q.save(f"{D}/cuadros_pixel/titulo_{i:02d}.png"); pix.append(q)
n = len(pix)
cr[0].resize((960, round(960 * cr[0].height / cr[0].width))).save(f"{D}/_t.png")
cr_s = [c.resize((960, round(960 * c.height / c.width))) for c in cr]
cr_s[0].save(f"{D}/preview_crudo.gif", save_all=True, append_images=cr_s[1:], duration=100, loop=0)
big = [p.resize((1440, 810), Image.NEAREST) for p in pix]
big[0].save(f"{D}/preview_pixel.gif", save_all=True, append_images=big[1:], duration=100, loop=0)
os.remove(f"{D}/_t.png")
m = n // 2; W, H = 720, 405
def fit(i): return i.resize((W, H), Image.NEAREST)
c = Image.new("RGB", (W * 2, H * 2))
c.paste(fit(cr[0]), (0, 0)); c.paste(fit(pix[0].resize(cr[0].size, Image.NEAREST)), (W, 0))
c.paste(fit(cr[m]), (0, H)); c.paste(fit(pix[m].resize(cr[0].size, Image.NEAREST)), (W, H))
c.save(f"{D}/comparacion.png")
a = [np.asarray(p, dtype=np.float32) for p in pix]
d = lambda x, y: float(np.abs(x - y).mean())
cons = [d(a[i], a[i + 1]) for i in range(n - 1)]
print("cuadros", n, "size", pix[0].size, "mid", m)
print("costura ultimo-primero", round(d(a[-1], a[0]), 3), "consecutivos media", round(sum(cons) / len(cons), 3))
