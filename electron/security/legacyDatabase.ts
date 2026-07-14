import Database from 'better-sqlite3';
import { existsSync, unlinkSync } from 'node:fs';

export interface LegacyPlaintextPaths {
  database: string;
  wal: string;
  shm: string;
  journal: string;
}

const SQLITE_MAGIC = Buffer.from('SQLite format 3\0', 'binary');

/**
 * sqlite3_serialize includes committed pages but preserves the source file's
 * WAL header flags. An anonymous in-memory database has no sidecar path, so
 * normalize those two header bytes to rollback-journal format before opening
 * the self-contained snapshot. No page content is changed.
 */
export function normalizeSerializedDatabase(snapshot: Buffer): Buffer {
  if (snapshot.length < 20 || !snapshot.subarray(0, SQLITE_MAGIC.length).equals(SQLITE_MAGIC)) {
    throw new Error('The SQLite snapshot has an invalid file header.');
  }
  const normalized = Buffer.from(snapshot);
  normalized[18] = 1;
  normalized[19] = 1;
  return normalized;
}

export function validateSerializedDatabase(snapshot: Buffer): void {
  let candidate: Database.Database | null = null;
  try {
    candidate = new Database(normalizeSerializedDatabase(snapshot));
    const result = candidate.pragma('integrity_check', { simple: true });
    if (result !== 'ok') throw new Error(`SQLite integrity check returned: ${String(result)}`);
  } finally {
    candidate?.close();
  }
}

/** Read a consistent committed snapshot without writing to the legacy files. */
export function readLegacySnapshot(path: string): Buffer {
  let legacy: Database.Database | null = null;
  try {
    legacy = new Database(path, { readonly: true, fileMustExist: true });
    const result = legacy.pragma('integrity_check', { simple: true });
    if (result !== 'ok') throw new Error(`Legacy SQLite integrity check returned: ${String(result)}`);
    const snapshot = normalizeSerializedDatabase(legacy.serialize());
    validateSerializedDatabase(snapshot);
    return snapshot;
  } finally {
    legacy?.close();
  }
}

export function retireLegacyMigration(
  legacy: LegacyPlaintextPaths,
  encryptedMigrationBackup: string,
): void {
  for (const path of [legacy.wal, legacy.shm, legacy.journal, legacy.database]) {
    if (existsSync(path)) unlinkSync(path);
  }
  if (existsSync(encryptedMigrationBackup)) unlinkSync(encryptedMigrationBackup);
}
