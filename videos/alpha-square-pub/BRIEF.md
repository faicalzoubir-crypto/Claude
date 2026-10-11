---
workflow: general-video
flow: automation
storyboard: no
message: "Alpha Square prépare les élèves de 1ère et 2ème Bac en cours du soir : appelez le 05 22 81 00 88 pour vous inscrire."
destination: instagram-reels
aspect: 1080x1920
language: fr
audience: "Élèves de 1ère Bac et 2ème Bac, et leurs parents (Casablanca)"
length: 29s
angle: publicité courte, scénario imposé en 6 scènes, appel à l'action téléphone
---

## Intent

Vidéo publicitaire pour **Alpha Square – Centre de formation & cours du soir**, Casablanca (Maroc). Objectif : donner envie d'appeler pour s'inscrire. Français, avec tous les accents corrects.

Format vertical 9:16, 1080×1920, 30 fps, pour Reels, TikTok et statuts WhatsApp. Durée initiale 22 s, passée à 24 s pour que la voix off lise le numéro en entier, puis à 28 s avec l'ajout, à la demande du client, d'une scène carte vue du ciel (orbite façon drone) sur l'emplacement du centre, puis à **29 s** quand le client a demandé la même voix que la vidéo EN-NOUR 3 (Siwis à vitesse normale). Les 150 px du haut et les 250 px du bas restent libres de texte important (interfaces des réseaux). Sortie : `out/alpha-square-pub.mp4`.

Scénario imposé par le client (temps du brief initial ; la version 24 s recale les scènes sur la voix off, voir STORYBOARD.md) :

1. 0–3 s, accroche : « Prêt pour ton Bac ? » plein écran, mot par mot, fond marine, formes or animées.
2. 3–6 s, marque : logo (zoom doux), puis « Centre de formation & cours du soir » et « Réussite · Progression · Accompagnement ».
3. 6–11 s, 1ère Bac : grande carte bleue « 1ère BAC », quatre lignes en cascade avec icône : Français, Arabe, Histoire-Géographie, Instruction islamique.
4. 11–16 s, 2ème Bac : carte orange « 2ème BAC », quatre lignes en cascade avec icône : Maths, Physique-Chimie, SVT, Philosophie.
5. 16–19 s, atouts : trois pastilles l'une après l'autre : Petits groupes · Suivi personnalisé · Examens blancs.
6. 19–22 s, appel à l'action : bandeau pinceau or « INSCRIPTIONS OUVERTES ! », téléphone en très grand « 05 22 81 00 88 » avec icône d'appel qui pulse, adresse « 3, Impasse Modibo Keita – Polo, Casablanca », logo en bas.

Ajout client (version 28 s) : entre les atouts et l'appel à l'action, la localisation sur une carte 3D vue du ciel, la caméra tournant autour du point comme un drone. Point fourni : 33.5620843, -7.6241886 (corrigé par le client). Le client veut une phrase disant que l'emplacement est approximatif, au centre de Casablanca.

Transitions courtes (0,3–0,5 s), fluides et cohérentes.

## Assets

