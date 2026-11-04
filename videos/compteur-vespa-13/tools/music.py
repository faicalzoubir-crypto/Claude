#!/usr/bin/env python3
"""Musique de fond de compteur-vespa-13 (déterministe, libre de droits, numpy seul).

Deuxième version : la première (nappe + arpège en sinus + basse à chaque temps)
était jugée agaçante. Celle-ci est un groove « lo-fi » chaleureux :
piano électrique (synthèse FM type Rhodes) en accords enrichis, nappe douce,
basse ronde, batterie feutrée avec swing, réverbération, et un petit motif de
kalimba seulement par moments. Toujours l'identité de la marque (brand/BRAND.md) :
90 BPM, ré mineur, Dm – B♭ – F – C, deux mesures par accord.

Sections (débuts des scènes, tools/plan.json écrit par tools/construire.py) :

  01–02  intro : piano + nappe, sans batterie
  03–04  groove : + basse, batterie
  05–06  groove + motif de kalimba
  07     pause : batterie et basse s'arrêtent, montée vers le radar, impact sur le radar
  09–10  groove complet + motif
  11     fin : batterie coupée, accord final de Dm9 sur la phrase de conclusion, fondu

  python3 tools/music.py
"""
import json
import subprocess
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SR = 44100
rng = np.random.default_rng(20261101)
mtof = lambda m: 440.0 * 2 ** ((m - 69) / 12)

plan = json.loads((ROOT / "tools/plan.json").read_text())
TOTAL = float(plan["total"])
F = {int(s["id"][:2]): float(s["debut"]) for s in plan["scenes"]}
N = int(TOTAL * SR) + 1
T = np.arange(N) / SR

BEAT = 60 / 90
BAR = 4 * BEAT
SWING = 0.08 * BEAT  # croches du contretemps légèrement retardées

# Accords (deux mesures chacun) : voicings serrés qui s'enchaînent sans saut.
ACCORDS = [
    (38, [53, 57, 60, 64]),  # Dm9    : F A C E sur ré
    (34, [53, 57, 58, 62]),  # B♭maj7 : F A B♭ D sur si♭
    (41, [55, 57, 60, 64]),  # Fmaj9  : G A C E sur fa
    (36, [55, 60, 62, 64]),  # Cadd9  : G C D E sur do
]
# Motif de kalimba sur un cycle de 8 mesures (temps, note, durée en temps)
MOTIF = [(0, 81, 1.5), (1.5, 79, .5), (2, 77, 1), (3, 76, 1), (4, 74, 3),
         (8, 77, 1.5), (9.5, 74, .5), (10, 74, 1), (11, 72, 1), (12, 70, 3),
         (16, 72, 1.5), (17.5, 74, .5), (18, 76, 1), (19, 77, 1), (20, 81, 3),
         (24, 79, 1.5), (25.5, 77, .5), (26, 76, 1), (27, 74, 1), (28, 72, 2), (30, 76, 2)]

RADAR = F[7] + 3.6     # le radar affiche 105 km/h (100 au compteur)
FINAL = F[11] + 5.0    # « Ton compteur compte des tours, le radar mesure la réalité. »


def section(t):
    if t < F[3]:
        return "intro"
    if t < F[5]:
        return "groove"
    if t < F[7]:
        return "groove+motif"
    if t < F[9]:
        return "pause"
    if t < F[11]:
        return "groove+motif"
    return "fin"


# ---------------------------------------------------------------------------
# Pistes (stéréo) et envoi vers la réverbération
pistes = {k: np.zeros((2, N)) for k in ("keys", "pad", "bass", "kick", "snare", "hat", "kal", "fx")}
ENVOI = {"keys": 0.28, "pad": 0.35, "bass": 0.0, "kick": 0.04, "snare": 0.35, "hat": 0.08, "kal": 0.5, "fx": 0.5}
GAIN = {"keys": 0.26, "pad": 0.07, "bass": 0.34, "kick": 0.55, "snare": 0.16, "hat": 0.045, "kal": 0.085, "fx": 0.3}


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


