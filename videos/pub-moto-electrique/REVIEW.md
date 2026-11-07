# Review — pub-moto-electrique (first delivery, 2026-11-07)

Delivered without voice, at the user's request: they record the Arabic voiceover outside Claude.

- `livrables/pub-moto-electrique-sous-titres.mp4` — captions burned in, for reading along.
- `livrables/pub-moto-electrique-sans-sous-titres.mp4` — the same film with the captions track hidden
  (`python3 tools/build.py --sans-sous-titres`), to add the voice and their own captions in their app.
- `livrables/timing.md` — when each line starts and ends; `livrables/sous-titres.srt` — the caption
  groups at those times.

## Creative calls

- No avatar (HeyGen blocked here, user's choice): scenes 1 and 6 are the user's own footage.
- Hook: « البنزين غلا » on a brand card from frame 0 over the Petromin board, whose real prices
  (Gasoil 15.95, SSP 15.63) stay readable under it; four cuts of about 1.2 s across four stations.
- Proof: the voltmeter photo with a push-in on its 80.0 V reading, then a brand graphic (grid
  background) where the bars grow right to left: electric 5 in green, petrol 60 in red, then the amber
  « أرخص بـ12 مرة » chip on a riser and low impact in the music, once in the film.
- Saad Abid: 9.0 s of his clip, cut at his pauses, his sound, music ducked to 0.10, no captions on his
  Darija (local transcription too rough to trust).
- Ending: night ride in slow motion (60 fps source at 0.49×), « شكراً @Saadabidofficiel », then
  « 5 مقابل 60 / سنتيم / كم » held for the last 2.5 s.
- Line timings are a deliberately unhurried reading pace (about 2.3–2.6 words a second, a breath at
  each full stop), because the user reads to them.

## What was measured, what was only looked at

- `check`: passes. Kept warnings: `nested_media_start_basis_ambiguous` (scene media times are local on
  purpose), `timeline_track_too_dense` (the 32 caption groups share the one captions track by design).
- Looked at: the review beat, seam and phone sheets (every card and caption reads at 360 px).
- Sound: the music bed and effects are measured on the rendered file (`hyperframes audio`), not heard.
  The music dips to 0.22 where each line will be spoken and rises to 0.55 in the gaps; without the voice
  those dips are audible on purpose.

## Weakest points, and what comes next

- Scene 3 is a stand-in (the night ride) until the user's clip of entering the station arrives.
- The captions follow estimated timings: once the recording exists, cut it into `assets/vo/`, time the
  groups to the words, set `HAVE_VOICE_AUDIO`, and re-render a single version with voice and captions.
- The hook title says « غلا » (user's correction) while line 1 still reads « يغلو »: the caption
  follows whatever the user actually says once the recording is in.
