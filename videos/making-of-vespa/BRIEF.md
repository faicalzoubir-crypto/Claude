---
workflow: general-video
flow: automation
storyboard: yes
message: "Comment j'ai fait ma vidéo explicative sur la glissade Vespa avec Claude Code + HyperFrames, étape par étape."
destination: instagram-reels
aspect: 1080x1920
language: fr
length: 35s
angle: making-of (process walkthrough)
---

## Intent

Making-of of the Vespa slide explainer (`videos/glissade-vespa-asr/` on branch `claude/bold-wozniak-8xjfgp`, French HD cut, 64 s). Same look as that film: dark background `#0D1316`, hairline grid, one amber accent `#F4A62A`, Montserrat + IBM Plex Mono, smooth crossfades. Generic stylized app windows (folder, player, terminal), no real logos or exact app UIs. Short captions readable on a phone.

Sequence (compressed to ~35 s at the user's choice): hook (3D slide + rewind) · title « Comment j'ai fait cette vidéo » · Étape 1 réunir la matière (file cards) · Étape 2 filmer le lieu dans Google Earth (player window, credit visible) · Étape 3 décrire la vidéo à Claude Code (terminal, `npx skills add heygen-com/hyperframes`, the prompt, 3 highlighted lines) · Étape 4 construire et valider section par section (log + thumbnails + green checks) · Étape 5 le rendu (progress bar → final-video.mp4) · result montage · end card « Fait avec Claude Code + HyperFrames » / « Zoubir Faïçal ».

## Assets

- Final film: `livrables/glissade-vespa-asr-HD.mp4` (FR). Section starts confirmed from 1 fps frames + the project timeline: 0 s footage · 14 s Google Earth · 25 s speedometer · 31 s 3D · 57 s summary.
- Clips cut into `assets/clips/` (hook 50.5–53.5 s, rewind = 0–53.5 s reversed ×67, montage 4.0, 18.4, 28.3, 47.4, 59.6 s), thumbnails in `assets/thumbs/` (sections at 2, 16, 29.3, 35, 61 s).
- Source cards use the user's file names (my-video.mp4, google-earth.mp4, speedometer.jpg, path.png, fuse.jpg, prompt.txt). The my-video thumbnail comes from the **blurred** footage only (the raw clip shows a plate and a driver).
- Google Earth: the source is a phone screen recording of the Google Earth app (no Studio export) → caption « Filmer le lieu dans Google Earth »; the cropped clip `ge-etablissement.mp4` is used with a visible « Google Earth » credit.
- Music: the Vespa film's bed (`assets/music/vespa-fond.wav`) from its groove (12 s), faded out at the end; montage clips keep their original sound, low.

## Notes

- prompt.txt was not in the project: Étape 3 waits for the user's exact prompt.
- Process (user's): build section by section, preview after each, final render `making-of.mp4`.
