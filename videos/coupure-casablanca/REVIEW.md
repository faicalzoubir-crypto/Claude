# REVIEW — coupure-casablanca (reoriented: the grid, two official accounts, the outage length)

## Reorientation (13 Nov, from the person's sources)
- Asked: "refute the wind theory" and "contradict the spokesperson". Not done as asked: the person's own
  sources say ONEE also blames the storm (4 × 225 kV lines at once, via Le360) and both substations sit on
  the SAME 225 kV artery. Agreed instead: show what the sources support, attributed, with every inference
  tagged. Nothing on screen says the wind is false or that anyone lied.
- S3: the artery Mediouna (N) ↔ Ouled Haddou ↔ Dar Bouazza ↔ Ouled Salah ↔ Laaouamer (S), fed from two
  directions, Jorf Lasfar and Safi (via Chemaia) behind it; caveat on screen: ONEE documents 2016–2022,
  current layout not confirmed. The pasted text's "one generator feeds both" contradicts its own later
  note ("no generator dedicated to these substations") and was not used.
- S4: spokesperson 3 cables vs ONEE (via Le360) 4 × 225 kV lines → «3 ≠ 4»; the communiqué named no line.
- S5: "fed from two sides, how did both go dark?" → official answer (4 lines at once, shown as four abstract
  cuts, never placed on named segments) + the planned Laaouamer–Ouled Haddou line (225 kV double, 32 km,
  ONEE tender 2020), still late after Cegelec and Medicable withdrew (Maroc Diplomatique, LesEco).
- S6: 3 h (spokesperson, as the person relayed it) vs 23:00 in the person's own neighbourhood (6 h 12 min
  after 16:48), tagged «شهادة»; worded "in at least one neighbourhood", never generalised.
- S7 = the five measures (unchanged), S8 = four open questions + «ننتظرو تقرير تقني مفصل»,
  sources card grouped (official / technical / press / testimony). Film 3:07.

# REVIEW — coupure-casablanca (subtitle version, short cut, official cause)

## Official cause (the person, 12 Nov: the government spokesperson's statement, as they relayed it)
- Cause given: strong winds and weather disturbances; the wind brought down three high-voltage cables,
  the main cable of the network among them (spokesperson + SRM). Name «سمير بلفقيه» used as the person wrote it.
- S4 is now «تصريح رسمي»: three cables gallop, snap off the right-hand tower (spark each), fall to the
  ground, the main one turns amber with «الكابل الرئيسي», the houses go dark. The hypotheses (wires
  touching, lightning, a conductive object) are gone: the official cause replaces them.
- S6 keeps the question, answers with the statement (the main cable was among those that fell), and waits
  for the full technical report. Sources card: + «تصريح الناطق الرسمي باسم الحكومة».


## Short cut (the person: «ثقيل بزاف… يكون أقصر… الأحياء سرّعهم»)
- No padding to the 3–4 min brief any more: scenes last their reading time (S1 17 s, S2 17, S3 30, S4 22,
  S5 25, S6 20, end card 5) → 2:16 instead of 3:38.
- Lines: 0.45 s + 0.30 s a word + 0.01 s a character (was 0.6 / 0.34 / 0.012); 0.2–0.35 s between lines.
- Map: one zone every 0.45 s (was 1.18 s), the switch-off flicker played at 0.55×, labels in 0.28 s;
  the five lit zones every 0.35 s; the whole map scene 17 s instead of 38 s.


## Creative calls
- **No presenter, no voice.** HeyGen avatars and voices need a paid HyperFrames Pro plan on the account;
  the person chose their own voice, then asked to "write it as subtitles". The narration is read on
  screen: burned-in Arabic subtitles (IBM Plex Sans Arabic 700, 58 px, ≤ 2 lines, bottom edge y 1650),
  each line held 0.6 s + 0.34 s a word + 0.012 s a character (`tools/subtitles.py`); SRT alongside.
- Avatar scenes rebuilt as full-frame drawings: S1 a lattice tower in the storm above a city whose
  windows go out; S4 two conductors galloping until they touch, breaker, houses going dark; S5 one bullet
  at a time growing a list; S6 question + three possibility cards + «ننتظرو تقرير رسمي».
- Map: real Esri World Imagery graded to night (media-treatment), points from OpenStreetMap Nominatim
  (curated; several differ from the reference image, e.g. Sbata south-east, Californie south), labels
  hand-placed with leader lines in the dense centre. Lit zones keep the warm glow; dark ones flicker off.
- Scene 5 narration lines (one per bullet + intro) were written for this film; the bullets themselves
  are the person's.
- Brand: #0D1316 ground + faint 60 px grid, amber = the one highlight (16:48, the hypothesis chip, the
  active step, power flow), mint = drawn objects, red only for the fault. No progress bar: the bottom
  250 px is reserved for app UI.

## Measured vs looked at
- `npx hyperframes check`: ok (1 warning kept: the generated map file is long).
- `snapshot --review` beats, seams and the 360 px phone sheet looked at; P0 fixed: S3 drop lines floated
  before their plants/substations existed (now revealed with them).
- Sound: brand bed (90 BPM, D minor) + bundled SFX (clicks per zone switching off, pop per lit zone,
  spark + bass hit at the touch, breaker click, whooshes on cuts). Measured, not heard: the render was
  −17.7 LUFS; the delivery file is normalised to −14.0 LUFS integrated, true peak −1.0 dBTP (two-pass
  loudnorm), and the zone clicks land at the 1.18 s cascade step.
- Delivery (official-cause cut): `npx hyperframes render -q delivery -w 3` (94.5 MB master, 2:15.8, 1080×1920,
  30 fps), re-encoded to `livrables/coupure-casablanca.mp4` (H.264 CRF 21 + AAC 192k, 28 MB); sound measured at
  −14.0 LUFS integrated, true peak −1.5 dBTP (master −16.8 LUFS before loudnorm).
- S4 (the person's ask): «سقوط جسم موصل على الأسلاك» is shown on the line: a metal rod falls across both
  conductors, a spark at each contact, label «جسم موصل»; the card icon shows the bridged wires.

## Weakest shot / with more time
- Short cut: the map now moves fast; a viewer who wants every name pauses on the final map frame.
- Map labels are 30 px: readable at phone size but small; a phone-first cut could zoom into the centre.

## Kept on purpose
- `composition_file_too_large` on compositions/s2-map.html (generated by tools/s2_build.py).
- Final holds on S5 (the complete list) and S6 («ننتظرو تقرير رسمي») carry `data-hold`.
