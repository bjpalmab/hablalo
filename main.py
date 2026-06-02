"""
Whisper Transcriber con Interfaz Web, Comandos de Voz y Bandeja del Sistema.
Mejorado con detección automática de micrófono y minimizado a tray.
"""
import os
import sys
import json
import time
import threading
import wave
import numpy as np
import pyaudio
import subprocess
import signal
from pathlib import Path
from flask import Flask, render_template_string, jsonify
from http.server import HTTPServer
import keyboard
import pystray
from pystray import Icon, MenuItem, Menu
from PIL import Image

# Cargar configuración
CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "audio": {"device_index": -1, "chunk_duration": 3, "silence_threshold": 0.01, "sample_rate": 16000},
    "whisper": {"model": "models/ggml-base.bin", "language": "es", "threads": 4, "use_gpu": False},
    "output": {"show_ui": True, "port": 8080, "save_to_file": True, "filename": "transcriptions.txt"},
    "features": {"auto_copy": True, "voice_commands": True, "minimize_to_tray": True}
}

def load_config():
    if Path(CONFIG_FILE).exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    # Crear config por defecto si no existe
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(DEFAULT_CONFIG, f, indent=4)
    return DEFAULT_CONFIG

config = load_config()

# Variables globales
running = True
paused = False
transcription_buffer = []
full_transcription = ""
audio_data = []
icon_ref = None

