"""Exponentielle e — voix off convertie vers la voix de l'utilisateur (kNN-VC, local).

La voix off Siwis (assets/voice/NN.wav) garde son texte et son minutage exacts ; seul le
timbre est remplacé, image par image, par les sons les plus proches trouvés dans
l'échantillon de la voix de l'utilisateur (méthode kNN-VC : traits WavLM + vocodeur
HiFi-GAN). Les animations restent donc synchronisées sans rien recaler.

Chaque fichier converti garde exactement la durée de l'original (même plan, même timing).
L'échantillon de voix de l'utilisateur n'est pas versionné : on passe son chemin en argument.

Usage :
  python tools/voice_clone.py --knnvc <dossier knn-vc> --ref <voix.wav> [--ref …] [--only 01] [--topk 4]
Sortie : assets/voice-clone/NN.wav (24 kHz, comme les originaux).
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal

ROOT = Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--knnvc", required=True, help="dossier du dépôt bshall/knn-vc")
    ap.add_argument("--ref", action="append", required=True, help="échantillon(s) de la voix cible, 16 kHz mono")
    ap.add_argument("--only", action="append", help="numéro(s) de plan à convertir (ex. 01)")
    ap.add_argument("--topk", type=int, default=4)
    args = ap.parse_args()

    sys.path.insert(0, args.knnvc)
    import torch
    import torchaudio

    # torchaudio récent exige torchcodec pour lire un fichier ; soundfile suffit ici.
    def _load(path, *_, **__):
        data, rate = sf.read(path, dtype="float32", always_2d=True)
        return torch.from_numpy(data.T.copy()), rate

    torchaudio.load = _load
    from hubconf import knn_vc

    torch.set_num_threads(max(1, torch.get_num_threads()))
    model = knn_vc(pretrained=True, progress=False, prematched=True, device="cpu")
    matching_set = model.get_matching_set(args.ref)
    print(f"échantillon : {matching_set.shape[0]} trames ({matching_set.shape[0] * 0.02:.1f} s de voix)")

    out_dir = ROOT / "assets" / "voice-clone"
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "_src16k.wav"
    sources = sorted((ROOT / "assets" / "voice").glob("[0-9][0-9].wav"))
    for src in sources:
        if args.only and src.stem not in args.only:
            continue
        x, sr = sf.read(src)
        x16 = signal.resample_poly(x, 16000, sr)
        sf.write(tmp, x16.astype(np.float32), 16000)
        with torch.inference_mode():
            query = model.get_features(str(tmp))
            y = model.match(query, matching_set, topk=args.topk).cpu().numpy()
        y = signal.resample_poly(y, sr, 16000)
        # même durée que l'original, au échantillon près : le minutage du plan ne bouge pas
        y = np.pad(y, (0, max(0, len(x) - len(y))))[: len(x)]
        y *= 0.9 / (np.abs(y).max() + 1e-9)
        sf.write(out_dir / src.name, y.astype(np.float32), sr, subtype="PCM_16")
        print(f"{src.name}: {len(y) / sr:.2f}s")
    tmp.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
