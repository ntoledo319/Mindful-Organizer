import Database from 'better-sqlite3';
import { app, safeStorage } from 'electron';
import { randomBytes } from 'node:crypto';
import {
  chmodSync,
  existsSync,
  mkdirSync,
  readFileSync,
  unlinkSync,
} from 'node:fs';
import { join } from 'node:path';
import { SCHEMA } from './schema';
import { MASTER_KEY_BYTES } from './security/envelope';
import { beginCryptographicDeletion, completeCryptographicDeletion } from './security/cryptographicDeletion';
import { runDurableTransaction, type TransactionState } from './security/durableTransaction';
import {
  readLegacySnapshot,
  retireLegacyMigration,
  normalizeSerializedDatabase,
  validateSerializedDatabase,
} from './security/legacyDatabase';
import {
  atomicWrite,
  persistMigrationBackup,
  persistSnapshot,
  recoverSnapshot,
  restorePrimary,
  verifySnapshot,
  type SnapshotPaths,
} from './security/secureFile';

/**
 * Paulatim keeps SQLite in memory and persists only authenticated ciphertext.
 *
 * - Each snapshot uses AES-256-GCM with a fresh IV.
 * - The random master key is protected by Electron safeStorage (DPAPI on
 *   Windows, Keychain on macOS, and a real Secret Service backend on Linux).
 * - Every mutation is serialized and atomically persisted before the caller
 *   receives success.
 * - One rolling encrypted backup and a temporary immutable encrypted migration
 *   backup prevent corrupt writes or migrations from becoming data-loss traps;
 *   the migration backup is retired after the primary and rollback verify.
 */

interface DatabasePaths extends SnapshotPaths {
  key: string;
  legacy: string;
  legacyWal: string;
  legacyShm: string;
  legacyJournal: string;
  deletionMarker: string;
}

let nativeDb: Database.Database | null = null;
let exposedDb: Database.Database | null = null;
let masterKey: Buffer | null = null;
let activePaths: DatabasePaths | null = null;
const transactionState: TransactionState = { depth: 0 };

function pathsFor(dir: string): DatabasePaths {
  const legacy = join(dir, 'ample.db');
  return {
    primary: join(dir, 'ample.secure'),
    backup: join(dir, 'ample.secure.backup'),
    migrationBackup: join(dir, 'ample.secure.migration-backup'),
    key: join(dir, 'ample.key'),
    legacy,
    legacyWal: `${legacy}-wal`,
    legacyShm: `${legacy}-shm`,
    legacyJournal: `${legacy}-journal`,
    deletionMarker: join(dir, 'ample.deleting'),
  };
}

function hasEncryptedSnapshot(paths: DatabasePaths): boolean {
  return [paths.primary, paths.backup, paths.migrationBackup].some(existsSync);
}

function assertSecureOsKeyStore(): void {
  if (!safeStorage.isEncryptionAvailable()) {
    throw new Error(
      'Secure local storage is unavailable. Paulatim will not open or create personal records without OS-backed encryption.',
    );
  }

  if (process.platform === 'linux') {
    const backend = safeStorage.getSelectedStorageBackend();
    const secureBackends = new Set(['gnome_libsecret', 'kwallet', 'kwallet5', 'kwallet6']);
    if (!secureBackends.has(backend)) {
      throw new Error(
        `Linux secure storage backend "${backend}" is not suitable for personal records. Configure Secret Service or KWallet before using Paulatim.`,
      );
    }
  }
}

function decodeProtectedKey(path: string): Buffer {
  try {
    const decoded = Buffer.from(safeStorage.decryptString(readFileSync(path)), 'base64');
    if (decoded.length !== MASTER_KEY_BYTES) throw new Error('unexpected key length');
    return decoded;
  } catch (error) {
    throw new Error(
      'Paulatim could not unlock its encrypted database key. No data was changed; sign in to the original OS account or restore its credential store.',
      { cause: error },
    );
  }
}

