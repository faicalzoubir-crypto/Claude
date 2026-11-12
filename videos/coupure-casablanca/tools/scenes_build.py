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
def s3():
    ph, dur, mk = cues("s3")
    XR, XL = 790, 290           # أولاد حدو (named first) right/east, دار بوعزة left/west, like the map
    Y = {"plant": 350, "corr": 610, "ss": 820, "house": 1130}
    css = f"""
    #s3-eyebrow {{ top: 178px; }} #s3-title {{ top: 222px; font-size: 56px; }}
    #s3-svg {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1400px; overflow: visible; }}
    .flow {{ fill: none; stroke: #F4A62A; stroke-width: 5; stroke-linecap: round; stroke-dasharray: 10 18; opacity: 0; }}
    #s3-cut-r, #s3-cut-l {{ opacity: 0; }}
    #s3-svg > .wire {{ opacity: 0; }}
    .s3-h-r-win, .s3-h-l-win {{ opacity: 0.22; }}
    .wire {{ fill: none; stroke: #93A4A7; stroke-width: 3; }}
    #s3-note {{ position: absolute; left: 64px; right: 64px; top: 1272px; text-align: center; font: 700 34px/1.25 "Plex Arabic"; color: #93A4A7; }}
    #s3-myth {{ position: absolute; left: 0; right: 0; top: 1268px; display: flex; justify-content: center; gap: 24px; align-items: center;
      font: 700 44px/1 "Plex Arabic"; color: #E8EEEC; }}
    #s3-myth .no {{ color: #93A4A7; position: relative; }}
    #s3-myth .no::after {{ content: ""; position: absolute; left: -6px; right: -6px; top: 52%; height: 5px; background: #F25C54; border-radius: 3px;
      transform-origin: right center; transform: scaleX(var(--strike, 0)); }}
"""
    cy = Y["corr"] - 4                      # conductor height at the pylons
    drop0, drop1 = cy + 34, Y["ss"]
    flow_paths = [("s3-f-pl-r", f"M {XR + 30} {Y['plant'] + 90} V {cy - 8}"), ("s3-f-pl-l", f"M {XL - 30} {Y['plant'] + 90} V {cy - 8}"),
                  ("s3-f-in-r", f"M {XR} {drop0} V {drop1}"), ("s3-f-in-l", f"M {XL} {drop0} V {drop1}")]
    out_paths = []
    o0 = Y["ss"] + 130 + 64
    for side, x in (("r", XR), ("l", XL)):
        for j, dx in enumerate((-96, 0, 96)):
            out_paths.append((f"s3-f-out-{side}{j}", f"M {x} {o0} C {x} {o0 + 40} {x + dx} {o0 + 44} {x + dx} {Y['house'] - 8}"))
    svg_paths = "".join(f'<path id="{i}" class="wire" d="{d}"/><path id="{i}-a" class="flow" d="{d}"/>' for i, d in flow_paths + out_paths)
    cut_y = (drop0 + drop1) / 2
    cut = lambda x, i: f'<path id="s3-cut-{i}" d="M {x - 24} {cut_y - 10} L {x + 24} {cut_y + 10} M {x - 24} {cut_y + 10} L {x + 24} {cut_y - 10}" stroke="#F25C54" stroke-width="7" stroke-linecap="round"/>'
    corr = f"M 120 {cy} Q 330 {cy + 30} 540 {cy} Q 750 {cy + 30} 960 {cy}"
    body = f"""    <div class="grid"></div>
    <div id="s3-eyebrow" class="eyebrow"><i></i><span>محطات التحويل</span></div>
    <div id="s3-title" class="title">كيفاش كيوصل الضو للحي؟</div>
    <svg id="s3-svg" viewBox="0 0 1080 1400">
      <g id="s3-plants">{plant(XL - 30, Y['plant'], "s3-pl-l")}{plant(XR + 30, Y['plant'], "s3-pl-r")}</g>
      <g id="s3-corr">
        <path d="{corr}" class="wire" stroke-width="3.5"/><path id="s3-c-flow" d="{corr}" class="flow"/>
        {pylon(120, cy - 14, 110)}{pylon(540, cy - 14, 110)}{pylon(960, cy - 14, 110)}
      </g>
      {svg_paths}
      {cut(XR, "r")}{cut(XL, "l")}
      {substation(XR, Y['ss'], "s3-ss-r")}{substation(XL, Y['ss'], "s3-ss-l")}
      {houses(XR, Y['house'], "s3-h-r")}{houses(XL, Y['house'], "s3-h-l")}
    </svg>
    <div id="s3-lb-plants" class="lbl s" style="right:540px;top:{Y['plant'] + 106}px">محطات التوليد · خارج المدينة</div>
    <div id="s3-lb-vhv" class="lbl s" style="right:540px;top:{cy + 112}px">خطوط الجهد العالي جدا</div>
    <div id="s3-ss-r-name" class="lbl" style="right:{1080 - XR}px;top:{Y['ss'] + 142}px">أولاد حدو</div>
    <div id="s3-ss-l-name" class="lbl" style="right:{1080 - XL}px;top:{Y['ss'] + 142}px">دار بوعزة</div>
    <div id="s3-tag" class="lbl" style="right:540px;top:{Y['ss'] + 22}px"><span class="tag">حسب <span class="lat">Le360</span></span></div>
    <div id="s3-lb-ss" class="lbl s" style="right:540px;top:{Y['ss'] + 84}px">محطتا تحويل</div>
    <div id="s3-lb-h" class="lbl s" style="right:540px;top:{Y['house'] + 10}px">الأحياء</div>
    <div id="s3-note">الشركة الجهوية لم تُسمِّ أي محطة رسميا</div>
    <div id="s3-myth"><span class="no" id="s3-no">محطات توليد</span><span>&larr;</span><span id="s3-yes">محطات تحويل</span></div>"""
    t_a, t_c, t_d, t_e, t_f = (T(ph, k) for k in ("s3a", "s3c", "s3d", "s3e", "s3f"))
    js = f"""
      const flows = gsap.utils.toArray("#s3-svg .flow");
      tl.fromTo("#s3-eyebrow, #s3-title", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.5, stagger: 0.1, ease: "power3.out" }}, 0);
      tl.fromTo("#s3-plants", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, {t_a + 0.1});
      tl.fromTo("#s3-lb-plants", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, {t_a + 0.3});
      tl.to("#s3-f-pl-r, #s3-f-pl-l", {{ opacity: 1, duration: 0.4 }}, {t_a + 0.6});
      tl.fromTo("#s3-corr", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5 }}, {t_a + 0.7});
      tl.to("#s3-f-in-r, #s3-f-in-l", {{ opacity: 1, duration: 0.4 }}, {T(ph, "s3b", 0.26)});
      tl.to("#s3-f-out-r0, #s3-f-out-r1, #s3-f-out-r2, #s3-f-out-l0, #s3-f-out-l1, #s3-f-out-l2", {{ opacity: 1, duration: 0.4 }}, {T(ph, "s3b", 0.7)});
      tl.fromTo("#s3-lb-vhv", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, {t_a + 0.9});
      tl.fromTo("#s3-ss-r", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, {T(ph, "s3b", 0.28)});
      tl.fromTo("#s3-ss-r-name", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.35 }}, {T(ph, "s3b", 0.3)});
      tl.fromTo("#s3-ss-l", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, {T(ph, "s3b", 0.42)});
      tl.fromTo("#s3-ss-l-name", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.35 }}, {T(ph, "s3b", 0.44)});
      tl.fromTo("#s3-tag", {{ opacity: 0, scale: 0.9 }}, {{ opacity: 1, scale: 1, duration: 0.4, ease: "back.out(1.6)" }}, {T(ph, "s3b", 0.5)});
      tl.fromTo("#s3-h-r, #s3-h-l, #s3-lb-h", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.5, stagger: 0.1, ease: "power3.out" }}, {T(ph, "s3b", 0.72)});
      tl.fromTo("#s3-note", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, {t_c});
      tl.to("#s3-note", {{ opacity: 0, duration: 0.3 }}, {t_d - 0.1});
      tl.fromTo("#s3-myth", {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }}, {t_d});
      tl.fromTo("#s3-no", {{ "--strike": 0 }}, {{ "--strike": 1, duration: 0.35, ease: "power2.out" }}, {T(ph, "s3d", 0.45)});
      tl.fromTo("#s3-lb-ss", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.35 }}, {T(ph, "s3d", 0.8)});
      tl.to(flows, {{ opacity: 1, duration: 0.4, stagger: 0.05 }}, {t_e});
      tl.fromTo(flows, {{ strokeDashoffset: 0 }}, {{ strokeDashoffset: -280, duration: {max(4.0, dur - t_e):.2f}, ease: "none" }}, {t_e});
      tl.to(".s3-h-r-win, .s3-h-l-win", {{ opacity: 1, duration: 0.4, stagger: 0.04 }}, {T(ph, "s3e", 0.7)});
      const cut = {T(ph, "s3f", 0.22)};
      tl.set("#s3-cut-r, #s3-cut-l", {{ opacity: 1 }}, cut);
      tl.to("#s3-f-in-r-a, #s3-f-in-l-a", {{ opacity: 0, duration: 0.15 }}, cut);
      tl.to("#s3-f-in-r, #s3-f-in-l", {{ stroke: "#F25C54", duration: 0.15 }}, cut);
      tl.to("#s3-ss-r-led, #s3-ss-l-led", {{ opacity: 0.12, duration: 0.25 }}, {T(ph, "s3f", 0.45)});
      tl.to("[id^='s3-f-out'][id$='-a']", {{ opacity: 0, duration: 0.3 }}, {T(ph, "s3f", 0.5)});
      tl.to(".s3-h-r-win, .s3-h-l-win", {{ opacity: 0.1, duration: 0.25, stagger: 0.06 }}, {T(ph, "s3f", 0.72)});"""
    return tpl("s3", css, body, js), dur


