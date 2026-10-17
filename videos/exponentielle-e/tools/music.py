"""Exponentielle e — fond musical synthétisé (déterministe, sans droits).

Calme et curieux : 76 BPM, fa majeur, boucle Fmaj7 – Am7 – Dm9 – B♭maj7 (une mesure
chacun). Nappe douce (sinus désaccordés filtrés), petit arpège type piano électrique
en croches, basse ronde sur le premier temps, réverbération légère. Entrée en fondu
(1,5 s), sortie en fondu (4 s). La musique est creusée sous la voix off : son niveau
baisse de ~9 dB quand la voix parle (enveloppe de la voix placée aux débuts de plans
lus dans tools/timing.json, comme dans index.html).

Usage : python tools/music.py [--sans-voix]   (numpy, scipy, soundfile)
  --sans-voix : version sans creusement (niveau constant), pour une voix off ajoutée ailleurs
               → assets/music/exponentielle-fond-sans-voix.wav
"""
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal

ROOT = Path(__file__).resolve().parent.parent
SR = 44100
BPM = 76
BEAT = 60 / BPM
BAR = 4 * BEAT
TIMING = json.loads((ROOT / "tools" / "timing.json").read_text())
FRAMES = TIMING["frames"]
TOTAL = sum(f["duration"] for f in FRAMES.values())
N = int(round(TOTAL * SR))
rng = np.random.default_rng(2718)

mtof = lambda m: 440.0 * 2 ** ((m - 69) / 12)

# Accords (notes MIDI) : Fmaj7, Am7, Dm9, B♭maj7.
CHORDS = [
    [53, 57, 60, 64],  # F A C E
    [57, 60, 64, 67],  # A C E G
    [50, 57, 60, 64],  # D A C E (Dm9 sans tierce grave : D–A–C–E, la 9e = E)
    [46, 53, 57, 62],  # B♭ F A D
]
ROOTS = [41, 45, 38, 46]
ARP = [0, 1, 2, 3, 2, 1, 3, 2]  # ordre des notes de l'arpège sur 8 croches


def t_axis(n):
    return np.arange(n) / SR


def pad_voice(freq, dur):
    n = int(dur * SR)
    t = t_axis(n)
    x = sum(np.sin(2 * np.pi * freq * (1 + d) * t + ph) for d, ph in ((-0.003, 0.0), (0.0, 1.1), (0.0035, 2.3)))
    x += 0.25 * np.sin(2 * np.pi * 2 * freq * t)
    env = np.minimum(1, t / 0.9) * np.minimum(1, (dur - t) / 0.9).clip(0, 1)
    return x * env / 3.3


def pluck(freq, dur=1.6):
    n = int(dur * SR)
    t = t_axis(n)
    env = np.exp(-t * 3.2) * np.minimum(1, t / 0.006)
    x = np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * 2 * freq * t) * np.exp(-t * 6) + 0.12 * np.sin(2 * np.pi * 3 * freq * t) * np.exp(-t * 9)
    return x * env


def bass(freq, dur):
    n = int(dur * SR)
    t = t_axis(n)
    env = np.minimum(1, t / 0.03) * np.exp(-t * 0.9)
    return (np.sin(2 * np.pi * freq * t) + 0.2 * np.sin(2 * np.pi * 2 * freq * t)) * env


def add(buf, x, start, gain=1.0, pan=0.0):
    i = int(start * SR)
    if i < 0:  # départ avant 0 : on coupe le début
        x, i = x[-i:], 0
    if i >= len(buf):
        return
    x = x[: len(buf) - i]
    left, right = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[i : i + len(x), 0] += gain * left * x
    buf[i : i + len(x), 1] += gain * right * x


def reverb(x, seconds=2.2, mix=0.22):
    n = int(seconds * SR)
    t = t_axis(n)
    ir = rng.standard_normal((n, 2)) * np.exp(-t * 3.0)[:, None]
    ir[: int(0.012 * SR)] = 0
    wet = np.stack([signal.fftconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], axis=1)
    wet *= np.abs(x).max() / (np.abs(wet).max() + 1e-9)
    return (1 - mix) * x + mix * wet


def voice_envelope():
    """Enveloppe (0–1) de la voix off placée aux débuts de plans."""
    env = np.zeros(N)
    start = 0.0
    for key in sorted(FRAMES):
        v, sr = sf.read(ROOT / "assets" / "voice" / f"{key}.wav")
        if v.ndim > 1:
            v = v.mean(axis=1)
        v = signal.resample_poly(v, SR, sr)
        i = int(round(start * SR))
        seg = np.abs(v[: max(0, N - i)])
        env[i : i + len(seg)] = np.maximum(env[i : i + len(seg)], seg)
        start += FRAMES[key]["duration"]
    # suiveur d'enveloppe : attaque rapide, relâchement lent
    win = int(0.03 * SR)
    env = np.sqrt(signal.fftconvolve(env**2, np.ones(win) / win, mode="same").clip(0))
    on = (env > 0.02).astype(float)
    att, rel = np.exp(-1 / (0.06 * SR)), np.exp(-1 / (0.5 * SR))
    out = np.zeros(N)
    acc = 0.0
    for k in range(0, N, 64):  # par blocs de 64 échantillons (assez fin, rapide)
        target = on[k]
        coef = att if target > acc else rel
        acc = target + (acc - target) * coef**64
        out[k : k + 64] = acc
    return out


def main():
    buf = np.zeros((N, 2))
    bars = int(np.ceil(TOTAL / BAR)) + 1
    for b in range(bars):
        c = b % 4
        t0 = b * BAR
        for m in CHORDS[c]:
            add(buf, pad_voice(mtof(m), BAR + 0.9), t0 - 0.45, gain=0.10, pan=0.0)
        add(buf, bass(mtof(ROOTS[c] - 12), BAR), t0, gain=0.22)
        for s, idx in enumerate(ARP):
            note = CHORDS[c][idx] + 12
            vel = 0.075 if s % 2 == 0 else 0.055
            add(buf, pluck(mtof(note)), t0 + s * BEAT / 2, gain=vel, pan=(-0.35 if s % 2 else 0.35))
    buf = reverb(buf)
    # douceur : léger passe-bas pour enlever le brillant
    b_lp, a_lp = signal.butter(2, 5200 / (SR / 2), "low")
    buf = signal.filtfilt(b_lp, a_lp, buf, axis=0)
    sans_voix = "--sans-voix" in sys.argv
    if not sans_voix:
        # creusement sous la voix (~ -9 dB)
        duck = 1 - 0.65 * voice_envelope()
        buf *= duck[:, None]
    # fondus d'entrée et de sortie
    t = t_axis(N)
    fade = np.minimum(1, t / 1.5) * np.clip((TOTAL - t) / 4.0, 0, 1)
    buf *= fade[:, None]
    buf *= 0.5 / (np.abs(buf).max() + 1e-9)
    out = ROOT / "assets" / "music" / ("exponentielle-fond-sans-voix.wav" if sans_voix else "exponentielle-fond.wav")
    out.parent.mkdir(parents=True, exist_ok=True)
    sf.write(out, buf.astype(np.float32), SR, subtype="PCM_16")
    print(out.relative_to(ROOT), f"{N / SR:.2f}s")


if __name__ == "__main__":
    main()
