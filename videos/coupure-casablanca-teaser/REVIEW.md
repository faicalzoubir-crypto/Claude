# REVIEW — coupure-casablanca-teaser (20 s, 1080×1920, music only)

Asked: «فيديو teaser بموسيقى حماسية فيه لقطات مهمة من الفيديو، بدون vo».

## How it is built
- `python3 tools/build.py [--src film.mp4]` cuts every shot from the full film's no-subtitle render
  (`../coupure-casablanca/livrables/coupure-casablanca-sans-sous-titres.mp4` by default; the delivered teaser
  used the uncompressed master of that render), trims the track, and writes `index.html`,
  `compositions/overlay.html` and `compositions/end.html`. Then `npx hyperframes render`.
- Music: HeyGen music catalog (free with the sign-in), «aggressive cinematic drums, heavy bass hits, fast-paced»,
  139 BPM, `assets/music/source-c08.mp3`. Beat grid from `npx hyperframes beats` in `data/beats.json`. The silent
  lead-in is dropped so the first hit is frame 0; 1.6 s fade under the end card.
- Brand (brand/BRAND.md): dark ground + grid, amber for the one key word per line, mint CTA. The brand's calm
  90 BPM bed was not used: the person asked for energetic music.

## Cut (bars of 4 beats) — 20 s («Make it 20 sec»; a first 27.6 s cut is replaced)
- 0–3.5 S1: «16:48», the tower in the storm; punch-in on the beat as the city's windows go out.
- 3.5–6.9 S2 at 3×: the neighbourhoods go dark (the track's breakdown) · «بزاف د الأحياء بلا ضو».
- 6.9 the drop: S3 at 3×, the 225 kV chain draws itself · «جوج محطات تحويل».
- 8.6–10.4 S4: «3», then «3 ≠ 4» · «تلاتة ولا ربعة؟».
- 10.4–12.1 S5: cut A, cut B (both substations dark, the film's «مثال توضيحي» chip visible) · «كيفاش طفاو بجوج؟».
- 12.1–13.8 S6 at 4×: 3 h vs 22:11 vs 23:03, «شهادات» tags visible · «شحال دام الانقطاع؟».
- 13.8–15.5 S8 questions at 3×; 15.5–17.2 four one-beat recap shots.
- 17.2–20.0 end card: date · «انقطاع الكهرباء بالدار البيضاء» · «شنو وقع فالشبكة؟» · «شوف الفيديو الكامل»; music fades
  over the last 1.4 s.
- Dropped for length: both supply sides (S3f), «متأخر» (S5g). No claim on screen that the film does not make.

## Looked at
- `npx hyperframes check`: ok, no warnings. Snapshots at every shot; fixed: the drop flash rendered from frame 0
  (fromTo immediateRender), the city punch-in cropped the title (now 1.04→1.08).
- Text sits in the film's old subtitle band (y ≈ 1450–1550) over a dark scrim; nothing in the top 150 px or the
  bottom 250 px except footage.
