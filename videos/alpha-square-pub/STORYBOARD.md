---
format: 1080x1920
fps: 30
duration: 26s
message: "Alpha Square prépare les élèves de 1ère et 2ème Bac en cours du soir : appelez le 05 22 81 00 88 pour vous inscrire."
audience: "Élèves de 1ère Bac et 2ème Bac, et leurs parents"
arc: accroche → marque → offre 1ère Bac → offre 2ème Bac → atouts → où nous trouver (vidéo du lieu) → appel à l'action
mode: autonomous
---

Une seule composition (`index.html`), une `<section class="clip">` par scène, une timeline GSAP en pause.
Zones sûres : aucun texte important au-dessus de y = 150 ni en dessous de y = 1670.
Voix : Kokoro ff_siwis, vitesse 1,0 (comme EN-NOUR 3), post-traitée par tools/voice_post.py (question montante sur « Bac ? »). Calage commun : tools/timing.json et l'objet T de index.html.
Transitions : coup de pinceau or (ouverture), poussée latérale (transitions principales, 0,4 s, y compris vers la carte), flash blanc par surexposition (carte → appel à l'action).

## Frame 1 — Accroche

- scene: « Prêt pour ton Bac ? » mot par mot, plein écran, fond marine, formes or animées
- duration: 3s
- voiceover: 0–3 s · voix : « Prêt pour ton Bac ? » lu comme une question, intonation montante (0,58 s ; « Bac » à 1,18 s)
- poster: 2s
- transition_in: cut
- status: animated
- src: index.html#s1
- motion: waterfall-entry (mots), spring-pop-entrance (« Bac ? »), svg-path-draw (soulignement pinceau), sine-wave-loop (formes)

Quatre mots arrivent l'un après l'autre (0,2 / 0,55 / 0,9 / 1,25 s) ; « Bac ? » en or, le plus lourd. Un trait de pinceau or se peint sous « Bac ». Anneaux, disques et touches de pinceau or dérivent en continu.

## Frame 2 — Marque

- scene: logo en zoom doux, puis « Centre de formation & cours du soir » sur bandeau pinceau marine, puis « Réussite · Progression · Accompagnement »
- duration: 3.46s
- voiceover: 3–6,46 s · voix : « Alpha Square, centre de formation et cours du soir. » (3,12 s)
- poster: 5.5s
- transition_in: brush-wipe
- status: animated
- src: index.html#s2
- motion: spring-pop-entrance (logo, calme), bandeau peint par clip-path, waterfall-entry (trois valeurs)

## Frame 3 — 1ère BAC

- scene: grande carte bleue « 1ère BAC », quatre lignes en cascade avec icônes (Français, Arabe, Histoire-Géographie, Instruction islamique)
- duration: 4.4s
- voiceover: 6,06–10,46 s · voix : « En première Bac, l'examen régional. » (6,41 s) ; badge « Examen régional » à 7,47 s
- poster: 9.5s
- transition_in: push-left
- status: animated
- src: index.html#s3
- motion: waterfall-entry (lignes), spring-pop-entrance (icônes), svg-path-draw (soulignement)

## Frame 4 — 2ème BAC

- scene: carte orange « 2ème BAC », quatre lignes en cascade avec icônes (Maths, Physique-Chimie, SVT, Philosophie)
- duration: 4.4s
- voiceover: 10,06–14,46 s · voix : « En deuxième Bac, l'examen national. » (10,51 s) ; badge « Examen national » à 11,55 s
- poster: 13.5s
- transition_in: push-left
- status: animated
- src: index.html#s4
- motion: identique à la scène 3 pour la cohérence

## Frame 5 — Atouts

- scene: trois pastilles qui s'animent l'une après l'autre : Petits groupes · Suivi personnalisé · Examens blancs
- duration: 3.58s
- voiceover: 14,06–17,64 s · voix : « Petits groupes, suivi personnalisé, examens blancs. » (14,51 s) ; pastilles à 14,51 / 15,61 / 16,39 s
- poster: 17s
- transition_in: push-left
- status: animated
- src: index.html#s5
- motion: spring-pop-entrance (pastilles, une par une), sine-wave-loop (icônes)

## Frame 6 — Où nous trouver (vidéo du lieu vue du ciel)

- scene: vidéo Google Earth du lieu fournie par le client (descente sur la ville depuis la mosquée Hassan II, puis orbite autour du point), en plein écran 1080×1920 ; repère or avec le logo posé sur le repère Google
- duration: 4.05s
- voiceover: 17,24–21,29 s · voix : « Retrouve-nous au centre de Casablanca. » (17,74 s) ; « Emplacement approximatif » affiché (non dit) à 19,14 s
- poster: 20.5s
- transition_in: push-left
- status: animated
- src: index.html#smap (vidéo : #smap-video dans #smap-footage, hors de la section chronométrée)
- motion: vidéo lue de 0 à 4,05 s ; repère avec logo qui tombe du ciel à 18,04 s et se pose sur le repère Google, bandeau peint

Vidéo : assets/footage/lieu-google-earth.mp4, préparée par tools/prep_footage.py à partir de assets/footage/source/lieu-google-earth.mov (coupée avant le carton CapCut, étiquette de coordonnées effacée, recadrée sans les boutons de l'application). Crédit affiché : « Images : Google Earth ».

## Frame 7 — Appel à l'action

- scene: bandeau pinceau or « INSCRIPTIONS OUVERTES ! », téléphone très grand avec icône d'appel qui pulse, adresse, logo en bas
- duration: 4.71s
- voiceover: 21,29–26 s · voix : « Inscriptions ouvertes ! Contactez-nous. » (21,44 s) ; chiffres en or l'un après l'autre à partir de 22,59 s
- poster: 25.5s
- transition_in: flash-white
- status: animated
- src: index.html#s6
- motion: bandeau peint par clip-path, spring-pop-entrance (téléphone), anneaux d'appel en boucle finie
