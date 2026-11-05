# Tarea: generar todas las animaciones y sprites de FDI-Z con WaveSpeed

Eres el agente que corre en la computadora del equipo (PowerShell, Windows). Tu trabajo es generar con la API de WaveSpeed todas las animaciones, efectos y objetos del videojuego FDI-Z, limpiarlos (recortar, quitar el fondo y alinear) y dejarlos listos para GDevelop. Al final entregas las rutas y un reporte que señale solo lo que haya que revisar.

Trabaja solo, sin pedir confirmación en cada paso. Detente y pregunta únicamente si la API no responde, si falta la API key o si el piloto (fase 1) sale tan mal que no se puede corregir con los prompts.

## 1. Rutas

- **Raíz del proyecto:** `C:\Users\Angel Perez\Downloads\fdiz` (de aquí en adelante, `RAIZ`).
- **Personajes base (NO se modifican):** `RAIZ\assetsimage\`. Todos miden 848×1264, en pixel art, con fondo blanco o transparente.
  - Jugables: `tony.png`, `tonyfuerte.png` (Tony en Modo gym), `miranda.png`, `cesar.png`, `alan.png`, `castillo.png`, `alessandro.png`, `gabo.png`, `carlos.png`.
  - Profes (su papel en el juego todavía no se define): `canepa.png`, `joel.png`, `justino.png`.
  - Zombies: `Z0.png` (alumno curado), `Z1.png` (normal), `Z2.png` (corredor), `Z3.png` (gritón), `Z4.png` (gordo), `Z5.png` (conserje, jefe).
  - Criollo todavía no tiene imagen: no se genera nada de él.
- **Lista de trabajos:** `RAIZ\pipeline\manifest.json`. Trae 180 trabajos y cada uno incluye:
  - `id`, `categoria`, `entidad` y `animacion`.
  - `frames` (cuántos cuadros debe traer la tira) y `escala` (qué cuadros usar para medir la estatura).
  - `aspect_ratio`, `resolution`, `referencias` (rutas relativas a `RAIZ`, en orden: imagen 1, imagen 2) y `prompt` (exacto, en inglés).
  - `salida_raw`, `fps` y `loop`.
  - En los objetos, también `nombres` (nombre de archivo de cada objeto, de izquierda a derecha).
- **Todo lo que generes va en `RAIZ\generado\`.** No escribas fuera de esa carpeta, salvo tus scripts en `RAIZ\pipeline\scripts\`.

## 2. Reglas que no se rompen

1. **Una sola imagen por llamada a la API.** Nada de modelos "multi" ni de pedir varias salidas.
2. **Resolución máxima `1k`.** Nunca 2k ni 4k.
3. **No se cambia a ningún personaje.** Siempre se manda su imagen base como referencia, en el orden del manifiesto. No reescribas la descripción del personaje.
4. **Las animaciones van en tiras.** Cada llamada genera una sola imagen 21:9 con todos los cuadros de esa animación en fila. Nunca generes cuadro por cuadro.
5. **No gastes de más.** El límite es de 220 generaciones en total (180 del manifiesto + 40 para repetir lo que salga mal). Cada trabajo se puede repetir como máximo 2 veces. Lleva la cuenta en el log.
6. **Retomable.** Si `salida_raw` ya existe, no se vuelve a generar ese trabajo, para que si se corta la corrida no se pague doble.
7. **La API key** se lee de la variable de entorno `WAVESPEED_API_KEY`. Nunca la imprimas ni la guardes en archivos. Si no existe, pídesela al usuario para que la configure (`setx WAVESPEED_API_KEY "..."` y abrir otra terminal).
8. **No toques `RAIZ\assetsimage\`** ni ningún archivo fuera de `RAIZ\generado\` y `RAIZ\pipeline\scripts\`.

## 3. API de WaveSpeed

- **Modelo:** `google/nano-banana-2.1/edit` (Nano Banana 2.1 Edit, acepta hasta 14 imágenes de referencia).
- **Antes de la corrida grande, confirma los nombres exactos de los campos** en https://wavespeed.ai/docs/docs-api/google/google-nano-banana-2.1-edit (sobre todo el campo de las imágenes de referencia; normalmente es `images`, una lista de URLs) y ajusta tu script a lo que diga.
- **Subir las referencias:** `POST https://api.wavespeed.ai/api/v3/media/upload/binary`, con `multipart/form-data`, el campo `file` y el encabezado `Authorization: Bearer <key>`. La respuesta trae la URL en `data.download_url`. Sube cada imagen de `assetsimage` una sola vez y guarda las URLs en `RAIZ\generado\log\uploads.json` (duran 7 días).
- **Generar:** `POST https://api.wavespeed.ai/api/v3/google/nano-banana-2.1/edit` con JSON:
  ```json
  { "prompt": "<prompt del manifiesto>", "images": ["<url ref 1>", "<url ref 2>"], "aspect_ratio": "21:9", "resolution": "1k", "output_format": "png" }
  ```
  Usa el `aspect_ratio` de cada trabajo; el camión va en 9:16.
