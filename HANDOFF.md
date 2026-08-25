# Hearth Mission Handoff

_Cold-start launchpad. Compressed 2026-07-24: supersedes the 528-line local
draft (archived at `docs/project/archive/pre-consolidation/2026-07-24/HANDOFF.local-draft-2026-07-15.md`)
and the 400-line published iteration (Git history, commit `0ff209e`). Current
coordination truth lives in `PROJECT_TRACKER.md`; this file only gets an agent
started. Last reconciled 2026-08-04 against `origin/main` `270e650`._

## 0B. Current correction — 2026-08-25

_This section supersedes the 2026-08-19 resume point below without rewriting
its historical record._

- **Execution outcome 2026-08-25T11:53Z:** AMPLE-001 is complete at exact
  source/CI SHA `3b8d225`. Quality run 32844120492 and Windows run 32844120483
  passed; the AppX SHA-256 is `7d6ca584…61866b`, and artifacts 9561731052 /
  9561704379 are staged at `tmp/AMPLE-001-3b8d225/` with a hash README. This
  supersedes the earlier same-day resume instructions below. Nothing was
  uploaded to Partner Center, reserved, submitted, certified, or published.
- Live `git`/`gh` observation found no remote movement since 2026-08-19:
  checked-out `feature/store-candidate-cand002`, `origin/main`, and the remote
  feature ref remained at `c0eb360`; the protected Python-era `stash@{0}`
  remained intact.
- **Execution update 2026-08-25T11:32Z:** after that observation, local `main`
  was safely fast-forwarded to `origin/main` and checked out with the prepared
  working tree intact. The remote refs remain at `c0eb360`, and only canonical
  `main` will be pushed for AMPLE-001. The complete local candidate gate then
  passed at 2026-08-25T11:38Z (VER-20260825-002); commit and exact-SHA CI are
  the remaining machine steps.
- With the owner's authorization, Partner Center product `9PLRSZZMFPJH` was
  reobserved. Product identity reports the exact Package/Identity/Name
  `ToledoTechnologies.Hearth`. Manage app names reports only `Hearth` as
  currently in use. No name was reserved or changed, and nothing was
  submitted, published, attested, or configured for payout.
- `store/identity.json` now records that observed package identity with
  `identityVerified: true`. The Ample marketing/display-name reservation is a
  separate owner action; it does not authorize changing the existing product's
  package identity to a guessed Ample-shaped string.
- No Ample candidate existed at the time of observation. The complete local
  gate has since passed; resume AMPLE-001 with one canonical `main` push,
  select CI by the exact pushed SHA, then hash and stage only that run's
  `ample-msix` and `ample-store-screenshots` artifacts.

## 0A. Current correction — 2026-08-19

_This section supersedes the 2026-08-07 resume point below without rewriting
its historical record._

- Live `git` and `gh` observation: checked-out
  `feature/store-candidate-cand002`, `origin/main`, and
  `origin/feature/store-candidate-cand002` all began this session at `c0eb360`.
  Local `main` remains stale at `c2b1fc2` (33 behind). `stash@{0}` still holds
  the Python-era file-indexer work and must not be cleared.
- Product source is now named **Ample**, but there is **no Ample candidate
  AppX**. Every hash and package recorded below is Hearth-era evidence.
  CAND-002 (`a5d2cf36…b18f`) and `tmp/CAND-002-SWAP/` are historical and must
  never be submitted after the manifest rename.
- `store/identity.json` still has `identityVerified: false`; its identity name
  is a rename-script guess. The only unblock is the exact
  Package/Identity/Name observed in Partner Center. Do not guess it and do not
  build an AppX before it is recorded.
- CI at `c0eb360` is red. Quality runs 32310869115 (main) and 32310866310
  (feature) exposed stale renamed third-party notices. Windows runs
  32310869046 and 32310866359 timed out because the screenshot launcher still
  exported `HEARTH_*` while the app reads `AMPLE_*`; both produced zero
  artifacts. The committed identity checker also ignored
  `identityVerified`, so the screenshot failure was the only thing that
  prevented a guessed-identity AppX.
- The current working tree contains local fixes for that identity guard, the
  screenshot environment, third-party notices, Store validation, regression
  tests, and platform-first listing copy. Safe non-package gates have passed;
  the tree remains intentionally uncommitted/unpushed until the owner supplies
  the observed identity, after which the full gate, single canonical push,
  exact-SHA CI observation, AppX hash record, and staging sequence resumes.

