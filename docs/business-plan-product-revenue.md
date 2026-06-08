# Hearth — Product Description & Revenue Model

_Formerly Mindful Organizer. Document version: 1.0 | May 2026_

---

## 1. Product Overview & Value Proposition

### What Hearth Is

Hearth is a desktop-native **psychological operating system** — the first desktop application that builds a persistent psychological profile and actively reconfigures the computing environment based on real-time psychological state. Unlike traditional productivity tools that ignore the user's mental state, or wellness apps that stop at logging, Hearth closes the loop: it _measures_, _interprets_, and _acts_.

The application sits in the system tray, evaluates wellness state every 10 minutes via the `SystemAutomationEngine`, and executes evidence-informed automations across display, applications, notifications, and focus context. It is built for users whose cognitive and emotional states fluctuate significantly — ADHD, anxiety disorders, depression, bipolar spectrum, burnout — and who need their environment to adapt when they cannot.

### Core Value Proposition

> **"Your computer should understand how you feel. Hearth is the first desktop app that actually does."**

**For individuals:**

- **Proactive, not reactive:** Intervenes before a low-energy slump becomes a lost afternoon, or before an anxiety spike leads to three hours of avoidance scrolling.
- **Privacy-first by architecture:** All psychological data, ML models, and profiles are local. No cloud required. No telemetry of mental health content.
- **Evidence-informed, not aspirational:** The 14 trigger→action rules are grounded in CBT, DBT, ACT, and circadian science — not generic "wellness" platitudes.

**For the market:**

- **No direct competitor** exists at the desktop OS-intervention layer. Headspace/Calm are content libraries. RescueTime/Qustodio are surveillance/restriction tools. Notion/Todoist are passive task lists. Hearth is an _active, state-aware automation layer_.
- **Desktop moat:** Keyboard-driven workflows, deep OS integration (AppleScript, shell, display APIs), and always-on tray presence create switching costs that mobile-first apps cannot replicate.

### Ethical Boundary

Core mental health tools — tracking, crisis planning, breathing exercises, journaling, DBT diary cards — remain free forever. Revenue is generated exclusively from infrastructure, convenience, and advanced AI/automation features. This aligns monetization with user agency: we charge for _doing things on your behalf_, not for _access to care_.

---

## 2. Feature Breakdown by Tier

| Capability                   | Free                                                  | Pro ($8/mo)                                                        | Premium ($15/mo)                                   |
| ---------------------------- | ----------------------------------------------------- | ------------------------------------------------------------------ | -------------------------------------------------- |
| **Core Mental Health Tools** | ✅ Mood/energy/sleep tracking                         | ✅                                                                 | ✅                                                 |
|                              | ✅ DBT diary card                                     | ✅                                                                 | ✅                                                 |
|                              | ✅ Crisis plan & resources                            | ✅                                                                 | ✅                                                 |
|                              | ✅ Breathing & grounding exercises                    | ✅                                                                 | ✅                                                 |
|                              | ✅ Journaling with sentiment analysis                 | ✅                                                                 | ✅                                                 |
|                              | ✅ Medication tracking                                | ✅                                                                 | ✅                                                 |
|                              | ✅ 2 condition-aware themes                           | ✅ All 4 themes                                                    | ✅ All 4 themes                                    |
| **Automation Engine**        | ✅ `SystemAutomationEngine` (evaluation every 10 min) | ✅                                                                 | ✅                                                 |
|                              | ✅ Suggestions / notifications only                   | ✅                                                                 | ✅                                                 |
|                              | ❌ No system changes executed                         | ✅ Autonomous execution of default rules                           | ✅ Autonomous execution                            |
|                              | ❌ —                                                  | ✅ Display adaptation (brightness, night shift, theme)             | ✅ Display adaptation                              |
|                              | ❌ —                                                  | ✅ `FocusModeManager` (distraction app closure)                    | ✅ Focus mode                                      |
|                              | ❌ —                                                  | ✅ `AppGuardian` (blacklisted app monitoring/closing)              | ✅ AppGuardian                                     |
|                              | ❌ —                                                  | ✅ `SystemTrayController` (quick mood/energy/focus/crisis buttons) | ✅ System tray                                     |
|                              | ❌ —                                                  | ✅ `GlobalHotkeyManager` (Ctrl+Shift+F/C/G)                        | ✅ Global hotkeys                                  |
|                              | ❌ —                                                  | ✅ Ask-first execution mode                                        | ✅ Ask-first + autonomous modes                    |
| **Rules & Profiles**         | ✅ 14 default trigger→action rules                    | ✅ 14 default rules                                                | ✅ 14 default rules                                |
|                              | ❌ —                                                  | ❌ —                                                               | ✅ Custom rule builder (UI + conditions)           |
|                              | ❌ Single profile                                     | ❌ Single profile                                                  | ✅ Multiple automation profiles                    |
|                              | ❌ —                                                  | ❌ —                                                               | ✅ Scheduled focus blocks (calendar-aware)         |
| **Analytics & Intelligence** | ✅ Basic wellness summary                             | ✅ Energy predictor                                                | ✅ `AutomationAnalytics`                           |
|                              | ❌ —                                                  | ❌ —                                                               | ✅ Effectiveness tracking ("Did this rule help?")  |
|                              | ❌ —                                                  | ❌ —                                                               | ✅ Focus trend dashboards                          |
|                              | ❌ —                                                  | ❌ —                                                               | ✅ Weekly automation summaries                     |
|                              | ❌ —                                                  | ❌ —                                                               | ✅ Advanced system integrations (future API hooks) |
| **Platform Support**         | macOS, Linux, Windows (stubs)                         | ✅ macOS full, Win/Linux improving                                 | ✅ All platforms + priority support                |
| **Trial**                    | —                                                     | 14-day Premium trial                                               | 14-day Premium trial                               |

