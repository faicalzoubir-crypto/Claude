"""The fifteen shots, each a function of shot-local time t (s) and shot length d.

Each returns (underpainting, camera). Coordinates are normalised: u across (0..1), v down (0..1).
The action stays between v 0.09 and 0.69 (the band a vertical-video app leaves clear).
"""
import math

import cv2
import numpy as np

from painter import (PAL, U, V, W, H, Batch, blob, crown3d, ease, ellipse_mask, fbm, king_back,
                     lay, line_mask, poly_mask, rot, soft_radial, vgrad)

ASP = H / W


def black():
    return np.zeros((H, W, 3), np.float32)


def rng_for(seed):
    return np.random.default_rng(seed)


# ------------------------------------------------------------------ 1a: the balcony
_CROWD = None


def _crowd():
    global _CROWD
    if _CROWD is None:
        r = rng_for(1001)
        figs = []
        rows = 17
        for i in range(rows):
            f = i / (rows - 1)
            v = 0.2 + 0.45 * f ** 1.3
            size = 0.005 + 0.014 * f ** 1.3
            n = int(0.9 / (size * 2.3 * ASP))
            for k in range(n):
                u = 0.05 + 0.9 * (k + r.uniform(-0.3, 0.3)) / max(1, n - 1)
                figs.append((u, v + r.uniform(-0.25, 0.25) * size, size, r.uniform(0.55, 1.0), r.uniform(0, 6.28)))
        _CROWD = figs
    return _CROWD


def s1a(t, d):
    img = black()
    pool = blob(0.5, 0.45, 0.66, 0.36, 101, t, wobble=0.22, blur=26)
    ground = vgrad(PAL["umber"] * 0.7, PAL["cream2"] * 0.95, 0.15, 0.66)
    img = lay(img, pool, ground)
    # sky above the horizon: dark umber with a faint warm haze on the line
    img = lay(img, np.clip((0.22 - V) / 0.08, 0, 1) * 0.85, PAL["black"])
    raise_t = ease((t - 0.9) / 1.6)
    arm = 0.15 + 2.35 * raise_t
    hand_u, hand_v = 0.5, 0.62
    wave_r = max(0.0, (t - 2.1)) * 0.22
    b = Batch()
    for u, v, size, lum, ph in _crowd():
        dist = math.hypot((u - hand_u) / 1.0, (v - hand_v) * 1.6)
        w = math.exp(-((dist - wave_r) / 0.05) ** 2) if t > 2.1 else 0.0
        lift = w * size * 1.6
        shimmer = 0.06 * math.sin(2.1 * t + ph)
        bright = np.clip(lum * (0.75 + 0.45 * w) + shimmer, 0, 1)
        b.ellipse(u, v - lift * 0.5, size * 1.15 * ASP, size * (0.62 + 0.55 * w), bright)
        b.ellipse(u + 0.25 * size * ASP, v - size * (0.55 + 1.0 * w) - lift * 0.5, size * 0.42 * ASP,
                  size * 0.42, min(1, bright * 1.1))
    m, val = b.get(0.7)
    crowd_col = PAL["umber"] * (1 - val[..., None]) + PAL["cream"] * 0.95 * val[..., None]
    far = np.clip((V - 0.18) / 0.3, 0.25, 1)[..., None]  # far rows sink into the dark
    crowd_col = crowd_col * far
    img = lay(img, m * pool, crowd_col)
    # gilded balustrade
    rail = poly_mask([(0.0, 0.665), (1.0, 0.665), (1.0, 0.69), (0.0, 0.69)], 1.0)
    img = lay(img, soft_radial(0.5, 0.66, 0.22, 0.12, 1.2) * 0.55, PAL["umber"] * 0.5)  # shade behind him
    railc = PAL["gold"] * 0.55 + PAL["cream2"] * 0.3
    img = lay(img, rail, railc * vgrad(np.ones(3) * 1.15, np.ones(3) * 0.55, 0.665, 0.69))
    bb = Batch()
    for k in range(13):
        u = 0.04 + k * 0.077
        bb.poly([(u - 0.012, 0.69), (u + 0.012, 0.69), (u + 0.018, 0.74), (u + 0.01, 0.8), (u + 0.014, 0.86),
                 (u - 0.014, 0.86), (u - 0.01, 0.8), (u - 0.018, 0.74)], 0.5 + 0.5 * ((k * 37) % 7) / 7)
    bm, bv = bb.get(1.0)
    img = lay(img, bm, (PAL["golddk"] * 0.7 + PAL["umber2"] * 0.3) * (0.55 + 0.5 * bv[..., None]))
    img = lay(img, np.clip((V - 0.86) / 0.06, 0, 1), PAL["umber"] * 0.5)
    # the king, from behind, raising his right hand over the crowd
    img = king_back(img, 0.5, 0.95, 0.42, t, arm=arm)
    cam = (1.0 + 0.05 * t / d, 0.0, -0.012 * t / d)
    return img, cam


# ------------------------------------------------------------------ shared bits

def pool_of(img, mask, base):
    return lay(img, mask, base)


def stones(seed, u0, u1, v0, v1, rows, cols, lum=(0.35, 0.62)):
    """a wall of rough stone blocks: coverage + value maps."""
    r = rng_for(seed)
    b = Batch()
    rh = (v1 - v0) / rows
    for i in range(rows):
        cw = (u1 - u0) / cols
        off = (i % 2) * cw * 0.5
        for j in range(-1, cols + 1):
            a = u0 + j * cw + off + r.uniform(-0.01, 0.01)
            c = a + cw - 0.008
            top = v0 + i * rh + 0.004
            bot = top + rh - 0.008
            jit = lambda: r.uniform(-0.004, 0.004)
            b.poly([(a + jit(), top + jit()), (c + jit(), top + jit()), (c + jit(), bot + jit()), (a + jit(), bot + jit())],
                   r.uniform(*lum))
    return b.get(1.2)


def king_front(img, cu, v_feet, height, alpha=1.0, crack=0.0, cloak=None):
    """the king facing us (in the mirror): faceless pale head, crown with its red gem."""
    img = king_back(img, cu, v_feet, height, crown=False, alpha=alpha, cloak=cloak, head_col=PAL["cream2"] * 0.9)
    head_r = height * 0.062
    sh_v = v_feet - height * 0.80
    hd_v = sh_v - head_r * 1.25
    return crown3d(img, cu, hd_v - head_r * 0.85, head_r * 1.05, -0.25, 0.0, 0.0, alpha=alpha, crack=crack)


# ------------------------------------------------------------------ 1b: the cell

