@echo off
REM ==========================================================
REM run.bat - Setup and run script for Windows
REM Equivalent to run.sh, fixed to stay open after running
REM ==========================================================

setlocal enabledelayedexpansion

REM === Colors ===
for /F "tokens=2 delims==" %%a in ('"echo prompt $E|cmd"') do set "ESC=%%a"
set "GREEN=%ESC%[32m"
set "RED=%ESC%[31m"
set "BLUE=%ESC%[34m"
set "RESET=%ESC%[0m"

echo %BLUE%=== Setting up Search Console Desktop App ===%RESET%

REM === Check Python ===
echo %BLUE%Checking Python...%RESET%

set "PYTHON_CMD="
for %%P in (python python3) do (
    where %%P >nul 2>nul
    if !errorlevel! == 0 (
        for /f "tokens=2" %%V in ('%%P --version 2^>^&1') do (
            if /I "%%V" GEQ "3" (
                set "PYTHON_CMD=%%P"
                echo %GREEN%Python found: %%P%%RESET%
                goto :foundpython
            )
        )
    )
)

echo %RED%Error: Python 3 not found.%RESET%
goto :pauseexit

:foundpython

REM === Create virtual environment if missing ===
if not exist ".venv" (
    echo %BLUE%Creating virtual environment...%RESET%
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 (
        echo %RED%Failed to create virtual environment.%RESET%
        goto :pauseexit
    )
    echo %GREEN%Virtual environment created.%RESET%
) else (
    echo %GREEN%Virtual environment already exists.%RESET%
)

REM === Activate virtual environment ===
echo %BLUE%Activating virtual environment...%RESET%
call .venv\Scripts\activate.bat

REM === Install dependencies ===
if exist requirements.txt (
    echo %BLUE%Installing dependencies from requirements.txt...%RESET%
    pip install -r requirements.txt
) else (
    echo %BLUE%Installing default dependencies...%RESET%
    pip install PyQt5 google-auth-oauthlib google-api-python-client google-generativeai pandas plotly python-dateutil
)

if errorlevel 1 (
    echo %RED%Dependency installation failed.%RESET%
    goto :pauseexit
)
echo %GREEN%All dependencies installed.%RESET%

REM === Run the application ===
echo %BLUE%Starting application...%RESET%
%PYTHON_CMD% main.py

REM === Keep window open after execution ===
:pauseexit
echo.
echo %BLUE%==========================================%RESET%
echo %GREEN%Script finished. Press any key to close...%RESET%
echo %BLUE%==========================================%RESET%
pause >nul
exit /b 0
