# V0 · Video del título (Kling 3.0 Std) — reporte

- request_id: `ab7af4d84dcb428f9b5b913a8639e04f` · estado: completed · 62.4 s totales (inferencia 56.2 s). Un solo envío.
- Costo: la API no lo reporta en la respuesta; según la doc 3 s × $0.084 = $0.252.
- Video real: 1284×716, 24 fps, 3.04 s, 73 cuadros (no 1376×768).
- Campos: la doc usa `last_image` (no `end_image`), se mandó con la misma URL que `image`. Sonido: existe el campo `sound`; se mandó `false`.
- Cuadros: 30 (10 fps) crudos y 30 pixel art 480×270 con paleta fija de 48 colores, sin dithering.
- Costura del bucle (diferencia media de píxel, 0-255): último→primero 0.923; entre consecutivos, media 0.666. La costura es algo mayor que un paso normal, pero de la misma magnitud (bucle casi limpio).
- Línea honesta: cámara quieta (sin zoom ni pan), nadie entra ni sale de cuadro, personajes sin deformaciones visibles en los cuadros revisados; el movimiento es muy sutil (apenas se nota). Problema: la paleta de 48 colores sacada del fondo reducido hace que el pixel art pierda color (azules viran a verde azulado, conos de luz amarillos lavados y granulado en la acera/zonas oscuras) — el crudo conserva mejor el color.
- Vistas previas (en `RAIZ\generado\interfaz\video\titulo\`): `preview_crudo.gif`, `preview_pixel.gif`, `comparacion.png`.
- Scripts: `pipeline\scripts\generar_video_v0.py`, `post_video_v0.py`. Nada copiado a `gdevelop\`.
