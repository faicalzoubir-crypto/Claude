// Shared visual kit for every frame of « La frise en flammes » — the PDF's components
// (frise, act banner, event card, arrow strip, navy box) and its icons, redrawn as SVG.
// tools/build_frames.mjs wraps each frame with wrap() into compositions/frames/NN-*.html.

export const W = 1920;
export const H = 1080;

export const ACT = {
  1: { c: "#C0392B", tint: "#FDECEA", n: "1", years: "1789", fire: "L'embrasement", title: "Le grand saut dans la Révolution" },
  2: { c: "#D68910", tint: "#FDF3E1", n: "2", years: "1790 — 1791", fire: "Le feu couve", title: "L'impasse d'une nouvelle France avec le roi" },
  3: { c: "#2C5AA0", tint: "#E8EEF8", n: "3", years: "1792", fire: "Le brasier se réveille", title: "Chute de la monarchie et naissance de la République" },
  4: { c: "#7B1D14", tint: "#F6E6E4", n: "4", years: "1793 — 1794", fire: "La fureur des flammes", title: "La mort du roi et la Terreur" },
  5: { c: "#5D6D7E", tint: "#ECEFF1", n: "5", years: "1795 — 1799", fire: "Sous les cendres", title: "La fin douloureuse d'une révolution pleine de promesses" },
};

const FONTS = `
@font-face{font-family:"Merriweather";src:url("assets/fonts/merriweather-latin-900-normal.woff2") format("woff2");font-weight:900;font-style:normal}
@font-face{font-family:"Merriweather";src:url("assets/fonts/merriweather-latin-700-normal.woff2") format("woff2");font-weight:700;font-style:normal}
@font-face{font-family:"Merriweather";src:url("assets/fonts/merriweather-latin-400-normal.woff2") format("woff2");font-weight:400;font-style:normal}
@font-face{font-family:"Merriweather";src:url("assets/fonts/merriweather-latin-400-italic.woff2") format("woff2");font-weight:400;font-style:italic}
@font-face{font-family:"Inter";src:url("assets/fonts/inter-latin-wght-normal.woff2") format("woff2");font-weight:100 900;font-style:normal}
@font-face{font-family:"JetBrains Mono";src:url("assets/fonts/jetbrains-mono-latin-500-normal.woff2") format("woff2");font-weight:500;font-style:normal}
`;

