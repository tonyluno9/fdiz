# FDI-Z · construye el mapa compacto: tiles procedurales (32 px), Tiled .tmj, colisiones, zonas, puertas y marcadores.
import json, ast, hashlib, os
from collections import Counter
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = '/home/claude/mapa_work/final'; os.makedirs(OUT, exist_ok=True)
T = 32
d = json.load(open('/home/claude/mapa_in/mapa_final.json'))
def rle(s, n):
    out = []
    for part in s.split(','):
        if part: v, c = part.split('x'); out += [int(v)] * int(c)
    return out[:n]
OW, OH = d['mundo']['ancho_casillas'], d['mundo']['alto_casillas']
og = rle(d['mundo']['suelo_rle'], OW * OH); oc = rle(d['mundo']['colision_rle'], OW * OH)
KX, KY, X0OLD, X0NEW = 0.33, 0.36, 295, 45
NW, NH = 274, 168
def wx(x): return X0NEW + (x - X0OLD) * KX
def wy(y): return y * KY

# ---------------- suelo base (deformación del mapa del compañero) ----------------
BOSQUE, PASTO, ASFALTO, BANQUETA, CONCRETO, CAMINO, CANCHA, CALLE, PIEDRA, ESCALON, TACTIL, TIERRA, CERCO = (
    'bosque', 'pasto', 'asfalto', 'banqueta', 'concreto', 'camino', 'cancha', 'calle', 'piedra', 'escalon', 'tactil', 'tierra', 'cerco')
oldmap = {0: BOSQUE, 1: PASTO, 2: ASFALTO, 3: BANQUETA, 4: CONCRETO, 5: CAMINO, 6: CANCHA, 7: CONCRETO, 8: CALLE, 9: BOSQUE, 10: ESCALON, 11: BANQUETA}
G = [[BOSQUE] * NW for _ in range(NH)]
for Y in range(NH):
    for X in range(X0NEW, NW):
        ox = X0OLD + (X - X0NEW) / KX; oy = Y / KY; cnt = Counter()
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                x, y = int(ox + dx), int(oy + dy)
                if 0 <= x < OW and 0 <= y < OH:
                    t = oldmap[og[y * OW + x]]
                    if oc[y * OW + x] and t == PASTO: t = BOSQUE
                    cnt[t] += 1
        if cnt: G[Y][X] = cnt.most_common(1)[0][0]
def fill(x0, y0, x1, y1, t):
    for Y in range(max(0, y0), min(NH, y1)):
        for X in range(max(0, x0), min(NW, x1)): G[Y][X] = t
# recorte de la plaza naranja grande de la derecha
fill(236, 32, NW, NH, BOSQUE); fill(206, 10, 273, 32, BANQUETA); fill(273, 0, NW, NH, BOSQUE)
fill(196, 92, 236, 150, CONCRETO)
fill(196, 150, 236, 152, BANQUETA)
# filtro de mayoría para quitar ruido
for _ in range(2):
    G2 = [r[:] for r in G]
    for Y in range(1, NH - 1):
        for X in range(1, NW - 1):
            c = Counter(G[Y + a][X + b] for a in (-1, 0, 1) for b in (-1, 0, 1))
            t, n = c.most_common(1)[0]
            if n >= 6: G2[Y][X] = t
    G = G2
# estacionamiento y calle
fill(0, 0, 4, NH, CALLE)
fill(4, 64, 45, 136, ASFALTO); fill(4, 62, 45, 64, CERCO); fill(4, 136, 45, 138, CERCO); fill(4, 64, 5, 136, CERCO)
fill(4, 82, 5, 90, ASFALTO); fill(4, 112, 5, 120, ASFALTO)   # reja de entrada (82-90) y salida (112-120)
fill(41, 96, 50, 108, BANQUETA)
fill(45, 62, 47, 140, BANQUETA)
# entrada principal (arco) por la calle de abajo
fill(4, 164, 100, NH, CALLE); fill(66, 106, 72, 164, BANQUETA); fill(60, 152, 78, 164, CONCRETO); fill(66, 160, 72, 164, TACTIL)
# cancha techada
fill(115, 0, 152, 26, BANQUETA); fill(117, 1, 150, 24, CANCHA)
# plaza del corazón (círculo de concreto)
CORAZON = (72, 103)
for Y in range(NH):
    for X in range(NW):
        if (X - CORAZON[0]) ** 2 + (Y - CORAZON[1]) ** 2 <= 30: G[Y][X] = CONCRETO
# plaza hundida: concreto con muro de piedra y escalones
PH = (146, 108, 170, 126)
fill(PH[0] - 1, PH[1] - 1, PH[2] + 1, PH[3] + 1, PIEDRA); fill(*PH, CONCRETO)
fill(PH[0] + 9, PH[1] - 1, PH[0] + 13, PH[1], ESCALON); fill(PH[2], PH[1] + 7, PH[2] + 1, PH[1] + 11, ESCALON); fill(PH[0] - 1, PH[1] + 7, PH[0], PH[1] + 11, ESCALON)
# mesas techadas junto al CIC
fill(141, 46, 172, 66, CONCRETO)
# franjas táctiles (rampas de acceso)
fill(41, 101, 50, 103, TACTIL); fill(PH[0] + 9, PH[1] - 2, PH[0] + 13, PH[1] - 1, TACTIL)

# ---------------- edificios ----------------
rooms, walls, doors, porches, pillars = [], set(), [], [], set()
def room(x0, y0, x1, y1, name, floor, zona=True):
    rooms.append(dict(x0=x0, y0=y0, x1=x1, y1=y1, nombre=name, piso=floor, zona=zona))
    for X in range(x0 - 1, x1 + 1): walls.add((X, y0 - 1)); walls.add((X, y1))
    for Y in range(y0 - 1, y1 + 1): walls.add((x0 - 1, Y)); walls.add((x1, Y))