# ------------------------------------------------------------------------------------------- S4
def s4():
    ph, dur, mk = cues("s4")
    css = """
    #s4-hyp { top: 172px; } #s4-title { top: 252px; font-size: 58px; }
    #s4-svg { position: absolute; left: 0; top: 0; width: 1080px; height: 1500px; overflow: visible; }
    .cond { fill: none; stroke: #93CDBB; stroke-width: 5; stroke-linecap: round; }
    .cur { fill: none; stroke: #F4A62A; stroke-width: 5; stroke-linecap: round; stroke-dasharray: 8 22; }
    .wind { stroke: #93A4A7; stroke-width: 3; stroke-linecap: round; opacity: 0; }
    #s4-sc { position: absolute; transform: translate(50%, 0); }
    #s4-trip { position: absolute; right: 64px; top: 990px; width: 600px; text-align: right; }
    #s4-trip b { display: block; font: 700 38px/1.25 "Plex Arabic"; color: #E8EEEC; }
    #s4-trip span { display: block; font: 600 32px/1.35 "Plex Arabic"; color: #93A4A7; margin-top: 6px; }
    #s4-other { position: absolute; left: 64px; right: 64px; top: 960px; height: 250px; display: flex; gap: 24px; }
    #s4-other .o { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px; }
    #s4-other .o span { font: 700 36px/1.2 "Plex Arabic"; color: #E8EEEC; text-align: center; }
    #s4-other .k { font: 600 30px/1 "Plex Arabic"; color: #93A4A7; }
    #s4-spark, #s4-sc, #s4-trip, #s4-other, #s4-breaker { opacity: 0; }
    #s4-lb-h { position: absolute; left: 0; right: 0; top: 1392px; text-align: center; font: 600 30px/1 "Plex Arabic"; color: #93A4A7; }
"""
    body = f"""    <div class="grid"></div>
    <div id="s4-hyp" class="hyp"><b>?</b><span>فرضية – غير مؤكدة</span></div>
    <div id="s4-title" class="title">إلا تلاقاو سلكين فالريح</div>
    <svg id="s4-svg" viewBox="0 0 1080 1500">
      <g id="s4-winds">{''.join(f'<path class="wind" id="s4-wd{i}" d="M {1000 + (i % 2) * 40} {390 + i * 70} H {860 + (i % 2) * 40}"/>' for i in range(6))}</g>
      {pylon(110, 420, 480, 1.7)}{pylon(970, 420, 480, 1.7)}
      <path d="M 66 440 H 154 M 66 510 H 154 M 926 440 H 1014 M 926 510 H 1014" stroke="#93CDBB" stroke-width="4"/>
      <path id="s4-c1" class="cond" d="M 110 440 Q 540 680 970 440"/>
      <path id="s4-c2" class="cond" d="M 110 510 Q 540 750 970 510"/>
      <path id="s4-i1" class="cur" d="M 110 440 Q 540 680 970 440"/>
      <path id="s4-i2" class="cur" d="M 110 510 Q 540 750 970 510"/>
      <g transform="translate(540,596)"><g id="s4-spark">
        <circle r="44" fill="none" stroke="#F25C54" stroke-width="5"/>
        <path d="M0 -50 L11 -13 L50 -17 L17 6 L35 44 L0 20 L-33 44 L-17 6 L-50 -15 L-11 -13 Z" fill="#F4A62A"/>
        <circle r="15" fill="#FFFFFF"/>
      </g></g>
      <g transform="translate(150,980)"><g id="s4-breaker">
        <rect x="0" y="0" width="130" height="160" rx="10" fill="#141D21" stroke="#93CDBB" stroke-width="3.5"/>
        <circle cx="65" cy="104" r="11" fill="#93CDBB"/>
        <path id="s4-lever" d="M65 104 L65 34" stroke="#E8EEEC" stroke-width="11" stroke-linecap="round"/>
      </g></g>
      {houses(540, 1300, "s4-h", n=6, gap=150, cls="s4-win")}
    </svg>
    <div id="s4-sc" style="right:540px;top:676px"><span class="tag" style="color:#F25C54;border-color:#F25C54">قصر دارة · تيار قوي بزاف</span></div>
    <div id="s4-trip"><b>أجهزة الحماية كتفصل الخط</b><span>فجزء من الثانية، باش ما تتخربش المعدات</span></div>
    <div id="s4-other">
      <div id="s4-o1" class="o card"><svg width="96" height="96" viewBox="0 0 90 90"><path d="M52 4 L22 50 H42 L32 86 L70 34 H48 L60 4 Z" fill="#F4A62A"/></svg><span>صاعقة</span><div class="k">احتمال آخر</div></div>
      <div id="s4-o2" class="o card"><svg width="128" height="96" viewBox="0 0 120 90" fill="none" stroke-linecap="round"><path d="M4 30 Q60 50 116 30" stroke="#93A4A7" stroke-width="4"/><path d="M30 8 L62 44 L100 70 M62 44 L58 74 M48 28 L32 40" stroke="#93CDBB" stroke-width="6"/></svg><span>سقوط جسم على الخط</span><div class="k">احتمال آخر</div></div>
    </div>
    <div id="s4-lb-h">الأحياء اللي كيغذيها الخط</div>"""
    t_touch = mk.get("touch", T(ph, "s4b", 0.3))
    t_trip = T(ph, "s4c", 0.3)
    t_off = T(ph, "s4c", 0.85)
    js = f"""
      tl.fromTo("#s4-hyp", {{ opacity: 0, scale: 0.92 }}, {{ opacity: 1, scale: 1, duration: 0.45, ease: "back.out(1.7)" }}, 0);
      tl.fromTo("#s4-title", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, 0.15);
      tl.fromTo("#s4-svg", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5 }}, 0.2);
      tl.fromTo("#s4-lb-h", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, 0.6);
      tl.fromTo("#s4-i1, #s4-i2", {{ strokeDashoffset: 0 }}, {{ strokeDashoffset: -600, duration: {t_trip + 0.1:.2f}, ease: "none" }}, 0);
      gsap.utils.toArray("#s4-winds .wind").forEach((w, i) => {{
        tl.fromTo(w, {{ x: 120, opacity: 0 }}, {{ x: -900, opacity: 0.7, duration: 1.4, ease: "none", repeat: {int(dur / 1.4) + 1} }}, 0.18 * i + {T(ph, "s4a", 0.2)});
      }});
      // galloping: amplitude grows until the two conductors meet at mid-span
      const st = {{ t: 0 }};
      const c1 = document.querySelector("#s4-c1"), c2 = document.querySelector("#s4-c2");
      const i1 = document.querySelector("#s4-i1"), i2 = document.querySelector("#s4-i2");
      const T0 = {T(ph, "s4a", 0.4)}, T1 = {t_touch};
      function sway(t) {{
        let a1 = 0, a2 = 0;
        if (t > T0 && t < T1) {{
          const u = (t - T0) / (T1 - T0), amp = 18 + 44 * u;
          a1 = Math.sin((t - T0) * 5.2) * amp;
          a2 = -Math.sin((t - T0) * 5.2 + 0.9) * amp;
          if (u > 0.82) {{ const v = (u - 0.82) / 0.18; a1 = a1 * (1 - v) + 35 * v; a2 = a2 * (1 - v) - 35 * v; }}
        }} else if (t >= T1) {{
          const k = Math.max(0, 1 - (t - T1) / 2.5);
          a1 = 35 * k + Math.sin((t - T1) * 4) * 10 * k; a2 = -35 * k - Math.sin((t - T1) * 4 + 0.6) * 10 * k;
        }}
        const d1 = `M 110 440 Q 540 ${{680 + a1 * 2}} 970 440`, d2 = `M 110 510 Q 540 ${{750 + a2 * 2}} 970 510`;
        c1.setAttribute("d", d1); i1.setAttribute("d", d1); c2.setAttribute("d", d2); i2.setAttribute("d", d2);
      }}
      tl.fromTo(st, {{ t: 0 }}, {{ t: {dur}, duration: {dur}, ease: "none", onUpdate: () => sway(st.t) }}, 0);
      tl.set("#s4-spark", {{ opacity: 1, scale: 0.4, transformOrigin: "50% 50%" }}, {t_touch});
      tl.to("#s4-spark", {{ scale: 1.25, duration: 0.18, ease: "power2.out" }}, {t_touch});
      tl.to("#s4-spark", {{ opacity: 0, duration: 0.5 }}, {t_touch + 0.5});
      tl.set("#s4-spark", {{ opacity: 0.9, scale: 0.8 }}, {t_touch + 1.1});
      tl.to("#s4-spark", {{ opacity: 0, duration: 0.3 }}, {t_touch + 1.25});
      tl.fromTo("#s4-sc", {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }}, {t_touch + 0.15});
      tl.to("#s4-i1, #s4-i2", {{ stroke: "#FFFFFF", strokeWidth: 7, duration: 0.15 }}, {T(ph, "s4b", 0.7)});
      tl.fromTo("#s4-breaker", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }}, {t_trip - 0.6});
      tl.fromTo("#s4-lever", {{ rotation: 0, transformOrigin: "50% 100%" }}, {{ rotation: 90, duration: 0.18, ease: "power2.in" }}, {t_trip});
      tl.to("#s4-i1, #s4-i2", {{ opacity: 0, duration: 0.12 }}, {t_trip + 0.12});
      tl.to("#s4-sc", {{ opacity: 0, duration: 0.3 }}, {t_trip + 0.2});
      tl.fromTo("#s4-trip", {{ opacity: 0, x: -16 }}, {{ opacity: 1, x: 0, duration: 0.45, ease: "power3.out" }}, {t_trip + 0.15});
      tl.to(".s4-win", {{ opacity: 0.08, duration: 0.2, stagger: 0.05 }}, {t_off});
      tl.to("#s4-trip, #s4-breaker", {{ opacity: 0, duration: 0.3 }}, {T(ph, "s4e", 0.05)});
      tl.set("#s4-other", {{ opacity: 1 }}, {T(ph, "s4e", 0.1)});
      tl.fromTo("#s4-o1", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }}, {T(ph, "s4e", 0.45)});
      tl.fromTo("#s4-o2", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }}, {T(ph, "s4e", 0.7)});
      tl.to("#s4-hyp", {{ scale: 1.08, duration: 0.2, yoyo: true, repeat: 1, ease: "power2.out" }}, {T(ph, "s4d", 0.05)});"""
    return tpl("s4", css, body, js), dur


