import { chromium } from "playwright";
import fs from "node:fs";
import path from "node:path";

/** Read environment variables with defaults */
const url = process.env.TARGET_URL;
const outPath = process.env.SCREENSHOT_PATH || "assets/img/homepage.png";
const width = parseInt(process.env.VIEWPORT_WIDTH || "1200", 10);
const height = parseInt(process.env.VIEWPORT_HEIGHT || "800", 10);
const deviceScaleFactor = parseInt(process.env.DEVICE_SCALE_FACTOR || "2", 10);

const waitForSelector = (process.env.WAIT_FOR_SELECTOR || "").trim();
const waitForSelectorTimeout = parseInt(
  process.env.WAIT_FOR_SELECTOR_TIMEOUT_MS || "15000",
  10
);

/** Ensure the output directory exists */
function ensureDirSync(filePath) {
  const dir = path.dirname(filePath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

async function main() {
  ensureDirSync(outPath);

  // Launch a headless Chromium browser
  const browser = await chromium.launch();

  // Create a clean context with your desired viewport & pixel density
  const context = await browser.newContext({
    viewport: { width, height },
    deviceScaleFactor
  });

  const page = await context.newPage();

  // Navigate to your site and wait until network is quiet (good default for static sites)
  await page.goto(url, { waitUntil: "networkidle" });

  // Optionally wait for a specific element to be present (hero/header/etc.)
  if (waitForSelector) {
    await page.waitForSelector(waitForSelector, {
      timeout: waitForSelectorTimeout
    });
  }

  // Take the screenshot
  await page.screenshot({ path: outPath });

  await browser.close();
}

// Run and surface non-zero exit on error (so Actions fails visibly)
main().catch((err) => {
  console.error(err);
  process.exit(1);
});
