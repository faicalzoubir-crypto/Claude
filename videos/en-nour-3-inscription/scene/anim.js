// The film: every visual state is a pure function of time t (seconds).
import * as THREE from "three";
import { E, clamp01, lerp, prog, popScale, track } from "./lib.js";
import { pose } from "./people.js";
import { WORLD, STATIONS } from "./world.js";
import { L, VO_DUR, at, lineEnd, DEPART, ARRIVE, TOTAL } from "./timing.js";

const V = (x, y, z) => new THREE.Vector3(x, y, z);
const S = STATIONS;
const sp = (i, x, y, z) => V(S[i].pos.x + x, S[i].pos.y + y, S[i].pos.z + z);

// ── Walking along a polyline ────────────────────────────────────────────────
function walk(P, pts, t0, t1, t, endRot = null, stride = 5.6) {
  const seg = [];
  let total = 0;
  for (let i = 0; i < pts.length - 1; i++) {
    const d = Math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]);
    seg.push(d);
    total += d;
  }
  const raw = clamp01((t - t0) / (t1 - t0));
  const k = E.inOut2(raw);
  let dist = k * total;
  let i = 0;
  while (i < seg.length - 1 && dist > seg[i]) {
    dist -= seg[i];
    i++;
  }
  const a = pts[i], b = pts[i + 1];
  const f = seg[i] ? Math.min(1, dist / seg[i]) : 1;
  P.root.position.x = lerp(a[0], b[0], f);
  P.root.position.z = lerp(a[1], b[1], f);
  const moving = raw > 0 && raw < 1;
  const heading = Math.atan2(b[0] - a[0], b[1] - a[1]);
  if (raw >= 1 && endRot !== null) {
    P.root.rotation.y = endRot;
  } else P.root.rotation.y = heading;
  const amt = moving ? Math.min(1, Math.min(raw, 1 - raw) * 8) : 0;
  return { walk: k * total * stride, walkAmt: amt };
}

