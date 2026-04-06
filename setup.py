from setuptools import setup, find_packages
from pathlib import Path

# Read requirements from requirements.txt
requirements = []
with open('requirements.txt') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            requirements.append(line)

# Read long description from README.md
long_description = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")

setup(
    name="mindful_organizer",
    version="1.0.0",
    description="A mental health-aware productivity and task management application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Nicholas Toledo",
    author_email="nicholas@example.com",
    url="https://github.com/ntoledo319/Mindful-Organizer",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    package_data={
        "": ["resources/**/*", "windows_store/assets/*"],
    },
    install_requires=[
        "PyQt6>=6.4.0",
        "numpy>=1.21.0",
        "pandas>=1.4.0",
        "python-dateutil>=2.8.2",
        "scikit-learn>=1.0.0",
        "joblib>=1.1.0",
        "cryptography>=38.0.0",
        "psutil>=5.9.0",
        "matplotlib>=3.5.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "pytest-qt>=4.2.0",
            "black>=22.3.0",
            "flake8>=4.0.0",
            "mypy>=0.910",
            "sphinx>=4.4.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
        "ml": [
            "sentence-transformers>=2.2.0",
            "hdbscan>=0.8.28",
            "umap-learn>=0.5.3",
        ],
        "windows": [
            "pyinstaller>=5.0",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Scheduling",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
    ],
    entry_points={
        "console_scripts": [
            "mindful-organizer=main:main",
        ],
        "gui_scripts": [
            "mindful-organizer-gui=main:main",
        ],
    },
    keywords=[
        "mental-health", "productivity", "task-management", "adhd",
        "anxiety", "depression", "ocd", "ptsd", "dbt", "cbt",
        "mood-tracking", "wellness", "organizer",
    ],
)
