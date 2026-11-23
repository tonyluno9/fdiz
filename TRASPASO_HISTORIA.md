# FDI-Z · Traspaso: Modo Historia (fase 68) y correcciones (fase 69)

Fecha: 2026-11-22. Escrito para seguir el trabajo en otra computadora.

**Resumen rápido**
- Todo lo de este documento ya está aplicado en `gdevelop/FDI-Z/FDI-Z.json`. Basta con bajar el repositorio y abrir el proyecto en GDevelop: no hay que correr ningún script.
- **Fase 70 (hecha):** los colores de las alertas ya están clasificados y aplicados (`gdevelop/ALERTAS.md`).
- Abajo, en «Lo que falta», está lo que quedó sin probar.

---

## 1. Cómo ponerlo al día en la otra computadora

1. Baja los cambios (ya están en **`main`**; también quedó la rama `historia-12-pasos` con lo mismo):
   ```
   git checkout main
   git pull
   ```
2. Abre en GDevelop (5.6.287 o más nuevo) `gdevelop/FDI-Z/FDI-Z.json` y arranca desde la escena **Titulo**, o desde **Menu**.
3. **No edites a mano** los eventos que tienen comentarios `FDIZ-FASE68…` / `FDIZ-FASE69…` ni los bloques JS `FDIZ-FASE…-MOD`.
   - Salen de scripts. Para cambiarlos, edita el `.js` o el `.py` y vuelve a correr las fases con GDevelop cerrado:
     ```
     python gdevelop/scripts/fase68_historia.py
     python gdevelop/scripts/fase69_correcciones.py
     node gdevelop/scripts/prueba_historia2.js
     node gdevelop/scripts/prueba_armas.js
     ```
   - **El orden importa:** la 68 incrusta `historia.js`, `usar.js`, `profes.js`, `dialogo.js` y `cine.js`. La 69 incrusta `armas.js` y aplica sus cambios en eventos y objetos. Las dos son idempotentes: correrlas de nuevo deja el mismo resultado.
4. Hace falta Python 3 con Pillow (`pip install pillow`) y Node.js, solo para los scripts y las pruebas.
5. **Para agregar un video que falta** (C04, C05, C06, C065, C07, C08, C09, C10): cópialo con ese nombre exacto a `gdevelop/FDI-Z/assets/historia/video/` y corre la fase 68 y luego la 69.
6. `sonidosfdi/` (77 MB) **no se subió**: ya estaba fuera del repositorio antes de esta sesión y no es parte de estos cambios. Los sonidos que el juego usa de ahí ya están copiados dentro del proyecto (fase 66).

## 2. Qué se hizo

### Fase 68 · Modo Historia de 12 pasos (pedido 1)
Fuente: `gdevelop/historia/02_HISTORIA_PARA_GDEVELOP.md` (secuencia) y `gdevelop/historia/01_DIALOGOS_PARA_VOCES.md` (textos). Son copias de los documentos que estaban en Descargas.

Detalle completo en `gdevelop/BITACORA.md`, sección «Fase 68».

- **Archivos nuevos:**
  - 55 voces en `gdevelop/FDI-Z/assets/historia/audio/`.
  - Videos C01_T1, C01_T2, C02 y C03 en `assets/historia/video/` (C03 ya existía en la carpeta `Videojuego2D`).
  - Alarma provisional `efectos/eventos/alarma_loop.wav`.
- **Lógica:** `gdevelop/scripts/historia.js`. Los datos (`historia_datos.js`) se generan solos.
- **Sistemas:**
  - Cinemática a pantalla completa (mantener Espacio, Enter o A 1 s para saltar, con un indicador circular).
  - Diálogos con voz y globo sobre quien habla, o con retrato si no está en pantalla. Avanzan al terminar el audio + 0.3 s; Espacio adelanta.
  - Objetivos en el letrero de siempre, con la flecha.
  - Zonas invisibles.
  - Checkpoint por paso; al perder sale **REINTENTAR**.
- **Los 12 pasos del documento**, con estas decisiones donde el documento chocaba con el proyecto:
  - El salón B-01 solo tiene una puerta (P06): el zombi la rompe y salen por ahí.
  - El objetivo va en el letrero de arriba al centro, no arriba a la izquierda (ahí está el panel de P1).
  - La «reja trasera» se creó en la única entrada al estacionamiento (x 1504, y 3072–3552).
  - El modo Historia viejo de 6 misiones quedó reemplazado.
