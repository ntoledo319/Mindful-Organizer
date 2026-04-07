#!/bin/bash
# Taste gate — warns on commits containing known anti-patterns

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

GENERIC_COPY=$(grep -rl --include="*.tsx" --include="*.jsx" --include="*.ts" --include="*.js" \
  -iE "(unlock the power|seamlessly|take .* to the next level|supercharge|revolutionize|empower|in today.s fast-paced)" \
  "$PROJECT_ROOT/src" 2>/dev/null | grep -v node_modules | wc -l | tr -d ' ')

GENERIC_NAMES=$(find "$PROJECT_ROOT/src" -type f \
  \( -name "Card.tsx" -o -name "Hero.tsx" -o -name "Section.tsx" \
  -o -name "Feature.tsx" -o -name "Widget.tsx" -o -name "Banner.tsx" \) \
  ! -path "*/node_modules/*" 2>/dev/null | wc -l | tr -d ' ')

TOTAL=$((GENERIC_COPY + GENERIC_NAMES))

if [ "$TOTAL" -gt 0 ]; then
  echo ""
  echo "╔══════════════════════════════════════════════════╗"
  echo "║  ⚠️  TASTE WARNING                               ║"
  echo "║  $TOTAL potential generic patterns detected.       ║"
  echo "║  Run /taste-audit to review.                     ║"
  echo "║  (This is a warning, not a block.)               ║"
  echo "╚══════════════════════════════════════════════════╝"
  echo ""
fi
