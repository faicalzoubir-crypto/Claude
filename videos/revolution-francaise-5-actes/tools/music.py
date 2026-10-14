"""« La frise en flammes » — music bed + sound effects, synthesized (deterministic, no samples).

Music follows the five acts (frame starts from STORYBOARD.md durations):
  F1        spark: low drone, swell as the flame runs, title chord
  F2-F3     Ancien Régime: harpsichord-like pluck ostinato over a minor pad; F3 held
  F4-F5     Acte 1: march — timpani, string ostinato, heroic minor → major
  F6        Acte 2: tension — low tremolo strings, sparse plucks
  F7        Acte 3: build — ostinato back, timpani crescendo
  F8-F10    Acte 4: fury — driving low ostinato and timpani; a bar of silence after the
            king's death; collapse at thermidor
  F11-F12   Acte 5: ashes — sparse pad and distant bell; thins to one low note
  F13-F14   answer + Hugo: resolution in D major, final chord rings out
The bed is carved under the voice-over (3-band dynamic dip driven by the VO envelope).

Sound effects are written as separate files (assets/sfx/*.wav) and listed in audio_meta.json
(source: host) with their frame and offset, so the assembler mounts each one on its own track.

Usage: /root/.venvs/hf-audio/bin/python tools/music.py
"""
import json
import re
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal

ROOT = Path(__file__).resolve().parent.parent
SR = 48000
rng = np.random.default_rng(1789)
mtof = lambda m: 440.0 * 2 ** ((m - 69) / 12)

# ── timeline ────────────────────────────────────────────────────────────────
sb = (ROOT / "STORYBOARD.md").read_text(encoding="utf-8")
DUR = [float(x) for x in re.findall(r"^- duration: ([\d.]+)s$", sb, re.M)]
START = np.concatenate([[0], np.cumsum(DUR)[:-1]])
TOTAL = float(sum(DUR))
N = int((TOTAL + 0.05) * SR)
F = {i + 1: float(s) for i, s in enumerate(START)}  # frame number → start (s)
CUES = json.loads((ROOT / "assets/voice/cues.json").read_text(encoding="utf-8"))


def at(frame, word, k=1):
    seen = 0
    for w in CUES[str(frame)]["words"]:
        norm = re.sub(r"[^a-zà-ÿ0-9'-]", "", w["w"].lower())
        if norm.startswith(word):
            seen += 1
            if seen == k:
                return w["t"]
    raise KeyError(f"frame {frame}: {word}#{k}")


def T(frame, word, k=1, dt=0.0):
    return F[frame] + at(frame, word, k) + dt


# ── helpers ─────────────────────────────────────────────────────────────────
def tt(d):
    return np.arange(int(d * SR)) / SR


def buf():
    return np.zeros((N, 2))


def add(dst, x, t0, gain=1.0, pan=0.0):
    i0 = int(t0 * SR)
    if i0 >= len(dst) or i0 < 0:
        return
    x = x[: len(dst) - i0]
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    dst[i0 : i0 + len(x), 0] += x * gain * l
    dst[i0 : i0 + len(x), 1] += x * gain * r


def lp(x, fc, order=2):
    return signal.sosfilt(signal.butter(order, fc, btype="low", fs=SR, output="sos"), x)


def bp(x, lo, hi, order=2):
    return signal.sosfilt(signal.butter(order, [lo, hi], btype="band", fs=SR, output="sos"), x)


def env_adsr(t, a, d, r, dur):
    e = np.minimum(np.clip(t / a, 0, 1), np.clip((dur + r - t) / r, 0, 1))
    return e


# ── instruments ─────────────────────────────────────────────────────────────
def saw(f, t, n=12):
    y = np.zeros_like(t)
    for k in range(1, n + 1):
        if f * k > SR / 2.2:
            break
        y += np.sin(2 * np.pi * f * k * t) / k
    return y


def pad(f, dur, a=0.9, r=1.2, bright=1600):
    t = tt(dur + r)
    y = sum(saw(f * (1 + d), t, 10) for d in (-0.004, 0.0, 0.0045)) / 3
    y = lp(y, bright)
    return y * env_adsr(t, a, 0, r, dur) * (0.9 + 0.1 * np.sin(2 * np.pi * 0.25 * t))