def door(x, y, w, h, kind='normal'):
    doors.append(dict(x=x, y=y, w=w, h=h, tipo=kind))
def porch(x0, y0, x1, y1, cols=None):
    porches.append((x0, y0, x1, y1))
    if cols == 'N':
        for X in range(x0 + 2, x1 - 1, 6): pillars.add((X, y0))
    if cols == 'S':
        for X in range(x0 + 2, x1 - 1, 6): pillars.add((X, y1 - 1))
    if cols == 'W':
        for Y in range(y0 + 2, y1 - 1, 6): pillars.add((x0, Y))
def fila_h(x, y, n, rw, rd, names, side):
    ry = y + 4 if side == 'N' else y + 1
    for i in range(n):
        rx = x + 1 + i * (rw + 1); room(rx, ry, rx + rw, ry + rd, names[i], 'aula')
        door(rx + rw // 2 - 1, ry - 1 if side == 'N' else ry + rd, 2, 1)
    tot = n * (rw + 1) + 1
    porch(x, y, x + tot, y + 3, 'N') if side == 'N' else porch(x, y + rd + 2, x + tot, y + rd + 5, 'S')
def fila_v(x, y, n, rw, rd, names):
    rx = x + 4
    for i in range(n):
        ry = y + 1 + i * (rd + 1); room(rx, ry, rx + rw, ry + rd, names[i], 'aula'); door(rx - 1, ry + rd // 2 - 1, 1, 2)
    porch(x, y, x + 3, y + n * (rd + 1) + 1, 'W')

fila_h(109, 70, 4, 14, 10, ['E-01', 'E-02', 'E-03', 'E-04'], 'N')
fila_v(178, 86, 3, 10, 15, ['B-01', 'B-02', 'B-03'])
fila_v(178, 32, 3, 10, 15, ['B-04', 'B-05', 'B-06'])
fill(178, 81, 195, 86, BANQUETA)  # pasillo techado entre las dos mitades de B
# D
fila_h(214, 14, 3, 13, 10, ['D-01', 'D-02', 'D-03'], 'S')
room(257, 15, 263, 25, 'Baño H (D)', 'bano') if False else None
room(214 + 43, 15, 214 + 49, 25, 'Baño H', 'bano'); door(214 + 45, 25, 2, 1)
room(214 + 50, 15, 214 + 56, 25, 'Baño M', 'bano'); door(214 + 52, 25, 2, 1)
fill(214, 26, 214 + 57, 30, BANQUETA); porch(214, 26, 214 + 57, 29, 'S')
# C
cx, cy = 211, 40
room(cx + 1, cy + 1, cx + 11, cy + 10, 'C-01 Cubículos', 'oficina'); room(cx + 15, cy + 1, cx + 25, cy + 10, 'C-02 Cubículos', 'oficina')
room(cx + 1, cy + 14, cx + 11, cy + 23, 'Baños C', 'bano'); room(cx + 15, cy + 14, cx + 25, cy + 23, 'Escaleras C', 'pasillo')
room(cx + 12, cy + 1, cx + 14, cy + 23, 'Pasillo C', 'pasillo', zona=False); room(cx + 1, cy + 11, cx + 25, cy + 13, 'Pasillo C2', 'pasillo', zona=False)
for (a, b, w, h, k) in [(cx + 5, cy + 10, 2, 1, 'normal'), (cx + 19, cy + 10, 2, 1, 'normal'), (cx + 5, cy + 13, 2, 1, 'normal'), (cx + 19, cy + 13, 2, 1, 'normal'),
                        (cx + 12, cy + 23, 2, 1, 'cristal'), (cx + 12, cy, 2, 1, 'cristal'), (cx, cy + 11, 1, 2, 'cristal'), (cx + 25, cy + 11, 1, 2, 'cristal'),
                        (cx + 11, cy + 4, 1, 2, 'abierta'), (cx + 14, cy + 4, 1, 2, 'abierta'), (cx + 11, cy + 17, 1, 2, 'abierta'), (cx + 14, cy + 17, 1, 2, 'abierta'),
                        (cx + 11, cy + 11, 1, 2, 'abierta'), (cx + 14, cy + 11, 1, 2, 'abierta')]:
    door(a, b, w, h, k)
# F (CIC)
fx, fy = 64, 43
room(fx + 1, fy + 1, fx + 19, fy + 11, 'Sala 1', 'lab'); room(fx + 1, fy + 12, fx + 19, fy + 22, 'Sala 2', 'lab')
room(fx + 53, fy + 1, fx + 71, fy + 11, 'Sala 3', 'lab'); room(fx + 53, fy + 12, fx + 71, fy + 22, 'Sala 4', 'lab')
room(fx + 20, fy + 1, fx + 30, fy + 8, 'Cubículos CIC', 'oficina'); room(fx + 31, fy + 1, fx + 42, fy + 8, 'Oficina CIC', 'oficina')
room(fx + 43, fy + 1, fx + 52, fy + 8, 'SITE', 'servidores')
room(fx + 20, fy + 9, fx + 52, fy + 22, 'Vestíbulo CIC', 'pasillo')
door(fx + 19, fy + 5, 1, 2); door(fx + 19, fy + 16, 1, 2); door(fx + 52, fy + 5, 1, 2); door(fx + 52, fy + 16, 1, 2)
door(fx + 24, fy + 8, 2, 1); door(fx + 36, fy + 8, 2, 1); door(fx + 47, fy + 8, 2, 1, 'restringida_electronica')
door(fx + 34, fy + 22, 4, 1, 'electronica')
# Nevería
nx, ny = 47, 36
room(nx + 1, ny + 1, nx + 15, ny + 8, 'Cocina nevería', 'cocina'); room(nx + 1, ny + 9, nx + 15, ny + 40, 'Nevería', 'cafeteria')
door(nx + 7, ny + 8, 2, 1); door(nx + 15, ny + 17, 1, 2, 'cristal'); door(nx + 15, ny + 30, 1, 2, 'cristal')
# baño entre F y E
room(95, 73, 105, 82, 'Baño E', 'bano'); door(105, 77, 1, 2)
# A
ax, ay = 88, 132
room(ax + 1, ay + 1, ax + 11, ay + 31, 'Servicios Escolares', 'oficina')
for i, nm in enumerate(['Dirección', 'Subdirección', 'Secretaría', 'Contabilidad']):
    room(ax + 12 + i * 9, ay + 1, ax + 20 + i * 9, ay + 10, nm, 'madera' if i == 0 else 'oficina')
    door(ax + 15 + i * 9, ay + 10, 2, 1, 'restringida' if i == 0 else 'normal')
room(ax + 12, ay + 11, ax + 48, ay + 14, 'Pasillo A', 'pasillo', zona=False)
room(ax + 12, ay + 15, ax + 26, ay + 31, 'Sala de espera', 'oficina'); room(ax + 27, ay + 15, ax + 39, ay + 31, 'Sala de juntas', 'madera')
room(ax + 40, ay + 15, ax + 48, ay + 22, 'Archivo', 'oficina'); room(ax + 40, ay + 23, ax + 48, ay + 31, 'Baño A', 'bano')
door(ax + 18, ay + 14, 2, 1); door(ax + 32, ay + 14, 2, 1); door(ax + 43, ay + 14, 2, 1); door(ax + 43, ay + 22, 2, 1)
door(ax + 11, ay + 12, 1, 2); door(ax, ay + 20, 1, 3, 'cristal'); door(ax + 48, ay + 12, 1, 2, 'cristal')
fill(ax - 3, ay - 3, ax + 52, ay, BANQUETA); fill(ax + 49, ay, ax + 52, ay + 33, BANQUETA); fill(ax - 3, ay, ax, ay + 33, BANQUETA)
# Conserjería junto a la cancha
room(153, 16, 163, 24, 'Conserjería', 'bodega'); door(157, 24, 2, 1, 'restringida')
fill(152, 24, 165, 27, BANQUETA)

# huecos de puertas
door_cells = {}
for i, dd in enumerate(doors):
    for X in range(dd['x'], dd['x'] + dd['w']):
        for Y in range(dd['y'], dd['y'] + dd['h']):
            walls.discard((X, Y)); door_cells[(X, Y)] = i
room_at = {}
for i, r in enumerate(rooms):
    for Y in range(r['y0'], r['y1']):
        for X in range(r['x0'], r['x1']): room_at[(X, Y)] = i
porch_cells = set()
for (x0, y0, x1, y1) in porches:
    for Y in range(y0, y1):
        for X in range(x0, x1):
            if (X, Y) not in walls: porch_cells.add((X, Y))

# ---------------- tipo final por casilla ----------------
FLOOR_OF = {'aula': 'ceramica', 'lab': 'ceramica_gris', 'oficina': 'ceramica_beige', 'servidores': 'loseta_site', 'pasillo': 'ceramica',
            'bano': 'azulejo', 'cocina': 'ceramica_gris', 'cafeteria': 'ceramica_grande', 'madera': 'madera', 'bodega': 'cemento'}
suelo = [[None] * NW for _ in range(NH)]
for Y in range(NH):
    for X in range(NW):
        t = G[Y][X]
        if (X, Y) in room_at: t = FLOOR_OF[rooms[room_at[(X, Y)]]['piso']]
        elif (X, Y) in porch_cells or (X, Y) in walls or (X, Y) in pillars: t = 'ceramica'
        elif (X, Y) in door_cells:
            # piso del cuarto vecino
            for a, b in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                if (X + a, Y + b) in room_at: t = FLOOR_OF[rooms[room_at[(X + a, Y + b)]]['piso']]; break
            else: t = 'ceramica'
        suelo[Y][X] = t
muro = [[None] * NW for _ in range(NH)]
for (X, Y) in walls:
    if 0 <= X < NW and 0 <= Y < NH: muro[Y][X] = 'muro'
for (X, Y) in pillars: muro[Y][X] = 'columna'
fondo = {}   # (X,Y) -> (fila, total)
for r in rooms:
    if not r['zona'] and r['piso'] == 'pasillo': continue
    n = 2 if (r['y1'] - r['y0']) >= 10 else 1
    for X in range(r['x0'], r['x1']):
        if (X, r['y0'] - 1) in door_cells: continue
        for k in range(n):
            if (X, r['y0'] + k) in door_cells: continue
            fondo[(X, r['y0'] + k)] = (k, n); muro[r['y0'] + k][X] = 'fondo'
for Y in range(NH):
    for X in range(NW):
        if suelo[Y][X] == PIEDRA: muro[Y][X] = 'piedra'
        if suelo[Y][X] == CERCO: muro[Y][X] = 'reja'

# ---------------- pintura de tiles ----------------
def hx(c): c = c.lstrip('#'); return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))
P = {k: hx(v) for k, v in dict(blanco='#ECEBE6', blanco_s='#D6D4CC', marino='#1E2B57', marino_c='#34457E', tope='#2B3352', tope_c='#46557F',
     vidrio='#3F8F6B', vidrio_c='#6DBB94', ceram='#E4D9C2', ceram_j='#CBBFA6', ceram_g='#D9DCDF', ceram_gj='#B9BDC2', beige='#DCCDAE', beige_j='#C1B08E',
     azul='#BFDDE8', azul_j='#93BCCB', madera='#9A6538', madera_o='#7A4A26', madera_c='#B27A48', site='#4A4F5E', site_j='#363A46', site_c='#5C6273',
     grande='#EFE8D8', grande_j='#D4CAB4', cemento='#A9A396', cemento_j='#918B7F', pasto='#5FA544', pasto_o='#4A8B35', pasto_c='#7CBF58',
     bosque='#2E5A2C', bosque_o='#1F4220', bosque_c='#3E7236', asf='#4E5058', asf_o='#44464D', asf_c='#5A5C64', calle='#3C3D43', linea='#E8E8E2',
     amarillo='#F2C230', banq='#C9C3B6', banq_j='#ADA698', conc='#C9A880', conc_j='#A8865E', conc_c='#D6B790', camino='#A4A29F', camino_j='#8E8C89',
     cancha='#3C7A55', cancha_r='#A8433A', piedra='#BFB6A2', piedra_o='#8C8372', piedra_c='#D3CBB8', mortero='#6E6658', tierra='#9B7650', tierra_o='#7F5F3E',
     contorno='#1A1D2B', reja='#E9E9E9', reja_s='#9A9A9A').items()}
