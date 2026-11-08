#!/usr/bin/env python3
"""Lay the film out from script.json (+ the voice timings when they exist).

Writes:
  cues.js                    window.CUES: scene windows and phrase/word times (absolute seconds)
  index.html                 root composition: map layer, scene hosts, captions host, voice, music, sfx
  compositions/captions.html one timed caption group per 2-5 words

Timing source:
  assets/voice/timing.json   written by tools/voice.py: per phrase {dur, words:[{text,start,end}]}
                             (word times relative to the phrase clip). Without it, phrase lengths
                             are estimated (~2.1 words/s) so the visuals can be built before the voice.

  python3 tools/assemble.py              # version with the Arabic voice and captions
  python3 tools/assemble.py --musique    # music only: no voice, no captions (same timing; the
                                         # scenes show a short line under each title instead)
Then python3 tools/music.py and this script again (the bed file differs per version).
"""
import html
import sys
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
script = json.loads((ROOT / "script.json").read_text())
timing_path = ROOT / "assets/voice/timing.json"
timing = json.loads(timing_path.read_text()) if timing_path.exists() else None

W, H = 1080, 1920
WORD_SPLIT = re.compile(r"\s+")


def words_of(text):
    return [w for w in WORD_SPLIT.split(text.strip()) if w]


def estimate(phrase):
    """Phrase length and word times when no voice exists yet."""
    ws = words_of(phrase["text"])
    n_tts = len(words_of(phrase["tts"]))
    dur = 0.25 + n_tts * 0.47
    weights = [len(w) + 2 for w in ws]
    total = sum(weights)
    t, out = 0.1, []
    span = dur - 0.15
    for w, k in zip(ws, weights):
        d = span * k / total
        out.append({"text": w, "start": round(t, 3), "end": round(t + d * 0.92, 3)})
        t += d
    return dur, out


# ---- phrase and scene times -------------------------------------------------------------
# The film has a target length (script.json "target", seconds). Fixed parts: lead, pauses, tail.
TARGET = script.get("target")
_gaps = sum(p["gap"] for sc in script["scenes"] for p in sc["phrases"]) - script["scenes"][-1]["phrases"][-1]["gap"]
OVERHEAD = script["lead"] + _gaps + script["sceneGap"] * (len(script["scenes"]) - 1) + script["tail"]
SPEECH_SCALE = 1.0
if TARGET and not timing:
    # no voice yet: scale the estimates so the draft already runs at the target length
    SPEECH_SCALE = (TARGET - OVERHEAD) / sum(estimate(p)[0] for sc in script["scenes"] for p in sc["phrases"])

t = script["lead"]
phrases, scenes = {}, {}
order = []
for si, sc in enumerate(script["scenes"]):
    if si > 0:
        t += script["sceneGap"]
    first = None
    for ph in sc["phrases"]:
        if timing and ph["id"] in timing:
            dur = timing[ph["id"]]["dur"]
            ws = timing[ph["id"]]["words"]
            # keep caption words (text field), voice timings by position
            cap = words_of(ph["text"])
            if len(cap) != len(ws):
                # different tokenisation (numbers spelled out): spread caption words over the voiced span
                a, b = ws[0]["start"], ws[-1]["end"]
                k = [len(w) + 2 for w in cap]
                tot, acc, ws2 = sum(k), a, []
                for w, kk in zip(cap, k):
                    d = (b - a) * kk / tot
                    ws2.append({"text": w, "start": acc, "end": acc + d * 0.92})
                    acc += d
                ws = ws2
            else:
                ws = [{"text": c, "start": w["start"], "end": w["end"]} for c, w in zip(cap, ws)]
        else:
            dur, ws = estimate(ph)
            dur *= SPEECH_SCALE
            ws = [{**w, "start": w["start"] * SPEECH_SCALE, "end": w["end"] * SPEECH_SCALE} for w in ws]
        start = t
        phrases[ph["id"]] = {
            "scene": sc["id"],
            "start": round(start, 3),
            "end": round(start + dur, 3),
            "text": ph["text"],
            "words": [{"text": w["text"], "start": round(start + w["start"], 3), "end": round(start + w["end"], 3)} for w in ws],
        }
        order.append(ph["id"])
        if first is None:
            first = start
        t = start + dur + ph["gap"]
    scenes[sc["id"]] = {"first": round(first, 3)}

