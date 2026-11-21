# Bitácora 2 · Correcciones del reporte de pruebas de jugabilidad

Fuente: `FDI-Z - Reporte de pruebas de jugabilidad.pdf` (2026-11-21). Se ignoran por ahora: Audio, Diálogos, Menú de inicio.
Se trabaja por bloques; cada uno espera la retroalimentación de Tony antes de pasar al siguiente.
Si se vuelve a correr una fase anterior (fase25…fase42), correr después `fase43_criticos.py` (y las posteriores).

Orden de bloques: **Críticos** (hecho, en revisión) → Medios → Menores → Arte/interfaz y cámara/minimapa → Jugabilidad.

## Bloque 1 · Críticos (fase 43)
Script: `scripts/fase43_criticos.py` (idempotente, último de la cadena; respaldo `respaldos/antes_de_fase43_20261121.json`). Lógica en `scripts/criticos.js`.

### 1. El conserje atraviesa la puerta y muerde
- **Causa real:** el cuadro `atacar_arriba` de ZNormal, ZCorredor, ZGriton, ZGordo y ZConserje no tenía máscara de colisión; usaba el sprite completo (101×124) con el origen 14 px más abajo. Al atacar hacia arriba, `SeparateFromObjects` contra las puertas lo expulsaba al otro lado.
- **Arreglo:** esos cuadros ahora usan la misma máscara de pies que los demás (desplazada 14 px por el origen distinto).
- **Red de seguridad:** `criticos.js → puertas()` (evento justo después de separar zombis de sólidos): si un zombi cambia de lado de una puerta cerrada en un cuadro, vuelve a su última posición buena. No afecta a puertas ya rotas.

### 2. Aliados atorados
`criticos.js → desatasco()`, al final de los grupos de bots (bots y profes aliados, Control −1). Si quieren moverse y avanzan menos de 7 px en 1 s, escalan:
1. 1.º–2.º intento: paso lateral de 0.6 s hacia una dirección libre (y ruta nueva).
2. 3.º–4.º: si están en una celda bloqueada, salen a la libre más cercana; salto de 120 px por la ruta.
3. 5.º–6.º: salto de 260 px por la ruta.
4. 7.º: reaparecen a 90–210 px de un humano vivo, con línea de vista.
Los saltos se detienen antes de cualquier puerta cerrada o muro. No actúan si están usando, curando, reviviendo o atacando. La escalera se reinicia tras 9 s sin atorarse. Valores en `criticos.js → CFG`.

### 3. Oscuridad persistente al salir del salón
- **Causa:** la capa negra inicial no se quitaba hasta que alguien estuviera 80 px fuera del salón, y luego tardaba 1.3 s en desvanecerse; al dar un paso afuera todo seguía negro.
- **Arreglo:** margen de 8 px; además se despeja en cuanto se rompe la puerta del salón de arranque (P03 si ya vieron la cinemática, P06 si no); desvanecimiento 450/s (≈0.6 s).


## Bloque 1 · Críticos — ronda 2 (retroalimentación de Tony, misma fase 43)
Si se vuelve a correr `fase42_correr.py` (embebe `correr.js`), correr después `fase43_criticos.py`.

### 1. Conserje: daño a través de la puerta, pasillo y bots que rodean
- **Causa del conserje atorado y de los bots que rodean:** la entrada al pasillo de la conserjería (hueco de 32 px de alto entre el borde del muro y el muro de abajo, y el pasillo de 64 px que lleva a la puerta) quedaba **cerrada para A\*** (holgura de 18 px a cada lado, pero los pies miden 14 px de alto). Comprobado con la rejilla real: las rutas hacia y desde ese pasillo salían *parciales* (sin camino). Ahora `criticos.js → abrirPasos()` abre, una vez por escena, las celdas que con la holgura real de los pies son transitables **y** unen dos zonas que quedaban separadas. Abre 90 celdas en 10 pasos de todo el mapa (el de la conserjería es el más largo); las 3 rutas de prueba pasan a completas. No toca nada más.
- **Daño a través de la puerta:** el evento original ya revisaba 7 puntos de la línea de vista. Se añadió un veto exacto (`criticos.js → golpe()`, evento "FDIZ-FASE43-GOLPE" justo antes del que quita vida): si zombi y objetivo quedan de lados opuestos de una puerta (puerta alargada 10 px a lo largo) y el segmento la toca, el golpe no cuenta. *Aviso:* no pude reproducir el daño en el código original; el veto cubre el caso, pero si sigue pasando necesito saber desde qué lado y con qué puerta.
- Se mantienen: máscara de `atacar_arriba` y el regreso a la posición anterior si un zombi cruza una puerta cerrada.

