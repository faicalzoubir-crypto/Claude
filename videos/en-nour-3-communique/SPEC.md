# SPEC — « Six gestes » · EN-NOUR 3, Communiqué évaluatif (full length, v2)

v2 (the person's request): the same length and the same steps as the recording, uncut; music and the
tap sounds, no voice. v1 (the 40 s cut) is kept as `livrables/communique-evaluatif-40s-HD.mp4`.

```text
GOAL:    a teacher who watches once can publish a communiqué évaluatif: they remember the six fields and the one tap on « Envoyer ».
OUTPUT:  HyperFrames, 1080 x 1920, 30 fps, MP4 for Reels / TikTok / Stories.
TIME:    100.733 s x 30 = 3022 frames = the recording, played once at 1x with no cut (film time = source time).
         Music 90 BPM, 1 beat = 20 frames; the bar grid starts at 0.3 s so the tap on « Envoyer » (80.3 s) is a downbeat.

LOOK:    house brand (brand/BRAND.md, brand/frame.md).
         ground #0D1316 + 60 px hairline grid #26343B at 55 %, flat, no gradients.
         ink #E8EEEC, secondary #93A4A7 / #6E8186; amber #F4A62A for the eyebrow, the newest chip, step numbers, boxes and callout lines.
         eyebrow: amber line 60 x 4 + Space Grotesk 600 28 px caps 0.08em amber; title Space Grotesk 600 76 px, -0.02em (intro 80 px, 2 lines).
         chips row y 352-400: Space Grotesk 600 28 px, radius 12; new = amber fill, landed = #141D21 + 1.5 px #26343B.
         the medium is the real iPad screen in a flat bezel #1B2529 / 1.5 px #2E3D44, radius 40; screen 720 x 1036 at (180, 456).
         boxes: 3 px amber outline, radius 12. callouts: 18 px amber dot, 2 px amber line, label #141D21 with a 2 px amber border.
         no shadow, no glow, no grain, no vignette. Claim Space Grotesk 700 120 px; end card: the school's logo, 560 px wide.
HAPTICS: every real tap: touch dot (in 0.12 s before, press 1 → 0.78 → 1), one white ring 64 → 154 px in 0.38 s,
         the screen content pressing around the finger (1 → 0.965 → elastic back), a 0.2 s device shake, a click + low thump.
MOTION:  camera = zoom z + focus point in source px, ln z interpolated; moves 0.45-0.8 s power3.inOut, arrivals expo.out,
         exits power3.in; holds during every tap; punch cuts where a move would pass the children's photos.
         titles per word (blur 6 → 0 in 0.13 s, 0.067 s apart, or grey → ink), whole line, or slam (scale 1.3 → 1); exit blur 8 px 0.18 s.
SHOTS (film s = source s):
  s0 intro 0-13.5      frame 0 = thumbnail: « Annoncer un DS en 6 gestes » over the EcolePlus icon on the iPad; tap 0.85,
                       the icon grows into the screen (1.05-1.65) and the app's home page appears; 3.6 push onto the day's
                       timetable, the two SVT lessons outlined (T.C.S.F2 08:30, T.C.S.F1 10:35); 8.75 punch out, « Six gestes »
                       and the plan rail 1 Menu · 2 Classes · 3 Type · 4 Matière · 5 Date · 6 Message.
  s1 ouvrir 13.5-25.33  punch in on ☰ (callout « Menu »), tap 17.62, cut to the menu items, tap 21.27, list, push to « + »,
                       tap 25.18 and zoom through it.
  s2 classes 25.33-30   taps 25.93, 27.65 (T.C.S.F2); chip 1.     s3 type 30-34.8: taps 31.15, 34.0 (DS); chip 2.
  s4 matiere 34.8-38.6  taps 35.95, 37.9 (SVT); chip 3.
  s5 rappel 38.6-50     the iPad steps aside: « 5 types d'épreuve » (the five real options, DS in amber); it comes back:
                       « 3 gestes sur 6 », the three filled fields outlined; push to the date field.
  s6 date 50-67         tap 54.05, the calendar; callouts « Aujourd'hui » (14) and « Mois suivant » (›); taps 64.62, 66.0; chip 4.
  s7 message 67-78.7    taps 67.9 (Titre), keys 69.75 / 69.95, 70.95, 72.45, 73.38 (Paste); the message; chip 5.
  s8 envoyer 78.7-80.73 the whole filled form, push to « Envoyer », riser, tap 80.3 = impact, amber flash.
  s9 resultat 80.73-90  iris from the « Envoyer » point onto the published list; the five chips fly into the card; read the
                       card; pan to the app's own status turning « Validé » (callout).
  s10 fin 90-100.73     the iPad leaves; « Un formulaire, un envoi. » (data-hold); 94.3 the EcolePlus icon + name +
                       « COMMUNIQUÉ ÉVALUATIF », 95.3 the EN-NOUR 3 logo below, held to the end.
SOUND:   brand bed 90 BPM D minor: intro pad + arpeggio; groove in the steps; lighter in the rappel; build from 77.6, near
         silence 79.95-80.3, drop on « Envoyer »; resolve on Dm add9 from 96.3. Taps: click + thump (3 takes), pops on chips and
         boxes, key ticks on the plan and callouts, whooshes on camera moves (rotated takes), one riser → impact. No voice.
         Mastered to −14 LUFS, true peak ≤ −1 dBTP (tools/master.sh).
BANNED:  a dark void with small things floating; glow, bloom, particles; gradients; glass; everything centred; everything fading
         and sliding up; titles moving after they land; breathing or pulsing loops; HUD corner labels; three cards in a row; the
         logo docked in a corner; redrawn app screens; children's photos or the account name in a close-up; invented claims; a
         voice-over; cutting or speeding the recording.
QA:      0.5 (thumbnail), 6.0 (boxes on the lessons), 11.5 (plan rail), 15.8 (callout Menu), 17.72 (cut, no photo, no name),
         every tap frame, 42 (types), 45.6 (three boxes), 56.5 / 60 (callouts), 80.5 (flash), 81.0 (iris), 83.2 (chips into the card),
         88.8 (Validé), 92 (claim), 99 (end card); values T.C.S.F1, T.C.S.F2, DS, SVT, 04/11/2026; text ≥ 28 px.
```
