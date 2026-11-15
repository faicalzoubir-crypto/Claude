#!/usr/bin/env bash
# Persist every plate's grade with the HyperFrames treatment tool (idempotent: clears, then applies).
set -euo pipefail
cd "$(dirname "$0")/.."
G='"grain":0.14,"grainSize":0.22,"grainRoughness":0.6'
apply() { # file selector json
  npx hyperframes media-treatment --file "$1" --selector "$2" --clear --json >/dev/null
  npx hyperframes media-treatment --file "$1" --selector "$2" --grading "$3" --apply --json \
    | python3 -c "import json,sys; d=json.load(sys.stdin); print(('ok ' if d.get('ok') else 'FAIL ') + sys.argv[1], '' if d.get('ok') else json.dumps(d)[:400])" "$2"
}
# the King
apply compositions/king.html "#king-royal-warm-img"  '{"adjust":{"temperature":0.18,"contrast":0.08,"saturation":-0.05},"details":{"vignette":0.22,'"$G"'}}'
apply compositions/king.html "#king-royal-cold-img"  '{"adjust":{"temperature":-0.28,"saturation":-0.4,"exposure":-0.2,"contrast":0.12},"details":{"vignette":0.22,'"$G"'}}'
apply compositions/king.html "#king-royal-shade-img" '{"adjust":{"temperature":-0.3,"saturation":-0.45,"exposure":-1.1,"contrast":0.1},"details":{'"$G"'}}'
apply compositions/king.html "#king-1793-img"        '{"adjust":{"temperature":-0.12,"exposure":-0.08,"contrast":0.1,"saturation":-0.3},"details":{"vignette":0.15,'"$G"'}}'
apply compositions/king.html "#king-key-img"         '{"adjust":{"temperature":0.08,"contrast":0.1},"details":{'"$G"'}}'
# verses: the Hall of Mirrors by candle (exposure is animated inline by the flicker)
for f in v1 v2; do
  apply compositions/$f.html "#$f-galerie" '{"adjust":{"contrast":0.06},"details":{"vignette":0.42,"vignetteFeather":0.7,'"$G"'}}'
done
# refrain 1: grey dawn
apply compositions/r1.html "#r1-cour"  '{"adjust":{"exposure":-0.95,"contrast":0.16},"details":{"vignette":0.42,"vignetteFeather":0.7,'"$G"'}}'
apply compositions/r1.html "#r1-foule" '{"adjust":{"exposure":-0.2,"saturation":-0.1},"details":{'"$G"'}}'
# final refrain: cold dawn
apply compositions/fr.html "#fr-place" '{"adjust":{"exposure":-0.22,"contrast":0.04},"details":{"vignette":0.45,"vignetteFeather":0.7,'"$G"'}}'
# outro montage
apply compositions/outro.html "#outro-feu-img"    '{"adjust":{"contrast":0.1},"details":{"vignette":0.38,'"$G"'}}'
apply compositions/outro.html "#outro-fumee-img"  '{"adjust":{"exposure":-0.7},"details":{"vignette":0.45,'"$G"'}}'
apply compositions/outro.html "#outro-crown-img"  '{"adjust":{"exposure":-0.1,"temperature":0.08},"details":{'"$G"'}}'
apply compositions/outro.html "#outro-nuit-img"   '{"adjust":{"exposure":-1.3},"details":{"vignette":0.5,'"$G"'}}'
apply compositions/outro.html "#outro-dial-img"   '{"adjust":{"exposure":-0.15,"temperature":0.1},"details":{'"$G"'}}'
apply compositions/outro.html "#outro-salle-img"  '{"adjust":{"exposure":-1.0},"details":{"vignette":0.5,'"$G"'}}'
apply compositions/outro.html "#outro-throne-img" '{"adjust":{"exposure":-0.15,"temperature":0.05},"details":{"vignette":0.2,'"$G"'}}'
# intro: every painting detail gets the same film stock and a light painterly pass (re-run after tools/build_intro.py)
apply compositions/intro.html ".intro-img" '{"adjust":{"contrast":0.05},"details":{"vignette":0.3,"vignetteFeather":0.7,'"$G"'}}'