- **Corrección general:** el botón REINICIAR de Resultados no funcionaba en ningún modo (usaba `if(...)`).

### Fase 69 · Las 10 correcciones (pedido 2)
Script: `gdevelop/scripts/fase69_correcciones.py`, más cambios en `historia.js`, `usar.js` y `armas.js`.

| Fase | Qué se cambió | Dónde |
|---|---|---|
| 1 · Pistola inicial | Escape/Jefe: ya estaba en el piso (fase 67). Historia: ya no se da equipada. En el paso 3 queda en el piso frente al escritorio (5960, 2960) y se recoge pasando encima (evento «Armas del salón»). Solo la recoge P1; desaparece del piso al recogerla. **Nuevo:** si P1 trae un arma cuerpo a cuerpo (escoba, silla…) y pisa la pistola, esa arma queda en el piso y toma la pistola. Antes la escoba de la intro podía dejar la pistola sin poder recogerse. Checkpoints: si ya la recogió, la conserva; si no, vuelve a estar en el piso | `historia.js` (evento `pistola`, `ponerPistola`, `restaurar`), `armas.js` (`cambiarPorPistola`) |
| 2 · Daño | Cada zombi guarda su vida completa (`VidaIni`) al aplicarle la dificultad. Pistola pequeña: exactamente 2 impactos. Sheriff y escopeta: 1 impacto, a cualquier zombi y con cualquier dificultad. La bala y el perdigón hacen la reacción del puñetazo (tinte rojo, empujón de 280, salpicadura, temblor). Un proyectil no pega a un zombi que ya está a 0 de vida, así que la escopeta da una sola muerte y un solo tumbado. Los proyectiles ya se borraban al pegar: no repiten daño | Eventos de Juego: «Configuración y dificultad» (DifOk), «Combate: pegar» (`Golpes` al crear el proyectil), «Lanzables» (impacto) |
| 3 · Solo Tony | El menú lleva HISTORIA directo a DIFICULTAD con Tony en P1 (teclado, o el mando con que se eligió). Miranda, Alan y César van como bots (NPC). Ya no hay pantalla de equipo ni opción EN LÍNEA para Historia. `historia.js` también lo fuerza al empezar la partida. Animaciones: `tony_pistola_lado` (4 cuadros de `tony_disparar_lado_pistola.gif`) y nueva `tony_escopeta_lado` (de `tony_disparar_lado_escopeta.gif`). La izquierda se voltea, como todas las «de lado»; los GIF «izquierda» son el mismo disparo en espejo y no se usan | Menú (evento de HISTORIA y Escape en dificultad), `historia.js` (`H.remap`), objeto Sup, `generado/sprites/personajes/tony/disparo_*_lado/`, `armas.js` (`A.anim`) |
| 4 · Posición de P1 | Causa: la partida arranca con todos en el punto de aparición general (frente a E-04, fuera del salón) y la historia los movía hasta ~1 s después. Ahora se colocan en el salón desde el primer cuadro, con la pantalla en negro. La cámara compartida cuenta como jugador a quien está sin control en una escena (`Control -2`): sigue a Tony y no a los bots | `historia.js` (`host`, primer cuadro), eventos «Cámara compartida» |
| 5 · No congelar | Ya no se toca `TimeScale` ni `Estado` en videos ni diálogos: zombis, bots, daño, tiempos y derrota siguen. Solo Tony queda sin control mientras dura la escena, y la pausa no abre (`HistBloq`). El control vuelve cuando se **suelta** la tecla con que se avanzó (A también es «usar»). Las zonas y los «usar» de la historia los activa Tony, no los bots | `historia.js` (`congelar` / `devolver`), evento de abrir la pausa |
| 6 · Menú | Orden HISTORIA, ESCAPE, JEFE DE ZOMBIES. Las ilustraciones de Historia y Escape están intercambiadas. Se actualizaron posiciones, textos, resaltado, teclas 1/2/3, clic y cursor. El cursor tenía un error previo: usaba las zonas de cuando había 2 tarjetas. Al entrar, Historia es la elegida. Las escenas de destino no cambian | Eventos de Menu (FASE28-POS, tarjetas, clic, cursor, teclas) |
| 7 · CIC | Se quitó la engrapadora que flotaba sobre el muro (2936, 1625). La puso el generador viejo `fase12_mejoras.py` sobre un escritorio al azar; ningún evento la vuelve a crear. El reloj subió a la pared: y 1690 → 1650 | Instancias de Juego, `mapa/final/mapa_fdiz_props.json` |
| 8 · Joel | La puerta con X 3744, Y 1792, Z 1856 es única: **P38**, entre el CIC y la **Sala 2**. Joel espera en el pasillo libre de la Sala 2, en (3990, 1965). Una sola instancia, mismas animaciones y diálogos | Instancia Profe «joel», `mapa/final/mapa_fdiz_datos.json` (`joel_rescate`) |
| 9 · Casillero | Los «usar» de la historia (casillero de la conserjería, escritorio del director y teléfono) solo se ofrecen y avanzan si Tony está dentro de la sala y la puerta ya se abrió. Se revisa también para los bots | `historia.js` (`H.USAR` con `sala` / `puerta`, `H.puedeUsar`), `usar.js` |
| 10 · Alertas | Inventario en **`gdevelop/ALERTAS.md`** (33 letreros). **Colores sin cambiar**: espera tu clasificación | — |

