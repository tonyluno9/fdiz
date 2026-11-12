# Reporte lote 1 (piezas de interfaz en hojas), 2026-11-11

## Generaciones
23 enviadas, 23 completadas, 0 fallidas, 0 reintentos de generacion (un intento por hoja). Modelo `google/nano-banana-2.1/edit`, 1k, png. Log: `generado/log/jobs_ui.jsonl`. Creditos: la API no los reporta en la respuesta.

| Hoja | request_id |
|---|---|
| bg_titulo | 842f047bfa3a44d2845290f3397b9ad0 |
| bg_modos | 0f3d15611a264a699f27ff9b88607529 |
| bg_seleccion | c3f174df1325423eaa9a5a1e0b8a01fe |
| bg_tienda | 093201f64b0a4c84bf125b705dd6c5e5 |
| bg_victoria | 3281cb5ae15a41e894b8c599f06299d2 |
| bg_derrota | 4d3d0c9847dc4448bd5171c679b85296 |
| ilus_modos | 0761afcd301641318eef63a7734e55bf |
| logo (21:9, aceptado por la API) | c1ac55c67c764729bf7510c79129233f |
| ui_botones | bd74e5b4d833415f965865c5001c10af |
| ui_paneles | a0aef07d922840e7930ca143a0bb0bf5 |
| ui_dificultad | fbd9f98ea50b4ed0a9e607298f34937f |
| ui_ranuras | face59a4a94b436bb07506d17e5b0e61 |
| hud_paneles | bef00cdb083b4ef7a284e858ce1d612b |
| hud_barras | 11e83e8c17aa4ab8ad5c5156e551ba4e |
| hud_cartas | 3b2e0d78de5f4de5bf9c0689b214b70f |
| iconos_tony_miranda | 5e700991af5545a494453005bc1c99a1 |
| iconos_cesar_alan | d621cb7727da4e3cb1637b7ece342510 |
| iconos_castillo_alessandro | dad8b476c2934706b6e47ec23e882a97 |
| iconos_gabo_carlos | c24baaa9846843cfb92174c423d17819 |
| iconos_hud | f01ff6c4d6114405bb71cbd1474fa48e |
| iconos_armas | 4cb307a0575e420ab3133583a4b6fc33 |
| ui_placas | c2eeb3732a5c40c69cce2051523bf62c |
| ui_marcos_icono | d82dc20c16ac4df197631e0b74a685c8 |

El logo 21:9 salio a 1584x672 (las demas hojas son 1376x768).

## Revision visual de las hojas y cosas a decidir (director)
- **Disposicion real distinta a la pedida:** `ui_botones` (2x2, no columna), `ui_ranuras` (2x2, no fila), `hud_barras` (banner arriba-izq, flecha arriba-der, infestacion y dinero abajo). Recortado en orden de lectura real y nombrado por contenido: en `hud_barras` quedan hud_banner_objetivo, hud_flecha_borde, hud_panel_infestacion (zombi), hud_panel_dinero (moneda). Botones: normal, seleccionado, presionado (oscuro hundido), deshabilitado (gris), correcto.
- **iconos_gabo_carlos:** la hoja trae 7 objetos, no 6: llave, DOS escudos y placa con flecha. `icono_carlos_q` = llave, `icono_carlos_pasiva` = placa con flecha abajo. **Decidido por Tony (11 nov): `icono_carlos_e` = escudo de borde naranja.** El otro (escudo de acero con centro naranja) quedó como `icono_carlos_extra_escudo`, sin uso.
- **Botones de dificultad y ui_boton_*:** `ui_boton_facil/normal_dificultad/dificil/comprar` traen una barra gris clara central (marcador de texto) que no se pidio; la calavera de "dificil" y la moneda de "comprar" estan bien. Hay que taparla en GDevelop o recortarla. Los botones normal/seleccionado/presionado/deshabilitado son limpios; el seleccionado incluye la flechita naranja a la izquierda (la pieza es 591 px de ancho, el cuerpo 534).
- `ui_placa_titulo` sale con interior gris (no navy) y adornos de slime/calaveras en las esquinas; el 9-slice debe tener en cuenta las esquinas.
- `ui_panel_tienda`: interior azul acero plano, ok. `ui_panel_pausa` lleva una cabecera integrada.
- `ui_ranura_tienda_sel` (brillo naranja) y `ui_ranura_retrato_sel` (brillo amarillo) traen glow horneado; se limpio el halo rosa/magenta pero queda un contorno claro difuso.
- `logo_fdiz_3` (version "compacta cuadrada") salio con texto en dos lineas: "FDI" y "-Z" separados; la Z se lee, pero el guion queda suelto. Letras correctas en las 3 versiones (F D I - Z). Los interiores de la D llevaban magenta de fondo; se volvieron transparentes.
- `iconos_hud`: `icono_mordido` es un brazo sin muchos rasgos (la marca verde es pequena); `icono_revivir` correcto. `icono_arma_punos` son dos punos (un solo icono con dos manos). `icono_arma_regla` sin marcas.
- Fondos: `bg_derrota` mantiene zombis tambien en el borde derecho (no tan calmo como pidio el prompt) y el conserje esta al frente; `bg_victoria` tiene la mitad derecha limpia, bus sin letras. `bg_titulo` muestra la fachada recreada con los 4 heroes a la izquierda, sin marcos ni logo; `bg_tienda` y `bg_modos` limpios, sin personajes. `bg_seleccion` con circulo de luz a la izquierda.

