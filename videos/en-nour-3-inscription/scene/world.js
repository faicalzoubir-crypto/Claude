// The EN-NOUR 3 visit world: a rising staircase of floating isometric islands.
// S0 = the real façade (from the client's photo); S1..S7 = the 7 steps of the visit plan.
import * as THREE from "three";
import {
  C, mat, ownMat, bubbleSprite, rbox, box, cyl, sph, group, canvasTex, panel, roundRect, hex, rng,
  pillSprite, iconBubble, badgeSprite, glowSprite, ICONS, FONT_DISPLAY, FONT_TEXT,
} from "./lib.js";
import { person, pose } from "./people.js";
import * as P from "./props.js";

const F = P.F;
const WALL_H = 2.5;
const WALL_T = 0.22;

// ── Layout ──────────────────────────────────────────────────────────────────
export const STATIONS = [
  { key: "facade", size: 12.4, floor: C.pave, exit: "z" },
  { key: "accueil", size: 9, floor: C.floorWarm, exit: "x" },
  { key: "presentation", size: 9, floor: 0xe9e2f2, exit: "z" },
  { key: "infra", size: 11.4, floor: C.floorTile, exit: "x" },
  { key: "organisation", size: 9, floor: 0xe3eef6, exit: "z" },
  { key: "services", size: 9, floor: 0xfaeed7, exit: "x" },
  { key: "modalites", size: 9, floor: 0xe8f0e6, exit: "z" },
  { key: "conclusion", size: 9.6, floor: C.lawn, exit: null },
];
const GAP = 2.4;
const RISE = [6.2, 3.4, 3.4, 3.4, 3.4, 3.4, 3.6];
(function layout() {
  let pos = new THREE.Vector3(0, 0, 0);
  STATIONS.forEach((s, i) => {
    s.pos = pos.clone();
    s.half = s.size / 2;
    if (i < STATIONS.length - 1) {
      const n = STATIONS[i + 1];
      const d = s.half + GAP + n.size / 2;
      pos = pos.clone().add(new THREE.Vector3(s.exit === "x" ? -d : 0, RISE[i], s.exit === "z" ? -d : 0));
      n.entry = s.exit; // enters on the + edge of that axis
    }
  });
  STATIONS[0].entry = "x";
})();

// ── Island base ─────────────────────────────────────────────────────────────
function island(parent, s) {
  const g = group(parent, s.pos.x, s.pos.y, s.pos.z);
  const S = s.size;
  rbox(g, S, 0.4, S, C.cream, 0, -0.4, 0, 0.16);
  rbox(g, S - 0.36, 0.05, S - 0.36, s.floor, 0, -0.02, 0, 0.02, { shadow: false });
  box(g, S - 0.5, 0.09, S - 0.5, C.sun, 0, -0.5, 0, { emissive: C.sun, emissiveIntensity: 0.55, shadow: false });
  rbox(g, S - 0.3, 1.05, S - 0.3, C.blue, 0, -1.55, 0, 0.2);
  rbox(g, S - 1.4, 0.55, S - 1.4, C.deep, 0, -2.0, 0, 0.24);
  s.group = g;
  return g;
}

// Back walls with an optional door gap. axis 'x' → wall along the -x edge.
function backWalls(g, s, opts = {}) {
  const S = s.size, h = opts.h ?? WALL_H, half = s.half;
  const color = opts.color ?? C.wall;
  const band = opts.band ?? C.blue;
  const door = s.exit; // door sits on the exit wall
  const doorU = opts.doorU ?? 0;
  const doorW = 1.3;
  function wallAlong(axis) {
    // axis 'z': wall at z=-half spanning x; axis 'x': wall at x=-half spanning z
    const segs = [];
    if (door === axis) {
      segs.push([-half, doorU - doorW / 2]);
      segs.push([doorU + doorW / 2, half]);
    } else segs.push([-half, half]);
    segs.forEach(([a, b]) => {
      const len = b - a, mid = (a + b) / 2;
      if (len < 0.05) return;
      if (axis === "z") {
        rbox(g, len, h, WALL_T, color, mid, F, -half + WALL_T / 2, 0.03);
        box(g, len, 0.5, 0.02, band, mid, F + 0.08, -half + WALL_T + 0.005, { shadow: false });
        box(g, len, 0.05, 0.02, C.sun, mid, F + 0.62, -half + WALL_T + 0.005, { shadow: false });
      } else {
        rbox(g, WALL_T, h, len, color, -half + WALL_T / 2, F, mid, 0.03);
        box(g, 0.02, 0.5, len, band, -half + WALL_T + 0.005, F + 0.08, mid, { shadow: false });
        box(g, 0.02, 0.05, len, C.sun, -half + WALL_T + 0.005, F + 0.62, mid, { shadow: false });
      }
    });
    if (door === axis) {
      // lintel + glowing doorway
      if (axis === "z") {
        rbox(g, doorW + 0.3, 0.35, WALL_T + 0.06, C.blue, doorU, F + 2.0, -half + WALL_T / 2, 0.04);
        const glow = box(g, doorW, 2.0, 0.02, C.sun, doorU, F, -half + 0.03, { basic: true, transparent: true, opacity: 0.35, shadow: false });
        s.doorGlow = glow;
      } else {
        rbox(g, WALL_T + 0.06, 0.35, doorW + 0.3, C.blue, -half + WALL_T / 2, F + 2.0, doorU, 0.04);
        const glow = box(g, 0.02, 2.0, doorW, C.sun, -half + 0.03, F, doorU, { basic: true, transparent: true, opacity: 0.35, shadow: false });
        s.doorGlow = glow;
      }
    }
  }
  wallAlong("z");
  wallAlong("x");
  // corner post
  rbox(g, WALL_T + 0.08, h + 0.06, WALL_T + 0.08, C.white, -half + WALL_T / 2, F, -half + WALL_T / 2, 0.04);
}

// Points where the light path leaves / enters an island (local coords).
function edgePoint(s, axis, sign) {
  const h = s.half - 0.2;
  return axis === "x" ? new THREE.Vector3(sign * h, F + 0.05, 0) : new THREE.Vector3(0, F + 0.05, sign * h);
}

