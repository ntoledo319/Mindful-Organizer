# Hearth Accessibility Status

_Last updated: 2026-07-14_

Hearth is designed to reduce cognitive load, but no formal accessibility
conformance claim has been completed for the release candidate.

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
- Preserve the Microsoft Store certification result for the exact submission
  package; if an installable test-signed equivalent is used for local WACK,
  label it as supporting evidence rather than the accepted package hash

Until those checks pass, the Store listing must not declare screen-reader,
high-contrast, reduced-motion, WCAG, or other formal accessibility conformance.

Accessibility problems can be reported through the channel described in
[SUPPORT.md](SUPPORT.md). Creating an issue requires GitHub sign-in. Do not
include private Hearth records in a public report.
