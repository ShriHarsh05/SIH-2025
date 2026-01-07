#!/usr/bin/env python3
"""
Installation Verification Script
Checks if all dependencies and files are properly set up
"""

import sys
import os
from pathlib import Path

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_check(name, status, message=""):
    symbol = "✅" if status else "❌"
    print(f"{symbol} {name:<40} {message}")
    return status

def check_python_version():
    """Check if Python version is 3.8+"""
    version = sys.version_info
    is_valid = version.major == 3 and version.minor >= 8
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    return print_check(
        "Python Version (3.8+)", 
        is_valid, 
        f"Current: {version_str}"
    )

def check_dependencies():
    """Check if all required packages are installed"""
    print_header("Checking Dependencies")
    
    packages = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "jose",
        "passlib",
        "authlib",
        "sentence_transformers",
        "rank_bm25",
        "sklearn",
        "numpy"
    ]
    
    all_installed = True
    for package in packages:
        try:
            __import__(package)
            print_check(package, True, "Installed")
        except ImportError:
            print_check(package, False, "NOT INSTALLED")
            all_installed = False
    
    return all_installed

def check_files():
    """Check if all required files exist"""
    print_header("Checking Files")
    
    required_files = [
        "api/server.py",
        "api/auth.py",
        "api/autocomplete.py",
        "api/__init__.py",
        "ui/index.html",
        "ui/style.css",
        "ui/script.js",
        "requirements.txt",
        ".env.example"
    ]
    
    all_exist = True
    for file_path in required_files:
        exists = Path(file_path).exists()
        print_check(file_path, exists)
        all_exist = all_exist and exists
    
    return all_exist

def check_data_files():
    """Check if data files exist"""
    print_header("Checking Data Files")
    
    data_files = [
        "data/siddha_clean.json",
        "data/ayurveda_data.json",
        "data/unani_data.json",
        "data/icd11_standard.json",
        "data/icd11_tm_codes.json"
    ]
    
    all_exist = True
    for file_path in data_files:
        exists = Path(file_path).exists()
        print_check(file_path, exists)
        all_exist = all_exist and exists
    
    return all_exist

def check_env_file():
    """Check if .env file exists"""
    print_header("Checking Environment Configuration")
    
    env_exists = Path(".env").exists()
    env_example_exists = Path(".env.example").exists()
    
    print_check(".env file", env_exists, "Create from .env.example" if not env_exists else "")
    print_check(".env.example", env_example_exists)
    
    if not env_exists and env_example_exists:
        print("\n⚠️  Recommendation: Copy .env.example to .env")
        print("   Command: copy .env.example .env  (Windows)")
        print("   Command: cp .env.example .env    (Linux/Mac)")
    
    return env_example_exists

def check_documentation():
    """Check if documentation files exist"""
    print_header("Checking Documentation")
    
    docs = [
        "README_OAUTH.md",
        "OAUTH_SETUP_GUIDE.md",
        "QUICK_START_NEW.md",
        "UI_IMPROVEMENTS.md",
        "CHANGES_SUMMARY.md"
    ]
    
    all_exist = True
    for doc in docs:
        exists = Path(doc).exists()
        print_check(doc, exists)
        all_exist = all_exist and exists
    
    return all_exist

def print_summary(checks):
    """Print summary of all checks"""
    print_header("Summary")
    
    total = len(checks)
    passed = sum(checks.values())
    failed = total - passed
    
    print(f"\nTotal Checks: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All checks passed! Your installation is complete.")
        print("\n📚 Next Steps:")
        print("   1. Start the server: uvicorn api.server:app --reload")
        print("   2. Open browser: http://localhost:8000/ui/index.html")
        print("   3. Login with: demo@example.com / demo123")
        print("\n✨ Enjoy your Traditional Medicine Mapping System!")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\n📚 Installation Guide:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Create .env file: copy .env.example .env")
        print("   3. Check data files exist in data/ folder")
        print("   4. Run this script again to verify")

def main():
    """Main verification function"""
    print("\n" + "="*70)
    print("  🏥 Traditional Medicine Mapping System")
    print("  Installation Verification Script")
    print("="*70)
    
    checks = {
        "Python Version": check_python_version(),
        "Dependencies": check_dependencies(),
        "Core Files": check_files(),
        "Data Files": check_data_files(),
        "Environment": check_env_file(),
        "Documentation": check_documentation()
    }
    
    print_summary(checks)
    
    return 0 if all(checks.values()) else 1

if __name__ == "__main__":
    sys.exit(main())
