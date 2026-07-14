import { describe, expect, it } from 'vitest';
import {
  CAPABILITIES,
  CAPABILITY_VAULT,
  CORE_CAPABILITIES,
  UTILITY_CAPABILITIES,
  capabilityFor,
  isRoute,
} from './capabilities';

describe('capability registry', () => {
  it('keeps the default navigation focused on the daily energy-planning loop', () => {
    expect(CORE_CAPABILITIES.map(({ route }) => route)).toEqual([
      'dashboard',
      'tasks',
      'reflect',
      'practices',
      'trends',
    ]);
    expect(UTILITY_CAPABILITIES.map(({ route }) => route)).toEqual(['crisis', 'settings']);
  });

  it('preserves specialist capabilities in the documented vault', () => {
    expect(CAPABILITY_VAULT.map(({ route }) => route)).toEqual(['diary', 'erp', 'meds']);
    for (const capability of CAPABILITY_VAULT) {
      expect(capability.vaultReason.length).toBeGreaterThan(40);
    }
  });

  it('has unique routes and safe route lookup', () => {
    const routes = CAPABILITIES.map(({ route }) => route);
    expect(new Set(routes).size).toBe(routes.length);
    expect(isRoute('dashboard')).toBe(true);
    expect(isRoute('not-a-route')).toBe(false);
    expect(capabilityFor('reflect')?.navLabel).toBe('Check in');
  });
});
