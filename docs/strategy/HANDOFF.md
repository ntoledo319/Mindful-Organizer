# Hearth Engineering and Revenue Handoff

_Current as of 2026-07-14._

## Product truth

Hearth is a substantial Electron/React/SQLite local-first organizer. It has task
energy budgeting, mood/sleep/journal reflection, practices and focus blocks,
local wellness heuristics, crisis-plan access, presence controls, ERP/diary
notes, and medication reference data. It is not a medical device and has no
validated clinical workflow.

## This cycle's corrections

- Replaced the fake clinic-license spinner with a real local PDF session summary
  available to every user.
- Removed Stripe test links, arbitrary `PRO-` keys, voice-dictation privacy risk,
  and unsupported medication-reminder language.
- Added explicit wellness-data consent, safe `tel:`/`sms:` crisis actions,
  transactional task decomposition, and correct tray lifecycle behavior.
- Upgraded to a supported Electron release and restricted IPC to Hearth's own
  top-level renderer.
- Replaced stale Python CI with the Node quality gate; removed the unsafe,
  known-broken Store publisher while retaining a review-only package build.
- Generated runtime license notices and packaged them with the project license.
- Reconciled privacy, Store, ethics, and strategy documentation with code truth.

## Release truth

No current public binary, paid listing, or collected revenue is verified. The
historical artifacts are expired and predate this work. Before a public binary:

1. resolve protection for the unencrypted sensitive local database;
2. record brand-asset rights and provenance;
3. enable a working support channel;
4. produce and smoke-test a fresh Windows package;
5. complete paid metadata and submission manually in Partner Center.

## Durable operating state

Resume from all six files in `revenue/`, beginning with `revenue/PLAN.md`.
Those files hold the asset audit, 35 monetization frames, selected bets, observed
metrics, owner queue, and decisions. Do not revive superseded projections from
git history.
