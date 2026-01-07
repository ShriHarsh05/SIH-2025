@echo off
REM Windows Build Script for TM-ICD Mapper

echo ========================================
echo TM-ICD Mapper - Build System
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

REM Run the build script
python build.py

pause
