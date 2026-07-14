# Hearth static landing artifact

This directory is a zero-dependency commercial landing page that can be served
as plain static files. It is currently truthful to the pre-release state:

- no purchase button;
- no fake availability, audience, review, or security claim;
- no external font, script, tracker, cookie, form, or third-party asset;
- three hash-recorded exact-candidate screenshots containing only seeded,
  fictional demonstration data;
- the implemented encrypted-at-rest boundary and its memory, OS-session,
  export, deletion, and recovery limits are visible;
- legal and project links point to stable main-branch document locations that
  must be verified after merge.

## Local preview

From the workspace root:

    python3 -m http.server 4173 --directory landing

Then open http://localhost:4173. The server touches only this workspace and
introduces no install or build step.

## Eligible deployment shape

Publish landing/ as the static root on a zero-cost host whose current terms allow
a commercial product page. Cloudflare Pages and Vercel are possible candidates,
but their terms, limits, account state, and domain behavior must be checked
immediately before deployment. GitHub Pages is intentionally excluded as the
primary commercial host under the repository's current terms decision.

No deployment is authorized by this artifact. Account sign-in, domain changes,
and any final public publish action remain owner-controlled when required.

## Live-transition checklist

After Store certification and only after the product page is visibly
purchasable:

1. Replace the “Store release pending” span in index.html with a link to:

       https://apps.microsoft.com/detail/9PLRSZZMFPJH?cid=landing-primary

2. Keep the protection and limits copy synchronized with the exact released
   data lifecycle, including migration-backup retirement after two verified
   encrypted generations.
3. Change “proposed” price/package language only to observed live terms.
4. Add the deployed canonical URL and matching Open Graph URL.
5. Verify privacy, terms, refunds, accessibility, support, source, and Store
   links in a private browser.
6. Validate HTML, run keyboard and screen-reader checks, test 320 px through
   large desktop widths, and run a no-cache performance check.
7. Record the host, public URL, publish time, and campaign ID in the evidence
   ledger.

Before any deployment, run `npm run store:validate` from the workspace root.

The tracked product frames can be regenerated only when the matching accepted
screenshot evidence is present under `tmp/artifacts/final-screenshots/`:

    npm run landing:media

## Measurement

The page intentionally has no analytics script. The landing-primary Store
campaign ID supplies aggregate page-view and conversion attribution in Partner
Center without adding third-party telemetry to Hearth. See
store/CAMPAIGNS.md.
