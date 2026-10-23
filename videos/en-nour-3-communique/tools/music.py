#!/usr/bin/env python3
"""Music bed and haptic sound for en-nour-3-communique (deterministic, royalty-free).

Music (assets/music/fond.m4a) keeps the brand's sound (brand/BRAND.md): 90 BPM, D minor,
soft pad + bass + gentle arpeggio, here with a light groove for the six steps. One bar = 2.667 s,
the film is 15 bars:

  bar  0-1   Dm  Dm     hook: pad + arpeggio; dips under the rewind (3.33-4.67)
  bar  2-9   B♭ B♭ F F C C Dm Dm   the six steps: + bass, kick, hats from the first tap (4.67)
  bar 10     B♭→C      « Envoyer »: hats build, bass out; near silence 28.95-29.33 under the riser
  bar 11     Dm        the impact (29.33): everything returns
  bar 12-14  B♭ F Dm   claim and end card: pad + arpeggio, resolve on Dm add9, fade out

Sound effects (assets/sfx/*.wav) come from the Pixabay files in assets/sfx/src (Pixabay Content
License, see CREDITS.md), pitched into takes so no repeated sound is identical, plus a synthesized
low thump under every tap (the haptic body, under 150 Hz) and a reversed whoosh for the rewind.

Cues are written to tools/sound.json (start, duration, volume) and become <audio> clips in
index.html through tools/build.mjs; each hit is placed so its peak lands one frame after the
picture.

  python3 tools/music.py && node tools/build.mjs
"""
import json
import subprocess
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SR = 44100
TOTAL = 40.0
N = int(TOTAL * SR)
rng = np.random.default_rng(20261023)
mtof = lambda m: 440.0 * 2 ** ((m - 69) / 12)
BEAT = 60 / 90
BAR = 4 * BEAT
FRAME = 1 / 30


def write_wav(path, left, right=None):
    right = left if right is None else right
    st = np.clip(np.stack([left, right], axis=1), -1, 1)
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((st * 32767).astype("<i2").tobytes())


def read_mono(path, rate=1.0):
    """Decode with ffmpeg; rate != 1 pitches and speeds the file (a different take)."""
    af = f"asetrate={int(SR * rate)},aresample={SR}" if rate != 1 else "anull"
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-af", af, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype="<i2").astype(np.float64) / 32768


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


def norm(x, peak=0.8):
    return x / (np.abs(x).max() + 1e-12) * peak


# ── music ──────────────────────────────────────────────────────────────────
CHORD = {"Dm": [62, 65, 69], "Bb": [58, 62, 65], "F": [60, 65, 69], "C": [60, 64, 67]}
ROOT_NOTE = {"Dm": 38, "Bb": 34, "F": 41, "C": 36}
BARS = ["Dm", "Dm", "Bb", "Bb", "F", "F", "C", "C", "Dm", "Dm", "Bb", "Dm", "Bb", "F", "Dm"]
GROOVE = (4.667, 26.667)
DROP = 29.333
GAP = (28.95, 29.333)
L = np.zeros(N)
R = np.zeros(N)


def place(sig, t0, gain=1.0, pan=0.0):
    i0 = int(round(t0 * SR))
    if i0 >= N or i0 + len(sig) <= 0:
        return
    if i0 < 0:
        sig, i0 = sig[-i0:], 0
    sig = sig[: N - i0]
    L[i0:i0 + len(sig)] += sig * gain * (1 - pan) / 2 * 2 ** 0.5
    R[i0:i0 + len(sig)] += sig * gain * (1 + pan) / 2 * 2 ** 0.5


def kick():
    n = int(0.32 * SR)
    t = np.arange(n) / SR
    f = 45 + 75 * np.exp(-t / 0.035)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.11) + 0.15 * tone(1800, 0.32, attack=0.0005, decay=0.004)


def hat(dur=0.05, decay=0.012):
    x = np.diff(rng.standard_normal(int(dur * SR) + 1))  # first difference = a cheap high-pass
    return x * np.exp(-np.arange(len(x)) / SR / decay)


def clap():
    x = np.diff(rng.standard_normal(int(0.18 * SR) + 1))
    t = np.arange(len(x)) / SR
    env = np.exp(-t / 0.05) * (1 + 0.6 * (np.sin(2 * np.pi * 90 * t) > 0))
    return x * env


