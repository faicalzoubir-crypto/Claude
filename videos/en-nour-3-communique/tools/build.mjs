#!/usr/bin/env node
// Writes compositions/*.html and index.html for en-nour-3-communique from one edit list.
//
// The teacher's recording plays once, at its own speed, from 0 to 100.73 s: no cut, so film time =
// source time and every scene is a window [f0, f0 + frames) of it. Every scene is the same iPad
// stage (assets/js/stage.js draws the camera, the haptic taps, the chips, the boxes and the
// callouts as a pure function of film time); this file says, per scene, what the title band says
// and the scene's own graphics. Times are in frames at 30 fps so the scenes tile the film exactly.
//
//   node tools/build.mjs
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const FPS = 30;
const TOTAL = 3022; // the recording: 100.733 s
const s = (f) => +(f / FPS).toFixed(6);
const r6 = (v) => +v.toFixed(6);

// beats: what the title band says. eyebrow: {text} or {step, roll}; at/out in scene seconds
// (at: null = already on screen at the scene's first frame).
const SCENES = [
  {
    id: "s0", name: "intro", f0: 0, frames: 405, rail: { at: 9.5, gap: 0.28, out: 12.9 },
    beats: [
      { eyebrow: { text: "COMMUNIQUÉ ÉVALUATIF", at: null, out: 3.4 },
        title: { lines: ["Annoncer un DS", "en 6 gestes"], size: 80, at: null, out: 3.35 } },
      { eyebrow: { text: "AUJOURD'HUI · MER. 14 OCT.", at: 3.75, out: 8.4 },
        title: { text: "Deux classes de SVT", kind: "ink", at: 3.85, out: 8.35 } },
      { eyebrow: { text: "LE PLAN", at: 8.8, out: 12.95 },
        title: { text: "Six gestes", kind: "slam", at: 8.9, out: 12.9 } },
    ],
  },
  { id: "s1", name: "ouvrir", f0: 405, frames: 355,
    beats: [{ eyebrow: { step: 1, at: 0.05 }, title: { text: "Ouvrir le communiqué", kind: "blur" } }] },
  { id: "s2", name: "classes", f0: 760, frames: 140,
    beats: [{ eyebrow: { step: 2, roll: true }, title: { text: "Choisir les classes", kind: "ink" } }] },
  { id: "s3", name: "type", f0: 900, frames: 144,
    beats: [{ eyebrow: { step: 3, roll: true }, title: { text: "Choisir le type", kind: "blur" } }] },
  { id: "s4", name: "matiere", f0: 1044, frames: 114,
    beats: [{ eyebrow: { step: 4, roll: true, out: "end" }, title: { text: "Choisir la matière", kind: "line" } }] },
  {
    id: "s5", name: "rappel", f0: 1158, frames: 342, types: true,
    beats: [
      { eyebrow: { text: "BON À SAVOIR", at: 0.25, out: 4.85 }, title: { text: "5 types d'épreuve", kind: "blur", at: 0.35, out: 4.8 } },
      { eyebrow: { text: "DÉJÀ FAIT", at: 5.6, out: "end" }, title: { text: "3 gestes sur 6", kind: "ink", at: 5.7 } },
    ],
  },
  { id: "s6", name: "date", f0: 1500, frames: 510,
    beats: [{ eyebrow: { step: 5, at: 0.05 }, title: { text: "Fixer la date", kind: "blur" } }] },
  { id: "s7", name: "message", f0: 2010, frames: 351,
    beats: [{ eyebrow: { step: 6, roll: true, out: "end" }, title: { text: "Écrire le message", kind: "blur" } }] },
  { id: "s8", name: "envoyer", f0: 2361, frames: 61, flashAt: 1.6,
    beats: [{ eyebrow: { text: "DERNIER GESTE", at: 0.05, out: 1.55 }, title: { text: "Envoyer", kind: "line", at: 0.1, out: 1.55 } }] },
  { id: "s9", name: "resultat", f0: 2422, frames: 278, iris: true,
    beats: [{ eyebrow: { text: "OPÉRATION RÉUSSIE", at: 0.4, out: "end" }, title: { text: "Le DS est publié", kind: "blur", at: 0.5 } }] },
  { id: "s10", name: "fin", f0: 2700, frames: 322, fin: true, clipFrames: 18 },
];

