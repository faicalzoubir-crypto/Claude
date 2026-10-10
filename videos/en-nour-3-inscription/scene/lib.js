// Shared modeling kit for the EN-NOUR 3 isometric world.
// Everything here is deterministic: no clocks, no randomness (use rng()).
import * as THREE from "three";
import { RoundedBoxGeometry } from "three/addons/RoundedBoxGeometry.js";

// ── Brand + world palette ───────────────────────────────────────────────────
export const C = {
  sun: 0xf8b114,
  sunDeep: 0xe89a0c,
  blue: 0x2a91d1,
  sky: 0x35b3e5,
  deep: 0x165a8a,
  ink: 0x1d3b57,
  cream: 0xf6eee1,
  ivory: 0xfbf7ef,
  white: 0xfdfcf9,
  wall: 0xf3f0ea,
  facade: 0xdcdedf,
  facadeDark: 0xc3c7ca,
  glass: 0x7f9fc0,
  mustard: 0xe3b23c,
  steel: 0xb7bec5,
  pave: 0xe8d8bd,
  paveDark: 0xd8c4a3,
  lawn: 0x9fd0a6,
  leaf: 0x4fa36b,
  leafDark: 0x2f7d52,
  palm: 0x3d9460,
  trunk: 0x9a7b5c,
  wood: 0xc99366,
  woodLight: 0xe2bb8f,
  woodDark: 0x8e5f3d,
  floorWarm: 0xefe5d4,
  floorTile: 0xe7ddcb,
  coral: 0xf28c5b,
  red: 0xd8423a,
  green: 0x2f8f4e,
  board: 0x2f5d50,
  dark: 0x2a2f38,
  metal: 0x8d97a3,
  pink: 0xf2a3a8,
  violet: 0x8a7fd8,
  // cycles, warm → cool as the child grows
  maternelle: 0xf28c5b,
  primaire: 0xf8b114,
  college: 0x35b3e5,
  lycee: 0x2a91d1,
};

export const FONT_DISPLAY = "Baloo 2";
export const FONT_TEXT = "Quicksand";

