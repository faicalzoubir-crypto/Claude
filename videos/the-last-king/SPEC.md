# The Last King — spec

GOAL:    a silent, dreamlike fall of a lone king told as one moving oil painting: power, the
         gamble of the crown, flight, omens, revolt, and the empty walk into the light. The viewer
         ends on black, having watched the crown roll away.
OUTPUT:  HyperFrames, 1920 x 1080, 30 fps, 16:9 landscape. Silent (no music, no voice, no captions,
         no on-screen text). The person adds their own track later.
TIME:    60 s x 30 = 1800 frames. Six scenes: 10 + 8 + 10 + 10 + 12 + 10 s.

## Look (one medium: oil on canvas, moving)

- **Ground**: near-black `#0B0D10`, never a flat void: the canvas weave and dark scumbled paint
  are always visible in it (the AI footage carries it; no CSS texture on top).
- **Ink A, cream-yellow** `#E9D9A6` → gold `#D9A441`: light, crowns, the palace, the crowd's raised arms.
- **Ink B, cold blue-violet** `#5B5FA8` → `#2B2D5C`: night, the cell, snow, ghosts, the end.
- **Accent, red** `#B3261E`: ONE small thing per frame at most (the gem on the crown, the flag in
  scene 5). Never a red wash.
- **Brushwork**: thick impasto, strokes 1–4% of frame width, directional with the motion; slow fluid
  motion only (camera ≤ 3% of frame width per second).
- **People**: no sharp facial detail anywhere. The king's face is a soft pale smear under the crown.
- **The king**: same figure every time: long pale cream cloak to the floor, simple gold band crown
  with one small red gem, thin, upright, alone. Reference still `assets/stills/king-ref.png`.
- **Brand note**: the repo brand (`brand/BRAND.md`) is a UI/data look (grid, amber, mint). This film
  has no UI or text, and the person set this film's palette explicitly, so the film follows the
  palette above; only the brand's near-black ground carries over.

## Objects (must read without a label)

balcony (gold balustrade, deep drop), kneeling crowd (hundreds of tiny bowed figures, rows that
ripple), stone cell (rough blocks, one high slit, one candle on the floor), crown (simple gold band,
one red gem), dice (two ivory cubes with dark pips), palace on pillars of pale sand and salt
(crystalline, grainy), carriage (black, two lamps, horses), key (old iron/gold, long bit), bells
(bronze, in a dark belfry), horsemen (pale, translucent, on a snowy plain), mirror (gilt frame,
silvered glass, a crack running through the reflected crown), palace doors (tall, double), windows
(tall, leaded panes), flag (one red cloth on a pole), marionette (the king as a wooden puppet, one
thin thread from above), doorway of light (a thin vertical slit in black).

## Motion

- AI shots: slow push or drift, one hero move per shot; everything else holds.
- Inner-scene shot changes: paint dissolve 0.6–0.8 s (strokes melt from one image to the next).
- Scene changes: **swirling brushstroke dissolve**, 1.6 s centred on the boundary: a curl-noise swirl
  warps the outgoing image while a matte of long curved brushstrokes paints the incoming one in,
  stroke by stroke, along the swirl. Baked per boundary as `assets/transitions/tN.mp4`
  (`tools/brush_transition.py`) and laid over the boundary on its own track.
- Ending: fade to pure black from 57.4 s, black from 59.2 s to 60 s.

## Shots

Times are on-screen spans including dissolve overlaps (root seconds).

| Shot | Span (s) | What happens (one hero move) | Hand-off |
| --- | --- | --- | --- |
| 1a | 0.0–5.8 | King on a vast gold balcony from behind, a sea of tiny kneeling figures below; he raises a hand and the rows ripple like a wave | gold drains to blue (graded drain + paint dissolve) |
| 1b | 5.0–10.8 | Bare stone cell in cold blue, the king seated alone, one candle flickers; slow push | swirl → 2 |
| 2a | 9.2–14.6 | Painted crowd raises its arms in warm cream strokes, a crown lifted above the hands | paint dissolve |
| 2b | 13.8–18.8 | Two dice tumble in slow motion over black and come apart into drifting gold paint | swirl → 3 |
| 3a | 17.2–21.8 | Gold palace on pillars of pale sand and salt; the pillars slowly crumble, grains pour | paint dissolve |
| 3b | 21.2–25.2 | A black carriage flees through blue-violet night; painted walls lean in on both sides | paint dissolve |
| 3c | 24.6–28.8 | Close on the king's pale hand: an old key dissolves into paint flakes | swirl → 4 |
| 4a | 27.2–31.4 | Bells swing in a dark belfry, each toll releases a ring of pale paint | paint dissolve |
| 4b | 30.8–34.6 | Ghostly pale horsemen gather on a distant snowy field under a violet sky | paint dissolve |
| 4c | 34.0–38.8 | The king faces a gilt mirror; the reflection shows his crown cracked | swirl → 5 |
| 5a | 37.2–42.0 | A wind of brushstrokes blows the palace doors open; the windows shatter into shards of light | paint dissolve |
| 5b | 41.4–45.6 | Dark crowd silhouettes pour through the doors beneath one red flag | paint dissolve |
| 5c | 45.0–50.8 | The king as a marionette on one thin thread; the thread is cut, the puppet drops into dark | swirl → 6 |
| 6a | 49.2–55.6 | Pure black; a pale cloaked silhouette walks away toward a thin vertical slit of light | paint dissolve |
| 6b | 55.0–60.0 | The gold crown falls, bounces once and rolls into darkness; fade to black | end |

## BANNED

Text, letters, numerals, logos, watermarks, signatures in any frame; captions; a presenter; stock
footage; glow, bloom, lens flares, floating particles as decoration; photographic realism; sharp
faces; gore, nooses, executions or anything graphic (scene 5 is a wooden marionette; scene 6 is
a walk into light); colours outside the palette (no green, no saturated orange, no teal); a red
wash; flat digital gradients; hard cuts between scenes.

## QA frames

0.5 (balcony, hand down), 3.5 (wave rippling), 7.5 (cell + candle), 10.0 (swirl mid), 12.0 (crown
over arms), 16.5 (dice → paint), 18.0 (swirl), 20.0 (pillars crumbling), 23.0 (carriage), 27.0
(key), 28.0 (swirl), 29.5 (bells + rings), 33.0 (horsemen), 37.0 (cracked crown in mirror), 38.0
(swirl), 40.0 (doors + shards), 44.0 (red flag), 48.0 (thread cut), 50.0 (swirl), 53.0 (silhouette
+ slit), 57.0 (crown rolling), 59.5 (black).
