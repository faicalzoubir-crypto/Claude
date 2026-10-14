"""Voice-over with known cue times — Kokoro (local), voice ff_siwis, fr-fr, speed 1.0.

Kokoro gives no word timestamps and no offline transcriber is available here, so each
SCRIPT.md line is synthesized sentence by sentence and re-assembled with designed pauses:
sentence starts are exact, and word times inside a sentence are placed in proportion to
each word's phoneme count (punctuation counted as a short pause).

Writes assets/voice/NN.wav (one per SCRIPT line, post-processed) and assets/voice/cues.json:
  { "<frame>": { "duration": s, "sentences": [{text,start,end}], "words": [{w,t,end}] } }

Usage: /root/.venvs/hf-audio/bin/python tools/voice.py   (needs kokoro-onnx, soundfile, numpy)
"""
import json
import re
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro
from kokoro_onnx.tokenizer import Tokenizer

ROOT = Path(__file__).resolve().parent.parent
CACHE = Path.home() / ".cache/hyperframes/tts"
VOICE, LANG, SPEED = "ff_siwis", "fr-fr", 1.0
LEAD, TAIL = 0.12, 0.75
PAUSE = {".": 0.40, "?": 0.45, "!": 0.40, "…": 0.62}
# Extra breath after specific sentences (frame, sentence index) — dramatic beats.
EXTRA = {(8, 1): 0.35, (6, 2): 0.15, (10, 0): 0.0}

kokoro = Kokoro(str(CACHE / "models/kokoro-v1.0.onnx"), str(CACHE / "voices/voices-v1.0.bin"))
tok = Tokenizer()


def script_lines():
    md = (ROOT / "SCRIPT.md").read_text(encoding="utf-8")
    out, cur = [], None
    for line in md.splitlines():
        h = re.match(r"^##\s+.*\(Frame\s+(\d+)\)", line)
        if h:
            cur = {"frame": int(h.group(1)), "text": ""}
            out.append(cur)
            continue
        m = re.match(r"^ {4,}(\S.*)$", line)
        if cur is not None and m:
            cur["text"] = (cur["text"] + " " + m.group(1)).strip()
    return [l for l in out if l["text"]]


def trim(x, sr, thr=0.008):
    idx = np.where(np.abs(x) > thr)[0]
    if not len(idx):
        return x
    a = max(0, idx[0] - int(0.01 * sr))
    b = min(len(x), idx[-1] + int(0.03 * sr))
    return x[a:b]


def weight(word):
    core = re.sub(r"[^\wÀ-ÿ'’-]", "", word)
    w = len(tok.phonemize(core, lang=LANG).replace(" ", "")) if core else 0
    if re.search(r"[,;]$", word):
        w += 3
    if re.search(r":$", word) or re.search(r"\s:$", word):
        w += 4
    return max(w, 1)


def main():
    cues = {}
    report = []
    for line in script_lines():
        fr = line["frame"]
        # keep French « mot : » spacing attached to the previous word
        text = re.sub(r"\s+([:;?!»])", " \\1", line["text"])
        sentences = [s.strip() for s in re.split(r"(?<=[.!?…])\s+", text) if s.strip()]
        sr = 24000
        parts = [np.zeros(int(LEAD * sr))]
        t = LEAD
        sent_meta, words = [], []
        for i, s in enumerate(sentences):
            spoken = s.replace(" ", " ")
            samples, sr = kokoro.create(spoken, voice=VOICE, speed=SPEED, lang=LANG)
            x = trim(np.asarray(samples, dtype=np.float32), sr)
            dur = len(x) / sr
            ph = len(tok.phonemize(spoken, lang=LANG).replace(" ", ""))
            report.append((fr, i, round(dur, 2), round(ph / dur, 1), spoken))
            toks = spoken.split()
            ws = [weight(w) for w in toks]
            total = sum(ws)
            acc = 0
            for w, wt in zip(toks, ws):
                words.append({"w": w, "t": round(t + dur * acc / total, 3), "end": round(t + dur * (acc + wt) / total, 3)})
                acc += wt
            sent_meta.append({"text": spoken, "start": round(t, 3), "end": round(t + dur, 3)})
            parts.append(x)
            t += dur
            if i < len(sentences) - 1:
                gap = PAUSE.get(s[-1], 0.4) + EXTRA.get((fr, i), 0.0)
                parts.append(np.zeros(int(gap * sr)))
                t += gap
        parts.append(np.zeros(int(TAIL * sr)))
        y = np.concatenate(parts)
        raw = ROOT / f"assets/voice/raw/{fr:02d}.wav"
        raw.parent.mkdir(parents=True, exist_ok=True)
        sf.write(raw, y, sr)
        out = ROOT / f"assets/voice/{fr:02d}.wav"
        # warmth + presence, gentle compression, broadcast loudness — no timing change
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af",
             "highpass=f=70,equalizer=f=220:t=q:w=1.2:g=2,equalizer=f=7500:t=q:w=1.5:g=-2,"
             "acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2,"
             "loudnorm=I=-17:TP=-2:LRA=9",
             "-ar", "48000", "-ac", "1", str(out)],
            check=True,
        )
        cues[str(fr)] = {"duration": round(len(y) / sr, 3), "sentences": sent_meta, "words": words}
    (ROOT / "assets/voice/cues.json").write_text(json.dumps(cues, ensure_ascii=False, indent=1), encoding="utf-8")
    for fr, i, d, rate, s in report:
        flag = "  <-- check" if rate > 21 or rate < 11 else ""
        print(f"{fr:2d}.{i} {d:5.2f}s {rate:5.1f} ph/s  {s[:70]}{flag}")
    print("total", round(sum(c["duration"] for c in cues.values()), 2), "s")


if __name__ == "__main__":
    main()
