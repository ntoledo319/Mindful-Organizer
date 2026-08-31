# Evidence Ledger

Only observed evidence belongs here. Forecasts and target arithmetic live in
PLAN.md and OPPORTUNITIES.md.

## 2026-07-14 — Money and market baseline

| Metric | Observed value | Evidence |
|---|---:|---|
| Partner Center earnings | **$0.00** | Signed-in Earnings workspace observed in Cycle 2; no data for the selected period |
| Collected profit recorded | **$0.00** | No sale, payout, refund, fee, or settlement record observed |
| Gap to target | **$4,000.00** | $4,000 target minus $0 collected |
| Live paid listing | 0 | Product is In draft; no public purchasable Store page verified |
| Product-page views | Not observed | Draft state has no live acquisition funnel |
| Acquisitions or installs | Not observed | No live submission |
| Signups | Not applicable | Hearth has no account system |
| Public GitHub stars | 0 | Repository metadata observed during Cycle 0 |
| Public GitHub forks | 0 | Repository metadata observed during Cycle 0 |
| Production dependency vulnerabilities | 0 | Production npm audit |

## 2026-07-14 — Accepted source candidate

- Candidate source commit:
  8172603b62c2457696608c145511bd3fe92429d4
- Candidate application tree:
  d731d4de78529435c5cc1e0a036536701cc737e9
- **Quality run 29322423682 passed** locked installation, lint, both TypeScript
  projects, 9 test files / 30 tests, renderer and Electron builds, store
  validation, license generation, production audit, secret scan, and diff/YAML
  checks:
  <https://github.com/ntoledo319/Mindful-Organizer/actions/runs/29322423682>
- **Windows Store run 29322423622 passed** package generation, MakeAppx
  semantic validation, exact-candidate screenshot capture, and the
  sentinel-guarded safeStorage/DPAPI lifecycle proof:
  <https://github.com/ntoledo319/Mindful-Organizer/actions/runs/29322423622>
- Automated lifecycle coverage observed as passing: fresh encrypted
  persistence, plaintext export warning, corrupt-primary backup recovery,
  key-first erase and reinitialization, interrupted-erase resume, representative
  legacy migration with consent/remnant retirement, and missing-key fail closed.
- Local verification also passed lint, typecheck, all 30 tests, both builds,
  store validation with 246 checks, production audit with zero vulnerabilities,
  a 155-path secret scan, and diff checks.
- Local screenshot execution was intentionally not used because safeStorage on
  macOS would involve OS key storage outside the workspace jail. Hosted Windows
  evidence is authoritative.

## 2026-07-14 — Exact AppX evidence

| Field | Observed value |
|---|---|
| Filename | Hearth 1.1.0.appx |
| AppX size | 175,488,515 bytes |
| AppX SHA-256 | 4900f3823febace53f86f69ee2567b50208aec8f6677741c3c4dcf3667facdb1 |
| Local jailed copy | tmp/artifacts/final-msix/Hearth 1.1.0.appx |
| GitHub artifact name / ID | hearth-msix / 8306541856 |
| Artifact archive size | 174,530,350 bytes |
| Artifact digest | sha256:4d5885c705cf6429e83ef3404135d6448ffdb903b0df8cd75e5fbf02d7d8a494 |
| Artifact expiry | 2026-08-13 |
| Partner Center result | Validated; x64; Windows Desktop minimum 10.0.14316.0 |

The exact accepted AppX is an unsigned Store-submission file with no
`AppxSignature.p7x`; locally signing it would change its bytes and hash. Passing
generation, lifecycle automation, and Partner validation do not prove Microsoft
certification, a Store-signed human smoke/accessibility pass, or publication.

## 2026-07-14 — Exact screenshot evidence

- Artifact ID: 8306519500
- Artifact digest:
  sha256:b03e6e42b771da7f693575d79473275e90723adbeea23801d08f8de380e7c905
- Candidate reference:
  8172603b62c2457696608c145511bd3fe92429d4
- All five PNGs are 1920 × 1080, use deterministic fictional demo data, passed
  visual review, and were uploaded to the Partner Center draft in the documented
  order with matching captions.

