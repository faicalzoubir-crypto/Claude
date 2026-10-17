---
format: 1080x1920
duration: 90s
message: "e ≈ 2,71828 est la limite de (1+1/n)^n ; c'est aussi la base, entre 2 et 3, dont la courbe a une pente de 1 en x = 0 ; c'est pour cela que (e^x)' = e^x."
arc: concept-explainer with process (une limite → deux courbes → une dérivée)
audience: "Élèves de 2ème Bac sciences (ou Terminale)"
mode: collaborative
music: none
---

## Video direction

- **Palette** (frame.md, surcharge « couleurs de Claude ») : fond crème #F5F0E8 + grille très légère ; formules et titres en noir chaud #1F1A17 ; orange terre cuite #CC6E50 réservé au nombre e, à la courbe eˣ et à sa tangente, aux étiquettes et à la signature ; encadrés de résultat pêche arrondis ; barres en segments arrondis orange clair.
- **Grammaire de mouvement** : apparitions en fondu montant (power3.out, ~0,7 s), traits qui se tracent de gauche à droite, tangentes qui s'ouvrent depuis le point de contact, barres qui poussent ; chaque élément arrive sur la réplique qui le nomme (instants exacts dans tools/timing.json). Aucune sortie : les transitions (fondu enchaîné, glissement vers la gauche entre les parties) font les sorties.
- **Respirations** : fin du plan 3 (encadré de la limite), fin du plan 4 (« 2 < e < 3 »), fin du plan 6 (résultat encadré) et la signature finale sont tenues 1,8 à 3 s.
- **À éviter** : tout afficher d'un coup puis figer ; éléments qui flottent sans raison ; une deuxième couleur vive ; le logo de Claude.

<!-- music: none — le fond musical est composé localement (tools/music.py) et déclaré dans audio_meta.json comme bgm "source": "host". -->

## Frame 1 — Le secret

- act: Accroche
- scene: « f ' = f » posé en grand sur la grille, puis « e ≈ 2,71828… » se tape chiffre par chiffre dessous
- voiceover: "Il existe une fonction égale à sa propre dérivée. Tout son secret tient dans un seul nombre : e."
- duration: 6.816s
- transition_in: cut
- status: animated
- src: compositions/frames/01-le-secret.html
- type: hook
- persuasion: Counterintuitive claim + concept announcement
- beat: Curiosité + intrigue
- blueprint: kinetic-type-beats

Shot : barre segmentée + curseur qui avance tout le plan (lecture) ; « f ′ = f » monte sur « Il existe une fonction… », l'annotation orange suit ; sur « Tout son secret… » le filet orange se trace, « e ≈ » puis les chiffres 2,71828… s'écrivent un à un ; sur « e » final, le e orange pulse et « LE NOMBRE e » apparaît.

narrativeRole: Ouvre la question (une fonction qui est sa propre dérivée ?) et nomme tout de suite le héros, le nombre e.
keyMessage: Tout tient dans un seul nombre, e ≈ 2,718.

## Frame 2 — Trois chemins

- act: Accroche
- scene: Trois lignes numérotées façon registre : 01 lim (1 + 1/n)ⁿ · 02 2ˣ et 3ˣ · 03 (eˣ)' = eˣ, qui arrivent l'une après l'autre
- voiceover: "Découvrons-le de trois façons : une limite, deux courbes, puis une dérivée."
- duration: 6.067s
- transition_in: crossfade
- status: animated
- src: compositions/frames/02-trois-chemins.html
- type: product_intro
- persuasion: Frame-then-fill + signposting
- beat: Orientation
- blueprint: grid-card-assemble

Shot : titre, puis une ligne du registre sur chaque mot : « une limite » → 01, « deux courbes » → 02, « une dérivée » → 03.

narrativeRole: Annonce le plan de la vidéo, dans l'ordre demandé, pour que l'élève sache où il va.
keyMessage: On va voir e de trois façons : une limite, deux courbes, une dérivée.

