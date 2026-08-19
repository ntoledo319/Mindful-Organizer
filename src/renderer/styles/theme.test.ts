import { describe, expect, it } from 'vitest';
import { THEME_COLORS } from '../../shared/theme';

function relativeLuminance(hex: string): number {
  const channels = hex
    .replace('#', '')
    .match(/../g)!
    .map((channel) => Number.parseInt(channel, 16) / 255)
    .map((channel) =>
      channel <= 0.04045 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4,
    );
  return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2];
}

function contrast(first: string, second: string): number {
  const firstLuminance = relativeLuminance(first);
  const secondLuminance = relativeLuminance(second);
  return (
    (Math.max(firstLuminance, secondLuminance) + 0.05) /
    (Math.min(firstLuminance, secondLuminance) + 0.05)
  );
}

describe('Ample theme', () => {
  it('keeps normal-size brand and warning text at WCAG AA contrast', () => {
    expect(contrast(THEME_COLORS.brand, '#FFFFFF')).toBeGreaterThanOrEqual(4.5);
    expect(contrast(THEME_COLORS.brand, THEME_COLORS.base.bg)).toBeGreaterThanOrEqual(4.5);
    expect(contrast(THEME_COLORS.semantic.warning, THEME_COLORS.base.bg)).toBeGreaterThanOrEqual(4.5);
    expect(contrast(THEME_COLORS.semantic.error, THEME_COLORS.base.bg)).toBeGreaterThanOrEqual(4.5);
    expect(contrast(THEME_COLORS.semantic.success, THEME_COLORS.base.bg)).toBeGreaterThanOrEqual(4.5);
    expect(contrast(THEME_COLORS.night.brand, THEME_COLORS.night.surface)).toBeGreaterThanOrEqual(4.5);
    expect(contrast(THEME_COLORS.night.error, THEME_COLORS.night.surface)).toBeGreaterThanOrEqual(4.5);
    expect(contrast(THEME_COLORS.night.warning, THEME_COLORS.night.surface)).toBeGreaterThanOrEqual(4.5);
    expect(contrast(THEME_COLORS.night.success, THEME_COLORS.night.surface)).toBeGreaterThanOrEqual(4.5);
  });

  it('keeps muted copy at AAA contrast on its primary canvas', () => {
    expect(contrast(THEME_COLORS.text.muted, THEME_COLORS.base.bg)).toBeGreaterThanOrEqual(7);
    expect(contrast(THEME_COLORS.night.muted, THEME_COLORS.night.surface)).toBeGreaterThanOrEqual(7);
  });
});
