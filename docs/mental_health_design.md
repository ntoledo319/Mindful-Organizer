# Mental Health Feature Design

## Philosophy
Mindful Organizer is designed to be **supportive, non-judgmental, and evidence-informed**. It does not diagnose. It adapts to the user's self-reported challenges.

## Feature Breakdown

### 1. The Profile Engine
**User Goal**: "I want an app that understands my brain."
**Design**:
- **Intake**: Asks "What is your biggest challenge right now?" (Focus, Anxiety, Mood, Organization).
- **Adaptation**:
    - **ADHD**: Simpler menus, larger buttons, gamification enabled (Streaks, Badges), frequent reminders.
    - **Anxiety**: Soothing colors (Teal/Lavender), "Zen Mode" (hides non-essential UI), emphasis on privacy and safety (Undo).
    - **Depression**: "Warm" tone, celebratory messages for small wins ("You opened the app!"), emphasis on behavioral activation (doing small tasks).

### 2. The "Mindful" File Organizer
**User Goal**: "My computer is a mess and it stresses me out."
**Design**:
- **Scan -> Breathe -> Plan -> Act**: The process is slowed down intentionally.
- **Decision Fatigue Reduction**: The app suggests *one* plan, rather than asking 50 questions.
- **Safety Net**: The "Undo" button is prominent. Fear of making mistakes is a huge blocker for anxiety/OCD users.

### 3. Mood & Symptom Tracker
**User Goal**: "I need to track my patterns for my therapist/myself."
**Design**:
- **Quick Log**: 1 click to log mood (Emoji/Number).
- **Context**: "What were you doing?" (Work, Social, Sleep).
- **Correlation**: Over time, shows "You tend to feel Anxious when your Desktop has >50 items" (Hypothetical V2 feature).

### 4. Crisis / Skill Tools
**User Goal**: "I'm overwhelmed right now."
**Design**:
- **TIPP Skills**: A guided walkthrough of TIPP (Temperature, Intense Exercise, Paced Breathing, Paired Muscle Relaxation).
- **5-4-3-2-1 Grounding**: Text-based guide to ground the user in their senses.
- **Thought Record**: A structured form to challenge negative thoughts (Situation -> Thought -> Emotion -> Evidence For/Against -> Balanced Thought).

## Safety & Ethics
- **Disclaimer**: Every mental health screen has a small footer: "Not a medical device. Call 911/988 in emergency."
- **Data Privacy**: All journal/mood data is encrypted locally. No cloud upload.
- **Language**: We use "Challenges" instead of "Deficits". We use "Neurodivergence" inclusive language.
