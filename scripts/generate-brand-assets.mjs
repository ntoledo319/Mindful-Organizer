// Deterministic, rights-clean Paulatim artwork generated entirely from code in
// this repository. No stock art, model output, fonts, or outside source files
// are used. The visual language mirrors the in-app PaulatimMark: a warm threshold
// held inside a calm, dark-green room.
import { Jimp, JimpMime } from 'jimp';
import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const out = join(root, 'resources');
mkdirSync(out, { recursive: true });

const clamp = (value, min = 0, max = 1) => Math.min(max, Math.max(min, value));
const mix = (a, b, amount) => a + (b - a) * clamp(amount);
const smoothstep = (a, b, value) => {
  const t = clamp((value - a) / (b - a));
  return t * t * (3 - 2 * t);
};
const hash = (x, y, seed = 0) => {
  const value = Math.sin(x * 12.9898 + y * 78.233 + seed * 37.719) * 43758.5453;
  return value - Math.floor(value);
};
const distanceToSegment = (px, py, ax, ay, bx, by) => {
  const dx = bx - ax;
  const dy = by - ay;
  const length2 = dx * dx + dy * dy;
  const t = length2 ? clamp(((px - ax) * dx + (py - ay) * dy) / length2) : 0;
  return Math.hypot(px - (ax + t * dx), py - (ay + t * dy));
};
const roundedBoxDistance = (x, y, halfW, halfH, radius) => {
  const qx = Math.abs(x) - halfW + radius;
  const qy = Math.abs(y) - halfH + radius;
  return Math.hypot(Math.max(qx, 0), Math.max(qy, 0)) + Math.min(Math.max(qx, qy), 0) - radius;
};

function setPixel(data, index, rgb, alpha = 1) {
  data[index] = Math.round(clamp(rgb[0], 0, 255));
  data[index + 1] = Math.round(clamp(rgb[1], 0, 255));
  data[index + 2] = Math.round(clamp(rgb[2], 0, 255));
  data[index + 3] = Math.round(clamp(alpha) * 255);
}

async function makeIcon() {
  const size = 1536;
  const image = new Jimp({ width: size, height: size, color: 0x00000000 });
  const data = image.bitmap.data;

  image.scan(0, 0, size, size, (x, y, index) => {
    const u = (x + 0.5) / size;
    const v = (y + 0.5) / size;
    const box = roundedBoxDistance(u - 0.5, v - 0.5, 0.455, 0.455, 0.155);
    const alpha = 1 - smoothstep(-0.0015, 0.0015, box);
    if (alpha <= 0) return;

    const vignette = clamp(Math.hypot(u - 0.46, v - 0.43) / 0.72);
    const glow = Math.exp(-Math.pow(Math.hypot(u - 0.5, v - 0.58) / 0.25, 2));
    const grain = (hash(x, y, 4) - 0.5) * 3.2;
    let rgb = [
      mix(41, 13, vignette) + glow * 5 + grain,
      mix(76, 31, vignette) + glow * 3 + grain,
      mix(62, 27, vignette) + grain,
    ];

    const segments = [
      [0.27, 0.49, 0.5, 0.27],
      [0.5, 0.27, 0.73, 0.49],
      [0.32, 0.455, 0.32, 0.73],
      [0.68, 0.455, 0.68, 0.73],
      [0.32, 0.73, 0.68, 0.73],
      [0.445, 0.73, 0.445, 0.585],
      [0.555, 0.73, 0.555, 0.585],
    ];
    let lineDistance = Infinity;
    for (const [ax, ay, bx, by] of segments) {
      lineDistance = Math.min(lineDistance, distanceToSegment(u, v, ax, ay, bx, by));
    }
    const line = 1 - smoothstep(0.012, 0.017, lineDistance);
    const emberDistance = Math.hypot(u - 0.5, v - 0.535);
    const ember = 1 - smoothstep(0.018, 0.028, emberDistance);
    const lineColor = [245, 232, 207];
    const emberColor = [226, 115, 82];
    rgb = rgb.map((channel, i) => mix(channel, lineColor[i], line));
    rgb = rgb.map((channel, i) => mix(channel, emberColor[i], ember));
    setPixel(data, index, rgb, alpha);
  });

  image.resize({ w: 1024, h: 1024 });
  writeFileSync(join(out, 'app-icon.png'), await image.getBuffer(JimpMime.png));
}

