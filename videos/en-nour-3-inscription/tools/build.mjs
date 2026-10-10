// Generates index.html from scene/timing.js so every data-start matches the voiceover.
// Usage: node tools/build.mjs
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { L, VO_DUR, TOTAL, CAPTIONS, STEPS, SCENE_START, SCENE_END, DEPART, at } from "../scene/timing.js";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const r = (v) => Math.round(v * 1000) / 1000;
const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;");

const CHIP_COLORS = ["#F8B114", "#35B3E5", "#2A91D1", "#F28C5B", "#2F8F4E"];

// ── step headers ──
let steps = "";
for (let i = 1; i <= 7; i++) {
  const st = STEPS[i];
  const s0 = SCENE_START(i), s1 = SCENE_END(i);
  const dots = Array.from({ length: 7 }, (_, k) => `<span class="dot${k + 1 < i ? " done" : ""}${k + 1 === i ? " now" : ""}"></span>`).join("");
  const chips = st.chips
    .map(([label], k) =>
      st.checklist
        ? `<div class="chip check" id="s${i}-chip${k}"><span class="box"><svg viewBox="0 0 24 24"><path d="M5 12.5l4.2 4.2L19 7" /></svg></span>${esc(label)}</div>`
        : `<div class="chip" id="s${i}-chip${k}"><span class="cdot" style="background:${CHIP_COLORS[k % CHIP_COLORS.length]}"></span>${esc(label)}</div>`
    )
    .join("");
  steps += `
      <div id="step-${i}" class="clip step" data-start="${r(s0)}" data-duration="${r(s1 - s0)}" data-track-index="2">
        <div class="step-inner" id="s${i}-inner">
          <div class="step-top"><div class="badge" id="s${i}-badge">ÉTAPE ${i} <span>/ 7</span></div><div class="dots" id="s${i}-dots">${dots}</div></div>
          <h1 class="title" id="s${i}-title">${esc(st.title)}</h1>
          <div class="chips${st.checklist ? " checklist" : ""}">${chips}</div>
        </div>
      </div>`;
}

// ── captions ──
let caps = "";
CAPTIONS.forEach((line, i) => {
  line.forEach(([txt, anchor], k) => {
    const t0 = at(i, anchor, -0.05);
    const t1 = k < line.length - 1 ? at(i, line[k + 1][1], -0.05) : L[i] + VO_DUR[i] + 0.25;
    caps += `
      <div id="cap-${i}-${k}" class="clip cap" data-start="${r(t0)}" data-duration="${r(t1 - t0)}" data-track-index="3"><span class="cap-pill" id="capp-${i}-${k}">${esc(txt)}</span></div>`;
  });
});

// ── audio ──
let audio = "";
VO_DUR.forEach((d, i) => {
  const id = String(i).padStart(2, "0");
  audio += `
      <audio id="vo-${id}" src="assets/vo/vo-${id}.wav" data-start="${r(L[i])}" data-duration="${r(d)}" data-track-index="10" data-volume="1"></audio>`;
});

// ── music bed (carved under the voice in tools/music.py) + sound design ──
audio += `
      <audio id="music" src="assets/music/ennour-chemin-de-lumiere.wav" data-start="0" data-duration="${TOTAL}" data-track-index="11" data-volume="1"></audio>`;
const SFX_DUR = { sparkle: 1.8, whoosh: 0.57, "whoosh-cinematic": 5.5, "whoosh-short": 0.57, chime: 2.54, pop: 0.72, ping: 1.32, notification: 2.45, "click-soft": 0.36 };
const cues = [
  ["sparkle", 0.15, 0.3],
  ["whoosh-cinematic", 1.7, 0.32],
  ["whoosh-short", 3.95, 0.26],
  ["click-soft", 4.6, 0.32],
  ["chime", at(0, "À Ennour", -0.25), 0.3],
];
for (let i = 1; i <= 7; i++) cues.push(["whoosh", DEPART(i) + 0.05, 0.24]);
cues.push(["pop", L[1] + 0.4, 0.26]);
for (let k = 0; k < 4; k++) cues.push(["pop", at(1, "identifions", -0.1 + k * 0.12), 0.16]);
cues.push(["ping", at(1, "niveau", 0.0), 0.22]);
["maternelle", "primaire", "collège", "lycée"].forEach((w) => cues.push(["ping", at(2, w, -0.05), 0.18]));
[["Visitez", 0.55], ["nos laboratoires", 0.4], ["la salle", 0.4], ["la cour", 0.4], ["et nos espaces", 0.4]].forEach(([w, o]) => cues.push(["pop", at(3, w, o), 0.18]));
["Méthodes", "suivi", "encadrement", "communication"].forEach((w) => cues.push(["pop", at(4, w, -0.05), 0.18]));
[at(5, "Avec", 0.9), at(5, "suivez", 0.1), at(5, "suivez", 0.7)].forEach((t) => cues.push(["notification", t, 0.16]));
["Admission", "places", "frais", "documents", "constitution"].forEach((w) => cues.push(["click-soft", at(6, w, 0.15), 0.3]));
cues.push(["whoosh-short", at(6, "documents", -0.2), 0.14]);
cues.push(["pop", L[7] + 0.2, 0.2]);
cues.push(["pop", at(7, "et si", 0.0), 0.2]);
cues.push(["chime", at(7, "nous finalisons", 0.5), 0.34]);
cues.push(["sparkle", at(7, "nous finalisons", 0.5), 0.3]);
cues.push(["sparkle", SCENE_START(8) + 0.7, 0.22]);
cues.push(["chime", at(8, "Réservez", -0.15), 0.3]);
// greedy lane assignment so overlapping effects never share a track
const laneEnd = [];
cues.sort((a, b) => a[1] - b[1]).forEach(([name, t, vol], k) => {
  const d = Math.min(SFX_DUR[name], TOTAL - t);
  let lane = laneEnd.findIndex((end) => end <= t);
  if (lane < 0) lane = laneEnd.push(0) - 1;
  laneEnd[lane] = t + d + 0.01;
  audio += `
      <audio id="sfx-${String(k).padStart(2, "0")}" src="assets/sfx/${name}.mp3" data-start="${r(t)}" data-duration="${r(d)}" data-track-index="${12 + lane}" data-volume="${vol}"></audio>`;
});

