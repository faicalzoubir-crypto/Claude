"""Musique originale de la vidéo, synthétisée et calée sur l'image.

Chaque scène note ses moments clés (self.marquer dans scenes.py : départ,
arrivées, danger, choc, carton…). Ce module en tire une partition : nappes
d'accords, tic-tac d'horloge (qui accélère pendant les courses), cloches aux
arrivées, pulsation de tension avant l'obstacle, coup sourd puis silence au
choc, résolution en majeur sur le carton final. Aucun échantillon externe,
donc aucun droit à gérer ; résultat identique à chaque rendu.

    python musique.py build/final_90s/reperes musique.wav   # à la main
(rendre.py l'appelle tout seul et mixe la musique dans la vidéo.)
"""

import json
import sys
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, fftconvolve, sosfilt

SR = 48000
TEMPO = 100  # pulsations par minute
TEMPS = 60 / TEMPO  # durée d'un temps (s)
RNG = np.random.default_rng(7)

# Accords en notes MIDI (voix médiums) et leur basse.
ACCORDS = {
    "Am": ([57, 60, 64, 71], 45),
    "F": ([53, 57, 60, 64], 41),
    "C": ([55, 60, 64, 67], 48),
    "G": ([55, 59, 62, 67], 43),
    "Dm": ([50, 57, 62, 65], 38),
    "Bb": ([53, 58, 62, 65], 46),
    "E": ([52, 56, 59, 64], 40),
    "Cadd9": ([55, 60, 62, 64, 67], 48),
}


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def temps_de(n):
    return np.arange(int(n * SR)) / SR


# --- Instruments ----------------------------------------------------------------


def nappe(notes, duree, attaque=1.2, relache=1.8, clarte=1600.0, desaccord=0.004):
    """Nappe douce : dents de scie additives filtrées, légèrement désaccordées
    entre gauche et droite. Renvoie un tableau stéréo (2, n)."""
    t = temps_de(duree + relache)
    out = np.zeros((2, t.size))
    lfo = 1 + 0.08 * np.sin(2 * np.pi * 0.17 * t)
    for m in notes:
        f0 = hz(m)
        for canal, d in ((0, -desaccord), (1, desaccord)):
            f = f0 * (1 + d)
            sig = np.zeros(t.size)
            k = 1
            while k * f < 7000:
                attenuation = 1 / (1 + (k * f / clarte) ** 4)
                sig += attenuation / k * np.sin(2 * np.pi * k * f * t + RNG.uniform(0, 2 * np.pi))
                k += 1
            out[canal] += sig
    env = np.ones(t.size)
    na = int(attaque * SR)
    env[:na] = np.sin(np.linspace(0, np.pi / 2, na)) ** 2
    nr = t.size - int(duree * SR)
    env[-nr:] *= np.exp(-np.linspace(0, 6, nr))
    return out * env * lfo / len(notes)


def pincee(midi, duree=1.6, brillance=1.0):
    """Note pincée (genre kalimba) : harmoniques qui s'éteignent vite."""
    t = temps_de(duree)
    f = hz(midi)
    sig = np.zeros(t.size)
    for k in range(1, 7):
        if k * f > 9000:
            break
        sig += (brillance / k**1.4) * np.sin(2 * np.pi * k * f * t) * np.exp(-t * (2.5 + 2.2 * k))
    sig *= np.minimum(1, t / 0.003)
    return sig


def cloche(midi, duree=3.0):
    """Cloche : partiels inharmoniques."""
    t = temps_de(duree)
    f = hz(midi)
    sig = np.zeros(t.size)
    for r, a, d in ((1, 1, 1.1), (2.0, 0.5, 1.6), (2.76, 0.35, 2.3), (4.07, 0.2, 3.2), (5.4, 0.12, 4.5)):
        sig += a * np.sin(2 * np.pi * r * f * t) * np.exp(-t * d)
    return sig * np.minimum(1, t / 0.002)


_PASSE_BANDE = butter(4, [1800, 7000], btype="bandpass", fs=SR, output="sos")


