// Render the map preview states to PNG: node preview/render.mjs
import { createRequire } from "module";
import path from "path";
import { fileURLToPath } from "url";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const here = path.dirname(fileURLToPath(import.meta.url));

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
for (const state of ["base", "s2", "s3"]) {
  await page.goto(`file://${here}/map-preview.html?state=${state}`);
  await page.waitForSelector("body[data-ready='1']");
  await page.locator("#frame").screenshot({ path: `${here}/preview-${state}.png` });
  console.log("wrote", `preview-${state}.png`);
}
await browser.close();
