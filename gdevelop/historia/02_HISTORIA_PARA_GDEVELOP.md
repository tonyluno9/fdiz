# FDI-Z · Modo Historia — Guía de implementación para GDevelop (versión final)

Este documento es para la IA que arma el juego en GDevelop. Explica **qué pasa en la historia, en qué orden, dónde se disparan las cinemáticas (videos), qué diálogos suenan, a qué personaje controla el jugador, qué armas se obtienen y qué objetivos ve el jugador.** Los nombres de audio coinciden exactamente con `01_DIALOGOS_PARA_VOCES.md`.

## 1. Resumen de la historia

Es de **noche** en la facultad. Cuatro estudiantes —**Alan, Miranda, Tony y César**— esperan a su profesor, que no llega. Encuentran su bolsa en el escritorio y, al abrirla, una **pistola**. Suena la alarma: hay un **brote zombie**. Un zombie rompe el vidrio de la puerta; Tony toma la pistola y huyen.

Van al **CIC** (sala de cómputo) a pedir ayuda; rescatan al **profe Joel**, pero no hay línea y se va la luz. A oscuras llegan a la **sala del conserje**: un zombie gordo los ataca y, al fondo, pasa el **conserje zombie**. En un casillero encuentran una **escopeta** con una nota («Para cuando vuelvan»). Joel reactiva la luz y se queda cuidando el tablero. En la **nevería**, el **profe Justino** les dice que el autobús está en el estacionamiento y que la llave de la reja está en **dirección**, «y algo más». En la oficina del director encuentran la **llave**, otra **pistola** y, con la llave, abren un armario con un **AK-47**. En el estacionamiento, el **profe Canepa** repara el **autobús**; el ruido del motor atrae a la horda y al conserje. Lo defienden hasta que arranca, rompen la reja de la entrada y escapan.

Personalidades: Alan = bromista/impulsivo · Miranda = sensata · Tony = líder · César = listo y sarcástico · Joel = miedoso · Justino = tranquilo, humor seco · Canepa = apurado.

## 2. Archivos y carpetas

```
assets/historia/audio/   <- todos los .mp3 (nombres de 01_DIALOGOS_PARA_VOCES.md)
assets/historia/video/   <- cinemáticas (nombres exactos abajo)
```

| Video | Escena |
|---|---|
| `C01_T1.mp4` | Se acercan al escritorio |
| `C01_T2.mp4` | Manotazo de Miranda |
| `C02.mp4` | La pistola y la alarma |
| `C03.mp4` | Zombie en la puerta, Tony toma la pistola |
| `C04.mp4` | El profe Joel en el CIC |
| `C05.mp4` | Sin línea · apagón |
| `C06.mp4` | Sala del conserje: zombie gordo, pasa el conserje |
| `C065.mp4` | La escopeta · regresa la luz |
| `C07.mp4` | Justino en la nevería |
| `C08.mp4` | Oficina del director: llave, pistola, armario y AK-47 |
| `C09.mp4` | Autobús, Canepa, llega la horda |
| `C10.mp4` | Escape: el autobús rompe la reja |

- Las cinemáticas traen **su propia música y efectos**; **no** traen voces (las voces son los .mp3 del juego).
- Si un video aún no existe: pantalla negra 1 s + los diálogos de esa escena en globos. Al agregar el archivo con ese nombre, debe funcionar sin cambiar eventos.

## 3. Sistemas que hay que implementar

### 3.1 Reproductor de cinemáticas
- Al dispararse: pausar gameplay, IA de zombies y música; ocultar HUD; video a pantalla completa encima de todo.
- **Saltar:** mantener `Espacio`/`Enter`/botón A 1 s (indicador circular).
- Al terminar: volver al gameplay y continuar con la secuencia siguiente. Cada cinemática se ve **una sola vez** por partida (`Historia.CinematicasVistas`).

### 3.2 Diálogos
- Secuencia de líneas `{audio, personaje, texto}`: globo sobre quien habla (o retrato + nombre si está fuera de pantalla) + audio. Avanza al terminar el audio + 0.3 s; `Espacio` adelanta.
- **[D]** bloqueante (nadie se mueve) · **[G]** durante gameplay (todo sigue).
- Color de nombre: Alan gris oscuro, Miranda café claro, Tony blanco, César azul, Joel verde, Justino rosa, Canepa naranja, Altavoz rojo.

### 3.3 Objetivos
- Texto arriba a la izquierda + flecha hacia la zona. Zonas invisibles `Zona_<id>` que se activan cuando entra el personaje controlado.

