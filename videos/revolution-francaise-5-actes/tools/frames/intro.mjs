// Frames 1-3: the spark (cover), the Ancien Régime, the problématique.
import { ACT, arrow, flame, frise, icon, yearX } from "../kit.mjs";

const chips = (id, x, y, w = 236, gap = 30) =>
  [1, 2, 3, 4, 5]
    .map(
      (a, i) => `<div class="chip" id="${id}-${a}" style="left:${x + i * (w + gap)}px;top:${y}px;width:${w}px;background:${ACT[a].c}">
  <div class="k">Acte ${a}</div><div class="y">${ACT[a].years.replace(/ — /, "-").replace(/^17(\d\d)-17(\d\d)$/, "17$1-$2")}</div><div class="f">${ACT[a].fire}</div></div>`,
    )
    .join("");
const CHIP_CSS = `
.chip{position:absolute;height:100px;border-radius:10px;color:#fff;text-align:center;display:flex;flex-direction:column;justify-content:center;gap:5px}
.chip .k{font:500 20px/1 "Inter";opacity:0.92}.chip .y{font:800 26px/1 "Inter"}.chip .f{font:500 20px/1.1 "Inter"}`;

export default [
  {
    id: "01-etincelle",
    build() {
      const fx = 310, fw = 1300, fy = 660;
      return {
        css: `${CHIP_CSS}
#f01-kick{left:0;right:0;top:150px;text-align:center;font-size:26px;color:var(--brown);letter-spacing:0.34em}
#f01-title{left:0;right:0;top:196px;text-align:center;font:900 132px/1.06 "Merriweather";color:var(--a4)}
#f01-title .lib{color:var(--blue)}
#f01-sub{left:0;right:0;top:508px;text-align:center;font:400 44px/1 "Merriweather"}
#f01-yrs{left:0;right:0;top:572px;text-align:center;font:900 48px/1 "Merriweather"}`,
        html: `
    <div class="band l"></div><div class="band r"></div>
    <div class="abs mono" id="f01-kick">Histoire · Chapitre 1 · Première</div>
    <div class="abs" id="f01-title">Les flammes<br/>de la <span class="lib">liberté</span></div>
    <div class="abs" id="f01-sub">La Révolution française en 5 actes</div>
    <div class="abs" id="f01-yrs">1789 — 1799</div>
    ${frise("f01-frise", { x: fx, y: fy, w: fw })}
    ${flame("f01-flame", yearX(fx, fw, 1799), fy + 41 - 98, 0.9)}
    ${chips("f01-chip", fx, 760)}`,
      };
    },
  },
  {
    id: "02-ancien-regime",
    build() {
      // pyramid of the three orders (SVG coords 940×620, drawn at 0.936 scale)
      const tri = (y) => ((y - 70) / 540) * 450;
      const tz = (y0, y1) => `${470 - tri(y0)},${y0} ${470 + tri(y0)},${y0} ${470 + tri(y1)},${y1} ${470 - tri(y1)},${y1}`;
      return {
        css: `
#f02-kick{left:120px;top:92px;font-size:24px;color:var(--brown)}
#f02-title{left:120px;top:124px;font:900 80px/1.1 "Merriweather";color:var(--a4)}
#f02-pyr{left:150px;top:300px;width:880px;height:580px}
#f02-crown{left:540px;top:236px;width:100px;height:100px;border-radius:50%;background:#fff;border:5px solid var(--gold);display:flex;align-items:center;justify-content:center}
#f02-crown svg{width:64px;height:64px}
#f02-king{left:662px;top:250px;font:500 29px/1.3 "Inter";width:440px}
#f02-lum{left:1150px;top:330px;width:650px;height:300px;background:#fff;border:3px solid var(--navy);border-radius:14px;padding:84px 34px 30px;box-shadow:0 8px 24px rgba(43,33,24,0.08)}
#f02-lum .medal{position:absolute;top:-52px;left:30px;width:112px;height:112px;border-radius:50%;background:#fff;border:5px solid var(--navy);display:flex;align-items:center;justify-content:center}
#f02-lum .medal svg{width:70px;height:70px}
#f02-lum .pill{position:absolute;top:28px;left:160px;background:var(--navy)}
#f02-lum .ct{font:700 44px/1.15 "Merriweather";color:var(--navy)}
#f02-lum .cl{font:500 30px/1.4 "Inter";margin-top:14px}`,
        html: `
    <div class="abs mono" id="f02-kick">Avant 1789</div>
    <div class="abs" id="f02-title">L'Ancien Régime</div>
    <svg class="abs" id="f02-pyr" viewBox="0 0 940 620" xmlns="http://www.w3.org/2000/svg">
      <polygon id="f02-t1" points="${tz(70, 70)} ${470 + tri(230)},230 ${470 - tri(230)},230" fill="#7A5A3A"/>
      <polygon id="f02-t2" points="${tz(238, 362)}" fill="#D4A017"/>
      <polygon id="f02-t3" points="${tz(370, 610)}" fill="#EFE3C8" stroke="#C9B48A" stroke-width="3"/>
      <text x="470" y="196" text-anchor="middle" font-family="Merriweather" font-weight="700" font-size="32" fill="#fff">Clergé</text>
      <text x="470" y="314" text-anchor="middle" font-family="Merriweather" font-weight="700" font-size="36" fill="#2B2118">Noblesse</text>
      <text x="470" y="472" text-anchor="middle" font-family="Merriweather" font-weight="900" font-size="52" fill="#2B2118">Tiers état</text>
      <text x="470" y="522" text-anchor="middle" font-family="Inter" font-weight="700" font-size="30" fill="#2B2118">98 % de la population</text>
      <text x="470" y="562" text-anchor="middle" font-family="Inter" font-weight="500" font-size="26" fill="#6B5A3A">aucun privilège</text>
      <g id="f02-priv" font-family="Inter" font-weight="700" font-size="26" fill="#9C7B20">
        <path d="M600 190 L690 170 M700 300 L770 286" stroke="#D4A017" stroke-width="3"/>
        <rect x="690" y="146" width="180" height="46" rx="23" fill="#FFF8E6" stroke="#D4A017" stroke-width="3"/>
        <text x="780" y="178" text-anchor="middle">privilèges</text>
        <rect x="770" y="262" width="168" height="46" rx="23" fill="#FFF8E6" stroke="#D4A017" stroke-width="3"/>
        <text x="854" y="294" text-anchor="middle">privilèges</text>
      </g>
      <path id="f02-crack" d="M476 84 L506 132 L532 176 L548 226 L586 270 L600 318 L642 372 L656 420 L702 468 L690 528 L742 606" fill="none" stroke="#2B2118" stroke-width="5" stroke-linejoin="round"/>
    </svg>
    <div class="abs" id="f02-crown">${icon("crown")}</div>
    <div class="abs" id="f02-king"><b>Le roi</b> : monarchie absolue,<br/>de droit divin</div>
    <div class="abs" id="f02-lum">
      <div class="medal">${icon("quill")}</div>
      <div class="pill">XVIII<sup>e</sup> siècle</div>
      <div class="ct">Les Lumières</div>
      <div class="cl">Voltaire, Montesquieu, Rousseau… <b>critiquent l'Ancien Régime</b>.</div>
    </div>
    ${arrow("f02-arrow", "Une <b>société d'ordres</b> : injuste et inégalitaire.", { x: 1150, y: 700, w: 650, h: 120, style: "font-size:31px" })}`,
      };
    },
  },
  {
    id: "03-problematique",
    build() {
      const fx = 360, fw = 1200, fy = 744;
      return {
        css: `
#f03-box{left:240px;top:200px;width:1440px;height:460px}
#f03-box .lab{position:absolute;left:0;right:0;top:56px}
#f03-q{position:absolute;left:100px;right:100px;top:118px;text-align:center;font:700 54px/1.42 "Merriweather"}
#f03-frise .seg{opacity:0.3}`,
        html: `
    <div class="band l"></div><div class="band r"></div>
    <div class="navy" id="f03-box"><div class="lab">Problématique</div>
      <div id="f03-q">Dans quelle mesure la Révolution française constitue-t-elle une <span class="gold">rupture majeure</span> dans l'histoire en faisant émerger une <span class="gold">nouvelle conception de la nation</span> ?</div></div>
    ${frise("f03-frise", { x: fx, y: fy, w: fw, years: [1790, 1792, 1793, 1795, 1799] })}
    <div class="abs" id="f03-y0" style="left:${fx - 92}px;top:${fy + 30}px;font:700 22px/1 Inter;color:var(--ink-soft)">1789</div>
    ${flame("f03-flame", yearX(fx, fw, 1789), fy + 41 - 98, 0.55)}`,
      };
    },
  },
];
