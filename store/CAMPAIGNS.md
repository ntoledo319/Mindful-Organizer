# Store campaign and measurement plan

Status: **prepared, inactive**

The reserved product ID is 9PLRSZZMFPJH. After the product page is publicly
visible and purchasable, its expected direct link is:

<https://apps.microsoft.com/detail/9PLRSZZMFPJH>

Do not distribute that link until the observed public page is checked in a
private browser. A reserved ID and a successful package build are not a live
listing.

Microsoft Store custom campaign IDs allow Partner Center to separate page views
and conversions from different links without adding third-party analytics to
Hearth. The campaign ID is public in the URL; it must never contain a name,
email, diagnosis, account identifier, or other personal data.

Official measurement reference:
<https://learn.microsoft.com/en-us/partner-center/insights/acquisitions-report>

## Link convention

Use this format only after the base listing is live:

    https://apps.microsoft.com/detail/9PLRSZZMFPJH?cid=<campaign-id>

Campaign IDs use lowercase ASCII letters, numbers, and hyphens. Keep them stable
so reports remain comparable.

| ID | Intended placement | Authorization |
|---|---|---|
| landing-primary | Primary button on the deployed Hearth landing page | May be wired after the Store page is live |
| github-readme | Public repository README | May be wired after the Store page is live |
| owner-launch-note | One launch note on an owner-controlled channel | Human review and send required |
| owner-approved-community-<slug> | One community whose rules explicitly permit the post | Human review and send required |
| product-update-<yyyymm> | A later, truthful release update | Human review and send required |

Do not reuse one community ID across different communities, and do not create a
campaign ID for organic Store search or browse traffic.

## Funnel ledger

For each source, record observed values only:

| Stage | Partner Center evidence | Diagnostic question |
|---|---|---|
| Search impressions | Product-page experiment or Store insights | Is the listing being surfaced? |
| Page views | Acquisitions report | Are people reaching the page? |
| Acquisitions | Acquisitions report | Does the page earn a purchase/license? |
| Installs | Acquisitions report | Does acquisition turn into installation? |
| Usage | Acquisition funnel and Usage report | Does the app launch after install? |
| Retention | Usage report | Do people return? |
| Health | Health report | Are crashes or hangs destroying trust? |
| Ratings and reviews | Ratings and reviews | What do customers say in public? |
| Refunds and collected proceeds | Payout summary | Did a purchase become retained cash? |

Acquisitions do not prove collected profit and do not include every refund,
reversal, or chargeback. Payout evidence remains the money source of truth.

## Decision rules

- No Store impressions: revisit category, keywords, market, and eligibility
  before changing product behavior.
- Impressions but no page views: improve the first visual, short description, and
  positioning.
- Page views but no acquisitions: test one page asset, price presentation, or
  value proposition at a time.
- Acquisitions but weak install/usage: investigate package, system requirements,
  first run, and activation.
- Usage but weak return: improve the first completed energy-planning loop before
  adding acquisition channels.

## Reposition protocol

When a decision rule above fires at the five-day gate, the pre-registered,
pre-costed fix is in [store/REPOSITION_KIT.md](REPOSITION_KIT.md) (menu in
`revenue/PLAN.md`): one change per Partner Center submission, executed by the
owner, recorded as observed values in `revenue/METRICS.md`. The
"no impressions → revisit market" step treats market expansion as a
Submission-2 decision, because the US crisis copy is hash-chained to the
accepted candidate (kit option RP-4). Launch destinations whose rules permit
owner-posted project notes are listed in `store/LAUNCH_TARGETS.md`.

No draft here authorizes autonomous posting, messaging, review solicitation, or
customer contact.
