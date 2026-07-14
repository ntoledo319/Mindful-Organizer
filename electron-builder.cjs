// electron-builder configuration as code so the Microsoft Store identity can be
// pulled from store/identity.json at build time instead of being hardcoded.
// The appx target is only emitted once real identity values are present, which
// keeps `npm run build:win` working with placeholders while making the Store
// build a no-op until Partner Center values land. See store/identity.cjs.
//
// The filename MUST be "electron-builder.cjs" (not "electron-builder.config.cjs"):
// electron-builder only auto-discovers config named electron-builder.{yml,yaml,
// json,json5,toml,js,cjs,ts}. A ".config.cjs" suffix is silently ignored, so the
// build falls back to defaults and the appx ships with placeholder identity.
const { readIdentity, hasRealIdentity } = require('./store/identity.cjs');

const identity = readIdentity();
const storeReady = hasRealIdentity(identity);

const winTargets = [
  { target: 'nsis', arch: ['x64'] },
  { target: 'portable', arch: ['x64'] },
];
if (storeReady) {
  winTargets.push({ target: 'appx', arch: ['x64'] });
}

module.exports = {
  appId: 'io.hearthproject.hearth',
  productName: 'Hearth',
  // Windows CI preinstalls and checksum-verifies the exact Electron runtime so
  // screenshot capture and packaging share one proven binary. Local builds
  // retain electron-builder's normal download behavior when this is unset.
  ...(process.env.HEARTH_ELECTRON_DIST
    ? { electronDist: process.env.HEARTH_ELECTRON_DIST }
    : {}),
  copyright: 'Copyright © 2026 Nicholas Toledo',
  directories: {
    output: 'release',
    buildResources: 'build',
  },
  files: ['dist', 'dist-electron'],
  extraResources: [
    { from: 'resources/hero-illustration.png', to: 'hero-illustration.png' },
    { from: 'resources/BRAND_PROVENANCE.md', to: 'BRAND_PROVENANCE.md' },
    { from: 'LICENSE', to: 'LICENSE' },
    { from: 'THIRD_PARTY_NOTICES.md', to: 'THIRD_PARTY_NOTICES.md' },
  ],
  asarUnpack: ['**/node_modules/better-sqlite3/**'],
  mac: {
    category: 'public.app-category.healthcare-fitness',
    icon: 'build/icon.icns',
    target: [{ target: 'zip', arch: ['x64', 'arm64'] }],
    hardenedRuntime: false,
    gatekeeperAssess: false,
  },
  win: {
    icon: 'build/icon.ico',
    target: winTargets,
  },
  appx: {
    applicationId: 'Hearth',
    identityName: identity.identityName,
    publisher: identity.publisher,
    publisherDisplayName: identity.publisherDisplayName,
    displayName: 'Hearth',
    backgroundColor: '#F5F0E6',
    showNameOnTiles: true,
    languages: ['en-US'],
  },
  nsis: {
    oneClick: false,
    perMachine: false,
    allowToChangeInstallationDirectory: true,
    artifactName: 'Hearth-Setup-${version}.${ext}',
  },
  portable: {
    artifactName: 'Hearth-Portable-${version}.${ext}',
  },
  linux: {
    icon: 'build/icon.png',
    category: 'Utility',
    target: ['AppImage'],
  },
};