const BASE = `
#root{position:absolute;inset:0;width:1920px;height:1080px;overflow:hidden;
  --paper:#FFFDF7;--card:#FFF8E6;--ink:#2B2118;--ink-soft:#6B5A3A;--brown:#7A5A3A;--gold:#D4A017;--gold-soft:#E3BF63;
  --navy:#1B3A6B;--gold-ink:#A67A0F;--blue:#2C5AA0;--red:#C0392B;--a1:#C0392B;--a2:#D68910;--a3:#2C5AA0;--a4:#7B1D14;--a5:#5D6D7E;
  font-family:"Inter",sans-serif;color:var(--ink)}
.ground{position:absolute;inset:0;background:
  radial-gradient(1200px 700px at 50% 45%, rgba(255,255,255,0.7), rgba(255,255,255,0) 70%),
  radial-gradient(900px 600px at 15% 90%, rgba(228,177,96,0.10), rgba(228,177,96,0) 70%),
  radial-gradient(900px 600px at 90% 10%, rgba(228,177,96,0.08), rgba(228,177,96,0) 70%),
  #FFFDF7}
.band{position:absolute;top:0;bottom:0;width:40px}
.band.l{left:0;background:var(--blue)}
.band.r{right:0;background:var(--red)}
.abs{position:absolute}
.mono{font-family:"JetBrains Mono",monospace;font-weight:500;text-transform:uppercase;letter-spacing:0.22em}
.serif{font-family:"Merriweather",serif}
b,strong{font-weight:700}

/* — frise strip — */
.frise{position:absolute;height:64px}
.frise .bar{position:absolute;left:0;right:0;top:34px;height:14px;display:flex;border-radius:7px;overflow:hidden}
.frise .seg{height:100%}
.frise .seg.off{opacity:0.22}
.frise .yr{position:absolute;top:0;font:700 20px/1 "Inter";color:var(--ink-soft);transform:translateX(-50%);white-space:nowrap}
.frise .tick{position:absolute;top:28px;width:3px;height:26px;margin-left:-1.5px;background:var(--ink);border-radius:2px;opacity:0.55}

/* — flame — */
.flame{position:absolute;width:70px;height:98px;margin-left:-35px}
.flame .glow{position:absolute;left:50%;top:58%;width:260px;height:260px;margin:-130px 0 0 -130px;border-radius:50%;
  background:radial-gradient(circle, rgba(255,196,77,0.55) 0%, rgba(245,166,35,0.25) 35%, rgba(245,166,35,0) 70%)}
.flame .fi{position:absolute;inset:0}
.flame svg{position:absolute;inset:0;width:100%;height:100%;overflow:visible}

/* — act banner (PDF act header) — */
.banner{position:absolute;display:flex;align-items:center;border-radius:14px;color:#fff;padding:0 40px;gap:30px;box-shadow:0 10px 30px rgba(43,33,24,0.10)}
.banner .num{display:flex;flex-direction:column;align-items:center;justify-content:center;min-width:92px}
.banner .num .k{font:500 20px/1 "JetBrains Mono";letter-spacing:0.28em;opacity:0.9}
.banner .num .n{font:900 76px/1 "Merriweather";margin-top:6px}
.banner .sep{width:2px;align-self:stretch;margin:22px 0;background:rgba(255,255,255,0.55)}
.banner .txt{display:flex;flex-direction:column;gap:6px}
.banner .fire{font:italic 400 26px/1.2 "Merriweather";opacity:0.92}
.banner .ttl{font:900 46px/1.12 "Merriweather"}
.banner .yrs{font:700 24px/1 "Inter";opacity:0.95}
.slim{position:absolute;display:flex;align-items:center;gap:18px;height:64px;padding:0 28px;border-radius:12px;color:#fff;font:700 26px/1 "Inter"}
.slim .k{font:500 20px/1 "JetBrains Mono";letter-spacing:0.24em}
.slim .f{font:italic 400 24px/1 "Merriweather";opacity:0.92}

/* — event card — */
.card{position:absolute;background:#fff;border:2px solid var(--gold-soft);border-radius:14px;padding:84px 34px 30px;box-shadow:0 8px 24px rgba(43,33,24,0.08)}
.card.star{border-width:3px}
.card .medal{position:absolute;top:-52px;left:30px;width:112px;height:112px;border-radius:50%;background:#fff;border:5px solid var(--gold-soft);display:flex;align-items:center;justify-content:center}
.card .medal svg{width:70px;height:70px}
.pill{display:inline-block;padding:9px 16px 8px;border-radius:8px;color:#fff;font:700 26px/1 "Inter";white-space:nowrap}
.card .pill{position:absolute;top:28px;left:160px}
.card .ct{font:700 40px/1.18 "Merriweather";margin-top:4px}
.card .ct .st{color:var(--gold-ink)}
.card .cl{font:500 29px/1.38 "Inter";margin-top:16px;color:var(--ink)}
.card .cl b{font-weight:700}

/* — arrow strip (PDF « → … » conclusion) — */
.arrow{position:absolute;display:flex;align-items:center;gap:18px;background:var(--card);border-left:8px solid var(--gold);border-radius:10px;padding:0 34px;font:500 32px/1.3 "Inter";color:var(--ink)}
.arrow .ar{font:900 40px/1 "Merriweather";color:var(--gold-ink)}
.arrow b{font-weight:800}

/* — navy box (problématique / réponse) — */
.navy{position:absolute;background:var(--navy);border-radius:18px;color:#fff;box-shadow:0 18px 40px rgba(27,58,107,0.25)}
.navy .lab{font:500 24px/1 "JetBrains Mono";letter-spacing:0.32em;color:#AEB8C5;text-align:center}
.gold{color:#E3BF63}

.tag{position:absolute;display:flex;align-items:center;gap:20px;background:#fff;border:2px solid var(--gold-soft);border-radius:12px;padding:0 26px;font:500 29px/1.3 "Inter"}
.tag svg{width:56px;height:56px;flex:none}
.credit{position:absolute;font:500 15px/1 "Inter";color:var(--ink-soft);opacity:0.8}
`;

