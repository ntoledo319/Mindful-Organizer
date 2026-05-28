# Market Analysis & Go-to-Market Strategy

**Product:** Hearth (formerly Mindful Organizer)  
**Classification:** Desktop-Native Psychological Operating System  
**Document Version:** 1.0  
**Date:** 2026-05-05

---

## 1. TAM / SAM / SOM Analysis

### Total Addressable Market (TAM)
**$17.9B by 2030** — Global digital mental health market.

| Segment | Population / Value | Rationale |
|---------|-------------------|-----------|
| US adults with any mental illness (annual) | 53M (21%) | NAMI 2023 data; desktop-native tools capture the subset in workforce/study |
| Global knowledge workers with 6+ hrs/day desktop use | ~420M | Gartner + IDC estimates; US = ~42M |
| Intersection: knowledge workers managing diagnosed or subclinical mental health conditions | **~88M globally** | 21% × 420M; conservative given 30%+ of tech workers self-report ADHD/anxiety |
| Revenue ceiling at $15/mo average | **$15.8B ARR** | 88M × $15 × 12; bounded by market saturation and pricing pressure |

**TAM refinement:** The mental health app market ($5.2B in 2023) is mobile-saturated. Hearth is attacking the **desktop wellness whitespace**, which we estimate as a **$2.1B subsegment** within the broader TAM — growing at 24% CAGR as remote/hybrid work stabilizes and desktop screen time remains structurally high.

### Serviceable Addressable Market (SAM)
**$840M** — Desktop-first mental health and productivity tools for English-speaking markets (US, UK, CA, AU, NZ) plus EU-5.

- Target population: 28M knowledge workers with mental health conditions in English-speaking + EU-5 markets
- Assumed penetration rate: 10% within 5 years
- ARPU blended: $30/year (heavy free tier, $80/yr PRO weighted at 65%, $150/yr PREMIUM at 35%)
- **28M × 10% × $30 = $840M**

### Serviceable Obtainable Market (SOM)
**$4.2M ARR by Year 3** — Realistic capture based on zero-to-one desktop mental health OS positioning.

| Year | Active Paying Users | ARPU | ARR | Key Milestone |
|------|---------------------|------|-----|---------------|
| Y1 | 3,500 | $95 | $332K | Windows Store launch; Reddit community traction |
| Y2 | 18,000 | $100 | $1.8M | Therapist referral program live; macOS beta |
| Y3 | 42,000 | $100 | $4.2M | Premium enterprise/therapist dashboard; internationalization |

**Bottom-up sanity check:**
- r/ADHD alone: 1.8M subscribers. Converting 0.5% = 9,000 users.
- r/anxiety: 520K. Converting 0.8% = 4,160 users.
- Therapist partner pipeline (Y2): 200 therapists × 15 referred patients each × 40% conversion = 1,200 users.
- Productivity YouTube/Twitch: 3 sponsored creators × 200K avg views × 0.3% CTR × 8% sign-up × 15% pay = 216 users/campaign.

---

## 2. Market Trends & Drivers

### Macro Trends

| Trend | Data Point | Implication for Hearth |
|-------|-----------|--------------------------|
| **Mental health prevalence rising** | 21% of US adults experienced mental illness in 2023; youth (18-25) at 33% | Expanding addressable population; normalization reduces stigma around desktop "wellness" tools |
| **Desktop screen time is sticky** | Knowledge workers average 6.5 hrs/day on desktop; post-pandemic hybrid work locked in | Desktop is where people *live* — mobile apps cannot intercept context-switching, notification overload, or workflow friction |
| **Context-switching crisis** | Average worker checks email every 6 minutes; 23 minutes to recover focus per switch (UC Irvine) | Direct addressable pain; Hearth's environment reconfiguration is a unique value prop vs. mobile trackers |
| **Mental health app fatigue** | 80% of mental health apps are abandoned within 7 days; mobile retention averages 4% at D30 | Desktop embedding = higher switching costs; OS-level integration is harder to abandon than a siloed app |
| **Neurodivergence in workforce** | 15-20% of global population is neurodivergent; ADHD diagnosis in adult women up 344% (2010-2022) | Underdiagnosed, high-functioning cohort needs *environmental* support, not just CBT worksheets |
| **Regulatory tailwinds** | FDA breakthrough device pathway for digital therapeutics; HSA/FSA expansion for mental health | Future PREMIUM tier can qualify for HSA/FSA reimbursement; enterprise wellness budgets expanding |

