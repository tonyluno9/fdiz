#!/usr/bin/env python3
"""Fase 21c: los parámetros de archivo de PlaySound/PlayMusic son de tipo 'soundfile' (nombre de recurso
sin comillas). Con comillas, GDevelop pedía el archivo '"musica/menu.ogg"' y Howler fallaba
('No codec support'). Se quitan las comillas. Idempotente."""
import json, os
PJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'FDI-Z', 'FDI-Z.json')
d = json.load(open(PJ, encoding='utf-8')); n = 0
def w(evs):
    global n
    for e in evs:
        for a in e.get('actions', []):
            if a['type']['value'] in ('PlaySound', 'PlayMusic'):
                p = a['parameters'][1]
                if p.startswith('"') and p.endswith('"'): a['parameters'][1] = p[1:-1]; n += 1
        w(e.get('events', []))
for s in d['layouts']: w(s['events'])
json.dump(d, open(PJ, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('rutas corregidas', n)
