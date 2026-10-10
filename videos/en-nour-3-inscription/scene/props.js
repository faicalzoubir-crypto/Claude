// Furniture and props for the isometric stations. Each builder adds to `parent`
// at local (x, z) on the floor (y = floor height) and returns its group.
import * as THREE from "three";
import { C, mat, rbox, box, cyl, sph, group, canvasTex, panel, roundRect, hex, rng, FONT_DISPLAY, FONT_TEXT, geoCyl } from "./lib.js";

export const F = 0.03; // floor top inside an island

export function plant(p, x, z, s = 1, pot = C.white, leaf = C.leaf) {
  const g = group(p, x, F, z);
  g.scale.setScalar(s);
  cyl(g, 0.22, 0.17, 0.34, pot, 0, 0, 0);
  cyl(g, 0.2, 0.2, 0.03, 0x6b4b34, 0, 0.32, 0, { shadow: false });
  sph(g, 0.3, leaf, 0, 0.62, 0);
  sph(g, 0.22, C.leafDark, 0.14, 0.5, 0.08);
  sph(g, 0.2, leaf, -0.12, 0.82, -0.04);
  return g;
}

export function tree(p, x, z, s = 1) {
  const g = group(p, x, F, z);
  g.scale.setScalar(s);
  cyl(g, 0.09, 0.13, 0.9, C.trunk, 0, 0, 0);
  sph(g, 0.6, C.leaf, 0, 1.25, 0);
  sph(g, 0.45, C.leafDark, 0.32, 1.05, 0.2);
  sph(g, 0.42, 0x6cbf83, -0.25, 1.55, -0.1);
  return g;
}

export function palm(p, x, z, s = 1, seed = 3) {
  const R = rng(seed);
  const g = group(p, x, F, z);
  g.scale.setScalar(s);
  let y = 0;
  let px = 0;
  for (let i = 0; i < 7; i++) {
    const r = 0.13 - i * 0.008;
    cyl(g, r - 0.01, r, 0.36, i % 2 ? C.trunk : 0x8a6c4f, px, y, 0, { seg: 10 });
    y += 0.34;
    px += 0.02;
  }
  const crown = group(g, px, y, 0);
  sph(crown, 0.12, 0x6e5a40, 0, 0, 0, { ws: 10, hs: 8 });
  for (let i = 0; i < 9; i++) {
    const a = (i / 9) * Math.PI * 2 + R() * 0.3;
    const leafG = group(crown, 0, 0.02, 0);
    leafG.rotation.y = a;
    const fr = new THREE.Mesh(new THREE.ConeGeometry(0.16, 1.25, 4, 1), mat(i % 2 ? C.palm : C.leafDark));
    fr.geometry.translate(0, 0.62, 0);
    fr.scale.set(1, 1, 0.28);
    fr.rotation.z = -Math.PI / 2 + 0.55 + R() * 0.25;
    fr.castShadow = true;
    leafG.add(fr);
  }
  return g;
}

export function bush(p, x, z, s = 1, color = C.leaf) {
  const g = group(p, x, F, z);
  g.scale.setScalar(s);
  sph(g, 0.32, color, 0, 0.24, 0);
  sph(g, 0.25, C.leafDark, 0.26, 0.18, 0.06);
  sph(g, 0.24, 0x6cbf83, -0.22, 0.2, 0.08);
  return g;
}

export function desk(p, x, z, w = 1.4, d = 0.7, color = C.woodLight, rotY = 0) {
  const g = group(p, x, F, z);
  g.rotation.y = rotY;
  rbox(g, w, 0.07, d, color, 0, 0.7, 0, 0.03);
  [-1, 1].forEach((sx) => [-1, 1].forEach((sz) => box(g, 0.06, 0.7, 0.06, C.metal, sx * (w / 2 - 0.08), 0, sz * (d / 2 - 0.08))));
  return g;
}

export function chair(p, x, z, rotY = 0, color = C.blue) {
  const g = group(p, x, F, z);
  g.rotation.y = rotY;
  rbox(g, 0.46, 0.07, 0.44, color, 0, 0.42, 0, 0.03);
  rbox(g, 0.46, 0.46, 0.07, color, 0, 0.48, -0.2, 0.03);
  [-1, 1].forEach((sx) => [-1, 1].forEach((sz) => box(g, 0.04, 0.42, 0.04, C.metal, sx * 0.18, 0, sz * 0.17)));
  return g;
}

