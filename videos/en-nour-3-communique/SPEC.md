# SPEC — « Six gestes » · EN-NOUR 3, Communiqué évaluatif

```text
GOAL:    a teacher who watches once can publish a communiqué évaluatif: they remember the six fields and the one tap on « Envoyer ».
OUTPUT:  HyperFrames, 1080 x 1920, 30 fps, MP4 for Reels / TikTok / Stories.
TIME:    40 s x 30 = 1200 frames. Music 90 BPM: 1 beat = 20 frames (0.667 s), 1 bar = 80 frames (2.667 s), 15 bars.

LOOK:    house brand (brand/BRAND.md, brand/frame.md).
         ground #0D1316 + 60 px hairline grid #26343B at 55 %, flat, no gradients.
         ink #E8EEEC, secondary #93A4A7; ONE amber #F4A62A per moment: the eyebrow + the newest chip (text on amber #0D1316).
         eyebrow: amber line 60 x 4 at x 80, y 212 + Space Grotesk 600 26 px caps 0.08em amber at x 156.
         title: Space Grotesk 600 76 px, -0.02em, #E8EEEC, x 80, top 240, one line (hook: 80 px, two lines).
         chips row y 352-400: Space Grotesk 600 28 px, radius 12, h 48; new = amber fill, landed = #141D21 + 1.5 px #26343B + #E8EEEC.
         the medium is the real iPad screen: the recording itself, never redrawn, in a flat bezel
         #1B2529 with a 1.5 px #2E3D44 line, radius 40; screen 720 x 1036 at (180, 456) = source x 2/3, radius 24.
         no shadow, no glow, no grain, no vignette. Claim: Space Grotesk 700 120 px. End card: the school's logo PNG, 560 px wide.
OBJECTS: the iPad (bezel + screen), the finger (touch dot 64 px, white 30 % fill, 2 px white 85 % line),
         the chips (one per value: T.C.S.F1 · T.C.S.F2, DS, SVT, 04/11/2026, Message), the published card in the list.
HAPTICS: (asked by the person) every real tap on screen gets all four, starting on the tap frame:
         touch dot in 0.12 s before, press 1 → 0.78 → 1; one white ring 64 → 154 px, 0.9 → 0 opacity in 0.38 s expo.out;
         screen content presses around the tap point 1 → 0.965 (0.07 s) → 1 (elastic 1, 0.45, 0.45 s);
         device shake x 0, -6, 5, -3, 1.5, 0 px over 0.2 s; sound click + low thump, peak one frame after the picture.
MOTION:  camera = zoom z (1 = whole screen) + focus point in source px, ln z interpolated; moves 0.45-0.6 s power3.inOut,
         arrivals expo.out, exits power3.in; holds during every tap. Render motion blur on (data-motion-blur).
         titles: per-word blur 6 → 0 px in 0.13 s, 0.067 s apart (alternating with grey → ink per word); exit blur 8 px in 0.2 s.
         step number rolls like a counter (0.2 s). Chips: pop at the tapped value back.out(1.7) 0.22 s, fly 0.5 s power3.inOut, land
         with a 1.12 → 1 settle. Springs on scale only, never on opacity or colour.
SHOTS (film s · source s → rate):
  s0 accroche 0-4.667   frame 0 = the published card, z 2.4 · 80.90-84.23 → 1.0; 0.333 card thump; 1.333 title lands;
                        3.333-4.667 rewind: reverse scrub 84.23 → 17.50 (pre-rendered, eased), camera pulls back to z 1. Whoosh.
  s1 ouvrir 4.667-9.333  menu (17.50-18.30 → 1.0, tap ☰ 4.787) · item (19.40-21.45 → 1.577, tap 6.653) ·
                        list (22.40-25.25 → 1.5, tap + 8.620) · form opens (25.25-25.70 → 0.675). Zoom through « + ».
  s2 classes 9.333-12.667   25.70-29.75 → 1.215; taps 9.522 field, 10.938 T.C.S.F2; chip 1 at 11.40. Zoom pulse out.
  s3 type 12.667-15.333     30.20-31.90 → 1.417, 33.16-34.70 → 1.05; taps 13.333, 14.667 (on beats); chip 2 at 14.80.
  s4 matiere 15.333-18      34.975-38.875 → 1.4625; taps 16.000, 17.333 (on beats); chip 3 at 17.45. Whip to the date.
  s5 date 18-21.333         53.40-54.55 → 0.975, 64.20-64.95 → 0.862, 65.40-66.645 → 0.97; taps 18.667, 19.667, 20.667; chip 4 at 20.85.
  s6 message 21.333-26.667  67.10-70.20 → 1.2, 70.80-72.70 → 1.5, 73.95-75.43 → 1.0; taps 22.0 titre, 24.016, 25.016, 25.533 Paste;
                        keys 23.54, 23.71 (sound only); chip 5 at 26.0.
  s7 envoyer 26.667-29.333  78.70-79.90 → 0.857 (keyboard drops, the whole filled form shows at z 1), 79.90-80.30 → 0.316;
                        push to « Envoyer », riser, music drops out at 28.95; tap = impact at 29.333 (bar 11 downbeat).
  s8 resultat 29.333-33.333 80.70-84.70 → 1.0; amber flash + iris from the Envoyer point (0.3 s); card at z 2.4, pull to z 1.1;
                        the five chips fly into the card's DS badge, tags, date, message, SVT (0.25 s apart) with pops.
  s9 fin 33.333-40      device exits (scale 0.9, y +80, blur, 0.4 s power3.in); « Un formulaire, un envoi. » per word;
                        36.0 blur swap to the EN-NOUR 3 logo + « COMMUNIQUÉ ÉVALUATIF », held 3.5 s; music resolves on Dm.
SOUND:   brand bed 90 BPM D minor (Dm | Dm | B♭ B♭ | F F | C C | Dm Dm | B♭→C riser | Dm impact | B♭ | F | Dm), pad + bass +
         arpeggio + light hats in the steps; near silence 28.95-29.333; −14 LUFS, true peak ≤ −1 dBTP.
         taps: click + thump (3 takes rotated); chip landings: pop; keys: key press; whooshes only on s0 rewind, s1 zoom-through,
         s4 whip, s9 exit (rotated takes); one riser → impact on Envoyer.
BANNED:  a dark void with small things floating (the iPad fills 70 % of the width); glow, bloom, particles; gradients; glass;
         everything centred (titles and chips are left-aligned; only the end card is centred); everything fading and sliding up;
         titles moving after they land; breathing or pulsing loops; corner labels, HUD; three cards in a row; the logo docked
         in a corner; redrawn app screens; the home-page posters (children's photos) or the account name in a close-up;
         invented claims (only what the recording shows: fields, values, « Opération réussie »); emoji.
QA:      0.0 (thumbnail: the card readable), 1.5 (title), 4.0 (rewind mid), each tap frame (dot on the real control),
         each chip landing, seams 4.667 9.333 12.667 15.333 18 21.333 26.667 29.333 33.333 36, 29.40 (iris), 32.5 (chips in the card),
         39.9 (end card); values exactly T.C.S.F1, T.C.S.F2, DS, SVT, 04/11/2026; text ≥ 28 px; words inside y 168-1330.
```
