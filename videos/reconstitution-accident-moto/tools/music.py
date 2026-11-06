#!/usr/bin/env python3
"""Musique de reconstitution-accident-moto (déterministe, libre de droits, numpy seul).

Identité de la marque (brand/BRAND.md) : 90 BPM, ré mineur, Dm – B♭ – F – C, deux mesures par accord,
mêmes instruments que compteur-vespa-13 (piano électrique FM, nappe, basse ronde, kalimba).
Ton calme et factuel : pas de batterie.

  0–3 s     nappe + piano (plongée)
  3–10,6 s  piano, nappe, basse douce (approche)
  10,6–11,5 la musique se retire, souffle filtré qui monte
  11,5 s    contact : impact grave étouffé, accord suspendu tenu pendant le ralenti
  12,3–20 s nappe et piano clairsemé (chute, vue d'ensemble)
  20–25 s   accord final de Dm9 sous la fiche de synthèse, fondu

  python3 tools/music.py
"""
import subprocess
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SR = 44100
rng = np.random.default_rng(20261106)
mtof = lambda m: 440.0 * 2 ** ((m - 69) / 12)
TOTAL = 25.0
N = int(TOTAL * SR) + 1
T = np.arange(N) / SR
BEAT = 60 / 90
BAR = 4 * BEAT
ACCORDS = [
    (38, [53, 57, 60, 64]),  # Dm9
    (34, [53, 57, 58, 62]),  # B♭maj7
    (41, [55, 57, 60, 64]),  # Fmaj9
    (36, [55, 60, 62, 64]),  # Cadd9
]
RETRAIT, CONTACT, REPRISE, FINAL = 10.6, 11.5, 12.3, 20.0

# ---------------------------------------------------------------------------
# Pistes (stéréo) et envoi vers la réverbération
pistes = {k: np.zeros((2, N)) for k in ("keys", "pad", "bass", "kal", "fx")}
ENVOI = {"keys": 0.3, "pad": 0.38, "bass": 0.0, "kal": 0.5, "fx": 0.35}
GAIN = {"keys": 0.26, "pad": 0.08, "bass": 0.30, "kal": 0.08, "fx": 0.45}


def place(piste, sig, t0, gain=1.0, pan=0.0):
    i0 = int(round(t0 * SR))
    if i0 >= N or len(sig) == 0:
        return
    sig = sig[: N - i0]
    g = gain * np.array([np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)]) * 2 ** 0.5
    pistes[piste][:, i0: i0 + len(sig)] += g[:, None] * sig[None, :]


def fft_filtre(x, reponse):
    """Filtre à phase nulle dans le domaine fréquentiel (reponse : fonction de la fréquence)."""
    X = np.fft.rfft(x, axis=-1)
    f = np.fft.rfftfreq(x.shape[-1], 1 / SR)
    return np.fft.irfft(X * reponse(f), n=x.shape[-1], axis=-1)


passe_bas = lambda fc, ordre=2: (lambda f: 1 / np.sqrt(1 + (f / fc) ** (2 * ordre)))
passe_haut = lambda fc, ordre=2: (lambda f: 1 / np.sqrt(1 + (fc / np.maximum(f, 1e-3)) ** (2 * ordre)))


def enveloppe(n, attaque, duree_tenue, relache, decroissance=None):
    t = np.arange(n) / SR
    env = np.minimum(1, t / max(attaque, 1e-4))
    if decroissance:
        env = env * np.exp(-t / decroissance)
    return env * np.clip((duree_tenue + relache - t) / relache, 0, 1)


# ---------------------------------------------------------------------------
# Instruments

def rhodes(midi, duree, vel):
    """Piano électrique : FM 1:1 à indice décroissant + « tine » aigu bref."""
    f = mtof(midi)
    n = int((duree + 0.5) * SR)
    t = np.arange(n) / SR
    indice = (1.1 * vel + 0.25) * np.exp(-t / 0.4) + 0.12
    s = np.sin(2 * np.pi * f * t + indice * np.sin(2 * np.pi * f * t))
    s += 0.10 * vel * np.sin(2 * np.pi * f * 7.0 * t) * np.exp(-t / 0.06)
    s *= enveloppe(n, 0.004, duree, 0.45, decroissance=2.4)
    return s * vel * (1.0 - 0.012 * (midi - 60))


def nappe(notes, duree):
    """Nappe : trois scies désaccordées par note, limitées en harmoniques (douce), attaque lente."""
    n = int((duree + 1.6) * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for m in notes:
        f0 = mtof(m)
        for d in (-0.004, 0.0, 0.0045):
            f = f0 * (1 + d)
            for k in range(1, 9):
                if f * k > 2400:
                    break
                s += np.sin(2 * np.pi * f * k * t + k * d * 40) / k * np.exp(-k * f / 1400)
    return s / len(notes) * enveloppe(n, 1.4, duree, 1.6)


def basse(midi, duree, vel):
    f = mtof(midi)
    n = int((duree + 0.08) * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.22 * np.sin(4 * np.pi * f * t) + 0.06 * np.sin(6 * np.pi * f * t)
    return s * enveloppe(n, 0.008, duree, 0.08, decroissance=1.1) * vel


def kalimba(midi, vel):
    f = mtof(midi)
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.0 * t) * np.exp(-t / 0.12)
    s += 0.12 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t / 0.03)
    return s * enveloppe(n, 0.002, 1.5, 0.1, decroissance=0.55) * vel



