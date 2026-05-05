# Mindful Organizer — Complete Feature List

> Last updated: 2026-05-02

---

## Tier Legend
- 🆓 **Free** — Unlimited, forever. Core mental health & productivity tools.
- ⭐ **Pro** — $4.99/mo or $39.99/yr. Insights, trends, sync, and personalization.
- ⭐⭐ **Premium** — $9.99/mo or $79.99/yr. Advanced reports and sharing.

---

## 🧠 Core Tracking (Free)

| Feature | Description |
|---------|-------------|
| 🆓 Mood Logging | Log mood scores (1-10) with condition-specific symptoms, therapy skills, and notes. Persists to SQLite via `MoodManager`. |
| 🆓 DBT Diary Card | Daily structured tracking: emotions, urges (0-5), skills used, effectiveness (1-5), target behaviors, medication adherence, substances. Condition-aware content. |
| 🆓 Sleep Logging | 3-tap entry: bedtime, wake time, quality (Poor/Okay/Good). Auto-calculates duration. |
| 🆓 Medication Logging | Track medications, dosages, schedules, and whether taken. Unlimited entries. |
| 🆓 Task Management | Create, edit, complete, and delete tasks with due dates and priorities. Unlimited tasks. |
| 🆓 Journal Entries | Rich-text journaling with condition-aware prompts (General, Anxiety, Depression, ADHD, OCD, PTSD). Unlimited entries. |
| 🆓 Panic Attack Logging | Log panic attacks with peak distress, triggers, symptoms, coping strategies, and aftermath. |
| 🆓 ERP Exposure Tracking | Track exposure exercises for OCD with hierarchy levels, anxiety ratings, and duration. |

---

## 🧘 Therapeutic Tools (Free)

| Feature | Description |
|---------|-------------|
| 🆓 Breathing Exercises | Box breathing, 4-7-8, and other guided techniques with animated visual circle. Reduced-motion support. |
| 🆓 Grounding Exercises | 5-4-3-2-1 senses grounding and other trauma-informed techniques. |
| 🆓 Crisis Plan | Create and edit a personalized crisis plan with contacts, warning signs, and coping strategies. |
| 🆓 Guided Meditations | Built-in guided meditation library with play/pause/stop and timer. |
| 🆓 Medication Reminders | Up to 3 scheduled reminders for free users. |

---

## 📊 Dashboard & Overview

| Feature | Tier | Description |
|---------|------|-------------|
| 🆓 Basic Dashboard | Free | Today's mood, tasks, and welcome message. |
| ⭐ Full Dashboard | Pro | Adds daily briefing, crisis signal banner, values card, energy forecast, gamification card. |
| ⭐ Daily Briefing | Pro | Energy forecast + prioritized task suggestions + coping skill recommendation. |
| ⭐ Crisis Signal Banner | Pro | Automatic wellness check-ins based on mood/sleep patterns. |
| ⭐ Trial Banner | Free | One-click 14-day trial start banner for free users. |
| ⭐ Trial Countdown | Free | Shows days remaining during active trial. |

---

## 📈 Analytics & Insights

| Feature | Tier | Description |
|---------|------|-------------|
| 🆓 7-Day History | Free | View last 7 days of mood and sleep data. |
| ⭐ Unlimited History | Pro | View 30/90/365-day trends and historical data. |
| ⭐ Mood Analytics | Pro | Trend detection (improving/declining/stable) with moving averages. |
| ⭐ Energy Predictor | Pro | Predict current and rest-of-day energy based on sleep, mood, and task history. Fully automatic — no manual logging. |
| ⭐ Journal Sentiment Analysis | Pro | Lexicon-based polarity scoring (-1 to +1) for journal entries. |
| ⭐ Cognitive Distortion Detection | Pro | Detects all-or-nothing thinking, catastrophizing, mind-reading, should-statements, labeling, emotional reasoning. |
| ⭐ Journal Analysis Trends | Pro | Alerts when distortion density exceeds 2× baseline over 14 days. |
| ⭐ Values Tracker | Pro | ACT values-based weekly review — tracks time/energy per value and generates neglect alerts. |
| ⭐ Weekly Insights Report | Pro | Auto-generated HTML summary (mood, sleep, tasks, values, personalized suggestions). |

---

## 🔔 Notifications & Reminders

| Feature | Tier | Description |
|---------|------|-------------|
| 🆓 Basic Medication Reminders | Free | Up to 3 scheduled medication reminders. |
| ⭐ Smart Notifications | Pro | Context-aware nudges: energy peak alerts, sleep debt warnings, behavioral activation nudges, afternoon slump alerts (ADHD), missed medication reminders. |
| ⭐ Unlimited Medication Reminders | Pro | Unlimited scheduled medication reminders. |

---

## 🎨 Personalization

