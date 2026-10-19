#!/usr/bin/env python3
"""Music bed and sound effects for compteur-roue-radar (deterministic, royalty-free).

Music (assets/music/fond.m4a) keeps the brand's sound (brand/BRAND.md, from the Vespa slide film):
90 BPM, D minor, Dm – B♭ – F – C, two bars per chord; soft pad + bass + gentle
arpeggio. It is ducked under the narration here (voice clips read from
audio_meta.json at their frame starts), so the root mix only sets one volume.

  0–11.2 s    question + title: pad + arpeggio
  11.2–63.5   mechanism, calculation, comparison: + bass, light hats in the transmission
  63.5–69.3   Karim: bass in eighths (tension), stab on the radar
  69.3–91.0   the stop: pad only, very soft (dialogue)
  91.0–102.1  table: bass + arpeggio return
  102.1–end   tips + closing line: pad + arpeggio, resolve on Dm, fade out

Sound effects are written to assets/sfx/ and listed in audio_meta.json as host audio.

  python3 tools/music.py              # version with narration (bed ducked under the voice)
  python3 tools/music.py --sans-voix  # no narration: no ducking, gentle arpeggio under the dialogue frame
"""
import json
import sys
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SR = 44100
rng = np.random.default_rng(20261019)
mtof = lambda m: 440.0 * 2 ** ((m - 69) / 12)

meta = json.loads((ROOT / "audio_meta.json").read_text())
cues = json.loads((ROOT / "voice_cues.json").read_text())
durs = [cues[str(i)]["duration_s"] for i in range(1, 11)]
starts = np.concatenate([[0.0], np.cumsum(durs)[:-1]])
TOTAL = float(sum(durs))
N = int(TOTAL * SR)
T = np.arange(N) / SR
SANS_VOIX = "--sans-voix" in sys.argv
F = {i + 1: float(starts[i]) for i in range(10)}  # frame starts


def write_wav(path, left, right=None):
    right = left if right is None else right
    st = np.stack([left, right], axis=1)
    st = np.clip(st, -1, 1)
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


# ── music ──────────────────────────────────────────────────────────────────
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
    if t < F[10]:
        return "table"
    return "outro"


bar = 0
t = 0.0
while t < TOTAL:
    ci = (bar // 2) % 4
    sec = section(t)
    chord, root = CHORDS[ci], ROOTS[ci]
    if bar % 2 == 0:  # pad, once per chord
        pg = 0.05 if sec == "dialogue" else 0.07
        for i, m in enumerate(chord):
            place(tone(mtof(m), 2 * BAR + 0.6, harm=((1, 1.0), (2, 0.25), (3, 0.08)), attack=1.2, release=1.4, detune=0.003), t, pg, pan=(-0.4, 0.0, 0.4)[i])
    if sec in ("body", "table"):
        for b in range(4):
            place(tone(mtof(root), BEAT * 0.95, harm=((1, 1.0), (2, 0.35)), attack=0.01, decay=0.5), t + b * BEAT, 0.16)
    if sec == "tension":
        for b in range(8):
            place(tone(mtof(root), BEAT * 0.45, harm=((1, 1.0), (2, 0.4)), attack=0.005, decay=0.18), t + b * BEAT / 2, 0.15)
    if sec in ("intro", "body", "table", "outro") or (SANS_VOIX and sec == "dialogue"):
        notes = [chord[0] + 12, chord[1] + 12, chord[2] + 12, chord[1] + 12]
        for b in range(8):
            place(tone(mtof(notes[b % 4]), BEAT * 0.6, harm=((1, 1.0), (2, 0.2)), attack=0.004, decay=0.28), t + b * BEAT / 2, 0.035, pan=0.3 if b % 2 else -0.3)
    if sec == "body" and F[3] <= t < F[4]:
        for b in range(8):
            n = int(0.04 * SR)
            hat = rng.standard_normal(n) * np.exp(-np.arange(n) / SR / 0.012)
            place(hat, t + b * BEAT / 2 + BEAT / 4, 0.02, pan=0.2)
    bar += 1
    t += BAR

# radar stab: low hit + minor chord swell
radar_t = F[7] + 4.45
place(tone(mtof(26), 1.2, harm=((1, 1.0), (2, 0.5)), attack=0.005, decay=0.35), radar_t, 0.35)
for m in (50, 53, 57):
    place(tone(mtof(m), 1.4, harm=((1, 1.0), (2, 0.3)), attack=0.02, decay=0.6), radar_t, 0.06)

# final resolution chord (Dm add9) and fade-out
end_t = F[10] + 8.7
for i, m in enumerate((50, 57, 62, 65, 69, 64)):
    place(tone(mtof(m), TOTAL - end_t, harm=((1, 1.0), (2, 0.2)), attack=0.8, release=2.5, detune=0.002), end_t, 0.05, pan=(-0.5, -0.2, 0, 0.2, 0.5, 0.0)[i])
fade = np.clip((TOTAL - T) / 3.0, 0, 1) * np.clip(T / 1.0, 0, 1)
L *= fade
R *= fade

# duck under the narration: voice envelope → gain 1 → 0.45 (not in the version without voice)
voice = np.zeros(N)
for v in ([] if SANS_VOIX else meta["voices"]):
    with wave.open(str(ROOT / v["path"]), "rb") as w:
        sr, x = w.getframerate(), np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float64) / 32768
    x = np.interp(np.arange(int(len(x) * SR / sr)) * sr / SR, np.arange(len(x)), x)
    i0 = int(F[v["frame"]] * SR)
    seg = np.abs(x[: N - i0])
    voice[i0 : i0 + len(seg)] = np.maximum(voice[i0 : i0 + len(seg)], seg)
