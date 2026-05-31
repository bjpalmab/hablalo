# 🎙️ Hablalo - Real-time Speech to Text

Aplicación Windows para transcribir voz a texto en tiempo real usando **whisper.cpp**. 100% funcional, basado en código Python sin UI compleja.

## 🚀 Inicio Rápido (Primera Vez)

### Setup Automático con Instalador Inteligente

**¡Solo necesitas ejecutar UN comando!** El instalador detecta tu hardware, descarga binarios pre-compilados (CPU) o compila para GPU automáticamente.

```bash
run.bat
```

**¿Qué hace el instalador automáticamente?**
- ✅ Verifica Python y Git
- ✅ Detecta si tienes GPU NVIDIA y CUDA Toolkit
- ✅ Clona whisper.cpp desde GitHub
- ✅ **CPU:** Descarga binario pre-compilado oficial (¡listo en segundos!)
- ✅ **GPU:** Compila con soporte CUDA si tienes GPU + CUDA Toolkit + VS Build Tools
- ✅ Instala dependencias de Python
- ✅ Descarga el modelo de IA recomendado
- ✅ Crea configuración óptima para tu hardware

**Requisitos previos mínimos:**
1. **Python 3.8+** ([Descargar](https://www.python.org/downloads/)) - Marcar "Add to PATH"
2. **Git** ([Descargar](https://git-scm.com/))

**Opcional para GPU NVIDIA:**
- **Visual Studio Build Tools** (GRATIS): [Descargar aquí](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022)
  - Seleccionar: **"Desktop development with C++"**
- **CUDA Toolkit**: [Descargar aquí](https://developer.nvidia.com/cuda-downloads)

⏱️ **Tiempo:** 
- CPU: 2-3 minutos (descarga binario pre-compilado)
- GPU: 5-10 minutos (compilación local)

Después del setup inicial, solo ejecuta:
```bash
run.bat
```

### Uso del Instalador con Opciones

Puedes ejecutar el instalador directamente con opciones personalizadas:

```powershell
# Instalación básica (detecta hardware automáticamente)
.\installer.ps1

# Especificar modelo y lenguaje
.\installer.ps1 -Model small -Language en

# Forzar modo CPU (aunque tengas GPU)
.\installer.ps1 -NoGPU

# Reinstalar todo desde cero
.\installer.ps1 -ForceReinstall

# Ver ayuda completa
.\installer.ps1 -Help
```

**Modelos disponibles:**
| Modelo | Tamaño | Velocidad | Precisión | Uso Recomendado |
|--------|--------|-----------|-----------|-----------------|
| `tiny` | ~75MB | ⚡⚡⚡ Muy rápido | ⭐ Básica | Pruebas, hardware limitado |
| `base` | ~150MB | ⚡⚡ Rápido | ⭐⭐ Buena | **Recomendado para inicio** |
| `small` | ~500MB | ⚡ Medio | ⭐⭐⭐ Muy buena | Producción, buena CPU/GPU |
| `medium` | ~1.5GB | 🐢 Lento | ⭐⭐⭐⭐ Excelente | Máxima precisión, GPU recomendada |
| `large-v3` | ~3GB | 🐌🐌 Muy lento | ⭐⭐⭐⭐⭐ Best | Máxima calidad, GPU requerida |

### Opción 2: Setup Manual Paso a Paso

Si prefieres hacerlo manualmente o tienes problemas con el instalador automático:

#### A. Clonar repositorio e instalar dependencias Python

```bash
git clone https://github.com/bjpalmab/hablalo.git
cd hablalo
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

#### B. Obtener whisper.cpp

**Opción A: Descargar pre-compilado (CPU - Más fácil)**

1. Ve a [releases de whisper.cpp](https://github.com/ggml-org/whisper.cpp/releases)
2. Descarga `whisper-bin-x64.zip` (última versión)
3. Extrae `main.exe` y colócalo en la raíz del proyecto

**Opción B: Compilar con soporte GPU (NVIDIA CUDA)**

1. Instalar Visual Studio Build Tools y CUDA Toolkit (ver requisitos arriba)
2. Clonar whisper.cpp:
```bash
git clone https://github.com/ggml-org/whisper.cpp.git
cd whisper.cpp
```

3. Compilar con CUDA:
```bash
mkdir build
cd build
cmake .. -DGGML_CUDA=ON
cmake --build . --config Release
```

4. Copiar `main.exe`:
```bash
copy Release\main.exe ..\..\main.exe
```

#### C. Descargar modelo

1. Descarga un modelo desde [Hugging Face](https://huggingface.co/ggerganov/whisper.cpp/tree/main):
   - `ggml-tiny.bin` (~75MB) - Más rápido, menos preciso
   - `ggml-base.bin` (~150MB) - Buen balance ⭐ RECOMENDADO
   - `ggml-small.bin` (~500MB) - Mejor precisión

2. Crea carpeta y coloca el modelo:
```bash
mkdir models
# Coloca el archivo .bin descargado aquí
```

O usa el launcher para descargar automáticamente:
```bash
python launcher.py --download-model base
```

## 📖 Uso

```bash
run.bat
```

O directamente desde PowerShell:
```powershell
.\venv\Scripts\Activate.ps1
python launcher.py
```

### Comandos Útiles del Launcher

```bash
# Listar dispositivos de audio
python launcher.py --list-devices

# Ejecutar con idioma específico
python launcher.py --language es

# Cambiar dispositivo de audio
python launcher.py --device 1

# Descargar modelo específico
python launcher.py --download-model small

# Usar modelo diferente
python launcher.py --model tiny

# Verificar prerequisitos
python launcher.py --check
```

### Ejemplo de Salida

```
============================================================
🎙️  Real-time Speech-to-Text with whisper.cpp
============================================================
Sample rate: 16000 Hz
Chunk duration: 3 seconds
Whisper model: ./models/ggml-base.bin
Whisper executable: ./main.exe
============================================================

🔊 Available audio devices:
   → [0] Microphone (Realtek Audio)
   [1] Stereo Mix (Realtek Audio)

🎙️  Press Ctrl+C to stop recording and exit
Starting continuous recording...

[████████░░░░] 42% | Recording chunk 1...
✓ Audio chunk recorded (3s)
🔄 Transcribing...

✨ Transcription #1:
   Hola, esta es una prueba del sistema de voz a texto

[████████████] 100% | Recording chunk 2...
```

### Hotkeys Disponibles

| Tecla | Acción |
|-------|--------|
| `Q` | Salir de la aplicación |
| `S` | Pausar/Reanudar grabación |
| `D` | Cambiar dispositivo de audio interactivamente |

## ⚙️ Configuración

La configuración se maneja desde `config.json`:

```json
{
  "audio": {
    "sample_rate": 16000,
    "channels": 1,
    "chunk_duration": 3,
    "silence_threshold": 0.01,
    "device_index": -1
  },
  "whisper": {
    "executable": ".\\main.exe",
    "model": ".\\models\\ggml-base.bin",
    "language": "es",
    "threads": 4,
    "temperature": 0.0,
    "print_timestamps": false
  },
  "output": {
    "file": "transcriptions.txt",
    "save_audio_chunks": false,
    "show_visualizer": true
  },
  "performance": {
    "use_gpu": false,
    "n_threads": 4
  }
}
```

**Parámetros clave:**
- `chunk_duration`: Duración de cada captura (segundos) - Recomendado: 2-5s
- `silence_threshold`: Umbral para detectar silencio (0.0-1.0) - Menor = más sensible
- `language`: Código de idioma (es, en, fr, de, etc.) o "auto" para detección automática
- `threads`: Número de hilos para procesamiento (ajustar según tu CPU)
- `save_audio_chunks`: True para guardar archivos .wav temporales
- `show_visualizer`: Mostrar barra de nivel de audio en consola
- `use_gpu`: Habilitar aceleración GPU (solo si compilaste con CUDA)

## 🎯 Características

- ✅ **Instalador inteligente** con detección automática de hardware
- ✅ **Soporte GPU NVIDIA** vía CUDA (compilación automática si está disponible)
- ✅ **Binarios pre-compilados** para CPU (sin necesidad de compilar)
- ✅ Captura de audio en tiempo real desde micrófono
- ✅ Transcripción automática en chunks configurables
- ✅ Detección automática de silencio (evita procesar audio vacío)
- ✅ Detección automática de idioma
- ✅ Guardado de transcripciones en `transcriptions.txt`
- ✅ Interfaz TUI con barra de nivel de audio en tiempo real
- ✅ Hotkeys: Q (Salir), S (Pausar), D (Cambiar dispositivo)
- ✅ Multi-threading para procesamiento paralelo
- ✅ Limpieza automática de archivos temporales
- ✅ Launcher inteligente con verificación de prerequisitos
- ✅ Descarga automática de modelos

## 📝 Archivos Generados

```
project/
├── installer.ps1         # Script de instalación inteligente
├── run.bat               # Launcher principal
├── config.json           # Configuración de la aplicación
├── launcher.py           # Script de verificación y ejecución
├── main.py               # Aplicación principal
├── transcriptions.txt    # Log de todas las transcripciones
├── models/               # Carpeta de modelos
│   └── ggml-base.bin    # Modelo whisper descargado
├── main.exe              # Ejecutable de whisper.cpp (CPU o GPU)
├── venv/                 # Entorno virtual de Python
└── whisper.cpp/          # Repositorio de whisper.cpp
```

## 🐛 Troubleshooting

### "Python no encontrado" / "Git no encontrado"
- Instala Python 3.8+ desde [python.org](https://www.python.org/downloads/)
  - **Importante:** Marcar "Add Python to PATH" durante la instalación
- Instala Git desde [git-scm.com](https://git-scm.com/)

### Error al descargar binario pre-compilado
- Verifica tu conexión a internet
- Intenta descargar manualmente desde [releases de whisper.cpp](https://github.com/ggml-org/whisper.cpp/releases)
- Extrae `main.exe` y colócalo en la raíz del proyecto

### Error al compilar con GPU (CUDA)
- **Verifica Visual Studio Build Tools:**
  1. Descarga desde [visualstudio.microsoft.com/downloads](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022)
  2. Ejecuta el instalador
  3. Selecciona **"Desktop development with C++"**
  4. Reinicia tu computadora
  
- **Verifica CUDA Toolkit:**
  1. Descarga desde [developer.nvidia.com/cuda-downloads](https://developer.nvidia.com/cuda-downloads)
  2. Instala la versión compatible con tu GPU
  3. Reinicia y ejecuta `.\installer.ps1` nuevamente

- **Alternativa rápida:** Usa modo CPU
  ```powershell
  .\installer.ps1 -NoGPU
  ```

### "Whisper executable not found"
- Verifica que `main.exe` esté en la raíz del proyecto
- Si compilaste manualmente, copia desde `whisper.cpp/build/bin/Release/main.exe`
- Ejecuta `.\installer.ps1` para reinstalar automáticamente

### "Model file not found"
- Usa el launcher para descargar: `python launcher.py --download-model base`
- O descarga manualmente de [Hugging Face](https://huggingface.co/ggerganov/whisper.cpp/tree/main)
- Coloca el archivo `.bin` en la carpeta `models/`
- Verifica que el nombre coincida en `config.json`

### Errores de audio / No detecta micrófono
- Comprueba que tu micrófono esté conectado y sea el dispositivo predeterminado
- Lista dispositivos disponibles: `python launcher.py --list-devices`
- Cambia dispositivo: `python launcher.py --device 1` (donde 1 es el ID)
- Cierra otras aplicaciones que puedan estar usando el micrófono (Zoom, Teams, etc.)

### Muy lento / Latencia alta
- Usa modelo `tiny` para velocidad máxima: `python launcher.py --model tiny`
- Reduce `chunk_duration` en `config.json` (ej: 2 segundos)
- Aumenta `threads` en `config.json` según los núcleos de tu CPU
- Si tienes GPU NVIDIA, asegúrate de usar la versión compilada con CUDA
- Cierra otras aplicaciones pesadas

### La app se cierra inmediatamente
- Ejecuta desde línea de comandos para ver el error: `python launcher.py`
- Verifica que todas las dependencias estén instaladas: `pip install -r requirements.txt`
- Revisa que `config.json` tenga formato JSON válido

### Hotkeys no responden
- Asegúrate de que la ventana de consola esté enfocada (click en ella)
- En algunas laptops, presiona `Fn` + la tecla correspondiente

## 📚 Recursos

- [whisper.cpp GitHub](https://github.com/ggml-org/whisper.cpp)
- [Modelos disponibles](https://huggingface.co/ggerganov/whisper.cpp)
- [Documentación Sounddevice](https://python-sounddevice.readthedocs.io/)
- [CUDA Toolkit](https://developer.nvidia.com/cuda-downloads)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022)

## 📄 Licencia

Este proyecto usa whisper.cpp que está bajo licencia MIT.

## 🤝 Contribuciones

¿Mejoras? ¡Abre un PR!

---

**Made with ❤️ for real-time speech recognition on Windows**
