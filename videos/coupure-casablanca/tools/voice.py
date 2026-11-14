#!/usr/bin/env python3
"""Voice layout: phrases (the person's recording cut by tools/recording.py, or HeyGen TTS) -> data/cues.json.

  python3 tools/voice.py --voice <voice_id>      # generates missing phrases, then lays out
  python3 tools/voice.py                         # lay out only (uses script.json "voice")

Writes assets/voice/ph/<id>.wav (trimmed), assets/voice/scene-<sid>.wav (avatar input, one per scene),
assets/voice/voice.wav (whole film), data/cues.json (scene starts/durations, scene-local phrase windows,
marks, caption words, sound effects).
"""
import argparse, json, re, subprocess, wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SR = 44100
ap = argparse.ArgumentParser()
ap.add_argument("--voice")
ap.add_argument("--only", help="comma list of phrase ids to (re)generate")
args = ap.parse_args()
SCRIPT = json.loads((ROOT / "script.json").read_text())
if args.voice:
    SCRIPT["voice"] = args.voice
    (ROOT / "script.json").write_text(json.dumps(SCRIPT, ensure_ascii=False, indent=2) + "\n")
VOICE = SCRIPT["voice"]
PH_DIR = ROOT / "assets/voice/ph"
PH_DIR.mkdir(parents=True, exist_ok=True)


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode:
        raise SystemExit(f"FAILED: {' '.join(cmd[:6])}…\n{r.stdout[-1500:]}\n{r.stderr[-1500:]}")
    return r.stdout


def read_wav(p):
    with wave.open(str(p)) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float32) / 32768
        return x.reshape(-1, w.getnchannels()).mean(axis=1)


def write_wav(p, x):
    p.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(p), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())


# 1. generate + trim every phrase
only = set(args.only.split(",")) if args.only else None
env = {**__import__("os").environ, "NODE_USE_ENV_PROXY": "1"}
for sc in SCRIPT["scenes"]:
    for p in sc["phrases"]:
        raw = PH_DIR / f"{p['id']}.mp3"
        out = PH_DIR / f"{p['id']}.wav"
        if out.exists() and not raw.exists():
            continue                      # cut from the person's own recording (tools/recording.py)
        if (not raw.exists()) or (only and p["id"] in only):
            if not VOICE:
                raise SystemExit("no voice chosen: pass --voice <id>")
            run(["npx", "hyperframes", "media-use", "generate", "--type", "voice", "--script", p.get("say", p["text"]),
                 "--voice", VOICE, "--out", str(raw.relative_to(ROOT))], cwd=ROOT, env=env)
        if (not out.exists()) or out.stat().st_mtime < raw.stat().st_mtime:
            run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-ac", "1", "-ar", str(SR), "-af",
                 "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.03,areverse,"
                 "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse", str(out)])

PH = {p["id"]: read_wav(PH_DIR / f"{p['id']}.wav") for sc in SCRIPT["scenes"] for p in sc["phrases"]}
LEN = {k: len(v) / SR for k, v in PH.items()}

# 2. lay out the scenes (scene-local seconds). Targets follow the brief (3–4 min film); a scene shorter
#    than its target gets longer breaths between lines (+1.2 s at most each), a longer lead-in and a
#    longer final hold (3 s at most), never stretched speech.
TARGET = {"s1": 28, "s2": 38, "s3": 40, "s4": 38, "s5": 38, "s6": 30}
layout, durs, marks = {}, {}, {}
for sc in SCRIPT["scenes"]:
    sid, pl = sc["id"], {}
    if sid == "s2":
        dark_t0, a = 1.6, 0.9
        pl["s2a"] = [a, a + LEN["s2a"]]
        T2 = max(TARGET["s2"], LEN["s2a"] + LEN["s2b"] + 14)
        step = min(1.35, max(0.8, (T2 - 13.4 - dark_t0) / 19))
        lit_t0 = round(max(dark_t0 + 19 * step + 0.9, pl["s2a"][1] + 1.0), 3)
        pl["s2b"] = [lit_t0, lit_t0 + LEN["s2b"]]
        off_t = lit_t0 + 5.2
        durs[sid] = round(max(off_t + 6.0, pl["s2b"][1] + 4.5, T2), 3)
        marks[sid] = {"dark_start": dark_t0, "dark_step": round(step, 3), "lit_start": lit_t0, "lit_step": 0.9, "offframe": off_t}
    else:
        phs = sc["phrases"]
        pauses = [p.get("pause", 0.5) for p in phs]
        lead, hold = 0.5, {"s6": 1.4, "s1": 0.6}.get(sid, 0.9)
        natural = lead + sum(LEN[p["id"]] for p in phs) + sum(pauses[:-1]) + hold + 0.6
        extra = TARGET[sid] - natural
        if extra > 0:
            k = len(phs) - 1
            add = min(1.2, extra * 0.65 / max(1, k))
            pauses = [x + add for x in pauses[:-1]] + pauses[-1:]
            extra -= add * k
            la = min(0.8, extra * 0.3); lead += la; extra -= la
            hold += min(3.0, max(0.0, extra))
        t = lead
        for p, ps in zip(phs, pauses):
            pl[p["id"]] = [round(t, 3), round(t + LEN[p["id"]], 3)]
            t += LEN[p["id"]] + ps
        durs[sid] = round(t - pauses[-1] + hold + 0.6, 3)
    layout[sid] = {k: [round(a, 3), round(b, 3)] for k, (a, b) in pl.items()}


