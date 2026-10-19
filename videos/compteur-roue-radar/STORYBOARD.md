---
format: 1920x1080
duration: 110s
message: "Ton compteur compte des tours de roue, pas des kilomètres : avec des roues plus grandes qu'à l'origine, tu roules plus vite qu'il ne l'affiche, et le radar, lui, mesure la vraie vitesse."
arc: concept-explainer with process
audience: Lycéens et grand public
mode: collaborative
language: fr
music: none
title: "Pourquoi ton compteur peut te mentir : de la roue au radar"
---

## Video direction

- **Palette** — the brand (`brand/BRAND.md`, `frame.md`): instrument-panel dark `#0D1316` with the 60 px hairline grid on every frame; cards `#141D21` + `#26343B` hairlines; text `#E8EEEC` / `#93A4A7`; ONE amber `#F4A62A` highlight per moment (the piece the voice is naming); mint `#93CDBB` for drawn objects (car, wheels, mechanics); red `#F25C54` / green `#3CC98F` only for above / below the displayed speed.
- **Motion grammar** — entrances 0.4–0.7 s on long-tail eases (`power3.out` / `expo.out`), amber elements draw on (stroke / scaleX) rather than pop; VO-paced reveal: every piece appears on the word that names it, never front-loaded; wheels and the needle are the only things allowed to keep moving during a hold.
- **Rhythm** — reveal frames: 01, 03, 04, 05, 06, 09; held reads: 02 (title settles, wheel keeps turning), 07 → 08 (tension, then the dialogue reads still), 10 (final sentence holds to the end).
- **Negative list** — no slideshow (layout dumped at t=0 then frozen), no screensaver (everything floating), no bounce/elastic, no glow halos, no second accent colour, no text below the subtitle line (y ≈ 900), no exit tweens except the last frame's settle.

## Frame 1 — La question

- scene: Une citadine 5 portes évoquant la Ford Fiesta 2023 roule de profil sur une route, roues qui tournent ; la question s'écrit à l'écran.
- voiceover: "Si je change la taille de mes roues… mon compteur affiche-t-il toujours la vraie vitesse ?"
- duration: 5.303s
- transition_in: cut
- status: animated
- src: compositions/frames/01-question.html
- type: hook
- persuasion: Rhetorical question
- beat: Curiosity + puzzlement
- blueprint: kinetic-type-beats (Adapt)
- focal: the question
- roles: question = foreground subject · car = supporting (mint) · speedometer = supporting · road + grid = background
- sfx: whoosh-soft

narrativeRole: Ouvre le doute sur un objet que tout le monde croit fiable — le compteur — avec la question exacte du brief.
keyMessage: Changer de roues pourrait fausser ce que le compteur affiche.

Scene 1 (0.0–0.6s): grid ground; the car rolls in from the left onto the road (wheels turning, dashes sliding), the speedometer card fades up right with the needle sweeping to 60 — Asymmetric 60/40.
Scene 2 (0.5–2.0s): per-word reveal of « Si je change la taille de mes roues, » on the VO; the tyre tag fades in under it.
Scene 3 (2.4–4.9s): per-word reveal of the second half; « vraie vitesse » gets its amber underline drawn on (scaleX) on the word; the « ? » badge pops in on « vitesse ».
Scene 4 (4.9–5.3s): hold; wheels and road keep moving.

## Frame 2 — Réponse courte : non

- scene: Carton titre « Pourquoi ton compteur peut te mentir : de la roue au radar » ; dessous, « il compte des tours de roue » ; bandeau discret « Hypothèse : compteur parfaitement étalonné en usine ».
- voiceover: "Réponse courte : non. Ton compteur ne mesure pas ta vitesse… il compte des tours de roue."
- duration: 5.893s
- transition_in: crossfade
- status: animated
- src: compositions/frames/02-titre.html
- type: product_intro
- persuasion: Counterintuitive claim + frame-then-fill
- beat: Surprise + orientation
- blueprint: titlecard-reveal (Adapt)
- focal: the title
- roles: title = foreground subject · « Non. » + claim = supporting · hypothesis card = supporting · wheel + turn arrow = supporting (mint/amber)
- sfx: tick

narrativeRole: Pose la thèse dès le deuxième temps (le compteur compte des tours) et affiche l'hypothèse de travail, avant toute explication.
keyMessage: Le compteur ne mesure pas la vitesse, il compte des tours de roue — et on le suppose parfaitement étalonné.