### 2. Ojo de oferta (Alan)
- Era un evento de GDevelop que, al terminar, dejaba las zonas en opacidad 190 (no volvían a 255) y calculaba el alcance con la distancia al **centro** de la zona (900 px): zonas grandes cercanas no se difuminaban "a veces".
- Ahora `criticos.js → ojo()`: dura **6 s**, al acabar las zonas reveladas vuelven a oscurecerse por completo (0.4 s) y arranca el enfriamiento de 30 s (cronómetro "ojo"). Alcance: 900 px al **borde** de la zona. Si Alan cae o se infecta durante el efecto, termina en ese momento. La activación (cada 30 s) sigue en el evento de siempre. Valores: `criticos.js → K.OJO`.

### 3. Los bots corren solos
`correr.js` (VER 3) → `pideBot()`. Misma estamina que los humanos (15, gasta 3/s, se recupera tras 0.8 s, agotado hasta 5) y su barra aparece en su panel. Corren cuando:
- **huyen** (`Huye = 1`, modo Jefe), con cualquier estamina > 0; o
- van **lejos de su meta** (> 420 px, para alcanzar al grupo) con estamina ≥ 7; paran al estar a < 190 px o con estamina ≤ 0.5 (histéresis, sin parpadeo).
No corren si: usan, atacan, curan o reviven; hay un zombi vivo a < 320 px (pelean, no corren hacia él) salvo que huyan; son profes aliados (Jugador > 4) o están caídos. El desatasco no se ve afectado (cuenta avance en px, no velocidad).
Pruebas: `node gdevelop/scripts/prueba_correr.js` (16 casos).

### Sin probar
Nada se corrió dentro de GDevelop. Verificado: `node --check` de todo el JS del proyecto (34 eventos), pruebas con objetos simulados (zombi revertido, paso lateral, veto de puertas, Ojo, bots corriendo), rutas A\* sobre la rejilla real y md5 estable en 3 corridas de fase42+fase43. Falta probar en juego: conserje saliendo del pasillo y bots entrando, daño con puerta cerrada, Ojo de Alan (zonas cercanas y re-oscurecer), bots corriendo (que no pasen de largo a su meta ni se atoren más rápido).

## Corrección fuera de bloque · Vallas del sur (fase 44)
Pedido de Tony (con captura): el sur del mapa debe estar cerrado por vallas blancas y el jugador no debe poder salir por la abertura junto al arco de entrada.
- **Causa:** la fila de vallas del sur (choque `ChoqueMueble` 128×20 en y = 5226 + sprite `hitos/reja_blanca` en y = 5246) tenía huecos sin choque ni reja: x 1920–2432 (la entrada principal junto al arco, 512 px), x 2688–2816 y x 4384–5600 (de muro a muro, junto al estacionamiento).
- **Cambio** (`scripts/fase44_valla_sur.py`, idempotente, va después de fase43; respaldo `respaldos/antes_de_fase44_20261121.json`): 15 tramos nuevos con el mismo patrón (choque en x, 5226; reja visible en x + 64, 5246) = 30 instancias. No se tocó ningún evento ni la puerta de cristal P57 (2944, 5216), que es una puerta del edificio.
- **Comprobación:** inundación de la rejilla (celdas de 16 px, holgura 12 px) desde el arco: antes salía a la calle por el hueco; ahora la única vía al exterior es la reja principal del oeste (x 128, y 3584, "se abre al terminar ¡Aguanten!"), que es parte del diseño.
- **Sin probar en el juego.** Falta verlo: que las rejas nuevas se vean alineadas con las existentes (el tramo de x 4320–5600 empieza 64 px dentro del muro de x 4352, y el de x 2688–2816 se encima con el borde del edificio de x 2496–2720).

