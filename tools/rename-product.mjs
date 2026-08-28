#!/usr/bin/env node
// Product rename sweep for <old name> -> <new name>.
//
// Lives in tools/ deliberately: scripts/** is inside windows-store.yml's path
// filter, so adding this there would trigger an MSIX rebuild and mint another
// decoy artifact. tools/ triggers nothing.
//
// POLICY - the important part:
//   REWRITE   forward-facing identity, product copy, and UI strings.
//   PRESERVE  historical ledgers. revenue/METRICS.md, revenue/DECISIONS.md,
//             docs/project/REPO_HISTORY.md, docs/project/VERIFICATION_LOG.md
//             and the archives record things that happened to a product that
//             WAS named Hearth. Rewriting them would falsify the record, which
//             is precisely what AGENTS.md exists to prevent. They get a
//             forward-pointing note instead, written by hand, not by a script.
//
// Usage:
//   node tools/rename-product.mjs --from Hearth --to Ember   # dry run (default)
//   node tools/rename-product.mjs --from Hearth --to Ember --apply
//   node tools/rename-product.mjs --from Hearth --to Ember --identity ToledoTechnologies.Hearth --apply
//
// Run the full gate suite afterwards. This script does not build, commit, or
// push, and it cannot reserve a name in Partner Center.

import { readFileSync, writeFileSync } from 'node:fs';
import { readdir } from 'node:fs/promises';
import { join, relative, extname } from 'node:path';

const ROOT = process.cwd();

const SKIP_DIRS = new Set([
  '.git', 'node_modules', 'tmp', 'dist', 'dist-electron', 'release', 'build',
  'venv312', '.mypy_cache', '.ruff_cache', '.pytest_cache', '.npm-cache',
  '.electron-gyp', '.aider.tags.cache.v4', '.claude', '.qodo', 'coverage',
]);

const PRESERVE = new Set([
  'revenue/METRICS.md',
  'revenue/DECISIONS.md',
  'revenue/MARKET-ANALYSIS-2026-08-07.md',
  'revenue/NAME-RISK-2026-08-07.md',
  'docs/project/REPO_HISTORY.md',
  'docs/project/VERIFICATION_LOG.md',
  'THIRD_PARTY_NOTICES.md',
  'store/WINDOWS-VALIDATION.md',
  'store/GET-LISTED-RUNBOOK.md',
  'store/README.md',
  'store/SCREENSHOTS.md',
  'store/POST_PUBLICATION_DOC_SWEEP.md',
  'store/REPOSITION_KIT.md',
  'store/identity.json',
  'store/listing-metadata.json',
  'CLAUDE.md',
  'README.md',
  'docs/PRIVACY.md',
  'docs/SUPPORT.md',
  'electron-builder.cjs',
  'package.json',
  'package-lock.json',
  'HANDOFF.md',
  'PROJECT_TRACKER.md',
]);

// tools/ is excluded outright: this script carries "Hearth" literals in its own
// rules table and doc comments. Letting the sweep rewrite itself would corrupt
// the rules and make a second run a no-op against the wrong source string.
const PRESERVE_PREFIXES = [
  'docs/project/',
  'docs/strategy/',
  '.github/workflows/',
  'electron/',
  'revenue/',
  'scripts/',
  'src/renderer/lib/',
  'src/shared/',
  'tools/',
];

// These paths intentionally keep implementation namespaces that predate a
// visible rename. They are skipped by the normal sweep. Recovery mode is
// limited to this allowlist so it cannot rewrite arbitrary prose or history.
const STABLE_INTERNAL_PATHS = new Set([
  '.github/workflows/windows-store.yml',
  'electron-builder.cjs',
  'package.json',
  'package-lock.json',
  'electron/dataLifecycle.ts',
  'electron/db.ts',
  'electron/main.ts',
  'electron/preload.ts',
  'electron/presence.ts',
  'electron/screenshot.ts',
  'electron/security/cryptographicDeletion.ts',
  'electron/security/secureFile.ts',
  'scripts/capture-store-screenshots.mjs',
  'scripts/validate-packaged-app.mjs',
  'src/renderer/lib/api.ts',
]);

const TEXT_EXT = new Set([
  '.ts', '.tsx', '.js', '.mjs', '.cjs', '.json', '.md', '.html', '.css',
  '.yml', '.yaml', '.txt',
]);

function parseArgs(argv) {
  const args = { apply: false, from: 'Hearth', restoreStableInternals: false };
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === '--from') args.from = argv[i + 1];
    else if (argv[i] === '--to') args.to = argv[i + 1];
    else if (argv[i] === '--identity') args.identity = argv[i + 1];
    else if (argv[i] === '--restore-stable-internals') args.restoreStableInternals = true;
    else if (argv[i] === '--apply') args.apply = true;
  }
  return args;
}

function isPreserved(rel) {
  if (PRESERVE.has(rel)) return true;
  return PRESERVE_PREFIXES.some((p) => rel.startsWith(p));
}

async function walk(dir, out = []) {
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    if (entry.isDirectory()) {
      if (SKIP_DIRS.has(entry.name)) continue;
      await walk(join(dir, entry.name), out);
    } else if (entry.isFile() && TEXT_EXT.has(extname(entry.name))) {
      out.push(join(dir, entry.name));
    }
  }
  return out;
}

