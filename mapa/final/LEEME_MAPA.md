# FDI-Z · Mapa compacto (versión 1)

## Archivos
| Archivo | Para qué sirve |
|---------|----------------|
| `tileset_fdiz.png` | 562 casillas de 32 px (pisos, muros, piedra, reja) |
| `mapa_fdiz_gdevelop.json` | Mapa de Tiled con el tileset incrustado, para el objeto **Tilemap** de GDevelop (es el mismo que `mapa_fdiz.tmj`) |
| `mapa_fdiz.tmj` | El mismo mapa, para abrirlo y editarlo en Tiled |
| `mapa_fdiz_datos.json` | En px: colisiones, zonas de niebla, puertas, marcadores de objetivos y props exteriores |
| `mapa_fdiz_props.json` | 758 muebles y objetos colocados: sprite, posición (ancla abajo al centro), capa y rectángulo de choque |
| `mapa_fdiz_completo.png` | El mapa entero en una imagen, a tamaño real (solo pisos y muros) |
| `mapa_fdiz_con_props.png` | El mapa entero con todos los muebles (y `_cuarto` a 1/4) |
| `vista_1a1_*.png` | Pantallas 1920×1080 a tamaño real del CIC, el edificio E, la nevería y el estacionamiento |
| `mapa_fdiz_guia.png` | Guía a 1/4 con nombres, puertas por tipo, inicio, objetivos, bidones y rejillas |
| `fuente/construir_mapa.py` y `fuente/amueblar.py` | Regeneran todo: el primero arma pisos, muros y marcadores; el segundo acomoda los muebles |

## Medidas
- **Casilla:** 32 px. El personaje mide 96 px (3 casillas).
- **Mapa:** 274 × 168 casillas = 8768 × 5376 px.
- **Cámara:** con 1920×1080 a zoom 1 se ven 60 × 34 casillas.
- **Velocidades del documento:** multiplicarlas por 3, porque estaban pensadas para sprites de 32 px. Por ejemplo, Tony 204 px/s, zombie normal 99 px/s y radio de detección 255 px.

## Capas del .json de Tiled
1. **`suelo` y `muros`:** son de casillas. Las casillas de muro, bosque, piedra y reja tienen clase `muro` y su forma de colisión.
2. **`colisiones`:** 218 rectángulos ya fusionados.
3. **`zonas_niebla`:** 40 cuartos.
4. **`puertas`:** 47. Cada una trae `tipo` (normal, electrónica, restringida o restringida_electrónica), `orientacion` y las `zonas` que abre.
5. **`marcadores`:**
   - inicio de jugadores (E-04)
   - camión, Canepa y rejas
   - servidor e interruptor del SITE
   - computadoras de la llamada
   - llaves de la conserjería
   - carnada en la nevería y horda de la explanada
   - bidones y bolsa de comida posibles
   - botín de Dirección y tarjeta
   - Joel (cubículos del CIC) y Justino (C-02)
   - rejillas del Jefe
6. **`props_exteriores`:** árboles, mesas redondas y postes de luz.

## Muebles y objetos
- Los sprites están en `generado\sprites\mapa\` (lote del mapa) y `generado\sprites\mapa_extra\` (versiones escaladas: pizarrón, barra, camión, etc.).
- **Capas de los props:**
  - `pared`: va pegado a la pared del fondo y no choca.
  - `piso` y `arbol`: se ordenan por Y para que el personaje pase delante o detrás.
  - `encima`: va arriba de otro mueble.
- **Choques:** solo chocan los props que traen `colision`, y es solo el pie del mueble, así se puede caminar "detrás" de los árboles.
- **Ventilador de techo:** no se colocó, porque taparía a los personajes. Se puede usar en una capa de techo semitransparente.

## En GDevelop
1. **Tilemap:** crear un objeto Tilemap en la capa Fondo:
   - archivo Tiled: `mapa_fdiz_gdevelop.json`
   - atlas: `tileset_fdiz.png`
2. **Colisiones de las balas y del movimiento:** un objeto **Tilemap collision mask** con el mismo .json y el filtro de clase `muro`.
3. **Pathfinding:** el comportamiento Pathfinding necesita objetos obstáculo. Hay que crear un sprite invisible `Muro` (comportamiento obstáculo) por cada rectángulo de `colisiones` de `mapa_fdiz_datos.json`. Lo mismo vale para las tapas de niebla (`zonas`) y las puertas.

   Cuando lleguen los props generados, Claude puede colocar todo eso directo en el proyecto de GDevelop.
