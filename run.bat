@echo off
cd /d "%~dp0"
echo ======================================================================
echo    KHOI CHAY HE THONG PHAN LOAI VA DEM BAO PHAN BON CA MAU (WEB UI)
echo ======================================================================
if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe main.py
) else (
    python main.py
)
pause
