from PIL import Image, ImageDraw, ImageFont
import json
D='/home/claude/mapa_work/final/'
im=Image.open(D+'mapa_fdiz_completo.png').convert('RGBA')
dat=json.load(open(D+'mapa_fdiz_datos.json'))
s=4
p=im.resize((im.width//s,im.height//s),Image.BOX); d=ImageDraw.Draw(p)
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',14)
fb=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',20)
def lab(x,y,t,font=f,col=(20,20,30)):
    w=d.textlength(t,font=font); d.rectangle([x-w/2-3,y-10,x+w/2+3,y+10],fill=(255,255,255,220)); d.text((x-w/2,y-9),t,fill=col,font=font)
col={'normal':(240,190,30),'electronica':(40,210,110),'restringida':(230,50,50),'restringida_electronica':(160,60,220)}
M=dat['marcadores']
def pt(m,c,r=6): d.ellipse([m['x']/s-r,m['y']/s-r,m['x']/s+r,m['y']/s+r],fill=c,outline=(0,0,0))
for a in dat['props_exteriores']['arboles']:
    r=22 if a['sprite']!='palma_alta' else 14
    d.ellipse([a['x']/s-r,a['y']/s-r,a['x']/s+r,a['y']/s+r],fill=(40,110,45,230),outline=(20,60,25))
for m in dat['props_exteriores']['mesas_redondas']: pt(m,(150,150,160),7)
for z in dat['zonas']:
    if z['nombre'] in ('Pasillo C','Pasillo C2','Pasillo A'): continue
    lab((z['x']+z['w']/2)/s,(z['y']+z['h']/2)/s-16,z['nombre'])
for pu in dat['puertas']:
    d.rectangle([pu['x']/s,pu['y']/s,(pu['x']+pu['w'])/s-1,(pu['y']+pu['h'])/s-1],fill=col[pu['tipo']])
for m in M['rejillas_jefe']: pt(m,(255,60,200),7)
for m in M['bidones_posibles']: pt(m,(230,40,40),6)
for m in M['aparicion_jugadores']: pt(m,(60,140,255),7)
for k in ('servidor_site','llaves_conserjeria','joel_rescate','justino_rescate','botin_raro','tarjeta_electronica','carnada_neveria','corazon_tapitas'): pt(M[k],(255,215,0),8)
h=M['horda_explanada']; d.ellipse([h['x']/s-h['radio']/s,h['y']/s-h['radio']/s,h['x']/s+h['radio']/s,h['y']/s+h['radio']/s],outline=(120,200,60),width=3)
cm=M['camion']; d.rectangle([cm['x']/s-12,cm['y']/s-40,cm['x']/s+12,cm['y']/s+40],fill=(240,190,40),outline=(0,0,0))
lab(cm['x']/s,cm['y']/s+52,'CAMIÓN')
for t,x,y in [('ESTACIONAMIENTO',24,70),('Explanada (horda)',88,96),('Plaza hundida',158,105),('Mesas techadas',156,45),('Cancha techada',133,27),('Edificio E',140,68),('Edificio F · CIC',99,40),('Edificio A',112,129),('Edificio C',224,38),('Edificio D',243,9),('Edificio B',185,30),('Salida peatonal',216,154)]:
    lab(x*32/s,y*32/s,t,fb)
L=[('Puerta normal',col['normal']),('Electrónica',col['electronica']),('Restringida',col['restringida']),('Restringida + electrónica',col['restringida_electronica']),
   ('Inicio de jugadores',(60,140,255)),('Objetivo / rescate / botín',(255,215,0)),('Bidón posible',(230,40,40)),('Rejilla del Jefe',(255,60,200))]
y=p.height-30*len(L)-10
d.rectangle([10,y-10,300,p.height-5],fill=(255,255,255,235))
for t,c in L:
    d.rectangle([20,y,38,y+18],fill=c,outline=(0,0,0)); d.text((46,y),t,fill=(20,20,20),font=f); y+=30
p.save(D+'mapa_fdiz_guia.png'); print(p.size)
