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

## 2026-07-14 — Cycle 2

### D024 — Stop automating the IARC rating tool

The packaged source audit found textual crisis/self-harm references and a
vaulted medication-reference screen that the saved 3+/Everyone questionnaire
did not disclose. During review, IARC's current Terms were found to prohibit
automated scripts from accessing or operating the rating tool. Decision: treat
any automated preview as invalid, do not save it, stop all agent interaction
with the questionnaire, and give the owner a manual, source-grounded answer
guide. The real publisher must read the definitions, accept the legal terms,
and attest majority age only if true.

### D025 — Make support public without soliciting private wellness data

GitHub Issues is enabled for all signed-in users and no interaction limit is
active, but the legacy templates asked for diagnoses, energy level, mental
health profile, screenshots, and nonexistent labels. Decision: replace them
with typed Windows/Hearth forms that require fictional reproduction data,
prohibit records/exports/keys/account details, disable blank issues, and route
urgent crisis needs away from software support. Use the public SUPPORT page as
the Store support URL because reading it does not require sign-in; disclose that
filing an issue does.

### D026 — Treat Microsoft certification as the exact unsigned-package gate

The accepted AppX has no `AppxSignature.p7x`. Microsoft's Store path accepts an
unsigned submission and re-signs it after certification. Local test signing or
rebuilding changes the package bytes and SHA-256, while hosted Windows runners
do not provide the active privileged desktop needed for authoritative WACK.
Decision: supersede D021's pre-certification exact-install/WACK requirement.
Microsoft certification is the exact-package install/run, security, and
technical-compliance gate. A Store-signed human smoke/accessibility pass remains
required before a quality claim or accessibility declaration.

### D027 — Preserve the manual hold and expose the testing tradeoff

The current submission is Public/discoverable but held after certification.
Microsoft's strongest first-release non-public install path is Private audience,
which requires a named tester Microsoft account and a later public submission.
Decision: do not silently change visibility or store a private tester address.
Put the choice in the Human Queue before certification. Never publish merely to
manufacture an install path.

### D028 — Use exact-candidate frames as conversion proof

The pre-release landing page was polished but relied on a concept illustration
and stale “package planned” wording. Decision: keep the illustration as an
explicit concept, add three SHA-verified frames from the accepted screenshot
manifest, and label them as fictional demo data from the exact candidate. Keep
the page static, scriptless, trackerless, form-free, and without a purchase link
until the Store page is observed live.

### D029 — Narrow payout readiness to the account-role boundary

The signed-in account can access Apps and games, Insights, and Earnings; the
Earnings workspace shows $0.00. Account settings still does not expose Payout
and tax. Microsoft documents Owner or Financial contributor context plus tax,
payout, and program assignment as prerequisites. Decision: no agent guesses or
enters private account, tax, bank, KYC, or role data. Queue the exact account
repair and start it early because validation can take up to 48 hours.

### D030 — Keep the local secret gate deletion-safe

Replacing legacy issue templates exposed that the secret scanner crashes on a
tracked path deleted in the working tree. Decision: skip only paths that no
longer exist, retain containment and symlink/size/binary checks for everything
else, and count readable files actually scanned. The repaired gate passed 160
files in the same deletion state that triggered the defect.

### D031 — Do not confuse launch assets with audience

The support route, screenshot-backed landing artifact, campaign IDs, and launch
copy are ready. None is a traffic source while the Store page is absent.
Decision: keep Microsoft Store discovery as the only autonomous acquisition
channel, preserve the five-day signal gate, and leave every post or human
contact in the owner-approved launch batch. Collected revenue remains the only
success metric.

### D032 — Publish the launch surface but keep the accepted package stable

The launch-hardening commit changed support, issue intake, landing presentation,
release documentation, and validation tooling but not Hearth runtime code. It
is live on GitHub main, both remote workflows passed, private vulnerability
reporting is enabled, and the public support/security pages resolve. The fresh
CI package has different bytes from the AppX already validated in Partner
Center. Decision: record the later artifact as independent verification
evidence, not as a replacement submission. Preserve the exact accepted AppX
and hash through certification unless product runtime code or Store package
requirements actually change.

## 2026-07-15 — Cycle 3

### D033 — Establish one canonical zero-context handoff

The existing strategy handoff was accurate but too brief to reproduce the mission, evidence chain, legal gates, release sequence, audience loop and capability-preservation rules without prior memory. Decision: make root HANDOFF.md the canonical handoff and require it to change whenever the candidate, critical path, public URL, testing route or money state changes.

### D034 — Preserve evidence boundaries during the shell failure

