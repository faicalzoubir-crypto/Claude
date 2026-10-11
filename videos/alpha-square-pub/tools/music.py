"""Alpha Square — fond musical synthétisé (déterministe, sans droits).

120 BPM (mesure = 2 s), boucle Am – F – C – G, calée sur le film (durée et repères lus dans tools/timing.json) :
  accroche (0–3 s)     : nappe filtrée, pluck, impact sur « Bac ? », montée vers la marque
  marque → atouts      : groove (kick, basse pulsée, arpège, charley), clap sur 2 et 4 à partir de 6 s
  carte vue du ciel    : batterie coupée (sauf charley), long souffle montant façon vol de drone
  0,8 s avant le flash : montée + roulement, impact au flash
  appel à l'action     : groove complet + motif de cloches, accord final, fondu de sortie
La musique est creusée sous la voix off (baisse dynamique sur 3 bandes pilotée par l'enveloppe de la voix).
Usage : python tools/music.py   (numpy, scipy, soundfile)
"""
import json
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal

ROOT = Path(__file__).resolve().parent.parent
SR = 44100
BPM = 120
BEAT = 60 / BPM
BAR = 4 * BEAT
TIMING = json.loads((ROOT / "tools" / "timing.json").read_text())  # calage commun avec index.html
TOTAL = TIMING["total"]
N = int(TOTAL * SR)
# Placement des voix off (doit correspondre aux <audio id="vo-xx"> de index.html).
VO_STARTS = TIMING["vo"]
BAC_HIT = TIMING["bac_hit"]  # « Bac ? » arrive à l'écran
MAP = TIMING["map"]  # carte vue du ciel (fin de la poussée)
CTA = TIMING["cta"]  # flash blanc → appel à l'action
rng = np.random.default_rng(2026)

mtof = lambda m: 440.0 * 2 ** ((m - 69) / 12)


def buf():
    return np.zeros((N, 2))


def add(dst, x, t0, gain=1.0, pan=0.0):
    i0 = int(round(t0 * SR))
    if i0 >= N or i0 < 0:
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
def pluck(f, dur=0.5, decay=9.0):
    t = tt(dur)
    y = np.sign(np.sin(2 * np.pi * f * t)) * 0.25 + np.sin(2 * np.pi * f * t)
    y += 0.3 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 14)
    sos = signal.butter(2, min(6000, f * 7), btype="low", fs=SR, output="sos")
    return signal.sosfilt(sos, y) * np.exp(-t * decay) * attack(t, 0.002)


def bell(f, dur=1.8):
    t = tt(dur)
    y = np.sin(2 * np.pi * f * t) * np.exp(-t * 2.2)
    y += 0.35 * np.sin(2 * np.pi * 2.756 * f * t) * np.exp(-t * 4.5)
    y += 0.14 * np.sin(2 * np.pi * 5.404 * f * t) * np.exp(-t * 8)
    return y * attack(t, 0.002)


def pad_voice(f, dur, a=0.4, r=0.5):
    t = tt(dur + r)
    y = np.zeros_like(t)
    for det in (-0.005, 0.0, 0.005):
        ff = f * (1 + det)
        for n in range(1, 7):
            y += (0.5**n) / n * np.sin(2 * np.pi * n * ff * t + n * det * 30)
    env = np.minimum(np.clip(t / a, 0, 1), np.clip((dur + r - t) / r, 0, 1))
    return y * env


def bass(f, dur):
    t = tt(dur + 0.03)
    y = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) + 0.12 * np.sin(2 * np.pi * 3 * f * t)
    env = attack(t, 0.004) * (0.5 + 0.5 * np.exp(-t * 7)) * np.clip((dur + 0.03 - t) / 0.03, 0, 1)
    return y * env


def kick():
    t = tt(0.35)
    ph = 2 * np.pi * np.cumsum(50 + 90 * np.exp(-t * 35)) / SR
    return np.sin(ph) * np.exp(-t * 9) * attack(t, 0.002)


def bandnoise(dur, lo, hi, decay):
    t = tt(dur)
    x = rng.standard_normal(len(t))
    sos = signal.butter(2, [lo, hi], btype="band", fs=SR, output="sos")
    return signal.sosfilt(sos, x) * np.exp(-t * decay)


def hat(open_=False):
    return bandnoise(0.25 if open_ else 0.06, 7000, 15000, 14 if open_ else 70)


def clap():
    y = np.zeros(int(0.3 * SR))
    for k, g in ((0, 1.0), (0.011, 0.75), (0.022, 0.55)):
        b = bandnoise(0.25, 900, 4000, 20) * g
        i = int(k * SR)
        y[i : i + len(b)] += b[: len(y) - i]
    return y


