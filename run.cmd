@echo off
title Search Console Desktop App (Windows CMD)
setlocal enabledelayedexpansion

echo ============================================
echo   Setting up Search Console Desktop App
echo ============================================
echo.

:: --- Check for Python 3 ---
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3 from https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do (
    set version=%%v
)
echo Found Python version: %version%

for /f "tokens=1 delims=." %%a in ("%version%") do (
    if %%a lss 3 (
        echo [ERROR] Python 3 is required. Found Python %version%.
        pause
        exit /b 1
    )
)

:: --- Create virtual environment if it doesn’t exist ---
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo Virtual environment already exists.
)

:: --- Detect virtual environment activation script ---
set ACTIVATE_PATH=.venv\Scripts\activate.bat
if not exist "%ACTIVATE_PATH%" (
    echo [WARN] Default activation path not found.
    echo Searching for activate.bat...
    for /r ".venv" %%F in (activate.bat) do (
        set ACTIVATE_PATH=%%F
        goto :found_activate
    )
    echo [ERROR] Could not find activate.bat inside .venv!
    pause
    exit /b 1
)
:found_activate

echo Activating virtual environment...
call "%ACTIVATE_PATH%"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)

:: --- Install dependencies ---
if exist "requirements.txt" (
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
) else (
    echo Installing default dependencies...
    pip install PyQt5 google-auth-oauthlib google-api-python-client google-generativeai pandas plotly python-dateutil
)
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo All dependencies installed successfully.
echo Starting the application...
echo ============================================
echo.

:: --- Run your Python app ---
python main.py

echo.
echo ============================================
echo Application exited.
echo ============================================
pause
endlocal
