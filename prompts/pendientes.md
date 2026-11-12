# Pendientes para la siguiente implementación

## Integración de videos

La implementación de videos no pudo completarse y debe retomarse desde cero o revisarse con cuidado. Por ahora solo se incorporaron archivos nuevos; la integración dentro de las escenas sigue pendiente.

### Dificultades encontradas

- Los videos se agregaron como objetos `Video::VideoObject`, pero no se comportaron como reemplazo directo de las animaciones de los sprites existentes.
- Los objetos de video podían quedar visibles simultáneamente, provocando superposición y ubicaciones incorrectas.
- La selección de personajes usa un único sprite con nombres de animación (`tony`, `miranda`, `cesar`, etc.); al sustituirlo por varios objetos de video, cada objeto requiere visibilidad, reproducción y selección coordinadas.
- Las pantallas de modos y selección comparten fondos y capas; cambiar un fondo exige ocultar explícitamente el otro y respetar el orden visual de la interfaz.
- No se contó con una validación fiable en ejecución dentro de GDevelop para confirmar reproducción, bucle, capas y escalado en todas las escenas.

### Recomendaciones

1. Abrir el proyecto en GDevelop y probar primero un solo video en una escena aislada.
2. Confirmar la sintaxis y el comportamiento exacto de las acciones de video disponibles en la versión de GDevelop usada por el proyecto.
3. Mantener los sprites originales hasta verificar cada reemplazo; no eliminarlos durante la primera prueba.
4. Para personajes, usar un solo contenedor visual o garantizar que todos los videos estén ocultos antes de mostrar y reproducir únicamente el seleccionado.
5. Revisar posición, tamaño, capa y `zOrder` en la escena real, no solo en el JSON.
6. Probar los cambios de forma independiente en las pantallas de título, modos, unión, selección de personaje y resultados.
7. Validar que el bucle, el volumen y la reproducción funcionen en la plataforma objetivo antes de dar la integración por terminada.

## Puertas

La lógica de golpes para abrir puertas fue eliminada. La puerta más cercana al jugador de teclado desaparece inmediatamente al presionar `R`.

- `R` fue elegido porque no estaba asignado a otro control de juego.
- La interacción requiere que la puerta esté a 110 píxeles o menos.
- No se añadió animación de apertura.
- No se reutilizaron botones existentes ni se modificaron sus acciones.

## Cuadro negro del mapa

Se revirtió la modificación experimental de colisiones del cuadro negro. El efecto visual vuelve a su comportamiento anterior y no se debe usar como barrera física. Si se necesita impedir el paso en el futuro, debe diseñarse una solución independiente que no convierta el efecto visual en un objeto sólido ni altere la exploración del mapa.
