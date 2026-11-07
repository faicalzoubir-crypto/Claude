#!/usr/bin/env python3
"""Builds pub-moto-electrique from the plan below: index.html, compositions/*.html, tools/plan.json.

The plan is the one place to retime the film: scene slots, shots (file, trim, speed, punch-in),
voice lines, caption groups and the moments each card lands. Edit it, then:

  python3 tools/build.py      # writes the HTML and tools/plan.json
  python3 tools/music.py      # music bed and sound effects from tools/plan.json

Brand: brand/BRAND.md (dark #0D1316 + hairline grid, amber #F4A62A the one highlight,
text #E8EEEC / #93A4A7, negative #F25C54 for petrol, positive #3CC98F for electric).
Arabic type: Readex Pro (assets/fonts, OFL); numbers in cards: Space Grotesk.
"""
import json
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
W, H = 1080, 1920

# ---------------------------------------------------------------------------
# Voice. Each line is one file in assets/vo/ (tools/voice.py cuts them from the user's recording).
# start: when the line starts on the film's clock; dur: its length. Until the recording arrives,
# starts and lengths are estimates and no audio is placed (have_audio False).
VOICE = [
    {"id": "vo1", "start": 0.25, "dur": 4.3, "text": "البنزين يغلو يوماً بعد يوم، وكل ما تملأ الخزان يخف جيبك."},
    {"id": "vo2", "start": 5.70, "dur": 4.2, "text": "مع الدراجة النارية، كل كيلومتر يكلفني 60 سنتيم من البنزين."},
    {"id": "vo3", "start": 18.60, "dur": 5.0, "text": "اليوم أدخل المحطة لا لأملأ الخزان، بل فقط لأضبط ضغط الهواء في العجلات!"},
    {"id": "vo4", "start": 27.60, "dur": 8.4, "text": "ولأنني لا أحب الكلام بلا دليل، هذا الفولطمتر. كلفة الكيلومتر بالكهرباء 5 سنتيمات فقط، أي أرخص بـ12 مرة من البنزين."},
    {"id": "vo5", "start": 49.40, "dur": 11.6, "text": "بعد فيديو سعد عبيد زرت المعرض أواخر أكتوبر، ووجدت فعلاً خيارات كثيرة تناسب كل ميزانية. شكراً سعد! وإن كنتم تفكرون في دراجة كهربائية، فالحسبة واضحة: 5 سنتيمات مقابل 60."},
]
HAVE_VOICE_AUDIO = False

# Caption groups per line (2–4 words, high energy). Times come from tools/captions.json when it
# exists (word timings from the recording), else they are spread over the line by character count.
GROUPS = {
    "vo1": ["البنزين يغلو", "يوماً بعد يوم،", "وكل ما تملأ الخزان", "يخف جيبك."],
    "vo2": ["مع الدراجة النارية،", "كل كيلومتر", "يكلفني 60 سنتيم", "من البنزين."],
    "vo3": ["اليوم أدخل المحطة", "لا لأملأ الخزان،", "بل فقط لأضبط", "ضغط الهواء في العجلات!"],
    "vo4": ["ولأنني لا أحب", "الكلام بلا دليل،", "هذا الفولطمتر.", "كلفة الكيلومتر بالكهرباء",
            "5 سنتيمات فقط،", "أي أرخص بـ12 مرة", "من البنزين."],
    "vo5": ["بعد فيديو سعد عبيد", "زرت المعرض", "أواخر أكتوبر،", "ووجدت فعلاً", "خيارات كثيرة",
            "تناسب كل ميزانية.", "شكراً سعد!", "وإن كنتم تفكرون", "في دراجة كهربائية،",
            "فالحسبة واضحة:", "5 سنتيمات مقابل 60."],
}

