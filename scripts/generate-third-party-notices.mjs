import { readFile, readdir, realpath, writeFile } from 'node:fs/promises';
import { dirname, join, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const lock = JSON.parse(await readFile(join(root, 'package-lock.json'), 'utf8'));
const packageEntries = Object.entries(lock.packages)
  .filter(([path, metadata]) => path.startsWith('node_modules/') && !metadata.dev && !metadata.devOptional)
  .concat([['node_modules/electron', lock.packages['node_modules/electron']]])
  .filter(([, metadata]) => Boolean(metadata));

const seen = new Set();
const packages = [];

for (const [relativePath, metadata] of packageEntries) {
  if (seen.has(relativePath)) continue;
  seen.add(relativePath);

  const directory = join(root, relativePath);
  const resolvedDirectory = await realpath(directory);
  if (!resolvedDirectory.startsWith(`${root}${sep}`)) {
    throw new Error(`Refusing to read package outside workspace: ${relativePath}`);
  }

  const manifest = JSON.parse(await readFile(join(resolvedDirectory, 'package.json'), 'utf8'));
  const files = await readdir(resolvedDirectory);
  const licenseFile = files
    .filter((name) => /^(licen[cs]e|copying|copyright)(\.|$)/i.test(name))
    .sort((a, b) => a.localeCompare(b))[0];
  const licenseText = licenseFile
    ? await readFile(join(resolvedDirectory, licenseFile), 'utf8')
    : null;
  const repository =
    typeof manifest.repository === 'string'
      ? manifest.repository
      : manifest.repository?.url ?? metadata.resolved ?? 'Not declared';

  packages.push({
    name: manifest.name ?? relativePath.replace(/^node_modules\//, ''),
    version: manifest.version ?? metadata.version ?? 'unknown',
    license: manifest.license ?? metadata.license ?? 'UNDECLARED',
    repository: String(repository).replace(/^git\+/, '').replace(/\.git$/, ''),
    licenseFile: licenseFile ?? null,
    licenseText,
  });
}

packages.sort((a, b) => `${a.name}@${a.version}`.localeCompare(`${b.name}@${b.version}`));

const forbidden = packages.filter(({ license }) =>
  /AGPL|LGPL|GPL|SSPL|CDDL|EUPL|EPL|MPL/i.test(String(license)),
);
if (forbidden.length) {
  throw new Error(
    `Copyleft license review required: ${forbidden.map((pkg) => `${pkg.name} (${pkg.license})`).join(', ')}`,
  );
}

const sections = packages.map((pkg) => {
  const notice = pkg.licenseText
    ? pkg.licenseText
        .replace(/\r\n?/g, '\n')
        .trim()
        .split('\n')
        .map((line) => {
          const clean = line.trimEnd();
          return clean ? `    ${clean}` : '';
        })
        .join('\n')
    : '    No license file was present in the installed package. Review the declared SPDX license before release.';
  return `## ${pkg.name}@${pkg.version}

- Declared license: ${pkg.license}
- Source: ${pkg.repository}
- Installed notice: ${pkg.licenseFile ?? 'none'}

${notice}`;
});

const output = `# Paulatim Third-Party Notices

Generated from the production dependency closure in \`package-lock.json\` plus the Electron runtime. Run \`npm run licenses\` after every dependency change.

Paulatim's own source is licensed under the repository's MIT \`LICENSE\`. The packages below remain subject to their respective licenses. Electron distributions also include \`LICENSES.chromium.html\` for Chromium and other bundled third-party components; electron-builder preserves those runtime notices in packaged applications.

Audit result: ${packages.length} runtime packages; no GPL, AGPL, LGPL, SSPL, CDDL, EUPL, EPL, or MPL declaration detected.

${sections.join('\n\n---\n\n')}
`;

await writeFile(join(root, 'THIRD_PARTY_NOTICES.md'), output, 'utf8');
console.log(`Wrote THIRD_PARTY_NOTICES.md for ${packages.length} runtime packages.`);
