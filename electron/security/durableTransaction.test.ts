import { describe, expect, it, vi } from 'vitest';
import { runDurableTransaction, type TransactionState } from './durableTransaction';

describe('durable transaction state', () => {
  it('returns depth to zero when post-commit persistence fails', () => {
    const state: TransactionState = { depth: 0 };
    expect(() =>
      runDurableTransaction(state, () => 'committed', [], () => {
        throw new Error('disk full');
      }),
    ).toThrow('disk full');
    expect(state.depth).toBe(0);

    const persisted = vi.fn();
    expect(runDurableTransaction(state, () => 'next', [], persisted)).toBe('next');
    expect(persisted).toHaveBeenCalledOnce();
    expect(state.depth).toBe(0);
  });

  it('persists once at the outer boundary of nested transactions', () => {
    const state: TransactionState = { depth: 0 };
    const persisted = vi.fn();
    runDurableTransaction(
      state,
      () => runDurableTransaction(state, () => undefined, [], persisted),
      [],
      persisted,
    );
    expect(persisted).toHaveBeenCalledOnce();
  });
});
