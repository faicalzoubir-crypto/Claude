#!/usr/bin/env node
// Renders the 3D shots of the film from film.html (built by build_film.py) with Playwright + ffmpeg.
//
//   node tools/render3d/render.cjs                 all shots
//   node tools/render3d/render.cjs s4 plate_on     some shots
//   node tools/render3d/render.cjs --probe s4      one still per keyframe → renders/probe-*.jpg
//
// Shots are timed on cues.js (the voice): see SHOTS below. Writes assets/footage/<shot>.mp4 (or .jpg
// for stills), tools/footage.json (which scene shows which clip) and footage-anchors.js
// (window.ANCHORS[shot][frame] = {name: [x, y, inFront]}, 1080x1920 px, read by the overlays).
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const ROOT = path.resolve(__dirname, '../..');
const HERE = __dirname;
const FPS = 30;
const raw = fs.readFileSync(path.join(ROOT, 'cues.js'), 'utf8');
const C = JSON.parse(raw.slice(raw.indexOf('=') + 1, raw.lastIndexOf(';')));
const sc = (id) => C.scenes[id];
const rel = (pid, sid, edge = 'start') => +(C.phrases[pid][edge] - sc(sid).start).toFixed(3);
const len = (sid) => +(sc(sid).end - sc(sid).start + 0.2).toFixed(3);

// world landmarks (see refinery/samir-3d): stack (-125,-30) h150 · furnace (-95,-30) · CDU (-62,-38) h62
// tanker (-195,-262) along x · pier x=-195 · LPG spheres x 55..105 z 64 · reformer (61,-46) · HCU (100..126,-46)
const SHOTS = {
  plate_off: { still: true, mode: 'off', fov: 50, flows: false,
    keys: [[0, [30, 15, 320], [-150, 25, -25]]], anchors: { stackTop: [-125, 150, -30], stackMid: [-125, 100, -30] } },
  plate_on: { still: true, mode: 'dusk', fov: 50, flows: false,
    keys: [[0, [30, 15, 320], [-150, 25, -25]]] },
  s3: { scene: 's3', dur: len('s3'), mode: 'dusk', fov: 46, emphasize: ['jetty', 'crude'], clock0: 3,
    keys: [[0, [-60, 70, -380], [-195, 4, -262]], [len('s3'), [-130, 95, -365], [-195, 4, -215]]],
    anchors: { tanker: [-195, 12, -262], pier: [-195, 6, -200] } },
  s4: { scene: 's4', dur: len('s4'), mode: 'dusk', fov: 50, emphasize: ['furnace', 'cdu', 'hdt', 'reformer', 'hcu', 'vdu', 'desalter'], clock0: 12,
    keys: [
      [0, [-80, 9, -88], [-97, 9, -30]],
      [Math.max(1, rel('s4p2', 's4') - 1.3), [-86, 8, -79], [-97, 9, -30]],
      [rel('s4p2', 's4') + 0.9, [-50, 40, -128], [-62, 29, -38]],
      [rel('s4p4', 's4') - 0.2, [-53, 40, -121], [-62, 29, -38]],
      [len('s4'), [112, 120, 62], [85, 10, -45]],
    ],
    anchors: { furnace: [-95, 22, -30], gas: [-58.6, 58, -38], gasoline: [-58.6, 46, -38], kero: [-58.6, 34, -38], diesel: [-58.6, 22, -38],
      convert: [105, 28, -50], sulfur: [13, 20, -43], sru: [151, 4, -58] } },
  s7: { scene: 's7', dur: len('s7'), mode: 'dusk', fov: 50, clock0: 30,
    keys: [[0, [10, 75, 170], [-40, 30, -60]], [len('s7'), [110, 210, 400], [-10, 10, -90]]] },
};

const outDir = path.join(ROOT, 'assets/footage');
fs.mkdirSync(outDir, { recursive: true });
fs.mkdirSync(path.join(ROOT, 'renders'), { recursive: true });

