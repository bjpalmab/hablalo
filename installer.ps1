# Whisper Voice-to-Text Installer for Windows
# Detecta hardware, descarga binarios pre-compilados (CPU) o compila para GPU

param(
    [switch]$Help,
    [string]$Model = "base",
    [string]$Language = "es",
    [switch]$NoGPU,
    [switch]$ForceReinstall
)

$ErrorActionPreference = "Stop"
$INSTALL_DIR = $PSScriptRoot
$WHISPER_REPO = "https://github.com/ggml-org/whisper.cpp.git"
$WHISPER_DIR = Join-Path $INSTALL_DIR "whisper.cpp"
$MODELS_DIR = Join-Path $INSTALL_DIR "models"
$EXECUTABLE = Join-Path $INSTALL_DIR "main.exe"
$PYTHON_VENV = Join-Path $INSTALL_DIR "venv"

# Colores para output
function Write-Color {
    param([string]$Text, [string]$Color = "White")
    Write-Host $Text -ForegroundColor $Color
}

function Show-Help {
    Write-Color @"
===========================================
  Whisper Voice-to-Text Installer (Windows)
===========================================

Uso: .\installer.ps1 [opciones]

Opciones:
  -Model <nombre>     Modelo a descargar: tiny, base, small, medium, large-v3 (default: base)
  -Language <codigo>  Idioma: es, en, fr, de, etc. (default: es)
  -NoGPU              Forzar uso de CPU incluso si hay GPU NVIDIA
  -ForceReinstall     Reinstalar todo desde cero
  -Help               Mostrar esta ayuda

Ejemplos:
  .\installer.ps1
  .\installer.ps1 -Model small -Language en
  .\installer.ps1 -NoGPU -Model base

"@ -ForegroundColor Cyan
    exit 0
}

if ($Help) { Show-Help }

Write-Color "`n========================================" "Cyan"
Write-Color "  Instalador Inteligente Whisper.cpp  " "Cyan"
Write-Color "========================================`n" "Cyan"

# 1. Verificar Python
Write-Color "[1/6] Verificando Python..." "Yellow"
try {
    $pythonVersion = python --version 2>&1
    Write-Color "  ✓ Python encontrado: $pythonVersion" "Green"
} catch {
    Write-Color "  ✗ ERROR: Python no está instalado o no está en PATH" "Red"
    Write-Color "  Instala Python 3.8+ desde https://python.org" "Red"
    Write-Color "  ¡Marca 'Add Python to PATH' durante la instalación!" "Red"
    exit 1
}

# 2. Verificar Git
Write-Color "`n[2/6] Verificando Git..." "Yellow"
try {
    $gitVersion = git --version 2>&1
    Write-Color "  ✓ Git encontrado: $gitVersion" "Green"
} catch {
    Write-Color "  ✗ ERROR: Git no está instalado" "Red"
    Write-Color "  Instala Git desde https://git-scm.com/download/win" "Red"
    exit 1
}

# 3. Detectar Hardware (GPU NVIDIA)
$hasNvidiaGPU = $false
$cudaInstalled = $false

if (-not $NoGPU) {
    Write-Color "`n[3/6] Detectando hardware..." "Yellow"
    
    # Verificar GPU NVIDIA
    try {
        $gpuInfo = Get-WmiObject Win32_VideoController | Where-Object { $_.Name -match "NVIDIA|Tesla|Quadro|GeForce|RTX|GTX" }
        if ($gpuInfo) {
            $hasNvidiaGPU = $true
            Write-Color "  ✓ GPU NVIDIA detectada: $($gpuInfo.Name)" "Green"
            
            # Verificar CUDA Toolkit
            $cudaPaths = @(
                "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA",
                "C:\CUDA",
                "$env:CUDA_PATH"
            )
            foreach ($path in $cudaPaths) {
                if ($path -and (Test-Path $path)) {
                    $cudaInstalled = $true
                    $cudaVersion = Split-Path $path -Leaf
                    Write-Color "  ✓ CUDA Toolkit encontrado: $cudaVersion" "Green"
                    break
                }
            }
            
            if (-not $cudaInstalled) {
                Write-Color "  ⚠ CUDA Toolkit NO encontrado" "Yellow"
                Write-Color "    Para usar GPU, instala CUDA Toolkit desde:" "Yellow"
                Write-Color "    https://developer.nvidia.com/cuda-downloads" "Yellow"
            }
        } else {
            Write-Color "  ℹ No se detectó GPU NVIDIA" "Gray"
        }
    } catch {
        Write-Color "  ⚠ No se pudo detectar GPU: $_" "Yellow"
    }
} else {
    Write-Color "`n[3/6] Modo CPU forzado por usuario" "Yellow"
}

$useGPU = ($hasNvidiaGPU -and $cudaInstalled)

if ($useGPU) {
    Write-Color "  → Se usará aceleración GPU (CUDA)" "Green"
} else {
    Write-Color "  → Se usará versión CPU (pre-compilada)" "Green"
}

# 4. Clonar/Actualizar whisper.cpp
Write-Color "`n[4/6] Preparando whisper.cpp..." "Yellow"