KICK, CLAP = kick(), clap()
for b, name in enumerate(BARS):
    t = b * BAR
    chord, root = CHORD[name], ROOT_NOTE[name]
    # pad, one long chord a bar (B♭ → C in bar 10, the last bar held to the end)
    if b == 10:
        for half, nm in ((0, "Bb"), (1, "C")):
            for i, m in enumerate(CHORD[nm]):
                place(tone(mtof(m), 2 * BEAT + 0.5, harm=((1, 1.0), (2, 0.3), (3, 0.1)), attack=0.3, release=0.4, detune=0.003),
                      t + half * 2 * BEAT, 0.06, pan=(-0.4, 0.0, 0.4)[i])
    elif b == len(BARS) - 1:
        for i, m in enumerate((50, 57, 62, 65, 69, 64)):  # Dm add9, held
            place(tone(mtof(m), TOTAL - t, harm=((1, 1.0), (2, 0.2)), attack=0.6, release=2.0, detune=0.002), t, 0.05,
                  pan=(-0.5, -0.2, 0, 0.2, 0.5, 0.0)[i])
    else:
        for i, m in enumerate(chord):
            place(tone(mtof(m), BAR + 0.7, harm=((1, 1.0), (2, 0.3), (3, 0.1)), attack=0.8, release=0.9, detune=0.003), t, 0.065,
                  pan=(-0.4, 0.0, 0.4)[i])
    # arpeggio in eighths, all film long except the gap
    notes = [chord[0] + 12, chord[1] + 12, chord[2] + 12, chord[1] + 12]
    for e in range(8):
        te = t + e * BEAT / 2
        if GAP[0] <= te < GAP[1] or te >= TOTAL - 1.4:
            continue
        place(tone(mtof(notes[e % 4]), BEAT * 0.6, harm=((1, 1.0), (2, 0.25), (3, 0.06)), attack=0.004, decay=0.25), te,
              0.045, pan=0.3 if e % 2 else -0.3)
    for q in range(4):
        tq = t + q * BEAT
        groove = GROOVE[0] - 0.01 <= tq < GROOVE[1] or DROP <= tq < 33.333
        if groove:
            place(tone(mtof(root), BEAT * 0.45, harm=((1, 1.0), (2, 0.45), (3, 0.15)), attack=0.006, decay=0.2), tq, 0.2)
            place(tone(mtof(root), BEAT * 0.4, harm=((1, 1.0), (2, 0.45)), attack=0.006, decay=0.16), tq + BEAT / 2, 0.13)
            if q in (0, 2):
                place(KICK, tq, 0.5)
            if q in (1, 3) and tq >= 10.667:
                place(CLAP, tq, 0.05, pan=0.1)
            place(hat(), tq + BEAT / 2, 0.035, pan=0.25)
        elif tq < GROOVE[0] and q == 0:
            place(tone(mtof(root), BAR, harm=((1, 1.0), (2, 0.4)), attack=0.01, decay=0.9), tq, 0.2)
        elif DROP + 4 <= tq and q == 0:
            place(tone(mtof(root), BAR, harm=((1, 1.0), (2, 0.4)), attack=0.01, decay=0.9), tq, 0.16)
    if b == 10:  # build: sixteenth hats rising towards the gap
        for s16 in range(16):
            ts = t + s16 * BEAT / 4
            if ts < GAP[0]:
                place(hat(0.04, 0.01), ts, 0.015 + 0.05 * s16 / 15, pan=-0.2 if s16 % 2 else 0.2)
# the drop: a low hit with the chord
place(tone(mtof(26), 1.4, harm=((1, 1.0), (2, 0.5)), attack=0.004, decay=0.4), DROP, 0.35)
place(KICK, DROP, 0.7)

T = np.arange(N) / SR
gain = np.ones(N)
gain *= np.interp(T, [3.333, 3.5, 4.45, 4.667], [1, 0.3, 0.3, 1], left=1, right=1)  # dips under the rewind
gain *= np.interp(T, [GAP[0] - 0.05, GAP[0], GAP[1] - 0.01, GAP[1]], [1, 0, 0, 1], left=1, right=1)
gain *= np.clip((TOTAL - T) / 2.0, 0, 1) * np.clip(T / 0.02, 0, 1)
L *= gain
R *= gain
peak = max(np.abs(L).max(), np.abs(R).max())
L, R = L / peak * 0.5, R / peak * 0.5
write_wav(ROOT / "assets/music/fond.wav", L, R)
# bed at −17 LUFS, true peak ≤ −1.5 dBTP: the taps and pops sit 3-6 dB over it
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(ROOT / "assets/music/fond.wav"), "-af", "loudnorm=I=-17:TP=-1.5:LRA=11",
                "-ar", str(SR), "-c:a", "aac", "-b:a", "192k", str(ROOT / "assets/music/fond.m4a")], check=True)
(ROOT / "assets/music/fond.wav").unlink()

# ── sound effects ──────────────────────────────────────────────────────────
SRC = ROOT / "assets/sfx/src"
SFX = {}


def thump(f0=95, f1=42, dur=0.16, decay=0.06):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t / 0.02)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / decay) * np.minimum(1, t / 0.0015)


click = read_mono(SRC / "click.mp3")
on = int(np.argmax(np.abs(click) > 0.1 * np.abs(click).max()))
for i, rate in enumerate((1.0, 0.94, 1.07)):
    c = read_mono(SRC / "click.mp3", rate)[int(on / rate):]  # trim the silence before the transient
    body = thump(95 * rate, 42)
    x = np.zeros(max(len(c), len(body)))
    x[: len(c)] += norm(c, 0.75)
    x[: len(body)] += 0.55 * body
    SFX[f"tap-{i + 1}"] = norm(x, 0.85)