// ── icons (viewBox 0 0 64 64), flat, warm browns + one accent ──────────────
const INK = "#4A3526";
export function icon(name, accent = "#C0392B") {
  const s = `stroke="${INK}" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"`;
  const I = {
    crown: `<path d="M10 46 L8 20 L22 32 L32 14 L42 32 L56 20 L54 46 Z" fill="#E4B33A" ${s}/><rect x="10" y="46" width="44" height="8" rx="2" fill="#D4A017" ${s}/><circle cx="32" cy="36" r="4" fill="${accent}"/><circle cx="20" cy="40" r="2.6" fill="#2C5AA0"/><circle cx="44" cy="40" r="2.6" fill="#2C5AA0"/>`,
    hand: `<path d="M22 58 C16 50 14 44 14 36 L14 26 C14 23 18 23 18 26 L18 33 L18 14 C18 10.5 23 10.5 23 14 L23 31 L23 10 C23 6.5 28 6.5 28 10 L28 31 L28 12 C28 8.5 33 8.5 33 12 L33 32 L33 17 C33 13.5 38 13.5 38 17 L38 40 C38 50 34 56 30 58 Z" fill="#F0CFAE" ${s}/>`,
    bastille: `<rect x="8" y="24" width="14" height="34" fill="#9C7B57" ${s}/><rect x="42" y="24" width="14" height="34" fill="#9C7B57" ${s}/><rect x="20" y="32" width="24" height="26" fill="#B89270" ${s}/><path d="M8 24 v-5 h4 v4 h3 v-4 h4 v4 h3 v5 M42 24 v-5 h4 v4 h3 v-4 h4 v4 h3 v5" fill="none" ${s}/><path d="M28 58 v-10 a4 4 0 0 1 8 0 v10" fill="#4A3526"/><path d="M15 16 C13 12 16 9 15 5 C19 8 20 12 17 16 Z" fill="${accent}"/><path d="M49 16 C47 12 50 9 49 5 C53 8 54 12 51 16 Z" fill="#F5A623"/>`,
    flame: `<path d="M32 6 C36 18 50 24 50 40 C50 52 42 58 32 58 C22 58 14 52 14 40 C14 30 20 26 22 16 C25 24 28 26 30 27 C30 20 29 13 32 6 Z" fill="#E2501C" ${s}/><path d="M32 26 C34 34 42 38 42 46 C42 53 37 56 32 56 C27 56 22 53 22 46 C22 40 27 37 28 31 C30 35 31 36 32 36 Z" fill="#F5A623"/><path d="M32 40 C33 45 37 47 37 51 C37 54 35 55 32 55 C29 55 27 54 27 51 C27 48 30 46 32 40 Z" fill="#FFE08A"/>`,
    scroll: `<rect x="14" y="10" width="36" height="44" rx="3" fill="#F6E7C1" ${s}/><path d="M10 10 h44 M10 54 h44" ${s}/><circle cx="10" cy="10" r="4" fill="#E0C48C" ${s}/><circle cx="54" cy="10" r="4" fill="#E0C48C" ${s}/><circle cx="10" cy="54" r="4" fill="#E0C48C" ${s}/><circle cx="54" cy="54" r="4" fill="#E0C48C" ${s}/><path d="M21 20 h22 M21 27 h22 M21 34 h22 M21 41 h14" stroke="#9C7B57" stroke-width="2.4" stroke-linecap="round"/>`,
    bread: `<path d="M8 40 C8 26 20 20 32 20 C44 20 56 26 56 40 C56 46 52 48 46 48 L18 48 C12 48 8 46 8 40 Z" fill="#D59A4E" ${s}/><path d="M20 30 l6 10 M30 27 l6 11 M40 28 l5 10" stroke="#8C5A22" stroke-width="2.4" stroke-linecap="round"/><path d="M32 8 v6" stroke="${accent}" stroke-width="3" stroke-linecap="round"/><path d="M29 12 l3 -5 l3 5" fill="${accent}"/>`,
    carriage: `<path d="M12 22 h40 v18 a4 4 0 0 1 -4 4 h-32 a4 4 0 0 1 -4 -4 Z" fill="#2B3A55" ${s}/><rect x="18" y="26" width="11" height="9" rx="1.5" fill="#F6E7C1"/><rect x="35" y="26" width="11" height="9" rx="1.5" fill="#F6E7C1"/><path d="M10 22 h44" ${s}/><circle cx="20" cy="50" r="8" fill="#F5D88A" ${s}/><circle cx="44" cy="50" r="8" fill="#F5D88A" ${s}/><path d="M20 43 v14 M13 50 h14 M44 43 v14 M37 50 h14" stroke="${INK}" stroke-width="1.8"/><circle cx="56" cy="14" r="4" fill="#E4B33A"/>`,
    guillotine: `<rect x="14" y="6" width="6" height="52" fill="#8C5A22" ${s}/><rect x="44" y="6" width="6" height="52" fill="#8C5A22" ${s}/><rect x="10" y="4" width="44" height="7" fill="#6E4419" ${s}/><path class="blade" d="M20 14 h24 v8 l-24 6 Z" fill="#C9D2DA" ${s}/><rect x="10" y="50" width="44" height="8" fill="#6E4419" ${s}/><circle cx="32" cy="44" r="5" fill="none" stroke="${INK}" stroke-width="2.4"/>`,
    bonnet: `<path d="M12 50 C10 34 18 16 34 12 C44 10 52 16 50 24 C48 30 42 28 42 24 C46 32 50 40 50 50 Z" fill="#C0392B" ${s}/><rect x="10" y="48" width="42" height="8" rx="3" fill="#A93226" ${s}/><circle cx="24" cy="40" r="6" fill="#fff" stroke="${INK}" stroke-width="1.6"/><circle cx="24" cy="40" r="4" fill="#C0392B"/><circle cx="24" cy="40" r="2" fill="#2C5AA0"/>`,
    scales: `<path d="M32 10 v42 M18 56 h28" ${s}/><path d="M12 18 h40" ${s}/><circle cx="32" cy="10" r="3" fill="#D4A017" ${s}/><path d="M12 18 l-6 16 h12 Z M52 18 l-6 16 h12 Z" fill="#E4B33A" ${s}/>`,
    temple: `<path d="M8 22 L32 8 L56 22 Z" fill="#E6DCC4" ${s}/><rect x="10" y="22" width="44" height="5" fill="#D8CBAA" ${s}/><path d="M15 27 v20 M24 27 v20 M33 27 v20 M42 27 v20 M50 27 v20" stroke="${INK}" stroke-width="4"/><rect x="8" y="47" width="48" height="6" fill="#D8CBAA" ${s}/><rect x="6" y="53" width="52" height="5" fill="#C9BB97" ${s}/>`,
    bicorne: `<path d="M6 40 C14 26 24 22 32 22 C40 22 50 26 58 40 C50 37 42 36 32 36 C22 36 14 37 6 40 Z" fill="#1E1A17" ${s}/><path d="M10 40 C20 44 44 44 54 40" fill="none" stroke="#D4A017" stroke-width="2.4"/><circle cx="42" cy="30" r="5" fill="#fff" stroke="${INK}" stroke-width="1.4"/><circle cx="42" cy="30" r="3.4" fill="#C0392B"/><circle cx="42" cy="30" r="1.6" fill="#2C5AA0"/>`,
    swords: `<path d="M12 12 L46 46 M52 12 L18 46" stroke="#AEB8C5" stroke-width="5" stroke-linecap="round"/><path d="M12 12 L46 46 M52 12 L18 46" stroke="${INK}" stroke-width="1.4" stroke-linecap="round"/><path d="M40 46 l10 -6 M24 46 l-10 -6" stroke="#8C5A22" stroke-width="5" stroke-linecap="round"/><circle cx="50" cy="50" r="4" fill="#D4A017" ${s}/><circle cx="14" cy="50" r="4" fill="#D4A017" ${s}/>`,
    ballot: `<rect x="10" y="28" width="44" height="28" rx="3" fill="#E6DCC4" ${s}/><rect x="22" y="27" width="20" height="4" rx="2" fill="${INK}"/><circle cx="32" cy="15" r="9" fill="#E4B33A" ${s}/><circle cx="32" cy="15" r="5" fill="none" stroke="#9C7B20" stroke-width="2"/>`,
    quill: `<path d="M52 8 C34 12 22 26 16 46 L20 48 C26 30 36 20 52 8 Z" fill="#F6E7C1" ${s}/><path d="M52 8 C46 22 36 34 20 48" fill="none" ${s}/><path d="M16 46 L12 56" ${s}/><path d="M8 58 h20" stroke="#2C5AA0" stroke-width="3" stroke-linecap="round"/>`,
    people: `<circle cx="20" cy="22" r="7" fill="#E9DCC0" ${s}/><circle cx="44" cy="22" r="7" fill="#E9DCC0" ${s}/><circle cx="32" cy="18" r="8" fill="#F0CFAE" ${s}/><path d="M8 52 C8 40 14 34 20 34 C26 34 32 40 32 52 Z" fill="#9C7B57" ${s}/><path d="M32 52 C32 40 38 34 44 34 C50 34 56 40 56 52 Z" fill="#9C7B57" ${s}/><path d="M18 54 C18 38 24 30 32 30 C40 30 46 38 46 54 Z" fill="#C0392B" ${s}/>`,
    five: `<g ${s} fill="#AEB8C5"><circle cx="12" cy="24" r="6"/><circle cx="22" cy="18" r="6"/><circle cx="32" cy="15" r="6"/><circle cx="42" cy="18" r="6"/><circle cx="52" cy="24" r="6"/></g><path d="M6 50 C6 38 58 38 58 50 Z" fill="#5D6D7E" ${s}/>`,
    veto: `<rect x="10" y="12" width="44" height="40" rx="4" fill="#fff" ${s}/><path d="M18 22 h28 M18 30 h28 M18 38 h18" stroke="#AEB8C5" stroke-width="2.4"/><g transform="rotate(-14 32 40)"><rect x="14" y="30" width="38" height="16" rx="3" fill="none" stroke="#C0392B" stroke-width="3"/><text x="33" y="43" text-anchor="middle" font-family="Inter" font-weight="800" font-size="12" fill="#C0392B">VETO</text></g>`,
    gavel: `<rect x="22" y="12" width="26" height="12" rx="3" transform="rotate(35 35 18)" fill="#8C5A22" ${s}/><path d="M28 30 L12 52" stroke="#6E4419" stroke-width="6" stroke-linecap="round"/><rect x="30" y="50" width="26" height="6" rx="2" fill="#6E4419" ${s}/>`,
    eye: `<path d="M6 32 C14 20 22 16 32 16 C42 16 50 20 58 32 C50 44 42 48 32 48 C22 48 14 44 6 32 Z" fill="#fff" ${s}/><circle cx="32" cy="32" r="9" fill="#7B1D14" ${s}/><circle cx="32" cy="32" r="3.5" fill="${INK}"/>`,
  };
  return `<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">${I[name] ?? ""}</svg>`;
}

