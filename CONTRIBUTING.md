# Contributing to Mindful Organizer 🤝

First off, thank you for considering contributing to Mindful Organizer! It's people like you that make this a tool that truly helps people manage their mental health while staying productive.

## 📋 Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [How Can I Contribute?](#how-can-i-contribute)
4. [Development Process](#development-process)
5. [Style Guidelines](#style-guidelines)
6. [Commit Messages](#commit-messages)
7. [Pull Request Process](#pull-request-process)
8. [Community](#community)

## 📜 Code of Conduct

### Our Pledge

We are committed to providing a friendly, safe, and welcoming environment for all, regardless of:
- Level of experience
- Gender identity and expression
- Sexual orientation
- Disability
- Personal appearance
- Body size
- Race, ethnicity, or religion
- Nationality
- Mental health status

### Mental Health Awareness

Given the nature of our application, we especially emphasize:
- **Respectful language** around mental health topics
- **Avoiding stigmatizing** terminology
- **Being supportive** of different mental health journeys
- **Maintaining confidentiality** if users share personal experiences

### Our Standards

Examples of behavior that contributes to a positive environment:
- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have:
- Python 3.9 or higher
- Git
- A GitHub account
- PyQt6 development tools
- Basic understanding of mental health sensitivity

### Setting Up Your Development Environment

1. **Fork the repository**
   - Click the "Fork" button at the top of the [Mindful Organizer repository](https://github.com/ntoledo319/Mindful-Organizer)

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR-USERNAME/Mindful-Organizer.git
   cd Mindful-Organizer
   ```

3. **Add upstream remote**
   ```bash
   git remote add upstream https://github.com/ntoledo319/Mindful-Organizer.git
   ```

4. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

5. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

6. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

## 🎯 How Can I Contribute?

### 🐛 Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear and descriptive title**
- **Detailed description** of the issue
- **Steps to reproduce** the behavior
- **Expected behavior** description
- **Screenshots** if applicable
- **System information**:
  - OS: [e.g., macOS 12.0]
  - Python version
  - Mindful Organizer version
- **Mental health profile settings** (if relevant and comfortable sharing)

### 💡 Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Use case**: Who will benefit and how?
- **Mental health impact**: How does this help users' well-being?
- **Proposed solution**: Your idea for implementation
- **Alternatives considered**: Other approaches you've thought about
- **Mockups/wireframes**: Visual representations if applicable

### 🔧 Code Contributions

#### Areas We Need Help With

- **Mental Health Features**
  - New therapy technique integrations
  - Improved mood tracking algorithms
  - Better energy prediction models
  
- **User Interface**
  - Accessibility improvements
  - New calming themes
  - Better responsive design
  
- **AI/ML Enhancements**
  - Improved task scheduling algorithms
  - Better pattern recognition
  - Quantum optimization improvements
  
- **Testing**
  - Unit test coverage
  - Integration tests
  - Performance benchmarks
  
- **Documentation**
  - User guides
  - API documentation
  - Translation to other languages

## 💻 Development Process

### Branch Naming Convention

- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `hotfix/description` - Critical fixes for production
- `docs/description` - Documentation updates
- `test/description` - Test additions/improvements

### Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, readable code
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Run unit tests
   pytest tests/unit/
   
   # Run integration tests
   pytest tests/integration/
   
   # Check code coverage
   pytest --cov=src --cov-report=html
   
   # Lint your code
   flake8 src/
   black src/
   ```

4. **Commit your changes** (see [Commit Messages](#commit-messages))

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**

### Mental Health Considerations in Code

When developing features:
- Consider users in various mental states
- Avoid overwhelming UI elements
- Provide clear, calming feedback
- Include appropriate content warnings
- Respect user privacy and data

## 🎨 Style Guidelines

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with these additions:

```python
# Good: Clear, descriptive names
def calculate_energy_level(mood_score: float, sleep_hours: float) -> float:
    """
    Calculate user's energy level based on mood and sleep.
    
    Args:
        mood_score: Current mood rating (0-10)
        sleep_hours: Hours of sleep last night
        
    Returns:
        Energy level as percentage (0-100)
    """
    # Implementation here
    
# Bad: Unclear naming
def calc_e(m, s):
    # Implementation here
```

### UI/UX Guidelines

- **Color Usage**: Consider color-blind users and those sensitive to bright colors
- **Animations**: Keep them subtle and provide option to disable
- **Text**: Use clear, simple language avoiding mental health jargon
- **Icons**: Use universally understood symbols
- **Spacing**: Provide adequate whitespace to avoid overwhelming users

### Documentation Style

- Write in clear, simple English
- Avoid mental health stigma in language
- Include examples for complex features
- Add screenshots for UI changes
- Document accessibility features

## 📝 Commit Messages

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, missing semicolons, etc.)
- **refactor**: Code changes that neither fix bugs nor add features
- **perf**: Performance improvements
- **test**: Adding or updating tests
- **chore**: Changes to build process or auxiliary tools

### Examples

```
feat(profile): add anxiety-specific UI adaptations

Implement automatic UI adjustments when anxiety is detected:
- Reduce animation speed
- Soften color contrasts
- Increase spacing between elements

Closes #123
```

```
fix(tasks): prevent task overflow during low energy periods

Tasks are now properly queued when user energy drops below 30%.
Previous behavior was causing stress by showing too many tasks.

Fixes #456
```

## 🔄 Pull Request Process

### Before Submitting

1. **Update documentation** for any changed functionality
2. **Add tests** for new features
3. **Run the test suite** and ensure all tests pass
4. **Update the README.md** if needed
5. **Check that your code follows** the style guidelines

### PR Template

When creating a PR, include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update

## Mental Health Impact
How do these changes affect users' mental health experience?

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review
- [ ] I have commented my code where necessary
- [ ] I have updated the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix/feature works
- [ ] New and existing unit tests pass locally
```

### Review Process

1. At least one maintainer review required
2. All CI checks must pass
3. No merge conflicts
4. Documentation updated if needed
5. Mental health impact considered

## 🌟 Community

### Getting Help

- **Discord**: [Join our community](https://discord.gg/mindfulorganizer)
- **GitHub Discussions**: For general questions and ideas
- **Stack Overflow**: Tag questions with `mindful-organizer`

### Recognition

Contributors are recognized in:
- [CONTRIBUTORS.md](CONTRIBUTORS.md) file
- Release notes
- Annual contributor spotlight blog posts

### Mental Health Resources

If working on this project brings up mental health concerns:
- [National Suicide Prevention Lifeline](https://suicidepreventionlifeline.org/): 988
- [Crisis Text Line](https://www.crisistextline.org/): Text HOME to 741741
- [International Crisis Lines](https://findahelpline.com/)

## 📚 Additional Resources

- [Project Architecture](docs/ARCHITECTURE.md)
- [API Documentation](docs/API.md)
- [Mental Health Guidelines](docs/MENTAL_HEALTH_GUIDELINES.md)
- [Security Policy](SECURITY.md)

---

Thank you for contributing to Mindful Organizer! Together, we're building a tool that makes a real difference in people's lives. 💚