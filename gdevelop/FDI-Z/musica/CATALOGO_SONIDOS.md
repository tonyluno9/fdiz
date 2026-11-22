# Catálogo de sonidos y música (Fase 21, estilo SNES)

Todo se sintetiza con `gdevelop/scripts/snes_synth.py` + `gdevelop/scripts/fase21_audio.py` (ondas de pulso, triángulo y ruido, cuantización de 8 bits, filtro gaussiano y eco, como el chip S-SMP/DSP de la SNES). Formato `.ogg` Vorbis 44.1 kHz mono. Cada sonido existe **una sola vez** (sin variantes).
Para rehacer uno que no te guste: dime su **ID** y se regenera con `python3 gdevelop/scripts/fase21_audio.py --solo ID` (y se ajusta el volumen en la tabla `SFX`/`MUS` del script).
**Volumen** = valor (0-100) que usan los eventos; todos están por debajo de 100 y los archivos tienen pico -1 dB. Los videos se bajaron a 3 % (fondos) y 12 % (personajes del selector) para que no tapen música ni efectos.

## Efectos

| ID | Archivo | Cuándo suena | Cómo suena | Dur. | Vol. |
|---|---|---|---|---:|---:|
| SFX_COMBATE_CONVERTIDO | combate/convertido | Un personaje se convierte en zombie | Barrido grave descendente con vibrato + rugido de ruido | 1.0 s | 70 |
| SFX_COMBATE_LANZAR | combate/lanzar | Lanzar un objeto | Silbido ascendente/descendente de ruido (whoosh) | 0.4 s | 60 |
| SFX_COMBATE_MORDIDA | combate/mordida | Mordida de zombie | Dos mordiscos secos de ruido + bajada de pulso | 0.35 s | 65 |
| SFX_EVENTO_APAGON | eventos/apagon | Se va la luz | Caída larga de tono agudo a grave + zumbido y chispazo | 1.5 s | 70 |
| SFX_EVENTO_ESCAPE | eventos/escape | Se activa la salida/escape | Sirena de 2 tonos + arpegio ascendente urgente | 1.8 s | 75 |
| SFX_EVENTO_FINAL_INICIO | eventos/final_inicio | Arranca el final | Bajos graves, acorde menor amenazante y campanada | 2.2 s | 75 |
| SFX_EVENTO_INFESTACION_SUBE | eventos/infestacion_sube | Sube el nivel de infestación | Dos deslizamientos graves tipo corno + gruñido | 1.6 s | 70 |
| SFX_EVENTO_OBJETIVO_CUMPLIDO | eventos/objetivo_cumplido | Objetivo cumplido | Arpegio mayor C-E-G-C alegre | 0.9 s | 65 |
| SFX_EVENTO_OBJETIVO_NUEVO | eventos/objetivo_nuevo | Aparece un objetivo nuevo | Dos "ding" (G-C) | 0.6 s | 65 |
| SFX_EVENTO_PASO_OBJETIVO | eventos/paso_objetivo | Avanza un paso del objetivo | Dos blips agudos cortos | 0.25 s | 55 |
| SFX_EVENTO_RESCATE_LOGRADO | eventos/rescate_logrado | Rescate logrado | Mini fanfarria heroica | 1.6 s | 70 |
| SFX_EVENTO_VICTORIA | eventos/victoria | Pantalla de victoria (junto con la música) | Fanfarria corta de victoria | 1.7 s | 65 |
| SFX_INTERFAZ_JEFE_INVOCAR | interfaz/jefe_invocar | El jefe invoca un zombie | Gong grave + 3 notas menores descendentes | 2.0 s | 75 |
| SFX_MOVIMIENTO_COMER | movimiento/comer | Comer | Tres crujidos de ruido | 0.5 s | 55 |
| SFX_MUNDO_BIDON | mundo/bidon | Interactuar con un bidón | Golpe metálico con campanilla | 0.6 s | 60 |
| SFX_MUNDO_INTERRUPTOR | mundo/interruptor | Interruptor | Dos "clics" eléctricos | 0.2 s | 55 |
| SFX_MUNDO_LOCKER | mundo/locker | Locker | Rechinido + portazo metálico | 0.7 s | 60 |
| SFX_MUNDO_MAQUINA | mundo/maquina | Máquina expendedora | Golpe mecánico + monedas + caída del producto | 0.9 s | 60 |
| SFX_MUNDO_MONEDA | mundo/moneda | Recoger moneda | Clásico B5→E6 | 0.5 s | 55 |
| SFX_MUNDO_PUERTA_GOLPE | mundo/puerta_golpe | Golpear una puerta | Golpe sordo grave + ruido | 0.35 s | 60 |
| SFX_MUNDO_PUERTA_ABRIR | mundo/puerta_abrir | Abrir una puerta | Rechinido que sube + pestillo | 0.8 s | 60 |

