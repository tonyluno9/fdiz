"""Fase 40 · Sprites de los profesores reclutables (Joel, Justino y Canepa).

Uso (desde la carpeta fdiz):  python gdevelop/scripts/fase40_sprites_profes.py
Requiere Pillow (pip install pillow). Idempotente: se puede correr varias veces.

1. Convierte los GIF de referencia de Joel y Justino (animaciones_gif/profes/<profe>/*.gif) en cuadros PNG
   recortados, escalados y anclados por los pies, igual que el resto de sprites:
       generado/sprites/profes/<profe>/<animacion>/<animacion>_NN.png
   Canepa ya tenía sus cuadros en generado/sprites/profes/canepa (no se tocan).
2. Genera los recursos TEMPORALES que faltan para los tres profes (marcados en LEEME_PROFES.md):
       caer_levantarse  -> el cuadro "quieto" se inclina hasta quedar acostado (no hay arte de caída).
       pegar_abajo      -> copia de pegar_lado (no hay arte de golpe hacia abajo).
   Solo se crean si la carpeta no existe, para no pisar arte real que se agregue después.
3. Versiones ZOMBI de cada profe:
       generado/sprites/zombies/profe_<profe>/<animacion>/<animacion>_NN.png
   con animaciones caminar_abajo, caminar_arriba, caminar_lado, atacar_lado, atacar_abajo, atacar_arriba y golpe_morir.
   Fuente: animaciones_gif/profes_zombi/<profe>/<animacion>.gif (Justino: GIF hechos a mano; Joel y Canepa:
   generados de sus hojas con fase40_hojas_zombi.py). Si hay GIF, siempre manda: se regenera la carpeta.
     - Se quitan cuadros repetidos (GIF con cuadros duplicados o grabados en video).
     - Escala: la estatura de un cuadro de referencia (de pie) queda en 96 px, como el profe humano.
     - Ancla: pies 2 px sobre el borde, centrados (al caminar, el centro del cuerpo; al atacar/morir, los pies).
     - atacar_arriba sin GIF: se deriva de caminar_arriba (se encoge y luego se estira hacia adelante, de espaldas).
     - caminar_izquierda / atacar_izquierda no se usan: el juego voltea "lado" (FlipX).
   Sin GIF (y sin PNG previos) se usa el profe teñido de verde (provisional).
   Después de cambiar o agregar cuadros, correr fase40_profesores.py para que el proyecto los lea.
"""
import os, sys, glob, shutil
from PIL import Image, ImageSequence, ImageEnhance

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
GIFS = os.path.join(RAIZ, "animaciones_gif", "profes")
ZGIFS = os.path.join(RAIZ, "animaciones_gif", "profes_zombi")
SPR = os.path.join(RAIZ, "generado", "sprites")

ALTO_PJ = 96          # estatura objetivo en px (Canepa mide ~96, los alumnos ~98)
LIENZO = (96, 112)    # lienzo común de Joel y Justino
PIE = 2               # los pies quedan 2 px arriba del borde inferior (como el resto)

# animación del juego -> GIF de origen
DESDE_GIF = {
    "quieto": "quieto", "caminar_lado": "caminar_lado", "caminar_abajo": "caminar_abajo",
    "caminar_arriba": "caminar_arriba", "pegar_lado": "pegar_lado", "pegar_arriba": "pegar_arriba",
}
# Los GIF "caminar_izquierda" y "pegar_izquierda" no hacen falta: el juego voltea "lado" (FlipX).
# justino/pegar_izquierda.gif está vacío (100 cuadros transparentes).


def cuadros_gif(ruta):
    im = Image.open(ruta)
    return [f.convert("RGBA") for f in ImageSequence.Iterator(im)]


def limpiar_alfa(im):
    """Alfa duro (pixel art): sin bordes semitransparentes."""
    r, g, b, a = im.split()
    a = a.point(lambda v: 255 if v >= 128 else 0)
    return Image.merge("RGBA", (r, g, b, a))


def centro_masa_x(im):
    a = im.split()[3]
    w, h = im.size
    px = a.load()
    tot = sx = 0
    for y in range(h):
        for x in range(w):
            if px[x, y]:
                tot += 1
                sx += x
    return sx / tot if tot else w / 2


