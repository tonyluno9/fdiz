# Música

Coloca aquí las pistas de música definidas en
[`../audio_manifest.json`](../audio_manifest.json).

Formato requerido:

- `.ogg` Vorbis.
- 44.1 kHz o 48 kHz.
- 16-bit, estéreo recomendado.
- La pista debe tener el nivel normalizado y no saturar.
- Las pistas de partida deben poder repetirse sin un corte audible cuando el evento use `yes`.

Valida la entrega desde la raíz del repositorio:

```bash
python3 gdevelop/scripts/validar_audio.py --check
```