// ── Deterministic RNG ───────────────────────────────────────────────────────
export function rng(seed = 1) {
  let s = seed >>> 0;
  return () => {
    s = (s + 0x6d2b79f5) >>> 0;
    let t = s;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// ── Materials (cached) ──────────────────────────────────────────────────────
const matCache = new Map();
export function mat(color, opts = {}) {
  const key = color + JSON.stringify(opts);
  if (!matCache.has(key)) {
    const { emissive, emissiveIntensity, transparent, opacity, basic, side } = opts;
    const m = basic
      ? new THREE.MeshBasicMaterial({ color, transparent: !!transparent, opacity: opacity ?? 1, side: side ?? THREE.FrontSide })
      : new THREE.MeshLambertMaterial({
          color,
          emissive: emissive ?? 0x000000,
          emissiveIntensity: emissiveIntensity ?? 1,
          transparent: !!transparent,
          opacity: opacity ?? 1,
          side: side ?? THREE.FrontSide,
        });
    matCache.set(key, m);
  }
  return matCache.get(key);
}
// Fresh (uncached) material when an object needs its own animated opacity/emissive.
export function ownMat(color, opts = {}) {
  return new THREE.MeshLambertMaterial({ color, transparent: true, opacity: 1, ...opts });
}

// ── Geometry (cached) ───────────────────────────────────────────────────────
const geoCache = new Map();
function cached(key, make) {
  if (!geoCache.has(key)) geoCache.set(key, make());
  return geoCache.get(key);
}
const r3 = (v) => Math.round(v * 1000) / 1000;

export function geoRBox(w, h, d, r = 0.06, seg = 2) {
  r = Math.min(r, w / 2 - 0.001, h / 2 - 0.001, d / 2 - 0.001);
  return cached(`rb${r3(w)}|${r3(h)}|${r3(d)}|${r3(r)}|${seg}`, () => new RoundedBoxGeometry(w, h, d, seg, Math.max(r, 0.001)));
}
export function geoBox(w, h, d) {
  return cached(`b${r3(w)}|${r3(h)}|${r3(d)}`, () => new THREE.BoxGeometry(w, h, d));
}
export function geoCyl(rt, rb, h, seg = 20) {
  return cached(`c${r3(rt)}|${r3(rb)}|${r3(h)}|${seg}`, () => new THREE.CylinderGeometry(rt, rb, h, seg));
}
export function geoSph(r, ws = 18, hs = 14) {
  return cached(`s${r3(r)}|${ws}|${hs}`, () => new THREE.SphereGeometry(r, ws, hs));
}
export function geoCap(r, len, cs = 4, rs = 10) {
  return cached(`k${r3(r)}|${r3(len)}`, () => new THREE.CapsuleGeometry(r, len, cs, rs));
}

function finish(m, shadow = true) {
  m.castShadow = shadow;
  m.receiveShadow = true;
  return m;
}

// Mesh builders. `y` is the BOTTOM of the object unless noted.
export function rbox(parent, w, h, d, color, x = 0, y = 0, z = 0, r = 0.06, opts) {
  const m = finish(new THREE.Mesh(geoRBox(w, h, d, r), opts?.material ?? mat(color, opts)), opts?.shadow ?? true);
  m.position.set(x, y + h / 2, z);
  if (parent) parent.add(m);
  return m;
}
export function box(parent, w, h, d, color, x = 0, y = 0, z = 0, opts) {
  const m = finish(new THREE.Mesh(geoBox(w, h, d), opts?.material ?? mat(color, opts)), opts?.shadow ?? true);
  m.position.set(x, y + h / 2, z);
  if (parent) parent.add(m);
  return m;
}
export function cyl(parent, rt, rb, h, color, x = 0, y = 0, z = 0, opts) {
  const m = finish(new THREE.Mesh(geoCyl(rt, rb, h, opts?.seg ?? 20), opts?.material ?? mat(color, opts)), opts?.shadow ?? true);
  m.position.set(x, y + h / 2, z);
  if (parent) parent.add(m);
  return m;
}
// Sphere: y is the CENTER.
export function sph(parent, r, color, x = 0, y = 0, z = 0, opts) {
  const m = finish(new THREE.Mesh(geoSph(r, opts?.ws ?? 18, opts?.hs ?? 14), opts?.material ?? mat(color, opts)), opts?.shadow ?? true);
  m.position.set(x, y, z);
  if (parent) parent.add(m);
  return m;
}
export function group(parent, x = 0, y = 0, z = 0) {
  const g = new THREE.Group();
  g.position.set(x, y, z);
  if (parent) parent.add(g);
  return g;
}

// ── Canvas textures ─────────────────────────────────────────────────────────
export function canvasTex(w, h, draw) {
  const cv = document.createElement("canvas");
  cv.width = w;
  cv.height = h;
  const ctx = cv.getContext("2d");
  draw(ctx, w, h);
  const tex = new THREE.CanvasTexture(cv);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 4;
  tex.userData = { canvas: cv, ctx, draw };
  return tex;
}
export const hex = (c) => "#" + c.toString(16).padStart(6, "0");

export function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}

// Flat textured panel (a sign, a screen, a poster). Plane lies in XY, faces +Z.
export function panel(parent, w, h, tex, x = 0, y = 0, z = 0, opts = {}) {
  const m = new THREE.Mesh(
    new THREE.PlaneGeometry(w, h),
    opts.lit === false
      ? new THREE.MeshBasicMaterial({ map: tex, transparent: !!opts.transparent, toneMapped: false })
      : new THREE.MeshLambertMaterial({ map: tex, transparent: !!opts.transparent, emissive: 0xffffff, emissiveMap: opts.glow ? tex : null, emissiveIntensity: opts.glow ?? 0 })
  );
  m.position.set(x, y, z);
  m.receiveShadow = !opts.glow;
  if (parent) parent.add(m);
  return m;
}

// Camera-facing label sprite: rounded pill with text. Height in world units.
export function pillSprite(text, opts = {}) {
  const {
    height = 0.6,
    bg = "#ffffff",
    fg = hex(C.deep),
    font = FONT_DISPLAY,
    weight = 700,
    px = 72,
    padX = 40,
    dot = null,
    border = null,
  } = opts;
  const meas = document.createElement("canvas").getContext("2d");
  meas.font = `${weight} ${px}px "${font}"`;
  const tw = Math.ceil(meas.measureText(text).width);
  const dotW = dot ? px * 0.62 : 0;
  const W = tw + padX * 2 + dotW;
  const H = Math.round(px * 1.55);
  const tex = canvasTex(W + 16, H + 16, (ctx) => {
    ctx.translate(8, 8);
    ctx.shadowColor = "rgba(22,58,90,0.18)";
    ctx.shadowBlur = 8;
    ctx.shadowOffsetY = 3;
    roundRect(ctx, 0, 0, W, H, H / 2);
    ctx.fillStyle = bg;
    ctx.fill();
    ctx.shadowColor = "transparent";
    if (border) {
      ctx.lineWidth = 5;
      ctx.strokeStyle = border;
      ctx.stroke();
    }
    if (dot) {
      ctx.beginPath();
      ctx.arc(padX + px * 0.22, H / 2, px * 0.2, 0, Math.PI * 2);
      ctx.fillStyle = dot;
      ctx.fill();
    }
    ctx.font = `${weight} ${px}px "${font}"`;
    ctx.fillStyle = fg;
    ctx.textBaseline = "middle";
    ctx.fillText(text, padX + dotW, H / 2 + px * 0.06);
  });
  const sm = new THREE.SpriteMaterial({ map: tex, transparent: true, depthTest: false, depthWrite: false });
  const s = new THREE.Sprite(sm);
  const aspect = (W + 16) / (H + 16);
  s.scale.set(height * aspect, height, 1);
  s.renderOrder = 50;
  s.userData.baseScale = s.scale.clone();
  return s;
}

// Speech bubble sprite (icon or short text).
export function bubbleSprite(drawInner, opts = {}) {
  const { size = 1.0, bg = "#ffffff" } = opts;
  const S = 256;
  const tex = canvasTex(S, S, (ctx) => {
    ctx.shadowColor = "rgba(22,58,90,0.2)";
    ctx.shadowBlur = 10;
    ctx.shadowOffsetY = 4;
    roundRect(ctx, 24, 20, S - 48, S - 80, 52);
    ctx.fillStyle = bg;
    ctx.fill();
    ctx.beginPath();
    ctx.moveTo(S * 0.36, S - 62);
    ctx.lineTo(S * 0.3, S - 22);
    ctx.lineTo(S * 0.52, S - 62);
    ctx.fill();
    ctx.shadowColor = "transparent";
    drawInner(ctx, S / 2, (S - 60) / 2 + 10, S);
  });
  const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, transparent: true, depthTest: false, depthWrite: false }));
  s.scale.set(size, size, 1);
  s.renderOrder = 60;
  s.userData.baseScale = s.scale.clone();
  return s;
}

