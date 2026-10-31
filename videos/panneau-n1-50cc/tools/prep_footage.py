#!/usr/bin/env python3
"""Prepares the user's ride clips (assets/footage/source/*.mov) for the render.

- fork_a/b/c.mov (HEVC, 60 fps variable) → assets/footage/fork_*.mp4: H.264,
  constant 30 fps, no sound (the film is music only).
- The sign still for scenes 1 and 7: fork_b at 6.55 s (sharpest frame of the
  moped / pedestrian signs), with the distant car and person blurred.
"""
import subprocess
from pathlib import Path

from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "footage" / "source"
OUT = ROOT / "assets" / "footage"

for name in ("fork_a", "fork_b", "fork_c"):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(SRC / f"{name}.mov"), "-an",
                    "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-crf", "17", "-preset", "medium",
                    "-g", "30", "-movflags", "+faststart", str(OUT / f"{name}.mp4")], check=True)

still = ROOT / "assets" / "images" / "sign_still.png"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "6.55", "-i", str(SRC / "fork_b.mov"), "-frames:v", "1", str(still)], check=True)
im = Image.open(still).convert("RGB")
# Privacy: the oncoming car (plate side) and the walker by the lamp post, both far.
for box in ((0, 1120, 140, 1230), (128, 1118, 176, 1186)):
    im.paste(im.crop(box).filter(ImageFilter.GaussianBlur(9)), box[:2])
im.save(still.with_suffix(".jpg"), quality=94)
still.unlink()
print("ok")
