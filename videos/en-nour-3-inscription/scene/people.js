// Low-poly characters with a small seek-safe pose API.
import * as THREE from "three";
import { C, mat, geoCap, geoSph, geoRBox, geoCyl, rbox, cyl, sph, group } from "./lib.js";

function capsule(parent, r, len, color, x, y, z) {
  const m = new THREE.Mesh(geoCap(r, len), mat(color));
  m.position.set(x, y, z);
  m.castShadow = true;
  m.receiveShadow = true;
  parent.add(m);
  return m;
}

function hairCap(parent, r, color, y, z = -0.015, theta = 0.56) {
  const g = new THREE.SphereGeometry(r, 18, 12, 0, Math.PI * 2, 0, Math.PI * theta);
  const m = new THREE.Mesh(g, mat(color));
  m.position.set(0, y, z);
  m.rotation.x = -0.32;
  m.castShadow = true;
  parent.add(m);
  return m;
}

/**
 * person({ skin, top, bottom, shoes, hair, hairStyle, scarf, kid, scale, sleeves, glasses, backpack, blazer, badge })
 * Root origin = between the feet, facing +Z.
 */
export function person(o = {}) {
  const skin = o.skin ?? 0xd9a07a;
  const top = o.top ?? C.blue;
  const bottom = o.bottom ?? C.ink;
  const shoes = o.shoes ?? 0x3b3f47;
  const hair = o.hair ?? 0x2b1e16;
  const root = new THREE.Group();
  const body = group(root); // bob / sit offset
  const P = { root, body, o };

  // legs (thigh + shin)
  P.legs = [-1, 1].map((s) => {
    const thigh = group(body, s * 0.1, 0.86, 0);
    capsule(thigh, 0.085, 0.3, bottom, 0, -0.2, 0);
    const knee = group(thigh, 0, -0.42, 0);
    capsule(knee, 0.075, 0.28, bottom, 0, -0.18, 0);
    rbox(knee, 0.15, 0.1, 0.27, shoes, 0, -0.43, 0.045, 0.04);
    return { thigh, knee };
  });

  // torso
  const torso = group(body, 0, 0.82, 0);
  P.torso = torso;
  rbox(torso, 0.46, 0.62, 0.29, top, 0, 0, 0, 0.12);
  if (o.tunic) {
    const tun = new THREE.Mesh(geoCyl(0.24, 0.3, 0.34, 18), mat(top));
    tun.position.set(0, 0.02, 0);
    tun.castShadow = true;
    torso.add(tun);
  }
  if (o.blazer) {
    rbox(torso, 0.13, 0.36, 0.04, C.white, 0, 0.24, 0.135, 0.02);
    if (o.badge !== false) rbox(torso, 0.08, 0.05, 0.03, C.sun, 0.12, 0.42, 0.15, 0.01);
  }
  if (o.collar) rbox(torso, 0.3, 0.06, 0.3, o.collar, 0, 0.56, 0, 0.03);
  if (o.backpack) {
    rbox(torso, 0.38, 0.44, 0.17, o.backpack, 0, 0.1, -0.22, 0.07);
    rbox(torso, 0.26, 0.14, 0.06, o.backpackPocket ?? C.sunDeep, 0, 0.12, -0.32, 0.03);
  }
  cyl(torso, 0.06, 0.07, 0.1, skin, 0, 0.6, 0);

  // arms (upper + forearm)
  const sleeve = o.sleeves === "short" ? skin : top;
  P.arms = [-1, 1].map((s) => {
    const shoulder = group(torso, s * 0.29, 0.54, 0);
    capsule(shoulder, 0.07, 0.2, top, 0, -0.16, 0);
    const elbow = group(shoulder, 0, -0.32, 0);
    capsule(elbow, 0.064, 0.17, sleeve, 0, -0.13, 0);
    sph(elbow, 0.068, skin, 0, -0.29, 0);
    return { shoulder, elbow };
  });

  // head
  const head = group(torso, 0, 0.84, 0);
  P.head = head;
  if (o.kid) head.scale.setScalar(1.22);
  const style = o.hairStyle ?? "short";
  if (style === "scarf") {
    const sc = o.scarf ?? C.sky;
    sph(head, 0.235, sc, 0, 0.0, -0.015);
    sph(head, 0.183, skin, 0, -0.018, 0.065);
    const drape = new THREE.Mesh(geoCyl(0.15, 0.27, 0.26, 20), mat(sc));
    drape.position.set(0, -0.2, -0.01);
    drape.castShadow = true;
    head.add(drape);
  } else {
    sph(head, 0.21, skin, 0, 0, 0);
    hairCap(head, 0.226, hair, 0.012);
    if (style === "bun") sph(head, 0.1, hair, 0, 0.17, -0.15);
    if (style === "long") rbox(head, 0.4, 0.42, 0.12, hair, 0, -0.34, -0.12, 0.06);
    if (style === "ponytail") {
      const pt = capsule(head, 0.07, 0.22, hair, 0, -0.08, -0.25);
      pt.rotation.x = 0.5;
      sph(head, 0.05, o.tie ?? C.coral, 0, 0.06, -0.21);
    }
    if (style === "pigtails")
      [-1, 1].forEach((s) => {
        sph(head, 0.085, hair, s * 0.22, -0.02, -0.06);
        sph(head, 0.035, o.tie ?? C.coral, s * 0.2, 0.05, -0.04);
      });
  }
  // face
  const faceZ = style === "scarf" ? 0.232 : 0.19;
  const faceY = style === "scarf" ? 0.0 : 0.02;
  [-1, 1].forEach((s) => sph(head, 0.022, 0x1f2430, s * 0.068, faceY, faceZ, { ws: 8, hs: 6, shadow: false }));
  [-1, 1].forEach((s) =>
    sph(head, 0.03, 0xf0948c, s * 0.115, faceY - 0.06, faceZ - 0.03, { ws: 8, hs: 6, shadow: false })
  );
  if (o.glasses) {
    [-1, 1].forEach((s) => {
      const ring = new THREE.Mesh(new THREE.TorusGeometry(0.048, 0.011, 6, 16), mat(0x22262e));
      ring.position.set(s * 0.068, faceY, faceZ + 0.012);
      head.add(ring);
    });
  }
  if (o.beard) {
    const b = new THREE.Mesh(new THREE.SphereGeometry(0.205, 16, 10, 0, Math.PI * 2, Math.PI * 0.55, Math.PI * 0.45), mat(hair));
    b.position.set(0, 0.005, 0.012);
    head.add(b);
  }

  root.scale.setScalar(o.scale ?? (o.kid ? 0.62 : 1));
  P.baseScale = root.scale.x;
  return P;
}