// ── Camera ──────────────────────────────────────────────────────────────────
// Keys: [time, [x, y, z, vh, az], ease]
const AZ = Math.PI / 4;
function camKeys() {
  const sun = WORLD.sun.group.position;
  const mid = S[0].pos.clone().lerp(S[7].pos, 0.5);
  const K = [];
  const push = (t, p, vh, ease = E.inOut3, az = AZ) => K.push([t, [p.x, p.y, p.z, vh, az], ease]);
  // Hook: from the sun, swoop down the whole visit, land on the façade
  push(0, V(sun.x + 1.5, sun.y - 3.2, sun.z + 1.5), 21);
  push(1.75, V(sun.x + 1.5, sun.y - 4.2, sun.z + 1.5), 19.5, E.inOut2);
  push(3.05, V(mid.x, mid.y + 3, mid.z), 64, E.inOut3, AZ + 0.12);
  push(4.45, sp(0, 0.5, 2.1, 0.7), 21, E.out4);
  push(DEPART(1), sp(0, -0.3, 2.3, 0.3), 17.5, E.inOut2);
  // S1 Accueil
  push(ARRIVE(1), sp(1, 0.4, 1.3, -0.6), 13.2);
  push(at(1, "et vous", -0.25), sp(1, 0.0, 1.4, -1.0), 12.4, E.inOut2);
  push(at(1, "et vous", 0.75), sp(1, -2.3, 1.75, -1.8), 7.6, E.inOut3);
  push(DEPART(2), sp(1, -2.3, 1.75, -1.8), 7.2, E.linear);
  // S2 Présentation
  push(ARRIVE(2), sp(2, 0.9, 1.4, -0.9), 13.0);
  push(at(2, "et nos", -0.2), sp(2, 0.6, 1.3, -0.6), 12.2, E.inOut2);
  push(at(2, "maternelle", 0.1), sp(2, -0.3, 1.45, 0.3), 7.4, E.inOut3);
  push(DEPART(3), sp(2, -0.3, 1.5, 0.3), 7.0, E.linear);
  // S3 Infrastructures — a tour of the rooms
  const z = S[3].zones;
  const zc = (c, dy = 0.1) => sp(3, c.x, c.y + dy, c.z);
  push(ARRIVE(3), sp(3, 0, 1.0, 0), 17.5);
  push(at(3, "Visitez", 0.75), zc(z.classe.center), 8.8);
  push(at(3, "nos laboratoires", 0.0), zc(z.classe.center), 8.6, E.linear);
  push(at(3, "nos laboratoires", 0.55), zc(z.labo.center), 8.8);
  push(at(3, "la salle", 0.0), zc(z.labo.center), 8.6, E.linear);
  push(at(3, "la salle", 0.55), zc(z.info.center), 8.8);
  push(at(3, "la cour", 0.0), zc(z.info.center), 8.6, E.linear);
  push(at(3, "la cour", 0.55), zc(z.cour.center, -0.2), 9.4);
  push(at(3, "et nos espaces", 0.0), zc(z.cour.center, -0.2), 9.2, E.linear);
  push(at(3, "et nos espaces", 0.9), sp(3, 0, 1.0, 0), 15.5);
  push(DEPART(4), sp(3, -0.3, 1.0, -0.3), 15.0, E.linear);
  // S4 Organisation
  push(ARRIVE(4), sp(4, 0.2, 1.8, -0.6), 13.4);
  push(DEPART(5), sp(4, -0.1, 1.9, -0.9), 11.2, E.inOut2);
  // S5 Services
  push(ARRIVE(5), sp(5, -0.1, 1.9, -0.3), 13.0);
  push(at(5, "suivez", -0.2), sp(5, -0.45, 2.3, -1.0), 7.8);
  push(at(5, "et découvrez", -0.15), sp(5, -0.45, 2.2, -1.0), 7.5, E.linear);
  push(at(5, "et découvrez", 0.8), sp(5, -0.4, 1.2, 1.6), 10.5);
  push(DEPART(6), sp(5, -0.2, 1.2, 1.5), 10.0, E.linear);
  // S6 Modalités
  push(ARRIVE(6), sp(6, -0.7, 1.4, -0.9), 12.4);
  push(at(6, "Admission", 0.3), sp(6, -2.0, 1.8, -0.35), 8.2);
  push(at(6, "constitution", 0.1), sp(6, -2.0, 1.8, -0.35), 7.9, E.linear);
  push(at(6, "les modalités", -0.2), sp(6, -0.4, 1.3, -1.2), 9.0);
  push(DEPART(7), sp(6, -0.3, 1.3, -1.2), 8.6, E.linear);
  // S7 Conclusion
  push(ARRIVE(7), sp(7, 0.2, 1.4, -0.7), 12.6);
  push(lineEnd(7) - 0.3, sp(7, 0.1, 1.4, -0.6), 9.8, E.inOut2);
  // CTA: rise to the sun, pull back to the whole visit
  push(L[8] + 2.6, V(mid.x, mid.y + 9.5, mid.z), 78, E.inOut3, AZ + 0.1);
  push(TOTAL, V(mid.x, mid.y + 9.0, mid.z), 74, E.out2, AZ + 0.12);
  return track(K.map(([t, v, e]) => [t, v, e]));
}

// ── Guide orb (a little sun) ────────────────────────────────────────────────
function orbAt(t, out) {
  const sun = WORLD.sun.group.position;
  const B = WORLD.bridges;
  const hoverAt = (i) => {
    const s = S[i];
    const base = s.pos.clone().add(V(0.6, 3.1, 0.6));
    base.y += Math.sin(t * 2.2 + i) * 0.12;
    return base;
  };
  if (t < 1.8) {
    out.copy(sun).add(V(0.8, -2.4, 0.8));
    out.y += Math.sin(t * 2) * 0.1;
    return 0.6 + 0.4 * prog(t, 0, 1.2, E.out2);
  }
  if (t < 4.6) {
    const k = prog(t, 1.8, 2.8, E.inOut3);
    const a = sun.clone().add(V(0.8, -2.4, 0.8));
    const b = sp(0, -0.9, 2.2, 2.6);
    out.copy(a).lerp(b, k);
    out.y += Math.sin(k * Math.PI) * 4;
    return 1;
  }
  for (let i = 1; i <= 7; i++) {
    if (t < DEPART(i)) {
      // hovering at station i-1
      if (i === 1) {
        out.copy(sp(0, -0.9, 2.2 + Math.sin(t * 2.2) * 0.12, 2.6 - prog(t, 4.6, 1.0) * 3.2));
      } else out.copy(hoverAt(i - 1));
      return 1;
    }
    if (t < ARRIVE(i)) {
      const k = prog(t, DEPART(i), ARRIVE(i) - DEPART(i), E.inOut2);
      out.copy(B[i - 1].curve.getPoint(k));
      out.y += 0.35;
      return 1.15;
    }
  }
  if (t < L[8] - 0.5) {
    out.copy(hoverAt(7));
    return 1;
  }
  // CTA: the orb flies home into the sun
  const k = prog(t, L[8] - 0.5, 2.4, E.inOut3);
  out.copy(hoverAt(7)).lerp(sun, k);
  return 1 - k * 0.8;
}

