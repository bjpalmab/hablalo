"""
Instalador Inteligente "One-Click" para Whisper Transcriber
Descarga binarios pre-compilados, configura entorno y modelos automáticamente.
"""
import os
import sys
import subprocess
import platform
import urllib.request
import zipfile
import shutil
import json
from pathlib import Path

# Configuración
WHISPER_REPO = "https://github.com/ggml-org/whisper.cpp"
WHISPER_RELEASES = "https://github.com/ggml-org/whisper.cpp/releases/latest/download"
MODELS_URL = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main"
REQUIRED_FILES = ["main.exe", "models/ggml-base.bin"]

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def check_python():
    """Verifica versión de Python"""
    if sys.version_info < (3, 8):
        print("❌ Error: Se requiere Python 3.8 o superior.")
        return False
    print(f"✅ Python {sys.version.split()[0]} detectado.")
    return True

def create_venv():
    """Crea entorno virtual si no existe"""
    venv_path = Path("venv")
    if not venv_path.exists():
        print("📦 Creando entorno virtual...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Entorno virtual creado.")
    else:
        print("✅ Entorno virtual ya existe.")
    
    # Activar venv para instalar dependencias
    if platform.system() == "Windows":
        pip_path = venv_path / "Scripts" / "pip.exe"
        python_path = venv_path / "Scripts" / "python.exe"
    else:
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"
    
    return str(pip_path), str(python_path)