### 3.4 Personaje controlado (cambia durante la historia)
El jugador controla **un** alumno a la vez; los otros tres son bots que lo siguen y pelean. Al cambiar: aviso en pantalla («Ahora controlas a TONY») + retrato en el HUD. Variable `Historia.Controlado`.

| Tramo | Desde | Hasta | Controlas a | Su arma |
|---|---|---|---|---|
| 1 | Inicio (PASO 1) | Fin de C02 | **ALAN** | sin arma (solo empujar) |
| 2 | Fin de C02 / C03 | Fin de C065 | **TONY** | pistola pequeña |
| 3 | Fin de C065 | Fin de C07 | **CÉSAR** | escopeta |
| 4 | Fin de C07 | Fin de C08 | **MIRANDA** | escopeta (se la pasa César en la nevería) |
| 5 | Fin de C08 | Final | **ALAN** | AK-47 |

En cooperativo (varios jugadores) este sistema se desactiva: cada quien conserva su personaje.

### 3.5 Armas (quién lleva qué)
| Arma | Se obtiene en | La lleva |
|---|---|---|
| Pistola pequeña (bolsa del profe) | C02/C03 | **Tony**, todo el juego |
| Escopeta (casillero del conserje) | C065 | **César** → en C07 se la pasa a **Miranda**, que la conserva hasta el final |
| Pistola del director (cajón) | C08 | **César**, hasta el final |
| AK-47 (armario del director) | C08 | **Alan**, hasta el final. Automática, cadencia alta, cargador de 30. Sprite de referencia: `cinematicas/_refs/arma_ak47.png` |

Los bots usan el arma que lleva su personaje.

## 4. Secuencia completa

> **[D]** diálogo bloqueante · **[G]** diálogo en gameplay · **[V]** video · **[O]** objetivo · **[E]** evento · **[C]** cambio de personaje controlado

### PASO 1 · INTRO — salón
- [E] Los 4 en el salón de noche. Fade in. **[C] Controlas a ALAN.**
- [D] `INT_01_cesar` → `INT_02_alan` → `INT_03_cesar` → `INT_04_miranda` → `INT_05_tony` → `INT_06_alan`
- [O] «Revisa el escritorio del profe» → `Zona_Escritorio`

### PASO 2 · C1 — La bolsa
- Disparador: `Zona_Escritorio`.
- [V] `C01_T1.mp4` → [D] `C1_01_alan` → `C1_02_miranda` → [V] `C01_T2.mp4` → [D] `C1_03_alan` → `C1_04_cesar` → `C1_05_tony`

### PASO 3 · C2 — La pistola y la alarma
- [V] `C02.mp4`
- [D] `C2_01_alan` → `C2_02_miranda` → `C2_03_altavoz` (con alarma de fondo) → `C2_04_cesar`
- [E] Luz roja intermitente + alarma en loop bajo.

### PASO 4 · C3 — Golpes en la puerta
- [V] `C03.mp4` (Tony toma la pistola y apunta a la puerta)
- [D] `C3_01_miranda` → `C3_02_tony` → `C3_03_cesar`
- [E] **Tony obtiene la pistola pequeña.** **[C] Controlas a TONY.**
- [E] El zombie rompe la puerta y entra: **primer combate** (tutorial «Clic/gatillo para disparar»). Se abre la puerta trasera.
- [O] «Llega al CIC» → `Zona_CIC`
- [G] En `Zona_Pasillo1`: `J1_01_alan` → `J1_02_miranda`

### PASO 5 · C4 — El profe Joel
- Disparador: `Zona_CIC`.
- [V] `C04.mp4`
- [D] `C4_01_joel` → `C4_02_tony` → `C4_03_joel` → `C4_04_miranda` → `C4_05_alan` → `C4_06_joel`
- [E] Joel se une como NPC (sigue al grupo, no ataca; si lo derriban se levanta a los 5 s).

### PASO 6 · C5 — Sin línea / apagón
- Disparador: interactuar con el teléfono del escritorio del CIC (`Zona_Telefono`).
- [V] `C05.mp4` (Tony con el teléfono; apagón)
- [D] `C5_01_tony` → `C5_02_joel` (se corta)
- [E] **Apagón** (mecánica existente). Los alumnos usan linterna de celular (cono de luz).
- [D] `C5_03_miranda` → [E] aparecen zombies en el pasillo.
- [O] «Encuentra la sala del conserje» → `Zona_Conserje`
- [G] Al salir del CIC: `J2_01_tony`

