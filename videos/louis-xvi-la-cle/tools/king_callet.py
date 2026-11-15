"""Callet 1786 → the King plate: oval-clipped cutout, red velvet coat recoloured to royal blue.
In: assets/src/callet-1786.jpg (3840x4677) + assets/src/callet-cut.png (remove-background).
Out: assets/img/king-royal.png (RGBA)."""
import numpy as np
from PIL import Image, ImageFilter
import colorsys, sys, os
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = Image.open(f"{P}/assets/src/callet-1786.jpg").convert("RGB")
cut = Image.open(f"{P}/assets/src/callet-cut.png").convert("RGBA")
W, H = src.size
rgb = np.asarray(src).astype(np.float32) / 255
alpha = np.asarray(cut)[..., 3].astype(np.float32) / 255

# 1. clip to the painted oval (inside the gilded frame), feathered
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
cx, cy, a, b = 1941, 2367, 1742 * 0.975, 2205 * 0.975
r = np.sqrt(((xx - cx) / a) ** 2 + ((yy - cy) / b) ** 2)
oval = np.clip((1.0 - r) / 0.07, 0, 1) ** 1.4
# the lower chest sinks into shadow above the caption band (display y 1150 → 1470 ⇔ source y 3200 → 4242)
sink = np.clip((4242 - yy) / (4242 - 3200), 0, 1) ** 1.6
alpha = alpha * oval * sink

# 2. recolour the coat: red/vermilion hues inside the coat region → deep royal blue
s = 3840 / 960  # preview coords (960 wide) → full res
def box(x0, y0, x1, y1):
    m = np.zeros((H, W), np.float32); m[int(y0*s):int(y1*s), int(x0*s):int(x1*s)] = 1; return m
region = np.clip(box(640, 545, 960, 1169) + box(500, 572, 640, 1169) + box(360, 585, 500, 1169), 0, 1)
region = region * (1 - box(340, 815, 478, 1120))          # keep the red bow and the hanging order
region = np.asarray(Image.fromarray((region*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(25))).astype(np.float32)/255
mx, mn = rgb.max(-1), rgb.min(-1)
sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
r_, g_, b_ = rgb[..., 0], rgb[..., 1], rgb[..., 2]
hue = np.degrees(np.arctan2(np.sqrt(3) * (g_ - b_), 2 * r_ - g_ - b_)) % 360   # 0 = red
hd = np.minimum(np.abs(hue - 8), 360 - np.abs(hue - 8))      # distance to vermilion
hw = np.clip((34 - hd) / 14, 0, 1)                            # 1 inside ±20°, fades to 0 at ±34°
sw = np.clip((sat - 0.18) / 0.15, 0, 1)
w = (hw * sw * region)[..., None]
# target: royal blue keeping the velvet's light structure (luminance) but darker overall
lum = (0.299 * r_ + 0.587 * g_ + 0.114 * b_)[..., None]
deep = np.array([0.025, 0.045, 0.15], np.float32)               # shadow blue  (~#060B26)
lite = np.array([0.30, 0.38, 0.62], np.float32)                 # sheen blue   (~#4D619E)
t = np.clip((lum - 0.10) / 0.70, 0, 1) ** 1.35
blue = deep + (lite - deep) * t
out = rgb * (1 - w) + blue * w
rgba = np.dstack([np.clip(out, 0, 1), alpha])
Image.fromarray((rgba * 255).astype(np.uint8), "RGBA").save(f"{P}/assets/img/king-royal.png", optimize=False)
prev = Image.new("RGBA", (W, H), (35, 45, 40, 255)); prev.alpha_composite(Image.open(f"{P}/assets/img/king-royal.png"))
prev.convert("RGB").resize((960, 1169)).save(sys.argv[1] if len(sys.argv) > 1 else "/dev/null", "JPEG", quality=85)
