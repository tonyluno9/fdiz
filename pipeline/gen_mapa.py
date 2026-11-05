# Genera referencias + manifest_mapa.json para el lote del mapa (props del entorno)
import json, os
from PIL import Image, ImageOps

OUT = '/home/claude/mapa_gen/out'           # espejo de RAIZ
FOT = '/mnt/user-data/uploads/fotos escuela/'
SPR = '/mnt/user-data/uploads/fdiz/generado/sprites/objetos/'
os.makedirs(f'{OUT}/mapa/referencias', exist_ok=True)
os.makedirs(f'{OUT}/pipeline', exist_ok=True)
fotos = sorted(f for f in os.listdir(FOT) if f.endswith('.jpeg'))

# ---- imagen 1: referencia de estilo (objetos del lote 1, pixeles grandes, fondo magenta)
objs = ['contenedores/locker_cerrado.png', 'contenedores/locker_abierto.png', 'contenedores/maquina_cerrada.png',
        'armas/silla.png', 'armas/extintor.png', 'contenedores/mochila_cerrada.png', 'objetivos/bidon.png',
        'props_especiales/laptop.png', 'camion/camion.png']
ims = [Image.open(SPR + o).convert('RGBA') for o in objs]
ims[-1] = ims[-1].rotate(90, expand=True)   # camion acostado para que quepa
S = 4
W = sum(i.width for i in ims[:-1]) * S + 40 * (len(ims)) ; H = 64 * S + 60 + ims[-1].height * S + 60
ref = Image.new('RGBA', (W, H), (255, 0, 255, 255)); x = 40
for i in ims[:-1]:
    big = i.resize((i.width * S, i.height * S), Image.NEAREST); ref.alpha_composite(big, (x, 40 + 64 * S - big.height)); x += big.width + 40
cam = ims[-1].resize((ims[-1].width * S, ims[-1].height * S), Image.NEAREST); ref.alpha_composite(cam, (40, 64 * S + 80))
ref.convert('RGB').save(f'{OUT}/mapa/referencias/estilo_mapa.png')

def collage(nombre, idxs):
    ps = [ImageOps.exif_transpose(Image.open(FOT + fotos[i])).convert('RGB') for i in idxs]
    h = 600
    ps = [p.resize((int(p.width * h / p.height), h), Image.LANCZOS) for p in ps]
    c = Image.new('RGB', (sum(p.width for p in ps) + 10 * (len(ps) - 1), h), (255, 255, 255)); x = 0
    for p in ps: c.paste(p, (x, 0)); x += p.width + 10
    if c.width > 1800: c = c.resize((1800, int(c.height * 1800 / c.width)), Image.LANCZOS)
    c.save(f'{OUT}/mapa/referencias/fotos_{nombre}.png'); return f'mapa/referencias/fotos_{nombre}.png'

BG = ("Flat solid magenta background (#FF00FF) filling the whole image, no floor, no floor shadow, "
      "no text, no letters, no numbers, no people, no characters, no borders, no grid lines.")
STYLE = ("Use image 1 ONLY as the pixel art style reference: the same chunky pixel size, flat block shading, "
         "dark 1-pixel outlines and the same color saturation as those game objects. "
         "Use image 2 only as a reference of what the real objects look like (shapes, materials and colors); it is a photo "
         "of the real school, do not copy its perspective, lighting or background. ")
VIEW = ("Draw every object in 3/4 top-down view for a 2D top-down video game (camera above and in front, like Stardew Valley "
        "or classic Pokemon games: we see the top surface and the front face of each object), no perspective distortion. ")
def grid(n):
    if n <= 4: return f"one single row of {n}"
    r = (n + 1) // 2; return f"two rows of {r} (top row first, left to right, then bottom row left to right)"

