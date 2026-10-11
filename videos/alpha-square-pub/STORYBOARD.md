---
format: 1080x1920
fps: 30
duration: 28s
message: "Alpha Square prépare les élèves de 1ère et 2ème Bac en cours du soir : appelez le 05 22 81 00 88 pour vous inscrire."
audience: "Élèves de 1ère Bac et 2ème Bac, et leurs parents"
arc: accroche → marque → offre 1ère Bac → offre 2ème Bac → atouts → où nous trouver (carte) → appel à l'action
mode: autonomous
---

Une seule composition (`index.html`), une `<section class="clip">` par scène, une timeline GSAP en pause.
Zones sûres : aucun texte important au-dessus de y = 150 ni en dessous de y = 1670.
Transitions : coup de pinceau or (ouverture), poussée latérale (transitions principales, 0,4 s, y compris vers la carte), flash blanc par surexposition (carte → appel à l'action).

## Frame 1 — Accroche

- scene: « Prêt pour ton Bac ? » mot par mot, plein écran, fond marine, formes or animées
- duration: 3s
- voiceover: 0–3 s · voix : « Prêt pour ton Bac ? » (0,58 s)
- poster: 2s
- transition_in: cut
- status: animated
- src: index.html#s1
- motion: waterfall-entry (mots), spring-pop-entrance (« Bac ? »), svg-path-draw (soulignement pinceau), sine-wave-loop (formes)

Quatre mots arrivent l'un après l'autre (0,2 / 0,55 / 0,9 / 1,25 s) ; « Bac ? » en or, le plus lourd. Un trait de pinceau or se peint sous « Bac ». Anneaux, disques et touches de pinceau or dérivent en continu.

## Frame 2 — Marque

- scene: logo en zoom doux, puis « Centre de formation & cours du soir » sur bandeau pinceau marine, puis « Réussite · Progression · Accompagnement »
- duration: 3.35s
- voiceover: 3–6,35 s · voix : « Alpha Square, centre de formation et cours du soir. » (3,12 s)
- poster: 5.5s
- transition_in: brush-wipe
- status: animated
- src: index.html#s2
- motion: spring-pop-entrance (logo, calme), bandeau peint par clip-path, waterfall-entry (trois valeurs)

## Frame 3 — 1ère BAC

- scene: grande carte bleue « 1ère BAC », quatre lignes en cascade avec icônes (Français, Arabe, Histoire-Géographie, Instruction islamique)
- duration: 5.15s
- voiceover: 5,95–11,1 s · voix : « En première Bac : français, arabe, histoire-géographie et instruction islamique. » (6,3 s)
- poster: 10s
- transition_in: push-left
- status: animated
- src: index.html#s3
- motion: waterfall-entry (lignes), spring-pop-entrance (icônes), svg-path-draw (soulignement)

## Frame 4 — 2ème BAC

- scene: carte orange « 2ème BAC », quatre lignes en cascade avec icônes (Maths, Physique-Chimie, SVT, Philosophie)
- duration: 4.7s
- voiceover: 10,7–15,4 s · voix : « En deuxième Bac : maths, physique-chimie, SVT et philosophie. » (11,15 s)
- poster: 15s
- transition_in: push-left
- status: animated
- src: index.html#s4
- motion: identique à la scène 3 pour la cohérence

## Frame 5 — Atouts

- scene: trois pastilles qui s'animent l'une après l'autre : Petits groupes · Suivi personnalisé · Examens blancs
- duration: 3.45s
- voiceover: 15–18,45 s · voix : « Petits groupes, suivi personnalisé, examens blancs. » (15,45 s) ; pastilles à 15,45 / 16,45 / 17,23 s
- poster: 17.9s
- transition_in: push-left
- status: animated
- src: index.html#s5
- motion: spring-pop-entrance (pastilles, une par une), sine-wave-loop (icônes)

## Frame 6 — Où nous trouver (carte vue du ciel)

- scene: carte 3D vue du ciel, la caméra descend et tourne autour du point comme un drone ; terre en trame de points, mer marine, trait de côte or, zone approximative, repère avec le logo
- duration: 4.35s
- voiceover: 18,05–22,4 s · voix : « Retrouve-nous au centre de Casablanca. Emplacement approximatif. » (18,55 s) ; « Emplacement approximatif » à l'écran à 20,62 s
- poster: 21.8s
- transition_in: push-left
- status: animated
- src: index.html#smap
- motion: caméra en perspective sur canvas 2D (fonction pure du temps), orbite -60° → +10°, altitude 24 km → 3,8 km ; repère qui tombe du ciel, ondes au sol, bandeau peint

Point : 33.5620843, -7.6241886 (emplacement approximatif fourni par le client). Données : © OpenStreetMap contributors (ODbL), via @geo-maps/earth-lands-100m.

## Frame 7 — Appel à l'action

- scene: bandeau pinceau or « INSCRIPTIONS OUVERTES ! », téléphone très grand avec icône d'appel qui pulse, adresse, logo en bas
- duration: 5.6s
- voiceover: 22,4–28 s · voix : « Inscriptions ouvertes ! Appelle le 05 22 81 00 88. » (22,55 s) ; chiffres en or à 24,15 / 24,87 / 25,45 / 26,13 / 26,77 s
- poster: 27s
- transition_in: flash-white
- status: animated
- src: index.html#s6
- motion: bandeau peint par clip-path, spring-pop-entrance (téléphone), anneaux d'appel en boucle finie
