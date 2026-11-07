# pub-moto-electrique — brief

Vertical ad (1080×1920, 30 fps, 55–65 s) that convinces viewers to buy an electric motorbike: honest and
enthusiastic, the user sharing a real experience. Arabic voiceover and large Arabic captions. Brand:
`brand/BRAND.md` (dark `#0D1316` + grid, amber `#F4A62A`, petrol in `#F25C54`, electric in `#3CC98F`).

## Decisions taken with the user (2026-11-06)

- **No avatar.** HeyGen is blocked by this environment's network and Kokoro has no Arabic: the user
  records the voiceover themselves; scenes 1 and 6 use their real footage.
- **Scene 3:** the user films a new clip (e-bike entering the station up to the air pump). Until it
  arrives, scene 3 holds the night e-bike ride as a placeholder (`s3-surprise` in `tools/build.py`).
- **Scene 4:** the photo shows the voltmeter on the battery (80.0 V) but not the bike's dashboard (the
  night clip's dashboard reads 75 V), so the line « وهذه لوحة الدراجة، والقيمة نفسها » is dropped.
- **Saad Abid's clip:** chosen here: clip A 2.85–6.35 s (« I came here to show you all the electric… »,
  with his name title) then clip B 2.60–8.10 s (brands on show, then the invitation), 9.0 s, cut at his
  pauses, his own sound, music ducked to 0.10. The second part is punched in ×1.08 to hide the jump cut.
  His speech is Moroccan Darija; local transcription was too rough to caption it, so the card carries it.

## Text the user records (one take, ~1 s pause between lines)

1. البنزين يغلو يوماً بعد يوم، وكل ما تملأ الخزان يخف جيبك.
2. مع الدراجة النارية، كل كيلومتر يكلفني 60 سنتيم من البنزين.
3. اليوم أدخل المحطة لا لأملأ الخزان، بل فقط لأضبط ضغط الهواء في العجلات!
4. ولأنني لا أحب الكلام بلا دليل، هذا الفولطمتر. كلفة الكيلومتر بالكهرباء 5 سنتيمات فقط، أي أرخص بـ12 مرة من البنزين.
5. بعد فيديو سعد عبيد زرت المعرض أواخر أكتوبر، ووجدت فعلاً خيارات كثيرة تناسب كل ميزانية. شكراً سعد! وإن كنتم تفكرون في دراجة كهربائية، فالحسبة واضحة: 5 سنتيمات مقابل 60.

## Scenes (target slots from the user's brief)

| Scene | Slot | Picture | On-screen text |
| --- | --- | --- | --- |
| s1-hook | 0–5 s | fast cuts: Petromin board (15.95 / 15.63), Shell, Afriquia at night, Yoom at dusk | البنزين غلا (from frame 0) |
| s2-essence | 5–18 s | Vespa rides past the Petromin and Shell boards | البنزين: 60 سنتيم / كم (60 counts up) |
| s3-surprise | 18–27 s | **pending: the user's station clip** | captions only |
| s4-preuve | 27–40 s | voltmeter photo, push-in on 80.0 V, then cost-per-km bars | الكهرباء: 5 سنتيمات / كم · مقابل · البنزين: 60 سنتيم / كم · أرخص بـ12 مرة |
| s5-saad | 40–49 s | Saad Abid's clip, his sound | @Saadabidofficiel · الفيديو الذي جعلني أزور المعرض |
| s6-merci | 49–63 s | night ride on the e-bike (slow motion, 60 fps source) | شكراً @Saadabidofficiel · 5 مقابل 60 سنتيم / كم |

## Files

- `sources/` — the user's uploads as received. `tools/footage.sh` makes `assets/footage/` (H.264,
  gitignored) and `assets/images/voltmetre.jpg`.
- `tools/build.py` — the plan (slots, shots, voice lines, caption groups, cues) → `index.html`,
  `compositions/*.html`, `tools/plan.json`.
- `tools/music.py` — brand music bed (90 BPM, Dm – B♭ – F – C) and sound effects (filtered noise) from
  `tools/plan.json`. Ducking is the music's volume lane in `index.html`.
- Fonts: Readex Pro (Arabic + Latin, OFL), Space Grotesk for numbers, both in `assets/fonts/`.

## Deliveries

- 2026-11-07: two renders without voice (the user records it outside Claude): with captions to read
  along, and without captions; timing table and SRT in `livrables/`. Line timings in `tools/build.py`
  (`VOICE`) are what the user reads to. Scene 3 still the stand-in. See `REVIEW.md`.

## When the recording arrives

Clean it (high-pass, light denoise, compression, −16 LUFS), cut it into `assets/vo/vo1…vo5.wav`, time the
caption groups and cues to the words, set `HAVE_VOICE_AUDIO = True`, retime the slots in `tools/build.py`,
then `python3 tools/build.py && python3 tools/music.py`, check, snapshot, review, render.
