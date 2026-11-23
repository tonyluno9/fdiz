# FDI-Z · Diálogos del Modo Historia (para generar las voces)

Instrucciones para la IA de voces:
- Genera **un archivo de audio por línea**, con el **nombre exacto** de la columna «Archivo» (formato `.mp3`, 44.1 kHz, mono, sin música ni efectos, sin silencio largo al inicio o al final: máximo 0.2 s).
- Idioma: **español de México**, natural, juvenil. Nada de doblaje neutro exagerado.
- Respeta la **voz de cada personaje** (tabla de perfiles) para que suene igual en todas sus líneas.
- La columna «Cómo se dice» es la actuación: emoción, volumen y ritmo.
- Los puntos suspensivos (…) son pausas cortas; los guiones (—) son interrupciones.

## Perfiles de voz

| Personaje | Voz |
|---|---|
| **ALAN** | Hombre joven (~20 años), bromista y travieso, ritmo rápido, tono pícaro; cuando tiene miedo intenta seguir bromeando. |
| **MIRANDA** | Mujer joven (~20 años), calmada y sensata, voz clara y firme; cuando regaña es seca y directa. |
| **TONY** | Hombre joven (~20 años), líder seguro, voz media-grave, frases cortas, tono de mando sin gritar de más. |
| **CÉSAR** | Hombre joven (~20 años), listo y sarcástico, voz algo nasal, habla con precisión; cuando se asusta se le quiebra la voz. |
| **JOEL** (profe) | Hombre de ~45 años, nervioso y miedoso, voz aguda cuando se espanta, temblorosa. |
| **JUSTINO** (profe) | Hombre de ~55 años, tranquilísimo, voz grave y lenta, humor seco, como si nada pasara. |
| **CANEPA** (profe) | Hombre de ~50 años, enérgico y apurado, voz fuerte, habla rápido bajo presión. |
| **ALTAVOZ** | Voz institucional grabada (hombre o mujer), monótona, con efecto de bocina/megáfono y ligero eco. |

---

## INTRO · El profe no llega (salón)

| Archivo | Personaje | Texto | Cómo se dice |
|---|---|---|---|
| `INT_01_cesar.mp3` | CÉSAR | Veinte minutos. Oficialmente ya nos podemos ir, eh. Está en el reglamento. | Relajado, burlón, estirándose en la silla. |
| `INT_02_alan.mp3` | ALAN | No está en el reglamento. | Seco, divertido, sin voltear. |
| `INT_03_cesar.mp3` | CÉSAR | Está en *mi* reglamento. | Sarcástico, orgulloso, énfasis en «mi». |
| `INT_04_miranda.mp3` | MIRANDA | Él nunca falta. Nunca. Ni cuando llovió y se inundó el estacionamiento. | Pensativa, un poco preocupada. |
| `INT_05_tony.mp3` | TONY | Pues dejó sus cosas. Ahí está su bolsa. | Observador, señalando, tono normal. |
| `INT_06_alan.mp3` | ALAN | … Entonces sí vino. Y se fue. Sin su bolsa. Qué raro. | Intrigado, lento, cada frase más sospechosa. |

## C1 · La bolsa del profesor

| Archivo | Personaje | Texto | Cómo se dice |
|---|---|---|---|
| `C1_01_alan.mp3` | ALAN | Le echamos un ojito. Uno nomás. | Travieso, medio susurrando, convenciendo. |
| `C1_02_miranda.mp3` | MIRANDA | No. Es su bolsa, Alan. | Firme, regañando, cortante. |
| `C1_03_alan.mp3` | ALAN | ¡Au! Ya, ya… | Dolor exagerado y cómico, sobándose la mano. |
| `C1_04_cesar.mp3` | CÉSAR | Técnicamente es evidencia. Si le pasó algo, hay que saber qué. | Lógico, convenciendo, tono de abogado. |
| `C1_05_tony.mp3` | TONY | Votación. ¿Quién quiere abrirla? | Sonriendo, juguetón pero de líder. |

## C2 · La pistola y la alarma

