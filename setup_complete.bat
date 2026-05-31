@echo off
setlocal EnableDelayedExpansion

echo ============================================================
echo   SETUP COMPLETO - Whisper Voice-to-Text para Windows
echo ============================================================
echo.
echo Este script instalara TODO lo necesario automaticamente:
echo  1. Clonara whisper.cpp
echo  2. Instalara dependencias de Python
echo  3. Compilara whisper.cpp
echo  4. Descargara el modelo base
echo  5. Dejara la app lista para usar
echo.
echo NOTA: Requiere tener instalado:
echo  - Python 3.8+ 
echo  - Git
echo  - Visual Studio Build Tools o Visual Studio con C++
echo  - CMake (se intentara instalar si falta)
echo.
pause

:: Verificar Python
echo [1/6] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no encontrado. Instale Python 3.8+ desde https://python.org
    echo Asegurese de marcar "Add Python to PATH" durante la instalacion.
    pause
    exit /b 1
)
echo OK: Python encontrado

:: Verificar Git
echo [2/6] Verificando Git...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Git no encontrado. Instale Git desde https://git-scm.com
    pause
    exit /b 1
)
echo OK: Git encontrado

:: Crear entorno virtual
echo [3/6] Creando entorno virtual de Python...
if not exist venv (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: No se pudo crear el entorno virtual
        pause
        exit /b 1
    )
    echo OK: Entorno virtual creado
) else (
    echo OK: Entorno virtual ya existe
)

:: Activar entorno e instalar dependencias
echo [4/6] Instalando dependencias de Python...
call venv\Scripts\activate.bat
pip install --upgrade pip >nul
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: No se pudieron instalar las dependencias
    pause
    exit /b 1
)
echo OK: Dependencias instaladas

:: Clonar whisper.cpp
echo [5/6] Clonando whisper.cpp...
if not exist whisper.cpp (
    git clone https://github.com/ggml-org/whisper.cpp.git
    if %errorlevel% neq 0 (
        echo ERROR: No se pudo clonar whisper.cpp
        pause
        exit /b 1
    )
    echo OK: whisper.cpp clonado
) else (
    echo OK: whisper.cpp ya existe, actualizando...
    cd whisper.cpp
    git pull
    cd ..
)

:: Verificar/Instalar CMake
echo [5.5/6] Verificando CMake...
where cmake >nul 2>&1
if %errorlevel% neq 0 (
    echo CMake no encontrado. Intentando instalar...
    pip install cmake
    if %errorlevel% neq 0 (
        echo ERROR: No se pudo instalar CMake. Instalelo manualmente desde https://cmake.org
        pause
        exit /b 1
    )
    echo OK: CMake instalado via pip
) else (
    echo OK: CMake encontrado
)

:: Compilar whisper.cpp
echo [5.6/6] Compilando whisper.cpp...
cd whisper.cpp
if exist build rmdir /s /q build
mkdir build
cd build

:: Configurar con CMake
cmake .. -DCMAKE_BUILD_TYPE=Release
if %errorlevel% neq 0 (
    echo ERROR: Fallo la configuracion de CMake
    echo.
    echo IMPORTANTE: Necesita Visual Studio Build Tools con soporte para C++
    echo Descarguelo gratis: https://visualstudio.microsoft.com/downloads/
    echo Instale: "Desktop development with C++"
    echo.
    cd ../..
    pause
    exit /b 1
)

:: Compilar
cmake --build . --config Release
if %errorlevel% neq 0 (
    echo ERROR: Fallo la compilacion
    echo.
    echo Asegurese de tener Visual Studio Build Tools instalado
    echo.
    cd ../..
    pause
    exit /b 1
)

:: Copiar ejecutable a la raiz
if exist Release\main.exe (
    copy Release\main.exe ..\..\main.exe >nul
    echo OK: main.exe compilado y copiado
) else if exist main.exe (
    copy main.exe ..\..\main.exe >nul
    echo OK: main.exe copiado
) else (
    echo ADVERTENCIA: No se encontro main.exe en la ubicacion esperada
    echo Buscando en todo el directorio build...
    for /r %%f in (main.exe) do (
        copy "%%f" ..\..\main.exe >nul
        echo OK: main.exe encontrado y copiado desde %%f
        goto :found
    )
    :found
    if not exist ..\..\main.exe (
        echo ERROR: No se pudo encontrar main.exe compilado
        cd ../..
        pause
        exit /b 1
    )
)

cd ../..

:: Crear carpeta de modelos
echo [6/6] Preparando carpeta de modelos...
if not exist models mkdir models

:: Descargar modelo usando el launcher
echo Descargando modelo 'base' (recomendado para empezar)...
call venv\Scripts\activate.bat
python launcher.py --download-model base
if %errorlevel% neq 0 (
    echo ADVERTENCIA: No se pudo descargar el modelo automaticamente
    echo Puede descargarlo manualmente con: python launcher.py --download-model base
    echo O ejecutar la app y seguira las instrucciones
) else (
    echo OK: Modelo descargado
)

echo.
echo ============================================================
echo   ¡INSTALACION COMPLETADA EXITOSAMENTE!
echo ============================================================
echo.
echo La app esta lista para usar. Para iniciar:
echo.
echo   run.bat
echo.
echo O directamente:
echo.
echo   venv\Scripts\activate
echo   python launcher.py
echo.
echo Primeras veces puede tardar unos segundos en cargar.
echo.
echo Para cambiar configuracion, edite: config.json
echo.
pause
