## Taste Standards

This project operates under active taste enforcement. Every code change,
UI element, copy block, and architectural decision must pass taste review.

### The Taste Hierarchy
- GENERIC: Could appear on any similar project unchanged. UNACCEPTABLE.
- SAFE-GOOD: Competent but predictable. UNACCEPTABLE.
- CONTEXTUAL: Specific to this project. MINIMUM VIABLE TASTE.
- DISTINCTIVE: Could only exist in this project. THE TARGET.

### Hard Rules
1. No statistical-average output. If it looks like a default template, rewrite.
2. Every UI component must answer: "Why does THIS project need THIS to
   look/work THIS way?"
3. Copy must have a point of view. Swap test: replace product name with
   competitor's. If it still works, the copy is dead.
4. No decoration-driven design. Every visual choice serves meaning.
5. Elimination before addition. Try removing elements first.

### Anti-Pattern Registry
These patterns are BANNED in this project. If you produce them, immediately
flag and rewrite:
- Purple-to-blue gradients on white backgrounds
- 3-column icon + heading + body card grids
- Hero sections with stock-photo-style AI imagery
- "Unlock / Revolutionize / Supercharge / Take to the next level" copy
- Glassmorphism or frosted glass used purely for aesthetics
- Geometric abstract illustrations as hero backgrounds
- The Tailwind default aesthetic (Inter font, gray-50 bg, rounded-xl cards)
- "Whether you're a [persona A] or [persona B]..." copy patterns
- Sans-serif heading + slightly lighter sans-serif body with zero personality
- Bento grid layouts copied from Vercel/Linear/Stripe marketing pages

### Project Identity (run /taste-brief to fill)
- This project believes: [FILL]
- This project is for: [FILL]
- This project should feel like: [FILL]
- This project should NEVER feel like: [FILL]
- Must-word: [FILL]
- Never-word: [FILL]

### Taste Verification
Before any task is complete, run the Specificity Test:
"Could this element exist in any other project without modification?"
If yes → rewrite.
