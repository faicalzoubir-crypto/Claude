// Render the news map to PNG: node news/2026-11-15-gleibat/render.mjs
import { createRequire } from "module";
import path from "path";
import { fileURLToPath } from "url";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const here = path.dirname(fileURLToPath(import.meta.url));

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1350 } });
await page.goto(`file://${here}/news.html`);
await page.waitForSelector("body[data-ready='1']");
await page.locator("#frame").screenshot({ path: `${here}/gleibat-el-foula-2026-11-15.png` });
console.log("wrote gleibat-el-foula-2026-11-15.png");
await browser.close();