### Rule Coverage (14 Evidence-Informed Automations)

1. **Energy Peak** → Launch focus session, close distraction apps, enable deep-work display profile.
2. **Energy Trough** → Reduce brightness, switch to low-cognitive-load theme, suggest 2-min breathing.
3. **Anxiety Spike** → Close social/news apps, enable grounding theme, surface crisis plan.
4. **ADHD Slump** → Simplify UI chrome, disable animations, prompt single-task mode.
5. **Burnout Risk** → Flag 14-day low-energy trend, enforce break reminders, suggest journaling.
6. **Hypomania Signal** → Flag elevated energy + reduced sleep trend, suggest sleep hygiene, log prompt.
7. **Sleep Debt** → Warmer display after 9 PM, delayed notifications, energy-adjusted task list.
8. **Crisis Indicators** → Immediate soft intervention (not alarmist), surface crisis resources, notify trusted contact (opt-in).
9. **Circadian Morning** → Gradual brightness increase, focus-mode prompt, high-priority task surfacing.
10. **Circadian Evening** → Dimming schedule, app wind-down list, journal prompt.
11. **Task Overload** → Collapse non-essential UI, suggest task deferral, enable Pomodoro.
12. **Social Media Spiral** → AppGuardian closure after threshold, suggest alternative activity.
13. **Medication Miss** → Soft reminder, adjust predicted energy, downgrade task difficulty suggestion.
14. **Post-Crisis Recovery** → Reduced automation intensity, gratitude prompt, gentle re-engagement schedule.

---

## 3. Technical Architecture Summary

Hearth is a desktop-native Python application designed for deep OS integration, local ML inference, and real-time automation.

