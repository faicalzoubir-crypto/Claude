"""Ducreux, January 1793 (CC0, Carnavalet D.7108) → the King of the final refrain.
Cutout alpha from remove-background; coat toned royal blue, face/wig/shirt cold dawn; sheet edges feathered;
mirrored so he faces the same way as the Callet. Out: assets/img/king-1793.webp (RGBA, 1600 px wide)."""
import os
import cv2
import numpy as np
from PIL import Image

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = np.asarray(Image.open(f"{P}/assets/src/ducreux-1793.jpg").convert("RGB")).astype(np.float32) / 255
alpha = np.asarray(Image.open(f"{P}/assets/src/ducreux-cut.png"))[..., 3].astype(np.float32) / 255
H, W = alpha.shape
lum = src @ np.array([0.299, 0.587, 0.114], np.float32)


def gmap(l, stops):
    xs = np.array([s[0] for s in stops], np.float32)
    return np.stack([np.interp(l, xs, np.array([s[1][c] for s in stops], np.float32) / 255) for c in range(3)], -1)


# the coat: below the collar line (unmirrored coords, measured on a 960-wide preview, ×4)
poly = np.array([(0, 1010), (130, 945), (250, 880), (285, 875), (380, 935), (470, 1000), (505, 1040), (560, 1035),
                 (640, 1005), (700, 995), (790, 1040), (880, 1100), (960, 1150), (960, 1577), (0, 1577)], np.float32) * 4
coat = np.zeros((H, W), np.uint8)
cv2.fillPoly(coat, [poly.astype(np.int32)], 255)
coat = cv2.GaussianBlur(coat, (0, 0), 14).astype(np.float32)[..., None] / 255

l = np.clip((lum - 0.18) / 0.72, 0, 1)
blue = gmap(l, [(0.0, (8, 11, 26)), (0.45, (34, 44, 82)), (0.75, (64, 80, 128)), (1.0, (150, 160, 192))])
skin = gmap(l, [(0.0, (22, 22, 26)), (0.45, (104, 96, 94)), (0.75, (170, 158, 148)), (1.0, (236, 236, 232))])
rgb = blue * coat + skin * (1 - coat)

# feather the drawing sheet's straight edges (sides and bottom) into the air
x = np.linspace(0, 1, W, dtype=np.float32)[None, :]
y = np.linspace(0, 1, H, dtype=np.float32)[:, None]
side = np.clip(x / 0.09, 0, 1) * np.clip((1 - x) / 0.09, 0, 1)
bottom = np.clip((0.93 - y) / 0.22, 0, 1)
a = alpha * side ** 1.5 * bottom ** 1.2

rgba = np.dstack([np.clip(rgb, 0, 1), a])[:, ::-1]               # mirror
im = Image.fromarray((rgba * 255).astype(np.uint8), "RGBA")
im = im.resize((1600, round(1600 * H / W)), Image.LANCZOS)
im.save(f"{P}/assets/img/king-1793.webp", quality=90, method=6)
print("king-1793", im.size)

# the Callet plate, downsized for the 4K render (its widest use is 1180 px × 1.13 push × 2 = 2670 px)
k = Image.open(f"{P}/assets/img/king-royal.png")
k = k.resize((2800, round(2800 * k.height / k.width)), Image.LANCZOS)
k.save(f"{P}/assets/img/king-royal.webp", quality=92, method=6)
print("king-royal", k.size)
