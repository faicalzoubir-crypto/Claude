#!/usr/bin/env bash
# Master the rendered film's sound for social: −14 LUFS integrated, true peak ≤ −1 dBTP (−2 target: AAC overshoots) (two-pass
# loudnorm; the picture is copied untouched).   usage: tools/master.sh renders/in.mp4 livrables/out.mp4
set -euo pipefail
IN="$1"; OUT="$2"
J=$(ffmpeg -hide_banner -nostats -i "$IN" -vn -af loudnorm=I=-14:TP=-2.0:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
get() { echo "$J" | python3 -c "import sys,json; print(json.load(sys.stdin)['$1'])"; }
ffmpeg -v error -y -i "$IN" -c:v copy -af "loudnorm=I=-14:TP=-2.0:LRA=11:measured_I=$(get input_i):measured_TP=$(get input_tp):measured_LRA=$(get input_lra):measured_thresh=$(get input_thresh):offset=$(get target_offset):linear=true" \
  -ar 48000 -c:a aac -b:a 192k -movflags +faststart "$OUT"
