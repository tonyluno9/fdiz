import json, sys
from pathlib import Path
from PIL import Image
sys.path.insert(0,'pipeline/scripts')
from recortar_ui_lote1 import OVER, PANTALLA, grosor, M, PZ
L=["# INDICE de piezas de interfaz (lote 1)","",
"Grosor de borde = px (izq, arriba, der, abajo) medido en la pieza recortada, desde el borde exterior hasta el relleno interior estable (mediana de 5 lineas de escaneo). `-1` = no se pudo medir. Usar como margenes del Panel Sprite (9-slice) de GDevelop; verificar a ojo los que tengan adornos en esquinas.","",
"| Archivo | Tamano | Hoja de origen | Pantalla | Borde (izq, arr, der, aba) |","|---|---|---|---|---|"]
for j in M['jobs']:
    if j['tipo']=='fondo':
        L.append(f"| {j['id']}.png | 1376x768 | {j['id']} (fondo, sin recorte) | {j['id'][3:]} | - |"); continue
    for n in OVER.get(j['id'],j['nombres']):
        p=PZ/f"{n}.png"; w,h=Image.open(p).size
        b=""
        if n.startswith(("ui_boton","ui_panel","ui_placa","ui_banner","ui_ranura","ui_marco","hud_panel","hud_banner","hud_carta","hud_marco")):
            if n.startswith("ui_boton_") and j['id']=='ui_dificultad': b=str(grosor(p,(.25,.3,.7,.75),(.12,.2,.8,.88),muestra=(.87,.5)))+" (barra gris central ignorada)"
            elif n=='ui_boton_deshabilitado': b=str(grosor(p,tol=8))
            elif n=='ui_placa_titulo': b=str(grosor(p,(.3,.4,.5),(.4,.5,.6),tol=10))+" (aprox: relleno gris, adornos en esquinas)"
            else: b=str(grosor(p))
        else: b="-"
        L.append(f"| {n}.png | {w}x{h} | {j['id']} | {PANTALLA[j['id']]} | {b} |")
for n in "tony tonyfuerte miranda cesar alan castillo alessandro gabo carlos silueta".split():
    L.append(f"| retrato_{n}.png | 256x256 | assetsimage (sin generar) | Retrato (seleccion/HUD/resultados) | - |")
Path('generado/interfaz/INDICE.md').write_text("\n".join(L)+"\n",encoding='utf-8')
print("\n".join(l for l in L if 'ui_' in l or 'hud_' in l)[:6000])