# ---------------------------------------------------------------------------
# Scenes: slot on the film's clock, shots (local times), and the moments cards land (film clock).
# shot: src, at (local start), dur, ms (trim into the source), rate, vol, z0/z1 (punch-in from/to),
# origin (punch-in centre).
F = "assets/footage/"
SCENES = [
    {"id": "s1-hook", "start": 0.0, "dur": 5.0, "shots": [
        {"src": F + "vespa-petromin.mp4", "at": 0.0, "dur": 1.40, "ms": 5.40, "z0": 1.0, "z1": 1.10, "origin": "70% 20%"},
        {"src": F + "vespa-shell.mp4", "at": 1.40, "dur": 1.20, "ms": 0.20, "z0": 1.04, "z1": 1.12, "origin": "60% 25%"},
        {"src": F + "vespa-afriquia-nuit.mp4", "at": 2.60, "dur": 1.25, "ms": 0.05, "z0": 1.0, "z1": 1.10, "origin": "75% 25%"},
        {"src": F + "vespa-yoom.mp4", "at": 3.85, "dur": 1.15, "ms": 0.0, "z0": 1.0, "z1": 1.06, "origin": "60% 30%"},
    ]},
    {"id": "s2-essence", "start": 5.0, "dur": 13.0, "shots": [
        {"src": F + "vespa-petromin.mp4", "at": 0.0, "dur": 4.6, "ms": 0.40, "z0": 1.0, "z1": 1.06, "origin": "60% 30%"},
        {"src": F + "vespa-shell.mp4", "at": 4.6, "dur": 3.6, "ms": 1.40, "z0": 1.0, "z1": 1.05, "origin": "60% 30%"},
        {"src": F + "vespa-petromin.mp4", "at": 8.2, "dur": 4.8, "ms": 7.10, "z0": 1.0, "z1": 1.05, "origin": "50% 40%"},
    ]},
    # PLACEHOLDER until the user's clip arrives: the e-bike entering the station (scene 3).
    {"id": "s3-surprise", "start": 18.0, "dur": 9.0, "shots": [
        {"src": F + "moto-elec-nuit.mp4", "at": 0.0, "dur": 9.0, "ms": 0.0, "rate": 0.75, "z0": 1.0, "z1": 1.06, "origin": "50% 70%", "vol": 0.10},
    ]},
    {"id": "s4-preuve", "start": 27.0, "dur": 13.0, "shots": []},
    {"id": "s5-saad", "start": 40.0, "dur": 9.0, "shots": [
        {"src": F + "saad-a.mp4", "at": 0.0, "dur": 3.5, "ms": 2.85, "z0": 1.0, "z1": 1.0, "origin": "50% 40%", "vol": 1.0},
        {"src": F + "saad-b.mp4", "at": 3.5, "dur": 5.5, "ms": 2.60, "z0": 1.08, "z1": 1.08, "origin": "50% 35%", "vol": 1.0},
    ]},
    {"id": "s6-merci", "start": 49.0, "dur": 13.0, "shots": [
        {"src": F + "moto-elec-nuit.mp4", "at": 0.0, "dur": 13.0, "ms": 0.0, "rate": 0.52, "z0": 1.0, "z1": 1.08, "origin": "50% 65%", "vol": 0.10},
    ]},
]
TOTAL = 62.0
VESPA_VOL = 0.18  # engine and wind under the voice

# Moments on the film clock, tied to words (estimates until the recording is timed).
CUE = {
    "titre": 0.0,           # « البنزين غلا » on screen from frame 0 (the hook and the thumbnail)
    "carte60": 8.3,         # « 60 سنتيم »
    "volt": 30.2,           # « هذا الفولطمتر »
    "graphe": 31.4,         # « كلفة الكيلومتر بالكهرباء »
    "barre5": 32.6,         # « 5 سنتيمات »
    "barre60": 33.6,        # the petrol bar for comparison
    "x12": 34.5,            # « أرخص بـ12 مرة » (riser into impact in the music)
    "saad": 40.15,          # Saad's card
    "merci": 55.0,          # « شكراً سعد »
    "fin": 59.2,            # « 5 سنتيمات مقابل 60 »
}

