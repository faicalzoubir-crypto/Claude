# SPEC: «شحال غادي يسوى اللتر؟»

GOAL: the viewer understands that a restarted SAMIR would only touch one part of the litre's price
(the purchase share), that the refining margin mostly stays with the refinery, and that taxes and
competition move the pump price more; its real value is energy security.

OUTPUT: HyperFrames, 1080 × 1920, 30 fps, Arabic (RTL), captions burned in.

TIME: set by the voice (Piper ar_JO-kareem, length scale 0.75, tools/voice.py → tools/assemble.py):
98 s. Music: brand bed 90 BPM (20 frames a beat), D minor, Dm–B♭–F–C, two bars a chord, ducked.

LOOK (brand/BRAND.md):
- two worlds. World A, the refinery: footage rendered from the project's own three.js model
  (refinery/samir-3d) at dusk, like the photo of SAMIR; the hook plate is the same view with the plant
  dark (stopped) and then lit. World B, the price: ground #0D1316 + 60 px hairline grid #26343B @55%.
- objects: a fuel dispenser display (steel #1B2327 body, black LCD windows, amber digits with a ghost
  "88.88" @8%, green "SANS PLOMB" strip #2E9E5B as on real pumps); a 1 L graduated cylinder (glass:
  1.5 px #E8EEEC @35% outline, ticks every 0.25 L); a steel oil drum (#5E7480, two ribs); barrel bars.
- colours: amber #F4A62A = the purchase share and every answer number (one amber thing per beat);
  taxes #4A5E66; margins mint #93CDBB; stream colours as in the model (crude #C98B5A, gas #6FB6E8,
  gasoline #F5D65B, kero #B99CF0, diesel #93CDBB, sulfur #C6E04A).
- type: IBM Plex Sans Arabic 600/700 (eyebrow 30 px amber with 60×4 rule, titles 64–68 px, chips
  34–40 px, captions 46 px on a 72% ground chip); numbers in Space Grotesk 700.
- layout: nothing in the top 168 px; header at 196 px; every word above 1190 px; captions 1206–1320 px;
  a 5 px amber progress bar on the bottom edge.

MOTION: arrivals expo.out 0.45 s; words blur-in 0.13 s, 0.067 s apart; exits blur-out 0.18 s; counters
power2.out; chips on the 3D footage follow projected anchors frame by frame (footage-anchors.js).

SHOTS (cue = narration phrase):
1. s1 hook: frame 0 = dark refinery plate + pump display + title. Counter 0 → 13.95 DH / 1.00 L on
   s1p1; chip on the stack on «لاسامير»; the plant lights up on «لو عادت».
2. s2 the litre: cylinder fills on s2p1; strata amber 46% (6.42), steel 38% (5.30), mint 16% (2.23) on
   s2p2–p4; on s2p5 the other two dim and the purchase share gets the bracket.
3. s3 tanker footage: chip «نفط خام» rides the tanker; drum + 159 count on s3p2.
4. s4 tour footage: furnace chip + 360 °C count; column chip; four product chips with boiling ranges on
   their names; then conversion and sulfur chips.
5. s5 margin: crude bar vs gasoline bar, the gap amber on «هامش»; ≈ 1.20 DH/L (example 20 $/bbl ÷ 159);
   energy / wages / maintenance bite the gap in three steps.
6. s6 who keeps it: two pump prices, both 13.95; the margin goes to «ربح المصفاة»; «تخفيض» struck.
7. s7 answer over the wide dusk footage: −0.5 → −2 DH (estimate), taxes ≈ 38% and competition, energy
   security; closing line and sources.

SOUND: brand bed ducked under the voice; ticks on the pump counter and the cost steps, a click when the
pump stops, pops when parts and chips land, rotated whooshes on scene cuts. No chimes.

BANNED: invented numbers (barrel prices, refinery costs); a narrator line repeated as the title; glow
rings; text below 1190 px other than captions; everything appearing at once; labels cut at the edge.

QA frames: 0 (hook reads), s1 lights on, s2 three strata labelled, s2 bracket, s3 drum 159, s4 furnace
360, s4 four products, s4 conversion, s5 gap + 1.20, s5 after the bites, s6 equal prices, s7 answer,
last frame.