## Frame 3 — La limite

- act: 1. La limite
- scene: Formule uₙ = (1 + 1/n)ⁿ en haut ; un tableau n | uₙ se remplit (1 → 2 ; 2 → 2,25 ; 3 → 2,370 ; 10 → 2,594 ; 100 → 2,705 ; 1000 → 2,717 ; 10⁶ → 2,71828) ; en bas, des points carrés montent vers la droite pointillée y = e ; conclusion « lim (1 + 1/n)ⁿ = e ≈ 2,71828 »
- voiceover: "Prenons un plus un sur n, puissance n. Pour n égal un : deux. Pour n égal deux : deux virgule vingt-cinq. Pour n égal trois : environ deux virgule trente-sept. Puis dix, cent, mille, un million… La suite grandit de moins en moins, et se rapproche d'une limite : le nombre e, environ deux virgule sept, un, huit, deux, huit."
- duration: 23.006s
- transition_in: push-slide LEFT
- status: animated
- src: compositions/frames/03-la-limite.html
- type: feature_showcase
- persuasion: Worked example with real numbers + progressive disclosure
- beat: Compréhension + fascination
- blueprint: dataviz-countup

Shot : formule uₙ ; en-tête du tableau et ligne pointillée orange « e » qui descend ; chaque ligne n arrive quand la voix dit n, sa valeur et sa barre quand la voix dit la valeur ; sur « se rapproche d'une limite », le e de la ligne pulse ; sur « le nombre e », l'encadré pêche monte, puis « e ≈ 2,71828… ».

narrativeRole: Donne la première définition de e par le calcul : chaque valeur de n ajoute une ligne au tableau et un point au graphique, jusqu'à la limite.
keyMessage: (1 + 1/n)ⁿ augmente de moins en moins et tend vers e ≈ 2,71828 quand n tend vers +∞.

## Frame 4 — Entre 2 et 3

- act: 2. Deux courbes
- scene: Un repère sur la grille ; 2ˣ et 3ˣ se tracent en pointillés fins ; le point (0 ; 1) ; leurs tangentes en 0 avec « pente ≈ 0,69 » et « pente ≈ 1,10 » ; puis eˣ se trace en trait épais entre les deux, avec sa tangente y = x + 1 et « pente = 1 » ; encart « 2 < e < 3 »
- voiceover: "Traçons deux puissance x et trois puissance x. Les deux courbes passent par le point zéro, un. Là, la pente de deux puissance x vaut environ zéro virgule soixante-neuf. Celle de trois puissance x, environ un virgule dix. Entre les deux, une seule base donne une pente exactement égale à un : c'est e, le même nombre que notre limite."
- duration: 21.746s
- transition_in: push-slide LEFT
- status: animated
- src: compositions/frames/04-entre-2-et-3.html
- type: feature_showcase
- persuasion: Comparison of two options + build-up (encadrement)
- beat: « Aha » + clarté
- blueprint: none — composé (tracé de courbes)

Shot : repère, 2ˣ puis 3ˣ se tracent (pointillés noirs) ; le point (0 ; 1) apparaît ; tangente de 2ˣ + ligne de légende puis « ≈ 0,69 » ; tangente de 3ˣ + « ≈ 1,10 » ; eˣ se trace en orange entre les deux, sa tangente orange s'ouvre, la ligne du milieu « = 1 » complète la légende ; « 2 < e < 3 » et « e = lim (1 + 1/n)ⁿ ».

narrativeRole: Deuxième regard sur e : par les courbes, e est la base entre 2 et 3 dont la pente en 0 vaut exactement 1, et c'est le même nombre que la limite.
keyMessage: La courbe de eˣ est la seule exponentielle dont la tangente en 0 a une pente de 1.

## Frame 5 — La tangente glisse