// Bridge i lights as the orb travels it (and stays lit).
function bridgeProgress(i, t) {
  return prog(t, DEPART(i + 1), ARRIVE(i + 1) - DEPART(i + 1) + 0.15, E.inOut2);
}

// ── Visibility windows for the family copies ───────────────────────────────
function famVisible(i, t) {
  if (i === 0) return t < ARRIVE(1) + 0.3;
  const show = t >= DEPART(i) - 0.05;
  const hide = i < 7 ? t > ARRIVE(i + 1) + 0.3 : t > L[8] + 1.2;
  return show && !hide;
}

// ── Station animations ──────────────────────────────────────────────────────
const tmpV = new THREE.Vector3();

function setSprite(sp_, s, x, y, z) {
  sp_.visible = s > 0.001;
  sp_.scale.copy(sp_.userData.baseScale).multiplyScalar(Math.max(s, 0.0001));
  if (x !== undefined) sp_.position.set(x, y, z);
}

function animFacade(t) {
  const s = S[0];
  // gates swing open
  const g = prog(t, 4.6, 0.9, E.out3);
  s.gates[0].rotation.y = -1.45 * g;
  s.gates[1].rotation.y = 1.45 * g;
  s.atriumDoor.material.opacity = 0.55 * prog(t, 5.2, 0.6);
  // family walks the sidewalk to the gate, then in
  const mom = walk(s.mom, [[3.9, 4.15], [-0.6, 3.3], [-0.75, 1.2], [-0.6, -0.4]], 2.2, 6.6, t);
  const kid = walk(s.kid, [[4.3, 3.55], [-1.2, 3.0], [-1.2, 1.1], [-1.0, -0.3]], 2.25, 6.7, t);
  pose(s.mom, { ...mom, hold: 0 });
  pose(s.kid, { ...kid });
  s.flag.rotation.y = Math.sin(t * 3) * 0.12;
}

function animAccueil(t) {
  const s = S[1];
  const t0 = L[1];
  const mom = walk(s.mom, [[1.7, 4.2], [1.5, 1.0], [1.3, -1.1]], DEPART(1) + 0.3, t0 + 2.0, t, Math.PI + 0.25);
  const kid = walk(s.kid, [[0.7, 4.4], [0.5, 1.2], [0.4, -0.9]], DEPART(1) + 0.4, t0 + 2.1, t, Math.PI - 0.2);
  pose(s.mom, mom);
  pose(s.kid, { ...kid, lookY: prog(t, at(1, "et vous"), 0.6) * 0.6 });
  const wave = prog(t, t0 + 0.3, 0.4, E.out2) * (1 - prog(t, t0 + 2.6, 0.5));
  pose(s.receptionist, { wave, wavePhase: t * 10, point: prog(t, at(1, "et vous"), 0.5) * 0.9 });
  s.receptionist.root.rotation.y = -0.6 * prog(t, at(1, "et vous"), 0.6);
  // welcome bubble
  setSprite(WORLD.hello, popScale(t, t0 + 0.4, at(1, "identifions", 0.2)), s.pos.x + 0.4, s.pos.y + 2.75, s.pos.z - 3.2);
  // level chips: the receptionist asks the level, "Primaire" is chosen
  const chips = WORLD.levelChips;
  chips.forEach((c, i) => {
    const tin = at(1, "identifions", -0.1 + i * 0.12);
    const sc = popScale(t, tin, at(1, "et vous", 0.35));
    const chosen = i === 1 ? 1 + 0.25 * prog(t, at(1, "niveau", 0.0), 0.35, E.outBack) : 1 - 0.25 * prog(t, at(1, "niveau", 0.0), 0.35);
    setSprite(c, sc * chosen, s.pos.x + 0.9 + (i - 1.5) * 1.15 * 0.7, s.pos.y + 2.9 + (i % 2) * 0.0, s.pos.z - 1.6 + (i - 1.5) * 1.15 * 0.7);
  });
  // visit plan board glows
  const glow = prog(t, at(1, "et vous", 0.3), 0.6);
  WORLD.planGlow.material.opacity = 0.75 * glow;
  if (s.doorGlow) s.doorGlow.material.opacity = 0.25 + 0.45 * prog(t, DEPART(2) - 0.6, 0.5);
}

