# FDI-Z: historial de prompts de personajes

Todos los prompts que se han usado para generar personajes (Nano Banana / WaveSpeed), en el orden en que se hicieron. Primero van los del estilo oficial; al final, los primeros prompts de exploración de estilos.

## Estilo oficial

- **Referencia de estilo:** la chica chibi en pixel art de cabello castaño largo, sudadera negra abierta, playera gris y jeans acampanados, sobre fondo blanco. Guárdenla como `estilo/referencia.png`.
- **Reglas:** cuerpo completo, de frente, proporciones chibi, sombreado por bloques, contornos oscuros, fondo blanco liso, sombra gris pequeña bajo los pies, formato vertical 2:3.
- **Cómo se usa:** se adjunta la referencia de estilo y, si hay, una foto de la persona. Si no hay foto, se describe a la persona en el texto.

### Asignación de personajes

| # | Personaje del prompt | Personaje del juego |
| --- | --- | --- |
| 1 | Chico de lentes, suéter de cuello de tortuga | Por asignar |
| 2 | Chica de lentes, blusa negra corta | Por asignar |
| 3 | Chico fitness con playera K.O. | Tony (según la tabla de personajes) |
| 4 | El mismo, sin camisa y musculoso | Tony, Modo gym |
| 5 | Chico de cabello rizado con reloj | Alessandro (según la tabla de personajes) |
| 6 | Chico de sudadera negra | Por asignar |
| 7 | Chico de polo azul y lentes aviador | Por asignar |
| 8 | Chico de cabello rizado con cadena y camisa blanca | Por confirmar (¿Tony con foto?) |
| 9 | Chico de camisa blanca formal y pantalón azul marino | Por asignar |
| 10 | Chico de sudadera verde (ganador de hackathon) | Por asignar |
| 11 | Profe de polo gris | Por asignar (profe) |
| 12 | Profe de polo blanco y pantalón caqui | Por asignar (profe) |
| 13 | Profe de barba con uniforme verde de gasolinero | Por asignar (profe) |

---

## 1. Chico de lentes y cuello de tortuga

**Imágenes adjuntas:** 1) referencia de estilo, 2) foto de él.

```
Usa la imagen 1 SOLO como referencia de estilo y la imagen 2 SOLO como referencia de la persona.

Crea un personaje de cuerpo completo en el mismo estilo de pixel art de la imagen 1: mismo tamaño de píxel, proporciones chibi (cabeza grande, cuerpo pequeño), sombreado suave por bloques, contornos oscuros, pose de pie frontal y relajada con los brazos a los lados, sombra gris pequeña bajo los pies y fondo blanco liso. No copies el cabello, la cara ni la ropa de la chica de la imagen 1.

El personaje es el chico de la imagen 2: cabello negro corto, abundante y un poco despeinado con ondas; lentes de armazón delgado oscuro y redondo; tono de piel claro-medio; sonrisa ligera de lado, segura. Que se reconozca que es él.

Ropa: suéter negro de cuello de tortuga y manga larga, jeans de mezclilla azul de corte recto, y tenis Nike rojos con el logo blanco a un costado.

No incluyas la hoja de examen, la pluma, el cuaderno ni el fondo del salón de la imagen 2. Un solo personaje, centrado, sin texto, formato vertical 2:3 como la imagen 1.
```

**Correcciones útiles:**
- Para que se parezca más: "haz más parecida la cara a la imagen 2: lentes redondos, cabello negro ondulado y sonrisa de lado".
- Si salen detalles de más: "píxeles grandes y nítidos, sin degradados, igual de simple que la imagen 1".

**Ajuste de estilo (acoplar al sprite de Alessandro):** el resultado salió con píxel más fino, ojos grandes y brillantes tipo anime y sombreado más suave. Se corrige con un prompt de edición.

**Imágenes adjuntas:** 1) sprite de Alessandro (estilo), 2) resultado de este prompt (personaje).

```
Use image 1 ONLY as the style reference and image 2 ONLY as the character to redraw.

Redraw the character from image 2 in the exact pixel art style of image 1: same big, chunky pixel size, same low level of detail, same limited palette with flat block shading (about 3 shades per color, no smooth gradients), same dark brown outlines, same chibi proportions and same body size and height as image 1. Same simple face as image 1: small dark eyes without big shiny highlights, a tiny mouth and a slight blush. Hair drawn with the same blocky, rough pixel clusters as image 1.

Keep everything that identifies the character from image 2: short black hair, slightly messy with a bit of wave, swept to the side; thin dark round glasses; slight side smile; black long-sleeve turtleneck sweater; straight blue jeans; red Nike sneakers with a white swoosh. Do not copy the curly hair, silver glasses, watch or clothes of image 1.

Front-facing standing pose, arms relaxed at his sides. Plain white background, flat gray shadow under the feet. Single character, centered, no text, vertical 2:3 like image 1.
```


**Resultado:** el prompt de edición devolvió casi la misma imagen (el modelo conserva la imagen 2 en vez de redibujarla). No sirvió.

**Versión desde cero (recomendada):** solo se adjunta el sprite de Alessandro, sin la imagen vieja.

```
Use the attached image ONLY as a style reference.

Create a NEW full-body character in the exact same pixel art style as the reference: same big, chunky pixel size, same low level of detail, same limited palette with flat block shading, same dark brown outlines, same chibi proportions and same body size. Same simple face as the reference: small dark eyes, a tiny mouth and a slight blush. Hair drawn with the same blocky, rough pixel clusters. Plain white background and a flat gray shadow under the feet. Do not copy the curly hair, silver glasses, watch or clothes of the reference.

The character is a university guy around 20, slim build, fair light skin. Short black hair neatly combed in a formal side-part style: a clean visible part on one side, hair combed smoothly to the side with a little volume on top, tidy and polished, no messy strands. Thin dark round glasses. Slight confident side smile.

Pose: front-facing, standing, arms relaxed at his sides, like the reference.

Outfit: black long-sleeve turtleneck sweater, straight blue jeans, and red Nike sneakers with a white swoosh.

Single character, centered, no text, vertical 2:3 like the reference.
```

