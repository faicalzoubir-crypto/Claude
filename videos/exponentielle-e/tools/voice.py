"""Exponentielle e — voix off phrase par phrase (Kokoro ff_siwis, vitesse 1,0).

Chaque plan est découpé en répliques (cues). Chaque réplique est synthétisée seule,
débarrassée de ses silences de bord, puis les répliques sont mises bout à bout avec
des pauses choisies. On connaît ainsi l'instant exact où chaque valeur est dite, et
les animations se calent dessus (tools/timing.json).

Chaque assets/voice/NN.wav contient l'amorce (LEAD), la voix et la tenue de fin du
plan : sa durée EST la durée du plan (audio.mjs sync-durations la recopie dans
STORYBOARD.md).

Usage : python tools/voice.py   (kokoro-onnx, numpy, soundfile)
"""
import json
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

ROOT = Path(__file__).resolve().parent.parent
MODELS = Path.home() / ".cache" / "hyperframes" / "tts"
VOICE, SPEED, LANG = "ff_siwis", 1.0, "fr-fr"
LEAD = 0.35  # silence avant la première réplique de chaque plan

# (id, texte, pause après) — l'id sert de clé dans timing.json.
FRAMES = {
    1: {
        "tail": 0.9,
        "cues": [
            ("fonction", "Il existe une fonction égale à sa propre dérivée.", 0.45),
            ("secret", "Tout son secret tient dans un seul nombre : e.", 0.0),
        ],
    },
    2: {
        "tail": 0.8,
        "cues": [
            ("trois", "Découvrons-le de trois façons :", 0.3),
            ("limite", "une limite,", 0.22),
            ("courbes", "deux courbes,", 0.22),
            ("derivee", "puis une dérivée.", 0.0),
        ],
    },
    3: {
        "tail": 1.8,
        "cues": [
            ("formule", "Prenons un plus un sur n, puissance n.", 0.5),
            ("n1", "Pour n égal un : deux.", 0.35),
            ("n2", "Pour n égal deux : deux virgule vingt-cinq.", 0.35),
            ("n3", "Pour n égal trois : environ deux virgule trente-sept.", 0.5),
            ("n10", "Puis dix,", 0.18),
            ("n100", "cent,", 0.18),
            ("n1000", "mille,", 0.18),
            ("n1e6", "un million…", 0.5),
            ("grandit", "La suite grandit de moins en moins, et se rapproche d'une limite :", 0.3),
            ("e", "le nombre e, environ deux virgule sept, un, huit, deux, huit.", 0.0),
        ],
    },
    4: {
        "tail": 1.8,
        "cues": [
            ("tracons", "Traçons deux puissance x et trois puissance x.", 0.4),
            ("point", "Les deux courbes passent par le point zéro, un.", 0.45),
            ("pente2", "Là, la pente de deux puissance x vaut environ zéro virgule soixante-neuf.", 0.4),
            ("pente3", "Celle de trois puissance x, environ un virgule dix.", 0.6),
            ("base", "Entre les deux, une seule base donne une pente exactement égale à un :", 0.3),
            ("cest_e", "c'est e, le même nombre que notre limite.", 0.0),
        ],
    },
    5: {
        "tail": 1.0,
        "cues": [
            ("glisser", "Sur la courbe de e puissance x, faisons glisser la tangente.", 0.4),
            ("partout", "Partout, sa pente est égale à la hauteur du point.", 0.5),
            ("x1", "En x égal un, la pente vaut e.", 0.0),
        ],
    },
    6: {
        "tail": 1.8,
        "cues": [
            ("pourquoi", "Pourquoi ?", 0.4),
            ("taux", "Le taux d'accroissement s'écrit e puissance x, fois e puissance h moins un, sur h.", 0.5),
            ("tend", "Quand h tend vers zéro, ce quotient tend vers un :", 0.25),
            ("pente0", "c'est la pente en zéro.", 0.5),
            ("donc", "Donc la dérivée de l'exponentielle, c'est l'exponentielle.", 0.0),
        ],
    },
    7: {
        "tail": 5.2,  # signature manuscrite : le temps de l'écrire puis de la tenir
        "cues": [
            ("trois", "Une limite, deux courbes, une dérivée :", 0.3),
            ("un_seul", "un seul nombre, e.", 0.0),
        ],
    },
}


def trim(x, sr, thresh=0.012, pad=0.03):
    """Coupe les silences de bord (seuil d'amplitude), en gardant un petit coussin."""
    loud = np.flatnonzero(np.abs(x) > thresh)
    if loud.size == 0:
        return x
    a = max(0, loud[0] - int(pad * sr))
    b = min(len(x), loud[-1] + int(pad * sr))
    return x[a:b]


def main():
    k = Kokoro(str(MODELS / "models" / "kokoro-v1.0.onnx"), str(MODELS / "voices" / "voices-v1.0.bin"))
    out_dir = ROOT / "assets" / "voice"
    out_dir.mkdir(parents=True, exist_ok=True)
    timing = {"lead": LEAD, "frames": {}}
    sr_all = None
    for num, spec in FRAMES.items():
        parts, cues, t = [], {}, LEAD
        for cid, text, pause in spec["cues"]:
            samples, sr = k.create(text, voice=VOICE, speed=SPEED, lang=LANG)
            sr_all = sr_all or sr
            seg = trim(np.asarray(samples, dtype=np.float32), sr)
            dur = len(seg) / sr
            cues[cid] = {"start": round(t, 3), "end": round(t + dur, 3), "text": text}
            parts += [seg, np.zeros(int(pause * sr), dtype=np.float32)]
            t += dur + pause
        total = t + spec["tail"]
        audio = np.concatenate([np.zeros(int(LEAD * sr_all), dtype=np.float32)] + parts)
        audio = np.pad(audio, (0, max(0, int(round(total * sr_all)) - len(audio))))
        path = out_dir / f"{num:02d}.wav"
        sf.write(path, audio, sr_all)
        timing["frames"][f"{num:02d}"] = {"duration": round(len(audio) / sr_all, 3), "cues": cues}
        print(f"{path.name}: {len(audio) / sr_all:.2f}s · " + " · ".join(f"{c} {v['start']:.2f}" for c, v in cues.items()))
    (ROOT / "tools" / "timing.json").write_text(json.dumps(timing, ensure_ascii=False, indent=2))
    print("total", round(sum(f["duration"] for f in timing["frames"].values()), 2), "s")


if __name__ == "__main__":
    main()
