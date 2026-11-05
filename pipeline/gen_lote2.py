import json, copy
M = {j['id']: j for j in json.load(open('manifest.json'))['jobs']}
BG = "Flat solid magenta background (#FF00FF) filling the whole image, no floor shadow, no text, no numbers, no borders, no extra characters."
KEEP = ("Use image 1 as the exact character reference: keep the same face, hair, glasses, skin tone, outfit, colors, body proportions and chunky pixel art style. Do not redesign or change the character. ")
def strip(n):
    return (f"Create a horizontal sprite strip for a 2D top-down pixel art video game: exactly {n} frames of this same character in one single row, left to right, each frame inside its own equal-width cell with wide clear empty space between cells, every frame the same size and scale, all feet on the same horizontal baseline, nothing touching the image edges. " + BG + " Chunky pixel art with flat block shading and dark outlines, exactly like image 1. ")
jobs=[]
def add(j): jobs.append(j)
BASE = {'tony':'tony','tonyfuerte':'tonyfuerte','miranda':'miranda','castillo':'castillo','alessandro':'alessandro','gabo':'gabo','carlos':'carlos','cesar':'cesar','alan':'alan',
        'normal':'Z1','corredor':'Z2','griton':'Z3','gordo':'Z4','conserje':'Z5','curado':'Z0'}
CAT = lambda e: 'zombies' if e in ('normal','corredor','griton','gordo','conserje','curado') else 'personajes'
# --- A. hojas de giro (referencia de vistas) ---
GIRO = ['tony','tonyfuerte','miranda','castillo','alessandro','gabo','carlos','normal','corredor','conserje','curado']
for e in GIRO:
    extra = ""
    if e=='tonyfuerte': extra=" Keep the bright golden anime-style aura around him in all three views."
    if e=='conserje': extra=" He holds his mop (with the mop head clearly visible) in all three views."
    if e in ('normal','corredor'): extra=" Zombie standing pose with arms stretched forward in all three views."
    p = (KEEP + "Create a character turnaround sheet for a 2D top-down pixel art game: the same character drawn three times in one single row, same size and scale, feet on the same baseline, wide empty space between them, nothing touching the image edges. "
         "Left: front view, exactly like image 1. Middle: true side profile facing RIGHT (only one eye visible, nose pointing right, body turned 90 degrees). Right: back view (we see the back of the head and the back of the body). Neutral standing pose." + extra + " " + BG)
    add(dict(id=f"{e}__giro", categoria='giros', entidad=e, animacion='giro', frames=3, escala='standing', aspect_ratio='21:9', resolution='1k',
             referencias=[f"assetsimage/{BASE[e]}.png"], prompt=p, salida_raw=f"generado/raw/giros/{e}/giro.png", fase='A'))
