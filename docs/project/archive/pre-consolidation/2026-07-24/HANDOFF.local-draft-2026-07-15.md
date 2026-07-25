# Hearth Mission Handoff

_Canonical zero-context continuation document. Last reconciled 2026-07-15
(America/New_York), against public GitHub `main` at
`4a32b7306ab9ca76a09fb3fae399649c07543e5a` and Partner Center evidence last
observed 2026-07-14._

This document is deliberately self-contained. It tells a new agent what Hearth
is, what is already proven, what must not be redone, exactly what remains, and
how to finish the revenue mission without outside memory.

## 1. Non-negotiable startup sequence

`AGENTS.md` outranks this document. Its workspace jail, legal/TOS, $0 spend,
truth, no-autonomous-contact, owner-time, evidence, and state-file laws are hard
constraints.

1. Start inside:
   `/Users/nicholastoledo/Development/active/mindful_organizer`.
2. Resolve `pwd -P` and `AGENTS.md`. Stop if either target is outside that root.
3. Confirm line 1 of `revenue/PLAN.md` is the same absolute root.
4. Read `AGENTS.md` completely.
5. Read all six state files before acting, in this order:
   `revenue/ASSETS.md`, `revenue/OPPORTUNITIES.md`, `revenue/PLAN.md`,
   `revenue/METRICS.md`, `revenue/HUMAN_QUEUE.md`, and
   `revenue/DECISIONS.md`.
6. Read this file, then the task-specific sources listed below.
7. Check `git status --short --branch`, current `origin/main`, and recent CI.
   Preserve unrelated or user-owned changes. Never reset them away.
8. Every cycle must end with an externally visible shipment and updates to all
   six revenue state files.

Do not read skills, memory, repositories, home-directory files, `/tmp`, or any
other local path outside `WORKSPACE_ROOT`. Installed tools may be invoked, but
their global configuration must not be changed.

### Authority order when documents disagree

1. `AGENTS.md`
2. Newly observed live evidence recorded in `revenue/METRICS.md`
3. The six `revenue/` state files as a set
4. This handoff
5. `store/README.md` and `store/WINDOWS-VALIDATION.md`
6. README and older strategy/history documents

Never silently choose the most optimistic statement. Reverify, record the
observation, update every affected document, and preserve the evidence.

## 2. Mission and money truth

- Mission: collect **$4,000 cumulative profit from strangers by Day 28**, at $0
  spend and no more than 60 owner minutes.
- Cycle 0 / Day 1 evidence began 2026-07-14. If that remains the accepted start,
  gates are Day 7 = July 20, Day 14 = July 27, Day 21 = August 3, and Day 28 =
  August 10, 2026.
- Collected profit observed: **$0.00**.
- Current gap: **$4,000.00**.
- Live paid listings: **0**.
- Observed Store views, acquisitions, installs, purchases, refunds, fees, and
  payouts: none.
- GitHub stars and forks last observed: 0 / 0.

The active fast bet is a one-time **$14.99** US Microsoft Store purchase. At
Microsoft's documented 15% non-game app fee, planning net is $12.7415 per sale;
314 retained sales model $4,000.83 before refunds and tax adjustments. This is
arithmetic, not demand evidence.

The conditional heavy bet is a genuinely new $249 Hearth-to-Production
Electron kit. It is not built or listed and must not be represented as shipped.
The first reserve is a standalone Focus Guard Store utility. Do not dilute the
shortest certification path merely to create activity.

## 3. Product truth

Hearth 1.1.0 is an Electron 43 / React 18 / TypeScript / Vite Windows desktop
energy planner for ADHD and other variable-capacity days. The user chooses a
4–24 daily energy budget, records tasks with duration and energy demand, sees up
to three open tasks that fit the remaining budget, and may use local check-ins,
trends, guided practices, focus controls, a user-written crisis plan, and
requested JSON/PDF exports.

