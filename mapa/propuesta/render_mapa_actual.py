import json, sys
from PIL import Image, ImageDraw, ImageFont
d=json.load(open('/home/claude/mapa_in/mapa_final.json'))
def rle(s,n):
    out=[]
    for part in s.split(','):
        v,c=part.split('x'); out+= [int(v)]*int(c)
    assert len(out)==n,(len(out),n)
    return out
W=d['mundo']['ancho_casillas']; H=d['mundo']['alto_casillas']
g=rle(d['mundo']['suelo_rle'],W*H); col=rle(d['mundo']['colision_rle'],W*H)
GC={0:(30,60,30),1:(110,170,80),2:(70,70,78),3:(185,180,170),4:(220,140,70),5:(150,150,155),6:(60,70,90),7:(230,160,90),8:(50,50,55),9:(120,60,50),10:(200,200,120),11:(205,200,190)}
S=int(sys.argv[1]) if len(sys.argv)>1 else 2
im=Image.new('RGB',(W,H))
px=im.load()
for y in range(H):
    for x in range(W):
        c=GC[g[y*W+x]]
        if col[y*W+x]: c=(c[0]//2+100,c[1]//2,c[2]//2)
        px[x,y]=c
PC={0:None,1:(235,230,215),2:(200,220,235),3:(210,205,190),4:(180,215,225),5:(40,40,60),6:(225,215,190),7:(240,190,150),8:(170,120,70)}
MC={1:(40,30,30),2:(120,190,230),3:(150,150,170)}
for b in d['edificios']:
    bw,bh=b['ancho_casillas'],b['alto_casillas']
    p=rle(b['piso_rle'],bw*bh); m=rle(b['muros_rle'],bw*bh)
    bi=Image.new('RGBA',(bw,bh),(0,0,0,0)); bp=bi.load()
    for y in range(bh):
        for x in range(bw):
            c=PC.get(p[y*bw+x]); mm=m[y*bw+x]
            if mm: c=MC[mm]
            if c: bp[x,y]=c+(255,)
    dr=ImageDraw.Draw(bi)
    for o in b['objetos']:
        if o.get('tipo') in ('colision',): continue
        x,y,w,h=o.get('x',0),o.get('y',0),o.get('w',1),o.get('h',1)
        dr.rectangle([x,y,x+max(w,1)-1,y+max(h,1)-1],outline=(160,90,40,255))
    for pu in b['puertas']:
        dr.rectangle([pu['x'],pu['y'],pu['x']+pu['w']-1,pu['y']+pu['h']-1],fill=(255,200,0,255))
    a=b['angulo_grados']
    if a: bi=bi.rotate(-a,expand=True)
    cx,cy=b['centro_casillas_mundo']
    im.paste(bi,(int(round(cx-bi.width/2)),int(round(cy-bi.height/2))),bi)
dr=ImageDraw.Draw(im)
for o in d['mundo']['objetos_exteriores']:
    x,y=o['x'],o['y']; r={'arbol':3,'arbusto':1,'circulo':2,'mesa_metalica':2}[o['tipo']]
    dr.ellipse([x-r,y-r,x+r,y+r],fill={'arbol':(20,100,30),'arbusto':(40,130,40),'circulo':(200,120,60),'mesa_metalica':(180,180,190)}[o['tipo']])
im=im.resize((W*S,H*S),Image.NEAREST)
dr=ImageDraw.Draw(im)
for a in d['areas']:
    if a['espacio']!='mundo': continue
    dr.rectangle([a['x']*S,a['y']*S,(a['x']+a['w'])*S,(a['y']+a['h'])*S],outline=(255,0,255),width=2)
    dr.text((a['x']*S+3,a['y']*S+3),a['texto'],fill=(255,255,0))
im.save('mapa_render.png'); print(im.size)
