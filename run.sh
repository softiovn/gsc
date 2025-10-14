#!/bin/bash

# run.sh - Simple setup and run script

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Setting up Search Console Desktop App ===${NC}"

# Check if Python is installed (try python3 first, then python)
echo -e "${BLUE}Checking Python...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo -e "${GREEN}Python 3 found: $(python3 --version)${NC}"
elif command -v python &> /dev/null; then
    # Check if python command points to Python 3
    PYTHON_VERSION=$(python -c "import sys; print(sys.version_info.major)" 2>/dev/null || echo "0")
    if [ "$PYTHON_VERSION" -eq 3 ]; then
        PYTHON_CMD="python"
        echo -e "${GREEN}Python 3 found: $(python --version)${NC}"
    else
        echo -e "${RED}Error: Python 3 is not installed (found Python 2)${NC}"
        exit 1
    fi
else
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    $PYTHON_CMD -m venv .venv
    echo -e "${GREEN}Virtual environment created${NC}"
else
    echo -e "${GREEN}Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source .venv/bin/activate

# Install requirements
if [ -f "requirements.txt" ]; then
    echo -e "${BLUE}Installing dependencies from requirements.txt...${NC}"
    pip install -r requirements.txt
else
    echo -e "${BLUE}Installing dependencies...${NC}"
    pip install PyQt5 google-auth-oauthlib google-api-python-client google-generativeai pandas plotly python-dateutil
fi

echo -e "${GREEN}All dependencies installed${NC}"

# Run the application
echo -e "${BLUE}Starting application...${NC}"
$PYTHON_CMD main.py