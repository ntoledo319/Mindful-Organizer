# Asset Audit

_Cycle 0 audit completed 2026-07-14. Scope is the containment root only._

## Workspace inventory

There is one codebase in the workspace: **Hearth**, an Electron/React/TypeScript
desktop application backed by local SQLite. Generated dependency, cache, build,
virtual-environment, and assistant-state directories are not separate assets.

## Codebase: Hearth

- **Buyer sentence:** Hearth is a calm desktop organizer that budgets tasks
  against the energy a person actually has, keeps reflection data local, and can
  create a user-controlled PDF summary of recent trends.
- **Completeness:** The product is substantial and the local Node gate can run,
  but there is no current public release. Historical CI used the wrong Python
  stack, old release artifacts expired, and the Store publish workflow failed.
  This cycle repaired those paths, but a new remote CI run and Windows smoke test
  are still required.
- **Distribution target:** Microsoft Store MSIX using the existing reserved
  identity and free Partner Center account; itch.io is a conditional target for
  a new developer kit. GitHub remains source/document distribution only.
- **License:** Project source is MIT, copyright Nicholas Toledo. Runtime
  dependencies are permissive or OFL and are documented in
  `THIRD_PARTY_NOTICES.md`. Production `npm audit` currently reports zero known
  vulnerabilities.
- **Provenance risks:** Rights and AI-assisted provenance for
  `resources/app-icon.png` and `resources/hero-illustration.png` are not yet
  documented. That blocks binary publication. Public MIT history makes a bare
  source-code resale weak and non-exclusive.
- **Release/policy risks:** Wellness-adjacent records are stored without
  application-level encryption. Microsoft Store policy 10.5.4 requires modern
  cryptography for stored personal information, so the paid Store package is
  blocked pending a grounded protection design and implementation.
- **Single capability a stranger could pay for:** A maintained, packaged,
  Store-delivered offline Windows organizer with energy-aware planning.
- **Smallest sellable unit:** One official Windows MSIX package at a one-time
  price, with honest local-data disclosures and no gated clinical claim.

## Separable asset map

### A1 — Full Hearth desktop app

Today, Tasks, Reflect, Practices, Rhythm, session summary, crisis plan, presence,
ERP/diary notes, medication references, and settings in one local-first app.
Smallest sellable unit: official packaged Windows build.

### A2 — Presence and Focus Guard engine

Tray lifecycle, optional whole-screen dim, focus hold, settings, notifications,
and escape routes. Smallest sellable unit: a narrowly extracted Focus Guard app.

### A3 — Adaptive planning engine

Spoon estimates, daily energy budget, task ranking, briefing, and transactional
Smart Decompose. Smallest sellable unit: a tested energy-budget planning module
plus demo—not a copy of already-public files.

### A4 — Local-first Electron architecture

Sandboxed renderer, typed preload bridge, sender-validated IPC, SQLite
repositories/migrations, packaging, and CI. Smallest sellable unit: a new
production kit with clean-room demo, threat model, upgrade guide, and tests.

### A5 — Earthenware UI system

Warm light/dark tokens, accessible type, motion, and React primitives. Smallest
sellable unit: a new documented component/theme kit with rights-cleared assets.

## Current bottom line

The repo contains real engineering value, but no asset is truthfully
“purchasable” yet. The full app has the shortest path because its marketplace
identity already exists. The architecture kit has the highest plausible ticket,
but requires genuinely new value beyond the public MIT repository.

## Cycle 0 close evidence — 2026-07-14 01:40 EDT

- Public review branch:
  <https://github.com/ntoledo319/Mindful-Organizer/tree/feature/revenue-cycle-0>
- Hosted Quality Gate #41 passed locked install, lint, renderer/main typechecks,
  11 tests, and renderer/Electron bundle builds:
  <https://github.com/ntoledo319/Mindful-Organizer/actions/runs/29309084417>.
- Local unpacked packaging failed during the Electron 43 native SQLite rebuild
  because this jailed machine's Apple Clang 14 / SDK 13.3 lacks the C++20
  `<source_location>` header. No outside-jail toolchain change was attempted.
- Therefore the codebase is source-gate green, but its distributable status
  remains **not release-ready** pending hosted Windows package proof and the
  policy/provenance gates above.
