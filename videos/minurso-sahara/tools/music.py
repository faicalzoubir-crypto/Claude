#!/usr/bin/env python3
"""Music bed and synthesized sound effects for minurso-sahara (deterministic, royalty-free).

Two themes, chosen by script.json "music": "brand" (below) or "nouveau" (compose_nouveau: 104 BPM,
C harmonic minor Cm–A♭–Fm–G, oud-like plucked motif, 16th ostinato, low drums, march snare in s3),
made because the brand bed was already used in earlier videos.

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
BED = "bed-voix.m4a" if C.get("mode", "voice") == "voice" else "bed-musique.m4a"


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




def pluck(freq, dur, decay=0.35, bright=1.0):
    """Plucked string (oud-like): harmonics that die faster the higher they are."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for k, a in ((1, 1.0), (2, 0.55 * bright), (3, 0.35 * bright), (4, 0.22 * bright), (5, 0.12 * bright), (6, 0.07 * bright)):
        s += a * np.sin(2 * np.pi * freq * k * t) * np.exp(-t * k**0.8 / decay)
    return s * np.minimum(1, t / 0.003)


def strings(freq, dur, attack=0.7, release=0.9):
    """Soft string pad: detuned band-limited saw, slow bow."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for k in range(1, 8):
        for d in (-0.0035, 0.0035):
            s += np.sin(2 * np.pi * freq * k * (1 + d) * t + k) / k**1.4
    env = np.minimum(1, t / attack) * np.clip((dur - t) / release, 0, 1)
    return s * env


def drum(dur=0.6, f0=120, f1=48, decay=0.32):
    """Low taiko-like drum: falling pitch + a short skin noise."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t / 0.05)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / decay)
    skin = rng.standard_normal(n) * np.exp(-t / 0.012) * 0.45
    return body + skin


def snare(dur=0.12, gain=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = rng.standard_normal(n)
    x = x - np.convolve(x, np.ones(12) / 12, mode="same")  # drop the lows
    return gain * x * np.exp(-t / 0.035) + 0.3 * np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.03)


def echo(x, delay=0.27, fb=0.32, taps=3):
    y = x.copy()
    d = int(delay * SR)
    for k in range(1, taps + 1):
        y[k * d:] += x[: len(x) - k * d] * fb**k
    return y


# C harmonic minor (C D E♭ F G A♭ B): Cm – A♭ – Fm – G, one bar each, 104 BPM
NBEAT = 60 / 104
NBAR = 4 * NBEAT
NCHORDS = [[60, 63, 67], [56, 60, 63], [53, 56, 60], [55, 59, 62]]  # Cm, A♭, Fm, G
NROOTS = [36, 32, 29, 31]
# the oud motif (two bars), in C harmonic minor: G A♭ B C | B A♭ G — ; and its answer E♭ D C B | C — — —
MOTIF_A = [(0, 67, 0.5), (0.5, 68, 0.5), (1, 71, 0.5), (1.5, 72, 1.5), (4, 71, 0.5), (4.5, 68, 0.5), (5, 67, 2.0)]
MOTIF_B = [(0, 75, 0.5), (0.5, 74, 0.5), (1, 72, 0.5), (1.5, 71, 1.0), (4, 72, 3.0)]


