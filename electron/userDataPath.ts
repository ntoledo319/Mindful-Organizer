import { join, resolve } from 'node:path';

// The product was called Ample when the encrypted profile namespace was
// established. Keep that implementation detail stable across visible renames
// so an upgrade never looks like it lost a user's local records.
export const STABLE_USER_DATA_DIRECTORY = 'Ample';

export function resolveUserDataPath(appDataDirectory: string, override?: string): string {
  return override
    ? resolve(override)
    : join(appDataDirectory, STABLE_USER_DATA_DIRECTORY);
}