Scene 1 (0.0–0.8s): diagonal panel and the wheel slide in from the right; the title rises in line by line, eyebrow first — Cover, left anchor.
Scene 2 (0.25–1.6s): « Réponse courte » chip, then « Non. » lands on « non » (scale 0.92 → 1, no bounce).
Scene 3 (1.8–4.0s): the wheel turns; the amber turn arrow draws on around it; the TOURS counter ticks 0001 → 0004.
Scene 4 (4.0–5.9s): « Il compte des tours de roue. » reveals on « il compte », « tours de roue » in amber; the hypothesis card slides up last and holds.

## Frame 3 — Du moteur à la roue

- scene: Vue éclatée de la traction avant de la Fiesta, de gauche à droite : moteur (pistons + vilebrequin), embrayage, boîte de vitesses, différentiel (même carter), arbres de transmission (cardans), roue avant ; une flèche de mouvement s'allume à chaque étape quand la voix la nomme.
- voiceover: "Tout part du moteur : les pistons font tourner le vilebrequin. L'embrayage relie ou sépare le moteur et la boîte. La boîte de vitesses échange de la vitesse contre de la force. Le différentiel partage la rotation entre gauche et droite, pour les virages. Les cardans l'amènent aux roues avant… et la roue transforme la rotation en déplacement."
- duration: 20.124s
- transition_in: push-slide LEFT
- status: animated
- src: compositions/frames/03-transmission.html
- type: feature_showcase
- persuasion: Causal chain + progressive disclosure
- beat: Comprehension + momentum
- blueprint: spatial-pan-stations (Adapt)
- focal: the lit station
- roles: 6 station cards = foreground subjects, dim until named · arrows = supporting (amber when lit) · « même carter » outline = supporting
- sfx: click, click, click, click, click, whoosh-soft

narrativeRole: Montre d'où vient la rotation que le compteur va compter, maillon par maillon, sur une scène unique où les flèches s'allument dans l'ordre.
keyMessage: La rotation du moteur arrive jusqu'aux roues, et c'est la roue qui fait avancer la voiture.

Adapt: one fixed canvas instead of a pan; the signature move (each station lit in turn, a callout per station) stays.
Scene 1 (0.0–0.6s): header in; the six cards appear dimmed (25%) in a quick left-to-right cascade — Six-across row, one depth layer.
Scene 2 (0.9–3.3s): « moteur » → card 1 lights to full, pistons pump and the crank turns; its label + sub reveal.
Scene 3 (3.5–6.2s): arrow 1 draws on, card 2 lights; the clutch disc slides against the flywheel and back (relie / sépare).
Scene 4 (6.6–10.0s): arrow 2 draws on, the dashed « même carter » outline draws around 3–4, card 3 lights, gears turn in mesh.
Scene 5 (10.2–14.5s): arrow 3, card 4 lights, the ring gear turns; the two curve arrows (gauche / droite) draw on.
Scene 6 (14.8–16.4s): arrow 4, card 5 lights, the shafts spin (bellows shimmer).
Scene 7 (16.8–20.1s): arrow 5, card 6 lights, the wheel turns; « la voiture avance » arrow draws on and holds.

## Frame 4 — Le capteur compte les tours

- scene: Zoom sur la roue avant : couronne dentée + capteur ABS ; à chaque tour, des impulsions filent par un câble vers un boîtier « calculateur », puis vers le compteur du tableau de bord ; un compteur « tours » s'incrémente.
- voiceover: "Ici, le capteur ABS compte les tours de roue, et envoie l'info au calculateur… puis au compteur."
- duration: 6.31s
- transition_in: zoom-through
- status: animated
- src: compositions/frames/04-capteur.html
- type: feature_showcase
- persuasion: Demonstration (show the mechanism running)
- beat: "Aha"
- blueprint: compose
- focal: the pulse path
- roles: wheel + tone ring + sensor = foreground subject (mint) · cable pulses = amber · calculateur + compteur = supporting
- sfx: blip, blip, blip, chime

narrativeRole: Relie la roue au compteur : l'information qui remonte est un nombre de tours, pas une vitesse.
keyMessage: Le compteur ne reçoit qu'un nombre de tours de roue.