big = np.zeros(int(0.5 * SR))
c = read_mono(SRC / "click.mp3", 0.9)[int(on / 0.9):]
big[: len(c)] += norm(c, 0.8)
bt = thump(110, 36, 0.45, 0.14)
big[: len(bt)] += 0.9 * bt
SFX["tap-big"] = norm(big, 0.9)

pop = read_mono(SRC / "pop.mp3")
pon = int(np.argmax(np.abs(pop) > 0.1 * np.abs(pop).max()))
for i, semis in enumerate((0, 2, 3, 5, 7)):  # D minor-ish steps up: the payoff cascade climbs
    rate = 2 ** (semis / 12)
    SFX[f"pop-{i + 1}"] = norm(read_mono(SRC / "pop.mp3", rate)[int(pon / rate):], 0.8)

for i, rate in enumerate((1.0, 1.12, 0.88)):
    SFX[f"whoosh-{i + 1}"] = norm(read_mono(SRC / "whoosh.mp3", rate), 0.8)

wc = read_mono(SRC / "whoosh-cinematic.mp3")
seg = wc[int(1.6 * SR): int(3.1 * SR)][::-1]  # the swell, reversed: the tape winding back
seg = seg * np.minimum(1, np.arange(len(seg)) / (0.05 * SR)) * np.clip((len(seg) - np.arange(len(seg))) / (0.15 * SR), 0, 1)
SFX["rembobine"] = norm(seg, 0.8)

key = read_mono(SRC / "key-press.mp3")
kon = int(np.argmax(np.abs(key) > 0.1 * np.abs(key).max()))
SFX["key"] = norm(key[kon:], 0.7)
SFX["riser"] = norm(read_mono(SRC / "riser.mp3"), 0.85)
SFX["impact"] = norm(read_mono(SRC / "impact-bass-1.mp3"), 0.85)

meta = {}
for name, x in SFX.items():
    write_wav(ROOT / f"assets/sfx/{name}.wav", x)
    env = np.convolve(np.abs(x), np.ones(220) / 220, "same")
    meta[name] = {"duration": round(len(x) / SR, 3), "peak": round(float(np.argmax(env)) / SR, 3)}

# ── cues: the picture time of each action → its sound ─────────────────────
TAPS = [4.787, 6.653, 8.62, 9.523, 10.938, 13.337, 14.667, 16.0, 17.333, 18.659, 19.652, 20.66, 22.004, 24.033, 25.033, 25.454]
ROW_LANDS = [11.57, 15.3, 17.96, 21.29, 26.5]
PAY_LANDS = [31.1, 31.35, 31.6, 31.85, 32.1]
cues = []  # (picture time, sound, volume, align: "peak" | "start")
for i, t in enumerate(TAPS):
    cues.append((t, f"tap-{i % 3 + 1}", 0.9, "peak"))
cues += [(0.333, "tap-big", 0.75, "peak"), (29.333, "tap-big", 1.0, "peak"), (36.0, "tap-big", 0.35, "peak")]
cues += [(23.556, "key", 0.6, "peak"), (23.724, "key", 0.5, "peak")]
for i, t in enumerate(ROW_LANDS):
    cues.append((t, f"pop-{(0, 1, 2, 1, 0)[i] + 1}", 0.55, "peak"))
for i, t in enumerate(PAY_LANDS):
    cues.append((t, f"pop-{i + 1}", 0.6, "peak"))
cues += [
    (3.333, "rembobine", 0.7, "start"),
    (8.75, "whoosh-1", 0.5, "peak"),    # zoom through the +
    (18.0, "whoosh-2", 0.45, "peak"),   # whip onto the calendar
    (21.55, "whoosh-3", 0.4, "peak"),   # whip back to the title field
    (27.2, "whoosh-3", 0.25, "peak"),   # the whole filled form
    (33.6, "whoosh-1", 0.45, "peak"),   # the iPad leaves
]
sfx = []
for t, name, vol, align in sorted(cues):
    offset = meta[name]["peak"] if align == "peak" else 0.0
    start = t + (FRAME if align == "peak" else 0.0) - offset
    sfx.append({"path": f"assets/sfx/{name}.wav", "start": round(max(0.0, start), 3), "duration": meta[name]["duration"],
                "volume": vol, "cue": round(t, 3)})
# riser: its swell (2.7-3.6 s into the file) sits on the gap, its drop-off just after the impact
sfx.append({"path": "assets/sfx/riser.wav", "start": 25.8, "duration": 3.7, "volume": 0.35, "cue": 29.333})
sfx.append({"path": "assets/sfx/impact.wav", "start": 29.333, "duration": 2.0, "volume": 0.35, "cue": 29.333})
sfx.sort(key=lambda x: x["start"])
sound = {"music": {"path": "assets/music/fond.m4a", "duration": TOTAL, "volume": 0.8}, "sfx": sfx}
(ROOT / "tools/sound.json").write_text(json.dumps(sound, ensure_ascii=False, indent=1))
print(f"music {TOTAL:.1f}s · {len(SFX)} sounds · {len(sfx)} cues")
