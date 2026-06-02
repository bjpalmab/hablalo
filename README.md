# 🎙️ Háblalo - Transcriptor de Voz a Texto

Aplicación de transcripción de voz a texto en tiempo real para Windows usando whisper.cpp, con interfaz web, comandos de voz, bandeja del sistema y procesamiento asíncrono.

**Repositorio:** [https://github.com/bjpalmab/hablalo](https://github.com/bjpalmab/hablalo)

## ✨ Características Principales

- **🌐 Interfaz Web Moderna**: Visualiza la transcripción en tiempo real desde cualquier navegador con historial y exportación
- **📜 Historial de Transcripciones**: Todos los segmentos se guardan con timestamps para revisión posterior
- **📥 Exportación Múltiple**: Exporta transcripciones en formatos TXT, JSON y CSV
- **🎤 Comandos de Voz**: Controla la app con tu voz ("copiar todo", "borrar", "pausar", etc.)
- **💡 Bandeja del Sistema**: Se minimiza discretamente cerca del reloj
- **📋 Portapapeles Automático**: Copia automáticamente el texto transcrito
- **✏️ Puntuación Automática**: Añade puntuación y capitalización inteligente a las transcripciones
- **🔇 Detección de Silencio**: Ignora pausas para ahorrar procesamiento
- **⚡ Procesamiento Asíncrono**: Arquitectura basada en colas para máximo rendimiento sin bloqueos
- **📊 Estadísticas en Tiempo Real**: Contador de caracteres, palabras y segmentos
- **🌓 Tema Oscuro/Claro**: Interfaz personalizable con preferencia persistente
- **🎛️ Detección Automática de Micrófono**: Usa el dispositivo por defecto o permite selección manual
- **📝 Logging Completo**: Registro detallado de eventos para debugging

## 🚀 Instalación Paso a Paso (Windows)

### Requisitos Previos
- **Python 3.8+** instalado ([Descargar aquí](https://www.python.org/downloads/))
- **Git** instalado (recomendado para clonar el repositorio)
- **Visual Studio Build Tools** (solo si necesitas GPU o no hay binarios pre-compilados de whisper.cpp)

### Método 1: Instalación Automática (Recomendado)

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/bjpalmab/hablalo.git
   cd hablalo
   ```

2. **Ejecuta el instalador automático:**
   ```bash
   setup.bat
   ```
   
   Este script realizará automáticamente:
   - ✅ Verificación de Python y versión
   - ✅ Creación de entorno virtual (`venv/`)
   - ✅ Instalación de dependencias de `requirements.txt`
   - ✅ Descarga/compilación de whisper.cpp
   - ✅ Descarga del modelo base de whisper
   - ✅ Creación de `config.json` con valores por defecto

3. **¡Listo! Inicia la aplicación:**
   ```bash
   run_app.bat
   ```

### Método 2: Instalación Manual (Paso a Paso Detallado)

Si prefieres controlar cada paso o el instalador automático falla:

#### Paso 1: Clonar el Repositorio
```bash
git clone https://github.com/bjpalmab/hablalo.git
cd hablalo
```

#### Paso 2: Crear Entorno Virtual
```bash
python -m venv venv
```

#### Paso 3: Activar Entorno Virtual
```bash
# En CMD
venv\Scripts\activate

# En PowerShell
.\venv\Scripts\Activate.ps1
```

#### Paso 4: Instalar Dependencias
```bash
pip install -r requirements.txt
```

**Nota:** Si `pyaudio` falla al instalarse:
- Descarga el wheel correspondiente desde [Gohlke's Python Packages](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)
- Instala con: `pip install PyAudio-0.2.14-cp312-cp312-win_amd64.whl` (ajusta la versión según tu Python)

#### Paso 5: Instalar whisper.cpp

**Opción A - Descargar binario pre-compilado (Recomendado):**
```bash
# Crea carpeta para whisper.cpp
mkdir whisper
cd whisper

# Descarga la última versión desde GitHub Releases
# Visita: https://github.com/ggml-org/whisper.cpp/releases
# Descarga whisper-bin-x64.zip y extrae en esta carpeta

cd ..
```

**Opción B - Compilar desde código fuente:**
```bash
git clone https://github.com/ggml-org/whisper.cpp.git
cd whisper.cpp
make
# Para GPU NVIDIA: make GGML_CUDA=1
cd ..
```

#### Paso 6: Descargar Modelo de Whisper
```bash
# Crea carpeta de modelos
mkdir models
cd models

# Descarga el modelo base (puedes cambiar a tiny, small, medium, large)
curl -L -o ggml-base.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin

cd ..
```

#### Paso 7: Verificar Configuración
El archivo `config.json` debería existir. Si no, créalo con:
```json
{
    "audio": {
        "device_index": -1,
        "chunk_duration": 3,
        "silence_threshold": 0.01,
        "sample_rate": 16000,
        "channels": 1
    },
    "whisper": {
        "model": "models/ggml-base.bin",
        "language": "es",
        "threads": 4,
        "use_gpu": false
    },
    "output": {
        "show_ui": true,
        "port": 8080,
        "save_to_file": true,
        "filename": "transcriptions.txt",
        "export_formats": ["txt", "json", "csv"]
    },
    "features": {
        "auto_copy": true,
        "voice_commands": true,
        "minimize_to_tray": true,
        "auto_punctuation": true
    },
    "performance": {
        "queue_size": 10,
        "processing_threads": 2,
        "timeout_seconds": 60
    }
}
```

#### Paso 8: Ejecutar la Aplicación
```bash
# Con el entorno virtual activado
python main.py
```

O usa el script batch:
```bash
run_app.bat
```

## 📖 Uso

### Inicio
1. Ejecuta `run_app.bat` o `python main.py`
2. La aplicación se minimizará a la bandeja del sistema (busca el icono 🎙️ cerca del reloj)
3. Abre tu navegador en `http://localhost:8080`

### Interfaz Web

La interfaz web ofrece las siguientes funcionalidades:

#### Panel Principal
- **Transcripción en Tiempo Real**: El texto aparece conforme se transcribe
- **Barra de Nivel de Audio**: Visualización del volumen del micrófono
- **Estadísticas**: Contador de caracteres, palabras y segmentos transcritos

#### Botones de Control
- **⏸️ Pausar/Reanudar**: Detiene o continúa la grabación
- **📋 Copiar**: Copia toda la transcripción al portapapeles
- **🗑️ Borrar**: Limpia toda la transcripción (con confirmación)
- **🌓 Tema**: Cambia entre modo oscuro y claro
- **📥 Exportar**: Descarga la transcripción en TXT, JSON o CSV

#### Historial de Segmentos
- Cada segmento transcrito se muestra con su timestamp
- Scroll infinito para revisar transcripciones anteriores
- Búsqueda en tiempo real dentro del historial

### Comandos de Voz

Di claramente cualquiera de estos comandos:

| Comando (Español) | Comando (Inglés) | Acción |
|-------------------|------------------|--------|
| "Copiar todo" | "Copy all" | Copia toda la transcripción |
| "Borrar" | "Clear" | Borra todo el texto |
| "Pausar grabación" | "Pause" | Detiene temporalmente la grabación |
| "Reanudar grabación" | "Resume" | Continúa grabando |
| "Nuevo párrafo" | "New paragraph" | Inserta un salto de línea |

### Icono en Bandeja del Sistema

Haz clic derecho en el icono 🎙️ para acceder al menú:
- **🌐 Abrir interfaz web** - Abre localhost:8080 en tu navegador
- **⏸️ Pausar/Reanudar grabación** - Controla el estado de grabación
- **📋 Copiar texto** - Copia la transcripción actual al portapapeles
- **❌ Salir** - Cierra la aplicación correctamente

## ⚙️ Configuración

Edita `config.json` para personalizar el comportamiento:

```json
{
    "audio": {
        "device_index": -1,          // -1 = automático, o número de dispositivo específico
        "chunk_duration": 3,         // Duración de cada fragmento en segundos
        "silence_threshold": 0.01,   // Umbral para detectar silencio (0.0-1.0)
        "sample_rate": 16000,        // Frecuencia de muestreo en Hz
        "channels": 1                // Canales de audio (1 = mono)
    },
    "whisper": {
        "model": "models/ggml-base.bin",  // Ruta al modelo
        "language": "es",                 // Código de idioma (es, en, fr, de, etc.)
        "threads": 4,                     // Hilos de CPU para procesamiento
        "use_gpu": false                  // true para GPU NVIDIA (requiere CUDA)
    },
    "output": {
        "show_ui": true,                    // Mostrar interfaz web
        "port": 8080,                       // Puerto del servidor web
        "save_to_file": true,               // Guardar transcripciones en archivo
        "filename": "transcriptions.txt",   // Nombre del archivo de salida
        "export_formats": ["txt", "json", "csv"]  // Formatos de exportación disponibles
    },
    "features": {
        "auto_copy": true,              // Copiar automáticamente al portapapeles
        "voice_commands": true,         // Habilitar comandos de voz
        "minimize_to_tray": true,       // Minimizar a bandeja del sistema
        "auto_punctuation": true        // Añadir puntuación automática
    },
    "performance": {
        "queue_size": 10,               // Tamaño máximo de la cola de audio
        "processing_threads": 2,        // Hilos para procesamiento asíncrono
        "timeout_seconds": 60           // Timeout para operaciones
    }
}
```

### Opciones Destacadas

#### `auto_punctuation` (Nuevo)
Cuando está activado (`true`):
- Capitaliza automáticamente la primera letra de cada segmento
- Añade punto final si el segmento no tiene puntuación
- Mejora la legibilidad del texto transcrito

#### `processing_threads`
- **1**: Mínimo uso de CPU, puede haber retrasos
- **2-4**: Balance recomendado para la mayoría de sistemas
- **4+**: Máximo rendimiento en sistemas multi-core

#### `queue_size`
- Controla cuántos fragmentos de audio pueden estar en espera
- Valor bajo: Menor latencia pero posible pérdida de audio
- Valor alto: Más buffer pero mayor uso de memoria

## 🎯 Modelos Disponibles

| Modelo | Tamaño | Velocidad | Precisión | Uso Recomendado | RAM Mínima |
|--------|--------|-----------|-----------|-----------------|------------|
| tiny   | 75 MB  | ⚡⚡⚡     | ⭐⭐       | Pruebas rápidas | 2 GB |
| base   | 142 MB | ⚡⚡       | ⭐⭐⭐      | Uso general ✅  | 4 GB |
| small  | 466 MB | ⚡         | ⭐⭐⭐⭐     | Mayor precisión | 8 GB |
| medium | 1.5 GB | 🐢         | ⭐⭐⭐⭐⭐    | Alta precisión  | 16 GB |
| large  | 3.1 GB | 🐢🐢       | ⭐⭐⭐⭐⭐    | Profesional     | 32 GB |

Para cambiar de modelo:
1. Descarga el modelo deseado en la carpeta `models/`
2. Edita `config.json` y cambia `"model"` a la nueva ruta
3. Reinicia la aplicación

## 🔧 Solución de Problemas

### ❌ "main.exe no encontrado"
**Causa:** whisper.cpp no está instalado o no se encuentra el ejecutable

**Solución:** 
1. Ejecuta `setup.bat` nuevamente
2. O descarga manualmente de [whisper.cpp releases](https://github.com/ggml-org/whisper.cpp/releases)
3. Extrae `main.exe` en la carpeta raíz del proyecto
4. Verifica que `main.exe` tenga permisos de ejecución

### ❌ "Modelo no encontrado"
**Causa:** El archivo del modelo no existe en la ruta especificada

**Solución:** 
1. Verifica la ruta en `config.json`
2. Descarga el modelo: `curl -L -o models/ggml-base.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin`
3. O usa el instalador automático que lo descarga por ti

### ❌ "Error de audio / PyAudio"
**Causa:** PyAudio no puede inicializarse o no encuentra dispositivos

**Solución:**
1. Instala Microsoft Visual C++ Redistributable
2. Reinstala PyAudio: `pip uninstall pyaudio && pip install pyaudio`
3. Si persiste, descarga el wheel pre-compilado desde [aquí](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)
4. Verifica que tu micrófono esté conectado y sea el dispositivo por defecto

### ❌ "No detecta el micrófono"
**Causa:** El dispositivo de audio no es el predeterminado o el índice es incorrecto

**Solución:**
1. Abre `config.json`
2. Cambia `"device_index": -1` por el número de tu dispositivo
3. Para ver la lista de dispositivos, revisa el archivo `transcriber.log` después de iniciar la app
4. En Windows, ve a Configuración → Sistema → Sonido y verifica el dispositivo de entrada

### ❌ "La GPU no funciona"
**Requisitos para GPU:**
- Tarjeta NVIDIA con drivers actualizados (versión 470+)
- CUDA Toolkit 11.x o superior instalado
- whisper.cpp compilado con soporte CUDA (`make GGML_CUDA=1`)

**Solución:**
1. Verifica CUDA: `nvidia-smi` debe mostrar tus GPUs
2. Compila whisper.cpp con CUDA: `make GGML_CUDA=1`
3. Cambia `"use_gpu": true` en `config.json`
4. Revisa `transcriber.log` para errores de inicialización CUDA

### ❌ "La interfaz web no carga"
**Causa:** El puerto está ocupado o el firewall bloquea la conexión

**Solución:**
1. Cambia el puerto en `config.json` (ej. de 8080 a 8081)
2. Verifica que no haya otra aplicación usando el puerto
3. Agrega una excepción en el firewall de Windows para Python
4. Accede explícitamente a `http://127.0.0.1:8080` en lugar de localhost

### ❌ "La aplicación se cierra inesperadamente"
**Causa:** Error no manejado o falta de recursos

**Solución:**
1. Revisa `transcriber.log` para ver el error específico
2. Reduce `processing_threads` a 1 en `config.json`
3. Disminuye `queue_size` si tienes poca RAM
4. Ejecuta como administrador si hay problemas de permisos

## 📁 Estructura del Proyecto

```
hablalo/
├── main.py                 # Aplicación principal con lógica completa
├── launcher.py             # Lanzador alternativo
├── install.py              # Script de instalación programático
├── installer.ps1           # Instalador PowerShell
├── config.json             # Configuración centralizada
├── requirements.txt        # Dependencias de Python
├── README.md               # Esta documentación
├── transcriber.log         # Logs de ejecución (auto-generado)
├── transcriptions.txt      # Transcripciones guardadas (auto-generado)
│
├── scripts/
│   ├── setup.bat           # Instalador automático Windows
│   ├── run_app.bat         # Ejecutor de la aplicación
│   └── setup_windows.bat   # Setup alternativo
│
├── models/                 # Modelos de whisper (descargar manualmente)
│   ├── ggml-tiny.bin
│   ├── ggml-base.bin       # Modelo por defecto
│   ├── ggml-small.bin
│   ├── ggml-medium.bin
│   └── ggml-large.bin
│
├── whisper/                # Binarios de whisper.cpp (opcional)
│   └── main.exe
│
└── venv/                   # Entorno virtual de Python (auto-generado)
```

## 💻 Ejemplo de Salida

```
============================================================
  🎙️ Háblalo - Transcriptor Iniciando...
============================================================
✅ Configuración cargada desde config.json
✅ Micrófono automático seleccionado: Micrófono (Realtek Audio)
✅ Modelo whisper cargado: models/ggml-base.bin
🌐 Interfaz web disponible en http://localhost:8080
💡 La app se ha minimizado a la bandeja del sistema.
   Busca el icono 🎙️ cerca del reloj.
🎙️ Grabando... (Habla claramente)
💬 Comandos disponibles: 'copiar todo', 'borrar', 'pausar', 'reanudar'
📊 Workers asíncronos iniciados: 2 hilos
🗣️  Hola, esto es una prueba de transcripción.
🗣️  La aplicación funciona correctamente con procesamiento asíncrono.
✏️  Puntuación automática aplicada.
📋 Texto copiado por comando de voz
```

## 🛠️ Desarrollo

### Instalar dependencias para desarrollo:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install pytest pytest-cov  # Para tests
```

### Ejecutar directamente:
```bash
python main.py
```

### Ver logs en tiempo real:
```bash
# PowerShell
Get-Content transcriber.log -Wait -Tail 50

# CMD
type transcriber.log | more
```

### Ejecutar tests (cuando estén disponibles):
```bash
pytest tests/ -v --cov=main
```

## 📊 Rendimiento y Optimización

### Recomendaciones por Hardware

**Sistema Básico (4GB RAM, CPU dual-core):**
```json
{
    "whisper": {"model": "models/ggml-tiny.bin", "threads": 2},
    "performance": {"queue_size": 5, "processing_threads": 1}
}
```

**Sistema Promedio (8-16GB RAM, CPU quad-core):**
```json
{
    "whisper": {"model": "models/ggml-base.bin", "threads": 4},
    "performance": {"queue_size": 10, "processing_threads": 2}
}
```

**Sistema Avanzado (32GB+ RAM, CPU 8+ cores, GPU NVIDIA):**
```json
{
    "whisper": {"model": "models/ggml-large.bin", "threads": 8, "use_gpu": true},
    "performance": {"queue_size": 20, "processing_threads": 4}
}
```

### Métricas Esperadas (modelo base, CPU)

| Duración de Audio | Tiempo de Transcripción | Latencia |
|-------------------|-------------------------|----------|
| 3 segundos        | ~1-2 segundos          | Baja     |
| 1 minuto          | ~20-30 segundos        | Media    |
| 10 minutos        | ~3-5 minutos           | Alta     |

*Con GPU NVIDIA, los tiempos se reducen aproximadamente 3-5x*

## 📝 Licencia

MIT License - Libre uso y modificación. Ver archivo LICENSE para detalles.

## 🙏 Agradecimientos

- **[whisper.cpp](https://github.com/ggml-org/whisper.cpp)** - Motor de transcripción de voz
- **[Flask](https://flask.palletsprojects.com/)** - Servidor web embebido
- **[pystray](https://github.com/moses-palmer/pystray)** - Icono en bandeja del sistema
- **[PyAudio](https://people.csail.mit.edu/hubert/pyaudio/)** - Captura de audio
- **[NumPy](https://numpy.org/)** - Procesamiento numérico

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Haz fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📞 Soporte

- **Issues:** [GitHub Issues](https://github.com/bjpalmab/hablalo/issues)
- **Discusiones:** [GitHub Discussions](https://github.com/bjpalmab/hablalo/discussions)

---

**¡Disfruta transcribiendo con Háblalo!** 🎉

*Última actualización: 2024*
