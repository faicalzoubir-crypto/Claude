#!/usr/bin/env python3
"""Build the scene files (compositions/s1, s3, s4, s5, s6, end) from data/cues.json.

Cues are scene-local phrase windows from the voice (tools/voice.py); without them every phrase is
estimated from its word count, so the layout can be checked before the voice exists.
Avatar framing (where the head sits in the 1080×1920 avatar video) is in AV below.

  python3 tools/scenes_build.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = json.loads((ROOT / "script.json").read_text())
CUES = json.loads((ROOT / "data/cues.json").read_text()) if (ROOT / "data/cues.json").exists() else {}

# Avatar video framing (px in the 1080×1920 avatar frame): top of the hair and the chin.
AV = {"head_top": 560, "chin": 860}
AV.update(CUES.get("avatar", {}))


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


def avatar_file(sid):
    p = ROOT / f"assets/avatar/{sid}.mp4"
    return p.exists()


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
    .muted { color: #93A4A7; }
    .card { background: #141D21; border: 1.5px solid #26343B; border-radius: 14px; }
    .lbl { position: absolute; transform: translate(50%, 0); white-space: nowrap; text-align: center;
      font: 700 32px/1.15 "Plex Arabic"; color: #E8EEEC; }
    .lbl.s { font: 600 28px/1.2 "Plex Arabic"; color: #93A4A7; }
    .tag { display: inline-block; font: 700 28px/1 "Plex Arabic"; color: #F4A62A; border: 2px solid #F4A62A;
      border-radius: 10px; padding: 6px 12px 10px; direction: rtl; }
    .tag .lat { font: 700 26px/1 "Space Grotesk"; direction: ltr; unicode-bidi: isolate; }
"""


def avatar_block(sid, dur, mode):
    """mode: full | low (scaled, anchored at the bottom) | pip."""
    has = avatar_file(sid)
    src = f"assets/avatar/{sid}.mp4"
    if mode == "full":
        box = "left:0;top:0;width:1080px;height:1920px;"
        inner = (f'<video id="{sid}-av" class="clip" src="{src}" muted playsinline data-start="0" data-duration="{dur}" '
                 f'data-track-index="1" style="position:absolute;{box}object-fit:cover;z-index:1"></video>') if has else \
                f'<div id="{sid}-av-ph" style="position:absolute;{box}z-index:1">{placeholder_svg()}</div>'
        return inner
    if mode == "low":
        k = 0.62 if sid in ("s4", "s5") else 0.74
        w, h = 1080 * k, 1920 * k
        left, top = (1080 - w) / 2, 1920 - h
        mask = ("-webkit-mask-image: linear-gradient(to right, transparent 0, #000 14%, #000 86%, transparent 100%),"
                " linear-gradient(to bottom, transparent 0, #000 12%);"
                " -webkit-mask-composite: source-in; mask-composite: intersect;")
        box = f"left:{left:.0f}px;top:{top:.0f}px;width:{w:.0f}px;height:{h:.0f}px;"
        if has:
            return (f'<video id="{sid}-av" class="clip" src="{src}" muted playsinline data-start="0" data-duration="{dur}" '
                    f'data-track-index="1" style="position:absolute;{box}object-fit:cover;z-index:1;{mask}"></video>')
        return f'<div id="{sid}-av-ph" style="position:absolute;{box}z-index:1;{mask}">{placeholder_svg()}</div>'
    # pip: 330 × 372 window at the bottom centre, above the captions
    win = "left:375px;top:1090px;width:330px;height:372px;"
    k = 0.62
    vw, vh = 1080 * k, 1920 * k
    face_y = (AV["head_top"] + AV["chin"]) / 2 * k
    vx, vy = (330 - vw) / 2, 372 * 0.46 - face_y
    vbox = f"left:{vx:.0f}px;top:{vy:.0f}px;width:{vw:.0f}px;height:{vh:.0f}px;"
    inner = (f'<video id="{sid}-av" class="clip" src="{src}" muted playsinline data-start="0" data-duration="{dur}" '
             f'data-track-index="1" style="position:absolute;{vbox}object-fit:cover"></video>') if has else \
            f'<div id="{sid}-av-ph" style="position:absolute;{vbox}">{placeholder_svg()}</div>'
    return (f'<div id="{sid}-pip" style="position:absolute;{win}overflow:hidden;border-radius:14px;'
            f'border:1.5px solid #26343B;background:#0D1316;z-index:5">{inner}</div>')


def placeholder_svg():
    ht, ch = AV["head_top"], AV["chin"]
    hr = (ch - ht) / 2
    cy = ht + hr
    return (f'<svg viewBox="0 0 1080 1920" width="100%" height="100%" style="position:absolute;inset:0">'
            f'<ellipse cx="540" cy="{cy}" rx="{hr * 0.8:.0f}" ry="{hr:.0f}" fill="#22303A"/>'
            f'<path d="M 230 1920 C 240 {ch + 140} 360 {ch + 70} 540 {ch + 60} C 720 {ch + 70} 840 {ch + 140} 850 1920 Z" fill="#1B2730"/>'
            f'<text x="540" y="{ch + 300}" fill="#6E8186" font-size="40" text-anchor="middle" font-family="Space Grotesk">AVATAR</text></svg>')


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