### Behavioral Drivers

1. **The "Second Brain" Movement:** Notion, Obsidian, and Arc Browser proved users want *environmental* control over digital workspaces. Hearth extends this to psychological state.
2. **Burnout as Status Signal:** LinkedIn culture is shifting from hustle to "sustainable productivity." Hearth is positioned as a performance tool that happens to be therapeutic.
3. **DIY Psychiatry:** 60% of adults with ADHD have comorbid anxiety/depression; many are self-managing due to provider shortages. Hearth fills the gap between diagnosis and treatment.

---

## 3. Competitive Landscape

### Direct Competitors

| Competitor | Price | Strength | Weakness vs. Hearth | Hearth's Kill Shot |
|------------|-------|----------|----------------------|----------------------|
| **Bearable** | $30/yr | Rich symptom tracking; beautiful UI | Passive data collection; zero automation | Hearth *acts* on data — it doesn't just log it |
| **Daylio** | Freemium / $24/yr | Micro-journaling; low friction | Mobile-only; no system integration | Desktop OS-level reconfiguration vs. manual mood entry |
| **eMoods** | $5/mo ($60/yr) | Bipolar-specific; clinician reports | Niche scope; 2003-era UI; no automation | Broader condition coverage; modern UX; proactive environment changes |
| **Sanvello** | $8/mo ($96/yr) | CBT exercises; guided journeys | Mobile-first; no desktop presence; reactive | Proactive desktop environment tuning; intercepts distress before coping exercises are needed |

### Indirect Competitors

| Competitor | Price | Strength | Weakness vs. Hearth | Hearth's Kill Shot |
|------------|-------|----------|----------------------|----------------------|
| **Headspace** | $13/mo | Brand recognition; content library | Meditation is reactive; no environmental control | Prevents the need for emergency meditation by shaping the workspace |
| **Freedom** | $8.50/mo ($65/yr) | Brute-force blocking; cross-platform | Dumb blocking; ignores psychological state; user circumvents when manic/hyperfocused | Context-aware blocking — blocks Twitter when anxiety spikes, not when deep in flow |
| **f.lux** | Free | Circadian display tuning | No wellness data; no integration; one lever | Multi-lever psychological tuning (notifications, apps, color, sound, layout) + feedback loop |
| **Notion / Obsidian** | Free-$10/mo | Workspace customization | Manual; no psychological intelligence | Auto-reconfigures workspace based on real-time state, not static templates |
| **macOS Focus Modes / Windows Do Not Disturb** | Free | Native; no cost | No psychological awareness; binary on/off | Granular, state-aware automation with longitudinal learning |

### Competitive Moat Analysis

**Why Hearth wins:**
1. **Data flywheel:** Every interaction trains the psychological model. Competitors have no desktop behavioral data stream.
2. **Switching costs:** OS-level integration (file organization, app launching, notification rules) creates embeddedness that mobile trackers cannot match.
3. **Regulatory moat:** If Hearth achieves FDA breakthrough designation as a digital therapeutic (3-5 year horizon), it becomes prescribable — a class competitors cannot enter without equivalent desktop instrumentation.
4. **Network effects (B2B2C):** Therapist dashboard sharing patient summaries creates a two-sided lock-in.

---

## 4. User Personas

### Persona 1: "Overwhelmed Olivia" — The Undiagnosed High-Performer

