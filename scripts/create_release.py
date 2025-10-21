#!/usr/bin/env python3
"""
Release script for EDMC-StreamSource plugin.

This script helps prepare and create releases locally or can be used
as a reference for the automated GitHub Actions workflow.
"""

import os
import sys
import re
import subprocess
import argparse
from pathlib import Path
import zipfile
from datetime import datetime


def get_current_version():
    """Extract current version from load.py."""
    load_py = Path("load.py")
    if not load_py.exists():
        print("❌ load.py not found. Run this script from the project root.")
        sys.exit(1)
    
    content = load_py.read_text(encoding='utf-8')
    match = re.search(r"VERSION = ['\"]([^'\"]+)['\"]", content)
    
    if match:
        return match.group(1)
    else:
        print("❌ Could not find VERSION in load.py")
        sys.exit(1)


def update_version_in_file(new_version):
    """Update version in load.py."""
    load_py = Path("load.py")
    content = load_py.read_text(encoding='utf-8')
    
    # Update version
    updated_content = re.sub(
        r"VERSION = ['\"][^'\"]+['\"]",
        f"VERSION = '{new_version}'",
        content
    )
    
    if updated_content != content:
        load_py.write_text(updated_content, encoding='utf-8')
        print(f"✅ Updated version to {new_version} in load.py")
        return True
    else:
        print("⚠️ Version was already up to date in load.py")
        return False


def run_tests():
    """Run all available tests."""
    print("🧪 Running tests...")
    
    # Run basic Python syntax check
    result = subprocess.run([sys.executable, "-m", "py_compile", "load.py"], 
                          capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ Syntax error in load.py:")
        print(result.stderr)
        return False
    
    # Run flake8 if available
    try:
        result = subprocess.run([sys.executable, "-m", "flake8", "load.py"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("⚠️ Flake8 warnings/errors:")
            print(result.stdout)
        else:
            print("✅ Flake8 passed")
    except FileNotFoundError:
        print("⚠️ Flake8 not available, skipping lint check")
    
    # Run mypy if available
    try:
        result = subprocess.run([sys.executable, "-m", "mypy", "load.py", "--ignore-missing-imports"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("⚠️ MyPy warnings/errors:")
            print(result.stdout)
        else:
            print("✅ MyPy passed")
    except FileNotFoundError:
        print("⚠️ MyPy not available, skipping type check")
    
    # Run test suite if available
    test_dir = Path("test")
    if test_dir.exists():
        print("Running test suite...")
        result = subprocess.run([sys.executable, "run_tests.py"], 
                              cwd=test_dir,
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Test suite failed:")
            print(result.stdout)
            print(result.stderr)
            return False
        else:
            print("✅ Test suite passed")
    else:
        print("⚠️ No test directory found, skipping tests")
    
    return True


def create_release_package(version, output_dir="dist"):
    """Create release package."""
    print(f"📦 Creating release package for version {version}...")
    
    package_name = f"EDMC-StreamSource-Release-{version}"
    package_dir = Path(output_dir) / package_name
    
    # Create directories
    package_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy essential files
    files_to_copy = [
        "load.py",
        "README.md", 
        "LICENSE"
    ]
    
    optional_files = [
        "CHANGELOG.md",
        "CONTRIBUTING.md"
    ]
    
    # Copy required files
    for file_name in files_to_copy:
        src = Path(file_name)
        if src.exists():
            dst = package_dir / file_name
            dst.write_bytes(src.read_bytes())
            print(f"  ✅ Copied {file_name}")
        else:
            print(f"  ❌ Required file {file_name} not found")
            return None
    
    # Copy optional files
    for file_name in optional_files:
        src = Path(file_name)
        if src.exists():
            dst = package_dir / file_name
            dst.write_bytes(src.read_bytes())
            print(f"  ✅ Copied {file_name}")
    
    # Create installation instructions
    install_txt = package_dir / "INSTALL.txt"
    install_txt.write_text(f"""EDMC-StreamSource Plugin Installation Instructions
================================================

Version: {version}

Installation:
1. Extract this folder to your EDMC plugins directory
2. Rename the folder to 'EDMC-StreamSource' (remove the version suffix)
3. Restart EDMC
4. Configure your output directory in EDMC settings

The plugin will create text files for streaming software like OBS Studio.

For more information, see README.md

Plugin Directory Locations:
- Windows: %LOCALAPPDATA%\\EDMarketConnector\\plugins\\
- macOS: ~/Library/Application Support/EDMarketConnector/plugins/
- Linux: ~/.local/share/EDMarketConnector/plugins/

Support:
- GitHub: https://github.com/gOOvER/EDMC-StreamSource
- Issues: https://github.com/gOOvER/EDMC-StreamSource/issues
""", encoding='utf-8')
    
    # Create version info
    version_txt = package_dir / "VERSION.txt"
    version_txt.write_text(f"""EDMC-StreamSource Plugin
Version: {version}
Build Date: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}
Build Host: {os.uname().nodename if hasattr(os, 'uname') else 'Windows'}
Python Version: {sys.version}
""", encoding='utf-8')
    
    # Create zip file
    zip_path = Path(output_dir) / f"{package_name}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in package_dir.rglob('*'):
            if file_path.is_file():
                arc_path = file_path.relative_to(Path(output_dir))
                zf.write(file_path, arc_path)
    
    print(f"✅ Created release package: {zip_path}")
    print(f"   Package size: {zip_path.stat().st_size / 1024:.1f} KB")
    
    return zip_path


def main():
    parser = argparse.ArgumentParser(description="Create EDMC-StreamSource release")
    parser.add_argument("--version", help="Release version (e.g., 1.11)")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running tests")
    parser.add_argument("--skip-version-update", action="store_true", help="Skip version update")
    parser.add_argument("--output-dir", default="dist", help="Output directory for release")
    
    args = parser.parse_args()
    
    print("🚀 EDMC-StreamSource Release Creator")
    print("=" * 40)
    
    # Get current version
    current_version = get_current_version()
    print(f"📋 Current version: {current_version}")
    
    # Determine target version
    if args.version:
        target_version = args.version
    else:
        target_version = input(f"Enter new version (current: {current_version}): ").strip()
        if not target_version:
            target_version = current_version
            print(f"Using current version: {target_version}")
    
    # Update version if needed
    if not args.skip_version_update and target_version != current_version:
        update_version_in_file(target_version)
    
    # Run tests
    if not args.skip_tests:
        if not run_tests():
            print("❌ Tests failed. Aborting release.")
            sys.exit(1)
    else:
        print("⚠️ Skipping tests (--skip-tests specified)")
    
    # Create release package
    zip_path = create_release_package(target_version, args.output_dir)
    if not zip_path:
        print("❌ Failed to create release package")
        sys.exit(1)
    
    print("\n🎉 Release created successfully!")
    print(f"📦 Release package: {zip_path}")
    print(f"🏷️ Version: {target_version}")
    
    print("\nNext steps:")
    print("1. Test the release package")
    print("2. Create a git tag: git tag v" + target_version)
    print("3. Push the tag: git push origin v" + target_version)
    print("4. The GitHub Actions will create the release automatically")


if __name__ == "__main__":
    main()