"""Logarithme ln — voix guide phrase par phrase (Kokoro ff_siwis, vitesse 1,0).

Voix GUIDE : l'utilisateur enregistre lui-même la voix off ; celle-ci sert à caler les animations
et à produire les repères (tools/cue_sheet.py). Une réplique peut avoir une graphie phonétique
pour la synthèse (4e élément) ; le texte affiché dans les repères reste l'orthographe correcte.

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

# (id, texte, pause après[, graphie pour la synthèse]) — l'id sert de clé dans timing.json.
FRAMES = {
    1: {
        "tail": 1.0,
        "cues": [
            ("question", "Si e puissance x égale cinq, combien vaut x ?", 0.5),
            ("nom", "La réponse a un nom : le logarithme népérien, ln.", 0.0, "La réponse a un nom : le logaritme népérien, ln."),
        ],
    },
    2: {
        "tail": 0.8,
        "cues": [
            ("quatre", "Quatre idées :", 0.25),
            ("reci", "la réciproque,", 0.2),
            ("prod", "les produits,", 0.2),
            ("deriv", "la dérivée,", 0.2),
            ("lim", "les limites.", 0.0),
        ],
    },
    3: {
        "tail": 1.6,
        "cues": [
            ("def", "Pour x strictement positif, y égale ln x signifie x égale e puissance y.", 0.5),
            ("reflet", "La courbe de ln est le reflet de celle de e puissance x par rapport à la droite y égale x.", 0.5),
            ("p1", "Le point zéro, un devient un, zéro :", 0.25),
            ("ln1", "ln de un vaut zéro.", 0.45),
            ("p2", "Le point un, e devient e, un :", 0.25),
            ("lne", "ln de e vaut un.", 0.0),
        ],
    },
    4: {
        "tail": 1.6,
        "cues": [
            ("prop", "ln transforme les produits en sommes :", 0.25),
            ("formule", "ln de a fois b égale ln a plus ln b.", 0.5),
            ("ex", "Par exemple, ln deux plus ln trois donne ln six :", 0.3),
            ("nums", "environ zéro virgule six neuf trois, plus un virgule zéro neuf neuf, soit un virgule sept neuf deux.", 0.5),
            ("quot", "On en déduit : ln de a sur b égale ln a moins ln b,", 0.3),
            ("puiss", "et ln de a puissance n égale n ln a.", 0.0),
        ],
    },
    5: {
        "tail": 1.6,
        "cues": [
            ("glisse", "Faisons glisser la tangente sur la courbe de ln.", 0.4),
            ("x1", "En x égal un, la pente vaut un ;", 0.3),
            ("x2", "en x égal deux, un demi ;", 0.3),
            ("xdemi", "en x égal un demi, deux.", 0.4),
            ("toujours", "La pente vaut toujours un sur x.", 0.5),
            ("preuve", "Preuve : en dérivant e puissance ln x égale x,", 0.25),
            ("obtient", "on obtient ln prime de x fois x égale un.", 0.3),
            ("donc", "Donc la dérivée de ln x est un sur x.", 0.0),
        ],
    },
    6: {
        "tail": 1.6,
        "cues": [
            ("croiss", "Un sur x est positif, donc ln est strictement croissante.", 0.45),
            ("lim0", "Quand x tend vers zéro, ln x tend vers moins l'infini.", 0.4),
            ("liminf", "Quand x tend vers plus l'infini, ln x tend vers plus l'infini,", 0.25),
            ("lent", "mais très lentement :", 0.25),
            ("million", "ln d'un million vaut seulement environ treize virgule huit.", 0.0),
        ],
    },
    7: {
        "tail": 5.2,  # signature manuscrite : le temps de l'écrire puis de la tenir
        "cues": [
            ("resume", "Réciproque de l'exponentielle, produits en sommes, dérivée un sur x :", 0.3),
            ("voila", "voilà ln.", 0.0),
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
        for cid, text, pause, *spoken in spec["cues"]:
            samples, sr = k.create(spoken[0] if spoken else text, voice=VOICE, speed=SPEED, lang=LANG)
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