const esc = (t) => t.replace(/&/g, "&amp;").replace(/</g, "&lt;");
const words = (t, cls = "w") => t.split(" ").map((w) => `<span class="${cls}">${esc(w)}</span>`).join(" ");

const FONTS = `
    @font-face { font-family: "Space Grotesk"; src: url("assets/fonts/space-grotesk-latin-500-normal.woff2") format("woff2"); font-weight: 500; }
    @font-face { font-family: "Space Grotesk"; src: url("assets/fonts/space-grotesk-latin-600-normal.woff2") format("woff2"); font-weight: 600; }
    @font-face { font-family: "Space Grotesk"; src: url("assets/fonts/space-grotesk-latin-700-normal.woff2") format("woff2"); font-weight: 700; }
    @font-face { font-family: "Inter"; src: url("assets/fonts/Inter-Medium.woff2") format("woff2"); font-weight: 500; }
    @font-face { font-family: "Inter"; src: url("assets/fonts/Inter-SemiBold.woff2") format("woff2"); font-weight: 600; }`;

const CSS = `
    #root { position: absolute; inset: 0; overflow: hidden; font-family: "Inter", sans-serif; color: #e8eeec; }
    /* the iPad: bezel + screen (= the recording at 2/3), camera inside the screen */
    .st-rig, .st-shake { position: absolute; inset: 0; }
    .st-bezel { position: absolute; left: 164px; top: 440px; width: 752px; height: 1068px; box-sizing: border-box;
      border-radius: 40px; background: #1b2529; border: 1.5px solid #2e3d44; }
    .st-screen { position: absolute; left: 180px; top: 456px; width: 720px; height: 1036px; border-radius: 24px;
      overflow: hidden; background: #f2f4f6; }
    .st-press, .st-iris, .st-flash { position: absolute; inset: 0; }
    .st-flash { background: #f4a62a; }
    .st-cam { position: absolute; left: 0; top: 0; width: 1080px; height: 1554px; transform-origin: 0 0; }
    .st-cam video { position: absolute; left: 0; top: 0; width: 1080px; height: 1554px; }
    /* the finger: a contact dot and one ring, outlined so they read on white and on navy */
    .st-dot, .st-ring { position: absolute; left: 0; top: 0; width: 64px; height: 64px; border-radius: 50%;
      box-sizing: border-box; opacity: 0; }
    .st-dot { background: rgba(30, 40, 46, 0.32); border: 2.5px solid #ffffff; box-shadow: 0 0 0 1.5px rgba(13, 19, 22, 0.5); }
    .st-ring { border: 3px solid #ffffff; box-shadow: 0 0 0 1.5px rgba(13, 19, 22, 0.4), inset 0 0 0 1.5px rgba(13, 19, 22, 0.4); }
    /* highlight boxes and callouts, drawn in frame pixels over the screen */
    .st-marks { position: absolute; inset: 0; }
    .st-box { position: absolute; left: 0; top: 0; width: 10px; height: 10px; box-sizing: border-box; border: 3px solid #f4a62a;
      border-radius: 12px; opacity: 0; }
    .st-cdot { position: absolute; left: 0; top: 0; width: 18px; height: 18px; border-radius: 50%; background: #f4a62a;
      box-shadow: 0 0 0 3px rgba(13, 19, 22, 0.85); opacity: 0; }
    .st-cline { position: absolute; left: 0; top: 0; width: 2px; height: 10px; background: #f4a62a; opacity: 0; }
    .st-clabel { position: absolute; left: 0; top: 0; height: 50px; box-sizing: border-box; border-radius: 12px; background: #141d21;
      border: 2px solid #f4a62a; color: #e8eeec; font: 600 28px/46px "Space Grotesk", sans-serif; text-align: center;
      white-space: nowrap; opacity: 0; }
    /* title band */
    .st-band { position: absolute; left: 80px; top: 190px; width: 920px; height: 230px; }
    .st-eyebrow { position: absolute; left: 0; top: 0; height: 36px; display: flex; align-items: center; }
    .st-line { display: block; width: 60px; height: 4px; border-radius: 2px; background: #f4a62a; transform-origin: 0 50%; }
    .st-etext { margin-left: 16px; font: 600 28px/28px "Space Grotesk", sans-serif; letter-spacing: 0.08em; color: #f4a62a;
      white-space: nowrap; display: flex; align-items: center; }
    .st-num { display: inline-block; height: 28px; overflow: hidden; margin: 0 0.3em; }
    .st-roll { display: flex; flex-direction: column; }
    .st-roll span { display: block; height: 28px; line-height: 28px; }
    .st-title { position: absolute; left: 0; top: 50px; font: 600 76px/1.05 "Space Grotesk", sans-serif; letter-spacing: -0.02em;
      color: #e8eeec; white-space: nowrap; }
    .st-title .w { display: inline-block; }
    /* value chips */
    .st-chips { position: absolute; inset: 0; }
    .st-chip { position: absolute; top: 352px; height: 48px; box-sizing: border-box; border-radius: 12px; border: 1.5px solid #f4a62a;
      background: #f4a62a; color: #0d1316; font: 600 28px/45px "Space Grotesk", sans-serif; text-align: center; white-space: nowrap; opacity: 0; }`;

