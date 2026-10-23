#!/usr/bin/env node
// Writes compositions/*.html and index.html for en-nour-3-communique from one edit list.
//
// Every scene is the same iPad stage (assets/js/stage.js draws the camera, the haptic taps and the
// chips as a pure function of film time); this file only says, per scene, which part of the
// recording plays at which speed, and what the title band says. Times are in frames at 30 fps so
// the scenes tile the 40 s film exactly.
//
//   node tools/build.mjs          # write the files
//   node tools/build.mjs --taps   # print the film time of every source tap (to check stage.js)
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const FPS = 30;
const s = (f) => +(f / FPS).toFixed(6);
const r6 = (v) => +v.toFixed(6);

// Each clip: source in/out (s) of `file`, placed over frames [fs, fe) of its scene.
const SCENES = [
  {
    id: "s0", name: "accroche", f0: 0, frames: 140,
    eyebrow: { text: "COMMUNIQUÉ ÉVALUATIF", at: null, out: 4.45 },
    title: { lines: ["Un DS annoncé", "à 2 classes"], at: 1.333, kind: "slam", size: 80, out: 3.15 },
    clips: [
      { in: 80.9, out: 84.2333, fs: 0, fe: 100 },
      { file: "rembobine", in: 0, out: 1.3333, fs: 100, fe: 140 },
    ],
  },
  {
    id: "s1", name: "ouvrir", f0: 140, frames: 140, step: 1,
    title: { text: "Ouvrir le communiqué", kind: "blur" },
    clips: [
      { in: 17.5, out: 18.3, fs: 0, fe: 24 },
      { in: 19.4, out: 21.45, fs: 24, fe: 63 },
      { in: 22.4, out: 25.25, fs: 63, fe: 120 },
      { in: 25.25, out: 25.7, fs: 120, fe: 140 },
    ],
  },
  {
    id: "s2", name: "classes", f0: 280, frames: 100, step: 2,
    title: { text: "Choisir les classes", kind: "ink" },
    clips: [{ in: 25.7, out: 29.75, fs: 0, fe: 100 }],
  },
  {
    id: "s3", name: "type", f0: 380, frames: 80, step: 3,
    title: { text: "Choisir le type", kind: "blur" },
    clips: [
      { in: 30.2, out: 31.9, fs: 0, fe: 36 },
      { in: 33.16, out: 34.7, fs: 36, fe: 80 },
    ],
  },
  {
    id: "s4", name: "matiere", f0: 460, frames: 80, step: 4,
    title: { text: "Choisir la matière", kind: "line" },
    clips: [{ in: 34.975, out: 38.875, fs: 0, fe: 80 }],
  },
  {
    id: "s5", name: "date", f0: 540, frames: 100, step: 5,
    title: { text: "Fixer la date", kind: "ink" },
    clips: [
      { in: 53.4, out: 54.55, fs: 0, fe: 35 },
      { in: 64.2, out: 64.95, fs: 35, fe: 61 },
      { in: 65.4, out: 66.645, fs: 61, fe: 100 },
    ],
  },
  {
    id: "s6", name: "message", f0: 640, frames: 160, step: 6, eyebrowOut: true,
    title: { text: "Écrire le message", kind: "blur" },
    clips: [
      { in: 67.1, out: 70.2, fs: 0, fe: 78 },
      { in: 70.8, out: 72.7, fs: 78, fe: 116 },
      { in: 73.05, out: 73.7, fs: 116, fe: 131 },
      { in: 74.3, out: 75.433, fs: 131, fe: 160 },
    ],
  },
  {
    id: "s7", name: "envoyer", f0: 800, frames: 80,
    eyebrow: { text: "DERNIER GESTE", at: 0.05, out: 2.48 },
    title: { text: "Envoyer", kind: "line", out: 2.45 },
    clips: [
      { in: 78.7, out: 79.9, fs: 0, fe: 42 },
      { in: 79.9, out: 80.3, fs: 42, fe: 80 },
    ],
  },
  {
    id: "s8", name: "resultat", f0: 880, frames: 120, iris: true,
    eyebrow: { text: "OPÉRATION RÉUSSIE", at: 0.35, out: 3.78 },
    title: { text: "Le DS est publié", kind: "blur", at: 0.45, out: 3.75 },
    clips: [{ in: 80.7, out: 84.7, fs: 0, fe: 120 }],
  },
  {
    id: "s9", name: "fin", f0: 1000, frames: 200, fin: true,
    clips: [{ in: 84.7, out: 85.1, fs: 0, fe: 12 }],
  },
];
const TOTAL = 1200;