// ── Textures ────────────────────────────────────────────────────────────────
function facadeTex() {
  return canvasTex(512, 512, (ctx, W, H) => {
    ctx.fillStyle = hex(C.facade);
    ctx.fillRect(0, 0, W, H);
    ctx.strokeStyle = "rgba(150,158,165,0.55)";
    ctx.lineWidth = 3;
    const lines = [[0, 120, 300, 0], [80, 512, 512, 140], [0, 380, 220, 512], [260, 0, 512, 330], [140, 260, 420, 512], [0, 250, 160, 180]];
    lines.forEach(([a, b, c, d]) => {
      ctx.beginPath();
      ctx.moveTo(a, b);
      ctx.lineTo(c, d);
      ctx.stroke();
    });
  });
}
function glassTex() {
  return canvasTex(256, 512, (ctx, W, H) => {
    const g = ctx.createLinearGradient(0, 0, W, H);
    g.addColorStop(0, "#9fc2e0");
    g.addColorStop(0.5, "#6d8fb3");
    g.addColorStop(1, "#557595");
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = "rgba(255,255,255,0.25)";
    ctx.beginPath();
    ctx.moveTo(0, H * 0.55);
    ctx.lineTo(W, H * 0.25);
    ctx.lineTo(W, H * 0.38);
    ctx.lineTo(0, H * 0.68);
    ctx.fill();
    ctx.strokeStyle = "rgba(230,236,240,0.9)";
    ctx.lineWidth = 5;
    for (let x = 0; x <= W; x += W / 4) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, H);
      ctx.stroke();
    }
    for (let y = 0; y <= H; y += H / 8) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(W, y);
      ctx.stroke();
    }
  });
}
function grilleTex() {
  // stainless moucharabieh-like gate panel
  return canvasTex(256, 256, (ctx, W, H) => {
    ctx.fillStyle = "#c9d0d6";
    ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = "#6f7a85";
    const R = rng(7);
    for (let i = 0; i < 46; i++) {
      const x = R() * W, y = R() * H, rx = 8 + R() * 14, ry = 6 + R() * 12;
      ctx.beginPath();
      ctx.ellipse(x, y, rx, ry, R() * 3, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.strokeStyle = "#e9edf0";
    ctx.lineWidth = 10;
    ctx.strokeRect(0, 0, W, H);
  });
}
function paveTex() {
  const t = canvasTex(256, 256, (ctx, W, H) => {
    ctx.fillStyle = hex(C.pave);
    ctx.fillRect(0, 0, W, H);
    ctx.strokeStyle = "rgba(170,140,100,0.35)";
    ctx.lineWidth = 3;
    for (let i = 0; i <= 4; i++) {
      ctx.beginPath();
      ctx.moveTo(i * 64, 0);
      ctx.lineTo(i * 64, H);
      ctx.moveTo(0, i * 64);
      ctx.lineTo(W, i * 64);
      ctx.stroke();
    }
  });
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  return t;
}
function roadTex() {
  return canvasTex(1024, 96, (ctx, W, H) => {
    ctx.fillStyle = "#62666d";
    ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = "rgba(255,255,255,0.75)";
    for (let x = 30; x < W; x += 120) ctx.fillRect(x, H / 2 - 4, 60, 8);
  });
}
// "EN-NOUR [3] (logo)" lettering of the left wing, after the client's photo
function facadeSignTex(logoImg) {
  return canvasTex(1320, 330, (ctx, W, H) => {
    ctx.font = `800 210px "${FONT_DISPLAY}"`;
    ctx.textBaseline = "middle";
    ctx.lineWidth = 10;
    ctx.strokeStyle = "rgba(120,86,20,0.55)";
    ctx.strokeText("EN-NOUR", 10, H / 2 + 18);
    ctx.fillStyle = "#e2b64a";
    ctx.fillText("EN-NOUR", 10, H / 2 + 18);
    const tw = ctx.measureText("EN-NOUR").width;
    const x3 = 10 + tw + 40;
    roundRect(ctx, x3, H / 2 - 110, 200, 220, 18);
    ctx.fillStyle = hex(C.sun);
    ctx.fill();
    ctx.fillStyle = "#ffffff";
    ctx.textAlign = "center";
    ctx.fillText("3", x3 + 100, H / 2 + 18);
    const cx = x3 + 200 + 150;
    ctx.beginPath();
    ctx.arc(cx, H / 2, 125, 0, Math.PI * 2);
    ctx.fillStyle = "#ffffff";
    ctx.fill();
    ctx.lineWidth = 8;
    ctx.strokeStyle = hex(C.sun);
    ctx.stroke();
    if (logoImg) {
      const s = 210 / Math.max(logoImg.width, logoImg.height);
      ctx.drawImage(logoImg, cx - (logoImg.width * s) / 2, H / 2 - (logoImg.height * s) / 2, logoImg.width * s, logoImg.height * s);
    }
  });
}
// "ÉCOLE EN-NOUR 3" letters on the entrance canopy
function schoolSignTex() {
  return canvasTex(1500, 270, (ctx, W, H) => {
    ctx.font = `800 170px "${FONT_DISPLAY}"`;
    ctx.textBaseline = "middle";
    const a = "ÉCOLE EN-NOUR ";
    const wa = ctx.measureText(a).width;
    const wb = ctx.measureText("3").width;
    const x0 = (W - wa - wb) / 2;
    ctx.lineWidth = 12;
    ctx.strokeStyle = "rgba(60,70,80,0.55)";
    ctx.strokeText(a, x0, H / 2 + 12);
    ctx.fillStyle = "#f4f6f8";
    ctx.fillText(a, x0, H / 2 + 12);
    ctx.strokeText("3", x0 + wa, H / 2 + 12);
    ctx.fillStyle = hex(C.sun);
    ctx.fillText("3", x0 + wa, H / 2 + 12);
  });
}
function textPlate(text, opts = {}) {
  const { px = 110, font = FONT_DISPLAY, weight = 800, color = hex(C.sun), w = 1400, h = 180, stroke = null, align = "center" } = opts;
  return canvasTex(w, h, (ctx, W, H) => {
    ctx.font = `${weight} ${px}px "${font}"`;
    ctx.textAlign = align;
    ctx.textBaseline = "middle";
    if (stroke) {
      ctx.lineWidth = px * 0.12;
      ctx.strokeStyle = stroke;
      ctx.strokeText(text, align === "center" ? W / 2 : 10, H / 2 + px * 0.05);
    }
    ctx.fillStyle = color;
    ctx.fillText(text, align === "center" ? W / 2 : 10, H / 2 + px * 0.05);
  });
}
function flagTex() {
  return canvasTex(180, 120, (ctx, W, H) => {
    ctx.fillStyle = "#c1272d";
    ctx.fillRect(0, 0, W, H);
    ctx.strokeStyle = "#006233";
    ctx.lineWidth = 6;
    ctx.beginPath();
    const cx = W / 2, cy = H / 2, r = 34;
    for (let i = 0; i <= 5; i++) {
      const a = -Math.PI / 2 + (i * 4 * Math.PI) / 5;
      const x = cx + Math.cos(a) * r, y = cy + Math.sin(a) * r;
      i ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
    }
    ctx.stroke();
  });
}

// Screen / board contents ----------------------------------------------------
function slideTex() {
  return canvasTex(768, 432, (ctx, W, H) => {
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = hex(C.blue);
    ctx.fillRect(0, 0, W, 86);
    ctx.font = `800 54px "${FONT_DISPLAY}"`;
    ctx.fillStyle = "#ffffff";
    ctx.textBaseline = "middle";
    ctx.fillText("Projet pédagogique", 34, 46);
    const cyc = [["Maternelle", C.maternelle], ["Primaire", C.primaire], ["Collège", C.college], ["Lycée", C.lycee]];
    cyc.forEach(([name, col], i) => {
      const x = 34 + i * 178, y = 130;
      roundRect(ctx, x, y, 160, 200, 22);
      ctx.fillStyle = hex(col);
      ctx.fill();
      ctx.fillStyle = "#ffffff";
      ctx.font = `800 30px "${FONT_DISPLAY}"`;
      ctx.textAlign = "center";
      ctx.fillText(name, x + 80, y + 160);
      ctx.beginPath();
      ctx.arc(x + 80, y + 76, 42, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(255,255,255,0.9)";
      ctx.fill();
      ctx.fillStyle = hex(col);
      ctx.font = `800 52px "${FONT_DISPLAY}"`;
      ctx.fillText(String(i + 1), x + 80, y + 80);
      ctx.textAlign = "left";
    });
    ctx.fillStyle = hex(C.sun);
    roundRect(ctx, 34, 360, 300, 40, 20);
    ctx.fill();
    ctx.fillStyle = "#d9e8f4";
    roundRect(ctx, 350, 360, 384, 40, 20);
    ctx.fill();
  });
}
function planBoardTex() {
  const steps = ["Accueil", "Présentation", "Infrastructures", "Organisation", "Services", "Modalités", "Conclusion"];
  return canvasTex(512, 720, (ctx, W, H) => {
    ctx.fillStyle = "#ffffff";
    roundRect(ctx, 0, 0, W, H, 34);
    ctx.fill();
    ctx.fillStyle = hex(C.blue);
    roundRect(ctx, 0, 0, W, 120, 34);
    ctx.fill();
    ctx.fillRect(0, 60, W, 60);
    ctx.fillStyle = "#ffffff";
    ctx.font = `800 50px "${FONT_DISPLAY}"`;
    ctx.textBaseline = "middle";
    ctx.textAlign = "center";
    ctx.fillText("La visite", W / 2, 64);
    ctx.textAlign = "left";
    steps.forEach((s, i) => {
      const y = 170 + i * 78;
      ctx.beginPath();
      ctx.arc(64, y, 26, 0, Math.PI * 2);
      ctx.fillStyle = hex(C.sun);
      ctx.fill();
      ctx.fillStyle = "#ffffff";
      ctx.font = `800 32px "${FONT_DISPLAY}"`;
      ctx.textAlign = "center";
      ctx.fillText(String(i + 1), 64, y + 2);
      ctx.textAlign = "left";
      ctx.fillStyle = hex(C.ink);
      ctx.font = `700 38px "${FONT_TEXT}"`;
      ctx.fillText(s, 110, y + 2);
    });
  });
}
function appTex(stage = 0) {
  return canvasTex(400, 760, (ctx, W, H) => {
    ctx.fillStyle = "#f4f8fc";
    ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = hex(C.blue);
    ctx.fillRect(0, 0, W, 150);
    ctx.fillStyle = "#ffffff";
    ctx.font = `800 52px "${FONT_DISPLAY}"`;
    ctx.textBaseline = "middle";
    ctx.fillText("Ecole Plus", 30, 92);
    const rows = [
      ["Notes", C.sun, "chart"],
      ["Absences", C.coral, "calendar"],
      ["Messages", C.sky, "chat"],
      ["Emploi du temps", C.blue, "calendar"],
    ];
    rows.forEach(([label, col, ic], i) => {
      const y = 190 + i * 132;
      ctx.fillStyle = "#ffffff";
      roundRect(ctx, 22, y, W - 44, 112, 24);
      ctx.fill();
      ctx.beginPath();
      ctx.arc(80, y + 56, 34, 0, Math.PI * 2);
      ctx.fillStyle = hex(col);
      ctx.fill();
      ICONS[ic](ctx, 80, y + 56, 40, "#ffffff");
      ctx.fillStyle = hex(C.ink);
      ctx.font = `700 32px "${FONT_TEXT}"`;
      ctx.fillText(label, 132, y + 46);
      ctx.fillStyle = "#c9d8e6";
      roundRect(ctx, 132, y + 70, 150 + (i % 2) * 40, 14, 7);
      ctx.fill();
    });
  });
}
function checklistTex() {
  const items = ["Conditions d'admission", "Places disponibles", "Frais de scolarité", "Documents nécessaires", "Constitution du dossier"];
  const tex = canvasTex(560, 720, () => {});
  tex.userData.items = items;
  tex.userData.drawState = (checked) => {
    const ctx = tex.userData.ctx, W = 560, H = 720;
    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = "#ffffff";
    roundRect(ctx, 0, 0, W, H, 30);
    ctx.fill();
    ctx.fillStyle = hex(C.blue);
    ctx.font = `800 48px "${FONT_DISPLAY}"`;
    ctx.textBaseline = "middle";
    ctx.fillText("Inscription", 40, 74);
    ctx.fillStyle = hex(C.sun);
    ctx.fillRect(40, 112, 120, 8);
    items.forEach((it, i) => {
      const y = 190 + i * 104;
      ctx.lineWidth = 6;
      ctx.strokeStyle = hex(C.blue);
      roundRect(ctx, 40, y - 30, 60, 60, 14);
      ctx.stroke();
      if (i < checked) {
        ctx.fillStyle = hex(C.green);
        roundRect(ctx, 40, y - 30, 60, 60, 14);
        ctx.fill();
        ICONS.check(ctx, 70, y, 46, "#ffffff");
      }
      ctx.fillStyle = hex(C.ink);
      ctx.font = `700 34px "${FONT_TEXT}"`;
      ctx.fillText(it, 124, y + 2);
    });
    tex.needsUpdate = true;
  };
  tex.userData.drawState(0);
  return tex;
}
function paintingTex() {
  return canvasTex(256, 200, (ctx, W, H) => {
    ctx.fillStyle = "#fffaf0";
    ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = hex(C.sky);
    ctx.fillRect(0, 0, W, H * 0.6);
    ctx.fillStyle = hex(C.sun);
    ctx.beginPath();
    ctx.arc(W * 0.7, H * 0.3, 30, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = hex(C.leaf);
    ctx.beginPath();
    ctx.moveTo(0, H * 0.75);
    ctx.quadraticCurveTo(W * 0.4, H * 0.4, W, H * 0.7);
    ctx.lineTo(W, H);
    ctx.lineTo(0, H);
    ctx.fill();
  });
}
function sportTex() {
  const t = canvasTex(512, 512, (ctx, W, H) => {
    ctx.fillStyle = "#7fc39a";
    ctx.fillRect(0, 0, W, H);
    ctx.strokeStyle = "rgba(255,255,255,0.85)";
    ctx.lineWidth = 8;
    ctx.strokeRect(30, 30, W - 60, H - 60);
    ctx.beginPath();
    ctx.moveTo(W / 2, 30);
    ctx.lineTo(W / 2, H - 30);
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(W / 2, H / 2, 70, 0, Math.PI * 2);
    ctx.stroke();
  });
  return t;
}

// ── Station builders ────────────────────────────────────────────────────────
const FAMILY = {
  mom: () => person({ skin: 0xd8a07a, top: C.coral, bottom: 0x3f4a66, hairStyle: "scarf", scarf: C.sky, tunic: true }),
  kid: () => person({ skin: 0xd8a07a, top: C.sun, bottom: C.blue, kid: true, hairStyle: "pigtails", hair: 0x3a2618, backpack: C.blue, backpackPocket: C.sky, sleeves: "short", tie: C.coral }),
};
const STAFF = {
  receptionist: () => person({ skin: 0xe0b08a, top: C.blue, bottom: C.ink, hairStyle: "bun", hair: 0x3a2618, blazer: true }),
  director: () => person({ skin: 0xc98e66, top: C.deep, bottom: C.ink, hairStyle: "short", hair: 0x2a2018, blazer: true, glasses: true, beard: true }),
  teacher: () => person({ skin: 0xdcae86, top: C.leaf, bottom: C.ink, hairStyle: "scarf", scarf: 0xf3d36b, tunic: true }),
  advisor: () => person({ skin: 0xe4b892, top: C.blue, bottom: C.ink, hairStyle: "long", hair: 0x2c1d14, blazer: true, glasses: true }),
};
const KIDS = [
  { top: C.coral, bottom: C.blue, hairStyle: "short", hair: 0x2a1c12, skin: 0xc68a62 },
  { top: C.sky, bottom: C.ink, hairStyle: "ponytail", hair: 0x4a2f1c, skin: 0xe2b38c, tie: C.sun },
  { top: C.sun, bottom: C.deep, hairStyle: "short", hair: 0x1f1610, skin: 0xb9805a },
  { top: C.violet, bottom: C.ink, hairStyle: "pigtails", hair: 0x2f1f14, skin: 0xd9a47e, tie: C.sky },
  { top: C.green, bottom: C.blue, hairStyle: "short", hair: 0x3a2618, skin: 0xd09168 },
];
const kid = (i, extra = {}) => person({ kid: true, sleeves: "short", ...KIDS[i % KIDS.length], ...extra });

function place(g, P_, x, z, rotY = 0) {
  WORLD.people.push(P_);
  P_.root.position.set(x, F, z);
  P_.root.rotation.y = rotY;
  g.add(P_.root);
  return P_;
}
// facing helpers (character faces +Z by default)
const FACE = { px: Math.PI / 2, nx: -Math.PI / 2, pz: 0, nz: Math.PI };

function buildFacade(s) {
  const g = island(WORLD.root, s);
  const half = s.half;
  // pavement texture
  const pt = paveTex();
  pt.repeat.set(6, 1.4);
  const pave = panel(g, s.size - 0.4, 2.5, pt, 0, F + 0.012, 3.55);
  pave.rotation.x = -Math.PI / 2;
  // curb + street (as on the photo)
  rbox(g, s.size - 0.4, 0.12, 0.16, 0xd9d4ca, 0, F, 4.86, 0.03);
  const road = panel(g, s.size - 0.4, 1.1, roadTex(), 0, F + 0.008, 5.48);
  road.rotation.x = -Math.PI / 2;
  // garden inside the wall
  rbox(g, 11.2, 0.05, 6.6, C.lawn, -0.2, F - 0.02, -2.2, 0.02, { shadow: false });
  // entrance path
  const pt2 = paveTex();
  pt2.repeat.set(1, 2);
  const path = panel(g, 1.5, 3.2, pt2, -0.9, F + 0.06, 0.25);
  path.rotation.x = -Math.PI / 2;

  const fx = facadeTex();
  // left wing
  rbox(g, 3.9, 3.7, 4.4, C.facade, -3.6, F, -3.0, 0.05);
  panel(g, 3.9, 3.7, fx, -3.6, F + 1.85, -0.79);
  rbox(g, 4.1, 0.16, 4.6, C.white, -3.6, F + 3.7, -3.0, 0.04);
  // logo plaque + cycles strip on the left wing
  const lp = panel(g, 3.3, 0.83, facadeSignTex(WORLD.logoTex.image), -3.55, F + 2.85, -0.765, { transparent: true });
  lp.receiveShadow = false;
  panel(g, 3.2, 0.36, textPlate("Maternelle - Primaire - Collège - Lycée", { px: 70, color: hex(C.sunDeep), font: FONT_TEXT, weight: 700, w: 1400, h: 120 }), -3.6, F + 2.28, -0.765, { transparent: true });
  // vertical window strip
  panel(g, 0.42, 2.8, glassTex(), -1.95, F + 1.6, -0.775);
  // glass atrium
  const gt = glassTex();
  rbox(g, 2.6, 4.5, 3.6, C.glass, -0.35, F, -2.75, 0.02);
  panel(g, 2.6, 4.5, gt, -0.35, F + 2.25, -0.94);
  const side = panel(g, 3.6, 4.5, glassTex(), 0.96, F + 2.25, -2.75);
  side.rotation.y = Math.PI / 2;
  rbox(g, 3.2, 0.22, 4.2, C.white, -0.35, F + 4.5, -2.75, 0.04);
  rbox(g, 3.0, 0.14, 1.2, C.white, -0.35, F + 2.6, -0.5, 0.03); // canopy over the door
  // door
  box(g, 1.1, 1.9, 0.04, 0x5c7898, -0.35, F, -0.92, { emissive: C.sun, emissiveIntensity: 0.0 });
  s.atriumDoor = box(g, 1.0, 1.8, 0.03, C.sun, -0.35, F, -0.9, { basic: true, transparent: true, opacity: 0.0, shadow: false });
  // right wing
  rbox(g, 3.2, 3.4, 3.8, C.facade, 2.6, F, -3.3, 0.05);
  rbox(g, 3.4, 0.16, 4.0, C.white, 2.6, F + 3.4, -3.3, 0.04);
  for (let i = 0; i < 3; i++) panel(g, 0.42, 2.4, glassTex(), 1.7 + i * 0.9, F + 1.7, -1.39);
  for (let i = 0; i < 3; i++) {
    const w = panel(g, 0.42, 2.4, glassTex(), 4.21, F + 1.7, -4.6 + i * 0.9);
    w.rotation.y = Math.PI / 2;
  }
  // upper block + flag
  rbox(g, 3.6, 1.1, 2.8, C.facadeDark, -1.3, F + 3.86, -3.8, 0.04);
  cyl(g, 0.03, 0.03, 1.5, C.metal, -1.6, F + 4.96, -3.4);
  const flag = panel(g, 0.72, 0.48, flagTex(), -1.22, F + 6.15, -3.4, {});
  flag.material.side = THREE.DoubleSide;
  s.flag = flag;
  // entrance canopy (right) with the school name
  const cx = 4.4, cz = 0.7;
  [-0.9, 0.9].forEach((dz) => rbox(g, 0.28, 2.3, 0.28, C.facade, cx - 0.6, F, cz + dz, 0.04));
  rbox(g, 2.6, 0.3, 2.6, C.facade, cx, F + 2.3, cz, 0.06);
  panel(g, 2.4, 0.22, textPlate("Maternelle - Primaire - Collège - Lycée", { px: 70, color: hex(C.sunDeep), font: FONT_TEXT, weight: 700, w: 1400, h: 120 }), cx, F + 2.45, cz + 1.306, { transparent: true });
  const sign = panel(g, 2.9, 0.52, schoolSignTex(), cx, F + 2.92, cz + 1.31, { transparent: true });
  sign.receiveShadow = false;
  // perimeter wall (mustard) with steel grille + gates
  const gr = grilleTex();
  const wallZ = 1.95;
  const segs = [[-half + 0.3, -1.7], [-0.1, 3.0]];
  segs.forEach(([a, b]) => {
    rbox(g, b - a, 0.95, 0.32, C.mustard, (a + b) / 2, F, wallZ, 0.04);
    const gp = panel(g, b - a - 0.1, 0.55, gr, (a + b) / 2, F + 1.25, wallZ, {});
    gp.material.side = THREE.DoubleSide;
  });
  rbox(g, 0.36, 1.6, 0.36, C.mustard, -1.75, F, wallZ, 0.04);
  rbox(g, 0.36, 1.6, 0.36, C.mustard, -0.05, F, wallZ, 0.04);
  // gate leaves (animated open), hinged on the posts
  s.gates = [-1, 1].map((sd) => {
    const hinge = group(g, sd < 0 ? -1.57 : -0.23, F, wallZ);
    const leaf = panel(hinge, 0.7, 1.4, gr, sd < 0 ? 0.35 : -0.35, 0.72, 0, {});
    leaf.material.side = THREE.DoubleSide;
    return hinge;
  });
  // greenery
  P.palm(g, 1.75, 0.35, 1.45, 4);
  P.palm(g, -5.0, 0.9, 1.0, 5);
  P.palm(g, 5.2, -2.2, 1.15, 6);
  P.palm(g, 3.9, -1.6, 0.95, 9);
  [-4.2, -3.0, 0.9, 2.4].forEach((x, i) => P.bush(g, x, 1.35, 0.75 + (i % 2) * 0.15));
  P.bush(g, 4.9, 1.9, 0.7);
  // street lamp + bench on the sidewalk
  P.lamp(g, -4.6, 4.55, 2.2);

  // family arrives on the sidewalk
  s.mom = place(g, FAMILY.mom(), 4.6, 4.1, FACE.nx);
  s.kid = place(g, FAMILY.kid(), 4.9, 3.5, FACE.nx);
  s.entryPt = new THREE.Vector3(5.6, F, 3.8);
  s.exitPt = new THREE.Vector3(-0.35, F + 4.7, -2.75); // from the atrium roof up to S1
}

function buildAccueil(s) {
  const g = island(WORLD.root, s);
  const half = s.half;
  backWalls(g, s, { doorU: 2.2, band: C.blue });
  // terrazzo inlay + rug
  P.rug(g, 0.6, 0.4, 3.6, 2.6, 0xdcebf6);
  P.rug(g, 0.6, 0.4, 3.2, 2.2, 0xf7e7c2);
  // logo + sign on the -z wall
  const lp = P.wallPanel(g, "z", half, -1.4, F + 1.55, 1.5, 1.3, WORLD.logoTex, { transparent: true });
  lp.receiveShadow = false;
  P.wallPanel(g, "z", half, 1.6, F + 1.85, 2.2, 0.5, textPlate("Accueil", { px: 130, color: hex(C.blue), w: 700, h: 200 }), { transparent: true });
  P.window_(g, "x", half, -1.4, F + 1.4, 1.5, 1.2);
  P.clock(g, "x", half, 0.2, F + 1.9);
  // reception desk
  const d = group(g, 0.9, F, -2.5);
  rbox(d, 3.4, 1.05, 0.8, C.white, 0, 0, 0, 0.12);
  rbox(d, 3.42, 0.32, 0.82, C.blue, 0, 0.12, 0.0, 0.1);
  rbox(d, 3.5, 0.08, 0.9, C.sun, 0, 1.02, 0, 0.03, { emissive: C.sun, emissiveIntensity: 0.25 });
  P.monitor(d, -0.8, 1.1, -0.1, Math.PI, null);
  P.plant(d, 1.4, 0.05, 0.45).position.y = 1.1;
  s.receptionist = place(g, STAFF.receptionist(), 0.4, -3.4, FACE.pz);
  // visit plan board on a stand
  const st = group(g, -2.6, F, -2.0);
  st.rotation.y = Math.PI / 4;
  box(st, 0.06, 1.0, 0.06, C.dark, 0, 0, 0);
  rbox(st, 0.6, 0.04, 0.4, C.dark, 0, 0, 0, 0.02);
  s.planBoard = panel(st, 1.1, 1.55, planBoardTex(), 0, 1.65, 0.05, { transparent: true });
  // waiting area
  P.sofa(g, -3.3, -0.2, FACE.px, C.sky, 1.9);
  rbox(g, 0.8, 0.4, 0.8, C.wood, -2.2, F, -0.2, 0.08);
  P.plant(g, -3.8, -3.8, 1.0);
  P.plant(g, 3.8, -3.8, 0.9);
  P.plant(g, -3.6, 3.7, 0.8);
  // family at the desk
  s.mom = place(g, FAMILY.mom(), 1.3, -1.1, FACE.nz + 0.25);
  s.kid = place(g, FAMILY.kid(), 0.4, -0.9, FACE.nz - 0.2);
  s.entryPt = edgePoint(s, "z", 1);
  s.exitPt = new THREE.Vector3(-half + 0.1, F + 0.05, 2.2);
}

function buildPresentation(s) {
  const g = island(WORLD.root, s);
  const half = s.half;
  backWalls(g, s, { doorU: -2.6, band: C.sky });
  // big screen on the -z wall
  P.frameBox(g, "z", half, 0.9, F + 1.4, 3.9, 2.25, C.dark, 0.08);
  s.screen = P.wallPanel(g, "z", half, 0.9, F + 1.4, 3.7, 2.08, slideTex(), { glow: 0.65 });
  s.screen.position.z += 0.07;
  P.bookshelf(g, -half + 0.4, -1.0, FACE.px, 1.8, 1.9);
  P.plant(g, -3.8, 3.6, 0.9);
  P.plant(g, 3.7, -3.6, 0.8);
  // round table with the cycles tower model
  const tb = group(g, 0.2, F, -0.3);
  cyl(tb, 1.25, 1.25, 0.08, C.woodLight, 0, 0.72, 0, { seg: 32 });
  cyl(tb, 0.12, 0.2, 0.72, C.metal, 0, 0, 0);
  const tower = group(tb, 0, 0.8, 0);
  const cyc = [C.maternelle, C.primaire, C.college, C.lycee];
  s.towerFloors = cyc.map((col, i) => {
    const fl = group(tower, 0, i * 0.34, 0);
    rbox(fl, 0.9, 0.3, 0.9, col, 0, 0, 0, 0.05, { material: ownMat(col, { emissive: col, emissiveIntensity: 0.0 }) });
    box(fl, 0.92, 0.07, 0.92, C.white, 0, 0.12, 0, { shadow: false });
    return fl;
  });
  s.tower = tower;
  // presenter
  s.director = place(g, STAFF.director(), 2.7, -2.9, FACE.pz - 0.5);
  // family on chairs facing the screen
  P.chair(g, 1.5, 1.55, FACE.nz, C.blue);
  P.chair(g, 0.2, 1.75, FACE.nz, C.blue);
  s.mom = place(g, FAMILY.mom(), 1.5, 1.55, FACE.nz);
  s.kid = place(g, FAMILY.kid(), 0.2, 1.75, FACE.nz);
  // cycle labels
  s.cycleLabels = ["Maternelle", "Primaire", "Collège", "Lycée"].map((n, i) => {
    const sp = pillSprite(n, { height: 0.42, bg: "#ffffff", fg: hex(C.deep), dot: hex(cyc[i]), px: 64 });
    sp.position.set(s.pos.x + 0.2 - 1.6, s.pos.y + F + 0.95 + i * 0.36, s.pos.z - 0.3 + 1.6);
    WORLD.root.add(sp);
    return sp;
  });
  s.entryPt = edgePoint(s, "x", 1);
  s.exitPt = new THREE.Vector3(-2.6, F + 0.05, -half + 0.1);
}

function buildInfra(s) {
  const g = island(WORLD.root, s);
  const half = s.half;
  backWalls(g, s, { doorU: 0.9, band: C.blue });
  // interior dividers (low, so the camera reads every room)
  rbox(g, 0.16, 1.3, half - 0.6, C.white, 0.0, F, -half / 2 - 0.3, 0.04);
  rbox(g, half - 0.6, 1.3, 0.16, C.white, -half / 2 - 0.3, F, 0.0, 0.04);
  box(g, 0.18, 0.06, half - 0.6, C.sun, 0.0, F + 1.3, -half / 2 - 0.3, { shadow: false });
  box(g, half - 0.6, 0.06, 0.18, C.sun, -half / 2 - 0.3, F + 1.3, 0.0, { shadow: false });
  const zones = {};

  // A — classroom (back)
  const A = group(g, -2.9, 0, -2.9);
  P.blackboard(g, "z", half, -2.9, F + 1.55, 2.6, 1.3);
  for (let r = 0; r < 2; r++)
    for (let c = 0; c < 2; c++) {
      P.desk(A, -0.9 + c * 1.6, 0.0 + r * 1.3, 1.1, 0.55, C.woodLight);
      P.chair(A, -0.9 + c * 1.6, 0.45 + r * 1.3, FACE.nz, [C.sky, C.sun, C.coral, C.blue][r * 2 + c]);
    }
  const kA = place(A, kid(0), -0.9, 0.45, FACE.nz);
  const kB = place(A, kid(1), 0.7, 1.75, FACE.nz);
  kA.rest = kB.rest = { sit: 1 };
  zones.classe = { center: new THREE.Vector3(-2.9, 1.0, -2.9), kids: [kA, kB] };

  // B — science lab (right)
  const B = group(g, 2.9, 0, -2.9);
  rbox(B, 2.4, 0.9, 0.9, C.white, 0, F, 0.3, 0.06);
  rbox(B, 2.5, 0.08, 1.0, C.ink, 0, F + 0.9, 0.3, 0.03);
  P.flask(B, -0.8, F + 0.98, 0.3, C.sky);
  P.flask(B, -0.4, F + 0.98, 0.15, C.coral, 0.8);
  P.flask(B, 0.0, F + 0.98, 0.4, C.green, 0.9);
  P.microscope(B, 0.7, F + 0.98, 0.3, -0.5);
  for (let i = 0; i < 4; i++) P.tube(B, -0.9 + i * 0.12, F + 0.98, 0.65, [C.sun, C.sky, C.coral, C.violet][i]);
  rbox(B, 1.8, 1.9, 0.5, C.white, 0.6, F, -1.55, 0.05);
  [0.6, 1.2].forEach((y) => box(B, 1.7, 0.03, 0.46, 0xd9e3ea, 0.6, F + y, -1.52));
  for (let i = 0; i < 5; i++) P.flask(B, -0.1 + i * 0.32, F + 1.23, -1.52, [C.sky, C.green, C.sun, C.coral, C.violet][i], 0.6);
  const kC = place(B, kid(2, {}), -0.3, 1.25, FACE.nz);
  zones.labo = { center: new THREE.Vector3(2.9, 1.0, -2.9), kids: [kC] };

  // C — computer room (left)
  const Cz = group(g, -2.9, 0, 2.9);
  for (let i = 0; i < 2; i++) {
    const row = group(Cz, -1.5 + i * 1.9, 0, 0);
    P.desk(row, 0, 0.4, 0.7, 2.6, C.white, 0);
    for (let j = 0; j < 3; j++) P.monitor(row, -0.05, F + 0.74, -0.6 + j * 0.85, FACE.px, WORLD.screenTex);
  }
  P.chair(Cz, -0.85, 0.25, FACE.nx, C.sun);
  const kD = place(Cz, kid(3), -0.85, 0.25, FACE.nx);
  kD.rest = { sit: 1 };
  zones.info = { center: new THREE.Vector3(-2.9, 1.0, 2.9), kids: [kD] };

  // D — playground (front, open air)
  const D = group(g, 2.9, 0, 2.9);
  const sp = panel(D, 5.0, 5.0, sportTex(), 0, F + 0.02, 0);
  sp.rotation.x = -Math.PI / 2;
  P.basketHoop(D, 1.9, -1.6, -Math.PI / 4);
  P.tree(D, -1.7, 1.7, 1.0);
  P.bench(D, 1.6, 1.9, FACE.nz + Math.PI, C.sun);
  const kE = place(D, kid(4), -0.3, 0.2, FACE.px - 0.6);
  const kF = place(D, kid(0, { top: C.blue, hairStyle: "ponytail", tie: C.sun }), 0.8, -0.6, FACE.nx + 0.4);
  s.ball = P.ball(D, 0.25, F, -0.2, 0.14, C.coral);
  zones.cour = { center: new THREE.Vector3(2.9, 0.8, 2.9), kids: [kE, kF] };

  // common space: lockers along the divider + a small admin office corner
  P.lockers(g, 0.35, -1.3, FACE.px, 3);
  P.plant(g, 0.6, 0.6, 0.7);
  zones.communs = { center: new THREE.Vector3(0, 1.0, 0) };
  s.zones = zones;
  // zone labels (world sprites)
  const labels = [["Salles de classe", zones.classe], ["Laboratoires", zones.labo], ["Salle informatique", zones.info], ["Cour de récréation", zones.cour], ["Espaces communs", zones.communs]];
  s.zoneLabels = labels.map(([txt, z], i) => {
    const spr = pillSprite(txt, { height: 0.5, bg: hex(C.blue), fg: "#ffffff", px: 64, dot: hex(C.sun) });
    spr.position.copy(z.center).add(s.pos).add(new THREE.Vector3(0, i === 4 ? 1.6 : 1.9, 0));
    WORLD.root.add(spr);
    return spr;
  });
  // family (visitors)
  s.mom = place(g, FAMILY.mom(), 1.2, 0.9, FACE.nz + 0.8);
  s.kid = place(g, FAMILY.kid(), 0.5, 1.4, FACE.nz + 0.8);
  s.entryPt = edgePoint(s, "z", 1);
  s.exitPt = new THREE.Vector3(-half + 0.1, F + 0.05, 0.9);
}

function buildOrganisation(s) {
  const g = island(WORLD.root, s);
  const half = s.half;
  backWalls(g, s, { doorU: 3.0, band: C.sky });
  // smart board
  P.frameBox(g, "z", half, -0.6, F + 1.4, 3.0, 1.6, C.dark, 0.06);
  s.board = P.wallPanel(g, "z", half, -0.6, F + 1.4, 2.85, 1.48, WORLD.lessonTex, { glow: 0.5 });
  s.board.position.z += 0.06;
  P.window_(g, "x", half, -1.6, F + 1.45, 1.4, 1.1);
  P.window_(g, "x", half, 0.4, F + 1.45, 1.4, 1.1);
  P.bookshelf(g, -half + 0.4, 2.6, FACE.px, 1.4, 1.5);
  // teacher desk
  P.desk(g, 1.9, -2.6, 1.4, 0.7, C.wood);
  s.teacher = place(g, STAFF.teacher(), 0.9, -3.3, FACE.pz + 0.35);
  // pupils
  s.pupils = [];
  for (let r = 0; r < 2; r++)
    for (let c = 0; c < 3; c++) {
      const x = -2.0 + c * 1.7, z = -0.9 + r * 1.6;
      P.desk(g, x, z, 1.0, 0.55, C.woodLight);
      P.chair(g, x, z + 0.45, FACE.nz, [C.sky, C.sun, C.coral][c]);
      if ((r + c) % 3 !== 2) {
        const k = place(g, kid(r * 3 + c), x, z + 0.45, FACE.nz);
        k.rest = { sit: 1 };
        s.pupils.push(k);
      }
    }
  P.plant(g, 3.8, 3.6, 0.85);
  // the four pillars as orbiting badges
  const items = [["bulb", C.sun, "Méthodes"], ["chart", C.sky, "Suivi & évaluation"], ["shield", C.blue, "Encadrement"], ["chat", C.coral, "École ↔ parents"]];
  s.badges = items.map(([ic, col]) => {
    const b = badgeSprite(ic, hex(col), 1.05);
    WORLD.root.add(b);
    return b;
  });
  s.entryPt = edgePoint(s, "x", 1);
  s.exitPt = new THREE.Vector3(3.0, F + 0.05, -half + 0.1);
}

function buildServices(s) {
  const g = island(WORLD.root, s);
  const half = s.half;
  backWalls(g, s, { doorU: 2.4, band: C.blue });
  // giant phone (Ecole Plus)
  const ph = group(g, -0.6, F, -1.4);
  ph.rotation.y = Math.PI / 4;
  rbox(ph, 2.3, 4.3, 0.3, C.ink, 0, 0, 0, 0.28);
  s.app = panel(ph, 2.05, 3.9, WORLD.appTex, 0, 2.17, 0.16, { glow: 0.55 });
  rbox(ph, 0.6, 0.08, 0.05, 0x111418, 0, 4.05, 0.15, 0.03);
  rbox(ph, 1.4, 0.2, 0.9, C.white, 0, -0.02, 0.2, 0.08);
  s.phone = ph;
  // notification bubbles
  s.notifs = [["chart", C.sun], ["calendar", C.coral], ["chat", C.sky]].map(([ic, col]) => {
    const b = badgeSprite(ic, hex(col), 0.85);
    WORLD.root.add(b);
    return b;
  });
  // activities corner
  P.goal(g, 2.6, 2.9, -Math.PI / 4);
  s.ball = P.ball(g, 1.9, F, 2.0, 0.17, C.sun);
  P.easel(g, -3.0, 2.2, Math.PI / 4 + 0.2, paintingTex());
  // music: a small keyboard
  const kb = group(g, -2.7, F, 0.0);
  kb.rotation.y = FACE.px;
  rbox(kb, 1.3, 0.12, 0.42, C.dark, 0, 0.72, 0, 0.03);
  box(kb, 1.2, 0.03, 0.22, C.white, 0, 0.84, 0.06);
  [-0.5, 0.5].forEach((x) => box(kb, 0.05, 0.72, 0.05, C.metal, x, 0, 0));
  P.plant(g, 3.8, -3.7, 0.9);
  P.plant(g, -3.8, -3.6, 0.8);
  // activity labels
  s.actLabels = [["Sport", new THREE.Vector3(2.6, 1.5, 2.9)], ["Arts", new THREE.Vector3(-3.0, 2.1, 2.2)], ["Musique", new THREE.Vector3(-2.7, 1.5, 0.0)]].map(([t, p]) => {
    const spr = pillSprite(t, { height: 0.4, bg: "#ffffff", fg: hex(C.deep), px: 60, dot: hex(C.sun) });
    spr.position.copy(p).add(s.pos);
    WORLD.root.add(spr);
    return spr;
  });
  s.mom = place(g, FAMILY.mom(), 1.6, 0.4, FACE.nx - 0.6);
  s.kid = place(g, FAMILY.kid(), 1.7, 1.6, FACE.nz + 0.7);
  s.entryPt = edgePoint(s, "z", 1);
  s.exitPt = new THREE.Vector3(-half + 0.1, F + 0.05, 2.4);
}

function buildModalites(s) {
  const g = island(WORLD.root, s);
  const half = s.half;
  backWalls(g, s, { doorU: 2.3, band: C.blue });
  P.window_(g, "z", half, -1.6, F + 1.45, 1.4, 1.1);
  P.bookshelf(g, -half + 0.4, -2.4, FACE.px, 1.8, 1.9);
  // advisor desk
  const d = group(g, 0.3, F, -1.9);
  rbox(d, 2.4, 0.08, 1.1, C.wood, 0, 0.72, 0, 0.03);
  rbox(d, 2.3, 0.62, 0.08, C.wood, 0, 0.1, -0.5, 0.02);
  [-1, 1].forEach((sx) => rbox(d, 0.08, 0.72, 1.05, C.wood, sx * 1.12, 0, 0, 0.02));
  P.monitor(d, 0.7, 0.8, -0.3, -0.4, WORLD.screenTex);
  // blue folder + documents
  const fold = group(d, -0.3, 0.8, 0.1);
  rbox(fold, 0.7, 0.05, 0.5, C.blue, 0, 0, 0, 0.02);
  s.folder = fold;
  s.docs = [0, 1, 2, 3].map((i) => {
    const doc = group(WORLD.root);
    rbox(doc, 0.5, 0.012, 0.66, 0xffffff, 0, 0, 0, 0.005);
    box(doc, 0.3, 0.004, 0.04, C.sky, -0.05, 0.012, -0.2, { shadow: false });
    box(doc, 0.36, 0.004, 0.03, 0xcfdbe6, 0, 0.012, -0.08, { shadow: false });
    box(doc, 0.36, 0.004, 0.03, 0xcfdbe6, 0, 0.012, 0.02, { shadow: false });
    return doc;
  });
  s.advisor = place(g, STAFF.advisor(), 0.3, -2.9, FACE.pz);
  P.chair(g, 0.3, -3.0, 0, C.ink);
  // checklist board
  const st = group(g, -2.5, F, -0.6);
  st.rotation.y = Math.PI / 4;
  box(st, 0.06, 0.9, 0.06, C.dark, 0, 0, 0);
  rbox(st, 0.6, 0.04, 0.4, C.dark, 0, 0, 0, 0.02);
  s.checklist = WORLD.checklistTex;
  panel(st, 1.4, 1.8, s.checklist, 0, 1.75, 0.05, { transparent: true });
  // family seated in front of the desk
  P.chair(g, 0.9, -0.85, FACE.nz, C.sky);
  P.chair(g, -0.3, -0.75, FACE.nz, C.sky);
  s.mom = place(g, FAMILY.mom(), 0.9, -0.85, FACE.nz);
  s.kid = place(g, FAMILY.kid(), -0.3, -0.75, FACE.nz);
  P.plant(g, 3.8, 3.6, 0.9);
  P.plant(g, -3.8, 3.6, 0.8);
  s.entryPt = edgePoint(s, "x", 1);
  s.exitPt = new THREE.Vector3(2.3, F + 0.05, -half + 0.1);
}

function buildConclusion(s) {
  const g = island(WORLD.root, s);
  const half = s.half;
  // garden terrace: path, flowerbeds, arch
  const pt = paveTex();
  pt.repeat.set(1, 3);
  const path = panel(g, 1.6, s.size - 0.6, pt, 0.0, F + 0.04, 0);
  path.rotation.x = -Math.PI / 2;
  // welcome arch
  const arch = group(g, 0.0, F, -2.6);
  [-1.25, 1.25].forEach((x) => rbox(arch, 0.32, 2.7, 0.32, C.blue, x, 0, 0, 0.08));
  rbox(arch, 3.0, 0.32, 0.4, C.blue, 0, 2.7, 0, 0.08);
  const ban = panel(arch, 2.8, 0.62, textPlate("Bienvenue à EN-NOUR 3", { px: 104, color: "#ffffff", w: 1500, h: 220, stroke: hex(C.sunDeep) }), 0, 2.45, 0.22, { transparent: true });
  ban.receiveShadow = false;
  rbox(arch, 2.6, 0.48, 0.06, C.sun, 0, 2.2, 0.17, 0.06);
  s.arch = arch;
  // balloons
  s.balloons = [[-1.6, -2.4, C.sun], [-1.9, -2.0, C.sky], [1.6, -2.4, C.blue], [1.9, -2.1, C.sun], [-1.5, -1.9, C.coral]].map(([x, z, c]) =>
    P.balloon(g, x, F + 1.6, z, c)
  );
  // trees, bushes, benches
  P.tree(g, -3.4, -3.0, 1.15);
  P.tree(g, 3.3, -3.4, 1.05);
  P.palm(g, -3.6, 2.8, 0.9, 12);
  [[-2.4, 0.6], [2.5, 0.8], [-2.5, 3.6], [2.8, 3.4]].forEach(([x, z], i) => P.bush(g, x, z, 0.75, i % 2 ? C.leaf : 0x6cbf83));
  P.bench(g, 3.2, 1.6, FACE.nx, C.wood);
  // flowers
  const R = rng(21);
  for (let i = 0; i < 26; i++) {
    const x = (R() - 0.5) * 7.4, z = (R() - 0.5) * 7.4;
    if (Math.abs(x) < 1.1) continue;
    sph(g, 0.09, [C.sun, C.coral, C.pink, 0xffffff][i % 4], x, F + 0.12, z, { ws: 8, hs: 6 });
  }
  // people: advisor + mom shake hands, kid cheers
  s.advisor = place(g, STAFF.director(), -0.45, -0.6, FACE.px - 0.25);
  s.mom = place(g, FAMILY.mom(), 0.45, -0.45, FACE.nx + 0.25);
  s.kid = place(g, FAMILY.kid(), 0.9, 0.7, FACE.nz + 0.6);
  // conclusion bubbles
  s.bubbles = [iconBubble("question", hex(C.blue), 0.85), iconBubble("check", hex(C.green), 0.85), iconBubble("heart", hex(C.coral), 0.85)];
  s.bubbles.forEach((b) => WORLD.root.add(b));
  s.entryPt = edgePoint(s, "z", 1);
}

// ── Light path (bridges between islands) ────────────────────────────────────
function buildBridges() {
  WORLD.bridges = [];
  for (let i = 0; i < STATIONS.length - 1; i++) {
    const a = STATIONS[i], b = STATIONS[i + 1];
    const p0 = a.exitPt.clone().add(a.pos);
    const p3 = b.entryPt.clone().add(b.pos);
    const mid = p0.clone().lerp(p3, 0.5);
    const lift = 1.6 + p0.distanceTo(p3) * 0.08;
    const p1 = p0.clone().lerp(mid, 0.6).add(new THREE.Vector3(0, lift, 0));
    const p2 = p3.clone().lerp(mid, 0.6).add(new THREE.Vector3(0, lift * 0.8, 0));
    const curve = new THREE.CatmullRomCurve3([p0, p1, p2, p3], false, "centripetal");
    const ghost = new THREE.Mesh(new THREE.TubeGeometry(curve, 90, 0.035, 6, false), new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.55, depthWrite: false }));
    const geo = new THREE.TubeGeometry(curve, 90, 0.075, 8, false);
    const core = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: 0xffd76a }));
    const haloGeo = new THREE.TubeGeometry(curve, 90, 0.22, 8, false);
    const halo = new THREE.Mesh(haloGeo, new THREE.MeshBasicMaterial({ color: C.sun, transparent: true, opacity: 0.3, depthWrite: false, blending: THREE.AdditiveBlending }));
    WORLD.root.add(ghost, core, halo);
    WORLD.bridges.push({ curve, core, halo, total: geo.index.count, totalHalo: haloGeo.index.count });
  }
}

