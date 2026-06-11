# Windows Store (MSIX) build

This folder contains the Windows Store packaging configuration and guidance for Hearth.

## Important: build host

The MSIX/AppX target **must be built on Windows** (`electron-builder` uses Windows-only tooling for `.appx` packages). Use a Windows 10/11 machine, a Windows CI runner, or a Windows VM.

## Required before building

1. **Reserve the app name** in [Microsoft Partner Center](https://partner.microsoft.com/dashboard).
2. Note the **Package/Identity/Name** and **Publisher** values from Partner Center.
3. Replace the placeholder publisher in `package.json` under `build.appx.publisher` with your real publisher string.

   ```json
   "appx": {
     "publisher": "CN=YOUR-REAL-PUBLISHER-CN"
   }
   ```

4. Optionally change `identityName` to match the identity name Microsoft assigned.

## Build command

From the repository root on Windows:

```powershell
npm install
npm run build:winstore
```

Output: `release/Hearth-1.0.0.appx` (unsigned test build).

For a Store-signed package, upload the `.appx` to Partner Center or sign it with your code-signing certificate.

## Generated assets

`npm run build:winstore` runs `npm run winstore-assets`, which creates all required tile, splash, and icon PNGs in `build/appx/`. These are derived from `resources/app-icon.png` and do not need to be committed.

## Store submission checklist

- [ ] App name reserved in Partner Center
- [ ] `build.appx.publisher` updated with real publisher CN
- [ ] `build.appx.identityName` matches Partner Center identity
- [ ] Screenshots uploaded (at least 1920×1080 or 1366×768)
- [ ] Store description, features, and privacy policy provided
- [ ] Age rating completed
- [ ] `.appx` uploaded and submitted for certification

## Privacy policy

Hearth stores all user data locally in a SQLite database inside the user's app-data directory. The app makes no network requests and collects no telemetry.
