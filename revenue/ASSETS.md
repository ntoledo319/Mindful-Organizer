# Asset Audit

_Cycle 3 handoff update 2026-07-15. Scope is the containment root only._

## Publication outcome — 2026-08-31

Microsoft certified exact PAULATIM-001 and, under the owner's explicit
publication direction, the manual hold was released. Paulatim 1.1.1 is now
publicly available for $14.99 USD at
<https://apps.microsoft.com/detail/9PLRSZZMFPJH>. Microsoft's live catalog
exposes a purchase action, so the official Windows package is now a sellable
unit. No purchase, payout, or collected revenue has yet been observed. The
physical-Windows keyboard/Narrator/presentation pass remains an explicit
post-publication validation gap, not a claimed capability.

## Execution outcome — 2026-08-28

PAULATIM-001 now exists at exact source `f2d2a417`. Quality 33169087812 and
Windows 33169087811 passed; `Paulatim 1.1.1.appx` hashes to
`af8b458149d4c00de7f02d4f4c73a4b786d14dbbd391b0db7e1750d4bf4b5146`, and
the exact kit is staged at `tmp/PAULATIM-001-f2d2a41/`. Partner Center contains
only that package and five matching screenshots. The Hearth package/name were
removed; Age ratings, tax, and payment profiles show Complete; submission
`1152921505701225649` is In certification under a manual publication hold. The
smallest sellable unit is technically staged for Microsoft review but is not
yet certified, Store-signed/installed, published, live, or purchasable.

## Current correction — 2026-08-28

The product's visible name is now **Paulatim**. Exact Paulatim is reserved on
existing Store product `9PLRSZZMFPJH`, while the stable assigned identity
remains `ToledoTechnologies.Hearth`. All AMPLE-001 and Hearth package/screenshot
evidence below is historical and never-submit. The source has been renamed with
stable app/storage identifiers preserved, but PAULATIM-001 does not exist until
the fresh exact-SHA CI cycle completes. The buyer capability, $14.99 offer, and
smallest sellable unit are otherwise unchanged.

## Current correction — 2026-08-19

The completeness and exact-release sections below describe the Hearth-era
candidate and are retained as historical evidence. Source is now renamed to
**Ample**, but no Ample AppX exists: the package identity is unverified, the
first Ample CI runs failed before artifact upload, and CAND-002 is never-submit.
The buyer capability and smallest sellable unit are unchanged; package
generation, exact-candidate evidence, and the Partner Center draft must be
re-established after the observed identity is supplied.

## Current correction — 2026-08-25

Partner Center product `9PLRSZZMFPJH` was reobserved with exact package identity
`ToledoTechnologies.Hearth`; only the Hearth app name is currently reserved.
The identity is now verified for a fresh build, but no new candidate existed at
observation time and Ample name reservation remains owner-only.

### Candidate outcome — 2026-08-25T11:51Z

AMPLE-001 now exists at exact source `3b8d225`: Windows run 32844120483 passed,
AppX `7d6ca584…61866b` and five exact-SHA screenshots were independently
verified and staged at `tmp/AMPLE-001-3b8d225/`. This restores a CI-validated
smallest sellable unit, but not a submitted, certified, published, or
purchasable product. Ample display-name reservation and all marketplace owner
gates remain open.

### Continuation check — 2026-08-26

Live `git`/GitHub and the staged kit were re-derived: canonical `main` remains
a documentation-only descendant of exact candidate source `3b8d225`; candidate
CI is green; the AppX still hashes to `7d6ca584…61866b`; and all five screenshot
hashes still match. No second candidate is needed or authorized. The remaining
asset risk is operational selection: every AppX except AMPLE-001 is now marked
historical/never-submit at the `tmp/` staging root.

### Partner Center draft observation — 2026-08-27

Authenticated Partner Center now reports the exact display name **Ample** as
unavailable. **Ample Energy Planner** returned available, but it was not
reserved because the owner retained that decision. The draft price was
observed at $0 and was corrected and saved to the already approved $14.99
one-time price; the existing Productivity / Health + fitness categories and
privacy URL were rechecked and left unchanged. AMPLE-001 and its screenshots
remain staged locally and were not uploaded. No listing-name change,
submission, certification, publication, IARC, terms, or payout/tax action
occurred.

## Workspace inventory