// ── Sky: sun, clouds, sparkles ──────────────────────────────────────────────
function buildSky() {
  const top = STATIONS[STATIONS.length - 1];
  const sunPos = top.pos.clone().add(new THREE.Vector3(-3.5, 9.5, -3.5));
  const sun = group(WORLD.root, sunPos.x, sunPos.y, sunPos.z);
  sph(sun, 2.0, C.sun, 0, 0, 0, { basic: true, shadow: false, ws: 32, hs: 24 });
  const rays = canvasTex(512, 512, (ctx, W, H) => {
    ctx.translate(W / 2, H / 2);
    ctx.fillStyle = hex(C.sun);
    const n = 16;
    for (let i = 0; i < n; i++) {
      const a = (i / n) * Math.PI * 2;
      const len = i % 2 ? 190 : 250;
      ctx.save();
      ctx.rotate(a);
      ctx.beginPath();
      ctx.moveTo(-14, -140);
      ctx.lineTo(0, -len);
      ctx.lineTo(14, -140);
      ctx.closePath();
      ctx.fill();
      ctx.restore();
    }
  });
  const raySpr = new THREE.Sprite(new THREE.SpriteMaterial({ map: rays, transparent: true, depthWrite: false }));
  raySpr.scale.set(8.4, 8.4, 1);
  sun.add(raySpr);
  const glow = glowSprite(0xffd36b, 13, 0.55);
  sun.add(glow);
  WORLD.sun = { group: sun, rays: raySpr, glow };

  // guide orb (a little sun) that leads the visit
  const orb = group(WORLD.root);
  sph(orb, 0.2, 0xffe08a, 0, 0, 0, { basic: true, shadow: false });
  const og = glowSprite(C.sun, 1.6, 0.95);
  orb.add(og);
  WORLD.orb = { group: orb, glow: og };

  // clouds
  const R = rng(5);
  WORLD.clouds = [];
  STATIONS.forEach((s, i) => {
    const side = i % 2 ? 1 : -1;
    const c1 = P.cloud(WORLD.root, s.pos.x + side * 9 + R() * 3, s.pos.y - 3 + R() * 2, s.pos.z - side * 6, 1.3 + R() * 0.8, 10 + i);
    const c2 = P.cloud(WORLD.root, s.pos.x - side * 7, s.pos.y + 1 + R() * 2, s.pos.z + side * 9, 1.0 + R() * 0.6, 30 + i);
    WORLD.clouds.push(c1, c2);
  });
  // sparkles
  const sparkGeo = new THREE.BufferGeometry();
  const pts = [];
  STATIONS.forEach((s) => {
    for (let k = 0; k < 14; k++) pts.push(s.pos.x + (R() - 0.5) * 16, s.pos.y + R() * 7, s.pos.z + (R() - 0.5) * 16);
  });
  sparkGeo.setAttribute("position", new THREE.Float32BufferAttribute(pts, 3));
  const spark = new THREE.Points(sparkGeo, new THREE.PointsMaterial({ color: 0xffd36b, size: 5, sizeAttenuation: false, transparent: true, opacity: 0.8, depthWrite: false }));
  WORLD.root.add(spark);
  WORLD.sparkles = spark;
}

