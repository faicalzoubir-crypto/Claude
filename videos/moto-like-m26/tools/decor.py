"""Deterministic SVG decor for the M26 film: night street layers, rial coin, green splashes.

usage: python3 tools/decor.py  ->  assets/decor/*.svg
"""
import math, random

OUT = "assets/decor"
R = random.Random(2026)


def svg(w, h, body, extra=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'{extra}{body}</svg>')


# ── far layer: modern skyline + a square minaret, lit windows ─────────────────
def skyline(w=3600, h=700):
    out = []
    x = 0
    while x < w:
        bw = R.randint(110, 260)
        bh = R.randint(260, 640)
        top = h - bh
        out.append(f'<rect x="{x}" y="{top}" width="{bw}" height="{bh}" fill="#0f1522"/>')
        for wy in range(top + 26, h - 30, 34):
            for wx in range(x + 16, x + bw - 18, 28):
                if R.random() < 0.34:
                    col = "#ffcf7a" if R.random() < 0.7 else "#9fd2ff"
                    out.append(f'<rect x="{wx}" y="{wy}" width="12" height="16" fill="{col}" opacity="{R.uniform(0.35, 0.85):.2f}"/>')
        x += bw + R.randint(6, 40)
    # square minaret silhouette, twice along the strip
    for mx in (900, 2700):
        out.append(f'<rect x="{mx}" y="140" width="96" height="560" fill="#0d1320"/>'
                   f'<rect x="{mx + 18}" y="80" width="60" height="62" fill="#0d1320"/>'
                   f'<rect x="{mx + 36}" y="40" width="24" height="42" fill="#0d1320"/>'
                   f'<circle cx="{mx + 48}" cy="32" r="9" fill="#0d1320"/>'
                   f'<rect x="{mx + 30}" y="210" width="36" height="54" rx="18" fill="#ffcf7a" opacity="0.55"/>')
    return svg(w, h, "".join(out))


