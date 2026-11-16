# The Last King (Darija): review

Delivery: `livrables/the-last-king-darija.mp4`, 1080 x 1920 (9:16), 30 fps, 85.77 s, H.264 + AAC
(the clips' own sound), 89.1 MB.

## What it is

The person's three clips (`assets/clips/part-1..3.mov`, their own edit of "The Last King" with
sound) joined in the order given (0-30.015, 30.015-60.0, 60.0-85.739), with six Arabic (Darija)
lines burned in one after another. Lines 1-5 within the first 40 s, line 6 over the last 20 s, as
the person asked. Text and timing live in `tools/captions.py` (run it to rewrite
`compositions/captions.html`).

| Line | Time (s) | Over |
| --- | --- | --- |
| واش كنتي عارف بلي هاد الأغنية | 0.15-6.74 | the balcony (card high, off the king) |
| لي ديما كاتطلق فالمناسبات و الاحتفالات | 6.74-15.74 | the cell, the crowd lifting the crown |
| هي فالأصل كاتهضر على سقوط الملكية ففرنسا | 15.74-23.77 | dice to gold, the palace swirl |
| فرقة coldplay عمرهم أكدو هادشي | 23.77-32.26 | horsemen, the carriage fleeing, the key |
| وكيقولو الأغنية كاتكلم على سقوط القوة | 32.26-40.0 | the palace crumbling |
| و أن كل من يعيش المجد اليوم قد يجرب الذل غدا | 65.74-85.74 | the walk to the light, the crown rolling away (card high, off the walker) |

## Creative calls

- Every change after the first sits on a strong beat of the music (measured onsets 6.74, 15.74,
  23.77, 32.26); line 6 starts exactly 20 s before the end.
- Brand (`brand/BRAND.md`): text `#E8EEEC` on a `#141D21` card at 82% with a `#26343B` border,
  14 px radius, one amber `#F4A62A` phrase per line, and the thin amber progress bar on the bottom
  edge. The brand faces (Space Grotesk, Inter) have no Arabic, so the lines use Readex Pro Bold
  (Arabic + Latin, a geometric companion; `assets/fonts/`, OFL licence alongside).
- Words enter in reading order (right to left), 0.06 s apart; a lone «و» stays with the next word
  and amber phrases never break across lines; lines are balanced.
- The text is the person's, unchanged (including the lower-case "coldplay").
- Placement: inside the area TikTok, Reels and Shorts all leave clear (from the CLI's own tables):
  low cards in x 130-770, bottom at 1240 px; high cards centred, top at 330 px.

## Measured

- `check`: ok, 0 errors, 0 safe-zone warnings.
- The render: 1080 x 1920, 30 fps, 85.77 s, audio present (mean -26.0 dB, peak -11.7 dB, same
  as the sources). Every stretch of rendered sound found in its source clip at offset +0.000 s.
- No black flash or level drop at the joins (30.015 s, 60.0 s).

## Only looked at

- Caption crops at full size and frames across the film; not watched at full speed on a phone.

## Kept on purpose

- `timeline_track_too_dense`: all six lines on one captions track, as Studio expects for captions.