def bowed(f, dur, bright=2200):
    t = tt(dur + 0.12)
    y = sum(saw(f * (1 + d), t, 10) for d in (-0.003, 0.003)) / 2
    y = lp(y, bright)
    e = np.clip(t / 0.025, 0, 1) * (0.7 + 0.3 * np.exp(-t * 6)) * np.clip((dur + 0.12 - t) / 0.12, 0, 1)
    return y * e


def tremolo(f, dur):
    t = tt(dur + 0.6)
    y = lp(sum(saw(f * (1 + d), t, 8) for d in (-0.004, 0.004)) / 2, 900)
    trem = 0.6 + 0.4 * np.sin(2 * np.pi * 9.5 * t)
    return y * trem * env_adsr(t, 0.4, 0, 0.6, dur)


def pluck(f, dur=1.0, bright=1.0):
    t = tt(dur)
    y = np.zeros_like(t)
    for k in range(1, 9):
        y += (0.8**k) * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (4 + 2.2 * k * bright))
    return y * np.clip(t / 0.002, 0, 1)


def timpani(f, dur=1.6):
    t = tt(dur)
    ph = 2 * np.pi * np.cumsum(f * (1 + 0.12 * np.exp(-t * 18))) / SR
    y = np.sin(ph) + 0.35 * np.sin(1.5 * ph) * np.exp(-t * 3)
    noise = lp(rng.standard_normal(len(t)), 600) * np.exp(-t * 30) * 0.5
    return (y * np.exp(-t * 2.4) + noise) * np.clip(t / 0.003, 0, 1)


def snare_roll(dur, peak=1.0):
    t = tt(dur)
    x = bp(rng.standard_normal(len(t)), 1500, 7000)
    strokes = 0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 14 * t))
    return x * strokes * (t / dur) ** 1.6 * peak


def bell(f, dur=3.0):
    t = tt(dur)
    y = np.sin(2 * np.pi * f * t) * np.exp(-t * 1.4)
    y += 0.4 * np.sin(2 * np.pi * 2.756 * f * t) * np.exp(-t * 3.2)
    y += 0.18 * np.sin(2 * np.pi * 5.404 * f * t) * np.exp(-t * 6)
    return y * np.clip(t / 0.002, 0, 1)


def riser(dur):
    t = tt(dur)
    x = rng.standard_normal(len(t))
    out = np.zeros_like(x)
    seg = int(0.05 * SR)
    for i in range(0, len(x), seg):
        k = i / len(x)
        fc = 300 + 5000 * k**2
        out[i : i + seg] = bp(x[i : i + seg], fc * 0.7, min(fc * 1.4, SR / 2 - 100))
    return out * (t / dur) ** 2


# chords (MIDI): bass + 3-4 voices
CH = {
    "Dm": (38, [62, 65, 69]), "Gm": (43, [62, 67, 70]), "A": (45, [61, 64, 69]), "Bb": (46, [62, 65, 70]),
    "F": (41, [60, 65, 69]), "C": (36, [60, 64, 67]), "Csd": (37, [61, 64, 67]), "D": (38, [62, 66, 69]),
    "Bm": (47, [62, 66, 71]), "G": (43, [62, 67, 71]), "Em": (40, [64, 67, 71]),
}
BEAT = 60 / 84  # 84 BPM


