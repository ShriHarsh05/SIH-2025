#!/bin/bash
# Linux/Mac Build Script for TM-ICD Mapper

echo "========================================"
echo "TM-ICD Mapper - Build System"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Run the build script
python3 build.py

read -p "Press Enter to exit..."
