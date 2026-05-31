@echo off
REM Setup script for hablalo on Windows

echo.
echo ============================================================
echo Setting up hablalo - Speech to Text with whisper.cpp
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)

echo [1/3] Creating Python virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

echo [2/3] Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo [3/3] Downloading whisper.cpp...
echo.
echo Visit: https://github.com/ggml-org/whisper.cpp
echo Instructions:
echo   1. Clone or download whisper.cpp repository
echo   2. Follow the build instructions (requires gcc/MSVC)
echo   3. Place the compiled 'main.exe' in the project root
echo   4. Download models from: https://huggingface.co/ggerganov/whisper.cpp
echo   5. Create 'models' folder and place model file (e.g., ggml-base.bin)
echo.
echo For Windows, you can download pre-built binaries or use:
echo   - Visual Studio Build Tools or
echo   - mingw-w64 for compilation
echo.

echo ============================================================
echo Setup complete!
echo ============================================================
echo.
echo Next steps:
echo   1. Make sure whisper.cpp is compiled and 'main.exe' is in root
echo   2. Download a whisper model to 'models' folder
echo   3. Run: run.bat
echo.
pause
