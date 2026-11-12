#!/usr/bin/env python3
"""Brand music bed for coupure-casablanca (brand/BRAND.md sound), deterministic and royalty-free.

90 BPM, D minor, Dm – B♭ – F – C, two bars per chord; soft pad + bass + gentle arpeggio, kept low
under the voice. Per scene:
  s1 what happened   pad + bass in quarters; the arpeggio enters with the storm (s1c)
  s2 the map         pad + sparse arpeggio (the zones carry the rhythm with their clicks)
  s3 substations     pad + bass + arpeggio
  s4 hypothesis      bass in eighths (tension); one low hit when the wires touch (the film's impact)
  s5 prevention      pad + arpeggio, brighter (no bass pulse)
  s6 open question   pad alone, then a Dm(add9) that rings into the sources card and fades
Ducked by 50 % under every phrase (data/cues.json).

  python3 tools/music.py     # after tools/recording.py
"""
import json, wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SR = 44100
C = json.loads((ROOT / "data/cues.json").read_text())
TOTAL = C["total"]
N = int(TOTAL * SR)
SC = {k: (v["start"], v["start"] + v["duration"]) for k, v in C["scenes"].items()}
SC["end"] = (C["end"]["start"], TOTAL)
PH = [(v["start"] + a, v["start"] + b) for v in C["scenes"].values() for a, b in v["phrases"].values()]
mtof = lambda m: 440.0 * 2 ** ((m - 69) / 12)
L = np.zeros(N); R = np.zeros(N)


def tone(freq, dur, harm=((1, 1.0),), attack=0.01, decay=None, release=0.05, detune=0.0):
    n = int(dur * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for k, a in harm:
        for d in ((-detune, detune) if detune else (0,)):
            s += a * np.sin(2 * np.pi * freq * k * (1 + d) * t)
    env = np.minimum(1, t / max(attack, 1e-4))
    if decay:
        env *= np.exp(-t / decay)
    env *= np.clip((dur - t) / max(release, 1e-4), 0, 1)
    return s * env


def place(sig, t0, gain=1.0, pan=0.0):
    i0 = int(t0 * SR)
    if i0 >= N:
        return
    sig = sig[: N - i0]
    L[i0:i0 + len(sig)] += sig * gain * (1 - pan) / 2 * 2 ** 0.5
    R[i0:i0 + len(sig)] += sig * gain * (1 + pan) / 2 * 2 ** 0.5


def scene_at(t):
    for k, (a, b) in SC.items():
        if a <= t < b:
            return k
    return "end"


BEAT = 60 / 90; BAR = 4 * BEAT
CHORDS = [[62, 65, 69], [58, 62, 65], [60, 65, 69], [60, 64, 67]]   # Dm, B♭, F/C, C
ROOTS = [38, 34, 41, 36]
s1 = C["scenes"]["s1"]
ARP_FROM = s1["start"] + s1["phrases"]["s1c"][0]
bar, t = 0, 0.0
while t < SC["s6"][1] - 0.5:
    ci = (bar // 2) % 4
    sc = scene_at(t + 0.01)
    chord, root = CHORDS[ci], ROOTS[ci]
    if bar % 2 == 0:
        pg = 0.075 if sc in ("s5", "s6") else 0.065
        for i, m in enumerate(chord):
            place(tone(mtof(m), 2 * BAR + 0.6, harm=((1, 1.0), (2, 0.25), (3, 0.08)), attack=1.2, release=1.4, detune=0.003), t, pg, pan=(-0.4, 0.0, 0.4)[i])
    if sc in ("s1", "s3"):
        for b in range(4):
            place(tone(mtof(root), BEAT * 0.95, harm=((1, 1.0), (2, 0.35), (3, 0.12)), attack=0.01, decay=0.5), t + b * BEAT, 0.14)
    if sc == "s4":
        for b in range(8):
            place(tone(mtof(root), BEAT * 0.45, harm=((1, 1.0), (2, 0.4), (3, 0.15)), attack=0.005, decay=0.18), t + b * BEAT / 2, 0.14)
    if (sc == "s1" and t + BAR > ARP_FROM) or sc in ("s2", "s3", "s5"):
        notes = [chord[0] + 12, chord[1] + 12, chord[2] + 12, chord[1] + 12]
        step = 2 if sc == "s2" else 1                     # sparse on the map
        for b in range(0, 8, step):
            tb = t + b * BEAT / 2
            if sc == "s1" and tb < ARP_FROM:
                continue
            place(tone(mtof(notes[b % 4] + (12 if sc == "s5" and b % 4 == 2 else 0)), BEAT * 0.6, harm=((1, 1.0), (2, 0.2)), attack=0.004, decay=0.28), tb, 0.032, pan=0.3 if b % 2 else -0.3)
    bar += 1
    t += BAR

# the one impact: the two wires touch (scene 4)
s4 = C["scenes"]["s4"]
hit = s4["start"] + s4.get("marks", {}).get("touch", s4["phrases"]["s4b"][0])
place(tone(mtof(26), 1.4, harm=((1, 1.0), (2, 0.5), (3, 0.2)), attack=0.005, decay=0.4), hit, 0.3)

# resolution under «ننتظرو تقرير رسمي», ringing into the sources card
s6 = C["scenes"]["s6"]
end_t = s6["start"] + s6["phrases"]["s6g"][0]
for i, m in enumerate((50, 57, 62, 65, 69, 64)):
    place(tone(mtof(m), TOTAL - end_t, harm=((1, 1.0), (2, 0.2)), attack=0.8, release=2.5, detune=0.002), end_t, 0.05, pan=(-0.5, -0.2, 0, 0.2, 0.5, 0.0)[i])

T = np.arange(N) / SR
fade = np.clip((TOTAL - T) / 2.5, 0, 1) * np.clip(T / 0.4, 0, 1)
env = np.zeros(N)
for a, b in PH:
    env[int(a * SR):int(b * SR)] = 1
win = int(0.3 * SR)
env = np.convolve(env, np.ones(win) / win, mode="same")
duck = 1 - 0.5 * env if C.get("mode") != "subtitles" else 1.0   # no voice: no ducking
L *= fade * duck; R *= fade * duck
peak = max(np.abs(L).max(), np.abs(R).max())
L, R = L / peak * 0.6, R / peak * 0.6
out = ROOT / "assets/music/bed.wav"
out.parent.mkdir(parents=True, exist_ok=True)
with wave.open(str(out), "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(np.stack([L, R], 1), -1, 1) * 32767).astype("<i2").tobytes())
print(f"music {TOTAL:.2f}s -> {out.relative_to(ROOT)}")