There is one product codebase in the workspace: **Paulatim**, an
Electron/React/TypeScript Windows desktop application backed by in-memory SQLite
and encrypted local snapshots. Generated dependencies, caches, build output,
evidence, and assistant state are not separate assets.

## Codebase: Paulatim

- **Buyer sentence:** Paulatim is a calm private Windows organizer that helps a
  person choose an energy budget, plan tasks that fit it, check in, and review
  their own rhythm without an account or cloud record sync.
- **Completeness:** Release-candidate source, tests, deterministic assets,
  package validation, DPAPI lifecycle automation, Store screenshots, support
  forms, a security policy, and the commercial product tour are complete. The
  exact unsigned AppX is validated in a fully populated Partner Center draft.
  A TOS-compliant manual IARC retake, seller/payout confirmation, Microsoft
  certification, Store-signed smoke/accessibility observation, and publication
  remain.
- **Completeness correction (2026-08-26):** the preceding Partner Center
  validation sentence records the historical Hearth draft. AMPLE-001 is
  CI-validated and staged but has not been uploaded or validated in Partner
  Center; the Ample listing fields remain repository-only.
- **Completeness correction (2026-08-28):** AMPLE-001 is now historical and
  never-submit. Paulatim is reserved and Age ratings is observed Complete, but
  PAULATIM-001 1.1.1 has not yet completed exact-SHA CI or been uploaded. Payout
  readiness still needs a non-sensitive live reconciliation before submission.
- **Completeness correction (2026-08-31):** the preceding corrections are
  historical. Exact PAULATIM-001 passed CI and Microsoft certification and is
  publicly purchasable at $14.99. IARC and tax/payment readiness are Complete;
  only the physical-Windows HQ-03 validation remains open. Separately, HQ-08
  records the owner-controlled correction for the live generic SupportUri.
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
- **Smallest sellable unit:** The future official x64 Paulatim 1.1.1 Store
  package at a one-time $14.99 price, with honest wellness and local-data
  boundaries. No sellable package exists until PAULATIM-001 is verified.
- **Sellable-unit correction (2026-08-31):** exact PAULATIM-001 is now the
  certified, live $14.99 Store package. No purchase or payout is yet observed.

## Separable asset map

### A1 — Full Paulatim desktop app

Launch scope: Today, Tasks, Check in, Practices, Rhythm, Crisis, and Settings.
Smallest sellable unit: the official Windows package. Status: release candidate
and Store draft complete; public support path prepared; not submitted or public.

_Status correction 2026-08-26: “Store draft complete” above records the
historical Hearth draft. AMPLE-001 is CI-validated and staged, but the Ample
package, listing fields, and screenshots have not been uploaded or saved in
Partner Center._

_Status correction 2026-08-28: PAULATIM-001 replaces AMPLE-001 and is still in
pre-CI preparation. Paulatim is reserved and IARC is Complete; no Paulatim
package/listing/screenshots are saved, submitted, certified, or live._

_Execution outcome 2026-08-28: the preceding correction records the earlier
same-day state. Exact PAULATIM-001 is now CI-verified and submitted with its
listing/screenshots. It is in certification under a manual publication hold;
it is not certified, live, purchasable, or revenue-producing._

_Publication outcome 2026-08-31: Microsoft certified that exact package and
the owner-authorized publication completed. The official Store package is live
and purchasable at $14.99; sales and collected revenue remain unobserved._

### A2 — Presence and Focus Guard engine

Tray lifecycle, optional whole-screen dim, focus hold, settings, notifications,
and escape routes. Smallest sellable unit: a narrowly extracted Focus Guard
utility. Status: bundled into Paulatim; standalone frame is reserve-only.

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

The source is no longer blocked by architecture, encryption, consent, asset
rights, listing copy, support setup, package automation, account readiness, or
submission preparation. Exact PAULATIM-001 is in Microsoft certification under
a manual publication hold. Remaining gates are Microsoft's result, the
Store-signed Windows human observation, and a separate publication decision.
No asset is purchasable, so collected revenue remains zero.

_Publication correction 2026-08-31: the preceding sentence is superseded.
Paulatim is now purchasable through the Microsoft Store; collected revenue
still remains zero because no sale or payout has been observed._

## Cycle 3 continuation authority — 2026-07-15

Root HANDOFF.md is the canonical zero-context continuation map. It preserves the accepted candidate, capability-vault boundary, public/private evidence distinction, release sequence, verification commands and completion criteria. Partner Center facts remain last observed 2026-07-14 until reverified live.
