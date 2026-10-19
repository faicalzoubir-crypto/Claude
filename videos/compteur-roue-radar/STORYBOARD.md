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

## Frame 1 — La question

- scene: Une citadine 5 portes évoquant la Ford Fiesta 2023 roule de profil sur une route, roues qui tournent ; la question s'écrit à l'écran.
- voiceover: "Si je change la taille de mes roues… mon compteur affiche-t-il toujours la vraie vitesse ?"
- duration: 5.303s
- transition_in: cut
- status: built
- src: compositions/frames/01-question.html
- type: hook
- persuasion: Rhetorical question
- beat: Curiosity + puzzlement
- blueprint: kinetic-type-beats

narrativeRole: Ouvre le doute sur un objet que tout le monde croit fiable — le compteur — avec la question exacte du brief.
keyMessage: Changer de roues pourrait fausser ce que le compteur affiche.

## Frame 2 — Réponse courte : non

- scene: Carton titre « Pourquoi ton compteur peut te mentir : de la roue au radar » ; dessous, « il compte des tours de roue » ; bandeau discret « Hypothèse : compteur parfaitement étalonné en usine ».
- voiceover: "Réponse courte : non. Ton compteur ne mesure pas ta vitesse… il compte des tours de roue."
- duration: 5.893s
- transition_in: crossfade
- status: built
- src: compositions/frames/02-titre.html
- type: product_intro
- persuasion: Counterintuitive claim + frame-then-fill
- beat: Surprise + orientation
- blueprint: titlecard-reveal

narrativeRole: Pose la thèse dès le deuxième temps (le compteur compte des tours) et affiche l'hypothèse de travail, avant toute explication.
keyMessage: Le compteur ne mesure pas la vitesse, il compte des tours de roue — et on le suppose parfaitement étalonné.

## Frame 3 — Du moteur à la roue

- scene: Vue éclatée de la traction avant de la Fiesta, de gauche à droite : moteur (pistons + vilebrequin), embrayage, boîte de vitesses, différentiel (même carter), arbres de transmission (cardans), roue avant ; une flèche de mouvement s'allume à chaque étape quand la voix la nomme.
- voiceover: "Tout part du moteur : les pistons font tourner le vilebrequin. L'embrayage relie ou sépare le moteur et la boîte. La boîte de vitesses échange de la vitesse contre de la force. Le différentiel partage la rotation entre gauche et droite, pour les virages. Les cardans l'amènent aux roues avant… et la roue transforme la rotation en déplacement."
- duration: 20.124s
- transition_in: push-slide LEFT
- status: built
- src: compositions/frames/03-transmission.html
- type: feature_showcase
- persuasion: Causal chain + progressive disclosure
- beat: Comprehension + momentum
- blueprint: spatial-pan-stations

narrativeRole: Montre d'où vient la rotation que le compteur va compter, maillon par maillon, sur une scène unique où les flèches s'allument dans l'ordre.
keyMessage: La rotation du moteur arrive jusqu'aux roues, et c'est la roue qui fait avancer la voiture.

## Frame 4 — Le capteur compte les tours

- scene: Zoom sur la roue avant : couronne dentée + capteur ABS ; à chaque tour, des impulsions filent par un câble vers un boîtier « calculateur », puis vers le compteur du tableau de bord ; un compteur « tours » s'incrémente.
- voiceover: "Ici, le capteur ABS compte les tours de roue, et envoie l'info au calculateur… puis au compteur."
- duration: 6.31s
- transition_in: zoom-through
- status: built
- src: compositions/frames/04-capteur.html
- type: feature_showcase
- persuasion: Demonstration (show the mechanism running)
- beat: "Aha"
- blueprint: none — compose (signal path roue → calculateur → compteur)

narrativeRole: Relie la roue au compteur : l'information qui remonte est un nombre de tours, pas une vitesse.
keyMessage: Le compteur ne reçoit qu'un nombre de tours de roue.

## Frame 5 — Le calcul du compteur

- scene: Flanc de pneu « 195/55 R16 » décomposé (195 largeur, 55 série, R16 jante) → formule du diamètre avec les valeurs → 621 mm ; la roue se déroule sur une ligne de 1,95 m ; puis la formule de la vitesse réelle s'écrit en bas.
- voiceover: "Le compteur multiplie ces tours par la circonférence d'origine. Pneu d'origine : 621 millimètres de diamètre, soit 1,95 mètre par tour. Changer de roues change donc la vitesse réelle… dans le rapport des diamètres."
- duration: 15.24s
- transition_in: crossfade
- status: built
- src: compositions/frames/05-calcul.html
- type: feature_showcase
- persuasion: Worked example with real numbers
- beat: Comprehension + confidence
- blueprint: none — compose (formules qui se remplissent)

