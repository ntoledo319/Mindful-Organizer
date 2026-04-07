---
name: taste-engineering
description: >
  Activates when the user asks to audit taste, perform a taste facelift,
  build with taste constraints, run generate-then-destroy, or apply taste
  standards. Triggers on: "taste audit", "taste facelift", "make this
  tasteful", "this looks generic", "AI slop", "looks like a template",
  "specificity test", "feels default", "too default", "escape the average",
  "rejection vocabulary", "generate and destroy", "taste score".
---

# Taste Engineering Skill

## When Activated

### For Taste Audits:
1. Read `references/anti-patterns.md` for ban list.
2. Invoke `@agent-taste-auditor` on the specified target.
3. Run `scripts/specificity-test.sh` on the target directory.
4. Compile audit report with Taste Score.
5. If score < 60%, recommend full facelift.

### For Taste Facelifts:
1. Run `@agent-taste-auditor` first.
2. For each flagged element, run `@agent-taste-destroyer`.
3. Hand principles + flagged elements to `@agent-taste-rebuilder`.
4. Final pass through `@agent-taste-critic`.
5. Run `scripts/specificity-test.sh` on modified files.

### For From-Scratch Builds:
1. Check CLAUDE.md for Project Identity fields. If empty → STOP → run
   Taste Brief process first.
2. Read `references/taste-brief.md` for identity anchors.
3. Build with rebuilder principles. Critic reviews each component.

### For Taste Brief Generation:
1. Interview user:
   a. What does this project believe that competitors don't?
   b. Name 3 generic products in this space. What DNA do they share?
   c. Name 3 things OUTSIDE this space that capture the right feeling.
   d. What should someone FEEL after 30 seconds?
   e. What will this project NEVER do?
2. Synthesize into Taste Brief → `references/taste-brief.md`
3. Update CLAUDE.md Project Identity fields.
