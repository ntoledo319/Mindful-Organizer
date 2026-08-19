import {
  chmodSync,
  closeSync,
  existsSync,
  fsyncSync,
  openSync,
  readFileSync,
  renameSync,
  unlinkSync,
  writeFileSync,
} from 'node:fs';
import { basename, dirname, join } from 'node:path';
import { randomBytes } from 'node:crypto';
import { decryptDatabase, encryptDatabase } from './envelope';

export interface SnapshotPaths {
  primary: string;
  backup: string;
  migrationBackup: string;
}

export type SnapshotSource = keyof SnapshotPaths;

export interface RecoveredSnapshot {
  plaintext: Buffer;
  source: SnapshotSource;
}

export type SnapshotValidator = (plaintext: Buffer) => void;

/** Write a file on the same volume, fsync it, then atomically replace target. */
export function atomicWrite(target: string, contents: Buffer): void {
  const temp = join(
    dirname(target),
    `.${basename(target)}.${process.pid}.${randomBytes(6).toString('hex')}.tmp`,
  );
  let fd: number | null = null;
  try {
    fd = openSync(temp, 'wx', 0o600);
    writeFileSync(fd, contents);
    fsyncSync(fd);
    closeSync(fd);
    fd = null;
    renameSync(temp, target);
    // Windows ignores POSIX mode bits; on Unix this prevents accidental
    // widening if an existing file had permissive permissions.
    try {
      chmodSync(target, 0o600);
    } catch {
      // The authenticated encryption envelope remains the security boundary.
    }
  } catch (error) {
    if (fd !== null) closeSync(fd);
    if (existsSync(temp)) unlinkSync(temp);
    throw error;
  }
}

function readVerified(path: string, key: Buffer, validate: SnapshotValidator): Buffer {
  const plaintext = decryptDatabase(readFileSync(path), key);
  validate(plaintext);
  return plaintext;
}

export function verifySnapshot(path: string, key: Buffer, validate: SnapshotValidator): void {
  readVerified(path, key, validate);
}

/**
 * Load the newest usable snapshot without mutating or deleting any candidate.
 * The caller may restore a fallback to primary only after it has opened and
 * validated successfully.
 */
export function recoverSnapshot(
  paths: SnapshotPaths,
  key: Buffer,
  validate: SnapshotValidator,
): RecoveredSnapshot {
  const failures: string[] = [];
  for (const source of ['primary', 'backup', 'migrationBackup'] as const) {
    const path = paths[source];
    if (!existsSync(path)) continue;
    try {
      return { plaintext: readVerified(path, key, validate), source };
    } catch (error) {
      failures.push(`${source}: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  throw new Error(
    `No authenticated Ample database snapshot could be opened. ${failures.join(' | ')}`,
  );
}

/** Persist a new snapshot while keeping one authenticated rollback generation. */
export function persistSnapshot(
  paths: SnapshotPaths,
  key: Buffer,
  plaintext: Buffer,
  validate: SnapshotValidator,
): void {
  validate(plaintext);
  const nextEnvelope = encryptDatabase(plaintext, key);
  const roundTrip = decryptDatabase(nextEnvelope, key);
  if (!roundTrip.equals(plaintext)) {
    throw new Error('Encrypted Ample database verification failed before write.');
  }

  if (existsSync(paths.primary)) {
    try {
      // Never replace a known-good backup with a corrupt primary.
      readVerified(paths.primary, key, validate);
      atomicWrite(paths.backup, readFileSync(paths.primary));
    } catch {
      // A prior backup or migration backup remains available for recovery.
    }
  }

  atomicWrite(paths.primary, nextEnvelope);
}

/** Save the pre-migration state exactly once, already encrypted and verified. */
export function persistMigrationBackup(
  path: string,
  key: Buffer,
  plaintext: Buffer,
  validate: SnapshotValidator,
): void {
  validate(plaintext);
  if (existsSync(path)) {
    readVerified(path, key, validate);
    return;
  }
  const envelope = encryptDatabase(plaintext, key);
  const roundTrip = decryptDatabase(envelope, key);
  validate(roundTrip);
  if (!roundTrip.equals(plaintext)) {
    throw new Error('Encrypted migration backup verification failed.');
  }
  atomicWrite(path, envelope);
}

/** Restore an already-authenticated fallback envelope as the primary file. */
export function restorePrimary(paths: SnapshotPaths, source: SnapshotSource): void {
  if (source === 'primary') return;
  atomicWrite(paths.primary, readFileSync(paths[source]));
}
