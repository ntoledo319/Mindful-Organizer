Create a taste debt issue for tracking.

1. Run /taste-audit on $ARGUMENTS
2. For every GENERIC element found, create one issue in the project
   tracker (GitHub Issues or Linear via MCP) with:
   - Title: "Taste Debt: [element name] — [classification]"
   - Body: The auditor's assessment, including what pattern it
     reproduces and the suggested replacement
   - Label: "taste-debt"
   - Priority: based on visibility (user-facing = high, internal = low)
3. Create one umbrella issue linking all individual items:
   "Taste Overhaul: [scope] — Current Score: [X]%"

Target: $ARGUMENTS
