import { existsSync, unlinkSync } from 'node:fs';
import { atomicWrite } from './secureFile';

export interface CryptographicDeletionPaths {
  marker: string;
  key: string;
  remnants: string[];
}

function removeBestEffort(paths: string[]): string[] {
  const failures: string[] = [];
  for (const path of paths) {
    if (!existsSync(path)) continue;
    try {
      unlinkSync(path);
    } catch (error) {
      failures.push(`${path}: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
  return failures;
}

/**
 * Finish an explicit user-requested deletion. The marker distinguishes this
 * state from an accidentally missing key, which must always fail closed.
 */
export function completeCryptographicDeletion(paths: CryptographicDeletionPaths): void {
  if (!existsSync(paths.marker)) return;

  // Key destruction is first: even if later unlink operations fail, snapshots
  // can no longer be decrypted. Every remnant is still attempted.
  const failures = removeBestEffort([paths.key, ...paths.remnants]);
  if (failures.length > 0) {
    throw new Error(`Paulatim erased the encryption key but could not remove every remnant. ${failures.join(' | ')}`);
  }
  unlinkSync(paths.marker);
}

export function beginCryptographicDeletion(paths: CryptographicDeletionPaths): void {
  atomicWrite(paths.marker, Buffer.from('ample-delete-v1\n', 'utf8'));
  completeCryptographicDeletion(paths);
}
