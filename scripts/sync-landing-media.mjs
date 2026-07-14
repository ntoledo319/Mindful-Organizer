import { createHash } from 'node:crypto';
import { copyFileSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const sourceDir = join(root, 'tmp', 'artifacts', 'final-screenshots');
const destinationDir = join(root, 'landing', 'assets', 'screens');
const selected = ['01-today.png', '04-rhythm.png', '03-reflect.png'];

function assertInsideRoot(path) {
  const resolved = resolve(path);
  if (resolved !== root && !resolved.startsWith(`${root}${sep}`)) {
    throw new Error(`Refusing path outside workspace: ${resolved}`);
  }
  return resolved;
}

const sourceManifestPath = assertInsideRoot(join(sourceDir, 'manifest.json'));
const sourceManifest = JSON.parse(readFileSync(sourceManifestPath, 'utf8'));
if (sourceManifest.buildRef !== '8172603b62c2457696608c145511bd3fe92429d4') {
  throw new Error(`Unexpected screenshot buildRef: ${sourceManifest.buildRef}`);
}

mkdirSync(assertInsideRoot(destinationDir), { recursive: true });
const copied = [];

for (const file of selected) {
  const record = sourceManifest.images.find((image) => image.file === file);
  if (!record) throw new Error(`Screenshot manifest is missing ${file}`);

  const source = assertInsideRoot(join(sourceDir, file));
  const bytes = readFileSync(source);
  const sha256 = createHash('sha256').update(bytes).digest('hex');
  if (sha256 !== record.sha256) {
    throw new Error(`${file} does not match the accepted screenshot manifest`);
  }

  const destination = assertInsideRoot(join(destinationDir, file));
  copyFileSync(source, destination);
  copied.push({ file, width: record.width, height: record.height, bytes: bytes.length, sha256 });
}

const outputManifest = {
  sourceBuildRef: sourceManifest.buildRef,
  containsFictionalDemoData: sourceManifest.containsFictionalDemoData,
  files: copied,
};
writeFileSync(
  assertInsideRoot(join(destinationDir, 'manifest.json')),
  `${JSON.stringify(outputManifest, null, 2)}\n`,
);

console.log(
  `Synced ${copied.length} accepted product frames to ${relative(root, destinationDir)}`,
);
