"""Post-proceso lote 1 (cero generaciones): recorta hojas, copia a gdevelop, mide bordes, escribe INDICE."""
import json, shutil, sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage
R = Path(__file__).resolve().parents[2]
M = json.loads((R/"pipeline/scripts/manifest_ui_lote1.json").read_text(encoding="utf-8"))
HOJAS = R/"generado/interfaz/hojas"; PZ = R/"generado/interfaz/piezas"; GD = R/"gdevelop/FDI-Z/assets/interfaz"
PZ.mkdir(parents=True, exist_ok=True); GD.mkdir(parents=True, exist_ok=True)
GRID = {  # id: (cols, filas)
 "ilus_modos":(2,1),"logo":(3,1),"ui_botones":(1,4),"ui_paneles":(2,2),"ui_dificultad":(2,2),"ui_ranuras":(4,1),
 "hud_paneles":(2,2),"hud_barras":(2,2),"hud_cartas":(4,1),"iconos_tony_miranda":(3,2),"iconos_cesar_alan":(3,2),
 "iconos_castillo_alessandro":(3,2),"iconos_gabo_carlos":(3,2),"iconos_hud":(4,2),"iconos_armas":(4,2),
 "ui_placas":(2,2),"ui_marcos_icono":(4,2)}
PANTALLA = {"ilus_modos":"Seleccion de modo","logo":"Titulo","ui_botones":"Menus (todos)","ui_paneles":"Pausa/Resultados/Seleccion/Tienda",
 "ui_dificultad":"Seleccion de modo / Tienda","ui_ranuras":"Tienda / Seleccion","hud_paneles":"HUD en partida","hud_barras":"HUD en partida",
 "hud_cartas":"Modo jefe / HUD","ui_placas":"Titulos de pantalla / Victoria / Derrota","ui_marcos_icono":"HUD habilidades / Resultados"}
for k in ("iconos_tony_miranda","iconos_cesar_alan","iconos_castillo_alessandro","iconos_gabo_carlos"): PANTALLA[k]="HUD habilidades / Seleccion"
PANTALLA["iconos_hud"]="HUD en partida"; PANTALLA["iconos_armas"]="HUD armas"
MARCOS = ("ui_boton","ui_panel","ui_placa","ui_banner","ui_ranura","ui_marco","hud_panel_p","hud_banner","hud_carta","hud_marco","hud_panel_")

def bgmask(a, tol=48):
    d = np.maximum.reduce([np.abs(a[:,:,0].astype(int)-255), a[:,:,1].astype(int), np.abs(a[:,:,2].astype(int)-255)])
    cand = d <= tol
    lab, n = ndimage.label(cand)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:,0], lab[:,-1]]))) - {0}
    bg = np.isin(lab, list(edge))
    # huecos encerrados de magenta casi puro (fondo visto por dentro de un item: D del logo, huecos de silla, etc.)
    strict = d <= 40
    l2, n2 = ndimage.label(strict & ~bg)
    if n2:
        areas = ndimage.sum(strict & ~bg, l2, range(1, n2+1))
        for i, ar in enumerate(areas, 1):
            if ar >= 4: bg |= (l2 == i)
    return bg

def limpiar_halo(a, bg):
    for it in range(8):
        r,g,b = [a[:,:,i].astype(int) for i in range(3)]
        rosa = ((r>150)&(b>140)&(g<r-60)&(g<b-50)) | ((r>180)&(b>g+35)&(r-g>50)&(b>90))
        if it < 3:
            rosa |= ((np.minimum(r,b)>=50)&(g<0.5*np.minimum(r,b))&(np.abs(r-b)<90))
        borde = ndimage.binary_dilation(bg, iterations=1) & ~bg
        bg = bg | (borde & rosa)
    return bg

def grupos(fg, N, minarea):
    for d in (3,6,10,16,24,36,50):
        st = ndimage.binary_dilation(fg, iterations=d) if d else fg
        lab, n = ndimage.label(st)
        lab = lab*fg
        ids = [i for i in range(1,n+1) if (lab==i).sum() >= minarea]
        if len(ids) == N: return [lab==i for i in ids], d
        if len(ids) < N: break
    return None, None

def ordenar(cajas, cols, filas):
    idx = sorted(range(len(cajas)), key=lambda i: cajas[i][1])
    rows = []
    for i in idx:
        x0,y0,x1,y1 = cajas[i]
        for r in rows:
            ov = min(r['y1'], y1) - max(r['y0'], y0)
            if ov > 0.4*min(r['y1']-r['y0'], y1-y0):
                r['ids'].append(i); r['y0']=min(r['y0'],y0); r['y1']=max(r['y1'],y1); break
        else:
            rows.append({'y0':y0,'y1':y1,'ids':[i]})
    if len(rows) != filas and cols > 1:
        cx = {i:(cajas[i][0]+cajas[i][2])/2 for i in range(len(cajas))}
        o = sorted(cx, key=cx.get)
        gaps = sorted(range(len(o)-1), key=lambda k: -(cx[o[k+1]]-cx[o[k]]))[:cols-1]
        cuts = sorted(gaps); colg=[]; ini=0
        for k in cuts+[len(o)-1]:
            colg.append(sorted(o[ini:k+1], key=lambda i: cajas[i][1])); ini=k+1
        return [colg[c][r] for r in range(filas) for c in range(len(colg)) if r < len(colg[c])]
    out=[]
    for r in sorted(rows, key=lambda r: r['y0']):
        out += sorted(r['ids'], key=lambda i: cajas[i][0])
    return out