## Correcciones fuera de bloque · arcos y bot 4 (fases 42 y 45)
- **Arcos (fase 45, `scripts/fase45_quitar_arcos.py`):** quitados los dos arcos del mapa: `arco_entrada` (grande, sur, junto al directorio) y `arco_salida` (chico con reja, x 6912, y 4864), con sus choques y el marcador `arco_entrada`. 5 instancias; ningún evento las usaba. Respaldo `antes_de_fase45_20261121.json`.
- **Bot 4 no corría (`correr.js` VER 4):** el evento "Bots" detiene a cada bot a una distancia distinta de su meta (90 + 45 × Jugador: 180 / 225 / 270 px), pero `pideBot` usaba un umbral fijo de 420 px para empezar y 190 px para dejar de correr. El bot 4 (270 px) nunca bajaba de 190, así que su estado de carrera se quedaba trabado (corría de más hasta agotarse y luego no volvía a arrancar). Ahora se mide el exceso sobre su propia distancia de parada: empieza a correr a +150 px y deja de correr a +25 px. Prueba nueva: bots 2, 3 y 4 (17 casos, todos bien).
  - *Aviso:* no vi el fallo en el juego; es la causa que encontré leyendo el código. Si el bot 4 sigue sin correr, necesito saber en qué situación (siguiendo a Tony, huyendo en modo Jefe, o tras pelear).

## Bloque 2 · Medios (fase 46)
Script: `scripts/fase46_medios.py` (idempotente, va después de la fase 45). Lógica nueva en `scripts/medios.js` (módulo `gdjs.fdizMedios`, se inserta arriba de los eventos de Juego). Pruebas: `scripts/prueba_medios.js` (9 casos, todos bien). Respaldo: `respaldos/antes_de_fase46_20261121.json`.

**4 · Oscuridad inestable sobre los salones.** Causa probable: el evento que decidía si un personaje se dibuja por delante de la oscuridad (capa `SupervivientesBorde`) usaba el tamaño del dibujo, que cambia en cada cuadro de animación, así que saltaba de capa. Ahora `borde()` usa una caja fija desde los pies, "pies dentro de la sala = capa Juego", y solo cambia de capa tras 3 cuadros seguidos.
**5 · Caminar de lado bugueado.** Antes se comparaba |vx| con |vy| en cada cuadro y se volteaba el sprite con cualquier velocidad mínima. `anim()` ahora usa histéresis en diagonales (factor 1.3), velocidad mínima de 12 y solo cambia animación/volteo cuando realmente cambia.
**6 · Llaves.** Los bots ya no las eligen como destino (condición `Tipo != "llaves"`). Si un no humano suma progreso, se deshace. Aviso cuando hay un jugador cerca ("mantén F|A junto a las llaves"), muestra "<Nombre> (P#) toma las llaves... N%" y al terminar "¡<Nombre> (P#) tomó las llaves!".
**7 · Habilidad E trabada.** Causa probable: la animación del especial duraba 0.5 s pero el bloqueo (Atacando) termina a 0.28 s, y se cortaba a mitad. Los 5 cuadros de los 9 personajes principales ahora duran 0.05 s (0.25 s en total).
- *Avisos:* 4 y 7 son hipótesis por lectura de código; no los reproduje en el juego. Si persisten, necesito saber en qué sala/personaje ocurre. Los de los profes (joel/justino/canepa) no se tocaron.
- Verificación: 37 eventos JavaScript sin errores de sintaxis; cadena fase42→46 ×3 con el mismo md5; pruebas de correr (17), medios (9) y profes (16) pasan.

