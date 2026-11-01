# Review — panneau-n1-50cc

## Creative calls

- The user's scene list was the storyline; no alternatives were built.
- Where footage was missing (fork, police), the user's Google Earth views carry the scene: the riders' route as a green line with their Vespa seen from above, the police stop as a badge with flashing red/blue lights.
- The sign is redrawn as a vector (traced on the user's clean render) because their photo of it was an 8× enlargement; in scene 1 it grows out of the real sign after a 0.8 s pause on the footage.
- Loop: scene 7 plays fork_b up to frame 197 and scene 1 opens on that frame, paused (PNG), so the last and first frames are identical; the music is rendered as a loop and cut on a beat at 39.0 s.
- The music is synthesised in code so the hit lands exactly at 20.0 s and the loop has no seam.

## Measured vs looked at

- `check`: no errors. Stills of every scene, the review, seam and phone sheets (360 px) looked at; all cards legible at phone width.
- Loop: last vs first frame, mean difference 0.0 outside the cards. Music: -14.3 LUFS, peak -1.0 dBFS, section levels measured (build -17.8 → -13.5 dB RMS, breath -26 dB before the hit, drop -13.2, scene 6 -17.5).
- Nobody has heard the music: it was measured, not listened to.

## Weakest shot

- Scene 3 wide view (11–12.5 s): the Vespa is 72 px on a large map; readable as a marker, not as a Vespa. With more time: a short push-in on the route as it is drawn.
- The synthesised music is functional; a produced track would sound richer.

## Warnings kept on purpose

- `line_unread` on scene 4's card: it continues across two scenes (s4-fork 1.9 s + s4-route 3.0 s = 4.9 s on screen); the check measures each half.
- `line_unread` on « ودابا ما يمكنش تقول… » (1.96 s vs 2.0 s): it is the loop line and reads straight into the opening quote; scene 7 is 2 s by the user's spec.