/**
 * Seek-safe pose. Every field is a plain number; call once per frame.
 * walk: phase (radians), walkAmt 0..1, sit 0..1, wave 0..1 (right arm), wavePhase,
 * cheer 0..1, point 0..1, hold 0..1 (forearms forward), shake 0..1 (right hand forward),
 * nod (radians), lookY (head yaw)
 */
export function pose(P, s = {}) {
  const walkAmt = s.walkAmt ?? 0;
  const ph = s.walk ?? 0;
  const sit = s.sit ?? 0;
  const [L, R] = P.legs;
  const [AL, AR] = P.arms;
  const sw = Math.sin(ph) * 0.55 * walkAmt;
  L.thigh.rotation.x = sw - (Math.PI / 2) * sit;
  R.thigh.rotation.x = -sw - (Math.PI / 2) * sit;
  L.knee.rotation.x = Math.max(0, -Math.sin(ph)) * 0.7 * walkAmt + (Math.PI / 2) * sit;
  R.knee.rotation.x = Math.max(0, Math.sin(ph)) * 0.7 * walkAmt + (Math.PI / 2) * sit;
  P.body.position.y = Math.abs(Math.cos(ph)) * 0.035 * walkAmt - 0.4 * sit;

  // arms
  const armSw = Math.sin(ph) * 0.45 * walkAmt;
  const hold = s.hold ?? 0;
  const point = s.point ?? 0;
  const cheer = s.cheer ?? 0;
  const wave = s.wave ?? 0;
  const shake = s.shake ?? 0;
  AL.shoulder.rotation.set(-armSw - 0.35 * hold - 0.2 * sit, 0, -0.08 - 2.75 * cheer);
  AL.elbow.rotation.set(-1.15 * hold - 0.3 * sit, 0, 0);
  AR.shoulder.rotation.set(
    armSw - 0.35 * hold - 1.25 * point - 0.75 * shake - 0.2 * sit,
    0,
    0.08 + 2.55 * wave + 2.75 * cheer + 0.25 * point
  );
  AR.elbow.rotation.set(-1.15 * hold - 0.35 * shake - 0.3 * sit - 0.2 * point, 0, wave * Math.sin((s.wavePhase ?? 0) * 1.0) * 0.55);
  if (cheer > 0) {
    AL.elbow.rotation.z = -Math.sin((s.wavePhase ?? 0)) * 0.25 * cheer;
    AR.elbow.rotation.z = Math.sin((s.wavePhase ?? 0)) * 0.25 * cheer;
  }
  P.head.rotation.set(s.nod ?? 0, s.lookY ?? 0, 0);
  P.torso.rotation.y = s.twist ?? 0;
}
