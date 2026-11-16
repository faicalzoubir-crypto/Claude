# The Last King (Darija): review

Delivery: `livrables/the-last-king-darija.mp4`, 1080 x 1920 (9:16), 30 fps, 85.77 s, H.264 + AAC
(the clips' own sound), 92.5 MB.

## What it is

The person's three clips (`assets/clips/part-1..3.mov`, their own edit of "The Last King" with
sound) joined in the order given (0-30.015, 30.015-60.0, 60.0-85.739), with six Arabic (Darija)
lines burned in one after another, all in the same place on screen (as asked): lines 1-5 within
the first 20 s, line 6 over the last 20 s. Text, times and place live in `tools/captions.py` (run it
to rewrite `compositions/captions.html`).

| Line | Time (s) | Over |
| --- | --- | --- |
| واش كنتي عارف بلي هاد الأغنية | 0.15-4.13 | the balcony |
| لي ديما كاتطلق فالمناسبات و الاحتفالات | 4.13-7.83 | the gold draining into the cell |
| هي فالأصل كاتهضر على سقوط الملكية ففرنسا | 7.83-11.31 | the king alone in the cell |
| فرقة coldplay عمرهم أكدو هادشي | 11.31-15.74 | the crowd lifting the crown |
| وكيقولو الأغنية كاتكلم على سقوط القوة | 15.74-20.0 | the crown, then the dice |
| و أن كل من يعيش المجد اليوم قد يجرب الذل غدا | 65.74-85.74 | the walk to the light, the crown rolling away |

## Creative calls

- Line changes sit on the nearest beats (measured onsets 4.13, 7.83, 11.31, 15.74); line 5 ends at
  20.0 s; line 6 starts exactly 20 s before the end.
- Brand (`brand/BRAND.md`): text `#E8EEEC` on a `#141D21` card at 82% with a `#26343B` border,
  14 px radius, one amber `#F4A62A` phrase per line, and the thin amber progress bar on the bottom
  edge. The brand faces (Space Grotesk, Inter) have no Arabic, so the lines use Readex Pro Bold
  (Arabic + Latin, a geometric companion; `assets/fonts/`, OFL licence alongside).
- Words enter in reading order (right to left), 0.06 s apart; a lone «و» stays with the next word
  and amber phrases never break across lines; lines are balanced.
- The text is the person's, unchanged (including the lower-case "coldplay").
- One place for every line: centred, top edge at 290 px, inside the area TikTok, Reels and Shorts
  all leave clear (x 120-888, y 288-840, from the CLI's own tables). Up there it keeps the king,
  the dice, the walker and the rolling crown clear; the lifted crown only grazes the card in the
  last second of its rise (about 16.5-17.5 s). Cards are compact (46 px text, two lines).
- Exits state both ends of the fade, so scrubbing backward in Studio shows the same frames as
  playing forward (tested both seek orders).

## Measured

- In the render: caption text present at 2, 6, 9.5, 13.5, 18, 66.5, 75 s; absent at 0.05, 20.2, 30,
  50, 65.5 s and in the last 0.2 s.

- `check`: ok, 0 errors, 0 safe-zone warnings.
- The render: 1080 x 1920, 30 fps, 85.77 s, audio present (mean -26.0 dB, peak -11.7 dB, same
  as the sources). Every stretch of rendered sound found in its source clip at offset +0.000 s.
- No black flash or level drop at the joins (30.015 s, 60.0 s).

## Only looked at

- Caption crops at full size and frames across the film; not watched at full speed on a phone.

## Kept on purpose

- `timeline_track_too_dense`: all six lines on one captions track, as Studio expects for captions.