- assets/brand/logo-alpha-square.png — logo officiel Alpha Square (1087×992, fond blanc), extrait tel quel, sans retouche, de la page 1 du document « Stratégie d'acquisition des élèves 2026/2027 » fourni par le client. Affiché dans une carte blanche en scène 2 (zoom doux) et en bas de la scène 6.
- assets/flyer (PNG) — référence de style uniquement (palette, icônes, bandeaux pinceau). **Pas encore fourni.**
- assets/music.mp3 — absent. À la place, fond musical composé par synthèse (aucun droit) : assets/music/alpha-square-bed.wav, généré par tools/music.py.
- assets/vo/ — voix off vo-00 à vo-06 (Kokoro, voix ff_siwis, vitesse 1,0), texte dans assets/vo/lines.txt.
- tools/timing.json — calage du film sur la voix (départs des voix, transitions, carte, appel à l'action) ; lu par tools/music.py, mêmes valeurs que l'objet T de index.html.
- assets/map/casablanca-map.js — terre et trait de côte réels dans un rayon de 36 km autour du point, en mètres locaux (tools/extract_map.py). Source : @geo-maps/earth-lands-100m (npm), données © OpenStreetMap contributors (ODbL), précision 100 m ; crédit affiché sur la scène.
- assets/fonts/ — Poppins 700/800, Figtree 500/600/700, Noto Naskh Arabic 700 (lettre « ع » de l'icône Arabe), en local (SIL OFL, via @fontsource).
- vendor/gsap.min.js — GSAP 3.14.2 en local.

## Customizations

- Identité : marine #0B2B5C, or #F0A21F, bleu #1766D6, orange #F28C1E, fond clair #F5F8FC.
- Titres en Poppins Bold ; texte en Figtree (sans-serif lisible). Polices chargées en local, aucun CDN.
- Style moderne et dynamique : cartes arrondies, bandeaux « coup de pinceau » or et marine, icônes simples par matière. Pas de personnages ni de photos inventés.
- Voix off française : synthèse locale Kokoro, voix féminine `ff_siwis`, vitesse 1,0 — identique à la vidéo EN-NOUR 3, à la demande du client (auparavant 1,08). Texte validé par le client (reprend uniquement le texte à l'écran) ; numéro lu en entier. Graphies phonétiques pour la synthèse uniquement : « Alpha Skouère » (/skwɛʁ/), « SVT », « quatre-vin-huit ».
- Musique : fond synthétisé 120 BPM (Am – F – C – G), impact sur « Bac ? », montée vers l'appel à l'action, fondu de sortie ; creusé sous la voix off (baisse dynamique sur 3 bandes). Mix final ≈ -16 LUFS.
- Synchronisation : les pastilles des atouts arrivent quand la voix les nomme ; chaque paire de chiffres du numéro s'allume en or quand elle est prononcée, puis tout le numéro reste en or.
- Scène carte (18,63–23,21 s) : perspective calculée sur un canvas 2D (sans WebGL) ; descente de 24 km à 3,8 km d'altitude, orbite de -60° à +10°, inclinaison de 20° à 60° ; terre claire en trame de points, mer marine, trait de côte or (port de Casablanca visible), zone approximative en disque or pointillé de 600 m, ondes au sol, repère or avec le logo. Textes : « Au centre de Casablanca », « Emplacement approximatif » (à l'instant où la voix le dit), « OCÉAN ATLANTIQUE », crédit « © OpenStreetMap contributors ». Voix : « Retrouve-nous au centre de Casablanca. Emplacement approximatif. »
- Musique (29 s, calée par tools/timing.json) : batterie coupée pendant le vol (souffle montant), retour du groove sur l'appel à l'action.
- Catalogue testé : `flash-through-white` (bloc shader WebGL) ne rend rien dans cet environnement (WebGL indisponible au rendu), donc remplacé par un flash blanc CSS (surexposition) pour l'entrée de l'appel à l'action.

## Notes

- Aucun prix, aucun taux de réussite, aucune promesse de résultat, aucun témoignage, aucune affirmation absente du brief, aucun chiffre en dehors du téléphone.
- Téléphone exactement : 05 22 81 00 88.
- Le document stratégique indique « Boulevard Modibo Keita » comme lieu ; la vidéo garde l'adresse exacte du brief : « 3, Impasse Modibo Keita – Polo, Casablanca ».
- Données cartographiques : les serveurs OpenStreetMap / Overpass / tuiles sont bloqués par la politique réseau de l'environnement ; seule la terre et la côte (paquet npm) sont disponibles, pas les rues ni les bâtiments. Autoriser overpass-api.de (ou fournir un export map.osm) permettrait d'ajouter rues et bâtiments 3D réels.
- Méthode demandée : init → HTML/CSS/GSAP piloté par le temps → lint → preview → rendu MP4 → images de contrôle ffmpeg à 1, 4, 8, 13, 17 et 21 s → corrections.