def grosse_caisse():
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    freq = 46 + 70 * np.exp(-t / 0.035)
    s = np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-t / 0.22)
    clic = fft_filtre(rng.standard_normal(n) * np.exp(-t / 0.003), passe_bas(3000))
    return s + 0.15 * clic


def caisse_claire():
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    bruit = fft_filtre(rng.standard_normal(n), lambda f: passe_haut(1200)(f) * passe_bas(5500)(f))
    corps = np.sin(2 * np.pi * 185 * t) * np.exp(-t / 0.05)
    return (bruit * np.exp(-t / 0.10) * 0.9 + 0.5 * corps) * np.minimum(1, t / 0.002)


def charleston():
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    bruit = fft_filtre(rng.standard_normal(n), passe_haut(7000, 3))
    return bruit * np.exp(-t / 0.022)


KICK, SNARE, HAT = grosse_caisse(), caisse_claire(), charleston()

# ---------------------------------------------------------------------------
# Écriture

coups_kick = []
mesure = 0
while mesure * BAR < TOTAL:
    t0 = mesure * BAR
    racine, voicing = ACCORDS[(mesure // 2) % 4]
    prochaine = ACCORDS[((mesure // 2) + 1) % 4][0]
    sec = section(t0)
    premiere = mesure % 2 == 0
    if t0 >= FINAL - 0.01:
        break

    # piano : accord plaqué légèrement égrené au premier temps, relances discrètes
    if premiere:
        rythme = [(0.0, 2.4, 0.9), (2.5, 1.3, 0.5)]
    else:
        rythme = [(0.5, 1.4, 0.55), (2.0, 1.8, 0.62)]
    for b, d, v in rythme:
        tb = t0 + b * BEAT
        if tb >= FINAL - 0.05:
            continue
        d = min(d * BEAT, FINAL - tb)
        for k, m in enumerate(voicing):
            place("keys", rhodes(m, d, v * (0.92 if k else 1.0)), tb + 0.011 * k, pan=(-0.35, -0.1, 0.12, 0.35)[k])

    # nappe : une fois par accord
    if premiere:
        place("pad", nappe([racine + 12, racine + 19, voicing[1], voicing[3]], min(2 * BAR, FINAL - t0)), t0)

    # basse et batterie hors intro, pause et fin
    if sec in ("groove", "groove+motif"):
        motif_basse = [(0, 1.5, 1.0, racine), (1.75, 0.5, 0.55, racine), (2.5, 1.0, 0.8, racine + 7)]
        if premiere:
            motif_basse.append((3.5, 0.45, 0.6, racine + 12))
        else:
            motif_basse.append((3.5, 0.45, 0.6, prochaine + (2 if prochaine < racine else -1)))
        for b, d, v, m in motif_basse:
            place("bass", basse(m, d * BEAT, v), t0 + b * BEAT)
        for b in (0.0, 2.5):  # grosse caisse
            coups_kick.append(t0 + b * BEAT)
            place("kick", KICK, t0 + b * BEAT)
        for b in (1.0, 3.0):  # caisse claire, un peu en arrière
            place("snare", SNARE, t0 + b * BEAT + 0.012, pan=0.05)
        for k in range(8):  # charleston en croches swinguées
            tb = t0 + (k * 0.5) * BEAT + (SWING if k % 2 else 0)
            place("hat", HAT, tb, gain=(1.0 if k % 2 else 0.6) * (0.85 + 0.15 * rng.random()), pan=0.3)

    # kalimba par moments
    if sec == "groove+motif":
        debut_cycle = (mesure // 8) * 8 * BAR
        for b, m, d in MOTIF:
            tb = debut_cycle + b * BEAT
            if t0 <= tb < t0 + BAR and section(tb) == "groove+motif":
                place("kal", kalimba(m, 0.9), tb, pan=-0.25)
    mesure += 1

# pause : montée de bruit filtré vers le radar, puis impact grave et accord suspendu
n = int(1.4 * SR)
t = np.arange(n) / SR
montee = fft_filtre(rng.standard_normal(n), passe_bas(2500)) * (t / t[-1]) ** 3
place("fx", montee, RADAR - 1.4, gain=0.35)
n = int(2.2 * SR)
t = np.arange(n) / SR
boom = np.sin(2 * np.pi * np.cumsum(40 + 30 * np.exp(-t / 0.08)) / SR) * np.exp(-t / 0.6)
place("fx", boom, RADAR, gain=1.0)
for k, m in enumerate((50, 57, 62, 65, 69)):
    place("keys", rhodes(m, 2.6, 0.75), RADAR + 0.01 * k, pan=(-0.4, -0.2, 0, 0.2, 0.4)[k])

# fin : accord de Dm9 tenu sur la phrase finale, nappe et basse longues
for k, m in enumerate((50, 57, 60, 64, 65, 69)):
    place("keys", rhodes(m, TOTAL - FINAL, 0.8), FINAL + 0.02 * k, pan=(-0.45, -0.25, -0.05, 0.1, 0.3, 0.45)[k])
place("pad", nappe([50, 57, 62, 65, 69], TOTAL - FINAL), FINAL)
place("bass", basse(38, TOTAL - FINAL, 0.8), FINAL)
place("kal", kalimba(81, 0.8), FINAL + 1.0, pan=-0.25)
place("kal", kalimba(76, 0.7), FINAL + 1.75, pan=-0.25)
place("kal", kalimba(74, 0.75), FINAL + 2.5, pan=-0.25)

# ---------------------------------------------------------------------------
# Mixage

# trémolo stéréo léger sur le piano (caractéristique du Rhodes)
trem = 0.12 * np.sin(2 * np.pi * 3.0 * T)
pistes["keys"] *= np.stack([1 + trem, 1 - trem])
# la basse et la grosse caisse restent au centre et sans aigus ; la nappe sans grave
pistes["bass"] = fft_filtre(pistes["bass"], passe_bas(900))
pistes["pad"] = fft_filtre(pistes["pad"], lambda f: passe_haut(180)(f) * passe_bas(2200)(f))

# compression « pompée » discrète par la grosse caisse
pompe = np.ones(N)
for tk in coups_kick:
    i0 = int(tk * SR)
    seg = np.arange(min(int(0.4 * SR), N - i0)) / SR
    pompe[i0: i0 + len(seg)] = np.minimum(pompe[i0: i0 + len(seg)], 1 - 0.28 * np.exp(-seg / 0.16))
for k in ("keys", "pad", "bass", "kal"):
    pistes[k] *= pompe

sec_bus = sum(GAIN[k] * pistes[k] for k in pistes)
envoi = sum(GAIN[k] * ENVOI[k] * pistes[k] for k in pistes)

# réverbération : réponse impulsionnelle synthétique (bruit à décroissance exponentielle, 2,2 s)
ni = int(2.2 * SR)
ti = np.arange(ni) / SR
ir = rng.standard_normal((2, ni)) * np.exp(-ti / 0.38)
ir[:, : int(0.02 * SR)] = 0  # pré-délai
ir = fft_filtre(ir, passe_bas(4500))
ir /= np.sqrt((ir ** 2).sum(axis=1, keepdims=True))
L = 1 << int(np.ceil(np.log2(N + ni)))
rev = np.fft.irfft(np.fft.rfft(envoi, L, axis=-1) * np.fft.rfft(ir, L, axis=-1), L, axis=-1)[:, :N]
mix = sec_bus + 0.55 * rev

# chaleur : aigus adoucis, rien sous 30 Hz
mix = fft_filtre(mix, lambda f: passe_bas(9000, 1)(f) * passe_haut(30)(f))
fondu = np.clip((TOTAL - T) / 3.0, 0, 1) * np.clip(T / 0.6, 0, 1)
mix *= fondu
mix = np.tanh(mix / np.abs(mix).max() * 1.2) / np.tanh(1.2) * 0.5

wav = ROOT / "assets/music/fond.wav"
wav.parent.mkdir(parents=True, exist_ok=True)
with wave.open(str(wav), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((np.clip(mix.T, -1, 1) * 32767).astype("<i2").tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wav), "-c:a", "aac", "-b:a", "192k", str(ROOT / "assets/music/fond.m4a")], check=True)
wav.unlink()
print(f"musique {TOTAL:.1f} s → assets/music/fond.m4a")