| Attribute | Detail |
|-----------|--------|
| **Demographics** | 28, UX designer, Brooklyn, $95K salary, remote-first company |
| **Condition** | Self-diagnosed ADHD (inattentive type); GAD; not medicated by choice |
| **Desktop Behavior** | 8-10 hrs/day on MacBook Pro; 40+ browser tabs; 6 Slack workspaces; Notion dashboard as "command center"; checks email every 4 minutes; works in 15-min bursts |
| **Current Stack** | Notion (task management), Freedom (blocking), Headspace (emergency meditation), Apple Reminders (forgetting things), Bearable (tried; abandoned in 3 days) |
| **Pain Points** | "I know what I should do but my brain won't let me do it." Starts day with intention; by 11am is in a tab-shame spiral. Guilt cycle from unfinished tasks. Sensory overload from notification badges. |
| **Job-to-be-Done** | *Help me create a desktop environment that enforces my intentions without me having to constantly police myself.* |
| **Willingness to Pay** | High — already spends $25/mo on productivity tools. Will pay $15/mo for something that "just works" without willpower. |
| **Acquisition Channel** | Reddit r/ADHD, r/productivity; ADHD YouTubers (How to ADHD, Jessica McCabe); Twitter/X threads on burnout |
| **Activation Moment** | First time Hearth auto-closes 30 tabs at 10pm and replaces them with a "wind-down" workspace — and she actually sleeps instead of doom-scrolling. |

### Persona 2: "Steady Sam" — The Managed Bipolar Developer

| Attribute | Detail |
|-----------|--------|
| **Demographics** | 34, senior backend engineer, Austin, $145K salary, hybrid office |
| **Condition** | Bipolar II; on lamotrigine + therapy; tracks mood rigorously |
| **Desktop Behavior** | 10+ hrs/day on Linux (work) + Windows (personal); uses eMoods daily; keeps spreadsheets of sleep and coding output; notices hypomania via commit velocity spikes |
| **Current Stack** | eMoods (tracking), GitHub (velocity proxy for mood), f.lux (sleep hygiene), therapist via BetterHelp |
| **Pain Points** | Tracking is *manual* and *backward-looking*. By the time he sees a mood swing in his spreadsheet, he's already committed to 3 side projects and argued with his manager. No tool intercepts the *behavioral* symptoms in real time. |
| **Job-to-be-Done** | *Detect my state shifts before I do, and gently constrain my environment to prevent destructive patterns.* |
| **Willingness to Pay** | Very high — views this as medical infrastructure. Would pay $20/mo+ if it reduces therapist sessions or prevents a manic episode. |
| **Acquisition Channel** | Therapist recommendation; r/bipolar; academic papers on digital phenotyping; Hacker News |
| **Activation Moment** | Hearth detects elevated activity at 1am, dims screen to candlelight, blocks GitHub commit pushes, and suggests a journal entry — preventing a sleep-deprivation spiral. |

### Persona 3: "Graduate Gia" — The Student in Crisis

| Attribute | Detail |
|-----------|--------|
| **Demographics** | 21, computer science grad student, Michigan, $28K stipend, lives alone |
| **Condition** | Panic disorder + MDD; on sertraline; sees university counseling center monthly; waitlisted for CBT |
| **Desktop Behavior** | 12+ hrs/day on laptop (class + study + entertainment blur); Netflix/YouTube as avoidance; essay deadlines trigger all-nighters and panic attacks; uses phone for Calm app (rarely opens) |
| **Current Stack** | Calm (free tier, barely used), Google Calendar (ignored during episodes), phone screentime limits (circumvented), nothing on desktop |
| **Pain Points** | "When I'm spiraling, my laptop becomes a portal to doom." Cannot self-regulate during panic; loses entire days to dissociative scrolling. Needs external scaffolding, not another app to remember to open. |
| **Job-to-be-Done** | *Be the external executive function I don't have right now — reshape my computer so I can't hurt myself with it.* |
| **Willingness to Pay** | Low direct; high indirect via parents, university disability services, or insurance. Free tier must be genuinely useful; upgrade triggered by academic success (e.g., "I finished my thesis because of this"). |
| **Acquisition Channel** | University disability office partnerships; r/college; TikTok/Instagram mental health creators; student Discord servers |
| **Activation Moment** | During a panic attack, Hearth auto-grayscales the screen, mutes all notifications, opens a grounding exercise overlay, and hides social media apps — without her having to think. |

