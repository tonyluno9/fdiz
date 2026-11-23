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
- **Sprite que faltaba (resuelto en la fase 26):** `generado\sprites\mapa_extra\cic__mostrador_curvo_h180.png` no existía y el mostrador del CIC salía como rectángulo magenta. Ya está dibujado y enlazado.
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
  - `cic__mostrador_curvo_h180.png`: resuelto en la fase 26 (ya existe el sprite).
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


## Fase 26 · Multijugador local, Jefe, controles, bots y texturas CIC (2026-11-17)

Script: `gdevelop/scripts/fase26_multijugador.py` (idempotente; respaldo `respaldos/antes_de_fase26_20261117.json`). No confundir con `fase26_correcciones.py`, que es un script viejo de otra numeración. Si se vuelve a correr `fase25_online.py`, correr después `fase26_multijugador.py` (re-incrusta `net_core.js`; el script de la fase 26 limpia lo que fase25 envuelve).

1. **P2 controlaba al bot de P3 (corregido).** Causa: el grupo "Unirse con control" daba el mando al primer superviviente de la lista (aunque fuera humano o el bot 3) y las asignaciones hechas en el menú nunca marcaban `Pad1..Pad4` como ocupados. Ahora al iniciar la escena `PadK = 1` si algún jugador ya usa ese mando, y la unión solo puede tomar a un superviviente con `Control = -1` (bot).
2. **Modo Jefe: nadie se une al host.** En Juego el grupo de unión no corre en modo Jefe (además los 4 mandos quedan ocupados) y si alguien pulsa A sale el aviso "MODO JEFE: nadie puede unirse…". En el Menú, A en la pantalla "ÚNANSE" del Jefe muestra "NO PUEDES UNIRTE…". En el lobby en línea el host-Jefe que pulsa Enter/A recibe "Eres el Jefe: no puedes unirte como sobreviviente…" (antes decía "no hay lugar").
3. **Salas por código (en línea).** Ya existían (fase 25: crear sala / unirme con código, lobby con código visible). Ahora la opción **3 EN LÍNEA** del menú de modos se puede elegir con flechas/W-S/cruceta y aceptar (antes solo con la tecla 3).
4. **Pantalla de controles** desde la pausa: la pausa tiene 4 botones (CONTINUAR, CONTROLES, REINICIAR, MENÚ). CONTROLES muestra teclado/ratón y mando; Enter/Espacio/clic/A/B vuelven. Solo existe en modo offline (en línea no hay pausa).
5. **Selección por turnos (local).** Variable `Turno` en el Menú: P1 elige y confirma mientras P2..P4 (humanos) ven "ESPERANDO TURNO…" y no pueden mover ni confirmar; luego P2, etc. Al confirmar el último humano (si hay 2 o más) pasa solo a la dificultad. Enter/Start solo avanzan cuando todos los humanos confirmaron.
6. **Sin colisión entre compañeros y bots.** Era un evento JS ("Los pies conservan su máscara del mapa", `separar_supervivientes.js`) que empujaba a los supervivientes entre sí; se eliminó. Las colisiones con muros, muebles y puertas siguen igual.
7. **Todos recogen objetos clave.** Bidón y bolsa ya los recogía cualquier superviviente por colisión; se añadió además recogida por cercanía (70 px) para cualquiera (humano o bot) porque la máscara de colisión podía no tocar el objeto.
8. **Bots siguen a P1 y también a P2/P3.** Antes seguían el centro de la cámara. Ahora cada bot sigue a un humano vivo (reparto por turnos entre humanos; sin humanos, sigue a la guía como antes). Variables `BotX/BotY` en `Sup`.
9. **Texturas CIC:** el mostrador curvo (era `falta.png` magenta) y la puerta restringida electrónica (era un cuadrado morado liso) ya tienen sprite. Las otras 3 puertas provisionales (normal, electrónica, restringida) siguen siendo colores lisos. Si se vuelve a correr `importar_mapa.py`, esa puerta vuelve a generarse lisa.
10. **Verificación del modo en línea:** implementado (PeerJS, host con autoridad, 4 jugadores, sonidos y apagón). Revisado solo de forma estática (sintaxis de `net_core.js`, flujo menú → sala → lobby). **No se ha probado con dos máquinas reales**; falta esa prueba.

## Fase 27 · Controles ilustrados, pantalla Local/En línea del Jefe y lobby en línea con estilo del juego (2026-11-17)
Script: `scripts/fase27_jefe_y_controles.py` (idempotente; respaldo `respaldos/antes_de_fase27_20261117.json`). Orden: `fase25_online.py` → `fase26_multijugador.py` → `fase27_jefe_y_controles.py` (fase25 re-embebe `net_core.js`, que fase27 también parchea).
1. **Pantalla de controles (Pausa → CONTROLES)**: ahora lleva una ilustración de teclado + ratón (`p27_ctl_teclado.png`) y otra de mando (`p27_ctl_mando.png`) en `assets/interfaz/`, con el texto resumido debajo de cada una. Objetos nuevos `CtlTeclado`/`CtlMando` (capa HUD); se ocultan fuera de esa vista.
2. **Menú · modo Jefe → paso nuevo `jefetipo`** (LOCAL / EN LÍNEA) con las mismas tarjetas y el mismo fondo de escuela que la pantalla de modos (ilustraciones `ilus_modo_local.png` / `ilus_modo_online.png`, animaciones "l"/"o" de `IlusModo`). Se elige con ◄ ► / A D / ↑ ↓ / 1-2 / mando / clic en la tarjeta; Enter, F, Espacio o A aceptan; Esc vuelve.
   - **Local**: va directo a la selección de personajes de los 4 bots (Esc desde ahí vuelve a `jefetipo`).
   - **En línea**: pone `OnlineJefe=1` (variable global nueva) y abre la escena Online. Al salir de Online, el menú regresa a `jefetipo`.
   - La opción 3 EN LÍNEA del menú de modos pone `OnlineJefe=0` (sala de modo Escape).
3. **Escena Online con el estilo del resto**: fondo de escuela, placa de título, panel oscuro (`p27_panel_sala.png`) y barra inferior (`Placa`, `BarraPie`, `PanelOn`).
   - **Sala del host**: arriba aparece "CÓDIGO DE LA SALA" y el código de 5 letras/números en grande, con la indicación de qué hacer en la otra PC.
   - **Modo Jefe en línea**: el modo lo fija el menú (se quitaron las teclas M/Y que lo cambiaban). El host es el Jefe (no puede unirse como sobreviviente). Quien se une con el código es **host secundario** ("Sub-host N"): su PC aloja hasta 4 jugadores locales (él con teclado + mandos), siempre con un máximo de 4 sobrevivientes entre todas las PCs, y espera a que el Jefe inicie la partida (mensaje "Esperando a que el Jefe inicie la partida…").
   - Lista de la sala rediseñada: contador de sobrevivientes x/4, etiquetas JEFE / host secundario, mensajes de estado.
4. Detalle técnico: `fase25_online.py` añadía "3 EN LÍNEA" a cualquier título de `TxtMenu` que contuviera "JEFE DE ZOMBIES"; el título del paso nuevo es "MODO JEFE: ¿CÓMO QUIERES JUGAR?" para evitarlo (y fase27 corrige uno ya creado).
**Verificado (estático)**: JSON carga, `node --check` en `net_core.js` y en el JS embebido, cadena fase25→26→27 ejecutada dos veces con el mismo md5. **NO probado**: nada se ha ejecutado en GDevelop (posición exacta de textos/tarjetas, z-order del panel) ni con dos máquinas reales; el modo en línea sigue sin prueba de extremo a extremo.

## Fase 28 — UI de lanzamiento, Jefe, fuera la tienda
Script: `scripts/fase28_ui_jefe_tienda.py` (idempotente; respaldo `respaldos/antes_de_fase28_20261117.json`; cadena fase25→26→27→28 con md5 estable).
- **UI sin textos de guía**: eliminados pies/ayudas en Título, Menú, Juego (demo, controles, "mantén Usar", banners de mordido y de unirse en Jefe), Pausa, Resultados y Online (`net_core.js`: sin "W/S elegir", "Enter conectar", etc.). Menú: tercera tarjeta **EN LÍNEA** en la selección de modo (antes solo accesible por los textos), selección con ratón (hover) y con izquierda/derecha.
- **Resultados**: fuente Pixelify Sans (`assets/interfaz/fuentes/`), ajuste automático del texto al cuadro, títulos de Jefe más cortos. Botones REINICIAR y MENÚ clicables con rectángulos fijos, resalte al pasar el ratón, teclado/mando (Enter/Espacio/A reinicia; Esc/M/B menú). La victoria también tiene los dos botones (se quitó el salto automático al título).
- **Online**: fondo con video + velo, sin barra de pie.
- **Jefe**: monedas 1 cada 2.5 s (fácil), 2 s (medio), 1.5 s (difícil). Quitado el panel de instrucciones y la ayuda en vivo; se conserva la barra de la próxima moneda.
- **Tienda eliminada**: máquinas, TxtPrecio, compra, `Dinero` del equipo, debug de dinero, línea de premios y "$" del HUD. Los lockers dan galletas en vez de monedas. Panel de dinero visible solo en Jefe (oro).
- **Tony**: nuevo pasivo "Come mejor" (la comida le cura 50 % más), también para Tony fuerte.
- Sin probar: nada se ejecutó en GDevelop; online sin probar con dos máquinas.

## Fase 29 — Menús reparados, fondos de texto, fuente, IA del Jefe local, título con latido
Script: `scripts/fase29_ui_ia.py` (idempotente; respaldo `respaldos/antes_de_fase29_20261117.json`; cadena fase25→29 con md5 estable). Nuevo asset `assets/interfaz/p29_fondo_texto.png`.
- **Menús**: título del paso Jefe → "MODO JEFE" (ya cabe en la placa); leyendas LOCAL/EN LÍNEA vuelven a quedar bajo sus tarjetas (el parche de la Fase 28 las había movido).
- **Fondo detrás de los textos**: objeto `FondoTxt` (PanelSprite de 9 cortes) y un motor en JS por escena que lo coloca detrás de: leyendas del menú de modos, lista de la sala, frase del título, TxtAyuda/TxtBanner/TxtDialogo del juego, etiquetas "ZONA VISIBLE/NO CABE" del Jefe, y todos los textos de la escena Online fuera de la sala (en la sala ya hay paneles).
- **Fuente**: Pixelify Sans en todos los TextObject del proyecto, con contorno y sombra.
- **Título**: "PRESIONA ENTER / A PARA INICIAR" dentro del cartel, con latido (tamaño, brillo y opacidad en doble pulso). Enter, Espacio, clic o A/Start siguen iniciando.
- **IA zombis**: se elimina el choque rígido zombi↔zombi (formaba la masa inmóvil); separación suave en JS; cada zombi tiene su hueco alrededor del objetivo; rutas escalonadas (`RutaJit`); desatasco (si lleva 1.2 s sin moverse lejos del objetivo, toma un desvío aleatorio).
- **IA bots (Jefe local)**: ya no se quedan quietos en un punto: patrullan hacia lockers lejanos del mapa, huyen de grupos de 4+ zombis (o 2+ con poca vida) hacia el punto abierto más lejano, y si quedan acorralados pelean 3 s. El bot que huye no corre hacia el zombi más cercano.
- Sin probar: nada se ejecutó en GDevelop. La IA es ajuste por lectura de código; los valores (radios 240/420, 4 zombis, etc.) pueden requerir afinar.

## Fase 30 — Solo ESCAPE y JEFE, zombis orientados, colisión de bots solo en Jefe local
Script: `scripts/fase30_modo_ia.py` (va al final de la cadena; deshace la tercera tarjeta de la Fase 28 cada vez que corre la cadena).
- **Menú de modos**: quitada la tarjeta EN LÍNEA; vuelven las dos tarjetas (marcos 340/1140, leyendas 560/1360, videos 390/1190), navegación y ratón de 2 opciones. Ya no hay acceso a En línea desde el modo Escape; el Jefe sigue ofreciendo Local/En línea.
- **Zombis**: la animación de caminar se orienta por su movimiento real (JS `FDIZ-FASE30-DIR`), no por el destino; separación entre zombis más suave (tope 1.1 px/cuadro).
- **Colisión entre supervivientes**: solo en Jefe local (Jefe=1 y NetRol=0), con `separar_supervivientes.js`; en el resto de modos sigue sin colisión. En Jefe se desactiva el empuje superviviente↔zombi (hacía vibrar a los bots contra paredes).
- **Bots**: Conserje y Gordo pesan x3 al decidir huir y se evitan con margen mayor al elegir ruta de escape.
- Sin probar en GDevelop.

## Fase 31 — Escape también con pantalla Local / En línea
Script: `scripts/fase31_escape_local_online.py` (al final de la cadena fase25→31; md5 estable en 3 corridas).
- Flujo: Modos (Escape | Jefe) → pantalla Local / En línea de ese modo → Local: Escape va a "unirse" (jugadores con teclado/mando + bots), Jefe va a elegir los 4 bots; En línea: escena Online (crear sala con código / unirse con código). Variable de escena `JT` (0 Escape, 1 Jefe) y global `OnlineEsc` (análoga a `OnlineJefe`).
- Esc retrocede un paso (unirse/equipo → Local/En línea → Modos → Título); al volver de la sala en línea el menú regresa a la pantalla Local/En línea del modo que se estaba usando, con En línea resaltado.
- Textos por modo: título "ESCAPE" / "MODO JEFE"; leyendas Escape: "1 a 4 jugadores + bots" y "Hasta 4 jugadores · sala con código".
- Quitados el atajo Num3 y la opción 3 del menú de modos.
- Verificación: simulador de los eventos del menú (script temporal, no incluido) recorre Escape y Jefe: Enter/Esc/derecha, entrar a Online y volver. Resultado correcto en ambos. La escena Online y la partida en línea de Escape no se ejecutaron (solo lectura de `net_core.js`: lobby con código, host + PCs, hasta 4 jugadores, bots completan).

