# FDI-Z · Plan del mapa compacto (propuesta, sin generar nada todavía)

## 1. Diagnóstico del mapa actual (mapa_final.json)
- Casillas de 16 px y personaje de 48 px → 1 personaje = 3 casillas. El área usada mide ~917 × 480 casillas = **~306 × 160 alturas de personaje**. Es casi la escala real (1 casilla ≈ 0.4 m).
- Con la velocidad del interactivo (172 px/s) cruzarlo toma ~84 s; con las velocidades del documento (Tony 68 px/s en sprites de 32 px) serían más de 2 minutos.
- El estacionamiento ocupa ~28 % del ancho (264 × 430 casillas).
- Los salones traen decenas de sillas (E: 312 sillas en 4 salones; B y su copia: 792).
- Hay 20 salones en total (E 4, B 6, B-copia 6, D 4) y solo la planta baja.
- La cámara es compartida y en una sola pantalla, así que un mapa tan grande obliga al grupo a caminar mucho sin nada que hacer.

## 2. Escala propuesta
- **Casilla de 32 px.** Los sprites miden 96 px (gordo y conserje 104), así que un personaje ocupa 3 casillas de alto y 1 de ancho.
- **Compresión de distancias:** ×0.33 en horizontal y ×0.36 en vertical en el campus. El estacionamiento se rediseña como una arena de ~41 × 68 casillas para el final "¡Aguanten!".
- **Tamaño resultante:** 285 × 172 casillas = 9120 × 5504 px, unas 95 × 57 alturas de personaje, más o menos 1/12 del área actual.
- **Una pantalla de 1920 × 1080 con zoom 1** muestra 60 × 34 casillas, o sea 20 × 11 personajes.
- **Tiempo para cruzar el campus:** ~35–40 s a 2 personajes por segundo.
- **Velocidades:** el documento las da para sprites de 32 px. Con sprites de 96 px hay que multiplicar velocidades y radios ×3:
  - Tony: 68 → 204 px/s
  - Zombie normal: 33 → 99 px/s
  - Radio de "te notan": 85 → 255 px
- **Medidas mínimas:**
  - Salón: 14 × 10 casillas interiores.
  - Pasillo: al menos 3 casillas (4 si pasan los 4 jugadores).
  - Puerta: 2 casillas.
  - Muro: 1 casilla.
- **Salones:**
  - Solo planta baja.
  - E queda con 4 salones (E-04 = salón de inicio).
  - B baja de 12 a 6 (3 en cada mitad, con el pasillo techado de la foto 24 entre ambas).
  - D queda con 3 salones y los baños.
- **Muebles:** en los salones, 4 filas × 5 pupitres como máximo.

## 3. Fotos → zona del mapa
| # | Foto | Zona | Qué aporta |
|---|------|------|------------|
| 0 | área verde entre E y A | Explanada | pasto, palmas reales, árbol frondoso |
| 1, 40, 11 | mesas frente a E / vistas desde B | Plaza hundida entre A, E y B | mesa redonda metálica con bancas curvas, muro de piedra, escalones, rampa con franja amarilla |
| 2 | de E hacia A | Explanada | concreto estampado color arena |
| 3, 4, 30 | cancha techada | Cancha | techo de lámina curvo, piso verde y rojo, malla, rampa con símbolo de accesibilidad, muro de piedra |
| 5, 6 | Centro CIC | F, oficina CIC | mostrador curvo blanco con canto de madera, archiveros beige, impresoras, cajas |
| 7, 8 | cubículos CIC | F, cubículos | cancel de vidrio, estantes con equipo, escritorio y PC |
| 9 | Edificio E | E, fachada | muro blanco, balcones, ventanas verdes, barandal |
| 10, 41 | Edificio A | A | blanco, azul marino, franja de vidrio verde, letra "A" |
| 12, 19, 28 | mesas a un costado del CIC | Mesas techadas | techo de policarbonato, postes blancos, mesas redondas, condensadores de AC |
| 13 | entrada | Arco de acceso | arco azul marino "FACULTAD DE INGENIERÍA", caseta, reja blanca |
| 14, 17 | tras el arco | Plaza del corazón | muro de piedra, corazón de tapitas sobre plataforma circular |
| 15, 16 | estacionamiento | Estacionamiento | asfalto, topes amarillo/negro, carros (pickup blanca, sedán rojo, SUV gris) |
| 18 | lockers CIC | F, vestíbulo | lockers beige de 2–3 puertas |
| 20–22 | nevería | Nevería | mesas y sillas blancas, barra de azulejo verde, refri rojo, plantas con flor rosa, lámparas colgantes |
| 23, 25, 31 | pasillos de salones | Porches de E y B | piso crema, barandal de acero, bote de basura |
| 24 | separación de B | Pasillo techado B | bancas metálicas grises |
| 26, 27 | pasillo F | F, pasillo de salas | ventanales con marco de aluminio, puertas de madera oscura, pósters |
| 29 | escaleras B | B | muro azul marino, barandal |
| 32, 38 | salones B y E | Salones | pupitres negros de paleta, escritorio de madera, minisplit, persianas beige, ventiladores |
| 33–36 | salas 1–3 F | Laboratorios | barras blancas con PCs negras, sillas negras, persiana vertical, pizarrón, proyector |
| 37 | salida derecha de A y B | ¿? (pregunta abierta) | arco pequeño azul con letrero "SALIDA" |
| 39 | servidores | F, SITE | racks negros con cables, caja Telmex, UPS |