Scene 1 (0.0–0.6s): header; wheel and tone ring in from the left, turning — Left-to-right signal path, 3 nodes.
Scene 2 (0.6–2.4s): on « capteur ABS » the sensor slides into place and label 1 reveals; each tooth passing sends a blip.
Scene 3 (2.7–3.9s): amber pulses travel cable 1; the TOURS counter ticks; on « calculateur » the chip card and label 2 reveal.
Scene 4 (4.9–6.3s): on « puis au compteur » pulses travel cable 2, the speedometer card and label 3 reveal, needle settles on 60.

## Frame 5 — Le calcul du compteur

- scene: Flanc de pneu « 195/55 R16 » décomposé (195 largeur, 55 série, R16 jante) → formule du diamètre avec les valeurs → 621 mm ; la roue se déroule sur une ligne de 1,95 m ; puis la formule de la vitesse réelle s'écrit en bas.
- voiceover: "Le compteur multiplie ces tours par la circonférence d'origine. Pneu d'origine : 621 millimètres de diamètre, soit 1,95 mètre par tour. Changer de roues change donc la vitesse réelle… dans le rapport des diamètres."
- duration: 15.24s
- transition_in: crossfade
- status: animated
- src: compositions/frames/05-calcul.html
- type: feature_showcase
- persuasion: Worked example with real numbers
- beat: Comprehension + confidence
- blueprint: compose
- focal: 621 mm
- roles: wheel diagram = foreground subject · formula card = foreground subject · chips + circumference + speed formula = supporting
- sfx: tick, tick