# ---------------------------------------------------------------------------
FONTS = """
    @font-face { font-family: "ReadexAr"; src: url("assets/fonts/readex-pro-arabic-500-normal.woff2") format("woff2"); font-weight: 500; }
    @font-face { font-family: "ReadexAr"; src: url("assets/fonts/readex-pro-arabic-700-normal.woff2") format("woff2"); font-weight: 700; }
    @font-face { font-family: "ReadexLat"; src: url("assets/fonts/readex-pro-latin-500-normal.woff2") format("woff2"); font-weight: 500; }
    @font-face { font-family: "ReadexLat"; src: url("assets/fonts/readex-pro-latin-700-normal.woff2") format("woff2"); font-weight: 700; }
    @font-face { font-family: "Space Grotesk"; src: url("assets/fonts/space-grotesk-latin-600-normal.woff2") format("woff2"); font-weight: 600; }
    @font-face { font-family: "Space Grotesk"; src: url("assets/fonts/space-grotesk-latin-700-normal.woff2") format("woff2"); font-weight: 700; }"""

BASE_CSS = """
    #root { position: absolute; inset: 0; overflow: hidden; }
    .shot { position: absolute; inset: 0; }
    .shot video, .shot img { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; }
    .ar { font-family: "ReadexAr", "ReadexLat", sans-serif; direction: rtl; }
    .card { position: absolute; background: rgba(20, 29, 33, 0.92); border: 1.5px solid #26343B; border-radius: 14px; }"""


def f2(x):
    return f"{x:.3f}".rstrip("0").rstrip(".") if "." in f"{x:.3f}" else f"{x}"


def shot_html(sid, k, s):
    rate = s.get("rate", 1.0)
    vol = s.get("vol", VESPA_VOL)
    return f"""    <div id="{sid}-w{k}" class="shot" style="z-index: {k + 1}; transform-origin: {s['origin']};" data-layout-allow-overflow>
      <video id="{sid}-v{k}" class="clip" src="{s['src']}" data-start="{f2(s['at'])}" data-duration="{f2(s['dur'])}"
        data-media-start="{f2(s['ms'])}" data-playback-rate="{f2(rate)}" data-has-audio="true" data-volume="{f2(vol)}"
        playsinline data-track-index="{k % 2}"></video>
    </div>"""


def shot_js(sid, k, s):
    return (f'      tl.fromTo("#{sid}-w{k}", {{ scale: {s["z0"]} }}, {{ scale: {s["z1"]}, duration: {f2(s["dur"])}, '
            f'ease: "none" }}, {f2(s["at"])});')


def scene_file(sc, css, markup, js):
    sid = sc["id"]
    shots = "\n".join(shot_html(sid, k, s) for k, s in enumerate(sc["shots"]))
    shots_js = "\n".join(shot_js(sid, k, s) for k, s in enumerate(sc["shots"]))
    return f"""<template>
  <!-- Generated by tools/build.py: change the plan there, then rebuild. -->
  <style>{FONTS}{BASE_CSS}{css}
  </style>
  <div id="root" data-composition-id="{sid}" data-width="{W}" data-height="{H}">
{shots}
{markup}
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
{shots_js}
{js}
      tl.to({{}}, {{ duration: {f2(sc['dur'])} }}, 0);
      window.__timelines["{sid}"] = tl;
    }})();
  </script>
</template>
"""


def loc(sc, cue):
    return round(CUE[cue] - sc["start"], 3)


# ---------------------------------------------------------------------------
# Scene overlays

def s1(sc):
    css = """
    #s1-title { left: 90px; right: 90px; top: 250px; padding: 34px 44px 40px; z-index: 20; text-align: center; }
    #s1-title .t { font-weight: 700; font-size: 132px; line-height: 1.15; color: #E8EEEC; }
    #s1-title .t b { color: #F4A62A; font-weight: 700; }
    #s1-title .bar { position: absolute; left: 50%; bottom: -2px; width: 60px; height: 4px; margin-left: -30px; background: #F4A62A; }"""
    markup = """    <div id="s1-title" class="card ar"><div id="s1-title-t" class="t">البنزين <b>غلا</b></div><div class="bar"></div></div>"""
    js = """      tl.fromTo("#s1-title-t", { scale: 1.0 }, { scale: 1.04, duration: 4.6, ease: "none" }, 0);
      tl.to("#s1-title", { opacity: 0, y: -20, duration: 0.25, ease: "power2.in" }, 4.7);"""
    return css, markup, js


