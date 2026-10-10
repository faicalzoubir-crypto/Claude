"""EN-NOUR 3 — "Le chemin de lumière" music bed, synthesized (deterministic).

D major, 100 BPM (bar = 2.4 s), bars aligned to the film:
  bars 0-1   (0.0-4.8 s)   intro: suspended IV-V pad + glockenspiel sparkle, riser
  bars 2-9   (4.8-24.0 s)  groove A: kalimba arpeggio, bass, soft kick, shaker
  bars 10-17 (24.0-43.2 s) groove B: + snaps on 2 & 4, counter-melody
  bars 18-21 (43.2-52.8 s) groove A' + build, riser into the call to action
  bars 22-23 (52.8-57.6 s) lift: IV-V with bell melody
  bar 24     (57.6 s-end)  resolution on D, ring out
The bed is carved under the voiceover (dynamic 3-band dip driven by the VO envelope).
Usage: python3 tools/music.py
"""
import json
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal

ROOT = Path(__file__).resolve().parent.parent
SR = 44100
BPM = 100
BEAT = 60 / BPM
BAR = 4 * BEAT
TIMING = json.loads(
    subprocess.check_output(
        ["node", "-e", 'import("./scene/timing.js").then(m=>console.log(JSON.stringify({L:m.L,D:m.VO_DUR,T:m.TOTAL})))'],
        cwd=ROOT,
    )
)
TOTAL = TIMING["T"]
N = int((TOTAL + 0.05) * SR)
rng = np.random.default_rng(1977)

mtof = lambda m: 440.0 * 2 ** ((m - 69) / 12)


def buf():
    return np.zeros((N, 2))


def add(dst, x, t0, gain=1.0, pan=0.0):
    i0 = int(t0 * SR)
    if i0 >= N:
        return
    x = x[: N - i0]
    l = np.cos((pan + 1) * np.pi / 4)
    r = np.sin((pan + 1) * np.pi / 4)
    dst[i0 : i0 + len(x), 0] += x * gain * l
    dst[i0 : i0 + len(x), 1] += x * gain * r


def tt(dur):
    return np.arange(int(dur * SR)) / SR


def attack(t, a=0.004):
    return np.clip(t / a, 0, 1)


# ── instruments ──────────────────────────────────────────────────────────────
def kalimba(f, dur=1.4, decay=4.5):
    t = tt(dur)
    y = np.sin(2 * np.pi * f * t) + 0.32 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 10)
    y += 0.1 * np.sin(2 * np.pi * 5.4 * f * t) * np.exp(-t * 22)
    return y * np.exp(-t * decay) * attack(t, 0.003)


def bell(f, dur=2.6):
    t = tt(dur)
    y = np.sin(2 * np.pi * f * t) * np.exp(-t * 1.8)
    y += 0.38 * np.sin(2 * np.pi * 2.756 * f * t) * np.exp(-t * 3.8)
    y += 0.16 * np.sin(2 * np.pi * 5.404 * f * t) * np.exp(-t * 7)
    return y * attack(t, 0.002)


def pad_voice(f, dur, a=0.7, r=0.9):
    t = tt(dur + r)
    y = np.zeros_like(t)
    for det in (-0.0045, 0.0, 0.0045):
        ff = f * (1 + det)
        for n in range(1, 7):
            y += (0.55**n) / n * np.sin(2 * np.pi * n * ff * t + n * det * 40)
    env = np.minimum(np.clip(t / a, 0, 1), np.clip((dur + r - t) / r, 0, 1))
    return y * env * (0.85 + 0.15 * np.sin(2 * np.pi * 0.3 * t))


def bass(f, dur):
    t = tt(dur + 0.08)
    y = np.sin(2 * np.pi * f * t) + 0.22 * np.sin(2 * np.pi * 2 * f * t) + 0.06 * np.sin(2 * np.pi * 3 * f * t)
    env = attack(t, 0.006) * (0.55 + 0.45 * np.exp(-t * 5)) * np.clip((dur + 0.08 - t) / 0.08, 0, 1)
    return y * env


def kick():
    t = tt(0.4)
    ph = 2 * np.pi * np.cumsum(48 + 75 * np.exp(-t * 32)) / SR
    return np.sin(ph) * np.exp(-t * 8.5) * attack(t, 0.002)


def bandnoise(dur, lo, hi, decay):
    t = tt(dur)
    x = rng.standard_normal(len(t))
    sos = signal.butter(2, [lo, hi], btype="band", fs=SR, output="sos")
    return signal.sosfilt(sos, x) * np.exp(-t * decay)


