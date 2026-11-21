# Prompts para las imágenes de la pantalla de controles (pausa)

Hay 2 imágenes de 720×300 px (relación 12:5). Hazlas con tu generador (Nano Banana Pro; prompts en inglés) y guárdalas con estos nombres en
`gdevelop/FDI-Z/assets/interfaz/`:

- `ctl_teclado_ia.png`  (teclado + ratón)
- `ctl_mando_ia.png`    (control de Xbox)

Luego corre `python3 gdevelop/scripts/fase49_arte.py` (las escala a 720×300 y reemplazan a las actuales). Si no existen, no cambia nada.
Pídelas con fondo oscuro azulado (#2e3347) y borde redondeado, para que combinen con el panel de pausa.

## Controles vigentes en el juego (verificados en el proyecto, 21 nov 2026)
| Acción | Teclado y ratón | Control de Xbox |
|---|---|---|
| Moverse | W A S D | Stick izquierdo |
| Correr (gasta estamina) | Shift (izq. o der.) | LB o clic del stick izquierdo (L3) |
| Pegar | Clic izquierdo del ratón | X |
| Lanzar objeto | Clic derecho del ratón o R | B |
| Usar / revivir / curar (mantener) | F | A |
| Habilidad | Q | Y |
| Especial | E | RB |
| Apuntar | Cursor del ratón | Stick derecho |
| Pausa | Esc o P | Start |

## Prompt 1 · Teclado y ratón (`ctl_teclado_ia.png`)
Pixel art game UI illustration, wide banner, aspect ratio 2.2:1 (about 980x440), dark navy-slate rounded panel background (#2e3347) with a thin
light-blue border, crisp chunky pixel-art style, flat colors, clean readable lettering, everything perfectly aligned.
LEFT HALF = top-down keyboard, glossy keycaps with bold letters, keys in this exact layout:
- Top row, left to right: "Esc" (light gray), then a gap, then "Q" (purple), "W" (blue), "E" (purple), "R" (red), then a gap, then "P" (light gray).
- Second row, slightly indented: "A" (blue), "S" (blue), "D" (blue), "F" (green).
- Bottom row: a wide "Shift" key (yellow) under the left side.
Small Spanish captions in uppercase, each with ONE thin straight leader line touching ONLY its own key(s), no crossing lines:
"HABILIDAD" -> Q only; "ESPECIAL" -> E only; "LANZAR" -> R only; "USAR (MANTENER)" -> F only; "CORRER" -> Shift only;
"PAUSA" -> one line that splits to reach both Esc and P; "MOVER" -> ONE bracket that spans all four keys W, A, S and D together (the bracket must
visibly cover W in the top row AND A, S, D in the second row).
RIGHT HALF = a computer mouse seen from above: left button orange, right button red, thin scroll wheel between them, big label "MOUSE" underneath,
a small arrow cursor icon to the right of the mouse. Captions: "PEGAR" -> left button only; "LANZAR" -> right button only; "APUNTAR" -> the cursor icon.
No characters, no people, no extra text, no watermark, no logos.

## Prompt 2 · Control de Xbox (`ctl_mando_ia.png`)
Pixel art game UI illustration, wide banner, aspect ratio 2.2:1 (about 980x440), dark navy-slate rounded panel background (#2e3347) with a thin
light-blue border, crisp chunky pixel-art style, flat colors, clean readable lettering, everything perfectly aligned. The gamepad must fill most of
the panel (large, not tiny, little empty space above and below). Top-down view of an Xbox-style controller with this exact anatomy:
- Left stick (upper left) with the letter "L". Right stick (lower middle-right) with the letter "R". D-pad (lower left of the right stick).
- Face-button diamond on the upper right, real Xbox colors and positions: "Y" yellow on TOP, "A" green on BOTTOM, "X" blue on the LEFT, "B" red on the RIGHT.
- Two small center buttons: the LEFT one is "View" (two overlapping squares icon) and has NO caption; the RIGHT one is "Start/Menu" (three horizontal lines icon).
- Bumpers "LB" (top left) and "RB" (top right), Xbox logo in the center top.
Spanish captions, each with ONE thin straight leader line touching ONLY the button it names, no crossing lines, captions in clean columns:
LEFT column: "MOVER" -> left stick "L"; "CORRER" -> LB; "CORRER (CLIC AL STICK)" -> left stick "L" as well.
TOP center: "PAUSA" -> the right small center button (Start/Menu, three lines) ONLY.
RIGHT column, top to bottom, in this order: "ESPECIAL" -> RB; "HABILIDAD" -> Y (yellow); "PEGAR" -> X (blue); "LANZAR" -> B (red); "USAR (MANTENER)" -> A (green);
"APUNTAR" -> right stick "R".
The line of "PEGAR" must end on the blue X, the line of "LANZAR" on the red B and the line of "USAR (MANTENER)" on the green A; never swap them.
No characters, no people, no extra text, no watermark, no logos.

## Si la imagen sale con un rótulo mal puesto: prompt de corrección (adjunta la imagen)
Edit the attached image, keep the style, colors and layout exactly the same, and only fix these captions/leader lines:
(Xbox) "PEGAR" must point to the blue X button, "LANZAR" to the red B button, "USAR (MANTENER)" to the green A button, and "PAUSA" to the right small
center button with three horizontal lines (Start/Menu), not the left one. (Keyboard) the "MOVER" bracket must cover all four keys W, A, S and D.
Do not change anything else.