PUMP_SVG = """<svg viewBox="0 0 48 48" width="64" height="64" aria-hidden="true">
          <rect x="8" y="6" width="20" height="36" rx="3" fill="none" stroke="#93A4A7" stroke-width="3"/>
          <rect x="12" y="11" width="12" height="9" rx="1.5" fill="#93A4A7"/>
          <path d="M28 18 h5 l5 6 v12 a3 3 0 0 1 -6 0 v-7 h-4" fill="none" stroke="#93A4A7" stroke-width="3" stroke-linejoin="round"/>
          <path d="M5 42 h26" stroke="#93A4A7" stroke-width="3" stroke-linecap="round"/>
        </svg>"""


def s2(sc):
    t = loc(sc, "carte60")
    css = """
    #s2-card { left: 150px; right: 150px; top: 230px; padding: 30px 40px 36px; z-index: 20; text-align: center; opacity: 0; }
    #s2-card .lbl { display: flex; align-items: center; justify-content: center; gap: 14px; font-weight: 500; font-size: 52px; color: #93A4A7; }
    #s2-card .row { display: flex; align-items: baseline; justify-content: center; gap: 22px; margin-top: 6px; }
    #s2-card .num { font-family: "Space Grotesk", sans-serif; font-weight: 700; font-size: 220px; line-height: 1; color: #F4A62A; direction: ltr; }
    #s2-card .unit { font-weight: 700; font-size: 60px; color: #E8EEEC; }"""
    markup = f"""    <div id="s2-card" class="card ar">
      <div class="lbl">{PUMP_SVG}<span>البنزين:</span></div>
      <div class="row"><span id="s2-num" class="num">60</span><span class="unit">سنتيم / كم</span></div>
    </div>"""
    js = f"""      tl.fromTo("#s2-card", {{ opacity: 0, y: 40, scale: 0.96 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.35, ease: "back.out(1.6)" }}, {f2(t - 0.35)});
      const n60 = {{ v: 0 }};
      tl.fromTo(n60, {{ v: 0 }}, {{ v: 60, duration: 0.7, ease: "power2.out",
        onUpdate: () => {{ document.getElementById("s2-num").textContent = Math.round(n60.v); }} }}, {f2(t - 0.25)});
      tl.to("#s2-card", {{ opacity: 0, y: -24, duration: 0.25, ease: "power2.in" }}, {f2(sc['dur'] - 0.4)});"""
    return css, markup, js


def s3(sc):
    return "", "", ""


