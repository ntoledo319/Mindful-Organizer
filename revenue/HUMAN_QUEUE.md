# Human Queue

_Owner labor ceiling: 60 minutes for the full run. Current queued total:
**56 minutes**. Machine wait and Microsoft review time are excluded. Do not add
extra outreach or content work._

The product, exact package, screenshots, copy, pricing, and Partner Center draft
are prepared. These are the remaining human-controlled release gates.

## HQ-01 — Exact AppX install, WACK, and manual accessibility pass — 25 minutes

- **What:** Verify the exact 1.1.0 AppX in an installed Windows session.
- **Why human-only:** WACK can require an interactive/elevated Windows session,
  and Narrator, high contrast, text scaling, keyboard behavior, and visual fit
  require human observation.
- **Direct evidence:**
  <https://github.com/ntoledo319/Mindful-Organizer/actions/runs/29322423622>
- **Steps:**
  1. Download artifact 8306541856 from the run above on a supported x64 Windows
     11 machine.
  2. In PowerShell run Get-FileHash on Hearth 1.1.0.appx and require SHA-256
     4900f3823febace53f86f69ee2567b50208aec8f6677741c3c4dcf3667facdb1.
     Stop if it differs.
  3. Follow store/WINDOWS-VALIDATION.md with fictional data: install from the
     AppX, launch from Start, exercise consent, capacity persistence, task,
     check-in, practice, crisis-plan edit, JSON/PDF export, erase, quit, and
     relaunch.
  4. Run WACK against that AppX and preserve the passing XML beside the package.
  5. Complete the keyboard-only, Narrator, high-contrast, 200% text,
     reduced-motion, minimum-window, light/dark, and modal-focus matrix in
     docs/ACCESSIBILITY.md.
  6. Record only Windows build, pass/fail, WACK report name, and date in
     revenue/METRICS.md. Never commit personal test records or key material.

## HQ-02 — Review and affirm the IARC answers — 6 minutes

- **What:** Decide whether the saved 3+/Everyone rating accurately reflects
  everything packaged, including vaulted code and text.
- **Why human-only:** IARC answers are a publisher legal/content
  representation. The app contains crisis language and a preserved optional
  self-harm urge field, so the classification should not be guessed by an
  agent.
- **Direct link:**
  <https://partner.microsoft.com/en-us/dashboard/products/9PLRSZZMFPJH/submissions/1152921505701225649/ageratings>
- **Steps:**
  1. Open the link and review the current IARC 10.3 result.
  2. Click Edit and compare each answer with the disclosures in
     store/listing-metadata.json, especially the question about inferences of or
     references to violence, blood, or gory images.
  3. Answer based on the packaged crisis/self-harm references, not merely the
     default navigation. Do not optimize for a lower rating.
  4. Save only when every answer is accurate, then record the resulting rating
     and date in revenue/METRICS.md.

## HQ-03 — Confirm seller, tax, payout, and account-role readiness — 10 minutes

- **What:** Confirm Toledo Technologies can receive paid Microsoft Store
  proceeds.
- **Why human-only:** Identity, tax attestations, banking, account roles, and KYC
  are owner-controlled legal and financial actions. No payout/tax navigation
  was visible in the current app-submission view, which may indicate a role or
  profile prerequisite.
- **Direct links:**
  <https://partner.microsoft.com/dashboard> and
  <https://partner.microsoft.com/en-us/dashboard/apps-and-games/overview>
- **Steps:**
  1. In Partner Center, open Settings → Account settings and verify the publisher
     entity matches the real Toledo Technologies account.
  2. Locate Payout and tax profiles. Complete or confirm every required profile
     and payment method; if the section is missing, verify the signed-in role or
     open Partner Center support.
  3. Confirm product 9PLRSZZMFPJH can be sold at the saved one-time price.
  4. Record only ready/not-ready, date, and any role blocker. Never put bank,
     tax, identity, or support-contact details in the repository.

## HQ-04 — Enable and verify the public support route — 3 minutes

- **What:** Enable the GitHub Issues support path already named by the release
  docs, or replace it with another channel the owner will monitor.
- **Why human-only:** Opening an inbound customer-contact channel creates an
  ongoing human support obligation.
- **Direct links:**
  <https://github.com/ntoledo319/Mindful-Organizer/settings> and
  <https://github.com/ntoledo319/Mindful-Organizer/issues/new/choose>
- **Steps:**
  1. Under repository Settings → General → Features, enable Issues.
  2. Open the new-issue link in a private window and verify that a customer can
     begin an issue. Do not submit a test issue.
  3. Put the verified URL into store/listing-metadata.json and record the check
     date. If Issues will not be monitored, choose and verify a different real
     support channel instead.

## HQ-05 — Submit for certification, then release from the manual hold — 7 minutes

- **What:** Make the final publisher declarations and start certification; after
  a pass, perform the separate Publish now action.
- **Why human-only:** Certification submission, content declarations,
  restricted-capability representation, paid pricing, and publication are
  legal/commercial commitments.
- **Blocked until:** HQ-01 through HQ-04 are complete.
- **Direct link:**
  <https://partner.microsoft.com/en-us/dashboard/products/9PLRSZZMFPJH/overview>
- **Steps:**
  1. Confirm Submission 1 still shows Pricing, Properties, Age ratings,
     Packages, and Store listings as Complete; the package must be Hearth
     1.1.0.appx and Validated.
  2. Review the saved runFullTrust explanation and Additional Testing
     Information. Confirm that no service, driver, elevation, background
     monitoring, cloud account, ads, sync, or telemetry claim has appeared.
  3. Review all URLs, $14.99 US price, screenshots, categories, IARC result, and
     the exact AppX hash.
  4. Click Submit for certification and record the timestamp/status in
     revenue/METRICS.md. If Microsoft requests a restricted-capability
     clarification, answer truthfully; do not broaden the capability claim.
  5. After certification passes, inspect the report and private product page.
     Because the draft is set to Do not publish until I select Publish now,
     click Publish now only when the page, price, support, and package are
     correct.
  6. In a private browser, verify the public page is visible and purchasable,
     then record the exact Store URL and time.

## HQ-06 — Approve and execute the first audience batch — 5 minutes

- **What:** Approve the prepared launch copy and make the minimum manual launch
  posts only after the Store page is purchasable.
- **Why human-only:** Posting as the owner or contacting real people is forbidden
  without explicit human review and action.
- **Source:** store/LAUNCH_KIT.md and store/CAMPAIGNS.md.
- **Steps:**
  1. Replace every draft link with the verified public Store URL and its
     source-specific campaign ID.
  2. Re-read each claim against the live listing and remove anything not
     demonstrable that day.
  3. Approve and manually post the smallest prepared batch to channels where the
     owner already has a legitimate account and the platform permits it. Do not
     cold-DM, scrape, automate, or manufacture engagement.
  4. Record links and timestamps in revenue/METRICS.md, then inspect Store
     acquisition data daily enough to enforce the five-day signal gate.

## Running owner-time ledger

Queued estimates: 25 + 6 + 10 + 3 + 7 + 5 = **56 minutes**, leaving 4 minutes
of reserve. No owner minutes are recorded as spent in the repository yet.

Cycle 1 used the signed-in Partner Center session to prepare the draft but did
not make the owner-only IARC change, certification declaration, publish action,
support commitment, payout attestation, or outreach. Those remain exactly the
items above.
