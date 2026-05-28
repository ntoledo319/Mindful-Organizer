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

### Project Identity
- Brand name: **Hearth** (casual / in-app). Legal: **The Hearth Project**.
- Primary domain: `hearthproject.io`.
- This project believes: Your computer should adapt to your psychology, not the other way around. Mental health tools belong in the OS layer, not buried in browser tabs.
- This project is for: People managing ADHD, anxiety, depression, OCD, PTSD, or bipolar who are tired of apps that track but don't act. Desktop workers who need their environment to respond to their state.
- This project should feel like: A quiet, attentive companion that dims the lights when you're drained, closes Discord when anxiety spikes, and protects your focus like a bodyguard. Not a dashboard. Not a therapist. The warm corner of the computer.
- This project should NEVER feel like: A wellness app. Corporate mindfulness software. A journal with ads. Anything that says "Unlock your potential" or "Supercharge your productivity."
- Must-word: hearth
- Never-word: optimize

### Taste Verification
Before any task is complete, run the Specificity Test:
"Could this element exist in any other project without modification?"
If yes → rewrite.