Hearth is personal organization and reflection software. It is not a medical
device, diagnosis, treatment, clinical monitor, healthcare service, emergency
service, or crisis detector. Never imply outcomes, protection, treatment,
clinical quality, or guaranteed privacy.

### Architecture map

- `electron/`: main process, SQLite repositories, migrations, encryption,
  sender-validated IPC, PDF export, lifecycle validation.
- `src/shared/`: typed IPC contract, models, spoon-cost and summary logic.
- `src/renderer/`: React shell, routes, screens, components, state and styles.
- `src/renderer/capabilities.ts`: executable visible/vaulted route registry.
- `resources/`: deterministic shipping art, icons, provenance and asset vault.
- `scripts/`: validation, screenshots, assets, notices and secret scanning.
- `store/`: authoritative Store metadata, screenshots, campaign, launch and
  Windows-validation procedures.
- `landing/`: scriptless, trackerless pre-release landing source; not deployed.
- `docs/`: privacy, terms, refunds, accessibility, support and architecture.
- `revenue/`: durable monetization brain and evidence ledger.

### Data-protection truth

SQLite operates in memory while Hearth is open. At rest, Hearth writes
versioned authenticated AES-256-GCM snapshots using fresh IVs and a random
256-bit key protected by Electron `safeStorage` / Windows DPAPI. It fails closed
when protected key storage is unavailable. CI covers encrypted persistence,
backup recovery, missing-key failure, legacy migration and retirement, export
warnings, key-first erase, and interrupted-erase recovery.

Required limits must accompany security claims: records and key are decrypted
in process memory while open; Windows may copy memory into swap, hibernation,
crash or diagnostic storage; someone controlling the signed-in OS session may
reach the same credential facility; user-requested JSON/PDF exports are
plaintext; deletion cannot guarantee removal from SSD recovery, snapshots or
backups. The developer cannot recover a lost protected key.

## 4. Preserved capabilities — do not delete

The launch surface was narrowed without destroying prior work. The restoration
contract is `docs/CAPABILITY_VAULT.md`.

- Diary cards, including a self-harm urge field
- ERP-session notes
- Medication-reference tables and screen
- Legacy condition-label metadata
- Unverified historic artwork under
  `resources/vault/unverified-2026-07-14/`

Their schemas, types, repository/IPC methods, renderers and export compatibility
are intentionally retained. They are absent from default navigation pending
specialist, opt-in, privacy, accessibility and Windows review. A cleanup must
not remove them. Permanent removal requires a reviewed migration, export
compatibility decision, vault update and new release candidate.

## 5. Immutable accepted release identity

The following package is already saved and marked Validated in Partner Center.
Do not replace, rebuild, sign, rename or confuse it with later CI output.

| Field | Accepted value |
|---|---|
| Source commit | `8172603b62c2457696608c145511bd3fe92429d4` |
| Application tree | `d731d4de78529435c5cc1e0a036536701cc737e9` |
| Package | `Hearth 1.1.0.appx` |
| Size | `175,488,515` bytes |
| SHA-256 | `4900f3823febace53f86f69ee2567b50208aec8f6677741c3c4dcf3667facdb1` |
| Package artifact | `hearth-msix`, ID `8306541856`, recorded expiry 2026-08-13 |
| Artifact ZIP digest | `sha256:4d5885c705cf6429e83ef3404135d6448ffdb903b0df8cd75e5fbf02d7d8a494` |
| Screenshot artifact | ID `8306519500` |
| Screenshot artifact digest | `sha256:b03e6e42b771da7f693575d79473275e90723adbeea23801d08f8de380e7c905` |
| Quality run | `29322423682` |
| Windows Store run | `29322423622` |
| Local recorded copy | `tmp/artifacts/final-msix/Hearth 1.1.0.appx` |

The accepted AppX is intentionally unsigned and has no `AppxSignature.p7x`.
Local test-signing changes its bytes. Standard GitHub-hosted Windows cannot
provide authoritative full WACK evidence for this exact unsigned candidate.
Microsoft certification is the exact-package install/run, security, technical
and content gate. A later Store-signed human Windows pass is still required.
The artifact ZIP digest and the inner AppX SHA are different evidence values;
never substitute one for the other.

