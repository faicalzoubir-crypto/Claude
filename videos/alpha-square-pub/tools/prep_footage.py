"""Prépare la vidéo du lieu (enregistrement d'écran Google Earth fourni par le client) pour la scène carte.

Source : assets/footage/source/lieu-google-earth.mov (HEVC 1036×1920, 30 i/s, piste son muette,
carton de fin CapCut à partir de 6,17 s).
Sortie : assets/footage/lieu-google-earth.mp4 (H.264 1080×1920, 30 i/s, sans son, 0–6,1 s).

1. Suit le repère rouge Google d'image en image.
2. Efface l'étiquette de coordonnées affichée au-dessus du repère (texte d'interface, chiffres)
   par retouche (inpainting) ; le reste de l'image n'est pas modifié.
3. Recadre autour du repère en 9:16 (702×1248 px source) pour sortir les boutons de l'application
   (recherche, calques, boussole, 2D, échelle), met à l'échelle en 1080×1920 (repère à x = 540, y ≈ 1011).

Usage : python tools/prep_footage.py   (numpy, opencv-python-headless ; ffmpeg dans le PATH)
"""
import subprocess
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "footage" / "source" / "lieu-google-earth.mov"
DST = ROOT / "assets" / "footage" / "lieu-google-earth.mp4"

W, H = 1036, 1920
FRAMES = 183  # 0–6,1 s, avant le carton CapCut (6,17 s)
CROP = (702, 1248, 167, 330)  # largeur, hauteur, x, y dans l'image source (9:16 exact)
# Étiquette de coordonnées : position fixe par rapport au repère (élément d'interface).
LABEL_DX = (-234, 228)  # par rapport au centre x du repère
LABEL_DY = (-50, -4)  # par rapport au haut de la tête du repère


def find_pin(rgb, prev):
    r, g, b = (rgb[..., i].astype(int) for i in range(3))
    m = (r > 190) & (g < 90) & (b < 90)
    if prev is None:
        x0, x1, y0, y1 = 300, 760, 600, 1150
    else:
        x0, x1, y0, y1 = prev[0] - 40, prev[0] + 40, prev[1] - 40, prev[1] + 90
    win = np.zeros_like(m)
    win[y0:y1, x0:x1] = True
    ys, xs = np.nonzero(m & win)
    if len(xs) < 20:
        return prev
    head = ys.min()
    body = ys < head + 60  # la tête et la pointe du repère, rien en dessous
    return int(round(np.median(xs[body]))), int(head)


def erase_label(rgb, pin):
    px, head = pin
    x0, x1 = px + LABEL_DX[0], px + LABEL_DX[1]
    y0, y1 = head + LABEL_DY[0], head + LABEL_DY[1]
    box = rgb[y0:y1, x0:x1]
    text = (box.min(axis=2) > 185).astype(np.uint8)
    text = cv2.dilate(text, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13)))
    mask = np.zeros(rgb.shape[:2], np.uint8)
    mask[y0:y1, x0:x1] = text * 255
    out = cv2.inpaint(rgb, mask, 7, cv2.INPAINT_TELEA)
    # fondu doux : léger flou limité à la zone retouchée
    soft = cv2.GaussianBlur(out, (0, 0), 2.2)
    a = cv2.GaussianBlur(mask.astype(np.float32) / 255, (0, 0), 3)[..., None]
    return (out * (1 - a) + soft * a).astype(np.uint8)


def main():
    DST.parent.mkdir(parents=True, exist_ok=True)
    dec = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-i", str(SRC), "-frames:v", str(FRAMES),
         "-vf", "scale=in_color_matrix=bt709:in_range=tv", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        stdout=subprocess.PIPE,
    )
    cw, ch, cx, cy = CROP
    enc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
         "-vf", f"crop={cw}:{ch}:{cx}:{cy},scale=1080:1920:flags=lanczos:out_color_matrix=bt709:out_range=tv,unsharp=5:5:0.45:3:3:0",
         "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-g", "15",
         "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
         "-movflags", "+faststart", "-an", str(DST)],
        stdin=subprocess.PIPE,
    )
    pin = None
    for i in range(FRAMES):
        buf = dec.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            raise SystemExit(f"image {i} manquante")
        rgb = np.frombuffer(buf, np.uint8).reshape(H, W, 3).copy()
        pin = find_pin(rgb, pin)
        enc.stdin.write(erase_label(rgb, pin).tobytes())
        if i % 30 == 0:
            print(f"t={i / 30:.1f} s  repère x={pin[0]} tête y={pin[1]}")
    enc.stdin.close()
    enc.wait()
    dec.wait()
    print(f"{DST.relative_to(ROOT)}  ok")


main()
