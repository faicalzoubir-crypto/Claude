# REVIEW — « Six gestes » v2, full length (EN-NOUR 3 · Communiqué évaluatif)

## What changed from v1, at the person's request

- Same length and same steps as the recording: 100.733 s, played once at 1×, no cut and no speed change, so film time = source time. v1 (the 40 s cut with the rewind hook) is kept as `livrables/communique-evaluatif-40s-HD.mp4`.
- Music and tap sounds, no voice-over (« Je ne veux pas voix off »). The recording's own voice is not used.
- The moments where nothing happens on the screen are not cut. Each one gets a graphic beat drawn from what is really on screen:
  - the home page (0–13.5 s): the title, then the day's two SVT lessons outlined, then the plan of the six steps;
  - the 15 s pause after SVT: the five real options of the « Type » list, then the three fields already filled, outlined;
  - the open calendar: callouts on today (14) and on the next-month arrow;
  - the end: the published card, the chips flying into it, the app's own status turning « Validé », the claim, the logo.

## v2.1: the app's logo (asked by the person)

- The EcolePlus icon comes from the person's screenshot: cropped to the 204 px icon, with the corners masked and the image upscaled 2× (`assets/brand/logo-ecoleplus.png`). It is the real pixels, not a redraw. Because the source is small, it is shown at 220–240 px at most.
- Opening: the icon and its name sit on the iPad as on a home screen. A tap (0.85 s) opens it, and the icon grows into the screen to reveal the app's home page. Frame 0, the thumbnail, now shows the title over the icon.
- End card: the EcolePlus icon and name with « COMMUNIQUÉ ÉVALUATIF », and the EN-NOUR 3 logo smaller below.

## Creative calls kept from v1

- The haptics on every real tap: touch dot, ring, the screen pressing in, a device shake, a click and a thump.
- Values lift off the screen as amber chips and fly into the published card at the end.
- The amber flash on « Envoyer » and the iris from that point onto the result.
- House brand from `brand/BRAND.md`. The school's colours appear only in its logo.

## Measured vs looked at

- `check`: 0 errors.
- Delivery render read frame by frame at every tap, chip, box, callout and seam, and at the iris and end card.
- Sound (`npx hyperframes audio`, ebur128): −14.0 LUFS integrated, true peak −1.3 dB, no clipping, the loudest moment at 80.38 s (the « Envoyer » impact). Each tap's sound lands 10–30 ms after its tap frame. Measured, not heard.
- `tools/master.sh` masters the delivery file (two-pass loudnorm). The raw render mixes quieter.

## Kept on purpose

- `line_unread` on the chips: each scene file sees only its own slice, but a chip stays on screen from its landing until it flies into the card.
- `escaped_container` on the camera layers: the camera layer is meant to be larger than the screen that clips it.
- Render motion blur is off. With it on, frames that contained a scale animation lost the recording, and the screen came out blank.
- Camera cuts at 8.75, 13.5 and 17.7 s instead of moves: a move there would pass the home-page posters (children's photos) at close-up size. The teacher's name in the menu is never in a close-up either.

## Weakest moments / with more time

- 50.0–53.8 s: about 4 s on the date field before the teacher taps it. Only the title changes there.
- 75.3–78.7 s: the pasted message is held without a new graphic for 3.4 s.
- 82.3–83.8 s: while the chips fly into the card, the camera is wide and the card's own text is too small to read. It becomes readable at 84.7 s.
