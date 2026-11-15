# The Last King — spec

GOAL:    a silent, dreamlike fall of a lone king told as one moving oil painting: power, the
         gamble of the crown, flight, omens, revolt, and the empty walk into the light. The viewer
         ends on black, having watched the crown roll away.
OUTPUT:  HyperFrames, 1920 x 1080, 24 fps, 16:9 landscape, the picture letterboxed to 2.4:1
         (138 px black bars) like the reference. Silent (no music, no voice, no captions, no
         on-screen text). The person adds their own track later.
TIME:    60 s x 24 = 1440 frames. Six scenes: 10 + 8 + 10 + 10 + 12 + 10 s.

## Reference: the person's clip (Scott Free ident, 17.5 s, 1920 x 800, 23.976 fps)

Its grammar, never its content (no figure-to-bird morph, no bird, no logo).
Measured: 2.4:1 frame; 47% of pixels near-black before the logo; no hard cut (no frame-diff
spike above the 0.25 scene threshold); slow drift for the first 3 s (mean frame difference 1–4 on
255 at 4 fps) then smear moves of 0.5–1 s (difference 70–90); palette clusters `#28211C` umber,
`#3C3632`, `#514B4B`, `#51546E` dusty blue-grey, `#6E6660`, `#897E77`, `#A6977A` cream-yellow,
`#B4ADB0` bone, plus one red spot `#A1382A`.
Seen (not measured): smooth wet-on-wet oil, like paint-on-glass animation, in long curved sweeps,
not thick impasto; each image is an irregular pool of light with a swept, brushy edge in pure black;
figures are a few strokes, faceless; changes happen by the paint smearing along an arc into the
next form while the camera keeps moving.

## Look (one medium: wet oil on glass, moving)

- **Ground**: pure black `#000000`; about half of every interior frame. The image floats in it as
  an irregular pool of painted light with swept edges (carried by the AI footage; no CSS vignette).
- **Light, cream-yellow** `#C9BD86` / `#A6977A`, bone `#B4ADB0`: lamp-light, crowns, the palace,
  the crowd's raised arms. Gold for the crown `#C9A24A`.
- **Cold, blue-violet** `#51546E` → periwinkle `#6F78A8`: night, the cell, snow, ghosts, the end.
- **Shadow, umber** `#28211C` / `#3C3632`.
- **Accent, red** `#A1382A`: ONE small thing per frame at most (the gem on the crown, the flag in
  scene 5). Never a red wash.
- **Brushwork**: smooth blended strokes 5–15% of frame width, curved, following the motion; faint
  canvas texture. Slow fluid motion only (camera ≤ 3% of frame width per second).
- **People**: no faces anywhere. The king's head is a soft pale shape under the crown.
- **The king**: same figure every time: long pale bone-white cloak to the floor, simple gold band
  crown with one small red gem, thin, upright, alone. Reference still `assets/stills/king-ref.png`.
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
  smears the outgoing image along an arc (4-sample smear along the flow, up to 190 px) while a matte
  of broad curved strokes (5 overlapping bristles, 48–112 px wide at 1080) paints the incoming one
  in, stroke by stroke, in spiral order. Baked per boundary as `assets/transitions/tN.mp4`
  (`tools/brush_transition.py`) and laid over the boundary on its own track.
- Ending: fade to pure black from 57.4 s, black from 59.2 s to 60 s.
- Reference shot grammar applied to the AI prompts: each shot is one continuous camera drift; the
  image is a pool of light in black.

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

Text, letters, numerals, logos, watermarks, signatures in any frame; thick impasto ridges; a
CSS vignette or grain; anything copied from the reference (its bird, its cloaked man, its logo); captions; a presenter; stock
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