// ── flame (the travelling light) ─────────────────────────────────────────
export function flameSVG(id) {
  return `<svg viewBox="0 0 100 140" xmlns="http://www.w3.org/2000/svg">
  <path id="${id}-o" d="M50 2 C58 30 92 46 92 90 C92 120 74 138 50 138 C26 138 8 120 8 90 C8 64 26 52 30 28 C38 46 44 52 48 54 C46 38 44 20 50 2 Z" fill="#E2501C"/>
  <path id="${id}-m" d="M50 44 C54 64 76 72 76 100 C76 120 64 132 50 132 C36 132 24 120 24 100 C24 84 36 76 38 62 C42 72 46 76 50 78 Z" fill="#F5A623"/>
  <path id="${id}-c" d="M50 84 C52 96 64 102 64 114 C64 124 58 130 50 130 C42 130 36 124 36 114 C36 106 44 100 50 84 Z" fill="#FFE08A"/>
</svg>`;
}

export function flame(id, x, y, scale = 1) {
  // outer box is positioned (moved with GSAP x); inner .fi carries the scale (set by GSAP, no CSS transform)
  return `<div class="flame" id="${id}" style="left:${x}px;top:${y}px"><div class="fi" id="${id}-i" data-s="${scale}"><div class="glow" id="${id}-glow"></div>${flameSVG(id)}</div></div>`;
}

