#!/usr/bin/env python3
"""
Real-time speech-to-text application using whisper.cpp
Captures audio from microphone and transcribes it in real time
"""

import subprocess
import sounddevice as sd
import numpy as np
import wave
import os
import sys
from datetime import datetime
import threading
from queue import Queue

# Configuration
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_DURATION = 3  # Duration of audio chunks in seconds
WHISPER_EXECUTABLE = "./main"  # Path to compiled whisper.cpp executable
MODEL_PATH = "./models/ggml-base.bin"  # Path to whisper model
OUTPUT_FORMAT = "txt"  # or "csv", "json", "vtt"

# Audio capture queue
audio_queue = Queue()
is_recording = False


def record_audio_chunk():
    """Record audio chunk from microphone and add to queue"""
    print("🎤 Recording audio chunk...")
    try:
        audio_data = sd.rec(
            int(SAMPLE_RATE * CHUNK_DURATION),
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=np.float32,
        )
        sd.wait()  # Wait for recording to finish
        audio_queue.put(audio_data)
        print(f"✓ Audio chunk recorded ({CHUNK_DURATION}s)")
    except Exception as e:
        print(f"❌ Error recording audio: {e}")


def save_audio_chunk(audio_data, filename):
    """Save audio chunk to WAV file"""
    try:
        with wave.open(filename, "wb") as wav_file:
            wav_file.setnchannels(CHANNELS)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(SAMPLE_RATE)
            # Convert float32 to int16
            audio_int16 = (audio_data * 32767).astype(np.int16)
            wav_file.writeframes(audio_int16.tobytes())
    except Exception as e:
        print(f"❌ Error saving audio: {e}")
        return False
    return True


def transcribe_audio(audio_file):
    """Transcribe audio file using whisper.cpp"""
    try:
        if not os.path.exists(WHISPER_EXECUTABLE):
            print(f"❌ Whisper executable not found at {WHISPER_EXECUTABLE}")
            return None

        if not os.path.exists(MODEL_PATH):
            print(f"❌ Model file not found at {MODEL_PATH}")
            return None

        # Build command
        cmd = [
            WHISPER_EXECUTABLE,
            "-m",
            MODEL_PATH,
            "-f",
            audio_file,
            "-l",
            "auto",  # Auto-detect language
            "-t",
            "8",  # Number of threads
            "-o",
            "./output",  # Output directory
        ]

        print(f"🔄 Transcribing: {audio_file}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            # Read the output file
            output_file = f"./output/{os.path.splitext(os.path.basename(audio_file))[0]}.txt"
            if os.path.exists(output_file):
                with open(output_file, "r", encoding="utf-8") as f:
                    transcription = f.read().strip()
                return transcription
        else:
            print(f"❌ Transcription error: {result.stderr}")
            return None

    except subprocess.TimeoutExpired:
        print("❌ Transcription timeout")
        return None
    except Exception as e:
        print(f"❌ Error transcribing: {e}")
        return None


def process_audio_queue():
    """Process audio chunks from queue and transcribe"""
    chunk_counter = 0
    while is_recording or not audio_queue.empty():
        try:
            audio_data = audio_queue.get(timeout=1)
            chunk_counter += 1

            # Save audio chunk
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_file = f"audio_{timestamp}_chunk_{chunk_counter}.wav"

            if save_audio_chunk(audio_data, audio_file):
                # Transcribe
                transcription = transcribe_audio(audio_file)
                if transcription:
                    print(f"\n✨ [{timestamp}] Transcription #{chunk_counter}:")
                    print(f"   {transcription}\n")
                    
                    # Optionally save to file
                    with open("transcriptions.txt", "a", encoding="utf-8") as log:
                        log.write(
                            f"[{timestamp}] Chunk {chunk_counter}:\n{transcription}\n\n"
                        )

                # Clean up audio file (optional)
                try:
                    os.remove(audio_file)
                except:
                    pass

        except Exception as e:
            print(f"Error processing queue: {e}")


def main():
    """Main application loop"""
    print("=" * 60)
    print("🎙️  Real-time Speech-to-Text with whisper.cpp")
    print("=" * 60)
    print(f"Sample rate: {SAMPLE_RATE} Hz")
    print(f"Chunk duration: {CHUNK_DURATION} seconds")
    print(f"Whisper model: {MODEL_PATH}")
    print("=" * 60)

    # Create output directory
    os.makedirs("./output", exist_ok=True)

    # Test audio device
    print("\n🔊 Available audio devices:")
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        marker = "→" if i == sd.default.device[0] else " "
        print(f"  {marker} [{i}] {device['name']}")

    global is_recording
    is_recording = True

    # Start audio processing thread
    processor_thread = threading.Thread(target=process_audio_queue, daemon=True)
    processor_thread.start()

    try:
        print("\n🎙️  Press Ctrl+C to stop recording and exit")
        print("Starting continuous recording...\n")

        while True:
            record_audio_chunk()

    except KeyboardInterrupt:
        print("\n\n⏹️  Stopping recording...")
        is_recording = False
        # Wait for queue to be processed
        processor_thread.join(timeout=5)
        print("✓ Application stopped")
        print("\n📝 Transcriptions saved to 'transcriptions.txt'")

    except Exception as e:
        print(f"❌ Fatal error: {e}")
        is_recording = False
        sys.exit(1)


if __name__ == "__main__":
    main()
