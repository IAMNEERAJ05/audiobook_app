# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

# Get the base directory
base_dir = Path.cwd()

# Define data files to include
datas = [
    ('data', 'data'),
    ('requirements.txt', '.'),
    ('README.md', '.'),
]

# Define hidden imports (modules that PyInstaller might miss)
hiddenimports = [
    'PyQt5.QtCore',
    'PyQt5.QtGui', 
    'PyQt5.QtWidgets',
    'google.generativeai',
    'pyttsx3',
    'PyMuPDF',
    'python-dotenv',
    'tqdm',
    'difflib',
    'soundfile',
    'numpy',
    'pydub',
    'sqlite3',
    'json',
    'base64',
    'codecs'
]

# Define excluded modules (to reduce size)
excludes = [
    'tkinter',
    'matplotlib',
    'scipy',
    'pandas',
    'jupyter',
    'IPython',
    'notebook'
]

# Analysis configuration
a = Analysis(
    ['main.py'],
    pathex=[str(base_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove duplicate files
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Create executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AudiobookGenerator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one
    version='version_info.txt'  # Version info file
)