JOBS = []
def hoja(hid, fotos_idx, items, aspect='16:9', extra=''):
    names = [it[0] for it in items]
    desc = ' '.join(f"{k+1}) {it[1]};" for k, it in enumerate(items))
    p = (STYLE + VIEW + f"Create exactly {len(items)} separate game props arranged in {grid(len(items))}, each one centered in its own "
         "equal-size cell with wide clear empty space between them, nothing touching another object or the image edges, all at a "
         "consistent real-world scale relative to each other. " + f"Objects in order: {desc} " + extra + BG)
    refs = ['mapa/referencias/estilo_mapa.png'] + ([collage(hid, fotos_idx)] if fotos_idx else [])
    if not fotos_idx:
        p = p.replace("Use image 2 only as a reference of what the real objects look like (shapes, materials and colors); it is a photo of the real school, do not copy its perspective, lighting or background. ", "")
    JOBS.append(dict(id=f"mapa__{hid}", categoria='mapa', entidad='mapa', animacion=hid, frames=len(items), escala='mapa',
                     aspect_ratio=aspect, resolution='1k', referencias=refs, prompt=p,
                     salida_raw=f"generado/raw/mapa/{hid}.png", nombres=names,
                     tamanos={it[0]: {it[2]: it[3]} for it in items}, filas=1 if len(items) <= 4 else 2, fase='M'))

