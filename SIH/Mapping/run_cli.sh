#!/bin/bash
# Linux/Mac shell script to run CLI application

echo "========================================"
echo "Traditional Medicine - ICD-11 Mapper"
echo "CLI Application"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.7 or higher"
    exit 1
fi

# Make cli_app.py executable
chmod +x cli_app.py

# Run the CLI application
python3 cli_app.py
