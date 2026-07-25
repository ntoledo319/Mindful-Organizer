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
