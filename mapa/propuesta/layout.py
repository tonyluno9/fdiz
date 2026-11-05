# Borrador del mapa compacto FDI-Z (casillas de 32 px, personaje 96 px = 3 casillas)
import json, ast
from collections import Counter
from PIL import Image, ImageDraw, ImageFont

d = json.load(open('/home/claude/mapa_in/mapa_final.json'))
def rle(s, n):
    out = []
    for part in s.split(','):
        if not part: continue
        v, c = part.split('x'); out += [int(v)] * int(c)
    return out[:n]
OW, OH = d['mundo']['ancho_casillas'], d['mundo']['alto_casillas']
og = rle(d['mundo']['suelo_rle'], OW * OH)
oc = rle(d['mundo']['colision_rle'], OW * OH)

KX, KY = 0.33, 0.36          # compresion del campus (en alturas de personaje)
X0OLD, X0NEW = 295, 45       # el campus empieza donde termina el estacionamiento
NW, NH = 285, 172
def wx(x): return X0NEW + (x - X0OLD) * KX
def wy(y): return y * KY

# ---------- suelo ----------
G = {}  # tipos nuevos
FOREST, GRASS, ASPH, SIDEW, PLAZA, PATH, COURT, STREET, WALL, STAIRS, CURB, TACT = range(12)
oldmap = {0: FOREST, 1: GRASS, 2: ASPH, 3: SIDEW, 4: PLAZA, 5: PATH, 6: COURT, 7: PLAZA, 8: STREET, 9: WALL, 10: STAIRS, 11: CURB}
grid = [[FOREST] * NW for _ in range(NH)]
for Y in range(NH):
    for X in range(X0NEW, NW):
        ox = X0OLD + (X - X0NEW) / KX; oy = Y / KY
        cnt = Counter()
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                x = int(ox + dx); y = int(oy + dy)
                if 0 <= x < OW and 0 <= y < OH:
                    v = og[y * OW + x]
                    t = oldmap[v]
                    if oc[y * OW + x] and t not in (FOREST, WALL): t = FOREST if t == GRASS else t
                    cnt[t] += 1
        if cnt: grid[Y][X] = cnt.most_common(1)[0][0]
# estacionamiento compacto (diseñado a mano)
def fill(x0, y0, x1, y1, t):
    for Y in range(max(0, y0), min(NH, y1)):
        for X in range(max(0, x0), min(NW, x1)):
            grid[Y][X] = t
fill(0, 0, 4, NH, STREET)
fill(4, 66, 45, 134, ASPH)
fill(4, 64, 45, 66, WALL); fill(4, 134, 45, 136, WALL)
fill(4, 66, 5, 134, WALL); fill(4, 80, 5, 90, ASPH); fill(4, 110, 5, 120, ASPH)  # rejas entrada/salida
fill(41, 96, 49, 108, SIDEW)  # acceso peatonal al campus

# ---------- edificios ----------
rooms = []   # (x0,y0,x1,y1,nombre,tipo_piso)
walls = set(); doors = []; porches = []
def room(x0, y0, x1, y1, name, floor):
    """interior x0..x1-1; muros alrededor"""
    rooms.append((x0, y0, x1, y1, name, floor))
    for X in range(x0 - 1, x1 + 1):
        walls.add((X, y0 - 1)); walls.add((X, y1))
    for Y in range(y0 - 1, y1 + 1):
        walls.add((x0 - 1, Y)); walls.add((x1, Y))
def door(x, y, w, h, kind='normal'):
    doors.append((x, y, w, h, kind))
    for X in range(x, x + w):
        for Y in range(y, y + h): walls.discard((X, Y))
def porch(x0, y0, x1, y1): porches.append((x0, y0, x1, y1))

