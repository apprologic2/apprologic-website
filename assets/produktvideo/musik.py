"""
Soundtrack für das Produktvideo (66 s), komplett synthetisch erzeugt – keine Lizenzfragen.
Benötigt nur numpy. Aufruf:  python musik.py  → musik.wav (wird von render.mjs ins Video gemischt)

Ablauf (Zeiten wie in produktvideo.html):
  0–2,2 s    Uhr tickt, ruhige Fläche
  2,2 s      Störung: tiefer Schlag
  2,4–14,6 s Moll, pulsierender Bass, Ticken wird dichter, Töne für die Chaos-Karten, Anstieg
  14,6 s     Titel: Akzent, Wechsel nach C-Dur
  19,4–57 s  Groove (C–G–Am–F) mit dezenten Bedien-Klängen, ab 45,8 s Melodie
  58,6 s     „Läuft wieder“: Glockenspiel, Schlussakkord, Ausblende
"""
import os
import wave
import numpy as np

SR = 44100
DUR = 66.0
N = int(SR * DUR)
rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N); SEND = np.zeros(N)


def add(sig, t, gain=1.0, pan=0.0, send=0.0):
    i = int(t * SR)
    if i >= N:
        return
    sig = sig[: N - i] * gain
    a = (pan + 1) * np.pi / 4
    L[i:i + len(sig)] += sig * np.cos(a) * 1.414
    R[i:i + len(sig)] += sig * np.sin(a) * 1.414
    SEND[i:i + len(sig)] += sig * send


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def tt(d):
    return np.arange(int(d * SR)) / SR


def noise(d):
    return rng.standard_normal(int(d * SR))


# ---------- Klangerzeuger ----------
def pad(m, dur, a=1.0, r=1.2):
    t = tt(dur + r); f = mtof(m); s = np.zeros_like(t)
    for k, det in enumerate((-0.07, 0.0, 0.06)):
        ff = f * 2 ** (det / 12)
        for h in range(1, 6):
            s += np.sin(2 * np.pi * ff * h * t + k + h) / h ** 1.7
    return s * np.minimum(1, t / a) * np.clip((dur + r - t) / r, 0, 1) / 3


def chord(ms, t, dur, gain, **kw):
    for m in ms:
        add(pad(m, dur, a=kw.get("a", 1.0), r=kw.get("r", 1.2)), t, gain, send=kw.get("send", .5), pan=kw.get("pan", 0))


def pluck(m, d=.7, dec=5.0):
    t = tt(d); f = mtof(m)
    s = (np.sin(2 * np.pi * f * t) + .5 * np.sin(4 * np.pi * f * t) * np.exp(-t * 8)
         + .25 * np.sin(6 * np.pi * f * t) * np.exp(-t * 12))
    return s * np.exp(-t * dec) * np.minimum(1, t / .003)


def bell(m, d=2.5):
    t = tt(d); f = mtof(m); s = np.zeros_like(t)
    for ratio, amp, dec in ((1, 1, 2.2), (2.0, .45, 3.5), (2.76, .3, 5), (5.4, .15, 8)):
        s += amp * np.sin(2 * np.pi * f * ratio * t) * np.exp(-t * dec)
    return s * np.minimum(1, t / .002)


def bass(m, d):
    t = tt(d); f = mtof(m)
    s = np.tanh(2.2 * np.sin(2 * np.pi * f * t)) * .7 + .5 * np.sin(np.pi * f * t)
    return s * np.minimum(1, t / .005) * np.exp(-t * 3) * np.clip((d - t) / .03, 0, 1)


def kick():
    t = tt(.45); f = 45 + 90 * np.exp(-t * 25)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)


def hat(d=.06):
    n = np.diff(noise(d), prepend=0); return n * np.exp(-tt(d)[:len(n)] * 60) * .5


def clap():
    n = np.diff(noise(.25), prepend=0); n = np.convolve(n, np.ones(4) / 4, "same")
    return n * np.exp(-tt(.25)[:len(n)] * 18)


def tick(f=3000):
    t = tt(.03); return np.sin(2 * np.pi * f * t) * np.exp(-t * 200)


def boom():
    t = tt(2.5); f = 30 + 45 * np.exp(-t * 3)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.5)


