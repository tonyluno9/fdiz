# FDI-Z · Bitácora de armado en GDevelop

## Fase 1 · Revisión (5 nov 2026)

### Qué se hizo
- Leí `prompts\PROMPT_GDEVELOP.md`, la descripción del juego, la lista de tareas del equipo (con sus notas), la lista de sonidos y `mapa\final\LEEME_MAPA.md`.
- Revisé la carpeta `fdiz`: `atlas.json`, `mapa_atlas.json`, `mapa_fdiz_datos.json`, `mapa_fdiz_props.json`, `mapa_fdiz_gdevelop.json` y la guía del mapa.
- Abrí GDevelop: **versión 5.6.287** (editor 5.6.287-cfaccd2c, core 5.6.287-0), la más reciente según el propio programa. Al primer intento Windows no lo encontraba; al reintentar sí. Captura: `gdevelop\capturas\fase1_gdevelop_version.jpg`. No toqué ni borré nada.

### Bloqueos
1. ~~GDevelop no está instalado~~: resuelto, está instalado (5.6.287).
2. **La ruta RAIZ del prompt no es la de esta PC.** El prompt dice `C:\Users\Angel Perez\Downloads\fdiz`; aquí es `C:\Users\alane\Downloads\fdiz`. Uso la segunda.

### Decisiones que tomo (técnicas)
- **Personajes jugables:** los 8 del prompt (Tony/tonyfuerte, Miranda, César, Alan, Castillo, Alessandro, Gabo y Carlos). Criollo, Alfredo y Tillit quedan fuera aunque sigan en los documentos.
- **Poderes:** mandan las notas del equipo sobre la descripción. Por ejemplo, Miranda usa minigun y Alan tiene Gorrear, Reembolso y Ojo de oferta (no Rayos X). Además, cada personaje tiene su pasiva y existe el dinero del equipo ($).
- **Zombies:** normal, corredor, gritón, gordo, conserje (jefe, 250 de vida) y curado.
- **Escala:** los lienzos del atlas miden de 100 a 127 px de alto. Voy a escalar cada entidad para que el cuerpo mida 96 px (104 el gordo y el conserje), sin suavizado.
- **Cafetería = Nevería.** En el mapa, la carnada y el festín de Tony van en la Nevería (`carnada_neveria`).
- **Conteos reales del mapa** (el LEEME tiene otros más viejos): 244 colisiones, 46 zonas de niebla, 52 puertas (48 normales, 2 restringidas, 1 electrónica y 1 restringida-electrónica), 661 muebles (507 con choque) y 11 rejillas del Jefe. El script de importación va a leer los JSON, no a usar números fijos.

### Preguntas abiertas → decididas por Claude (5 nov, a pedido de Alan)
- **Especial = C** (nota más nueva del equipo); **Lanzar = clic derecho o Q**. Habilidad = E.
- **Salón de la cinemática = B-01** (primer salón al bajar del pasillo de separación de B). Queda en una variable para cambiarlo fácil.

Texto original de las preguntas:
1. **Tecla del Especial.** La tabla de controles dice Q, pero una nota nueva del equipo dice "una con la E y la otra con la C". ¿El Especial va en C? ¿Y Q queda libre o sirve para algo?
2. **Salón de la cinemática.** El edificio B es una columna vertical y el pasillo que lo separa queda entre B-06 (arriba) y B-01 (abajo). ¿"La esquina izquierda antes del pasillo" es B-06 o B-01?