async function makeHero() {
  const width = 2048;
  const height = 1024;
  const image = new Jimp({ width, height, color: 0x000000ff });
  const data = image.bitmap.data;

  image.scan(0, 0, width, height, (x, y, index) => {
    const u = (x + 0.5) / width;
    const v = (y + 0.5) / height;
    const rightLight = smoothstep(0.58, 1, u);
    const vertical = smoothstep(0.1, 0.95, v);
    const beamCenter = 0.17 + (1 - u) * 0.49;
    const beam = Math.exp(-Math.pow((v - beamCenter) / 0.14, 2)) * smoothstep(0.18, 0.92, u);
    const lowerBeam = Math.exp(-Math.pow((v - beamCenter - 0.18) / 0.09, 2)) * smoothstep(0.4, 1, u);
    const grain = (hash(x, y, 9) - 0.5) * 7;

    let rgb = [
      mix(19, 63, rightLight) + beam * 78 + lowerBeam * 36 + grain,
      mix(43, 70, rightLight) + beam * 57 + lowerBeam * 25 + grain,
      mix(36, 52, rightLight) + beam * 28 + lowerBeam * 12 + grain,
    ];

    // Window glow and mullions.
    if (u > 0.905) {
      const windowGlow = smoothstep(0.905, 0.99, u);
      rgb = rgb.map((channel, i) => mix(channel, [255, 226, 165][i], 0.36 + windowGlow * 0.58));
      const mullion = Math.min(Math.abs(u - 0.922), Math.abs(u - 0.985));
      if (mullion < 0.008) rgb = [92, 75, 54];
    }

    // The table is a broad, grounded plane rather than a floating card.
    const tableTop = 0.785 - Math.max(0, u - 0.5) * 0.08;
    if (u > 0.46 && v > tableTop && v < 0.91) {
      const wood = (hash(Math.floor(x / 7), Math.floor(y / 3), 17) - 0.5) * 9;
      rgb = [122 + rightLight * 48 + wood, 78 + rightLight * 35 + wood, 48 + rightLight * 18 + wood];
    }
    if (u > 0.49 && u < 0.54 && v >= 0.89) rgb = [62, 43, 31];
    if (u > 0.88 && u < 0.92 && v >= 0.86) rgb = [62, 43, 31];

    // Closed notebook: two softly offset slabs.
    const inBook = u > 0.67 && u < 0.83 && v > 0.745 && v < 0.81;
    if (inBook) {
      const edge = Math.min(u - 0.67, 0.83 - u, v - 0.745, 0.81 - v);
      rgb = edge < 0.004 ? [105, 89, 69] : [230, 219, 192];
    }
    if (u > 0.69 && u < 0.85 && v > 0.725 && v < 0.778) rgb = [244, 235, 211];

    // Cup and handle, kept deliberately illustrative.
    const cup = Math.pow((u - 0.60) / 0.038, 2) + Math.pow((v - 0.755) / 0.055, 2);
    const cupRim = Math.pow((u - 0.60) / 0.039, 2) + Math.pow((v - 0.71) / 0.012, 2);
    const handleOuter = Math.pow((u - 0.637) / 0.027, 2) + Math.pow((v - 0.748) / 0.033, 2);
    const handleInner = Math.pow((u - 0.637) / 0.015, 2) + Math.pow((v - 0.748) / 0.021, 2);
    if (cup < 1 && v > 0.705) rgb = [201, 187, 158];
    if (cupRim < 1) rgb = cupRim < 0.55 ? [53, 46, 38] : [231, 218, 190];
    if (handleOuter < 1 && handleInner > 1) rgb = [193, 176, 145];

    // A small rising thread of steam.
    const steamX = 0.6 + Math.sin(v * 96) * 0.007;
    const steam = Math.abs(u - steamX) < 0.0017 && v > 0.61 && v < 0.695;
    if (steam) rgb = rgb.map((channel) => mix(channel, 241, 0.45));

    // Subtle edge darkening keeps text readable over the left half.
    const vignette = smoothstep(0.38, 0.75, Math.hypot((u - 0.48) * 0.85, v - 0.48));
    rgb = rgb.map((channel) => channel * (1 - vignette * 0.18 * (1 - rightLight)));
    setPixel(data, index, rgb, 1);
  });

  writeFileSync(join(out, 'hero-illustration.png'), await image.getBuffer(JimpMime.png));
}

await Promise.all([makeIcon(), makeHero()]);
console.log('Generated rights-clean resources/app-icon.png and resources/hero-illustration.png');
