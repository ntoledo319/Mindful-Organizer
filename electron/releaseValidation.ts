/**
 * Exact-package Windows data-lifecycle validation.
 *
 * This module is reachable only when HEARTH_RELEASE_VALIDATION=1 and refuses to
 * run unless HEARTH_DATA_DIR points at a fresh directory containing the
 * explicit sentinel created by CI. It exercises the packaged better-sqlite3
 * binary and Electron safeStorage/DPAPI, not mocks.
 */
import Database from 'better-sqlite3';
import { app } from 'electron';
import { createHash } from 'node:crypto';
import {
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  unlinkSync,
  writeFileSync,
} from 'node:fs';
import { join } from 'node:path';
import { buildPersonalDataExport, deleteAllData } from './dataLifecycle';
import { closeDb, getDb } from './db';
import * as repo from './repo';
import { SCHEMA } from './schema';
import { beginCryptographicDeletion } from './security/cryptographicDeletion';
import { atomicWrite } from './security/secureFile';

const SENTINEL = '.hearth-release-validation';

interface ValidationPaths {
  root: string;
  data: string;
  primary: string;
  backup: string;
  migrationBackup: string;
  key: string;
  legacy: string;
  legacyWal: string;
  legacyShm: string;
  legacyJournal: string;
  deletionMarker: string;
  report: string;
}

function paths(): ValidationPaths {
  const root = app.getPath('userData');
  const data = join(root, 'data');
  const legacy = join(data, 'hearth.db');
  return {
    root,
    data,
    primary: join(data, 'hearth.secure'),
    backup: join(data, 'hearth.secure.backup'),
    migrationBackup: join(data, 'hearth.secure.migration-backup'),
    key: join(data, 'hearth.key'),
    legacy,
    legacyWal: `${legacy}-wal`,
    legacyShm: `${legacy}-shm`,
    legacyJournal: `${legacy}-journal`,
    deletionMarker: join(data, 'hearth.deleting'),
    report: join(root, 'release-validation.json'),
  };
}

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(`[release-validation] ${message}`);
}

function sha256(path: string): string {
  return createHash('sha256').update(readFileSync(path)).digest('hex');
}

function consent(): void {
  repo.saveSettings({
    displayName: 'Windows validation profile',
    onboarded: true,
    privacyConsentAt: '2026-07-14T12:00:00.000Z',
  });
}

function createLegacyFixture(path: string): void {
  const legacy = new Database(path);
  try {
    legacy.exec(SCHEMA);
    legacy.prepare('INSERT INTO settings (key, value) VALUES (?, ?)').run(
      'app',
      JSON.stringify({
        displayName: 'Migrated profile',
        onboarded: true,
        conditions: ['adhd'],
        dailySpoons: 99,
        privacyConsentAt: '2026-07-14T12:00:00.000Z',
      }),
    );
    legacy.prepare('INSERT INTO tasks (title, spoon_cost) VALUES (?, ?)').run(
      'Migrated task',
      2,
    );

    // Represent a pre-consent release after creating a structurally complete
    // current fixture: remove the new triggers, then remove the consent field.
    const triggers = legacy
      .prepare("SELECT name FROM sqlite_master WHERE type = 'trigger'")
      .all() as { name: string }[];
    for (const trigger of triggers) {
      legacy.exec(`DROP TRIGGER ${JSON.stringify(trigger.name)}`);
    }
    legacy.prepare('UPDATE settings SET value = ? WHERE key = ?').run(
      JSON.stringify({
        displayName: 'Migrated profile',
        onboarded: true,
        conditions: ['adhd'],
        dailySpoons: 99,
      }),
      'app',
    );
  } finally {
    legacy.close();
  }
}

function removeEncryptedStoreForLegacyFixture(p: ValidationPaths): void {
  closeDb();
  beginCryptographicDeletion({
    marker: p.deletionMarker,
    key: p.key,
    remnants: [
      p.primary,
      p.backup,
      p.migrationBackup,
      p.legacyWal,
      p.legacyShm,
      p.legacyJournal,
      p.legacy,
    ],
  });
}

