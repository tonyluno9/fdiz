import json
STYLE_REF = "assetsimage/alessandro.png"
BG = "Flat solid magenta background (#FF00FF) filling the whole image, no floor shadow, no text, no numbers, no borders, no extra characters."
KEEP = ("Use image 1 as the exact character reference: keep the same face, hair, glasses, skin tone, outfit, colors, body proportions and chunky pixel art style. Do not redesign or change the character. ")
def strip(n):
    return (f"Create a horizontal sprite strip for a 2D top-down pixel art video game: exactly {n} frames of this same character in one single row, left to right, evenly spaced with clear empty space between frames, every frame the same size and scale, all feet on the same horizontal baseline. " + BG + " Chunky pixel art with flat block shading and dark outlines, exactly like image 1. ")
A = {
 'quieto': (4, 'standing', "Idle breathing, front view facing the camera. Frame 1: neutral standing pose. Frame 2: body slightly lower (inhale). Frame 3: neutral pose with eyes closed (blink). Frame 4: body slightly lower."),
 'caminar_abajo': (6, 'standing', "Walking toward the viewer (front view, facing the camera), full walk cycle. Frame 1: right foot forward touching the floor. Frame 2: body at its lowest point. Frame 3: legs passing each other. Frame 4: left foot forward touching the floor. Frame 5: body at its lowest point. Frame 6: legs passing each other. Arms swing opposite to the legs."),
 'caminar_arriba': (6, 'standing', "Walking away from the viewer (back view: we see the back of the head and the back of the body), same 6-frame walk cycle: right foot forward, lowest point, passing, left foot forward, lowest point, passing. Arms swing opposite to the legs."),
 'caminar_lado': (6, 'standing', "Walking to the right (side profile view, facing right), same 6-frame walk cycle: right foot forward, lowest point, passing, left foot forward, lowest point, passing. Arms swing opposite to the legs."),
 'pegar_lado': (4, 'standing', "Attacking to the right (side profile, facing right) with a strong punch, empty hands. Frame 1: wind-up, pulling the arm back. Frame 2: swinging forward. Frame 3: full extension with a small white motion arc in front of the fist. Frame 4: recovering to the ready pose."),
 'pegar_abajo': (4, 'standing', "Attacking toward the viewer (front view) with a strong punch, empty hands. Frame 1: wind-up. Frame 2: swinging forward. Frame 3: full extension with a small white motion arc. Frame 4: recovering."),
 'pegar_arriba': (4, 'standing', "Attacking away from the viewer (back view) with a strong punch, empty hands. Frame 1: wind-up. Frame 2: swinging forward. Frame 3: full extension with a small white motion arc. Frame 4: recovering."),
 'caer_levantarse': (6, 'frames_1_6_standing', "Getting knocked down and getting back up, front view. Frame 1: hit flinch, leaning back. Frame 2: knees buckling. Frame 3: falling backwards. Frame 4: lying flat on the floor seen from above (body horizontal, eyes closed). Frame 5: pushing up from the floor. Frame 6: standing again."),
 'festejo': (4, 'standing', "Victory celebration, front view. Frame 1: fist pump. Frame 2: jumping with both arms up. Frame 3: landing with a big smile. Frame 4: thumbs up."),
}
ZA = {
 'caminar_abajo': (6, 'standing', "Zombie walking toward the viewer (front view) with a slow shuffling zombie walk, arms stretched forward, 6-frame walk cycle: right foot forward, lowest point, passing, left foot forward, lowest point, passing."),
 'caminar_arriba': (6, 'standing', "Zombie walking away from the viewer (back view), shuffling zombie walk, 6-frame walk cycle."),
 'caminar_lado': (6, 'standing', "Zombie walking to the right (side profile, facing right), shuffling zombie walk with arms stretched forward, 6-frame walk cycle."),
 'atacar_lado': (4, 'standing', "Zombie attacking to the right (side profile): Frame 1: leaning back. Frame 2: lunging forward. Frame 3: clawing/biting at full reach with a small motion arc. Frame 4: recovering."),
 'atacar_abajo': (4, 'standing', "Zombie attacking toward the viewer (front view): Frame 1: leaning back. Frame 2: lunging forward. Frame 3: clawing at full reach with a small motion arc. Frame 4: recovering."),
 'golpe_morir': (6, 'frame_1_standing', "Zombie getting hit and defeated, front view, school-friendly (no blood, no gore). Frame 1: hit flinch. Frame 2: stagger backwards. Frame 3: falling. Frame 4: lying flat on the floor seen from above. Frame 5: body dissolving into green smoke. Frame 6: only a small green smoke puff left."),
}
# habilidades y especiales (pose del personaje) + efectos (sin personaje)
CH = {
 'tony': dict(
   habilidad="Ability 'Cook': Frame 1: pulls out a spatula. Frame 2: flips a burger in the air. Frame 3: catches it on a plate. Frame 4: holds the plate with a juicy burger toward the camera. Frame 5: proud smile with a thumbs up. Front view.",
   especial="Ability 'Gym mode' transformation, front view: image 2 shows his final shirtless muscular form. Frame 1: normal Tony crouching, powering up. Frame 2: golden aura appears around him. Frame 3: his shirt tears apart, body growing. Frame 4: he becomes exactly the shirtless muscular character from image 2 with a bright golden anime-style aura. Frame 5: flexing both biceps with the golden aura.",
   esp_refs=['assetsimage/tony.png','assetsimage/tonyfuerte.png'],
   efecto_habilidad="A pixel art burger on a small white plate with steam puffs rising: 4 frames of the steam looping upward.",
   efecto_especial="A bright golden anime-style power aura with flame-like spikes and sparkles, empty inside (no character), 4-frame looping flicker."),
 'miranda': dict(
   habilidad="Ability 'Lullaby', front view: Frame 1: hands together near her mouth. Frame 2: singing softly with eyes closed. Frame 3: musical notes and a soft blue wave coming out. Frame 4: bigger blue wave with 'Zzz'. Frame 5: calm smile.",
   especial="Ability 'Minigun', side profile facing right: Frame 1: pulls out a huge gray six-barrel minigun. Frame 2: holds it with both hands, aiming right. Frame 3: firing with a bright yellow muzzle flash. Frame 4: firing, bullets flying right. Frame 5: firing with shell casings falling.",
   efecto_habilidad="A soft blue expanding circular sleep wave with small 'Zzz' letters floating up, 4 frames growing outward.",
   efecto_especial="Minigun muzzle flash and a line of small yellow bullets flying to the right, 4-frame loop."),
 'cesar': dict(
   habilidad="Ability 'Hack', front view: Frame 1: pulls out a silver laptop. Frame 2: opens it. Frame 3: typing fast, glowing green lines of code appear floating over him. Frame 4: more green code around him. Frame 5: closes the laptop with a confident smile.",
   especial="Ability 'School control', front view: Frame 1: holds the silver laptop up high. Frame 2: presses a key, the screen glows. Frame 3: a burst of electric blue light comes out. Frame 4: sound waves spread from the laptop. Frame 5: confident pose.",
   efecto_habilidad="Glowing green lines of computer code and binary digits floating and fading, 4-frame loop.",
   efecto_especial="Electric blue light burst with expanding sound-wave rings, 4 frames expanding outward."),
 'alan': dict(
   habilidad="Ability 'Freebie', front view: Frame 1: looks around sneakily. Frame 2: reaches out a hand. Frame 3: a random snack appears in his hand with sparkles. Frame 4: holds it up happily. Frame 5: winks.",
   especial="Ability 'Refund', front view: Frame 1: pulls out a long paper receipt. Frame 2: waves it in the air. Frame 3: small items (snack, soda can, ball) pop out around him. Frame 4: throws them to the sides. Frame 5: satisfied pose.",
   efecto_habilidad="A yellow sparkle burst with small stars and a coin, 4 frames popping and fading.",
   efecto_especial="A long white paper receipt flying with small item icons (snack, soda can, ball) bursting around it, 4 frames."),
 'castillo': dict(
   habilidad="Ability 'Swallow', front view, cartoon and funny: Frame 1: opens his mouth very wide. Frame 2: huge cartoon chomp. Frame 3: cheeks full, chewing. Frame 4: swallowing. Frame 5: patting his belly happily.",
   especial="Ability 'Health app', front view: Frame 1: pulls out his phone. Frame 2: holds it up toward the front. Frame 3: a blue scanning beam comes out of the phone. Frame 4: the beam sweeps with small green plus symbols. Frame 5: satisfied smile looking at the phone.",
   efecto_habilidad="A cartoon chomp effect: white bite marks and small crumbs flying, 4 frames.",
   efecto_especial="A blue phone scanning beam sweeping forward with small green plus (+) health symbols, 4-frame loop."),
 'alessandro': dict(
   habilidad="Ability 'Joke', front view: Frame 1: raises a finger as if starting a joke. Frame 2: telling the joke with hand gestures. Frame 3: delivering the punchline with a big grin. Frame 4: laughing with his eyes closed. Frame 5: laughing harder, holding his belly.",
   especial="Ability 'Watch', front view: Frame 1: raises his left wrist showing the gold wristwatch. Frame 2: taps the watch. Frame 3: the watch glows gold. Frame 4: a golden clock-face ring appears around him. Frame 5: confident pose while everything around turns gray.",
   efecto_habilidad="Yellow comic laughter burst lines and small bouncing laugh symbols, 4 frames.",
   efecto_especial="A large golden clock-face ring with clock hands, expanding outward, 4 frames."),
 'gabo': dict(
   habilidad="Ability 'Super speed', side profile running to the right: Frame 1: crouch start. Frame 2: explodes into a sprint with speed lines. Frame 3: running very fast with faded afterimages behind him. Frame 4: same with longer speed lines. Frame 5: skidding to a stop.",
   especial="Ability 'Apple ecosystem', front view: Frame 1: pulls out a silver laptop. Frame 2: holds a phone and earbuds case. Frame 3: throws the laptop forward. Frame 4: throws the phone and a tablet. Frame 5: confident pose with sparks in the air.",
   efecto_habilidad="Horizontal speed lines and a dust trail moving to the left, 4-frame loop.",
   efecto_especial="Thrown gadgets (silver laptop, phone, tablet, white earbuds) on the floor emitting electric sparks and sound waves, 4-frame loop."),
 'carlos': dict(
   habilidad="Ability 'Master key', front view: Frame 1: reaches to his belt. Frame 2: pulls out a big key ring. Frame 3: holds up a golden key that glints. Frame 4: turns the key in the air. Frame 5: satisfied smile.",
   especial="Ability 'Tank', front view: Frame 1: plants his feet firmly. Frame 2: crosses his arms in front. Frame 3: a translucent blue shield bubble appears around him. Frame 4: the shield glows stronger. Frame 5: confident pose inside the shield.",
   efecto_habilidad="A golden key glint with small sparkles, 4 frames.",
   efecto_especial="A translucent blue protective shield bubble, empty inside, 4-frame pulsing loop."),
}
jobs=[]
FPS={'quieto':(6,True),'caminar_abajo':(10,True),'caminar_arriba':(10,True),'caminar_lado':(10,True),'pegar_lado':(14,False),'pegar_abajo':(14,False),'pegar_arriba':(14,False),
 'caer_levantarse':(8,False),'festejo':(8,True),'habilidad':(10,False),'especial':(10,False),'efecto_habilidad':(10,True),'efecto_especial':(10,True),
 'atacar_lado':(10,False),'atacar_abajo':(10,False),'golpe_morir':(10,False),'gritar':(8,False)}