## Corrección fuera de bloque · porcentaje de 101% (fase 47)
- **Causa:** los textos "Usando… N%", "Revisando… N%" y "Curando a P#… N%" calculaban `round(100 * progreso / total)` sin tope; en el cuadro en que el progreso sobrepasa el total (el último incremento) salía 101%.
- **Arreglo (`scripts/fase47_tope_100.py`):** los 6 textos (usando, revisando, curando P1–P4) ahora usan `min(100, …)`. Las llaves (fase 46) ya tenían tope. Respaldo `antes_de_fase47_20261121.json`; mismo md5 en 2 corridas.

## Bloque 3 · Menores (fase 48)
Script: `scripts/fase48_menores.py` (idempotente, después de la fase 47), escena `Menu`, paso "equipo" (elegir personaje). Respaldo `antes_de_fase48_20261121.json`; mismo md5 en 2 corridas.

**8 · Reasignar al Player 1 tras elegir los 4.** Causa: los clics sobre las celdas solo funcionaban mientras quedara algún jugador pendiente (`Cola > 0`); con todos confirmados `Cola = 0` y el clic se ignoraba. Ahora 8 eventos nuevos (uno por personaje, insertados tras los de clic derecho de las celdas) atienden el clic izquierdo cuando `Cola = 0` y asignan ese personaje al Player 1 (`S1Pj`, `S1Ok = 1`). Si el personaje ya lo tiene otro jugador confirmado, no pasa nada (misma regla que ya existía).
- *Límite:* solo cambia al Player 1 y solo con el ratón (lo pedido: "tocar a otro"). Los demás jugadores se cambian como antes: clic derecho sobre su personaje para soltarlo y volver a elegir.

**9 · Botón de salir.** Nuevo botón "SALIR (ESC)" arriba a la izquierda (40,40; 280×84), visible solo en el paso de elegir personaje, con brillo al pasar el ratón. Al hacer clic hace lo mismo que ESC/B: vuelve a "Únanse" (o al tipo de jefe si el modo es Jefe). Objetos `BtnSalir` (marco rojo de dificultad reutilizado) y `TxtSalir`.
- *Sin probar en el juego:* posición del botón y que el texto quede centrado; si no se ve bien lo ajusto.

### Ajustes a Menores (ronda 2, fase 48)
- **Calavera del botón Salir:** estaba dibujada dentro de la imagen del marco "difícil" que reutilicé. Nueva imagen `assets/interfaz/ui_boton_salir_p48.png` (mismo marco rojo, sin calavera; recurso `p48_BtnSalir`).
- **Soltar con clic izquierdo:** el clic izquierdo sobre un personaje ya elegido por un bot o por el jugador de teclado/ratón lo suelta (igual que el clic derecho) para elegir otro. Son 8 eventos copiados de los de clic derecho, puestos después de los de reasignar al Player 1 para que no choquen en el mismo cuadro. Los jugadores con mando no se sueltan con el ratón (igual que con el clic derecho).
- Mismo md5 en 2 corridas de la cadena fase42→48.

### Revertido: soltar con clic izquierdo (fase 48)
Rompía la selección: al hacer clic izquierdo en un personaje libre, el evento que lo asigna al bot y el de "soltar" corrían en el mismo cuadro, y el segundo lo soltaba al instante. Se quitó por completo; soltar un personaje elegido vuelve a ser **solo con el clic derecho**. Se mantienen el botón Salir sin calavera y la reasignación al Player 1 con todos confirmados.

