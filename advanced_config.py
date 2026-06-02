"""
Advanced configuration for hablalo
Customize behavior without modifying main.py
"""

# Audio Settings
AUDIO_CONFIG = {
    "sample_rate": 16000,  # Hz - Don't change, whisper.cpp expects 16kHz
    "channels": 1,  # Mono audio
    "chunk_duration": 3,  # Seconds per chunk
    "device_id": None,  # None = default, or specify device number
}

# Whisper.cpp Settings
WHISPER_CONFIG = {
    "executable": "./main",  # Path to compiled whisper.cpp
    "model": "./models/ggml-base.bin",  # Model file path
    "language": "auto",  # "auto" for auto-detection, or "es", "en", etc.
    "threads": 8,  # Number of CPU threads
    "no_timestamps": True,  # Remove timestamps from output
}

# Output Settings
OUTPUT_CONFIG = {
    "log_file": "transcriptions.txt",  # Where to save transcriptions
    "save_chunks": False,  # Keep .wav files or delete them
    "output_format": "txt",  # txt, csv, json, vtt
}

# Performance Settings
PERFORMANCE_CONFIG = {
    "timeout_seconds": 30,  # Max time to wait for transcription
    "queue_size": 10,  # Max audio chunks in queue
    "process_threads": 2,  # Number of processing threads
}

# Logging Settings
LOGGING_CONFIG = {
    "verbose": True,  # Print detailed output
    "show_devices": True,  # List audio devices on startup
    "timestamps": True,  # Include timestamps in output
}


def get_audio_config():
    """Get audio configuration"""
    return AUDIO_CONFIG


def get_whisper_config():
    """Get whisper configuration"""
    return WHISPER_CONFIG


def get_output_config():
    """Get output configuration"""
    return OUTPUT_CONFIG


def get_performance_config():
    """Get performance configuration"""
    return PERFORMANCE_CONFIG


def get_logging_config():
    """Get logging configuration"""
    return LOGGING_CONFIG
