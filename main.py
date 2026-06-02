"""
Whisper Transcriber con Interfaz Web, Comandos de Voz y Bandeja del Sistema.
Versión mejorada con procesamiento asíncrono, colas, y mejor manejo de errores.
"""
import os
import sys
import json
import time
import threading
import wave
import logging
import queue
import re
import numpy as np
import pyaudio
import subprocess
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template_string, jsonify, request
from http.server import HTTPServer
import pystray
from pystray import Icon, MenuItem, Menu
from PIL import Image

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('transcriber.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Cargar configuración unificada
CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
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
        "use_gpu": False
    },
    "output": {
        "show_ui": True, 
        "port": 8080, 
        "save_to_file": True, 
        "filename": "transcriptions.txt",
        "export_formats": ["txt", "json", "csv"]
    },
    "features": {
        "auto_copy": True, 
        "voice_commands": True, 
        "minimize_to_tray": True,
        "auto_punctuation": True
    },
    "performance": {
        "queue_size": 10,
        "processing_threads": 2,
        "timeout_seconds": 60
    }
}

def load_config():
    """Carga configuración desde archivo o crea default"""
    try:
        if Path(CONFIG_FILE).exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                # Fusionar con defaults para asegurar todas las claves
                for key in DEFAULT_CONFIG:
                    if key not in loaded_config:
                        loaded_config[key] = DEFAULT_CONFIG[key]
                    elif isinstance(DEFAULT_CONFIG[key], dict):
                        for subkey in DEFAULT_CONFIG[key]:
                            if subkey not in loaded_config[key]:
                                loaded_config[key][subkey] = DEFAULT_CONFIG[key][subkey]
                return loaded_config
    except Exception as e:
        logger.error(f"Error cargando config: {e}")
    
    # Crear config por defecto
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        logger.info("Configuración por defecto creada")
    except Exception as e:
        logger.error(f"Error creando config: {e}")
    return DEFAULT_CONFIG

config = load_config()

# Cola de procesamiento asíncrono
audio_queue = queue.Queue(maxsize=config.get("performance", {}).get("queue_size", 10))
transcription_queue = queue.Queue(maxsize=config.get("performance", {}).get("queue_size", 10))

# Estado de la aplicación con gestión centralizada
class AppState:
    def __init__(self):
        self.running = True
        self.paused = False
        self.full_transcription = ""
        self.transcription_history = []  # Historial de transcripciones
        self.audio_level = 0
        self.lock = threading.Lock()
        self.session_start = datetime.now()
    
    def add_transcription(self, text):
        with self.lock:
            self.full_transcription += text + " "
            self.transcription_history.append({
                "text": text,
                "timestamp": datetime.now().isoformat()
            })
    
    def get_full_text(self):
        with self.lock:
            return self.full_transcription
    
    def clear(self):
        with self.lock:
            self.full_transcription = ""
            self.transcription_history = []
    
    def export(self, format_type="txt"):
        with self.lock:
            if format_type == "txt":
                return self.full_transcription
            elif format_type == "json":
                return json.dumps({
                    "session_start": self.session_start.isoformat(),
                    "transcriptions": self.transcription_history,
                    "full_text": self.full_transcription
                }, indent=2, ensure_ascii=False)
            elif format_type == "csv":
                lines = ["timestamp,text"]
                for item in self.transcription_history:
                    text_escaped = item["text"].replace('"', '""')
                    lines.append(f'{item["timestamp"]},"{text_escaped}"')
                return "\n".join(lines)
            return self.full_transcription

state = AppState()
icon_ref = None

# Función de puntuación automática
def add_punctuation(text):
    """Añade puntuación básica automáticamente"""
    if not config.get("features", {}).get("auto_punctuation", True):
        return text
    
    # Reglas básicas de puntuación
    text = text.strip()
    if not text:
        return text
    
    # Capitalizar primera letra
    text = text[0].upper() + text[1:] if len(text) > 1 else text.upper()
    
    # Añadir punto final si no tiene puntuación
    if not any(text.endswith(c) for c in '.!?¿?'):
        text += '.'
    
    return text

