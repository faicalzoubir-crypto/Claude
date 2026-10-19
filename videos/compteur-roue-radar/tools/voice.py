#!/usr/bin/env python3
"""Narration for compteur-roue-radar, phrase by phrase, with exact timings.

Whisper cannot run here (its models are not reachable), so instead of
"synthesize then transcribe" this script synthesizes each sentence of
SCRIPT.md separately with Kokoro (voice ff_siwis), joins them with planned
pauses, and records where every phrase and word lands:

  assets/voice/NN.wav   one clip per frame (lead + speech + planned beats)
  audio_meta.json       voices[] in the shape captions.mjs / assemble-index.mjs read
  voice_cues.json       per frame: phrase start/end, for pacing the animation

Word timings inside a sentence come from its internal pauses (one per comma
or colon) when Kokoro's pauses match the punctuation, otherwise from character
length. Phrases flagged caption=False get no words, so no subtitle (their words
are already on screen in large type).

  python3 tools/voice.py            # all frames
  python3 tools/voice.py 3 8        # only these frames (others kept)
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

ROOT = Path(__file__).resolve().parent.parent
CACHE = Path.home() / ".cache/hyperframes/tts"
VOICE = "ff_siwis"
SR = 24000

# Pauses (s) — between sentences, at an ellipsis, between speakers.
GAP_SENTENCE = 0.25
GAP_ELLIPSIS = 0.4
GAP_SPEAKER = 0.5

# Per frame: lead/tail silence and the beats the picture needs.
# "utterances" overrides how a frame's text is split (dialogue speakers).
FRAMES = {
    1: {"lead": 0.5, "tail": 0.4, "caption": False},
    2: {"lead": 0.25, "tail": 0.5},
    3: {"lead": 0.25, "tail": 0.6},
    4: {"lead": 0.25, "tail": 0.4},
    5: {"lead": 0.25, "tail": 0.8},
    6: {"lead": 0.25, "tail": 0.6},
    7: {"lead": 0.25, "tail": 1.5},  # radar is raised, "70" flashes
    8: {
        "lead": 0.3,
        "tail": 1.2,  # Karim looks down at his wheels
        "caption": False,  # the bubbles carry the words
        "utterances": [
            ("policier", "Bonjour monsieur, vous rouliez à 70 kilomètres-heure dans une zone limitée à 60."),
            ("karim", "Impossible ! Mon compteur indiquait exactement 60, j'en suis sûr !"),
            ("policier", "Votre compteur est réglé pour les roues d'origine. Avec des roues plus grandes, chaque tour vous fait parcourir plus de distance. Le radar, lui, mesure votre vitesse réelle."),
        ],
    },
    9: {"lead": 0.8, "tail": 1.5},  # title first; footnote read at the end
    10: {"lead": 0.25, "tail": 1.6, "no_caption_from": "Ton compteur compte des tours"},
}
SPEED = {"karim": 1.06}


def script_lines():
    """SCRIPT.md → {frame: spoken text} (indented blocks under `## … (Frame N)`)."""
    out, cur = {}, None
    for line in (ROOT / "SCRIPT.md").read_text(encoding="utf8").splitlines():
        m = re.match(r"^#{2,3}\s+.*?\(frame\s+(\d+)\)", line, re.I)
        if m:
            cur = int(m.group(1))
            continue
        if cur is not None and re.match(r"^( {4,}|\t)\S", line):
            out[cur] = (out.get(cur, "") + " " + line.strip()).strip()
    return out


def sentences(text):
    """Split at . ! ? and at an ellipsis; keep the mark that ended each piece."""
    parts = re.findall(r"[^.!?…]+(?:[.!?]+|…|$)", text)
    return [p.strip() for p in parts if p.strip()]


def trim(audio, thresh=0.006, pad=0.03):
    """Cut leading/trailing silence, keep a short pad."""
    idx = np.where(np.abs(audio) > thresh)[0]
    if not len(idx):
        return audio
    a = max(0, idx[0] - int(pad * SR))
    b = min(len(audio), idx[-1] + int(pad * SR))
    return audio[a:b]


def internal_pauses(audio, min_len=0.09, thresh=0.008):
    """Centers (s) of silent stretches inside a clip, in order."""
    win = int(0.01 * SR)
    n = len(audio) // win
    if n == 0:
        return []
    env = np.abs(audio[: n * win]).reshape(n, win).max(axis=1)
    quiet = env < thresh
    out, start = [], None
    for i, q in enumerate(quiet):
        if q and start is None:
            start = i
        elif not q and start is not None:
            if (i - start) * 0.01 >= min_len and start > 5 and i < n - 5:
                out.append((start + i) / 2 * 0.01)
            start = None
    return out


def word_times(text, dur, pauses):
    """Spread the words of one sentence over [0, dur]."""
    words = text.split()
    # Clauses split after , : ; — each clause maps to one detected pause.
    clauses, cur = [], []
    for w in words:
        cur.append(w)
        if re.search(r"[,:;]$", w) or w in (":", ";"):
            clauses.append(cur)
            cur = []
    if cur:
        clauses.append(cur)
    if len(clauses) > 1 and len(pauses) == len(clauses) - 1:
        bounds = [0.0] + pauses + [dur]
    else:
        clauses = [words]
        bounds = [0.0, dur]
    out = []
    for ci, clause in enumerate(clauses):
        a, b = bounds[ci], bounds[ci + 1]
        weights = [max(1, len(re.sub(r"[^\wÀ-ÿ']", "", w))) + 1 for w in clause]
        total = sum(weights)
        t = a
        for w, wt in zip(clause, weights):
            d = (b - a) * wt / total
            out.append((w, t, t + d))
            t += d
    return out


def main():
    only = {int(a) for a in sys.argv[1:]}
    kokoro = Kokoro(str(CACHE / "models/kokoro-v1.0.onnx"), str(CACHE / "voices/voices-v1.0.bin"))
    texts = script_lines()
    (ROOT / "assets/voice").mkdir(parents=True, exist_ok=True)

    meta_path = ROOT / "audio_meta.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {"bgm": None, "bgm_pending": False, "voices": [], "sfx": []}
    cues_path = ROOT / "voice_cues.json"
    cues_all = json.loads(cues_path.read_text()) if cues_path.exists() else {}
    voices = {v["frame"]: v for v in meta.get("voices", [])}

    for frame in sorted(texts):
        if only and frame not in only:
            continue
        cfg = FRAMES.get(frame, {})
        utterances = cfg.get("utterances") or [("narration", texts[frame])]
        chunks = []  # (speaker, sentence, gap_before)
        for ui, (speaker, utt) in enumerate(utterances):
            for si, s in enumerate(sentences(utt)):
                if ui == 0 and si == 0:
                    gap = 0.0
                elif si == 0:
                    gap = GAP_SPEAKER
                else:
                    gap = GAP_ELLIPSIS if chunks[-1][1].endswith("…") else GAP_SENTENCE
                chunks.append((speaker, s, gap))

        pieces = [np.zeros(int(cfg.get("lead", 0.3) * SR), dtype=np.float32)]
        t = cfg.get("lead", 0.3)
        phrases, words = [], []
        captions_on = cfg.get("caption", True)
        for speaker, s, gap in chunks:
            if gap:
                pieces.append(np.zeros(int(gap * SR), dtype=np.float32))
                t += gap
            say = s.rstrip("…").strip() if s.endswith("…") else s
            audio, sr = kokoro.create(say, voice=VOICE, speed=SPEED.get(speaker, 1.0), lang="fr-fr")
            assert sr == SR, sr
            audio = trim(audio.astype(np.float32))
            dur = len(audio) / SR
            if cfg.get("no_caption_from") and s.startswith(cfg["no_caption_from"]):
                captions_on = False
            phrases.append({"speaker": speaker, "text": s, "start": round(t, 3), "end": round(t + dur, 3)})
            if captions_on:
                for w, a, b in word_times(s, dur, internal_pauses(audio)):
                    words.append({"text": w, "start": round(t + a, 3), "end": round(t + b, 3)})
            pieces.append(audio)
            t += dur
        pieces.append(np.zeros(int(cfg.get("tail", 0.5) * SR), dtype=np.float32))
        t += cfg.get("tail", 0.5)

        clip = np.concatenate(pieces)
        rel = f"assets/voice/{frame:02d}.wav"
        sf.write(ROOT / rel, clip, SR, subtype="PCM_16")
        dur = round(len(clip) / SR, 3)
        for i, w in enumerate(words):
            w["id"] = f"w{frame:02d}-{i:03d}"
        voices[frame] = {"frame": frame, "path": rel, "duration_s": dur, "words": words}
        cues_all[str(frame)] = {"duration_s": dur, "phrases": phrases}
        print(f"frame {frame:2d}: {dur:6.2f}s  {len(phrases)} phrase(s)  {len(words)} caption word(s)")

    meta["voices"] = [voices[k] for k in sorted(voices)]
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    cues_path.write_text(json.dumps(dict(sorted(cues_all.items(), key=lambda kv: int(kv[0]))), ensure_ascii=False, indent=2))
    total = sum(v["duration_s"] for v in meta["voices"])
    print(f"total {total:.1f}s")


if __name__ == "__main__":
    main()
