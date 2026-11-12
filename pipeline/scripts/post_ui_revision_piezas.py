import json, sys
from pathlib import Path
from PIL import Image, ImageDraw
M=json.load(open('pipeline/scripts/manifest_ui_lote1.json',encoding='utf-8'))
sys.path.insert(0,'pipeline/scripts')
from recortar_ui_lote1 import OVER
def sheet(ids,dest,cell=300,cols=6):
    names=[]
    for j in M['jobs']:
        if j['id'] in ids: names+=OVER.get(j['id'],j['nombres'])
    rows=(len(names)+cols-1)//cols
    sh=Image.new('RGB',(cols*cell,rows*(cell+14)),(70,70,90)); d=ImageDraw.Draw(sh)
    for i,n in enumerate(names):
        im=Image.open(f'generado/interfaz/piezas/{n}.png').convert('RGBA'); im.thumbnail((cell-6,cell-6))
        x,y=(i%cols)*cell,(i//cols)*(cell+14); sh.paste(im,(x+3,y+14),im); d.text((x+3,y),n,fill=(255,255,0))
    sh.save(dest)
b=sys.argv[1]
sheet(['logo','ui_botones','ui_paneles','ui_dificultad','ui_ranuras'],b+'s1.png',cols=5)
sheet(['hud_paneles','hud_barras','hud_cartas','ui_placas','ui_marcos_icono'],b+'s2.png',cols=5)
sheet(['iconos_tony_miranda','iconos_cesar_alan','iconos_castillo_alessandro','iconos_gabo_carlos'],b+'s3.png',cell=200,cols=7)
sheet(['iconos_hud','iconos_armas'],b+'s4.png',cell=200,cols=8)
