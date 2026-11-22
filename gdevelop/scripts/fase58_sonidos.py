"""Fase 58 · Efectos de sonido del repositorio (gdevelop/FDI-Z/sonidos_nuevos) en lugar de los sintetizados. Idempotente.

Uso (desde la carpeta fdiz, con GDevelop CERRADO; solo la biblioteca estándar de Python):
    python -I gdevelop/scripts/fase58_sonidos.py
Si se vuelve a correr fase21_proyecto.py (que registra los .ogg), correr esta fase otra vez.

Regla (después del pull del 2026-11-21): los archivos de sonidos_nuevos/ (subidos por el equipo) son copias de la
carpeta 2dsounds con el nombre del uso que se les quiere dar. Manda el repositorio:
  * si el repositorio trae un archivo para ese efecto, se usa ese archivo;
  * si un archivo de 2dsounds que se había elegido aquí el repositorio lo destinó a otra cosa (p. ej. la campana es
    "main_menu_start_sound"), ese efecto vuelve a su sonido original (.ogg);
  * solo se conserva una elección propia cuando el repositorio no le da otro uso a ese archivo (la moneda).
Los archivos de sonidos_nuevos/ no se modifican: se lee de ahí y se escribe una copia procesada en efectos/.

Cada efecto conserva su evento, su momento y su volumen de evento; solo cambia el archivo. Los nuevos son WAV PCM
16 bits mono (48 kHz los que venían a 96 kHz, 44.1 kHz los demás): GDevelop/Howler los reproduce sin convertir.
Procesado: mezcla a mono, baja de 96 a 48 kHz con filtro, quita silencio inicial y final (sin cortar la cola: se
corta 25 ms después del último momento que pasa de -50 dB respecto al pico, con fundido de 15 ms), pico a -1 dBFS y,
si el promedio (RMS de la parte que suena) pasa de -16 dBFS, se baja hasta ahí para que no tape a los demás.
Los .ogg anteriores se quedan en su carpeta (ya no se usan) por si se quiere volver.
"""
import json, math, os, shutil, struct, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
PROY = os.path.join(RAIZ, "gdevelop", "FDI-Z")
PRY = os.path.join(PROY, "FDI-Z.json")
FUENTE = os.path.join(PROY, "sonidos_nuevos")

# recurso del juego -> (archivo de sonidos_nuevos/, por qué)
MAPA = {
    "efectos/mundo/puerta_golpe.ogg": ("door_punch.wav", "el repositorio lo trae para el golpe a la puerta (golpe grave, 0.38 s)"),
    "efectos/habilidades/miranda_especial.ogg": ("minigun.wav", "el repositorio lo trae para la minigun (2.5 s; el especial dura 8 s)"),
    "efectos/habilidades/tony_habilidad.ogg": ("tony_cook_sound.wav", "el repositorio lo trae para Tony cocinando"),
    "efectos/habilidades/tony_especial.ogg": ("tony_powerup.wav", "el repositorio lo trae para el poder de Tony (sube 1.1 s)"),
    "efectos/habilidades/castillo_especial.ogg": ("powerup_generic_sound.wav", "power-up genérico del repositorio (0.39 s): poción curativa"),
    "efectos/mundo/moneda.ogg": ("FNF_EBA_fx_misc_coin_collector.wav", "moneda de dos notas 980 -> 1336 Hz; el repositorio la trae sin otro uso"),
}
# Elegidos antes aquí y devueltos a su .ogg porque el repositorio destinó ese archivo a otro uso:
REVERTIDOS = {
    "efectos/eventos/apagon.ogg": "concierge_death_effect.wav",
    "efectos/mundo/interruptor.ogg": "minigun_ednd_sound.wav",
    "efectos/eventos/objetivo_nuevo.ogg": "main_menu_start_sound.wav",
    "efectos/habilidades/alan_habilidad.ogg": "item_collected.wav",
    "efectos/eventos/objetivo_cumplido.ogg": "tony_cook_sound.wav",
    "efectos/habilidades/gabo_habilidad.ogg": "tony_powerup.wav",
    "efectos/habilidades/cesar_habilidad.ogg": "start_game_sound.wav",
    "efectos/combate/mordida.ogg": "kick_sound_effect.wav",
    "efectos/eventos/paso_objetivo.ogg": "zombie_death.wav",
}
PICO_DB, RMS_MAX_DB, UMBRAL_COLA_DB, MARGEN_COLA, FUNDIDO = -1.0, -16.0, -50.0, 0.025, 0.015
SONIDO = ("PlaySound", "PlaySoundCanal", "PlayMusic", "PlayMusicCanal")


