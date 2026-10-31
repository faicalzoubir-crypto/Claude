#!/usr/bin/env python3
"""Prepares the user's ride clips (assets/footage/source/*.mov) for the render.

- fork_a/b/c.mov (HEVC, 60 fps variable) → assets/footage/fork_*.mp4: H.264,
  constant 30 fps, no sound (the film is music only).
- The pause frame for scene 1: fork_b frame 197, where scene 7's clip ends.
"""
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "footage" / "source"
OUT = ROOT / "assets" / "footage"

for name in ("fork_a", "fork_b", "fork_c"):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(SRC / f"{name}.mov"), "-an",
                    "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-crf", "17", "-preset", "medium",
                    "-g", "30", "-movflags", "+faststart", str(OUT / f"{name}.mp4")], check=True)

# The pause frame: fork_b.mp4 frame 197 (6.567 s), exactly where scene 7's clip
# ends, so the loop from scene 7 into scene 1 continues the same picture. The car
# and the walker far behind the sign are a few pixels tall (no readable plate or
# face) and stay as filmed, matching the moving clip.
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(OUT / "fork_b.mp4"), "-vf", "select=eq(n\\,197)",
                "-vsync", "0", "-frames:v", "1", str(ROOT / "assets" / "images" / "sign_still.png")], check=True)  # lossless: same pixels as the clip
print("ok")
