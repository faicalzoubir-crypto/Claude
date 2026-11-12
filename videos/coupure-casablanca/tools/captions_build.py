#!/usr/bin/env python3
"""compositions/captions.html: burned-in Arabic captions from data/cues.json "words".

Groups of at most 6 words (calm delivery), never across a phrase, broken at «،» when the phrase allows,
max 2 lines at 58 px, bottom edge at y 1650 (the user's bottom safe zone starts at 1670).
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
C = json.loads((ROOT / "data/cues.json").read_text())
W = C["words"]
TOTAL = C["total"]

groups, cur = [], []
by_phrase = {}
for w in W:
    by_phrase.setdefault(w["phrase"], []).append(w)
for pid, ws in by_phrase.items():
    n = len(ws)
    k = max(1, -(-n // 6))                      # number of groups
    size = -(-n // k)
    i = 0
    while i < n:
        j = min(n, i + size)
        # prefer a break right after a comma inside the window
        for m in range(j - 1, i + 1, -1):
            if re.search(r"[،,:]$", ws[m - 1]["text"]) and m - i >= 3 and n - m >= 2:
                j = m
                break
        groups.append(ws[i:j])
        i = j

items = []
for gi, g in enumerate(groups):
    a = max(0.1, g[0]["start"] - 0.06)
    nxt = groups[gi + 1][0]["start"] - 0.06 if gi + 1 < len(groups) else TOTAL
    b = min(g[-1]["end"] + 0.35, nxt - 0.02)
    text = " ".join(w["text"] for w in g)
    items.append((gi, round(a, 3), round(b, 3), text))

divs = "\n    ".join(f'<div id="cap-{i}" class="cap"><span>{t}</span></div>' for i, a, b, t in items)
js = "\n      ".join(
    f'tl.set("#cap-{i}", {{ opacity: 1, visibility: "visible" }}, {a}); '
    f'tl.to("#cap-{i}", {{ opacity: 0, duration: 0.1, ease: "power2.in" }}, {b - 0.1:.3f}); '
    f'tl.set("#cap-{i}", {{ opacity: 0, visibility: "hidden" }}, {b});'
    for i, a, b, t in items)

html = f"""<template>
  <style>
    @font-face {{ font-family: "Plex Arabic"; src: url("assets/fonts/IBMPlexSansArabic-Bold.ttf"); font-weight: 700; }}
    @font-face {{ font-family: "Space Grotesk"; src: url("assets/fonts/space-grotesk-latin-700-normal.woff2"); font-weight: 700; }}
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    .cap {{ position: absolute; left: 70px; right: 70px; bottom: 270px; text-align: center; direction: rtl;
      opacity: 0; visibility: hidden; overflow: visible; }}
    .cap span {{ display: inline; font: 700 58px/1.32 "Plex Arabic", "Space Grotesk"; color: #E8EEEC;
      -webkit-text-stroke: 2px #0D1316; paint-order: stroke fill;
      text-shadow: 0 3px 10px rgba(0, 0, 0, 0.7), 0 0 2px #0D1316;
      -webkit-box-decoration-break: clone; box-decoration-break: clone; }}
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
    {divs}
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      {js}
      window.__timelines["captions"] = tl;
    }})();
  </script>
</template>
"""
(ROOT / "compositions/captions.html").write_text(html)
print(len(items), "caption groups; longest", max(len(t.split()) for *_, t in items), "words")