### Later verification evidence — not the submission package

- Launch/support hardening commit:
  `d01c013fd8beec91014c37d27a9a310cf5dd0470`
- State close commit:
  `4a32b7306ab9ca76a09fb3fae399649c07543e5a`
- Quality run: `29345864617`
- Windows Store run: `29345863949`
- Verification AppX artifact: `8316167277`
- Verification AppX SHA-256:
  `93279f430e024deb3b28ee12d98271ffa19d7093f8d9e667e7c9defcace2fc10`
- Verification screenshots artifact: `8316137548`
- Final state-only Quality run: `29346492274`

Those runs prove current source/launch hardening remains valid. Artifact
8316167277 has different bytes and **must not replace** the accepted Partner
Center package because no product-runtime change required a new candidate.

Canonical remote branch is `main`. `feature/monetization` preserves accepted
candidate history; `feature/revenue-cycle-0` is diverged legacy history. Do not
continue release work on either branch or merge old projections back into main.

## 6. Partner Center draft truth

Private Partner Center state below was last observed 2026-07-14 and must be
reverified before any commercial action.

- Product: Hearth
- Product ID: `9PLRSZZMFPJH`
- Submission: `1152921505701225649` / Submission 1
- Product state: **In draft**
- Audience currently saved: Public, discoverable
- Market: United States only
- Price: $14.99 one-time; no trial or sale
- Categories: Productivity primary; Health + fitness secondary
- Package: only the accepted `Hearth 1.1.0.appx`, marked Validated
- Listing: complete copy, eight features, seven keywords and five exact
  1920×1080 fictional-data screenshots
- Properties: complete, including personal-information declaration
- Submission options: Partner Center displayed Incomplete although runFullTrust
  explanation and testing information were saved
- Saved release control: **Do not publish until I select Publish now**
- Certification: not submitted
- Public listing / checkout: not observed
- Earnings observed: $0.00
- Payout and tax navigation: not visible in the observed account context

Direct entry points:

- Product overview:
  `https://partner.microsoft.com/en-us/dashboard/products/9PLRSZZMFPJH/overview`
- Age ratings:
  `https://partner.microsoft.com/en-us/dashboard/products/9PLRSZZMFPJH/submissions/1152921505701225649/ageratings`
- Pricing/audience:
  `https://partner.microsoft.com/en-us/dashboard/products/9PLRSZZMFPJH/submissions/1152921505701225649/availability`
- Account settings:
  `https://partner.microsoft.com/dashboard/v2/account-settings/overview`
- Earnings:
  `https://partner.microsoft.com/dashboard/v2/earnings/earnings`

Never record account names, tester email addresses, banking, tax, KYC,
identity documents or support-contact details in the repository.

## 7. What is already shipped — do not redo

- Release-candidate architecture, encrypted persistence, migration, recovery,
  erase, export warnings, sender validation and automated lifecycle coverage
- Electron/toolchain/security upgrades and zero known high production
  dependency vulnerabilities at last verification
- Deterministically generated, rights-documented shipping art and vaulted
  unverified historic art
- MIT license and generated third-party notices
- Exact accepted AppX, screenshots and Partner Center package validation
- Truthful Store copy, price, category, declarations, testing notes and manual
  publication hold
- Privacy, terms, refunds, accessibility-status and support documents
- Privacy-guarded typed bug/feature forms with blank issues disabled
- Public support route and private GitHub vulnerability reporting
- Accurate GitHub description/topics
- Screenshot-backed, responsive commercial landing source
- Campaign IDs, product-page experiment plan and owner-reviewed launch drafts
- Secret scanner repaired for legitimate deleted working-tree paths

Public routes:

- Repository: `https://github.com/ntoledo319/Mindful-Organizer`
- Support: `https://github.com/ntoledo319/Mindful-Organizer/blob/main/docs/SUPPORT.md`
- Issue chooser: `https://github.com/ntoledo319/Mindful-Organizer/issues/new/choose`
- Security policy: `https://github.com/ntoledo319/Mindful-Organizer/security/policy`
- Private vulnerability report:
  `https://github.com/ntoledo319/Mindful-Organizer/security/advisories/new`

Creating an issue requires GitHub sign-in. Public issues must contain only
fictional/redacted reproduction data—never databases, snapshots, keys, exports,
journals, crisis plans, medication/check-in data, account information or
identifying screenshots.

## 8. Remaining blockers and exact human sequence

`revenue/HUMAN_QUEUE.md` is the sole detailed owner-action list. It totals **44
minutes**, leaving 16 minutes reserve. No owner time is recorded as spent.

### HQ-01 — Manual IARC retake — 5 minutes

The current saved IARC 3+ / ESRB Everyone result is not trusted against all
downloaded crisis/self-harm and medication-reference content. IARC terms forbid
automated scripts operating the rating tool and require complete answers plus a
real legal/majority-age attestation.

Factual source boundaries: references are text-only; there is no visual
violence, blood/gore, frightening audiovisual material, sexuality, gambling,
profanity, crude humor, alcohol/tobacco or illegal/recreational drug use. A
named prescription medication example is packaged. The owner must manually read
the current question definitions, answer for all
code/assets in the downloaded package (including vaulted routes), accept the
calculated result rather than targeting a preferred rating, and save only if
the legal statements are true. Treat the detailed path in HUMAN_QUEUE as a
source-grounded starting guide, not permission to ignore current IARC help
text. An agent must not click, type, save or accept this questionnaire.

After completion, record only date, resulting regional ratings and non-sensitive
notes in `revenue/METRICS.md`.

### HQ-02 — Seller/tax/payout readiness — 10 minutes

The owner must verify the real seller entity and appropriate Owner/Financial
contributor context, then create/validate and assign tax and payout profiles to
the correct Store seller/program. Payout readiness is required before public
release, not merely before expecting money. Microsoft says validation may take
up to 48 hours.

An agent must not guess or enter banking, tax, KYC, identity or role facts.
Record only ready/not-ready, date and a non-sensitive blocker.

### HQ-03 — Choose test route and perform Windows pass — 18 minutes

Before certification, the owner must choose whether to change the first
submission from Public to **Private audience** and provide the named Microsoft
tester account privately. Private audience is the strongest fully hidden
Store-signed test path, but it requires a later submission to move Public.

Do not imply a non-public Store install is guaranteed while this choice is open.
After certification, install the Microsoft-signed build through the chosen
supported route and complete `store/WINDOWS-VALIDATION.md` and
`docs/ACCESSIBILITY.md` using fictional data. Record Windows build, x64,
install route, pass/fail, footprint and date only.

### HQ-04 — Certification and separate publication — 6 minutes

This is blocked until IARC is corrected, payout readiness is settled, and the
test route is chosen. Before submission, verify the accepted package filename,
size/hash, listing URLs, $14.99 price, categories, screenshots, truthful IARC,
runFullTrust explanation, testing notes and manual publication hold.

The owner submits for certification. Preserve status, timestamp and any report.
Certification success must remain held. Complete the Store-signed Windows pass,
then use **Publish now** only after package, certification, payout, preview,
price, support and human Windows evidence all pass. Verify the final listing and
checkout in a signed-out browser.

### HQ-05 — First audience batch — 5 minutes

Only after the page is visibly purchasable may the owner approve and post the
smallest launch batch from `store/LAUNCH_KIT.md`. Every destination's current
rules must be read first. Disclose “I built Hearth.” Never cold-DM, scrape,
automate, impersonate a customer, manufacture engagement or promise outcomes.

## 9. Agent continuation playbook

### While waiting for owner gates

- Do not wait idly. Keep the draft, public policies, support surface and CI
  healthy.