## Fase 32 — Modo en línea también en la versión web
Script: `scripts/fase32_online_web.py` (parchea `net_core.js`; correr la cadena fase25→32 dos veces, md5 estable).
- El online ya era 100 % JavaScript de navegador (PeerJS/WebRTC dentro del motor de GDevelop), así que corre igual en la exportación HTML5 y en las versiones de escritorio; web y escritorio pueden jugar en la misma sala (mismo protocolo, misma versión del juego).
- Añadido: lista de servidores STUN (Google y Cloudflare) y punto de configuración `TURN` (arreglo vacío en `net_core.js` o `window.FDIZ_TURN`) para redes que bloquean la conexión directa; pegar el código con el evento `paste` (el navegador no deja leer el portapapeles con Ctrl+V); mensaje de error de conexión más claro.
- Cómo publicar la versión web: exportar HTML5 desde GDevelop y subir la carpeta a un hosting con HTTPS (itch.io, GitHub Pages, Netlify). Abrir `index.html` con doble clic (file://) no sirve para el juego ni para la red.
- Límites conocidos: el host debe dejar su pestaña visible (los navegadores frenan pestañas en segundo plano); sin TURN, algunas redes móviles/corporativas no conectan; el servidor de señalización es el gratuito de PeerJS (solo para encontrar la sala; la partida va directa entre jugadores). Sin probar con dos máquinas ni en navegador real.

## Fase 33 · Iconos Local / En línea y reacción al mouse
- Causa del bug: `fase28`/`fase30` ponían `VidIlusEscape` (x 390) y `VidIlusJefe` (x 1190) en las tarjetas también fuera de la pantalla de modos, y los videos tapaban las animaciones `l` (computadora) y `o` (globo) de `IlusModo` en la pantalla Local / En línea de Escape y de Jefe.
- Arreglo (`scripts/fase33_iconos_y_hover.py`, última de la cadena): en el grupo Videos, con `Paso != "modo"` esos videos van a x = -6000; con `Paso = "modo"` siguen en 390 / 1190.
- Hover: un evento JS al final de Menu, Juego y Resultados. Los botones se iluminan y el cursor pasa a mano (sin cambiar tamaño ni posición: la primera versión escalaba y los videos crecían sin parar, se quitó). Menu: MarcoModo, SelMarco, DifBtn, EqCelda (ilustraciones y videos no se tocan). Juego: PausaBtn, BtnOmitir. Resultados: BtnRei, BtnMenuR.
- Online (lobby): se maneja solo con teclado, no tiene botones de mouse, así que no hay hover ahí.
- Cadena: fase25 → 26_multijugador → 27_jefe_y_controles → 28 → 29 → 30 → 31 → 32 → 33. Tres pasadas dan el mismo md5. Respaldo: `respaldos/antes_de_fase33_20261117.json`.
- Sin probar dentro de GDevelop (solo revisión estática y node --check).

## Fase 34 · Pantallas de jugar en línea con el mouse
- `scripts/fase34_online_mouse.py` (parchea `net_core.js`; correr la cadena dos veces). `T()` ahora devuelve su rectángulo y hay botones de texto con resalte y cursor de mano.
- Menú en línea: pasar el mouse selecciona la opción, clic la activa; botón Volver.
- Código de sala: Pegar código (portapapeles), Unirme a la sala, Volver. Conectando: Cancelar. Error: Aceptar.
- Sala: columna "CON EL RATÓN" con Unirme, ◄ / ► Personaje, Listo, Cancelar, Dificultad (host), INICIAR PARTIDA (host, cuando todos están listos) y Salir. El mouse entra como el jugador "TECLADO".
- Límite: el código de sala solo se escribe con teclado o con Pegar (en web el navegador puede pedir permiso de portapapeles; Ctrl+V sigue funcionando).
- Sin probar en GDevelop ni con dos máquinas; solo node --check y cadena estable (mismo md5).

## Fase 35 · Hover en la pantalla de dificultad
- `scripts/fase35_hover_dificultad.py`: tres eventos (FDIZ-FASE35-HOV-D0/D1/D2) antes de la actualización de PMX/PMY: al mover el mouse sobre FÁCIL / NORMAL / PESADILLA (x 720–1200) se cambia `Sel`, así la opción se ilumina igual que con el teclado (opacidad 255 + animación) y el resto se atenúa. El clic ya aceptaba la opción elegida. Además queda el tinte cálido de la Fase 33.
- Sin probar en GDevelop; cadena estable (mismo md5 entre pasadas).

## Fase 36 · Hover en el selector de personajes
- `scripts/fase36_hover_personajes.py`: variable de escena `HV` (-1 sin vista previa, 0–7 = retrato bajo el mouse; orden tony, miranda, cesar, alan, castillo, alessandro, gabo, carlos).
- Eventos FDIZ-FASE36-SET (antes de PMX/PMY): al mover el mouse sobre un retrato (rejilla x 1105+171·col, y 212+176·fila, 156×156) `HV` toma ese índice; se limpia al salir de la rejilla, al pulsar teclas de navegación/Enter o al salir del paso `equipo`.
- FDIZ-FASE36-PREV (después de calcular KF/NMF): con `HV` activo, `KF` y `NMF` son los del personaje bajo el mouse, así cambian video, cuerpo, nombre, habilidades e iconos (todo se deriva de KF). El subtítulo conserva su texto por slot (P1/BOT 2/P2… · eligiendo / LISTO); el texto "VISTA PREVIA" se quitó.
- Resalte ligero: `EqRet` se añade al motor de hover de la Fase 33 (tinte cálido). El clic sigue eligiendo como antes.
- Sin probar en GDevelop; cadena estable (mismo md5 entre pasadas).

## Fase 37 · Pantalla "Únanse": botones A / Y / P
- `scripts/fase37_unirse_botones.py` genera tres iconos pixel art (144×108 como los `slot_ico_*`): `slot_ico_btn_a` (A verde de Xbox), `slot_ico_btn_y` (Y amarilla), `slot_ico_key_p` (tecla P). Se registran como recursos.
- (a) La animación `libre` de `SlotIco` (slots vacíos) ahora usa la A de Xbox en lugar del mando con "+".
- (b) Objeto nuevo `SlotAlt` (animaciones `y` y `p`), una instancia bajo el teclado del P1 (x 240, y 770, 120×90, dentro de la tarjeta; oculto fuera de la pantalla `unirse`).
- Lógica (FDIZ-FASE37-CTL, después de los eventos de icono de slot): con `S1Ctl = 0` (teclado), Y en el mando n (1–4) → `S1Ctl = n` si ningún otro slot usa ese mando; el icono grande pasa a mando (evento existente `S1Ctl > 0`) y `SlotAlt` pasa a P. Con `S1Ctl > 0`, la tecla P → `S1Ctl = 0` (teclado y ratón), icono de teclado y `SlotAlt` vuelve a Y.
- Las reglas existentes siguen: A en un mando nuevo ocupa el primer slot libre y el mando del P1 se excluye; `P1Ctl` se copia a la partida desde `S1Ctl`.
- Sin probar en GDevelop ni con mandos reales; cadena estable (mismo md5 entre pasadas).

## Fase 38 · Ajuste de la pantalla "Únanse"
- `scripts/fase38_unirse_ajuste.py`: `SlotAlt` (Y/P) sube de y 770 a 745. Eventos FDIZ-FASE38-RETRATOS (antes de FASE37-CTL): en `unirse`, `SelRetrato` baja de y 275 a 300 y se corrige en x según la imagen (slots vacíos +15 px, con jugador +9 px, medidos en captura); fuera de `unirse` (selección de personaje) vuelve a x base / y 275, sin cambios.
- Los 15/9 px salen de medir una captura, no de la geometría de los PNG (que sugiere que ya estaban casi centrados): si queda descentrado, ajustar esos dos números.
- Sin probar en GDevelop; cadena estable (mismo md5).

## Fase 39 · Navegación con mando en todo el juego
- `scripts/fase39_mando_global.py` (parchea también `scripts/Gamepads.json`).
- Stick izquierdo = cruceta: en la extensión Gamepads (`onFirstSceneLoaded`, tarea de inicio de cuadro) los botones 12–15 (Arriba/Abajo/Izquierda/Derecha) cuentan como pulsados si el stick pasa de 0.6 en esa dirección (eje dominante). Todo lo que ya leía la cruceta (menú de modos, tipo de jefe, selección de personajes, dificultad, pausa) responde también al joystick. El movimiento en partida no cambia (usa los ejes directamente).
- Selección de personajes: eventos FDIZ-FASE39-START-EQ. Start del mando dueño del slot que tiene el turno confirma su personaje y, si ya no falta ningún humano por confirmar, pasa a dificultad (`Sel = 1`); si faltan, solo confirma. Con todos listos (`Turno = 5`) el Start de siempre sigue pasando.
- Cinemática: Select (`BACK`) de los mandos 1–4 también la omite (junto a Start / Enter).
- Resultados: variable de escena `Sel` (0 Reintentar, 1 Menú). Arriba/Abajo/Izquierda/Derecha (cruceta, joystick o flechas) alternan; la opción resaltada va a opacidad 255; A / Start / Enter / Espacio confirman la resaltada (con `Sel = 0` es lo de siempre). B / Esc / M siguen yendo al menú.
- Pausa: los mandos 1–4 (antes 1–3 en algunos eventos) pausan y navegan.
- Sin probar con mandos reales ni en GDevelop; cadena estable (mismo md5 entre pasadas). `BACK` es el nombre del botón Select en la extensión (mandos tipo Xbox; en PS4 es SHARE y la extensión lo mapea al mismo índice 8).

## Fase 40 · Profesores reclutables: Joel, Justino y Canepa (2026-11-17)
Scripts: `scripts/fase40_sprites_profes.py` (sprites) y `scripts/fase40_profesores.py` (proyecto; idempotente, va al final de la cadena, después de fase39; respaldo `respaldos/antes_de_fase40_20261117.json`). Lógica en `scripts/profes.js` (se incrusta como evento JS `FDIZ-FASE40-MOD`). Pruebas: `node gdevelop/scripts/prueba_profes.js`.
Si se vuelve a correr `fase25_online.py` (o cualquier fase anterior), correr después `fase40_profesores.py`.

**Cómo funciona**
- Un solo objeto `Profe` (variable `Nombre`) para los tres mientras esperan; se quitó el objeto `Canepa`. Una instancia de cada uno.
- Estados por profe (variables de escena `ProfJoel`, `ProfJustino`, `ProfCanepa`, sincronizadas en línea): `espera`, `conversacion`, `aliado`, `mordido`, `caido`, `rechazado`, `convertido`, `fuera`. `Prof<Nombre>Seg` = segundos que faltan (rechazo o mordida).
- Esperando: quieto, animación de reposo, inmune (no es un `Sup`, así que los zombis no lo eligen ni lo muerden). Pide ayuda cuando un humano de esa máquina entra a 480 px (cada 10 s, máximo 4 veces por visita, un aviso a la vez). Acercarse, oírlo o irse no cuenta como rechazo.
- Usar (F / A del mando) a menos de 115 px y con línea de vista: indicación según el dispositivo (`[F] Hablar con Joel` / `(A) Hablar con Joel`). El diálogo abre con un flanco de Usar y no confirma hasta soltar el botón. W/S, flechas, cruceta o stick eligen; F/Enter/Espacio/A aceptan; Retroceso/Esc/B cierran (cerrar = sigue esperando e inmune). El jugador de teclado también puede usar el clic. Mientras hay diálogo, Esc/P/Start no pausan (`ProfDlg`).
- "Dejarlo aquí" pide confirmación y explica la consecuencia (30 s → zombi, sin vuelta atrás).
- Aceptar: se crea un `Sup` bot (Jugador 5 = Joel, 6 = Justino, 7 = Canepa, Control −1) en el lugar del profe; usa toda la lógica de los bots (ruta A*, puertas, pelea, armas del piso, revivir, curar, niebla de bordes, orden de profundidad, choques con muros y muebles). `Rescatados` +1 una sola vez por profe.
- Rechazar: pierde la inmunidad, se queda en su lugar, cuenta individual de 30 s de juego (se detiene con la pausa; alejarse no la cambia). Un zombi pegado a él le pega (vida mínima 1, tinte rojo), pero eso no reinicia, acumula ni adelanta la cuenta. Encima se ve `Joel · 23 s` y en el panel `ZOMBI EN 23 s`; el profe se va poniendo verde.
- Conversión (rechazo o mordida sin curar): se borra el profe o aliado y se crea **un** `ZJoel` / `ZJustino` / `ZCanepa` en la misma posición, persiguiendo; etiqueta `JOEL (ZOMBI)`. Están en el grupo `Zombies`: navegación, colisiones, combate, muerte, premios, Oro y niebla de bordes iguales a los demás.
- Panel compacto de profes a la izquierda (y 262–440, entre los paneles de P1 y P3): nombre, estado, barra de vida, cuenta de rechazo o barra de infección. Encima de cada aliado: nombre y `MORDIDO 20 s` / `¡AYÚDALO!`.
- Salas oscuras: si el profe está bajo niebla, la petición sale arriba en el HUD (`Alguien pide ayuda desde LA NEVERÍA: «…»`) y no se dibuja nada sobre él; las etiquetas de profes y de su zombi también se ocultan bajo niebla.

**Valores elegidos** (centralizados en `profes.js` → `PROFES` / `CFG`; los de los zombis en `fase40_profesores.py`)

| Aliado | Vida | Velocidad | Fuerza (× daño del arma; puños 7) |
|---|---|---|---|
| Joel | 100 | 204 | 1.0 |
| Justino | 110 | 198 | 1.1 |
| Canepa | 120 | 192 | 1.15 |

- Zombis de profe: vida base = la de `ZConserje` leída del proyecto (hoy 250); el evento `DifOk` le aplica `DifVida` una sola vez, igual que al conserje (el JS no escala nada). Daño 12 (normal 5, conserje 14) × `DifDanio`. Velocidad 84 (normal 99, conserje 72) + 8 % por nivel de infestación, como todos. Oro 5.
- Mordida, caída y cura: mismas reglas que los alumnos (12 % por golpe; 35 s para curar manteniendo Usar 3 s a ≤ 95 px; caído 25 s, revivir manteniendo Usar 3 s a ≤ 80 px). Los auxilian los jugadores y los bots (un bot va a un profe caído o mordido a ≤ 600 px si no está ayudando a un alumno). Los profes aliados también reviven y curan a los alumnos.
- Recompensa del rescate anterior: **se conserva** (+30 de vida al equipo principal de pie), una sola vez por profe, al reclutarlo.

**Decisiones que cambian la experiencia (y conflictos con la propuesta)**
1. *Justino "detrás de la barra"*: la franja entre la barra horizontal y los refrigeradores / congelador está cerrada en la rejilla de navegación (solo conecta con la cocina, que tampoco tiene salida); ahí no podría salir como aliado. Se colocó en el **lado interior de la pata de la barra en L** (1936, 1668): accesible por el pasillo de la puerta lateral P45 y por el salón, a ~120 px del congelador, lejos de los refrigeradores (x ≤ 1661) y de la caja (1700, 1586). Ver `capturas/fase40_ubicaciones_profes.jpg` (el PNG del mapa con props está desactualizado: el congelador real está arriba a la derecha, donde marca su colisión roja). Nota: el bidón o bolsa posible de "Cocina nevería" está en esa zona cerrada (problema anterior, no se tocó).
2. *Sin red, el diálogo detiene la partida* (como la pausa) para que nadie reciba golpes mientras lee. En línea no se puede pausar: solo se congela la entrada de quien habla.
3. *Derrota*: solo cuentan los 4 principales de pie (`Vivos` filtra Jugador ≤ 4). Un profe aliado no mantiene viva la partida.
4. *Aliado caído 25 s sin ayuda* → `fuera` el resto de la partida (no reaparece con el siguiente objetivo como los alumnos).
5. *Profe rechazado*: no es un `Sup`, así que no puede ser mordido; los golpes son visuales y no cambian la cuenta (como pide la propuesta).
6. Si un profe cura a un alumno, al profe no se le cobra comida ni vida (el costo existente es entre alumnos). Si un alumno cura a un profe, sí se le cobra al alumno, igual que entre alumnos.
7. Modo Jefe local: los sobrevivientes son bots y los bots no deciden, así que los profes se quedan esperando.
8. *Final ¡Aguanten!*: la victoria nunca dependió de Canepa (60 s aguantando). Ahora el camión ya no anima a ningún objeto Canepa. Si Canepa es aliado y está de pie, en el final camina por ruta a su lugar junto al camión y, sin zombis encima, hace la animación de reparar (banner "¡AGUANTEN! Canepa repara el camión"). Si fue rechazado, se convirtió, cayó o quedó fuera: banner "¡AGUANTEN! Reparen el camión y resistan" y el final se completa igual. Nunca se crea otro Canepa ni se mueve desde otra parte del mapa, y su versión zombi no recibe animaciones del camión.
9. Bots: la distancia a la que se detienen sigue siendo 90 + 45·Jugador para P2–P4; para los profes es 150 / 195 / 240 px (con la fórmula original serían 315–405).

**Cambios en eventos** (todos con la marca `FDIZ-FASE40`): módulo JS al inicio; `input` después de `FASE25-INPUT`; `botsDestino` dentro de "Bots"; `bots` al final de "Bots: curar mordidos"; `ayuda` en "Vida, caída y revivir"; `mordidas` al inicio de "Compañeros mordidos" y `curaAlumno` dentro de los ciclos M1–M4; grupo **"Profesores reclutables"** en lugar de "Rescates: Joel y Justino" (sin compuerta de red: también dibuja en los clientes). Filtros `Jugador <= 4`: unirse con mando (un mando nunca toma a un profe), mordida genérica, conteo de `Vivos` y reaparición al cumplir objetivo. La pausa exige `ProfDlg = 0`. Listas de zombis del JS incrustado, `niebla_borde.js` (+ `Profe`) y `bots_habilidades.js` (los profes no usan habilidades).

**En línea**: el host decide todo (estados, cuentas, daño, mordidas, conversión). El cliente manda `{t:"prof", k, d: abre|cierra|acepta|rechaza}` (`net_core.js`: `N.toHost`, `N.onProf`, `N.onLocalInput`). El host acepta una sola decisión por profe (la primera válida; quien abrió el diálogo tiene prioridad) y sincroniza `Prof*`, `Profe` y los zombis nuevos con la configuración de red. Reiniciar la escena devuelve los tres profes a su lugar, inmunes, con diálogos y contadores en cero (todo el estado vive en la escena).

**Recursos gráficos**
- Convertidos de los GIF: Joel y Justino (quieto, caminar abajo/arriba/lado, pegar lado/arriba) → `generado/sprites/profes/<profe>/`. No hacen falta `caminar_izquierda` ni `pegar_izquierda` (se voltea "lado"); `justino/pegar_izquierda.gif` está vacío.
- **Provisionales** (faltan): `caer_levantarse` de los tres (el cuadro quieto que se inclina) y `pegar_abajo` de los tres (copia de pegar_lado).
- **Zombis de profe: arte real** (sustituye a los provisionales verdes). Fuente: `animaciones_gif/profes_zombi/<profe>/<animacion>.gif` → `fase40_sprites_profes.py` → `generado/sprites/zombies/profe_<profe>/` (cada carpeta tiene un `LEEME.txt` con el origen de cada animación).
  - Justino: GIF hechos a mano (caminar ×3, atacar_lado, atacar_abajo, golpe_morir). Venían con cuadros duplicados (7 → 4 poses) y `caminar_lado` grabado en video (79 cuadros, 40 distintos): se toma el ciclo de 4 poses que se repite. `caminar_izquierda` y `atacar_izquierda` no se usan (el juego voltea "lado"; además `atacar_izquierda` es otro golpe y trae manchas de sangre que no tiene el resto).
  - Joel y Canepa: GIF generados por `scripts/fase40_hojas_zombi.py` desde sus hojas (`animaciones_gif/profes_zombi/hojas/<profe>_caminar.jpg` y `<profe>_ataque.jpg`): fila 1 de lado, 2 de espaldas, 3 de frente; en la de ataque, fila 1 ataque de lado, 2 golpe desde arriba (→ `atacar_abajo`), 3 golpe final con humo (→ `golpe_morir`).
  - Inconsistencias revisadas en las hojas: de cada profe había dos versiones. Se descartaron (quedan en `hojas/descartadas/`): Joel caminar B (sin barba, otro peinado), Joel ataque B (ojos sin rojo en varios cuadros, sin barba, cuerpo final translúcido), Canepa caminar B (primer cuadro de lado sin pose de caminar; de espaldas gira la cabeza y se ve la visera) y Canepa ataque B (ojos color piel en el primer cuadro, humo blanco que tapa al personaje). Correcciones: Joel caminaba mirando a la izquierda (se volteó), restos de fondo blanco entre brazo y cuerpo y junto a la cara (se quitaron), halo claro del JPG alrededor del contorno (se quitó).
  - **Derivado** (no hay arte): `atacar_arriba` de los tres = `caminar_arriba` que se encoge y se estira hacia adelante (como el ataque de espaldas del conserje). `atacar_abajo` de Joel y Canepa es el golpe desde arriba, que mira un poco a la derecha (el juego no voltea `atacar_abajo`); el de Justino sí es de frente.
  - Escala: la estatura de pie queda en 96 px, igual que el profe humano. Tiempos (`ANIM_Z`): caminar 0.18 s por cuadro, ataques 0.12 s, golpe final 0.15 s (4 cuadros cada una).

**Pruebas**: `prueba_profes.js` (16 casos, todos correctos) simula la escena y recorre: encontrar sin interactuar (posición, inmunidad, límite de peticiones), abrir y cerrar, mantener F no confirma, aceptar, los tres con 4 principales, rechazar con aviso, pausa / alejarse / golpes contra la cuenta, conversión única con vida 250, mordida curada, mordida → zombi, caído auxiliado por un bot, profe que revive a un alumno, aliado fuera, decisiones simultáneas en línea y cliente que manda su decisión, final con Canepa aliado o rechazado, reinicio, sala oscura y mando. Además: `node --check` de los 35 eventos JS del proyecto, `fase40_profesores.py` estable (mismo md5 en pasadas sucesivas) y las APIs usadas existen en el runtime GDJS 5.6.287 instalado.
**Sin probar**: nada se ejecutó dentro de GDevelop (combate, rutas reales por puertas y muebles, colisiones, dibujo de la interfaz, sonido) ni con dos máquinas en línea.


## Fase 41 · Pasillo de la nevería más ancho y monedas solo en modo Jefe (2026-11-17)
Script: `scripts/fase41_pasillo_y_monedas.py` (idempotente; va después de `fase40_profesores.py`; respaldos `respaldos/antes_de_fase41_*`). Si se vuelve a importar el mapa, correrlo otra vez (también deja corregidos los datos fuente de `mapa/final`).

**Pasillo de piedra entre la nevería (puerta P45) y las Salas 3 y 4**
- Medía 32 px (1 casilla). El pie de un personaje mide 40 px y la navegación A* pide 18 px de holgura por lado, así que nadie podía pasar.
- La pared izquierda de las Salas 3 y 4 se recorrió **2 casillas (64 px) a la derecha**. El pasillo queda de **96 px** (x 2016-2112, de y 1376 a 2112) y abierto arriba y abajo. Las salas quedan de 512 px de ancho (antes 576).
- Cambios: muros (remate de arriba, pared de arriba de Sala 3, pared izquierda, muro entre salas y pared de abajo), fondo visible (`assets/mapa/fondo/fondo_0_1.png` y `fondo_1_1.png`: la piedra y la pared movida), Tilemap oculto (`mapa_fdiz_gdevelop.json` del proyecto) y niebla de Sala 3 y Sala 4.
- Se quitó la primera columna de computadoras y sillas de cada sala (4 escritorios con su choque), porque quedaba dentro de la pared nueva. El letrero de salida de emergencia de la Sala 4 se recorrió con la pared.
- Datos fuente actualizados igual: `mapa/final/mapa_fdiz_completo.png`, `mapa_fdiz_gdevelop.json`, `mapa_fdiz.tmj`, `mapa_fdiz_datos.json` (colisiones, zonas y cuartos) y `mapa_fdiz_props.json`. `fuente/construir_mapa.py` y `amueblar.py` **no** se tocaron: si se regenera el mapa desde ahí, hay que volver a correr esta fase.
- Comprobado: rejilla A* de 16 px con holgura 18 sobre los Muro y ChoqueMueble del proyecto. Desde la nevería se llega por el pasillo a la salida de abajo y a la de arriba, con 4 celdas libres de ancho (antes 0).

**Monedas**
- Los lockers y mochilas soltaban una moneda (45 %) en todos los modos. La fase 28 quería cambiarla por galletas, pero el proyecto seguía creando la moneda, y ya no hay evento para recogerla (la tienda y el dinero se quitaron).
- Ahora la moneda solo sale con `Jefe = 1`. En modo escape ese 45 % da galletas (Cura 30), como pretendía la fase 28. Marca `FDIZ-FASE41-MONEDAS`.
- En modo Jefe la moneda aparece pero sigue sin poder recogerse (no hay evento de recoger); queda como estaba.

**Sin probar** dentro de GDevelop: el recorrido real por el pasillo y cómo se ve la moneda o las galletas en cada modo.


## Fase 42 · Correr con estamina (2026-11-17)
Script: `scripts/fase42_correr.py` (idempotente; va después de `fase41`; respaldo `respaldos/antes_de_fase42_*.json`). Lógica en `scripts/correr.js` (evento JS `FDIZ-FASE42-MOD`). Pruebas: `node gdevelop/scripts/prueba_correr.js` (13 casos). Si se vuelve a correr `fase5_jugadores.py` o `fase25_online.py`, correr esta fase otra vez.

- Antes, mantener Shift bajaba la velocidad a la mitad ("caminar despacio") y no servía para nada. Ahora **Shift** (izquierdo o derecho), o **LB / L3** en el mando, sirve para **correr**: la velocidad normal × 1.5 (ya con la `Rapidez` de pasivas y efectos). Las piernas se animan 1.35 veces más rápido.
- **Estamina 15.** Correr gasta 3 por segundo (5 s con la barra llena). Al soltar, tras 0.8 s se recupera a 2.5 por segundo (de vacía a llena en unos 6.8 s). Solo gasta si el personaje se mueve; quieto con Shift no gasta.
- **Agotado:** si se vacía, no puede volver a correr hasta juntar 5, aunque mantenga o toque el botón. Así no se puede spamear. Los toques cortos tampoco ayudan: cada toque gasta y la espera de 0.8 s vuelve a empezar.
- **Barra:** en el HUD, pegada al panel de cada jugador y del mismo ancho: debajo de los paneles de arriba (P1 y P2) y encima de los de abajo (P3 y P4). Solo aparece si el panel está visible y se ve siempre, aunque esté llena. Es azul; anaranjada bajo 5; roja y parpadeando cuando está agotado, con una marca blanca en el 5. Tiene divisiones cada 5 de estamina. Se dibuja con el objeto `EstDib`, también en los clientes en línea. Para dejarle lugar, los 3 espacios de inventario (`HudInv`) se recorrieron: arriba de y 186 a 210, abajo de y 858 a 832. La medida de la barra está en `correr.js` → `BARRA` (alto, separación y margen).
- Solo los 4 personajes principales de pie. Los profes aliados no corren (los bots sí desde la fase 43, ver bitacora2.md). La pausa congela la estamina.
- Valores en `correr.js` → `CFG` (max, gasto, regen, espera, umbral, factor, anim).
- Variables nuevas en `Sup`: `Estamina`, `Agotado`, `Corre`, `EstPausa`. Las tres primeras se sincronizan en línea.
- Se quitaron los dos eventos de caminar despacio de "Movimiento y animación" (Shift del teclado y `NetSp` del jugador remoto). El texto de controles del mando ahora dice "LB  correr"; el de teclado ya decía "Shift  correr".
- **Corrección en línea:** el cliente preguntaba por la tecla 16 para mandar Shift, pero GDevelop la registra como 1016 (izquierda) o 2016 (derecha), así que nunca llegaba. Ahora manda Shift, LB o L3 (`net_core.js` y la copia incrustada en Titulo).
- **Sin probar** dentro de GDevelop ni con dos máquinas: cómo se siente la velocidad, la barra del HUD con 2 a 4 jugadores y LB/L3 en mandos reales.


## Fase 55 · Modo Historia: 5 objetivos fijos en orden (2026-11-20; desde la fase 61 son 6 misiones: ver abajo)
Scripts: `scripts/fase55_ilus_historia.py` (ilustración provisional de la tarjeta, una vez) y `scripts/fase55_historia.py` (idempotente; va después de `fase54` de cesar; respaldo `respaldos/antes_de_fase55_*.json`). Pruebas: `python gdevelop/scripts/prueba_historia.py` (17 casos). Si se vuelve a correr una fase que regenere eventos del Menú o de Juego, correr esta fase otra vez.

**Cómo se juega**
- Menú "ELIGE EL MODO": ahora hay tres tarjetas: ESCAPE | JEFE DE ZOMBIES | HISTORIA (Modo global `"historia"`). Después se elige LOCAL o EN LÍNEA, igual que en Escape. Historia se comporta como Escape en todo lo demás (bots, profes, final, resultados).
- Orden fijo: 1) llamar desde la computadora del CIC → 2) se va la luz: activar los 3 interruptores del CIC → 3) llaves del conserje → 4) comida a la nevería → 5) 3 bidones de gasolina al camión → final del camión (60 s, como siempre).
- HUD: "Objetivo n/5" con el texto propio de Historia (contadores de bidones e interruptores incluidos).
- Señales: al cumplir, letrero "¡OBJETIVO n/5 CUMPLIDO!" con su sonido, y el HUD dice "¡Objetivo n/5 cumplido! Prepárense…". Pasados **2.5 s** se activa el siguiente, con el letrero "OBJETIVO n/5 · …" y el sonido de nuevo objetivo. Antes del final pasa lo mismo y luego sale "¡AL ESTACIONAMIENTO!".

