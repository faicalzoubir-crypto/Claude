#!/usr/bin/env python3
"""Teaser for «انقطاع الكهرباء بالدار البيضاء»: shots cut from the full film (no subtitles), on the beat
of an energetic catalog track (HeyGen music library, «aggressive cinematic drums, heavy bass hits», 139 BPM).

Clock = the music. OFFSET drops the track's silent lead-in, so its first hit lands on frame 0.
Bars (4 beats): 0.08 · 1.76 · 3.50 · 5.21 · 6.94 (the drop) · 8.65 · 10.36 · 12.08 · 13.79 · 15.50 · 17.22 ·
18.93 · 20.65 · 22.36 · 24.08 (end card) · 25.79 · 27.58.

  python3 tools/build.py [--src <film.mp4>]   # default: the film's no-subtitle master if present, else its livrable
"""
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILM = ROOT.parent / "coupure-casablanca"
SRC = next((Path(a) for a in sys.argv[sys.argv.index("--src") + 1:][:1]) if "--src" in sys.argv else None) \
    or FILM / "livrables/coupure-casablanca-sans-sous-titres.mp4"
FPS = 30
OFFSET = 0.80                                              # track time of frame 0
BEATS = [b - OFFSET for b in json.loads((ROOT / "data/beats.json").read_text())["beatTimes"]]
TOTAL = 27.6
FADE = 1.6
fr = lambda t: round(t * FPS)
B = lambda i: BEATS[i]

# shot: (id, beat in, beat out, film time at the shot's first frame, speed, zoom)
#   film times come from the film's cues (coupure-casablanca/data/cues.json):
#   S1 windows go out 13.34–14.6 · S4 «3 ≠ 4» lands 95.79 · S5 cut A 111.66, cut B 116.21 (substations dark 116.5),
#   dark neighbourhoods 128.3 · «متأخر» 140.79 · S6 bars 147.0–160.0 · S8 questions 198.8–205.0
SHOTS = [
    ("v01", None, 4, 11.10, 1.0, None),          # 16:48, the tower in the storm (frame 0 = the hook)
    ("v02", 4, 8, None, 1.0, "city"),            # close on the city: the windows go out
    ("v03", 8, 16, 17.80, 3.0, None),            # map 2: the neighbourhoods go dark (breakdown)
    ("v04", 16, 20, 58.40, 3.0, None),           # DROP · map 3: the 225 kV chain draws itself
    ("v05", 20, 24, 66.00, 3.0, None),           # power from both sides
    ("v06", 24, 26, 80.50, 1.0, None),           # «3» cables (spokesperson)
    ("v07", 26, 28, 92.00, 1.0, None),           # «4» lines (ONEE)
    ("v08", 28, 32, 95.74, 1.0, None),           # «3 ≠ 4»
    ("v09", 32, 34, 111.62, 1.0, None),          # cut A
    ("v10", 34, 36, 116.17, 1.0, None),          # cut B: both substations dark
    ("v11", 36, 38, 128.30, 1.5, None),          # the reported-dark neighbourhoods
    ("v12", 38, 40, 140.75, 1.0, None),          # «متأخر»
    ("v13", 40, 48, 146.90, 4.0, None),          # 3 h vs 22:11 vs 23:03
    ("v14", 48, 52, 202.40, 3.0, None),          # the open questions
    ("v15", 52, 53, 31.00, 1.0, "stutter"),      # recap, one beat each
    ("v16", 53, 54, 74.00, 1.0, "stutter"),
    ("v17", 54, 55, 119.00, 1.0, "stutter"),
    ("v18", 55, 56, 166.00, 1.0, "stutter"),
]
END_AT = B(56)

# overlay lines (bottom band, where the film's subtitles were): (id, beat in, beat out, html)
LINES = [
    ("o1", 8, 16, "بزاف د الأحياء <em>بلا ضو</em>"),
    ("o2", 16, 20, "جوج <em>محطات تحويل</em>"),
    ("o3", 20, 24, "الضو يقدر يوصل <em>من جوج جهات</em>"),
    ("o4", 24, 32, "<em>تلاتة</em> ولا <em>ربعة</em>؟"),
    ("o5", 32, 38, "كيفاش <em>طفاو بجوج</em>؟"),
    ("o6", 38, 40, "وخط التقوية <em>باقي متأخر</em>"),
    ("o7", 40, 48, "شحال <em>دام</em> الانقطاع؟"),
]


