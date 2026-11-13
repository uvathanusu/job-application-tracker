@echo off
title Jobtrail - Job Application Tracker
echo ========================================================
echo        Jobtrail - Job Application Tracker
echo ========================================================
echo.

cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found in .\venv
    echo Please make sure Python and virtual environment are configured.
    pause
    exit /b 1
)

echo Starting backend server on http://127.0.0.1:5000 ...
echo Press Ctrl+C in this window to stop the server.
echo.

start "" http://127.0.0.1:5000

venv\Scripts\python.exe app.py

pause