// Soft radial glow sprite (additive).
let glowTex = null;
export function glowSprite(color = C.sun, size = 2, opacity = 0.9) {
  if (!glowTex) {
    glowTex = canvasTex(256, 256, (ctx) => {
      const g = ctx.createRadialGradient(128, 128, 0, 128, 128, 128);
      g.addColorStop(0, "rgba(255,255,255,1)");
      g.addColorStop(0.25, "rgba(255,255,255,0.55)");
      g.addColorStop(0.6, "rgba(255,255,255,0.12)");
      g.addColorStop(1, "rgba(255,255,255,0)");
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, 256, 256);
    });
  }
  const s = new THREE.Sprite(
    new THREE.SpriteMaterial({ map: glowTex, color, transparent: true, opacity, blending: THREE.AdditiveBlending, depthWrite: false })
  );
  s.scale.set(size, size, 1);
  s.userData.baseScale = s.scale.clone();
  return s;
}

// ── Icons drawn on canvas (no emoji fonts in the renderer) ─────────────────
export const ICONS = {
  check(ctx, cx, cy, s, color = "#2f8f4e") {
    ctx.strokeStyle = color;
    ctx.lineWidth = s * 0.14;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.beginPath();
    ctx.moveTo(cx - s * 0.32, cy + s * 0.02);
    ctx.lineTo(cx - s * 0.08, cy + s * 0.26);
    ctx.lineTo(cx + s * 0.34, cy - s * 0.24);
    ctx.stroke();
  },
  question(ctx, cx, cy, s, color) {
    ctx.fillStyle = color;
    ctx.font = `800 ${s}px "${FONT_DISPLAY}"`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("?", cx, cy + s * 0.06);
  },
  bulb(ctx, cx, cy, s, color) {
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(cx, cy - s * 0.1, s * 0.3, Math.PI * 0.8, Math.PI * 2.2);
    ctx.lineTo(cx + s * 0.13, cy + s * 0.25);
    ctx.lineTo(cx - s * 0.13, cy + s * 0.25);
    ctx.closePath();
    ctx.fill();
    roundRect(ctx, cx - s * 0.14, cy + s * 0.29, s * 0.28, s * 0.13, s * 0.04);
    ctx.fill();
  },
  chart(ctx, cx, cy, s, color) {
    ctx.fillStyle = color;
    const bw = s * 0.16;
    [0.3, 0.5, 0.78].forEach((h, i) => {
      roundRect(ctx, cx - s * 0.36 + i * s * 0.26, cy + s * 0.36 - s * h, bw, s * h, s * 0.04);
      ctx.fill();
    });
  },
  shield(ctx, cx, cy, s, color) {
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.moveTo(cx, cy - s * 0.4);
    ctx.lineTo(cx + s * 0.34, cy - s * 0.26);
    ctx.quadraticCurveTo(cx + s * 0.32, cy + s * 0.22, cx, cy + s * 0.42);
    ctx.quadraticCurveTo(cx - s * 0.32, cy + s * 0.22, cx - s * 0.34, cy - s * 0.26);
    ctx.closePath();
    ctx.fill();
    ICONS.check(ctx, cx, cy, s * 0.5, "#ffffff");
  },
  chat(ctx, cx, cy, s, color) {
    ctx.fillStyle = color;
    roundRect(ctx, cx - s * 0.4, cy - s * 0.34, s * 0.56, s * 0.38, s * 0.1);
    ctx.fill();
    ctx.globalAlpha = 0.65;
    roundRect(ctx, cx - s * 0.12, cy - s * 0.06, s * 0.52, s * 0.36, s * 0.1);
    ctx.fill();
    ctx.globalAlpha = 1;
  },
  heart(ctx, cx, cy, s, color) {
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.moveTo(cx, cy + s * 0.32);
    ctx.bezierCurveTo(cx - s * 0.5, cy, cx - s * 0.3, cy - s * 0.42, cx, cy - s * 0.16);
    ctx.bezierCurveTo(cx + s * 0.3, cy - s * 0.42, cx + s * 0.5, cy, cx, cy + s * 0.32);
    ctx.fill();
  },
  calendar(ctx, cx, cy, s, color) {
    ctx.fillStyle = color;
    roundRect(ctx, cx - s * 0.36, cy - s * 0.3, s * 0.72, s * 0.66, s * 0.08);
    ctx.fill();
    ctx.fillStyle = "#ffffff";
    for (let r = 0; r < 2; r++)
      for (let c = 0; c < 3; c++) {
        roundRect(ctx, cx - s * 0.26 + c * s * 0.19, cy - s * 0.04 + r * s * 0.17, s * 0.13, s * 0.11, s * 0.02);
        ctx.fill();
      }
  },
  star(ctx, cx, cy, s, color) {
    ctx.fillStyle = color;
    ctx.beginPath();
    for (let i = 0; i < 10; i++) {
      const a = -Math.PI / 2 + (i * Math.PI) / 5;
      const r = i % 2 ? s * 0.18 : s * 0.4;
      ctx.lineTo(cx + Math.cos(a) * r, cy + Math.sin(a) * r);
    }
    ctx.closePath();
    ctx.fill();
  },
  hello(ctx, cx, cy, s, color) {
    ctx.fillStyle = color;
    ctx.font = `800 ${s * 0.36}px "${FONT_DISPLAY}"`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("Bienvenue !", cx, cy + s * 0.03);
  },
};

