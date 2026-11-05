# Reporte del lote del mapa (props del entorno)

**Generaciones usadas: 14 de 20.** Se generaron las 14 hojas al primer intento y no se usó ningún reintento.

- El lote 2 no estaba corriendo al empezar.
- El script no avisó en ninguna hoja que encontrara un número distinto de piezas.
- Atlas: `generado\sprites\mapa\mapa_atlas.json` (89 piezas).
- Hojas de revisión: `generado\revision\mapa\<hoja>.png`.

## Arreglos hechos en el procesamiento (sin regenerar)

Los cambios están en `pipeline\scripts\procesar_mapa.py`. Respaldé el original en `procesar_mapa.py.bak`.

1. **Orden de `hitos`.** El modelo puso el corazón arriba del arco chico, así que al cortar de izquierda a derecha salían cambiados `corazon_tapitas` y `arco_salida`. Lo arreglé con `ORDEN_MANUAL = {"mapa__hitos": [0, 2, 1, 3]}`.
2. **Tinte magenta (despill).** Casi todas las piezas tenían un halo morado en el contorno. Además se veía el magenta del fondo a través de la malla de `silla_profesor`, del vidrio de `cancel_vidrio` y de la malla del corazón. Ahora a los pixeles con tono magenta se les quita ese tinte: el contorno queda oscuro y el vidrio gris. Los colores rosas reales se conservan, por ejemplo los helados del congelador y las flores.

## Calificación por hoja

| Hoja | Calificación | Notas |
|---|---|---|
| salon | REVISAR | La malla de `generado\sprites\mapa\salon\silla_profesor.png` ya está corregida. Los pupitres y la silla se ven casi de frente o de espaldas, con poca vista desde arriba. |
| laboratorio | OK | |
| cic | OK | Está en vista 3/4 isométrica, pero queda consistente. |
| site | OK | Lo que distingue `tablero_apagado` de `tablero_prendido` (LED rojo o verde y la posición de la palanca) casi no se nota a 72 px: `generado\sprites\mapa\site\tablero_*.png`. |
| neveria | REVISAR | `generado\sprites\mapa\neveria\barra_verde.png` está dibujada en diagonal. Escalada a 176 de ancho queda de unos 145 px de alto, más alta que el personaje. Habría que bajarle el tamaño o reubicarla. |
| oficinas | REVISAR | El vidrio de `generado\sprites\mapa\oficinas\cancel_vidrio.png` ya quedó gris, sin magenta. Conviene confirmar que se ve bien en el juego. |
| banos | OK | |
| exterior | OK | |
| vegetacion | OK | |
| hitos | REVISAR | El orden ya está corregido. Las piezas están en isométrico (diagonal), no en 3/4 frontal. Revisa `generado\sprites\mapa\hitos\corazon_tapitas.png`: su malla era magenta y ahora queda rojo oscuro o gris. |
| estacionamiento | REVISAR | `generado\sprites\mapa\estacionamiento\reja_abierta.png` es un panel chico en ángulo y no se lee claramente como reja abierta. Los coches vistos desde arriba están bien. |
| cancha | OK | |
| senaletica | OK | `extintor_pared` incluye su letrero rojo encima, como parte de la misma pieza. |
| texturas | OK (solo corte) | Están cortadas en alta en `generado\limpio_hd\mapa\texturas\` (4 de 495×495). Falta hacerlas repetibles (las termina Claude). |

Ninguna hoja salió REHACER, así que no se usaron reintentos.