**Revisión de ubicaciones y condiciones (cambios)**
- *Llamada:* en Escape primero hay que prender el servidor del SITE, y el SITE está tras la puerta P41 (restringida y electrónica: solo se abre a golpes, con 150 de vida, o con Carlos). Hoy se alcanzaba usándolo a través de la pared, porque la distancia de uso no toma en cuenta los muros. En Historia la llamada es directa en la computadora del CIC (3136, 1760; 20 s). Al CIC se entra por la puerta electrónica P43 (mantener F 8 s) o por las Salas 3 y 4 (puertas normales).
- *Interruptores:* los de Escape están uno en el SITE, otro en la Sala 3 y otro en el CIC. En Historia los tres están en el CIC: pared del pasillo CIC oeste (2736, 1640), salón del CIC (3336, 1760; el mismo de antes) y pared del pasillo CIC este (3696, 1640). Escape conserva los suyos.
- *Una sola vez:* cada objetivo se borra al cumplirse y `Paso = 99` avanza un solo número (lo comprueba la prueba manteniendo el objetivo hecho varios cuadros). **Corrección que también aplica a Escape:** si se recogían 2 bidones en el mismo cuadro contaba 1 y la gasolina quedaba imposible. Ahora suma `PickedInstancesCount(Bidon)`.
- Los "/3" y "ObjNum = 4" fijos usan `ObjTotal` (3 en Escape y Jefe, 5 en Historia), también en "Guía de los bots" y "Modo presentación (F1)".
- *En línea:* el texto del objetivo no llegaba a los clientes (sus eventos solo corren en el host). Ahora el host lo copia en `ObjTxt` (sincronizada) y los clientes lo muestran. Sirve para todos los modos. La sala se crea en modo `"historia"` (`net_core.js`: `N.preHist` con `OnlineEsc = 2`) y la sala muestra "Modo: HISTORIA".
- Variables nuevas de Juego: `ObjTotal`, `O4`, `O5`, `ObjEspera`, `ObjTxt` (todas sincronizadas).

