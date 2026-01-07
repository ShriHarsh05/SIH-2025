#!/usr/bin/env python3
"""
Cross-platform executable builder for TM-ICD Mapping System
Uses PyInstaller to create standalone executables for Windows and Linux
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        print("✓ PyInstaller is installed")
        return True
    except ImportError:
        print("✗ PyInstaller is not installed")
        print("\nInstalling PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✓ PyInstaller installed successfully")
            return True
        except Exception as e:
            print(f"✗ Failed to install PyInstaller: {e}")
            print("\nPlease install manually: pip install pyinstaller")
            return False

def create_spec_file():
    """Create PyInstaller spec file for the CLI application"""
    
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Data files to include
datas = [
    ('data/*.json', 'data'),
    ('indexes/*', 'indexes'),
]

# Hidden imports (modules not automatically detected)
hiddenimports = [
    'sklearn.utils._cython_blas',
    'sklearn.neighbors.typedefs',
    'sklearn.neighbors.quad_tree',
    'sklearn.tree._utils',
    'sentence_transformers',
    'torch',
    'transformers',
    'rank_bm25',
    'sqlite3',
]

a = Analysis(
    ['cli_app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='tm-icd-mapper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='tm-icd-mapper',
)
"""
    
    spec_file = Path(__file__).parent / "tm-icd-mapper.spec"
    with open(spec_file, 'w') as f:
        f.write(spec_content)
    
    print(f"✓ Created spec file: {spec_file}")
    return spec_file

def build_executable():
    """Build the executable using PyInstaller"""
    
    print("=" * 70)
    print("TM-ICD MAPPER - EXECUTABLE BUILDER")
    print("=" * 70)
    
    # Check system
    system = platform.system()
    print(f"\nDetected OS: {system}")
    print(f"Python version: {sys.version}")
    
    # Check PyInstaller
    if not check_pyinstaller():
        return False
    
    # Create spec file
    print("\nCreating PyInstaller spec file...")
    spec_file = create_spec_file()
    
    # Build executable
    print("\nBuilding executable...")
    print("This may take several minutes...")
    print("-" * 70)
    
    try:
        # Run PyInstaller
        cmd = [
            sys.executable,
            "-m", "PyInstaller",
            "--clean",
            str(spec_file)
        ]
        
        subprocess.check_call(cmd)
        
        print("-" * 70)
        print("\n✓ Build completed successfully!")
        
        # Show output location
        dist_dir = Path(__file__).parent / "dist" / "tm-icd-mapper"
        print(f"\nExecutable location: {dist_dir}")
        
        if system == "Windows":
            exe_name = "tm-icd-mapper.exe"
        else:
            exe_name = "tm-icd-mapper"
        
        exe_path = dist_dir / exe_name
        
        if exe_path.exists():
            print(f"Executable file: {exe_path}")
            print(f"\nTo run the application:")
            if system == "Windows":
                print(f"  {exe_path}")
            else:
                print(f"  ./{exe_path}")
        
        print("\n" + "=" * 70)
        print("BUILD SUMMARY")
        print("=" * 70)
        print(f"Platform: {system}")
        print(f"Output directory: {dist_dir}")
        print(f"Executable: {exe_name}")
        print("\nThe 'dist/tm-icd-mapper' folder contains:")
        print("  - The executable file")
        print("  - All required dependencies")
        print("  - Data files (indexes, JSON data)")
        print("\nYou can distribute this entire folder to other machines.")
        print("=" * 70)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point"""
    
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    # Check if indexes exist
    indexes_dir = Path("indexes")
    if not indexes_dir.exists() or not list(indexes_dir.glob("*.pkl")):
        print("\n⚠ WARNING: Index files not found!")
        print("Please build indexes first before creating executable:")
        print("  1. python build_indexes/build_indexes_siddha.py")
        print("  2. python build_indexes/build_indexes_ayurveda.py")
        print("  3. python build_indexes/build_indexes_unani.py")
        print("  4. python build_indexes/build_indexes_icd11_standard.py")
        print("  5. python build_indexes/build_indexes_icd_tm2.py")
        print("\nContinue anyway? (y/n): ", end="")
        
        response = input().strip().lower()
        if response != 'y':
            print("Build cancelled.")
            return
    
    # Build
    success = build_executable()
    
    if success:
        print("\n✓ Executable build completed successfully!")
        sys.exit(0)
    else:
        print("\n✗ Executable build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
