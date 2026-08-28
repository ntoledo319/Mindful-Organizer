import { createHash } from 'node:crypto';
import { copyFileSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const destinationDir = join(root, 'landing', 'assets', 'screens');
const selected = ['01-today.png', '04-rhythm.png', '03-reflect.png'];

function argumentValue(name) {
  const index = process.argv.indexOf(name);
  return index === -1 ? undefined : process.argv[index + 1];
}

function assertInsideRoot(path) {
  const resolved = resolve(path);
  if (resolved !== root && !resolved.startsWith(`${root}${sep}`)) {
    throw new Error(`Refusing path outside workspace: ${resolved}`);
  }
  return resolved;
}

const sourceArgument = argumentValue('--source');
const expectedBuildRef = argumentValue('--build-ref');
if (!sourceArgument || !expectedBuildRef) {
  throw new Error(
    'Usage: npm run landing:media -- --source <exact-screenshot-directory> --build-ref <exact-candidate-sha>',
  );
}
const sourceDir = assertInsideRoot(resolve(root, sourceArgument));

const sourceManifestPath = assertInsideRoot(join(sourceDir, 'manifest.json'));
const sourceManifest = JSON.parse(readFileSync(sourceManifestPath, 'utf8'));
if (sourceManifest.buildRef !== expectedBuildRef) {
  throw new Error(
    `Unexpected screenshot buildRef: expected ${expectedBuildRef}, got ${sourceManifest.buildRef}`,
  );
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
