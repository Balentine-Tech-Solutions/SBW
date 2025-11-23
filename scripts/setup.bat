@echo off
REM SBW CLI Tool Setup Script for Windows
REM SBWv1.i2 Mark I Prototype

echo ==================================
echo SBW CLI Tool Setup
echo ==================================
echo.

REM Check Python version
python --version 2>NUL
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher
    pause
    exit /b 1
)

echo Installing SBW CLI Tool...
echo.

REM Install in development mode
pip install -e .

if errorlevel 1 (
    echo ERROR: Installation failed
    pause
    exit /b 1
)

echo.
echo Installation completed successfully!
echo.
echo Usage:
echo   sbw-cli decode input.sbw --out output_dir
echo   decode input.sbw --out output_dir --csv --json --plots
echo.
echo For help:
echo   sbw-cli decode --help
echo.
pause