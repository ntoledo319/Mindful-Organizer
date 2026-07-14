# Decision Ledger

## 2026-07-14 — Cycle 0

### D001 — Enforce the workspace jail before all work

Resolved root:
`/Users/nicholastoledo/Development/active/mindful_organizer`. Local work remained
inside it; external skill/memory files were not read because §1 forbids even
read-only access outside the root.

### D002 — Retire the clinic/fleet-key monetization branch

The $249 path used Stripe test mode, accepted any `PRO-` prefix, had no
fulfillment, and showed a spinner instead of a report. Clinical and guaranteed
revenue claims were unsupported. Decision: remove the gate and make a truthful
personal PDF summary available to every user.

### D003 — Remove browser speech input

Web Speech implementations may use a remote speech service, contradicting the
local-only journal promise. Decision: keep typed local journaling; do not add a
new dependency or weaker privacy exception.

### D004 — Select Microsoft Store as Bet A

The repo has a real reserved product identity, Store discovery and checkout are
built in, account creation has no registration fee, and the documented app fee
is 15%. This is shorter and more constrained than inventing an audience or
payment stack. Price is a $14.99 hypothesis, not a live claim.

### D005 — Block Store release on cryptography, provenance, and support

Microsoft policy 10.5.4 requires modern cryptography when personal information
is stored. Hearth's SQLite database is not application-level encrypted. Brand
asset rights are undocumented and GitHub Issues is disabled. Decision: no
submission or binary-release claim until these gates are closed.

### D006 — Keep paid Store work manual

The previous `msstore submission updateMetadata` command failed in production,
and the workflow downloaded an unpinned latest CLI. Decision: remove the
publisher entirely. Keep a package-build workflow for review, and queue paid
metadata, upload, and submission in Partner Center.

### D007 — Reject GitHub Pages for commercial hosting

GitHub's additional Pages terms prohibit using Pages primarily for online
business/e-commerce/SaaS. Decision: do not deploy a commercial Hearth landing
page there. GitHub may still host the MIT source and project documentation.

### D008 — Select itch.io kit as conditional Bet B

itch.io supplies hosting, discovery, checkout, and zero-upfront page creation.
Its default 10% share, typical 2.9% + $0.30 processing, one-time $3 tax-identity
adjustment, and payout delay are explicitly modeled. The bet proceeds only for
a genuinely new production kit—not a paid copy of public MIT files.

### D009 — Upgrade security/toolchain before distribution

Electron 33 was outside the supported stable window and IPC handlers did not
validate senders. Decision: upgrade to Electron 43, Node 22.12 CI, validate the
top-level renderer origin, include licenses, and remove known vulnerable build
tool versions rather than publishing with known avoidable exposure.

### D010 — Publish reviewable work, not an unready product

The cycle's external shipment will be a public source/documentation branch. It
is honest evidence of progress without representing the app as certified,
purchasable, or safe for Store release. No PR, outreach, post, or commitment is
authorized.

### D011 — Treat the local native-package failure as evidence

`npm run build:dir` reached Electron 43's native `better-sqlite3` rebuild and
failed because the contained Apple Clang 14 / SDK 13.3 toolchain has no C++20
`<source_location>`. Upgrading system tooling would leave the jail. Decision:
record the failure, preserve the supported Electron/runtime upgrades, and use a
hosted current Windows runner for the next package proof.

### D012 — Ship a public review branch without opening a PR

Published `feature/revenue-cycle-0` at
<https://github.com/ntoledo319/Mindful-Organizer/tree/feature/revenue-cycle-0>.
Quality Gate #41 passed. A branch and CI evidence satisfy the external-change
law while avoiding an unauthorized PR/post and avoiding a false product-release
claim.

### D013 — Classify the successful MSIX as a review artifact

Hosted Windows Store Build #9 generated and uploaded `hearth-msix` successfully
from commit `6fb4d88`, with the digest recorded in `METRICS.md`. Decision: count
this as package-build evidence only. Do not call it released, distribute it to
customers, or submit it until exact-artifact install smoke, encryption,
provenance, support, screenshots, certification preparation, and the owner-only
Partner Center gates are complete.

## 2026-07-14 — Cycle 1