### PASO 7 · C6 — Sala del conserje
- Disparador: `Zona_Conserje`.
- [V] `C06.mp4` (sale un zombie gordo, Tony le dispara; al fondo pasa el conserje zombie)
- [D] `C6_01_tony` → `C6_02_alan`
- [E] Combate corto contra un **zombie gordo**.

### PASO 8 · C6.5 — La escopeta
- Disparador: interactuar con el casillero (`Zona_Casillero`) tras vencer al zombie.
- [V] `C065.mp4` (César abre el casillero; aparece la escopeta; Joel sube el tablero y regresa la luz)
- [D] `C65_01_cesar` → `C65_02_joel` → `C65_03_tony` → `C65_04_joel` → `C65_05_tony`
- [E] **Escopeta para César.** **[C] Controlas a CÉSAR.** **Termina el apagón** (luz parcial).
- [E] **Joel deja el grupo** y se queda en la sala del conserje.
- [O] «Busca a otro profesor: la nevería» → `Zona_Neveria`

### PASO 9 · C7 — Justino en la nevería
- Disparador: `Zona_Neveria`.
- [V] `C07.mp4` (Miranda entra con la escopeta; Justino señala la salida con la cuchara)
- [D] `C7_01_justino` → `C7_02_miranda` → `C7_03_justino` → `C7_04_tony` → `C7_05_justino` → `C7_06_alan` → `C7_07_justino`
- [E] **César le pasa la escopeta a Miranda.** **[C] Controlas a MIRANDA.**
- [E] Justino se queda en la nevería (NPC). Opcional: curación completa.
- [O] «Consigue la llave en la oficina del director» → `Zona_Direccion`

### PASO 10 · C8 — Oficina del director
- Disparador: interactuar con el escritorio del director (`Zona_CajonDirector`).
- [V] `C08.mp4` (Tony abre el cajón: llave y pistola; con la llave abre el armario; destello dorado; Alan saca el AK-47)
- [D] `C8_01_tony` → `C8_02_cesar` → `C8_03_alan` → `C8_04_miranda`
- [E] Se obtienen la **llave de la reja**, la **pistola del director → César** y el **AK-47 → Alan**. **[C] Controlas a ALAN.**
- [E] Sube la dificultad: más zombies; el **conserje zombie** empieza a perseguir.
- [O] «Llega al autobús» → `Zona_Autobus`

### PASO 11 · C9 — El autobús y Canepa
- Disparador: `Zona_Autobus`.
- [V] `C09.mp4` (Canepa en el motor; el motor truena y el ruido atrae a la horda y al conserje)
- [D] `C9_01_canepa` → `C9_02_tony` → `C9_03_canepa` → `C9_04_alan` → `C9_05_miranda`
- [E] **Defensa final**: sobrevivir 90 s (usar el evento «¡Aguanten!») mientras Canepa repara. Oleadas crecientes + conserje zombie (jefe).
- [O] «Protege a Canepa: 1:30» (cuenta regresiva)

### PASO 12 · C10 — Escape
- Disparador: termina la cuenta regresiva con el grupo vivo.
- [D] `C10_01_canepa` → `C10_02_alan`
- [V] `C10.mp4` (arranca, suben, el autobús rompe la reja de la entrada). Si no existe, usar `15_victoria.mp4`.
- [D] `C10_03_tony` sobre la pantalla de victoria → menú.

### Derrota
- Si cae todo el equipo: `16_derrota.mp4` y reiniciar desde el inicio del PASO actual (checkpoint). Las cinemáticas vistas no se repiten. Se restauran el personaje controlado y las armas de ese paso.

## 5. Checklist
- [ ] Variables: `Historia.Paso`, `Historia.Controlado`, `Historia.CinematicasVistas`, `Historia.Armas`.
- [ ] Zonas: Escritorio, Pasillo1, CIC, Telefono, Conserje, Casillero, Neveria, Direccion, CajonDirector, Autobus.
- [ ] Reproductor de video con «mantener para saltar».
- [ ] Diálogos con audio + globo + avance automático.
- [ ] Cambio de personaje controlado con aviso y retrato.
- [ ] Armas: pistola pequeña, escopeta, pistola del director, **AK-47 (nueva)**.
- [ ] NPCs: Joel (seguidor, luego quieto), Justino (quieto), Canepa (quieto, objetivo a defender).
- [ ] Linterna de celular durante el apagón (PASO 6 a 8).
- [ ] Placeholders para videos faltantes.
