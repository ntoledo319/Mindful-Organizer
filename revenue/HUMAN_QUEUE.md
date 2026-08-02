# Human Queue

_Canonical context: root HANDOFF.md. Queue rechecked 2026-07-28: HQ-06 and
HQ-07 added; HQ-02 and HQ-05 amended._

_Owner labor ceiling: 60 minutes for the full run. Current queued total:
**59 minutes** (44 prior + 5 HQ-06 + 10 HQ-07; **50 minutes** if HQ-07 is
resolved by the 1-minute risk acceptance). Machine wait and Microsoft review
time are excluded. Do not add extra outreach or content work. Bet B is
deliberately not queued — the explicit either/or is D038 in
`revenue/DECISIONS.md`._

The exact package, five screenshots, copy, price, release hold, public support
page, privacy-guarded issue forms, security policy, private vulnerability
reporting, accurate repository metadata, audience assets, and both remote CI
gates are shipped. Only factual/legal attestations, private financial setup,
active Windows observation, certification, publication, and owner-authored
posts remain.

## HQ-01 — Retake IARC manually and accept its terms — 5 minutes

- **What:** Replace the untrusted low-rating draft with a source-grounded IARC
  questionnaire completed manually by the real publisher.
- **Why human-only:** IARC's current Terms prohibit automated scripts from
  operating the rating tool. Saving also requires the signer to accept a legal
  agreement and attest that they are of majority age in their jurisdiction.
- **Direct link:**
  <https://partner.microsoft.com/en-us/dashboard/products/9PLRSZZMFPJH/submissions/1152921505701225649/ageratings>
- **Steps:**
  1. Click **Edit** and retake the questionnaire manually. Do not use browser
     automation and do not optimize for a lower rating.
  2. Use **All Other App Types** and answer **Yes** to ratings-relevant content
     in the downloaded package.
  3. Disclose textual crisis/self-harm references: Violence **Yes** → violence
     or implied violence against humans → realistic setting → not childlike or
     pixelated → realistic reaction → **Referred to** only → blood/gore None →
     no war setting → no injured/killed characters → no fierce sounds,
     intimidating characters, or dark visual/audio overtones.
  4. Answer Fear No, Sexuality No, Gambling No, Language No, and Crude Humor No.
  5. Disclose the vaulted medication-reference code: Controlled Substance Yes
     → Medical Drugs → **Reference** → Rarely. Do not select illegal/recreational
     drugs, alcohol, tobacco, use, or encouragement/glamorization unless a
     manual reading of IARC's definitions changes that factual assessment.
  6. Keep the no-social-sharing, no-purchases, no-location-sharing, no-rewards,
     no-browser/search, and digital-only answers. Manually open IARC's help for
     **Online Content** and confirm how it treats links handed to the external
     browser before saving.
  7. Read the IARC Terms. Check the legal/majority-age box only if true, save,
     and record the resulting ratings and date in `revenue/METRICS.md`.

## HQ-02 — Confirm seller, tax, payout, and role readiness — 10 minutes

- **What:** Make the Store seller account capable of receiving proceeds.
- **Why human-only:** Tax status, banking, identity, role assignment, and KYC are
  private legal and financial facts. The live account has Earnings access and
  shows $0.00, but **Payout and tax** is absent from Account settings.
- **Direct links:**
  <https://partner.microsoft.com/dashboard/v2/account-settings/overview> and
  <https://learn.microsoft.com/en-us/partner-center/account-settings/set-up-your-payout-account>