win = int(0.25 * SR)
env = np.convolve(voice, np.ones(win) / win, mode="same")
env = np.clip(env / 0.03, 0, 1)
duck = 1 - 0.55 * env
L *= duck
R *= duck
peak = max(np.abs(L).max(), np.abs(R).max())
L, R = L / peak * 0.5, R / peak * 0.5
write_wav(ROOT / "assets/music/fond.wav", L, R)
import subprocess
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(ROOT / "assets/music/fond.wav"), "-c:a", "aac", "-b:a", "192k", str(ROOT / "assets/music/fond.m4a")], check=True)
(ROOT / "assets/music/fond.wav").unlink()

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
n = int(0.7 * SR); t = np.arange(n) / SR
SFX["whoosh-soft"] = norm(lowpass(noise(0.7), 0.08) * np.sin(np.pi * t / 0.7) ** 2, 0.6)
SFX["tick"] = norm(tone(2200, 0.06, attack=0.001, decay=0.012) + 0.5 * tone(3300, 0.06, attack=0.001, decay=0.008), 0.7)
SFX["click"] = norm(tone(1400, 0.08, harm=((1, 1), (2, 0.4)), attack=0.001, decay=0.02), 0.6)
SFX["blip"] = norm(tone(1500, 0.09, attack=0.003, decay=0.03), 0.5)
SFX["chime"] = norm(sum(tone(mtof(m), 1.6, harm=((1, 1), (2.76, 0.3), (5.4, 0.1)), attack=0.003, decay=0.55) for m in (74, 77, 81)), 0.7)
SFX["ding"] = norm(tone(mtof(81), 1.1, harm=((1, 1), (2.76, 0.35)), attack=0.002, decay=0.4), 0.7)
n = int(2.4 * SR); t = np.arange(n) / SR
SFX["roll"] = norm(lowpass(noise(2.4), 0.02) * (1 + 0.3 * np.sin(2 * np.pi * 9 * t)) * np.sin(np.pi * t / 2.4), 0.5)
beep = tone(1800, 0.12, attack=0.002, release=0.01)
SFX["radar-beep"] = norm(np.concatenate([beep, np.zeros(int(0.07 * SR)), beep]), 0.6)
n = int(0.9 * SR); t = np.arange(n) / SR
f = np.where(t < 0.45, 600 + 900 * (t / 0.45), 1500 - 900 * ((t - 0.45) / 0.45))
ph = 2 * np.pi * np.cumsum(f) / SR
SFX["siren-chirp"] = norm((np.sin(ph) + 0.3 * np.sin(2 * ph)) * np.minimum(1, t / 0.02) * np.minimum(1, (0.9 - t) / 0.1), 0.55)

for name, x in SFX.items():
    write_wav(ROOT / f"assets/sfx/{name}.wav", x)

# Cues (frame, sound, offset in the frame, volume) — on the words they punctuate.
CUES = [
    (1, "whoosh-soft", 0.0, 0.35),
    (2, "tick", 1.25, 0.4), (2, "tick", 2.4, 0.2), (2, "tick", 3.0, 0.2), (2, "tick", 3.6, 0.2),
    (3, "click", 0.85, 0.35), (3, "click", 3.45, 0.35), (3, "click", 6.6, 0.35), (3, "click", 10.2, 0.35), (3, "click", 14.9, 0.35), (3, "click", 16.85, 0.35), (3, "whoosh-soft", 18.7, 0.3),
    (4, "blip", 1.95, 0.3), (4, "blip", 2.45, 0.3), (4, "blip", 2.95, 0.3), (4, "blip", 3.45, 0.3), (4, "chime", 5.35, 0.3),
    (5, "tick", 5.2, 0.35), (5, "tick", 8.05, 0.35),
    (6, "roll", 0.2, 0.3), (6, "ding", 4.05, 0.35),
    (7, "tick", 3.3, 0.4), (7, "radar-beep", 4.5, 0.45),
    (8, "siren-chirp", 0.0, 0.35),
    (9, "tick", 2.15, 0.3), (9, "tick", 4.55, 0.3), (9, "tick", 7.1, 0.3),
    (10, "chime", 8.65, 0.3),
]
meta["bgm"] = {"path": "assets/music/fond.m4a", "volume": 0.5, "source": "host"}
meta["bgm_pending"] = False
meta["sfx"] = [
    {"frame": fr, "file": f"assets/sfx/{name}.wav", "offset_s": off, "duration_s": round(len(SFX[name]) / SR, 3), "volume": vol, "source": "host"}
    for fr, name, off, vol in CUES
]
(ROOT / "audio_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
print(f"music {TOTAL:.2f}s → assets/music/fond.m4a · {len(SFX)} sounds · {len(CUES)} cues")
