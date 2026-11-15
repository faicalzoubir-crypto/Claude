#!/usr/bin/env python3
"""Write index.html and compositions/sN.html from the timing table, and bake the dissolves.

  python3 tools/build.py html            # index.html + compositions/s1..s6.html
  python3 tools/build.py transitions     # assets/transitions/*.mp4 (needs assets/shots/*.mp4)
  python3 tools/build.py check           # print each shot's source window against its length

Timing (root seconds): each shot shows from `in` to `out`; `src` is the source time shown at
`in`. A dissolve is centred on the cut between two shots and reads `dur/2` of source past the
cut on the outgoing shot and before it on the incoming one (the drain dissolve runs 1.0 s each
side). Scene dissolves (swirl) sit on the root's "dissolves" track; dissolves inside a scene
(melt) sit inside that scene's file. The underlying shots cut hard at the centre, under them.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS = {s["id"]: s for s in json.load(open(os.path.join(ROOT, "tools", "shots.json")))["shots"]}

SCENES = [  # id, start, end
    ("s1", 0.0, 10.0), ("s2", 10.0, 18.0), ("s3", 18.0, 28.0),
    ("s4", 28.0, 38.0), ("s5", 38.0, 50.0), ("s6", 50.0, 60.0),
]
# shot id, in, out, src
CUTS = [
    ("s1a", 0.0, 4.8, 0.0), ("s1b", 4.8, 10.0, 1.0),
    ("s2a", 10.0, 14.2, 0.8), ("s2b", 14.2, 18.0, 0.4),
    ("s3a", 18.0, 21.5, 0.8), ("s3b", 21.5, 24.9, 0.3), ("s3c", 24.9, 28.0, 0.3),
    ("s4a", 28.0, 31.1, 0.8), ("s4b", 31.1, 34.3, 0.3), ("s4c", 34.3, 38.0, 0.3),
    ("s5a", 38.0, 41.7, 0.8), ("s5b", 41.7, 45.3, 0.3), ("s5c", 45.3, 50.0, 0.3),
    ("s6a", 50.0, 55.3, 0.8), ("s6b", 55.3, 60.0, 0.3),
]
# dissolve after shot id: duration, mode, seed, drain
DISSOLVES = {
    "s1a": (2.0, "melt", 11, True),
    "s1b": (1.6, "swirl", 2, False),
    "s2a": (0.8, "melt", 13, False),
    "s2b": (1.6, "swirl", 5, False),
    "s3a": (0.6, "melt", 17, False),
    "s3b": (0.6, "melt", 19, False),
    "s3c": (1.6, "swirl", 7, False),
    "s4a": (0.6, "melt", 23, False),
    "s4b": (0.6, "melt", 29, False),
    "s4c": (1.6, "swirl", 3, False),
    "s5a": (0.6, "melt", 31, False),
    "s5b": (0.6, "melt", 37, False),
    "s5c": (1.6, "swirl", 9, False),
    "s6a": (0.6, "melt", 41, False),
}
FADE = (57.4, 59.2)  # fade to black
GROUND = "#000000"


def scene_of(t):
    for sid, a, b in SCENES:
        if a <= t < b:
            return sid
    return SCENES[-1][0]


def dissolve_windows():
    out = []
    for i, (sid, tin, tout, src) in enumerate(CUTS[:-1]):
        if sid not in DISSOLVES:
            continue
        nxt = CUTS[i + 1]
        dur, mode, seed, drain = DISSOLVES[sid]
        start = round(tout - dur / 2, 3)
        a_from = round(src + (start - tin), 3)
        b_from = round(nxt[3] - dur / 2, 3)
        out.append(dict(a=sid, b=nxt[0], start=start, dur=dur, mode=mode, seed=seed,
                        drain=drain, a_from=a_from, b_from=b_from,
                        file=f"assets/transitions/{sid}-{nxt[0]}.mp4"))
    return out


def fmt(x):
    return f"{x:.3f}".rstrip("0").rstrip(".") if x % 1 else f"{x:.1f}"


def video_tag(vid, src, start, dur, media_start, track, z):
    return (f'    <video id="{vid}" class="clip media" src="{src}" muted playsinline\n'
            f'      data-start="{fmt(start)}" data-duration="{fmt(dur)}" data-media-start="{fmt(media_start)}"\n'
            f'      data-track-index="{track}" style="z-index: {z}"></video>')


def write_html():
    diss = dissolve_windows()
    os.makedirs(os.path.join(ROOT, "compositions"), exist_ok=True)
    for sid, a, b in SCENES:
        lines = []
        for k, (shot, tin, tout, src) in enumerate([c for c in CUTS if scene_of(c[1]) == sid]):
            lines.append(video_tag(f"{shot}", f"assets/shots/{shot}.mp4", tin - a, tout - tin, src, 0, 1 + k))
        inner = [d for d in diss if d["mode"] == "melt" and scene_of(d["start"] + d["dur"] / 2) == sid]
        for d in inner:
            lines.append(video_tag(f"dz-{d['a']}-{d['b']}", d["file"], d["start"] - a, d["dur"], 0, 1, 20))
        extra_css, extra_html, extra_js = "", "", ""
        if sid == "s6":
            extra_css = ("    #fade { position: absolute; inset: 0; z-index: 40; background: #000; opacity: 0; }\n")
            extra_html = (f'    <div id="fade-host" class="clip" data-start="{fmt(FADE[0] - a - 0.1)}" '
                          f'data-duration="{fmt(b - FADE[0] + 0.1)}" data-track-index="2"\n'
                          '      style="position: absolute; inset: 0; z-index: 40"><div id="fade"></div></div>\n')
            extra_js = (f'      tl.fromTo("#fade", {{ opacity: 0 }}, {{ opacity: 1, duration: {fmt(FADE[1] - FADE[0])}, '
                        f'ease: "sine.inOut" }}, {fmt(FADE[0] - a)});\n')
        html = f"""<template>
  <script src="vendor/gsap.min.js"></script>
  <style>
    #root {{ position: absolute; inset: 0; overflow: hidden; background: {GROUND}; }}
    #root .media {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; }}
{extra_css}  </style>
  <!-- Written by tools/build.py from its timing table: retime there, then run it again. -->
  <div id="root" data-composition-id="{sid}" data-width="1080" data-height="1920" data-duration="{fmt(b - a)}">
{chr(10).join(lines)}
{extra_html}  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
{extra_js}      tl.set({{}}, {{}}, {fmt(b - a)});
      window.__timelines = window.__timelines || {{}};
      window.__timelines["{sid}"] = tl;
    }})();
  </script>
