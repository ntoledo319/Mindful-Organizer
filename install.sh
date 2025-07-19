#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Installing Mindful Organizer...${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo -e "${BLUE}Upgrading pip...${NC}"
pip install --upgrade pip

# Install requirements
echo -e "${BLUE}Installing dependencies...${NC}"
pip install -r requirements.txt

# Install the package in development mode
echo -e "${BLUE}Installing Mindful Organizer...${NC}"
pip install -e .

# Create desktop entry
echo -e "${BLUE}Creating desktop entry...${NC}"
cat > ~/Desktop/MindfulOrganizer.command << EOL
#!/bin/bash
cd "$(dirname "$0")"
cd ../CascadeProjects/mindful_organizer
source venv/bin/activate
mindful-organizer
EOL

# Make the desktop entry executable
chmod +x ~/Desktop/MindfulOrganizer.command

echo -e "${GREEN}Installation complete!${NC}"
echo -e "${GREEN}You can now run Mindful Organizer by double-clicking MindfulOrganizer.command on your desktop${NC}"
