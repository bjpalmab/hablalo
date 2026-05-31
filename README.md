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

Esto creará un virtual environment e instalará dependencias.

### Paso 3: Compilar whisper.cpp

**Opción A: Usar Visual Studio (Recomendado)**

1. Clonar whisper.cpp:
```bash
git clone https://github.com/ggml-org/whisper.cpp.git
cd whisper.cpp
```

2. Compilar con MSVC:
```bash
mkdir build
cd build
cmake ..
cmake --build . --config Release
```

3. Copiar `main.exe` a la carpeta del proyecto:
```bash
copy Release\main.exe ..\..\hablalo\
```

**Opción B: Usar mingw-w64**

```bash
cd whisper.cpp
make
# El ejecutable estará en la raíz de whisper.cpp como 'main.exe'
```

**Opción C: Descargar pre-compilado** (Más fácil)

Ve a [releases de whisper.cpp](https://github.com/ggml-org/whisper.cpp/releases) y descarga el ejecutable compilado.

### Paso 4: Descargar modelo

1. Descarga un modelo desde [Hugging Face](https://huggingface.co/ggerganov/whisper.cpp/tree/main):
   - `ggml-base.bin` (~150MB) - Buen balance
   - `ggml-small.bin` (~500MB) - Mejor precisión
   - `ggml-tiny.bin` (~75MB) - Rápido pero menos preciso

2. Crea carpeta y coloca el modelo:
```bash
mkdir models
# Coloca el archivo .bin descargado aquí
```

3. Actualiza `MODEL_PATH` en `main.py` si usas diferente modelo

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
============================================================

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
SAMPLE_RATE = 16000          # Frecuencia de muestreo (Hz)
CHUNK_DURATION = 3            # Duración de cada captura (segundos)
WHISPER_EXECUTABLE = "./main" # Ruta del ejecutable whisper.cpp
MODEL_PATH = "./models/ggml-base.bin"  # Ruta del modelo
```

## 🎯 Características

- ✅ Captura de audio en tiempo real
- ✅ Transcripción automática en chunks
- ✅ Detección automática de idioma
- ✅ Guardado de transcripciones en `transcriptions.txt`
- ✅ Multi-threading para procesamiento paralelo
- ✅ Sin dependencias externas complejas
- ✅ 100% funcional vía código

## 📝 Archivos Generados

```
project/
├── transcriptions.txt    # Log de todas las transcripciones
├── output/               # Archivos de salida temporal de whisper.cpp
├── models/               # Carpeta de modelos
│   └── ggml-base.bin    # Modelo whisper descargado
└── main/                 # Ejecutable compilado de whisper.cpp
```

## 🐛 Troubleshooting

### "Whisper executable not found"
- Verifica que `main.exe` esté en la raíz del proyecto
- Asegúrate de haber compilado whisper.cpp correctamente

### "Model file not found"
- Descarga el modelo a `./models/`
- Verifica que el nombre coincida en `MODEL_PATH`

### Errores de audio
- Comprueba que tu micrófono esté conectado y funcional
- Intenta cambiar el dispositivo de audio en `sd.query_devices()`
- Ajusta el índice en: `sd.default.device[0] = 1` (donde 1 es el ID del dispositivo)

### Muy lento
- Usa `ggml-tiny.bin` para velocidad
- Reduce `CHUNK_DURATION` (ej: 2 segundos)
- Aumenta el número de threads en el comando whisper.cpp

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
