# FDI-Z · Reporte de generación de sprites

## Generaciones

- Generaciones usadas: **180 de 220** (180 del manifiesto + 40 de margen).
- Intentos que no terminaron bien: 1.
  - `tonyfuerte__pegar_lado` intento 2: processing
- **Ojo con el cobro:** la corrida de la fase 2 la detuvo Claude Code por falta de memoria. Hasta **3 trabajos** que estaban en curso pudieron cobrarse en WaveSpeed sin quedar en el log (en esa versión del script la línea se escribía al terminar). Revisa el historial de WaveSpeed: el uso real puede ser hasta 3 generaciones mayor que el de arriba. Desde entonces el script escribe una línea "enviado" con su request_id antes de esperar el resultado.
- Trabajos sin imagen al final: 21 (21 de profes, pendientes a propósito).
- Regenerados tras la revisión (REHACER): 20: `alessandro__pegar_abajo`, `carlos__caminar_lado`, `carlos__pegar_abajo`, `castillo__caminar_lado`, `castillo__pegar_abajo`, `conserje__caminar_lado`, `conserje__golpe_morir`, `corredor__caminar_lado`, `corredor__atacar_abajo`, `gabo__pegar_abajo`, `gordo__caminar_lado`, `gordo__atacar_lado`, `griton__atacar_abajo`, `miranda__caminar_lado`, `miranda__efecto_especial`, `normal__atacar_abajo`, `normal__golpe_morir`, `tony__caminar_lado`, `tonyfuerte__caminar_lado`, `tonyfuerte__pegar_lado`.

## Resultado

- **OK:** 124
- **REVISAR:** 30
- **REHACER:** 5
- **PENDIENTE:** 21

## Lo que hay que revisar

