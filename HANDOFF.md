# Hearth Mission Handoff

_Cold-start launchpad. Compressed 2026-07-24: supersedes the 528-line local
draft (archived at `docs/project/archive/pre-consolidation/2026-07-24/HANDOFF.local-draft-2026-07-15.md`)
and the 400-line published iteration (Git history, commit `0ff209e`). Current
coordination truth lives in `PROJECT_TRACKER.md`; this file only gets an agent
started. Last reconciled 2026-08-04 against `origin/main` `270e650`._

## 0. Resume point — 2026-08-04 (read this first)

The prior session (Eve) finished **all machine-doable work** and landed it.
Current state:

- **`origin/main` @ `270e650`** — fast-forwarded from `246baac` this session
  (D040). CAND-002 is landed; CI **Quality Gate + Windows Store MSIX both green**
  on this commit (runs 30891743797, 30891744008). Working tree clean.
- **CAND-002 is the current replacement candidate.** Source `07cf815`, package
  `Hearth 1.1.0.appx`, AppX SHA-256
  `a5d2cf3633def56983702d41d17f6fa458abd8dfedc818039ed1af040f36b18f`, from CI
  Windows Store run 30790687808 (green; artifacts `hearth-msix` + refreshed
  `hearth-store-screenshots`). Full record: `store/WINDOWS-VALIDATION.md`. It
  deliberately supersedes the old accepted AppX `4900f382…` — see §4.
- **All local gates green** on clean `07d938c` (VER-20260804-001): lint 0,
  typecheck ×2, 46 tests, vite build, secrets 189, store 276, docs validator.

**There is no agent work left.** The only path to a live, purchasable listing is
the owner-only Human Queue (`revenue/HUMAN_QUEUE.md`), ≈54 min via the HQ-07
risk-accept path: HQ-02 payout (48h latency — start first) → HQ-01 IARC →
CAND-002 Partner Center package swap (HQ-04 "Package swap first") → HQ-03
Windows/a11y pass → HQ-04 submit + publish → HQ-06 landing deploy → HQ-05 launch
batch (HQ-07 name check or 1-min risk-accept before HQ-04).

**Honest money truth (unchanged):** $0 collected, $4,000 gap. The Day-21 gate
concluded the $4,000-by-Day-28 (2026-08-10) target is **not reachable in-window**
— the Store pays monthly, so August sales pay ~mid-September. Landing CAND-002
only makes the product *submit-ready*; the real goal is a live listing + first
real demand signal. Do not manufacture urgency, velocity, or claims that aren't
real (§2 truth law).

**If the owner rejects the land:** revert with
`git push --force-with-lease origin 246baac:main`.

Do not attempt the owner-only HQ items (legal attestations, payout/KYC, Windows
device testing, publication, owner-authored posts) or anything outside this
repo — that violates the §1 jail and §10 human-queue protocol below.

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

- Candidate lineage (as of 2026-08-04): the **Partner Center guard hash** is
  still the old accepted AppX — source `8172603b62c2457696608c145511bd3fe92429d4`,
  SHA-256 `4900f3823febace53f86f69ee2567b50208aec8f6677741c3c4dcf3667facdb1`,
  artifact `8306541856`, marked Validated under a saved manual publication hold.
  It stays the HQ-04 step-1 guard **until the owner deliberately swaps in
  CAND-002** (`a5d2cf36…`, run 30790687808), the intended replacement built
  because the 2026-07-29 remediation changed the app bytes. Both are distinct
  from CI artifact `8316167277`, which is verification-only and must never be
  submitted. Do not swap packages autonomously — the swap is owner action HQ-04.
- Release state: draft only — not submitted, certified, published, or
  purchasable. Remaining gates are owner-only: HQ-01 IARC retake, HQ-02 payout
  readiness, HQ-03 test route + signed Windows pass, HQ-04 CAND-002 package swap
  + certification then deliberate publication, HQ-06 landing deploy, HQ-05 launch
  batch (≈54 min via the HQ-07 risk-accept path; `revenue/HUMAN_QUEUE.md` is the
  sole detailed owner-action list).
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