| File | SHA-256 |
|---|---|
| 01-today.png | e1294c9c6bf869cc13e903932feac540da9122f46af40aa2d776a24ce2d64979 |
| 02-tasks.png | 67708bf4165b4cc9e8be027dfdc3342b33b3b76b84dcd3a983b6573cfdd153af |
| 04-rhythm.png | 208e9cca284fec8bf284706f670f698a5e5cd64dc497bea7cbbbc16afb40c483 |
| 03-reflect.png | 76e3888e666f2a9f3ed9effc7cc15072621551259274b98ac31723bfb3db93cc |
| 05-onboarding.png | 6f49b190a72913d32a83c3e8f2f4f6bb4812a1938a2cf1c051b0372abbbffe99 |

## 2026-07-14 — Partner Center draft evidence

- Product: Hearth, product ID 9PLRSZZMFPJH.
- Submission: 1152921505701225649, displayed as Submission 1.
- Product state: **In draft**.
- Pricing and availability: **Complete** — $14.99 USD one-time, United States
  only, public and discoverable, no trial or sale, publish after a separate
  manual action.
- Properties: **Complete** — Productivity primary, Health + fitness secondary,
  personal-information declaration saved.
- Age ratings: current saved result IARC 3+ / ESRB Everyone, IARC 10.3. It is not
  accepted as accurate against packaged crisis/self-harm and
  medication-reference content. A Cycle 2 source audit produced a conservative
  manual answer guide, but no automated questionnaire result was saved after
  IARC's automation prohibition was identified.
- Packages: **Complete** — only Hearth 1.1.0.appx remains in the draft and is
  marked Validated.
- Store listings: **Complete** — final truthful description, eight features,
  short description, seven keywords, copyright, and five exact screenshots.
- Submission options: **Incomplete** in Partner Center. The runFullTrust
  explanation and Additional Testing Information are saved; restricted
  capability review is expected during certification.
- Submit for certification: **enabled but not clicked**.
- Release control: **Do not publish until I select Publish now** is saved.

## 2026-07-14 — Cycle 2 support and audience evidence

- Repository Settings → General showed Issues enabled with creation allowed by
  all users. Repository- and account-level interaction limits were disabled.
- Authenticated issue creation exposed Bug report, Feature request, and blank
  issue options before the unsafe legacy templates were replaced. Signed-out
  issue creation requires GitHub sign-in.
- New local issue forms parse as YAML, disable blank issues, use only `bug` and
  `enhancement` labels, and prohibit databases, snapshots, keys, plaintext
  exports, personal records, and identifying screenshots.
- A public support page, security policy, and private vulnerability-reporting
  link were prepared for main. No issue, message, post, or customer commitment
  was created.
- Three accepted-candidate screenshots were copied only after their source
  build reference and SHA-256 values matched the accepted manifest. The landing
  product tour was visually inspected at 1440 px and 390 px; images loaded at
  their natural 1920 × 1080 size.

## 2026-07-14 — Cycle 2 local verification

- GitHub form YAML: 3 files parsed.
- Store identity check: true.
- Store validator: **263 checks passed**.
- ESLint: passed with zero warnings.
- TypeScript: renderer and Electron projects passed.
- Vitest: **9 files / 30 tests passed**.
- Renderer and Electron production builds: passed.
- Secret scan: **160 readable files passed**. The scanner was repaired to skip
  tracked paths deleted in the working tree instead of crashing before it
  scanned remaining files.
- Third-party notices regenerated for **54 runtime packages**.
- Deterministic brand assets regenerated without a source change.

## 2026-07-14 — Cycle 2 seller-account evidence

- My access showed Apps and games, Insights, and Earnings access granted.
- The signed-in Earnings workspace showed $0.00 payments and no earnings data
  for the current filter period.
- Account settings did not expose a Payout and tax section. Official Microsoft
  guidance says Store/Marketplace payout setup requires the appropriate Owner
  or Financial contributor context and assigned tax and payout profiles.
- No bank, tax, KYC, identity, or private account detail was entered or recorded
  in the workspace.

## 2026-07-14 — Cycle 2 remote publication evidence

- GitHub main commit:
  `d01c013fd8beec91014c37d27a9a310cf5dd0470` — 35 files, 1,031 additions,
  463 deletions.
