#!/usr/bin/env python3
"""Cut the person's own narration into the 30 phrases of script.json -> assets/voice/ph/<id>.wav.

  python3 tools/recording.py <file> [<file> ...]   # one take for everything, or one file per scene (in order)

Cleans each file (80 Hz high-pass, light denoise, loudness to -16 LUFS), finds speech between pauses
(threshold from the file's own noise floor), then groups consecutive speech runs into the phrases by
dynamic programming on expected length (characters × the speaker's own rate). A retake shows up as a
group far longer than expected: the report flags it so the take can be checked.
Then run tools/voice.py to lay out the film.
"""
import json, subprocess, sys, wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SR = 44100
SCRIPT = json.loads((ROOT / "script.json").read_text())
PHRASES = [p for sc in SCRIPT["scenes"] for p in sc["phrases"]]
OUT = ROOT / "assets/voice/ph"
OUT.mkdir(parents=True, exist_ok=True)


def load(path):
    clean = ROOT / f"assets/voice/clean-{Path(path).stem}.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-ac", "1", "-ar", str(SR), "-af",
                    "highpass=f=80,afftdn=nf=-28,loudnorm=I=-16:TP=-1.5:LRA=11", str(clean)], check=True)
    with wave.open(str(clean)) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float32) / 32768
    return x


def runs(x, min_gap=0.55, min_len=0.12):
    hop = int(0.02 * SR)
    fr = x[: len(x) // hop * hop].reshape(-1, hop)
    db = 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-9)
    floor = np.percentile(db, 10)
    thr = max(floor + 14, np.percentile(db, 60) - 22)
    on = db > thr
    segs, i = [], 0
    while i < len(on):
        if on[i]:
            j = i
            while j < len(on) and on[j]:
                j += 1
            segs.append([i * 0.02, j * 0.02]); i = j
        else:
            i += 1
    merged = []
    for a, b in segs:
        if merged and a - merged[-1][1] < min_gap:
            merged[-1][1] = b
        else:
            merged.append([a, b])
    return [s for s in merged if s[1] - s[0] >= min_len], thr


def group(segs, phrases):
    """Split consecutive speech runs into len(phrases) groups, lengths close to expectation."""
    n, m = len(phrases), len(segs)
    if m < n:
        raise SystemExit(f"only {m} speech runs for {n} phrases: the pauses between lines are too short")
    chars = np.array([len(p["text"].replace(" ", "")) for p in phrases], float)
    speech = sum(b - a for a, b in segs)
    rate = speech / chars.sum()
    exp = chars * rate
    INF = 1e18
    cost = np.full((n + 1, m + 1), INF); back = np.zeros((n + 1, m + 1), int)
    cost[0, 0] = 0
    for i in range(1, n + 1):
        for j in range(i, m - (n - i) + 1):
            for k in range(i - 1, j):
                if cost[i - 1, k] >= INF:
                    continue
                d = segs[j - 1][1] - segs[k][0]
                c = cost[i - 1, k] + np.log(d / exp[i - 1]) ** 2
                if c < cost[i, j]:
                    cost[i, j], back[i, j] = c, k
    out, j = [], m
    for i in range(n, 0, -1):
        k = back[i, j]; out.append((k, j)); j = k
    return out[::-1], exp


files = sys.argv[1:]
if not files:
    raise SystemExit(__doc__)
if len(files) == 1:
    sets = [(files[0], PHRASES)]
else:
    sets = [(f, sc["phrases"]) for f, sc in zip(files, SCRIPT["scenes"])]
report = []
for f, phrases in sets:
    x = load(f)
    segs, thr = runs(x)
    groups, exp = group(segs, phrases)
    for p, (k, j), e in zip(phrases, groups, exp):
        a, b = segs[k][0], segs[j - 1][1]
        a0, b0 = max(0, int((a - 0.06) * SR)), min(len(x), int((b + 0.12) * SR))
        y = x[a0:b0].copy()
        fade = int(0.01 * SR)
        y[:fade] *= np.linspace(0, 1, fade); y[-fade:] *= np.linspace(1, 0, fade)
        with wave.open(str(OUT / f"{p['id']}.wav"), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())
        ratio = (b - a) / e
        report.append(f"{p['id']}  {a:7.2f}–{b:7.2f}  {b - a:5.2f}s  x{ratio:4.2f}{'  CHECK' if ratio > 1.6 or ratio < 0.55 else ''}  {p['text'][:48]}")
    print(f"{Path(f).name}: {len(segs)} speech runs -> {len(phrases)} phrases (threshold {thr:.1f} dB)")
print("\n".join(report))
