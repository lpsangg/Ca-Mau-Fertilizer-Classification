@echo off
cd /d "%~dp0"
echo ======================================================================
echo    KHOI CHAY HE THONG PHAN LOAI & DEM BAO PHAN BON CA MAU
echo ======================================================================
if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe run_app.py
) else (
    python run_app.py
)
pause