## Bloque 4 · Arte e interfaz (fase 49)
Script: `scripts/fase49_arte.py` (idempotente, después de la fase 48). Respaldo `antes_de_fase49_20261121.json`; mismo md5 en corridas repetidas.
- **Habilidad E más grande:** en el juego la Habilidad es Q y el Especial es E, así que se agrandó el efecto del Especial (los `*_esp` de `EfectoPj`) ×2.6 (eran ~100 px sobre un personaje de ~100 px). Un evento JavaScript junto al que borra los efectos fija la escala; la habilidad Q no cambió.
- **Cámara más cercana:** el tope del zoom sube de 1.4 a 1.75 (+25 %). El piso (0.7) no cambia, para que los aliados lejanos sigan en pantalla; por eso el minimapa (bloque Jugabilidad) ayudará a orientarse.
- **Pantalla de controles:** las imágenes actuales (`p27_ctl_teclado`, `p27_ctl_mando`, 720×300) están hechas con formas simples. Yo no genero imágenes: dejé los prompts en inglés en `gdevelop/prompts_controles.md`. Al guardar `ctl_teclado_ia.png` / `ctl_mando_ia.png` en `assets/interfaz/` y correr la fase 49, se escalan a 720×300 y reemplazan a las actuales.
- **Fuera de este bloque:** la animación de correr se deja en segundo plano (según el reporte); el minimapa va en Jugabilidad.
- *Sin probar en el juego:* el tamaño ×2.6 y el zoom 1.75 son valores a ojo; fáciles de ajustar (`ESC_ZOOM`, `TOPE_ZOOM` en el script).
- **Prompts de controles actualizados:** `prompts_controles.md` ahora trae la tabla de controles vigentes (Shift/LB/L3 = correr, ya no "caminar despacio"; clic izq. pegar, clic der. o R lanzar, cursor apuntar, Esc/P y Start pausa; mando: stick izq. mover, stick der. apuntar, X pegar, A usar, Y habilidad, RB especial, B lanzar) y los dos prompts reescritos con esos textos.
- **Imágenes de controles puestas (fase 49):** `ctl_teclado_ia.png` (981×441) y `ctl_mando_ia.png` (1024×1024, recortada a 1024×585 quitando el margen vacío) → `p49_ctl_teclado.png` (712×320) y `p49_ctl_mando.png` (560×320), escaladas sin deformar y centradas en cada mitad de la pantalla de controles (centros x 510 y 1410, y 190). Mismo md5 en 2 corridas.
- **Prompts de controles v3:** reescritos con distribución exacta de teclas y botones, qué rótulo toca qué botón y un prompt de corrección para editar las imágenes ya generadas (errores vistos: "pegar" en B, "lanzar" junto a A, "pausa" en View, "mover" solo sobre W).
- **Imágenes de controles dibujadas con código (no IA):** `scripts/dibujar_controles.py` dibuja en estilo pixel art el teclado + ratón (712×320) y el mando Xbox (560×320) con los controles vigentes y cada rótulo tocando solo su tecla/botón (X pegar, B lanzar, A usar, Start pausa, Shift/LB/clic del stick = correr, W A S D = mover, cursor = apuntar). Salen como `ctl_teclado_ia.png` / `ctl_mando_ia.png` y la fase 49 las aplica. Las generadas con IA por Tony quedaron como `ctl_*_ia_original.png`.

### Pantalla de controles con imágenes IA nuevas (fase 49, ronda 3)
- Fuentes de Tony: `assets/interfaz/ctl_teclado_ia_fuente.png` y `ctl_mando_ia_fuente.png` (1536×688).
- Verificación: mando correcto (stick izq. mover, stick der. apuntar, X pegar, A usar, Y habilidad, RB especial, B lanzar). Teclado: Esc/P pausa, Q habilidad, E especial, R lanzar, F usar (mantener), Shift correr, ratón pegar/lanzar/apuntar correctos.
- Retoque (`scripts/retocar_controles.py`, debe correr antes de `fase49_arte.py`): el MOVER superior tapaba W y E; se borró y quedó una sola etiqueta "MOVER (WASD)" abajo (el corchete solo abarca S–D porque Shift bloquea extenderlo hasta A).
- Pendiente menor: en el mando, la línea de PEGAR cruza la B roja antes de llegar a X (no se tocó).
- `fase49_arte.py` las escala a 714×320 y coloca CtlTeclado (x=153) y CtlMando (x=1053), y=190. `dibujar_controles.py` queda obsoleto.
- No probado en juego.

