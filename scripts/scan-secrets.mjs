// Lightweight repository secret gate. Reports only rule + path + line number;
// matched values are never printed. This complements GitHub's remote scanning
// without adding another dependency or uploading the working tree elsewhere.
import { execFileSync } from 'node:child_process';
import { lstatSync, readFileSync } from 'node:fs';
import { dirname, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const tracked = execFileSync('git', ['ls-files', '--cached', '--others', '--exclude-standard', '-z'], { cwd: root })
  .toString('utf8')
  .split('\0')
  .filter(Boolean);

const rules = [
  ['private-key', /-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----/],
  ['github-token', /\b(?:ghp|gho|ghu|ghs|github_pat)_[A-Za-z0-9_]{20,}\b/],
  ['aws-access-key', /\b(?:AKIA|ASIA)[A-Z0-9]{16}\b/],
  ['openai-key', /\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b/],
  ['stripe-secret', /\b(?:sk|rk)_(?:live|test)_[A-Za-z0-9]{16,}\b/],
  ['google-api-key', /\bAIza[0-9A-Za-z_-]{30,}\b/],
];

const findings = [];
for (const relative of tracked) {
  const absolute = resolve(root, relative);
  if (!(absolute === root || absolute.startsWith(`${root}${sep}`))) {
    throw new Error(`Refusing path outside workspace: ${relative}`);
  }
  const stat = lstatSync(absolute);
  if (!stat.isFile() || stat.isSymbolicLink() || stat.size > 2_000_000) continue;
  const buffer = readFileSync(absolute);
  if (buffer.includes(0)) continue;
  const lines = buffer.toString('utf8').split(/\r?\n/);
  lines.forEach((line, index) => {
    for (const [rule, pattern] of rules) {
      if (pattern.test(line)) findings.push(`${relative}:${index + 1} (${rule})`);
    }
  });
}

if (findings.length) {
  console.error(`Secret scan failed with ${findings.length} potential finding(s):`);
  findings.forEach((finding) => console.error(`- ${finding}`));
  process.exit(1);
}

console.log(`Secret scan passed across ${tracked.length} tracked paths.`);
