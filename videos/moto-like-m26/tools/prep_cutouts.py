"""Build the M26 image layers used by the compositions from the BiRefNet cutouts.

usage: python3 tools/prep_cutouts.py
Inputs : source/cutouts/*.png (raw BiRefNet cutouts) + tools/cutout-specs/*.json
Outputs: assets/m26/*.webp, *.png masks, assets/m26/layout.json (positions in % of each image)
"""
import json, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from skimage import measure

from m26lib import polar_inpaint

SRC, OUT = "source/cutouts", "assets/m26"



layout = {}

def trim(im, pad=12):
    a = np.array(im.getchannel("A"))
    ys, xs = np.where(a > 10)
    box = (max(xs.min() - pad, 0), max(ys.min() - pad, 0),
           min(xs.max() + pad, im.width), min(ys.max() + pad, im.height))
    box = tuple(int(v) for v in box)
    return im.crop(box), box

def save(im, name, q=90):
    im.save(f"{OUT}/{name}.webp", "WEBP", quality=q, method=6)

# 1. side profile: remove the neighbouring scooters, then trim
subprocess.run([sys.executable, "tools/clean_cutout.py", f"{SRC}/m26-profil-gauche.png",
                "tools/cutout-specs/profil-gauche.json", "/tmp/m26-profil-clean.png"], check=True)
prof = Image.open("/tmp/m26-profil-clean.png").convert("RGBA")
prof_t, box = trim(prof)
ox, oy = box[0], box[1]
W, H = prof_t.size
save(prof_t, "profil")

# riding variant: centre stand removed
ride = prof_t.copy()
d = ImageDraw.Draw(ride)
d.rectangle([880 - ox, 1478 - oy, 1100 - ox, H], fill=(0, 0, 0, 0))
save(ride, "profil-roule")

# wheels: rotating discs + fixed masks that leave the occluding parts (fork, fender, shock, swingarm) static
wheels = {
    "rear": {"c": (426, 1449), "r": 312, "occ": [
        [(40, 1080), (430, 1040), (410, 1190), (310, 1250), (372, 1352), (350, 1425), (305, 1425), (250, 1305), (185, 1290), (120, 1395), (40, 1400)],
        [(378, 1150), (500, 1040), (650, 1050), (630, 1160), (525, 1310), (470, 1410), (420, 1425), (378, 1385)],
        [(325, 1478), (360, 1440), (560, 1418), (760, 1378), (900, 1378), (900, 1462), (700, 1492), (560, 1524), (420, 1534), (325, 1534)],
        [(600, 1000), (900, 1000), (900, 1395), (705, 1420), (625, 1300)],
    ]},
    "front": {"c": (2164, 1514), "r": 292, "occ": [
        [(1866, 1030), (1962, 1010), (2116, 1440), (2096, 1530), (2036, 1530), (1986, 1425), (1876, 1205)],
        [(1985, 1050), (2300, 1072), (2425, 1175), (2452, 1335), (2380, 1342), (2220, 1312), (2110, 1312), (2078, 1392), (2008, 1360), (1985, 1200)],
        [(1700, 900), (1880, 900), (1880, 1700), (1700, 1700)],
    ]},
}
layout["profil"] = {"w": W, "h": H, "wheels": {}}
for name, wd in wheels.items():
    cx, cy, r = wd["c"][0] - ox, wd["c"][1] - oy, wd["r"]
    size = 2 * r
    disc = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    disc.paste(prof_t.crop((cx - r, cy - r, cx + r, cy + r)), (0, 0))
    circle = Image.new("L", (size, size), 0)
    ImageDraw.Draw(circle).ellipse([2, 2, size - 2, size - 2], fill=255)
    disc.putalpha(Image.fromarray(np.minimum(np.array(disc.getchannel("A")), np.array(circle))))
    mask = circle.copy()
    md = ImageDraw.Draw(mask)
    for poly in wd["occ"]:
        md.polygon([(x - ox - (cx - r), y - oy - (cy - r)) for x, y in poly], fill=0)
    disc = polar_inpaint(disc, np.array(mask) < 128, r)
    save(disc, f"roue-{name}", q=92)
    # spinning version: rotational motion blur (average of small rotations)
    acc = np.zeros((size, size, 4), np.float32)
    angles = np.linspace(-9, 9, 13)
    for ang in angles:
        acc += np.array(disc.rotate(float(ang), resample=Image.BICUBIC)).astype(np.float32)
    save(Image.fromarray((acc / len(angles)).astype(np.uint8), "RGBA"), f"roue-{name}-flou", q=90)
    mask = mask.filter(ImageFilter.GaussianBlur(2.5))
    mask_rgba = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    mask_rgba.putalpha(mask)
    mask_rgba.save(f"{OUT}/roue-{name}-masque.png")
    layout["profil"]["wheels"][name] = {
        "left": round(100 * (cx - r) / W, 3), "top": round(100 * (cy - r) / H, 3),
        "w": round(100 * size / W, 3), "h": round(100 * size / H, 3),
        "cx": round(100 * cx / W, 3), "cy": round(100 * cy / H, 3)}

# silhouette contour for the light-line trace (SVG path in image px of the trimmed profile)
a = np.array(prof_t.getchannel("A").filter(ImageFilter.GaussianBlur(3))) > 110
contours = measure.find_contours(a.astype(float), 0.5)
contours.sort(key=len, reverse=True)
paths = []
for c in contours[:6]:
    if len(c) < 200:
        continue
    poly = measure.approximate_polygon(c, tolerance=2.2)
    paths.append("M" + " L".join(f"{p[1]:.0f},{p[0]:.0f}" for p in poly) + " Z")
layout["profil"]["outline"] = paths

# other views
for src, name in [("m26-trois-quarts-avant-gauche", "trois-quarts-avant"),
                  ("m26-trois-quarts-arriere-droit", "trois-quarts-arriere"),
                  ("m26-face-phare", "face"), ("logo-moto-like", "logo")]:
    im = Image.open(f"{SRC}/{src}.png").convert("RGBA")
    if name == "logo":
        # keep the white inside of the badge: fill the holes of the cutout mask
        from scipy.ndimage import binary_fill_holes
        full = binary_fill_holes(np.array(im.getchannel("A")) > 128)
        alpha = Image.fromarray((full * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
        im = Image.open("source/logo-moto-like.jpg").convert("RGBA")
        im.putalpha(alpha)
    im, b = trim(im)
    save(im, name)
    layout[name] = {"w": im.width, "h": im.height, "crop": [int(v) for v in b]}

json.dump(layout, open(f"{OUT}/layout.json", "w"), indent=1)
print(json.dumps({k: (v["w"], v["h"]) for k, v in layout.items()}))
print("wheels", layout["profil"]["wheels"])
print("outline paths", [len(p) for p in paths])