### Pantalla de controles: sin texto inferior e imágenes más grandes (fase 49, ronda 4)
- Se vació el texto bajo las imágenes (`TxtPausaCtl1/2` = "") en `fase49_arte.py`.
- Imágenes de 320 a 400 px de alto (893×400 c/u), y=300, centradas en pantalla con 30 px de separación (x=51 y x=977). Cadena idempotente (md5 estable). No probado en juego.

## Bloque 5 · Jugabilidad y mecánicas — parte 1: minimapa (fase 50)
Script: `scripts/fase50_minimapa.py` (idempotente, último de la cadena; respaldo `respaldos/antes_de_fase50_20261121.json`). Lógica en `scripts/minimapa.js`.
- Minimapa a la derecha de la pantalla (x 1596, y 446, 300×184) en el modo normal (el Jefe conserva el suyo). Reusa el sprite `Minimapa` y un pintor nuevo `MmDib`.
- Muestra: aliados con el color de su jugador (humanos más grandes), profes aliados en lila, caídos/mordidos en gris, objetivo actual (cuadro amarillo que pulsa) y el cuadro de lo que ve la cámara. **No muestra zombis** a propósito.
- Se oculta en pausa/cinemáticas/final. Tecla **M** lo muestra u oculta.
- *Sin probar en el juego:* posición/tamaño a ojo (`MM` en minimapa.js); en línea podría chocar con el ocultado de `net_core.js`.

### Parte 2 · Habilidades de aliados con clic (fase 51)
Script: `scripts/fase51_aliados_hab.py` (idempotente, después de fase50; respaldo `respaldos/antes_de_fase51_20261121.json`). Lógica en `scripts/aliados_hab.js`, evento justo después del grupo "Entrada (teclado y controles)".
- Clic izquierdo en el icono **Q** (habilidad) o **E** (especial) del panel de un aliado bot → el bot la usa (`PideHab`/`PideEsp`). En recarga: destello rojo y no pasa nada; lista: destello verde. Al pasar el cursor sale un marco dorado.
- Los bots siguen usándolas solos con su criterio (`bots_habilidades.js`); el clic es un "úsala ya". Mientras el cursor está sobre un icono, el clic no golpea.
- Solo con ratón (los iconos están en pantalla); no actúa en cliente en línea (NetRol 2) ni en modo Jefe. *Sin probar en el juego.*
- **Ronda 2 (iluminado):** el marco usaba coordenadas fijas y no cubría todo el icono; ahora toma la caja real del `HudIcono` (posición y tamaño). El hover es un halo que respira (cian si está lista, ámbar si recarga), brillo interior, esquinas que se abren y cierran y destellos que recorren el borde. Al hacer clic: listo = ondas verdes, rayos y relleno que se desvanece; en recarga = X roja que tiembla. Sin probar en el juego.
- **Ronda 3 (iluminado simple, por pedido de Tony):** se quitaron halo, esquinas, destellos, ondas y X. Hover = latido suave (relleno y marco que laten, blanco si está lista, ámbar si recarga); clic = destello corto de 0.3 s (verde lo usa, rojo en recarga). Se conserva la caja real del icono. Sin probar en el juego.
- **Ronda 4 (iluminado):** Tony pidió volver al halo de la ronda 2 sin las bolitas que giran. Hover = halo que respira + brillo interior + marco fino + esquinas que se abren y cierran; clic = ondas/rayos verdes (lista) o X roja que tiembla (recarga), 0.55 s. Sin probar en el juego.