- Reverify current Store/marketplace policies before making a platform change.
- Do not build Bet B merely to avoid the certification task; start it only when
  the active plan/falsifier or a recorded blocker justifies the pivot.
- A docs-only or analysis cycle still needs a visible shipment and all six state
  files updated.

### When HQ-01 and HQ-02 are complete

1. Read all six state files again.
2. Verify only the accepted package remains in Partner Center and is Validated.
3. Verify the manual hold still reads **Do not publish until I select Publish
   now**.
4. Verify policy/support/privacy/terms/refund URLs signed out.
5. Record the IARC outcome and payout-ready boolean without private details.
6. Confirm the Private/Public test choice.
7. Have the owner submit for certification; record submission time/status.

### During certification

- Microsoft review time is machine wait, not owner minutes.
- Monitor without changing the package or claims.
- On failure: preserve and redact the report, log it in METRICS/DECISIONS, fix
  the narrow real cause, and create a completely new candidate/evidence chain
  if runtime/package bytes change. Never weaken a truthful disclosure to pass.
- On success: do not release the hold yet.

### After certification, before publication

1. Obtain the supported Store-signed install selected in HQ-03.
2. Run the smoke matrix: first render, consent accept/decline, 4–24 capacity
   persistence, task, check-in, practice, crisis-plan edit, JSON/PDF export,
   plaintext warnings, erase, full quit/relaunch and identity/footprint checks.
3. Run keyboard-only, Narrator, focus, high contrast/forced colors, 200% text
   scaling, minimum window, reduced motion, light/dark and modal-focus checks.
4. Do not make formal accessibility claims until this passes.
5. Confirm payout readiness and signed-out page preview.
6. Have the owner click **Publish now**.

### Immediately after publication

1. Verify the exact public page and paid checkout signed out. Expected pattern:
   `https://apps.microsoft.com/detail/9PLRSZZMFPJH`; do not distribute it before
   observation.
2. Record the observed Store URL, price, timestamp, package/version and status
   in METRICS.
3. Update `store/listing-metadata.json`: live release state and `storeListing`.
4. Update README, SUPPORT, TERMS, store docs and landing copy from pre-release to
   only what is observed.
5. Wire source-specific campaign links from `store/CAMPAIGNS.md`.
6. Deploy `landing/` only to a current-TOS-compatible $0 static host. Do not use
   GitHub Pages as a commercial checkout/landing host.
7. Run full verification, publish the doc/link changes and record evidence.
8. Have the owner execute HQ-05. No agent posts or contacts humans.

## 10. Audience and decision gates

Current funnel:

`Microsoft Store discovery or owner-approved campaign link → Store product page
→ checkout → install → first run → retained use → retained proceeds`

The landing source, campaign IDs and launch copy reduce friction but are not an
audience. Store discovery is the only autonomous acquisition source currently
available.

After the listing is genuinely live:

- No external signal after 5 live days: allow one repositioning (price,
  positioning or channel), recorded in DECISIONS.
- Still zero after 4 more live days: replace Bet A with the next-ranked viable
  opportunity.
- 100 observed product-page views with zero purchases: treat as an immediate
  conversion failure.
- No impressions: examine category, keywords, market and eligibility.
- Impressions but no views: change first visual/short description.
- Views but no acquisitions: test one value/price/page asset at a time.
- Acquisitions but weak install/use: investigate package and first run.
- Usage but weak return: improve the first completed planning loop before adding
  acquisition channels.

Evidence hierarchy is dollars > signups > visits > stars. Acquisitions are not
collected profit. Recompute `$4,000 - collected profit` at every gate.

## 11. Verification commands

All targets and generated output must remain inside the workspace. Use the
locked project dependencies; never install globally.

```bash
npm ci
npm run store:check          # must print true
npm run secrets
npm run store:validate       # last observed: 263 checks
npm run brand-assets
npm run licenses
npm audit --omit=dev --audit-level=high
npm run lint
npm run typecheck
npm test                     # last observed: 9 files / 30 tests
npm run vite:build
git diff --check
```

