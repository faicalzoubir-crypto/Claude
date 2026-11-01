#!/usr/bin/env python3
"""Cleans the user's Google Earth views of the police stop and keeps their marks.

Inputs (assets/images/source/): police_x_top.jpg (✕ where the police stop),
police_route_top.jpg (same view, the riders' route sketched), police_route_3d.jpg
(the route from a 3D angle), police_x_top2.jpg (✕ again, framed a little lower).

Writes assets/images/police_top.jpg and police_3d.jpg without the sketches, and
tools/police_geo.json: the ✕ centres, in police_top pixels, and the route's
stroke pixels (thinned) for checking the traced path against.
"""
import json
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "images" / "source"
OUT = ROOT / "assets" / "images"
x_top = cv2.imread(str(SRC / "police_x_top.jpg"))
route_top = cv2.imread(str(SRC / "police_route_top.jpg"))
r3d = cv2.imread(str(SRC / "police_route_3d.jpg"))
x_top2 = cv2.imread(str(SRC / "police_x_top2.jpg"))
k3 = np.ones((3, 3), np.uint8)


def whiteish(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    return (hsv[..., 2] > 215) & (hsv[..., 1] < 45)


def centre(mask):
    ys, xs = np.nonzero(mask)
    return [round(float(xs.mean()), 1), round(float(ys.mean()), 1)]


# 1. Top-down: the two views share one screenshot, so each sketch is where one
#    of them is much brighter than the other; the darker pixel is the road.
a, b = x_top.astype(np.int16), route_top.astype(np.int16)
lum_a, lum_b = a.mean(axis=2), b.mean(axis=2)
x_mask = cv2.dilate(((lum_a - lum_b) > 40).astype(np.uint8), k3, iterations=2)
r_mask = cv2.dilate(((lum_b - lum_a) > 40).astype(np.uint8), k3, iterations=2)
clean = np.where((x_mask[..., None] > 0), route_top, x_top)
clean = np.where((r_mask[..., None] > 0), x_top, clean)
# Where the ✕ and the route cross, both views are white: inpaint those few pixels.
both = (whiteish(x_top) & whiteish(route_top)).astype(np.uint8)
near = cv2.dilate(((x_mask > 0) | (r_mask > 0)).astype(np.uint8), k3, iterations=6)
both = cv2.dilate(both & near, k3, iterations=2)
clean = cv2.inpaint(clean, both * 255, 7, cv2.INPAINT_TELEA)
# Feathered edges of the strokes: anything still white along them gets inpainted too.
rest = cv2.dilate((whiteish(clean) & (cv2.dilate(x_mask | r_mask, k3, iterations=3) > 0)).astype(np.uint8), k3, iterations=2)
clean = cv2.inpaint(clean, rest * 255, 7, cv2.INPAINT_TELEA)
cv2.imwrite(str(OUT / "police_top.jpg"), clean, [cv2.IMWRITE_JPEG_QUALITY, 93])

x_core = (lum_a - lum_b) > 60
route_core = ((lum_b - lum_a) > 60).astype(np.uint8)
thin = cv2.ximgproc.thinning(route_core * 255) if hasattr(cv2, "ximgproc") else route_core * 255
ys, xs = np.nonzero(thin)
route_pts = sorted({(int(x) // 6 * 6, int(y) // 6 * 6) for x, y in zip(xs, ys)})

# 2. The second ✕ view: inpaint its ✕, then place it on police_top.
sk2 = np.zeros(x_top2.shape[:2], np.uint8)
sk2[900:1080, 340:480] = whiteish(x_top2)[900:1080, 340:480]
x2_centre = centre(sk2 > 0)
g1 = cv2.cvtColor(clean, cv2.COLOR_BGR2GRAY)
g2 = cv2.cvtColor(cv2.inpaint(x_top2, cv2.dilate(sk2, k3, iterations=3) * 255, 7, cv2.INPAINT_TELEA), cv2.COLOR_BGR2GRAY)
m = np.zeros(g1.shape, np.uint8); m[:, :1000] = 255
sift = cv2.SIFT_create(5000)
k1, d1 = sift.detectAndCompute(g1, m)
k2, d2 = sift.detectAndCompute(g2, m)
good = [p for p, q in cv2.BFMatcher().knnMatch(d2, d1, k=2) if p.distance < 0.75 * q.distance]
M, inl = cv2.estimateAffinePartial2D(np.float32([k2[p.queryIdx].pt for p in good]),
                                     np.float32([k1[p.trainIdx].pt for p in good]), method=cv2.RANSAC)
x2_on_top = (M @ np.array([x2_centre[0], x2_centre[1], 1.0])).round(1).tolist()

# 3. The 3D view: the sketch lies on roads, inpaint it inside the area it covers.
sk3 = np.zeros(r3d.shape[:2], np.uint8)
sk3[700:1540, 210:1030] = whiteish(r3d)[700:1540, 210:1030]
sk3 = cv2.dilate(sk3.astype(np.uint8), k3, iterations=3)
clean3d = cv2.inpaint(r3d, sk3 * 255, 9, cv2.INPAINT_TELEA)
# The app's round buttons on the right edge (layers, compass ring, compass) fall
# inside the frame once the route is centred: cover each with the imagery just to
# its left, through a soft round mask (a clone stamp, not a blur).
for cx, cy, r in ((1095, 64, 78), (1101, 637, 84), (1095, 1893, 78)):
    dx = int(2.3 * r)
    y0, y1, x0, x1 = max(cy - r, 0), min(cy + r, clean3d.shape[0]), cx - r, min(cx + r, clean3d.shape[1])
    yy, xx = np.mgrid[y0:y1, x0:x1]
    w = np.clip((r - np.hypot(xx - cx, yy - cy)) / 14.0, 0, 1)[..., None]
    patch = clean3d[y0:y1, x0 - dx:x1 - dx].astype(np.float32)
    clean3d[y0:y1, x0:x1] = (w * patch + (1 - w) * clean3d[y0:y1, x0:x1].astype(np.float32)).astype(np.uint8)
cv2.imwrite(str(OUT / "police_3d.jpg"), clean3d, [cv2.IMWRITE_JPEG_QUALITY, 93])

geo = {
    "x_top": centre(x_core),
    "x_top2_on_top": x2_on_top,
    "x_top2_align": {"inliers": int(inl.sum()), "scale": round(float(np.hypot(M[0, 0], M[1, 0])), 4)},
    "route_stroke_pts": route_pts,
}
(ROOT / "tools" / "police_geo.json").write_text(json.dumps(geo) + "\n")
print(json.dumps({k: v for k, v in geo.items() if k != "route_stroke_pts"}), len(route_pts), "route points")
