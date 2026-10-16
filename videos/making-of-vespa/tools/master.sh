#!/bin/sh
# Brings the rendered mix to about -14 LUFS (social platforms) with true peaks near -2 dBTP.
# The pinned renderer (hyperframes 0.8.164) ignores a master chain on the root, so the
# loudness step runs here, on the finished file; the picture is copied untouched.
# Usage: sh tools/master.sh renders/making-of.mp4 livrables/making-of.mp4
set -e
ffmpeg -v error -y -i "$1" -map 0:v -map 0:a -c:v copy \
  -af "volume=6.5dB,alimiter=limit=0.708:attack=3:release=80:level=false" \
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$2"