def section(t0, t1, prog, layers, buses, bar=4 * BEAT, gain=1.0):
    """Lay chord progression `prog` (looped) from t0 to t1 with the named layers."""
    pd, st, pl, pc, lo = buses
    t = t0
    i = 0
    while t < t1 - 0.05:
        name = prog[i % len(prog)]
        bass, voices = CH[name]
        d = min(bar, t1 - t)
        if "pad" in layers:
            for k, m in enumerate(voices):
                add(pd, pad(mtof(m), d, a=0.6, r=0.9), t, 0.09 * gain, pan=-0.4 + 0.4 * k)
            add(pd, pad(mtof(bass + 12), d, a=0.6, r=0.9, bright=700), t, 0.10 * gain)
        if "drone" in layers:
            add(lo, pad(mtof(bass), d, a=1.2, r=1.5, bright=400), t, 0.16 * gain)
        if "pluck" in layers:
            arp = [voices[0], voices[1], voices[2], voices[1] + 12 if voices[1] + 12 < 84 else voices[1]]
            for s in range(int(round(d / (BEAT / 2)))):
                m = arp[s % 4] + (12 if s % 8 >= 4 else 0)
                add(pl, pluck(mtof(m), 0.9), t + s * BEAT / 2, 0.07 * gain * (1.0 if s % 2 == 0 else 0.7), pan=0.3 if s % 2 else -0.3)
        if "ostinato" in layers or "fury" in layers:
            step = BEAT / 2 if "ostinato" in layers else BEAT / 4
            for s in range(int(round(d / step))):
                m = bass + 12 + (0 if s % 4 != 2 else 7)
                add(st, bowed(mtof(m), step * 0.8, bright=1400 if "fury" in layers else 1800), t + s * step, (0.08 if "fury" in layers else 0.07) * gain, pan=-0.2)
        if "trem" in layers:
            for m in voices[:2]:
                add(st, tremolo(mtof(m - 12), d), t, 0.06 * gain, pan=0.25)
        if "timp" in layers:
            for b in (0, 2):
                if t + b * BEAT < t1:
                    add(pc, timpani(mtof(bass)), t + b * BEAT, 0.32 * gain)
        if "timp8" in layers:
            for b in range(int(round(d / (BEAT / 2)))):
                acc = 1.0 if b % 2 == 0 else 0.55
                add(pc, timpani(mtof(bass), 0.9), t + b * BEAT / 2, 0.24 * gain * acc)
        t += bar
        i += 1


def build():
    pd, st, pl, pc, lo, fx = buf(), buf(), buf(), buf(), buf(), buf()
    buses = (pd, st, pl, pc, lo)
    run0 = T(1, "et")
    # F1 — spark
    add(lo, pad(mtof(38), run0 + 0.5, a=1.5, r=1.0, bright=380), 0.0, 0.22)
    add(lo, pad(mtof(45), run0 + 0.5, a=2.0, r=1.0, bright=380), 0.6, 0.12)
    add(fx, riser(run0 - 0.4), 0.4, 0.05)
    section(run0, F[1] + DUR[0], ["Dm", "Bb", "Gm", "A"], ["pad", "drone"], buses, bar=2 * BEAT, gain=1.1)
    for k, m in enumerate([74, 77, 81, 86]):
        add(pl, bell(mtof(m)), T(1, "cinq") + k * 0.12, 0.05, pan=-0.3 + 0.2 * k)
    # F2-F3 — Ancien Régime (F3 held: pad only)
    section(F[2], F[3], ["Dm", "Gm", "A", "Dm"], ["pad", "pluck"], buses, gain=0.9)
    section(F[3], F[4], ["Gm", "A"], ["pad", "drone"], buses, bar=DUR[2] / 2, gain=0.8)
    # Acte 1 — march
    add(fx, snare_roll(1.6, 0.6), F[4] - 1.6, 0.05)
    section(F[4], F[5], ["Dm", "Bb", "F", "C"], ["pad", "ostinato", "timp"], buses, gain=1.0)
    section(F[5], F[6], ["F", "C", "Dm", "Bb"], ["pad", "ostinato", "timp", "pluck"], buses, gain=1.0)
    # Acte 2 — tension
    section(F[6], F[7], ["Dm", "Csd", "Dm", "A"], ["trem", "drone"], buses, gain=1.0)
    for s in range(0, int(DUR[5] / BEAT), 3):
        add(pl, pluck(mtof(62 if s % 2 else 57), 1.2, 0.6), F[6] + s * BEAT, 0.05, pan=0.2)
    # Acte 3 — build
    add(fx, riser(1.4), F[7] - 1.4, 0.05)
    section(F[7], F[8], ["Gm", "A", "Dm", "Bb"], ["pad", "ostinato", "timp8"], buses, gain=1.05)
    # Acte 4 — fury, with a bar of silence after « guillotiné »
    cut0, cut1 = T(8, "guillotiné", dt=0.25), T(8, "guillotiné", dt=0.25) + 4 * BEAT
    section(F[8], cut0, ["Dm", "Bb", "Gm", "A"], ["pad", "fury", "timp"], buses, gain=1.05)
    add(pc, timpani(mtof(38), 3.0), cut0, 0.35)
    section(cut1, F[11], ["Dm", "Bb", "Gm", "A", "Dm", "C", "Bb", "A"], ["pad", "fury", "timp8", "drone"], buses, gain=1.0)
    # Acte 5 — ashes
    section(F[11], F[13], ["Dm", "Bb", "Gm", "A"], ["pad"], buses, bar=8 * BEAT, gain=0.75)
    for k in range(4):
        add(pl, bell(mtof(81 - 5 * (k % 2))), F[11] + 2.0 + k * 6.5, 0.035, pan=0.4)
    # Conclusion — resolution in D major
    section(F[13], F[14], ["D", "A", "Bm", "G"], ["pad", "pluck", "drone"], buses, gain=0.95)
    end = TOTAL
    for k, m in enumerate([62, 66, 69, 74]):
        add(pd, pad(mtof(m), end - F[14] - 0.6, a=0.8, r=1.2), F[14], 0.10, pan=-0.3 + 0.2 * k)
    add(lo, pad(mtof(38), end - F[14] - 0.6, a=0.8, r=1.2, bright=420), F[14], 0.18)
    for k, m in enumerate([74, 78, 81, 86]):
        add(pl, bell(mtof(m)), F[14] + 0.1 + k * 0.15, 0.045, pan=-0.4 + 0.25 * k)
    return pd, st, pl, pc, lo, fx