def add(id, cat, ent, anim, n, frames_info, prompt, refs, ar='21:9', nombres=None):
    fps,loop=FPS.get(anim,(0,False))
    if ent=='corredor' and anim.startswith('caminar'): fps=14
    if cat in('zombies',) and anim.startswith('caminar') and ent!='corredor': fps=8
    j=dict(id=id, categoria=cat, entidad=ent, animacion=anim, frames=n, escala=frames_info,
        aspect_ratio=ar, resolution='1k', referencias=refs, prompt=prompt,
        salida_raw=f"generado/raw/{cat}/{ent}/{anim}.png")
    if fps: j['fps']=fps; j['loop']=loop
    if nombres: j['nombres']=nombres
    jobs.append(j)
playable=['tony','miranda','cesar','alan','castillo','alessandro','gabo','carlos']
for ch in playable:
    ref=f"assetsimage/{ch}.png"
    for anim,(n,sc,d) in A.items():
        add(f"{ch}__{anim}",'personajes',ch,anim,n,sc, KEEP+strip(n)+"Animation: "+d, [ref])
    c=CH[ch]
    add(f"{ch}__habilidad",'personajes',ch,'habilidad',5,'standing', KEEP+strip(5)+"Animation: "+c['habilidad'], [ref])
    erefs=c.get('esp_refs',[ref])
    add(f"{ch}__especial",'personajes',ch,'especial',5,'standing', KEEP+strip(5)+"Animation: "+c['especial'], erefs)
    for k in ['efecto_habilidad','efecto_especial']:
        p=("Use image 1 ONLY as a pixel art style reference (same chunky pixel size, flat block shading, dark outlines). "
           f"Create a horizontal strip of exactly 4 animation frames of a visual effect only, with NO character: {c[k]} "
           "Frames in one single row, evenly spaced, equal size, clear empty space between them. "+BG)
        add(f"{ch}__{k}",'efectos',ch,k,4,'effect', p, [ref])
