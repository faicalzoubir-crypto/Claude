# REVIEW: meteo-depression-darija (silent, music-only, 90 s)

Checked from stills (`npx hyperframes snapshot`) and `npx hyperframes check` (0 errors, 0 warnings); the
sound was measured, not heard.

| Frame | Must show | Result |
| --- | --- | --- |
| 0 s | «منخفض أطلسي» already on screen over the skyline in rain | yes |
| s1 «دارك / وطوموبيلك» | house and car cards with an orange «؟» | yes |
| s2 after the four names | whole map (one outline, southern provinces), 4 provinces orange with chips | yes |
| s2 after «الشمال» | north + centre light orange, panel «الثلاثاء ← الأربعاء», rain / wind / cold | yes |
| s3 each instruction | hero drawing swapped on the word, current row orange | yes |
| s4 «30 سم» | water to the 30 cm mark, car lifting | yes |
| s5 | question → two branches → question to ask the insurer | yes |
| s6 end | marocmeteo.ma, 15 / 19 / 177, «شارك الفيديو», held 2.2 s after the last line | yes |
| subtitles | one line each (widest 796 px of 908), bottom edge 1590 px (bottom 15 % clear), ≤ 15 characters a second | yes |

Defaults avoided: no footage, no glow, no three-cards row except the 15 / 19 / 177 strip the user asked for;
nothing in the bottom 15 % except the 6 px progress bar.

Choices to confirm with the user: «برد» drawn as cold (thermometer); «الشمال والوسط» = the 7 regions listed in SPEC.md.

## Render (livrables/meteo-depression-darija-90s.mp4)

1080 × 1920, 30 fps, H.264 + AAC, 90.0 s, 7.9 MB. Sound measured with ffmpeg ebur128 (not heard): music only,
-16.1 LUFS integrated, true peak -4.7 dBFS, LRA 2.0 LU. Frames pulled from the MP4 at 0.5 / 12 / 17.5 / 30 / 40.5 /
70 / 88 s match the stills: Cairo loaded, map whole, subtitles one line above the bottom 15 %.