def tic(aigu=True):
    """Tic (ou tac) d'horloge : bruit filtré très court + petit clic."""
    t = temps_de(0.04)
    bruit = sosfilt(_PASSE_BANDE, RNG.standard_normal(t.size)) * np.exp(-t / 0.004)
    clic = np.sin(2 * np.pi * (2400 if aigu else 1700) * t) * np.exp(-t / 0.006)
    return 0.6 * bruit + 0.5 * clic


def basse(midi, duree=0.28):
    """Coup de basse court (sinus + octave), pour les pulsations."""
    t = temps_de(duree)
    f = hz(midi)
    env = np.minimum(1, t / 0.006) * np.exp(-t * 7)
    return (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t)) * env


def bourdon(midi, duree):
    """Note grave tenue (sinus + octave), fondus doux."""
    t = temps_de(duree)
    f = hz(midi)
    env = np.minimum(1, t / 0.6) * np.minimum(1, (duree - t) / 0.8)
    return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(4 * np.pi * f * t)) * np.clip(env, 0, 1)


def battement():
    """Cœur : deux coups sourds (« poum-poum »)."""
    t = temps_de(0.7)
    sig = np.zeros(t.size)
    for decalage, a in ((0.0, 1.0), (0.17, 0.7)):
        tt = np.clip(t - decalage, 0, None)
        f = 55 + 25 * np.exp(-tt * 30)
        sig += a * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 14) * (t >= decalage)
    return sig


def coup_sourd(duree=2.5):
    """Impact amorti : grave qui descend + souffle (rien d'agressif)."""
    t = temps_de(duree)
    f = 34 + 70 * np.exp(-t * 7)
    grave = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.8)
    souffle = sosfilt(butter(2, 300, fs=SR, output="sos"), RNG.standard_normal(t.size)) * np.exp(-t * 9)
    return (grave + 0.8 * souffle) * np.minimum(1, t / 0.004)


def montee(duree):
    """Montée de tension : glissando + souffle qui s'ouvre, crescendo."""
    t = temps_de(duree)
    x = t / duree
    f = 220 * 2 ** (2 * x)
    phase = 2 * np.pi * np.cumsum(f) / SR
    ton = np.sin(phase) + 0.5 * np.sin(2 * phase) + 0.3 * np.sin(0.5 * phase)
    bruit = RNG.standard_normal(t.size)
    souffle = np.zeros(t.size)
    pas = SR // 50  # filtre qui s'ouvre par tranches de 20 ms, état conservé (pas de clic)
    zi = np.zeros((1, 2))
    for i in range(0, t.size, pas):
        fc = 400 * 2 ** (4 * x[i])
        souffle[i : i + pas], zi = sosfilt(butter(2, min(fc, 16000), fs=SR, output="sos"), bruit[i : i + pas], zi=zi)
    return (0.6 * ton + 0.5 * souffle) * x**2


def tenue(midi, duree, vibrato=5.0):
    """Note tenue aiguë et fragile (arrêt sur image)."""
    t = temps_de(duree + 0.5)
    f = hz(midi) * (1 + 0.004 * np.sin(2 * np.pi * vibrato * t))
    phase = 2 * np.pi * np.cumsum(f) / SR
    sig = np.sin(phase) + 0.3 * np.sin(2 * phase)
    env = np.minimum(1, t / 0.15) * np.where(t > duree, np.exp(-(t - duree) * 10), 1)
    return sig * env


def pluie(duree):
    """Pluie légère : souffle aigu + gouttes."""
    t = temps_de(duree)
    souffle = sosfilt(butter(2, 3500, btype="highpass", fs=SR, output="sos"), RNG.standard_normal(t.size))
    env = np.minimum(1, t / 0.8) * np.minimum(1, (duree - t) / 0.8)
    sig = 0.25 * souffle * env
    for g in RNG.uniform(0, duree - 0.05, int(duree * 9)):
        goutte = pincee(RNG.integers(84, 96), 0.08) * 0.5
        i = int(g * SR)
        sig[i : i + goutte.size] += goutte[: sig.size - i]
    return sig


# --- Table de mixage ---------------------------------------------------------------


