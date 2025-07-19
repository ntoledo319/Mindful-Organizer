#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}Building Mindful Organizer...${NC}"

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if (( $(echo "$python_version < 3.9" | bc -l) )); then
    echo -e "${RED}Error: Python 3.9 or higher is required (found $python_version)${NC}"
    exit 1
fi

# Check for required build tools
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}Error: pip3 is required but not installed${NC}"
    exit 1
fi

# Clean previous builds
echo -e "${BLUE}Cleaning previous builds...${NC}"
rm -rf build/ dist/ *.egg-info/

# Create optimized Python bytecode
echo -e "${BLUE}Compiling Python bytecode...${NC}"
python3 -m compileall mindful_organizer/

# Build the package
echo -e "${BLUE}Building package...${NC}"
python3 setup.py sdist bdist_wheel

# Run tests if they exist
if [ -d "tests" ]; then
    echo -e "${BLUE}Running tests...${NC}"
    python3 -m pytest tests/
fi

# Create application bundle for macOS
echo -e "${BLUE}Creating application bundle...${NC}"
mkdir -p "dist/Mindful Organizer.app/Contents/"{MacOS,Resources}

# Create Info.plist
cat > "dist/Mindful Organizer.app/Contents/Info.plist" << EOL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>MindfulOrganizer</string>
    <key>CFBundleIdentifier</key>
    <string>com.mindfulorganizer.app</string>
    <key>CFBundleName</key>
    <string>Mindful Organizer</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOL

# Create launcher script
cat > "dist/Mindful Organizer.app/Contents/MacOS/MindfulOrganizer" << EOL
#!/bin/bash
cd "\$(dirname "\$0")"
source ../Resources/venv/bin/activate
mindful-organizer
EOL

chmod +x "dist/Mindful Organizer.app/Contents/MacOS/MindfulOrganizer"

# Copy resources
cp -r venv "dist/Mindful Organizer.app/Contents/Resources/"
cp -r mindful_organizer/resources/* "dist/Mindful Organizer.app/Contents/Resources/"

echo -e "${GREEN}Build complete!${NC}"
echo -e "${GREEN}You can find the application bundle in the dist directory${NC}"
