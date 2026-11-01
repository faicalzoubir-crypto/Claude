# REVIEW — reel_rotation_1BAC

## Creative calls
- No avatar, no voice, no music, no SFX: the person asked for it ("sans voix off sans musique", "sans avatar"). So HeyGen was not used; the reel is a HyperFrames composition rendered locally.
- Look = the fiche itself (white squared paper, bordeaux margin rule, one white section card, Caveat titles on a yellow marker, KaTeX formulas in pills, blue / red / green / violet roles). The repo's dark "Vespa" brand was set aside on purpose for this video.
- Captions (white Inter 800, black outline) carry the script; the sheet carries the diagram and the formulas, so the text is not read twice word for word.
- Lower part of the frame (y > 1330) left as grid only, for the TikTok / Reels UI.
- Hook: the question "Tous les points d'une roue tournent-ils à la même vitesse ?" (chosen by the person, option 3), answered in scene 4 (same ω, V = Rω grows with R). It replaced "7,85 rad/s ? FAUX !", which left a struck wrong value on screen with its explanation 43 s later. Not built: "Tout le chapitre en 75 secondes". The hook lasts 4 s (12 words to read), so the film is 85 s.
- Transitions: the disk carries across scenes 1→2→3→4→5 (it grows / moves into the next diagram); a whip up from 5 to 6; blur swaps 6→7→8.

## Measured vs looked at
- `hyperframes check`: ok, 0 errors. Layout, contrast, motion and type floor measured.
- Looked at: every scene's landed frame, the seams, the phone-width sheet.
- Values checked against the fiche: ω = π / 0,2 ≈ 15,7 rad/s and θ(t) = 15,7 t (courbe 1), T = 16 τ = 16 × 20 × 10⁻³ s = 0,32 s, ω ≈ 19,6 rad/s, f ≈ 3,1 Hz.
- Not applicable: sound (silent film by request).
- Delivery file: H.264 1080×1920, 30 fps, 85.0 s; a silent AAC track (max −91 dB) and faststart were added after the render so Instagram / TikTok imports never reject a video without an audio stream. Measured, not heard.

## Warnings kept on purpose
- `film_silent`: asked by the person.
- `line_unread` on the "T" of ω = 2π/T at 73.07 s: the pill stays on screen until 74.7 s (checked on the 74.5 s frame); the finding is a measuring artefact of the stamp-in.
- `connector_orphan` (info) on the graph axes at 52.3 s: the axes are drawn, both ends are on stage.

## Weakest shot / with more time
- Scene 5 (T et f): the turn is drawn at an illustrative speed (one turn in 2 s), no numbers attached on purpose; a chronometer with a real T would be stronger.
- Captions with Greek letters (ω, π, θ) in Inter 800 + outline are heavier than the Latin text; a KaTeX-styled caption span for symbols would read cleaner.
