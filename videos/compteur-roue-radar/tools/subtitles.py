#!/usr/bin/env python3
"""Readable French subtitles for compteur-roue-radar.

Run after `captions.mjs build` (which writes compositions/captions.html with the
caption skin). This script:

  1. regroups the on-screen subtitles into phrases of up to 9 words, cut at
     punctuation (captions.mjs groups 2–4 words, a karaoke rhythm too fast for a
     teaching video), and lets the last one clear instead of holding to the end;
  2. points the captions at the vendored GSAP (the render browser has no CDN) and
     sizes the skin for subtitles (44 px, tight word spacing);
  3. writes livrables/compteur-roue-radar.srt with the WHOLE narration, including
     the lines kept off screen because they are already shown in large type
     (the question, the dialogue bubbles, the closing sentence).

Words come from audio_meta.json (tools/voice.py); phrases without words get
their words spread over the phrase by length.

  python3 tools/subtitles.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
meta = json.loads((ROOT / "audio_meta.json").read_text())
cues = json.loads((ROOT / "voice_cues.json").read_text())
durs = [cues[str(i)]["duration_s"] for i in range(1, 11)]
start = {i + 1: sum(durs[:i]) for i in range(10)}
DISPLAY = [("kilomètres-heure", "km/h")]


def display(text):
    for a, b in DISPLAY:
        text = text.replace(a, b)
    return text


def merge_punct(words):
    """Fold lone punctuation tokens (« : », « », »…) into their neighbours, French spacing."""
    out = []
    for w in words:
        t = w["text"]
        if t in ("«",) and out is not None:
            w = dict(w, text=t)
            out.append(w)
            continue
        if re.fullmatch(r"[:;!?»…]+|»…", t) and out:
            out[-1] = dict(out[-1], text=out[-1]["text"] + " " + t, end=w["end"])
            continue
        if out and out[-1]["text"] == "«":
            out[-1] = dict(w, text="« " + t, start=out[-1]["start"])
            continue
        out.append(dict(w))
    return out


def spread(text, t0, t1):
    ws = text.split()
    weights = [len(w) + 1 for w in ws]
    tot = sum(weights)
    out, t = [], t0
    for w, k in zip(ws, weights):
        d = (t1 - t0) * k / tot
        out.append({"text": w, "start": t, "end": t + d})
        t += d
    return out


def group(words, max_words, max_chars, gap=0.35):
    """Cut at punctuation, rejoin short pieces of the same sentence, split long clauses evenly."""
    text = lambda ws: " ".join(w["text"] for w in ws)
    clauses, cur = [], []
    for w in words:
        if cur and (w["frame"] != cur[-1]["frame"] or w["start"] - cur[-1]["end"] > gap):
            clauses.append(cur)
            cur = []
        cur.append(w)
        if re.search(r"[.!?…,:;]$|[.!?…] ?»$", w["text"]):
            clauses.append(cur)
            cur = []
    if cur:
        clauses.append(cur)
    merged = []
    for c in clauses:
        prev = merged[-1] if merged else None
        if (prev and prev[-1]["frame"] == c[0]["frame"] and c[0]["start"] - prev[-1]["end"] <= gap
                and not re.search(r"[.!?…]$|[.!?…] ?»$", prev[-1]["text"])
                and len(prev) + len(c) <= max_words and len(text(prev + c)) <= max_chars):
            merged[-1] = prev + c
        else:
            merged.append(c)
    groups = []
    for c in merged:
        k = 1
        while len(c) / k > max_words or len(text(c)) / k > max_chars:
            k += 1
        size = -(-len(c) // k)
        groups += [c[i:i + size] for i in range(0, len(c), size)]
    return groups


# ── on-screen subtitles (only the words voice.py kept for captions) ──
screen = []
for v in meta["voices"]:
    for w in merge_punct(v["words"]):
        screen.append({"frame": v["frame"], "text": display(w["text"]), "start": start[v["frame"]] + w["start"], "end": start[v["frame"]] + w["end"]})
G = []
groups = group(screen, max_words=9, max_chars=46)
for gi, g in enumerate(groups):
    nxt = groups[gi + 1][0]["start"] if gi + 1 < len(groups) else None
    end = g[-1]["end"] + 0.15
    if nxt is not None:
        end = min(end, nxt - 0.02)
    G.append({
        "id": f"caption-group-{gi}", "frame": g[0]["frame"], "start": round(g[0]["start"], 3), "end": round(end, 3),
        "text": " ".join(w["text"] for w in g),
        "words": [{"id": f"caption-word-{gi}-{i}", "text": w["text"], "start": round(w["start"], 3), "end": round(w["end"], 3)} for i, w in enumerate(g)],
    })

cap = ROOT / "compositions/captions.html"
html = cap.read_text()
html = re.sub(r"var GROUPS = \[.*?\];\n", lambda m: "var GROUPS = " + json.dumps(G, ensure_ascii=False).replace("<", "\\u003c") + ";\n", html, count=1, flags=re.S)
html = html.replace('<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>', '<script src="vendor/gsap.min.js"></script>')
html = html.replace("var end = isLast ? DURATION :", "var end = isLast ? Math.min(DURATION, Number(group.end) + 0.3) :")
# subtitle proportions: the preset skin is sized for 2–4-word karaoke captions
for old, new in (("gap: 0.1em 0.34em;", "gap: 0.06em 0.14em;"), ("font-size: clamp(40px, 4.4vw, 58px);", "font-size: 44px;"), ("padding: 0 0.18em;", "padding: 0 0.08em;"), ("padding: 20px 44px 24px;", "padding: 14px 34px 18px;")):
    html = html.replace(old, new)
cap.write_text(html)
(ROOT / "caption_groups.json").write_text(json.dumps({"total_duration_s": sum(durs), "width": 1920, "height": 1080, "groups": G}, ensure_ascii=False, indent=2))

# ── .srt: every spoken phrase ──
allw = []
for f in range(1, 11):
    v = next(x for x in meta["voices"] if x["frame"] == f)
    have = merge_punct(v["words"])
    for p in cues[str(f)]["phrases"]:
        inside = [w for w in have if p["start"] - 0.05 <= w["start"] < p["end"]]
        ws = inside if inside else spread(p["text"], p["start"], p["end"])
        for w in ws:
            allw.append({"frame": f, "text": display(w["text"]), "start": start[f] + w["start"], "end": start[f] + w["end"]})


def ts(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def two_lines(text, width=42):
    if len(text) <= width:
        return text
    words, best = text.split(), None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        score = max(len(a), len(b))
        if best is None or score < best[0]:
            best = (score, a + "\n" + b)
    return best[1]


srt = []
sgroups = group(allw, max_words=14, max_chars=80, gap=0.6)
for i, g in enumerate(sgroups):
    a = g[0]["start"]
    b = g[-1]["end"] + 0.2
    if i + 1 < len(sgroups):
        b = min(b, sgroups[i + 1][0]["start"] - 0.04)
    srt.append(f"{i + 1}\n{ts(a)} --> {ts(b)}\n{two_lines(' '.join(w['text'] for w in g))}\n")
out = ROOT / "livrables/compteur-roue-radar.srt"
out.parent.mkdir(exist_ok=True)
out.write_text("\n".join(srt), encoding="utf-8")
print(f"on screen: {len(G)} subtitle(s) · srt: {len(srt)} cue(s) → {out.relative_to(ROOT)}")
