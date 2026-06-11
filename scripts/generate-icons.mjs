// Derive packaging icon sets from the master brand mark (resources/app-icon.png).
// Produces build/icon.png (Linux/AppImage), build/icon.ico (Windows NSIS), and
// build/icon.icns (macOS dmg/zip). Pure JS (jimp + png-to-ico) plus a hand-rolled
// ICNS writer, so it runs identically on Linux, macOS, and Windows CI runners —
// no ImageMagick, no `iconutil`, no native toolchain.
import Jimp from 'jimp';
import pngToIco from 'png-to-ico';
import { mkdirSync, writeFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const SRC = join(root, 'resources', 'app-icon.png');
const BUILD = join(root, 'build');
mkdirSync(BUILD, { recursive: true });

const master = await Jimp.read(SRC);

const pngAt = async (size) => master.clone().resize(size, size).getBufferAsync(Jimp.MIME_PNG);

// 1) Linux / generic PNG
writeFileSync(join(BUILD, 'icon.png'), await pngAt(512));

// 2) Windows ICO (multi-resolution)
const icoSizes = [16, 24, 32, 48, 64, 128, 256];
const icoPngs = await Promise.all(icoSizes.map(pngAt));
writeFileSync(join(BUILD, 'icon.ico'), await pngToIco(icoPngs));

// 3) macOS ICNS — assemble the container from the standard icon slots.
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
  const data = await pngAt(size);
  const header = Buffer.alloc(8);
  header.write(type, 0, 4, 'ascii');
  header.writeUInt32BE(data.length + 8, 4);
  chunks.push(header, data);
}

const body = Buffer.concat(chunks);
const fileHeader = Buffer.alloc(8);
fileHeader.write('icns', 0, 4, 'ascii');
fileHeader.writeUInt32BE(body.length + 8, 4);
writeFileSync(join(BUILD, 'icon.icns'), Buffer.concat([fileHeader, body]));

console.log('Generated build/icon.png, build/icon.ico, build/icon.icns');