**Resultado:** el estilo ya coincide con Alessandro. Se cambió el peinado a formal (arriba ya está actualizado) y, para no regenerar, se editó solo el cabello adjuntando el resultado:

```
Use the attached image as the reference. Keep everything exactly the same: same pixel art style, same pixel size, face, glasses, smile, clothes, sneakers, pose, background and shadow.

Change only the hair: short black hair neatly combed in a formal side-part style, with a clean visible part on one side, hair combed smoothly to the side with a little volume on top, tidy and polished, no messy strands. Draw it with the same chunky pixels and flat block shading as the rest of the image.

Also make his skin tone lighter: fair, light skin, keeping the same flat block shading and the slight blush.
```
---

## 2. Chica de lentes, blusa negra corta

**Imágenes adjuntas:** la referencia de estilo (y opcionalmente su foto).

```
Usa la imagen adjunta SOLO como referencia de estilo.

Crea un personaje de cuerpo completo en el mismo estilo de pixel art de la imagen: mismo tamaño de píxel, proporciones chibi (cabeza grande, cuerpo pequeño), sombreado suave por bloques, contornos oscuros, pose de pie frontal y relajada con los brazos a los lados, sombra gris pequeña bajo los pies y fondo blanco liso. No copies el cabello, la cara ni la ropa de la chica de la imagen de referencia.

El personaje es una chica universitaria de unos 20 años, de estatura baja (1.60 m), un poco más bajita y delgada que la referencia. Piel muy clara, cabello castaño claro, lentes, expresión amable y tranquila.

Ropa: blusa negra corta que llega un poco arriba del ombligo, pantalón de mezclilla azul acampanado, y tenis Adidas negros de suela plana con las tres franjas blancas.

Un solo personaje, centrado, sin texto, formato vertical 2:3 como la imagen de referencia.
```

**Variantes:**
- Con su foto como segunda imagen, la primera línea cambia a: "Usa la imagen 1 SOLO como referencia de estilo y la imagen 2 SOLO como referencia de la persona; que se reconozca que es ella."
- Para la escala: "ponla al lado del chico de la imagen de referencia; ella es una cabeza más bajita".

---

## 3. Chico fitness con playera K.O. (Tony)

**Imágenes adjuntas:** 1) referencia de estilo, 2) logo K.O. (opcional: 3) foto de él).

```
Use image 1 ONLY as a style reference and image 2 ONLY as the logo to put on the shirt.

Create a full-body character in the exact same pixel art style as image 1: same pixel size, chibi proportions (big head, small body), soft block shading, dark outlines, relaxed front-facing standing pose with arms at the sides, small gray shadow under the feet, and a plain white background. Do not copy the hair, face or clothes of the girl in image 1.

The character is a university guy around 20 years old, 1.70 m tall (a bit taller than the reference), with a fit, athletic build: broad shoulders and toned arms. Short curly dark hair, glasses, and a small earring on his right ear (on the viewer's left, since he faces the camera). Confident, friendly expression.

Outfit: a fitted black t-shirt with the K.O. logo from image 2 centered on the chest, simplified to pixel art but keeping its white letters and blue lightning-bolt outline. Blue denim jeans, and white Nike Blazer sneakers with a blue swoosh.

Single character, centered, no extra text, vertical 2:3 format like image 1.
```

**Variantes:**
- Con su foto como imagen 3: "Use image 3 ONLY as the reference for his face and hair, so he is recognizable."
- Si el logo sale deforme: "make the K.O. logo bigger and simpler on the shirt, only the white letters with a blue outline".

---

## 4. Tony sin camisa (Modo gym)

**Imagen adjunta:** el resultado del prompt 3.

```
Use the attached image as the reference for both the style and the character.

Recreate this exact same character in the exact same pixel art style: same pixel size, same chibi proportions, same soft block shading, dark outlines, front-facing standing pose with arms at the sides, small gray shadow under the feet, and a plain white background.

Keep the same face, short curly dark hair, glasses, the small earring on his right ear (viewer's left), the same blue jeans, and the same white sneakers with the blue swoosh.

Change only this: he is shirtless, with a big, muscular build. His shoulders, chest and arms are noticeably wider and bulkier, with visible pecs and defined abs drawn with simple pixel shading. His body is a bit larger overall than the reference, while the head stays the same size. Confident expression with a slight proud smile.

Single character, centered, no text, vertical 2:3 format like the reference.
```

**Variantes:**
- Presumiendo músculo: "flexing both biceps in a classic bodybuilder pose".
- Aura del poder: "with a faint yellow glowing aura around him".

---

## 5. Chico de cabello rizado con reloj (Alessandro)

### Versión 1: con foto y reloj de bolsillo (reemplazada)

**Imágenes adjuntas:** 1) referencia de estilo, 2) foto de él.

```
Use image 1 ONLY as a style reference and image 2 ONLY as the reference for the person.

Create a full-body character in the exact same pixel art style as image 1: same pixel size, chibi proportions (big head, small body), soft block shading, dark outlines, plain white background and a small gray shadow under the feet. Do not copy the face, hair or clothes of the character in image 1.

The character is the guy from image 2, recognizable: short, curly, messy black hair; thin round wire-frame glasses; light-medium skin; calm, slight smile; slim build.

Pose: relaxed front-facing standing pose with both arms down at his sides, like image 1. Ignore the extended arm pose from the photo.

Outfit, same as the photo: a plain black t-shirt, loose gray cargo pants with side pockets, and light gray running sneakers.

In his right hand (on the viewer's left, since he faces the camera) he holds a golden pocket watch with a small chain, clearly visible.

Single character, centered, no text, no background from the photo, vertical 2:3 format like image 1.
```

### Versión 2 (final): sin foto, reloj de pulsera

**Imagen adjunta:** solo la referencia de estilo.

