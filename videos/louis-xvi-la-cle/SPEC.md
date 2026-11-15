# SPEC — « La clé » (Louis XVI, 90 s, vertical, on Viva La Vida)

GOAL: a hook in the reference clip's style pulls the viewer in ("Wait, what's the song that goes like…"), then one
still King watches his world turn behind him — the candlelit Hall of Mirrors, the crowd at Versailles, the cold
Place de la Révolution — and loses the key ("One minute I held the key… I know Saint Peter won't call my name").

OUTPUT: HyperFrames, authored 1080 × 1920, 30 fps, rendered `--resolution portrait-4k` (2160 × 3840) by
`tools/render_4k.sh`: 6-s spans in fresh browsers, joined without re-encoding, soundtrack muxed once.

SOUND (tools/bande.sh → assets/audio/bande.wav, −14.9 LUFS / −1 dBTP, exactly 90.000 s; kept out of git):
| film s           | source                              | words                                             |
| ---------------- | ----------------------------------- | ------------------------------------------------- |
| 0.000–22.845     | reference clip 0–22.845             | "Wait, what's the song that goes like…" · verse 1 lines 1–4 |
| 22.845–36.765    | Viva La Vida 54.715–68.635          | "One minute I held the key … pillars of sand"     |
| 36.765–50.685    | 68.635–82.545                       | "I hear Jerusalem bells … in a foreign field"     |
| 50.685–64.605    | 124.265–138.195                     | "Revolutionaries wait … who would ever want to be king?" |
| 64.605–90.000    | 152.115–177.510 (fade 87.8–90)      | "For some reason … Saint Peter … when I ruled the world", bridge |
Splices: 80 ms equal-power crossfades centred on downbeats, all at the same position of the 4-chord loop.
138 BPM: beat 0.435 s, bar 1.739 s, section (8 bars) 13.92 s.

TIME / SECTIONS (each later scene dissolves in over 1.5 s from its downbeat; the intro → verse 1 is a hard cut):
| section        | s               | scene      | picture                                                    |
| -------------- | --------------- | ---------- | ---------------------------------------------------------- |
| INTRO          | 0–22.845        | intro      | reference edit: hook shot, black, a pan, 27 one-beat details |
| VERSE 1        | 22.845–36.765   | v1 + king  | Hall of Mirrors by candle; the King holds the key; push in |
| REFRAIN 1      | 36.765–50.685   | r1 + king  | Versailles at grey dawn; the women's march rises behind him; dawn light, half his face in shadow |
| VERSE 2        | 50.685–64.605   | v2 + king  | the Hall again, dimmer; the key lowers on "Just a puppet…" (57.66) |
| FINAL REFRAIN  | 64.605–78.515   | fr + king  | Place de la Révolution, cold dawn; the King of 1793; the key slips on "Saint Peter" (70.39) |
| OUTRO          | 78.515–90       | outro+king | torches (Houël) · falling crown · turning clock · empty throne, one bar each; pull back; black at 90 |

INTRO (compositions/intro.html, written by tools/build_intro.py):
- 0–5.667 the Galerie des Glaces, push 1.00 → 1.08; words WAIT · WHAT'S · SONG · THAT · GOES · LIKE on the speech.
- 5.667–6.100 black. 6.100–9.467 a pan across the whole Cochin gallery, `power2.in`, 2563 px.
- 9.467–22.845 the reference's cut times (one detail per beat from 11.9 s), each with a push in/out or a 120 px drift.
- one word per sung word (the reference's timing): USED RULE THE WORLD SEAS RISE WHEN I GAVE THE WORD NOW IN THE
  MORNING I SLEEP ALONE SWEEP THE STREETS I USED TO OWN — OWN (22.75–23.25) rides over the cut to the King.
- lettering (the reference's): Montserrat 500, 138 px caps, tracking +0.02 em, #E3957F, `mix-blend-mode: difference`,
  centred on y 820. Words appear only in the intro.

LAYOUT (1080 × 1920): action box x 108–972, y 96–1536; caption band y 1536–1920 sinks to 0.84–0.9 black from y 1180.
The King is one layer (sub-composition `king`, 22.845–90) never repositioned; only a camera scale about his eyes (507, 590).

LOOK — an oil painting lit by one candle:
- real 18th-century works (public domain / CC0, see CREDITS.md); Kuwahara 0.22–0.35 on prints and photos, none on the Callet.
- verse light: temperature +0.18, exposure flicker ±0.03 in 0.45–0.8 s seeded segments; verse 2 at −0.12.
- dawn: temperature −0.28, saturation −40 %, exposure −0.2; the shadow copy (exposure −1.1) masked over the far half of his face.
- grain 0.14 / size 0.22 / roughness 0.6 on every image; vignette 0.3–0.45.
- the King: Callet 1786 (red velvet coat recoloured to royal blue #060B26 → #4D619E), oval softened, lower chest sinking
  into shadow; in the final refrain Ducreux's January 1793 drawing (mirrored, coat toned blue, cold), eyes on the same point.
- the key: Met 89207 (18th c.), 250 px, near-black iron with a warm edge, over the white lace jabot.

MOTION: camera `sine.inOut` 1.00 → 1.07 (verse 1) → 1.09 → 1.12 (verse 2) → 1.13 → 0.96 (outro pull-back);
backgrounds drift 1.00 → 1.035 linear; the crowd rises 520 px over 7 s; the key falls 1000 px in 0.85 s (`power2.in`,
+73°) after a 4-frame lift; outro shots enter on a 230 px vertical move (0.6 s `power3.out`), the crown falls,
the dial turns 300°; the world goes dark 86.9–88.5, the King 87.5–90.

BANNED: words outside the intro; lettering inside any painting crop; glow, bloom, flares, particles, light leaks;
a blade, a head or blood at the scaffold (the Demachy crop keeps the guillotine out of frame); the King moving on his
own; CSS filters for grade, grain, blur or vignette; anything modern.

QA: 0.3, 2.5, 7.5, 9.6, 12.1, 16.9, 22.7, 23.0, 30, 37.5, 45, 55, 60, 65.4, 70.6, 75, 80, 83.5, 85.8, 88.6 —
the King in the same place from 22.845 on; nothing but shadow below y 1536 after the intro; no lettering inside
pictures; the scaffold never readable; words only before 23.25.
