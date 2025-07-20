# Mindful Organizer 🧘‍♀️

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/PyQt6-6.4.0+-green.svg" alt="PyQt6">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  <img src="https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows-informational.svg" alt="Platform">
</p>

## 🌟 Overview

Mindful Organizer is a revolutionary mental health-focused task and energy management application that adapts to your unique psychological needs. Unlike traditional productivity apps that push for maximum output, Mindful Organizer prioritizes your mental well-being while helping you stay organized and productive.

### 🎯 Mission Statement

Our mission is to create a productivity tool that doesn't just manage tasks, but actively supports mental health through adaptive interfaces, energy-aware scheduling, and evidence-based therapeutic techniques.

## ✨ Key Features

### 🧠 Mental Health Profile System
- **Adaptive Interface**: UI automatically adjusts based on your mental health profile
- **Clinical Combinations**: Support for ADHD, Anxiety, Depression, OCD, PTSD, and combinations
- **Personalized Recommendations**: Task scheduling that respects your energy patterns
- **Therapy Integration**: Built-in CBT, DBT, ACT, and mindfulness techniques

### 📋 Intelligent Task Management
- **Energy-Based Prioritization**: Tasks are scheduled based on your available mental energy
- **Smart Categorization**: Work, Personal, Health, Learning, Social, and custom categories
- **Adaptive Scheduling**: Automatically adjusts deadlines based on your current state
- **Break Suggestions**: Intelligent break reminders based on energy depletion

### 🎨 Customizable Themes
- **Light Mode**: Clean and energizing for high-energy periods
- **Dark Mode**: Reduces eye strain during low-energy times
- **Calm Mode**: Soothing colors for anxiety management
- **High Contrast**: Accessibility-focused for better focus

### 🤖 AI-Powered Features
- **Quantum-Enhanced Optimization**: Uses Qiskit for advanced task scheduling
- **Machine Learning**: Learns your patterns to better predict energy levels
- **Natural Language Processing**: Understands task descriptions contextually
- **Predictive Analytics**: Anticipates energy crashes before they happen

### 🗂️ Smart File Organization
- **Auto-Categorization**: Files are automatically sorted based on content
- **Mental State Folders**: Organize work based on required mental energy
- **Quick Access**: Frequently needed files surface when you need them
- **Backup System**: Automatic backups to prevent anxiety about data loss

### 🧘 Wellness Features
- **Guided Meditations**: Curated collection from UCLA MARC, Oxford Mindfulness, NHS
- **Breathing Exercises**: Quick stress relief techniques
- **Mood Tracking**: Daily mood and energy level monitoring
- **Progress Visualization**: See your mental health journey over time