def reverb(x, seconds=2.4, seed=7):
    r = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = r.standard_normal((n, 2)) * np.exp(-t / (seconds / 6.9))[:, None]
    ir = signal.sosfilt(signal.butter(1, 4500, btype="low", fs=SR, output="sos"), ir, axis=0)
    ir /= np.sqrt((ir**2).sum(axis=0))
    return np.stack([signal.fftconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], axis=1)


def vo_envelope():
    env = np.zeros(N)
    for i, s in enumerate(START[:13]):
        y, sr = sf.read(ROOT / f"assets/voice/{i + 1:02d}.wav")
        y = y.mean(axis=1) if y.ndim > 1 else y
        if sr != SR:
            y = signal.resample_poly(y, SR, sr)
        i0 = int(s * SR)
        y = np.abs(y[: N - i0])
        env[i0 : i0 + len(y)] = np.maximum(env[i0 : i0 + len(y)], y)
    win = int(0.03 * SR)
    rms = np.sqrt(np.convolve(env**2, np.ones(win) / win, mode="same"))
    gate = (rms > 0.02).astype(float)
    out = np.zeros_like(gate)
    a, r = np.exp(-1 / (0.06 * SR)), np.exp(-1 / (0.4 * SR))
    g = 0.0
    for i in range(0, N, 32):
        target = gate[i]
        coef = a if target > g else r
        g = target + (g - target) * coef**32
        out[i : i + 32] = g
    return out


# ── sound effects ───────────────────────────────────────────────────────────
def norm(x, peak_db=-3.0):
    return x / (np.abs(x).max() + 1e-9) * 10 ** (peak_db / 20)