def rng(*k):
    h = hashlib.md5(('|'.join(map(str, k))).encode()).digest(); return np.random.default_rng(int.from_bytes(h[:8], 'little'))
def base(c): a = np.zeros((T, T, 3), np.uint8); a[:] = c; return a
def speckle(a, c, p, r):
    m = r.random((T, T)) < p; a[m] = c; return a

# textura periódica de concreto estampado (voronoi en toro de 4x4 tiles)
def voronoi_periodic(size, n, seed, jitter=1.0):
    r = np.random.default_rng(seed); pts = r.random((n, 2)) * size
    yy, xx = np.mgrid[0:size, 0:size]
    d1 = np.full((size, size), 1e9); d2 = np.full((size, size), 1e9)
    for (px, py) in pts:
        for ox in (-size, 0, size):
            for oy in (-size, 0, size):
                dd = np.hypot(xx - px - ox, yy - py - oy)
                d2 = np.where(dd < d1, d1, np.minimum(d2, dd)); d1 = np.minimum(d1, dd)
    return d2 - d1
VOR = voronoi_periodic(128, 22, 7)
VORP = voronoi_periodic(128, 40, 11)
def bosque_tex():
    r = np.random.default_rng(3); a = np.zeros((128, 128, 3), np.uint8); a[:] = P['bosque_o']
    yy, xx = np.mgrid[0:128, 0:128]
    for _ in range(40):
        cx, cy, rad = r.random() * 128, r.random() * 128, 10 + r.random() * 12
        for ox in (-128, 0, 128):
            for oy in (-128, 0, 128):
                dd = np.hypot(xx - cx - ox, yy - cy - oy)
                a[dd < rad] = P['bosque']; a[(np.hypot(xx - cx - ox + rad * 0.3, yy - cy - oy + rad * 0.35) < rad * 0.45)] = P['bosque_c']
                a[(dd >= rad) & (dd < rad + 1.5)] = P['bosque_o']
    return a
