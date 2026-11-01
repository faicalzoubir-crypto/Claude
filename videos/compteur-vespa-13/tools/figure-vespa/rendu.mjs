// Rend la figure de la Vespa debout (figure.html) en image fixe.
//   node tools/figure-vespa/rendu.mjs <sortie.png> [paramètres d'URL, ex. "cam=3.6,1.9,3.4&tgt=0,0.62,0.62&fov=36"]
// Écrit l'image et affiche en JSON la position de la roue avant dans l'image.
import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { dirname, join, extname } from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const ICI = dirname(fileURLToPath(import.meta.url));
const [sortie, params = ""] = process.argv.slice(2);
if (!sortie) throw new Error("usage : rendu.mjs <sortie.png> [paramètres]");

const types = { ".html": "text/html", ".js": "text/javascript" };
const serveur = createServer(async (req, res) => {
  try {
    const chemin = join(ICI, decodeURIComponent(new URL(req.url, "http://x").pathname));
    if (!chemin.startsWith(ICI)) throw new Error("hors dossier");
    res.writeHead(200, { "content-type": types[extname(chemin)] || "application/octet-stream" });
    res.end(await readFile(chemin));
  } catch {
    res.writeHead(404).end();
  }
});
await new Promise((ok) => serveur.listen(0, "127.0.0.1", ok));
const port = serveur.address().port;
const q = new URLSearchParams(params);
const W = +(q.get("w") || 2238), H = +(q.get("h") || 1742);

const navigateur = await chromium.launch({ args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"] });
const page = await navigateur.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
page.on("pageerror", (e) => console.error("erreur page :", e.message));
await page.goto(`http://127.0.0.1:${port}/figure.html?${params}`);
await page.waitForFunction(() => window.__done === true, null, { timeout: 60000 });
await page.locator("#c").screenshot({ path: sortie });
console.log(JSON.stringify(await page.evaluate(() => window.__figure)));
await navigateur.close();
serveur.close();