| Layer                    | Component                 | Technology                                                     | Responsibility                                                                               |
| ------------------------ | ------------------------- | -------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| **Automation Core**      | `SystemAutomationEngine`  | Python 3.12, threading                                         | Central conductor; evaluates wellness state every 10 min; maintains automation state machine |
|                          | `AutomationConfigManager` | PyQt6, SQLite                                                  | Rule persistence, profile management, scheduling logic                                       |
|                          | `AutomationAnalytics`     | scikit-learn (RandomForest), pandas                            | Effectiveness modeling, trend detection, weekly report generation                            |
| **Platform Abstraction** | `PlatformActions`         | macOS: AppleScript + shell; Win/Linux: stubs + PowerShell/bash | Cross-platform system execution (brightness, apps, notifications, display)                   |
| **User Interface**       | `SystemTrayController`    | PyQt6 QSystemTrayIcon                                          | Always-on tray with quick-action buttons and status indicator                                |
|                          | `GlobalHotkeyManager`     | pynput / native hotkey registration                            | Global shortcuts (Ctrl+Shift+F/C/G) for focus, calm, grounding                               |
|                          | Main Dashboard            | PyQt6, Chart.js (embedded)                                     | Wellness visualization, rule status, manual override controls                                |
| **Focus & Guard**        | `FocusModeManager`        | Platform-specific process APIs                                 | Deep-work session orchestration: app closure, DND, timer                                     |
|                          | `AppGuardian`             | Process monitoring (psutil)                                    | Blacklist enforcement, usage-threshold detection, soft/hard closure                          |
|                          | `DisplayAdaptationEngine` | macOS CoreDisplay / Windows WMI / Linux ddcutil                | Brightness, night shift, color temperature, theme switching                                  |
| **Data & ML**            | Local Profile Store       | SQLite (encrypted at rest)                                     | Psychological profile, historical wellness data, rule effectiveness scores                   |
|                          | Inference Engine          | scikit-learn RandomForest                                      | Real-time classification of psychological state from mood/energy/sleep/task signals          |
| **Quality**              | Test Suite                | pytest                                                         | 6,200+ lines of tests across 23 test files; CI via GitHub Actions                            |
|                          | Code Quality              | ruff, mypy                                                     | Linting, formatting, type checking                                                           |

### Key Technical Constraints & Moats

- **Desktop-native:** Requires OS-level APIs (AppleScript, CoreDisplay, process signals) that web apps and mobile apps cannot access. This is the technical barrier to entry.
- **Local-first ML:** RandomForest models trained on-device. No model upload. No inference latency from network calls.
- **No cloud dependency:** SQLite + optional encrypted sync (future). Users own their data. This is a marketing advantage in the mental health space.

---

## 4. Pricing Strategy & Rationale

### Price Points

| Tier        | Monthly | Annual (2 months free) | Effective Monthly |
| ----------- | ------- | ---------------------- | ----------------- |
| **Free**    | $0      | $0                     | $0                |
| **Pro**     | $8.00   | $79.99                 | $6.67             |
| **Premium** | $15.00  | $149.99                | $12.50            |

### Rationale

**Anchor: Productivity + Wellness SaaS Benchmarks**

| Comparable            | Price      | Notes                                                                                                 |
| --------------------- | ---------- | ----------------------------------------------------------------------------------------------------- |
| RescueTime Premium    | $12/mo     | Time tracking + focus sessions; no mental health layer                                                |
| Freedom (app blocker) | $8.50/mo   | Blocking only; no intelligence                                                                        |
| Headspace             | $12.99/mo  | Content only; no OS integration                                                                       |
| Notion AI             | $10/mo     | Productivity + AI; no wellness                                                                        |
| Todoist Premium       | $4/mo      | Tasks only                                                                                            |
| **Hearth Pro**        | **$8/mo**  | _Positioned between pure blockers and full wellness suites_                                           |
| **Hearth Premium**    | **$15/mo** | _Priced at parity with RescueTime + Headspace combined, but with OS-level integration neither offers_ |

**Pricing Psychology:**

- **$8 Pro** is below the "subscription fatigue" threshold of $10. It feels like a utility (like Spotify or a coffee).
- **$15 Premium** is anchored against combined tool stacks. A user paying for RescueTime + Calm + a Pomodoro timer is spending $25-30/month. Hearth Premium replaces that stack.
- **Annual discount (17% off)** is conservative but meaningful. Annual plans improve cash flow and reduce churn exposure. We do not offer aggressive 40-50% discounts to avoid training users to wait for sales.

**Why not the old $4.99/$9.99?**
The previous pricing reflected a task-manager-plus-mood-tracker. Hearth is an _automation infrastructure product_ — it modifies the OS, closes apps, adapts displays, and runs ML inference continuously. That value justifies a higher price, and the target user (knowledge worker with mental health needs) has willingness-to-pay for tools that demonstrably protect their productivity.

---

## 5. Revenue Model & Projections (3-Year Forecast)

