#!/usr/bin/env python3
"""Fase 21b: activa el audio (SonidoActivo = 1); estaba en 0 desde la fase 10 porque no existían los audios."""
import json, os
PJ = os.path.join(os.path.dirname(__file__), '..', 'FDI-Z', 'FDI-Z.json')
d = json.load(open(PJ, encoding='utf-8'))
for v in d['variables']:
    if v['name'] == 'SonidoActivo': v['value'] = 1
json.dump(d, open(PJ, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
used = set()
def w(evs):
    for e in evs:
        for a in e.get('actions', []):
            if a['type']['value'] in ('PlaySound', 'PlayMusic'): used.add(a['parameters'][1].strip('"'))
        w(e.get('events', []))
for s in d['layouts']: w(s['events'])
allp = {r['name'] for r in d['resources']['resources'] if r['kind'] == 'audio'}
print('SonidoActivo =', [v['value'] for v in d['variables'] if v['name'] == 'SonidoActivo'])
print('audios sin uso en eventos:', sorted(allp - used))