# --- B. rehacer las 35 marcadas ---
SIDE = " Use image 2 only as a guide for the views: for this animation use the RIGHT SIDE PROFILE view from image 2 in every frame (only one eye visible, nose pointing right, body turned 90 degrees, never facing the camera)."
BACK = " Use image 2 only as a guide for the views: for this animation use the BACK view from image 2 in every frame."
FRONT = " Use image 2 only as a guide for the views: for this animation use the FRONT view from image 2 in every frame."
FIX = {
 'tonyfuerte__pegar_lado': (SIDE+" Frame 1: fist pulled back at the waist. Frame 2: swinging forward. Frame 3: full punch to the right with a small white motion arc. Frame 4: side-view guard pose. Keep the golden aura in every frame.", 'giro'),
 'normal__atacar_abajo': (FRONT+" Both arms reach straight toward the camera (hands in front of the chest, foreshortened), body symmetrical, never turned to the side.", 'giro'),
 'normal__golpe_morir': (" The lying body in frame 4 is drawn small enough to fit completely inside its own cell and never touches frames 3 or 5.", None),
 'conserje__caminar_lado': (SIDE+" He holds his mop with the mop head clearly visible in every frame.", 'giro'),
 'conserje__golpe_morir': (" The lying body in frame 4 (with its mop) is drawn small enough to fit completely inside its own cell and never touches frames 3 or 5.", None),
 'tony__pegar_lado': (SIDE, 'giro'), 'miranda__pegar_lado': (SIDE, 'giro'),
 'miranda__caer_levantarse': (" Frame 4 must show her WHOLE body (head, torso, legs) lying flat on the floor seen from above, inside its own cell. Do not add accessories that are not in image 1 (no hair bow).", None),
 'miranda__especial': (" Leave wide empty space at the right side of every frame so the minigun barrel and muzzle flash are fully visible; nothing touches the image edges.", None),
 'cesar__efecto_habilidad': (" Use simple, sparse, chunky pixel code symbols (only 0, 1, <, >, / characters), not dense text; every frame has a similar amount of symbols and frame 4 is still clearly visible.", None),
 'cesar__efecto_especial': (" Keep every ring small enough that nothing touches the image edges; wide empty margins around each frame.", None),
 'castillo__caminar_lado': (SIDE, 'giro'), 'castillo__pegar_lado': (SIDE, 'giro'),
 'castillo__pegar_arriba': (BACK+" The punch goes straight up, away from the viewer (toward the top of the image), not to the side.", 'giro'),
 'castillo__especial': (" The scanning beam is solid opaque light BLUE pixel-art light (not purple, not translucent) and goes forward from the phone without covering his face or arm.", None),
 'castillo__efecto_especial': (" Solid opaque light BLUE beam (not purple or violet, not translucent), with the same beam shape in all 4 frames so it loops smoothly.", None),
 'alessandro__caminar_lado': (SIDE, 'giro'), 'alessandro__pegar_lado': (SIDE, 'giro'),
 'alessandro__pegar_arriba': (BACK+" The punch goes straight up, away from the viewer (toward the top of the image), not to the side.", 'giro'),
 'alessandro__efecto_habilidad': (" Not an explosion: simple yellow comic laughter lines radiating like a sound burst, with small bouncing yellow laugh marks.", None),
 'gabo__caminar_lado': (SIDE, 'giro'), 'gabo__pegar_lado': (SIDE, 'giro'),
 'gabo__efecto_habilidad': (" Exactly 4 frames in ONE single horizontal row (not a grid).", None),
 'carlos__pegar_lado': (SIDE, 'giro'),
 'carlos__especial': (" The shield bubble in frames 3-5 stays fully inside its own frame cell, with clear empty space around it.", None),
 'carlos__efecto_especial': (" Draw the shield bubble as an OPAQUE light-blue pixel outline with a few opaque white highlight pixels, NOT translucent; the inside of the bubble is plain background.", None),
 'normal__caminar_lado': (SIDE+" His arms stay stretched forward in all 6 frames.", 'giro'),
 'normal__atacar_lado': (SIDE, 'giro'), 'corredor__atacar_lado': (SIDE, 'giro'),
 'griton__golpe_morir': (" The lying body in frame 4 is drawn small enough to fit completely inside its own cell and never touches frames 3 or 5. Frames 2 and 3 stay in front view.", None),
 'gordo__golpe_morir': (" The lying body in frame 4 is drawn small enough to fit completely inside its own cell and never touches frames 3 or 5.", None),
 'conserje__caminar_abajo': (FRONT+" He holds his mop in his right hand with the mop head visible in EVERY frame; arms do not point to the side.", 'giro'),
 'conserje__caminar_arriba': (BACK+" The mop (with its head) is visible in EVERY frame.", 'giro'),
 'conserje__atacar_lado': (SIDE+" He swings his mop to the right; the mop head is visible in every frame.", 'giro'),
 'curado__pegar_lado': (SIDE+" The white motion arc stays right in front of the fist inside frame 3.", 'giro'),
}
REPROCESAR_PRIMERO = {'gordo__golpe_morir','carlos__especial','gabo__efecto_habilidad'}
for jid,(fix,giro) in FIX.items():
    o = copy.deepcopy(M[jid]); n=o['frames']
    # reconstruir con el formato de tira reforzado
    prompt = o['prompt']
    if o['categoria']!='efectos':
        anim_part = prompt.split('Animation: ',1)[1]
        prompt = KEEP + strip(n) + "Animation: " + anim_part
    prompt += fix
    refs = list(o['referencias'])
    if giro:
        refs = [refs[0], f"generado/raw/giros/{o['entidad']}/giro.png"] + refs[1:]
        o['depende_de'] = f"{o['entidad']}__giro"
    o.update(prompt=prompt, referencias=refs, fase='B', reemplaza=o['salida_raw'])
    if jid in REPROCESAR_PRIMERO: o['intentar_reprocesar_primero']=True
    if jid=='gabo__efecto_habilidad': o['nota']='El raw actual viene en cuadrícula 2x2: primero intenta separarlo como cuadrícula de 2x2 antes de regenerar.'
    add(o)
