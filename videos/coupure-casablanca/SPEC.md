# SPEC: «انقطاع الكهرباء بالدار البيضاء» (11 نونبر 2026)

GOAL: the viewer knows what happened at 16:48, sees which neighbourhoods were reported dark, understands
that Ouled Haddou and Dar Bouazza are SUBSTATIONS (transformation, not generation), hears ONE marked
hypothesis for the cause, five ways to prevent a repeat, and leaves with the open question.

OUTPUT: HyperFrames, 1080 × 1920 (9:16), 30 fps, Arabic RTL, burned-in captions, one avatar presenter.

TIME: set by the voice (one HeyGen voice, phrase by phrase, `script.json`). Target 3:20–3:45.
Scene slots (s): S1 ≈ 26 · S2 ≈ 40 · S3 ≈ 44 · S4 ≈ 38 · S5 ≈ 36 · S6 ≈ 28 · END 7.
Music: brand bed (brand/BRAND.md) 90 BPM = 20 frames a beat, D minor Dm–B♭–F–C two bars a chord,
under the voice at about 0.14, mix −14 LUFS, true peak ≤ −1 dBTP.

SAFE AREA (user rule, stricter than the platform guide):
- y 0–150 and y 1670–1920 stay empty of avatar and text (only the ground, the map, the progress bar).
- Captions: bottom edge at y 1650, max 2 lines, IBM Plex Sans Arabic 700 at 58 px (min 46 px by fit),
  line-height 1.32, fg #E8EEEC, 2 px #0D1316 outline (paint-order stroke) + 0 3px 10px rgba(0,0,0,.65).
- Everything else read on screen: y 160–1470, x 64–1016.

LOOK (brand/BRAND.md):
- ground #0D1316 + 60 px hairline grid #26343B @ 40 % on avatar/schematic scenes (the user's "plain dark
  navy": the grid stays faint). Surfaces #141D21, lines #26343B, text #E8EEEC / #93A4A7, faint #6E8186.
- ONE amber #F4A62A thing per moment: the time 16:48, the active zone label, the "فرضية – غير مؤكدة" chip,
  the current bullet number. Mint #93CDBB only for drawn objects (pylons, plants, transformers, wires).
  #F25C54 only for the fault (the short-circuit spark ring, the cut line).
- Type: IBM Plex Sans Arabic 700 (titles 84–96 px, labels 30–34 px, bullets 76 px), 600 for secondary;
  Latin/numbers Space Grotesk 700 (16:48 at 150 px). Thin dark outline on every word over the map.
- Map: real Esri World Imagery (z14, stitched once, `tools/basemap.py`), graded to night with
  media-treatment (exposure −1.25, saturation −0.55, temperature −0.35, contrast +0.15, vignette 0.3).
  Dark zones: radial #04080A @ 0.92 → 0 over r ≈ 46–64 px (soft edge), dim ring #93A4A7 @ 0.35 1.5 px,
  white labels 30 px. Lit zones: amber radial glow #F4A62A @ 0.55 → 0 over r ≈ 70 px, screen blend,
  amber labels. Off-frame: 26 px chevrons on the frame edge with labels.
  Disclaimer "مواقع الأحياء تقريبية وليست حدودا رسمية" + note "«المضاءة» معناها أن التقارير لم تذكرها"
  + credit "Esri, Maxar, Earthstar Geographics · OpenStreetMap" (data-layout-ignore).

OBJECTS: presenter (HeyGen talking photo, waist-up, on #0D1316); the city (satellite); power plant
(building + stacks, mint); very-high-voltage line (lattice pylons + 3 conductors); substation (fenced
yard, transformer with fins and bushings); neighbourhood (block of small houses with windows that light);
two conductors between two crossarms (catenaries that sway); protection relay/breaker (box, lever).

MOTION:
- enter `power3.out` 0.5 s; move `power2.inOut` 0.8–1.2 s; exit `power2.in` 0.3 s; camera `sine.inOut`.
- Map camera: one push from scale 0.85 → 1.0 of the end framing over the whole scene (40 s), anchored at
  the city centre (540, 700).
- A zone switching off: warm glow 0.25 s flicker (2 dips), then the dark blob 0.6 s `power2.out`,
  label 0.35 s `power3.out` from 12 px below. Stagger 1.05 s between zones.
- Captions: group in 0.12 s, hard kill at end.

SHOTS:
1. S1 (avatar full): 0.0 presenter already on screen (frame 0 = face + title). Title «انقطاع الكهرباء
   بالدار البيضاء» at y 190; date line; "16:48" lands (amber, 150 px) on «16:48» in the voice; storm cue:
   wind streaks + one lightning flicker behind the title on «رياح قوية وعواصف رعدية». AI-presenter note.
2. S2 (map, voice only): night city, all 24 zones softly warm; 19 go dark one by one with labels
   (centre outward), the 5 lit ones get labels + glow on «أما المضاءة»; off-frame arrows; legend + notes.
3. S3 (schematic, PiP presenter 30 % width at y 1080–1460): plants → VHV lines → 2 substations (tag
   «حسب Le360») → arrows to neighbourhoods; «ما سمات حتى محطة» note; the incoming line cuts → substation
   dark → houses dark.
4. S4 (avatar small bottom, wires top, chip «فرضية – غير مؤكدة»): conductors sway, touch, spark,
   relay trips, current dashes stop, lights off; other possibilities: lightning, object on line.
5. S5 (avatar small bottom, bullets top): five numbered bullets, one at a time, 76 px, step dots 1–5.
6. S6 (avatar full, chip «فرضية – غير مؤكدة»): question card, three possibilities, «ننتظرو تقرير رسمي».
7. END: sources card.

BANNED: dark void with small floating elements (the map and the presenter fill their frames); neon,
bloom and particles (the lit-zone glow is the user's request, only there); purple/blue gradients;
everything centred and fading up at once; text moving while read; three cards in a row; HUD corners;
invented numbers, names or causes; the reference image's title, legend, numbering or layout.

QA: S1 t=0.2 (hook frame), «16:48» land; S2 mid-cascade + end (every label readable, no collision);
S3 cut moment; S4 touch/spark; S5 bullet 5; S6 possibilities; END; captions never > 2 lines and never
below y 1650; nothing above y 150.
