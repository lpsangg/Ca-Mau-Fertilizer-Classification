@echo off
cd /d "%~dp0"
echo ======================================================================
echo    KHOI CHAY MODERN AI DASHBOARD (PVCFC VISION - FASTAPI & WEBVIEW)
echo ======================================================================
if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe run_web_app.py
) else (
    python run_web_app.py
)
pause