# ---------------------------------------------------------------------------
# Écriture
mesure = 0
while mesure * BAR < FINAL:
    t0 = mesure * BAR
    racine, voicing = ACCORDS[(mesure // 2) % 4]
    premiere = mesure % 2 == 0
    calme = t0 >= REPRISE - 0.01
    rythme = [(0.0, 2.6, 0.8), (2.5, 1.3, 0.42)] if premiere else [(0.5, 1.4, 0.45), (2.0, 1.8, 0.5)]
    if calme:
        rythme = rythme[:1]
    for b, d, v in rythme:
        tb = t0 + b * BEAT
        if RETRAIT - 0.3 <= tb < REPRISE or tb >= FINAL - 0.05:
            continue
        d = min(d * BEAT, FINAL - tb, max(0.2, RETRAIT - tb) if tb < RETRAIT else 9)
        for k, m in enumerate(voicing):
            place("keys", rhodes(m, d, v * (0.92 if k else 1.0)), tb + 0.011 * k, pan=(-0.35, -0.1, 0.12, 0.35)[k])
    if premiere:
        place("pad", nappe([racine + 12, racine + 19, voicing[1], voicing[3]], min(2 * BAR, FINAL - t0)), t0)
    if 3.0 <= t0 < RETRAIT - 0.5 or 15.5 <= t0 < FINAL:
        for b, d, v, m in [(0, 1.8, 0.8, racine), (2.0, 1.6, 0.55, racine + 7)]:
            if t0 + b * BEAT < RETRAIT - 0.2 or t0 >= 15.5:
                place("bass", basse(m, d * BEAT, v), t0 + b * BEAT)
    mesure += 1

# retrait avant le contact : souffle filtré qui monte, puis impact grave étouffé et accord suspendu
n = int(0.9 * SR); t = np.arange(n) / SR
souffle = fft_filtre(rng.standard_normal(n), passe_bas(1600)) * (t / t[-1]) ** 2.5
place("fx", souffle, CONTACT - 0.9, gain=0.18)
n = int(2.4 * SR); t = np.arange(n) / SR
boom = np.sin(2 * np.pi * np.cumsum(44 + 26 * np.exp(-t / 0.07)) / SR) * np.exp(-t / 0.55)
place("fx", boom, CONTACT + 0.033, gain=0.8)
for k, m in enumerate((50, 57, 62, 64)):
    place("keys", rhodes(m, 1.4, 0.45), CONTACT + 0.05 + 0.02 * k, pan=(-0.3, -0.1, 0.1, 0.3)[k])
place("pad", nappe([50, 57, 64], REPRISE - CONTACT + 1.0), CONTACT)
place("kal", kalimba(74, 0.55), CONTACT + 0.05, pan=-0.2)

# fin : accord de Dm9 tenu sous la fiche de synthèse
for k, m in enumerate((50, 57, 60, 64, 65, 69)):
    place("keys", rhodes(m, TOTAL - FINAL, 0.7), FINAL + 0.02 * k, pan=(-0.45, -0.25, -0.05, 0.1, 0.3, 0.45)[k])
place("pad", nappe([50, 57, 62, 65, 69], TOTAL - FINAL), FINAL)
place("bass", basse(38, TOTAL - FINAL, 0.7), FINAL)
for dt, m in ((1.0, 81), (1.75, 76), (2.5, 74)):
    place("kal", kalimba(m, 0.6), FINAL + dt, pan=-0.25)

# ---------------------------------------------------------------------------
# Mixage
trem = 0.12 * np.sin(2 * np.pi * 3.0 * T)
pistes["keys"] *= np.stack([1 + trem, 1 - trem])
pistes["bass"] = fft_filtre(pistes["bass"], passe_bas(900))
pistes["pad"] = fft_filtre(pistes["pad"], lambda f: passe_haut(180)(f) * passe_bas(2200)(f))
# la musique se retire pendant l'approche du contact, revient doucement après
retrait = 1 - 0.75 * np.clip((T - RETRAIT) / 0.5, 0, 1) * np.clip((REPRISE + 0.8 - T) / 0.8, 0, 1)
for k in ("keys", "pad", "bass", "kal"):
    pistes[k] *= retrait
sec_bus = sum(GAIN[k] * pistes[k] for k in pistes)
envoi = sum(GAIN[k] * ENVOI[k] * pistes[k] for k in pistes)
ni = int(2.2 * SR); ti = np.arange(ni) / SR
ir = rng.standard_normal((2, ni)) * np.exp(-ti / 0.38)
ir[:, : int(0.02 * SR)] = 0
ir = fft_filtre(ir, passe_bas(4500))
ir /= np.sqrt((ir ** 2).sum(axis=1, keepdims=True))
L = 1 << int(np.ceil(np.log2(N + ni)))
rev = np.fft.irfft(np.fft.rfft(envoi, L, axis=-1) * np.fft.rfft(ir, L, axis=-1), L, axis=-1)[:, :N]
mix = sec_bus + 0.55 * rev
mix = fft_filtre(mix, lambda f: passe_bas(9000, 1)(f) * passe_haut(30)(f))
mix *= np.clip((TOTAL - T) / 2.5, 0, 1) * np.clip(T / 0.4, 0, 1)
mix = np.tanh(mix / np.abs(mix).max() * 1.2) / np.tanh(1.2) * 0.5

wav = ROOT / "assets/music/fond.wav"
with wave.open(str(wav), "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(mix.T, -1, 1) * 32767).astype("<i2").tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wav), "-c:a", "aac", "-b:a", "192k", str(ROOT / "assets/music/fond.m4a")], check=True)
wav.unlink()
print(f"musique {TOTAL:.1f} s → assets/music/fond.m4a")