---

## 5. Go-to-Market Strategy

### Phase 0: Stealth / Pre-Launch (Months -3 to 0)

**Objective:** Build anticipation; validate demand; seed early community.

| Tactic | Detail | Owner | Success Metric |
|--------|--------|-------|----------------|
| **Subreddit AMA Series** | Founder does AMAs in r/ADHD, r/anxiety, r/bipolar, r/productivity. Not promotional — problem-validation focused. "What would your ideal desktop mental health tool do?" | Founder | 500+ comment threads; 3 feature requests that make the roadmap |
| **Landing Page + Waitlist** | Single-page site with product demo video (60s). Waitlist captures condition, OS, and job role. | Marketing | 5,000 waitlist signups; 40% indicate ADHD |
| **Beta Cohort** | 200-person closed beta: 100 from waitlist, 50 from subreddits, 50 from personal networks. Discord server for feedback. | Product | 70% D7 retention; 50+ pieces of qualitative feedback |
| **Press Seeding** | Pitch to TechCrunch, Fast Company, Wired (health desk). Angle: "The first OS that knows your psychology." | PR | 3 published articles |

### Phase 1: Windows Store Launch (Months 1-3)

**Objective:** Prove unit economics on a single channel; establish product-market fit signals.

| Tactic | Detail | Budget | Success Metric |
|--------|--------|--------|----------------|
| **Windows Store Feature Push** | Microsoft's Store editorial team prioritizes wellness/health apps post-pandemic. Pitch for "App of the Day" / "Health & Wellness" feature. | $0 (relationships) | 10,000 organic downloads in M1 |
| **Reddit Organic Campaign** | 3 posts/week across target subreddits. Format: "I built a desktop app that reconfigures your PC based on your mental state. Here's what happened in month 1." No ads; authenticity-first. | $0 | 50K+ upvotes aggregate; 15% of traffic from Reddit |
| **YouTube Micro-Influencers** | 5 creators (50K-200K subs) in ADHD/productivity niche. 60-second integration spots. Pay: $500-$2,000 each or rev-share. | $5,000 | 2,000 attributed installs; CAC < $2.50 |
| **Product Hunt Launch** | Coordinated launch with maker comment engagement. Target: #1 Product of the Day in Health & Wellness. | $0 | 3,000 upvotes; 5,000 site visits |

### Phase 2: Channel Expansion (Months 4-9)

**Objective:** Diversify acquisition; introduce paid channels; build therapist network.

| Tactic | Detail | Budget (Monthly) | Success Metric |
|--------|--------|------------------|----------------|
| **Therapist Partnership Pilot** | 50 therapists in Austin + NYC get free PREMIUM + patient dashboard. They recommend Hearth as "homework between sessions." Track via unique referral codes. | $0 (time) | 200 referred patients; 30% convert to paid |
| **Discord Community** | Official server with channels by condition. Moderated by community managers with lived experience. Weekly office hours with founder. | $2,000 | 5,000 members; 20% DAU/MAU |
| **TikTok / Reels** | 2-3 short-form videos/week showing "before/after" desktop transformation. Hire creator with ADHD lived experience. | $3,000 | 1M views/month; 5% traffic share |
| **Paid Reddit Ads** | Targeted ads in r/ADHD, r/anxiety, r/productivity. Creative: screenshot comparisons ("My desktop at 9am vs. 3pm during a panic attack"). | $4,000 | CAC < $8; CTR > 1.2% |
| **Podcast Sponsorships** | 3 podcasts: *How I Built This* (health angle), *ADHD Experts*, *The Happiness Lab*. | $6,000 | 1,500 attributed installs; CAC < $12 |

### Phase 3: Scale & Platform Expansion (Months 10-18)

**Objective:** macOS launch; enterprise/institutional sales; internationalization.