function animPresentation(t) {
  const s = S[2];
  const t0 = L[2];
  pose(s.mom, { sit: 1, lookY: 0.2 * Math.sin(t * 0.8) });
  pose(s.kid, { sit: 1, nod: -0.1 });
  const pointK = prog(t, t0 + 0.2, 0.5) * (1 - prog(t, at(2, "et nos"), 0.5));
  pose(s.director, { point: pointK, wave: 0, nod: Math.sin(t * 6) * 0.03 });
  s.director.root.rotation.y = lerp(-0.5, -1.9, pointK * 0.5);
  // tower floors light up with the cycle names
  const names = ["maternelle", "primaire", "collège", "lycée"];
  names.forEach((n, i) => {
    const tn = at(2, n, -0.05);
    const k = prog(t, tn, 0.35, E.out3);
    const fl = s.towerFloors[i];
    fl.children[0].material.emissiveIntensity = 0.45 * k;
    fl.position.y = i * 0.34 + 0.12 * Math.sin(Math.PI * clamp01((t - tn) / 0.45));
    setSprite(s.cycleLabels[i], popScale(t, tn, Infinity, 0.4));
  });
  s.tower.rotation.y = 0.35 * prog(t, at(2, "et nos"), 3.0, E.inOut2);
  if (s.doorGlow) s.doorGlow.material.opacity = 0.25 + 0.45 * prog(t, DEPART(3) - 0.6, 0.5);
}

function animInfra(t) {
  const s = S[3];
  const z = s.zones;
  // labels pop in sequence as the camera visits each room
  const keys = ["Visitez", "nos laboratoires", "la salle", "la cour", "et nos espaces"];
  s.zoneLabels.forEach((lb, i) => {
    const tin = at(3, keys[i], i === 0 ? 0.55 : 0.4);
    setSprite(lb, popScale(t, tin, Infinity, 0.4));
  });
  z.classe.kids.forEach((k, i) => pose(k, { sit: 1, wave: i === 1 ? 0.75 * prog(t, at(3, "Visitez", 0.9), 0.3) : 0, wavePhase: 0 }));
  pose(z.labo.kids[0], { hold: 0.8, nod: Math.sin(t * 3) * 0.05 });
  pose(z.info.kids[0], { sit: 1, hold: 0.9 });
  // playground: two kids pass the ball
  const [a, b] = z.cour.kids;
  const ph = (t * 1.3) % 2;
  const k = ph < 1 ? ph : 2 - ph;
  const ax = -0.3, az = 0.2, bx = 0.8, bz = -0.6;
  s.ball.position.set(2.9 + lerp(ax + 0.25, bx - 0.25, E.inOut2(k)), 0.03 + 0.14 + Math.sin(Math.PI * k) * 0.55, 2.9 + lerp(az, bz, E.inOut2(k)));
  pose(a, { hold: 0.6 * (1 - k), walk: t * 6, walkAmt: 0.15 });
  pose(b, { hold: 0.6 * k, walk: t * 6 + 1, walkAmt: 0.15 });
  pose(s.mom, { lookY: Math.sin(t * 0.7) * 0.4 });
  pose(s.kid, { point: prog(t, at(3, "la cour", 0.2), 0.4) * (1 - prog(t, at(3, "et nos espaces", 0.5), 0.4)) });
  if (s.doorGlow) s.doorGlow.material.opacity = 0.25 + 0.45 * prog(t, DEPART(4) - 0.6, 0.5);
}

function animOrganisation(t) {
  const s = S[4];
  pose(s.teacher, { point: 0.7 + 0.2 * Math.sin(t * 2), nod: Math.sin(t * 5) * 0.04 });
  s.pupils.forEach((k, i) => {
    const up = clamp01((Math.sin(t * 1.6 + i * 1.7) - 0.55) / 0.3);
    pose(k, { sit: 1, wave: 0.8 * up * prog(t, ARRIVE(4), 0.5), wavePhase: 0 });
  });
  // the four pillars orbit above the class
  const keys = ["Méthodes", "suivi", "encadrement", "communication"];
  const c = sp(4, -0.3, 3.4, -0.6);
  s.badges.forEach((b, i) => {
    const tin = at(4, keys[i], -0.05);
    const a = (i / 4) * Math.PI * 2 + t * 0.55;
    const r = 2.5;
    setSprite(b, popScale(t, tin, Infinity, 0.5), c.x + Math.cos(a) * r, c.y + Math.sin(a * 2) * 0.15, c.z + Math.sin(a) * r);
  });
  if (s.doorGlow) s.doorGlow.material.opacity = 0.25 + 0.45 * prog(t, DEPART(5) - 0.6, 0.5);
}

