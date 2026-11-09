#!/usr/bin/env python3
"""Lay the film out from script.json and, once it exists, the user's own recording.

  python3 tools/assemble.py

Timing source:
  default (the user's choice) a SILENT film: no voice, the speech is shown as subtitles; each line gets a
                            reading time and the film is fitted to script.json "target" (90 s).
  assets/voice/words.json   only if a recording is ever added: the words as spoken, with times
                            (tools/align.py), which then replace the reading times.

Writes:
  cues.js                     window.CUES: scene windows, named cue times, every word (absolute s)
  index.html                  root: ground, scene hosts, captions, chrome, voice, music, sfx
  compositions/captions.html  one timed caption group per 2-5 spoken words
  compositions/<id>.html      each scene, rendered from tools/scenes/<id>.html with its cue times

No presenter, no avatar, no voice, no footage: drawings, music and subtitles (the user's choices).
"""
import html
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
script = json.loads((ROOT / "script.json").read_text())
SCENES = script["scenes"]
PUNCT = "،,.!?؟:;«»\"'()"
END_PUNCT = tuple("،,.!?؟:;")
SENT_END = tuple(".!?؟:;")


def bare(w):
    return w.strip(PUNCT)


def ffprobe_len(p):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
        capture_output=True, text=True,
    ).stdout.strip()
    return float(out) if out else None


def find_media(folder, stem):
    for ext in (".wav", ".m4a", ".mp3", ".aac", ".ogg", ".opus", ".flac", ".mp4", ".webm", ".mov"):
        p = ROOT / folder / f"{stem}{ext}"
        if p.exists():
            return p
    return None


# ---- subtitle lines --------------------------------------------------------------------------
MAX_CHARS, MAX_WORDS = 27, 5  # one line of 62 px Cairo 800 inside 908 px


def clen(ws):
    return sum(len(x["text"]) + 1 for x in ws) - 1


def balanced(run):
    """Split one phrase into the fewest lines that fit, the longest line as short as possible (no orphan word)."""
    from itertools import combinations
    L = len(run)
    for n in range(1, L + 1):
        best = None
        for cuts in combinations(range(1, L), n - 1):
            parts = [run[a:b] for a, b in zip((0,) + cuts, cuts + (L,))]
            if any(clen(g) > MAX_CHARS or len(g) > MAX_WORDS for g in parts):
                continue
            score = (max(clen(g) for g in parts), -min(len(g) for g in parts))
            if best is None or score < best[0]:
                best = (score, parts)
        if best:
            return best[1]
    return [[w] for w in run]

def phrases(sw):
    """Phrases of one scene: a sentence end, a pause, or a comma once the phrase has 3 words
    (keeps lists like 15، 19، 177 together)."""
    out, run = [], []
    for i, w in enumerate(sw):
        run.append(w)
        nxt = sw[i + 1] if i + 1 < len(sw) else None
        long_pause = nxt is not None and "start" in w and nxt["start"] - w["end"] >= 0.35
        stop = w["text"].endswith(SENT_END) or (w["text"].endswith(("،", ",")) and len(run) >= 3)
        if nxt is None or stop or long_pause:
            out.append(run)
            run = []
    return out


voice = find_media("assets/voice", "voice")
words_path = ROOT / "assets/voice/words.json"

# ---- words ----------------------------------------------------------------------------------
if words_path.exists():
    MODE = "voice"
    words = json.loads(words_path.read_text())
    for sc in SCENES:
        assert any(w["scene"] == sc["id"] for w in words), f"no spoken words for {sc['id']}"
else:
    # Silent film (the user's choice): no voice, the speech is read as subtitles. Every line gets a reading
    # time (0.5 s + 0.25 s a word + 0.03 s a character), scenes follow one another, and the whole film is
    # stretched or squeezed to the target length (script.json "target", 90 s: about 10 characters a second).
    MODE = "read"
    LEAD, TAIL, GAP, SENT_PAUSE, END_HOLD = 0.45, 0.4, 0.1, 0.2, 2.2  # the last frame holds 2.2 s after the last line
    plan = []
    for sc in SCENES:
        toks = [{"scene": sc["id"], "text": t} for t in sc["text"].split()]
        lines = [ln for ph in phrases(toks) for ln in balanced(ph)]
        plan.append((sc, lines))
    weight = lambda ln: 0.5 + 0.25 * len(ln) + 0.03 * clen(ln)
    n_lines = sum(len(ls) for _, ls in plan)
    fixed = len(plan) * (LEAD + TAIL) + (END_HOLD - TAIL) + GAP * (n_lines - len(plan)) + SENT_PAUSE * sum(
        1 for _, ls in plan for ln in ls[:-1] if ln[-1]["text"].endswith(SENT_END))
    k = (float(script["target"]) - fixed) / sum(weight(ln) for _, ls in plan for ln in ls)
    words, read_lines, t = [], [], 0.0
    for sc, lines in plan:
        t += LEAD
        for li, ln in enumerate(lines):
            d = weight(ln) * k
            n_ch = clen(ln) or 1
            acc = 0
            for wi, w in enumerate(ln):
                ws = t + 0.55 * d * acc / n_ch
                acc += len(w["text"]) + 1
                we = t + d - 0.02 if wi == len(ln) - 1 else min(t + d - 0.02, ws + 0.3)
                words.append({**w, "start": round(ws, 3), "end": round(we, 3)})
            read_lines.append((ln[0]["scene"], len(words) - len(ln), len(words), round(t, 3), round(t + d, 3)))
            t += d
            if li < len(lines) - 1:
                t += GAP + (SENT_PAUSE if ln[-1]["text"].endswith(SENT_END) else 0)
        t += TAIL if sc is not plan[-1][0] else END_HOLD
    print(f"reading speed {sum(len(sc['text']) for sc in SCENES) / script['target']:.1f} characters a second")

