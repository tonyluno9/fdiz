# FDI-Z · Modo Historia — Guía de implementación para GDevelop

Este documento es para la IA que arma el juego en GDevelop. Explica **qué pasa en la historia, en qué orden, dónde se disparan las cinemáticas (videos), qué diálogos suenan y qué objetivos ve el jugador.** Los nombres de archivo de audio coinciden exactamente con `01_DIALOGOS_PARA_VOCES.md`.

## 1. Resumen de la historia

Es de **noche** en la facultad. Cuatro estudiantes —**Alan, Miranda, Tony y César**— esperan a su profesor, que no llega. Encuentran su bolsa en el escritorio y, al abrirla, una pistola. En ese momento suena la alarma: hay un **brote zombie** en el edificio. Un zombie golpea la puerta y tienen que huir.

Van al **CIC** a pedir ayuda por teléfono; rescatan al **profe Joel**, pero no hay línea y se va la luz. En la **sala del conserje** reactivan la luz y encuentran una **escopeta** con una nota que sugiere que alguien ya sabía lo que iba a pasar. Joel se queda cuidando el tablero. En la **nevería**, el **profe Justino** les dice que el autobús escolar está atrás y que la llave de la reja está en **dirección**, donde encuentran también otra **pistola**. En el estacionamiento, el **profe Canepa** intenta arrancar el **autobús**: el grupo lo defiende de la horda (y del **conserje zombie**) hasta que arranca y escapan al amanecer.

Personalidades (para globos y retratos): Alan = bromista/impulsivo · Miranda = sensata, voz de la razón · Tony = líder · César = listo y sarcástico · Joel = miedoso · Justino = tranquilo, humor seco · Canepa = apurado.

## 2. Archivos y carpetas

```
assets/historia/audio/        <- todos los .mp3 de diálogos (nombres de 01_DIALOGOS_PARA_VOCES.md)
assets/historia/video/        <- cinemáticas: C01_T1.mp4, C01_T2.mp4, C02.mp4, C03.mp4 ... C10.mp4
```
- Las cinemáticas traen su **propia música y efectos**; **no** traen voces.
- Las cinemáticas que aún no existan (por ahora solo están C01_T1 y C01_T2) se reemplazan temporalmente por: pantalla negra 1 s + los diálogos de esa escena en globos. Al llegar el video, solo se agrega.

## 3. Sistemas que hay que implementar

### 3.1 Reproductor de cinemáticas
- Al dispararse: pausar gameplay e IA de zombies, ocultar HUD, reproducir el video a pantalla completa (capa encima de todo).
- **Saltar:** mantener `Espacio`/`Enter`/botón A 1 s (indicador circular en la esquina) → termina el video.
- Al terminar: volver al gameplay en la posición indicada y continuar con la secuencia de diálogo que sigue.
- Cada cinemática se ve **una sola vez** por partida (variable global `Historia.CinematicasVistas`).

### 3.2 Sistema de diálogos
- Secuencia = lista de líneas `{audio, personaje, texto}`. Por cada línea: mostrar globo sobre el personaje (o retrato + nombre abajo si está fuera de pantalla) y reproducir el audio. Pasa a la siguiente cuando **termina el audio + 0.3 s**. El jugador puede adelantar con `Espacio`.
- Durante diálogos de escena (**«diálogo bloqueante»**) el jugador no se mueve; en los de **«gameplay»** sí puede moverse y los zombies siguen.
- Color del nombre: Alan gris oscuro, Miranda café claro, Tony blanco, César azul, Joel verde, Justino rosa, Canepa naranja, Altavoz rojo.
- Usar el plan de diálogos de `prompts/pendientes.md` (datos en JSON, pool de textos) si ya existe.

### 3.3 Objetivos
- Texto de objetivo arriba a la izquierda + flecha/indicador hacia el disparador.
- Disparadores = zonas invisibles (`Zona_<id>`) en el mapa; se activan cuando entra **cualquier** jugador.

### 3.4 Elenco
- En Modo Historia el equipo es **fijo**: Alan, Miranda, Tony y César (bots o jugadores). Joel es NPC que sigue al grupo de C4 a C6.5.

## 4. Secuencia completa (en orden)

> Formato: **[D]** diálogo bloqueante · **[G]** diálogo durante gameplay · **[V]** video · **[O]** objetivo · **[E]** evento de juego

### PASO 1 · INTRO — salón (inicio de la partida)
- [E] Aparecen los 4 sentados en el salón. Pantalla negra → fade in.
- [D] `INT_01_cesar` → `INT_02_alan` → `INT_03_cesar` → `INT_04_miranda` → `INT_05_tony` → `INT_06_alan`
- [O] «Revisa el escritorio del profe» → `Zona_Escritorio`.

### PASO 2 · C1 — La bolsa
- Disparador: entrar a `Zona_Escritorio`.
- [V] `C01_T1.mp4` (se acercan al escritorio).
- [D] `C1_01_alan` → `C1_02_miranda`
- [V] `C01_T2.mp4` (Alan va a tocar la bolsa y Miranda le da un manotazo).
- [D] `C1_03_alan` → `C1_04_cesar` → `C1_05_tony`
- Sigue directo al paso 3.

### PASO 3 · C2 — La pistola y la alarma
- [V] `C02.mp4` (abren la bolsa, pistola, luz roja de alarma).
- [D] `C2_01_alan` → `C2_02_miranda` → `C2_03_altavoz` (sonar con la alarma de fondo) → `C2_04_cesar`
- [E] Se obtiene la **pistola pequeña** (arma inicial). Activar luz roja intermitente en el salón + sonido de alarma en loop bajo.