function animServices(t) {
  const s = S[5];
  pose(s.mom, { hold: 1, lookY: 0.1 });
  const kick = prog(t, at(5, "et découvrez", 1.2), 0.9, E.out2);
  pose(s.kid, { walk: kick * 4, walkAmt: kick > 0 && kick < 1 ? 0.6 : 0, point: 0 });
  s.ball.position.set(lerp(1.9, 2.55, kick), 0.03 + 0.17 + Math.sin(Math.PI * kick) * 0.3, lerp(2.0, 2.75, kick));
  const nk = [at(5, "Avec", 0.9), at(5, "suivez", 0.1), at(5, "suivez", 0.7)];
  const base = sp(5, -0.6, 0, -1.4);
  s.notifs.forEach((n, i) => {
    const pos = [V(1.45, 3.6, 0.2), V(1.6, 2.6, 0.5), V(1.35, 1.6, 0.85)][i];
    setSprite(n, popScale(t, nk[i], Infinity, 0.45), base.x + pos.x, base.y + pos.y + Math.sin(t * 2 + i) * 0.05, base.z + pos.z);
  });
  s.actLabels.forEach((lb, i) => setSprite(lb, popScale(t, at(5, "et découvrez", 0.7 + i * 0.25), Infinity, 0.4)));
  WORLD.appGlow.material.opacity = 0.5 * prog(t, at(5, "Avec", 0.5), 0.6) * (1 - prog(t, at(5, "et découvrez", 0.4), 0.6));
  if (s.doorGlow) s.doorGlow.material.opacity = 0.25 + 0.45 * prog(t, DEPART(6) - 0.6, 0.5);
}

let lastChecked = -1;
function animModalites(t) {
  const s = S[6];
  pose(s.mom, { sit: 1, lookY: -0.35 });
  pose(s.kid, { sit: 1, lookY: -0.2 });
  pose(s.advisor, { hold: 0.8, nod: Math.sin(t * 4) * 0.04 });
  const keys = ["Admission", "places", "frais", "documents", "constitution"];
  const n = keys.filter((k) => t >= at(6, k, 0.15)).length;
  if (n !== lastChecked) {
    s.checklist.userData.drawState(n);
    lastChecked = n;
  }
  // documents fly into the blue folder
  const fold = sp(6, 0.0, 0.83, -1.8);
  s.docs.forEach((d, i) => {
    const t0 = at(6, "documents", -0.2 + i * 0.22);
    const k = prog(t, t0, 0.75, E.inOut2);
    const from = sp(6, -2.1 + i * 0.15, 2.6 + i * 0.25, -0.2 + i * 0.1);
    d.visible = t >= t0 - 0.01;
    d.position.copy(from).lerp(fold, k);
    d.position.y += Math.sin(Math.PI * k) * 0.9 + i * 0.015 * k;
    d.rotation.set((1 - k) * 0.6, (1 - k) * (1.5 + i * 0.4), (1 - k) * 0.3);
  });
  const fk = prog(t, at(6, "constitution", 0.1), 0.4, E.outBack);
  s.folder.scale.setScalar(1 + 0.25 * fk * (1 - prog(t, at(6, "constitution", 0.6), 0.5)));
  if (s.doorGlow) s.doorGlow.material.opacity = 0.25 + 0.45 * prog(t, DEPART(7) - 0.6, 0.5);
}