narrativeRole: Donne la règle de calcul avec les vrais chiffres du pneu d'origine, et les deux formules du brief.
keyMessage: Vitesse affichée = tours × 1,95 m ; vitesse réelle = vitesse affichée × (diamètre nouveau / diamètre d'origine).

Scene 1 (0.0–3.9s): header; the wheel fades in; « circonférence d'origine » underline already amber in the title — Split 40/60.
Scene 2 (4.1–5.1s): « Pneu d'origine » → the code 195 / 55 R16 reveals part by part, then its three chips.
Scene 3 (5.1–7.5s): on « 621 » the formula card writes line by line; the full-diameter dimension line draws on and « 621 mm » lands in amber; the rim and sidewall dimensions draw on.
Scene 4 (7.5–9.9s): on « 1,95 mètre » the circumference line reveals, « 1,95 m » counts up.
Scene 5 (10.3–15.2s): on « Changer de roues » the speed-formula card slides up; hold.

On screen (mot pour mot) : « Diamètre = (jante en pouces × 25,4) + 2 × (largeur × série / 100) » → (16 × 25,4) + 2 × (195 × 55 / 100) = 406,4 + 214,5 ≈ 621 mm → circonférence ≈ 1,95 m par tour. « Vitesse réelle = vitesse affichée × (diamètre nouveau / diamètre d'origine) ».

## Frame 6 — Petite roue, grande roue

- scene: Deux roues côte à côte au-dessus d'une règle graduée : la petite (583 mm) et la grande (724 mm) font chacune exactement 1 tour ; la grande s'arrête plus loin (1,83 m contre 2,27 m) ; au-dessus, le compteur affiche « 1 tour » pour les deux ; puis deux cartes : roue plus grande → vitesse réelle SUPÉRIEURE (rouge), roue plus petite → INFÉRIEURE.
- voiceover: "Chaque roue fait un tour : la grande va plus loin. Mais le compteur compte « un tour »… dans les deux cas. Roue plus grande : tu roules plus vite qu'affiché. Plus petite : moins vite."
- duration: 10.607s
- transition_in: push-slide LEFT
- status: animated
- src: compositions/frames/06-comparaison.html
- type: benefit_highlight
- persuasion: Comparison of two options + demonstration
- beat: "Aha" + delight
- blueprint: comparison-split (Adapt)
- focal: the distance gap
- roles: two wheels = foreground subjects (mint) · rulers = background · trails + distance chips = amber · counter cards = supporting
- sfx: roll, ding, tick

narrativeRole: Rend la conséquence visible : même nombre de tours, distance différente — donc vitesse différente de l'affichage.
keyMessage: Roue plus grande → vitesse réelle supérieure à l'affichage ; roue plus petite → inférieure.

Adapt: the two items are stacked lanes on one ruler instead of mirrored tilts; the punctuating badge (the counter card) stays.
Scene 1 (0.0–0.4s): header, the two empty rulers and dashed start ghosts — Stacked lanes + right column.
Scene 2 (0.25–2.6s): both wheels roll exactly one turn (rotation 360°, translation = circumference); the amber trails draw behind them; « 1,83 m » and « 2,27 m » chips land on « plus loin ».
Scene 3 (3.0–5.8s): on « un tour » both counter cards reveal with « 1 tour ».
Scene 4 (6.1–8.5s): lane B's verdict reveals (SUPÉRIEURE in red); 8.8–10.0s lane A's verdict (INFÉRIEURE in green); hold.

## Frame 7 — Karim est serein

- scene: Rue en ville, panneau « 60 ». La Fiesta de Karim, montée en grandes roues « 225/65 R17 » (étiquette « dimension hypothétique »), passe ; gros plan sur son compteur : l'aiguille se cale sur 60. Un policier au bord de la route lève son radar : l'écran affiche 70.
- voiceover: "Karim a monté de grandes roues. Son compteur indique 60 : il est serein."
- duration: 5.854s
- transition_in: crossfade
- status: animated
- src: compositions/frames/07-karim.html
- type: social_proof
- persuasion: Worked example (story case) + before/after setup
- beat: Calm → tension
- blueprint: compose
- focal: 60 vs 70
- roles: car = foreground subject (mint) · gauge card = supporting · officer + radar = supporting · sign + city = background
- sfx: tick, radar-beep

narrativeRole: Passe de la règle au cas concret : le compteur dit 60 alors que le radar mesure 70.
keyMessage: Avec ses grandes roues, Karim roule à 70 en croyant rouler à 60.

Scene 1 (0.0–1.8s): city, road and sign in place; the car drives in from the left and stops at its mark, wheels turning; the tyre tag reveals on « grandes roues » — Wide street, 3 depth layers.
Scene 2 (2.0–4.4s): the gauge card reveals, the needle sweeps up and settles on 60 on « 60 »; title line « Compteur : 60 » holds.
Scene 3 (4.4–5.9s): the officer raises the radar, the beam sweeps on, the radar card reveals « 70 » in red with a double beep; « Radar : 70 » completes the title.

## Frame 8 — Le contrôle

- scene: Karim arrêté au bord de la route ; le policier et lui échangent en bulles de BD, une réplique après l'autre ; à la fin, Karim baisse les yeux vers ses grandes roues.
- voiceover: "« Bonjour monsieur, vous rouliez à 70 km/h dans une zone limitée à 60. » « Impossible ! Mon compteur indiquait exactement 60, j'en suis sûr ! » « Votre compteur est réglé pour les roues d'origine. Avec des roues plus grandes, chaque tour vous fait parcourir plus de distance. Le radar, lui, mesure votre vitesse réelle. »"
- duration: 21.631s
- transition_in: cut
- status: animated
- src: compositions/frames/08-controle.html
- type: social_proof
- persuasion: Common-belief vs reality (dialogue)
- beat: Tension → recognition
- blueprint: compose
- focal: the speaking bubble
- roles: bubbles = foreground subjects (one at a time) · Karim + car (mint) and officer = supporting · wheel ring = amber at the end
- sfx: siren-chirp

narrativeRole: Fait dire l'explication par le personnage qui a la vraie mesure — le radar — face à la croyance de Karim.
keyMessage: Le compteur est réglé pour les roues d'origine ; le radar mesure la vitesse réelle.

Scene 1 (0.0–0.3s): the car at a stop by the curb, the officer at the window; a short siren chirp.
Scene 2 (0.3–5.5s): bubble 1 (officer) grows from its tail and holds while it is read.
Scene 3 (6.0–10.4s): bubble 1 fades to 0; bubble 2 (Karim) grows from its tail.
Scene 4 (10.9–20.4s): bubble 2 dims to 40%; bubble 3 (officer) grows and holds — the explanation reads still.
Scene 5 (20.4–21.6s): Karim's eyes drop to his wheel; the amber dashed ring draws around the front wheel and the « 225/65 R17 au lieu de 195/55 R16 » callout reveals.

Dialogue (mot pour mot, bulles) :
- Policier : « Bonjour monsieur, vous rouliez à 70 km/h dans une zone limitée à 60. »
- Karim : « Impossible ! Mon compteur indiquait exactement 60, j'en suis sûr ! »
- Policier : « Votre compteur est réglé pour les roues d'origine. Avec des roues plus grandes, chaque tour vous fait parcourir plus de distance. Le radar, lui, mesure votre vitesse réelle. »

## Frame 9 — Le tableau

- scene: Titre « Compteur affiché : 60 km/h – Ford Fiesta 2023 (référence 195/55 R16) » ; tableau 4 colonnes (Pneu · Diamètre · Écart · Vitesse réelle) dont les 8 lignes arrivent une par une ; les vitesses réelles au-dessus de 60 passent en rouge ; la ligne 225/65 R17 (Karim, 70,0) est soulignée ; la note s'affiche en bas.
- voiceover: "Pour 60 au compteur : 56 en vrai avec de petites roues… 70 avec celles de Karim… et 73,5 avec les plus grandes."
- duration: 11.123s
- transition_in: crossfade
- status: animated
- src: compositions/frames/09-tableau.html
- type: social_proof
- persuasion: Statistical proof (worked table)
- beat: Conviction
- blueprint: grid-card-assemble (Adapt)
- focal: the 70,0 km/h row
- roles: table rows = foreground subjects · bars = supporting (red / green) · footnote = supporting
- sfx: tick, tick, tick

narrativeRole: Généralise le cas de Karim à toutes les tailles de pneus avec les chiffres exacts.
keyMessage: Plus le pneu est grand, plus la vitesse réelle dépasse les 60 affichés.

Scene 1 (0.0–0.8s): eyebrow, title and column heads; the dashed 60 line draws down — Data table, full width.
Scene 2 (0.8–4.2s): rows 1–4 slide in one by one (row 1 on « 56 »), each bar growing from the 60 line.
Scene 3 (4.2–6.9s): rows 5–7 slide in; row 7 (Karim, 70,0) lands on « 70 », its Karim chip pops.
Scene 4 (6.9–11.1s): row 8 lands on « 73,5 »; the footnote reveals; hold.

Tableau (mot pour mot) :

| Pneu | Diamètre | Écart | Vitesse réelle |
|---|---|---|---|
| 175/65 R14 | 583 mm | −6,1 % | 56,3 km/h |
| 195/60 R15 (usine) | 615 mm | −1,0 % | 59,4 km/h |
| 195/55 R16 (référence) | 621 mm | 0 % | 60,0 km/h |
| 205/55 R16 | 632 mm | +1,8 % | 61,1 km/h |
| 205/60 R16 | 652 mm | +5,1 % | 63,0 km/h |
| 215/65 R16 | 686 mm | +10,5 % | 66,3 km/h |
| 225/65 R17 | 724 mm | +16,7 % | 70,0 km/h |
| 235/70 R17 | 761 mm | +22,5 % | 73,5 km/h |

Note : « les dimensions au-delà de 205/55 R16 sont hypothétiques et ne sont pas homologuées sur la Fiesta. »

## Frame 10 — Trois réflexes

- scene: Trois conseils numérotés qui arrivent l'un après l'autre (pneu + carte grise, téléphone GPS, clé de réglage), puis la phrase finale seule, en grand : « Ton compteur compte des tours, le radar mesure la réalité. »
- voiceover: "Trois réflexes : respecte les tailles homologuées, vérifie ta vitesse au GPS après un changement de roues, et fais recalibrer ton compteur si besoin. Ton compteur compte des tours, le radar mesure la réalité."
- duration: 13.496s
- transition_in: crossfade
- status: animated
- src: compositions/frames/10-conclusion.html
- type: cta
- persuasion: Rule of three + distillation (callback to the title)
- beat: Clarity + resolve
- blueprint: kinetic-type-beats (Adapt)
- focal: the final sentence
- roles: three tip cards = foreground subjects then supporting · final sentence = foreground subject · rings = background
- sfx: chime

narrativeRole: Transforme la compréhension en gestes concrets, puis condense toute la vidéo en une phrase.
keyMessage: Ton compteur compte des tours, le radar mesure la réalité.

Scene 1 (0.0–1.1s): eyebrow; the rings fade in very faint — Three-up row, then centered closer.
Scene 2 (1.2–8.4s): tip 1 on « respecte », tip 2 on « vérifie », tip 3 on « fais recalibrer » — each card rises in, its number pops.
Scene 3 (8.7–12.0s): the final sentence reveals line by line, « tours » and « réalité » in amber; the cards dim slightly.
Scene 4 (12.0–13.5s): hold, then a slow settle to the end (final frame).

On screen (mot pour mot) :
1. Respecter les dimensions de pneus homologuées (voir carte grise / notice).
2. Vérifier sa vitesse avec le GPS du téléphone après un changement de roues.
3. Faire recalibrer le compteur chez un professionnel si nécessaire.
