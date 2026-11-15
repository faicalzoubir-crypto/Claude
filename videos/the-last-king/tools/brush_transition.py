#!/usr/bin/env python3
"""Bake a painterly dissolve between two shots into a short 1920x1080 clip.

The outgoing shot (A) is swirled away along a curl-noise flow field while a matte of
long, bristled brushstrokes, laid along the same flow, paints the incoming shot (B) in.
Deterministic: same arguments, same frames.

  python3 tools/brush_transition.py --a assets/shots/s1b.mp4 --a-from 5.2 \
      --b assets/shots/s2a.mp4 --b-from 0.0 --dur 1.6 --mode swirl --seed 2 \
      --out assets/transitions/t1-2.mp4

Modes: swirl (scene changes: strong vortex, strokes in a spiral order),
       melt  (shot changes inside a scene: gentle flow, strokes in a drifting order).
--drain tints A into the cold blue-violet duotone before the strokes start.
"""
import argparse
import subprocess

import cv2
import numpy as np

W, H, FPS = 1920, 1080, 30
MW, MH = 960, 540  # matte resolution


def read_frames(path, t0, n):
    vf = (f"fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,"
          f"crop={W}:{H},setsar=1")
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{t0:.4f}", "-i", path,
           "-frames:v", str(n), "-vf", vf, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"]
    raw = subprocess.run(cmd, check=True, capture_output=True).stdout
    frames = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    if len(frames) == 0:
        raise SystemExit(f"no frames read from {path} at {t0}")
    if len(frames) < n:  # hold the last frame if the source runs short
        frames = np.concatenate([frames, np.repeat(frames[-1:], n - len(frames), 0)])
    return frames


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def value_noise(rng, w, h, cells_x, octaves=3):
    out = np.zeros((h, w), np.float32)
    amp, total = 1.0, 0.0
    cx = cells_x
    for _ in range(octaves):
        cy = max(2, int(round(cx * h / w)))
        grid = rng.random((cy + 1, cx + 1)).astype(np.float32)
        out += amp * cv2.resize(grid, (w, h), interpolation=cv2.INTER_CUBIC)
        total += amp
        amp *= 0.5
        cx *= 2
    out /= total
    out -= out.min()
    out /= max(out.max(), 1e-6)
    return out


