# Paulatim

> **Continuation:** agents and operators with no prior context must start with
> [HANDOFF.md](HANDOFF.md) and [PROJECT_TRACKER.md](PROJECT_TRACKER.md);
> monetization cycles then read all six files in `revenue/`.

**Plan the day you have, not the day a calendar assumes.**

Paulatim brings energy-budget planning to Windows for ADHD and other
variable-capacity days. It gives tasks an estimated energy cost, keeps a finite
daily “spoon” budget, and shows a small set of open tasks whose recorded cost
fits what remains. Its local design, with no separate Paulatim account, is
supporting proof, not the headline.

> **Release status correction — 2026-08-28:** Paulatim is reserved on existing
> Partner Center product `9PLRSZZMFPJH`, and the source/listing rename is in
> progress. No Paulatim AppX exists yet. AMPLE-001 and every Hearth package are
> historical and never-submit; only a fresh exact-SHA Paulatim CI candidate may
> replace the canceled draft and proceed to certification.

> **Execution outcome — 2026-08-28:** exact source `f2d2a417` produced
> PAULATIM-001 (`Paulatim 1.1.1.appx`, SHA-256
> `af8b458149d4c00de7f02d4f4c73a4b786d14dbbd391b0db7e1750d4bf4b5146`) through
> green Quality and Windows CI. The Paulatim package, listing, and five matching
> screenshots were saved in Partner Center; the Hearth package and Hearth
> display-name reservation were removed. Submission `1152921505701225649` is
> now **In certification** under a manual publication hold. It is not certified,
> published, live, or purchasable; Microsoft must finish review and the
> Store-signed build must pass HQ-03 before a separate **Publish now** decision.