def crash(d=2.5):
    n = np.diff(noise(d), prepend=0); return n * np.exp(-tt(d)[:len(n)] * 2.2) * .35


def sweep(d, shape):
    """Rauschen mit wanderndem Tiefpass (gleitender Mittelwert); shape(x) liefert Helligkeit 0..1."""
    n = noise(d); out = np.zeros_like(n); chunks = 48; cl = len(n) // chunks
    for c in range(chunks):
        w = max(1, int(70 * (1 - shape(c / chunks))) + 1)
        seg = n[c * cl:(c + 1) * cl + w]
        out[c * cl:(c + 1) * cl] = np.convolve(seg, np.ones(w) / w, "same")[:cl]
    return out


def riser(d):
    x = tt(d)[: int(d * SR)] / d
    return sweep(d, lambda p: p)[: len(x)] * x ** 2


def whoosh(d=.8):
    x = tt(d)[: int(d * SR)] / d
    return sweep(d, lambda p: np.sin(np.pi * p))[: len(x)] * np.sin(np.pi * x) ** 2


def blip(m):
    t = tt(.12); return np.sin(2 * np.pi * mtof(m) * t) * np.exp(-t * 30)


# ---------- Arrangement ----------
BAR = 2.4   # 100 BPM, 4/4
BEAT = BAR / 4

# 0–2,2 s: Uhr tickt
chord([57, 60, 64], 0, 2.2, .12, a=.8, r=.6)
for k in range(4):
    add(tick(2600 if k % 2 == 0 else 2000), .3 + k * BEAT, .25, pan=-.2 if k % 2 == 0 else .2)

# 2,2 s: Störung
add(boom(), 2.2, .9)
add(crash(), 2.2, .25, send=.3)
for m in (45, 46, 51):
    add(pluck(m, 1.5, 2.5), 2.2, .22)

# 2,4–14,6 s: Moll, Spannung
tense = [(45, [57, 60, 64]), (41, [53, 57, 60]), (38, [50, 53, 57, 62]), (40, [52, 56, 59]), (45, [57, 60, 64])]
for b, (root, notes) in enumerate(tense):
    tb = 2.4 + b * BAR
    lift = b / len(tense)
    chord(notes, tb, BAR, .12 + .06 * lift, a=.5, r=.8)
    for k in range(8):
        if tb + k * BEAT / 2 < 14.4:
            add(bass(root, .25), tb + k * BEAT / 2, (.32 if k % 2 == 0 else .22) + .08 * lift)
t = 6.6
while t < 13.4:
    add(hat(), t, .04 + .1 * (t - 6.6) / 6.8, pan=.3)
    t += BEAT / 4
for d, m, p in zip([6.4, 7.0, 7.6, 8.2, 8.8, 9.4, 10.0], [81, 84, 79, 76, 88, 83, 86], [-.6, .6, -.5, .5, -.7, .7, 0]):
    add(pluck(m, .8, 6), d, .16, pan=p, send=.5)
add(riser(1.6), 13.0, .35, send=.3)

# 14,6 s: Titel – Akzent und Wechsel nach Dur
T0 = 14.6
add(kick(), T0, .8); add(boom(), T0, .45); add(crash(3), T0, .3, send=.4)
for m in (72, 79, 84):
    add(bell(m, 3), T0, .16, send=.6)

CHORDS = [(48, [60, 64, 67]), (43, [59, 62, 67]), (45, [57, 60, 64]), (41, [57, 60, 65])]   # C G Am F
MELODY = {13: [74, 71], 14: [72, 76], 15: [77, 72], 16: [76, 79], 17: [74]}
for i in range(18):
    tb = T0 + i * BAR
    root, notes = CHORDS[i % 4]
    chord(notes, tb, BAR, .11, a=.3, r=1.0)
    tones = notes + [notes[0] + 12]
    groove = tb >= 19.4
    if not groove:
        for k in range(4):
            add(pluck(tones[k % 4] + 12, .9, 4), tb + k * BEAT, .1, pan=-.3 if k % 2 else .3, send=.5)
    else:
        for k, idx in enumerate([0, 1, 2, 3, 2, 1, 0, 1]):
            add(pluck(tones[idx] + 12, .5, 7), tb + k * BEAT / 2, .085, pan=-.35 if k % 2 else .35, send=.4)
        for k, o in enumerate([0, 0, 12, 0, 0, 0, 12, 0]):
            add(bass(root + o, .28), tb + k * BEAT / 2, .26)
        for k in range(4):
            bt = tb + k * BEAT
            if bt < 57.0:
                add(kick(), bt, .5)
                add(hat(), bt + BEAT / 2, .07, pan=.25)
                if k in (1, 3):
                    add(clap(), bt, .16, pan=-.1, send=.2)
    for j, m in enumerate(MELODY.get(i, [])):
        add(bell(m, 2.2), tb + j * BAR / 2, .14, pan=.1, send=.6)