| Tactic | Detail | Budget | Success Metric |
|--------|--------|--------|----------------|
| **macOS App Store Launch** | Replicate Windows Store playbook. macOS users have higher LTV (premium hardware, higher app spend). | $15,000 | 20% of total MAU by M18 |
| **University Pilot Program** | 10 universities (disability services + counseling centers). Free campus-wide licenses; students upgrade individually post-graduation. | $0 (pilot) | 5,000 student users; 8% annual upgrade rate |
| **Enterprise Wellness Pilot** | Pitch to 3 remote-first tech companies (100+ employees). Position as "neurodiversity accommodation + productivity tool." Seat-based PREMIUM. | Sales time | 1 signed contract; $50K ARR |
| **Internationalization** | German, French, Spanish (EU-5 markets). Localize app + marketing. | $20,000 | 15% of revenue from EU by M18 |

### Timeline Summary

```
M-3 ━━ Waitlist opens, Reddit AMAs, beta recruitment
M0  ━━ Windows Store launch, Product Hunt, YouTube micro-influencers
M3  ━━ Therapist pilot begins, Discord community launch
M6  ━━ Paid Reddit + TikTok scale, first paid channel profitability
M9  ━━ macOS beta, podcast sponsorships, university outreach
M12 ━━ macOS App Store launch, first enterprise deal
M18 ━━ EU localization, 50K MAU, $2M ARR run rate
```

---

## 6. Growth Hacking Tactics

### Viral Loop: "Desktop Before/After"

**Mechanic:** Users share a generated image showing their desktop "before Hearth" (chaos) vs. "after Hearth" (calm, organized, state-aware). One-click share to Reddit, Twitter/X, Instagram Stories.

- **Trigger:** User hits 7-day streak of using Hearth sessions.
- **Reward:** Unlock exclusive "Ambassador" theme pack (PREMIUM aesthetic for free tier).
- **K-factor target:** 0.3 (every 10 users generate 3 new signups via sharing).
- **Why it works:** Desktop screenshots are highly specific and authentic. Unlike generic wellness quotes, they prove tangible transformation.

### Referral Program: "Gift a Calm Workspace"

**Mechanic:** Free tier users earn PRO days by referring friends. PRO users earn PREMIUM days.

| Action | Reward |
|--------|--------|
| Referral signs up (free) | +3 days PRO |
| Referral upgrades to PRO | +30 days PRO |
| Referral upgrades to PREMIUM | +60 days PREMIUM |

- **Double-sided:** Referee gets 14-day PREMIUM trial (vs. standard 7-day).
- **Target:** 25% of new signups come from referrals by M12.
- **CAC implication:** Referral CAC = $0 (marginal server cost only). This is critical for free-to-funnel economics.

### Community Building: "Hearth Advocates"

**Structure:** Tiered community program.

| Tier | Requirement | Perks |
|------|-------------|-------|
| **Member** | Join Discord | Access to channels, support, beta features |
| **Contributor** | 5 forum answers or 2 bug reports | Early access to new builds; founder AMA priority |
| **Ambassador** | 3 successful referrals OR 10K social impressions | Free PREMIUM for life; annual retreat invite; input on roadmap |
| **Clinical Advisor** | Licensed therapist/counselor | Free patient dashboard; CME-style credits; co-authorship on research papers |

**Community KPIs:**
- Discord MAU/Total Members: > 30%
- User-generated content (UGC) pieces/month: > 200
- Support tickets resolved by community (not staff): > 40%

### The "Streak" Gamification Layer

Hearth is not a game, but **continuity matters for habit formation.**

- **Daily Check-In Streak:** Visual "calm streak" counter. Not competitive (no leaderboards — mental health is not a sport).
- **Milestone Rewards:** 7-day streak = new wallpaper pack. 30-day = PRO feature preview. 90-day = founder handwritten thank-you note (real mail; high surprise-and-delight).
- **Loss Aversion Design:** If streak breaks, message reads "Your wellbeing isn't a streak — it's a practice. Start again when you're ready." (Anti-toxicity positioning).

### SEO / Content Hack: "Condition + Desktop" Long Tail

Target zero-competition keywords where Hearth is the only relevant result.

