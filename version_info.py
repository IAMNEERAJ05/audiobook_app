"""
version_info.py
Application version and metadata information.
"""
import sys
from pathlib import Path

# Application metadata
APP_NAME = "Audiobook Generator"
APP_VERSION = "1.0.0"
APP_AUTHOR = "IAMNEERAJ05"
APP_DESCRIPTION = "AI-powered audiobook generator with PDF processing, summarization, and text-to-speech capabilities"
APP_URL = "https://github.com/IAMNEERAJ05/audiobook_app"

# Build information
BUILD_DATE = "2025-01-27"
PYTHON_VERSION = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

# File paths
BASE_DIR = Path(__file__).parent
ICON_PATH = BASE_DIR / "assets" / "icon.ico"
LOGO_PATH = BASE_DIR / "assets" / "logo.png"

def get_version_string():
    """Get formatted version string."""
    return f"{APP_NAME} v{APP_VERSION}"

def get_build_info():
    """Get build information string."""
    return f"Built on {BUILD_DATE} with Python {PYTHON_VERSION}"

def get_app_info():
    """Get complete application information."""
    return {
        'name': APP_NAME,
        'version': APP_VERSION,
        'author': APP_AUTHOR,
        'description': APP_DESCRIPTION,
        'url': APP_URL,
        'build_date': BUILD_DATE,
        'python_version': PYTHON_VERSION
    }
