# Hearth Mission Handoff

Canonical zero-context continuation document. Last reconciled 2026-07-15
(America/New_York) against public GitHub main at
4a32b7306ab9ca76a09fb3fae399649c07543e5a. Private Partner Center facts were
last observed 2026-07-14 and must be reverified before commercial action.

This file is self-contained. It tells a new agent what is proven, what must not
be redone, what remains, and how to finish the revenue mission without outside
memory.

## 1. Start here and obey the jail

AGENTS.md outranks this document.

1. Start inside /Users/nicholastoledo/Development/active/mindful_organizer.
2. Resolve pwd -P and AGENTS.md. Stop if either is outside that root.
3. Confirm line 1 of revenue/PLAN.md is the same absolute root.
4. Read AGENTS.md completely.
5. Read all six state files before acting:
   revenue/ASSETS.md, revenue/OPPORTUNITIES.md, revenue/PLAN.md,
   revenue/METRICS.md, revenue/HUMAN_QUEUE.md, and revenue/DECISIONS.md.
6. Read this file, then store/README.md and store/WINDOWS-VALIDATION.md.
7. Check git status, origin/main and recent CI without discarding user work.
8. Every cycle ends with an externally visible shipment and updates to all six
   revenue files.

Do not read local skills, memory, repositories, home files, /tmp or anything
outside WORKSPACE_ROOT. Never install globally or alter global machine state.

Authority when documents disagree:

1. AGENTS.md
2. Newly observed evidence recorded in revenue/METRICS.md
3. The six revenue files as a set
4. This handoff
5. Store release documents
6. README and older strategy/history documents

Choose the conservative truth, reverify it, record it, and synchronize docs.

## 2. Mission and money

- Mission: $4,000 cumulative collected profit from strangers by Day 28.
- Constraints: $0 spend, at most 60 total owner minutes, no autonomous contact.
- Cycle 0 / Day 1 was 2026-07-14. If unchanged: Day 7 July 20, Day 14 July 27,
  Day 21 August 3, Day 28 August 10.
- Collected profit observed: $0.00.
- Gap: $4,000.00.
- Live paid listings: zero.
- No Store views, acquisitions, installs, purchases, refunds, fees or payouts
  are observed.

Fast bet: Hearth 1.1.0 at $14.99 one-time in the US Microsoft Store. At the
documented 15 percent app fee, planning net is $12.7415 each; 314 retained sales
model $4,000.83 before refunds/tax. This is arithmetic, not demand evidence.

Conditional heavy bet: a genuinely new $249 Hearth-to-Production Electron kit.
It is not built or shipped. First reserve: standalone Focus Guard Store utility.

## 3. Product truth

Hearth is an Electron 43, React 18, TypeScript and Vite Windows energy planner
for ADHD and other variable-capacity days. The user chooses a 4-24 daily energy
budget, costs tasks by duration/energy, sees up to three fitting open tasks, and
may use local check-ins, trends, guided practices, focus controls, a user-written
crisis plan, and requested JSON/PDF exports.

It is personal organization and reflection software, not a medical device,
diagnosis, treatment, clinical monitor, healthcare service, emergency service
or crisis detector.

Repository map:

- electron/: main process, SQLite, encryption, migrations, IPC, PDF, validation
- src/shared/: typed contracts, models, spoon-cost and summary logic
- src/renderer/: React shell, routes, screens, state and styles
- src/renderer/capabilities.ts: visible/vaulted route registry
- resources/: deterministic shipping art, provenance and asset vault
- scripts/: validation, screenshots, assets, notices and secret scan
- store/: Store metadata, screenshots, campaigns, launch and Windows validation
- landing/: scriptless/trackerless pre-release landing source; not deployed
- docs/: legal, privacy, accessibility, support and architecture
- revenue/: durable mission state and evidence

Data protection: SQLite runs in memory. At rest Hearth uses versioned,
authenticated AES-256-GCM snapshots with fresh IVs and a random 256-bit key
protected through Electron safeStorage / Windows DPAPI. It fails closed when
protected storage is unavailable. CI covers persistence, recovery, missing-key
failure, migration, export warnings, key-first erase and interrupted erase.

