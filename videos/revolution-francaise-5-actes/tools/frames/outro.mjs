// Frames 13-14: the answer to the problématique (+ the whole frise as recap), Victor Hugo.
// Layouts are the confirmed sketches; js adds the VO-paced motion (cue times from cues.json).
import { ACT, frise, yearX } from "../kit.mjs";

// Key dates of the PDF's overview frise (page 2): above / below the bar.
const ABOVE = [
  [1789.54, "1789", "Bastille"],
  [1791.47, "1791", "Varennes"],
  [1792.72, "22/09/92", "République"],
  [1793.9, "1793-94", "Terreur"],
  [1795.5, "1795", "Directoire"],
];
const BELOW = [
  [1789.65, "26/08/89", "DDHC", 0],
  [1792.61, "10/08/92", "Chute du roi", 0],
  [1793.06, "21/01/93", "Mort du roi", 1],
  [1794.57, "28/07/94", "Robespierre", 0],
  [1798.86, "1799", "Bonaparte", 0],
];
const SEGS = [[1, 1789, 1790], [2, 1790, 1792], [3, 1792, 1793], [4, 1793, 1795], [5, 1795, 1799]];
const r2 = (v) => Math.round(v * 100) / 100;

export default [
  {
    id: "13-reponse",
    build({ at }) {
      const fx = 160, fw = 1600, fy = 672;
      const lab = (pos, i, [yr, d, name, lvl = 0]) => {
        const x = yearX(fx, fw, yr);
        const top = pos === "a" ? fy - 92 : fy + 74 + lvl * 74;
        return `<div class="kd ${pos}" id="f13-${pos}${i}" style="left:${x}px;top:${top}px"><div class="d">${d}</div><div class="n">${name}</div></div>
      <div class="kt" id="f13-${pos}t${i}" style="left:${x}px;top:${pos === "a" ? fy + 12 : fy + 52}px;height:${pos === "a" ? 22 : 18 + lvl * 74}px"></div>`;
      };
      // the recap bar draws 1789 → 1799 while the VO says « en dix ans … libres et égaux »
      const b0 = at("oui"), b1 = at("égaux") + 0.3, bD = b1 - b0;
      const tYear = (yr) => r2(b0 + ((yr - 1789) / 10) * bD);
      const l1 = "Une <span class=\"gold\">rupture majeure</span>";
      return {
        css: `
#f13-box{left:160px;top:84px;width:1600px;height:452px}
#f13-box .lab{position:absolute;left:0;right:0;top:38px;color:#E3BF63}
#f13-l1{position:absolute;left:0;right:0;top:86px;text-align:center;font:900 64px/1.1 "Merriweather"}
#f13-l2{position:absolute;left:120px;right:120px;top:182px;text-align:center;font:500 33px/1.42 "Inter"}
#f13-l2 b{font-weight:800}
#f13-l3{position:absolute;left:0;right:0;top:296px;text-align:center;font:italic 400 42px/1 "Merriweather";color:#E3BF63}
#f13-tags{position:absolute;left:0;right:0;top:368px;display:flex;justify-content:center;gap:18px}
#f13-tags span{padding:12px 24px;border-radius:30px;background:rgba(255,255,255,0.12);border:2px solid rgba(255,255,255,0.32);font:600 26px/1 "Inter"}
.kd{position:absolute;text-align:center;white-space:nowrap;width:220px;margin-left:-110px}
.kd .d{font:800 24px/1 "Inter"}
.kd .n{font:500 21px/1.2 "Inter";color:var(--ink-soft);margin-top:4px}
.kd.b .d{color:var(--ink)}
.kt{position:absolute;width:3px;margin-left:-1.5px;background:var(--ink);opacity:0.6;border-radius:2px}
#f13-frise .bar{height:20px;top:30px;border-radius:10px;background:#E9E1D0}
#f13-frise .yr,#f13-frise .tick{display:none}`,
        html: `
    <div class="band l"></div><div class="band r"></div>
    <div class="navy" id="f13-box"><div class="lab">Réponse à la problématique</div>
      <div id="f13-l1">${l1}</div>
      <div id="f13-l2">De la <b>monarchie absolue</b> de droit divin à une <b>nation de citoyens libres et égaux</b>, où la <b>souveraineté appartient à la nation</b>.</div>
      <div id="f13-l3">… mais violente et inachevée</div>
      <div id="f13-tags"><span id="f13-g1">Guerres</span><span id="f13-g2">Terreur</span><span id="f13-g3">Femmes et pauvres exclus de la citoyenneté</span><span id="f13-g4">Bonaparte au pouvoir</span></div></div>
    ${frise("f13-frise", { x: fx, y: fy - 30, w: fw, years: [] })}
    ${ABOVE.map((d, i) => lab("a", i, d)).join("")}
    ${BELOW.map((d, i) => lab("b", i, d)).join("")}`,
        js: `
      rise("#f13-box", 0.0, { y: 30, d: 0.8 });
      fade("#f13-box .lab", 0.2, 0.5);
      rise("#f13-l1", ${r2(at("rupture") - 0.2)}, { y: 22, d: 0.7 });
      ${SEGS.map(([a, f, t]) => `tl.fromTo(q("#f13-frise-s${a}"), { scaleX: 0, transformOrigin: "0% 50%" }, { scaleX: 1, duration: ${r2(((t - f) / 10) * bD)}, ease: "none" }, ${tYear(f)});`).join("\n      ")}
      ${ABOVE.map(([yr], i) => `rise("#f13-a${i}", ${tYear(yr)}, { y: 14, d: 0.45 }); fade("#f13-at${i}", ${tYear(yr)}, 0.3);`).join("\n      ")}
      ${BELOW.map(([yr], i) => `rise("#f13-b${i}", ${tYear(yr)}, { y: -14, d: 0.45 }); fade("#f13-bt${i}", ${tYear(yr)}, 0.3);`).join("\n      ")}
      rise("#f13-l2", ${r2(at("roi") - 0.3)}, { y: 16, d: 0.7 });
      rise("#f13-l3", ${r2(at("violente") - 0.35)}, { y: 16, d: 0.7 });
      pop("#f13-g1", ${r2(at("guerres") - 0.1)}, 0.4, 0.6);
      pop("#f13-g2", ${r2(at("terreur") - 0.1)}, 0.4, 0.6);
      pop("#f13-g3", ${r2(at("femmes") - 0.1)}, 0.4, 0.6);
      pop("#f13-g4", ${r2(at("bonaparte") - 0.1)}, 0.4, 0.6);`,
      };
    },
  },
  {
    id: "14-hugo",
    build({ duration }) {
      const chips = [1, 2, 3, 4, 5]
        .map((a, i) => `<div class="hc" id="f14-chip${a}" style="left:${428 + i * 220}px;background:${ACT[a].c}">Acte ${a}</div>`)
        .join("");
      return {
        css: `
.hc{position:absolute;top:150px;width:200px;height:52px;border-radius:10px;color:#fff;font:700 24px/52px "Inter";text-align:center}
.rule{position:absolute;left:380px;width:1160px;height:3px;background:var(--gold)}
#f14-q{left:300px;width:1320px;top:300px;text-align:center;font:italic 400 50px/1.5 "Merriweather"}
#f14-by{left:0;right:0;top:548px;text-align:center;font:800 32px/1 "Inter"}
#f14-name{left:0;right:0;top:670px;text-align:center;font:400 72px/1 "Merriweather";color:var(--navy)}
#f14-sub{left:0;right:0;top:772px;text-align:center;font:500 28px/1 "Inter";color:var(--brown)}
#f14-veil{position:absolute;inset:0;background:#FFFDF7}`,
        html: `
    <div class="band l"></div><div class="band r"></div>
    ${chips}
    <div class="rule" id="f14-r1" style="top:262px"></div>
    <div class="abs" id="f14-q">« La Révolution française est le plus puissant pas du genre humain depuis l'avènement du Christ. »</div>
    <div class="abs" id="f14-by">— Victor Hugo</div>
    <div class="rule" id="f14-r2" style="top:612px"></div>
    <div class="abs" id="f14-name">Yazid Tragha</div>
    <div class="abs" id="f14-sub">Frise chronologique de révision — Évaluation</div>
    <div id="f14-veil"></div>`,
        js: `
      ${[1, 2, 3, 4, 5].map((a, i) => `rise("#f14-chip${a}", ${r2(0.1 + i * 0.08)}, { y: 20, d: 0.5 });`).join(" ")}
      tl.fromTo(q("#f14-r1"), { scaleX: 0, transformOrigin: "50% 50%" }, { scaleX: 1, duration: 0.8, ease: "power3.inOut" }, 0.35);
      rise("#f14-q", 0.7, { y: 20, d: 1.1 });
      fade("#f14-by", 2.1, 0.6);
      tl.fromTo(q("#f14-r2"), { scaleX: 0, transformOrigin: "50% 50%" }, { scaleX: 1, duration: 0.8, ease: "power3.inOut" }, 2.4);
      rise("#f14-name", 2.8, { y: 22, d: 0.8 });
      fade("#f14-sub", 3.2, 0.7);
      // the film's only exit: the frame fades to paper
      tl.fromTo(q("#f14-veil"), { opacity: 0 }, { opacity: 1, duration: 0.8, ease: "power2.in" }, ${r2(duration - 0.8)});`,
      };
    },
  },
];