## 4. Paleta del entorno (de las fotos)
| Uso | Color |
|-----|-------|
| Muro blanco | #ECEBE6 |
| Azul marino | #1E2B57 |
| Vidrio verde | #3F8F6B |
| Piso cerámico crema | #E4D9C2 |
| Concreto estampado | #C9A880, juntas #A8865E |
| Piedra caliza | #BFB6A2, sombra #8C8372 |
| Pasto | #5FA544, oscuro #3F7F33 |
| Franja táctil | #F2C230 |
| Persiana | #CDB48A |
| Madera | #8A5A32 |
| Asfalto | #4E5058 |
| Barra de la nevería | #2F6B4A |

## 5. Qué se hace sin gastar generaciones (en código, con la paleta)
Pisos y muros en mosaico, porque necesitan repetirse sin costuras y que se vean nítidos:
- **Pisos:**
  - cerámico crema
  - cerámico gris de laboratorio
  - azulejo de baño
  - madera
  - loseta de servidores
  - asfalto con rayas
  - banqueta
  - calle
  - cancha con líneas
  - franja táctil
  - escalones
- **Muros (vista 3/4):** remate superior + cara frontal de 1 casilla, con variantes:
  - blanco liso
  - zoclo azul
  - ventana verde
  - ventana con persiana
  - esquinas y uniones

## 6. Qué se genera en WaveSpeed (≈14 imágenes, varias piezas por imagen)
Todas con fondo magenta, vista cenital 3/4 como los personajes, imagen 1 = estilo (hoja de sprites existente) e imagen 2 = foto real.

| # | Hoja | Piezas | Foto de referencia |
|---|------|--------|--------------------|
| M1 | Salón | pupitre de paleta negro (2 ángulos), escritorio del profesor, silla, pizarrón de pared, minisplit, ventilador de techo, bote, persiana | 38 |
| M2 | Laboratorio | estación PC (barra + monitor), silla de oficina, pizarrón, proyector | 33 |
| M3 | CIC | mostrador curvo, archivero, impresora/copiadora, cajas, lockers beige, estante con equipo | 6, 18 |
| M4 | Site | rack de servidores (2), UPS, caja Telmex, bulto de cables, tablero eléctrico | 39 |
| M5 | Nevería | mesa blanca, silla blanca, barra verde, refri rojo, vitrina de helados, cartel del menú, maceta con flor, caja registradora | 21, 22 |
| M6 | Oficinas A/C | escritorio en L, sillón de espera, mesa de juntas, silla de visita, librero, garrafón, cancel de vidrio | 7, 8 |
| M7 | Baños | inodoro, mingitorio, lavabo con espejo, divisor con puerta, secador | (sin foto) |
| M8 | Exterior · mobiliario | mesa redonda con bancas curvas, banca de pasillo, poste de luz, bote exterior, directorio UACAM, condensador de AC, barandal | 1, 24, 41 |
| M9 | Exterior · vegetación | palma real (2), árbol frondoso (2), arbusto, árbol joven, jardinera de piedra | 0, 40 |
| M10 | Hitos | arco "FACULTAD DE INGENIERÍA" con caseta, corazón de tapitas en plataforma, arco de salida | 13, 17, 37 |
| M11 | Estacionamiento | pickup blanca, sedán rojo, SUV gris, tope, reja corrediza (cerrada/abierta), cono | 15, 16 |
| M12 | Cancha | postes y orilla del techo, canasta, malla, rampa | 3, 4 |
| T1 | Texturas | concreto estampado, muro de piedra (tope y cara), pasto con detalles, tierra; luego se vuelven repetibles en código | 2, 14 |
| T2 | Fachadas | segmento de fachada E/B con balcón, torre de escalera azul marino, letra "A", techo de policarbonato | 9, 10, 29 |

Tope sugerido: 20 generaciones (14 + reintentos). Puertas, servidor, computadora e interruptor ya vienen en el lote 2.
Nota: los lockers y la máquina del lote 1 miden 48 px de alto (la mitad de un personaje). En el mapa conviene usarlos ×2 (vecino más cercano).

## 7. Entrega para GDevelop
- Mapa en Tiled (.tmj) con estas capas:
  - suelo
  - muros (colisión)
  - decoración baja
  - decoración alta (copas de árbol, techos)
  - objetos (puertas, niebla por zona, rejillas del Jefe, objetivos, bidones, aparición de jugadores, camión)
- Tileset PNG de 32 px.
- Sprites sueltos para los objetos.
- Lista de zonas con su rectángulo en px para las tapas de niebla.