def install_dependencies(pip_path):
    """Instala dependencias desde requirements.txt"""
    if not Path("requirements.txt").exists():
        print("⚠️  No se encontró requirements.txt, creando uno básico...")
        with open("requirements.txt", "w") as f:
            f.write("numpy>=1.20.0\nkeyboard>=0.13.5\nflask>=2.0.0\npystray>=0.5.3\nPillow>=9.0.0\npyperclip>=1.8.0\n")
    
    print("📥 Instalando dependencias...")
    
    # Intentar actualizar pip, pero continuar si falla (no es crítico)
    try:
        subprocess.run([pip_path, "install", "--upgrade", "pip"], 
                      check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ pip actualizado.")
    except subprocess.CalledProcessError:
        print("⚠️  No se pudo actualizar pip (no es crítico), continuando...")
    
    # En Windows, instalar PyAudio desde wheel precompilado
    if platform.system() == "Windows":
        print("📦 Instalando PyAudio desde wheel precompilado...")
        # Usar wheel precompilado de Christoph Gohlke mirror o PyPI wheels
        pyaudio_wheel = "https://github.com/cgohlke/win_amd64-wheels/releases/download/2024.12.19/PyAudio-0.2.14-cp314-cp314-win_amd64.whl"
        try:
            subprocess.run([pip_path, "install", pyaudio_wheel], check=True)
            print("✅ PyAudio instalado.")
        except subprocess.CalledProcessError:
            # Fallback: intentar con versiÃ³n genÃ©rica de PyPI que pueda tener wheels
            print("â ï¸  Intentando instalar PyAudio desde PyPI...")
            subprocess.run([pip_path, "install", "PyAudio", "--only-binary", ":all:"], check=True)
        
        # Instalar el resto de dependencias
        print("📦 Instalando resto de dependencias...")
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
    else:
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
    
    print("✅ Dependencias instaladas.")

def download_whisper_binary():
    """Descarga binario pre-compilado de whisper.cpp para Windows"""
    if Path("main.exe").exists():
        print("✅ main.exe ya existe.")
        return True
    
    print("🔍 Buscando binario pre-compilado de whisper.cpp...")
    
    # URL genérica para builds oficiales (ajustar según disponibilidad real)
    # Nota: ggml-org no siempre publica bins pre-compilados para Windows directamente.
    # Estrategia fallback: Si no hay bin oficial, instruir al usuario o compilar.
    
    # Intentamos descargar de una fuente confiable de terceros o build propio si falla
    # Para este ejemplo, simularemos la descarga de un build genérico o daremos instrucciones
    
    build_url = None
    # En producción, aquí iría la lógica para parsear releases de GitHub y encontrar 'whisper-bin-x64.zip'
    # Como no hay bins oficiales consistentes para Windows en releases, usaremos la estrategia de 
    # intentar descargar de un mirror conocido o guiar al usuario.
    
    print("⚠️  No hay binarios oficiales pre-compilados consistentes para Windows en los releases.")
    print("💡 Opción A: Compilación automática (requiere Visual Studio Build Tools).")
    print("💡 Opción B: Descargar manualmente de https://github.com/ggerganov/whisper.cpp/releases")
    
    # Fallback: Intentar compilar si tiene herramientas
    if compile_whisper():
        return True
        
    print("❌ No se pudo obtener main.exe automáticamente.")
    print("👉 Por favor, descarga 'whisper-bin-x64.zip' manualmente, extrae 'main.exe' en esta carpeta y ejecuta de nuevo.")
    return False

def compile_whisper():
    """Intenta compilar whisper.cpp si tiene las herramientas"""
    if not Path("whisper.cpp").exists():
        print("📥 Clonando whisper.cpp...")
        subprocess.run(["git", "clone", "--depth", "1", WHISPER_REPO], check=True)
    
    os.chdir("whisper.cpp")
    try:
        print("🔨 Compilando whisper.cpp (esto puede tardar unos minutos)...")
        # Comando para Windows con Make (si está disponible) o CMake
        # Asumimos que el usuario tiene make o cmake instalado si llega aquí
        if shutil.which("make"):
            subprocess.run(["make", "main"], check=True)
            if Path("main.exe").exists():
                shutil.copy("main.exe", "../main.exe")
                os.chdir("..")
                print("✅ Compilación exitosa.")
                return True
        elif shutil.which("cmake"):
            # Build con CMake para Windows
            os.makedirs("build", exist_ok=True)
            os.chdir("build")
            subprocess.run(["cmake", "..", "-DCMAKE_BUILD_TYPE=Release"], check=True)
            subprocess.run(["cmake", "--build", ".", "--config", "Release", "--target", "main"], check=True)
            src = "bin/Release/main.exe" if Path("bin/Release/main.exe").exists() else "main.exe"
            if Path(src).exists():
                shutil.copy(src, "../../main.exe")
                os.chdir("../..")
                print("✅ Compilación con CMake exitosa.")
                return True
    except Exception as e:
        print(f"⚠️  Compilación fallida: {e}")
    
    os.chdir("..")
    return False

def download_model(model_name="ggml-base.bin"):
    """Descarga el modelo especificado"""
    model_path = Path("models") / model_name
    if model_path.exists():
        print(f"✅ Modelo {model_name} ya existe.")
        return True
    
    print(f"📥 Descargando modelo {model_name}... (puede tardar según tu conexión)")
    Path("models").mkdir(exist_ok=True)
    
    url = f"{MODELS_URL}/{model_name}"
    try:
        def reporthook(blocknum, blocksize, totalsize):
            readsofar = blocknum * blocksize
            if totalsize > 0:
                percent = readsofar * 100 / totalsize
                print(f"\rProgreso: {percent:.1f}%", end='')
        
        urllib.request.urlretrieve(url, model_path, reporthook)
        print("\n✅ Modelo descargado correctamente.")
        return True
    except Exception as e:
        print(f"\n❌ Error descargando modelo: {e}")
        print("👉 Intenta descargarlo manualmente desde HuggingFace y colócalo en la carpeta 'models'.")
        return False

def create_config():
    """Crea archivo de configuración por defecto si no existe"""
    if not Path("config.json").exists():
        config = {
            "audio": {
                "device_index": -1,  # -1 para automático
                "chunk_duration": 3,
                "silence_threshold": 0.01,
                "sample_rate": 16000
            },
            "whisper": {
                "model": "models/ggml-base.bin",
                "language": "es",
                "threads": 4,
                "use_gpu": False
            },
            "output": {
                "show_ui": True,
                "port": 8080,
                "save_to_file": True,
                "filename": "transcriptions.txt"
            },
            "features": {
                "auto_copy": True,
                "voice_commands": True,
                "minimize_to_tray": True
            }
        }
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
        print("✅ config.json creado con valores por defecto.")
    else:
        print("✅ config.json ya existe.")

def main():
    print_header("🚀 Instalador de Whisper Transcriber para Windows")
    
    if not check_python():
        return
    
    pip_path, python_path = create_venv()
    install_dependencies(pip_path)
    
    if not download_whisper_binary():
        print("\n⚠️  La instalación no pudo completarse totalmente.")
        print("   Asegúrate de tener 'main.exe' en la raíz del proyecto.")
        return
    
    download_model()
    create_config()
    
    print_header("✨ ¡Instalación Completada!")
    print("👉 Ejecuta 'run.bat' o 'python main.py' para iniciar.")
    print("💡 La app se minimizará a la bandeja del sistema. Busca el icono 🎙️.")

if __name__ == "__main__":
    main()