- **Steps:**
  1. Open Settings → Account settings and confirm the real seller entity.
  2. Verify this account has Owner or Financial contributor rights for the
     Store seller account. If **Payout and tax** is still missing, use Partner
     Center support to correct the developer-profile role/context.
  3. Create or confirm the tax profile and payout profile, then assign both to
     the Store program/seller ID. Microsoft says validation can take up to 48
     hours; start it before certification wait time is spent.
  4. Record the payout threshold and expected first payout date — both
     non-sensitive facts — in `revenue/METRICS.md`. Microsoft's
     payout-methods documentation (linked from ADA §6(c),
     <https://go.microsoft.com/fwlink/?linkid=2199849>) states the payment
     threshold is USD $50 and that payments occur monthly; note the first
     monthly date on which accrued proceeds would actually pay out.
  5. Record only ready/not-ready, date, and a non-sensitive blocker in
     `revenue/METRICS.md`. Never commit account names, bank data, tax data,
     identity documents, or support-contact details.

## HQ-03 — Choose the non-public Store test route and perform the Windows pass — 18 minutes

- **What:** Observe the Microsoft-signed app on supported x64 Windows before a
  public release.
- **Why human-only:** The accepted AppX is intentionally unsigned; signing it
  locally changes its hash. Narrator, high contrast, text scaling, keyboard
  behavior, and visual fit require an active Windows session and human judgment.
- **Direct links:**
  <https://partner.microsoft.com/en-us/dashboard/products/9PLRSZZMFPJH/submissions/1152921505701225649/availability>
  and `store/WINDOWS-VALIDATION.md`.
- **Steps:**
  1. Before certification, decide whether to change the first submission from
     Public to Microsoft's **Private audience** and add the Microsoft account
     used by the Windows test device. This is the strongest non-public test
     path, but it requires a second submission to move to Public later.
  2. After certification, install the Microsoft-signed build through that
     supported Store route. Do not test-sign or overwrite the accepted AppX.
  3. With fictional data, run consent, capacity persistence, task, check-in,
     practice, crisis-plan edit, JSON/PDF export, erase, quit, and relaunch.
  4. Complete keyboard-only, Narrator, high contrast, 200% text scaling,
     reduced motion, minimum-window, light/dark, and modal-focus checks in
     `docs/ACCESSIBILITY.md`.
  5. Record only Windows build, install route, pass/fail, installed footprint,
     and date. Never commit test records, exports, snapshots, or keys.

## HQ-04 — Submit for certification, then release the manual hold — 6 minutes

- **What:** Start Microsoft review and, only after every gate passes, perform
  the separate publication action.
- **Why human-only:** Submission and publication are legal and commercial
  commitments. Certification itself installs/runs and technically checks the
  exact package; the saved hold prevents automatic public release.
- **Blocked until:** HQ-01 is complete. Complete HQ-02 before expecting payouts;
  choose the HQ-03 test route before submitting.
- **Direct link:**
  <https://partner.microsoft.com/en-us/dashboard/products/9PLRSZZMFPJH/overview>
- **Steps:**
  1. Confirm the package is only `Hearth 1.1.0.appx`, Partner Center says
     Validated, and its source artifact SHA-256 is
     `4900f3823febace53f86f69ee2567b50208aec8f6677741c3c4dcf3667facdb1`.
  2. Review the $14.99 US price, screenshots, categories, URLs, corrected IARC
     result, runFullTrust explanation, testing notes, and release control **Do
     not publish until I select Publish now**.
     The public support URL now resolves signed out. Do not replace the validated
     Partner Center package with verification artifact 8316167277; it is a
     later documentation/launch-hardening build, not a new runtime candidate.
  3. Click **Submit for certification** and record the timestamp/status. Answer
     any Microsoft request truthfully without broadening capability claims.
  4. Preserve the certification result. Complete HQ-03 against the signed build.
  5. Click **Publish now** only after certification, Windows observation, payout
     readiness, page preview, price, support, and package all pass.
  6. In a signed-out browser, verify the page is visible and purchasable; record
     the exact Store URL and time.

## HQ-05 — Approve and execute the first audience batch — 5 minutes

- **What:** Make the smallest owner-authored launch posts after the Store page
  is purchasable.
- **Why human-only:** Posting as the owner or contacting people is forbidden
  without explicit human review and action.
- **Source:** `store/LAUNCH_KIT.md`, `store/CAMPAIGNS.md`, and the
  rule-checked destination list in `store/LAUNCH_TARGETS.md` (built
  2026-07-28; re-verify each destination's current rules immediately before
  posting).
- **Steps:**
  1. Replace draft links with the verified Store URL and source-specific
     campaign IDs.
  2. Re-read each claim against the live listing; remove anything not
     demonstrable that day.
  3. Manually post only to legitimate existing accounts and channels whose
     current rules permit it. Do not cold-DM, scrape, automate, or manufacture
     engagement.
  4. Record URLs and timestamps, then inspect Store acquisition data often
     enough to enforce the five-day signal gate.

## HQ-06 — Approve landing deploy sequencing and enable the $0 static host — 5 minutes

- **What:** Approve the PROP-004 sequencing amendment (deploy at
  certification-submit time, not post-publication) and enable a $0 static
  host for the scriptless `landing/` artifact; record the public URL.
- **Why human-only:** Amending PROP-004 is an owner approval (D039), and
  creating a hosting account/project is an external commitment tied to the
  owner's identity.
- **Direct links:** <https://pages.cloudflare.com/> or
  <https://www.netlify.com/>; proposal text in
  `docs/project/PROPOSALS.md` (PROP-004).
- **Steps:**
  1. Approve or reject the sequencing amendment: deploy the landing page when
     HQ-04's certification submission goes in, so the page is established
     before the Store page is live. The page's prelaunch state is truthful
     ("Store release pending") and is enforced by
     `scripts/validate-store.mjs` while the listing remains a draft.
  2. Use **Cloudflare Pages or Netlify** per PROP-004. D007 rejected GitHub
     Pages for commercial hosting; use GitHub Pages only if you first
     re-check its current terms and record the reversal of D007 in
     `revenue/DECISIONS.md`.
  3. On the chosen host: create a free account, create a new project
     connected to the GitHub repository, set **no build command** with the
     publish/output directory `landing/`, and deploy.
  4. Run the AGENTS.md §9 pre-publish checklist against the deployed page
     (every claim demonstrable today; the artifact is already tracker-,
     form-, script-, cookie-, and remote-asset-free by validator).
  5. Record the public URL and date in `revenue/METRICS.md`.
  6. Do **not** wire any `?cid=landing-primary` link until the Store page is
     observed live and purchasable (HQ-04 step 6). The store validator fails
     the build if that link appears while the listing is in draft state.

## HQ-07 — Clear the "Hearth" name, or explicitly accept the risk — 10 minutes (or 1 minute)

- **What:** A minimum trademark/name collision check for "Hearth" before a
  paid listing attaches money to the name — or an explicit, informed decision
  to accept the risk without searching.
- **Why human-only:** Judging which collisions matter is a legal-risk
  judgment, and accepting the risk is an owner decision. Neither path enters
  private data.
- **Direct links:** <https://tmsearch.uspto.gov/> (USPTO Trademark Search;
  the legacy TESS system was retired 2023-11-30) and
  <https://apps.microsoft.com/search?query=Hearth>.
