import { spawn } from 'node:child_process';
import { createRequire } from 'node:module';
import { execFileSync } from 'node:child_process';
import { existsSync, mkdirSync, rmSync, unlinkSync } from 'node:fs';
import { dirname, join, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const dataDir = join(root, 'tmp', 'screenshot-data');
const shotDir = join(root, 'store', 'screenshots');
const outputFiles = [
  '01-today.png',
  '02-tasks.png',
  '03-reflect.png',
  '04-rhythm.png',
  '05-onboarding.png',
  'manifest.json',
];

for (const path of [dataDir, shotDir]) {
  const resolved = resolve(path);
  if (!(resolved === root || resolved.startsWith(`${root}${sep}`))) {
    throw new Error(`Refusing screenshot path outside the repository: ${resolved}`);
  }
}

rmSync(dataDir, { recursive: true, force: true });
mkdirSync(dataDir, { recursive: true });
mkdirSync(shotDir, { recursive: true });
for (const name of outputFiles) {
  const path = join(shotDir, name);
  if (existsSync(path)) unlinkSync(path);
}

const head = execFileSync('git', ['rev-parse', '--short=12', 'HEAD'], { cwd: root })
  .toString('utf8')
  .trim();
const dirty = execFileSync('git', ['status', '--porcelain'], { cwd: root }).length > 0;
const buildRef = process.env.AMPLE_SHOT_BUILD_REF || `${head}${dirty ? '-working-tree' : ''}`;
const electronBinary = require('electron');

const child = spawn(electronBinary, [root], {
  cwd: root,
  env: {
    ...process.env,
    AMPLE_SCREENSHOT: '1',
    AMPLE_DATA_DIR: dataDir,
    AMPLE_SHOT_DIR: shotDir,
    AMPLE_SHOT_BUILD_REF: buildRef,
  },
  stdio: 'inherit',
});

let finished = false;
const timeout = setTimeout(() => {
  if (finished) return;
  console.error('Screenshot harness exceeded 150 seconds; terminating the Electron process.');
  child.kill();
  process.exitCode = 1;
}, 150_000);

function finish(code) {
  if (finished) return;
  finished = true;
  clearTimeout(timeout);
  process.exitCode = code;
}

child.once('error', (error) => {
  console.error(`Could not start Electron screenshot harness: ${error.message}`);
  finish(1);
});

child.once('exit', (code, signal) => {
  if (signal) {
    console.error(`Screenshot harness ended from signal ${signal}.`);
    finish(1);
    return;
  }
  finish(code ?? 1);
});
