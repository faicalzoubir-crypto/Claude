#!/usr/bin/env python3
"""Build the scene files (compositions/s1, s3, s4, s5, s6, end) from data/cues.json.

Cues are scene-local phrase windows from the narration (tools/recording.py: the person's own voice);
without them every phrase is estimated from its word count, so the layout can be checked first.
No presenter: every scene is full-frame graphics in the brand look.

  python3 tools/scenes_build.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = json.loads((ROOT / "script.json").read_text())
CUES = json.loads((ROOT / "data/cues.json").read_text()) if (ROOT / "data/cues.json").exists() else {}


def estimate(scene):
    t, out = 0.45, {}
    for p in scene["phrases"]:
        d = len(p["text"].split()) / 2.25 + 0.25
        out[p["id"]] = [round(t, 3), round(t + d, 3)]
        t += d + p.get("pause", 0.5)
    return out, round(t + 0.6, 3)


def cues(sid):
    sc = next(s for s in SCRIPT["scenes"] if s["id"] == sid)
    if sid in CUES.get("scenes", {}):
        c = CUES["scenes"][sid]
        return c["phrases"], c["duration"], c.get("marks", {})
    ph, dur = estimate(sc)
    return ph, dur, {}


BASE_CSS = """
    @font-face { font-family: "Plex Arabic"; src: url("assets/fonts/IBMPlexSansArabic-Bold.ttf"); font-weight: 700; }
    @font-face { font-family: "Plex Arabic"; src: url("assets/fonts/IBMPlexSansArabic-SemiBold.ttf"); font-weight: 600; }
    @font-face { font-family: "Space Grotesk"; src: url("assets/fonts/space-grotesk-latin-700-normal.woff2"); font-weight: 700; }
    #root { position: absolute; inset: 0; overflow: hidden; background: #0D1316; direction: rtl; }
    .grid { position: absolute; inset: 0; opacity: 0.38;
      background-image: linear-gradient(#26343B 1.5px, transparent 1.5px), linear-gradient(90deg, #26343B 1.5px, transparent 1.5px);
      background-size: 60px 60px; background-position: 0 0; }
    .ink { -webkit-text-stroke: 2px #0D1316; paint-order: stroke fill; }
    .eyebrow { position: absolute; right: 64px; display: flex; align-items: center; gap: 14px;
      font: 700 32px/1 "Plex Arabic"; color: #F4A62A; white-space: nowrap; }
    .eyebrow i { display: block; width: 60px; height: 4px; background: #F4A62A; border-radius: 2px; }
    .hyp { position: absolute; right: 64px; display: flex; align-items: center; gap: 12px; white-space: nowrap;
      font: 700 34px/1 "Plex Arabic"; color: #0D1316; background: #F4A62A; padding: 10px 20px 14px; border-radius: 12px; }
    .hyp b { display: inline-block; width: 30px; height: 30px; border-radius: 50%; border: 3.5px solid #0D1316;
      font: 700 22px/23px "Space Grotesk"; text-align: center; }
    .title { position: absolute; right: 64px; left: 64px; font: 700 60px/1.18 "Plex Arabic"; color: #E8EEEC; text-align: right; }
    .card { background: #141D21; border: 1.5px solid #26343B; border-radius: 14px; }
    .lbl { position: absolute; transform: translate(50%, 0); white-space: nowrap; text-align: center;
      font: 700 34px/1.15 "Plex Arabic"; color: #E8EEEC; }
    .lbl.s { font: 600 30px/1.2 "Plex Arabic"; color: #93A4A7; }
    .tag { display: inline-block; font: 700 30px/1 "Plex Arabic"; color: #F4A62A; border: 2px solid #F4A62A;
      border-radius: 10px; padding: 6px 12px 10px; direction: rtl; background: rgba(13,19,22,.9); }
    .tag .lat { font: 700 28px/1 "Space Grotesk"; direction: ltr; unicode-bidi: isolate; }
"""


def tpl(sid, css, body, js):
    return f"""<template>
  <style>{BASE_CSS}{css}
  </style>
  <div id="root" data-composition-id="{sid}" data-width="1080" data-height="1920">
{body}
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
{js}
      window.__timelines["{sid}"] = tl;
    }})();
  </script>
</template>
"""


def T(ph, pid, frac=0.0):
    a, b = ph[pid]
    return round(a + (b - a) * frac, 3)


# ------------------------------------------------------------------------------------ drawn objects
def pylon(x, y, h=110, sc=1.0):
    w = 46 * sc
    arm = 30 * sc
    return (f'<g transform="translate({x},{y})" stroke="#93CDBB" stroke-width="{3 * min(sc, 1.4):.1f}" fill="none">'
            f'<path d="M{-w/2} {h} L-6 0 L6 0 L{w/2} {h}"/><path d="M{-arm} 14 H{arm} M{-arm*0.75} 34 H{arm*0.75}"/>'
            f'<path d="M{-w*0.38} {h*0.62} L{w*0.3} {h*0.36} M{w*0.38} {h*0.62} L{-w*0.3} {h*0.36} M{-w*0.46} {h*0.88} L{w*0.4} {h*0.62} M{w*0.46} {h*0.88} L{-w*0.4} {h*0.62}"/></g>')


def big_pylon():
    """The hero of S1: a lattice tower, base y 1230, top y 610, three crossarms."""
    L = []
    legs = "M 430 1230 L 512 640 L 568 640 L 650 1230"
    L.append(f'<path d="{legs}"/>')
    # bracing: X between the legs, ten bays
    ys = [640 + i * 59 for i in range(11)]
    def xl(y): return 512 - (y - 640) * (82 / 590)
    def xr(y): return 568 + (y - 640) * (82 / 590)
    for a, b in zip(ys[:-1], ys[1:]):
        L.append(f'<path d="M {xl(a):.1f} {a} L {xr(b):.1f} {b} M {xr(a):.1f} {a} L {xl(b):.1f} {b} M {xl(b):.1f} {b} H {xr(b):.1f}" stroke-width="2.5"/>')
    for y, half in ((660, 230), (760, 200), (860, 230)):
        L.append(f'<path d="M {540 - half} {y} H {540 + half} M {540 - half} {y} L {xl(y + 40):.1f} {y + 40} M {540 + half} {y} L {xr(y + 40):.1f} {y + 40}"/>')
        for sx in (-1, 1):
            X = 540 + sx * (half - 14)
            L.append(f'<path d="M {X} {y} V {y + 34}" stroke-width="3"/><path d="M {X - 9} {y + 12} H {X + 9} M {X - 9} {y + 21} H {X + 9} M {X - 9} {y + 30} H {X + 9}" stroke-width="2.5"/>')
    L.append('<path d="M 512 640 L 540 600 L 568 640" />')
    return '<g id="s1-pylon" stroke="#93CDBB" stroke-width="4" fill="none" stroke-linejoin="round">' + "".join(L) + "</g>"


def plant(x, y, idp):
    return (f'<g transform="translate({x},{y})"><g id="{idp}" stroke="#93CDBB" stroke-width="3.5" fill="#141D21" stroke-linejoin="round">'
            f'<path d="M-70 90 V40 L-40 20 V40 L-10 20 V40 L20 20 V90 Z"/>'
            f'<path d="M30 90 C36 60 34 30 26 4 H66 C58 30 56 60 62 90 Z"/>'
            f'<path d="M40 -4 c-8 -10 8 -16 0 -28 M54 -4 c-8 -10 8 -16 0 -28" fill="none" stroke="#93A4A7" stroke-width="3" stroke-linecap="round"/>'
            f'<path d="M-58 62 h12 M-30 62 h12 M-2 62 h12" stroke-width="5"/></g></g>')


def substation(x, y, idp):
    return (f'<g transform="translate({x},{y})"><g id="{idp}">'
            f'<rect x="-120" y="0" width="240" height="130" rx="8" fill="#141D21" stroke="#26343B" stroke-width="2"/>'
            f'<path d="M-120 0 V130 H120 V0" fill="none" stroke="#93A4A7" stroke-width="2" stroke-dasharray="2 9"/>'
            f'<g stroke="#93CDBB" stroke-width="3.5" fill="#0D1316" stroke-linejoin="round">'
            f'<rect x="-50" y="42" width="100" height="70" rx="5"/>'
            f'<path d="M-40 42 V112 M-26 42 V112 M26 42 V112 M40 42 V112" stroke-width="2.5"/>'
            f'<rect x="-32" y="20" width="12" height="22" rx="3"/><rect x="-6" y="16" width="12" height="26" rx="3"/><rect x="20" y="20" width="12" height="22" rx="3"/>'
            f'<path d="M-98 114 V64 H-72 V114 M72 114 V64 H98 V114" fill="none"/></g>'
            f'<circle id="{idp}-led" cx="0" cy="77" r="10" fill="#F4A62A"/></g></g>')


def houses(cx, y, idp, n=3, gap=96, cls=None):
    cls = cls or f"{idp}-win"
    out = [f'<g id="{idp}">']
    for i in range(n):
        x = cx + (i - (n - 1) / 2) * gap
        out.append(f'<g transform="translate({x:.0f},{y})"><path d="M-36 60 V22 L0 -6 L36 22 V60 Z" fill="#141D21" stroke="#93CDBB" stroke-width="3" stroke-linejoin="round"/>'
                   f'<rect class="{cls}" x="-22" y="26" width="16" height="14" rx="2" fill="#F4A62A"/>'
                   f'<rect class="{cls}" x="6" y="26" width="16" height="14" rx="2" fill="#F4A62A"/></g>')
    out.append("</g>")
    return "".join(out)


def skyline():
    """S1: the city at the foot of the tower, windows lit (y 1250–1450)."""
    blds = [(64, 130), (150, 190), (238, 110), (300, 230), (392, 150), (470, 120), (560, 260), (650, 170),
            (735, 210), (820, 140), (895, 240), (975, 160)]
    out = ['<g id="s1-city">']
    k = 0
    for i, (x, h) in enumerate(blds):
        w = 70 if i % 3 else 82
        top = 1450 - h
        out.append(f'<rect x="{x}" y="{top}" width="{w}" height="{h}" fill="#141D21" stroke="#93CDBB" stroke-width="2.5"/>')
        for r in range(int((h - 24) // 34)):
            for c in range(2):
                k += 1
                out.append(f'<rect class="s1-win" data-k="{k}" x="{x + 14 + c * (w - 42)}" y="{top + 16 + r * 34}" width="14" height="16" rx="2" fill="#F4A62A"/>')
    out.append('<path d="M 40 1450 H 1040" stroke="#26343B" stroke-width="3"/></g>')
    return "".join(out)


# ------------------------------------------------------------------------------------------- S1
def s1():
    ph, dur, mk = cues("s1")
    t_time = mk.get("time_word", T(ph, "s1a", 0.72))
    css = """
    #s1-date { top: 178px; }
    #s1-title { top: 228px; font-size: 64px; }
    #s1-clock { position: absolute; left: 0; right: 0; top: 322px; text-align: center; direction: ltr;
      font: 700 138px/1 "Space Grotesk"; color: #F4A62A; letter-spacing: -0.02em; }
    #s1-fault { position: absolute; left: 0; right: 0; top: 482px; text-align: center; font: 700 34px/1 "Plex Arabic"; color: #E8EEEC; }
    #s1-svg { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; overflow: visible; }
    .wx { position: absolute; display: flex; align-items: center; gap: 12px; white-space: nowrap; }
    .wx span { font: 700 34px/1.1 "Plex Arabic"; color: #E8EEEC; }
    #s1-wind { left: 64px; top: 1000px; } #s1-storm { right: 64px; top: 1000px; }
    #s1-flash { position: absolute; inset: 0; background: #E8EEEC; opacity: 0; pointer-events: none; }
    .s1-wd { stroke: #93A4A7; stroke-width: 3; stroke-linecap: round; opacity: 0; }
    #s1-bolt { opacity: 0; }
"""
    wires = []
    for i, (y, half) in enumerate(((694, 216), (794, 186), (894, 216))):
        for sx, edge in ((-1, -20), (1, 1100)):
            X = 540 + sx * half
            wires.append(f'<path class="s1-wire" d="M {X} {y} Q {(X + edge) / 2:.0f} {y + 70} {edge} {y + 20}" fill="none" stroke="#93CDBB" stroke-width="3"/>')
    winds = "".join(f'<path class="s1-wd" id="s1-wd{i}" d="M {980 - (i % 2) * 60} {600 + i * 70} H {840 - (i % 2) * 60}"/>' for i in range(6))
    body = f"""    <div class="grid"></div>
    <svg id="s1-svg" viewBox="0 0 1080 1920">
      <g id="s1-cloud" transform="translate(880,590)">
        <path d="M-120 60 a46 46 0 0 1 14 -88 a66 66 0 0 1 122 14 a42 42 0 0 1 10 80 Z" fill="#141D21" stroke="#93A4A7" stroke-width="4" stroke-linejoin="round"/>
        <path id="s1-bolt" d="M-10 60 L-38 120 H-8 L-26 176 L30 98 H0 L18 60 Z" fill="#E8EEEC"/>
      </g>
      {winds}
      {''.join(wires)}
      {big_pylon()}
      {skyline()}
    </svg>
    <div id="s1-flash"></div>
    <div id="s1-date" class="eyebrow"><i></i><span>الأربعاء 11 نونبر 2026</span></div>
    <div id="s1-title" class="title ink">انقطاع الكهرباء بالدار البيضاء</div>
    <div id="s1-clock" class="ink">16:48</div>
    <div id="s1-fault" class="ink">عطل فخطوط الجهد العالي جدا</div>
    <div id="s1-wind" class="wx"><svg width="84" height="64" viewBox="0 0 120 90" fill="none" stroke="#93CDBB" stroke-width="8" stroke-linecap="round"><path d="M8 28 H78 a14 14 0 1 0 -14 -14"/><path d="M8 50 H96 a14 14 0 1 1 -14 14"/><path d="M20 72 H60"/></svg><span>رياح قوية</span></div>
    <div id="s1-storm" class="wx"><svg width="70" height="64" viewBox="0 0 90 90"><path d="M52 4 L22 50 H42 L32 86 L70 34 H48 L60 4 Z" fill="#E8EEEC"/></svg><span>عواصف رعدية</span></div>"""
    f = T(ph, "s1c", 0.78)
    off = T(ph, "s1d", 0.3)
    js = f"""
      tl.fromTo("#s1-date", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, 0);
      tl.fromTo("#s1-title", {{ opacity: 0, y: 18 }}, {{ opacity: 1, y: 0, duration: 0.55, ease: "power3.out" }}, 0);
      tl.fromTo("#s1-clock", {{ opacity: 0, scale: 0.86 }}, {{ opacity: 1, scale: 1, duration: 0.42, ease: "back.out(1.6)" }}, {t_time - 0.12});
      tl.fromTo("#s1-fault", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }}, {T(ph, "s1b", 0.25)});
      // the line in the storm: wind, a wire sway, one lightning strike
      tl.fromTo("#s1-wind", {{ opacity: 0, x: 24 }}, {{ opacity: 1, x: 0, duration: 0.5, ease: "power3.out" }}, {T(ph, "s1c", 0.05)});
      gsap.utils.toArray("#s1-svg .s1-wd").forEach((w, i) => {{
        tl.fromTo(w, {{ x: 100, opacity: 0 }}, {{ x: -900, opacity: 0.7, duration: 1.5, ease: "none", repeat: {max(1, int((dur - T(ph, "s1c")) / 1.5))} }}, {T(ph, "s1c", 0.05)} + i * 0.22);
      }});
      tl.fromTo(".s1-wire", {{ y: 0 }}, {{ y: 10, duration: 0.7, ease: "sine.inOut", yoyo: true, repeat: {max(1, int((dur - T(ph, "s1c")) / 0.7))}, stagger: 0.08 }}, {T(ph, "s1c", 0.05)});
      tl.fromTo("#s1-storm", {{ opacity: 0, x: -24 }}, {{ opacity: 1, x: 0, duration: 0.5, ease: "power3.out" }}, {T(ph, "s1c", 0.45)});
      tl.set("#s1-flash", {{ opacity: 0.16 }}, {f}); tl.set("#s1-flash", {{ opacity: 0 }}, {f + 0.067});
      tl.set("#s1-flash", {{ opacity: 0.09 }}, {f + 0.167}); tl.set("#s1-flash", {{ opacity: 0 }}, {f + 0.233});
      tl.set("#s1-bolt", {{ opacity: 1 }}, {f}); tl.to("#s1-bolt", {{ opacity: 0, duration: 0.4 }}, {f + 0.3});
      // «انقطع الضو»: the windows go out in a sweep with a flicker
      const wins = gsap.utils.toArray("#s1-svg .s1-win");
      wins.forEach((w, i) => {{
        const k = Number(w.dataset.k), t = {off} + ((k * 37) % 23) * 0.045;
        tl.to(w, {{ opacity: 0.25, duration: 0.04 }}, t);
        tl.to(w, {{ opacity: 0.9, duration: 0.04 }}, t + 0.07);
        tl.to(w, {{ opacity: 0.06, duration: 0.12 }}, t + 0.14);
      }});"""
    return tpl("s1", css, body, js), dur


# ------------------------------------------------------------------------------------------- S3
CHECK = '<svg width="{s}" height="{s}" viewBox="0 0 34 34" fill="none"><circle cx="17" cy="17" r="15" stroke="{c}" stroke-width="3"/><path d="M10 17.5 L15 22 L24 12" stroke="{c}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
DOC = '<svg width="{w}" height="{h}" viewBox="0 0 64 76" fill="none" stroke="#93CDBB" stroke-width="4" stroke-linejoin="round"><path d="M6 4 H42 L58 20 V72 H6 Z"/><path d="M42 4 V20 H58"/><path d="M16 36 H48 M16 48 H48 M16 60 H36" stroke-linecap="round"/></svg>'
RG = json.loads((ROOT / "data/region.json").read_text())
GRADE = '{"adjust":{"exposure":-0.8,"contrast":0.15,"saturation":-0.55,"temperature":-0.35},"details":{"vignette":0.3}}'


def scr(p):
    s, c = RG["scale"], RG["center"]
    return (540 + (p[0] - c["x"]) * s, 960 + (p[1] - c["y"]) * s)


def pts(seg, rev=False):
    q = [scr(p) for p in RG["segs"][seg]["pts"]]
    return q[::-1] if rev else q


def d_of(q):
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in q)


def mid(q):
    return q[len(q) // 2]


SUBXY = {k: scr(v["px"]) for k, v in RG["subs"].items()}
# flows run from the sources (Mediouna, Laawamer) towards the two substations
FLOWS = {"x-med": True, "oh-x": True, "j-aw": True, "db-j": False, "j-os": False, "oh-db": False}
CHAIN = ["x-med", "oh-x", "x-ne", "oh-db", "db-j", "j-os", "j-aw"]


def region_layer(p):
    """Satellite (night grade) + the 225 kV chain from OpenStreetMap, in screen px."""
    s, c = RG["scale"], RG["center"]
    img = (f'<img id="{p}-sat" src="assets/map/casa-region.jpg" alt="" style="position:absolute;'
           f'left:{540 - c["x"] * s:.1f}px;top:{960 - c["y"] * s:.1f}px;width:{RG["w"] * s:.1f}px;height:{RG["h"] * s:.1f}px"/>')
    city = "".join(f'<circle class="{p}-dk" cx="{scr(xy)[0]:.1f}" cy="{scr(xy)[1]:.1f}" r="30" fill="url(#{p}-black)"/>' for xy in RG["dark"].values())
    lines = (f'<path id="{p}-l-jorf" class="l4" d="{d_of(pts("jorf-med"))}" pathLength="100"/>'
             f'<path id="{p}-l-awj" class="l2" d="{d_of(pts("aw-jorf"))}" pathLength="100"/>'
             + "".join(f'<path id="{p}-l-{k}" class="ln{" ne" if k == "x-ne" else ""}" d="{d_of(pts(k))}" pathLength="100"/>' for k in CHAIN)
             + "".join(f'<path id="{p}-f-{k}" class="fl" d="{d_of(pts(k, rev))}"/>' for k, rev in FLOWS.items()))
    marks = "".join(
        f'<g id="{p}-m-{k}" class="mk"><rect x="{x - 13:.1f}" y="{y - 13:.1f}" width="26" height="26" rx="5" '
        f'fill="{"#F4A62A" if k in ("oh", "db") else "#141D21"}" stroke="{"#F4A62A" if k in ("oh", "db") else "#93CDBB"}" stroke-width="4"/></g>'
        for k, (x, y) in SUBXY.items())
    svg = (f'<svg id="{p}-svg" viewBox="0 0 1080 1920" style="position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:visible">'
           f'<defs><radialGradient id="{p}-black"><stop offset="0" stop-color="#010203" stop-opacity="0.95"/><stop offset="0.6" stop-color="#02050A" stop-opacity="0.8"/><stop offset="1" stop-color="#02050A" stop-opacity="0"/></radialGradient></defs>'
           f'{city}{lines}{marks}</svg>')
    return img + svg


REGION_CSS = """
    .ln { fill: none; stroke: #93CDBB; stroke-width: 5; stroke-linecap: round; stroke-linejoin: round; }
    .ln.ne { stroke-width: 3.5; stroke-opacity: 0.7; }
    .l4 { fill: none; stroke: #E8EEEC; stroke-width: 4; stroke-opacity: 0.8; stroke-linejoin: round; }
    .l2 { fill: none; stroke: #93A4A7; stroke-width: 3.5; stroke-opacity: 0.8; stroke-linejoin: round; }
    .fl { fill: none; stroke: #F4A62A; stroke-width: 5; stroke-linecap: round; stroke-dasharray: 9 17; opacity: 0; }
    .nm { position: absolute; padding: 6px 12px 9px; background: rgba(13,19,22,.9); border: 1.5px solid #26343B; border-radius: 10px; opacity: 0; white-space: nowrap; }
    .nm b { display: block; font: 700 32px/1.1 "Plex Arabic"; color: #E8EEEC; }
    .nm i { display: block; font: 600 28px/1.2 "Plex Arabic"; font-style: normal; color: #93A4A7; }
    .nm.sub { border-color: rgba(244,166,42,.6); } .nm.sub b { color: #F4A62A; }
    .km { position: absolute; font: 700 28px/1 "Plex Arabic"; color: #E8EEEC; background: rgba(13,19,22,.85); padding: 4px 8px 7px; border-radius: 8px; opacity: 0; white-space: nowrap; }
    .src { position: absolute; font: 700 28px/1.2 "Plex Arabic"; color: #F4A62A; opacity: 0; white-space: nowrap;
      background: rgba(13,19,22,.88); padding: 4px 10px 8px; border-radius: 8px; }
    .cav { position: absolute; left: 64px; right: 64px; font: 600 28px/1.3 "Plex Arabic"; color: #93A4A7; text-align: right; opacity: 0;
      background: rgba(13,19,22,.86); padding: 6px 12px 10px; border-radius: 10px; }
    .cav .lat, .nm .lat { font-family: "Space Grotesk"; direction: ltr; unicode-bidi: isolate; }
    .s3-dk, .s5-dk { opacity: 0; }
    .credit { position: absolute; right: 64px; top: 1448px; font: 600 16px/1 "Space Grotesk", sans-serif; color: #93A4A7; background: rgba(13,19,22,.7); padding: 3px 6px; border-radius: 4px; direction: ltr; }
"""


def name_chip(p, k, name, sub, x, y, align="r"):
    cls = "nm sub" if k in ("oh", "db") else "nm"
    pos = f"left:{x}px;" if align == "l" else f"right:{1080 - x}px;"
    return f'<div id="{p}-n-{k}" class="{cls}" style="{pos}top:{y}px"><b>{name}</b><i>{sub}</i></div>'


def s3():
    """The 225 kV artery on the real map (OpenStreetMap substations and line routes)."""
    ph, dur, mk = cues("s3")
    p = "s3"
    km = RG["segs"]
    css = REGION_CSS + """
    #s3-eyebrow { top: 178px; } #s3-title { top: 224px; font-size: 54px; }
    #s3-svg .ln, #s3-svg .l4, #s3-svg .l2 { stroke-dasharray: 100 120; stroke-dashoffset: 110; }
    #s3-svg .mk { opacity: 0; }
    #s3-roles { position: absolute; right: 64px; left: 64px; top: 1250px; display: flex; gap: 12px; justify-content: flex-start; opacity: 0; }
    #s3-roles span { font: 700 28px/1 "Plex Arabic"; color: #E8EEEC; background: rgba(13,19,22,.9); border: 1.5px solid #26343B; border-radius: 10px; padding: 8px 12px 12px; }
    #s3-roles span em { font-style: normal; color: #93CDBB; }
"""
    L = SUBXY
    chips = "".join([
        name_chip(p, "oh", "أولاد حدو", "225 ك.ف · عين الشق", int(L["oh"][0]) + 18, int(L["oh"][1]) - 104, "l"),
        name_chip(p, "db", "دار بوعزة", "225 ك.ف · الحي الحسني", int(L["db"][0]) - 18, int(L["db"][1]) - 104),
        name_chip(p, "med", "مديونة", "400/225 ك.ف", int(L["med"][0]) - 26, int(L["med"][1]) - 104),
        name_chip(p, "os", "أولاد صالح", "225 ك.ف", int(L["os"][0]) + 22, int(L["os"][1]) - 10, "l"),
        name_chip(p, "aw", "العوامر", "225/60 ك.ف", int(L["aw"][0]) + 22, int(L["aw"][1]) + 6, "l"),
    ])
    m = lambda seg: mid(pts(seg))
    kms = (f'<div id="s3-k1" class="km" style="left:{m("oh-x")[0] - 40:.0f}px;top:{m("oh-x")[1] + 14:.0f}px">{km["oh-x"]["km"] + km["x-med"]["km"]:.0f} كلم</div>'
           f'<div id="s3-k2" class="km" style="left:{m("oh-db")[0] + 16:.0f}px;top:{m("oh-db")[1] - 6:.0f}px">{km["oh-db"]["km"]:.0f} كلم</div>'
           f'<div id="s3-k3" class="km" style="right:{1080 - m("db-j")[0] + 14:.0f}px;top:{m("db-j")[1] + 40:.0f}px">{km["db-j"]["km"] + km["j-os"]["km"]:.0f} كلم</div>'
           f'<div id="s3-k4" class="km" style="right:{1080 - m("j-aw")[0] + 30:.0f}px;top:{m("j-aw")[1] - 30:.0f}px">{km["j-aw"]["km"] + km["j-os"]["km"]:.0f} كلم</div>')
    srcs = (f'<div id="s3-fromm" class="src" style="right:{1080 - int(L["med"][0]) + 30}px;top:{int(L["med"][1]) + 26}px">من جهة مديونة ←</div>'
            f'<div id="s3-froma" class="src" style="left:{int(L["aw"][0]) + 22}px;top:{int(L["aw"][1]) + 96}px">→ من جهة العوامر</div>'
            f'<div id="s3-le" class="src" style="left:{int(L["oh"][0]) + 18}px;top:{int(L["oh"][1]) - 152}px">حسب <span style="font-family:Space Grotesk">Le360</span></div>')
    j4 = pts("jorf-med"); lab4 = next(q for q in j4[::-1] if q[1] > 1180)
    body = f"""    <div class="grid"></div>
    {region_layer(p)}
    <div id="s3-eyebrow" class="eyebrow"><i></i><span>الشبكة على الخريطة</span></div>
    <div id="s3-title" class="title ink">منين كيجي الضو للمحطتين؟</div>
    {chips}{kms}{srcs}
    <div id="s3-l400" class="km" style="right:{1080 - lab4[0] + 16:.0f}px;top:{lab4[1] - 50:.0f}px">400 ك.ف من الجرف الأصفر</div>
    <div id="s3-l225" class="km" style="left:64px;top:{scr(RG['segs']['aw-jorf']['pts'][len(RG['segs']['aw-jorf']['pts']) // 3])[1] + 30:.0f}px">← 225 ك.ف نحو الجرف الأصفر</div>
    <div id="s3-roles"><span><em>المكتب الوطني</em>: النقل بالتوتر العالي</span><span><em>الشركة الجهوية</em>: التوزيع</span></div>
    <div id="s3-cav" class="cav" style="top:1318px">المواقع ومسارات الخطوط: <span class="lat">OpenStreetMap</span> (قد ما تكونش محيّنة) · + خط 400 ك.ف من الشماعية (آسفي) منذ يونيو 2026 حسب <span class="lat">Médias24</span>، ما مرسومش</div>
    <div class="credit" data-layout-ignore>Imagery: Esri, Maxar, Earthstar Geographics · Grid: © OpenStreetMap</div>"""
    draw = lambda ids, t, dd=0.7, st=0.15: f'tl.to("{", ".join("#s3-l-" + i for i in ids)}", {{ strokeDashoffset: 0, duration: {dd}, stagger: {st}, ease: "power2.inOut" }}, {t:.3f});'
    tE = T(ph, "s3e", 0.25)
    tF = T(ph, "s3f", 0.1)
    js = f"""
      tl.fromTo("#s3-eyebrow, #s3-title", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.5, stagger: 0.1, ease: "power3.out" }}, 0);
      // the two substations named by Le360
      tl.to("#s3-m-oh, #s3-m-db", {{ opacity: 1, duration: 0.3, stagger: 0.12 }}, {T(ph, "s3a", 0.4)});
      tl.fromTo("#s3-n-oh, #s3-n-db", {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: 0.4, stagger: 0.15, ease: "power3.out" }}, {T(ph, "s3a", 0.45)});
      tl.fromTo("#s3-le", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, {T(ph, "s3a", 0.05)});
      tl.to("#s3-le", {{ opacity: 0, duration: 0.3 }}, {T(ph, "s3c", 0.0)});
      tl.fromTo("#s3-m-oh rect, #s3-m-db rect", {{ scale: 1, transformOrigin: "50% 50%" }}, {{ scale: 1.5, duration: 0.2, yoyo: true, repeat: 1 }}, {T(ph, "s3c", 0.5)});
      tl.fromTo("#s3-roles", {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }}, {T(ph, "s3d", 0.1)});
      // the chain, in the order it is named
      tl.to("#s3-m-med", {{ opacity: 1, duration: 0.3 }}, {tE:.3f});
      tl.fromTo("#s3-n-med", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, {tE:.3f});
      {draw(["x-med", "oh-x", "x-ne"], tE + 0.2)}
      {draw(["oh-db"], tE + 1.1)}
      tl.to("#s3-m-os", {{ opacity: 1, duration: 0.3 }}, {tE + 1.9:.3f});
      tl.fromTo("#s3-n-os", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, {tE + 1.9:.3f});
      {draw(["db-j", "j-os"], tE + 1.8)}
      tl.to("#s3-m-aw, #s3-m-ne", {{ opacity: 1, duration: 0.3 }}, {tE + 2.7:.3f});
      tl.fromTo("#s3-n-aw", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, {tE + 2.7:.3f});
      {draw(["j-aw"], tE + 2.6)}
      tl.fromTo("#s3-k1, #s3-k2, #s3-k3, #s3-k4", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3, stagger: 0.25 }}, {tE + 0.8:.3f});
      tl.fromTo("#s3-cav", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, {tE + 1.0:.3f});
      // two directions: from Mediouna and from Laawamer
      tl.to("#s3-svg .fl", {{ opacity: 1, duration: 0.3 }}, {tF:.3f});
      tl.fromTo("#s3-svg .fl", {{ strokeDashoffset: 0 }}, {{ strokeDashoffset: -260, duration: {max(3.0, dur - tF):.2f}, ease: "none" }}, {tF:.3f});
      tl.fromTo("#s3-fromm", {{ opacity: 0, x: 12 }}, {{ opacity: 1, x: 0, duration: 0.35 }}, {T(ph, "s3f", 0.55)});
      tl.fromTo("#s3-froma", {{ opacity: 0, x: -12 }}, {{ opacity: 1, x: 0, duration: 0.35 }}, {T(ph, "s3f", 0.75)});
      // 400 kV supply behind Mediouna
      {draw(["jorf", "awj"], T(ph, "s3g", 0.3), 1.2, 0.3)}
      tl.fromTo("#s3-l400, #s3-l225", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.35, stagger: 0.3 }}, {T(ph, "s3g", 0.55)});"""
    return tpl("s3", css, body, js), dur


# ------------------------------------------------------------------------------------------- S4
def s4():
    """Two official accounts of the same night: the spokesperson (3 cables) and ONEE via Le360 (4 lines)."""
    ph, dur, mk = cues("s4")
    css = """
    #s4-eyebrow { top: 178px; } #s4-title { top: 224px; font-size: 58px; }
    .st4 { position: absolute; right: 64px; left: 64px; height: 370px; padding: 26px 30px; opacity: 0; display: flex; gap: 28px; align-items: center; }
    .st4 .num { flex: 0 0 auto; width: 190px; text-align: center; font: 700 190px/1 "Space Grotesk"; color: #E8EEEC; }
    .st4 .tx { flex: 1; }
    .st4 .who { display: flex; gap: 10px; align-items: center; font: 700 30px/1.25 "Plex Arabic"; color: #93CDBB; }
    .st4 .what { margin-top: 14px; font: 700 46px/1.2 "Plex Arabic"; color: #E8EEEC; }
    .st4 .sub { margin-top: 12px; font: 600 30px/1.3 "Plex Arabic"; color: #93A4A7; }
    .st4 .lat { font-family: "Space Grotesk"; direction: ltr; unicode-bidi: isolate; }
    #s4-a { top: 330px; } #s4-b { top: 740px; }
    #s4-neq { position: absolute; left: 0; right: 0; top: 1140px; text-align: center; opacity: 0; }
    #s4-neq b { display: inline-block; font: 700 64px/1 "Space Grotesk"; color: #0D1316; background: #F4A62A; border-radius: 14px; padding: 12px 30px 16px; direction: ltr; }
    #s4-neq span { display: block; margin-top: 14px; font: 700 34px/1 "Plex Arabic"; color: #E8EEEC; }
    #s4-note { position: absolute; left: 64px; right: 64px; top: 1340px; text-align: center; font: 600 30px/1.3 "Plex Arabic"; color: #93A4A7; opacity: 0; }
"""
    body = f"""    <div class="grid"></div>
    <div id="s4-eyebrow" class="eyebrow"><i></i><span>الرواية الرسمية</span></div>
    <div id="s4-title" class="title">شحال من خط طاح؟</div>
    <div id="s4-a" class="st4 card"><div class="num">3</div><div class="tx">
      <div class="who">{CHECK.format(s=28, c="#93CDBB")}<span>الناطق الرسمي باسم الحكومة</span></div>
      <div class="what">كابلات ديال الجهد العالي طاحو</div>
      <div class="sub">من بينهم الكابل الرئيسي · السبب: الرياح</div></div></div>
    <div id="s4-b" class="st4 card"><div class="num">4</div><div class="tx">
      <div class="who">{CHECK.format(s=28, c="#93CDBB")}<span>المكتب الوطني · بلاغ حسب <span class="lat">Le360</span></span></div>
      <div class="what">خطوط ديال 225 ك.ف تتلفو</div>
      <div class="sub">فنفس الوقت · السبب: العاصفة</div></div></div>
    <div id="s4-neq"><b>3 ≠ 4</b><span>الرقم ماشي نفسو</span></div>
    <div id="s4-note">البلاغ ما سمّاش الخطوط: ما نقدروش نأكدو واش الشريان ديال المحطتين من بينهم</div>"""
    js = f"""
      tl.fromTo("#s4-eyebrow, #s4-title", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.5, stagger: 0.1, ease: "power3.out" }}, 0);
      tl.fromTo("#s4-a", {{ opacity: 0, y: 22 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, {T(ph, "s4a", 0.1)});
      tl.fromTo("#s4-a .num", {{ scale: 0.6 }}, {{ scale: 1, duration: 0.45, ease: "back.out(1.8)" }}, {T(ph, "s4a", 0.45)});
      tl.fromTo("#s4-b", {{ opacity: 0, y: 22 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, {T(ph, "s4b", 0.1)});
      tl.fromTo("#s4-b .num", {{ scale: 0.6 }}, {{ scale: 1, duration: 0.45, ease: "back.out(1.8)" }}, {T(ph, "s4b", 0.5)});
      tl.to("#s4-a .num, #s4-b .num", {{ color: "#F4A62A", duration: 0.25 }}, {T(ph, "s4c")});
      tl.fromTo("#s4-neq", {{ opacity: 0, scale: 0.85 }}, {{ opacity: 1, scale: 1, duration: 0.4, ease: "back.out(1.7)" }}, {T(ph, "s4c", 0.1)});
      tl.fromTo("#s4-note", {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }}, {T(ph, "s4d", 0.05)});"""
    return tpl("s4", css, body, js), dur


# ------------------------------------------------------------------------------------------- S5
def s5():
    """How the outage happens, on the same map: one cut is bridged, two cuts (one on each side)
    isolate both substations (illustrative positions: ONEE named no line); then the planned line."""
    ph, dur, mk = cues("s5")
    p = "s5"
    L = SUBXY
    ca = mid(pts("oh-x")); cb = mid(pts("db-j"))
    a, o = L["aw"], L["oh"]
    plan = f"M {a[0]:.1f} {a[1]:.1f} Q 640 1020 {o[0]:.1f} {o[1]:.1f}"
    css = REGION_CSS + """
    #s5-eyebrow { top: 178px; } #s5-title { top: 224px; font-size: 54px; }
    .cut { opacity: 0; }
    #s5-ex { position: absolute; top: 1138px; right: 64px; opacity: 0; }
    #s5-ex span { display: inline-block; font: 700 30px/1 "Plex Arabic"; color: #F25C54; border: 2.5px solid #F25C54; border-radius: 10px;
      padding: 6px 12px 10px; background: rgba(13,19,22,.92); }
    #s5-step { position: absolute; left: 64px; right: 64px; top: 1196px; height: 236px; }
    .stp { position: absolute; inset: 0; padding: 18px 24px 22px; opacity: 0; }
    .stp .k { display: flex; gap: 10px; align-items: center; font: 700 28px/1.2 "Plex Arabic"; color: #93CDBB; }
    .stp .v { margin-top: 10px; font: 700 38px/1.25 "Plex Arabic"; color: #E8EEEC; }
    .stp .v b { color: #F25C54; }
    .stp .s { margin-top: 8px; font: 600 28px/1.3 "Plex Arabic"; color: #93A4A7; }
    .stp .lat { font-family: "Space Grotesk"; direction: ltr; unicode-bidi: isolate; }
    #s5-plan { fill: none; stroke: #F4A62A; stroke-width: 6; stroke-dasharray: 14 12; stroke-linecap: round; opacity: 0; }
    #s5-late, #s5-pl, #s5-city { opacity: 0; }
    #s5-late { position: absolute; left: 560px; top: 900px; transform: rotate(-8deg); }
    #s5-late span { display: inline-block; font: 700 34px/1 "Plex Arabic"; color: #F25C54; border: 3px solid #F25C54; border-radius: 10px; padding: 6px 12px 10px; background: rgba(13,19,22,.92); }
    #s5-pl { position: absolute; left: 560px; top: 965px; }
    #s5-city { position: absolute; left: 64px; top: 330px; font: 700 28px/1.25 "Plex Arabic"; color: #E8EEEC; background: rgba(13,19,22,.9);
      border: 1.5px solid #26343B; border-radius: 10px; padding: 6px 12px 10px; width: 300px; text-align: right; }
"""
    xmark = lambda i, c: (f'<g transform="translate({c[0]:.1f},{c[1]:.1f})"><g id="s5-cut{i}" class="cut"><circle r="26" fill="rgba(13,19,22,.9)" stroke="#F25C54" stroke-width="4"/>'
                          f'<path d="M -11 -11 L 11 11 M 11 -11 L -11 11" stroke="#F25C54" stroke-width="6" stroke-linecap="round"/></g></g>')
    body = f"""    <div class="grid"></div>
    {region_layer(p)}
    <svg viewBox="0 0 1080 1920" style="position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:visible">
      <path id="s5-plan" d="{plan}"/>{xmark("a", ca)}{xmark("b", cb)}
    </svg>
    {name_chip(p, "oh", "أولاد حدو", "225 ك.ف", int(L["oh"][0]) + 18, int(L["oh"][1]) - 104, "l")}
    {name_chip(p, "db", "دار بوعزة", "225 ك.ف", int(L["db"][0]) - 18, int(L["db"][1]) - 104)}
    {name_chip(p, "med", "مديونة", "400/225 ك.ف", int(L["med"][0]) - 26, int(L["med"][1]) - 104)}
    {name_chip(p, "os", "أولاد صالح", "225 ك.ف", int(L["os"][0]) + 22, int(L["os"][1]) - 10, "l")}
    {name_chip(p, "aw", "العوامر", "225/60 ك.ف", int(L["aw"][0]) + 22, int(L["aw"][1]) + 6, "l")}
    <div id="s5-eyebrow" class="eyebrow"><i></i><span>كيفاش طرا الانقطاع؟</span></div>
    <div id="s5-title" class="title ink">جوج جهات… وطفاو بجوج</div>
    <div id="s5-ex"><span>مثال توضيحي · البلاغ ما سمّاش الخطوط</span></div>
    <div id="s5-city">الأحياء اللي تبلّغ على انقطاعها (الخريطة 2)</div>
    <div id="s5-late"><span>متأخر</span></div>
    <div id="s5-pl" class="km">خط مبرمج · 32 كلم · مسار تقريبي</div>
    <div id="s5-step">
      <div id="s5-st1" class="stp card"><div class="k">1 · خط واحد مقطوع</div><div class="v">الضو يقدر يدوز من <b>الجهة الأخرى</b></div><div class="s">المحطتين باقيين كيتغذاو</div></div>
      <div id="s5-st2" class="stp card"><div class="k">2 · مقطوع من الجهتين</div><div class="v">المحطتين <b>بلا تغذية</b></div><div class="s">أولاد صالح باقي كيتغذى من العوامر</div></div>
      <div id="s5-st3" class="stp card"><div class="k">{CHECK.format(s=26, c="#93CDBB")}<span>بلاغ المكتب الوطني (حسب <span class="lat">Le360</span>)</span></div><div class="v">4 خطوط ديال 225 ك.ف تتلفو فنفس الوقت</div><div class="s">شمن خطوط؟ البلاغ ما حددش</div></div>
      <div id="s5-st4" class="stp card"><div class="k">{DOC.format(w=22, h=26)}<span>طلب عروض المكتب الوطني (2020)</span></div><div class="v">خط مبرمج: العوامر–أولاد حدو</div><div class="s">225 ك.ف مزدوج · 32 كيلومتر</div></div>
      <div id="s5-st5" class="stp card"><div class="k">{DOC.format(w=22, h=26)}<span>حسب <span class="lat">Maroc Diplomatique</span> و <span class="lat">LesEco</span></span></div><div class="v">الشركات انسحبات، والخط باقي متأخر</div><div class="s" style="direction:ltr;text-align:right;font-family:'Space Grotesk'">Cegelec · Medicable</div></div>
    </div>
    <div class="credit" data-layout-ignore>Imagery: Esri, Maxar, Earthstar Geographics · Grid: © OpenStreetMap</div>"""
    tb, tc, td, te, tf, tg = (T(ph, k, 0.1) for k in ("s5b", "s5c", "s5d", "s5e", "s5f", "s5g"))
    swap = lambda a_, b_, t: (f'tl.to("#s5-st{a_}", {{ opacity: 0, duration: 0.2 }}, {t - 0.05:.3f});' if a_ else "") + \
        f'tl.fromTo("#s5-st{b_}", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }}, {t:.3f});'
    js = f"""
      tl.fromTo("#s5-eyebrow, #s5-title", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.5, stagger: 0.1, ease: "power3.out" }}, 0);
      tl.fromTo("#s5-svg .mk, .nm", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, 0.2);
      tl.set("#s5-svg .l4, #s5-svg .l2", {{ opacity: 0.6 }}, 0);
      // normal: power from both ends
      tl.to("#s5-svg .fl", {{ opacity: 1, duration: 0.3 }}, 0.3);
      tl.fromTo("#s5-svg .fl", {{ strokeDashoffset: 0 }}, {{ strokeDashoffset: -{int(dur * 40)}, duration: {dur:.2f}, ease: "none" }}, 0);
      // 1) one line cut: Mediouna's side stops, the south still reaches both substations
      tl.fromTo("#s5-ex", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, {tb:.3f});
      tl.fromTo("#s5-cuta", {{ opacity: 0, scale: 1.6, transformOrigin: "50% 50%" }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "power3.out" }}, {tb + 0.3:.3f});
      tl.to("#s5-f-x-med, #s5-f-oh-x", {{ opacity: 0, duration: 0.25 }}, {tb + 0.45:.3f});
      {swap(0, 1, tb + 0.3)}
      // 2) cut on the other side too: both substations lose their supply; Ouled Saleh is still fed
      tl.fromTo("#s5-cutb", {{ opacity: 0, scale: 1.6, transformOrigin: "50% 50%" }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "power3.out" }}, {tc + 0.3:.3f});
      tl.to("#s5-f-db-j, #s5-f-oh-db", {{ opacity: 0, duration: 0.25 }}, {tc + 0.45:.3f});
      tl.to("#s5-m-oh rect, #s5-m-db rect", {{ fill: "#05080A", duration: 0.35 }}, {tc + 0.6:.3f});
      {swap(1, 2, tc + 0.3)}
      {swap(2, 3, td)}
      tl.to("#s5-ex", {{ scale: 1.08, duration: 0.18, yoyo: true, repeat: 1 }}, {T(ph, "s5d", 0.7):.3f});
      // the neighbourhoods reported dark
      tl.to(".s5-dk", {{ opacity: 1, duration: 0.5, stagger: 0.04 }}, {te:.3f});
      tl.fromTo("#s5-city", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.35 }}, {te + 0.2:.3f});
      // the planned Laawamer–Oulad Haddou line, still late
      tl.to("#s5-ex, #s5-city", {{ opacity: 0, duration: 0.3 }}, {tf - 0.1:.3f});
      {swap(3, 4, tf)}
      tl.fromTo("#s5-plan", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.6 }}, {tf + 0.2:.3f});
      tl.fromTo("#s5-plan", {{ strokeDashoffset: 0 }}, {{ strokeDashoffset: -78, duration: 3.0, ease: "none" }}, {tf + 0.2:.3f});
      tl.fromTo("#s5-pl", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, {tf + 0.8:.3f});
      {swap(4, 5, tg)}
      tl.fromTo("#s5-late", {{ opacity: 0, scale: 1.4 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "power3.out" }}, {T(ph, "s5g", 0.4):.3f});"""
    return tpl("s5", css, body, js), dur


# ------------------------------------------------------------------------------------------- S6
def s6():
    """How long it lasted: 3 h in the spokesperson's statement, 23:00 in one resident's neighbourhood."""
    ph, dur, mk = cues("s6")
    Y0, PX = 360, 125                      # 16:00 at y 360, 125 px an hour
    y = lambda h: Y0 + (h - 16) * PX
    t_start, t_a, t_b = 16 + 48 / 60, 16 + 48 / 60 + 3, 23.0
    css = f"""
    #s6-eyebrow {{ top: 178px; }} #s6-title {{ top: 224px; font-size: 58px; }}
    #s6-axis {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1500px; }}
    .hr {{ position: absolute; left: 64px; width: 110px; font: 700 28px/1 "Space Grotesk"; color: #6E8186; direction: ltr; text-align: left; }}
    .bar {{ position: absolute; top: {y(t_start):.0f}px; border-radius: 0 0 12px 12px; transform-origin: 50% 0; }}
    #s6-ba {{ left: 270px; width: 170px; height: {y(t_a) - y(t_start):.0f}px; background: rgba(147,205,187,.22); border: 2.5px solid #93CDBB; }}
    #s6-bb {{ left: 610px; width: 170px; height: {y(t_b) - y(t_start):.0f}px; background: rgba(244,166,42,.22); border: 2.5px solid #F4A62A; }}
    .lab6 {{ position: absolute; width: 380px; text-align: center; opacity: 0; }}
    .lab6 b {{ display: block; font: 700 46px/1.1 "Space Grotesk"; color: #E8EEEC; direction: ltr; }}
    .lab6 span {{ display: block; margin-top: 6px; font: 700 28px/1.25 "Plex Arabic"; color: #93A4A7; }}
    #s6-la {{ left: 165px; top: {y(t_a) + 14:.0f}px; }} #s6-lb {{ left: 505px; top: {y(t_b) + 14:.0f}px; }}
    #s6-lb b {{ color: #F4A62A; }}
    #s6-start {{ position: absolute; left: 180px; right: 64px; top: {y(t_start) - 46:.0f}px; display: flex; justify-content: space-between; opacity: 0; }}
    #s6-start span {{ font: 700 30px/1 "Plex Arabic"; color: #E8EEEC; }}
    #s6-gap {{ position: absolute; left: 812px; top: {(y(t_a) + y(t_b)) / 2 - 60:.0f}px; width: 220px; text-align: center; opacity: 0; }}
    #s6-gap b {{ display: block; font: 700 40px/1.1 "Plex Arabic"; color: #F4A62A; }}
    #s6-gap span {{ display: block; margin-top: 8px; font: 600 28px/1.25 "Plex Arabic"; color: #93A4A7; }}
    .tagw {{ display: inline-block; margin-top: 8px; font: 700 28px/1 "Plex Arabic"; color: #F4A62A; border: 2px solid #F4A62A; border-radius: 8px; padding: 4px 10px 8px; }}
"""
    ticks = "".join(f'<path d="M 180 {y(h):.0f} H 1016" stroke="#26343B" stroke-width="{2 if h % 2 == 0 else 1}"/>' for h in range(16, 25))
    hrs = "".join(f'<div class="hr" style="top:{y(h) - 13:.0f}px">{h:02d}:00</div>' for h in range(16, 25))
    body = f"""    <div class="grid"></div>
    <div id="s6-eyebrow" class="eyebrow"><i></i><span>مدة الانقطاع</span></div>
    <div id="s6-title" class="title">ثلاث ساعات… ولا ست؟</div>
    <svg id="s6-axis" viewBox="0 0 1080 1500">{ticks}
      <path d="M 180 {y(t_start):.0f} H 1016" stroke="#E8EEEC" stroke-width="3" stroke-dasharray="10 8"/></svg>
    {hrs}
    <div id="s6-start"><span>16:48 · الانقطاع</span></div>
    <div id="s6-ba" class="bar"></div>
    <div id="s6-bb" class="bar"></div>
    <div id="s6-la" class="lab6"><b>19:48</b><span>3 ساعات · حسب الناطق الرسمي</span></div>
    <div id="s6-lb" class="lab6"><b>23:00</b><span>شهادة من ساكن فالدار البيضاء</span></div>
    <div id="s6-gap" data-hold><b>+6 ساعات</b><span>و12 دقيقة فهاد الحي</span><div class="tagw">شهادة</div></div>"""
    js = f"""
      tl.fromTo("#s6-eyebrow, #s6-title", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.5, stagger: 0.1, ease: "power3.out" }}, 0);
      tl.fromTo("#s6-axis, .hr", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5 }}, 0.2);
      tl.fromTo("#s6-start", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, 0.4);
      tl.fromTo("#s6-ba", {{ scaleY: 0 }}, {{ scaleY: 1, duration: 1.2, ease: "power2.inOut" }}, {T(ph, "s6a", 0.3)});
      tl.fromTo("#s6-la", {{ opacity: 0, y: -8 }}, {{ opacity: 1, y: 0, duration: 0.4 }}, {T(ph, "s6a", 0.3) + 1.1:.3f});
      tl.fromTo("#s6-bb", {{ scaleY: 0 }}, {{ scaleY: 1, duration: 2.0, ease: "power2.inOut" }}, {T(ph, "s6b", 0.1)});
      tl.fromTo("#s6-lb", {{ opacity: 0, y: -8 }}, {{ opacity: 1, y: 0, duration: 0.4 }}, {T(ph, "s6b", 0.1) + 1.9:.3f});
      tl.fromTo("#s6-gap", {{ opacity: 0, scale: 0.9 }}, {{ opacity: 1, scale: 1, duration: 0.4, ease: "back.out(1.6)" }}, {T(ph, "s6c", 0.1)});"""
    return tpl("s6", css, body, js), dur


# ------------------------------------------------------------------------------------------- S7 (prevention, unchanged from the earlier S5)
BULLETS = ["ربط المحطات بأكثر من خط تغذية", "فحص وصيانة الخطوط والعوازل قبل العواصف", "حماية ضد الصواعق",
           "مراقبة الشبكة حسب الإنذارات الجوية", "مولدات احتياطية للمرافق الحيوية"]
ICONS = [
    '<path d="M20 10 V60 M100 10 V60" stroke="#93A4A7" stroke-width="5"/><path d="M20 60 Q20 80 60 80 M100 60 Q100 80 60 80" fill="none" stroke="#F4A62A" stroke-width="5"/><rect x="34" y="80" width="52" height="40" rx="5" fill="#141D21" stroke="#93CDBB" stroke-width="4"/>',
    '<path d="M40 10 V90" stroke="#93A4A7" stroke-width="4"/><g fill="#141D21" stroke="#93CDBB" stroke-width="4"><ellipse cx="40" cy="34" rx="18" ry="6"/><ellipse cx="40" cy="50" rx="18" ry="6"/><ellipse cx="40" cy="66" rx="18" ry="6"/></g><circle cx="80" cy="56" r="22" fill="none" stroke="#E8EEEC" stroke-width="5"/><path d="M96 72 L114 92" stroke="#E8EEEC" stroke-width="7" stroke-linecap="round"/>',
    '<path d="M60 30 V116 M44 116 H76" stroke="#93CDBB" stroke-width="5"/><path d="M60 30 L54 12 M60 30 L66 12" stroke="#93CDBB" stroke-width="4"/><path d="M96 4 L80 34 H92 L84 58 L108 26 H96 L104 4 Z" fill="#F4A62A"/>',
    '<rect x="10" y="16" width="100" height="72" rx="8" fill="#141D21" stroke="#93CDBB" stroke-width="4"/><path d="M60 30 L84 74 H36 Z" fill="none" stroke="#F4A62A" stroke-width="5" stroke-linejoin="round"/><path d="M60 44 V58 M60 64 V66" stroke="#F4A62A" stroke-width="5" stroke-linecap="round"/><path d="M44 102 H76 M60 88 V102" stroke="#93CDBB" stroke-width="4"/>',
    '<rect x="10" y="36" width="100" height="62" rx="8" fill="#141D21" stroke="#93CDBB" stroke-width="4"/><circle cx="40" cy="67" r="16" fill="none" stroke="#93CDBB" stroke-width="4"/><path d="M84 52 L72 70 H82 L76 86 L94 62 H84 L90 52 Z" fill="#F4A62A"/><path d="M20 98 V110 M100 98 V110" stroke="#93CDBB" stroke-width="5"/>',
]


def s7():
    ph, dur, mk = cues("s7")
    css = """
    #s7-eyebrow { top: 178px; } #s7-title { top: 224px; font-size: 58px; }
    #s7-steps { position: absolute; right: 64px; left: 64px; top: 330px; display: flex; gap: 18px; justify-content: flex-start; direction: rtl; }
    .st { width: 64px; height: 64px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
      font: 700 32px/1 "Space Grotesk"; color: #6E8186; border: 2px solid #26343B; background: #141D21; }
    .bl { position: absolute; right: 64px; left: 64px; top: 440px; display: flex; flex-direction: column; align-items: flex-start; gap: 22px; }
    .bl .tx { font: 700 80px/1.16 "Plex Arabic"; color: #E8EEEC; text-align: right; }
    #s7-list { position: absolute; right: 64px; left: 64px; top: 960px; display: flex; flex-direction: column; gap: 12px; }
    .li { display: flex; align-items: center; gap: 16px; padding: 12px 20px 16px; font: 700 34px/1.2 "Plex Arabic"; color: #E8EEEC; }
    .li b { flex: 0 0 auto; width: 48px; height: 48px; border-radius: 50%; border: 2px solid #93CDBB; color: #93CDBB;
      font: 700 28px/44px "Space Grotesk"; text-align: center; }
    .bl, .li { opacity: 0; }
"""
    steps = "".join(f'<div id="s7-st{i}" class="st">{i + 1}</div>' for i in range(5))
    bl = "".join(f'<div id="s7-b{i}" class="bl"><svg width="190" height="180" viewBox="0 0 120 120" fill="none">{ICONS[i]}</svg><div class="tx ink">{BULLETS[i]}</div></div>' for i in range(5))
    li = "".join(f'<div id="s7-l{i}" class="li card"><b>{i + 1}</b><span>{BULLETS[i]}</span></div>' for i in range(5))
    body = f"""    <div class="grid"></div>
    <div id="s7-eyebrow" class="eyebrow"><i></i><span>باش ما يتعاودش</span></div>
    <div id="s7-title" class="title">حلول معروفة</div>
    <div id="s7-steps">{steps}</div>
    {bl}
    <div id="s7-list" data-hold>{li}</div>"""
    starts = [T(ph, k) for k in ("s7b", "s7c", "s7d", "s7e", "s7f")]
    bj = []
    for i, t in enumerate(starts):
        if i > 0:
            bj += [f'tl.to("#s7-b{i - 1}", {{ opacity: 0, y: -18, duration: 0.3, ease: "power2.in" }}, {t - 0.05:.3f});',
                   f'tl.to("#s7-st{i - 1}", {{ backgroundColor: "#141D21", color: "#93CDBB", borderColor: "#93CDBB", duration: 0.25 }}, {t - 0.05:.3f});',
                   f'tl.fromTo("#s7-l{i - 1}", {{ opacity: 0, x: 24 }}, {{ opacity: 1, x: 0, duration: 0.4, ease: "power3.out" }}, {t + 0.05:.3f});']
        bj += [f'tl.to("#s7-st{i}", {{ backgroundColor: "#F4A62A", color: "#0D1316", borderColor: "#F4A62A", duration: 0.25 }}, {t});',
               f'tl.fromTo("#s7-b{i}", {{ opacity: 0, y: 26 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, {t + 0.1:.3f});']
    bul_js = "\n".join("      " + x for x in bj)
    fin = round(min(dur - 1.9, T(ph, "s7f") + (ph["s7f"][1] - ph["s7f"][0]) + 0.6), 3)
    js = f"""
      tl.fromTo("#s7-eyebrow, #s7-title", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.5, stagger: 0.1, ease: "power3.out" }}, 0);
      tl.fromTo("#s7-steps .st", {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: 0.35, stagger: 0.06, ease: "power3.out" }}, {T(ph, "s7a", 0.4)});
{bul_js}
      tl.to("#s7-st4", {{ backgroundColor: "#141D21", color: "#93CDBB", borderColor: "#93CDBB", duration: 0.25 }}, {fin});
      tl.fromTo("#s7-l4", {{ opacity: 0, x: 24 }}, {{ opacity: 1, x: 0, duration: 0.4, ease: "power3.out" }}, {fin});"""
    return tpl("s7", css, body, js), dur


# ------------------------------------------------------------------------------------------- S8
def s8():
    ph, dur, mk = cues("s8")
    qs = [("s8b", "علاش تلاتة فالتصريح وربعة فالبلاغ؟"), ("s8c", "علاش شريان كيتغذى من جوج جهات طفا كامل؟"),
          ("s8d", "علاش خط التقوية باقي متأخر؟"), ("s8e", "علاش ثلاث ساعات فالتصريح، وأكثر من ست فواحد الحي؟")]
    css = """
    #s8-eyebrow { top: 178px; } #s8-title { top: 224px; font-size: 60px; }
    .q8 { position: absolute; right: 64px; left: 64px; display: flex; align-items: center; gap: 20px; padding: 22px 26px 28px; opacity: 0; }
    .q8 b { flex: 0 0 auto; width: 56px; height: 56px; border-radius: 50%; background: #F4A62A; color: #0D1316;
      font: 700 34px/56px "Plex Arabic"; text-align: center; }
    .q8 span { font: 700 40px/1.25 "Plex Arabic"; color: #E8EEEC; }
    #s8-wait { position: absolute; right: 64px; left: 64px; top: 1130px; display: flex; align-items: center; gap: 22px;
      padding: 26px 30px 32px; font: 700 48px/1.2 "Plex Arabic"; color: #E8EEEC; border-color: #93CDBB; opacity: 0; }
"""
    cards = "".join(f'<div id="s8-q{i}" class="q8 card" style="top:{330 + i * 190}px"><b>؟</b><span>{t}</span></div>' for i, (_, t) in enumerate(qs))
    body = f"""    <div class="grid"></div>
    <div id="s8-eyebrow" class="eyebrow"><i></i><span>أسئلة</span></div>
    <div id="s8-title" class="title">باقية بلا جواب</div>
    {cards}
    <div id="s8-wait" class="card" data-hold>{DOC.format(w=60, h=72)}<span>ننتظرو تقرير تقني مفصل</span></div>"""
    lines = "\n".join(f'      tl.fromTo("#s8-q{i}", {{ opacity: 0, x: 24 }}, {{ opacity: 1, x: 0, duration: 0.45, ease: "power3.out" }}, {T(ph, k, 0.02)});' for i, (k, _) in enumerate(qs))
    js = f"""
      tl.fromTo("#s8-eyebrow, #s8-title", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.5, stagger: 0.1, ease: "power3.out" }}, 0);
{lines}
      tl.fromTo("#s8-wait", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, {T(ph, "s8f")});"""
    return tpl("s8", css, body, js), dur


# ------------------------------------------------------------------------------------------- END
def end():
    dur = CUES.get("end", {}).get("duration", 8.0)
    groups = [
        ("رسمي", ["تصريح الناطق الرسمي باسم الحكومة", "بلاغ <span class=\"lat\">SRM</span> الدار البيضاء–سطات",
                  "بلاغ المكتب الوطني للكهرباء (حسب <span class=\"lat\">Le360</span>)"]),
        ("وثائق تقنية", ["طلب عروض المكتب الوطني: خط العوامر–أولاد حدو (2020)", "<span class=\"lat\">ONEE — Rapport d'activités 2021</span>",
                         "المكتب الوطني: خط 400 ك.ف الجرف الأصفر–مديونة", "تقرير تدريب جامعي: مركز العوامر (2016)"]),
        ("صحافة", ["<span class=\"lat\">Le360 · Médias24 · Hespress · Le Matin · L'Usine Nouvelle · Challenge · Maroc Diplomatique · LesEco</span>"]),
        ("شهادة", ["ساكن من الدار البيضاء: رجوع الضو حتى 23:00"]),
    ]
    html = []
    for gi, (g, items) in enumerate(groups):
        html.append(f'<div id="end-g{gi}" class="eg"><div class="eh">{g}</div>' + "".join(f'<div class="ei">{x}</div>' for x in items) + "</div>")
    css = """
    #end-eyebrow { top: 178px; }
    #end-list { position: absolute; right: 64px; left: 64px; top: 236px; display: flex; flex-direction: column; gap: 22px; }
    .eg { padding: 18px 24px 22px; background: #141D21; border: 1.5px solid #26343B; border-radius: 14px; }
    .eh { font: 700 28px/1 "Plex Arabic"; color: #93CDBB; margin-bottom: 10px; }
    .ei { font: 700 30px/1.4 "Plex Arabic"; color: #E8EEEC; }
    .ei .lat, #end-credits .lat { font-family: "Space Grotesk"; direction: ltr; unicode-bidi: isolate; }
    #end-credits { position: absolute; right: 64px; left: 64px; top: 1330px; font: 600 28px/1.5 "Plex Arabic"; color: #93A4A7; text-align: right; }
"""
    body = f"""    <div class="grid"></div>
    <div id="end-eyebrow" class="eyebrow"><i></i><span>المصادر</span></div>
    <div id="end-list" data-hold>{''.join(html)}</div>
    <div id="end-credits">صورة الخريطة: <span class="lat">Esri, Maxar, Earthstar Geographics</span> · مواقع الأحياء: <span class="lat">© OpenStreetMap</span></div>"""
    js = """
      tl.fromTo("#end-eyebrow", { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }, 0.1);
      tl.fromTo("#end-list .eg", { opacity: 0, y: 18 }, { opacity: 1, y: 0, duration: 0.45, stagger: 0.2, ease: "power3.out" }, 0.3);
      tl.fromTo("#end-credits", { opacity: 0 }, { opacity: 1, duration: 0.5 }, 1.4);"""
    return tpl("end", css, body, js), dur


if __name__ == "__main__":
    (ROOT / "compositions").mkdir(exist_ok=True)
    durs = {}
    for name, fn in (("s1", s1), ("s3", s3), ("s4", s4), ("s5", s5), ("s6", s6), ("s7", s7), ("s8", s8), ("end", end)):
        html, d = fn()
        (ROOT / f"compositions/{name}.html").write_text(html)
        durs[name] = d
    import subprocess
    for sid in ("s3", "s5"):
        r = subprocess.run(["npx", "hyperframes", "media-treatment", "--project", str(ROOT), "--file", f"compositions/{sid}.html",
                            "--selector", f"#{sid}-sat", "--grading", GRADE, "--apply", "--json"], capture_output=True, text=True)
        if '"ok": true' not in r.stdout:
            print("GRADE FAILED", sid, r.stdout[-300:], r.stderr[-300:])
    print(json.dumps(durs))