- **Steps (clearance path — 10 minutes):**
  1. On tmsearch.uspto.gov, run a basic wordmark search for **Hearth**;
     filter to **live** marks and skim software-relevant classes (IC 009,
     IC 042) for anything covering productivity or wellness software.
  2. Open the Microsoft Store search link and skim whether existing apps
     already trade on "Hearth" in adjacent categories.
  3. This is a spot check, not a legal opinion. If anything looks
     conflicting, stop and decide before HQ-04.
  4. Record a one-line, non-sensitive note in `revenue/METRICS.md`: date,
     what was searched, outcome (no-obvious-conflict / follow-up-needed).
- **Steps (risk-acceptance path — 1 minute):**
  1. Record in `revenue/DECISIONS.md` that you accept the name-collision
     risk for the 1.1.0 launch without a search. Nothing else changes.

## Running owner-time ledger

Queued estimates: 5 + 10 + 18 + 6 + 5 + 5 + 10 = **59 minutes**, leaving 1
minute of reserve (resolving HQ-07 by the 1-minute risk acceptance lowers the
total to **50 minutes**, leaving 10). No owner minutes are recorded as spent
in the repository yet.

Bet B (PROP-005 approval + itch.io payout setup, ≈ 12 minutes) is **not
queued**: adding it would reach ≈ 71 minutes, over the 60-minute law. The
explicit either/or is D038 in `revenue/DECISIONS.md` — Option A keeps the
queue at 59–60; Option B requires dropping/deferring another item or the
owner accepting ≈ 11 minutes over budget.

Removed from the queue this cycle: enabling Issues, correcting issue forms,
publishing the support/security pages, and preparing the visual/audience assets.
Those are shipped repository work, not owner chores.

## Cycle 3 clarification — 2026-07-15

Root HANDOFF.md is the canonical context and sequence. The 44-minute queue is unchanged. IARC answer paths below are factual preparation only: the owner must read the exact current question/help wording. Fear classification can depend on how the current tool treats emotionally distressing text, and Controlled Substance wording can distinguish prescribed medical references from illegal drugs. Do not blindly reuse a saved route or target a preferred rating.