export function sofa(p, x, z, rotY = 0, color = C.sky, w = 1.8) {
  const g = group(p, x, F, z);
  g.rotation.y = rotY;
  rbox(g, w, 0.4, 0.8, color, 0, 0.05, 0, 0.12);
  rbox(g, w, 0.55, 0.22, color, 0, 0.35, -0.32, 0.1);
  rbox(g, 0.2, 0.32, 0.8, color, -w / 2 + 0.1, 0.35, 0, 0.08);
  rbox(g, 0.2, 0.32, 0.8, color, w / 2 - 0.1, 0.35, 0, 0.08);
  rbox(g, w - 0.5, 0.12, 0.55, 0xffffff, 0, 0.45, 0.06, 0.06);
  return g;
}

export function bookshelf(p, x, z, rotY = 0, w = 1.6, h = 1.9) {
  const g = group(p, x, F, z);
  g.rotation.y = rotY;
  const R = rng(11);
  rbox(g, w, h, 0.36, C.wood, 0, 0, 0, 0.03);
  const cols = [C.blue, C.sun, C.coral, C.sky, C.green, C.white, C.deep];
  for (let r = 0; r < 4; r++) {
    const y = 0.12 + r * (h / 4.2);
    box(g, w - 0.1, 0.03, 0.3, C.woodDark, 0, y, 0.04);
    let bx = -w / 2 + 0.12;
    while (bx < w / 2 - 0.2) {
      const bw = 0.07 + R() * 0.08;
      const bh = 0.22 + R() * 0.14;
      box(g, bw, bh, 0.24, cols[Math.floor(R() * cols.length)], bx + bw / 2, y + 0.03, 0.05, { shadow: false });
      bx += bw + 0.015;
    }
  }
  return g;
}

export function rug(p, x, z, w, d, color, rotY = 0) {
  const g = group(p, x, F, z);
  g.rotation.y = rotY;
  rbox(g, w, 0.025, d, color, 0, 0, 0, 0.012, { shadow: false });
  return g;
}

// Wall-mounted textured panel on a back wall. side: 'z' (wall at -z, faces +z) or 'x' (wall at -x, faces +x)
export function wallPanel(p, side, half, u, y, w, h, tex, opts = {}) {
  const off = 0.235;
  const m = panel(p, w, h, tex, 0, y, 0, opts);
  if (side === "z") m.position.set(u, y, -half + off);
  else {
    m.position.set(-half + off, y, u);
    m.rotation.y = Math.PI / 2;
  }
  return m;
}

export function frameBox(p, side, half, u, y, w, h, color = C.white, depth = 0.06) {
  const g = group(p);
  if (side === "z") {
    g.position.set(u, y, -half + 0.22 + depth / 2);
  } else {
    g.position.set(-half + 0.22 + depth / 2, y, u);
    g.rotation.y = Math.PI / 2;
  }
  rbox(g, w, h, depth, color, 0, -h / 2, 0, 0.02);
  return g;
}

export function lamp(p, x, z, h = 1.6) {
  const g = group(p, x, F, z);
  cyl(g, 0.18, 0.2, 0.05, C.dark, 0, 0, 0);
  cyl(g, 0.025, 0.025, h, C.dark, 0, 0.05, 0);
  cyl(g, 0.12, 0.24, 0.26, C.sun, 0, h - 0.05, 0, { emissive: C.sun, emissiveIntensity: 0.35 });
  return g;
}

export function monitor(p, x, y, z, rotY = 0, screenTex = null, w = 0.62, h = 0.4) {
  const g = group(p, x, y, z);
  g.rotation.y = rotY;
  box(g, 0.18, 0.02, 0.14, C.dark, 0, 0, 0);
  box(g, 0.04, 0.18, 0.04, C.dark, 0, 0.02, -0.02);
  rbox(g, w, h, 0.05, C.dark, 0, 0.18, -0.02, 0.02);
  if (screenTex) {
    const s = panel(g, w - 0.06, h - 0.06, screenTex, 0, 0.18 + h / 2, 0.006, { glow: 0.55 });
    s.castShadow = false;
  } else {
    box(g, w - 0.06, h - 0.06, 0.01, C.sky, 0, 0.21, 0.006, { emissive: C.sky, emissiveIntensity: 0.4 });
  }
  return g;
}

export function laptopScreenTex(accent = C.blue) {
  return canvasTex(256, 160, (ctx, w, h) => {
    ctx.fillStyle = "#eef6fc";
    ctx.fillRect(0, 0, w, h);
    ctx.fillStyle = hex(accent);
    ctx.fillRect(0, 0, w, 30);
    ctx.fillStyle = "#cfe4f3";
    for (let i = 0; i < 3; i++) {
      roundRect(ctx, 14, 44 + i * 36, w - 28, 24, 8);
      ctx.fill();
    }
    ctx.fillStyle = hex(C.sun);
    roundRect(ctx, 14, 44, 70, 24, 8);
    ctx.fill();
  });
}