# ---- scene windows ----------------------------------------------------------------------------
first = {sc["id"]: next(w for w in words if w["scene"] == sc["id"]) for sc in SCENES}
last = {sc["id"]: [w for w in words if w["scene"] == sc["id"]][-1] for sc in SCENES}
starts = []
for i, sc in enumerate(SCENES):
    if i == 0:
        starts.append(0.0)
        continue
    prev_end = last[SCENES[i - 1]["id"]]["end"]
    nxt = first[sc["id"]]["start"]
    # cut a little before the first word, never before the previous scene's last word ends
    starts.append(round(max(prev_end + 0.05, nxt - min(0.4, (nxt - prev_end) * 0.6)), 3))

media_len = ffprobe_len(voice) if voice else None
if MODE == "voice":
    total = max(last[SCENES[-1]["id"]]["end"] + 1.2, media_len or 0)
else:
    total = float(script["target"])
TOTAL = round(total, 3)

scene_win = {}
for i, sc in enumerate(SCENES):
    end = starts[i + 1] if i + 1 < len(SCENES) else TOTAL
    scene_win[sc["id"]] = {"start": starts[i], "end": round(end, 3)}

# ---- named cues ----------------------------------------------------------------------------------
at = {}
for sc in SCENES:
    sw = [w for w in words if w["scene"] == sc["id"]]
    for name, needle in sc.get("cues", {}).items():
        hit = next((w for w in sw if needle in bare(w["text"]) or bare(w["text"]) in needle and len(bare(w["text"])) > 2), None)
        if hit is None:
            print(f"warning: cue {sc['id']}.{name} ('{needle}') not spoken; placed at scene middle")
            win = scene_win[sc["id"]]
            at[f"{sc['id']}.{name}"] = round((win["start"] + win["end"]) / 2, 3)
        else:
            at[f"{sc['id']}.{name}"] = hit["start"]

cues = {"mode": MODE, "duration": TOTAL, "scenes": scene_win, "at": at,
        "words": [{"s": w["scene"], "t": w["text"], "a": w["start"], "b": w["end"]} for w in words]}
(ROOT / "cues.js").write_text(
    "// generated by tools/assemble.py: do not edit by hand\nwindow.CUES = "
    + json.dumps(cues, ensure_ascii=False, indent=1) + ";\n")

# ---- scene files: tools/scenes/<id>.html → compositions/<id>.html --------------------------------
# {{expr}} in a scene source is evaluated with the scene's cue names as scene-local seconds and `end` as
# the scene's length, e.g. data-start="{{drains}}" data-duration="{{balcony-drains}}".
TOKEN = re.compile(r"\{\{([^}]+)\}\}")
broll_warn = []
FONTS = (ROOT / "tools/fonts.css").read_text().rstrip()
for src in sorted((ROOT / "tools/scenes").glob("*.html")):
    sid = src.stem
    win = scene_win.get(sid, {"start": 0.0, "end": TOTAL})
    ns = {k.split(".", 1)[1]: round(v - win["start"], 3) for k, v in at.items() if k.startswith(sid + ".")}
    ns["end"] = round(win["end"] - win["start"], 3)
    sc = {"id": sid}
    text = src.read_text().replace("/*FONTS*/", FONTS.strip())
    out_txt = TOKEN.sub(lambda m: f"{max(0.0, eval(m.group(1), {'__builtins__': {}}, ns)):.3f}", text)
    # a b-roll window longer than its clip would go blank: warn
    for m in re.finditer(r'<video[^>]*src="([^"]+)"[^>]*data-duration="([0-9.]+)"', out_txt):
        L = ffprobe_len(ROOT / m.group(1))
        if L and float(m.group(2)) > L - 0.05:
            broll_warn.append(f"{sc['id']}: {m.group(1)} shown {m.group(2)} s but lasts {L:.2f} s")
    (ROOT / "compositions" / f"{sc['id']}.html").write_text(
        "<!-- generated from tools/scenes/" + sc["id"] + ".html by tools/assemble.py: edit the source -->\n" + out_txt)
for w_ in broll_warn:
    print("warning:", w_)

# ---- captions: groups of the spoken words --------------------------------------------------------
if MODE == "read":
    windows = [(words[i0:i1], max(0.1, a), b) for _, i0, i1, a, b in read_lines]