**Menú**
- Tarjetas de 440 px en x 160 / 740 / 1320; los videos de Escape y Jefe se movieron con su tarjeta. La 3.ª tarjeta era una "EN LÍNEA" vieja sin instancias: ahora es HISTORIA, con la ilustración provisional `assets/interfaz/ilus_modo_historia.png` (una lista de 5 pasos, en el estilo de LOCAL / EN LÍNEA).
- Navegación: Izquierda/Arriba y Derecha/Abajo recorren las 3. Antes Derecha estaba en los dos eventos y se anulaba: no se movía. También tecla 3 y clic sobre cada tarjeta, que la elige y la confirma; antes el clic solo confirmaba la tarjeta ya seleccionada.
- Paso LOCAL / EN LÍNEA de Historia: copia de los eventos de Escape con `JT = 2`. Al volver de la sala en línea, `OnlineEsc = 1` regresa a Escape y `OnlineEsc = 2` a Historia.

**Pruebas** (`prueba_historia.py`, simula los eventos reales del proyecto)
- Historia: orden de los 5 objetivos y el final, victoria, llamada sin servidor, 3 interruptores dentro del CIC, carnada en la nevería, 2 bidones a la vez, los 5 letreros de cumplido y los 5 de nuevo objetivo con 2.5 s entre ellos, 5 + 5 sonidos, cada objetivo una sola vez, texto del HUD y `ObjTxt`.
- Escape: con tres semillas, mismos objetivos, objetos creados, letreros y resultado que el respaldo de antes de la fase 55, y el HUD sigue en "/3".
- Además: alcance con la máscara real de los pies (todos los puntos de objetivo se alcanzan; las llaves y el bidón de la conserjería solo tras la puerta restringida P59), `node --check` de los 38 eventos JS, `net_core.js` y la fase idempotente (mismo md5).

**Pendiente / sin cambiar**
- Nada se ejecutó dentro de GDevelop ni con dos máquinas: el menú con 3 tarjetas, el clic y los letreros en pantalla.
- La conserjería (llaves) sigue tras la puerta restringida P59: a golpes o con Carlos, igual que en Escape.
- La entrada a su pasillo mide 32 px entre dos esquinas de muro: un jugador cabe (sus pies miden 16 px de alto), pero la navegación de los bots no la cruza.
- `MejorTiempo` es uno solo para todos los modos: una victoria en Historia también puede guardarse como récord.
- La ilustración de Historia es provisional.


## Fase 56 · Interacción con F / A: una acción a la vez (2026-11-20)
Script: `scripts/fase56_interaccion.py` (idempotente; va después de `fase55`; respaldo `respaldos/antes_de_fase56_*.json`). Lógica en `scripts/usar.js` (evento JS `FDIZ-FASE56-MOD`). Pruebas: `node gdevelop/scripts/prueba_usar.js` (22 casos). Si se vuelve a correr una fase que regenere eventos de Juego, correr esta fase otra vez.

**Antes:** mantener F (A en el mando) hacía a la vez todo lo que estuviera al alcance: abrir una puerta, levantar a un caído, curar a un mordido, usar un objetivo y revisar un locker. R también abría puertas (y lanza objetos). Al soltar, el avance para levantar a alguien bajaba poco a poco.

**Ahora** (`usar.js`, lo decide el host o la partida sin red):
- Para cada jugador humano (teclado, mando o remoto) se elige **un** objetivo interactuable. Se usan los mismos alcances que los eventos:
  - levantar a un caído: 80 px;
  - curar a un mordido: 95 px;
  - puerta: 130 px, de los pies al centro;
  - objetivo: 140 px, centro a centro;
  - locker o mochila: 95 px;
  - profe esperando: 115 px.
- Gana el de menor distancia relativa a su alcance. Salvar (levantar o curar) cuenta × 0.75, por ser urgente.
- Mientras se mantiene F, se conserva el elegido aunque otro quede más cerca.
- **Nunca dos acciones con la misma pulsación.** Solo el elegido avanza: su bandera (`UsaPuerta`, `UsaRevivir`, `UsaCurar`, `UsaObjetivo` o `UsaCofre`) y `Elegida` en la puerta u objetivo. Si lo que se mantenía termina o queda fuera de alcance, hay que soltar F antes de empezar otra cosa (indicación «Suelta F para la siguiente acción»).
- **Cancelar:** al soltar o alejarse, el avance vuelve a 0:
  - puertas y lockers: ya era así;
  - curar: ya era así;
  - levantar: **nuevo**; antes bajaba poco a poco.
  - Los objetivos largos (la llamada de 20 s, interruptores...) conservan su avance como antes.
- **Indicación** sobre cada jugador local: «Mantén F para abrir», «Mantén F para abrir (electrónica, 8 s)», «Mantén F para salvar a P2», «Mantén F para curar a P3», «Mantén F para llamar», «Mantén F para revisar»... Con mando dice A. Mientras se mantiene, aparece una barra de avance. Los clientes en línea la ven para su jugador (`Accion`, `UsarTxt`, `UsarProg` sincronizadas).
- **Requisitos que se respetan:**
  - Puertas restringidas sin derribar (`TiempoAbrir` 0): no se abren con F y avisan «Puerta restringida: derríbala a golpes». La llave maestra de Carlos (especial) y los golpes funcionan igual que antes.
  - Electrónicas: 8 s, o 1 s con la tarjeta, como antes.
  - El camión del final no se «usa».
- **Profes:** el diálogo para reclutar solo se ofrece y abre si, para ese jugador, F es para el profe (`gdjs.fdizUsar.permite`). Curar a un profe mordido lee `UsaCurar`. `profes.js` se volvió a incrustar.
- **Bots y profes aliados:** sin cambios. Todas sus banderas valen lo mismo que `Usando` y todas las puertas y objetivos a su alcance quedan elegidos.
- **Eventos:**
  - Se quitaron los dos de «R para abrir puertas»: el del teclado y el del jugador remoto (`NetDr`).
  - Levantar usa `J<n>Rev` y curar usa `J<n>Cur`, en lugar de `J<n>Usa`, que se conserva para lo demás.
- **Textos:** controles del menú de pausa («F (mantener)  abrir puertas, salvar, revisar y usar objetivos», igual con A) y su fuente `fase27_jefe_y_controles.py`, comentarios de los eventos y `fase17_navegacion.py`, y la sección de teclas del LEEME. Las imágenes de controles de la pausa no tienen texto de acciones, así que no cambian.

**Pruebas:**
- `prueba_usar.js` cubre:
  - indicación sin mantener;
  - puerta sola;
  - puerta y caído (elige uno), y la puerta mucho más cerca;
  - conservar lo elegido;
  - soltar después de terminar;
  - alejarse;
  - puertas restringida y electrónica, con y sin tarjeta;
  - curar;
  - mando, remoto y bots;
  - objetivo y camión del final;
  - locker;
  - profe;
  - caído.
- También revisa en el proyecto que los eventos de puertas, levantar, curar, objetivos, lockers, textos y `profes.js` quedaron conectados.
- Siguen pasando `prueba_profes.js` (16), `prueba_correr.js` (13) y `prueba_historia.py` (17); los 41 eventos JS compilan y la fase es idempotente (mismo md5).
- **Sin probar** dentro de GDevelop ni con mandos reales o dos máquinas: cómo se ve la indicación, la barra y el tacto de la elección.


## Fase 57 · Volumen de música y efectos; música en «Elige el modo» (2026-11-20)
Script: `scripts/fase57_volumen.py` (idempotente; va después de `fase56`; respaldo `respaldos/antes_de_fase57_*.json`). Lógica en `scripts/audio.js` (evento JS `FDIZ-FASE57-MOD` al inicio de **todas** las escenas). Pruebas: `node gdevelop/scripts/prueba_audio.js` (17 casos). Si se vuelve a correr una fase que regenere eventos (en especial `fase25_online.py`, que pone la compuerta de host a los eventos JS sueltos de Juego), correr esta fase otra vez.

**Por qué no sonaba música en «Elige el modo»:** GDevelop detiene todos los sonidos al empezar una escena. El Título ponía `musica/menu.ogg`, pero al pasar a Menu se cortaba y Menu no tenía ningún evento de música. La sala en línea (Online) tampoco tenía. Ahora las dos ponen la música del menú al entrar (DepartScene, canal 1, 45 %, como el Título). Como cada escena detiene la anterior al empezar, y en el mismo canal la música nueva reemplaza a la vieja, nunca suenan dos a la vez.

**Volumen:**
- Variables globales `VolMusica` y `VolEfectos`, de 0 a 100 en pasos de 10. Por defecto valen 100, que es como sonaba antes.
- `audio.js` las limita a ese rango en cada cuadro.
- Se conservan al cambiar de escena, porque son globales, y además se guardan en el navegador (`localStorage` «fdiz_volumen») para la próxima vez que se abra el juego.

**Cómo se aplica:**
- `audio.js` envuelve `createHowlerSound` del gestor de sonido de GDevelop, que es la función por la que pasan todas las formas de reproducir: `playSound`, `playSoundOnChannel`, `playMusic` y `playMusicOnChannel`.
  - Cada efecto nuevo sale con su volumen × `VolEfectos` / 100.
  - Cada música nueva, × `VolMusica` / 100.
  - No hubo que tocar las ~45 acciones de sonido del proyecto, y sus volúmenes de la fase 21 se respetan.
- Al cambiar una barra se actualiza también lo que ya está sonando (la música de fondo baja o sube al instante).
- El audio de los videos (fondos y personajes del menú, resultados) cuenta como música y conserva su volumen base (3 %, 12 %).
- El módulo se aplica al inicio de cada escena, antes de su música, así que la música de cada pantalla ya empieza con el volumen elegido.

**Pantalla:**
- En el menú de pausa, el botón CONTROLES ahora dice **AJUSTES**. Su pantalla se llama «CONTROLES Y SONIDO»: los controles de siempre arriba y, abajo, un bloque SONIDO con dos filas, MÚSICA y EFECTOS (− / barra de 10 segmentos / + / porcentaje, o «SIN SONIDO» en 0), y VOLVER.
- **Teclado:** W/S o ↑/↓ eligen la fila, A/D o ←/→ ajustan, y Enter o Espacio en VOLVER sale. Retroceso también sale.
- **Mando:** la cruceta o el stick izquierdo ajustan y A en VOLVER sale. Un paso por pulsación: mantenerlo no repite.
- **Ratón:** clic en − o +, clic sobre la barra (fija ese valor) y clic en VOLVER.
- Al mover EFECTOS suena un efecto corto de prueba.
- Antes esa pantalla se cerraba con cualquier Enter, Espacio, clic o A. Ahora no, para poder ajustar: se cierra con VOLVER, Retroceso o B del mando. Esc sigue quitando la pausa.

**Límite conocido:** en línea no hay menú de pausa (ya era así), así que ahí no se puede ajustar el volumen. Sí se usa el que quedó guardado, y en los clientes el módulo corre igual: aplica su volumen local.

**Pruebas:**
- `prueba_audio.js` cubre:
  - 100 % igual que antes;
  - música y efectos por separado, incluida la música que ya suena;
  - límites y pasos de 10;
  - cambio de escena;
  - guardado entre sesiones;
  - una sola música por canal;
  - videos;
  - la pantalla con teclado, mando y ratón: Enter no cierra fuera de VOLVER y Retroceso sí;
  - que no se dibuja fuera de esa pantalla.
- En el proyecto revisa:
  - que el módulo esté en las 5 escenas antes de su música;
  - que la música del menú esté en Menu y Online, una sola vez;
  - los textos de la pausa, que la pantalla solo se cierre con B, los objetos nuevos y las globales.
- Siguen pasando `prueba_usar.js` (21), `prueba_profes.js` (16), `prueba_correr.js` (13) y `prueba_historia.py` (17); los 52 eventos JS compilan y la fase es idempotente (mismo md5).
- **Sin probar** dentro de GDevelop: oírlo, el acomodo exacto del bloque SONIDO bajo los textos de controles y los mandos reales.


## (Antes «Fase 46» local) · Conserje atravesando puertas: reemplazada por la fase 43 de cesar (2026-11-21)
Esta corrección se hizo localmente como `fase46_zombi_puertas.py` + `zombi_puertas.js`, pero el pull del 2026-11-21 trajo `fase43_criticos.py` de cesar, que arregla lo mismo: máscara de pies del conserje y `criticos.js → puertas()`. Para no tener dos seguros que se pisen, se quitaron el script, el módulo y su prueba locales, y se quedó el de cesar. La máscara generada en `fase19_correcciones.py` (atacar_arriba con máscara de pies) se conserva porque no choca con la suya.


## Fase 58 · Efectos de sonido del repositorio (`sonidos_nuevos/`) (2026-11-21)
Script: `scripts/fase58_sonidos.py`. Es idempotente y solo usa la biblioteca estándar: `python -I gdevelop/scripts/fase58_sonidos.py`. Lee de `FDI-Z/sonidos_nuevos/` (subido por el equipo, que no se modifica) y escribe copias procesadas en `FDI-Z/efectos/<categoría>/<nombre>.wav`. Mediciones en `FDI-Z/efectos/fase58_informe.json`. Si se vuelve a correr `fase21_proyecto.py`, hay que correr esta fase otra vez.

Antes del pull, esta fase local (llamada «fase 47») había reemplazado 13 efectos con archivos de la carpeta 2dsounds. El pull trajo `sonidos_nuevos/`: las mismas grabaciones de 2dsounds, renombradas por el equipo según el uso que les quiere dar, todavía sin conectar al proyecto. **Regla: manda el repositorio.**
- Si el repositorio trae un archivo para un efecto, se usa ese archivo.
- Si un archivo que yo había elegido el repositorio lo destinó a otra cosa, ese efecto vuelve a su `.ogg` original.
- Una elección propia solo se mantiene cuando el repositorio no le da otro uso a ese archivo.

**Ahora usan el archivo del repositorio (6)**

