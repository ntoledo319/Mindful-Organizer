# Human Queue

> **Execution outcome — 2026-08-28T09:41-04:00:** HQ-02 and HQ-04 are complete.
> Partner Center shows tax and payment profiles Complete without any private
> values being recorded. Exact PAULATIM-001 source `f2d2a417` passed both CI
> gates; `Paulatim 1.1.1.appx` hashes to
> `af8b458149d4c00de7f02d4f4c73a4b786d14dbbd391b0db7e1750d4bf4b5146`.
> The package/listing/five screenshots were saved, the Hearth package/name were
> removed, and submission `1152921505701225649` entered certification under the
> manual publication hold. Do not repeat HQ-01, HQ-02, or HQ-04. Wait for
> Microsoft, then perform HQ-03 on the Store-signed build. A later **Publish
> now** click remains separate and is not implied by certification. Known
> remaining human-only work is at most about **27 active minutes**: HQ-03 15,
> publication/checkout 2, and optional HQ-05/HQ-06 5 each.

> **Execution correction — 2026-08-28:** the owner selected **Paulatim** and
> explicitly delegated name reservation, draft replacement, and full
> certification submission to the agent. Paulatim is reserved on product
> `9PLRSZZMFPJH` and set as dashboard name. The old Hearth submission was
> canceled to draft; Hearth cannot be deleted from app names until its Store
> listing references are removed. AMPLE-001 and all Hearth packages are
> historical/never-submit. The agent is preparing PAULATIM-001 and may execute
> the package/listing/submission clicks. Publication remains a distinct later
> action; the signed-build accessibility pass still requires real Windows
> observation after certification.

_Canonical context: root HANDOFF.md. Queue rechecked 2026-07-28: HQ-06 and
HQ-07 added; HQ-02 and HQ-05 amended._

> **Historical candidate update — 2026-08-25 (superseded 2026-08-28):** AMPLE-001 is staged at
> `tmp/AMPLE-001-3b8d225/`. Its only current AppX has SHA-256
> `7d6ca584a8cee92497217ab48fbd04153f32c8f8746b4cd19135d709aa61866b`
> (source `3b8d225`, Windows run 32844120483, artifact 9561731052); screenshots
> are artifact 9561704379. Do not upload it until the owner reserves Ample and
> reaches the package step. Never substitute CAND-002 or another artifact.

> **Current correction — 2026-08-19:** CAND-002 and every package named in the
> existing HQ-04 text are historical Hearth artifacts and must never be
> uploaded for Ample. No Ample AppX exists. HQ-00 below is now the first release
> dependency; after it lands, the agent creates and records a new exact
> candidate before any HQ-04 package action. The old renamed artifact labels
> `ample-msix`, `ample-store-screenshots`, and `Ample 1.1.0.appx` in HQ-04 do
> not describe run 30790687808, which actually produced Hearth-named artifacts.

> **Current correction — 2026-08-25:** HQ-00 is complete. With the owner's
> authorization, the agent reobserved product `9PLRSZZMFPJH` and recorded exact
> Package/Identity/Name `ToledoTechnologies.Hearth` with
> `identityVerified: true`. Manage app names showed only `Hearth`; no name was
> reserved or changed. Reserving the Ample display name remains owner-only and
> must happen before submission. The 59/50-minute estimate below was made before
> the renamed listing and AMPLE-001 upload work was counted; see the dated
> 2026-08-26 calculation for the current totals.

> **Owner-time correction — 2026-08-26:** entering/reviewing the Ample listing,
> uploading the AppX, and uploading five ordered screenshots remains an
> estimated 13-minute owner task, the separate display-name reservation is
> estimated at five minutes, the IARC runbook estimate is ten minutes, and the
> exact CI evidence narrows the non-duplicative HQ-03 human pass to 15 active
> minutes. Remaining queued work therefore totals about **79 minutes** with the
> full HQ-07 screen or **70 minutes** with its one-minute informed-risk path.
> Deferring post-live HQ-05 and optional HQ-06 reduces the remaining critical
> path to **69 minutes** or **60 minutes**, respectively. If—and only if—the
> owner independently chooses the informed-risk path and records that one-line
> decision inside the five-minute reservation batch, the estimate is **59
> remaining / 60 cumulative minutes** after conservatively counting the
> completed HQ-00 authorization. This is the sole documented within-ceiling
> path and is not an agent recommendation to waive screening.