def s1b(t, d):
    img = black()
    cold = blob(0.5, 0.42, 0.55, 0.42, 202, t, wobble=0.2, blur=30)
    m, val = stones(2020, -0.05, 1.05, 0.02, 0.74, 16, 4)
    wall = PAL["night"] * 0.6 + (PAL["bluegrey"] * 0.9 - PAL["night"] * 0.6) * val[..., None]
    img = lay(img, m * cold, wall)
    img = lay(img, np.clip((V - 0.72) / 0.03, 0, 1) * cold, PAL["night"] * 0.75)  # floor
    # the high slit window and the cold light that falls from it
    img = lay(img, soft_radial(0.5, 0.2, 0.25, 0.25, 1.4) * 0.6, PAL["peri"] * 0.9)
    img = lay(img, poly_mask([(0.488, 0.1), (0.512, 0.1), (0.512, 0.28), (0.488, 0.28)], 1.2), PAL["snow"])
    img = lay(img, poly_mask([(0.49, 0.28), (0.51, 0.28), (0.62, 0.72), (0.38, 0.72)], 14) * 0.18, PAL["peri"])
    # the bench and the seated king
    img = lay(img, poly_mask([(0.33, 0.6), (0.67, 0.6), (0.67, 0.64), (0.33, 0.64)], 1.5), PAL["night"] * 1.4)
    drop = 0.035 * ease((t - 1.8) / 3.5)
    img = king_back(img, 0.5, 0.63, 0.36, t, seated=True, head_drop=drop,
                    cloak=PAL["bone"] * 0.55 + PAL["peri"] * 0.3, head_col=PAL["umber"])
    # one candle on the floor
    fl = 1 + 0.18 * math.sin(17 * t) + 0.1 * math.sin(29 * t + 1.3) + 0.06 * math.sin(41 * t + 0.4)
    warm = soft_radial(0.5, 0.74, 0.3 * (0.95 + 0.05 * fl), 0.1, 1.3)
    img = img + warm[..., None] * PAL["cream"] * 0.45
    img = lay(img, poly_mask([(0.494, 0.705), (0.506, 0.705), (0.506, 0.745), (0.494, 0.745)], 0.8), PAL["ivory"])
    img = lay(img, ellipse_mask(0.5 + 0.002 * math.sin(11 * t), 0.69, 0.006 * ASP, 0.013 * fl, 0, 1.2), PAL["light"] * 1.2)
    img = lay(img, ellipse_mask(0.5, 0.695, 0.0025 * ASP, 0.005, 0, 0.8), PAL["redhot"] * 1.1)
    cam = (1.02 + 0.06 * t / d, 0.0, 0.01 * t / d)
    return img, cam


# ------------------------------------------------------------------ 2a: the crowd lifts a crown
_ARMS = None


def s2a(t, d):
    global _ARMS
    if _ARMS is None:
        r = rng_for(303)
        _ARMS = [(0.04 + 0.92 * (k + r.uniform(-0.3, 0.3)) / 25, r.uniform(0.76, 0.86), r.uniform(0.4, 0.6),
                  r.uniform(-0.3, 0.3), r.uniform(0, 6.28), r.uniform(0.55, 1.0)) for k in range(26)]
    img = black()
    pool = blob(0.5, 0.45, 0.6, 0.4, 304, t, wobble=0.25, blur=30)
    img = lay(img, pool, vgrad(PAL["cream"] * 0.75, PAL["umber"] * 0.7, 0.1, 0.8))
    img = lay(img, soft_radial(0.5, 0.3, 0.42, 0.24, 1.5) * 0.7, PAL["light"])
    rise = ease(t / 2.4)
    b = Batch()
    for u, vb, vt, lean, ph, lum in _ARMS:
        top = vt + (1 - rise) * 0.12 + 0.01 * math.sin(1.7 * t + ph)
        sway = lean * 0.12 + 0.025 * math.sin(1.3 * t + ph)
        tu = u + sway
        elbow = (u + (tu - u) * 0.5 + 0.025 * math.sin(ph) , vb + (top - vb) * 0.55)
        b.line([(u, vb), elbow], 22 + 8 * lum, lum * 0.8)
        b.line([elbow, (tu, top)], 16 + 6 * lum, lum)
        b.ellipse(tu, top - 0.012, 0.016 * ASP, 0.02, min(1, lum * 1.15), angle=lean * 40)
    m, val = b.get(1.4)
    arms = PAL["umber2"] * (1 - val[..., None]) + PAL["light"] * val[..., None]
    arms = arms * np.clip(1.2 - (V - 0.4) / 0.5, 0.25, 1.1)[..., None]
    img = lay(img, m, arms)
    hb = Batch()  # heads at the bottom, in shadow
    r = rng_for(305)
    for k in range(22):
        hb.ellipse(r.uniform(0, 1), r.uniform(0.82, 0.95), 0.03 * ASP, 0.035, 0.2)
    hm, _ = hb.get(3)
    img = lay(img, hm, PAL["umber"] * 0.45)
    cv_ = 0.31 - 0.07 * ease(t / d)
    img = crown3d(img, 0.5, cv_, 0.07, -0.42, 0.35 * t, 0.0)
    cam = (1.04, 0.0, -0.025 * ease(t / d))
    return img, cam


# ------------------------------------------------------------------ 2b: the dice
PIPS = {1: [(0, 0)], 2: [(-0.5, -0.5), (0.5, 0.5)], 3: [(-0.5, -0.5), (0, 0), (0.5, 0.5)],
        4: [(-0.5, -0.5), (0.5, -0.5), (-0.5, 0.5), (0.5, 0.5)],
        5: [(-0.5, -0.5), (0.5, -0.5), (0, 0), (-0.5, 0.5), (0.5, 0.5)],
        6: [(-0.5, -0.5), (0.5, -0.5), (-0.5, 0), (0.5, 0), (-0.5, 0.5), (0.5, 0.5)]}
FACES = [((0, 0, -1), (1, 0, 0), (0, 1, 0), 1), ((0, 0, 1), (-1, 0, 0), (0, 1, 0), 6),
         ((1, 0, 0), (0, 0, 1), (0, 1, 0), 3), ((-1, 0, 0), (0, 0, -1), (0, 1, 0), 4),
         ((0, -1, 0), (1, 0, 0), (0, 0, 1), 2), ((0, 1, 0), (1, 0, 0), (0, 0, -1), 5)]


def rotm(ax, ay, az):
    cx, sx, cy, sy, cz, sz = math.cos(ax), math.sin(ax), math.cos(ay), math.sin(ay), math.cos(az), math.sin(az)
    return (np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]) @ np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
            @ np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]]))