| Keyword | Monthly Volume | Content Type |
|---------|---------------|--------------|
| "desktop app for ADHD" | 90 | Landing page |
| "computer anxiety relief tool" | 40 | Blog post + tool |
| "bipolar productivity software" | 30 | Case study (Sam persona) |
| "automatically organize files ADHD" | 50 | Feature page |
| "desktop environment for depression" | 20 | Blog post |

**Strategy:** Create 50 condition-specific landing pages by M6. Aggregate search volume: ~5,000/month. At 10% CTR and 15% conversion = 75 signups/month, effectively free.

---

## 7. User Acquisition Strategy

### Channel Mix (Year 1)

| Channel | % of Budget | Monthly Spend | Expected CAC | Expected Volume (Month 6) | Primary Persona |
|---------|-------------|---------------|--------------|---------------------------|-----------------|
| **Organic / Reddit** | 0% | $0 | $0 | 800 signups | Olivia, Gia |
| **Referral / Viral** | 0% | $0 | $0.50 | 400 signups | All |
| **YouTube / Influencer** | 20% | $2,000 | $4.00 | 500 signups | Olivia |
| **Paid Social (Reddit/TikTok)** | 35% | $3,500 | $7.50 | 470 signups | Gia, Olivia |
| **Podcast / Audio** | 25% | $2,500 | $12.00 | 210 signups | Sam |
| **Therapist Referral** | 0% | $0 | $2.00* | 150 signups | Sam |
| **Windows Store Organic** | 20% | $2,000** | $1.00 | 2,000 signups | All |

\* Therapist CAC = cost of free dashboard + time; marginal acquisition cost is near-zero.  
\*\* Store optimization (ASO), featured placement lobbying, creative assets.

**Blended CAC Target (Y1): $3.50**  
**Blended CAC Target (Y2): $5.00** (as organic share decreases and paid scales)

### LTV Projections

| Tier | Monthly Price | Annual Price | Annual Churn | Gross LTV | LTV:CAC |
|------|--------------|--------------|--------------|-----------|---------|
| **Free → PRO** | $8 | $80 | 35% | $154 | 44:1 (organic) |
| **Free → PREMIUM** | $15 | $150 | 25% | $450 | 90:1 (organic) |
| **Paid (blended)** | — | $110 | 30% | $261 | 52:1 (blended) |

**LTV formula:** ARPU × Gross Margin / Monthly Churn  
- PRO: $6.67/mo × 0.85 / 0.029 = $195 → rounded to $154 (conservative, early-stage churn higher)
- PREMIUM: $12.50/mo × 0.85 / 0.021 = $506 → rounded to $450

**Payback period target:** < 6 months on paid channels. At $5 CAC and $110 ARPU with 30% annual churn, payback = ~2.7 months.

### Cohort-Based LTV Sensitivity

| Cohort | Churn at M3 | Churn at M12 | LTV | Driver |
|--------|-------------|--------------|-----|--------|
| Reddit organic | 45% | 60% | $88 | Low intent; curious signups |
| Therapist referral | 15% | 25% | $520 | High trust; clinical context |
| YouTube influencer | 30% | 50% | $165 | Medium intent; parasocial trust |
| Product Hunt | 55% | 75% | $55 | Tourists; low fit |

**Strategic implication:** Prioritize therapist channel expansion even if volume is lower. LTV is 6× Reddit cohort.

---

## 8. Retention Strategy

### Onboarding: The "First Session" Protocol

**Goal:** Time-to-value < 3 minutes. User must feel a *tangible* desktop change before any data entry.

| Step | Action | Psychology |
|------|--------|------------|
| **0:00-0:30** | One-click install from Windows Store. No account required. | Remove friction; curiosity-driven |
| **0:30-1:00** | Hearth auto-detects desktop state (tab count, open apps, notification load). Displays: "We detected 47 tabs and 12 notifications. Want to see what calm looks like?" | Pattern interrupt; shock of recognition |
| **1:00-2:00** | One-tap "Calm My Desktop" button. Hearth executes: closes excess tabs, mutes notifications, changes wallpaper, opens focus workspace. | Immediate, visible value |
| **2:00-3:00** | Micro-survey: "How are you feeling right now?" (3 emojis). First data point; begins personalization. | Investment loop |
| **Day 1-3** | Daily push (gentle, native Windows notification): "Your desktop is getting chaotic. 2 clicks to reset." | Habit cue |
| **Day 7** | Achievement: "7 days of calmer computing." Offer 14-day PREMIUM trial. | Conversion trigger |

