# FDI-Z en GDevelop: cómo abrirlo en otra computadora

El juego editable está en `gdevelop/FDI-Z/FDI-Z.json`. Todo lo que necesita viene en este repositorio.
Usa rutas relativas, así que funciona en cualquier carpeta, siempre que se baje el repositorio **completo**.

## Requisitos
- **GDevelop 5.6.287 o más nuevo** (https://gdevelop.io/download).
- La extensión de controles (*Gamepads*) ya viene dentro del proyecto; no hay que instalar nada más.
- **Solo para volver a generar eventos con los scripts:** Python 3 y Pillow (`pip install pillow`).

## Abrir el juego
1. Baja el repositorio con Git, con GitHub Desktop o con "Code → Download ZIP" en GitHub.
   ```
   git clone https://github.com/tonyluno9/fdiz.git
   ```
2. En GDevelop: **Abrir proyecto** → `fdiz/gdevelop/FDI-Z/FDI-Z.json`.
3. **Vista previa** arranca la escena que tengas abierta. Para jugar el flujo completo, abre la escena **Titulo**.

> No muevas ni renombres las carpetas `fdiz/generado/sprites` ni `fdiz/gdevelop`. El proyecto lee los sprites de los personajes y zombies desde `../../generado/sprites/`.
> Si quieres sacar **solo** la carpeta `FDI-Z` del repositorio, primero corre (con GDevelop cerrado):
> `python gdevelop/scripts/empaquetar_recursos.py gdevelop/FDI-Z`
> Copia los sprites dentro del proyecto, y entonces la carpeta ya funciona sola.

## Teclas
- **Moverse:** WASD.
- **Pegar:** clic izquierdo.
- **Interactuar (mantener):** F (A en el mando). Sirve para abrir puertas, salvar a un caído, curar a un mordido, usar objetivos y revisar lockers.
  - Si hay varias cosas cerca, se hace solo una, la más cercana (salvar a alguien tiene preferencia), y arriba del personaje sale qué hará: «Mantén F para abrir», «Mantén F para salvar a P2»...
  - Si sueltas o te alejas antes de terminar, se pierde el avance de puertas, lockers y salvar o curar. Los objetivos largos, como la llamada, lo conservan como antes.
  - Al terminar una acción hay que soltar F antes de empezar otra.
  - Las puertas restringidas no se abren con F: hay que derribarlas a golpes o usar la llave maestra de Carlos.
  - Junto a un profe (Joel, Justino o Canepa), F o A abre el diálogo para reclutarlo.
- **Habilidad:** Q.
- **Especial:** E.
- **Lanzar:** R o clic derecho (B en el mando). R ya no abre puertas.
- **Correr:** Shift (LB o L3 en el mando), mientras haya estamina.
- **Volumen:** en la pausa (Esc, P o Start) → AJUSTES. Ahí se ajustan MÚSICA y EFECTOS por separado (de 0 a 100 %, en pasos de 10) con ← →, la cruceta o el ratón. Se conserva al cambiar de pantalla y la próxima vez que se abra el juego.
- **Saltar la cinemática:** Esc.
- **Modo presentación:** F1. Luego, con los números: 1 completar objetivo, 2 saltar al final, 3 vida infinita, 4 y 5 infestación, 6 reiniciar, 7 morder a P1, 8 dar $200, 9 engrapadora para P1.
- **Texto de depuración:** F3. Con F3 visible: B convierte a P1 en bot y T lo lleva a la siguiente máquina expendedora.

## Cómo está organizado
| Carpeta | Qué es |
|---|---|
| `gdevelop/FDI-Z/` | El proyecto de GDevelop (`FDI-Z.json`) y sus recursos (`assets/`) |
| `gdevelop/scripts/` | Scripts que generan el mapa y los eventos (ver abajo) |
| `gdevelop/BITACORA.md` | Qué se hizo en cada fase, los problemas y **lo que falta** |
| `gdevelop/capturas/` | Capturas de cada fase |
| `generado/sprites/` | Sprites finales (no editar los PNG originales) |
| `mapa/final/` | Mapa provisional (`mapa_fdiz_*.json`) |

## Los eventos se generan con scripts (no editarlos a mano)
Los eventos de la escena Juego y las escenas Titulo, Menu y Resultados salen de estos scripts. Si los cambias a mano en GDevelop, se pierden la próxima vez que se corran.
Para cambiar algo, edita el script y vuelve a correrlo **con GDevelop cerrado** (desde la carpeta `fdiz`):
```
python gdevelop/scripts/importar_mapa.py . gdevelop/FDI-Z                     # solo si cambió el mapa
python gdevelop/scripts/fase5_jugadores.py gdevelop/FDI-Z/FDI-Z.json generado/sprites/atlas.json mapa/final/mapa_fdiz_datos.json gdevelop/scripts/Gamepads.json
python gdevelop/scripts/fases_6_a_11.py gdevelop/FDI-Z/FDI-Z.json mapa/final/mapa_fdiz_datos.json
python gdevelop/scripts/fase12_mejoras.py gdevelop/FDI-Z/FDI-Z.json mapa/final/mapa_fdiz_datos.json mapa/final/mapa_fdiz_props.json
```
`fase5` regenera los eventos de Juego, así que **siempre** se corren los tres, en ese orden.

Los cambios posteriores (fases 13 a 62) son parches que se aplican sobre el JSON, en orden (ver `gdevelop/BITACORA.md`). Los últimos, en este orden:
```
python gdevelop/scripts/fase40_hojas_zombi.py        # (solo si cambian las hojas) hojas de Joel y Canepa zombi -> GIF
python gdevelop/scripts/fase40_sprites_profes.py     # convierte los GIF de los profes y de los profes zombi a PNG
python gdevelop/scripts/fase40_profesores.py         # profesores reclutables (idempotente)
node gdevelop/scripts/prueba_profes.js               # pruebas de la lógica de los profes (sin GDevelop)
python gdevelop/scripts/fase41_pasillo_y_monedas.py  # pasillo de la nevería de 3 casillas; monedas solo en modo Jefe
python gdevelop/scripts/fase42_correr.py             # Shift / LB / L3 = correr con estamina (lógica en correr.js)
node gdevelop/scripts/prueba_correr.js               # pruebas de la estamina (sin GDevelop)
python gdevelop/scripts/fase43_criticos.py           # (cesar) bloque Críticos: conserje y puertas, desatasco, etc.
python gdevelop/scripts/fase44_valla_sur.py          # (cesar) vallas de la calle sur
python gdevelop/scripts/fase45_quitar_arcos.py       # (cesar) quita los arcos de entrada/salida
python gdevelop/scripts/fase46_medios.py             # (cesar) bloque Medios (lógica en medios.js)
node gdevelop/scripts/prueba_medios.js               # (cesar) pruebas de medios.js
python gdevelop/scripts/fase47_tope_100.py           # (cesar) porcentajes topados a 100
python gdevelop/scripts/fase48_menores.py            # (cesar) bloque Menores
python gdevelop/scripts/fase49_arte.py               # (cesar) arte e interfaz (imágenes de controles en la pausa)
python gdevelop/scripts/fase50_minimapa.py           # (cesar) minimapa
python gdevelop/scripts/fase51_aliados_hab.py        # (cesar) habilidades de aliados con clic
python gdevelop/scripts/fase52_lanzables.py          # (cesar) lanzables con distracción y daño en área
python gdevelop/scripts/fase53_flechas.py            # (cesar) flechas de aliados fuera de pantalla
python gdevelop/scripts/fase54_iconos_lanzables.py   # (cesar) ícono del lanzable en el panel
python gdevelop/scripts/fase55_ilus_historia.py      # (una vez) ilustración provisional de la tarjeta HISTORIA
python gdevelop/scripts/fase55_historia.py           # modo Historia: 6 misiones fijas en orden
python gdevelop/scripts/prueba_historia.py           # simula los eventos de objetivos (sin GDevelop)
python gdevelop/scripts/fase56_interaccion.py        # F / A: una acción a la vez, la más cercana (lógica en usar.js; re-incrusta profes.js y medios.js)
node gdevelop/scripts/prueba_usar.js                 # pruebas de la interacción (sin GDevelop)
python gdevelop/scripts/fase57_volumen.py            # volumen de música y efectos; música en «Elige el modo» (lógica en audio.js)
node gdevelop/scripts/prueba_audio.js                # pruebas del volumen (sin GDevelop)
python -I gdevelop/scripts/fase58_sonidos.py         # efectos de sonidos_nuevos/ (WAV); ver efectos/CATALOGO_SONIDOS.md
python gdevelop/scripts/fase59_arte_armas.py         # (una vez) arte y sonidos del revólver y la escopeta
python gdevelop/scripts/fase59_armas_fuego.py        # pistola pequeña, sheriff y escopeta: balas, disparo y lugar en el mapa (POS)
python gdevelop/scripts/prueba_armas_fuego.py        # pruebas de las armas de fuego (sin GDevelop)
python -I gdevelop/scripts/fase60_sonidos2d.py     # efectos de sonidos/ (22 OGG; lógica en sfx.js); copia desde ..\sonidos 2d si hace falta
node gdevelop/scripts/prueba_sfx.js                 # pruebas de los efectos de sonido (sin GDevelop)
python gdevelop/scripts/fase61_canepa.py           # Historia: charla con Canepa en el camión (burbujas; lógica en canepa.js)
node gdevelop/scripts/prueba_canepa.js              # pruebas de la charla con Canepa (sin GDevelop)
python gdevelop/scripts/fase62_arte_pistola.py     # (si cambian los sprites) mira y animaciones placeholder de pistola
python gdevelop/scripts/fase62_armas_uso.py        # pistola pequeña del jugador 1, mira, balas en el HUD (lógica en armas.js)
node gdevelop/scripts/prueba_armas.js               # pruebas de la mira, el HUD de balas y las animaciones (sin GDevelop)
```
Arte de los profes zombis: un GIF por animación en `animaciones_gif/profes_zombi/<profe>/` (caminar_lado mirando a la derecha, caminar_arriba, caminar_abajo, atacar_lado, atacar_abajo, golpe_morir; atacar_arriba es opcional). Para cambiarlo, reemplaza el GIF y vuelve a correr los dos últimos scripts con GDevelop cerrado.
En Windows basta con doble clic en `gdevelop\scripts\reconstruir.bat`: hace un respaldo con fecha y corre los tres. Antes de correrlos, haz una copia de `FDI-Z.json`.

## Subir tus cambios
```
git add -A
git commit -m "Describe lo que cambiaste"
git push
```
Antes de seguir trabajando en otra compu, haz `git pull`. Para evitar conflictos en `FDI-Z.json`, que no trabajen dos personas en él al mismo tiempo.