### PASO 4 · C3 — Golpes en la puerta
- [V] `C03.mp4` (zombie golpea la puerta, se agrieta el vidrio).
- [D] `C3_01_miranda` → `C3_02_tony` → `C3_03_cesar`
- [E] El zombie rompe la puerta principal y entra: **primer combate** (tutorial de disparo: mostrar «Clic/gatillo para disparar»). Se abre la puerta trasera del salón.
- [O] «Llega al CIC» → `Zona_CIC`.
- [G] A mitad del pasillo (`Zona_Pasillo1`): `J1_01_alan` → `J1_02_miranda`

### PASO 5 · C4 — El profe Joel
- Disparador: `Zona_CIC`.
- [V] `C04.mp4`
- [D] `C4_01_joel` → `C4_02_tony` → `C4_03_joel` → `C4_04_miranda` → `C4_05_alan` → `C4_06_joel`
- [E] Joel se une como NPC (sigue al grupo, no ataca, puede ser derribado: si cae, se levanta tras 5 s).

### PASO 6 · C5 — Sin línea / apagón
- Disparador: interactuar con el teléfono del CIC (`Zona_Telefono`).
- [V] `C05.mp4`
- [D] `C5_01_cesar` → `C5_02_joel` (se corta) 
- [E] **Apagón**: activar la mecánica de apagón que ya existe.
- [D] `C5_03_miranda`
- [E] Aparecen zombies en el pasillo.
- [O] «Encuentra la sala del conserje» → `Zona_Conserje`.
- [G] Al salir del CIC: `J2_01_tony`

### PASO 7 · C6 — Sala del conserje
- Disparador: `Zona_Conserje`.
- [V] `C06.mp4` (abren la puerta, salta un zombie de intendencia; al fondo pasa el conserje zombie jefe).
- [D] `C6_01_tony` → `C6_02_alan`
- [E] Combate corto contra el zombie de intendencia (zombie normal).

### PASO 8 · C6.5 — La escopeta
- Disparador: interactuar con el casillero (`Zona_Casillero`) tras vencer al zombie.
- [V] `C065.mp4`
- [D] `C65_01_cesar` → `C65_02_joel` → `C65_03_tony`
- [E] Se obtiene la **escopeta**. Se activa el tablero: **termina el apagón** (luz parcial).
- [D] `C65_04_joel` → `C65_05_tony`
- [E] **Joel deja el grupo**: se queda en la sala del conserje (NPC quieto).
- [O] «Busca a otro profesor: la nevería» → `Zona_Neveria`.

### PASO 9 · C7 — Justino en la nevería
- Disparador: `Zona_Neveria`.
- [V] `C07.mp4`
- [D] `C7_01_justino` → `C7_02_miranda` → `C7_03_justino` → `C7_04_tony` → `C7_05_justino` → `C7_06_alan` → `C7_07_justino`
- [E] Justino se queda en la nevería (NPC). Opcional: la nevería da **curación completa** al grupo.
- [O] «Consigue la llave en la oficina del director» → `Zona_Direccion`.

### PASO 10 · C8 — Oficina del director
- Disparador: interactuar con el escritorio del director (`Zona_CajonDirector`).
- [V] `C08.mp4`
- [D] `C8_01_tony` → `C8_02_cesar` → `C8_03_miranda`
- [E] Se obtienen la **llave de la reja** y una **pistola** extra. Sube la dificultad: más zombies; el **conserje zombie** empieza a perseguir.
- [O] «Llega al autobús» → `Zona_Autobus` (la reja trasera solo se abre con la llave).

### PASO 11 · C9 — El autobús y Canepa
- Disparador: `Zona_Autobus`.
- [V] `C09.mp4`
- [D] `C9_01_canepa` → `C9_02_tony` → `C9_03_canepa` → `C9_04_alan` → `C9_05_miranda`
- [E] **Defensa final**: sobrevivir 90 s (usar el evento «¡Aguanten!» existente) mientras Canepa repara. Oleadas crecientes + conserje zombie.
- [O] «Protege a Canepa: 1:30» (cuenta regresiva).

### PASO 12 · C10 — Escape (final)
- Disparador: termina la cuenta regresiva con el grupo vivo.
- [D] `C10_01_canepa` → `C10_02_alan`
- [V] `C10.mp4` (o, si no existe, el video de victoria actual `15_victoria.mp4`).
- [D] `C10_03_tony` (sobre la pantalla de victoria)
- [E] Pantalla de victoria del Modo Historia → menú.

### Derrota
- Si cae todo el equipo en cualquier paso: pantalla de derrota actual (`16_derrota.mp4`) y **reiniciar desde el último paso** (checkpoint al inicio de cada PASO; las cinemáticas ya vistas no se repiten).

## 5. Checklist para quien implementa
- [ ] Variables globales: `Historia.Paso`, `Historia.CinematicasVistas`, `Historia.Armas`.
- [ ] Zonas en el mapa: Escritorio, Pasillo1, CIC, Telefono, Conserje, Casillero, Neveria, Direccion, CajonDirector, Autobus.
- [ ] Reproductor de video con «mantener para saltar».
- [ ] Sistema de diálogos con audio + globo + avance automático.
- [ ] NPCs: Joel (seguidor), Justino (quieto), Canepa (quieto, objetivo a defender).
- [ ] Placeholders para videos faltantes.
