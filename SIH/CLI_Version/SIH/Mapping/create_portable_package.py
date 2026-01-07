#!/usr/bin/env python3
"""
Create a portable package of the TM-ICD Mapping System
This creates a lightweight, cross-platform package that can run on any system with Python
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def create_portable_package():
    """Create a portable package"""
    
    print("=" * 70)
    print("TM-ICD MAPPER - PORTABLE PACKAGE CREATOR")
    print("=" * 70)
    
    # Package name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"tm-icd-mapper-portable-{timestamp}"
    package_dir = Path(__file__).parent / "dist" / package_name
    
    print(f"\nCreating portable package: {package_name}")
    
    # Create dist directory
    package_dir.mkdir(parents=True, exist_ok=True)
    
    # Files and directories to include
    include_items = [
        # Python files
        "cli_app.py",
        "database.py",
        "fhir_generator.py",
        "search.py",
        "search_ayurveda.py",
        "search_unani.py",
        "search_icd11_standard.py",
        "search_icd_tm2.py",
        "__init__.py",
        
        # Directories
        "api",
        "build_indexes",
        "data",
        "indexes",
        "ui",
        
        # Documentation
        "README.md",
        "requirements.txt",
        "SETUP_GUIDE.md",
        "CLI_USER_GUIDE.md",
        "CLI_QUICK_START.txt",
        "DATABASE_INTEGRATION_SUMMARY.md",
        
        # Launch scripts
        "run_cli.bat",
        "run_cli.sh",
    ]
    
    # Copy files
    print("\nCopying files...")
    base_path = Path(__file__).parent
    
    for item in include_items:
        src = base_path / item
        dst = package_dir / item
        
        if not src.exists():
            print(f"  ⚠ Skipping {item} (not found)")
            continue
        
        if src.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print(f"  ✓ Copied {item}")
        elif src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"  ✓ Copied {item}/ (directory)")
    
    # Create launcher scripts
    print("\nCreating launcher scripts...")
    
    # Windows launcher
    windows_launcher = package_dir / "START_CLI.bat"
    with open(windows_launcher, 'w') as f:
        f.write("""@echo off
echo ========================================
echo TM-ICD Mapper - CLI Application
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

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
call venv\\Scripts\\activate.bat

REM Install requirements
if not exist "venv\\.installed" (
    echo Installing requirements...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install requirements
        pause
        exit /b 1
    )
    echo. > venv\\.installed
)

REM Run the application
echo.
echo Starting TM-ICD Mapper CLI...
echo.
python cli_app.py

pause
""")
    print(f"  ✓ Created {windows_launcher.name}")
    
    # Linux/Mac launcher
    linux_launcher = package_dir / "START_CLI.sh"
    with open(linux_launcher, 'w') as f:
        f.write("""#!/bin/bash

echo "========================================"
echo "TM-ICD Mapper - CLI Application"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
if [ ! -f "venv/.installed" ]; then
    echo "Installing requirements..."
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install requirements"
        exit 1
    fi
    touch venv/.installed
fi

# Run the application
echo
echo "Starting TM-ICD Mapper CLI..."
echo
python cli_app.py

read -p "Press Enter to exit..."
""")
    
    # Make Linux launcher executable
    os.chmod(linux_launcher, 0o755)
    print(f"  ✓ Created {linux_launcher.name}")
    
    # Create README for the package
    readme = package_dir / "PORTABLE_README.txt"
    with open(readme, 'w') as f:
        f.write(f"""TM-ICD MAPPER - PORTABLE PACKAGE
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

========================================
QUICK START
========================================

WINDOWS:
  Double-click: START_CLI.bat

LINUX/MAC:
  Run in terminal: ./START_CLI.sh
  (or: bash START_CLI.sh)

========================================
REQUIREMENTS
========================================

- Python 3.8 or higher
- Internet connection (first run only, to download dependencies)
- Minimum 2GB RAM
- 1GB free disk space

========================================
FIRST RUN
========================================

On first run, the launcher will:
1. Create a virtual environment (venv folder)
2. Install all required Python packages
3. Start the CLI application