After deterministic generators, inspect the diff. Shipping brand assets should
not change without an intentional provenance-reviewed change.

For a genuine new Store candidate, use `.github/workflows/windows-store.yml` on
the exact commit. It performs locked install, secrets/listing/identity checks,
asset/license/audit gates, lint/typecheck/tests, Windows native rebuild,
screenshots, AppX validation, real Windows DPAPI lifecycle proof and artifact
upload. A green build is not certification or an installed accessibility pass.

`.github/workflows/tests.yml` is the normal Quality Gate. Do not create a `v*`
tag or trigger `.github/workflows/release.yml` merely to test; tags create
cross-platform release artifacts. Do not point `.github/workflows/pages.yml` at
the commercial landing source.

Landing preview, if needed:

```bash
npm run landing:media
python3 -m http.server 4173 --directory landing
```

Use only matching screenshot evidence and stop the server you start.

## 12. Claims and safety guardrails

Allowed claims must be paired with exact boundaries: local-first, no account,
no cloud API, no ads, no record sync, no app telemetry, authenticated encrypted
snapshots at rest, user-controlled capacity, conservative local rules and
plaintext user-requested exports.

Forbidden without new evidence: AI-powered diagnosis, therapeutic, clinical,
medical-device, crisis detection/prevention, secure/anonymous by guarantee,
zero data collection, best/first/revolutionary, guaranteed outcomes, fabricated
users/reviews/revenue, or formal accessibility conformance.

Never:

- automate IARC or accept legal/identity attestations as the owner;
- enter or commit private tax, bank, KYC, tester or account data;
- replace the accepted AppX with artifact 8316167277;
- locally sign the accepted package and call it exact-hash evidence;
- claim WACK, certification, installed behavior, accessibility or revenue that
  was not observed;
- publish merely to manufacture a test route;
- deploy a commercial landing page to GitHub Pages;
- add analytics, a waitlist or cloud intake just to simulate audience;
- contact, email, DM, post, solicit reviews or commit to customers autonomously;
- remove vaulted capabilities or historic assets in a cleanup pass;
- expose secrets, personal records, exports, snapshots or keys.

## 13. State-file close protocol

At the end of every cycle, update all six files even if only a short current
truth line changes:

- `ASSETS.md`: product/capability/completeness/provenance truth
- `OPPORTUNITIES.md`: ranking, fee/distribution evidence and falsifiers
- `PLAN.md`: root on line 1, active bets, next action and current dollar gap
- `METRICS.md`: timestamped observed evidence only
- `HUMAN_QUEUE.md`: exact human-only steps, direct links and total minutes
- `DECISIONS.md`: pivots, superseded assumptions and why

Update this handoff whenever the accepted candidate, Partner Center status,
critical path, money state, testing route or public URL changes. Do not create a
second competing handoff.

## 14. Definition of mission completion

Technical release is not mission completion. The active bet becomes shipped
only when there is a live URL, payment rail, submitted/certified listing,
analytics/evidence route, honest public page, real price and METRICS entry.

The mission completes only when cumulative collected profit reaches $4,000 or
the Day-28 process ends with every gate/pivot honestly recorded. A live Store
page, downloads, impressions, acquisitions, CI artifacts or potential revenue
do not equal collected cash.

## 15. Handoff-generation environment note

During creation on 2026-07-15, every local shell subprocess—including `pwd` and
`true`—was immediately killed with exit 137. No command was redirected outside
the jail. Current files were audited through the authenticated GitHub connector
against remote main, and specialist audits used the same read-only fallback.

The next agent must first retry the startup/status/verification commands. If the
local checkout contains handoff/state changes that match newer `origin/main`,
reconcile them without destructive reset and preserve any unrelated user work.
Remove this environment note only after recording a successful local-shell and
worktree verification in `revenue/METRICS.md`.