def cut_clips():
    out = ROOT / "assets/clips"
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    prev_end = 0.0
    for sid, bi, bo, src, speed, zoom in SHOTS:
        t0 = 0.0 if bi is None else B(bi)
        t1 = B(bo)
        f0, f1 = fr(t0), fr(t1)
        if src is None:                          # continues the previous shot's film time
            src = rows[-1]["src"] + (rows[-1]["f1"] - rows[-1]["f0"]) / FPS * rows[-1]["speed"]
        n = f1 - f0
        p = out / f"{sid}.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{src:.3f}", "-i", str(SRC),
                        "-vf", f"setpts=(PTS-STARTPTS)/{speed},fps={FPS}", "-frames:v", str(n), "-an",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p", "-g", "15", str(p)], check=True)
        rows.append({"id": sid, "f0": f0, "f1": f1, "src": src, "speed": speed, "zoom": zoom})
        prev_end = f1
    assert rows[0]["f0"] == 0 and all(a["f1"] == b["f0"] for a, b in zip(rows, rows[1:])), "gap between shots"
    return rows


def music():
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{OFFSET}", "-t", f"{TOTAL}", "-i", str(ROOT / "assets/music/source-c08.mp3"),
                    "-af", f"afade=t=out:st={TOTAL - FADE}:d={FADE}", "-ar", "48000", "-ac", "2", str(ROOT / "assets/music/teaser.wav")], check=True)


HEAD = """<!doctype html>
<html lang="ar">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="vendor/gsap.min.js"></script>
    <style>
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { width: 1080px; height: 1920px; overflow: hidden; background: #0D1316; }
      #root { position: relative; width: 1080px; height: 1920px; overflow: hidden; background: #0D1316; }
      .shot { position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; }
      .scene { position: absolute; inset: 0; width: 100%; height: 100%; }
    </style>
  </head>
"""

FONTS = """
    @font-face { font-family: "Plex Arabic"; src: url("assets/fonts/IBMPlexSansArabic-Bold.ttf"); font-weight: 700; }
    @font-face { font-family: "Plex Arabic"; src: url("assets/fonts/IBMPlexSansArabic-SemiBold.ttf"); font-weight: 600; }
    @font-face { font-family: "Space Grotesk"; src: url("assets/fonts/space-grotesk-latin-700-normal.woff2"); font-weight: 700; }"""


