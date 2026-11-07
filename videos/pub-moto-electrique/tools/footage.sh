#!/usr/bin/env bash
# Footage for pub-moto-electrique, from the user's uploads (kept as is in sources/).
# The DJI clips are HEVC 1080x1920 at 60 fps: re-encoded to H.264 (the render browser
# cannot decode HEVC), 60 fps kept for smooth slow motion, a keyframe every 0.25 s for
# exact seeks, sound kept (engine and wind, mixed low in index.html).
# Saad Abid's clips (720x1280, 25 fps) keep their size; the page scales them.
#   usage: tools/footage.sh
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p assets/footage assets/images

enc() { # source, output, fps
  ffmpeg -nostdin -v error -y -i "sources/$1" -map 0:v:0 -map 0:a:0 \
    -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -g "$3" -keyint_min "$3" -sc_threshold 0 \
    -colorspace bt709 -color_primaries bt709 -color_trc bt709 \
    -c:a aac -b:a 160k -ar 48000 -movflags +faststart "assets/footage/$2"
}

enc dji_20261101_104733.mov vespa-petromin.mp4 15      # day, Vespa past the Petromin price board (12.2 s)
enc dji_20261101_104803.mov vespa-shell.mp4 15         # day, Vespa towards the Shell price board (5.1 s)
enc dji_20261101_104902.mov vespa-yoom.mp4 15          # dusk, Vespa towards the Yoom station (1.2 s)
enc dji_20261101_104937.mov vespa-afriquia-nuit.mp4 15 # night, Vespa past the Afriquia price board (2.6 s)
enc dji_20261103_231641.mov moto-elec-nuit.mp4 15      # night, the electric motorbike, dashboard in view (6.9 s)
enc saad-abid-a.mov saad-a.mp4 6                       # Saad Abid at the EV Mobility Show, name title (6.8 s)
enc saad-abid-b.mov saad-b.mp4 6                       # Saad Abid, second part, stands (8.1 s)

cp sources/voltmetre.jpg assets/images/voltmetre.jpg
