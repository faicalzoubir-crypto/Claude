// Frames 13-14: the answer to the problématique (+ the whole frise as recap), Victor Hugo.
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

export default [
  {
    id: "13-reponse",
    build() {
      const fx = 160, fw = 1600, fy = 672;
      const lab = (pos, i, [yr, d, name, lvl = 0]) => {
        const x = yearX(fx, fw, yr);
        const top = pos === "a" ? fy - 92 : fy + 74 + lvl * 74;
        return `<div class="kd ${pos}" id="f13-${pos}${i}" style="left:${x}px;top:${top}px"><div class="d">${d}</div><div class="n">${name}</div></div>
      <div class="kt" id="f13-${pos}t${i}" style="left:${x}px;top:${pos === "a" ? fy + 12 : fy + 52}px;height:${pos === "a" ? 22 : 18 + lvl * 74}px"></div>`;
      };
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
.kd{position:absolute;transform:translateX(-50%);text-align:center;white-space:nowrap}
.kd .d{font:800 24px/1 "Inter"}
.kd .n{font:500 21px/1.2 "Inter";color:var(--ink-soft);margin-top:4px}
.kd.b .d{color:var(--ink)}
.kt{position:absolute;width:3px;margin-left:-1.5px;background:var(--ink);opacity:0.6;border-radius:2px}
#f13-frise .bar{height:20px;top:30px;border-radius:10px}
#f13-frise .yr,#f13-frise .tick{display:none}`,
        html: `
    <div class="band l"></div><div class="band r"></div>
    <div class="navy" id="f13-box"><div class="lab">Réponse à la problématique</div>
      <div id="f13-l1">Une <span class="gold">rupture majeure</span></div>
      <div id="f13-l2">De la <b>monarchie absolue</b> de droit divin à une <b>nation de citoyens libres et égaux</b>, où la <b>souveraineté appartient à la nation</b>.</div>
      <div id="f13-l3">… mais violente et inachevée</div>
      <div id="f13-tags"><span>Guerres</span><span>Terreur</span><span>Femmes et pauvres exclus de la citoyenneté</span><span>Bonaparte au pouvoir</span></div></div>
    ${frise("f13-frise", { x: fx, y: fy - 30, w: fw, years: [] })}
    ${ABOVE.map((d, i) => lab("a", i, d)).join("")}
    ${BELOW.map((d, i) => lab("b", i, d)).join("")}`,
      };
    },
  },
  {
    id: "14-hugo",
    build() {
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
#f14-sub{left:0;right:0;top:772px;text-align:center;font:500 28px/1 "Inter";color:var(--brown)}`,
        html: `
    <div class="band l"></div><div class="band r"></div>
    ${chips}
    <div class="rule" id="f14-r1" style="top:262px"></div>
    <div class="abs" id="f14-q">« La Révolution française est le plus puissant pas du genre humain depuis l'avènement du Christ. »</div>
    <div class="abs" id="f14-by">— Victor Hugo</div>
    <div class="rule" id="f14-r2" style="top:612px"></div>
    <div class="abs" id="f14-name">Yazid Tragha</div>
    <div class="abs" id="f14-sub">Frise chronologique de révision — Évaluation</div>`,
      };
    },
  },
];
