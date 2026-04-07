Create a pull request with taste documentation.

1. Run /taste-diff to check for regressions.
2. If PASS or WARN:
   a. Stage all changes.
   b. Generate a PR description that includes:
      - Taste Score delta (before → after) if available
      - Which elements were rebuilt and why
      - Which taste principles were applied
      - Any new anti-patterns discovered
   c. Create the PR via GitHub MCP.
3. If FAIL:
   a. List the regressions.
   b. Ask me if I want to fix them first or ship anyway.

Branch: $ARGUMENTS