const hookEnd = SCENE_END(0);
const ctaStart = SCENE_START(8);

// Two deliverables share one film: 9:16 (index.html) and 16:9 (index-16x9.html).
const FORMATS = [
  { file: "index.html", w: 1080, h: 1920, css: "scene/overlay.css", fmt: "" },
  { file: "index-16x9.html", w: 1920, h: 1080, css: "scene/overlay-16x9.css", fmt: '<script>window.__HF_FORMAT = { w: 1920, h: 1080 };</script>' },
];
for (const F of FORMATS) {
const html = `<!doctype html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=${F.w}, height=${F.h}" />
    <script src="vendor/gsap.min.js"></script>
    <script type="importmap">
      { "imports": { "three": "./vendor/three.module.js", "three/addons/": "./vendor/addons/" } }
    </script>
    <style>
${readFileSync(join(ROOT, F.css), "utf8")}    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="${TOTAL}" data-width="${F.w}" data-height="${F.h}">
      <div id="bg"></div>
      <canvas id="world" width="${F.w}" height="${F.h}" data-layout-allow-overflow></canvas>
      <div id="veil-top"></div>
      <div id="veil-bot"></div>

      <div id="hook" class="clip" data-start="0" data-duration="${r(hookEnd)}" data-track-index="1">
        <div id="hook-title">
          <div class="hl" id="hl-1">Avant d'inscrire</div>
          <div class="hl" id="hl-2">votre enfant,</div>
          <div class="hl accent" id="hl-3">venez tout découvrir.</div>
        </div>
        <div id="hook-brand">
          <img id="hook-logo" src="assets/brand/logo-en-nour-3.png" alt="EN-NOUR 3" />
          <div id="hook-sub">La visite guidée, pas à pas</div>
        </div>
      </div>
${steps}

      <div id="cta" class="clip" data-start="${r(ctaStart)}" data-duration="${r(TOTAL - ctaStart)}" data-track-index="1">
        <div id="cta-card">
          <div id="cta-logo" role="img" aria-label="EN-NOUR 3"></div>
          <div id="cta-cycles">Maternelle · Primaire · Collège · Lycée</div>
          <div id="cta-button">Réservez votre visite</div>
          <div id="cta-sub">Visite guidée de 30 à 40 minutes</div>
          <div id="cta-contacts">
            <div class="ct" id="cta-phone"><svg viewBox="0 0 24 24" class="ic"><path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z" /></svg>+212 5 22 81 00 88</div>
            <div class="ct" id="cta-social"><svg viewBox="0 0 24 24" class="ic stroke"><rect x="3" y="3" width="18" height="18" rx="5" /><circle cx="12" cy="12" r="4.2" /><circle cx="17.4" cy="6.6" r="1.1" class="fill" /></svg><svg viewBox="0 0 24 24" class="ic"><path d="M13.5 21v-7.6h2.6l.4-3h-3V8.5c0-.9.3-1.5 1.5-1.5h1.6V4.3c-.3 0-1.2-.1-2.3-.1-2.3 0-3.9 1.4-3.9 4V10.4H7.8v3h2.6V21z" /></svg>Ecole Ennour 3</div>
          </div>
        </div>
      </div>
${caps}
${audio}
    </div>
    ${F.fmt}
    <script type="module">
      import { boot } from "./scene/main.js";
      window.__timelines["main"] = boot();
    </script>
  </body>
</html>
`;
writeFileSync(join(ROOT, F.file), html);
console.log(`${F.file} written · ${F.w}x${F.h} · duration ${TOTAL}s · lines at ${L.map((x) => x.toFixed(2)).join(", ")}`);
}