## Habilidades (tema de cada personaje)

| ID | Archivo | Tema | Cómo suena | Dur. | Vol. |
|---|---|---|---|---:|---:|
| SFX_HABILIDAD_TONY | habilidades/tony_habilidad | Cocina | Chisporroteo de sartén + arpegio mágico | 1.0 s | 70 |
| SFX_HABILIDAD_TONY_ESPECIAL | habilidades/tony_especial | Banquete | Subida de poder de 7 notas + explosión | 1.5 s | 75 |
| SFX_HABILIDAD_MIRANDA | habilidades/miranda_habilidad | Canción de cuna | Mini nana (melodía tipo Brahms) con bajo en triángulo | 3.0 s | 65 |
| SFX_HABILIDAD_MIRANDA_ESPECIAL | habilidades/miranda_especial | Minigun | 26 disparos rápidos de ruido + cierre | 1.5 s | 70 |
| SFX_HABILIDAD_CESAR | habilidades/cesar_habilidad | Hackeo | Ráfaga de bips digitales + confirmación | 1.0 s | 65 |
| SFX_HABILIDAD_CESAR_ESPECIAL | habilidades/cesar_especial | Sobrecarga | Alarma alterna + ruido creciente + explosión | 1.5 s | 70 |
| SFX_HABILIDAD_ALAN | habilidades/alan_habilidad | Dinero | "Ka-ching" de caja registradora | 0.9 s | 65 |
| SFX_HABILIDAD_ALAN_ESPECIAL | habilidades/alan_especial | Lluvia de dinero | 14 monedas rápidas + explosión | 1.4 s | 70 |
| SFX_HABILIDAD_CASTILLO | habilidades/castillo_habilidad | Beber | Glub-glub-gulp | 0.8 s | 65 |
| SFX_HABILIDAD_CASTILLO_ESPECIAL | habilidades/castillo_especial | Poción curativa | Escala pentatónica brillante con brillos | 1.4 s | 70 |
| SFX_HABILIDAD_ALESSANDRO | habilidades/alessandro_habilidad | Chiste | Tambores "ba-dum-tss" (redoble + platillo) | 1.3 s | 70 |
| SFX_HABILIDAD_ALESSANDRO_ESPECIAL | habilidades/alessandro_especial | Tiempo | Tic-tac de reloj + frenada del tiempo | 1.8 s | 70 |
| SFX_HABILIDAD_GABO | habilidades/gabo_habilidad | Velocidad | Dos barridos rápidos ascendentes | 0.7 s | 65 |
| SFX_HABILIDAD_GABO_ESPECIAL | habilidades/gabo_especial | Estampido | Boom grave + ecos de estela | 1.4 s | 70 |
| SFX_HABILIDAD_CARLOS | habilidades/carlos_habilidad | Llaves | Tintineo de llaves + clic de cerradura + clunk | 0.9 s | 65 |
| SFX_HABILIDAD_CARLOS_ESPECIAL | habilidades/carlos_especial | Armadura | Golpe pesado + resonancia metálica + subida de poder | 1.4 s | 70 |

## Música (`musica/`)