### Plan (orden del prompt)
1. Revisión. **Hecha.**
2. **Proyecto base:** crear `gdevelop\FDI-Z\` con la escena Juego a 1920×1080, sin suavizado y con redondeo de píxeles. Capas: Fondo, Juego (orden por Y), Techo, Niebla, Luz y HUD. Tony con su atlas (izquierda = espejo) y la cámara siguiéndolo.
3. **Mapa:** Tilemap + Tilemap collision mask (`muro`). Un script de Python (`gdevelop\scripts\importar_mapa.py`) que respalda el proyecto con fecha, borra lo que importó antes (todo lo marcado con la variable `DeMapa`) y vuelve a crear muros, choques de muebles, muebles, puertas, nieblas y marcadores.
4. **Combate y zombies:** puños y armas, el zombie normal con Pathfinding (recalcula cada 0.5 s), los demás tipos y la infestación.
5. **Multijugador local:** hasta 4 jugadores (teclado y ratón + controles Xbox, con ayuda según el dispositivo), bots, cámara compartida y revivir.
6. **Zonas y objetivos:** niebla, tipos de puerta, 3 objetivos al azar, flecha amarilla, "¡Aguanten!" y rescates de Joel, Justino y compañeros mordidos.
7. **Habilidades, especiales y pasivas** de los 8 personajes.
8. **HUD, menús, selección de personajes y Resultados.**
9. **Cinemática de inicio** (en los dos modos, se puede saltar) y modo Jefe de zombies.
10. **Ambiente y sonido:** luces y parpadeo, marcadores de destrozos y eventos de sonido con los nombres de la lista.
11. **Modo presentación (F1)** y partidas completas de prueba.

### Assets que faltan (irán con marcadores provisionales: rectángulos de color con nombre)
**Personajes y profes**
- `tonyfuerte`: solo tiene quieto, caminar y pegar_lado. Le faltan pegar arriba y abajo, caer/levantarse, habilidad, especial y festejo.
- Joel y Justino: solo tienen imagen base en `assetsimage`, sin animaciones.
- Profesor Canto: no existe (Justino lo suple).
- Canepa: le faltan reparar y caer.
- Alumnos sin nombre y la animación de alumno convirtiéndose en zombie (cinemática).

**Zombies**
- No hay animación de dormido/quieto, reírse ni recibir golpe por separado (`golpe_morir` viene junta).
- Ninguno tiene `atacar_arriba`.
- El curado solo tiene pegar_lado.

**Objetos**
- Rastrillo, cofre (abierto y cerrado), interruptor (apagado y prendido), servidor (apagado y prendido), computadora (normal, parpadeando y llamada hecha), barricada y camión arrancando.
- Puertas por estado (abierta, cerrada, electrónica, restringida y rota): no las encontré como sprites; hay que confirmar si vienen en el tileset.

**Efectos**
- "JAJA" de risa, flecha amarilla, aviso "¡REVÍVANME!", rejilla de aparición y números de daño (estos se pueden hacer con texto).

**Interfaz**
- No existen `generado\sprites\iconos\` ni `generado\mockups\` (el lote 2 no se ha corrido).
- Faltan el logo FDI-Z, los íconos de habilidad, el marco del HUD, las cartas del Jefe y los retratos recortados.
- La fuente pixel con acentos no está en la carpeta.

**Mapa**
- Solo hay planta baja: la planta 1 de B, donde ocurre la cinemática, queda pendiente.
- Hay 2 interruptores de luz y el objetivo pide 3.
- Faltan los props de destrozo y las fotos nuevas del edificio A, la nevería y la plaza a la derecha de B.

**Sonido y música**
- No existe la carpeta `sonido` ni `musica`; hay 0 audios. Los eventos van a quedar listos con los nombres de la lista de sonidos.

## Fase 2 · Proyecto base (5 nov 2026) — HECHA

### Qué se hizo
- Proyecto creado desde GDevelop: `gdevelop\FDI-Z\FDI-Z.json` (Escritorio Full HD, optimizado para pixel art).
- Script `gdevelop\scripts\fase2_base.py` (+ `gd_util.py`), re-ejecutable:
  - 1920×1080, antialiasing apagado, escalado `nearest` y redondeo de píxeles.
  - Escena **Juego** (primera escena) con capas, de abajo hacia arriba: `""` (base vacía, la usan las acciones de cámara), Fondo, Juego, Techo, Niebla, Luz (iluminación con luz ambiente de noche suave, se ajusta en la fase 10) y HUD (fija a la cámara).
  - **Tony**: 11 animaciones del atlas copiadas a `FDI-Z\assets\sprites\personajes\tony\` (los originales no se tocaron). Origen en los pies (40, 125); máscara de choque solo en los pies (28×16 px) para caminar "detrás" de los muebles.
  - **Escala 1:1:** el cuerpo de Tony ya mide 96 px dentro de su lienzo (y 29→125), así que no hace falta reescalar.
  - Movimiento top-down a **204 px/s** (68 × 3) con WASD, controles por defecto apagados.
  - Animación según la velocidad: caminar_lado (izquierda = espejo), caminar_arriba, caminar_abajo y quieto.
  - Orden Z = Y.
  - Cámara centrada en Tony con suavizado.
  - Piso de prueba provisional (cuadrícula de 32 px) hasta que entre el mapa en la fase 3.
- `gdevelop\scripts\depuracion.py`: grupo rojo **Depuración** con piloto automático (I/J/K/L caminar solo, O parar) para probar animaciones. **Quitar antes de presentar** con `python depuracion.py FDI-Z.json --quitar`.
- Respaldos con fecha en `gdevelop\respaldos\`.

### Pruebas
- La vista previa abre sin errores.
- WASD mueve a Tony y la cámara lo sigue: se ve la orilla del piso de prueba.
- Las cuatro direcciones y el espejo a la izquierda se ven bien.
- Capturas en `gdevelop\capturas\fase2_*`.

### Problemas encontrados
- A veces el botón Vista previa necesita dos clics: el primero solo da foco a GDevelop.
- GDevelop guarda el proyecto al lanzar la vista previa. Antes de cada script hay que cerrar GDevelop y partir del archivo guardado (el script ya hace respaldo).
- Las carpetas de objetos que mete el script no las respeta GDevelop. Las dejo planas y GDevelop las acomoda.

### Pendiente para fases siguientes
- Control de Xbox: necesita la extensión **Gamepads** de la tienda de extensiones de GDevelop. Se instala en la fase 5. No hay control conectado para probar.
- Mirar hacia la dirección del mouse (apuntar) y "quieto" según el último lado: fase 4/5.

## Fase 3 · Mapa (5 nov 2026) — HECHA

### Qué se hizo
- **`gdevelop\scripts\importar_mapa.py RAIZ PROYECTO`**: un solo script que se vuelve a correr cuando cambie el mapa (con GDevelop cerrado). Hace lo siguiente:
  - Saca respaldo con fecha.
  - Copia el JSON de Tiled, el tileset y los 73 PNG de muebles a `FDI-Z\assets\mapa\`.
  - **Borra y vuelve a crear** todos los objetos e instancias del mapa:
    - `Mapa` (Tilemap) y `MapaChoque` (Tilemap collision mask, clase `muro`).
    - `MapaFondo`: el piso y los muros dibujados con 15 pedazos de 2048 px de `mapa_fdiz_completo.png`.
    - **244 `Muro`** (rectángulos de `colisiones`) y **507 `ChoqueMueble`**, los dos con comportamiento de obstáculo de Pathfinding.
    - **658 `Mueble`**: un solo objeto con 74 animaciones, una por sprite; cada instancia elige la suya y lleva orden Z = Y.
    - **52 `Puerta`** con Id, Tipo, Estilo, Orientación, Zonas, Vida, TiempoAbrir y Progreso. Son rectángulos de color por tipo; también son obstáculos.
    - **46 `Niebla`** con Zona y Grupo, en la capa Niebla.
    - **47 `Marcador`** con Tipo, Zona, Nota e Índice: inicio de jugadores, camión, Canepa, rejas, servidor, interruptores, computadoras, llaves, conserje, carnada, horda, bidones, bolsa de comida, botín, tarjeta, Joel, Justino, rejillas y el salón de la cinemática (B-01).
  - Pone a los jugadores en el punto de inicio (E-04).
  - No necesita librerías, salvo Pillow para recortar el fondo (`pip install pillow`).
- **`gdevelop\scripts\fase3_eventos.py`**:
  - Quita el piso de prueba.
  - Oculta las ayudas al empezar.
  - Pone el choque de Tony contra el grupo `Solidos` (Muro, ChoqueMueble, Puerta).
  - Puertas con F: normal 1 s, electrónica 8 s; las restringidas no se abren con F.
  - Cámara limitada a la orilla del mapa.

### Pruebas
- **Fondo:** el mapa se ve completo y con luz de noche.
- **Choques:** Tony no atraviesa paredes ni muebles (pupitres, pared lateral, pared de abajo).
- **Puertas:** con F lejos no pasa nada. Junto a la puerta se abre solo esa después de 1 s y se puede salir.
- **Capturas:** `capturas\fase3_*`.

### Problemas encontrados
- **El objeto Tilemap sale casi negro en la vista previa** de GDevelop 5.6.287, aunque en el editor se ve bien.
  - Descarté la capa Luz, el collision mask, el tipo de render de las capas y el tileset.
  - Solución: el fondo se dibuja con `MapaFondo`. El Tilemap se queda en el proyecto (lo usa el collision mask y sirve para el editor) y se oculta al empezar.
  - Si en otra versión de GDevelop se arregla, basta con quitar `MapaFondo` y la acción que oculta `Mapa`.
- **`DistanceToObject` no existe** en las expresiones de GDevelop; la correcta es `Objeto.Distance(Otro)`. Ya está corregido; con el error se abrían todas las puertas a la vez.
- **Sprite que falta:** `generado\sprites\mapa_extra\cic__mostrador_curvo_h180.png` no existe en la carpeta. El mostrador del CIC sale como rectángulo magenta.
- **Mesas redondas:** las 14 de `props_exteriores` no vienen en `mapa_fdiz_props.json`. Solo se colocan las mesas que ya trae ese archivo.
- **Árboles:** son sprites completos sin copa aparte, así que van en la capa Juego ordenados por Y. La capa Techo queda vacía hasta que haya copas separadas.
- **Rendimiento:** hay unas 800 instancias de obstáculo de Pathfinding. Si en la fase 4 el Pathfinding va lento, se juntan los choques de muebles vecinos.

### Pendiente
- Niebla y reglas por tipo de puerta: fase 6.
- Rejas y camión como objetos con estado: fases 6 y 9.

## Fase 4 · Combate y zombies (5 nov 2026) — BASE FUNCIONANDO

### Qué se hizo (`gdevelop\scripts\fase4_combate.py`, re-ejecutable)
- **Pegar:** con clic izquierdo hacia el cursor. Mantener el clic sigue pegando según la cadencia del arma.
  - Animación pegar_lado/arriba/abajo según hacia dónde apuntas; la izquierda es el espejo.
  - El golpe le pega a los zombies cuyo cuerpo queda dentro de un radio frente a Tony; el radio depende del alcance del arma.
  - Al pegar: el zombie se pone rojo, sale empujado, suelta salpicadura verde y empieza a perseguirte.
- **Armas del salón:**
  - Hay escoba, regla y silla en E-04, el extintor en el pasillo de E y el bate en el botín de Dirección.
  - Se recogen pasando encima con las manos vacías.
  - Daño, alcance, cadencia y usos según la tabla del equipo; al acabarse los usos vuelves a los puños.
- **Zombies:**
  - Objetos ZNormal, ZCorredor, ZGriton, ZGordo y ZConserje (más ZCurado, listo para Castillo) en el grupo `Zombies`.
  - Vida, daño, velocidad (×3) y oro del Jefe según la tabla.
  - Te notan a 255 px y persiguen con Pathfinding: la ruta se recalcula cada 0.75 s y, si no hay ruta, van directo hacia ti.
  - Pegan cada 1 s.
  - El gritón despierta a los que están a 450 px.
  - El gordo y el conserje empujan.
  - Al morir se reproduce golpe_morir, se borran y suman a `Tumbados` y a `OroJefe`.
- **Tony:**
  - Con 0 de vida cae: se queda en el cuadro 4 de caer_levantarse.
  - Revivir con compañeros queda para la fase 5.
- **Infestación:**
  - Sube un nivel cada 95 s, hasta 5.
  - Zombies objetivo por nivel: 10/15/22/30/40. Velocidad +8% por nivel.
  - Tipos por nivel: corredores desde el 2; gordos y gritones desde el 3.
  - Salen cada 2 s por las **salidas libres junto a las rejillas** (las calcula `importar_mapa.py`) que estén lejos de la cámara.
- **Depuración:**
  - Texto amarillo arriba con estado, vida, arma, infestación, zombies y tumbados.
  - Teclas: U levanta a Tony, N sube la infestación, Z crea un zombie (todavía no funciona).
- **Recursos:**
  - Los sprites de zombies, armas y efectos se leen de `..\..\generado\sprites\` para no copiar 200 archivos uno por uno desde aquí.
  - `gdevelop\scripts\empaquetar_recursos.py` los copia dentro del proyecto con un solo comando, para que FDI-Z sea portable. Correrlo antes de mover la carpeta o exportar.

### Pruebas
- Recoger la escoba: el contador de usos baja con cada golpe.
- Abrir la puerta, salir y pelear: Tony tumbó un zombie y la infestación repuso otro.
- Los zombies le quitan vida a Tony.
- Capturas: `capturas\fase4_*`.

### Problemas encontrados y soluciones
- **Pathfinding sin ruta:** cientos de avisos "No path was found", sobre todo con zombies que salían de rejillas pegadas a la pared. Se arregló con las salidas libres calculadas, el plan B de ir directo y la ruta cada 0.75 s.
- **Golpes que no conectaban:** los zombies solo chocan con los pies (para no trabarse en las paredes). La detección del golpe ahora usa la distancia al cuerpo.
- **El juego parecía congelado:** en realidad Tony estaba caído y por eso ignoraba los clics.
- **Pruebas automáticas:** un clic de menos de un cuadro no lo detecta GDevelop; para probar hay que mantener el botón. Un jugador real no tiene este problema.

### Pendiente de la fase 4
- **Números de daño y temblor de cámara:** van con el HUD en la fase 8. El objeto de texto ya funciona.
- **Animaciones que faltan en los zombies:** no hay `atacar_arriba`, dormido ni reírse. Por ahora se usa lo que existe.
- **Extintor:** su efecto de cono que aturde llega con habilidades y efectos (fase 7). Por ahora pega 3 y empuja.
- **Tecla Z de depuración:** no creó el zombie; hay que revisarla.
- **Ajustes de juego:** balance de daño y velocidad cuando se juegue en serio.
- **Rendimiento:** probar con 40 zombies en la laptop de la presentación.

## Fase 5 · Multijugador local (5 nov 2026) — HECHA
### Qué se hizo (`gdevelop\scripts\fase5_jugadores.py`, re-ejecutable; regenera TODOS los eventos de la escena Juego)
- **Un solo objeto `Sup`** con las 93 animaciones de los 8 personajes (`<personaje>_<animación>`, incluye `tonyfuerte`). Cada instancia tiene `Personaje`, `Jugador` (1-4) y `Control` (0 teclado y ratón, 1-4 control, -1 bot).
- **Controles:** extensión oficial *Gamepads 0.9.3* incrustada en el proyecto (no hace falta instalar nada).
  - Teclado: WASD moverse, clic izquierdo pegar, F usar/revivir (mantener), E Habilidad, C Especial, Q o clic derecho lanzar, Shift caminar despacio.
  - Control: stick izq. moverse, X pegar, A usar/revivir, Y Habilidad, RB Especial, B lanzar. Si alguien presiona A en un control libre, ese control reemplaza a un bot.
- **Bots:**
  - Siguen al jugador humano más cercano.
  - Pegan al zombie más cercano y usan habilidades cuando hay 3 o más zombies cerca.
  - Si se atascan, se teletransportan junto al grupo.
- **Cámara compartida:**
  - Se centra en el promedio de los humanos de pie y se aleja (zoom 1 a 0.6) si se separan.
  - Nadie puede salirse de la pantalla.
- **Revivir:**
  - Con 0 de vida, el jugador queda caído 25 s.
  - Un compañero de pie lo levanta manteniendo Usar 3 s junto a él; aunque ayuden varios, tarda lo mismo.
  - Vuelve con 50 % de vida.
  - Si nadie lo revive, queda fuera y reaparece al cumplir el siguiente objetivo.
  - Si no queda nadie de pie, es derrota.

### Pruebas
- Los 4 jugadores (Tony con teclado y 3 bots) caminan, pegan y se reviven entre ellos.
- La cámara se aleja cuando el grupo se separa.
- Capturas: `capturas\fase5_*`.

### Problemas y soluciones
- Las variables de texto de escena necesitan las acciones de texto (`ModVarSceneTxt`); las numéricas las dejaban vacías.
- `SceneInstancesCount` cuenta todas las instancias de la escena, no solo las elegidas; se cambió a `PickedInstancesCount`.
- Con varios ayudantes, el revivir era más rápido; ahora se usa una bandera `Ayuda`.

### Pendiente
- Probar con controles reales: no hay ninguno conectado en esta computadora.

## Fases 6 a 11 (5 nov 2026) — HECHAS, con pendientes anotados
Todo lo genera `gdevelop\scripts\fases_6_a_11.py`, que se corre **después** de `fase5_jugadores.py`. No editar eventos a mano: cambiar el script y volver a correrlo. Respaldo con fecha en `gdevelop\respaldos\` antes de cada cambio.

Escenas: **Titulo** (primera) → **Menu** → **Juego** → **Resultados**.

### Fase 6 · Zonas y objetivos
- **Niebla por zonas:**
  - Cada zona del JSON tiene su niebla.
  - Al abrir la puerta de una zona, su niebla se desvanece. Las zonas abiertas se guardan en `ZonasAbiertas`.
- **Tipos de puerta:**
  - Normal, electrónica y restringida. Toda puerta se puede tumbar a golpes (80, 100 y 150 de vida).
  - Con la tarjeta, las electrónicas se abren en 1 s.
  - Las restringidas se abren con la Llave maestra de Carlos o a golpes.
  - César (Hackeo) también abre la puerta cercana.
- **Objetivos:**
  - 3 objetivos al azar de 5 tipos: llamada desde el SITE/CIC, llaves de la conserjería, gasolina (3 bidones al camión), luz (3 interruptores durante un apagón) y carnada (comida a la nevería para distraer a la horda).
  - Hay 48 combinaciones; la luz nunca sale primera.
  - El texto de arriba dice qué hacer.
  - La **flecha amarilla** apunta al objetivo, bidón o bolsa más cercano y se oculta cuando el objetivo ya está en pantalla.
- **Final ¡Aguanten!:**
  - Al llegar alguien al camión del estacionamiento empieza una cuenta de 60 s.
  - Canepa repara el camión mientras llegan oleadas por los pasillos del estacionamiento (2 zombies cada 3 s, máximo 60).
  - Al terminar la cuenta aparece "¡ESCAPARON!" y luego Resultados.
- **Rescates:**
  - Joel y Justino tienen miedo y piden ayuda.
  - Para salvarlos hay que mantener Usar 2 s junto a ellos.
  - Costo: el tiempo, y que luego van lento detrás del grupo.
  - Recompensa: el equipo se cura 30 y cuentan en los premios.
  - A los profes no los muerden.
- **Horda de la explanada:**
  - 8 zombies dormidos alrededor de la fuente que despiertan a 150 px.
  - La carnada o el festín de Tony los manda a comer a la nevería.

### Fase 7 · Habilidades, especiales y pasivas (los 8)
- **Habilidad:** E o Y, recarga de 12 a 20 s.
- **Especial:** C o RB, recarga de 45 a 60 s.
- El HUD muestra la recarga.
- Los bots usan la Habilidad con 3 o más zombies cerca y el Especial con 5 o más.
- **Personajes:**
  - **Tony:**
    - Cocinar: deja 2 comidas. Cerca de la nevería es un festín que manda a los zombies a comer allá.
    - Modo gym (10 s): cambia a `tonyfuerte`, con fuerza ×2 y 40 % menos daño.
    - Pasiva: gana dinero para el equipo.
  - **Miranda:**
    - Arrullo: duerme a los zombies a 380 px por 6 s.
    - Minigun (8 s): golpes rápidos de largo alcance, pero camina más lento.
    - Pasiva: se cura poco a poco si no la golpean.
  - **César:**
    - Hackeo: abre la puerta cercana y hace la computadora del objetivo al doble.
    - Control de la escuela: descubre la zona donde está, empuja y aturde a los zombies a 650 px.
  - **Alan:**
    - Gorrear: aparece una regla y a veces comida.
    - Reembolso: escobas para todos los que pelean a puños.
  - **Castillo:**
    - Tragar: se come un zombie normal cercano y se cura 15.
    - App de salud: convierte hasta 4 zombies normales en "curados", que pelean de su lado 15 s.
  - **Alessandro:**
    - Chiste: los zombies a 320 px se ríen 4 s.
    - Reloj: congela a todos los zombies 4 s.
    - Pasiva: recargas 20 % más rápidas para quien esté cerca.
  - **Gabo:**
    - Supervelocidad (4 s): velocidad ×2 y avienta a los zombies que toca.
    - Ecosistema: 3 aparatos que distraen a los zombies 8 s.
  - **Carlos:**
    - Llave maestra: abre cualquier puerta cercana.
    - Tanque (8 s): 50 % menos daño para el equipo.
    - Pasiva: recibe 25 % menos daño.

### Fase 8 · HUD, menús, selección y Resultados
- **HUD:**
  - Un panel por jugador, en su esquina y con su color: nombre, vida, recargas y arma.
  - Abajo: barra de infestación, nivel, tiempo, dinero y tumbados.
  - Arriba: el objetivo. Banners grandes para los avisos.
  - Los textos centrados se centran solos, con el evento "Textos centrados".
- **Menú:**
  1. Modo (Escape o Jefe de zombies).
  2. Únanse: con A en un control libre.
  3. Equipo: A/D o ←/→ para cambiar, F o A para aceptar. Los bots se eligen solos sin repetir personaje.
  4. Dificultad (Fácil, Normal, Pesadilla): cambia la infestación, la vida y el daño de los zombies y el tamaño de las hordas.
- **Resultados:**
  - ¡ESCAPARON! o LOS ATRAPARON.
  - Tiempo, dificultad y tumbados por jugador (con cuántas veces cayó cada uno).
  - Profes rescatados y dinero de Tony.
  - Mejor tiempo (no cuenta si se usó el modo presentación).
  - Enter o A vuelve al título.
- **Título:** si nadie toca nada en 25 s, arranca una partida demo con bots.

### Fase 9 · Cinemática de inicio y modo Jefe
- **Cinemática de inicio (salón B-01):**
  - Relajo, alerta en el teléfono, atrancan la puerta, un zombie la rompe y P1 agarra la regla.
  - Luego aparece "clic para pegar".
  - Se salta con Esc o Start.
  - Completa solo la primera vez; después se salta sola.
- **Modo Jefe de zombies:**
  - El Jefe usa el ratón y los otros 3 juegan con control o como bots.
  - Minimapa abajo a la derecha. Cartas con las teclas 1 a 8: Zombie, Corredor, Gritón, Gordo, Horda chica, Trabar puerta, Apagón y Horda grande (esta desde la infestación 3).
  - Se hace clic en el minimapa para usar la carta.
  - No se pueden poner zombies donde los ven los sobrevivientes, salvo en las rejillas.
  - Gana 1 de oro cada 5 s, y el doble durante el ¡Aguanten!.

### Fase 10 · Ambiente y sonido
- **Luz:**
  - Capa de luz nocturna (120;125;165) y luces que parpadean al azar.
  - Apagón con el objetivo de luz y con la carta del Jefe.
- **Destrozos:** 40 marcadores `destrozo` donde irán los sprites de destrozo, que todavía no existen.
- **Sonido:** todos los eventos de sonido y música están puestos, pero detrás de la variable global `SonidoActivo` = 0 porque los audios aún no existen. Los nombres de archivo esperados están en el grupo "Música y sonido de fondo".

### Fase 11 · Modo presentación (F1)
- **Menú oculto:**
  1. Completar objetivo.
  2. Saltar al final: lleva al equipo al camión.
  3. Vida infinita.
  4. Subir infestación.
  5. Bajar infestación.
  6. Reiniciar.
- Si se usa, la partida no cuenta para el récord.
- **F3** muestra u oculta el texto amarillo de depuración. Ahora empieza oculto para no taparse con el panel de P1.

### Pruebas (vista previa)
- **Cinemática:** completa. Saltar con Esc funciona.
- **HUD de 4 jugadores:**
  - El objetivo y la flecha funcionan.
  - El tiempo corre.
  - La niebla se quita al abrir.
- **F1:**
  - Opción 1: completar objetivo → NUEVO OBJETIVO.
  - Opción 2: saltar al final → el equipo aparece en el camión → ¡AGUANTEN! con cuenta de 60 s → ¡ESCAPARON! → Resultados con premios → Enter → Título.
- **Menú completo:** modo, únanse, equipo (P1 cambiado a Miranda) y Pesadilla. La partida arranca con el equipo elegido.
- **Habilidades de Tony:** E deja la comida y C activa el Modo gym (`tonyfuerte`).
- **Modo Jefe:**
  - Arranca sin P4 y con el minimapa.
  - El oro sube.
  - Un clic en el minimapa compra un zombie y descuenta el oro.
- Capturas: `capturas\fase6_*` a `capturas\fase10_*`.

### Problemas encontrados y soluciones
- **`%` no existe en las expresiones de GDevelop:** el tiempo se quedaba en 0:0, Resultados salía sin detalles y el menú de equipo no giraba. Se cambió a `mod(a, b)`.
- **Temporizadores que nunca arrancan:** un temporizador que nunca se inició no cuenta en GDevelop, y las oleadas del final, el oro del Jefe y el parpadeo no arrancaban. Ahora todos se inician al empezar la escena.
- **Teletransporte al camión deshecho:** la cámara "regresaba" a los jugadores al encuadre anterior. Ahora la cámara también se mueve.
- **Personaje elegido con estadísticas de otro:** salía con la vida de Tony (120). El grupo de configuración ahora va primero.
- **Textos centrados corridos a la derecha:** GDevelop centra las líneas dentro del bloque, no en la X de la instancia. Se arreglaron con el evento "Textos centrados".
- **La configuración pisaba el estado de la cinemática:** quitado.
- **Crédito de los tumbados:** ahora se cuentan cuando el zombie pasa a "muerto", con la bandera `Contado`.
- **Sin expresiones ternarias ni `and`:** todo se resolvió con eventos.

### Pendiente (para el equipo)
- **Audios:** cuando existan en `fdiz\sonido` y `fdiz\musica` con los nombres del grupo de música, poner `SonidoActivo` = 1.
- **Sprites que faltan:**
  - Destrozos.
  - Profe Canto (no sale en la cinemática).
  - `cic__mostrador_curvo_h180.png`: hoy hay un rectángulo magenta en su lugar.
- **Planta 1 del edificio B:** la cinemática usa el salón de planta baja en la misma posición.
- **"Salvar o no salvar" a compañeros mordidos:** falta la mecánica de mordida. Hoy solo caen y se reviven.
- **Detalles de habilidades:**
  - El pase por Rutas de César.
  - El "Ojo de oferta" de Alan.
  - El AirDrop de Gabo.
  - El resto funciona.
- **Pruebas que faltan:**
  - Controles reales: no hay uno conectado.
  - Una partida completa de 8 a 12 minutos sin F1.
  - Rendimiento con 40 o más zombies en la laptop de la presentación.
  - Balance de daño y velocidad.
- **Pulido visual:** en el minimapa del Jefe no se dibuja la zona roja; solo se avisa "Zona prohibida".
- **Antes de presentar:**
  - Correr `scripts\empaquetar_recursos.py`, que copia los sprites al proyecto.
  - Borrar o desactivar el grupo "Depuración".

## Fase 12 · Mejoras y bugs (6 nov 2026)
Script nuevo `gdevelop\scripts\fase12_mejoras.py`, que se corre **después** de `fases_6_a_11.py`. También cambiaron `fase5_jugadores.py` y `fases_6_a_11.py`. Hay un respaldo en `respaldos\FDI-Z_respaldo_20261106_0054.json`.

### Bugs corregidos
- **El zombie de la cinemática aparecía dentro del salón:**
  - Ahora 2 zombies llegan por el pasillo y golpean la puerta del salón B-01 (P06, pared oeste), que se pone roja.
  - A los 19 s la tumban y entran.
- **Los zombies se quedaban atorados en las puertas cerradas:** si no tienen ruta, le pegan a la puerta más cercana hasta tumbarla.
- **Al saltar la cinemática, P1 se quedaba a puños:** ahora recibe la regla.
- **Modo gym:** Tony ya no puede ser tumbado.
- **Textos durante la cinemática:** el objetivo y la flecha ya no salen.
- **Informe de diagnóstico de GDevelop:**
  - Marcaba "Cambiar opacidad" en un objeto de texto (`TxtDanio`); se quitó.
  - El resto de lo que marca son los sonidos que todavía no existen. Es normal y se quita solo cuando estén los audios.

### Nuevo
- **Lanzables:**
  - Balón: empuja lejos y se vuelve a recoger.
  - Engrapadora: 8 grapas.
  - Libro gordo: aturde 1 s y se vuelve a recoger.
  - Se recogen pasando encima y se lanzan con Q o clic derecho (B en el control). Los bots también lanzan.
  - Hay 16 en el mapa: libros en pupitres, engrapadoras en escritorios y balones en las canchas.
- **Lockers y mochilas (16):**
  - Se revisan manteniendo Usar 1 s.
  - Sueltan monedas de $10–30, galletas (cura 30), jugo (cura 22) o un libro.
- **Máquinas expendedoras (4, en los refris de refresco):** compran con el dinero del equipo.
  - Comida: $40.
  - Lanzable: $60.
  - Arma básica: $80.
  - Arma rara (bate o extintor): $200.
  - El precio sale arriba de cada máquina.
- **Dinero:** cada zombie tumbado da $2 (además de la pasiva de Tony).
- **Comida guardada:**
  - Con la vida llena, guardas 1 comida y se come sola bajo 30 %.
  - El panel muestra el lanzable, la comida guardada y si estás mordido.
- **Compañeros mordidos (salvar o no salvar):**
  - Cada golpe de zombie tiene 12 % de morder.
  - El mordido tiene 35 s y lleva un letrero con la cuenta.
  - Un compañero lo cura manteniendo Usar 3 s junto a él. Le cuesta su comida guardada o, si no tiene, 20 de vida.
  - Si nadie lo cura, se convierte en zombie y queda fuera hasta el siguiente objetivo.
  - Los bots van a curar.
- **Sensación:** números de daño que suben, y temblor de cámara al pegar.
- **Efectos de habilidad:** los 16 sprites de `generado\sprites\efectos` salen sobre el personaje al usar la Habilidad o el Especial.
- **Pasivas que faltaban:**
  - Alan, Ojo de oferta: cada 30 s ve 6 s dentro de las zonas oscuras cercanas.
  - César, Rutas: cada 25 s, una línea punteada hacia el objetivo durante 10 s.
  - Gabo, AirDrop: si pisa un arma que ya trae, se la manda al compañero más cercano que pelea a puños.
- **Director automático (Escape):**
  - Ciclo de 60 s: calma 18 s, crecimiento y pico (15 s con más zombies).
  - Afloja si alguien está caído o mordido, o con poca vida.
  - No toca el final ni el modo Jefe.
- **Modo Jefe:** la zona roja (lo que ven los sobrevivientes) se dibuja en el minimapa.
- **F1 nuevo:**
  - 7: morder a P1.
  - 8: dar $200.
  - 9: engrapadora para P1.

### Pruebas (vista previa)
- **Cinemática:** los zombies golpean la puerta, la tumban y entran.
- **Combate:** se ven los números de daño.
- **Mochila:** al revisarla soltó un libro; P1 lo recogió y lo lanzó.
- **Mordido:** con F1 + 7, el bot Miranda fue a curar a P1. Se vio "Curando a P1… 84 %", luego "SALVADO" y quitó el tinte verde.
- **Lanzables:** F1 + 9 da la engrapadora y el panel muestra "engrapadora x7" después de lanzar.
- **Modo Jefe:** se ve la zona roja.
- Capturas: `capturas\fase12_*`.

### Segunda ronda (6 nov 2026, madrugada)
- **Bots sin humanos (demo del título o Jefe sin controles):**
  - Ahora siguen a un **guía invisible** con Pathfinding que va al objetivo.
  - Llega a un punto de acceso libre junto a cada lugar de objetivo, calculado por el script desde las colisiones y los muebles.
  - Espera a que lo alcancen y regresa por el bot que se atora en una esquina.
  - Los rezagados a más de 450 px aparecen junto a él.
  - Los bots mantienen Usar junto a objetivos y puertas (y le pegan a las que no abren), y recogen bidones y bolsas cercanos.
  - En la demo, si un objetivo tarda más de 80 s se da por cumplido, y a los 4 min vuelve al título.
  - Sale el letrero "DEMOSTRACIÓN · presiona Enter…".
- **Puertas:**
  - Las puertas cerradas ya no bloquean el Pathfinding.
  - Los zombies planean a través de ellas y, al llegar, les pegan hasta tumbarlas.
  - Los jugadores siguen chocando con ellas.
- **Máquinas expendedoras:**
  - Probado: con $215 se compró comida y un balón.
  - Bug corregido: se compraba en las 2 máquinas de al lado a la vez; ahora una compra por vez y dice "Comprando… (hay $N)".
  - Precio en 2 renglones, centrado.
- **Pasivas:** sus avisos (Rutas, Ojo de oferta, AirDrop) ya no usan el letrero grande rojo; salen en la línea de ayuda.
- **Objetivos:** se pueden usar desde 140 px (antes 110). Algunos estaban pegados a muebles.
- **Depuración (con F3 visible):**
  - B convierte a P1 en bot.
  - T lleva a P1 a la siguiente máquina expendedora.
  - Se ve el guía y una línea con el objetivo, su posición y el estado del guía.

### Pruebas de la segunda ronda
- **Partidas solo con bots y vida infinita:**
  - Cumplieron la carnada sin ayuda.
  - Subieron interruptores.
  - En la demo juntaron un bidón y curaron a un mordido ("¡P1 SALVADO!"); con el salto de 80 s, la demo pasó al objetivo 2.
- **Lanzables:** balón comprado, recogido y lanzado.
- Capturas: `capturas\fase12_demo_*` y `fase12_maquina_compra.jpg`.

### Pendiente
- **Bots solos:** avanzan, pero lento, y a veces se atoran en salones con muchos muebles. Por eso la demo salta objetivos tardados. Con jugadores humanos los bots los siguen como siempre.
- **Lo que no se hizo de las notas:**
  - Ruido al correr y pelear.
  - Doble daño a los zombies dormidos (Miranda).
  - Premios MVP, Gamer, Hacker, etc., con sus conteos propios.
  - El personaje Criollo (no tiene sprites).
- **Sigue pendiente lo de las fases 6-11:** audios, destrozos, Canto, planta 1 de B, controles reales, partida completa de 8 a 12 min y rendimiento.

## Cambio de controles (11 nov 2026)
- **Teclado nuevo:** Habilidad = **Q**, Especial = **E**, Lanzar = **R** o clic derecho (antes: E, C y Q).
- **Por qué respondían raro:** Habilidad, Especial y Lanzar se disparaban al *soltar* la tecla (`KeyReleased`), así que parecía que había retraso o que no pasaba nada. Ahora se disparan al *presionar*, también en el control de Xbox (Y, RB y B). La recarga evita que se repitan.
- Cambiado en `fase5_jugadores.py`, `fase12_mejoras.py` y `fases_6_a_11.py` (incluido el texto de ayuda en pantalla). Respaldo previo: `respaldos\FDI-Z_respaldo_antes_de_controles_20261111.json`.
- Probado en la vista previa: Q activa la Habilidad.

## Oscuridad inicial y botón de omitir (11 nov 2026)
- **Oscuridad:** antes solo los salones tenían niebla (12 % del mapa); pasillos, patios y estacionamiento siempre se veían con la luz de noche. Ahora 4 rectángulos negros (`OscuridadIni`, capa Niebla) tapan todo el mapa menos el salón donde arranca el equipo: **B-01** en la cinemática (primera partida) y **E-04** cuando ya se vio. Se desvanece en ~1 s cuando alguien sale del salón (más de 80 px fuera de la zona).
- **Botón OMITIR:** abajo a la derecha durante la cinemática (`BtnOmitir` + `TxtOmitir`, capa HUD). Se omite con clic en el botón, Esc, Enter o Start de cualquier control.
- Cambios en `fase12_mejoras.py` (grupo "Oscuridad inicial y botón omitir") y `fases_6_a_11.py` (Enter y Start 3-4 saltan la cinemática). Respaldo previo: `respaldos\FDI-Z_respaldo_antes_de_oscuridad_20261111.json`.
- **Probado en la vista previa (11 nov):** la cinemática arranca con todo el mapa negro menos B-01; el clic en OMITIR salta a la partida; Q activa la Habilidad (recarga de 17 s). El botón ahora es rojo semitransparente (antes era negro y no se veía sobre la oscuridad). Pendiente: probar E y R con una pulsación real (las pulsaciones automáticas muy cortas no las detecta el juego) y suavizar el borde de la luz si se quiere.

## Colisión entre personajes y zombies que atravesaban paredes (11 nov 2026)
- **Personajes:** los supervivientes de pie (jugadores y bots) ahora se empujan entre sí (`SeparateFromObjects` Sup contra Sup, antes de la separación contra muros). Los caídos no estorban, para poder revivirlos. La caja de choque de los personajes pasó de 28 a 40 px de ancho, porque el dibujo es más ancho que la caja y se veían traslapados.
- **Zombies:** antes golpeaban a cualquiera a menos de 80 px, aunque hubiera una pared en medio. Ahora, antes de pegar, revisan 7 puntos sobre la línea entre el zombie y el superviviente (condición `CollisionPoint`, "punto dentro del objeto"); si alguno cae dentro de un `Muro` o una `Puerta` cerrada, no hay golpe. Variable de escena `Bloq`.
- Cambios en `fase5_jugadores.py` y `fase12_mejoras.py`. Respaldos en `respaldos\`.
- **Probado:** los bots se ven separados y sin encimarse en la vista previa; el evento del zombie se lee bien en el editor (sin errores). **Sin probar en juego real:** que un zombie junto a una pared ya no golpee al otro lado.
- Pendiente parecido: los golpes del jugador (arco de `Golpe`) y el empujón del Gordo/Conserje tampoco revisan paredes.

## Bots y golpes no atraviesan paredes (11 nov)
- Los golpes del jugador y de los bots contra zombis ahora comprueban linea de vision (7 puntos CollisionPoint contra Muro/Puerta, variable Bloq). Los bots tampoco avanzan para pegar si hay pared de por medio.
- Probado en vista previa: el combate normal sigue funcionando. No probado a mano: bloqueo real contra una pared concreta. Gordo/Conserje (empuje) aun no comprueban paredes.
- Empuje del Gordo y del Conserje: ahora tambien comprueba linea de vision (no empujan a traves de paredes). Regenerado, no probado en juego.
- Quitado el parpadeo de la luz ambiente (cambiaba 120 a 60 al azar cada 0.08-3 s y se veia como parpadeo de toda la pantalla). Ahora la luz nocturna es fija. Respaldo: antes_de_parpadeo.
- Camara mas cerca: zoom de 0.6-1 a 0.7-1.4 (x1.4). Si se separan mucho, se aleja hasta 0.7. Respaldo: antes_de_zoom.
- Bots sin teletransporte: ahora siguen al grupo por ruta (comportamiento PathBot en Sup, ruta cada 0.2 s, rodea paredes y muebles). Quitados los saltos "aparecen junto al jugador" (>1100 px, atascados >250 px y rezagados >450 px del guia). Probado: abre sin errores; pruebas cortas sin saltos. Falta probar distancias largas y puertas. Respaldo: antes_de_teletransporte.

## Pendientes planeados (anotados el 11 nov, no urgentes)
Arte y pantallas (se pueden generar con WaveSpeed vía API; primero mockup y luego se arma en GDevelop con imágenes):
1. Pantalla de inicio / título bonita (hoy no hay).
2. Pantalla de modos de juego (va ANTES de la selección de personaje).
3. Pantalla de selección de personaje: muestra los personajes, sus habilidades y permite escoger.
4. Pantalla de dinero recolectado y tienda: gastar el dinero en artículos (definir qué artículos habrá).
5. Corregir animaciones de caminar de lado de algunos personajes (las piernas se ven mal; WaveSpeed las generó mal).
6. Animaciones en pantalla cuando un personaje usa una habilidad.
7. Iconos de habilidades para que el menú/HUD no se vea feo.
8. Poner la fuente descargada en todo el juego (hoy usa la fuente por defecto).
Pendientes anteriores que siguen abiertos: audio, sprites faltantes, planta 1 B, prueba con controles, partida completa de principio a fin, rendimiento, y empuje del Gordo/Conserje y bots en puertas/distancias largas (probar).

## Interfaz con las piezas de arte (2026-11-11)
- Orden de scripts: fase5 -> fases_6_a_11 -> fase12 -> preparar_interfaz -> fase13_interfaz -> fase14_pantallas (GDevelop cerrado / recargar sin guardar). Respaldos: respaldos/antes_de_interfaz_*, antes_de_pantallas_*.
- fase13: HUD con paneles por jugador, banner de objetivo (2 líneas), infestación, dinero. Resolución fija 1920x1080 (adaptGameResolutionAtRuntime=False) para que no se corten los paneles de la derecha.
- fase14: Título (bg_titulo, logo, cartel), Menú (modo con 2 tarjetas, unirse y personaje con 4 cartas + iconos Q/E/pasiva, dificultad con 3 botones), Resultados (fondo/banner victoria o derrota + panel). La lógica de teclado/control no cambió. Los marcos de 9 cortes se arman como PNG exacto (assets/interfaz/hud/p9_*.png) porque PanelSprite salía magenta en la vista previa.
- Pendiente de interfaz: pausa (no existía), tienda como pantalla (hoy son máquinas expendedoras con cartel de precio), cartas/minimapa del modo jefe, flecha nueva, fuente, textos de opacidad de TxtDif.
- fase15_seleccion.py (corre después de fase14): la pantalla "ELIGEN SU PERSONAJE" ahora sigue el mockup `generado/interfaz/mockups/seleccion.png`: personaje grande de cuerpo completo con foco y placa, cuadrícula de 8 retratos, panel con las 3 habilidades, 4 barras de jugador. Clic en un retrato = elegir (primero P1, luego los bots en orden); clic derecho = quitar; W/S o arriba/abajo cambian de fila; A/D, F, pads y Enter siguen como antes. El marco de cada retrato toma el color del jugador (amarillo, azul, verde, rosa).

## Videos en escenas, navegación A*, puertas (12 nov 2026)
- **Videos:** `scripts/fase16_videos.py` integra 15 videos (el 14, fondo de tienda, queda sin usar porque aún no hay pantalla de tienda). Un objeto `Video::VideoObject` por video; solo el que toca se muestra y se reproduce. El renderer del video ignora `Montre/Cache` y `Opacity` no es válida para este objeto, así que se oculta moviéndolo fuera de pantalla (`MettreX` = -6000) y pausándolo. Las acciones correctas son `Video::Play` y `Video::Pause`. Los videos 02-03 y 04-11 se recortaron con ffmpeg (`*_recorte.mp4`) para encajar en su marco sin deformarse. Volumen 35 % personajes y 10 % el resto, en bucle. Los sprites originales solo se ocultan.
- **Navegación:** `scripts/fase17_navegacion.py` inserta como primer evento de Juego un evento JavaScript con `scripts/nav_astar.js`: A* propio sobre rejilla de 16 px con holgura de 18 px, heap binario, 8 vecinos sin cortar esquinas, suavizado por línea de vista, caché por celda destino, presupuesto de expansiones por cuadro y ruta parcial si no hay camino. Sustituye `moveTo` y `doStepPreEvents` del behavior Pathfinding, así que zombis, bots y guía lo usan sin cambiar sus eventos. Las puertas cerradas cuestan más pero se pueden cruzar.
- **Causas encontradas:** (1) el temporizador `ruta` de los bots nunca se iniciaba (`NaN >= 0.2` es falso), así que no pedían ruta jamás; (2) con `maxSpeed 0` el behavior devolvía al bot al inicio de su ruta en cada cuadro; (3) el buscador original inflaba los obstáculos con el sprite completo (80x127) y no hallaba ruta en pasillos angostos; los zombis sin ruta eran empujados contra la pared (evento desactivado).
- **Puertas:** se restauró la lógica original (Usar junto a la puerta, golpes, zombis, tarjeta) y el descubrimiento de zonas (`ZonasAbiertas`), que dejó de funcionar al quitarla; sin eso las zonas se quedaban negras. R en teclado sigue abriendo. La distancia ahora se mide desde los pies (130 px), porque `Distance()` usa el centro del sprite, ~62 px más arriba. Los bots abren las puertas que cruza su ruta aunque haya humanos.
- **Probado en Chromium sin pantalla:** los bots salen del salón inicial, abren la puerta, llegan al jugador y matan zombis; el jugador abre la puerta de E-04 con F y se descubre la zona; menú de modos, selección de personaje y dificultad se ven bien con sus videos. No probado con control de Xbox ni una partida completa.
- **Fase 18 (correcciones, 2026-11-13):** `scripts/fase18_correcciones.py` parchea el JSON en sitio (idempotente; no regenerar con la cadena de fases, el JSON tiene ediciones manuales de GDevelop). (1) Se quitó la colisión Sup–Sup: los bots ya no empujan al jugador; entre bots y entre zombis sí hay separación (evento etiquetado `fdiz18`). (2) Golpe: el objeto `Golpe` queda como hitbox invisible y un nuevo `GolpeFx` se coloca en el puño según la dirección (der/izq/arr/aba) con rotación y escala por alcance. (3) Selector de personajes: marco amarillo `p9_EqMarcoVideo.png` sobre los videos. (4) Bugs de IA: los bots se detienen a distancias distintas del guía (90+45*Jugador) para no apilarse; los zombis quietos pausan la animación y miran al objetivo en vez de caminar en su lugar. `scripts/depuracion_ia.py` es un logger temporal (off por defecto). Pendiente: probar a fondo el golpe hacia la izquierda; zombis sin animación `atacar_arriba`; rectángulos grises tras los textos de dificultad.

## Fase 19 (13 nov 2026): correcciones pedidas por Tony
Todo se aplica en sitio sobre `FDI-Z.json` con `scripts/fase19_correcciones.py` (idempotente) y `scripts/fase19_botones.py` (imágenes de botones). No regenerar con la cadena de fases: el JSON tiene ediciones manuales de GDevelop. Probado en vista previa de GDevelop (no con control de Xbox).

- **Botones de dificultad (Menú):** la placa gris estaba horneada en las imágenes `ui_boton_*.png`, no era un objeto. Se generaron `ui_boton_facil_p19.png`, `ui_boton_normal_dificultad_p19.png` y `ui_boton_dificil_p19.png` sin placa y con el mismo tamaño (480x168, instancias alineadas en x=720). El texto `TxtDif` ahora es crema con borde oscuro para leerse sobre botones azules y naranja.
- **Zombis, `atacar_arriba`:** no existía el arte. Se generó con los cuadros de `caminar_arriba` desplazados hacia arriba (embestida) para los 5 tipos (carpetas `generado/sprites/zombies/<tipo>/atacar_arriba/`).
- **Efecto de golpe:** estaba girado 180° (el arco "C" quedaba con la curva hacia el personaje). Se invirtieron los 4 ángulos (der 0, izq 180, arriba 270, abajo 90). Sigue pegado al puño. La dirección izquierda y arriba no se vieron en la prueba (el efecto dura 0.22 s).
- **Zombis que no desaparecían:** causa real: la pausa de animación de la fase 18 dejaba en pausa la animación `golpe_morir`, y el evento que borra al zombi espera que termine. Ahora al morir se reanuda la animación y, por seguridad, se borran 1.2 s después (variable `MuerteIni`, temporizador `muerte`). Los 5 tipos tienen `golpe_morir`; no faltaba ninguna animación de muerte.
- **Tony en modo Gym:** los cuadros `tonyfuerte` tenían el cuerpo ~9 % más chico que Tony (el resto del cuadro eran las llamas). Se escalaron x1.09 (`generado/sprites/personajes_p19/tonyfuerte/`, origen 46,107) y se añadieron las animaciones que faltaban (pegar arriba/abajo, caer, festejo, habilidad, especial) copiándolas de Tony. Comprobado en vista previa.
- **Rutas de César:** ya no es una línea recta de 11 puntos. Un evento JS (marca `FDIZ19-RUTA`, dentro de "Pasivas: Ojo de oferta, Rutas y AirDrop") calcula el camino con el A* del juego (`gdjs.fdizNav.path`), que evita muros, muebles y salones; se recalcula cada 0.6 s durante 14 s para seguir a César. Los puntos son más grandes con borde oscuro y se dibujan en la capa `Niebla` con z alto, así se ven también dentro de las zonas negras. Comprobado: sale por la puerta del salón.
- **Pantalla de derrota:** botones REINICIAR (naranja) y MENÚ (verde). Reiniciar (clic, R, Enter, Espacio o A/Start de control) vuelve a `Juego` con los mismos personajes y controles (variables globales `P1Pj..P4Ctl`); MENÚ (clic, Esc o M) va al título. En victoria sigue igual (cualquier tecla: título).
- **Derrota inmediata:** si hay un solo humano (con 3 bots) y no está de pie, pasa directo a Game Over (variable de escena `HumTot`, eventos al final de "Cámara compartida"). Comprobado con una tecla de prueba temporal, ya retirada.
- **Limpieza:** el registrador de depuración de IA quedó apagado (`depuracion_ia.py off`).
- **Pendiente anotado:** los botones REINICIAR/MENÚ tapan un poco la ilustración de derrota (esquina inferior izquierda); el borde brillante del botón NORMAL seleccionado se ve ~4 % más grande por el brillo.

## Fase 19b y 20 (13 nov 2026): segunda ronda de correcciones
Scripts: `scripts/fase19_correcciones.py` (actualizado) y `scripts/fase20_pausa.py` (nuevo), ambos idempotentes y aplicados en sitio.
- **Tony Gym al caminar:** el escalado único x1.09 no servía: cada animación de `tonyfuerte` tenía el cuerpo de distinto tamaño (las llamas cambian el cuadro). Ahora cada animación se escala para que el cuerpo (pelo a zapatos, medido por píxeles oscuros) mida lo mismo que el de Tony normal: quieto x1.089, caminar abajo x1.011, caminar arriba x1.116, caminar lado x1.116, pegar x1.066 (carpeta `generado/sprites/personajes_p19/`).
- **Zombis "flotando":** causa: la pausa de animación de la fase 18 usaba `Pathfinding::Speed()`, que vale 0 cuando el zombi avanza por fuerzas (`AddForceVersPos`), así que la animación de caminar quedaba pausada mientras se movía. Ahora se mide el desplazamiento real por cuadro (variable `Mov`, promedio móvil; pausa si Mov <= 0.3).
- **Rutas de César:** puntos 30 % más pequeños (0.4 y 0.56 de escala) y opacidad con parpadeo `110 + 68*sin(5t)` (máximo 178 de 255, un 30 % menos que antes). Se sigue recalculando al caminar.
- **Menú de pausa (nuevo grupo "Menú de pausa" en Juego):** Esc o P pausa y reanuda (solo con Estado = "juego"). Congela todo con `ChangeTimeScale 0` y muestra un velo gris semitransparente (opacidad 150) con panel y botones CONTINUAR, REINICIAR y MENÚ (W/S o flechas + Enter/Espacio, o clic). 12 grupos de entrada (pegar, habilidades, lanzar, usar, etc.) quedaron envueltos en la condición `Pausa = 0` para no actuar en pausa. Comprobado en vista previa: pausa, selección con teclado y reanudar. No probados REINICIAR/MENÚ desde la pausa ni el uso con control de Xbox (no hay botón de pausa en el control: START ya sirve para unirse).

## Fase 21 (13 nov 2026): audio estilo SNES (efectos + música)
Scripts: `scripts/snes_synth.py` (motor: pulso, triángulo, ruido, cuantización 8 bits, filtro gaussiano y eco, 32 kHz nativo como el DSP de la SNES), `scripts/fase21_audio.py` (genera los 44 sonidos; `--solo ID` rehace uno) y `scripts/fase21_proyecto.py` (idempotente: aplica al proyecto). Respaldo: `respaldos/antes_de_fase21_20261113.json`.
- **Sonidos creados (una sola versión de cada uno):** 21 efectos de combate/eventos/mundo/interfaz, 16 de habilidades y 7 músicas, todos en `.ogg` Vorbis 44.1 kHz mono dentro de `FDI-Z/efectos/<categoría>/` y `FDI-Z/musica/`. La validación `validar_audio.py --check` pasa (44 revisados, 0 problemas). No hizo falta WAV: ffmpeg tiene libvorbis.
- **Temas:** habilidad de Miranda = mini nana; especial de Miranda = minigun; Alessandro = "ba-dum-tss" de tambores (chiste) y tic-tac de tiempo; Alan = caja registradora y lluvia de monedas; Castillo = trago y poción; César = hackeo y alarma; Gabo = velocidad y estampido; Carlos = llaves y armadura; Tony = sartén y banquete.
- **Música:** menu, partida_1/2/3 y final_aguanten van en bucle sin corte (eco circular); victoria y derrota no repiten.
- **`puerta_abrir.ogg`:** los eventos ya lo usaban pero no estaba en el manifiesto; se añadió (`SFX_MUNDO_PUERTA_ABRIR`).
- **Recursos y volúmenes:** los 44 audios se registraron como recursos de audio del proyecto y se cambió el volumen de las 56 acciones PlaySound/PlayMusic. Todos < 100 (efectos 55-75, música 45-50; antes había efectos en 100).
- **Videos:** volumen de fondos 10 → 3 % y de los videos de personajes del selector 35 → 12 %, para que no tapen la música ni los efectos.
- **Catálogo:** `FDI-Z/efectos/CATALOGO_SONIDOS.md` (copia en `musica/`) con ID, cuándo suena, descripción, duración y volumen de cada sonido, para indicar cuáles rehacer.
- **Sin probar en vista previa:** el audio se validó por formato y volumen; falta que Tony lo escuche en el juego.

### Fase 21b (13 nov 2026): audio activado en el juego
- **Causa de que no sonara nada:** la variable global `SonidoActivo` seguía en 0 desde la fase 10 (se dejó apagada porque no había audios) y todos los eventos de sonido y música exigen `SonidoActivo = 1`.
- **Arreglo:** `scripts/fase21b_activar_sonido.py` (idempotente) la pone en 1. Comprobado que los 44 audios registrados están usados por algún evento (ninguno huérfano).
- **Segunda causa (fase 21c):** aun con `SonidoActivo = 1` no sonaba nada. La consola de la vista previa daba `No codec support for selected audio sources` en todos los audios: los parámetros de archivo de PlaySound/PlayMusic son de tipo `soundfile` (nombre de recurso **sin comillas**) y los eventos los tenían entre comillas (`"musica/menu.ogg"`), así que GDevelop pedía un archivo cuyo nombre terminaba en `.ogg"`. `scripts/fase21c_rutas_audio.py` (idempotente) quitó las comillas de las 56 acciones. Tras recargar, la consola ya no muestra errores de audio.


