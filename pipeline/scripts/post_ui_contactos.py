from pathlib import Path
from PIL import Image, ImageDraw
R = Path(__file__).resolve().parents[2]
O = R/"generado/interfaz"
def hoja(items, dest, celda=160, cols=None):
    # items: (etiqueta, [paths])
    rows = []
    for et, ps in items:
        fr = [Image.open(p).convert("RGBA") for p in ps]
        rows.append((et, fr))
    n = max(len(f) for _, f in rows)
    W = 110 + n*celda; Hh = len(rows)*celda
    sh = Image.new("RGBA", (W, Hh), (60, 60, 80, 255)); d = ImageDraw.Draw(sh)
    for i, (et, fr) in enumerate(rows):
        d.text((4, i*celda+celda//2), et, fill=(255,255,255,255))
        for j, f in enumerate(fr):
            f.thumbnail((celda-6, celda-6), Image.LANCZOS)
            sh.paste(f, (110+j*celda+3, i*celda+3), f)
    sh.save(dest)
E = R/"generado/sprites/efectos"; it = []
for p in "tony miranda cesar alan castillo alessandro gabo carlos".split():
    for k in ("efecto_habilidad", "efecto_especial"):
        it.append((f"{p}/{k[7:]}", sorted((E/p/k).glob(f"{k}_0?.png"))))
hoja(it, O/"revision_efectos.png")
C = R/"generado/limpio_hd/personajes"; it = []
for p in "tony tonyfuerte miranda cesar alan castillo alessandro gabo carlos".split():
    it.append((p, sorted((C/p/"caminar_lado").glob("caminar_lado_0?.png"))))
hoja(it, O/"revision_caminar_lado.png", celda=200)
