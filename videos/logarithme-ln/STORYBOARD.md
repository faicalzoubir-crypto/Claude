---
format: 1080x1920
duration: 107s
message: "ln est la réciproque de exp : sa courbe est le reflet de e^x, elle transforme les produits en sommes, sa dérivée vaut 1/x, et elle monte vers +∞ très lentement."
arc: concept-explainer with process (réciproque → propriétés → dérivée → limites)
audience: "Élèves de 2ème Bac sciences (ou Terminale)"
mode: collaborative
music: none
---

## Video direction

- **Palette** (frame.md) : fond anthracite + grille très légère ; formules en blanc cassé ; titres et étiquettes gris ; cuivre réservé à la courbe de ln, à sa tangente, aux résultats clés et à la signature ; eˣ en pointillés blancs, y = x en gris pointillé.
- **Grammaire de mouvement** : comme exponentielle-e : fondus montants (power3.out), traits qui se tracent, tangentes et points synchronisés sur les répliques (tools/timing.json) ; aucune sortie, les transitions font les sorties.
- **Respirations** : fin des plans 3, 4, 5, 6 (≈ 1,6 s) et la signature finale.
- **Rigueur** : toute valeur approchée s'écrit avec « ≈ », jamais « = ».

<!-- music: none — fond musical composé localement (tools/music.py --sans-voix pour la version livrée), déclaré dans audio_meta.json comme bgm "source": "host". -->

## Frame 1 — La question

- act: Accroche
- scene: « eˣ = 5 » puis « x = ln 5 ≈ 1,609 » ; segments et curseur
- voiceover: "Si e puissance x égale cinq, combien vaut x ? La réponse a un nom : le logarithme népérien, ln."
- duration: 7.479s
- transition_in: cut
- status: animated
- src: compositions/frames/01-la-question.html
- type: hook
- persuasion: Rhetorical question + concept announcement
- beat: Curiosité
- blueprint: kinetic-type-beats

narrativeRole: Pose la question qui donne naissance à ln et la nomme tout de suite.
keyMessage: ln 5 est le nombre dont l'exponentielle vaut 5 (≈ 1,609).

## Frame 2 — Quatre idées

- act: Accroche
- scene: Registre 01–04 : y = ln x ⟺ x = eʸ · ln(ab) = ln a + ln b · (ln x)′ = 1/x · lim ln x = +∞
- voiceover: "Quatre idées : la réciproque, les produits, la dérivée, les limites."
- duration: 6.18s
- transition_in: crossfade
- status: animated
- src: compositions/frames/02-quatre-idees.html
- type: product_intro
- persuasion: Frame-then-fill + signposting
- beat: Orientation
- blueprint: grid-card-assemble

narrativeRole: Annonce les quatre idées dans l'ordre du film.
keyMessage: Réciproque, produits, dérivée, limites.

## Frame 3 — Réciproque

- act: 1. Réciproque
- scene: Repère : eˣ en pointillés blancs, droite y = x grise ; la courbe de eˣ se retourne autour de y = x et devient ln (cuivre) ; (0 ; 1) ↔ (1 ; 0) et (1 ; e) ↔ (e ; 1) ; « y = ln x ⟺ x = eʸ (x > 0) », « ln 1 = 0 », « ln e = 1 »
- voiceover: "Pour x strictement positif, y égale ln x signifie x égale e puissance y. La courbe de ln est le reflet de celle de e puissance x par rapport à la droite y égale x. Le point zéro, un devient un, zéro : ln de un vaut zéro. Le point un, e devient e, un : ln de e vaut un."
- duration: 20.197s
- transition_in: push-slide LEFT
- status: animated
- src: compositions/frames/03-reciproque.html
- type: feature_showcase
- persuasion: Demonstration (symétrie) + worked example
- beat: « Aha »
- blueprint: compose

narrativeRole: Définit ln comme réciproque de exp et le montre par la symétrie des courbes.
keyMessage: La courbe de ln est le reflet de celle de eˣ par rapport à y = x ; ln 1 = 0, ln e = 1.