export function blackboard(p, side, half, u, y, w, h, color = C.board, lines = true) {
  const tex = canvasTex(512, 300, (ctx, W, H) => {
    ctx.fillStyle = hex(color);
    ctx.fillRect(0, 0, W, H);
    ctx.strokeStyle = "rgba(255,255,255,0.85)";
    ctx.lineWidth = 6;
    ctx.lineCap = "round";
    if (lines) {
      ctx.font = `700 64px "${FONT_DISPLAY}"`;
      ctx.fillStyle = "rgba(255,255,255,0.9)";
      ctx.fillText("a + b = c", 40, 100);
      ctx.beginPath();
      ctx.arc(380, 150, 60, 0, Math.PI * 2);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(40, 190);
      ctx.lineTo(260, 190);
      ctx.moveTo(40, 240);
      ctx.lineTo(200, 240);
      ctx.stroke();
    }
    ctx.lineWidth = 18;
    ctx.strokeStyle = hex(C.wood);
    ctx.strokeRect(0, 0, W, H);
  });
  return wallPanel(p, side, half, u, y, w, h, tex);
}

export function window_(p, side, half, u, y, w, h) {
  const tex = canvasTex(256, 256, (ctx, W, H) => {
    const g = ctx.createLinearGradient(0, 0, W, H);
    g.addColorStop(0, "#bfe6fa");
    g.addColorStop(1, "#e9f6fd");
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = "rgba(255,255,255,0.7)";
    ctx.beginPath();
    ctx.moveTo(W * 0.15, H);
    ctx.lineTo(W * 0.45, 0);
    ctx.lineTo(W * 0.6, 0);
    ctx.lineTo(W * 0.3, H);
    ctx.fill();
    ctx.strokeStyle = "#ffffff";
    ctx.lineWidth = 14;
    ctx.strokeRect(0, 0, W, H);
    ctx.beginPath();
    ctx.moveTo(W / 2, 0);
    ctx.lineTo(W / 2, H);
    ctx.moveTo(0, H / 2);
    ctx.lineTo(W, H / 2);
    ctx.lineWidth = 8;
    ctx.stroke();
  });
  return wallPanel(p, side, half, u, y, w, h, tex);
}

export function clock(p, side, half, u, y) {
  const tex = canvasTex(128, 128, (ctx) => {
    ctx.beginPath();
    ctx.arc(64, 64, 60, 0, Math.PI * 2);
    ctx.fillStyle = "#ffffff";
    ctx.fill();
    ctx.lineWidth = 8;
    ctx.strokeStyle = hex(C.blue);
    ctx.stroke();
    ctx.strokeStyle = hex(C.ink);
    ctx.lineWidth = 6;
    ctx.lineCap = "round";
    ctx.beginPath();
    ctx.moveTo(64, 64);
    ctx.lineTo(64, 26);
    ctx.moveTo(64, 64);
    ctx.lineTo(92, 72);
    ctx.stroke();
  });
  return wallPanel(p, side, half, u, y, 0.5, 0.5, tex, { transparent: true });
}

// Flasks & lab bench
export function flask(p, x, y, z, color, s = 1) {
  const g = group(p, x, y, z);
  g.scale.setScalar(s);
  const glass = mat(0xd9eef8, { transparent: true, opacity: 0.55 });
  const liq = mat(color, { emissive: color, emissiveIntensity: 0.25 });
  const body = new THREE.Mesh(new THREE.ConeGeometry(0.13, 0.22, 16), liq);
  body.position.y = 0.11;
  g.add(body);
  const neck = new THREE.Mesh(geoCyl(0.035, 0.035, 0.14, 10), glass);
  neck.position.y = 0.28;
  g.add(neck);
  return g;
}
export function tube(p, x, y, z, color) {
  const g = group(p, x, y, z);
  cyl(g, 0.035, 0.035, 0.24, 0xd9eef8, 0, 0, 0, { transparent: true, opacity: 0.5, seg: 10 });
  cyl(g, 0.03, 0.03, 0.12, color, 0, 0.01, 0, { emissive: color, emissiveIntensity: 0.3, seg: 10 });
  return g;
}
export function microscope(p, x, y, z, rotY = 0) {
  const g = group(p, x, y, z);
  g.rotation.y = rotY;
  rbox(g, 0.26, 0.04, 0.3, C.white, 0, 0, 0, 0.02);
  box(g, 0.06, 0.38, 0.06, C.white, 0, 0.04, -0.1);
  const eye = new THREE.Mesh(geoCyl(0.04, 0.05, 0.3, 12), mat(C.dark));
  eye.position.set(0, 0.42, -0.03);
  eye.rotation.x = 0.5;
  g.add(eye);
  box(g, 0.16, 0.02, 0.14, C.metal, 0, 0.16, 0.0);
  return g;
}

