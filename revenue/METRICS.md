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

- Remote main was observed at
  `4a32b7306ab9ca76a09fb3fae399649c07543e5a`; Quality run 29346492274 passed.
- Root `HANDOFF.md` was prepared from all six revenue files, current public main,
  Store/release/support/audience sources, and three independent specialist
  audits.
- Partner Center private state was not refreshed and remains explicitly dated
  2026-07-14.
- Local shell execution was unavailable: even `pwd` and `true` exited 137 with
  no output. Therefore local branch cleanliness, sync and jailed artifact
  presence are not newly observed. A future agent must reverify them.
- No revenue, listing, certification, publication, post or human contact was
  observed during this documentation cycle. Collected remains $0; gap $4,000.

## 2026-07-24 — Host move, drift discovery, local verification restored

- Workspace observed at `/home/nick/Development/active/mindful_organizer`
  (Linux); `revenue/PLAN.md` line 1 corrected to match (AGENTS.md §1 law).
- The 2026-07-15 exit-137 local-shell failure does not reproduce on this host;
  commands ran normally all session. This entry satisfies the cycle-3
  requirement to record a successful local-shell verification.
- `git fetch` + `ls-remote`: `origin/main` advanced `4a32b73` → `e0fc9e0`
  (cycle-3 handoff published remotely 2026-07-15). The uncommitted local
  working tree is the pre-publication draft of that content (all 9 files
  differ in wording); it is preserved in the working tree and archived, and
  reconciliation is queued (`PROJECT_TRACKER.md` RECON-001 / PROP-001). No
  destructive git action was taken.
- First vitest attempt failed because `node_modules` carried macOS native
  builds from the previous host (missing `@rollup/rollup-linux-x64-gnu`).
  Repaired with locked `npm ci` using in-jail caches; no global installs.
  Electron binary and 3 install-script approvals remain pending on this host,
  so packaging and `npm run dev` are not yet verified here.
- Local gates green on the dirty working tree (docs/state changes only, no
  product-code change): secret scan 181 files; Store validation 269 checks;
  both TypeScript projects; 9 test files / 30 tests; project-docs validator
  PASS. Detail: `docs/project/VERIFICATION_LOG.md` VER-20260724-001…005.
- Project documentation control system established: `PROJECT_TRACKER.md` plus
  `docs/project/` (index, history, verification, proposals, migration map,
  archive, commit index). See `docs/project/REPO_HISTORY.md`
  HIST-20260724-001…003.
- No revenue, listing, certification, publication, post, or human contact was
  observed. Collected profit remains **$0.00**; the gap remains **$4,000.00**.