> **Name/draft correction — 2026-08-27:** authenticated Partner Center reports
> exact `Ample` as unavailable. `Ample Energy Planner` returned available, but
> no name was reserved. The owner must choose whether to reserve that available
> fallback or select another name; the agent must not choose or reserve it.
> The draft price was independently corrected from $0 to the approved $14.99
> and saved. Do not upload AMPLE-001 or rewrite the listing until the selected
> name is reserved and appears in the product-name control.

## HQ-00 — Provide the observed Ample package identity — 1 minute

**Completed 2026-08-25 — VER-20260825-001.** The historical instructions below
are retained as the record of the former blocker.

- **What:** Send the exact **Package/Identity/Name** string already assigned by
  Partner Center for the Ample reservation.
- **Why human-only:** Name reservation and Partner Center identity observation
  are tied to the owner's account. The agent must not reserve a name or infer
  this assigned value from a naming pattern.
- **Direct link:**
  <https://partner.microsoft.com/en-us/dashboard/products/9PLRSZZMFPJH/overview>
- **Steps:** Open the product's **Product identity** page, copy only the exact
  Package/Identity/Name value, and provide it to the agent. Do not submit,
  publish, accept terms, or enter financial data as part of this step.
- **Completion evidence:** `store/identity.json` contains the observed value and
  `identityVerified: true`; a fresh CI candidate is then required.

_Owner labor ceiling: 60 minutes for the full run. Current queued total:
**60 minutes** (44 prior + 5 HQ-06 + 10 HQ-07 + 1 HQ-00; **51 minutes** if
HQ-07 is resolved by the 1-minute risk acceptance). Machine wait and Microsoft review
time are excluded. Do not add extra outreach or content work. Bet B is
deliberately not queued — the explicit either/or is D038 in
`revenue/DECISIONS.md`._

_Correction 2026-08-25: the preceding total includes the now-completed one-
minute HQ-00 and is retained as its historical calculation. Remaining queued
owner time is **59 minutes**, or **50 minutes** with HQ-07's informed-risk
path._

_Correction 2026-08-26: the preceding 59/50-minute calculation omitted the
13-minute Ample listing/package/screenshot task, the separate five-minute
display-name reservation, and the current ten-minute IARC estimate; it also
predated the exact-CI-supported 15-minute HQ-03 scope. Remaining totals are
79/70 minutes for every queued item, or 69/60 minutes when post-live HQ-05 and
optional HQ-06 are deferred. The conditional batched path above is 59 remaining
/ 60 cumulative._

_Correction 2026-08-28: the preceding calculations are historical. IARC and
name reservation are complete, while package/listing/certification submission
is now agent-delegated and consumes no further owner minutes. Known remaining
human-only active work is at most about 37 minutes if HQ-02 still needs its full
10 minutes, HQ-03 uses 15, a later publication/checkout check uses 2, and
optional HQ-05/HQ-06 use 5 each. Payout support or Microsoft waits are wall
clock, not active labor. Actual cumulative owner minutes already spent were not
reliably timed, so the repository does not invent that observation._

The exact package, five screenshots, copy, price, release hold, public support
page, privacy-guarded issue forms, security policy, private vulnerability
reporting, accurate repository metadata, audience assets, and both remote CI
gates are shipped. Only factual/legal attestations, private financial setup,
active Windows observation, certification, publication, and owner-authored
posts remain.

_Readiness correction 2026-08-28: the preceding sentence describes AMPLE-001
readiness on 2026-08-26. No exact Paulatim package, screenshots, or remote CI
gate exists yet. Public policies/support and prepared copy remain shipped;
PAULATIM-001 1.1.1 must establish the new exact evidence chain._

## HQ-01 — Retake IARC manually and accept its terms — 5 minutes

> **Completed-state correction — 2026-08-28:** the owner completed the IARC
> flow, and Partner Center subsequently showed Age ratings **Complete**. Do not
> retake or reconstruct the legal questionnaire unless Partner Center requires
> a correction; the historical preparation steps below remain evidence only.

> **Time correction — 2026-08-26:** the five-minute heading is the historical
> queue estimate. Use the later, more conservative **ten-minute** estimate in
> `store/GET-LISTED-RUNBOOK.md`; current D047 arithmetic uses ten minutes.

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

