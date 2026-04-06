# Mindful Organizer - Project Tracker

> No timeframes. Ordered by priority and logical sequence.

---

## Phase 1: Get It Up and Running (MVP for Windows Store)

### Critical Path - Must Have for Launch

- [ ] **Windows packaging with MSIX/AppX** - Package PyQt6 app for Windows Store submission using `pyinstaller` or `cx_Freeze` + MSIX tooling
- [ ] **Windows Store manifest** - Create AppxManifest.xml with identity, capabilities, visual assets
- [ ] **App icons and store assets** - Design all required tile sizes (44x44, 150x150, 310x310, splash screen, store listing screenshots)
- [ ] **Code signing certificate** - Obtain or self-sign for Store submission
- [ ] **First-run onboarding flow** - Guided mental health profile setup wizard for new users
- [ ] **Installer/uninstaller for Windows** - Clean install/remove experience (currently only macOS/Linux scripts)
- [ ] **Fix all critical bugs** - Full pass on task creation, profile switching, mood tracking flows
- [ ] **Data directory setup on Windows** - Ensure `~/.mindful_optimizer/` works correctly on Windows paths (`%APPDATA%`)
- [ ] **PyQt6 Windows compatibility pass** - Test all UI elements render correctly on Windows 10/11
- [ ] **Error handling and crash recovery** - Graceful error dialogs instead of console tracebacks
- [ ] **App startup performance** - Cold start under 3 seconds; lazy-load heavy ML models
- [ ] **Windows Store privacy policy page** - Required for submission; detail local-only data storage
- [ ] **Store listing copy** - Description, feature list, screenshots, categories
- [ ] **Age rating questionnaire** - Complete Microsoft's content rating for mental health content
- [ ] **Accessibility compliance** - Keyboard navigation, screen reader support, Windows high contrast mode integration

### Core Functionality Polish

- [ ] **Task manager stability** - Ensure CRUD operations are bulletproof with proper validation
- [ ] **Profile persistence** - Profile switching fully functional, settings survive restarts
- [ ] **Mood tracker data integrity** - Entries saved reliably, no data loss on unexpected close
- [ ] **Theme consistency** - All 4 themes (Light, Dark, Calm, High Contrast) render correctly across every tab
- [ ] **File organizer dry-run mode** - Preview changes before moving files (safety net for users)
- [ ] **Settings export/import** - Users can back up and restore their configuration
- [ ] **Meditation player** - Functional audio playback for guided meditation library (UCLA MARC, Oxford, NHS, Free Mindfulness)

---

## Phase 2: Make It Better (Post-Launch Improvements)

### User Experience

- [ ] **Dashboard overhaul** - At-a-glance view of mood trends, energy levels, task completion, streaks
- [ ] **Onboarding tutorial** - Interactive walkthrough of each feature
- [ ] **Notification system** - Gentle reminders for mood check-ins, task deadlines, meditation breaks
- [ ] **Undo/redo for all actions** - Especially file organization and task edits
- [ ] **Search across everything** - Global search for tasks, files, mood entries, skills
- [ ] **Keyboard shortcuts** - Power user shortcuts for common actions
- [ ] **Drag-and-drop task reordering** - Manual priority adjustment
- [ ] **Custom task categories** - Let users define their own beyond the 7 defaults
- [ ] **Recurring tasks** - Daily, weekly, monthly task templates
- [ ] **Task notes and attachments** - Rich context per task

### Mental Health Features

- [ ] **Mood analytics dashboard** - Charts showing mood/energy trends over weeks and months
- [ ] **Trigger identification** - Pattern recognition linking mood dips to activities or times
- [ ] **Crisis plan quick-access** - One-tap access to personal crisis plan and emergency contacts
- [ ] **Breathing exercise timer** - Visual guided breathing (box breathing, 4-7-8, etc.)
- [ ] **Grounding exercise walk-throughs** - Interactive 5-4-3-2-1 and other grounding techniques
- [ ] **ERP module completion** - Full Exposure & Response Prevention tracking for OCD (currently stubbed)
- [ ] **Journaling with prompts** - Condition-specific prompts (gratitude, CBT thought records, etc.)
- [ ] **Sleep tracking integration** - Manual sleep log with correlation to mood/energy
- [ ] **Medication reminder system** - Simple medication tracking (not medical advice)