// Order matters: the most specific replacement runs first so the generic
// word-level rule cannot corrupt a package identity it has already rewritten.
function buildRules(from, to, identity) {
  const fromLower = from.toLowerCase();
  const toLower = to.toLowerCase();
  const escapedFrom = from.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const escapedFromLower = fromLower.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const rules = [];
  if (identity) rules.push([`ToledoTechnologies.${from}`, identity]);
  rules.push(
    [`${from}-Setup`, `${to}-Setup`],
    [`${from}-Portable`, `${to}-Portable`],
    [`${fromLower}-msix`, `${toLower}-msix`],
    [`${fromLower}-store-screenshots`, `${toLower}-store-screenshots`],
    [`${fromLower}-appx`, `${toLower}-appx`],
    [`${from.toUpperCase()}_`, `${to.toUpperCase()}_`],
    [new RegExp(`\\b${escapedFrom}\\b`, 'g'), to],
    [new RegExp(`\\b${escapedFromLower}\\b`, 'g'), toLower],
  );
  return rules;
}

// A visible rename must not silently change persisted data names, preload/API
// contracts, CI harness variables, or the AppX application ID. Those values
// are implementation namespaces, not branding. Keeping them stable protects
// upgrades and lets an existing install keep finding its encrypted profile.
function buildStableInternalRestoreRules(from, to) {
  const fromLower = from.toLowerCase();
  const toLower = to.toLowerCase();
  return [
    [`${to.toUpperCase()}_`, `${from.toUpperCase()}_`],
    [`--${toLower}-screenshot`, `--${fromLower}-screenshot`],
    [`__${toLower}Shot`, `__${fromLower}Shot`],
    [`window.${toLower}Presence`, `window.${fromLower}Presence`],
    [`window.${toLower}`, `window.${fromLower}`],
    [`exposeInMainWorld('${toLower}Presence'`, `exposeInMainWorld('${fromLower}Presence'`],
    [`exposeInMainWorld('${toLower}'`, `exposeInMainWorld('${fromLower}'`],
    [`.${toLower}-release-validation`, `.${fromLower}-release-validation`],
    [`${toLower}.secure.migration-backup`, `${fromLower}.secure.migration-backup`],
    [`${toLower}.secure.backup`, `${fromLower}.secure.backup`],
    [`${toLower}.secure`, `${fromLower}.secure`],
    [`${toLower}.deleting`, `${fromLower}.deleting`],
    [`${toLower}.key`, `${fromLower}.key`],
    [`${toLower}.db`, `${fromLower}.db`],
    [`${toLower}-delete-v1`, `${fromLower}-delete-v1`],
    [`${toLower}-personal-data`, `${fromLower}-personal-data`],
    [`io.${toLower}project.${toLower}`, `io.${fromLower}project.${fromLower}`],
    [`applicationId: '${to}'`, `applicationId: '${from}'`],
    [`"name": "${toLower}"`, `"name": "${fromLower}"`],
    [`${toLower}-test`, `${fromLower}-test`],
  ];
}

function applyRules(text, rules) {
  let out = text;
  let count = 0;
  for (const [source, into] of rules) {
    const parts = out.split(source);
    count += parts.length - 1;
    out = parts.join(into);
  }
  return { out, count };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (!args.from || !args.to) {
    console.error('Usage: node tools/rename-product.mjs --from <OldName> --to <NewName> [--identity <Pkg.Identity>] [--apply]');
    process.exit(2);
  }

  const stableInternalRules = buildStableInternalRestoreRules(args.from, args.to);
  const rules = args.restoreStableInternals
    ? stableInternalRules
    : [...buildRules(args.from, args.to, args.identity), ...stableInternalRules];
  const files = await walk(ROOT);
  const scanName = args.restoreStableInternals ? args.to : args.from;
  const sourcePattern = new RegExp(scanName.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi');

  let rewritten = 0;
  let occurrences = 0;
  const preserved = [];
  const changes = [];

  for (const file of files) {
    const rel = relative(ROOT, file);
    let text;
    try {
      text = readFileSync(file, 'utf8');
    } catch {
      continue;
    }
    if (!sourcePattern.test(text)) continue;
    sourcePattern.lastIndex = 0;

    if (args.restoreStableInternals && !STABLE_INTERNAL_PATHS.has(rel)) continue;

    if (!args.restoreStableInternals && isPreserved(rel)) {
      const hits = (text.match(sourcePattern) || []).length;
      sourcePattern.lastIndex = 0;
      preserved.push([rel, hits]);
      continue;
    }

    const { out, count } = applyRules(text, rules);
    if (out === text) continue;
    changes.push([rel, count]);
    rewritten += 1;
    occurrences += count;
    if (args.apply) writeFileSync(file, out, 'utf8');
  }

  const mode = args.apply ? 'APPLIED' : 'DRY RUN (no files written)';
  const action = args.restoreStableInternals
    ? `restore stable ${args.from} internal namespaces after ${args.to} rename`
    : `${args.from} -> ${args.to}`;
  console.log(`\n${mode} — ${action}\n`);
  console.log(`Rewrite: ${rewritten} files, ${occurrences} occurrences`);
  for (const [rel, n] of changes.sort((a, b) => b[1] - a[1]).slice(0, 20)) {
    console.log(`  ${String(n).padStart(4)}  ${rel}`);
  }
  if (changes.length > 20) console.log(`  ... and ${changes.length - 20} more files`);

  const preservedTotal = preserved.reduce((sum, [, n]) => sum + n, 0);
  console.log(`\nPreserved (historical record, untouched): ${preserved.length} files, ${preservedTotal} occurrences`);
  for (const [rel, n] of preserved.sort((a, b) => b[1] - a[1])) {
    console.log(`  ${String(n).padStart(4)}  ${rel}`);
  }

  console.log(`
Not done by this script — owner or follow-up work:
  1. Confirm the new name is reserved on the intended Partner Center product.
  2. Preserve the Partner Center-assigned identity unless that exact page
     explicitly reports a different observed value.
  3. Regenerate icons and Store assets: npm run icons && npm run winstore-assets
  4. Run the full gate suite, then a fresh CI candidate cycle.
  5. Add a forward note to the preserved ledgers by hand.
`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
