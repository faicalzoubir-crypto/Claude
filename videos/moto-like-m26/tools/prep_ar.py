"""Image layers for the Arabic version: the three M26 colourways from the client's product sheet.

usage: python3 tools/prep_ar.py
Inputs : source/cutouts/ar/*.png (BiRefNet cutouts of source/ar/crops, already upscaled x2)
Outputs: assets/m26-ar/*.webp, wheel discs + masks for the grey/green profile, assets/m26-ar/layout.json
The renders face LEFT: front wheel on the left, rear wheel on the right.
"""
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import label
from skimage import measure

from m26lib import polar_inpaint  # same ring-completion used for the French version

SRC, OUT = "source/cutouts/ar", "assets/m26-ar"
layout = {}


def clean(im):
    """Keep the largest opaque component (drops slivers of the neighbouring views), sharpen a touch."""
    a = np.array(im.getchannel("A"))
    lab, n = label(a > 24)
    if n > 1:
        sizes = np.bincount(lab.ravel())
        sizes[0] = 0
        keep = lab == sizes.argmax()
        keep = np.array(Image.fromarray((keep * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5))) > 0
        a = np.where(keep, a, 0)
    rgb = im.convert("RGB").filter(ImageFilter.UnsharpMask(radius=2, percent=55, threshold=2))
    out = rgb.convert("RGBA")
    out.putalpha(Image.fromarray(a.astype(np.uint8)))
    return out


def trim(im, pad=10):
    a = np.array(im.getchannel("A"))
    ys, xs = np.where(a > 10)
    box = (int(max(xs.min() - pad, 0)), int(max(ys.min() - pad, 0)),
           int(min(xs.max() + pad, im.width)), int(min(ys.max() + pad, im.height)))
    return im.crop(box), box


for colour in ("vert", "blanc", "noir"):
    for view in ("profil", "face"):
        im, box = trim(clean(Image.open(f"{SRC}/{view}-{colour}.png").convert("RGBA")))
        im.save(f"{OUT}/{view}-{colour}.webp", "WEBP", quality=92, method=6)
        layout[f"{view}-{colour}"] = {"w": im.width, "h": im.height, "box": list(box)}

# wheels of the grey/green profile (coordinates in the untrimmed cutout, front wheel on the left)
prof = Image.open(f"{OUT}/profil-vert.webp").convert("RGBA")
ox, oy = layout["profil-vert"]["box"][:2]
W, H = prof.size
wheels = {
    "front": {"c": (195, 880), "r": 186, "occ": [
        [(0, 600), (420, 600), (420, 792), (0, 792)],                 # fender and everything above the hub line
        [(212, 620), (296, 620), (288, 905), (222, 905)],             # fork leg
        [(228, 852), (306, 852), (306, 985), (228, 985)],             # caliper
    ]},
    "rear": {"c": (1175, 900), "r": 178, "occ": [
        [(960, 600), (1420, 600), (1420, 828), (960, 828)],           # fender, shock top
        [(1122, 750), (1222, 750), (1222, 905), (1122, 905)],         # shock body and mount
        [(1210, 866), (1306, 866), (1306, 995), (1210, 995)],         # caliper
    ]},
}
layout["profil-vert"]["wheels"] = {}
for name, wd in wheels.items():
    cx, cy, r = wd["c"][0] - ox, wd["c"][1] - oy, wd["r"]
    size = 2 * r
    disc = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    disc.paste(prof.crop((cx - r, cy - r, cx + r, cy + r)), (0, 0))
    circle = Image.new("L", (size, size), 0)
    ImageDraw.Draw(circle).ellipse([2, 2, size - 2, size - 2], fill=255)
    disc.putalpha(Image.fromarray(np.minimum(np.array(disc.getchannel("A")), np.array(circle))))
    mask = circle.copy()
    md = ImageDraw.Draw(mask)
    for poly in wd["occ"]:
        md.polygon([(x - ox - (cx - r), y - oy - (cy - r)) for x, y in poly], fill=0)
    disc = polar_inpaint(disc, np.array(mask) < 128, r)
    disc.save(f"{OUT}/roue-{name}.webp", "WEBP", quality=92, method=6)
    acc = np.zeros((size, size, 4), np.float32)
    for ang in np.linspace(-9, 9, 13):
        acc += np.array(disc.rotate(float(ang), resample=Image.BICUBIC)).astype(np.float32)
    Image.fromarray((acc / 13).astype(np.uint8), "RGBA").save(f"{OUT}/roue-{name}-flou.webp", "WEBP", quality=90, method=6)
    mrgba = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    mrgba.putalpha(mask.filter(ImageFilter.GaussianBlur(2.5)))
    mrgba.save(f"{OUT}/roue-{name}-masque.png")
    layout["profil-vert"]["wheels"][name] = {
        "left": round(100 * (cx - r) / W, 3), "top": round(100 * (cy - r) / H, 3),
        "w": round(100 * size / W, 3), "h": round(100 * size / H, 3)}

# riding variant: centre stand removed (it hangs below the frame between the wheels)
ride = prof.copy()
ImageDraw.Draw(ride).rectangle([720 - ox, 946 - oy, 1000 - ox, H], fill=(0, 0, 0, 0))
ride.save(f"{OUT}/profil-vert-roule.webp", "WEBP", quality=92, method=6)

# silhouette outline for the light-line trace
a = np.array(prof.getchannel("A").filter(ImageFilter.GaussianBlur(2))) > 110
cs = sorted(measure.find_contours(a.astype(float), 0.5), key=len, reverse=True)
poly = measure.approximate_polygon(cs[0], tolerance=1.6)
layout["profil-vert"]["outline"] = ["M" + " L".join(f"{p[1]:.0f},{p[0]:.0f}" for p in poly) + " Z"]

json.dump(layout, open(f"{OUT}/layout.json", "w"), indent=1)
print({k: (v["w"], v["h"]) for k, v in layout.items()})
print("wheels", layout["profil-vert"]["wheels"])
