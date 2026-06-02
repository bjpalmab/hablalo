@echo off
echo ============================================================
echo   Whisper Transcriber - Iniciando...
echo ============================================================
echo.

REM Verificar entorno virtual
if not exist "venv" (
    echo ❌ Error: El entorno virtual no existe.
    echo 👉 Ejecuta primero: setup.bat
    pause
    exit /b 1
)

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Verificar prerequisitos básicos
if not exist "main.exe" (
    echo ⚠️  Advertencia: main.exe no encontrado.
    echo    La aplicación puede no funcionar correctamente.
    echo    Ejecuta setup.bat para intentar descargarlo/compilarlo.
    echo.
)

if not exist "models" (
    echo ⚠️  Advertencia: La carpeta models no existe.
    echo    Ejecuta setup.bat para descargar el modelo.
    echo.
)

REM Iniciar aplicación
echo 🎙️  Iniciando Whisper Transcriber...
echo 💡 La app se minimizará a la bandeja del sistema.
echo    Busca el icono 🎙️ cerca del reloj.
echo.
echo 🌐 Interfaz web: http://localhost:8080
echo.

python main.py

pause