- Quality Gate run 29345864617: **passed**.
- Windows Store run 29345863949: **passed** in 4m57s, including secret scan,
  Store/listing validation, identity, deterministic assets, license and
  production-dependency audits, lint, both typechecks, 30 tests, native rebuild,
  both production builds, screenshot capture, AppX packaging, payload
  validation, and artifact upload.
- Verification-only AppX artifact 8316167277: 175,488,400 bytes; extracted AppX
  SHA-256
  `93279f430e024deb3b28ee12d98271ffa19d7093f8d9e667e7c9defcace2fc10`.
  Screenshot artifact: 8316137548. These do not replace the exact AppX already
  validated in Partner Center; the published changes did not change product
  runtime code.
- The public SUPPORT page and SECURITY policy resolve signed out. The issue
  chooser redirects signed-out visitors to GitHub authentication as disclosed.
- Repository description and eight topics were saved; private vulnerability
  reporting is enabled. No issue, release, post, listing, or human contact was
  created.

## Current not-observed list

Store-signed installed behavior, Windows Narrator/high-contrast/text-scaling
results, owner-approved IARC answers, seller tax/payout readiness, Microsoft
certification, public listing visibility, product-page traffic, purchases,
refunds, fees, and payouts remain unobserved. The attempted Lighthouse run was
terminated without usable audit results and is not counted as evidence.

Collected profit remains **$0.00**. The current gap remains **$4,000.00**.

## 2026-07-15 — Cycle 3 handoff evidence

- Remote main before the handoff was 4a32b7306ab9ca76a09fb3fae399649c07543e5a; Quality run 29346492274 passed.
- Root HANDOFF.md was published at commit 0ff209e273c3111c2db619d83a5f80372f89bd55 after review of all six revenue files, current public main, Store/release/support/audience sources and three specialist audits.
- Partner Center private state was not refreshed and remains dated 2026-07-14.
- Local shell execution was unavailable: even pwd and true exited 137. Local branch cleanliness, sync and jailed artifact presence are therefore not newly observed.
- No listing, certification, publication, post, human contact or revenue was observed. Collected remains $0.00; gap remains $4,000.00.


## 2026-07-24 — Host move, drift discovery, local verification restored

- Workspace observed at `/home/nick/Development/active/mindful_organizer`
  (Linux); `revenue/PLAN.md` line 1 corrected to match (AGENTS.md §1 law).
- The 2026-07-15 exit-137 local-shell failure does not reproduce on this host;
  commands ran normally all session. This entry satisfies the cycle-3
  requirement to record a successful local-shell verification.
- `git fetch` + `ls-remote`: `origin/main` advanced `4a32b73` → `e0fc9e0`
  (cycle-3 handoff published remotely 2026-07-15). The uncommitted local
  working tree was the pre-publication draft of that content; it was committed
  as `d1c9d91` and reconciled with the published iteration by merge (see
  `docs/project/REPO_HISTORY.md` HIST-20260724-004…006).
- First vitest attempt failed because `node_modules` carried macOS native
  builds from the previous host (missing `@rollup/rollup-linux-x64-gnu`).
  Repaired with locked `npm ci` using in-jail caches; no global installs.
  Electron binary and 3 install-script approvals remain pending on this host,
  so packaging and `npm run dev` are not yet verified here.
- Local gates green: secret scan 181 files; Store validation 269 checks; both
  TypeScript projects; 9 test files / 30 tests; project-docs validator PASS.
  Detail: `docs/project/VERIFICATION_LOG.md` VER-20260724-001…006.
- Project documentation control system established: `PROJECT_TRACKER.md` plus
  `docs/project/` (index, history, verification, proposals, migration map,
  archive, commit index).
- No revenue, listing, certification, publication, post, or human contact was
  observed. Collected profit remains **$0.00**; the gap remains **$4,000.00**.

## 2026-07-28 — Day 15 gate assessment (covers the missed Day 7 and Day 14 gates)

Observed facts:

| Metric | Observed value | Evidence |
|---|---:|---|
| Collected profit | **$0.00** | No sale, payout, refund, fee, or settlement record observed; no live listing exists to produce one |
| Accrued net earnings | **$0.00** | No sales exist; nothing has accrued |
| Gap to target | **$4,000.00** | $4,000 target minus $0 collected |
| Live paid listing | 0 | Product remains In draft; no public purchasable Store page verified |
| Owner queue consumption | 0 of 44 queued minutes | No HQ item recorded as executed in the repository since 2026-07-15 |
| §8 gate assessments | 0 performed | No ledger entries exist for Day 7 (2026-07-20) or Day 14 (2026-07-27); this entry executes both late |

Planning analysis (clearly labeled assumptions, not observations):

- **Live-window math.** If the owner completes HQ-01/HQ-02 today (Day 15)
  and certification is submitted immediately after, Microsoft certification
  takes roughly 1–7 days, so the listing goes live around Day 17–23 —
  leaving roughly **4–11 live days** before Day 28 (2026-08-10). The
  falsifier cycle needs a minimum of 9 live days (5 + one reposition + 4),
  so at the short end the full reposition-replace cycle cannot complete even
  once.
- **Required velocity.** At the revised 322–335-sale model (revenue/PLAN.md,
  blended fee plus refund planning assumptions), closing the gap needs
  roughly **29–84 sales per live day** (≈ 26–78/day under the pre-revision
  314 baseline) from a zero-review, US-only, $14.99, no-trial listing, with
  $0 spend and zero owned audience. `revenue/OPPORTUNITIES.md`'s own planning
  range for this frame is U = $0–$4,001; the honest reading of that floor is
  that this velocity is **not plausible**.
- **Payout timing.** ADA v8.11 §6(c) pays monthly, subject to the USD $50
  threshold; August sales pay out mid-August at the earliest, realistically
  mid-September — after Day 28. Bet A dollars are accrued-not-collected
  in-window.

Gate conclusion: **the $4,000 collected-cash target is not reachable
in-window through Bet A.** The §8 escalation executed today: (a) all
agent-doable distribution prep shipped (reposition menu in `revenue/PLAN.md`,
`store/REPOSITION_KIT.md`, `store/LAUNCH_TARGETS.md`, HQ-05 wiring); (b) the
Bet B sequencing decision put to the owner as an explicit either/or (D038);
(c) the Day-28 success criterion restated in `revenue/PLAN.md` as live
listing + first collected dollars + real demand signal. Decision records:
D035–D039. The Day-21 gate (2026-08-03) executes on schedule.

Collected profit remains **$0.00**. The current gap remains **$4,000.00**.

## 2026-08-04 — CAND-002 landed; gates re-verified

- **Code:** the CAND-002 replacement-candidate cycle was fast-forwarded to
  `origin/main` (`246baac`→`07d938c`, D040). Re-verified on the clean commit:
  lint 0, typecheck ×2 0, 12 files / 46 tests, renderer vite build, secrets 189
  files, store identity ✓, store validation 276 checks, docs validator PASS
  (VER-20260804-001).
- **Windows package:** CI Windows Store MSIX run 30790687808 green (3m16s);
  artifacts `hearth-msix` (AppX `a5d2cf36…`, 175,489,287 B) + refreshed
  `hearth-store-screenshots`. This is the CAND-002 candidate, **not yet the
  accepted Partner Center package** — the swap is owner action HQ-04.
- **Money: unchanged.** Collected profit **$0.00**, gap **$4,000.00**, 0 live
  listings. The Day-21 conclusion stands: with monthly ADA §6(c) payout timing,
  in-window *collected* cash by Day 28 remains implausible; landing CAND-002
  only makes the product submit-ready. All that now blocks a live listing is the
  owner-only HQ queue.

## 2026-08-07 — Independent reverification; market/pricing re-derivation

- **Verification (VER-20260807-001).** The 2026-08-04 handoff was reverified
  against `git`, the GitHub API, and a full local gate run under owner
  direction. Confirmed accurate: CI runs 30891743797, 30891744008, 30790687808
  all green; lint/typecheck/build/secrets(189)/store(276) exact; **CAND-002 AppX
  hash independently recomputed as `a5d2cf36…b18f` — matches**. `npm audit
  --omit=dev`: 0 vulnerabilities.
