import { app, BrowserWindow, dialog, type BrowserWindow as BrowserWindowType } from 'electron';
import { writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import * as repo from './repo';
import * as wellness from './wellness';
import {
  buildSessionSummaryHtml,
  hasSummaryData,
  normalizeSummaryDays,
} from '../src/shared/sessionSummary';
import type { SessionSummaryExportResult } from '../src/shared/types';

export async function exportSessionSummary(
  requestedDays: number,
  parent: BrowserWindowType | null,
): Promise<SessionSummaryExportResult> {
  const days = normalizeSummaryDays(requestedDays);
  const trends = wellness.trends(days);
  if (!hasSummaryData(trends)) return { status: 'empty' };

  const generatedAt = new Date();
  const html = buildSessionSummaryHtml({
    days,
    displayName: repo.getSettings().displayName,
    generatedAt,
    trends,
  });
  const defaultPath = join(
    app.getPath('documents'),
    `Hearth-session-summary-${generatedAt.toISOString().slice(0, 10)}.pdf`,
  );
  const options = {
    title: 'Save Hearth session summary',
    defaultPath,
    filters: [{ name: 'PDF document', extensions: ['pdf'] }],
  };
  const selection = parent
    ? await dialog.showSaveDialog(parent, options)
    : await dialog.showSaveDialog(options);

  if (selection.canceled || !selection.filePath) return { status: 'cancelled' };

  const reportWindow = new BrowserWindow({
    show: false,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });

  try {
    await reportWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(html)}`);
    const pdf = await reportWindow.webContents.printToPDF({
      pageSize: 'A4',
      printBackground: true,
      preferCSSPageSize: true,
    });
    await writeFile(selection.filePath, pdf);
    return { status: 'saved', filePath: selection.filePath };
  } finally {
    if (!reportWindow.isDestroyed()) reportWindow.destroy();
  }
}
