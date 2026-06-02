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

echo [1/4] Creating Python virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

echo [2/4] Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo [3/4] Downloading whisper.cpp...
echo.
if not exist "whisper.cpp" (
    echo Cloning whisper.cpp repository...
    git clone https://github.com/ggml-org/whisper.cpp.git
) else (
    echo whisper.cpp already exists, skipping clone
)

echo [4/4] Compiling whisper.cpp for Windows...
echo.
echo IMPORTANT: For Windows, you need one of these options:
echo   Option A: Visual Studio Build Tools with C++ support
echo   Option B: MSYS2 with mingw-w64 toolchain
echo   Option C: Download pre-built binaries from releases
echo.
echo If you have Visual Studio:
echo   cd whisper.cpp
echo   mkdir build
echo   cd build
echo   cmake ..
echo   cmake --build . --config Release
echo   copy Release\main.exe ..\..\main.exe
echo.
echo Or download pre-built binary from:
echo https://github.com/ggml-org/whisper.cpp/releases
echo and place main.exe in the project root
echo.

echo Next step: Download a whisper model
echo Visit: https://huggingface.co/ggerganov/whisper.cpp/tree/main
echo Recommended models:
echo   - ggml-tiny.bin (75MB) - Fastest, less accurate
echo   - ggml-base.bin (150MB) - Good balance
echo   - ggml-small.bin (500MB) - Better accuracy
echo.
echo Create 'models' folder and place the .bin file there:
echo   mkdir models
echo   move ggml-base.bin models\
echo.

echo ============================================================
echo Setup complete!
echo ============================================================
echo.
echo Final checklist:
echo   [ ] whisper.cpp compiled OR main.exe in project root
echo   [ ] Model file (.bin) in 'models' folder
echo   [ ] Run: run.bat
echo.
pause