- act: 3. Une dérivée
- scene: Même repère, la courbe eˣ seule ; un point carré glisse de x = −1 à x = 1,2 ; la tangente le suit ; deux compteurs « hauteur eˣ » et « pente » affichent toujours la même valeur (0,37 … 1 … 2,72)
- voiceover: "Sur la courbe de e puissance x, faisons glisser la tangente. Partout, sa pente est égale à la hauteur du point. En x égal un, la pente vaut e."
- duration: 9.65s
- transition_in: crossfade
- status: animated
- src: compositions/frames/05-la-tangente-glisse.html
- type: feature_showcase
- persuasion: Demonstration (show the mechanism running)
- beat: Fascination
- blueprint: none — composé (tangente animée)

Shot : même repère, eˣ seule ; les compteurs HAUTEUR et PENTE apparaissent ; le point glisse de x = −1,5 à 1,45 puis revient à x = 1 ; tangente et pointillé vertical le suivent ; les deux compteurs affichent toujours la même valeur ; « = e » s'ajoute sous « En x égal un, la pente vaut e ».

narrativeRole: Montre en mouvement que la pente de eˣ en chaque point est égale à sa hauteur, avant de le prouver.
keyMessage: En tout point de la courbe de eˣ, pente = hauteur.

## Frame 6 — Pourquoi

- act: 3. Une dérivée
- scene: Le calcul en trois lignes : (eˣ⁺ʰ − eˣ) / h = eˣ · (eʰ − 1) / h ; puis (eʰ − 1) / h → 1 quand h → 0 (rappel : la pente en 0) ; puis « (eˣ)' = eˣ » encadré
- voiceover: "Pourquoi ? Le taux d'accroissement s'écrit e puissance x, fois e puissance h moins un, sur h. Quand h tend vers zéro, ce quotient tend vers un : c'est la pente en zéro. Donc la dérivée de l'exponentielle, c'est l'exponentielle."
- duration: 15.889s
- transition_in: crossfade
- status: animated
- src: compositions/frames/06-pourquoi.html
- type: benefit_highlight
- persuasion: Causal chain + callback (la pente 1 de la partie 2)
- beat: Conviction
- blueprint: none — composé (calcul ligne à ligne)

Shot : chaque ligne du calcul arrive sur sa phrase (taux d'accroissement, factorisation, limite quand h → 0) ; le rappel orange « c'est la pente de eˣ en 0 » sur « c'est la pente en zéro » ; l'encadré (eˣ)′ = eˣ sur « Donc… ».

narrativeRole: Prouve le résultat avec le taux d'accroissement, en réutilisant la pente 1 en 0 vue avec les courbes.
keyMessage: (eˣ⁺ʰ − eˣ)/h = eˣ · (eʰ − 1)/h → eˣ · 1, donc (eˣ)' = eˣ.

## Frame 7 — Un seul nombre

- act: Fin
- scene: Les trois chemins se resserrent sur « e ≈ 2,71828 » et « (eˣ)' = eˣ » ; la signature « Z.Faïçal » apparaît en bas
- voiceover: "Une limite, deux courbes, une dérivée : un seul nombre, e."
- duration: 6.862s
- transition_in: crossfade
- status: animated
- src: compositions/frames/07-un-seul-nombre.html
- type: branding
- persuasion: Distillation + callback (retour à l'accroche)
- beat: Satisfaction
- blueprint: titlecard-reveal

Shot : barre segmentée ; LIMITE · COURBES · DÉRIVÉE mot par mot ; (eˣ)′ = eˣ ; « e ≈ 2,71828… » sur « un seul nombre, e », le e pulse ; filet orange et signature « Z.Faïçal » tenus jusqu'à la fin.

narrativeRole: Referme la boucle de l'accroche : les trois chemins mènent au même nombre ; la vidéo est signée.
keyMessage: Une limite, deux courbes, une dérivée : un seul nombre, e.
