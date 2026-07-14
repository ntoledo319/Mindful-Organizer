/**
 * Hearth's navigation contract.
 *
 * `core` is the small daily loop shown to every user. `utility` entries stay
 * close at hand without competing with that loop. `vaulted` capabilities are
 * preserved, typed, and renderable, but deliberately absent from the default
 * navigation until they have an explicit opt-in and their specialist safety
 * review is complete.
 */
export const CAPABILITIES = [
  {
    route: 'dashboard',
    navLabel: 'Today',
    title: 'Today',
    status: 'core',
    purpose: 'Turn recent check-ins into one energy-aware next step.',
  },
  {
    route: 'tasks',
    navLabel: 'Tasks',
    title: 'Tasks',
    status: 'core',
    purpose: 'Plan work against the energy available today.',
  },
  {
    route: 'reflect',
    navLabel: 'Check in',
    title: 'Reflect',
    status: 'core',
    purpose: 'Record mood, energy, anxiety, sleep, or a private note.',
  },
  {
    route: 'practices',
    navLabel: 'Practices',
    title: 'Practices',
    status: 'core',
    purpose: 'Use a short grounding, breathing, or focus practice.',
  },
  {
    route: 'trends',
    navLabel: 'Rhythm',
    title: 'Rhythm',
    status: 'core',
    purpose: 'Review personal patterns without scores or streaks.',
  },
  {
    route: 'crisis',
    navLabel: 'Crisis plan',
    title: 'Crisis plan',
    status: 'utility',
    purpose: 'Keep personal support steps and crisis resources nearby.',
  },
  {
    route: 'settings',
    navLabel: 'Settings',
    title: 'Settings',
    status: 'utility',
    purpose: 'Control appearance, presence, and local preferences.',
  },
  {
    route: 'diary',
    navLabel: 'Diary cards',
    title: 'Diary cards',
    status: 'vaulted',
    purpose: 'Preserved structured DBT-style reflection records.',
    vaultReason: 'Specialist terminology and self-harm fields require deliberate opt-in and a dedicated safety introduction.',
  },
  {
    route: 'erp',
    navLabel: 'ERP notes',
    title: 'ERP notes',
    status: 'vaulted',
    purpose: 'Preserved exposure-and-response-prevention session notes.',
    vaultReason: 'Exposure work should not be presented as a default self-guided workflow without a specialist safety introduction.',
  },
  {
    route: 'meds',
    navLabel: 'Medication reference',
    title: 'Medication reference',
    status: 'vaulted',
    purpose: 'Preserved local reference list for names, doses, and usual times.',
    vaultReason: 'The reference-only boundary needs deliberate opt-in so it is never mistaken for reminders or adherence monitoring.',
  },
] as const;

export type Capability = (typeof CAPABILITIES)[number];
export type Route = Capability['route'];
export type CapabilityStatus = Capability['status'];

export const CORE_CAPABILITIES = CAPABILITIES.filter((capability) => capability.status === 'core');
export const UTILITY_CAPABILITIES = CAPABILITIES.filter((capability) => capability.status === 'utility');
export const CAPABILITY_VAULT = CAPABILITIES.filter((capability) => capability.status === 'vaulted');

export function capabilityFor(route: string): Capability | undefined {
  return CAPABILITIES.find((capability) => capability.route === route);
}

export function isRoute(route: string): route is Route {
  return capabilityFor(route) !== undefined;
}