def s4(sc):
    tv, tg = loc(sc, "volt"), loc(sc, "graphe")
    t5, t60, t12 = loc(sc, "barre5"), loc(sc, "barre60"), loc(sc, "x12")
    css = """
    #s4-photo { z-index: 1; transform-origin: 37% 19%; }
    #s4-chip { left: 600px; top: 700px; padding: 14px 30px; z-index: 5; opacity: 0; border-color: #F4A62A; }
    #s4-chip span { font-family: "Space Grotesk", sans-serif; font-weight: 700; font-size: 60px; color: #F4A62A; direction: ltr; }
    #s4-graph { position: absolute; inset: 0; z-index: 10; background-color: #0D1316; opacity: 0;
      background-image: linear-gradient(rgba(38, 52, 59, 0.55) 1px, transparent 1px), linear-gradient(90deg, rgba(38, 52, 59, 0.55) 1px, transparent 1px);
      background-size: 60px 60px; }
    #s4-eyebrow { position: absolute; right: 108px; top: 290px; text-align: right; }
    #s4-eyebrow .ln { width: 60px; height: 4px; background: #F4A62A; margin-left: auto; margin-bottom: 18px; }
    #s4-eyebrow .tx { font-weight: 700; font-size: 46px; letter-spacing: 0.02em; color: #F4A62A; }
    .s4-row { position: absolute; right: 108px; left: 108px; }
    .s4-row .head { display: flex; justify-content: space-between; align-items: baseline; }
    .s4-row .lab { font-weight: 700; font-size: 64px; color: #E8EEEC; }
    .s4-row .val { font-weight: 500; font-size: 50px; color: #93A4A7; }
    .s4-row .val b { font-family: "Space Grotesk", sans-serif; font-weight: 700; font-size: 88px; }
    .s4-row .track { position: relative; height: 56px; margin-top: 18px; border-radius: 6px; background: #141D21; border: 1.5px solid #26343B; overflow: hidden; }
    .s4-row .fill { position: absolute; top: 0; bottom: 0; right: 0; border-radius: 6px; transform-origin: 100% 50%; }
    #s4-e { top: 440px; }
    #s4-e .val b { color: #3CC98F; }
    #s4-e .fill { width: 8.333%; background: #3CC98F; }
    #s4-vs { position: absolute; left: 0; right: 0; top: 655px; text-align: center; font-weight: 500; font-size: 48px; color: #93A4A7; }
    #s4-p { top: 740px; }
    #s4-p .val b { color: #F25C54; }
    #s4-p .fill { width: 100%; background: #F25C54; }
    #s4-x12 { position: absolute; left: 0; right: 0; top: 975px; text-align: center; opacity: 0; }
    #s4-x12 span { display: inline-block; padding: 18px 44px; border-radius: 100px; background: #F4A62A; color: #0D1316; font-weight: 700; font-size: 70px; }"""
    markup = f"""    <div id="s4-photo" class="shot" data-layout-allow-overflow>
      <img id="s4-img" class="clip" src="assets/images/voltmetre.jpg" alt="" data-start="0" data-duration="{f2(tg + 0.5)}" data-track-index="0" />
    </div>
    <div id="s4-chip" class="card"><span>80.0 V</span></div>
    <div id="s4-graph" class="ar">
      <div id="s4-eyebrow"><div class="ln"></div><div class="tx">كلفة الكيلومتر</div></div>
      <div id="s4-e" class="s4-row"><div class="head"><div class="lab">الكهرباء:</div><div class="val"><b>5</b> سنتيمات / كم</div></div><div class="track"><div id="s4-e-fill" class="fill"></div></div></div>
      <div id="s4-vs">مقابل</div>
      <div id="s4-p" class="s4-row"><div class="head"><div class="lab">البنزين:</div><div class="val"><b>60</b> سنتيم / كم</div></div><div class="track"><div id="s4-p-fill" class="fill"></div></div></div>
      <div id="s4-x12"><span>أرخص بـ12 مرة</span></div>
    </div>"""
    js = f"""      tl.fromTo("#s4-photo", {{ scale: 1.0 }}, {{ scale: 1.32, duration: {f2(tg)}, ease: "power1.inOut" }}, 0);
      tl.fromTo("#s4-chip", {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "back.out(1.6)" }}, {f2(tv - 0.1)});
      tl.to("#s4-chip", {{ opacity: 0, duration: 0.2 }}, {f2(tg + 0.15)});
      tl.fromTo("#s4-graph", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.35, ease: "power2.out" }}, {f2(tg - 0.2)});
      tl.fromTo("#s4-eyebrow", {{ opacity: 0, x: 30 }}, {{ opacity: 1, x: 0, duration: 0.35, ease: "power3.out" }}, {f2(tg)});
      tl.fromTo("#s4-e", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }}, {f2(tg + 0.1)});
      tl.fromTo("#s4-e-fill", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.5, ease: "power3.out" }}, {f2(t5)});
      tl.fromTo("#s4-vs", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, {f2(t60 - 0.4)});
      tl.fromTo("#s4-p", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }}, {f2(t60 - 0.3)});
      tl.fromTo("#s4-p-fill", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.9, ease: "power2.inOut" }}, {f2(t60)});
      tl.fromTo("#s4-x12", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.4, ease: "back.out(2)" }}, {f2(t12)});"""
    return css, markup, js