## Fase 22 · Modo Jefe de zombies funcional (2026-11-13)

Respaldo: `respaldos/antes_de_fase22_20261113.json`. Script idempotente: `scripts/fase22_jefe.py` (lee `scripts/jefe_modo.js` y `scripts/bots_habilidades.js` y los incrusta en la escena Juego). Iconos: `scripts/fase22_iconos_jefe.py` → `assets/interfaz/jefe_icono_c1..c8.png`.

**Qué cambió**
- El grupo "Modo Jefe de zombies" se reescribió: toda la lógica e interfaz del Jefe está en un evento JavaScript (`jefe_modo.js`). Se eliminaron las condiciones/acciones antiguas (texto plano en `TxtJefe`, minimapa-solo-clic, etc.).
- El Jefe juega solo con teclado y ratón: WASD/flechas mueven la cámara libre (Shift más rápido, Espacio = ir al grupo), clic en el minimapa mueve la cámara, teclas 1-8 o clic eligen carta, clic en el mapa invoca, clic derecho cancela la carta, H muestra/oculta la ayuda.
- Interfaz nueva: panel "MISIÓN DEL JEFE", ayuda inicial de 3 pasos, 8 cartas con icono, coste, recarga (velo con barra) y bloqueo por oro/nivel, cuadro explicativo de la carta elegida, minimapa con puntos (sobrevivientes por color, zombis, objetivo, ventana de cámara, zona visible), barra del próximo oro, mensajes de error junto al cursor y cursor verde/rojo según si se puede invocar.
- Regla de invocación: no se puede invocar dentro del círculo rojo (lo que ven los sobrevivientes) ni sobre paredes/muebles (rejilla de navegación).
- Modo Jefe ahora usa los 4 sobrevivientes como bots (Control -1; ya no se borra al P4); sin cinemática ni oscuridad inicial, sin niebla de zonas, sin aparición automática de zombis (solo los que invoca el Jefe).
- Cámara compartida desactivada con `Jefe=1`; `ZonaRoja` antigua oculta; el HUD de dinero muestra el oro del Jefe.
- Fin de partida: si los 4 sobrevivientes caen → "¡GANÓ EL JEFE!"; si cumplen el objetivo → "¡ESCAPARON! EL JEFE PERDIÓ" (textos en Resultados).
- Bots (todos los modos): `bots_habilidades.js` se ejecuta antes del grupo de habilidades y decide Q/E según el personaje (zombis cerca, gordos, vida baja, aliados heridos; Castillo cura, Carlos/Alessandro/Gabo se defienden, Miranda/César/Alan atacan en área).
- Bug corregido durante las pruebas: `setCoordinatesAbsolute` no existe en esta versión del Drawer (se usa la propiedad del objeto).


