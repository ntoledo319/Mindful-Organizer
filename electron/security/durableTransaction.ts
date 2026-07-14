export interface TransactionState {
  depth: number;
}

/**
 * Keep nesting state correct even when durable persistence fails after SQLite
 * commits. Persistence deliberately runs outside the runner catch block so its
 * failure cannot decrement depth twice.
 */
export function runDurableTransaction(
  state: TransactionState,
  runner: (...args: unknown[]) => unknown,
  args: unknown[],
  persistIfOutermost: () => void,
): unknown {
  state.depth += 1;
  let result: unknown;
  try {
    result = Reflect.apply(runner, undefined, args);
  } catch (error) {
    state.depth = Math.max(0, state.depth - 1);
    throw error;
  }

  state.depth = Math.max(0, state.depth - 1);
  if (state.depth === 0) persistIfOutermost();
  return result;
}
