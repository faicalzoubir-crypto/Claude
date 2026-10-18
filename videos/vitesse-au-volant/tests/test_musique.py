"""La partition se génère sur une chronologie factice, sans saturer."""

import numpy as np
from scipy.signal import butter, sosfilt

import musique


def chronologie():
    ev = {
        "s1": {"aiguille": [0.2], "question": [1.0]},
        "s2": {"depart": [0.5], "arrivee_rapide": [1.0], "arrivee_lente": [1.4], "gain": [1.6]},
        "s3": {"depart": [0.5], "arrivee_rapide": [0.8], "arrivee_lente": [1.1], "gain": [1.4]},
        "s4": {"marche": [0.5, 1.0], "message": [1.5]},
        "s5": {"approche": [0.2], "danger": [0.5], "reaction": [0.6], "freinage": [1.0], "arret": [1.5], "bilan": [1.7]},
        "s6": {"barres": [0.2], "carre": [1.0], "mouille": [1.5]},
        "s7": {k: [v, v + 5] for k, v in dict(partie=0, approche=0.3, gel=0.6, reprise=0.9, impact=1.4, arret=1.8, equivalence=3.0).items()},
        "s8": {"ligne2": [0.6], "carton": [1.2]},
    }
    scenes, t0 = [], 0.0
    for sid in ("s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8"):
        d = 10.0 if sid == "s7" else 2.5
        scenes.append((sid, t0, d, {k: [t0 + x for x in v] for k, v in ev[sid].items()}))
        t0 += d
    return scenes, t0


def test_partition():
    scenes, total = chronologie()
    audio = musique.partition(scenes)
    assert audio.shape == (2, int(total * musique.SR))
    assert np.isfinite(audio).all()
    assert 0.5 < np.abs(audio).max() <= 0.9
    # Au choc, la musique se coupe : seule la queue du coup sourd reste dans les aigus.
    aigus = sosfilt(butter(4, 2000, btype="highpass", fs=musique.SR, output="sos"), audio.mean(axis=0))
    choc = scenes[6][3]["impact"][0]

    def niveau(a, b):
        return np.sqrt((aigus[int(a * musique.SR) : int(b * musique.SR)] ** 2).mean())

    assert niveau(choc + 0.2, choc + 0.7) < niveau(choc - 0.3, choc - 0.05) / 3  # −10 dB : il ne reste que la queue du coup sourd