export async function runExactCandidateValidation(): Promise<void> {
  const p = paths();
  assert(process.env.HEARTH_DATA_DIR, 'HEARTH_DATA_DIR is required.');
  assert(existsSync(join(p.root, SENTINEL)), `missing ${SENTINEL} sentinel.`);
  assert(!existsSync(p.data), 'refusing to run because the test data directory already exists.');
  mkdirSync(p.data, { recursive: true });

  const checks: string[] = [];

  // Fresh DPAPI-backed store and durable reopen.
  getDb();
  consent();
  repo.createTask({ title: 'Fresh encrypted task', spoonCost: 1.5 });
  repo.saveSettings({ theme: 'dark', dailySpoons: 99 });
  assert(repo.getSettings().dailySpoons === 24, 'daily budget was not normalized at persistence.');
  closeDb();
  assert(existsSync(p.primary) && existsSync(p.backup) && existsSync(p.key), 'fresh encrypted files are incomplete.');
  assert(!readFileSync(p.primary).subarray(0, 16).toString('binary').startsWith('SQLite format 3'), 'primary leaked plaintext SQLite.');
  getDb();
  assert(repo.listTasks(false).some((task) => task.title === 'Fresh encrypted task'), 'fresh task did not survive reopen.');
  checks.push('fresh DPAPI-backed encrypted persistence and normalized budget');

  // User-requested export builder includes records and an explicit plaintext warning.
  const exported = buildPersonalDataExport(new Date('2026-07-14T12:30:00.000Z'));
  const exportedTasks = (exported.records as Record<string, Array<{ title?: string }>>).tasks;
  assert(exportedTasks.some((task) => task.title === 'Fresh encrypted task'), 'export omitted a stored task.');
  assert(String(exported.securityNotice).includes('not encrypted'), 'export omitted its plaintext warning.');
  checks.push('plaintext export contents and warning');

  // Corrupt-primary recovery must use the authenticated rolling generation and
  // must not rotate the OS-protected key.
  closeDb();
  const keyHashBeforeRecovery = sha256(p.key);
  atomicWrite(p.primary, Buffer.from('deliberately corrupt candidate'));
  getDb();
  assert(repo.listTasks(false).some((task) => task.title === 'Fresh encrypted task'), 'rolling-backup recovery lost the known task.');
  assert(sha256(p.key) === keyHashBeforeRecovery, 'rollback recovery replaced the protected key.');
  checks.push('authenticated corrupt-primary rollback recovery');

  // Explicit erase rotates the key and creates a truly empty, unconsented store.
  const keyHashBeforeErase = sha256(p.key);
  deleteAllData();
  assert(repo.listTasks(true).length === 0, 'explicit erase left task records.');
  assert(repo.getSettings().privacyConsentAt === null, 'explicit erase retained consent.');
  assert(sha256(p.key) !== keyHashBeforeErase, 'explicit erase did not rotate the protected key.');
  checks.push('key-first erase and empty-store reinitialization');

  // Simulate a crash after the erase marker is durable but before cleanup.
  consent();
  repo.createTask({ title: 'Interrupted erase task', spoonCost: 1 });
  closeDb();
  const keyHashBeforeInterruptedErase = sha256(p.key);
  atomicWrite(p.deletionMarker, Buffer.from('hearth-delete-v1\n', 'utf8'));
  getDb();
  assert(repo.listTasks(true).length === 0, 'startup did not finish interrupted deletion.');
  assert(repo.getSettings().privacyConsentAt === null, 'interrupted deletion retained consent.');
  assert(sha256(p.key) !== keyHashBeforeInterruptedErase, 'interrupted deletion did not destroy the prior key.');
  checks.push('resumable interrupted erase');

  // Representative plaintext legacy database: migration must preserve records,
  // normalize an out-of-range legacy budget, gate new writes until consent, and
  // retire every plaintext/migration remnant after two encrypted generations.
  removeEncryptedStoreForLegacyFixture(p);
  createLegacyFixture(p.legacy);
  getDb();
  assert(repo.listTasks(false).some((task) => task.title === 'Migrated task'), 'legacy migration lost its task.');
  assert(repo.getSettings().dailySpoons === 24, 'legacy budget was not normalized.');
  assert(repo.getSettings().privacyConsentAt === null, 'legacy profile bypassed consent gating.');
  let preConsentWriteRejected = false;
  try {
    repo.createTask({ title: 'Must be rejected before consent' });
  } catch (error) {
    preConsentWriteRejected = /Explicit privacy consent/.test(String(error));
  }
  assert(preConsentWriteRejected, 'legacy profile accepted a personal write before consent.');
  assert(existsSync(p.primary) && existsSync(p.backup), 'migration did not create two encrypted generations.');
  for (const remnant of [p.legacy, p.legacyWal, p.legacyShm, p.legacyJournal, p.migrationBackup]) {
    assert(!existsSync(remnant), `migration remnant was not retired: ${remnant}`);
  }
  consent();
  repo.createTask({ title: 'Post-consent migrated task', spoonCost: 1 });
  checks.push('legacy migration, consent gate, remnant retirement, and compatibility normalization');

  // Losing the protected key while ciphertext exists must fail closed without
  // modifying either encrypted generation.
  closeDb();
  const protectedKey = readFileSync(p.key);
  const primaryHashBeforeMissingKey = sha256(p.primary);
  const backupHashBeforeMissingKey = sha256(p.backup);
  unlinkSync(p.key);
  let missingKeyRejected = false;
  try {
    getDb();
  } catch (error) {
    missingKeyRejected = /key is missing/.test(String(error));
  }
  assert(missingKeyRejected, 'missing protected key did not fail closed.');
  assert(sha256(p.primary) === primaryHashBeforeMissingKey, 'missing-key failure changed the primary.');
  assert(sha256(p.backup) === backupHashBeforeMissingKey, 'missing-key failure changed the backup.');
  atomicWrite(p.key, protectedKey);
  getDb();
  assert(repo.listTasks(false).some((task) => task.title === 'Post-consent migrated task'), 'restored key did not reopen the known store.');
  checks.push('missing-key fail-closed behavior with unchanged ciphertext');

  closeDb();
  const report = {
    schemaVersion: 1,
    status: 'passed',
    platform: process.platform,
    architecture: process.arch,
    appVersion: app.getVersion(),
    generatedAt: new Date().toISOString(),
    checks,
    files: {
      primarySha256: sha256(p.primary),
      backupSha256: sha256(p.backup),
      protectedKeyFileSha256: sha256(p.key),
    },
  };
  writeFileSync(p.report, `${JSON.stringify(report, null, 2)}\n`, { encoding: 'utf8', mode: 0o600 });

  // Ensure the report itself did not accidentally contain validation records.
  const reportText = readFileSync(p.report, 'utf8');
  assert(!/Fresh encrypted task|Migrated task|Windows validation profile/.test(reportText), 'report contains fixture records.');
  assert(readdirSync(p.root).includes('release-validation.json'), 'validation report was not written.');
}