function animConclusion(t) {
  const s = S[7];
  const t0 = L[7];
  const shake = prog(t, at(7, "nous finalisons", -0.3), 0.4) * (1 - prog(t, L[8] + 0.4, 0.4));
  const pump = Math.sin(t * 12) * 0.12 * shake;
  pose(s.mom, { shake, nod: pump * 0.3 });
  pose(s.advisor, { shake, nod: pump * 0.3 });
  s.mom.arms[1].shoulder.rotation.x += pump;
  s.advisor.arms[1].shoulder.rotation.x += pump;
  const cheer = prog(t, at(7, "nous finalisons", 0.6), 0.4);
  pose(s.kid, { cheer, wavePhase: t * 9 });
  s.kid.root.position.y = 0.03 + Math.abs(Math.sin(t * 7)) * 0.18 * cheer;
  const [q, ok, heart] = s.bubbles;
  setSprite(q, popScale(t, t0 + 0.2, at(7, "et si", 0.2)), s.pos.x + 0.6, s.pos.y + 2.7, s.pos.z - 0.2);
  setSprite(ok, popScale(t, at(7, "et si", 0.0), at(7, "nous finalisons", 0.4)), s.pos.x - 0.6, s.pos.y + 2.75, s.pos.z - 0.8);
  setSprite(heart, popScale(t, at(7, "nous finalisons", 0.9), L[8] + 0.8), s.pos.x + 1.3, s.pos.y + 2.4, s.pos.z + 0.5);
  setSprite(WORLD.doneCard, popScale(t, at(7, "nous finalisons", 0.5), L[8] + 1.0, 0.5), s.pos.x, s.pos.y + 3.5, s.pos.z - 0.5);
  s.balloons.forEach((b, i) => {
    b.position.y = 0.03 + 1.6 + Math.sin(t * 1.4 + i) * 0.12;
  });
  // confetti
  const ck = clamp01((t - at(7, "nous finalisons", 0.5)) / 2.6);
  WORLD.confetti.visible = ck > 0 && ck < 1;
  if (WORLD.confetti.visible) {
    const pos = WORLD.confetti.geometry.attributes.position;
    const vel = WORLD.confetti.userData.vel;
    const tt = ck * 2.6;
    for (let i = 0; i < vel.length; i++) {
      const [vx, vy, vz] = vel[i];
      pos.setXYZ(i, s.pos.x + vx * tt, s.pos.y + 2.4 + vy * tt - 2.4 * tt * tt, s.pos.z - 0.4 + vz * tt);
    }
    pos.needsUpdate = true;
    WORLD.confetti.material.opacity = 1 - E.in2(ck);
  }
}

// ── Main entry ──────────────────────────────────────────────────────────────
let camTrack = null;
const orbPos = new THREE.Vector3();

export function setupAnim() {
  camTrack = camKeys();
}

export function applyTime(t, eng) {
  // rest poses
  WORLD.people.forEach((p) => pose(p, p.rest || {}));
  // family copies visibility
  S.forEach((s, i) => {
    const v = famVisible(i, t);
    if (s.mom) s.mom.root.visible = v;
    if (s.kid) s.kid.root.visible = v;
  });
  animFacade(t);
  animAccueil(t);
  animPresentation(t);
  animInfra(t);
  animOrganisation(t);
  animServices(t);
  animModalites(t);
  animConclusion(t);

  // bridges
  WORLD.bridges.forEach((b, i) => {
    const k = bridgeProgress(i, t);
    const cta = prog(t, L[8] - 0.4, 1.2);
    const kk = Math.max(k, cta);
    b.core.geometry.setDrawRange(0, Math.floor(b.total * kk / 6) * 6);
    b.halo.geometry.setDrawRange(0, Math.floor(b.totalHalo * kk / 6) * 6);
    b.core.visible = b.halo.visible = kk > 0.001;
  });
  // orb
  const os = orbAt(t, orbPos);
  WORLD.orb.group.position.copy(orbPos);
  WORLD.orb.group.scale.setScalar(Math.max(0.001, os));
  WORLD.orb.glow.material.opacity = 0.75 + 0.25 * Math.sin(t * 5);
  // sun
  WORLD.sun.rays.material.rotation = t * 0.12;
  const flare = prog(t, L[8] + 0.6, 1.2);
  WORLD.sun.glow.scale.setScalar(13 * (1 + 0.25 * flare + 0.04 * Math.sin(t * 2)));
  // clouds drift
  WORLD.clouds.forEach((c, i) => {
    c.position.x = c.userData.x0 + Math.sin(t * 0.08 + i) * 1.2;
  });
  WORLD.sparkles.material.opacity = 0.55 + 0.25 * Math.sin(t * 3);
  // camera
  const [x, y, z, vh, az] = camTrack(t);
  eng.setCamera({ x, y, z, vh, az });
}
