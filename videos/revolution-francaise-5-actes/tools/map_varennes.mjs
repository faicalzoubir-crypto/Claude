// Bakes the Varennes map (Acte 2) from real geographic data — no tiles, no network at render.
//   - rivers: @geo-maps/earth-rivers-10m (OpenStreetMap water polygons, ODbL) — extracted once
//     to assets/map/source/rivers-bbox.json
//   - border: world-atlas countries-10m (Natural Earth, public domain) — France ∩ Belgium /
//     Luxembourg shared arcs, extracted once to assets/map/source/border-bbox.json
//   - places: lon/lat of the PDF's towns + the historical post road Paris → Varennes.
// Output: assets/map/varennes-geo.json — Web-Mercator projected SVG path data + place pixels,
// for a 1920×1080 frame (the composition inlines it as SVG paths it can animate).
//
// Usage:
//   node tools/map_varennes.mjs extract <rivers map.geo.json> <world-atlas countries-10m.json>
//   node tools/map_varennes.mjs
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const SRC = join(ROOT, "assets/map/source");
const BBOX = { w: 0.8, e: 7.2, s: 47.8, n: 50.6 };
const inb = ([lon, lat]) => lon > BBOX.w && lon < BBOX.e && lat > BBOX.s && lat < BBOX.n;

if (process.argv[2] === "extract") {
  const rivers = JSON.parse(readFileSync(process.argv[3], "utf8"));
  const polys = [];
  for (const gm of rivers.geometries ?? rivers.features.map((f) => f.geometry))
    for (const p of gm.type === "Polygon" ? [gm.coordinates] : gm.coordinates)
      if (p[0].some(inb)) polys.push(p.map((ring) => ring.map(([x, y]) => [+x.toFixed(5), +y.toFixed(5)])));
  writeFileSync(join(SRC, "rivers-bbox.json"), JSON.stringify(polys));

  const topo = JSON.parse(readFileSync(process.argv[4], "utf8"));
  const [sx, sy] = topo.transform.scale;
  const [tx, ty] = topo.transform.translate;
  const arcs = topo.arcs.map((arc) => {
    let x = 0, y = 0;
    return arc.map(([dx, dy]) => ((x += dx), (y += dy), [x * sx + tx, y * sy + ty]));
  });
  const geoms = topo.objects.countries.geometries;
  const arcSet = (id) => {
    const g = geoms.find((c) => c.id === id);
    const s = new Set();
    const walk = (a) => (Array.isArray(a) ? a.forEach(walk) : s.add(a < 0 ? ~a : a));
    walk(g.arcs);
    return s;
  };
  const fr = arcSet("250");
  const shared = [...new Set([...arcSet("056"), ...arcSet("442")])].filter((i) => fr.has(i));
  const lines = shared.map((i) => arcs[i]).filter((l) => l.some(inb));
  writeFileSync(join(SRC, "border-bbox.json"), JSON.stringify(lines.map((l) => l.map(([x, y]) => [+x.toFixed(5), +y.toFixed(5)]))));
  console.log(`extracted ${polys.length} river polygons, ${lines.length} border arcs`);
  process.exit(0);
}

// ── Web-Mercator projection fitted to the frame ─────────────────────────────
const PX_PER_DEG = 430; // horizontal scale: Paris → Montmédy spans ~1300px
const LON0 = 3.86, LAT0 = 49.2; // frame center
const K = (PX_PER_DEG * 180) / Math.PI;
const mercY = (lat) => Math.log(Math.tan(Math.PI / 4 + (lat * Math.PI) / 360));
const proj = ([lon, lat]) => [960 + (lon - LON0) * PX_PER_DEG, 540 - (mercY(lat) - mercY(LAT0)) * K];
const r1 = (v) => Math.round(v * 10) / 10;
const path = (pts, close) =>
  pts.map((p, i) => (i ? "L" : "M") + proj(p).map(r1).join(",")).join("") + (close ? "Z" : "");

const rivers = JSON.parse(readFileSync(join(SRC, "rivers-bbox.json"), "utf8"));
const border = JSON.parse(readFileSync(join(SRC, "border-bbox.json"), "utf8"));

const PLACES = {
  paris: { name: "Paris", lonlat: [2.3522, 48.8566] },
  menehould: { name: "Sainte-Menehould", lonlat: [4.8975, 49.0903] },
  varennes: { name: "Varennes", lonlat: [5.0331, 49.2258] },
  montmedy: { name: "Montmédy", lonlat: [5.3681, 49.5203] },
};
// The king's road, June 1791 (post road): Paris → Meaux → Montmirail → Châlons →
// Sainte-Menehould → Clermont-en-Argonne → Varennes. Intermediate stages stay unlabeled.
const ROUTE = [
  [2.3522, 48.8566], [2.878, 48.96], [3.537, 48.868], [4.0, 48.92], [4.363, 48.957],
  [4.62, 49.03], [4.8975, 49.0903], [5.07, 49.107], [5.0331, 49.2258],
];
// What was planned beyond Varennes: Dun, Stenay, Montmédy — never reached.
const PLANNED = [[5.0331, 49.2258], [5.185, 49.385], [5.187, 49.48], [5.3681, 49.5203]];
const RIVER_LABELS = [
  { name: "Seine", lonlat: [2.0, 48.95], rot: -8 },
  { name: "Marne", lonlat: [3.3, 48.96], rot: 6 },
  { name: "Meuse", lonlat: [5.66, 48.98], rot: -76 },
  { name: "Aisne", lonlat: [4.2, 49.47], rot: 4 },
];