function loadOrCreateMasterKey(paths: DatabasePaths): Buffer {
  assertSecureOsKeyStore();
  if (existsSync(paths.key)) return decodeProtectedKey(paths.key);

  if (hasEncryptedSnapshot(paths)) {
    throw new Error(
      'The encrypted Paulatim database exists but its OS-protected key is missing. Paulatim will not replace it or erase existing data.',
    );
  }

  const key = randomBytes(MASTER_KEY_BYTES);
  try {
    const protectedKey = safeStorage.encryptString(key.toString('base64'));
    atomicWrite(paths.key, protectedKey);
    const verified = decodeProtectedKey(paths.key);
    const matches = verified.equals(key);
    verified.fill(0);
    if (!matches) throw new Error('OS-protected key verification failed.');
    return key;
  } catch (error) {
    key.fill(0);
    if (existsSync(paths.key)) unlinkSync(paths.key);
    throw error;
  }
}

function openMemoryDatabase(snapshot?: Buffer): Database.Database {
  const opened = snapshot
    ? new Database(normalizeSerializedDatabase(snapshot))
    : new Database(':memory:');
  opened.pragma('journal_mode = MEMORY');
  opened.pragma('synchronous = FULL');
  opened.pragma('foreign_keys = ON');
  return opened;
}

function invalidateInMemoryDatabase(error: unknown): never {
  const failed = nativeDb;
  nativeDb = null;
  exposedDb = null;
  activePaths = null;
  transactionState.depth = 0;
  try {
    failed?.close();
  } finally {
    masterKey?.fill(0);
    masterKey = null;
  }
  throw new Error(
    'Paulatim could not durably save the encrypted database. The previous authenticated snapshot is intact; reopen the app before continuing.',
    { cause: error },
  );
}

function persistCurrentDatabase(): void {
  if (!nativeDb || !masterKey || !activePaths) {
    throw new Error('The secure Paulatim database is not open.');
  }
  try {
    persistSnapshot(
      activePaths,
      masterKey,
      nativeDb.serialize(),
      validateSerializedDatabase,
    );
  } catch (error) {
    invalidateInMemoryDatabase(error);
  }
}

function mutationCompleted(): void {
  if (transactionState.depth === 0) persistCurrentDatabase();
}

function wrapStatement(statement: Database.Statement): Database.Statement {
  const proxy: Database.Statement = new Proxy(statement, {
    get(target, property) {
      if (property === 'database') return exposedDb;
      if (property === 'run') {
        return (...args: unknown[]) => {
          const result = Reflect.apply(target.run, target, args) as Database.RunResult;
          mutationCompleted();
          return result;
        };
      }
      if (['bind', 'pluck', 'expand', 'raw', 'safeIntegers'].includes(String(property))) {
        return (...args: unknown[]) => {
          const method = Reflect.get(target, property, target) as (...params: unknown[]) => unknown;
          Reflect.apply(method, target, args);
          return proxy;
        };
      }
      const value = Reflect.get(target, property, target) as unknown;
      return typeof value === 'function' ? value.bind(target) : value;
    },
  });
  return proxy;
}

type TransactionCallback = (...args: unknown[]) => unknown;
type TransactionRunner = ((...args: unknown[]) => unknown) & {
  default: (...args: unknown[]) => unknown;
  deferred: (...args: unknown[]) => unknown;
  immediate: (...args: unknown[]) => unknown;
  exclusive: (...args: unknown[]) => unknown;
};

function wrapTransaction(callback: TransactionCallback): TransactionRunner {
  if (!nativeDb) throw new Error('The secure Paulatim database is not open.');
  const transaction = nativeDb.transaction(callback) as unknown as TransactionRunner;
  const run = (runner: (...args: unknown[]) => unknown, args: unknown[]) =>
    runDurableTransaction(transactionState, runner, args, mutationCompleted);
  const wrapped = ((...args: unknown[]) => run(transaction, args)) as TransactionRunner;
  wrapped.default = (...args) => run(transaction.default, args);
  wrapped.deferred = (...args) => run(transaction.deferred, args);
  wrapped.immediate = (...args) => run(transaction.immediate, args);
  wrapped.exclusive = (...args) => run(transaction.exclusive, args);
  return wrapped;
}

function createDatabaseProxy(database: Database.Database): Database.Database {
  return new Proxy(database, {
    get(target, property) {
      if (property === 'prepare') {
        return ((source: string) => wrapStatement(target.prepare(source))) as Database.Database['prepare'];
      }
      if (property === 'transaction') {
        return ((callback: TransactionCallback) => wrapTransaction(callback)) as Database.Database['transaction'];
      }
      if (property === 'exec') {
        return ((source: string) => {
          target.exec(source);
          mutationCompleted();
          return exposedDb;
        }) as Database.Database['exec'];
      }
      const value = Reflect.get(target, property, target) as unknown;
      return typeof value === 'function' ? value.bind(target) : value;
    },
  });
}