export function iconBubble(icon, color, size = 0.9, bg = "#ffffff") {
  return bubbleSprite((ctx, cx, cy, S) => ICONS[icon](ctx, cx, cy, S * 0.42, color), { size, bg });
}

// Round icon badge sprite (a coin with an icon), for orbiting badges.
export function badgeSprite(icon, bgColor, size = 0.9, fg = "#ffffff") {
  const S = 256;
  const tex = canvasTex(S, S, (ctx) => {
    ctx.shadowColor = "rgba(22,58,90,0.25)";
    ctx.shadowBlur = 12;
    ctx.shadowOffsetY = 5;
    ctx.beginPath();
    ctx.arc(S / 2, S / 2, S * 0.4, 0, Math.PI * 2);
    ctx.fillStyle = bgColor;
    ctx.fill();
    ctx.shadowColor = "transparent";
    ctx.lineWidth = 10;
    ctx.strokeStyle = "rgba(255,255,255,0.9)";
    ctx.stroke();
    ICONS[icon](ctx, S / 2, S / 2, S * 0.42, fg);
  });
  const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, transparent: true, depthTest: false, depthWrite: false }));
  s.scale.set(size, size, 1);
  s.renderOrder = 55;
  s.userData.baseScale = s.scale.clone();
  return s;
}