### D014 — Replace plaintext persistence with authenticated protected snapshots

The earlier Store policy blocker is resolved in the release candidate. SQLite
now operates in memory, and versioned snapshots use AES-256-GCM with fresh IVs
and a random 256-bit key protected by Windows DPAPI through Electron
safeStorage. Primary/backup recovery, legacy migration, missing-key failure,
export disclosure, and key-first erase behavior are verified by Windows CI.
Decision: retain explicit limitations in every privacy and listing claim; do not
call local encryption an absolute security guarantee.

### D015 — Make capacity explicitly user-controlled

Capacity is a 4–24 value chosen by the user. Hearth never infers or changes it
from diagnosis labels, mood, sleep, anxiety, or check-ins. Today recommends only
open tasks whose exact recorded cost fits the remaining budget. Decision:
remove all copy and behavior suggesting adaptive diagnosis-driven capacity.

### D016 — Narrow the launch without destroying capabilities

Today, Tasks, Check in, Practices, Rhythm, Crisis, and Settings are the launch
surface. Diary cards, ERP notes, medication reference, and legacy condition
metadata are preserved in schema, types, IPC/repository code, renderers, and
exports but removed from default collection/navigation. Earlier undocumented
art is preserved under resources/vault/unverified-2026-07-14/ and excluded from
shipping. docs/CAPABILITY_VAULT.md is the restoration contract. No permanent
deletion is authorized without a separately reviewed migration.

### D017 — Treat premium usability and accessibility as release behavior

Decision: replace the inconsistent prototype surface with one warm editorial
system, coherent hierarchy, purposeful states, deterministic art, modal focus
traps/restoration, reduced-motion handling, accessible chart descriptions, and
tested contrast tokens. Do not make a Store accessibility declaration until the
installed Windows/Narrator/high-contrast/text-scaling matrix is complete.

### D018 — Accept one exact 1.1.0 candidate

Candidate 8172603b62c2457696608c145511bd3fe92429d4 passed the hosted Quality and
Windows Store workflows. Its AppX SHA-256 is
4900f3823febace53f86f69ee2567b50208aec8f6677741c3c4dcf3667facdb1.
Five exact-candidate screenshots were hash-recorded and visually inspected.
Decision: no changed package or screenshot may inherit this evidence; any
candidate change restarts the affected gates.

### D019 — Configure the Partner Center draft completely but hold publication

The exact AppX, $14.99 US one-time price, public/discoverable audience, truthful
copy, categories, properties, five screenshots, runFullTrust explanation, and
testing notes are saved in Submission 1. The old 1.0.0 package was removed from
the draft; its source and removed capabilities remain preserved in the
workspace. Decision: set release control to Do not publish until I select
Publish now so certification cannot silently make the product public.

### D020 — Do not guess the IARC legal classification

The existing Partner Center result is IARC 3+ / ESRB Everyone. The packaged
source includes crisis language and a vaulted self-harm urge field. An
exploratory questionnaire edit was canceled without saving. Decision: require
the owner to review and affirm every answer before certification, including
whether those references change the violence-content answer.

### D021 — Hold certification on installed-Windows and owner gates

Partner Center enables Submit for certification, but button availability is not
release readiness. Decision: do not click it until the exact installed AppX,
WACK, manual accessibility, IARC, payout/account-role, and support checks are
complete. The saved runFullTrust request must be reviewed during certification;
Hearth uses no service, driver, elevation, system-policy change, background
monitoring, account, cloud sync, ads, or telemetry.

### D022 — Keep distribution claims evidence-based

There is no owned audience, live Store page, page-view count, acquisition, sale,
or payout. Decision: use Store discovery as the only autonomous channel and
keep all prepared launch posts in store/LAUNCH_KIT.md until the owner approves
and manually sends them after publication. No autonomous email, DM, post,
review solicitation, or customer promise is authorized.

### D023 — Keep the $14.99 model, not a revenue promise

The saved one-time price is a market test. At the documented 15% non-game app
fee, 314 sales would model $4,000.83 before refunds and tax adjustments. No
demand evidence supports that quantity yet. Decision: start the five-day signal
gate only after the listing is actually visible and purchasable, then reposition
once and replace promptly if external signal remains zero.
