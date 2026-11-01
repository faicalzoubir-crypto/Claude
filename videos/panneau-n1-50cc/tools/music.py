#!/usr/bin/env python3
"""Music bed for the N1 sign Reel, synthesised here: no samples, no vocals.

The shape the user asked for: a tense, investigative build over scenes 1–4
(0–20 s), a hit when the police appear (20.0 s), lighter and resolving in
scene 6 (25–37 s), and a hard cut on a beat at 39 s with no fade, so the Reel
loops. 120 BPM, D minor; the tension texture comes back at 37 s and runs on
into the start.

The track is rendered as a loop: every tail that rings past 39 s (notes,
echoes, reverb) is folded back onto the start, and the drone's partials make
whole cycles in 39 s, so the jump from the end back to 0 has no seam.
Writes assets/music/track.wav (48 kHz, stereo, 16-bit, about -14 LUFS).
"""
import wave
from pathlib import Path

import numpy as np
import pyloudnorm
from scipy import signal

ROOT = Path(__file__).resolve().parent.parent
SR = 48000
LOOP = 39.0
TAIL = 4.0
N = int((LOOP + TAIL) * SR)
NL = int(LOOP * SR)
rng = np.random.default_rng(39)

L, R, SEND = np.zeros(N), np.zeros(N), np.zeros(N)


# ---- building blocks -------------------------------------------------------------
def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def tt(dur):
    return np.arange(int(dur * SR)) / SR


def loopf(f):
    """A frequency that makes a whole number of cycles in the loop (seamless wrap)."""
    return round(f * LOOP) / LOOP


def saw(f, dur, nharm=40, t=None):
    t = tt(dur) if t is None else t
    out = np.zeros_like(t)
    for k in range(1, int(min(nharm, 16000 / f)) + 1):
        out += np.sin(2 * np.pi * k * f * t) / k
    return out * (2 / np.pi)


def filt(x, kind, fc, order=2):
    fc = np.atleast_1d(fc) / (SR / 2)
    b, a = signal.butter(order, fc if len(fc) > 1 else fc[0], kind)
    return signal.lfilter(b, a, x)


def env(dur, decay, attack=0.003):
    t = tt(dur)
    return np.exp(-t / decay) * np.clip(t / attack, 0, 1)


def adsr(dur, a, r, peak=1.0):
    t = tt(dur)
    e = np.clip(t / a, 0, 1) * peak
    return e * np.clip((dur - t) / r, 0, 1)


def add(sig, t, gain=1.0, pan=0.0, send=0.0):
    i = int(round(t * SR))
    j = min(i + len(sig), N)
    if j <= i:
        return
    s = sig[: j - i] * gain
    gl, gr = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    L[i:j] += s * gl
    R[i:j] += s * gr
    SEND[i:j] += s * send


def noise(dur):
    return rng.standard_normal(int(dur * SR))


# ---- instruments -----------------------------------------------------------------
def kick(gain, t, low=48, punch=100, decay=0.32):
    x = tt(0.6)
    f = low + punch * np.exp(-x / 0.04)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x / decay)
    click = filt(noise(0.6), "high", 3000) * np.exp(-x / 0.004) * 0.25
    add(body + click, t, gain)


def clap(gain, t, send=0.3):
    x = tt(0.4)
    n = filt(noise(0.4), "band", [900, 2600])
    e = sum(np.exp(-np.clip(x - d, 0, None) / 0.012) * (x >= d) for d in (0, 0.011, 0.022))
    e += np.exp(-np.clip(x - 0.03, 0, None) / 0.14) * (x >= 0.03)
    add(n * e * 0.6, t, gain, send=send)


def snare(gain, t, send=0.25):
    x = tt(0.35)
    n = filt(noise(0.35), "band", [1500, 7000]) * np.exp(-x / 0.12)
    body = np.sin(2 * np.pi * 190 * x) * np.exp(-x / 0.06) * 0.6
    add(n + body, t, gain, send=send)


