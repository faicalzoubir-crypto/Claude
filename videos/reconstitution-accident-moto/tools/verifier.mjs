// Affiche les valeurs de la reconstitution (node tools/verifier.mjs).
import "../assets/kinematics.js";

const K = globalThis.KIN;
const f = (v, n = 2) => v.toFixed(n);
console.log("tau(t=3) =", f(K.tauAt(3)), " tau(7) =", f(K.tauAt(7)), " tau(11) =", f(K.tauAt(11)), " tau(12) =", f(K.tauAt(12)), " tau(15) =", f(K.tauAt(15)));
console.log("contact tauC =", f(K.tauC, 3), " t vidéo =", K.tContact);
console.log("freinage BMW aB =", f(K.aB), "m/s² (", f(K.aB / 9.81), "g )   vitesse au contact =", f(K.vC * 3.6, 1), "km/h");
console.log("BMW freine à t =", f(K.tBrakeB), "  scooter arrêté à t =", f(K.tStopA), "  distance d'arrêt scooter =", f(K.dStopA), "m");
console.log("repos à tau =", f(K.tauRest), " t vidéo =", f(K.tRest));
console.log("contact", K.contact, "\nrepos A", K.restA, "\nrepos B", K.restB, "\nrepos motard", K.restR);
console.log("glissade BMW (contact → repos) =", f(K.dist(K.contact, K.restB)), "m ; motard =", f(K.dist(K.contact, K.restR)), "m");
for (const t of [0, 3, 5, 7, 8, 9, 10, 11, 11.5, 12, 13, 14, 15]) {
  const tau = K.tauAt(t), a = K.scooter(tau), b = K.bmw(tau), r = K.rider(tau);
  const gap = (a.y - K.P.LA / 2) - (b.y + K.P.LB / 2);
  console.log(`t=${f(t, 1)} tau=${f(tau)} A y=${f(a.y)} v=${f(a.v * 3.6, 0)} | B x=${f(b.x)} y=${f(b.y)} head=${f(b.head, 1)} lean=${f(b.lean, 0)} v=${f(b.v * 3.6, 0)} | gap=${f(gap)} | R x=${f(r.x)} y=${f(r.y)}`);
}