## Fase 22b · Corrección de bots y música (2026-11-13)

- **Bots atorados (causa):** en modo Jefe bloqueé todo el evento "CamN > 0" de la cámara compartida, y ese mismo evento calcula `CamX/CamY` (promedio de los bots). Sin dividir, `CamX/CamY` quedaban enormes y la guía invisible de los bots se teletransportaba fuera del mapa, así que nadie avanzaba. Ahora el evento corre siempre y solo se bloquea el movimiento de cámara (sub-eventos con `Jefe=0`). Probado: los bots completan objetivos (1/3 → 2/3 …) en el modo Jefe.
- **Música superpuesta:** todas las acciones `PlayMusic` (Título, Juego: partida_1/2/3 y final, Resultados: derrota/victoria) pasaron a `PlayMusicCanal` en el canal 1. Al arrancar una pista en ese canal reemplaza a la anterior, incluso al cambiar de escena. (Hecho dentro de `fase22_jefe.py`, idempotente.)
- Apagón del Jefe: se deja para después (la carta sigue en el juego, sin tocar).
- El Jefe actúa al soltar clic/tecla (`isMouseButtonReleased` / `wasKeyReleased`) para no perder pulsaciones cortas.


## Fase 24 · Multijugador local (fase A del multijugador) (2026-11-13)

