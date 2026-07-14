# Evidence Ledger

Only observed evidence belongs here. Forecasts and target arithmetic live in
PLAN.md and OPPORTUNITIES.md.

## 2026-07-14 — Money and market baseline

| Metric | Observed value | Evidence |
|---|---:|---|
| Partner Center earnings | **$0.00** | Signed-in Hearth overview observed this cycle |
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

Passing generation, lifecycle automation, and Partner validation do not prove an
installed-package smoke test, WACK pass, certification, or publication.

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
- Age ratings: **Complete** — current saved result IARC 3+ / ESRB Everyone,
  IARC 10.3. An exploratory questionnaire change was canceled without saving;
  the result still requires owner review against the packaged crisis and
  self-harm references.
- Packages: **Complete** — only Hearth 1.1.0.appx remains in the draft and is
  marked Validated.
- Store listings: **Complete** — final truthful description, eight features,
  short description, seven keywords, copyright, and five exact screenshots.
- Submission options: **Incomplete** in Partner Center. The runFullTrust
  explanation and Additional Testing Information are saved; restricted
  capability review is expected during certification.
- Submit for certification: **enabled but not clicked**.
- Release control: **Do not publish until I select Publish now** is saved.

## Current not-observed list

Installed AppX behavior, WACK result, Windows Narrator/high-contrast/text-scaling
results, owner-approved IARC answers, seller tax/payout readiness, certification
result, public listing visibility, product-page traffic, purchases, refunds,
fees, and payouts remain unobserved.

Collected profit remains **$0.00**. The current gap remains **$4,000.00**.
