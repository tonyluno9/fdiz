# Pendientes (no implementados)

## 1. Diálogos entre personajes
Objetivo: diálogos entre personajes con mejor UI, que detecten solos qué personajes están en el equipo, aleatorios y con duración definida.

Recomendaciones:
- **Datos aparte del código:** un archivo JSON/JS (`gdevelop/scripts/datos/dialogos.json`) con entradas `{id, requiere:["tony","miranda"], contexto:"inicio|zombis_cerca|herido|objetivo_cumplido|calma", lineas:[{quien:"tony", texto:"..."}, ...], duracion:3.5, peso:1}`. Así se agregan diálogos sin tocar eventos.
- **Detección de equipo:** en JS, cada cierto tiempo leer los `Sup` vivos y su variable `Personaje`; un diálogo es elegible solo si todos sus `requiere` están en el equipo (en online, tras la sincronización, el host decide).
- **Aleatoriedad controlada:** elegir por peso entre los elegibles del contexto actual; guardar cooldown global (p. ej. 25–45 s entre diálogos) y cooldown por diálogo para que no se repitan seguidos.
- **Disparadores por contexto:** reutilizar variables que ya existen (Infestacion, Estado, Banner, vida baja de un Sup, objetivo cumplido, zombis cerca) en vez de crear lógica nueva.
- **Duración:** cada línea con tiempo propio (~0.06 s por carácter, mín. 2 s); cola de líneas; no mostrar diálogos durante el modo Jefe del lado del Jefe ni mientras hay un banner importante.
- **UI:** globo estilo cómic anclado sobre el personaje que habla (cola hacia el Sup), retrato pequeño (HudRetrato), nombre coloreado por personaje, fondo semitransparente con borde, aparición con fade/escala. Usar el patrón de textos en pool que ya usan `jefe_modo.js` y `net_core.js`.
- **Online:** que el host decida y mande `{t:"dlg", id}` por el canal existente; los clientes solo lo dibujan (igual que los sonidos).
- **Pruebas:** modo depuración que fuerza un diálogo por tecla y un equipo fijo.

## 2. Mejorar la UI de los eventos
Objetivo: que banners, avisos y mensajes de eventos no parezcan texto sobrepuesto.

Recomendaciones:
- Un único sistema de avisos (toast/banner) en JS con panel de fondo (sprite 9-slice), icono por tipo de evento, borde, sombra y animación de entrada/salida; cola con prioridades (crítico > objetivo > informativo).
- Definir 3–4 estilos (peligro rojo, objetivo amarillo, éxito verde, info azul) y reutilizarlos en Banner, objetivos, rescates, final ¡Aguanten! y apagón.
- Generar el arte de los paneles/iconos con el mismo flujo de arte pixel (prompts en inglés) y registrarlos como recursos.
- Reemplazar gradualmente los `TxtBanner/TxtObjetivo` actuales; mantener la variable `Banner` como entrada para no reescribir eventos.
- Probar legibilidad sobre mapa claro y oscuro, y con el apagón.

## 3. Zonas sin texturas y bugs visuales
- Hacer un recorrido sistemático del mapa con una lista por zona (captura + nota) y atacar primero lo que se ve en la ruta del juego.
- Revisar capas (Fondo/Juego/Techo) y z-order en las zonas con fallos; confirmar que las instancias usan los tiles/recursos correctos y que no faltan imágenes en el JSON.
- Añadir una tecla de depuración que muestre cajas de colisión y nombres de zona para ubicar rápido los huecos.

## 4. Modelos y mecánicas de profesores
- Definir primero la lista de profesores, su rol (jefe de zona, aliado, obstáculo) y 1–2 mecánicas por cada uno (ataque, habilidad, condición de derrota).
- Crear el arte (sprites con animaciones quieto/caminar/atacar/muerte) con el flujo habitual y registrarlo como objetos nuevos; reutilizar la IA de zombis (`Zombies: IA`) como base y añadir un tipo de variable `Rol`.
- Agregar sus objetos a la lista de sincronización online (`fase25_online.py`, `TRACK`) para que se vean en los clientes.

## 5. Tienda (opcional, se puede omitir)
- Si se implementa: escena o panel propio con la moneda ya existente (`Dinero`), 4–6 artículos baratos, y compras que solo cambien variables de Sup para que sea simple.
- En online, la compra la valida el host.
