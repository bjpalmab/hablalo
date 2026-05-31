# 🎙️ Hablalo - Real-time Speech to Text

Aplicación Windows para transcribir voz a texto en tiempo real usando **whisper.cpp**. 100% funcional, basado en código Python sin UI compleja.

## 📋 Requisitos Previos

- **Windows 10/11**
- **Python 3.8+** ([Descargar](https://www.python.org/downloads/))
- **whisper.cpp** compilado ([Ver sección de instalación](#instalación))
- **Micrófono** funcional

## 🚀 Instalación Rápida

### Paso 1: Clonar el repositorio
```bash
git clone https://github.com/bjpalmab/hablalo.git
cd hablalo
```

### Paso 2: Ejecutar setup (Windows)
```bash
setup_windows.bat
```

Esto creará un virtual environment e instalará dependencias. También clonará whisper.cpp automáticamente.

### Paso 3: Compilar whisper.cpp

**Opción A: Usar Visual Studio (Recomendado)**

1. Ir al directorio de whisper.cpp:
```bash
cd whisper.cpp
```

2. Crear build y compilar con MSVC:
```bash
mkdir build
cd build
cmake ..
cmake --build . --config Release
```

3. Copiar `main.exe` a la carpeta del proyecto:
```bash
copy Release\main.exe ..\..\main.exe
```

**Opción B: Descargar pre-compilado** (Más fácil)

Ve a [releases de whisper.cpp](https://github.com/ggml-org/whisper.cpp/releases) y descarga el ejecutable compilado para Windows. Coloca `main.exe` en la raíz del proyecto.

### Paso 4: Descargar modelo

1. Descarga un modelo desde [Hugging Face](https://huggingface.co/ggerganov/whisper.cpp/tree/main):
   - `ggml-tiny.bin` (~75MB) - Más rápido, menos preciso
   - `ggml-base.bin` (~150MB) - Buen balance ⭐ RECOMENDADO
   - `ggml-small.bin` (~500MB) - Mejor precisión

2. Crea carpeta y coloca el modelo:
```bash
mkdir models
# Coloca el archivo .bin descargado aquí
```

## 📖 Uso

```bash
run.bat
```

O directamente desde PowerShell:
```powershell
.\venv\Scripts\Activate.ps1
python main.py
```

### Ejemplo de Salida

```
============================================================
🎙️  Real-time Speech-to-Text with whisper.cpp
============================================================
Sample rate: 16000 Hz
Chunk duration: 3 seconds
Whisper model: ./models/ggml-base.bin
Whisper executable: ./main
============================================================

🔊 Available audio devices:
   → [0] Microphone (Realtek Audio)
   [1] Stereo Mix (Realtek Audio)

🎙️  Press Ctrl+C to stop recording and exit
Starting continuous recording...

🎤 Recording audio chunk...
✓ Audio chunk recorded (3s)
🔄 Transcribing: audio_20260531_143022_chunk_1.wav

✨ [20260531_143022] Transcription #1:
   Hello, this is a test of the speech to text system

🎤 Recording audio chunk...
```

## ⚙️ Configuración

Edita `main.py` para ajustar:

```python
SAMPLE_RATE = 16000          # Frecuencia de muestreo (Hz) - No cambiar
CHUNK_DURATION = 3            # Duración de cada captura (segundos)
WHISPER_EXECUTABLE = "./main" # Ruta del ejecutable whisper.cpp
MODEL_PATH = "./models/ggml-base.bin"  # Ruta del modelo
SAVE_AUDIO_CHUNKS = False     # True para guardar archivos .wav
```

## 🎯 Características

- ✅ Captura de audio en tiempo real desde micrófono
- ✅ Transcripción automática en chunks de 3 segundos
- ✅ Detección automática de idioma
- ✅ Guardado de transcripciones en `transcriptions.txt`
- ✅ Multi-threading para procesamiento paralelo
- ✅ Sin dependencias externas complejas
- ✅ 100% funcional vía código, sin UI
- ✅ Limpieza automática de archivos temporales

## 📝 Archivos Generados

```
project/
├── transcriptions.txt    # Log de todas las transcripciones
├── models/               # Carpeta de modelos
│   └── ggml-base.bin    # Modelo whisper descargado
├── main.exe              # Ejecutable compilado de whisper.cpp
├── venv/                 # Entorno virtual de Python
└── whisper.cpp/          # Repositorio de whisper.cpp
```

## 🐛 Troubleshooting

### "Whisper executable not found"
- Verifica que `main.exe` esté en la raíz del proyecto
- Asegúrate de haber compilado whisper.cpp correctamente
- Si usas Windows, asegúrate de que sea `.exe` no solo `main`

### "Model file not found"
- Descarga el modelo a `./models/`
- Verifica que el nombre coincida en `MODEL_PATH`
- Los modelos deben ser formato `.bin` de whisper.cpp

### Errores de audio
- Comprueba que tu micrófono esté conectado y funcional
- Intenta cambiar el dispositivo de audio en `sd.query_devices()`
- Ajusta el índice en: `sd.default.device[0] = 1` (donde 1 es el ID del dispositivo)

### Muy lento
- Usa `ggml-tiny.bin` para velocidad máxima
- Reduce `CHUNK_DURATION` (ej: 2 segundos)
- Aumenta el número de threads en el comando whisper.cpp

### Error al compilar whisper.cpp en Windows
- Instala Visual Studio Build Tools con soporte C++
- O usa MSYS2 con toolchain mingw-w64
- O descarga binario pre-compilado de releases

## 📚 Recursos

- [whisper.cpp GitHub](https://github.com/ggml-org/whisper.cpp)
- [Modelos disponibles](https://huggingface.co/ggerganov/whisper.cpp)
- [Documentación Sounddevice](https://python-sounddevice.readthedocs.io/)

## 📄 Licencia

Este proyecto usa whisper.cpp que está bajo licencia MIT.

## 🤝 Contribuciones

¿Mejoras? ¡Abre un PR!

---

**Made with ❤️ for real-time speech recognition on Windows**