BOSQ = bosque_tex()
TEX = {n: np.array(Image.open(f'/home/claude/mapa_work/tex/{n}.png').convert('RGB')) for n in ('pasto', 'tierra', 'muro_piedra')}

def floor_tile(t, X, Y):
    r = rng(t, X % 4, Y % 4)
    if t in ('ceramica', 'ceramica_gris', 'ceramica_beige'):
        c, j = {'ceramica': ('ceram', 'ceram_j'), 'ceramica_gris': ('ceram_g', 'ceram_gj'), 'ceramica_beige': ('beige', 'beige_j')}[t]
        a = base(P[c])
        for qy in (0, 16):
            for qx in (0, 16):
                tone = int(r.integers(-4, 5)); a[qy:qy + 16, qx:qx + 16] = np.clip(np.array(P[c]) + tone, 0, 255)
                a[qy + 2, qx + 2:qx + 6] = np.clip(np.array(P[c]) + 10, 0, 255)
        a[0, :] = P[j]; a[:, 0] = P[j]; a[16, :] = P[j]; a[:, 16] = P[j]; return a
    if t == 'ceramica_grande':
        a = base(P['grande']); a[0, :] = P['grande_j']; a[:, 0] = P['grande_j']; a[3, 3:9] = (250, 247, 240); return a
    if t == 'azulejo':
        a = base(P['azul'])
        for k in range(0, 32, 8): a[k, :] = P['azul_j']; a[:, k] = P['azul_j']
        return a
    if t == 'madera':
        a = base(P['madera'])
        for k in range(0, 32, 8):
            a[k, :] = P['madera_o']; off = (Y * 13 + k * 3) % 32; a[k:k + 8, off] = P['madera_o']
            a[k + 2, :] = np.where(r.random((32, 1)) < 0.5, P['madera_c'], P['madera']).reshape(32, 3)
        return a
    if t == 'loseta_site':
        a = base(P['site']); a[0, :] = P['site_j']; a[:, 0] = P['site_j']; a[16, :] = P['site_j']; a[:, 16] = P['site_j']
        for qy in (5, 21):
            for qx in (5, 21): a[qy:qy + 2, qx:qx + 2] = P['site_c']
        return a
    if t == 'cemento':
        a = base(P['cemento']); speckle(a, P['cemento_j'], 0.08, r); a[0, :] = P['cemento_j']; return a
    if t == PASTO: return TEX['pasto'][(Y % 4) * 32:(Y % 4) * 32 + 32, (X % 4) * 32:(X % 4) * 32 + 32].copy()
    if t == TIERRA: return TEX['tierra'][(Y % 4) * 32:(Y % 4) * 32 + 32, (X % 4) * 32:(X % 4) * 32 + 32].copy()
    if t == BOSQUE: return BOSQ[(Y % 4) * 32:(Y % 4) * 32 + 32, (X % 4) * 32:(X % 4) * 32 + 32].copy()
    if t in (ASFALTO, CALLE):
        a = base(P['asf'] if t == ASFALTO else P['calle']); speckle(a, P['asf_o'], 0.15, r); speckle(a, P['asf_c'], 0.06, r); return a
    if t == BANQUETA:
        a = base(P['banq']); speckle(a, P['banq_j'], 0.05, r); a[0, :] = P['banq_j']; a[:, 0] = P['banq_j']; return a
    if t == CAMINO:
        a = base(P['camino']); speckle(a, P['camino_j'], 0.08, r); return a
    if t == CONCRETO:
        a = base(P['conc']); v = VOR[(Y % 4) * 32:(Y % 4) * 32 + 32, (X % 4) * 32:(X % 4) * 32 + 32]
        speckle(a, P['conc_c'], 0.06, r); a[v < 1.3] = P['conc_j']; return a
    if t == CANCHA: return base(P['cancha'])
    if t == ESCALON:
        a = base(P['banq'])
        for k in range(0, 32, 8): a[k:k + 2, :] = P['banq_j']
        return a
    if t == TACTIL:
        a = base(P['amarillo'])
        for yy in range(3, 32, 6):
            for xx in range(3, 32, 6): a[yy:yy + 2, xx:xx + 2] = (214, 166, 30)
        return a
    if t in (PIEDRA, CERCO): return base(P['conc'])
    if t == TIERRA:
        a = base(P['tierra']); speckle(a, P['tierra_o'], 0.12, r); return a
    return base((255, 0, 255))