## 🚀 Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager
- Git (for cloning the repository)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/ntoledo319/Mindful-Organizer.git
   cd Mindful-Organizer
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment**
   ```bash
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

4. **Install the application**
   ```bash
   pip install -e .
   ```

### Alternative Installation Methods

#### Using the install script (macOS/Linux):
```bash
chmod +x install.sh
./install.sh
```

#### Building from source:
```bash
chmod +x build.sh
./build.sh
```

## 📖 Usage

### Starting the Application

```bash
mindful-organizer
```

Or use the launch script:
```bash
./launch.sh
```

### First-Time Setup

1. **Mental Health Profile**: Complete the initial assessment to customize your experience
2. **Energy Baseline**: Set your typical energy patterns throughout the day
3. **Therapy Preferences**: Select which therapeutic techniques you'd like integrated
4. **Theme Selection**: Choose your preferred visual theme

### Core Workflows

#### Adding Tasks
1. Click the "Add Task" button or press `Ctrl+N`
2. Enter task details including title, category, and estimated energy requirement
3. Set priority based on importance and urgency
4. The app will suggest optimal scheduling based on your energy patterns

#### Energy Tracking
- Update your current energy level using the slider (0-100)
- The app adapts task suggestions based on your energy
- Low energy? The app suggests simpler tasks and break activities

#### Using Therapeutic Tools
- Access breathing exercises via the wellness menu
- Start guided meditations from the meditation library
- Use grounding techniques during high-anxiety moments
- Journal directly within the app for CBT exercises

## 🏗️ Architecture

### Project Structure

```
mindful_organizer/
├── src/
│   ├── core/                    # Core business logic
│   │   ├── task_manager.py      # Task management system
│   │   ├── ai_optimizer.py      # AI/ML optimization
│   │   ├── file_organizer.py    # File management
│   │   └── system_optimizer.py  # System performance
│   ├── gui/                     # User interface
│   │   └── main_window.py       # PyQt6 main application
│   ├── profile/                 # Mental health profiles
│   │   ├── mental_health_profile_builder.py
│   │   └── clinical_combinations.py
│   ├── security/                # Security features
│   └── file_organization/       # File management system
├── tests/
│   ├── unit/                    # Unit tests
│   └── integration/             # Integration tests
├── resources/
│   ├── meditations/             # Guided meditation library
│   └── guideds.json            # Meditation metadata
├── scripts/                     # Utility scripts
├── docs/                        # Additional documentation
└── .github/workflows/           # CI/CD pipelines
```

### Technology Stack

- **Frontend**: PyQt6 for cross-platform native UI
- **Backend**: Python 3.9+ with async support
- **AI/ML**: TensorFlow, Keras, scikit-learn
- **Quantum**: Qiskit for quantum-enhanced optimization
- **Data**: Pandas for data manipulation, NumPy for calculations
- **System**: psutil for system monitoring

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src

# Run specific test categories
pytest tests/unit/
pytest tests/integration/

# Run with verbose output
pytest -v
```

### Test Coverage Goals
- Unit tests: >80% coverage
- Integration tests: Critical user workflows
- Performance tests: Ensure responsive UI

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details on:
- Code of Conduct
- Development workflow
- Coding standards
- Testing requirements
- PR process

## 📋 Roadmap

### Version 1.1 (Q2 2024)
- [ ] Mobile companion app
- [ ] Cloud sync capabilities
- [ ] Advanced analytics dashboard
- [ ] Integration with calendar apps

### Version 1.2 (Q3 2024)
- [ ] Wearable device integration
- [ ] Voice commands
- [ ] Collaborative features
- [ ] Therapist portal

### Future Features
- AR/VR meditation experiences
- Biometric integration
- AI therapist chat
- Community support features

## 🆘 Support

### Getting Help
- **Documentation**: Check our [comprehensive docs](docs/)
- **Issues**: Report bugs on [GitHub Issues](https://github.com/ntoledo319/Mindful-Organizer/issues)
- **Discussions**: Join our [community discussions](https://github.com/ntoledo319/Mindful-Organizer/discussions)
- **Email**: support@mindfulorganizer.app

### FAQ

**Q: Is my mental health data private?**
A: Absolutely. All data is stored locally on your device. We never transmit personal information.

**Q: Can I use this alongside therapy?**
A: Yes! Mindful Organizer complements professional therapy but doesn't replace it.

**Q: What if I have multiple mental health conditions?**
A: Our clinical combinations system supports multiple conditions and adapts accordingly.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **UCLA MARC** for meditation content
- **Oxford Mindfulness Centre** for mindfulness resources
- **NHS** for clinical relaxation techniques
- **Free Mindfulness Project** for open meditation resources
- Our amazing community of users and contributors

## 📊 Stats & Badges

![GitHub stars](https://img.shields.io/github/stars/ntoledo319/Mindful-Organizer?style=social)
![GitHub forks](https://img.shields.io/github/forks/ntoledo319/Mindful-Organizer?style=social)
![GitHub issues](https://img.shields.io/github/issues/ntoledo319/Mindful-Organizer)
![GitHub pull requests](https://img.shields.io/github/issues-pr/ntoledo319/Mindful-Organizer)

---

<p align="center">
  Made with ❤️ for mental health awareness<br>
  © 2024 Nicholas Toledo
</p>
