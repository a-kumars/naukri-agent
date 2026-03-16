@echo off
echo 🚀 Starting Naukri Agent Daily Scheduler
echo ========================================
echo This will run resume updates at 6:30 AM and 7:00 PM daily
echo Press Ctrl+C to stop
echo.
cd /d "%~dp0"
python daily_scheduler.py
pause