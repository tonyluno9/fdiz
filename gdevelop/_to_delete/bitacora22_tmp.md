

## Fase 22 · Modo Jefe de zombies funcional (2026-11-13)

Respaldo: `respaldos/antes_de_fase22_20261113.json`. Script idempotente: `scripts/fase22_jefe.py` (lee `scripts/jefe_modo.js` y `scripts/bots_habilidades.js` y los incrusta en la escena Juego). Iconos: `scripts/fase22_iconos_jefe.py` → `assets/interfaz/jefe_icono_c1..c8.png`.

**Qué cambió**
- El grupo "Modo Jefe de zombies" se reescribió: toda la lógica e interfaz del Jefe está en un evento JavaScript (`jefe_modo.js`). Se eliminaron las condiciones/acciones antiguas (texto plano en `TxtJefe`, minimapa-solo-clic, etc.).
- El Jefe juega solo con teclado y ratón: WASD/flechas mueven la cámara libre (Shift más rápido, Espacio = ir al grupo), clic en el minimapa mueve la cámara, teclas 1-8 o clic eligen carta, clic en el mapa invoca, clic derecho cancela la carta, H muestra/oculta la ayuda.
- Interfaz nueva: panel "MISIÓN DEL JEFE", ayuda inicial de 3 pasos, 8 cartas con icono, coste, recarga (velo con barra) y bloqueo por oro/nivel, cuadro explicativo de la carta elegida, minimapa con puntos (sobrevivientes por color, zombis, objetivo, ventana de cámara, zona visible), barra del próximo oro, mensajes de error junto al cursor y cursor verde/rojo según si se puede invocar.
- Regla de invocación: no se puede invocar dentro del círculo rojo (lo que ven los sobrevivientes) ni sobre paredes/muebles (rejilla de navegación).
- Modo Jefe ahora usa los 4 sobrevivientes como bots (Control -1; ya no se borra al P4); sin cinemática ni oscuridad inicial, sin niebla de zonas, sin aparición automática de zombis (solo los que invoca el Jefe).
- Cámara compartida desactivada con `Jefe=1`; `ZonaRoja` antigua oculta; el HUD de dinero muestra el oro del Jefe.
- Fin de partida: si los 4 sobrevivientes caen → "¡GANÓ EL JEFE!"; si cumplen el objetivo → "¡ESCAPARON! EL JEFE PERDIÓ" (textos en Resultados).
- Bots (todos los modos): `bots_habilidades.js` se ejecuta antes del grupo de habilidades y decide Q/E según el personaje (zombis cerca, gordos, vida baja, aliados heridos; Castillo cura, Carlos/Alessandro/Gabo se defienden, Miranda/César/Alan atacan en área).
- Bug corregido durante las pruebas: `setCoordinatesAbsolute` no existe en esta versión del Drawer (se usa la propiedad del objeto).