> **Completed-state correction — 2026-08-28:** Partner Center shows the tax
> profile and payment profile **Complete**. No private financial, identity, or
> banking values were copied into the repository. Do not repeat setup unless
> Microsoft later reports a specific payout blocker.

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

> **Time/scope correction — 2026-08-26:** the heading is the historical
> estimate. Exact AMPLE-001 CI already proves package structure/identity,
> first render/preload, Windows DPAPI lifecycle, export warnings, erase/recovery,
> consent gating, and five rendered scenes. Do not repeat those as separate
> exercises. Budget **15 active owner minutes**, excluding machine/install wait,
> for one combined signed-build pass: ≈2 minutes to choose/record the route and
> launch/build facts; ≈8 minutes for one keyboard+Narrator traversal covering
> consent/budget, a task, check-in, practice, crisis edit, real JSON/PDF save
> dialogs, modal focus, quit/relaunch persistence, and final erase/relaunch;
> ≈4 minutes for forced colors/high contrast, 200% text/minimum window, reduced
> motion, light/dark, and screenshot-scene presentation; ≈1 minute to record
> pass/fail. Do not budget below 15: CI does not prove Store installation or
> assistive-technology behavior.

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

### HQ-04 prerequisite — Reserve the Ample display name — ≈5 minutes

> **Completion correction — 2026-08-28:** this prerequisite is resolved under
> the owner's explicit delegation. Exact Paulatim is reserved on the existing
> product and set as dashboard name; the assigned package identity remains
> `ToledoTechnologies.Hearth`. The Ample instructions below are historical and
> non-executable.

> **Execution correction — 2026-08-27:** exact `Ample` cannot currently be
> reserved because Partner Center reports it unavailable. The available,
> unreserved fallback observed in the same product is `Ample Energy Planner`.
> The owner must make this naming decision; after choosing, reserve only the
> chosen available name and confirm it appears beside Hearth. The historical
> exact-Ample instruction below is non-executable unless availability changes.

- **What:** Add **Ample** to the existing product's reserved Store names without
  changing its observed package identity.
- **Why human-only:** Name reservation is an account-bound Partner Center action
  that the owner explicitly retained.
- **Direct link:**
  <https://partner.microsoft.com/en-us/dashboard/products/9PLRSZZMFPJH/overview>
- **Steps:** After completing HQ-07's search or recording the owner's informed
  risk decision, open **Product identity → Manage app names**, reserve
  **Ample**, and confirm it appears beside the existing Hearth name. Do not
  rewrite `ToledoTechnologies.Hearth`, create a new product, accept terms,
  submit, or publish during this step. Record only the non-sensitive outcome
  and date in `revenue/METRICS.md`.

## HQ-04 — Finalize listing, submit, then release the hold — ≈19 minutes

> **Completed-state correction — 2026-08-28:** the certification-submission
> portion is complete with exact PAULATIM-001. Partner Center contains only
> `Paulatim 1.1.1.appx` (SHA-256
> `af8b458149d4c00de7f02d4f4c73a4b786d14dbbd391b0db7e1750d4bf4b5146`) and the
> five matching screenshots; Hearth package/name references were removed;
> submission `1152921505701225649` is In certification. The title's “release the
> hold” portion remains a distinct post-certification action and has not been
> done.

> **Paulatim execution override — 2026-08-28:** every AMPLE-001 package/hash
> clause below is non-executable. Use only fresh PAULATIM-001 1.1.1 after its
> exact-SHA CI/hash record exists. The agent has explicit authority to replace
> the draft and submit for certification; publication remains separate.

> **Historical candidate — 2026-08-25 (superseded 2026-08-28):** after the owner reserves Ample and all
> preceding gates pass, use only `tmp/AMPLE-001-3b8d225/Ample 1.1.0.appx` and
> independently confirm SHA-256 `7d6ca584…61866b` before upload. This replaces
> the historical CAND-002 swap procedure below; it does not authorize the agent
> to upload, submit, certify, or publish.

