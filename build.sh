#!/bin/bash
# Build script for Mindful Organizer (macOS / Linux)
#
# Uses PyInstaller with the existing mindful_organizer.spec.
# For Windows, use build_windows.bat instead.
#
# CONFIRMED: This script builds from src/ using pyproject.toml dependencies.

set -euo pipefail

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}Building Mindful Organizer...${NC}"

# Check Python version
python_version=$(python3 -c 'import sys; v=sys.version_info; print(f"{v.major}.{v.minor}")')
min_version="3.11"
if [ "$(printf '%s\n' "$min_version" "$python_version" | sort -V | head -n1)" != "$min_version" ]; then
    echo -e "${RED}Error: Python 3.11+ is required (found $python_version)${NC}"
    exit 1
fi

# Check for required build tools
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}Error: pip3 is required but not installed${NC}"
    exit 1
fi

if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo -e "${RED}Error: PyInstaller is required. Install with: pip install pyinstaller${NC}"
    exit 1
fi

# Clean previous builds
echo -e "${BLUE}Cleaning previous builds...${NC}"
rm -rf build/ dist/*.app dist/*.exe dist/*.dmg

# Install / verify dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
pip3 install -e ".[dev]"

# Run tests
echo -e "${BLUE}Running tests...${NC}"
python3 -m pytest -m "not gui and not slow" --tb=short

# Build with PyInstaller
echo -e "${BLUE}Building executable with PyInstaller...${NC}"
python3 -m PyInstaller mindful_organizer.spec --clean

echo -e "${GREEN}Build complete!${NC}"
echo -e "${GREEN}Artifacts are in the dist/ directory.${NC}"
