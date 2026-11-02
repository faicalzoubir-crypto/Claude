# SPEC: «بعد 35 سنة… المينورسو تغادر»

GOAL: the viewer understands that MINURSO's mandate ended (31 Oct 2026), sees the buffer zone east of the
berm, and weighs three possible scenarios (labelled "possible"), then answers the closing question.

OUTPUT: HyperFrames, 1080 × 1920, 30 fps, Arabic (RTL), captions burned in.

TIME: set by the voice (tools/voice.py → tools/assemble.py). Estimate without voice: 97 s. Music 90 BPM
(20 frames a beat), D minor, Dm–B♭–F–C, two bars a chord.

LOOK (brand/BRAND.md, approved in preview-*.png):
- ground #0D1316; a 60-unit hairline grid #26343B @55% drawn ON the tilted map plane, faded at its edges.
- map: dark 3D; plane tilted 27–33°, Morocco (whole territory) #213130 top face + 10-unit extrusion
  #2B4540, mint outline #93CDBB 2 + 5-blur glow @45%, relief noise @22% screen.
- buffer zone: amber #F4A62A @18% + 45° hatch 1.5/10 + 1.5 edge; the one amber thing while it is the subject.
- berm: #E8EEEC 3 + 6-unit ticks on the zone side every 14 units. MINURSO sites: UN blue #009EDB (real colour).
- forces/tanks: mint; threats: #F25C54; neighbours #141D21 / #26343B; names #6E8186, cities #93A4A7.
- type: IBM Plex Sans Arabic 600/700 (titles 68 px, eyebrow 30 px amber with 60×4 rule, cards 36–46 px,
  map chips 30 px, captions 46 px on a 72% ground chip); numbers in Space Grotesk 700.
- layout (vertical safe band): nothing in the top 168 px; header at 196 px; every word above 1190 px;
  captions at 1206–1320 px; below that only the map floor and the 5 px amber progress bar.

OBJECTS: the map itself (real Natural Earth borders; berm = Natural Earth's edge between "Morocco" and
"W. Sahara", approximate); 5 MINURSO team sites east of the berm (Wikipedia coordinates); tanks drawn
top-down (tracks, hull, turret, barrel) so they read without a label; marchers as two rows of mint dots.

MOTION:
- camera: one pure function of t (map.html `camAt`), moves 1.4–2.0 s `power2.inOut`, ±3 px drift.
- arrivals `expo.out` 0.45 s / words blur-in 0.13 s, 0.067 s apart; exits blur-out 0.18 s.
- berm draws north→south 2.2 s; sites switch off 0.38 s apart; tanks 3.6 s `power2.inOut`, 0.15 s
  stagger; the wall dissolves north→south over 3.2 s into 240 sand grains blown east.

SHOTS (cue = narration phrase):
1. s1 hook: frame 0 = title + whole map + amber zone. Years 1991→2026 on «خمس وثلاثين». Push to the zone on
   s1p2, zone glows on «المنطقة», berm draws on «الجدار» with ≈2,700 km.
2. s2 facts: map dims; timeline 31 Oct / 1 Nov / 6 Nov. Map returns, sites close-up, sites go dark one by
   one; card "Morocco cooperates".
3. s3 scenario 1: 1975 card (350,000 count-up) then 2026 card (51 years). Map returns, marchers cross the wall.
4. s4 scenario 2: tanks roll from the wall to the border, the wall dissolves to sand, the zone becomes
   national ground, the border lights amber; Guerguerat chip (Nov 2020).
5. s5 reactions then scenario 3: statement cards; header swaps; red threats approach from the east;
   the border becomes a mint shield, threats pull back (the film's one low hit).
6. s6 recap: pull back to the whole map, dimmed; 3 scenarios list; the question (amber «الأقرب»); sources.

SOUND: brand synth bed ducked under the voice; effects only on visible actions: whooshes on camera moves
(3 takes), clicks on cards, ticks on sites going dark, rumble for tanks, sand for the wall, blips for
threats, one low hit on the shield.

BANNED: quotes attributed to the 6 Nov speech; fabricated numbers; explosions, fire, smoke; a narrator
line repeated as a big on-screen sentence; pulsing loops; everything fading in at once; text below 1190 px
other than captions; labels cut at the frame edge.

QA frames: 0 (hook reads), berm draw (north→south), sites off, 1975/2026 cards, march, tanks mid-way,
wall gone + amber border, threats + shield, recap + question.