## 0. Resume point — 2026-08-07 (read this first)

_Corrected 2026-08-07 after an owner-directed independent reverification. The
2026-08-04 revision of this section was already wrong when it was committed —
see "Corrections" below. Do not trust a resume point that has not been
re-derived from `git` and `gh` in the current session._

Current state:

- **`origin/main` @ `37feea1`** — the commit that added the 2026-08-04 resume
  point. CI **Quality Gate green** on it (run 31154833115). The last commit to
  get a **Windows Store MSIX** build is `270e650` (run 30891744008); the last to
  produce the *submission candidate* is `07cf815` (run 30790687808).
- **Checked out branch is `feature/store-candidate-cand002`, not `main`.**
  Local `main` is stale at `c2b1fc2` (25 behind). Startup step 6's git-vs-tracker
  comparison will look wrong until you account for this.
- Working tree clean. CAND-002 is landed.

**Local test suite requires one command before it will pass.** `better-sqlite3`
in `node_modules` is currently compiled for whichever ABI last touched it. After
any `electron-builder` run it targets Electron's `NODE_MODULE_VERSION` and 16 of
46 tests fail on plain node with an ABI mismatch — this is environmental, not a
regression, and CI stays green throughout. Fix with `npm rebuild better-sqlite3`
(restores node ABI; `electron-builder` re-rebuilds for Electron when packaging).
Verified both directions 2026-08-07: broken 30/46 → rebuilt → **46/46 pass**.

**The CAND-002 swap package is pre-staged.** `tmp/CAND-002-SWAP/` holds the
AppX, the five refreshed screenshots, and a README. The hash was independently
recomputed from the downloaded artifact and matches. HQ-04's "download from CI
and confirm the hash" step is already done — see §4.

### Corrections to the 2026-08-04 resume point

| It said | Actually |
|---|---|
| `origin/main` @ `270e650` | `37feea1`. `PROJECT_TRACKER.md` separately said `07d938c`. Three documents, three answers. |
| "Working tree clean" (§0) | True — but §7 simultaneously claimed an uncommitted cycle-3 draft exists and must be preserved. It does not. |
| "All local gates green ... 46 tests" | Not reproducible on this host without the rebuild above. |
| "There is no agent work left" | False. This correction pass, the hash verification, the decoy documentation, the staging kit, and the test-environment fix were all machine work. |
- **CAND-002 is the current replacement candidate.** Source `07cf815`, package
  `Hearth 1.1.0.appx`, AppX SHA-256
  `a5d2cf3633def56983702d41d17f6fa458abd8dfedc818039ed1af040f36b18f`, from CI
  Windows Store run 30790687808 (green; artifacts `hearth-msix` + refreshed
  `hearth-store-screenshots`). Full record: `store/WINDOWS-VALIDATION.md`. It
  deliberately supersedes the old accepted AppX `4900f382…` — see §4.
- **Local gates re-run 2026-08-07 on `37feea1`** (VER-20260807-001): lint 0,
  typecheck ×2, **46/46 tests after `npm rebuild better-sqlite3`**, vite build,
  secrets 189, store 276, `npm audit --omit=dev` 0 vulnerabilities.

