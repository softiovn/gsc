@echo off
set "VENV_DIR=venv"

echo Checking for Python 3...
python --version 2>NUL
if errorlevel 1 (
    echo Python 3 not found. Please ensure Python 3 is installed and in your PATH.
    pause
    exit /b 1
) else (
    echo Python 3 found.
)

echo Creating virtual environment...
python -m venv %VENV_DIR%

if exist "%VENV_DIR%\Scripts\activate.bat" (
    echo Activating virtual environment...
    call "%VENV_DIR%\Scripts\activate.bat"
) else (
    echo Error: Could not find virtual environment activation script.
    pause
    exit /b 1
)

echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

echo Launching main.py...
python main.py

echo Deactivating virtual environment...
deactivate

pause