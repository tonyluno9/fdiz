# Efectos de sonido

Coloca aquí los efectos usando las subcarpetas y nombres definidos en
[`gdevelop/FDI-Z/audio_manifest.json`](../audio_manifest.json).

Formato requerido:

- `.ogg` Vorbis.
- 44.1 kHz o 48 kHz.
- 16-bit.
- Efectos cortos, sin silencio inicial o final innecesario.
- Un archivo por ID; las variantes se agregan como archivos numerados solo cuando el manifiesto las solicite.

No cambies los nombres de los archivos sin actualizar el manifiesto y ejecutar:

```bash
python3 gdevelop/scripts/validar_audio.py --check
```
