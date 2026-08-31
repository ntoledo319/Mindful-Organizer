# Paulatim static landing artifact

This directory is a zero-dependency commercial landing page that can be served
as plain static files. Its copy is synchronized to the 2026-08-31 public Store
release, but the landing page itself remains undeployed:

- the purchase links target the signed-out, observed Microsoft Store page with
  the documented `landing-primary` campaign ID;
- no fake audience, review, revenue, or security claim;
- no external font, script, tracker, cookie, form, or third-party asset;
- three hash-recorded Paulatim screenshots copied from the exact PAULATIM-001
  `f2d2a417` screenshot artifact, containing only seeded fictional data; the
  landing page remains undeployed;
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

## Live-transition outcome

Completed locally on 2026-08-31 after the Store page and live $14.99 purchase
action were observed:

1. The “Store release pending” span was replaced with:

       https://apps.microsoft.com/detail/9PLRSZZMFPJH?cid=landing-primary

2. Keep the protection and limits copy synchronized with the exact released
   data lifecycle, including migration-backup retirement after two verified
   encrypted generations.
3. “Proposed” price/package language was changed only to the observed $14.99
   Store terms.
4. After deployment, add the deployed canonical URL and matching Open Graph URL. JSON-LD
   structured data (the store validator's application/ld+json carve-out), a
   sitemap, and absolute og:image URLs are also due at deploy time, once the
   domain is known.
5. The Store link resolved signed out; reverify privacy, terms, refunds,
   accessibility, support, and source links after the documentation commit is
   public.
6. Before deployment, validate HTML, run keyboard and screen-reader checks, test 320 px through
   large desktop widths, and run a no-cache performance check.
7. After deployment, record the host, public URL, publish time, and campaign ID
   in the evidence ledger.

Before any deployment, run `npm run store:validate` from the workspace root.

The tracked product frames can be regenerated only from the independently
verified exact-candidate screenshot directory. Never reuse the historical
Hearth or AMPLE-001 pixels for Paulatim:

    npm run landing:media -- \
      --source tmp/PAULATIM-001-<sha7>/downloads/screenshots \
      --build-ref <exact-candidate-sha>

## Measurement

The page intentionally has no analytics script. The landing-primary Store
campaign ID supplies aggregate page-view and conversion attribution in Partner
Center without adding third-party telemetry to Paulatim. See
store/CAMPAIGNS.md.
