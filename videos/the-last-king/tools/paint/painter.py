"""Procedural wet-oil painter: soft underpainting -> flow-aligned brushstrokes.

Each shot draws an underpainting per frame (float BGR in 0..1 at working resolution), then
`Painter.paint` turns it into a moving oil painting:
  1. the stroke direction comes from the image's own structure tensor (strokes run along forms),
     blended with the shot's own flow where the image is flat;
  2. a line-integral convolution smears colour and a bristle-noise texture along that direction,
     so every area becomes long, smooth, curved strokes with streaks in them;
  3. the bristle noise is fixed to the camera (no shower-door crawl) and "boils" slowly, like
     paint-on-glass animation repainted frame to frame.
Deterministic: frame i of a shot is a pure function of (shot, i).
"""
import math
import subprocess

import cv2
import numpy as np

OUT_W, OUT_H, FPS = 1080, 1920, 24
W, H = 720, 1280  # working resolution


def hexc(h):
    h = h.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return np.array([b, g, r], np.float32) / 255.0


PAL = {
    "black": hexc("000000"),
    "umber": hexc("28211C"),
    "umber2": hexc("3C3632"),
    "grey": hexc("514B4B"),
    "bluegrey": hexc("51546E"),
    "peri": hexc("6F78A8"),
    "night": hexc("1C1F3A"),
    "cream": hexc("C9BD86"),
    "cream2": hexc("A6977A"),
    "light": hexc("E6DDB0"),
    "bone": hexc("B4ADB0"),
    "gold": hexc("C9A24A"),
    "golddk": hexc("7A5A22"),
    "red": hexc("A1382A"),
    "redhot": hexc("C8432F"),
    "ivory": hexc("DCD3BE"),
    "snow": hexc("C9CBD8"),
}

YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
ASPX = H / W
U, V = XX / W, YY / H  # normalised coordinates, v grows downward


# ---------------------------------------------------------------- drawing helpers

def P(u, v):
    """normalised -> working pixel coords (fixed-point, shift=3)."""
    return (int(round(u * W * 8)), int(round(v * H * 8)))


def poly_mask(pts, blur=1.0):
    m = np.zeros((H, W), np.uint8)
    arr = np.array([[int(round(u * W * 8)), int(round(v * H * 8))] for u, v in pts], np.int32)
    cv2.fillPoly(m, [arr], 255, cv2.LINE_AA, shift=3)
    m = m.astype(np.float32) / 255.0
    return cv2.GaussianBlur(m, (0, 0), blur) if blur > 0 else m


def ellipse_mask(cu, cv, ru, rv, angle=0.0, blur=1.0):
    m = np.zeros((H, W), np.uint8)
    cv2.ellipse(m, P(cu, cv), (max(1, int(ru * W * 8)), max(1, int(rv * H * 8))), angle, 0, 360,
                255, -1, cv2.LINE_AA, shift=3)
    m = m.astype(np.float32) / 255.0
    return cv2.GaussianBlur(m, (0, 0), blur) if blur > 0 else m


def line_mask(pts, width_px, blur=0.8):
    m = np.zeros((H, W), np.uint8)
    arr = np.array([[int(round(u * W * 8)), int(round(v * H * 8))] for u, v in pts], np.int32)
    cv2.polylines(m, [arr], False, 255, max(1, int(round(width_px))), cv2.LINE_AA, shift=3)
    m = m.astype(np.float32) / 255.0
    return cv2.GaussianBlur(m, (0, 0), blur) if blur > 0 else m


def soft_radial(cu, cv, ru, rv, power=1.6):
    d = np.sqrt(((U - cu) / ru) ** 2 + ((V - cv) / rv) ** 2)
    return np.clip(1 - d, 0, 1) ** power


def vgrad(c_top, c_bot, v0=0.0, v1=1.0):
    t = np.clip((V - v0) / (v1 - v0), 0, 1)[..., None]
    return c_top * (1 - t) + c_bot * t


