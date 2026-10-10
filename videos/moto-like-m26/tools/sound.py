"""M26 sound bed: synthesized electronic music + Pixabay SFX, carved under the voice-over.

A minor, 120 BPM, beat grid anchored on the photo reveal (3.0 s):
  0.0–3.0   intro: sub drone + noise swell into the reveal impact
  3.0–6.5   kick + bass + pad
  6.5–20.0  full groove: kick, clap, hats, pumped bass, 16th pluck arp
  20.0–28.0 breakdown under the calculation (no kick)
  28.0–37.0 groove back, one tick per equipment beat
  37.0–39.0 build: snare roll + riser
  39.0      hard stop on the freeze, held pad under « moins d'un rial »
  41.5–43.5 soft groove return
  43.5–49.5 warm chords at sunset, resolve and ring out
usage: python3 tools/sound.py  ->  assets/music/m26-bed.wav (+ /tmp preview mix with VO)
"""
import json
import numpy as np
import soundfile as sf
from scipy import signal

SR = 44100
TOTAL = 49.5
N = int(TOTAL * SR)
BEAT = 0.5
T0 = 3.0
rng = np.random.default_rng(26)
mtof = lambda m: 440.0 * 2 ** ((m - 69) / 12)
VO = [(0.3, 1), (6.7, 2), (13.1, 3), (20.6, 4), (28.2, 5), (39.1, 6), (44.0, 7)]


def tt(d):
    return np.arange(int(d * SR)) / SR


def add(dst, x, t0, g=1.0, pan=0.0):
    i0 = int(round(t0 * SR))
    if i0 >= N or i0 + len(x) <= 0:
        return
    if i0 < 0:
        x = x[-i0:]; i0 = 0
    x = x[: N - i0]
    if x.ndim == 1:
        l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        dst[i0:i0 + len(x), 0] += x * g * l * 1.414
        dst[i0:i0 + len(x), 1] += x * g * r * 1.414
    else:
        dst[i0:i0 + len(x)] += x * g


def lp(x, fc, order=2):
    b, a = signal.butter(order, fc / (SR / 2), "low")
    return signal.lfilter(b, a, x, axis=0)


def hp(x, fc, order=2):
    b, a = signal.butter(order, fc / (SR / 2), "high")
    return signal.lfilter(b, a, x, axis=0)


def bp(x, f1, f2):
    b, a = signal.butter(2, [f1 / (SR / 2), f2 / (SR / 2)], "band")
    return signal.lfilter(b, a, x, axis=0)


# ── instruments ──────────────────────────────────────────────────────────────
def kick():
    t = tt(0.42)
    f = 48 + 120 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 7.5) * np.clip(t / 0.002, 0, 1)


def clap():
    t = tt(0.25)
    n = bp(rng.standard_normal(len(t)), 900, 3200)
    env = np.exp(-t * 22) * (1 + 0.6 * (np.sin(2 * np.pi * 90 * t) > 0) * (t < 0.03))
    return n * env * 0.6


def hat(open_=False):
    t = tt(0.22 if open_ else 0.06)
    n = hp(rng.standard_normal(len(t)), 7000)
    return n * np.exp(-t * (14 if open_ else 70)) * 0.35


def snare():
    t = tt(0.16)
    n = bp(rng.standard_normal(len(t)), 1500, 6000) * np.exp(-t * 30)
    return (n + 0.4 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 40)) * 0.5


def saw(f, t):
    return 2 * ((f * t) % 1.0) - 1


def pad(notes, dur, a=0.8, r=1.2, cut=1800):
    t = tt(dur + r)
    y = np.zeros_like(t)
    for m in notes:
        for det in (-0.09, 0.0, 0.08):
            y += saw(mtof(m + det), t)
    env = np.clip(t / a, 0, 1) * np.where(t > dur, np.exp(-(t - dur) * 3.5), 1)
    return lp(y / (3 * len(notes)), cut) * env


def pluck(m, dur=0.35, cut=2600):
    t = tt(dur)
    y = saw(mtof(m), t) * 0.6 + np.sin(2 * np.pi * mtof(m) * t)
    return lp(y * np.exp(-t * 11), cut) * np.clip(t / 0.003, 0, 1)


def bass(m, dur):
    t = tt(dur)
    y = np.sin(2 * np.pi * mtof(m) * t) + 0.35 * saw(mtof(m), t)
    return lp(y, 420) * np.exp(-t * 2.5) * np.clip(t / 0.005, 0, 1)


def bar_chord(k):
    # Am  F  C  G  (root midi, chord tones)
    return [(45, [57, 60, 64]), (41, [57, 60, 65]), (48, [55, 60, 64]), (43, [55, 59, 62])][k % 4]


music = np.zeros((N, 2))
kick_times = []