> **Historical AMPLE-001 replacement procedure — 2026-08-26 (superseded 2026-08-28):** after Ample is reserved,
> HQ-01 is complete, HQ-02 is payout-ready, and the HQ-03 audience route is
> chosen, use only
> `tmp/AMPLE-001-3b8d225/Ample 1.1.0.appx`. Confirm the full SHA-256
> `7d6ca584a8cee92497217ab48fbd04153f32c8f8746b4cd19135d709aa61866b`,
> upload the five matching images in this exact Store order—`01-today`,
> `02-tasks`, `04-rhythm`, `03-reflect`, `05-onboarding`—using the captions in
> `store/SCREENSHOTS.md`, then confirm Partner Center reports the package as
> Validated. Save/review the platform-first copy, seven keywords, price,
> categories, URLs, notes, and release hold. Do not change the observed package
> identity `ToledoTechnologies.Hearth`. Stop on any filename, size, manifest,
> or hash mismatch. Estimate: **≈13 active minutes** before the existing
> ≈6-minute submission/release actions: 1 minute to hash, 1.5 for AppX
> selection/upload/validation review, 3.5 for prepared copy/features/keywords,
> 3 for ordered screenshots/captions/previews, 2 for price/market/categories/
> URLs/notes/hold, and 2 for the completeness/saved-state sweep. Passive
> transfer and Microsoft validation wait are excluded; stop rather than spend
> contingency on a mismatch.

> **Superseded package instruction — 2026-08-19:** do not execute the CAND-002
> swap paragraph or its hash checks below. They remain solely as a record of the
> pre-rename plan. HQ-04 stays blocked until the forthcoming Ample candidate and
> its new SHA-256 are added in a dated correction.

- **What:** Replace the canceled draft with exact PAULATIM-001, start Microsoft
  review under the manual publication hold, and preserve the result. Publication
  is a separate later action.
- **Authority:** The owner explicitly delegated draft replacement and full
  certification submission to the agent on 2026-08-28. That does not delegate
  private payout/tax data entry or a later **Publish now** action.
- **Blocked until:** PAULATIM-001 has an exact-SHA green CI/hash/screenshot
  evidence chain and HQ-02 readiness has been reobserved. HQ-01 is complete.
- **Direct link:**
  <https://partner.microsoft.com/en-us/dashboard/products/9PLRSZZMFPJH/overview>

> **Historical block boundary — 2026-08-26:** the CAND-002 package-swap bullet
> immediately below is retained only as the true pre-rename plan. It is
> non-executable. The AMPLE-001 replacement procedure above was the sole current
> package instruction.