- **Corrections.** `origin/main` is `37feea1` (HANDOFF said `270e650`, the
  tracker said `07d938c`). HANDOFF §7's "uncommitted cycle-3 draft" no longer
  exists. Tracker blockers B2/R4 were live five days after resolution. "All
  local gates green" was not reproducible — `better-sqlite3` carried the
  Electron ABI and failed 16/46 tests locally (environmental; 46/46 after
  `npm rebuild better-sqlite3`). `store/WINDOWS-VALIDATION.md` claimed Partner
  Center marked the CAND-002 AppX Validated; that contradicts HQ-04 and has been
  retracted.
- **New risk recorded (R5).** Previously undocumented MSIX artifact 8885413072
  (run 30891744008, `270e650`), AppX `368b0eeb…e7b1` — the newest build in the
  Actions list and within 124 bytes of CAND-002. Now named as never-submit in
  HANDOFF §4 and `store/WINDOWS-VALIDATION.md`. The correct package and the five
  screenshots are staged at `tmp/CAND-002-SWAP/`.
- **Owner-time re-estimate.** ≈50–60 minutes of clicking is roughly right, but
  the figure omits the three things that control the date: HQ-02's missing
  payout role may need a multi-day Partner Center support ticket; HQ-03 needs an
  x64 Windows machine that is nowhere established to exist; certification is
  days of wall-clock. Expect at least three sessions.
- **Market/pricing.** First comparable set recorded:
  `revenue/MARKET-ANALYSIS-2026-08-07.md`. Microsoft's 15% app fee confirmed
  against Microsoft Learn (own-commerce 0% path exists but is incompatible with
  the no-network product claim). The ADHD-planner category is subscription-based
  and mobile/Apple-dominated at roughly $2.49–$22/month; **$14.99 one-time is
  the cheapest serious option in the category, not an expensive one.** Price
  recommended unchanged — not because it is optimal, but because demand, not
  price, is the binding constraint and there is still zero demand data.
  Positioning finding raised as a proposal, not a change.
- **Money: unchanged.** Collected profit **$0.00**, gap **$4,000.00**, 0 live
  listings, 0 owner minutes spent. Day 28 is 2026-08-10 and nothing is
  submitted. No owner-only action was taken this session: nothing submitted,
  published, attested, priced, or connected to payment.

## 2026-08-07 — HQ-07 name check executed (agent research; owner judgment still required)

HQ-07 steps 1–2 are public research, not a legal judgment, so they were run by
the agent. **Outcome: follow-up-needed, not no-obvious-conflict.**

Searched 2026-08-07 via public trademark mirrors and open web. Not USPTO
tmsearch directly, and **not a legal opinion** — the agent is not a lawyer and
third-party mirrors carry stale status data.

**Material finding — HEARTH DISPLAY / Hearth Display, Inc.**

- USPTO serial **97524800**, word mark HEARTH DISPLAY, filed 2022-07-28.
  IC 009 covers *downloadable and recorded software for use in family and
  household management and productivity, calendaring and scheduling, routine
  building, and task delegation and reporting*; IC 042 covers the
  non-downloadable equivalent. Status as mirrored: 630 (new application) —
  **stale, must be rechecked on tmsearch.uspto.gov**.
- Corresponding WIPO filing 1716122 (2023-01-27), owner Hearth Display, Inc.,
  Brooklyn NY.
- The company is real, funded, founded 2020, and **markets under "Hearth"
  alone** — its own materials describe Hearth as a tool for family management
  and productivity, with calendars, routines, to-dos, task assignment, and a
  subscription tier.

**Why this matters:** this is not an adjacent industry with a coincidentally
similar name. It is the same short word, used as a standalone brand, by a
funded company, over goods in the same International Classes and arguably the
same description of goods — household/personal organization, routines, task
management software.

**Non-material:** HEARTH BY DESIGN (reg. 5415274) is registered but covers
fireplace-configuration software and **disclaims "HEARTH"**. HEARTHMATES,
HEARTHMATCH, HEARTH TIME, HEARTH-AID, HEARTH FLO are unrelated goods
(roommate matching, hearth-product installation, fire pits, stoves).

**Recommendation:** the queue's suggested 1-minute risk-accept path is no longer
the appropriate default. Attaching a paid listing to this name without at least
rechecking 97524800's current status on tmsearch.uspto.gov is a materially
different decision than it was when HQ-07 was written with no search behind it.
Options are the owner's: proceed with informed risk acceptance, recheck status
first, seek actual counsel, or rename before the listing is live — renaming
costs far less now than after a purchasable page exists.