Respaldo: `respaldos/antes_de_fase24_20261113.json`. Script idempotente: `scripts/fase24_local.py` (corre después de `fase22_jefe.py`).

- **Pantalla Únanse:** cada hueco muestra un icono en vez de letras: teclado + ratón, mando, o mando con "+" (libre: presiona A en un mando; si nadie entra, ese hueco será bot). Iconos nuevos `assets/interfaz/slot_ico_*.png` (objeto `SlotIco`). Texto específico para el modo Jefe.
- **Límite por máquina:** 4 personas como máximo. En Escape: teclado + 3 mandos. En Jefe: el Jefe usa teclado y ratón y solo se aceptan 3 mandos de sobrevivientes. Los huecos que nadie ocupa se rellenan con bots (ya existía).
- **Mandos (auditoría y arreglos):** movimiento, atacar (X), usar (A), habilidad (Y) y especial (RB) ya estaban para los 4 mandos. Nuevo: apuntar con la palanca derecha; **pausa con mando** (Start pausa, cruceta arriba/abajo elige, A acepta; antes no se podía pausar con mando). El menú de Título/Únanse/Equipo/Dificultad ya funcionaba con mando.
- **Modo Jefe con mandos:** ya no se fuerzan los 4 sobrevivientes a bot; los huecos con mando son humanos. Los humanos no pueden salir de lo que ve la pantalla del Jefe. El Jefe puede seguir al grupo con F (Espacio salta al grupo, WASD cámara libre).
- **Pendiente (fase B, online):** conexión P2P (PeerJS, servidor público), sincronía de eventos, el Jefe como host con vista distinta a la de los sobrevivientes, y quitar el límite de pantalla cuando cada jugador tiene su propia PC. No se tocó en esta fase.
- No hay mandos físicos en las pruebas: los cambios de mando se revisaron por eventos, no se probaron con hardware.