scene_ids = [s["id"] for s in script["scenes"]]
for i, sid in enumerate(scene_ids):
    start = 0.0 if i == 0 else round(scenes[sid]["first"] - 0.35, 3)
    scenes[sid]["start"] = start
for i, sid in enumerate(scene_ids):
    nxt = scenes[scene_ids[i + 1]]["start"] if i + 1 < len(scene_ids) else None
    last_phrase = [p for p in order if phrases[p]["scene"] == sid][-1]
    if nxt is not None:
        scenes[sid]["end"] = nxt
    else:
        natural = phrases[last_phrase]["end"] + script["tail"]
        # land exactly on the target when the last line still gets at least 1.6 s of hold
        fits = TARGET and TARGET >= phrases[last_phrase]["end"] + 1.6
        scenes[sid]["end"] = round(TARGET if fits else natural, 3)
DUR = scenes[scene_ids[-1]]["end"]

MODE = "music" if "--musique" in sys.argv else "voice"
# The music-only version follows no voice, so it may run longer (script.json "targetMusic"):
# every cue is stretched by the same factor, so each beat gets more time on screen.
LONG = script.get("targetMusic") if MODE == "music" else None
FOOT_SPEED = 1.0  # the 3D footage plays this much faster when the film is squeezed
if LONG and abs(LONG - DUR) > 0.01:
    k = LONG / DUR
    FOOT_SPEED = round(1 / k, 6)
    for ph in phrases.values():
        ph["start"], ph["end"] = round(ph["start"] * k, 3), round(ph["end"] * k, 3)
        for w in ph["words"]:
            w["start"], w["end"] = round(w["start"] * k, 3), round(w["end"] * k, 3)
    for sc in scenes.values():
        for key in ("first", "start", "end"):
            sc[key] = round(sc[key] * k, 3)
    DUR = LONG
cues = {"duration": DUR, "scenes": scenes, "phrases": phrases, "voiced": bool(timing), "mode": MODE, "footSpeed": FOOT_SPEED}
(ROOT / "cues.js").write_text(
    "// generated by tools/assemble.py: do not edit by hand\nwindow.CUES = "
    + json.dumps(cues, ensure_ascii=False, indent=1)
    + ";\n"
)

# ---- captions -------------------------------------------------------------------------
PUNCT = ("،", ".", "؟", ":", "!", "؛")
groups = []
for pid in order:
    ws = phrases[pid]["words"]
    cur = []
    for i, w in enumerate(ws):
        cur.append(w)
        long_enough = len(cur) >= 5 or (len(cur) >= 3 and sum(len(x["text"]) for x in cur) >= 26)
        if w["text"].endswith(PUNCT) or long_enough or i == len(ws) - 1:
            # don't leave a lone word behind
            if not w["text"].endswith(PUNCT) and i == len(ws) - 2:
                continue
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)

cap_items = []
for gi, g in enumerate(groups):
    start = g[0]["start"] - 0.08
    end = g[-1]["end"] + 0.18
    nxt = groups[gi + 1][0]["start"] - 0.08 if gi + 1 < len(groups) else None
    if nxt is not None and nxt - end < 0.35:
        end = nxt  # bridge short silences: the next group replaces this one
    if nxt is not None:
        end = min(end, nxt)
    text = " ".join(w["text"] for w in g)
    cap_items.append((gi, round(start, 3), round(end - start, 3), text))