def anclar(im, lienzo):
    """Recorta al contenido y lo pega en el lienzo: pies abajo, centro de masa al centro."""
    bb = im.getbbox()
    W, H = lienzo
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if not bb:
        return out
    c = im.crop(bb)
    x = int(round(W / 2 - centro_masa_x(c)))
    y = H - PIE - c.height
    out.alpha_composite(c, (max(0, min(W - c.width, x)), max(0, y)))
    return out


def convertir_gif(profe, anim, gif):
    fr = cuadros_gif(gif)
    fr = [f for f in fr if f.getbbox()]
    if not fr:
        print("  (vacío)", gif)
        return 0
    # escala por archivo: estatura mediana de sus cuadros -> ALTO_PJ
    altos = sorted(f.getbbox()[3] - f.getbbox()[1] for f in fr)
    esc = ALTO_PJ / altos[len(altos) // 2]
    dest = os.path.join(SPR, "profes", profe, anim)
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    os.makedirs(dest)
    for i, f in enumerate(fr):
        bb = f.getbbox()
        c = f.crop(bb)
        c = c.resize((max(1, round(c.width * esc)), max(1, round(c.height * esc))), Image.Resampling.BOX)
        c = limpiar_alfa(c)
        anclar(c, LIENZO).save(os.path.join(dest, "%s_%02d.png" % (anim, i)))
    return len(fr)


def png_de(profe, anim):
    return sorted(glob.glob(os.path.join(SPR, "profes", profe, anim, anim + "_[0-9][0-9].png")))


def caida(base, n=6):
    """Provisional: el cuadro quieto se inclina hacia un lado hasta quedar acostado."""
    W, H = base.size
    out = []
    for i in range(n):
        ang = 90 * min(1, i / 3.0)          # 0, 30, 60, 90, 90, 90
        r = base.rotate(ang, resample=Image.Resampling.NEAREST, expand=True)
        out.append(anclar(r, (max(W, r.width), H)) if ang else base.copy())
    # mismo lienzo para todos: el más ancho
    Wm = max(f.width for f in out)
    return [anclar(f, (Wm, H)) for f in out]


def faltantes(profe):
    """Recursos provisionales del aliado: caer_levantarse y pegar_abajo."""
    hecho = []
    d = os.path.join(SPR, "profes", profe, "caer_levantarse")
    if not png_de(profe, "caer_levantarse"):
        os.makedirs(d, exist_ok=True)
        base = Image.open(png_de(profe, "quieto")[0]).convert("RGBA")
        for i, f in enumerate(caida(base)):
            f.save(os.path.join(d, "caer_levantarse_%02d.png" % i))
        hecho.append("caer_levantarse")
    d = os.path.join(SPR, "profes", profe, "pegar_abajo")
    if not png_de(profe, "pegar_abajo"):
        os.makedirs(d, exist_ok=True)
        for i, p in enumerate(png_de(profe, "pegar_lado")):
            shutil.copy(p, os.path.join(d, "pegar_abajo_%02d.png" % i))
        hecho.append("pegar_abajo")
    return hecho


def verde(im):
    """Tinte zombi provisional: desatura y empuja a verde, conservando la silueta."""
    r, g, b, a = im.split()
    gris = ImageEnhance.Color(Image.merge("RGB", (r, g, b))).enhance(0.25)
    r, g, b = gris.split()
    r = r.point(lambda v: int(v * 0.70))
    g = g.point(lambda v: min(255, int(v * 0.95 + 40)))
    b = b.point(lambda v: int(v * 0.65))
    return Image.merge("RGBA", (r, g, b, a))


Z_DESDE = {"caminar_abajo": "caminar_abajo", "caminar_arriba": "caminar_arriba", "caminar_lado": "caminar_lado",
           "atacar_lado": "pegar_lado", "atacar_abajo": "pegar_abajo", "atacar_arriba": "pegar_arriba",
           "golpe_morir": "caer_levantarse"}


def zombi(profe):
    hecho = []
    base = os.path.join(SPR, "zombies", "profe_" + profe)
    for zan, src in Z_DESDE.items():
        d = os.path.join(base, zan)
        if glob.glob(os.path.join(d, "*.png")):
            continue  # ya hay arte (real o provisional): no se toca
        os.makedirs(d, exist_ok=True)
        for i, p in enumerate(png_de(profe, src)):
            verde(Image.open(p).convert("RGBA")).save(os.path.join(d, "%s_%02d.png" % (zan, i)))
        hecho.append(zan)
    leeme = os.path.join(base, "LEEME.txt")
    if not os.path.exists(leeme):
        open(leeme, "w", encoding="utf-8").write(
            "Lugar para el arte de %s convertido en zombi.\n"
            "Los PNG actuales son PROVISIONALES (sprite del profe teñido de verde, generado por fase40_sprites_profes.py).\n"
            "Para poner el arte real: reemplaza los PNG de cada carpeta (mismo nombre: <animacion>_00.png, _01.png...).\n"
            "Puede haber más o menos cuadros. Anclaje: pies abajo al centro (2 px sobre el borde inferior).\n"
            "Animaciones: caminar_abajo, caminar_arriba, caminar_lado (mirando a la derecha), atacar_lado, atacar_abajo,\n"
            "atacar_arriba y golpe_morir (no se repite). Luego, con GDevelop cerrado, corre:\n"
            "  python gdevelop/scripts/fase40_profesores.py\n" % profe.capitalize())
    return hecho


# ------------------------------------------------------------------ zombis desde GIF
Z_ANIMS = ["caminar_abajo", "caminar_arriba", "caminar_lado", "atacar_lado", "atacar_abajo", "atacar_arriba", "golpe_morir"]
# cuadro de referencia para la escala y la estatura que debe medir (un cuadro en el que está de pie)
Z_REF = {"caminar_abajo": ("mediana", ALTO_PJ), "caminar_arriba": ("mediana", ALTO_PJ),
         "caminar_lado": ("mediana", ALTO_PJ), "atacar_lado": ("ultimo", ALTO_PJ),
         "atacar_abajo": ("ultimo", ALTO_PJ), "atacar_arriba": ("ultimo", ALTO_PJ),
         "golpe_morir": ("primero", ALTO_PJ - 2)}   # al recibir el golpe ya está un poco encorvado
Z_MAX_CUADROS = 8


def cuadros_unicos(fr):
    """Quita duplicados: primero los consecutivos; si siguen siendo muchos (GIF de video), se queda con el ciclo
    que se repite y, si aún sobran, toma Z_MAX_CUADROS repartidos."""
    fr = [f for f in fr if f.getbbox()]
    out = []
    for f in fr:
        if not out or f.tobytes() != out[-1].tobytes():
            out.append(f)
    if len(out) > Z_MAX_CUADROS:
        cuenta = {}
        for f in out:
            k = f.tobytes()
            cuenta[k] = cuenta.get(k, 0) + 1
        vistos, ciclo = set(), []
        for f in out:
            k = f.tobytes()
            if cuenta[k] >= 2 and k not in vistos:
                vistos.add(k)
                ciclo.append(f)
        if len(ciclo) >= 3:
            out = ciclo
    if len(out) > Z_MAX_CUADROS:
        n = len(out)
        out = [out[int(i * n / Z_MAX_CUADROS)] for i in range(Z_MAX_CUADROS)]
    return out


def centro_pies_x(im):
    """Centro horizontal de la franja de los pies (12 % inferior)."""
    w, h = im.size
    return centro_masa_x(im.crop((0, int(h * 0.88), w, h)))


def lienzo_anim(cs, anclas):
    """Todos los cuadros de una animación en un lienzo común: ancla al centro, pies a PIE px del borde."""
    medio = max(max(a, c.width - a) for a, c in zip(anclas, cs))
    W = max(LIENZO[0], 2 * int(medio + 0.999) + 4)
    W += W % 2
    H = max(LIENZO[1], max(c.height for c in cs) + PIE + 2)
    out = []
    for a, c in zip(anclas, cs):
        o = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        o.alpha_composite(c, (int(round(W / 2 - a)), H - PIE - c.height))
        out.append(o)
    return out


def guardar(dest, anim, frames):
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    os.makedirs(dest)
    for i, f in enumerate(frames):
        f.save(os.path.join(dest, "%s_%02d.png" % (anim, i)))


def zombi_gif(profe, anim, gif):
    fr = cuadros_unicos([f.convert("RGBA") for f in ImageSequence.Iterator(Image.open(gif))])
    if not fr:
        return 0
    regla, alto = Z_REF[anim]
    hs = [f.getbbox()[3] - f.getbbox()[1] for f in fr]
    ref = {"mediana": sorted(hs)[len(hs) // 2], "ultimo": hs[-1], "primero": hs[0]}[regla]
    esc = alto / ref
    cs = []
    for f in fr:
        c = f.crop(f.getbbox())
        c = c.resize((max(1, round(c.width * esc)), max(1, round(c.height * esc))), Image.Resampling.BOX)
        cs.append(limpiar_alfa(c))
    caminar = anim.startswith("caminar")
    anclas = [centro_masa_x(c) if caminar else centro_pies_x(c) for c in cs]
    guardar(os.path.join(SPR, "zombies", "profe_" + profe, anim), anim, lienzo_anim(cs, anclas))
    return len(cs)


def zombi_atacar_arriba(profe):
    """Sin arte de ataque de espaldas: se toma caminar_arriba ya convertido, se encoge (preparación) y se estira
    hacia adelante (embestida), como el ataque de espaldas del conserje."""
    src = sorted(glob.glob(os.path.join(SPR, "zombies", "profe_" + profe, "caminar_arriba", "caminar_arriba_[0-9][0-9].png")))
    if not src:
        return 0
    pasos = [(0, 1.03, 0.95), (1, 0.97, 1.07), (2, 0.98, 1.04), (3, 1.0, 1.0)]   # (cuadro, ancho, alto)
    cs = []
    for i, sx, sy in pasos:
        f = Image.open(src[i % len(src)]).convert("RGBA")
        c = f.crop(f.getbbox())
        cs.append(c.resize((round(c.width * sx), round(c.height * sy)), Image.Resampling.NEAREST))
    guardar(os.path.join(SPR, "zombies", "profe_" + profe, "atacar_arriba"), "atacar_arriba",
            lienzo_anim(cs, [c.width / 2 for c in cs]))
    return len(cs)


def zombi_desde_gifs(profe):
    """Convierte animaciones_gif/profes_zombi/<profe>/*.gif. Devuelve {anim: origen} o None si no hay GIF."""
    d = os.path.join(ZGIFS, profe)
    if not glob.glob(os.path.join(d, "*.gif")):
        return None
    base = os.path.join(SPR, "zombies", "profe_" + profe)
    hecho = {}
    for anim in Z_ANIMS:
        g = os.path.join(d, anim + ".gif")
        if os.path.exists(g):
            hecho[anim] = "%s.gif (%d cuadros)" % (anim, zombi_gif(profe, anim, g))
    if "atacar_arriba" not in hecho and "caminar_arriba" in hecho:
        hecho["atacar_arriba"] = "derivado de caminar_arriba (%d cuadros)" % zombi_atacar_arriba(profe)
    if "atacar_abajo" not in hecho and "atacar_lado" in hecho:
        fs = sorted(glob.glob(os.path.join(base, "atacar_lado", "*.png")))
        guardar(os.path.join(base, "atacar_abajo"), "atacar_abajo", [Image.open(f).convert("RGBA") for f in fs])
        hecho["atacar_abajo"] = "copia de atacar_lado (%d cuadros)" % len(fs)
    falta = [a for a in Z_ANIMS if a not in hecho]
    lineas = "\n".join("  %-14s <- %s" % (a, o) for a, o in hecho.items())
    open(os.path.join(base, "LEEME.txt"), "w", encoding="utf-8").write(
        "Arte de %s convertido en zombi (generado por fase40_sprites_profes.py; no editar a mano).\n"
        "Fuente: animaciones_gif/profes_zombi/%s/<animacion>.gif\n\n%s\n%s\n"
        "Para cambiarlo: reemplaza el GIF y, con GDevelop cerrado, corre\n"
        "  python gdevelop/scripts/fase40_sprites_profes.py\n"
        "  python gdevelop/scripts/fase40_profesores.py\n"
        % (profe.capitalize(), profe, lineas,
           ("FALTAN (quedan provisionales, profe teñido de verde): " + ", ".join(falta)) if falta else ""))
    return hecho


def main():
    for profe in ("joel", "justino"):
        print(profe)
        for anim, g in DESDE_GIF.items():
            ruta = os.path.join(GIFS, profe, g + ".gif")
            if not os.path.exists(ruta):
                print("  falta GIF", ruta)
                continue
            n = convertir_gif(profe, anim, ruta)
            print("  %-15s %d cuadros" % (anim, n))
    for profe in ("joel", "justino", "canepa"):
        f = faltantes(profe)
        zg = zombi_desde_gifs(profe)
        if zg:
            print(profe, "zombi desde GIF:")
            for a, o in zg.items():
                print("  %-14s <- %s" % (a, o))
        z = zombi(profe)
        if f or z:
            print(profe, "provisionales:", f, "zombi:", z)
    print("Listo.")


if __name__ == "__main__":
    main()