const RAIL_CSS = `
    #s0-rail { position: absolute; left: 80px; top: 348px; height: 56px; display: flex; gap: 16px; align-items: center; }
    #s0-rail .ri { display: inline-flex; align-items: center; gap: 8px; font: 600 28px/1 "Space Grotesk", sans-serif; color: #e8eeec;
      white-space: nowrap; }
    #s0-rail .ri b { display: inline-flex; width: 40px; height: 40px; border-radius: 50%; background: #f4a62a; color: #0d1316;
      align-items: center; justify-content: center; font-weight: 700; }`;

const TYPES_CSS = `
    #s5-types { position: absolute; left: 80px; top: 500px; font: 600 76px/1.25 "Space Grotesk", sans-serif; letter-spacing: -0.02em;
      color: #e8eeec; white-space: nowrap; }
    #s5-types .t { display: block; }`;

const FIN_CSS = `
    #s10-claim { position: absolute; left: 80px; top: 690px; font: 700 120px/1.08 "Space Grotesk", sans-serif; letter-spacing: -0.02em;
      color: #e8eeec; white-space: nowrap; }
    #s10-claim .w { display: inline-block; }
    #s10-claim .a { color: #f4a62a; }
    #s10-logo { position: absolute; left: 260px; top: 560px; width: 560px; height: 487px; }
    #s10-end { position: absolute; left: 0; width: 1080px; top: 1120px; display: flex; flex-direction: column; align-items: center; gap: 22px; }
    #s10-endline { display: block; width: 60px; height: 4px; border-radius: 2px; background: #f4a62a; }
    #s10-endtext { font: 600 30px/1 "Space Grotesk", sans-serif; letter-spacing: 0.08em; color: #f4a62a; }`;

const CHIPS = [
  ["c1", "T.C.S.F1 · T.C.S.F2", 80, 300], ["c2", "DS", 392, 80], ["c3", "SVT", 484, 100],
  ["c4", "04/11/2026", 596, 210], ["c5", "Message", 818, 160],
];

function device(sc) {
  const id = sc.id;
  const fe = sc.clipFrames ?? sc.frames;
  const video = `            <video id="${id}-v1" class="clip" src="assets/footage/ecran.mp4" data-start="0" data-duration="${s(fe)}" data-media-start="${s(sc.f0)}" data-playback-rate="1" data-hf-media-start-basis="local" data-track-index="1" muted playsinline></video>`;
  const cam = `          <div id="${id}-press" class="st-press">
            <div id="${id}-cam" class="st-cam">
${video}
            </div>
          </div>`;
  let inner = cam;
  if (sc.iris) inner = `          <div id="${id}-flash" class="st-flash"></div>
          <div id="${id}-iris" class="st-iris">
${cam.replace(/^/gm, "  ")}
          </div>`;
  if (sc.flashAt) inner = `${cam}
          <div id="${id}-flash" class="st-flash" style="opacity: 0"></div>`;
  return `    <div id="${id}-rig" class="st-rig">
      <div id="${id}-shake" class="st-shake">
        <div class="st-bezel"></div>
        <div class="st-screen">
${inner}
          <div id="${id}-dot" class="st-dot"></div>
          <div id="${id}-ring" class="st-ring"></div>
        </div>
      </div>
    </div>`;
}

