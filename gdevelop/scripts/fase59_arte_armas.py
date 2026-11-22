"""Fase 59 · Arte y sonido de las armas de fuego (revólver tipo sheriff y escopeta). Solo Pillow + biblioteca estándar.

Uso (desde la carpeta fdiz):  python gdevelop/scripts/fase59_arte_armas.py
Escribe (no toca el proyecto; eso lo hace fase59_armas_fuego.py):
  generado/sprites/objetos/armas/pistola.png        revólver en el piso (42 x 30, pixel art, mismo contorno que las demás)
  generado/sprites/objetos/armas/escopeta.png       escopeta en el piso (32 x 32, reducida del ícono del HUD que ya existía)
  generado/sprites/objetos/lanzables/bala.png       bala del revólver (10 x 4)
  generado/sprites/objetos/lanzables/perdigon.png   perdigón de la escopeta (4 x 4)
  gdevelop/FDI-Z/assets/interfaz/hud/ico128_arma_revolver.png   ícono del HUD (el revólver x3, 128 x 128)
  gdevelop/FDI-Z/efectos/combate/revolver.wav y escopeta.wav    disparos (ruido + golpe grave, 8 bits, como los demás)
"""
import math, os, random, struct
from PIL import Image, ImageDraw

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
ARMAS = os.path.join(RAIZ, "generado", "sprites", "objetos", "armas")
LANZ = os.path.join(RAIZ, "generado", "sprites", "objetos", "lanzables")
HUD = os.path.join(RAIZ, "gdevelop", "FDI-Z", "assets", "interfaz", "hud")
SFX = os.path.join(RAIZ, "gdevelop", "FDI-Z", "efectos", "combate")

CONTORNO = (26, 20, 32, 255)
M_OSC, M_MED, M_CLA, M_BRI = (64, 68, 82, 255), (112, 118, 134, 255), (168, 174, 190, 255), (214, 220, 232, 255)
W_OSC, W_MED, W_CLA = (88, 50, 28, 255), (138, 84, 46, 255), (182, 118, 66, 255)
ORO, ORO_OSC = (222, 178, 62, 255), (160, 118, 34, 255)


