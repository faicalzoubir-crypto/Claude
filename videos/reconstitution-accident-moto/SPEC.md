# SPEC — Reconstitution d'accident (simulation)

```text
GOAL:    the viewer understands, calmly and without shock, how a sudden stop led to a light contact and a fall,
         and never mistakes it for real footage.
OUTPUT:  HyperFrames, 1080 x 1920, 30 fps
TIME:    37 s x 30 = 1110 frames. Music 90 BPM (20 frames per beat), D minor, soft, no drums.
LOOK:    a top-down forensic animation over an aerial plate in evening light:
         - plate: dirt lots #a68a62 with 5 cm grain, asphalt #45474a, white lane paint, light concrete curbs,
           median soil with round tree canopies, tree and building shadows thrown 2-3 m to the east;
           warm multiply grade (evening). The city (beige / white roofs) is seen only in the dive.
         - one world in metres (assets/kinematics.js): every shot is the same road, same lanes, same median.
         - vehicles drawn as real objects seen from above: scooter in mint #93CDBB (brand object colour),
           BMW S1000 XR in red #c4161c / silver / black with gold forks; riders with helmets, dark jacket for B.
         - chrome = brand: cards #141D21 at 92 %, 1.5 px #26343B border, 14 px radius; amber #F4A62A = the one
           highlight (step number, impact point, 20 m measure); text #E8EEEC / #93A4A7.
         - type: Cairo 800 titles, Cairo 700 labels, all Arabic RTL, nothing under 28 px.
OBJECTS: scooter A (leg shield, floorboard, seat, rack, helmeted rider in a blue-grey jacket);
         BMW B (beak, smoked screen, wide bars with hand guards, mirrors, exhaust on the right, gold forks);
         rider B lying = schematic body, no injury shown; tyre marks (dark), scrape marks (light);
         impact = amber ring at the scooter's left-rear corner.
MOTION:  camera eases power2.inOut on log(scale); dive 0 → 2.95 s (0.42 → 24 px/m);
         follow 3 → 9 s (24 → 50 px/m); push to 190 px/m at 10.8 → 11.25 s; pull to 62 px/m at 11.95 → 12.9 s;
         overview 15 → 16.6 s (23 px/m). Action at ×0.5, slow motion ×0.1 from 11.1 to 11.9 s (ramps 0.3 s).
         Labels: blur 8 → 0 px + opacity in 0.25 s power3.out; out 0.15 s.
SHOTS:   0-3     dive from the city to the boulevard; title card (frame 0 already titled)
         3-7     both bikes in the left lane by the median curb; tags A ~35 km/h, B ~55 km/h; 20 m measure at 6-7.7
         7-9     scooter brakes to a stop (speed tag falls to 0)
         9-11    BMW brakes (tyre marks) and moves 0.65 m left into the gap; camera pushes in
         11-12   slow motion ×0.1: right hand guard brushes the scooter's left-rear; amber ring; scooter stays up
         12-15   BMW wobbles, falls to its left, slides ~8 m; rider thrown onto the median curb behind it
         15-20   pull up: ghosts at the sudden-stop positions, dotted paths, distances, rest positions labelled
         20-32   legal card: article 6, decree 2.10.420 (quoted), key passage highlighted
         32-37   summary card on the brand ground
BANNED:  blood, injury detail, real-footage look, extra vehicles, glow / bloom, three cards in a row,
         text moving while read, everything centred, a dark void with floating elements.
QA:      t = 0, 2.5, 4, 6.8, 8.5, 10.2, 11.5, 13.5, 15, 18, 22.5 — road geometry identical, labels readable at 360 px,
         nothing to read below y = 1330 or above y = 168.
```

Numbers (from `assets/kinematics.js`, printed by `node tools/verifier.mjs`): scooter braking 7.5 m/s², stops in
6.3 m; BMW rider reaction 1.0 s, braking ≈ 7.2 m/s² (0.74 g), contact at ≈ 28 km/h; BMW slides ≈ 8 m on its side;
rider ends ≈ 5 m from the contact point, on the median curb, behind the BMW. All values are illustrative estimates.
