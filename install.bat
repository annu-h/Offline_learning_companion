@echo off
setlocal

echo ====================================================
echo  Lumi - Offline Learning Companion Environment Setup
echo ====================================================

:: Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python was not found in your PATH.
    echo Please install Python 3.10+ and make sure it is added to PATH.
    pause
    exit /b 1
)

:: Create virtual environment if it does not already exist
if not exist ".venv" (
    echo [INFO] Creating Python virtual environment in .venv...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo [INFO] Virtual environment .venv already exists.
)

:: Activate the virtual environment
echo [INFO] Activating virtual environment...
call .venv\Scripts\activate.bat

:: Upgrade pip and install dependencies
echo [INFO] Installing required offline dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo ====================================================
    echo [SUCCESS] Lumi environment setup completed!
    echo To run Lumi with GUI:
    echo   run.bat
    echo or
    echo   .venv\Scripts\python.exe -m Python.main
    echo ====================================================
) else (
    echo [ERROR] Dependency installation encountered errors.
)

pause
