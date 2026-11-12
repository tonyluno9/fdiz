# Bitácora de modificaciones

**Fecha:** 2026-11-12

## Videos

Se implementó únicamente la incorporación de nuevos archivos de video al proyecto:

- Nuevos archivos `.mp4` en `gdevelop/FDI-Z/assets/interfaz/videos/`.
- Archivo de respaldo `gdevelop/FDI-Z/FDI-Z-Original.json`.
- Script auxiliar `gdevelop/scripts/reemplazar_imagenes_por_videos.py`.

La integración de los videos en las escenas, su reproducción, ubicación, capas y selección de personajes **queda pendiente**.

## Puertas

Se eliminó la lógica de abrir puertas mediante golpes, daño, progreso o animación.

- La tecla `R`, que no estaba asignada a otro control de juego, abre inmediatamente la puerta más cercana al jugador.
- La puerta desaparece directamente al presionar `R`; no se agregó animación de apertura.
- La interacción solo se activa para el jugador de teclado y dentro de un radio de 110 píxeles.
- No se reutilizó ni se sobrepuso ningún botón existente.

## Preparación de audio y música

Se preparó la infraestructura para recibir y validar los sonidos del juego:

- Se creó el manifiesto [`gdevelop/FDI-Z/audio_manifest.json`](../gdevelop/FDI-Z/audio_manifest.json) con los 43 recursos de audio ya referenciados por los eventos del proyecto.
- Se crearon las carpetas `gdevelop/FDI-Z/efectos/` y `gdevelop/FDI-Z/musica/`, con instrucciones por categoría para la entrega de archivos.
- Se añadió [`gdevelop/scripts/validar_audio.py`](../gdevelop/scripts/validar_audio.py), que comprueba existencia, extensión `.ogg` y, si está disponible `ffprobe`, codec Vorbis, frecuencia y profundidad.
- Se añadió el catálogo [`prompts/sonidos-musica.md`](sonidos-musica.md), con IDs, descripción, variantes y prioridad.

Los archivos de audio todavía no fueron entregados; la validación quedará lista para ejecutarse cuando se copien los `.ogg` en las carpetas indicadas.

## Palabras clave para búsqueda de audio

Se actualizó [`prompts/sonidos-musica.md`](sonidos-musica.md) para añadir palabras clave en inglés para cada efecto y pista musical. Estas búsquedas están pensadas para FreeSound y bibliotecas gratuitas similares; se debe revisar la licencia de cada archivo antes de incorporarlo al juego.

## Cuadro negro del mapa

Se revirtieron las modificaciones experimentales realizadas al cuadro negro:

- `Niebla` ya no pertenece al grupo `Solidos`.
- Se eliminó el ajuste de opacidad `190`; se restauró el comportamiento original.
- No se añadió ninguna colisión alternativa al efecto visual.
- La modificación de apertura de puertas con `R` se conserva sin cambios.