def shaker():
    return bandnoise(0.12, 5500, 12000, 48)


def snap():
    y = np.zeros(int(0.25 * SR))
    for k, g in ((0, 1.0), (0.009, 0.7), (0.019, 0.45)):
        b = bandnoise(0.2, 900, 3200, 24) * g
        i = int(k * SR)
        y[i : i + len(b)] += b[: len(y) - i]
    return y


def riser(dur):
    t = tt(dur)
    x = rng.standard_normal(len(t))
    out = np.zeros_like(x)
    seg = int(0.05 * SR)
    for i in range(0, len(x), seg):
        k = i / len(x)
        fc = 400 + 7000 * k**2
        sos = signal.butter(2, [fc * 0.7, min(fc * 1.4, SR / 2 - 100)], btype="band", fs=SR, output="sos")
        out[i : i + seg] = signal.sosfilt(sos, x[i : i + seg])
    return out * (t / dur) ** 2.2


# ── harmony ─────────────────────────────────────────────────────────────────
CH = {
    "D": dict(bass=38, pad=[62, 66, 69, 74], arp=[74, 78, 81, 86]),
    "A": dict(bass=45, pad=[61, 64, 69, 73], arp=[73, 76, 81, 85]),
    "Bm": dict(bass=47, pad=[62, 66, 71, 74], arp=[71, 74, 78, 83]),
    "G": dict(bass=43, pad=[62, 67, 71, 74], arp=[74, 79, 83, 86]),
}
BARS = ["G", "A"] + ["D", "A", "Bm", "G"] * 5 + ["G", "A", "D"]
NB = len(BARS)  # 25
COUNTER = {"D": [78, 76, 74, None], "A": [76, 73, 69, None], "Bm": [74, 76, 78, None], "G": [83, 81, 79, 78]}


def build():
    pad, arp, bas, drm, bel, fx = buf(), buf(), buf(), buf(), buf(), buf()
    for b, name in enumerate(BARS):
        c = CH[name]
        t0 = b * BAR
        last = b == NB - 1
        dur = (TOTAL - t0) if last else BAR
        # pad (always)
        for k, m in enumerate(c["pad"]):
            add(pad, pad_voice(mtof(m), dur, a=0.5 if b else 1.2, r=1.2 if last else 0.6), t0, 0.16, pan=(-0.5 + k / 3))
        groove = 2 <= b <= 21
        lift = 22 <= b <= 23
        # bass
        if groove or lift:
            f = mtof(c["bass"])
            add(bas, bass(f, BEAT * 1.4), t0, 0.33)
            add(bas, bass(f, BEAT * 0.45), t0 + BEAT * 1.5, 0.27)
            add(bas, bass(f * (1.5 if name in ("D", "G") else 1), BEAT * 1.8), t0 + BEAT * 2, 0.3)
        if last:
            add(bas, bass(mtof(c["bass"]), dur - 0.1), t0, 0.42)
        # kalimba arpeggio (8ths)
        if groove or lift:
            patt = [0, 2, 1, 2, 3, 2, 1, 2]
            for i, p in enumerate(patt):
                acc = 1.0 if i % 2 == 0 else 0.72
                add(arp, kalimba(mtof(c["arp"][p])), t0 + i * BEAT / 2, 0.15 * acc, pan=0.35 if i % 2 else -0.25)
        # counter-melody (B section)
        if 10 <= b <= 17:
            for i, m in enumerate(COUNTER[name]):
                if m is not None:
                    add(bel, kalimba(mtof(m + 12), 1.6, 3.2), t0 + i * BEAT, 0.09, pan=0.2)
        # drums
        if groove or lift:
            for beat in range(4):
                if beat in (0, 2):
                    add(drm, kick(), t0 + beat * BEAT, 0.4)
                if b >= 10 and beat in (1, 3):
                    add(drm, snap(), t0 + beat * BEAT, 0.16, pan=0.1)
            for s in range(16):
                acc = 1.0 if s % 4 == 2 else (0.55 if s % 2 else 0.35)
                add(drm, shaker(), t0 + s * BEAT / 4 + (0.012 if s % 2 else 0), 0.07 * acc, pan=0.45)
    # intro glockenspiel sparkle (bars 0-1)
    intro = [(0.3, 71), (0.6, 74), (0.9, 79), (1.2, 83), (1.8, 86), (2.7, 73), (3.0, 76), (3.3, 81), (3.6, 85), (4.2, 88)]
    for t0, m in intro:
        add(bel, bell(mtof(m + 12)), t0, 0.11, pan=0.3)
    # call-to-action melody (bars 22-24)
    t22 = 22 * BAR
    cta = [(0, 86), (BEAT, 83), (2 * BEAT, 81), (3 * BEAT, 78), (BAR, 76), (BAR + BEAT, 78), (BAR + 2 * BEAT, 81), (2 * BAR, 86), (2 * BAR + 0.02, 81), (2 * BAR + 0.04, 78)]
    for dt, m in cta:
        add(bel, bell(mtof(m)), t22 + dt, 0.12, pan=-0.2)
    # risers into the groove and into the CTA
    add(fx, riser(1.8), 2 * BAR - 1.8, 0.05)
    add(fx, riser(2.2), 22 * BAR - 2.2, 0.06)
    # final shimmer
    for k, m in enumerate([86, 90, 93, 98]):
        add(bel, bell(mtof(m)), 24 * BAR + 0.05 + k * 0.09, 0.06, pan=-0.4 + k * 0.25)
    return pad, arp, bas, drm, bel, fx