# HTML para la interfaz web
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
        .container { max-width: 900px; margin: 0 auto; }
        h1 { text-align: center; color: #2196F3; }
        .status { text-align: center; padding: 10px; margin: 10px 0; border-radius: 5px; 
                  background: #e3f2fd; color: #1976D2; font-weight: bold; }
        .dark-mode .status { background: #333; color: #64B5F6; }
        .controls { text-align: center; margin: 20px 0; }
        button { padding: 10px 20px; margin: 5px; font-size: 16px; cursor: pointer; 
                 border: none; border-radius: 5px; background: #2196F3; color: white; }
        button:hover { background: #1976D2; }
        button.danger { background: #f44336; }
        button.danger:hover { background: #d32f2f; }
        .transcription { background: white; padding: 20px; border-radius: 8px; 
                         box-shadow: 0 2px 5px rgba(0,0,0,0.1); min-height: 300px; 
                         white-space: pre-wrap; line-height: 1.6; }
        .dark-mode .transcription { background: #2d2d2d; box-shadow: 0 2px 5px rgba(255,255,255,0.1); }
        .audio-level { height: 20px; background: #e0e0e0; border-radius: 10px; 
                       overflow: hidden; margin: 10px 0; }
        .level-bar { height: 100%; background: linear-gradient(90deg, #4CAF50, #8BC34A); 
                     width: 0%; transition: width 0.1s; }
        .commands { margin-top: 20px; padding: 15px; background: #fff3cd; border-radius: 5px; }
        .dark-mode .commands { background: #444; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎙️ Whisper Transcriber</h1>
        <div class="status" id="status">Estado: Grabando...</div>
        <div class="audio-level"><div class="level-bar" id="levelBar"></div></div>
        <div class="controls">
            <button onclick="togglePause()">⏸️ Pausar/Reanudar</button>
            <button onclick="copyText()">📋 Copiar Todo</button>
            <button onclick="clearText()" class="danger">🗑️ Borrar</button>
            <button onclick="toggleTheme()">🌓 Tema</button>
        </div>
        <div class="transcription" id="transcription">Esperando audio...</div>
        <div class="commands">
            <strong>🎤 Comandos de Voz:</strong><br>
            "Copiar todo", "Borrar texto", "Nuevo párrafo", "Pausar grabación", "Reanudar grabación"
        </div>
    </div>
    <script>
        let isPaused = false;
        function updateTranscription() {
            fetch('/api/transcription').then(r => r.json()).then(data => {
                document.getElementById('transcription').innerText = data.text || 'Esperando audio...';
                document.getElementById('levelBar').style.width = (data.level || 0) + '%';
            });
        }
        setInterval(updateTranscription, 500);
        function togglePause() {
            fetch('/api/pause', {method: 'POST'}).then(() => location.reload());
        }
        function copyText() {
            fetch('/api/copy', {method: 'POST'}).then(() => alert('¡Texto copiado!'));
        }
        function clearText() {
            fetch('/api/clear', {method: 'POST'}).then(() => location.reload());
        }
        function toggleTheme() {
            document.body.classList.toggle('dark-mode');
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
        # Crear imagen simple de 64x64 con Pillow
        img = Image.new('RGB', (64, 64), color='#2196F3')
        pixels = img.load()
        # Dibujar un micrófono simple
        for i in range(20, 44):
            for j in range(15, 35):
                if 27 < i < 37 and j > 25:  # Base
                    pixels[i, j] = (255, 255, 255)
                elif not (30 < i < 34 and j < 25):  # Cuerpo
                    pixels[i, j] = (255, 255, 255)
        return img
    
    def on_open(self, icon, item):
        """Abrir interfaz web"""
        import webbrowser
        webbrowser.open(f"http://localhost:{config['output']['port']}")
    
    def on_pause(self, icon, item):
        """Pausar/Reanudar"""
        global paused
        paused = not paused
        status = "Reanudado" if not paused else "Pausado"
        print(f"🎙️ Grabación {status.lower()}")
    
    def on_copy(self, icon, item):
        """Copiar texto al portapapeles"""
        global full_transcription
        try:
            import pyperclip
            pyperclip.copy(full_transcription)
            print("📋 Texto copiado al portapapeles")
        except:
            print("⚠️  No se pudo copiar (instala: pip install pyperclip)")
    
    def on_exit(self, icon, item):
        """Salir de la aplicación"""
        global running
        running = False
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
        self.setup_routes()
    
    def setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template_string(HTML_TEMPLATE)
        
        @self.app.route('/api/transcription')
        def get_transcription():
            global full_transcription, audio_data
            level = 0
            if audio_data:
                level = self.transcriber_app.audio_processor.get_audio_level(audio_data[-1])
            return jsonify({'text': full_transcription, 'level': level})
        
        @self.app.route('/api/pause', methods=['POST'])
        def pause():
            global paused
            paused = not paused
            return jsonify({'status': 'ok'})
        
        @self.app.route('/api/copy', methods=['POST'])
        def copy():
            global full_transcription
            try:
                import pyperclip
                pyperclip.copy(full_transcription)
                return jsonify({'status': 'copied'})
            except:
                return jsonify({'status': 'error'})
        
        @self.app.route('/api/clear', methods=['POST'])
        def clear():
            global full_transcription, transcription_buffer
            full_transcription = ""
            transcription_buffer = []
            return jsonify({'status': 'cleared'})
    
    def run(self):
        port = config["output"]["port"]
        print(f"🌐 Interfaz web disponible en http://localhost:{port}")
        self.app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False, threaded=True)

def check_voice_commands(text):
    """Procesa comandos de voz simples"""
    if not config["features"]["voice_commands"]:
        return False
    
    text_lower = text.lower()
    global paused, full_transcription
    
    if "copiar todo" in text_lower or "copy all" in text_lower:
        try:
            import pyperclip
            pyperclip.copy(full_transcription)
            print("📋 Texto copiado por comando de voz")
        except:
            print("⚠️  Instala pyperclip para copiar: pip install pyperclip")
        return True
    
    if "borrar" in text_lower or "clear" in text_lower:
        full_transcription = ""
        print("🗑️ Texto borrado por comando de voz")
        return True
    
    if "pausar" in text_lower or "pause" in text_lower:
        paused = True
        print("⏸️ Grabación pausada por comando de voz")
        return True
    
    if "reanudar" in text_lower or "resume" in text_lower:
        paused = False
        print("▶️ Grabación reanudada por comando de voz")
        return True
    
    if "nuevo párrafo" in text_lower or "new paragraph" in text_lower:
        full_transcription += "\n\n"
        print("📝 Nuevo párrafo insertado")
        return True
    
    return False

def main():
    global running, paused, full_transcription, audio_data, icon_ref
    
    print_header("🎙️ Whisper Transcriber Iniciando...")
    
    # Inicializar componentes
    audio_proc = AudioProcessor()
    # audio_proc.list_devices()  # Descomentar para ver dispositivos
    
    transcriber = WhisperTranscriber(audio_proc)
    
    # Iniciar interfaz web en hilo separado
    web_if = WebInterface(transcriber)
    web_thread = threading.Thread(target=web_if.run, daemon=True)
    web_thread.start()
    
    # Configurar bandeja del sistema si está habilitado
    if config["features"]["minimize_to_tray"]:
        tray = TrayApp(transcriber)
        tray_thread = threading.Thread(target=tray.run, daemon=True)
        tray_thread.start()
        icon_ref = tray
        print("💡 La app se ha minimizado a la bandeja del sistema.")
        print("   Busca el icono 🎙️ cerca del reloj.")
    else:
        print("🌐 Interfaz web abierta. Presiona Ctrl+C para salir.")
    
    # Bucle principal de grabación
    print("🎙️ Grabando... (Habla claramente)")
    print("💬 Comandos disponibles: 'copiar todo', 'borrar', 'pausar', 'reanudar'")
    
    try:
        while running:
            if paused:
                time.sleep(0.5)
                continue
            
            # Grabar chunk
            audio_chunk = audio_proc.record_chunk()
            audio_data = [audio_chunk]  # Para visualización web
            
            # Detectar silencio
            if audio_proc.detect_silence(audio_chunk):
                continue
            
            # Transcribir
            result = transcriber.transcribe(audio_chunk)
            
            if result:
                # Verificar comandos de voz
                if not check_voice_commands(result):
                    # Agregar a buffer y texto completo
                    transcription_buffer.append(result)
                    full_transcription += result + " "
                    
                    # Auto-copiar si está habilitado
                    if config["features"]["auto_copy"]:
                        try:
                            import pyperclip
                            pyperclip.copy(full_transcription)
                        except:
                            pass
                    
                    # Guardar en archivo
                    if config["output"]["save_to_file"]:
                        with open(config["output"]["filename"], 'a', encoding='utf-8') as f:
                            f.write(result + " ")
                    
                    print(f"🗣️  {result}")
            
            time.sleep(0.2)
    
    except KeyboardInterrupt:
        print("\n👋 Deteniendo...")
        running = False
    
    # Guardar transcripción final
    if full_transcription and config["output"]["save_to_file"]:
        with open(config["output"]["filename"], 'w', encoding='utf-8') as f:
            f.write(full_transcription)
        print(f"💾 Transcripción guardada en {config['output']['filename']}")

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

if __name__ == "__main__":
    main()
