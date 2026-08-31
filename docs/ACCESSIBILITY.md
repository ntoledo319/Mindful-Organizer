# Paulatim Accessibility Status

_Last updated: 2026-08-31_

_Visible-name correction — 2026-08-28: the dated accessibility review remains
the Hearth-era source record; product wording is now Paulatim. No conformance
claim was added, and the Store-signed manual matrix remains open._

_Publication correction — 2026-08-31: Microsoft certified exact PAULATIM-001
and Paulatim 1.1.1 is publicly available in the United States Store market.
Certification evidence is preserved,
but the physical-Windows keyboard, Narrator, forced-colors, contrast, scaling,
reduced-motion, and modal-focus matrix remains unobserved. No Store or formal
accessibility conformance declaration is claimed._

Paulatim is designed to reduce cognitive load, but no formal accessibility
conformance claim has been completed for the current Store release.

## Present in the source

- Native buttons, text inputs, text areas, checkboxes, and range inputs in core
  flows
- Visible focus styling on primary interactive controls
- Keyboard focus trapping and Escape handling in the shared modal
- Semantic navigation, dialog, tab, switch, status, and alert markup in core
  flows
- Light, dark, and match-system appearance choices
- Atkinson Hyperlegible for body copy
- Text alternatives or intentionally empty alternatives on reviewed images
- A reduced-motion media query that removes nonessential transitions and
  animations when the operating-system preference is enabled
- Automated theme-token contrast checks for reviewed foreground/background
  pairs

These implementation details are not a substitute for testing with people or
assistive technology.

## Required before a Store accessibility declaration

- Complete every first-run and core task with keyboard only on supported Windows
- Test Narrator reading order, names, state, error feedback, and live regions
- Check light and dark color contrast, Windows high-contrast mode, and
  forced-colors behavior
- Test Windows text scaling, browser zoom, and the minimum supported window size
- Verify the implemented reduced-motion behavior across every release flow
- Check focus visibility and restoration after every dialog and route change

Completed platform evidence: Microsoft certification passed on 2026-08-31 for
the exact submitted package. This does not replace any manual check above. If
an installable test-signed equivalent is ever used for local WACK, label it as
supporting evidence rather than the accepted package hash.

Until those checks pass, the Store listing must not declare screen-reader,
high-contrast, reduced-motion, WCAG, or other formal accessibility conformance.

Accessibility problems can be reported through the channel described in
[SUPPORT.md](SUPPORT.md). Creating an issue requires GitHub sign-in. Do not
include private Paulatim records in a public report.
