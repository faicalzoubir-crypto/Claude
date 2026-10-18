"""Exponentielle e — repères de la voix off pour l'enregistrer soi-même sur la vidéo muette.

Lit tools/timing.json (débuts de plans + instants exacts de chaque réplique) et écrit :
  livrables/reperes-voix-off.srt  — un sous-titre par réplique, à importer comme guide dans un monteur
  livrables/reperes-voix-off.txt  — la même liste, lisible : début, fin, texte

Usage : python tools/cue_sheet.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TIMING = json.loads((ROOT / "tools" / "timing.json").read_text())


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def clock(t):
    m, s = divmod(t, 60)
    return f"{int(m)}:{s:05.2f}"


def main():
    rows, start = [], 0.0
    for key in sorted(TIMING["frames"]):
        frame = TIMING["frames"][key]
        for cue in frame["cues"].values():
            rows.append((int(key), start + cue["start"], start + cue["end"], cue["text"]))
        start += frame["duration"]
    out = ROOT / "livrables"
    out.mkdir(exist_ok=True)
    srt = "\n".join(f"{k}\n{srt_time(a)} --> {srt_time(b)}\n{text}\n" for k, (_, a, b, text) in enumerate(rows, 1))
    (out / "reperes-voix-off.srt").write_text(srt)
    lines = ["Repères de la voix off — La fonction exponentielle et le nombre e",
             f"Durée de la vidéo : {clock(start)} · commencez chaque phrase à l'instant indiqué.", ""]
    plan = None
    for num, a, b, text in rows:
        if num != plan:
            lines.append(f"Plan {num:02d}")
            plan = num
        lines.append(f"  {clock(a)} → {clock(b)}  {text}")
    (out / "reperes-voix-off.txt").write_text("\n".join(lines) + "\n")
    print(f"{len(rows)} répliques, vidéo {start:.2f} s")


if __name__ == "__main__":
    main()
