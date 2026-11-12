# coupure-casablanca — how the film is built

1. `python3 tools/recording.py <recording>` — cuts the narration (the person's own voice, one take or one
   file per scene) into the 30 phrases of `script.json` → `assets/voice/ph/*.wav`.
2. `python3 tools/voice.py` — lays the phrases into scenes (targets: S1 28 s, S2 38, S3 40, S4 38, S5 38,
   S6 30, end card 7) → `assets/voice/voice.wav`, `data/cues.json` (phrase windows, caption words, SFX).
3. `python3 tools/s2_build.py` (map, applies the night grade) · `python3 tools/scenes_build.py` ·
   `python3 tools/captions_build.py` · `python3 tools/music.py` (brand bed) · `python3 tools/assemble.py`.
4. `npx hyperframes check`, `npx hyperframes snapshot`, `npx hyperframes render`.

Map: Esri World Imagery z14 stitched once by `tools/basemap.py`; neighbourhood points from OpenStreetMap
Nominatim (`data/places-raw.json`), curated in `tools/basemap.py`; positions are approximate.
