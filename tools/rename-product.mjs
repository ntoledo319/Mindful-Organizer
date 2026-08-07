#!/usr/bin/env node
// Product rename sweep for Hearth -> <new name>.
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
//   node tools/rename-product.mjs --to Ember                 # dry run (default)
//   node tools/rename-product.mjs --to Ember --apply
//   node tools/rename-product.mjs --to Ember --identity ToledoTechnologies.Ember --apply
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
  'HANDOFF.md',
  'PROJECT_TRACKER.md',
]);

// tools/ is excluded outright: this script carries "Hearth" literals in its own
// rules table and doc comments. Letting the sweep rewrite itself would corrupt
// the rules and make a second run a no-op against the wrong source string.
const PRESERVE_PREFIXES = ['docs/project/archive/', 'tools/'];

const TEXT_EXT = new Set([
  '.ts', '.tsx', '.js', '.mjs', '.cjs', '.json', '.md', '.html', '.css',
  '.yml', '.yaml', '.txt',
]);

function parseArgs(argv) {
  const args = { apply: false };
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === '--to') args.to = argv[i + 1];
    else if (argv[i] === '--identity') args.identity = argv[i + 1];
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
function buildRules(to, identity) {
  const lower = to.toLowerCase();
  return [
    ['ToledoTechnologies.Hearth', identity || `ToledoTechnologies.${to}`],
    ['Hearth-Setup', `${to}-Setup`],
    ['Hearth-Portable', `${to}-Portable`],
    ['hearth-msix', `${lower}-msix`],
    ['hearth-store-screenshots', `${lower}-store-screenshots`],
    ['hearth-appx', `${lower}-appx`],
    ['HEARTH_', `${to.toUpperCase()}_`],
    ['Hearth', to],
    ['hearth', lower],
  ];
}

function applyRules(text, rules) {
  let out = text;
  let count = 0;
  for (const [from, into] of rules) {
    const parts = out.split(from);
    count += parts.length - 1;
    out = parts.join(into);
  }
  return { out, count };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (!args.to) {
    console.error('Usage: node tools/rename-product.mjs --to <NewName> [--identity <Pkg.Identity>] [--apply]');
    process.exit(2);
  }

  const rules = buildRules(args.to, args.identity);
  const files = await walk(ROOT);

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
    if (!/[Hh]earth/.test(text)) continue;

    if (isPreserved(rel)) {
      const hits = (text.match(/[Hh]earth/g) || []).length;
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
  console.log(`\n${mode} — Hearth -> ${args.to}\n`);
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
  1. Reserve the new name in Partner Center (owner action).
  2. Decide whether identityName can change on product 9PLRSZZMFPJH or whether
     a new product reservation is required. This determines whether the
     existing submission is edited or replaced.
  3. Regenerate icons and Store assets: npm run icons && npm run winstore-assets
  4. Run the full gate suite, then a fresh CI candidate cycle.
  5. Add a forward note to the preserved ledgers by hand.
`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
