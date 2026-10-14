// Frames 1-3: the spark (cover), the Ancien Régime, the problématique.
// Layouts are the confirmed sketches; js adds the VO-paced motion (cue times from cues.json).
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
const SEGS = [[1, 1789, 1790], [2, 1790, 1792], [3, 1792, 1793], [4, 1793, 1795], [5, 1795, 1799]];
const r2 = (v) => Math.round(v * 100) / 100;

export default [
  {
    id: "01-etincelle",
    build({ at }) {
      const fx = 310, fw = 1300, fy = 660;
      // the flame runs 1789 → 1799 at constant speed while the VO says « en dix ans … citoyens »
      const run0 = at("et") - 0.05, run1 = at("citoyens") + 0.5, runD = run1 - run0;
      const tYear = (yr) => r2(run0 + ((yr - 1789) / 10) * runD);
      const years = [1789, 1790, 1792, 1793, 1795, 1799];
      return {
        css: `${CHIP_CSS}
#f01-kick{left:0;right:0;top:150px;text-align:center;font-size:26px;color:var(--brown);letter-spacing:0.34em}
#f01-title{left:0;right:0;top:196px;text-align:center;font:900 132px/1.06 "Merriweather";color:var(--a4)}
#f01-title .w{display:inline-block}
#f01-title .lib{color:var(--blue)}
#f01-sub{left:0;right:0;top:508px;text-align:center;font:400 44px/1 "Merriweather"}
#f01-yrs{left:0;right:0;top:572px;text-align:center;font:900 48px/1 "Merriweather"}
#f01-frise .bar{background:#E9E1D0}`,
        html: `
    <div class="band l"></div><div class="band r"></div>
    <div class="abs mono" id="f01-kick">Histoire · Chapitre 1 · Première</div>
    <div class="abs" id="f01-title"><span class="w">Les</span> <span class="w">flammes</span><br/><span class="w">de</span> <span class="w">la</span> <span class="w lib">liberté</span></div>
    <div class="abs" id="f01-sub">La Révolution française en 5 actes</div>
    <div class="abs" id="f01-yrs">1789 — 1799</div>
    ${frise("f01-frise", { x: fx, y: fy, w: fw, years })}
    ${flame("f01-flame", yearX(fx, fw, 1799), fy + 41 - 98, 0.9)}
    ${chips("f01-chip", fx, 760)}`,
        js: `
      // the spark: the flame ignites on 1789 (it sits at 1799 in the layout; x carries it back)
      tl.fromTo(q("#f01-flame"), { x: ${-fw} }, { x: 0, duration: ${r2(runD)}, ease: "none" }, ${r2(run0)});
      tl.fromTo(q("#f01-flame-i"), { scale: 0.05, opacity: 0 }, { scale: 0.55, opacity: 1, duration: 0.6, ease: "power3.out" }, 0.05);
      tl.fromTo(q("#f01-flame-i"), { scale: 0.55 }, { scale: 0.9, duration: 1.2, ease: "power2.inOut", immediateRender: false }, ${r2(run0)});
      // each act segment fills as the flame passes it
      ${SEGS.map(([a, f, t]) => `tl.fromTo(q("#f01-frise-s${a}"), { scaleX: 0, transformOrigin: "0% 50%" }, { scaleX: 1, duration: ${r2(((t - f) / 10) * runD)}, ease: "none" }, ${tYear(f)});`).join("\n      ")}
      qa("#f01-frise .yr").forEach((el, i) => fade(el, i === 0 ? ${r2(at("mille") - 0.1)} : [${years.map(tYear).join(",")}][i] - 0.1, 0.4));
      qa("#f01-frise .tick").forEach((el, i) => fade(el, i === 0 ? ${r2(at("mille") - 0.1)} : [${years.map(tYear).join(",")}][i] - 0.1, 0.3));
      // the title rises with the thesis
      fade("#f01-kick", ${r2(at("et") + 0.1)}, 0.8);
      words("#f01-title .w", ${r2(at("france") - 0.25)}, 0.32, { y: 40, d: 0.8 });
      rise("#f01-yrs", ${r2(at("dix") + 0.1)}, { y: 20 });
      rise("#f01-sub", ${r2(at("révolution") - 0.1)}, { y: 20 });
      ${[1, 2, 3, 4, 5].map((a, i) => `rise("#f01-chip-${a}", ${r2(at("cinq") - 0.25 + i * 0.1)}, { y: 30, d: 0.6 });`).join("\n      ")}`,
      };
    },
  },
  {
    id: "02-ancien-regime",
    build({ at }) {
      // pyramid of the three orders (SVG coords 940×620, drawn at 0.936 scale)
      const tri = (y) => ((y - 70) / 540) * 450;
      const tz = (y0, y1) => `${470 - tri(y0)},${y0} ${470 + tri(y0)},${y0} ${470 + tri(y1)},${y1} ${470 - tri(y1)},${y1}`;
      const soc = at("société");
      return {
        css: `
#f02-kick{left:120px;top:92px;font-size:24px;color:var(--brown)}
#f02-title{left:120px;top:124px;font:900 80px/1.1 "Merriweather";color:var(--a4)}
#f02-title .w{display:inline-block}
#f02-pyr{left:150px;top:300px;width:880px;height:580px;overflow:visible}
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
    <div class="abs" id="f02-title"><span class="w">L'Ancien</span> <span class="w">Régime</span></div>
    <svg class="abs" id="f02-pyr" viewBox="0 0 940 620" xmlns="http://www.w3.org/2000/svg">
      <g id="f02-g3">
        <polygon points="${tz(370, 610)}" fill="#EFE3C8" stroke="#C9B48A" stroke-width="3"/>
        <text x="470" y="472" text-anchor="middle" font-family="Merriweather" font-weight="900" font-size="52" fill="#2B2118">Tiers état</text>
        <text x="470" y="522" text-anchor="middle" font-family="Inter" font-weight="700" font-size="30" fill="#2B2118">98 % de la population</text>
        <text x="470" y="562" text-anchor="middle" font-family="Inter" font-weight="500" font-size="26" fill="#6B5A3A">aucun privilège</text>
      </g>
      <g id="f02-g2">
        <polygon points="${tz(238, 362)}" fill="#D4A017"/>
        <text x="470" y="314" text-anchor="middle" font-family="Merriweather" font-weight="700" font-size="36" fill="#2B2118">Noblesse</text>
      </g>
      <g id="f02-g1">
        <polygon points="470,70 ${470 + tri(230)},230 ${470 - tri(230)},230" fill="#7A5A3A"/>
        <text x="470" y="196" text-anchor="middle" font-family="Merriweather" font-weight="700" font-size="32" fill="#fff">Clergé</text>
      </g>
      <g font-family="Inter" font-weight="700" font-size="26" fill="#9C7B20">
        <g id="f02-p1"><path d="M600 190 L690 170" stroke="#D4A017" stroke-width="3"/>
          <rect x="690" y="146" width="180" height="46" rx="23" fill="#FFF8E6" stroke="#D4A017" stroke-width="3"/><text x="780" y="178" text-anchor="middle">privilèges</text></g>
        <g id="f02-p2"><path d="M700 300 L770 286" stroke="#D4A017" stroke-width="3"/>
          <rect x="770" y="262" width="168" height="46" rx="23" fill="#FFF8E6" stroke="#D4A017" stroke-width="3"/><text x="854" y="294" text-anchor="middle">privilèges</text></g>
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
        js: `
      fade("#f02-kick", 0.05, 0.5);
      words("#f02-title .w", 0.15, 0.3, { y: 34, d: 0.8 });
      pop("#f02-crown", ${r2(at("roi") - 0.15)}, 0.55, 0.4);
      slideX("#f02-king", ${r2(at("droit") - 0.2)}, -24);
      // the society builds bottom-up on « une société d'ordres »
      rise("#f02-g3", ${r2(soc - 0.2)}, { y: 40, d: 0.7 });
      rise("#f02-g2", ${r2(soc + 0.25)}, { y: 40, d: 0.7 });
      rise("#f02-g1", ${r2(soc + 0.65)}, { y: 40, d: 0.7 });
      slideX("#f02-p1", ${r2(at("clergé") - 0.1)}, -30, 0.5);
      slideX("#f02-p2", ${r2(at("noblesse") - 0.1)}, -30, 0.5);
      // the Enlightenment cracks it
      cardIn("#f02-lum", ${r2(at("lumières") - 0.25)});
      draw("#f02-crack", ${r2(at("dénoncent") - 0.05)}, 0.8, "power2.in");
      slideX("#f02-arrow", ${r2(at("injustice") - 0.2)}, -40);`,
      };
    },
  },
  {
    id: "03-problematique",
    build({ at }) {
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
      <div id="f03-q">Dans quelle mesure la Révolution française constitue-t-elle une <span class="gold" id="f03-k1">rupture majeure</span> dans l'histoire en faisant émerger une <span class="gold" id="f03-k2">nouvelle conception de la nation</span> ?</div></div>
    <div class="abs" id="f03-low" style="left:0;top:0;width:1920px;height:1080px">
      ${frise("f03-frise", { x: fx, y: fy, w: fw, years: [1790, 1792, 1793, 1795, 1799] })}
      <div class="abs" id="f03-y0" style="left:${fx - 92}px;top:${fy + 30}px;font:700 22px/1 Inter;color:var(--ink-soft)">1789</div>
      ${flame("f03-flame", yearX(fx, fw, 1789), fy + 41 - 98, 0.55)}
    </div>`,
        js: `
      rise("#f03-box", 0.0, { y: 30, d: 0.8 });
      fade("#f03-box .lab", 0.3, 0.5);
      rise("#f03-q", ${r2(at("question") - 0.1)}, { y: 18, d: 0.9 });
      glowWord("#f03-k1", ${r2(at("rupture") - 0.05)}, "#FFFFFF", "#E3BF63");
      glowWord("#f03-k2", ${r2(at("nouvelle") - 0.05)}, "#FFFFFF", "#E3BF63");
      fade("#f03-low", 0.45, 0.8);`,
      };
    },
  },
];
