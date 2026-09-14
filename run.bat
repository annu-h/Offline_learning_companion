@echo off
setlocal

echo ====================================================
echo  Starting Lumi - Offline Learning Companion...
echo ====================================================

if exist ".venv\Scripts\python.exe" (
    call .venv\Scripts\activate.bat
    python -m Python.main
) else (
    python -m Python.main
)

pause