def compose_nouveau():
    plk = np.zeros(N)  # plucks go through the echo
    bar, t = 0, 0.0
    motif_bars = set()
    while t < TOTAL:
        ci = bar % 4
        sc = scene_at(t + 0.01)
        chord, root = NCHORDS[ci], NROOTS[ci]
        # strings: every scene, quieter under the facts
        sg = {"s1": 0.07, "s2": 0.06, "s3": 0.065, "s4": 0.07, "s5": 0.075, "s6": 0.07}[sc]
        for i, m in enumerate(chord):
            place(strings(mtof(m), NBAR + 0.9), t, sg, pan=(-0.5, 0.0, 0.5)[i])
        # ostinato: 16th-note plucks on the chord tones
        if sc in ("s1", "s3", "s4", "s5"):
            pat = [chord[0], chord[2], chord[1], chord[2]]
            og = {"s1": 0.075, "s3": 0.07, "s4": 0.085, "s5": 0.06}[sc]
            for k in range(16):
                tb = t + k * NBEAT / 4
                i0 = int(tb * SR)
                note = pluck(mtof(pat[k % 4] + (12 if k % 8 >= 4 and sc == "s4" else 0)), 0.3, decay=0.12, bright=0.7)
                note *= og * (1.0 if k % 4 == 0 else 0.7)
                if i0 < N:
                    plk[i0 : i0 + len(note)] += note[: N - i0]
        # bass: eighth-note pulse (s2 quarter notes, s5 a held drone)
        if sc == "s5":
            place(tone(mtof(root), NBAR + 0.2, harm=((1, 0.6), (2, 0.6), (3, 0.3), (4, 0.15)), attack=0.3, release=0.3), t, 0.09)
        else:
            step = NBEAT if sc in ("s2", "s6") else NBEAT / 2
            for k in range(int(round(NBAR / step))):
                place(tone(mtof(root), step * 0.9, harm=((1, 0.6), (2, 0.6), (3, 0.35), (4, 0.15)), attack=0.005, decay=0.22), t + k * step, 0.085)
        # clock-like shaker under the facts
        if sc == "s2":
            for k in range(16):
                n_ = int(0.03 * SR)
                place(rng.standard_normal(n_) * np.exp(-np.arange(n_) / SR / 0.008), t + k * NBEAT / 4, 0.025 if k % 2 else 0.04, pan=0.25)
        # march: a soft snare on the eighths, a roll into each bar
        if sc == "s3":
            for k in range(8):
                place(snare(gain=0.9 if k % 2 == 0 else 0.55), t + k * NBEAT / 2, 0.05, pan=-0.15)
            for k in range(4):
                place(snare(0.08, 0.5), t + NBAR - NBEAT / 2 + k * NBEAT / 8, 0.035, pan=-0.15)
        # drums: the tanks (s4) drive on 1, 2&, 3; the march (s3) on 1 and 3; the hook opens with one
        if sc == "s4":
            for b_ in (0, 1.5, 2, 3.5):
                place(drum(f0=140, f1=62), t + b_ * NBEAT, 0.24 if b_ in (0, 2) else 0.16)
        elif sc == "s3":
            for b_ in (0, 2):
                place(drum(f0=120, f1=58), t + b_ * NBEAT, 0.16)
        elif sc == "s1" and bar < 2:
            place(drum(1.2, f0=130, f1=55, decay=0.6), t, 0.28)
        # the oud motif: hook, march and recap, on the first bar of a two-bar pair
        if sc in ("s1", "s3", "s6") and bar % 2 == 0 and bar not in motif_bars:
            motif = MOTIF_B if sc == "s6" or (bar // 2) % 2 else MOTIF_A
            for off, m, ln in motif:
                note = pluck(mtof(m), ln * NBEAT + 0.4, decay=0.45, bright=1.0) * 0.17
                i0 = int((t + off * NBEAT) * SR)
                if i0 < N:
                    plk[i0 : i0 + len(note)] += note[: N - i0]
            motif_bars.update({bar, bar + 1})
        bar += 1
        t += NBAR
    wet = echo(plk)
    L[:] += wet * 0.9
    R[:] += np.concatenate([np.zeros(int(0.012 * SR)), wet])[:N] * 0.9  # a little width

    # swell into the shield, then the one low impact of the film
    shield_t = PH["s5p4"]["start"] + 0.5
    n_ = int(1.4 * SR)
    sw = rng.standard_normal(n_)
    sw = np.convolve(sw, np.ones(20) / 20, mode="same") * np.linspace(0, 1, n_) ** 2.5
    place(sw, shield_t - 1.4, 0.05)
    place(drum(1.8, f0=110, f1=45, decay=0.7), shield_t, 0.4)
    for m in (48, 55, 60, 63):
        place(strings(mtof(m), 2.2, attack=0.02, release=1.6), shield_t, 0.05)

    # end: Cm(add9) held under the question, the motif's answer over it
    end_t = PH["s6p2"]["start"]
    for i, m in enumerate((36, 48, 55, 60, 62, 63, 67)):
        place(strings(mtof(m), TOTAL - end_t + 0.5, attack=1.0, release=2.4), end_t, 0.035, pan=(-0.6, -0.3, 0, 0.3, 0.6, -0.2, 0.2)[i])

THEME = json.loads((ROOT / "script.json").read_text()).get("music", "brand")
if THEME == "brand":
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
else:
    compose_nouveau()

fade = np.clip((TOTAL - T) / 2.5, 0, 1) * np.clip(T / 0.4, 0, 1)
L *= fade
R *= fade

# duck under the narration
if C.get("voiced") and C.get("mode", "voice") == "voice":
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

subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(ROOT / "assets/music/bed.wav"), "-c:a", "aac", "-b:a", "192k", str(ROOT / f"assets/music/{BED}")], check=True)
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
print(f"music [{THEME}] {TOTAL:.2f}s → assets/music/{BED} (mode={C.get('mode', 'voice')}) · sfx: {', '.join(SFX)}")