const marks = (sc) => `    <div class="st-marks">
      <div id="${sc.id}-box1" class="st-box"></div><div id="${sc.id}-box2" class="st-box"></div><div id="${sc.id}-box3" class="st-box"></div>
      <div id="${sc.id}-cline" class="st-cline"></div><div id="${sc.id}-cdot" class="st-cdot"></div><div id="${sc.id}-clabel" class="st-clabel"></div>
    </div>`;

function band(sc) {
  const id = sc.id;
  return sc.beats.map((b, k) => {
    const e = b.eyebrow;
    let eb;
    if (e.step) {
      const nums = e.roll ? `<span>${e.step - 1}</span><span>${e.step}</span>` : `<span>${e.step}</span>`;
      eb = `ÉTAPE<span class="st-num"><span id="${id}-b${k}-roll" class="st-roll">${nums}</span></span>/ 6`;
    } else eb = esc(e.text);
    const t = b.title;
    const title = t.lines ? t.lines.map((l) => words(l)).join("<br />") : words(t.text);
    const size = t.size ? ` style="font-size: ${t.size}px"` : "";
    return `    <div id="${id}-b${k}" class="st-band">
      <div class="st-eyebrow"><span id="${id}-b${k}-eline" class="st-line"></span><span id="${id}-b${k}-etext" class="st-etext">${eb}</span></div>
      <div id="${id}-b${k}-title" class="st-title"${size}>${title}</div>
    </div>`;
  }).join("\n");
}

const chips = (sc) => `    <div class="st-chips">
${CHIPS.map(([c, txt, x, w]) => `      <div id="${sc.id}-${c}" class="st-chip" style="left: ${x}px; width: ${w}px">${esc(txt)}</div>`).join("\n")}
    </div>`;

function beatTweens(sc) {
  const id = sc.id, dur = s(sc.frames), out = [];
  const endAt = (v, back) => (v === "end" ? dur - back : v);
  sc.beats.forEach((b, k) => {
    const P = `#${id}-b${k}`, W = `"${P}-title .w"`, t = b.title, e = b.eyebrow;
    // eyebrow
    if (e.roll) out.push(`tl.fromTo("${P}-roll", { y: 0 }, { y: -28, duration: 0.22, ease: "power3.inOut" }, 0.06);`);
    else if (e.at !== null) {
      out.push(`tl.fromTo("${P}-eline", { scaleX: 0 }, { scaleX: 1, duration: 0.3, ease: "power3.out" }, ${e.at});`);
      out.push(`tl.fromTo("${P}-etext", { opacity: 0, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.16, ease: "power2.out" }, ${r6(e.at + 0.06)});`);
    }
    if (e.out !== undefined)
      out.push(`tl.fromTo(["${P}-eline", "${P}-etext"], { opacity: 1, filter: "blur(0px)" }, { opacity: 0, filter: "blur(8px)", duration: 0.18, ease: "power3.in", immediateRender: false }, ${r6(endAt(e.out, 0.22))});`);
    // title
    const at = t.at === undefined ? 0.12 : t.at;
    if (at !== null) {
      out.push({
        blur: `tl.fromTo(${W}, { opacity: 0, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.13, ease: "power2.out", stagger: 0.067 }, ${at});`,
        ink: `tl.fromTo(${W}, { opacity: 0, color: "#6e8186" }, { opacity: 1, duration: 0.06, ease: "none", stagger: 0.08 }, ${at});
      tl.fromTo(${W}, { color: "#6e8186" }, { color: "#e8eeec", duration: 0.12, ease: "power1.out", stagger: 0.08, immediateRender: false }, ${r6(at + 0.1)});`,
        line: `tl.fromTo("${P}-title", { opacity: 0, filter: "blur(8px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.18, ease: "power2.out" }, ${at});`,
        slam: `tl.fromTo(${W}, { opacity: 0, scale: 1.3, filter: "blur(10px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.22, ease: "expo.out", stagger: 0.08 }, ${at});`,
      }[t.kind]);
    }
    const tOut = t.out === undefined ? dur - 0.24 : t.out;
    const exitSel = t.kind === "line" ? `"${P}-title"` : W;
    out.push(`tl.fromTo(${exitSel}, { opacity: 1, filter: "blur(0px)" }, { opacity: 0, filter: "blur(8px)", duration: 0.18, ease: "power3.in", stagger: 0.025, immediateRender: false }, ${r6(tOut)});`);
  });
  return out.map((l) => `      ${l}`).join("\n");
}