function initializeDatabase(): void {
  const dir = join(app.getPath('userData'), 'data');
  mkdirSync(dir, { recursive: true, mode: 0o700 });
  try {
    chmodSync(dir, 0o700);
  } catch {
    // Authenticated encryption and the OS-protected key remain mandatory.
  }

  const paths = pathsFor(dir);
  completeCryptographicDeletion({
    marker: paths.deletionMarker,
    key: paths.key,
    remnants: [
      paths.primary,
      paths.backup,
      paths.migrationBackup,
      paths.legacyWal,
      paths.legacyShm,
      paths.legacyJournal,
      paths.legacy,
    ],
  });
  const key = loadOrCreateMasterKey(paths);
  let opened: Database.Database | null = null;
  const migrationCleanupPending = existsSync(paths.migrationBackup) || existsSync(paths.legacy);

  try {
    if (hasEncryptedSnapshot(paths)) {
      const recovered = recoverSnapshot(paths, key, validateSerializedDatabase);
      opened = openMemoryDatabase(recovered.plaintext);
      restorePrimary(paths, recovered.source);
    } else if (existsSync(paths.legacy)) {
      const legacySnapshot = readLegacySnapshot(paths.legacy);
      persistMigrationBackup(
        paths.migrationBackup,
        key,
        legacySnapshot,
        validateSerializedDatabase,
      );
      persistSnapshot(paths, key, legacySnapshot, validateSerializedDatabase);
      // Re-open and validate the just-written encrypted primary before removing
      // any legacy file. The migration backup remains immutable for rollback.
      const recovered = recoverSnapshot(paths, key, validateSerializedDatabase);
      opened = openMemoryDatabase(recovered.plaintext);
    } else {
      opened = openMemoryDatabase();
    }

    opened.exec(SCHEMA);
    validateSerializedDatabase(opened.serialize());

    nativeDb = opened;
    masterKey = key;
    activePaths = paths;
    exposedDb = createDatabaseProxy(opened);
    persistCurrentDatabase();

    if (migrationCleanupPending) {
      // The common persistence above creates/validates the rolling backup from
      // the authenticated primary. Only now is it safe to remove plaintext and
      // retire the migration snapshot so later deletions cannot resurrect old
      // records. A crash leaves the marker files for the next startup to finish.
      verifySnapshot(paths.primary, key, validateSerializedDatabase);
      verifySnapshot(paths.backup, key, validateSerializedDatabase);
      retireLegacyMigration(
        {
          database: paths.legacy,
          wal: paths.legacyWal,
          shm: paths.legacyShm,
          journal: paths.legacyJournal,
        },
        paths.migrationBackup,
      );
    }
  } catch (error) {
    if (opened?.open) opened.close();
    key.fill(0);
    nativeDb = null;
    exposedDb = null;
    masterKey = null;
    activePaths = null;
    throw error;
  }
}

export function getDb(): Database.Database {
  if (!exposedDb) initializeDatabase();
  if (!exposedDb) throw new Error('The secure Paulatim database did not initialize.');
  return exposedDb;
}

export function closeDb(): void {
  const closing = nativeDb;
  nativeDb = null;
  exposedDb = null;
  activePaths = null;
  transactionState.depth = 0;
  try {
    closing?.close();
  } finally {
    masterKey?.fill(0);
    masterKey = null;
  }
}

/**
 * Cryptographically withdraw consent by removing every encrypted snapshot and
 * its OS-protected master key, then create a fresh empty encrypted store.
 */
export function deleteAllData(): void {
  const paths = activePaths ?? pathsFor(join(app.getPath('userData'), 'data'));
  closeDb();

  beginCryptographicDeletion({
    marker: paths.deletionMarker,
    key: paths.key,
    remnants: [
      paths.primary,
      paths.backup,
      paths.migrationBackup,
      paths.legacyWal,
      paths.legacyShm,
      paths.legacyJournal,
      paths.legacy,
    ],
  });

  // Reinitialize before acknowledging deletion. The new store has a new key
  // and no consent/settings row, so the renderer returns to onboarding.
  getDb();
}
