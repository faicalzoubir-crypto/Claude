#!/usr/bin/env python3
"""Cuts the user's close-up of the moped-ban sign into a round badge for the map.

The photo is an enlargement (about 75 px of real detail across the sign), so it
is used small: centred on its red ring, masked to a disc just inside the ring's
outer edge, averaged down to 192 px (which also smooths the blocky enlargement).
Writes assets/images/sign_badge.png (with transparency).
"""
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
im = cv2.imread(str(ROOT / "assets/images/source/sign_closeup_user.jpg"))
hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
red = ((hsv[..., 0] < 10) | (hsv[..., 0] > 170)) & (hsv[..., 1] > 120) & (hsv[..., 2] > 120)
ys, xs = np.nonzero(red)
cx, cy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
r = (xs.max() - xs.min() + ys.max() - ys.min()) / 4 - 4  # just inside the ring's outer edge
x0, y0, side = int(cx - r), int(cy - r), int(2 * r)
crop = im[y0:y0 + side, x0:x0 + side]
yy, xx = np.mgrid[0:side, 0:side]
alpha = np.clip((r - np.hypot(xx - r, yy - r)) / 3.0, 0, 1)
rgba = np.dstack([crop, (alpha * 255).astype(np.uint8)])
out = cv2.resize(rgba, (192, 192), interpolation=cv2.INTER_AREA)
cv2.imwrite(str(ROOT / "assets/images/sign_badge.png"), out)
print("ok", round(cx), round(cy), round(r))
