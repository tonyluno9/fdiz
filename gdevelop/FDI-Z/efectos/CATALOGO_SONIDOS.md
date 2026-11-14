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