- **Resultado:** la respuesta trae un id (puede venir dentro de `data`). Consulta `GET https://api.wavespeed.ai/api/v3/predictions/{id}/result` cada 2 s:
  - con `completed`, descarga `outputs[0]` a `salida_raw`;
  - con `failed`, `cancelled`, `timeout` o `deleted`, cuéntalo como intento fallido.
- **Concurrencia:** máximo 3 trabajos a la vez. En errores de red o 5xx, reintenta con espera (2, 4 y 8 s) sin contar como generación nueva si la API no llegó a aceptar el trabajo.
- **Log:** una línea JSON por intento en `RAIZ\generado\log\jobs.jsonl`, con `id`, intento, `request_id`, estado, segundos y error si hubo.

## 4. Herramientas

Usa Python 3 (`requests`, `Pillow`, `numpy`; instala con `pip install`) para los scripts y ejecútalos desde PowerShell. Guarda los scripts en `RAIZ\pipeline\scripts\`, separados en: generación, procesamiento, revisión automática y reporte.

## 5. Fases

### Fase 1: piloto (4 trabajos)

1. Genera y procesa solo estos: `tony__caminar_lado`, `tony__especial`, `normal__caminar_abajo` y `objetos__armas`.
2. Mira tú mismo las tiras y los GIF.
3. Si los cuadros salen bien (cantidad correcta, mismo personaje, fondo magenta limpio), sigue con todo.
4. Si algo general falla, por ejemplo que siempre salgan cuadros de más o que el fondo no sea magenta, corrige solo la parte genérica de los prompts (las frases de formato), nunca la descripción del personaje, y anota el cambio en el reporte.

### Fase 2: generar todo

Corre el resto del manifiesto en este orden: personajes jugables, Tony fuerte, zombies, alumno curado, efectos, objetos y al final los profes. Así, si se acaba el límite, lo importante ya quedó.

### Fase 3: procesar cada tira

Para cada imagen en `generado\raw\...`:

1. **Quitar el fondo:**
   - Considera fondo todo lo que esté cerca del magenta (distancia RGB a (255,0,255) menor a ~90) y esté conectado con el borde de la imagen (relleno desde los bordes). Haz además una pasada global para manchas magenta aisladas entre las piernas o los brazos.
   - Limpia el halo: borra o recolorea los píxeles de orilla con tinte magenta.
   - Si quedó una sombra gris en el piso separada del cuerpo, bórrala.
   - El resultado no debe tener transparencias a medias: alfa 0 o 255.
2. **Separar los cuadros:**
   - Usa la proyección de columnas con alfa para encontrar los huecos entre cuadros. Une pedazos pequeños (chispas, líneas de movimiento) al cuadro más cercano.
   - Si no salen exactamente `frames` cuadros, intenta agrupar las piezas por su centro horizontal en `frames` grupos.
   - Si aun así no cuadra, separa en partes iguales y marca el trabajo como `REVISAR: cuadros`.
3. **Recortar** cada cuadro a su contenido.
4. **Escalar al tamaño del juego:**
   - La estatura de pie objetivo es de 96 px para personajes, profes, alumno curado y zombies; 104 px para el gordo y el conserje.
   - La estatura de referencia se mide según `escala`:
     - `standing`: mediana de la altura de todos los cuadros;
     - `frames_1_6_standing`: cuadros 1 y 6;
     - `frame_1_standing`: cuadro 1.
   - Aplica el MISMO factor a todos los cuadros de la tira; los cuadros acostado deben quedar más bajitos.
   - Efectos: el lado más grande mide 96 px.
   - Objetos (hojas de `objetos`): cada objeto se separa por su celda y su lado más grande mide 32 px. Los contenedores miden 48 px y el camión 160 px de alto.
   - Reduce con `Image.Resampling.BOX`.
   - Después ajusta los colores a la paleta de la imagen base de ese personaje (sácala cuantizando la base a 32 colores sin el fondo y pon cada píxel en su color más cercano). Esto aplica a personajes, profes y zombies. En efectos y objetos solo cuantiza a 32 colores. Sin antialias: alfa en 0 o 255.
5. **Alinear:**
   - Todas las animaciones de una misma entidad comparten un solo lienzo (ancho y alto máximos de todos sus cuadros, más 4 px de margen), excepto sus efectos.
   - Ancla en el centro de abajo: los pies sobre la misma línea (2 px arriba del borde inferior) y centrado horizontalmente según el centro de masa del cuerpo.
   - Los efectos se centran en ambos ejes.
6. **Exportar:**
   - **Cuadros sueltos:** `generado\sprites\<categoria>\<entidad>\<animacion>\<animacion>_00.png`, `_01.png`, … (los que GDevelop usa).
   - **Tira alineada:** `generado\sprites\<categoria>\<entidad>\<animacion>\<animacion>_tira.png`.
   - **Objetos:** `generado\sprites\objetos\<hoja>\<nombre>.png`, con los nombres de `nombres`.
   - **Versión limpia en alta resolución** (sin escalar, fondo transparente), para el futuro: `generado\limpio_hd\...`, con la misma estructura.
   - **GIF para revisar,** ampliado 4× sin suavizado, sobre fondo gris claro, con el `fps` del manifiesto: `generado\preview\<categoria>\<entidad>\<animacion>.gif`.
   - **Atlas** en `generado\sprites\atlas.json`, por entidad y animación: lista de cuadros, tamaño de lienzo, ancla `bottom-center`, `fps` y `loop`. Agrega una nota de que la izquierda es el espejo de `caminar_lado`, `pegar_lado` y `atacar_lado`, y que el cuadro 4 de `caer_levantarse` sirve como estado "caído".

### Fase 4: revisión automática

Para cada animación, calcula y guarda en `generado\revision\metricas.json`:

- Cuadros detectados contra esperados.
- Variación de estatura entre cuadros de pie (marca si pasa de 12%).
- Píxeles magenta sobrantes.
- Cuadros cortados (que tocaban el borde de la imagen original).
- Distancia de color contra la paleta de la base (marca si es alta: puede ser otro personaje u otra ropa).
- Cuadros repetidos idénticos en animaciones que deberían moverse.

### Fase 5: revisión de coherencia con Opus

1. Para cada entidad, arma una hoja de contacto en `generado\revision\hojas\<entidad>.png`: a la izquierda su imagen base y a la derecha cada tira alineada, ampliada 2× y con su nombre.
2. Lanza un subagente con el modelo **Opus** (`model: "opus"`) por entidad, hasta 4 a la vez. Dale la ruta de la hoja de contacto, la imagen base, los GIF de esa entidad y sus métricas.
3. Pídele que califique cada animación como **OK**, **REVISAR** o **REHACER**, con una línea de razón, según estos criterios:
   - Mismo personaje que la base: cara, cabello, lentes, ropa, colores y complexión. Es lo más importante.
   - Cantidad y orden de cuadros correctos.
   - La vista y la dirección coinciden con el nombre (de frente, de espaldas, de lado mirando a la derecha).
   - El movimiento se entiende y el ciclo cierra bien si es `loop`.
   - Mismo estilo de pixel art (tamaño de píxel, contornos).
   - Sin texto, objetos ni personajes de más; sin sangre ni gore.
   - Que sea lo que dice la habilidad (por ejemplo, que Miranda de verdad tenga una minigun).
4. **REHACER:** si queda límite, se regenera una vez con el mismo prompt más una frase corta de corrección que proponga el revisor (por ejemplo, "keep his glasses", "exactly 6 frames"), se procesa y se revisa de nuevo. Si sigue mal o no queda límite, se queda marcada.
5. Si no puedes lanzar subagentes, haz tú la revisión con los mismos criterios, viendo las hojas de contacto.

### Fase 6: reporte y entrega

1. **`generado\revision\index.html`:** una página que se abre en el navegador con todas las entidades. Por cada una, su imagen base y los GIF de todas sus animaciones con su calificación; las marcadas, resaltadas en amarillo (REVISAR) o rojo (REHACER).
2. **`generado\revision\REPORTE.md`, en español:**
   - Generaciones usadas contra el límite y trabajos fallidos.
   - Cuántas animaciones quedaron OK, cuántas en REVISAR y cuántas en REHACER.
   - **Una tabla solo con las que hay que revisar**, con entidad, animación, calificación, razón y ruta del GIF y de la tira.
   - Lo que no se generó y por qué (Criollo sin imagen; profes con un set básico porque su papel no se ha definido).
   - Cualquier cambio que hayas hecho a los prompts genéricos.
3. **Mensaje final al usuario,** corto y en español:
   - Ruta de los sprites listos (`RAIZ\generado\sprites`).
   - Ruta de la página de revisión (`RAIZ\generado\revision\index.html`) y del reporte.
   - Cuántas quedaron bien.
   - La lista corta de las que sí conviene que mire él, con su razón. No le pidas revisar todo: solo lo marcado.