// ── frise: 1789 → 1799, five act segments in the PDF's proportions ───────
const SEGS = [
  { a: 1, from: 1789, to: 1790 },
  { a: 2, from: 1790, to: 1792 },
  { a: 3, from: 1792, to: 1793 },
  { a: 4, from: 1793, to: 1795 },
  { a: 5, from: 1795, to: 1799 },
];
export function yearX(x0, w, year) {
  return x0 + ((year - 1789) / 10) * w;
}
export function frise(id, { x = 120, y = 30, w = 1680, active = null, years = [1789, 1790, 1792, 1793, 1795, 1799], height } = {}) {
  const segs = SEGS.map(
    (s) =>
      `<div class="seg${active && s.a !== active ? " off" : ""}" id="${id}-s${s.a}" style="width:${((s.to - s.from) / 10) * 100}%;background:var(--a${s.a})"></div>`,
  ).join("");
  const labels = years
    .map((yr) => `<div class="yr" style="left:${((yr - 1789) / 10) * w}px">${yr}</div><div class="tick" style="left:${((yr - 1789) / 10) * w}px"></div>`)
    .join("");
  return `<div class="frise" id="${id}" style="left:${x}px;top:${y}px;width:${w}px${height ? `;height:${height}px` : ""}"><div class="bar">${segs}</div>${labels}</div>`;
}

