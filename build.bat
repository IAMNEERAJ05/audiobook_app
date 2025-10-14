@echo off
echo Building Audiobook Generator...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Install/update requirements
echo Installing requirements...
pip install -r requirements.txt

REM Run the build script
echo.
echo Starting build process...
python build_exe.py

echo.
echo Build process completed!
pause