def contorno(im):
    """Contorno de 1 px alrededor de lo dibujado (como el resto de los sprites)."""
    w, h = im.size
    px = im.load()
    marca = [(x, y) for y in range(h) for x in range(w) if px[x, y][3] == 0 and any(
        0 <= x + dx < w and 0 <= y + dy < h and px[x + dx, y + dy][3] > 0 and px[x + dx, y + dy] != CONTORNO
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    for p in marca:
        px[p] = CONTORNO
    return im


def revolver():
    """Revólver de vaquero/sheriff mirando a la derecha: cañón largo, tambor, martillo, cacha de madera con remate dorado."""
    im = Image.new("RGBA", (42, 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # cañón y varilla extractora
    d.rectangle([19, 8, 39, 10], fill=M_MED); d.line([19, 8, 39, 8], fill=M_BRI); d.line([19, 10, 39, 10], fill=M_OSC)
    d.rectangle([21, 11, 33, 11], fill=M_OSC); d.point((34, 11), fill=M_MED)
    d.point((38, 7), fill=M_CLA)                                       # mira
    # armazón
    d.polygon([(9, 7), (20, 7), (20, 13), (15, 14), (9, 13)], fill=M_MED); d.line([10, 7, 20, 7], fill=M_CLA)
    # tambor con estrías
    d.rectangle([12, 6, 18, 12], fill=M_CLA)
    for x in (13, 15, 17):
        d.line([x, 7, x, 11], fill=M_OSC)
    d.line([12, 6, 18, 6], fill=M_BRI)
    # martillo (amartillado)
    d.polygon([(9, 7), (11, 7), (9, 4), (7, 3), (6, 4)], fill=M_OSC); d.point((7, 3), fill=M_MED)
    # guardamonte y gatillo
    d.arc([12, 11, 18, 17], 0, 180, fill=M_OSC); d.line([15, 13, 14, 15], fill=M_MED)
    # cacha (empuñadura curva) de madera
    d.polygon([(9, 12), (15, 13), (13, 18), (11, 24), (5, 25), (4, 22), (6, 16)], fill=W_MED)
    d.line([6, 16, 4, 22], fill=W_CLA); d.line([10, 14, 7, 21], fill=W_CLA)
    d.line([13, 18, 11, 24], fill=W_OSC); d.line([12, 15, 9, 22], fill=W_OSC)
    d.point((9, 17), fill=ORO)                                         # tornillo
    d.rectangle([4, 25, 11, 26], fill=ORO); d.line([4, 26, 11, 26], fill=ORO_OSC)   # remate dorado
    d.point((20, 9), fill=ORO)                                         # detalle de sheriff
    return contorno(im)


def escopeta_piso():
    """Del ícono que ya existía (128 x 128, dibujado a x4): muestreo en el centro de cada píxel -> 32 x 32."""
    ic = Image.open(os.path.join(HUD, "ico128_arma_escopeta.png")).convert("RGBA")
    out = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    for y in range(32):
        for x in range(32):
            p = ic.getpixel((x * 4 + 2, y * 4 + 2))
            out.putpixel((x, y), p if p[3] >= 128 else (0, 0, 0, 0))
    return out


def bala():
    im = Image.new("RGBA", (10, 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 9, 3], fill=CONTORNO); d.rectangle([1, 1, 6, 2], fill=ORO); d.rectangle([7, 1, 8, 2], fill=(240, 220, 150, 255))
    return im


def perdigon():
    im = Image.new("RGBA", (4, 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([0, 0, 3, 3], fill=CONTORNO); d.point((1, 1), fill=M_BRI); d.point((2, 1), fill=M_CLA); d.point((1, 2), fill=M_CLA); d.point((2, 2), fill=M_MED)
    return im


def icono(im):
    k = 3
    g = im.resize((im.width * k, im.height * k), Image.NEAREST)
    out = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    out.alpha_composite(g, ((128 - g.width) // 2, (128 - g.height) // 2))
    return out


# ------------------------------------------------------------------ sonido (8 bits, como el resto)
def wav(ruta, x, sr=44100):
    pico = max(abs(v) for v in x) or 1
    x = [v / pico * 0.89 for v in x]                                   # -1 dBFS
    q = [round(v * 127) / 127 for v in x]                              # cuantización de 8 bits (estilo del juego)
    pcm = b"".join(struct.pack("<h", int(v * 32767)) for v in q)
    cab = b"RIFF" + struct.pack("<I", 36 + len(pcm)) + b"WAVE" + b"fmt " + struct.pack("<IHHIIHH", 16, 1, 1, sr, sr * 2, 2, 16) \
        + b"data" + struct.pack("<I", len(pcm))
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    open(ruta, "wb").write(cab + pcm)


def disparo(dur, f0, f1, ruido_dec, grave_dec, mezcla, semilla, cola=0.0):
    rnd = random.Random(semilla); sr = 44100; n = int(sr * dur); out = []; fase = 0.0; ant = 0.0
    for i in range(n):
        t = i / sr
        r = rnd.uniform(-1, 1); ant = ant * 0.55 + r * 0.45                # ruido un poco filtrado
        ruido = ant * math.exp(-t / ruido_dec)
        f = f1 + (f0 - f1) * math.exp(-t / 0.03)
        fase += 2 * math.pi * f / sr
        grave = (1 if math.sin(fase) >= 0 else -1) * 0.6 * math.exp(-t / grave_dec)   # pulso cuadrado que cae
        eco = cola * rnd.uniform(-1, 1) * math.exp(-t / 0.25) if t > 0.05 else 0
        out.append(ruido * mezcla + grave * (1 - mezcla) + eco)
    m = int(sr * 0.012)
    for i in range(m):
        out[-m + i] *= 1 - (i + 1) / m
    return out


def main():
    for p in (ARMAS, LANZ, HUD):
        os.makedirs(p, exist_ok=True)
    r = revolver()
    r.save(os.path.join(ARMAS, "pistola.png"))
    icono(r).save(os.path.join(HUD, "ico128_arma_revolver.png"))
    escopeta_piso().save(os.path.join(ARMAS, "escopeta.png"))
    bala().save(os.path.join(LANZ, "bala.png"))
    perdigon().save(os.path.join(LANZ, "perdigon.png"))
    wav(os.path.join(SFX, "revolver.wav"), disparo(0.42, 520, 70, 0.05, 0.09, 0.62, 7, cola=0.08))
    wav(os.path.join(SFX, "escopeta.wav"), disparo(0.62, 380, 45, 0.09, 0.16, 0.7, 11, cola=0.16))
    print("Arte y sonidos de las armas de fuego listos.")


if __name__ == "__main__":
    main()