```
Use the attached image ONLY as a style reference.

Create a full-body character in the exact same pixel art style as the reference: same pixel size, chibi proportions (big head, small body), soft block shading, dark outlines, plain white background and a small gray shadow under the feet. Do not copy the face, hair or clothes of the character in the reference.

The character is a Mexican university guy around 20 years old, slim build, light-medium skin. Short, curly, messy black hair with volume on top. Thin round wire-frame glasses in a light silver color. Calm expression with a slight smile.

Pose: relaxed front-facing standing pose with both arms down at his sides, like the reference.

Outfit: a plain black crew-neck t-shirt, loose gray cargo pants with side pockets, and light gray running sneakers.

He wears a large, clearly visible wristwatch on his right wrist (on the viewer's left, since he faces the camera), with a gold case and a black strap.

Single character, centered, no text, vertical 2:3 format like the reference.
```

**Corrección útil:** si el reloj sale chiquito, "make the wristwatch slightly oversized so it reads clearly in pixel art".

---

## 6. Chico de sudadera negra

**Imagen adjunta:** solo la referencia de estilo.

```
Use the attached image ONLY as a style reference.

Create a full-body character in the exact same pixel art style as the reference: same pixel size, chibi proportions (big head, small body), soft block shading, dark outlines, plain white background and a small gray shadow under the feet. Do not copy the face, hair or clothes of the character in the reference.

The character is a Mexican university guy around 20 years old, medium height with a stocky, solid build and a slightly round, full face. Medium tan-brown skin. Short dark brown hair, a bit longer and fuller on top, swept slightly to the side, with short sides. Thick dark eyebrows and a calm, serious expression with a neutral mouth.

Pose: relaxed front-facing standing pose with both arms down at his sides, like the reference.

Outfit: a plain black hoodie with the hood down, a small white logo on the left side of the chest, and a front kangaroo pocket. Medium-blue straight-leg jeans and black sneakers with white soles.

Single character, centered, no text, vertical 2:3 format like the reference.
```

**Nota:** en la foto no se veían los tenis; se pusieron negros con suela blanca.

---

## 7. Chico de polo azul y lentes aviador

**Imagen adjunta:** solo la referencia de estilo.

```
Use the attached image ONLY as a style reference.

Create a full-body character in the exact same pixel art style as the reference: same pixel size, chibi proportions (big head, small body), soft block shading, dark outlines, plain white background and a small gray shadow under the feet. Do not copy the face, hair or clothes of the character in the reference.

The character is a university guy around 20 years old, slim build, light-medium skin. Straight black hair, medium length and a bit messy, with thick bangs falling over the forehead and covering the ears. Big oversized aviator-style glasses with clear lenses and a thin light gold metal frame. Playful expression with a slight smile.

Pose: relaxed front-facing standing pose with both arms down at his sides, like the reference.

Outfit: a royal blue polo shirt with a collar, a dark bracelet on his right wrist (viewer's left), dark blue jeans and white sneakers.

Single character, centered, no text, vertical 2:3 format like the reference.
```

**Variante (para Castillo o Tony):** "holding a black bowl in one hand and chopsticks in the other, about to eat".

**Nota:** en la foto no se veían el pantalón ni los tenis; se pusieron jeans oscuros y tenis blancos.


---

## 8. Chico de cabello rizado con cadena y camisa blanca

### Versión 1 (descartada)

Salió en pixel art fino tipo HD, con cabello castaño y bigote; no coincidía con el estilo ni con él.

### Versión 2: con el sprite de Alessandro como referencia de estilo

**Imágenes adjuntas:** 1) sprite de Alessandro (resultado del prompt 5), 2) foto de él.

```
Use image 1 ONLY as a style reference and image 2 ONLY as the reference for the person's face and hair.

Copy the pixel art style of image 1 exactly: same big, chunky pixel size, same low level of detail, same limited palette with flat block shading, same dark outlines, same chibi proportions with a big head and short body, same simple face (small dark eyes, tiny mouth, slight blush). Plain white background and a flat gray shadow under the feet. Do not copy the hair, glasses or clothes of the character in image 1.

The character is the guy from image 2: university guy around 20, athletic build with broad shoulders, light-medium skin. BLACK curly hair (not brown): curls on top falling over the forehead, with short faded sides that look shaved. Thick BLACK rectangular glasses (not round, not silver). Clean-shaven: no mustache, no beard. A small silver hoop earring on one ear. Calm, serious expression.

Pose: front-facing, standing, arms relaxed at his sides, like image 1.

Outfit: plain white crew-neck t-shirt, a silver chain necklace over the shirt, blue denim jeans, and white Nike Blazer sneakers with a blue swoosh.

Single character, centered, no text, vertical 2:3 like image 1.
```

**Correcciones útiles:**
- Si sale con barba o bigote: "remove all facial hair, completely clean-shaven face".
- Si el cabello sale café: "make the hair pure black, same color as the hair in image 1".
- Si se parece demasiado a Alessandro: "make the sides of the head clearly shaved (fade) and the glasses thick, black and rectangular".



### Modo gym (sin camisa y musculoso)

**Imagen adjunta:** el resultado final del prompt 8.

```
Use the attached image as the reference for both the style and the character.

Recreate this exact same character in the exact same pixel art style: same big, chunky pixel size, same flat block shading, same dark outlines, same chibi head size, front-facing standing pose with arms at the sides, plain white background and gray shadow.

Keep the same face, black curly hair with faded sides, thick black rectangular glasses, silver earring, silver chain necklace, blue jeans and white sneakers with the blue swoosh.

Change only this: he is shirtless, with a big, muscular build. His shoulders, chest and arms are much wider and bulkier, with visible pecs and defined abs drawn with simple pixel shading. His body is noticeably larger and taller overall than the reference, while the head stays the same size. The silver chain rests on his bare chest. Confident expression with a slight proud smile.

Single character, centered, no text, vertical 2:3 like the reference.
```

**Variantes:**
- Presumiendo músculo: "flexing both biceps in a classic bodybuilder pose".
- Si no sale lo bastante grande: "make him even bigger and more muscular, about 1.4 times as wide as the reference".

---

## 9. Chico de camisa blanca formal y pantalón azul marino

**Imágenes adjuntas:** 1) sprite de Alessandro (estilo), 2) foto de él.