export function ball(p, x, y, z, r = 0.16, color = C.sun) {
  return sph(p, r, color, x, y + r, z);
}

export function basketHoop(p, x, z, rotY = 0) {
  const g = group(p, x, F, z);
  g.rotation.y = rotY;
  cyl(g, 0.05, 0.06, 2.1, C.metal, 0, 0, 0);
  rbox(g, 0.9, 0.6, 0.05, C.white, 0, 1.9, 0.12, 0.02);
  box(g, 0.32, 0.22, 0.02, C.coral, 0, 1.98, 0.15, { shadow: false });
  const ring = new THREE.Mesh(new THREE.TorusGeometry(0.17, 0.02, 6, 20), mat(C.coral));
  ring.rotation.x = Math.PI / 2;
  ring.position.set(0, 1.95, 0.35);
  g.add(ring);
  return g;
}

export function bench(p, x, z, rotY = 0, color = C.wood) {
  const g = group(p, x, F, z);
  g.rotation.y = rotY;
  rbox(g, 1.3, 0.07, 0.4, color, 0, 0.38, 0, 0.03);
  rbox(g, 1.3, 0.3, 0.06, color, 0, 0.5, -0.17, 0.03);
  [-1, 1].forEach((s) => box(g, 0.06, 0.38, 0.36, C.dark, s * 0.55, 0, 0));
  return g;
}

export function lockers(p, x, z, rotY = 0, n = 4) {
  const g = group(p, x, F, z);
  g.rotation.y = rotY;
  const cols = [C.sky, C.blue, C.sun, C.coral];
  for (let i = 0; i < n; i++) {
    rbox(g, 0.42, 1.5, 0.42, cols[i % cols.length], (i - (n - 1) / 2) * 0.45, 0, 0, 0.03);
    box(g, 0.05, 0.15, 0.02, C.white, (i - (n - 1) / 2) * 0.45 + 0.12, 0.8, 0.22, { shadow: false });
  }
  return g;
}

export function easel(p, x, z, rotY = 0, tex) {
  const g = group(p, x, F, z);
  g.rotation.y = rotY;
  const legA = box(g, 0.05, 1.5, 0.05, C.wood, -0.3, 0, 0.05);
  legA.rotation.z = 0.12;
  const legB = box(g, 0.05, 1.5, 0.05, C.wood, 0.3, 0, 0.05);
  legB.rotation.z = -0.12;
  const legC = box(g, 0.05, 1.45, 0.05, C.wood, 0, 0, -0.25);
  legC.rotation.x = -0.2;
  box(g, 0.8, 0.04, 0.1, C.wood, 0, 0.55, 0.1);
  if (tex) panel(g, 0.84, 0.66, tex, 0, 0.92, 0.12);
  return g;
}

export function goal(p, x, z, rotY = 0) {
  const g = group(p, x, F, z);
  g.rotation.y = rotY;
  const w = 1.4, h = 0.8;
  box(g, 0.06, h, 0.06, C.white, -w / 2, 0, 0);
  box(g, 0.06, h, 0.06, C.white, w / 2, 0, 0);
  box(g, w + 0.06, 0.06, 0.06, C.white, 0, h, 0);
  const net = new THREE.Mesh(new THREE.PlaneGeometry(w, h), mat(0xffffff, { transparent: true, opacity: 0.35, side: THREE.DoubleSide }));
  net.position.set(0, h / 2, -0.3);
  g.add(net);
  return g;
}

export function balloon(p, x, y, z, color) {
  const g = group(p, x, y, z);
  const b = sph(g, 0.24, color, 0, 0.9, 0, { emissive: color, emissiveIntensity: 0.12 });
  b.scale.set(1, 1.18, 1);
  box(g, 0.01, 0.65, 0.01, 0x8f8f8f, 0, 0.0, 0, { shadow: false });
  return g;
}

// Low-poly cloud (merged spheres), y = center.
export function cloud(p, x, y, z, s = 1, seed = 1) {
  const g = group(p, x, y, z);
  g.scale.setScalar(s);
  const R = rng(seed);
  const m = mat(0xffffff, { emissive: 0xffffff, emissiveIntensity: 0.35 });
  const n = 5;
  for (let i = 0; i < n; i++) {
    const r = 0.5 + R() * 0.45;
    const s2 = new THREE.Mesh(new THREE.SphereGeometry(r, 12, 9), m);
    s2.position.set((i - (n - 1) / 2) * 0.62, (R() - 0.3) * 0.3, (R() - 0.5) * 0.5);
    s2.scale.y = 0.72;
    g.add(s2);
  }
  return g;
}
