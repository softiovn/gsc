# run.ps1 - Windows setup and run script
# To execute: Right-click → Run with PowerShell
# Or in terminal: powershell -ExecutionPolicy Bypass -File run.ps1

$ErrorActionPreference = "Stop"

# --- Colors ---
$GREEN = "`e[32m"
$RED = "`e[31m"
$BLUE = "`e[34m"
$NC = "`e[0m"

Write-Host "$BLUE=== Setting up Search Console Desktop App ===$NC"

# --- Check Python installation ---
Write-Host "$BLUE Checking Python...$NC"

$pythonCmd = ""
$python3 = Get-Command python3 -ErrorAction SilentlyContinue
$python = Get-Command python -ErrorAction SilentlyContinue

if ($python3) {
    $pythonCmd = "python3"
    Write-Host "$GREEN Python 3 found: $("$(python3 --version)")$NC"
}
elseif ($python) {
    $ver = & python -c "import sys; print(sys.version_info.major)" 2>$null
    if ($ver -eq 3) {
        $pythonCmd = "python"
        Write-Host "$GREEN Python 3 found: $("$(python --version)")$NC"
    }
    else {
        Write-Host "$RED Error: Python 3 is not installed (found Python 2)$NC"
        exit 1
    }
}
else {
    Write-Host "$RED Error: Python 3 not found. Please install Python 3 first.$NC"
    exit 1
}

# --- Create virtual environment if not exists ---
if (!(Test-Path ".venv")) {
    Write-Host "$BLUE Creating virtual environment...$NC"
    & $pythonCmd -m venv .venv
    Write-Host "$GREEN Virtual environment created.$NC"
}
else {
    Write-Host "$GREEN Virtual environment already exists.$NC"
}

# --- Activate virtual environment ---
Write-Host "$BLUE Activating virtual environment...$NC"
$venvPath = ".\.venv\Scripts\Activate.ps1"
if (!(Test-Path $venvPath)) {
    Write-Host "$RED Virtual environment activation script not found!$NC"
    exit 1
}
. $venvPath

# --- Install dependencies ---
if (Test-Path "requirements.txt") {
    Write-Host "$BLUE Installing dependencies from requirements.txt...$NC"
    pip install -r requirements.txt
}
else {
    Write-Host "$BLUE Installing default dependencies...$NC"
    pip install PyQt5 google-auth-oauthlib google-api-python-client google-generativeai pandas plotly python-dateutil
}

Write-Host "$GREEN All dependencies installed.$NC"

# --- Run the application ---
Write-Host "$BLUE Starting application...$NC"
& $pythonCmd main.py
