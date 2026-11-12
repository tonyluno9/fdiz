# Lote V0 · Piloto de video: pantalla de título (1 solo video)

Objetivo: probar si Kling 3.0 Standard anima bien nuestro pixel art. Es **un solo video, un solo intento**. Si sale mal, no se regenera: se reporta.
Costo esperado: 3 s × $0.084 ≈ $0.25 USD.

RAIZ = `C:\Users\Angel Perez\Downloads\fdiz`

## 1. Preparar la imagen de entrada (sin generar nada)
- Origen: `RAIZ\gdevelop\FDI-Z\assets\interfaz\bg_titulo.png` (1376×768, RGBA). No lo modifiques.
- Haz una copia en RGB (sin canal alfa, aplanada sobre negro), mismo tamaño, sin reescalar ni suavizar:
  `RAIZ\generado\interfaz\video\titulo\entrada_titulo.png`
- Súbela a WaveSpeed (`POST https://api.wavespeed.ai/api/v3/media/upload/binary`) y usa esa URL.

## 2. Generar el video
- **Modelo:** `kwaivgi/kling-v3.0-std/image-to-video`
- **Endpoint:** `POST https://api.wavespeed.ai/api/v3/kwaivgi/kling-v3.0-std/image-to-video`
- Antes de enviar, confirma los nombres exactos de los campos en https://wavespeed.ai/docs/docs-api/kwaivgi/kwaivgi-kling-v3.0-std-image-to-video y ajusta el JSON si alguno cambia.
- **Parámetros:**
  - `image`: URL de `entrada_titulo.png`
  - `end_image`: **la MISMA URL** que `image` (para que el video termine igual que empieza y se pueda repetir en bucle sin salto)
  - `duration`: 3
  - `cfg_scale`: 0.5
  - Sonido: **apagado**. Si el modelo tiene un campo de sonido/audio (por ejemplo `sound` o `generate_audio`), mándalo en `false`. Si no existe, no lo mandes.
  - No uses `multi_prompt` ni `shot_type` (no son compatibles con `end_image`).
  - `prompt` y `negative_prompt`: los de abajo, exactos.

**prompt:**
```
Animate this pixel art title screen as a subtle, seamless looping idle animation. The camera is completely locked: no zoom, no pan, no tilt, no camera shake. Keep every object and character exactly in place, with the same design, colors and chunky pixel art style as the image. Small motions only: the four students on the left breathe gently and shift their weight slightly; the green-skinned zombies at the door sway and shuffle in place with their arms stretched forward; the old janitor zombie in the doorway sways slightly and his mop moves a little; the yellow light cones of the two street lamps flicker softly; the palm tree leaves and the round bushes sway gently in a light night breeze; the moon glows softly. The scene ends exactly as it starts.
```

**negative_prompt:**
```
camera movement, zoom, pan, camera shake, scene change, cut, new characters, characters walking away, characters leaving the frame, morphing, melting, face distortion, extra limbs, realistic style, 3D render, smooth painterly shading, blur, motion blur, text, letters, logo, watermark, flashing, strobe
```

- Guarda el video tal cual llega: `RAIZ\generado\interfaz\video\titulo\raw_kling_titulo.mp4`
- Log en `RAIZ\generado\log\jobs_ui.jsonl` (id `V0_titulo_kling`, request_id, estado, segundos, error).

## 3. Post-proceso para que se vea pixel art (script Python + ffmpeg/Pillow, en `RAIZ\pipeline\scripts\`)
Guarda todo en `RAIZ\generado\interfaz\video\titulo\`:

1. **Cuadros crudos:** extrae el video a **10 fps** (unos 30 cuadros) como PNG en `cuadros_crudos\`.
2. **Paleta fija:** reduce `entrada_titulo.png` a **480×270** con promedio de área (Pillow `Image.BOX`) y saca de ahí una paleta de **48 colores** (`quantize(colors=48, method=MEDIANCUT)`). Esa misma paleta se usa en TODOS los cuadros.
3. **Cuadros pixel art:** cada cuadro crudo → reducir a **480×270** con `Image.BOX` → aplicar la paleta fija **sin dithering** (`quantize(palette=..., dither=Image.Dither.NONE)`) → guardar en `cuadros_pixel\titulo_00.png`, `titulo_01.png`… (480×270, RGB).
4. **Vistas previas para revisar** (no van al juego):
   - `preview_crudo.gif`: el video crudo a 10 fps, reducido a 960 de ancho.
   - `preview_pixel.gif`: los cuadros pixel art ampliados ×3 con NEAREST (1440×810), 10 fps, en bucle infinito.
   - `comparacion.png`: el primer cuadro y el cuadro del medio, crudo vs pixel art, lado a lado.
5. **Costura del bucle:** calcula la diferencia media de píxel entre el último y el primer cuadro de `cuadros_pixel`, y compárala con la diferencia media entre cuadros consecutivos. Anota los dos números.

**No copies nada a `gdevelop\`** todavía. Primero se revisa.

## 4. Reporte
`RAIZ\pipeline\interfaz\reportes\V0_video_titulo_reporte.md` (corto):
- request_id, estado, segundos, costo si la API lo reporta, duración y resolución reales del video.
- Si el campo de sonido existía y cómo se mandó.
- Cuántos cuadros salieron y los dos números de la costura del bucle.
- Una línea honesta: ¿se movió la cámara? ¿algún personaje se deformó o cambió? ¿alguien salió o entró a cuadro?
- Rutas de `preview_crudo.gif`, `preview_pixel.gif` y `comparacion.png`.