class Mix:
    def __init__(self, duree):
        n = int((duree + 4) * SR)
        self.duree = duree
        self.sec = np.zeros((2, n))
        self.envoi = np.zeros((2, n))  # vers la réverbération

    def jouer(self, t, son, gain=1.0, pan=0.0, reverb=0.25):
        if t >= self.duree:
            return
        son = np.atleast_2d(son)
        if son.shape[0] == 1:
            g, d = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
            son = np.vstack([son[0] * g * np.sqrt(2), son[0] * d * np.sqrt(2)])
        i = int(max(t, 0) * SR)
        n = min(son.shape[1], self.sec.shape[1] - i)
        self.sec[:, i : i + n] += gain * son[:, :n]
        self.envoi[:, i : i + n] += gain * reverb * son[:, :n]

    def silence(self, t0, t1, fondu=0.05):
        """Coupe net tout ce qui sonne entre t0 et t1 (fondus courts)."""
        i0, i1, nf = int(t0 * SR), int(t1 * SR), int(fondu * SR)
        env = np.ones(self.sec.shape[1])
        env[i0 : i0 + nf] = np.linspace(1, 0, nf)
        env[i0 + nf : i1] = 0
        env[i1 : i1 + nf] = np.linspace(0, 1, nf)
        self.sec *= env
        self.envoi *= env

    def rendre(self):
        t = temps_de(2.8)
        ir = RNG.standard_normal((2, t.size)) * np.exp(-t / 0.55)
        ir = sosfilt(butter(2, 5000, fs=SR, output="sos"), ir)
        ir /= np.sqrt((ir**2).sum(axis=1, keepdims=True))
        reverb = np.vstack([fftconvolve(self.envoi[c], ir[c])[: self.envoi.shape[1]] for c in range(2)])
        out = self.sec + 0.9 * reverb
        out = out[:, : int(self.duree * SR)]
        # Fondu final pour finir sur le silence.
        nf = int(1.2 * SR)
        out[:, -nf:] *= np.linspace(1, 0, nf) ** 2
        return out / (np.abs(out).max() + 1e-9) * 0.89


# --- Partition, scène par scène --------------------------------------------------------


def accords(mix, plages, **kw):
    """plages : [(début, fin, accord)] en temps absolus."""
    for t0, t1, nom in plages:
        if t1 - t0 > 0.05:
            mix.jouer(t0, nappe(ACCORDS[nom][0], t1 - t0, **kw), gain=0.32, reverb=0.35)


def tictac(mix, t0, t1, pas=TEMPS, gain=0.12):
    for i, t in enumerate(np.arange(t0, t1, pas)):
        mix.jouer(t, tic(i % 2 == 0), gain=gain, pan=0.15 if i % 2 else -0.15, reverb=0.12)


def pulsation(mix, t0, t1, note, pas=TEMPS / 2, gain=0.28):
    for i, t in enumerate(np.arange(t0, t1, pas)):
        mix.jouer(t, basse(note, min(pas * 1.6, 0.4)), gain=gain * (1 if i % 2 == 0 else 0.7), reverb=0.05)


def arpege(mix, t0, t1, accord, pas=TEMPS / 2, gain=0.13, octave=12):
    notes = ACCORDS[accord][0]
    motif = [notes[0], notes[1], notes[2], notes[-1], notes[2], notes[1]]
    for i, t in enumerate(np.arange(t0, t1, pas)):
        mix.jouer(t, pincee(motif[i % len(motif)] + octave), gain=gain, pan=0.3 * (-1) ** i, reverb=0.35)