narrativeRole: Donne la règle de calcul avec les vrais chiffres du pneu d'origine, et les deux formules du brief.
keyMessage: Vitesse affichée = tours × 1,95 m ; vitesse réelle = vitesse affichée × (diamètre nouveau / diamètre d'origine).

On screen (mot pour mot) : « Diamètre = (jante en pouces × 25,4) + 2 × (largeur × série / 100) » → (16 × 25,4) + 2 × (195 × 55 / 100) = 406,4 + 214,5 ≈ 621 mm → circonférence ≈ 1,95 m par tour. « Vitesse réelle = vitesse affichée × (diamètre nouveau / diamètre d'origine) ».

## Frame 6 — Petite roue, grande roue

- scene: Deux roues côte à côte au-dessus d'une règle graduée : la petite (583 mm) et la grande (724 mm) font chacune exactement 1 tour ; la grande s'arrête plus loin (1,83 m contre 2,27 m) ; au-dessus, le compteur affiche « 1 tour » pour les deux ; puis deux cartes : roue plus grande → vitesse réelle SUPÉRIEURE (rouge), roue plus petite → INFÉRIEURE.
- voiceover: "Chaque roue fait un tour : la grande va plus loin. Mais le compteur compte « un tour »… dans les deux cas. Roue plus grande : tu roules plus vite qu'affiché. Plus petite : moins vite."
- duration: 10.607s
- transition_in: push-slide LEFT
- status: built
- src: compositions/frames/06-comparaison.html
- type: benefit_highlight
- persuasion: Comparison of two options + demonstration
- beat: "Aha" + delight
- blueprint: comparison-split

narrativeRole: Rend la conséquence visible : même nombre de tours, distance différente — donc vitesse différente de l'affichage.
keyMessage: Roue plus grande → vitesse réelle supérieure à l'affichage ; roue plus petite → inférieure.

## Frame 7 — Karim est serein

- scene: Rue en ville, panneau « 60 ». La Fiesta de Karim, montée en grandes roues « 225/65 R17 » (étiquette « dimension hypothétique »), passe ; gros plan sur son compteur : l'aiguille se cale sur 60. Un policier au bord de la route lève son radar : l'écran affiche 70.
- voiceover: "Karim a monté de grandes roues. Son compteur indique 60 : il est serein."
- duration: 5.854s
- transition_in: crossfade
- status: built
- src: compositions/frames/07-karim.html
- type: social_proof
- persuasion: Worked example (story case) + before/after setup
- beat: Calm → tension
- blueprint: none — compose (rue + compteur 60 + radar 70)

narrativeRole: Passe de la règle au cas concret : le compteur dit 60 alors que le radar mesure 70.
keyMessage: Avec ses grandes roues, Karim roule à 70 en croyant rouler à 60.

## Frame 8 — Le contrôle

- scene: Karim arrêté au bord de la route ; le policier et lui échangent en bulles de BD, une réplique après l'autre ; à la fin, Karim baisse les yeux vers ses grandes roues.
- voiceover: "« Bonjour monsieur, vous rouliez à 70 km/h dans une zone limitée à 60. » « Impossible ! Mon compteur indiquait exactement 60, j'en suis sûr ! » « Votre compteur est réglé pour les roues d'origine. Avec des roues plus grandes, chaque tour vous fait parcourir plus de distance. Le radar, lui, mesure votre vitesse réelle. »"
- duration: 21.631s
- transition_in: cut
- status: built
- src: compositions/frames/08-controle.html
- type: social_proof
- persuasion: Common-belief vs reality (dialogue)
- beat: Tension → recognition
- blueprint: none — compose (dialogue en bulles)

narrativeRole: Fait dire l'explication par le personnage qui a la vraie mesure — le radar — face à la croyance de Karim.
keyMessage: Le compteur est réglé pour les roues d'origine ; le radar mesure la vitesse réelle.

Dialogue (mot pour mot, bulles) :
- Policier : « Bonjour monsieur, vous rouliez à 70 km/h dans une zone limitée à 60. »
- Karim : « Impossible ! Mon compteur indiquait exactement 60, j'en suis sûr ! »
- Policier : « Votre compteur est réglé pour les roues d'origine. Avec des roues plus grandes, chaque tour vous fait parcourir plus de distance. Le radar, lui, mesure votre vitesse réelle. »

## Frame 9 — Le tableau

- scene: Titre « Compteur affiché : 60 km/h – Ford Fiesta 2023 (référence 195/55 R16) » ; tableau 4 colonnes (Pneu · Diamètre · Écart · Vitesse réelle) dont les 8 lignes arrivent une par une ; les vitesses réelles au-dessus de 60 passent en rouge ; la ligne 225/65 R17 (Karim, 70,0) est soulignée ; la note s'affiche en bas.
- voiceover: "Pour 60 au compteur : 56 en vrai avec de petites roues… 70 avec celles de Karim… et 73,5 avec les plus grandes."
- duration: 11.123s
- transition_in: crossfade
- status: built
- src: compositions/frames/09-tableau.html
- type: social_proof
- persuasion: Statistical proof (worked table)
- beat: Conviction
- blueprint: grid-card-assemble

narrativeRole: Généralise le cas de Karim à toutes les tailles de pneus avec les chiffres exacts.
keyMessage: Plus le pneu est grand, plus la vitesse réelle dépasse les 60 affichés.

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
- status: built
- src: compositions/frames/10-conclusion.html
- type: cta
- persuasion: Rule of three + distillation (callback to the title)
- beat: Clarity + resolve
- blueprint: kinetic-type-beats

narrativeRole: Transforme la compréhension en gestes concrets, puis condense toute la vidéo en une phrase.
keyMessage: Ton compteur compte des tours, le radar mesure la réalité.

On screen (mot pour mot) :
1. Respecter les dimensions de pneus homologuées (voir carte grise / notice).
2. Vérifier sa vitesse avec le GPS du téléphone après un changement de roues.
3. Faire recalibrer le compteur chez un professionnel si nécessaire.
