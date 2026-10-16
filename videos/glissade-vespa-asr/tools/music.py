"""Fond musical synthétisé (déterministe, sans droits) calé sur le film de 79 s.

90 BPM, ré mineur (Rém – Si♭ – Fa – Do, deux mesures par accord).
  0–13,4 s   images réelles : nappe seule, très discrète (le son d'origine domine)
  13,4–31 s  carte et tableau de bord : nappe + basse + arpège doux
  31–52 s    explication 3D : + charleston léger ; carillon quand l'ASR coupe la puissance (36,2 s)
  50,6–52 s  montée de tension (l'arrière décroche), impact grave à la chute (52,0 s), puis silence rythmique
  57–64 s    résumé : accord de résolution
  64–74 s    vos commentaires : le groove revient (un commentaire par temps), vague à 72,7 s
  74–79 s    la question épinglée (nassim132001) : accord ouvert, fondu de sortie
Usage : python3 tools/music.py   (numpy + bibliothèque standard)
"""
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/music/fond.wav"
SR = 44100
TOTAL = 79.0
N = int(TOTAL * SR)
BEAT = 60 / 90
BAR = 4 * BEAT
T = np.arange(N) / SR
rng = np.random.default_rng(20260919)

# repères (temps global du film)
S2, S4, ASR_CUT, RISE, FALL, CALM_END, S5 = 13.4, 31.2, 36.2, 50.6, 52.0, 54.6, 57.0
S6, QUESTION = 64.0, 74.0  # commentaires (sur les temps : 96e et 111e)

mtof = lambda m: 440.0 * 2 ** ((m - 69) / 12)
L = np.zeros(N)
Rr = np.zeros(N)


def place(sig, t0, gain=1.0, pan=0.0):
    i0 = int(t0 * SR)
    if i0 >= N:
        return
    sig = sig[: N - i0]
    L[i0 : i0 + len(sig)] += sig * gain * (1 - pan) / 2 * 2 ** 0.5
    Rr[i0 : i0 + len(sig)] += sig * gain * (1 + pan) / 2 * 2 ** 0.5