> **Publication outcome — 2026-08-31:** Microsoft certified exact PAULATIM-001
> (`Paulatim 1.1.1.appx`, SHA-256
> `af8b458149d4c00de7f02d4f4c73a4b786d14dbbd391b0db7e1750d4bf4b5146`).
> After the owner's explicit publication direction, **Publish now** was used and
> the signed-out Store page plus Microsoft's live catalog were observed with an
> active **$14.99 USD** purchase action on the
> [Microsoft Store](https://apps.microsoft.com/detail/9PLRSZZMFPJH?cid=github-readme).
> The physical-Windows
> keyboard, Narrator, forced-colors, scaling, and reduced-motion pass remains
> unobserved, so no Store accessibility declaration is claimed.

> **Market/account correction — 2026-08-31:** the observed $14.99 purchase
> action is for the United States Store market. “No account” in product copy
> means no separate Paulatim or in-app account; Microsoft may require a
> Microsoft account for Store acquisition or installation.

> **Record-integrity note — 2026-08-28:** the next paragraph is retained as a
> historical 2026-08-25 misstatement, not release evidence: it mislabeled the
> Hearth draft as Ample. The dated corrections immediately after it supply the
> observed facts.
>
> **Historical misstatement present 2026-08-25:** Ample 1.1.0 is an accepted x64 package in a fully prepared
> Microsoft Partner Center draft, but it is not certified, public, or
> purchasable. The exact package passed source, package-structure, and real
> Windows DPAPI lifecycle automation. Microsoft certification, a manual Windows
> accessibility pass, an owner-completed IARC attestation, and seller payout
> readiness remain release gates. See store/README.md before making any
> availability claim.

> **Correction — 2026-08-19:** the preceding release-status paragraph describes
> the historical Hearth package. The Ample rename changed the manifest; no Ample
> AppX exists yet, and `store/identity.json` remains blocked until its package
> identity is copied from Partner Center and explicitly verified.

> **Correction — 2026-08-25:** Partner Center was reobserved. Existing product
> `9PLRSZZMFPJH` retains exact Package/Identity/Name
> `ToledoTechnologies.Hearth`; only `Hearth` is currently reserved. The package
> identity is now verified for a fresh Ample-branded build, but no fresh
> candidate existed at observation time and reserving the Ample display name
> remains an owner-only pre-submission action.

> **Candidate update — 2026-08-25:** exact source `3b8d225` passed Quality and
> Windows CI. `Ample 1.1.0.appx` hashes to `7d6ca584…61866b` and is staged with
> five exact-SHA screenshots. This is CI candidate evidence only: the package
> is not uploaded, submitted, certified, published, or purchasable, and the
> owner must reserve the Ample display name before submission.

## The core loop

1. **Set the capacity you have.** Choose a daily energy budget from 4 to 24.
   Optional mood, energy, and sleep check-ins shape a plain-language Today
   briefing, but Paulatim never infers or changes that budget from a diagnosis or
   a check-in.
2. **Cost the work honestly.** Give a task its priority, expected duration, and
   energy demand. Paulatim estimates a spoon cost, and completing the task
   subtracts that cost from today's budget.
3. **Choose what fits.** Today can show up to three open tasks whose recorded
   cost fits the remaining budget. Smart Decompose can replace one task with a
   short set of starter steps in one local transaction.

This is deliberately not an automatic productivity score or a diagnosis. The
rules are local and inspectable, and the user remains in control of every entry
and action.

## Privacy model

Paulatim has no separate in-app account, cloud API, advertising, record sync,
app telemetry, or remote AI service. While the app is open, SQLite runs in memory. At rest, Paulatim
writes versioned, authenticated AES-256-GCM snapshots with a fresh random IV for
each successful write. A random 256-bit key is protected through Electron
`safeStorage`—Windows DPAPI on Windows—and Paulatim fails closed when protected key
storage is unavailable.

Those protections have limits. Decrypted records and the key exist in process
memory while Paulatim is open, and the operating system may copy memory into swap,
hibernation, crash, or diagnostic storage. Someone controlling the signed-in OS
session may be able to access the same credential facility. User-requested JSON
and PDF exports are plaintext, and deleting old database files cannot guarantee
removal from SSD recovery, snapshots, or backups. During migration, the legacy
plaintext database is retained only until encrypted copies verify; the encrypted
migration backup is retired after two verified encrypted generations. Read
[the privacy policy](docs/PRIVACY.md) before entering sensitive information.

## Secondary toolkit

The launch promise is energy planning. Paulatim also contains optional local tools
that support a broader personal routine:

| Area | Demonstrable behavior |
|---|---|
| Reflect | Mood, energy, anxiety, sleep, and typed journal entries |
| Rhythm | Local 7, 14, and 30 day trends plus a user-requested PDF summary |
| Practices | Guided breathing, grounding, body scan, and focus blocks |
| Presence | Optional tray controls, whole-screen dim, and focus hold |
| Crisis plan | User-written warning signs, coping steps, contacts, and US 988 links |
| Preserved modules | ERP notes, diary cards, medication references, and legacy condition-label metadata remain in the codebase but are outside the default experience pending dedicated opt-in and safety review |

Paulatim does not monitor a person, guarantee crisis detection, deliver medication
reminders, diagnose a condition, provide treatment, or replace professional or
emergency care. In a US crisis, call or text 988; in immediate danger, call the
local emergency number.

## What the paid Store package provides

Paulatim 1.1.1 is available in the United States on the
[Microsoft Store](https://apps.microsoft.com/detail/9PLRSZZMFPJH?cid=github-readme)
for a one-time $14.99 USD purchase. The purchase pays
for the official x64 package and Store delivery; the source remains MIT
licensed. Microsoft certification and automated Windows package/lifecycle
checks passed. Manual assistive-technology and presentation checks remain an
open post-publication validation item.

The paragraphs and corrections below preserve the release path that preceded
publication.

The source is MIT licensed and stays public. The proposed one-time Microsoft
Store purchase pays for an official x64 MSIX package and Store delivery, not
exclusive code, a clinical capability, or guaranteed future features.

The reserved Store identity is real. The exact package, proposed $14.99 US
price, listing copy, declarations, and five screenshots are saved in Submission
1 under a manual publication hold. The draft has not been submitted for
certification. The owner must still complete the IARC legal attestation and
seller payout checks; Microsoft must certify the package; and a human must
review the installed Store-signed build before publication. The detailed
release gate is in [store/README.md](store/README.md).

> **Correction — 2026-08-19:** those saved-package and identity statements are
> historical Hearth observations from 2026-07-14, not current Ample evidence.
> Partner Center has not been reobserved after the rename.

> **Correction — 2026-08-25:** product identity, app names, and the submission
> overview were reobserved. The exact identity is
> `ToledoTechnologies.Hearth`, only `Hearth` is reserved, and the validated
> package shown in Partner Center remains the historical Hearth AppX. Ample
> listing fields were not saved or reverified.

> **Correction — 2026-08-28:** the owner selected and reserved Paulatim and
> authorized a full certification submission. The previous Hearth submission
> was canceled back to draft. The Paulatim listing and fresh package have not
> yet been saved, certified, published, or made purchasable. Partner Center
> shows Age ratings Complete; do not retake that legal questionnaire. Private
> payout readiness still requires a non-sensitive status reconciliation.

> **Execution outcome — 2026-08-28:** the preceding correction describes the
> pre-submission state. Partner Center now shows Age ratings, tax profile, and
> payment profile Complete. Exact PAULATIM-001 is the only uploaded package and
> the submission is in certification under the manual publication hold.

## Technology

| Layer | Current implementation |
|---|---|
| Desktop shell | Electron 43, sandboxed renderer, context isolation, no renderer Node integration |
| Interface | React 18, TypeScript, Vite, Tailwind CSS, Framer Motion |
| Local data | SQLite through better-sqlite3 in the main process |
| State | Zustand plus TanStack Query |
| Desktop bridge | Typed preload contract and sender-validated IPC handlers |
| Packaging | electron-builder, including an x64 AppX/MSIX target |
| CI | Node 22.12 quality and Windows package workflows |

## Local development

Prerequisite: Node.js 22.12 or later and npm.

    npm ci
    npm run icons
    npm run dev

Quality gate:

    npm run lint
    npm run typecheck
    npm test
    npm run vite:build
    npm run secrets
    npm run licenses
    npm run brand-assets
    npm run store:validate

Package commands:

    npm run build:win
    npm run build:mac
    npm run build:linux
    npm run build:winstore

Build output lands in release/. A successful package command is not a
certification, signing, installation, security, or usability result.

## Repository map

    electron/            Main process, local data, IPC, wellness rules, PDF export
    src/shared/          Types, IPC contract, spoon-cost logic, summary builder
    src/renderer/        React shell, screens, components, state, and styles
    resources/           Deterministically generated shipping brand assets and provenance
    scripts/             Icon, Store-asset, and third-party-notice generation
    store/               Manual Store listing, launch, campaign, and screenshot plans
    landing/             Zero-dependency undeployed commercial landing artifact
    docs/                Architecture, design, privacy, terms, refunds, and accessibility
    revenue/             Durable monetization state and evidence ledger

## Distribution documents

- [Store release path](store/README.md)
- [Listing metadata](store/listing-metadata.json)
- [Screenshot plan](store/SCREENSHOTS.md)
- [Campaign measurement](store/CAMPAIGNS.md)
- [Product-page experiments](store/PRODUCT-PAGE-EXPERIMENTS.md)
- [Launch drafts](store/LAUNCH_KIT.md)
- [Exact-candidate Windows validation](store/WINDOWS-VALIDATION.md)
- [Capability vault](docs/CAPABILITY_VAULT.md)
- [Static landing artifact](landing/README.md)
- [Shipping brand provenance](resources/BRAND_PROVENANCE.md)

## Legal and support

- [Privacy](docs/PRIVACY.md)
- [Terms](docs/TERMS.md)
- [Purchases and refunds](docs/REFUNDS.md)
- [Accessibility status](docs/ACCESSIBILITY.md)
- [Support status](docs/SUPPORT.md)
- [License](LICENSE)
- [Third-party notices](THIRD_PARTY_NOTICES.md)

The public support page is [docs/SUPPORT.md](docs/SUPPORT.md). Reproducible
software reports use privacy-guarded GitHub Issue forms and require a free
GitHub sign-in. Private records, exports, databases, keys, and crisis or medical
requests do not belong there.