| Entidad | Animación | Calificación | Razón | GIF | Tira |
|---|---|---|---|---|---|
| tony | personajes/pegar_lado | REVISAR | puñetazo hacia la derecha correcto, pero el cuerpo está en 3/4 de frente en vez de perfil puro | `generado/preview/personajes/tony/pegar_lado.gif` | `generado/sprites/personajes/tony/pegar_lado/pegar_lado_tira.png` |
| miranda | personajes/pegar_lado | REVISAR | golpe claro hacia la derecha pero la cara queda casi de frente (3/4), no perfil puro | `generado/preview/personajes/miranda/pegar_lado.gif` | `generado/sprites/personajes/miranda/pegar_lado/pegar_lado_tira.png` |
| miranda | personajes/caer_levantarse | REVISAR | cuadro 4 es solo cabeza/cabello con un moño azul inexistente y sin cuerpo; fragmentos sueltos en cuadros 3-4 | `generado/preview/personajes/miranda/caer_levantarse.gif` | `generado/sprites/personajes/miranda/caer_levantarse/caer_levantarse_tira.png` |
| miranda | personajes/especial | REVISAR | perfil a la derecha con minigun correcta, pero el cuadro 5 tiene la boca del cañón cortada en el borde | `generado/preview/personajes/miranda/especial.gif` | `generado/sprites/personajes/miranda/especial/especial_tira.png` |
| cesar | efectos/efecto_habilidad | REVISAR | código verde muy denso, con pseudotexto ilegible y bloques cortados en recto arriba; cuadro 4 casi vacío | `generado/preview/efectos/cesar/efecto_habilidad.gif` | `generado/sprites/efectos/cesar/efecto_habilidad/efecto_habilidad_tira.png` |
| cesar | efectos/efecto_especial | REVISAR | estallido y anillos correctos, pero el anillo del cuadro 4 toca el borde derecho y está cortado | `generado/preview/efectos/cesar/efecto_especial.gif` | `generado/sprites/efectos/cesar/efecto_especial/efecto_especial_tira.png` |
| castillo | personajes/caminar_lado | REVISAR | Mejoró: la cabeza ya está de perfil a la derecha, pero el torso sigue en 3/4 (se ve la botonadura) y asoma el segundo lente; se puede usar, pero no es un perfil puro. | `generado/preview/personajes/castillo/caminar_lado.gif` | `generado/sprites/personajes/castillo/caminar_lado/caminar_lado_tira.png` |
| castillo | personajes/pegar_lado | REVISAR | vista tres cuartos (cuadros 1 y 4 casi de frente) más que perfil; el golpe sí va a la derecha | `generado/preview/personajes/castillo/pegar_lado.gif` | `generado/sprites/personajes/castillo/pegar_lado/pegar_lado_tira.png` |
| castillo | personajes/pegar_arriba | REVISAR | de espaldas correcto, pero el golpe se desvía hacia arriba-derecha en lugar de ir al frente | `generado/preview/personajes/castillo/pegar_arriba.gif` | `generado/sprites/personajes/castillo/pegar_arriba/pegar_arriba_tira.png` |
| castillo | personajes/especial | REVISAR | el haz es violeta, no azul, y en cuadros 3-4 tapa la cara y el brazo de forma translúcida rara | `generado/preview/personajes/castillo/especial.gif` | `generado/sprites/personajes/castillo/especial/especial_tira.png` |
| castillo | efectos/efecto_especial | REVISAR | 432 px magenta/violeta en bordes del haz; las formas del haz cambian mucho entre cuadros como loop | `generado/preview/efectos/castillo/efecto_especial.gif` | `generado/sprites/efectos/castillo/efecto_especial/efecto_especial_tira.png` |
| alessandro | personajes/caminar_lado | REVISAR | piernas caminan a la derecha, pero la cara y el torso están en vista 3/4 de frente, no de perfil; se ve como si caminara de lado mirando a cámara | `generado/preview/personajes/alessandro/caminar_lado.gif` | `generado/sprites/personajes/alessandro/caminar_lado/caminar_lado_tira.png` |
| alessandro | personajes/pegar_lado | REVISAR | golpe a la derecha bien hecho y mismo personaje, pero el cuerpo y la cara están en 3/4 de frente en lugar de perfil | `generado/preview/personajes/alessandro/pegar_lado.gif` | `generado/sprites/personajes/alessandro/pegar_lado/pegar_lado_tira.png` |
| alessandro | personajes/pegar_arriba | REVISAR | vista de espaldas correcta, pero el brazo se extiende hacia la derecha en lugar de hacia arriba/al frente; dirección ambigua | `generado/preview/personajes/alessandro/pegar_arriba.gif` | `generado/sprites/personajes/alessandro/pegar_arriba/pegar_arriba_tira.png` |
| alessandro | efectos/efecto_habilidad | REVISAR | 4 cuadros con caritas riendo, pero el estallido central parece más una explosión que líneas de risa | `generado/preview/efectos/alessandro/efecto_habilidad.gif` | `generado/sprites/efectos/alessandro/efecto_habilidad/efecto_habilidad_tira.png` |
| gabo | personajes/caminar_lado | REVISAR | piernas caminan a la derecha pero cara y torso quedan en vista 3/4 casi de frente, no de perfil | `generado/preview/personajes/gabo/caminar_lado.gif` | `generado/sprites/personajes/gabo/caminar_lado/caminar_lado_tira.png` |
| gabo | personajes/pegar_lado | REVISAR | golpe a la derecha legible, pero en vista 3/4 con la cara hacia la cámara en lugar de perfil | `generado/preview/personajes/gabo/pegar_lado.gif` | `generado/sprites/personajes/gabo/pegar_lado/pegar_lado_tira.png` |
| gabo | efectos/efecto_habilidad | REVISAR | SEPARACIÓN: la IA lo hizo en cuadrícula 2x2 (nubes de polvo con líneas de velocidad) y los cuadros quedaron mal cortados | `generado/preview/efectos/gabo/efecto_habilidad.gif` | `generado/sprites/efectos/gabo/efecto_habilidad/efecto_habilidad_tira.png` |
| carlos | personajes/pegar_lado | REVISAR | Mismo personaje y golpe hacia la derecha con arco, pero en vista 3/4 con la cara casi de frente en lugar de perfil. | `generado/preview/personajes/carlos/pegar_lado.gif` | `generado/sprites/personajes/carlos/pegar_lado/pegar_lado_tira.png` |
| carlos | personajes/especial | REVISAR | SEPARACIÓN: la imagen original está bien, pero el escudo del cuadro 5 quedó recortado en el borde (casi se toca con el cuadro 4); el cambio de color se debe al escudo, no al personaje. | `generado/preview/personajes/carlos/especial.gif` | `generado/sprites/personajes/carlos/especial/especial_tira.png` |
| carlos | efectos/efecto_especial | REVISAR | La burbuja original está bien, pero el recorte de magenta perforó el interior translúcido (hueco irregular en 3 de 4 cuadros) y dejó 2102 px con tinte magenta. | `generado/preview/efectos/carlos/efecto_especial.gif` | `generado/sprites/efectos/carlos/efecto_especial/efecto_especial_tira.png` |
| tonyfuerte | personajes/pegar_lado | REHACER | Sigue igual: cuadros 1 y 4 de frente en guardia (dos ojos) y cuadros 2-3 vistos de espaldas en 3/4; no es perfil a la derecha. | `generado/preview/personajes/tonyfuerte/pegar_lado.gif` | `generado/sprites/personajes/tonyfuerte/pegar_lado/pegar_lado_tira.png` |
| normal | zombies/caminar_lado | REVISAR | mismo personaje pero en vista 3/4 hacia la derecha, no perfil puro; el cuadro 4 baja los brazos y rompe el ciclo | `generado/preview/zombies/normal/caminar_lado.gif` | `generado/sprites/zombies/normal/caminar_lado/caminar_lado_tira.png` |
| normal | zombies/atacar_lado | REVISAR | mismo personaje y ataque legible con arco, pero en vista 3/4 hacia la derecha en lugar de perfil | `generado/preview/zombies/normal/atacar_lado.gif` | `generado/sprites/zombies/normal/atacar_lado/atacar_lado_tira.png` |
| normal | zombies/atacar_abajo | REHACER | Sigue igual: vista 3/4 y en los cuadros 2-3 los brazos se estiran hacia el lado derecho, no hacia el espectador. | `generado/preview/zombies/normal/atacar_abajo.gif` | `generado/sprites/zombies/normal/atacar_abajo/atacar_abajo_tira.png` |
| normal | zombies/golpe_morir | REHACER | Sigue igual: en el raw el cuerpo acostado (cuadro 4) toca el humo del cuadro 5; en la tira los pies quedan cortados y pasan al cuadro 5. | `generado/preview/zombies/normal/golpe_morir.gif` | `generado/sprites/zombies/normal/golpe_morir/golpe_morir_tira.png` |
| corredor | zombies/atacar_lado | REVISAR | mismo personaje y ataque hacia la derecha correcto, pero el cuerpo está en vista 3/4 en lugar de perfil puro, no coincide del todo con caminar_lado | `generado/preview/zombies/corredor/atacar_lado.gif` | `generado/sprites/zombies/corredor/atacar_lado/atacar_lado_tira.png` |
| griton | zombies/golpe_morir | REVISAR | SEPARACIÓN: en el raw el cuadro 3 se encima con el cuerpo acostado y el cuadro 3 quedó con piernas del 4; además cuadros 2-3 en 3/4 y el cuadro 4 acostado de lado, sin sangre | `generado/preview/zombies/griton/golpe_morir.gif` | `generado/sprites/zombies/griton/golpe_morir/golpe_morir_tira.png` |
| gordo | zombies/golpe_morir | REVISAR | SEPARACIÓN: la punta de la mano del cuadro 3 quedó cortada y aparece como fragmento suelto en el cuadro 4; secuencia y personaje correctos, sin gore | `generado/preview/zombies/gordo/golpe_morir.gif` | `generado/sprites/zombies/gordo/golpe_morir/golpe_morir_tira.png` |
| conserje | zombies/caminar_abajo | REVISAR | Mismo conserje y ciclo de 6 cuadros correcto, pero sin el trapeador y los brazos apuntan a la derecha (vista 3/4) en vez de hacia el frente. | `generado/preview/zombies/conserje/caminar_abajo.gif` | `generado/sprites/zombies/conserje/caminar_abajo/caminar_abajo_tira.png` |
| conserje | zombies/caminar_arriba | REVISAR | Vista de espaldas correcta y mismo personaje, pero el trapeador desaparece en el cuadro 4 y salta en el ciclo. | `generado/preview/zombies/conserje/caminar_arriba.gif` | `generado/sprites/zombies/conserje/caminar_arriba/caminar_arriba_tira.png` |
| conserje | zombies/caminar_lado | REHACER | Sigue igual: la cara y el cuerpo miran de frente o en 3/4 a la cámara, no de perfil a la derecha; además, en los cuadros 2-6 sostiene el palo sin la cabeza del trapeador. | `generado/preview/zombies/conserje/caminar_lado.gif` | `generado/sprites/zombies/conserje/caminar_lado/caminar_lado_tira.png` |
| conserje | zombies/atacar_lado | REVISAR | Mismo personaje y golpe con trapeador hacia la derecha en 4 cuadros, pero el cuerpo y la cara están en 3/4 de frente, no de perfil. | `generado/preview/zombies/conserje/atacar_lado.gif` | `generado/sprites/zombies/conserje/atacar_lado/atacar_lado_tira.png` |
| conserje | zombies/golpe_morir | REHACER | Sigue mal: en la imagen original de la IA, los cuadros 3 y 4 se superponen (la pierna que cae se cruza con el trapeador del cuerpo acostado), así que en la tira el cuadro 3 sale cortado y el 4 trae un pie ajeno; no hay espacio entre cuadros. | `generado/preview/zombies/conserje/golpe_morir.gif` | `generado/sprites/zombies/conserje/golpe_morir/golpe_morir_tira.png` |
| curado | zombies/pegar_lado | REVISAR | SEPARACIÓN: en el raw el arco blanco está frente al puño del cuadro 3, pero tras separar quedó suelto a la izquierda del cuadro 4; además la pose es 3/4 y no un perfil puro (mira a la derecha) | `generado/preview/zombies/curado/pegar_lado.gif` | `generado/sprites/zombies/curado/pegar_lado/pegar_lado_tira.png` |