# HTML mejorado para la interfaz web con historial y exportación
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Whisper Transcriber</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; 
               background: #f5f5f5; color: #333; transition: all 0.3s; }
        .dark-mode { background: #1a1a1a; color: #e0e0e0; }
        .container { max-width: 1000px; margin: 0 auto; }
        h1 { text-align: center; color: #2196F3; }
        .status { text-align: center; padding: 10px; margin: 10px 0; border-radius: 5px; 
                  background: #e3f2fd; color: #1976D2; font-weight: bold; }
        .dark-mode .status { background: #333; color: #64B5F6; }
        .controls { text-align: center; margin: 20px 0; flex-wrap: wrap; display: flex; justify-content: center; gap: 8px; }
        button { padding: 10px 20px; margin: 5px; font-size: 14px; cursor: pointer; 
                 border: none; border-radius: 5px; background: #2196F3; color: white; transition: all 0.2s; }
        button:hover { background: #1976D2; transform: translateY(-2px); }
        button.danger { background: #f44336; }
        button.danger:hover { background: #d32f2f; }
        button.success { background: #4CAF50; }
        button.success:hover { background: #45a049; }
        button.secondary { background: #9E9E9E; }
        button.secondary:hover { background: #757575; }
        .transcription { background: white; padding: 20px; border-radius: 8px; 
                         box-shadow: 0 2px 5px rgba(0,0,0,0.1); min-height: 300px; 
                         white-space: pre-wrap; line-height: 1.6; max-height: 500px; overflow-y: auto; }
        .dark-mode .transcription { background: #2d2d2d; box-shadow: 0 2px 5px rgba(255,255,255,0.1); }
        .audio-level { height: 20px; background: #e0e0e0; border-radius: 10px; 
                       overflow: hidden; margin: 10px 0; }
        .level-bar { height: 100%; background: linear-gradient(90deg, #4CAF50, #8BC34A); 
                     width: 0%; transition: width 0.1s; }
        .commands { margin-top: 20px; padding: 15px; background: #fff3cd; border-radius: 5px; }
        .dark-mode .commands { background: #444; }
        .history-panel { margin-top: 20px; background: white; padding: 15px; border-radius: 8px; 
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .dark-mode .history-panel { background: #2d2d2d; }
        .history-item { padding: 8px; margin: 5px 0; background: #f5f5f5; border-radius: 4px; 
                       border-left: 3px solid #2196F3; }
        .dark-mode .history-item { background: #3d3d3d; }
        .history-time { font-size: 12px; color: #666; }
        .dark-mode .history-time { color: #aaa; }
        .export-options { margin: 15px 0; padding: 15px; background: #e8f5e9; border-radius: 5px; }
        .dark-mode .export-options { background: #2e4a2e; }
        select { padding: 8px; border-radius: 4px; border: 1px solid #ccc; margin: 5px; }
        .stats { display: flex; justify-content: space-around; margin: 15px 0; flex-wrap: wrap; }
        .stat-box { background: #e3f2fd; padding: 10px 20px; border-radius: 5px; text-align: center; }
        .dark-mode .stat-box { background: #333; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎙️ Whisper Transcriber</h1>
        <div class="status" id="status">Estado: Grabando...</div>
        <div class="audio-level"><div class="level-bar" id="levelBar"></div></div>
        
        <div class="stats">
            <div class="stat-box">
                <strong id="charCount">0</strong><br>Caracteres
            </div>
            <div class="stat-box">
                <strong id="wordCount">0</strong><br>Palabras
            </div>
            <div class="stat-box">
                <strong id="segmentCount">0</strong><br>Segmentos
            </div>
        </div>
        
        <div class="controls">
            <button onclick="togglePause()">⏸️ Pausar/Reanudar</button>
            <button onclick="copyText()">📋 Copiar</button>
            <button onclick="clearText()" class="danger">🗑️ Borrar</button>
            <button onclick="toggleTheme()">🌓 Tema</button>
            <button onclick="showHistory()" class="secondary">📜 Historial</button>
        </div>
        
        <div class="export-options">
            <strong>📥 Exportar:</strong>
            <select id="exportFormat">
                <option value="txt">Texto Plano (.txt)</option>
                <option value="json">JSON (.json)</option>
                <option value="csv">CSV (.csv)</option>
            </select>
            <button onclick="exportText()" class="success">💾 Descargar</button>
        </div>
        
        <div class="transcription" id="transcription">Esperando audio...</div>
        
        <div class="history-panel" id="historyPanel" style="display: none;">
            <h3>📜 Historial de Segmentos</h3>
            <div id="historyList"></div>
            <button onclick="hideHistory()" class="secondary">Ocultar Historial</button>
        </div>
        
        <div class="commands">
            <strong>🎤 Comandos de Voz:</strong><br>
            "Copiar todo", "Borrar texto", "Nuevo párrafo", "Pausar grabación", "Reanudar grabación"
        </div>
    </div>
    <script>
        let isPaused = false;
        let historyVisible = false;
        
        function updateTranscription() {
            fetch('/api/transcription').then(r => r.json()).then(data => {
                document.getElementById('transcription').innerText = data.text || 'Esperando audio...';
                document.getElementById('levelBar').style.width = (data.level || 0) + '%';
                
                // Actualizar estadísticas
                const text = data.text || '';
                document.getElementById('charCount').textContent = text.length;
                document.getElementById('wordCount').textContent = text.trim() ? text.trim().split(/\\s+/).length : 0;
                document.getElementById('segmentCount').textContent = data.segments || 0;
            });
        }
        setInterval(updateTranscription, 500);
        
        function togglePause() {
            fetch('/api/pause', {method: 'POST'}).then(() => location.reload());
        }
        
        function copyText() {
            navigator.clipboard.writeText(document.getElementById('transcription').innerText)
                .then(() => alert('¡Texto copiado al portapapeles!'))
                .catch(() => fetch('/api/copy', {method: 'POST'}).then(() => alert('¡Texto copiado!')));
        }
        
        function clearText() {
            if(confirm('¿Estás seguro de borrar todo el texto?')) {
                fetch('/api/clear', {method: 'POST'}).then(() => location.reload());
            }
        }
        
        function toggleTheme() {
            document.body.classList.toggle('dark-mode');
            localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
        }
        
        // Cargar preferencia de tema
        if(localStorage.getItem('darkMode') === 'true') {
            document.body.classList.add('dark-mode');
        }
        
        function showHistory() {
            fetch('/api/history').then(r => r.json()).then(data => {
                const list = document.getElementById('historyList');
                list.innerHTML = '';
                data.history.forEach(item => {
                    const div = document.createElement('div');
                    div.className = 'history-item';
                    div.innerHTML = `<span class="history-time">${new Date(item.timestamp).toLocaleString()}</span>: ${item.text}`;
                    list.appendChild(div);
                });
                document.getElementById('historyPanel').style.display = 'block';
                historyVisible = true;
            });
        }
        
        function hideHistory() {
            document.getElementById('historyPanel').style.display = 'none';
            historyVisible = false;
        }
        
        function exportText() {
            const format = document.getElementById('exportFormat').value;
            window.open(`/api/export?format=${format}`, '_blank');
        }
    </script>
</body>
</html>
"""

class AudioProcessor:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.device_index = config["audio"]["device_index"]
        self.sample_rate = config["audio"]["sample_rate"]
        self.chunk_duration = config["audio"]["chunk_duration"]
        self.silence_threshold = config["audio"]["silence_threshold"]
        self.detect_device()
    
    def detect_device(self):
        """Detecta automáticamente el micrófono por defecto o permite selección"""
        if self.device_index == -1:
            # Usar dispositivo por defecto
            self.device_index = self.p.get_default_input_device_info()['index']
            print(f"✅ Micrófono automático seleccionado: {self.p.get_device_info_by_index(self.device_index)['name']}")
        else:
            try:
                info = self.p.get_device_info_by_index(self.device_index)
                print(f"✅ Micrófono configurado: {info['name']}")
            except Exception as e:
                print(f"⚠️  Dispositivo {self.device_index} no encontrado, usando default.")
                self.device_index = self.p.get_default_input_device_info()['index']
    
    def list_devices(self):
        """Lista todos los dispositivos de entrada disponibles"""
        print("\n🎤 Dispositivos de audio disponibles:")
        for i in range(self.p.get_device_count()):
            info = self.p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                default = " (DEFAULT)" if i == self.p.get_default_input_device_info()['index'] else ""
                print(f"  [{i}] {info['name']}{default}")
    
    def record_chunk(self):
        """Graba un fragmento de audio"""
        chunk_size = int(self.sample_rate * self.chunk_duration)
        stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=self.sample_rate,
                            input=True, input_device_index=self.device_index, frames_per_buffer=chunk_size)
        
        frames = []
        for _ in range(int(self.sample_rate / 1024 * self.chunk_duration)):
            data = stream.read(1024, exception_on_overflow=False)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
        
        audio_data = b''.join(frames)
        return np.frombuffer(audio_data, dtype=np.int16)
    
    def detect_silence(self, audio_chunk):
        """Detecta si el chunk es silencio"""
        rms = np.sqrt(np.mean(audio_chunk.astype(float)**2))
        return rms < self.silence_threshold * 32768
    
    def get_audio_level(self, audio_chunk):
        """Obtiene nivel de audio para visualización (0-100%)"""
        rms = np.sqrt(np.mean(audio_chunk.astype(float)**2))
        level = min(100, int((rms / (32768 * 0.5)) * 100))
        return level

class WhisperTranscriber:
    def __init__(self, audio_processor):
        self.audio_processor = audio_processor
        self.model = config["whisper"]["model"]
        self.language = config["whisper"]["language"]
        self.threads = config["whisper"]["threads"]
        self.use_gpu = config["whisper"]["use_gpu"]
    
    def transcribe(self, audio_chunk):
        """Transcribe un chunk de audio usando whisper.cpp"""
        if not Path("main.exe").exists():
            print("❌ Error: main.exe no encontrado.")
            return ""
        
        # Guardar chunk temporalmente
        temp_wav = "temp_chunk.wav"
        with wave.open(temp_wav, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.audio_processor.sample_rate)
            wf.writeframes(audio_chunk.tobytes())
        
        # Construir comando
        cmd = ["main.exe", "-m", self.model, "-f", temp_wav, "-l", self.language, 
               "-t", str(self.threads), "--no-timestamps"]
        
        if self.use_gpu:
            cmd.insert(1, "-ngl")  # GPU layers (ajustar según necesidad)
            cmd.insert(2, "99")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            transcription = result.stdout.strip()
            
            # Limpieza básica
            if transcription and not any(x in transcription.lower() for x in ['[blanks]', '[silence]']):
                return transcription
            
        except subprocess.TimeoutExpired:
            print("⏱️  Timeout en transcripción.")
        except Exception as e:
            print(f"❌ Error en transcripción: {e}")
        finally:
            if Path(temp_wav).exists():
                os.remove(temp_wav)
        
        return ""

class TrayApp:
    def __init__(self, transcriber_app):
        self.transcriber_app = transcriber_app
        self.icon = None
    
    def create_icon(self):
        """Crea icono simple para la bandeja"""
        img = Image.new('RGB', (64, 64), color='#2196F3')
        pixels = img.load()
        for i in range(20, 44):
            for j in range(15, 35):
                if 27 < i < 37 and j > 25:
                    pixels[i, j] = (255, 255, 255)
                elif not (30 < i < 34 and j < 25):
                    pixels[i, j] = (255, 255, 255)
        return img
    
    def on_open(self, icon, item):
        """Abrir interfaz web"""
        import webbrowser
        webbrowser.open(f"http://localhost:{config['output']['port']}")
    
    def on_pause(self, icon, item):
        """Pausar/Reanudar"""
        state.paused = not state.paused
        status = "Reanudado" if not state.paused else "Pausado"
        logger.info(f"🎙️ Grabación {status.lower()}")
    
    def on_copy(self, icon, item):
        """Copiar texto al portapapeles"""
        try:
            import pyperclip
            pyperclip.copy(state.get_full_text())
            logger.info("📋 Texto copiado al portapapeles")
        except Exception as e:
            logger.warning(f"No se pudo copiar: {e}")
    
    def on_exit(self, icon, item):
        """Salir de la aplicación"""
        state.running = False
        icon.stop()
    
    def run(self):
        """Ejecutar icono en bandeja"""
        menu = Menu(
            MenuItem('🌐 Abrir Interfaz', self.on_open),
            MenuItem('⏸️ Pausar/Reanudar', self.on_pause),
            MenuItem('📋 Copiar Texto', self.on_copy),
            MenuItem(),
            MenuItem('❌ Salir', self.on_exit)
        )
        self.icon = Icon("WhisperTranscriber", self.create_icon(), "Whisper Transcriber", menu)
        self.icon.run(detach=False)

class WebInterface:
    def __init__(self, transcriber_app):
        self.app = Flask(__name__)
        self.transcriber_app = transcriber_app
        self.last_audio_chunk = None
        self.setup_routes()
    
    def setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template_string(HTML_TEMPLATE)
        
        @self.app.route('/api/transcription')
        def get_transcription():
            """Obtiene transcripción actual y nivel de audio"""
            try:
                text = state.get_full_text()
                level = 0
                if self.last_audio_chunk is not None:
                    try:
                        level = self.transcriber_app.audio_processor.get_audio_level(self.last_audio_chunk)
                    except:
                        pass
                return jsonify({
                    'text': text, 
                    'level': level,
                    'segments': len(state.transcription_history)
                })
            except Exception as e:
                logger.error(f"Error en /api/transcription: {e}")
                return jsonify({'text': '', 'level': 0, 'segments': 0})
        
        @self.app.route('/api/history')
        def get_history():
            """Obtiene historial de segmentos"""
            try:
                return jsonify({'history': state.transcription_history[-50:]})  # Últimos 50 segmentos
            except Exception as e:
                logger.error(f"Error en /api/history: {e}")
                return jsonify({'history': []})
        
        @self.app.route('/api/export')
        def export():
            """Exporta transcripción en formato seleccionado"""
            try:
                format_type = request.args.get('format', 'txt')
                content = state.export(format_type)
                
                from flask import make_response
                response = make_response(content)
                response.headers['Content-Disposition'] = f'attachment; filename=transcripcion.{format_type}'
                response.headers['Content-Type'] = 'application/octet-stream'
                return response
            except Exception as e:
                logger.error(f"Error en exportación: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/pause', methods=['POST'])
        def pause():
            """Pausar/Reanudar grabación"""
            state.paused = not state.paused
            logger.info(f"Pausa: {state.paused}")
            return jsonify({'status': 'ok', 'paused': state.paused})
        
        @self.app.route('/api/copy', methods=['POST'])
        def copy():
            """Copiar texto al portapapeles (fallback)"""
            try:
                import pyperclip
                pyperclip.copy(state.get_full_text())
                return jsonify({'status': 'copied'})
            except Exception as e:
                logger.warning(f"No se pudo copiar: {e}")
                return jsonify({'status': 'error', 'message': str(e)})
        
        @self.app.route('/api/clear', methods=['POST'])
        def clear():
            """Borrar transcripción"""
            try:
                state.clear()
                logger.info("Transcripción borrada")
                return jsonify({'status': 'cleared'})
            except Exception as e:
                logger.error(f"Error al borrar: {e}")
                return jsonify({'status': 'error'}), 500
    
    def run(self):
        port = config["output"]["port"]
        logger.info(f"Interfaz web en http://localhost:{port}")
        self.app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False, threaded=True)

def check_voice_commands(text):
    """Procesa comandos de voz simples"""
    if not config.get("features", {}).get("voice_commands", True):
        return False
    
    text_lower = text.lower()
    
    if "copiar todo" in text_lower or "copy all" in text_lower:
        try:
            import pyperclip
            pyperclip.copy(state.get_full_text())
            logger.info("📋 Texto copiado por comando de voz")
        except Exception as e:
            logger.warning(f"No se pudo copiar: {e}")
        return True
    
    if "borrar" in text_lower or "clear" in text_lower:
        state.clear()
        logger.info("🗑️ Texto borrado por comando de voz")
        return True
    
    if "pausar" in text_lower or "pause" in text_lower:
        state.paused = True
        logger.info("⏸️ Grabación pausada por comando de voz")
        return True
    
    if "reanudar" in text_lower or "resume" in text_lower:
        state.paused = False
        logger.info("▶️ Grabación reanudada por comando de voz")
        return True
    
    if "nuevo párrafo" in text_lower or "new paragraph" in text_lower:
        with state.lock:
            state.full_transcription += "\n\n"
        logger.info("📝 Nuevo párrafo insertado")
        return True
    
    return False

def process_audio_worker(transcriber):
    """Worker que procesa audio de la cola asíncronamente"""
    while state.running:
        try:
            audio_chunk = audio_queue.get(timeout=1)
            if audio_chunk is None:  # Señal de parada
                break
            
            # Transcribir
            result = transcriber.transcribe(audio_chunk)
            
            if result:
                # Aplicar puntuación automática
                if config.get("features", {}).get("auto_punctuation", True):
                    result = add_punctuation(result)
                
                # Verificar comandos de voz
                if not check_voice_commands(result):
                    # Agregar al estado
                    state.add_transcription(result)
                    
                    # Auto-copiar si está habilitado
                    if config.get("features", {}).get("auto_copy", True):
                        try:
                            import pyperclip
                            pyperclip.copy(state.get_full_text())
                        except Exception as e:
                            logger.debug(f"No se pudo auto-copiar: {e}")
                    
                    # Guardar en archivo
                    if config.get("output", {}).get("save_to_file", True):
                        try:
                            with open(config["output"]["filename"], 'a', encoding='utf-8') as f:
                                f.write(result + " ")
                        except Exception as e:
                            logger.error(f"Error guardando en archivo: {e}")
                    
                    logger.info(f"🗣️  {result}")
            
            audio_queue.task_done()
        except queue.Empty:
            continue
        except Exception as e:
            logger.error(f"Error en worker: {e}")

def main():
    logger.info("🎙️ Whisper Transcriber Iniciando...")
    print_header("🎙️ Whisper Transcriber Iniciando...")
    
    try:
        # Inicializar componentes
        audio_proc = AudioProcessor()
        transcriber = WhisperTranscriber(audio_proc)
        
        # Iniciar workers de procesamiento
        num_workers = config.get("performance", {}).get("processing_threads", 2)
        workers = []
        for i in range(num_workers):
            t = threading.Thread(target=process_audio_worker, args=(transcriber,), daemon=True)
            t.start()
            workers.append(t)
        logger.info(f"Iniciados {num_workers} workers de procesamiento")
        
        # Iniciar interfaz web
        web_if = WebInterface(transcriber)
        web_thread = threading.Thread(target=web_if.run, daemon=True)
        web_thread.start()
        
        # Configurar bandeja del sistema
        if config.get("features", {}).get("minimize_to_tray", True):
            tray = TrayApp(transcriber)
            tray_thread = threading.Thread(target=tray.run, daemon=True)
            tray_thread.start()
            logger.info("Bandeja del sistema iniciada")
            print("💡 La app se ha minimizado a la bandeja del sistema.")
            print("   Busca el icono 🎙️ cerca del reloj.")
        else:
            print("🌐 Interfaz web abierta. Presiona Ctrl+C para salir.")
        
        # Bucle principal de grabación
        print("🎙️ Grabando... (Habla claramente)")
        print("💬 Comandos: 'copiar todo', 'borrar', 'pausar', 'reanudar'")
        
        while state.running:
            if state.paused:
                time.sleep(0.5)
                continue
            
            try:
                # Grabar chunk
                audio_chunk = audio_proc.record_chunk()
                web_if.last_audio_chunk = audio_chunk  # Para visualización
                
                # Detectar silencio
                if audio_proc.detect_silence(audio_chunk):
                    continue
                
                # Encolar para procesamiento asíncrono
                try:
                    audio_queue.put_nowait(audio_chunk)
                except queue.Full:
                    logger.warning("Cola llena, descartando chunk")
                
            except Exception as e:
                logger.error(f"Error en grabación: {e}")
                time.sleep(0.5)
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        logger.info("Interrupción recibida")
        print("\n👋 Deteniendo...")
    except Exception as e:
        logger.error(f"Error crítico: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
    finally:
        state.running = False
        
        # Esperar cola vacía
        logger.info("Esperando procesamiento pendiente...")
        audio_queue.join()
        
        # Guardar transcripción final
        final_text = state.get_full_text()
        if final_text and config.get("output", {}).get("save_to_file", True):
            try:
                with open(config["output"]["filename"], 'w', encoding='utf-8') as f:
                    f.write(final_text)
                logger.info(f"Transcripción guardada en {config['output']['filename']}")
                print(f"💾 Transcripción guardada en {config['output']['filename']}")
            except Exception as e:
                logger.error(f"Error guardando transcripción: {e}")
        
        print("✅ Aplicación cerrada correctamente")

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

if __name__ == "__main__":
    main()
