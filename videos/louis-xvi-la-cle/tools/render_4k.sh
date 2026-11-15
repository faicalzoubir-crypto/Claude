#!/usr/bin/env bash
# Delivery render, 2160 × 3840, in short spans.
# One long render here slows from ~1 s to ~24 s a frame as the software-GL (SwiftShader) process grows, so each
# span runs in a fresh browser (renders are serialised per account anyway). The pictures are joined without
# re-encoding and the full soundtrack is muxed once, so the AAC frames never restart at a join.
# Spans that already finished (log says EXIT 0) are kept: re-run the script to resume.
# usage: tools/render_4k.sh [SPAN_SECONDS=6]      → livrables/louis-xvi-la-cle-4k.mp4 (git-ignored: it carries the song)
set -u
cd "$(dirname "$0")/.."
HFV=0.9.52            # the project's pinned CLI: an unpinned npx updated itself mid-run once and killed a span
SPAN=${1:-6}
TOTAL=90
DIR=renders/chunks
mkdir -p "$DIR" livrables

names=()
for ((s = 0; s < TOTAL; s += SPAN)); do
  e=$((s + SPAN)); ((e > TOTAL)) && e=$TOTAL
  name=$(printf 'c%03d' "$s"); names+=("$name")
  if [[ -s $DIR/$name.mp4 ]] && grep -q "^EXIT 0 $name" "$DIR/$name.log" 2>/dev/null; then continue; fi
  t0=$(date +%s)
  npx --yes "hyperframes@$HFV" render --resolution portrait-4k --quality looks --start "$s" --end "$e" \
    -o "$DIR/$name.mp4" --skill hyperframes < /dev/null > "$DIR/$name.log" 2>&1
  echo "EXIT $? $name $(( $(date +%s) - t0 ))s $HFV" | tee -a "$DIR/$name.log"
done

: > "$DIR/list.txt"
for name in "${names[@]}"; do
  grep -q "^EXIT 0 $name" "$DIR/$name.log" || { echo "FAILED $name (see $DIR/$name.log, then re-run)"; exit 1; }
  printf "file '%s.mp4'\n" "$name" >> "$DIR/list.txt"
done

ffmpeg -y -v error -f concat -safe 0 -i "$DIR/list.txt" -i assets/audio/bande.wav \
  -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -ar 48000 -movflags +faststart -shortest \
  livrables/louis-xvi-la-cle-4k.mp4
echo "EXIT $? ASSEMBLED livrables/louis-xvi-la-cle-4k.mp4"
