import { randomBytes } from 'node:crypto';
import {
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from 'node:fs';
import { join } from 'node:path';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { MASTER_KEY_BYTES } from './envelope';
import { persistMigrationBackup, persistSnapshot, recoverSnapshot, type SnapshotPaths } from './secureFile';

let dir: string;
let paths: SnapshotPaths;
const validate = (contents: Buffer) => {
  if (!contents.toString('utf8').startsWith('valid:')) throw new Error('invalid snapshot');
};

beforeEach(() => {
  const tmpRoot = join(process.cwd(), 'tmp');
  mkdirSync(tmpRoot, { recursive: true });
  dir = mkdtempSync(join(tmpRoot, 'secure-file-test-'));
  paths = {
    primary: join(dir, 'hearth.secure'),
    backup: join(dir, 'hearth.secure.backup'),
    migrationBackup: join(dir, 'hearth.secure.migration-backup'),
  };
});

afterEach(() => rmSync(dir, { recursive: true, force: true }));

describe('encrypted snapshot persistence', () => {
  it('falls back to the last authenticated snapshot when primary is corrupt', () => {
    const key = randomBytes(MASTER_KEY_BYTES);
    persistSnapshot(paths, key, Buffer.from('valid:first'), validate);
    persistSnapshot(paths, key, Buffer.from('valid:second'), validate);
    expect(readFileSync(paths.primary).includes(Buffer.from('valid:second'))).toBe(false);

    writeFileSync(paths.primary, Buffer.from('corrupt'));
    const recovered = recoverSnapshot(paths, key, validate);
    expect(recovered.source).toBe('backup');
    expect(recovered.plaintext.toString('utf8')).toBe('valid:first');
  });

  it('keeps a verified migration snapshot available until cleanup', () => {
    const key = randomBytes(MASTER_KEY_BYTES);
    persistMigrationBackup(paths.migrationBackup, key, Buffer.from('valid:legacy'), validate);
    writeFileSync(paths.primary, Buffer.from('corrupt'));
    writeFileSync(paths.backup, Buffer.from('also corrupt'));

    const recovered = recoverSnapshot(paths, key, validate);
    expect(recovered.source).toBe('migrationBackup');
    expect(recovered.plaintext.toString('utf8')).toBe('valid:legacy');
  });

  it('does not manufacture a replacement when every snapshot is invalid', () => {
    const key = randomBytes(MASTER_KEY_BYTES);
    writeFileSync(paths.primary, Buffer.from('corrupt'));
    expect(() => recoverSnapshot(paths, key, validate)).toThrow(/No authenticated/);
    expect(existsSync(paths.primary)).toBe(true);
  });
});