cap_html = "\n".join(
    f'    <div id="cap-{gi}" class="cap clip" data-start="{s}" data-duration="{d}"><span class="cap-t">{html.escape(tx)}</span></div>'
    for gi, s, d, tx in cap_items
)
if MODE == "voice":  # the music-only version has no captions; keep the voice ones on disk
  (ROOT / "compositions/captions.html").write_text(
    f"""<template>
  <style>
    @font-face {{ font-family: "Plex Arabic"; src: url("assets/fonts/IBMPlexSansArabic-SemiBold.ttf"); font-weight: 600; }}
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    .cap {{
      position: absolute; left: 0; right: 0; top: 1206px; padding: 0 90px;
      text-align: center; direction: rtl; overflow: visible;
    }}
    .cap-t {{
      display: inline-block; font-family: "Plex Arabic", sans-serif; font-weight: 600;
      font-size: 46px; line-height: 1.42; color: #E8EEEC;
      background: rgba(13, 19, 22, 0.72); border-radius: 12px; padding: 4px 22px 8px;
      -webkit-box-decoration-break: clone; box-decoration-break: clone;
    }}
  </style>
  <div id="root" data-composition-id="captions" data-width="{W}" data-height="{H}">
{cap_html}
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      document.querySelectorAll("#root .cap").forEach((el) => {{
        const s = parseFloat(el.dataset.start);
        tl.fromTo(el.querySelector(".cap-t"), {{ opacity: 0, filter: "blur(6px)" }},
          {{ opacity: 1, filter: "blur(0px)", duration: 0.16, ease: "power2.out" }}, s);
      }});
      window.__timelines["captions"] = tl;
    }})();
  </script>
</template>
"""
)

# ---- sound effects (cue-relative) ---------------------------------------------------------
def at(pid, off=0.0, edge="start"):
    return round(phrases[pid][edge] + off, 3)


SFX = [
    # pump counter running, then the stop
    *[("tick", round(phrases["s1p1"]["start"] + 0.35 + k * 0.16, 3), 0.35) for k in range(14)],
    ("click", at("s1p1", 2.75), 0.6),
    # lights of the refinery switching on
    ("whoosh-a", at("s1p3", 0.0), 0.45),
    # the litre splits into its three parts
    ("pop", at("s2p2", 0.15), 0.5),
    ("pop", at("s2p3", 0.15), 0.5),
    ("pop", at("s2p4", 0.15), 0.5),
    # cuts into the 3D footage
    ("whoosh-b", round(scenes["s3"]["start"] + 0.02, 3), 0.5),
    ("pop", at("s3p2", 0.4), 0.45),
    ("whoosh-c", round(scenes["s4"]["start"] + 0.02, 3), 0.45),
    *[("pop", at("s4p3", 0.05 + k * 0.62), 0.4) for k in range(4)],
    ("whoosh-a", round(scenes["s5"]["start"] + 0.02, 3), 0.45),
    ("pop", at("s5p2", 0.3), 0.45),
    *[("tick", at("s5p3", 1.2 + k * 0.55), 0.5) for k in range(3)],
    ("whoosh-b", round(scenes["s6"]["start"] + 0.02, 3), 0.45),
    ("whoosh-c", round(scenes["s7"]["start"] + 0.02, 3), 0.45),
    ("pop", at("s7p1", 0.5), 0.5),
]
import wave


def wav_len(name):
    with wave.open(str(ROOT / f"assets/sfx/{name}.wav")) as w:
        return round(w.getnframes() / w.getframerate(), 3)


# each effect on the first free lane (Studio shows overlapping sounds on separate tracks)
lanes, sfx_rows = [], []
for i, (name, t0, v) in enumerate(sorted(SFX, key=lambda x: x[1])):
    if not (ROOT / f"assets/sfx/{name}.wav").exists():
        continue
    d = wav_len(name)
    k = next((j for j, end in enumerate(lanes) if end <= t0), None)
    if k is None:
        lanes.append(0)
        k = len(lanes) - 1
    lanes[k] = t0 + d
    sfx_rows.append(f'      <audio id="sfx-{i:02d}-{name}" class="clip" src="assets/sfx/{name}.wav" data-start="{t0}" data-duration="{d}" data-volume="{v}" data-track-index="{20 + k}"></audio>')
sfx_html = "\n".join(sfx_rows)

voice_html = ""
if timing and MODE == "voice":
    voice_html = "\n".join(
        f'      <audio id="voice-{pid}" class="clip" src="assets/voice/{pid}.wav" data-start="{phrases[pid]["start"]}" data-duration="{timing[pid]["dur"]}" data-volume="1" data-track-index="10"></audio>'
        for pid in order
    )