Every security claim must also state the limits: data/key exist in process
memory while open; Windows can copy memory into swap/hibernation/crash storage;
a controller of the signed-in OS session may reach the credential facility;
requested exports are plaintext; deletion cannot guarantee SSD/snapshot/backup
erasure; the developer cannot recover a lost key.

## 4. Capability vault - do not delete

docs/CAPABILITY_VAULT.md is the restoration contract. Preserved outside default
navigation:

- Diary cards including a self-harm urge field
- ERP-session notes
- Medication-reference tables/screen
- Legacy condition-label metadata
- Historic unverified art under resources/vault/unverified-2026-07-14/

Schemas, types, repository/IPC methods, renderers and export compatibility are
intentionally retained. Permanent removal requires a reviewed migration, export
compatibility decision, vault update and new candidate.

## 5. Accepted Store candidate - immutable

Do not replace, rebuild, sign, rename or confuse this package with later CI:

| Field | Accepted value |
|---|---|
| Source | 8172603b62c2457696608c145511bd3fe92429d4 |
| Application tree | d731d4de78529435c5cc1e0a036536701cc737e9 |
| Package | Hearth 1.1.0.appx |
| Size | 175,488,515 bytes |
| Inner AppX SHA-256 | 4900f3823febace53f86f69ee2567b50208aec8f6677741c3c4dcf3667facdb1 |
| Package artifact ID | 8306541856, recorded expiry 2026-08-13 |
| Artifact ZIP digest | sha256:4d5885c705cf6429e83ef3404135d6448ffdb903b0df8cd75e5fbf02d7d8a494 |
| Screenshot artifact ID | 8306519500 |
| Screenshot ZIP digest | sha256:b03e6e42b771da7f693575d79473275e90723adbeea23801d08f8de380e7c905 |
| Quality run | 29322423682 |
| Windows run | 29322423622 |
| Recorded jailed copy | tmp/artifacts/final-msix/Hearth 1.1.0.appx |

The ZIP digest and inner AppX hash are different evidence. The AppX is
intentionally unsigned. Signing changes bytes. GitHub-hosted Windows cannot
provide authoritative full WACK for this exact unsigned package. Microsoft
certification is the exact submission install/run/security/technical/content
gate. Store-signed human Windows/accessibility testing remains required.

Later verification, not the submission package:

- Launch hardening commit d01c013fd8beec91014c37d27a9a310cf5dd0470
- State close commit 4a32b7306ab9ca76a09fb3fae399649c07543e5a
- Quality 29345864617; Windows 29345863949
- Artifact 8316167277, AppX SHA
  93279f430e024deb3b28ee12d98271ffa19d7093f8d9e667e7c9defcace2fc10
- Screenshot artifact 8316137548
- State-only Quality 29346492274

Artifact 8316167277 must never replace the Partner Center package.

Canonical branch is main. feature/monetization preserves candidate history.
feature/revenue-cycle-0 is diverged legacy. Do not resume release work there.

## 6. Partner Center, last observed 2026-07-14

- Product Hearth, ID 9PLRSZZMFPJH
- Submission 1152921505701225649 / Submission 1
- State: In draft
- Audience saved: Public and discoverable
- Market: United States only
- Price: $14.99 one-time; no trial/sale
- Productivity primary; Health + fitness secondary
- Only accepted Hearth 1.1.0.appx present and Validated
- Listing copy, eight features, seven keywords, five exact screenshots complete
- Properties complete
- Submission options displayed Incomplete although runFullTrust/testing notes
  were saved
- Release control: Do not publish until I select Publish now
- Not submitted, certified, published or purchasable
- Earnings observed $0.00
- Payout and tax navigation not visible in observed account context

Entry points:

- Product:
  https://partner.microsoft.com/en-us/dashboard/products/9PLRSZZMFPJH/overview
- IARC:
  https://partner.microsoft.com/en-us/dashboard/products/9PLRSZZMFPJH/submissions/1152921505701225649/ageratings
- Audience:
  https://partner.microsoft.com/en-us/dashboard/products/9PLRSZZMFPJH/submissions/1152921505701225649/availability
- Account:
  https://partner.microsoft.com/dashboard/v2/account-settings/overview
- Earnings:
  https://partner.microsoft.com/dashboard/v2/earnings/earnings