| Efecto del juego | Archivo de `sonidos_nuevos/` | Duración |
|---|---|---|
| Golpe a la puerta (`mundo/puerta_golpe`) | door_punch.wav | 0.41 s |
| Minigun de Miranda (`habilidades/miranda_especial`) | minigun.wav | 2.48 s |
| Habilidad de Tony, cocinar (`habilidades/tony_habilidad`) | tony_cook_sound.wav | 0.39 s |
| Especial de Tony (`habilidades/tony_especial`) | tony_powerup.wav | 1.14 s |
| Especial de Castillo, poción (`habilidades/castillo_especial`) | powerup_generic_sound.wav | 0.39 s |
| Moneda (`mundo/moneda`) | FNF_EBA_fx_misc_coin_collector.wav | 0.34 s |

**Vuelven a su `.ogg` original (9)**, porque el repositorio le dio ese archivo a otro uso:
- apagón: concierge_death_effect
- interruptor: minigun_ednd_sound
- objetivo nuevo: main_menu_start_sound
- habilidad de Alan: item_collected
- objetivo cumplido: tony_cook_sound
- habilidad de Gabo: tony_powerup
- habilidad de César: start_game_sound
- mordida: kick_sound_effect
- paso de objetivo: zombie_death

Sus WAV locales se borraron, y todas las referencias en los eventos, el JS incrustado, `profes.js`, `audio.js` y el manifiesto volvieron al `.ogg`. El sonido de prueba del volumen vuelve a ser `mundo/interruptor.ogg`.

**Sin conectar todavía**: se dejan para quien los subió, porque su uso no es un efecto que ya exista:
- punch1-4
- zombie_death_2/3
- item_collected
- start_game_sound
- main_menu_start_sound
- concierge_death_effect
- minigun_ednd_sound
- kick_sound_effect
- los BULLYFINGER
- las músicas `main_menu*.MP3`

**Formato y volumen**
- WAV PCM 16 bits mono, a 48 kHz (bajado desde 96 kHz con filtro) o a 44.1 kHz.
- Sin silencio al inicio, y la cola no se corta.
- Pico a −1 dBFS y promedio limitado a −16 dBFS.
- Los volúmenes de cada evento no cambian.
- `validar_audio.py --check` revisó 44 y no encontró problemas.

**Sin probar:** escucharlos dentro de GDevelop.


## Fase 59 · Revólver (tipo sheriff) y escopeta (2026-11-20; desde la fase 62: sheriff con 4 balas y en la Dirección, y pistola pequeña inicial: ver abajo)
Scripts: `scripts/fase59_arte_armas.py` (arte y sonidos, solo Pillow) y `scripts/fase59_armas_fuego.py` (proyecto; idempotente; va después de `fase58`; respaldo `respaldos/antes_de_fase59_*.json`). Pruebas: `python gdevelop/scripts/prueba_armas_fuego.py` (7 casos).

**Integración con el sistema de armas que ya existía**
- Son `ArmaPiso` con `Tipo` `pistola` (el revólver) y `escopeta`, los nombres que ya usaban los íconos del HUD.
- Se recogen igual que las demás: pasando encima con los puños.
- `Usos` es la munición: se gasta 1 por disparo con la regla de siempre y, al llegar a 0, vuelven los puños.
- `DanioArma`, `Alcance` y `Cadencia` se ponen en «Armas del salón», como las otras armas. El daño se multiplica por `Fuerza`.
- Nueva variable `Sup.ArmaFuego` (1 con estas dos armas). Con ella el ataque no crea el golpe cuerpo a cuerpo: dispara con el objeto `Proyectil` de los lanzables, el mismo de la engrapadora. Ese proyectil:
  - daña al primer zombi a 46 px;
  - se detiene en muros y puertas;
  - acredita la baja con `UltJugador`.
- `Proyectil.Dura` = `Alcance` / 4 s. Los lanzables siguen en 0.9 s.
- Las balas y los perdigones no quedan tirados como lanzables.

| Arma | Usos (munición) | DanioArma | Alcance | Cadencia | Disparo |
|---|---|---|---|---|---|
| pistola (revólver) | 6 | 24 por bala | 2.4 → 0.6 s a 1000 px/s ≈ 600 px | 0.55 s | 1 bala, empuje -120 |
| escopeta | 6 | 9 por perdigón (×5 = 45) | 1.2 → 0.3 s a 900 px/s ≈ 270 px | 0.95 s | 5 perdigones a -12/-6/0/6/12°, empuje -90 |
Para comparar: el bate hace 21 de daño con alcance 1.25 y cadencia de 0.5 s (24 usos), y la engrapadora 9 por grapa.

**Arte y sonido**
- `generado/sprites/objetos/armas/pistola.png`: revólver de vaquero nuevo, 42 × 30 px, pixel art con el contorno del juego. Tiene tambor estriado, cañón largo, cacha de madera y remate dorado.
- `generado/sprites/objetos/armas/escopeta.png`: 32 × 32 px, reducida del ícono que ya existía.
- `generado/sprites/objetos/lanzables/bala.png` y `perdigon.png`.
- HUD: `escopeta` usa su ícono de siempre. `pistola` ahora muestra `assets/interfaz/hud/ico128_arma_revolver.png`, el revólver ×3; el ícono de pistola semiautomática se queda en su carpeta, sin uso.
- `efectos/combate/revolver.wav` y `escopeta.wav`: ruido más un golpe grave, en 8 bits como los demás, de 0.42 y 0.62 s. Suenan al 70 %.

**En el mapa**
- **Escopeta: (5136, 650)**, con el origen en los pies (abajo al centro), en la conserjería.
  - Está a la derecha de las llaves del objetivo, en (5056, 640), a 80 px, y no las tapa (hay 55 px entre sus dibujos).
  - Queda en piso libre, lejos de los estantes y del bote de basura.
  - La conserjería tiene la puerta restringida P59: se entra derribándola o con Carlos, igual que para las llaves.
- **Revólver: pendiente.** La sala de la imagen de referencia no se pudo identificar porque la imagen no llegó. Basta con poner su posición en `POS["pistola"]` de `fase59_armas_fuego.py` y volver a correrlo.

**Pruebas** (`prueba_armas_fuego.py`):
- que los recursos existan;
- que la escopeta esté dentro de la conserjería, fuera de muros, muebles y puertas, sin encimarse con el dibujo de los muebles ni con las llaves, a 50-140 px de ellas;
- que un jugador alcance a tocarla, con la caja real de sus pies;
- que recogerla ponga los valores correctos;
- el disparo: 1 bala o 5 perdigones, con el daño del arma por `Fuerza`, sonido, gasto de munición y sin golpe cuerpo a cuerpo;
- los proyectiles: se detienen en muros, duran según su alcance y no quedan en el piso.

Siguen pasando las demás pruebas y el validador de audio (44), y los 54 eventos JS compilan. **Sin probar** dentro de GDevelop.


## Pull del 2026-11-21 · Compatibilidad de las fases locales con las 43-54 de cesar
Las fases locales que no se habían subido se renumeraron después de las del repositorio:
| Antes | Ahora |
|---|---|
| fase43_historia | fase55_historia |
| fase44_interaccion | fase56_interaccion |
| fase45_volumen | fase57_volumen |
| fase46 | reemplazada por fase43_criticos de cesar |
| fase47_sonidos | fase58_sonidos |
| fase48_armas | fase59_armas |

Todas se volvieron a aplicar sobre el `FDI-Z.json` del pull. La copia local de antes quedó en `respaldos/local_antes_del_pull_20261121/` y en el stash «local antes del pull 2026-11-21».

**Ajustes para que convivan:**
- `medios.js` (llaves, fase 46 de cesar): el texto «toma las llaves… %» solo cuenta a quien el árbitro de la F le dio ese objetivo (`UsaObjetivo` y `Elegida`). Así ya no se ve un progreso que no avanza cuando la F de ese jugador iba a otra cosa. Es un cambio de una línea; la fase 56 vuelve a incrustar `medios.js` en `FDIZ-FASE46-MOD`.
- Pausa: cesar cambió los textos de controles por imágenes (fase 49, en y 300-700) y los vació. Las filas de volumen (y 832 y 882) quedan debajo, sin encimarse. La prueba de textos ahora acepta que estén vacíos.
- Lanzables (fase 52 de cesar): el impacto en área y la distracción solo aplican a balón y libro, así que las balas y los perdigones no los activan. El aviso del primer lanzable usa `Sup.Lanz`, no las armas.

**Pruebas sobre el proyecto final:**
| Prueba | Resultado |
|---|---|
| audio | 17 |
| interacción | 22 (una nueva: llaves con el árbitro) |
| profes | 16 |
| correr | 17 |
| medios | 9 |
| Historia | 17 |
| armas de fuego | 7 |
| `validar_audio --check` | 44, sin problemas |

Además, los 67 eventos JS compilan, todas las marcas de cesar siguen (43, 46, 48-53), y volver a correr las fases 55-59 deja el mismo md5. **Sin probar** dentro de GDevelop.


## Fase 60 · Efectos de sonido de «sonidos 2d» (2026-11-21)
Script: `scripts/fase60_sonidos2d.py`. Es idempotente; se corre con `python -I gdevelop/scripts/fase60_sonidos2d.py`, va después de `fase59` y deja un respaldo en `respaldos/antes_de_fase60_*.json`.
- Lógica en `scripts/sfx.js`, que se incrusta como `FDIZ-FASE60-MOD` y `-TICK` en **todas** las escenas, sin compuerta de host.
- Pruebas: `node gdevelop/scripts/prueba_sfx.js` (17 casos).
- Si se vuelve a correr una fase que regenere eventos (sobre todo `fase25_online.py`), hay que correr esta otra vez.

**Archivos**
- Los 22 `.ogg` de `Videojuego2D/sonidos 2d/sonidos 2d/ogg` se copiaron a `fdiz/sonidos/`.
- Se registraron como recursos de audio con el mismo nombre del archivo (`ui_click.ogg`, …). La ruta es `../../sonidos/<nombre>.ogg`, relativa a `FDI-Z.json`.
- También se agregaron al manifiesto de audio: `validar_audio.py` revisa 66, sin problemas.

**Cómo suenan**
- Casi todos los pone `sfx.js`, que compara cada cuadro lo que cambió: vida, estado y animación de jugadores y zombis, y las variables de escena.
- Corre en cada máquina con los datos que ya se sincronizan. Reproduce con la función original de GDevelop, sin el reenvío por red de `net_core`, así que en línea los clientes oyen lo mismo sin duplicados. La interfaz suena solo en la máquina de quien la usa.
- Volumen: efectos 70–100 e interfaz 50–60. La música queda en 40–50. Ajustes → Efectos (fase 57) escala todo.
- Ninguno va en loop.
- Pitch aleatorio ±0.1 en golpes, dolor y growl.
- Zombis: normal 1.0, gordo y conserje 0.7, corredor 1.3. Gritón y profes zombi: 1.0.
- Dolor: 0.8 para todos, Miranda 1.0.
- Cooldown corto: golpes, mordida, dolor, monedas, ataques y muertes 0.1 s; aparición 0.25 s; hover 0.08 s.
- Los sonidos de un zombi (aparición, golpe, ataque, muerte) solo suenan a menos de 1300 px del centro de la cámara.
- El growl suena cada 0.8–2 s: un zombi cercano al azar, que repite entre 5 y 12 s después. Volumen 80 × (1 − d/1000)^1.3, y no suena si queda por debajo de 12. No gruñen los dormidos, congelados, muertos ni aliados.
- En pausa no suena nada del mundo.

| Sonido | Escena | Evento (qué lo dispara) |
|---|---|---|
| ui_click | Menu, Juego (pausa), Resultados, Online | Clic sobre un botón; cambiar de paso del menú; elegir personaje, control o dificultad; abrir o cerrar la pausa o cambiar su vista; elegir carta del Jefe; cambiar de pantalla en la sala en línea |
| ui_hover (50) | Menu, Resultados, Juego, Online | El cursor entra a un botón (MarcoModo, SelMarco, DifBtn, EqCelda, EqRet, BtnSalir, BtnRei, BtnMenuR, PausaBtn, JfCarta); mover la selección con teclado o mando |
| ui_confirm | Menu, Juego, Online | LISTO de un jugador; todos listos; empezar partida (al entrar a Juego); compra del Jefe con oro; entrar a la sala en línea |
| ui_error | Juego, Online | Error del Jefe (falta oro, recargando, bloqueada, zona visible, no cabe); F en una puerta restringida; error de red |
| golpe_impacto | Juego | A un jugador o a un zombi le baja la vida |
| jugador_dolor | Juego | Un jugador recibe daño (pitch por personaje) |
| cuerpo_caida | Juego | Un jugador cae (Estado «caido») o muere un zombi |
| whoosh_esquivar | Menu, Online, Juego | Al entrar a Menu u Online (transición); el jugador ataca (animación «pegar», no con armas de fuego) |
| zombie_growl | Juego | Zombi cerca de la cámara, intervalo aleatorio, volumen según la distancia |
| zombie_ataque | Juego | Un zombi empieza la animación «atacar» |
| zombie_mordida | Juego | Un zombi le conecta daño a un jugador |
| zombie_muerte_01 / _02 | Juego | Un zombi pasa a «muerto» (uno al azar) |
| zombie_spawn_braam | Juego | Aparece un zombi nuevo (infestación, horda, convertido, invocación del Jefe); los del mapa al empezar no |
| oro_moneda | Juego | Se recoge una moneda; cambia el Dinero; el Jefe gana o gasta oro (solo en su máquina) |
| objeto_recoger | Juego | Tomar un arma, un lanzable, comida guardada, la bolsa o las llaves; tomar y entregar el bidón (evento) |
| puerta_casillero | Juego | Se abre una puerta o un locker/mochila/máquina, y se abre la salida (eventos) |
| curar_powerup | Juego | Un jugador recupera 5 o más de vida de golpe (comida, pociones, habilidades); lo levantan |
| oleada_riser | Juego | Sube la infestación (evento del HUD); llega una horda; empieza la cuenta regresiva del final |
| evento_impacto_cinematico | Titulo, Juego | Al entrar al título; empieza el final (alarma, evento); el conserje (jefe) aparece o empieza a perseguir; empieza el modo Jefe |
| game_over | Resultados | Al entrar si no fue victoria |
| victoria | Resultados | Al entrar si fue victoria (escapar o ganar) |

**Cambios en eventos de Juego:**
- puerta_abrir, locker y bidón ahora usan los sonidos nuevos.
- infestacion_sube pasó a oleada_riser y final_inicio a evento_impacto_cinematico.
- La sirena de escape suma puerta_casillero.
- Se quitaron comer, mordida, victoria.ogg (Resultados) y jefe_invocar (en `jefe_modo.js`), porque ahora los pone `sfx.js`.
- Se conservan los sonidos propios que no estaban en la lista: habilidades y especiales, objetivos, interruptor, apagón, golpe a puerta, sirena de escape, convertido, lanzar y las armas de fuego.

**Pendientes, preparados:**
- `// TODO: footsteps`: evento desactivado en «Movimiento y animación» que usaría `pasos.ogg`.
- `// TODO: música de partida / tensión`: evento desactivado en «Música y sonido de fondo» que usaría `musica_tension.ogg` (canal 1, 45, loop). Se dispara con `OleadaInicio`, que `sfx.js` pone en 1 durante un cuadro cuando empieza una oleada.
- Para usarlos: importar el archivo y activar el evento. `fase58` ya no revisa los eventos desactivados.
- El juego **no tiene** esquivar; el whoosh se usa en ataques y transiciones.
- Las monedas del modo Jefe todavía no tienen evento para recogerlas; cuando lo tengan, sonarán solas.