This may take 5-10 minutes depending on your internet speed.
Subsequent runs will be much faster.

========================================
WHAT'S INCLUDED
========================================

- CLI Application (cli_app.py)
- Web UI (ui/ folder)
- API Server (api/ folder)
- Database Module (database.py)
- FHIR Generator (fhir_generator.py)
- Search Modules (search_*.py)
- Build Tools (build_indexes/ folder)
- Data Files (data/ folder)
- Index Files (indexes/ folder)
- Documentation (*.md files)

========================================
DOCUMENTATION
========================================

- CLI_USER_GUIDE.md - Complete CLI usage guide
- CLI_QUICK_START.txt - Quick start instructions
- SETUP_GUIDE.md - Detailed setup instructions
- DATABASE_INTEGRATION_SUMMARY.md - Database documentation

========================================
RUNNING THE WEB UI
========================================

To run the web interface instead of CLI:

WINDOWS:
  venv\\Scripts\\activate
  python api/server.py

LINUX/MAC:
  source venv/bin/activate
  python api/server.py

Then open browser to: http://localhost:5000

========================================
TROUBLESHOOTING
========================================

If you encounter issues:

1. Ensure Python 3.8+ is installed:
   python --version  (Windows)
   python3 --version (Linux/Mac)

2. Manually install requirements:
   pip install -r requirements.txt

3. Check if indexes exist:
   The indexes/ folder should contain .pkl files
   If missing, run build scripts in build_indexes/

4. Check data files:
   The data/ folder should contain .json files

========================================
SUPPORT
========================================

For issues or questions, refer to the documentation files
included in this package.

========================================
""")
    print(f"  ✓ Created {readme.name}")
    
    # Create ZIP archive
    print("\nCreating ZIP archive...")
    zip_path = package_dir.parent / f"{package_name}.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(package_dir.parent)
                zipf.write(file_path, arcname)
                
    print(f"  ✓ Created {zip_path.name}")
    
    # Calculate sizes
    package_size = sum(f.stat().st_size for f in package_dir.rglob('*') if f.is_file())
    zip_size = zip_path.stat().st_size
    
    print("\n" + "=" * 70)
    print("PACKAGE CREATED SUCCESSFULLY")
    print("=" * 70)
    print(f"\nPackage directory: {package_dir}")
    print(f"Package size: {package_size / (1024*1024):.2f} MB")
    print(f"\nZIP archive: {zip_path}")
    print(f"ZIP size: {zip_size / (1024*1024):.2f} MB")
    
    print("\n" + "=" * 70)
    print("DISTRIBUTION INSTRUCTIONS")
    print("=" * 70)
    print("\n1. Share the ZIP file with users")
    print("2. Users extract the ZIP file")
    print("3. Users run the launcher script:")
    print("   - Windows: START_CLI.bat")
    print("   - Linux/Mac: START_CLI.sh")
    print("\nThe launcher will automatically:")
    print("  - Create a virtual environment")
    print("  - Install all dependencies")
    print("  - Start the application")
    
    print("\n" + "=" * 70)
    
    return True

def main():
    """Main entry point"""
    
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    # Check if indexes exist
    indexes_dir = Path("indexes")
    if not indexes_dir.exists() or not list(indexes_dir.glob("*.pkl")):
        print("\n⚠ WARNING: Index files not found!")
        print("The package will not work without index files.")
        print("\nPlease build indexes first:")
        print("  1. python build_indexes/build_indexes_siddha.py")
        print("  2. python build_indexes/build_indexes_ayurveda.py")
        print("  3. python build_indexes/build_indexes_unani.py")
        print("  4. python build_indexes/build_indexes_icd11_standard.py")
        print("  5. python build_indexes/build_indexes_icd_tm2.py")
        print("\nContinue anyway? (y/n): ", end="")
        
        response = input().strip().lower()
        if response != 'y':
            print("Package creation cancelled.")
            return
    
    # Create package
    success = create_portable_package()
    
    if success:
        print("\n✓ Portable package created successfully!")
    else:
        print("\n✗ Package creation failed!")

if __name__ == "__main__":
    main()
