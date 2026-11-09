# SPEC: «منخفض أطلسي: واش دارك وطوموبيلك واجدين؟»

GOAL: a Moroccan viewer knows which provinces are on orange alert, that the next depression (Tuesday to Wednesday) covers the north and the centre, the eight things to do at home and on the road, what law 110.14 covers, and where to follow the bulletin and whom to call.

OUTPUT: HyperFrames, 1080 × 1920 (9:16), 30 fps, Moroccan Darija, RTL, large subtitles burned in.

TIME: the user's own recording is the clock (about 90 s). Until it exists, `script.json` ranges give an estimate (s1 0–5, s2 5–18, s3 18–40, s4 40–58, s5 58–78, s6 78–90). Music: brand bed, 90 BPM (20 frames a beat), D minor, Dm–B♭–F–C.

## Voice (user's rules)

- No presenter and no avatar (the user said «لا اريد افاتار»): graphics, b-roll and the user's voice only.
- The voice is the user's recording, used exactly as recorded: `assets/voice/voice.<ext>`, no denoise, no EQ, no pitch, no loudness change, `data-volume="1"`. Nothing in this project generates, clones or replaces a voice.
- Subtitles: the words as spoken, word for word (`tools/align.py` → `assets/voice/words.json`, report checked), groups of up to 5 words / 27 characters, one line, Cairo 800 62 px white on a navy chip @86 %, bottom edge at 1590 px (the bottom 15 % = below 1632 px stays clear).
- Music very low: bed at -24 LUFS × 0.32 (≈ -34 LUFS) under a voice around -16 LUFS.

## Look

The user asked for this film's colours (dark navy, white, orange = alert level); the house brand (`brand/BRAND.md`) gives the structure: 60 px hairline grid, cards with 1.5–2.5 px borders and 14 px radius, no shadows, an eyebrow with a 60 × 6 rule, a thin progress bar at the bottom edge.

- ground `#0A1626` + grid `#1B2E48` @55 %; cards `#10233A` / navy @90–95 %; lines `#22395A`.
- text `#FFFFFF`, secondary `#A9B8CC`.
- orange `#FF8A1F` = the alert level and the one thing being said (provinces, active row, the 30 cm fact, the number being read); light orange `#FFBE7D` = the second depression's area. Green `#3CC98F` / red `#F25C54` only for yes / no in s5.
- type: Cairo (OFL, vendored woff2) 900 titles 66–128 px, 800 labels 32–46 px, captions 800 62 px. On-screen captions: 6 words at most.

## Map (must hold in every frame of s2)

- The complete official map of Morocco: Natural Earth "Morocco" ∪ "Western Sahara" drawn as ONE territory with ONE outline and no line inside it; southern provinces down to Lagouira included; neighbours dim, unnamed.
- The map arrives whole (fade + 0.97→1 scale), never drawn in pieces, never cropped, never zoomed past the frame.
- Province fills from geoBoundaries MAR ADM2 (75 provinces) clipped to the outline: Chichaoua, Al Haouz, Taroudant, Essaouira in orange, each on its spoken name with a labelled chip; then the north and centre (the 7 regions Tanger-Tétouan-Al Hoceïma, Oriental, Fès-Meknès, Rabat-Salé-Kénitra, Béni Mellal-Khénifra, Casablanca-Settat, Marrakech-Safi: 54 provinces) sweep in light orange from north to south.

## Shots

1. s1 hook: storm-over-the-city b-roll under a navy scrim; frame 0 = «منخفض أطلسي» already on screen (150 px, orange edge); «جاي بين الثلاثاء والأربعاء» lands on «الثلاثاء»; a house and a car, each with an orange «؟», land on «دارك» and «وطوموبيلك».
2. s2 map: header «نشرة إنذارية برتقالية» on «نشرة»; four provinces fill on their names; header swaps to «المنخفض الثاني أشمل»; panel (over Algeria/Mauritania, outside the territory) «الثلاثاء ← الأربعاء»; north + centre sweep on «الشمال»; rain / wind / cold icons one per word.
3. s3 home: b-roll cut on each instruction (rainy street → drain → balcony/roof → phone + torch → meter panel); four rows land on their verbs, the current row orange; «دخل الما؟ طفّي العداد» on «طفّي».
4. s4 road: b-roll (flooded road → underground car park → car in water → children with umbrellas near a school); card «30 سم = سيارة تطفو»: water rises to the 30 cm mark, the car lifts 16 px and tilts 4°; rows for parking, engine, children.
5. s5 law 110.14: question card → two branches (insured: contract → compensation → after the Head of Government declares the event catastrophic; not insured: solidarity fund → bodily harm, loss of the main home) → the question to ask your insurer.
6. s6 close on the navy ground: marocmeteo.ma card (hero) with «الموقع الرسمي للأرصاد الجوية - يُحدَّث مرتين في اليوم», then «الوقاية المدنية 15 | الشرطة 19 | الدرك 177» below it, each number orange as it is said, then «شارك الفيديو».

## B-roll to generate (9:16, 8–10 s each, no people's faces, no brands or readable signs, no victims, no disaster footage)

| File | Shot |
| --- | --- |
| b0-storm-city | dark storm clouds over a Moroccan city skyline (white houses, a minaret far off), rain starting, slow push |
| b1-rain-street | a Moroccan city street in steady rain, wet asphalt, whitewashed walls, slow push |
| b2-drain | a street drain clogged with leaves and plastic, rainwater pooling around it, close up |
| b3-balcony | a Moroccan rooftop terrace / balcony in rain and wind, plant pots and a chair by the railing |
| b4-phone-torch | a smartphone charging on a table next to a flashlight, rain on the window behind |
| b5-meter | a home electricity meter and breaker panel on a wall, a hand-free shot, rain light |
| b6-flooded-road | a car driving slowly into a flooded road, water up to the wheels, seen from behind |
| b7-parking | an empty underground car park with water on the floor near the ramp |
| b8-car-water | a parked car standing in water up to the bumper on a street, rain |
| b9-school | children seen from behind with umbrellas walking near a school gate, rain, faces not visible |

## Banned

Disaster footage, victims, identifiable faces in b-roll, brands and readable plates/signs; any map that is cut, cropped or drawn with an inner line; a generated or altered voice; text in the bottom 15 %; more than 6 words in an on-screen caption; everything fading in at once; text that moves while it is read; pulsing loops.

## QA frames

0 (hook reads), s2 after the four provinces (labels clear, map whole), s2 after the sweep (light orange north + centre, panel), each s3/s4 row change (b-roll cut on the word), the 30 cm card mid-lift, s5 full tree, s5 question, s6 site card, s6 numbers. Then the subtitles against the voice at the start, the middle and the end.