(async () => {
  const args = process.argv.slice(2);
  const probe = args.includes('--probe');
  const anchorsOnly = args.includes('--anchors');
  const pick = args.filter((a) => !a.startsWith('--'));
  const names = pick.length ? pick : Object.keys(SHOTS);
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on('pageerror', (e) => console.error('PAGEERROR', e.stack));
  page.on('console', (m) => { if (m.type() === 'error') console.error('console:', m.text()); });
  await page.route('https://cdn.jsdelivr.net/npm/three@0.160.0/**', (r) => {
    const f = path.join(HERE, 'node_modules/three', r.request().url().split('three@0.160.0/')[1]);
    r.fulfill({ status: 200, contentType: 'application/javascript', body: fs.readFileSync(f) });
  });
  await page.route('http://film.local/film.html', (r) => r.fulfill({ status: 200, contentType: 'text/html', body: fs.readFileSync(path.join(HERE, 'film.html')) }));
  await page.route('http://film.local/shots.js', (r) => r.fulfill({ status: 200, contentType: 'application/javascript', body: 'window.SHOTS = ' + JSON.stringify(SHOTS) + ';' }));
  await page.goto('http://film.local/film.html');
  await page.waitForFunction(() => window.FILM && window.FILM.ready, null, { timeout: 30000 });

  const anchorsPath = path.join(ROOT, 'footage-anchors.js');
  const prev = fs.existsSync(anchorsPath) ? fs.readFileSync(anchorsPath, 'utf8') : '';
  const ANCH = prev ? JSON.parse(prev.slice(prev.indexOf('=') + 1, prev.lastIndexOf(';'))) : {};
  const footPath = path.join(ROOT, 'tools/footage.json');
  const FOOT = fs.existsSync(footPath) ? JSON.parse(fs.readFileSync(footPath, 'utf8')) : {};

  for (const name of names) {
    const S = SHOTS[name];
    await page.evaluate((n) => window.FILM.setShot(n), name);
    if (anchorsOnly) {
      const n = S.still ? 1 : Math.round(S.dur * FPS);
      const frames = [];
      for (let f = 0; f < n; f++) frames.push(await page.evaluate((tt) => window.FILM.project(tt), f / FPS));
      ANCH[name] = frames;
      console.log('anchors', name, n, JSON.stringify(frames[0]));
      continue;
    }
    if (probe || S.still) {
      const times = S.still ? [0] : S.keys.map((k) => k[0]);
      for (const [i, t] of times.entries()) {
        const r = await page.evaluate((tt) => window.FILM.frame(tt), Math.min(t, (S.dur || 1) - 0.05));
        const file = S.still && !probe ? path.join(outDir, `${name}.jpg`) : path.join(ROOT, `renders/probe-${name}-${i}.jpg`);
        fs.writeFileSync(file, Buffer.from(r.jpeg.split(',')[1], 'base64'));
        console.log(name, 't=' + t, '→', path.relative(ROOT, file), JSON.stringify(r.anchors));
      }
      continue;
    }
    const n = Math.round(S.dur * FPS);
    const out = path.join(outDir, `${name}.mp4`);
    const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    const frames = [];
    const t0 = Date.now();
    for (let f = 0; f < n; f++) {
      const r = await page.evaluate((tt) => window.FILM.frame(tt), f / FPS);
      frames.push(r.anchors);
      if (!ff.stdin.write(Buffer.from(r.jpeg.split(',')[1], 'base64'))) await new Promise((ok) => ff.stdin.once('drain', ok));
      if (f % 60 === 0) console.log(`${name} ${f}/${n} (${((Date.now() - t0) / (f + 1)).toFixed(0)} ms/frame)`);
    }
    ff.stdin.end();
    await new Promise((ok) => ff.on('close', ok));
    ANCH[name] = frames;
    FOOT[S.scene] = { src: `assets/footage/${name}.mp4`, shot: name, frames: n };
    console.log('wrote', path.relative(ROOT, out), n, 'frames');
  }
  if (!probe) {
    if (anchorsOnly) { fs.writeFileSync(anchorsPath, '// generated by tools/render3d/render.cjs: do not edit by hand\nwindow.ANCHORS = ' + JSON.stringify(ANCH) + ';\n'); await browser.close(); return; }
    fs.writeFileSync(anchorsPath, '// generated by tools/render3d/render.cjs: do not edit by hand\nwindow.ANCHORS = ' + JSON.stringify(ANCH) + ';\n');
    fs.writeFileSync(footPath, JSON.stringify(FOOT, null, 1));
  }
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