```
Use image 1 ONLY as a style reference and image 2 ONLY as the reference for the person's face and hair.

Copy the pixel art style of image 1 exactly: same big, chunky pixel size, same low level of detail, same limited palette with flat block shading, same dark brown outlines, same chibi proportions and same body size. Same simple face as image 1: small dark eyes, a tiny mouth and a slight blush. Plain white background and a flat gray shadow under the feet. Do not copy the hair, glasses, watch or clothes of the character in image 1.

The character is the guy from image 2, recognizable: university guy around 20, slim build, light-medium skin. Short black hair, combed up and to the side with volume on top, tidy. Dark brown rectangular glasses. Serious, focused expression, slightly frowning.

Pose: front-facing, standing, arms relaxed at his sides, like image 1. Ignore the pose, the phone and the water bottle from the photo.

Outfit: a white button-up dress shirt with a collar, sleeves rolled up to the elbows, tucked in; a black leather belt with a silver buckle; dark navy blue dress pants; black dress shoes. A black sports watch on his right wrist (viewer's left) and a brown bead bracelet on his left wrist (viewer's right).

Single character, centered, no text, no background from the photo, vertical 2:3 like image 1.
```

**Correcciones útiles:**
- Para que se parezca más: "make the face closer to image 2: dark brown rectangular glasses, black hair combed up and to the side, serious look".
- Si el pixel sale fino: "use the same big chunky pixels as image 1, much less detail".

**Variante (pose de la foto):** cambiar la pose por "holding a smartphone to his right ear with his right hand, looking serious and busy, like he is on an important call".

**Nota:** en la foto no se ven los zapatos; se pusieron zapatos negros de vestir.


---

## 10. Chico de sudadera verde (ganador de hackathon)

**Imágenes adjuntas:** 1) sprite de Alessandro (estilo), 2) foto de él.

```
Use image 1 ONLY as a style reference and image 2 ONLY as the reference for the person's face and hair.

Copy the pixel art style of image 1 exactly: same big, chunky pixel size, same low level of detail, same limited palette with flat block shading, same dark brown outlines, same chibi proportions. Same simple face as image 1: small dark eyes, a tiny mouth and a slight blush. Plain white background and a flat gray shadow under the feet. Do not copy the hair, glasses, watch or clothes of the character in image 1.

The character is the guy from image 2, recognizable: university guy around 20, big and robust: clearly taller and wider than the character in image 1, with a large, solid, sturdy build, broad shoulders, a wide chest and thick arms. Not fat and no pronounced belly: a straight, solid torso, like a big strong guy. Slightly fuller face. His body is noticeably bigger overall while the chibi style stays the same. Light-medium skin. Black wavy hair with volume on top, a bit messy. Thin light metal-frame glasses. Friendly, happy smile.

Pose: front-facing, standing, arms relaxed at his sides, like image 1. Ignore the pose, the big sign and the background from the photo.

Outfit: a dark green hoodie with the hood down, with the hem of a white t-shirt showing slightly underneath; dark charcoal gray jeans; black sneakers with white soles.

Single character, centered, no text, no background from the photo, vertical 2:3 like image 1.
```

**Correcciones útiles:**
- Para que se parezca más: "make the face closer to image 2: wavy black hair with volume, thin light glasses, big friendly smile".
- Si sale muy delgado: "make him bigger and more robust: wider shoulders and chest, thicker arms and legs, about 1.4 times as wide as the character in image 1, without a belly".
- Si sale con panza: "flatten the belly, straight solid torso, big and strong but not fat".

**Variante (ganador):** cambiar la pose por "holding a giant blue winner check sign with both hands in front of his chest, proud smile". Sin logos ni texto en el cheque.

**Nota:** en la foto no se ven los tenis; se pusieron negros con suela blanca.



---

## 11. Profe de polo gris

**Imágenes adjuntas:** 1) sprite de Alessandro (estilo), 2) foto de él.

```
Use image 1 ONLY as a style reference and image 2 ONLY as the reference for the person's face and hair.

Copy the pixel art style of image 1 exactly: same big, chunky pixel size, same low level of detail, same limited palette with flat block shading, same dark brown outlines, same chibi proportions. Same simple face style as image 1: small dark eyes and a tiny mouth. Plain white background and a flat gray shadow under the feet. Do not copy the hair, glasses, watch or clothes of the character in image 1.

The character is the man from image 2, recognizable: a university teacher in his 40s, an adult, a bit taller than the character in image 1, slim build, medium tan skin. Black wavy hair, medium-short with volume on top, a little messy. A dark mustache and goatee with a few gray hairs. No glasses. Calm, observant expression, slightly serious.

Pose: front-facing, standing, arms relaxed at his sides, like image 1. Ignore the sitting pose, the desk and the classroom from the photo.

Outfit: a dark gray polo shirt with a collar and dark trim on the collar and sleeves; dark blue jeans; dark gray sneakers with black soles.

Single character, centered, no text, no background from the photo, vertical 2:3 like image 1.
```

**Correcciones útiles:**
- Para que se parezca más: "make the face closer to image 2: wavy black hair with volume, mustache and goatee, calm serious look".
- Si sale muy joven: "make him look like an adult in his 40s, a bit older than the students".

**Variante (dando clase):** cambiar la pose por "holding a whiteboard marker in one hand, pointing slightly to the side as if explaining a lesson".


---

## 12. Profe de polo blanco y pantalón caqui

**Imágenes adjuntas:** 1) sprite de Alessandro (estilo), 2) foto de él.