### Technical Improvements

- [ ] **Comprehensive test suite** - Unit tests for all managers, integration tests for workflows
- [ ] **Automated Windows builds** - GitHub Actions pipeline producing MSIX packages
- [ ] **Auto-update mechanism** - Check for and install updates from within the app
- [ ] **Database migration system** - Handle schema changes between versions gracefully
- [ ] **Logging framework** - Structured logging for debugging (never log sensitive health data)
- [ ] **Performance profiling** - Identify and fix memory leaks, slow renders
- [ ] **Localization framework** - i18n infrastructure for future translations

---

## Phase 3: Make It Best on Market (Competitive Edge)

### AI and Intelligence

- [ ] **Adaptive task scheduling** - ML model learns user's peak productivity hours per condition
- [ ] **Energy prediction engine** - Predict energy levels based on historical patterns, sleep, weather
- [ ] **Smart task decomposition** - AI breaks overwhelming tasks into micro-steps (critical for ADHD/depression)
- [ ] **Natural language task entry** - Type "call dentist tomorrow high priority" and it parses automatically
- [ ] **Personalized coping suggestions** - AI recommends specific DBT/CBT/ACT skills based on current mood state
- [ ] **Anomaly alerts** - Detect concerning mood patterns and gently suggest professional support
- [ ] **Context-aware organization** - File organizer learns from user corrections and improves over time
- [ ] **Conversational AI companion** - Supportive chat interface using therapeutic frameworks (not a replacement for therapy)

### Platform Expansion

- [ ] **Cloud sync (optional, encrypted)** - End-to-end encrypted sync across devices; zero-knowledge architecture
- [ ] **Mobile companion app (Windows Phone / cross-platform)** - Quick mood check-ins and task management on the go
- [ ] **Web dashboard** - Read-only analytics view accessible from any browser
- [ ] **Calendar integration** - Sync with Outlook, Google Calendar for task deadlines
- [ ] **Wearable integration** - Pull heart rate, sleep data from Fitbit, Apple Watch, Garmin
- [ ] **Voice commands** - Hands-free task creation and mood logging
- [ ] **Widgets** - Windows desktop widgets for quick mood entry and task view

### Professional and Clinical

- [ ] **Therapist portal** - Optional sharing of mood/task data with a therapist (user-controlled)
- [ ] **Clinical report generation** - Export mood/symptom data in formats useful for therapy sessions
- [ ] **Multi-profile support** - Family accounts with individual private profiles
- [ ] **Insurance/EAP integration** - Connect with employee assistance programs
- [ ] **HIPAA-aligned data handling** - For users who want to share data with healthcare providers

### Community

- [ ] **Anonymous peer support** - Moderated community forums within the app
- [ ] **Shared coping strategy library** - Users contribute and rate coping techniques
- [ ] **Challenge system** - Community wellness challenges (meditation streaks, gratitude chains)
- [ ] **Template marketplace** - Share and download task templates, organization strategies

---

## Phase 4: Unique Features - What We Have and What to Add

### Existing Unique Features (Already Built)

- **Mental health profile system** - No other task manager adapts to clinical conditions (ADHD, Anxiety, Depression, OCD, PTSD, Bipolar)
- **Evidence-based clinical combinations** - Research-backed settings for comorbid conditions with conflict resolution
- **Energy-based task prioritization** - Tasks matched to current energy level, not just urgency
- **Condition-adaptive UI** - Interface literally changes based on your mental health profile (animation speed, color palette, layout density, notification style)
- **ADHD gamification engine** - Points, streaks, achievements, daily challenges, dopamine-optimized feedback
- **Integrated therapy skill references** - Built-in DBT, CBT, ACT, and Mindfulness skill libraries
- **Mental health-aware file organization** - Organization strategies designed for specific conditions (minimal for ADHD, visual for depression, detailed for anxiety)
- **Encrypted sensitive content management** - Fernet encryption, passcode-protected folders, secure deletion
- **Curated clinical meditation library** - Sourced from UCLA MARC, Oxford Mindfulness Centre, NHS, Free Mindfulness Project
- **Local-first privacy** - All data stored locally by design; no cloud dependency
- **AI-powered system optimization** - ML-based resource monitoring and optimization suggestions
- **Smart file clustering** - Semantic file grouping using embeddings and HDBSCAN

