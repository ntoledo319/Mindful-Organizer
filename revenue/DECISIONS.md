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
