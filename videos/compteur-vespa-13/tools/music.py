#!/usr/bin/env python3
"""Musique de fond de compteur-vespa-13 (déterministe, libre de droits).

Identité sonore de la marque (brand/BRAND.md, film Vespa) : 90 BPM, ré mineur,
Dm – B♭ – F – C, deux mesures par accord ; nappe + basse + arpège discret.
Pas de voix off : rien n'est creusé, l'arpège reste sous le dialogue.
Les sections suivent les débuts des scènes (tools/plan.json, écrit par
tools/construire.py) :

  01–02  question, titre : nappe + arpège
  03–06  transmission, capteur, calcul, comparaison : + basse (charleston léger pendant la transmission)
  07     serein : basse en croches (tension), impact sur le radar
  08     contrôle : nappe douce + arpège
  09–10  tableau, carburant : basse + arpège
  11     conclusion : nappe + arpège, résolution sur Dm, fondu

  python3 tools/music.py
"""
import json
import subprocess
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SR = 44100
rng = np.random.default_rng(20261101)
mtof = lambda m: 440.0 * 2 ** ((m - 69) / 12)

plan = json.loads((ROOT / "tools/plan.json").read_text())
TOTAL = float(plan["total"])
F = {int(s["id"][:2]): float(s["debut"]) for s in plan["scenes"]}
N = int(TOTAL * SR)
T = np.arange(N) / SR


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
    env *= np.clip((dur - t) / max(release, 1e-4), 0, 1)
    return s * env


BEAT = 60 / 90
BAR = 4 * BEAT
CHORDS = [[62, 65, 69], [58, 62, 65], [60, 65, 69], [60, 64, 67]]  # Dm, B♭, F (F/C), C
ROOTS = [38, 34, 41, 36]
L = np.zeros(N)
R = np.zeros(N)


def place(sig, t0, gain=1.0, pan=0.0):
    i0 = int(t0 * SR)
    if i0 >= N or i0 + len(sig) <= 0:
        return
    if i0 < 0:
        sig, i0 = sig[-i0:], 0
    sig = sig[: N - i0]
    L[i0 : i0 + len(sig)] += sig * gain * (1 - pan) / 2 * 2**0.5
    R[i0 : i0 + len(sig)] += sig * gain * (1 + pan) / 2 * 2**0.5


def section(t):
    if t < F[3]:
        return "intro"
    if t < F[7]:
        return "body"
    if t < F[8]:
        return "tension"
    if t < F[9]:
        return "dialogue"
    if t < F[11]:
        return "table"
    return "outro"


bar, t = 0, 0.0
while t < TOTAL:
    ci = (bar // 2) % 4
    sec = section(t)
    chord, root = CHORDS[ci], ROOTS[ci]
    if bar % 2 == 0:  # nappe, une fois par accord
        pg = 0.05 if sec == "dialogue" else 0.07
        for i, m in enumerate(chord):
            place(tone(mtof(m), 2 * BAR + 0.6, harm=((1, 1.0), (2, 0.25), (3, 0.08)), attack=1.2, release=1.4, detune=0.003), t, pg, pan=(-0.4, 0.0, 0.4)[i])
    if sec in ("body", "table"):
        for b in range(4):
            place(tone(mtof(root), BEAT * 0.95, harm=((1, 1.0), (2, 0.35)), attack=0.01, decay=0.5), t + b * BEAT, 0.16)
    if sec == "tension":
        for b in range(8):
            place(tone(mtof(root), BEAT * 0.45, harm=((1, 1.0), (2, 0.4)), attack=0.005, decay=0.18), t + b * BEAT / 2, 0.15)
    if sec in ("intro", "body", "table", "outro", "dialogue"):
        notes = [chord[0] + 12, chord[1] + 12, chord[2] + 12, chord[1] + 12]
        for b in range(8):
            place(tone(mtof(notes[b % 4]), BEAT * 0.6, harm=((1, 1.0), (2, 0.2)), attack=0.004, decay=0.28), t + b * BEAT / 2,
                  0.03 if sec == "dialogue" else 0.035, pan=0.3 if b % 2 else -0.3)
    if sec == "body" and F[3] <= t < F[4]:
        for b in range(8):
            n = int(0.04 * SR)
            hat = rng.standard_normal(n) * np.exp(-np.arange(n) / SR / 0.012)
            place(hat, t + b * BEAT / 2 + BEAT / 4, 0.02, pan=0.2)
    bar += 1
    t += BAR

# impact sur le radar : grave + accord mineur qui gonfle
radar_t = F[7] + 4.8
place(tone(mtof(26), 1.2, harm=((1, 1.0), (2, 0.5)), attack=0.005, decay=0.35), radar_t, 0.35)
for m in (50, 53, 57):
    place(tone(mtof(m), 1.4, harm=((1, 1.0), (2, 0.3)), attack=0.02, decay=0.6), radar_t, 0.06)

# résolution finale (Dm add9) sur la phrase de conclusion, puis fondu
end_t = F[11] + 7.0
for i, m in enumerate((50, 57, 62, 65, 69, 64)):
    place(tone(mtof(m), TOTAL - end_t, harm=((1, 1.0), (2, 0.2)), attack=0.8, release=2.5, detune=0.002), end_t, 0.05, pan=(-0.5, -0.2, 0, 0.2, 0.5, 0.0)[i])
fade = np.clip((TOTAL - T) / 3.0, 0, 1) * np.clip(T / 1.0, 0, 1)
L *= fade
R *= fade
peak = max(np.abs(L).max(), np.abs(R).max())
L, R = L / peak * 0.5, R / peak * 0.5

wav = ROOT / "assets/music/fond.wav"
wav.parent.mkdir(parents=True, exist_ok=True)
with wave.open(str(wav), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((np.clip(np.stack([L, R], axis=1), -1, 1) * 32767).astype("<i2").tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wav), "-c:a", "aac", "-b:a", "192k", str(ROOT / "assets/music/fond.m4a")], check=True)
wav.unlink()
print(f"musique {TOTAL:.1f} s → assets/music/fond.m4a")