def hat(gain, t, pan=0.0, decay=0.03):
    add(filt(noise(0.25), "high", 7000) * env(0.25, decay), t, gain, pan)


def rim(gain, t):
    x = tt(0.12)
    add((np.sin(2 * np.pi * 1700 * x) * 0.6 + filt(noise(0.12), "high", 2500) * 0.4) * np.exp(-x / 0.02), t, gain, 0.15, 0.2)


def pluck(m, gain, t, pan=0.0, send=0.3, echoes=3, decay=1.0):
    """Plucked tone: harmonics that die faster the higher they are; with ping-pong echoes."""
    f, x = midi(m), tt(1.6)
    tone = sum(np.sin(2 * np.pi * k * f * x) / k ** 1.3 * np.exp(-x * (2.2 + 1.1 * k) / decay) for k in range(1, 9))
    tone *= np.clip(x / 0.002, 0, 1)
    for e in range(echoes + 1):
        add(tone, t + e * 0.375, gain * 0.38 ** e, pan if e % 2 == 0 else -pan, send)


def bass_note(m, gain, t, dur, cutoff, decay):
    x = saw(midi(m), dur) * env(dur, decay)
    add(filt(x, "low", cutoff) + np.sin(2 * np.pi * midi(m - 12) * tt(dur)) * env(dur, decay * 1.4) * 0.5, t, gain)


def pad(notes, gain, t, dur, cutoff=1800, send=0.45):
    for m in notes:
        for det, pan in ((-0.07, -0.35), (0.07, 0.35)):
            x = filt(saw(midi(m + det), dur + 0.6, nharm=30), "low", cutoff) * adsr(dur + 0.6, 0.25, 0.6)
            add(x, t, gain, pan, send)


# ---- arrangement -----------------------------------------------------------------
D1, D2, D3 = 26, 38, 50

# Tension texture: 0–19.75 s, and again 37–39 s running into the start.
in_tension = lambda t: t < 19.75 or t >= 37.0

# Drone: D and A partials on loop-locked frequencies, swelling across the build,
# gone for the hit and scene 6, back at 37 s at the level it starts with.
x = np.arange(NL) / SR
lfo = 0.5 + 0.5 * np.sin(2 * np.pi * loopf(0.1) * x)
drone = (np.sin(2 * np.pi * loopf(midi(D1)) * x) * 0.9 + np.sin(2 * np.pi * loopf(midi(D2)) * x) * 0.5
         + np.sin(2 * np.pi * loopf(midi(D2 + 7)) * x) * 0.22 * lfo)
drone += filt(saw(loopf(midi(D2)), LOOP, nharm=24, t=x), "low", 420) * (0.25 + 0.2 * lfo)
g = np.interp(x, [0, 19.7, 19.75, 36.99, 37.0, 37.4, LOOP], [0.4, 0.85, 0.0, 0.0, 0.0, 0.4, 0.4])
L[:NL] += drone * g * 0.33
R[:NL] += drone * g * 0.33
SEND[:NL] += drone * g * 0.05

# Pulse bass on the eighths, its filter opening through the build.
pattern = [D2] * 8 + [D2, D2, D2, D2, D2 + 1, D2 + 1, D2 - 2, D2 - 2]
for i in range(int(LOOP / 0.25)):
    t = i * 0.25
    if not in_tension(t):
        continue
    note = pattern[i % 16] if t < 20 else D2
    cutoff = 220 * (1300 / 220) ** (t / 19.75) if t < 20 else 240
    bass_note(note, 0.36 + 0.24 * (t / 19.75) if t < 20 else 0.36, t, 0.26, cutoff, 0.16)

# Ticks on the sixteenths, rising with the build.
for i in range(int(LOOP / 0.125)):
    t = i * 0.125
    if not in_tension(t):
        continue
    level = 0.08 + 0.24 * (t / 20) if t < 20 else 0.08
    accent = (1.0, 0.45, 0.7, 0.45)[i % 4]
    hat(level * accent, t, 0.3 if i % 2 else -0.3)

