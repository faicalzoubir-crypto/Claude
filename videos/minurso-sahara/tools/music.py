#!/usr/bin/env python3
"""Music bed and synthesized sound effects for minurso-sahara (deterministic, royalty-free).

The bed keeps the brand's sound (brand/BRAND.md): 90 BPM, D minor, Dm – B♭ – F – C, two bars per
chord, soft pad + bass + gentle arpeggio, darker here for a geopolitical piece:

  s1 hook          pad + bass, arpeggio enters on the zone reveal
  s2 facts         pad + bass in quarters
  s3 scenario 1    pad + bass + arpeggio (the march)
  s4 scenario 2    bass in eighths (tension) + arpeggio
  s5 scenario 3    pad + bass in eighths, low hit when the shield rises
  s6 recap         pad + arpeggio, resolves on Dm(add9), fades out

It is ducked under the narration (phrase windows from cues.js) when the voice exists.
Also writes sfx: whoosh-a/b/c, rumble (tanks), sand (the wall dissolving).

  python3 tools/music.py      # after tools/assemble.py (reads cues.js)
"""
import json
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SR = 44100
rng = np.random.default_rng(20261106)
mtof = lambda m: 440.0 * 2 ** ((m - 69) / 12)

raw = (ROOT / "cues.js").read_text()
C = json.loads(raw[raw.index("=") + 1 : raw.rindex(";")])
TOTAL = C["duration"]
N = int(TOTAL * SR)
T = np.arange(N) / SR
SC = {k: (v["start"], v["end"]) for k, v in C["scenes"].items()}
PH = C["phrases"]


def write_wav(path, left, right=None):
    right = left if right is None else right
    st = np.clip(np.stack([left, right], axis=1), -1, 1)
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((st * 32767).astype("<i2").tobytes())


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
CHORDS = [[62, 65, 69], [58, 62, 65], [60, 65, 69], [60, 64, 67]]  # Dm, B♭, F/C, C
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


def scene_at(t):
    for k, (a, b) in SC.items():
        if a <= t < b:
            return k
    return "s6"


ARP_FROM = PH["s1p2"]["start"]
bar, t = 0, 0.0
while t < TOTAL:
    ci = (bar // 2) % 4
    sc = scene_at(t + 0.01)
    chord, root = CHORDS[ci], ROOTS[ci]
    if bar % 2 == 0:  # pad, once per chord
        pg = 0.06 if sc in ("s2", "s5") else 0.07
        for i, m in enumerate(chord):
            place(tone(mtof(m - 12 if sc == "s5" and i == 2 else m), 2 * BAR + 0.6, harm=((1, 1.0), (2, 0.25), (3, 0.08)), attack=1.2, release=1.4, detune=0.003), t, pg, pan=(-0.4, 0.0, 0.4)[i])
    if sc in ("s1", "s2", "s3"):
        for b in range(4):
            place(tone(mtof(root), BEAT * 0.95, harm=((1, 1.0), (2, 0.35), (3, 0.12)), attack=0.01, decay=0.5), t + b * BEAT, 0.15)
    if sc in ("s4", "s5"):
        for b in range(8):
            place(tone(mtof(root), BEAT * 0.45, harm=((1, 1.0), (2, 0.4), (3, 0.15)), attack=0.005, decay=0.18), t + b * BEAT / 2, 0.15)
    if (sc == "s1" and t + BAR > ARP_FROM) or sc in ("s3", "s4", "s6"):
        notes = [chord[0] + 12, chord[1] + 12, chord[2] + 12, chord[1] + 12]
        for b in range(8):
            tb = t + b * BEAT / 2
            if sc == "s1" and tb < ARP_FROM:
                continue
            place(tone(mtof(notes[b % 4]), BEAT * 0.6, harm=((1, 1.0), (2, 0.2)), attack=0.004, decay=0.28), tb, 0.033, pan=0.3 if b % 2 else -0.3)
    bar += 1
    t += BAR

# low hit when the shield rises (scenario 3): the one impact of the film
shield_t = PH["s5p4"]["start"] + 0.5
place(tone(mtof(26), 1.4, harm=((1, 1.0), (2, 0.5), (3, 0.2)), attack=0.005, decay=0.4), shield_t, 0.32)
for m in (50, 53, 57):
    place(tone(mtof(m), 1.6, harm=((1, 1.0), (2, 0.3)), attack=0.02, decay=0.7), shield_t, 0.05)

# final resolution (Dm add9) under the question, then fade
end_t = PH["s6p2"]["start"]
for i, m in enumerate((50, 57, 62, 65, 69, 64)):
    place(tone(mtof(m), TOTAL - end_t, harm=((1, 1.0), (2, 0.2)), attack=0.8, release=2.5, detune=0.002), end_t, 0.05, pan=(-0.5, -0.2, 0, 0.2, 0.5, 0.0)[i])
fade = np.clip((TOTAL - T) / 2.5, 0, 1) * np.clip(T / 0.4, 0, 1)
L *= fade
R *= fade

# duck under the narration
if C.get("voiced"):
    env = np.zeros(N)
    for p in PH.values():
        a, b = int(p["start"] * SR), int(p["end"] * SR)
        env[a:b] = 1
    win = int(0.3 * SR)
    env = np.convolve(env, np.ones(win) / win, mode="same")
    duck = 1 - 0.5 * env
    L *= duck
    R *= duck
peak = max(np.abs(L).max(), np.abs(R).max())
L, R = L / peak * 0.6, R / peak * 0.6
write_wav(ROOT / "assets/music/bed.wav", L, R)
import subprocess

subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(ROOT / "assets/music/bed.wav"), "-c:a", "aac", "-b:a", "192k", str(ROOT / "assets/music/bed.m4a")], check=True)
(ROOT / "assets/music/bed.wav").unlink()


