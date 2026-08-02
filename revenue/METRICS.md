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
