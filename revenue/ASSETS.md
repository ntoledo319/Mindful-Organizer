# Asset Audit

_Cycle 3 handoff update 2026-07-15. Scope is the containment root only._

## Workspace inventory

There is one product codebase in the workspace: **Hearth**, an
Electron/React/TypeScript Windows desktop application backed by in-memory SQLite
and encrypted local snapshots. Generated dependencies, caches, build output,
evidence, and assistant state are not separate assets.

## Codebase: Hearth

- **Buyer sentence:** Hearth is a calm private Windows organizer that helps a
  person choose an energy budget, plan tasks that fit it, check in, and review
  their own rhythm without an account or cloud record sync.
- **Completeness:** Release-candidate source, tests, deterministic assets,
  package validation, DPAPI lifecycle automation, Store screenshots, support
  forms, a security policy, and the commercial product tour are complete. The
  exact unsigned AppX is validated in a fully populated Partner Center draft.
  A TOS-compliant manual IARC retake, seller/payout confirmation, Microsoft
  certification, Store-signed smoke/accessibility observation, and publication
  remain.
- **Distribution target:** Microsoft Store using reserved product ID
  9PLRSZZMFPJH and its built-in discovery and checkout. GitHub remains the
  public source and policy host, not the commercial checkout.
- **License:** Project source is MIT, copyright Nicholas Toledo. Runtime
  dependencies are covered by THIRD_PARTY_NOTICES.md and the production audit
  reports zero known vulnerabilities.
- **Provenance:** Shipping art is deterministically generated and documented in
  resources/BRAND_PROVENANCE.md. Earlier undocumented PNGs are preserved
  byte-for-byte in resources/vault/unverified-2026-07-14/ and excluded from the
  package.
- **Data protection:** SQLite operates in memory. At rest, versioned snapshots
  use authenticated AES-256-GCM with a random 256-bit key protected by Windows
  DPAPI through Electron safeStorage. Primary/backup recovery, legacy plaintext
  migration, missing-key fail-closed behavior, interrupted erase, and plaintext
  export warnings are covered by automated Windows lifecycle validation.
- **Single capability a stranger could pay for:** A maintained, packaged,
  Store-delivered offline Windows planner built around user-chosen capacity.
- **Smallest sellable unit:** The official x64 Hearth 1.1.0 Store package at a
  one-time $14.99 price, with honest wellness and local-data boundaries.

## Separable asset map

### A1 — Full Hearth desktop app

Launch scope: Today, Tasks, Check in, Practices, Rhythm, Crisis, and Settings.
Smallest sellable unit: the official Windows package. Status: release candidate
and Store draft complete; public support path prepared; not submitted or public.

### A2 — Presence and Focus Guard engine

Tray lifecycle, optional whole-screen dim, focus hold, settings, notifications,
and escape routes. Smallest sellable unit: a narrowly extracted Focus Guard
utility. Status: bundled into Hearth; standalone frame is reserve-only.

### A3 — Adaptive planning engine

User-chosen 4–24 energy budget, exact recorded task costs, up to three fitting
recommendations, local briefing rules, and transactional Smart Decompose.
Smallest sellable unit: a tested energy-budget planning module plus demo.

### A4 — Local-first Electron architecture

Sandboxed renderer, typed preload bridge, sender-validated IPC, in-memory
SQLite, authenticated encrypted persistence, DPAPI key protection, migrations,
packaging, and CI. Smallest sellable unit: a new production kit with clean demo,
threat model, upgrade guide, and tests.

### A5 — Earthenware UI system

Warm light/dark tokens, Fraunces/Atkinson typography, accessible controls,
motion preferences, charts, modal focus management, and deterministic brand
assets. Smallest sellable unit: a documented React theme/component kit.

## Preserved capability inventory

The launch surface was narrowed without destroying work:

| Capability | Safe-keeping location | Launch state |
|---|---|---|
| Diary cards and self-harm urge field | schema, types, IPC/repository, Diary renderer, JSON export | Vaulted pending opt-in and safety review |
| ERP session notes | schema, types, IPC/repository, ERP renderer, JSON export | Vaulted pending specialist review |
| Medication reference | medication tables, types, IPC/repository, Meds renderer, JSON export | Vaulted pending a clearer reference-only contract |
| Legacy condition labels | encrypted Settings metadata and JSON export | Collection UI removed; compatibility preserved |
| Superseded artwork | resources/vault/unverified-2026-07-14/ | Excluded from shipping; preserved byte-for-byte |

docs/CAPABILITY_VAULT.md is the restoration contract. Route-registry tests keep
the three specialist screens preserved and renderable while preventing them
from silently returning to default navigation.

## Exact release evidence

- Candidate source: 8172603b62c2457696608c145511bd3fe92429d4
- Candidate application tree: d731d4de78529435c5cc1e0a036536701cc737e9
- Quality run: <https://github.com/ntoledo319/Mindful-Organizer/actions/runs/29322423682>
- Windows Store run: <https://github.com/ntoledo319/Mindful-Organizer/actions/runs/29322423622>
- AppX SHA-256:
  4900f3823febace53f86f69ee2567b50208aec8f6677741c3c4dcf3667facdb1
- GitHub package artifact ID: 8306541856
- Screenshot artifact ID: 8306519500
- Public launch-hardening commit:
  d01c013fd8beec91014c37d27a9a310cf5dd0470
- Public-commit Quality run:
  <https://github.com/ntoledo319/Mindful-Organizer/actions/runs/29345864617>
- Public-commit Windows Store run:
  <https://github.com/ntoledo319/Mindful-Organizer/actions/runs/29345863949>
- Verification-only package artifact ID / AppX SHA-256:
  8316167277 / 93279f430e024deb3b28ee12d98271ffa19d7093f8d9e667e7c9defcace2fc10

The later verification build proves the public commit remains buildable and
package-valid. It does not supersede the exact candidate already saved and
validated in Partner Center because this cycle changed support, launch,
validation, and documentation surfaces rather than product runtime code.

## Current bottom line

The product is no longer blocked by architecture, encryption, consent, asset
rights, package generation, listing copy, screenshots, support setup, public
repository presentation, vulnerability intake, CI, or core Partner Center data
entry. It is a high-quality technical release candidate,
but it is not a live listing. Because the accepted AppX is intentionally
unsigned, Microsoft certification—not a locally altered test signature—is the
exact-package technical gate. The remaining blockers are manual IARC/legal
attestation, seller payout setup, certification, Store-signed Windows human
observation, and publication. No asset is yet purchasable, so collected revenue
remains zero.

## Cycle 3 continuation authority — 2026-07-15

Root HANDOFF.md is the canonical zero-context continuation map. It preserves the accepted candidate, capability-vault boundary, public/private evidence distinction, release sequence, verification commands and completion criteria. Partner Center facts remain last observed 2026-07-14 until reverified live.

