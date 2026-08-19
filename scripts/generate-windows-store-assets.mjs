// Derive Windows Store (MSIX/AppX) visual assets from the master brand mark.
// Produces build/appx/* with the exact filename convention electron-builder
// expects for appx targets. Run with `npm run winstore-assets`.
//
// Required by the Microsoft Store:
//   StoreLogo, Square44x44Logo, Square150x150Logo, Square310x310Logo,
//   Wide310x150Logo, SplashScreen — each at 100%, 125%, 150%, 200%, 400%.
//   Square44x44Logo also needs targetsize variants (16, 24, 32, 48, 256).

import { Jimp, JimpMime } from 'jimp';
import { mkdirSync, writeFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const SRC = join(root, 'resources', 'app-icon.png');
const OUT = join(root, 'build', 'appx');
mkdirSync(OUT, { recursive: true });

const BG = 0xF5F0E6FF; // warm cream opaque — matches the Ample light theme

const master = await Jimp.read(SRC);

async function renderSquare(size, pad = 0) {
  const canvas = new Jimp({ width: size, height: size, color: 0x00000000 });
  if (pad <= 0) {
    const resized = master.clone().resize({ w: size, h: size });
    canvas.composite(resized, 0, 0);
  } else {
    const avail = size;
    const iconSize = Math.floor(avail * (1 - pad));
    const resized = master.clone().resize({ w: iconSize, h: iconSize });
    const x = Math.floor((size - iconSize) / 2);
    const y = Math.floor((size - iconSize) / 2);
    canvas.composite(resized, x, y);
  }
  return canvas.getBuffer(JimpMime.png);
}

async function renderWide(w, h) {
  // Transparent canvas with the squircle centered — the wide tile reads as the
  // mark floating, not a logo pinned to a cream slab.
  const canvas = new Jimp({ width: w, height: h, color: 0x00000000 });
  const logoH = Math.floor(h * 0.6);
  const logoW = logoH;
  const logoY = Math.floor((h - logoH) / 2);
  const logoX = Math.floor((w - logoW) / 2);
  const resized = master.clone().resize({ w: logoW, h: logoH });
  canvas.composite(resized, logoX, logoY);
  return canvas.getBuffer(JimpMime.png);
}

async function renderSplash(w, h) {
  const canvas = new Jimp({ width: w, height: h, color: BG });
  const logoSize = Math.floor(Math.min(w, h) * 0.35);
  const x = Math.floor((w - logoSize) / 2);
  const y = Math.floor((h - logoSize) / 2);
  const resized = master.clone().resize({ w: logoSize, h: logoSize });
  canvas.composite(resized, x, y);
  return canvas.getBuffer(JimpMime.png);
}

const SCALES = [100, 125, 150, 200, 400];

async function writeSquare(name, baseSize, pad) {
  for (const scale of SCALES) {
    const size = Math.floor(baseSize * (scale / 100));
    const buf = await renderSquare(size, pad);
    writeFileSync(join(OUT, `${name}.scale-${scale}.png`), buf);
  }
  const baseBuf = await renderSquare(baseSize, pad);
  writeFileSync(join(OUT, `${name}.png`), baseBuf);
}

async function writeWide() {
  for (const scale of SCALES) {
    const w = Math.floor(310 * (scale / 100));
    const h = Math.floor(150 * (scale / 100));
    const buf = await renderWide(w, h);
    writeFileSync(join(OUT, `Wide310x150Logo.scale-${scale}.png`), buf);
  }
  const baseBuf = await renderWide(310, 150);
  writeFileSync(join(OUT, 'Wide310x150Logo.png'), baseBuf);
}

async function writeSplash() {
  for (const scale of SCALES) {
    const w = Math.floor(620 * (scale / 100));
    const h = Math.floor(300 * (scale / 100));
    const buf = await renderSplash(w, h);
    writeFileSync(join(OUT, `SplashScreen.scale-${scale}.png`), buf);
  }
  const baseBuf = await renderSplash(620, 300);
  writeFileSync(join(OUT, 'SplashScreen.png'), baseBuf);
}

async function writeTargetSizes() {
  const sizes = [16, 24, 32, 48, 256];
  for (const size of sizes) {
    const buf = await renderSquare(size, 0.12);
    writeFileSync(join(OUT, `Square44x44Logo.targetsize-${size}.png`), buf);
  }
}

await writeSquare('StoreLogo', 50, 0.12);
await writeSquare('Square44x44Logo', 44, 0.12);
await writeSquare('Square150x150Logo', 150, 0.08);
await writeSquare('Square310x310Logo', 310, 0.08);
await writeWide();
await writeSplash();
await writeTargetSizes();

console.log(`Generated Windows Store assets in ${OUT}`);
