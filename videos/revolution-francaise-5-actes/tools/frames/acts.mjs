// Frames 4-12: the five acts. Every act frame shares one stage — the frise strip on top
// (current act lit, the flame riding it), the PDF act banner, then PDF-style event cards.
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { ACT, arrow, banner, card, flame, frise, icon, slim, yearX } from "../kit.mjs";

const SX = 120, SW = 1680, SY = 22; // top frise strip
const strip = (id, a, year, scale = 0.6) =>
  `${frise(`${id}-frise`, { x: SX, y: SY, w: SW, active: a })}${flame(`${id}-flame`, yearX(SX, SW, year), SY + 41 - 98 + 6, scale)}`;

const TAG_CSS = `.tag .t b{font-weight:800}`;

export default [
  {
    id: "04-acte1-grand-saut",
    build() {
      return {
        css: TAG_CSS,
        html: `
    ${strip("f04", 1, 1789.45)}
    ${banner("f04-banner", 1)}
    ${card("f04-c1", 1, { x: 120, y: 342, w: 520, h: 400, ico: "crown", date: "5 mai 1789", title: "Ouverture des États généraux", line: "Vote <b>par ordre</b> : le tiers état, 98&nbsp;% de la population, est mis en minorité → <b>échec</b>." })}
    ${card("f04-c2", 1, { x: 700, y: 342, w: 520, h: 400, ico: "hand", date: "17 & 20 juin 1789", title: "Serment du Jeu de paume", line: "Le tiers état se proclame <b>Assemblée nationale</b> et jure de donner une <b>constitution</b>.", star: true })}
    ${card("f04-c3", 1, { x: 1280, y: 342, w: 520, h: 400, ico: "bastille", date: "14 juillet 1789", title: "Prise de la Bastille", line: "Le peuple de Paris prend la prison royale. Aujourd'hui, la <b>fête nationale</b>.", star: true })}
    ${arrow("f04-arrow", "Déclaration de guerre à la monarchie absolue : <b>la souveraineté passe du roi à la nation</b>.", { x: 120, y: 792, w: 1680 })}`,
      };
    },
  },
  {
    id: "05-acte1-societe-nouvelle",
    build() {
      return {
        css: `
#f05-c2 .q{margin-top:18px;background:#F5EBD5;border-radius:10px;padding:18px 24px;font:italic 400 30px/1.45 "Merriweather";color:var(--ink)}
#f05-c2 .q b{font-weight:400;color:var(--a1)}
#f05-bilan{left:120px;top:744px;width:1680px;height:148px;background:#fff;border:3px solid var(--a1);border-radius:14px;padding:16px 30px}
#f05-bilan .h{font:900 28px/1 "Merriweather";color:var(--a1)}
#f05-bilan .row{display:flex;gap:36px;margin-top:16px;font:600 27px/1.25 "Inter"}
#f05-bilan .row span{flex:1}`,
        html: `
    ${strip("f05", 1, 1789.7)}
    ${slim("f05-slim", 1, "Une société nouvelle")}
    ${card("f05-c1", 1, { x: 120, y: 290, w: 470, h: 430, ico: "flame", date: "Nuit du 4 août 1789", title: "Abolition des privilèges", line: "La <b>société d'ordres</b>, qui structurait le royaume depuis des siècles, est mise à mort.", star: true })}
    <div class="card star" id="f05-c2" style="left:630px;top:290px;width:660px;height:430px;background:linear-gradient(180deg, ${ACT[1].tint} 0%, #FFFFFF 55%);border-color:${ACT[1].c}">
      <div class="medal" style="border-color:${ACT[1].c}">${icon("scroll")}</div>
      <div class="pill" style="background:${ACT[1].c}">26 août 1789</div>
      <div class="ct" style="color:${ACT[1].c}">Déclaration des droits de l'homme et du citoyen <span class="st">★</span></div>
      <div class="q">Art. 1 : « Les hommes naissent et demeurent <b>libres et égaux en droits</b>. »</div>
    </div>
    ${card("f05-c3", 1, { x: 1330, y: 290, w: 470, h: 430, ico: "bread", date: "5 & 6 octobre 1789", title: "Marche des femmes sur Versailles", line: "Le roi doit venir vivre à Paris, aux <b>Tuileries</b>, sous surveillance." })}
    <div class="abs" id="f05-bilan"><div class="h">Bilan de 1789</div>
      <div class="row"><span>→ Fin de la monarchie absolue et de la société d'ordres</span><span>→ Les Français deviennent des <b>citoyens</b></span><span>→ La souveraineté appartient à la <b>nation</b></span></div></div>`,
      };
    },
  },
  {
    id: "06-acte2-varennes",
    build({ ROOT }) {
      const g = JSON.parse(readFileSync(join(ROOT, "assets/map/varennes-geo.json"), "utf8"));
      const P = g.places;
      const town = (k, dx, dy, anchor = "start", sub = "") =>
        `<g id="f06-town-${k}"><circle cx="${P[k].xy[0]}" cy="${P[k].xy[1]}" r="10" fill="#2B2118" stroke="#FFFDF7" stroke-width="4"/>
        <text class="tl" x="${P[k].xy[0] + dx}" y="${P[k].xy[1] + dy}" text-anchor="${anchor}">${P[k].name}</text>
        ${sub ? `<text class="ts" x="${P[k].xy[0] + dx}" y="${P[k].xy[1] + dy + 34}" text-anchor="${anchor}">${sub}</text>` : ""}</g>`;
      const [vx, vy] = P.varennes.xy;
      return {
        css: `
#f06-ground2{position:absolute;inset:0;background:radial-gradient(1400px 900px at 55% 55%, #F7EED9 0%, #EFE0BF 70%, #E3CFA4 100%)}
#f06-map{position:absolute;left:0;top:0;width:1920px;height:1080px}
#f06-map .riv{fill:#9DB7CB;stroke:#9DB7CB;stroke-width:1.2;opacity:0.45}
#f06-map .rline{fill:none;stroke:#7E9CB5;stroke-width:4.5;stroke-linecap:round;stroke-linejoin:round}
#f06-map .rl{font:italic 400 24px "Merriweather";fill:#6F8DA6}
#f06-map .tl{font:800 32px "Inter";fill:#2B2118;paint-order:stroke;stroke:#F7EED9;stroke-width:8px}
#f06-map .ts{font:600 24px "Inter";fill:#7A5A3A;paint-order:stroke;stroke:#F7EED9;stroke-width:7px}
#f06-map .bl{font:500 19px "JetBrains Mono";letter-spacing:0.18em;fill:#8C6A43}
#f06-top{position:absolute;left:0;top:0;width:1920px;height:104px;background:rgba(255,253,247,0.88);border-bottom:2px solid rgba(201,180,138,0.6)}
#f06-cart{left:${vx - 128}px;top:${vy - 40}px;width:96px;height:96px}
#f06-cart svg{width:96px;height:96px}
#f06-mc{left:70px;top:268px;width:760px;height:80px;font-size:27px}`,
        html: `
    <div class="clip" id="f06-ground2" data-start="0" data-duration="__D__" data-track-index="1"></div>
    <svg id="f06-map" viewBox="0 0 1920 1080" xmlns="http://www.w3.org/2000/svg">
      <g id="f06-rivers">${g.rivers.map((d) => `<path class="riv" d="${d}"/>`).join("")}</g>
      <g id="f06-rlines">${Object.values(g.riverLines).map((d) => `<path class="rline" d="${d}"/>`).join("")}</g>
      ${g.riverLabels.map((l) => `<text class="rl" x="${l.xy[0]}" y="${l.xy[1]}" transform="rotate(${l.rot} ${l.xy[0]} ${l.xy[1]})">${l.name}</text>`).join("")}
      <g id="f06-border">${g.border.map((d) => `<path d="${d}" fill="none" stroke="#8C6A43" stroke-width="3.5" stroke-dasharray="14 10"/>`).join("")}</g>
      <text class="bl" x="1690" y="196">PAYS-BAS</text>
      <text class="bl" x="1690" y="222">AUTRICHIENS</text>
      <path id="f06-planned" d="${g.planned}" fill="none" stroke="#D68910" stroke-width="5" stroke-dasharray="3 13" stroke-linecap="round" opacity="0.85"/>
      <path id="f06-route" d="${g.route}" fill="none" stroke="#D68910" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>
      ${town("paris", 0, 52, "middle")}
      ${town("menehould", -14, 50, "end", "Drouet reconnaît le roi")}
      ${town("varennes", 40, -6, "start", "arrêté le 21 juin 1791")}
      ${town("montmedy", 24, 2, "start", "jamais atteint")}
      <g id="f06-x" stroke="#C0392B" stroke-width="9" stroke-linecap="round"><path d="M${vx - 22} ${vy - 22} L${vx + 22} ${vy + 22} M${vx + 22} ${vy - 22} L${vx - 22} ${vy + 22}"/></g>
    </svg>
    <div class="abs" id="f06-cart">${icon("carriage", "#D68910")}</div>
    <div id="f06-top"></div>
    ${strip("f06", 2, 1791.47)}
    ${banner("f06-banner", 2, { x: 70, y: 124, w: 760, h: 128, title: "La fuite à Varennes" })}
    <div class="tag" id="f06-mc">${icon("scales")}<span class="t"><b>Monarchie constitutionnelle</b> : le roi partage le pouvoir</span></div>
    ${card("f06-c1", 2, { x: 70, y: 430, w: 760, h: 250, ico: "carriage", date: "Nuit du 20 au 21 juin 1791", title: "La fuite du roi", line: "Déguisé en valet, Louis XVI fuit avec sa famille vers <b>Montmédy</b>.", star: true })}
    ${arrow("f06-arrow", "La <b>confiance</b> entre le roi et le peuple <b>est brisée</b>.", { x: 980, y: 792, w: 850 })}
    <div class="credit" id="f06-credit" style="left:60px;top:872px">${g.credits}</div>`,
      };
    },
  },
  {
    id: "07-acte3-republique",
    build() {
      return {
        css: `${TAG_CSS}
#f07-why{left:120px;top:300px;font-size:21px;color:var(--ink-soft)}
#f07-c1 .ct,#f07-c2 .ct{font-size:36px}
.tag{height:110px}`,
        html: `
    ${strip("f07", 3, 1792.4)}
    ${banner("f07-banner", 3)}
    <div class="abs mono" id="f07-why">Pourquoi la monarchie échoue</div>
    <div class="tag" id="f07-t1" style="left:120px;top:345px;width:690px">${icon("veto")}<span class="t">Droit de <b>veto</b> : le roi bloque les lois</span></div>
    <div class="tag" id="f07-t2" style="left:120px;top:477px;width:690px">${icon("swords")}<span class="t"><b>20 avril 1792</b> : la guerre contre l'Autriche tourne mal</span></div>
    <div class="tag" id="f07-t3" style="left:120px;top:609px;width:690px">${icon("eye")}<span class="t">Le roi est <b>soupçonné de trahison</b></span></div>
    ${card("f07-c1", 3, { x: 860, y: 352, w: 450, h: 400, ico: "temple", date: "10 août 1792", title: "Prise des Tuileries", line: "Les sans-culottes, menés par Danton : <b>chute de la monarchie</b>.", star: true })}
    ${card("f07-c2", 3, { x: 1350, y: 352, w: 450, h: 400, ico: "bonnet", date: "21 & 22 sept. 1792", title: "Naissance de la République", line: "La <b>Convention</b> abolit la monarchie : c'est l'<b>an I</b>.", star: true })}
    ${arrow("f07-arrow", "La Convention est élue au <b>suffrage universel masculin</b> · la veille, victoire de <b>Valmy</b>.", { x: 120, y: 792, w: 1680 })}`,
      };
    },
  },
  {
    id: "08-acte4-mort-du-roi",
    build() {
      return {
        css: `${TAG_CSS}
#f08-h{left:1000px;top:322px;font:900 46px/1.1 "Merriweather";color:var(--a4)}
.tag{flex-direction:row;align-items:center;height:160px}
.tag .t{display:flex;flex-direction:column;gap:8px}
.tag .k{font:500 20px/1 "JetBrains Mono";letter-spacing:0.24em;color:var(--a4)}
#f08-c1 .cl{font-size:31px}
#f08-c1 .q{margin-top:20px;background:#F6E6E4;border-radius:10px;padding:16px 22px;font:italic 400 27px/1.45 "Merriweather";color:var(--a4)}`,
        html: `
    ${strip("f08", 4, 1793.35, 0.75)}
    ${banner("f08-banner", 4)}
    ${card("f08-c1", 4, { x: 120, y: 352, w: 800, h: 400, ico: "guillotine", date: "21 janvier 1793 · 10 h 22", title: "La mort de Louis Capet", line: "Jugé par la Convention, il est guillotiné place de la Révolution : <b>la fin de la monarchie</b>.<div class=\"q\">La foule : « Vive la Révolution ! Vive la République ! Vive la nation ! »</div>", star: true })}
    <div class="abs" id="f08-h">La guerre, dehors et dedans</div>
    <div class="tag" id="f08-t1" style="left:1000px;top:408px;width:800px">${icon("swords")}<span class="t"><span class="k">Dehors</span><span><b>Guerre extérieure</b> : Prusse, Autriche-Hongrie, Angleterre… se coalisent.</span></span></div>
    <div class="tag" id="f08-t2" style="left:1000px;top:592px;width:800px">${icon("flame")}<span class="t"><span class="k">Dedans</span><span><b>Guerre civile</b> : les royalistes de Vendée prennent les armes (mars 1793).</span></span></div>
    ${arrow("f08-arrow", "Fracture dans la Convention : <b>Girondins</b> contre <b>Montagnards</b>.", { x: 120, y: 800, w: 1680, h: 84 })}`,
      };
    },
  },
  {
    id: "09-acte4-terreur",
    build() {
      return {
        css: `
.col{position:absolute;top:208px;width:780px;height:300px;border-radius:14px;overflow:hidden;background:#fff}
.col .hd{height:62px;display:flex;align-items:center;padding:0 28px;font:900 34px/1 "Merriweather";color:#fff}
.col ul{margin:0;padding:18px 28px 0 54px;font:500 27px/1.5 "Inter"}
.col b{font-weight:800}
#f09-g{left:120px;border:2px solid #AEB8C5;background:#F6F8FA}
#f09-g .hd{background:#8796A8}
#f09-g ul{color:#6B7785}
#f09-m{left:1020px;border:3px solid var(--a4);background:linear-gradient(180deg, ${ACT[4].tint}, #fff 70%)}
#f09-m .hd{background:var(--a4)}
#f09-stamp{left:520px;top:432px;padding:10px 18px;border:3px solid #C0392B;border-radius:8px;color:#C0392B;font:800 24px/1 "Inter";transform:rotate(-6deg);background:rgba(255,255,255,0.85)}
#f09-jun{left:906px;top:318px;width:108px;height:108px;border-radius:50%;background:var(--a4);color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;font:800 22px/1.1 "Inter";text-align:center}
#f09-jun .ar{font:900 36px/1 "Merriweather"}
#f09-an1{left:1020px;top:522px;width:780px;height:52px;border-radius:10px;background:#FFF8E6;border:2px dashed var(--gold);display:flex;align-items:center;padding:0 20px;font:600 22px/1 "Inter";white-space:nowrap}
#f09-an1 .st{color:var(--gold);margin:0 8px}
#f09-lab{left:120px;top:540px;font-size:22px;color:var(--a4)}
.blk{position:absolute;top:592px;height:166px;background:#fff;border:2px solid var(--gold-soft);border-radius:14px;padding:20px 22px;display:flex;gap:18px;align-items:flex-start}
.blk svg{width:60px;height:60px;flex:none}
.blk .t{font:800 29px/1.2 "Inter";color:var(--a4)}
.blk .s{font:500 25px/1.35 "Inter";margin-top:8px}`,
        html: `
    ${strip("f09", 4, 1793.6, 0.85)}
    ${slim("f09-slim", 4, "La Terreur des Montagnards")}
    <div class="col" id="f09-g"><div class="hd">Girondins</div><ul>
      <li>Députés de province : Brissot, Vergniaud…</li><li>Bourgeoisie · république modérée</li><li>Hésitent sur le sort du roi</li></ul></div>
    <div class="abs" id="f09-stamp">Arrêtés le 2 juin 1793</div>
    <div class="abs" id="f09-jun"><span class="ar">→</span>2 juin<br/>1793</div>
    <div class="col" id="f09-m"><div class="hd">Montagnards</div><ul>
      <li>Députés de Paris : <b>Robespierre</b>, Danton, Saint-Just, Marat</li><li>Soutenus par les <b>sans-culottes</b></li><li>Mesures d'exception pour sauver la République</li></ul></div>
    <div class="abs" id="f09-an1"><span>24 juin 1793 · <b>Constitution de l'an I</b></span><span class="st">★</span><span>votée, jamais appliquée</span></div>
    <div class="abs mono" id="f09-lab">La Terreur · été 1793 — 1794</div>
    <div class="blk" id="f09-b1" style="left:120px;width:400px">${icon("people")}<div><div class="t">Comité de salut public</div><div class="s">12 membres, fixe la politique</div></div></div>
    <div class="blk" id="f09-b2" style="left:545px;width:400px">${icon("scales")}<div><div class="t">Tribunal révolutionnaire</div><div class="s">juge les « ennemis de la Révolution »</div></div></div>
    <div class="blk" id="f09-b3" style="left:970px;width:400px">${icon("eye")}<div><div class="t">Loi des suspects</div><div class="s">septembre 1793</div></div></div>
    <div class="blk" id="f09-b4" style="left:1395px;width:405px;border:3px solid var(--a4)">${icon("guillotine")}<div><div class="t">16 octobre 1793</div><div class="s">Marie-Antoinette guillotinée</div></div></div>
    ${arrow("f09-arrow", "<b>Terrifier les ennemis</b> de la Révolution pour <b>sauver la République</b>.", { x: 120, y: 800, w: 1680, h: 84 })}`,
      };
    },
  },
  {
    id: "10-acte4-thermidor",
    build() {
      const plate = (id, x, rot, name, extra, date, sub, star) => `
    <div class="plate" id="${id}" style="left:${x}px;transform:rotate(${rot}deg)">
      <div class="medal">${icon("guillotine")}</div>
      <div class="pill" style="background:${ACT[4].c}">${date}</div>
      <div class="nm">${name}${star ? ' <span class="st">★</span>' : ""}</div>${extra ? `<div class="ex">${extra}</div>` : ""}
      <div class="sb">${sub}</div></div>`;
      return {
        css: `
#f10-q{left:120px;width:1680px;top:208px;text-align:center;font:900 64px/1.2 "Merriweather";color:var(--a4)}
.plate{position:absolute;top:396px;width:500px;height:340px;background:#fff;border:3px solid var(--a4);border-radius:14px;padding:92px 34px 26px;box-shadow:0 10px 26px rgba(43,33,24,0.1)}
.plate .medal{position:absolute;top:-52px;left:30px;width:112px;height:112px;border-radius:50%;background:#fff;border:5px solid var(--a4);display:flex;align-items:center;justify-content:center}
.plate .medal svg{width:70px;height:70px}
.plate .pill{position:absolute;top:28px;left:160px}
.plate .nm{font:900 54px/1.1 "Merriweather";color:var(--ink)}
.plate .nm .st{color:var(--gold);font-size:44px}
.plate .ex{font:700 28px/1.2 "Inter";color:var(--ink-soft);margin-top:4px}
.plate .sb{font:500 27px/1.38 "Inter";margin-top:14px}
.plate .sb b{font-weight:800}`,
        html: `
    ${strip("f10", 4, 1794.4, 1.15)}
    ${slim("f10-slim", 4, "Thermidor")}
    <div class="abs" id="f10-q">« La Révolution dévore ses propres enfants »</div>
    ${plate("f10-p1", 120, -2, "Danton", "", "5 avril 1794", "<b>Indulgent</b> : voulait ralentir la Terreur. Guillotiné.")}
    ${plate("f10-p2", 710, 2, "Desmoulins", "", "5 avril 1794", "<b>Indulgent</b>, ami de Danton. Guillotiné.")}
    ${plate("f10-p3", 1300, -2.5, "Robespierre", "et Saint-Just", "27 — 28 juillet 1794", "<b>9 thermidor an II</b> : arrêté, puis guillotiné.", true)}
    ${arrow("f10-arrow", "<b>Fin de la Terreur</b> et de la domination des Montagnards : une nouvelle phase.", { x: 120, y: 800, w: 1680, h: 84 })}`,
      };
    },
  },
  {
    id: "11-acte5-directoire",
    build() {
      return {
        css: `
#f11-c2 ul{margin:14px 0 0;padding:0 0 0 30px;font:500 28px/1.45 "Inter"}
#f11-c2 b{font-weight:800}
#f11-frise .seg{filter:saturate(0.6)}`,
        html: `
    ${strip("f11", 5, 1795.55, 0.5)}
    ${banner("f11-banner", 5)}
    ${card("f11-c1", 5, { x: 120, y: 352, w: 470, h: 400, ico: "temple", date: "Août 1794", title: "Fin de la Commune de Paris", line: "Les <b>sans-culottes</b> sont écartés du pouvoir." })}
    <div class="card star" id="f11-c2" style="left:630px;top:352px;width:660px;height:400px;background:linear-gradient(180deg, ${ACT[5].tint} 0%, #FFFFFF 55%);border-color:${ACT[5].c}">
      <div class="medal" style="border-color:${ACT[5].c}">${icon("ballot")}</div>
      <div class="pill" style="background:${ACT[5].c}">1795 (an III)</div>
      <div class="ct" style="color:${ACT[5].c}">Le Directoire <span class="st">★</span></div>
      <ul><li><b>Retour du suffrage censitaire</b> : seuls les plus riches votent</li><li>2 assemblées : Anciens et Cinq-Cents</li><li>5 Directeurs au pouvoir exécutif</li></ul>
    </div>
    ${card("f11-c3", 5, { x: 1330, y: 352, w: 470, h: 400, ico: "bicorne", date: "1795 — 1799", title: "Un régime instable", line: "Il s'appuie sur l'<b>armée</b>, où brille le général <b>Bonaparte</b>." })}
    ${arrow("f11-arrow", "Une <b>République modérée</b>, moins démocratique que celle de 1793.", { x: 120, y: 800, w: 1680, h: 84 })}`,
      };
    },
  },
  {
    id: "12-brumaire",
    build() {
      const fx = 160, fw = 1600, fy = 742;
      const ex = yearX(fx, fw, 1799);
      return {
        css: `
#f12-c .ct{font-size:50px}
#f12-c .cl{font-size:32px}
#f12-smoke{left:${ex - 60}px;top:${fy - 190}px;width:120px;height:200px}`,
        html: `
    ${slim("f12-slim", 5, "18 brumaire")}
    ${card("f12-c", 5, { x: 410, y: 268, w: 1100, h: 380, ico: "bicorne", date: "9 novembre 1799 · 18 brumaire an VIII", title: "Coup d'État de Bonaparte : fin de la Révolution", line: "Bonaparte prend le pouvoir et met en place le <b>Consulat</b>. La Révolution aura duré <b>10 ans</b>.", star: true })}
    ${frise("f12-frise", { x: fx, y: fy, w: fw, years: [1789, 1790, 1792, 1793, 1795] })}
    <div class="abs" id="f12-y1799" style="left:${ex - 40}px;top:${fy + 66}px;font:800 26px/1 Inter;color:var(--a5)">1799</div>
    <svg class="abs" id="f12-smoke" viewBox="0 0 120 200" xmlns="http://www.w3.org/2000/svg">
      <path id="f12-sm1" d="M60 196 C40 170 78 150 58 124 C40 100 76 84 60 56" fill="none" stroke="#8C949C" stroke-width="7" stroke-linecap="round" opacity="0.55"/>
      <path id="f12-sm2" d="M66 190 C84 168 52 146 72 118 C88 96 60 78 74 40" fill="none" stroke="#AEB8C5" stroke-width="5" stroke-linecap="round" opacity="0.45"/>
    </svg>
    ${flame("f12-flame", ex, fy + 41 - 98 + 6, 0.32)}`,
      };
    },
  },
];