## Lo que no se generó

- **Criollo:** todavía no tiene imagen base, así que no se generó nada de él.
- **Profes (Canepa, Joel, Justino): PENDIENTE.** Su papel en el juego todavía no se define, así que por decisión del equipo no se generaron los 21 trabajos que faltaban: `canepa__pegar_abajo`, `canepa__caer_levantarse`, `canepa__festejo`, `joel__quieto`, `joel__caminar_abajo`, `joel__caminar_arriba`, `joel__caminar_lado`, `joel__pegar_lado`, `joel__pegar_abajo`, `joel__pegar_arriba`, `joel__caer_levantarse`, `joel__festejo`, `justino__quieto`, `justino__caminar_abajo`, `justino__caminar_arriba`, `justino__caminar_lado`, `justino__pegar_lado`, `justino__pegar_abajo`, `justino__pegar_arriba`, `justino__caer_levantarse`, `justino__festejo`. De Canepa sí quedaron las 6 animaciones que alcanzaron a generarse (procesadas y revisadas); Joel y Justino no tienen nada todavía. Cuando se defina su papel, se generan con `python generar.py --ids ...` (los que ya existen no se vuelven a cobrar).

## Cambios a los prompts genéricos

- Ninguno: el piloto salió bien con las frases de formato originales.
- Frases de corrección añadidas al regenerar (solo en esos trabajos, sin tocar la descripción del personaje):
  - `alessandro__pegar_abajo`: “Front view facing the camera, punching straight toward the viewer with the fist coming at the camera, not to the side.”
  - `carlos__caminar_lado`: “True side profile view facing right: head, face and body turned fully to the right, only one eye visible.”
  - `carlos__pegar_abajo`: “Punch straight toward the camera, fist foreshortened in front of the body, not to the side.”
  - `castillo__caminar_lado`: “True side profile facing right: show only one eye and the side of the face and body, nose pointing right.”
  - `castillo__pegar_abajo`: “The punch goes straight toward the camera, fist extended at the viewer, not to the side.”
  - `conserje__caminar_lado`: “True side profile facing right, face and body turned fully to the right, holding his mop, with space at the right edge.”
  - `conserje__golpe_morir`: “All 6 frames side by side in one single row, the lying body in its own separate frame 4.”
  - `corredor__caminar_lado`: “Exactly 6 frames, side view facing right.”
  - `corredor__atacar_abajo`: “Front view facing the camera, clawing straight toward the viewer, not to the side.”
  - `gabo__pegar_abajo`: “Front view facing the camera, punching straight toward the viewer, not to the side.”
  - `gordo__caminar_lado`: “True side profile view facing right: only one eye and one lens visible, body turned 90 degrees, walking to the right.”
  - `gordo__atacar_lado`: “True side profile view facing right: head and body turned 90 degrees, only one eye visible, lunging to the right.”
  - `griton__atacar_abajo`: “All 4 frames in front view facing the viewer; lunge and claw straight toward the camera, not to the side.”
  - `miranda__caminar_lado`: “Strict side profile view facing right: we see only one eye and the side of her face, body turned fully to the right.”
  - `miranda__efecto_especial`: “Exactly 4 frames in one single row, one muzzle flash per frame, nothing touching the image edges.”
  - `normal__atacar_abajo`: “Keep the front view in all 4 frames; the zombie lunges and claws straight toward the viewer, not to the side.”
  - `normal__golpe_morir`: “Keep clear empty space between all 6 frames; the falling and lying bodies must not overlap.”
  - `tony__caminar_lado`: “Strict side profile view facing right: we see only one eye, one lens of the glasses and the side of the body.”
  - `tonyfuerte__caminar_lado`: “Strict side profile facing right in all 6 frames (only one eye visible), same size and full golden aura in every frame.”
  - `tonyfuerte__pegar_lado`: “All 4 frames in side profile facing right; frame 1 pulls the fist back to the waist, frame 4 is a side-view guard pose.”