# --- C. profes con su papel ---
PR = {
 'canepa__reparar': ('canepa', 6, True, 6, "Repairing the engine of a school bus, side profile facing right, kneeling on one knee with a wrench (the bus itself is NOT drawn). Frame 1: reaching forward with the wrench. Frame 2: turning the wrench. Frame 3: turning the wrench harder with small yellow sparks. Frame 4: tapping with the wrench, sparks. Frame 5: wiping his forehead with his arm. Frame 6: back to working with the wrench."),
}
for who in ['joel','justino']:
    PR[f'{who}__quieto_miedo'] = (who,4,True,5,"Scared and cowering in a corner, front view: crouched down hugging his knees, trembling, eyes wide with fear, looking left and right. Frames 1-4: small trembling loop with the head turning nervously.")
    PR[f'{who}__pedir_ayuda'] = (who,4,True,6,"Calling for help, front view, scared face: Frame 1: both arms up waving. Frame 2: arms waving to the other side, mouth open shouting. Frame 3: arms up waving. Frame 4: hands cupped around the mouth shouting.")
    PR[f'{who}__caminar_miedo_abajo'] = (who,6,True,10,"Walking scared toward the viewer (front view): hunched shoulders, arms close to the body, nervous face looking around, quick short steps. 6-frame walk cycle: right foot forward, lowest point, passing, left foot forward, lowest point, passing.")
    PR[f'{who}__caminar_miedo_arriba'] = (who,6,True,10,"Walking scared away from the viewer (back view): hunched shoulders, arms close to the body, head turning nervously, quick short steps. 6-frame walk cycle.")
    PR[f'{who}__caminar_miedo_lado'] = (who,6,True,10,"Walking scared to the right (true side profile facing right, only one eye visible): hunched shoulders, arms close to the body, nervous face, quick short steps. 6-frame walk cycle.")
    PR[f'{who}__rescatado'] = (who,4,False,6,"Relieved after being rescued, front view: Frame 1: surprised. Frame 2: big sigh of relief. Frame 3: hands together thanking. Frame 4: thumbs up with a smile.")
for jid,(who,n,loop,fps,d) in PR.items():
    anim=jid.split('__')[1]
    add(dict(id=jid, categoria='profes', entidad=who, animacion=anim, frames=n, escala='standing', aspect_ratio='21:9', resolution='1k',
             referencias=[f"assetsimage/{who}.png"], prompt=KEEP+strip(n)+"Animation: "+d, salida_raw=f"generado/raw/profes/{who}/{anim}.png", fps=fps, loop=loop, fase='C'))
# --- D. iconos de habilidades (24) en 4 hojas de 6 ---
ICON_STYLE = ("Use image 1 ONLY as a pixel art style reference (same chunky pixel size, flat block shading, dark outlines). "
  "Create exactly 6 square game ability icons in one single row, left to right, each one centered in its own equal-width cell with clear empty space between them, all the same size. "
  "Each icon is a rounded square tile with a dark navy background and a thick colored border, with one bold, simple, readable pixel art symbol centered inside. Border colors: ability = yellow border, special = red border, passive = cyan border. "
  "No text, no letters, no numbers. Flat solid magenta background (#FF00FF) outside the tiles.")
ICONS = [
 ('iconos_1', ['tony_habilidad','tony_especial','tony_pasiva','miranda_habilidad','miranda_especial','miranda_pasiva'],
  "Icons in order: 1) yellow border: a juicy burger with a spatula; 2) red border: a flexed muscular bicep with a golden aura; 3) cyan border: a stack of gold coins with a green up arrow; 4) yellow border: a blue crescent moon with 'Zzz' shapes; 5) red border: a gray six-barrel minigun firing; 6) cyan border: a green heart with a plus sign and a circular arrow."),
 ('iconos_2', ['cesar_habilidad','cesar_especial','cesar_pasiva','alan_habilidad','alan_especial','alan_pasiva'],
  "Icons in order: 1) yellow border: an open silver laptop with green code on the screen; 2) red border: a lightning bolt with speaker sound waves; 3) cyan border: a dotted path with an arrow ending at a map pin; 4) yellow border: a hand grabbing a snack with sparkles; 5) red border: a paper receipt with a circular return arrow; 6) cyan border: an eye with an X-ray glow and a small price tag."),
 ('iconos_3', ['castillo_habilidad','castillo_especial','castillo_pasiva','alessandro_habilidad','alessandro_especial','alessandro_pasiva'],
  "Icons in order: 1) yellow border: a big cartoon open mouth chomping; 2) red border: a smartphone with a green cross on the screen and a blue scan beam; 3) cyan border: a fork and knife over a steel shield; 4) yellow border: a laughing face with tears of joy; 5) red border: a golden wristwatch glowing; 6) cyan border: two smiling faces with circular arrows around them."),
 ('iconos_4', ['gabo_habilidad','gabo_especial','gabo_pasiva','carlos_habilidad','carlos_especial','carlos_pasiva'],
  "Icons in order: 1) yellow border: a running sneaker with speed lines; 2) red border: a silver laptop, a phone and white earbuds flying with sparks (no logos); 3) cyan border: two phones with an arrow passing between them; 4) yellow border: a golden key glinting; 5) red border: a blue shield; 6) cyan border: a solid brick wall with a small downward arrow."),
]
for name,noms,desc in ICONS:
    add(dict(id=f"iconos__{name}", categoria='iconos', entidad='iconos', animacion=name, frames=6, escala='icons', aspect_ratio='21:9', resolution='1k',
             referencias=["assetsimage/alessandro.png"], prompt=ICON_STYLE+" "+desc, salida_raw=f"generado/raw/iconos/{name}.png", nombres=noms, fase='D'))
