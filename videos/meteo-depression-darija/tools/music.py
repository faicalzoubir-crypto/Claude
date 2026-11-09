#!/usr/bin/env python3
"""Brand music bed (brand/BRAND.md): 90 BPM, D minor, Dm – B♭ – F – C, two bars a chord,
soft pad + bass + gentle arpeggio. Deterministic, royalty-free, written to assets/music/bed.m4a at
-24 LUFS; index.html plays it at a further -10 dB (data-volume 0.32) so the voice stays clear.

  python3 tools/music.py     # after tools/assemble.py (reads the film length from cues.js)
"""
import json
import subprocess
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SR = 44100
raw = (ROOT / "cues.js").read_text()
C = json.loads(raw[raw.index("=") + 1: raw.rindex(";")])
TOTAL = C["duration"] + 0.5
N = int(TOTAL * SR)
t = np.arange(N) / SR
mtof = lambda m: 440.0 * 2 ** ((m - 69) / 12)

BEAT = 60 / 90
BAR = 4 * BEAT
CHORDS = [[50, 53, 57, 62], [46, 50, 53, 58], [41, 45, 48, 53], [48, 52, 55, 60]]  # Dm Bb F C
ROOTS = [38, 34, 41, 36]


def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):  # one-pole, fine at this length
        acc = (1 - a) * x[i] + a * acc
        y[i] = acc
    return y


def env(n, att, rel):
    e = np.ones(n)
    a, r = int(att * SR), int(rel * SR)
    e[:a] = np.linspace(0, 1, a)
    e[-r:] *= np.linspace(1, 0, r)
    return e


pad = np.zeros(N)
bass = np.zeros(N)
arp = np.zeros(N)
seg = 2 * BAR
k = 0
while k * seg < TOTAL:
    ci = k % 4
    a = int(k * seg * SR)
    b = min(N, int((k + 1) * seg * SR) + int(0.4 * SR))
    tt = t[a:b] - t[a]
    n = b - a
    e = env(n, 0.8, 1.2)
    for m in CHORDS[ci]:
        f = mtof(m)
        for det in (-0.12, 0.12):
            ph = 2 * np.pi * f * (1 + det / 100) * tt
            pad[a:b] += e * (np.sin(ph) + 0.25 * np.sin(2 * ph) + 0.1 * np.sin(3 * ph)) * 0.05
    fb = mtof(ROOTS[ci])
    for q in range(8):  # bass on quarters, soft
        qa = a + int(q * BEAT * SR)
        qb = min(N, qa + int(BEAT * 0.9 * SR))
        if qa >= N:
            break
        qt = t[qa:qb] - t[qa]
        bass[qa:qb] += np.exp(-qt * 3.0) * (np.sin(2 * np.pi * fb * qt) + 0.3 * np.sin(4 * np.pi * fb * qt)) * 0.22
    notes = CHORDS[ci] + [CHORDS[ci][1] + 12]
    for s in range(16):  # gentle arpeggio in eighths
        sa = a + int(s * BEAT / 2 * SR)
        sb = min(N, sa + int(0.6 * SR))
        if sa >= N:
            break
        st = t[sa:sb] - t[sa]
        f = mtof(notes[s % len(notes)] + 12)
        arp[sa:sb] += np.exp(-st * 6.5) * np.sin(2 * np.pi * f * st) * 0.06
    k += 1

pad = lowpass(pad, 1800.0)
mix = pad + bass + arp
fade = np.ones(N)
fade[: int(1.0 * SR)] = np.linspace(0, 1, int(1.0 * SR))
fade[-int(2.5 * SR):] = np.linspace(1, 0, int(2.5 * SR))
mix *= fade
mix /= np.max(np.abs(mix)) + 1e-9
mix *= 0.5

out = ROOT / "assets/music/bed.m4a"
tmp = ROOT / "assets/music/bed-raw.wav"
pcm = (np.stack([mix, mix], axis=1) * 32767).astype(np.int16)
with wave.open(str(tmp), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(tmp), "-af", "loudnorm=I=-24:TP=-3:LRA=11",
                "-ar", str(SR), "-c:a", "aac", "-b:a", "192k", str(out)], check=True)
tmp.unlink()
print(f"{out} ({TOTAL:.1f} s, -24 LUFS)")
