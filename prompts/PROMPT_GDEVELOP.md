# Tarea: armar FDI-Z en GDevelop controlando la computadora

Vas a construir el juego **FDI-Z** en **GDevelop 5**, en la computadora del equipo. Puedes ver y controlar la pantalla, y tienes acceso a la carpeta del proyecto. Trabaja por fases y prueba cada fase en la vista previa antes de seguir. Escribe todo en español.

## 1. Antes de empezar, lee esto

- **Descripción del juego (fuente de verdad):** https://claude.ai/artifact/WRfCcXiUBGqcQrUMCznaW9
  - Modos, personajes, habilidades y especiales, zombies, objetivos y tienda del Jefe.
  - Cinemática de inicio y ambiente del mapa.
  - Sección "Cómo hacerlo en GDevelop".
- **Lista de tareas y decisiones del equipo:** https://claude.ai/artifact/HBUcMHbZtSs1tioQKWiFkv
  - Trae notas del equipo encima del texto. Si chocan con la descripción, mandan las notas.
- **Lista de sonidos:** https://claude.ai/artifact/QBeFXk2LWCt3LjEe14gYQL
  - Todavía no hay audios. Deja los eventos de sonido listos con esos nombres de archivo.
- `mapa\final\LEEME_MAPA.md`: cómo está hecho el mapa y sus archivos.

## 2. Carpeta y assets

`RAIZ` = `C:\Users\Angel Perez\Downloads\fdiz`