def frac_before(text, needle):
    i = text.find(needle)
    return max(0.0, i / max(1, len(text))) if i >= 0 else 0.5


s1a = next(p for p in SCRIPT["scenes"][0]["phrases"] if p["id"] == "s1a")
a, b = layout["s1"]["s1a"]
marks["s1"] = {"time_word": round(a + (b - a) * frac_before(s1a.get("say", s1a["text"]), "ستّاش"), 3)}
s4b = next(p for sc in SCRIPT["scenes"] for p in sc["phrases"] if p["id"] == "s4b")
a, b = layout["s4"]["s4b"]
marks["s4"] = {"touch": round(a + (b - a) * frac_before(s4b["text"], "كيوقع"), 3)}

# 3. absolute timeline: scenes back to back, then the end card
ORDER = ["s1", "s2", "s3", "s4", "s5", "s6"]
starts, t = {}, 0.0
for sid in ORDER:
    starts[sid] = round(t, 3)
    t += durs[sid]
starts["end"] = round(t, 3)
END_DUR = 7.0
TOTAL = round(t + END_DUR, 3)

film = np.zeros(int(TOTAL * SR) + SR)
for sid in ORDER:
    scene = np.zeros(int(durs[sid] * SR) + 1)
    for pid, (a, _) in layout[sid].items():
        x = PH[pid]
        i = int(a * SR)
        scene[i:i + len(x)] += x[: len(scene) - i]
        j = int((starts[sid] + a) * SR)
        film[j:j + len(x)] += x
    write_wav(ROOT / f"assets/voice/scene-{sid}.wav", scene)
film = film[: int(TOTAL * SR)]
write_wav(ROOT / "assets/voice/voice.wav", film)

# 4. caption words: the script's own words, timed by character share inside each phrase
words = []
for sc in SCRIPT["scenes"]:
    for p in sc["phrases"]:
        a, b = layout[sc["id"]][p["id"]]
        a += starts[sc["id"]]; b += starts[sc["id"]]
        toks = p["text"].split()
        w = np.array([len(re.sub(r"[،,.:؟?]", "", x)) + 1.5 for x in toks], dtype=float)
        edges = a + (b - a) * np.concatenate([[0], np.cumsum(w) / w.sum()])
        for k, tok in enumerate(toks):
            words.append({"id": f"w{len(words)}", "phrase": p["id"], "text": tok, "start": round(float(edges[k]), 3), "end": round(float(edges[k + 1]), 3)})

# 5. sound effects (absolute seconds), each with a cause on screen
S = lambda sid, x: round(starts[sid] + x, 3)
sfx = []
cuts = ["whoosh-short", "whoosh", "whoosh-short", "whoosh", "whoosh-short", "whoosh"]
for i, sid in enumerate(ORDER[1:] + ["end"]):
    sfx.append({"file": f"{cuts[i]}.wav", "t": starts[sid] - 0.12, "d": 0.57, "v": 0.32})
f1 = marks["s1"]["time_word"]
m2 = marks["s2"]
for i in range(19):
    tt = m2["dark_start"] + i * m2["dark_step"] + 0.32
    sfx.append({"file": "click-soft.wav" if i % 2 == 0 else "click.wav", "t": S("s2", tt), "d": 0.36, "v": 0.22 if i % 2 == 0 else 0.13})
for i in range(5):
    sfx.append({"file": "pop.wav", "t": S("s2", m2["lit_start"] + i * m2["lit_step"]), "d": 0.6, "v": 0.16})
s3f = layout["s3"]["s3f"]
sfx.append({"file": "glitch-2.wav", "t": S("s3", s3f[0] + (s3f[1] - s3f[0]) * 0.22), "d": 0.7, "v": 0.22, "fo": 0.2})
tch = marks["s4"]["touch"]
sfx.append({"file": "glitch-1.wav", "t": S("s4", tch), "d": 0.9, "v": 0.3, "fo": 0.25})
sfx.append({"file": "impact-bass-2.wav", "t": S("s4", tch), "d": 2.0, "v": 0.4, "fo": 0.6})
s4c = layout["s4"]["s4c"]
sfx.append({"file": "click.wav", "t": S("s4", s4c[0] + (s4c[1] - s4c[0]) * 0.3), "d": 0.36, "v": 0.5})
for k in ("s5b", "s5c", "s5d", "s5e", "s5f"):
    sfx.append({"file": "pop.wav", "t": S("s5", layout["s5"][k][0] + 0.1), "d": 0.6, "v": 0.26})
for k, fr in (("s6d", 0.4), ("s6e", 0.05), ("s6f", 0.05)):
    a, b = layout["s6"][k]
    sfx.append({"file": "click-soft.wav", "t": S("s6", a + (b - a) * fr), "d": 0.36, "v": 0.3})

cues = {
    "voice": VOICE, "total": TOTAL,
    "scenes": {sid: {"start": starts[sid], "duration": durs[sid], "phrases": layout[sid], "marks": marks.get(sid, {})} for sid in ORDER},
    "end": {"start": starts["end"], "duration": END_DUR},
    "words": words, "sfx": sorted(sfx, key=lambda s: s["t"]),
}
# s2's own builder reads its marks from "s2"
cues["s2"] = {"duration": durs["s2"], **marks["s2"]}
(ROOT / "data/cues.json").write_text(json.dumps(cues, ensure_ascii=False, indent=1))
print("total", TOTAL, {k: durs[k] for k in ORDER})
print("phrase seconds", round(sum(LEN.values()), 1))