def lay(img, mask, color):
    """paint `color` (vec3 or HxWx3) over img through mask (HxW)."""
    m = mask[..., None]
    return img * (1 - m) + color * m


def blob(cu, cv, ru, rv, seed, t=0.0, wobble=0.18, blur=18.0, lobes=6, speed=0.15):
    """an irregular pool of light: an ellipse whose radius is modulated by a few seeded sines."""
    rng = np.random.default_rng(seed)
    ph = rng.uniform(0, 2 * np.pi, lobes)
    fr = np.arange(2, 2 + lobes)
    amp = rng.uniform(0.3, 1.0, lobes) / np.arange(1, lobes + 1) ** 0.6
    ang = np.arctan2((V - cv) / rv, (U - cu) / ru)
    r = np.sqrt(((U - cu) / ru) ** 2 + ((V - cv) / rv) ** 2)
    mod = np.zeros_like(r)
    for k in range(lobes):
        mod += amp[k] * np.sin(fr[k] * ang + ph[k] + speed * t * (1 + k * 0.3))
    mod = mod / amp.sum()
    edge = 1 + wobble * mod
    m = np.clip((edge - r) / 0.25, 0, 1)
    m = m * m * (3 - 2 * m)
    return cv2.GaussianBlur(m.astype(np.float32), (0, 0), blur)


def fbm(seed, cells=6, octaves=4, w=W, h=H):
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    amp, tot, c = 1.0, 0.0, cells
    for _ in range(octaves):
        ch = max(2, int(round(c * h / w)))
        g = rng.random((ch + 1, c + 1)).astype(np.float32)
        out += amp * cv2.resize(g, (w, h), interpolation=cv2.INTER_CUBIC)
        tot += amp
        amp *= 0.5
        c *= 2
    out /= tot
    return (out - out.min()) / max(1e-6, out.max() - out.min())


def rot(px, py, cx, cy, a):
    ca, sa = math.cos(a), math.sin(a)
    x, y = px - cx, py - cy
    return cx + ca * x - sa * y, cy + sa * x + ca * y


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


# ---------------------------------------------------------------- figures

