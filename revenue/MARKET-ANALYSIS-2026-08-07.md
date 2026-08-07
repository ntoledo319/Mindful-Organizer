# Market and pricing re-derivation — 2026-08-07

_Agent work under the owner directive "re-run market analysis and pricing."
Nothing here changes the listing. Price and positioning changes are owner
actions. Sources are public web pages observed 2026-08-07; none of this is
demand evidence for Hearth specifically, and it must not be recorded as such._

## Why this was needed

`revenue/PLAN.md` set $14.99 and derived "314 sales ≈ $4,000.83" before any
comparable set existed. `HANDOFF.md` §2 already flags that figure as
"arithmetic, not demand." This document supplies the missing comparables so the
number can at least be argued about honestly.

## 1. The fee assumption is correct

Microsoft Learn's Store distribution page states the current model: developers
may use their own commerce platform and keep 100% of revenue for non-gaming
apps, or use Microsoft's commerce platform at 15% for apps and 12% for games.
The repo's 15% blended assumption and the $12.7415 net on $14.99 are right.

The 0%-fee own-commerce path is real but not worth taking here. It would mean
building payment handling into an application whose entire product claim is
that it has no account, no cloud, and no network calls. The 15% is the cost of
keeping that claim true. Recommend: no change.

## 2. Comparable set

Observed 2026-08-07 across ADHD/neurodivergent planner roundups (toolfinder,
habi.app, koalaforwork, fluidwave). Prices as reported by those sources, not
verified against each vendor's own checkout:

| Product | Model | Reported price | Platforms |
|---|---|---|---|
| Sunsama | subscription | ~$20–22/mo, ~$16–17/mo annual | cross-platform |
| Tiimo | subscription | ~$12/mo or ~$54/yr | mobile-first |
| Structured | freemium + lifetime tier | lifetime unlocks AI planning | iOS-centric |
| Amazing Marvin | subscription | mid-range, below Sunsama | cross-platform |
| Habi | freemium | free core, ~$2.49/mo premium | Apple only |

Two facts matter more than any individual number:

- **The category is subscription.** Effectively every serious entrant bills
  monthly or annually. One-time purchase is not the norm.
- **The category is mobile, and disproportionately Apple.** Structured and Habi
  are Apple-only. Tiimo is mobile-first. The roundups are written for phone
  users.

## 3. What that means for Hearth

**$14.99 one-time is not expensive. It is the cheapest serious option in the
category by a wide margin.** It is roughly three months of Tiimo, or three
weeks of Sunsama, paid once, forever. Whatever is wrong with the plan, the
price being too high is not it.

**Hearth is the weakest entrant in the ADHD-planner category and nearly the
only entrant in a different one.** As "an ADHD planner," it is Windows-only,
has no sync, no mobile app, no AI, and no free tier, competing against
well-funded products with years of head start on the platform its audience
actually uses. As "a planner that never touches the network," it has almost no
competition at all — every product in the table above is a cloud account.

The four differentiators stack into one sentence: *local-only, no account,
one-time purchase, Windows desktop.* Not one of the comparables offers even two
of those.

## 4. Pricing scenarios (arithmetic only)

At the 15% Microsoft fee, to reach $4,000 gross-to-net:

| Price | Net per sale | Sales needed |
|---|---|---|
| $14.99 | $12.74 | 314 |
| $19.99 | $16.99 | 236 |
| $24.99 | $21.24 | 189 |
| $29.99 | $25.49 | 157 |

**Recommendation: do not change the price.** Not because $14.99 is optimal —
$19.99 is arguably better supported by the comparable set — but because there
is zero demand data, and moving the price on speculation would replace one
unevidenced number with another. Price is not the binding constraint. Nobody
knowing the product exists is the binding constraint. Revisit after the
five-day signal gate in `revenue/PLAN.md` produces real conversion data.

## 5. The positioning finding

This is the substantive result of the exercise.

The current listing leads with ADHD and variable-capacity days. That framing
aims the product at the most crowded, most subscription-saturated,
most mobile-dominated corner of the market, where Hearth's Windows-only,
sync-free, AI-free profile reads as a list of missing features.

The same binary, described as *the planner that works entirely on your machine
and never phones home*, aims at an audience where those same properties read as
the product. Privacy-first desktop software has amplification channels that
ADHD-planner software does not, and they cost $0: they are places where "no
account, no telemetry, no cloud, verifiable" is itself the story.

This is a listing-copy and launch-targeting question, not a code question. The
app does not change. Raised as a proposal rather than a decision because
changing the listing is an owner action — see `docs/project/PROPOSALS.md`.

Caveat worth stating plainly: this is reasoning from category structure, not
from observed demand for Hearth. It is a better-grounded guess than the one it
replaces. It is still a guess.

## 6. On the $4,000 / Day-28 target

Day 28 is 2026-08-10, three days out. Nothing is submitted. Certification alone
is days of wall-clock, and per ADA §6(c) the Store pays monthly with a $50
threshold, so August sales pay around mid-September regardless.

The Day-21 gate already concluded the target is unreachable in-window. The
recommendation here is to stop carrying it as a live gap. A target that cannot
be hit, restated daily as a $4,000 shortfall, is exactly the mechanism that
manufactures the urgency `AGENTS.md` §2 forbids. Closing it out is an owner
decision; the honest replacement is a live purchasable listing plus a first
real demand signal.
