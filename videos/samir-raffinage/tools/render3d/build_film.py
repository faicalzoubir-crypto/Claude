#!/usr/bin/env python3
"""Build film.html: the refinery scene of refinery/samir-3d/samir-refinery.html, driven by time.

The interactive page's module is reused as is up to its flows (materials, units, sea, flare, sky,
bloom); its UI parts (labels, picking, orbit loop) are dropped and replaced by window.FILM:

  FILM.setShot(name)   picks a shot from SHOTS (camera keyframes, light mode, fov)
  FILM.frame(t)        renders time t (s) of that shot; returns {jpeg, anchors}
                       anchors = named 3D points projected to 1080x1920 px

  python3 tools/render3d/build_film.py   (then node tools/render3d/render.cjs)
"""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parents[3] / "refinery/samir-3d/samir-refinery.html"
src = SRC.read_text()
mod = src[src.index('<script type="module">') + len('<script type="module">'): src.rindex("</script>")]
imports = mod[: mod.index("const REF = window.REF;")]
body = mod[mod.index("function start() {") + len("function start() {"): mod.index("// ---------- selection ring ----------")]
body = body.replace("REF.STREAM_TYPES[f.type].color", "STREAM_COLORS[f.type]")
body = body.replace("antialias: false", "antialias: false, preserveDrawingBuffer: true")
assert "REF." not in body, re.findall(r"REF\.\w+", body)

FILM = r"""
// ---------- film: light modes, shots, frame(t) ----------
lampPtsMesh: {
}
MODES.off = { ...MODES.dusk, warmI: 0, emissiveI: 0, lamp: [0, 0, 0], win: [0.5, 0.42, 0.3], bloom: 0.6, flareI: 0 };
function applyMode(name) {
  const m = MODES[name]; mode = m;
  skyU.top.value.set(m.top); skyU.horizon.value.set(m.horizon); skyU.bottom.value.set(m.bottom); skyU.glow.value.set(m.glow); skyU.sunDir.value.set(...m.sunDir).normalize();
  scene.fog.color.set(m.fog); scene.fog.near = m.fogNear; scene.fog.far = m.fogFar;
  hemi.color.set(m.hemiSky); hemi.groundColor.set(m.hemiGround); hemi.intensity = m.hemiI;
  sun.color.set(m.sunColor); sun.intensity = m.sunI; sun.position.set(...m.sunPos);
  warm.forEach((l) => (l.intensity = m.warmI));
  lampMat.color.setRGB(...m.lamp); lampMat.visible = name !== 'off';
  windowMat.color.setRGB(...m.win);
  fireMat.color.setRGB(...(name === 'off' ? [0.04, 0.03, 0.02] : [5, 1.6, 0.3]));
  flame.visible = name !== 'off'; streamGroup.visible = name !== 'off' && SHOT.flows !== false;
  cityMesh.visible = m.city; bloom.strength = m.bloom; renderer.toneMappingExposure = m.exposure;
  seaMat.color.set(m.sea);
  for (const mat of stdMats) { mat.envMapIntensity = m.envI; mat.emissive.set(m.emissive); mat.emissiveIntensity = m.emissiveI; }
  flows.forEach((f) => { f.mat.color.copy(f.base).multiplyScalar(1.6); f.mat.opacity = 1; });
  updateEnv();
}

const W = 1080, H = 1920;
renderer.setPixelRatio(1);
renderer.setSize(W, H, false);
composer.setSize(W, H);
camera.aspect = W / H;

const smoother = (x) => x * x * x * (x * (x * 6 - 15) + 10);
let SHOT = null;
function setShot(name) {
  SHOT = window.SHOTS[name];
  camera.fov = SHOT.fov || 50; camera.updateProjectionMatrix();
  applyMode(SHOT.mode || 'dusk');
  if (SHOT.emphasize) flows.forEach((f) => { f.mat.opacity = SHOT.emphasize.some((u) => f.units.includes(u)) ? 1 : 0.18; });
}
function camAt(t) {
  const K = SHOT.keys;
  if (t <= K[0][0]) return [V(...K[0][1]), V(...K[0][2])];
  for (let i = 0; i < K.length - 1; i++) {
    const [t0, p0, q0] = K[i], [t1, p1, q1] = K[i + 1];
    if (t <= t1) {
      const k = smoother((t - t0) / (t1 - t0));
      return [V(...p0).lerp(V(...p1), k), V(...q0).lerp(V(...q1), k)];
    }
  }
  const L = K[K.length - 1];
  return [V(...L[1]), V(...L[2])];
}
const tmpP = V();
function filmFrame(t) {
  const [p, q] = camAt(t);
  camera.position.copy(p); camera.lookAt(q); camera.updateMatrixWorld();
  const T = (SHOT.clock0 || 0) + t;
  seaMat.normalMap.offset.set(T * 0.0035, T * 0.005);
  const fl = 1 + 0.22 * Math.sin(T * 9.3) + 0.12 * Math.sin(T * 23.1);
  flameOuter.scale.set(1, fl, 1); flameInner.scale.set(1, 0.9 + 0.3 * Math.sin(T * 13.7 + 1), 1);
  flame.rotation.z = 0.12 * Math.sin(T * 1.3); flameGlow.material.opacity = 0.75 + 0.2 * Math.sin(T * 7);
  flareLight.intensity = mode.flareI * (0.85 + 0.15 * Math.sin(T * 11));
  for (const f of flows) f.tex.offset.x = -0.55 * T;
  composer.render();
  const anchors = {};
  for (const [k, xyz] of Object.entries(SHOT.anchors || {})) {
    tmpP.set(...xyz).project(camera);
    anchors[k] = [Math.round((tmpP.x * 0.5 + 0.5) * W * 10) / 10, Math.round((-tmpP.y * 0.5 + 0.5) * H * 10) / 10, tmpP.z < 1 ? 1 : 0];
  }
  return { jpeg: canvas.toDataURL('image/jpeg', 0.93), anchors };
}
function project(t) {
  const [p, q] = camAt(t);
  camera.position.copy(p); camera.lookAt(q); camera.updateMatrixWorld();
  const anchors = {};
  for (const [k, xyz] of Object.entries(SHOT.anchors || {})) {
    tmpP.set(...xyz).project(camera);
    anchors[k] = [Math.round((tmpP.x * 0.5 + 0.5) * W * 10) / 10, Math.round((-tmpP.y * 0.5 + 0.5) * H * 10) / 10, tmpP.z < 1 ? 1 : 0];
  }
  return anchors;
}
window.FILM = { setShot, frame: filmFrame, project, ready: true };
"""
FILM = FILM.replace("lampPtsMesh: {\n}\n", "")

STREAMS = """const STREAM_COLORS = { crude: '#C98B5A', gas: '#6FB6E8', naphtha: '#F5D65B', kero: '#B99CF0', diesel: '#93CDBB', heavy: '#D9736B', h2: '#F29BC0', h2s: '#C6E04A', product: '#E8EEEC' };
"""

html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>film</title>
<style>html,body{{margin:0;background:#000}} canvas{{display:block;width:1080px;height:1920px}}</style>
<script type="importmap">
{{ "imports": {{ "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
  "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/" }} }}
</script>
<script src="shots.js"></script>
</head><body>
<canvas id="gl" width="1080" height="1920"></canvas>
<script type="module">
{imports}
start();
function start() {{
{STREAMS}{body}{FILM}
}}
</script>
</body></html>
"""
(HERE / "film.html").write_text(html)
print("film.html", len(html), "bytes from", SRC.name)
