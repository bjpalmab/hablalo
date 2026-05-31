#!/usr/bin/env python3
"""
Real-time speech-to-text application using whisper.cpp
Captures audio from microphone and transcribes it in real time

Features:
- Interactive TUI with audio level visualization
- Silence detection to avoid transcribing empty chunks
- Hotkey controls (S=Start/Stop, Q=Quit)
- Configuration via config.json
- Auto-download models if missing
"""

import subprocess
import sounddevice as sd
import numpy as np
import wave
import os
import sys
import json
import threading
from queue import Queue
from datetime import datetime
import keyboard
import time
import argparse

# Default configuration
DEFAULT_CONFIG = {
    "audio": {
        "sample_rate": 16000,
        "channels": 1,
        "chunk_duration": 3,
        "device_id": None,
        "silence_threshold": 0.01,
        "silence_duration": 1.5
    },
    "whisper": {
        "executable": "./main",
        "model": "./models/ggml-base.bin",
        "language": "auto",
        "threads": 8,
        "no_timestamps": True
    },
    "output": {
        "log_file": "transcriptions.txt",
        "save_chunks": False,
        "output_format": "txt",
        "show_visualization": True
    },
    "performance": {
        "timeout_seconds": 60,
        "queue_size": 10,
        "process_threads": 2
    },
    "logging": {
        "verbose": True,
        "show_devices": True,
        "timestamps": True
    }
}