### Model Structure

Revenue = Consumer Subscriptions + B2B (Therapist Dashboard + Enterprise Wellness)

### Assumptions (Conservative, Desktop-First)

| Metric                        | Assumption       | Source / Rationale                                                                                                         |
| ----------------------------- | ---------------- | -------------------------------------------------------------------------------------------------------------------------- |
| Organic install base (Year 1) | 4,000 users      | Desktop-only apps have lower top-of-funnel than mobile; growth via Reddit, ADHD communities, organic Windows Store traffic |
| Year-over-year user growth    | 2.5x → 2.0x      | Slowing as base expands; no paid acquisition budget in Year 1                                                              |
| Free-to-Pro conversion        | 3.5%             | Freemium SaaS benchmark for tools with strong daily utility                                                                |
| Free-to-Premium conversion    | 1.2%             | Lower conversion for higher price; offset by annual plan preference                                                        |
| Annual plan mix               | 40%              | Standard for productivity tools; improves retention                                                                        |
| Monthly churn (monthly plans) | 8%               | Conservative for consumer wellness; desktop stickiness helps                                                               |
| Monthly churn (annual plans)  | 2.5% (effective) | Annual plans reduce cancellation flexibility                                                                               |
| Blended ARPU (Pro)            | $86/year         | Mix of monthly ($96) and annual ($80)                                                                                      |
| Blended ARPU (Premium)        | $162/year        | Mix of monthly ($180) and annual ($150)                                                                                    |
| Therapist Dashboard (Year 2+) | $39/mo/seat      | Clinical tooling price point                                                                                               |
| Enterprise Wellness           | $8/employee/year | Volume B2B pricing                                                                                                         |

### 3-Year Projection

| Metric                                    | Year 1      | Year 2       | Year 3       |
| ----------------------------------------- | ----------- | ------------ | ------------ |
| **Total Registered Users**                | 4,000       | 12,000       | 28,000       |
| **Monthly Active Users (MAU)**            | 1,800       | 6,000        | 15,000       |
| **Pro Subscribers**                       | 140         | 580          | 1,400        |
| **Premium Subscribers**                   | 48          | 200          | 500          |
| **Consumer ARR**                          | $28,000     | $118,000     | $300,000     |
| **Therapist Seats**                       | 0           | 30           | 150          |
| **B2B ARR (Therapist)**                   | $0          | $14,000      | $70,000      |
| **Enterprise Employees Covered**          | 0           | 2,500        | 10,000       |
| **B2B ARR (Enterprise)**                  | $0          | $20,000      | $80,000      |
| **Total ARR**                             | **$28,000** | **$152,000** | **$450,000** |
| **Monthly Burn (Solo Dev + Contractors)** | $4,000      | $6,500       | $10,000      |
| **Gross Margin**                          | ~85%        | ~87%         | ~88%         |
| **Net Revenue (after payment fees ~5%)**  | $26,600     | $144,400     | $427,500     |

### Revenue Mix Trajectory

```
Year 1:  100% Consumer / 0% B2B
Year 2:   78% Consumer / 22% B2B
Year 3:   67% Consumer / 33% B2B
```

### Sensitivity Analysis

If conversion rates are 50% lower (2.5% Pro, 0.8% Premium):

- Year 3 Consumer ARR drops to ~$215K
- Total Year 3 ARR: ~$365K (still viable for a lean solo/contractor operation)

If B2B lands one 5,000-employee enterprise contract in Year 2:

- Adds $40K ARR immediately
- Reduces CAC burden on consumer side

---

## 6. Unit Economics

### Customer Acquisition Cost (CAC)

| Channel                                   | CAC             | Volume Potential | Primary Use                 |
| ----------------------------------------- | --------------- | ---------------- | --------------------------- |
| Organic Content (Reddit, Twitter/X, blog) | ~$5-10\*        | High             | Primary Year 1 driver       |
| SEO / long-tail content                   | ~$15-25         | Medium           | 6-12 month lag              |
| Affiliate (ADHD coaches, therapists)      | $20-30 (payout) | Medium           | Year 2 scaling              |
| Windows Store organic                     | ~$2-5           | Medium           | Always-on, low intent       |
| Paid social (Meta, Reddit ads)            | $35-55          | High             | Year 2+ only                |
| **Blended CAC (Year 1)**                  | **~$12**        | —                | Heavily organic             |
| **Blended CAC (Year 2)**                  | **~$22**        | —                | Introduce paid + affiliates |
| **Blended CAC (Year 3)**                  | **~$28**        | —                | Diversified mix             |