# ------------------------------------------------------------------------------------------- S5
BULLETS = ["ربط المحطات بأكثر من خط تغذية", "فحص وصيانة الخطوط والعوازل قبل العواصف", "حماية ضد الصواعق",
           "مراقبة الشبكة حسب الإنذارات الجوية", "مولدات احتياطية للمرافق الحيوية"]
ICONS = [
    '<path d="M20 10 V60 M100 10 V60" stroke="#93A4A7" stroke-width="5"/><path d="M20 60 Q20 80 60 80 M100 60 Q100 80 60 80" fill="none" stroke="#F4A62A" stroke-width="5"/><rect x="34" y="80" width="52" height="40" rx="5" fill="#141D21" stroke="#93CDBB" stroke-width="4"/>',
    '<path d="M40 10 V90" stroke="#93A4A7" stroke-width="4"/><g fill="#141D21" stroke="#93CDBB" stroke-width="4"><ellipse cx="40" cy="34" rx="18" ry="6"/><ellipse cx="40" cy="50" rx="18" ry="6"/><ellipse cx="40" cy="66" rx="18" ry="6"/></g><circle cx="80" cy="56" r="22" fill="none" stroke="#E8EEEC" stroke-width="5"/><path d="M96 72 L114 92" stroke="#E8EEEC" stroke-width="7" stroke-linecap="round"/>',
    '<path d="M60 30 V116 M44 116 H76" stroke="#93CDBB" stroke-width="5"/><path d="M60 30 L54 12 M60 30 L66 12" stroke="#93CDBB" stroke-width="4"/><path d="M96 4 L80 34 H92 L84 58 L108 26 H96 L104 4 Z" fill="#F4A62A"/>',
    '<rect x="10" y="16" width="100" height="72" rx="8" fill="#141D21" stroke="#93CDBB" stroke-width="4"/><path d="M60 30 L84 74 H36 Z" fill="none" stroke="#F4A62A" stroke-width="5" stroke-linejoin="round"/><path d="M60 44 V58 M60 64 V66" stroke="#F4A62A" stroke-width="5" stroke-linecap="round"/><path d="M44 102 H76 M60 88 V102" stroke="#93CDBB" stroke-width="4"/>',
    '<rect x="10" y="36" width="100" height="62" rx="8" fill="#141D21" stroke="#93CDBB" stroke-width="4"/><circle cx="40" cy="67" r="16" fill="none" stroke="#93CDBB" stroke-width="4"/><path d="M84 52 L72 70 H82 L76 86 L94 62 H84 L90 52 Z" fill="#F4A62A"/><path d="M20 98 V110 M100 98 V110" stroke="#93CDBB" stroke-width="5"/>',
]