**Sin probar:** escucharlo dentro de GDevelop. Tampoco se probó que la vista previa y la exportación encuentren los archivos fuera de la carpeta del proyecto (`../../sonidos/`).


## Fase 61 · Historia: hablar con Canepa en el camión antes de la gasolina (2026-11-22)
Scripts, ambos idempotentes y en este orden:
- `scripts/fase55_historia.py` (actualizado): el orden, el HUD, el letrero, el punto de la misión y el evento que abre la charla.
- `scripts/fase61_canepa.py` (nuevo): la charla con burbujas, en `scripts/canepa.js`.

Pruebas:
- `node gdevelop/scripts/prueba_canepa.js` (18 casos).
- `python gdevelop/scripts/prueba_historia.py` (21 casos).

Respaldo: `respaldos/antes_de_fase61_*.json`.

**Orden de Historia (6 misiones).** Las cuatro primeras no cambian.

| # | Misión | Se cumple con |
|---|---|---|
| 1 | Llamar desde la computadora del CIC | Mantener F 20 s |
| 2 | Activar los 3 interruptores del CIC | Los tres interruptores |
| 3 | Llaves del conserje | Las toma un jugador |
| 4 | Llevar comida a la nevería | Entregar la bolsa |
| 5 | **Hablar con el profe Canepa en el camión** | Mantener F 0.6 s junto a Canepa (544, 3328); al terminar el diálogo se cumple |
| 6 | Buscar la gasolina: 3 bidones al camión | Igual que antes |
| — | Final ¡Aguanten! | Igual que antes |

- **HUD:** «Objetivo 5/6 · Hablen con el profe Canepa en el camión».
- **Letrero:** «OBJETIVO 5/6 · HABLAR CON CANEPA EN EL CAMIÓN».
- **Indicación:** «Mantén F para hablar con Canepa».
- **Menú:** la tarjeta dice «6 misiones».
- **Una sola vez:** `CanepaCharla` pasa de 0 a 1 a 2 y nunca vuelve. El evento que abre la charla pide `CanepaCharla = 0`, y el punto de la misión se borra al usarlo. Volver a mantener F o repetir la interacción no hace nada.
- **Misión cumplida:** `canepa.js` pone `Paso = 99` solo al pasar de 1 a 2. Después siguen el letrero de cumplido, la pausa de 2.5 s y la gasolina.

**La charla (`canepa.js`)**
- **Mundo congelado.** El host (o el juego sin red) pone `Estado = "dialogo"` y `TimeScale = 0`, así que zombis, bots, tiempos y profes se detienen. La pausa no se puede abrir porque pide `Estado = "juego"`.
- **Sin control.** Los jugadores humanos, locales y remotos, quedan con `Control = -2`, como en la intro. Al terminar se devuelve todo como estaba.
- **Saltar líneas.** Las líneas van en orden y cada una dura lo que tarda leerla: 2.4–6.5 s. F, Enter, Espacio, clic o A la adelantan después de 0.6 s. Mantener la tecla no salta más de una.
- **En línea.** `CanepaCharla`, `CinLinea` y `CinHabla` viajan a los clientes, que dibujan la misma burbuja.
- **Quién habla.** Las líneas de Canepa las dice el profe (instancia `Profe` «canepa»). Las de Tony y Miranda, ellos si están en el equipo. Si no, las dice otro del equipo, primero los que están de pie; la burbuja muestra el nombre de quien habla.
- **Burbujas.** Tienen el estilo de las de los profes: `TxtProfe` sobre `ProfPanel`, nombre en amarillo y una colita (`DlgDib`, objeto nuevo copiado de `ProfDib`).
  - Van encima de la cabeza de quien habla.
  - Si ahí tapan el HUD (paneles, letrero, ayuda, minimapa), una cara o el letrero visible, se corren a un lado o bajan a los pies.
  - Solo hay una a la vez y se retira al terminar.
- **Reclutamiento.** Mientras `CanepaCharla < 2`, en Historia `usar.js` y `profes.js` no ofrecen a Canepa para reclutar. Así nadie lo rechaza ni lo vuelve zombi antes de la charla. Después se le puede reclutar como siempre, y en Escape y Jefe no cambia nada.

**Diálogo (en este orden)**
1. Canepa: «¡Llegaron! Necesito ayuda. El autobús no puede salir.»
2. Tony: «¿Qué pasó?»
3. Canepa: «No queda suficiente gasolina. Sin combustible no podremos alejarnos del campus.»
4. Miranda: «Acabamos de distraer a la horda. Podemos buscar gasolina.»
5. Canepa: «Gracias. Revisen el campus, pero tengan cuidado.»
6. Tony: «De acuerdo. Vamos a encontrarla.»

**Voces**
- En el proyecto no hay voces: no hay ningún recurso de voz.
- `audios_fish/` tiene 76 WAV de Alan, Castillo, César, Miranda y Tony, y cada carpeta trae una `lista.txt` con la frase de cada archivo. Ninguno dice estas líneas: son de otras situaciones (caer, revivir, escapar, abrir puertas…).
- Canepa es profe y no tiene voz: sus líneas van solo con texto, como se pidió.
- Ninguna línea quedó con audio. Las burbujas funcionan solas.

| Línea | Personaje | Archivo |
|---|---|---|
| 1, 3, 5 | Canepa | — (profe, sin voz: omitido) |
| 2 «¿Qué pasó?» | Tony | **falta** |
| 4 «Acabamos de distraer a la horda…» | Miranda | **falta** |
| 6 «De acuerdo. Vamos a encontrarla.» | Tony | **falta** |

**Cuando lleguen las voces**
- Se registran en `C.VOCES` de `canepa.js`, por ejemplo `C.VOCES[1] = { pj: "tony", archivo: "<recurso>" }`, después de importar el archivo como recurso.
- Suenan en un solo canal (7), así que no se enciman. La línea espera a que termine la voz (máximo 10 s).
- Si otro personaje dice esa línea, la voz no se usa.
- Si el archivo falta o no carga, la línea sigue con texto.

**Sin cambios:** Escape (tres semillas, igual que el respaldo anterior a la fase 55), Jefe, las misiones 1–4, el final y el resto de `profes.js` y `usar.js`. Los recursos no se tocaron.

**Sin probar:** jugarlo dentro de GDevelop (posición real de las burbujas con la cámara y el texto de verdad) y en línea con dos máquinas.


## Fase 62 · Uso de las armas: pistola pequeña inicial, mira, munición en el HUD y animación con pistola (2026-11-22)
Todos los modos: Escape, Historia y Jefe; sin red, host y clientes. Scripts:
- `scripts/fase59_armas_fuego.py` (actualizado): datos de las armas, disparo y lugar del sheriff. Ahora reescribe valores en cada corrida.
- `scripts/fase62_arte_pistola.py` (nuevo, solo Pillow): mira y animaciones placeholder.
- `scripts/fase62_armas_uso.py` (nuevo, idempotente): integración. La lógica está en `scripts/armas.js`.

Pruebas:
- `node gdevelop/scripts/prueba_armas.js` (11 casos).
- `python gdevelop/scripts/prueba_armas_fuego.py` (7 casos; ahora revisa también al sheriff).

Respaldo: `respaldos/antes_de_fase62_*.json`.

**Munición.** Es la regla que ya existía: `Usos` = balas, 1 por disparo y al llegar a 0 vuelven los puños. **No hay recarga**, así que no se inventaron reservas.

| Arma (`Sup.Arma`) | Balas | Daño | Alcance | Cadencia | Cómo se consigue |
|---|---|---|---|---|---|
| `pistolita` (pistola pequeña) | 9 | 12 por bala | 2.0 (~500 px) | 0.4 s | Inicial del **jugador 1** (solo él), en todos los modos |
| `pistola` (revólver sheriff) | **4** (antes 6) | 24 por bala | 2.4 (~600 px) | 0.55 s | En el piso de la **Dirección**, en (3400, 4470), detrás de la puerta P47 (3296, 4544) |
| `escopeta` | 6 | 9 × 5 perdigones | 1.2 (~270 px) | 0.95 s | Conserjería, en (5136, 650), sin cambios |

- **Pistola pequeña:** dispara una bala con el mismo sonido del revólver, pero con pitch 1.3. Su ícono en el HUD es `ico128_arma_pistola.png`, que ya estaba en el repo sin usarse.
- **Mientras tenga la pistola:** el jugador 1 no recoge otra arma, porque la regla de siempre solo deja recoger con los puños.
- **En la intro:** el jugador 1 ya no recibe la regla, porque no tiene los puños. La silla y la escoba siguen en el piso, pero la línea «¡Agarra la regla!» del diálogo de la intro quedó igual.
- **Sheriff:** queda dentro de la Dirección, sin encimarse con los muebles ni con el bate del botín raro, y un jugador puede llegar a él. La puerta P47 es restringida: se entra derribándola o con Carlos.

**Mira (indicador de apuntado)**
- Es una cruz hueca de 11 × 11 px (`generado/sprites/objetos/armas/mira.png`) con contorno oscuro. No tapa lo que hay debajo.
- Va a 78 px del arma, hacia donde apunta el jugador (`AimX`, `AimY`).
- Si queda sobre un personaje o un zombi se vuelve más transparente (opacidad 110 en vez de 210).
- **Cuándo se ve:** solo para jugadores, no para bots, de pie, con arma de fuego y balas, en juego.
- **Cuándo se esconde:** en pausa, en la intro y en la charla con Canepa. Cada máquina dibuja la suya y no viaja por la red.

**Munición en el HUD**
- En el panel de cada jugador aparece el número de balas a la derecha del ícono del arma (`TxtBalas`, mismo estilo que los tiempos de las habilidades). Se pone rojo con 2 o menos.
- Debajo del ícono se ve el cargador completo con una marca por bala (`BalasDib`): las que quedan en dorado y las gastadas en gris.
- Solo aparece con armas de fuego, y no en la intro ni si el panel del jugador está oculto.

**Animaciones (placeholders)**
- Al disparar con pistola, pequeña o sheriff, de lado o hacia abajo, se usa `<personaje>_pistola_lado` o `<personaje>_pistola_abajo`, en lugar de `_pegar_` (`armas.js` las cambia en el host y llegan a los clientes por la red).
- Se hicieron para los 12 personajes de `Sup`: los 8 alumnos, Tony gym y los 3 profes.
- **Cómo se hicieron:**
  - De lado: el cuadro del brazo estirado de `pegar_lado`, con una pistola de 13 × 8 px en el puño.
  - Hacia abajo: la guardia de frente de `pegar_abajo`, con la pistola de frente en el puño derecho.
  - Tres cuadros en total; el del medio tiene retroceso de 1 px y fogonazo.
- Tienen el mismo origen y la misma máscara de colisión que la base.
- **Respaldo (fallback):**
  - Hacia arriba no hay animación de pistola: se queda `pegar_arriba`.
  - Con la escopeta sigue la de pegar.
  - Si a un personaje le faltara la animación, GDevelop no la cambia y sigue la de pegar. Nunca queda invisible ni detenido.

**Recursos**
- Nuevos: `mira.png` y 72 cuadros `pistola_lado/abajo_00..02.png`, en la carpeta de cada personaje en `generado/sprites`.
- Se generó `objetos/armas/pistolita.png` para un futuro sprite de piso, pero no se registró porque ningún objeto la usa.
- No se borró ningún recurso.

**Sin probar:** jugarlo dentro de GDevelop (cómo se ven la mira, el número y las animaciones en movimiento) y en línea.


## Fase 63 · Color de los letreros de eventos: rojo solo para infección y FDI llenándose (2026-11-22)
Script: `scripts/fase63_avisos.py` (idempotente). Lógica: `scripts/avisos.js`. Pruebas: `node gdevelop/scripts/prueba_avisos.js` (6 casos). Respaldo: `respaldos/antes_de_fase63_*.json`. Todos los modos.

**Por qué salían rojos.** Todos los letreros de la partida pasan por la variable `Banner` y se muestran con el objeto `TxtBanner`. Ese objeto tenía rojo fijo (255;80;80) y ningún evento lo cambiaba.

Escriben en `Banner`:
- eventos de los grupos «Objetivos y flecha», «Final ¡Aguanten!», «Compañeros mordidos», «Habilidades», «HUD», «Puertas» y «Unirse con control»;
- `profes.js` y `medios.js`.

Por eso se corrigió en el único punto por donde pasan todos: donde se muestra el letrero. Así ningún mensaje queda fuera.
- `TxtBanner` ahora es verde por defecto (110;230;110).
- `FDIZ-FASE63-COLOR`, dentro del evento del grupo «HUD» que pone el texto del letrero, aplica el color que corresponde al texto visible. Solo lo recalcula cuando el texto cambia.

**Regla de color.** El texto se normaliza antes de clasificar: minúsculas, sin acentos ni signos, espacios simples.
- **Rojo:** «mordido / mordida», «infectado / infectada», «se convirtió en zombi / zombie», «la FDI se está llenando».
- **Excepciones a lo rojo:** «salvado», «curado» o «ya no» lo vuelven verde.
- **Verde:** todo lo demás: objetivos nuevos y cumplidos, «¡AGUANTEN!», «¡ESCAPARON!», «salvado», profes que se unen, llaves, tarjeta, servidor, festín, «¡SE FUE LA LUZ!», «quedó fuera de combate», «se quedó atrás»…
- **Letreros rojos de hoy:** «¡Pn MORDIDO!», «¡Pn SE CONVIRTIÓ EN ZOMBIE!», «¡<PROFE> MORDIDO!», «¡<PROFE> SE CONVIRTIÓ EN ZOMBI!» y «¡LA FDI SE ESTÁ LLENANDO!».

**No cambian:** el texto de los letreros, cuándo aparecen ni cuánto duran.
- **Mensajes de error del Jefe** («Te falta oro», «Recargando…», «Zona visible…»): siguen en su color, porque no son letreros de eventos sino avisos de acciones no válidas del jugador Jefe.
- **Etiquetas de estado de los profes, número de balas bajas y colores del minimapa:** no son mensajes y no se tocaron.

**Pruebas:**
- Todos los letreros que hoy pone el proyecto están en una tabla con su color esperado. Si se agrega uno nuevo, la prueba falla hasta clasificarlo.
- También se prueban variaciones de acentos, mayúsculas, espacios y plurales, y que los textos son los mismos que antes de la fase.

**Sin probar:** verlo dentro de GDevelop.


## Fase 64 · Diálogos en burbujas con voz durante la partida (2026-11-22)
Scripts:
- `scripts/fase64_datos_dialogos.py` (`python -I`): lee el banco y las voces, y genera `scripts/dialogos_datos.js` y **`gdevelop/DIALOGOS.md`** (la tabla línea por línea).
- `scripts/fase64_dialogos.py` (idempotente): integración. La lógica está en `scripts/dialogo.js`.

