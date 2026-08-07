# Hearth Proposals

_Unapproved scope. Nothing here is active work; promotion requires owner
approval (or an explicit user instruction). Monetization frame proposals live
in `revenue/OPPORTUNITIES.md`; this file covers repository-maintenance and
process scope. Established 2026-07-24._

| ID | Title | Size | Approval | Affected area |
|---|---|---|---|---|
| PROP-001 | Reconcile working tree with `origin/main` | S | **executed 2026-07-24** (merge `59787f4`) | git state |
| PROP-002 | Branch hygiene: remove duplicate-content and superseded branches | S | pending (destructive; explicit approval required) | git refs |
| PROP-003 | Branch strategy: fast-forward local `main`, retire `cycle-*` naming | S | pending | git workflow |
| PROP-004 | Deploy `landing/` to an eligible $0 static host after Store publication | S | pending (gated on live Store URL) | distribution |
| PROP-005 | Bet B — Hearth-to-Production Electron Kit (frame A4.6) | L | pending (conditional behind Bet A) | monetization |

## PROP-001 — Reconcile working tree with origin/main

- **Status: EXECUTED 2026-07-24** via user-authorized commit + merge + push
  (HIST-20260724-004…006). The draft was committed (`d1c9d91`), `origin/main`
  merged (`59787f4`), and the result pushed to `main`. Resolution rules applied:
  consolidated documents win where consolidation made a decision (HANDOFF.md,
  PLAN.md, METRICS.md hand-merge); published remote iterations win for the four
  revenue files the consolidation never touched. No content lost: draft lives in
  `d1c9d91` and the archive; published iteration lives in `0ff209e`/`e0fc9e0`.
- ~~What~~ (original): adopt the published cycle-3 state (`e0fc9e0`) into the
  checkout and retire the uncommitted local draft.
- **Evidence:** VER-20260724-006 (post-merge gates green).

## PROP-002 — Branch hygiene

- **What:** delete local `cycle-1-published`, `cycle-1-release-state`, local
  `feature/monetization`, and (with owner approval) remote `handoff-cycle-3`
  and `feature/revenue-cycle-0`.
- **Why:** local duplicates have trees byte-identical to main-line commits
  (verified 2026-07-24, empty diffs vs `4a32b73` / `5bb2611` / `8172603`) and
  exist only as cycle bookkeeping; `handoff-cycle-3` content is already on
  `origin/main`; `feature/revenue-cycle-0` is declared diverged legacy.
- **Risks:** destructive ref removal — trees are preserved on main /
  `origin/feature/monetization`; explicit owner approval required; record a
  `remote-changed` / `branch-removed` history event if executed.

## PROP-003 — Branch strategy

- **What:** fast-forward local `main` to `origin/main` (0 ahead, 17 behind),
  work on `main` or short-lived feature branches, stop creating `cycle-*`
  bookkeeping branches; adjust workflow branch triggers only if conventions
  change.
- **Why:** local `main` currently points at a 2026-06-13 commit while the
  effective main line lives on `origin/main`; stale `main` misleads any tool
  or agent that assumes it is current.

## PROP-004 — Landing deployment (post-publication)

- **What:** deploy the scriptless `landing/` artifact to an eligible $0 static
  host (Cloudflare Pages / Netlify after a current-TOS re-check) once the Store
  page is observed live.
- **Why:** D007 rejected GitHub Pages for commercial hosting; the artifact is
  ready but has no purchase link until the listing exists.
- **Prerequisites:** live Store URL (HQ-04), campaign IDs (store/CAMPAIGNS.md).

## PROP-005 — Bet B: Hearth-to-Production Electron Kit

- **What:** genuinely new $249 developer kit (frame A4.6 in
  `revenue/OPPORTUNITIES.md`): clean demo, threat model, encrypted-storage
  migration pattern, sender-validated IPC, packaging, CI, tests. Not a paid
  copy of the MIT repo.
- **Status:** conditional; stays behind Bet A's certification path. Falsifier,
  arithmetic, and funnel are defined in `revenue/OPPORTUNITIES.md` and
  `revenue/PLAN.md`.

## PROP-006 — Lead with privacy, not with ADHD (2026-08-07)

- **What:** reframe the Store listing's leading claim and the HQ-05 launch
  targets around *local-only, no account, no telemetry, one-time purchase,
  Windows desktop* — keeping ADHD and variable-capacity days as the supporting
  use case rather than the headline. No code, no feature, and no price change.
- **Why:** the first comparable set for this product
  (`revenue/MARKET-ANALYSIS-2026-08-07.md`) shows the ADHD-planner category is
  subscription-priced and mobile/Apple-dominated. In that category Hearth's
  Windows-only, sync-free, AI-free, no-free-tier profile reads as a list of
  missing features against better-funded incumbents. Described instead as
  software that never touches the network, the same properties read as the
  product, and the comparable set contains no competitor at all — every one is
  a cloud account.
- **Also:** the privacy framing has $0 amplification channels (technical and
  privacy communities) that the ADHD framing does not, which matters because
  HQ-05 is capped at owner-authored posts and there is no ad budget.
- **Prerequisites:** owner approval. Listing copy is an owner action; the
  agent-side work (redrafting `store/listing-metadata.json` copy,
  `store/LAUNCH_KIT.md`, and re-vetting `store/LAUNCH_TARGETS.md` against the
  new framing) can be prepared for review in advance.
- **Honest limit:** this reasons from category structure, not from observed
  demand for Hearth. It is better grounded than the current framing's evidence
  base, which is none. It is still a guess, and the five-day signal gate is what
  would actually settle it.
- **Do not:** widen any capability claim to fit the new frame. The privacy
  claims must stay exactly as narrow and demonstrable as `docs/PRIVACY.md` and
  `README.md` already make them.

## PROP-007 — Close out the $4,000 / Day-28 target (2026-08-07)

- **What:** formally retire the $4,000-collected-by-Day-28 goal in
  `revenue/PLAN.md` and replace it with: a live purchasable listing, first
  collected dollar, and a first real demand signal.
- **Why:** Day 28 is 2026-08-10 and nothing is submitted; certification is days
  and the Store pays monthly against a $50 threshold, so August sales pay
  ~mid-September. The Day-21 gate already reached this conclusion. Continuing to
  restate a $4,000 gap that is arithmetically unreachable is itself a source of
  manufactured urgency, which `AGENTS.md` §2 forbids.
- **Prerequisites:** owner decision. This changes the mission statement, so it
  is not agent-executable.