def s5():
    ph, dur, mk = cues("s5")
    css = """
    #s5-eyebrow { top: 178px; } #s5-title { top: 224px; font-size: 58px; }
    #s5-steps { position: absolute; right: 64px; left: 64px; top: 330px; display: flex; gap: 18px; justify-content: flex-start; direction: rtl; }
    .st { width: 64px; height: 64px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
      font: 700 32px/1 "Space Grotesk"; color: #6E8186; border: 2px solid #26343B; background: #141D21; }
    .bl { position: absolute; right: 64px; left: 64px; top: 440px; display: flex; flex-direction: column; align-items: flex-start; gap: 22px; }
    .bl .tx { font: 700 80px/1.16 "Plex Arabic"; color: #E8EEEC; text-align: right; }
    #s5-list { position: absolute; right: 64px; left: 64px; top: 960px; display: flex; flex-direction: column; gap: 12px; }
    .li { display: flex; align-items: center; gap: 16px; padding: 12px 20px 16px; font: 700 34px/1.2 "Plex Arabic"; color: #E8EEEC; }
    .li b { flex: 0 0 auto; width: 48px; height: 48px; border-radius: 50%; border: 2px solid #93CDBB; color: #93CDBB;
      font: 700 28px/44px "Space Grotesk"; text-align: center; }
    .bl, .li { opacity: 0; }
"""
    steps = "".join(f'<div id="s5-st{i}" class="st">{i + 1}</div>' for i in range(5))
    bl = "".join(f'<div id="s5-b{i}" class="bl"><svg width="190" height="180" viewBox="0 0 120 120" fill="none">{ICONS[i]}</svg><div class="tx ink">{BULLETS[i]}</div></div>' for i in range(5))
    li = "".join(f'<div id="s5-l{i}" class="li card"><b>{i + 1}</b><span>{BULLETS[i]}</span></div>' for i in range(5))
    body = f"""    <div class="grid"></div>
    <div id="s5-eyebrow" class="eyebrow"><i></i><span>باش ما يتعاودش</span></div>
    <div id="s5-title" class="title">حلول معروفة</div>
    <div id="s5-steps">{steps}</div>
    {bl}
    <div id="s5-list" data-hold>{li}</div>"""
    starts = [T(ph, k) for k in ("s5b", "s5c", "s5d", "s5e", "s5f")]
    bj = []
    for i, t in enumerate(starts):
        if i > 0:
            bj += [f'tl.to("#s5-b{i - 1}", {{ opacity: 0, y: -18, duration: 0.3, ease: "power2.in" }}, {t - 0.05:.3f});',
                   f'tl.to("#s5-st{i - 1}", {{ backgroundColor: "#141D21", color: "#93CDBB", borderColor: "#93CDBB", duration: 0.25 }}, {t - 0.05:.3f});',
                   f'tl.fromTo("#s5-l{i - 1}", {{ opacity: 0, x: 24 }}, {{ opacity: 1, x: 0, duration: 0.4, ease: "power3.out" }}, {t + 0.05:.3f});']
        bj += [f'tl.to("#s5-st{i}", {{ backgroundColor: "#F4A62A", color: "#0D1316", borderColor: "#F4A62A", duration: 0.25 }}, {t});',
               f'tl.fromTo("#s5-b{i}", {{ opacity: 0, y: 26 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, {t + 0.1:.3f});']
    bul_js = "\n".join("      " + x for x in bj)
    fin = round(min(dur - 1.9, T(ph, "s5f") + (ph["s5f"][1] - ph["s5f"][0]) + 0.6), 3)
    js = f"""
      tl.fromTo("#s5-eyebrow, #s5-title", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.5, stagger: 0.1, ease: "power3.out" }}, 0);
      tl.fromTo("#s5-steps .st", {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: 0.35, stagger: 0.06, ease: "power3.out" }}, {T(ph, "s5a", 0.4)});
{bul_js}
      tl.to("#s5-st4", {{ backgroundColor: "#141D21", color: "#93CDBB", borderColor: "#93CDBB", duration: 0.25 }}, {fin});
      tl.fromTo("#s5-l4", {{ opacity: 0, x: 24 }}, {{ opacity: 1, x: 0, duration: 0.4, ease: "power3.out" }}, {fin});"""
    return tpl("s5", css, body, js), dur