Microsoft Store name-collision search (HQ-07 step 2) not yet run.

## 2026-08-19 — Ample rename state independently re-derived

- Live `git` observation: checked-out
  `feature/store-candidate-cand002`, `origin/main`, and
  `origin/feature/store-candidate-cand002` all pointed to `c0eb360`; local
  `main` remained `c2b1fc2` (33 behind). `stash@{0}` remained intact.
- Live GitHub observation: Quality runs 32310869115 (main) and 32310866310
  (feature) failed because regenerated third-party notices changed two Hearth
  references to Ample. Windows runs 32310869046 (main) and 32310866359
  (feature) failed when the screenshot launcher timed out after exporting the
  obsolete `HEARTH_*` harness variables. Both Windows runs produced **zero
  artifacts**.
- Safety finding: committed `store/identity.cjs` ignored
  `identityVerified: false` and reported the guessed rename identity ready.
  Packaging did not occur only because screenshot capture failed first. The
  local correction now reports false and rejects the Store-build preflight.
- Candidate state: **no Ample AppX exists**. CAND-002
  (`a5d2cf36…b18f`) and all other recorded packages are historical Hearth
  artifacts and never-submit after the manifest rename.
- Local prep: platform-first listing copy and seven revised keywords are edited
  in the working tree but are not saved in Partner Center. Non-package checks
  passed: lint 0; typecheck ×2; 14 test files / 49 tests; renderer + Electron
  bundle build; secrets 197 files; Store validation 278 checks; project-docs
  validator; production audit 0 vulnerabilities; deterministic brand assets;
  third-party notices for 54 runtime packages. A package was deliberately not
  built because the Partner Center identity remains unobserved.
- Money and publication are unchanged: collected profit **$0.00**, gap
  **$4,000.00**, 0 live listings, 0 Ample artifacts, and no submission,
  certification, publication, payout setup, or owner-authored contact.

## 2026-08-25 — Partner Center identity reobserved

- Live `git`/GitHub state had not moved: checked-out
  `feature/store-candidate-cand002`, `origin/main`, and the remote feature ref
  remained at `c0eb360`; the prior Quality and Windows failures still had zero
  artifacts, and `stash@{0}` remained intact.
- With owner authorization, authenticated Partner Center product
  `9PLRSZZMFPJH` was inspected. Product identity reports exact
  Package/Identity/Name `ToledoTechnologies.Hearth`, publisher
  `CN=FBC80173-0C85-481E-BC5E-A3BE88BC2020`, and publisher display name
  `Toledo Technologies`.
- Manage app names reports `Hearth` as the only name currently in use. No name
  was reserved or changed. The submission remains a draft/not submitted, and
  the package shown there remains the historical Hearth AppX.
- `store/identity.json` now records the observed identity with
  `identityVerified: true`; both `npm run store:check` and
  `npm run store:require-verified` passed. This clears the package-build
  identity gate but not the separate owner-only Ample display-name reservation,
  IARC, payout/tax, submission, certification, or publication gates.
- Money and publication remain unchanged: collected profit **$0.00**, gap
  **$4,000.00**, 0 live listings, and nothing submitted, certified, published,
  or purchasable.

## 2026-08-25 — AMPLE-001 exact candidate produced

- Exact remote source `3b8d225c1ce32be04a7940099649789876d1e353`
  (tree `cfb17be0c06e456beb9bcf54ec2e211eb0085a5b`) passed Quality run
  32844120492 and Windows run 32844120483.
- Artifact `ample-msix` 9561731052 contains `Ample 1.1.0.appx`, 175,489,305
  bytes. Independent `sha256sum` produced
  `7d6ca584a8cee92497217ab48fbd04153f32c8f8746b4cd19135d709aa61866b`,
  exactly matching CI's hash file.
- The AppX manifest independently confirms package identity
  `ToledoTechnologies.Hearth`, publisher
  `CN=FBC80173-0C85-481E-BC5E-A3BE88BC2020`, display name `Ample`, x64, and
  version `1.1.0.0`. The Windows DPAPI lifecycle report passed.