\* _Time cost imputed; no direct ad spend._

### Lifetime Value (LTV)

**Pro Tier:**

- Average revenue per month: $7.33 (60% monthly @ $8, 40% annual @ $6.67)
- Gross margin: 85%
- Contribution margin: $6.23/mo
- Average customer lifespan: 14 months (blended churn ~7%/mo)
- **LTV (Pro): $87**

**Premium Tier:**

- Average revenue per month: $13.50 (60% monthly @ $15, 40% annual @ $12.50)
- Gross margin: 85%
- Contribution margin: $11.48/mo
- Average customer lifespan: 18 months (blended churn ~5.5%/mo; higher engagement reduces churn)
- **LTV (Premium): $207**

**Blended LTV (weighted 70% Pro / 30% Premium): $123**

### LTV:CAC Ratio & Payback Period

| Metric                 | Year 1         | Year 2         | Year 3         |
| ---------------------- | -------------- | -------------- | -------------- |
| Blended CAC            | $12            | $22            | $28            |
| Blended LTV            | $123           | $123           | $123           |
| **LTV:CAC Ratio**      | **10.3:1**     | **5.6:1**      | **4.4:1**      |
| **CAC Payback Period** | **1.9 months** | **3.5 months** | **4.5 months** |

### Interpretation

- **Year 1** economics are exceptional because CAC is near-zero (organic/community). This funds product development without external capital.
- **Year 2-3** ratios remain healthy. SaaS benchmarks consider 3:1 good and 5:1 excellent. Our blended ratio stays above 4:1 even with paid acquisition, indicating sustainable unit economics.
- **Risk:** If organic channels saturate faster than expected, blended CAC could rise to $40+, pushing payback beyond 6 months. Mitigation: annual plans improve cash flow even if payback lengthens.

---

## 7. Free-to-Paid Conversion Strategy

### The Conversion Funnel

```
Install → Onboard (Day 0) → Activate (Day 1-3) → Habit (Day 7) → Trial Prompt (Day 10) → Convert (Day 14-24)
```

### Stage-Specific Tactics

**1. Install → Onboard (Day 0): Activation in < 3 minutes**

- Welcome: "Hearth learns how you work. Let's teach it."
- Profile builder: Conditions, typical energy patterns, work hours.
- _First magic moment:_ Manually trigger one rule (e.g., "Focus Mode") and watch Hearth close a distraction app. This demonstrates value immediately.
- Crisis plan setup (free): Builds trust and emotional investment.

**2. Onboard → Activate (Day 1-3): The First Automation**

- Day 1: SystemTrayController appears. User sees passive suggestions (free tier).
- Day 2: If user logs mood + energy, show a prediction: "Your energy usually drops at 2 PM. Want Hearth to prepare your environment?" → **Upsell to Pro**.
- Day 3: Display adaptation preview. "Your screen would have dimmed at 9 PM yesterday. Upgrade to enable this."

**3. Activate → Habit (Day 7): The Hook**

- Streak counter for mood logging (free).
- Week 1 summary: "You logged mood 5 times. Here's what we noticed." (teaser; full analytics = Premium).
- Community nudge: "Join 400+ people using Hearth for ADHD focus."

**4. Habit → Trial Prompt (Day 10): Contextual Upsell**

- Trigger: User hits a free-tier boundary (e.g., tries to enable a second automation profile, or asks for custom rules).
- Modal: "This feature requires Premium. Start your 14-day free trial — no credit card."
- Alternative: If user has high engagement but hasn't converted, offer a 7-day Pro trial as a down-sell.

**5. Trial → Convert (Day 14-24): The Decision Window**