**Agent work remaining is listed in §8.** The only path to a live, purchasable listing is
the owner-only Human Queue (`revenue/HUMAN_QUEUE.md`): HQ-02 payout (start
first) → HQ-01 IARC → CAND-002 Partner Center package swap (HQ-04 "Package swap
first", now pre-staged) → HQ-03 Windows/a11y pass → HQ-04 submit + publish →
HQ-06 landing deploy → HQ-05 launch batch (HQ-07 name check or 1-min risk-accept
before HQ-04).

**Re-estimate 2026-08-07 — the ≈54-minute figure is not wrong, it is
incomplete.** Clicking time is roughly right (and HQ-04's swap step drops from
≈4 min to ≈1 with the staged kit). What the number omits are three things that
actually control the date:

1. **HQ-02 may not be a 10-minute task at all.** The queue itself records that
   "Payout and tax" is *absent* from Account settings and may require Partner
   Center **support** to fix the developer-profile role. A support ticket is
   days, not minutes. This — not the documented 48-hour payout validation — is
   the real critical path, and it is unpriced.
2. **HQ-03 requires a physical x64 Windows machine.** Nothing in this repository
   establishes that one is available. That is a hard dependency with no owner or
   date attached to it.
3. **Microsoft certification is days of wall-clock.** It is correctly excluded
   from the labor ceiling but it is not excluded from the calendar.

Honest shape: ≈50–60 owner-minutes of actual clicking, spread over **at least
three sessions**, gated by payout-role resolution (unknown, possibly days),
certification (days), and Windows-hardware availability (unestablished).

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
  because the 2026-07-29 remediation changed the app bytes. Do not swap packages
  autonomously — the swap is owner action HQ-04.
- **The CAND-002 hash is independently verified.** On 2026-08-07 artifact
  8846968340 was downloaded from run 30790687808 and the contained AppX
  recomputed: `a5d2cf36…b18f`, matching. The package and the five refreshed
  screenshots are staged at `tmp/CAND-002-SWAP/` with a README.
- **Never-submit artifacts.** `8316167277` and `8613344727` are verification
  output. Added 2026-08-07: **`8885413072`** (run 30891744008, `270e650`), AppX
  SHA-256 `368b0eeb…e7b1`, zipped 174,530,569 B — within 124 bytes of CAND-002
  because `07cf815..270e650` is docs-only. It is the **newest** MSIX in the
  Actions list and therefore the one an owner reaching for "the latest build"
  hits first. This was previously undocumented and is the single most likely
  way to break the evidence chain by accident.
- **Partner Center facts in this repository are memory, not observation.** The
  guard-hash claim above rests on a live check dated **2026-07-14**. Tracker
  risk R3 says the same thing. Reobserve before acting on any of it.
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
local verification runs normally.

**Corrected 2026-08-07:** this section previously stated that "the uncommitted
working tree is the pre-publication cycle-3 draft ... do not discard it without
owner approval." That has been false since `fe0fc4a`/`07cf815`/`07d938c`/
`270e650` landed. The working tree is clean; RECON-001 is `done`. The claim
directly contradicted §0's own "Working tree clean" line in the same document.

**Orphaned stash (documented 2026-08-07, not resolved).** `git stash list`
holds `stash@{0}`, created on `release/v1.1.0-prep` — a branch that no longer
exists and which no document in this repository references. Its contents belong
to the **Python** incarnation of this project, not to Hearth: a Windows SQLite
handle-cleanup fix across `src/core/database.py`,
`src/core/smart_file_system/file_indexer.py`, and `smart_file_system.py`, plus
an apt-package fix in a Python-era `tests.yml`. It is not Hearth work and is not
applicable to the Electron tree, but it is real prior work and is one
`git stash clear` away from being gone. Owner decision required: keep, branch
it for the record, or drop. Do not clear it silently — §5 forbids removing
historic assets in a cleanup pass.

**Local `node_modules` ABI (see §0).** `better-sqlite3` flips between node and
Electron ABIs depending on whether `electron-builder` last ran. `npm rebuild
better-sqlite3` restores the node ABI for `npm test`; packaging re-rebuilds for
Electron automatically. Neither state indicates a code problem.

## 8. Agent work remaining (added 2026-08-07)

The 2026-08-04 resume point asserted "there is no agent work left." That was
false, and stating it prevented the next session from looking. Current list:

**Done this session (2026-08-07):**

- CAND-002 hash independently reverified from the downloaded artifact.
- Decoy artifact 8885413072 identified, hashed, and documented (§4).
- Swap kit staged at `tmp/CAND-002-SWAP/` with README.
- `better-sqlite3` ABI mismatch diagnosed and fixed; 46/46 tests restored.
- False Partner Center "Validated" claim removed from
  `store/WINDOWS-VALIDATION.md`.
- Cross-document `origin/main` disagreement reconciled.
- Orphaned Python-era stash documented (§7).

**Open, machine-doable:**

- **Stash disposition** — needs an owner decision (keep / branch / drop), then
  the agent executes it. Blocked on the owner, not on capability.
- **Pricing and positioning re-derivation** — the $14.99 price and the "314
  sales" arithmetic in §2 were set before any market observation. A fresh
  comparable-set and price-band analysis is agent work and does not touch the
  Store. Any change to the listed price is an owner action.
- **Post-publication doc sweep** — `store/POST_PUBLICATION_DOC_SWEEP.md` is
  pre-drafted; it executes the same day the listing goes live.
- **Standing hygiene** — every future session should re-derive the resume point
  from `git`/`gh` rather than trusting the previous session's summary. The
  failure mode in this repository is not dishonesty; it is four documents that
  each claim canonical status drifting out of sync between sessions.
