#!/usr/bin/env python3
"""Paint the shots to assets/shots/<id>.mp4 (1080x1920, 24 fps).

  python3 tools/paint/render_shots.py                  # every shot, 4 in parallel
  python3 tools/paint/render_shots.py s1a s2b          # some shots
  python3 tools/paint/render_shots.py --stills s1a     # frames at 0, 1/3, 2/3, end as PNGs only
"""
import json
import os
import sys
import time
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402
import cv2  # noqa: E402

from painter import FPS, Painter, Writer, apply_cam, weave  # noqa: E402
from scenes import SHOTS  # noqa: E402

LENGTH = {s["id"]: s["seconds"] for s in json.load(open(os.path.join(ROOT, "tools", "shots.json")))["shots"]}


def frame(sid, painter, i, d):
    t = i / FPS
    spec = SHOTS[sid]
    under, cam = spec["fn"](t, d)
    under = apply_cam(under, cam)
    out = painter.paint(under, t, cam, **spec.get("paint", {}))
    return Painter.finish(out)


def render(sid, stills=False):
    spec = SHOTS[sid]
    d = LENGTH[sid]
    n = int(round(d * FPS))
    painter = Painter(spec["seed"], spec.get("flow", "swirl"), **spec.get("painter", {}))
    t0 = time.time()
    if stills:
        os.makedirs(os.path.join(ROOT, "assets", "paint-stills"), exist_ok=True)
        wv = weave()
        for i in sorted({0, n // 3, 2 * n // 3, n - 1}):
            img = frame(sid, painter, i, d)
            cv2.imwrite(os.path.join(ROOT, "assets", "paint-stills", f"{sid}-{i:03d}.png"),
                        np.clip(img * wv * 255, 0, 255).astype(np.uint8))
        return f"{sid}: stills in {time.time() - t0:.1f}s"
    w = Writer(os.path.join(ROOT, "assets", "shots", f"{sid}.mp4"))
    for i in range(n):
        w.write(frame(sid, painter, i, d))
    w.close()
    return f"{sid}: {n} frames in {time.time() - t0:.0f}s"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    stills = "--stills" in sys.argv
    ids = args or list(SHOTS)
    os.makedirs(os.path.join(ROOT, "assets", "shots"), exist_ok=True)
    if len(ids) == 1:
        print(render(ids[0], stills), flush=True)
        return
    with Pool(4) as pool:
        for line in pool.starmap(render, [(i, stills) for i in ids]):
            print(line, flush=True)


if __name__ == "__main__":
    main()