| Archivo | Personaje | Texto | Cómo se dice |
|---|---|---|---|
| `C2_01_alan.mp3` | ALAN | … ¿Por qué el profe trae una pistola? | Incrédulo, voz baja, casi sin aire. |
| `C2_02_miranda.mp3` | MIRANDA | Ciérrala. Ciérrala ya. | Nerviosa, urgente, susurro fuerte. |
| `C2_03_altavoz.mp3` | ALTAVOZ | Alerta. Se reporta un brote infeccioso en el edificio. Permanezcan en sus salones. Repito: no salgan. | Monótono, institucional, con efecto de bocina y eco. |
| `C2_04_cesar.mp3` | CÉSAR | ¿Brote… infeccioso? | Asustado, la voz se le quiebra. |

## C3 · Golpes en la puerta

| Archivo | Personaje | Texto | Cómo se dice |
|---|---|---|---|
| `C3_01_miranda.mp3` | MIRANDA | Dijeron que no saliéramos… | Susurro, asustada, temblando. |
| `C3_02_tony.mp3` | TONY | Y ya entró uno. Cambio de plan. Nos vamos al CIC, ahí hay teléfono. | Decidido, rápido, tomando el control. |
| `C3_03_cesar.mp3` | CÉSAR | La puerta trasera da directo al pasillo. ¡Vamos! | Urgente, apurado. |

## Camino al CIC (gameplay)

| Archivo | Personaje | Texto | Cómo se dice |
|---|---|---|---|
| `J1_01_alan.mp3` | ALAN | Esto es un simulacro bien hecho, ¿verdad? | Nervioso, risa forzada, intentando bromear. |
| `J1_02_miranda.mp3` | MIRANDA | No es simulacro, Alan. | Seria, seca. |

## C4 · El profe Joel

| Archivo | Personaje | Texto | Cómo se dice |
|---|---|---|---|
| `C4_01_joel.mp3` | JOEL | ¡No me muerdan! ¡No me—! … Ah. Son alumnos. Gracias a Dios. | Pánico total gritando, se corta, y luego alivio jadeando. |
| `C4_02_tony.mp3` | TONY | Profe, ¿qué está pasando? | Serio, preocupado. |
| `C4_03_joel.mp3` | JOEL | No sé. Empezó en el estacionamiento. Gente que… que no se moría. | Tembloroso, en shock, con pausas. |
| `C4_04_miranda.mp3` | MIRANDA | Se viene con nosotros. | Decidida, sin dudar. |
| `C4_05_alan.mp3` | ALAN | ¿Seguro? Grita más que los zombies. | Burlón, en voz baja a los demás. |
| `C4_06_joel.mp3` | JOEL | ¡Te estoy oyendo! | Ofendido, agudo. |

## C5 · Sin línea · Apagón

| Archivo | Personaje | Texto | Cómo se dice |
|---|---|---|---|
| `C5_01_cesar.mp3` | CÉSAR | No hay línea. Cortaron todo… o se cayó todo. | Frustrado, analizando, preocupado. |
| `C5_02_joel.mp3` | JOEL | Hay radio en la oficina del director. Y llaves. Y— | Esperanzado, rápido; se corta de golpe (apagón). |
| `C5_03_miranda.mp3` | MIRANDA | … ¿Alguien más ve eso? | Susurro aterrado, en la oscuridad. |

## Camino a la sala del conserje (gameplay)

| Archivo | Personaje | Texto | Cómo se dice |
|---|---|---|---|
| `J2_01_tony.mp3` | TONY | La sala del conserje tiene el tablero de luz. Vamos para allá. | Tranquilo pero firme. |

## C6 · La sala del conserje

| Archivo | Personaje | Texto | Cómo se dice |
|---|---|---|---|
| `C6_01_tony.mp3` | TONY | ¡Atrás! | Grito corto, de alerta. |
| `C6_02_alan.mp3` | ALAN | ¡Que no sea él, que no sea él…! | Pánico cómico, repitiendo rápido. |

## C6.5 · La escopeta