def king_back(img, cu, v_feet, height, t=0.0, arm=None, cloak=None, crown=True, head_drop=0.0,
              alpha=1.0, seated=False, head_col=None):
    """the king seen from behind: a long flaring pale cloak, the dark back of a head, a gold crown.
    arm: right arm raise angle in radians (0 = hanging, ~2.4 = up and out to the right)."""
    cloak = PAL["bone"] if cloak is None else cloak
    head_col = PAL["umber2"] if head_col is None else head_col
    hgt = height
    head_r = hgt * 0.062
    sh_v = v_feet - hgt * (0.80 if not seated else 0.62) + head_drop * hgt
    hd_v = sh_v - head_r * 1.25
    sw = hgt * 0.11 * ASPX  # shoulder half-width in u
    left, right = [], []
    for k in range(13):
        f = k / 12
        if seated:
            wdt = sw * (1.0 + 1.3 * f ** 1.2)
        else:
            wdt = sw * (0.92 + 0.95 * f ** 1.7)
        v = sh_v + (v_feet - sh_v) * f
        bulge = 0.08 * sw * math.sin(math.pi * f)
        left.append((cu - wdt - bulge, v))
        right.append((cu + wdt + bulge, v))
    hem = [(cu + (right[-1][0] - cu) * math.cos(a), v_feet + 0.012 * hgt * math.sin(a))
           for a in np.linspace(0, math.pi, 9)]
    top = [(cu - sw * 0.92 + sw * 1.84 * f, sh_v - 0.02 * hgt * math.sin(math.pi * f)) for f in np.linspace(0, 1, 7)]
    body = top + right + hem + left[::-1]
    m = poly_mask(body, 1.0) * alpha
    shade = np.clip(0.8 + 0.45 * (U - cu) / (sw * 4) - 0.25 * (V - sh_v) / hgt, 0.5, 1.15)[..., None]
    img = lay(img, m, cloak * shade)
    for off in (-0.35, 0.3):  # folds
        img = lay(img, line_mask([(cu + sw * off, sh_v + hgt * 0.1), (cu + sw * off * 1.9, v_feet - hgt * 0.01)],
                                 max(2, hgt * H * 0.01), 2.5) * 0.3 * alpha, cloak * 0.62)
    if arm is not None:
        a = arm
        sx, sy = cu + sw * 0.75, sh_v + hgt * 0.04
        L = hgt * 0.36
        ex, ey = sx + math.sin(a) * L * ASPX, sy + math.cos(a) * L
        nx, ny = math.cos(a) * 0.009 * ASPX, -math.sin(a) * 0.009
        sleeve = [(sx - nx * 1.3, sy - ny * 1.3), (sx + nx * 1.3, sy + ny * 1.3), (ex + nx * 0.6, ey + ny * 0.6),
                  (ex - nx * 0.6, ey - ny * 0.6)]
        img = lay(img, poly_mask(sleeve, 1.0) * alpha, cloak * 0.92)
        img = lay(img, ellipse_mask(ex + math.sin(a) * 0.012 * ASPX, ey + math.cos(a) * 0.012, head_r * 0.42 * ASPX,
                                    head_r * 0.42, 0, 1.0) * alpha, PAL["cream"] * 1.05)
    img = lay(img, ellipse_mask(cu, sh_v - head_r * 0.2, head_r * 0.5 * ASPX, head_r * 0.5, 0, 1.2) * alpha, head_col)
    img = lay(img, ellipse_mask(cu, hd_v, head_r * 0.92 * ASPX, head_r, 0, 1.2) * alpha, head_col)
    if crown:
        cw = head_r * 1.0 * ASPX
        cb = hd_v - head_r * 0.45
        ch = head_r * 0.75
        pts = [(cu - cw, cb), (cu - cw * 1.05, cb - ch), (cu - cw * 0.6, cb - ch * 0.5), (cu - cw * 0.2, cb - ch * 1.15),
               (cu + cw * 0.2, cb - ch * 0.5), (cu + cw * 0.6, cb - ch * 1.15), (cu + cw * 1.05, cb - ch * 0.5),
               (cu + cw, cb)]
        img = lay(img, poly_mask(pts, 0.7) * alpha, PAL["gold"] * 1.1)
        img = lay(img, poly_mask([(cu - cw, cb), (cu + cw, cb), (cu + cw, cb - ch * 0.3), (cu - cw, cb - ch * 0.3)], 0.6)
                  * alpha, PAL["golddk"] * 1.2)
    return img