Never record account names, tester emails, bank, tax, KYC or identity data.

## 7. Already shipped - do not redo

- Encryption/migration/recovery/erase/export and sender-validation architecture
- Exact accepted AppX/screenshots and Partner validation
- Deterministic rights-documented art; unverified art vaulted
- MIT license and third-party notices
- Store copy, price, category, declarations, notes and manual hold
- Privacy, terms, refunds, accessibility status and support documents
- Guarded typed issue forms; blank issues disabled
- Public support and private vulnerability reporting
- Accurate GitHub description/topics
- Screenshot-backed responsive landing source
- Campaign IDs, experiment plan and owner-reviewed launch drafts
- Deletion-safe secret scanner and green quality/package CI

Public support:
https://github.com/ntoledo319/Mindful-Organizer/blob/main/docs/SUPPORT.md

Issue chooser:
https://github.com/ntoledo319/Mindful-Organizer/issues/new/choose

Security:
https://github.com/ntoledo319/Mindful-Organizer/security/policy

Private vulnerability reporting:
https://github.com/ntoledo319/Mindful-Organizer/security/advisories/new

Public issues require sign-in and fictional/redacted data only. Never solicit
databases, snapshots, keys, exports, journals, crisis/medication/check-in data,
account information or identifying screenshots.

## 8. Remaining Human Queue - 44 minutes

revenue/HUMAN_QUEUE.md is the sole detailed owner list. Sixteen minutes remain.

1. Manual IARC retake - 5 minutes.
   Existing 3+ / ESRB Everyone is untrusted. IARC forbids automation and requires
   real legal/age attestations. Text-only crisis/self-harm references and a named
   prescription example exist in the downloaded package; no visual violence,
   gore, frightening audiovisual content, sexuality, gambling, profanity,
   crude humor, alcohol/tobacco or illegal/recreational drug use exists.
   The owner must read exact current question/help wording, answer for all
   packaged code/assets including vaulted routes, and accept the calculated
   rating. Agents must not operate or accept IARC.

2. Seller/tax/payout - 10 minutes.
   Owner verifies entity/role and validates/assigns tax and payout profiles to
   the Store seller/program. Payout readiness is required before publication.
   Agents never enter or record private facts.

3. Test-route choice and Windows pass - 18 minutes.
   Before certification, owner decides Public versus Private audience. Private
   is the strongest hidden Store-signed test but needs a named tester and later
   public submission. After certification, use the supported Store-signed route
   and complete store/WINDOWS-VALIDATION.md and docs/ACCESSIBILITY.md with
   fictional data.

4. Certification and separate publication - 6 minutes.
   Blocked until IARC, payout and route choice. Reverify immutable package,
   listing URLs, price, categories, screenshots, IARC, runFullTrust notes and
   hold. Owner submits. Preserve result. Keep hold until signed Windows pass,
   payout, preview, support and price all pass. Owner clicks Publish now, then
   verify listing and checkout signed out.

5. Audience batch - 5 minutes.
   Only after paid checkout is visibly live may owner approve/post the smallest
   store/LAUNCH_KIT.md batch. Read each destination's current rules, disclose
   maker status, never cold-DM/scrape/automate/manufacture engagement.

## 9. Completion runbook

When IARC/payout are done:

1. Read all six state files again.
2. Verify accepted package only and Partner Validated state.
3. Verify the manual publication hold.
4. Verify support/privacy/terms/refunds signed out.
5. Record IARC result and payout-ready boolean without private detail.
6. Confirm Private/Public route.
7. Owner submits; record time/status.

During certification:

- Monitor; do not change package or claims.
- On failure: preserve/redact report, log METRICS/DECISIONS, fix the narrow cause.
  Runtime/package changes require a new candidate, hash and complete evidence.
- On success: do not release the hold.

Before publication:

- Install via selected Store-signed route.
- Smoke: render, consent accept/decline, capacity persistence, task, check-in,
  practice, crisis-plan edit, JSON/PDF export/warnings, erase, quit/relaunch,
  package identity and footprint.
- Accessibility: keyboard, Narrator, focus, high contrast, 200 percent scaling,
  minimum window, reduced motion, themes and modal focus.
- No formal accessibility claims until pass.
- Confirm payout and signed-out preview.
- Owner clicks Publish now.