## 3. Pruebas hechas (separando lo ejecutado de lo revisado)

**Ejecutado en el juego exportado a HTML** con el exportador de GDevelop 5.6. Es el mismo runtime; no fue el editor:
- **Fase 68:** recorrido completo del paso 1 al 12 hasta la victoria; derrota → REINTENTAR → mismo paso; Escape y Jefe arrancan igual. Todo esto fue **antes de la fase 69**.
- **Fase 6:**
  - Orden y figuras.
  - Flechas, teclas 1/2/3, Enter y Esc: cada tarjeta abre su modo.
  - Clic con el ratón en las 3 tarjetas.
- **Fase 3:**
  - Menú → HISTORIA → DIFICULTAD → partida con Tony (P1, teclado) y Miranda, Alan y César como bots, aunque el jugador hubiera elegido otro antes.
  - Animación de pistola al disparar, volteada a la izquierda, y regreso a `tony_quieto`.
  - Animación de escopeta.
- **Fase 4:**
  - Desde el primer cuadro dibujado, Tony está dentro del salón en (5894, 3024).
  - Sigue ahí al recuperar el control.
  - Hay una sola instancia y la cámara lo sigue.
- **Fase 5:**
  - Durante un diálogo `TimeScale` = 1. Los bots se mueven y pelean, y un zombi pegado a Tony le bajó la vida de 120 a 105.
  - El control solo vuelve al soltar la tecla de avanzar.
  - La pausa está bloqueada durante la escena.
- **Fase 1:**
  - Escape: empieza a puños, la pistola está en el piso (6000, 3100), se recoge (9 balas), sale del piso y dispara.
  - Con la escoba en la mano, al pisar la pistola se cambia.
  - Historia: con los bots parados en la zona del escritorio y Tony afuera, la historia no avanza.
- **Fase 2:** disparos reales (ratón) contra las 8 variantes con las 3 armas, en normal.
  - Pistola pequeña: 2 impactos. Sheriff y escopeta: 1.
  - Salpicadura en todos; un escopetazo suma +1 tumbado.
  - En fácil (corredor, gordo, conserje) y pesadilla (corredor, gordo, conserje): 2 impactos de pistola.
- **Fase 7:** el reloj se ve sobre la pared y no hay engrapadora en el CIC.
- **Fase 8:** Joel aparece una vez en la Sala 2 («[F] Hablar con Joel» funciona en Escape). En Historia se une desde ahí.
- **Fase 9:** puerta cerrada y afuera, nada (solo el aviso de la puerta); puerta abierta afuera o lejos, nada; adentro junto al escritorio, «revisar el escritorio» y arranca C08.

**Pruebas automáticas** (sin GDevelop):
- `prueba_historia2.js` 39/39 y `prueba_armas.js` 16/16. Siguen pasando usar, profes, dialogo, cine, canepa, audio, avisos, correr, medios y sfx.
- `prueba_historia.py` es de la Historia vieja de 6 misiones: sus casos de Historia fallan a propósito; los de Escape pasan.

