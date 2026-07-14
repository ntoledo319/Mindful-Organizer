# Product-page experiment plan

Status: **pre-registered, not eligible to run**

Microsoft reports that icons and screenshots can occupy up to half of the Store
product page and supports certified 50/50 product-page experiments. The feature
can compare search impressions, page views, installs, and conversion.

Official reference:
<https://learn.microsoft.com/en-us/windows/apps/publish/product-page-experiments>

## Entry gate

Do not start an experiment until:

- the paid listing is public and stable;
- the package, policy, support, candidate-provenance, and certification gates
  are closed;
- the baseline screenshot set passes store/SCREENSHOTS.md;
- Partner Center shows enough baseline traffic to make a comparison useful;
- no package, price, description, market, or campaign change is scheduled during
  the test;
- the owner approves the Partner Center submission.

Low traffic is evidence to improve distribution, not permission to declare a
winning design from a handful of visits.

## Experiment 1 — first screenshot

**Question:** Does an outcome-led Today frame communicate the energy-planning job
more clearly than a more data-dense Today frame?

- Control: accepted 01-today.png.
- Variant: the same exact build and seeded state, reframed so the energy budget,
  briefing, and fitting tasks are the dominant visible elements.
- Hold constant: icon, remaining screenshots, captions, description, price,
  categories, markets, and package.
- Primary measure: Store page-to-install conversion.
- Supporting measures: page views and installs.
- Guardrails: certification remains green; Health and review sentiment do not
  deteriorate.

The variant must remain a raw, truthful app screenshot. Do not add outcome text,
ratings, badges, testimonials, or a fake Windows frame.

## Experiment 2 — icon, only after Experiment 1

Run only if the candidate reproduces the documented deterministic asset set and
Experiment 1 is complete.

**Question:** Does a simpler small-size Hearth mark improve search-result entry
without reducing recognition?

- Control: accepted 300 × 300 Store icon.
- Variant: one deterministically generated icon variant built from the same
  documented brand system.
- Hold constant: every screenshot and all text/commerce fields.
- Primary measure: search-impression-to-page-view movement.
- Guardrails: no misleading symbol, medical cross, platform mark, or imitation
  of another product.

## Analysis record

Before launching either test, record the start date, control hash, variant hash,
package version, listing revision, markets, and hypothesis. At close, record the
observed metrics, limitations, and decision. “Inconclusive” is a valid result.

Never change the original page assets mid-experiment; Microsoft warns that doing
so can invalidate the comparison.