export function banner(id, a, { x = 120, y = 118, w = 1680, h = 132, title } = {}) {
  const A = ACT[a];
  return `<div class="banner" id="${id}" style="left:${x}px;top:${y}px;width:${w}px;height:${h}px;background:${A.c}">
  <div class="num"><div class="k">ACTE</div><div class="n">${A.n}</div></div><div class="sep"></div>
  <div class="txt"><div class="fire">« ${A.fire} »</div><div class="ttl">${title ?? A.title}</div><div class="yrs">${A.years}</div></div></div>`;
}

export function slim(id, a, label, { x = 120, y = 112 } = {}) {
  const A = ACT[a];
  return `<div class="slim" id="${id}" style="left:${x}px;top:${y}px;background:${A.c}"><span class="k">ACTE ${A.n}</span><span>${A.years}</span><span class="f">« ${A.fire} »</span>${label ? `<span>· ${label}</span>` : ""}</div>`;
}

export function card(id, a, { x, y, w, h, ico, date, title, line, star = false, style = "" }) {
  const A = ACT[a];
  const bg = star ? `background:linear-gradient(180deg, ${A.tint} 0%, #FFFFFF 55%);border-color:${A.c}` : "";
  return `<div class="card${star ? " star" : ""}" id="${id}" style="left:${x}px;top:${y}px;width:${w}px;${h ? `height:${h}px;` : ""}${bg};${style}">
  <div class="medal" style="border-color:${A.c}">${icon(ico, A.c)}</div>
  <div class="pill" style="background:${A.c}">${date}</div>
  <div class="ct" style="color:${A.c}">${title}${star ? ` <span class="st">★</span>` : ""}</div>
  ${line ? `<div class="cl">${line}</div>` : ""}</div>`;
}