def sfx_bank():
    s = {}
    t = tt(0.9)
    burst = bp(rng.standard_normal(len(t)), 1800, 7000) * np.exp(-t * 14) * (np.abs(np.sin(2 * np.pi * 37 * t)) ** 3 + 0.3)
    whoomp = lp(rng.standard_normal(len(t)), 500) * np.exp(-((t - 0.25) ** 2) / 0.02) * 1.2
    s["match"] = norm(burst + whoomp)
    t = tt(0.9)
    sweep = np.zeros_like(t)
    x = rng.standard_normal(len(t))
    seg = int(0.03 * SR)
    for i in range(0, len(t), seg):
        k = i / len(t)
        fc = 400 + 2600 * np.sin(np.pi * k)
        sweep[i : i + seg] = bp(x[i : i + seg], fc * 0.6, fc * 1.5)
    s["whoosh"] = norm(sweep * np.sin(np.pi * t / 0.9) ** 2)
    t = tt(1.8)
    clicks = np.zeros_like(t)
    for c in sorted(rng.uniform(0, 1.7, 26)):
        i = int(c * SR)
        n = int(0.006 * SR)
        clicks[i : i + n] += rng.standard_normal(n) * np.exp(-np.arange(n) / (0.0015 * SR)) * rng.uniform(0.3, 1)
    roar = lp(rng.standard_normal(len(t)), 380) * 0.35
    s["crackle"] = norm((bp(clicks, 1200, 9000) + roar) * np.sin(np.pi * t / 1.8) ** 0.7)
    t = tt(0.5)
    thump = np.sin(2 * np.pi * np.cumsum(70 + 60 * np.exp(-t * 40)) / SR) * np.exp(-t * 10)
    s["stamp"] = norm(thump + bp(rng.standard_normal(len(t)), 900, 4000) * np.exp(-t * 60) * 0.6)
    t = tt(0.3)
    s["paper"] = norm(bp(rng.standard_normal(len(t)), 2500, 9000) * np.sin(np.pi * t / 0.3) ** 2, -9)
    dur = 3.6
    t = tt(dur)
    hooves = np.zeros_like(t)
    knock_t = tt(0.07)
    knock = np.sin(2 * np.pi * 820 * knock_t) * np.exp(-knock_t * 70) + 0.5 * np.sin(2 * np.pi * 1260 * knock_t) * np.exp(-knock_t * 90)
    beat = 0.36
    for b in range(int(dur / beat)):
        for off, g in ((0.0, 1.0), (0.09, 0.7), (0.17, 0.85)):
            i = int((b * beat + off) * SR)
            hooves[i : i + len(knock)] += knock[: len(hooves) - i] * g
    s["hooves"] = norm(hooves * np.clip(t / 0.6, 0, 1) * np.clip((dur - t) / 0.8, 0, 1), -6)
    t = tt(0.7)
    slide = np.zeros_like(t)
    x = rng.standard_normal(len(t))
    for i in range(0, int(0.32 * SR), seg):
        fc = 5200 - 3800 * (i / (0.32 * SR))
        slide[i : i + seg] = bp(x[i : i + seg], fc * 0.9, fc * 1.1, 2)
    slide *= np.clip(t / 0.05, 0, 1) * (t < 0.33)
    thud_t = tt(0.4)
    thud = np.sin(2 * np.pi * np.cumsum(62 + 40 * np.exp(-thud_t * 30)) / SR) * np.exp(-thud_t * 9)
    blade = slide * 0.5
    blade[int(0.32 * SR) : int(0.32 * SR) + len(thud)] += thud[: len(blade) - int(0.32 * SR)]
    s["blade"] = norm(blade, -4)
    s["drum"] = norm(timpani(mtof(38), 2.0), -3)
    t = tt(0.5)
    crack = np.zeros_like(t)
    for k, off in enumerate((0.0, 0.03, 0.07, 0.12)):
        i = int(off * SR)
        n = int(0.05 * SR)
        crack[i : i + n] += bp(rng.standard_normal(n), 1500, 6000) * np.exp(-np.arange(n) / (0.008 * SR)) * (1 - 0.2 * k)
    s["crack"] = norm(crack + lp(rng.standard_normal(len(t)), 300) * np.exp(-t * 12) * 0.4, -4)
    t = tt(0.8)
    s["coin"] = norm(sum(np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, d in ((2093, 6), (3378, 9), (5230, 14))) * np.clip(t / 0.001, 0, 1), -8)
    s["chime"] = norm(bell(mtof(86), 2.5) + 0.6 * bell(mtof(93), 2.5), -9)
    t = tt(1.6)
    hiss = bp(rng.standard_normal(len(t)), 2000, 9000) * np.exp(-t * 2.2) * 0.6 + lp(rng.standard_normal(len(t)), 250) * np.exp(-t * 3)
    s["hiss"] = norm(hiss, -6)
    return s