OVER = {"hud_barras": ["hud_banner_objetivo","hud_flecha_borde","hud_panel_infestacion","hud_panel_dinero"],
 "iconos_gabo_carlos": ["icono_gabo_q","icono_gabo_e","icono_gabo_pasiva","icono_carlos_q","icono_carlos_extra_escudo","icono_carlos_e","icono_carlos_pasiva"]}

def recortar(j):
    jid = j["id"]; cols, filas = GRID[jid]; j = dict(j)
    if jid in OVER: j["nombres"] = OVER[jid]
    N = len(j["nombres"])
    im = Image.open(HOJAS/f"{jid}.png").convert("RGBA"); a = np.array(im)
    bg = limpiar_halo(a, bgmask(a)); fg = ~bg
    H, W = fg.shape; nota = ""
    gr, d = grupos(fg, N, minarea=W*H*0.0015)
    piezas = []
    if gr is not None:
        cajas=[]
        for m in gr:
            ys,xs=np.where(m); cajas.append((xs.min(),ys.min(),xs.max()+1,ys.max()+1))
        for i in ordenar(cajas, cols, filas):
            piezas.append((gr[i], cajas[i]))
        nota = f"componentes (dil {d})"
    else:
        cw, ch = W//cols, H//filas
        for r in range(filas):
            for c in range(cols):
                m = np.zeros_like(fg); m[r*ch:(r+1)*ch, c*cw:(c+1)*cw] = fg[r*ch:(r+1)*ch, c*cw:(c+1)*cw]
                ys,xs=np.where(m)
                if len(xs)==0: piezas.append((m,(c*cw,r*ch,(c+1)*cw,(r+1)*ch))); continue
                piezas.append((m,(xs.min(),ys.min(),xs.max()+1,ys.max()+1)))
        nota = "CUADRICULA (los componentes no dieron %d)" % N
    res=[]
    for (m,(x0,y0,x1,y1)), nombre in zip(piezas, j["nombres"]):
        x0=max(0,x0-4);y0=max(0,y0-4);x1=min(W,x1+4);y1=min(H,y1+4)
        sub = a[y0:y1,x0:x1].copy(); mk = m[y0:y1,x0:x1]
        # incluir fg de otras componentes? no: solo el grupo. 
        sub[~mk,3]=0
        out = Image.fromarray(sub); out.save(PZ/f"{nombre}.png"); shutil.copy(PZ/f"{nombre}.png", GD/f"{nombre}.png")
        res.append((nombre, out.size, int((sub[:,:,3]>0).sum())))
    return nota, res

def grosor(p, fh=(.3,.4,.5,.6,.7), fv=(.3,.4,.5,.6,.7), tol=28, muestra=None):
    a = np.array(Image.open(p).convert("RGBA")); h,w = a.shape[:2]
    op = a[:,:,3]>0
    cy0,cy1,cx0,cx1 = int(h*.3),int(h*.7),int(w*.3),int(w*.7)
    cen = a[cy0:cy1,cx0:cx1,:3].reshape(-1,3)//16
    key = cen[:,0].astype(int)*256+cen[:,1]*16+cen[:,2]
    mod = np.bincount(key).argmax(); inter = np.array([mod//256, (mod//16)%16, mod%16])*16+8
    if muestra:
        px=a[int(h*muestra[1])-2:int(h*muestra[1])+3,int(w*muestra[0])-2:int(w*muestra[0])+3,:3].reshape(-1,3); inter=np.median(px,axis=0)
    def esc(linea):
        # linea: array (n,4) desde el borde exterior hacia dentro
        n=len(linea); k0=0
        while k0<n and linea[k0,3]==0: k0+=1
        for k in range(k0,n-4):
            if linea[k,3]==0 and k-k0<40 and k>k0+2:  # hueco transparente (p.ej. flecha separada): reiniciar
                k0=k
                while k0<n and linea[k0,3]==0: k0+=1
                continue
            if all(linea[k+t,3]>0 and np.abs(linea[k+t,:3].astype(int)-inter).max()<=tol for t in range(4)): return k-k0
        return None
    out=[]
    for lado in range(4):
        v=[]
        for f in (fh if lado in (0,2) else fv):
            if lado==0: l=a[int(h*f),:int(w*.5)]
            elif lado==2: l=a[int(h*f),int(w*.5):][::-1]
            elif lado==1: l=a[:int(h*.5),int(w*f)]
            else: l=a[int(h*.5):,int(w*f)][::-1]
            e=esc(l)
            if e is not None: v.append(e)
        out.append(int(np.median(v)) if v else -1)
    return tuple(out)

if __name__ == "__main__":
    ids = sys.argv[1:]
    indice=[]; avisos=[]
    for j in M["jobs"]:
        if j["tipo"]!="hoja" or (ids and j["id"] not in ids): continue
        if not (HOJAS/f"{j['id']}.png").exists(): print("sin hoja", j["id"]); continue
        nota,res = recortar(j); print(j["id"], nota, [(n,s) for n,s,_ in res])
        for n,s,area in res: indice.append((n,j["id"],PANTALLA[j["id"]],s))
    json.dump([(n,h,p,list(s)) for n,h,p,s in indice], open(R/"generado/log/_indice_tmp.json","w"))