## Notas del procesamiento

- Paleta: los colores cercanos a la paleta de la base (distancia RGB < 55) se ajustan a ella; los colores que no existen en la base (aura dorada, armas, ojos rojos de zombie, fuego, etc.) se cuantizan aparte a 16 colores. Ajustar todo a la paleta de la base volvía café el aura de Tony y los ojos rojos del zombie (se vio en el piloto).
- En animaciones con dos referencias (p. ej. tony/especial con tonyfuerte.png) la paleta es la unión de ambas bases.
- Envío a la API: solo se reintenta si la API no aceptó el trabajo (error de conexión, 5xx o 429 en el envío); un trabajo aceptado (con id) siempre cuenta como generación.
- Objetos: cada objeto se recorta a su contenido (sin lienzo común); 32 px por el lado mayor, contenedores 48 px y camión 160 px de alto. El GIF de objetos muestra cada objeto a 2 fps.
- Separación de cuadros, en este orden: proyección de columnas; si faltan cuadros, piezas conectadas (cada figura es una pieza: resuelve el cuadro 'acostado' que la IA dibuja debajo del cuadro de caída, y el último cuadro de humo de golpe_morir); luego corte en el valle de la proyección; luego agrupar por centro; y al final partes iguales (marcada REVISAR: cuadros). Con esto se arreglaron sin regenerar caer_levantarse de Tony, Alan y César y golpe_morir del corredor, que el revisor había marcado.
- Sombra del piso: la IA la pinta como magenta oscuro; en personajes, profes y zombies todo píxel con tono magenta se toma como fondo. En efectos no (pueden ser violetas de verdad).
- Las imágenes anteriores a una regeneración se conservan como generado/raw/.../<animacion>.v1.png.
