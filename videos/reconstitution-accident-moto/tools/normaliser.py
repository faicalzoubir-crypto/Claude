#!/usr/bin/env python3
"""Met le son de la vidéo rendue à −14 LUFS (crête −1,5 dBTP), sans réencoder l'image.

Le rendu HyperFrames sort vers −23 LUFS ; la charte (brand/BRAND.md) vise −14.
Deux passes loudnorm : mesure, puis correction linéaire.

  python3 tools/normaliser.py livrables/compteur-vespa-13.mp4
"""
import json
import re
import subprocess
import sys
from pathlib import Path

CIBLE = "I=-14:TP=-1.5:LRA=11"

video = Path(sys.argv[1])
mesure = subprocess.run(
    ["ffmpeg", "-hide_banner", "-i", str(video), "-af", f"loudnorm={CIBLE}:print_format=json", "-f", "null", "-"],
    capture_output=True, text=True, check=True).stderr
m = json.loads(re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", mesure).group(0))
filtre = (f"loudnorm={CIBLE}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
          f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample=48000")
tmp = video.with_name(video.stem + ".norm" + video.suffix)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-c:v", "copy", "-af", filtre,
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(tmp)], check=True)
tmp.replace(video)
print(f"{video} : {m['input_i']} LUFS → −14 LUFS")
