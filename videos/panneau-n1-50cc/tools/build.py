#!/usr/bin/env python3
"""Writes index.html and compositions/*.html for the N1 sign Reel.

Edit the SCENES table (timings, footage slots, cards) and rerun. A footage slot
becomes a <video> as soon as assets/footage/<slot>.mp4 exists; until then it is
a labelled stand-in slate.

HF_VARIANT=plain builds the version without text or music (same pictures and
timing; the Google Earth credit stays): render it, then rerun without the
variable to bring the main version back.
"""
import html
import json
import math
import os
import re
from pathlib import Path

PLAIN = os.environ.get("HF_VARIANT") == "plain"

ROOT = Path(__file__).resolve().parent.parent
FOOTAGE = ROOT / "assets" / "footage"
TOTAL = 39.0

INK = "#FAF9F5"
BOX = "rgba(20, 20, 19, 0.7)"  # #141413 at 70%
CLAY = "#D97757"
RED = "#E5484D"
BLUE = "#3E8EF7"
GREEN = "#33D17A"  # the riders' route, as the user asked

# Stand-in tint per footage slot (only used while the file is missing).
SLOTS = {
    "sign_closeup": "#24343a",
    "vespa_ride": "#3a2e24",
    "road_pov": "#22362b",
    "google_earth": "#1d2c3d",
    "fork": "#30294a",
    "police_stop": "#3f2424",
    "vespa_stop": "#3a3324",
}

# Card positions: "top" sits just under the 250 px UI band, "center" in the
# middle of the safe area (250..1520), "bottom" on the lower edge of it.
# Scene 7 plays fork_b up to frame 197 (6.567 s), the moped sign square in shot;
# scene 1 opens on that same frame, paused (assets/images/sign_still.png), so the
# loop back to the start does not show. There the real sign measures 140 px across,
# centred at (602, 896): the redrawn sign grows out of it.
SIGN_REAL = {"cx": 602, "cy": 896, "d": 140}

SCENES = [
    {
        "id": "s1-quote", "start": 0.0, "dur": 3.0,
        "shots": [("sign_still", 0.0, 3.0, 0.0)], "sign_pop": 0.8,
        # On screen from frame 0: it is the thumbnail and the loop lands on it.
        "cards": [("c1", 0.0, 3.0, "top", "« أفراد المديرية العامة للأمن الوطني كيتعداو على عباد الله »", False)],
    },
    {
        # Out of the roundabout behind the Vespa, then past the sign itself.
        "id": "s2-sign", "start": 3.0, "dur": 5.0,
        "shots": [("fork_b", 0.0, 5.0, 2.0)],
        "cards": [("c2", 0.1, 4.9, "top", "هاد العلامة [[فالطريق الوطنية 1]] كتمنع الدراجات **أقل من 50cc**", True)],
    },
    {"id": "s3-map", "start": 8.0, "dur": 7.0, "map": True},
    # Scene 4: the real fork (Rabat / Casablanca Centre sign), then the riders'
    # route from the 3D Google Earth angle; one card runs across both.
    {
        "id": "s4-fork", "start": 15.0, "dur": 2.0,
        "shots": [("fork_a", 0.0, 2.0, 7.6)],
        "cards": [("c4", 0.1, 1.9, "top", "ولكن المنع كيبدا **من العلامة**…\nماشي من مدخل الأوطوروت", True)],
    },
    {
        "id": "s4-route", "start": 17.0, "dur": 3.0, "view": "fork",
        "cards": [("c4", 0.0, 3.0, "top", "ولكن المنع كيبدا **من العلامة**…\nماشي من مدخل الأوطوروت", False)],
    },
    {
        "id": "s5-police", "start": 20.0, "dur": 5.0, "view": "police",
        "cards": [("c5", 0.0, 5.0, "center", "والناس كاتقول\n« أفراد المديرية العامة للأمن الوطني كيتعداو على عباد الله »", True)],
    },
    {
        "id": "s6-who", "start": 25.0, "dur": 12.0,
        # Google Earth; the N1 after the sign; the Vespa taking the city-centre exit.
        "shots": [("google_earth", 0.0, 6.0, 0.0), ("fork_b", 6.0, 3.0, 7.2), ("fork_a", 9.0, 3.0, 10.4)],
        "cards": [
            ("c6a", 0.0, 3.0, "top", "شكون دار المنع؟", True),
            ("c6b", 3.0, 3.0, "top", "**وزارة التجهيز** [[(المكلفة بالطرق)]] بتنسيق مع **وزارة الداخلية**", True),
            ("c6c", 6.0, 3.0, "top", "شكون كيطبقو؟ **الأمن الوطني**", True),
            ("c6d", 9.0, 3.0, "top", "البوليسي ما كيتعداش عليك… **كيدير خدمتو**", True),
        ],
    },
    {
        "id": "s7-loop", "start": 37.0, "dur": 2.0,
        "shots": [("fork_b", 0.0, 2.0, 4.6)],
        "cards": [("c7", 0.0, 2.0, "top", "ودابا ما يمكنش تقول…", True)],
    },
]

