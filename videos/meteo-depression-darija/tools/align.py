#!/usr/bin/env python3
"""Time the script's words on the user's own recording.

  npx hyperframes transcribe assets/voice/voice.<ext> --model large-v3 --language ar --json
  python3 tools/align.py assets/transcript.json

The transcript gives each heard word a time; the script gives the spelling. Words are matched in
order (Arabic normalised: no diacritics, unified alef/ya/ta marbuta, clitics tolerated). Writes:

  assets/voice/words.json        [{scene, text, start, end}] in speaking order → tools/assemble.py
  assets/voice/align-report.md   every place where what was heard differs from the script

The report must be read before rendering: where the speaker said something other than the script,
words.json is edited so the captions follow the recording word for word.
"""
import difflib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
script = json.loads((ROOT / "script.json").read_text())
raw = json.loads(Path(sys.argv[1]).read_text())
heard = raw if isinstance(raw, list) else raw.get("words") or [w for s in raw.get("segments", []) for w in s.get("words", [])]
heard = [{"text": (w.get("text") or w.get("word") or "").strip(), "start": float(w["start"]), "end": float(w["end"])} for w in heard]
heard = [w for w in heard if w["text"] and not re.fullmatch(r"[♪�\W]+", w["text"])]

DIAC = re.compile(r"[ً-ْٰـ]")


def norm(w):
    w = DIAC.sub("", w)
    w = re.sub(r"[^\w.]", "", w)
    w = re.sub("[أإآٱ]", "ا", w).replace("ة", "ه").replace("ى", "ي").replace("ڤ", "ف")
    return w.lower()


def close(a, b):
    a, b = norm(a), norm(b)
    if not a or not b:
        return False
    if a == b:
        return True
    for p in ("و", "ف", "ل", "ب", "ال", "وال", "فال"):
        if a == p + b or b == p + a:
            return True
    return difflib.SequenceMatcher(None, a, b).ratio() >= 0.72


toks = [(sc["id"], t) for sc in script["scenes"] for t in sc["text"].split()]
A = [norm(t) for _, t in toks]
B = [norm(w["text"]) for w in heard]
sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
times = [None] * len(toks)
report = []
for op, i1, i2, j1, j2 in sm.get_opcodes():
    if op == "equal":
        for k in range(i2 - i1):
            times[i1 + k] = (heard[j1 + k]["start"], heard[j1 + k]["end"])
        continue
    # pair what can be paired by spelling, in order
    j = j1
    for i in range(i1, i2):
        for jj in range(j, j2):
            if close(toks[i][1], heard[jj]["text"]):
                times[i] = (heard[jj]["start"], heard[jj]["end"])
                j = jj + 1
                break
    report.append(f"- script «{' '.join(t for _, t in toks[i1:i2]) or '∅'}» ↔ heard «{' '.join(w['text'] for w in heard[j1:j2]) or '∅'}» "
                  f"({heard[j1]['start'] if j1 < len(heard) else '?'} s)")

# words never heard get times between their neighbours (by character length)
k = 0
while k < len(toks):
    if times[k] is not None:
        k += 1
        continue
    a = k
    while k < len(toks) and times[k] is None:
        k += 1
    t0 = times[a - 1][1] if a > 0 else 0.2
    t1 = times[k][0] if k < len(toks) else t0 + 0.4 * (k - a)
    span = max(0.2, t1 - t0)
    weights = [len(norm(toks[i][1])) + 1 for i in range(a, k)]
    acc = t0
    for i, wt in zip(range(a, k), weights):
        d = span * wt / sum(weights)
        times[i] = (acc, acc + d * 0.9)
        acc += d

words = [{"scene": sid, "text": t, "start": round(s, 3), "end": round(e, 3)} for (sid, t), (s, e) in zip(toks, times)]
(ROOT / "assets/voice/words.json").write_text(json.dumps(words, ensure_ascii=False, indent=1))
(ROOT / "assets/voice/align-report.md").write_text(
    "# Script vs recording\n\n" + ("\n".join(report) if report else "No differences: the recording follows the script.") + "\n")
matched = sum(1 for o in sm.get_opcodes() if o[0] == "equal" for _ in range(o[2] - o[1]))
print(f"{len(words)} script words, {len(heard)} heard, {matched} exact matches, {len(report)} places to check → assets/voice/align-report.md")