## Frame 4 — Produits en sommes

- act: 2. Propriétés
- scene: « ln(ab) = ln a + ln b » ; barres cuivre ln 2 ≈ 0,693 et ln 3 ≈ 1,099 mises bout à bout = barre ln 6 ≈ 1,792 ; puis ln(a/b) = ln a − ln b et ln(aⁿ) = n ln a
- voiceover: "ln transforme les produits en sommes : ln de a fois b égale ln a plus ln b. Par exemple, ln deux plus ln trois donne ln six : environ zéro virgule six neuf trois, plus un virgule zéro neuf neuf, soit un virgule sept neuf deux. On en déduit : ln de a sur b égale ln a moins ln b, et ln de a puissance n égale n ln a."
- duration: 23.452s
- transition_in: push-slide LEFT
- status: animated
- src: compositions/frames/04-produits-en-sommes.html
- type: feature_showcase
- persuasion: Worked example with real numbers + concretization
- beat: Compréhension
- blueprint: compose

narrativeRole: Montre la propriété fondamentale avec un exemple chiffré visible (barres).
keyMessage: ln transforme les produits en sommes.

## Frame 5 — La dérivée

- act: 3. Dérivée
- scene: Repère : ln en cuivre ; le point glisse x = 1 → 2 → 1/2 ; compteurs x et pente (1 ; 0,5 ; 2) ; puis la preuve : e^(ln x) = x ⇒ (ln x)′ × x = 1 ⇒ (ln x)′ = 1/x
- voiceover: "Faisons glisser la tangente sur la courbe de ln. En x égal un, la pente vaut un ; en x égal deux, un demi ; en x égal un demi, deux. La pente vaut toujours un sur x. Preuve : en dérivant e puissance ln x égale x, on obtient ln prime de x fois x égale un. Donc la dérivée de ln x est un sur x."
- duration: 21.478s
- transition_in: push-slide LEFT
- status: animated
- src: compositions/frames/05-la-derivee.html
- type: feature_showcase
- persuasion: Demonstration + causal chain
- beat: Fascination + conviction
- blueprint: compose

narrativeRole: Fait voir puis prouve que la pente de ln en x vaut 1/x.
keyMessage: (ln x)′ = 1/x pour x > 0.

## Frame 6 — Limites et variations

- act: 4. Limites
- scene: Tableau de variations (x : 0, 1, +∞ ; (ln x)′ = 1/x : + ; ln x : −∞ ↗ 0 ↗ +∞), les deux limites, puis « ln(1 000 000) ≈ 13,8 »
- voiceover: "Un sur x est positif, donc ln est strictement croissante. Quand x tend vers zéro, ln x tend vers moins l'infini. Quand x tend vers plus l'infini, ln x tend vers plus l'infini, mais très lentement : ln d'un million vaut seulement environ treize virgule huit."
- duration: 17.341s
- transition_in: push-slide LEFT
- status: animated
- src: compositions/frames/06-limites-et-variations.html
- type: benefit_highlight
- persuasion: Signposting + counterintuitive claim (très lentement)
- beat: Surprise
- blueprint: compose

narrativeRole: Tire les variations de la dérivée et montre la lenteur de la croissance.
keyMessage: ln est strictement croissante, de −∞ à +∞, mais très lentement.

## Frame 7 — Voilà ln

- act: Fin
- scene: Les trois formules clés, puis la signature « Faïçal Zoubir » qui s'écrit
- voiceover: "Réciproque de l'exponentielle, produits en sommes, dérivée un sur x : voilà ln."
- duration: 10.664s
- transition_in: crossfade
- status: animated
- src: compositions/frames/07-voila-ln.html
- type: branding
- persuasion: Distillation + callback
- beat: Satisfaction
- blueprint: titlecard-reveal

narrativeRole: Résume ln en trois formules et signe la vidéo.
keyMessage: Réciproque de exp, produits en sommes, dérivée 1/x.
