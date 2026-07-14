import { randomBytes } from 'node:crypto';
import { describe, expect, it } from 'vitest';
import {
  decryptDatabase,
  encryptDatabase,
  InvalidEncryptedDatabaseError,
  MASTER_KEY_BYTES,
} from './envelope';

describe('encrypted database envelope', () => {
  it('round-trips with AES-256-GCM without embedding plaintext', () => {
    const key = randomBytes(MASTER_KEY_BYTES);
    const plaintext = Buffer.from('private journal: take the smaller next step', 'utf8');
    const encrypted = encryptDatabase(plaintext, key);

    expect(encrypted.includes(plaintext)).toBe(false);
    expect(decryptDatabase(encrypted, key)).toEqual(plaintext);
  });

  it('fails closed when ciphertext or the key is changed', () => {
    const key = randomBytes(MASTER_KEY_BYTES);
    const encrypted = encryptDatabase(Buffer.from('sensitive', 'utf8'), key);
    const tampered = Buffer.from(encrypted);
    tampered[tampered.length - 1] ^= 0x01;

    expect(() => decryptDatabase(tampered, key)).toThrow(InvalidEncryptedDatabaseError);
    expect(() => decryptDatabase(encrypted, randomBytes(MASTER_KEY_BYTES))).toThrow(
      InvalidEncryptedDatabaseError,
    );
  });

  it('uses a fresh IV for every persisted snapshot', () => {
    const key = randomBytes(MASTER_KEY_BYTES);
    const plaintext = Buffer.from('same database bytes', 'utf8');
    expect(encryptDatabase(plaintext, key)).not.toEqual(encryptDatabase(plaintext, key));
  });
});
