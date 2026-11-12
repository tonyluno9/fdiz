# FDI-Z · Videos animados para el equipo

Hay que convertir 16 imágenes del juego en videos cortos que se repitan en bucle (pantalla de título, modos, selección de personaje y fondos). Con Kling no salió bien, así que los hacemos con **Veo** (en la app de Gemini con Gemini Pro, o en **Google Flow**).

## Qué hay en esta carpeta
- `imagenes/` → las 16 imágenes, ya listas, en 1920×1080 (16:9). **No las edites.**
- `entregas/` → aquí van los videos terminados.
- `_contacto_personajes.png` → vista rápida de los 8 personajes (solo referencia).

## Cómo hacer cada video
1. Abre la herramienta y elige **video a partir de imagen** (image-to-video).
2. Sube la imagen de la tabla de abajo.
3. **En Google Flow:** usa *Frames to Video* y pon **la misma imagen como primer y último cuadro**. Así el video termina igual que empieza y se repite en bucle sin brinco. Si puedes elegir el modelo, Veo 3.1 Fast ahorra créditos.
4. Formato **16:9** horizontal, la mejor calidad que deje descargar (1080p si se puede).
5. Pega el prompt: **primero el prompt del video y después el BLOQUE COMÚN**, en un solo texto.
6. Puedes generar varias versiones de cada uno y quedarte con la mejor. No hace falta recortarlo: lo recortamos nosotros.

## BLOQUE COMÚN (va al final de TODOS los prompts)
```
Keep the exact same artwork: chunky 2D pixel art with dark outlines and flat colors, the same characters, faces, hairstyles, glasses, clothes, colors and composition as the image. Static locked camera: no zoom, no pan, no tilt, no camera shake, no cuts. Subtle idle motion only; nothing enters or leaves the frame and no new characters appear. The last frame must look exactly like the first frame so the clip loops seamlessly. No text, no subtitles, no logo, no music, no dialogue.
```

## Se rechaza un video si…
- La cámara se mueve o hace zoom.
- Un personaje cambia de cara, de ropa, de peinado o de color, o se deforma.
- Aparece gente nueva, texto o letras.
- Se vuelve 3D o realista en lugar de pixel art.
- Al final queda muy distinto del principio (brinca al repetirse).

## Cómo entregar
Guarda en `entregas/` con el número y el nombre de la imagen, por ejemplo `01_titulo.mp4` o `04_personaje_tony.mp4`. Si entregas varias versiones: `01_titulo_v1.mp4`, `01_titulo_v2.mp4`, y marca la que te guste más con `_mejor` (`01_titulo_v2_mejor.mp4`).

---

## Prioridad A (estos primero)

### 01 · Pantalla de título — `imagenes/01_titulo.png`
```
Animate this pixel art title screen. The four students on the left breathe gently and shift their weight slightly, ready to fight. The green-skinned zombies at the open glass door sway and shuffle in place with their arms stretched forward, and their red eyes glow. The old janitor zombie in the doorway sways slightly and moves his mop a little. The yellow light cones of the two street lamps flicker softly. The palm tree leaves and the round bushes sway in a light night breeze. The moon glows softly.
```

### 02 · Modo Escape — `imagenes/02_modo_escape.png`
```
Only the square illustration in the center moves; the dark hallway around it stays completely still. Inside the illustration, the four students run in place toward the camera in a looping running cycle: arms pumping, legs moving, hair bouncing, without moving forward. The zombies behind them lurch and stumble in place with arms reaching out. The three street lamp cones flicker. The yellow school bus stays parked and its lights blink.
```

### 03 · Modo Jefe de zombies — `imagenes/03_modo_jefe.png`
```
Only the square illustration in the center moves; the dark hallway around it stays completely still. Inside the illustration, the old janitor zombie grins and breathes heavily, his red eyes glow and pulse, and his clawed green hand hovers over the glowing green holographic school map, wiggling its fingers. The holographic map pulses with green light and the tiny green zombie figures on it shuffle and blink.
```

### 04 a 11 · Selección de personaje (uno por personaje)
Todos llevan esta frase **antes** del prompt del personaje:
```
The character stands in the center under a soft blue spotlight in a dark blurred classroom. The background stays completely still; only the spotlight shimmers softly with floating dust particles. The character stays in the same spot and the same front-facing pose, and only does a small idle action:
```

| # | Imagen | Acción del personaje (va después de la frase de arriba) |
|---|---|---|
| 04 | `04_personaje_tony.png` | `he breathes, pushes his glasses up with one finger, cracks his knuckles and gives a small confident nod.` |
| 05 | `05_personaje_miranda.png` | `she breathes softly, her long wavy hair sways, she gives a small sleepy yawn and tucks a lock of hair behind her ear.` |
| 06 | `06_personaje_cesar.png` | `he breathes, glances left and right with a sly look and pushes his glasses up, his fingers tapping quickly in the air as if typing.` |
| 07 | `07_personaje_alan.png` | `he breathes, shrugs his shoulders with a cheeky little smile and puts his hands in his hoodie pocket and back out.` |
| 08 | `08_personaje_castillo.png` | `he breathes, straightens his shirt collar with both hands and keeps a calm, serious look.` |
| 09 | `09_personaje_alessandro.png` | `he breathes, chuckles so his shoulders shake, and glances at the gold watch on his wrist.` |
| 10 | `10_personaje_gabo.png` | `he breathes and bounces lightly on his toes, shaking out his legs, ready to sprint.` |
| 11 | `11_personaje_carlos.png` | `he takes a big proud breath, puffs out his chest, pats it once with his hand and smiles.` |

Prompt completo de ejemplo (Tony): frase de selección + acción de Tony + BLOQUE COMÚN.

## Prioridad B (si queda tiempo)

### 12 · Fondo del menú de modos (pasillo) — `imagenes/12_fondo_modos.png`
```
Animate this empty dark school hallway at night. The ceiling lights flicker softly now and then, dust particles float in the light, and a locker door moves very slightly. No people.
```

### 13 · Fondo de selección (salón) — `imagenes/13_fondo_seleccion.png`
```
Animate this dark classroom at night. Moonlight shimmers softly through the windows, the computer screens flicker, the clock hand ticks, and dust floats in the light spot on the desk. No people.
```

### 14 · Fondo de la tienda — `imagenes/14_fondo_tienda.png`
```
Animate this dark school hallway at night. The lights flicker softly, dust particles float in the air, and the glow on the lockers shimmers. No people.
```

### 15 · Victoria — `imagenes/15_victoria.png`
```
Animate this victory scene at sunrise. The four students on the left cheer, jumping slightly and waving their raised arms. The yellow school bus idles with a slight vibration and small puffs of exhaust. The clouds drift slowly and the sunrise glow gently brightens.
```

### 16 · Derrota — `imagenes/16_derrota.png`
```
Animate this defeat scene in a dark hallway. The scared students tremble and look around. The zombies sway and reach toward them in place with glowing red eyes, and the janitor zombie in front sways with his mop. The red vignette around the edges pulses slowly and a ceiling light flickers.
```

---
**Reparto sugerido:** una persona hace 01-03, otra 04-07, otra 08-11 y quien termine primero sigue con la prioridad B.
