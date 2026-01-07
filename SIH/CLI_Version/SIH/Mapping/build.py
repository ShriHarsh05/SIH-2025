#!/usr/bin/env python3
"""
Master build script for TM-ICD Mapping System
Provides options for creating different types of distributions
"""

import sys
import subprocess
from pathlib import Path

def print_menu():
    """Print build options menu"""
    print("=" * 70)
    print("TM-ICD MAPPER - BUILD SYSTEM")
    print("=" * 70)
    print("\nBuild Options:\n")
    print("  1. Create Portable Package (Recommended)")
    print("     - Lightweight ZIP package")
    print("     - Works on Windows, Linux, Mac")
    print("     - Requires Python on target system")
    print("     - Auto-installs dependencies on first run")
    print("     - Size: ~50-100 MB")
    print()
    print("  2. Create Standalone Executable (PyInstaller)")
    print("     - Single executable file")
    print("     - No Python required on target system")
    print("     - Larger file size")
    print("     - Size: ~500-800 MB")
    print()
    print("  3. Build All Index Files")
    print("     - Required before creating distributions")
    print("     - Builds search indexes for all systems")
    print()
    print("  4. Test Database Integration")
    print("     - Run database tests")
    print()
    print("  0. Exit")
    print()

def build_indexes():
    """Build all index files"""
    print("\n" + "=" * 70)
    print("BUILDING INDEX FILES")
    print("=" * 70)
    
    scripts = [
        "build_indexes/build_indexes_siddha.py",
        "build_indexes/build_indexes_ayurveda.py",
        "build_indexes/build_indexes_unani.py",
        "build_indexes/build_indexes_ayurveda_sat.py",
        "build_indexes/build_indexes_icd11_standard.py",
        "build_indexes/build_indexes_icd_tm2.py",
    ]
    
    for script in scripts:
        script_path = Path(__file__).parent / script
        if not script_path.exists():
            print(f"\n✗ Script not found: {script}")
            continue
        
        print(f"\n{'=' * 70}")
        print(f"Building: {script}")
        print('=' * 70)
        
        try:
            subprocess.check_call([sys.executable, str(script_path)])
            print(f"✓ Completed: {script}")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed: {script}")
            print(f"Error: {e}")
            return False
        except KeyboardInterrupt:
            print("\n\n✗ Build interrupted by user")
            return False
    
    print("\n" + "=" * 70)
    print("✓ ALL INDEX FILES BUILT SUCCESSFULLY")
    print("=" * 70)
    return True

def create_portable():
    """Create portable package"""
    script = Path(__file__).parent / "create_portable_package.py"
    try:
        subprocess.check_call([sys.executable, str(script)])
        return True
    except subprocess.CalledProcessError:
        return False

def create_executable():
    """Create standalone executable"""
    script = Path(__file__).parent / "build_executable.py"
    try:
        subprocess.check_call([sys.executable, str(script)])
        return True
    except subprocess.CalledProcessError:
        return False

def test_database():
    """Test database integration"""
    script = Path(__file__).parent / "test_database.py"
    try:
        subprocess.check_call([sys.executable, str(script)])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    """Main entry point"""
    
    while True:
        print_menu()
        
        choice = input("Enter your choice (0-4): ").strip()
        
        if choice == '1':
            print("\n" + "=" * 70)
            print("CREATING PORTABLE PACKAGE")
            print("=" * 70)
            success = create_portable()
            if success:
                print("\n✓ Portable package created successfully!")
            else:
                print("\n✗ Failed to create portable package")
            input("\nPress Enter to continue...")
            
        elif choice == '2':
            print("\n" + "=" * 70)
            print("CREATING STANDALONE EXECUTABLE")
            print("=" * 70)
            success = create_executable()
            if success:
                print("\n✓ Executable created successfully!")
            else:
                print("\n✗ Failed to create executable")
            input("\nPress Enter to continue...")
            
        elif choice == '3':
            success = build_indexes()
            if not success:
                print("\n✗ Index building failed or was interrupted")
            input("\nPress Enter to continue...")
            
        elif choice == '4':
            print("\n" + "=" * 70)
            print("TESTING DATABASE INTEGRATION")
            print("=" * 70)
            success = test_database()
            if success:
                print("\n✓ Database tests completed!")
            else:
                print("\n✗ Database tests failed")
            input("\nPress Enter to continue...")
            
        elif choice == '0':
            print("\nExiting build system. Goodbye!")
            sys.exit(0)
            
        else:
            print("\n✗ Invalid choice. Please try again.")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBuild system interrupted by user. Goodbye!")
        sys.exit(0)
