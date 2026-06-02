@echo off
echo ============================================================
echo   Whisper Transcriber - Inicio Rápido
echo ============================================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python no está instalado o no está en el PATH.
    echo 👉 Instala Python desde https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python detectado.
echo.

REM Crear entorno virtual si no existe
if not exist "venv" (
    echo 📦 Creando entorno virtual...
    python -m venv venv
    echo ✅ Entorno virtual creado.
) else (
    echo ✅ Entorno virtual ya existe.
)
echo.

REM Activar entorno virtual y ejecutar instalador
echo 🚀 Ejecutando instalador...
call venv\Scripts\activate.bat
python install.py

echo.
echo ============================================================
echo   ¡Listo! La aplicación está configurada.
echo ============================================================
echo.
echo Para iniciar la aplicación:
echo   1. Ejecuta: run_app.bat
echo   2. O usa el acceso directo si lo creaste.
echo.
echo 💡 La app se minimizará a la bandeja del sistema.
echo    Busca el icono 🎙️ cerca del reloj.
echo.
pause