- Day 14 of trial: Email + in-app: "Your trial ends today. Here's what Hearth did for you this week:" (personalized summary of rules triggered, focus time gained, apps closed).
- Day 16 (if not converted): Soft discount on annual plan: "Save 17% with an annual plan. Lock in your focus routine."
- Day 21: Final nudge: "Your profile and rules are saved. Upgrade anytime to re-activate."

### Anti-Patterns We Avoid

- **No dark patterns:** No surprise charges, no difficult cancellation, no pre-checked boxes.
- **No health data paywalling:** Crisis resources, breathing, mood logging remain free. Users never feel extorted during vulnerability.
- **No interstitial ads:** Upsells are contextual (feature-gated) and respectful.

### Conversion Targets

| Funnel Stage                  | Target Rate                                   |
| ----------------------------- | --------------------------------------------- |
| Install → Onboard completion  | 65%                                           |
| Onboard → Day-3 active        | 45%                                           |
| Day-3 active → Trial start    | 12%                                           |
| Trial start → Paid conversion | 25%                                           |
| **Overall install → paid**    | **~1.5%** (within freemium norms for desktop) |

---

## 8. B2B Expansion Path

### 8.1 Therapist Dashboard (Year 2)

**Product:** A HIPAA-ready web dashboard for mental health professionals to monitor patient wellness data with explicit consent.

**Features:**

- Patient roster with color-coded risk indicators (green/yellow/red based on mood trajectory).
- Diary card history with annotation tools ("Discussed sleep hygiene 5/12").
- Crisis flag alerts (real-time notification if patient activates crisis protocol).
- Export to EHR-compatible formats (HL7 FHIR, PDF summary).
- Hearth rule adherence: Did the patient allow automations? Did they override frequently?

**Pricing:**

- **$39/month per therapist seat** (annual: $390/seat).
- Patient-facing app remains free or Premium (patient choice; therapist can recommend).
- **First 3 months free** for therapists with 5+ active patient referrals.

**Go-to-Market:**

- Start with beta group of 10-15 therapists who already have patients using Hearth.
- Conference presence: ADAA (Anxiety and Depression Association of America), ISRII (International Society for Research on Internet Interventions).
- Credentialing: Pursue HIPAA Business Associate Agreement (BAA) readiness; SOC 2 Type I audit by Year 2 end.

**Market Sizing:**

- ~550,000 licensed mental health professionals in the US.
- Addressable: 5% who are tech-forward and CBT/DBT-oriented = ~27,500.
- Target: 150 seats by end of Year 3 = $70K ARR.

### 8.2 Enterprise Wellness (Year 2-3)

**Product:** White-label or co-branded Hearth deployment for Employee Assistance Programs (EAPs) and corporate wellness budgets.

**Value Proposition to Employers:**

- "Reduce context-switching and burnout-related productivity loss."
- Aggregate (anonymized) reporting: "47% of enrolled employees report improved focus scores after 60 days."
- No employer access to individual mental health data. Aggregate trends only.

**Pricing:**

- **$8 per employee per year** (volume tiers: $6 at 5,000+ employees, $5 at 20,000+).
- Includes: deployment package, admin dashboard (enrollment, aggregate reports), priority support.

**Target Customers:**

- Mid-size tech companies (200-2,000 employees) with existing wellness budgets.
- EAP providers (ComPsych, Optum, Lyra) as an embedded tool.

**Year 3 Target:** 10,000 employees covered = $80K ARR.

### 8.3 Clinical Trials & Research (Year 3+)

- Partner with academic researchers studying digital interventions for ADHD, depression, or bipolar disorder.
- Offer custom data fields, REDCap integration, and adherence tracking.
- Revenue: $15K-50K per study (custom pricing).
- Strategic value: Peer-reviewed publications generate organic credibility and SEO.

---

## 9. App Store Optimization Strategy (Windows Store)

### 9.1 Listing Copy

**App Name:** Hearth — Psychological Operating System

**Short Description (100 chars max):**

> Desktop automation that adapts to your mental state. Focus, calm, and productivity built in.

**Full Description:**

