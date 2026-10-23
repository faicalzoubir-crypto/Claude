# SPEC — Reel « Rotation d'un solide autour d'un axe fixe »

GOAL:    an élève de 1BAC finishes the reel able to write s = Rθ, V = Rω, T = 2π/ω, and never again reads π/2 for π on a θ(t) graph.
OUTPUT:  HyperFrames, 1080 x 1920, 30 fps, silent (no voice, no music, no SFX: asked by the person).
TIME:    84 s x 30 = 2520 frames. No beat grid (no music).

LOOK:    the fiche itself, as a medium (the person asked for its colours instead of the repo's dark brand).
         ground: #FFFFFF with a 48 px grid of 2 px #E9ECF4 lines; bordeaux margin rule 3 px #9B3A3B at x = 64.
         sheet: one white card x 100–1036, y 150–1100, 2 px #D7DCE7 border, radius 36, persistent all film.
         ink #17181C; titles Caveat 700 88–96 px #8E1B1B on a yellow #FFEC3D marker band (lower 40 % of the line);
         definitions / main circle #2236D6; warnings and errors #E0262B; units #15853A; arc s #7F2CAE;
         circle fill #F4F6FF; grey notes #5D6373; "à retenir" box #FDF3F3.
         formulas: KaTeX_Main / KaTeX_Math italic, 50–90 px, inside 4 px #17181C pills; key result pill filled #FFEC3D.
         tags (CORRIGÉ red, RÉSULTAT / AJOUT green): Inter 800 28 px caps, radius 8.
         captions: Inter 900 60 px, white, 14 px #17181C outline, band y 1130–1320, x 60–940.
         no shadows, no grain, no glow.
PLATFORM: words only in y 168–1330; below 1330 grid only (TikTok / Reels UI); nothing to read at x > 950 below y 1000.
OBJECTS: the solid = a disk seen from the axis (blue rim, pale fill, black centre O on (Δ));
         points = 12–14 px dots (M red, M green / N red in §3, positions green in §6);
         velocity vectors = arrows tangent to the circle, length proportional to R;
         graph = θ(rad) vs t(s) axes with π-ticks, courbe 1 blue 7 px;
         enregistrement = semicircle with M₀…M₇ every π/8.
MOTION:  enter: expo.out / power4.out 0.25–0.45 s; carry / camera: power3.inOut 0.45 s; exit: power3.in 0.2 s;
         rotations linear (constant ω is the physics), one decel power2.out 1.0 s in scene 4;
         titles: whole-line blur 8 → 0 px in 0.2 s, marker band scaleX 0 → 1 in 0.35 s; stamps: back.out(1.6);
         staggers: positions 0.25 s, pills 0.25 s.
SHOTS:   1 hook 0–3: disk turning + "7,85 rad/s ?" on frame 0; red strike 0.55, FAUX stamp 0.85; carry: the disk grows into §1.
         2 définition 3–11: three points trace their circles over one turn; O stays, "immobile" leader at 7.5; carry: disk → §2 circle.
         3 θ et s 11–23: M₀ → M₁ sweeps θ (green) and s (violet); pill s = Rθ at 16.9; red "1 tour = 2π rad" at 19.8; carry → disk §3.
         4 V = Rω 23–35: M and N turn together (same ω), tangent vectors V_M < V_N, decel stop at 28.6; pill V = Rω at 29.7.
         5 T et f 35–46: one full turn traced in bordeaux = T; pills T = 2π/ω, f = 1/T ⇒ ω = 2πf; whip up into the graph.
         6 piège 46–60: graph draws; red misreading to π/2 + 7,85 struck; green reading to π; pill ω ≈ 15,7 rad/s; θ(t) = 15,7 t CORRIGÉ.
         7 enregistrement 60–74: M₀…M₇ every 0.25 s; quarter turn in 4τ; 16τ; pill T = 0,32 s RÉSULTAT; ω ≈ 19,6 rad/s, f ≈ 3,1 Hz.
         8 fin 74–84: three yellow pills; "Réalisé par Mr ELASRI Mohamed" from 79 s to the end.
BANNED:  dark void ground; glow / bloom / particles; gradients; everything centred and fading up; pulsing or breathing loops;
         text moving while read; corner HUD labels; three cards in a row; emoji (no emoji font in the render browser).
QA:      t = 0 (thumbnail), 2.5 (cover PNG), each scene's last landed frame (PNG per scene), seams 3, 11, 23, 35, 46, 60, 74,
         phone-width readability of every caption, the values 15,7 rad/s and 0,32 s exactly as in the fiche.