// Source times of the real taps (from the recording, frame by frame).
const SOURCE_TAPS = [
  ["☰", 17.62], ["Communiqué évaluatif", 21.27], ["+", 25.18], ["Classes", 25.93], ["T.C.S.F2", 27.65],
  ["Type", 31.15], ["DS", 34.0], ["Matière", 35.95], ["SVT", 37.9], ["Date", 54.05], ["mois suivant", 64.62],
  ["4", 66.0], ["Titre", 67.9], ["touche d", 69.75], ["touche s", 69.95], ["Description", 70.95],
  ["Description (menu)", 72.45], ["Paste", 73.38], ["Envoyer", 80.3],
];

function filmTime(src) {
  for (const sc of SCENES)
    for (const c of sc.clips)
      if (!c.file && src >= c.in && src <= c.out) {
        const rate = (c.out - c.in) / s(c.fe - c.fs);
        return s(sc.f0 + c.fs) + (src - c.in) / rate;
      }
  return null;
}

if (process.argv.includes("--taps")) {
  for (const [name, t] of SOURCE_TAPS) console.log(`${name.padEnd(22)} src ${t.toFixed(2)}  film ${filmTime(t)?.toFixed(3)}`);
  process.exit(0);
}

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

const CHIPS = [
  ["c1", "T.C.S.F1 · T.C.S.F2", 80, 300], ["c2", "DS", 392, 80], ["c3", "SVT", 484, 100],
  ["c4", "04/11/2026", 596, 210], ["c5", "Message", 818, 160],
];