Immediately after publication:

1. Verify page and paid checkout signed out. Expected pattern:
   https://apps.microsoft.com/detail/9PLRSZZMFPJH
2. Record URL, price, timestamp, version/package and status.
3. Update store/listing-metadata.json release state and storeListing.
4. Update README, SUPPORT, TERMS, store docs and landing from pre-release using
   observed claims only.
5. Wire campaign links from store/CAMPAIGNS.md.
6. Deploy landing only to a current-TOS-compatible $0 host. Never commercial
   GitHub Pages.
7. Verify/publish changes and update all six revenue files.
8. Owner executes the approved launch batch.

## 10. Audience gates

Funnel: Store discovery or approved link -> product page -> checkout -> install
-> first use -> retained use -> retained proceeds.

- Five live days with zero external signal: one recorded reposition.
- Four more zero-signal days: replace Bet A.
- 100 page views with zero purchases: immediate conversion failure.
- No impressions: category/keywords/market.
- Impressions/no views: first visual/short description.
- Views/no acquisitions: one price/value/page test.
- Acquisitions/weak use: package/first-run investigation.
- Usage/weak return: improve the first planning loop.

Dollars outrank signups, visits and stars. Acquisitions are not collected cash.

## 11. Verification

Inside the jail, with project-local dependencies:

    npm ci
    npm run store:check
    npm run secrets
    npm run store:validate
    npm run brand-assets
    npm run licenses
    npm audit --omit=dev --audit-level=high
    npm run lint
    npm run typecheck
    npm test
    npm run vite:build
    git diff --check

store:check must print true. Last Store validation: 263 checks. Last tests:
9 files / 30 tests.

A genuine new candidate uses .github/workflows/windows-store.yml. Green CI does
not prove Store installation, WACK, certification, signing or human
accessibility. .github/workflows/tests.yml is normal Quality Gate. Do not create
a v* tag or trigger release.yml merely to test. Do not use pages.yml for the
commercial landing.

Landing preview:

    npm run landing:media
    python3 -m http.server 4173 --directory landing

Stop the server you start.

## 12. Never do these

- Automate IARC or accept owner legal/identity attestations
- Enter/commit private tax, bank, KYC, tester or account data
- Replace accepted AppX with artifact 8316167277
- Sign the accepted package and call it exact-hash evidence
- Claim WACK, certification, install, accessibility or revenue unobserved
- Publish just to manufacture a test route
- Use GitHub Pages as commercial landing/checkout
- Add analytics/waitlist/cloud intake to simulate audience
- Contact/email/DM/post/solicit reviews autonomously
- Remove vaulted capabilities/assets in cleanup
- Expose secrets or personal records
- Use clinical, therapeutic, crisis-prevention, guaranteed privacy/outcome,
  fabricated user/review/revenue, or formal accessibility claims

## 13. End every cycle

Update all six revenue files:

- ASSETS: product/capability/completeness/provenance
- OPPORTUNITIES: ranking, fees/distribution and falsifiers
- PLAN: root line 1, bets, next action and dollar gap
- METRICS: observed evidence only
- HUMAN_QUEUE: human-only steps, links and total minutes
- DECISIONS: pivots/superseded assumptions and why

Update this handoff whenever candidate, Partner state, critical path, testing
route, public URL or money changes. Do not create another competing handoff.

## 14. Completion definition

A technical release is not the mission. The bet is shipped only with live URL,
payment rail, certified/listed product, analytics/evidence route, honest page,
real price and METRICS entry.

Mission completion requires $4,000 cumulative collected profit, or an honest
Day-28 close with all gates/pivots recorded. A listing, downloads, acquisitions,
CI artifacts or potential revenue are not collected cash.

## 15. Environment note

During handoff creation every local shell subprocess, including pwd and true,
was killed with exit 137. Current files were audited through the authenticated
GitHub connector and three read-only specialist audits. Local branch/worktree
cleanliness, sync and jailed artifact presence are therefore unverified.

The next agent must retry status and verification first, preserve unrelated user
work, reconcile any handoff/state files with newer origin/main without
destructive reset, and remove this note only after recording a successful local
shell/worktree verification in revenue/METRICS.md.