# intro drone + swell
t = tt(3.2)
drone = (np.sin(2 * np.pi * 55 * t) + 0.5 * np.sin(2 * np.pi * 110.3 * t)) * np.clip(t / 2.2, 0, 1) * 0.5
add(music, lp(drone, 300), 0.0, 0.55)
sw = lp(rng.standard_normal(int(2.9 * SR)), 2500) * np.linspace(0, 1, int(2.9 * SR)) ** 2
add(music, hp(sw, 300), 0.1, 0.18)

def in_any(x, spans):
    return any(a <= x < b for a, b in spans)

KICK = [(3.0, 20.0), (28.0, 39.0), (41.5, 43.5)]
CLAP = [(6.5, 20.0), (28.0, 37.0)]
HATS = [(6.5, 39.0), (41.5, 43.5)]
ARP = [(6.5, 39.0)]
BASS = [(3.0, 39.0), (41.5, 43.5)]

for i in range(int((TOTAL - T0) / BEAT)):
    tb = T0 + i * BEAT
    bar = int((tb - T0) // 2.0)
    root, tones = bar_chord(bar)
    if in_any(tb, KICK):
        add(music, kick(), tb, 0.75); kick_times.append(tb)
    if in_any(tb, CLAP) and i % 2 == 1:
        add(music, clap(), tb, 0.45, 0.05)
    if in_any(tb + 0.25, HATS):
        add(music, hat(i % 4 == 3), tb + 0.25, 0.5, 0.3)
    if in_any(tb, BASS):
        for s in (0.0, 0.25):
            add(music, bass(root - 12 if s == 0 else root, 0.24), tb + s, 0.42)
    if in_any(tb, ARP):
        for s in range(4):
            m = tones[(i * 4 + s) % 3] + (12 if (i + s) % 5 == 0 else 0)
            add(music, pluck(m), tb + s * 0.125, 0.16, -0.35 + 0.7 * ((s % 2)))

# breakdown hats (soft) and plucks under the calculation
for i in range(16):
    tb = 20.0 + i * BEAT
    add(music, hat(), tb + 0.25, 0.25, 0.3)
# pads, bar by bar
for bar in range(int((TOTAL - T0) / 2.0) + 1):
    tb = T0 + bar * 2.0
    if tb >= 39.0 and tb < 43.5:
        continue
    root, tones = bar_chord(bar)
    g = 0.14 if 20.0 <= tb < 28.0 else 0.1
    add(music, pad(tones, 2.0, a=0.4, r=0.6, cut=1600 if tb < 43.5 else 2400), tb, g)
# build: snare roll + filtered noise
for k in range(32):
    tk = 37.0 + 2.0 * (1 - (1 - k / 32) ** 1.6)
    add(music, snare(), tk, 0.12 + 0.25 * k / 32, 0.1)
for j, ch in enumerate([[53, 57, 60, 64], [55, 59, 62, 67], [57, 60, 64, 69], [60, 64, 67, 72]]):
    add(music, pad(ch, 1.5, a=0.3, r=1.6 if j == 3 else 0.5, cut=2600), 43.5 + j * 1.5, 0.22)
for j, m in enumerate([69, 72, 76, 74, 72, 76, 79, 81]):
    add(music, pluck(m, 0.9, 3200), 43.75 + j * 0.75, 0.18, -0.3 + 0.6 * (j % 2))

# sidechain pump on everything but the kick (bass + pad breathe with the kick)
pump = np.ones(N)
for kt in kick_times:
    i0 = int(kt * SR); L = int(0.22 * SR)
    seg = 1 - 0.5 * np.exp(-np.arange(L) / SR * 18)
    pump[i0:i0 + L] = np.minimum(pump[i0:i0 + L], seg[: max(0, min(L, N - i0))])
music *= pump[:, None] ** 0.6
# hard stop at the freeze
gate = np.ones(N)
i39 = int(39.0 * SR)
gate[i39 - int(0.02 * SR):i39] = np.linspace(1, 0, int(0.02 * SR))
gate[i39:int(41.5 * SR)] = 0

# ── SFX (Pixabay library) ────────────────────────────────────────────────────
def load(name):
    x, sr = sf.read(f"assets/sfx/{name}.mp3", always_2d=True)
    if x.shape[1] == 1:
        x = np.repeat(x, 2, axis=1)
    if sr != SR:
        g = np.gcd(sr, SR)
        x = signal.resample_poly(x, SR // g, sr // g, axis=0)
    return x

C = {}
def sfx(name, t0, g):
    if name not in C:
        C[name] = load(name)
    add(fx, C[name], t0, g)

fx = np.zeros((N, 2))
for t0, n, g in [
    (0.12, "click-soft", 0.25), (0.3, "click-soft", 0.2), (0.25, "sparkle", 0.28), (2.95, "impact-bass-1", 0.55),
    (4.1, "whoosh-short", 0.38), (4.5, "ping", 0.22), (4.66, "click", 0.32), (4.96, "click", 0.32), (5.26, "click", 0.36),
    (5.4, "whoosh", 0.18), (6.2, "whoosh", 0.32), (7.8, "glitch-2", 0.1), (9.95, "whoosh-short", 0.34),
    (12.7, "whoosh", 0.28), (13.1, "sparkle", 0.18), (14.0, "whoosh-short", 0.24),
    (15.2, "ping", 0.12), (15.48, "ping", 0.12), (15.76, "ping", 0.13), (16.04, "ping", 0.14), (16.3, "pop", 0.3),
    (17.7, "whoosh-short", 0.14), (19.6, "impact-bass-2", 0.22), (19.6, "click", 0.32), (19.78, "whoosh", 0.22),
    (20.25, "click", 0.36), (22.2, "whoosh", 0.3), (22.5, "pop", 0.14), (22.62, "pop", 0.14), (22.74, "pop", 0.14), (22.86, "pop", 0.14),
    (23.55, "pop", 0.3), (25.25, "whoosh-short", 0.14), (25.6, "whoosh-short", 0.14), (26.05, "chime", 0.24), (27.75, "whoosh", 0.28),
    (28.1, "click-soft", 0.3), (29.05, "ping", 0.3), (30.2, "click-soft", 0.3), (30.5, "notification", 0.14), (31.45, "click-soft", 0.3),
    (31.65, "sparkle", 0.16), (32.4, "click-soft", 0.3), (33.1, "click-soft", 0.3), (34.7, "click-soft", 0.3), (35.9, "click-soft", 0.3),
    (36.78, "whoosh-short", 0.36), (37.0, "riser", 0.0), (38.98, "impact-bass-1", 0.4),
    (39.1, "chime", 0.34), (39.42, "ping", 0.12), (39.62, "ping", 0.08), (41.45, "whoosh-short", 0.2),
    (43.15, "whoosh-short", 0.3), (44.0, "sparkle", 0.24), (44.8, "ping", 0.2), (46.05, "whoosh", 0.18), (46.85, "click-soft", 0.22),
]:
    if g > 0:
        sfx(n, t0, g)
# riser into the freeze: take the last 2.2 s of the riser so it peaks at 39.0
if "riser" not in C:
    C["riser"] = load("riser")
r = C["riser"]
seg = r[-int(2.2 * SR):]
add(fx, seg * np.linspace(0.2, 1, len(seg))[:, None], 36.8, 0.32)

# synthesized electric details: motor whine (X-ray), road hum (rides), charge hum
def whine(d, f0, f1):
    t = tt(d)
    f = f0 + (f1 - f0) * (t / d) ** 0.8
    ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) + 0.3 * np.sin(2 * ph)) * np.clip(t / 0.3, 0, 1) * np.clip((d - t) / 0.3, 0, 1)