## Fase 25 · Online por internet (PeerJS) + ajustes del modo Jefe
- Modo Jefe: oro del Jefe por segundo según dificultad (fácil 2 · normal 4 · pesadilla 6). Dificultad (para los sobrevivientes) escala vida/daño de zombis: 0.7 / 1 / 1.6. En Jefe local los 4 sobrevivientes son siempre bots (ya no entran humanos).
- Online: `scripts/net_core.js` + `peerjs.min.js` se incrustan en un JsCode al inicio de la escena Titulo (`fase25_online.py`, idempotente, respaldo `respaldos/antes_de_fase25_20261113.json`).
- Menú > modo > tecla 3 = escena nueva **Online**: crear sala (código de 5 letras) o unirse con código. Cada PC elige sus jugadores (A/Enter entra, A/D cambia personaje, Enter confirma); host: M modo, N dificultad, Enter/Start empieza. Huecos libres = bots. En modo Jefe el host es el Jefe.
- Arquitectura: el host corre todo el juego; clientes mandan entrada (30 Hz) y reciben instantáneas (solo cambios). Jugador remoto = Control -3 (mando virtual). En clientes se congelan todos los grupos de eventos salvo HUD, cámara, música, etc. Sin pausa ni cinemática en línea. Máquina con 2+ jugadores: el host los limita a lo que ve esa pantalla. Cliente desconectado → sus personajes pasan a bots. Esc sale.
- ESTADO: código integrado y con sintaxis validada; NO probado aún con dos instancias reales (falta prueba de punta a punta).

### Fase 25b · Sonidos en red y apagón
- `net_core.js` envuelve `gdjs.evtTools.sound.playSound`: el host reenvía cada efecto a los clientes (que ignoran los suyos y solo reproducen lo del host, respetando su SonidoActivo). La música ya corría en los clientes por las variables sincronizadas.
- Apagón: los clientes ejecutan los eventos de luz del grupo "Ambiente" (Apagon se sincroniza) y oscurecen su pantalla; con Jefe=1 el host/Jefe no se oscurece. Dura 15 s (carta del Jefe). Sin probar con dos máquinas.
- (Fase 24 corregida en Fase 25) `fase24_local.py` ya no deja entrar mandos en modo Jefe local (límite 0) y el texto del paso "Únanse" indica que los sobrevivientes son bots; `jefe_modo.js` fija DifVida/DifDanio por dificultad al iniciar el Jefe.
