import { createCipheriv, createDecipheriv, randomBytes } from 'node:crypto';

const MAGIC = Buffer.from('HEARTHDB', 'ascii');
const VERSION = 1;
const IV_BYTES = 12;
const TAG_BYTES = 16;
const HEADER_BYTES = MAGIC.length + 1 + IV_BYTES + TAG_BYTES;

export const MASTER_KEY_BYTES = 32;

export class InvalidEncryptedDatabaseError extends Error {
  constructor(message = 'The encrypted Ample database could not be authenticated.') {
    super(message);
    this.name = 'InvalidEncryptedDatabaseError';
  }
}
function assertKey(key: Buffer): void {
  if (key.length !== MASTER_KEY_BYTES) {
    throw new Error(`Ample database keys must be ${MASTER_KEY_BYTES} bytes.`);
  }
}

function authenticatedHeader(version: number): Buffer {
  return Buffer.concat([MAGIC, Buffer.from([version])]);
}

/**
 * Wrap a serialized SQLite database in a versioned AES-256-GCM envelope.
 * The IV is unique per write, and the format marker/version are authenticated
 * as additional data so a corrupted or downgraded file fails closed.
 */
export function encryptDatabase(plaintext: Buffer, key: Buffer): Buffer {
  assertKey(key);
  const iv = randomBytes(IV_BYTES);
  const aad = authenticatedHeader(VERSION);
  const cipher = createCipheriv('aes-256-gcm', key, iv);
  cipher.setAAD(aad);
  const ciphertext = Buffer.concat([cipher.update(plaintext), cipher.final()]);
  const tag = cipher.getAuthTag();
  return Buffer.concat([aad, iv, tag, ciphertext]);
}

/** Decrypt and authenticate a Ample database envelope. */
export function decryptDatabase(envelope: Buffer, key: Buffer): Buffer {
  assertKey(key);
  if (envelope.length < HEADER_BYTES) {
    throw new InvalidEncryptedDatabaseError('The encrypted Ample database is truncated.');
  }

  const magic = envelope.subarray(0, MAGIC.length);
  if (!magic.equals(MAGIC)) {
    throw new InvalidEncryptedDatabaseError('The encrypted Ample database has an unknown format.');
  }

  const version = envelope[MAGIC.length];
  if (version !== VERSION) {
    throw new InvalidEncryptedDatabaseError(`Unsupported Ample database version: ${version}.`);
  }

  const aad = envelope.subarray(0, MAGIC.length + 1);
  const ivStart = aad.length;
  const tagStart = ivStart + IV_BYTES;
  const ciphertextStart = tagStart + TAG_BYTES;
  const iv = envelope.subarray(ivStart, tagStart);
  const tag = envelope.subarray(tagStart, ciphertextStart);
  const ciphertext = envelope.subarray(ciphertextStart);

  try {
    const decipher = createDecipheriv('aes-256-gcm', key, iv);
    decipher.setAAD(aad);
    decipher.setAuthTag(tag);
    return Buffer.concat([decipher.update(ciphertext), decipher.final()]);
  } catch {
    throw new InvalidEncryptedDatabaseError();
  }
}
