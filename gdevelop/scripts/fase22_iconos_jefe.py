#!/usr/bin/env python3
"""Fase 22: iconos de las 8 cartas del modo Jefe (assets/interfaz/jefe_icono_c1..c8.png, 96x96)."""
import os
from PIL import Image, ImageDraw
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, 'gdevelop', 'FDI-Z', 'assets', 'interfaz')
Z = os.path.join(ROOT, 'generado', 'sprites', 'zombies')
S = 96

def zom(tipo, h=78):
    im = Image.open(os.path.join(Z, tipo, 'caminar_abajo', 'caminar_abajo_00.png')).convert('RGBA')
    im = im.crop(im.getbbox())
    k = h / im.height
    return im.resize((max(1, round(im.width * k)), h), Image.NEAREST)

def canvas(): return Image.new('RGBA', (S, S), (0, 0, 0, 0))

def single(tipo, h=80):
    c = canvas(); z = zom(tipo, h)
    c.alpha_composite(z, ((S - z.width) // 2, S - z.height - 6)); return c

def horda(tipos, h):
    c = canvas(); n = len(tipos)
    for i, t in enumerate(tipos):
        z = zom(t, h)
        x = int(6 + i * (S - 12 - z.width) / max(1, n - 1)) if n > 1 else (S - z.width) // 2
        y = S - z.height - 4 - (6 if i % 2 else 0)
        c.alpha_composite(z, (x, y))
    return c

def pix(draw, rows, pal, ox=0, oy=0, k=4):
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in pal: draw.rectangle([ox + x * k, oy + y * k, ox + x * k + k - 1, oy + y * k + k - 1], fill=pal[ch])

def puerta():
    c = canvas(); d = ImageDraw.Draw(c)
    rows = ["..BBBBBBBBBBBB..", "..BDDDDDDDDDDB..", "..BDLLDDLLDDDB..", "..BDLLDDLLDDDB..", "..BDDDDDDDDDDB..",
            "..BDLLDDLLDDDB..", "..BDLLDDLLDDYB..", "..BDDDDDDDDYYB..", "..BDDDDDDDDYYB..", "..BDDDDDDDDDDB..",
            "..BDDDDDDDDDDB..", "..BDDDDDDDDDDB..", "..BBBBBBBBBBBB.."]
    pix(d, rows, {'B': (60, 38, 24, 255), 'D': (150, 98, 52, 255), 'L': (200, 150, 90, 255), 'Y': (255, 215, 60, 255)}, 0, 14, 6)
    pix(d, ["..KKKK..", ".K....K.", ".K....K.", "KKKKKKKK", "KYYYYYYK", "KYYKKYYK", "KYYKKYYK", "KKKKKKKK"],
        {'K': (30, 22, 10, 255), 'Y': (255, 215, 60, 255)}, 40, 40, 6)
    return c

def bombilla():
    c = canvas(); d = ImageDraw.Draw(c)
    rows = ["....GGGGGG....", "...GYYYYYYG...", "..GYYWWYYYYG..", ".GYYWWYYYYYYG.", ".GYYWYYYYYYYG.", ".GYYYYYYYYYYG.",
            ".GYYYYYYYYYYG.", "..GYYYYYYYYG..", "...GYYYYYYG...", "....GYYYYG....", "....SSSSSS....", "....DDDDDD....", "....SSSSSS....", ".....DDDD....."]
    pix(d, rows, {'G': (90, 80, 40, 255), 'Y': (255, 235, 120, 255), 'W': (255, 255, 230, 255), 'S': (150, 150, 160, 255), 'D': (90, 90, 105, 255)}, 6, 4, 6)
    d.line([10, 10, 86, 86], fill=(220, 40, 40, 255), width=9); d.line([86, 10, 10, 86], fill=(220, 40, 40, 255), width=9)
    return c

ICONS = [single('normal'), single('corredor'), single('griton'), single('gordo', 84),
         horda(['normal', 'normal', 'normal'], 58), puerta(), bombilla(),
         horda(['normal', 'corredor', 'gordo', 'griton', 'normal'], 54)]
for i, im in enumerate(ICONS, 1):
    im.save(os.path.join(OUT, f'jefe_icono_c{i}.png'))
print('iconos', len(ICONS))
