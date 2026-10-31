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

Safe zone (user's): no text in the top 250 px or bottom 400 px, 80 px sides. Cards sit at 300 px (top) or in the middle of 250–1520 (scene 5). Monogram bottom-left at 80,1400 (120 px, 70%), clear of the right-hand action rail.

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
- google_earth: the user sent a Google Earth app screenshot (`assets/images/google_earth.jpg`, 1186×2576) and marked the sign (« مكان علامة التشوير », confirmed « نقطة بيضاء ») with the white dot at the roundabout's north-east exit (563, 1419). Placed at ×1.047, top −66 so the app buttons fall outside the frame; « © Google Earth » credit beside the monogram (the screenshot has no attribution of its own). Used in scene 3 (zoom out from the sign, route to the interchange) and scene 6 (slow push-in).
- Close-up of the sign: the user sent a ×4 Google Earth view with a sketch (circle on the sign, arrow north along the right-hand carriageway) and « زووم على مكان علامة التشوير ثم اتجاه الطريقة المقصودة بالكلام ». `tools/prep_ge_zoom.py` removes the sketch (inpaint) → `assets/images/google_earth_zoom.jpg`, and aligns it on the wide view (SIFT, ×0.2434, no rotation; the sketched circle lands on the white dot) → `tools/ge_zoom_align.json`. Scene 3 opens on it: ring on the sign, clay arrow north as sketched, then a continuous zoom-out (log-even, 1.6 s) dissolving into the wide view, route to the interchange (along the sketched carriageway), exits.
- Police stop and route (user: « مكان توقف الشرطة ثم اتجاه الحركة من زاويتين »): four Google Earth views of the interchange — two top views with a ✕ (the two ✕ sit about 60 m apart on the loop's entry ramp; the second one is used), the riders' route sketched on the top view and on a 3D view. Route: N1 north under the bridge → loop on the right → out onto the avenue into the city. This confirms the exits on the scene 3 map: blue = city centre (loop, road to the left), red = highway (straight on). `tools/prep_police.py` rebuilds clean images (the two top views share one screenshot; the 3D sketch is inpainted, the app buttons cloned out) → `assets/images/police_top.jpg`, `police_3d.jpg`, `tools/police_geo.json`.
- Routes in scenes 4–5 re-traced on the lanes (user: « Create a similar road like this one and dont follow my line exactlily, make in the road like this », with their Google Maps and Apple Maps routes): N1 eastbound under the Route Al Jamiaa / Rte d'El Jadida bridge → exit lane along the top of the loop → clockwise round the ring → Route Al Jamiaa northbound (figure of eight). Top view: N1 northbound carriageway, then the loop's entry ramp to the ✕.
- Scene 4: fork_a (2 s), then the 3D view (3 s): route with their Vespa seen from above (user: « show from up a little motorcycle like mine riding that way », with a still of the slide film's map) — the slide film's top-down Vespa (mint #93CDBB, dark seat, headlight), laid on the ground (squash 0.5), turned along the route, shrinking towards the avenue; push-in ×1.10; card at 64 px (3 lines).
- Scene 5 (no police footage): the top view, push-in on the hit, route up to the ✕, the same top-down Vespa stopped just short of a stop badge with red/blue lights flashing 4× a second; quote card centred above it.
- Ride clips (user: « و كذلك مكان تفرع الطريقين واحد باتجاه وسط المدينة و آخر باتجاه الطريق السيار »): three 360-camera clips from the Vespa, Casablanca, kept as `assets/footage/source/fork_a|b|c.mov`. `tools/prep_footage.py` makes H.264 30 fps silent copies (`assets/footage/*.mp4`, git-ignored: rerun the script in a fresh session before previewing or rendering) and the sign still.
  - fork_b: out of the roundabout behind the Vespa, then past the moped / pedestrian ban signs (≈5–6.8 s), then the N1 north.
  - fork_a: under the bridge, then the fork's direction sign « الرباط RABAT ↙ / وسط الدار البيضاء CASABLANCA CENTRE ↘ » (8.4–9.6 s), then the right-hand exit to the city centre.
  - fork_c: the highway branch (green autoroute signs) — not used yet.
- Footage in use: s1 + s7 sign still (fork_b 6.55 s, distant car and walker blurred; zoom 1.25 → 1.33 at one rate across s7 → s1, measured seamless: last vs first frame differ by ~1/255); s2 fork_b 2.0–7.0; s4 fork_a 7.2–9.6 (sign stays under the card) then the 3D route; s6c fork_b 7.2–10.2; s6d fork_a 10.4–13.4. No readable plate or face in these spans.
- Waiting for: fz_monogram.png and the music (track or route: HeyGen sign-in / local generation). Optional: a real static sign_closeup, a third-person vespa_ride, police footage. A footage slot becomes a `<video>` once `assets/footage/<slot>.mp4` exists (rerun `python3 tools/build.py`).

## To do once the footage is in

- Blur every face and plate (the user's Vespa included) with `npx hyperframes media-treatment`, not CSS.
- Loop: scene 7 takes the sign_closeup span just before scene 1's, so the cut back to 0 continues the same shot.
- Music: tense build (1–4), hit at 20.0 s, lighter in 6, hard cut on a beat at 39.0 s, no fade.