PAVED = {CONCRETO, BANQUETA, CAMINO, ESCALON, TACTIL, 'ceramica'}
def edges(a, X, Y, t):
    """bordes entre pasto y pavimento, y sombra del bosque"""
    def n(dx, dy):
        x, y = X + dx, Y + dy
        return suelo[y][x] if 0 <= x < NW and 0 <= y < NH else BOSQUE
    if t in PAVED:
        for (dx, dy, sl) in ((0, -1, (slice(0, 2), slice(None))), (0, 1, (slice(30, 32), slice(None))), (-1, 0, (slice(None), slice(0, 2))), (1, 0, (slice(None), slice(30, 32)))):
            if n(dx, dy) in (PASTO, BOSQUE, TIERRA): a[sl] = P['banq']; a[sl][..., :] = a[sl]
        if n(0, -1) in (PASTO, BOSQUE): a[0, :] = P['banq_j']
    if t == PASTO:
        if n(0, -1) == BOSQUE: a[0:3, :] = P['pasto_o']
    return a

def cancha_lines(a, X, Y):
    x0, y0, x1, y1 = 117, 1, 150, 24
    if X < x0 + 2 or X >= x1 - 2 or Y < y0 + 2 or Y >= y1 - 2: a[:] = P['cancha_r']
    gx = np.arange(32) + X * 32; gy = np.arange(32) + Y * 32
    for lx in ((x0 + 2) * 32, (x1 - 2) * 32 - 2, ((x0 + x1) // 2) * 32):
        m = (gx >= lx) & (gx < lx + 2)
        if (y0 + 2) <= Y < (y1 - 2): a[:, m] = P['linea']
    for ly in ((y0 + 2) * 32, (y1 - 2) * 32 - 2):
        m = (gy >= ly) & (gy < ly + 2)
        if (x0 + 2) <= X < (x1 - 2): a[m, :] = P['linea']
    cxp, cyp = ((x0 + x1) // 2) * 32 + 1, ((y0 + y1) / 2) * 32
    yy, xx = np.meshgrid(gy, gx, indexing='ij'); dd = np.hypot(xx - cxp, yy - cyp)
    a[(dd > 94) & (dd < 97)] = P['linea']
    return a

def parking_lines(a, X, Y):
    # cajones: columnas cada 4 casillas en filas de 7 casillas
    for (ry0, ry1) in ((66, 73), (84, 91), (109, 116), (127, 134)):
        if ry0 <= Y < ry1 and 7 <= X <= 39 and (X - 7) % 4 == 0: a[:, 0:2] = P['linea']
    if Y in (99, 100) and 6 <= X <= 40: a[14:18, 4:20] = P['amarillo']  # tope pintado
    return a

def calle_lines(a, X, Y):
    if X == 1 and (Y // 2) % 2 == 0: a[:, 30:32] = P['amarillo']
    return a

def wall_tile(kind, X, Y):
    def isw(x, y):
        return 0 <= x < NW and 0 <= y < NH and muro[y][x] in ('muro', 'columna') if kind in ('muro', 'columna') else (0 <= x < NW and 0 <= y < NH and muro[y][x] == kind)
    a = np.zeros((T, T, 4), np.uint8)
    face = not isw(X, Y + 1)
    sigue = 0 <= Y + 1 < NH and muro[Y + 1][X] == 'fondo'
    if kind == 'fondo':
        k, n = fondo[(X, Y)]
        a[..., :3] = P['blanco']; a[..., 3] = 255
        if k == n - 1: a[28:31, :, :3] = P['marino']; a[31, :, :3] = P['contorno']
        if not (0 <= X - 1 < NW and muro[Y][X - 1] in ('fondo', 'muro')): a[:, 0, :3] = P['contorno']
        if not (0 <= X + 1 < NW and muro[Y][X + 1] in ('fondo', 'muro')): a[:, 31, :3] = P['contorno']
        return a
    if kind in ('muro', 'columna'):
        exterior_below = (X, Y + 1) not in room_at
        cap_h = 12 if face else 32
        a[:cap_h, :, :3] = P['tope']; a[:cap_h, :, 3] = 255
        if not isw(X, Y - 1): a[1:3, :, :3] = P['tope_c']
        if not isw(X - 1, Y): a[:cap_h, 0:2, :3] = P['contorno']
        if not isw(X + 1, Y): a[:cap_h, 30:32, :3] = P['contorno']
        if not isw(X, Y - 1): a[0, :, :3] = P['contorno']
        if face:
            a[cap_h:, :, :3] = P['blanco']; a[cap_h:, :, 3] = 255
            a[cap_h, :, :3] = P['contorno']; a[cap_h + 1:cap_h + 3, :, :3] = P['blanco_s']
            if not sigue: a[28:31, :, :3] = P['marino']; a[31, :, :3] = P['contorno']
            if kind == 'columna':
                a[cap_h:, :, :3] = P['marino']; a[cap_h:, 2:5, :3] = P['marino_c']; a[cap_h:, 0, :3] = P['contorno']; a[cap_h:, 31, :3] = P['contorno']
            elif exterior_below and X % 2 == 0 and isw(X - 1, Y) and isw(X + 1, Y):
                a[14:28, 1:31, :3] = P['contorno']; a[15:27, 2:30, :3] = P['vidrio']; a[15:18, 2:30, :3] = P['vidrio_c']; a[15:27, 15:17, :3] = P['contorno']
            if not isw(X - 1, Y): a[cap_h:, 0, :3] = P['contorno']
            if not isw(X + 1, Y): a[cap_h:, 31, :3] = P['contorno']
        return a
    if kind == 'piedra':
        a[..., 3] = 255; a[..., :3] = TEX['muro_piedra'][(Y % 4) * 32:(Y % 4) * 32 + 32, (X % 4) * 32:(X % 4) * 32 + 32]
        if face: a[26:, :, :3] = P['piedra_o']; a[31, :, :3] = P['contorno']
        if not isw(X, Y - 1): a[0:2, :, :3] = P['piedra_c']
        return a
    if kind == 'reja':
        horiz = isw(X - 1, Y) or isw(X + 1, Y)
        if horiz:
            for k in range(2, 32, 6): a[6:30, k:k + 2, :3] = P['reja']; a[6:30, k:k + 2, 3] = 255; a[6:30, k + 2, :3] = P['reja_s']; a[6:30, k + 2, 3] = 255
            a[8:10, :, :3] = P['reja']; a[8:10, :, 3] = 255; a[26:28, :, :3] = P['reja']; a[26:28, :, 3] = 255
        else:
            a[:, 14:18, :3] = P['reja']; a[:, 14:18, 3] = 255; a[:, 18, :3] = P['reja_s']; a[:, 18, 3] = 255
        return a
    return a

# ---------------- hornear y deduplicar ----------------
tiles, index = [], {}
def add_tile(arr):
    if arr.shape[2] == 3: arr = np.dstack([arr, np.full((T, T), 255, np.uint8)])
    key = hashlib.md5(arr.tobytes()).hexdigest()
    if key not in index: index[key] = len(tiles); tiles.append(arr)
    return index[key] + 1
L_suelo = [[0] * NW for _ in range(NH)]; L_muro = [[0] * NW for _ in range(NH)]
for Y in range(NH):
    for X in range(NW):
        t = suelo[Y][X]; a = floor_tile(t, X, Y); a = edges(a, X, Y, t)
        if t == CANCHA: a = cancha_lines(a, X, Y)
        if t == ASFALTO and X < 45: a = parking_lines(a, X, Y)
        if t == CALLE: a = calle_lines(a, X, Y)
        L_suelo[Y][X] = add_tile(a)
        if muro[Y][X]: L_muro[Y][X] = add_tile(wall_tile(muro[Y][X], X, Y))
print('tiles únicos:', len(tiles))
COLS = 32
rows = (len(tiles) + COLS - 1) // COLS
ts = np.zeros((rows * T, COLS * T, 4), np.uint8)
for i, a in enumerate(tiles): ts[(i // COLS) * T:(i // COLS) * T + T, (i % COLS) * T:(i % COLS) * T + T] = a
Image.fromarray(ts, 'RGBA').save(f'{OUT}/tileset_fdiz.png')
solid_ids = sorted({L_muro[Y][X] for Y in range(NH) for X in range(NW) if L_muro[Y][X]} |
                   {L_suelo[Y][X] for Y in range(NH) for X in range(NW) if suelo[Y][X] == BOSQUE})

# ---------------- colisiones (rectángulos fusionados) ----------------
blocked = np.zeros((NH, NW), bool)
for Y in range(NH):
    for X in range(NW):
        if muro[Y][X] or suelo[Y][X] == BOSQUE: blocked[Y, X] = True
def merge_rects(b):
    b = b.copy(); out = []
    for Y in range(b.shape[0]):
        X = 0
        while X < b.shape[1]:
            if b[Y, X]:
                x1 = X
                while x1 < b.shape[1] and b[Y, x1]: x1 += 1
                y1 = Y + 1
                while y1 < b.shape[0] and b[y1, X:x1].all(): y1 += 1
                b[Y:y1, X:x1] = False; out.append((X, Y, x1 - X, y1 - Y)); X = x1
            else: X += 1
    return out
rects = merge_rects(blocked)
print('rectángulos de colisión:', len(rects))

# ---------------- marcadores de juego ----------------
def c(rn):
    r = next(r for r in rooms if r['nombre'] == rn); return ((r['x0'] + r['x1']) / 2 * T, (r['y0'] + r['y1']) / 2 * T)
TIPO_PUERTA = {'normal': 'normal', 'cristal': 'normal', 'abierta': 'abierta', 'electronica': 'electronica', 'restringida': 'restringida', 'restringida_electronica': 'restringida_electronica'}
def zona_de_puerta(dd):
    cands = []
    for X in range(dd['x'] - 1, dd['x'] + dd['w'] + 1):
        for Y in range(dd['y'] - 1, dd['y'] + dd['h'] + 1):
            if (X, Y) in room_at and rooms[room_at[(X, Y)]]['zona']: cands.append(rooms[room_at[(X, Y)]]['nombre'])
    return sorted(set(cands))
puertas = [dict(id=f'P{i:02d}', tipo=TIPO_PUERTA[dd['tipo']], estilo='cristal' if dd['tipo'] == 'cristal' else 'madera',
                orientacion='horizontal' if dd['w'] >= dd['h'] else 'vertical', x=dd['x'] * T, y=dd['y'] * T, w=dd['w'] * T, h=dd['h'] * T,
                zonas=zona_de_puerta(dd)) for i, dd in enumerate(doors) if dd['tipo'] != 'abierta']
zonas = [dict(nombre=r['nombre'], x=r['x0'] * T, y=r['y0'] * T, w=(r['x1'] - r['x0']) * T, h=(r['y1'] - r['y0']) * T) for r in rooms if r['zona']]
zonas.append(dict(nombre='Inicio (E-04) descubierta', x=0, y=0, w=0, h=0)) if False else None
ext = d['mundo']['objetos_exteriores']; ext = ast.literal_eval(ext) if isinstance(ext, str) else ext
def libre(X, Y, r=1):
    X, Y = int(X), int(Y)
    return all(0 <= X + a < NW and 0 <= Y + b < NH and not blocked[Y + b, X + a] and (X + a, Y + b) not in room_at and suelo[Y + b][X + a] in (PASTO,)
               for a in range(-r, r + 1) for b in range(-r, r + 1))
arboles = []
for o in ext:
    if o['tipo'] != 'arbol': continue
    X, Y = wx(o['x']), wy(o['y'])
    if libre(X, Y) and all((X - a) ** 2 + (Y - b) ** 2 > 20 for a, b, _ in arboles):
        arboles.append((X, Y, 'palma_alta' if len(arboles) % 3 == 0 else 'arbol_grande' if len(arboles) % 3 == 1 else 'arbol_mediano'))
def snap(X, Y):
    best = None
    for r in range(0, 20):
        for a in range(-r, r + 1):
            for b in range(-r, r + 1):
                x, y = X + a, Y + b
                if 0 <= x < NW and 0 <= y < NH and not blocked[y, x] and (x, y) not in room_at and (x, y) not in door_cells:
                    if all(0 <= x + i < NW and 0 <= y + j < NH and not blocked[y + j, x + i] for i in (-1, 0, 1) for j in (-1, 0, 1)):
                        return (x, y)
    return (X, Y)
marcadores = {
    'aparicion_jugadores': [dict(x=c('E-04')[0] + dx, y=c('E-04')[1] + 64) for dx in (-96, -32, 32, 96)],
    'camion': dict(x=12.5 * T, y=102 * T, nota='camión estacionado, mirando hacia la reja de salida'),
    'canepa': dict(x=17 * T, y=104 * T),
    'reja_principal': dict(x=4 * T, y=112 * T, w=T, h=8 * T, nota='se abre al terminar ¡Aguanten!'),
    'reja_entrada': dict(x=4 * T, y=82 * T, w=T, h=8 * T),
    'arco_acceso_campus': dict(x=44 * T, y=96 * T, w=4 * T, h=12 * T),
    'arco_entrada': dict(x=69 * T, y=158 * T, nota='entrada principal desde la calle'),
    'servidor_site': dict(x=c('SITE')[0], y=c('SITE')[1] - 48),
    'interruptor_principal': dict(x=c('SITE')[0] + 96, y=(43 + 1) * T + 8),
    'computadoras_llamada': [dict(x=c('Oficina CIC')[0] + dx, y=c('Oficina CIC')[1]) for dx in (-64, 64)],
    'llaves_conserjeria': dict(x=c('Conserjería')[0], y=c('Conserjería')[1]),
    'conserje_zombie': dict(x=c('Conserjería')[0] - 64, y=c('Conserjería')[1] + 32),
    'carnada_neveria': dict(x=c('Nevería')[0], y=c('Nevería')[1]),
    'horda_explanada': dict(x=CORAZON[0] * T + 16, y=CORAZON[1] * T + 16, radio=6 * T),
    'corazon_tapitas': dict(x=CORAZON[0] * T + 16, y=CORAZON[1] * T + 16),
    'bidones_posibles': [dict(x=c(n)[0], y=c(n)[1], zona=n) for n in ('Sala 4', 'Baños C', 'D-03', 'Archivo', 'Cocina nevería', 'B-05', 'Conserjería', 'Sala de juntas')],
    'bolsa_comida_posible': [dict(x=c(n)[0], y=c(n)[1], zona=n) for n in ('Cocina nevería', 'Sala de espera', 'C-01 Cubículos')],
    'botin_raro': dict(x=c('Dirección')[0], y=c('Dirección')[1], zona='Dirección'),
    'tarjeta_electronica': dict(x=c('Secretaría')[0], y=c('Secretaría')[1], zona='Secretaría'),
    'interruptor_luz_lab': dict(x=c('Sala 3')[0] + 240, y=(43 + 1) * T + 8),
    'joel_rescate': dict(x=c('Cubículos CIC')[0], y=c('Cubículos CIC')[1], zona='Cubículos CIC', nota='foto "cubiculos joel"'),
    'justino_rescate': dict(x=c('C-02 Cubículos')[0], y=c('C-02 Cubículos')[1], zona='C-02 Cubículos'),
    'rejillas_jefe': [dict(x=snap(X, Y)[0] * T + 16, y=snap(X, Y)[1] * T + 16) for (X, Y) in ((60, 30), (100, 30), (160, 30), (205, 34), (230, 60), (215, 120), (150, 150), (60, 150), (30, 75), (30, 128), (120, 100))],
}
props_ext = dict(arboles=[dict(x=round(X * T), y=round(Y * T), sprite=s) for X, Y, s in arboles],
                 mesas_redondas=[dict(x=(PH[0] + 4 + 6 * i) * T, y=(PH[1] + 4 + 8 * j) * T) for i in range(4) for j in range(2)] +
                                [dict(x=(145 + 7 * i) * T, y=(50 + 8 * j) * T) for i in range(4) for j in range(2)],
                 postes_luz=[dict(x=X * T, y=Y * T) for (X, Y) in ((60, 90), (90, 92), (120, 92), (140, 95), (176, 92), (100, 128), (140, 128), (30, 66), (30, 133), (200, 100))])

# ---------------- Tiled (.tmj) ----------------
def layer(name, data, lid): return dict(id=lid, name=name, type='tilelayer', width=NW, height=NH, x=0, y=0, opacity=1, visible=True, data=[v for row in data for v in row])
objid = [1]
def obj(name, typ, x, y, w=0, h=0, props=None, point=False):
    o = dict(id=objid[0], name=name, type=typ, x=x, y=y, width=w, height=h, rotation=0, visible=True)
    if point: o['point'] = True
    if props: o['properties'] = [dict(name=k, type='string', value=str(v)) for k, v in props.items()]
    objid[0] += 1; return o
ol_col = [obj('muro', 'colision', x * T, y * T, w * T, h * T) for (x, y, w, h) in rects]
ol_zonas = [obj(z['nombre'], 'zona', z['x'], z['y'], z['w'], z['h']) for z in zonas]
ol_puertas = [obj(p['id'], 'puerta', p['x'], p['y'], p['w'], p['h'], dict(tipo=p['tipo'], estilo=p['estilo'], orientacion=p['orientacion'], zonas=','.join(p['zonas']))) for p in puertas]
ol_marc = []
for k, v in marcadores.items():
    for i, m in enumerate(v if isinstance(v, list) else [v]):
        ol_marc.append(obj(f'{k}' + (f'_{i}' if isinstance(v, list) else ''), k, m['x'], m['y'], m.get('w', 0), m.get('h', 0),
                           {kk: vv for kk, vv in m.items() if kk not in ('x', 'y', 'w', 'h')}, point='w' not in m))
ol_props = [obj(a['sprite'], 'prop_exterior', a['x'], a['y'], point=True) for a in props_ext['arboles']] + \
           [obj('mesa_redonda_bancas', 'prop_exterior', m['x'], m['y'], point=True) for m in props_ext['mesas_redondas']] + \
           [obj('poste_luz', 'prop_exterior', m['x'], m['y'], point=True) for m in props_ext['postes_luz']]
tileset = dict(firstgid=1, name='tileset_fdiz', image='tileset_fdiz.png', imagewidth=COLS * T, imageheight=rows * T, tilewidth=T, tileheight=T,
               tilecount=len(tiles), columns=COLS, margin=0, spacing=0,
               tiles=[dict(id=i - 1, type='muro', **{'class': 'muro'}, objectgroup=dict(draworder='index', type='objectgroup', name='', visible=True, x=0, y=0, opacity=1,
                      objects=[dict(id=1, name='', type='', x=0, y=0, width=T, height=T, rotation=0, visible=True)])) for i in solid_ids])
tmj = dict(type='map', version='1.10', tiledversion='1.10.2', orientation='orthogonal', renderorder='right-down', infinite=False,
           width=NW, height=NH, tilewidth=T, tileheight=T, nextlayerid=9, nextobjectid=objid[0], compressionlevel=-1,
           tilesets=[tileset],
           layers=[layer('suelo', L_suelo, 1), layer('muros', L_muro, 2),
                   dict(id=3, name='colisiones', type='objectgroup', draworder='topdown', objects=ol_col, opacity=1, visible=False, x=0, y=0),
                   dict(id=4, name='zonas_niebla', type='objectgroup', draworder='topdown', objects=ol_zonas, opacity=1, visible=False, x=0, y=0),
                   dict(id=5, name='puertas', type='objectgroup', draworder='topdown', objects=ol_puertas, opacity=1, visible=True, x=0, y=0),
                   dict(id=6, name='marcadores', type='objectgroup', draworder='topdown', objects=ol_marc, opacity=1, visible=True, x=0, y=0),
                   dict(id=7, name='props_exteriores', type='objectgroup', draworder='topdown', objects=ol_props, opacity=1, visible=True, x=0, y=0)])
json.dump(tmj, open(f'{OUT}/mapa_fdiz.tmj', 'w', encoding='utf-8'), ensure_ascii=False)
json.dump(tmj, open(f'{OUT}/mapa_fdiz_gdevelop.json', 'w', encoding='utf-8'), ensure_ascii=False)
json.dump(dict(casilla_px=T, ancho_px=NW * T, alto_px=NH * T, colisiones=[dict(x=x * T, y=y * T, w=w * T, h=h * T) for (x, y, w, h) in rects],
               zonas=zonas, puertas=puertas, marcadores=marcadores, props_exteriores=props_ext,
               cuartos=[dict(r, x0=r['x0'] * T, y0=r['y0'] * T, x1=r['x1'] * T, y1=r['y1'] * T) for r in rooms]),
          open(f'{OUT}/mapa_fdiz_datos.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---------------- imagen completa ----------------
full = np.zeros((NH * T, NW * T, 4), np.uint8)
for Y in range(NH):
    for X in range(NW):
        full[Y * T:Y * T + T, X * T:X * T + T] = tiles[L_suelo[Y][X] - 1]
        if L_muro[Y][X]:
            w = tiles[L_muro[Y][X] - 1]; m = w[..., 3:] > 0
            full[Y * T:Y * T + T, X * T:X * T + T] = np.where(m, w, full[Y * T:Y * T + T, X * T:X * T + T])
img = Image.fromarray(full, 'RGBA')
img.save(f'{OUT}/mapa_fdiz_completo.png')
print('listo', img.size, 'puertas', len(puertas), 'zonas', len(zonas))
