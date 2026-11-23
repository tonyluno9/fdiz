# FDI-Z · Inventario de letreros de alerta (fase 10, para clasificar colores)

**Estado:** colores **aplicados en la fase 70** (2026-11-22) con la clasificación aprobada (verde = positivo, amarillo = aviso de evento, rojo = peligro). La columna «Color actual» ya muestra el color nuevo de cada letrero.

Cómo funcionan:
- Todos los letreros pasan por la variable de escena `Banner` y se muestran con el objeto `TxtBanner` (escena **Juego**; grupo de eventos "HUD").
- El color lo decide `gdevelop/scripts/avisos.js` (fases 63 y 70) según el texto. Se aplica solo cuando el texto cambia (`__fdizAviso`), así que un letrero nunca hereda el color del anterior.
  - **Rojo** (`255;80;80`): infección (mordido, infectado, se convirtió en zombi), «la FDI se está llenando», «¡ROMPIÓ LA PUERTA!» y «… QUEDÓ FUERA DE COMBATE».
  - **Amarillo** (`255;240;150`, el mismo de los avisos bajo el centro): 2, 3, 4, 7, 17, 18, 22, 23, 24, 26, 30, 31 y 32.
  - **Verde** (`110;230;110`): todo lo demás.
- Para cambiar un color: edita las listas `PELIGRO` / `AVISO` de `avisos.js`, la tabla de `prueba_avisos.js`, y vuelve a correr `python gdevelop/scripts/fase63_avisos.py` (con GDevelop cerrado) y `node gdevelop/scripts/prueba_avisos.js`.
- No hay otras escenas con letreros: Titulo, Menu, Resultados y Online no usan `Banner`.
- Busqué en todos los eventos de todas las escenas y en todos los `.js` del proyecto, incluido el JS escrito dentro de los eventos.

Para clasificar, responde con el número y el color. Por ejemplo: «1 verde, 2 amarillo, 14 rojo…».