# --- E. objetos que faltaban ---
OBJ = ("Use image 1 ONLY as a pixel art style reference (same chunky pixel size, flat block shading, dark outlines). "
  "Create exactly {n} separate game sprites in one single row, left to right, each one centered in its own equal-width cell with clear empty space between them, drawn front-facing as seen in a top-down 2D RPG, consistent scale: {d}. " + BG)
OB = [
 ('interruptores_servidor', ['interruptor_apagado','interruptor_prendido','servidor_apagado','servidor_prendido'],
  "a wall breaker box switch with its lever DOWN and a red light; the same breaker box with its lever UP and a green light; a black server rack turned off with dark lights; the same server rack turned on with many green and blue blinking lights"),
 ('computadoras_muebles', ['computadora_normal','computadora_alerta','computadora_llamada','barricada','mueble_pesado'],
  "a desk with a computer monitor showing a blue screen; the same desk and monitor with a flashing red alert screen; the same desk and monitor with a green screen showing a phone call icon; a wooden plank barricade with nails; a heavy tall wooden cabinet"),
 ('puertas_cofres', ['puerta_cerrada','puerta_abierta','puerta_restringida','puerta_rota','cofre_cerrado','cofre_abierto'],
  "a closed wooden school classroom door in its frame; the same door open; the same door closed with a big red padlock and red stripes (restricted); the same door broken off its hinges and lying in pieces; a closed wooden treasure chest; the same chest open and empty"),
]
for name,noms,d in OB:
    add(dict(id=f"objetos__{name}", categoria='objetos', entidad='objetos', animacion=name, frames=len(noms), escala='items', aspect_ratio='21:9', resolution='1k',
             referencias=["assetsimage/alessandro.png"], prompt=OBJ.format(n=len(noms), d=d), salida_raw=f"generado/raw/objetos/objetos/{name}.png", nombres=noms, fase='E'))
# --- F. mockups de interfaz (NO son assets finales) ---
GAME = ("FDI-Z is a local-multiplayer (up to 4 players) top-down 2D pixel art zombie survival game set in a Mexican university (Facultad de Ingeniería). "
        "The images attached are the real character sprites of the game: use them as the style and characters reference. ")
