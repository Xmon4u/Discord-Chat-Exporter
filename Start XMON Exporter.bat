@echo off
title XMON Discord Chat Exporter
color 0F

echo.
echo  ============================================
echo   XMON Discord Chat Exporter
echo  ============================================
echo.

:: Move to the folder where this bat file lives
cd /d "%~dp0"

:: Check Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found!
    echo  Please install Python from https://www.python.org/downloads/
    echo  Make sure to check "Add Python to PATH" during install.
    echo.
    pause
    exit /b 1
)

:: Install/check dependencies silently
echo  Checking dependencies...
pip install -r requirements.txt --quiet

echo  Starting XMON Exporter...
echo.

:: Launch the GUI
python main.py

:: If it crashes, keep window open to show error
if errorlevel 1 (
    echo.
    echo  [ERROR] Something went wrong. See message above.
    pause
)
