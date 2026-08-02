# Store reposition kit (Day-5 gate)

Status: **pre-registered decision options — nothing here is live, scheduled,
or submitted**

Registered 2026-07-28 (Day 15) alongside the reposition menu in
`revenue/PLAN.md`. Trigger diagnostics live in `store/CAMPAIGNS.md` (Decision
rules). This file holds ready-to-execute artifacts so the owner can act in
minutes when a gate fires. Every price below is a **sale configuration
option**, not the current price: the saved draft price is $14.99 and no sale
exists. Every option requires a new Partner Center submission that passes
certification before it takes effect, and every click is made by the owner
(submissions are legal/commercial acts — same pattern as HQ-04).

Claims boundary: every draft obeys the claims blacklist in
`store/LAUNCH_KIT.md` — no AI/clinical/therapeutic or medical-device
language; no "best", "first", "revolutionary", "guaranteed", or "effortless";
no user counts, outcomes, testimonials, or ratings that are not in the
evidence ledger; privacy wording only in the exact documented protection
boundary.

## RP-1 — Scheduled sale pricing ($0)

**Use when:** page views arrive but acquisitions are zero at the five-day
gate.
**Partner Center field:** app submission → **Pricing and availability** →
**Sale pricing** section.

Click path (from Microsoft's current sale-pricing documentation, fetched
2026-07-28:
<https://learn.microsoft.com/en-us/windows/apps/publish/put-apps-and-add-ons-on-sale>):

1. Open the Hearth submission (product 9PLRSZZMFPJH) and go to the
   **Pricing and availability** page.
2. In the **Sale pricing** section, select **Show options**, then
   **New sale**.
3. In the **Market selection** popup, select **United States** only (the
   launch market), then **Create**.
4. Under discount type, choose **Price** and select the **$9.99** tier
   (sale configuration option; the base price remains $14.99).
5. In **Offered to**, choose **Everyone**.
6. Set start and end dates for a **14-day** window (UTC). The price reverts
   to $14.99 automatically at the end date.
7. Select **Save** at the bottom of the page, then **Submit to the Store**
   from the submission overview.

Notes:

- $0 cost. Microsoft shows strikethrough pricing to customers on Windows
  10/11 during the sale period.
- Once the app is published, scheduling a sale requires a new submission that
  completes certification before the sale appears.
- Do not edit the start date after a sale has started, and avoid ending a
  sale early — customers see the published end date.
- Record the scheduled configuration, then the observed results, in
  `revenue/METRICS.md` (observed values only).

## RP-2 — Keyword revision ($0)

**Use when:** Store impressions are near zero (surfacing failure).
**Partner Center field:** app submission → **Store listings** → English
(United States) → **Search terms** (maximum 7 terms, ≤ 40 characters each,
≤ 21 words total — the same limits `scripts/validate-store.mjs` enforces on
`store/listing-metadata.json`).

Current saved terms: ADHD planner · energy planner · spoon theory · offline
task manager · focus planner · mood journal · variable capacity.

Candidate replacements, grounded in the ADHD/spoon-theory niche. Swap at most
2–3 terms per revision so the acquisitions report can attribute the effect:

| Swap out | Swap in | Rationale |
|---|---|---|
| mood journal | ADHD task manager | Buyers search the task job, not the diary |
| focus planner | energy budget | Matches the product's own vocabulary |
| offline task manager | spoon counter | Spoon-theory niche term buyers use |

All candidates fit the 40-character and 21-word limits in every listed
combination. Category note: primary **Productivity** / secondary
**Health + fitness** are set under **Properties**, not the listing page; a
category swap is a separate, later option — do not bundle it with a keyword
swap. When a revision is executed, update `store/listing-metadata.json` in
the same change and rerun `npm run store:validate` so the checked-in source
matches Partner Center.

## RP-3 — Listing copy variant ($0)

**Use when:** impressions are healthy but page views do not convert to
acquisitions.
**Partner Center fields:** app submission → **Store listings** → English
(United States) → **Short description** (≤ 200 characters), and the first
screenshot with its caption.

Alternate short description draft (181 characters; a decision option, not
live copy; current live draft is a different, also-truthful sentence):

> Give every task an energy cost, choose a daily budget from 4 to 24, and see
> what fits the day you actually have. Local and encrypted at rest. No
> account, cloud, ads, or record sync.

Every claim in the draft is demonstrable in the packaged product today:
task energy costs, the user-chosen 4–24 daily budget, the fitting-tasks view,
local encrypted-at-rest storage, and the absence of account, cloud,
advertising, and record sync.

First-screenshot reframe plan:

- Goal: make the energy-planning job legible in the first visible frame,
  which dominates search results and the top of the product page.
- Method: recapture **01-today.png** from the same exact accepted build and
  seeded fictional state, reframed so the remaining energy budget, the daily
  briefing, and the fitting tasks are the dominant visible elements (the
  variant concept already defined in `store/PRODUCT-PAGE-EXPERIMENTS.md`,
  Experiment 1).
- Constraints: raw, truthful app screenshot only — no added outcome text,
  ratings, badges, testimonials, or fake Windows frame. Same 1920 × 1080
  canvas, same fictional demo data; record the new file's SHA-256 in
  `revenue/METRICS.md`.
- Sequencing: change the first screenshot **or** the short description in a
  given submission, not both, so the effect is attributable. The certified
  50/50 product-page experiment remains the cleaner test once baseline
  traffic exists (entry gate in `store/PRODUCT-PAGE-EXPERIMENTS.md`).

## RP-4 — Market expansion (deferred to Submission 2; constrained)

**Use when:** the "no impressions → revisit category, keywords, market, and
eligibility" diagnostic in `store/CAMPAIGNS.md` points at market after RP-2
has failed — and only as a Submission-2 decision, never a Day-5 quick fix.
**Partner Center field:** app submission → **Pricing and availability** →
**Markets** (currently United States only).

Constraint that keeps this out of the quick-fix tier: the runtime crisis copy
is US-specific (988 resources) and is hash-chained to the accepted candidate
(D018). Serving new markets truthfully means localized emergency-resource
copy, which changes runtime code, which restarts the candidate evidence
chain — new build, new hosted screenshots, new quality and Windows Store
gates, new AppX hash. `store/listing-metadata.json` already documents this
reason on the markets field. Estimate: a full candidate cycle, not minutes;
schedule only after a US-market signal exists that is worth expanding.

## Execution ledger rule

Whichever option fires: one option per submission; the owner performs every
Partner Center action; results are recorded as observed values in
`revenue/METRICS.md`; and the change is announced nowhere until it is
actually live.