# ------------------------------------------------------------------ WAV
def leer_wav(ruta):
    b = open(ruta, "rb").read()
    if b[:4] != b"RIFF" or b[8:12] != b"WAVE":
        raise ValueError("no es WAV: " + ruta)
    i, fmt, data = 12, None, None
    while i + 8 <= len(b):
        cid, n = b[i:i + 4], struct.unpack("<I", b[i + 4:i + 8])[0]
        if cid == b"fmt ":
            fmt = struct.unpack("<HHIIHH", b[i + 8:i + 24])
        elif cid == b"data":
            data = b[i + 8:i + 8 + n]
        i += 8 + n + (n & 1)
    tag, ch, sr, _, align, bits = fmt
    if tag not in (1, 0xFFFE) or bits not in (16, 24, 32):
        raise ValueError("formato no soportado %s: %s" % (fmt, ruta))
    w, out = bits // 8, []
    for f in range(len(data) // align):
        acc = 0.0
        for c in range(ch):
            o = f * align + c * w
            acc += int.from_bytes(data[o:o + w], "little", signed=True) / float(1 << (bits - 1))
        out.append(acc / ch)
    return sr, out


def escribir_wav(ruta, sr, x):
    pcm = b"".join(struct.pack("<h", max(-32767, min(32767, int(round(v * 32767))))) for v in x)
    cab = b"RIFF" + struct.pack("<I", 36 + len(pcm)) + b"WAVE" + b"fmt " + struct.pack("<IHHIIHH", 16, 1, 1, sr, sr * 2, 2, 16) \
        + b"data" + struct.pack("<I", len(pcm))
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    open(ruta, "wb").write(cab + pcm)


def procesar(sr, x):
    if sr >= 88200:                                    # 96 kHz -> 48 kHz con un filtro paso bajo corto
        k = [0.0625, 0.25, 0.375, 0.25, 0.0625]
        x = [sum(k[j] * x[min(len(x) - 1, max(0, i + j - 2))] for j in range(5)) for i in range(0, len(x), 2)]
        sr //= 2
    pico = max(abs(v) for v in x) or 1.0
    umbral = pico * 10 ** (UMBRAL_COLA_DB / 20)
    ini = next(i for i, v in enumerate(x) if abs(v) > umbral)
    fin = max(i for i, v in enumerate(x) if abs(v) > umbral)
    ini = max(0, ini - int(sr * 0.002))
    fin = min(len(x), fin + int(sr * MARGEN_COLA))
    x = x[ini:fin]
    nf = min(len(x), int(sr * FUNDIDO))
    for i in range(nf):
        x[len(x) - nf + i] *= 1 - (i + 1) / nf
    g = 10 ** (PICO_DB / 20) / pico
    x = [v * g for v in x]
    son = [v for v in x if abs(v) > 10 ** (-40 / 20)] or x
    rms = math.sqrt(sum(v * v for v in son) / len(son))
    lim = 10 ** (RMS_MAX_DB / 20)
    if rms > lim:
        x = [v * lim / rms for v in x]
    return sr, x


def medir(x, sr):
    pico = max(abs(v) for v in x) or 1e-9
    son = [v for v in x if abs(v) > 10 ** (-40 / 20)] or x
    return {"dur": round(len(x) / sr, 3), "pico_db": round(20 * math.log10(pico), 1),
            "rms_db": round(20 * math.log10(math.sqrt(sum(v * v for v in son) / len(son)) or 1e-9), 1), "sr": sr}


def main():
    # 1) los archivos del repositorio (sonidos_nuevos/) tienen que estar
    for _, (arch, _) in MAPA.items():
        if not os.path.exists(os.path.join(FUENTE, arch)):
            sys.exit("Falta gdevelop/FDI-Z/sonidos_nuevos/%s (¿falta hacer pull?)" % arch)

    # 2) procesar y escribir los WAV del juego
    informe = {}
    for viejo, (arch, motivo) in MAPA.items():
        sr, x = leer_wav(os.path.join(FUENTE, arch))
        antes = medir(x, sr)
        sr, x = procesar(sr, x)
        nuevo = viejo[:-4] + ".wav"
        escribir_wav(os.path.join(PROY, *nuevo.split("/")), sr, x)
        informe[viejo] = {"nuevo": nuevo, "origen": arch, "motivo": motivo, "antes": antes, "despues": medir(x, sr)}

    # 3) proyecto: recursos y referencias (eventos y código JS incrustado)
    d = json.load(open(PRY, encoding="utf-8"))
    res = d["resources"]["resources"]
    for viejo, inf in informe.items():
        nuevo = inf["nuevo"]
        res[:] = [r for r in res if r["name"] != viejo]
        if not any(r["name"] == nuevo for r in res):
            res.append({"file": nuevo, "kind": "audio", "metadata": "", "name": nuevo, "userAdded": True})   # igual que los demás
    # los revertidos vuelven a su .ogg (por si este proyecto ya tenía el .wav de una versión anterior de esta fase)
    for viejo in REVERTIDOS:
        wav = viejo[:-4] + ".wav"
        if any(r["name"] == wav for r in res):
            res[:] = [r for r in res if r["name"] != wav]
            if not any(r["name"] == viejo for r in res):
                res.append({"file": viejo, "kind": "audio", "metadata": "", "name": viejo, "userAdded": True})
    txt = json.dumps(d, ensure_ascii=False, indent=2)
    for viejo, inf in informe.items():
        txt = txt.replace('"%s"' % viejo, '"%s"' % inf["nuevo"]).replace('\\"%s\\"' % viejo, '\\"%s\\"' % inf["nuevo"])
    for viejo in REVERTIDOS:
        wav = viejo[:-4] + ".wav"
        txt = txt.replace('"%s"' % wav, '"%s"' % viejo).replace('\\"%s\\"' % wav, '\\"%s\\"' % viejo)
    d = json.loads(txt)
    # comprobación: cada sonido que se reproduce existe como recurso y como archivo
    nombres = {r["name"]: r for r in d["resources"]["resources"]}
    faltan = []

    def recorrer(lst):
        for e in lst:
            if e.get("disabled"):          # desactivado (p. ej. los TODO de pasos y música de la fase 60): no se compila
                continue
            yield e
            yield from recorrer(e.get("events", []))
    for L in d["layouts"]:
        for e in recorrer(L["events"]):
            for a in e.get("actions", []):
                if a["type"]["value"] in SONIDO:
                    n = a["parameters"][1]
                    if n not in nombres or not os.path.exists(os.path.join(PROY, *nombres[n]["file"].split("/"))):
                        faltan.append((L["name"], n))
    if faltan:
        sys.exit("Sonidos sin recurso o sin archivo: %s" % faltan)
    tmp = PRY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False, indent=2))
    os.replace(tmp, PRY)

    # 4) fuentes JS que reproducen sonidos por nombre, y manifiesto de audio
    for nombre in ("audio.js", "profes.js", "jefe_modo.js", "bots_habilidades.js", "net_core.js", "usar.js"):
        ruta = os.path.join(AQUI, nombre)
        if not os.path.exists(ruta):
            continue
        s = open(ruta, encoding="utf-8", newline="").read()
        s2 = s
        for viejo, inf in informe.items():
            s2 = s2.replace('"%s"' % viejo, '"%s"' % inf["nuevo"])
        for viejo in REVERTIDOS:
            s2 = s2.replace('"%s"' % (viejo[:-4] + ".wav"), '"%s"' % viejo)
        if s2 != s:
            open(ruta, "w", encoding="utf-8", newline="").write(s2)
    man_ruta = os.path.join(PROY, "audio_manifest.json")
    man = json.load(open(man_ruta, encoding="utf-8"))
    man["format"]["extensions"] = [".ogg", ".wav"]
    man["format"]["wav"] = "PCM 16 bits mono, 44100 o 48000 Hz (fase 58)"
    for it in man["effects"]:
        # solo los efectos de esta fase: los reemplazados pasan a su .wav y los revertidos vuelven a su .ogg.
        # Los demás .wav del manifiesto (armas, voces de la fase 64...) no se tocan.
        ogg = it["path"][:-4] + ".ogg" if it["path"].endswith(".wav") else it["path"]
        if ogg in informe:
            it["path"] = informe[ogg]["nuevo"]
            it["origen"] = "sonidos_nuevos/" + informe[ogg]["origen"]
        elif ogg in REVERTIDOS:
            it["path"] = ogg
            it.pop("origen", None)
    json.dump(man, open(man_ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(informe, open(os.path.join(PROY, "efectos", "fase58_informe.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for viejo, inf in informe.items():
        print("%-42s -> %-44s %s" % (viejo, inf["origen"], inf["despues"]))
    print("Fase 58 aplicada: %d efectos reemplazados." % len(informe))


def viejo_de(informe, nuevo):
    return next(k for k, v in informe.items() if v["nuevo"] == nuevo)


if __name__ == "__main__":
    main()