if ((Test-Path $WHISPER_DIR) -and -not $ForceReinstall) {
    Write-Color "  ✓ whisper.cpp ya existe, actualizando..." "Green"
    Set-Location $WHISPER_DIR
    git pull --quiet 2>&1 | Out-Null
    Set-Location $INSTALL_DIR
} else {
    if (Test-Path $WHISPER_DIR) {
        Write-Color "  Eliminando instalación anterior..." "Gray"
        Remove-Item -Recurse -Force $WHISPER_DIR
    }
    Write-Color "  Clonando whisper.cpp..." "Gray"
    git clone --depth 1 $WHISPER_REPO $WHISPER_DIR --quiet 2>&1
    Write-Color "  ✓ whisper.cpp clonado exitosamente" "Green"
}

# 5. Obtener binario (descargar o compilar)
Write-Color "`n[5/6] Obteniendo binario de whisper.cpp..." "Yellow"

if ($useGPU) {
    # Compilar con soporte CUDA
    Write-Color "  Compilando con soporte GPU (esto puede tomar 5-10 minutos)..." "Gray"
    
    # Verificar Visual Studio Build Tools
    $vsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
    if (-not (Test-Path $vsWhere)) {
        Write-Color "  ✗ ERROR: Visual Studio Build Tools no encontrado" "Red"
        Write-Color "    Para compilar con GPU, necesitas:" "Red"
        Write-Color "    1. Instalar Visual Studio Build Tools" "Red"
        Write-Color "       https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022" "Red"
        Write-Color "    2. Durante instalación, marca 'Desarrollo para el escritorio con C++'" "Red"
        Write-Color "    3. Reinicia y ejecuta este instalador nuevamente" "Red"
        Write-Color "`n  Alternativa: Ejecuta con -NoGPU para usar versión CPU pre-compilada" "Yellow"
        exit 1
    }
    
    # Configurar entorno de compilación
    $vsPath = & $vsWhere -latest -products * -requires Microsoft.Component.MSBuild -find MSBuild\**\Bin\MSBuild.exe
    $vcVarsAll = (Split-Path (Split-Path $vsPath -Parent) -Parent) + "\VC\Auxiliary\Build\vcvarsall.bat"
    
    if (Test-Path $vcVarsAll) {
        Write-Color "  Configurando entorno de compilación..." "Gray"
        cmd /c "`"$vcVarsAll`" x64 && cd /d `"$WHISPER_DIR`" && cmake -B build -DGGML_CUDA=ON && cmake --build build --config Release"
        
        if ($LASTEXITCODE -eq 0) {
            $builtExe = Join-Path $WHISPER_DIR "build\bin\Release\main.exe"
            if (Test-Path $builtExe) {
                Copy-Item $builtExe $EXECUTABLE -Force
                Write-Color "  ✓ Binario compilado con éxito (GPU habilitada)" "Green"
            } else {
                Write-Color "  ✗ ERROR: No se encontró main.exe después de compilar" "Red"
                exit 1
            }
        } else {
            Write-Color "  ✗ ERROR: Falló la compilación" "Red"
            Write-Color "    Verifica que CUDA Toolkit y VS Build Tools estén correctamente instalados" "Red"
            exit 1
        }
    } else {
        Write-Color "  ✗ ERROR: No se encontró vcvarsall.bat" "Red"
        exit 1
    }
} else {
    # Descargar binario pre-compilado para CPU
    Write-Color "  Descargando binario pre-compilado para CPU..." "Gray"
    
    $releaseUrl = "https://github.com/ggml-org/whisper.cpp/releases/latest/download/whisper-bin-x64.zip"
    $tempZip = Join-Path $env:TEMP "whisper-bin-x64.zip"
    
    try {
        Invoke-WebRequest -Uri $releaseUrl -OutFile $tempZip -UseBasicParsing
        
        # Extraer solo main.exe
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        $zip = [System.IO.Compression.ZipFile]::OpenRead($tempZip)
        $mainExe = $zip.Entries | Where-Object { $_.Name -eq "main.exe" }
        
        if ($mainExe) {
            [System.IO.Compression.ZipFileExtensions]::ExtractToFile($mainExe, $EXECUTABLE, $true)
            Write-Color "  ✓ Binario descargado exitosamente" "Green"
        } else {
            Write-Color "  ✗ ERROR: No se encontró main.exe en el zip" "Red"
            Remove-Item $tempZip -Force
            exit 1
        }
        
        $zip.Dispose()
        Remove-Item $tempZip -Force
    } catch {
        Write-Color "  ✗ ERROR al descargar binario: $_" "Red"
        Write-Color "    Intenta descargar manualmente desde:" "Yellow"
        Write-Color "    https://github.com/ggml-org/whisper.cpp/releases" "Yellow"
        exit 1
    }
}

# Verificar que el ejecutable funcione
Write-Color "  Verificando ejecutable..." "Gray"
try {
    $testOutput = & $EXECUTABLE --help 2>&1 | Select-Object -First 1
    if ($testOutput -match "usage") {
        Write-Color "  ✓ Ejecutable verificado correctamente" "Green"
    } else {
        throw "Output inesperado"
    }
} catch {
    Write-Color "  ✗ ERROR: El ejecutable no funciona correctamente" "Red"
    exit 1
}

