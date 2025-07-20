from setuptools import setup, find_packages
from pathlib import Path

# Read requirements from requirements.txt
requirements = []
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# Read long description from README.md
long_description = (Path(__file__).parent / "README.md").read_text()

setup(
    name="mindful_organizer",
    version="0.1.0",
    description="A smart file system for organizing and clustering documents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Nicholas Toledo",
    author_email="nicholas@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=requirements,
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    entry_points={
        "console_scripts": [
            "mindful-organizer=core.smart_file_system.cli:main",
        ],
    },
)