def s5(sc):
    t = loc(sc, "saad")
    css = """
    #s5-card { left: 110px; right: 110px; top: 220px; padding: 26px 36px 30px; z-index: 20; text-align: center; opacity: 0; }
    #s5-card .h { font-family: "Space Grotesk", sans-serif; font-weight: 700; font-size: 60px; color: #F4A62A; direction: ltr; }
    #s5-card .s { font-weight: 500; font-size: 48px; line-height: 1.35; color: #E8EEEC; margin-top: 8px; }"""
    markup = """    <div id="s5-card" class="card ar"><div class="h">@Saadabidofficiel</div><div class="s">الفيديو الذي جعلني أزور المعرض</div></div>"""
    js = f"""      tl.fromTo("#s5-card", {{ opacity: 0, y: -30 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }}, {f2(t)});
      tl.to("#s5-card", {{ opacity: 0, y: -20, duration: 0.25, ease: "power2.in" }}, {f2(sc['dur'] - 0.35)});"""
    return css, markup, js


def s6(sc):
    tm, tf = loc(sc, "merci"), loc(sc, "fin")
    css = """
    #s6-thanks { left: 110px; right: 110px; top: 240px; padding: 26px 36px 30px; z-index: 20; text-align: center; opacity: 0; }
    #s6-thanks .s { font-weight: 700; font-size: 72px; color: #E8EEEC; }
    #s6-thanks .h { font-family: "Space Grotesk", sans-serif; font-weight: 700; font-size: 60px; color: #F4A62A; direction: ltr; margin-top: 4px; }
    #s6-end { left: 90px; right: 90px; top: 300px; padding: 34px 30px 40px; z-index: 21; text-align: center; opacity: 0; }
    #s6-end .nums { display: flex; justify-content: center; align-items: baseline; gap: 34px; direction: rtl; }
    #s6-end .n { font-family: "Space Grotesk", sans-serif; font-weight: 700; font-size: 190px; line-height: 1; }
    #s6-end .e { color: #3CC98F; }
    #s6-end .p { color: #F25C54; }
    #s6-end .vs { font-weight: 500; font-size: 60px; color: #93A4A7; }
    #s6-end .u { font-weight: 700; font-size: 54px; color: #E8EEEC; margin-top: 12px; }"""
    markup = """    <div id="s6-thanks" class="card ar"><div class="s">شكراً</div><div class="h">@Saadabidofficiel</div></div>
    <div id="s6-end" class="card ar">
      <div class="nums"><span class="n e">5</span><span class="vs">مقابل</span><span class="n p">60</span></div>
      <div class="u">سنتيم / كم</div>
    </div>"""
    js = f"""      tl.fromTo("#s6-thanks", {{ opacity: 0, y: 30, scale: 0.96 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.35, ease: "back.out(1.6)" }}, {f2(tm - 0.1)});
      tl.to("#s6-thanks", {{ opacity: 0, y: -20, duration: 0.25, ease: "power2.in" }}, {f2(tf - 0.6)});
      tl.fromTo("#s6-end", {{ opacity: 0, y: 40, scale: 0.94 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.4, ease: "back.out(1.6)" }}, {f2(tf - 0.2)});"""
    return css, markup, js


OVERLAYS = {"s1-hook": s1, "s2-essence": s2, "s3-surprise": s3, "s4-preuve": s4, "s5-saad": s5, "s6-merci": s6}

# ---------------------------------------------------------------------------
# Captions


def caption_times():
    timed = ROOT / "tools/captions.json"
    if timed.exists():
        return json.loads(timed.read_text())
    out = []
    for line in VOICE:
        groups = GROUPS[line["id"]]
        weights = [len(g) + 4 for g in groups]
        t, total = line["start"], sum(weights)
        for g, w in zip(groups, weights):
            d = line["dur"] * w / total
            out.append({"line": line["id"], "text": g, "start": round(t, 3), "end": round(t + d, 3)})
            t += d
    return out