```
Use image 1 ONLY as a style reference and image 2 ONLY as the reference for the person's face and hair.

Copy the pixel art style of image 1 exactly: same big, chunky pixel size, same low level of detail, same limited palette with flat block shading, same dark brown outlines, same chibi proportions. Same simple face style as image 1: small dark eyes and a tiny mouth. Plain white background and a flat gray shadow under the feet. Do not copy the hair, glasses, watch or clothes of the character in image 1.

The character is the man from image 2, recognizable: a university teacher in his 50s, an adult, a bit taller than the character in image 1, with a sturdy build and a rounded belly. Medium tan skin. Balding on top, with short dark hair with some gray only on the sides and back of the head. Thin wire-frame glasses. A thick dark mustache with some gray. Friendly, talkative expression with a slight smile.

Pose: front-facing, standing, arms relaxed at his sides, like image 1. Ignore the background from the photo.

Outfit: a white short-sleeve polo shirt with a collar and a small navy blue round emblem on the left side of the chest (no text); a black leather belt with a silver buckle; loose beige khaki pleated dress pants; black work shoes. A black digital watch on his left wrist (viewer's right).

Single character, centered, no text, no background from the photo, vertical 2:3 like image 1.
```

**Correcciones útiles:**
- Para que se parezca más: "make the face closer to image 2: bald on top with short gray-dark hair on the sides, thin glasses, thick mustache".
- Si sale con cabello arriba: "clearly bald on top of the head, hair only on the sides and back".


---

## 13. Profe de barba con uniforme verde de gasolinero

**Imágenes adjuntas:** 1) sprite de Alessandro (estilo), 2) foto de su cara (polo gris), 3) foto del outfit (polo verde y gorra).

```
Use image 1 ONLY as a style reference, image 2 ONLY as the reference for the person's face and hair, and image 3 ONLY as the reference for the outfit.

Copy the pixel art style of image 1 exactly: same big, chunky pixel size, same low level of detail, same limited palette with flat block shading, same dark brown outlines, same chibi proportions. Same simple face style as image 1: small eyes and a tiny mouth. Plain white background and a flat gray shadow under the feet. Do not copy the hair, glasses, watch or clothes of the character in image 1.

The character is the man from image 2, recognizable: a young adult teacher around 30, a bit taller than the character in image 1, sturdy build. Fair, light skin. Light eyes (light hazel-green), clearly lighter than the dark eyes of image 1. Dark, slightly messy hair, short and a bit spiky. A full, short dark beard with mustache. Big, cheerful smile. A thin black cord necklace with a small white pendant. No glasses.

Outfit, like image 3: a bright green short-sleeve work polo shirt with a collar, with a small white emblem on the chest and a small colorful patch on one sleeve (no readable text, no logos); a black baseball cap worn forward with a green brim; dark work pants; black work boots. A black digital sports watch on one wrist.

Pose: front-facing, standing, arms relaxed at his sides, like image 1. Ignore the poses, the car, the office and the backgrounds from the photos.

Single character, centered, no text, vertical 2:3 like image 1.
```

**Correcciones útiles:**
- Para que se parezca más: "make the face closer to image 2: full short dark beard, big smile, messy dark hair under the cap".
- Si los ojos salen oscuros: "make his eyes clearly light hazel-green, not dark".
- Si la gorra tapa la cara: "push the cap slightly up so the eyes and face are clearly visible".

**Nota:** los logos del uniforme se dejaron como emblemas sin texto (en pixel art las letras salen deformes). En las fotos no se ven el pantalón ni el calzado; se pusieron pantalón oscuro de trabajo y botas negras.


**Corrección sobre el resultado** (adjuntar solo la imagen generada):

```
Use the attached image as the reference. Keep everything exactly the same: same pixel art style, same pixel size, cap, hair, beard, smile, green polo, watch, pants, boots, pose, background and shadow.

Change only two things:
- Skin: make it fair and light, clearly lighter than now, keeping the same flat block shading.
- Eyes: make them light hazel-green instead of dark, still small and simple.
```
---

## Zombies

Todos los zombies salen de un mismo alumno base. Primero se genera el alumno normal (el "curado") y después cada zombie se hace editando esa imagen, para que todos tengan el mismo cuerpo y tamaño.

### Z0. Alumno normal (curado), base de todos

**Imagen adjunta:** sprite de Alessandro (solo estilo).

```
Use the attached image ONLY as a style reference.

Create a NEW full-body character in the exact same pixel art style as the reference: same big, chunky pixel size, same low level of detail, same limited palette with flat block shading, same dark brown outlines, same chibi proportions and same body size. Same simple face as the reference: small dark eyes, a tiny mouth and a slight blush. Plain white background and a flat gray shadow under the feet. Do not copy the curly hair, silver glasses, watch or clothes of the reference.

The character is a generic, ordinary university student around 20, average height and slim build, light-medium skin. Short, plain dark brown hair, neatly cut, simple and generic. Big, thick black square nerd glasses. Neutral, slightly shy expression with a small smile.

Pose: front-facing, standing, arms relaxed at his sides, like the reference.

Outfit: a dark navy blue polo shirt with a collar and two buttons, tucked out; plain medium-blue jeans; plain white sneakers.

He must look like a generic background student, simple and plain, with no logos, accessories or distinctive features besides the glasses.

Single character, centered, no text, vertical 2:3 like the reference.
```

**Correcciones útiles:**
- Si los lentes salen chicos: "make the glasses bigger and thicker, classic nerd glasses".
- Si sale con detalles de más: "simpler, no logos, no accessories, plain generic student".

**Nota:** este sprite es la base para los zombies normal, corredor, gordo, gritón y conserje.


### Z1. Zombie normal

**Imagen adjunta:** el sprite del alumno normal (resultado de Z0).

```
Use the attached image as the reference for both the style and the character.

Turn this exact same student into a zombie. Keep the exact same pixel art style, pixel size, chibi proportions, body size, haircut, nerd glasses, outfit colors, white background and gray shadow.

Changes:
- Skin: pale grayish-green instead of the normal skin tone, with flat block shading.
- Eyes: glowing red eyes behind the glasses, no pupils. Remove the blush and the smile; mouth slightly open with a blank, hungry expression.
- Clothes: the same navy polo, jeans and white sneakers, but torn and ragged: rips on the sleeves and the bottom of the polo, holes on the knees of the jeans, dirty sneakers. Glasses slightly crooked.
- Stains: a few green slime stains on the clothes and skin. No blood, no gore, no wounds.
- Pose: both arms stretched straight forward at shoulder height, classic zombie walk, still front-facing.

Keep it cartoony and kid-friendly. Single character, centered, no text, vertical 2:3.
```

