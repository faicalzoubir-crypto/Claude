#!/usr/bin/env python3
"""Cleans the user's zoomed Google Earth screenshot and aligns it on the wide one.

- Removes the white sketch (circle on the sign, arrow north) the user drew to
  explain the scene: masked by colour inside the sketch's area, then inpainted.
- Finds the similarity (scale, rotation, shift) that maps zoom pixels onto wide
  pixels, so the zoom can sit exactly inside the wide view and dissolve into it.

Writes assets/images/google_earth_zoom.jpg and tools/ge_zoom_align.json.
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "images" / "source"
zoom = cv2.imread(str(SRC / "google_earth_zoom_annotated.jpg"))
wide = cv2.imread(str(SRC / "google_earth_wide.jpg"))

# 1. The sketch: near-white, unsaturated pixels inside the band it occupies.
x0, y0, x1, y1 = 320, 230, 520, 1600
hsv = cv2.cvtColor(zoom, cv2.COLOR_BGR2HSV)
white = ((hsv[..., 2] > 225) & (hsv[..., 1] < 40)).astype(np.uint8) * 255
mask = np.zeros_like(white)
mask[y0:y1, x0:x1] = white[y0:y1, x0:x1]
mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=3)
clean = cv2.inpaint(zoom, mask, 9, cv2.INPAINT_TELEA)
cv2.imwrite(str(ROOT / "assets" / "images" / "google_earth_zoom.jpg"), clean, [cv2.IMWRITE_JPEG_QUALITY, 93])
if "--mask" in sys.argv:
    cv2.imwrite(sys.argv[sys.argv.index("--mask") + 1], mask)

# 2. Alignment, ignoring the app's buttons on the right edge.
def features(img, keep):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    m = np.zeros(g.shape, np.uint8)
    m[keep[1]:keep[3], keep[0]:keep[2]] = 255
    return cv2.SIFT_create(6000).detectAndCompute(g, m)

# The zoom shows the wide view's area around the roundabout at about ×4.7.
wide_small = cv2.resize(wide, None, fx=4.0, fy=4.0, interpolation=cv2.INTER_CUBIC)
kz, dz = features(clean, (0, 0, 1000, 2400))
kw, dw = features(wide_small, (300 * 4, 900 * 4, 900 * 4, 1800 * 4))
matches = cv2.BFMatcher().knnMatch(dz, dw, k=2)
good = [m for m, n in matches if m.distance < 0.75 * n.distance]
src = np.float32([kz[m.queryIdx].pt for m in good])
dst = np.float32([kw[m.trainIdx].pt for m in good]) / 4.0
M, inl = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=3.0)
scale = float(np.hypot(M[0, 0], M[1, 0]))
angle = float(np.degrees(np.arctan2(M[1, 0], M[0, 0])))
out = {"a": M[0, 0], "b": M[1, 0], "tx": M[0, 2], "ty": M[1, 2]}
out = {k: round(float(v), 6) for k, v in out.items()}
out.update({"scale": round(scale, 5), "angle_deg": round(angle, 3), "inliers": int(inl.sum()), "matches": len(good)})
(ROOT / "tools" / "ge_zoom_align.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out))