- Screenshot artifact 9561704379 contains five 1920×1080 PNGs bound to exact
  source `3b8d225`; all five hashes match its manifest. The preserved artifact
  ZIP hashes to `06f74a6e…dbfe65`.
- The exact kit is staged at `tmp/AMPLE-001-3b8d225/`. No Partner Center
  package upload, display-name reservation, IARC action, payout/tax action,
  submission, certification, publication, or live listing occurred.
- Money remains unchanged: collected profit **$0.00**, gap **$4,000.00**, 0
  sales, and 0 live purchasable listings.

## 2026-08-26 — Post-candidate continuation revalidation

- Live `git`/GitHub observation before this documentation-only close:
  local `main` and `origin/main` both pointed to `13bdea2`; its Quality run
  32845727178 passed. Exact candidate source `3b8d225` still has green Quality
  32844120492 and Windows 32844120483; no Windows run exists for `13bdea2`.
- Artifacts 9561731052 (`ample-msix`) and 9561704379
  (`ample-store-screenshots`) remain available and bound to candidate source
  `3b8d225`. No replacement artifact was selected or created.
- The staged AppX independently recomputed to
  `7d6ca584a8cee92497217ab48fbd04153f32c8f8746b4cd19135d709aa61866b`;
  the preserved screenshots ZIP recomputed to
  `06f74a6e2d68b3b53b0b5ed73b8ffbdb5808cb61fe8178d4884a00e924dbfe65`,
  and all five PNG hashes still match the exact-SHA manifest.
- A signed-out Store-product check still returned ProductNotFound/410, so no
  live listing or purchase path exists.