def fila_h(x, y, n, rw, rd, names, porch_side, floor='aula', extra=None):
    """salones en fila horizontal; porch_side 'N' o 'S' (pasillo exterior de 3)"""
    py = y if porch_side == 'N' else y + rd + 1
    ry = y + 4 if porch_side == 'N' else y + 1
    for i in range(n):
        rx = x + 1 + i * (rw + 1)
        room(rx, ry, rx + rw, ry + rd, names[i], floor)
    for i in range(n):
        rx = x + 1 + i * (rw + 1)
        dyw = ry - 1 if porch_side == 'N' else ry + rd
        door(rx + rw // 2 - 1, dyw, 2, 1)
    total = n * (rw + 1) + 1
    porch(x, py, x + total, py + 3)
def fila_v(x, y, n, rw, rd, names, porch_side, floor='aula'):
    px = x if porch_side == 'W' else x + rw + 1
    rx = x + 4 if porch_side == 'W' else x + 1
    for i in range(n):
        ry = y + 1 + i * (rd + 1)
        room(rx, ry, rx + rw, ry + rd, names[i], floor)
        dxw = rx - 1 if porch_side == 'W' else rx + rw
        door(dxw, ry + rd // 2 - 1, 1, 2)
    porch(px, y, px + 3, y + n * (rd + 1) + 1)

# E: ISC e ICA (4 salones, pasillo al norte)
fila_h(109, 70, 4, 14, 10, ['E-01', 'E-02', 'E-03', 'E-04 (inicio)', ], 'N')
# B sur y B norte (ITS e IE), pasillo al oeste, separacion (pasillo techado) entre ambos
fila_v(178, 86, 3, 10, 15, ['B-01', 'B-02', 'B-03'], 'W')
fila_v(178, 32, 3, 10, 15, ['B-04', 'B-05', 'B-06'], 'W')
# D: IM e IME + baños, pasillo al sur
fila_h(214, 14, 3, 13, 10, ['D-01', 'D-02', 'D-03'], 'S')
room(214 + 1 + 3 * 14, 15, 214 + 1 + 3 * 14 + 6, 25, 'WC H', 'bano'); door(214 + 1 + 3 * 14 + 2, 25, 2, 1)
room(214 + 1 + 3 * 14 + 7, 15, 214 + 1 + 3 * 14 + 13, 25, 'WC M', 'bano'); door(214 + 1 + 3 * 14 + 9, 25, 2, 1)
porch(214, 26, 214 + 3 * 14 + 15, 29)
# C: cubiculos de maestros (cruz de pasillos)
cx, cy = 211, 40
room(cx + 1, cy + 1, cx + 11, cy + 10, 'C-01 Cubículos', 'oficina'); room(cx + 15, cy + 1, cx + 25, cy + 10, 'C-02 Cubículos', 'oficina')
room(cx + 1, cy + 14, cx + 11, cy + 23, 'WC', 'bano'); room(cx + 15, cy + 14, cx + 25, cy + 23, 'Escaleras', 'pasillo')
room(cx + 12, cy + 1, cx + 14, cy + 23, '', 'pasillo'); room(cx + 1, cy + 11, cx + 25, cy + 13, '', 'pasillo')
for (a, b, w, h) in [(cx + 5, cy + 10, 2, 1), (cx + 19, cy + 10, 2, 1), (cx + 5, cy + 13, 2, 1), (cx + 19, cy + 13, 2, 1),
                     (cx + 11, cy + 4, 1, 2), (cx + 14, cy + 4, 1, 2), (cx + 11, cy + 17, 1, 2), (cx + 14, cy + 17, 1, 2),
                     (cx + 12, cy + 23, 2, 1), (cx + 12, cy, 2, 1), (cx, cy + 11, 1, 2), (cx + 25, cy + 11, 1, 2)]:
    door(a, b, w, h, 'cristal' if (b in (cy, cy + 23) or a in (cx, cx + 25)) else 'normal')
# F: CIC
fx, fy = 64, 43
room(fx + 1, fy + 1, fx + 19, fy + 11, 'Sala 1', 'lab'); room(fx + 1, fy + 12, fx + 19, fy + 22, 'Sala 2', 'lab')
room(fx + 53, fy + 1, fx + 71, fy + 11, 'Sala 3', 'lab'); room(fx + 53, fy + 12, fx + 71, fy + 22, 'Sala 4', 'lab')
room(fx + 20, fy + 1, fx + 30, fy + 8, 'Cubículos', 'oficina'); room(fx + 31, fy + 1, fx + 42, fy + 8, 'Oficina CIC', 'oficina')
room(fx + 43, fy + 1, fx + 52, fy + 8, 'SITE servidores', 'servidores')
room(fx + 20, fy + 9, fx + 52, fy + 22, 'CIC vestíbulo', 'pasillo')
door(fx + 19, fy + 5, 1, 2, 'electronica'); door(fx + 19, fy + 16, 1, 2, 'electronica'); door(fx + 52, fy + 5, 1, 2, 'electronica'); door(fx + 52, fy + 16, 1, 2, 'electronica')
door(fx + 24, fy + 8, 2, 1); door(fx + 36, fy + 8, 2, 1); door(fx + 47, fy + 8, 2, 1, 'restringida')
door(fx + 34, fy + 22, 4, 1, 'cristal')
# Neveria
nx, ny = 47, 36
room(nx + 1, ny + 1, nx + 15, ny + 8, 'Cocina', 'cocina'); room(nx + 1, ny + 9, nx + 15, ny + 40, 'NEVERÍA', 'cafeteria')
door(nx + 7, ny + 8, 2, 1); door(nx + 15, ny + 17, 1, 2, 'cristal'); door(nx + 15, ny + 30, 1, 2, 'cristal')
# baño junto a E
room(95, 73, 105, 82, 'Baño', 'bano'); door(105, 77, 1, 2)
# A: administrativas
ax, ay = 88, 132
room(ax + 1, ay + 1, ax + 11, ay + 31, 'Servicios Escolares', 'oficina')
for i, nm in enumerate(['Dirección', 'Subdirección', 'Secretaría', 'Contabilidad']):
    room(ax + 12 + i * 9, ay + 1, ax + 20 + i * 9, ay + 10, nm, 'madera' if i == 0 else 'oficina')
    door(ax + 15 + i * 9, ay + 10, 2, 1, 'restringida' if i == 0 else 'normal')
room(ax + 12, ay + 11, ax + 48, ay + 14, '', 'pasillo')
room(ax + 12, ay + 15, ax + 26, ay + 31, 'Sala de espera', 'oficina'); room(ax + 27, ay + 15, ax + 39, ay + 31, 'Sala de juntas', 'madera')
room(ax + 40, ay + 15, ax + 48, ay + 22, 'Archivo', 'oficina'); room(ax + 40, ay + 23, ax + 48, ay + 31, 'WC', 'bano')
door(ax + 18, ay + 14, 2, 1); door(ax + 32, ay + 14, 2, 1); door(ax + 43, ay + 14, 2, 1); door(ax + 43, ay + 22, 2, 1)
door(ax + 11, ay + 12, 1, 2); door(ax, ay + 20, 1, 3, 'cristal'); door(ax + 48, ay + 12, 1, 2, 'cristal')
# Conserjeria (restringida) junto a la cancha
room(152, 16, 162, 24, 'Conserjería', 'bodega'); door(156, 24, 2, 1, 'restringida')

# ---------- exteriores ----------
ext = d['mundo']['objetos_exteriores']
ext = ast.literal_eval(ext) if isinstance(ext, str) else ext
trees, tables, lamps = [], [], []
for o in ext:
    X, Y = wx(o['x']), wy(o['y'])
    if o['tipo'] == 'arbol' and all((X - a) ** 2 + (Y - b) ** 2 > 16 for a, b in trees): trees.append((X, Y))
    if o['tipo'] == 'mesa_metalica': tables.append((X, Y))
    if o['tipo'] == 'circulo' and all((X - a) ** 2 + (Y - b) ** 2 > 36 for a, b in lamps): lamps.append((X, Y))
specials = [  # (x,y,w,h,nombre,color)
    (117, 1, 33, 23, 'Cancha techada', (60, 110, 80)),
    (42, 97, 4, 10, 'Arco', (30, 45, 100)),
    (10, 92, 5, 20, 'CAMIÓN', (240, 190, 40)),
]

json.dump({'tile_px': 32, 'ancho': NW, 'alto': NH, 'grid': grid, 'rooms': rooms, 'walls': sorted(walls), 'doors': doors,
           'porches': porches, 'trees': trees, 'tables': tables, 'lamps': lamps, 'specials': specials},
          open('layout_borrador.json', 'w'))

# ---------- render ----------
COL = {FOREST: (32, 62, 34), GRASS: (104, 168, 76), ASPH: (78, 80, 88), SIDEW: (196, 186, 166), PLAZA: (214, 170, 120),
       PATH: (160, 158, 156), COURT: (60, 110, 80), STREET: (52, 52, 58), WALL: (150, 140, 120), STAIRS: (200, 200, 140), CURB: (205, 200, 190)}
FL = {'aula': (236, 228, 205), 'lab': (226, 230, 236), 'oficina': (232, 222, 198), 'servidores': (52, 56, 72), 'pasillo': (222, 214, 196),
      'bano': (190, 220, 232), 'cocina': (210, 210, 205), 'cafeteria': (240, 236, 226), 'madera': (176, 122, 72), 'bodega': (170, 160, 140)}
DC = {'normal': (240, 190, 30), 'cristal': (120, 200, 240), 'electronica': (60, 220, 120), 'restringida': (230, 50, 50)}
S = 6
im = Image.new('RGB', (NW * S, NH * S)); dr = ImageDraw.Draw(im)
for Y in range(NH):
    for X in range(NW):
        dr.rectangle([X * S, Y * S, X * S + S - 1, Y * S + S - 1], fill=COL[grid[Y][X]])
for (x0, y0, x1, y1) in porches: dr.rectangle([x0 * S, y0 * S, x1 * S - 1, y1 * S - 1], fill=(210, 204, 190))
for (x, y, w, h, n, c) in specials: dr.rectangle([x * S, y * S, (x + w) * S - 1, (y + h) * S - 1], fill=c, outline=(255, 255, 255))
for (x0, y0, x1, y1, n, f) in rooms: dr.rectangle([x0 * S, y0 * S, x1 * S - 1, y1 * S - 1], fill=FL[f])
for (X, Y) in walls: dr.rectangle([X * S, Y * S, X * S + S - 1, Y * S + S - 1], fill=(36, 40, 60))
for (x, y, w, h, k) in doors: dr.rectangle([x * S, y * S, (x + w) * S - 1, (y + h) * S - 1], fill=DC[k])
for (X, Y) in trees: dr.ellipse([(X - 1.5) * S, (Y - 1.5) * S, (X + 1.5) * S, (Y + 1.5) * S], fill=(30, 110, 40))
for (X, Y) in tables: dr.ellipse([(X - 1) * S, (Y - 1) * S, (X + 1) * S, (Y + 1) * S], fill=(150, 150, 160), outline=(60, 60, 70))
# lineas de estacionamiento
for r in range(3):
    yy = 72 + r * 22
    for c in range(8):
        xx = 8 + c * 4.3
        dr.line([xx * S, yy * S, xx * S, (yy + 6) * S], fill=(230, 230, 230), width=2)
try:
    f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 13)
    fb = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 18)
