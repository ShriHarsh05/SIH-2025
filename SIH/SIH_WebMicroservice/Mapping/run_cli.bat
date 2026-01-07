@echo off
REM Windows batch script to run CLI application

echo ========================================
echo Traditional Medicine - ICD-11 Mapper
echo CLI Application
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher
    pause
    exit /b 1
)

REM Run the CLI application
python cli_app.py

pause