**Onboarding KPIs:**
- Day 1 retention: > 60%
- Day 7 retention: > 35%
- Day 30 retention: > 20%
- Free-to-trial start: > 15%
- Trial-to-paid: > 25%

### Activation: Defining "Aha" Moments by Persona

| Persona | Primary Aha Moment | Secondary Aha Moment | Tertiary Aha Moment |
|---------|--------------------|----------------------|---------------------|
| **Olivia** | Auto-closes 30+ tabs in one click | Morning "focus mode" auto-launches work apps only | Weekly report: "You focused 4.2 hrs this week" |
| **Sam** | Mood spike detected → environment auto-adjusts at 1am | Exportable report for therapist session | Medication reminder tied to desktop state |
| **Gia** | Panic mode overlay during high heart rate / fast typing | Assignment deadline auto-prioritization | Parental dashboard shows "Gia is doing okay this week" |

**Activation metric:** User completes primary Aha moment within 48 hours of install. Target: 40% of new users.

### Habit Formation: The "Environmental Cue" Model

Hearth's retention superpower is that it does not rely on the user *remembering* to open the app. It is ambient.

**Habit Loop Design:**
- **Cue:** Desktop chaos (high tab count, rapid window switching, late hour) → Hearth surfaces a gentle intervention.
- **Routine:** User clicks "Yes, help me" → environment transforms.
- **Reward:** Immediate sensation of calm (sympathetic nervous system downregulation via reduced visual clutter).

**Reinforcement schedule:**
- **Week 1-2:** Variable ratio (interventions feel surprising and magical).
- **Week 3-4:** Fixed interval (daily morning check-in becomes expected).
- **Month 2+:** User initiates (habit internalized; user opens Hearth proactively).

### Churn Prevention Triggers

| Signal | Intervention | Channel |
|--------|-------------|---------|
| No session for 3 days | Email: "Your desktop misses you. One click to restore calm." + deep-link to auto-fix | Email |
| No session for 7 days | Push: "We saved your last calm workspace. Ready to return?" | Windows native notification |
| No session for 14 days | Personal email from founder: "What got in the way?" (qualitative research + re-engagement) | Email |
| Trial ending, low usage | In-app: "You haven't activated your superpowers yet. Extend trial 7 days?" | In-app modal |
| Payment failed | Grace period: 7 days full access + empathetic messaging (mental health = no shame around money) | In-app + email |

### Retention Metrics by Cohort

| Metric | M1 Target | M3 Target | M6 Target | M12 Target |
|--------|-----------|-----------|-----------|------------|
| Day 1 Retention | 55% | 60% | 65% | 70% |
| Day 7 Retention | 28% | 35% | 40% | 45% |
| Day 30 Retention | 15% | 20% | 25% | 30% |
| Monthly Churn (paid) | — | 8% | 5% | 3.5% |
| NPS | — | +25 | +35 | +45 |

---

## 9. Key Metrics & North Star

### North Star Metric

**"Calm Hours Created" (CHC)**

**Definition:** The cumulative number of focused, low-distraction, psychologically aligned hours that Hearth enables across all users, measured by:
- Time in "focus mode" workspaces (no context switches > 5 minutes)
- Reduction in notification interruptions vs. baseline
- User self-reported "calm" state during check-ins