def crown3d(img, cu, cv, size, rx, ry, rz, alpha=1.0, light=(0.4, -0.6, 0.7), gem=True, crack=0.0, spin=0.0):
    """a gold circlet with five points, as a 3D ring projected to the screen.
    size: radius in v units. rx, ry, rz: rotation in radians."""
    n = 40
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    r, hgt = 1.0, 0.55
    pts_bot = np.stack([r * np.cos(th), np.zeros(n), r * np.sin(th)], 1)
    spike = 0.5 + 0.5 * np.cos(5 * th)
    pts_top = np.stack([r * np.cos(th), -(hgt + 0.55 * spike ** 3), r * np.sin(th)], 1)

    def R(p):
        cx, sx = math.cos(rx), math.sin(rx)
        cy, sy = math.cos(ry), math.sin(ry)
        cz, sz = math.cos(rz), math.sin(rz)
        Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
        Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
        Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
        cs, ss = math.cos(spin), math.sin(spin)
        Rs = np.array([[cs, 0, ss], [0, 1, 0], [-ss, 0, cs]])
        return p @ (Rz @ Ry @ Rx @ Rs).T

    pb, pt = R(pts_bot), R(pts_top)
    asp = ASPX
    to = lambda p: (cu + p[0] * size * asp, cv + p[1] * size)
    quads = []
    for i in range(n):
        j = (i + 1) % n
        z = (pb[i, 2] + pb[j, 2] + pt[i, 2] + pt[j, 2]) / 4
        e1, e2 = pb[j] - pb[i], pt[i] - pb[i]
        nrm = np.cross(e1, e2)
        nrm /= np.linalg.norm(nrm) + 1e-9
        lam = abs(float(np.dot(nrm, np.array(light) / np.linalg.norm(light))))
        quads.append((z, [to(pb[i]), to(pb[j]), to(pt[j]), to(pt[i])], lam, i))
    quads.sort(key=lambda q: -q[0])  # far first (larger z is farther)
    for z, q, lam, i in quads:
        back = z > 0
        col = PAL["gold"] * (0.35 + 0.85 * lam) * (0.6 if back else 1.0)
        img = lay(img, poly_mask(q, 0.6) * alpha, col)
    if gem:
        k = 0  # gem at the front-most spike base
        front = np.argmin(pb[:, 2])
        g = to((pb[front] * 0.6 + pt[front] * 0.4))
        if pb[front, 2] < 0.2:
            img = lay(img, ellipse_mask(g[0], g[1], size * 0.13 * asp, size * 0.13, 0, 0.8) * alpha, PAL["redhot"])
    if crack > 0:
        front = np.argmin(pb[:, 2])
        a = to(pt[front])
        b = to(pb[front])
        k = max(2, int(6 * crack))
        pts = []
        for s in range(k + 1):
            f = s / 6
            pts.append((a[0] + (b[0] - a[0]) * f + (0.012 if s % 2 else -0.01), a[1] + (b[1] - a[1]) * f))
        img = lay(img, line_mask(pts, 3, 0.6) * alpha, PAL["black"])
    return img


# ---------------------------------------------------------------- painter