# ------------------------------------------------------------------------------------------- S6
def s6():
    ph, dur, mk = cues("s6")
    css = """
    #s6-hyp { top: 172px; }
    #s6-ctx { position: absolute; right: 64px; left: 64px; top: 272px; font: 600 36px/1.3 "Plex Arabic"; color: #93A4A7; text-align: right; }
    #s6-q { top: 330px; font-size: 76px; line-height: 1.16; }
    #s6-ans { position: absolute; right: 64px; top: 548px; font: 700 42px/1 "Plex Arabic"; color: #F25C54; }
    #s6-lead { position: absolute; right: 64px; top: 640px; font: 600 34px/1 "Plex Arabic"; color: #93A4A7; }
    #s6-list { position: absolute; right: 64px; left: 64px; top: 700px; display: flex; flex-direction: column; gap: 18px; }
    .pos { display: flex; align-items: center; gap: 18px; padding: 22px 26px 28px; font: 700 44px/1.2 "Plex Arabic"; color: #E8EEEC; }
    .pos i { flex: 0 0 auto; width: 18px; height: 18px; border-radius: 50%; border: 3.5px solid #93A4A7; }
    #s6-wait { position: absolute; right: 64px; left: 64px; top: 1150px; display: flex; align-items: center; gap: 22px;
      padding: 26px 30px 32px; font: 700 54px/1.1 "Plex Arabic"; color: #E8EEEC; border-color: #93CDBB; }
"""
    body = """    <div class="grid"></div>
    <div id="s6-hyp" class="hyp"><b>?</b><span>فرضية – غير مؤكدة</span></div>
    <div id="s6-ctx">الدار البيضاء عرفات رياح قوية فالماضي</div>
    <div id="s6-q" class="title ink">علاش هاد المرة تأثر أكثر من موقع؟</div>
    <div id="s6-ans">الجواب ما مؤكدش</div>
    <div id="s6-lead">من الاحتمالات:</div>
    <div id="s6-list">
      <div id="s6-p1" class="pos card"><i></i><span>اجتماع الرياح مع الرعد</span></div>
      <div id="s6-p2" class="pos card"><i></i><span>وقوع العطل فوقت الذروة</span></div>
      <div id="s6-p3" class="pos card"><i></i><span>خط مشترك كيغذي محطتين فنفس الوقت</span></div>
    </div>
    <div id="s6-wait" class="card" data-hold><svg width="64" height="76" viewBox="0 0 64 76" fill="none" stroke="#93CDBB" stroke-width="4" stroke-linejoin="round"><path d="M6 4 H42 L58 20 V72 H6 Z"/><path d="M42 4 V20 H58"/><path d="M16 36 H48 M16 48 H48 M16 60 H36" stroke-linecap="round"/></svg><span>ننتظرو تقرير رسمي</span></div>"""
    js = f"""
      tl.fromTo("#s6-hyp", {{ opacity: 0, scale: 0.92 }}, {{ opacity: 1, scale: 1, duration: 0.45, ease: "back.out(1.7)" }}, 0);
      tl.fromTo("#s6-ctx", {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }}, {T(ph, "s6a", 0.3)});
      tl.fromTo("#s6-q", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, {T(ph, "s6b")});
      tl.fromTo("#s6-ans", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.35 }}, {T(ph, "s6c")});
      tl.fromTo("#s6-lead", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.35 }}, {T(ph, "s6d")});
      tl.fromTo("#s6-p1", {{ opacity: 0, x: 24 }}, {{ opacity: 1, x: 0, duration: 0.45, ease: "power3.out" }}, {T(ph, "s6d", 0.4)});
      tl.fromTo("#s6-p2", {{ opacity: 0, x: 24 }}, {{ opacity: 1, x: 0, duration: 0.45, ease: "power3.out" }}, {T(ph, "s6e", 0.05)});
      tl.fromTo("#s6-p3", {{ opacity: 0, x: 24 }}, {{ opacity: 1, x: 0, duration: 0.45, ease: "power3.out" }}, {T(ph, "s6f", 0.05)});
      tl.fromTo("#s6-wait", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, {T(ph, "s6g")});"""
    return tpl("s6", css, body, js), dur


