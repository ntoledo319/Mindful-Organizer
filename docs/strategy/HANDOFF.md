# Hearth Engineering and Revenue Handoff

_Current as of 2026-07-14 after Revenue Cycle 2._

## Product truth

Hearth is a release-candidate Electron/React/SQLite Windows organizer centered
on a user-chosen energy budget. It has local tasks, check-ins, practices,
rhythm, PDF/JSON exports, crisis-plan access, and presence controls. Diary, ERP,
medication-reference, and legacy condition capabilities remain preserved behind
the capability vault. Hearth is not a medical device, clinical monitor,
emergency service, or cloud product.

At rest, records use authenticated AES-256-GCM snapshots and a random key
protected through Electron safeStorage/Windows DPAPI. CI verifies migration,
backup recovery, missing-key failure, export warnings, and key-first erase. The
documented memory, OS-session, swap/hibernation, plaintext-export, and deletion
limits remain part of every claim.

## Release truth

- Accepted source candidate:
  `8172603b62c2457696608c145511bd3fe92429d4`
- Accepted AppX SHA-256:
  `4900f3823febace53f86f69ee2567b50208aec8f6677741c3c4dcf3667facdb1`
- Partner Center product/submission:
  `9PLRSZZMFPJH` / `1152921505701225649`
- Exact package, $14.99 US price, copy, categories, declarations, testing notes,
  and five exact-candidate screenshots are in a held draft.
- Publication control is **Do not publish until I select Publish now**.
- Public support/security docs and privacy-guarded GitHub forms are prepared.
- No certification, public listing, purchase, fee, payout, or revenue is
  observed.

The accepted AppX is intentionally unsigned. Microsoft certification is the
authoritative exact-package install/run and technical-compliance gate; locally
signing it would change its hash. Store-signed Windows smoke, Narrator, high
contrast, text scaling, keyboard, and reduced-motion observation remain open.

## Remaining gates

1. The owner must manually retake IARC because its Terms prohibit automated
   operation and saving requires legal/majority-age attestations.
2. Partner Center Earnings access works and shows $0.00, but Account settings
   does not expose Payout and tax. The real owner must resolve the seller role,
   tax profile, payout profile, and program assignment privately.
3. Before certification, choose whether to use Microsoft's Private audience
   path for a non-public Store-signed install. It requires a named tester
   account and a later public submission.
4. Submit for certification under the hold, preserve the result, complete the
   active-Windows matrix, and publish only when every gate passes.
5. After checkout is visibly live, execute the owner-approved launch batch and
   enforce the five-day signal gate.

## Durable operating state

Resume by reading all six files in `revenue/`, beginning with
`revenue/PLAN.md`. `revenue/HUMAN_QUEUE.md` is the only owner-action list. Do not
revive superseded projections or old release blockers from git history.