// ── Extra animated sprites ──────────────────────────────────────────────────
function buildExtras() {
  const add = (o) => (WORLD.root.add(o), o);
  WORLD.hello = add(pillSprite("Bienvenue !", { height: 0.62, bg: "#ffffff", fg: hex(C.blue), px: 76, dot: hex(C.sun) }));
  const cyc = [["Maternelle", C.maternelle], ["Primaire", C.primaire], ["Collège", C.college], ["Lycée", C.lycee]];
  WORLD.levelChips = cyc.map(([n, c]) => add(pillSprite(n, { height: 0.5, bg: "#ffffff", fg: hex(C.deep), px: 64, dot: hex(c), border: n === "Primaire" ? hex(C.sun) : null })));
  const s1 = STATIONS[1];
  WORLD.planGlow = add(glowSprite(0xffe6a0, 3.2, 0));
  WORLD.planGlow.position.copy(s1.pos).add(new THREE.Vector3(-2.55, 1.7, -1.9));
  const s5 = STATIONS[5];
  WORLD.appGlow = add(glowSprite(0xbfe6ff, 5.5, 0));
  WORLD.appGlow.position.copy(s5.pos).add(new THREE.Vector3(-0.5, 2.3, -1.3));
  WORLD.doneCard = add(pillSprite("Inscription finalisée", { height: 0.62, bg: hex(C.green), fg: "#ffffff", px: 72, dot: "#ffffff" }));
  // confetti burst (positions driven per frame)
  const R = rng(99);
  const n = 140;
  const geo = new THREE.BufferGeometry();
  const pos = new Float32Array(n * 3), col = new Float32Array(n * 3);
  const palette = [C.sun, C.blue, C.sky, C.coral, 0xffffff].map((c) => new THREE.Color(c));
  const vel = [];
  for (let i = 0; i < n; i++) {
    const a = R() * Math.PI * 2, sp = 0.6 + R() * 1.6;
    vel.push([Math.cos(a) * sp, 2.0 + R() * 2.4, Math.sin(a) * sp]);
    const c = palette[i % palette.length];
    col.set([c.r, c.g, c.b], i * 3);
  }
  geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  geo.setAttribute("color", new THREE.BufferAttribute(col, 3));
  WORLD.confetti = new THREE.Points(geo, new THREE.PointsMaterial({ size: 11, sizeAttenuation: false, vertexColors: true, transparent: true, depthWrite: false }));
  WORLD.confetti.userData.vel = vel;
  WORLD.confetti.frustumCulled = false;
  WORLD.confetti.visible = false;
  WORLD.root.add(WORLD.confetti);
  // hide every animated sprite until the film reveals it
  [WORLD.hello, ...WORLD.levelChips, WORLD.doneCard].forEach((o) => (o.visible = false));
  WORLD.clouds.forEach((c) => (c.userData.x0 = c.position.x));
}

