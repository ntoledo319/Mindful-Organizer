# Hearth

**Plan the day you have, not the day a calendar assumes.**

Hearth is a privacy-first Windows energy planner for ADHD and other
variable-capacity days. It gives tasks an estimated energy cost, keeps a finite
daily “spoon” budget, and shows a small set of open tasks whose recorded cost
fits what remains.

> **Release status:** Hearth is substantial software with a generated x64 Store
> package, but it is not currently certified, listed, or purchasable. The current
> source implements authenticated encrypted snapshots and OS-protected key
> storage, but the exact Windows release package still needs migration,
> installation, accessibility, and certification verification. See
> store/README.md before making any availability claim.

## The core loop

1. **Set the capacity you have.** Choose a daily energy budget from 4 to 24.
   Optional mood, energy, and sleep check-ins shape a plain-language Today
   briefing, but Hearth never infers or changes that budget from a diagnosis or
   a check-in.
2. **Cost the work honestly.** Give a task its priority, expected duration, and
   energy demand. Hearth estimates a spoon cost, and completing the task
   subtracts that cost from today's budget.
3. **Choose what fits.** Today can show up to three open tasks whose recorded
   cost fits the remaining budget. Smart Decompose can replace one task with a
   short set of starter steps in one local transaction.

This is deliberately not an automatic productivity score or a diagnosis. The
rules are local and inspectable, and the user remains in control of every entry
and action.

## Privacy model

Hearth has no account, cloud API, advertising, record sync, app telemetry, or
remote AI service. While the app is open, SQLite runs in memory. At rest, Hearth
writes versioned, authenticated AES-256-GCM snapshots with a fresh random IV for
each successful write. A random 256-bit key is protected through Electron
`safeStorage`—Windows DPAPI on Windows—and Hearth fails closed when protected key
storage is unavailable.

Those protections have limits. Decrypted records and the key exist in process
memory while Hearth is open, and the operating system may copy memory into swap,
hibernation, crash, or diagnostic storage. Someone controlling the signed-in OS
session may be able to access the same credential facility. User-requested JSON
and PDF exports are plaintext, and deleting old database files cannot guarantee
removal from SSD recovery, snapshots, or backups. During migration, the legacy
plaintext database is retained only until encrypted copies verify; the encrypted
migration backup is retired after two verified encrypted generations. Read
[the privacy policy](docs/PRIVACY.md) before entering sensitive information.

## Secondary toolkit

The launch promise is energy planning. Hearth also contains optional local tools
that support a broader personal routine:

| Area | Demonstrable behavior |
|---|---|
| Reflect | Mood, energy, anxiety, sleep, and typed journal entries |
| Rhythm | Local 7, 14, and 30 day trends plus a user-requested PDF summary |
| Practices | Guided breathing, grounding, body scan, and focus blocks |
| Presence | Optional tray controls, whole-screen dim, and focus hold |
| Crisis plan | User-written warning signs, coping steps, contacts, and US 988 links |
| Preserved modules | ERP notes, diary cards, medication references, and legacy condition-label metadata remain in the codebase but are outside the default experience pending dedicated opt-in and safety review |

Hearth does not monitor a person, guarantee crisis detection, deliver medication
reminders, diagnose a condition, provide treatment, or replace professional or
emergency care. In a US crisis, call or text 988; in immediate danger, call the
local emergency number.

## What the paid Store package would provide

The source is MIT licensed and stays public. The proposed one-time Microsoft
Store purchase pays for an official x64 MSIX package and Store delivery, not
exclusive code, a clinical capability, or guaranteed future features.

The reserved Store identity is real, but the current build is not submitted.
Price, package upload, age rating, declarations, screenshots, public URLs, and
the final publish action remain manual owner decisions. The detailed release
gate is in [store/README.md](store/README.md).

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

    npm install
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

The planned public support path is GitHub Issues. It must not be advertised as a
working customer channel until issue creation is enabled and verified.