## Recorte (cero generaciones)
- Las 17 hojas de piezas dieron el numero esperado de componentes por flood fill desde el borde + union de fragmentos (dilatacion 3 a 24 px segun la hoja, anotada en el script). Ninguna necesito el recorte por cuadricula.
- Huecos de fondo encerrados dentro de un item (contador de la D, huecos de silla/pistola/escopeta, centro de las escobas de Alan, triangulo del tenis) se quitaron como fondo cuando eran magenta casi puro (>= 4 px); es posible que algun toque de magenta voluntario del modelo (p. ej. punto de la chincheta de `icono_cesar_pasiva`) haya quedado igual. Halo magenta/rosa en el contorno limpiado hasta 8 iteraciones; no se ve halo en las hojas de contacto, pero revisar bordes oscuros-morados en fondos claros.
- Celdas vacias de pasivas: ninguna; las 8 pasivas estan dibujadas (Tony monedas, Miranda corazon con remolino, Cesar ruta y chincheta, Alan ojo con etiqueta, Castillo hamburguesa con cruces verdes, Alessandro reloj de arena con flechas, Gabo escoba entre manos, Carlos placa con flecha).
- Piezas dudosas: `icono_miranda_e` (minigun) 569 px de ancho por ser un objeto alargado, correcto; `icono_alan_e` el circulo magenta interior se hizo transparente.
- Piezas: `generado/interfaz/piezas/` (95 archivos con los 9 retratos + silueta y los 6 fondos), copiadas a `gdevelop/FDI-Z/assets/interfaz/`.

## Retratos
`retrato_<tony|tonyfuerte|miranda|cesar|alan|castillo|alessandro|gabo|carlos>.png` y `retrato_silueta.png` (silueta de Tony), 256x256, nearest, transparentes. Busto cuadrado (cabeza y hombros). Alguna mota blanca suelta en el pelo de Tony/Tonyfuerte/Miranda (fondo blanco original no totalmente limpio).

## Revision de efectos y caminar_lado (cero generaciones)
- `generado/interfaz/revision_efectos.png` (16 efectos x 4 frames): ok en general. Los de Gabo/habilidad son frames con humo y rayas de velocidad cortados/irregulares; los de Cesar/habilidad (lluvia de codigo) y Miranda/habilidad cambian de forma mucho entre frames.
- `generado/interfaz/revision_caminar_lado.png` (9 jugables x 6 frames): marcados en rojo con "PIERNAS?": alan frame 02, alessandro frame 03, carlos frame 02 (piernas juntas/una pierna oculta o postura rara). Tony frames 03 y 05 tienen una sombra gris extra en el torso (no son piernas). Marcado a ojo, conviene confirmar.

## Otros archivos
`generado/interfaz/INDICE.md` (archivo, hoja, pantalla y grosor de borde izq/arriba/der/abajo medido). Scripts: `pipeline/scripts/generar_ui_lote1.py`, `recortar_ui_lote1.py`, `indice_ui_lote1.py`, `post_ui_retratos.py`, `post_ui_contactos.py`, `post_ui_revision_piezas.py`.
