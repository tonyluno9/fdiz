# FDI-Z: prompts de zombies

Todos los zombies eran alumnos, así que comparten la misma ropa: polo azul oscuro, jeans y tenis blancos. Lo que cambia es el cuerpo y la cara. El conserje va de beige.

**Orden recomendado:** primero el alumno normal (el "curado"). Luego se usa esa imagen como referencia para convertirlo en zombie, y el zombie normal como referencia para los demás. Así todos salen con la misma ropa y el mismo estilo.

Todos van con la referencia de estilo oficial adjunta (`estilo/referencia.png`). Los efectos de estado (dormido con "Zzz", riéndose, congelado) no necesitan imagen aparte: son el mismo sprite quieto con un globo de diálogo encima.

---

## 1. Alumno normal (zombie curado)

**Adjunta:** la referencia de estilo.

```
Use the attached image ONLY as a style reference.

Create a full-body character in the exact same pixel art style as the reference: same pixel size, chibi proportions (big head, small body), soft block shading, dark outlines, relaxed front-facing standing pose with both arms down at his sides, plain white background and a small gray shadow under the feet. Do not copy the face, hair or clothes of the character in the reference.

The character is a generic university student, around 20 years old, average slim build, light-medium skin, short neat dark brown hair, and thick black square "nerd" glasses. Friendly but slightly confused expression, as if he just woke up.

Outfit: a dark navy blue polo shirt with a collar, blue denim jeans, and plain white sneakers.

Single character, centered, no text, vertical 2:3 format like the reference.
```

**Se guarda en:** `zombies/curado/base.png`

---

## 2. Zombie normal

**Adjunta:** 1) la referencia de estilo, 2) el alumno normal (prompt 1).

```
Use image 1 ONLY as a style reference and image 2 as the base character.

Turn the student from image 2 into a zombie, in the exact same pixel art style as image 1: same pixel size, chibi proportions, soft block shading, dark outlines, plain white background and a small gray shadow under the feet. Keep his same clothes and body: dark navy blue polo shirt, blue jeans and white sneakers, and remove the glasses.

Zombie look: pale green-gray skin, dark circles around empty glowing red eyes, messy hair, mouth slightly open, a few rips on the polo and jeans, dirty sneakers, and small green stains on the clothes (no blood, no gore, school-friendly). Classic zombie pose, front-facing, both arms stretched forward, slightly hunched.

Single character, centered, no text, vertical 2:3 format like image 1.
```

**Se guarda en:** `zombies/normal/base.png`

**Variantes para que la horda no se vea repetida** (mismo prompt, cambia solo esto al final):
- "Make him a girl student with a ponytail, same outfit."
- "Give him a backpack hanging from one shoulder."
- "Make him a bit taller with shaggy hair and one sneaker missing."

---

## 3. Corredor

**Adjunta:** 1) la referencia de estilo, 2) el zombie normal (prompt 2).

```
Use image 1 ONLY as a style reference and image 2 as the base zombie.

Create a variant of the zombie from image 2 in the exact same pixel art style: same pixel size, chibi proportions, soft block shading, dark outlines, plain white background and a small gray shadow under the feet. Keep the same outfit: dark navy blue polo shirt, blue jeans and white sneakers.

This is the fast "runner" zombie: very skinny and lanky, bony arms, a lighter and more yellowish green skin, wild spiky hair, wide crazy glowing red eyes and a hungry grin. His polo is more torn and the jeans are ripped at the knees. Hunched forward in a running pose, leaning ahead with arms swinging back, front-facing.

Single character, centered, no text, vertical 2:3 format like image 1.
```

**Se guarda en:** `zombies/corredor/base.png`

---

## 4. Gritón

**Adjunta:** 1) la referencia de estilo, 2) el zombie normal (prompt 2).

```
Use image 1 ONLY as a style reference and image 2 as the base zombie.

Create a variant of the zombie from image 2 in the exact same pixel art style: same pixel size, chibi proportions, soft block shading, dark outlines, plain white background and a small gray shadow under the feet. Keep the same outfit: dark navy blue polo shirt, blue jeans and white sneakers.

This is the "screamer" zombie: normal build, long messy white-gray hair, and a huge wide-open mouth screaming, taking up much of the face. Eyes squeezed and glowing red, hands raised next to the head. Add three small sound lines coming out of the mouth to show the scream. Front-facing.

Single character, centered, no text, vertical 2:3 format like image 1.
```

**Se guarda en:** `zombies/griton/base.png`

---

## 5. Gordo

**Adjunta:** 1) la referencia de estilo, 2) el zombie normal (prompt 2).

```
Use image 1 ONLY as a style reference and image 2 as the base zombie.

Create a variant of the zombie from image 2 in the exact same pixel art style: same pixel size, chibi proportions, soft block shading, dark outlines, plain white background and a small gray shadow under the feet. Keep the same outfit: dark navy blue polo shirt, blue jeans and white sneakers.

This is the big "tank" zombie: much wider and heavier than the normal zombie (about 1.5 times as wide), with a big round belly stretching the polo, which no longer covers his belly completely, thick arms and legs, and a darker olive-green skin. Small glowing red eyes, a tired heavy expression. Slow standing pose, front-facing, arms hanging forward.

Single character, centered, no text, vertical 2:3 format like image 1.
```

**Se guarda en:** `zombies/gordo/base.png`

---

## 6. Conserje zombie (jefe)

**Adjunta:** 1) la referencia de estilo, 2) el zombie gordo (prompt 5).

```
Use image 1 ONLY as a style reference and image 2 as the base for the body size.

Create a boss zombie in the exact same pixel art style as image 1: same pixel size, chibi proportions, soft block shading, dark outlines, plain white background and a small gray shadow under the feet. He is as big and wide as the zombie in image 2, but slightly taller, so he clearly looks like a boss.

This is the school janitor zombie: a beige work uniform (beige button-up work shirt with rolled sleeves and beige work pants), brown work boots, a big ring of keys hanging from his belt, and a mop held in one hand like a weapon. Older look, with a gray mustache and thinning gray hair. Dark green skin, glowing red eyes, angry expression. A few green stains on the uniform (no gore). Front-facing, standing tall.

Single character, centered, no text, vertical 2:3 format like image 1.
```

**Se guarda en:** `zombies/conserje/base.png`

---

## Correcciones útiles

- Si sale demasiado detallado o realista: "big clean pixels, simple flat shading, same simplicity as image 1".
- Si da miedo de más para la presentación: "make it more cartoony and funny, less scary".
- Si cambia la ropa: "keep exactly the same dark navy blue polo shirt, blue jeans and white sneakers as image 2".
