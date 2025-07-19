from setuptools import setup, find_packages

setup(
    name="mindful_organizer",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "PyQt6>=6.4.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scikit-learn>=0.24.0",
        "tensorflow>=2.8.0",
        "keras-tuner>=1.1.0",
        "qiskit>=0.34.0",
        "qiskit-aer>=0.10.0",
        "psutil>=5.8.0",
        "joblib>=1.1.0",
    ],
    entry_points={
        "console_scripts": [
            "mindful-organizer=src.main:main",
        ],
    },
    author="Nicholas Toledo",
    author_email="your.email@example.com",
    description="An AI-powered mindfulness and system optimization application",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords="mindfulness, system optimization, mental health, productivity",
    url="https://github.com/yourusername/mindful_organizer",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python :: 3.9",
        "Topic :: Office/Business :: Scheduling",
    ],
    python_requires=">=3.9",
)
