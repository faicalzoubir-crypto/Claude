---
format: 1080x1920
fps: 30
duration: 22s
message: "Alpha Square prépare les élèves de 1ère et 2ème Bac en cours du soir : appelez le 05 22 81 00 88 pour vous inscrire."
audience: "Élèves de 1ère Bac et 2ème Bac, et leurs parents"
arc: accroche → marque → offre 1ère Bac → offre 2ème Bac → atouts → appel à l'action
mode: autonomous
---

Une seule composition (`index.html`), une `<section class="clip">` par scène, une timeline GSAP en pause.
Zones sûres : aucun texte important au-dessus de y = 150 ni en dessous de y = 1670.
Transitions : coup de pinceau or (ouverture), poussée latérale (transitions principales, 0,4 s), flash blanc par surexposition (entrée de l'appel à l'action).

## Frame 1 — Accroche

- scene: « Prêt pour ton Bac ? » mot par mot, plein écran, fond marine, formes or animées
- duration: 3s
- poster: 2s
- transition_in: cut
- status: animated
- src: index.html#s1
- motion: waterfall-entry (mots), spring-pop-entrance (« Bac ? »), svg-path-draw (soulignement pinceau), sine-wave-loop (formes)

Quatre mots arrivent l'un après l'autre (0,2 / 0,55 / 0,9 / 1,25 s) ; « Bac ? » en or, le plus lourd. Un trait de pinceau or se peint sous « Bac ». Anneaux, disques et touches de pinceau or dérivent en continu.

## Frame 2 — Marque

- scene: logo en zoom doux, puis « Centre de formation & cours du soir » sur bandeau pinceau marine, puis « Réussite · Progression · Accompagnement »
- duration: 3s
- poster: 5.5s
- transition_in: brush-wipe
- status: animated
- src: index.html#s2
- motion: spring-pop-entrance (logo, calme), bandeau peint par clip-path, waterfall-entry (trois valeurs)

## Frame 3 — 1ère BAC

- scene: grande carte bleue « 1ère BAC », quatre lignes en cascade avec icônes (Français, Arabe, Histoire-Géographie, Instruction islamique)
- duration: 5s
- poster: 10s
- transition_in: push-left
- status: animated
- src: index.html#s3
- motion: waterfall-entry (lignes), spring-pop-entrance (icônes), svg-path-draw (soulignement)

## Frame 4 — 2ème BAC

- scene: carte orange « 2ème BAC », quatre lignes en cascade avec icônes (Maths, Physique-Chimie, SVT, Philosophie)
- duration: 5s
- poster: 15s
- transition_in: push-left
- status: animated
- src: index.html#s4
- motion: identique à la scène 3 pour la cohérence

## Frame 5 — Atouts

- scene: trois pastilles qui s'animent l'une après l'autre : Petits groupes · Suivi personnalisé · Examens blancs
- duration: 3s
- poster: 18.5s
- transition_in: push-left
- status: animated
- src: index.html#s5
- motion: spring-pop-entrance (pastilles, une par une), sine-wave-loop (icônes)

## Frame 6 — Appel à l'action

- scene: bandeau pinceau or « INSCRIPTIONS OUVERTES ! », téléphone très grand avec icône d'appel qui pulse, adresse, logo en bas
- duration: 3s
- poster: 21.5s
- transition_in: flash-white
- status: animated
- src: index.html#s6
- motion: bandeau peint par clip-path, spring-pop-entrance (téléphone), anneaux d'appel en boucle finie