class Painter:
    def __init__(self, seed, flow_kind="swirl", L=14, step=2.0, stroke_scale=1.0):
        rng = np.random.default_rng(seed)
        big = (int(H * 1.3), int(W * 1.3))
        self.noise_fine = rng.random(big).astype(np.float32)
        self.noise_wide = cv2.GaussianBlur(rng.random(big).astype(np.float32), (0, 0), 3.2)
        self.boil = [cv2.GaussianBlur(rng.random(big).astype(np.float32), (0, 0), 2.2) for _ in range(4)]
        self.tint = np.stack([fbm(seed + i, 4, 3, big[1], big[0]) for i in range(3)], -1) - 0.5
        self.L, self.step = L, step * stroke_scale
        self.flow_kind = flow_kind
        self.seed = seed
        # default flow where the picture is flat
        psi = fbm(seed + 9, 3, 3)
        if flow_kind == "swirl":
            psi = psi * 0.6 + np.exp(-(((U - 0.5) / 0.45) ** 2 + ((V - 0.42) / 0.35) ** 2)) * 1.4
        elif flow_kind == "horizontal":
            psi = psi * 0.4 + V * 2.0
        elif flow_kind == "vertical":
            psi = psi * 0.4 + U * 2.0
        psi = cv2.GaussianBlur(psi.astype(np.float32), (0, 0), 30)
        gy, gx = np.gradient(psi)
        fx, fy = gy, -gx
        n = np.sqrt(fx * fx + fy * fy) + 1e-6
        self.hx, self.hy = (fx / n).astype(np.float32), (fy / n).astype(np.float32)

    def _cam(self, tex, cam):
        """crop the oversized texture through the camera (scale, du, dv) so strokes move with it."""
        s, du, dv = cam
        th, tw = tex.shape[:2]
        cx, cy = tw / 2 + du * W, th / 2 + dv * H
        M = np.array([[1 / s, 0, cx - (W / 2) / s], [0, 1 / s, cy - (H / 2) / s]], np.float32)
        return cv2.warpAffine(tex, M, (W, H), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP,
                              borderMode=cv2.BORDER_REFLECT)

    def paint(self, under, t, cam=(1.0, 0.0, 0.0), tint_amt=0.06, streak=0.13, smear=1.0, keep=0.3):
        under = np.clip(under, 0, 1.5).astype(np.float32)
        tint = self._cam(self.tint, cam)
        lum0 = under.mean(2, keepdims=True)
        under = under + tint * tint_amt * np.clip(lum0 * 3, 0, 1)

        lum = cv2.GaussianBlur(under.mean(2), (0, 0), 2.0)
        gx = cv2.Sobel(lum, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(lum, cv2.CV_32F, 0, 1, ksize=3)
        sig = 7.0
        jxx = cv2.GaussianBlur(gx * gx, (0, 0), sig)
        jxy = cv2.GaussianBlur(gx * gy, (0, 0), sig)
        jyy = cv2.GaussianBlur(gy * gy, (0, 0), sig)
        tr = jxx + jyy
        det = np.sqrt((jxx - jyy) ** 2 + 4 * jxy * jxy)
        l1, l2 = (tr + det) / 2, (tr - det) / 2
        coh = (l1 - l2) / (l1 + l2 + 1e-7)
        ang = 0.5 * np.arctan2(2 * jxy, jxx - jyy) + np.pi / 2
        tx, ty = np.cos(ang), np.sin(ang)
        strength = np.clip(coh * np.clip(np.sqrt(l1) / 0.02, 0, 1), 0, 1)
        # orient the structure field consistently with the hint before blending
        sgn = np.sign(tx * self.hx + ty * self.hy + 1e-6)
        fx = strength * tx * sgn + (1 - strength) * self.hx
        fy = strength * ty * sgn + (1 - strength) * self.hy
        n = np.sqrt(fx * fx + fy * fy) + 1e-6
        fx, fy = (fx / n).astype(np.float32), (fy / n).astype(np.float32)

        k = t * 6.0  # boil: crossfade between bristle textures ~6 times a second
        i0 = int(math.floor(k)) % 4
        f = k - math.floor(k)
        f = f * f * (3 - 2 * f)
        boil = self.boil[i0] * (1 - f) + self.boil[(i0 + 1) % 4] * f
        noise = 0.2 * self._cam(self.noise_fine, cam) + 0.55 * self._cam(self.noise_wide, cam) \
            + 0.25 * self._cam(boil, cam)

        stack = np.dstack([under, noise[..., None]]).astype(np.float32)
        acc = stack.copy()
        wsum = 1.0
        L = max(2, int(self.L * smear))
        for sgn_dir in (1.0, -1.0):
            px, py = XX.copy(), YY.copy()
            dx, dy = fx * sgn_dir, fy * sgn_dir
            for s in range(1, L + 1):
                px = px + dx * self.step
                py = py + dy * self.step
                wk = 0.5 + 0.5 * math.cos(math.pi * s / (L + 1))
                acc += wk * cv2.remap(stack, px, py, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
                wsum += wk
                nfx = cv2.remap(fx, px, py, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
                nfy = cv2.remap(fy, px, py, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
                flip = np.where(nfx * dx + nfy * dy < 0, -1.0, 1.0).astype(np.float32)
                dx, dy = nfx * flip, nfy * flip
        acc /= wsum
        col, st = acc[..., :3], acc[..., 3]
        if keep > 0:  # keep some of the drawn form so small shapes still read
            col = col * (1 - keep) + cv2.GaussianBlur(under, (0, 0), 1.2) * keep
        st = (st - st.mean()) / (st.std() + 1e-6)
        lum = col.mean(2, keepdims=True)
        out = col * (1 + streak * 0.5 * st[..., None] * np.clip(lum * 4, 0.15, 1))
        # a faint raking light across the stroke ridges (smooth paint, not impasto)
        ex = cv2.Sobel(st, cv2.CV_32F, 1, 0, ksize=3)
        ey = cv2.Sobel(st, cv2.CV_32F, 0, 1, ksize=3)
        out += (-0.6 * ex - 0.8 * ey)[..., None] * 0.006 * np.clip(lum * 3, 0, 1)
        out = np.clip((out - 0.015) / 0.985, 0, 1)
        return out

    @staticmethod
    def finish(img):
        """working res -> output res, with a faint canvas weave."""
        big = cv2.resize(img, (OUT_W, OUT_H), interpolation=cv2.INTER_CUBIC)
        blur = cv2.GaussianBlur(big, (0, 0), 1.2)
        big = np.clip(big + 0.35 * (big - blur), 0, 1)
        return big


def weave():
    yy, xx = np.mgrid[0:OUT_H, 0:OUT_W].astype(np.float32)
    w = 0.5 + 0.25 * np.sin(xx * 1.9) + 0.25 * np.sin(yy * 2.1)
    w += 0.15 * np.sin((xx + yy) * 0.37)
    return (1 + 0.035 * (w - 0.5)).astype(np.float32)[..., None]


class Writer:
    def __init__(self, path):
        self.p = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{OUT_W}x{OUT_H}",
             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "15",
             "-pix_fmt", "yuv420p", "-movflags", "+faststart", path], stdin=subprocess.PIPE)
        self.weave = weave()

    def write(self, img):
        out = np.clip(img * self.weave * 255, 0, 255).astype(np.uint8)
        self.p.stdin.write(out.tobytes())

    def close(self):
        self.p.stdin.close()
        self.p.wait()


def apply_cam(img, cam):
    """zoom/pan the drawn underpainting through the camera (scale >= 1, du, dv in frame units)."""
    s, du, dv = cam
    cx, cy = W / 2 + du * W, H / 2 + dv * H
    M = np.array([[1 / s, 0, cx - (W / 2) / s], [0, 1 / s, cy - (H / 2) / s]], np.float32)
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP,
                          borderMode=cv2.BORDER_REPLICATE)


class Batch:
    """many small shapes into one coverage mask + one value map (fast: one blur at the end)."""

    def __init__(self):
        self.cov = np.zeros((H, W), np.uint8)
        self.val = np.zeros((H, W), np.uint8)

    def ellipse(self, u, v, ru, rv, value, angle=0.0):
        c, ax = P(u, v), (max(1, int(ru * W * 8)), max(1, int(rv * H * 8)))
        cv2.ellipse(self.cov, c, ax, angle, 0, 360, 255, -1, cv2.LINE_AA, shift=3)
        cv2.ellipse(self.val, c, ax, angle, 0, 360, int(np.clip(value, 0, 1) * 255), -1, cv2.LINE_AA, shift=3)

    def poly(self, pts, value):
        arr = np.array([[int(round(a * W * 8)), int(round(b * H * 8))] for a, b in pts], np.int32)
        cv2.fillPoly(self.cov, [arr], 255, cv2.LINE_AA, shift=3)
        cv2.fillPoly(self.val, [arr], int(np.clip(value, 0, 1) * 255), cv2.LINE_AA, shift=3)

    def line(self, pts, width_px, value):
        arr = np.array([[int(round(a * W * 8)), int(round(b * H * 8))] for a, b in pts], np.int32)
        wpx = max(1, int(round(width_px)))
        cv2.polylines(self.cov, [arr], False, 255, wpx, cv2.LINE_AA, shift=3)
        cv2.polylines(self.val, [arr], False, int(np.clip(value, 0, 1) * 255), wpx, cv2.LINE_AA, shift=3)

    def get(self, blur=1.0):
        m = self.cov.astype(np.float32) / 255.0
        v = self.val.astype(np.float32) / 255.0
        if blur > 0:
            m = cv2.GaussianBlur(m, (0, 0), blur)
            v = cv2.GaussianBlur(v, (0, 0), blur)
        return m, v
