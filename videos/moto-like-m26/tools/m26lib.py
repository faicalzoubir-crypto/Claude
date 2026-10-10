"""Shared image helpers for the M26 asset scripts."""
import numpy as np
from PIL import Image, ImageFilter


def polar_inpaint(disc, occ, R, n_theta=2400):
    """Fill occluded pixels of a wheel disc from the same radius at other angles.

    A tyre and rim are close to rotation-invariant, so each ring is completed by
    circular interpolation of its visible samples. The result can spin freely
    without carrying fork, fender or shock pixels around."""
    from scipy.ndimage import map_coordinates
    arr = np.array(disc).astype(np.float32)
    size = arr.shape[0]
    c = (size - 1) / 2
    th = np.linspace(0, 2 * np.pi, n_theta, endpoint=False)
    rr = np.arange(0, R + 1, dtype=np.float32)
    TT, RR = np.meshgrid(th, rr)
    X, Y = c + RR * np.cos(TT), c + RR * np.sin(TT)
    pol = np.stack([map_coordinates(arr[..., k], [Y, X], order=1) for k in range(4)], -1)
    valid = map_coordinates((~occ).astype(np.float32), [Y, X], order=0) > 0.5
    for i in range(len(rr)):
        v = valid[i]
        if v.all() or not v.any():
            continue
        for k in range(4):
            pol[i, ~v, k] = np.interp(th[~v], th[v], pol[i, v, k], period=2 * np.pi)
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    dr = np.hypot(xx - c, yy - c)
    dt = np.mod(np.arctan2(yy - c, xx - c), 2 * np.pi) * n_theta / (2 * np.pi)
    filled = np.stack([map_coordinates(pol[..., k], [np.clip(dr, 0, R), dt], order=1, mode="grid-wrap")
                       for k in range(4)], -1)
    soft = np.array(Image.fromarray((occ * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))) / 255.0
    out = arr * (1 - soft[..., None]) + filled * soft[..., None]
    out[..., 3] = np.where(dr <= R - 1, out[..., 3], 0)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")