FONT_CSS = """
        @font-face {
          font-family: "Cairo";
          font-weight: 800;
          src: url("assets/fonts/cairo-arabic-800-normal.woff2") format("woff2");
          unicode-range: U+0600-06FF, U+0750-077F, U+0870-088E, U+0890-0891, U+0897-08E1, U+08E3-08FF, U+200C-200E, U+2010-2011, U+204F, U+2E41, U+FB50-FDFF, U+FE70-FE74, U+FE76-FEFC;
        }
        @font-face {
          font-family: "Cairo";
          font-weight: 800;
          src: url("assets/fonts/cairo-latin-800-normal.woff2") format("woff2");
          unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
        }"""

# The user's Google Earth screenshot (1186×2576) placed in the frame: scaled so the
# app's buttons on the right fall outside it, the sign low and the fork mid-frame.
GE = {"src": "assets/images/google_earth.jpg", "w": 1186, "h": 2576, "s": 1.047, "ox": 0, "oy": -66}


def ge_xy(x, y):
    """Screenshot pixels → frame pixels."""
    return (round(GE["s"] * x + GE["ox"], 1), round(GE["s"] * y + GE["oy"], 1))


CARD_CSS = f"""
        #root {{ position: absolute; inset: 0; overflow: hidden; background: #141413; }}
        .bg {{ position: absolute; inset: 0; }}
        .bg video, .bg .ph, .bg img.still {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
        .bg img.ge {{ position: absolute; left: {GE['ox']}px; top: {GE['oy']}px; width: {GE['w'] * GE['s']:.1f}px; height: {GE['h'] * GE['s']:.1f}px; max-width: none; }}
        .credit {{ position: absolute; left: 80px; top: 1478px; font-family: "Cairo", sans-serif; font-weight: 800; font-size: 26px; line-height: 1.3;
          color: rgba(250, 249, 245, 0.88); background: rgba(20, 20, 19, 0.6); padding: 4px 14px 6px; border-radius: 8px; direction: ltr; }}
        .ph {{ display: flex; align-items: flex-end; justify-content: center; padding-bottom: 120px;
          background-image: linear-gradient(rgba(250, 249, 245, 0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(250, 249, 245, 0.05) 1px, transparent 1px);
          background-size: 90px 90px; }}
        .ph span {{ font-family: monospace; font-size: 30px; letter-spacing: 0.08em; color: rgba(250, 249, 245, 0.45);
          border: 2px dashed rgba(250, 249, 245, 0.3); padding: 12px 22px; border-radius: 10px; }}
        .cw {{ position: absolute; left: 80px; right: 80px; display: flex; justify-content: center; }}
        .cw.top {{ top: 300px; }}
        .cw.center {{ top: 250px; bottom: 400px; align-items: center; }}
        .cw.bottom {{ bottom: 400px; }}
        .card {{ direction: rtl; font-family: "Cairo", sans-serif; font-weight: 800; font-size: 70px; line-height: 1.5;
          color: {INK}; background: {BOX}; padding: 14px 44px 22px; border-radius: 22px; text-align: center; max-width: 920px; text-wrap: balance; }}
        .hl {{ color: {CLAY}; white-space: nowrap; }}
        .nw {{ white-space: nowrap; }}
        .card.nb {{ text-wrap: wrap; font-size: 64px; }}"""


def card_html(text):
    """Escapes the copy: **words** become clay highlights, [[words]] stay on one
    line, and a newline is a line break. The words themselves are left as written."""
    out = html.escape(text, quote=False)
    out = re.sub(r"\*\*(.+?)\*\*", r'<span class="hl">\1</span>', out)
    out = re.sub(r"\[\[(.+?)\]\]", r'<span class="nw">\1</span>', out)
    return out.replace("\n", "<br />")


def credit_html(sid, start, dur, k=0):
    return (f'<div id="{sid}-credit{k}" class="credit clip" data-layout-ignore data-start="{start}" data-duration="{dur}"'
            f' data-track-index="{20 + k}">© Google Earth</div>')


def shot_html(sid, i, slot, start, dur, media_start):
    el_id = f"{sid}-shot{i}"
    if slot == "google_earth" and (ROOT / GE["src"]).exists():
        return (f'<img id="{el_id}" class="ge clip" src="{GE["src"]}" alt=""'
                f' data-start="{start}" data-duration="{dur}" data-track-index="{i + 1}" />')
    if slot == "sign_still" and (ROOT / "assets/images/sign_still.png").exists():
        return (f'<img id="{el_id}" class="still clip" src="assets/images/sign_still.png" alt=""'
                f' data-start="{start}" data-duration="{dur}" data-track-index="{i + 1}" />')
    src = FOOTAGE / f"{slot}.mp4"
    if src.exists():
        trim = f' data-media-start="{media_start}"' if media_start else ""
        return (f'<video id="{el_id}" class="clip" src="assets/footage/{slot}.mp4" data-hf-media-start-basis="local" muted playsinline'
                f' data-start="{start}" data-duration="{dur}"{trim} data-track-index="{i + 1}"></video>')
    return (f'<div id="{el_id}" class="ph clip" style="background-color: {SLOTS[slot]}"'
            f' data-start="{start}" data-duration="{dur}" data-track-index="{i + 1}"><span>{slot}</span></div>')