| Qué | Dónde |
|-----|-------|
| Sprites de personajes, zombies, profes, objetos y efectos (PNG por cuadro) | `RAIZ\generado\sprites\` |
| Índice de animaciones: cuadros, lienzo, ancla, fps y loop | `RAIZ\generado\sprites\atlas.json` |
| Vista previa en GIF de cada animación | `RAIZ\animaciones_gif\` |
| Muebles y objetos del mapa | `RAIZ\generado\sprites\mapa\` y `mapa_extra\`, índice `mapa\mapa_atlas.json` |
| Mapa en Tiled, con el tileset incrustado | `RAIZ\mapa\final\mapa_fdiz_gdevelop.json` + `tileset_fdiz.png` |
| Colisiones, zonas de niebla, puertas y marcadores de objetivos (en px) | `RAIZ\mapa\final\mapa_fdiz_datos.json` |
| 661 muebles y objetos colocados, con su choque | `RAIZ\mapa\final\mapa_fdiz_props.json` |
| Imagen del mapa completo para ubicarte | `RAIZ\mapa\final\mapa_fdiz_con_props_cuarto.png` y `mapa_fdiz_guia.png` |
| Retratos y bases de personajes (solo lectura) | `RAIZ\assetsimage\` |
| Íconos de habilidades y mockups de interfaz (si ya se corrió el lote 2) | `RAIZ\generado\sprites\iconos\`, `RAIZ\generado\mockups\` |

Notas del atlas:
- El ancla está abajo al centro: los pies quedan 2 px arriba del borde inferior del lienzo.
- La izquierda es el espejo de `*_lado`: voltea el sprite, no hay animación aparte.
- Todas las animaciones de una entidad comparten el mismo lienzo.
- El cuadro 4 (índice 03) de `caer_levantarse` sirve como estado "caído".

## 3. Reglas

- **No modifiques** `RAIZ\assetsimage\`, `RAIZ\generado\raw\` ni los PNG originales de `generado\sprites\`. Si necesitas variantes, cópialas dentro del proyecto.
- **No gastes generaciones de WaveSpeed** ni crees assets nuevos con IA sin preguntarme. Si falta algo, usa un marcador provisional (rectángulo de color con nombre) y anótalo.
- **No borres nada sin preguntar.** Antes de editar el archivo del proyecto a mano o con un script, haz una copia de respaldo con fecha.
- **El mapa es provisional:** van a mandar fotos nuevas para corregir el edificio A, la nevería y la plaza a la derecha de B.
  - Todo lo que salga de `mapa_fdiz_*.json` tiene que poder volver a importarse con un solo script, que borre y vuelva a crear las instancias del mapa.
  - No coloques muebles del mapa a mano.
- **Bitácora:** lleva `RAIZ\gdevelop\BITACORA.md` con lo que hiciste, lo que falta y los problemas encontrados. Al terminar cada fase, mándame un resumen corto con capturas de pantalla.

## 4. Datos técnicos que ya están decididos

- **Proyecto:** `RAIZ\gdevelop\FDI-Z\`. Copia ahí los recursos que use el juego, para que el proyecto sea portable.
- **Resolución:** 1920×1080.
  - Pixel art: desactiva el suavizado de texturas y usa redondeo de píxeles.
  - Personajes a 96 px de alto (gordo y conserje, 104).
  - Casillas de 32 px: un personaje mide 3 casillas.
- **Velocidades:** las de la descripción estaban pensadas para sprites de 32 px, así que multiplícalas ×3.
  - Ejemplo: Tony 204 px/s, zombie normal 99 px/s.
  - El radio en el que un zombie "te nota" pasa de 85 a 255 px.
  - Ajusta jugando si se siente lento o rápido.
- **Capas, de abajo hacia arriba:**
  - Fondo: tilemap.
  - Juego: personajes, zombies y muebles ordenados por Y.
  - Techo: copas de árboles.
  - Niebla.
  - Luz: luz ambiente oscura, porque es de noche.
  - HUD: fija a la cámara.
- **Cámara compartida:** centrada en el promedio de los jugadores, se aleja si se separan y nadie puede salirse de la pantalla.
- **Controles:** se adaptan a lo que use cada jugador.
  - Teclado: WASD para moverse, mouse para apuntar y clic para pegar. Las teclas de habilidad, especial, usar y lanzar van como dice la descripción.
  - Control de Xbox: stick y botones.
  - Los letreros de ayuda muestran la tecla o el botón de quien los lee.
- **Mapa en GDevelop:**
  - Objeto Tilemap con `mapa_fdiz_gdevelop.json` y `tileset_fdiz.png`, más un objeto Tilemap collision mask con la clase `muro`.
  - El comportamiento Pathfinding necesita objetos obstáculo: crea un sprite invisible `Muro` por cada rectángulo de `colisiones` y uno `ChoqueMueble` por cada mueble que trae `colision` en `mapa_fdiz_props.json`.
  - Niebla: un sprite negro por zona, con las variables Zona y Grupo.
  - Puertas: con su Tipo (normal, electronica, restringida, restringida_electronica), su Vida y las Zonas que abren.
  - Marcadores: inicio de jugadores, objetivos, bidones, rejillas del Jefe, Joel y Justino, camión.
- **Muchas instancias:** colocar 650 muebles con clics es lento y frágil. Usa este método:
  1. Arma en la interfaz lo mínimo (escena, capas, un objeto de ejemplo) y guarda.
  2. Cierra GDevelop.
  3. Con un script de Python, agrega objetos e instancias al `.json` del proyecto, copiando la estructura que GDevelop guardó.
  4. Vuelve a abrir GDevelop y revisa.

  Para eventos complejos puedes hacer lo mismo: crea un evento de ejemplo en la interfaz, guarda, mira cómo quedó en el JSON y reproduce el patrón. Siempre con respaldo previo.

## 5. Lo que tiene que hacer el juego

Está todo en la descripción. Lo más importante:

- **Personajes jugables:** Tony (con su forma `tonyfuerte` en el Modo gym), Miranda, César, Alan, Castillo, Alessandro, Gabo y Carlos.
  - Cada uno tiene Habilidad, Especial y Pasiva.
  - Juegan de 1 a 4; si faltan jugadores, entran bots.
- **Zombies:** normal, corredor, gritón, gordo, conserje y "curado" (el de Castillo).
  - La infestación sube por niveles.
- **Profes:**
  - Canepa repara y maneja el camión.
  - Joel y Justino tienen miedo y se les puede rescatar.
  - A los profes no los muerden.
- **Salvar o no salvar:** aplica a Joel, a Justino y también a compañeros mordidos.
- **Modos:**
  - Supervivencia: cooperativo con objetivos y final "¡Aguanten!" en el estacionamiento.
  - Jefe de zombies: un jugador con mouse compra zombies con oro.
- **Cinemática de inicio (en los dos modos, se puede saltar):**
  - Ocurre en el salón de la esquina izquierda del edificio B, antes del pasillo de separación, en la planta 1.
  - El mapa por ahora solo tiene planta baja: usa el salón de B que está en esa posición y anótalo como pendiente.
  - Están solo los personajes que se juegan. El profe Canto no llega; el grupo hace relajo hasta que les suena la alerta en el teléfono.
  - Se ve a alumnos sin nombre convertirse en zombies. El grupo atranca la puerta y un zombie la rompe.
  - El **jugador 1** agarra la regla y aparece "clic para pegar". Luego cada quien toma un arma del salón y empieza el juego.
- **Ambiente:** de noche, luces que parpadean, zonas sin luz y destrozos recientes.
  - Los objetos de destrozo todavía no existen: deja dónde irían.

## 6. Orden de trabajo

En cada fase: vista previa, prueba con teclado (y control si hay uno conectado), captura de pantalla, corregir y anotar en la bitácora.

1. **Revisión:**
   - Lee los documentos y revisa la carpeta.
   - Abre GDevelop y confirma la versión.
   - Escribe en la bitácora el plan y la lista de assets que faltan.
   - Mándame ese resumen antes de seguir.
2. **Proyecto base:**
   - Escena Juego con las capas, la resolución y el pixel art bien configurados.
   - Un personaje (Tony) con sus animaciones del atlas, caminando en 4 direcciones (izquierda = espejo) y la cámara siguiéndolo.
3. **Mapa:**
   - Tilemap y colisiones.
   - Script que importa muros, muebles, puertas, zonas de niebla y marcadores desde los JSON.
   - Comprueba que no se atraviesan paredes ni muebles y que las puertas se abren.
4. **Combate y zombies:**
   - Pegar y armas del salón.
   - Zombie normal con Pathfinding, vida y daño.
   - Luego los demás tipos.
   - Infestación.
5. **Multijugador local:**
   - Hasta 4 jugadores con controles que se adaptan.
   - Bots.
   - Cámara compartida.
   - Revivir.
6. **Zonas y objetivos:**
   - Niebla por zonas y tipos de puerta.
   - Objetivos al azar, flecha amarilla y final en el estacionamiento.
   - Rescates.
7. **Habilidades y especiales** de los 8 personajes, y la pasiva de cada uno.
8. **HUD, menús, selección de personajes y Resultados.**
9. **Cinemática de inicio y modo Jefe de zombies.**
10. **Ambiente y sonido:** luces, parpadeo, marcadores de destrozos y eventos de sonido.
11. **Modo presentación (F1)** y pruebas completas de una partida de 8 a 12 minutos.

Si algo no está claro o una decisión cambia el juego (no un detalle técnico), pregúntame antes de seguir.
