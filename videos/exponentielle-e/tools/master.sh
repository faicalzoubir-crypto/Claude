#!/bin/sh
# Amène le mixage rendu à environ -14 LUFS (réseaux sociaux), crêtes vraies sous -1,5 dBTP.
# Deux passes loudnorm (mesure, puis correction linéaire) ; l'image est copiée telle quelle.
# Usage : sh tools/master.sh renders/video.mp4 livrables/exponentielle-e.mp4
set -e
IN="$1"
OUT="$2"
mkdir -p "$(dirname "$OUT")"
STATS=$(ffmpeg -hide_banner -nostats -i "$IN" -map 0:a -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
get() { printf '%s' "$STATS" | python3 -I -c "import json,sys; print(json.load(sys.stdin)['$1'])"; }
ffmpeg -v error -y -i "$IN" -map 0:v -map 0:a -c:v copy \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(get input_i):measured_TP=$(get input_tp):measured_LRA=$(get input_lra):measured_thresh=$(get input_thresh):offset=$(get target_offset):linear=true" \
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$OUT"
