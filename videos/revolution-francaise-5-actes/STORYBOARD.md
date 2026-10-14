---
format: 1920x1080
duration: 165s
message: "En 10 ans (1789-1799), la France passe de la monarchie absolue à une nation de citoyens : une rupture majeure, mais violente et inachevée."
arc: story-explainer with timeline (5 actes)
audience: "Élèves de Première (histoire, chapitre 1) qui révisent la Révolution française pour une évaluation"
mode: collaborative
music: "solennel et dramatique, cordes et timbales légères ; étincelle au début, tension qui monte jusqu'à la Terreur, retombée sous les cendres, résolution calme ; composé par synthèse, sans droits"
captions: skipped (the key words of every line are already on screen — date, title, one key line; 16:9 classroom projection)
---

# La frise en flammes — storyboard

One stage for the whole film: the PDF's frise (1789 → 1799, five act colors) runs along the top of every act frame, and the flame rides it. Each act opens on its PDF banner (ACTE N · fire metaphor · title · years), then its events arrive as PDF-style cards — date pill, title, one key line — each when the voice names it. Within an act the seams push left (time moves forward); between acts the seam is a smoky blur-crossfade.

## Video direction

- **Palette system** — from `frame.md`: paper ground everywhere; each act frame uses only its act color as accent (acte1 red, acte2 orange, acte3 blue, acte4 bordeaux, acte5 slate); intro / problématique / réponse / Hugo use the cover's blue + red bands and the navy box; gold only for ★, rules and the arrow strips. The flame is the only light source and the only glow.
- **One stage** — the frise strip rides the top of every act frame (same position, current act lit, the flame sitting on the current date); act openings wipe their PDF banner in from the left; events always arrive as PDF cards (medallion → date pill → title → one line).
- **Motion grammar + reveal model** — long-tail `power3` settles, no bounce; every card, tag, label and keyword reveals on its spoken cue (word times from `assets/voice/cues.json`), never front-loaded; holds are still (the flame's flicker is the only sanctioned aliveness — the subject doing something, finite, deterministic).
- **Rhythm / held frames** — 03 (problématique) and 14 (Hugo) are deliberate held reads; 08 holds a beat of stillness after « guillotiné »; 10 peaks the flame then collapses it; 12 puts it out.
- **Negative list** — no slideshow (front-load then freeze), no screensaver (independent floating), no lazy breathing, no back-half camera drift, no gore (the guillotine is an icon, the death a blade drop + silence), no invented facts, dates or images beyond the PDF.

## Frame 1 — L'étincelle

- scene: Paper ground with the cover's blue and red bands. A match strikes on « 1789 » ; the flame runs along the five-color frise to « 1799 », then the title « Les flammes de la liberté » and the five act chips land.
- voiceover: "Une étincelle, en 1789… Et en dix ans, la France passe d'un roi tout-puissant à une nation de citoyens. La Révolution française, en cinq actes."
- duration: 10.7s
- transition_in: cut
- status: built
- src: compositions/frames/01-etincelle.html
- type: hook
- persuasion: Visceral metaphor (the spark) + thesis up front
- beat: Curiosity + anticipation
- blueprint: spatial-pan-stations
- act: 0

narrativeRole: Opens the gap with the PDF's own metaphor and states the thesis immediately (value first): king → nation in ten years.
keyMessage: La Révolution dure dix ans (1789-1799) et fait passer la France d'un roi tout-puissant à une nation de citoyens.
- focal: the flame on the frise
- roles: frise = foreground subject (unlit track that lights act by act) · title block = foreground · bands + paper = background · act chips = supporting
- sfx: match-strike@0.0, whoosh-soft@3.4

Adapt (spatial-pan-stations): keep the stations-on-one-line signature — the five act segments are the stations, the flame is the traveller lighting each; no camera pan, the flame moves instead.
Scene 1 (0.0–1.0s): paper + bands; only the unlit grey frise track; the match flame ignites at 1789 (spring-pop entrance, glow blooms) — « Une étincelle ».
Scene 2 (1.0–3.4s): « 1789 » label lights in ink as the VO says it; the flame flickers, gathering (subtle jitter).
Scene 3 (3.4–7.5s): « Et en dix ans… » — the flame runs right along the track; each act segment fills with its color as it passes (scaleX reveal, act by act, power3 ease); the kicker and the title « Les flammes / de la liberté » rise per-word on « la France passe… nation de citoyens »; « 1789 — 1799 » lands on « dix ans ». Centered, layered depth.
Scene 4 (7.6–10.25s): « La Révolution française » → subtitle fades up; « en cinq actes » → the five act chips cascade left to right (staggered rise) and hold; the flame settles at 1799.

## Frame 2 — Avant 1789 : l'Ancien Régime

- scene: A crown above a three-tier pyramid: clergé and noblesse (small, gold « privilèges » tags) on top of a huge tiers état base. « Monarchie absolue · droit divin » under the crown; « Lumières : Voltaire, Montesquieu, Rousseau » arrives as a stamp that cracks the pyramid.
- voiceover: "Avant, c'est l'Ancien Régime : un roi aux pleins pouvoirs, de droit divin, et une société d'ordres, où seuls le clergé et la noblesse ont des privilèges. Les Lumières dénoncent cette injustice."
- duration: 11.118s
- transition_in: blur-crossfade
- status: built
- src: compositions/frames/02-ancien-regime.html
- type: pain_point
- persuasion: Concretization (the pyramid of orders) + progressive disclosure
- beat: Recognition + unease
- blueprint: kinetic-type-beats
- act: 0

narrativeRole: Sets the "before" picture the whole Revolution breaks: absolute monarchy and an unequal society of orders.
keyMessage: Avant 1789 : monarchie absolue de droit divin et société d'ordres injuste, critiquée par les Lumières.
- focal: the pyramid of the three orders
- roles: pyramid = foreground subject · crown + king line = supporting · Lumières card + arrow strip = supporting · paper = background
- sfx: soft-thud@4.6, crack@9.2

Compose: progressive disclosure of the society, then a crack drawn through it.
Scene 1 (0.0–1.9s): kicker « AVANT 1789 » and title « L'Ancien Régime » rise (per-word) — top-left, asymmetric 60/40.
Scene 2 (1.9–4.3s): « un roi aux pleins pouvoirs » → the crown medallion pops in above the empty apex; « de droit divin » → the king line reveals beside it.
Scene 3 (4.3–6.0s): « une société d'ordres » → the pyramid builds bottom-up: tiers état base, then noblesse, then clergé (layer-reveal, each tier rising 30px).
Scene 4 (6.0–8.4s): « le clergé » → first « privilèges » tag slides out; « la noblesse » → second tag; « privilèges » → both tags glow gold once.
Scene 5 (8.5–10.67s): « Les Lumières » → the Lumières card slides in from the right; « dénoncent » → the crack draws down through the pyramid (svg-path-draw) with a small shake of the tiers; « injustice » → arrow strip slides in and holds.

## Frame 3 — La problématique

- scene: The navy problématique box of page 2, centered on paper; the key words « rupture majeure » and « nouvelle conception de la nation » light in gold. The match flame waits at the left end of the frise.
- voiceover: "Une question : en quoi la Révolution est-elle une rupture majeure, qui fait naître une nouvelle idée de la nation ?"
- duration: 6.662s
- transition_in: blur-crossfade
- status: built
- src: compositions/frames/03-problematique.html
- type: product_intro
- persuasion: Question→answer pairing (frame the question the film answers)
- beat: Focus
- blueprint: titlecard-reveal
- act: 0

narrativeRole: Names the exam question the whole film answers, exactly as the sheet words it.
keyMessage: La problématique : la Révolution comme rupture majeure qui fait émerger une nouvelle conception de la nation.
- focal: the navy problématique box
- roles: navy box + question = foreground subject · frise (dimmed) + waiting flame = supporting · bands = background
- sfx: none

Reproduce (titlecard-reveal): one restrained move — the box rises with a soft crossfade, then the question reads line by line; deliberate held read.
Scene 1 (0.0–1.0s): the navy box rises into place; « PROBLÉMATIQUE » label reveals; the dim frise and the small flame waiting at 1789 fade up below.
Scene 2 (1.0–3.6s): the question reveals line by line with the VO; « rupture majeure » glows gold on « rupture majeure ».
Scene 3 (3.7–6.21s): « nouvelle conception de la nation » glows gold on « nouvelle idée de la nation »; hold still, only the flame flickers.

## Frame 4 — Acte 1 : le grand saut

- scene: Red act banner « ACTE 1 · L'embrasement · Le grand saut dans la Révolution · 1789 », then the frise strip (acte 1 lit) with three event cards arriving left to right: 5 mai (États généraux → échec), 20 juin ★ (serment du Jeu de paume), 14 juillet ★ (prise de la Bastille). Arrow strip: « → La souveraineté passe du roi à la nation ».
- voiceover: "Acte un : l'embrasement. Mis en minorité aux États généraux, le tiers état se proclame Assemblée nationale. Le 20 juin, au Jeu de paume, ses députés jurent de donner une constitution au pays. Le 14 juillet, Paris prend la Bastille."
- duration: 14.959s
- transition_in: blur-crossfade
- status: built
- src: compositions/frames/04-acte1-grand-saut.html
- type: feature_showcase
- persuasion: Signposting (act banner) + causal chain
- beat: Momentum
- blueprint: spatial-pan-stations
- act: 1

narrativeRole: Lights the fire: the deputies take sovereignty from the king, the people of Paris back them.
keyMessage: En 1789, les députés du tiers état fondent l'Assemblée nationale et la souveraineté passe à la nation ; le 14 juillet, la Bastille tombe.
- focal: the three event cards
- roles: cards = foreground subject · act banner = supporting · frise strip + flame = supporting · arrow strip = supporting · paper = background
- sfx: whoosh@0.0, crackle-swell@0.4, stamp@13.8

Adapt (spatial-pan-stations): the stations are the three dated cards laid along the act; the camera stays still, the cards arrive in date order on the VO.
Scene 1 (0.0–1.7s): the flame at 1789 flares as the red act-1 segment lights; the act banner wipes in from the left on « Acte un : l'embrasement ».
Scene 2 (1.7–6.8s): « États généraux » → card 1 rises (medallion → pill → title → line); « Assemblée nationale » → the arrow strip « la souveraineté passe du roi à la nation » slides in.
Scene 3 (6.9–11.8s): « Le vingt juin » → card 2 rises; « jurent » → its gold ★ pops.
Scene 4 (11.9–14.51s): « Le quatorze juillet » → card 3 rises; « la Bastille » → the Bastille's tower flames flare and the ★ pops; hold.

## Frame 5 — Acte 1 : une société nouvelle

- scene: Same frise strip, the flame further right. Card 4 août ★ (abolition des privilèges — the pyramid of frame 2 collapses flat), card 26 août ★ (DDHC as a scroll with Art. 1 « Les hommes naissent et demeurent libres et égaux en droits »), card 5-6 octobre (marche des femmes → le roi aux Tuileries). Bilan strip: « Fin de la monarchie absolue · des citoyens · la souveraineté appartient à la nation ».
- voiceover: "Le 4 août, les privilèges sont abolis. Le 26, la Déclaration des droits de l'homme proclame : les hommes naissent et demeurent libres et égaux en droits. En octobre, les femmes ramènent le roi à Paris."
- duration: 12.417s
- transition_in: push-slide LEFT
- status: built
- src: compositions/frames/05-acte1-societe-nouvelle.html
- type: benefit_highlight
- persuasion: Callback (the pyramid of frame 2 falls) + citation (Art. 1)
- beat: "Aha" + conviction
- blueprint: grid-card-assemble
- act: 1

narrativeRole: Shows what 1789 changes for good: the end of orders and privileges, and the founding text of the new society.
keyMessage: Bilan de 1789 : fin de la monarchie absolue et de la société d'ordres ; des citoyens libres et égaux ; la nation est souveraine.
- focal: the DDHC card and its Article 1
- roles: DDHC card = foreground subject · 4 août + octobre cards = supporting · bilan box = supporting · strip = supporting · paper = background
- sfx: stamp@2.0, paper@3.0

Adapt (grid-card-assemble): three cards assemble in a row (staggered by the VO, not by a fixed stagger) and the bilan list accumulates below.
Scene 1 (0.0–2.8s): slim act header; « Le quatre août » → card 1 rises; « abolis » → bilan box appears with its first line « Fin de la monarchie absolue et de la société d'ordres ».
Scene 2 (2.8–8.9s): « Le vingt-six » → the DDHC card rises (hero, wider); « les hommes naissent » → the Article 1 quote reveals; « libres et égaux en droits » → those words light in red; « droits » → bilan line 2 « citoyens ».
Scene 3 (9.2–11.97s): « En octobre » → card 3 rises; « Paris » → bilan line 3 « la souveraineté appartient à la nation »; hold.

## Frame 6 — Acte 2 : la fuite à Varennes

- scene: Orange banner « ACTE 2 · Le feu couve · 1790-1791 » then a real map aged like parchment: the carriage leaves Paris by night, passes Sainte-Menehould (Drouet recognizes the king), stops at Varennes (red cross); Montmédy stays out of reach, dashed. The carriage turns back to Paris. Closing strip: « → La confiance entre le roi et le peuple est brisée ».
- voiceover: "Acte deux : le feu couve. Le roi doit partager le pouvoir : c'est la monarchie constitutionnelle. Mais une nuit de juin, il s'enfuit, déguisé en valet. Reconnu, il est arrêté à Varennes, et ramené à Paris. La confiance est brisée."
- duration: 14.352s
- transition_in: blur-crossfade
- status: built
- src: compositions/frames/06-acte2-varennes.html
- type: feature_showcase
- persuasion: Demonstration (the route plays out on the map) + before/after
- beat: Tension + suspense
- blueprint: camera-journey
- act: 2

narrativeRole: Turns the PDF's six Varennes vignettes into one journey the student can see: the flight that breaks the king's credibility.
keyMessage: 1791 : la fuite du roi, arrêtée à Varennes, ruine la confiance dans la monarchie constitutionnelle.
- focal: the king's route on the real map
- roles: map (rivers, border, towns) = background · route + carriage = foreground subject · act banner, tag and card = supporting · arrow strip = supporting
- sfx: whoosh@0.0, hooves@6.6, stamp@10.5

Adapt (camera-journey, cursorless): keep the motivated journey — the route draws and the carriage travels Paris → Sainte-Menehould → Varennes; the map layer pushes in gently while the carriage travels, then holds.
Scene 1 (0.0–1.8s): parchment map with rivers and the dashed border fades up; the strip lights act 2 (small ember flame); the orange act banner wipes in on « Acte deux : le feu couve ».
Scene 2 (1.8–5.9s): « partager le pouvoir » → the « Monarchie constitutionnelle » tag slides in under the banner. Paris dot + label appear.
Scene 3 (5.9–9.6s): « une nuit de juin » → the flight card rises; « il s'enfuit » → the route draws from Paris eastward (svg-path-draw) with the carriage riding its tip; « Reconnu » → Sainte-Menehould dot + « Drouet reconnaît le roi ».
Scene 4 (9.7–12.2s): « arrêté à Varennes » → the carriage stops, the red ✕ stamps on Varennes with its label; the dotted planned road to Montmédy and « jamais atteint » fade in; « ramené à Paris » → the carriage turns back (flips to face west).
Scene 5 (12.3–13.9s): « La confiance est brisée » → arrow strip slides in; hold.

## Frame 7 — Acte 3 : la chute de la monarchie

- scene: Blue banner « ACTE 3 · Le brasier se réveille · 1792 ». Three causes stack as tags (veto, guerre qui tourne mal, soupçon de trahison), then card 10 août ★ (prise des Tuileries → la couronne tombe) and card 21-22 septembre ★ (naissance de la République, an I) with the bonnet phrygien replacing the crown.
- voiceover: "Acte trois : le brasier se réveille. Le roi bloque les lois par son veto, la guerre tourne mal : on l'accuse de trahison. Le 10 août, les sans-culottes prennent les Tuileries : la monarchie tombe. En septembre, la République est proclamée."
- duration: 14.079s
- transition_in: blur-crossfade
- status: built
- src: compositions/frames/07-acte3-republique.html
- type: feature_showcase
- persuasion: Causal chain (veto + guerre + trahison → 10 août → République)
- beat: Momentum + release
- blueprint: kinetic-type-beats
- act: 3

narrativeRole: Explains why the constitutional monarchy fails and how the Republic is born in 1792.
keyMessage: 1792 : la monarchie tombe le 10 août et la République naît les 21-22 septembre.
- focal: the two 1792 cards (Tuileries → République)
- roles: cards = foreground subject · cause tags = supporting · banner + strip = supporting · paper = background
- sfx: whoosh@0.0, crackle-swell@1.0, stamp@10.3, chime@12.8

Reproduce (kinetic-type-beats, as a causal relay): causes stack one per beat, then the payoff cards land.
Scene 1 (0.0–2.3s): blue act banner wipes in; the strip lights act 3 and the flame swells on « le brasier se réveille ».
Scene 2 (2.3–6.6s): « POURQUOI LA MONARCHIE ÉCHOUE » label; tags slide in on « bloque les lois » (veto), « la guerre tourne mal » (20 avril 1792), « trahison ».
Scene 3 (7.0–10.9s): « Le dix août » → Tuileries card rises; « la monarchie tombe » → its ★ pops.
Scene 4 (11.0–13.63s): « En septembre » → République card rises; « République » → arrow strip (Convention, suffrage universel masculin, Valmy); « proclamée » → ★ pops; hold.

## Frame 8 — Acte 4 : la mort du roi

- scene: Bordeaux banner « ACTE 4 · La fureur des flammes · 1793-1794 ». Card 21 janvier 1793 ★ (Louis Capet guillotiné, guillotine icon, one hard cut to silence). Then two fronts open on a small Europe/France split: « guerre extérieure : coalition des monarchies » and « guerre civile : Vendée ».
- voiceover: "Acte quatre : la fureur des flammes. Le 21 janvier 1793, Louis Capet est guillotiné. Les rois d'Europe se coalisent contre la France, et la Vendée se soulève : c'est la guerre, dehors et dedans."
- duration: 13.58s
- transition_in: blur-crossfade
- status: built
- src: compositions/frames/08-acte4-mort-du-roi.html
- type: feature_showcase
- persuasion: Contrast (dehors / dedans)
- beat: Shock + tension
- blueprint: kinetic-type-beats
- act: 4

narrativeRole: The point of no return: the king's death, and the double war that pushes the Republic toward the Terror.
keyMessage: 21 janvier 1793 : Louis XVI est exécuté ; la République affronte une guerre extérieure et une guerre civile.
- focal: the hero card « La mort de Louis Capet »
- roles: hero card = foreground subject · war tiles = supporting · banner + strip = supporting · paper = background
- sfx: whoosh@0.0, crackle-swell@0.9, blade@6.0, drum-low@7.5

Reproduce (kinetic-type-beats, two beats): the death, a held silence, then the two wars.
Scene 1 (0.0–2.4s): bordeaux act banner wipes in; the strip lights act 4 and the flame grows big on « la fureur des flammes ».
Scene 2 (2.4–7.2s): « Le vingt et un janvier » → hero card rises; « guillotiné » → the blade in the medallion drops (svg internal move), the card holds still a beat; the crowd's cry line fades in after.
Scene 3 (7.3–11.9s): « Les rois d'Europe » → heading « La guerre, dehors et dedans »; « se coalisent » → DEHORS tile slides in; « la Vendée » → DEDANS tile slides in.
Scene 4 (12.0–13.13s): « dehors et dedans » → arrow strip (Girondins contre Montagnards); hold.

## Frame 9 — Acte 4 : la Terreur

- scene: A two-column split from the PDF's table: Girondins (province, bourgeoisie, république modérée) dim out; Montagnards (Paris, sans-culottes, Robespierre) light up. Then the Terror's machinery assembles as three blocks: Comité de salut public (12 membres), tribunal révolutionnaire, loi des suspects. Small card 16 octobre 1793 : Marie-Antoinette guillotinée.
- voiceover: "Avec les sans-culottes, les Montagnards de Robespierre écartent les Girondins. Pour sauver la République, ils organisent la Terreur : Comité de salut public, tribunal révolutionnaire, loi des suspects. Marie-Antoinette est guillotinée."
- duration: 14.095s
- transition_in: push-slide LEFT
- status: built
- src: compositions/frames/09-acte4-terreur.html
- type: feature_showcase
- persuasion: Comparison of two options (Girondins vs Montagnards) + frame-then-fill
- beat: Unease + comprehension
- blueprint: grid-card-assemble
- act: 4

narrativeRole: Shows who takes power in 1793 and what the Terror is made of.
keyMessage: Les Montagnards prennent le pouvoir (2 juin 1793) et mettent en place la Terreur pour sauver la République.
- focal: the Terror's machinery (three blocks)
- roles: Montagnards / Girondins columns = foreground (comparison) · Terror blocks = foreground subject · Marie-Antoinette block + arrow = supporting · strip = supporting · paper = background
- sfx: stamp@3.0, drum-low@7.5, drum-low@9.0, drum-low@10.6, blade@12.8

Adapt (grid-card-assemble): the PDF comparison table splits left/right, then the Terror's blocks assemble in a row, one per spoken item.
Scene 1 (0.0–3.4s): slim header; Girondins column reveals; « les Montagnards de Robespierre » → Montagnards column slides in from the right.
Scene 2 (3.0–6.8s): « écartent les Girondins » → Girondins dim, the red « Arrêtés le 2 juin 1793 » stamp lands, the « 2 juin 1793 » badge pops; « sauver la République » → the Constitution de l'an I line reveals.
Scene 3 (6.9–11.7s): « la Terreur » → « LA TERREUR » label; « Comité de salut public », « tribunal révolutionnaire », « loi des suspects » → one block each, on cue.
Scene 4 (11.8–13.65s): « Marie-Antoinette » → her block; « guillotinée » → arrow strip; hold.

## Frame 10 — Acte 4 : la Révolution dévore ses enfants

- scene: Quote card « La Révolution dévore ses propres enfants » ★. Portrait-less name plates Danton and Desmoulins (Indulgents) fall at 5 avril 1794; then Robespierre's plate falls at 27-28 juillet 1794 (9 thermidor an II ★). The flame, at its peak, collapses into embers.
- voiceover: "Mais la Révolution dévore ses enfants : Danton et Desmoulins, qui voulaient ralentir la Terreur, sont guillotinés. Puis Robespierre tombe à son tour : le 9 thermidor, la Terreur prend fin."
- duration: 11.225s
- transition_in: push-slide LEFT
- status: built
- src: compositions/frames/10-acte4-thermidor.html
- type: feature_showcase
- persuasion: Callback (the flame's peak then collapse) + distillation (the quote)
- beat: Fascination + release
- blueprint: kinetic-type-beats
- act: 4

narrativeRole: The Terror turns on its own leaders and ends with Robespierre's fall.
keyMessage: 1794 : Danton et Desmoulins puis Robespierre sont guillotinés ; le 9 thermidor marque la fin de la Terreur.
- focal: the three name plates
- roles: plates = foreground subject · quote = foreground (headline) · strip flame = supporting · arrow strip = supporting · paper = background
- sfx: blade@5.4, blade@7.2, ember-hiss@9.9

Reproduce (kinetic-type-beats): the quote lands as the headline, then the plates fall one beat at a time.
Scene 1 (0.0–2.1s): the flame on the strip is at its peak; the quote « La Révolution dévore ses propres enfants » assembles per-word.
Scene 2 (2.2–6.2s): « Danton » → plate 1 rises straight; « Desmoulins » → plate 2 rises; « guillotinés » → both tilt and dim (they « fall »).
Scene 3 (6.3–9.3s): « Robespierre » → plate 3 rises; « tombe » → it tilts and dims; « thermidor » → its ★ pops.
Scene 4 (9.4–10.78s): « la Terreur prend fin » → the flame collapses to embers; arrow strip slides in; hold.

## Frame 11 — Acte 5 : le Directoire

- scene: Slate banner « ACTE 5 · Sous les cendres · 1795-1799 ». The frise turns ash grey. Card 1795 ★ Directoire: « Retour du suffrage censitaire » (a ballot box that only accepts coins), « 2 assemblées : Anciens · Cinq-Cents », « 5 Directeurs ». Then a sword/army tag tips the balance toward « Bonaparte ».
- voiceover: "Acte cinq : sous les cendres. La République modérée écarte les sans-culottes. Le Directoire rétablit le suffrage censitaire : seuls les riches votent. Fragile, il s'appuie sur l'armée… et sur un général : Bonaparte."
- duration: 13.73s
- transition_in: blur-crossfade
- status: built
- src: compositions/frames/11-acte5-directoire.html
- type: feature_showcase
- persuasion: Before/after (suffrage universel → censitaire again)
- beat: Unease + foresight
- blueprint: grid-card-assemble
- act: 5

narrativeRole: The Revolution cools into a moderate, less democratic republic that leans on the army.
keyMessage: 1795-1799 : le Directoire, république modérée au suffrage censitaire, instable, s'appuie sur l'armée et Bonaparte.
- focal: the Directoire card
- roles: Directoire card = foreground subject · Commune + régime instable cards = supporting · banner + strip = supporting · paper = background
- sfx: whoosh@0.0, coin@6.3, drum-low@12.5

Adapt (grid-card-assemble): three cards assemble left to right on the VO, the centre one carrying a three-line list revealed item by item.
Scene 1 (0.0–1.9s): slate act banner wipes in; the strip lights act 5 in ash grey; the flame is a small ember.
Scene 2 (1.9–4.6s): « La République modérée » → Commune card rises.
Scene 3 (4.7–8.9s): « Le Directoire » → hero card rises; « suffrage censitaire » → list item 1; then items 2 and 3 on « seuls les riches votent »; arrow strip (moins démocratique) on « votent ».
Scene 4 (9.0–13.28s): « Fragile » → régime instable card rises; « Bonaparte » → its bicorne medallion pops; hold.

## Frame 12 — Le 18 brumaire

- scene: The bicorne icon in a slate medallion; card « 9 novembre 1799 · 18 brumaire an VIII ★ — Coup d'État de Bonaparte → le Consulat ». The flame on the frise goes out at 1799 in a curl of smoke.
- voiceover: "Le 18 brumaire, le 9 novembre 1799, Bonaparte prend le pouvoir par un coup d'État. La Révolution est finie."
- duration: 8.811s
- transition_in: push-slide LEFT
- status: built
- src: compositions/frames/12-brumaire.html
- type: benefit_highlight
- persuasion: Callback (the flame born in frame 1 goes out)
- beat: Inevitability
- blueprint: titlecard-reveal
- act: 5

narrativeRole: Closes the decade on the event that ends the Revolution.
keyMessage: 9 novembre 1799 (18 brumaire) : le coup d'État de Bonaparte met fin à la Révolution.
- focal: the coup d'État card, then the flame going out
- roles: card = foreground subject · full frise + flame + smoke = foreground (finale) · slim header = supporting · paper = background
- sfx: drum-low@4.1, ember-hiss@7.0

Reproduce (titlecard-reveal): one clean card reveal and a still hold; the only other move is the flame going out.
Scene 1 (0.0–4.0s): slim header; the full five-color frise lies across the bottom with the small flame at 1799; « Le dix-huit brumaire » → the card rises (date pill, title).
Scene 2 (4.1–6.7s): « Bonaparte prend le pouvoir » → the line reveals; « coup d'État » → its ★ pops.
Scene 3 (6.8–8.36s): « La Révolution est finie » → the flame shrinks and goes out; two curls of smoke draw upward and fade; hold.

## Frame 13 — Réponse à la problématique

- scene: The whole five-color frise returns, every key date ticked (recap of page 12). Above it, the navy answer box: « Rupture majeure : de la monarchie absolue à une nation de citoyens libres et égaux » in white, then « … mais violente et inachevée » with four tags: guerres · Terreur · femmes et pauvres exclus · Bonaparte.
- voiceover: "Alors, rupture majeure ? Oui : en dix ans, on passe d'un roi absolu à une nation de citoyens libres et égaux. Mais une rupture violente, et inachevée : guerres, Terreur, femmes et pauvres exclus… et Bonaparte au pouvoir."
- duration: 13.685s
- transition_in: blur-crossfade
- status: built
- src: compositions/frames/13-reponse.html
- type: branding
- persuasion: Distillation + rule of three (gains) vs four limits
- beat: Clarity + "now I get it"
- blueprint: grid-card-assemble
- act: 0

narrativeRole: Answers the problématique of frame 3 in the sheet's own terms and recaps the decade on the frise.
keyMessage: La Révolution est une rupture majeure (nation de citoyens, souveraineté nationale) mais violente et inachevée.
- focal: the navy answer box
- roles: answer box = foreground subject · full frise with key dates = foreground (recap) · bands = background
- sfx: whoosh-soft@0.0, chime@2.0

Adapt (grid-card-assemble): the answer lines assemble on the VO while the recap frise builds below, its key dates popping left to right.
Scene 1 (0.0–1.9s): navy box rises with « RÉPONSE À LA PROBLÉMATIQUE »; « rupture majeure ? » → « Une rupture majeure » per-word.
Scene 2 (1.9–6.5s): « Oui » → the frise bar draws left to right in its five colors; the key-date labels pop in date order across « en dix ans… libres et égaux »; « roi absolu » → line 2 reveals with its bold words.
Scene 3 (6.6–8.8s): « Mais une rupture violente, et inachevée » → line 3 « … mais violente et inachevée » in gold.
Scene 4 (8.9–13.24s): tags pop on « guerres », « Terreur », « femmes et pauvres exclus », « Bonaparte »; hold.

## Frame 14 — Victor Hugo

- scene: Cover layout returns (blue and red bands, gold rules): the Victor Hugo quote from page 1, then « Yazid Tragha — Frise chronologique de révision ». Silent, music resolves.
- voiceover: ""
- duration: 6s
- transition_in: blur-crossfade
- status: built
- src: compositions/frames/14-hugo.html
- type: cta
- persuasion: Callback (the cover) + citation
- beat: Resolution + inspiration
- blueprint: titlecard-reveal
- act: 0

narrativeRole: Lands the film on the sheet's own epigraph and signature, like the PDF's cover.
keyMessage: « La Révolution française est le plus puissant pas du genre humain depuis l'avènement du Christ. » — Victor Hugo
- focal: Victor Hugo's quote
- roles: quote = foreground subject · act chips + gold rules = supporting · name + subtitle = supporting · bands = background
- sfx: none (music resolves)

Reproduce (titlecard-reveal, end-card chain): chips → quote → attribution → signature, each with one restrained move; the final frame fades out.
Scene 1 (0.0–1.0s): act chips cascade in; the top gold rule draws.
Scene 2 (0.6–2.6s): the quote reveals line by line; « — Victor Hugo » fades up; the bottom rule draws.
Scene 3 (2.8–5.2s): « Yazid Tragha » and the subtitle rise; hold still.
Scene 4 (5.2–6.0s): the whole frame fades to paper (the film's only exit).
