#!/usr/bin/env bash
# Footage for en-nour-3-communique, from the teacher's iPad screen recording (1080x1554, 30 fps, 100.7 s).
#   assets/footage/ecran.mp4    the recording, muted, H.264 (keyframe every 0.5 s for exact seeks)
#   assets/footage/rembobine.mp4 the hook's rewind: 40 frames scrubbing back 84.23 s -> 17.50 s on an
#                                ease-in-out curve, each frame blended with its neighbours (tape smear)
# usage: tools/footage.sh /path/to/recording.mov
set -euo pipefail
SRC="$1"
cd "$(dirname "$0")/.."
ffmpeg -v error -y -i "$SRC" -an -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -g 15 -keyint_min 15 \
  -movflags +faststart assets/footage/ecran.mp4
TMP=$(mktemp -d)
python3 - "$TMP" <<'PY'
import math, sys
n, a, b = 40, 84.23, 17.50
ease = lambda p: 0.5 - 0.5 * math.cos(math.pi * p)
with open(sys.argv[1] + "/times.txt", "w") as f:
    for i in range(n):
        f.write(f"{a - (a - b) * ease(i / (n - 1)):.3f}\n")
PY
i=0
while read -r t; do
  ffmpeg -nostdin -v error -y -ss "$t" -i assets/footage/ecran.mp4 -frames:v 1 "$TMP/f_$(printf %03d $i).png"
  i=$((i + 1))
done < "$TMP/times.txt"
ffmpeg -v error -y -framerate 30 -i "$TMP/f_%03d.png" -vf "tmix=frames=3:weights='1 2 1',format=yuv420p" \
  -c:v libx264 -preset slow -crf 17 -g 15 -movflags +faststart assets/footage/rembobine.mp4
rm -rf "$TMP"