def cards_html(s):
    """The scene's text cards, and the pop-in tween of each that pops."""
    sid, cards, tweens = s["id"], [], []
    if PLAIN:
        return cards, tweens
    for j, (cid, start, dur, pos, text, pop) in enumerate(s["cards"]):
        nb = " nb" if cid in NO_BALANCE else ""
        cards.append(f'<div id="{sid}-{cid}" class="cw {pos} clip" data-start="{start}" data-duration="{dur}"'
                     f' data-track-index="{10 + j}"><div id="{sid}-{cid}-box" class="card{nb}" lang="ar" dir="rtl">{card_html(text)}</div></div>')
        if pop:
            tweens.append(f'tl.fromTo("#{sid}-{cid}-box", {{ opacity: 0, scale: 0.9 }},'
                          f' {{ opacity: 1, scale: 1, duration: 0.2, ease: "back.out(2)" }}, {start});')
    return cards, tweens


def scene_html(s):
    sid = s["id"]
    shots = "\n          ".join(shot_html(sid, i, *shot) for i, shot in enumerate(s["shots"]))
    cards, tweens = cards_html(s)
    if s.get("punch"):
        # Lands with the music hit: a short push-in that settles.
        tweens.append(f'tl.fromTo("#{sid}-bg", {{ scale: 1.1 }}, {{ scale: 1, duration: 0.45, ease: "power3.out" }}, 0);')
    extra_css = ""
    for i, (slot, start, dur, _) in enumerate(s["shots"]):
        if slot == "google_earth" and (ROOT / GE["src"]).exists():
            # The still screenshot drifts in slowly towards the fork, and keeps its credit.
            fx, fy = ge_xy(*ROUTE["road"][-1])
            extra_css += f"\n        #{sid}-shot{i} {{ transform-origin: {fx - GE['ox']}px {fy - GE['oy']}px; }}"
            tweens.append(f'tl.fromTo("#{sid}-shot{i}", {{ scale: 1 }}, {{ scale: 1.12, duration: {dur}, ease: "none" }}, {start});')
            cards.append(credit_html(sid, start, dur, i))
    tweens.append(f'tl.set({{}}, {{}}, {s["dur"]});')
    if s.get("sign_pop"):
        # After a pause on the real sign, the redrawn one grows out of it: it starts on
        # it at its size (the red ring is 0.967 of the drawing's box) and opens to 450 px.
        big, t = 450, s["sign_pop"]
        cx, cy = SIGN_REAL["cx"], SIGN_REAL["cy"]
        extra_css += (f"\n        #{sid}-signbig {{ position: absolute; left: {cx - big / 2}px; top: {cy - big / 2}px; width: {big}px;"
                      f" height: {big}px; opacity: 0; filter: drop-shadow(0 10px 22px rgba(0, 0, 0, 0.45)); }}")
        shots += f'\n          <img id="{sid}-signbig" src="assets/images/sign_moped.svg" alt="" />'
        tweens.append(f'tl.set("#{sid}-signbig", {{ opacity: 1, scale: {round(SIGN_REAL["d"] / 0.967 / big, 4)} }}, {t});')
        tweens.append(f'tl.to("#{sid}-signbig", {{ scale: 1, duration: 0.6, ease: "power3.inOut" }}, {t});')
    return TEMPLATE.format(
        lang="ar", fonts=FONT_CSS, css=CARD_CSS, extra_css=extra_css, sid=sid, body=f"""<div id="{sid}-bg" class="bg">
          {shots}
        </div>
        {chr(10).join('        ' + c for c in cards).lstrip()}""", script="\n        ".join(tweens))


TEMPLATE = """<!doctype html>
<html lang="{lang}">
  <head>
    <meta charset="UTF-8" />
  </head>
  <body>
    <template>
      <style>{fonts}{css}{extra_css}
      </style>

      <div id="root" data-composition-id="{sid}" data-width="1080" data-height="1920">
        {body}
      </div>

      <script>
        const tl = gsap.timeline({{ paused: true }});
        {script}
        window.__timelines["{sid}"] = tl;
      </script>
    </template>
  </body>
</html>
"""