MK = [
 ('hud','opcion_a',['tony','miranda','Z1','gabo'],"Clean dark style: semi-transparent dark navy panels with thin white borders. Show a gameplay screenshot of a school hallway seen from above with the 4 characters fighting zombies, and the full HUD: one panel in each corner per player (small face portrait, name, green health bar, three ability icons: yellow-border ability, red-border special, cyan-border passive, and small inventory slots for weapon, throwable and food), an infestation bar at the top center with 5 levels, an objective box under it, a timer, a small minimap in a corner, and a team money counter with a coin icon."),
 ('hud','opcion_b',['tony','miranda','Z1','gabo'],"Bold retro arcade style: chunky bright colored frames (yellow, cyan, magenta, green per player), big pixel numbers, scanline feel. Same gameplay scene and the same full HUD elements: 4 corner player panels (portrait, name, health bar, ability, special and passive icons, inventory slots), infestation bar at top with 5 levels, objective box, timer, minimap, team money counter with a coin icon."),
 ('hud','opcion_c',['tony','miranda','Z1','gabo'],"School notebook style: panels look like taped sticky notes and graph paper, hand-drawn pencil borders, red pen marks. Same gameplay scene and the same full HUD elements: 4 corner player panels (portrait, name, health bar, ability, special and passive icons, inventory slots), infestation bar at top with 5 levels, objective box, timer, minimap, team money counter with a coin icon."),
 ('hud_jefe','opcion_a',['Z1','Z2','Z3','Z4','Z5'],"HUD for the 'Zombie Boss' player who controls the zombies with the mouse: a large minimap of the whole school on the right with red forbidden zones where the survivors can see, a gold counter with a coin icon, and a row of 7 purchasable cards at the bottom (runner zombie, screamer zombie, fat zombie, small horde, lock door, blackout, big horde), each with its price in gold and a cooldown overlay. Dark red and black evil theme."),
 ('hud_jefe','opcion_b',['Z1','Z2','Z3','Z4','Z5'],"HUD for the 'Zombie Boss' player: same elements (large school minimap with red forbidden zones, gold counter with coin icon, row of 7 zombie and trick cards with prices and cooldowns) but styled like a toxic green lab computer terminal."),
 ('seleccion','opcion_a',['tony','miranda','cesar','alan','castillo','alessandro','gabo','carlos'],"Character select screen: 8 character cards in a 4x2 grid, each card with the character sprite, the name (Tony, Miranda, César, Alan, Castillo, Alessandro, Gabo, Carlos), three small ability icons and small stat bars (health, speed, strength). Colored cursor frames for P1 (yellow) and P2 (cyan) on two of the cards, a 'BOT' tag on another. Dark purple background."),
 ('seleccion','opcion_b',['tony','miranda','cesar','alan','castillo','alessandro','gabo','carlos'],"Character select screen styled like a school ID card / student credential: 8 characters (Tony, Miranda, César, Alan, Castillo, Alessandro, Gabo, Carlos) shown as student ID cards with photo, name and three small ability icons; the selected one is bigger in the center. Player cursors P1 yellow and P2 cyan."),
 ('titulo','opcion_a',['tony','miranda','Z1','Z5'],"Title screen: the big game logo 'FDI-Z' on top of a pixel art university building facade at night with a full moon, broken windows and zombies walking in front, the 8 heroes posing below, and 'Presiona A para empezar' blinking text."),
 ('titulo','opcion_b',['tony','miranda','Z1','Z5'],"Title screen: close-up horror style, the logo 'FDI-Z' dripping green slime over a dark school hallway with lockers, zombie hands reaching from the bottom edge, and 'Presiona A para empezar' text."),
 ('logo','opciones_1',['alessandro'],"A logo design sheet: 4 different logo options for the game title 'FDI-Z', side by side, each one complete and separate: 1) green slime dripping pixel letters, 2) bold arcade pixel letters with a yellow and black hazard stripe, 3) university crest/shield with a zombie hand, 4) letters made of school lockers. Dark background."),
 ('logo','opciones_2',['alessandro'],"A logo design sheet: 4 more logo options for the game title 'FDI-Z', side by side: 1) cracked stone letters with blood-red 'Z' (no gore), 2) neon sign style in cyan and magenta, 3) chalkboard hand-written chalk letters with a zombie doodle, 4) minimal pixel letters with a bitten 'Z'. Dark background."),
 ('resultados','opcion_a',['tony','miranda','cesar','gabo'],"End-of-game results screen: big title '¡ESCAPARON!', total time, 4 player cards with portrait, zombies defeated, times knocked down and revives, and a list of funny awards (MVP, Más zombies tumbados, El empresario, Mejor chiste) with small trophy icons. Celebratory confetti, dark background."),
]
for tipo,opc,refs,d in MK:
    add(dict(id=f"mockup__{tipo}__{opc}", categoria='mockups', entidad=tipo, animacion=opc, frames=0, escala='mockup', aspect_ratio='21:9' if tipo=='logo' else '16:9', resolution='1k',
             referencias=[f"assetsimage/{r}.png" for r in refs],
             prompt=GAME+"Create a UI design MOCKUP image (concept, not final art) in pixel art style matching the attached sprites. "+d+" Spanish text where text appears.",
             salida_raw=f"generado/mockups/{tipo}/{opc}.png", fase='F'))
from collections import Counter
json.dump({"proyecto":"FDI-Z","lote":2,"modelo":"google/nano-banana-2.1/edit","total":len(jobs),"limite_generaciones":95,"jobs":jobs}, open('manifest_lote2.json','w'), ensure_ascii=False, indent=1)
print(len(jobs), Counter(j['fase'] for j in jobs))