**Correcciones útiles:**
- Si cambia el cuerpo o el peinado: "keep the same body, size and haircut as the reference, only change skin, eyes, clothes damage and arms".
- Si los brazos se ven raros de frente: "arms stretched forward toward the viewer, drawn slightly foreshortened, hands visible in front of the body".


### Z2. Zombie corredor

**Imagen adjunta:** el sprite del zombie normal (resultado de Z1).

```
Use the attached image as the reference for both the style and the character.

Create a faster, skinnier variant of this exact same zombie student. Keep the exact same pixel art style, pixel size, chibi proportions with the same head size, nerd glasses, glowing red eyes, torn navy polo, torn jeans, dirty white sneakers, green slime stains (no blood), white background and gray shadow.

Changes:
- Body: much thinner and lankier, with skinny arms and legs and a narrow torso. The clothes hang loose on him. Same height as the reference.
- Skin: a more yellowish green, sickly and brighter than the reference, with flat block shading.
- Hair: the same dark hair but standing straight up and spiky, messy, as if blown back by speed.
- Pose: running toward the viewer, still front-facing: body leaning forward, one knee raised high, arms swinging wildly, mouth open. A few small speed lines at his sides.

Keep it cartoony and kid-friendly. Single character, centered, no text, vertical 2:3.
```

**Correcciones útiles:**
- Si no se ve flaco: "make him much skinnier, about 60% of the width of the reference, very thin arms and legs".
- Si pierde el estilo: "same chunky pixels and flat shading as the reference".


### Z3. Zombie gritón

**Imagen adjunta:** el sprite del zombie normal (resultado de Z1).

```
Use the attached image as the reference for both the style and the character.

Create a screaming variant of this exact same zombie student. Keep the exact same pixel art style, pixel size, chibi proportions, body size, grayish-green skin, nerd glasses, glowing red eyes, torn navy polo, torn jeans, dirty white sneakers, green slime stains (no blood), white background and gray shadow.

Changes:
- Hair: the same haircut but gray and white, like gray hair, a bit messy and standing up from the scream.
- Mouth: a huge, wide-open mouth screaming, taking up most of the lower half of the face, dark inside with a few simple teeth. Eyebrows angled, eyes wide.
- Pose: still front-facing and standing, with both hands pressed against the sides of his head, elbows out.
- Optional: two or three small curved sound-wave lines coming out of his mouth.

Keep it cartoony and kid-friendly. Single character, centered, no text, vertical 2:3.
```

**Correcciones útiles:**
- Si la boca sale chica: "make the mouth even bigger, a giant open scream, cartoon style".
- Si el pelo sale blanco puro: "gray hair with darker gray shading, not pure white".


### Z4. Zombie gordo

**Imagen adjunta:** el sprite del zombie normal (resultado de Z1).

```
Use the attached image as the reference for both the style and the character.

Create a big, heavy variant of this exact same zombie student. Keep the exact same pixel art style, pixel size, chibi proportions with the same head size, same height, haircut, nerd glasses, glowing red eyes, torn jeans, dirty white sneakers, green slime stains (no blood), white background and gray shadow.

Changes:
- Body: about 1.5 times as wide as the reference, with a big round belly, thick arms and thick legs, and a rounder face with chubby cheeks. Same height, so he looks wide and heavy.
- Polo: the same torn navy polo, but too small for him: stretched tight over the belly, riding up a little so the bottom of the belly shows, buttons straining, small rips at the seams.
- Skin: olive green instead of grayish green, with flat block shading.
- Pose: front-facing, arms stretched forward like the reference, slow and heavy stance with legs a bit apart.

Keep it cartoony and kid-friendly. Single character, centered, no text, vertical 2:3.
```

**Correcciones útiles:**
- Si no sale lo bastante ancho: "make him wider, exactly 1.5 times the width of the reference".
- Si crece también de alto: "same height as the reference, only wider".


### Z5. Zombie conserje (jefe)

**Imagen adjunta:** el sprite del zombie gordo (resultado de Z4).

```
Use the attached image as the reference for the style, the zombie look and the body width.

Create a new zombie boss: the school janitor. Keep the exact same pixel art style, pixel size, chibi proportions with the same head size, glowing red eyes, green slime stains (no blood), white background and gray shadow. He is a different person, an older adult man, not the student: no nerd glasses, no polo, no jeans.

Body: the same width as the reference (big and heavy, with a round belly), but clearly taller, about 1.3 times the height of the reference, so he looks like a big, imposing boss.

Face and hair: an older man with short gray hair and a thick, bushy gray mustache. Dark grayish-green zombie skin with flat block shading. Angry, menacing expression with heavy eyebrows.

Outfit: a beige janitor work uniform (button-up work shirt and matching beige work pants), a bit torn and dirty, with a dark brown belt. A big ring of many keys hanging from the belt on one side. Dark brown work boots.

Weapon: he holds a mop in one hand like a weapon, gripping the handle with the mop head up near his shoulder, ready to swing.

Pose: front-facing, standing firm with legs apart, the other arm stretched forward like a zombie.

Keep it cartoony and kid-friendly. Single character, centered, no text, vertical 2:3.
```

**Correcciones útiles:**
- Si no sale más alto: "make him taller than the reference, about 1.3 times the height, same width".
- Si sale con lentes o ropa del alumno: "remove the glasses, the polo and the jeans; beige janitor uniform only".
- Si el trapeador se pierde: "make the mop bigger and clearly visible, with a gray mop head and a wooden handle".

---

## Exploración de estilos (primeros prompts)

Estos se hicieron antes de elegir el estilo oficial, con la lista de personajes de la versión anterior (Facu Z). Se guardan por si sirven para portadas o tarjetas.

### Estilos visuales distintos (uno por personaje)