| # | Texto exacto | Qué lo activa | Dónde | Color actual |
|---|---|---|---|---|
| 1 | `¡Tarjeta! Las puertas electrónicas abren en 1 s` | Un jugador toma la tarjeta electrónica (Secretaría) | Eventos · grupo «Puertas: tipos y golpes» | Verde |
| 2 | `¡SE FUE LA LUZ!` | Escape/Jefe: empieza el objetivo «luz». Historia: el apagón del paso 6 | Eventos · «Objetivos y flecha» y `historia.js` (evento `apagon`) | Amarillo |
| 3 | `NUEVO OBJETIVO` | Escape/Jefe: se crea un objetivo nuevo | Eventos · «Objetivos y flecha» | Amarillo |
| 4 | `¡AL ESTACIONAMIENTO!` | Escape/Jefe: después del último objetivo empieza el final. Historia: dura un instante al iniciar la defensa del paso 11 | Eventos · «Objetivos y flecha» | Amarillo |
| 5 | `¡Servidor prendido! Ahora la llamada` | Escape: se prendió el servidor del SITE | Eventos · «Objetivos y flecha» | Verde |
| 6 | `¡OBJETIVO CUMPLIDO!` | Escape/Jefe: se cumple un objetivo | Eventos · «Objetivos y flecha» | Verde |
| 7 | `¡AGUANTEN!` | Alguien llega al camión: empieza el final. Al instante lo reemplaza el 30 | Eventos · «Final ¡Aguanten!» | Amarillo |
| 8 | `¡ESCAPARON!` | Victoria (Escape/Jefe por eventos; Historia en el paso 12) | Eventos · «Final ¡Aguanten!» y `historia.js` (evento `victoria`) | Verde |
| 9 | `¡FESTÍN! Los zombies van a la nevería` | Habilidad de Tony (cocinar) cerca de la nevería | Eventos · «Habilidades, especiales y pasivas» | Verde |
| 10 | `Sabía a... facultad.` | Habilidad de Castillo (tragar a un zombi) | Eventos · «Habilidades, especiales y pasivas» | Verde |
| 11 | `Aquí no pueden pasar... excepto yo.` | Habilidad de Carlos junto a una puerta | Eventos · «Habilidades, especiales y pasivas» | Verde |
| 12 | `¡LA FDI SE ESTÁ LLENANDO!` | Sube el nivel de infestación | Eventos · «HUD» | **Rojo** |
| 13 | `¡P` + N + ` MORDIDO!` → «¡P1 MORDIDO!» … «¡P4 MORDIDO!». Cambia N, el jugador (1–4) | A un jugador lo muerden (12 % por golpe). También F1 + 7 en el modo presentación | Eventos · «Compañeros mordidos» | **Rojo** |
| 14 | `¡P1 SALVADO!`, `¡P2 SALVADO!`, `¡P3 SALVADO!`, `¡P4 SALVADO!` | Curan a un jugador mordido | Eventos · «Compañeros mordidos» (un evento por jugador) | Verde |
| 15 | `¡P1 SE CONVIRTIÓ EN ZOMBIE!` … `¡P4 SE CONVIRTIÓ EN ZOMBIE!` | Pasan 35 s mordido sin cura | Eventos · «Compañeros mordidos» (un evento por jugador) | **Rojo** |
| 16 | `¡` + QUIÉN + ` tomó las llaves!`. QUIÉN = «Nombre (Pn)», por ejemplo «¡Tony (P1) tomó las llaves!» | Escape: alguien toma las llaves del conserje | `medios.js` (`M.llaves`) | Verde |
| 17 | Texto del objetivo en MAYÚSCULAS. Cambia según el paso: `REVISA EL ESCRITORIO DEL PROFE`, `LLEGA AL CIC`, `USA EL TELÉFONO DEL CIC`, `ENCUENTRA LA SALA DEL CONSERJE`, `REVISA EL CASILLERO DEL CONSERJE`, `BUSCA A OTRO PROFESOR: LA NEVERÍA`, `CONSIGUE LA LLAVE EN LA OFICINA DEL DIRECTOR`, `LLEGA AL AUTOBÚS` | Historia: empieza un paso con objetivo | `historia.js` (función `objetivo`) | Amarillo |
| 18 | `¡RECOGE LA PISTOLA DEL PROFE!` | Historia, paso 3: la pistola queda en el piso | `historia.js` (evento `pistola`) | Amarillo |
| 19 | `¡ROMPIÓ LA PUERTA!` | Historia, paso 4: el zombi rompe la puerta del salón | `historia.js` (evento `irrumpe`) | **Rojo** |
| 20 | `¡` + NOMBRE + ` TIENE LA ESCOPETA! Volvió la luz`, por ejemplo «¡TONY TIENE LA ESCOPETA! Volvió la luz». Cambia NOMBRE, quien la recibe | Historia, paso 8 | `historia.js` (evento `escopeta`) | Verde |
| 21 | `La nevería: el equipo recupera toda la vida` | Historia, paso 9 (Justino) | `historia.js` (evento `justino`) | Verde |
| 22 | `¡LLAVE DE LA REJA` [+ ` Y PISTOLA PARA ` + NOMBRE] + `! El conserje los persigue`, por ejemplo «¡LLAVE DE LA REJA Y PISTOLA PARA CÉSAR! El conserje los persigue». La parte entre corchetes sale solo si alguien recibe la pistola | Historia, paso 10 | `historia.js` (evento `llave`) | Amarillo |
| 23 | `¡VIENEN MÁS!` | Historia, defensa del autobús a los 30 s | `historia.js` (espera `defensa`) | Amarillo |
| 24 | `¡LA ÚLTIMA OLEADA!` | Historia, defensa del autobús a los 60 s | `historia.js` (espera `defensa`) | Amarillo |
| 25 | `¡` + PROFE + ` SE UNE AL EQUIPO! El equipo se cura`. PROFE = JOEL, JUSTINO o CANEPA | Se recluta a un profe (Escape/Jefe). Historia: Joel en el paso 5 | `profes.js` (`reclutar`) | Verde |
| 26 | PROFE + ` SE QUEDÓ ATRÁS` | Escape/Jefe: se decide dejar al profe | `profes.js` (`rechazar`) | Amarillo |
| 27 | `¡` + PROFE + ` SE CONVIRTIÓ EN ZOMBI!` | Un profe se convierte | `profes.js` (`convertir`) | **Rojo** |
| 28 | PROFE + ` QUEDÓ FUERA DE COMBATE` | Un profe aliado caído no fue revivido a tiempo | `profes.js` (`logicaHost`) | **Rojo** |
| 29 | `¡` + PROFE + ` SALVADO!` | Curan a un profe mordido | `profes.js` (`logicaHost`) | Verde |
| 30 | `¡AGUANTEN! Canepa repara el autobús` | Historia: empieza la defensa del paso 11 | `profes.js` (letrero del final) | Amarillo |
| 31 | `¡AGUANTEN! Canepa repara el camión` | Escape/Jefe: empieza el final con Canepa aliado y de pie | `profes.js` (letrero del final) | Amarillo |
| 32 | `¡AGUANTEN! Reparen el camión y resistan` | Escape/Jefe: empieza el final sin Canepa aliado | `profes.js` (letrero del final) | Amarillo |
| 33 | `¡` + PROFE + ` MORDIDO!` (`PROFE` si no se sabe el nombre) | Muerden a un profe aliado | `profes.js` (`API.mordidas`) | **Rojo** |
| — | `""` (vacío) | Modo Jefe: borra el letrero al unirse con un control | Eventos · «Unirse con control» | — (no se ve) |

**Letreros que existen en los eventos pero ya no aparecen** (Historia de 6 misiones de las fases 55/61, reemplazada por la fase 68). Se listan para que no se pierdan:
- `OBJETIVO n/total · LLAMAR DESDE EL CIC`, `· ¡SE FUE LA LUZ! INTERRUPTORES DEL CIC`, `· LAS LLAVES DEL CONSERJE`, `· COMIDA A LA NEVERÍA`, `· HABLAR CON CANEPA EN EL CAMIÓN` y `· BUSCAR LA GASOLINA`.
- `¡OBJETIVO n/total CUMPLIDO!`.
- En todos ellos cambian n y total. Hoy son verdes.

**Otros avisos que no son el letrero** (no van en `TxtBanner`; dime si también quieres clasificarlos):
- Avisos amarillos (`255;240;150`) bajo el centro de la pantalla, en Historia:
  - `Pasa sobre la pistola para recogerla`
  - `Clic izquierdo (o gatillo del mando) para disparar`
  - `La reja trasera está cerrada con llave`
- Las indicaciones «Mantén F para …» sobre el personaje (`usar.js`): amarillo claro y, si es un aviso como «Puerta restringida…», naranja (`255;150;120`).

Cuando me des la clasificación:
- Cambiaré solo los colores.
- Texto, duración, posición y condiciones de aparición se quedan igual.
- Se respetará la regla de no heredar el color del letrero anterior.