def main():
    pd, st, pl, pc, lo, fx = build()
    dry = pd + st * 1.0 + pl + pc + lo + fx
    wet = reverb(pd * 0.5 + st * 0.6 + pl + pc * 0.25)
    mix = dry + 0.3 * wet
    mix = signal.sosfilt(signal.butter(2, 35, btype="high", fs=SR, output="sos"), mix, axis=0)
    e = vo_envelope()[:, None]
    lo_b = signal.sosfiltfilt(signal.butter(2, 220, btype="low", fs=SR, output="sos"), mix, axis=0)
    hi_b = signal.sosfiltfilt(signal.butter(2, 4500, btype="high", fs=SR, output="sos"), mix, axis=0)
    mid_b = mix - lo_b - hi_b
    carved = lo_b * (1 - 0.35 * e) + mid_b * (1 - 0.66 * e) + hi_b * (1 - 0.45 * e)
    rms = np.sqrt(np.mean(carved**2))
    carved *= 10 ** (-28.5 / 20) / rms
    t = np.arange(N) / SR
    carved *= np.clip(t / 0.3, 0, 1)[:, None] * np.clip((TOTAL - t) / 1.4, 0, 1)[:, None]
    carved = np.tanh(carved * 1.2) / 1.2
    out = ROOT / "assets/music/frise-en-flammes.wav"
    out.parent.mkdir(parents=True, exist_ok=True)
    sf.write(out, carved.astype(np.float32), SR, subtype="PCM_16")
    print(out.relative_to(ROOT), f"{len(carved) / SR:.2f}s", "peak", f"{20 * np.log10(np.abs(carved).max()):.1f} dBFS")

    bank = sfx_bank()
    (ROOT / "assets/sfx").mkdir(parents=True, exist_ok=True)
    for name, x in bank.items():
        sf.write(ROOT / f"assets/sfx/{name}.wav", x.astype(np.float32), SR, subtype="PCM_16")
    # cue list: (frame, sfx, local time, volume)
    loc = lambda f, w, k=1, dt=0.0: at(f, w, k) + dt
    cues = [
        (1, "match", 0.02, 0.45), (1, "crackle", loc(1, "et", dt=-0.1), 0.22),
        (2, "stamp", loc(2, "société", dt=-0.15), 0.22), (2, "crack", loc(2, "dénoncent"), 0.4),
        (4, "whoosh", 0.05, 0.22), (4, "crackle", 0.1, 0.2), (4, "paper", loc(4, "états", dt=-0.3), 0.25),
        (4, "paper", loc(4, "vingt", dt=-0.2), 0.25), (4, "paper", loc(4, "quatorze", dt=-0.2), 0.25),
        (5, "stamp", loc(5, "abolis"), 0.3), (5, "paper", loc(5, "vingt-six", dt=-0.15), 0.25), (5, "paper", loc(5, "octobre", dt=-0.2), 0.25),
        (6, "whoosh", 0.05, 0.22), (6, "hooves", loc(6, "s'enfuit", dt=-0.2), 0.3), (6, "stamp", loc(6, "varennes"), 0.42),
        (7, "whoosh", 0.05, 0.22), (7, "crackle", loc(7, "brasier", dt=-0.1), 0.25), (7, "drum", loc(7, "tombe"), 0.35), (7, "chime", loc(7, "proclamée"), 0.22),
        (8, "whoosh", 0.05, 0.22), (8, "crackle", loc(8, "fureur", dt=-0.1), 0.3), (8, "blade", loc(8, "guillotiné", dt=-0.2), 0.35),
        (9, "stamp", loc(9, "girondins", dt=0.1), 0.4), (9, "drum", loc(9, "comité", dt=-0.1), 0.25), (9, "drum", loc(9, "tribunal", dt=-0.1), 0.25),
        (9, "drum", loc(9, "loi", dt=-0.1), 0.25), (9, "blade", loc(9, "guillotinée", dt=-0.2), 0.25),
        (10, "blade", loc(10, "guillotinés", dt=-0.2), 0.28), (10, "blade", loc(10, "tombe", dt=-0.2), 0.28), (10, "hiss", loc(10, "prend", dt=-0.3), 0.35),
        (11, "whoosh", 0.05, 0.2), (11, "coin", loc(11, "suffrage"), 0.3), (11, "drum", loc(11, "bonaparte"), 0.3),
        (12, "drum", loc(12, "bonaparte"), 0.28), (12, "hiss", loc(12, "révolution", dt=-0.1), 0.38),
        (13, "whoosh", 0.0, 0.15), (13, "chime", loc(13, "oui"), 0.18),
    ]
    meta_p = ROOT / "audio_meta.json"
    meta = json.loads(meta_p.read_text(encoding="utf-8"))
    meta["bgm"] = {"path": "assets/music/frise-en-flammes.wav", "volume": 1.0, "source": "host"}
    meta["sfx"] = [
        {"frame": f, "file": f"assets/sfx/{name}.wav", "offset_s": round(max(0.0, o), 3), "duration_s": round(len(bank[name]) / SR, 3), "volume": v, "source": "host"}
        for f, name, o, v in cues
    ]
    meta_p.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"{len(bank)} sfx files · {len(cues)} cues → audio_meta.json")


main()