| Feature | Tier | Description |
|---------|------|-------------|
| 🆓 2 Themes | Free | Default light + one alternate theme. |
| ⭐ All 8 Condition-Aware Themes | Pro | Focus (ADHD), Gentle (PTSD), Calm (Anxiety), Structured (OCD), Energetic (Bipolar), Soft (Depression), Balanced (General), High-Contrast (Accessibility). Each has unique layout density, animation speed, border radius, and chrome visibility. |
| ⭐ Gamification & Achievements | Pro | XP, levels, streaks, and unlockable rewards for task completion and tracking consistency. |

---

## 📤 Export, Sync & Sharing

| Feature | Tier | Description |
|---------|------|-------------|
| ⭐ Data Export (JSON/CSV) | Pro | Full backup and export of all user data. |
| ⭐ Calendar Sync (ICS) | Pro | Export tasks with energy levels to calendar apps. |
| ⭐⭐ Shareable Web Reports | Premium | Self-contained HTML with Chart.js: mood timelines, diary card summaries, sleep charts, journal highlights. Browser-openable, cloud-shareable, Notion-pastable. |
| ⭐⭐ Medication Adherence Heatmap | Premium | Visual calendar heatmap of medication consistency. |
| ⭐⭐ Values Alignment Radar | Premium | Polar chart showing time/energy distribution across personal values. |
| ⭐⭐ Support Network Sharing | Premium | Share reports directly with trusted support networks. |

---

## 🔒 Security & Privacy

| Feature | Tier | Description |
|---------|------|-------------|
| 🆓 Local-First Storage | Free | All data stored in SQLite on-device. No cloud required. |
| 🆓 Encrypted Vault | Free | Secure folder encryption using Fernet + scrypt passcode hashing. |
| 🆓 HIPAA-Inspired Safeguards | Free | No telemetry, no third-party analytics, no data collection. |
| ⭐⭐ Onboarding Analytics | Premium | Privacy-respecting funnel metrics (step names + timestamps only, no health data). |

---

## 🔧 System & Utilities

| Feature | Tier | Description |
|---------|------|-------------|
| 🆓 File Organizer | Free | Condition-aware organization: ADHD (emoji/action folders), OCD (numbered structure), Depression (energy-tiered), Anxiety (detailed hierarchy). Dry-run, undo, duplicates, batch rename. |
| ⭐ Auto-Updater | Pro | Checks GitHub releases every 24 hours; one-click update. |
| ⭐ Accessibility Suite | Free | Auto-detects screen readers, font scaling, color-blind modes, reduced motion, dyslexia-friendly font, keyboard navigation. |
| ⭐ StateBus | Free | Reactive pub/sub system — widgets auto-refresh when mood/tasks change. |
| ⭐ Theme Engine | Free | Runtime theme switching with QSS generation. |
| ⭐ Database Manager | Free | Thread-safe SQLite with WAL mode, migrations, and extended wellness schema. |
| ⭐ Migration Manager | Free | JSON→SQLite migration wizard with progress dialog. |

---

## 💳 Subscription & Licensing

| Feature | Description |
|---------|-------------|
| 🆓 Free Tier | All core tracking + therapeutic tools + 7-day history + 2 themes. No time limits. |
| ⭐ Pro Tier | $4.99/mo or $39.99/yr. Insights, trends, sync, smart notifications, all themes, gamification, export. |
| ⭐⭐ Premium Tier | $9.99/mo or $79.99/yr. Everything in Pro + shareable reports, heatmaps, radar charts, sharing. |
| 🎁 14-Day Trial | Full Premium access for 14 days. No credit card required. Single-use per device. |
| 🔑 Offline License Keys | HMAC-validated keys. Works without internet. Cryptographically secure. |
| ⚙️ Settings Integration | View tier, start trial, enter license key, or deactivate — all inside the app. |

---

## 🗺️ Tab Structure

| Tab | Tier | Description |
|-----|------|-------------|
| Dashboard | Free/Pro | Overview with widgets gated by tier. |
| Tasks | Free | Full task manager. |
| Mood | Free | Mood tracker with analytics gated. |
| Diary Card | Free | DBT-style daily structured tracking. |
| Journal | Free | Journaling with sentiment analysis gated. |
| Breathing | Free | Breathing exercises. |
| Meditation | Free | Guided meditations. |
| ERP | OCD | ERP exposure tracker (condition-gated). |
| Panic Log | Panic/Anxiety/PTSD | Panic attack logging (condition-gated). |
| Crisis Plan | Free | Crisis plan editor. |
| Sleep | Free | 3-tap sleep tracker. |
| Medication | Free | Medication tracker with reminders gated. |
| Files | Free | Condition-aware file organizer. |
| Settings | Free | Profile, theme, accessibility, subscription, data management. |

---

## 🏗️ Architecture Highlights

- **67 source files, ~27K lines, 565+ tests**
- **Python 3.11+ with PyQt6**
- **SQLite primary persistence (WAL mode) with schema v2**
- **Cross-platform: macOS, Linux, Windows**
- **Component library**: CardFrame, AccentButton, SectionTitle, ScrollContainer, ThemedProgressBar
- **Unified enums**: Single canonical `Condition` enum across all modules
- **Safety-conscious design**: 14-day minimum data thresholds, observation language (never implies diagnosis)
