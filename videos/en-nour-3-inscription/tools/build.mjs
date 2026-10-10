// Generates index.html from scene/timing.js so every data-start matches the voiceover.
// Usage: node tools/build.mjs
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { L, VO_DUR, TOTAL, CAPTIONS, STEPS, SCENE_START, SCENE_END, at } from "../scene/timing.js";

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

const hookEnd = SCENE_END(0);
const ctaStart = SCENE_START(8);

const html = `<!doctype html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="vendor/gsap.min.js"></script>
    <script type="importmap">
      { "imports": { "three": "./vendor/three.module.js", "three/addons/": "./vendor/addons/" } }
    </script>
    <style>
${readFileSync(join(ROOT, "scene/overlay.css"), "utf8")}    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="${TOTAL}" data-width="1080" data-height="1920">
      <div id="bg"></div>
      <canvas id="world" width="1080" height="1920" data-layout-allow-overflow></canvas>
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
        </div>
      </div>
${caps}
${audio}
    </div>
    <script type="module">
      import { boot } from "./scene/main.js";
      window.__timelines["main"] = boot();
    </script>
  </body>
</html>
`;
writeFileSync(join(ROOT, "index.html"), html);
console.log(`index.html written · duration ${TOTAL}s · lines at ${L.map((x) => x.toFixed(2)).join(", ")}`);