BED = "bed-voix.m4a" if MODE == "voice" else "bed-musique.m4a"
music_html = ""
if (ROOT / f"assets/music/{BED}").exists():
    music_html = f'      <audio id="music" class="clip" src="assets/music/{BED}" data-start="0" data-duration="{DUR}" data-volume="{0.5 if MODE == 'voice' else 1}" data-track-index="11"></audio>'

FOOT = json.loads((ROOT / "tools/footage.json").read_text()) if (ROOT / "tools/footage.json").exists() else {}
footage_rows = []
import subprocess
for sid, f in FOOT.items():
    if sid not in scenes or not (ROOT / f["src"]).exists():
        continue
    if abs(FOOT_SPEED - 1) > 1e-6:
        # a re-timed copy of the clip (same frames, FOOT_SPEED x faster); overlays index the anchors the same way
        fast = f["src"].replace(".mp4", f"-{round(DUR)}s.mp4")
        if not (ROOT / fast).exists():
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(ROOT / f["src"]), "-filter:v", f"setpts=PTS/{FOOT_SPEED}", "-r", "30",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-an", str(ROOT / fast)], check=True)
        f = {**f, "src": fast}
    s0 = scenes[sid]["start"]
    d = round(scenes[sid]["end"] - s0, 3)
    footage_rows.append(f'      <video id="foot-{sid}" class="clip" src="{f['src']}" muted playsinline data-start="{s0}" data-duration="{d}" data-track-index="1" style="position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover;z-index:1"></video>')
footage_html = "\n".join(footage_rows)

hosts = "\n".join(
    f"""      <div id="{sid}" class="scene" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html"
        data-start="{scenes[sid]['start']}" data-duration="{round(scenes[sid]['end'] - scenes[sid]['start'], 3)}"
        data-track-index="2" data-track-kind="graphics" style="z-index: 2"></div>"""
    for sid in scene_ids
)

(ROOT / "compositions/progress.html").write_text(
    f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    #pg-bar {{ position: absolute; left: 0; right: 0; bottom: 0; height: 5px; background: #F4A62A; transform-origin: 100% 50%; }}
  </style>
  <div id="root" data-composition-id="progress" data-width="{W}" data-height="{H}">
    <div id="pg-bar"></div>
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#pg-bar", {{ scaleX: 0 }}, {{ scaleX: 1, duration: {DUR}, ease: "none" }}, 0);
      window.__timelines["progress"] = tl;
    }})();
  </script>
</template>
"""
)
progress_host = (
    f'      <div id="progress" class="scene" data-composition-id="progress" data-composition-src="compositions/progress.html"\n'
    f'        data-start="0" data-duration="{DUR}" data-track-index="4" data-track-kind="graphics" style="z-index: 6"></div>'
)
captions_host = (
    '      <div id="captions" class="scene" data-composition-id="captions" data-composition-src="compositions/captions.html"\n        data-start="0" data-duration="{DUR}" data-track-index="3" data-track-kind="captions" style="z-index: 5"></div>'.format(DUR=DUR) if MODE == "voice" else "      <!-- music-only version: no captions -->"
)
(ROOT / "index.html").write_text(
    f"""<!doctype html>
<html lang="ar">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="vendor/gsap.min.js"></script>
    <script src="cues.js"></script>
    <script src="footage-anchors.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #0D1316; }}
      #root {{ position: relative; width: {W}px; height: {H}px; overflow: hidden; background: #0D1316; }}
      .scene {{ position: absolute; inset: 0; width: 100%; height: 100%; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="{W}" data-height="{H}">
{footage_html}
{hosts}
{captions_host}
{progress_host}
{voice_html}
{music_html}
{sfx_html}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""
)

print(f"[{MODE}] duration {DUR:.2f}s, {len(order)} phrases, {len(cap_items)} caption groups, voiced={bool(timing)}")
for sid in scene_ids:
    print(f"  {sid}: {scenes[sid]['start']:6.2f} → {scenes[sid]['end']:6.2f}")
