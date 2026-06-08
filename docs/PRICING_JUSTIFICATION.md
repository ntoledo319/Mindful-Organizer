# Pricing Justification for Hearth v1.1.0

## Summary

Hearth’s subscription prices increased with the v1.1.0 release to reflect a substantially expanded feature set and deeper OS-level integration. The app has evolved from a task-manager-plus-mood-tracker into a **psychological operating system** that actively reconfigures the desktop environment based on real-time mental state.

| Tier    | Monthly | Annual (2 months free) | Effective Monthly |
| ------- | ------- | ---------------------- | ----------------- |
| Free    | $0      | $0                     | $0                |
| Pro     | $8.00   | $79.99                 | $6.67             |
| Premium | $15.00  | $149.99                | $12.50            |

## What Changed

- **Pro**: $4.99/month → **$8.00/month** ($39.99/year → **$79.99/year**)
- **Premium**: $9.99/month → **$15.00/month** ($79.99/year → **$149.99/year**)

## Why the Increase Is Warranted

### New Features in v1.1.0

1. **Focus Sessions / Pomodoro Widget**
   - Circular visual timer with gentle animations.
   - Do-Not-Disturb integration to protect attention.
   - Session history and productivity trend tracking.
   - _Value_: Replaces standalone focus timers; tied directly to the automation engine.

2. **Voice Journaling**
   - Record journal entries directly in the app.
   - Transcription-ready when `sounddevice` is available.
   - _Value_: Low-friction emotional logging for users who struggle with typing during distress.

3. **Personal Insights Engine**
   - Generates real insights from the user’s own historical data.
   - No generic templates — every observation is data-driven.
   - _Value_: Transforms raw tracking into actionable self-knowledge.

4. **PDF Export**
   - One-click export of wellness reports, diary cards, and mood timelines.
   - Clinician-ready formatting for therapy sessions.
   - _Value_: Bridges the gap between self-tracking and professional care.

5. **Enhanced Auto-Updater**
   - In-app changelog viewer.
   - Direct download links; no manual version checking.
   - _Value_: Keeps users on the latest, most secure build effortlessly.

6. **Security Hardening**
   - Vault encryption keys enforced in OS keyring.
   - Hardened Ed25519 license validation.
   - HTTPS-only update channels.
   - _Value_: Mental health data deserves bank-grade protection.

7. **Improved GUI Test Coverage**
   - More reliable UI behavior across macOS, Linux, and Windows.
   - Reduced flaky-test rate in CI.
   - _Value_: A product that behaves predictably is a product users can trust.

### Ethical Boundaries Preserved

- **Free tier remains genuinely usable.** Crisis support, basic tasks, mood tracking, breathing exercises, DBT diary cards, and journaling are still free forever.
- **No health-data paywalling.** Users are never extorted during vulnerability.
- **Existing subscribers get everything.** All new features are included for current Pro and Premium users at their existing rate until renewal.

## Market Positioning

| Comparable Tool       | Price      | What Hearth Replaces                               |
| --------------------- | ---------- | -------------------------------------------------- |
| RescueTime Premium    | $12/mo     | Time tracking + focus sessions (no mental health)  |
| Freedom (app blocker) | $8.50/mo   | Blocking only (no intelligence)                    |
| Headspace             | $12.99/mo  | Content library (no OS integration)                |
| Notion AI             | $10/mo     | Productivity + AI (no wellness layer)              |
| **Hearth Pro**        | **$8/mo**  | _Automation + focus + wellness, OS-integrated_     |
| **Hearth Premium**    | **$15/mo** | _Replaces RescueTime + Headspace + Pomodoro stack_ |

## Conclusion

The price increase is not arbitrary. It reflects a product that now modifies the OS, closes apps, adapts displays, runs ML inference locally, and protects mental health data with production-grade security. Users paying for RescueTime + Calm + a Pomodoro timer are spending **$25–30/month**. Hearth Premium replaces that entire stack at **$15/month** — with deeper integration and genuine privacy.

**More value. Sustainable development. Transparent pricing.**
