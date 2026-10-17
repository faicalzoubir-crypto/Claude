---
workflow: faceless-explainer
flow: automation
storyboard: yes
message: "e ≈ 2,71828 est la limite de (1+1/n)^n ; c'est aussi la base, entre 2 et 3, dont la courbe a une pente de 1 en x = 0 ; c'est pour cela que (e^x)' = e^x."
destination: instagram-reels
aspect: 1080x1920
language: fr
audience: "Élèves de 2ème Bac sciences (ou Terminale) ; notation française : exp, e^x, lim."
length: 90s
angle: concept (explication en 3 parties, dans l'ordre demandé)
narration: yes
style_preset: cobalt-grid
voice: ff_siwis
---

## Intent

Demande de l'utilisateur, mot pour mot : « Prompt pour une video explicative de la fonction exponentielle et la valeur de e, de la formule lim(1+1/n)^n du n=1 jusqu'à plus l inf. Puis par les courbes de fonction 2^x et 3^x. Enfin une partie pour que la derive de l exp c exp ».

Vidéo explicative de maths, verticale pour Reels / TikTok, environ 90 s, en français. Trois parties dans cet ordre :

1. La valeur de e : la suite (1+1/n)^n pour n = 1, 2, 3, 10, 100, 1000, 10^6 donne 2 ; 2,25 ; 2,370 ; 2,594 ; 2,705 ; 2,717 ; 2,71828… Les points montent vers la droite y = e.
2. Les courbes de 2^x et 3^x et leur tangente en 0 : pente ≈ 0,69 pour 2^x, ≈ 1,10 pour 3^x. Entre les deux, une seule base donne une pente de exactement 1 : c'est e, et la courbe e^x apparaît entre les deux.
3. La dérivée de exp est exp : une tangente glisse le long de e^x et sa pente reste égale à la hauteur ; preuve courte (e^(x+h) − e^x)/h = e^x · (e^h − 1)/h → e^x · 1, grâce à la partie 2.

Accroche d'environ 5 s au début, plan de fin d'environ 5 s avec e ≈ 2,71828 et la signature.

## Customizations

- Style Cobalt Grid choisi sur image (mise en page, grille, typographie). Couleurs : d'abord « façon Claude » (crème, noir chaud, terre cuite), puis **palette sombre retenue par l'utilisateur** d'après une référence d'équations : fond anthracite #1E1E1E, formules blanc cassé #F2EFE9, titres gris, cuivre #CB7B4F réservé à e, à la courbe e^x et à sa tangente, au point qui glisse et à la signature. 2^x et 3^x en pointillés blancs fins ; chaque courbe avec son nom à côté.
- Voix off : **la voix de l'utilisateur** (validée après un essai sur le plan 1). Le texte est d'abord synthétisé par Kokoro `ff_siwis` (vitesse 1,0, minutage dans tools/timing.json), puis converti vers sa voix par kNN-VC (tools/voice_clone.py) à partir d'un échantillon de ~17 s extrait d'une de ses vidéos ; l'échantillon n'est pas versionné. **Pas de sous-titres** (choix de l'utilisateur) : les formules et valeurs clés restent affichées pour que la vidéo se comprenne sans le son.
- Musique douce en fond, baissée sous la voix.
- Plan de fin signé avec **la signature de l'utilisateur**, reprise de son canevas « Faïçal Zoubir Signature » (https://claude.ai/artifact/3L389kdioJf7WJPjNjC9Gs) : « Faïçal Zoubir » en Mrs Saint Delafield qui s'écrit, paraphe tracé, « فيصل زبير » en Aref Ruqaa entre deux filets ; adaptée au fond sombre (nom blanc cassé, paraphe et arabe cuivre). Remplace le « Z.Faïçal » tapé du début. Plan 7 allongé de 2 s pour la tenir.

## Notes

- Zones libres pour l'interface des Reels : rien d'important dans les 150 px du haut ni les 250 px du bas.
- Français avec tous les accents corrects ; nombres décimaux avec virgule (2,718).
