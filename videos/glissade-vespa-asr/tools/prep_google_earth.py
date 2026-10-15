"""Prépare les images Google Earth (enregistrement d'écran de l'appli, vertical 1038×1920).

Le cadrage x 0–850 retire tous les boutons de l'appli (recherche, calques, boussole,
Street View, 2D, échelle) ; il est mis à l'échelle en 1080×1920.

- assets/footage/ge-etablissement.mp4 : vue rasante avec horizon (source 9,4–14,85 s), muette ;
- assets/images/ge-plan.jpg : vue plongeante figée (source 0,5 s, identique à path.png sans le tracé),
  en 2160×3840 pour supporter le zoom sur le point de glissade.

Usage : python3 tools/prep_google_earth.py   (Pillow, ffmpeg)
"""
import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets/footage/source/google-earth-ecran-telephone.mov"
CLIP = ROOT / "assets/footage/ge-etablissement.mp4"
PLATE = ROOT / "assets/images/ge-plan.jpg"

# fenêtre de recadrage (coordonnées source) — même largeur 850 pour les deux
CLIP_CROP = (0, 205, 850, 1510)  # x, y, w, h
PLATE_CROP = (0, 135, 850, 1510)


def main():
    x, y, w, h = CLIP_CROP
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-ss", "9.4", "-t", "5.45", "-i", str(SRC), "-an",
         "-vf", f"crop={w}:{h}:{x}:{y},scale=1080:1920:flags=lanczos,fps=30",
         "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-g", "30", "-keyint_min", "30", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(CLIP)],
        check=True,
    )
    tmp = ROOT / "assets/images/.ge-frame.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "0.5", "-i", str(SRC), "-frames:v", "1", str(tmp)], check=True)
    x, y, w, h = PLATE_CROP
    Image.open(tmp).convert("RGB").crop((x, y, x + w, y + h)).resize((2160, 3840), Image.LANCZOS).save(PLATE, quality=92)
    tmp.unlink()
    print("écrit :", CLIP, PLATE)


if __name__ == "__main__":
    main()
