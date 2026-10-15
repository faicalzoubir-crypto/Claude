---
workflow: general-video
flow: companion
storyboard: yes
message: "A detached fuse disabled the traction control (ASR). Accelerating while leaning in the roundabout made the rear wheel spin, and nothing stopped it, so the scooter slid."
aspect: 1080x1920
language: fr
length: 60-90s
angle: factual incident explainer
---

## Intent

Short factual explanation video (60–90 s) of a motorcycle slide on a Vespa 300 in a roundabout in Bouznika (Morocco), 19/09/2026. The fuse that powers the ASR (traction control) had come loose, so ASR was off without the rider knowing. While leaning in the roundabout, the rider accelerated; the rear wheel lost grip and spun, nothing cut the engine power, the rear slid out and the scooter went down. No other vehicle involved.

Look (user's words): clean, neutral, factual. Dark background for the diagram and 3D parts, one accent color for highlights, smooth transitions between sections. 30 fps. Format changed by the user after the section 1 preview: 9:16 vertical, 1080×1920 (was 1920×1080).

Structure, in this order:
1. Real footage with a title card "Motorcycle slide – 19/09/2026, Bouznika" (in French; the user first wrote Casablanca, then corrected the place to Bouznika).
2. Google Earth clip: fly-in as-is, then on the top-down hold an animated top-down scooter overlay following the path from path.png; zoom on the slide point and animate the slide (rear stepping out, scooter going down) matching the real footage's timing and direction. Keep the "Google Earth" attribution visible.
3. Speedometer photo: slow zoom onto the check-engine light and the ASR indicator, highlight circle, label "ASR OFF".
4. 3D explanation in Three.js, simplified stylized scooter (not photoreal): shown one after the other (vertical format): (a) ASR ON — lean, accelerate, rear wheel spins faster than front (wheel-speed indicators), ASR cuts power, grip returns, continues safely; (b) ASR OFF — show the detached fuse (fuse photo at the start), same lean + acceleration, rear keeps spinning, no power cut, rear slides out, scooter falls. Labels: "Lean angle = less grip available", "Rear wheel spinning", "ASR cuts power" / "No power cut – fuse detached".
5. Summary card with the message above.

Rough timing: footage 10–15 s, Google Earth 15–20 s, speedometer 5–8 s, 3D 25–30 s, summary 5 s.

## Assets

- assets/footage/source/accident-camera-embarquee.mov — rider's chest-cam footage (vertical 1080×1920, 25 fps, 23.6 s; CapCut end card from 22 s). Section 1. Plate of the dark SUV ahead (≈0–1.3 s) and its driver through the window (≈1.3–2 s) must be blurred.
- assets/footage/source/google-earth-ecran-telephone.mov — phone screen recording of the Google Earth app (vertical, 18.5 s, app UI visible, oblique view, no fly-in, no top-down hold). Section 2 candidate; user asked for a Google Earth Studio fly-in instead (pending decision A/B/C).
- assets/images/source/path-trajet.webp — Google Earth app screenshot with the rider's path drawn in white: entry from the south arm, around the east side (counterclockwise), arrowhead at the north-east of the island = slide point. Section 2.
- assets/images/source/compteur-asr.jpg — dashboard photo: check-engine light (amber, right) and "ASR" on the LCD (bottom right, next to the clock). Section 3.
- assets/images/source/fusible.jpg — photo of the fuse (green blade fuse). Shown at the start of the 3D "ASR OFF" scene.

## Customizations

- No voice-over.
- Audio: keep the original sound of the footage + light background music (synthesized locally, no rights issues).
- Half-speed replay of the slide inside section 1 (proposed, not objected to).
- Entry road name: R322 (route côtière).
- Google Earth: option B chosen (no Studio export). The phone recording is cropped free of the app buttons; its horizon view is the establishing shot, its still overview carries the scooter path, then the camera zooms and un-tilts into a top-down schematic for the half-speed slide. "Google Earth" credit stays on screen through section 2.
- Slide geometry (from footage timing + path.png): onset ≈ 2:40 o'clock on the ring, scooter ends near the outer curb ≈ 1 o'clock.
- Section 3 labels: "VOYANT MOTEUR" and "ASR OFF"; caption "Deux voyants allumés" / "ASR OFF : l'antipatinage est désactivé".
- Section 4 (Three.js, software WebGL in this container): chase camera 3/4 rear, gauges for front/rear wheel speed, power and ASR status; ASR ON then ASR OFF (fuse photo + circuit diagram first). No rider figure.
- Section 5: three numbered steps (fusible débranché → roue arrière qui patine → glissade).
- Music: tools/music.py (numpy synth, 90 BPM, D minor), very low under the footage sound, chime at the ASR cut, riser + hit at the fall, resolve on the summary.

## Notes

- Footage reading (frames every 0.25 s): enters the roundabout ≈2.2 s, leans left around the island (counterclockwise, Morocco), rear lets go and steps out to the outside ≈4.9 s (nose swings left), scooter down on its LEFT side ≈5.6–5.75 s, slides away on its left side 5.75–6.75 s (nose left, seat facing the rider), rider stops ≈7.5 s. ≈2.7 s after entering ≈ a quarter turn → north-east side of the roundabout, matching the path.png arrowhead; aftermath shows the villas of the north-east corner.
- Scooter color: pale mint / sage green (Vespa), used for the overlay and the 3D model.
- Language: the user did not pick one; French chosen (they wrote "voix off", "côtière"; previous project in French). All on-screen text kept in one place so it can switch to English or Arabic.
- Process (user's own): build section by section, render a preview after each and wait for approval; final MP4 at the end.
- If Three.js/WebGL fails inside HyperFrames, tell the user and fall back to rendering the 3D part separately and importing it as a clip.
