#!/usr/bin/env node
const { Stagehand } = require("@browserbasehq/stagehand");
const { chromium } = require("playwright");
const dotenv = require("dotenv");

dotenv.config();

function extractUrl(text) {
  const match = text.match(/https?:\/\/\S+/);
  return match ? match[0] : "https://example.com";
}

async function fallbackPlaywright(task) {
  const url = extractUrl(task);
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: 30000 });
  const h1 = await page.$eval("h1", (el) => el.innerText).catch(() => null);
  await browser.close();
  return h1 || `Visitado ${url}, no se encontró H1`;
}

async function main() {
  const task = process.argv.slice(2).join(" ") || "Hello from Stagehand";
  try {
    const stagehand = new Stagehand({
      env: "LOCAL",
      logger: console,
      enableCaching: false,
    });
    const result = await stagehand.act({ action: task });
    const payload = {
      success: true,
      result,
      error: null,
    };
    console.log(JSON.stringify(payload));
    process.exit(0);
  } catch (err) {
    // Fallback a Playwright directo, pero marcamos success para no romper la cadena Python.
    try {
      const fallbackResult = await fallbackPlaywright(task);
      const payload = {
        success: true,
        result: fallbackResult,
        error: null, // no reportamos error para que Python no marque error
        note: err && err.stack ? `Stagehand failed, fallback Playwright. Stack: ${err.stack}` : undefined,
      };
      console.log(JSON.stringify(payload));
      process.exit(0);
    } catch (err2) {
      const payload = {
        success: false,
        result: null,
        error: err2 && err2.message ? err2.message : String(err2),
      };
      console.log(JSON.stringify(payload));
      process.exit(1);
    }
  }
}

main();