def highlight(text):
    return re.sub(r"(\d+)", r'<b>\1</b>', escape(text))


def captions_file(caps):
    rows, js = [], []
    for i, c in enumerate(caps):
        start = c["start"] - 0.05
        end = c["end"] + 0.08
        if i + 1 < len(caps):
            end = min(end, caps[i + 1]["start"] - 0.05)
        dur = end - start
        rows.append(f'    <div id="cap-{i}" class="cap clip" data-start="{f2(start)}" data-duration="{f2(dur)}" '
                    f'data-track-index="0"><span id="cap-{i}-t" class="ar">{highlight(c["text"])}</span></div>')
        js.append(f'      tl.fromTo("#cap-{i}-t", {{ opacity: 0, y: 14, scale: 0.96 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.14, ease: "power2.out" }}, {f2(start)});')
        js.append(f'      tl.to("#cap-{i}-t", {{ opacity: 0, duration: 0.1, ease: "power2.in" }}, {f2(end - 0.1)});')
    return f"""<template>
  <!-- Generated by tools/build.py from the voice lines (tools/captions.json once the recording is timed). -->
  <style>{FONTS}
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    .ar {{ font-family: "ReadexAr", "ReadexLat", sans-serif; direction: rtl; }}
    /* bottom of the readable band (168–1330 px), clear of the app's caption and buttons */
    .cap {{ position: absolute; left: 90px; width: 820px; top: 1120px; height: 190px;
      display: flex; align-items: flex-end; justify-content: center; }}
    .cap span {{ display: inline-block; max-width: 820px; padding: 10px 30px 18px; border-radius: 14px;
      background: rgba(13, 19, 22, 0.80); font-weight: 700; font-size: 68px; line-height: 1.3;
      color: #E8EEEC; text-align: center; }}
    .cap span b {{ color: #F4A62A; font-family: "ReadexLat", sans-serif; font-weight: 700; }}
  </style>
  <div id="root" data-composition-id="captions" data-width="{W}" data-height="{H}">
{chr(10).join(rows)}
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
      tl.to({{}}, {{ duration: {f2(TOTAL)} }}, 0);
      window.__timelines["captions"] = tl;
    }})();
  </script>
</template>
"""


# ---------------------------------------------------------------------------
# Sound: music bed with ducking, sound effects, voice

SFX = [  # file, film time of the picture it belongs to, volume
    ("assets/sfx/pop-1.wav", CUE["carte60"] - 0.05, 0.5),
    ("assets/sfx/whoosh-1.wav", 18.0 - 0.35, 0.35),
    ("assets/sfx/pop-2.wav", CUE["volt"], 0.4),
    ("assets/sfx/whoosh-2.wav", CUE["graphe"] - 0.5, 0.3),
    ("assets/sfx/pop-1.wav", CUE["barre5"], 0.4),
    ("assets/sfx/pop-2.wav", CUE["merci"] - 0.05, 0.45),
    ("assets/sfx/pop-1.wav", CUE["fin"] - 0.05, 0.5),
]
MUSIC = {"open": 0.55, "voice": 0.22, "saad": 0.10}


def music_lane():
    s5 = next(s for s in SCENES if s["id"] == "s5-saad")
    spans = [(v["start"] - 0.25, v["start"] + v["dur"] + 0.2, MUSIC["voice"]) for v in VOICE]
    spans.append((s5["start"] - 0.2, s5["start"] + s5["dur"], MUSIC["saad"]))
    spans.sort()
    pts, t = [{"t": 0, "v": MUSIC["voice"]}], 0.0
    for a, b, v in spans:
        if a - t > 1.2:  # a gap long enough to lift the bed
            pts += [{"t": round(t + 0.3, 2), "v": MUSIC["open"]}, {"t": round(a - 0.3, 2), "v": MUSIC["open"]}]
        pts += [{"t": round(max(a, t), 2), "v": v}, {"t": round(b, 2), "v": v}]
        t = b
    pts += [{"t": round(t + 0.4, 2), "v": MUSIC["open"]}, {"t": TOTAL, "v": MUSIC["open"]}]
    clean = []
    for p in pts:
        if clean and p["t"] <= clean[-1]["t"]:
            p = {"t": round(clean[-1]["t"] + 0.01, 2), "v": p["v"]}
        clean.append(p)
    return json.dumps({"version": 1, "lanes": [{"target": "volume", "points": clean}]}, separators=(",", ":"))


