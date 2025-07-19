# Mindful Organizer Git Documentation

## Table of Contents
1. [Project Setup](#project-setup)
2. [Branching Strategy](#branching-strategy)
3. [Commit Guidelines](#commit-guidelines)
4. [Development Workflow](#development-workflow)
5. [Common Commands](#common-commands)

## Project Setup
```bash
# Clone the repository
git clone https://github.com/ntoledo319/Mindful-Organizer.git
cd Mindful-Organizer

# Set up Python virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Branching Strategy
- `main`: Production-ready code (protected branch)
- `develop`: Integration branch for features
- `feature/*`: Feature development branches
- `hotfix/*`: Critical bug fixes
- `release/*`: Release preparation branches

## Commit Guidelines
- Use present tense ("Add feature" not "Added feature")
- Keep first line under 50 characters
- Include detailed message in body when needed
- Reference issues/tickets when applicable

Example:
```
feat: Implement meditation download functionality

Adds functionality to download meditation audio files from multiple sources.
Includes error handling and retry logic.

Fixes #123
```

## Development Workflow
1. Create feature branch from develop:
   ```bash
   git checkout develop
   git pull
   git checkout -b feature/your-feature-name
   ```
2. Make changes and commit
3. Push branch to remote:
   ```bash
   git push -u origin feature/your-feature-name
   ```
4. Create pull request to develop branch
5. After review and approval, merge via PR

## Common Commands
```bash
# Check current status
git status

# Stage changes
git add .

# Commit changes
git commit -m "Your commit message"

# Push to remote
git push

# Pull latest changes
git pull

# Create and switch to new branch
git checkout -b branch-name

# Merge branch
git checkout main
git merge feature/your-feature-name

# View commit history
git log --oneline --graph
```

## Code Review Process
1. All changes require pull request review
2. Minimum 1 approval required before merge
3. CI tests must pass before merging
4. Resolve all comments before merging

## Release Process
1. Create release branch from develop
2. Update version numbers
3. Run final tests
4. Merge to main and tag release
5. Merge back to develop
