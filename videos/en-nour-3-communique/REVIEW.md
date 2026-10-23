# REVIEW — « Six gestes » (EN-NOUR 3 · Communiqué évaluatif)

## Creative calls

- Storyline 1 « Six gestes » (picked by the person), music + haptic sound, no voice. Not built: 2 « Mercredi 4 novembre » (one continuous take from the timetable) and 3 « Tap, tap, envoyé » (beat-cut kinetic type). Both are in `STORYLINES.md`.
- The 100.7 s recording became 40 s (15 bars at 90 BPM). The waiting is cut: the 15 s pause after SVT, most of the calendar, the final 15 s on the list. Every screen is the real recording, sped up 1.2–1.6× in the steps, and the source is never redrawn.
- "Haptics" (the person's word) means four things on every real tap, all starting on the tap frame: a touch dot, one ring, the screen content pressing around the finger (scale 0.965 with an elastic return), and a 0.2 s device shake, plus a click with a low thump. Five taps land exactly on beats (13.33, 14.67, 16.0, 17.33, 29.33).
- Graphic transitions, each with a cause: a rewind scrub (the hook), a zoom through « + », a zoom pulse, whips to the calendar and back to the title field, a pull-back that shows the whole filled form, an amber flash plus an iris from « Envoyer », and a blur swap to the logo.
- The values the teacher sets lift off the tapped control as amber chips and collect under the title. In the result they fly into the matching parts of the published card.
- House brand from `brand/BRAND.md`. The school's colours appear only in its logo, on the end card.

## Measured vs looked at

- `check`: 0 errors. The kept warnings are listed below.
- Snapshots at every tap, chip and seam; a full render reviewed frame by frame (see "Render pass").
- Sound: measured on the render (loudness, true peak, hit positions), not heard.

## Kept on purpose

- `line_unread` on the chips (s2-c1, s5-c4, s8-c1): each scene file sees only its own slice. A chip stays on screen from its landing until it flies into the card, 5–19 s in all.
- Layout infos `escaped_container` / `container_overflow` on the camera layers: the camera layer is meant to be larger than the screen that clips it.
- Render motion blur (`data-motion-blur`) is off: with it on, frames that contained a scale animation lost the screen recording (blank screen at 1.6 s and 9.53 s in snapshots). The chips carry their own blur in flight instead.

## Render pass

- Read 54 frames of the delivery render: every tap, chip, seam, the iris (29.37–29.65) and the end card. The recording shows in every frame (with render motion blur on, the snapshots had blank screens).
- The values on screen match the recording: T.C.S.F1, T.C.S.F2, DS, SVT, 2026-11-04 / « LE : Mer. 04 nov. 2026 », « Opération réussie ».
- Sound (`npx hyperframes audio`, ebur128): −14.0 LUFS integrated, true peak −1.2 dB, no clipping, the loudest moment at 29.42 (the « Envoyer » impact). Each tap's sound lands 0–27 ms after its tap frame. Measured, not heard.
- The delivery file's sound is mastered by `tools/master.sh` (two-pass loudnorm). The raw render mixes at −21 LUFS.

## Weakest shot / with more time

- 18.0–18.66: the whip lands on the right half of the form about 0.6 s before the calendar opens, so the screen is mostly empty grey fields. Next step: land on the date field itself, then pan to the calendar as it opens.
- 30.6–32.1: while the chips fly into the card, the camera is wide (z 1.1) and the card's own text is too small to read. It becomes readable at 32.85 after the push-in. Next step: follow each chip's target with a short pan at z ≈ 1.8.
- The claim frame (33.6–36) is type alone on the grid. It could keep the published card small beside it.

## Not used

- The voice in the recording: the person chose music and haptic sound. A transcript was never made, because the only Whisper model reachable here is a third-party npm copy and auto mode blocked running it.
- Children's photos on the home page appear only at full-screen size (rewind end, menu opening), never in a close-up. The teacher's name in the menu is never in a close-up.
