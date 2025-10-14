"""
build_exe.py
Script to build the Audiobook Generator executable using PyInstaller.
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

def clean_build():
    """Clean previous build artifacts."""
    print("🧹 Cleaning previous build artifacts...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.pyc', '*.pyo', '*.pyd']
    
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"   Removed {dir_name}/")
    
    # Clean .pyc files
    for pyc_file in Path('.').rglob('*.pyc'):
        pyc_file.unlink()
    
    print("✅ Cleanup completed!")

def create_assets_dir():
    """Create assets directory and placeholder files."""
    print("📁 Creating assets directory...")
    
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)
    
    # Create placeholder icon file (you can replace this with actual icon)
    icon_content = """
# Placeholder for app icon
# Replace this with actual icon.ico file
# Recommended size: 256x256 pixels
"""
    
    with open(assets_dir / "icon.ico", "w") as f:
        f.write(icon_content)
    
    print("✅ Assets directory created!")

def build_executable():
    """Build the executable using PyInstaller."""
    print("🔨 Building executable...")
    
    try:
        # Run PyInstaller with the spec file
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            "audiobook_generator.spec"
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Build completed successfully!")
            return True
        else:
            print("❌ Build failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Build error: {str(e)}")
        return False

def create_installer():
    """Create a simple installer/package."""
    print("📦 Creating installer package...")
    
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("❌ No dist directory found. Build failed.")
        return False
    
    # Create installer directory
    installer_dir = Path("installer")
    installer_dir.mkdir(exist_ok=True)
    
    # Copy executable
    exe_file = dist_dir / "AudiobookGenerator.exe"
    if exe_file.exists():
        shutil.copy2(exe_file, installer_dir / "AudiobookGenerator.exe")
        print(f"✅ Copied executable to installer/")
    
    # Create README for installer
    readme_content = """
# Audiobook Generator v1.0.0

## Installation Instructions

1. Extract all files to a folder of your choice
2. Run `AudiobookGenerator.exe`
3. On first launch, you'll be prompted to enter your Google Gemini API key
4. Enjoy creating audiobooks!

## Requirements

- Windows 10 or later
- Internet connection (for AI features)

## Getting API Key

1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Create a new API key
4. Copy the key and paste it when prompted

## Features

- PDF to audiobook conversion
- AI-powered chapter summarization
- Text-to-speech generation
- Library management
- Audio player with controls

## Support

For issues and support, visit: https://github.com/IAMNEERAJ05/audiobook_app

---
© 2025 IAMNEERAJ05
"""
    
    with open(installer_dir / "README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("✅ Installer package created!")
    return True

def main():
    """Main build process."""
    print("🚀 Starting Audiobook Generator build process...")
    print("=" * 50)
    
    # Step 1: Clean previous builds
    clean_build()
    
    # Step 2: Create assets
    create_assets_dir()
    
    # Step 3: Build executable
    if not build_executable():
        print("❌ Build failed. Exiting.")
        return False
    
    # Step 4: Create installer
    if not create_installer():
        print("❌ Installer creation failed.")
        return False
    
    print("=" * 50)
    print("🎉 Build process completed successfully!")
    print("\n📁 Output files:")
    print("   - dist/AudiobookGenerator.exe (Main executable)")
    print("   - installer/ (Complete package)")
    print("\n📋 Next steps:")
    print("   1. Test the executable in dist/")
    print("   2. Package installer/ folder for distribution")
    print("   3. Consider creating an MSI installer for professional distribution")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
