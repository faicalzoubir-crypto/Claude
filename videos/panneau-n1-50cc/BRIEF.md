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
- Waiting for the user's files: sign_closeup, road_pov, vespa_ride, vespa_stop, google_earth, fork, police_stop, fz_monogram.png, music. A footage slot becomes a `<video>` once `assets/footage/<slot>.mp4` exists (rerun `python3 tools/build.py`).

## To do once the footage is in

- Blur every face and plate (the user's Vespa included) with `npx hyperframes media-treatment`, not CSS.
- Loop: scene 7 takes the sign_closeup span just before scene 1's, so the cut back to 0 continues the same shot.
- Re-locate the map points (sign, fork, exits) on the real Google Earth image; keep its attribution in frame.
- Music: tense build (1–4), hit at 20.0 s, lighter in 6, hard cut on a beat at 39.0 s, no fade.
