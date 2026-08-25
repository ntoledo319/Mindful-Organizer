import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';

const launcherPath = fileURLToPath(
  new URL('../scripts/capture-store-screenshots.mjs', import.meta.url),
);
const launcherSource = readFileSync(launcherPath, 'utf8');

describe('Store screenshot launcher', () => {
  it('uses the Ample harness contract expected by the Electron main process', () => {
    for (const variable of [
      'AMPLE_SCREENSHOT',
      'AMPLE_DATA_DIR',
      'AMPLE_SHOT_DIR',
      'AMPLE_SHOT_BUILD_REF',
    ]) {
      expect(launcherSource).toContain(variable);
    }

    expect(launcherSource).not.toMatch(/HEARTH_(?:SCREENSHOT|DATA_DIR|SHOT_DIR|SHOT_BUILD_REF)/);
  });
});
