"""Generate the French voice-over lines with local Kokoro (voice ff_siwis).

usage: python3 tools/vo.py [speed]
Writes assets/vo/vo-0N.wav and prints each duration. "Moto Like" is forced to /laɪk/.
"""
import re, sys, json
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
from kokoro_onnx.tokenizer import Tokenizer

C = "/root/.cache/hyperframes/tts"
LINES = [
    "Et si chaque kilomètre vous coûtait moins d'un rial ? Voici le M vingt-six, signé Moto Like.",
    "Un moteur-roue de deux mille watts, intégré à la roue arrière. Sans embrayage : vous tournez, il avance.",
    "Sa batterie lithium amovible stocke trois virgule vingt-quatre kilowattheures : de cent à cent vingt kilomètres annoncés.",
    "Une simple prise suffit. La recharge complète ? Environ quatre dirhams cinquante, pour cent kilomètres.",
    "Démarrage N F C sans clé, alarme à distance, phare L E D, écran numérique, freins à disque hydrauliques, et double amortisseur.",
    "Résultat : moins d'un rial le kilomètre. Roulez plus, dépensez moins.",
    "Le M vingt-six, de Moto Like. L'économie intelligente commence ici.",
]
speed = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
k = Kokoro(f"{C}/models/kokoro-v1.0.onnx", f"{C}/voices/voices-v1.0.bin")
tok = Tokenizer()
out = []
for i, line in enumerate(LINES, 1):
    ph = tok.phonemize(line, lang="fr-fr")
    ph = re.sub(r"\((en|fr)\)", "", ph)          # drop espeak language-switch tags
    ph = ph.replace("lˈɪθiəm", "litjˈɔm")       # espeak reads "lithium" the English way
    audio, sr = k.create(ph, voice="ff_siwis", speed=speed, lang="fr-fr", is_phonemes=True)
    path = f"assets/vo/vo-{i:02d}.wav"
    sf.write(path, audio, sr)
    out.append({"line": i, "seconds": round(len(audio) / sr, 2), "phonemes": ph})
    print(f"vo-{i:02d}  {len(audio)/sr:5.2f}s  {ph}")
json.dump(out, open("assets/vo/vo.json", "w"), ensure_ascii=False, indent=1)
