#!/usr/bin/env python3
"""Arabic narration with Piper (voice ar_JO-kareem-medium), phrase by phrase, with word timings.

Reads script.json ('tts' = hand-vocalized text). Before a pause (، . ؟ : or the end) the final
short vowel / tanween is dropped (waqf), as a news reader would.
Word times come from Piper's phoneme alignments (word = run of phonemes between spaces).

Writes:
  assets/voice/<phrase>.wav    one clip per phrase, silence trimmed to 40 ms each side
  assets/voice/timing.json     {phrase: {dur, words:[{text,start,end}]}}  (read by tools/assemble.py)

The model (~63 MB) is downloaded once from huggingface.co into ~/.cache/hyperframes/tts.

  python3 tools/voice.py                 # fits the speech to script.json "target" (90 s)
  python3 tools/voice.py --speed 0.95    # a fixed length scale instead (< 1 faster)

With a target, the narration is synthesized once at normal speed, then again at the length scale that
makes lead + speech + pauses + tail land on the target (allowed range 0.82–1.15, else it says so).
"""
import json
import re
import sys
import urllib.request
import wave
from pathlib import Path

import numpy as np
from piper import PiperVoice, SynthesisConfig

ROOT = Path(__file__).resolve().parent.parent
CACHE = Path.home() / ".cache/hyperframes/tts"
NAME = "ar_JO-kareem-medium"
BASE = "https://huggingface.co/rhasspy/piper-voices/resolve/main/ar/ar_JO/kareem/medium/"
FIXED_SPEED = float(sys.argv[sys.argv.index("--speed") + 1]) if "--speed" in sys.argv else None

CACHE.mkdir(parents=True, exist_ok=True)
for suffix in (".onnx", ".onnx.json"):
    dst = CACHE / (NAME + suffix)
    if not dst.exists():
        print("downloading", dst.name)
        urllib.request.urlretrieve(BASE + NAME + suffix, dst)

voice = PiperVoice.load(CACHE / f"{NAME}.onnx", config_path=CACHE / f"{NAME}.onnx.json", include_alignments=True)
SR = voice.config.sample_rate

HARAKAT = "ٌٍَُِْ"  # fatha damma kasra, tanween damm/kasr, sukun
PAUSE = "،.؟:!؛"


def waqf(text):
    """Drop the case ending before each pause (keep tanween fath + alif, read as -ā)."""
    out, ws = [], text.split()
    for i, w in enumerate(ws):
        core = w.rstrip(PAUSE)
        punct = w[len(core):]
        if punct or i == len(ws) - 1:
            core = re.sub(f"[{HARAKAT}]+$", "", core)
            core = re.sub("ً(?=[اى]?$)", "", core)  # تَنْوِينُ فَتْحٍ → ā
        out.append(core + punct)
    return " ".join(out)


script = json.loads((ROOT / "script.json").read_text())


def synth_all(speed):
    cfg = SynthesisConfig(length_scale=speed, noise_scale=0.6, noise_w_scale=0.75, normalize_audio=True, volume=0.9)
    timing, clips = {}, {}
    for sc in script["scenes"]:
        for ph in sc["phrases"]:
            text = waqf(ph["tts"])
            chunks = list(voice.synthesize(text, cfg, include_alignments=True))
            audio, words = [], []
            offset = 0
            for ci, ch in enumerate(chunks):
                a = ch.audio_float_array
                if ci > 0:  # a short breath between sentences inside one phrase
                    gap = np.zeros(int(0.18 * SR), dtype=np.float32)
                    audio.append(gap)
                    offset += len(gap)
                pos, cur = offset, None
                for al in ch.phoneme_alignments or []:
                    p = al.phoneme
                    if p == " " or p in PAUSE + ",.?!;" or p in ("^", "$"):
                        if cur is not None:
                            words.append(cur)
                            cur = None
                    elif al.num_samples > 0 or cur is not None:
                        if cur is None:
                            cur = [pos, pos + al.num_samples]
                        else:
                            cur[1] = pos + al.num_samples
                    pos += al.num_samples
                if cur is not None:
                    words.append(cur)
                audio.append(a)
                offset += len(a)
            x = np.concatenate(audio)
            # trim silence (keep 40 ms)
            thr = 0.02 * np.abs(x).max()
            idx = np.where(np.abs(x) > thr)[0]
            a0 = max(0, idx[0] - int(0.04 * SR))
            a1 = min(len(x), idx[-1] + int(0.04 * SR))
            x = x[a0:a1]
            tts_words = ph["tts"].split()
            ws = [{"text": tts_words[i] if i < len(tts_words) else "",
                   "start": round(max(0, (s0 - a0) / SR), 3), "end": round(max(0, (s1 - a0) / SR), 3)}
                  for i, (s0, s1) in enumerate(words)]
            if len(ws) != len(tts_words):
                print(f"  {ph['id']}: {len(ws)} voiced words vs {len(tts_words)} written (times spread by assemble)")
            timing[ph["id"]] = {"dur": round(len(x) / SR, 3), "words": ws, "read": text, "speed": speed}
            clips[ph["id"]] = x
    return timing, clips


gaps = sum(p["gap"] for sc in script["scenes"] for p in sc["phrases"]) - script["scenes"][-1]["phrases"][-1]["gap"]
overhead = script["lead"] + gaps + script["sceneGap"] * (len(script["scenes"]) - 1) + script["tail"]
speed = FIXED_SPEED or 1.0
timing, clips = synth_all(speed)
speech = sum(v["dur"] for v in timing.values())
target = script.get("target")
if target and FIXED_SPEED is None:
    want = (target - overhead) / speech
    print(f"speech {speech:.2f}s at speed 1.0 + {overhead:.2f}s fixed → target {target}s needs length scale {want:.3f}")
    if not 0.82 <= want <= 1.15:
        print("  outside 0.82–1.15: shorten or lengthen the script instead; using the nearest bound")
    speed = round(min(1.15, max(0.82, want)), 3)
    if abs(speed - 1.0) > 0.005:
        timing, clips = synth_all(speed)
        speech = sum(v["dur"] for v in timing.values())

(ROOT / "assets/voice").mkdir(parents=True, exist_ok=True)
for pid, x in clips.items():
    with wave.open(str(ROOT / f"assets/voice/{pid}.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())
(ROOT / "assets/voice/timing.json").write_text(json.dumps(timing, ensure_ascii=False, indent=1))
print(f"speech {speech:.2f}s at length scale {speed} → film ≈ {speech + overhead:.2f}s; {len(clips)} clips in assets/voice/")