Every local subprocess on 2026-07-15, including pwd and true, was killed with exit 137. Decision: do not call the local worktree clean, synced or verified. Audit public main through the authenticated GitHub connector, label Partner Center state with its 2026-07-14 observation date, publish the handoff remotely, and require the next agent to rerun local status and verification without destructive reset.

## 2026-07-28 — Day-15 market-readiness remediation

### D035 — Execute the missed Day 7/14 §8 gates late, and escalate

No Day 7 (2026-07-20) or Day 14 (2026-07-27) gate assessment was ever
recorded, and the 44-minute owner queue sat untouched from 2026-07-15 through
today. Decision: execute both gates now as one Day-15 assessment
(`revenue/METRICS.md`, 2026-07-28). Conclusion: with 13 days left, a live
window of only ~4–11 days (certification 1–7 days after queue completion),
and 322–335 required sales at ~29–84 per live day with zero audience and $0
spend, the $4,000 collected-cash target is not reachable in-window through
Bet A — and ADA §6(c) monthly payout timing means even perfect sales would be
accrued, not collected, by Day 28. §8 escalation applied: ship all
agent-doable distribution prep today (D037, D039), put Bet B sequencing to
the owner as an explicit choice (D038), and restate the Day-28 success
criterion as live listing + first collected dollars + real demand signal
(`revenue/PLAN.md`). The Day-21 gate (2026-08-03) executes on schedule.

### D036 — Restate the money model: accrued vs collected, blended fees, Bet B tax fee cited