def index(rows):
    end_f = fr(END_AT)
    vids, tw = [], []
    for r in rows:
        s, d = r["f0"] / FPS, (r["f1"] - r["f0"]) / FPS
        vids.append(f'      <video id="{r["id"]}" class="clip shot" src="assets/clips/{r["id"]}.mp4" data-start="{s:.3f}" data-duration="{d:.3f}" '
                    f'data-track-index="1" muted playsinline></video>')
        if r["zoom"] == "city":                       # punch in on the beat, slow push while the windows go out
            tw.append(f'      tl.fromTo("#{r["id"]}", {{ scale: 1.04, transformOrigin: "48% 50%" }}, {{ scale: 1.08, duration: {d:.3f}, ease: "none" }}, {s:.3f});')
        elif r["zoom"] == "stutter":
            tw.append(f'      tl.fromTo("#{r["id"]}", {{ scale: 1.14 }}, {{ scale: 1.0, duration: {d:.3f}, ease: "power2.out" }}, {s:.3f});')
        else:                                         # punch-in on every cut
            tw.append(f'      tl.fromTo("#{r["id"]}", {{ scale: 1.07 }}, {{ scale: 1.0, duration: 0.45, ease: "power3.out" }}, {s:.3f});')
    body = f"""  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
{chr(10).join(vids)}
      <div id="overlay" class="scene" data-composition-id="overlay" data-composition-src="compositions/overlay.html"
        data-start="0" data-duration="{end_f / FPS:.3f}" data-track-index="3" data-track-kind="graphics" style="z-index: 3"></div>
      <div id="end" class="scene" data-composition-id="end" data-composition-src="compositions/end.html"
        data-start="{end_f / FPS:.3f}" data-duration="{TOTAL - end_f / FPS:.3f}" data-track-index="4" data-track-kind="graphics" style="z-index: 4"></div>
      <audio id="music" class="clip" src="assets/music/teaser.wav" data-start="0" data-duration="{TOTAL}" data-volume="1" data-track-index="10"></audio>
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
{chr(10).join(tw)}
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
    (ROOT / "index.html").write_text(HEAD + body)


def overlay():
    dur = fr(END_AT) / FPS
    css = FONTS + f"""
    #root {{ position: absolute; inset: 0; overflow: hidden; direction: rtl; }}
    #ov-scrim {{ position: absolute; left: 0; right: 0; top: 1240px; height: 680px;
      background: linear-gradient(rgba(13,19,22,0), rgba(13,19,22,.78) 38%, rgba(13,19,22,.9)); }}
    .ln {{ position: absolute; left: 70px; right: 70px; top: 1452px; text-align: center; opacity: 0;
      font: 700 74px/1.2 "Plex Arabic"; color: #E8EEEC; text-wrap: balance; }}
    .ln em {{ font-style: normal; color: #F4A62A; }}
    #ov-flash {{ position: absolute; inset: 0; background: #E8EEEC; opacity: 0; }}
"""
    lines = "\n".join(f'    <div id="{i}" class="ln">{h}</div>' for i, _, _, h in LINES)
    js = []
    for i, bi, bo, _ in LINES:
        a, b = fr(B(bi)) / FPS, fr(B(bo)) / FPS
        js.append(f'      tl.fromTo("#{i}", {{ opacity: 0, y: 34 }}, {{ opacity: 1, y: 0, duration: 0.22, ease: "power3.out" }}, {a + 0.03:.3f});')
        js.append(f'      tl.to("#{i}", {{ opacity: 0, duration: 0.1 }}, {b - 0.1:.3f});')
    drop = fr(B(16)) / FPS
    js.append(f'      tl.fromTo("#ov-flash", {{ opacity: 0.45 }}, {{ opacity: 0, duration: 0.3, ease: "power2.out", immediateRender: false }}, {drop:.3f});')
    html = f"""<template>
  <style>{css}
  </style>
  <div id="root" data-composition-id="overlay" data-width="1080" data-height="1920">
    <div id="ov-scrim"></div>
{lines}
    <div id="ov-flash"></div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
      tl.set({{}}, {{}}, {dur:.3f});
      window.__timelines = window.__timelines || {{}};
      window.__timelines["overlay"] = tl;
    }})();
  </script>
</template>
"""
    (ROOT / "compositions/overlay.html").write_text(html)


def end():
    t0 = fr(END_AT) / FPS
    dur = TOTAL - t0
    beat = lambda i: B(i) - t0                         # local time of beat i
    css = FONTS + """
    #root { position: absolute; inset: 0; overflow: hidden; background: #0D1316; direction: rtl; }
    .grid { position: absolute; inset: 0; opacity: 0.38;
      background-image: linear-gradient(#26343B 1.5px, transparent 1.5px), linear-gradient(90deg, #26343B 1.5px, transparent 1.5px);
      background-size: 60px 60px; }
    #e-eye { position: absolute; right: 80px; top: 600px; display: flex; align-items: center; gap: 16px; opacity: 0;
      font: 700 36px/1 "Plex Arabic"; color: #F4A62A; white-space: nowrap; }
    #e-eye i { display: block; width: 70px; height: 5px; background: #F4A62A; border-radius: 3px; }
    .et { position: absolute; right: 80px; left: 80px; font: 700 112px/1.12 "Plex Arabic"; color: #E8EEEC; opacity: 0; }
    #e-t1 { top: 680px; } #e-t2 { top: 806px; }
    #e-sub { position: absolute; right: 80px; left: 80px; top: 1000px; font: 700 60px/1.2 "Plex Arabic"; color: #F4A62A; opacity: 0; }
    #e-cta { position: absolute; right: 80px; top: 1130px; display: flex; align-items: center; gap: 18px; opacity: 0;
      padding: 18px 30px 24px; border: 3px solid #93CDBB; border-radius: 16px; background: #141D21;
      font: 700 46px/1 "Plex Arabic"; color: #E8EEEC; }
    #e-cta b { display: block; width: 0; height: 0; border-top: 16px solid transparent; border-bottom: 16px solid transparent;
      border-right: 24px solid #93CDBB; }
"""
    html = f"""<template>
  <style>{css}
  </style>
  <div id="root" data-composition-id="end" data-width="1080" data-height="1920">
    <div class="grid"></div>
    <div id="e-eye"><i></i><span>الأربعاء 11 نونبر 2026 · 16:48</span></div>
    <div id="e-t1" class="et">انقطاع الكهرباء</div>
    <div id="e-t2" class="et">بالدار البيضاء</div>
    <div id="e-sub">شنو وقع فالشبكة؟</div>
    <div id="e-cta" data-hold><b></b><span>شوف الفيديو الكامل</span></div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#e-eye", {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: 0.3, ease: "power3.out" }}, 0.02);
      tl.fromTo("#e-t1", {{ opacity: 0, y: 40, scale: 1.08 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.35, ease: "power3.out" }}, 0.06);
      tl.fromTo("#e-t2", {{ opacity: 0, y: 40, scale: 1.08 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.35, ease: "power3.out" }}, {beat(57):.3f});
      tl.fromTo("#e-sub", {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "power3.out" }}, {beat(58):.3f});
      tl.fromTo("#e-cta", {{ opacity: 0, x: -40 }}, {{ opacity: 1, x: 0, duration: 0.35, ease: "back.out(1.6)" }}, {beat(60):.3f});
      tl.set({{}}, {{}}, {dur:.3f});
      window.__timelines = window.__timelines || {{}};
      window.__timelines["end"] = tl;
    }})();
  </script>
</template>
"""
    (ROOT / "compositions/end.html").write_text(html)


if __name__ == "__main__":
    print("source:", SRC)
    rows = cut_clips()
    music()
    index(rows)
    overlay()
    end()
    for r in rows:
        print(f'{r["id"]}  {r["f0"] / FPS:6.2f}–{r["f1"] / FPS:6.2f}  film {r["src"]:7.2f} ×{r["speed"]}')
    print("end card", round(fr(END_AT) / FPS, 3), "total", TOTAL)