# ------------------------------------------------------------------------------------------- S1
def s1():
    ph, dur, mk = cues("s1")
    t_time = mk.get("time_word", T(ph, "s1a", 0.72))
    css = """
    #s1-date { top: 178px; }
    #s1-title { top: 228px; font-size: 64px; }
    #s1-clock { position: absolute; left: 0; right: 0; top: 322px; text-align: center; direction: ltr;
      font: 700 138px/1 "Space Grotesk"; color: #F4A62A; letter-spacing: -0.02em; }
    #s1-fault { position: absolute; left: 0; right: 0; top: 478px; text-align: center; font: 600 32px/1 "Plex Arabic"; color: #E8EEEC; }
    .wx { position: absolute; top: 640px; display: flex; flex-direction: column; align-items: center; gap: 10px; width: 250px; }
    .wx span { font: 700 32px/1.1 "Plex Arabic"; color: #E8EEEC; }
    #s1-wind { left: 64px; } #s1-storm { right: 64px; }
    #s1-flash { position: absolute; inset: 0; background: #E8EEEC; opacity: 0; z-index: 3; pointer-events: none; }
    #s1-ai { position: absolute; right: 64px; top: 1430px; font: 600 28px/1 "Plex Arabic"; color: #93A4A7;
      background: rgba(13,19,22,.86); border: 1.5px solid #26343B; border-radius: 10px; padding: 6px 12px 10px; }
"""
    body = f"""    {avatar_block("s1", dur, "full")}
    <div id="s1-flash"></div>
    <div id="s1-date" class="eyebrow" style="z-index:4"><i></i><span>الأربعاء 11 نونبر 2026</span></div>
    <div id="s1-title" class="title ink" style="z-index:4">انقطاع الكهرباء بالدار البيضاء</div>
    <div id="s1-clock" class="ink" style="z-index:4">16:48</div>
    <div id="s1-fault" class="ink" style="z-index:4">عطل فخطوط الجهد العالي جدا</div>
    <div id="s1-wind" class="wx" style="z-index:4">
      <svg width="120" height="90" viewBox="0 0 120 90" fill="none" stroke="#93CDBB" stroke-width="7" stroke-linecap="round">
        <path id="s1-w1" d="M8 28 H78 a14 14 0 1 0 -14 -14" pathLength="100"/>
        <path id="s1-w2" d="M8 50 H96 a14 14 0 1 1 -14 14" pathLength="100"/>
        <path id="s1-w3" d="M20 72 H60" pathLength="100"/>
      </svg><span>رياح قوية</span></div>
    <div id="s1-storm" class="wx" style="z-index:4">
      <svg width="120" height="90" viewBox="0 0 120 90" fill="none">
        <path d="M30 52 a18 18 0 0 1 6 -35 a26 26 0 0 1 48 6 a16 16 0 0 1 4 31 Z" stroke="#93CDBB" stroke-width="7" stroke-linejoin="round"/>
        <path id="s1-bolt" d="M62 50 L50 72 H62 L54 90 L76 62 H64 L72 50 Z" fill="#E8EEEC"/>
      </svg><span>عواصف رعدية</span></div>
    <div id="s1-ai" style="z-index:4">مقدِّم افتراضي مولَّد بالذكاء الاصطناعي</div>"""
    js = f"""
      tl.fromTo("#s1-date", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, 0);
      tl.fromTo("#s1-title", {{ opacity: 0, y: 18 }}, {{ opacity: 1, y: 0, duration: 0.55, ease: "power3.out" }}, 0);
      tl.fromTo("#s1-ai", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, 0.3);
      tl.fromTo("#s1-clock", {{ opacity: 0, scale: 0.86 }}, {{ opacity: 1, scale: 1, duration: 0.42, ease: "back.out(1.6)" }}, {t_time - 0.12});
      tl.fromTo("#s1-fault", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }}, {T(ph, "s1b", 0.25)});
      tl.fromTo("#s1-wind", {{ opacity: 0, x: 24 }}, {{ opacity: 1, x: 0, duration: 0.5, ease: "power3.out" }}, {T(ph, "s1c", 0.1)});
      tl.fromTo("#s1-w1, #s1-w2, #s1-w3", {{ strokeDasharray: "100 120", strokeDashoffset: 110 }}, {{ strokeDashoffset: 0, duration: 0.6, stagger: 0.12, ease: "power2.out" }}, {T(ph, "s1c", 0.1)});
      tl.fromTo("#s1-storm", {{ opacity: 0, x: -24 }}, {{ opacity: 1, x: 0, duration: 0.5, ease: "power3.out" }}, {T(ph, "s1c", 0.5)});
      // one lightning flicker on «رعدية»
      const f = {T(ph, "s1c", 0.78)};
      tl.set("#s1-flash", {{ opacity: 0.16 }}, f); tl.set("#s1-flash", {{ opacity: 0 }}, f + 0.067);
      tl.set("#s1-flash", {{ opacity: 0.09 }}, f + 0.167); tl.set("#s1-flash", {{ opacity: 0 }}, f + 0.233);
      tl.fromTo("#s1-bolt", {{ opacity: 0.25 }}, {{ opacity: 1, duration: 0.05 }}, f);"""
    return tpl("s1", css, body, js), dur