// River centerlines: the OSM water polygons are fragments along each course, so each main river
// is rebuilt as a line through its own fragments — a coarse corridor (towns on the river) picks
// the fragments within CORRIDOR_KM, they are ordered along the corridor, then smoothed.
const CORRIDOR_KM = 7;
const RIVERS = {
  Seine: [[1.62, 49.05], [1.72, 48.99], [2.04, 48.93], [2.25, 48.84], [2.35, 48.855], [2.41, 48.82], [2.66, 48.54], [2.95, 48.38], [3.1, 48.3]],
  Marne: [[2.41, 48.82], [2.6, 48.85], [2.88, 48.96], [3.4, 49.04], [3.95, 49.04], [4.36, 48.96], [4.58, 48.72], [4.95, 48.64], [5.05, 48.4]],
  Oise: [[2.09, 49.0], [2.1, 49.05], [2.47, 49.26], [2.83, 49.42], [3.0, 49.58], [3.22, 49.62], [3.62, 49.9], [3.75, 50.0]],
  Aisne: [[2.83, 49.42], [3.32, 49.38], [3.9, 49.4], [4.37, 49.51], [4.7, 49.4], [4.87, 49.34], [4.9, 49.09], [4.98, 48.92]],
  Meuse: [[5.6, 48.5], [5.59, 48.76], [5.54, 48.89], [5.38, 49.16], [5.18, 49.38], [5.19, 49.49], [4.94, 49.7], [4.72, 49.77], [4.83, 50.14], [4.86, 50.3]],
};
const KM = ([a, b], [c, d]) => Math.hypot((a - c) * 111.32 * Math.cos((49 * Math.PI) / 180), (b - d) * 110.57);
function nearestOnPolyline(pt, line) {
  let best = { d: Infinity, s: 0 }, acc = 0;
  for (let i = 0; i < line.length - 1; i++) {
    const A = line[i], B = line[i + 1];
    const seg = KM(A, B);
    const kx = 111.32 * Math.cos((49 * Math.PI) / 180), ky = 110.57;
    const ax = A[0] * kx, ay = A[1] * ky, bx = B[0] * kx, by = B[1] * ky, px = pt[0] * kx, py = pt[1] * ky;
    const t = Math.max(0, Math.min(1, ((px - ax) * (bx - ax) + (py - ay) * (by - ay)) / ((bx - ax) ** 2 + (by - ay) ** 2 || 1)));
    const d = Math.hypot(px - (ax + t * (bx - ax)), py - (ay + t * (by - ay)));
    if (d < best.d) best = { d, s: acc + t * seg };
    acc += seg;
  }
  return best;
}
const centroids = rivers.map((p) => {
  const r = p[0];
  return [r.reduce((a, c) => a + c[0], 0) / r.length, r.reduce((a, c) => a + c[1], 0) / r.length];
});
function riverLine(corridor) {
  const pts = centroids
    .map((c) => ({ c, ...nearestOnPolyline(c, corridor) }))
    .filter((x) => x.d <= CORRIDOR_KM)
    .sort((a, b) => a.s - b.s)
    .map((x) => x.c);
  const seq = [corridor[0], ...pts, corridor[corridor.length - 1]];
  // moving-average smoothing (window 7), endpoints kept
  const sm = seq.map((p, i) => {
    if (i === 0 || i === seq.length - 1) return p;
    const w = seq.slice(Math.max(0, i - 3), Math.min(seq.length, i + 4));
    return [w.reduce((a, c) => a + c[0], 0) / w.length, w.reduce((a, c) => a + c[1], 0) / w.length];
  });
  // decimate to ~2.5 km steps
  const out = [sm[0]];
  for (const p of sm.slice(1)) if (KM(p, out[out.length - 1]) > 2.5) out.push(p);
  out.push(sm[sm.length - 1]);
  return { line: out, n: pts.length };
}
const riverLines = Object.fromEntries(Object.entries(RIVERS).map(([k, c]) => [k, riverLine(c)]));

const out = {
  frame: [1920, 1080],
  projection: { type: "web-mercator", PX_PER_DEG, LON0, LAT0 },
  rivers: rivers.map((p) => p.map((ring) => path(ring, true)).join("")),
  riverLines: Object.fromEntries(Object.entries(riverLines).map(([k, v]) => [k, path(v.line, false)])),
  border: border.map((l) => path(l, false)),
  route: path(ROUTE, false),
  planned: path(PLANNED, false),
  places: Object.fromEntries(Object.entries(PLACES).map(([k, v]) => [k, { name: v.name, xy: proj(v.lonlat).map(r1) }])),
  riverLabels: RIVER_LABELS.map((l) => ({ ...l, xy: proj(l.lonlat).map(r1) })),
  credits: "Données : Natural Earth · © contributeurs OpenStreetMap",
};
writeFileSync(join(ROOT, "assets/map/varennes-geo.json"), JSON.stringify(out));
console.log(Object.entries(riverLines).map(([k, v]) => `${k}: ${v.n} fragments`).join(" · "));
console.log(
  `rivers ${out.rivers.length} · border ${out.border.length} · places`,
  Object.values(out.places).map((p) => `${p.name}@${p.xy}`).join(" "),
);