function extraTweens(sc) {
  const id = sc.id, x = [];
  if (sc.rail) {
    const r = sc.rail;
    x.push(`// the plan: the six steps, one by one
      tl.fromTo("#s0-rail .ri", { opacity: 0, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.16, ease: "power2.out", stagger: ${r.gap} }, ${r.at});
      tl.fromTo("#s0-rail .ri", { opacity: 1, filter: "blur(0px)" }, { opacity: 0, filter: "blur(8px)", duration: 0.18, ease: "power3.in", stagger: 0.03, immediateRender: false }, ${r.out});`);
  }
  if (sc.types) {
    x.push(`// the iPad steps aside for the five real types of the « Type » list, then comes back
      tl.fromTo("#${id}-rig", { y: 0 }, { y: 1500, duration: 0.5, ease: "power3.in" }, 0.15);
      tl.fromTo("#s5-types .t", { opacity: 0, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.14, ease: "power2.out", stagger: 0.16 }, 0.8);
      tl.fromTo("#s5-types .t:not(.a)", { color: "#e8eeec" }, { color: "#6e8186", duration: 0.25, ease: "power1.out", immediateRender: false }, 2.4);
      tl.fromTo("#s5-types .a", { color: "#e8eeec" }, { color: "#f4a62a", duration: 0.25, ease: "power1.out", immediateRender: false }, 2.4);
      tl.fromTo("#s5-types .t", { opacity: 1, filter: "blur(0px)" }, { opacity: 0, filter: "blur(8px)", duration: 0.18, ease: "power3.in", stagger: 0.04, immediateRender: false }, 4.6);
      tl.fromTo("#${id}-rig", { y: 1500 }, { y: 0, duration: 0.7, ease: "expo.out", immediateRender: false }, 5.0);`);
  }
  if (sc.flashAt) {
    x.push(`// the tap on « Envoyer » floods the screen amber
      tl.fromTo("#${id}-flash", { opacity: 0 }, { opacity: 1, duration: 0.04, ease: "none" }, ${sc.flashAt});`);
  }
  if (sc.iris) {
    x.push(`// …and the published list irises open from the « Envoyer » point
      const o = S.screenPt(80.25, 990, 1406), at = \`\${o.x.toFixed(1)}px \${o.y.toFixed(1)}px\`;
      tl.fromTo("#${id}-iris", { clipPath: \`circle(0px at \${at})\` }, { clipPath: \`circle(1300px at \${at})\`, duration: 0.28, ease: "power2.in" }, 0);`);
  }
  if (sc.fin) {
    x.push(`// the iPad leaves: scale down, drop, blur
      tl.fromTo("#${id}-rig", { opacity: 1, scale: 1, y: 0, filter: "blur(0px)", transformOrigin: "540px 974px" },
        { opacity: 0, scale: 0.9, y: 80, filter: "blur(10px)", duration: 0.4, ease: "power3.in" }, 0);
      // the claim, word by word, then a blur swap to the school's mark
      tl.fromTo("#${id}-claim .w", { opacity: 0, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.14, ease: "power2.out", stagger: 0.1 }, 0.45);
      tl.fromTo("#${id}-claim .w", { opacity: 1, filter: "blur(0px)" }, { opacity: 0, filter: "blur(8px)", duration: 0.18, ease: "power3.in", stagger: 0.03, immediateRender: false }, 4.0);
      tl.fromTo("#${id}-logo", { opacity: 0, y: 36, clipPath: "inset(100% 0% 0% 0%)", filter: "blur(10px)" },
        { opacity: 1, y: 0, clipPath: "inset(0% 0% 0% 0%)", filter: "blur(0px)", duration: 0.6, ease: "expo.out" }, 4.3);
      tl.fromTo("#${id}-endline", { scaleX: 0 }, { scaleX: 1, duration: 0.3, ease: "power3.out" }, 4.75);
      tl.fromTo("#${id}-endtext", { opacity: 0, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.16, ease: "power2.out" }, 4.81);`);
  }
  return x.length ? `      ${x.join("\n      ")}\n` : "";
}

