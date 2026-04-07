Generate a React artifact that visualizes my project's taste trajectory.

1. Read .claude/memory/taste/score-history.md
2. Read .claude/memory/taste/principles.md
3. Read .claude/memory/taste/rejection-log.md
4. Create a React component (single .jsx file) that displays:

   a. TASTE SCORE OVER TIME — line chart using recharts
      - X axis: dates from score-history
      - Y axis: taste score percentage (0-100)
      - Color: green above 75, yellow 50-75, red below 50
      - Show trend line

   b. ELEMENT BREAKDOWN — stacked bar chart
      - Per audit: bars showing Generic / Safe-Good / Contextual / Distinctive
      - Color coded: red / yellow / blue / green

   c. DISCOVERED PRINCIPLES — scrollable list
      - Each principle with date and originating element
      - Most recent first
      - Total count prominently displayed

   d. REJECTION HEATMAP — category breakdown
      - Group rejections by category
      - Show which categories appear most often
      - These are the project's taste blind spots

   e. CRITIC VERDICT HISTORY — approval rate over time
      - Track approved / conditional / rejected ratios
      - Show if approval rate is climbing (taste muscle developing)

   Style the dashboard itself with taste:
   - Do NOT use the default recharts styling
   - Do NOT use a generic dashboard layout
   - Use a dark background with high-contrast data visualization
   - Monospace typography for data, serif for labels
   - Minimal chrome — the data is the interface
   - No decorative elements. Every pixel serves information.

5. The component should accept data as props with sensible defaults
   for demo purposes.

Output the artifact. Do not ask for permission.
