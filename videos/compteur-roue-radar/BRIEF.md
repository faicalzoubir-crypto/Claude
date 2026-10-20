---
workflow: faceless-explainer
flow: automation
storyboard: yes
message: "Ton compteur compte des tours de roue, pas des kilomètres : avec des roues plus grandes qu'à l'origine, tu roules plus vite qu'il ne l'affiche, et le radar, lui, mesure la vraie vitesse."
destination: youtube
aspect: 1920x1080
language: fr
audience: "Lycéens et grand public"
length: 110s
angle: concept
narration: no
voice: ff_siwis
---

## Intent

Vidéo pédagogique en français intitulée **« Pourquoi ton compteur peut te mentir : de la roue au radar »**. Ton clair et dynamique, pour lycéens et grand public. Format 16:9, couleurs sobres, flèches animées pour la transmission, tableau animé ligne par ligne.

Durée demandée par l'utilisateur : **« Just 1min30sec to 2min max »** (le brief collé prévoyait 3 à 4 min). Cible ≈ 1 min 50, jamais plus de 2 min. Les 7 scènes sont gardées et raccourcies (minutage proposé : intro 7 s · transmission 28 s · calcul 17 s · comparaison 12 s · contrôle de police 22 s · tableau 16 s · conclusion 10 s).

Véhicule d'exemple : **Ford Fiesta 2023** (moteur 1.0 EcoBoost, traction avant), pneus d'origine **195/55 R16**.

Hypothèse à afficher : « pour simplifier, on suppose un compteur parfaitement étalonné en usine ».

Scènes (le texte complet du brief est dans `capture/extracted/visible-text.txt`) :

1. Introduction — la Fiesta roule ; question à l'écran : « Si je change la taille de mes roues, mon compteur affiche-t-il toujours la vraie vitesse ? »
2. Chaîne de transmission — vue éclatée, flèches qui s'allument étape par étape : moteur (pistons → vilebrequin, translation → rotation), embrayage, boîte de vitesses (rapport vitesse de rotation / couple), différentiel (gauche/droite, virages), arbres de transmission (cardans) vers les roues avant, roues (rotation → déplacement). Puis le capteur de vitesse (roue/ABS) → calculateur → compteur.
3. Comment le compteur calcule — il compte les tours et les multiplie par la circonférence d'ORIGINE. 195/55 R16 : diamètre ≈ 621 mm → circonférence ≈ 1,95 m. Formules : « Diamètre = (jante en pouces × 25,4) + 2 × (largeur × série / 100) » et « Vitesse réelle = vitesse affichée × (diamètre nouveau / diamètre d'origine) ».
4. Comparaison visuelle — petite et grande roue font 1 tour sur une règle ; la grande va plus loin ; le compteur compte « 1 tour » dans les deux cas. Roue plus grande → vitesse réelle SUPÉRIEURE ; plus petite → INFÉRIEURE.
5. Contrôle de police — route urbaine, panneau 60 ; Karim, Fiesta en 225/65 R17 (dimension hypothétique) ; compteur 60, radar 70 ; dialogue mot pour mot (voir Notes) ; Karim regarde ses roues.
6. Tableau récapitulatif — titre « Compteur affiché : 60 km/h – Ford Fiesta 2023 (référence 195/55 R16) », 8 lignes une par une, vitesses réelles au-dessus de 60 en rouge, note sur les dimensions non homologuées.
7. Conclusion — trois conseils ; phrase finale « Ton compteur compte des tours, le radar mesure la réalité. »

## Customizations

- **Sans voix off** (demande après la première livraison : « Remove voix off ») : la narration Siwis est retirée du mix ; la musique n'est plus creusée sous la voix (`python3 tools/music.py --sans-voix`), les voix sont retirées de `index.html` (`python3 tools/sans_voix.py`, après `assemble-index.mjs` et `transitions.mjs`). Les sous-titres incrustés restent et portent le texte, au même rythme. La version avec voix reste livrée : `livrables/compteur-roue-radar-avec-voix.mp4`.
- **Troisième version, sans voix ni sous-titres** (« Une autre version sans subtitles ») : `livrables/compteur-roue-radar-sans-sous-titres.mp4`, image + musique + bruitages. Les sous-titres sont masqués (`data-hidden`) le temps du rendu avec `python3 tools/sous_titres.py off`, puis réaffichés (`on`) : le projet reste sur la version sans voix avec sous-titres.
- Narration : voix française de synthèse Kokoro `ff_siwis` (même voix qu'EN-NOUR 3 et Alpha Square). Pas d'avatar présentateur (aucun compte HeyGen connecté).
- Sous-titres français incrustés + fichier `.srt` livré à part. Une bande basse reste libre pour les sous-titres : ils ne recouvrent jamais le tableau ni les formules.
- Dialogue du contrôle en bulles de BD, lu par la même voix (seule voix française disponible).
- Musique de fond discrète, baissée sous la voix, + quelques bruitages motivés (bip du radar, sirène de police, aiguille qui se cale sur 60). Mixage final ≈ −14 LUFS.
- Flèches de mouvement animées pour la transmission ; tableau animé ligne par ligne ; vitesses réelles > 60 en rouge.

## Notes

- Narration : écrite à partir des scènes (restructurée pour tenir en < 2 min). Gardés mot pour mot : le titre, l'hypothèse, la question de la scène 1, les deux formules, les trois répliques du dialogue, le tableau, les trois conseils, la phrase finale.
- Dialogue (mot pour mot) :
  - Policier : « Bonjour monsieur, vous rouliez à 70 km/h dans une zone limitée à 60. »
  - Karim : « Impossible ! Mon compteur indiquait exactement 60, j'en suis sûr ! »
  - Policier : « Votre compteur est réglé pour les roues d'origine. Avec des roues plus grandes, chaque tour vous fait parcourir plus de distance. Le radar, lui, mesure votre vitesse réelle. »
- Tableau vérifié avec la formule du brief : tous les diamètres, écarts et vitesses réelles sont exacts.
- Note du tableau : « les dimensions au-delà de 205/55 R16 sont hypothétiques et ne sont pas homologuées sur la Fiesta. »
- Visuels : voiture dessinée évoquant une Fiesta (citadine 5 portes), sans photo ni logo Ford ; Karim et le policier en personnages plats simples.
- Transmission en traction avant comme sur la Fiesta : moteur transversal, boîte et différentiel dans le même carter, arbres de transmission directement vers les roues avant ; capteur roue/ABS → calculateur → compteur.
- Palette : d'abord « Tjr utilise les couleur orange et marron comme claude », puis « I want the colors of the video of sliding scooter » → les couleurs du film Vespa (glissade-vespa-asr) : fond #0D1316 + grille fine #26343B, panneaux #141D21, texte #E8EEEC / #93A4A7, un seul accent ambre #F4A62A, objets dessinés en menthe #93CDBB ; rouge #F25C54 au-dessus de l'affichage, vert #3CC98F en dessous. Préférence durable (CLAUDE.md à la racine).
- Livrable : `livrables/compteur-roue-radar.mp4` (1920×1080, 30 i/s) + `livrables/compteur-roue-radar.srt`.
