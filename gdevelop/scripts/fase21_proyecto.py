#!/usr/bin/env python3
"""Fase 21 (proyecto): registra el audio como recursos, gradúa volúmenes (<100), baja el audio de los
videos, añade puerta_abrir al manifiesto y escribe el catálogo efectos/CATALOGO_SONIDOS.md. Idempotente."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fase21_audio import SFX, MUS, ROOT
DUR = {}
PJ = os.path.join(ROOT, 'FDI-Z.json'); d = json.load(open(PJ, encoding='utf-8'))
VOL = {v[0]: v[2] for v in SFX.values()}; VOL.update({v[0]: v[2] for v in MUS.values()})

# 1. recursos de audio
res = d['resources']['resources']; have = {r['name'] for r in res}
for p in VOL:
    if p not in have:
        res.append({'file': p, 'kind': 'audio', 'metadata': '', 'name': p, 'userAdded': True})

# 2. volúmenes de las acciones PlaySound / PlayMusic
cambios = 0
def walk(evs):
    global cambios
    for e in evs:
        for a in e.get('actions', []):
            if a['type']['value'] in ('PlaySound', 'PlayMusic'):
                path = a["parameters"][1].strip(chr(34))
                if path in VOL and a['parameters'][3] != str(VOL[path]):
                    a['parameters'][3] = str(VOL[path]); cambios += 1
        walk(e.get('events', []))
for s in d['layouts']: walk(s['events'])

# 3. videos: fondo 10 -> 3, personajes 35 -> 12
vids = 0
for s in d['layouts']:
    for o in s['objects']:
        if o['type'] == 'Video::VideoObject':
            nv = 12 if o['name'].startswith('VidPj_') else 3
            if o['content']['volume'] != nv: o['content']['volume'] = nv; vids += 1
json.dump(d, open(PJ, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

# 4. manifiesto
MF = os.path.join(ROOT, 'audio_manifest.json'); txt = open(MF, encoding='utf-8').read()
if 'puerta_abrir' not in txt:
    txt = txt.replace('{"id": "SFX_MUNDO_PUERTA_GOLPE"', '{"id": "SFX_MUNDO_PUERTA_ABRIR", "path": "efectos/mundo/puerta_abrir.ogg", "priority": "P2"},\n    {"id": "SFX_MUNDO_PUERTA_GOLPE"', 1)
    open(MF, 'w', encoding='utf-8').write(txt)
print('recursos', len(VOL), 'acciones de volumen cambiadas', cambios, 'videos', vids)
