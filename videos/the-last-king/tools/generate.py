#!/usr/bin/env python3
"""Generate the film's stills and shots on HeyGen through the HyperFrames CLI.

  python3 tools/generate.py ref                 # assets/stills/king-ref.png
  python3 tools/generate.py stills [ids...]     # assets/stills/<id>.png (first frames)
  python3 tools/generate.py videos [ids...]     # assets/shots/<id>.mp4 from the first frames
  add --plan to print what each call would do without making anything.
Runs from the project root. Existing outputs are skipped unless --force.
"""
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(ROOT, "tools", "shots.json")))


def fill(text):
    return text.replace("{king}", CFG["king"]).replace("{style}", CFG["style"])


def run(args, out):
    if os.path.exists(os.path.join(ROOT, out)) and "--force" not in sys.argv and "--plan" not in sys.argv:
        return f"skip {out} (exists)"
    cmd = ["npx", "-y", "hyperframes", "media-use", "generate", *args, "--out", out]
    if "--plan" in sys.argv:
        cmd.append("--plan")
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    tail = (r.stdout + r.stderr).strip().splitlines()[-6:]
    return f"{'ok' if r.returncode == 0 else 'FAILED'} {out}\n  " + "\n  ".join(tail)


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    what = sys.argv[1]
    ids = [a for a in sys.argv[2:] if not a.startswith("--")]
    shots = [s for s in CFG["shots"] if not ids or s["id"] in ids]
    jobs = []
    if what == "ref":
        jobs.append((["--type", "image", "--aspect", "16:9", "--prompt", fill(CFG["ref"]["prompt"])],
                     "assets/stills/king-ref.png"))
    elif what == "stills":
        for s in shots:
            args = ["--type", "image", "--aspect", "16:9", "--prompt", fill(s["still"])]
            if s["king"]:
                args += ["--reference", "assets/stills/king-ref.png"]
            jobs.append((args, f"assets/stills/{s['id']}.png"))
    elif what == "videos":
        for s in shots:
            prompt = ("Oil-painting animation with thick visible brushstrokes on canvas, slow fluid motion. "
                      + s["motion"] + " No text.")
            jobs.append((["--type", "video", "--first-frame", f"assets/stills/{s['id']}.png",
                          "--seconds", str(s["seconds"]), "--prompt", prompt],
                         f"assets/shots/{s['id']}.mp4"))
    else:
        raise SystemExit(__doc__)
    with ThreadPoolExecutor(max_workers=5) as ex:
        for line in ex.map(lambda j: run(*j), jobs):
            print(line, flush=True)


if __name__ == "__main__":
    main()
