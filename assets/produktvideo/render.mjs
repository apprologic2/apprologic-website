// Nimmt produktvideo.html Bild für Bild mit Microsoft Edge auf und erzeugt daraus eine MP4.
// Liegt musik.wav im selben Ordner (erzeugt mit: python musik.py), wird sie als Tonspur eingemischt.
// Benötigt (nicht Teil des Projekts): npm i puppeteer-core ffmpeg-static
// Aufruf:  node render.mjs                 → video-ohne-ton.mp4 und service-pacemaker.mp4 (mit Musik)
//          node render.mjs --ton           → nur Musik neu einmischen, ohne die Bilder neu aufzunehmen
//          node render.mjs --frames 3 20   → nur Standbilder bei 3 s und 20 s (zum Prüfen)
import { createRequire } from "node:module";
import { spawn } from "node:child_process";
import { existsSync, copyFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import path from "node:path";

const require = createRequire(process.env.RENDER_MODULES ? path.join(process.env.RENDER_MODULES, "x.js") : import.meta.url);
const ffmpeg = require("ffmpeg-static");

const FPS = 30;
const here = path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Z]:)/, "$1"));
const silent = path.join(here, "video-ohne-ton.mp4");
const music = path.join(here, "musik.wav");
const out = path.join(here, "service-pacemaker.mp4");

const run = (args, stdin = "ignore") => spawn(ffmpeg, args, { stdio: [stdin, "ignore", "inherit"] });
const done = (proc) => new Promise((r) => proc.on("close", r));

async function record() {
  const puppeteer = require("puppeteer-core");
  const url = pathToFileURL(path.join(here, "produktvideo.html")).href + "?render";
  const edge = process.env.EDGE || "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe";
  const browser = await puppeteer.launch({ executablePath: edge, headless: true, args: ["--hide-scrollbars"] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });
  await page.goto(url, { waitUntil: "networkidle0" });
  await page.evaluate(() => document.fonts.ready);
  const DURATION = await page.evaluate(() => DURATION); // Länge aus produktvideo.html

  const idx = process.argv.indexOf("--frames");
  if (idx > 0) {
    for (const s of process.argv.slice(idx + 1)) {
      await page.evaluate((t) => window.render(t), +s);
      await page.screenshot({ path: path.join(process.env.OUT_DIR || here, `frame-${s}.png`) });
    }
    await browser.close();
    return false;
  }
  const ff = run(["-y", "-f", "image2pipe", "-framerate", String(FPS), "-i", "-",
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "slow", "-crf", "18", "-movflags", "+faststart", silent], "pipe");
  const total = FPS * DURATION;
  for (let i = 0; i < total; i++) {
    await page.evaluate((t) => window.render(t), i / FPS);
    const buf = await page.screenshot({ type: "jpeg", quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once("drain", r));
    if (i % 150 === 0) console.log(`${Math.round((i / total) * 100)} %`);
  }
  ff.stdin.end();
  await done(ff);
  await browser.close();
  return true;
}

if (process.argv.includes("--ton") || await record()) {
  if (existsSync(music)) {
    await done(run(["-y", "-i", silent, "-i", music, "-map", "0:v", "-map", "1:a",
      "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out]));
  } else {
    copyFileSync(silent, out);
  }
  console.log("Fertig:", out);
}