**Alessandro: caricatura animada antigua**
```
Ilustración de personaje en estilo caricatura animada de los años 30: líneas negras gruesas y redondeadas, brazos de "manguera" sin codos, ojos grandes y expresivos, textura de película vieja con grano suave. Un estudiante universitario mexicano de unos 20 años con playera amarilla, jeans azules y tenis negros, con una sonrisa enorme de oreja a oreja, contando un chiste con una mano levantada. A su alrededor, tres zombies estudiantes de piel verde están tirados en el piso muertos de risa, agarrándose la panza. Fondo: pasillo de facultad con lockers. Paleta limitada: amarillo, verde zombie, crema y negro. Encuadre de cuerpo completo, personaje centrado, formato 1:1, sin texto.
```

**Tony: rótulo de taquería pintado a mano**
```
Retrato de personaje al estilo de rótulo de taquería mexicana pintado a mano sobre una pared: colores planos y brillantes, contornos firmes, sombras simples con brocha, ligero desgaste de pintura vieja. Un estudiante universitario de unos 20 años con gorro de chef blanco, mandil blanco sobre playera verde azulado, sonriendo y sosteniendo un plato de tacos al pastor humeantes. Detrás de él, un zombie estudiante de piel verde se asoma babeando por los tacos. Marco decorativo con flores y piñas pintadas alrededor. Arriba, letras de rotulista que dicen "TONY". Paleta: rojo, amarillo, verde azulado, blanco y naranja. Formato 1:1.
```

**Alan: collage de stickers tipo fanzine**
```
Ilustración en estilo collage de fanzine punk: recortes de papel con bordes rotos, cinta adhesiva, stickers, texturas de fotocopia y medios tonos. Un estudiante universitario de unos 20 años con playera verde y una mochila naranja enorme que va reventando de cosas: papitas, latas de refresco, galletas, una engrapadora, un balón y un libro (todo genérico, sin marcas). Hace un guiño con cara pícara mientras saca un snack de una máquina expendedora abierta. Un zombie estudiante de piel verde lo mira confundido. Fondo de papel kraft con flechas y estrellas recortadas. Formato 1:1, sin logos ni marcas.
```

**Miranda: carátula de máquina arcade en pixel art**
```
Arte de personaje en pixel art de 16 bits estilo carátula de máquina arcade de los 90: píxeles nítidos y visibles, paleta limitada, brillos de neón y fondo con cuadrícula futurista en perspectiva. Una estudiante universitaria de unos 20 años con cabello castaño largo, audífonos grandes color cian, sudadera morada y jeans oscuros, en pose de acción y con expresión segura. A su alrededor, zombies estudiantes de piel verde se mueven en cámara lenta con líneas de movimiento, mientras ella brilla con un aura azul. Paleta: morado, cian, magenta y negro. Formato 1:1, sin texto.
```

**Kevin: plano técnico (blueprint)**
```
Ilustración en estilo plano técnico de ingeniería (blueprint): fondo azul cianotipo con cuadrícula, dibujo de líneas blancas finas, cotas, flechas de medidas y notas técnicas pequeñas escritas a mano. Un estudiante universitario de unos 20 años, serio y callado, con lentes y playera azul con una franja blanca horizontal en el pecho, de pie junto a su invento: una torreta casera hecha con un resorte, chatarra y una engrapadora, con un despiece de piezas numeradas alrededor. Junto a su cabeza, un globo de diálogo vacío con solo "...". Un zombie estudiante aparece dibujado como "objetivo" con una línea punteada. Formato 1:1.
```

**Gemelo hablador: cómic pop art**
```
Ilustración en estilo cómic pop art de los años 60: puntos de semitono (halftone) visibles, contornos negros gruesos, colores primarios saturados, onomatopeyas grandes. Un estudiante universitario fornido de unos 20 años con playera roja con una franja blanca horizontal en el pecho, empujando con los dos brazos a un grupo de zombies estudiantes de piel verde que salen volando. Tiene la boca muy abierta, hablando a gritos, y le salen muchos globos de diálogo encimados unos sobre otros. Onomatopeya gigante "¡PUM!" en amarillo y rojo. Fondo de rayos de acción. Formato 1:1.
```

### Pixel art de 16 bits (todos iguales)

**Alessandro**
```
Retrato de personaje en pixel art de 16 bits, estilo videojuego clásico de consola de los 90: píxeles nítidos y visibles, sin antialiasing, paleta limitada de 16 colores, sombreado con dithering suave, contorno oscuro de 1 píxel. Un estudiante universitario mexicano de unos 20 años con cabello negro despeinado, playera amarilla, jeans azules y tenis negros, con una sonrisa enorme de oreja a oreja mostrando los dientes, una mano levantada como contando un chiste. A sus pies, dos pequeños zombies estudiantes de piel verde riéndose a carcajadas. Cuerpo completo, vista frontal, personaje centrado, fondo de un solo color liso morado oscuro. Formato 1:1, sin texto.
```

**Tony**
```
Retrato de personaje en pixel art de 16 bits, estilo videojuego clásico de consola de los 90: píxeles nítidos y visibles, sin antialiasing, paleta limitada de 16 colores, sombreado con dithering suave, contorno oscuro de 1 píxel. Un estudiante universitario de unos 20 años, piel morena, con gorro de chef blanco, mandil blanco sobre playera verde azulado, pantalón oscuro, sonriendo y sosteniendo un plato de tacos humeantes con píxeles de vapor. Cuerpo completo, vista frontal, personaje centrado, fondo de un solo color liso morado oscuro. Formato 1:1, sin texto.
```

**Alan**
```
Retrato de personaje en pixel art de 16 bits, estilo videojuego clásico de consola de los 90: píxeles nítidos y visibles, sin antialiasing, paleta limitada de 16 colores, sombreado con dithering suave, contorno oscuro de 1 píxel. Un estudiante universitario de unos 20 años con cabello castaño, playera verde, pantalón gris y una mochila naranja enorme llena hasta reventar de snacks, latas y objetos que se asoman (sin marcas). Hace un guiño pícaro y sostiene una bolsa de papitas. Cuerpo completo, vista frontal ligeramente de tres cuartos para que se vea la mochila, personaje centrado, fondo de un solo color liso morado oscuro. Formato 1:1, sin texto.
```

