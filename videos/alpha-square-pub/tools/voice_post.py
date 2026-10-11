"""Post-traitement de la voix off (Kokoro ff_siwis) : intonation de question + chaleur.

- vo-00 « Prêt pour ton Bac ? » : Kokoro le lit avec une intonation descendante (affirmation).
  On remplace la fin de la courbe de hauteur par une montée de question sur « Bac »
  (analyse/resynthèse WORLD) et on allonge légèrement la dernière syllabe.
- Toutes les lignes : passe-haut, un peu de chaleur, aigus adoucis, compression légère,
  pour un rendu moins synthétique.

Entrées : assets/vo/raw/vo-XX.wav (sortie brute de `hyperframes tts`).
Sorties : assets/vo/vo-XX.wav.
Usage : python tools/voice_post.py   (numpy, soundfile, pyworld ; ffmpeg dans le PATH)
"""
import subprocess
import warnings
from pathlib import Path

import numpy as np
import soundfile as sf

warnings.filterwarnings("ignore", category=UserWarning)
import pyworld as pw  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "assets" / "vo" / "raw"
OUT = ROOT / "assets" / "vo"
FRAME = 5.0  # ms

# « Bac » commence vers 0,58 s dans vo-00 (mesuré sur la sortie brute).
BAC_START, BAC_END = 0.58, 1.02
F0_FROM, F0_TO = 222.0, 355.0  # montée d'environ 8 demi-tons sur la dernière syllabe
STRETCH = 1.18  # « Bac » un peu plus long, comme dans une vraie question

CHAIN = (
    "highpass=f=85,"
    "equalizer=f=210:t=q:w=1.0:g=2,"
    "equalizer=f=3200:t=q:w=1.2:g=-1.5,"
    "equalizer=f=7500:t=q:w=1.5:g=-3,"
    "acompressor=threshold=-22dB:ratio=2.5:attack=6:release=90:makeup=1.88,"
    "alimiter=limit=0.89:level=disabled"
)


def question(src, dst):
    x, fs = sf.read(src)
    x = x.astype(np.float64)
    f0, t = pw.harvest(x, fs, frame_period=FRAME, f0_floor=110, f0_ceil=520)
    sp = pw.cheaptrick(x, f0, t, fs)
    ap = pw.d4c(x, f0, t, fs)
    # nouvelle courbe : montée lissée sur « Bac »
    f0n = f0.copy()
    for i, ti in enumerate(t):
        if f0[i] <= 0 or ti < BAC_START - 0.1:
            continue
        if ti < BAC_START:  # transition douce vers le début de la montée
            k = (ti - (BAC_START - 0.1)) / 0.1
            f0n[i] = f0[i] * (1 - k) + F0_FROM * k
        else:
            u = min(1.0, (ti - BAC_START) / (BAC_END - BAC_START))
            f0n[i] = F0_FROM * (F0_TO / F0_FROM) ** (u**1.25)
    # allongement de la dernière syllabe (rééchantillonnage des trames)
    n = len(t)
    i0 = int(BAC_START * 1000 / FRAME)
    tail = np.arange(i0, n)
    new_len = int(len(tail) * STRETCH)
    src_idx = np.concatenate([np.arange(i0), i0 + np.linspace(0, len(tail) - 1, new_len)])
    lo = np.floor(src_idx).astype(int)
    hi = np.minimum(lo + 1, n - 1)
    w = (src_idx - lo)[:, None]
    sp2 = sp[lo] * (1 - w) + sp[hi] * w
    ap2 = ap[lo] * (1 - w) + ap[hi] * w
    f02 = np.where((f0n[lo] > 0) & (f0n[hi] > 0), f0n[lo] * (1 - w[:, 0]) + f0n[hi] * w[:, 0], 0.0)
    y = pw.synthesize(np.ascontiguousarray(f02), np.ascontiguousarray(sp2), np.ascontiguousarray(ap2), fs, FRAME)
    y = y / max(1e-9, np.abs(y).max()) * np.abs(x).max()
    sf.write(dst, y.astype(np.float32), fs, subtype="PCM_16")


def polish(src, dst):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-af", CHAIN, "-ar", "24000", "-ac", "1", str(dst)], check=True)


def main():
    tmp = RAW / "_vo-00-question.wav"
    question(RAW / "vo-00.wav", tmp)
    for src in sorted(RAW.glob("vo-*.wav")):
        polish(tmp if src.name == "vo-00.wav" else src, OUT / src.name)
    tmp.unlink()
    for f in sorted(OUT.glob("vo-*.wav")):
        info = sf.info(f)
        print(f"{f.relative_to(ROOT)}  {info.duration:.3f} s")


main()
