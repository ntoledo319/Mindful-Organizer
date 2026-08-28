import { app, dialog, type BrowserWindow } from 'electron';
import { chmod, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { deleteAllData as deleteEncryptedDatabase, getDb } from './db';
import type { PersonalDataExportResult } from '../src/shared/types';

const EXPORT_TABLES = [
  'tasks',
  'mood_entries',
  'sleep_logs',
  'journal_entries',
  'practice_sessions',
  'erp_sessions',
  'diary_cards',
  'medications',
  'medication_logs',
  'gamification',
  'clinical_profiles',
] as const;

interface SettingRow {
  key: string;
  value: string;
}

function parseSetting(row: SettingRow): unknown {
  try {
    return JSON.parse(row.value) as unknown;
  } catch {
    return row.value;
  }
}

export function buildPersonalDataExport(exportedAt = new Date()): Record<string, unknown> {
  const db = getDb();
  const records: Record<string, unknown[]> = {};
  for (const table of EXPORT_TABLES) {
    // Table names are a closed compile-time allowlist, never renderer input.
    records[table] = db.prepare(`SELECT * FROM ${table} ORDER BY id`).all() as unknown[];
  }

  const settings = Object.fromEntries(
    (db.prepare('SELECT key, value FROM settings ORDER BY key').all() as SettingRow[]).map((row) => [
      row.key,
      parseSetting(row),
    ]),
  );

  return {
    format: 'ample-personal-data',
    version: 1,
    exportedAt: exportedAt.toISOString(),
    securityNotice:
      'This user-requested JSON export is not encrypted. Store or share it only where you intend.',
    settings,
    records,
  };
}

export async function exportAllData(parent: BrowserWindow | null): Promise<PersonalDataExportResult> {
  const now = new Date();
  const options = {
    title: 'Export all Paulatim data',
    defaultPath: join(
      app.getPath('documents'),
      `Paulatim-personal-data-${now.toISOString().slice(0, 10)}.json`,
    ),
    filters: [{ name: 'JSON document', extensions: ['json'] }],
  };
  const selection = parent
    ? await dialog.showSaveDialog(parent, options)
    : await dialog.showSaveDialog(options);

  if (selection.canceled || !selection.filePath) return { status: 'cancelled' };

  const json = `${JSON.stringify(buildPersonalDataExport(now), null, 2)}\n`;
  await writeFile(selection.filePath, json, { encoding: 'utf8', mode: 0o600 });
  try {
    await chmod(selection.filePath, 0o600);
  } catch {
    // Windows does not implement POSIX mode bits. The explicit warning above
    // remains in the export so the user understands it is plaintext.
  }
  return { status: 'saved', filePath: selection.filePath };
}

export function deleteAllData(): void {
  deleteEncryptedDatabase();
}