- **Package swap first (CAND-002) — ≈4 min:** the 2026-07-29 remediation changed
  the app bytes, so the originally accepted AppX is superseded. Before step 1,
  replace the held Submission 1 package and screenshots with CAND-002: download
  `ample-msix` + `ample-store-screenshots` from CI run 30790687808
  (<https://github.com/ntoledo319/Mindful-Organizer/actions/runs/30790687808>),
  confirm the AppX SHA-256 is
  `a5d2cf3633def56983702d41d17f6fa458abd8dfedc818039ed1af040f36b18f`
  (full record in `store/WINDOWS-VALIDATION.md`), then upload that AppX and the
  five refreshed screenshots. **After the swap, the hash to confirm in step 1 is
  the CAND-002 hash above, not `4900f382…facdb1`.**

> **Current numbered-step override — 2026-08-26:** the package/hash clauses in
> historical step 1 below are non-executable. Current step 1 is: confirm the
> only uploaded package is `Ample 1.1.0.appx`, Partner Center marks it
> Validated, and its full SHA-256 is
> `7d6ca584a8cee92497217ab48fbd04153f32c8f8746b4cd19135d709aa61866b`.
> Step 2 must review the newly saved Ample fields and the exact screenshot order
> in the replacement procedure above. Preserve the old numbered text solely as
> Hearth history.

> **Paulatim numbered-step override — 2026-08-28:** the preceding 2026-08-26
> override and every package/hash clause in the numbered steps below are now
> non-executable. Current step 1 is to upload only the independently verified
> PAULATIM-001 1.1.1 AppX from its exact-SHA kit and confirm its full new hash;
> no such hash exists yet. Step 2 uses the prepared Paulatim fields and fresh
> screenshots, preserves the manual publication hold, and records Age ratings as
> already Complete. Step 3 is agent-authorized certification submission. Steps
> 4–6 remain post-certification/publication work; **Publish now is not authorized
> by the current submission delegation.**

- **Steps:**
  1. Confirm the package is only `Ample 1.1.0.appx`, Partner Center says
     Validated, and its source artifact SHA-256 is the accepted candidate —
     `a5d2cf36…b18f` (CAND-002) once swapped, else the prior
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

## HQ-07 — Clear the "Ample" name, or explicitly accept the risk — 10 minutes (or 1 minute)

> **Completed-state correction — 2026-08-28:** the owner rejected Ample,
> selected Paulatim, and exact Paulatim was reserved in Partner Center. D049
> records the decision. The historical Ample screening steps below are closed.

> **Screening update — 2026-08-26:** a read-only public sweep surfaced
> [Amplenote](https://www.amplenote.com/), an adjacent task, goal, mood, and
> planning product. The agent could not complete an authoritative live-status
> USPTO clearance or a reliable Microsoft Store result through the available
> read-only interfaces. Record this as **follow-up-needed**, not
> no-obvious-conflict. The owner should perform the official searches below;
> this note is neither a legal conclusion nor a reservation action.

- **What:** A minimum trademark/name collision check for "Ample" before a
  paid listing attaches money to the name — or an explicit, informed decision
  to accept the risk without searching.
- **Why human-only:** Judging which collisions matter is a legal-risk
  judgment, and accepting the risk is an owner decision. Neither path enters
  private data.
- **Direct links:** <https://tmsearch.uspto.gov/> (USPTO Trademark Search;
  the legacy TESS system was retired 2023-11-30) and
  <https://apps.microsoft.com/search?query=Ample>.
- **Steps (clearance path — 10 minutes):**
  1. On tmsearch.uspto.gov, run a basic wordmark search for **Ample**;
     filter to **live** marks and skim software-relevant classes (IC 009,
     IC 042) for anything covering productivity or wellness software.
  2. Open the Microsoft Store search link and skim whether existing apps
     already trade on "Ample" in adjacent categories.
  3. This is a spot check, not a legal opinion. If anything looks
     conflicting, stop and decide before HQ-04.
  4. Record a one-line, non-sensitive note in `revenue/METRICS.md`: date,
     what was searched, outcome (no-obvious-conflict / follow-up-needed).
- **Steps (risk-acceptance path — 1 minute):**
  1. Record in `revenue/DECISIONS.md` that you accept the name-collision
     risk for the 1.1.0 launch without a search. Nothing else changes.

## Running owner-time ledger

> **Execution calculation — 2026-08-28:** HQ-02 and HQ-04 are complete. The
> known remaining human-only maximum is about **27 active minutes**: HQ-03 15,
> later publication/checkout 2, and optional HQ-05/HQ-06 5 each. Certification
> wait time is external wall clock. Previously spent owner minutes were not
> reliably timed and are not invented here.

> **Current calculation — 2026-08-28:** IARC and Paulatim reservation are
> complete; the owner delegated package/listing/certification submission to the
> agent. Known remaining human-only work is at most about **37 active minutes**
> under the assumptions recorded above. The 2026-08-26 and earlier calculations
> below remain true historical planning records but are no longer operational.

> **Current calculation — 2026-08-26:** CAND-002 retrieval is removed, but the
> renamed listing plus AMPLE-001 AppX/five-screenshot upload is ≈13 minutes,
> the separate display-name reservation is ≈5 minutes, the current IARC
> estimate is ≈10 minutes, and the exact-CI-scoped HQ-03 pass is ≈15 active
> minutes. Remaining queued work totals **≈79 minutes** with full HQ-07
> screening or **≈70 minutes** with its one-minute informed-risk path.
> Deferring post-live HQ-05 and optional HQ-06 yields **≈69 minutes** or
> **≈60 minutes**. The old arithmetic and recommendation below are historical,
> not current instructions. Only if the owner independently chooses the risk
> path and records it inside the five-minute reservation session does that
> critical path become 59 remaining minutes; the completed HQ-00 authorization
> is conservatively the sixtieth minute.

Queued estimates: 5 + 10 + 18 + 6 + 5 + 5 + 10 = **59 minutes**, plus the
CAND-002 package swap in HQ-04 (**≈4 min**, added 2026-08-04 after the candidate
landed to main, D040) → **≈63 minutes** at the full HQ-07 clearance path (just
over the 60-min §10 ceiling), or **≈54 minutes** with the HQ-07 1-minute
risk-acceptance path (within ceiling). **Recommended: take the HQ-07 risk-accept
path to stay in budget.** No owner minutes are recorded as spent in the
repository yet.

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