class AudioRecorder:
    """Handles audio recording with silence detection and visualization"""
    
    def __init__(self, config):
        self.config = config
        self.sample_rate = config["audio"]["sample_rate"]
        self.channels = config["audio"]["channels"]
        self.chunk_duration = config["audio"]["chunk_duration"]
        self.device_id = config["audio"].get("device_id")
        self.silence_threshold = config["audio"].get("silence_threshold", 0.01)
        self.silence_duration = config["audio"].get("silence_duration", 1.5)
        self.show_visualization = config["output"].get("show_visualization", True)
        
        self.is_recording = False
        self.is_paused = False
        self.audio_queue = Queue()
        self.current_level = 0
        
    def detect_silence(self, audio_data):
        """Check if audio chunk is mostly silence"""
        rms = np.sqrt(np.mean(audio_data ** 2))
        return rms < self.silence_threshold
    
    def calculate_audio_level(self, audio_data):
        """Calculate audio level for visualization (0-100)"""
        rms = np.sqrt(np.mean(audio_data ** 2))
        # Normalize to 0-100 scale (typical max is around 0.5)
        level = min(int((rms / 0.5) * 100), 100)
        return level
    
    def visualize_audio(self, level, transcription_line=""):
        """Display audio level bar and current transcription"""
        if not self.show_visualization:
            return
            
        bar_length = 40
        filled = int((level / 100) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        # Move cursor up and clear line
        print(f"\r🎤 [{bar}] {level:3d}% {transcription_line}", end="", flush=True)
        
    def record_audio_chunk(self):
        """Record audio chunk from microphone"""
        try:
            samples = int(self.sample_rate * self.chunk_duration)
            audio_data = sd.rec(
                samples,
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.float32,
                device=self.device_id
            )
            
            # Record while showing visualization
            start_time = time.time()
            while time.time() - start_time < self.chunk_duration:
                if not self.is_recording:
                    sd.stop()
                    return None
                    
                elapsed = time.time() - start_time
                # Calculate current level from recorded data so far
                current_idx = min(int(elapsed * self.sample_rate), len(audio_data)-1)
                if current_idx > 100:
                    recent_audio = audio_data[max(0, current_idx-1600):current_idx]
                    level = self.calculate_audio_level(recent_audio)
                    self.current_level = level
                    self.visualize_audio(level)
                time.sleep(0.1)
            
            sd.wait()
            
            # Check for silence
            if self.detect_silence(audio_data):
                return None  # Skip silent chunks
                
            return audio_data
            
        except Exception as e:
            print(f"\n❌ Error recording audio: {e}")
            return None


class Transcriber:
    """Handles transcription using whisper.cpp"""
    
    def __init__(self, config):
        self.config = config
        self.executable = config["whisper"]["executable"]
        self.model_path = config["whisper"]["model"]
        self.language = config["whisper"].get("language", "auto")
        self.threads = config["whisper"].get("threads", 8)
        self.no_timestamps = config["whisper"].get("no_timestamps", True)
        self.timeout = config["performance"].get("timeout_seconds", 60)
        self.save_chunks = config["output"].get("save_chunks", False)
        self.log_file = config["output"].get("log_file", "transcriptions.txt")
        
    def save_audio_chunk(self, audio_data, filename):
        """Save audio chunk to WAV file"""
        try:
            with wave.open(filename, "wb") as wav_file:
                wav_file.setnchannels(self.config["audio"]["channels"])
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(self.sample_rate)
                audio_int16 = np.clip(audio_data * 32767, -32768, 32767).astype(np.int16)
                wav_file.writeframes(audio_int16.tobytes())
            return True
        except Exception as e:
            print(f"\n❌ Error saving audio: {e}")
            return False
    
    def transcribe_audio(self, audio_file):
        """Transcribe audio file using whisper.cpp"""
        try:
            if not os.path.exists(self.executable):
                print(f"\n❌ Whisper executable not found at {self.executable}")
                return None

            if not os.path.exists(self.model_path):
                print(f"\n❌ Model file not found at {self.model_path}")
                return None

            cmd = [
                self.executable,
                "-m", self.model_path,
                "-f", audio_file,
                "--language", self.language,
                "--threads", str(self.threads),
            ]
            
            if self.no_timestamps:
                cmd.append("--no-timestamps")

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout)

            if result.returncode == 0:
                transcription = result.stdout.strip()
                return transcription if transcription else None
            else:
                print(f"\n❌ Transcription error: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            print("\n❌ Transcription timeout")
            return None
        except Exception as e:
            print(f"\n❌ Error transcribing: {e}")
            return None


class RealTimeApp:
    """Main application class with TUI and hotkey support"""
    
    def __init__(self, config):
        self.config = config
        self.recorder = AudioRecorder(config)
        self.transcriber = Transcriber(config)
        self.is_running = False
        self.chunk_counter = 0
        self.last_transcription = ""
        
    def list_audio_devices(self):
        """List available audio devices"""
        print("\n🔊 Available audio devices:")
        devices = sd.query_devices()
        default_input = sd.default.device[0]
        
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:  # Only show input devices
                marker = "→" if i == default_input else " "
                status = "✓" if device['hostapi'] == 0 else " "
                print(f"  {marker} [{i}] {device['name']} {status}")
        
        return devices
    
    def select_device(self, devices):
        """Let user select audio device"""
        try:
            choice = input("\nSelect device number (or press Enter for default): ").strip()
            if choice and choice.isdigit():
                device_id = int(choice)
                if 0 <= device_id < len(devices):
                    self.config["audio"]["device_id"] = device_id
                    self.recorder.device_id = device_id
                    print(f"✓ Selected device: {devices[device_id]['name']}")
                    return True
                else:
                    print("❌ Invalid device number")
                    return False
            return True  # Use default
        except Exception as e:
            print(f"Error selecting device: {e}")
            return False
    
    def process_audio(self):
        """Process audio chunks in background thread"""
        while self.is_running:
            try:
                if self.recorder.is_paused:
                    time.sleep(0.1)
                    continue
                    
                audio_data = self.recorder.record_audio_chunk()
                
                if audio_data is not None:
                    self.chunk_counter += 1
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    audio_file = f"audio_{timestamp}_chunk_{self.chunk_counter}.wav"
                    
                    if self.transcriber.save_audio_chunk(audio_data, audio_file):
                        transcription = self.transcriber.transcribe_audio(audio_file)
                        
                        if transcription:
                            self.last_transcription = transcription
                            print(f"\n✨ [{timestamp}] #{self.chunk_counter}: {transcription}\n")
                            
                            # Save to log file
                            with open(self.transcriber.log_file, "a", encoding="utf-8") as log:
                                log.write(f"[{timestamp}] #{self.chunk_counter}: {transcription}\n")
                        
                        # Clean up
                        if not self.transcriber.save_chunks:
                            try:
                                os.remove(audio_file)
                            except:
                                pass
                                
            except Exception as e:
                print(f"\nError processing audio: {e}")
                time.sleep(1)
    
    def handle_hotkeys(self):
        """Handle keyboard shortcuts"""
        print("\n🎹 Hotkeys: [S] Start/Pause  [Q] Quit  [D] Change Device")
        
        while self.is_running:
            try:
                if keyboard.is_pressed('q'):
                    print("\n\n⏹️  Quitting...")
                    self.is_running = False
                    break
                elif keyboard.is_pressed('s'):
                    self.recorder.is_paused = not self.recorder.is_paused
                    status = "⏸️  PAUSED" if self.recorder.is_paused else "▶️  RECORDING"
                    print(f"\n{status}\n")
                    time.sleep(0.3)  # Debounce
                elif keyboard.is_pressed('d'):
                    self.recorder.is_paused = True
                    self.list_audio_devices()
                    self.select_device(sd.query_devices())
                    self.recorder.is_paused = False
                    print("▶️  Recording resumed\n")
                    time.sleep(0.3)  # Debounce
                time.sleep(0.1)
            except Exception as e:
                pass
    
    def check_prerequisites(self):
        """Check if all prerequisites are met"""
        errors = []
        
        # Check executable
        exe = self.config["whisper"]["executable"]
        if not os.path.exists(exe):
            errors.append(f"Whisper executable not found at '{exe}'")
        
        # Check model
        model = self.config["whisper"]["model"]
        if not os.path.exists(model):
            errors.append(f"Model file not found at '{model}'")
            errors.append("Download a model with: python download_models.py")
        
        if errors:
            print("\n❌ ERRORS FOUND:")
            for error in errors:
                print(f"   • {error}")
            print("\nRun 'python launcher.py' for automatic setup.\n")
            return False
        
        return True
    
    def run(self):
        """Main application loop"""
        print("=" * 60)
        print("🎙️  Real-time Speech-to-Text with whisper.cpp")
        print("=" * 60)
        print(f"Sample rate: {self.config['audio']['sample_rate']} Hz")
        print(f"Chunk duration: {self.config['audio']['chunk_duration']}s")
        print(f"Silence threshold: {self.config['audio'].get('silence_threshold', 0.01)}")
        print(f"Model: {self.config['whisper']['model']}")
        print("=" * 60)
        
        # Check prerequisites
        if not self.check_prerequisites():
            return False
        
        # Show devices
        if self.config["logging"].get("show_devices", True):
            devices = self.list_audio_devices()
        
        # Start processing thread
        processor_thread = threading.Thread(target=self.process_audio, daemon=True)
        processor_thread.start()
        
        # Start hotkey handler
        hotkey_thread = threading.Thread(target=self.handle_hotkeys, daemon=True)
        hotkey_thread.start()
        
        self.is_running = True
        self.recorder.is_recording = True
        
        try:
            print("\n🎙️  Press 'Q' to quit, 'S' to pause/resume\n")
            print("Starting continuous recording...\n")
            
            # Keep main thread alive
            while self.is_running:
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Stopping...")
        finally:
            self.is_running = False
            self.recorder.is_recording = False
            processor_thread.join(timeout=2)
            print("\n✓ Application stopped")
            print(f"📝 Transcriptions saved to '{self.config['output']['log_file']}'")
        
        return True


def load_config(config_file="config.json"):
    """Load configuration from JSON file"""
    config = DEFAULT_CONFIG.copy()
    
    if os.path.exists(config_file):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                file_config = json.load(f)
                # Merge configurations
                for key in file_config:
                    if key in config:
                        if isinstance(config[key], dict):
                            config[key].update(file_config[key])
                        else:
                            config[key] = file_config[key]
            print(f"✓ Loaded configuration from {config_file}")
        except Exception as e:
            print(f"⚠️  Error loading config: {e}, using defaults")
    else:
        print("ℹ️  No config.json found, using defaults")
    
    return config


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Real-time speech-to-text with whisper.cpp")
    parser.add_argument("--config", default="config.json", help="Configuration file")
    parser.add_argument("--device", type=int, help="Audio device ID")
    parser.add_argument("--language", choices=["auto", "es", "en", "fr", "de", "it"], help="Language code")
    parser.add_argument("--model", help="Path to whisper model")
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Override with command line arguments
    if args.device is not None:
        config["audio"]["device_id"] = args.device
    if args.language:
        config["whisper"]["language"] = args.language
    if args.model:
        config["whisper"]["model"] = args.model
    
    # Create and run app
    app = RealTimeApp(config)
    success = app.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