Pruebas: `node gdevelop/scripts/prueba_dialogo.js` (15 casos). Respaldo: `respaldos/antes_de_fase64_*.json`. Todos los modos.

**Fuentes**
- **Texto:** `FDI-Z · Banco de diálogos (versión limpia).md`, en la raíz de fdiz. Tiene 132 frases individuales (Partes 2 y 4) y 38 conversaciones (Partes 1 y 3).
- **Voces:** `audios_fish/<Personaje>/*.wav` (76: Alan 24, Castillo 13, César 7, Miranda 15, Tony 17), con su `lista.txt`.
  - Formato: WAV PCM de 16 bits, mono, 44.1 kHz, de 0.65 a 5.4 s.
  - Se registran como recursos `voces/<pj>/<archivo>`, con la ruta `../../audios_fish/…`. El validador revisa 142 audios sin problemas.
- **Cómo se relaciona cada voz con su línea:** una línea tiene voz solo si el texto grabado en `lista.txt` (sin las etiquetas de tono, signos ni acentos) es **igual** al de la línea, del mismo personaje. Así quedaron las 76, sin sobrar ni repetirse; nada se asignó por parecido.
- **Sin voz:** Gabo, Alessandro, Carlos y los profes. Sus líneas salen solo en texto.

**Cómo funciona (`dialogo.js`)**
- **Qué se dice:** el host, o el juego sin red, detecta los momentos del banco y elige una frase o, si están los dos personajes, a veces la conversación. Lo pone en una cola.
- **Orden:** las líneas salen **de una en una y en orden**. Cada una dura lo que su voz más 0.35 s, o lo que tarda leerse (2.2–6 s) si no tiene voz. Al terminar se retira la burbuja.
  - Entre líneas de una misma conversación o frase de dos cuadros hay una pausa de 0.35 s; entre diálogos distintos, de 2.5 s.
- **Una sola voz:** todas suenan en un solo canal, el 7, el mismo de la charla de Canepa. Nunca suenan dos a la vez.
- **Si falta la voz o no carga:** la línea sigue con su texto.
- **Para no repetir:** cada frase espera 40 s antes de volver a salir y cada personaje 8 s. Algunos momentos frecuentes solo hablan a veces (`PROB`). La cola guarda hasta 3 diálogos, y uno que espera más de 5 s se descarta.
- **En línea:** `DlgLinea`, `DlgHabla` y `DlgSeq` viajan a los clientes, que dibujan la burbuja y ponen la voz. Los clientes no deciden nada.
- **Cuándo no hay diálogos:** en pausa, durante la charla con Canepa y fuera de la partida. Al pausar se retira la burbuja y se corta la voz.
- **Burbujas:**
  - Tienen el estilo de las de los profes: `ProfPanel` y `TxtProfe`, nombre en amarillo y colita `DlgDib`.
  - Van encima de quien habla, en pantalla.
  - Si ahí tapan el HUD, una cara, el letrero, la ayuda, el texto de la intro u otra burbuja (de los profes o de la charla), se corren a un lado o bajan a los pies. Siempre quedan dentro de la pantalla.
- **Intro (sin red):**
  - Las tres líneas de antes de la alerta las dicen, con su voz, tres personajes distintos del equipo que tengan frase de ese momento: Tony, Alan, Miranda, Castillo, Gabo o Alessandro.
  - En ese caso se quitan del texto de la intro las líneas «Tony: …», «Alan: …» y «Miranda: …», que reemplazan.
  - También se agrega la del celular (Tony) y la de la puerta tumbada (Alan o Castillo). La narración (alerta, «¡CRASH!») no cambia.

**Momentos que se detectan (disparadores)**
- **De quien actúa:**
  - cae, cae con alguien cerca, lo muerden, revive (habla quien levanta) o lo reviven, empieza a curar;
  - habilidad Q o E de cada personaje (Gorrear distingue regla o comida; Hackeo, con puerta cerca);
  - levanta una silla, lanza la engrapadora, revisa un locker;
  - recoge llaves, bidón o carnada, último interruptor, empieza la llamada;
  - abre una puerta, se atora en una restringida, puerta electrónica, ve un arma en el piso, termina una pelea.
- **Del equipo:**
  - tarjeta, apagón, horda, festín, objetivo cumplido o nuevo (llaves), final ¡Aguanten! (y a los 5, 18, 32, 42 y 50 s), escape;
  - rescate de Justino (inicio y fin), se calma el pasillo, respiro, el equipo duda;
  - zombis golpeando o tumbando una puerta, un compañero se acelera, un compañero cae cerca.

**Sin disparador** (ese momento no existe en el juego, así que la línea no se usa): 28 frases y 9 conversaciones, listadas en `DIALOGOS.md`. Ejemplos: comprar en la máquina, Ojo de oferta, AirDrop, «sube al camión».
- Por eso no suenan 8 voces aunque están relacionadas: `alan_06`, `alan_10`, `alan_11`, `miranda_08`, `miranda_09`, `tony_10`, `castillo_07` y `castillo_08`.

**Voces que faltan** (las líneas se ven en texto; detalle en `DIALOGOS.md`, marcadas **falta**):
- Frases de **Gabo (9), Alessandro (13) y Carlos (9)**: no tienen carpeta en `audios_fish`.
- Líneas de las 29 conversaciones que el juego usa: Alan 12, Miranda 6, Tony 7, César 4, Castillo 6, Alessandro 10, Gabo 9 y Carlos 5. Las grabaciones de `audios_fish` son de las frases individuales, no de las conversaciones (salvo `tony_02`, que sí coincide).
- Justino y Canepa: sin voz por ser profes (omitidos).

**Para que funcione en otra computadora:** `audios_fish/` y el banco de diálogos tienen que estar en el repo, porque las voces se cargan desde ahí y los datos se generan del banco.

**Sin probar:** escucharlo y verlo dentro de GDevelop, y en línea.


## Fase 65 · Cinemáticas del modo Historia como videos (2026-11-22)
Script: `scripts/fase65_cinematicas.py` (idempotente). Lógica: `scripts/cine.js`. Pruebas: `node gdevelop/scripts/prueba_cine.js` (16 casos). Respaldo: `respaldos/antes_de_fase65_*.json`. Solo Historia; Escape y Jefe no cambian.

**Carpeta.** El proyecto ya guarda sus videos en `gdevelop/FDI-Z/assets/interfaz/videos/`, así que los de la historia van en la subcarpeta **`assets/interfaz/videos/historia/`**. Ahí quedó un `LEEME.txt` con lo que espera cada archivo.
- Por cada archivo que exista, el script registra el recurso de video `vid_historia_0N`, con la ruta relativa `assets/interfaz/videos/historia/<archivo>`, y el objeto `VidHist0N` (Video, sin loop).
- **Hoy no hay ninguno**, así que no se registró nada. Hay que volver a correr el script cada vez que se copie un video.

| # | Archivo | Cuándo se reproduce (una vez por partida) | Si falta el archivo |
|---|---|---|---|
| 1 | `historia_01_inicio_aula.mp4` | Al empezar una partida de Historia, con el equipo en el salón B-01. Después, el interludio corto. | Tarjeta de texto y el interludio |
| 2 | `historia_02_joel_cic.mp4` | Un jugador entra a los Cubículos del CIC (3488–3744, 1920–2080) y Joel sigue esperando ayuda | Tarjeta |
| 3 | `historia_03_telefono_apagon.mp4` | Se completa la llamada en la computadora del CIC; después empieza la misión de la luz | Tarjeta |
| 4 | `historia_04_zombi_conserje.mp4` | Se abre o se derriba la puerta de la conserjería (P59) | Tarjeta |
| 5 | `historia_05_escopeta_casillero.mp4` | Se abre el casillero nuevo de la conserjería (5120, 596). Al terminar aparece la escopeta en (5136, 650). | Tarjeta |
| 6 | `historia_06_justino_neveria.mp4` | Un jugador llega a la nevería a menos de 240 px de Justino (antes de abrir el diálogo de reclutarlo) | Tarjeta |
| 7 | `historia_07_cajon_director.mp4` | Se revisa el cajón del escritorio del director (3328, 4436; F en el escritorio). Al terminar aparece el sheriff en (3400, 4470). | Tarjeta |
| 8 | `historia_08_canepa_autobus.mp4` | Se habla con Canepa (misión 5, después de la comida). Al terminar se cumple la misión y empieza la gasolina. | La charla con burbujas de la fase 61 |

**Cómo funciona**
- **Durante el video, la tarjeta o el interludio** (host o sin red):
  - `Estado = "cine"`: se detienen objetivos, cámara, bots, profes, diálogos y la pausa.
  - `TimeScale` 0: no se mueven zombis ni tiempos.
  - Los jugadores quedan sin control (`Control -2`) y sin entradas.
  - La música del canal 1 se pausa en cada máquina.
- **Saltar:** Enter, Espacio, Esc, clic, A o Start, a partir de 0.5 s. La tecla con la que se interactuó no salta el video.
- **Al terminar o saltar:** todo vuelve como estaba (controles, tiempo, estado y música).
- **Si un video no carga:** a los 4 s sigue la historia. Si el archivo no está, se muestra una tarjeta de 3.5 s con el título y lo que pasa.
- **Una sola vez:** `HistVistos` guarda los videos ya vistos en la partida. Mantener una tecla, repetir la interacción o volver a entrar a la sala no los repite.
- **En línea:** `CineModo`, `CineVid`, `CineSeq` y `HistVistos` viajan a los clientes. Cada máquina reproduce el video y el host decide cuándo termina.
- **Interludio corto (después del video 1):**
  - Aparecen dos zombis del otro lado de la puerta del salón (P06) y la golpean tres veces en 3.2 s: destello rojo, sonido, empujón y temblor. La puerta queda dañada (80 → 50), no rota.
  - Luego los zombis la siguen golpeando como siempre, aparecen la silla y la escoba (las mismas que deja la intro de Escape) y vuelve el control.
  - La intro de Escape no se tocó: solo se le agregó la condición `Modo != "historia"` para que no arranque en Historia.
- **Objetos guardados:**
  - En Historia, la escopeta y el sheriff ya no están en el piso: se guardan en el casillero (visible) y en el cajón.
  - El cajón no se dibuja porque es parte del escritorio; al acercarse aparece «Mantén F para revisar».
  - Al abrirlos se abren como cualquier casillero (con su objeto al azar), y al terminar el video aparece el arma.
- **Canepa:** `canepa.js` pregunta a `cine.js` (`toma()`) antes de empezar la charla. Si está el video 8, lo reproduce `cine.js`; si no, siguen las burbujas.
- **Objetos nuevos:** `CineDib` (velo) y `TxtCine` (textos de la tarjeta). Y en Historia, el casillero y el cajón (instancias de `Contenedor` creadas al empezar).

**Archivos que faltan:** los 8 videos de la tabla, en `gdevelop/FDI-Z/assets/interfaz/videos/historia/`. Formato: MP4 (H.264), 16:9, con su audio.

**Sin probar:** dentro de GDevelop. Sobre todo el interludio (posición de los zombis frente a la puerta) y la reproducción real de los videos cuando existan.

## Fase 66 · Música nueva del menú y de la partida (2026-11-22)

Script: `gdevelop/scripts/fase66_musica.py` (idempotente; con GDevelop cerrado). Originales en `fdiz/sonidosfdi/`.

| Original | En el proyecto | Dónde suena |
|---|---|---|
| `SOUNDTRACK2D.MP3.mpeg` | `musica/soundtrack2d.mp3` (copia exacta, es un MP3) | Titulo, Menu y Online: canal 1, en bucle, volumen 45 (antes `musica/menu.ogg`) |
| `ambiente juego.wav` | `musica/ambiente_juego.wav` | Juego, todos los modos: canal 1, en bucle, volumen 45 (antes `partida_1.ogg`) |
| `va encima de ambiente de juego.wav` | `musica/ambiente_juego_capa.wav` | Juego: encima del ambiente, canal 2, en bucle, volumen 40 |

- Los dos WAV se pasaron de PCM 24 bits a 16 bits (la regla de `audio_manifest.json`); no se recortaron ni se cambió nada más.
- En Juego quedan **desactivados** los cambios de pista por infestación 3 y 5 (`partida_2`, `partida_3`) y del final (`final_aguanten`), para que el ambiente no se corte. Los `.ogg` viejos se conservan.
- Al entrar a Titulo, Menu, Online y Resultados se detiene el canal 2. Resultados sigue con `victoria.ogg` / `derrota.ogg` en el canal 1.
- `cine.js` pausa los canales 1 y 2 durante las cinemáticas de Historia.
- `audio_manifest.json`: 3 pistas nuevas y la extensión `.mp3`. `validar_audio.py` acepta MP3.
- Los 22 efectos de `sonidosfdi/sonidos 2d/ogg` son idénticos (md5) a los de `fdiz/sonidos/` de la fase 60; no se cambiaron.
- No se usan (no estaban en el pedido): los loops BOS_* y NW_* de `sonidosfdi/`.

Fase 65: el video 1 está en la carpeta como `historia_01_inicio_aula.mp4.mp4` (Windows oculta la extensión). `fase65_cinematicas.py` ahora acepta un nombre que empiece igual y termine en `.mp4`, sin renombrarlo.

**Sin probar:** dentro de GDevelop (que las dos pistas de la partida suenen juntas sin saturar).

## Fase 67 · La pistola inicial se recoge del piso del salón (2026-11-22)

Script: `gdevelop/scripts/fase67_pistola_inicial.py` (después de volver a correr `fase62_armas_uso.py`). Lógica en `armas.js` (`ponerPistola`).
- Nadie empieza con la pistola pequeña: `fase62_armas_uso.py` ya no la da en "Inicio de supervivientes".
- Al empezar, el host pone UNA `ArmaPiso` Tipo `pistolita` (Solo = 1) en el salón del jugador 1: B-01 (6000, 3100) en la intro de Escape e Historia; E-04 (5200, 2570) en los demás casos. `PistolaPuesta` evita repetirla.
- Se recoge con el evento de siempre (puños, pasar encima): Arma = pistolita, 9 balas, valores de arma de fuego, y se borra del piso. Solo el jugador 1 (condición `Solo = 0 o Solo = Sup.Jugador`).
- Escape: al terminar o saltar la intro el jugador 1 ya no recibe la regla (decisión del usuario); el consejo dice "¡Agarra la pistola!".
- Sprite de piso `generado/sprites/objetos/armas/pistolita_piso.png` (pistolita.png x3).
- No hay partidas guardadas en el juego (solo el volumen).
- Probado en una exportación HTML del proyecto: empieza a puños, la pistola está en B-01, al pisarla queda equipada (9 balas, ícono y mira). El disparo no se pudo comprobar con clics simulados.

## Fase 68 · Modo Historia de 12 pasos: cinemáticas en video, diálogos con voz, objetivos y checkpoints (2026-11-22)

Fuente: `gdevelop/historia/02_HISTORIA_PARA_GDEVELOP.md` (la secuencia, seguida al pie de la letra) y `gdevelop/historia/01_DIALOGOS_PARA_VOCES.md` (textos exactos de los globos). Copias de los archivos que estaban en Descargas.

