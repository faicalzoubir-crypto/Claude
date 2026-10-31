#!/usr/bin/env python3
"""Writes index.html and compositions/*.html for the N1 sign Reel.

Edit the SCENES table (timings, footage slots, cards) and rerun. A footage slot
becomes a <video> as soon as assets/footage/<slot>.mp4 exists; until then it is
a labelled stand-in slate.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FOOTAGE = ROOT / "assets" / "footage"
TOTAL = 39.0

INK = "#FAF9F5"
BOX = "rgba(20, 20, 19, 0.7)"  # #141413 at 70%
CLAY = "#D97757"
RED = "#E5484D"
BLUE = "#3E8EF7"

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
SCENES = [
    {
        "id": "s1-quote", "start": 0.0, "dur": 3.0,
        "shots": [("sign_closeup", 0.0, 3.0, 0.0)],
        # On screen from frame 0: it is the thumbnail and the loop lands on it.
        "cards": [("c1", 0.0, 3.0, "top", "« أفراد المديرية العامة للأمن الوطني كيتعداو على عباد الله »", False)],
    },
    {
        "id": "s2-sign", "start": 3.0, "dur": 5.0,
        "shots": [("vespa_ride", 0.0, 2.5, 0.0), ("road_pov", 2.5, 2.5, 0.0)],
        "cards": [("c2", 0.1, 4.9, "top", "هاد العلامة [[فالطريق الوطنية 1]] كتمنع الدراجات **أقل من 50cc**", True)],
    },
    {"id": "s3-map", "start": 8.0, "dur": 7.0, "map": True},
    {
        "id": "s4-fork", "start": 15.0, "dur": 5.0,
        "shots": [("fork", 0.0, 5.0, 0.0)],
        "cards": [("c4", 0.1, 4.9, "top", "ولكن المنع كيبدا **من العلامة**…\nماشي من مدخل الأوطوروت", True)],
    },
    {
        "id": "s5-police", "start": 20.0, "dur": 5.0, "punch": True,
        "shots": [("police_stop", 0.0, 5.0, 0.0)],
        "cards": [("c5", 0.0, 5.0, "center", "والناس كاتقول\n« أفراد المديرية العامة للأمن الوطني كيتعداو على عباد الله »", True)],
    },
    {
        "id": "s6-who", "start": 25.0, "dur": 12.0,
        "shots": [("google_earth", 0.0, 6.0, 0.0), ("road_pov", 6.0, 3.0, 2.5), ("vespa_stop", 9.0, 3.0, 0.0)],
        "cards": [
            ("c6a", 0.0, 3.0, "top", "شكون دار المنع؟", True),
            ("c6b", 3.0, 3.0, "top", "**وزارة التجهيز** [[(المكلفة بالطرق)]] بتنسيق مع **وزارة الداخلية**", True),
            ("c6c", 6.0, 3.0, "top", "شكون كيطبقو؟ **الأمن الوطني**", True),
            ("c6d", 9.0, 3.0, "top", "البوليسي ما كيتعداش عليك… **كيدير خدمتو**", True),
        ],
    },
    {
        "id": "s7-loop", "start": 37.0, "dur": 2.0,
        "shots": [("sign_closeup", 0.0, 2.0, 0.0)],
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

CARD_CSS = f"""
        #root {{ position: absolute; inset: 0; overflow: hidden; background: #141413; }}
        .bg {{ position: absolute; inset: 0; }}
        .bg video, .bg .ph {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
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
        .nw {{ white-space: nowrap; }}"""


def card_html(text):
    """Escapes the copy: **words** become clay highlights, [[words]] stay on one
    line, and a newline is a line break. The words themselves are left as written."""
    out = html.escape(text, quote=False)
    out = re.sub(r"\*\*(.+?)\*\*", r'<span class="hl">\1</span>', out)
    out = re.sub(r"\[\[(.+?)\]\]", r'<span class="nw">\1</span>', out)
    return out.replace("\n", "<br />")


def shot_html(sid, i, slot, start, dur, media_start):
    el_id = f"{sid}-shot{i}"
    src = FOOTAGE / f"{slot}.mp4"
    if src.exists():
        trim = f' data-media-start="{media_start}"' if media_start else ""
        return (f'<video id="{el_id}" class="clip" src="assets/footage/{slot}.mp4" muted playsinline'
                f' data-start="{start}" data-duration="{dur}"{trim} data-track-index="{i + 1}"></video>')
    return (f'<div id="{el_id}" class="ph clip" style="background-color: {SLOTS[slot]}"'
            f' data-start="{start}" data-duration="{dur}" data-track-index="{i + 1}"><span>{slot}</span></div>')


def scene_html(s):
    sid = s["id"]
    shots = "\n          ".join(shot_html(sid, i, *shot) for i, shot in enumerate(s["shots"]))
    cards, tweens = [], []
    for j, (cid, start, dur, pos, text, pop) in enumerate(s["cards"]):
        track = 10 + j
        cards.append(f'<div id="{sid}-{cid}" class="cw {pos} clip" data-start="{start}" data-duration="{dur}"'
                     f' data-track-index="{track}"><div id="{sid}-{cid}-box" class="card" lang="ar" dir="rtl">{card_html(text)}</div></div>')
        if pop:
            tweens.append(f'tl.fromTo("#{sid}-{cid}-box", {{ opacity: 0, scale: 0.9 }},'
                          f' {{ opacity: 1, scale: 1, duration: 0.2, ease: "back.out(2)" }}, {start});')
    if s.get("punch"):
        # Lands with the music hit: a short push-in that settles.
        tweens.append(f'tl.fromTo("#{sid}-bg", {{ scale: 1.1 }}, {{ scale: 1, duration: 0.45, ease: "power3.out" }}, 0);')
    tweens.append(f'tl.set({{}}, {{}}, {s["dur"]});')
    return TEMPLATE.format(
        lang="ar", fonts=FONT_CSS, css=CARD_CSS, extra_css="", sid=sid, body=f"""<div id="{sid}-bg" class="bg">
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
# Stand-in geometry in frame pixels. Once the Google Earth recording is in, these
# points are re-located on the real road (sign, fork, the two exits).
MAP = {
    "road": "M600 1400 C 640 1300, 560 1220, 572 1150 S 545 1090, 540 1060",
    "red": "M540 1060 C 500 1000, 420 965, 330 945",
    "blue": "M540 1060 C 600 960, 690 850, 770 790",
    "sign": (600, 1400),
}

SCOOTER = """<g id="s3-scooter-shape" transform="translate(-50 -66)" fill="{clay}" stroke="#141413" stroke-width="4" paint-order="stroke" stroke-linejoin="round">
              <circle cx="22" cy="54" r="12" />
              <circle cx="80" cy="54" r="12" />
              <path d="M6 48 C 6 36 18 30 32 30 L 54 30 C 58 30 60 36 62 42 L 68 42 L 75 15 L 69 13 L 70 7 L 86 7 L 85 12 L 80 14 L 92 50 L 72 50 C 68 42 56 42 52 50 L 36 50 C 32 40 14 40 6 48 Z" />
              <rect x="22" y="22" width="30" height="9" rx="4" />
            </g>""".format(clay=CLAY)

MAP_CSS = f"""
        #s3-bg {{ transform-origin: 600px 1400px; }}
        #s3-svg {{ position: absolute; inset: 0; }}
        .lab {{ position: absolute; direction: rtl; font-family: "Cairo", sans-serif; font-weight: 800; font-size: 46px; line-height: 1.45;
          color: {INK}; background: {BOX}; padding: 8px 30px 14px; border-radius: 16px; text-align: center; }}
        #s3-lab-red {{ left: 80px; top: 830px; border-right: 10px solid {RED}; }}
        #s3-lab-blue {{ right: 80px; top: 580px; border-right: 10px solid {BLUE}; }}
        #s3-lab-blue .nw {{ white-space: nowrap; }}"""


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


def map_scene():
    sx, sy = MAP["sign"]
    body = f"""<div id="s3-bg" class="bg">
          {shot_html("s3", 0, "google_earth", 0.0, 7.0, 0.0)}
        </div>
        <svg id="s3-svg" viewBox="0 0 1080 1920" width="1080" height="1920">
          <defs>
            <marker id="s3-head-red" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">
              <path d="M0 0 L10 5 L0 10 Z" fill="{RED}" />
            </marker>
            <marker id="s3-head-blue" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">
              <path d="M0 0 L10 5 L0 10 Z" fill="{BLUE}" />
            </marker>
          </defs>
          <circle id="s3-sign" cx="{sx}" cy="{sy}" r="22" fill="none" stroke="{CLAY}" stroke-width="8" opacity="0" />
          <path id="s3-road-halo" d="{MAP['road']}" pathLength="100" fill="none" stroke="#141413" stroke-opacity="0.55" stroke-width="22" stroke-linecap="round" stroke-dasharray="100 120" stroke-dashoffset="110" />
          <path id="s3-road" d="{MAP['road']}" pathLength="100" fill="none" stroke="{CLAY}" stroke-width="12" stroke-linecap="round" stroke-dasharray="100 120" stroke-dashoffset="110" />
          <path id="s3-red" d="{MAP['red']}" pathLength="100" fill="none" stroke="{RED}" stroke-width="12" stroke-linecap="round" stroke-dasharray="100 120" stroke-dashoffset="110" marker-end="url(#s3-head-red)" opacity="0" />
          <path id="s3-blue" d="{MAP['blue']}" pathLength="100" fill="none" stroke="{BLUE}" stroke-width="12" stroke-linecap="round" stroke-dasharray="100 120" stroke-dashoffset="110" marker-end="url(#s3-head-blue)" opacity="0" />
          <g id="s3-scooter" opacity="0">
            {SCOOTER}
          </g>
        </svg>
        <div id="s3-lab-red" class="lab clip" lang="ar" dir="rtl" data-start="4.3" data-duration="2.7" data-track-index="11">الطريق السيار (ممنوع)</div>
        <div id="s3-lab-blue" class="lab clip" lang="ar" dir="rtl" data-start="4.5" data-duration="2.5" data-track-index="12">وسط المدينة:<br /><span class="nw">طريق الرباط / شارع مولاي إسماعيل</span></div>
        <div id="s3-c3" class="cw top clip" data-start="0.1" data-duration="6.9" data-track-index="10"><div id="s3-c3-box" class="card" lang="ar" dir="rtl">هاد المقطع عندو جوج مخارج</div></div>"""
    script = f"""// Route sampled at build time (tools/build.py), evenly by distance, so the
        // scooter keeps pace with the line drawing without measuring the DOM.
        const route = {json.dumps(sample_path(MAP["road"], 48))};
        tl.fromTo("#s3-c3-box", {{ opacity: 0, scale: 0.9 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "back.out(2)" }}, 0.1);
        // Slow zoom out from the sign, then the ride along the road to the fork.
        tl.fromTo("#s3-bg", {{ scale: 1.35 }}, {{ scale: 1, duration: 1.6, ease: "power2.inOut" }}, 0);
        tl.fromTo("#s3-sign", {{ opacity: 0, attr: {{ r: 60 }} }}, {{ opacity: 1, attr: {{ r: 22 }}, duration: 0.3, ease: "power2.out" }}, 1.4);
        tl.set("#s3-scooter", {{ opacity: 1, x: route[0][0], y: route[0][1] }}, 1.6);
        tl.fromTo(["#s3-road", "#s3-road-halo"], {{ strokeDashoffset: 100 }}, {{ strokeDashoffset: 0, duration: 2.4, ease: "none" }}, 1.6);
        tl.to("#s3-scooter", {{ keyframes: route.slice(1).map(([x, y]) => ({{ x, y, duration: 2.4 / (route.length - 1), ease: "none" }})) }}, 1.6);
        // The two exits from the fork.
        tl.set(["#s3-red", "#s3-blue"], {{ opacity: 1 }}, 4.0);
        tl.fromTo("#s3-red", {{ strokeDashoffset: 100 }}, {{ strokeDashoffset: 0, duration: 0.4, ease: "power2.out" }}, 4.0);
        tl.fromTo("#s3-blue", {{ strokeDashoffset: 100 }}, {{ strokeDashoffset: 0, duration: 0.45, ease: "power2.out" }}, 4.15);
        tl.fromTo("#s3-lab-red", {{ opacity: 0, scale: 0.9 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "back.out(2)" }}, 4.3);
        tl.fromTo("#s3-lab-blue", {{ opacity: 0, scale: 0.9 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "back.out(2)" }}, 4.5);
        tl.set({{}}, {{}}, 7);"""
    return TEMPLATE.format(lang="ar", fonts=FONT_CSS, css=CARD_CSS, extra_css=MAP_CSS, sid="s3-map", body=body, script=script)


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
    mono = ROOT / "assets" / "images" / "fz_monogram.png"
    if mono.exists():
        wm = '<img id="wm" class="clip" src="assets/images/fz_monogram.png" alt="" data-start="0" data-duration="39" data-track-index="20" />'
    else:
        wm = '<div id="wm" class="clip" data-start="0" data-duration="39" data-track-index="20"><span>FZ</span></div>'
    music = ROOT / "assets" / "music" / "track.wav"
    audio = (f'<audio id="music" class="clip" src="assets/music/track.wav" data-start="0" data-duration="{TOTAL}" data-volume="1" data-track-index="30"></audio>'
             if music.exists() else "<!-- music: assets/music/track.wav once it is in -->")
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
      /* Monogram: bottom-left corner of the safe area, clear of the right-hand action rail. */
      #wm {{ position: absolute; left: 80px; top: 1400px; width: 120px; height: 120px; opacity: 0.7; z-index: 50; object-fit: contain; }}
      div#wm {{ display: flex; align-items: center; justify-content: center; border: 4px solid {INK}; border-radius: 50%;
        font-family: "Cairo", sans-serif; font-weight: 800; font-size: 44px; color: {INK}; }}
    </style>
  </head>
  <body>
    <!-- N1 sign Reel. Generated by tools/build.py: edit the SCENES table there. -->
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-fps="30" data-width="1080" data-height="1920">
{chr(10).join(hosts)}
      {wm}
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
        out = map_scene() if s.get("map") else scene_html(s)
        (ROOT / "compositions" / f"{s['id']}.html").write_text(out, encoding="utf-8")
    (ROOT / "index.html").write_text(index_html(), encoding="utf-8")
    missing = sorted({sl for s in SCENES for sl, *_ in s.get("shots", [])} | {"google_earth"})
    missing = [m for m in missing if not (FOOTAGE / f"{m}.mp4").exists()]
    print(json.dumps({"scenes": len(SCENES), "stand_ins": missing}))


if __name__ == "__main__":
    main()
