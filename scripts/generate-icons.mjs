// Derive packaging icon sets from the master brand mark (resources/app-icon.png).
// Produces build/icon.png (Linux/AppImage), build/icon.ico (Windows NSIS), and
// build/icon.icns (macOS dmg/zip). Uses ImageMagick `convert` plus a hand-rolled
// ICNS writer so it works on Linux CI without macOS-only `iconutil`.
import { execFileSync } from 'node:child_process';
import { mkdirSync, readFileSync, writeFileSync, rmSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const SRC = join(root, 'resources', 'app-icon.png');
const BUILD = join(root, 'build');
const TMP = join(BUILD, '.icontmp');
mkdirSync(BUILD, { recursive: true });
mkdirSync(TMP, { recursive: true });

const convert = (args) => execFileSync('convert', args, { stdio: 'inherit' });

// 1) Linux / generic PNG
convert([SRC, '-resize', '512x512', join(BUILD, 'icon.png')]);

// 2) Windows ICO (multi-resolution)
const icoSizes = [16, 24, 32, 48, 64, 128, 256];
convert([
  SRC,
  ...icoSizes.flatMap((s) => ['(', '-clone', '0', '-resize', `${s}x${s}`, ')']),
  '-delete',
  '0',
  join(BUILD, 'icon.ico'),
]);

// 3) macOS ICNS — build the container ourselves from a set of PNGs.
// Each entry: OSType -> pixel size. (Apple's standard icns slots.)
const icnsSlots = [
  ['icp4', 16],
  ['icp5', 32],
  ['icp6', 64],
  ['ic07', 128],
  ['ic08', 256],
  ['ic09', 512],
  ['ic10', 1024],
];

const chunks = [];
for (const [type, size] of icnsSlots) {
  const png = join(TMP, `${size}.png`);
  convert([SRC, '-resize', `${size}x${size}`, png]);
  const data = readFileSync(png);
  const len = data.length + 8;
  const header = Buffer.alloc(8);
  header.write(type, 0, 4, 'ascii');
  header.writeUInt32BE(len, 4);
  chunks.push(header, data);
}

const body = Buffer.concat(chunks);
const fileHeader = Buffer.alloc(8);
fileHeader.write('icns', 0, 4, 'ascii');
fileHeader.writeUInt32BE(body.length + 8, 4);
writeFileSync(join(BUILD, 'icon.icns'), Buffer.concat([fileHeader, body]));

rmSync(TMP, { recursive: true, force: true });
console.log('Generated build/icon.png, build/icon.ico, build/icon.icns');
