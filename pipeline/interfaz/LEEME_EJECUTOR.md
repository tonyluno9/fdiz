# Instrucciones fijas para el chat ejecutor (WaveSpeed)

El director de arte deja aquí todo lo que hay que generar. Tú no inventas prompts ni cambias nada del arte: solo lees y ejecutas.

Carpeta: `RAIZ\pipeline\interfaz\` (RAIZ = `C:\Users\Angel Perez\Downloads\fdiz`)

## Cada vez que Tony te diga "revisa la carpeta"
1. Abre `ACTUAL.md`. Dice qué lote toca y en qué archivo está.
2. Si ese lote ya está marcado como HECHO en `ACTUAL.md`, no hagas nada y avísale a Tony.
3. Lee el archivo del lote completo y ejecútalo tal cual.
4. Al terminar:
   - Escribe tu reporte en `RAIZ\pipeline\interfaz\reportes\<lote>_reporte.md`.
   - En `ACTUAL.md` cambia el estado del lote a HECHO, con la fecha.

## Reglas que aplican a todos los lotes (salvo que el lote diga otra cosa)
- Un solo intento por imagen u hoja. Nunca regeneres; si sale mal, anótalo en el reporte y sigue.
- Una imagen por llamada. Resolución máxima 1k.
- Modelos: `google/nano-banana-2.1/edit` si la imagen lleva referencias; `google/nano-banana-2.1/text-to-image` solo si no lleva ninguna.
- Prompts copiados exactos, en inglés. Sin texto dentro de las imágenes, salvo el logo "FDI-Z".
- API key en la variable de entorno `WAVESPEED_API_KEY`. Nunca la imprimas ni la guardes.
- Máximo 3 trabajos a la vez. Si la salida ya existe, no se regenera (retomable).
- No toques `assetsimage\`, `FDI-Z.json` ni los scripts de `gdevelop\`.
- Detente y pregunta solo si la API falla, falta la key o algo del lote no se entiende.
