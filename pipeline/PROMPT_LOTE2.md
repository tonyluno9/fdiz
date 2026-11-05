# Tarea: lote 2 de sprites de FDI-Z

Sigues siendo el agente de la computadora del equipo. Es la continuación del lote 1: usa los mismos scripts de `C:\Users\Angel Perez\Downloads\fdiz\pipeline\scripts\` (generación, procesamiento, revisión automática y reporte), con las mismas reglas de `PROMPT_GENERAR_SPRITES.md`. Hay cambios y cosas nuevas que se explican abajo.

- **Lista de trabajos:** `RAIZ\pipeline\manifest_lote2.json` (78 trabajos; `RAIZ` = `C:\Users\Angel Perez\Downloads\fdiz`).
- **Límite de este lote: 95 generaciones** (78 + 17 para reintentos), aparte de las 180 del lote 1. Máximo 2 reintentos por trabajo.
- **Siguen las mismas reglas:** una imagen por llamada, `1k` como máximo, mismo modelo (`google/nano-banana-2.1/edit`), API key en `WAVESPEED_API_KEY`, máximo 3 a la vez, retomable.
- **Antes de enviar cada trabajo,** escribe en el log una línea "enviado" con su `request_id`.
- **Memoria:** procesa una entidad a la vez, cierra cada imagen al terminar y lanza como máximo 2 subagentes a la vez.

## Decisiones del equipo (ya tomadas)

- **Criollo queda fuera del juego.** No se genera nada de él.
- **Profes:**
  - **Canepa** solo repara el autobús, se sube y lo maneja. Sus animaciones del lote 1 (quieto y caminar) se quedan; las de pegar ya no se usan, pero no las borres. Lo nuevo es `reparar`.
  - **Joel y Justino** son personajes en peligro que los jugadores pueden rescatar: se quedan con miedo en un rincón, piden ayuda, caminan con miedo y agradecen al ser rescatados.
  - Los 21 trabajos de profes que quedaron pendientes en el lote 1 se cancelan. Los reemplaza la fase C de este lote.
- **Interfaz:** por ahora solo mockups (opciones para elegir). No son assets finales: no se recortan ni se separan.

## Fases (campo `fase` de cada trabajo), en este orden

**A. Hojas de giro (11):** el mismo personaje de frente, de perfil a la derecha y de espaldas.
- Se generan primero, porque los trabajos de la fase B con `depende_de` las usan como imagen 2. Súbelas a WaveSpeed igual que las bases y guarda su URL en `uploads.json`.
- Revísalas tú: el personaje debe ser igual a su base y la vista del centro un perfil real (un solo ojo). Si una sale mal, regénerala antes de usarla.
- Procésalas solo para guardar una copia limpia en `generado\limpio_hd\giros\<entidad>\` (frente, perfil y espalda). No van al atlas.

**B. Rehacer las 35 animaciones marcadas en el lote 1.**
- Cada trabajo trae `reemplaza` (el raw anterior). Antes de generar, renombra el raw anterior a `.v1.png` o, si ya existe, `.v2.png`. No borres versiones.
- **Si el trabajo trae `intentar_reprocesar_primero`, primero solo reprocesa el raw actual** con una separación mejorada (`gabo__efecto_habilidad` viene en cuadrícula de 2x2: sepáralo como cuadrícula). Si con eso la revisión sale OK, no lo regeneres.
- Después de generar, procesa y revisa con Opus igual que en el lote 1, comparando contra la base y la hoja de giro. Si alguno sale REHACER otra vez, tiene 1 reintento con una frase de corrección; si sigue mal, se queda marcado.

**C. Profes (13):** las animaciones nuevas de Canepa, Joel y Justino.
- Procésalas igual que las de personajes: 96 px de alto, ancla abajo al centro y el mismo lienzo por entidad.
- `quieto_miedo` está agachado, así que es más bajito; usa como estatura de referencia la de `caminar_miedo_abajo`.

**D. Íconos de habilidades (4 hojas de 6 = 24 íconos).**
- Separa cada ícono por su celda, recórtalo al cuadro con borde de color y exporta cada uno a 64×64 y 32×32 (reducción sin suavizado), con fondo transparente fuera del cuadro.
- Ruta: `generado\sprites\iconos\<nombre>_64.png` y `<nombre>_32.png`, con los nombres de `nombres` (por ejemplo `tony_habilidad`).
- Agrega a la página de revisión una hoja con los 24 íconos en una cuadrícula de 8 personajes × 3 (habilidad, especial y pasiva).

**E. Objetos nuevos (3 hojas):** interruptores y servidor, computadoras y muebles, puertas y cofres.
- Procésalas como las hojas de objetos del lote 1, con los nombres de `nombres`.
- Tamaños (lado mayor): interruptor 32 px; servidor, computadoras, barricada y mueble 48 px; puertas 48 px de alto; cofres 32 px.

**F. Mockups de interfaz (12):** 3 de HUD, 2 de HUD del Jefe, 2 de selección de personaje, 2 de pantalla de título, 2 hojas de logos (4 opciones cada una) y 1 de resultados.
- Se guardan tal cual en `generado\mockups\<tipo>\<opcion>.png`, sin quitar fondo ni separar.
- No los califiques como animaciones. Solo revisa que se vean como una pantalla del juego y que no tengan errores graves (personajes deformes o texto ilegible). Anota esa observación en una línea.

## Entrega

1. **Actualiza `generado\sprites\atlas.json`:**
   - Agrega las animaciones nuevas de los profes con su `fps` y `loop`.
   - Marca a Canepa como `rol: "repara y maneja el camión"`, y a Joel y Justino como `rol: "rescate"`.
   - Agrega una sección `iconos` y los objetos nuevos.
2. **Actualiza `generado\revision\index.html`:**
   - Las animaciones rehechas muestran la versión nueva, y al lado, pequeña, la anterior.
   - Agrega secciones para profes, íconos, objetos nuevos y una galería de mockups agrupada por tipo, con cada opción en grande.
3. **Escribe `generado\revision\REPORTE_LOTE2.md` en español:**
   - Generaciones usadas contra el límite (95).
   - Cuántas de las 35 rehechas quedaron OK y cuáles siguen marcadas, con su razón y la ruta del GIF.
   - Estado de profes, íconos y objetos.
   - **Lista de mockups con su ruta,** agrupados por tipo, para que el equipo elija.
4. **Mensaje final, corto y en español:**
   - Rutas de los sprites, de la página de revisión y del reporte.
   - Cuántas de las 35 se arreglaron.
   - La lista corta de lo que el usuario sí debe mirar.
   - Que los mockups están listos para elegir: HUD, HUD del Jefe, selección, título, logos y resultados.