def snare_tick():
    return bandnoise(0.12, 1500, 6000, 35)


def impact(dur=1.6):
    t = tt(dur)
    ph = 2 * np.pi * np.cumsum(38 + 60 * np.exp(-t * 18)) / SR
    boom = np.sin(ph) * np.exp(-t * 3.2)
    crash = bandnoise(dur, 3000, 12000, 3.5) * 0.35
    return (boom + crash) * attack(t, 0.002)


def riser(dur):
    t = tt(dur)
    x = rng.standard_normal(len(t))
    out = np.zeros_like(x)
    seg = int(0.05 * SR)
    for i in range(0, len(x), seg):
        k = i / len(x)
        fc = 500 + 8000 * k**2
        sos = signal.butter(2, [fc * 0.7, min(fc * 1.4, SR / 2 - 100)], btype="band", fs=SR, output="sos")
        out[i : i + seg] = signal.sosfilt(sos, x[i : i + seg])
    return out * (t / dur) ** 2


def swoosh(dur=0.45):
    t = tt(dur)
    x = rng.standard_normal(len(t))
    out = np.zeros_like(x)
    seg = int(0.02 * SR)
    for i in range(0, len(x), seg):
        k = i / len(x)
        fc = 900 + 5000 * np.sin(np.pi * k)
        sos = signal.butter(2, [fc * 0.6, min(fc * 1.6, SR / 2 - 100)], btype="band", fs=SR, output="sos")
        out[i : i + seg] = signal.sosfilt(sos, x[i : i + seg])
    return out * np.sin(np.pi * t / dur) ** 2


# ── harmonie : Am – F – C – G ───────────────────────────────────────────────
CH = {
    "Am": dict(bass=45, pad=[57, 60, 64, 69], arp=[69, 72, 76, 81]),
    "F": dict(bass=41, pad=[57, 60, 65, 69], arp=[69, 72, 77, 81]),
    "C": dict(bass=48, pad=[55, 60, 64, 67], arp=[67, 72, 76, 79]),
    "G": dict(bass=43, pad=[55, 59, 62, 67], arp=[67, 71, 74, 79]),
}
LOOP = ["Am", "F", "C", "G"]
NB = int(TOTAL / BAR)  # 14 mesures


