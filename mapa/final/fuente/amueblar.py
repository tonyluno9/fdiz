# FDI-Z · coloca los props generados (lote del mapa) en el mapa compacto y arma la vista previa
import json, os, random
import numpy as np
from PIL import Image

T = 32
SPR = '/mnt/user-data/uploads/fdiz/generado/sprites/mapa/'
OBJ = '/mnt/user-data/uploads/fdiz/generado/sprites/objetos/'
OUT = '/home/claude/mapa_work/final'
EXTRA = f'{OUT}/sprites_extra'; os.makedirs(EXTRA, exist_ok=True)
D = json.load(open(f'{OUT}/mapa_fdiz_datos.json', encoding='utf-8'))
rnd = random.Random(7)

# ---------- sprites y variantes escaladas ----------
cache = {}
def sprite(key):
    if key not in cache:
        p = SPR + key + '.png' if not key.startswith('extra/') else f'{OUT}/sprites_extra/{key[6:]}.png'
        cache[key] = Image.open(p).convert('RGBA')
    return cache[key]
def variante(key, alto=None, ancho=None, espejo=False, base=None):
    im = sprite(key) if base is None else base
    w, h = im.size
    f = (alto / h) if alto else (ancho / w) if ancho else 1
    nw, nh = max(1, round(w * f)), max(1, round(h * f))
    name = key.replace('/', '__') + (f'_h{nh}' if f != 1 else '') + ('_espejo' if espejo else '')
    if f'extra/{name}' in cache: return f'extra/{name}'
    a = im.resize((nw, nh), Image.BOX) if f != 1 else im.copy()
    arr = np.array(a); arr[..., 3] = np.where(arr[..., 3] >= 128, 255, 0)
    rgb = Image.fromarray(arr[..., :3]).quantize(colors=48, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert('RGB')
    out = Image.fromarray(np.dstack([np.array(rgb), arr[..., 3]]).astype(np.uint8), 'RGBA')
    if espejo: out = out.transpose(Image.FLIP_LEFT_RIGHT)
    out.save(f'{EXTRA}/{name}.png'); cache[f'extra/{name}'] = out
    return f'extra/{name}'

# ---------- ocupación (para no tapar puertas ni encimar muebles) ----------
NW, NH = D['ancho_px'] // T, D['alto_px'] // T
ocupado = np.zeros((NH, NW), bool)
for c in D['colisiones']:
    ocupado[c['y'] // T:(c['y'] + c['h']) // T, c['x'] // T:(c['x'] + c['w']) // T] = True
libre_puerta = np.zeros((NH, NW), bool)
for p in D['puertas']:
    x0, y0, x1, y1 = p['x'] // T, p['y'] // T, (p['x'] + p['w']) // T, (p['y'] + p['h']) // T
    libre_puerta[max(0, y0 - 2):y1 + 2, max(0, x0 - 2):x1 + 2] = True
for z in ('Pasillo C', 'Pasillo C2', 'Pasillo A'): pass

props = []
def poner(key, x, y, capa='piso', choque=True, pie=None, forzar=False):
    """x,y = ancla abajo-centro en px. pie = (ancho, alto) del área que choca, en px."""
    im = sprite(key); w, h = im.size
    if choque:
        pw, ph = pie or (int(w * 0.86), int(min(max(h * 0.4, 18), 44)))
        rect = dict(x=int(x - pw / 2), y=int(y - ph), w=pw, h=ph)
        tx0, ty0, tx1, ty1 = rect['x'] // T, rect['y'] // T, (rect['x'] + rect['w'] - 1) // T, (rect['y'] + rect['h'] - 1) // T
        if not forzar and (libre_puerta[ty0:ty1 + 1, tx0:tx1 + 1].any() or ocupado[ty0:ty1 + 1, tx0:tx1 + 1].any()):
            return False
        ocupado[ty0:ty1 + 1, tx0:tx1 + 1] = True
    else:
        rect = None
    archivo = (f'mapa/{key}.png' if not key.startswith('extra/') else f'mapa_extra/{key[6:]}.png')
    props.append(dict(sprite=key, archivo=archivo, x=int(x), y=int(y), capa=capa, colision=rect, w=w, h=h))
    return True

def fondo_n(r):
    return 2 if (r['y1'] - r['y0']) // T >= 10 else 1
def segmentos_pared(r):
    """columnas (en casillas) de la pared de fondo sin hueco de puerta"""
    tx0, tx1, ty0 = r['x0'] // T, r['x1'] // T, r['y0'] // T
    cols = [X for X in range(tx0, tx1) if not any(p['y'] // T == ty0 - 1 and p['x'] // T <= X < (p['x'] + p['w']) // T for p in D['puertas'])]
    segs, cur = [], []
    for X in cols:
        if cur and X != cur[-1] + 1: segs.append(cur); cur = []
        cur.append(X)
    if cur: segs.append(cur)
    return sorted(segs, key=len, reverse=True)
def en_pared(r, key, xcent_tiles, alto_max):
    n = fondo_n(r); h_face = 20 + n * T
    im = sprite(key)
    k = variante(key, alto=min(im.height, alto_max(h_face))) if im.height > alto_max(h_face) else key
    y = r['y0'] + n * T - 6
    poner(k, xcent_tiles * T, y, capa='pared', choque=False)

# ---------- cuartos ----------
def aula(r):
    tx0, tx1 = r['x0'] // T, r['x1'] // T; n = fondo_n(r); ty_walk = r['y0'] // T + n; ty1 = r['y1'] // T
    segs = segmentos_pared(r)
    s = segs[0]; cx = (s[0] + s[-1] + 1) / 2
    en_pared(r, 'salon/pizarron', cx, lambda f: f - 14)
    if len(s) >= 9 or len(segs) > 1:
        s2 = segs[1] if len(segs) > 1 else s
        en_pared(r, 'salon/minisplit', (s2[0] + s2[-1] + 1) / 2 if s2 is not s else s[-1] - 1, lambda f: 30)
    # escritorio del profe
    poner('salon/silla_profesor', cx * T + 20, (ty_walk + 1) * T + 10, choque=False)
    poner('salon/escritorio_profesor', cx * T, (ty_walk + 2) * T + 8, pie=(90, 30))
    # pupitres (vemos a los alumnos de espaldas: miran al pizarrón)
    for yy in range(ty_walk + 4, ty1, 2):
        for xx in range(tx0 + 1, tx1 - 1, 2):
            if (xx - tx0) == (tx1 - tx0) // 2: continue  # pasillo central
            if rnd.random() < 0.12: continue           # huecos (desorden)
            poner('salon/pupitre_espalda', xx * T + 16, yy * T + 26, pie=(30, 18))
    for _ in range(2):
        x = rnd.choice([tx0 + 0.6, tx1 - 0.6]); poner('exterior/bote_exterior' if False else variante('exterior/bote_exterior', alto=34), x * T, (ty1 - 0.2) * T)
def lab(r):
    tx0, tx1 = r['x0'] // T, r['x1'] // T; n = fondo_n(r); ty_walk = r['y0'] // T + n; ty1 = r['y1'] // T
    for xx in range(tx0 + 1, tx1 - 1, 2):
        poner('laboratorio/pc_frente', xx * T + 32, (ty_walk + 1) * T + 6, pie=(62, 30))
        poner('laboratorio/silla_oficina_espalda', xx * T + 32, (ty_walk + 2) * T + 12, choque=False)
        poner('laboratorio/silla_oficina_frente', xx * T + 32, (ty1 - 1) * T - 4, choque=False)
        poner('laboratorio/pc_espalda', xx * T + 32, ty1 * T - 2, pie=(62, 30))
    poner('laboratorio/mesa_maestro_lab', (tx0 + 0.5) * T + 44, (ty1 - 2) * T - 4, pie=(76, 30), forzar=True)
    segs = segmentos_pared(r)
    en_pared(r, 'senaletica/salida_emergencia', segs[0][0] + 1, lambda f: 24)
    en_pared(r, 'salon/minisplit', segs[0][-1], lambda f: 30)
def oficina_cic(r):
    tx0, tx1 = r['x0'] // T, r['x1'] // T; n = fondo_n(r); ty_walk = r['y0'] // T + n; ty1 = r['y1'] // T
    poner('cic/archivero', (tx0 + 0.7) * T, (ty_walk + 1.6) * T)
    poner('cic/copiadora', (tx0 + 2.2) * T, (ty_walk + 1.6) * T)
    poner('cic/mostrador_curvo', (tx0 + tx1) / 2 * T + 40, (ty1 - 0.5) * T, pie=(170, 40), forzar=False)
    poner('cic/escritorio_oficina_pc', (tx1 - 1.6) * T, (ty_walk + 2) * T)
def cubiculos_cic(r):
    tx0, tx1 = r['x0'] // T, r['x1'] // T; n = fondo_n(r); ty_walk = r['y0'] // T + n; ty1 = r['y1'] // T
    poner('cic/estante_equipo', (tx0 + 1.1) * T, (ty_walk + 1.8) * T)
    poner('cic/escritorio_oficina_pc', (tx0 + 4) * T, (ty_walk + 2.2) * T)
    poner('laboratorio/silla_oficina_frente', (tx0 + 4) * T + 10, (ty_walk + 0.9) * T, choque=False)
    poner('cic/escritorio_oficina_pc', (tx1 - 2) * T, (ty_walk + 2.2) * T)
    poner('cic/cajas_carton', (tx1 - 1) * T, (ty1 - 0.2) * T)
    poner('cic/cajas_carton', (tx0 + 1) * T, (ty1 - 0.2) * T)
def site(r):
    tx0, tx1 = r['x0'] // T, r['x1'] // T; n = fondo_n(r); ty_walk = r['y0'] // T + n; ty1 = r['y1'] // T
    en_pared(r, 'site/tablero_apagado', tx1 - 1.5, lambda f: f - 8)
    en_pared(r, 'site/caja_telecom', tx0 + 1, lambda f: f - 10)
    for i, xx in enumerate((tx0 + 1.5, tx0 + 4.2)):
        poner('site/rack_apagado', xx * T, (ty_walk + 3.2) * T, pie=(70, 40))
    poner('site/ups', (tx1 - 1.3) * T, (ty_walk + 2) * T)
    poner('site/cables_piso', (tx0 + 3) * T, (ty1 - 0.3) * T, choque=False)
def vestibulo(r):
    tx0, tx1 = r['x0'] // T, r['x1'] // T; n = fondo_n(r); ty_walk = r['y0'] // T + n; ty1 = r['y1'] // T
    for i, xx in enumerate(range(tx0 + 1, tx0 + 9, 2)):
        poner('cic/locker_abierto' if i == 2 else 'cic/lockers_cerrados', xx * T + 16, (ty_walk + 1.3) * T, pie=(46, 22))
    segs = segmentos_pared(r)
    en_pared(r, 'senaletica/tablero_avisos', (segs[0][0] + segs[0][-1] + 1) / 2, lambda f: f - 16)
    en_pared(r, 'senaletica/reloj_pared', segs[0][-1] - 1, lambda f: 30)
    poner('oficinas/sillon_espera', (tx1 - 5) * T, (ty_walk + 2) * T)
    poner('oficinas/garrafon_agua', (tx1 - 1) * T, (ty_walk + 1.5) * T)
    poner('oficinas/planta_oficina', (tx0 + 0.7) * T, (ty1 - 0.2) * T)
    poner('oficinas/planta_oficina', (tx1 - 0.7) * T, (ty1 - 0.2) * T)
    poner('exterior/banca_metal', (tx0 + tx1) / 2 * T - 120, (ty1 - 3) * T)
def neveria(r):
    tx0, tx1 = r['x0'] // T, r['x1'] // T; n = fondo_n(r); ty_walk = r['y0'] // T + n; ty1 = r['y1'] // T
    segs = segmentos_pared(r)
    en_pared(r, 'neveria/menu_pared', (segs[0][0] + segs[0][-1] + 1) / 2, lambda f: f - 12)
    barra = variante('neveria/barra_verde', ancho=150)
    poner(barra, (tx0 + tx1) / 2 * T, (ty_walk + 4) * T, pie=(140, 64))
    poner('neveria/caja_registradora', (tx0 + tx1) / 2 * T + 30, (ty_walk + 2.2) * T, capa='encima', choque=False)
    poner('neveria/refri_refresco', (tx0 + 0.9) * T, (ty_walk + 1.8) * T)
    poner('neveria/congelador_helados', (tx1 - 1.4) * T, (ty_walk + 1.8) * T)
    for yy in range(ty_walk + 7, ty1 - 1, 4):
        for xx in (tx0 + 3.5, tx1 - 3.5):
            poner('neveria/mesa_sillas_blancas', xx * T, yy * T + 40, pie=(96, 50))
    for yy in (ty_walk + 6, ty1 - 1):
        poner('neveria/maceta_flores', (tx0 + 0.8) * T, yy * T + 20); poner('neveria/maceta_flores', (tx1 - 0.8) * T, yy * T + 20)
    poner(variante('exterior/bote_exterior', alto=40), (tx1 - 0.6) * T, (ty1 - 3) * T)
def cocina(r):
    tx0, tx1 = r['x0'] // T, r['x1'] // T; n = fondo_n(r); ty_walk = r['y0'] // T + n; ty1 = r['y1'] // T
    poner('neveria/refri_refresco', (tx0 + 1) * T, (ty_walk + 2) * T)
    poner('neveria/refri_refresco', (tx0 + 3) * T, (ty_walk + 2) * T)
    poner('neveria/congelador_helados', (tx0 + 6.5) * T, (ty_walk + 2) * T)
    poner('cic/estante_equipo', (tx1 - 1.2) * T, (ty_walk + 2.2) * T)
    poner('cic/cajas_carton', (tx1 - 3) * T, (ty1 - 0.2) * T)
def bano(r, hombres=True):
    tx0, tx1 = r['x0'] // T, r['x1'] // T; n = fondo_n(r); ty_walk = r['y0'] // T + n; ty1 = r['y1'] // T
    xx = tx0 + 1.2
    k = 0
    while xx + 1.2 <= tx1 and k < 4:
        poner('banos/cubiculo_abierto' if k == 1 else 'banos/cubiculo_cerrado', xx * T, (ty_walk + 2.6) * T, pie=(66, 30)); xx += 2.4; k += 1
    poner('banos/lavabo_espejo', (tx1 - 1.2) * T, (ty1 - 0.2) * T, pie=(56, 22))
    if hombres and tx1 - tx0 >= 8: poner('banos/mingitorio', (tx0 + 1) * T, (ty1 - 0.2) * T)
def oficina(r, jefe=False):
    tx0, tx1 = r['x0'] // T, r['x1'] // T; n = fondo_n(r); ty_walk = r['y0'] // T + n; ty1 = r['y1'] // T
    poner('oficinas/librero', (tx0 + 1) * T, (ty_walk + 1.9) * T, pie=(56, 24))
    poner('cic/archivero', (tx1 - 0.8) * T, (ty_walk + 1.6) * T)
    poner('laboratorio/silla_oficina_frente', (tx0 + tx1) / 2 * T + 8, (ty_walk + 2.7) * T, choque=False)
    poner('oficinas/escritorio_l', (tx0 + tx1) / 2 * T, (ty_walk + 4) * T, pie=(100, 36))
    poner('oficinas/silla_visita', (tx0 + tx1) / 2 * T - 20, (ty_walk + 5.4) * T, pie=(24, 14))
    poner('oficinas/planta_oficina', (tx1 - 0.8) * T, (ty1 - 0.1) * T)
def servicios(r):
    tx0, tx1 = r['x0'] // T, r['x1'] // T; n = fondo_n(r); ty_walk = r['y0'] // T + n; ty1 = r['y1'] // T
    for yy in (ty_walk + 3, ty_walk + 9, ty_walk + 15):
        poner('cic/escritorio_oficina_pc', (tx0 + 3) * T, yy * T, pie=(84, 34))
        poner('laboratorio/silla_oficina_frente', (tx0 + 3) * T + 8, (yy - 1.2) * T, choque=False)
        poner('oficinas/silla_visita', (tx0 + 3) * T, (yy + 1.2) * T, pie=(24, 14))
    poner('oficinas/sillon_espera', (tx0 + 4) * T, (ty1 - 3) * T)
    poner('oficinas/garrafon_agua', (tx1 - 0.7) * T, (ty1 - 0.3) * T)
    for yy in (ty_walk + 1.8, ty_walk + 7):
        poner('cic/archivero', (tx1 - 0.7) * T, yy * T)
    poner('oficinas/planta_oficina', (tx0 + 0.8) * T, (ty1 - 0.1) * T)
def espera(r):
    tx0, tx1 = r['x0'] // T, r['x1'] // T; n = fondo_n(r); ty_walk = r['y0'] // T + n; ty1 = r['y1'] // T
    segs = segmentos_pared(r); en_pared(r, 'senaletica/tablero_avisos', (segs[0][0] + segs[0][-1] + 1) / 2, lambda f: f - 16)
    for yy in range(ty_walk + 3, ty1 - 1, 3):
        poner('oficinas/sillon_espera', (tx0 + 4) * T, yy * T); poner('oficinas/sillon_espera', (tx1 - 4) * T, yy * T)
    poner('oficinas/garrafon_agua', (tx0 + 0.7) * T, (ty_walk + 1.6) * T)
    poner('oficinas/planta_oficina', (tx1 - 0.8) * T, (ty_walk + 1.6) * T)
def juntas(r):
    tx0, tx1 = r['x0'] // T, r['x1'] // T; n = fondo_n(r); ty_walk = r['y0'] // T + n; ty1 = r['y1'] // T
    poner('oficinas/mesa_juntas', (tx0 + tx1) / 2 * T, (ty_walk + 9) * T, pie=(170, 100))
    poner('oficinas/librero', (tx0 + 1) * T, (ty_walk + 1.9) * T, pie=(56, 24)); poner('oficinas/librero', (tx0 + 3) * T, (ty_walk + 1.9) * T, pie=(56, 24))
    poner('oficinas/planta_oficina', (tx1 - 0.8) * T, (ty_walk + 1.6) * T)
def archivo(r):
    tx0, tx1 = r['x0'] // T, r['x1'] // T; n = fondo_n(r); ty_walk = r['y0'] // T + n; ty1 = r['y1'] // T
    for i in range(3): poner('cic/archivero', (tx0 + 0.7 + i * 1.2) * T, (ty_walk + 1.6) * T)
    poner('oficinas/librero', (tx1 - 1.2) * T, (ty_walk + 1.9) * T, pie=(56, 24))
    poner('cic/cajas_carton', (tx0 + 1) * T, (ty1 - 0.2) * T); poner('cic/cajas_carton', (tx0 + 2.3) * T, (ty1 - 0.2) * T)
def conserjeria(r):
    tx0, tx1 = r['x0'] // T, r['x1'] // T; n = fondo_n(r); ty_walk = r['y0'] // T + n; ty1 = r['y1'] // T
    poner('cic/estante_equipo', (tx0 + 1.1) * T, (ty_walk + 2) * T); poner('cic/estante_equipo', (tx0 + 3.2) * T, (ty_walk + 2) * T)
    for i in range(3): poner('cic/cajas_carton', (tx1 - 1 - i * 1.3) * T, (ty1 - 0.2) * T)
    poner(variante('exterior/bote_exterior', alto=40), (tx1 - 1) * T, (ty_walk + 1.5) * T)
def cubiculos_c(r):
    tx0, tx1 = r['x0'] // T, r['x1'] // T; n = fondo_n(r); ty_walk = r['y0'] // T + n; ty1 = r['y1'] // T
    poner('oficinas/librero', (tx0 + 1) * T, (ty_walk + 1.9) * T, pie=(56, 24))
    poner('oficinas/escritorio_l', (tx0 + 4.5) * T, (ty_walk + 3) * T, pie=(100, 36))
    poner('laboratorio/silla_oficina_frente', (tx0 + 4.5) * T + 8, (ty_walk + 1.8) * T, choque=False)
    poner('oficinas/cancel_vidrio', (tx0 + 7) * T, (ty1 - 0.1) * T, pie=(60, 16))
    poner('oficinas/planta_oficina', (tx1 - 0.8) * T, (ty_walk + 1.6) * T)

POR_NOMBRE = {'Oficina CIC': oficina_cic, 'Cubículos CIC': cubiculos_cic, 'SITE': site, 'Vestíbulo CIC': vestibulo, 'Nevería': neveria,
              'Cocina nevería': cocina, 'Servicios Escolares': servicios, 'Sala de espera': espera, 'Sala de juntas': juntas, 'Archivo': archivo,
              'Conserjería': conserjeria, 'C-01 Cubículos': cubiculos_c, 'C-02 Cubículos': cubiculos_c, 'Dirección': lambda r: oficina(r, True),
              'Baño M': lambda r: bano(r, False)}
for r in D['cuartos']:
    f = POR_NOMBRE.get(r['nombre'])
    if f: f(r)
    elif r['piso'] == 'aula': aula(r)
    elif r['piso'] == 'lab': lab(r)
    elif r['piso'] == 'bano': bano(r)
    elif r['piso'] == 'oficina': oficina(r)

# ---------- exteriores ----------
M = D['marcadores']
def tile_libre(x, y):
    X, Y = int(x // T), int(y // T); return 0 <= X < NW and 0 <= Y < NH and not ocupado[Y, X]
# hitos
poner('hitos/arco_entrada', M['arco_entrada']['x'], M['arco_entrada']['y'], capa='hito', choque=False)
ax, ay = M['arco_entrada']['x'], M['arco_entrada']['y']
for rect in (dict(x=ax - 160, y=ay - 40, w=96, h=40), dict(x=ax + 104, y=ay - 150, w=44, h=40)):
    props.append(dict(sprite='colision', archivo=None, x=rect['x'], y=rect['y'], capa='colision', colision=rect, w=rect['w'], h=rect['h']))
poner('hitos/corazon_tapitas', M['corazon_tapitas']['x'], M['corazon_tapitas']['y'] + 40, capa='hito', pie=(140, 60), forzar=True)
poner('hitos/arco_salida', 216 * T, 152 * T, capa='hito', pie=(30, 30), forzar=True)
poner('exterior/directorio', (ax + 200), ay - 40, forzar=True)
for x in range(4 * T + 64, 100 * T, 128):
    if not (60 * T < x < 78 * T): poner('hitos/reja_blanca', x, 164 * T - 2, capa='piso', pie=(128, 20), forzar=True)
# estacionamiento
cam = M['camion']
camion = variante('camion', base=Image.open(OBJ + 'camion/camion.png').convert('RGBA'), alto=320)
props.append(dict(sprite=camion, archivo=f'mapa_extra/{camion[6:]}.png', x=int(cam['x']), y=int(cam['y'] + 160), capa='piso',
                  colision=dict(x=int(cam['x'] - 46), y=int(cam['y'] - 150), w=92, h=300), w=100, h=320))
carros = ['estacionamiento/pickup_blanca', 'estacionamiento/sedan_rojo', 'estacionamiento/suv_gris']
for (ry0, ry1) in ((66, 73), (84, 91), (109, 116), (127, 134)):
    for c in range(8):
        if rnd.random() < 0.45: continue
        x = (7 + c * 4 + 2) * T; y = ry1 * T - 6
        if 10 * T <= x <= 15 * T and 90 * T < y < 118 * T: continue
        k = rnd.choice(carros)
        if ry0 in (84, 127): k = variante(k, espejo=False)
        poner(k, x, y, pie=(int(sprite(k).width * 0.9), int(sprite(k).height * 0.8)), forzar=True)
poner('estacionamiento/caseta_vigilancia', 8 * T, 81 * T, pie=(100, 50), forzar=True)
poner('estacionamiento/reja_cerrada', 3 * T + 16, 120 * T, capa='piso', choque=False)
for (x, y) in ((22, 98), (24, 98), (26, 104), (30, 104)): poner('estacionamiento/cono', x * T, y * T, pie=(20, 12))
# cancha
poner('cancha/canasta_basquet', 119 * T, 13 * T, pie=(30, 20), forzar=True)
poner(variante('cancha/canasta_basquet', espejo=True), 148 * T, 13 * T, pie=(30, 20), forzar=True)
for x in (116, 133, 151):
    poner('cancha/poste_techo', x * T, 2 * T, pie=(20, 16), forzar=True); poner('cancha/poste_techo', x * T, 25 * T, pie=(20, 16), forzar=True)
# mesas redondas, postes, árboles
for m in D['props_exteriores']['mesas_redondas']: poner('exterior/mesa_redonda_bancas', m['x'] + 16, m['y'] + 60, pie=(110, 50))
for m in D['props_exteriores']['postes_luz']:
    if tile_libre(m['x'], m['y']): poner('exterior/poste_luz', m['x'], m['y'], pie=(16, 12))
for a in D['props_exteriores']['arboles']:
    k = {'palma_alta': 'vegetacion/palma_alta', 'arbol_grande': 'vegetacion/arbol_grande', 'arbol_mediano': 'vegetacion/arbol_mediano'}[a['sprite']]
    if rnd.random() < 0.3: k = 'vegetacion/palma_baja'
    poner(k, a['x'], a['y'] + 20, capa='arbol', pie=(26, 16))
# arbustos y flores junto a los edificios y en la explanada
pasto = []
G = Image.open(f'{OUT}/mapa_fdiz_completo.png').convert('RGB').resize((NW, NH), Image.NEAREST)
gp = np.array(G)
for Y in range(2, NH - 2):
    for X in range(48, NW - 2):
        c = gp[Y, X]
        if 113 <= X <= 153 and Y <= 27: continue
        if c[1] > 120 and c[0] < 120 and c[2] < 90 and not ocupado[Y, X]: pasto.append((X, Y))
rnd.shuffle(pasto)
k = 0
for (X, Y) in pasto:
    if k >= 70: break
    if poner(rnd.choice(['vegetacion/arbusto', 'vegetacion/arbusto', 'vegetacion/mata_flores', 'vegetacion/arbol_joven']), X * T + 16, Y * T + 28, pie=(30, 14)):
        k += 1
# jardineras con árbol en las plazas grandes
for (x0, y0, x1, y1) in ((200, 98, 234, 148), (128, 130, 162, 160), (174, 140, 196, 160)):
    for yy in range(y0, y1, 9):
        for xx in range(x0, x1, 9):
            if poner('vegetacion/jardinera_piedra', xx * T, yy * T, pie=(90, 40)):
                poner(rnd.choice(['vegetacion/arbol_mediano', 'vegetacion/palma_baja']), xx * T, yy * T - 18, capa='arbol', choque=False)
            poner('exterior/banca_metal', xx * T + 4 * T, yy * T + 3 * T, pie=(90, 20))
# botes y bancas en los porches
for (x, y) in ((112, 72), (130, 72), (148, 72), (166, 72), (180, 40), (180, 95), (180, 125), (220, 28), (245, 28)):
    poner(variante('exterior/bote_exterior', alto=40), x * T + 16, y * T + 28, pie=(24, 14))
for (x, y) in ((183, 83), (189, 83)):
    poner('exterior/banca_metal', x * T, y * T + 20, pie=(90, 20))
for (x, y) in ((140, 106), (172, 106)):
    poner('exterior/condensador_ac', x * T, y * T, pie=(50, 24))

json.dump(dict(nota='x,y = ancla abajo-centro en px; colision en px (None = no choca); capa: piso, pared, encima, arbol, hito',
               props=props), open(f'{OUT}/mapa_fdiz_props.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('props:', len(props), 'extra:', len(os.listdir(EXTRA)))

# ---------- vista previa con props ----------
img = Image.open(f'{OUT}/mapa_fdiz_completo.png').convert('RGBA')
orden = {'piso': 1, 'pared': 0, 'encima': 2, 'hito': 1, 'arbol': 1}
for p in sorted([p for p in props if p['archivo']], key=lambda p: (orden[p['capa']] if p['capa'] == 'pared' else 1, p['y'] + (1000 if p['capa'] == 'encima' else 0))):
    im = sprite(p['sprite'])
    img.paste(im, (int(p['x'] - im.width / 2), int(p['y'] - im.height)), im)
img.save(f'{OUT}/mapa_fdiz_con_props.png')
print('ok')
