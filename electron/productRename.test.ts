import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';
import { resolveUserDataPath, STABLE_USER_DATA_DIRECTORY } from './userDataPath';

const require = createRequire(import.meta.url);

describe('Paulatim product rename boundaries', () => {
  it('uses Paulatim for visible package branding without changing Store internals', () => {
    const config = require('../electron-builder.cjs');
    const packageJson = require('../package.json');

    expect(packageJson.name).toBe('ample');
    expect(packageJson.productName).toBe('Paulatim');
    expect(packageJson.version).toBe('1.1.1');
    expect(config.productName).toBe('Paulatim');
    expect(config.appId).toBe('io.ampleproject.ample');
    expect(config.appx.applicationId).toBe('Ample');
    expect(config.appx.displayName).toBe('Paulatim');
    expect(config.appx.identityName).toBe('ToledoTechnologies.Hearth');
    expect(config.appx.publisher).toBe('CN=FBC80173-0C85-481E-BC5E-A3BE88BC2020');
  });

  it('keeps the established encrypted-profile directory unless a harness overrides it', () => {
    expect(STABLE_USER_DATA_DIRECTORY).toBe('Ample');
    expect(resolveUserDataPath('/profiles')).toBe(join('/profiles', 'Ample'));
    expect(resolveUserDataPath('/profiles', './tmp/profile')).toBe(
      join(process.cwd(), 'tmp/profile'),
    );
  });

  it('preserves encrypted-storage and export format compatibility markers', () => {
    const dbSource = readFileSync(join(process.cwd(), 'electron/db.ts'), 'utf8');
    const envelopeSource = readFileSync(join(process.cwd(), 'electron/security/envelope.ts'), 'utf8');
    const deletionSource = readFileSync(join(process.cwd(), 'electron/security/cryptographicDeletion.ts'), 'utf8');
    const exportSource = readFileSync(join(process.cwd(), 'electron/dataLifecycle.ts'), 'utf8');

    for (const stableName of [
      'ample.db',
      'ample.secure',
      'ample.secure.backup',
      'ample.secure.migration-backup',
      'ample.key',
      'ample.deleting',
    ]) {
      expect(dbSource).toContain(stableName);
    }
    expect(envelopeSource).toContain("Buffer.from('HEARTHDB', 'ascii')");
    expect(deletionSource).toContain("Buffer.from('ample-delete-v1\\n', 'utf8')");
    expect(exportSource).toContain("format: 'ample-personal-data'");

    expect(dbSource).not.toContain('paulatim.secure');
    expect(deletionSource).not.toContain('paulatim-delete-v1');
    expect(exportSource).not.toContain("format: 'paulatim-personal-data'");
  });
});
