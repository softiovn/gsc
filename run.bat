@echo off
REM run.bat - Simple setup and run script for Windows Command Prompt

echo === Setting up Search Console Desktop App ===

REM Check if Python is installed
echo Checking Python...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Python found
    set PYTHON_CMD=python
    goto check_python_version
)

python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Python 3 found
    set PYTHON_CMD=python3
    goto check_python_version
)

echo Error: Python is not installed or not in PATH
echo Please install Python 3 from https://python.org
pause
exit /b 1

:check_python_version
REM Check Python version (major version only)
for /f "tokens=1" %%i in ('%PYTHON_CMD% -c "import sys; print(sys.version_info[0])" 2^>nul') do set PYTHON_MAJOR=%%i

if "%PYTHON_MAJOR%" NEQ "3" (
    echo Error: Python 3 is required but found Python %PYTHON_MAJOR%
    pause
    exit /b 1
)

%PYTHON_CMD% -c "import sys; print('Using Python: ' + sys.version)" 2>nul

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo Creating virtual environment...
    %PYTHON_CMD% -m venv .venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install requirements
if exist "requirements.txt" (
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
) else (
    echo Installing dependencies...
    pip install PyQt5 google-auth-oauthlib google-api-python-client google-generativeai pandas plotly python-dateutil
)

echo All dependencies installed

REM Run the application
echo Starting application...
%PYTHON_CMD% main.py

REM Keep window open if there's an error
if %errorlevel% neq 0 (
    echo.
    echo Application exited with error code %errorlevel%
    pause
)