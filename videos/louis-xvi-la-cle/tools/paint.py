"""Bake the painterly (Kuwahara) pass into the still plates once, instead of running the multipass shader on every
frame of a CPU-only 4K render. Live grading keeps the cheap single-pass work (exposure, temperature, vignette, grain).
Usage: python3 tools/paint.py <image> [<image> …]   (in place; RGBA keeps its alpha)"""
import sys
import cv2
import numpy as np


def kuwahara(img, r):
    """Classic 4-quadrant Kuwahara on float32 BGR, radius r (px): each pixel takes the mean of its least-varied quadrant."""
    k = r + 1
    lum = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mean = cv2.blur(img, (k, k), borderType=cv2.BORDER_REFLECT)
    lmean = cv2.blur(lum, (k, k), borderType=cv2.BORDER_REFLECT)
    lvar = cv2.blur(lum * lum, (k, k), borderType=cv2.BORDER_REFLECT) - lmean * lmean
    h, w = lum.shape
    # the four quadrants' box centres are offset by ±r/2 from the pixel
    o = r // 2 + (1 if r % 2 else 0)
    shifts = [(-o, -o), (-o, o), (o, -o), (o, o)]
    best_var = np.full((h, w), np.inf, np.float32)
    out = np.zeros_like(img)
    for dy, dx in shifts:
        M = np.float32([[1, 0, -dx], [0, 1, -dy]])
        v = cv2.warpAffine(lvar, M, (w, h), borderMode=cv2.BORDER_REFLECT)
        m = cv2.warpAffine(mean, M, (w, h), borderMode=cv2.BORDER_REFLECT)
        sel = v < best_var
        best_var[sel] = v[sel]
        out[sel] = m[sel]
    return out


def paint(path, strength=0.6):
    im = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    alpha = im[..., 3] if im.ndim == 3 and im.shape[2] == 4 else None
    bgr = im[..., :3].astype(np.float32) / 255
    r = max(2, round(min(bgr.shape[:2]) / 380))      # ~3 px on a 1080-wide plate, scales with resolution
    p = kuwahara(bgr, r)
    out = bgr * (1 - strength) + p * strength
    out = (np.clip(out, 0, 1) * 255).astype(np.uint8)
    if alpha is not None:
        out = np.dstack([out, alpha])
    params = [cv2.IMWRITE_JPEG_QUALITY, 92] if path.lower().endswith(".jpg") else []
    cv2.imwrite(path, out, params)
    print("painted", path, "r", r)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        paint(p)
