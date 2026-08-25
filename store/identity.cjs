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
    identityVerified: raw.identityVerified,
    publisher: raw.publisher,
    publisherDisplayName: raw.publisherDisplayName,
    productId: raw.productId,
  };
}

function isPlaceholder(value) {
  return typeof value !== 'string' || value.trim() === '' || value.startsWith(PLACEHOLDER_PREFIX);
}

// Identity is "real" only after the Partner Center value has been observed and
// every required field is filled with a non-placeholder value. A plausible
// identityName is not evidence: rename tooling can produce a syntactically
// valid guess, so identityVerified must be exactly true.
function hasRealIdentity(identity = readIdentity()) {
  return (
    identity.identityVerified === true &&
    !isPlaceholder(identity.identityName) &&
    !isPlaceholder(identity.publisher) &&
    !isPlaceholder(identity.publisherDisplayName)
  );
}

module.exports = { IDENTITY_PATH, readIdentity, isPlaceholder, hasRealIdentity };

// CLI helpers so CI can branch/read values without parsing JSON in shell:
//   --check       → prints "true"/"false" (identity ready for an appx build)
//   --require-verified → exits non-zero unless the Partner Center identity is verified
//   --product-id  → prints the Store product ID (empty if unset)
// Used by windows-store.yml, release.yml, and local Store package checks.
if (require.main === module) {
  if (process.argv.includes('--check')) {
    process.stdout.write(hasRealIdentity() ? 'true' : 'false');
  } else if (process.argv.includes('--require-verified')) {
    if (!hasRealIdentity()) {
      console.error(
        'Store package identity is unverified. Copy the observed Partner Center identity into store/identity.json and set identityVerified to true before building an AppX.',
      );
      process.exitCode = 1;
    }
  } else if (process.argv.includes('--product-id')) {
    process.stdout.write(readIdentity().productId || '');
  }
}
