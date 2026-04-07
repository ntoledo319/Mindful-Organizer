Review changed files for taste regression before PR.

1. git diff --name-only HEAD~1 (or staged files)
2. For each changed file, quick @agent-taste-auditor:
   - Flag only GENERIC or SAFE-GOOD elements
   - Check anti-pattern registry
   - Check component names (specificity test)
   - Check new copy (swap test)
3. Classify each flag:
   - NEW regression → BLOCK
   - Pre-existing debt → WARN
4. Output:
   - PASS: No regressions. Ship it.
   - WARN: [N] pre-existing generic elements touched but not improved.
   - FAIL: [N] new generic elements. Fix before merging.