Scripts:
- `scripts/fase68_historia.py` (idempotente; con GDevelop cerrado; va al final de la cadena, después de fase67).
- Lógica en `scripts/historia.js` (`gdjs.fdizHistoria`).
- Los datos de las líneas (personaje, texto, archivo y duración del audio) y los videos presentes se generan en `scripts/historia_datos.js`.

Pruebas: `node gdevelop/scripts/prueba_historia2.js` (39 casos). Comprueba el orden de videos y audios de cada paso contra el documento, los 55 audios y lo incrustado en el proyecto.

Respaldos: `respaldos/antes_de_fase68_historia_20261122_2215.json` (proyecto) y `respaldos/antes_de_fase68_<usar|profes|dialogo|cine>_20261122_2215.js`.

### Archivos
| Qué | Dónde |
|---|---|
| 55 voces `.mp3` (de `Videojuego2D/voces/voces`) | `FDI-Z/assets/historia/audio/` (recursos `historia/audio/<archivo>.mp3`) |
| Videos `C01_T1.mp4`, `C01_T2.mp4`, `C02.mp4` y también `C03.mp4` (ya existía en `Videojuego2D/`) | `FDI-Z/assets/historia/video/` (recursos `vid_hist_<C..>`, objetos `Vid<C..>`; `LEEME.txt` dice cuáles faltan) |
| Alarma en bucle (provisional, sintetizada por el script) | `FDI-Z/efectos/eventos/alarma_loop.wav` (también en `audio_manifest.json`) |

- `voces_trabajo/voces_trabajo` solo tiene los WAV intermedios (`fish/`, `rvc/`). Se usaron los MP3 finales de `voces/voces`.
- Los videos venían como `C01_t1.mp4`, `c01_t2.mp4` y `c02.mp4`. Se copiaron con el nombre exacto del documento.
- **Para agregar un video nuevo (C04 … C10):** copiarlo con su nombre exacto a `assets/historia/video/` y correr `python gdevelop/scripts/fase68_historia.py`. No hay que tocar eventos.
  - Mientras `C10.mp4` no exista, la escena final usa `assets/interfaz/videos/15_victoria.mp4`, como pide el documento.
- **Aviso sobre una voz:** `C65_01_cesar.mp3` dura 1.2 s para una frase de 48 letras («Para cuando vuelvan». ¿Cuando vuelvan… quiénes?). Parece recortada; conviene regenerarla. Las demás voces duran entre 0.8 y 8.6 s, acorde con su texto.

### Sistemas (sección 3 del documento)
- **Cinemáticas:**
  - Video a pantalla completa en la capa HUD (z 2000), encima del HUD.
  - Mientras suena, el mundo se congela como en las fases 61 y 65: `Estado = "cine"`, `TimeScale 0`, jugadores con `Control -2`. Así se detienen los zombis, los bots y los tiempos.
  - La música del juego (canales 1 y 2) y la alarma se pausan.
  - **Mantener Espacio, Enter o A durante 1 s** salta el video; hay un indicador circular abajo a la derecha. Si la tecla ya venía apretada, primero hay que soltarla.
  - Cada video se ve una vez por partida (`Historia.CinematicasVistas`, global: sobrevive al reintentar).
  - Si falta el archivo: pantalla negra de 1 s con el título de la escena, y luego sus diálogos.
  - Si un video no carga, a los 6 s la historia sigue.
- **Diálogos:**
  - Globo sobre quien habla, con el mismo estilo y la misma colocación que los de la fase 64: evita el HUD.
  - Si quien habla no está en pantalla (o es el Altavoz), aparece un panel abajo al centro con el nombre y, para los cuatro alumnos, su retrato (objeto `HistRetrato`).
  - Nombre del color del documento: Alan gris, Miranda café claro, Tony blanco, César azul, Joel verde, Justino rosa, Canepa naranja, Altavoz rojo.
  - La voz suena en el canal 8 (el banco de la fase 64 usa el 7).
  - La línea pasa al terminar el audio + 0.3 s (duración leída del MP3 por el script). **Espacio** adelanta.
  - Bloqueantes [D]: mundo congelado. De gameplay [G]: J1 en el pasillo y J2 al salir del CIC, con el juego en marcha.
  - Mientras habla la historia, el banco de la fase 64 se calla (gancho en `dialogo.js`).
- **Objetivos:**
  - Texto «Objetivo / <texto>» en el letrero de objetivos de siempre (`TxtObjetivo`) y la flecha amarilla de siempre hacia la zona (`HistObjX/Y` → `ObjX/Y`).
  - Al empezar un objetivo: letrero grande y el sonido de nuevo objetivo.
  - Zonas invisibles: se activan cuando entra cualquiera de los cuatro (humano o bot).
  - Las de «usar» son un `Objetivo` (mantener F/A 1 s, con la misma indicación «Mantén F para…» de la fase 56).
- **Checkpoints:**
  - Al empezar cada paso se guarda `Historia.Paso` (y `Historia.Armas`).
  - Si cae todo el equipo: la derrota de siempre (`16_derrota.mp4`) con el botón **REINTENTAR** y «Seguirán desde el paso N de 12».
  - Al reintentar, la partida arranca en el lugar de ese paso con el mundo como debe estar: armas con cargador lleno, puertas ya abiertas, Joel con el grupo o en la conserjería, apagón, reja, conserje y dificultad.
  - Elegir HISTORIA en el menú empieza siempre desde el paso 1. Al ganar también se reinicia.
- **Elenco fijo:**
  - Equipo Tony, Miranda, Alan y César. Quien eligió a uno de ellos lo conserva; los demás reciben los que falten (por ejemplo, Gabo → Miranda). También se corrige `P1Pj..P4Pj`.
  - En Historia, Joel, Justino y Canepa no se reclutan con F ni piden ayuda (ganchos en `profes.js` y `usar.js`).

### Los 12 pasos (como en el documento)
| Paso | Disparador | Video | Evento |
|---|---|---|---|
| 1 | Inicio (negro → fundido) | — | INT_01–06; objetivo «Revisa el escritorio del profe» |
| 2 | `Zona_Escritorio` | C01_T1, C01_T2 | — |
| 3 | Sigue solo | C02 | Alarma (luz roja intermitente en el salón + bucle bajo, desde el Altavoz); **pistola pequeña** al jugador 1 |
| 4 | Sigue solo | C03 | El zombi rompe P06 y entra; texto «Clic izquierdo (o gatillo) para disparar» hasta que lo tumban |
| 5 | `Zona_CIC` (J1 en `Zona_Pasillo1`) | C04 | Joel se une (aliado bot; no ataca; si cae se levanta a los 5 s; no se infecta) |
| 6 | Usar `Zona_Telefono` | C05 | **Apagón** (`Apagon = 1`, la mecánica de siempre; también se apaga la alarma); 3 zombis en los pasillos del CIC |
| 7 | `Zona_Conserje` (J2 al salir del CIC) | C06 | Se abre P59 y sale el zombi de intendencia (normal) |
| 8 | Usar `Zona_Casillero` (después de tumbarlo) | C065 | **Escopeta** (a Tony); termina el apagón; Joel se queda en la conserjería |
| 9 | `Zona_Neveria` | C07 | Justino se queda; el equipo recupera toda la vida |
| 10 | `Zona_Direccion` → usar `Zona_CajonDirector` | C08 | **Llave** (se abre la reja trasera) y **pistola** (a César, o a quien no tenga arma de fuego); `ExtraZombies = 8`; el conserje zombi aparece y persigue |
| 11 | `Zona_Autobus` | C09 | Defensa con el final **¡Aguanten!** de siempre, ahora de **90 s** («Protege a Canepa: 1:30»), oleadas extra a los 30 y 60 s y el conserje |
| 12 | Termina la cuenta con el equipo vivo | C10 (o `15_victoria.mp4`) | C10_01–02 antes del video; victoria; **C10_03** suena en Resultados, sobre la pantalla de victoria |

### Zonas colocadas (no existían en el mapa: rectángulos en `historia.js → H.ZONAS / H.USAR`)
| Zona | Dónde | Por qué |
|---|---|---|
| Escritorio | x 5904–6064, y 2884–2984 | Frente al escritorio del profe del salón B-01, donde empieza el equipo |
| Pasillo1 | Franja x 4380–4460, y 2080–4300 | A mitad de camino entre B-01 y el CIC; cualquier ruta la cruza |
| CIC | x 2688–3744, y 1632–2080 | El CIC con sus dos pasillos; se entra por P43 o por las salas 1 a 4. Joel espera en los Cubículos del CIC (3616, 2000) |
| Telefono | (3136, 1760) | La computadora del CIC (`computadoras_llamada` del mapa), visible |
| Conserje | x 4930–5190, y 792–884 | El pasillo frente a la puerta P59 de la conserjería |
| Casillero | (5112, 622) | Un casillero nuevo (mueble `cic/lockers_cerrados`) contra la pared de la conserjería |
| Neveria | La nevería completa (1536–1984, 1440–2432) | Justino espera en (1936, 1668) |
| Direccion | La oficina del director (3200–3456, 4256–4544) | Adentro, el objetivo cambia a «Revisa el escritorio del director» |
| CajonDirector | (3328, 4436) | Frente al escritorio del director |
| Autobus | x 240–740, y 3080–3460 | Junto al autobús (400, 3264) y Canepa (544, 3328), dentro del radio de 380 px del final de siempre |

### Decisiones donde el documento chocaba con el proyecto (se eligió no romper lo existente)
- **El modo Historia anterior (6 misiones: fases 55, 61 y 65) queda reemplazado** en la misma tarjeta HISTORIA del menú (Modo `"historia"`), que ahora dice «12 pasos».
  - Sus eventos siguen en el proyecto, pero quedan quietos: el evento nuevo `FDIZ-FASE68-OBJ` detiene los objetivos de Escape en Historia hasta la defensa, y `cine.js` ya no corre.
  - Escape y Jefe no cambian: lo comprobé en el juego exportado y con las pruebas.
  - `prueba_historia.py` (la Historia de 6 misiones) ya no aplica: sus casos de Historia fallan a propósito; los de Escape pasan.
- **Puerta trasera del salón:** B-01 solo tiene una puerta (P06). No se abrió una nueva en el muro: el zombi rompe P06 y por ahí mismo salen. La línea de César que la menciona se dejó igual.
  - Hasta el paso 4, P06 está cerrada y no se puede tumbar; dice «La puerta está cerrada».
- **Objetivo «arriba a la izquierda»:** ahí está el panel del jugador 1. Se usa el letrero de objetivos de siempre (arriba al centro), con su flecha.
- **«Reja trasera»:** no existía. Se puso en la única entrada del campus al estacionamiento (x 1504, y 3072–3552): un choque invisible y la valla blanca girada (arte provisional). Desaparece al tomar la llave; sin llave avisa «La reja trasera está cerrada con llave».
- **Pistola de C8:** es el revólver «pistola» de 4 balas de la fase 59.
  - La escopeta y el revólver ya no están en el piso en Historia.
  - La pistola pequeña ya no se pone en el piso (fase 67): llega en el paso 3.
- **Objetivos agregados** (el documento no los listaba, pero sus disparadores son de «usar»): «Usa el teléfono del CIC» y «Revisa el casillero del conserje».
- **Canepa** es un NPC inmune (como los profes que esperan): durante la defensa no puede morir. El letrero dice «¡AGUANTEN! Canepa repara el autobús».
- **Conserje zombi:** se quita del mapa al empezar (vigilaba la conserjería y habría peleado en C6). Aparece en el paso 10 persiguiendo, cerca de la Dirección. Si ya lo tumbaron, no vuelve en la defensa.
- **«Luz parcial» al terminar el apagón:** el juego solo tiene dos niveles de luz, así que vuelve la luz de noche normal.
- **Modo presentación (F1):** la tecla 1 completa lo que se esté esperando (zona, uso o combate). La tecla 2 (saltar al final) no hace nada en Historia.

### Correcciones que también aplican a los demás modos
- **REINICIAR de Resultados no funcionaba:** usaba `if(...)`, que GDevelop no tiene, y el código generado cambiaba a la escena `""`. Ahora va a `"Juego"` (estaba en la rama sin red, donde el valor siempre era ese).
- El final ¡Aguanten! dura `FinalSeg` (60 por omisión: Escape y Jefe igual que antes).

### Pruebas
- Probado en una exportación HTML del proyecto con el exportador de GDevelop 5.6:
  - El recorrido completo del paso 1 al 12 termina en Resultados con victoria y el checkpoint en 0. Las zonas se alcanzaron moviendo al equipo; el teléfono, el casillero y el escritorio, manteniendo F.
  - Verificado en el recorrido: los 4 videos se ven a pantalla completa y se saltan con el indicador; las pantallas negras de los que faltan; globos con nombre y color; J1 y J2; tutorial de disparo.
  - Verificado también: alarma roja, apagón y vuelta de la luz; Joel con el grupo, que se levanta a los 5 s; reja cerrada y abierta; armas; defensa de 90 s con oleadas; C10_03 en la victoria.
  - Derrota → REINTENTAR → mismo paso, con el estado restaurado (pasos 7, 10 y 11).
  - El menú real: la tecla 3 elige HISTORIA y reinicia el checkpoint.
- Escape (intro, 3 objetivos, final de 60 s) y Jefe arrancan igual que antes. Los errores de exportación son los mismos 4 que antes de la fase (Canepa, StickAngle, dos textos del Menú).
- `prueba_historia2.js` 39/39. Las pruebas de `usar`, `profes`, `dialogo`, `cine`, `canepa`, `armas`, `audio`, `avisos`, `correr`, `medios` y `sfx` siguen pasando.

### Pendiente
- **Videos C04, C05, C06, C065, C07, C08, C09 y C10:** copiar a `assets/historia/video/` y correr la fase 68.
- Regenerar `C65_01_cesar.mp3` (parece recortado).
- Arte: la reja trasera (valla girada) y una alarma grabada en lugar de la sintetizada.
- **Sin probar:**
  - Dentro del editor de GDevelop (se probó con su exportador y su runtime).
  - Con mando físico.
  - En línea con dos máquinas: las variables `Hist*` viajan y los clientes dibujan videos, globos y voces, pero solo el anfitrión puede saltar.
  - Recorrer los caminos completos caminando: los bots y los humanos llegaron, pero en la prueba se movió al equipo entre zonas.

## Fase 69 · Correcciones: pistola inicial, daño de armas, Historia solo con Tony, mundo sin congelar, menú de modos, CIC, Joel y casillero (2026-11-22)

Script: `scripts/fase69_correcciones.py` (idempotente; después de `fase68_historia.py`). Cambios también en `historia.js`, `usar.js` y `armas.js`. Respaldo: `respaldos/antes_de_fase69_20261122_2307.json`.

El detalle por fase, las pruebas ejecutadas y lo pendiente están en **`TRASPASO_HISTORIA.md`** (raíz de fdiz). El inventario de letreros para clasificar colores está en **`gdevelop/ALERTAS.md`**; los colores aún no se cambian.
