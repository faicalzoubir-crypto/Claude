#!/usr/bin/env python3
"""Build compositions/s2-map.html: the night map of Casablanca (scene 2).

Reads data/map.json (tools/basemap.py) and data/cues.json (scene timing; defaults if absent).
Every zone is drawn in image pixels inside #s2-cam (the camera wrapper GSAP scales); labels are
counter-scaled so they keep their screen size. Label positions are computed here (screen px at the
end framing), in callout rows over the sea (north cluster) and over the empty southern fields
(south cluster), with leader lines, so no two labels collide.

  python3 tools/s2_build.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
M = json.loads((ROOT / "data/map.json").read_text())
S_END = M["scaleEnd"]                       # image px -> screen px at the end framing
CX, CY = M["center"]["x"], M["center"]["y"]  # image px at screen (540, 960) at the end framing
ANCHOR = (540, 700)                          # the zoom holds this screen point still
ZOOM_FROM = 0.85                             # start scale as a fraction of the end scale

cues = {}
cp = ROOT / "data/cues.json"
if cp.exists():
    cues = json.loads(cp.read_text()).get("s2", {})
DUR = cues.get("duration", 40.0)
DARK_T0 = cues.get("dark_start", 1.6)        # first zone switches off
DARK_STEP = cues.get("dark_step", 1.0)
LIT_T0 = cues.get("lit_start", 24.0)         # «أما المضاءة»
LIT_STEP = cues.get("lit_step", 0.9)
OFF_T = cues.get("offframe", LIT_T0 + 5.2)

AR = {
    "centre": "وسط المدينة", "belyout": "سيدي بليوط", "anfa": "أنفا", "bourgogne": "بورغون",
    "maarif": "المعاريف", "ghallef": "درب غلف", "merssultan": "مرس السلطان", "hopitaux": "حي المستشفيات",
    "fida": "الفداء", "californie": "كاليفورنيا", "ainchock": "عين الشق", "oulfa": "الألفة",
    "cfc": "القطب المالي CFC", "hassani": "الحي الحسني", "sbata": "سباتة", "benmsick": "ابن مسيك",
    "sidiothmane": "سيدي عثمان", "sidimaarouf": "سيدي معروف", "bouskoura": "بوسكورة",
    "ainsebaa": "عين السبع", "haymohammadi": "الحي المحمدي", "sidimoumen": "سيدي مومن",
    "bernoussi": "سيدي البرنوصي", "aindiab": "عين الذئاب",
}
DARK = ["centre", "belyout", "anfa", "bourgogne", "maarif", "ghallef", "merssultan", "hopitaux", "fida",
        "californie", "ainchock", "oulfa", "cfc", "hassani", "sbata", "benmsick", "sidiothmane",
        "sidimaarouf", "bouskoura"]
LIT = ["ainsebaa", "haymohammadi", "sidimoumen", "bernoussi", "aindiab"]
# Zone radius on screen (px) at the end framing: rough extent of each neighbourhood.
R = {k: 50 for k in DARK + LIT}
R.update({"centre": 44, "belyout": 40, "bourgogne": 40, "maarif": 42, "ghallef": 36, "hopitaux": 36,
          "merssultan": 40, "anfa": 48, "hassani": 60, "bouskoura": 62, "sidimaarouf": 54, "cfc": 44,
          "californie": 48, "ainchock": 50, "oulfa": 46, "benmsick": 46, "sbata": 46, "sidiothmane": 46,
          "fida": 42, "aindiab": 56, "bernoussi": 66, "sidimoumen": 62, "ainsebaa": 60,
          "haymohammadi": 54})

FONT = 30          # label size on screen
CH = 0.50          # Arabic glyph advance ≈ CH × FONT per character (IBM Plex Sans Arabic 700)


def scr(k):
    p = M["places"][k]
    return (540 + (p["x"] - CX) * S_END, 960 + (p["y"] - CY) * S_END)


def img(x, y):
    return (CX + (x - 540) / S_END, CY + (y - 960) / S_END)


def width(text):
    return len(text) * FONT * CH + 26


# --- label layout (screen px, end framing) -----------------------------------------------------
# "near": label sits next to its zone (dx, dy from the dot); "bank": a callout row with a leader.
NEAR = {
    "aindiab": (0, -58), "haymohammadi": (60, -64), "ainsebaa": (10, -66), "bernoussi": (-50, -72),
    "sidimoumen": (-10, 70), "bouskoura": (-118, 0),
    "hassani": (20, -50), "oulfa": (0, 50), "cfc": (-28, 52), "ghallef": (-20, 48), "fida": (20, -50),
    "benmsick": (0, 50), "sidiothmane": (40, -50), "californie": (0, -50), "ainchock": (0, 52),
    "sbata": (0, 52), "sidimaarouf": (-10, 52),
}
SEA_ROWS = [352, 414]            # north cluster, over the sea
FIELD_ROWS = [1000, 1062, 1124]  # south cluster, over the fields
SEA = ["anfa", "bourgogne", "maarif", "hopitaux", "centre", "belyout", "merssultan"]
FIELD = []


def bank(ids, rows, xmin, xmax, gap=14):
    ids = sorted(ids, key=lambda k: scr(k)[0])
    out = {}
    for ri, row in enumerate(rows):
        members = ids[ri::len(rows)]
        xs = [scr(k)[0] for k in members]
        ws = [width(AR[k]) for k in members]
        # sweep right, then left, to remove overlaps while staying near the dot
        for i in range(len(xs)):
            lo = xmin + ws[i] / 2 if i == 0 else xs[i - 1] + ws[i - 1] / 2 + gap + ws[i] / 2
            xs[i] = max(xs[i], lo)
        for i in range(len(xs) - 1, -1, -1):
            hi = xmax - ws[i] / 2 if i == len(xs) - 1 else xs[i + 1] - ws[i + 1] / 2 - gap - ws[i] / 2
            xs[i] = min(xs[i], hi)
        for k, x in zip(members, xs):
            out[k] = (x, row)
    return out


# Hand-placed label centres (screen px, end framing), checked against each other in snapshots.
LAB = {
    "aindiab": (153, 542), "anfa": (245, 492), "bourgogne": (340, 462), "centre": (430, 385),
    "belyout": (610, 445), "maarif": (285, 625), "merssultan": (600, 610), "hopitaux": (492, 712),
    "ghallef": (305, 690), "fida": (576, 666), "hassani": (117, 701), "oulfa": (158, 862),
    "cfc": (230, 785), "californie": (419, 906), "ainchock": (568, 931), "benmsick": (627, 833),
    "sbata": (708, 928), "sidiothmane": (765, 718), "sidimaarouf": (313, 978), "bouskoura": (186, 1330),
    "haymohammadi": (755, 544), "ainsebaa": (835, 428), "bernoussi": (955, 348), "sidimoumen": (962, 684),
}
LEADER = {k for k in DARK if ((LAB[k][0] - scr(k)[0]) ** 2 + (LAB[k][1] - scr(k)[1]) ** 2) ** 0.5 > 40}


def zone_svg(k, lit):
    x, y = img(*scr(k))
    r = R[k] / S_END
    g = []
    g.append(f'<circle id="s2-glow-{k}" class="glow" cx="{x:.1f}" cy="{y:.1f}" r="{r * (1.35 if lit else 0.95):.1f}" fill="url(#s2-warm)"/>')
    if not lit:
        g.append(f'<circle id="s2-dark-{k}" class="dark" cx="{x:.1f}" cy="{y:.1f}" r="{r * 1.45:.1f}" fill="url(#s2-black)"/>')
        g.append(f'<circle id="s2-ring-{k}" class="ring" cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.82:.1f}"/>')
    if k in LEADER:
        lx, ly = LAB[k]
        ex, ey = img(lx, ly)
        g.append(f'<line id="s2-lead-{k}" class="lead" x1="{x:.1f}" y1="{y:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" pathLength="100"/>')
    if not lit:
        g.append(f'<circle id="s2-pin-{k}" class="pin" cx="{x:.1f}" cy="{y:.1f}" r="{3.2 / S_END:.1f}"/>')
    return "\n        ".join(g)


def label_html(k, lit):
    x, y = img(*LAB[k])
    cls = "lab lit" if lit else "lab"
    return (f'<div class="labpos" style="left:{x:.1f}px;top:{y:.1f}px">'
            f'<div id="s2-lab-{k}" class="{cls}">{AR[k]}</div></div>')


zones = "\n        ".join(zone_svg(k, k in LIT) for k in DARK + LIT)
labels = "\n      ".join(label_html(k, k in LIT) for k in DARK + LIT)

# camera: GSAP sets x, y, scale on #s2-cam (transform-origin 0 0)
ax, ay = ANCHOR
pa = ((ax - 540) / S_END + CX, (ay - 960) / S_END + CY)   # image point under the anchor
s1 = S_END
s0 = S_END * ZOOM_FROM
cam0 = dict(x=ax - pa[0] * s0, y=ay - pa[1] * s0, scale=s0)
cam1 = dict(x=ax - pa[0] * s1, y=ay - pa[1] * s1, scale=s1)

dark_times = {k: round(DARK_T0 + i * DARK_STEP, 3) for i, k in enumerate(DARK)}
_LAB_FROM = "opacity: 0, y: 12, xPercent: -50, yPercent: -50"
_LAB_TO = "opacity: 1, y: 0, xPercent: -50, yPercent: -50, duration: 0.35, ease: \"power3.out\""
lit_times = {k: round(LIT_T0 + i * LIT_STEP, 3) for i, k in enumerate(["aindiab", "haymohammadi", "ainsebaa", "sidimoumen", "bernoussi"])}
_z = []
for k, t in dark_times.items():
    _z += [f'tl.to("#s2-glow-{k}", {{ opacity: 0.12, duration: 0.06 }}, {t});',
           f'tl.to("#s2-glow-{k}", {{ opacity: 0.5, duration: 0.06 }}, {t + 0.08:.3f});',
           f'tl.to("#s2-glow-{k}", {{ opacity: 0.05, duration: 0.05 }}, {t + 0.18:.3f});',
           f'tl.to("#s2-glow-{k}", {{ opacity: 0.3, duration: 0.05 }}, {t + 0.25:.3f});',
           f'tl.to("#s2-glow-{k}", {{ opacity: 0, duration: 0.12 }}, {t + 0.32:.3f});',
           f'tl.to("#s2-dark-{k}", {{ opacity: 1, duration: 0.6, ease: "power2.out" }}, {t + 0.3:.3f});',
           f'tl.to("#s2-ring-{k}", {{ opacity: 1, duration: 0.5, ease: "power2.out" }}, {t + 0.45:.3f});',
           f'tl.to("#s2-pin-{k}", {{ opacity: 1, duration: 0.2 }}, {t + 0.4:.3f});']
    if k in LEADER:
        _z.append(f'tl.fromTo("#s2-lead-{k}", {{ strokeDashoffset: 110 }}, {{ strokeDashoffset: 0, duration: 0.4, ease: "power2.out" }}, {t + 0.4:.3f});')
    _z.append(f'tl.fromTo("#s2-lab-{k}", {{ {_LAB_FROM} }}, {{ {_LAB_TO} }}, {t + 0.55:.3f});')
for k, t in lit_times.items():
    _z += [f'tl.to("#s2-glow-{k}", {{ opacity: 1, duration: 0.5, ease: "power2.out" }}, {t});',
           f'tl.fromTo("#s2-lab-{k}", {{ {_LAB_FROM} }}, {{ {_LAB_TO} }}, {t + 0.15:.3f});']
zone_js = "\n".join("      " + x for x in _z)

html = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; overflow: hidden; background: #05090B; }}
    @font-face {{ font-family: "Plex Arabic"; src: url("assets/fonts/IBMPlexSansArabic-Bold.ttf"); font-weight: 700; }}
    @font-face {{ font-family: "Plex Arabic"; src: url("assets/fonts/IBMPlexSansArabic-SemiBold.ttf"); font-weight: 600; }}
    @font-face {{ font-family: "Space Grotesk"; src: url("assets/fonts/space-grotesk-latin-700-normal.woff2"); font-weight: 700; }}
    #s2-cam {{ position: absolute; left: 0; top: 0; width: {M["w"]}px; height: {M["h"]}px; transform-origin: 0 0; --s: {s0:.4f}; }}
    #s2-sat {{ position: absolute; left: 0; top: 0; width: {M["w"]}px; height: {M["h"]}px; }}
    #s2-zones {{ position: absolute; left: 0; top: 0; width: {M["w"]}px; height: {M["h"]}px; overflow: visible; }}
    #s2-zones .glow {{ mix-blend-mode: screen; opacity: 0.6; }}
    #s2-zones .dark, #s2-zones .ring, #s2-zones .pin {{ opacity: 0; }}
    #s2-zones .ring {{ fill: none; stroke: #93A4A7; stroke-opacity: 0.38; stroke-width: {1.6 / S_END:.2f}; stroke-dasharray: 3 3; }}
    #s2-zones .lead {{ stroke: #E8EEEC; stroke-opacity: 0.55; stroke-width: {1.6 / S_END:.2f}; stroke-dasharray: 100 120; stroke-dashoffset: 110; }}
    #s2-zones .pin {{ fill: #E8EEEC; }}
    .labpos {{ position: absolute; width: 0; height: 0; transform: scale(calc(1 / var(--s))); }}
    .lab {{ position: absolute; left: 0; top: 0; opacity: 0; white-space: nowrap;
      font: 700 {FONT}px/1 "Plex Arabic"; color: #E8EEEC; direction: rtl; padding: 5px 11px 8px;
      background: rgba(13, 19, 22, 0.92); border: 1.5px solid #26343B; border-radius: 10px;
      -webkit-text-stroke: 1.5px #0D1316; paint-order: stroke fill; }}
    .lab.lit {{ color: #F4A62A; border-color: rgba(244, 166, 42, 0.45); }}
    #s2-head {{ position: absolute; left: 64px; width: 700px; top: 170px; direction: rtl; text-align: right; }}
    #s2-eyebrow {{ display: flex; align-items: center; justify-content: flex-start; gap: 14px;
      font: 700 30px/1 "Plex Arabic"; color: #F4A62A; }}
    #s2-eyebrow i {{ display: block; width: 60px; height: 4px; background: #F4A62A; border-radius: 2px; }}
    #s2-title {{ margin-top: 14px; font: 700 52px/1.2 "Plex Arabic"; color: #E8EEEC; white-space: nowrap;
      -webkit-text-stroke: 2px #0D1316; paint-order: stroke fill; }}
    #s2-legend {{ position: absolute; left: 64px; right: 64px; top: 1352px; direction: rtl; }}
    .leg {{ display: flex; align-items: center; gap: 14px; font: 700 30px/1.25 "Plex Arabic"; color: #E8EEEC;
      -webkit-text-stroke: 1.5px #0D1316; paint-order: stroke fill; margin-bottom: 10px; }}
    .leg .sw {{ flex: 0 0 auto; width: 30px; height: 30px; border-radius: 50%; }}
    .leg .sw.d {{ background: radial-gradient(circle, #000 0 45%, rgba(0,0,0,0) 72%); border: 1.5px dashed rgba(147,164,167,.6); }}
    .leg .sw.l {{ background: radial-gradient(circle, #FFD27A 0 25%, rgba(244,166,42,.55) 50%, rgba(244,166,42,0) 72%); }}
    .leg.lit {{ color: #F4A62A; }}
    #s2-disc {{ font: 600 28px/1.3 "Plex Arabic"; color: #93A4A7; -webkit-text-stroke: 1.2px #0D1316; paint-order: stroke fill; }}
    #s2-credit {{ position: absolute; right: 64px; top: 1318px; font: 600 16px/1 "Space Grotesk", sans-serif; color: #93A4A7;
      background: rgba(13,19,22,.7); padding: 3px 6px; border-radius: 4px; direction: ltr; }}
    .off {{ position: absolute; display: flex; align-items: center; gap: 10px; direction: rtl; white-space: nowrap;
      font: 700 28px/1 "Plex Arabic"; color: #E8EEEC; padding: 6px 12px 8px; background: rgba(13,19,22,.82);
      border: 1.5px solid #26343B; border-radius: 10px; }}
    .off.lit {{ color: #F4A62A; border-color: rgba(244,166,42,.45); }}
    .off b {{ font: 700 26px/1 "Space Grotesk", sans-serif; }}
  </style>
  <div id="root" data-composition-id="s2" data-width="1080" data-height="1920">
    <div id="s2-cam">
      <img id="s2-sat" src="assets/map/casa-sat.jpg" alt="" />
      <svg id="s2-zones" viewBox="0 0 {M["w"]} {M["h"]}">
        <defs>
          <radialGradient id="s2-black"><stop offset="0" stop-color="#010203" stop-opacity="0.97"/><stop offset="0.6" stop-color="#02050A" stop-opacity="0.88"/><stop offset="1" stop-color="#03070A" stop-opacity="0"/></radialGradient>
          <radialGradient id="s2-warm"><stop offset="0" stop-color="#FFD27A" stop-opacity="0.85"/><stop offset="0.35" stop-color="#F4A62A" stop-opacity="0.45"/><stop offset="1" stop-color="#F4A62A" stop-opacity="0"/></radialGradient>
        </defs>
        {zones}
      </svg>
      {labels}
    </div>
    <div id="s2-head">
      <div id="s2-eyebrow"><i></i><span>الخريطة</span></div>
      <div id="s2-title">الأحياء المعنية بالانقطاع</div>
    </div>
    <div id="s2-off-west" class="off" style="left:40px;top:900px"><span>دار بوعزة · أولاد عزوز</span><b>&larr;</b></div>
    <div id="s2-off-south" class="off" style="left:620px;top:1250px"><b>&darr;</b><span>النواصر</span></div>
    <div id="s2-off-east" class="off lit" style="right:40px;top:230px"><b>&rarr;</b><span>المحمدية</span></div>
    <div id="s2-legend">
      <div id="s2-leg-dark" class="leg"><span class="sw d"></span><span>مظلمة: انقطاع ورد فالصحافة أو بلاغ الشركة</span></div>
      <div id="s2-leg-lit" class="leg lit"><span class="sw l"></span><span>«المضاءة» معناها أن التقارير لم تذكرها</span></div>
      <div id="s2-disc">مواقع الأحياء تقريبية وليست حدودا رسمية</div>
    </div>
    <div id="s2-credit" data-layout-ignore>Imagery: Esri, Maxar, Earthstar Geographics · Places: © OpenStreetMap</div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      const DUR = {DUR};
      // camera: one slow push over the whole scene
      tl.fromTo("#s2-cam", {{ x: {cam0["x"]:.2f}, y: {cam0["y"]:.2f}, scale: {cam0["scale"]:.4f}, "--s": {cam0["scale"]:.4f} }},
                {{ x: {cam1["x"]:.2f}, y: {cam1["y"]:.2f}, scale: {cam1["scale"]:.4f}, "--s": {cam1["scale"]:.4f}, duration: DUR, ease: "sine.inOut" }}, 0);
      tl.fromTo("#s2-head", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, 0.15);
      tl.fromTo("#s2-leg-dark", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4, ease: "power2.out" }}, {DARK_T0 + 0.4});
      tl.fromTo("#s2-disc", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4, ease: "power2.out" }}, {DARK_T0 + 0.8});
      tl.fromTo("#s2-leg-lit", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4, ease: "power2.out" }}, {LIT_T0});
      tl.fromTo("#s2-credit", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, 0.5);
{zone_js}
      tl.fromTo("#s2-off-west", {{ opacity: 0, x: 14 }}, {{ opacity: 1, x: 0, duration: 0.45, ease: "power3.out" }}, {OFF_T});
      tl.fromTo("#s2-off-south", {{ opacity: 0, y: -14 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }}, {OFF_T + 0.35});
      tl.fromTo("#s2-off-east", {{ opacity: 0, x: -14 }}, {{ opacity: 1, x: 0, duration: 0.45, ease: "power3.out" }}, {OFF_T + 0.7});
      window.__timelines["s2"] = tl;
    }})();
  </script>
</template>
"""
(ROOT / "compositions").mkdir(exist_ok=True)
(ROOT / "compositions/s2-map.html").write_text(html)
# night look on the satellite image: a media-treatment grade (never a CSS filter)
import subprocess
GRADE = '{"adjust":{"exposure":-0.8,"contrast":0.15,"saturation":-0.55,"temperature":-0.35},"details":{"vignette":0.3}}'
r = subprocess.run(["npx", "hyperframes", "media-treatment", "--project", str(ROOT), "--file", "compositions/s2-map.html",
                    "--selector", "#s2-sat", "--grading", GRADE, "--apply", "--json"], capture_output=True, text=True)
print("grade applied" if '"ok": true' in r.stdout else "GRADE FAILED: " + r.stdout[-400:] + r.stderr[-400:])
print("wrote compositions/s2-map.html", "dark until", max(dark_times.values()), "lit until", max(lit_times.values()))
for k in sorted(LAB, key=lambda k: LAB[k][1]):
    print(f"  {k:13s} dot {scr(k)[0]:6.0f},{scr(k)[1]:5.0f}  label {LAB[k][0]:6.0f},{LAB[k][1]:5.0f}")