// ── Timing helpers (pure functions of t) ────────────────────────────────────
export const clamp01 = (v) => (v < 0 ? 0 : v > 1 ? 1 : v);
export const lerp = (a, b, k) => a + (b - a) * k;
export const E = {
  linear: (k) => k,
  inOut2: (k) => (k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2),
  inOut3: (k) => (k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2),
  out2: (k) => 1 - (1 - k) * (1 - k),
  out3: (k) => 1 - Math.pow(1 - k, 3),
  out4: (k) => 1 - Math.pow(1 - k, 4),
  in2: (k) => k * k,
  outBack: (k) => {
    const c1 = 1.70158, c3 = c1 + 1;
    return 1 + c3 * Math.pow(k - 1, 3) + c1 * Math.pow(k - 1, 2);
  },
  outElastic: (k) => {
    if (k === 0 || k === 1) return k;
    return Math.pow(2, -10 * k) * Math.sin((k * 10 - 0.75) * ((2 * Math.PI) / 3)) + 1;
  },
};
// progress of t through [t0, t0+dur], eased
export function prog(t, t0, dur, ease = E.inOut3) {
  return ease(clamp01((t - t0) / dur));
}
// Keyframe track: [[time, value], ...] with per-segment ease (value can be number or array)
export function track(keys, ease = E.inOut3) {
  return (t) => {
    if (t <= keys[0][0]) return keys[0][1];
    for (let i = 0; i < keys.length - 1; i++) {
      const [t0, v0] = keys[i];
      const [t1, v1, e] = keys[i + 1];
      if (t <= t1) {
        const k = (e ?? ease)(clamp01((t - t0) / (t1 - t0)));
        if (Array.isArray(v0)) return v0.map((a, j) => lerp(a, v1[j], k));
        return lerp(v0, v1, k);
      }
    }
    return keys[keys.length - 1][1];
  };
}
// Pop-in scale (0 → 1 with overshoot) then optional pop-out.
export function popScale(t, tin, tout = Infinity, dIn = 0.45, dOut = 0.3) {
  if (t < tin) return 0;
  if (t < tin + dIn) return E.outBack(clamp01((t - tin) / dIn));
  if (t < tout) return 1;
  if (t < tout + dOut) return 1 - E.in2(clamp01((t - tout) / dOut));
  return 0;
}
