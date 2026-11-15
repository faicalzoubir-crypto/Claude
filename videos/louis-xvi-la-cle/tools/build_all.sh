#!/usr/bin/env bash
# Rebuild every derived asset, in order. Sources: assets/src (Wikimedia Commons, see CREDITS.md).
set -euo pipefail
cd "$(dirname "$0")/.."
for n in callet-1786 ducreux-1793; do   # the two portraits, cut out by the local model
  [ -f assets/src/$n-cut.png ] || npx hyperframes remove-background assets/src/$n.jpg -o assets/src/$n-cut.png
done
python3 -I tools/king_callet.py          # the King 1786: oval cutout, blue coat → assets/img/king-royal.png
python3 -I tools/king_ducreux.py         # the King 1793 + the 4K-sized King plate (.webp)
python3 -I tools/objects.py              # key, crown, throne, dial
python3 -I tools/plates.py               # background plates (crops without lettering, toned)
python3 -I tools/paint.py assets/img/{galerie,cour,place,feu,fumee}.jpg assets/img/{foule,couronne,trone,cadran}.png
python3 -I tools/build_intro.py          # intro crops + compositions/intro.html
python3 -I tools/paint.py assets/img/intro/*.jpg
./tools/grades.sh                        # live grades (single pass: light, vignette, grain)
./tools/bande.sh                         # soundtrack (needs the git-ignored audio in assets/src/audio)