function sceneScript(sc) {
  const id = sc.id, T0 = s(sc.f0), dur = s(sc.frames);
  const chipEls = CHIPS.map(([c]) => `${c}: $("${c}")`).join(", ");
  const els = sc.fin
    ? `{ cam: $("cam"), press: $("press"), shake: $("shake"), dot: $("dot"), ring: $("ring") }`
    : `{ cam: $("cam"), press: $("press"), shake: $("shake"), dot: $("dot"), ring: $("ring"), chips: { ${chipEls} },
        boxes: [$("box1"), $("box2"), $("box3")], callout: { dot: $("cdot"), line: $("cline"), label: $("clabel") } }`;
  return `  <script>
    (function () {
      const S = window.STAGE;
      const $ = (k) => document.getElementById("${id}-" + k);
      const tl = gsap.timeline({ paused: true });
      S.drive(tl, ${els}, ${T0}, ${dur});
${sc.beats ? beatTweens(sc) + "\n" : ""}${extraTweens(sc)}      window.__timelines["${id}"] = tl;
    })();
  </script>`;
}

function sceneMarkup(sc) {
  if (sc.fin)
    return `    <div id="s10-claim" data-hold>${words("Un formulaire,")}<br />${words("un envoi.", "w a")}</div>
    <img id="s10-logo" src="assets/brand/logo-en-nour-3.png" alt="EN-NOUR 3" />
    <div id="s10-end"><span id="s10-endline"></span><span id="s10-endtext">COMMUNIQUÉ ÉVALUATIF</span></div>`;
  const parts = [marks(sc), band(sc), chips(sc)];
  if (sc.rail)
    parts.push(`    <div id="s0-rail">${["Menu", "Classes", "Type", "Matière", "Date", "Message"].map((w, i) => `<span class="ri"><b>${i + 1}</b>${w}</span>`).join("")}</div>`);
  if (sc.types)
    parts.push(`    <div id="s5-types"><span class="t a">DS</span><span class="t">DM</span><span class="t">Contrôle</span><span class="t">Évaluation</span><span class="t">Évaluation d'étape</span></div>`);
  return parts.join("\n");
}

function scene(sc) {
  const extraCss = (sc.rail ? RAIL_CSS : "") + (sc.types ? TYPES_CSS : "") + (sc.fin ? FIN_CSS : "");
  return `<template>
  <script src="vendor/gsap.min.js"></script>
  <script src="assets/js/stage.js"></script>
  <style>${FONTS}
${CSS}${extraCss}
  </style>

  <div id="root" data-composition-id="${sc.id}" data-width="1080" data-height="1920" data-duration="${s(sc.frames)}">
${device(sc)}
${sceneMarkup(sc)}
  </div>

${sceneScript(sc)}
</template>
`;
}

const PROGRESS = `<template>
  <script src="vendor/gsap.min.js"></script>
  <style>
    #root { position: absolute; inset: 0; overflow: hidden; }
    #progress-bar { position: absolute; left: 0; bottom: 0; width: 1080px; height: 4px; background: #f4a62a; transform-origin: 0 50%; }
  </style>
  <div id="root" data-composition-id="progress" data-width="1080" data-height="1920" data-duration="${s(TOTAL)}">
    <div id="progress-bar" data-layout-ignore></div>
  </div>
  <script>
    (function () {
      const tl = gsap.timeline({ paused: true });
      tl.fromTo("#progress-bar", { scaleX: 0 }, { scaleX: 1, duration: ${s(TOTAL)}, ease: "none" }, 0);
      window.__timelines["progress"] = tl;
    })();
  </script>
</template>
`;