**Why this metric:**
- Correlates with retention (users who log CHC stay subscribed).
- Aligns with mission (mental health outcomes, not engagement for engagement's sake).
- Defensible against "time spent in app" vanity metrics. We do not want addiction; we want efficacy.

**North Star target:** 1M CHC by end of Y1; 25M CHC by end of Y3.

### Input Metrics (Leading Indicators)

| Metric | Definition | Y1 Target | Owner |
|--------|-----------|-----------|-------|
| **Weekly Active Workspaces (WAW)** | Unique users who activated at least one Hearth workspace/session in a week | 25,000 | Product |
| **Intervention Acceptance Rate** | % of suggested interventions that user accepts | 65% | ML/AI |
| **Time to First Value (TTFV)** | Minutes from install to first completed intervention | < 3 min | Onboarding |
| **Psychological Profile Completion** | % of users who complete baseline assessment | 45% | UX Research |
| **Free-to-Trial Rate** | % of free users who start 14-day PREMIUM trial | 15% | Growth |
| **Trial-to-Paid Rate** | % of trial users who convert to paid | 25% | Growth |

### Output Metrics (Lagging Indicators)

| Metric | Definition | Y1 Target | Y3 Target |
|--------|-----------|-----------|-----------|
| **Monthly Active Users (MAU)** | Unique users with ≥1 session | 50,000 | 300,000 |
| **Paying User %** | Paid users / Total registered | 8% | 12% |
| **Monthly Recurring Revenue (MRR)** | — | $28K | $350K |
| **Annual Recurring Revenue (ARR)** | — | $332K | $4.2M |
| **Net Revenue Retention (NRR)** | (Starting MRR + Expansions - Contractions - Churn) / Starting MRR | — | 110% |
| **Blended CAC** | Total sales + marketing spend / New paid users | $3.50 | $5.00 |
| **LTV:CAC Ratio** | LTV / CAC | > 30:1 | > 40:1 |
| **Gross Margin** | (Revenue - COGS) / Revenue | 85% | 88% |
| **Burn Multiple** | Net burn / Net new ARR | < 2.0x | < 1.5x |

### Unit Economics Dashboard (Y1)

```
Monthly New Signups:        5,000
Free-to-Trial Rate:         15%        → 750 trials
Trial-to-Paid Rate:         25%        → 187 new paid users/mo
Blended ARPU:               $9.17/mo   → $110/yr
Monthly Churn:              5%         → 95% retention/mo
Gross LTV:                  $261
Blended CAC:                $3.50
LTV:CAC:                    74.6:1
Months to Payback:          0.4 months (exceptional, driven by organic/referral)
```

### Health Metrics (Guardrails)

| Metric | Red Flag | Yellow | Green |
|--------|----------|--------|-------|
| Day 1 Retention | < 40% | 40-55% | > 55% |
| Day 7 Retention | < 20% | 20-30% | > 30% |
| Trial-to-Paid | < 15% | 15-22% | > 22% |
| Monthly Churn | > 10% | 5-10% | < 5% |
| NPS | < 0 | 0-30 | > 30 |
| Support Tickets / 1K Users | > 50 | 25-50 | < 25 |
| App Store Rating | < 3.5 | 3.5-4.2 | > 4.2 |

---

## Appendix: Key Assumptions & Risks

### Critical Assumptions
1. Desktop screen time remains structurally high (> 6 hrs/day for knowledge workers) through 2030.
2. Users will grant OS-level permissions to a mental health app (trust hurdle).
3. Windows Store distribution can achieve meaningful organic discovery without paid UA.
4. Therapist referral channel scales linearly with relationship investment.

### Mitigated Risks
| Risk | Mitigation |
|------|------------|
| **Privacy backlash** | HIPAA-ready architecture; local-first data processing; transparent privacy policy; no data sale |
| **FDA / medical device classification** | Pre-submission meeting scheduled for Y2; maintain "wellness" (not "treatment") positioning until designation secured |
| **Platform risk (Microsoft changes Store rules)** | Maintain direct-download channel; never 100% dependent on single distributor |
| **Burnout of founder-led community** | Hire community manager by M4; automate support with condition-specific chatbot by M8 |
| **Competitor copy (Apple/Windows build native)** | Speed-to-market + data flywheel; 12-month lead time is defensible if we move fast |

---

*This document is a living strategy. Review monthly in founder standups, quarterly in board meetings.*
