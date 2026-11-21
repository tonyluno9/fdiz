"""Retoca las imágenes de controles hechas con IA (ctl_*_ia_fuente.png, 1536x688) y deja ctl_teclado_ia.png / ctl_mando_ia.png para la fase 49. Idempotente.
Teclado: el corchete "MOVER" de arriba cubría W y E (E es el Especial) y el de abajo solo S y D. Se borra el de arriba y el de abajo pasa a decir
"MOVER (WASD)". El mando no se toca (ver nota de PEGAR en bitacora2.md)."""
import os, shutil
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(AQUI, "..", "FDI-Z", "assets", "interfaz")
FONDO = (39, 48, 67, 255)

tec = Image.open(os.path.join(IMG, "ctl_teclado_ia_fuente.png")).convert("RGBA")
assert tec.size == (1536, 688), tec.size
d = ImageDraw.Draw(tec)
for caja in ((408, 174, 528, 211),      # texto MOVER de arriba
             (352, 211, 533, 233),      # corchete, parte izquierda de la línea de ESPECIAL
             (541, 211, 596, 233)):     # corchete, parte derecha
    d.rectangle(caja, fill=FONDO)
d.rectangle((440, 506, 566, 546), fill=FONDO)                       # texto MOVER de abajo
f = ImageFont.truetype(os.path.join(IMG, "fuentes", "PixelifySans.ttf"), 34)
t = "MOVER (WASD)"; w = d.textlength(t, font=f)
d.text((503 - w / 2, 508), t, font=f, fill=(255, 255, 255, 255))
tec.save(os.path.join(IMG, "ctl_teclado_ia.png"))
shutil.copy(os.path.join(IMG, "ctl_mando_ia_fuente.png"), os.path.join(IMG, "ctl_mando_ia.png"))
print("OK retoque")