> **Hearth** is the first desktop app that builds a psychological profile and actively reconfigures your computer based on your real-time mental state.
>
> Traditional productivity tools ignore how you feel. Mindfulness apps stop at logging. Hearth closes the loop: it detects energy peaks, anxiety spikes, ADHD slumps, and burnout risk — then automatically adjusts your display, closes distractions, and guides you into focus.
>
> **How it works:**
>
> 1. **Log** your mood, energy, and sleep in seconds.
> 2. **Learn** — Hearth's local AI identifies your patterns.
> 3. **Adapt** — Your screen, apps, and notifications respond automatically.
>
> **Core features:**
>
> - **14 evidence-informed automations** for energy, anxiety, ADHD, burnout, hypomania, sleep debt, and crisis.
> - **Focus Mode** — One shortcut closes distraction apps and enables deep work.
> - **Display Adaptation** — Brightness, night shift, and theme adjust to your circadian rhythm and mood.
> - **App Guardian** — Automatically limits blacklisted apps when your state indicates risk.
> - **Crisis Support** — One-tap access to your crisis plan, breathing exercises, and trusted contacts.
> - **Privacy-first** — All data stays local. No cloud required. No mental health telemetry.
>
> **Always free:** Mood tracking, DBT diary cards, crisis planning, breathing, and journaling.
> **Pro:** Autonomous automation, focus mode, display adaptation, global hotkeys.
> **Premium:** Custom rules, multiple profiles, scheduled focus blocks, advanced analytics.
>
> 14-day free trial of Premium. No credit card required.

### 9.2 Keywords & Tags

**Primary (high volume, targeted):**
`adhd focus`, `focus timer`, `productivity automation`, `mental health tracker`, `distraction blocker`, `deep work`, `burnout prevention`

**Secondary (niche, high intent):**
`dbt diary card`, `mood tracker desktop`, `anxiety app`, `autism productivity`, `bipolar tracker`, `circadian rhythm app`, `pomodoro alternative`, `app blocker windows`

**Long-tail (low competition):**
`psychological operating system`, `adaptive desktop environment`, `energy-based task manager`, `condition-aware productivity`, `mental health automation`

### 9.3 Category Strategy

| Category                      | Position                 | Justification                                                                                 |
| ----------------------------- | ------------------------ | --------------------------------------------------------------------------------------------- |
| **Primary: Health & Fitness** | Mental health & wellness | Core value prop is psychological state management; 14 automations are wellness interventions. |
| **Secondary: Productivity**   | Task management & focus  | Secondary value is productivity enhancement via focus mode and app blocking.                  |

### 9.4 Screenshot Strategy (6 images)

1. **The Problem → Solution Hero:** Split screen. Left: chaotic desktop with 12 tabs and notifications. Right: Hearth tray menu open, "Focus Mode activated," clean desktop. Caption: "Your brain is not broken. Your environment is."

2. **System Tray Controller:** Close-up of the tray menu showing mood/energy/focus/crisis buttons. Caption: "One click. Your entire environment responds."

3. **Focus Mode in Action:** Active focus session with circular timer, current task, and list of apps that were automatically closed. Caption: "Deep work without willpower."

4. **Rule Engine Preview:** The 14 default rules with one expanded (e.g., "Anxiety Spike → Close social apps, enable grounding theme"). Caption: "14 evidence-informed automations. Zero configuration required."

5. **Wellness Dashboard:** Mood timeline, energy prediction graph, sleep debt indicator. Caption: "See your patterns. Then let Hearth act on them."

6. **Privacy & Ethics Promise:** Clean UI with a lock icon and "Your data never leaves this device." Caption: "Mental health tools should never spy on you."

### 9.5 Review Generation

- **Prompt timing:** Day 10, after a successful focus session completion. In-app: "Hearth just helped you focus for 45 minutes. Enjoying the app? Rate us on the Microsoft Store."
- **Escalation:** Day 30, power users (7+ days active) get a personalized email with a direct Store link.
- **Negative review triage:** Respond within 24 hours. Offer support email. Track common complaints for prioritization.

---

## 10. Product Roadmap (Q1–Q4)

### Q2 2026 — Foundation & Store Launch

