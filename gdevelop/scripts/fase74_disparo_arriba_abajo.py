"""FDI-Z · Fase 74 · Animaciones de disparo hacia arriba y hacia abajo desde las hojas de sprites (fondo verde).
Correr con GDevelop cerrado, después de la 73:
    python gdevelop/scripts/fase74_disparo_arriba_abajo.py

Fuentes: animaciones_gif/personajes/<pj>/*.jpg (4 cuadros por hoja, en 4 columnas iguales, fondo verde).
Se quita el verde, se recorta cada cuadro, se escala como los disparos de lado (98 px de alto, pies en el origen) y se
reemplaza la animación del Sup:
  tony     pistola_arriba (de espaldas)  · pistola_abajo (de frente)
  cesar    pistola_arriba · pistola_abajo
  miranda  escopeta_arriba · escopeta_abajo
  alan     pistola_arriba · pistola_abajo  (el AK-47 usa las animaciones de pistola)
Las demás (por ejemplo César con escopeta) siguen con el placeholder de la fase 73.
Cuadros en generado/sprites/personajes/<pj>/disparo_<arma>_<dir>/. Idempotente.
"""
import json
import os
import sys

from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import fase69_correcciones as F  # noqa: E402

RAIZ, PRY, GEN = F.RAIZ, F.PRY, F.GEN
GIFS = os.path.join(RAIZ, "animaciones_gif", "personajes")
HOJAS = {
    ("tony", "pistola", "arriba"): "tony/tony_disparar_adelante_pistola_hojasprite.jpg",
    ("tony", "pistola", "abajo"): "tony/tony_disparar_abajo_pistola_hojasprite.jpg",
    ("cesar", "pistola", "arriba"): "cesar/Man_shooting_pixel_art_sprite_0a326839.jpg",
    ("cesar", "pistola", "abajo"): "cesar/Crear_sprite_sheet_pixel_art_966c6061.jpg",
    ("miranda", "escopeta", "arriba"): "miranda/Woman_shooting_shotgun_pixel_art_b3acdbda.jpg",
    ("miranda", "escopeta", "abajo"): "miranda/Sprite_sheet_pixel_art_shooting_5da3b3d3.jpg",
    ("alan", "pistola", "arriba"): "alan/Crear_hoja_de_sprites_pixel_8c565758.jpg",
    ("alan", "pistola", "abajo"): "alan/Sprite_sheet_of_shooting_man_fbbbe42f.jpg",
}
COLUMNAS = 4


def sin_verde(im):
    """Fondo verde -> transparente (con margen para los bordes del JPG) y sin halo verde en las orillas."""
    im = im.convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if g > 110 and g > r + 45 and g > b + 45:
                px[x, y] = (0, 0, 0, 0)
            elif g > max(r, b):                                   # orilla con tinte verde: se quita el exceso
                px[x, y] = (r, max(r, b), b, 255)
    return im


def cuadros(ruta):
    hoja = sin_verde(Image.open(ruta))
    w = hoja.width // COLUMNAS
    out = []
    for k in range(COLUMNAS):
        c = hoja.crop((k * w, 0, (k + 1) * w, hoja.height))
        caja = c.getbbox()
        out.append(c.crop((0, caja[1], c.width, caja[3])) if caja else c)
    return out


def arte(pj, arma, dire, ruta):
    fr = cuadros(ruta)
    # misma escala para los 4 cuadros (la del primero) y pies alineados: anclas() da cabeza, pies y centro de las piernas
    top, pie, _ = F.anclas(fr[0])
    s = F.ALTO_CUERPO / (pie - top)
    carpeta = os.path.join(GEN, "personajes", pj, "disparo_%s_%s" % (arma, dire))
    os.makedirs(carpeta, exist_ok=True)
    nombres = []
    for k, f in enumerate(fr):
        _, pie_k, cx = F.anclas(f)
        g = f.resize((max(1, round(f.width * s)), max(1, round(f.height * s))), Image.LANCZOS)
        g.putalpha(g.getchannel("A").point(lambda v: 255 if v >= 110 else 0))
        lienzo = Image.new("RGBA", F.LIENZO, (0, 0, 0, 0))
        lienzo.alpha_composite(g, (round(F.ORIGEN[0] - cx * s), round(F.ORIGEN[1] - pie_k * s)))
        nombre = "disparo_%s_%s_%02d.png" % (arma, dire, k)
        lienzo.save(os.path.join(carpeta, nombre))
        nombres.append("personajes/%s/disparo_%s_%s/%s" % (pj, arma, dire, nombre))
    return nombres


def main():
    d = json.load(open(PRY, encoding="utf-8"))
    J = next(l for l in d["layouts"] if l["name"] == "Juego")
    sup = next(o for o in J["objects"] if o["name"] == "Sup")
    res = d["resources"]["resources"]
    nombres = {r["name"] for r in res}
    hechas = {}
    for (pj, arma, dire), hoja in HOJAS.items():
        imgs = arte(pj, arma, dire, os.path.join(GIFS, *hoja.split("/")))
        for im in imgs:
            if im not in nombres:
                res.append({"file": "../../generado/sprites/" + im, "kind": "image", "metadata": "", "name": im, "smoothed": False, "userAdded": True})
                nombres.add(im)
        nombre = "%s_%s_%s" % (pj, arma, dire)
        nueva = F.animacion(nombre, imgs)
        k = next((i for i, x in enumerate(sup["animations"]) if x["name"] == nombre), None)
        if k is None:
            sup["animations"].append(nueva)
        else:
            sup["animations"][k] = nueva
        hechas[nombre] = len(imgs)
    tmp = PRY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=2))
    os.replace(tmp, PRY)
    print("Fase 74 aplicada:", hechas)


if __name__ == "__main__":
    main()
