// Entry: overlay GSAP timeline + Three.js world, both driven by HyperFrames time.
import { createEngine } from "./engine.js";
import { buildWorld } from "./world.js";
import { setupAnim, applyTime } from "./anim.js";
import { L, TOTAL, STEPS, CAPTIONS, SCENE_START, SCENE_END, at } from "./timing.js";

// ── Overlay timeline (HTML text, chips, captions, CTA) ─────────────────────
export function boot() {
const tl = gsap.timeline({ paused: true });
const $ = (id) => document.getElementById(id);

// hook
["hl-1", "hl-2", "hl-3"].forEach((id, k) => {
  tl.fromTo($(id), { y: 70, opacity: 0 }, { y: 0, opacity: 1, duration: 0.6, ease: "power3.out" }, 0.2 + k * 0.22);
});
tl.to(["#hl-1", "#hl-2", "#hl-3"], { y: -50, opacity: 0, duration: 0.4, ease: "power2.in", stagger: 0.05 }, 2.95);
tl.fromTo("#hook-logo", { scale: 0.6, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.7, ease: "back.out(1.6)" }, at(0, "À Ennour", -0.25));
tl.fromTo("#hook-sub", { y: 24, opacity: 0 }, { y: 0, opacity: 1, duration: 0.45, ease: "power2.out" }, at(0, "vous guide", -0.2));
tl.to("#hook-brand", { y: -40, opacity: 0, duration: 0.4, ease: "power2.in" }, SCENE_END(0) - 0.42);

// steps
for (let i = 1; i <= 7; i++) {
  const st = STEPS[i];
  const s0 = SCENE_START(i), s1 = SCENE_END(i);
  tl.fromTo(`#s${i}-badge`, { scale: 0.5, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.45, ease: "back.out(2)" }, s0 + 0.05);
  tl.fromTo(`#s${i}-dots`, { x: -20, opacity: 0 }, { x: 0, opacity: 1, duration: 0.4, ease: "power2.out" }, s0 + 0.15);
  tl.fromTo(`#s${i}-title`, { y: 54, opacity: 0 }, { y: 0, opacity: 1, duration: 0.55, ease: "power3.out" }, s0 + 0.12);
  st.chips.forEach(([, anchor], k) => {
    const tc = Math.max(s0 + 0.45 + k * 0.08, at(i, anchor, -0.1));
    tl.fromTo(`#s${i}-chip${k}`, { scale: 0.6, opacity: 0, y: 10 }, { scale: 1, opacity: 1, y: 0, duration: 0.42, ease: "back.out(1.8)" }, tc);
    if (st.checklist) {
      const tick = tc + 0.25;
      tl.to(`#s${i}-chip${k} .box`, { backgroundColor: "#2F8F4E", borderColor: "#2F8F4E", duration: 0.2 }, tick);
      tl.to(`#s${i}-chip${k} path`, { strokeDashoffset: 0, duration: 0.3, ease: "power2.out" }, tick + 0.05);
    }
  });
  tl.to(`#s${i}-inner`, { y: -36, opacity: 0, duration: 0.36, ease: "power2.in" }, s1 - 0.4);
}

// captions
CAPTIONS.forEach((line, i) =>
  line.forEach(([, anchor], k) => {
    tl.fromTo(`#capp-${i}-${k}`, { y: 18, opacity: 0 }, { y: 0, opacity: 1, duration: 0.2, ease: "power2.out" }, at(i, anchor, -0.05));
  })
);

// CTA
const c0 = SCENE_START(8);
tl.fromTo("#cta-card", { y: -70, opacity: 0 }, { y: 0, opacity: 1, duration: 0.75, ease: "power3.out" }, c0 + 0.7);
tl.fromTo("#cta-logo", { scale: 0.75, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.7, ease: "back.out(1.5)" }, c0 + 0.85);
tl.fromTo("#cta-cycles", { y: 16, opacity: 0 }, { y: 0, opacity: 1, duration: 0.4 }, c0 + 1.3);
const tb = at(8, "Réservez", -0.15);
tl.fromTo("#cta-button", { scale: 0.3, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.55, ease: "back.out(2.2)" }, tb);
tl.fromTo("#cta-sub", { y: 16, opacity: 0 }, { y: 0, opacity: 1, duration: 0.4 }, tb + 0.35);
tl.to("#cta-button", { scale: 1.07, duration: 0.28, ease: "power2.out", yoyo: true, repeat: 3 }, tb + 1.1);
tl.set({}, {}, TOTAL);
return tl;
}

// ── 3D world ────────────────────────────────────────────────────────────────
const eng = createEngine(document.getElementById("world"));
let ready = false;
let pending = 0;

async function build() {
  await Promise.all([
    document.fonts.load('800 60px "Baloo 2"'),
    document.fonts.load('700 60px "Baloo 2"'),
    document.fonts.load('700 40px "Quicksand"'),
  ]);
  await buildWorld(eng.scene);
  setupAnim();
  ready = true;
  renderAt(window.__hfThreeTime ?? pending);
}
window.__hf = window.__hf || {};
window.__hf.buildReady = window.__hf.buildReady || {};
window.__hf.buildReady["world"] = build();

function renderAt(t) {
  pending = t;
  if (!ready) return;
  applyTime(t, eng);
  eng.renderer.render(eng.scene, eng.camera);
}
window.addEventListener("hf-seek", (e) => renderAt(e.detail.time));