# ------------------------------------------------------------------------------------------- S3
def pylon(x, y, h=110, sc=1.0):
    w = 46 * sc
    return (f'<g transform="translate({x},{y})" stroke="#93CDBB" stroke-width="3" fill="none">'
            f'<path d="M{-w/2} {h} L-6 0 L6 0 L{w/2} {h}"/><path d="M-30 14 H30 M-22 34 H22"/>'
            f'<path d="M{-w*0.38} {h*0.62} L{w*0.3} {h*0.36} M{w*0.38} {h*0.62} L{-w*0.3} {h*0.36} M{-w*0.46} {h*0.88} L{w*0.4} {h*0.62} M{w*0.46} {h*0.88} L{-w*0.4} {h*0.62}"/></g>')


def plant(x, y, idp):
    return (f'<g id="{idp}" transform="translate({x},{y})" stroke="#93CDBB" stroke-width="3.5" fill="#141D21" stroke-linejoin="round">'
            f'<path d="M-70 90 V40 L-40 20 V40 L-10 20 V40 L20 20 V90 Z"/>'
            f'<path d="M30 90 C36 60 34 30 26 4 H66 C58 30 56 60 62 90 Z"/>'
            f'<path id="{idp}-steam" d="M40 -4 c-8 -10 8 -16 0 -28 M54 -4 c-8 -10 8 -16 0 -28" fill="none" stroke="#93A4A7" stroke-width="3" stroke-linecap="round"/>'
            f'<path d="M-58 62 h12 M-30 62 h12 M-2 62 h12" stroke-width="5"/></g>')


def substation(x, y, idp):
    return (f'<g transform="translate({x},{y})"><g id="{idp}">'
            f'<rect x="-110" y="0" width="220" height="120" rx="8" fill="#141D21" stroke="#26343B" stroke-width="2"/>'
            f'<path d="M-110 0 V120 H110 V0" fill="none" stroke="#93A4A7" stroke-width="2" stroke-dasharray="2 9"/>'
            f'<g stroke="#93CDBB" stroke-width="3.5" fill="#0D1316" stroke-linejoin="round">'
            f'<rect id="{idp}-tx" x="-46" y="38" width="92" height="64" rx="5"/>'
            f'<path d="M-36 38 V102 M-22 38 V102 M22 38 V102 M36 38 V102" stroke-width="2.5"/>'
            f'<rect x="-30" y="18" width="12" height="20" rx="3"/><rect x="-6" y="14" width="12" height="24" rx="3"/><rect x="18" y="18" width="12" height="20" rx="3"/>'
            f'<path d="M-90 104 V58 H-66 V104 M66 104 V58 H90 V104" fill="none"/></g>'
            f'<circle id="{idp}-led" cx="0" cy="70" r="9" fill="#F4A62A"/></g></g>')


def houses(cx, y, idp):
    out = [f'<g id="{idp}">']
    for i, dx in enumerate((-96, 0, 96)):
        x = cx + dx
        out.append(f'<g transform="translate({x},{y})"><path d="M-36 60 V22 L0 -6 L36 22 V60 Z" fill="#141D21" stroke="#93CDBB" stroke-width="3" stroke-linejoin="round"/>'
                   f'<rect class="{idp}-win" x="-22" y="26" width="16" height="14" rx="2" fill="#F4A62A"/>'
                   f'<rect class="{idp}-win" x="6" y="26" width="16" height="14" rx="2" fill="#F4A62A"/></g>')
    out.append("</g>")
    return "".join(out)