**Miranda**
```
Retrato de personaje en pixel art de 16 bits, estilo videojuego clásico de consola de los 90: píxeles nítidos y visibles, sin antialiasing, paleta limitada de 16 colores, sombreado con dithering suave, contorno oscuro de 1 píxel. Una estudiante universitaria de unos 20 años con cabello castaño largo, audífonos grandes color cian, sudadera morada, jeans oscuros y tenis, en pose segura con un control de videojuego en la mano y un ligero brillo azul a su alrededor. Cuerpo completo, vista frontal, personaje centrado, fondo de un solo color liso morado oscuro. Formato 1:1, sin texto.
```

**Kevin**
```
Retrato de personaje en pixel art de 16 bits, estilo videojuego clásico de consola de los 90: píxeles nítidos y visibles, sin antialiasing, paleta limitada de 16 colores, sombreado con dithering suave, contorno oscuro de 1 píxel. Un estudiante universitario de unos 20 años, serio y callado, cabello negro corto, lentes negros, playera azul con una franja blanca horizontal en el pecho, pantalón oscuro, sosteniendo una llave inglesa y con un pequeño invento hecho de chatarra y un resorte a su lado. Arriba de su cabeza, un pequeño globo de diálogo con solo "...". Cuerpo completo, vista frontal, personaje centrado, fondo de un solo color liso morado oscuro. Formato 1:1.
```

**Gemelo hablador**
```
Retrato de personaje en pixel art de 16 bits, estilo videojuego clásico de consola de los 90: píxeles nítidos y visibles, sin antialiasing, paleta limitada de 16 colores, sombreado con dithering suave, contorno oscuro de 1 píxel. Un estudiante universitario fornido de unos 20 años, cabello negro corto, playera roja con una franja blanca horizontal en el pecho (la misma ropa que su gemelo pero en rojo), pantalón oscuro, con la boca muy abierta hablando y un brazo flexionado mostrando fuerza. Junto a él, varios globos de diálogo pequeños encimados con garabatos. Cuerpo completo, vista frontal, personaje centrado, fondo de un solo color liso morado oscuro. Formato 1:1.
```

### Varios estilos de pixel art (uno por personaje)

**Alessandro: 8 bits**
```
Personaje en pixel art de 8 bits estilo consola de los años 80: muy pocos píxeles (como un sprite de 32x32 ampliado), píxeles grandes y cuadrados, máximo 4 colores por personaje, sin degradados ni dithering, contorno negro. Proporciones chibi con cabeza grande. Un estudiante universitario con cabello negro despeinado, playera amarilla, jeans azules y una sonrisa enorme, con una mano levantada contando un chiste. A sus pies, un pequeño zombie verde riéndose. Vista frontal, centrado, fondo negro liso. Formato 1:1, sin texto.
```

**Tony: isométrico tipo diorama**
```
Escena en pixel art isométrico, como un diorama pequeño visto en diagonal desde arriba: píxeles nítidos, líneas isométricas limpias 2:1, colores cálidos, iluminación suave. Una pequeña cocina de cafetería escolar sobre una plataforma flotante con estufa, comal y un cartel de "TACOS". En el centro, un estudiante universitario de piel morena con gorro de chef blanco, mandil blanco y playera verde azulado, sirviendo tacos humeantes. En una esquina del diorama, un zombie estudiante verde se asoma con hambre. Fondo de un solo color liso morado oscuro. Formato 1:1.
```

**Alan: consola portátil de 4 tonos verdes**
```
Personaje en pixel art estilo pantalla de consola portátil de los 90: solo 4 tonos de verde (del verde muy oscuro al verde amarillento claro), píxeles nítidos, sin otros colores, textura sutil de pantalla LCD. Un estudiante universitario con una mochila enorme llena hasta reventar de snacks, latas y objetos que se asoman (sin marcas), haciendo un guiño pícaro mientras saca algo de una máquina expendedora abierta. Un zombie estudiante lo mira desde atrás. Cuerpo completo, ligeramente de tres cuartos, centrado. Formato 1:1, sin texto.
```

**Miranda: 16 bits, carátula de arcade**
```
Personaje en pixel art de 16 bits estilo videojuego clásico de consola y arcade de los 90: píxeles nítidos y visibles, sin antialiasing, paleta de 16 colores, sombreado con dithering, contorno oscuro de 1 píxel, brillos de neón. Una estudiante universitaria con cabello castaño largo, audífonos grandes color cian, sudadera morada y jeans oscuros, en pose de acción con un aura azul brillante. A su alrededor, zombies estudiantes verdes se mueven en cámara lenta con líneas de movimiento. Fondo con cuadrícula futurista en perspectiva en morado y magenta. Formato 1:1, sin texto.
```

**Kevin: 1 bit, blanco y negro**
```
Personaje en pixel art de 1 bit: solo blanco y negro puro, sin grises, con sombras hechas únicamente con patrones de dithering, píxeles nítidos, estilo de computadora antigua de pantalla monocromática. Un estudiante universitario serio y callado, con lentes y playera con una franja horizontal en el pecho, sosteniendo una llave inglesa junto a una torreta casera hecha de chatarra y un resorte. Arriba de su cabeza, un pequeño globo de diálogo que solo dice "...". Cuerpo completo, vista frontal, centrado, fondo negro. Formato 1:1.
```

**Gemelo hablador: pixel art moderno en alta definición**
```
Personaje en pixel art moderno de alta definición, estilo videojuego indie actual: muchos píxeles pero todos nítidos, paleta rica, iluminación dramática con luz de borde, partículas y efectos de impacto en pixel. Un estudiante universitario fornido con playera roja con una franja blanca horizontal en el pecho y pantalón oscuro, dando un empujón con los dos brazos que manda a volar a varios zombies estudiantes verdes. Tiene la boca muy abierta, gritando, con globos de diálogo pixelados a su alrededor y una onda de choque en el piso. Fondo de pasillo escolar con lockers azules, oscuro y desenfocado en pixel. Formato 1:1, sin texto.
```