- A public name screen surfaced [Amplenote](https://www.amplenote.com/), an
  adjacent productivity/task/mood-planning product. The agent interfaces did
  not yield an authoritative live-status USPTO clearance or reliable Microsoft
  Store search result. HQ-07 therefore remains **follow-up-needed** for the
  owner's official searches and legal-risk judgment; no name was reserved or
  changed.
- No package upload, IARC interaction, payout/tax action, terms acceptance,
  submission, certification, publication, post, or human contact occurred.
  Collected profit remains **$0.00**; the gap remains **$4,000.00**.

## 2026-08-27 — Partner Center draft intervention

- Authenticated Partner Center product `9PLRSZZMFPJH`, submission
  `1152921505701225649`, remains **In draft**. No certification or publication
  action was taken.
- **Manage app names:** exact `Ample` returned **not available**. `Ample Energy
  Planner` returned available (green availability result), but it was not
  reserved because the owner retained the reservation and naming decision.
  `Hearth` remains the only reserved/in-use name.
- **Pricing and availability:** the held draft was observed at **$0** despite
  older Hearth-era records. The already approved one-time US price was changed
  to **$14.99** and saved; Partner Center returned to the application overview
  with Pricing and availability still Complete and displayed the expected
  warning that tax and payout information must be updated before charging
  money. No tax or payout data was opened or entered.
- **Properties:** Productivity primary, Health + fitness secondary, and the
  repository privacy-policy URL were reobserved. Unsupported product,
  accessibility, AI, and hardware declarations remained unchecked; no
  Properties change was saved.
- The package remains the historical validated `Hearth 1.1.0.appx`. AMPLE-001,
  its five screenshots, and the platform-first listing fields were not
  uploaded or saved. No IARC, terms, submission, certification, publication,
  contact, or human-authored post occurred.
- Collected profit remains **$0.00**; the gap remains **$4,000.00**.

## 2026-08-28 — Paulatim reservation and draft reset

- The owner selected **Paulatim** and explicitly authorized its reservation,
  replacement Store draft, certification submission, and removal of Hearth
  listing/name references.
- On existing Partner Center product `9PLRSZZMFPJH`, exact `Paulatim` returned
  available and was reserved. It was then set as the dashboard name. The
  Microsoft-assigned package identity remains `ToledoTechnologies.Hearth`.
- The earlier Hearth submission had entered certification and was canceled;
  the application returned to **In draft** before the Paulatim rename. The
  overview showed Age ratings Complete after the owner-completed IARC flow, but
  questionnaire answers were not reconstructed or silently changed.
- Partner Center would not delete `Hearth` while the Store listing still
  referenced it. Removal is deferred until the historical package/listing is
  replaced by the exact Paulatim candidate.
- No Paulatim AppX, screenshot artifact, package hash, certification result,
  publication, live listing, purchase, or external revenue exists yet.
  Collected profit remains **$0.00**; the gap remains **$4,000.00**.

## 2026-08-28 — Exact Paulatim candidate and certification submission

- Exact source `f2d2a4177fcb05d5b24405c598d0eb9b9d7f01e6` (tree
  `320490a5cfc1d5e409e8ce0ea2fb05147dc97e4d`) passed Quality run 33169087812
  and Windows Store run 33169087811.
- Artifact `paulatim-msix` 9684903207 contains `Paulatim 1.1.1.appx`,
  175,489,702 bytes. Independent SHA-256 is
  `af8b458149d4c00de7f02d4f4c73a4b786d14dbbd391b0db7e1750d4bf4b5146`, matching
  CI's checksum. Artifact `paulatim-store-screenshots` 9684887490 has digest
  `a4bc6785dfc0bc08317239ecd06b1ce126a24674766852cb4aeeb4d630045e50`; all five
  1920×1080 PNG hashes match the exact-source manifest.
- Manifest inspection confirms identity `ToledoTechnologies.Hearth`, publisher
  `CN=FBC80173-0C85-481E-BC5E-A3BE88BC2020`, x64, version `1.1.1.0`, stable
  application ID `Ample`, visible name `Paulatim`, and executable
  `app\Paulatim.exe`. The exact kit is `tmp/PAULATIM-001-f2d2a41/`.
- Partner Center product `9PLRSZZMFPJH` contains only the Paulatim package and
  five matching screenshots. The platform-first listing, Additional Testing
  Info, and manual release control were saved. The Hearth package and Hearth
  display-name reservation were removed. Age ratings, tax profile, and payment
  profile show Complete.
- Submission `1152921505701225649` entered **In certification** at
  Pre-processing. Partner Center states publishing begins only when **Publish
  now** is clicked; that hold was not released. This is not certification,
  publication, live visibility, purchase, or revenue evidence.
- Collected profit remains **$0.00**; gap remains **$4,000.00**; observed live
  listings, product-page traffic, purchases, acquisitions, and payouts remain 0.

## 2026-08-31 — Paulatim certification and public release

- Partner Center showed exact submission `1152921505701225649` **Ready to
  publish** with every certification stage green and only
  `Paulatim 1.1.1.appx` in the package section. The exact release candidate
  remains PAULATIM-001 from source `f2d2a417`, 175,489,702 bytes, SHA-256
  `af8b458149d4c00de7f02d4f4c73a4b786d14dbbd391b0db7e1750d4bf4b5146`.
- Under the owner's explicit publication direction, **Publish now** was
  executed. Partner Center moved to **In publishing** and stated that the
  certified product had started publishing.
- At approximately 2026-08-31 08:56 EDT, the canonical signed-out page resolved
  publicly at <https://apps.microsoft.com/detail/9PLRSZZMFPJH> with title
  Paulatim, publisher Toledo Technologies, Productivity category, the
  Windows-first short description, Paulatim screenshots, and ESRB Everyone
  10+ / Violent References.
- Microsoft's live catalog returned product ID `9PLRSZZMFPJH`, a USD $14.99
  price/list price, a `Purchase` action, nine image records, and release
  timestamp `2026-08-31T12:47:05.3548026Z`. This proves a public purchase path;
  it does not prove a completed customer transaction.
- The signed-out page exposed `https://toledotechnologies.com/` as both the
  publisher website and `SupportUri`. That generic studio page is not the
  intended Paulatim support page (`docs/SUPPORT.md`); the live-field mismatch
  is recorded as follow-up, not silently represented as correct.
- Physical-Windows installation, installed footprint, keyboard, Narrator,
  forced-colors, 200% scaling, reduced-motion, and modal-focus checks remain
  unobserved under HQ-03. No accessibility declaration is claimed.
- Observed product-page views, acquisitions, completed purchases, refunds,
  accrued proceeds, payouts, and collected profit remain **unobserved / $0.00**.
  Gap to the collected-profit target remains **$4,000.00**. The five-day signal
  clock begins 2026-08-31.
