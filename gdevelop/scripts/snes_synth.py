"""Motor de síntesis estilo chip de sonido SNES (S-SMP/DSP simulado): pulso, triángulo, ruido,
cuantización de 8 bits, filtro gaussiano y eco. Usado por fase21_audio.py."""
import numpy as np
SR = 32000  # frecuencia nativa del DSP de la SNES
_RAND = np.random.default_rng(1993).uniform(-1, 1, 400000)
_N = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def hz(name):
    i, acc = 1, 0
    if name[1] == '#': acc, i = 1, 2
    elif name[1] == 'b': acc, i = -1, 2
    m = 12 * (int(name[i:]) + 1) + _N[name[0]] + acc
    return 440.0 * 2 ** ((m - 69) / 12)


def osc(f, wave='p', duty=0.5):
    ph = np.cumsum(f) / SR
    if wave == 'p': return np.where((ph % 1) < duty, 1.0, -1.0)
    if wave == 't': return 4 * np.abs((ph % 1) - 0.5) - 1
    if wave == 's': return 2 * (ph % 1) - 1
    return _RAND[np.floor(ph).astype(np.int64) % len(_RAND)]  # 'n' ruido muestreado


def tone(f0, f1=None, dur=0.2, wave='p', duty=0.5, vol=1.0, a=0.004, r=0.04, curve=1.0, vib=(0, 0)):
    f1 = f0 if f1 is None else f1
    n = max(int(dur * SR), 8); t = np.arange(n) / SR
    f = f0 * (f1 / f0) ** (t / max(dur, 1e-6))
    if vib[0]: f = f * (1 + vib[1] * np.sin(2 * np.pi * vib[0] * t))
    y = osc(f, wave, duty)
    env = np.minimum(1, t / max(a, 1e-4)) * np.clip((dur - t) / max(r, 1e-4), 0, 1) ** curve
    return y * env * vol


def noise(f0, f1, dur, vol=1.0, decay=3.0, a=0.002):
    n = int(dur * SR); t = np.arange(n) / SR
    f = f0 * (f1 / f0) ** (t / dur)
    return osc(f, 'n') * np.minimum(1, t / a) * np.exp(-decay * t / dur) * vol


class Buf:
    def __init__(self, dur, wrap=False):
        self.x = np.zeros(int(dur * SR) + 1); self.wrap = wrap

    def add(self, t, arr):
        i = int(t * SR); L = len(self.x)
        if self.wrap:
            idx = (np.arange(len(arr)) + i) % L; np.add.at(self.x, idx, arr)
        else:
            e = min(L, i + len(arr))
            if e > i: self.x[i:e] += arr[:e - i]

    def seq(self, t, notes, step, **kw):
        for k, f in enumerate(notes):
            if f: self.add(t + k * step, tone(f, f, step, **kw))


def echo(x, delay=0.13, fb=0.38, taps=4, circular=False):
    d = int(delay * SR); out = x.copy()
    for k in range(1, taps + 1):
        sh = np.roll(x, k * d)
        if not circular: sh[:k * d] = 0
        out += sh * fb ** k
    return out


def master(x, peak=0.9, eco=True, circular=False, fade=0.012, bits=8):
    if eco: x = echo(x, circular=circular)
    x = np.convolve(x, [0.25, 0.5, 0.25], mode='same')  # interpolación gaussiana
    m = np.max(np.abs(x)) or 1; x = x / m
    q = 2 ** (bits - 1); x = np.round(x * q) / q  # pérdida de resolución tipo BRR
    x = x * peak
    if not circular and fade:
        n = int(fade * SR); x[-n:] *= np.linspace(1, 0, n)
    return x


def write_wav(path, x):
    import wave
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype('<i2').tobytes())


def parse(s):
    out = []
    for tok in s.split():
        n, b = tok.split(':'); out.append((None if n == 'R' else hz(n), float(b)))
    return out


def music(bpm, chords, lead, lead_wave='p', lead_duty=0.25, lead_vol=0.5, bass='q', arp=None,
          arp_step=0.5, arp_vol=0.22, drums=None, loop=True, tail=1.5, vib=(5.5, 0.006)):
    beat = 60.0 / bpm; bars = len(chords); total = bars * 4 * beat
    b = Buf(total if loop else total + tail, wrap=loop)
    t = 0.0
    for f, bt in parse(lead):
        if f: b.add(t, tone(f, f, bt * beat * 0.92, lead_wave, lead_duty, lead_vol, r=0.05, vib=vib))
        t += bt * beat
    for i, (root, tones) in enumerate(chords):
        t0 = i * 4 * beat; r = hz(root)
        pat = [(0, r), (1, r), (2, r * 1.5), (3, r)] if bass == 'q' else \
              [(k * .5, r * (2 if k % 4 == 2 else 1)) for k in range(8)]
        for off, f in pat:
            ln = beat * (0.9 if bass == 'q' else 0.45)
            b.add(t0 + off * beat, tone(f, f, ln, 't', vol=0.55, a=0.003, r=0.03))
        if arp:
            for k in range(int(4 / arp_step)):
                f = hz(tones[arp[k % len(arp)] % len(tones)])
                b.add(t0 + k * arp_step * beat, tone(f, f, arp_step * beat * 0.8, 'p', 0.125, arp_vol, r=0.03))
        if drums:
            for k in range(16):
                tt = t0 + k * 0.25 * beat
                if drums['k'][k % 16] == 'x': b.add(tt, tone(170, 45, 0.11, 't', vol=0.8, r=0.05))
                if drums['s'][k % 16] == 'x': b.add(tt, noise(5000, 2500, 0.11, 0.45, 4)); b.add(tt, tone(240, 160, .05, 't', vol=.3))
                if drums['h'][k % 16] == 'x': b.add(tt, noise(14000, 9000, 0.04, 0.17, 5))
    return master(b.x, circular=loop, eco=True)
