# SPEC: «منخفض أطلسي: واش دارك وطوموبيلك واجدين؟»

GOAL: a Moroccan viewer asks whether Morocco insures against natural disasters, then learns which provinces are on orange alert, that the next depression (Tuesday to Thursday) covers the north, the centre and Agadir with its surroundings, the eight things to do at home and on the road, what law 110.14 covers, and where to follow the bulletin and whom to call.

OUTPUT: HyperFrames, 1080 × 1920 (9:16), 30 fps, Moroccan Darija text, RTL, silent apart from music, large subtitles burned in.

TIME: 90 s, set by reading time (s1 6.4, s2 13.4, s3 14.0, s4 19.8, s5 24.5, s6 11.9 s). Music: brand bed, 90 BPM (20 frames a beat), D minor, Dm–B♭–F–C.

## Sound and subtitles (user's choices)

- No presenter, no avatar (« لا اريد افاتار »), no voice (« كتب غير الكلام بحال subtitle » → silent video), no footage (« بموسيقى فقط »): drawings, music and subtitles.
- Subtitles are OFF in the current build (script.json "subtitles": false, « الآن بدون subtitles »); the subtitled render stays in livrables. When on: the script text word for word, one line each (≤ 27 characters, ≤ 5 words, lines balanced inside each phrase), Cairo 800 62 px white on a navy chip @86 %, bottom edge at 1590 px (the bottom 15 % = below 1632 px stays clear).
- Timing for reading: each line 0.5 s + 0.25 s a word + 0.03 s a character, scaled so the film is 90 s (about 10 characters a second); scenes follow the text, every visual cue lands while its word is on screen.
- Music only (« بموسيقى فقط »): the brand bed at -16 LUFS is the whole soundtrack; no voice, no sound effects.
- No footage: every picture is drawn (map, skyline under rain, one large line drawing per instruction).

## Look

The user asked for this film's colours (dark navy, white, orange = alert level); the house brand (`brand/BRAND.md`) gives the structure: 60 px hairline grid, cards with 1.5–2.5 px borders and 14 px radius, no shadows, an eyebrow with a 60 × 6 rule, a thin progress bar at the bottom edge.

- ground `#0A1626` + grid `#1B2E48` @55 %; cards `#10233A` / navy @90–95 %; lines `#22395A`.
- text `#FFFFFF`, secondary `#A9B8CC`.
- orange `#FF8A1F` = the alert level and the one thing being said (provinces, active row, the 30 cm fact, the number being read); light orange `#FFBE7D` = the second depression's area. Green `#3CC98F` / red `#F25C54` only for yes / no in s5.
- type: Cairo (OFL, vendored woff2) 900 titles 66–128 px, 800 labels 32–46 px, captions 800 62 px. On-screen captions: 6 words at most.

## Map (must hold in every frame of s2)

- The complete official map of Morocco: Natural Earth "Morocco" ∪ "Western Sahara" drawn as ONE territory with ONE outline and no line inside it; southern provinces down to Lagouira included; neighbours dim, unnamed.
- The map arrives whole (fade + 0.97→1 scale), never drawn in pieces, never cropped, never zoomed past the frame.
- Province fills from geoBoundaries MAR ADM2 (75 provinces) clipped to the outline: Chichaoua, Al Haouz, Taroudant, Essaouira in orange, each on its spoken name with a labelled chip; then the north and centre (the 7 regions Tanger-Tétouan-Al Hoceïma, Oriental, Fès-Meknès, Rabat-Salé-Kénitra, Béni Mellal-Khénifra, Casablanca-Settat, Marrakech-Safi: 54 provinces) sweep in light orange (#FFBA75) from north to south; Agadir and its surroundings join them in the same colour.

## Shots

0. s0 hook (the user's question opens the film, answered in s5): «سؤال» + «واش فالمغرب كاين تأمين» on frame 0, «ضد الكوارث الطبيعية» and «بحال الفيضانات والزلازل؟» on their words, then a flood tile and an earthquake tile.
1. s1: a Moroccan skyline (flat roofs, a minaret) under seeded rain streaks falling with the clock; frame 0 = «منخفض أطلسي» already on screen (150 px, orange edge); «من الثلاثاء حتى الخميس» lands on «الثلاثاء»; a house and a car, each with an orange «؟», land on «دارك» and «وطوموبيلك».
2. s2 map: header «نشرة إنذارية برتقالية» on «نشرة»; four provinces fill on their names; header swaps to «المنخفض الثاني أشمل»; panel (over Algeria/Mauritania, outside the territory) «الثلاثاء ← الخميس»; north + centre sweep on «الشمال»; Agadir and its surroundings (Agadir Ida-Outanane, Inezgane-Aït Melloul, Chtouka-Aït Baha) fill on «اگادير» with the chip «اگادير ونواحيها»; rain / wind / cold icons one per word.
3. s3 home: hero panel (y 350–880) with one drawing per instruction, swapped on its word: house in the rain → drain whose leaves clear and water flows in → pot strapped to the railing in the wind → phone charging + torch beam → meter whose orange breaker drops on «طفّي»; below, four rows land on their verbs, the current row orange.
4. s4 road: hero drawings: car from behind as the water rises + orange no-entry sign → «30 سم = سيارة تطفو» (water rises to the 30 cm mark, the car lifts 16 px and tilts 4°) → crossed-out P, ramp into the underground, flood → key crossed out under drops → umbrella over a dashed line, the wadi flowing; rows for road, parking, engine, children.
5. s5 law 110.14: question card → two branches (insured: contract → compensation → after the Head of Government declares the event catastrophic; not insured: solidarity fund → bodily harm, loss of the main home) → the question to ask your insurer.
6. s6 close on the navy ground: marocmeteo.ma card (hero) with «الموقع الرسمي للأرصاد الجوية - يُحدَّث مرتين في اليوم», then «الوقاية المدنية 15 | الشرطة 19 | الدرك 177» below it, each number orange as it is said, then «شارك الفيديو».

## Banned

Footage of any kind (music-only, drawn film); disaster imagery, victims, people's faces, brands; any map that is cut, cropped or drawn with an inner line; a voice of any kind; text in the bottom 15 %; more than 6 words in an on-screen caption; everything fading in at once; text that moves while it is read; pulsing loops.

## QA frames

0 (hook reads), s2 after the four provinces (labels clear, map whole), s2 after the sweep (light orange north + centre, panel), each s3/s4 row change (hero drawing swapped on the word), the 30 cm card mid-lift, s5 full tree, s5 question, s6 site card, s6 numbers. Then read every subtitle at full speed on a phone: none disappears before it can be read.