function device(sc) {
  const id = sc.id;
  const videos = sc.clips.map((c, i) => {
    const dur = s(c.fe - c.fs), rate = r6((c.out - c.in) / dur);
    return `            <video id="${id}-v${i + 1}" class="clip" src="assets/footage/${c.file || "ecran"}.mp4" data-start="${s(c.fs)}" data-duration="${dur}" data-media-start="${c.in}" data-playback-rate="${rate}" data-hf-media-start-basis="local" data-track-index="${i + 1}" muted playsinline></video>`;
  }).join("\n");
  const cam = `          <div id="${id}-press" class="st-press">
            <div id="${id}-cam" class="st-cam">
${videos}
            </div>
          </div>`;
  const inner = sc.iris
    ? `          <div id="${id}-flash" class="st-flash"></div>
          <div id="${id}-iris" class="st-iris">
${cam.replace(/^/gm, "  ")}
          </div>`
    : cam;
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

function band(sc) {
  const id = sc.id;
  let eb = "";
  if (sc.step) {
    const nums = sc.step > 1 ? `<span>${sc.step - 1}</span><span>${sc.step}</span>` : `<span>${sc.step}</span>`;
    eb = `ÉTAPE<span class="st-num"><span id="${id}-roll" class="st-roll">${nums}</span></span>/ 6`;
  } else if (sc.eyebrow) eb = esc(sc.eyebrow.text);
  const t = sc.title;
  const title = t.lines
    ? t.lines.map((l) => words(l)).join("<br />")
    : words(t.text);
  const size = t.size ? ` style="font-size: ${t.size}px"` : "";
  return `    <div id="${id}-band" class="st-band">
      <div class="st-eyebrow"><span id="${id}-eline" class="st-line"></span><span id="${id}-etext" class="st-etext">${eb}</span></div>
      <div id="${id}-title" class="st-title"${size}>${title}</div>
    </div>`;
}

function chips(sc) {
  return `    <div class="st-chips">
${CHIPS.map(([c, txt, x, w]) => `      <div id="${sc.id}-${c}" class="st-chip" style="left: ${x}px; width: ${w}px">${esc(txt)}</div>`).join("\n")}
    </div>`;
}

function titleTweens(sc) {
  const id = sc.id, t = sc.title, dur = s(sc.frames);
  const at = t.at ?? 0.12, out = t.out ?? dur - 0.24;
  const W = `"#${id}-title .w"`;
  const enter = {
    blur: `tl.fromTo(${W}, { opacity: 0, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.13, ease: "power2.out", stagger: 0.067 }, ${at});`,
    ink: `tl.fromTo(${W}, { opacity: 0, color: "#6e8186" }, { opacity: 1, duration: 0.06, ease: "none", stagger: 0.08 }, ${at});
      tl.fromTo(${W}, { color: "#6e8186" }, { color: "#e8eeec", duration: 0.12, ease: "power1.out", stagger: 0.08, immediateRender: false }, ${r6(at + 0.1)});`,
    line: `tl.fromTo("#${id}-title", { opacity: 0, filter: "blur(8px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.18, ease: "power2.out" }, ${at});`,
    slam: `tl.fromTo(${W}, { opacity: 0, scale: 1.3, filter: "blur(10px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.22, ease: "expo.out", stagger: 0.08 }, ${at});`,
  }[t.kind];
  const exitSel = t.kind === "line" ? `"#${id}-title"` : W;
  const exit = `tl.fromTo(${exitSel}, { opacity: 1, filter: "blur(0px)" }, { opacity: 0, filter: "blur(8px)", duration: 0.18, ease: "power3.in", stagger: 0.025, immediateRender: false }, ${r6(out)});`;
  return `      ${enter}\n      ${exit}`;
}

function eyebrowTweens(sc) {
  const id = sc.id, dur = s(sc.frames);
  const lines = [];
  const enterEyebrow = (at) => {
    lines.push(`tl.fromTo("#${id}-eline", { scaleX: 0 }, { scaleX: 1, duration: 0.3, ease: "power3.out" }, ${at});`);
    lines.push(`tl.fromTo("#${id}-etext", { opacity: 0, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.16, ease: "power2.out" }, ${r6(at + 0.06)});`);
  };
  const exitEyebrow = (at) =>
    lines.push(`tl.fromTo(["#${id}-eline", "#${id}-etext"], { opacity: 1, filter: "blur(0px)" }, { opacity: 0, filter: "blur(8px)", duration: 0.18, ease: "power3.in", immediateRender: false }, ${r6(at)});`);
  if (sc.step === 1) enterEyebrow(0.05);
  else if (sc.step) lines.push(`tl.fromTo("#${id}-roll", { y: 0 }, { y: -28, duration: 0.22, ease: "power3.inOut" }, 0.06);`);
  else if (sc.eyebrow && sc.eyebrow.at !== null) enterEyebrow(sc.eyebrow.at);
  if (sc.eyebrowOut) exitEyebrow(dur - 0.22);
  else if (sc.eyebrow && sc.eyebrow.out) exitEyebrow(sc.eyebrow.out);
  return lines.map((l) => `      ${l}`).join("\n");
}

function sceneScript(sc) {
  const id = sc.id, T0 = s(sc.f0), dur = s(sc.frames);
  const chipEls = CHIPS.map(([c]) => `${c}: document.getElementById("${id}-${c}")`).join(", ");
  const els = `{ cam: $("cam"), press: $("press"), shake: $("shake"), dot: $("dot"), ring: $("ring")${sc.fin ? "" : `, chips: { ${chipEls} }`} }`;
  const extra = [];
  if (sc.iris) {
    // the tap on « Envoyer » floods the screen amber, then the result irises open from that point
    extra.push(`const o = S.screenPt(29.3, 990, 1406), at = \`\${o.x.toFixed(1)}px \${o.y.toFixed(1)}px\`;
      tl.fromTo("#${id}-iris", { clipPath: \`circle(0px at \${at})\` }, { clipPath: \`circle(1300px at \${at})\`, duration: 0.32, ease: "power2.in" }, 0.05);`);
  }
  if (sc.fin) {
    extra.push(`// the iPad leaves: scale down, drop, blur
      tl.fromTo("#${id}-rig", { opacity: 1, scale: 1, y: 0, filter: "blur(0px)", transformOrigin: "540px 974px" },
        { opacity: 0, scale: 0.9, y: 80, filter: "blur(10px)", duration: 0.4, ease: "power3.in" }, 0);
      // the claim, word by word, then a blur swap to the school's mark
      tl.fromTo("#${id}-claim .w", { opacity: 0, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.14, ease: "power2.out", stagger: 0.1 }, 0.35);
      tl.fromTo("#${id}-claim .w", { opacity: 1, filter: "blur(0px)" }, { opacity: 0, filter: "blur(8px)", duration: 0.18, ease: "power3.in", stagger: 0.03, immediateRender: false }, 2.45);
      tl.fromTo("#${id}-logo", { opacity: 0, y: 36, clipPath: "inset(100% 0% 0% 0%)", filter: "blur(10px)" },
        { opacity: 1, y: 0, clipPath: "inset(0% 0% 0% 0%)", filter: "blur(0px)", duration: 0.6, ease: "expo.out" }, 2.667);
      tl.fromTo("#${id}-endline", { scaleX: 0 }, { scaleX: 1, duration: 0.3, ease: "power3.out" }, 3.15);
      tl.fromTo("#${id}-endtext", { opacity: 0, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.16, ease: "power2.out" }, 3.21);`);
  }
  return `  <script>
    (function () {
      const S = window.STAGE;
      const $ = (k) => document.getElementById("${id}-" + k);
      const tl = gsap.timeline({ paused: true });
      S.drive(tl, ${els}, ${T0}, ${dur});
${sc.fin ? "" : titleTweens(sc) + "\n" + eyebrowTweens(sc) + "\n"}      ${extra.join("\n      ")}
      window.__timelines["${id}"] = tl;
    })();
  </script>`;
}

const FIN_CSS = `
    #s9-claim { position: absolute; left: 80px; top: 690px; font: 700 120px/1.08 "Space Grotesk", sans-serif; letter-spacing: -0.02em;
      color: #e8eeec; white-space: nowrap; }
    #s9-claim .w { display: inline-block; }
    #s9-claim .a { color: #f4a62a; }
    #s9-logo { position: absolute; left: 260px; top: 560px; width: 560px; height: 487px; }
    #s9-end { position: absolute; left: 0; width: 1080px; top: 1120px; display: flex; flex-direction: column; align-items: center; gap: 22px; }
    #s9-endline { display: block; width: 60px; height: 4px; border-radius: 2px; background: #f4a62a; }
    #s9-endtext { font: 600 30px/1 "Space Grotesk", sans-serif; letter-spacing: 0.08em; color: #f4a62a; }`;

function finMarkup() {
  return `    <div id="s9-claim">${words("Un formulaire,")}<br />${words("un envoi.", "w a")}</div>
    <img id="s9-logo" src="assets/brand/logo-en-nour-3.png" alt="EN-NOUR 3" />
    <div id="s9-end"><span id="s9-endline"></span><span id="s9-endtext">COMMUNIQUÉ ÉVALUATIF</span></div>`;
}

function scene(sc) {
  const dur = s(sc.frames);
  return `<template>
  <script src="vendor/gsap.min.js"></script>
  <script src="assets/js/stage.js"></script>
  <style>${FONTS}
${CSS}${sc.fin ? FIN_CSS : ""}
  </style>

  <div id="root" data-composition-id="${sc.id}" data-width="1080" data-height="1920" data-duration="${dur}">
${device(sc)}
${sc.fin ? finMarkup() : band(sc) + "\n" + chips(sc)}
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
    out.push(`      <audio id="sfx-${String(i + 1).padStart(2, "0")}" class="clip" src="${x.path}" data-start="${x.start}" data-duration="${x.duration}" data-track-index="${21 + lane}" data-volume="${x.volume}"></audio>`);
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
  for (const c of sc.clips) if (c.fs < 0 || c.fe > sc.frames) throw new Error(`${sc.id}: clip outside the scene`);
}
if (f !== TOTAL) throw new Error(`scenes end at frame ${f}, expected ${TOTAL}`);

fs.mkdirSync(path.join(ROOT, "compositions"), { recursive: true });
for (const sc of SCENES) fs.writeFileSync(path.join(ROOT, `compositions/${sc.id}-${sc.name}.html`), scene(sc));
fs.writeFileSync(path.join(ROOT, "compositions/progress.html"), PROGRESS);
fs.writeFileSync(path.join(ROOT, "index.html"), index());
console.log(`wrote ${SCENES.length} scenes + progress + index.html (${s(TOTAL)} s)`);
