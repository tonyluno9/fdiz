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
- **Usar, revivir, curar o revisar (mantener):** F.
- **Habilidad:** E.
- **Especial:** C.
- **Lanzar:** Q o clic derecho.
- **Caminar despacio:** Shift.
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
En Windows basta con doble clic en `gdevelop\scripts\reconstruir.bat`: hace un respaldo con fecha y corre los tres. Antes de correrlos, haz una copia de `FDI-Z.json`.

## Subir tus cambios
```
git add -A
git commit -m "Describe lo que cambiaste"
git push
```
Antes de seguir trabajando en otra compu, haz `git pull`. Para evitar conflictos en `FDI-Z.json`, que no trabajen dos personas en él al mismo tiempo.
