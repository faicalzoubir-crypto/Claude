// Builds compositions/frames/NN-*.html from the shared kit (tools/kit.mjs) and the per-frame
// layouts + motion in tools/frames/*.mjs. Durations come from the real voice (assets/voice/cues.json).
//   node tools/build_frames.mjs            → all frames
//   node tools/build_frames.mjs 06 13      → only those frames
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { wrap } from "./kit.mjs";
import intro from "./frames/intro.mjs";
import acts from "./frames/acts.mjs";
import outro from "./frames/outro.mjs";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const cues = JSON.parse(readFileSync(join(ROOT, "assets/voice/cues.json"), "utf8"));
const SILENT = { 14: 6 };

const only = process.argv.slice(2);
const frames = [...intro, ...acts, ...outro];
mkdirSync(join(ROOT, "compositions/frames"), { recursive: true });
for (const f of frames) {
  const nn = f.id.slice(0, 2);
  if (only.length && !only.includes(nn)) continue;
  const n = Number(nn);
  const cue = cues[String(n)];
  const duration = cue ? cue.duration : SILENT[n];
  // word-cue helper: time (s) of the k-th occurrence of a word starting with `w` in the voice line
  const at = (w, k = 1, fallback = 0) => {
    if (!cue) return fallback;
    let seen = 0;
    for (const x of cue.words) {
      const norm = x.w.toLowerCase().replace(/[^a-zà-ÿ0-9'-]/g, "");
      if (norm.startsWith(w.toLowerCase()) && ++seen === k) return x.t;
    }
    throw new Error(`frame ${f.id}: cue word "${w}" #${k} not found`);
  };
  const built = f.build({ duration, at, ROOT });
  built.html = built.html.replaceAll("__D__", String(duration));
  writeFileSync(join(ROOT, `compositions/frames/${f.id}.html`), wrap({ id: f.id, duration, ...built }));
  console.log(`✓ ${f.id}  ${duration}s`);
}
