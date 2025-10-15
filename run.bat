@echo off
chcp 65001 >nul
title Search Analytics Pro

echo ========================================
echo   Search Analytics Pro - Starting...
echo ========================================

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

:: Check if virtual environment exists, if not create it
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Install/upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

:: Check if requirements are already installed, if not install them
echo Installing required packages...
pip install -r requirements.txt

:: Run the main application
echo ========================================
echo   Starting Search Analytics Pro...
echo ========================================
python main.py

:: Deactivate virtual environment when done
deactivate

pause