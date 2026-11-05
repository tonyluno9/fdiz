# Tarea: lote del mapa de FDI-Z (props del entorno)

Sigues siendo el agente de la computadora del equipo. Este lote genera los muebles, objetos y texturas del mapa, en el mismo estilo pixel art de los sprites.

- **Raíz:** `RAIZ` = `C:\Users\Angel Perez\Downloads\fdiz`.
- **Lista de trabajos:** `RAIZ\pipeline\manifest_mapa.json`. Son 14 hojas: 13 traen de 4 a 8 piezas cada una y 1 trae 4 texturas.
- **Límite de este lote: 20 generaciones** (14 + 6 para reintentos). Es independiente de los lotes 1 y 2, y `generar_mapa.py` ya lleva la cuenta solo de este lote.
- **Mismas reglas de siempre:**
  - una imagen por llamada
  - `1k` como máximo
  - modelo `google/nano-banana-2.1/edit`
  - API key solo desde `WAVESPEED_API_KEY`, nunca la imprimas
  - máximo 3 a la vez, retomable
  - una línea "enviado" en el log antes de esperar cada resultado
- **No toques** `RAIZ\assetsimage\` ni nada de los lotes 1 y 2.
- **Si el lote 2 todavía está corriendo,** termina primero el lote 2 y luego empieza este.

## Pasos

1. **Generar:**
   ```
   python pipeline\scripts\generar_mapa.py --todo
   ```
   Las referencias ya están en `RAIZ\mapa\referencias\`:
   - `estilo_mapa.png` es el estilo.
   - `fotos_<hoja>.png` son las fotos reales de la escuela.

   El script las sube solo.
2. **Procesar:**
   ```
   python pipeline\scripts\procesar_mapa.py
   ```
   Recorta cada pieza, quita el magenta, la escala al tamaño del juego (personaje = 96 px) y escribe:
   - `generado\sprites\mapa\<hoja>\<nombre>.png`
   - `generado\limpio_hd\mapa\...`
   - `generado\sprites\mapa\mapa_atlas.json`
   - `generado\revision\mapa\<hoja>.png`

   Las texturas solo se cortan en alta; las termina Claude.
3. **Revisar cada hoja** (puedes usar un subagente Opus, máximo 2 a la vez). Abre `generado\revision\mapa\<hoja>.png` y la raw, y califica cada hoja OK, REVISAR o REHACER:
   - **Número de piezas:** hay exactamente las que pide `nombres`, en ese orden. Si el script avisó "encontré X piezas", revísalo.
   - **Vista:** las piezas se ven en vista 3/4 desde arriba, como el resto del juego. Ninguna en perspectiva de foto ni de lado (salvo las que lo piden).
   - **Estilo:** pixel art con contorno oscuro, como `estilo_mapa.png`. Sin texto inventado, sin personas y sin fondo de la foto.
   - **Escala:** junto al personaje de la hoja de revisión, la pieza tiene un tamaño creíble.

   Si una hoja sale REHACER, tiene 1 reintento con una frase de corrección en `generado\log\prompt_overrides.json`, en `correcciones`:
   ```
   python pipeline\scripts\generar_mapa.py --ids mapa__<hoja> --rehacer
   ```
   Antes de regenerar, renombra la raw anterior a `.v1.png`.

   Si solo falla el corte (piezas pegadas o en otro orden), no regeneres: arréglalo en el procesamiento.

## Entrega

1. **Escribe `generado\revision\REPORTE_MAPA.md` en español:**
   - generaciones usadas contra el límite (20)
   - calificación de cada hoja y qué pieza falla, con su ruta
2. **Mensaje final, corto y en español:**
   - generaciones usadas
   - hojas OK
   - lista de piezas que el usuario sí debe mirar
   - ruta de `generado\revision\mapa\`
