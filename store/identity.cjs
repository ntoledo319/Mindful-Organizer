// Single source of truth for reading store/identity.json and deciding whether
// the Microsoft Store appx package is publishable yet. Both the electron-builder
// config (electron-builder.cjs) and CI (`node store/identity.cjs --check`)
// share this so the gate is defined in exactly one place.
const { readFileSync } = require('node:fs');
const { join } = require('node:path');

const IDENTITY_PATH = join(__dirname, 'identity.json');
const PLACEHOLDER_PREFIX = 'PLACEHOLDER';

function readIdentity() {
  const raw = JSON.parse(readFileSync(IDENTITY_PATH, 'utf8'));
  return {
    identityName: raw.identityName,
    publisher: raw.publisher,
    publisherDisplayName: raw.publisherDisplayName,
    productId: raw.productId,
  };
}

function isPlaceholder(value) {
  return typeof value !== 'string' || value.trim() === '' || value.startsWith(PLACEHOLDER_PREFIX);
}

// Identity is "real" only when every required field is filled with a non-placeholder value.
function hasRealIdentity(identity = readIdentity()) {
  return (
    !isPlaceholder(identity.identityName) &&
    !isPlaceholder(identity.publisher) &&
    !isPlaceholder(identity.publisherDisplayName)
  );
}

module.exports = { IDENTITY_PATH, readIdentity, isPlaceholder, hasRealIdentity };

// CLI helpers so CI can branch/read values without parsing JSON in shell:
//   --check       → prints "true"/"false" (identity ready for an appx build)
//   --product-id  → prints the Store product ID (empty if unset)
// Used by windows-store.yml, release.yml, and local Store package checks.
if (require.main === module) {
  if (process.argv.includes('--check')) {
    process.stdout.write(hasRealIdentity() ? 'true' : 'false');
  } else if (process.argv.includes('--product-id')) {
    process.stdout.write(readIdentity().productId || '');
  }
}