add(fx, whine(1.8, 220, 900), 8.4, 0.05)
add(fx, whine(2.9, 520, 640), 10.0, 0.035)
add(fx, whine(1.9, 300, 760), 20.8, 0.04)
add(fx, whine(2.0, 560, 820), 37.0, 0.035)
for t0, d in [(10.0, 2.9), (37.0, 2.0)]:
    n = lp(rng.standard_normal(int(d * SR)), 900)
    add(fx, n * np.clip(tt(d) / 0.3, 0, 1) * np.clip((d - tt(d)) / 0.1, 0, 1), t0, 0.1)

# ── carve the music under the voice-over ──────────────────────────────────────
env = np.zeros(N)
for t0, k in VO:
    v, sr = sf.read(f"assets/vo/vo-{k:02d}.wav")
    i0 = int(t0 * SR)
    a = np.abs(v)
    env[i0:i0 + len(a)] = np.maximum(env[i0:i0 + len(a)], a[: N - i0])
env = signal.filtfilt(*signal.butter(1, 4 / (SR / 2)), env)
env = np.clip(env / (np.percentile(env[env > 0.01], 90) + 1e-9), 0, 1)
duck = 1 - 0.72 * env
music *= (duck * gate)[:, None]
# held pad under the line (Am add9), added after the hard stop
held = np.zeros((N, 2))
add(held, pad([57, 60, 64, 71], 2.6, a=0.15, r=1.0, cut=2000), 39.0, 0.13)
music += held * duck[:, None]

fx_duck = 1 - 0.45 * env
bed = music * 0.55 + fx * 0.6 * fx_duck[:, None]
peak = np.max(np.abs(bed))
bed *= 0.89 / peak if peak > 0.89 else 1.0
fade = int(0.8 * SR)
bed[-fade:] *= np.linspace(1, 0, fade)[:, None]
sf.write("assets/music/m26-bed.wav", bed.astype(np.float32), SR, subtype="PCM_16")

# preview mix (voice + bed) for a listening check
mix = bed.copy()
for t0, k in VO:
    v, _ = sf.read(f"assets/vo/vo-{k:02d}.wav")
    add(mix, v, t0, 1.0)
mix *= 0.95 / np.max(np.abs(mix))
sf.write("/tmp/m26-preview-mix.wav", mix.astype(np.float32), SR)
print("bed ok", round(len(bed) / SR, 2), "s, peak", round(float(np.max(np.abs(bed))), 3))