</template>
"""
        open(os.path.join(ROOT, "compositions", f"{sid}.html"), "w").write(html)

    hosts = []
    for i, (sid, a, b) in enumerate(SCENES):
        hosts.append(
            f'      <div id="el-{sid}" class="scene" data-track-kind="graphics"\n'
            f'        data-composition-id="{sid}" data-composition-src="compositions/{sid}.html"\n'
            f'        data-start="{fmt(a)}" data-duration="{fmt(b - a)}" data-track-index="0"></div>')
    swirls = []
    for d in [d for d in diss if d["mode"] == "swirl"]:
        swirls.append(
            f'      <video id="dz-{d["a"]}-{d["b"]}" class="clip media" src="{d["file"]}" muted playsinline\n'
            f'        data-start="{fmt(d["start"])}" data-duration="{fmt(d["dur"])}" data-media-start="0"\n'
            f'        data-track-index="1" style="z-index: 30"></video>')
    index = f"""<!doctype html>
<html lang="en" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="vendor/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #000; }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; }}
      #ground {{ position: absolute; inset: 0; background: {GROUND}; }}
      .scene {{ position: absolute; inset: 0; width: 100%; height: 100%; }}
      .media {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; }}
    </style>
  </head>
  <body>
    <!-- The Last King. Written by tools/build.py from its timing table: retime there, then run it again. -->
    <div id="root" data-composition-id="main" data-start="0" data-duration="60" data-fps="24" data-width="1080" data-height="1920">
      <div id="ground"></div>
      <!-- scenes -->
{chr(10).join(hosts)}
      <!-- swirling brushstroke dissolves between scenes -->
{chr(10).join(swirls)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      tl.set({{}}, {{}}, 60);
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
    open(os.path.join(ROOT, "index.html"), "w").write(index)
    print("wrote index.html and compositions/s1..s6.html")


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                        "default=nw=1:nk=1", path], capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


def check():
    diss = dissolve_windows()
    ok = True
    for i, (sid, tin, tout, src) in enumerate(CUTS):
        path = os.path.join(ROOT, "assets", "shots", f"{sid}.mp4")
        length = probe(path) if os.path.exists(path) else SHOTS[sid]["seconds"]
        after = next((d["dur"] / 2 if not d["drain"] else d["dur"] / 2 for d in diss if d["a"] == sid), 0)
        before = next((d["dur"] / 2 for d in diss if d["b"] == sid), 0)
        need_from, need_to = src - before, src + (tout - tin) + after
        flag = "" if need_from >= -1e-6 and need_to <= length + 1e-6 else "  <-- OUT OF RANGE"
        ok &= not flag
        print(f"{sid}: shows {tin:5.1f}-{tout:5.1f}  source {need_from:4.2f}-{need_to:4.2f} of {length:4.2f}{flag}")
    return ok


def bake(only=None):
    tool = os.path.join(ROOT, "tools", "brush_transition.py")
    os.makedirs(os.path.join(ROOT, "assets", "transitions"), exist_ok=True)
    for d in dissolve_windows():
        if only and d["a"] not in only and d["b"] not in only:
            continue
        cmd = [sys.executable, tool, "--a", f"assets/shots/{d['a']}.mp4", "--a-from", str(d["a_from"]),
               "--b", f"assets/shots/{d['b']}.mp4", "--b-from", str(d["b_from"]),
               "--dur", str(d["dur"]), "--mode", d["mode"], "--seed", str(d["seed"]), "--out", d["file"]]
        if d["drain"]:
            cmd.append("--drain")
        subprocess.run(cmd, cwd=ROOT, check=True)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else ""
    if what == "html":
        write_html()
    elif what == "transitions":
        bake(sys.argv[2:])
    elif what == "check":
        sys.exit(0 if check() else 1)
    else:
        raise SystemExit(__doc__)