hoja('salon', [38, 32], [
    ('pupitre_espalda', 'a student desk-chair with a black plastic seat and a small black writing tablet arm, metal legs, seen from BEHIND (the student would face away from the camera, toward the top)', 'alto', 52),
    ('pupitre_frente', 'the same student desk-chair seen from the FRONT (facing the camera)', 'alto', 52),
    ('escritorio_profesor', "a teacher's desk with an orange-brown wooden top and dark metal frame, wide", 'ancho', 96),
    ('silla_profesor', 'a black office chair for the teacher', 'alto', 46),
    ('pizarron', 'a wide white whiteboard with a thin aluminium frame and a marker tray, hanging on a wall, seen from the front', 'ancho', 160),
    ('minisplit', 'a white wall-mounted split air conditioner unit, seen from the front', 'ancho', 72),
    ('ventana_persiana', 'a window with a beige roller blind half down and a white frame, seen from the front', 'ancho', 96),
    ('ventilador_techo', 'a white four-blade ceiling fan seen from directly below, flat, round', 'ancho', 72),
])
hoja('laboratorio', [33, 36], [
    ('pc_espalda', 'a section of long white computer desk with a black PC tower and a black monitor seen from BEHIND (screen facing away from the camera), keyboard', 'ancho', 64),
    ('pc_frente', 'the same white computer desk section with the monitor screen FACING the camera (blue screen), keyboard, PC tower', 'ancho', 64),
    ('pc_lado', 'the same white computer desk section seen from the side, the monitor screen facing RIGHT', 'alto', 64),
    ('silla_oficina_espalda', 'a black office chair with wheels seen from behind', 'alto', 46),
    ('silla_oficina_frente', 'the same black office chair seen from the front', 'alto', 46),
    ('mesa_maestro_lab', "a small white teacher's table with a closed grey laptop on it", 'ancho', 80),
])
hoja('cic', [6, 5, 18], [
    ('mostrador_curvo', 'a long curved white reception counter with a brown wooden edge on top, with a monitor and papers on it', 'ancho', 176),
    ('archivero', 'a beige metal four-drawer filing cabinet', 'alto', 64),
    ('copiadora', 'a large grey and white office photocopier', 'alto', 60),
    ('cajas_carton', 'a stack of three brown cardboard boxes', 'alto', 48),
    ('lockers_cerrados', 'a beige metal locker column with three closed doors with small vent slits and small white labels', 'alto', 100),
    ('locker_abierto', 'the same beige locker column with the middle door open, showing a backpack inside', 'alto', 100),
    ('estante_equipo', 'a grey metal shelf full of computer parts, keyboards and small boxes', 'alto', 96),
    ('escritorio_oficina_pc', 'an office desk with a dark wooden top, a black monitor and papers', 'ancho', 88),
])
hoja('site', [39], [
    ('rack_apagado', 'a tall black server rack with cables and all lights off', 'alto', 116),
    ('rack_prendido', 'the same tall black server rack with many green and blue lights on and bundles of white and blue network cables', 'alto', 116),
    ('ups', 'a black UPS battery box on the floor', 'alto', 40),
    ('caja_telecom', 'a grey wall-mounted telecom distribution box', 'alto', 48),
    ('tablero_apagado', 'a big grey main electrical panel on the wall with a large lever DOWN and a red light', 'alto', 72),
    ('tablero_prendido', 'the same main electrical panel with the large lever UP and a green light', 'alto', 72),
    ('cables_piso', 'a messy bundle of blue and white network cables on the floor', 'ancho', 64),
], extra='')
hoja('neveria', [22, 21, 20], [
    ('mesa_sillas_blancas', 'a square white plastic table with four white plastic chairs around it', 'ancho', 104),
    ('silla_blanca', 'a single white plastic chair', 'alto', 44),
    ('barra_verde', 'a long serving counter with a white top and a front covered in dark green square tiles', 'ancho', 176),
    ('refri_refresco', 'a tall red soda refrigerator with a glass door and bottles inside', 'alto', 104),
    ('congelador_helados', 'a white ice cream freezer with a glass top showing colorful ice cream tubs', 'ancho', 84),
    ('menu_pared', 'a framed menu board hanging on a wall, with colorful pictures of ice cream and lines instead of text', 'ancho', 64),
    ('maceta_flores', 'a potted indoor plant with green leaves and pink flowers', 'alto', 76),
    ('caja_registradora', 'a small cash register', 'ancho', 32),
])
hoja('oficinas', [7, 8, 10], [
    ('escritorio_l', 'an L-shaped office desk with a wooden top, a monitor and folders', 'ancho', 104),
    ('silla_visita', 'a simple office visitor chair with dark blue fabric', 'alto', 44),
    ('sillon_espera', 'a three-seat waiting room bench with dark blue seats and a metal frame', 'ancho', 112),
    ('mesa_juntas', 'a long dark wooden conference table with black chairs around it', 'ancho', 200),
    ('librero', 'a tall wooden bookshelf full of binders and folders', 'alto', 100),
    ('garrafon_agua', 'a water dispenser with a big blue water jug on top', 'alto', 68),
    ('cancel_vidrio', 'a section of glass partition wall with an aluminium frame, seen from the front', 'ancho', 64),
    ('planta_oficina', 'a tall potted office plant', 'alto', 68),
])
hoja('banos', [], [
    ('inodoro', 'a white toilet seen from the front', 'alto', 48),
    ('mingitorio', 'a white urinal on a wall', 'alto', 56),
    ('lavabo_espejo', 'a white sink on a counter with a mirror above it', 'ancho', 64),
    ('cubiculo_cerrado', 'a grey toilet stall partition with its door closed', 'alto', 100),
    ('cubiculo_abierto', 'the same grey toilet stall with its door open', 'alto', 100),
    ('secador_manos', 'a small white wall-mounted hand dryer', 'alto', 30),
])
hoja('exterior', [1, 24, 41], [
    ('mesa_redonda_bancas', 'a round grey metal picnic table with three curved grey metal benches around it', 'ancho', 132),
    ('banca_metal', 'a long grey metal bench with legs', 'ancho', 96),
    ('poste_luz', 'a tall modern white street lamp post with a round lamp head', 'alto', 200),
    ('bote_exterior', 'a grey outdoor trash can', 'alto', 48),
    ('directorio', 'a tall navy blue and white information sign board standing on two legs, with blank lines instead of text', 'alto', 116),
    ('condensador_ac', 'an outdoor air conditioner condenser unit, white with a round fan grille', 'ancho', 56),
    ('barandal', 'a straight section of stainless steel railing with two horizontal bars', 'ancho', 96),
    ('tapa_registro', 'a flat square metal drain cover on the ground', 'ancho', 44),
])
hoja('vegetacion', [0, 40, 30], [
    ('palma_alta', 'a tall royal palm tree with a smooth grey trunk and a green crown', 'alto', 288),
    ('palma_baja', 'a shorter young royal palm tree', 'alto', 192),
    ('arbol_grande', 'a big round leafy tropical tree with a dense dark green crown', 'ancho', 192),
    ('arbol_mediano', 'a medium leafy tropical tree', 'ancho', 128),
    ('arbusto', 'a round green bush', 'ancho', 64),
    ('arbol_joven', 'a young thin tree tied to a wooden stake', 'alto', 96),
    ('jardinera_piedra', 'a low square planter made of rough grey-beige limestone rocks with grass inside', 'ancho', 96),
    ('mata_flores', 'a small plant with red flowers', 'ancho', 44),
], aspect='16:9')
hoja('hitos', [13, 17, 37], [
    ('arco_entrada', 'a big navy blue rectangular entrance arch with a small guard booth with a window on its left side, the sign band on top is plain navy blue and BLANK (no text), a white metal fence on each side', 'ancho', 320),
    ('corazon_tapitas', 'a big heart-shaped metal mesh cage filled with colorful plastic bottle caps standing on a low round beige concrete platform', 'ancho', 160),
    ('arco_salida', 'a small navy blue pedestrian gate arch with an open grey metal gate', 'ancho', 160),
    ('reja_blanca', 'a straight section of white metal picket fence', 'ancho', 128),
], aspect='21:9')
hoja('estacionamiento', [15, 16], [
    ('pickup_blanca', 'a white pickup truck seen from above at a 3/4 angle, pointing UP (hood toward the top of the image)', 'alto', 190),
    ('sedan_rojo', 'a red sedan car seen from above at a 3/4 angle, pointing UP', 'alto', 176),
    ('suv_gris', 'a grey SUV seen from above at a 3/4 angle, pointing UP', 'alto', 184),
    ('tope', 'a yellow and black striped speed bump, horizontal', 'ancho', 96),
    ('reja_cerrada', 'a wide sliding metal gate, closed, white bars', 'ancho', 192),
    ('reja_abierta', 'the same sliding gate pushed open to the side (mostly hidden, only a short section visible)', 'ancho', 80),
    ('cono', 'an orange traffic cone with a white stripe', 'alto', 34),
    ('caseta_vigilancia', 'a small white and navy blue guard booth with a window', 'alto', 140),
])
hoja('cancha', [3, 4], [
    ('canasta_basquet', 'a basketball hoop with a white backboard on a tall white steel post', 'alto', 200),
    ('poste_techo', 'a tall white steel column that holds a roof', 'alto', 200),
    ('malla', 'a straight section of tall green chain-link fence', 'ancho', 96),
    ('porteria', 'a small white futsal goal with a net', 'ancho', 128),
], aspect='21:9')
hoja('senaletica', [26, 27, 18], [
    ('tablero_avisos', 'a cork bulletin board on a wall with colorful posters and papers (no readable text)', 'ancho', 72),
    ('salida_emergencia', 'a green emergency exit sign with a white running figure pictogram and an arrow', 'ancho', 40),
    ('reloj_pared', 'a round white wall clock', 'ancho', 28),
    ('extintor_pared', 'a red fire extinguisher hanging on a wall under a small red sign', 'alto', 56),
    ('bebedero', 'a steel drinking fountain on a wall', 'alto', 48),
    ('botiquin', 'a white first aid box with a red cross on a wall', 'ancho', 32),
])
# texturas (las vuelvo repetibles yo; el agente solo genera)
JOBS.append(dict(id='mapa__texturas', categoria='mapa', entidad='mapa', animacion='texturas', frames=4, escala='textura', aspect_ratio='1:1',
    resolution='1k', referencias=['mapa/referencias/estilo_mapa.png', collage('texturas', [2, 14, 0])],
    prompt=(STYLE + "Create a 2x2 grid of four square seamless TILEABLE ground textures for a 2D top-down pixel art game, seen straight "
            "from above (orthographic, no perspective), each texture filling its whole square, separated by thin magenta lines: "
            "top-left) beige-tan stamped concrete with an irregular flagstone pattern of thin darker joints; "
            "top-right) a wall face of rough grey-beige limestone rocks with dark mortar gaps; "
            "bottom-left) green grass with small darker blades and tiny light specks; "
            "bottom-right) brown dry dirt with a few small pebbles and dry leaves. Chunky pixels, flat colors, no text, no objects, no shadows from outside."),
    salida_raw='generado/raw/mapa/texturas.png', nombres=['concreto_estampado', 'muro_piedra', 'pasto', 'tierra'],
    tamanos={}, filas=2, fase='T'))

m = {'proyecto': 'FDI-Z', 'lote': 'mapa', 'modelo': 'google/nano-banana-2.1/edit', 'total': len(JOBS), 'limite_generaciones': 20, 'jobs': JOBS}
json.dump(m, open(f'{OUT}/pipeline/manifest_mapa.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(JOBS), sum(j['frames'] for j in JOBS), [j['id'] for j in JOBS])
print(max(len(j['prompt']) for j in JOBS))