except Exception:
    f = fb = ImageFont.load_default()
def label(x, y, t, font=f, col=(20, 20, 30)):
    w = dr.textlength(t, font=font)
    dr.rectangle([x - w / 2 - 2, y - 9, x + w / 2 + 2, y + 9], fill=(255, 255, 255))
    dr.text((x - w / 2, y - 8), t, fill=col, font=font)
for (x0, y0, x1, y1, n, fl) in rooms:
    if n: label((x0 + x1) / 2 * S, (y0 + y1) / 2 * S, n)
for (x, y, w, h, n, c) in specials: label((x + w / 2) * S, (y + h / 2) * S, n)
for X, Y, t in [(28, 68, 'ESTACIONAMIENTO (final ¡Aguanten!)'), (141, 66, 'Edificio E'), (99, 40, 'Edificio F – CIC'), (186, 29, 'B'), (240, 11, 'Edificio D'),
                (224, 37, 'Edificio C'), (112, 129, 'Edificio A'), (85, 104, 'Explanada (horda + corazón)'), (160, 58, 'Mesas techadas'),
                (156, 112, 'Plaza hundida (mesas)'), (184, 82, 'pasillo techado'), (2, 85, 'reja')]:
    label(X * S, Y * S, t, fb)
# escala: personaje y pantalla 1920x1080 (60x34 casillas)
cx0, cy0 = 200, 120
dr.rectangle([cx0 * S, cy0 * S, (cx0 + 60) * S, (cy0 + 34) * S], outline=(255, 40, 200), width=3)
label((cx0 + 30) * S, (cy0 + 2) * S, 'lo que se ve en pantalla 1920×1080 (zoom 1)', f, (200, 0, 150))
dr.rectangle([(cx0 + 29) * S, (cy0 + 15) * S, (cx0 + 30) * S, (cy0 + 18) * S], fill=(255, 40, 200))
label((cx0 + 30) * S, (cy0 + 21) * S, 'personaje (96 px = 3 casillas)', f, (200, 0, 150))
for i in range(0, NW, 30): dr.line([i * S, 0, i * S, 4], fill=(255, 255, 255))
im.save('mapa_borrador.png'); print(im.size, len(rooms), len(doors), len(trees))
