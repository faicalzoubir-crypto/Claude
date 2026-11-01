---
workflow: hyperframes
flow: automation
message: "Le panneau « pas de cyclomoteurs < 50cc » sur la N1 : l'interdiction commence au panneau, pas à l'entrée de l'autoroute ; la police ne fait qu'appliquer."
destination: instagram-reels / tiktok
aspect: 1080x1920
fps: 30
language: ar (darija, écriture arabe, RTL)
length: 39s
loop: seamless (last shot = first shot)
---

## Intent

Vertical Reel, music + on-screen text only (no voice, no avatar). Copy in Moroccan Darija, used exactly as the user wrote it; line breaks and keep-together groups are layout only.

Look set by the user for this film (it replaces `brand/BRAND.md` here): Cairo ExtraBold, ivory `#FAF9F5` on `#141413` at 70%, `**highlights**` in clay `#D97757`, 0.2 s pop-in, about 1 s per 4 words and at least 2 s per card. Shapes and arrows, no emoji. Map arrows: red = highway (forbidden), blue = city centre.

Safe zone (user's): no text in the top 250 px or bottom 400 px, 80 px sides. Cards sit at 300 px (top) or in the middle of 250–1520 (scene 5). No monogram (user: « Dont put a monogram »); the « © Google Earth » credit sits bottom-left at 80, 1478 on the Google Earth shots.

## Scenes (tools/build.py → SCENES)

1. 0–3 sign_closeup · « quote » (on screen from frame 0: thumbnail + loop landing)
2. 3–8 vespa_ride 2.5 s → road_pov · sign forbids **< 50cc**
3. 8–15 google_earth · zoom out from the sign, clay line + scooter to the fork, red/blue exits with labels
4. 15–20 fork · ban starts **at the sign**
5. 20–25 police_stop · music hit, push-in, quote centred
6. 25–37 four cards: google_earth ×2, road_pov, vespa_stop
7. 37–39 sign_closeup, same framing as 1 · « ودابا ما يمكنش تقول… » → hard cut to 0

## Status

- Text, timing and map motion built on labelled stand-ins; Arabic checked on stills (shaping, RTL, « », 50cc, ellipsis).
- google_earth: the user sent a Google Earth app screenshot (`assets/images/google_earth.jpg`, 1186×2576) and marked the sign (« مكان علامة التشوير », confirmed « نقطة بيضاء ») with the white dot at the roundabout's north-east exit (563, 1419). Placed at ×1.047, top −66 so the app buttons fall outside the frame; « © Google Earth » credit bottom-left (the screenshot has no attribution of its own). Used in scene 3 (zoom out from the sign, route to the interchange) and scene 6 (slow push-in).
- Close-up of the sign: the user sent a ×4 Google Earth view with a sketch (circle on the sign, arrow north along the right-hand carriageway) and « زووم على مكان علامة التشوير ثم اتجاه الطريقة المقصودة بالكلام ». `tools/prep_ge_zoom.py` removes the sketch (inpaint) → `assets/images/google_earth_zoom.jpg`, and aligns it on the wide view (SIFT, ×0.2434, no rotation; the sketched circle lands on the white dot) → `tools/ge_zoom_align.json`. Scene 3 opens on it: ring on the sign (confirmed again by the user: « The place of the sign is here from the beginning of the white line »), clay arrow north on the middle of the lane (not on the hand line, which runs along the road's edge), then a continuous zoom-out (log-even, 1.6 s) dissolving into the wide view, route to the interchange (along the sketched carriageway), exits.
- Police stop and route (user: « مكان توقف الشرطة ثم اتجاه الحركة من زاويتين »): four Google Earth views of the interchange — two top views with a ✕ (the two ✕ sit about 60 m apart on the loop's entry ramp; the second one is used), the riders' route sketched on the top view and on a 3D view. Route: N1 north under the bridge → loop on the right → out onto the avenue into the city. This confirms the exits on the scene 3 map: blue = city centre (loop, road to the left), red = highway (straight on). `tools/prep_police.py` rebuilds clean images (the two top views share one screenshot; the 3D sketch is inpainted, the app buttons cloned out) → `assets/images/police_top.jpg`, `police_3d.jpg`, `tools/police_geo.json`.
- Routes in scenes 4–5 re-traced on the lanes (user: « Create a similar road like this one and dont follow my line exactlily, make in the road like this », with their Google Maps and Apple Maps routes): N1 eastbound under the Route Al Jamiaa / Rte d'El Jadida bridge → exit lane along the top of the loop → clockwise round the ring → Route Al Jamiaa northbound (figure of eight). Top view: N1 northbound carriageway, then the loop's entry ramp to the ✕.
- Scene 4: fork_a (2 s), then the 3D view (3 s): route with their Vespa seen from above (user: « show from up a little motorcycle like mine riding that way », with a still of the slide film's map) — the slide film's top-down Vespa (mint #93CDBB, dark seat, headlight), laid on the ground (squash 0.5), turned along the route, shrinking towards the avenue; push-in ×1.10; card at 64 px (3 lines).
- Scene 5 (no police footage): the top view, push-in on the hit, route up to the ✕, the same top-down Vespa stopped just short of a stop badge with red/blue lights flashing 4× a second; quote card centred above it.
- Ride clips (user: « و كذلك مكان تفرع الطريقين واحد باتجاه وسط المدينة و آخر باتجاه الطريق السيار »): three 360-camera clips from the Vespa, Casablanca, kept as `assets/footage/source/fork_a|b|c.mov`. `tools/prep_footage.py` makes H.264 30 fps silent copies (`assets/footage/*.mp4`, git-ignored: rerun the script in a fresh session before previewing or rendering) and the sign still.
  - fork_b: out of the roundabout behind the Vespa, then past the moped / pedestrian ban signs (≈5–6.8 s), then the N1 north.
  - fork_a: under the bridge, then the fork's direction sign « الرباط RABAT ↙ / وسط الدار البيضاء CASABLANCA CENTRE ↘ » (8.4–9.6 s), then the right-hand exit to the city centre.
  - fork_c: the highway branch (green autoroute signs) — not used yet.
- Footage in use: s7 fork_b 4.6 → 6.567 s (rolling up to the signs, ends on frame 197); s1 opens on that same frame paused (`assets/images/sign_still.png`, PNG so the pixels match: last vs first frame differ by 0.0); s2 fork_b 2.0–7.0; s4 fork_a 7.6–9.6 then the 3D route; s6c fork_b 7.2–10.2; s6d fork_a 10.4–13.4. No readable plate or face in these spans (the car and walker behind the sign are a few pixels tall and stay as filmed).
- Sign close-up from the user (« And this is the sign if you want to use it »): `assets/images/source/sign_closeup_user.jpg` is an 8× enlargement (~75 px of real detail across the sign). At their request (« Creat a the same sign to use it, learn from the given one because its resolution is bad ») it is redrawn as a vector, `assets/images/sign_moped.svg`: red #E43223 (measured on their photo). The user then sent a clean render of the sign (« Here is it », `assets/images/source/sign_reference.jpg`): the pictogram is traced on it in the same 600-unit frame (mudguards, Z handlebar, engine, seat on its post, rear rack, swingarm and hubs; ring inner/outer 0.705) and checked overlaid; drawn flat, without the render's gloss, rim and reflection, so it sits on the real pole and on the map. Used as the map marker in scene 3 (close-up r 52, wide view r 36) and in scene 1 (user: « keep my fotage video pause fore a while and then show the sign given zoomed from the original in the video »): after a 0.8 s pause on the real frame, it grows out of the real sign (140 px at 602, 896 → 450 px), covering the « no pedestrians » sign under it.
- Music (user: « generate the music here »): `tools/music.py` synthesises it in code (no samples, no vocals, royalty-free): 120 BPM, D minor. 0–20 s pulse bass with its filter opening, sixteenth ticks, a plucked D F A G# motif every other bar, heartbeat from 8 s, riser and snare roll from 15 s, a breath at 19.75 s; the hit at 20.0 s (sub boom, crack, D minor stab) and a four-on-the-floor drop to 25 s; 25–37 s lighter, Bb–F–C–Dm–Bb–A with arpeggios; the tension texture returns at 37 s and runs into the start. Rendered as a loop (tails folded onto the start, drone on loop-locked frequencies, filter and limiter wrapped), hard cut at 39.0 s on a beat; -14 LUFS, peak -1 dBFS. `assets/music/track.wav`.
- Plain version (user: « Give me another video without writing without music »): `livrables/panneau-n1-50cc-sans-texte-sans-musique.mp4`, same pictures and timing, no cards, no map labels, no music (silent AAC track added for editing apps); the « © Google Earth » credit stays. Build with `HF_VARIANT=plain python3 tools/build.py`, render, then rerun `python3 tools/build.py` to restore the main version.
- Final: `livrables/panneau-n1-50cc.mp4` (render: `npx hyperframes render -o livrables/panneau-n1-50cc.mp4 --quality delivery`). In a fresh session, run `python3 -I tools/prep_footage.py` first (the transcoded clips are git-ignored).

- Riders' route (user: « make it with a green line and make the motocycle from above looks like riding the right way like the green on not the orange one »): route lines green #33D17A in scenes 3, 4, 5 (and the close-up arrow), and the top-down Vespa, nose first, in all three (scene 3 at 72 px, top view) instead of the clay side-view scooter.

