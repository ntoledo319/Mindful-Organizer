# Store discovery review — 2026-08-07

_Agent analysis of the listing's searchable fields against Microsoft's published
listing rules. Nothing here is applied — listing copy is an owner action, and
`store/listing-metadata.json` is untouched. Companion to
`revenue/MARKET-ANALYSIS-2026-08-07.md`._

> **Application note — 2026-08-19:** the preceding sentence remains true for
> the 2026-08-07 review date. Its recommendation is now applied in the local
> working tree: platform-first copy plus seven replacement keywords. Nothing
> has been saved in Partner Center. The chosen keywords contain 14 words, so
> this document's later "16 words" count was an arithmetic error; the terms
> themselves are unchanged.

## 0. Correction to PROP-006

PROP-006 asserted that the listing "leads with ADHD." That is **wrong**, and the
proposal's premise needs amending. The listing already leads with privacy:

- `positioning`: a privacy-first Windows energy planner for ADHD and other
  variable-capacity days
- `shortDescription`: plan a realistic day around the energy you have, with no
  account, cloud, ads, or record sync

The privacy framing is already first in both. The real gap is not the prose —
it is the **keywords**, which are the fields that actually drive Store search.
PROP-006 should be narrowed accordingly: it is a keyword and category question,
not a rewrite.

## 1. The rules (verified against Microsoft Learn, 2026-08-07)

- **7 keywords maximum.** One Microsoft page states 40 characters each with a
  hard cap of **21 separate words across all keywords**; another states 30
  characters each. The docs disagree. Treat 30 chars / 21 words as the safe
  envelope and confirm the live field limits in Partner Center.
- Keywords are **not shown to customers**. They exist purely for the Store's
  internal search engine.
- Short description: keep under **270 characters** for display (the field
  accepts more, but some views truncate). The current one is ~92 — fine.

**Current word budget: 15 of 21 used.** There is headroom, but all 7 keyword
slots are occupied, so improvement means replacement, not addition.

## 2. Keyword-by-keyword

| Keyword | Verdict | Reasoning |
|---|---|---|
| `spoon theory` | **keep — best asset** | Near-zero competition, exact intent. Anyone typing this is the target buyer and knows why. |
| `offline task manager` | **keep** | High intent, directly names the differentiator, uncontested by the subscription incumbents. |
| `ADHD planner` | **keep** | Highest volume of the set. Contested by Tiimo/Structured, and results skew mobile — but the intent is exact and it is worth one slot. |
| `energy planner` | **drop — actively harmful** | In a general app store, "energy" collocates with electricity, utilities, and home-energy monitoring. This term likely surfaces the product to people looking for a power-bill app, and buries it under them. It is also the product's own coinage, so almost nobody searches it. |
| `variable capacity` | **drop** | Internal vocabulary. Effectively zero query volume — nobody describes their own day this way in a search box. |
| `mood journal` | **weak** | Heavily contested, and it pulls the listing toward the crowded wellness space and the Health category rather than the uncontested privacy/offline space. |
| `focus planner` | **weak** | Contested, generic, no differentiation. |

## 3. Candidate replacements

Ranked by intent-to-competition ratio:

1. **`pacing`** — the term chronic-illness, ME/CFS, and long-COVID communities
   actually use, and the natural sibling of spoon theory. Near-uncontested in
   app stores. Strongest single addition available.
2. **`no subscription`** — people search this deliberately, to escape
   subscriptions. It is true of this product and false of every competitor in
   the comparable set.
3. **`offline planner`** or **`private planner`** — restates the differentiator
   in the words a buyer would actually type.
4. **`executive function`** — reaches the ADHD/autistic audience without
   competing head-on for `ADHD planner`.

A defensible 7, at 16 words: `spoon theory`, `pacing`, `offline task manager`,
`ADHD planner`, `no subscription`, `offline planner`, `executive function`.

**This is reasoning about search behaviour, not measured search volume.** No
keyword-volume data source was consulted, and Microsoft does not publish Store
query volumes. Treat it as a better-argued starting hypothesis than the current
set, and let Partner Center acquisition data settle it after launch — that is
what `store/PRODUCT-PAGE-EXPERIMENTS.md` exists for.

## 4. Category question

`category.secondary` is **Health + fitness**. Worth the owner reconsidering:

- It places the listing beside fitness and wellness apps, where it competes
  poorly and where the audience is not looking for a desktop planner.
- It may invite closer content review of a product that explicitly and
  repeatedly disclaims being a medical device, diagnosis, treatment, or monitor.
- The uncontested position identified in the market analysis — private,
  offline, one-time desktop software — lives entirely in Productivity.

Primary = Productivity is right and should stay.

## 5. What this does not change

Nothing about capability claims. The privacy and accessibility language in
`docs/PRIVACY.md`, `README.md`, and the listing stays exactly as narrow as it
is. Better discovery must never be bought by widening a claim.
