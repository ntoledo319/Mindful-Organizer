# Mindful Organizer

A mental health-focused task and energy management application.

## Smart File System Module

The Smart File System module provides intelligent document organization using machine learning to:
- Automatically index and categorize files
- Cluster similar documents together
- Generate reports on document relationships
- Find similar files based on semantic content

### CLI Usage

```bash
# Index files in a directory
mindful-organizer index /path/to/documents

# Cluster indexed files
mindful-organizer cluster

# Generate a report (default: JSON format)
mindful-organizer report --output report.json

# Search for similar files
mindful-organizer search "machine learning models" --top-k 3

# Using a custom database location
mindful-organizer index /path/to/documents --db custom.db
mindful-organizer cluster --db custom.db
```

### Expected Outputs

```
# Indexing
Indexed 42 files in 1.23s

# Clustering
Found 5 clusters in 2.45s

# Search Results
Similar files:
1. research_paper.pdf (similarity: 0.872)
2. notes.txt (similarity: 0.815)
3. presentation.pptx (similarity: 0.792)
```

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