| Milestone | Deliverable                              | Success Criteria                                   |
| --------- | ---------------------------------------- | -------------------------------------------------- |
| M1        | Windows Store submission (MSIX packaged) | Pass certification; live in Store                  |
| M2        | macOS AppleScript automation GA          | 100% of 14 rules execute reliably on macOS         |
| M3        | `AutomationAnalytics` MVP (Premium)      | Weekly summary email; basic effectiveness tracking |
| M4        | Onboarding v2.0                          | 65% completion rate; < 3 min to first automation   |
| M5        | Landing page + email capture             | Live at adaptive.app; 500 emails in 30 days        |

**Theme:** Make it findable, installable, and immediately valuable.

### Q3 2026 — Customization & Retention

| Milestone | Deliverable                            | Success Criteria                                            |
| --------- | -------------------------------------- | ----------------------------------------------------------- |
| M6        | Custom Rule Builder (Premium)          | Users can build IF-THEN rules with 5+ condition types       |
| M7        | Multiple Automation Profiles (Premium) | Work / Home / Travel profiles with quick switch             |
| M8        | Scheduled Focus Blocks                 | Calendar integration (ICS / Outlook / Google Calendar read) |
| M9        | Linux `PlatformActions` parity         | 80% rule coverage on Ubuntu/Pop!\_OS                        |
| M10       | Referral program (Pro/Premium)         | 10% of new installs from referrals by quarter end           |

**Theme:** Convert trial users to paid by making Premium indispensable.

### Q4 2026 — B2B Beta & Ecosystem

| Milestone | Deliverable                           | Success Criteria                                                |
| --------- | ------------------------------------- | --------------------------------------------------------------- |
| M11       | Therapist Dashboard (beta)            | 15 beta therapists; HIPAA BAA drafted                           |
| M12       | Encrypted Cloud Sync (Premium add-on) | End-to-end encrypted sync between 2+ desktops                   |
| M13       | Advanced Display Profiles             | Multi-monitor support, per-app color filters, dyslexia overlays |
| M14       | Community Template Library            | 20+ community-submitted rule templates                          |
| M15       | Annual retention push                 | 40% of eligible monthly users convert to annual                 |

**Theme:** Build the B2B wedge and reduce churn through ecosystem lock-in.

### Q1 2027 — Scale & Enterprise

| Milestone | Deliverable                | Success Criteria                                                             |
| --------- | -------------------------- | ---------------------------------------------------------------------------- |
| M16       | Enterprise Admin Dashboard | Bulk license distribution, SSO (SAML), aggregate reporting                   |
| M17       | First Enterprise Pilot     | 1 paid pilot (500+ employees)                                                |
| M18       | Mobile Companion (MVP)     | iOS/Android mood/energy quick-log + crisis button; syncs via encrypted cloud |
| M19       | Wearable Integration       | Apple Health / Google Fit sleep import; Oura Ring readiness scores           |
| M20       | ML Model Improvements      | Gradient-boosted models; 20% improvement in energy prediction accuracy       |

**Theme:** Expand TAM beyond desktop-only constraint.

---

## Appendices

### A. Competitor Positioning Map

```
                    High OS Integration
                           |
        Hearth ●         |
                           |
    RescueTime ●           |   ● Freedom
                           |
    ———————————————————————+———————————————————————
    Passive Logging        |        Active Blocking
                           |
    ● Notion               |
                           |   ● Headspace
    ● Todoist              |
                           |
                    Low OS Integration
```

Hearth occupies the unique quadrant: **high OS integration + mental health awareness**.

### B. Risk Factors to Unit Economics

1. **Desktop TAM ceiling:** The total addressable market for desktop-only wellness apps is smaller than mobile. Roadmap Q1 2027 addresses this with mobile companion.
2. **OS API fragility:** macOS and Windows may restrict automation APIs (e.g., AppleScript deprecation, Windows Store sandboxing). Mitigation: maintain native packaging outside Store as fallback.
3. **Churn from over-automation:** Users may find autonomous rules intrusive. Mitigation: "Ask-first" mode in Pro; granular rule toggles; effectiveness feedback loops.
4. **B2B sales cycle:** Therapist and enterprise sales cycles are 3-6 months. Mitigation: start beta early (Q4 2026); do not depend on B2B for Year 1 revenue.

---

_Document maintained by Product Strategy. Updated quarterly against actuals._