def partition(scenes):
    """scenes : [(id, début absolu, durée, {événement: [instants absolus]})]."""
    total = sum(d for _, _, d, _ in scenes)
    mix = Mix(total)
    for sid, t0, d, ev in scenes:
        fin = t0 + d
        un = {k: v[0] for k, v in ev.items()}

        if sid == "s1":
            accords(mix, [(t0, fin, "Am")], attaque=1.0)
            tictac(mix, t0 + 0.2, fin - 0.2)
            q = un.get("question", t0 + d / 2)
            a = un.get("aiguille", t0)
            mix.jouer(a, montee(max(q - a, 0.5)), gain=0.14, reverb=0.3)
            for i, n in enumerate((57, 60, 64, 67)):  # motif « question » qui ne se résout pas
                mix.jouer(q + i * TEMPS / 2, pincee(n + 12), gain=0.16, pan=-0.2 + 0.13 * i, reverb=0.4)

        elif sid in ("s2", "s3"):
            avant, pendant, apres = ("Am", "Am", "F") if sid == "s2" else ("F", "G", "C")
            dep, ar_r, ar_l, gain_t = un["depart"], un["arrivee_rapide"], un["arrivee_lente"], un["gain"]
            accords(mix, [(t0, dep, avant), (dep, ar_l, pendant), (ar_l, un.get("bilan", fin), apres)])
            tictac(mix, t0 + 0.1, dep)
            tictac(mix, dep, ar_l, pas=TEMPS / 4, gain=0.1)  # le temps s'emballe
            pulsation(mix, dep, ar_l, ACCORDS[pendant][1])
            mix.jouer(ar_r, cloche(81), gain=0.16, pan=0.3, reverb=0.5)
            mix.jouer(ar_l, cloche(76), gain=0.16, pan=-0.3, reverb=0.5)
            for i, n in enumerate(ACCORDS[apres][0]):
                mix.jouer(gain_t + i * 0.05, pincee(n + 12, 2.5), gain=0.14, reverb=0.4)
            if "bilan" in un:
                accords(mix, [(un["bilan"], fin, "Am")], attaque=0.8)
                arpege(mix, un["bilan"], fin - 0.5, "Am", pas=TEMPS)

        elif sid == "s4":
            m = ev.get("marche", [t0 + d / 3, t0 + d / 2])
            msg = un.get("message", t0 + 2 * d / 3)
            plages = [(t0, m[0], "C"), (m[0], m[1], "G"), (m[1], msg, "Am"), (msg, fin, "F")]
            accords(mix, plages)
            for a, b, nom in plages:
                arpege(mix, a, b, nom)
            for t in m:
                mix.jouer(t, cloche(84), gain=0.09, reverb=0.5)

        elif sid == "s5":
            accords(mix, [(t0, un.get("bilan", fin), "Dm"), (un.get("bilan", fin), un.get("reprise", fin), "Bb")], clarte=1000)
            if "reprise" in un:
                accords(mix, [(un["reprise"], fin, "Dm")], clarte=1000)
            mix.jouer(t0, bourdon(38, d), gain=0.22, reverb=0.1)
            if "approche" in un and "danger" in un:
                mix.jouer(un["approche"], montee(max(un["danger"] - un["approche"], 0.3)), gain=0.12)
            if "danger" in un:
                mix.jouer(un["danger"], cloche(81) + 0.6 * cloche(82), gain=0.12, reverb=0.5)
            arrets = ev.get("arret", [])
            debuts = [un["reaction"]] + ev.get("reprise", [])
            for a, b in zip(debuts, arrets):
                for t in np.arange(a, b, 0.75):
                    mix.jouer(t, battement(), gain=0.5, reverb=0.08)
            for t in arrets:
                mix.jouer(t, basse(33, 0.6), gain=0.4, reverb=0.2)

        elif sid == "s6":
            b, c, m = un.get("barres", t0), un.get("carre", t0 + d / 3), un.get("mouille", t0 + 2 * d / 3)
            accords(mix, [(t0, c, "Bb"), (c, m, "F"), (m, fin, "Dm")])
            gamme = [57, 60, 62, 64, 67, 69, 72, 74, 76, 79, 81]  # une note par barre qui monte
            for i, n in enumerate(gamme):
                mix.jouer(b + i * (c - b) * 0.8 / len(gamme), pincee(n), gain=0.12, pan=-0.4 + 0.08 * i, reverb=0.35)
            mix.jouer(c, cloche(77), gain=0.12, reverb=0.5)
            mix.jouer(m, pluie(fin - m), gain=0.3, reverb=0.3)

        elif sid == "s7":
            parties = ev["partie"] + [fin]
            for i, p0 in enumerate(parties[:-1]):
                p1 = parties[i + 1]
                g, r, imp = ev["gel"][i], ev["reprise"][i], ev["impact"][i]
                eq = ev["equivalence"][i]
                accords(mix, [(p0, g, "Am")], clarte=900, attaque=0.4)
                pulsation(mix, p0, g, 33, gain=0.3)
                mix.jouer(ev["approche"][i], montee(max(g - ev["approche"][i], 0.4)), gain=0.16 + 0.04 * i)
                mix.silence(g, g + 0.02, fondu=0.03)  # la musique se fige avec l'image
                mix.jouer(g, tenue(76, r - g) + 0.5 * tenue(71, r - g), gain=0.08, reverb=0.6)
                accords(mix, [(r, imp, "E")], clarte=900, attaque=0.2, relache=0.3)
                pulsation(mix, r, imp, 33, pas=TEMPS / 4, gain=0.32)
                mix.silence(imp, min(imp + 0.9, eq))
                mix.jouer(imp, coup_sourd(), gain=0.7 + 0.15 * i, reverb=0.4)
                accords(mix, [(eq, p1, "Am")], clarte=700, attaque=0.8)
                mix.jouer(eq + 0.3, cloche(45 + 12 * (1 - i)), gain=0.14, reverb=0.6)

        elif sid == "s8":
            l2 = un.get("ligne2", t0 + d / 4)
            liv, msg, ca = un.get("livreurs", fin), un.get("message", fin), un.get("carton")
            fin_msg = ca if ca else fin
            plages = [(t0, l2, "F"), (l2, liv, "Dm"), (liv, msg, "C"), (msg, fin_msg, "F")]
            if ca:
                plages.append((ca, fin, "Cadd9"))
            accords(mix, plages, attaque=1.0)
            if "notif" in un:  # « ding-ding » de notification
                mix.jouer(un["notif"], cloche(91, 1.2), gain=0.07, pan=0.2, reverb=0.4)
                mix.jouer(un["notif"] + 0.13, cloche(96, 1.2), gain=0.06, pan=0.2, reverb=0.4)
            if "reponse" in un:  # message envoyé
                mix.jouer(un["reponse"], pincee(79), gain=0.12, pan=-0.2, reverb=0.3)
                mix.jouer(un["reponse"] + 0.09, pincee(84), gain=0.12, pan=-0.2, reverb=0.3)
            if msg < fin:
                mix.jouer(msg, cloche(72), gain=0.13, reverb=0.6)
                mix.jouer(msg, basse(41, 3.0), gain=0.3, reverb=0.2)
                arpege(mix, msg + 0.3, fin_msg - 0.6, "F", pas=TEMPS, gain=0.1)
            if ca:
                mix.jouer(ca, cloche(72), gain=0.13, reverb=0.6)
                mix.jouer(ca, basse(36, 3.0), gain=0.3, reverb=0.2)
                arpege(mix, ca + 0.3, fin - 1.0, "Cadd9", pas=TEMPS, gain=0.1)
    return mix.rendre()


ORDRE = {
    "S1Accroche": "s1",
    "S2Ville": "s2",
    "S3Autoroute": "s3",
    "S4Paradoxe": "s4",
    "S5Schema": "s5",
    "S6Graphique": "s6",
    "S7Experiences": "s7",
    "S8Conclusion": "s8",
}


def scenes_depuis(reperes, durees=None):
    """Lit les repères des scènes ; `durees` (nom → s) remplace celles notées
    par Manim (on préfère la durée réelle des fichiers vidéo)."""
    scenes, t0 = [], 0.0
    for nom, sid in ORDRE.items():
        info = json.loads((Path(reperes) / f"{nom}.json").read_text(encoding="utf-8"))
        d = durees[nom] if durees else info["duree"]
        ev = {}
        for e in info.get("evenements", []):
            ev.setdefault(e["nom"], []).append(t0 + e["t"])
        scenes.append((sid, t0, d, ev))
        t0 += d
    return scenes


def ecrire(scenes, chemin):
    audio = partition(scenes)
    wavfile.write(chemin, SR, (audio.T * 32767).astype(np.int16))


if __name__ == "__main__":
    ecrire(scenes_depuis(sys.argv[1]), sys.argv[2])
