import { createRequire } from 'node:module';
import { describe, expect, it } from 'vitest';

const require = createRequire(import.meta.url);

interface StoreIdentity {
  identityName?: unknown;
  identityVerified?: unknown;
  publisher?: unknown;
  publisherDisplayName?: unknown;
  productId?: unknown;
}

const { hasRealIdentity } = require('../store/identity.cjs') as {
  hasRealIdentity: (identity: StoreIdentity) => boolean;
};

const observedIdentity: StoreIdentity = {
  identityName: 'ToledoTechnologies.ObservedInPartnerCenter',
  identityVerified: true,
  publisher: 'CN=FBC80173-0C85-481E-BC5E-A3BE88BC2020',
  publisherDisplayName: 'Toledo Technologies',
  productId: '9PLRSZZMFPJH',
};

describe('Store package identity guard', () => {
  it('accepts a complete identity only after explicit Partner Center verification', () => {
    expect(hasRealIdentity(observedIdentity)).toBe(true);
    expect(hasRealIdentity({ ...observedIdentity, identityVerified: false })).toBe(false);
    expect(hasRealIdentity({ ...observedIdentity, identityVerified: 'true' })).toBe(false);
    expect(hasRealIdentity({ ...observedIdentity, identityVerified: undefined })).toBe(false);
  });

  it('rejects missing and placeholder package fields even when verification is true', () => {
    expect(hasRealIdentity({ ...observedIdentity, identityName: '' })).toBe(false);
    expect(hasRealIdentity({ ...observedIdentity, identityName: 'PLACEHOLDER.Ample' })).toBe(false);
    expect(hasRealIdentity({ ...observedIdentity, publisher: undefined })).toBe(false);
    expect(hasRealIdentity({ ...observedIdentity, publisherDisplayName: '' })).toBe(false);
  });
});