else:
    groups = [ln for sc in SCENES for ph in phrases([w for w in words if w["scene"] == sc["id"]]) for ln in balanced(ph)]
    windows = []
    for i, g in enumerate(groups):
        a = max(0.1, g[0]["start"] - 0.06)
        nxt = groups[i + 1][0]["start"] - 0.06 if i + 1 < len(groups) else TOTAL
        windows.append((g, a, min(TOTAL, nxt, max(g[-1]["end"] + 0.45, a + 0.9))))
groups = [g for g, _, _ in windows]

cap_rows = []
for i, (g, a, b) in enumerate(windows):
    text = " ".join(html.escape(w["text"]) for w in g)
    cap_rows.append(
        f'    <div id="cap-{i}" class="cap clip" data-start="{a:.3f}" data-duration="{b - a:.3f}">'
        f'<span class="cap-t">{text}</span></div>')

captions_html = f"""<template>
  <style>
    @font-face {{ font-family: "Cairo"; src: url("assets/fonts/cairo-arabic-800-normal.woff2") format("woff2"); font-weight: 800; unicode-range: U+0600-06FF, U+0750-077F, U+0870-088E, U+0890-0891, U+0897-08E1, U+08E3-08FF, U+200C-200E, U+2010-2011, U+204F, U+2E41, U+FB50-FDFF, U+FE70-FE74, U+FE76-FEFC; }}
    @font-face {{ font-family: "Cairo"; src: url("assets/fonts/cairo-latin-800-normal.woff2") format("woff2"); font-weight: 800; unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+2000-206F, U+20AC, U+2122, U+2190-2193, U+2212, U+FEFF; }}
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    /* subtitles: bottom edge at 1590 px, clear of the bottom 15 % (1632 px) */
    .cap {{ position: absolute; left: 0; right: 0; bottom: 330px; padding: 0 56px; text-align: center; direction: rtl; overflow: visible; }}
    .cap-t {{
      display: inline-block; max-width: 968px; white-space: nowrap; font-family: "Cairo", sans-serif; font-weight: 800;
      font-size: 62px; line-height: 1.32; color: #FFFFFF;
      background: rgba(7, 17, 31, 0.86); border-radius: 16px; padding: 6px 30px 14px;
      -webkit-box-decoration-break: clone; box-decoration-break: clone;
    }}
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
{chr(10).join(cap_rows)}
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      document.querySelectorAll("#root .cap").forEach((el) => {{
        const s = parseFloat(el.dataset.start);
        tl.fromTo(el.querySelector(".cap-t"), {{ opacity: 0, y: 10 }},
          {{ opacity: 1, y: 0, duration: 0.14, ease: "power2.out" }}, s);
      }});
      window.__timelines["captions"] = tl;
    }})();
  </script>
</template>
"""
(ROOT / "compositions/captions.html").write_text(captions_html)

# ---- sound: music only (the user's choice: no voice, no sound effects) -------------------------------
sfx = []

# ---- index.html -------------------------------------------------------------------------------------
def host(id_, z, track, kind="graphics", start=0.0, dur=TOTAL):
    return (f'      <div id="{id_}" class="scene" data-composition-id="{id_}" data-composition-src="compositions/{id_}.html"\n'
            f'        data-start="{start:.3f}" data-duration="{dur:.3f}" data-track-index="{track}" '
            f'data-track-kind="{kind}" style="z-index: {z}"></div>')


rows = [host("ground", 1, 1)]
for sc in SCENES:
    w = scene_win[sc["id"]]
    rows.append(host(sc["id"], 2, 2, start=w["start"], dur=w["end"] - w["start"]))
rows.append(host("chrome", 9, 4))
rows.append(host("captions", 10, 5, kind="captions"))
if voice:
    rows.append(f'      <audio id="voice" class="clip" src="assets/voice/{voice.name}" data-start="0" '
                f'data-duration="{min(TOTAL, media_len):.3f}" data-volume="1" data-track-index="10"></audio>')
music = ROOT / "assets/music/bed.m4a"
if music.exists():
    rows.append(f'      <audio id="music" class="clip" src="assets/music/bed.m4a" data-start="0" data-duration="{TOTAL}" '
                f'data-volume="{0.32 if MODE == "voice" else 1}" data-track-index="11"></audio>')

index = f"""<!doctype html>
<html lang="ar" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="vendor/gsap.min.js"></script>
    <script src="geo.js"></script>
    <script src="cues.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #0A1626; }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; }}
      .scene {{ position: absolute; inset: 0; width: 100%; height: 100%; }}
    </style>
  </head>
  <body>
    <!-- generated by tools/assemble.py ({MODE} timing): do not edit by hand -->
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
{chr(10).join(rows)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""
(ROOT / "index.html").write_text(index)
print(f"{MODE} timing, {TOTAL} s, {len(words)} words, {len(groups)} caption groups, {len(sfx)} sfx")
for sc in SCENES:
    w = scene_win[sc["id"]]
    print(f"  {sc['id']}: {w['start']:7.3f} → {w['end']:7.3f}  ({w['end'] - w['start']:.2f} s)")
