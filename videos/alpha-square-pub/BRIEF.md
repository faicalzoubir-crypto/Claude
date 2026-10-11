---
workflow: general-video
flow: automation
storyboard: no
message: "Alpha Square prépare les élèves de 1ère et 2ème Bac en cours du soir : appelez le 05 22 81 00 88 pour vous inscrire."
destination: instagram-reels
aspect: 1080x1920
language: fr
audience: "Élèves de 1ère Bac et 2ème Bac, et leurs parents (Casablanca)"
length: 22s
angle: publicité courte, scénario imposé en 6 scènes, appel à l'action téléphone
---

## Intent

Vidéo publicitaire pour **Alpha Square – Centre de formation & cours du soir**, Casablanca (Maroc). Objectif : donner envie d'appeler pour s'inscrire. Français, avec tous les accents corrects.

Format vertical 9:16, 1080×1920, 30 fps, 22 secondes, pour Reels, TikTok et statuts WhatsApp. Les 150 px du haut et les 250 px du bas restent libres de texte important (interfaces des réseaux). Sortie : `out/alpha-square-pub.mp4`.

Scénario imposé par le client :

1. 0–3 s, accroche : « Prêt pour ton Bac ? » plein écran, mot par mot, fond marine, formes or animées.
2. 3–6 s, marque : logo (zoom doux), puis « Centre de formation & cours du soir » et « Réussite · Progression · Accompagnement ».
3. 6–11 s, 1ère Bac : grande carte bleue « 1ère BAC », quatre lignes en cascade avec icône : Français, Arabe, Histoire-Géographie, Instruction islamique.
4. 11–16 s, 2ème Bac : carte orange « 2ème BAC », quatre lignes en cascade avec icône : Maths, Physique-Chimie, SVT, Philosophie.
5. 16–19 s, atouts : trois pastilles l'une après l'autre : Petits groupes · Suivi personnalisé · Examens blancs.
6. 19–22 s, appel à l'action : bandeau pinceau or « INSCRIPTIONS OUVERTES ! », téléphone en très grand « 05 22 81 00 88 » avec icône d'appel qui pulse, adresse « 3, Impasse Modibo Keita – Polo, Casablanca », logo en bas.

Transitions courtes (0,3–0,5 s), fluides et cohérentes.

## Assets

- assets/brand/logo-alpha-square.png — logo officiel Alpha Square (1087×992, fond blanc), extrait tel quel, sans retouche, de la page 1 du document « Stratégie d'acquisition des élèves 2026/2027 » fourni par le client. Affiché dans une carte blanche en scène 2 (zoom doux) et en bas de la scène 6.
- assets/flyer (PNG) — référence de style uniquement (palette, icônes, bandeaux pinceau). **Pas encore fourni.**
- assets/music.mp3 — **absent**, donc pas de musique (consigne du client : ne rien télécharger de protégé).
- assets/fonts/ — Poppins 700/800, Figtree 500/600/700, Noto Naskh Arabic 700 (lettre « ع » de l'icône Arabe), en local (SIL OFL, via @fontsource).
- vendor/gsap.min.js — GSAP 3.14.2 en local.

## Customizations

- Identité : marine #0B2B5C, or #F0A21F, bleu #1766D6, orange #F28C1E, fond clair #F5F8FC.
- Titres en Poppins Bold ; texte en Figtree (sans-serif lisible). Polices chargées en local, aucun CDN.
- Style moderne et dynamique : cartes arrondies, bandeaux « coup de pinceau » or et marine, icônes simples par matière. Pas de personnages ni de photos inventés.
- Catalogue testé : `flash-through-white` (bloc shader WebGL) ne rend rien dans cet environnement (WebGL indisponible au rendu), donc remplacé par un flash blanc CSS (surexposition) pour l'entrée de l'appel à l'action.

## Notes

- Aucun prix, aucun taux de réussite, aucune promesse de résultat, aucun témoignage, aucune affirmation absente du brief, aucun chiffre en dehors du téléphone.
- Téléphone exactement : 05 22 81 00 88.
- Le document stratégique indique « Boulevard Modibo Keita » comme lieu ; la vidéo garde l'adresse exacte du brief : « 3, Impasse Modibo Keita – Polo, Casablanca ».
- Méthode demandée : init → HTML/CSS/GSAP piloté par le temps → lint → preview → rendu MP4 → images de contrôle ffmpeg à 1, 4, 8, 13, 17 et 21 s → corrections.
