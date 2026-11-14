#!/usr/bin/env python3
"""Subtitle-driven timing (no narration): the script is read on screen -> data/cues.json + livrables/*.srt.

Every phrase of script.json is split into subtitle groups (≤ 6 words, never across a phrase, broken after
«،» when possible). A group stays up for its reading time, 0.6 s + 0.34 s a word + 0.012 s a character
(a 6-word line ≈ 3 s), groups of a phrase follow each other, phrases are separated by the script's pauses.
Scenes then get the same targets as the voiced version (S1 28 s, S2 38, S3 40, S4 38, S5 38, S6 30,
end card 7): a short scene breathes longer between lines, never shows a line faster.

  python3 tools/subtitles.py
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = json.loads((ROOT / "script.json").read_text())
TARGET = {sc["id"]: 0 for sc in SCRIPT["scenes"]}   # no padding: the short cut
END_DUR = 8.0   # the sources card holds many lines


STOP = {"من", "عن", "على", "في", "ف", "د", "ما", "اللي", "حسب", "ديال", "مع", "بحال", "أو", "و", "باش", "إلا", "حتى"}
NOBREAK = {("فجزء", "من"), ("الجهد", "العالي"), ("العالي", "جدا"), ("بزاف", "د"), ("عن", "قرب"), ("للمرافق", "الحيوية"),
           ("محطتي", "أولاد"), ("أولاد", "حدو"), ("دار", "بوعزة"), ("الدار", "البيضاء"), ("الجزء", "الجنوبي"),
           ("تلاتة", "د"), ("والاضطرابات", "الجوية"), ("كان", "من"),
           ("225", "كيلوفولط"), ("225/20", "كيلوفولط"), ("32", "كيلومتر"), ("مديونة", "فالشمال"), ("والعوامر", "فالجنوب"),
           ("جوج", "جهات"), ("ثلاث", "ساعات"), ("ست", "ساعات"), ("ربعة", "د"), ("الجرف", "الأصفر"), ("سمير", "بلفقيه"),
           ("أولاد", "صالح"), ("نفس", "الشريان"), ("خط", "التقوية"), ("الحداش", "د"), ("بلاغ", "نقلاتو"),
           ("الخطوط", "ديال"), ("يقوّي", "أولاد"),
           ("شهادات", "السكان"), ("عدة", "أحياء"), ("حوالي", "الحداش"), ("حوالي", "ست"), ("بلا", "ضو")}
bare = lambda w: re.sub(r"[،,.:؟?«»]", "", w)


def split(tokens, cap=6, single=7):
    """Readable subtitle lines: ≤ single words stay one line; break after a comma when one is in reach,
    never after a particle or inside a fixed pair; the rest is re-balanced after every break."""
    n, out, i = len(tokens), [], 0
    bad = lambda m: bare(tokens[m - 1]) in STOP or (bare(tokens[m - 1]), bare(tokens[m])) in NOBREAK
    while i < n:
        rem = n - i
        if rem <= single:
            out.append(tokens[i:]); break
        k = -(-rem // cap); size = -(-rem // k); j = i + size
        cands = [m for m in range(i + 2, min(n - 2, i + single) + 1) if re.search(r"[،,:]$", tokens[m - 1])]
        if cands:
            j = min(cands, key=lambda m: abs(m - j))
        else:
            m = j
            while m > i + 2 and bad(m):
                m -= 1
            if bad(m):
                m = j
                while m < min(n - 2, i + single) and bad(m):
                    m += 1
            j = m
        out.append(tokens[i:j]); i = j
    return out


def read_time(words):
    chars = sum(len(w) for w in words)
    return max(1.4, 0.45 + 0.30 * len(words) + 0.01 * chars)


# phrase -> groups with their own reading times
G, LEN = {}, {}
for sc in SCRIPT["scenes"]:
    for p in sc["phrases"]:
        gs = split(p["text"].split())
        G[p["id"]] = [(g, round(read_time(g), 3)) for g in gs]
        LEN[p["id"]] = round(sum(d for _, d in G[p["id"]]), 3)

layout, durs, marks = {}, {}, {}
for sc in SCRIPT["scenes"]:
    sid, pl = sc["id"], {}
    if sid == "s2":
        dark_t0, a = 0.9, 0.5
        pl["s2a"] = [a, a + LEN["s2a"]]
        step = 0.45                     # one zone every 0.45 s
        lit_t0 = round(max(dark_t0 + 18 * step + 0.8, pl["s2a"][1] + 0.3), 3)
        pl["s2b"] = [lit_t0, lit_t0 + LEN["s2b"]]
        off_t = lit_t0 + 2.0
        durs[sid] = round(max(off_t + 2.5, pl["s2b"][1] + 1.5), 3)
        marks[sid] = {"dark_start": dark_t0, "dark_step": round(step, 3), "lit_start": lit_t0, "lit_step": 0.35, "offframe": off_t}
    else:
        phs = sc["phrases"]
        pauses = [min(0.35, max(0.2, 0.4 * p.get("pause", 0.5))) for p in phs]
        lead, hold = 0.4, {"s8": 1.4, "s1": 0.4, "s7": 1.9, "s6": 1.6, "s5": 1.2, "s4": 1.2, "s3": 1.0}.get(sid, 0.6)
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
        durs[sid] = round(t - pauses[-1] + hold + 0.2, 3)
    layout[sid] = {k: [round(a, 3), round(b, 3)] for k, (a, b) in pl.items()}

ORDER = [sc["id"] for sc in SCRIPT["scenes"]]
starts, t = {}, 0.0
for sid in ORDER:
    starts[sid] = round(t, 3); t += durs[sid]
starts["end"] = round(t, 3)
TOTAL = round(t + END_DUR, 3)

# groups and words on the absolute clock
groups, words = [], []
pid_scene = {p["id"]: sc["id"] for sc in SCRIPT["scenes"] for p in sc["phrases"]}
for pid, gs in G.items():
    sid = pid_scene[pid]
    t = starts[sid] + layout[sid][pid][0]
    for g, d in gs:
        groups.append({"phrase": pid, "start": round(t, 3), "end": round(t + d, 3), "text": " ".join(g)})
        per = d / len(g)
        for k, w in enumerate(g):
            words.append({"id": f"w{len(words)}", "phrase": pid, "text": w, "start": round(t + k * per, 3), "end": round(t + (k + 1) * per, 3)})
        t += d


def group_with(pid, needle):
    for g in groups:
        if g["phrase"] == pid and needle in g["text"]:
            return g
    return next(g for g in groups if g["phrase"] == pid)


sc_local = lambda sid, x: round(x - starts[sid], 3)
marks["s1"] = {"time_word": sc_local("s1", group_with("s1a", "16:48")["start"]) + 0.15}

# sound effects: each with a cause on screen
S = lambda sid, x: round(starts[sid] + x, 3)
sfx = []
cuts = ["whoosh-short", "whoosh", "whoosh-short", "whoosh", "whoosh-short", "whoosh"]
for i, sid in enumerate(ORDER[1:] + ["end"]):
    sfx.append({"file": f"{cuts[i % len(cuts)]}.wav", "t": starts[sid] - 0.12, "d": 0.57, "v": 0.32})
flash = layout["s1"]["s1c"]
sfx.append({"file": "impact-bass-1.wav", "t": S("s1", flash[0] + (flash[1] - flash[0]) * 0.78), "d": 1.8, "v": 0.3, "fo": 0.6})
m2 = marks["s2"]
for i in range(19):
    tt = m2["dark_start"] + i * m2["dark_step"] + 0.32
    sfx.append({"file": "click-soft.wav" if i % 2 == 0 else "click.wav", "t": S("s2", tt), "d": 0.36, "v": 0.16 if i % 2 == 0 else 0.09})
for i in range(5):
    sfx.append({"file": "pop.wav", "t": S("s2", m2["lit_start"] + i * m2["lit_step"]), "d": 0.6, "v": 0.16})
# S4: the two numbers disagree
s4c = layout["s4"]["s4c"]
sfx.append({"file": "impact-bass-2.wav", "t": S("s4", s4c[0] + 0.1), "d": 2.0, "v": 0.38, "fo": 0.6})
# S5: four cut lines, then the «متأخر» stamp
s5b, s5d = layout["s5"]["s5b"], layout["s5"]["s5d"]
for j in range(4):
    sfx.append({"file": "click.wav", "t": S("s5", s5b[0] + (s5b[1] - s5b[0]) * 0.35 + 0.12 * j), "d": 0.36, "v": 0.3})
sfx.append({"file": "click.wav", "t": S("s5", s5d[0] + (s5d[1] - s5d[0]) * 0.45), "d": 0.36, "v": 0.45})
# S6: the gap badge
s6c = layout["s6"]["s6c"]
sfx.append({"file": "pop.wav", "t": S("s6", s6c[0] + (s6c[1] - s6c[0]) * 0.1), "d": 0.6, "v": 0.3})
# S7: one pop per measure; S8: one soft click per question
for k in ("s7b", "s7c", "s7d", "s7e", "s7f"):
    sfx.append({"file": "pop.wav", "t": S("s7", layout["s7"][k][0] + 0.1), "d": 0.6, "v": 0.26})
for k in ("s8b", "s8c", "s8d", "s8e"):
    sfx.append({"file": "click-soft.wav", "t": S("s8", layout["s8"][k][0]), "d": 0.36, "v": 0.3})

cues = {
    "mode": "subtitles", "total": TOTAL,
    "scenes": {sid: {"start": starts[sid], "duration": durs[sid], "phrases": layout[sid], "marks": marks.get(sid, {})} for sid in ORDER},
    "end": {"start": starts["end"], "duration": END_DUR},
    "groups": groups, "words": words, "sfx": sorted(sfx, key=lambda s: s["t"]),
    "s2": {"duration": durs["s2"], **marks["s2"]},
}
(ROOT / "data").mkdir(exist_ok=True)
(ROOT / "data/cues.json").write_text(json.dumps(cues, ensure_ascii=False, indent=1))


def ts(x):
    h, r = divmod(x, 3600); m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s - int(s)) * 1000)) % 1000:03d}"


(ROOT / "livrables").mkdir(exist_ok=True)
srt = []
for i, g in enumerate(groups, 1):
    srt += [str(i), f"{ts(g['start'])} --> {ts(g['end'])}", g["text"], ""]
(ROOT / "livrables/coupure-casablanca.srt").write_text("\n".join(srt), encoding="utf-8")
print("total", TOTAL, {k: durs[k] for k in ORDER}, "| groups", len(groups), "| reading s", round(sum(LEN.values()), 1))
