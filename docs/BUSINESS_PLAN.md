# Hearth — Business Plan

*The first desktop-native psychological operating system.*

**Version:** 1.0  
**Date:** May 2026  
**Status:** Formal business plan for investor, partner, and internal strategic review

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Brand Strategy & Positioning](#2-brand-strategy--positioning)
3. [Market Analysis](#3-market-analysis)
4. [Product & Revenue Model](#4-product--revenue-model)
5. [Go-to-Market Strategy](#5-go-to-market-strategy)
6. [Marketing & Content Strategy](#6-marketing--content-strategy)
7. [Financial Projections](#7-financial-projections)
8. [Product Roadmap](#8-product-roadmap)
9. [Risks & Mitigations](#9-risks--mitigations)
10. [Appendices](#10-appendices)

---

## 1. Executive Summary

Hearth is the first desktop-native **psychological operating system** — an application that builds a clinical-grade psychological profile and actively reconfigures the computing environment based on real-time psychological state. Unlike mobile wellness apps that track symptoms and offer suggestions, Hearth exists at the OS layer: it kills applications when anxiety spikes, dims the display when depression flattens energy, enforces Do Not Disturb during manic windows, and reorganizes files to match cognitive capacity.

The product serves people managing ADHD, anxiety, depression, OCD, PTSD, and bipolar disorder who have abandoned browser-based trackers because **tracking does not change outcomes**. Hearth operates on an ethical freemium model: core mental health tools remain free forever, while autonomous execution, custom automation rules, and longitudinal analytics drive paid tiers at $8/month (Pro) and $15/month (Premium).

**The Market:** The digital mental health market will reach $17.9B by 2030, yet 90%+ of mental health apps are mobile-only. Hearth attacks the **$2.1B desktop wellness whitespace** — the intersection of knowledge work and psychological state management. No competitor combines tracking + profiling + proactive system adaptation.

**The Team:** Solo founder + contractor model. 73 source files, 30,000+ lines of production Python, 6,200+ lines of tests, all passing. Windows Store-ready with MSIX packaging, macOS AppleScript backend, and Linux stubs.

**The Ask:** This plan is built for execution without external capital. Year 1 is organic/community-driven. Year 2 introduces paid acquisition and B2B channels. Year 3 targets $450K ARR with healthy 4.4:1 LTV:CAC economics.

---

## 2. Brand Strategy & Positioning

### Brand Purpose
We exist because the computing environment is the most influential and least accountable force in modern mental health. Every notification, open tab, and bright pixel is a stimulus with clinical consequences — and until now, no tool has treated the desktop as a therapeutic intervention surface. Hearth makes the computer itself a partner in psychological stability.

### Vision
A world where people with psychiatric conditions do not spend cognitive energy fighting their tools. Where the devices they work on recognize their state and modify themselves accordingly — quietly, without spectacle, with the same inevitability as a thermostat responding to temperature.

### Mission
To embed evidence-based mental health support into the operating system layer, making proactive environmental adaptation the default behavior of personal computing — not a feature to be remembered, launched, and maintained.

### Brand Values

| Value | Definition | Behavioral Manifestation |
|-------|-----------|--------------------------|
| **Action Over Awareness** | Insight without intervention is a failed intervention | Every data point triggers a mechanical response; analytics are calibration inputs, not charts for contemplation |
| **System-Level Integrity** | If we cannot modify the actual computing context, the feature does not ship | Desktop-native architecture; tested against real system states; explicit documentation of capabilities |
| **Evidence-Based Ruthlessness** | Rules derived from clinical literature, not productivity folklore | 14 core rules cite clinical origins; CBT/DBT/ACT/ERP implemented by condition |
| **Dignity Through Invisibility** | Mental health support should not require performance | Crisis states trigger changes without dialogs; gamification is optional and disableable; no engagement pings |
| **Core Access as Infrastructure** | Basic mental health tooling is not a luxury good | Tracking, diary cards, breathing, crisis plans free forever; revenue from infrastructure, not care access |

### Brand Personality
Hearth behaves like a **competent bodyguard** who has worked with you long enough to anticipate trouble. Not chatty. Not clinical. Not optimistic. Observant, decisive, and slightly ahead of the moment.

**Voice Rules:**
- Never infantilize (no "Hey there!", no exclamation points in system messages)
- Never medicalize (we do not diagnose; we operationalize research)
- **Never optimize** (the word and concept are excluded)
- Never celebrate for show (no confetti for streaks; the reward is a system that works better tomorrow)

### Positioning Statement
For desktop workers managing ADHD, anxiety, depression, OCD, PTSD, or bipolar disorder, Hearth is the desktop-native psychological operating system that reconfigures the computing environment in real time based on psychological state. Unlike mobile mood trackers or browser-based CBT apps that require the user to remember to engage, Hearth acts proactively at the OS layer — closing applications, adjusting brightness, enforcing focus states, and reorganizing files before the user recognizes they need it.

### Competitive Differentiation

| Dimension | Hearth | Bearable | Daylio | Sanvello | Headspace | Freedom | f.lux |
|-----------|----------|----------|--------|----------|-----------|---------|-------|
| Platform Depth | Desktop-native (system-level) | Mobile/web | Mobile | Mobile/web | Mobile/web | Desktop (blocking only) | Desktop (display only) |
| Intervention Model | Proactive automation | Reactive tracking | Reactive tracking | Reactive CBT | Reactive meditation | Reactive blocking | Reactive display |
| Psychological Profile | Built-in clinical profile | Symptom tracking | Mood journal | General anxiety | None | None | None |
| System Reconfiguration | Full (apps, brightness, DND, themes, files) | None | None | None | None | App blocking only | Display temp only |
| Evidence Base | 14 clinical automation rules | User-reported correlation | User-reported correlation | CBT curriculum | Mindfulness research | Willpower substitution | Circadian research |
| Revenue Ethics | Core tools free forever | Subscription for insights | Subscription for features | Subscription for CBT | Subscription for content | Subscription for scheduling | Free (donation) |

**Key insight:** No competitor combines **tracking + profiling + proactive system adaptation**. This is a category difference, not a feature difference.

---

## 3. Market Analysis

### TAM / SAM / SOM

| Market | Size | Rationale |
|--------|------|-----------|
| **TAM** | $17.9B (2030) | Global digital mental health market |
| **Desktop Wellness Sub-TAM** | $2.1B | Desktop-native mental health + productivity whitespace; 24% CAGR |
| **SAM** | $840M | English-speaking + EU-5 knowledge workers with mental health conditions; 10% penetration at $30/yr ARPU |
| **SOM (Year 3)** | $4.2M ARR | 42,000 paying users at $100 ARPU; validated by Reddit community sizing and therapist referral modeling |

### Market Trends

1. **Mental health prevalence rising** — 21% of US adults experienced mental illness in 2023 (NAMI)
2. **Desktop screen time is sticky** — Knowledge workers average 6.5 hrs/day; post-pandemic hybrid work locked in
3. **Context-switching crisis** — Average worker checks email every 6 minutes; 23 minutes to recover focus per switch (UC Irvine)
4. **Mental health app fatigue** — 80% of apps abandoned within 7 days; mobile D30 retention averages 4%
5. **Neurodivergence in workforce** — ADHD diagnosis in adult women up 344% (2010–2022)

### Target Personas

**Persona 1: "Overwhelmed Olivia" — Undiagnosed High-Performer**
- 28, UX designer, $95K, remote-first
- Self-diagnosed ADHD (inattentive) + GAD; not medicated by choice
- 8–10 hrs/day on MacBook; 40+ tabs; checks email every 4 minutes
- Current stack: Notion, Freedom, Headspace, Apple Reminders, Bearable (abandoned)
- **Job-to-be-Done:** *Help me create a desktop environment that enforces my intentions without me having to constantly police myself.*
- **Willingness to Pay:** High — already spends $25/mo on productivity tools

**Persona 2: "Steady Sam" — Managed Bipolar Developer**
- 34, senior backend engineer, $145K, hybrid
- Bipolar II; on lamotrigine + therapy; tracks mood rigorously
- 10+ hrs/day on Linux + Windows; uses eMoods daily; notices hypomania via commit velocity
- **Job-to-be-Done:** *Detect my state shifts before I do, and gently constrain my environment to prevent destructive patterns.*
- **Willingness to Pay:** Very high — views as medical infrastructure; would pay $20/mo+

**Persona 3: "Graduate Gia" — Student in Crisis**
- 21, CS grad student, $28K stipend
- Panic disorder + MDD; on sertraline; waitlisted for CBT
- 12+ hrs/day on laptop; Netflix/YouTube as avoidance; loses days to dissociative scrolling
- **Job-to-be-Done:** *Be the external executive function I don't have right now — reshape my computer so I can't hurt myself with it.*
- **Willingness to Pay:** Low direct; high indirect via parents, university disability services, or insurance

---

## 4. Product & Revenue Model

### Product Overview
Hearth measures, interprets, and acts. It sits in the system tray, evaluates wellness state every 10 minutes, and executes evidence-informed automations across display, applications, notifications, and focus context.

**Core Value Proposition:** *"Your computer should understand how you feel. Hearth is the first desktop app that actually does."*

### Feature Tiers

| Capability | Free | Pro ($8/mo) | Premium ($15/mo) |
|---|---|---|---|
| Core Mental Health Tools (tracking, diary card, crisis plan, breathing, journaling, medication) | ✅ | ✅ | ✅ |
| Automation Engine (evaluation every 10 min) | ✅ Suggestions only | ✅ Autonomous execution | ✅ Autonomous execution |
| Display Adaptation (brightness, night shift, theme) | ❌ | ✅ | ✅ |
| Focus Mode + App Guardian | ❌ | ✅ | ✅ |
| System Tray + Global Hotkeys | ❌ | ✅ | ✅ |
| 14 Default Rules | ✅ | ✅ | ✅ |
| Custom Rule Builder | ❌ | ❌ | ✅ |
| Multiple Automation Profiles | ❌ | ❌ | ✅ |
| Scheduled Focus Blocks | ❌ | ❌ | ✅ |
| Automation Analytics | ❌ | ❌ | ✅ |
| Trial | — | 14-day Premium | 14-day Premium |

### The 14 Evidence-Informed Automation Rules

1. **Energy Peak** → Launch focus session, close distractions, enable deep-work display
2. **Energy Trough** → Reduce brightness, switch to low-cognitive-load theme, suggest breathing
3. **Anxiety Spike** → Close social/news apps, enable grounding theme, surface crisis plan
4. **ADHD Slump** → Simplify UI, disable animations, prompt single-task mode
5. **Burnout Risk** → Flag 14-day low-energy trend, enforce breaks, suggest journaling
6. **Hypomania Signal** → Flag elevated energy + reduced sleep, suggest sleep hygiene
7. **Sleep Debt** → Warmer display after 9 PM, delayed notifications, adjusted task list
8. **Crisis Indicators** → Soft intervention, surface resources, notify trusted contact (opt-in)
9. **Circadian Morning** → Gradual brightness increase, focus-mode prompt, high-priority surfacing
10. **Circadian Evening** → Dimming schedule, app wind-down list, journal prompt
11. **Task Overload** → Collapse non-essential UI, suggest deferral, enable Pomodoro
12. **Social Media Spiral** → App Guardian closure after threshold, suggest alternative activity
13. **Medication Miss** → Soft reminder, adjust predicted energy, downgrade task difficulty
14. **Post-Crisis Recovery** → Reduced automation intensity, gratitude prompt, gentle re-engagement

### Technical Architecture

| Layer | Component | Technology |
|-------|-----------|------------|
| Automation Core | `SystemAutomationEngine` | Python 3.12, threading |
| | `AutomationConfigManager` | PyQt6, SQLite |
| | `AutomationAnalytics` | scikit-learn RandomForest |
| Platform Abstraction | `PlatformActions` | macOS: AppleScript + shell; Win/Linux: stubs |
| User Interface | `SystemTrayController`, `GlobalHotkeyManager` | PyQt6, pynput |
| Focus & Guard | `FocusModeManager`, `AppGuardian` | psutil, process APIs |
| Display | `DisplayAdaptationEngine` | CoreDisplay / WMI / ddcutil |
| Data & ML | Local Profile Store | SQLite (encrypted at rest) |
| Quality | Test Suite | pytest (6,200+ lines, 23 test files) |

**Key moat:** Desktop-native architecture requires OS-level APIs (AppleScript, CoreDisplay, process signals) that web and mobile apps cannot access. This is the technical barrier to entry.

### Pricing Rationale

| Comparable | Price | Notes |
|---|---|---|
| RescueTime Premium | $12/mo | Time tracking + focus; no mental health layer |
| Freedom | $8.50/mo | Blocking only; no intelligence |
| Headspace | $12.99/mo | Content only; no OS integration |
| **Hearth Pro** | **$8/mo** | *Between pure blockers and full wellness suites* |
| **Hearth Premium** | **$15/mo** | *Replaces RescueTime + Calm + Pomodoro timer stack ($25-30/mo)* |

**Psychology:** $8 Pro is below the subscription fatigue threshold of $10. $15 Premium is anchored against combined tool stacks. Annual discount is 17% (conservative, avoids training users to wait for sales).

### 3-Year Revenue Projection

| Metric | Year 1 | Year 2 | Year 3 |
|---|---|---|---|
| Total Registered Users | 4,000 | 12,000 | 28,000 |
| Pro Subscribers | 140 | 580 | 1,400 |
| Premium Subscribers | 48 | 200 | 500 |
| Consumer ARR | $28,000 | $118,000 | $300,000 |
| B2B ARR (Therapist + Enterprise) | $0 | $34,000 | $150,000 |
| **Total ARR** | **$28,000** | **$152,000** | **$450,000** |
| Gross Margin | ~85% | ~87% | ~88% |

**Sensitivity:** If conversion rates are 50% lower, Year 3 total ARR still reaches ~$365K — viable for a lean solo/contractor operation.

### Unit Economics

| Metric | Year 1 | Year 2 | Year 3 |
|---|---|---|---|
| Blended CAC | $12 | $22 | $28 |
| Blended LTV | $123 | $123 | $123 |
| **LTV:CAC Ratio** | **10.3:1** | **5.6:1** | **4.4:1** |
| **CAC Payback Period** | **1.9 months** | **3.5 months** | **4.5 months** |

Year 1 economics are exceptional because CAC is near-zero (organic/community). Year 2-3 ratios remain healthy — SaaS benchmarks consider 3:1 good and 5:1 excellent.

### B2B Expansion

1. **Therapist Dashboard (Year 2)** — $39/mo/seat. HIPAA-ready web dashboard for patient wellness monitoring with explicit consent. Target: 150 seats by Year 3 = $70K ARR.
2. **Enterprise Wellness (Year 2-3)** — $8/employee/yr. White-label deployment for EAPs and corporate wellness. Target: 10,000 employees = $80K ARR.
3. **Clinical Trials (Year 3+)** — $15K-50K/study. Academic partnerships for digital intervention research. Strategic value: peer-reviewed credibility and SEO.

---

## 5. Go-to-Market Strategy

### Launch Timeline

```
M-3 ━━ Waitlist opens, Reddit AMAs, beta recruitment
M0  ━━ Windows Store launch, Product Hunt, YouTube micro-influencers
M3  ━━ Therapist pilot begins, Discord community launch
M6  ━━ Paid Reddit + TikTok scale, first paid channel profitability
M9  ━━ macOS beta, podcast sponsorships, university outreach
M12 ━━ macOS App Store launch, first enterprise deal
M18 ━━ EU localization, 50K MAU, $2M ARR run rate
```

### Phase 0: Pre-Launch (Months -3 to 0)

| Tactic | Detail | Success Metric |
|--------|--------|----------------|
| Subreddit AMA Series | Founder AMAs in r/ADHD, r/anxiety, r/bipolar — problem-validation focused | 500+ comment threads |
| Landing Page + Waitlist | Single-page site with 60s demo video | 5,000 waitlist signups |
| Beta Cohort | 200-person closed beta with Discord feedback server | 70% D7 retention |

### Phase 1: Windows Store Launch (Months 1-3)

| Tactic | Budget | Success Metric |
|--------|--------|----------------|
| Windows Store Feature Push | $0 (relationships) | 10,000 organic downloads in M1 |
| Reddit Organic Campaign | $0 | 50K+ upvotes aggregate |
| YouTube Micro-Influencers | $5,000 | 2,000 attributed installs; CAC < $2.50 |
| Product Hunt Launch | $0 | #1 Product of the Day in Health & Wellness |

### Phase 2: Channel Expansion (Months 4-9)

| Tactic | Budget (Monthly) | Success Metric |
|--------|------------------|----------------|
| Therapist Partnership Pilot | $0 (time) | 200 referred patients; 30% convert |
| Discord Community | $2,000 | 5,000 members; 20% DAU/MAU |
| TikTok / Reels | $3,000 | 1M views/month |
| Paid Reddit Ads | $4,000 | CAC < $8; CTR > 1.2% |
| Podcast Sponsorships | $6,000 | 1,500 attributed installs |

### Viral Loop: "Desktop Before/After"

Users share a generated image showing their desktop "before Hearth" (chaos) vs. "after Hearth" (calm). One-click share to Reddit, Twitter/X, Instagram Stories.
- **Trigger:** 7-day streak of Hearth sessions
- **Reward:** Unlock exclusive "Ambassador" theme pack
- **K-factor target:** 0.3

### Referral Program: "Gift a Calm Workspace"

| Action | Reward |
|--------|--------|
| Referral signs up (free) | +3 days PRO |
| Referral upgrades to PRO | +30 days PRO |
| Referral upgrades to PREMIUM | +60 days PREMIUM |

Double-sided: Referee gets 14-day PREMIUM trial (vs. standard 7-day). Target: 25% of new signups from referrals by M12.

### North Star Metric

**"Calm Hours Created" (CHC)** — The cumulative number of focused, low-distraction, psychologically aligned hours that Hearth enables across all users.

**Target:** 1M CHC by end of Y1; 25M CHC by end of Y3.

---

## 6. Marketing & Content Strategy

### Core Narrative
The modern desktop is hostile to fragile minds. It blares the same brightness at 9:00 AM and 9:00 PM. It delivers notifications with identical urgency whether you're hyperfocused or dissociating. Hearth replaces this indifference with attentiveness.

### Strategic Principles
1. **Show, don't claim.** Demonstrate the system adapting in real time. No superlatives.
2. **Lead with the free core.** Acquire users through genuine utility, not funnel pressure.
3. **Own the desktop.** The desktop is the moat and the message.
4. **Evidence over enthusiasm.** Citations and clinician validation outweigh hype.
5. **Community before conversion.** Build spaces where users feel recognized before asking for payment.

### Content Pillar Architecture

**Pillar 1: Problem Education** (2,000–3,000 word blogs)
- "Why Your Computer Should Know When You're Anxious"
- "The Notification Economy Is Built for Interruption, Not Intention"
- "Why Manual Focus Timers Fail People with ADHD"

**Pillar 2: Research Translation** (whitepaper-style with citations)
- "The Science Behind Environmental Adaptation for ADHD"
- "Display Temperature and Affective State: What the Research Actually Says"

**Pillar 3: User Narrative** (case studies and first-person essays)
- "How Sarah's Laptop Started Protecting Her Focus"
- "48 Hours Without Manual Distraction Blockers: An Hearth User Diary"

### Free Tools as Acquisition Engines
1. **Spoon Calculator** — Interactive energy cost estimator
2. **Hearth Environment Audit** — PDF checklist for desktop wellness
3. **Focus Session Logger Template** — Notion/Obsidian/Markdown template
4. **Circadian Display Schedule Generator** — Custom f.lux-style schedule

### SEO Keyword Clusters

| Cluster | Example Keywords | Content Target |
|---------|-----------------|---------------|
| Problem-Aware | "ADHD productivity software" (1,900/mo), "anxiety focus app" (590/mo) | Pillar blogs + landing pages |
| Solution-Aware | "desktop wellness tool" (210/mo), "computer adapts to mood" (90/mo) | Feature deep-dives |
| Competitor Comparison | "Hearth vs Freedom app", "best desktop app for ADHD" (260/mo) | Honest comparison pages |
| Tool/Resource | "spoon calculator online" (210/mo), "energy tracker template" (140/mo) | Free tools + lead magnets |

### Channel Strategy

**Reddit (highest priority):** r/ADHD (1.8M), r/productivity (1.2M), r/anxiety (450K). Value-first posts, AMAs, free tools shared without signup gates. Never cross-post launch announcements to more than two subreddits.

**Twitter/X:** Research threads (2x/week), feature vignettes (2x/week), building-in-public founder narrative. Muted, captioned screen recordings only.

**YouTube:** "Hearth Lab" monthly deep-dives, "User Diaries" documentary-style videos, "Compared" honest competitor reviews.

**TikTok/Reels:** "POV: Your computer finally gets it" split-screens, therapist collaboration clips, authentic day-in-my-life vlogs. No trending audio. Original ambient sound only.

### Paid Acquisition Budget

| Channel | M1-3 Budget | M4-12 Budget |
|---------|-------------|--------------|
| Google Search (branded + problem) | $800 | $1,500 |
| Google Search (competitor) | $400 | $600 |
| Reddit Ads | $600 | $1,200 |
| Twitter/X Ads | $300 | $500 |
| YouTube Pre-Roll | $0 | $800 |
| **Total** | **$2,100** | **$4,600** |

### Email Marketing

**Newsletter: "The Hearth State"** — Weekly, Thursday mornings. Plain-text-dominant, accessible screen-reader formatting.

**Nurture Sequences:**
- **Free Tool Download:** 5-email sequence over 21 days → soft app invitation
- **App Download:** 6-email sequence over 21 days → Pro trial pitch on Day 14
- **Trial to Paid:** 6-email sequence → personalized summary of trial value, transparent pricing explanation, gentle reminder

### 90-Day Content Calendar (Post-Launch)

**Month 1:** Launch & Problem Framing
- Week 1: "Why Your Computer Should Know When You're Anxious" + HN launch + Reddit AMA
- Week 2: Hearth vs. Freedom vs. f.lux comparison + free Spoon Calculator in r/ADHD
- Week 3: User story "Sarah's Laptop" + TikTok POV content
- Week 4: "The Notification Economy" + Hearth Lab #001 video

**Month 2:** Authority & Education
- Week 5: "Science of Environmental Adaptation for ADHD" + HN submission
- Week 6: "Burnout Isn't a Time Problem" + User Diaries #002
- Week 7: Hearth vs. RescueTime comparison + free focus template
- Week 8: "Display Temperature and Affective State" + Hearth Lab #002

**Month 3:** Community & Depth
- Week 9: "I Stopped Fighting My Computer" first-person essay + ambassador program
- Week 10: "Stimulus Control in Digital Environments" + Discord Q&A with therapist
- Week 11: "48 Hours Without Manual Blockers" + r/HearthApp community launch
- Week 12: Quarterly roundup + Q2 roadmap + open Q&A Twitter Spaces

---

## 7. Financial Projections

### Revenue Mix Trajectory

```
Year 1:  100% Consumer / 0% B2B
Year 2:   78% Consumer / 22% B2B
Year 3:   67% Consumer / 33% B2B
```

### Key Financial Metrics (Year 1-3)

| Metric | Year 1 | Year 2 | Year 3 |
|---|---|---|---|
| Total ARR | $28,000 | $152,000 | $450,000 |
| Monthly Burn | $4,000 | $6,500 | $10,000 |
| Gross Margin | ~85% | ~87% | ~88% |
| Net Revenue (after 5% payment fees) | $26,600 | $144,400 | $427,500 |
| Blended CAC | $12 | $22 | $28 |
| Blended LTV | $123 | $123 | $123 |
| LTV:CAC Ratio | 10.3:1 | 5.6:1 | 4.4:1 |
| CAC Payback Period | 1.9 months | 3.5 months | 4.5 months |

### Free-to-Paid Conversion Funnel

```
Install → Onboard (Day 0) → Activate (Day 1-3) → Habit (Day 7) → Trial Prompt (Day 10) → Convert (Day 14-24)
```

| Stage | Target Rate |
|---|---|
| Install → Onboard completion | 65% |
| Onboard → Day-3 active | 45% |
| Day-3 active → Trial start | 12% |
| Trial start → Paid conversion | 25% |
| **Overall install → paid** | **~1.5%** |

### Cohort-Based LTV Sensitivity

| Cohort | LTV | Driver |
|--------|-----|--------|
| Reddit organic | $88 | Low intent; curious signups |
| Therapist referral | $520 | High trust; clinical context |
| YouTube influencer | $165 | Medium intent; parasocial trust |
| Product Hunt | $55 | Tourists; low fit |

**Strategic implication:** Prioritize therapist channel expansion. LTV is 6× Reddit cohort.

---

## 8. Product Roadmap

### Q2 2026 — Foundation & Store Launch
- M1: Windows Store submission (MSIX packaged)
- M2: macOS AppleScript automation GA
- M3: `AutomationAnalytics` MVP (Premium)
- M4: Onboarding v2.0 (65% completion; < 3 min to first automation)
- M5: Landing page + email capture live at adaptive.app

### Q3 2026 — Customization & Retention
- M6: Custom Rule Builder (Premium)
- M7: Multiple Automation Profiles (Premium)
- M8: Scheduled Focus Blocks with calendar integration
- M9: Linux `PlatformActions` parity (80% rule coverage)
- M10: Referral program (10% of new installs from referrals)

### Q4 2026 — B2B Beta & Ecosystem
- M11: Therapist Dashboard beta (15 beta therapists; HIPAA BAA drafted)
- M12: Encrypted Cloud Sync (Premium add-on)
- M13: Advanced Display Profiles (multi-monitor, per-app color filters)
- M14: Community Template Library (20+ rule templates)
- M15: Annual retention push (40% monthly → annual conversion)

### Q1 2027 — Scale & Enterprise
- M16: Enterprise Admin Dashboard (SSO, bulk licenses, aggregate reporting)
- M17: First Enterprise Pilot (500+ employees)
- M18: Mobile Companion MVP (iOS/Android quick-log + crisis button)
- M19: Wearable Integration (Apple Health, Google Fit, Oura Ring)
- M20: ML Model Improvements (20% accuracy improvement)

---

## 9. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Privacy backlash** | Medium | High | HIPAA-ready architecture; local-first data; transparent privacy policy; no data sale |
| **FDA / medical device classification** | Low | High | Pre-submission meeting Y2; maintain "wellness" (not "treatment") positioning |
| **Platform risk (Microsoft changes Store rules)** | Medium | Medium | Maintain direct-download channel; never 100% dependent on single distributor |
| **Competitor copy (Apple/Windows build native)** | Medium | High | Speed-to-market + data flywheel; 12-month lead time is defensible |
| **Desktop TAM ceiling** | Medium | Medium | Mobile companion in Q1 2027 roadmap; expands TAM beyond desktop-only |
| **OS API fragility** | Medium | High | Maintain native packaging outside Store as fallback; abstract platform layer |
| **Churn from over-automation** | Medium | Medium | "Ask-first" mode in Pro; granular rule toggles; effectiveness feedback loops |
| **Founder burnout** | Medium | High | Hire community manager by M4; automate support with condition-specific chatbot by M8 |

---

## 10. Appendices

### Appendix A: Competitor Positioning Map

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

### Appendix B: Windows Store Listing

**App Name:** Hearth — Psychological Operating System

**Short Description:** Desktop automation that adapts to your mental state. Focus, calm, and productivity built in.

**Full Description:**
> **Hearth** is the first desktop app that builds a psychological profile and actively reconfigures your computer based on your real-time mental state.
>
> Traditional productivity tools ignore how you feel. Mindfulness apps stop at logging. Hearth closes the loop: it detects energy peaks, anxiety spikes, ADHD slumps, and burnout risk — then automatically adjusts your display, closes distractions, and guides you into focus.
>
> **Always free:** Mood tracking, DBT diary cards, crisis planning, breathing, and journaling.
> **Pro:** Autonomous automation, focus mode, display adaptation, global hotkeys.
> **Premium:** Custom rules, multiple profiles, scheduled focus blocks, advanced analytics.
>
> 14-day free trial of Premium. No credit card required.

### Appendix C: Team & Operating Model

**Current Structure:** Solo founder + contractors
- Product, engineering, brand: Founder
- Community management: Contractor (M4+)
- Content creation: Contractor + ambassador program (M6+)
- B2B sales: Founder-led (Y2)

**Burn Targets:**
- Year 1: $4,000/mo (founder living expenses + contractors)
- Year 2: $6,500/mo (+ community manager + content contractor)
- Year 3: $10,000/mo (+ part-time B2B sales + customer success)

### Appendix D: Key Metrics Dashboard

| Health Metric | Red Flag | Yellow | Green |
|---------------|----------|--------|-------|
| Day 1 Retention | < 40% | 40-55% | > 55% |
| Day 7 Retention | < 20% | 20-30% | > 30% |
| Trial-to-Paid | < 15% | 15-22% | > 22% |
| Monthly Churn | > 10% | 5-10% | < 5% |
| NPS | < 0 | 0-30 | > 30 |
| App Store Rating | < 3.5 | 3.5-4.2 | > 4.2 |

---

*Hearth is not a wellness app. It is not a therapist. It is an operating system that finally acknowledges the person sitting in front of it.*

**Document Version 1.0 — Hearth Business Plan**  
*Compiled from Brand Strategy, Market Analysis, Product & Revenue, and Marketing Strategy sections.*
