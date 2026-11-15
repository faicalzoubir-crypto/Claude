"""Background plates: vertical crops (no lettering) from the period works, toned for their light.
Coordinates are in the 3840-px sources (assets/src). Out: assets/img/*.jpg (and foule.png, RGBA).
Usage: python3 tools/plates.py [preview_dir]"""
import os, sys
import cv2
import numpy as np
from PIL import Image

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC, OUT = f"{P}/assets/src", f"{P}/assets/img"
PREV = sys.argv[1] if len(sys.argv) > 1 else None


def load(name, box):
    x0, y0, x1, y1 = box
    im = np.asarray(Image.open(f"{SRC}/{name}").convert("RGB")).astype(np.float32) / 255
    return im[y0:y1, x0:x1]


def gradient_map(img, stops):
    lum = img @ np.array([0.299, 0.587, 0.114], np.float32)
    xs = np.array([s[0] for s in stops], np.float32)
    out = np.empty(lum.shape + (3,), np.float32)
    for c in range(3):
        out[..., c] = np.interp(lum, xs, np.array([s[1][c] for s in stops], np.float32) / 255)
    return out


def save(img, name, alpha=None):
    img = np.clip(img, 0, 1)
    if alpha is None:
        Image.fromarray((img * 255).astype(np.uint8)).save(f"{OUT}/{name}.jpg", quality=92)
    else:
        rgba = np.dstack([img, np.clip(alpha, 0, 1)])
        Image.fromarray((rgba * 255).astype(np.uint8), "RGBA").save(f"{OUT}/{name}.png")
    if PREV:
        pv = img if alpha is None else img * alpha[..., None] + np.array([0.2, 0.27, 0.23]) * (1 - alpha[..., None])
        Image.fromarray((np.clip(pv, 0, 1) * 255).astype(np.uint8)).resize(
            (540, int(540 * img.shape[0] / img.shape[1]))).save(f"{PREV}/plate-{name}.jpg", quality=85)
    print(name, img.shape[1], "x", img.shape[0])


# VERSE — the Galerie des Glaces at night (Cochin, Bal masqué, 1745/46): candle-gold tone
g = load("galerie-bal-masque-1746.jpg", (1440, 149, 2494, 2021))
save(gradient_map(g, [(0.00, (12, 7, 3)), (0.30, (58, 30, 12)), (0.62, (150, 92, 40)),
                      (0.85, (222, 172, 104)), (1.00, (250, 222, 166))]), "galerie")

# REFRAIN 1 — far: the Cour de Marbre, 5-6 October 1789, grey dawn
c = load("cour-de-marbre-1789.jpg", (1361, 365, 2407, 2213))
dawn = gradient_map(c, [(0.00, (18, 22, 28)), (0.40, (70, 80, 92)), (0.78, (150, 158, 166)),
                        (1.00, (206, 208, 204))])
h, w = dawn.shape[:2]
y = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
horizon = 0.235                       # the palace roofline, as a fraction of the crop height
glow = np.exp(-((y - horizon) / 0.07) ** 2) * (y < horizon + 0.04)
dawn = dawn * (1 - 0.28 * glow) + np.array([0.86, 0.74, 0.62], np.float32) * 0.28 * glow
save(dawn, "cour")

# REFRAIN 1 — near: the women's march (À Versailles, à Versailles, 1789), keyed off the paper
f = load("a-versailles-1789.jpg", (240, 520, 3624, 2252))
paper = np.median(f[:60, :].reshape(-1, 3), axis=0)
diff = np.abs(f - paper).max(axis=2)
ink = np.clip((diff - 0.06) / 0.10, 0, 1)
hgt = f.shape[0]
split = int(hgt * 0.24)               # above: pikes and heads (thin key); below: bodies (closed, filled)
body = (ink > 0.5).astype(np.uint8) * 255
body = cv2.morphologyEx(body, cv2.MORPH_CLOSE, np.ones((31, 31), np.uint8))
flood = body.copy()
cv2.floodFill(flood, np.zeros((body.shape[0] + 2, body.shape[1] + 2), np.uint8), (0, 0), 255)
body = body | cv2.bitwise_not(flood)
body = cv2.GaussianBlur(body, (9, 9), 0).astype(np.float32) / 255
ramp = np.clip((np.arange(hgt, dtype=np.float32) - split) / 120, 0, 1)[:, None]
alpha = np.maximum(ink, body * ramp)
lum = f @ np.array([0.299, 0.587, 0.114], np.float32)
crowd = f * 0.45 + lum[..., None] * 0.55                         # muted, colours still there
crowd = crowd * np.array([0.60, 0.64, 0.72], np.float32)         # backlit by a cold dawn
save(crowd, "foule", alpha)

# FINAL REFRAIN — the Place de la Révolution (Demachy, 1793): crop keeps the guillotine out of frame
p = load("demachy-execution-1793.jpg", (288, 149, 1685, 2623))
lum = (p @ np.array([0.299, 0.587, 0.114], np.float32))[..., None]
cold = (p * 0.35 + lum * 0.65) * np.array([0.84, 0.90, 1.00], np.float32)
h = cold.shape[0]
y = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
fog = 0.16 + 0.24 * np.exp(-((y - 0.50) / 0.16) ** 2)
cold = cold * (1 - fog) + np.array([0.60, 0.64, 0.68], np.float32) * fog
save(cold * 0.92, "place")

# OUTRO — torches: the fire and smoke of Houël's Prise de la Bastille (1789)
save(load("houel-bastille-1789.jpg", (2236, 53, 3762, 2813)), "feu")

# OUTRO — the crown's backdrop: smoke over the Place de la Révolution (Demachy, Fête de l'Unité, 1793)
save(load("demachy-unite-1793.jpg", (456, 36, 1805, 2431)), "fumee")