### Parte 3 · Lanzables: distracción + daño y cuadro del primer lanzable (fase 52)
Script: `scripts/fase52_lanzables.py` (idempotente, después de fase51; respaldo `respaldos/antes_de_fase52_20261121.json`). Lógica en `lanz_impacto.js`, `lanz_frame.js`, `lanz_entrada.js`.
- **Distracción:** al caer un **balón** (radio 650 px, 5 s) o un **libro** (550 px, 4 s) los zombis cercanos (normal, corredor, gritón, gordo; no el conserje) que perseguían, paseaban o estaban de guardia pasan al estado `distraido` y van por ruta (Pathfinding) al punto de impacto. Terminan si se acaba el tiempo o hay un sobreviviente de pie a menos de 150 px (vuelven a perseguir). La engrapadora no distrae.
- **Daño:** además del golpe directo de siempre, daño en área en el punto de impacto: balón 5 (radio 120), libro 8 (radio 110), con número de daño y crédito de kills. Onda de impacto dibujada en el mundo (0.7 s).
- **Cuadro explicativo:** la primera vez que un jugador **humano** recoge un lanzable, sale un cuadro que **detiene el juego** (TimeScale 0, solo sin red) con cómo lanzar, qué hace cada objeto y la distracción. Se cierra con clic, Enter, Espacio, Esc o A (mando); no se puede cerrar en los primeros 0.5 s. El clic que lo cierra no golpea (movimiento y golpes bloqueados mientras está abierto y 0.4 s después) y Esc/P/Start no abren la pausa mientras está (usa `ProfDlg`). No vuelve a salir en la partida: la bandera es la variable de escena `LanzInfo`, que vuelve a 0 al iniciar o reiniciar la partida, así que sale de nuevo tras recoger el primer lanzable de la partida nueva.
- *Límites:* en línea el cuadro no sale (no se detiene el juego); la distracción sí funciona en host/sin red. *Sin probar en el juego:* `moveTo` del Pathfinding, radios, tiempos y daños son valores a ojo (`CFG` en lanz_impacto.js). Los bots y la IA de grupo ven a los zombis distraídos como no-amenaza mientras dura.

### Parte 4 · Flechas de aliados fuera de pantalla (fase 53)
Script: `scripts/fase53_flechas.py` (idempotente, después de fase52; respaldo `respaldos/antes_de_fase53_20261121.json`). Lógica en `scripts/flechas.js`, evento justo después del minimapa.
- Cada aliado vivo (alumnos y profes) que sale de lo que ve la cámara obtiene una **flecha en el borde de la pantalla** que apunta hacia él, con su color de jugador y su nombre. Caídos/mordidos: flecha gris/roja que parpadea y el aviso "(caído)" / "(mordido)".
- Se oculta en pausa, cinemáticas, modo Jefe y con el cuadro de lanzables abierto. Aliados atorados: ya cubiertos por el desatasco del bloque Críticos (`criticos.js → desatasco()`); no se tocó la IA en esta parte.
- *Sin probar en el juego:* márgenes (70 px) y tamaño de flecha a ojo; las flechas pueden quedar sobre los paneles de las esquinas.
- **Corrección fase 53:** el pintor de GDevelop no tiene `drawTriangle` (error "dib.drawTriangle is not a function" y el juego se trababa). La flecha ahora se dibuja con líneas (relleno + borde).

### Icono del lanzable según el objeto (fase 54)
Script: `scripts/fase54_iconos_lanzables.py` (idempotente, después de fase53; respaldo `respaldos/antes_de_fase54_20261121.json`).
- El panel mostraba siempre el balón (`HudInv` solo tenía la animación `lanzable`). Ahora hay `lanzable_balon`, `lanzable_libro` y `lanzable_engrapadora` (`assets/interfaz/hud/ico128_lanzable_*.png`; libro y engrapadora salen de los sprites del objeto, recortados y escalados a ~100 px dentro de 128×128) y un evento por jugador que elige la animación con `Sup.Lanz`. *Sin probar en el juego.*
