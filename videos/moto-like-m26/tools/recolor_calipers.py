"""Tint the red brake calipers of the real close-ups to the green of the hero colourway
(the client's grey/green renders show green calipers).

usage: python3 tools/recolor_calipers.py -> assets/m26-ar/zoom-frein-*.webp
"""
import numpy as np
from PIL import Image

TARGET_HUE = 88 / 360  # Moto Like green
for name in ("frein-avant", "frein-arriere"):
    im = Image.open(f"assets/m26/zoom-{name}.webp").convert("RGB")
    hsv = np.array(im.convert("HSV")).astype(np.float32) / 255.0
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    red = ((h < 0.05) | (h > 0.94)) & (s > 0.42) & (v > 0.18)
    # soften the selection edge
    m = Image.fromarray((red * 255).astype(np.uint8)).resize(im.size).filter(__import__("PIL.ImageFilter", fromlist=["x"]).GaussianBlur(1.5))
    w = np.array(m).astype(np.float32) / 255.0
    h2 = h * (1 - w) + TARGET_HUE * w
    s2 = s * (1 - w) + np.minimum(s * 0.85, 0.8) * w
    v2 = v * (1 - w) + np.minimum(v * 1.12, 1) * w
    out = Image.fromarray((np.stack([h2, s2, v2], -1) * 255).astype(np.uint8), "HSV").convert("RGB")
    out.save(f"assets/m26-ar/zoom-{name}.webp", "WEBP", quality=88, method=6)
    print(name, "pixels tinted:", int(red.sum()))
