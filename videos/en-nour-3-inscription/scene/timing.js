// Single source of truth for timing: voiceover lines drive every beat.
export const VO_DUR = [5.483, 5.696, 6.357, 6.592, 6.272, 6.549, 6.379, 5.397, 5.056];

export const VO_TEXT = [
  "Avant d'inscrire votre enfant, venez tout découvrir. À Ennour trois, une visite vous guide, pas à pas.",
  "Nous vous accueillons avec votre enfant, identifions son niveau, et vous présentons le déroulé de la visite.",
  "Découvrez notre école, notre projet pédagogique, et nos quatre cycles : maternelle, primaire, collège et lycée.",
  "Visitez nos salles de classe, nos laboratoires, la salle informatique, la cour de récréation, et nos espaces communs.",
  "Méthodes d'enseignement, suivi et évaluation, encadrement, communication avec les parents : tout vous est expliqué.",
  "Avec l'application École Plus, suivez la scolarité de votre enfant, et découvrez nos activités complémentaires.",
  "Admission, places disponibles, frais de scolarité, documents, constitution du dossier : les modalités sont claires.",
  "Nous répondons à toutes vos questions, et si vous le souhaitez, nous finalisons ensemble l'inscription.",
  "Ennour trois, l'excellence depuis mille neuf cent soixante-dix-sept. Réservez votre visite.",
];

const GAP = 0.5;
export const L = [];
{
  let t = 0.5;
  VO_DUR.forEach((d, i) => {
    if (i === 8) t += 0.1;
    L.push(Math.round(t * 1000) / 1000);
    t += d + GAP;
  });
}
export const END_HOLD = 1.9;
export const TOTAL = Math.ceil((L[8] + VO_DUR[8] + END_HOLD) * 10) / 10;

// Optional measured word timings (seconds from line start), filled from transcription.
export const WORDS = {};

// Estimated time where `substr` begins inside line i (character-proportional).
export function at(i, substr, offset = 0) {
  const w = WORDS[i]?.[substr];
  if (w !== undefined) return L[i] + w + offset;
  const text = VO_TEXT[i];
  const idx = text.indexOf(substr);
  if (idx < 0) throw new Error(`at(): "${substr}" not in line ${i}`);
  return L[i] + (idx / text.length) * VO_DUR[i] + offset;
}
export const lineEnd = (i) => L[i] + VO_DUR[i];

// camera travel into station i (1..7)
export const DEPART = (i) => L[i] - 0.75;
export const ARRIVE = (i) => L[i] + 0.45;
// overlay scene windows
export const SCENE_START = (i) => (i === 0 ? 0 : L[i] - 0.5);
export const SCENE_END = (i) => (i === 8 ? TOTAL : L[i + 1] - 0.5);

// Captions: [display text, anchor substring in the TTS line]
export const CAPTIONS = [
  [["Avant d'inscrire votre enfant,", "Avant"], ["venez tout découvrir.", "venez"], ["À EN-NOUR 3, une visite", "À Ennour"], ["vous guide, pas à pas.", "vous guide"]],
  [["Nous vous accueillons avec votre enfant,", "Nous"], ["identifions son niveau,", "identifions"], ["et vous présentons le déroulé de la visite.", "et vous"]],
  [["Découvrez notre école,", "Découvrez"], ["notre projet pédagogique,", "notre projet"], ["et nos quatre cycles :", "et nos"], ["maternelle, primaire, collège et lycée.", "maternelle"]],
  [["Visitez nos salles de classe,", "Visitez"], ["nos laboratoires,", "nos laboratoires"], ["la salle informatique,", "la salle"], ["la cour de récréation,", "la cour"], ["et nos espaces communs.", "et nos espaces"]],
  [["Méthodes d'enseignement,", "Méthodes"], ["suivi et évaluation, encadrement,", "suivi"], ["communication avec les parents :", "communication"], ["tout vous est expliqué.", "tout vous"]],
  [["Avec l'application Ecole Plus,", "Avec"], ["suivez la scolarité de votre enfant,", "suivez"], ["et découvrez nos activités complémentaires.", "et découvrez"]],
  [["Admission, places disponibles,", "Admission"], ["frais de scolarité, documents,", "frais"], ["constitution du dossier :", "constitution"], ["les modalités sont claires.", "les modalités"]],
  [["Nous répondons à toutes vos questions,", "Nous"], ["et si vous le souhaitez,", "et si"], ["nous finalisons ensemble l'inscription.", "nous finalisons"]],
  [["EN-NOUR 3, l'excellence depuis 1977.", "Ennour"], ["Réservez votre visite.", "Réservez"]],
];

// Step headers (top overlay). chips: [label, anchor substring or null, dot color]
export const STEPS = [
  null,
  { title: "Accueil du prospect", chips: [["Accueil du parent et de l'enfant", "Nous"], ["Niveau scolaire recherché", "identifions"], ["Déroulé de la visite", "et vous"]] },
  { title: "Présentation de l'établissement", chips: [["Projet pédagogique", "notre projet"], ["4 cycles, de la maternelle au lycée", "et nos"], ["Nos atouts", "maternelle"]] },
  { title: "Visite des infrastructures", chips: [] },
  { title: "Organisation pédagogique", chips: [["Méthodes d'enseignement", "Méthodes"], ["Suivi & évaluation", "suivi"], ["Encadrement", "encadrement"], ["Communication école-parents", "communication"]] },
  { title: "Nos services", chips: [["Application Ecole Plus", "Avec"], ["Suivi scolaire", "suivez"], ["Activités complémentaires", "et découvrez"]] },
  { title: "Modalités d'inscription", chips: [["Conditions d'admission", "Admission"], ["Places disponibles", "places"], ["Frais de scolarité", "frais"], ["Documents nécessaires", "documents"], ["Constitution du dossier", "constitution"]], checklist: true },
  { title: "Conclusion de la visite", chips: [["Réponses à vos questions", "Nous"], ["Vos impressions et besoins", "et si"], ["Finalisation de l'inscription", "nous finalisons"]] },
];