def sfx_len(src):
    import wave
    with wave.open(str(ROOT / src)) as w:
        return round(w.getnframes() / w.getframerate(), 2)


def index_file():
    hosts = []
    for k, sc in enumerate(SCENES):
        hosts.append(f'      <div id="{sc["id"]}" class="scene" data-composition-id="{sc["id"]}" '
                     f'data-composition-src="compositions/{sc["id"]}.html"\n'
                     f'        data-start="{f2(sc["start"])}" data-duration="{f2(sc["dur"])}" data-track-index="{k % 2}" '
                     f'data-track-kind="graphics" data-width="{W}" data-height="{H}"></div>')
    hosts.append(f'      <div id="captions" class="scene" data-composition-id="captions" data-composition-src="compositions/captions.html"\n'
                 f'        data-start="0" data-duration="{f2(TOTAL)}" data-track-index="2" data-track-kind="captions" '
                 f'data-width="{W}" data-height="{H}"></div>')
    audio = [f"""      <audio id="music" class="clip" src="assets/music/fond.m4a" data-start="0" data-duration="{f2(TOTAL)}"
        data-track-index="3" data-volume="1" data-fade-out="2.5" data-audio-group="music"
        data-automation="{escape(music_lane())}"></audio>"""]
    if HAVE_VOICE_AUDIO:
        for v in VOICE:
            audio.append(f'      <audio id="{v["id"]}" class="clip" src="assets/vo/{v["id"]}.wav" data-start="{f2(v["start"])}" '
                         f'data-duration="{f2(v["dur"])}" data-track-index="4" data-volume="1" data-audio-group="voiceover"></audio>')
    for k, (src, t, vol) in enumerate(SFX):
        audio.append(f'      <audio id="sfx-{k}" class="clip" src="{src}" data-start="{f2(max(0, t))}" data-duration="{f2(sfx_len(src))}" '
                     f'data-track-index="{5 + k % 2}" data-volume="{f2(vol)}" data-audio-group="sfx"></audio>')
    return f"""<!doctype html>
<!-- Generated by tools/build.py: change the plan there, then rebuild. -->
<html lang="ar">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="vendor/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #0D1316; }}
      #root {{ position: relative; width: {W}px; height: {H}px; overflow: hidden; background: #0D1316; }}
      .scene {{ position: absolute; inset: 0; width: 100%; height: 100%; z-index: 1; }}
      #captions {{ z-index: 50; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{f2(TOTAL)}" data-width="{W}" data-height="{H}">
{chr(10).join(hosts)}
{chr(10).join(audio)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""


def main():
    (ROOT / "compositions").mkdir(exist_ok=True)
    for sc in SCENES:
        css, markup, js = OVERLAYS[sc["id"]](sc)
        (ROOT / f"compositions/{sc['id']}.html").write_text(scene_file(sc, css, markup, js))
    caps = caption_times()
    (ROOT / "compositions/captions.html").write_text(captions_file(caps))
    (ROOT / "index.html").write_text(index_file())
    plan = {"total": TOTAL, "cue": CUE, "voice": VOICE,
            "scenes": [{"id": s["id"], "start": s["start"], "dur": s["dur"]} for s in SCENES]}
    (ROOT / "tools/plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1))
    print(f"built {len(SCENES)} scenes, {len(caps)} caption groups, {TOTAL:.1f} s")


if __name__ == "__main__":
    main()
