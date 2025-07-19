#!/bin/bash

# Colors for output
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Uninstalling Mindful Organizer...${NC}"

# Deactivate virtual environment if active
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi

# Remove virtual environment
if [ -d "venv" ]; then
    echo -e "${BLUE}Removing virtual environment...${NC}"
    rm -rf venv
fi

# Remove desktop entry
if [ -f ~/Desktop/MindfulOrganizer.command ]; then
    echo -e "${BLUE}Removing desktop entry...${NC}"
    rm ~/Desktop/MindfulOrganizer.command
fi

# Remove .mindful_organizer directory from home
if [ -d ~/.mindful_organizer ]; then
    echo -e "${BLUE}Removing application data...${NC}"
    rm -rf ~/.mindful_organizer
fi

echo -e "${RED}Uninstallation complete!${NC}"