| ID | Archivo | Dónde suena | Estilo | Bucle | Dur. | Vol. |
|---|---|---|---|---|---:|---:|
| MUSICA_MENU | menu | Título y menús | La menor misteriosa, 96 bpm, arpegio suave | Sí | 20.0 s | 45 |
| MUSICA_PARTIDA_1 | partida_1 | Partida inicial | Re menor tensa y escasa, 108 bpm | Sí | 17.8 s | 45 |
| MUSICA_PARTIDA_2 | partida_2 | Infestación 3 | Mi menor con batería, 132 bpm | Sí | 14.6 s | 45 |
| MUSICA_PARTIDA_3 | partida_3 | Infestación 5 | Do# menor frenético, 156 bpm | Sí | 12.3 s | 45 |
| MUSICA_FINAL_AGUANTEN | final_aguanten | Final "aguanten" | La menor épica y urgente, 168 bpm | Sí | 11.4 s | 50 |
| MUSICA_VICTORIA | victoria | Resultados: victoria | Fanfarria en Do mayor | No | 9.3 s | 50 |
| MUSICA_DERROTA | derrota | Resultados: derrota | Melodía descendente triste en La menor | No | 12.9 s | 50 |

Los bucles se renderizan con eco circular, así que el final empalma con el inicio sin corte.


## Fase 58 (2026-11-21): efectos de `sonidos_nuevos/` del repositorio
Script: `gdevelop/scripts/fase58_sonidos.py` (`python -I`). Lee de `FDI-Z/sonidos_nuevos/` (no se modifica) y escribe copias procesadas. Mediciones en `efectos/fase58_informe.json`.
Regla: **manda el repositorio**. Si trae un archivo para un efecto, se usa ese archivo. Si yo había elegido un archivo de 2dsounds que el repositorio destinó a otra cosa, el efecto vuelve a su `.ogg` original. Los nuevos son **WAV PCM 16 bits mono** (48 kHz si venían a 96 kHz; si no, 44.1 kHz), con pico ≤ -1 dBFS y promedio ~-16 dBFS. Conservan su evento, su momento y su volumen de evento.

| Efecto | Antes | Ahora ← archivo de `sonidos_nuevos/` | Dur. |
|---|---|---|---:|
| puerta_golpe | `efectos/mundo/puerta_golpe.ogg` | `efectos/mundo/puerta_golpe.wav` ← `door_punch.wav` | 0.41 s |
| miranda_especial | `efectos/habilidades/miranda_especial.ogg` | `efectos/habilidades/miranda_especial.wav` ← `minigun.wav` | 2.48 s |
| tony_habilidad | `efectos/habilidades/tony_habilidad.ogg` | `efectos/habilidades/tony_habilidad.wav` ← `tony_cook_sound.wav` | 0.39 s |
| tony_especial | `efectos/habilidades/tony_especial.ogg` | `efectos/habilidades/tony_especial.wav` ← `tony_powerup.wav` | 1.14 s |
| castillo_especial | `efectos/habilidades/castillo_especial.ogg` | `efectos/habilidades/castillo_especial.wav` ← `powerup_generic_sound.wav` | 0.39 s |
| moneda | `efectos/mundo/moneda.ogg` | `efectos/mundo/moneda.wav` ← `FNF_EBA_fx_misc_coin_collector.wav` | 0.34 s |

**Vuelven a su `.ogg` original** (el repositorio usa su archivo para otra cosa):
- apagon (concierge_death_effect)
- interruptor (minigun_ednd_sound)
- objetivo_nuevo (main_menu_start_sound)
- alan_habilidad (item_collected)
- objetivo_cumplido (tony_cook_sound)
- gabo_habilidad (tony_powerup)
- cesar_habilidad (start_game_sound)
- mordida (kick_sound_effect)
- paso_objetivo (zombie_death)

**En `sonidos_nuevos/` sin conectar todavía:**
- punch1-4
- zombie_death, _2 y _3
- item_collected
- start_game_sound
- main_menu_start_sound
- concierge_death_effect
- minigun_ednd_sound
- kick_sound_effect
- BULLYFINGER (hihat 3, kick 4 y 16, percussion 17)
- las músicas `main_menu*.MP3`

**Siguen los sintetizados (sin archivo en el repositorio):**
- combate: convertido, lanzar
- eventos: escape, final_inicio, infestacion_sube, rescate_logrado, victoria
- interfaz: jefe_invocar
- movimiento: comer
- mundo: bidon, locker, maquina, puerta_abrir
- habilidades: miranda_habilidad, cesar_especial, alan_especial, castillo_habilidad, alessandro (las dos), gabo_especial, carlos (las dos)
- las 7 músicas

**Armas de fuego (fase 59):** `efectos/combate/revolver.wav` y `escopeta.wav`, sintetizados.


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
