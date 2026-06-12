# Microsoft Store packaging

Everything needed to ship Hearth to the Microsoft Store as an MSIX/`appx`,
kept as code so a submission is reproducible.

| File | Purpose |
| ---- | ------- |
| `identity.json` | Package identity from Partner Center (`identityName`, `publisher`, `publisherDisplayName`) plus `productId` (the reserved app's Store ID, e.g. `9PLRSZZMFPJH`, used by `msstore submission` commands). Ships with `PLACEHOLDER_*` values; the `appx` build and the publish workflow stay no-ops until these are real. |
| `identity.cjs` | Single source of truth for reading `identity.json` and deciding whether identity is real. Used by `electron-builder.cjs` and CI (`node store/identity.cjs --check`). |
| `listing-metadata.json` | The Store listing (name, descriptions, keywords, URLs) as code. Fed to `msstore submission updateMetadata`. |

## The build host

The `appx` target **must be built on Windows** — `electron-builder` shells out to
Windows-only packaging tools. Use a Windows 10/11 machine or the `windows-latest`
CI runner. Both the **Windows Store (MSIX) Build** and **Microsoft Store Publish**
workflows already run there.

## One-time setup

1. **Reserve the app name** in [Partner Center](https://partner.microsoft.com/dashboard).
2. Open **Product → Product identity** and copy the three values into
   `store/identity.json`:

   ```json
   {
     "identityName": "1234 The-Hearth-Project.Hearth",
     "publisher": "CN=ABCD1234-5678-90AB-CDEF-1234567890AB",
     "publisherDisplayName": "The Hearth Project"
   }
   ```

3. Confirm the gate is open:

   ```bash
   npm run store:check   # prints "true" once no placeholders remain
   ```

4. Add the four publish secrets to the repo (Settings → Secrets and variables →
   Actions): `MS_TENANT_ID`, `MS_SELLER_ID`, `MS_CLIENT_ID`, `MS_CLIENT_SECRET`.

## Building locally

```powershell
npm install
npm run build:winstore   # icons + tiles + typecheck + vite build + appx
```

Output: `release/Hearth-1.0.0.appx`. With placeholder identity the `appx` target
is dropped, so this produces nothing until step 2 above is done.

## Generated assets

`npm run winstore-assets` derives every required tile, splash, and icon PNG into
`build/appx/` from `resources/app-icon.png`. They are generated, not committed.

## Submission checklist

- [ ] App name reserved in Partner Center
- [ ] `store/identity.json` filled with real values (`npm run store:check` → `true`)
- [ ] `MS_*` secrets configured on the repo
- [ ] `store/listing-metadata.json` reviewed
- [ ] Screenshots uploaded in Partner Center (1366×768 or larger)
- [ ] Age rating completed
- [ ] Privacy policy URL points at `docs/PRIVACY.md` (already set in the listing)

## Privacy policy

See [`../docs/PRIVACY.md`](../docs/PRIVACY.md). In short: all data is stored
locally in SQLite on your device; nothing is collected or transmitted.