| Archivo | Personaje | Texto | Cómo se dice |
|---|---|---|---|
| `C65_01_cesar.mp3` | CÉSAR | «Para cuando vuelvan». ¿Cuando vuelvan… quiénes? | Leyendo en voz alta, luego confundido y con miedo. |
| `C65_02_joel.mp3` | JOEL | El conserje lo sabía. Lo dijo en la junta y nadie le creyó. | Pálido, voz baja, culpable. |
| `C65_03_tony.mp3` | TONY | Pues ahora le creemos. Nos la llevamos. | Decidido, cargando la escopeta. |
| `C65_04_joel.mp3` | JOEL | Yo me quedo aquí cuidando el tablero. Si se va la luz otra vez, nadie sale vivo. | Nervioso pero valiente por primera vez. |
| `C65_05_tony.mp3` | TONY | Ahorita volvemos por usted, profe. | Respetuoso, prometiendo. |

## C7 · El profe Justino en la nevería

| Archivo | Personaje | Texto | Cómo se dice |
|---|---|---|---|
| `C7_01_justino.mp3` | JUSTINO | Si van a morir, mínimo que sea con nieve. ¿De cuál quieren? | Tranquilísimo, humor seco, comiendo helado. |
| `C7_02_miranda.mp3` | MIRANDA | Profe, hay zombies afuera. | Incrédula, desesperada. |
| `C7_03_justino.mp3` | JUSTINO | Ya sé. Por eso cerré. Escuchen: el autobús escolar está en el estacionamiento de atrás. El profe Canepa tiene las llaves. | Calmado, ahora serio, explicando despacio. |
| `C7_04_tony.mp3` | TONY | ¿Y por dónde salimos? | Directo, con prisa. |
| `C7_05_justino.mp3` | JUSTINO | Por dirección. El director tiene la llave de la reja trasera en su escritorio. Y algo más, si lo buscan bien. | Misterioso, con media sonrisa. |
| `C7_06_alan.mp3` | ALAN | ¿Usted no viene? | Sorprendido, preocupado. |
| `C7_07_justino.mp3` | JUSTINO | Alguien tiene que cuidar la nieve. | Muy serio, como si fuera obvio (cómico). |

## C8 · La oficina del director

| Archivo | Personaje | Texto | Cómo se dice |
|---|---|---|---|
| `C8_01_tony.mp3` | TONY | La llave… y otra pistola. | Sorprendido, en voz baja. |
| `C8_02_cesar.mp3` | CÉSAR | ¿Todos los profes de esta escuela andan armados o qué? | Sarcástico, indignado. |
| `C8_03_miranda.mp3` | MIRANDA | No importa. Al autobús. Ya. | Urgente, cortante. |

## C9 · El autobús y el profe Canepa

| Archivo | Personaje | Texto | Cómo se dice |
|---|---|---|---|
| `C9_01_canepa.mp3` | CANEPA | ¡Por fin! No arranca. Necesito que alguien me cubra mientras lo conecto. | Agitado, rápido, gritando por encima del ruido. |
| `C9_02_tony.mp3` | TONY | ¿Cuánto tiempo? | Tenso, directo. |
| `C9_03_canepa.mp3` | CANEPA | ¿Un minuto? ¿Dos? ¡Ya vienen! | Nervioso, apurado, gritando. |
| `C9_04_alan.mp3` | ALAN | Siempre son dos. | Resignado, irónico. |
| `C9_05_miranda.mp3` | MIRANDA | Todos en círculo. Nadie se separa. | Firme, tomando el mando. |

## C10 · Escape (final)

| Archivo | Personaje | Texto | Cómo se dice |
|---|---|---|---|
| `C10_01_canepa.mp3` | CANEPA | ¡Arrancó! ¡Súbanse, súbanse! | Eufórico, gritando. |
| `C10_02_alan.mp3` | ALAN | ¡Acelérele, profe! | Emocionado, gritando. |
| `C10_03_tony.mp3` | TONY | … Lo logramos. | Agotado, aliviado, casi riendo. |

**Total: 55 archivos de audio.**
