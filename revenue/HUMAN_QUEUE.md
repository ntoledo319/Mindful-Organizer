# Human Queue

_Owner labor ceiling: 60 minutes for the full run. Current queued total: **44
minutes**. Do not batch in extra outreach or content work._

## HQ-01 — Verify Microsoft seller, tax, and payout readiness — 12 minutes

- **What:** Confirm the existing Toledo Technologies Partner Center account can
  receive paid app proceeds and that product `9PLRSZZMFPJH` is still reserved.
- **Why human-only:** Sign-in, identity/KYC, tax attestations, and banking details
  are owner-controlled credentials and legal representations.
- **Steps:**
  1. Open <https://partner.microsoft.com/dashboard> and sign in.
  2. Open **Settings → Account settings**; confirm the publisher is the real
     Toledo Technologies entity represented in `store/identity.json`.
  3. Open **Payout and tax**; complete or confirm every required profile without
     sharing credentials in the repo.
  4. Open **Apps and games**, search product ID `9PLRSZZMFPJH`, and confirm the
     reservation is active. Do not submit a package yet.
  5. Record only status/date—never account numbers or tax identifiers—in this
     queue item.

## HQ-02 — Enable the advertised GitHub support channel — 2 minutes

- **What:** Allow users to create GitHub Issues in the public repository.
- **Why human-only:** This changes public repository interaction settings and
  opens a human-contact channel the owner must monitor.
- **Steps:**
  1. Open <https://github.com/ntoledo319/Mindful-Organizer/settings>.
  2. Under **General → Features**, check **Issues**.
  3. Open <https://github.com/ntoledo319/Mindful-Organizer/issues/new> in a
     private window and confirm a new issue form is available. Do not submit one.

## HQ-03 — Confirm or reject brand-asset provenance — 5 minutes

- **What:** Provide the origin, creator, rights, and AI-assistance status for
  `resources/app-icon.png` and `resources/hero-illustration.png`.
- **Why human-only:** Git history identifies only an agent-authored commit; the
  owner must know whether source material was owned, commissioned, licensed, or
  AI-generated.
- **Steps:**
  1. Review the [app icon](https://github.com/ntoledo319/Mindful-Organizer/blob/main/resources/app-icon.png)
     and [hero](https://github.com/ntoledo319/Mindful-Organizer/blob/main/resources/hero-illustration.png).
  2. For each, state one of: `original-owned`, `AI-generated with tool/model`,
     `licensed with source URL/license`, or `unknown`.
  3. If either is unknown, mark it `replace`; do not guess. The agent will build
     rights-clean replacements inside the workspace in the next cycle.

## HQ-04 — Front-load itch.io seller verification — 10 minutes

- **What:** Create/inspect the zero-upfront seller account for Bet B and confirm
  its payout method can be configured.
- **Why human-only:** Account acceptance, tax interview, and payout identity are
  owner legal/financial actions.
- **Steps:**
  1. Open <https://itch.io/register> or sign into the existing account.
  2. Read/accept the current Terms and seller terms shown by the platform.
  3. Open <https://itch.io/user/settings/seller>, choose itch.io Payouts, and
     complete the tax/payout setup if it requires **no upfront payment**.
  4. itch.io documents a one-time $3 tax-identity adjustment deducted from the
     seller balance; do not pay a separate setup charge. If any upfront charge
     appears, stop and mark this bet blocked.
  5. Do not create a public product page until the new kit passes its own
     license/provenance gate.

## HQ-05 — Manual paid Store submission, only when unblocked — 15 minutes

- **What:** Enter the final $14.99 price/listing and submit the exact verified
  MSIX from the green commit.
- **Why human-only:** Paid pricing, legal declarations, age rating, package
  submission, and the final public publish click are owner commitments.
- **Blocked until:** Encryption/migration implemented, asset provenance cleared,
  support works, fresh Windows smoke passes, screenshots match, and the agent
  marks all `store/README.md` gates complete.
- **Steps after unblock:**
  1. Open <https://partner.microsoft.com/dashboard>, then product
     `9PLRSZZMFPJH`.
  2. Create a new submission; set the base one-time price to **$14.99**.
  3. Manually enter the reviewed copy from `store/listing-metadata.json`, the
     live privacy/terms/support URLs, age rating, screenshots, and certification
     notes disclosing local wellness data and protection.
  4. Upload the hash-matched MSIX recorded in `METRICS.md`.
  5. Review every declaration, click **Submit to the Store**, and record the
     submission ID/time in `METRICS.md`.

## Running owner-time ledger

No owner minutes are recorded as spent in this cycle. Queue estimates total
12 + 2 + 5 + 10 + 15 = **44 minutes**, leaving 16 minutes of reserve.

## Cycle 0 close — 2026-07-14 01:40 EDT

The public review branch and green hosted code gate required **0 owner minutes**.
No queue item was guessed complete. HQ-01 through HQ-04 are ready to batch;
HQ-05 remains explicitly blocked. The total stays **44 minutes**.