export function arrow(id, html, { x, y, w, h = 88, style = "" }) {
  return `<div class="arrow" id="${id}" style="left:${x}px;top:${y}px;width:${w}px;height:${h}px;${style}"><span class="ar">→</span><span>${html}</span></div>`;
}

// Wrap one frame into the sub-composition file the assembler mounts.
// The script gets a small, seek-safe helper set (fromTo entrances only, no exits).
export function wrap({ id, duration, css = "", html, js = "" }) {
  return `<template>
  <style>${FONTS}${BASE}${css}</style>
  <div id="root" data-composition-id="${id}" data-start="0" data-duration="${duration}" data-width="${W}" data-height="${H}">
    <div class="clip ground" id="bg-${id}" data-start="0" data-duration="${duration}" data-track-index="0"></div>
${html}
  </div>
  <script src="vendor/gsap.min.js"></script>
  <script>
    (function () {
      window.__timelines = window.__timelines || {};
      const D = ${duration};
      const tl = gsap.timeline({ paused: true });
      const root = document.querySelector('[data-composition-id="${id}"]');
      const q = (s) => (typeof s === "string" ? root.querySelector(s) : s);
      const qa = (s) => Array.from(root.querySelectorAll(s));
      const P3 = "power3.out";
      const has = (el) => el && (!Array.isArray(el) || el.length);
      const rise = (s, t, o = {}) => { const el = q(s); if (has(el)) tl.fromTo(el, { opacity: 0, y: o.y ?? 36 }, { opacity: 1, y: 0, duration: o.d ?? 0.7, ease: P3 }, t); };
      const fade = (s, t, d = 0.6) => { const el = q(s); if (has(el)) tl.fromTo(el, { opacity: 0 }, { opacity: 1, duration: d, ease: "power2.out" }, t); };
      const slideX = (s, t, x = -50, d = 0.7) => { const el = q(s); if (has(el)) tl.fromTo(el, { opacity: 0, x }, { opacity: 1, x: 0, duration: d, ease: P3 }, t); };
      const pop = (s, t, d = 0.5, from = 0.5) => { const el = q(s); if (has(el)) tl.fromTo(el, { opacity: 0, scale: from }, { opacity: 1, scale: 1, duration: d, ease: P3 }, t); };
      const wipe = (s, t, d = 0.9, r = 14) => { const el = q(s); if (has(el)) tl.fromTo(el, { clipPath: "inset(0% 100% 0% 0% round " + r + "px)" }, { clipPath: "inset(0% 0% 0% 0% round " + r + "px)", duration: d, ease: "power3.inOut" }, t); };
      // card: lift, medallion, date pill, then title/line; "late" delays named children to their own cue
      const cardIn = (s, t, late = {}) => {
        const c = q(s); if (!c) return;
        rise(c, t, { y: 46, d: 0.75 });
        pop(c.querySelector(".medal"), t + 0.12, 0.55, 0.55);
        const pill = c.querySelector(".pill"); if (pill) tl.fromTo(pill, { opacity: 0, x: -18 }, { opacity: 1, x: 0, duration: 0.5, ease: P3 }, t + 0.22);
        let i = 0;
        c.querySelectorAll(".ct, .cl, .q, ul, .nm, .ex, .sb").forEach((el) => {
          const k = Object.keys(late).find((sel) => el.matches(sel));
          const at = k ? late[k] : t + 0.3 + i++ * 0.14;
          tl.fromTo(el, { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.55, ease: P3 }, at);
        });
      };
      const star = (s, t) => { const st = q(s).querySelector(".st"); if (st) tl.fromTo(st, { opacity: 0, scale: 0.2, rotation: -40 }, { opacity: 1, scale: 1, rotation: 0, duration: 0.5, ease: P3 }, t); };
      const flameTo = (s, dx, t, d = 1.1) => { const el = q(s); if (el && dx) tl.fromTo(el, { x: dx }, { x: 0, duration: d, ease: "power2.inOut" }, t); };
      const flameScale = (s, a, b, t, d = 1) => { const el = q(s); if (el) tl.fromTo(el, { scale: a }, { scale: b, duration: d, ease: "power2.inOut", transformOrigin: "50% 100%", immediateRender: false }, t); };
      const blade = (s, t) => { const el = q(s); if (el) tl.fromTo(el, { y: 0 }, { y: 24, duration: 0.2, ease: "power4.in" }, t); };
      const polyLen = (d) => { const n = (d.match(/-?[\\d.]+/g) || []).map(Number); let L = 0; for (let i = 2; i + 1 < n.length; i += 2) L += Math.hypot(n[i] - n[i - 2], n[i + 1] - n[i - 1]); return L; };
      const draw = (s, t, d = 0.8, ease = "power2.inOut") => { const el = q(s); if (!el) return; const L = polyLen(el.getAttribute("d")); el.style.strokeDasharray = L + " " + L; tl.fromTo(el, { strokeDashoffset: L }, { strokeDashoffset: 0, duration: d, ease }, t); };
      const words = (s, t, step = 0.12, o = {}) => qa(s).forEach((w, i) => rise(w, t + i * step, { y: o.y ?? 28, d: o.d ?? 0.55 }));
      const light = (s, t, d = 0.6) => { const el = q(s); if (has(el)) tl.fromTo(el, { opacity: 0.22 }, { opacity: 1, duration: d, ease: "power2.out" }, t); };
      const glowWord = (s, t, from, to) => { const el = q(s); if (has(el)) tl.fromTo(el, { color: from }, { color: to, duration: 0.6, ease: "power2.out" }, t); };
      // flames: scale from data-s, then a deterministic flicker read from the timeline clock
      qa(".flame").forEach((f, k) => {
        const fi = f.querySelector(".fi");
        gsap.set(fi, { scale: +fi.dataset.s, transformOrigin: "50% 100%" });
        const o = f.querySelector('[id$="-o"]'), m = f.querySelector('[id$="-m"]'), c = f.querySelector('[id$="-c"]'), g = f.querySelector(".glow");
        const flick = { v: 0 };
        tl.to(flick, { v: 1, duration: D, ease: "none", onUpdate() {
          const t = tl.time() + k * 1.7;
          const a = 0.55 * Math.sin(t * 11.3) + 0.3 * Math.sin(t * 17.9 + 1.3) + 0.15 * Math.sin(t * 5.1 + 0.4);
          gsap.set(o, { scaleY: 1 + 0.06 * a, skewX: 3 * a, transformOrigin: "50% 100%" });
          gsap.set(m, { scaleY: 1 + 0.09 * Math.sin(t * 13.7 + 1), skewX: -2 * a, transformOrigin: "50% 100%" });
          gsap.set(c, { scaleY: 1 + 0.12 * Math.sin(t * 19.1 + 2), transformOrigin: "50% 100%" });
          gsap.set(g, { opacity: 0.82 + 0.18 * a });
        } }, 0);
      });
${js}
      window.__timelines["${id}"] = tl;
    })();
  </script>
</template>
`;
}
