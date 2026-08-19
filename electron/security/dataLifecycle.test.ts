import Database from 'better-sqlite3';
import { randomBytes } from 'node:crypto';
import {
  existsSync,
  mkdirSync,
  mkdtempSync,
  rmSync,
  writeFileSync,
} from 'node:fs';
import { join } from 'node:path';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { beginCryptographicDeletion, completeCryptographicDeletion } from './cryptographicDeletion';
import { readLegacySnapshot, retireLegacyMigration, validateSerializedDatabase } from './legacyDatabase';

let dir: string;

beforeEach(() => {
  const tmpRoot = join(process.cwd(), 'tmp');
  mkdirSync(tmpRoot, { recursive: true });
  dir = mkdtempSync(join(tmpRoot, 'data-lifecycle-test-'));
});

afterEach(() => rmSync(dir, { recursive: true, force: true }));

describe('legacy migration lifecycle', () => {
  it('captures committed WAL data and retires plaintext plus migration backup', () => {
    const database = join(dir, 'ample.db');
    const writer = new Database(database);
    writer.pragma('journal_mode = WAL');
    writer.exec('CREATE TABLE private_notes (id INTEGER PRIMARY KEY, note TEXT NOT NULL)');
    writer.prepare('INSERT INTO private_notes (note) VALUES (?)').run('keep this safely');

    const snapshot = readLegacySnapshot(database);
    validateSerializedDatabase(snapshot);
    const migrated = new Database(snapshot);
    expect(
      (migrated.prepare('SELECT note FROM private_notes').get() as { note: string }).note,
    ).toBe('keep this safely');
    migrated.close();
    writer.close();

    const migrationBackup = join(dir, 'ample.secure.migration-backup');
    writeFileSync(migrationBackup, randomBytes(64));
    retireLegacyMigration(
      {
        database,
        wal: `${database}-wal`,
        shm: `${database}-shm`,
        journal: `${database}-journal`,
      },
      migrationBackup,
    );

    expect(existsSync(database)).toBe(false);
    expect(existsSync(migrationBackup)).toBe(false);
  });
});
describe('cryptographic erase lifecycle', () => {
  it('destroys the protected key and every encrypted remnant', () => {
    const marker = join(dir, 'ample.deleting');
    const key = join(dir, 'ample.key');
    const remnants = [join(dir, 'ample.secure'), join(dir, 'ample.secure.backup')];
    for (const path of [key, ...remnants]) writeFileSync(path, randomBytes(32));

    beginCryptographicDeletion({ marker, key, remnants });
    for (const path of [marker, key, ...remnants]) expect(existsSync(path)).toBe(false);
  });

  it('resumes an interrupted explicit deletion before storage can reopen', () => {
    const marker = join(dir, 'ample.deleting');
    const key = join(dir, 'ample.key');
    const remnants = [join(dir, 'ample.secure.migration-backup')];
    for (const path of [marker, key, ...remnants]) writeFileSync(path, randomBytes(32));

    completeCryptographicDeletion({ marker, key, remnants });
    for (const path of [marker, key, ...remnants]) expect(existsSync(path)).toBe(false);
  });
});
