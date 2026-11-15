"""Cut out the montage objects and the key from their museum photos (public domain / CC0).
Out (assets/img): cle.png, couronne.png, trone.png, cadran.png — RGBA, trimmed to content.
Usage: python3 tools/objects.py [preview_dir]"""
import os, sys
import cv2
import numpy as np
from PIL import Image

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC, OUT = f"{P}/assets/src", f"{P}/assets/img"
PREV = sys.argv[1] if len(sys.argv) > 1 else None


def largest_components(mask, keep=1, min_frac=0.02):
    n, lab, stats, _ = cv2.connectedComponentsWithStats((mask > 127).astype(np.uint8), 8)
    if n <= 1:
        return mask
    areas = stats[1:, cv2.CC_STAT_AREA]
    order = np.argsort(areas)[::-1][:keep]
    out = np.zeros_like(mask)
    for i in order:
        if areas[i] >= min_frac * areas[order[0]]:
            out[lab == i + 1] = 255
    return out


def fill_holes(mask):
    h, w = mask.shape
    flood = mask.copy()
    cv2.floodFill(flood, np.zeros((h + 2, w + 2), np.uint8), (0, 0), 255)
    return mask | cv2.bitwise_not(flood)


def save_rgba(rgb_bgr, alpha, name, pad=12):
    ys, xs = np.where(alpha > 8)
    y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad, alpha.shape[0])
    x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad, alpha.shape[1])
    rgba = np.dstack([cv2.cvtColor(rgb_bgr, cv2.COLOR_BGR2RGB), alpha])[y0:y1, x0:x1]
    Image.fromarray(rgba, "RGBA").save(f"{OUT}/{name}.png")
    if PREV:
        im = Image.fromarray(rgba, "RGBA")
        bg = Image.new("RGBA", im.size, (52, 70, 60, 255)); bg.alpha_composite(im)
        bg.convert("RGB").save(f"{PREV}/obj-{name}.jpg", quality=85)
    print(name, rgba.shape)


# ---------- the key (Met 89207, 18th c.) ----------
img = cv2.imread(f"{SRC}/cle-met-89207.jpg")
h, w = img.shape[:2]
small = cv2.resize(img, (w // 2, h // 2))
gc = np.zeros(small.shape[:2], np.uint8)
bgd, fgd = np.zeros((1, 65)), np.zeros((1, 65))
cv2.grabCut(small, gc, (20, 100, 930, 310), bgd, fgd, 8, cv2.GC_INIT_WITH_RECT)
m = np.where((gc == 1) | (gc == 3), 255, 0).astype(np.uint8)
m = cv2.resize(m, (w, h), interpolation=cv2.INTER_LINEAR)
# rebuild the quatrefoil bow: mirror its clean right half onto the cracked left half
cx, cy, R = 335, 585, 238
yy, xx = np.mgrid[0:h, 0:w]
in_left = ((xx - cx) ** 2 + (yy - cy) ** 2 <= R * R) & (xx < cx)
mx = np.clip(2 * cx - xx, 0, w - 1)
img[in_left] = img[yy[in_left], mx[in_left]]
m[in_left] = m[yy[in_left], mx[in_left]]
# close the crack across the shank: fill the axis band and inpaint the photo there
band = np.zeros_like(m)
cv2.rectangle(band, (1150, 555), (1330, 610), 255, -1)
gap = band & cv2.bitwise_not(m)
img = cv2.inpaint(img, gap, 7, cv2.INPAINT_TELEA)
m = m | gap
m = largest_components(m, keep=1)
m = cv2.GaussianBlur(m, (3, 3), 0)
# tone: old dark iron, one warm candle edge from the upper left
g = cv2.bilateralFilter(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 9, 40, 9).astype(np.float32) / 255
g = np.clip((g - 0.30) / 0.55, 0, 1)
dark = np.array([20, 19, 18], np.float32)      # BGR: near-black iron
lite = np.array([158, 164, 170], np.float32)   # worn steel highlight
iron = dark + (lite - dark) * (g[..., None] ** 1.6)
edge = cv2.Sobel(cv2.GaussianBlur(g, (0, 0), 3), cv2.CV_32F, 0, 1, ksize=5)
warm = np.clip(-edge * 0.9, 0, 1)[..., None] * np.array([60, 140, 225], np.float32)
key = np.clip(iron + warm * 0.45, 0, 255).astype(np.uint8)
save_rgba(key, m, "cle")

# ---------- the crown (Louis XV, Louvre; photo on black) ----------
img = cv2.imread(f"{SRC}/couronne-louis-xv.jpg")
v = img.max(axis=2).astype(np.float32) / 255
a = np.clip((v - 0.07) / 0.16, 0, 1)
a = (a * 255).astype(np.uint8)
a = largest_components(np.where(a > 40, 255, 0).astype(np.uint8), keep=3) & a
save_rgba(img, cv2.GaussianBlur(a, (3, 3), 0), "couronne")

# ---------- the empty throne (Habsburg portable throne, Versailles; on black, plinth below) ----------
img = cv2.imread(f"{SRC}/trone-habsbourg.jpg")
h, w = img.shape[:2]
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
v = hsv[..., 2].astype(np.float32) / 255
mask = np.where(v > 0.16, 255, 0).astype(np.uint8)
# find the plinth top: the first row (from the bottom half) where a wide light band starts
sat = hsv[..., 1].astype(np.float32) / 255
plain = (v > 0.35) & (sat < 0.22)               # the beige museum plinth (unsaturated), not the gold silk
rows = plain[int(h * 0.55):].mean(axis=1)
plinth = int(h * 0.55) + int(np.argmax(rows > 0.5))
mask[plinth - 6:] = 0
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
mask = fill_holes(largest_components(mask, keep=1))
mask = cv2.GaussianBlur(mask, (5, 5), 0)
save_rgba(img, mask, "trone")
print("throne plinth row", plinth, "of", h)

# ---------- the clock dial (Met DT6546, c.1757) ----------
img = cv2.imread(f"{SRC}/pendule-met-dt6546.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
white = np.where(gray > 205, 255, 0).astype(np.uint8)
white = largest_components(cv2.morphologyEx(white, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)), keep=1)
(cx, cy), r = cv2.minEnclosingCircle(cv2.findNonZero(white))
# paint out the maker's signature ("JULIEN" / "LE ROY") from the enamel; numerals and hands stay
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
ink = (gray < 140) & (hsv[..., 1] < 70)
sig = np.zeros_like(gray)
for (dx0, dy0, dx1, dy1) in [(-0.34, -0.47, 0.34, -0.22), (-0.34, 0.27, 0.34, 0.52)]:
    cv2.rectangle(sig, (int(cx + dx0 * r), int(cy + dy0 * r)), (int(cx + dx1 * r), int(cy + dy1 * r)), 255, -1)
sig = (sig > 0) & ink
sig = cv2.dilate(sig.astype(np.uint8) * 255, np.ones((5, 5), np.uint8))
img = cv2.inpaint(img, sig, 5, cv2.INPAINT_TELEA)
r *= 1.06  # include the gilt bezel
yy, xx = np.mgrid[0:img.shape[0], 0:img.shape[1]]
d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
a = np.clip((r - d) / 3.0, 0, 1)
save_rgba(img, (a * 255).astype(np.uint8), "cadran", pad=2)
print("dial", round(cx), round(cy), round(r))