def flow_field(rng, w, h, mode):
    """Divergence-free flow (curl of a stream function), unit max magnitude."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    nx, ny = (xx - w / 2) / (h / 2), (yy - h / 2) / (h / 2)
    r2 = nx * nx + ny * ny
    noise = value_noise(rng, w, h, 3 if mode == "swirl" else 4)
    if mode == "swirl":
        cxo, cyo = rng.uniform(-0.25, 0.25), rng.uniform(-0.15, 0.15)
        rv2 = (nx - cxo) ** 2 + (ny - cyo) ** 2
        psi = 1.6 * np.exp(-rv2 / 1.3) + 0.9 * noise
    else:
        psi = 1.2 * noise + 0.15 * ny
    psi = cv2.GaussianBlur(psi.astype(np.float32), (0, 0), w / 60)
    gy, gx = np.gradient(psi)
    vx, vy = gy, -gx
    mag = np.sqrt(vx * vx + vy * vy).max()
    return (vx / mag).astype(np.float32), (vy / mag).astype(np.float32), r2


def make_strokes(rng, vx, vy, mode):
    """Streamline strokes in matte space: (points, width, start, length, bristles)."""
    strokes = []
    gx, gy = (18, 10) if mode == "swirl" else (22, 12)
    extra = 60 if mode == "swirl" else 90
    seeds = []
    for j in range(gy):
        for i in range(gx):
            seeds.append(((i + rng.random()) * MW / gx, (j + rng.random()) * MH / gy))
    for _ in range(extra):
        seeds.append((rng.random() * MW, rng.random() * MH))
    rng.shuffle(seeds)
    for sx, sy in seeds:
        length = rng.uniform(120, 360) if mode == "swirl" else rng.uniform(80, 220)
        width = rng.uniform(16, 40) if mode == "swirl" else rng.uniform(10, 26)
        step, x, y = 4.0, sx, sy
        sign = 1.0 if rng.random() < 0.85 else -1.0
        pts = [(x, y)]
        for _ in range(int(length / step)):
            ix, iy = int(np.clip(x, 0, MW - 1)), int(np.clip(y, 0, MH - 1))
            dx, dy = vx[iy, ix], vy[iy, ix]
            n = np.hypot(dx, dy) + 1e-6
            x += sign * step * dx / n
            y += sign * step * dy / n
            pts.append((x, y))
        pts = np.array(pts, np.float32)
        # order: a spiral sweep for swirl, a drifting diagonal for melt
        cx, cy = MW / 2, MH / 2
        if mode == "swirl":
            ang = (np.arctan2(sy - cy, sx - cx) / (2 * np.pi)) % 1.0
            rad = np.hypot(sx - cx, sy - cy) / np.hypot(cx, cy)
            key = (ang + 0.55 * rad) % 1.0
            start = 0.06 + 0.58 * key + rng.uniform(-0.04, 0.04)
            dur = rng.uniform(0.16, 0.28)
        else:
            key = 0.6 * sx / MW + 0.4 * sy / MH
            start = 0.04 + 0.55 * key + rng.uniform(-0.08, 0.08)
            dur = rng.uniform(0.18, 0.3)
        nb = 7
        bristles = []
        for b in range(nb):
            off = (b - (nb - 1) / 2) / (nb - 1) * width * 0.9
            bristles.append((off, rng.uniform(0.55, 1.0), rng.uniform(0.8, 1.0),
                             max(1, int(round(width / nb * rng.uniform(1.3, 2.0))))))
        strokes.append((pts, width, max(0.02, start), dur, bristles))
    return strokes


def draw_strokes(strokes, p, prev):
    canvas = np.zeros((MH, MW), np.uint8)
    for pts, width, start, dur, bristles in strokes:
        g = (p - start) / dur
        if g <= 0:
            continue
        g = min(1.0, g)
        g = 1 - (1 - g) ** 2  # the brush decelerates at the end of its pull
        if len(pts) < 2:
            continue
        d = np.diff(pts, axis=0)
        nrm = np.stack([-d[:, 1], d[:, 0]], 1)
        nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-6
        nrm = np.vstack([nrm, nrm[-1:]])
        for off, alpha, lfrac, thick in bristles:
            k = max(2, int(len(pts) * g * lfrac))
            line = pts[:k] + nrm[:k] * off
            cv2.polylines(canvas, [np.round(line * 4).astype(np.int32)], False,
                          int(alpha * 255), thick, cv2.LINE_AA, shift=2)
    m = canvas.astype(np.float32) / 255.0
    return np.maximum(prev, m) if prev is not None else m


DUO = np.array([[16, 13, 11], [92, 45, 43], [168, 95, 91], [214, 190, 196]], np.float32)  # BGR


def drain(img, amt):
    if amt <= 0:
        return img
    lum = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    pos = np.clip(lum, 0, 1) * (len(DUO) - 1)
    i0 = np.floor(pos).astype(np.int32).clip(0, len(DUO) - 2)
    f = (pos - i0)[..., None]
    duo = DUO[i0] * (1 - f) + DUO[i0 + 1] * f
    return (img.astype(np.float32) * (1 - amt) + duo * amt).clip(0, 255).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--a-from", type=float, required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--b-from", type=float, required=True)
    ap.add_argument("--dur", type=float, default=1.6)
    ap.add_argument("--mode", choices=["swirl", "melt"], default="swirl")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--drain", action="store_true")
    ap.add_argument("--out", required=True)
    ap.add_argument("--debug-matte")
    args = ap.parse_args()

    n = int(round(args.dur * FPS))
    A = read_frames(args.a, args.a_from, n)
    B = read_frames(args.b, args.b_from, n)
    rng = np.random.default_rng(args.seed)

    vx, vy, _ = flow_field(rng, MW, MH, args.mode)
    strokes = make_strokes(rng, vx, vy, args.mode)
    fill_noise = value_noise(rng, MW, MH, 5)
    # full-res displacement field
    fvx = cv2.resize(vx, (W, H), interpolation=cv2.INTER_LINEAR)
    fvy = cv2.resize(vy, (W, H), interpolation=cv2.INTER_LINEAR)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    amp = 150.0 if args.mode == "swirl" else 45.0
    cream = np.array([166, 217, 233], np.float32)  # BGR of #E9D9A6

    enc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow",
         "-crf", "14", "-pix_fmt", "yuv420p", "-movflags", "+faststart", args.out],
        stdin=subprocess.PIPE)

    prev = None
    for i in range(n):
        p = i / (n - 1)
        if args.drain:
            dr = smoothstep(0.0, 0.5, p)
            sp = np.clip((p - 0.35) / 0.65, 0, 1)  # strokes run in the last 65%
        else:
            dr, sp = 0.0, p
        e = smoothstep(0.0, 1.0, sp)
        prev = draw_strokes(strokes, sp, prev)
        q = np.clip((sp - 0.55) / 0.45, 0, 1)
        fill = smoothstep(fill_noise - 0.15, fill_noise + 0.15, q * 1.3 - 0.15)
        m = np.maximum(prev, fill)
        if i == 0 and not args.drain:
            m = np.zeros_like(m)
        if i == n - 1:
            m = np.ones_like(m)
        m = cv2.GaussianBlur(m, (0, 0), 0.9)
        M = cv2.resize(m, (W, H), interpolation=cv2.INTER_CUBIC).clip(0, 1)[..., None]

        a = drain(A[i], dr)
        ka, kb = float(amp * e), float(amp * (1 - e) * 0.7)
        wa = cv2.remap(a, xx + fvx * ka, yy + fvy * ka, cv2.INTER_LINEAR,
                       borderMode=cv2.BORDER_REFLECT)
        wb = cv2.remap(B[i], xx - fvx * kb, yy - fvy * kb, cv2.INTER_LINEAR,
                       borderMode=cv2.BORDER_REFLECT)
        out = wa.astype(np.float32) * (1 - M) + wb.astype(np.float32) * M
        edge = (M * (1 - M) * 4.0) ** 2  # wet paint edge, a faint cream lift
        out = out * (1 - 0.10 * edge) + cream * 0.10 * edge
        enc.stdin.write(out.clip(0, 255).astype(np.uint8).tobytes())
        if args.debug_matte and i in (n // 4, n // 2, 3 * n // 4):
            cv2.imwrite(f"{args.debug_matte}-{i:02d}.png", (M[..., 0] * 255).astype(np.uint8))
    enc.stdin.close()
    enc.wait()
    print(f"wrote {args.out} ({n} frames, {args.mode}{', drain' if args.drain else ''})")


if __name__ == "__main__":
    main()