# 6. Configurar Python y dependencias
Write-Color "`n[6/6] Configurando entorno Python..." "Yellow"

if ((Test-Path $PYTHON_VENV) -and -not $ForceReinstall) {
    Write-Color "  ✓ Entorno virtual ya existe" "Green"
} else {
    if (Test-Path $PYTHON_VENV) {
        Remove-Item -Recurse -Force $PYTHON_VENV
    }
    Write-Color "  Creando entorno virtual..." "Gray"
    python -m venv $PYTHON_VENV
}

# Activar e instalar dependencias
Write-Color "  Instalando dependencias..." "Gray"
& "$PYTHON_VENV\Scripts\Activate.ps1"
pip install --upgrade pip --quiet
pip install -r (Join-Path $INSTALL_DIR "requirements.txt") --quiet
Write-Color "  ✓ Dependencias instaladas" "Green"

# 7. Descargar modelo
Write-Color "`n[7/7] Descargando modelo '$Model'..." "Yellow"

if (-not (Test-Path $MODELS_DIR)) {
    New-Item -ItemType Directory -Path $MODELS_DIR | Out-Null
}

$modelFile = "ggml-$Model.bin"
$modelPath = Join-Path $MODELS_DIR $modelFile

if ((Test-Path $modelPath) -and -not $ForceReinstall) {
    Write-Color "  ✓ Modelo ya descargado" "Green"
} else {
    $modelUrl = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/$modelFile"
    
    # Usar ProgressAction para mostrar progreso en PowerShell 7+
    if ($PSVersionTable.PSVersion.Major -ge 7) {
        Invoke-WebRequest -Uri $modelUrl -OutFile $modelPath -ProgressAction SilentlyContinue
    } else {
        Invoke-WebRequest -Uri $modelUrl -OutFile $modelPath
    }
    
    if (Test-Path $modelPath) {
        $sizeMB = [math]::Round((Get-Item $modelPath).Length / 1MB, 2)
        Write-Color "  ✓ Modelo descargado ($sizeMB MB)" "Green"
    } else {
        Write-Color "  ✗ ERROR: Falló la descarga del modelo" "Red"
        exit 1
    }
}

# Crear/Actualizar config.json
Write-Color "`n  Configurando aplicación..." "Gray"
$configPath = Join-Path $INSTALL_DIR "config.json"

if (-not (Test-Path $configPath)) {
    $config = @{
        audio = @{
            sample_rate = 16000
            channels = 1
            chunk_duration = 3
            silence_threshold = 0.01
            device_index = -1
        }
        whisper = @{
            executable = ".\main.exe"
            model = ".\models\ggml-$Model.bin"
            language = $Language
            threads = [Environment]::ProcessorCount
            max_context = -1
            max_len = 0
            best_of = 1
            beam_size = -1
            patience = -1
            suppress_blank = $true
            suppress_tokens = @(-1)
            temperature = 0.0
            initial_prompt = ""
            print_special = $false
            print_progress = $true
            print_realtime = $true
            print_timestamps = $false
        }
        output = @{
            file = "transcriptions.txt"
            save_audio_chunks = $false
            show_visualizer = $true
        }
        performance = @{
            use_gpu = $useGPU
            n_threads = [Environment]::ProcessorCount
        }
        logging = @{
            level = "INFO"
            file = "whisper.log"
        }
    }
    
    $config | ConvertTo-Json -Depth 10 | Set-Content $configPath -Encoding UTF8
    Write-Color "  ✓ config.json creado" "Green"
} else {
    # Actualizar configuración existente
    $existingConfig = Get-Content $configPath | ConvertFrom-Json
    $existingConfig.whisper.model = ".\models\ggml-$Model.bin"
    $existingConfig.whisper.language = $Language
    $existingConfig.performance.use_gpu = $useGPU
    $existingConfig | ConvertTo-Json -Depth 10 | Set-Content $configPath -Encoding UTF8
    Write-Color "  ✓ config.json actualizado" "Green"
}

# Resumen final
Write-Color "`n========================================" "Cyan"
Write-Color "  ¡INSTALACIÓN COMPLETADA CON ÉXITO!   " "Green"
Write-Color "========================================" "Cyan"
Write-Color "`nConfiguración:" "White"
Write-Color "  • Modelo: $Model ($($useGPU ? 'GPU' : 'CPU'))" "Gray"
Write-Color "  • Idioma: $Language" "Gray"
Write-Color "  • Hilos: $([Environment]::ProcessorCount)" "Gray"
Write-Color "`nPara ejecutar la aplicación:" "White"
Write-Color "  .\run.bat" "Cyan"
Write-Color "`nO directamente:" "White"
Write-Color "  .\venv\Scripts\Activate.ps1" "Gray"
Write-Color "  python launcher.py --language $Language" "Gray"
Write-Color "`nPara cambiar configuración, edita:" "White"
Write-Color "  config.json" "Gray"
Write-Color "`n" "White"
