# Ample

> **Continuation:** agents and operators with no prior context must start with
> [HANDOFF.md](HANDOFF.md) and [PROJECT_TRACKER.md](PROJECT_TRACKER.md);
> monetization cycles then read all six files in `revenue/`.

**Plan the day you have, not the day a calendar assumes.**

Ample is a privacy-first Windows energy planner for ADHD and other
variable-capacity days. It gives tasks an estimated energy cost, keeps a finite
daily “spoon” budget, and shows a small set of open tasks whose recorded cost
fits what remains.

> **Release status:** Ample 1.1.0 is an accepted x64 package in a fully prepared
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
   briefing, but Ample never infers or changes that budget from a diagnosis or
   a check-in.
2. **Cost the work honestly.** Give a task its priority, expected duration, and
   energy demand. Ample estimates a spoon cost, and completing the task
   subtracts that cost from today's budget.
3. **Choose what fits.** Today can show up to three open tasks whose recorded
   cost fits the remaining budget. Smart Decompose can replace one task with a
   short set of starter steps in one local transaction.

This is deliberately not an automatic productivity score or a diagnosis. The
rules are local and inspectable, and the user remains in control of every entry
and action.

## Privacy model

Ample has no account, cloud API, advertising, record sync, app telemetry, or
remote AI service. While the app is open, SQLite runs in memory. At rest, Ample
writes versioned, authenticated AES-256-GCM snapshots with a fresh random IV for
each successful write. A random 256-bit key is protected through Electron
`safeStorage`—Windows DPAPI on Windows—and Ample fails closed when protected key
storage is unavailable.

Those protections have limits. Decrypted records and the key exist in process
memory while Ample is open, and the operating system may copy memory into swap,
hibernation, crash, or diagnostic storage. Someone controlling the signed-in OS
session may be able to access the same credential facility. User-requested JSON
and PDF exports are plaintext, and deleting old database files cannot guarantee
removal from SSD recovery, snapshots, or backups. During migration, the legacy
plaintext database is retained only until encrypted copies verify; the encrypted
migration backup is retired after two verified encrypted generations. Read
[the privacy policy](docs/PRIVACY.md) before entering sensitive information.

## Secondary toolkit

The launch promise is energy planning. Ample also contains optional local tools
that support a broader personal routine:

| Area | Demonstrable behavior |
|---|---|
| Reflect | Mood, energy, anxiety, sleep, and typed journal entries |
| Rhythm | Local 7, 14, and 30 day trends plus a user-requested PDF summary |
| Practices | Guided breathing, grounding, body scan, and focus blocks |
| Presence | Optional tray controls, whole-screen dim, and focus hold |
| Crisis plan | User-written warning signs, coping steps, contacts, and US 988 links |
| Preserved modules | ERP notes, diary cards, medication references, and legacy condition-label metadata remain in the codebase but are outside the default experience pending dedicated opt-in and safety review |

Ample does not monitor a person, guarantee crisis detection, deliver medication
reminders, diagnose a condition, provide treatment, or replace professional or
emergency care. In a US crisis, call or text 988; in immediate danger, call the
local emergency number.

## What the paid Store package would provide

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
    landing/             Zero-dependency pre-release commercial landing artifact
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