def tone(freq, dur, harm=((1, 1.0),), attack=0.01, decay=None, release=0.05, detune=0.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for k, a in harm:
        for d in ((-detune, detune) if detune else (0,)):
            s += a * np.sin(2 * np.pi * freq * k * (1 + d) * t)
    env = np.minimum(1, t / max(attack, 1e-4))
    if decay:
        env *= np.exp(-t / decay)
    env *= np.minimum(1, (dur - t) / max(release, 1e-4))
    return s * env


def noise(dur):
    return rng.standard_normal(int(dur * SR))


def highpass(x):
    return np.diff(x, prepend=x[0])


CHORDS = [[50, 53, 57, 62], [46, 50, 53, 58], [41, 45, 48, 53], [48, 52, 55, 60]]  # Rém, Si♭, Fa, Do
CH_DUR = 2 * BAR
n_ch = int(np.ceil(TOTAL / CH_DUR))

for c in range(n_ch):
    t0 = c * CH_DUR
    if t0 >= S6:
        break  # les commentaires ont leur propre passage, plus bas
    chord = CHORDS[c % 4]
    if t0 >= S5:
        chord = [50, 57, 62, 64]  # Rém add9, résolution
    # nappe
    for m in chord:
        place(tone(mtof(m), CH_DUR + 1.6, harm=((1, 1.0), (2, 0.28), (3, 0.1)), attack=1.4, release=1.6, detune=0.0016), t0, 0.05)
    # basse (à partir de la carte, coupée pendant la glissade)
    for b in range(4):
        tb = t0 + b * (CH_DUR / 4)
        if S2 <= tb < FALL or tb >= S5:
            place(tone(mtof(chord[0] - 12), 1.3, harm=((1, 1.0), (2, 0.25)), attack=0.02, decay=0.6), tb, 0.16)
    # arpège en croches
    pattern = [chord[0] + 12, chord[1] + 12, chord[2] + 12, chord[3] + 12, chord[2] + 12, chord[1] + 12]
    for k in range(int(CH_DUR / (BEAT / 2))):
        tk = t0 + k * BEAT / 2
        if not (S2 <= tk < FALL or (tk >= S5 and k % 2 == 0)):
            continue
        g = 0.055 if tk < S4 else 0.065
        place(tone(mtof(pattern[k % len(pattern)]), 0.6, harm=((1, 1.0), (2, 0.35), (4, 0.08)), attack=0.005, decay=0.18), tk, g, pan=0.35 if k % 2 else -0.35)

# charleston léger sur les contretemps pendant l'explication 3D
k = 0
tk = S4 + BEAT / 2
while tk < FALL:
    hat = highpass(highpass(noise(0.08))) * np.exp(-np.arange(int(0.08 * SR)) / SR / 0.018)
    place(hat, tk, 0.018, pan=0.2)
    tk += BEAT

# carillon : l'ASR coupe la puissance
for m, dt in ((81, 0.0), (88, 0.12)):
    place(tone(mtof(m), 1.6, harm=((1, 1.0), (2.76, 0.25), (5.4, 0.08)), attack=0.003, decay=0.45), ASR_CUT + dt, 0.07)

# montée de tension puis impact à la chute
n_r = int((FALL - RISE) * SR)
u = np.arange(n_r) / n_r
riser = highpass(noise(FALL - RISE)) * u ** 2 * 0.5
sweep = np.sin(2 * np.pi * np.cumsum(200 + 600 * u ** 2) / SR) * u ** 1.5
place(riser, RISE, 0.09)
place(sweep, RISE, 0.035)
tb = np.arange(int(1.6 * SR)) / SR
boom = np.sin(2 * np.pi * np.cumsum(58 - 18 * np.minimum(1, tb / 0.5)) / SR) * np.exp(-tb / 0.45)
place(boom, FALL, 0.32)
place(highpass(noise(0.35)) * np.exp(-np.arange(int(0.35 * SR)) / SR / 0.08), FALL, 0.12)

# vos commentaires : une mesure par accord, basse + arpège en croches + charleston (générateur à part,
# pour que les bruits des passages précédents et la réverbération restent identiques)
rng6 = np.random.default_rng(20261016)
for b in range(int(round((QUESTION - S6) / BAR)) + 1):
    t0 = S6 + b * BAR
    if t0 >= QUESTION:
        break
    chord = CHORDS[b % 4]
    dur = min(BAR, QUESTION - t0)
    for m in chord:
        place(tone(mtof(m), dur + 1.2, harm=((1, 1.0), (2, 0.28), (3, 0.1)), attack=0.6, release=1.2, detune=0.0016), t0, 0.045)
    for q in range(4):
        tq = t0 + q * BEAT
        if tq < QUESTION:
            place(tone(mtof(chord[0] - 12), 0.9, harm=((1, 1.0), (2, 0.25)), attack=0.02, decay=0.45), tq, 0.15)
    pattern = [chord[0] + 12, chord[1] + 12, chord[2] + 12, chord[3] + 12, chord[2] + 12, chord[1] + 12, chord[3] + 12, chord[2] + 12]
    for k in range(8):
        tk = t0 + k * BEAT / 2
        if tk < QUESTION:
            place(tone(mtof(pattern[k]), 0.5, harm=((1, 1.0), (2, 0.35), (4, 0.08)), attack=0.005, decay=0.15), tk, 0.06, pan=0.35 if k % 2 else -0.35)
        th = tk + BEAT / 4
        if k % 2 == 1 and th < QUESTION:
            hat = highpass(highpass(rng6.standard_normal(int(0.07 * SR)))) * np.exp(-np.arange(int(0.07 * SR)) / SR / 0.016)
            place(hat, tk, 0.02, pan=0.2)
# la vague (72,7 s) : petite montée sur une mesure
n_w = int((QUESTION - (QUESTION - 2 * BEAT)) * SR)
uw = np.arange(n_w) / n_w
place(highpass(rng6.standard_normal(n_w)) * uw ** 2 * 0.4, QUESTION - 2 * BEAT, 0.07)
# la question : accord ouvert (Si♭ maj7 add9, pas de résolution), deux notes qui montent
for m in (46, 53, 57, 60, 62):
    place(tone(mtof(m), TOTAL - QUESTION + 1.0, harm=((1, 1.0), (2, 0.28), (3, 0.1)), attack=0.9, release=2.0, detune=0.0016), QUESTION, 0.05)
place(tone(mtof(46 - 12), 2.4, harm=((1, 1.0), (2, 0.25)), attack=0.02, decay=1.0), QUESTION, 0.18)
for m, dt in ((81, 0.0), (86, 0.22)):
    place(tone(mtof(m), 1.8, harm=((1, 1.0), (2.76, 0.25), (5.4, 0.08)), attack=0.003, decay=0.5), QUESTION + dt, 0.06)

# niveaux par passage : très bas sous les images réelles, calme pendant la glissade, fondu final
lvl = np.interp(T, [0, S2 - 0.4, S2 + 1.0, FALL, FALL + 0.4, CALM_END, S5, QUESTION, TOTAL - 1.8, TOTAL], [0.35, 0.35, 1, 1, 0.55, 0.55, 0.9, 0.9, 0.8, 0])
L *= lvl
Rr *= lvl

# réverbération (convolution FFT avec une réponse impulsionnelle synthétique)
ir_n = int(1.8 * SR)
ir = rng.standard_normal(ir_n) * np.exp(-np.arange(ir_n) / SR / 0.45)
ir /= np.sqrt((ir ** 2).sum())
size = 1 << int(np.ceil(np.log2(N + ir_n)))
IR = np.fft.rfft(ir, size)
wetL = np.fft.irfft(np.fft.rfft(L, size) * IR, size)[:N]
wetR = np.fft.irfft(np.fft.rfft(Rr, size) * IR, size)[:N]
mixL, mixR = L + 0.28 * wetL, Rr + 0.28 * wetR
peak = max(np.abs(mixL).max(), np.abs(mixR).max())
mix = np.stack([mixL, mixR], axis=1) / peak * 10 ** (-3 / 20)

OUT.parent.mkdir(parents=True, exist_ok=True)
with wave.open(str(OUT), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print("écrit :", OUT, f"{TOTAL:.1f} s")
