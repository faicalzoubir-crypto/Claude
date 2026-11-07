/* Reconstitution cinématique (valeurs estimées) — source unique des positions, vitesses et distances.
 *
 * Repère « monde », en mètres :
 *   x : en travers de la chaussée, 0 = nez de la bordure du terre-plein central côté voie montante,
 *       positif vers la droite (est). Voie de gauche (la plus proche du terre-plein) : 0 → 3,5 m.
 *   y : le long de la route, positif dans le sens de marche (nord, vers le haut de l'écran).
 * Temps : `tau` = temps simulé en secondes, 0 = le scooter commence à freiner.
 * Le film montre l'action à ×0,5 et le ralenti à ×0,1 : `tauAt(t)` convertit le temps vidéo.
 *
 * Chargé par index.html (window.KIN) et par node (tools/verifier.mjs).
 */
(function (root) {
  const KMH = 1 / 3.6;
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const smooth = (u) => { u = clamp(u, 0, 1); return u * u * (3 - 2 * u); };
  const easeOut = (u) => 1 - Math.pow(1 - clamp(u, 0, 1), 2);
  const lerp = (a, b, u) => a + (b - a) * u;

  // ── Données (demande) et hypothèses ──
  const P = {
    vA: 35 * KMH, // scooter 49 cm³, ~35 km/h
    vB: 55 * KMH, // BMW S1000 XR, ~55 km/h
    gap: 20, // BMW ~20 m derrière (avant BMW → arrière scooter) quand le scooter freine
    aA: 7.5, // freinage du scooter, m/s²
    prt: 1.0, // temps de perception-réaction du motard B, s
    LA: 1.85, WA: 0.70, // Docker Super C50 (49 cm³) : longueur, largeur au guidon
    LB: 2.18, WB: 0.94, // BMW : longueur, largeur au guidon (protège-mains)
    xA: 2.05, // scooter : centre à 2,05 m de la bordure (un peu à droite du milieu de voie)
    xB0: 1.95, // BMW avant l'évitement
    overlap: 0.06, // recouvrement latéral guidon droit BMW / arrière gauche scooter
    reachB: 0.34, // guidon BMW en avant de son centre, m
    contactBack: 0.12, // point touché : 12 cm en avant de l'arrière du scooter
    swerveFrom: 0.95, // début du décalage à gauche (s)
    aPost: 4.0, // décélération de la BMW après le contact (chute puis glissade sur le flanc)
    uSep: 0.42, // séparation motard / moto après le contact (s)
    riderDir: -32, // direction de projection du motard, degrés (négatif = vers la gauche)
    aRider: 7.0, // décélération du motard au sol
    yawRestB: -28, // orientation finale de la BMW couchée
    xRestB: 1.25, // ligne des roues de la BMW couchée (le haut de la moto touche la bordure)
  };

  // ── Temps vidéo → temps simulé (vitesse d'affichage ×0,5, ralenti ×0,1 autour du contact) ──
  const RATE = [ // [t vidéo, vitesse d'affichage]
    [0, 0.5], [10.8, 0.5], [11.1, 0.1], [11.9, 0.1], [12.2, 0.5], [30, 0.5],
  ];
  const T0 = 7.0; // le scooter freine à t = 7 s
  function rateAt(t) {
    for (let i = 1; i < RATE.length; i++) {
      if (t <= RATE[i][0]) {
        const [a, ra] = RATE[i - 1], [b, rb] = RATE[i];
        return lerp(ra, rb, (t - a) / (b - a));
      }
    }
    return RATE[RATE.length - 1][1];
  }
  const DT = 0.001, NT = 30001, TAB = new Float64Array(NT);
  (function () { // intégrale de la vitesse d'affichage, calée pour tau(T0) = 0
    for (let i = 1; i < NT; i++) TAB[i] = TAB[i - 1] + 0.5 * (rateAt((i - 1) * DT) + rateAt(i * DT)) * DT;
    const off = TAB[Math.round(T0 / DT)];
    for (let i = 0; i < NT; i++) TAB[i] -= off;
  })();
  function tauAt(t) {
    const f = clamp(t, 0, 30) / DT, i = Math.min(NT - 2, Math.floor(f));
    return lerp(TAB[i], TAB[i + 1], f - i);
  }
  function tAtTau(tau) { // inverse (bissection)
    let a = 0, b = 30;
    for (let k = 0; k < 60; k++) { const m = (a + b) / 2; if (tauAt(m) < tau) a = m; else b = m; }
    return (a + b) / 2;
  }

  // ── Scooter A ──
  const tStopA = P.vA / P.aA;
  const dStopA = (P.vA * P.vA) / (2 * P.aA);
  function yA(tau) {
    if (tau < 0) return P.vA * tau;
    if (tau < tStopA) return P.vA * tau - 0.5 * P.aA * tau * tau;
    return dStopA;
  }
  function vA(tau) { return tau < 0 ? P.vA : Math.max(0, P.vA - P.aA * tau); }

  // ── BMW B avant le contact ──
  const yB0 = -P.LA / 2 - P.gap - P.LB / 2; // centre de la BMW à tau = 0
  const contactY = dStopA - P.LA / 2 + P.contactBack; // point touché sur le scooter
  const xContactB = P.xA - P.WA / 2 - P.WB / 2 + P.overlap; // centre BMW au contact
  // Le contact est fixé à tauC (milieu du ralenti, t vidéo = 11,5 s) ; on en déduit le freinage de B.
  const tauC = tauAt(11.5);
  const aB = (function () {
    const need = contactY - P.reachB - yB0 - P.vB * P.prt; // distance après la réaction
    const d = tauC - P.prt;
    return (2 * (P.vB * d - need)) / (d * d);
  })();
  function yBpre(tau) {
    if (tau < P.prt) return yB0 + P.vB * tau;
    const d = tau - P.prt;
    return yB0 + P.vB * P.prt + P.vB * d - 0.5 * aB * d * d;
  }
  function vBpre(tau) { return tau < P.prt ? P.vB : P.vB - aB * (tau - P.prt); }
  function xBpre(tau) { return lerp(P.xB0, xContactB, smooth((tau - P.swerveFrom) / (tauC - P.swerveFrom))); }
  const yC = yBpre(tauC), vC = vBpre(tauC);

  // ── Après le contact ──
  const uStopB = vC / P.aPost;
  const dSlideB = (vC * vC) / (2 * P.aPost);
  function sPost(u) { u = clamp(u, 0, uStopB); return vC * u - 0.5 * P.aPost * u * u; }
  // inclinaison (chute à gauche) : 0 → 90° entre 0,16 et 0,60 s après le contact
  function leanB(u) { const k = clamp((u - 0.16) / 0.44, 0, 1); return 90 * k * k; }

  const headPre = (tau) => { // cap en degrés (négatif = nez vers la gauche), d'après la tangente
    const h = 0.004, dx = xBpre(tau + h) - xBpre(tau - h), dy = yBpre(tau + h) - yBpre(tau - h);
    return (Math.atan2(dx, Math.max(1e-6, dy)) * 180) / Math.PI;
  };
  const headC = headPre(tauC - 0.004);

  function bmw(tau) {
    if (tau <= tauC) {
      return { x: xBpre(tau), y: yBpre(tau), head: headPre(tau), lean: 0, v: vBpre(tau), u: tau - tauC };
    }
    const u = tau - tauC, k = clamp(u / uStopB, 0, 1);
    const wob = u < 0.6 ? 7 * Math.sin((2 * Math.PI * u) / 0.3) * Math.exp(-u / 0.22) : 0;
    const head = lerp(headC, P.yawRestB, smooth((u - 0.25) / (uStopB - 0.25))) + wob;
    const x = lerp(xContactB, P.xRestB, easeOut(k));
    return { x, y: yC + sPost(u), head, lean: leanB(u), v: Math.max(0, vC - P.aPost * u), u };
  }

  // ── Motard B ──
  const sep = (function () {
    const b = bmw(tauC + P.uSep);
    const a = (b.lean * Math.PI) / 180;
    // assis : 0,25 m en arrière du centre ; le haut du corps (~1 m) suit l'inclinaison vers la gauche
    const hx = (b.head * Math.PI) / 180;
    return {
      x: b.x - 0.25 * Math.sin(hx) - 1.0 * Math.sin(a),
      y: b.y - 0.25 * Math.cos(hx),
      v: b.v,
      head: b.head,
    };
  })();
  // orientation finale du motard au sol : en travers de la bordure en 9:16 ; le long de la bordure en 16:9
  // (vu de dessus, un corps vertical à l'écran se lit « debout » : il doit rester à peu près horizontal)
  const RIDER_TURN = root.FORMAT === "16x9" ? -165 : -105;
  const uStopR = sep.v / P.aRider;
  const dRider = (sep.v * sep.v) / (2 * P.aRider);
  const dirR = ((sep.head + P.riderDir) * Math.PI) / 180;
  function rider(tau) {
    if (tau <= tauC + P.uSep) {
      const b = bmw(tau), a = (b.lean * Math.PI) / 180, hx = (b.head * Math.PI) / 180;
      return { x: b.x - 0.25 * Math.sin(hx) - 1.0 * Math.sin(a), y: b.y - 0.25 * Math.cos(hx), head: b.head, lean: b.lean, flying: 0, on: true };
    }
    const u = clamp(tau - tauC - P.uSep, 0, uStopR);
    const s = sep.v * u - 0.5 * P.aRider * u * u;
    const k = clamp(u / uStopR, 0, 1);
    return {
      x: sep.x + s * Math.sin(dirR),
      y: sep.y + s * Math.cos(dirR),
      head: lerp(sep.head, sep.head + RIDER_TURN, easeOut(k)), // le corps pivote en glissant
      lean: 90,
      flying: smooth(u / 0.22), // 0 assis → 1 allongé
      on: false,
    };
  }

  function scooter(tau) {
    const u = tau - tauC;
    const k = u > 0 ? easeOut(u / 0.3) : 0;
    return { x: P.xA + 0.12 * k, y: yA(tau), head: -4 * k, v: vA(tau) };
  }

  const tauRest = Math.max(tauC + uStopB, tauC + P.uSep + uStopR);
  const restB = bmw(tauRest), restR = rider(tauRest), restA = scooter(tauRest);
  const contact = { x: P.xA - P.WA / 2 + 0.02, y: contactY };

  // ── Version longue (55 s) : temps d'origine (montage de 37 s) → temps du film ──
  // L'action passe de ×0,5 à ×0,4 (×1,25), le ralenti de ×0,1 à ×0,05 (×2) ; vue d'ensemble, fiche juridique et
  // synthèse tenues plus longtemps. La scène du monde est dessinée au temps d'origine Tinv(t) : physique inchangée.
  const TK = [[0, 0], [3, 4], [10.8, 13.75], [11.1, 14.125], [11.9, 15.725], [12.2, 16.1], [16.6, 21.6], [20.0, 27.6], [20.4, 28.0], [32.0, 43.6], [37.0, 55.0]];
  function pw(x, a, b) {
    if (x <= TK[0][a]) return TK[0][b] + (x - TK[0][a]);
    for (let i = 1; i < TK.length; i++) {
      if (x <= TK[i][a]) return lerp(TK[i - 1][b], TK[i][b], (x - TK[i - 1][a]) / (TK[i][a] - TK[i - 1][a]));
    }
    return TK[TK.length - 1][b] + (x - TK[TK.length - 1][a]);
  }
  const T = (old) => pw(old, 0, 1), Tinv = (t) => pw(t, 1, 0);

  const KIN = {
    T, Tinv, TK,
    P, tauAt, tAtTau, rateAt, scooter, bmw, rider,
    tauC, tContact: 11.5, aB, vC, yC, uStopB, dSlideB, dRider, tauRest, tRest: tAtTau(tauRest),
    tBrakeB: tAtTau(P.prt), tStopA: tAtTau(tStopA), dStopA, yB0,
    restA, restB, restR, contact,
    dist: (a, b) => Math.hypot(a.x - b.x, a.y - b.y),
  };
  root.KIN = KIN;
  if (typeof module !== "undefined" && module.exports) module.exports = KIN;
})(typeof window !== "undefined" ? window : globalThis);
