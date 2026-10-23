/* Shared stage for en-nour-3-communique: the iPad, its camera, the haptic taps and the value chips.
 *
 * Every scene draws the same device at the same place and calls STAGE.render(els, t) from one
 * linear clock tween, so each frame is a pure function of film time t (seconds from the start of
 * the whole film): seek-safe, identical in preview and render, continuous across scene seams.
 *
 * Coordinates of taps and chips are in source pixels of the recording (1080 x 1554).
 */
(function () {
  if (window.STAGE) return;

  const SRC = { w: 1080, h: 1554 };
  const SCR = { x: 180, y: 456, w: 720, h: 1036 }; // the iPad screen in the 1080 x 1920 frame
  const K = SCR.w / SRC.w; // 2/3: the whole recording fits the screen at z = 1
  const ease = (name) => gsap.parseEase(name);
  const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));
  const lerp = (a, b, p) => a + (b - a) * p;

  // Camera: arrive at {fx, fy, z} at t1, moving from the previous key since t0 (t0 = t1 is a cut).
  // fx, fy: the source point held at the centre of the screen; z: zoom over the whole screen.
  const CAM = [
    { t1: 0, fx: 250, fy: 385, z: 2.25 },
    { t0: 0.3, t1: 0.42, fx: 250, fy: 385, z: 2.4, ease: "power4.out" }, // the card lands
    { t0: 3.333, t1: 4.533, fx: 540, fy: 777, z: 1, ease: "power2.inOut" }, // rewind: pull back
    // s1 ouvrir
    { t0: 4.85, t1: 5.4, fx: 850, fy: 1100, z: 1.6 },
    { t0: 5.85, t1: 6.4, fx: 820, fy: 1385, z: 2.3 },
    { t0: 6.8, t1: 7.35, fx: 540, fy: 777, z: 1 },
    { t0: 7.85, t1: 8.4, fx: 990, fy: 1480, z: 2.2 },
    { t0: 8.62, t1: 8.8, fx: 1026, fy: 1520, z: 4.2, ease: "power3.in" }, // zoom through the +
    { t0: 8.8, t1: 9.25, fx: 395, fy: 700, z: 1.45, ease: "expo.out" }, // the form lands and settles
    // s2 classes
    { t0: 9.62, t1: 10.17, fx: 255, fy: 860, z: 2.3 },
    { t0: 12.25, t1: 12.667, fx: 255, fy: 860, z: 1.6, ease: "power3.in" }, // zoom pulse out…
    // s3 type
    { t0: 12.667, t1: 13.15, fx: 255, fy: 870, z: 2.3, ease: "expo.out" }, // …and back in
    // s4 matière
    { t0: 15.35, t1: 15.85, fx: 245, fy: 840, z: 2.4 },
    // s5 date: whip right onto the calendar
    { t0: 17.8, t1: 18.2, fx: 730, fy: 880, z: 1.55 },
    { t0: 18.8, t1: 19.3, fx: 880, fy: 860, z: 1.9 },
    // s6 titre et message
    { t0: 21.25, t1: 21.85, fx: 265, fy: 940, z: 2.2 },
    { t0: 22.3, t1: 22.75, fx: 265, fy: 600, z: 2.2 }, // follows the page up as the keyboard rises
    { t0: 25.85, t1: 26.35, fx: 560, fy: 700, z: 1.25 },
    // s7 envoyer: the whole filled form, then « Envoyer »
    { t0: 26.75, t1: 27.75, fx: 540, fy: 777, z: 1, ease: "power2.inOut" },
    { t0: 28.15, t1: 29.0, fx: 990, fy: 1406, z: 2.2, ease: "power3.inOut" },
    // s8 résultat: cut to the published card, then the whole card
    { t0: 29.333, t1: 29.333, fx: 250, fy: 385, z: 2.4 },
    { t0: 30.0, t1: 30.55, fx: 540, fy: 400, z: 1.1 },
    { t0: 32.25, t1: 32.85, fx: 250, fy: 385, z: 2.4 }, // every value now in the card: read it
  ];

  // Real taps of the recording, at their film time (computed from source time and clip rate).
  // camT: read the position with the camera of that instant (the tap that cuts to the next scene).
  const TAPS = [
    { t: 4.787, x: 1045, y: 235 }, // ☰
    { t: 6.653, x: 760, y: 1400 }, // Communiqué évaluatif
    { t: 8.62, x: 1026, y: 1520 }, // +
    { t: 9.523, x: 300, y: 555 }, // Classes
    { t: 10.938, x: 120, y: 980 }, // T.C.S.F2
    { t: 13.337, x: 300, y: 668 }, // Type
    { t: 14.667, x: 105, y: 790 }, // DS
    { t: 16.0, x: 300, y: 780 }, // Matière
    { t: 17.333, x: 115, y: 916 }, // SVT
    { t: 18.659, x: 560, y: 886 }, // Date
    { t: 19.652, x: 922, y: 704 }, // mois suivant
    { t: 20.66, x: 840, y: 830 }, // 4
    { t: 22.004, x: 300, y: 985 }, // Titre
    { t: 24.033, x: 300, y: 700 }, // Description
    { t: 25.033, x: 300, y: 700 }, // Description (menu)
    { t: 25.454, x: 80, y: 700 }, // Paste
    { t: 29.333, x: 990, y: 1406, camT: 29.3 }, // Envoyer
  ];

  // The values the teacher sets: each lifts off the tapped control as an amber chip, flies to the
  // row under the title, and in the result flies into the published card.
  const ROW = { y: 352, h: 48 };
  const PAY0 = 30.6; // first chip leaves the row for the card
  const CHIPS = [
    { id: "c1", text: "T.C.S.F1 · T.C.S.F2", t: 10.97, x: 120, y: 980, slot: { x: 80, w: 300 }, card: { x: 135, y: 440 } },
    { id: "c2", text: "DS", t: 14.7, x: 105, y: 790, slot: { x: 392, w: 80 }, card: { x: 56, y: 324 } },
    { id: "c3", text: "SVT", t: 17.36, x: 115, y: 916, slot: { x: 484, w: 100 }, card: { x: 1024, y: 378 } },
    { id: "c4", text: "04/11/2026", t: 20.69, x: 840, y: 830, slot: { x: 596, w: 210 }, card: { x: 160, y: 412 } },
    { id: "c5", text: "Message", t: 25.9, x: 300, y: 700, slot: { x: 818, w: 160 }, card: { x: 420, y: 368 } },
  ];
  const POP = 0.18, FLY = 0.42, SETTLE = 0.25, PAY_FLY = 0.5, PAY_GAP = 0.25;
  CHIPS.forEach((c, i) => {
    c.land = c.t + POP + FLY;
    c.pay = PAY0 + i * PAY_GAP;
    c.payLand = c.pay + PAY_FLY;
  });

  // Haptic hits: every tap, plus the hook's landing card and each chip landing in the result.
  const HITS = TAPS.map((p) => ({ ...p, dot: true }))
    .concat([{ t: 0.333, x: 250, y: 385, dot: false }])
    .concat(CHIPS.map((c) => ({ t: c.payLand, x: c.card.x, y: c.card.y, dot: false, soft: true })))
    .sort((a, b) => a.t - b.t);

  function camAt(t) {
    let st = { fx: CAM[0].fx, fy: CAM[0].fy, lz: Math.log(CAM[0].z) };
    for (const k of CAM) {
      const t1 = k.t1, t0 = k.t0 === undefined ? t1 : k.t0;
      const to = { fx: k.fx, fy: k.fy, lz: Math.log(k.z) };
      if (t >= t1) { st = to; continue; }
      if (t > t0) {
        const p = ease(k.ease || "power3.inOut")((t - t0) / (t1 - t0));
        return { fx: lerp(st.fx, to.fx, p), fy: lerp(st.fy, to.fy, p), z: Math.exp(lerp(st.lz, to.lz, p)) };
      }
      break;
    }
    return { fx: st.fx, fy: st.fy, z: Math.exp(st.lz) };
  }

  // Transform of the camera layer (origin 0 0) inside the screen, clamped to the recording's edges.
  function xform(t) {
    const c = camAt(t), s = K * c.z;
    return {
      s,
      x: clamp(SCR.w / 2 - c.fx * s, SCR.w - SRC.w * s, 0),
      y: clamp(SCR.h / 2 - c.fy * s, SCR.h - SRC.h * s, 0),
    };
  }
  function screenPt(t, sx, sy) {
    const f = xform(t);
    return { x: f.x + sx * f.s, y: f.y + sy * f.s };
  }
  function framePt(t, sx, sy) {
    const p = screenPt(t, sx, sy);
    return { x: SCR.x + p.x, y: SCR.y + p.y };
  }

  // Envelopes of one hit, dt = seconds since the tap.
  function dotAt(dt) {
    if (dt < -0.14 || dt > 0.46) return null;
    if (dt < -0.02) { const p = ease("power2.out")((dt + 0.14) / 0.12); return { o: p, s: lerp(1.3, 1, p) }; }
    if (dt < 0) return { o: 1, s: 1 };
    if (dt < 0.06) return { o: 1, s: lerp(1, 0.78, ease("power2.out")(dt / 0.06)) };
    if (dt < 0.3) return { o: 1, s: lerp(0.78, 1, ease("back.out(2)")(Math.min(1, (dt - 0.06) / 0.22))) };
    const p = ease("power2.in")((dt - 0.3) / 0.16);
    return { o: 1 - p, s: lerp(1, 0.9, p) };
  }
  function ringAt(dt, soft) {
    if (dt < 0 || dt > 0.38) return null;
    const p = dt / 0.38;
    return { o: (soft ? 0.6 : 0.9) * (1 - ease("power1.out")(p)), s: lerp(1, soft ? 1.9 : 2.4, ease("expo.out")(p)) };
  }
  function pressAt(dt, soft) {
    const d = soft ? 0.985 : 0.965;
    if (dt < 0 || dt > 0.52) return 1;
    if (dt < 0.07) return lerp(1, d, ease("power2.out")(dt / 0.07));
    return lerp(d, 1, ease("elastic.out(1,0.45)")((dt - 0.07) / 0.45));
  }
  const SHAKE = [0, -6, 5, -3, 1.5, 0];
  function shakeAt(dt, soft) {
    if (dt < 0 || dt >= 0.2) return 0;
    const f = (dt / 0.2) * (SHAKE.length - 1), i = Math.floor(f);
    return lerp(SHAKE[i], SHAKE[i + 1], f - i) * (soft ? 0.5 : 1);
  }

  function chipState(c, t) {
    if (t < c.t || t >= c.payLand) return null;
    const slotC = { x: c.slot.x + c.slot.w / 2, y: ROW.y + ROW.h / 2 };
    let x = slotC.x, y = slotC.y, s = 1, o = 1, blur = 0;
    if (t < c.t + POP) {
      const st = framePt(c.t, c.x, c.y), p = (t - c.t) / POP;
      x = st.x; y = st.y; s = lerp(0.35, 1, ease("back.out(1.7)")(p)); o = Math.min(1, p * 2);
    } else if (t < c.land) {
      const st = framePt(c.t, c.x, c.y), p = ease("power3.inOut")((t - c.t - POP) / FLY);
      x = lerp(st.x, slotC.x, p); y = lerp(st.y, slotC.y, p); s = lerp(1, 1.08, p);
      blur = 6 * Math.sin(Math.PI * p); // motion blur peaking mid-flight
    } else if (t < c.land + SETTLE) {
      s = lerp(1.08, 1, ease("back.out(2.5)")((t - c.land) / SETTLE));
    }
    if (t >= c.pay) {
      const end = framePt(c.pay, c.card.x, c.card.y), p = ease("power3.inOut")((t - c.pay) / PAY_FLY);
      x = lerp(slotC.x, end.x, p); y = lerp(slotC.y, end.y, p); s = lerp(1, 0.55, p);
      blur = 6 * Math.sin(Math.PI * p);
      o = p < 0.7 ? 1 : 1 - (p - 0.7) / 0.3;
    }
    // amber while it is the newest value, then the landed (surface) style once the next one lands
    const next = CHIPS[CHIPS.indexOf(c) + 1];
    const fade = next && t >= next.land ? Math.min(1, (t - next.land) / 0.2) : 0;
    return { dx: x - slotC.x, dy: y - slotC.y, s, o, blur, amber: 1 - fade };
  }

  const AMBER = [244, 166, 42], SURF = [20, 29, 33], INK_DARK = [13, 19, 22], INK = [232, 238, 236];
  const BORDER_A = [244, 166, 42], BORDER_S = [38, 52, 59];
  const mix = (a, b, p) => `rgb(${a.map((v, i) => Math.round(lerp(b[i], v, p))).join(",")})`;

  // els: { cam, press, shake, dot, ring, chips: {c1: el, …} } — any may be missing.
  function render(els, t) {
    if (els.cam) {
      const f = xform(t);
      els.cam.style.transform = `translate(${f.x.toFixed(2)}px, ${f.y.toFixed(2)}px) scale(${f.s.toFixed(5)})`;
    }
    let press = 1, shake = 0, origin = null, dot = null, ring = null;
    for (const h of HITS) {
      const dt = t - h.t;
      if (dt < -0.15 || dt > 0.6) continue;
      const p = screenPt(h.camT === undefined ? h.t : h.camT, h.x, h.y);
      if (dt >= 0) {
        press = pressAt(dt, h.soft); shake = shakeAt(dt, h.soft); origin = p;
        const r = ringAt(dt, h.soft);
        if (r) ring = { p, ...r };
      }
      if (h.dot) { const d = dotAt(dt); if (d) dot = { p, ...d }; }
    }
    if (els.press) {
      els.press.style.transformOrigin = origin ? `${origin.x.toFixed(1)}px ${origin.y.toFixed(1)}px` : "50% 50%";
      els.press.style.transform = `scale(${press.toFixed(5)})`;
    }
    if (els.shake) els.shake.style.transform = `translateX(${shake.toFixed(2)}px)`;
    const place = (el, v) => {
      if (!el) return;
      if (!v) { el.style.opacity = "0"; return; }
      el.style.opacity = v.o.toFixed(3);
      el.style.transform = `translate(${(v.p.x - 32).toFixed(1)}px, ${(v.p.y - 32).toFixed(1)}px) scale(${v.s.toFixed(4)})`;
    };
    place(els.dot, dot);
    place(els.ring, ring);
    if (els.chips) {
      for (const c of CHIPS) {
        const el = els.chips[c.id];
        if (!el) continue;
        const st = chipState(c, t);
        if (!st) { el.style.opacity = "0"; continue; }
        el.style.opacity = st.o.toFixed(3);
        el.style.transform = `translate(${st.dx.toFixed(1)}px, ${st.dy.toFixed(1)}px) scale(${st.s.toFixed(4)})`;
        el.style.filter = st.blur > 0.05 ? `blur(${st.blur.toFixed(2)}px)` : "none";
        el.style.backgroundColor = mix(AMBER, SURF, st.amber);
        el.style.borderColor = mix(BORDER_A, BORDER_S, st.amber);
        el.style.color = mix(INK_DARK, INK, st.amber);
      }
    }
  }

  // One linear clock per scene drives render(); T0 = the scene's start in film time.
  function drive(tl, els, T0, dur) {
    const clock = { t: 0 };
    tl.fromTo(clock, { t: 0 }, { t: dur, duration: dur, ease: "none", onUpdate: () => render(els, T0 + clock.t) }, 0);
    render(els, T0);
  }

  window.STAGE = { SRC, SCR, K, CAM, TAPS, CHIPS, HITS, ROW, camAt, xform, screenPt, framePt, render, drive };
})();
