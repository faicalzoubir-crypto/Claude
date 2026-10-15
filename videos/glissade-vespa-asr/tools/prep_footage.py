"""Prépare la vidéo embarquée pour la composition.

- coupe la source à 0–9 s (la fin de CapCut et l'après-chute ne sont pas utilisées) ;
- floute la plaque du SUV sombre devant (suivie image par image) et sa vitre latérale
  (conducteur visible) quand on le double ;
- encode en H.264 25 i/s avec le son d'origine.

Usage : python3 tools/prep_footage.py            (numpy, Pillow, ffmpeg)
        python3 tools/prep_footage.py --check    (planche de contrôle des zones floutées)
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets/footage/source/accident-camera-embarquee.mov"
OUT = ROOT / "assets/footage/accident-floute.mp4"
W, H, FPS = 1080, 1920, 25
DUR = 9.0
N = int(DUR * FPS)

# Plaque : centres repérés à la main (coordonnées pleine résolution), affinés par suivi.
PLATE_KEYS = {0: (630, 685), 6: (635, 704), 12: (677, 711), 18: (754, 723), 24: (884, 740), 30: (1065, 763)}
PLATE_LAST = 34  # la plaque sort du cadre à droite
# Second SUV à droite (vu de trois quarts arrière) : zone arrière floutée tant qu'il est dans le cadre.
SUV2_KEYS = {0: (840, 560, 120, 90), 6: (1020, 520, 150, 110), 10: (1100, 520, 150, 110)}
# Vitres latérales du SUV quand on le double (x, y, w, h) — boîtes larges, conducteur compris.
WINDOW_KEYS = {
    27: (690, 560, 260, 150),
    30: (690, 560, 330, 160),
    36: (840, 520, 260, 200),
    42: (900, 520, 200, 250),
    46: (960, 560, 140, 220),
    50: (1010, 620, 90, 160),
}


def interp(keys, f):
    ks = sorted(keys)
    if f <= ks[0]:
        return keys[ks[0]]
    if f >= ks[-1]:
        return keys[ks[-1]]
    for a, b in zip(ks, ks[1:]):
        if a <= f <= b:
            t = (f - a) / (b - a)
            return tuple(va + (vb - va) * t for va, vb in zip(keys[a], keys[b]))


def read_frames():
    cmd = ["ffmpeg", "-v", "error", "-i", str(SRC), "-t", str(DUR), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    size = W * H * 3
    while True:
        b = p.stdout.read(size)
        if len(b) < size:
            break
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3)
    p.wait()


def track_plate(frames):
    """Affine les centres de plaque par corrélation normalisée autour de la position interpolée."""
    centers = {}
    tw, th = 56, 20
    tmpl = None
    for f in range(0, PLATE_LAST + 1):
        g = frames[f].astype(np.float32).mean(axis=2)
        cx, cy = interp(PLATE_KEYS, f)
        cx, cy = int(cx), int(cy)
        if tmpl is None:
            centers[f] = (cx, cy)
        else:
            best, bxy = -2, (cx, cy)
            for dy in range(-24, 25, 2):
                for dx in range(-30, 31, 2):
                    x0, y0 = cx + dx - tw // 2, cy + dy - th // 2
                    if x0 < 0 or y0 < 0 or x0 + tw > W or y0 + th > H:
                        continue
                    patch = g[y0 : y0 + th, x0 : x0 + tw]
                    a = patch - patch.mean()
                    den = np.sqrt((a * a).sum() * (tmpl * tmpl).sum()) + 1e-6
                    s = (a * tmpl).sum() / den
                    if s > best:
                        best, bxy = s, (cx + dx, cy + dy)
            # on garde le suivi seulement s'il est franc ; sinon la position interpolée
            centers[f] = bxy if best > 0.55 else (cx, cy)
        x, y = centers[f]
        x0, y0 = max(0, x - tw // 2), max(0, y - th // 2)
        patch = g[y0 : y0 + th, x0 : x0 + tw]
        if patch.shape == (th, tw):
            tmpl = patch - patch.mean()
    return centers


def boxes_for(f, plate):
    out = []
    if f in plate:
        x, y = plate[f]
        s = 1.0 + 0.6 * max(0, f - 18) / 16  # la plaque grossit en se rapprochant
        out.append((x - 75 * s, y - 34 * s, 150 * s, 68 * s))
    if f <= 12:
        out.append(interp(SUV2_KEYS, f))
    if 27 <= f <= 52:
        out.append(interp(WINDOW_KEYS, f))
    return out


def blur_boxes(frame, boxes):
    im = Image.fromarray(frame)
    for x, y, w, h in boxes:
        x0, y0 = int(max(0, x)), int(max(0, y))
        x1, y1 = int(min(W, x + w)), int(min(H, y + h))
        if x1 - x0 < 4 or y1 - y0 < 4:
            continue
        pad = 24
        X0, Y0, X1, Y1 = max(0, x0 - pad), max(0, y0 - pad), min(W, x1 + pad), min(H, y1 + pad)
        region = im.crop((X0, Y0, X1, Y1))
        blurred = region.resize((max(1, (X1 - X0) // 10), max(1, (Y1 - Y0) // 10)), Image.BILINEAR)
        blurred = blurred.resize(region.size, Image.BILINEAR).filter(ImageFilter.GaussianBlur(10))
        mask = Image.new("L", region.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((x0 - X0, y0 - Y0, x1 - X0, y1 - Y0), radius=18, fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(6))
        region.paste(blurred, (0, 0), mask)
        im.paste(region, (X0, Y0))
    return np.asarray(im)


def main():
    frames = list(read_frames())
    plate = track_plate(frames)
    if "--check" in sys.argv:
        tiles = []
        for f in range(0, 54, 3):
            im = Image.fromarray(blur_boxes(frames[f], boxes_for(f, plate))).crop((400, 380, 1080, 960)).resize((340, 290))
            ImageDraw.Draw(im).text((4, 4), f"f{f}", fill="yellow")
            tiles.append(im)
        sheet = Image.new("RGB", (340 * 6, 290 * 3))
        for i, t in enumerate(tiles):
            sheet.paste(t, ((i % 6) * 340, (i // 6) * 290))
        out = Path(sys.argv[sys.argv.index("--check") + 1]) if len(sys.argv) > sys.argv.index("--check") + 1 else ROOT / "blur-check.jpg"
        sheet.save(out, quality=88)
        print("planche :", out)
        return
    enc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-ss", "0", "-t", str(DUR), "-i", str(SRC), "-map", "0:v", "-map", "1:a",
         "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
         "-c:a", "aac", "-b:a", "192k", "-shortest", str(OUT)],
        stdin=subprocess.PIPE,
    )
    for f, fr in enumerate(frames):
        b = boxes_for(f, plate)
        enc.stdin.write((blur_boxes(fr, b) if b else fr).tobytes())
    enc.stdin.close()
    enc.wait()
    print("écrit :", OUT)


if __name__ == "__main__":
    main()
