@echo off
REM Launcher for hablalo - Speech-to-Text App
REM This script checks prerequisites and runs the application

echo ============================================================
echo   hablalo - Real-time Speech-to-Text
echo ============================================================
echo.

REM Check if whisper.cpp is already installed
if not exist "main.exe" (
    echo [INSTALADOR] Ejecutando instalador por primera vez...
    echo.
    powershell -ExecutionPolicy Bypass -File "%~dp0installer.ps1"
    if errorlevel 1 (
        echo.
        echo ERROR: La instalacion fallo. Revisa los mensajes arriba.
        pause
        exit /b 1
    )
    echo.
) else (
    echo [INFO] whisper.cpp ya esta instalado.
    echo.
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo Installing dependencies...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Starting application...
echo ============================================================
echo.
echo Hotkeys:
echo   Q - Quit
echo   S - Pause/Resume recording
echo   D - Change audio device
echo.

REM Run the launcher which will check everything and start the app
python launcher.py %*

pause
