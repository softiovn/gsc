@echo off
title Search Console Desktop App
echo ============================================
echo    Starting Search Console Desktop App
echo ============================================
echo.

:: Check if PowerShell is available
where powershell >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] PowerShell not found on this system.
    pause
    exit /b 1
)

:: Run PowerShell setup and start script
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run.ps1"

echo.
echo ============================================
echo Application has exited.
echo ============================================
pause