# Tony modo gym
for anim in ['quieto','caminar_abajo','caminar_arriba','caminar_lado','pegar_lado']:
    n,sc,d=A[anim]
    add(f"tonyfuerte__{anim}",'personajes','tonyfuerte',anim,n,sc, KEEP+strip(n)+"Animation: "+d+" Keep the bright golden anime-style aura around him in every frame.", ["assetsimage/tonyfuerte.png"])
# profes (rol pendiente): set basico
for p in ['canepa','joel','justino']:
    for anim in ['quieto','caminar_abajo','caminar_arriba','caminar_lado','pegar_lado','pegar_abajo','pegar_arriba','caer_levantarse','festejo']:
        n,sc,d=A[anim]
        add(f"{p}__{anim}",'profes',p,anim,n,sc, KEEP+strip(n)+"Animation: "+d, [f"assetsimage/{p}.png"])
# zombies
zmap={'Z1':'normal','Z2':'corredor','Z3':'griton','Z4':'gordo','Z5':'conserje'}
for z,name in zmap.items():
    ref=f"assetsimage/{z}.png"
    for anim,(n,sc,d) in ZA.items():
        extra=""
        if z=='Z2': extra=" This is the fast runner zombie: keep his hunched running posture and make the movement fast and frantic."
        if z=='Z4': extra=" This is the big heavy zombie: slow and heavy movement, keep his width."
        if z=='Z5' and anim.startswith('atacar'): extra=" He attacks by swinging his mop like a weapon."
        add(f"{name}__{anim}",'zombies',name,anim,n,sc, KEEP+strip(n)+"Animation: "+d+extra, [ref])