// ── Public ──────────────────────────────────────────────────────────────────
export const WORLD = { root: null, stations: STATIONS, people: [] };

export async function buildWorld(scene) {
  WORLD.root = new THREE.Group();
  scene.add(WORLD.root);
  WORLD.logoTex = await new THREE.TextureLoader().loadAsync("assets/brand/logo-en-nour-3.png");
  WORLD.logoTex.colorSpace = THREE.SRGBColorSpace;
  WORLD.logoTex.anisotropy = 4;
  WORLD.screenTex = P.laptopScreenTex(C.blue);
  WORLD.lessonTex = canvasTex(640, 340, (ctx, W, H) => {
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = hex(C.sky);
    ctx.fillRect(0, 0, W, 64);
    ctx.font = `800 40px "${FONT_DISPLAY}"`;
    ctx.fillStyle = "#ffffff";
    ctx.textBaseline = "middle";
    ctx.fillText("Sciences · Leçon 4", 24, 34);
    ICONS.bulb(ctx, 110, 190, 150, hex(C.sun));
    ICONS.chart(ctx, 320, 200, 170, hex(C.blue));
    ICONS.star(ctx, 520, 190, 150, hex(C.coral));
  });
  WORLD.appTex = appTex();
  WORLD.checklistTex = checklistTex();
  const builders = [buildFacade, buildAccueil, buildPresentation, buildInfra, buildOrganisation, buildServices, buildModalites, buildConclusion];
  STATIONS.forEach((s, i) => builders[i](s));
  buildBridges();
  buildSky();
  buildExtras();
  return WORLD;
}