function audioTags() {
  const f = path.join(ROOT, "tools/sound.json");
  if (!fs.existsSync(f)) return "";
  const snd = JSON.parse(fs.readFileSync(f, "utf8"));
  const out = [`      <!-- music: tools/music.py (brand bed, 90 BPM, D minor) -->`];
  out.push(`      <audio id="music" class="clip" src="${snd.music.path}" data-start="0" data-duration="${snd.music.duration}" data-track-index="20" data-volume="${snd.music.volume}"></audio>`);
  out.push(`      <!-- sound on every visible action: taps, chips, whooshes, riser and impact -->`);
  const ends = []; // one Studio lane per sound that would overlap another
  snd.sfx.forEach((x, i) => {
    let lane = ends.findIndex((e) => e <= x.start);
    if (lane < 0) lane = ends.push(0) - 1;
    ends[lane] = x.start + x.duration;
    const fade = x.fadeOut ? ` data-fade-out="${x.fadeOut}"` : "";
    out.push(`      <audio id="sfx-${String(i + 1).padStart(2, "0")}" class="clip" src="${x.path}" data-start="${x.start}" data-duration="${x.duration}" data-track-index="${21 + lane}" data-volume="${x.volume}"${fade}></audio>`);
  });
  return out.join("\n");
}

function index() {
  const hosts = SCENES.map((sc) => `      <div
        id="${sc.id}"
        class="scene"
        data-composition-id="${sc.id}"
        data-composition-src="compositions/${sc.id}-${sc.name}.html"
        data-start="${s(sc.f0)}"
        data-duration="${s(sc.frames)}"
        data-track-index="1"
        data-track-kind="graphics"
      ></div>`).join("\n");
  return `<!doctype html>
<html lang="fr" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="vendor/gsap.min.js"></script>
    <style>
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #0d1316; }
      #root { position: relative; width: 1080px; height: 1920px; overflow: hidden; }
      /* the house ground: #0D1316 with a 60 px hairline grid (#26343B at 55 %) */
      #ground { position: absolute; inset: 0; background-color: #0d1316;
        background-image: linear-gradient(to right, rgba(38, 52, 59, 0.55) 1px, transparent 1px),
          linear-gradient(to bottom, rgba(38, 52, 59, 0.55) 1px, transparent 1px);
        background-size: 60px 60px; background-position: 0 0; }
      .scene { position: absolute; inset: 0; }
    </style>
  </head>
  <body>
    <div
      id="root"
      data-composition-id="main"
      data-start="0"
      data-duration="${s(TOTAL)}"
      data-width="1080"
      data-height="1920"
    >
      <div id="ground"></div>

${hosts}
      <div
        id="progress"
        class="scene"
        data-composition-id="progress"
        data-composition-src="compositions/progress.html"
        data-start="0"
        data-duration="${s(TOTAL)}"
        data-track-index="2"
        data-track-kind="graphics"
      ></div>

${audioTags()}
    </div>
    <script>
      window.__timelines = window.__timelines || {};
      window.__timelines["main"] = gsap.timeline({ paused: true });
    </script>
  </body>
</html>
`;
}

// sanity: scenes tile the film
let f = 0;
for (const sc of SCENES) {
  if (sc.f0 !== f) throw new Error(`${sc.id} starts at frame ${sc.f0}, expected ${f}`);
  f += sc.frames;
}
if (f !== TOTAL) throw new Error(`scenes end at frame ${f}, expected ${TOTAL}`);

fs.mkdirSync(path.join(ROOT, "compositions"), { recursive: true });
for (const old of fs.readdirSync(path.join(ROOT, "compositions"))) fs.unlinkSync(path.join(ROOT, "compositions", old));
for (const sc of SCENES) fs.writeFileSync(path.join(ROOT, `compositions/${sc.id}-${sc.name}.html`), scene(sc));
fs.writeFileSync(path.join(ROOT, "compositions/progress.html"), PROGRESS);
fs.writeFileSync(path.join(ROOT, "index.html"), index());
console.log(`wrote ${SCENES.length} scenes + progress + index.html (${s(TOTAL)} s)`);