add("griton__gritar",'zombies','griton','gritar',4,'standing', KEEP+strip(4)+"Animation: Screaming zombie, front view. Frame 1: inhaling, leaning back. Frame 2: mouth wide open screaming with sound lines. Frame 3: bigger scream with more sound lines and hands on his head. Frame 4: recovering.", ["assetsimage/Z3.png"])
# alumno curado
for anim in ['quieto','caminar_abajo','caminar_arriba','caminar_lado','pegar_lado']:
    n,sc,d=A[anim]
    add(f"curado__{anim}",'zombies','curado',anim,n,sc, KEEP+strip(n)+"Animation: "+d, ["assetsimage/Z0.png"])
# objetos (hojas de items)
IT = [
 ('armas',5,"broom, wooden school chair, metal ruler, baseball bat, red fire extinguisher",['escoba','silla','regla','bate','extintor']),
 ('lanzables',4,"soccer ball, black stapler, thick red book, a single small metal staple",['balon','engrapadora','libro','grapa']),
 ('comida',5,"juicy burger, Mexican torta sandwich, juice box, chocolate chip cookies, brown paper bag of food",['hamburguesa','torta','jugo','galletas','bolsa_comida']),
 ('objetivos',5,"red gasoline can, ring of janitor keys, white electronic key card, red restricted-area key, gold coin",['bidon','llaves_conserjeria','tarjeta','llave_restringida','moneda']),
 ('contenedores',6,"closed blue school locker, open empty blue locker, closed vending machine full of snacks, open broken vending machine, closed backpack on the floor, open backpack",['locker_cerrado','locker_abierto','maquina_cerrada','maquina_abierta','mochila_cerrada','mochila_abierta']),
 ('props_especiales',6,"huge gray six-barrel minigun, silver laptop (open), black smartphone, white wireless earbuds case, silver tablet, smartphone showing a health app with a green cross",['minigun','laptop','celular','audifonos','tablet','cel_app_salud']),
 ('efectos_generales',6,"white curved attack swing arc, green slime splash (no blood), small dust cloud, blue 'Zzz' sleep symbol, yellow dizzy stars circle, red exclamation mark",['arco_golpe','salpicadura_verde','polvo','zzz','estrellas_mareo','exclamacion']),
]
for name,n,desc,noms in IT:
    p=("Use image 1 ONLY as a pixel art style reference (same chunky pixel size, flat block shading, dark outlines, same colors palette feel). "
       f"Create exactly {n} separate game item sprites in one single row, left to right, each one centered in its own equal-width cell with clear empty space between them, all drawn at a consistent scale as seen in a top-down 2D game: {desc}. "+BG)
    add(f"objetos__{name}",'objetos','objetos',name,n,'items',p,[STYLE_REF],nombres=noms)
add("objetos__camion",'objetos','objetos','camion',1,'items',
    "Use image 1 ONLY as a pixel art style reference (same chunky pixel size, flat block shading, dark outlines). Create one yellow school bus seen exactly from above (top-down view), vertical orientation with the front facing down, windows along both sides, black wheels slightly visible. "+BG, [STYLE_REF], ar='9:16', nombres=['camion'])
json.dump({"proyecto":"FDI-Z","modelo":"google/nano-banana-2.1/edit","total":len(jobs),"jobs":jobs}, open('manifest.json','w'), ensure_ascii=False, indent=1)
from collections import Counter
print(len(jobs), Counter(j['categoria'] for j in jobs))