# ------------------------------------------------------------------------------------------- END
def end():
    dur = CUES.get("end", {}).get("duration", 7.0)
    css = """
    #end-eyebrow { top: 520px; }
    #end-list { position: absolute; right: 64px; left: 64px; top: 590px; display: flex; flex-direction: column; gap: 18px; }
    .src { font: 700 46px/1.25 "Plex Arabic"; color: #E8EEEC; padding: 18px 26px 24px; }
    .src .lat { font-family: "Space Grotesk"; direction: ltr; unicode-bidi: isolate; }
    #end-credits { position: absolute; right: 64px; left: 64px; top: 1130px; font: 600 28px/1.5 "Plex Arabic"; color: #93A4A7; text-align: right; }
    #end-credits .lat { font-family: "Space Grotesk"; direction: ltr; unicode-bidi: isolate; }
"""
    body = """    <div class="grid"></div>
    <div id="end-eyebrow" class="eyebrow"><i></i><span>المصادر</span></div>
    <div id="end-list">
      <div id="end-s1" class="src card">بلاغ <span class="lat">SRM</span> الدار البيضاء–سطات</div>
      <div id="end-s2" class="src card"><span class="lat">Le360</span></div>
      <div id="end-s3" class="src card"><span class="lat">Médias24</span></div>
      <div id="end-s4" class="src card"><span class="lat">Hespress</span></div>
    </div>
    <div id="end-credits">صورة الخريطة: <span class="lat">Esri, Maxar, Earthstar Geographics</span><br>مواقع الأحياء: <span class="lat">© OpenStreetMap</span></div>"""
    js = """
      tl.fromTo("#end-eyebrow", { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }, 0.1);
      tl.fromTo("#end-list .src", { opacity: 0, y: 18 }, { opacity: 1, y: 0, duration: 0.45, stagger: 0.18, ease: "power3.out" }, 0.3);
      tl.fromTo("#end-credits", { opacity: 0 }, { opacity: 1, duration: 0.5 }, 1.4);"""
    return tpl("end", css, body, js), dur


if __name__ == "__main__":
    (ROOT / "compositions").mkdir(exist_ok=True)
    durs = {}
    for name, fn in (("s1", s1), ("s3", s3), ("s4", s4), ("s5", s5), ("s6", s6), ("end", end)):
        html, d = fn()
        (ROOT / f"compositions/{name}.html").write_text(html)
        durs[name] = d
    print(json.dumps(durs))
