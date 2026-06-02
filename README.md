# 🎙️ Whisper Transcriber para Windows

Aplicación de transcripción de voz a texto en tiempo real usando whisper.cpp, con interfaz web, comandos de voz y bandeja del sistema.

## ✨ Características Principales

- **🌐 Interfaz Web Moderna**: Visualiza la transcripción en tiempo real desde cualquier navegador
- **🎤 Comandos de Voz**: Controla la app con tu voz ("copiar todo", "borrar", "pausar", etc.)
- **💡 Bandeja del Sistema**: Se minimiza discretamente cerca del reloj
- **📋 Portapapeles Automático**: Copia automáticamente el texto transcrito
- **🔇 Detección de Silencio**: Ignora pausas para ahorrar procesamiento
- **⚡ Instalación One-Click**: Configuración automática con un solo comando
- **🎛️ Detección Automática de Micrófono**: Usa el dispositivo por defecto o permite selección manual

## 🚀 Instalación Rápida (Windows)

### Requisitos Previos
- Python 3.8+ instalado ([Descargar aquí](https://www.python.org/downloads/))
- Git instalado (opcional, para compilación automática)
- Visual Studio Build Tools (solo si necesitas GPU o no hay binarios pre-compilados)

### Pasos de Instalación

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/tu-usuario/whisper-transcriber.git
   cd whisper-transcriber
   ```

2. **Ejecuta el instalador automático:**
   ```bash
   setup.bat
   ```
   
   Este script hará automáticamente:
   - ✅ Verificará Python
   - ✅ Creará entorno virtual
   - ✅ Instalará dependencias
   - ✅ Descargará/compilará whisper.cpp
   - ✅ Descargará el modelo base
   - ✅ Creará configuración por defecto

3. **¡Listo! Inicia la aplicación:**
   ```bash
   run_app.bat
   ```

## 📖 Uso

### Inicio
1. Ejecuta `run_app.bat`
2. La aplicación se minimizará a la bandeja del sistema (busca el icono 🎙️)
3. Abre tu navegador en `http://localhost:8080`

### Interfaz Web
- **Ver transcripción en tiempo real**
- **Barra de nivel de audio** visual
- **Botones de control**: Pausar/Reanudar, Copiar, Borrar, Cambiar tema
- **Lista de comandos de voz** disponibles

### Comandos de Voz
Di claramente cualquiera de estos comandos:
- **"Copiar todo"** / **"Copy all"** → Copia toda la transcripción
- **"Borrar"** / **"Clear"** → Borra todo el texto
- **"Pausar grabación"** / **"Pause"** → Detiene temporalmente la grabación
- **"Reanudar grabación"** / **"Resume"** → Continúa grabando
- **"Nuevo párrafo"** / **"New paragraph"** → Inserta un salto de línea

### Icono en Bandeja del Sistema
Haz clic derecho en el icono 🎙️ para:
- 🌐 Abrir interfaz web
- ⏸️ Pausar/Reanudar grabación
- 📋 Copiar texto al portapapeles
- ❌ Salir de la aplicación

## ⚙️ Configuración

Edita `config.json` para personalizar:

```json
{
    "audio": {
        "device_index": -1,          // -1 = automático, o número de dispositivo
        "chunk_duration": 3,         // Duración de cada fragmento (segundos)
        "silence_threshold": 0.01,   // Umbral para detectar silencio
        "sample_rate": 16000         // Frecuencia de muestreo
    },
    "whisper": {
        "model": "models/ggml-base.bin",  // Modelo a usar
        "language": "es",                 // Código de idioma (es, en, fr, etc.)
        "threads": 4,                     // Hilos de CPU
        "use_gpu": false                  // true para GPU NVIDIA (requiere CUDA)
    },
    "output": {
        "show_ui": true,           // Mostrar interfaz web
        "port": 8080,              // Puerto de la interfaz web
        "save_to_file": true,      // Guardar en archivo
        "filename": "transcriptions.txt"  // Nombre del archivo
    },
    "features": {
        "auto_copy": true,         // Copiar automáticamente al portapapeles
        "voice_commands": true,    // Habilitar comandos de voz
        "minimize_to_tray": true   // Minimizar a bandeja del sistema
    }
}
```

## 🎯 Modelos Disponibles

| Modelo | Tamaño | Velocidad | Precisión | Uso Recomendado |
|--------|--------|-----------|-----------|-----------------|
| tiny   | 75 MB  | ⚡⚡⚡     | ⭐⭐       | Pruebas rápidas |
| base   | 142 MB | ⚡⚡       | ⭐⭐⭐      | Uso general ✅  |
| small  | 466 MB | ⚡         | ⭐⭐⭐⭐     | Mayor precisión |
| medium | 1.5 GB | 🐢         | ⭐⭐⭐⭐⭐    | Máxima precisión |
| large  | 3.1 GB | 🐢🐢       | ⭐⭐⭐⭐⭐    | Profesional |

Para cambiar de modelo, edita `config.json` y cambia el valor de `"model"`.

## 🔧 Solución de Problemas

### ❌ "main.exe no encontrado"
**Solución:** 
- Ejecuta `setup.bat` nuevamente
- O descarga manualmente de [whisper.cpp releases](https://github.com/ggml-org/whisper.cpp/releases)
- Extrae `main.exe` en la carpeta del proyecto

### ❌ "Modelo no encontrado"
**Solución:** El instalador lo descarga automáticamente. Si falla, reinicia el script.

### ❌ "Error de audio / PyAudio"
**Solución:**
- Instala Microsoft Visual C++ Redistributable
- Reinstala PyAudio: `pip install --force-reinstall pyaudio`

### ❌ "No detecta el micrófono"
**Solución:**
1. Abre `config.json`
2. Cambia `"device_index": -1` por el número de tu dispositivo
3. Para ver dispositivos disponibles, ejecuta manualmente y busca la lista

### ❌ "La GPU no funciona"
**Requisitos para GPU:**
- Tarjeta NVIDIA con drivers actualizados
- CUDA Toolkit instalado
- whisper.cpp compilado con soporte CUDA

## 📁 Estructura del Proyecto

```
whisper-transcriber/
├── main.py              # Aplicación principal
├── install.py           # Instalador automático
├── config.json          # Configuración
├── requirements.txt     # Dependencias de Python
├── setup.bat            # Script de instalación
├── run_app.bat          # Script de ejecución
├── models/              # Carpeta de modelos
│   └── ggml-base.bin
├── venv/                # Entorno virtual (auto-generado)
└── transcriptions.txt   # Transcripciones guardadas
```

## 💻 Ejemplo de Salida

```
============================================================
  🎙️ Whisper Transcriber Iniciando...
============================================================
✅ Micrófono automático seleccionado: Micrófono (Realtek Audio)
🌐 Interfaz web disponible en http://localhost:8080
💡 La app se ha minimizado a la bandeja del sistema.
   Busca el icono 🎙️ cerca del reloj.
🎙️ Grabando... (Habla claramente)
💬 Comandos disponibles: 'copiar todo', 'borrar', 'pausar', 'reanudar'
🗣️  Hola, esto es una prueba de transcripción.
🗣️  La aplicación funciona correctamente.
📋 Texto copiado por comando de voz
```

## 🛠️ Desarrollo

### Instalar dependencias manualmente:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Ejecutar directamente:
```bash
python main.py
```

## 📝 Licencia

MIT License - Libre uso y modificación.

## 🙏 Agradecimientos

- [whisper.cpp](https://github.com/ggml-org/whisper.cpp) - Motor de transcripción
- [Flask](https://flask.palletsprojects.com/) - Servidor web
- [pystray](https://github.com/moses-palmer/pystray) - Icono en bandeja

---

**¡Disfruta transcribiendo!** 🎉