# ---- Scene 3: the map ---------------------------------------------------------
def smooth(points, to=None):
    """A Catmull-Rom curve through screenshot points, as a cubic path in frame pixels."""
    p = [(to or ge_xy)(*q) for q in points]
    d = f"M{p[0][0]} {p[0][1]}"
    for i in range(len(p) - 1):
        p0, p1, p2 = p[max(i - 1, 0)], p[i], p[i + 1]
        p3 = p[min(i + 2, len(p) - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C {c1[0]:.1f} {c1[1]:.1f}, {c2[0]:.1f} {c2[1]:.1f}, {p2[0]} {p2[1]}"
    return d


# Points in the user's screenshot pixels. The sign is the white dot they marked at
# the roundabout's north-east exit; the fork is the interchange to the north.
# Which exit is the highway and which the city centre is a guess to confirm.
ROUTE = {
    # Up the carriageway the user drew on their close-up, then on to the interchange.
    "road": [(562, 1419), (567, 1389), (568, 1326), (568, 1263), (568, 1200), (568, 1138), (569, 1080), (571, 1010), (574, 950), (578, 880)],
    "red": [(578, 880), (597, 800), (620, 715)],
    "blue": [(565, 880), (500, 842), (440, 800)],
}
MAP = {k: smooth(v) for k, v in ROUTE.items()}
MAP["sign"] = ge_xy(*ROUTE["road"][0])

# The user's close-up of the sign (same app, about ×4.1), cleaned of their sketch
# and aligned on the wide screenshot by tools/prep_ge_zoom.py.
ZOOM_ALIGN = json.loads((ROOT / "tools" / "ge_zoom_align.json").read_text())
GE_ZOOM = {"src": "assets/images/google_earth_zoom.jpg", "w": 1186, "h": 2576}
ZB_S = GE["s"] * ZOOM_ALIGN["a"]                    # close-up px → frame px once zoomed out
ZB_X = GE["s"] * ZOOM_ALIGN["tx"] + GE["ox"]
ZB_Y = GE["s"] * ZOOM_ALIGN["ty"] + GE["oy"]
SIGN_Z = (367, 1539)                                # the circle the user drew
# The road north from the sign (where the user's white line starts), traced on the
# middle of the lane rather than on their hand line, which runs along its edge.
SKETCH_Z = [(367, 1539), (370, 1480), (371, 1420), (373, 1360), (376, 1300), (383, 1240), (383, 1180), (379, 1100),
            (378, 1030), (377, 960)]
# The scene opens on the close-up at 1.3 frame px per close-up px, sign at OPEN:
# wide enough that the app's buttons on its right edge stay out of frame.
ZOOM_K, OPEN = 1.3, (375, 1350)


def zf(x, y):
    """Close-up pixels → frame pixels while the scene is zoomed in."""
    return (round(OPEN[0] + ZOOM_K * (x - SIGN_Z[0]), 1), round(OPEN[1] + ZOOM_K * (y - SIGN_Z[1]), 1))


def zoom_out(n=30):
    """Scale and shift of the map layer, from the close-up to the full view.

    The scale moves evenly on a log scale and the sign glides from OPEN to its
    place in the wide view, with an ease in and out across the whole move."""
    s0 = ZOOM_K / ZB_S
    bx, by = ZB_S * SIGN_Z[0] + ZB_X, ZB_S * SIGN_Z[1] + ZB_Y
    out = []
    for k in range(n + 1):
        t = k / n
        u = t * t * (3 - 2 * t)
        sc = s0 ** (1 - u)
        px, py = OPEN[0] + (bx - OPEN[0]) * u, OPEN[1] + (by - OPEN[1]) * u
        out.append({"scale": round(sc, 5), "x": round(px - sc * bx, 2), "y": round(py - sc * by, 2)})
    return out

MAP_CSS = f"""
        #s3-bg {{ transform-origin: 0 0; }}
        #s3-svg {{ position: absolute; inset: 0; }}
        .lab {{ position: absolute; direction: rtl; font-family: "Cairo", sans-serif; font-weight: 800; font-size: 40px; line-height: 1.45;
          color: {INK}; background: {BOX}; padding: 6px 26px 12px; border-radius: 14px; text-align: center; }}
        /* Each label sits by the tip of its arrow: city centre up the left, highway to the right of its arrow. */
        #s3-lab-red {{ right: 80px; top: 640px; border-right: 10px solid {RED}; }}
        #s3-lab-blue {{ left: 80px; top: 565px; border-right: 10px solid {BLUE}; }}"""


def sample_path(d, n):
    """Points along an M/C/S path, evenly spaced by arc length (n segments)."""
    toks = re.findall(r"[MCS]|-?[0-9.]+", d)
    pts, i, cur, last_ctrl, segs = [], 0, None, None, []
    while i < len(toks):
        cmd = toks[i]; i += 1
        nums = []
        while i < len(toks) and toks[i] not in "MCS":
            nums.append(float(toks[i])); i += 1
        xy = list(zip(nums[0::2], nums[1::2]))
        if cmd == "M":
            cur = xy[0]
        elif cmd == "C":
            for k in range(0, len(xy), 3):
                c1, c2, end = xy[k:k + 3]
                segs.append((cur, c1, c2, end)); cur, last_ctrl = end, c2
        elif cmd == "S":
            for k in range(0, len(xy), 2):
                c2, end = xy[k:k + 2]
                c1 = (2 * cur[0] - last_ctrl[0], 2 * cur[1] - last_ctrl[1])
                segs.append((cur, c1, c2, end)); cur, last_ctrl = end, c2
    dense = []
    for p0, p1, p2, p3 in segs:
        for k in range(200):
            t = k / 200
            a, b, c, e = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
            dense.append((a * p0[0] + b * p1[0] + c * p2[0] + e * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + e * p3[1]))
    dense.append(segs[-1][3])
    acc = [0.0]
    for (x0, y0), (x1, y1) in zip(dense, dense[1:]):
        acc.append(acc[-1] + ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5)
    out, j = [], 0
    for k in range(n + 1):
        target = acc[-1] * k / n
        while j < len(acc) - 2 and acc[j + 1] < target:
            j += 1
        span = (acc[j + 1] - acc[j]) or 1
        f = (target - acc[j]) / span
        (x0, y0), (x1, y1) = dense[j], dense[j + 1]
        out.append([round(x0 + (x1 - x0) * f, 1), round(y0 + (y1 - y0) * f, 1)])
    return out


def sign_badge(bid, x, y, r):
    """The N1 sign (redrawn from the user's photo) as a round map marker, soft shadow."""
    return (f'<g transform="translate({x} {y})"><g id="{bid}" opacity="0">'
            f'<circle cy="5" r="{r + 3}" fill="#141413" opacity="0.4" />'
            f'<image href="assets/images/sign_moped.svg" x="{-r - 4}" y="{-r - 4}" width="{2 * r + 8}" height="{2 * r + 8}" /></g></g>')


def map_scene():
    sx, sy = MAP["sign"]
    zx, zy = zf(*SIGN_Z)
    zw, zh = GE_ZOOM["w"] * ZB_S, GE_ZOOM["h"] * ZB_S
    css = MAP_CSS + f"""
        #s3-zoom {{ position: absolute; left: {ZB_X:.2f}px; top: {ZB_Y:.2f}px; width: {zw:.2f}px; height: {zh:.2f}px; max-width: none;
          /* Soft edges, and the app's buttons on the right edge faded out. */
          -webkit-mask-image: linear-gradient(to right, transparent 0%, #000 6%, #000 77%, transparent 85.5%),
            linear-gradient(to bottom, transparent 0%, #000 5%, #000 95%, transparent 100%);
          -webkit-mask-composite: source-in; mask-composite: intersect; }}"""
    line = lambda pid, d, color, extra="": (f'<path id="{pid}" d="{d}" pathLength="100" fill="none" stroke="{color}" stroke-width="12"'
                                            f' stroke-linecap="round" stroke-dasharray="100 120" stroke-dashoffset="110"{extra} />')
    zdir = smooth(SKETCH_Z, zf)
    vespa, ride = vespa_ride("s3-vespa", sample_path(MAP["road"], 48), 3.1, 4.5, length=72)

    def tip(tid, d, color):
        """Arrowhead at the end of a line, hidden until the line has been drawn to it."""
        (x0, y0), (x1, y1) = sample_path(d, 48)[-2:]
        ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
        return (f'<g transform="translate({x1} {y1}) rotate({ang:.1f})">'
                f'<path id="{tid}" d="M-14 -17 L 22 0 L -14 17 Z" fill="{color}" opacity="0" /></g>')
    body = f"""<div id="s3-bg" class="bg">
          {shot_html("s3", 0, "google_earth", 0.0, 7.0, 0.0)}
          <img id="s3-zoom" class="clip" src="{GE_ZOOM['src']}" alt="" data-start="0" data-duration="3.2" data-track-index="2" />
        </div>
        <svg id="s3-svg" viewBox="0 0 1080 1920" width="1080" height="1920">
          <g id="s3-zoomed">
            {line("s3-zdir-halo", zdir, "#141413", ' stroke-opacity="0.55" stroke-width="22"')}
            {line("s3-zdir", zdir, GREEN)}
            {tip("s3-zdir-tip", zdir, GREEN)}
            {sign_badge("s3-zsign", zx, zy, 52)}
          </g>
          {line("s3-road-halo", MAP["road"], "#141413", ' stroke-opacity="0.55" stroke-width="22"')}
          {line("s3-road", MAP["road"], GREEN)}
          {line("s3-red", MAP["red"], RED, ' opacity="0"')}
          {tip("s3-red-tip", MAP["red"], RED)}
          {line("s3-blue", MAP["blue"], BLUE, ' opacity="0"')}
          {tip("s3-blue-tip", MAP["blue"], BLUE)}
          {vespa}
          {sign_badge("s3-sign", sx, sy, 36)}
        </svg>
        <div id="s3-lab-red" class="lab clip" lang="ar" dir="rtl" data-start="4.7" data-duration="2.3" data-track-index="11">الطريق السيار<br />(ممنوع)</div>
        <div id="s3-lab-blue" class="lab clip" lang="ar" dir="rtl" data-start="4.85" data-duration="2.15" data-track-index="12">وسط المدينة:<br />طريق الرباط /<br />شارع مولاي إسماعيل</div>
        {credit_html("s3", 0.0, 7.0)}
        <div id="s3-c3" class="cw top clip" data-start="0.1" data-duration="6.9" data-track-index="10"><div id="s3-c3-box" class="card" lang="ar" dir="rtl">هاد المقطع عندو جوج مخارج</div></div>"""
    zoom = zoom_out()
    script = f"""// Map layer moves, computed in tools/build.py: a log-even zoom-out from the
        // close-up of the sign, then the route sampled evenly by distance, so the
        // Vespa keeps pace with the line without measuring the DOM.
        const zoomOut = {json.dumps(zoom)};
        {(chr(10) + "        ").join(ride)}
        tl.fromTo("#s3-c3-box", {{ opacity: 0, scale: 0.9 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "back.out(2)" }}, 0.1);
        // 1. On the sign: ring it, then the direction of the road, as the user sketched it.
        tl.set("#s3-bg", zoomOut[0], 0);
        tl.fromTo("#s3-zsign", {{ opacity: 0, scale: 0.4, transformOrigin: "50% 50%" }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)" }}, 0.15);
        tl.fromTo(["#s3-zdir", "#s3-zdir-halo"], {{ strokeDashoffset: 100 }}, {{ strokeDashoffset: 0, duration: 0.8, ease: "power1.inOut" }}, 0.4);
        tl.set("#s3-zdir-tip", {{ opacity: 1 }}, 1.17);
        // 2. Pull back to the whole stretch; the close-up dissolves into the wide view.
        tl.to("#s3-zoomed", {{ opacity: 0, duration: 0.2, ease: "none" }}, 1.5);
        tl.to("#s3-bg", {{ keyframes: zoomOut.slice(1).map((f) => ({{ ...f, duration: 1.6 / (zoomOut.length - 1), ease: "none" }})) }}, 1.5);
        tl.to("#s3-zoom", {{ opacity: 0, duration: 0.35, ease: "none" }}, 2.25);
        // 3. From the sign to the fork.
        tl.fromTo("#s3-sign", {{ opacity: 0, scale: 0.4, transformOrigin: "50% 50%" }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)" }}, 3.0);
        tl.fromTo(["#s3-road", "#s3-road-halo"], {{ strokeDashoffset: 100 }}, {{ strokeDashoffset: 0, duration: 1.4, ease: "none" }}, 3.1);
        // 4. The two exits.
        tl.set(["#s3-red", "#s3-blue"], {{ opacity: 1 }}, 4.5);
        tl.fromTo("#s3-red", {{ strokeDashoffset: 100 }}, {{ strokeDashoffset: 0, duration: 0.4, ease: "power2.out" }}, 4.5);
        tl.fromTo("#s3-blue", {{ strokeDashoffset: 100 }}, {{ strokeDashoffset: 0, duration: 0.45, ease: "power2.out" }}, 4.6);
        tl.set("#s3-red-tip", {{ opacity: 1 }}, 4.82);
        tl.set("#s3-blue-tip", {{ opacity: 1 }}, 4.97);
        tl.fromTo("#s3-lab-red", {{ opacity: 0, scale: 0.9 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "back.out(2)" }}, 4.7);
        tl.fromTo("#s3-lab-blue", {{ opacity: 0, scale: 0.9 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "back.out(2)" }}, 4.85);
        tl.set({{}}, {{}}, 7);"""
    if PLAIN:  # no card, no exit labels
        body = re.sub(r'\n        <div id="s3-(lab-red|lab-blue|c3)".*?</div>(</div>)?(?=\n|$)', "", body)
        script = "\n".join(l for l in script.split("\n") if not re.search(r"#s3-(lab|c3)", l))
    return TEMPLATE.format(lang="ar", fonts=FONT_CSS, css=CARD_CSS, extra_css=css, sid="s3-map", body=body, script=script)


# The user's Vespa seen from above, as drawn for their slide film (mint body, dark
# seat, headlight; no logo). 66 units long, nose towards +x, centred on its middle.
VESPA_TOP = """<g transform="translate(24 0)">
              <ellipse cx="-22" cy="3" rx="36" ry="14" fill="#000" opacity="0.35" />
              <rect x="-57" y="-9" width="12" height="18" rx="2.5" fill="#1f2a2e" stroke="#0b1012" stroke-width="1.2" />
              <path d="M -50 0 C -50 -11 -42 -12 -30 -12 L -8 -9 C -3 -9 -3 9 -8 9 L -30 12 C -42 12 -50 11 -50 0 Z" fill="#93cdbb" stroke="#0b1012" stroke-width="1.5" />
              <rect x="-41" y="-7" width="27" height="14" rx="6.5" fill="#1f2a2e" />
              <rect x="-9" y="-6" width="10" height="12" rx="2" fill="#7db3a3" stroke="#0b1012" stroke-width="1.2" />
              <path d="M 0 -12 C 6 -12 9 -6 9 0 C 9 6 6 12 0 12 Z" fill="#93cdbb" stroke="#0b1012" stroke-width="1.5" />
              <line x1="-1" y1="-16" x2="-1" y2="16" stroke="#1b2428" stroke-width="3.6" stroke-linecap="round" />
              <rect x="-4" y="-4" width="8" height="8" rx="2" fill="#93cdbb" stroke="#0b1012" stroke-width="1.2" />
              <circle cx="8" cy="0" r="2.2" fill="#fff4cf" />
            </g>"""


def vespa_ride(vid, route, t0, t1, q=1.0, length=70, depth=lambda y: 1, drop_last=0):
    """The user's Vespa seen from above riding a sampled route, nose first.

    Position and ground squash (q: 1 = straight down) go on an outer layer, the
    heading on an inner one, so the squash follows the ground, not the Vespa.
    Returns the markup and the timeline lines."""
    heads = []
    for i in range(len(route)):
        (px, py), (nx, ny) = route[max(i - 1, 0)], route[min(i + 1, len(route) - 1)]
        heads.append(math.degrees(math.atan2((ny - py) / q, nx - px)))  # heading on the ground
    for i in range(1, len(heads)):  # unwrap, so a turn never spins the long way round
        while heads[i] - heads[i - 1] > 180:
            heads[i] -= 360
        while heads[i] - heads[i - 1] < -180:
            heads[i] += 360
    k = lambda y: length / 66 * depth(y)
    move = [{"x": x, "y": y, "scaleX": round(k(y), 4), "scaleY": round(k(y) * q, 4)} for x, y in route]
    turn = [{"rotation": round(h, 1)} for h in heads]
    if drop_last:
        move, turn = move[:-drop_last], turn[:-drop_last]
    step = round((t1 - t0) / (len(route) - 1), 5)
    markup = f"""<g id="{vid}" opacity="0"><g id="{vid}-turn">
            {VESPA_TOP}
          </g></g>"""
    v = vid.replace("-", "_")
    script = [f"// The Vespa's ride, computed in tools/build.py (evenly by distance along the route).",
              f"const {v}_move = {json.dumps(move)};",
              f"const {v}_turn = {json.dumps(turn)};",
              f'tl.set("#{vid}", {{ opacity: 1, svgOrigin: "0 0", ...{v}_move[0] }}, {t0});',
              f'tl.set("#{vid}-turn", {{ transformOrigin: "50% 50%", ...{v}_turn[0] }}, {t0});',
              f'tl.to("#{vid}", {{ keyframes: {v}_move.slice(1).map((f) => ({{ ...f, duration: {step}, ease: "none" }})) }}, {t0});',
              f'tl.to("#{vid}-turn", {{ keyframes: {v}_turn.slice(1).map((f) => ({{ ...f, duration: {step}, ease: "none" }})) }}, {t0});']
    return markup, script


# ---- Scenes 4 and 5: the interchange, from the user's two angles ----------------
# Route points are in the screenshots' own pixels (1186×2576), traced on the lanes
# (the user's sketches and their Google / Apple Maps routes give the way): N1 north under the bridge, the loop's entry ramp, round
# the loop and out onto the avenue into the city centre. "place" scales and shifts a
# screenshot into the frame; s ≥ 1.05 keeps the app's buttons on the right outside.
VIEWS = {
    "fork": {
        "src": "assets/images/police_3d.jpg", "place": (1.08, -100, -110),
        # Traced lane by lane, as the navigation apps draw it: N1 eastbound under the
        # Route Al Jamiaa bridge, the exit lane along the top of the loop, the ring
        # round to its west side, then Route Al Jamiaa northbound into the city.
        "route": [(225, 1338), (330, 1328), (430, 1318), (510, 1305), (590, 1291), (700, 1287), (820, 1290), (920, 1296),
                  (975, 1305), (1010, 1325), (1027, 1365), (1022, 1415), (995, 1458), (950, 1488), (880, 1504), (790, 1512),
                  (710, 1508), (650, 1490), (618, 1458), (605, 1420), (598, 1375), (588, 1335), (570, 1305), (560, 1270),
                  (558, 1200), (560, 1100), (566, 1000), (573, 900), (578, 830)],
        "draw": (0.1, 2.8),
        # Seen in perspective: the Vespa lies flat on the ground (q) and shrinks
        # towards the horizon (depth: screenshot y → size factor).
        "vespa": {"q": 0.5, "len": 110},
        "depth": ((750, 0.55), (1505, 1.0)),
        "drift": 1.10,
    },
    "police": {
        "src": "assets/images/police_top.jpg", "place": (1.6, -194, 0),
        # N1 northbound carriageway, under the bridges, then the loop's entry ramp.
        "route": [(255, 1900), (262, 1700), (275, 1500), (290, 1300), (310, 1150), (335, 1020), (365, 940), (395, 890),
                  (420, 850), (440, 820), (459, 789)],
        "draw": (0.0, 0.5),
        "vespa": {"q": 1.0, "len": 110},
        # The ✕ (second sketch, on the loop's entry ramp).
        "stop": (459, 789),
        "punch": True,
    },
}


# Cards whose explicit line break already sets the shape: wrap them plainly, a
# touch smaller so each half holds on one line (2 lines instead of 4).
NO_BALANCE = {"c4"}


def view_scene(s):
    sid, v = s["id"], VIEWS[s["view"]]
    sc, ox, oy = v["place"]
    to = lambda x, y: (round(sc * x + ox, 1), round(sc * y + oy, 1))
    d = smooth(v["route"], to)
    route = sample_path(d, 48)
    t0, t1 = v["draw"]
    if "depth" in v:
        (ya, ka), (yb, kb) = v["depth"]
        depth = lambda y: round(ka + (kb - ka) * min(max((y / sc - oy / sc - ya) / (yb - ya), 0), 1), 3)
    else:
        depth = lambda y: 1
    (ex0, ey0), (ex1, ey1) = route[-2:]
    ang = math.degrees(math.atan2(ey1 - ey0, ex1 - ex0))
    stop = to(*v["stop"]) if "stop" in v else None
    # With a stop, the Vespa pulls up just short of the police.
    vespa, ride = vespa_ride(f"{sid}-vespa", route, t0, t1, q=v["vespa"]["q"], length=v["vespa"]["len"],
                             depth=depth, drop_last=3 if stop else 0)

    css = f"""
        #{sid}-img {{ position: absolute; left: {ox}px; top: {oy}px; width: {1186 * sc:.1f}px; height: {2576 * sc:.1f}px; max-width: none; }}
        #{sid}-bg {{ transform-origin: {stop[0] if stop else 600}px {stop[1] if stop else 1300}px; }}
        #{sid}-svg {{ position: absolute; inset: 0; }}"""
    stroke = lambda pid, color, extra="": (f'<path id="{pid}" d="{d}" pathLength="100" fill="none" stroke="{color}" stroke-width="12"'
                                           f' stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="100 120" stroke-dashoffset="110"{extra} />')
    police = ""
    if stop:
        # Police lights: two rings flashing red and blue, round a dark stop badge.
        police = f"""<g transform="translate({stop[0]} {stop[1]})"><g id="{sid}-police">
            <circle id="{sid}-ring-red" r="62" fill="none" stroke="{RED}" stroke-width="10" opacity="0" />
            <circle id="{sid}-ring-blue" r="88" fill="none" stroke="{BLUE}" stroke-width="10" opacity="0" />
            <circle r="38" fill="#141413" fill-opacity="0.85" stroke="{INK}" stroke-width="5" />
            <path d="M-12 -29 L12 -29 L29 -12 L29 12 L12 29 L-12 29 L-29 12 L-29 -12 Z" fill="{RED}" />
            <rect x="-17" y="-5" width="34" height="10" rx="2" fill="{INK}" />
          </g></g>"""
    cards, tweens = cards_html(s)
    cards.append(credit_html(sid, 0.0, s["dur"]))
    body = f"""<div id="{sid}-bg" class="bg">
          <img id="{sid}-img" class="clip" src="{v['src']}" alt="" data-start="0" data-duration="{s['dur']}" data-track-index="1" />
          <svg id="{sid}-svg" viewBox="0 0 1080 1920" width="1080" height="1920">
          {stroke(f"{sid}-route-halo", "#141413", ' stroke-opacity="0.55" stroke-width="22"')}
          {stroke(f"{sid}-route", GREEN)}
          {"" if stop else f'<g transform="translate({ex1} {ey1}) rotate({ang:.1f})"><path id="{sid}-tip" d="M-14 -17 L 22 0 L -14 17 Z" fill="{GREEN}" opacity="0" /></g>'}
          {police}
          {vespa}
          </svg>
        </div>
        {chr(10).join('        ' + c for c in cards).lstrip()}"""
    script = ride + [f'tl.fromTo(["#{sid}-route", "#{sid}-route-halo"], {{ strokeDashoffset: 100 }}, {{ strokeDashoffset: 0, duration: {t1 - t0}, ease: "{"none" if t1 - t0 > 1 else "power2.out"}" }}, {t0});']
    if not stop:
        script.append(f'tl.set("#{sid}-tip", {{ opacity: 1 }}, {round(t1 - 0.03, 2)});')
    if v.get("drift"):
        script.append(f'tl.fromTo("#{sid}-bg", {{ scale: 1 }}, {{ scale: {v["drift"]}, duration: {s["dur"]}, ease: "none" }}, 0);')
    if v.get("punch"):
        # Lands with the music hit: a push-in that settles on the stop.
        script.append(f'tl.fromTo("#{sid}-bg", {{ scale: 1.12 }}, {{ scale: 1, duration: 0.5, ease: "power3.out" }}, 0);')
    if stop:
        script.append(f'tl.fromTo("#{sid}-police", {{ opacity: 0, scale: 1.6, transformOrigin: "50% 50%" }},'
                      f' {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)" }}, 0.05);')
        # Lights alternate four times a second for the whole scene (fixed times, seek-safe).
        flashes = [round(0.1 + 0.25 * k, 2) for k in range(int((s["dur"] - 0.1) / 0.25))]
        script.append(f"[{', '.join(map(str, flashes))}].forEach((t, k) => {{")
        script.append(f'  tl.set("#{sid}-ring-red", {{ opacity: k % 2 ? 0.25 : 1 }}, t);')
        script.append(f'  tl.set("#{sid}-ring-blue", {{ opacity: k % 2 ? 1 : 0.25 }}, t);')
        script.append("});")
    script += tweens
    script.append(f'tl.set({{}}, {{}}, {s["dur"]});')
    return TEMPLATE.format(lang="ar", fonts=FONT_CSS, css=CARD_CSS, extra_css=css, sid=sid, body=body,
                           script="\n        ".join(script))


# ---- Root -----------------------------------------------------------------------
def index_html():
    hosts = []
    for k, s in enumerate(SCENES):
        hosts.append(f"""      <div
        id="el-{s['id']}"
        data-composition-id="{s['id']}"
        data-composition-src="compositions/{s['id']}.html"
        data-start="{s['start']}"
        data-duration="{s['dur']}"
        data-track-index="{k + 1}"
        data-track-kind="graphics"
        data-width="1080"
        data-height="1920"
      ></div>""")
    music = ROOT / "assets" / "music" / "track.wav"
    audio = (f'<audio id="music" class="clip" src="assets/music/track.wav" data-start="0" data-duration="{TOTAL}" data-volume="1" data-track-index="30"></audio>'
             if music.exists() else "<!-- music: assets/music/track.wav once it is in -->")
    if PLAIN:
        audio = "<!-- plain version: no music -->"
    return f"""<!doctype html>
<html lang="ar">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="vendor/gsap.min.js"></script>
    <style>{FONT_CSS}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #141413; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: #141413; }}
      #root > div[data-composition-src] {{ position: absolute; inset: 0; }}
    </style>
  </head>
  <body>
    <!-- N1 sign Reel. Generated by tools/build.py: edit the SCENES table there. -->
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-fps="30" data-width="1080" data-height="1920">
{chr(10).join(hosts)}
      {audio}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      tl.set({{}}, {{}}, {TOTAL});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""


def main():
    (ROOT / "compositions").mkdir(exist_ok=True)
    for s in SCENES:
        out = map_scene() if s.get("map") else view_scene(s) if s.get("view") else scene_html(s)
        (ROOT / "compositions" / f"{s['id']}.html").write_text(out, encoding="utf-8")
    (ROOT / "index.html").write_text(index_html(), encoding="utf-8")
    missing = sorted({sl for s in SCENES for sl, *_ in s.get("shots", [])} | {"google_earth"})
    images = {"google_earth": ROOT / GE["src"], "sign_still": ROOT / "assets/images/sign_still.png"}
    missing = [m for m in missing if not (FOOTAGE / f"{m}.mp4").exists() and not images.get(m, FOOTAGE / "-").exists()]
    print(json.dumps({"scenes": len(SCENES), "stand_ins": missing}))


if __name__ == "__main__":
    main()