def die(img, cu, cv_, size, R, alpha=1.0):
    light = np.array([-0.4, -0.7, -0.6])
    light /= np.linalg.norm(light)
    faces = []
    for n, a, b, k in FACES:
        n, a, b = R @ np.array(n, float), R @ np.array(a, float), R @ np.array(b, float)
        if n[2] >= 0:
            continue
        faces.append((n, a, b, k))
    to = lambda p: (cu + p[0] * size * ASP, cv_ + p[1] * size)
    for n, a, b, k in faces:
        c = n
        corners = [to(c + a * sa + b * sb) for sa, sb in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        lam = max(0.0, float(-np.dot(n, light)))
        img = lay(img, poly_mask(corners, 0.8) * alpha, PAL["ivory"] * (0.55 + 0.7 * lam))
        pb = Batch()
        for pu, pv in PIPS[k]:
            p = to(c + a * pu * 1.05 + b * pv * 1.05)
            pb.ellipse(p[0], p[1], 0.16 * size * ASP * max(0.3, -n[2]), 0.16 * size * max(0.3, -n[2]), 1.0)
        pm, _ = pb.get(0.8)
        img = lay(img, pm * alpha, PAL["umber"] * 0.6)
    return img


_RIBBONS = None


def s2b(t, d):
    global _RIBBONS
    t_break = 2.6
    img = black()
    pool = blob(0.5, 0.42, 0.42, 0.3, 404, t, blur=30)
    img = lay(img, pool, PAL["umber"] * 1.3 + PAL["bluegrey"] * 0.25)
    img = lay(img, soft_radial(0.48, 0.38, 0.35, 0.22, 1.4) * 0.45, PAL["cream2"])
    dice = [(0.4, 0.34, 0.085, (0.6, 0.3, 0.2), (0.55, 0.8, 0.3)), (0.62, 0.48, 0.078, (1.9, 0.9, 0.5), (-0.7, 0.6, 0.45))]
    fade = 1 - ease((t - t_break) / 1.8)
    centers = []
    for cu, cv_, size, a0, w in dice:
        cvv = cv_ + 0.02 * t
        R = rotm(a0[0] + w[0] * t * 0.55, a0[1] + w[1] * t * 0.55, a0[2] + w[2] * t * 0.55)
        centers.append((cu, cvv, size))
        if fade > 0.01:
            img = die(img, cu, cvv, size, R, fade)
    if _RIBBONS is None:
        r = rng_for(405)
        rib = []
        for k in range(70):
            cu, cv_, size = centers[k % 2][0], 0.34 + 0.02 * t_break if k % 2 == 0 else 0.48 + 0.02 * t_break, 0.08
            p = np.array([cu + r.uniform(-1, 1) * size * ASP * 0.9, cv_ + r.uniform(-1, 1) * size * 0.9])
            ang0 = math.atan2(p[1] - cv_, (p[0] - cu) / ASP)
            path = [p.copy()]
            for s in range(160):
                ang = ang0 + 0.9 * math.sin(s * 0.03 + k) + s * 0.012
                p = p + np.array([math.cos(ang) * 0.0028 * ASP * 0.6, math.sin(ang) * 0.0028 - 0.0009])
                path.append(p.copy())
            rib.append((np.array(path), r.uniform(0.0, 0.8), r.uniform(4, 10), r.uniform(0.5, 1.0)))
        _RIBBONS = rib
    if t > t_break:
        b = Batch()
        age = t - t_break
        for path, delay, wpx, lum in _RIBBONS:
            a = age - delay
            if a <= 0:
                continue
            head = min(len(path) - 1, int(a * 55))
            tail = max(0, head - 45)
            pts = [tuple(p) for p in path[tail:head + 1]]
            if len(pts) > 1:
                b.line(pts, wpx * (1 - 0.4 * min(1, a / 3)), lum * (1 - 0.6 * ease((a - 2.2) / 1.2)))
        m, val = b.get(1.2)
        gold = PAL["golddk"] * (1 - val[..., None]) + (PAL["gold"] * 0.6 + PAL["cream"] * 0.5) * val[..., None]
        img = lay(img, m * np.clip(val * 1.6, 0, 1), gold)
    cam = (1.03 + 0.03 * t / d, 0.0, 0.0)
    return img, cam


# ------------------------------------------------------------------ 3a: the palace on salt and sand
_GRAINS = None


def palace_layer(t):
    img = black()
    m = np.zeros((H, W), np.float32)

    def add(mask, col):
        nonlocal img, m
        img = lay(img, mask, col)
        m = np.maximum(m, mask)

    shade = np.clip(0.75 + 0.6 * (0.5 - U), 0.5, 1.15)[..., None]
    add(poly_mask([(0.24, 0.27), (0.76, 0.27), (0.76, 0.38), (0.24, 0.38)], 1.0), PAL["gold"] * 0.85 * shade)
    add(ellipse_mask(0.5, 0.27, 0.13 * ASP * 0.55, 0.075, 0, 1.0) * (V < 0.27), PAL["gold"] * 1.05 * shade)
    for tu in (0.29, 0.71):
        add(poly_mask([(tu - 0.035, 0.2), (tu + 0.035, 0.2), (tu + 0.035, 0.38), (tu - 0.035, 0.38)], 1.0),
            PAL["cream"] * 0.95 * shade)
        add(ellipse_mask(tu, 0.2, 0.035, 0.03, 0, 1.0) * (V < 0.2), PAL["gold"] * shade)
    add(line_mask([(0.5, 0.195), (0.5, 0.16)], 3, 0.8), PAL["gold"])
    wb = Batch()
    for k in range(7):
        u = 0.32 + k * 0.06
        wb.poly([(u - 0.012, 0.3), (u + 0.012, 0.3), (u + 0.012, 0.35), (u - 0.012, 0.35)], 1)
    wm, _ = wb.get(1.0)
    img = lay(img, wm, PAL["umber"] * 0.8)
    return img, m


def s3a(t, d):
    global _GRAINS
    img = black()
    sky = blob(0.5, 0.36, 0.62, 0.4, 505, t, blur=30)
    img = lay(img, sky, vgrad(PAL["night"] * 0.8, PAL["peri"] * 0.55, 0.05, 0.6))
    img = lay(img, soft_radial(0.5, 0.29, 0.45, 0.2, 1.3) * 0.55, PAL["cream"] * 0.8)
    crumble = ease((t - 0.4) / (d - 0.6))
    sag = ease((t - 2.0) / 2.8)
    # pillars, eaten away from below and in patches
    grain = fbm(5050, 18, 3)
    pb = Batch()
    xs = [0.31, 0.405, 0.5, 0.595, 0.69]
    for k, x in enumerate(xs):
        w = 0.018 if k % 2 else 0.022
        pb.poly([(x - w, 0.38), (x + w, 0.38), (x + w * 1.15, 0.97), (x - w * 1.15, 0.97)], 0.55 if k % 2 else 0.95)
    pm, pv = pb.get(1.0)
    erode = fbm(5051, 9, 3)
    keep = np.clip((erode + 0.25 * (1 - (V - 0.38) / 0.6) - crumble * 0.85 + 0.1) / 0.08, 0, 1)
    pm = pm * keep
    salt = PAL["snow"] * 0.95
    sand = PAL["cream2"] * 0.95
    col = sand * (1 - pv[..., None]) + salt * pv[..., None]
    col = col * (0.75 + 0.45 * grain[..., None])
    img = lay(img, pm * blob(0.5, 0.6, 0.5, 0.5, 506, 0, blur=10, wobble=0.1), col)
    # grains pouring down
    if _GRAINS is None:
        r = rng_for(507)
        _GRAINS = [(xs[r.integers(0, 5)] + r.uniform(-0.024, 0.024), r.uniform(0.4, 0.9), r.uniform(0.2, d),
                    r.uniform(0.5, 1.0)) for _ in range(900)]
    gb = Batch()
    for x, v0, ts, lum in _GRAINS:
        if t < ts or crumble * 1.4 < (ts / d):
            continue
        a = t - ts
        v = v0 + 0.5 * 0.6 * a * a
        if v > 1.0:
            continue
        gb.ellipse(x + 0.004 * math.sin(ts * 9), v, 0.0016 * ASP, 0.0045, lum)
    gm, gv = gb.get(0.6)
    img = lay(img, gm, PAL["snow"] * 0.6 + PAL["cream"] * 0.4 * gv[..., None])
    # the palace, sagging as its pillars go
    pal, pm2 = palace_layer(t)
    ang = -1.8 * sag
    M = cv2.getRotationMatrix2D((0.5 * W, 0.38 * H), ang, 1.0)
    M[1, 2] += 0.03 * sag * H
    pal = cv2.warpAffine(pal, M, (W, H))
    pm2 = cv2.warpAffine(pm2, M, (W, H))
    img = lay(img, pm2, pal)
    cam = (1.0 + 0.06 * t / d, 0.0, -0.01 * t / d)
    return img, cam


# ------------------------------------------------------------------ 3b: the carriage in the night

def s3b(t, d):
    img = black()
    lean = ease(t / d)
    vp = (0.5, 0.3)
    img = lay(img, blob(0.5, 0.42, 0.6, 0.45, 606, t, blur=30), vgrad(PAL["peri"] * 0.75, PAL["night"] * 0.9, 0.05, 0.5))
    img = lay(img, soft_radial(0.5, 0.13, 0.25, 0.1, 1.2) * 0.8, PAL["snow"] * 0.9)  # moon haze
    img = lay(img, ellipse_mask(0.53, 0.11, 0.03 * ASP, 0.03, 0, 2.0), PAL["ivory"] * 0.95)
    road = poly_mask([(0.47, vp[1]), (0.53, vp[1]), (0.95, 1.0), (0.05, 1.0)], 3)
    img = lay(img, road * 0.9, vgrad(PAL["peri"] * 0.45, PAL["night"] * 0.8, 0.3, 1.0))
    img = lay(img, poly_mask([(0.497, vp[1]), (0.503, vp[1]), (0.56, 1.0), (0.44, 1.0)], 6) * 0.35, PAL["snow"] * 0.7)
    # walls that lean in
    li = 0.43 + 0.05 * lean
    ri = 0.57 - 0.05 * lean
    wl = [(-0.05, 0.0), (li - 0.12, 0.0), (li, 0.26), (li - 0.02, 0.32), (0.06 + 0.04 * lean, 1.0), (-0.05, 1.0)]
    wr = [(1.05, 0.0), (ri + 0.12, 0.0), (ri, 0.26), (ri + 0.02, 0.32), (0.94 - 0.04 * lean, 1.0), (1.05, 1.0)]
    for poly, side in ((wl, -1), (wr, 1)):
        m = poly_mask(poly, 4)
        img = lay(img, m, PAL["night"] * 0.55 + PAL["umber"] * 0.4)
    img = lay(img, line_mask([(li, 0.26), (0.06 + 0.04 * lean, 1.0)], 4, 3) * 0.5, PAL["peri"] * 0.7)
    img = lay(img, line_mask([(ri, 0.26), (0.94 - 0.04 * lean, 1.0)], 4, 3) * 0.5, PAL["peri"] * 0.7)
    # the carriage, from behind, racing away up the road
    f = ease(t / d) * 0.85 + 0.15 * t / d
    s = 1.0 - 0.6 * f
    cv_ = 0.76 - 0.3 * f + 0.004 * math.sin(t * 19)
    cu = 0.5 + 0.01 * math.sin(t * 2.3)
    bw, bh = 0.12 * s * ASP * 0.5, 0.11 * s
    car = Batch()
    car.poly([(cu - bw, cv_ - bh), (cu + bw, cv_ - bh), (cu + bw * 1.05, cv_), (cu - bw * 1.05, cv_)], 0.2)
    car.poly([(cu - bw * 1.15, cv_ - bh * 1.12), (cu + bw * 1.15, cv_ - bh * 1.12), (cu + bw, cv_ - bh), (cu - bw, cv_ - bh)], 0.3)
    for sx in (-1, 1):
        car.ellipse(cu + sx * bw * 0.95, cv_ + bh * 0.12, bw * 0.12, bh * 0.38, 0.1)
    for hx in (-0.35, 0.35):  # horses ahead, smaller
        car.ellipse(cu + hx * bw, cv_ - bh * 1.35, bw * 0.28, bh * 0.22, 0.15)
        car.ellipse(cu + hx * bw * 1.1, cv_ - bh * 1.7, bw * 0.12, bh * 0.15, 0.15)
    cm, cvv = car.get(1.0)
    img = lay(img, cm, PAL["black"] + PAL["umber"] * cvv[..., None] * 1.5)
    for sx in (-1, 1):
        lx, ly = cu + sx * bw * 0.85, cv_ - bh * 0.75
        img = img + soft_radial(lx, ly, 0.05 * s, 0.03 * s, 2.0)[..., None] * PAL["cream"] * 0.5
        img = lay(img, ellipse_mask(lx, ly, 0.008 * s * ASP, 0.008 * s, 0, 0.8), PAL["light"] * 1.2)
    cam = (1.04 + 0.03 * t / d, 0.0, -0.02 * t / d)
    return img, cam


# ------------------------------------------------------------------ 3c: the key dissolves in his hand
_FLAKES = None


def s3c(t, d):
    global _FLAKES
    img = black()
    img = lay(img, blob(0.5, 0.46, 0.5, 0.3, 707, t, blur=30), PAL["night"] * 0.7 + PAL["bluegrey"] * 0.25)
    img = lay(img, soft_radial(0.52, 0.44, 0.4, 0.2, 1.4) * 0.5, PAL["bluegrey"] * 1.2)
    cloak = PAL["bone"] * 0.8
    img = lay(img, poly_mask([(-0.1, 0.62), (0.05, 0.53), (0.3, 0.47), (0.36, 0.5), (0.34, 0.58), (0.1, 0.7), (-0.1, 0.78)], 2.0), cloak)
    img = lay(img, line_mask([(0.0, 0.66), (0.3, 0.52)], 4, 3) * 0.4, cloak * 0.6)
    skin = PAL["cream2"] * 0.75 + PAL["bone"] * 0.35
    img = lay(img, ellipse_mask(0.47, 0.5, 0.16 * ASP * 0.55, 0.05, -8, 1.5), skin)
    for k, (fu, fv, ln) in enumerate([(0.6, 0.47, 0.07), (0.62, 0.495, 0.075), (0.61, 0.52, 0.07), (0.58, 0.54, 0.055)]):
        img = lay(img, ellipse_mask(fu, fv, ln * ASP * 0.5, 0.011, -6 - k * 4, 1.2), skin * (0.92 + 0.03 * k))
    img = lay(img, ellipse_mask(0.44, 0.46, 0.05 * ASP * 0.5, 0.012, -40, 1.2), skin * 0.9)  # thumb
    img = lay(img, ellipse_mask(0.5, 0.515, 0.12 * ASP * 0.5, 0.02, -8, 4) * 0.4, skin * 0.6)  # palm shadow
    # the key, eaten from its bit toward its bow
    key = black()
    km = np.zeros((H, W), np.float32)
    ring = np.clip(ellipse_mask(0.41, 0.475, 0.022 * ASP, 0.022, 0, 0.8) - ellipse_mask(0.41, 0.475, 0.011 * ASP, 0.011, 0, 0.8), 0, 1)
    shaft = line_mask([(0.43, 0.476), (0.61, 0.472)], 7, 0.8)
    bit = poly_mask([(0.585, 0.472), (0.61, 0.472), (0.61, 0.497), (0.6, 0.497), (0.6, 0.488), (0.592, 0.488), (0.592, 0.497), (0.585, 0.497)], 0.7)
    km = np.clip(ring + shaft + bit, 0, 1)
    gold = PAL["gold"] * np.clip(0.8 + 0.5 * (0.47 - V) / 0.03, 0.6, 1.3)[..., None]
    front = 0.64 - 0.3 * ease((t - 0.8) / 3.2)
    edge = fbm(7070, 30, 2) * 0.03
    keep = np.clip((front - U - edge) / 0.01, 0, 1)
    img = lay(img, km * keep, gold)
    if _FLAKES is None:
        r = rng_for(708)
        _FLAKES = [(r.uniform(0.39, 0.62), r.uniform(0.455, 0.5), r.uniform(0.3, 1.0), r.uniform(0, 6.28)) for _ in range(260)]
    fb = Batch()
    for fu, fv, lum, ph in _FLAKES:
        ts = 0.8 + 3.2 * (0.64 - fu) / 0.3
        a = t - ts
        if a < 0 or a > 2.6:
            continue
        u = fu + 0.05 * a + 0.01 * math.sin(2 * a + ph)
        v = fv - 0.07 * a - 0.02 * a * a + 0.008 * math.cos(3 * a + ph)
        sz = 0.005 * (1 - a / 2.8)
        fb.ellipse(u, v, sz * ASP * 1.5, sz * 0.7, lum * (1 - a / 2.6), angle=ph * 30)
    fm, fv_ = fb.get(0.8)
    img = lay(img, np.clip(fm * fv_ * 1.8, 0, 1), PAL["gold"] * 1.05 + PAL["cream"] * 0.2)
    cam = (1.06 + 0.04 * t / d, 0.0, 0.0)
    return img, cam


# ------------------------------------------------------------------ 4a: the bells

def bell(img, pu, pv, size, ang, alpha=1.0):
    prof = [(0.1, 0.06), (0.24, 0.12), (0.3, 0.3), (0.32, 0.55), (0.4, 0.8), (0.52, 0.96), (0.56, 1.0)]
    pts = [(-x, y) for x, y in prof[::-1]] + list(prof)
    scr = []
    for x, y in pts:
        X, Y = rot(x * size * ASP, y * size, 0, 0, ang)
        scr.append((pu + X, pv + Y))
    sh = np.clip(0.75 + 0.7 * (U - pu) / (size * ASP), 0.35, 1.25)[..., None]
    img = lay(img, poly_mask(scr, 1.0) * alpha, (PAL["gold"] * 0.6 + PAL["umber2"] * 0.5) * sh)
    lip = [rot(x * size * ASP, 1.0 * size, 0, 0, ang) for x in (-0.56, 0.56)]
    img = lay(img, line_mask([(pu + lip[0][0], pv + lip[0][1]), (pu + lip[1][0], pv + lip[1][1])], 5, 1.0) * alpha,
              PAL["cream"] * 0.8)
    yoke = [rot(x * size * ASP, y * size, 0, 0, ang) for x, y in ((-0.22, -0.06), (0.22, -0.06), (0.22, 0.07), (-0.22, 0.07))]
    img = lay(img, poly_mask([(pu + a, pv + b) for a, b in yoke], 1.0) * alpha, PAL["umber"] * 1.3)
    mouth = rot(0, 1.0 * size, 0, 0, ang)
    return img, (pu + mouth[0], pv + mouth[1])


def s4a(t, d):
    img = black()
    arch = poly_mask([(0.2, 0.75), (0.2, 0.25), (0.8, 0.25), (0.8, 0.75)], 6) + ellipse_mask(0.5, 0.25, 0.3, 0.17, 0, 6) * (V < 0.25)
    img = lay(img, np.clip(arch, 0, 1) * blob(0.5, 0.4, 0.5, 0.45, 808, t, blur=20), vgrad(PAL["night"] * 0.9, PAL["peri"] * 0.45, 0.1, 0.8))
    bells = [(0.5, 0.17, 0.21, 2.6, 0.0), (0.5, 0.47, 0.14, 2.1, 1.1)]
    rings = []
    for pu, pv, size, T, ph in bells:
        ang = 0.38 * math.sin(2 * math.pi * t / T + ph)
        img, mouth = bell(img, pu, pv, size, ang)
        # a toll at each end of the swing; rings born there spread and fade
        k0 = math.floor((t * 2 / T) + ph / math.pi - 0.5)
        for k in range(k0 - 3, k0 + 1):
            te = (k + 0.5 - ph / math.pi) * T / 2
            if te < -1.6 or te > t:
                continue
            angk = 0.38 * math.sin(2 * math.pi * te / T + ph)
            mk = rot(0, size, 0, 0, angk)
            rings.append((pu + mk[0], pv + mk[1], t - te, size))
    rb = Batch()
    for u, v, a, size in rings:
        if a > 1.8:
            continue
        r = size * (0.35 + 1.6 * a)
        rb.ellipse(u, v, r * ASP * 0.9, r * 0.45, 0)  # placeholder for coverage, drawn as an outline below
    for u, v, a, size in rings:
        if a > 1.8:
            continue
        r = size * (0.35 + 1.6 * a)
        m = np.clip(ellipse_mask(u, v, r * ASP * 0.9, r * 0.45, 0, 2.5) - ellipse_mask(u, v, r * ASP * 0.9 * 0.93, r * 0.45 * 0.88, 0, 2.5), 0, 1)
        img = lay(img, m * (1 - a / 1.8) * 0.85, PAL["light"] * 0.95)
    img = lay(img, poly_mask([(0.0, 0.135), (1.0, 0.135), (1.0, 0.165), (0.0, 0.165)], 2), PAL["umber"] * 1.1)
    for pu in (0.1, 0.9):
        img = lay(img, poly_mask([(pu - 0.02, 0.0), (pu + 0.02, 0.0), (pu + 0.02, 1.0), (pu - 0.02, 1.0)], 3) * 0.7, PAL["umber"] * 0.6)
    cam = (1.03, 0.0, 0.0)
    return img, cam


# ------------------------------------------------------------------ 4b: ghost horsemen on the snow
_SNOW = None


def horseman(b, u, v, s, val, ph):
    """a ghost rider seen side-on, horse facing right."""
    bw = 0.06 * s
    X = lambda k: u + k * bw * ASP * 0.5
    Y = lambda k: v + k * bw
    b.ellipse(u, v, bw * ASP * 0.3, bw * 0.17, val)  # barrel
    b.poly([(X(0.4), Y(-0.08)), (X(0.6), Y(-0.5)), (X(0.78), Y(-0.52)), (X(0.62), Y(0.02))], val)  # neck
    b.ellipse(X(0.86), Y(-0.44), bw * ASP * 0.085, bw * 0.05, val, angle=35)  # head
    b.line([(X(-0.55), Y(-0.06)), (X(-0.72), Y(0.12)), (X(-0.7), Y(0.32))], max(1, 3 * s), val * 0.8)  # tail
    for k, lx in enumerate((-0.42, -0.28, 0.3, 0.45)):
        sw = 0.12 * math.sin(ph + k * 1.7)
        b.line([(X(lx), Y(0.1)), (X(lx + sw * 0.5), Y(0.45)), (X(lx + sw), Y(0.8))], max(1, 3.5 * s), val)
    b.poly([(X(-0.08), Y(-0.12)), (X(0.1), Y(-0.12)), (X(0.06), Y(-0.62)), (X(-0.06), Y(-0.62))], val)  # rider
    b.ellipse(X(0.0), Y(-0.72), bw * ASP * 0.06, bw * 0.08, val)
    b.poly([(X(-0.05), Y(-0.6)), (X(-0.45 - 0.05 * math.sin(ph)), Y(-0.35)), (X(-0.4), Y(-0.2)), (X(-0.05), Y(-0.3))],
           val * 0.7)  # cloak streaming back


def s4b(t, d):
    global _SNOW
    img = black()
    hz = 0.53
    sky = blob(0.5, 0.36, 0.62, 0.42, 909, t, blur=30)
    img = lay(img, sky, vgrad(PAL["night"] * 0.9, PAL["peri"] * 0.85, 0.05, hz))
    field = vgrad(PAL["snow"] * 0.8, PAL["peri"] * 0.4, hz, 0.95)
    img = lay(img, np.clip((V - hz) / 0.01, 0, 1) * blob(0.5, 0.62, 0.65, 0.35, 910, t, blur=24), field)
    img = lay(img, np.exp(-((V - hz) / 0.025) ** 2) * 0.6, PAL["bone"] * 0.9)  # mist on the horizon
    riders = [(-0.08, 0.32, 0.2), (1.08, 0.68, 0.5), (0.1, 0.4, 0.9), (0.9, 0.58, 1.3), (-0.05, 0.25, 1.8),
              (1.05, 0.75, 2.2), (0.35, 0.5, 2.6)]
    b = Batch()
    for k, (u0, u1, ts) in enumerate(riders):
        a = t - ts
        if a < 0:
            continue
        f = ease(a / 2.8)
        u = u0 + (u1 - u0) * f
        horseman(b, u, hz - 0.012 + 0.002 * math.sin(a * 6 + k), 1.35, min(1.0, a / 0.9), a * 7 + k)
    m, val = b.get(1.4)
    img = lay(img, m * val * 0.75, PAL["bone"] * 1.1 + PAL["snow"] * 0.1)
    if _SNOW is None:
        r = rng_for(911)
        _SNOW = [(r.uniform(-0.2, 1.0), r.uniform(0, 1), r.uniform(0.6, 1.4), r.uniform(0.4, 1)) for _ in range(500)]
    sb = Batch()
    for u0, v0, sp, lum in _SNOW:
        u = (u0 + 0.025 * t * sp) % 1.1
        v = (v0 + 0.05 * t * sp) % 1.0
        sb.ellipse(u, v, 0.0018 * ASP * sp, 0.0018 * sp, lum)
    sm, sv = sb.get(0.6)
    img = lay(img, sm * sv * 0.8, PAL["snow"])
    cam = (1.05, -0.02 + 0.04 * t / d, 0.0)
    return img, cam


# ------------------------------------------------------------------ 4c: the mirror and the cracked crown

def s4c(t, d):
    img = black()
    img = lay(img, blob(0.5, 0.4, 0.5, 0.42, 1111, t, blur=30), PAL["umber"] * 0.9)
    fr = poly_mask([(0.22, 0.08), (0.78, 0.08), (0.78, 0.64), (0.22, 0.64)], 1.2)
    glass_m = poly_mask([(0.27, 0.115), (0.73, 0.115), (0.73, 0.605), (0.27, 0.605)], 1.0)
    img = lay(img, fr, PAL["gold"] * 0.75 * np.clip(0.8 + 0.6 * (0.5 - U), 0.5, 1.2)[..., None])
    ob = Batch()
    for cu_, cv_ in ((0.22, 0.08), (0.78, 0.08), (0.22, 0.64), (0.78, 0.64), (0.5, 0.075)):
        ob.ellipse(cu_, cv_, 0.03 * ASP, 0.025, 1)
    om, _ = ob.get(1.5)
    img = lay(img, om, PAL["gold"] * 0.9)
    glass = vgrad(PAL["bluegrey"] * 0.75, PAL["night"] * 0.8, 0.11, 0.6)
    refl = glass.copy()
    refl = lay(refl, soft_radial(0.42, 0.25, 0.3, 0.25, 1.2) * 0.5, PAL["snow"] * 0.6)
    crack = ease((t - 0.8) / 3.4)
    refl = king_front(refl, 0.5, 0.74, 0.5, crack=crack, cloak=PAL["bone"] * 0.7 + PAL["peri"] * 0.15)
    img = lay(img, glass_m, refl)
    # the crack in the glass itself, following the crown
    if crack > 0:
        pts = [(0.5, 0.31 - 0.01)]
        r = rng_for(1112)
        for k in range(int(1 + 7 * crack)):
            pts.append((pts[-1][0] + r.uniform(-0.03, 0.03), pts[-1][1] + 0.022))
        img = lay(img, line_mask(pts, 2, 0.6) * glass_m, PAL["light"])
    # the king himself, from behind, in the foreground
    img = king_back(img, 0.24, 1.18, 0.75, cloak=PAL["bone"] * 0.75, head_col=PAL["black"] + PAL["umber"] * 0.5)
    cam = (1.0 + 0.08 * ease(t / d), 0.02 * ease(t / d), -0.04 * ease(t / d))
    return img, cam


# ------------------------------------------------------------------ 5a: the wind opens the doors
_SHARDS = None
_WIND = None


def s5a(t, d):
    global _SHARDS, _WIND
    img = black()
    img = lay(img, blob(0.5, 0.45, 0.55, 0.45, 1212, t, blur=30), PAL["umber"] * 0.8)
    door_l, door_r, top, bot = 0.31, 0.69, 0.36, 0.86
    open_ = ease((t - 0.9) / 1.4)
    storm = vgrad(PAL["peri"] * 1.0, PAL["night"] * 0.9, top, bot)
    storm = lay(storm, soft_radial(0.5, 0.55, 0.25, 0.25, 1.2) * 0.6, PAL["snow"] * 0.9)
    opening = poly_mask([(door_l, top), (door_r, top), (door_r, bot), (door_l, bot)], 1.0) + \
        ellipse_mask(0.5, top, 0.19, 0.08, 0, 1.0) * (V < top)
    img = lay(img, np.clip(opening, 0, 1), storm)
    hw = (door_r - door_l) / 2
    for side, hinge in ((-1, door_l), (1, door_r)):
        w = hw * math.cos(open_ * 1.35)
        inner = hinge - side * w
        sk = 0.04 * math.sin(open_ * 1.35)
        pts = [(hinge, top), (inner, top + sk), (inner, bot - sk), (hinge, bot)]
        img = lay(img, poly_mask(pts, 1.0), PAL["umber2"] * 0.9)
        img = lay(img, line_mask([(hinge + (inner - hinge) * 0.5, top + sk * 0.5 + 0.03), (hinge + (inner - hinge) * 0.5, bot - sk * 0.5 - 0.03)], 3, 1.0) * 0.8, PAL["golddk"] * 1.2)
    # the window above, shattering
    wtop, wbot = 0.08, 0.27
    t_sh = 1.9
    if t < t_sh:
        wm = poly_mask([(0.42, 0.13), (0.58, 0.13), (0.58, wbot), (0.42, wbot)], 1.0) + ellipse_mask(0.5, 0.13, 0.08 * ASP * 0.56, 0.05, 0, 1.0) * (V < 0.13)
        img = lay(img, np.clip(wm, 0, 1), PAL["cream"] * (0.7 + 0.25 * t))
        lb = Batch()
        for k in range(1, 4):
            lb.line([(0.42 + k * 0.04, 0.09), (0.42 + k * 0.04, wbot)], 2, 1)
        for k in range(1, 5):
            lb.line([(0.42, 0.13 + k * 0.028), (0.58, 0.13 + k * 0.028)], 2, 1)
        lm, _ = lb.get(0.7)
        img = lay(img, lm, PAL["umber"])
    else:
        if _SHARDS is None:
            r = rng_for(1213)
            _SHARDS = []
            for k in range(70):
                cu, cv_ = r.uniform(0.42, 0.58), r.uniform(0.1, wbot)
                ang = math.atan2(cv_ - 0.17, cu - 0.5) + r.uniform(-0.6, 0.6)
                sp = r.uniform(0.12, 0.35)
                tri = [(r.uniform(-1, 1), r.uniform(-1, 1)) for _ in range(3)]
                _SHARDS.append((cu, cv_, ang, sp, tri, r.uniform(0.008, 0.02), r.uniform(-3, 3), r.uniform(0.6, 1)))
        a = t - t_sh
        sb = Batch()
        for cu, cv_, ang, sp, tri, sz, spin, lum in _SHARDS:
            grow = 1 + 1.6 * a
            u = cu + math.cos(ang) * sp * a * ASP * 0.4
            v = cv_ + math.sin(ang) * sp * a * 0.5 + 0.08 * a * a
            pts = []
            for x, y in tri:
                X, Y = rot(x * sz * grow * ASP, y * sz * grow, 0, 0, spin * a)
                pts.append((u + X, v + Y))
            sb.poly(pts, lum * max(0, 1 - a / 3.2))
        sm, sv = sb.get(0.8)
        img = lay(img, sm * np.clip(sv * 1.5, 0, 1), PAL["light"] * 1.15)
    # wind: swept strokes blowing in through the doors
    if _WIND is None:
        r = rng_for(1214)
        _WIND = [(r.uniform(0.2, 0.8), r.uniform(0.3, 0.9), r.uniform(0.5, 1.0), r.uniform(0, 6.28), r.uniform(0.6, 1.4)) for _ in range(40)]
    wb = Batch()
    for u0, v0, lum, ph, sp in _WIND:
        a = (t * 0.35 * sp + ph / 6.28) % 1.0
        pts = []
        for k in range(10):
            f = a + k * 0.02
            ang = ph + f * 5
            rr = 0.35 * (1 - f) + 0.05
            pts.append((0.5 + math.cos(ang) * rr * ASP * 0.5, 0.58 + math.sin(ang) * rr * 0.7))
        wb.line(pts, 3 + 4 * lum, lum * open_ * math.sin(math.pi * a))
    wm2, wv = wb.get(1.6)
    img = lay(img, wm2 * wv * 0.6, PAL["bone"] * 0.9)
    cam = (1.02 + 0.05 * t / d, 0.0, 0.0)
    return img, cam


# ------------------------------------------------------------------ 5b: the crowd pours in under one red flag
_PEOPLE = None


def s5b(t, d):
    global _PEOPLE
    img = black()
    img = lay(img, blob(0.5, 0.48, 0.55, 0.45, 1313, t, blur=30), PAL["umber"] * 0.7)
    arch = np.clip(poly_mask([(0.22, 0.32), (0.78, 0.32), (0.78, 0.92), (0.22, 0.92)], 2) +
                   ellipse_mask(0.5, 0.32, 0.28, 0.14, 0, 2) * (V < 0.32), 0, 1)
    back = vgrad(PAL["snow"] * 0.9, PAL["peri"] * 0.8, 0.2, 0.9)
    back = lay(back, soft_radial(0.5, 0.45, 0.3, 0.3, 1.0) * 0.7, PAL["ivory"] * 0.95)
    img = lay(img, arch, back)
    if _PEOPLE is None:
        r = rng_for(1314)
        _PEOPLE = sorted([(r.uniform(-1.2, d), r.uniform(-1, 1), r.uniform(0.85, 1.15), r.uniform(0, 6.28)) for _ in range(140)],
                         key=lambda p: p[0], reverse=True)
    b = Batch()
    for ts, side, s0, ph in _PEOPLE:
        a = t - ts
        if a < 0 or a > 3.2:
            continue
        f = a / 3.2
        sc = (0.35 + 2.4 * f ** 1.6) * s0
        u = 0.5 + side * (0.12 + 0.55 * f ** 1.4)
        v = 0.66 + 0.5 * f ** 1.5 + 0.004 * math.sin(a * 9 + ph)
        b.ellipse(u, v - 0.05 * sc, 0.022 * sc * ASP * 0.55, 0.026 * sc, 0.1)
        b.ellipse(u, v + 0.02 * sc, 0.06 * sc * ASP * 0.55, 0.06 * sc, 0.1)
        b.poly([(u - 0.055 * sc * ASP * 0.55, v + 0.02 * sc), (u + 0.055 * sc * ASP * 0.55, v + 0.02 * sc),
                (u + 0.07 * sc * ASP * 0.55, v + 0.3 * sc), (u - 0.07 * sc * ASP * 0.55, v + 0.3 * sc)], 0.1)
    m, _ = b.get(1.4)
    img = lay(img, m, PAL["black"] + PAL["umber"] * 0.25)
    # the red flag, carried in, the only red in the frame
    f = ease(t / d)
    pole_b = (0.56 - 0.03 * f, 0.72 + 0.1 * f)
    pole_t = (0.53 - 0.04 * f, 0.2 - 0.06 * f)
    img = lay(img, line_mask([pole_b, pole_t], 4 + 3 * f, 0.8), PAL["umber"] * 0.5)
    fw, fh = 0.2 + 0.08 * f, 0.1 + 0.035 * f
    topl, botl = [], []
    for k in range(12):
        x = k / 11
        wv = 0.022 * math.sin(6 * x - 4.2 * t) * x
        topl.append((pole_t[0] + x * fw * ASP * 0.56, pole_t[1] + wv + 0.01 * x))
        botl.append((pole_t[0] + x * fw * ASP * 0.56 * 0.97, pole_t[1] + fh + wv * 1.2 + 0.02 * x))
    flag = topl + botl[::-1]
    fm = poly_mask(flag, 1.2)
    shade = (0.75 + 0.35 * np.sin(np.clip((U - pole_t[0]) / (fw * ASP * 0.56), 0, 1) * 6 - 4.2 * t))[..., None]
    img = lay(img, fm, PAL["red"] * 1.15 * shade)
    cam = (1.02 + 0.04 * t / d, 0.0, 0.0)
    return img, cam


# ------------------------------------------------------------------ 5c: the marionette and the cut thread

def s5c(t, d):
    img = black()
    img = lay(img, blob(0.5, 0.4, 0.42, 0.42, 1414, t, blur=30), PAL["night"] * 0.55)
    img = lay(img, soft_radial(0.5, 0.25, 0.4, 0.45, 1.3) * 0.7, PAL["peri"] * 1.0)
    t_cut = 3.0
    top = (0.5, -0.05)
    L = 0.3
    if t < t_cut:
        sw = 0.11 * math.sin(2 * math.pi * t / 2.3)
        drop, spin = 0.0, 0.0
    else:
        a = t - t_cut
        sw = 0.11 * math.sin(2 * math.pi * t_cut / 2.3) * (1 - min(1, a))
        drop = 0.5 * 1.5 * a * a
        spin = 0.5 * a
    head = (top[0] + math.sin(sw) * L * ASP * 0.5, top[1] + math.cos(sw) * L + drop)
    cut_v = 0.07
    if t < t_cut:
        img = lay(img, line_mask([top, head], 2, 0.5), PAL["gold"] * 1.1)
    else:
        st = (top[0] + math.sin(sw) * (cut_v - top[1]) * ASP * 0.5, cut_v)
        img = lay(img, line_mask([top, st], 2, 0.5), PAL["gold"] * 1.1)
        img = lay(img, line_mask([(head[0], max(head[1] - 0.25, cut_v + drop)), head], 2, 0.5), PAL["gold"])
        a = t - t_cut
        if a < 0.35:  # the snip: a small point of light where the thread parts
            img = lay(img, ellipse_mask(st[0], cut_v, 0.006 * ASP, 0.006, 0, 1.0) * (1 - a / 0.35), PAL["light"] * 1.3)
    if head[1] < 1.15:
        ang = sw * 0.6 + spin
        wood = PAL["cream2"] * 0.8
        dark = PAL["umber2"] * 1.2

        def P2(x, y, k=1.55):
            X, Y = rot(x * ASP * k, y * k, 0, 0, ang)
            return (head[0] + X, head[1] + Y)

        flail = 0.0 if t < t_cut else min(1.0, (t - t_cut) * 1.2)
        body = [P2(-0.035 * 0.56, 0.035), P2(0.035 * 0.56, 0.035), P2(0.06 * 0.56, 0.21), P2(-0.06 * 0.56, 0.21)]
        img = lay(img, poly_mask(body, 1.0), PAL["bone"] * 0.85)
        b = Batch()
        limbs = [((-0.04, 0.06), (-0.1, 0.1), (-0.12 - 0.04 * flail, 0.17 - 0.1 * flail)),   # arms splay out
                 ((0.04, 0.06), (0.1, 0.11), (0.13 + 0.04 * flail, 0.18 - 0.09 * flail)),
                 ((-0.02, 0.21), (-0.035, 0.27), (-0.03 - 0.04 * flail, 0.33 - 0.04 * flail)),  # legs bend
                 ((0.02, 0.21), (0.04, 0.27), (0.035 + 0.04 * flail, 0.33 - 0.03 * flail))]
        for (sx, sy), (mx, my), (ex, ey) in limbs:
            a, m_, e = P2(sx * 0.56, sy), P2(mx * 0.56, my), P2(ex * 0.56, ey)
            b.line([a, m_], 10, 0.75)
            b.line([m_, e], 9, 0.8)
            for q, r_ in ((a, 0.009), (m_, 0.009), (e, 0.011)):  # wooden joints
                b.ellipse(q[0], q[1], r_ * ASP, r_, 1.0)
        m, val = b.get(1.0)
        img = lay(img, m, wood * (0.6 + 0.4 * val[..., None]))
        img = lay(img, ellipse_mask(*P2(0, 0.0), 0.034 * ASP, 0.04, -math.degrees(ang), 1.0), wood)
        img = lay(img, ellipse_mask(*P2(0.008 * 0.56, -0.005), 0.018 * ASP, 0.022, 0, 1.5) * 0.35, dark)
        img = lay(img, line_mask([P2(-0.02 * 0.56, 0.028), P2(0.02 * 0.56, 0.028)], 2, 0.6) * 0.6, dark)  # jaw seam
        cr = [P2(x * 0.56, y) for x, y in ((-0.025, -0.02), (-0.03, -0.05), (-0.012, -0.035), (0.0, -0.058),
                                            (0.012, -0.035), (0.03, -0.05), (0.025, -0.02))]
        img = lay(img, poly_mask(cr, 0.7), PAL["gold"] * 1.05)
        img = lay(img, ellipse_mask(*P2(0, -0.03), 0.006 * ASP, 0.006, 0, 0.6), PAL["redhot"])
    cam = (1.03, 0.0, 0.0)
    return img, cam


# ------------------------------------------------------------------ 6a: the walk toward the slit of light

def s6a(t, d):
    img = black()
    f = t / d
    w = 0.006 + 0.007 * ease(f)
    img = lay(img, soft_radial(0.5, 0.42, 0.12, 0.3, 2.2) * 0.35, PAL["cream2"] * 0.6)
    img = lay(img, poly_mask([(0.5 - w, 0.2), (0.5 + w, 0.2), (0.5 + w, 0.6), (0.5 - w, 0.6)], 1.5), PAL["light"] * 1.15)
    floor = poly_mask([(0.5 - w * 1.5, 0.6), (0.5 + w * 1.5, 0.6), (0.5 + w * 7, 0.9), (0.5 - w * 7, 0.9)], 8)
    img = img + (floor * np.clip(1 - (V - 0.6) / 0.3, 0, 1) * 0.35)[..., None] * PAL["cream"]  # its light on the floor
    vf = 0.86 - 0.24 * f ** 0.9
    hgt = 0.36 - 0.24 * f ** 0.8
    bob = 0.005 * abs(math.sin(math.pi * t * 1.5)) * (1 - f)
    u = 0.5 + 0.03 * (1 - f) * math.sin(t * 0.5)
    rim = PAL["bone"] * 0.75
    img = king_back(img, u, vf - bob, hgt, crown=False, cloak=rim, head_col=PAL["bone"] * 0.55)
    cam = (1.0 + 0.04 * f, 0.0, 0.0)
    return img, cam


# ------------------------------------------------------------------ 6b: the crown falls and rolls away

def s6b(t, d):
    img = black()
    floor_v = 0.6
    t = max(0.0, t - 0.6)  # the fall starts once the melt into this shot has cleared
    d = d - 0.6
    if t < 1.0:
        a = t / 1.0
        cu, cv_ = 0.5, 0.12 + (floor_v - 0.12) * a * a
        rx, ry, rz, spin = -0.4 + 1.3 * a, 0.0, 0.3 * a, 2.0 * a
        size = 0.07
    elif t < 1.5:
        a = (t - 1.0) / 0.5
        cu, cv_ = 0.5, floor_v - 0.05 * math.sin(math.pi * a)
        rx, ry, rz, spin = 0.9 + 0.3 * a, 0.0, 0.3 + 1.0 * ease(a), 2.0 + 0.8 * a
        size = 0.07
    else:
        a = (t - 1.5) / (d - 1.5)
        cu = 0.5 + 0.2 * ease(a)
        cv_ = floor_v - 0.1 * a
        size = 0.07 * (1 - 0.65 * a)
        rx, ry, rz, spin = 1.2, 0.6, 1.3, 2.8 + 9.0 * a
    dim = 1.0 if t < 1.5 else 1 - 0.85 * ease((t - 1.5) / (d - 1.5))
    img = lay(img, soft_radial(cu, cv_ + 0.03, 0.35, 0.12, 1.4) * 0.55 * dim, PAL["umber2"] * 1.4)
    img = lay(img, soft_radial(cu, cv_ - 0.02, 0.22, 0.12, 1.6) * 0.35 * dim, PAL["cream2"] * 0.7)
    img = crown3d(img, cu, cv_ - size * 0.5, size, rx, ry, rz, alpha=dim ** 0.5, spin=spin)
    cam = (1.02, 0.0, 0.0)
    return img, cam


SHOTS = {
    "s1a": dict(fn=s1a, seed=11, flow="horizontal"),
    "s1b": dict(fn=s1b, seed=12, flow="vertical"),
    "s2a": dict(fn=s2a, seed=21, flow="vertical"),
    "s2b": dict(fn=s2b, seed=22, flow="swirl"),
    "s3a": dict(fn=s3a, seed=31, flow="vertical"),
    "s3b": dict(fn=s3b, seed=32, flow="vertical"),
    "s3c": dict(fn=s3c, seed=33, flow="swirl"),
    "s4a": dict(fn=s4a, seed=41, flow="swirl"),
    "s4b": dict(fn=s4b, seed=42, flow="horizontal"),
    "s4c": dict(fn=s4c, seed=43, flow="vertical"),
    "s5a": dict(fn=s5a, seed=51, flow="swirl"),
    "s5b": dict(fn=s5b, seed=52, flow="vertical"),
    "s5c": dict(fn=s5c, seed=53, flow="vertical"),
    "s6a": dict(fn=s6a, seed=61, flow="vertical"),
    "s6b": dict(fn=s6b, seed=62, flow="swirl"),
}