# The motif: D F A G#, a plucked question every other bar, and once more at 37 s.
for bar in (4.0, 8.0, 12.0, 16.0, 37.0):
    up = 12 if bar == 16.0 else 0
    for k, m in enumerate((62, 65, 69, 68)):
        pluck(m + up, 0.2, bar + 0.5 * k, pan=0.4, send=0.35)

# Heartbeat from 8 s: a soft sub on beats 1 and 3.
for t in np.arange(8.0, 19.5, 1.0):
    kick(0.32 + 0.2 * (t - 8) / 11, t, low=42, punch=40, decay=0.25)

# Riser 15–19.75 s: noise sweeping up through a band-pass, and a rising tone.
seg = 0.05
for k in range(int(4.75 / seg)):
    t = 15.0 + k * seg
    p = k * seg / 4.75
    centre = 400 * (6000 / 400) ** p
    chunk = filt(noise(seg * 2), "band", [centre * 0.7, min(centre * 1.4, 20000)]) * np.hanning(int(seg * 2 * SR))
    add(chunk, t, 0.05 + 0.3 * p ** 2, send=0.2)
x = tt(4.75)
glide = np.sin(2 * np.pi * np.cumsum(midi(50) * 4 ** (x / 4.75)) / SR) * (x / 4.75) ** 2
add(glide * np.clip((4.75 - x) / 0.01, 0, 1), 15.0, 0.12, send=0.3)

# Snare roll into the hit: sixteenths, then thirty-seconds; then a breath of silence.
for k, t in enumerate(list(np.arange(18.0, 19.0, 0.125)) + list(np.arange(19.0, 19.75, 0.0625))):
    snare(0.15 + 0.4 * (t - 18) / 1.75, t, send=0.2)

# THE HIT at 20.0 s: sub boom, crack, a dark D minor stab.
x = tt(2.5)
boom = np.sin(2 * np.pi * np.cumsum(32 + 80 * np.exp(-x / 0.12)) / SR) * np.exp(-x / 1.1)
add(boom, 20.0, 0.95, send=0.25)
add(filt(noise(0.6), "high", 1200) * env(0.6, 0.09), 20.0, 0.6, send=0.6)
for m in (D2, D2 + 7, D3, D3 + 3):
    add(filt(saw(midi(m), 2.5), "low", 900) * env(2.5, 0.7, 0.004), 20.0, 0.16, send=0.6)

# The drop, 20–25 s: four on the floor, claps, driving bass, dark pad.
for t in np.arange(20.5, 25.0, 0.5):
    kick(0.8, t)
for t in (20.5, 21.5, 22.5, 23.5):
    clap(0.5, t)
for t in np.arange(20.25, 24.0, 0.5):
    hat(0.25, t, 0.2, decay=0.08)
drop_bass = [D2, D2, D3, D2, D2 + 3, D2 + 3, D2 + 2, D2 + 2]
for i, t in enumerate(np.arange(20.0, 24.0, 0.25)):
    bass_note(drop_bass[i % 8], 0.5, t, 0.24, 900, 0.18)
pad((D3, D3 + 3, D3 + 7), 0.12, 20.0, 4.0, cutoff=1300, send=0.5)
# Fill 24–25 s: snare sixteenths and a noise swell into scene 6.
for k, t in enumerate(np.arange(24.0, 25.0, 0.125)):
    snare(0.15 + 0.06 * k, t)
x = tt(1.0)
add(filt(noise(1.0), "high", 3000) * (x / 1.0) ** 3, 24.0, 0.25, send=0.4)

# Scene 6, 25–37 s: lighter, resolving. Bb – F – C – Dm – Bb – A, then Dm at 37.
chords = [(25.0, (58, 62, 65), 34), (27.0, (57, 60, 65), 41), (29.0, (55, 60, 64), 36),
          (31.0, (57, 62, 65), 38), (33.0, (58, 62, 65), 34), (35.0, (57, 61, 64), 33)]