# ── mid layer: 3–5 storey buildings with arcades, palms and street lamps ──────
def street(w=4200, h=1100):
    out = []
    x = 0
    ground = h - 40
    pal = ["#161d2b", "#1a2232", "#141a26", "#1d2537"]
    while x < w:
        bw = R.randint(300, 520)
        floors = R.randint(3, 5)
        fh = 150
        top = ground - floors * fh - 40
        col = R.choice(pal)
        out.append(f'<rect x="{x}" y="{top}" width="{bw}" height="{ground - top}" fill="{col}"/>')
        out.append(f'<rect x="{x - 6}" y="{top - 14}" width="{bw + 12}" height="16" fill="#232c40"/>')
        # upper floors: tall windows with balconies
        for f in range(1, floors):
            wy = top + 30 + (f - 1) * fh
            nwin = max(2, bw // 110)
            step = bw / nwin
            for i in range(nwin):
                wx = x + step * i + step / 2 - 26
                lit = R.random() < 0.55
                c = "#ffc56b" if R.random() < 0.75 else "#a8d8ff"
                out.append(f'<rect x="{wx:.0f}" y="{wy}" width="52" height="86" rx="4" fill="{c if lit else "#0b0f18"}" opacity="{0.8 if lit else 1}"/>')
                out.append(f'<rect x="{wx - 8:.0f}" y="{wy + 86}" width="68" height="8" fill="#2a3449"/>')
        # ground floor arcade (Moroccan arches)
        na = max(2, bw // 130)
        aw = bw / na
        ay = ground - 150
        for i in range(na):
            ax = x + aw * i + 14
            a_w = aw - 28
            r = a_w / 2
            lit = R.random() < 0.6
            out.append(f'<path d="M{ax:.0f},{ground} L{ax:.0f},{ay + r:.0f} A{r:.0f},{r:.0f} 0 0 1 {ax + a_w:.0f},{ay + r:.0f} L{ax + a_w:.0f},{ground} Z" '
                       f'fill="{"#ffb54d" if lit else "#0a0e16"}" opacity="{0.55 if lit else 1}"/>')
        x += bw + R.randint(0, 24)
    # street lamps (warm glow) and palms in front of the facades
    glow = '<radialGradient id="lg"><stop offset="0" stop-color="#ffc46b" stop-opacity="0.75"/><stop offset="1" stop-color="#ffc46b" stop-opacity="0"/></radialGradient>'
    for lx in range(260, w, 700):
        out.append(f'<circle cx="{lx + 60}" cy="{ground - 520}" r="150" fill="url(#lg)"/>'
                   f'<rect x="{lx}" y="{ground - 520}" width="10" height="520" fill="#0a0d14"/>'
                   f'<path d="M{lx + 5},{ground - 520} q20,-30 60,-10" stroke="#0a0d14" stroke-width="10" fill="none"/>'
                   f'<ellipse cx="{lx + 62}" cy="{ground - 528}" rx="22" ry="9" fill="#ffd690"/>')
    for px in range(600, w, 900):
        hgt = R.randint(560, 700)
        out.append(f'<path d="M{px},{ground} q-14,-{hgt // 2} 8,-{hgt}" stroke="#0b0e15" stroke-width="22" fill="none"/>')
        tx, ty = px + 8, ground - hgt
        for k in range(9):
            a = math.radians(-170 + k * 40 + R.uniform(-8, 8))
            L = R.randint(150, 230)
            ex, ey = tx + L * math.cos(a), ty + L * math.sin(a) * 0.55 + 60
            cx, cy = tx + L * 0.5 * math.cos(a), ty + L * 0.5 * math.sin(a) - 40
            out.append(f'<path d="M{tx},{ty} Q{cx:.0f},{cy:.0f} {ex:.0f},{ey:.0f}" stroke="#0b0e15" stroke-width="16" fill="none" stroke-linecap="round"/>')
    # red and white kerb, typical of Moroccan streets
    for kx in range(0, w, 120):
        c = "#c8333a" if (kx // 120) % 2 == 0 else "#e9e4da"
        out.append(f'<rect x="{kx}" y="{ground}" width="120" height="40" fill="{c}" opacity="0.85"/>')
    return svg(w, h, "".join(out), f"<defs>{glow}</defs>")


# ── 5 centimes coin (1 rial) ─────────────────────────────────────────────────
def coin(s=400):
    c = s / 2
    defs = ('<defs><radialGradient id="cg" cx="0.38" cy="0.32" r="0.75">'
            '<stop offset="0" stop-color="#ffe9a3"/><stop offset="0.45" stop-color="#e8b23c"/>'
            '<stop offset="1" stop-color="#9a6a12"/></radialGradient>'
            '<linearGradient id="rim" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff0b8"/>'
            '<stop offset="1" stop-color="#8a5c0c"/></linearGradient></defs>')
    leaves = []
    for k in range(9):
        a = math.radians(200 + k * 16)
        x, y = c + 128 * math.cos(a), c + 128 * math.sin(a)
        leaves.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="13" ry="6" transform="rotate({math.degrees(a) + 90:.0f} {x:.1f} {y:.1f})" fill="#b98420" opacity="0.8"/>')
    body = (f'<circle cx="{c}" cy="{c}" r="{c - 4}" fill="url(#rim)"/>'
            f'<circle cx="{c}" cy="{c}" r="{c - 22}" fill="url(#cg)"/>'
            f'<circle cx="{c}" cy="{c}" r="{c - 34}" fill="none" stroke="#b98420" stroke-width="3" stroke-dasharray="2 7" opacity="0.8"/>'
            + "".join(leaves) +
            f'<text x="{c}" y="{c + 62}" text-anchor="middle" font-family="Georgia, serif" font-size="190" font-weight="700" fill="#a8741a">5</text>'
            f'<text x="{c - 3}" y="{c + 58}" text-anchor="middle" font-family="Georgia, serif" font-size="190" font-weight="700" fill="#fff2c4" opacity="0.55">5</text>')
    return svg(s, s, body, defs)


# ── lime paint splashes (poster style) ───────────────────────────────────────
def splash(w=1200, h=700, seed=7, color="#A6F21C"):
    r = random.Random(seed)
    out = []
    for _ in range(9):
        cx, cy = r.uniform(0.15, 0.85) * w, r.uniform(0.25, 0.75) * h
        pts = []
        n = 26
        base = r.uniform(60, 170)
        for i in range(n):
            a = 2 * math.pi * i / n
            rad = base * (0.55 + 0.6 * r.random())
            pts.append((cx + rad * math.cos(a) * 1.6, cy + rad * math.sin(a)))
        d = "M" + " L".join(f"{x:.0f},{y:.0f}" for x, y in pts) + " Z"
        out.append(f'<path d="{d}" fill="{color}" opacity="{r.uniform(0.75, 1):.2f}"/>')
    for _ in range(70):
        a = r.uniform(0, 2 * math.pi)
        dist = r.uniform(0.25, 0.62) * w
        x, y = w / 2 + dist * math.cos(a), h / 2 + dist * math.sin(a) * 0.55
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r.uniform(3, 16):.1f}" fill="{color}"/>')
    for _ in range(10):
        x = r.uniform(0.2, 0.8) * w
        y0 = r.uniform(0.55, 0.7) * h
        L = r.uniform(40, 160)
        out.append(f'<path d="M{x:.0f},{y0:.0f} L{x:.0f},{y0 + L:.0f}" stroke="{color}" stroke-width="{r.uniform(5, 11):.0f}" stroke-linecap="round"/>')
    return svg(w, h, "".join(out))


open(f"{OUT}/ville-loin.svg", "w").write(skyline())
open(f"{OUT}/ville-rue.svg", "w").write(street())
open(f"{OUT}/piece-5-centimes.svg", "w").write(coin())
open(f"{OUT}/eclaboussure-a.svg", "w").write(splash(seed=7))
open(f"{OUT}/eclaboussure-b.svg", "w").write(splash(seed=19))
print("decor ok")
