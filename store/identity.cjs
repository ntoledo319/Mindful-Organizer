// Single source of truth for reading store/identity.json and deciding whether
// the Microsoft Store appx package is publishable yet. Both the electron-builder
// config (electron-builder.config.cjs) and CI (`node store/identity.cjs --check`)
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

// `node store/identity.cjs --check` → prints "true"/"false" and exits 0 so CI
// can branch without parsing JSON in shell. Used by store-publish.yml + release.yml.
if (require.main === module && process.argv.includes('--check')) {
  process.stdout.write(hasRealIdentity() ? 'true' : 'false');
}