**Errores de exportación:** son los mismos 4 que ya existían (objeto «Canepa», `Gamepads::StickAngle` y dos textos del Menú). No son de estos cambios.

## 4. Lo que falta / sin probar

1. ~~**Fase 10:** clasificar colores en `gdevelop/ALERTAS.md` y luego aplicarlos.~~ Hecho en la fase 70: verde = positivo, amarillo = aviso de evento, rojo = peligro. Falta verlo en el juego.
2. **Recorrido completo de Historia DESPUÉS de la fase 69.**
   - La pausa me llegó a mitad de esa prueba: se probaron el menú, la intro y que los bots no disparan zonas.
   - Falta: recoger la pistola en el paso 3, el combate del paso 4, J1 y J2, el resto de pasos y la defensa final, ahora con el mundo sin congelar.
   - Riesgo a vigilar: con el mundo en marcha, un zombi puede tumbar a Tony mientras ve un video (es lo pedido, pero puede sentirse injusto).
3. Probar **dentro del editor de GDevelop** (vista previa) y **con un mando** físico.
4. **Historia en línea:** ya no se ofrece desde el menú (solo Tony). La sala en línea vieja en modo «historia» (`net_core.js`) quedó sin acceso.
5. **Videos que faltan:** C04, C05, C06, C065, C07, C08, C09 y C10. Mientras tanto sale la pantalla negra de 1 s. Sin C10 se usa `15_victoria.mp4`.
6. **Voz `C65_01_cesar.mp3`:** dura 1.2 s para una frase larga; parece recortada.
7. **Arte provisional:** la reja trasera (valla girada) y la alarma sintetizada.
8. **Tony hacia abajo con pistola:** sigue el cuadro provisional de la fase 62. No hay GIF de disparo hacia abajo ni hacia arriba, ni de escopeta hacia abajo.
9. ~~**Si se vuelve a correr la cadena completa:** el generador viejo `fase12_mejoras.py` vuelve a sembrar engrapadoras al azar.~~ Corregido en la fase 70: `fase12_mejoras.py` ya no pone engrapadora en el escritorio del CIC que la dejaba sobre el muro. Además, `.gitattributes` mantiene los `.js` con saltos de línea Unix, así las pruebas pasan también en Windows.

## 5. Archivos tocados en esta sesión

| Archivo | Qué |
|---|---|
| `gdevelop/FDI-Z/FDI-Z.json` | El proyecto, con las fases 68 y 69 aplicadas |
| `gdevelop/scripts/historia.js`, `historia_datos.js` | Nuevos: lógica y datos de la historia |
| `gdevelop/scripts/fase68_historia.py`, `fase69_correcciones.py` | Nuevos: scripts que aplican los cambios |
| `gdevelop/scripts/prueba_historia2.js` | Nuevo: pruebas |
| `gdevelop/scripts/usar.js`, `profes.js`, `dialogo.js`, `cine.js`, `armas.js`, `prueba_armas.js` | Ganchos para la historia y armas |
| `gdevelop/FDI-Z/assets/historia/` | Voces y videos |
| `gdevelop/FDI-Z/efectos/eventos/alarma_loop.wav`, `audio_manifest.json` | Alarma provisional |
| `gdevelop/historia/` | Los dos documentos de la historia |
| `generado/sprites/personajes/tony/disparo_pistola_lado/`, `disparo_escopeta_lado/` | Cuadros de disparo de Tony (de los GIF) |
| `animaciones_gif/personajes/tony/tony_disparar_*.gif` | Tus 4 GIF de disparo, para poder regenerar los cuadros |
| `mapa/final/mapa_fdiz_datos.json`, `mapa_fdiz_props.json` | Marcador de Joel y reloj |
| `gdevelop/BITACORA.md`, `LEEME_GDEVELOP.md`, `gdevelop/ALERTAS.md`, este archivo | Documentación |

Respaldos (solo en esta computadora; `gdevelop/respaldos/` no se sube): `antes_de_fase68_historia_20261122_2215.json` y `antes_de_fase69_20261122_2307.json`, más los `.js` anteriores en `antes_de_fase69_scripts_20261122_2307/`.
