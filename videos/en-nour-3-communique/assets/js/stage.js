/* Shared stage for en-nour-3-communique: the iPad, its camera, the haptic taps, the value chips,
 * the highlight boxes and the callouts.
 *
 * The recording plays at its own speed from 0 to 100.73 s with no cut, so film time = source time.
 * Every scene draws the same device at the same place and calls STAGE.render(els, t) from one
 * linear clock tween: each frame is a pure function of film time t, seek-safe, identical in preview
 * and render, continuous across scene seams.
 *
 * Coordinates of taps, chips, boxes and callouts are in source pixels of the recording (1080 x 1554).
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
    // intro on the home page
    { t1: 0, fx: 540, fy: 777, z: 1 },
    { t0: 3.6, t1: 4.1, fx: 260, fy: 1080, z: 2.4 }, // the day's timetable (the posters stay out of frame)
    { t0: 8.75, t1: 8.75, fx: 540, fy: 777, z: 1 }, // punch out on the title change
    { t0: 13.5, t1: 13.5, fx: 900, fy: 200, z: 3.2 }, // punch in on the menu button, above the posters
    // 1 ouvrir: as the menu opens, cut to its items (the account name and the posters stay out of frame)
    { t0: 17.7, t1: 17.7, fx: 880, fy: 1250, z: 1.9 },
    { t0: 19.6, t1: 20.4, fx: 820, fy: 1385, z: 2.3 },
    { t0: 21.6, t1: 22.3, fx: 540, fy: 777, z: 1 },
    { t0: 23.6, t1: 24.5, fx: 990, fy: 1480, z: 2.2 },
    { t0: 25.18, t1: 25.33, fx: 1026, fy: 1520, z: 4.0, ease: "power3.in" }, // zoom through the +
    { t0: 25.33, t1: 25.8, fx: 395, fy: 700, z: 1.45, ease: "expo.out" }, // the form lands and settles
    // 2 classes
    { t0: 26.05, t1: 26.6, fx: 255, fy: 860, z: 2.3 },
    { t0: 29.6, t1: 30.0, fx: 255, fy: 860, z: 1.6, ease: "power3.in" }, // zoom pulse out…
    // 3 type
    { t0: 30.0, t1: 30.5, fx: 255, fy: 870, z: 2.3, ease: "expo.out" }, // …and back in
    // 4 matière
    { t0: 34.85, t1: 35.4, fx: 245, fy: 840, z: 2.4 },
    // rappel: the whole form while the iPad steps aside, then the date field
    { t0: 38.65, t1: 39.3, fx: 540, fy: 777, z: 1 },
    { t0: 47.6, t1: 48.4, fx: 300, fy: 886, z: 1.9 },
    // 5 date
    { t0: 54.3, t1: 55.0, fx: 880, fy: 860, z: 1.9 },
    // 6 titre et message
    { t0: 66.4, t1: 67.1, fx: 265, fy: 940, z: 2.2 },
    { t0: 68.3, t1: 68.75, fx: 265, fy: 600, z: 2.2 }, // follows the page up as the keyboard rises
    { t0: 74.5, t1: 75.1, fx: 560, fy: 700, z: 1.25 },
    // envoyer: the whole filled form, then « Envoyer »
    { t0: 78.8, t1: 79.7, fx: 540, fy: 777, z: 1, ease: "power2.inOut" },
    { t0: 79.75, t1: 80.2, fx: 990, fy: 1406, z: 2.2 },
    // résultat: cut to the published card, the whole card, then read it
    { t0: 80.733, t1: 80.733, fx: 250, fy: 385, z: 2.4 },
    { t0: 81.6, t1: 82.15, fx: 540, fy: 400, z: 1.1 },
    { t0: 84.1, t1: 84.7, fx: 250, fy: 385, z: 2.4 },
    { t0: 86.3, t1: 86.9, fx: 830, fy: 360, z: 2.2 },
  ];

  // Real taps of the recording (source time = film time). camT: read the position with the camera of
  // that instant (the tap whose flash cuts to the next scene).
  const TAPS = [
    { t: 0.85, x: 540, y: 717 }, // the EcolePlus icon (drawn over the screen in the intro)
    { t: 17.62, x: 1045, y: 97 }, // ☰
    { t: 21.27, x: 760, y: 1400 }, // Communiqué évaluatif
    { t: 25.18, x: 1026, y: 1520 }, // +
    { t: 25.93, x: 300, y: 555 }, // Classes
    { t: 27.65, x: 120, y: 980 }, // T.C.S.F2
    { t: 31.15, x: 300, y: 668 }, // Type
    { t: 34.0, x: 105, y: 790 }, // DS
    { t: 35.95, x: 300, y: 780 }, // Matière
    { t: 37.9, x: 115, y: 916 }, // SVT
    { t: 54.05, x: 450, y: 886 }, // Date
    { t: 64.62, x: 922, y: 704 }, // mois suivant
    { t: 66.0, x: 840, y: 830 }, // 4
    { t: 67.9, x: 300, y: 985 }, // Titre
    { t: 70.95, x: 300, y: 700 }, // Description
    { t: 72.45, x: 300, y: 700 }, // Description (menu)
    { t: 73.38, x: 80, y: 700 }, // Paste
    { t: 80.3, x: 990, y: 1406, camT: 80.25 }, // Envoyer
  ];

  // The values the teacher sets: each lifts off the tapped control as an amber chip, flies to the
  // row under the title, and in the result flies into the published card.
  const ROW = { y: 352, h: 48 };
  const PAY0 = 82.3; // first chip leaves the row for the card
  const CHIPS = [
    { id: "c1", text: "T.C.S.F1 · T.C.S.F2", t: 27.68, x: 120, y: 980, slot: { x: 80, w: 300 }, card: { x: 135, y: 440 } },
    { id: "c2", text: "DS", t: 34.03, x: 105, y: 790, slot: { x: 392, w: 80 }, card: { x: 56, y: 324 } },
    { id: "c3", text: "SVT", t: 37.93, x: 115, y: 916, slot: { x: 484, w: 100 }, card: { x: 1024, y: 378 } },
    { id: "c4", text: "04/11/2026", t: 66.03, x: 840, y: 830, slot: { x: 596, w: 210 }, card: { x: 160, y: 412 } },
    { id: "c5", text: "Message", t: 74.7, x: 300, y: 700, slot: { x: 818, w: 160 }, card: { x: 420, y: 368 } },
  ];
  const POP = 0.18, FLY = 0.42, SETTLE = 0.25, PAY_FLY = 0.5, PAY_GAP = 0.25;
  CHIPS.forEach((c, i) => {
    c.land = c.t + POP + FLY;
    c.pay = PAY0 + i * PAY_GAP;
    c.payLand = c.pay + PAY_FLY;
  });

  // Amber outlines drawn round real parts of the screen: the day's two SVT lessons, then the three
  // fields already filled.
  const BOXES = [
    { t0: 5.0, t1: 8.3, x: 40, y: 897, w: 270, h: 156 },
    { t0: 5.45, t1: 8.3, x: 40, y: 1070, w: 270, h: 158 },
    { t0: 44.6, t1: 47.4, x: 10, y: 516, w: 1060, h: 80 },
    { t0: 44.95, t1: 47.4, x: 10, y: 628, w: 1060, h: 80 },
    { t0: 45.3, t1: 47.4, x: 10, y: 740, w: 1060, h: 80 },
  ];

  // Callouts: a dot on the control, a short line, a label dy px above (−) or below (+) it.
  const CALLOUTS = [
    { t0: 15.0, t1: 17.45, x: 1045, y: 97, text: "Menu", dy: 120 },
    { t0: 55.3, t1: 58.4, x: 840, y: 872, text: "Aujourd'hui", dy: 130 },
    { t0: 58.9, t1: 64.55, x: 922, y: 704, text: "Mois suivant", dy: -130 },
    { t0: 87.7, t1: 89.6, x: 1006, y: 350, text: "Validé", dy: 120 }, // the app's own status turns green
  ];

  // Haptic hits: every tap, plus each chip landing in the result.
  const HITS = TAPS.map((p) => ({ ...p, dot: true }))
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

  // in/out envelope of a timed overlay: 0 before t0, 1 once drawn, back to 0 after t1
  function inOut(t, t0, t1, tin, tout) {
    if (t < t0 || t > t1 + tout) return null;
    return { pin: Math.min(1, (t - t0) / tin), pout: t > t1 ? (t - t1) / tout : 0 };
  }

  // els: { cam, press, shake, dot, ring, chips: {c1: el, …}, boxes: [el, el, el], callout: {dot, line, label} }
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

    if (els.boxes) {
      const live = BOXES.map((b) => ({ b, e: inOut(t, b.t0, b.t1, 0.3, 0.2) })).filter((x) => x.e);
      els.boxes.forEach((el, i) => {
        const x = live[i];
        if (!x) { el.style.opacity = "0"; return; }
        const a = framePt(t, x.b.x, x.b.y), z = framePt(t, x.b.x + x.b.w, x.b.y + x.b.h);
        const pin = ease("expo.out")(x.e.pin);
        el.style.left = `${a.x.toFixed(1)}px`; el.style.top = `${a.y.toFixed(1)}px`;
        el.style.width = `${(z.x - a.x).toFixed(1)}px`; el.style.height = `${(z.y - a.y).toFixed(1)}px`;
        el.style.opacity = (Math.min(1, x.e.pin * 2) * (1 - x.e.pout)).toFixed(3);
        el.style.transform = `scale(${lerp(1.06, 1, pin).toFixed(4)})`;
      });
    }

    if (els.callout) {
      const c = CALLOUTS.find((k) => inOut(t, k.t0, k.t1, 0.4, 0.2));
      const { dot: d, line: ln, label: lb } = els.callout;
      if (!c) { [d, ln, lb].forEach((el) => (el.style.opacity = "0")); return; }
      const e = inOut(t, c.t0, c.t1, 0.4, 0.2), p = framePt(t, c.x, c.y), o = (1 - e.pout).toFixed(3);
      const pd = ease("back.out(2)")(Math.min(1, e.pin / 0.5));
      const pl = ease("power3.out")(clamp((e.pin - 0.25) / 0.5, 0, 1));
      const pt = clamp((e.pin - 0.55) / 0.45, 0, 1);
      d.style.opacity = o;
      d.style.transform = `translate(${(p.x - 9).toFixed(1)}px, ${(p.y - 9).toFixed(1)}px) scale(${pd.toFixed(3)})`;
      const len = Math.abs(c.dy) - 34, top = c.dy < 0 ? p.y - 9 - len : p.y + 9;
      ln.style.opacity = o;
      ln.style.height = `${len}px`;
      ln.style.transformOrigin = c.dy < 0 ? "50% 100%" : "50% 0%";
      ln.style.transform = `translate(${(p.x - 1).toFixed(1)}px, ${top.toFixed(1)}px) scaleY(${pl.toFixed(3)})`;
      const w = c.text.length * 16 + 44, ly = c.dy < 0 ? p.y + c.dy - 25 : p.y + c.dy - 23; // no layout reads per frame
      const lx = clamp(p.x - w / 2, 100, 980 - w);
      lb.style.opacity = (pt * (1 - e.pout)).toFixed(3);
      lb.style.filter = pt < 1 ? `blur(${(6 * (1 - pt)).toFixed(2)}px)` : "none";
      lb.style.transform = `translate(${lx.toFixed(1)}px, ${ly.toFixed(1)}px)`;
      lb.style.width = `${w}px`;
      lb.textContent = c.text;
    }
  }

  // One linear clock per scene drives render(); T0 = the scene's start in film time.
  function drive(tl, els, T0, dur) {
    const clock = { t: 0 };
    tl.fromTo(clock, { t: 0 }, { t: dur, duration: dur, ease: "none", onUpdate: () => render(els, T0 + clock.t) }, 0);
    render(els, T0);
  }

  window.STAGE = { SRC, SCR, K, CAM, TAPS, CHIPS, BOXES, CALLOUTS, HITS, ROW, camAt, xform, screenPt, framePt, render, drive };
})();
