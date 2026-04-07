#!/bin/bash
# Specificity Test — finds copy and names that are too generic
TARGET_DIR="${1:-.}"

echo "═══════════════════════════════════════════════"
echo "  SPECIFICITY TEST"
echo "  Scanning: $TARGET_DIR"
echo "═══════════════════════════════════════════════"
echo ""

echo "── GENERIC COPY DETECTED ──"
grep -rn --include="*.tsx" --include="*.jsx" --include="*.ts" --include="*.js" --include="*.html" --include="*.md" --include="*.mdx" \
  -iE "(unlock the power|seamlessly|take .* to the next level|whether you.re|supercharge|revolutionize|empower|in today.s fast-paced|built for teams|all-in-one platform|leverage )" \
  "$TARGET_DIR" 2>/dev/null | grep -v node_modules | grep -v .next | head -30
echo ""

echo "── GENERIC COMPONENT NAMES ──"
grep -rn --include="*.tsx" --include="*.jsx" \
  -E "^(export .*)?(function|const) (Card|Hero|Section|Feature|Testimonial|Footer|Header|Sidebar|Modal|Button|Badge|Banner|Widget|Container|Wrapper|Item|List|Grid|Layout)\b" \
  "$TARGET_DIR" 2>/dev/null | grep -v node_modules | head -20
echo ""

echo "── TAILWIND DEFAULT AESTHETIC ──"
grep -rn --include="*.tsx" --include="*.jsx" --include="*.html" \
  -E "(bg-gradient-to-r from-purple|from-blue-500 to-purple|rounded-xl shadow-lg|backdrop-blur)" \
  "$TARGET_DIR" 2>/dev/null | grep -v node_modules | head -15
echo ""

echo "── FRAMEWORK DEFAULT STRUCTURE ──"
for dir in "components/ui" "components/common" "components/shared" "components/layout"; do
  if [ -d "$TARGET_DIR/$dir" ]; then
    echo "  ⚠️  $dir/ — framework default. Consider domain-based organization."
  fi
done
echo ""

echo "── GENERIC FILE NAMES ──"
find "$TARGET_DIR" -type f \( -name "Card.tsx" -o -name "Hero.tsx" -o -name "Section.tsx" \
  -o -name "Feature.tsx" -o -name "Widget.tsx" -o -name "Banner.tsx" \
  -o -name "Container.tsx" -o -name "Wrapper.tsx" \) \
  ! -path "*/node_modules/*" 2>/dev/null | head -10
echo ""

GENERIC_COUNT=$(grep -rl --include="*.tsx" --include="*.jsx" --include="*.ts" --include="*.js" \
  -iE "(unlock the power|seamlessly|take .* to the next level|supercharge|revolutionize|empower)" \
  "$TARGET_DIR" 2>/dev/null | grep -v node_modules | wc -l | tr -d ' ')

echo "═══════════════════════════════════════════════"
echo "  Files with generic patterns: $GENERIC_COUNT"
echo "  Ask: 'Could this exist in any other project"
echo "  without modification?'"
echo "═══════════════════════════════════════════════"