add(riser(1.2), 44.6, .15, send=.3)

# Bedien-Klänge
for k in range(5):
    add(tick(1800), 20.2 + k * .16, .08)                                   # Tippen „E-217“
for t_, m in ((22.2, 84), (22.8, 88), (25.4, 84), (26.2, 88)):
    add(blip(m), t_, .12, send=.3)                                         # Chat-Blasen
add(tick(1500), 27.5, .2)                                                  # Klick „Serviceanfrage stellen“
for t_, m in ((29.2, 76), (29.6, 79), (30.0, 83), (30.4, 86)):
    add(blip(m), t_, .1, send=.3)                                          # Formular-Schritte
add(tick(1500), 31.6, .2)                                                  # Klick „Absenden“
add(whoosh(.8), 31.7, .3, send=.3)                                         # Umschlag fliegt
add(bell(88, 1.5), 32.4, .16, send=.5)                                     # Eingang beim Team
add(bell(91, 1.2), 33.2, .1, send=.5)                                      # Team Hydraulik
for t_ in (37.4, 39.6, 42.0):
    add(blip(88), t_, .12, send=.3); add(blip(93), t_ + .07, .1, send=.3)  # Chat-Nachrichten
for j, m in enumerate((84, 88, 91)):
    add(bell(m, 1.8), 42.3 + j * .08, .14, send=.6)                        # „Lösung gesendet“

# 57–58,6 s: kurz still, Spannung
chord([55, 60, 62], 57.2, 1.4, .1, a=.6, r=.6)

# 58,6 s: „Läuft wieder“
add(kick(), 58.6, .4); add(crash(2.5), 58.6, .14, send=.4)
for j, m in enumerate((72, 76, 79, 84)):
    add(bell(m, 2.5), 58.6 + j * .1, .18, send=.6)
end = [(58.6, 48, [60, 64, 67]), (61.0, 41, [57, 60, 65, 67]), (63.4, 48, [55, 60, 64, 67, 72])]
for j, (tb, root, notes) in enumerate(end):
    last = j == len(end) - 1
    chord(notes, tb, 2.6 if last else 2.4, .13, a=.4, r=2.0 if last else 1.0)
    add(bass(root, 1.2 if not last else 2.0), tb, .18)
    if not last:
        tones = notes[:3] + [notes[0] + 12]
        for k, idx in enumerate([0, 1, 2, 3, 2, 1, 0, 1]):
            add(pluck(tones[idx] + 12, .5, 7), tb + k * BEAT / 2, .07, pan=-.35 if k % 2 else .35, send=.4)
for m in (84, 91):
    add(bell(m, 3), 62.2, .12, send=.7)                                    # Abspann


# ---------- Mischung ----------
def ir(seed, d=2.2):
    r = np.random.default_rng(seed).standard_normal(int(d * SR))
    r *= np.exp(-tt(d)[:len(r)] * 3); r = np.convolve(r, np.ones(8) / 8, "same")
    return r / np.sqrt(np.sum(r ** 2))


def conv(x, h):
    n = len(x) + len(h); nf = 1 << (n - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, nf) * np.fft.rfft(h, nf), nf)[:len(x)]


L += conv(SEND, ir(1)) * .35
R += conv(SEND, ir(2)) * .35
mix = np.stack([L, R], axis=1)
mix /= np.max(np.abs(mix))
mix = np.tanh(mix * 1.3) / np.tanh(1.3) * .89
x = np.arange(N) / SR
mix *= np.clip(x / .3, 0, 1)[:, None] * np.clip((DUR - x) / 1.4, 0, 1)[:, None]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "musik.wav")
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print("Fertig:", out)