# ── sound effects ──────────────────────────────────────────────────────────
def noise(dur):
    return rng.standard_normal(int(dur * SR))


def lowpass(x, a):
    y = np.zeros_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc += a * (v - acc)
        y[i] = acc
    return y


def norm(x, p=0.8):
    return x / (np.abs(x).max() + 1e-9) * p


SFX = {}
for name, dur, a in (("whoosh-a", 0.7, 0.08), ("whoosh-b", 0.6, 0.12), ("whoosh-c", 0.85, 0.06)):
    n = int(dur * SR)
    t = np.arange(n) / SR
    SFX[name] = norm(lowpass(noise(dur), a) * np.sin(np.pi * t / dur) ** 2, 0.6)

# tanks: engine hum + track rumble with some mid content so it reads on a phone speaker
dur = 4.4
n = int(dur * SR)
t = np.arange(n) / SR
hum = sum(g * np.sin(2 * np.pi * f * t + 0.3 * np.sin(2 * np.pi * 3.1 * t)) for f, g in ((48, 1.0), (96, 0.6), (192, 0.35), (288, 0.18)))
grind = lowpass(noise(dur), 0.06) * (0.6 + 0.4 * np.sin(2 * np.pi * 11 * t) ** 2)
env = np.minimum(1, t / 0.6) * np.clip((dur - t) / 1.2, 0, 1)
SFX["rumble"] = norm((0.5 * hum / 2.1 + grind * 1.6) * env, 0.7)

# sand: grains of high noise in short bursts, a pour that thins out
dur = 2.6
n = int(dur * SR)
t = np.arange(n) / SR
hiss = noise(dur) - lowpass(noise(dur), 0.15)
grains = np.zeros(n)
for _ in range(900):
    c = int(rng.uniform(0, 1) ** 1.6 * n)
    w = int(rng.uniform(0.002, 0.008) * SR)
    grains[c : c + w] += rng.uniform(0.3, 1.0)
grains = np.convolve(grains, np.ones(64) / 64, mode="same")
SFX["sand"] = norm(hiss * (0.25 + grains) * np.minimum(1, t / 0.08) * np.clip((dur - t) / 1.6, 0, 1), 0.55)

for name, x in SFX.items():
    write_wav(ROOT / f"assets/sfx/{name}.wav", x)
print(f"music {TOTAL:.2f}s → assets/music/bed.m4a (ducked={bool(C.get('voiced'))}) · sfx: {', '.join(SFX)}")
