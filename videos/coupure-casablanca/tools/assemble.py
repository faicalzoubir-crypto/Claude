#!/usr/bin/env python3
"""Write index.html: scene hosts back to back, the voice, music, sound effects and the captions host.

Durations come from data/cues.json (tools/voice.py) or, before the voice exists, from the scene builders'
estimates. Run after tools/s2_build.py and tools/scenes_build.py.
"""
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CUES = json.loads((ROOT / "data/cues.json").read_text()) if (ROOT / "data/cues.json").exists() else {}
est = json.loads(subprocess.run([sys.executable, str(ROOT / "tools/scenes_build.py")], capture_output=True, text=True, check=True).stdout.strip().splitlines()[-1])
ORDER = [("s1", "s1.html"), ("s2", "s2-map.html")] + [(f"s{i}", f"s{i}.html") for i in range(3, 9)] + [("end", "end.html")]

def dur(sid):
    if sid in CUES.get("scenes", {}):
        return CUES["scenes"][sid]["duration"]
    if sid == "end" and "end" in CUES:
        return CUES["end"]["duration"]
    if sid == "s2":
        return 40.0
    return est[sid]

t = 0.0
hosts, starts = [], {}
for sid, f in ORDER:
    d = round(dur(sid), 3)
    starts[sid] = round(t, 3)
    hosts.append(f'''      <div id="{sid}" class="scene" data-composition-id="{sid}" data-composition-src="compositions/{f}"
        data-start="{t:.3f}" data-duration="{d:.3f}" data-track-index="2" data-track-kind="graphics" style="z-index: 2"></div>''')
    t += d
TOTAL = round(t, 3)

media = []
voice = ROOT / "assets/voice/voice.wav"
if voice.exists():
    media.append(f'      <audio id="voice" class="clip" src="assets/voice/voice.wav" data-start="0" data-duration="{TOTAL}" data-volume="1" data-track-index="10"></audio>')
music = ROOT / "assets/music/bed.wav"
if music.exists():
    media.append(f'      <audio id="music" class="clip" src="assets/music/bed.wav" data-start="0" data-duration="{TOTAL}" data-volume="1" data-track-index="11"></audio>')
sfx = CUES.get("sfx", [])
busy = []                                   # one sound per track at a time: first free track from 20
for i, s in enumerate(sorted(sfx, key=lambda x: x["t"])):
    k = next((j for j, e in enumerate(busy) if e <= s["t"]), None)
    if k is None:
        busy.append(0.0); k = len(busy) - 1
    busy[k] = s["t"] + s["d"] + 0.01
    media.append(f'      <audio id="sfx-{i:02d}" class="clip" src="assets/sfx/{s["file"]}" data-start="{s["t"]:.3f}" data-duration="{s["d"]:.3f}" data-volume="{s.get("v", 0.5)}"{f' data-fade-out="{s["fo"]}"' if s.get("fo") else ""} data-track-index="{20 + k}"></audio>')
if (ROOT / "compositions/captions.html").exists() and "--no-captions" not in sys.argv:
    hosts.append(f'''      <div id="captions" class="scene" data-composition-id="captions" data-composition-src="compositions/captions.html"
        data-start="0" data-duration="{TOTAL}" data-track-index="5" data-track-kind="captions" style="z-index: 6"></div>''')

html = f'''<!doctype html>
<html lang="ar">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="vendor/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #0D1316; }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; background: #0D1316; }}
      .scene {{ position: absolute; inset: 0; width: 100%; height: 100%; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
{chr(10).join(hosts)}
{chr(10).join(media)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
'''
(ROOT / "index.html").write_text(html)
(ROOT / "data").mkdir(exist_ok=True)
(ROOT / "data/starts.json").write_text(json.dumps({"starts": starts, "total": TOTAL}, indent=1))
print("total", TOTAL, starts)