def reverb(x, seconds=1.9, seed=3):
    r = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = r.standard_normal((n, 2)) * np.exp(-t / (seconds / 6.9))[:, None]
    sos = signal.butter(1, 5000, btype="low", fs=SR, output="sos")
    ir = signal.sosfilt(sos, ir, axis=0)
    ir /= np.sqrt((ir**2).sum(axis=0))
    out = np.stack([signal.fftconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], axis=1)
    return out


def vo_envelope():
    env = np.zeros(N)
    for i, (t0, d) in enumerate(zip(TIMING["L"], TIMING["D"])):
        y, sr = sf.read(ROOT / "assets" / "vo" / f"vo-{i:02d}.wav")
        if y.ndim > 1:
            y = y.mean(axis=1)
        y = signal.resample_poly(y, SR, sr)
        i0 = int(t0 * SR)
        y = np.abs(y[: N - i0])
        env[i0 : i0 + len(y)] = np.maximum(env[i0 : i0 + len(y)], y)
    # gate + smooth: fast attack, slow release
    win = int(0.03 * SR)
    rms = np.sqrt(np.convolve(env**2, np.ones(win) / win, mode="same"))
    gate = (rms > 0.02).astype(float)
    out = np.zeros_like(gate)
    a, r = np.exp(-1 / (0.06 * SR)), np.exp(-1 / (0.35 * SR))
    g = 0.0
    for i in range(0, N, 32):  # control rate
        target = gate[i]
        coef = a if target > g else r
        g = target + (g - target) * coef**32
        out[i : i + 32] = g
    return out


def main():
    pad, arp, bas, drm, bel, fx = build()
    dry = pad + arp + bas + drm * 0.9 + bel + fx
    wet = reverb(pad * 0.6 + arp + bel * 1.2 + drm * 0.15)
    mix = dry + 0.26 * wet
    # gentle master: high-pass rumble, soft clip
    sos = signal.butter(2, 32, btype="high", fs=SR, output="sos")
    mix = signal.sosfilt(sos, mix, axis=0)
    # carve under the voiceover: 3-band dynamic dip
    e = vo_envelope()[:, None]
    lo = signal.sosfiltfilt(signal.butter(2, 220, btype="low", fs=SR, output="sos"), mix, axis=0)
    hi = signal.sosfiltfilt(signal.butter(2, 4500, btype="high", fs=SR, output="sos"), mix, axis=0)
    mid = mix - lo - hi
    carved = lo * (1 - 0.35 * e) + mid * (1 - 0.68 * e) + hi * (1 - 0.45 * e)
    # level: bed mean ≈ -29.5 dBFS (≈10 dB under the voiceover)
    rms = np.sqrt(np.mean(carved**2))
    carved *= 10 ** (-29.5 / 20) / rms
    # fade in/out
    t = np.arange(N) / SR
    carved *= np.clip(t / 0.25, 0, 1)[:, None] * np.clip((TOTAL - t) / 1.6, 0, 1)[:, None]
    carved = np.tanh(carved * 1.2) / 1.2
    out = ROOT / "assets" / "music" / "ennour-chemin-de-lumiere.wav"
    out.parent.mkdir(parents=True, exist_ok=True)
    sf.write(out, carved.astype(np.float32), SR, subtype="PCM_16")
    print(out, f"{len(carved) / SR:.2f}s", "peak", f"{20 * np.log10(np.abs(carved).max()):.1f} dBFS")


main()