def s3():
    ph, dur, mk = cues("s3")
    # x of the two branches: RTL reading order puts أولاد حدو (named first) on the right, like the map (east)
    XR, XL = 790, 290
    css = """
    #s3-eyebrow { top: 178px; } #s3-title { top: 222px; font-size: 52px; }
    #s3-svg { position: absolute; left: 0; top: 0; width: 1080px; height: 1100px; overflow: visible; }
    .flow { fill: none; stroke: #F4A62A; stroke-width: 5; stroke-linecap: round; stroke-dasharray: 10 18; }
    .wire { fill: none; stroke: #93A4A7; stroke-width: 3; }
    #s3-note { position: absolute; left: 64px; right: 64px; top: 1032px; text-align: center; font: 600 28px/1.25 "Plex Arabic"; color: #93A4A7; }
    #s3-myth { position: absolute; left: 0; right: 0; top: 1026px; display: flex; justify-content: center; gap: 22px; align-items: center;
      font: 700 34px/1 "Plex Arabic"; color: #E8EEEC; }
    #s3-myth .no { color: #93A4A7; position: relative; }
    #s3-myth .no::after { content: ""; position: absolute; left: -6px; right: -6px; top: 52%; height: 4px; background: #F25C54; border-radius: 2px;
      transform-origin: right center; transform: scaleX(var(--strike, 0)); }
"""
    flow_paths = [
        # plants -> corridor -> substations -> houses
        (f"s3-f-pl-r", f"M {XR + 30} 420 V 498"), (f"s3-f-pl-l", f"M {XL - 30} 420 V 498"),
        (f"s3-f-in-r", f"M {XR} 548 V 662"), (f"s3-f-in-l", f"M {XL} 548 V 662"),
    ]
    out_paths = []
    for side, x in (("r", XR), ("l", XL)):
        for j, dx in enumerate((-96, 0, 96)):
            out_paths.append((f"s3-f-out-{side}{j}", f"M {x} 842 C {x} 880 {x + dx} 884 {x + dx} 930"))
    svg_paths = "".join(f'<path id="{i}" class="wire" d="{d}"/><path id="{i}-a" class="flow" d="{d}"/>' for i, d in flow_paths + out_paths)
    body = f"""    <div class="grid"></div>
    <div id="s3-eyebrow" class="eyebrow"><i></i><span>محطات التحويل</span></div>
    <div id="s3-title" class="title">كيفاش كيوصل الضو للحي؟</div>
    <svg id="s3-svg" viewBox="0 0 1080 1100">
      <g id="s3-plants">{plant(XL - 30, 330, "s3-pl-l")}{plant(XR + 30, 330, "s3-pl-r")}</g>
      <g id="s3-corr">
        <path id="s3-c-wire" d="M 120 506 Q 330 536 540 506 Q 750 536 960 506" class="wire" stroke-width="3.5"/>
        <path id="s3-c-flow" d="M 120 506 Q 330 536 540 506 Q 750 536 960 506" class="flow"/>
        {pylon(120, 492, 96)}{pylon(540, 492, 96)}{pylon(960, 492, 96)}
      </g>
      {svg_paths}
      <path id="s3-cut-r" d="M {XR - 22} 596 L {XR + 22} 614 M {XR - 22} 614 L {XR + 22} 596" stroke="#F25C54" stroke-width="6" stroke-linecap="round"/>
      <path id="s3-cut-l" d="M {XL - 22} 596 L {XL + 22} 614 M {XL - 22} 614 L {XL + 22} 596" stroke="#F25C54" stroke-width="6" stroke-linecap="round"/>
      {substation(XR, 662, "s3-ss-r")}{substation(XL, 662, "s3-ss-l")}
      {houses(XR, 936, "s3-h-r")}{houses(XL, 936, "s3-h-l")}
    </svg>
    <div id="s3-lb-plants" class="lbl s" style="right:540px;top:434px">محطات التوليد · خارج المدينة</div>
    <div id="s3-lb-vhv" class="lbl s" style="right:540px;top:598px">خطوط الجهد العالي جدا</div>
    <div id="s3-ss-r-name" class="lbl" style="right:{1080 - XR}px;top:796px">أولاد حدو</div>
    <div id="s3-ss-l-name" class="lbl" style="right:{1080 - XL}px;top:796px">دار بوعزة</div>
    <div id="s3-tag" class="lbl" style="right:540px;top:676px"><span class="tag">حسب <span class="lat">Le360</span></span></div>
    <div id="s3-lb-ss" class="lbl s" style="right:540px;top:736px">محطتا تحويل</div>
    <div id="s3-note">الشركة الجهوية لم تُسمِّ أي محطة رسميا</div>
    <div id="s3-myth"><span class="no" id="s3-no">محطات توليد</span><span>&larr;</span><span id="s3-yes">محطات تحويل</span></div>
    {avatar_block("s3", dur, "pip")}"""
    t_a, t_b, t_c, t_d, t_e, t_f = (T(ph, k) for k in ("s3a", "s3b", "s3c", "s3d", "s3e", "s3f"))
    js = f"""
      const flows = gsap.utils.toArray("#s3-svg .flow");
      tl.set(flows, {{ opacity: 0 }}, 0);
      tl.set("#s3-cut-r, #s3-cut-l", {{ opacity: 0 }}, 0);
      tl.set(".s3-h-r-win, .s3-h-l-win", {{ opacity: 0.25 }}, 0);
      tl.fromTo("#s3-eyebrow, #s3-title", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.5, stagger: 0.1, ease: "power3.out" }}, 0);
      tl.fromTo("#s3-pip", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, 0.1);
      // the chain grows top-down while the source is named
      tl.fromTo("#s3-plants", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, {t_a + 0.1});
      tl.fromTo("#s3-lb-plants", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, {t_a + 0.3});
      tl.fromTo("#s3-corr", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5 }}, {t_a + 0.7});
      tl.fromTo("#s3-lb-vhv", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, {t_a + 0.9});
      tl.fromTo("#s3-ss-r", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, {T(ph, "s3b", 0.28)});
      tl.fromTo("#s3-ss-r-name", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.35 }}, {T(ph, "s3b", 0.3)});
      tl.fromTo("#s3-ss-l", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, {T(ph, "s3b", 0.42)});
      tl.fromTo("#s3-ss-l-name", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.35 }}, {T(ph, "s3b", 0.44)});
      tl.fromTo("#s3-tag", {{ opacity: 0, scale: 0.9 }}, {{ opacity: 1, scale: 1, duration: 0.4, ease: "back.out(1.6)" }}, {T(ph, "s3b", 0.5)});
      tl.fromTo("#s3-h-r, #s3-h-l", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.5, stagger: 0.1, ease: "power3.out" }}, {T(ph, "s3b", 0.72)});
      tl.fromTo("#s3-note", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, {t_c});
      tl.to("#s3-note", {{ opacity: 0, duration: 0.3 }}, {t_d - 0.1});
      // not generation, transformation
      tl.fromTo("#s3-myth", {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }}, {t_d});
      tl.fromTo("#s3-no", {{ "--strike": 0 }}, {{ "--strike": 1, duration: 0.35, ease: "power2.out" }}, {T(ph, "s3d", 0.45)});
      tl.fromTo("#s3-lb-ss", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.35 }}, {T(ph, "s3d", 0.8)});
      tl.to("#s3-tag", {{ y: -6, duration: 0.3 }}, {T(ph, "s3d", 0.8)});
      // power flows: corridor -> substations -> neighbourhoods
      tl.to(flows, {{ opacity: 1, duration: 0.4, stagger: 0.05 }}, {t_e});
      tl.fromTo(flows, {{ strokeDashoffset: 0 }}, {{ strokeDashoffset: -280, duration: {max(4.0, t_f + 1.6 - t_e):.2f}, ease: "none" }}, {t_e});
      tl.to(".s3-h-r-win, .s3-h-l-win", {{ opacity: 1, duration: 0.4, stagger: 0.04 }}, {T(ph, "s3e", 0.7)});
      // the incoming line is cut: everything downstream goes dark
      const cut = {T(ph, "s3f", 0.22)};
      tl.set("#s3-cut-r, #s3-cut-l", {{ opacity: 1 }}, cut);
      tl.to("#s3-f-in-r-a, #s3-f-in-l-a", {{ opacity: 0, duration: 0.15 }}, cut);
      tl.to("#s3-f-in-r, #s3-f-in-l", {{ stroke: "#F25C54", duration: 0.15 }}, cut);
      tl.to("#s3-ss-r-led, #s3-ss-l-led", {{ opacity: 0.12, duration: 0.25 }}, {T(ph, "s3f", 0.45)});
      tl.to("[id^='s3-f-out']", {{ opacity: 0, duration: 0.3 }}, {T(ph, "s3f", 0.5)});
      tl.to(".s3-h-r-win, .s3-h-l-win", {{ opacity: 0.12, duration: 0.25, stagger: 0.06 }}, {T(ph, "s3f", 0.72)});"""
    return tpl("s3", css, body, js), dur


