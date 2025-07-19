# Mindful Organizer

A mental health-focused task and energy management application.

## Setup

1. Create a virtual environment:
```bash
python3 -m venv venv
```

2. Activate the virtual environment:
```bash
source venv/bin/activate  # On macOS/Linux
```

3. Install package in development mode:
```bash
pip install -e .
```

## Running the Application

```bash
mindful-organizer
```

## Features

- Task Management with energy-based prioritization
- Energy and Mood Tracking
- Adaptive Interface based on mental health profile
- Break suggestions based on energy levels
- Multiple themes (Light, Dark, Calm)

## Testing

Run tests with coverage:
```bash
pytest --cov=src
```

## Project Structure

```
mindful_organizer/
├── src/
│   ├── core/           # Core functionality
│   ├── gui/            # User interface
│   ├── profile/        # Mental health profiles
│   ├── security/       # Security features
│   └── file_organization/  # File management
├── tests/
│   ├── unit/          # Unit tests
│   └── integration/   # Integration tests
├── resources/          # Application resources
└── docs/              # Documentation
```