Three corrections to the money model, all applied in `revenue/PLAN.md`.
(1) **Accrued vs collected.** ADA v8.11 (published 2026-03-17, effective
2026-04-17) §6(c) pays App Proceeds monthly, subject to the USD $50 payment
threshold stated in the payout-methods documentation §6(c) references
(<https://go.microsoft.com/fwlink/?linkid=2199849>, fetched 2026-07-28). Bet A
proceeds from an ~Aug 1 launch pay out mid-August at the earliest,
realistically mid-September — after Day 28. Accrued Store earnings are now
tracked separately from collected cash and never counted as revenue.
(2) **Blended fee model.** ADA §1(h) retains an extra 10% Commerce Expansion
Adjustment on gift-card/mobile-operator-billing transactions (25% total on
those) and §1(t) defines Net Receipts as net of refunds and chargebacks. The
plan now models a blended $12.10–$12.74 net per sale with a 3% refund
planning assumption → ≈ 322–335 required sales, replacing 314 as the
planning figure (314 remains the optimistic baseline bound, verified per
§6(b)(i)).
(3) **Bet B tax-identity fee.** The "$3 one-time tax-identity adjustment"
was recorded in D008 and `revenue/PLAN.md` without a cited source. A fresh
fetch (2026-07-28) of <https://itch.io/docs/creators/payments> confirms the
fee exists — "Account Adjustments → Tax Identity: a flat fee of $3.00 will be
applied to your account once" — and that it applies to the "Collected by
itch.io (Payouts)" mode only; the "Direct to you" mode gives tax identity to
each payment provider and lists no such adjustment. Decision: keep the fee in
the model with this citation and mode scope rather than remove it.

### D037 — Pre-register the Day-5 reposition menu

The falsifier allows exactly one reposition after five live days with zero
signal. Decision: pre-register four concrete, pre-costed options in
`revenue/PLAN.md` — RP-1 scheduled sale pricing, RP-2 keyword revision, RP-3
listing copy variant, RP-4 market expansion deferred to Submission 2 with the
crisis-copy evidence-chain constraint — with full execution artifacts in
`store/REPOSITION_KIT.md` and a cross-link from `store/CAMPAIGNS.md`, so a
gate fire costs the owner minutes instead of days. Every option names its
exact Partner Center field and requires a new certified submission; every
draft obeys the `store/LAUNCH_KIT.md` claims boundary.

### D038 — Bet B sequencing put to the owner as an explicit either/or (not queued)

> **Accounting correction — 2026-08-26:** the estimates and over-budget option
> below are retained as the historical decision. D047 supersedes them: accepting
> more than 60 owner minutes is not a valid path under the operating law, and
> HQ-07 risk acceptance is an owner judgment, not a recommendation.

Adding PROP-005 approval plus itch.io payout setup (~12 owner minutes) to the
queue would push the total to ~71 minutes, over the 60-minute §10 law.
Decision: no queue item is added; the choice is presented here and referenced
from `revenue/HUMAN_QUEUE.md`.

- **Option A — stay Bet-A-only.** Queue total ≈ 59–60 minutes (44 + HQ-06
  5 min + HQ-07 10 min; 50 if HQ-07 is resolved by the 1-minute risk
  acceptance). Bet B remains conditional and unbuilt.
- **Option B — approve PROP-005 now.** Requires dropping or deferring another
  queued item, or the owner accepting ~11 minutes over budget. CFO finding
  recorded: Bet B's itch.io Direct-to-you rail pays at purchase — better
  cash-timing than Bet A's monthly ADA §6(c) cadence, which cannot collect
  before Day 28 — and the kit build itself is agent work that can start
  immediately upon approval, consuming no owner minutes until listing review.

### D039 — Distribution prep shipped; PROP-004 sequencing amendment proposed

Two agent-doable distribution artifacts shipped today:
`store/LAUNCH_TARGETS.md` (six rule-checked, owner-posted destinations plus
two documented exclusions; HQ-05 now names the file) and the reposition
cross-link in `store/CAMPAIGNS.md`. Separately, the council's sequencing
recommendation — deploy the `landing/` artifact at certification-submit time
instead of after publication — amends PROP-004 and therefore requires owner
approval, so it is queued as HQ-06 (5 minutes) with the D007 GitHub-Pages
constraint carried into the click steps (Cloudflare Pages or Netlify per
PROP-004; GitHub Pages only if a current-TOS re-check reverses D007) and the
rule that no `?cid=landing-primary` wiring happens until the Store page is
observed live (enforced by `scripts/validate-store.mjs` while the listing
stays in draft state).

### D040 — Land CAND-002 to main under owner "get all you can do done" directive

The owner directed the agent to complete all machine-doable work. The CAND-002
replacement-candidate cycle — the 2026-07-29 council remediation plus the
`07cf815` packaged-smoke-gate fix — was already committed and pushed on
`feature/store-candidate-cand002`, CI-green (Windows Store MSIX run
30790687808, AppX `a5d2cf36…`), and was re-verified locally on the **clean**
commit `07d938c` (VER-20260804-001: lint/typecheck/46 tests/vite build/secrets/
store 276/docs validator all pass). Superseding the stale 2026-07-29 "awaiting
owner commit decision" note, `origin/main` was fast-forwarded `246baac`→`07d938c`.

- **Scope:** code land only. It publishes nothing to the Store, connects no
  payment, and contacts no one. The accepted-candidate hash guard
  `4900f382…facdb1` still protects HQ-04 until the owner deliberately swaps in
  CAND-002 (new HQ-04 "Package swap first" step).
- **Reversible:** `git push --force-with-lease origin 246baac:main` restores the
  prior default-branch HEAD.
- **Consequence:** no agent-doable work remains; the sole path to a live listing
  is the owner-only HQ queue. Honest money position is unchanged — the Day-21
  gate finding (collected cash not reachable in-window; Store pays monthly)
  still stands; landing the candidate only makes the product submit-ready.

## 2026-08-19 — Ample candidate reset

### D041 — Treat all Hearth packages as historical after the Ample rename

The rename at `8c853b2` changed the AppX manifest. Decision: CAND-002 and every
other existing MSIX are never-submit; no package hash, screenshot set, or
Partner Center validation observation transfers to Ample. This supersedes
D040's operational conclusion that no agent-doable work remained while
preserving D040 as the true record of the Hearth candidate land.

### D042 — Make observed identity a hard executable gate

The committed checker at `c0eb360` discarded `identityVerified` and therefore
accepted the rename-script guess. The first Ample Windows runs avoided producing
that unsafe AppX only because an unrelated screenshot timeout occurred first.
Decision: require `identityVerified === true` in the shared identity checker,
put the preflight before the local Store build script, cover it with regression
tests, and keep the release state draft while false. The identity string must
come from Partner Center; syntax and naming patterns are not evidence.

### D043 — Lead Store copy with the Windows opening

The 2026-08-07 discovery review found the comparable energy-planning set to be
Apple-only. Decision: lead positioning, short description, feature order, and
description with Windows availability; use local/no-account protections as
proof instead of the headline. Replace the seven search terms with `spoon
theory`, `pacing`, `offline task manager`, `ADHD planner`, `no subscription`,
`offline planner`, and `executive function`. Capability, privacy, medical, and
release claims remain within README.md and docs/PRIVACY.md.

## 2026-08-25 — Existing-product identity observation

### D044 — Separate immutable package identity evidence from display-name work

Authenticated Partner Center observation corrected the 2026-08-19 assumption
that the Ample display-name reservation would yield a new Ample-shaped package
identity. Existing product `9PLRSZZMFPJH` reports exact
Package/Identity/Name `ToledoTechnologies.Hearth`, while Manage app names shows
only `Hearth` currently in use. Decision: build the renamed source with that
observed existing-product identity and keep `identityVerified: true`; never
rewrite it from branding patterns. Reserving the Ample display name remains an
owner-only pre-submission action. No reservation, submission, publication,
attestation, payout/tax, or terms action was taken during the observation.

### D045 — Bind the only current candidate to one source, run, and hash

The locally gated tree was published once on canonical `main` as exact remote
source `3b8d225`; Quality 32844120492 and Windows 32844120483 passed. Decision:
AMPLE-001 is exclusively AppX SHA-256 `7d6ca584…61866b` from artifact
9561731052 with screenshots artifact 9561704379. CAND-002 and every other MSIX
remain never-submit. The evidence-only documentation close must not touch a
Windows-workflow trigger, so it cannot mint another near-identical candidate.
The candidate does not remove the owner-only display-name, IARC, payout,
submission, certification, signed-build review, or publication gates.

## 2026-08-26 — Post-candidate continuation

### D046 — Stop package churn; remove wrong-candidate ambiguity instead

Live revalidation found AMPLE-001 unchanged and complete: source `3b8d225`,
Windows run 32844120483, and AppX `7d6ca584…61866b` remain the sole candidate.
Decision: do not generate another package merely to create activity. Use this
cycle for documentation-only safety work: mark CAND-002 never-submit inside its
ignored staging folder, add a root `tmp/` selection guard, distinguish
historical Hearth Partner Center fields from current Ample readiness, and keep
launch drafts platform-first. The public Ample name screen remains
follow-up-needed, not clearance. Reservation and legal judgment remain owner
actions, as do IARC, payout/tax, upload, submission, terms, certification, and
publication.

### D047 — Count every renamed-product owner step before claiming the 60-minute path

The prior queue arithmetic omitted the separate Ample display-name reservation
and understated the renamed listing/package/screenshot work. Decision: retain
the historical totals but never present them as current. Remaining work is
approximately 79 minutes with a full HQ-07 screen or 70 minutes with its
one-minute informed-risk path after two grounded scope corrections: exact
AMPLE-001 CI removes three minutes of duplicate HQ-03 smoke work (15 active
human minutes remain; do not go lower), and the fully prepared package/copy/
screenshot batch is 13 active minutes (passive transfer/validation wait
excluded; do not go lower). Deferring post-live HQ-05 and optional HQ-06 yields
69 or 60 minutes. The sole documented full-run plan at the hard ceiling also
batches the one-line risk record into the five-minute reservation session: 59
remaining minutes plus the conservatively counted one-minute HQ-00
authorization. This is conditional arithmetic, not a recommendation or legal
conclusion; full screening still requires further truthful scope reduction.

## 2026-08-27 — Partner Center draft intervention

### D048 — Treat exact-name unavailability as an owner naming gate

Authenticated Partner Center reported exact `Ample` unavailable and returned
`Ample Energy Planner` available. Decision: do not reserve a fallback or save
an internally inconsistent package/listing on the owner's behalf. Keep the
AMPLE-001 upload and Ample-branded listing edit blocked until the owner chooses
and reserves an available display name. The agent may still correct independent
draft fields already approved by the owner: the observed $0 price was changed
to $14.99 and saved. No package, screenshot, listing-name, IARC, terms,
submission, certification, publication, or payout/tax action was taken.

## 2026-08-28 — Paulatim selection and submission authority

### D049 — Rename visibly to Paulatim while preserving Store/data identity

The owner rejected Ample, selected **Paulatim**, and explicitly authorized the
agent to reserve the name, create the replacement Store candidate, replace the
draft, submit it for certification, and remove Hearth application-name/listing
references. Partner Center returned exact Paulatim available; it was reserved
on existing product `9PLRSZZMFPJH` and set as dashboard name. Decision: treat
this as a visible-brand rename only. Preserve Microsoft-assigned package
identity `ToledoTechnologies.Hearth`, AppX application ID `Ample`, Electron app
ID `io.ampleproject.ample`, the established `Ample` user-data directory,
`ample.*` encrypted-file names, preload/harness contracts, and export schema so
an update cannot lose data or break package continuity. AMPLE-001 and all
Hearth artifacts become historical/never-submit; only fresh PAULATIM-001 may be
uploaded. Certification submission is authorized; publication remains a
separate post-certification state change.

### D050 — Use version 1.1.1 for the changed Paulatim package bytes

The canceled Hearth draft already uploaded x64 version 1.1.0. Microsoft Store
package rules require a unique full name for packages with different contents
at the same architecture; reusing 1.1.0 for Paulatim can be rejected even after
removing the old draft package. Decision: advance the fresh Paulatim package to
1.1.1 while preserving product/package/application identity. This is a package
uniqueness correction, not a claim that 1.1.0 was published.