# ------------------------------------------------------------------------------------------- S4
def s4():
    ph, dur, mk = cues("s4")
    css = """
    #s4-hyp { top: 172px; } #s4-title { top: 252px; font-size: 56px; }
    #s4-svg { position: absolute; left: 0; top: 0; width: 1080px; height: 1080px; overflow: visible; }
    .cond { fill: none; stroke: #93CDBB; stroke-width: 5; stroke-linecap: round; }
    .cur { fill: none; stroke: #F4A62A; stroke-width: 5; stroke-linecap: round; stroke-dasharray: 8 22; }
    .wind { stroke: #93A4A7; stroke-width: 3; stroke-linecap: round; opacity: 0.6; }
    #s4-sc { position: absolute; transform: translate(50%, 0); }
    #s4-trip { position: absolute; right: 64px; top: 770px; width: 560px; text-align: right; }
    #s4-trip b { display: block; font: 700 32px/1.2 "Plex Arabic"; color: #E8EEEC; }
    #s4-trip span { display: block; font: 600 28px/1.3 "Plex Arabic"; color: #93A4A7; }
    #s4-other { position: absolute; left: 64px; right: 64px; top: 760px; height: 240px; display: flex; gap: 24px; }
    #s4-other .o { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px; }
    #s4-other .o span { font: 700 32px/1.2 "Plex Arabic"; color: #E8EEEC; }
    #s4-other .k { font: 600 28px/1 "Plex Arabic"; color: #93A4A7; }
"""
    body = f"""    <div class="grid"></div>
    <div id="s4-hyp" class="hyp"><b>?</b><span>فرضية – غير مؤكدة</span></div>
    <div id="s4-title" class="title">إلا تلاقاو سلكين فالريح</div>
    <svg id="s4-svg" viewBox="0 0 1080 1080">
      <g id="s4-winds">
        <path class="wind" id="s4-wd0" d="M 1000 380 H 860"/><path class="wind" id="s4-wd1" d="M 1040 470 H 880"/>
        <path class="wind" id="s4-wd2" d="M 980 690 H 820"/><path class="wind" id="s4-wd3" d="M 1020 620 H 900"/>
        <path class="wind" id="s4-wd4" d="M 960 540 H 840"/>
      </g>
      {pylon(110, 420, 300, 1.6)}{pylon(970, 420, 300, 1.6)}
      <path d="M 70 440 H 150 M 70 510 H 150 M 930 440 H 1010 M 930 510 H 1010" stroke="#93CDBB" stroke-width="4"/>
      <path id="s4-c1" class="cond" d="M 110 440 Q 540 680 970 440"/>
      <path id="s4-c2" class="cond" d="M 110 510 Q 540 750 970 510"/>
      <path id="s4-i1" class="cur" d="M 110 440 Q 540 680 970 440"/>
      <path id="s4-i2" class="cur" d="M 110 510 Q 540 750 970 510"/>
      <g id="s4-spark" transform="translate(540,600)">
        <circle id="s4-ring" r="40" fill="none" stroke="#F25C54" stroke-width="5"/>
        <path d="M0 -46 L10 -12 L46 -16 L16 6 L32 40 L0 18 L-30 40 L-16 6 L-46 -14 L-10 -12 Z" fill="#F4A62A"/>
        <circle r="14" fill="#FFFFFF"/>
      </g>
      <g transform="translate(150,780)"><g id="s4-breaker">
        <rect x="0" y="0" width="120" height="150" rx="10" fill="#141D21" stroke="#93CDBB" stroke-width="3.5"/>
        <circle cx="60" cy="96" r="10" fill="#93CDBB"/>
        <path id="s4-lever" d="M60 96 L60 30" stroke="#E8EEEC" stroke-width="10" stroke-linecap="round"/>
        <text x="60" y="140" fill="#93A4A7" font-size="20" text-anchor="middle" font-family="Space Grotesk" font-weight="700">ON / OFF</text>
      </g></g>
    </svg>
    <div id="s4-sc" style="right:540px;top:660px"><span class="tag" style="color:#F25C54;border-color:#F25C54;background:rgba(13,19,22,.9)">قصر دارة · تيار قوي بزاف</span></div>
    <div id="s4-trip"><b>أجهزة الحماية كتفصل الخط</b><span>فجزء من الثانية، باش ما تتخربش المعدات</span></div>
    <div id="s4-other">
      <div id="s4-o1" class="o card"><svg width="90" height="90" viewBox="0 0 90 90"><path d="M52 4 L22 50 H42 L32 86 L70 34 H48 L60 4 Z" fill="#F4A62A"/></svg><span>صاعقة</span><div class="k">احتمال آخر</div></div>
      <div id="s4-o2" class="o card"><svg width="120" height="90" viewBox="0 0 120 90" fill="none" stroke-linecap="round"><path d="M4 30 Q60 50 116 30" stroke="#93A4A7" stroke-width="4"/><path d="M30 8 L62 44 L100 70 M62 44 L58 74 M48 28 L32 40" stroke="#93CDBB" stroke-width="6"/></svg><span>سقوط جسم على الخط</span><div class="k">احتمال آخر</div></div>
    </div>
    {avatar_block("s4", dur, "low")}"""
    t_touch = mk.get("touch", T(ph, "s4b", 0.3))
    t_trip = T(ph, "s4c", 0.3)
    sway_end = t_touch
    js = f"""
      tl.fromTo("#s4-hyp", {{ opacity: 0, scale: 0.92 }}, {{ opacity: 1, scale: 1, duration: 0.45, ease: "back.out(1.7)" }}, 0);
      tl.fromTo("#s4-title", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, 0.15);
      tl.set("#s4-spark, #s4-sc, #s4-trip, #s4-other", {{ opacity: 0 }}, 0);
      tl.fromTo("#s4-svg", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5 }}, 0.2);
      // current runs in both conductors until the trip
      tl.fromTo("#s4-i1, #s4-i2", {{ strokeDashoffset: 0 }}, {{ strokeDashoffset: -600, duration: {t_trip + 0.1:.2f}, ease: "none" }}, 0);
      // wind streaks: each crosses the frame, repeated a fixed number of times
      gsap.utils.toArray("#s4-winds .wind").forEach((w, i) => {{
        tl.fromTo(w, {{ x: 120, opacity: 0 }}, {{ x: -880, opacity: 0.7, duration: 1.4, ease: "none", repeat: {int((dur) / 1.4) + 1}, delay: 0 }}, 0.15 * i + {T(ph, "s4a", 0.2)});
      }});
      // galloping: amplitude grows until the two conductors meet at mid-span
      const st = {{ t: 0 }};
      const c1 = document.querySelector("#s4-c1"), c2 = document.querySelector("#s4-c2");
      const i1 = document.querySelector("#s4-i1"), i2 = document.querySelector("#s4-i2");
      const T0 = {T(ph, "s4a", 0.4)}, T1 = {sway_end};
      function sway(t) {{
        let a1 = 0, a2 = 0;
        if (t > T0 && t < T1) {{
          const u = (t - T0) / (T1 - T0);
          const amp = 18 + 44 * u;
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
      // the touch: spark, short circuit, current surge
      tl.set("#s4-spark", {{ opacity: 1, scale: 0.4, transformOrigin: "50% 50%" }}, {t_touch});
      tl.to("#s4-spark", {{ scale: 1.25, duration: 0.18, ease: "power2.out" }}, {t_touch});
      tl.to("#s4-spark", {{ opacity: 0, duration: 0.5 }}, {t_touch + 0.5});
      tl.set("#s4-spark", {{ opacity: 0.9, scale: 0.8 }}, {t_touch + 1.1});
      tl.to("#s4-spark", {{ opacity: 0, duration: 0.3 }}, {t_touch + 1.25});
      tl.fromTo("#s4-sc", {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }}, {t_touch + 0.15});
      tl.to("#s4-i1, #s4-i2", {{ stroke: "#FFFFFF", strokeWidth: 7, duration: 0.15 }}, {T(ph, "s4b", 0.7)});
      // protection trips: lever falls, current stops
      tl.fromTo("#s4-breaker", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }}, {t_trip - 0.6});
      tl.fromTo("#s4-lever", {{ rotation: 0, transformOrigin: "50% 100%" }}, {{ rotation: 90, duration: 0.18, ease: "power2.in" }}, {t_trip});
      tl.to("#s4-i1, #s4-i2", {{ opacity: 0, duration: 0.12 }}, {t_trip + 0.12});
      tl.to("#s4-sc", {{ opacity: 0, duration: 0.3 }}, {t_trip + 0.2});
      tl.fromTo("#s4-trip", {{ opacity: 0, x: -16 }}, {{ opacity: 1, x: 0, duration: 0.45, ease: "power3.out" }}, {t_trip + 0.15});
      // other possibilities
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
    # two feeds into one substation
    '<path d="M20 10 V60 M100 10 V60" stroke="#93A4A7" stroke-width="5"/><path d="M20 60 Q20 80 60 80 M100 60 Q100 80 60 80" fill="none" stroke="#F4A62A" stroke-width="5"/><rect x="34" y="80" width="52" height="40" rx="5" fill="#141D21" stroke="#93CDBB" stroke-width="4"/>',
    # magnifier over an insulator string
    '<path d="M40 10 V90" stroke="#93A4A7" stroke-width="4"/><g fill="#141D21" stroke="#93CDBB" stroke-width="4"><ellipse cx="40" cy="34" rx="18" ry="6"/><ellipse cx="40" cy="50" rx="18" ry="6"/><ellipse cx="40" cy="66" rx="18" ry="6"/></g><circle cx="80" cy="56" r="22" fill="none" stroke="#E8EEEC" stroke-width="5"/><path d="M96 72 L114 92" stroke="#E8EEEC" stroke-width="7" stroke-linecap="round"/>',
    # lightning rod with a bolt
    '<path d="M60 30 V116 M44 116 H76" stroke="#93CDBB" stroke-width="5"/><path d="M60 30 L54 12 M60 30 L66 12" stroke="#93CDBB" stroke-width="4"/><path d="M96 4 L80 34 H92 L84 58 L108 26 H96 L104 4 Z" fill="#F4A62A"/>',
    # weather alert on a screen
    '<rect x="10" y="16" width="100" height="72" rx="8" fill="#141D21" stroke="#93CDBB" stroke-width="4"/><path d="M60 30 L84 74 H36 Z" fill="none" stroke="#F4A62A" stroke-width="5" stroke-linejoin="round"/><path d="M60 44 V58 M60 64 V66" stroke="#F4A62A" stroke-width="5" stroke-linecap="round"/><path d="M44 102 H76 M60 88 V102" stroke="#93CDBB" stroke-width="4"/>',
    # generator
    '<rect x="10" y="36" width="100" height="62" rx="8" fill="#141D21" stroke="#93CDBB" stroke-width="4"/><circle cx="40" cy="67" r="16" fill="none" stroke="#93CDBB" stroke-width="4"/><path d="M84 52 L72 70 H82 L76 86 L94 62 H84 L90 52 Z" fill="#F4A62A"/><path d="M20 98 V110 M100 98 V110" stroke="#93CDBB" stroke-width="5"/>',
]


def s5():
    ph, dur, mk = cues("s5")
    css = """
    #s5-eyebrow { top: 178px; } #s5-title { top: 224px; font-size: 56px; }
    #s5-steps { position: absolute; right: 64px; left: 64px; top: 340px; display: flex; gap: 18px; justify-content: flex-start; direction: rtl; }
    .st { width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
      font: 700 30px/1 "Space Grotesk"; color: #6E8186; border: 2px solid #26343B; background: #141D21; }
    .bl { position: absolute; right: 64px; left: 64px; top: 450px; display: flex; flex-direction: column; align-items: flex-start; gap: 26px; }
    .bl .tx { font: 700 76px/1.18 "Plex Arabic"; color: #E8EEEC; text-align: right; }
    .bl svg { flex: 0 0 auto; }
"""
    steps = "".join(f'<div id="s5-st{i}" class="st">{i + 1}</div>' for i in range(5))
    bl = "".join(f'<div id="s5-b{i}" class="bl"><svg width="140" height="130" viewBox="0 0 120 120" fill="none">{ICONS[i]}</svg><div class="tx ink">{BULLETS[i]}</div></div>' for i in range(5))
    body = f"""    <div class="grid"></div>
    <div id="s5-eyebrow" class="eyebrow"><i></i><span>باش ما يتعاودش</span></div>
    <div id="s5-title" class="title">حلول معروفة</div>
    <div id="s5-steps">{steps}</div>
    {bl}
    {avatar_block("s5", dur, "low")}"""
    starts = [T(ph, k) for k in ("s5b", "s5c", "s5d", "s5e", "s5f")]
    js = f"""
      tl.fromTo("#s5-eyebrow, #s5-title", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.5, stagger: 0.1, ease: "power3.out" }}, 0);
      tl.fromTo("#s5-steps .st", {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: 0.35, stagger: 0.06, ease: "power3.out" }}, {T(ph, "s5a", 0.4)});
      tl.set(".bl", {{ opacity: 0 }}, 0);
      const S = {json.dumps(starts)};
      S.forEach((t, i) => {{
        if (i > 0) {{
          tl.to(`#s5-b${{i - 1}}`, {{ opacity: 0, y: -18, duration: 0.3, ease: "power2.in" }}, t - 0.05);
          tl.to(`#s5-st${{i - 1}}`, {{ backgroundColor: "#141D21", color: "#93CDBB", borderColor: "#93CDBB", duration: 0.25 }}, t - 0.05);
        }}
        tl.to(`#s5-st${{i}}`, {{ backgroundColor: "#F4A62A", color: "#0D1316", borderColor: "#F4A62A", duration: 0.25 }}, t);
        tl.fromTo(`#s5-b${{i}}`, {{ opacity: 0, y: 26 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, t + 0.1);
      }});"""
    return tpl("s5", css, body, js), dur


# ------------------------------------------------------------------------------------------- S6
def s6():
    ph, dur, mk = cues("s6")
    css = """
    #s6-hyp { top: 172px; }
    #s6-ctx { position: absolute; right: 64px; left: 64px; top: 262px; font: 600 32px/1.3 "Plex Arabic"; color: #93A4A7; text-align: right; }
    #s6-q { top: 312px; font-size: 62px; }
    #s6-ans { position: absolute; right: 64px; top: 478px; font: 700 34px/1 "Plex Arabic"; color: #F25C54; }
    #s6-list { position: absolute; right: 64px; left: 64px; top: 540px; display: flex; flex-direction: column; gap: 14px; }
    .pos { display: flex; align-items: center; gap: 16px; padding: 14px 20px 18px; font: 700 36px/1.2 "Plex Arabic"; color: #E8EEEC; }
    .pos i { flex: 0 0 auto; width: 14px; height: 14px; border-radius: 50%; border: 3px solid #93A4A7; }
    #s6-wait { position: absolute; right: 64px; top: 822px; font: 700 40px/1 "Plex Arabic"; color: #E8EEEC; }
"""
    body = f"""    <div class="grid"></div>
    {avatar_block("s6", dur, "low")}
    <div id="s6-hyp" class="hyp" style="z-index:4"><b>?</b><span>فرضية – غير مؤكدة</span></div>
    <div id="s6-ctx" style="z-index:4">الدار البيضاء عرفات رياح قوية فالماضي</div>
    <div id="s6-q" class="title ink" style="z-index:4">علاش هاد المرة تأثر أكثر من موقع؟</div>
    <div id="s6-ans" style="z-index:4">الجواب ما مؤكدش</div>
    <div id="s6-list" style="z-index:4">
      <div id="s6-p1" class="pos card"><i></i><span>اجتماع الرياح مع الرعد</span></div>
      <div id="s6-p2" class="pos card"><i></i><span>وقوع العطل فوقت الذروة</span></div>
      <div id="s6-p3" class="pos card"><i></i><span>خط مشترك كيغذي محطتين فنفس الوقت</span></div>
    </div>
    <div id="s6-wait" class="ink" style="z-index:4">ننتظرو تقرير رسمي</div>"""
    js = f"""
      tl.fromTo("#s6-hyp", {{ opacity: 0, scale: 0.92 }}, {{ opacity: 1, scale: 1, duration: 0.45, ease: "back.out(1.7)" }}, 0);
      tl.fromTo("#s6-ctx", {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }}, {T(ph, "s6a", 0.3)});
      tl.fromTo("#s6-q", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, {T(ph, "s6b")});
      tl.fromTo("#s6-ans", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.35 }}, {T(ph, "s6c")});
      tl.fromTo("#s6-p1", {{ opacity: 0, x: -20 }}, {{ opacity: 1, x: 0, duration: 0.45, ease: "power3.out" }}, {T(ph, "s6d", 0.4)});
      tl.fromTo("#s6-p2", {{ opacity: 0, x: -20 }}, {{ opacity: 1, x: 0, duration: 0.45, ease: "power3.out" }}, {T(ph, "s6e", 0.05)});
      tl.fromTo("#s6-p3", {{ opacity: 0, x: -20 }}, {{ opacity: 1, x: 0, duration: 0.45, ease: "power3.out" }}, {T(ph, "s6f", 0.05)});
      tl.fromTo("#s6-wait", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }}, {T(ph, "s6g")});"""
    return tpl("s6", css, body, js), dur


# ------------------------------------------------------------------------------------------- END
def end():
    dur = 7.0
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
    <div id="end-credits">صورة الخريطة: <span class="lat">Esri, Maxar, Earthstar Geographics</span> · مواقع الأحياء: <span class="lat">OpenStreetMap</span><br>المقدِّم والصوت مولَّدان بالذكاء الاصطناعي (<span class="lat">HeyGen</span>)</div>"""
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
