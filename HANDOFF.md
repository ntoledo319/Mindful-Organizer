# Hearth Mission Handoff

_Cold-start launchpad. Compressed 2026-07-24: supersedes the 528-line local
draft (archived at `docs/project/archive/pre-consolidation/2026-07-24/HANDOFF.local-draft-2026-07-15.md`)
and the 400-line published iteration (Git history, commit `0ff209e`). Current
coordination truth lives in `PROJECT_TRACKER.md`; this file only gets an agent
started. Last reconciled 2026-07-24 against `origin/main` `e0fc9e0`._

## 1. Startup sequence

1. Working directory must be `/home/nick/Development/active/mindful_organizer`
   and must match line 1 of `revenue/PLAN.md`. Stop if either is outside it.
2. Read `AGENTS.md` completely — it outranks this file (jail, legal/TOS, $0
   spend, truth, no-autonomous-contact, owner-time, evidence laws).
3. Read `PROJECT_TRACKER.md` completely — current state, tasks, blockers.
4. Monetization cycles: also read all six `revenue/` state files (AGENTS.md §3).
5. Read only the canonical document for the active task (tracker §2 map).
   History/archives are for historical questions, not routine work.
6. Run `git status --short --branch` and compare with the tracker header.
   Preserve user-owned and uncommitted changes; never reset them away.
7. End of session: update tracker + ledgers per tracker §0 and AGENTS.md §14.

Authority order when documents disagree: `AGENTS.md` → newly observed live
evidence in `revenue/METRICS.md` → the six `revenue/` files →
`PROJECT_TRACKER.md` → this file → `store/README.md` +
`store/WINDOWS-VALIDATION.md` → README and older strategy documents. Never
silently choose the most optimistic statement: reverify, record, update every
affected document.

## 2. Mission and money truth

Collect **$4,000 cumulative profit from strangers by Day 28** at $0 spend and
≤60 owner minutes (Day 1 = 2026-07-14; Day 28 = 2026-08-10 if that start
holds). Collected so far: **$0.00**; gap **$4,000.00**; live paid listings: 0.
Active bet: one-time **$14.99** Microsoft Store purchase (planning net $12.7415
at the documented 15% fee; 314 sales ≈ $4,000.83 — arithmetic, not demand).
Details: `revenue/PLAN.md`, `revenue/OPPORTUNITIES.md`, `revenue/METRICS.md`.

## 3. Product truth (one paragraph)

Hearth 1.1.0 is an Electron 43 / React 18 / TypeScript Windows desktop energy
planner for ADHD and other variable-capacity days: user-chosen 4–24 daily
budget, honestly costed tasks, up to three fitting recommendations, local
check-ins, trends, practices, focus controls, a user-written crisis plan, and
requested JSON/PDF exports. Local-only: no account, cloud, ads, sync,
telemetry, or remote AI. SQLite in memory while open; versioned AES-256-GCM
snapshots at rest with the random key protected by Windows DPAPI via Electron
`safeStorage`; fails closed without protected key storage. It is personal
organization software — never a medical device, diagnosis, treatment, monitor,
or crisis detector. Full claims boundary: `README.md`, `docs/PRIVACY.md`,
`store/LAUNCH_KIT.md`.

## 4. Non-negotiable release facts

- Accepted candidate: source `8172603b62c2457696608c145511bd3fe92429d4`, AppX
  SHA-256 `4900f3823febace53f86f69ee2567b50208aec8f6677741c3c4dcf3667facdb1`,
  artifact `8306541856`, marked Validated in Partner Center Submission 1 under
  a saved manual publication hold. Never replace it with later CI artifact
  `8316167277` (different bytes, verification-only).
- Release state: draft only — not submitted, certified, published, or
  purchasable. Remaining gates are owner-only: HQ-01 IARC retake, HQ-02 payout
  readiness, HQ-03 test route + signed Windows pass, HQ-04 certification then
  deliberate publication, HQ-05 launch batch (44 minutes total;
  `revenue/HUMAN_QUEUE.md` is the sole detailed owner-action list).
- Full evidence chain (hashes, run IDs, screenshot digests):
  `revenue/METRICS.md` and `docs/project/VERIFICATION_LOG.md`.
- Vaulted capabilities (diary cards, ERP notes, medication reference, legacy
  condition labels, unverified artwork) are preserved, not deleted:
  `docs/CAPABILITY_VAULT.md`. Permanent removal requires a reviewed migration.

## 5. Never

- automate IARC or accept legal/identity attestations as the owner;
- enter or commit banking, tax, KYC, tester, or account data;
- claim certification, WACK, installed behavior, accessibility, audience, or
  revenue that was not observed;
- publish merely to manufacture a test route, or deploy commercial landing to
  GitHub Pages (D007);
- contact, email, DM, post, solicit reviews, or promise customers autonomously;
- remove vaulted capabilities or historic assets in a cleanup pass;
- expose secrets, personal records, exports, snapshots, or keys.

## 6. Where things live

- Current state, tasks, blockers, next actions: `PROJECT_TRACKER.md`
- Money, evidence, decisions: `revenue/METRICS.md`, `revenue/PLAN.md`,
  `revenue/DECISIONS.md`
- Store release path + certification/publication playbook: `store/README.md`
- Installed-Windows validation: `store/WINDOWS-VALIDATION.md`
- Repository/release history: `docs/project/REPO_HISTORY.md`
- Documentation map: `docs/project/DOCS_INDEX.md`

## 7. Environment note (updated 2026-07-24)

The workspace moved hosts: macOS `/Users/nicholastoledo/...` → Linux
`/home/nick/...` (`revenue/PLAN.md` line 1 corrected 2026-07-24). The 2026-07-15
exit-137 local-shell failure (D034, HIST-20260715-001) does not reproduce here;
local verification runs normally. The uncommitted working tree is the
pre-publication cycle-3 draft and differs from the published `origin/main`
iteration — preserved and tracked as RECON-001 / PROP-001. Do not discard it
without owner approval.