### Unique Features to Add

- [ ] **Spoon Theory energy budgeting** - Visual "spoon" allocation for daily energy management (popular in chronic illness communities)
- [ ] **Body doubling virtual rooms** - Timer-based co-working sessions for ADHD focus
- [ ] **Sensory profile settings** - Customize app sounds, colors, animation based on sensory sensitivities
- [ ] **Rejection sensitivity tracker** - ADHD-specific mood tracking for RSD episodes
- [ ] **Doom scrolling intervention** - Optional integration that gently nudges users back to tasks
- [ ] **Emotional granularity training** - Help users develop more specific emotional vocabulary over time
- [ ] **Values-aligned task tagging** - ACT-based feature connecting tasks to personal values
- [ ] **Worry time scheduler** - CBT technique: schedule designated worry periods to reduce anxiety throughout the day
- [ ] **Cognitive load meter** - Real-time assessment of how many open loops the user has
- [ ] **Transition support** - Guided transitions between tasks (critical for ADHD task-switching difficulty)
- [ ] **Burnout early warning system** - Track overwork patterns and flag before burnout hits
- [ ] **Hypomania detection** - For bipolar users: flag unusually high productivity/energy patterns
- [ ] **Accessibility-first design system** - Dyslexia-friendly fonts, colorblind modes, reduced motion
- [ ] **Offline-first architecture** - Works fully without internet; sync when available
- [ ] **Data portability** - Export all data in open formats (JSON, CSV, PDF reports)

---

## Phase 5: Windows Store Launch Checklist

### Pre-Submission

- [ ] Register Microsoft Partner Center developer account
- [ ] Reserve app name "Mindful Organizer" in the Store
- [ ] Complete app identity in AppxManifest.xml
- [ ] Build MSIX package with all required assets
- [ ] Test on Windows 10 (1809+) and Windows 11
- [ ] Test on ARM64 Windows devices (Surface Pro X, etc.)
- [ ] Complete Windows App Certification Kit (WACK) testing
- [ ] Write Store listing (description, features, screenshots, keywords)
- [ ] Prepare privacy policy URL
- [ ] Set pricing (Free with optional premium features, or fully free)
- [ ] Select Store categories: Health & Fitness, Productivity
- [ ] Complete age rating questionnaire
- [ ] Prepare support contact information and URL

### Submission

- [ ] Upload MSIX package to Partner Center
- [ ] Submit for certification review
- [ ] Address any certification feedback
- [ ] Plan launch announcement

### Post-Launch

- [ ] Monitor crash reports via Partner Center analytics
- [ ] Respond to user reviews
- [ ] Track download and retention metrics
- [ ] Plan first update based on user feedback
- [ ] Set up feedback collection within the app

---

## Technical Debt and Maintenance

- [ ] Refactor `main_window.py` - Currently a monolith; split into separate widget classes
- [ ] Increase test coverage to 80%+
- [ ] Add type hints to all public APIs
- [ ] Document all configuration options
- [ ] Audit dependencies for security vulnerabilities
- [ ] Remove unused imports and dead code
- [ ] Standardize error handling patterns
- [ ] Profile and optimize memory usage (ML models are heavy)
- [ ] Set up automated dependency updates (Dependabot)
- [ ] Create development environment setup documentation

---

## Architecture Decisions to Make

- [ ] **Packaging tool**: PyInstaller vs cx_Freeze vs Nuitka for Windows executable
- [ ] **Update mechanism**: Custom updater vs Windows Store auto-update vs Squirrel
- [ ] **Database**: Stay with SQLite + JSON or migrate to a single SQLite database for everything
- [ ] **Cloud sync protocol**: If adding sync, choose architecture (CRDTs, last-write-wins, manual merge)
- [ ] **Plugin system**: Allow third-party extensions for therapy techniques and organization strategies
- [ ] **Monetization model**: Free / Freemium / One-time purchase / Subscription

---

*This tracker is a living document. Items can be reordered, added, or removed as the project evolves.*
