---
workflow: faceless-explainer
flow: automation
storyboard: yes
message: "ln est la réciproque de exp : sa courbe est le reflet de e^x, elle transforme les produits en sommes, sa dérivée vaut 1/x, et elle monte vers +∞ très lentement."
destination: instagram-reels
aspect: 1080x1920
language: fr
audience: "Élèves de 2ème Bac sciences (ou Terminale) ; notation française : ln, exp, e^x."
length: 100s
angle: concept (explication en 4 parties : réciproque, propriétés, dérivée, limites et variations)
narration: yes
style_preset: cobalt-grid
---

## Intent

Demande de l'utilisateur : « Maintenant une video de la fonction Ln(x) », avec les mêmes réglages que la vidéo exponentielle-e (« Oui, tout pareil »). Contenu choisi : ln réciproque de exp, dérivée (ln x)' = 1/x, propriétés ln(ab) = ln a + ln b, limites et variations. Ordre retenu (validé avec le plan) : réciproque → propriétés → dérivée → limites et variations.

Reels / TikTok 9:16, environ 1 min 40 (4 notions : plus que les 90 s de l'exponentielle, validé), en français, toutes les valeurs justes et notées avec ≈ quand elles sont approchées.

## Customizations

- Mêmes réglages que videos/exponentielle-e : mise en page Cobalt Grid, palette sombre (anthracite #1E1E1E, formules blanc cassé #F2EFE9, titres gris, cuivre #CB7B4F), musique douce, pas de sous-titres, formules et valeurs clés affichées.
- Couleurs propres à ce sujet : la courbe de **ln en cuivre** (l'héroïne), e^x en pointillés blancs fins, la droite y = x en gris.
- **Voix : musique seule.** L'utilisateur enregistre lui-même la voix off. Une voix guide Kokoro `ff_siwis` sert seulement à caler les animations (tools/timing.json) ; livrés : la vidéo musique seule, les repères (SRT + TXT) et le texte à lire.
- Plan de fin avec **la signature de l'utilisateur** (canevas « Faïçal Zoubir Signature » : « Faïçal Zoubir » manuscrit, paraphe cuivre, « فيصل زبير »), comme dans exponentielle-e.

## Notes

- Zones libres pour l'interface des Reels : rien d'important dans les 150 px du haut ni les 250 px du bas.
- Rigueur : ne jamais écrire une valeur approchée avec « = » (leçon de la vidéo exponentielle : « 2,72 = e » était faux).
- Valeurs vérifiées : ln 5 ≈ 1,6094 ; ln 2 ≈ 0,6931 ; ln 3 ≈ 1,0986 ; ln 6 ≈ 1,7918 ; ln(10^6) ≈ 13,8155.
