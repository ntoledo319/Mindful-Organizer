# Post-publication doc sweep — pre-drafted replacements

Created 2026-07-28 (market-readiness remediation D2-1). This file exists so
playbook step 4 ("Immediately after publication", store/README.md) is a
same-day apply, not fresh writing under time pressure.

**Apply only after playbook steps 1–3 are done**: the public Store page and
paid checkout were observed in a signed-out browser, the observation is
recorded in `revenue/METRICS.md`, and `store/listing-metadata.json` carries
the live URL. Until then, every replacement below would be a false claim.

## Placeholders

Replace these with observed values only — never with plans or expectations:

- `<LIVE_STORE_URL>` — the observed public Store URL. Expected pattern:
  `https://apps.microsoft.com/detail/9PLRSZZMFPJH`. Use what was actually
  observed in the signed-out browser.
- `<OBSERVED_PRICE>` — the price shown on the live page. Expected `$14.99`;
  if the page shows anything else, the page wins.
- `<PUBLICATION_DATE>` — the date publication was observed (ISO format); use
  it for `_Last updated:_` lines.

If a gate named in a replacement was not actually completed (for example the
manual accessibility pass), delete that clause — claim only what happened.

## 1. `README.md` (lines 14–20) — release-status blockquote

Current:

> **Release status:** Ample 1.1.0 is an accepted x64 package in a fully
> prepared Microsoft Partner Center draft, but it is not certified, public, or
> purchasable. The exact package passed source, package-structure, and real
> Windows DPAPI lifecycle automation. Microsoft certification, a manual Windows
> accessibility pass, an owner-completed IARC attestation, and seller payout
> readiness remain release gates. See store/README.md before making any
> availability claim.

Replacement:

> **Release status:** Ample 1.1.0 is available on the Microsoft Store for
> <OBSERVED_PRICE>: <LIVE_STORE_URL>. The shipped package passed source,
> package-structure, and real Windows DPAPI lifecycle automation, Microsoft
> certification, and a manual Windows accessibility pass. The source remains
> MIT licensed; a purchase pays for the official packaged binary and Store
> delivery. See store/README.md before making any availability claim beyond
> this.

Also: in the directory map (line ~140), the entry
`landing/  Zero-dependency pre-release commercial landing artifact` drops
"pre-release" once the landing is deployed (playbook step 5).

## 2. `docs/TERMS.md` (lines 5–9) — "Current status"

Current:

```
## Current status

Ample is not currently listed as purchasable. These terms describe the intended
official Microsoft Store package and do not represent that a price, package, or
listing is live.
```

Replacement:

```
## Current status

Ample is available on the Microsoft Store for <OBSERVED_PRICE> at
<LIVE_STORE_URL>. These terms govern the official Microsoft Store package.
```

Also bump `_Last updated: 2026-07-14_` to `_Last updated: <PUBLICATION_DATE>_`.

## 3. `docs/REFUNDS.md` (lines 5–9)

Current:

```
Ample is not currently listed as purchasable. No direct payment link,
developer-run checkout, subscription, in-app purchase, or license-key sale is
active.

If an official paid Microsoft Store package is released:
```

Replacement:

```
Ample is available on the Microsoft Store for <OBSERVED_PRICE> at
<LIVE_STORE_URL>. No developer-run checkout, subscription, in-app purchase,
or license-key sale exists; Microsoft processes every purchase.

For the official paid Microsoft Store package:
```

Also bump `_Last updated:_` as above.

## 4. `docs/SUPPORT.md` (line 7)

Current:

```
Ample is not currently released. This page is the public support landing page.
```

Replacement:

```
Ample is available on the Microsoft Store at <LIVE_STORE_URL>. This page is
the public support landing page.
```

Also bump `_Last updated:_` as above.

## 5. `SECURITY.md` (lines 5–7) — "Supported release"

Current:

```
Ample 1.1.x is the current release-candidate line. No Ample binary is public
or purchasable yet. Security fixes will be evaluated against the current source
and, after publication, the current Microsoft Store release.
```

Replacement:

```
Ample 1.1.x is the current Microsoft Store release line, available at
<LIVE_STORE_URL>. Security fixes are evaluated against the current source and
the current Microsoft Store release.
```

## 6. `landing/index.html` — FAQ entry (deploy-time, with the landing checklist)

Apply together with the landing live-transition checklist in
`landing/README.md`, not in isolation — that checklist owns the
`data-release-state="prelaunch"` attribute and the "Store release pending"
hero span. The store validator's draft-only invariants stop applying once
`store/listing-metadata.json` flips to `live` (playbook step 3).

Current (lines ~324–334):

```
<summary>Is Ample available to buy now?</summary>
<p>
  No. The exact 1.1.0 x64 package, proposed price, listing copy, and
  five screenshots are saved in a Partner Center draft under a
  manual publication hold. An owner-completed IARC attestation,
  seller payout readiness, Microsoft certification, and a manual
  accessibility review of the Store-signed build remain release
  gates.
</p>
```

Replacement:

```
<summary>Is Ample available to buy now?</summary>
<p>
  Yes. Ample 1.1.0 is available on the Microsoft Store for
  <OBSERVED_PRICE>: <LIVE_STORE_URL>?cid=landing-primary
</p>
```

(The `cid=landing-primary` campaign parameter matches store/CAMPAIGNS.md.)

## 7. `docs/PRIVACY.md` — check only, no replacement drafted

Verified 2026-07-28: the policy contains no pre-release, price, or
purchasability status lines — its content is release-state-independent. On
publication day, re-check with:

    grep -nEi "not currently|not yet|pending|pre-release|purchas" docs/PRIVACY.md

If nothing matches, leave the file and its `_Last updated:_` line untouched.

## State records, not copy

These files describe live state and are updated as records during playbook
steps 2, 3, and 6 rather than from this sheet: `store/listing-metadata.json`
(releaseState + live URL), `revenue/METRICS.md` (observation ledger),
`store/README.md` ("Current Partner Center state"), `PROJECT_TRACKER.md`
(snapshot rows), and `store/WINDOWS-VALIDATION.md` (certification result).