def build():
    pad, arp, bas, drm, bel, fx = buf(), buf(), buf(), buf(), buf(), buf()
    for b in range(NB):
        name = "Am" if b == NB - 1 else LOOP[b % 4]
        c = CH[name]
        t0 = b * BAR
        last = b == NB - 1
        dur = TOTAL - t0 if last else BAR
        for k, m in enumerate(c["pad"]):
            add(pad, pad_voice(mtof(m), dur, a=0.9 if b == 0 else 0.3, r=1.2 if last else 0.4), t0, 0.12, pan=-0.5 + k / 3)
        for s in range(16 if not last else 8):
            t = t0 + s * BEAT / 4
            if t < 3.0 - 1e-6:
                # accroche : arpège clairsemé (croches)
                if s % 2 == 0:
                    add(arp, pluck(mtof(c["arp"][(s // 2) % 4]), 0.6, 6), t, 0.1, pan=0.3 if s % 4 else -0.3)
                continue
            # groove : arpège en doubles croches
            p = [0, 2, 1, 3][s % 4]
            acc = 1.0 if s % 4 == 0 else 0.6
            add(arp, pluck(mtof(c["arp"][p] + (12 if s % 8 == 7 else 0))), t, 0.075 * acc, pan=0.35 if s % 2 else -0.3)
        # basse pulsée en croches à partir de la marque
        if t0 + BAR > 3.0:
            for e in range(8 if not last else 4):
                t = t0 + e * BEAT / 2
                if t < 3.0 - 1e-6:
                    continue
                add(bas, bass(mtof(c["bass"]), BEAT / 2 * 0.85), t, 0.3 if e % 2 == 0 else 0.22)
        if last:
            add(bas, bass(mtof(c["bass"]), dur - 0.2), t0 + 2 * BEAT, 0.3)
        # batterie
        for beat in range(4):
            t = t0 + beat * BEAT
            if t < 3.0 - 1e-6 or (last and beat >= 2):
                continue
            airborne = MAP <= t < CTA
            if not airborne:
                add(drm, kick(), t, 0.42)
                if t >= 6.0 and beat in (1, 3):
                    add(drm, clap(), t, 0.16, pan=0.1)
            for h in range(2):
                th = t + h * BEAT / 2
                add(drm, hat(open_=h == 1 and beat == 3), th, 0.05 if h == 0 else 0.07, pan=0.4)
    # accroche : impact sur « Bac ? »
    add(fx, impact(1.6), BAC_HIT, 0.22)
    # montée vers la marque et souffles de transition (pinceau, poussées)
    add(fx, riser(1.2), 3.0 - 1.2, 0.05)
    for t in TIMING["transitions"]:
        add(fx, swoosh(0.45), t, 0.07, pan=-0.3)
    # carte : long souffle montant pendant le vol
    add(fx, riser(CTA - MAP - 0.1), MAP, 0.035, pan=0.2)
    # montée + roulement vers l'appel à l'action, impact au flash
    add(fx, riser(0.8), CTA - 0.8, 0.08)
    for i in range(8):
        add(drm, snare_tick(), CTA - 0.8 + i * 0.1, 0.05 + 0.012 * i, pan=0.1)
    add(fx, impact(2.2), CTA, 0.25)
    # appel à l'action : motif de cloches (une note par temps)
    motif = [81, 79, 76, 79, 81, 84, 83, 79, 76, 77, 79, 76]
    for i, m in enumerate(motif):
        add(bel, bell(mtof(m)), CTA + 0.1 + i * BEAT, 0.06, pan=0.25)
    for k, m in enumerate([69, 72, 76, 81]):
        add(bel, bell(mtof(m + 12), 2.5), TOTAL - 3.0 + k * 0.08, 0.05, pan=-0.4 + k * 0.25)
    return pad, arp, bas, drm, bel, fx


def reverb(x, seconds=1.6, seed=5):
    r = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = r.standard_normal((n, 2)) * np.exp(-t / (seconds / 6.9))[:, None]
    sos = signal.butter(1, 5500, btype="low", fs=SR, output="sos")
    ir = signal.sosfilt(sos, ir, axis=0)
    ir /= np.sqrt((ir**2).sum(axis=0))
    return np.stack([signal.fftconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], axis=1)


def vo_envelope():
    env = np.zeros(N)
    for vid, t0 in VO_STARTS.items():
        y, sr = sf.read(ROOT / "assets" / "vo" / f"vo-{vid}.wav")
        if y.ndim > 1:
            y = y.mean(axis=1)
        y = signal.resample_poly(y, SR, sr)
        i0 = int(t0 * SR)
        y = np.abs(y[: N - i0])
        env[i0 : i0 + len(y)] = np.maximum(env[i0 : i0 + len(y)], y)
    win = int(0.03 * SR)
    rms = np.sqrt(np.convolve(env**2, np.ones(win) / win, mode="same"))
    gate = (rms > 0.02).astype(float)
    out = np.zeros_like(gate)
    a, r = np.exp(-1 / (0.05 * SR)), np.exp(-1 / (0.3 * SR))
    g = 0.0
    for i in range(0, N, 32):
        target = gate[i]
        coef = a if target > g else r
        g = target + (g - target) * coef**32
        out[i : i + 32] = g
    return out


def main():
    pad, arp, bas, drm, bel, fx = build()
    dry = pad + arp + bas + drm + bel + fx
    wet = reverb(pad * 0.5 + arp + bel * 1.2 + fx * 0.5 + drm * 0.1)
    mix = dry + 0.22 * wet
    mix = signal.sosfilt(signal.butter(2, 30, btype="high", fs=SR, output="sos"), mix, axis=0)
    # creusée sous la voix off : baisse dynamique sur 3 bandes
    e = vo_envelope()[:, None]
    lo = signal.sosfiltfilt(signal.butter(2, 220, btype="low", fs=SR, output="sos"), mix, axis=0)
    hi = signal.sosfiltfilt(signal.butter(2, 4500, btype="high", fs=SR, output="sos"), mix, axis=0)
    mid = mix - lo - hi
    carved = lo * (1 - 0.35 * e) + mid * (1 - 0.7 * e) + hi * (1 - 0.45 * e)
    # niveau : fond à ≈ -27 dBFS RMS (voix off ≈ -19 dBFS)
    rms = np.sqrt(np.mean(carved**2))
    carved *= 10 ** (-27 / 20) / rms
    # fondu d'entrée court, fondu de sortie sur les 1,6 dernières secondes
    t = np.arange(N) / SR
    carved *= np.clip(t / 0.05, 0, 1)[:, None] * np.clip((TOTAL - t) / 1.6, 0, 1)[:, None]
    carved = np.tanh(carved * 1.3) / 1.3
    out = ROOT / "assets" / "music" / "alpha-square-bed.wav"
    out.parent.mkdir(parents=True, exist_ok=True)
    sf.write(out, carved.astype(np.float32), SR, subtype="PCM_16")
    print(out.relative_to(ROOT), f"{len(carved) / SR:.2f}s", "peak", f"{20 * np.log10(np.abs(carved).max()):.1f} dBFS")


main()
