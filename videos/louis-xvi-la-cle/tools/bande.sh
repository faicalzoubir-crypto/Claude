#!/usr/bin/env bash
# The soundtrack: the reference clip's intro, then Viva La Vida cut on downbeats (138 BPM, 8-bar blocks).
#   film  0.000–22.845  reference clip 0–22.845 ("Wait, what's the song… I used to own")
#   film 22.845–50.675  song 54.715–82.545  ("One minute I held the key" … "foreign field")
#   film 50.675–64.605  song 124.265–138.195 ("Revolutionaries wait" … "want to be king")
#   film 64.605–90.000  song 152.115–177.510 ("For some reason I can't explain" … "ruled the world", bridge)
# Each splice is an 80 ms equal-power crossfade centred on the downbeat (segments padded ±40 ms); total exactly 90.000 s; −14 LUFS.
set -euo pipefail
cd "$(dirname "$0")/.."
R=assets/src/audio/reference-intro.mp4
S=assets/src/audio/viva-la-vida.m4a
ffmpeg -v error -y -i "$R" -i "$S" -filter_complex "
 [0:a]aresample=48000,atrim=0:22.885,asetpts=N/SR/TB[a];
 [1:a]aresample=48000,atrim=54.675:82.585,asetpts=N/SR/TB[b];
 [1:a]aresample=48000,atrim=124.225:138.235,asetpts=N/SR/TB[c];
 [1:a]aresample=48000,atrim=152.075:177.510,asetpts=N/SR/TB,afade=t=out:st=23.235:d=2.2[d];
 [a][b]acrossfade=d=0.08:c1=qsin:c2=qsin[ab];
 [ab][c]acrossfade=d=0.08:c1=qsin:c2=qsin[abc];
 [abc][d]acrossfade=d=0.08:c1=qsin:c2=qsin,atrim=0:90,loudnorm=I=-14:TP=-1.0:LRA=11[out]" \
 -map "[out]" -ar 48000 -c:a pcm_s16le assets/audio/bande.wav
ffprobe -v error -show_entries format=duration -of csv=p=0 assets/audio/bande.wav