for bar, (t0, notes, root) in enumerate(chords):
    pad(notes, 0.085 + 0.01 * bar, t0, 2.0)
    arp = [notes[0] + 12, notes[1] + 12, notes[2] + 12, notes[0] + 24]
    for k, idx in enumerate([0, 1, 2, 3, 2, 1, 0, 1] * 2):
        pluck(arp[idx], 0.07 + 0.006 * bar, t0 + k * 0.125, pan=0.35 if k % 2 else -0.35, send=0.3, echoes=1, decay=0.6)
    for off in (0.0, 0.75, 1.5):
        bass_note(root, 0.42, t0 + off, 0.6, 500, 0.4)
    for off in (0.0, 1.0):
        kick(0.45, t0 + off, decay=0.25)
    for off in (0.5, 1.5):
        rim(0.2, t0 + off)
    for k in range(16):
        hat((0.05, 0.025, 0.04, 0.025)[k % 4] * (1.3 if bar == 5 else 1.0), t0 + k * 0.125, 0.25)
    if bar == 5:  # lift into the cadence
        for off in (0.5, 1.5):
            kick(0.4, t0 + off, decay=0.22)

# ---- mix, reverb, fold the tail onto the start, master --------------------------------
x = tt(2.6)
ir = [filt(rng.standard_normal(len(x)) * np.exp(-x / 0.3), "low", 6000) for _ in range(2)]
pre = int(0.018 * SR)
for k in range(2):
    ir[k] = np.concatenate([np.zeros(pre), ir[k]])[: len(x)] / np.sqrt(np.sum(ir[k] ** 2))
wetL = signal.fftconvolve(SEND, ir[0])[:N]
wetR = signal.fftconvolve(SEND, ir[1])[:N]
mix = np.stack([L + 0.5 * wetL, R + 0.5 * wetR], axis=1)

loop = mix[:NL].copy()
loop[: N - NL] += mix[NL:]                     # tails past 39 s ring on at the start
# No DC or sub rumble; filtered round the loop (primed with its last second) so
# the filter does not start cold at 0 s.
loop = filt(np.concatenate([loop[-SR:], loop]).T, "high", 25).T[SR:]

meter = pyloudnorm.Meter(SR)
loop *= 10 ** ((-14.0 - meter.integrated_loudness(loop)) / 20)
# Peak limiter (ceiling -1 dBFS): gain from the loudest sample 3 ms ahead, 80 ms release.
ceiling = 10 ** (-1 / 20)
peak = np.max(np.abs(loop), axis=1)
need = np.minimum(1.0, ceiling / np.maximum(peak, 1e-9))
ahead = int(0.003 * SR)
need = np.minimum.accumulate(np.lib.stride_tricks.sliding_window_view(np.pad(need, (0, ahead), constant_values=1), ahead + 1), axis=1)[:, -1]
gain = np.empty_like(need)
g, rel = 1.0, np.exp(-1 / (0.08 * SR))
for _ in range(2):  # second pass starts where the first ended: the gain wraps round the loop too
    for i, n in enumerate(need):
        g = n if n < g else n + (g - n) * rel
        gain[i] = g
loop *= gain[:, None]

out = ROOT / "assets" / "music" / "track.wav"
out.parent.mkdir(parents=True, exist_ok=True)
pcm = np.clip(np.round(loop * 32767), -32768, 32767).astype("<i2")
with wave.open(str(out), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print(f"{out.relative_to(ROOT)}: {len(loop) / SR:.2f} s, {meter.integrated_loudness(loop):.1f} LUFS, "
      f"peak {20 * np.log10(np.max(np.abs(loop))):.1f} dBFS, end→start step {np.max(np.abs(loop[-1] - loop[0])):.4f} "
      f"(sample-to-sample inside: 99th pct {np.percentile(np.abs(np.diff(loop, axis=0)), 99):.4f}, max {np.max(np.abs(np.diff(loop, axis=0))):.4f})")
